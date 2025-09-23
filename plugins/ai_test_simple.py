"""
简化的AI测试插件
用于测试AI功能是否正常工作
"""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.log import logger
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from src.core.config import config


# 创建命令处理器
ai_test_simple_handler = on_command("ai_test_simple", priority=5, aliases={"?ai_test_simple"})


@ai_test_simple_handler.handle()
async def handle_ai_test_simple(bot: Bot, event: GroupMessageEvent):
    """处理AI简单测试请求"""
    try:
        logger.info("AI简单测试命令被触发")
        await ai_test_simple_handler.finish("✅ AI简单测试成功！插件正常工作")
        
    except Exception as e:
        logger.error(f"AI简单测试插件错误: {e}")
        try:
            await ai_test_simple_handler.finish("AI简单测试失败，请稍后重试")
        except:
            pass
