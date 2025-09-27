"""
群消息总结插件
功能：
1. 通过HTTP API获取指定群的指定日期的历史聊天记录
2. 将聊天记录整合为易于AI读取的格式，并以群聊id-日期的形式保存到./data/history路径
3. 将指定聊天记录发送给AI，要求它按指定格式整理聊天内容里的技术答疑和知识共享内容
4. 接收AI的回复并生成文件储存到./data/historySummary
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.rule import to_me, Rule

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.config import config
from src.core.http_client import get_client
from src.core.ai_manager import ai_manager
from src.core.message_sender import get_sender


# 创建数据目录
def ensure_data_dirs():
    """确保数据目录存在"""
    os.makedirs("./data/history", exist_ok=True)
    os.makedirs("./data/daySummary", exist_ok=True)


# 命令处理器
summary_cmd = on_command("群总结", rule=to_me(), priority=5)


@summary_cmd.handle()
async def handle_summary_command(event: GroupMessageEvent, args=CommandArg()):
    """处理群总结命令"""
    try:
        # 解析参数
        arg_str = str(args).strip()
        
        if not arg_str:
            # 默认总结昨天的消息
            target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            # 解析日期参数
            try:
                if arg_str == "今天":
                    target_date = datetime.now().strftime("%Y-%m-%d")
                elif arg_str == "昨天":
                    target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                else:
                    # 尝试解析日期格式 YYYY-MM-DD
                    datetime.strptime(arg_str, "%Y-%m-%d")
                    target_date = arg_str
            except ValueError:
                logger.error("日期格式错误，请使用 YYYY-MM-DD 格式，或使用'今天'、'昨天'")
                return
        
        # 确保数据目录存在
        ensure_data_dirs()
        
        # 执行总结流程
        result = await process_group_summary(event.group_id, target_date)
        
        if result["success"]:
            summary_file = result["summary_file"]
            logger.info(f"群消息总结完成，文件保存到: {summary_file}")
        else:
            logger.error(f"群消息总结失败: {result['error']}")
            
    except Exception as e:
        logger.error(f"群总结命令处理异常: {e}")


async def process_group_summary(group_id: int, target_date: str) -> Dict[str, Any]:
    """
    处理群消息总结的完整流程
    
    Args:
        group_id: 群ID
        target_date: 目标日期 (YYYY-MM-DD)
        
    Returns:
        处理结果字典
    """
    try:
        # 1. 获取群聊历史记录
        logger.info(f"开始获取群 {group_id} 在 {target_date} 的历史消息")
        history_data = await fetch_group_history(group_id, target_date)
        
        if not history_data["success"]:
            return {"success": False, "error": f"获取历史消息失败: {history_data['error']}"}
        
        # 2. 保存优化后的历史记录
        history_file = f"./data/history/{group_id}-{target_date}.json"
        try:
            optimized_data = optimize_message_data(history_data["data"])
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(optimized_data, f, ensure_ascii=False, indent=2)
            logger.info(f"历史消息已保存到: {history_file}")
        except Exception as e:
            logger.error(f"保存历史消息文件失败: {e}")
            # 如果优化失败，保存原始数据
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data["data"], f, ensure_ascii=False, indent=2)
            logger.info(f"已保存原始历史消息到: {history_file}")
        
        # 3. 格式化聊天记录为AI可读格式
        formatted_messages = format_messages_for_ai(history_data["data"])
        
        # 4. 调用AI进行总结
        logger.info("开始调用AI进行消息总结")
        ai_result = await call_ai_for_summary(formatted_messages)
        
        if not ai_result["success"]:
            return {"success": False, "error": f"AI总结失败: {ai_result['error']}"}
        
        # 5. 保存AI总结结果
        summary_file = f"./data/daySummary/{group_id}-{target_date}-summary.json"
        summary_data = {
            "group_id": group_id,
            "date": target_date,
            "summary": ai_result["data"],
            "created_at": datetime.now().isoformat(),
            "message_count": len(history_data["data"])
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"AI总结已保存到: {summary_file}")
        
        return {
            "success": True,
            "history_file": history_file,
            "summary_file": summary_file,
            "message_count": len(history_data["data"])
        }
        
    except Exception as e:
        logger.error(f"群消息总结处理异常: {e}")
        return {"success": False, "error": str(e)}


async def fetch_group_history(group_id: int, target_date: str) -> Dict[str, Any]:
    """
    获取群聊历史记录
    
    Args:
        group_id: 群ID
        target_date: 目标日期 (YYYY-MM-DD)
        
    Returns:
        获取结果字典
    """
    try:
        client = get_client()
        
        # 计算目标日期的时间范围
        target_datetime = datetime.strptime(target_date, "%Y-%m-%d")
        
        # 计算目标日期的开始和结束时间戳（本地时间）
        start_time = int(target_datetime.timestamp())
        end_time = int((target_datetime + timedelta(days=1)).timestamp())
        
        logger.info(f"获取群 {group_id} 从 {start_time} 到 {end_time} 的消息")
        logger.info(f"时间范围: {datetime.fromtimestamp(start_time)} 到 {datetime.fromtimestamp(end_time)}")
        
        # 获取群消息历史 - 使用message_id参数来获取更多历史消息
        all_messages = []
        message_id = None
        max_attempts = 10  # 最多尝试10次，避免无限循环
        
        for attempt in range(max_attempts):
            logger.info(f"尝试获取历史消息，第 {attempt + 1} 次，message_id: {message_id}")
            
            result = await client.get_group_msg_history(group_id, message_id, 50)  # 每次获取50条消息
            
            if result.get("status") != "ok":
                logger.warning(f"获取消息失败: {result.get('error', '未知错误')}")
                break
            
            messages = result.get("data", {}).get("messages", [])
            if not messages:
                logger.info("没有更多消息了")
                break
            
            # 检查是否已经获取到目标日期之前的消息
            oldest_msg_time = min(msg.get("time", 0) for msg in messages)
            oldest_msg_date = datetime.fromtimestamp(oldest_msg_time)
            
            logger.info(f"本次获取到 {len(messages)} 条消息，最早消息时间: {oldest_msg_date}")
            
            all_messages.extend(messages)
            
            # 如果最早的消息已经早于目标日期，停止获取
            if oldest_msg_time < start_time:
                logger.info(f"已获取到目标日期之前的消息，停止获取")
                break
            
            # 更新message_id为最早消息的ID，继续获取更早的消息
            oldest_message = min(messages, key=lambda msg: msg.get("time", 0))
            message_id = str(oldest_message.get("message_id", ""))
            if not message_id or message_id == "0":
                logger.info("无法获取更早的消息")
                break
        
        logger.info(f"总共获取到 {len(all_messages)} 条历史消息")
        
        # 过滤指定日期的消息
        filtered_messages = []
        for msg in all_messages:
            msg_time = msg.get("time", 0)
            if start_time <= msg_time < end_time:
                filtered_messages.append(msg)
        
        logger.info(f"找到 {len(filtered_messages)} 条 {target_date} 的消息")
        
        # 如果没有找到目标日期的消息，记录一些调试信息
        if not filtered_messages and all_messages:
            logger.warning(f"未找到 {target_date} 的消息，但获取到了 {len(all_messages)} 条历史消息")
            # 显示最近几条消息的时间信息
            for i, msg in enumerate(all_messages[:5]):
                msg_time = msg.get("time", 0)
                msg_date = datetime.fromtimestamp(msg_time)
                logger.info(f"消息 {i+1}: {msg_date} - {msg.get('raw_message', '')[:50]}")
        
        return {
            "success": True,
            "data": filtered_messages
        }
        
    except Exception as e:
        logger.error(f"获取群历史消息异常: {e}")
        return {"success": False, "error": str(e)}


def optimize_message_data(messages: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    优化消息数据格式，使用message_id作为key，raw_message作为值
    
    Args:
        messages: 原始消息列表
        
    Returns:
        优化后的消息字典
    """
    optimized = {}
    
    for msg in messages:
        # 获取消息ID
        message_id = msg.get("message_id")
        if message_id is None:
            continue
            
        # 获取消息内容
        raw_message = msg.get("raw_message", "").strip()
        
        # 跳过空消息
        if not raw_message:
            continue
            
        # 使用message_id作为key
        optimized[str(message_id)] = raw_message
    
    return optimized


