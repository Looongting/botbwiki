"""
AI管理器 - 统一管理多种AI服务
支持火山引擎和LongCat AI
"""

import json
import httpx
from typing import List, Dict, Optional
from nonebot.log import logger

from .config import config


class LongCatAI:
    """LongCat AI客户端"""
    
    def __init__(self):
        self.api_key = config.LONGCAT_API_KEY
        self.api_url = config.LONGCAT_API_URL
        self.model = config.LONGCAT_MODEL
        self.timeout = config.AI_SUMMARY_TIMEOUT
    
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


class VolcAI:
    """火山引擎AI客户端"""
    
    def __init__(self):
        self.api_key = config.ARK_API_KEY
        self.region = config.VOLC_AI_REGION
        self.endpoint = config.VOLC_AI_ENDPOINT
        self.api_url = config.VOLC_AI_API_URL
        self.timeout = config.AI_SUMMARY_TIMEOUT
    
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


class AIManager:
    """AI管理器 - 统一管理多种AI服务"""
    
    def __init__(self):
        self.longcat_ai = LongCatAI()
        self.volc_ai = VolcAI()
        self.default_service = config.DEFAULT_AI_SERVICE
    
    async def chat_completion(self, messages: List[Dict[str, str]], service: Optional[str] = None) -> Optional[str]:
        """
        调用AI聊天完成API
        
        Args:
            messages: 消息列表
            service: AI服务类型，可选值: "longcat", "volc"，默认使用配置的默认服务
        
        Returns:
            AI回复内容，失败时返回None
        """
        # 确定使用的服务
        if service is None:
            service = self.default_service
        
        logger.info(f"使用AI服务: {service}")
        
        # 根据服务类型调用对应的AI
        if service == "longcat":
            return await self.longcat_ai.chat_completion(messages)
        elif service == "volc":
            return await self.volc_ai.chat_completion(messages)
        else:
            logger.error(f"不支持的AI服务类型: {service}")
            return None
    
    async def test_connection(self, service: Optional[str] = None) -> tuple[bool, str]:
        """
        测试AI服务连接
        
        Args:
            service: AI服务类型，可选值: "longcat", "volc"，默认使用配置的默认服务
        
        Returns:
            (是否成功, 响应消息)
        """
        if service is None:
            service = self.default_service
        
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
        available = []
        
        if self.longcat_ai.api_key:
            available.append("longcat")
        
        if self.volc_ai.api_key:
            available.append("volc")
        
        return available


# 全局AI管理器实例
ai_manager = AIManager()
