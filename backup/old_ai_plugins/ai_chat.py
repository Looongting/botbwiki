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
from src.core.message_sender import get_sender


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
        # 获取消息发送器
        message_sender = get_sender()
        
        # 提取用户问题
        message = str(event.get_message()).strip()
        user_question = message[len(config.AI_TRIGGER_PREFIX):].strip()
        
        if not user_question:
            # 使用引用回复发送用法说明
            await message_sender.send_reply_with_reference(
                event,
                f"用法：{config.AI_TRIGGER_PREFIX} <你的问题>\n"
                f"例如：{config.AI_TRIGGER_PREFIX} 今天天气怎么样？"
            )
            return
        
        # 发送思考中的提示
        await message_sender.send_reply(event, "🤖 AI正在思考...")
        
        # 构建消息 - 在用户问题前添加配置的prompt前缀
        full_question = f"{config.AI_PROMPT_PREFIX}{user_question}"
        messages = [
            {"role": "user", "content": full_question}
        ]
        
        # 获取默认AI服务配置
        default_config = config.default_ai_service_config
        if not default_config:
            await message_sender.send_reply_with_reference(event, "❌ 没有可用的AI服务，请检查配置")
            return
        
        # 找到默认AI服务名称
        default_service = None
        for service_name, service_config in config.AI_SERVICES.items():
            if service_config == default_config:
                default_service = service_name
                break
        
        # 调用默认AI服务
        result = await ai_manager.chat_completion(messages, default_service)
        
        if result:
            # 直接使用AI的完整回复，不进行截断
            service_name = default_config.get('name', default_service)
            await message_sender.send_reply_with_reference(event, f"🤖 {service_name}回复：\n{result}")
        else:
            # 尝试使用其他可用服务
            available_services = ai_manager.get_available_services()
            if len(available_services) > 1:
                # 尝试其他可用服务
                for service in available_services:
                    if service != default_service:
                        logger.info(f"尝试使用备用AI服务: {service}")
                        result = await ai_manager.chat_completion(messages, service)
                        if result:
                            # 直接使用AI的完整回复，不进行截断
                            service_name = config.AI_SERVICES.get(service, {}).get('name', service)
                            await message_sender.send_reply_with_reference(event, f"🤖 {service_name}回复：\n{result}")
                            return
            
            # 使用引用回复发送错误信息
            await message_sender.send_reply_with_reference(event, "❌ AI暂时无法回复，请稍后重试")
            
    except asyncio.TimeoutError:
        await message_sender.send_reply_with_reference(event, "⏰ AI响应超时，请稍后重试")
    except Exception as e:
        # 忽略FinishedException，这是NoneBot正常的结束异常
        if "FinishedException" not in str(type(e)):
            logger.error(f"AI对话插件错误: {e}")
            await message_sender.send_reply_with_reference(event, "❌ AI服务异常，请稍后重试")


# AI测试命令 - 保持命令形式，方便管理员测试
from nonebot import on_command

ai_test_handler = on_command("ai_test", priority=5)


@ai_test_handler.handle()
async def handle_ai_test(bot: Bot, event: GroupMessageEvent):
    """处理AI测试请求"""
    try:
        # 获取消息发送器
        message_sender = get_sender()
        
        # 检查是否在允许的群中
        if event.group_id not in config.TARGET_GROUP_IDS:
            return
        
        await message_sender.send_reply(event, "🤖 正在测试AI连接...")
        
        # 获取默认AI服务配置
        default_config = config.default_ai_service_config
        if not default_config:
            await message_sender.send_reply(event, "❌ 没有可用的AI服务，请检查配置")
            return
        
        # 找到默认AI服务名称
        default_service = None
        for service_name, service_config in config.AI_SERVICES.items():
            if service_config == default_config:
                default_service = service_name
                break
        
        # 测试默认AI服务
        success, message = await ai_manager.test_connection(default_service)
        
        if success:
            await message_sender.send_reply(event, f"✅ AI测试成功！\n\n使用的服务: {default_config.get('name', default_service)}\nAI回复：{message}")
        else:
            # 尝试其他可用服务
            available_services = ai_manager.get_available_services()
            if len(available_services) > 1:
                for service in available_services:
                    if service != default_service:
                        success, message = await ai_manager.test_connection(service)
                        if success:
                            service_name = config.AI_SERVICES.get(service, {}).get('name', service)
                            await message_sender.send_reply(event, f"⚠️ 默认AI服务失败，但备用服务可用\n\n使用的服务: {service_name}\nAI回复：{message}")
                            return
            
            await message_sender.send_reply(event, f"❌ AI测试失败\n\n错误信息：{message}")
            
    except Exception as e:
        # 忽略FinishedException，这是NoneBot正常的结束异常
        if "FinishedException" not in str(type(e)):
            logger.error(f"AI测试插件错误: {e}")
            await message_sender.send_reply(event, "❌ AI测试失败，请稍后重试")


# AI服务状态查询命令
ai_status_handler = on_command("ai_status", priority=5)


@ai_status_handler.handle()
async def handle_ai_status(bot: Bot, event: GroupMessageEvent):
    """查询AI服务状态"""
    try:
        # 获取消息发送器
        message_sender = get_sender()
        
        # 检查是否在允许的群中
        if event.group_id not in config.TARGET_GROUP_IDS:
            return
        
        # 获取可用服务
        available_services = ai_manager.get_available_services()
        
        status_info = f"🤖 AI服务状态\n\n"
        status_info += f"默认触发词：{config.AI_TRIGGER_PREFIX}\n"
        
        # 显示所有AI服务状态
        for service_name, service_config in config.AI_SERVICES.items():
            service_display_name = service_config.get('name', service_name)
            trigger_prefix = service_config.get('trigger_prefix', '')
            enabled = service_config.get('enabled', False)
            status = "✅ 启用" if enabled else "❌ 未启用"
            status_info += f"• {service_display_name}: {status} ({trigger_prefix})\n"
        
        status_info += f"\n可用服务：{', '.join([config.AI_SERVICES.get(s, {}).get('name', s) for s in available_services]) if available_services else '无'}\n"
        
        if available_services:
            status_info += f"\n使用方法：\n"
            status_info += f"• {config.AI_TRIGGER_PREFIX} <问题> - 使用默认AI\n"
            for service_name in available_services:
                service_config = config.AI_SERVICES.get(service_name, {})
                trigger_prefix = service_config.get('trigger_prefix', '')
                service_display_name = service_config.get('name', service_name)
                if trigger_prefix:
                    status_info += f"• {trigger_prefix} <问题> - 使用{service_display_name}\n"
        else:
            status_info += "\n⚠️ 当前没有可用的AI服务，请检查配置"
        
        await message_sender.send_reply(event, status_info)
        
    except Exception as e:
        # 忽略FinishedException，这是NoneBot正常的结束异常
        if "FinishedException" not in str(type(e)):
            logger.error(f"AI状态查询错误: {e}")
            await message_sender.send_reply(event, "❌ 查询AI状态失败")
