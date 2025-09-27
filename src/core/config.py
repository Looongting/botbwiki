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
    
    # HTTP API 配置（用于直接调用 Lagrange.OneBot API）
    ONEBOT_HTTP_API_URL: str = os.getenv("ONEBOT_HTTP_API_URL", "http://127.0.0.1:8081")
    
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
    
    # 测试配置
    TEST_GROUP_ID: Optional[int] = int(os.getenv("TEST_GROUP_ID", "0")) or None  # 测试群组ID
    TEST_USER_ID: Optional[int] = int(os.getenv("TEST_USER_ID", "0")) or None    # 测试私聊对象QQ号
    
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
    AI_DAY_SUMMARY_PREFIX: str = os.getenv("AI_DAY_SUMMARY_PREFIX", "?ai_daySum")     # 日总结指令
    DEFAULT_AI_SERVICE: str = os.getenv("DEFAULT_AI_SERVICE", "volc")                 # 用户选择默认AI服务
    AI_SUMMARY_MAX_TOKENS: int = int(os.getenv("AI_SUMMARY_MAX_TOKENS", "2000"))     # 性能调优
    AI_SUMMARY_TIMEOUT: int = int(os.getenv("AI_SUMMARY_TIMEOUT", "30"))             # 性能调优
    AI_LOG_DIR: str = "logs/ai"                                                       # 固定路径
    AI_SUMMARY_ENABLED: bool = os.getenv("AI_SUMMARY_ENABLED", "true").lower() == "true"  # 功能开关
    
    # AI Prompt配置 - 自动添加到用户问题前的提示词
    AI_PROMPT_PREFIX: str = os.getenv("AI_PROMPT_PREFIX", "请不要使用markdown语法，回复token控制在2000以内。用户问题：")
    
    # AI服务配置 - 统一的字典结构管理多个AI服务
    AI_SERVICES: dict = {
        "glm": {
            "api_key": os.getenv("GLM_API_KEY", ""),                                 # 敏感信息
            "api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",     # 智谱AI官方API端点
            "model": "glm-4.5-flash",                                               # 免费的GLM-4.5-flash模型
            "name": "智谱AI GLM",                                                    # 服务名称
            "enabled": True,          # 用户手动配置是否启用
            "trigger_prefix": "?glm"                                                  # 群聊触发前缀
        },
        "longcat": {
            "api_key": os.getenv("LONGCAT_API_KEY", ""),                              # 敏感信息
            "api_url": "https://api.longcat.chat/openai",                             # 固定端点
            "model": "LongCat-Flash-Chat",                                            # 固定模型
            "name": "LongCat AI",                                                     # 服务名称
            "enabled": True,      # 用户手动配置是否启用
            "trigger_prefix": "?lc"                                                   # 群聊触发前缀
        },
        "volc": {
            "api_key": os.getenv("ARK_API_KEY", ""),                                 # 敏感信息
            "api_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",  # 固定端点
            "model": "ep-20250811175605-fxzbh",                                      # 固定端点（火山引擎的endpoint）
            "region": "cn-beijing",                                                   # 固定区域
            "name": "火山引擎AI",                                                     # 服务名称
            "enabled": True,         # 用户手动配置是否启用
            "trigger_prefix": "?volc"                                                 # 群聊触发前缀
        }        
        # 示例：其他AI服务配置结构
        # "openai": {
        #     "api_key": os.getenv("OPENAI_API_KEY", ""),
        #     "api_url": "https://api.openai.com/v1/chat/completions",
        #     "model": "gpt-3.5-turbo",
        #     "name": "OpenAI GPT",
        #     "enabled": bool(os.getenv("OPENAI_API_KEY", "")),
        # },
        # "claude": {
        #     "api_key": os.getenv("CLAUDE_API_KEY", ""),
        #     "api_url": "https://api.anthropic.com/v1/messages",
        #     "model": "claude-3-haiku-20240307",
        #     "name": "Claude AI",
        #     "enabled": bool(os.getenv("CLAUDE_API_KEY", "")),
        # },
    }
    
    # AI服务配置访问方法
    @property
    def available_ai_services(self) -> list:
        """获取所有可用的AI服务列表"""
        return [service for service, config in self.AI_SERVICES.items() if config.get("enabled", False)]
    
    def get_ai_service_config(self, service_name: str) -> dict:
        """获取指定AI服务的配置"""
        return self.AI_SERVICES.get(service_name, {})
    
    def is_ai_service_enabled(self, service_name: str) -> bool:
        """检查指定AI服务是否启用"""
        return self.AI_SERVICES.get(service_name, {}).get("enabled", False)
    
    @property
    def default_ai_service_config(self) -> dict:
        """获取默认AI服务的配置 - ?ai命令使用的AI服务"""
        # 从AI_SERVICES中从上往下选择第一个enabled为true的AI作为?ai的默认AI模型
        for service, config in self.AI_SERVICES.items():
            if config.get("enabled", False):
                return config
        
        return {}
    
    def get_ai_service_by_trigger_prefix(self, trigger_prefix: str) -> tuple:
        """根据trigger_prefix获取对应的AI服务配置和服务名"""
        for service_name, config in self.AI_SERVICES.items():
            if config.get("trigger_prefix") == trigger_prefix:
                return service_name, config
        return None, {}
    
    # ===========================================
    # 📤 消息发送配置
    # ===========================================
    
    # 消息发送器配置
    MESSAGE_SENDER_ENABLED: bool = True  # 消息发送器开关
    HTTP_API_TIMEOUT: int = 10                 # HTTP 请求超时（秒）
    MESSAGE_MAX_RETRIES: int = 3            # 最大重试次数
    MESSAGE_RETRY_DELAY: int = 1            # 重试延迟（秒）
    
    # 频率限制配置
    MESSAGE_RATE_LIMIT_ENABLED: bool = True  # 频率限制开关
    MESSAGE_RATE_LIMIT_COUNT: int = 10 # 时间窗口内最大发送数
    MESSAGE_RATE_LIMIT_WINDOW: int = 60 # 时间窗口（秒）
    
    # 转发消息配置
    MESSAGE_FORWARD_ENABLED: bool = True  # 转发消息开关
    MESSAGE_FORWARD_THRESHOLD: int = 200  # 超过此长度自动转发（字符数）
    MESSAGE_FORWARD_MAX_LENGTH: int = 2000  # 单条转发消息最大长度
    MESSAGE_FORWARD_MAX_COUNT: int = 10  # 最大转发消息数量
    
    
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
