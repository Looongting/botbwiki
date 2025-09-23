"""
AI对话插件
功能：监听群消息中的AI触发词，提供AI对话功能
"""

import asyncio
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.rule import Rule
from nonebot.log import logger
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.config import config
from src.core.ai_manager import ai_manager


def is_ai_trigger() -> Rule:
    """检查消息是否包含AI触发词"""
    def _check(event: GroupMessageEvent) -> bool:
        # 检查是否在目标群中
        if event.group_id not in config.TARGET_GROUP_IDS:
            return False
        
        message = str(event.get_message()).strip()
        
        # 检查是否以AI触发词开头
        if message.startswith(config.AI_TRIGGER_PREFIX + " "):
            return True
        
        return False
    
    return Rule(_check)


# 创建AI对话处理器 - 使用较高优先级确保及时响应
ai_chat_handler = on_message(rule=is_ai_trigger(), priority=3)


@ai_chat_handler.handle()
async def handle_ai_chat(bot: Bot, event: GroupMessageEvent):
    """处理AI对话请求"""
    try:
        # 提取用户问题
        message = str(event.get_message()).strip()
        user_question = message[len(config.AI_TRIGGER_PREFIX):].strip()
        
        if not user_question:
            await ai_chat_handler.finish(
                f"用法：{config.AI_TRIGGER_PREFIX} <你的问题>\n"
                f"例如：{config.AI_TRIGGER_PREFIX} 今天天气怎么样？"
            )
            return
        
        # 发送思考中的提示
        await ai_chat_handler.send("🤖 AI正在思考...")
        
        # 构建消息
        messages = [
            {"role": "user", "content": user_question}
        ]
        
        # 调用AI服务
        result = await ai_manager.chat_completion(messages)
        
        if result:
            # 限制回复长度，避免消息过长
            max_length = 1000
            if len(result) > max_length:
                result = result[:max_length] + "...\n\n[回复内容过长，已截断]"
            
            await ai_chat_handler.finish(f"🤖 AI回复：\n{result}")
        else:
            # 尝试使用备用AI服务
            available_services = ai_manager.get_available_services()
            if len(available_services) > 1:
                # 尝试其他可用服务
                for service in available_services:
                    if service != config.DEFAULT_AI_SERVICE:
                        logger.info(f"尝试使用备用AI服务: {service}")
                        result = await ai_manager.chat_completion(messages, service)
                        if result:
                            max_length = 1000
                            if len(result) > max_length:
                                result = result[:max_length] + "...\n\n[回复内容过长，已截断]"
                            await ai_chat_handler.finish(f"🤖 AI回复：\n{result}")
                            return
            
            await ai_chat_handler.finish("❌ AI暂时无法回复，请稍后重试")
            
    except asyncio.TimeoutError:
        await ai_chat_handler.finish("⏰ AI响应超时，请稍后重试")
    except Exception as e:
        # 忽略FinishedException，这是NoneBot正常的结束异常
        if "FinishedException" not in str(type(e)):
            logger.error(f"AI对话插件错误: {e}")
            await ai_chat_handler.finish("❌ AI服务异常，请稍后重试")


# AI测试命令 - 保持命令形式，方便管理员测试
from nonebot import on_command

ai_test_handler = on_command("ai_test", priority=5)


@ai_test_handler.handle()
async def handle_ai_test(bot: Bot, event: GroupMessageEvent):
    """处理AI测试请求"""
    try:
        # 检查是否在允许的群中
        if event.group_id not in config.TARGET_GROUP_IDS:
            return
        
        await ai_test_handler.send("🤖 正在测试AI连接...")
        
        # 测试默认AI服务
        success, message = await ai_manager.test_connection()
        
        if success:
            await ai_test_handler.finish(f"✅ AI测试成功！\n\n使用的服务: {config.DEFAULT_AI_SERVICE}\nAI回复：{message}")
        else:
            # 尝试其他可用服务
            available_services = ai_manager.get_available_services()
            if len(available_services) > 1:
                for service in available_services:
                    if service != config.DEFAULT_AI_SERVICE:
                        success, message = await ai_manager.test_connection(service)
                        if success:
                            await ai_test_handler.finish(f"⚠️ 默认AI服务失败，但备用服务可用\n\n使用的服务: {service}\nAI回复：{message}")
                            return
            
            await ai_test_handler.finish(f"❌ AI测试失败\n\n错误信息：{message}")
            
    except Exception as e:
        # 忽略FinishedException，这是NoneBot正常的结束异常
        if "FinishedException" not in str(type(e)):
            logger.error(f"AI测试插件错误: {e}")
            await ai_test_handler.finish("❌ AI测试失败，请稍后重试")


# AI服务状态查询命令
ai_status_handler = on_command("ai_status", priority=5)


@ai_status_handler.handle()
async def handle_ai_status(bot: Bot, event: GroupMessageEvent):
    """查询AI服务状态"""
    try:
        # 检查是否在允许的群中
        if event.group_id not in config.TARGET_GROUP_IDS:
            return
        
        # 获取可用服务
        available_services = ai_manager.get_available_services()
        
        status_info = f"🤖 AI服务状态\n\n"
        status_info += f"触发词：{config.AI_TRIGGER_PREFIX}\n"
        status_info += f"默认服务：{config.DEFAULT_AI_SERVICE}\n"
        status_info += f"可用服务：{', '.join(available_services) if available_services else '无'}\n\n"
        
        if available_services:
            status_info += f"使用方法：{config.AI_TRIGGER_PREFIX} <你的问题>"
        else:
            status_info += "⚠️ 当前没有可用的AI服务，请检查配置"
        
        await ai_status_handler.finish(status_info)
        
    except Exception as e:
        # 忽略FinishedException，这是NoneBot正常的结束异常
        if "FinishedException" not in str(type(e)):
            logger.error(f"AI状态查询错误: {e}")
            await ai_status_handler.finish("❌ 查询AI状态失败")
