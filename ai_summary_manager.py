"""
AI总结管理器
负责获取群消息历史、调用AI总结、保存结果
"""

import os
import json
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from config import config
from ai_prompts import MediaWikiSummaryPrompts, SummaryTemplates
# 移除本地消息存储依赖，直接使用OneBot API获取消息


class AISummaryManager:
    """AI总结管理器"""
    
    def __init__(self):
        self.onebot_http_url = config.ONEBOT_HTTP_URL
        self.target_group_id = config.TARGET_GROUP_ID
        self.ai_log_dir = config.AI_LOG_DIR
        self.ark_api_key = config.ARK_API_KEY
        self.api_url = config.VOLC_AI_API_URL
        self.max_tokens = config.AI_SUMMARY_MAX_TOKENS
        self.timeout = config.AI_SUMMARY_TIMEOUT
        
        # 确保AI_LOG目录存在
        self.ensure_ai_log_dir()
    
    def ensure_ai_log_dir(self):
        """确保AI_LOG目录存在"""
        try:
            Path(self.ai_log_dir).mkdir(exist_ok=True)
        except Exception as e:
            print(f"创建AI_LOG目录失败: {e}")
    
    async def get_group_message_history(self, group_id: int, message_id: str = None, count: int = 20) -> List[Dict]:
        """
        获取群消息历史记录
        
        Args:
            group_id: 群号
            message_id: 起始消息ID，为空则从最新消息开始
            count: 获取消息数量，默认20条
            
        Returns:
            消息列表
        """
        try:
            # 根据Lagrange.OneBot API文档调用获取群历史聊天记录API
            payload = {
                "group_id": group_id,
                "count": count
            }
            
            # 如果指定了消息ID，则从该消息开始获取
            if message_id:
                payload["message_id"] = message_id
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.onebot_http_url}/get_group_msg_history",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"API调用状态: {response.status_code}")
                print(f"API响应内容: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "ok" and "data" in result:
                        messages = result["data"].get("messages", [])
                        print(f"获取到 {len(messages)} 条原始消息")
                        return self.format_messages(messages)
                    else:
                        print(f"获取群消息失败: {result}")
                        return []
                else:
                    print(f"API调用失败: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            print(f"获取群消息历史失败: {e}")
            return []
    
    async def get_group_info(self, group_id: int) -> Optional[Dict]:
        """
        获取群信息
        
        Args:
            group_id: 群号
            
        Returns:
            群信息字典
        """
        try:
            payload = {"group_id": group_id}
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.onebot_http_url}/get_group_info",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"获取群信息API状态: {response.status_code}")
                print(f"获取群信息API响应: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "ok" and "data" in result:
                        return result["data"]
                    else:
                        print(f"获取群信息失败: {result}")
                        return None
                else:
                    print(f"获取群信息API调用失败: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"获取群信息异常: {e}")
            return None
    
    async def get_group_messages_by_date(self, group_id: int, target_date: datetime) -> List[Dict]:
        """
        获取指定日期的群消息（通过多次调用API获取足够的消息）
        
        Args:
            group_id: 群号
            target_date: 目标日期
            
        Returns:
            该日期的消息列表
        """
        try:
            all_messages = []
            message_id = None
            max_requests = 50  # 最多请求50次，避免无限循环
            request_count = 0
            
            # 计算目标日期的时间范围
            start_timestamp = target_date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
            end_timestamp = target_date.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp()
            
            print(f"查找 {target_date.strftime('%Y-%m-%d')} 的消息，时间范围: {start_timestamp} - {end_timestamp}")
            
            while request_count < max_requests:
                request_count += 1
                print(f"第 {request_count} 次API调用，当前message_id: {message_id}")
                
                # 获取一批消息
                messages = await self.get_group_message_history(group_id, message_id, 20)
                
                if not messages:
                    print("没有更多消息了")
                    break
                
                # 过滤出目标日期的消息
                date_messages = []
                oldest_timestamp = None
                
                for msg in messages:
                    msg_timestamp = msg.get("timestamp", 0)
                    if oldest_timestamp is None or msg_timestamp < oldest_timestamp:
                        oldest_timestamp = msg_timestamp
                    
                    # 检查消息是否在目标日期范围内
                    if start_timestamp <= msg_timestamp <= end_timestamp:
                        date_messages.append(msg)
                
                print(f"本批次找到目标日期消息: {len(date_messages)} 条")
                all_messages.extend(date_messages)
                
                # 如果最老的消息已经早于目标日期开始时间，说明已经查找完毕
                if oldest_timestamp and oldest_timestamp < start_timestamp:
                    print(f"已查找到目标日期之前的消息，停止查找")
                    break
                
                # 使用最后一条消息的ID作为下次查询的起点
                if messages:
                    last_message = messages[-1]
                    message_id = str(last_message.get("message_id", ""))
                    if not message_id:
                        print("无法获取下一个消息ID，停止查找")
                        break
                else:
                    break
            
            print(f"总共找到目标日期消息: {len(all_messages)} 条")
            
            # 按时间排序（从早到晚）
            all_messages.sort(key=lambda x: x.get("timestamp", 0))
            
            return all_messages
            
        except Exception as e:
            print(f"按日期获取群消息失败: {e}")
            return []
    
    def format_messages(self, raw_messages: List[Dict]) -> List[Dict]:
        """
        格式化消息数据
        
        Args:
            raw_messages: 原始消息数据
            
        Returns:
            格式化后的消息列表
        """
        formatted_messages = []
        
        for msg in raw_messages:
            try:
                # 提取消息信息
                message_id = msg.get("message_id", 0)
                user_id = msg.get("user_id", 0)
                
                # 处理消息内容 - 可能是字符串或消息段数组
                raw_message = msg.get("raw_message", "")
                message_content = msg.get("message", [])
                
                # 如果有raw_message就使用，否则尝试从message数组构建
                if raw_message:
                    message_text = raw_message
                else:
                    # 处理消息段数组，提取文本内容
                    text_parts = []
                    if isinstance(message_content, list):
                        for segment in message_content:
                            if isinstance(segment, dict):
                                if segment.get("type") == "text":
                                    text_parts.append(segment.get("data", {}).get("text", ""))
                                elif segment.get("type") == "at":
                                    at_name = segment.get("data", {}).get("name", "")
                                    text_parts.append(f"@{at_name}")
                    message_text = "".join(text_parts)
                
                # 跳过空消息
                if not message_text.strip():
                    continue
                
                # 获取时间戳 - 注意API可能返回的字段名
                time_value = msg.get("time", 0)
                if time_value == 0:
                    # 如果没有time字段，尝试使用当前时间
                    time_value = int(datetime.now().timestamp())
                
                # 获取发送者信息
                sender_info = msg.get("sender", {})
                sender_name = sender_info.get("nickname", f"用户{user_id}")
                
                # 格式化时间
                timestamp = datetime.fromtimestamp(time_value)
                time_str = timestamp.strftime("%H:%M:%S")
                
                formatted_messages.append({
                    "message_id": message_id,
                    "user_id": user_id,
                    "username": sender_name,
                    "message": message_text,
                    "type": "text",
                    "timestamp": time_value,
                    "time": time_str,
                    "datetime": timestamp.strftime("%Y-%m-%d %H:%M:%S")
                })
                
            except Exception as e:
                print(f"格式化消息失败: {e}, 消息内容: {msg}")
                continue
        
        return formatted_messages
    
    async def call_ai_summary(self, messages: List[Dict], date: str) -> Optional[str]:
        """
        调用AI进行总结
        
        Args:
            messages: 消息列表
            date: 日期
            
        Returns:
            AI总结结果
        """
        try:
            # 生成prompt
            prompt = MediaWikiSummaryPrompts.get_daily_summary_prompt(messages, date)
            
            # 准备AI请求数据
            data = {
                "model": "ep-20250811175605-fxzbh",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.max_tokens,
                "temperature": 0.7,
                "stream": False
            }
            
            body = json.dumps(data, ensure_ascii=False)
            
            # 准备请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.ark_api_key}"
            }
            
            # 发送请求
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    content=body
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    else:
                        print(f"AI响应格式异常: {result}")
                        return None
                else:
                    print(f"AI API调用失败: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"调用AI总结失败: {e}")
            return None
    
    def save_summary(self, summary: str, date: datetime, group_id: int) -> str:
        """
        保存总结结果
        
        Args:
            summary: 总结内容
            date: 日期
            group_id: 群号
            
        Returns:
            保存的文件路径
        """
        try:
            # 生成文件名
            filename = SummaryTemplates.create_summary_filename(date)
            filepath = Path(self.ai_log_dir) / filename
            
            # 准备保存内容
            content = f"""# MediaWiki技术讨论总结 - {date.strftime('%Y年%m月%d日')}

**群号**: {group_id}  
**总结时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**生成方式**: AI自动总结

---

{summary}

---

*此总结由AI自动生成，仅供参考*
"""
            
            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"总结已保存到: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"保存总结失败: {e}")
            return ""
    
    async def generate_daily_summary(self, target_date: datetime = None, group_id: int = None) -> bool:
        """
        生成指定日期的总结
        
        Args:
            target_date: 目标日期，默认为昨天
            group_id: 群号，默认使用配置中的目标群
            
        Returns:
            是否成功
        """
        try:
            if target_date is None:
                target_date = datetime.now() - timedelta(days=1)
            
            if group_id is None:
                group_id = self.target_group_id
            
            date_str = target_date.strftime("%Y-%m-%d")
            print(f"开始生成 {date_str} 的群消息总结...")
            print(f"获取群 {group_id} 在 {date_str} 的消息...")
            
            # 使用新的按日期获取消息方法
            messages = await self.get_group_messages_by_date(group_id, target_date)
            
            if not messages:
                print(f"未找到 {date_str} 的消息记录")
                return False
            
            print(f"获取到 {len(messages)} 条消息")
            
            # 过滤掉机器人自己的消息和无意义的消息
            filtered_messages = self.filter_messages(messages)
            
            if not filtered_messages:
                print(f"过滤后没有有效消息")
                return False
            
            print(f"过滤后剩余 {len(filtered_messages)} 条有效消息")
            
            # 调用AI总结
            print("正在调用AI进行总结...")
            summary = await self.call_ai_summary(filtered_messages, date_str)
            
            if not summary:
                print("AI总结失败")
                return False
            
            # 保存总结
            filepath = self.save_summary(summary, target_date, group_id)
            
            if filepath:
                print(f"✅ 总结生成成功！")
                print(f"📁 文件路径: {filepath}")
                return True
            else:
                print("❌ 保存总结失败")
                return False
                
        except Exception as e:
            print(f"生成总结失败: {e}")
            return False
    
    def filter_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        过滤消息，移除无意义的内容
        
        Args:
            messages: 原始消息列表
            
        Returns:
            过滤后的消息列表
        """
        filtered = []
        
        for msg in messages:
            try:
                message_text = msg.get("message", "").strip()
                user_id = msg.get("user_id", 0)
                
                # 跳过空消息
                if not message_text:
                    continue
                
                # 跳过太短的消息（可能是表情或无意义内容）
                if len(message_text) < 3:
                    continue
                
                # 跳过纯符号或表情的消息
                if message_text.replace(" ", "") in ["...", "？？？", "！！！", "???", "!!!"]:
                    continue
                
                # 跳过机器人指令消息
                if message_text.startswith(('.', '/', '!', '。')):
                    continue
                
                # 可以添加更多过滤条件，比如跳过特定用户ID（机器人自己）
                # if user_id == bot_user_id:
                #     continue
                
                filtered.append(msg)
                
            except Exception as e:
                print(f"过滤消息时出错: {e}")
                continue
        
        return filtered
    
    async def generate_summary_for_date_range(self, start_date: datetime, end_date: datetime, group_id: int = None) -> List[str]:
        """
        生成日期范围内的总结
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            group_id: 群号，默认使用配置中的目标群
            
        Returns:
            生成的总结文件路径列表
        """
        generated_files = []
        current_date = start_date
        
        while current_date <= end_date:
            success = await self.generate_daily_summary(current_date, group_id)
            if success:
                filename = SummaryTemplates.create_summary_filename(current_date)
                filepath = Path(self.ai_log_dir) / filename
                generated_files.append(str(filepath))
            
            current_date += timedelta(days=1)
        
        return generated_files


# 创建全局实例
ai_summary_manager = AISummaryManager()
