"""
AI特定服务对话插件
功能：监听群消息中的特定AI服务触发词（?lc、?volc、?glm等），提供特定AI服务对话功能
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


def is_specific_ai_trigger() -> Rule:
    """检查消息是否包含特定AI服务触发词"""
    def _check(event: GroupMessageEvent) -> bool:
        # 检查是否在目标群中
        if event.group_id not in config.TARGET_GROUP_IDS:
            return False
        
        message = str(event.get_message()).strip()
        
        # 检查是否以任何AI服务的触发前缀开头
        for service_name, service_config in config.AI_SERVICES.items():
            trigger_prefix = service_config.get("trigger_prefix", "")
            if trigger_prefix and message.startswith(trigger_prefix + " "):
                return True
        
        return False
    
    return Rule(_check)


# 创建特定AI对话处理器 - 使用较高优先级确保及时响应
specific_ai_chat_handler = on_message(rule=is_specific_ai_trigger(), priority=2)


@specific_ai_chat_handler.handle()
async def handle_specific_ai_chat(bot: Bot, event: GroupMessageEvent):
    """处理特定AI服务对话请求"""
    try:
        # 获取消息发送器
        message_sender = get_sender()
        
        # 获取消息内容
        message = str(event.get_message()).strip()
        
        # 找到匹配的AI服务
        matched_service = None
        matched_config = None
        trigger_prefix = None
        
        for service_name, service_config in config.AI_SERVICES.items():
            prefix = service_config.get("trigger_prefix", "")
            if prefix and message.startswith(prefix + " "):
                matched_service = service_name
                matched_config = service_config
                trigger_prefix = prefix
                break
        
        if not matched_service:
            return  # 不应该发生，但防御性编程
        
        # 检查该AI服务是否启用
        if not matched_config.get("enabled", False):
            # 使用引用回复告知用户该AI未开放
            await message_sender.send_reply_with_reference(
                event, 
                f"❌ {matched_config.get('name', matched_service)} 未开放"
            )
            return
        
        # 提取用户问题
        user_question = message[len(trigger_prefix):].strip()
        
        if not user_question:
            # 使用引用回复发送用法说明
            await message_sender.send_reply_with_reference(
                event,
                f"用法：{trigger_prefix} <你的问题>\n"
                f"例如：{trigger_prefix} 今天天气怎么样？"
            )
            return
        
        # 发送思考中的提示
        await message_sender.send_reply(event, f"🤖 {matched_config.get('name', matched_service)}正在思考...")
        
        # 构建消息 - 在用户问题前添加配置的prompt前缀
        full_question = f"{config.AI_PROMPT_PREFIX}{user_question}"
        messages = [
            {"role": "user", "content": full_question}
        ]
        
        # 调用指定的AI服务
        result = await ai_manager.chat_completion(messages, matched_service)
        
        if result:
            # 直接使用AI的完整回复，不进行截断
            await message_sender.send_reply_with_reference(
                event, 
                f"🤖 {matched_config.get('name', matched_service)}回复：\n{result}"
            )
        else:
            # 使用引用回复发送错误信息
            await message_sender.send_reply_with_reference(
                event, 
                f"❌ {matched_config.get('name', matched_service)}暂时无法回复，请稍后重试"
            )
            
    except asyncio.TimeoutError:
        await message_sender.send_reply_with_reference(event, "⏰ AI响应超时，请稍后重试")
    except Exception as e:
        # 忽略FinishedException，这是NoneBot正常的结束异常
        if "FinishedException" not in str(type(e)):
            logger.error(f"特定AI对话插件错误: {e}")
            await message_sender.send_reply_with_reference(event, "❌ AI服务异常，请稍后重试")
