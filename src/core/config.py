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
    ONEBOT_WS_URLS: str = os.getenv("ONEBOT_WS_URLS", '["ws://127.0.0.1:8080/onebot/v11/ws"]')
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
        "?m": {
            "url": "https://wiki.biligame.com/mistria", 
            "api_url": "https://wiki.biligame.com/mistria/api.php",
            "name": "米斯特利亚WIKI"
        },
        "?t": {
            "url": "https://wiki.biligame.com/tools",
            "api_url": "https://wiki.biligame.com/tools/api.php",
            "name": "tools"
        }
    }
    
    # 火山引擎AI配置
    ARK_API_KEY: str = os.getenv("ARK_API_KEY", "")
    VOLC_AI_REGION: str = os.getenv("VOLC_AI_REGION", "cn-beijing")
    VOLC_AI_ENDPOINT: str = os.getenv("VOLC_AI_ENDPOINT", "ep-20250811175605-fxzbh")
    VOLC_AI_API_URL: str = f"https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    # AI总结功能配置
    AI_SUMMARY_MAX_TOKENS: int = int(os.getenv("AI_SUMMARY_MAX_TOKENS", "2000"))
    AI_SUMMARY_TIMEOUT: int = int(os.getenv("AI_SUMMARY_TIMEOUT", "30"))
    
    # 目标群配置 - 支持多个群
    @property
    def TARGET_GROUP_IDS(self) -> list:
        """获取目标群ID列表，支持多种配置格式"""
        import json
        
        # 尝试从TARGET_GROUP_IDS环境变量读取
        target_groups_env = os.getenv("TARGET_GROUP_IDS", "")
        if target_groups_env:
            # 支持JSON数组格式: [717421103,1059707281]
            if target_groups_env.startswith('[') and target_groups_env.endswith(']'):
                try:
                    return json.loads(target_groups_env)
                except json.JSONDecodeError:
                    pass
            
            # 支持逗号分隔格式: 717421103,1059707281
            if ',' in target_groups_env:
                return [int(x.strip()) for x in target_groups_env.split(",") if x.strip().isdigit()]
            
            # 单个群ID
            if target_groups_env.isdigit():
                return [int(target_groups_env)]
        
        # 回退到TARGET_GROUP_ID（向后兼容）
        target_group_id = os.getenv("TARGET_GROUP_ID", "717421103")
        if target_group_id.startswith('[') and target_group_id.endswith(']'):
            try:
                return json.loads(target_group_id)
            except json.JSONDecodeError:
                pass
        
        # 默认返回单个群
        return [int(target_group_id) if target_group_id.isdigit() else 717421103]
    
    # 主要目标群（向后兼容）
    @property 
    def TARGET_GROUP_ID(self) -> int:
        """获取主要目标群ID"""
        groups = self.TARGET_GROUP_IDS
        return groups[0] if groups else 717421103
    
    # AI总结日志配置
    AI_LOG_DIR: str = os.getenv("AI_LOG_DIR", "AI_LOG")
    AI_SUMMARY_ENABLED: bool = os.getenv("AI_SUMMARY_ENABLED", "true").lower() == "true"


# 全局配置实例
config = Config()