def format_messages_for_ai(messages: List[Dict[str, Any]]) -> str:
    """
    将消息格式化为AI可读的格式，优化token使用
    
    Args:
        messages: 消息列表
        
    Returns:
        格式化后的消息文本
    """
    formatted_lines = []
    
    for msg in messages:
        # 提取消息信息
        user_id = msg.get("user_id", "未知用户")
        content = msg.get("raw_message", "").strip()
        
        # 跳过空消息
        if not content:
            continue
            
        # 跳过机器人自己的消息（避免循环）
        if user_id == 3330219965:  # 机器人自己的ID
            continue
            
        # 跳过纯表情包和图片消息
        if (content.startswith("[CQ:image") or 
            content.startswith("[CQ:forward") or
            content in ["？", "。", "！", "?", ".", "!"] or
            len(content) < 2):
            continue
            
        # 跳过AI触发词消息（避免重复处理）
        if content.startswith("?ai "):
            # 提取问题部分
            question = content[4:].strip()
            if question:
                formatted_lines.append(f"用户{user_id}: {question}")
            continue
            
        # 跳过AI回复相关的消息
        if content in ["🤖 AI正在思考...", "请查收", "已截断"]:
            continue
            
        # 只保留有意义的文本消息
        if content and len(content) > 1:
            formatted_lines.append(f"用户{user_id}: {content}")
    
    return "\n".join(formatted_lines)


