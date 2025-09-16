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
from config import config


# 创建命令处理器
random_handler = on_command("rand", priority=5)


@random_handler.handle()
async def handle_random(bot: Bot, event: GroupMessageEvent):
    """处理随机数生成请求"""
    try:
        # 生成指定范围内的随机整数
        random_number = random.randint(config.DEFAULT_RANDOM_MIN, config.DEFAULT_RANDOM_MAX)
        
        # 发送随机数
        await random_handler.finish(f"🎲 随机数：{random_number}")
        
    except Exception as e:
        # 检查是否是 FinishedException，如果是则不需要处理
        if "FinishedException" in str(type(e)):
            return
        logger.error(f"随机数生成插件错误: {e}")
        try:
            await random_handler.finish("随机数生成失败，请稍后重试")
        except:
            pass  # 如果已经 finish 过了，忽略错误


# 可选：添加更多随机数功能
random_range_handler = on_command("randrange", priority=5)


@random_range_handler.handle()
async def handle_random_range(bot: Bot, event: GroupMessageEvent):
    """处理指定范围的随机数生成请求"""
    try:
        # 获取命令参数
        args = str(event.get_message()).strip().split()
        
        if len(args) < 2:
            await random_range_handler.finish("用法：.randrange <最小值> <最大值>\n例如：.randrange 1 100")
            return
        
        try:
            min_val = int(args[1])
            max_val = int(args[2]) if len(args) > 2 else 100
            
            if min_val >= max_val:
                await random_range_handler.finish("最小值必须小于最大值")
                return
                
            if max_val - min_val > config.MAX_RANDOM_RANGE:
                await random_range_handler.finish(f"范围过大，最大支持 {config.MAX_RANDOM_RANGE} 的差值")
                return
                
        except ValueError:
            await random_range_handler.finish("请输入有效的数字")
            return
        
        # 生成指定范围的随机数
        random_number = random.randint(min_val, max_val)
        
        # 发送随机数
        await random_range_handler.finish(f"🎲 随机数 ({min_val}-{max_val})：{random_number}")
        
    except Exception as e:
        # 检查是否是 FinishedException，如果是则不需要处理
        if "FinishedException" in str(type(e)):
            return
        logger.error(f"范围随机数生成插件错误: {e}")
        try:
            await random_range_handler.finish("随机数生成失败，请稍后重试")
        except:
            pass  # 如果已经 finish 过了，忽略错误
