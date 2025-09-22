"""
AI总结插件
功能：调用火山引擎AI对群消息进行总结分析
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import httpx
import hashlib
import hmac
from urllib.parse import urlencode

try:
    from volcengine.maas import MaasService, MaasException
    VOLC_SDK_AVAILABLE = True
except ImportError:
    VOLC_SDK_AVAILABLE = False

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.log import logger
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config


class VolcAI:
    """火山引擎AI客户端"""
    
    def __init__(self):
        self.api_key = config.ARK_API_KEY
        self.region = config.VOLC_AI_REGION
        self.endpoint = config.VOLC_AI_ENDPOINT
        self.api_url = config.VOLC_AI_API_URL
        self.max_tokens = config.AI_SUMMARY_MAX_TOKENS
        self.timeout = config.AI_SUMMARY_TIMEOUT
    
    async def chat_completion(self, messages: List[Dict[str, str]], model: str = "ep-20250811175605-fxzbh") -> Optional[str]:
        """调用火山引擎AI聊天完成API"""
        if not self.api_key:
            logger.error("火山引擎AI配置不完整，请检查ARK_API_KEY")
            return None
        
        try:
            # 准备请求数据
            data = {
                "model": model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": 0.7,
                "stream": False
            }
            
            body = json.dumps(data, ensure_ascii=False)
            
            # 准备请求头 - 使用火山方舟API Key
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 发送请求
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    content=body
                )
                
                logger.info(f"AI API响应状态: {response.status_code}")
                logger.info(f"AI API响应内容: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    else:
                        logger.error(f"AI响应格式异常: {result}")
                        return None
                else:
                    logger.error(f"AI API调用失败: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"调用火山引擎AI时发生错误: {e}")
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误详情: {str(e)}")
            import traceback
            logger.error(f"完整堆栈跟踪: {traceback.format_exc()}")
            return None


# 创建AI客户端实例
volc_ai = VolcAI()

# 创建命令处理器 - 使用?作为前缀
ai_test_handler = on_command("ai_test", priority=5)
ai_summary_handler = on_command("ai_summary", priority=5)


@ai_test_handler.handle()
async def handle_ai_test(bot: Bot, event: GroupMessageEvent):
    """处理AI测试请求"""
    try:
        # 检查是否在允许的群中
        if event.group_id not in config.TARGET_GROUP_IDS:
            return  # 不在目标群中，不响应
        # 简单的测试prompt
        test_messages = [
            {"role": "user", "content": "请简单介绍一下你自己，用一句话即可。"}
        ]
        
        await ai_test_handler.send("🤖 正在测试AI连接...")
        
        # 调用AI
        result = await volc_ai.chat_completion(test_messages)
        
        if result:
            await ai_test_handler.finish(f"✅ AI测试成功！\n\nAI回复：{result}")
        else:
            await ai_test_handler.finish("❌ AI测试失败，请检查配置或稍后重试")
            
    except Exception as e:
        # 忽略FinishedException，这是NoneBot正常的结束异常
        if "FinishedException" not in str(type(e)):
            logger.error(f"AI测试插件错误: {e}")
            try:
                await ai_test_handler.finish("AI测试失败，请稍后重试")
            except:
                pass


@ai_summary_handler.handle()
async def handle_ai_summary(bot: Bot, event: GroupMessageEvent):
    """处理AI总结请求"""
    try:
        # 检查是否在允许的群中
        if event.group_id not in config.TARGET_GROUP_IDS:
            return  # 不在目标群中，不响应
        # 获取命令参数
        args = str(event.get_message()).strip().split()
        
        if len(args) < 1:
            await ai_summary_handler.finish(
                "用法：?ai_summary [日期]\n"
                "例如：?ai_summary          # 总结昨天的消息\n"
                "例如：?ai_summary 2024-01-15  # 总结指定日期的消息\n"
                f"说明：总结当前群({event.group_id})的技术讨论内容"
            )
            return
        
        # 解析日期参数
        target_date = None
        if len(args) > 1:
            try:
                date_str = args[1]
                target_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                await ai_summary_handler.finish("日期格式错误，请使用 YYYY-MM-DD 格式")
                return
        
        # 导入总结管理器
        from ai_summary_manager import ai_summary_manager
        
        # 发送开始消息
        date_desc = target_date.strftime("%Y年%m月%d日") if target_date else "昨天"
        await ai_summary_handler.send(f"📊 正在生成群 {event.group_id} {date_desc} 的技术讨论总结...")
        
        # 生成总结（使用当前群ID）
        success = await ai_summary_manager.generate_daily_summary(target_date, event.group_id)
        
        if success:
            date_for_file = target_date if target_date else datetime.now() - timedelta(days=1)
            filename = f"summary_{date_for_file.strftime('%Y%m%d')}.md"
            filepath = f"{config.AI_LOG_DIR}/{filename}"
            
            await ai_summary_handler.finish(
                f"✅ 总结生成成功！\n"
                f"📁 文件已保存到: {filepath}\n"
                f"📋 内容包含：MediaWiki技术问题分析、解决方案汇总、讨论热点等"
            )
        else:
            await ai_summary_handler.finish("❌ 总结生成失败，请检查配置或稍后重试")
            
    except Exception as e:
        # 忽略FinishedException，这是NoneBot正常的结束异常
        if "FinishedException" not in str(type(e)):
            logger.error(f"AI总结插件错误: {e}")
            try:
                await ai_summary_handler.finish("消息总结失败，请稍后重试")
            except:
                pass


# 添加一个简单的AI对话功能用于测试
ai_chat_handler = on_command("ai", priority=5)

# 添加定时总结功能
ai_auto_summary_handler = on_command("ai_auto", priority=5)


@ai_chat_handler.handle()
async def handle_ai_chat(bot: Bot, event: GroupMessageEvent):
    """处理AI对话请求"""
    try:
        # 检查是否在允许的群中
        if event.group_id not in config.TARGET_GROUP_IDS:
            return  # 不在目标群中，不响应
        # 获取用户输入
        user_input = str(event.get_message()).strip()
        if user_input.startswith("?ai "):
            user_input = user_input[4:]  # 移除 "?ai " 前缀
        elif user_input.startswith(".ai "):
            user_input = user_input[4:]  # 移除 ".ai " 前缀（兼容旧格式）
        
        if not user_input:
            await ai_chat_handler.finish("用法：?ai <你的问题>\n例如：?ai 今天天气怎么样？")
            return
        
        await ai_chat_handler.send("🤖 AI正在思考...")
        
        # 调用AI
        messages = [
            {"role": "user", "content": user_input}
        ]
        
        result = await volc_ai.chat_completion(messages)
        
        if result:
            await ai_chat_handler.finish(f"🤖 AI回复：\n{result}")
        else:
            await ai_chat_handler.finish("❌ AI回复失败，请稍后重试")
            
    except Exception as e:
        # 忽略FinishedException，这是NoneBot正常的结束异常
        if "FinishedException" not in str(type(e)):
            logger.error(f"AI对话插件错误: {e}")
            try:
                await ai_chat_handler.finish("AI对话失败，请稍后重试")
            except:
                pass


@ai_auto_summary_handler.handle()
async def handle_ai_auto_summary(bot: Bot, event: GroupMessageEvent):
    """处理自动总结请求"""
    try:
        # 检查是否在允许的群中
        if event.group_id not in config.TARGET_GROUP_IDS:
            return  # 不在目标群中，不响应
        # 检查权限（只有管理员可以使用）
        if event.user_id != config.BOT_MASTER_ID:
            await ai_auto_summary_handler.finish("❌ 只有管理员可以使用此功能")
            return
        
        # 获取命令参数
        args = str(event.get_message()).strip().split()
        
        if len(args) < 2:
            await ai_auto_summary_handler.finish(
                "用法：?ai_auto <天数>\n"
                "例如：?ai_auto 7    # 生成过去7天的总结\n"
                "例如：?ai_auto 1    # 生成昨天的总结\n"
                f"说明：批量生成当前群({event.group_id})的技术讨论总结"
            )
            return
        
        try:
            days = int(args[1])
            if days <= 0 or days > 30:
                await ai_auto_summary_handler.finish("天数必须在1-30之间")
                return
        except ValueError:
            await ai_auto_summary_handler.finish("请输入有效的天数")
            return
        
        # 导入总结管理器
        from ai_summary_manager import ai_summary_manager
        
        # 计算日期范围
        end_date = datetime.now() - timedelta(days=1)  # 昨天
        start_date = end_date - timedelta(days=days-1)  # 开始日期
        
        await ai_auto_summary_handler.send(
            f"📊 开始批量生成群 {event.group_id} 从 {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')} 的总结..."
        )
        
        # 批量生成总结（使用当前群ID）
        generated_files = await ai_summary_manager.generate_summary_for_date_range(start_date, end_date, event.group_id)
        
        if generated_files:
            file_list = "\n".join([f"  - {os.path.basename(f)}" for f in generated_files])
            await ai_auto_summary_handler.finish(
                f"✅ 批量总结生成完成！\n"
                f"📁 共生成 {len(generated_files)} 个总结文件：\n{file_list}\n"
                f"📂 保存目录：{config.AI_LOG_DIR}"
            )
        else:
            await ai_auto_summary_handler.finish("❌ 没有生成任何总结文件，请检查配置或数据")
            
    except Exception as e:
        # 忽略FinishedException，这是NoneBot正常的结束异常
        if "FinishedException" not in str(type(e)):
            logger.error(f"自动总结插件错误: {e}")
            try:
                await ai_auto_summary_handler.finish("自动总结失败，请稍后重试")
            except:
                pass
