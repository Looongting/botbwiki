"""
随机数生成插件
功能：响应 .rand 命令，生成 1-100 之间的随机整数
"""

import random
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
from src.core.message_sender import get_sender


# 创建命令处理器
random_handler = on_command("rand", priority=5)


@random_handler.handle()
async def handle_random(bot: Bot, event: GroupMessageEvent):
    """处理随机数生成请求"""
    try:
        # 获取消息发送器
        message_sender = get_sender()
        
        # 生成指定范围内的随机整数
        random_number = random.randint(config.DEFAULT_RANDOM_MIN, config.DEFAULT_RANDOM_MAX)
        
        # 使用新的消息发送器发送随机数
        await message_sender.send_reply(event, f"🎲 随机数：{random_number}")
        
    except Exception as e:
        # 检查是否是 FinishedException，如果是则不需要处理
        if "FinishedException" in str(type(e)):
            return
        logger.error(f"随机数生成插件错误: {e}")
        try:
            message_sender = get_sender()
            await message_sender.send_reply(event, "随机数生成失败，请稍后重试")
        except:
            pass  # 如果已经发送过了，忽略错误


# 可选：添加更多随机数功能
random_range_handler = on_command("randrange", priority=5)


@random_range_handler.handle()
async def handle_random_range(bot: Bot, event: GroupMessageEvent):
    """处理指定范围的随机数生成请求"""
    try:
        # 获取消息发送器
        message_sender = get_sender()
        
        # 获取命令参数
        args = str(event.get_message()).strip().split()
        
        if len(args) < 2:
            await message_sender.send_reply(event, "用法：.randrange <最小值> <最大值>\n例如：.randrange 1 100")
            return
        
        try:
            min_val = int(args[1])
            max_val = int(args[2]) if len(args) > 2 else 100
            
            if min_val >= max_val:
                await message_sender.send_reply(event, "最小值必须小于最大值")
                return
                
            if max_val - min_val > config.MAX_RANDOM_RANGE:
                await message_sender.send_reply(event, f"范围过大，最大支持 {config.MAX_RANDOM_RANGE} 的差值")
                return
                
        except ValueError:
            await message_sender.send_reply(event, "请输入有效的数字")
            return
        
        # 生成指定范围的随机数
        random_number = random.randint(min_val, max_val)
        
        # 使用新的消息发送器发送随机数
        await message_sender.send_reply(event, f"🎲 随机数 ({min_val}-{max_val})：{random_number}")
        
    except Exception as e:
        # 检查是否是 FinishedException，如果是则不需要处理
        if "FinishedException" in str(type(e)):
            return
        logger.error(f"范围随机数生成插件错误: {e}")
        try:
            message_sender = get_sender()
            await message_sender.send_reply(event, "随机数生成失败，请稍后重试")
        except:
            pass  # 如果已经发送过了，忽略错误