async def call_ai_for_summary(formatted_messages: str) -> Dict[str, Any]:
    """
    调用AI进行消息总结
    
    Args:
        formatted_messages: 格式化的消息文本
        
    Returns:
        AI处理结果字典
    """
    try:
        # 构建AI提示词
        prompt = f"""你是一个专业的技术内容分析师。请分析以下群聊记录，提取其中的技术答疑和知识共享内容。

分析要求：
1. 识别所有技术相关的讨论内容（编程、工具使用、问题解决等）
2. 将相同主题的内容合并到一起
3. 提取具体的解决方案、建议和知识点
4. 忽略纯闲聊、表情包、问候等非技术内容
5. 每个主题要包含清晰的名称和具体的方案列表

群聊记录：
{formatted_messages}

请严格按照以下JSON格式回复，不要添加任何其他文字：
[
  {{
    "name": "具体的技术主题名称",
    "方案": [
      "具体的解决方案或知识点1",
      "具体的解决方案或知识点2"
    ]
  }}
]

如果群聊中没有技术内容，请返回空数组：[]"""

        # 调用AI
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        result = await ai_manager.chat_completion(messages)
        
        if not result:
            return {"success": False, "error": "AI服务调用失败"}
        
        # 尝试解析AI返回的JSON
        try:
            # 清理AI返回的内容，提取JSON部分
            json_start = result.find('[')
            json_end = result.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = result[json_start:json_end]
                parsed_data = json.loads(json_str)
                
                return {
                    "success": True,
                    "data": parsed_data
                }
            else:
                # 如果没找到JSON格式，返回原始结果
                return {
                    "success": True,
                    "data": [{"name": "AI总结", "方案": [result]}]
                }
                
        except json.JSONDecodeError as e:
            logger.warning(f"AI返回内容JSON解析失败: {e}")
            # JSON解析失败，返回原始结果
            return {
                "success": True,
                "data": [{"name": "AI总结", "方案": [result]}]
            }
        
    except Exception as e:
        logger.error(f"AI总结调用异常: {e}")
        return {"success": False, "error": str(e)}


# 批量总结命令
batch_summary_cmd = on_command("批量总结", rule=to_me(), priority=5)


@batch_summary_cmd.handle()
async def handle_batch_summary_command(event: GroupMessageEvent, args=CommandArg()):
    """处理批量总结命令"""
    try:
        arg_str = str(args).strip()
        
        if not arg_str:
            logger.error("请指定要总结的天数，例如：批量总结 7")
            return
        
        try:
            days = int(arg_str)
            if days <= 0 or days > 30:
                logger.error("天数必须在1-30之间")
                return
        except ValueError:
            logger.error("天数必须是数字")
            return
        
        # 确保数据目录存在
        ensure_data_dirs()
        
        logger.info(f"开始批量总结最近 {days} 天的群消息")
        
        # 批量处理
        success_count = 0
        failed_dates = []
        
        for i in range(days):
            target_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            
            try:
                result = await process_group_summary(event.group_id, target_date)
                if result["success"]:
                    success_count += 1
                    logger.info(f"成功总结 {target_date} 的消息")
                else:
                    failed_dates.append(f"{target_date}: {result['error']}")
                    logger.warning(f"总结 {target_date} 失败: {result['error']}")
                
                # 避免请求过于频繁
                await asyncio.sleep(1)
                
            except Exception as e:
                failed_dates.append(f"{target_date}: {str(e)}")
                logger.error(f"总结 {target_date} 异常: {e}")
        
        # 记录结果
        logger.info(f"批量总结完成！成功: {success_count} 天")
        if failed_dates:
            logger.warning(f"失败: {len(failed_dates)} 天")
            if len(failed_dates) <= 5:  # 只显示前5个失败项
                logger.warning(f"失败详情: {'\n'.join(failed_dates[:5])}")
        
    except Exception as e:
        logger.error(f"批量总结命令处理异常: {e}")


