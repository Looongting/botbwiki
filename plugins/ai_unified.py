"""
统一AI对话插件
功能：智能识别AI触发词，统一处理所有AI服务的对话请求
替代原有的 ai_chat.py 和 ai_specific_chat.py
"""

import sys
import os
from nonebot import on_message, on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.rule import Rule
from nonebot.log import logger

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.config import config
from src.core.ai_manager import ai_manager
from src.core.message_sender import get_sender
from src.core.ai_handler import AIHandler


def ai_trigger_rule() -> Rule:
    """智能AI触发规则 - 支持默认和特定服务触发词"""
    def _check(event: GroupMessageEvent) -> bool:
        # 检查是否在目标群中
        if event.group_id not in config.TARGET_GROUP_IDS:
            return False
        
        message = str(event.get_message()).strip()
        
        # 使用配置类的智能识别方法
        result = config.get_service_by_trigger(message)
        return result is not None
    
    return Rule(_check)


# 创建统一AI对话处理器 - 使用最高优先级确保及时响应
unified_ai_handler = on_message(rule=ai_trigger_rule(), priority=2)


@unified_ai_handler.handle()
async def handle_unified_ai_chat(bot: Bot, event: GroupMessageEvent):
    """统一的AI对话处理"""
    try:
        message = str(event.get_message()).strip()
        
        # 智能识别使用哪个AI服务
        service_info = config.get_service_by_trigger(message)
        if not service_info:
            return  # 不应该发生，但防御性编程
        
        service_name, trigger_prefix = service_info
        
        # 如果是特定服务，检查该服务是否可用
        if service_name is not None:
            service_config = config.AI_SERVICES.get(service_name, {})
            if not service_config.get("api_key"):
                # 使用引用回复告知用户该AI未配置
                message_sender = get_sender()
                await message_sender.send_reply_with_reference(
                    event, 
                    f"❌ {service_config.get('name', service_name)} 未配置API密钥"
                )
                return
            
            # 获取服务显示名称
            service_display_name = service_config.get('name', service_name)
        else:
            # 使用默认服务
            service_display_name = None
        
        # 创建AI处理器并处理请求
        ai_handler = AIHandler(ai_manager, get_sender())
        await ai_handler.process_ai_request(
            event=event,
            trigger_prefix=trigger_prefix,
            service_name=service_name,
            service_display_name=service_display_name
        )
        
    except Exception as e:
        # 忽略FinishedException，这是NoneBot正常的结束异常
        if "FinishedException" not in str(type(e)):
            logger.error(f"统一AI对话插件错误: {e}")
            try:
                message_sender = get_sender()
                await message_sender.send_reply_with_reference(event, "❌ AI服务异常，请稍后重试")
            except:
                pass  # 避免在错误处理中再次出错


# ====================================
# AI管理命令
# ====================================

# AI测试命令
ai_test_handler = on_command("ai_test", priority=5)


@ai_test_handler.handle()
async def handle_ai_test(bot: Bot, event: GroupMessageEvent):
    """AI连接测试"""
    try:
        # 检查是否在允许的群中
        if event.group_id not in config.TARGET_GROUP_IDS:
            return
        
        # 使用统一的AI处理器
        ai_handler = AIHandler(ai_manager, get_sender())
        await ai_handler.test_ai_connection(event)
        
    except Exception as e:
        # 忽略FinishedException，这是NoneBot正常的结束异常
        if "FinishedException" not in str(type(e)):
            logger.error(f"AI测试命令错误: {e}")
            try:
                message_sender = get_sender()
                await message_sender.send_reply(event, "❌ AI测试失败，请稍后重试")
            except:
                pass


# AI服务状态查询命令
ai_status_handler = on_command("ai_status", priority=5)


@ai_status_handler.handle()
async def handle_ai_status(bot: Bot, event: GroupMessageEvent):
    """查询AI服务状态"""
    try:
        # 检查是否在允许的群中
        if event.group_id not in config.TARGET_GROUP_IDS:
            return
        
        # 使用统一的AI处理器
        ai_handler = AIHandler(ai_manager, get_sender())
        await ai_handler.get_ai_status(event)
        
    except Exception as e:
        # 忽略FinishedException，这是NoneBot正常的结束异常
        if "FinishedException" not in str(type(e)):
            logger.error(f"AI状态查询命令错误: {e}")
            try:
                message_sender = get_sender()
                await message_sender.send_reply(event, "❌ 查询AI状态失败")
            except:
                pass


# ====================================
# 特定服务测试命令（可选）
# ====================================

# 可以添加特定服务的测试命令，例如：
# ?test_glm, ?test_longcat, ?test_volc 等
# 这些命令可以测试特定AI服务的连接状态

def create_service_test_command(service_name: str):
    """动态创建特定服务的测试命令"""
    command_name = f"test_{service_name}"
    test_handler = on_command(command_name, priority=5)
    
    @test_handler.handle()
    async def handle_service_test(bot: Bot, event: GroupMessageEvent):
        try:
            # 检查是否在允许的群中
            if event.group_id not in config.TARGET_GROUP_IDS:
                return
            
            # 检查服务是否存在
            if service_name not in config.AI_SERVICES:
                message_sender = get_sender()
                await message_sender.send_reply(event, f"❌ 未知的AI服务: {service_name}")
                return
            
            # 使用统一的AI处理器测试特定服务
            ai_handler = AIHandler(ai_manager, get_sender())
            await ai_handler.test_ai_connection(event, service_name)
            
        except Exception as e:
            # 忽略FinishedException，这是NoneBot正常的结束异常
            if "FinishedException" not in str(type(e)):
                logger.error(f"AI服务 {service_name} 测试命令错误: {e}")
                try:
                    message_sender = get_sender()
                    await message_sender.send_reply(event, f"❌ {service_name} 测试失败，请稍后重试")
                except:
                    pass
    
    return test_handler


# 为所有配置的AI服务创建测试命令
for service_name in config.AI_SERVICES.keys():
    create_service_test_command(service_name)


logger.info("统一AI对话插件已加载")
logger.info(f"支持的AI服务: {list(config.AI_SERVICES.keys())}")
logger.info(f"可用的AI服务: {config.available_ai_services}")
logger.info(f"默认AI触发词: {config.AI_TRIGGER_PREFIX}")

# 显示所有特定服务的触发词
for service_name, service_config in config.AI_SERVICES.items():
    trigger_prefix = service_config.get('trigger_prefix', '')
    if trigger_prefix:
        logger.info(f"{service_config.get('name', service_name)} 触发词: {trigger_prefix}")
