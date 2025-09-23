#!/usr/bin/env python3
"""
QQ 机器人主程序
基于 Nonebot2 框架，提供短链生成和随机数生成功能
"""

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.log import logger
import os
import sys
from dotenv import load_dotenv

# 添加src目录到Python路径
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))

# 加载环境变量
load_dotenv(os.path.join(project_root, '.env'))

# 初始化 Nonebot
nonebot.init(
    driver="~httpx+~websockets",
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    command_start={"?", "."}  # 设置命令前缀为?和.（兼容）
)

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

# 加载插件
nonebot.load_plugins("plugins")

# 配置日志
log_file = os.getenv("LOG_FILE", "bot.log")
if not os.path.isabs(log_file):
    log_file = os.path.join(project_root, "logs", log_file)
logger.add(
    log_file,
    rotation="1 day",
    retention="7 days",
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
)

if __name__ == "__main__":
    logger.info("正在启动 QQ 机器人...")
    nonebot.run()
