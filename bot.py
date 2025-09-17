#!/usr/bin/env python3
"""
QQ 机器人主程序
基于 Nonebot2 框架，提供短链生成和随机数生成功能
"""

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.log import logger
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化 Nonebot
nonebot.init(
    driver="~httpx+~websockets",
    log_level=os.getenv("LOG_LEVEL", "INFO")
)

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

# 加载插件
nonebot.load_plugins("plugins")

# 配置日志
logger.add(
    os.getenv("LOG_FILE", "bot.log"),
    rotation="1 day",
    retention="7 days",
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
)

if __name__ == "__main__":
    logger.info("正在启动 QQ 机器人...")
    nonebot.run()