# 日总结命令
def is_target_group() -> Rule:
    """检查是否在目标群中"""
    def _check(event: GroupMessageEvent) -> bool:
        return event.group_id in config.TARGET_GROUP_IDS
    return Rule(_check)

day_summary_cmd = on_command("ai_daySum", rule=is_target_group(), priority=5)


@day_summary_cmd.handle()
async def handle_day_summary_command(event: GroupMessageEvent, args=CommandArg()):
    """处理日总结命令"""
    try:
        # 检查是否在允许的群中
        if event.group_id not in config.TARGET_GROUP_IDS:
            return
        
        arg_str = str(args).strip()
        
        if not arg_str:
            # 默认总结今天的消息
            target_date = datetime.now().strftime("%Y-%m-%d")
        else:
            # 解析日期参数
            try:
                if arg_str == "今天":
                    target_date = datetime.now().strftime("%Y-%m-%d")
                elif arg_str == "昨天":
                    target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                else:
                    # 尝试解析日期格式 YYYYMMDD
                    if len(arg_str) == 8 and arg_str.isdigit():
                        # 格式：20250925 -> 2025-09-25
                        year = arg_str[:4]
                        month = arg_str[4:6]
                        day = arg_str[6:8]
                        target_date = f"{year}-{month}-{day}"
                        # 验证日期是否有效
                        datetime.strptime(target_date, "%Y-%m-%d")
                    else:
                        # 尝试解析标准日期格式 YYYY-MM-DD
                        datetime.strptime(arg_str, "%Y-%m-%d")
                        target_date = arg_str
            except ValueError:
                logger.error("日期格式错误，请使用 YYYYMMDD 格式（如20250925），或使用'今天'、'昨天'")
                return
        
        # 确保数据目录存在
        ensure_data_dirs()
        
        # 执行总结流程
        result = await process_group_summary(event.group_id, target_date)
        
        if result["success"]:
            summary_file = result["summary_file"]
            message_count = result["message_count"]
            logger.info(f"群消息总结完成！处理了 {message_count} 条消息，文件保存到: {summary_file}")
        else:
            logger.error(f"群消息总结失败: {result['error']}")
            
    except Exception as e:
        logger.error(f"日总结命令处理异常: {e}")


# 查看总结命令
view_summary_cmd = on_command("查看总结", rule=to_me(), priority=5)


@view_summary_cmd.handle()
async def handle_view_summary_command(event: GroupMessageEvent, args=CommandArg()):
    """处理查看总结命令"""
    try:
        arg_str = str(args).strip()
        
        if not arg_str:
            # 默认查看昨天的总结
            target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            try:
                if arg_str == "今天":
                    target_date = datetime.now().strftime("%Y-%m-%d")
                elif arg_str == "昨天":
                    target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                else:
                    datetime.strptime(arg_str, "%Y-%m-%d")
                    target_date = arg_str
            except ValueError:
                logger.error("日期格式错误，请使用 YYYY-MM-DD 格式，或使用'今天'、'昨天'")
                return
        
        # 查找总结文件
        summary_file = f"./data/daySummary/{event.group_id}-{target_date}-summary.json"
        
        if not os.path.exists(summary_file):
            logger.warning(f"未找到 {target_date} 的总结文件，请先运行群总结命令")
            return
        
        # 读取并显示总结
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary_data = json.load(f)
            
            summary_content = summary_data.get("summary", [])
            message_count = summary_data.get("message_count", 0)
            
            if not summary_content:
                logger.info(f"{target_date} 的总结为空")
                return
            
            # 格式化显示
            display_text = f"📊 {target_date} 群消息总结 (共{message_count}条消息)\n\n"
            
            for i, item in enumerate(summary_content, 1):
                name = item.get("name", "未知主题")
                solutions = item.get("方案", [])
                
                display_text += f"{i}. {name}\n"
                for j, solution in enumerate(solutions, 1):
                    display_text += f"   {j}) {solution}\n"
                display_text += "\n"
            
            # 记录总结内容到日志
            logger.info(f"查看总结内容: {display_text}")
            
        except Exception as e:
            logger.error(f"读取总结文件异常: {e}")
            
    except Exception as e:
        logger.error(f"查看总结命令处理异常: {e}")
