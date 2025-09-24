"""
机器人配置文件
"""

import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """机器人配置类 - 包含所有默认值和应用逻辑配置"""
    
    # ===========================================
    # 🌐 网络连接配置
    # ===========================================
    
    # OneBot连接配置
    ONEBOT_WS_URL: str = os.getenv("ONEBOT_WS_URL", "ws://127.0.0.1:8080/onebot/v11/ws")
    ONEBOT_WS_URLS: str = os.getenv("ONEBOT_WS_URLS", '["ws://127.0.0.1:8080/onebot/v11/ws"]')
    ONEBOT_HTTP_URL: str = os.getenv("ONEBOT_HTTP_URL", "http://127.0.0.1:8080")
    
    # 短链服务配置
    SHORTLINK_TIMEOUT: int = int(os.getenv("SHORTLINK_TIMEOUT", "3"))  # 可调优
    SHORTLINK_RETRY: int = int(os.getenv("SHORTLINK_RETRY", "2"))      # 可调优
    SHORTLINK_API_URL: str = "https://api.b23.tv/shorten"             # 固定端点
    FALLBACK_SHORTLINK_URL: str = "https://tinyurl.com/api-create.php" # 固定端点
    
    # ===========================================
    # 🤖 机器人基础配置
    # ===========================================
    
    BOT_NAME: str = "QQ机器人"  # 固定名称
    BOT_MASTER_ID: Optional[int] = int(os.getenv("BOT_MASTER_ID", "0")) or None  # 敏感信息
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")        # 调试需要
    LOG_FILE: str = "logs/bot.log"                         # 固定路径
    
    # ===========================================
    # 🎮 功能配置
    # ===========================================
    
    # 随机数功能 - 业务逻辑固定
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
    
    # ===========================================
    # 🤖 AI功能配置
    # ===========================================
    
    # AI基础配置
    AI_TRIGGER_PREFIX: str = os.getenv("AI_TRIGGER_PREFIX", "?ai")                     # 用户偏好
    DEFAULT_AI_SERVICE: str = os.getenv("DEFAULT_AI_SERVICE", "volc")              # 用户选择 longcat 或 volc
    AI_SUMMARY_MAX_TOKENS: int = int(os.getenv("AI_SUMMARY_MAX_TOKENS", "2000"))     # 性能调优
    AI_SUMMARY_TIMEOUT: int = int(os.getenv("AI_SUMMARY_TIMEOUT", "30"))             # 性能调优
    AI_LOG_DIR: str = "logs/ai"                                                       # 固定路径
    AI_SUMMARY_ENABLED: bool = os.getenv("AI_SUMMARY_ENABLED", "true").lower() == "true"  # 功能开关
    
    # AI Prompt配置 - 自动添加到用户问题前的提示词
    AI_PROMPT_PREFIX: str = os.getenv("AI_PROMPT_PREFIX", "请不要使用markdown语法，回复token控制在2000以内。用户问题：")
    
    # LongCat AI配置（默认服务）
    LONGCAT_API_KEY: str = os.getenv("LONGCAT_API_KEY", "")                          # 敏感信息
    LONGCAT_API_URL: str = "https://api.longcat.chat/openai"                        # 固定端点
    LONGCAT_MODEL: str = "LongCat-Flash-Chat"                                       # 固定模型
    
    # 火山引擎AI配置（备用服务）
    ARK_API_KEY: str = os.getenv("ARK_API_KEY", "")                                 # 敏感信息
    VOLC_AI_REGION: str = "cn-beijing"                                              # 固定区域
    VOLC_AI_ENDPOINT: str = "ep-20250811175605-fxzbh"                               # 固定端点
    VOLC_AI_API_URL: str = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"  # 固定端点
    
    
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
    


# 全局配置实例
config = Config()
