"""
机器人配置文件
"""

import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """机器人配置类"""
    
    # Onebot 连接配置
    ONEBOT_WS_URL: str = os.getenv("ONEBOT_WS_URL", "ws://127.0.0.1:8080/onebot/v11/ws")
    ONEBOT_HTTP_URL: str = os.getenv("ONEBOT_HTTP_URL", "http://127.0.0.1:8080")
    
    # 机器人配置
    BOT_NAME: str = os.getenv("BOT_NAME", "QQ机器人")
    BOT_MASTER_ID: Optional[int] = int(os.getenv("BOT_MASTER_ID", "0")) or None
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "bot.log")
    
    # 短链服务配置 - 平衡速度和成功率
    SHORTLINK_TIMEOUT: int = int(os.getenv("SHORTLINK_TIMEOUT", "2"))
    SHORTLINK_RETRY: int = int(os.getenv("SHORTLINK_RETRY", "1"))
    
    # 短链服务 URL
    SHORTLINK_API_URL: str = "https://api.b23.tv/shorten"
    FALLBACK_SHORTLINK_URL: str = "https://tinyurl.com/api-create.php"
    
    # 随机数配置
    DEFAULT_RANDOM_MIN: int = 1
    DEFAULT_RANDOM_MAX: int = 100
    MAX_RANDOM_RANGE: int = 10000
    
    # Wiki配置 - 关键字到wiki URL的映射
    WIKI_CONFIGS: dict = {
        "gd": {
            "url": "https://wiki.biligame.com/lysk",
            "api_url": "https://wiki.biligame.com/lysk/api.php",
            "name": "恋与深空WIKI"
        },
        "m": {
            "url": "https://wiki.biligame.com/mistria", 
            "api_url": "https://wiki.biligame.com/mistria/api.php",
            "name": "米斯特利亚WIKI"
        }
    }


# 全局配置实例
config = Config()
