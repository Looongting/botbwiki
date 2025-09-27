"""
AI管理器 - 统一管理多种AI服务
支持火山引擎和LongCat AI等多种AI服务
"""

import json
import httpx
from typing import List, Dict, Optional
from nonebot.log import logger

from .config import config


class BaseAIClient:
    """AI客户端基类"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.service_config = config.AI_SERVICES.get(service_name, {})
        self.timeout = config.AI_SUMMARY_TIMEOUT
        
    @property
    def is_enabled(self) -> bool:
        """检查服务是否启用（有API密钥即为启用）"""
        return bool(self.service_config.get("api_key"))
    
    async def chat_completion(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """调用AI聊天完成API - 子类需要实现"""
        raise NotImplementedError


class LongCatAI(BaseAIClient):
    """LongCat AI客户端"""
    
    def __init__(self):
        super().__init__("longcat")
        self.api_key = self.service_config.get("api_key", "")
        self.api_url = self.service_config.get("api_url", "")
        self.model = self.service_config.get("model", "")
    
    async def chat_completion(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """调用LongCat AI聊天完成API"""
        if not self.api_key:
            logger.error("LongCat AI配置不完整，请检查LONGCAT_API_KEY")
            return None
        
        try:
            # 准备请求数据
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": config.AI_SUMMARY_MAX_TOKENS,
                "temperature": 0.7,
                "stream": False
            }
            
            # 准备请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 发送请求 - 拼接完整的endpoint
            full_url = f"{self.api_url.rstrip('/')}/v1/chat/completions"
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    full_url,
                    headers=headers,
                    json=data
                )
                
                logger.debug(f"LongCat AI API响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    else:
                        logger.error(f"LongCat AI响应格式异常: {result}")
                        return None
                else:
                    logger.error(f"LongCat AI API调用失败: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"调用LongCat AI时发生错误: {e}")
            return None


class VolcAI(BaseAIClient):
    """火山引擎AI客户端"""
    
    def __init__(self):
        super().__init__("volc")
        self.api_key = self.service_config.get("api_key", "")
        self.region = self.service_config.get("region", "")
        self.endpoint = self.service_config.get("model", "")  # 火山引擎使用model字段存储endpoint
        self.api_url = self.service_config.get("api_url", "")
    
    async def chat_completion(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """调用火山引擎AI聊天完成API"""
        if not self.api_key:
            logger.error("火山引擎AI配置不完整，请检查ARK_API_KEY")
            return None
        
        try:
            # 准备请求数据
            data = {
                "model": self.endpoint,
                "messages": messages,
                "max_tokens": config.AI_SUMMARY_MAX_TOKENS,
                "temperature": 0.7,
                "stream": False
            }
            
            body = json.dumps(data, ensure_ascii=False)
            
            # 准备请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 发送请求
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    content=body
                )
                
                logger.debug(f"火山引擎AI API响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    else:
                        logger.error(f"火山引擎AI响应格式异常: {result}")
                        return None
                else:
                    logger.error(f"火山引擎AI API调用失败: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"调用火山引擎AI时发生错误: {e}")
            return None


class GLMAI(BaseAIClient):
    """智谱AI GLM客户端"""
    
    def __init__(self):
        super().__init__("glm")
        self.api_key = self.service_config.get("api_key", "")
        self.api_url = self.service_config.get("api_url", "")
        self.model = self.service_config.get("model", "")
    
    async def chat_completion(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """调用智谱AI GLM聊天完成API"""
        if not self.api_key:
            logger.error("智谱AI GLM配置不完整，请检查GLM_API_KEY")
            return None
        
        try:
            # 准备请求数据
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": config.AI_SUMMARY_MAX_TOKENS,
                "temperature": 0.7,
                "stream": False
            }
            
            # 准备请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 发送请求
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=data
                )
                
                logger.debug(f"智谱AI GLM API响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    else:
                        logger.error(f"智谱AI GLM响应格式异常: {result}")
                        return None
                else:
                    logger.error(f"智谱AI GLM API调用失败: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"调用智谱AI GLM时发生错误: {e}")
            return None


class AIManager:
    """AI管理器 - 统一管理多种AI服务"""
    
    def __init__(self):
        self.clients = {}
        # AI客户端注册表 - 支持动态扩展
        self.client_registry = {
            "longcat": LongCatAI,
            "volc": VolcAI,
            "glm": GLMAI,
            # 新增AI服务只需在这里注册类即可
        }
        self._initialize_clients()
    
    def _initialize_clients(self):
        """动态初始化AI客户端"""
        for service_name, service_config in config.AI_SERVICES.items():
            client_class = self.client_registry.get(service_name)
            if client_class:
                try:
                    self.clients[service_name] = client_class()
                    logger.debug(f"成功初始化AI客户端: {service_name}")
                except Exception as e:
                    logger.error(f"初始化AI客户端 {service_name} 失败: {e}")
            else:
                logger.warning(f"未找到AI服务 {service_name} 对应的客户端类")
    
    def register_client(self, service_name: str, client_class):
        """
        注册新的AI客户端类
        
        Args:
            service_name: 服务名称
            client_class: 客户端类（必须继承自BaseAIClient）
        """
        if not issubclass(client_class, BaseAIClient):
            raise ValueError(f"客户端类 {client_class} 必须继承自 BaseAIClient")
        
        self.client_registry[service_name] = client_class
        logger.info(f"注册AI客户端类: {service_name} -> {client_class.__name__}")
        
        # 如果配置中存在该服务，立即初始化
        if service_name in config.AI_SERVICES:
            try:
                self.clients[service_name] = client_class()
                logger.info(f"成功初始化新注册的AI客户端: {service_name}")
            except Exception as e:
                logger.error(f"初始化新注册的AI客户端 {service_name} 失败: {e}")
    
    def get_client(self, service_name: str) -> Optional[BaseAIClient]:
        """获取指定AI服务的客户端"""
        return self.clients.get(service_name)
    
    async def chat_completion(self, messages: List[Dict[str, str]], service: Optional[str] = None) -> Optional[str]:
        """
        调用AI聊天完成API
        
        Args:
            messages: 消息列表
            service: AI服务类型，默认使用配置的默认服务
        
        Returns:
            AI回复内容，失败时返回None
        """
        # 确定使用的服务
        if service is None:
            # 使用第一个可用的AI服务
            available_services = self.get_available_services()
            if not available_services:
                logger.error("没有可用的AI服务")
                return None
            service = available_services[0]
        
        logger.info(f"使用AI服务: {service}")
        
        # 获取对应的客户端
        client = self.get_client(service)
        if client is None:
            logger.error(f"不支持的AI服务类型: {service}")
            return None
        
        if not client.is_enabled:
            logger.error(f"AI服务 {service} 未启用或配置不完整")
            return None
        
        return await client.chat_completion(messages)
    
    async def test_connection(self, service: Optional[str] = None) -> tuple[bool, str]:
        """
        测试AI服务连接
        
        Args:
            service: AI服务类型，可选值: "longcat", "volc", "glm"，默认使用配置的默认服务
        
        Returns:
            (是否成功, 响应消息)
        """
        if service is None:
            # 使用第一个可用的AI服务
            available_services = self.get_available_services()
            if not available_services:
                return False, "没有可用的AI服务"
            service = available_services[0]
        
        test_messages = [
            {"role": "user", "content": "请简单介绍一下自己"}
        ]
        
        try:
            result = await self.chat_completion(test_messages, service)
            if result:
                return True, result
            else:
                return False, f"{service} AI服务连接失败"
        except Exception as e:
            return False, f"{service} AI服务连接异常: {str(e)}"
    
    def get_available_services(self) -> List[str]:
        """获取可用的AI服务列表"""
        return config.available_ai_services


# 全局AI管理器实例
ai_manager = AIManager()
