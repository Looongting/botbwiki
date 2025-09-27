"""
Lagrange.OneBot HTTP API 客户端
提供统一的 HTTP API 调用接口，支持消息发送、信息获取等功能
"""

import asyncio
import httpx
import json
from typing import Dict, Any, Optional, List
from nonebot.log import logger
from .config import config


class LagrangeAPIClient:
    """Lagrange.OneBot HTTP API 客户端"""
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 10):
        """
        初始化客户端
        
        Args:
            base_url: API 基础地址，默认使用配置中的地址
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url or config.ONEBOT_HTTP_API_URL
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """获取 HTTP 客户端实例"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
            )
        return self._client
    
    async def close(self):
        """关闭客户端连接"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def call_api(self, action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        调用 OneBot API
        
        Args:
            action: API 动作名称
            params: 请求参数
            
        Returns:
            API 响应结果
        """
        if params is None:
            params = {}
        
        url = f"{self.base_url}/{action}"
        
        try:
            client = await self._get_client()
            response = await client.post(
                url,
                json=params,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"API 调用成功: {action} -> {result.get('status', 'unknown')}")
                return result
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"API 调用失败: {action} -> {error_msg}")
                return {
                    "status": "failed",
                    "error": error_msg,
                    "retcode": response.status_code
                }
                
        except httpx.TimeoutException:
            error_msg = f"请求超时: {action}"
            logger.error(error_msg)
            return {
                "status": "failed",
                "error": error_msg,
                "retcode": -1
            }
        except Exception as e:
            error_msg = f"请求异常: {action} -> {str(e)}"
            logger.error(error_msg)
            return {
                "status": "failed",
                "error": error_msg,
                "retcode": -1
            }
    
    # ===========================================
    # 消息发送相关 API
    # ===========================================
    
    async def send_private_msg(self, user_id: int, message: str) -> Dict[str, Any]:
        """
        发送私聊消息
        
        Args:
            user_id: 目标用户ID
            message: 消息内容
            
        Returns:
            API 响应结果
        """
        return await self.call_api("send_private_msg", {
            "user_id": user_id,
            "message": message
        })
    
    async def send_group_msg(self, group_id: int, message: str) -> Dict[str, Any]:
        """
        发送群消息
        
        Args:
            group_id: 目标群ID
            message: 消息内容
            
        Returns:
            API 响应结果
        """
        return await self.call_api("send_group_msg", {
            "group_id": group_id,
            "message": message
        })
    
    # ===========================================
    # 信息获取相关 API
    # ===========================================
    
    async def get_login_info(self) -> Dict[str, Any]:
        """获取登录信息"""
        return await self.call_api("get_login_info", {})
    
    async def get_group_list(self) -> Dict[str, Any]:
        """获取群列表"""
        return await self.call_api("get_group_list", {})
    
    async def get_friend_list(self) -> Dict[str, Any]:
        """获取好友列表"""
        return await self.call_api("get_friend_list", {})
    
    async def get_group_member_list(self, group_id: int) -> Dict[str, Any]:
        """
        获取群成员列表
        
        Args:
            group_id: 群ID
            
        Returns:
            API 响应结果
        """
        return await self.call_api("get_group_member_list", {
            "group_id": group_id
        })
    
    async def get_msg(self, message_id: int) -> Dict[str, Any]:
        """
        获取消息信息
        
        Args:
            message_id: 消息ID
            
        Returns:
            API 响应结果
        """
        return await self.call_api("get_msg", {
            "message_id": message_id
        })
    
    async def get_group_msg_history(self, group_id: int, message_id: str = None, count: int = 20) -> Dict[str, Any]:
        """
        获取群聊历史消息
        
        Args:
            group_id: 群ID
            message_id: 起始消息ID，不指定则从最新消息开始
            count: 获取消息数量，默认20条
            
        Returns:
            API 响应结果
        """
        params = {"group_id": group_id, "count": count}
        if message_id is not None:
            params["message_id"] = message_id
        return await self.call_api("get_group_msg_history", params)
    
    async def set_group_reaction(self, group_id: int, message_id: int, code: str, is_add: bool = True) -> Dict[str, Any]:
        """
        设置群消息表情回复
        
        Args:
            group_id: 群ID
            message_id: 消息ID
            code: 表情代码
            is_add: 是否添加表情，False为移除表情
            
        Returns:
            API 响应结果
        """
        return await self.call_api("set_group_reaction", {
            "group_id": group_id,
            "message_id": message_id,
            "code": code,
            "is_add": is_add
        })
    
    # ===========================================
    # 批量操作相关 API
    # ===========================================
    
    async def send_multiple_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量发送消息
        
        Args:
            messages: 消息列表，每个消息包含 type, target_id, message 字段
            
        Returns:
            每个消息的发送结果列表
        """
        tasks = []
        for msg in messages:
            if msg.get("type") == "group":
                task = self.send_group_msg(msg["target_id"], msg["message"])
            elif msg.get("type") == "private":
                task = self.send_private_msg(msg["target_id"], msg["message"])
            else:
                task = asyncio.create_task(asyncio.sleep(0))  # 空任务
                task.set_result({"status": "failed", "error": "不支持的消息类型"})
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "status": "failed",
                    "error": str(result),
                    "retcode": -1
                })
            else:
                processed_results.append(result)
        
        return processed_results


# 全局客户端实例
_global_client: Optional[LagrangeAPIClient] = None


def get_client() -> LagrangeAPIClient:
    """获取全局客户端实例"""
    global _global_client
    if _global_client is None:
        _global_client = LagrangeAPIClient()
    return _global_client


async def close_client():
    """关闭全局客户端"""
    global _global_client
    if _global_client:
        await _global_client.close()
        _global_client = None
