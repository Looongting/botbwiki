"""
统一消息发送器
提供统一的消息发送接口，支持群消息、私聊消息、批量发送等功能
包含重试机制、错误处理、限流控制等特性
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from .http_client import get_client
from .config import config


@dataclass
class Message:
    """消息数据类"""
    type: str  # "group" 或 "private"
    target_id: int  # 群ID或用户ID
    content: str  # 消息内容
    retry_count: int = 0  # 重试次数
    max_retries: int = 3  # 最大重试次数


class MessageSender:
    """统一消息发送器"""
    
    def __init__(self):
        self.client = get_client()
        self.rate_limit_enabled = getattr(config, 'MESSAGE_RATE_LIMIT_ENABLED', True)
        self.rate_limit_count = getattr(config, 'MESSAGE_RATE_LIMIT_COUNT', 10)
        self.rate_limit_window = getattr(config, 'MESSAGE_RATE_LIMIT_WINDOW', 60)
        self.retry_delay = getattr(config, 'MESSAGE_RETRY_DELAY', 1)
        self.max_retries = getattr(config, 'MESSAGE_MAX_RETRIES', 3)
        
        # 限流控制
        self._message_times: List[float] = []
        self._lock = asyncio.Lock()
    
    async def _check_rate_limit(self) -> bool:
        """检查是否超过发送频率限制"""
        if not self.rate_limit_enabled:
            return True
        
        async with self._lock:
            now = time.time()
            # 清理过期的记录
            self._message_times = [t for t in self._message_times if now - t < self.rate_limit_window]
            
            # 检查是否超过限制
            if len(self._message_times) >= self.rate_limit_count:
                return False
            
            # 记录本次发送时间
            self._message_times.append(now)
            return True
    
    async def _wait_for_rate_limit(self):
        """等待直到可以发送消息"""
        while not await self._check_rate_limit():
            wait_time = self.rate_limit_window - (time.time() - self._message_times[0])
            if wait_time > 0:
                logger.info(f"消息发送频率限制，等待 {wait_time:.1f} 秒")
                await asyncio.sleep(min(wait_time, 5))  # 最多等待5秒
    
    async def _send_with_retry(self, message: Message) -> Dict[str, Any]:
        """带重试机制的消息发送"""
        last_error = None
        
        for attempt in range(message.max_retries + 1):
            try:
                # 检查频率限制
                await self._wait_for_rate_limit()
                
                # 发送消息
                if message.type == "group":
                    result = await self.client.send_group_msg(message.target_id, message.content)
                elif message.type == "private":
                    result = await self.client.send_private_msg(message.target_id, message.content)
                else:
                    return {
                        "status": "failed",
                        "error": f"不支持的消息类型: {message.type}",
                        "retcode": -1
                    }
                
                # 检查结果
                if result.get("status") == "ok":
                    logger.info(f"消息发送成功: {message.type}:{message.target_id}")
                    return result
                else:
                    error_msg = result.get("error", "未知错误")
                    retcode = result.get("retcode", -1)
                    
                    # 判断是否应该重试
                    if self._should_retry(retcode, error_msg) and attempt < message.max_retries:
                        logger.warning(f"消息发送失败，准备重试 ({attempt + 1}/{message.max_retries}): {error_msg}")
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))  # 指数退避
                        last_error = error_msg
                        continue
                    else:
                        logger.error(f"消息发送失败: {error_msg}")
                        return result
                        
            except Exception as e:
                error_msg = str(e)
                if attempt < message.max_retries:
                    logger.warning(f"消息发送异常，准备重试 ({attempt + 1}/{message.max_retries}): {error_msg}")
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    last_error = error_msg
                    continue
                else:
                    logger.error(f"消息发送异常: {error_msg}")
                    return {
                        "status": "failed",
                        "error": error_msg,
                        "retcode": -1
                    }
        
        # 所有重试都失败了
        return {
            "status": "failed",
            "error": f"重试 {message.max_retries} 次后仍然失败: {last_error}",
            "retcode": -1
        }
    
    def _should_retry(self, retcode: int, error_msg: str) -> bool:
        """判断是否应该重试"""
        # 网络错误、超时错误等可以重试
        retryable_codes = [-1, 10001, 10002, 10003]  # 网络错误、超时等
        retryable_errors = ["timeout", "connection", "network", "超时", "连接"]
        
        if retcode in retryable_codes:
            return True
        
        if any(keyword in error_msg.lower() for keyword in retryable_errors):
            return True
        
        return False
    
    # ===========================================
    # 公共接口方法
    # ===========================================
    
    async def send_group_message(self, group_id: int, message: str, max_retries: Optional[int] = None) -> bool:
        """
        发送群消息
        
        Args:
            group_id: 群ID
            message: 消息内容
            max_retries: 最大重试次数，默认使用配置值
            
        Returns:
            发送是否成功
        """
        msg = Message(
            type="group",
            target_id=group_id,
            content=message,
            max_retries=max_retries or self.max_retries
        )
        
        result = await self._send_with_retry(msg)
        return result.get("status") == "ok"
    
    async def send_private_message(self, user_id: int, message: str, max_retries: Optional[int] = None) -> bool:
        """
        发送私聊消息
        
        Args:
            user_id: 用户ID
            message: 消息内容
            max_retries: 最大重试次数，默认使用配置值
            
        Returns:
            发送是否成功
        """
        msg = Message(
            type="private",
            target_id=user_id,
            content=message,
            max_retries=max_retries or self.max_retries
        )
        
        result = await self._send_with_retry(msg)
        return result.get("status") == "ok"
    
    async def send_reply(self, event: Union[GroupMessageEvent, PrivateMessageEvent], message: str, max_retries: Optional[int] = None) -> bool:
        """
        回复消息（自动判断群消息或私聊消息）
        
        Args:
            event: 消息事件
            message: 回复内容
            max_retries: 最大重试次数，默认使用配置值
            
        Returns:
            发送是否成功
        """
        if isinstance(event, GroupMessageEvent):
            return await self.send_group_message(event.group_id, message, max_retries)
        elif isinstance(event, PrivateMessageEvent):
            return await self.send_private_message(event.user_id, message, max_retries)
        else:
            logger.error(f"不支持的事件类型: {type(event)}")
            return False
    
    async def send_multiple_messages(self, messages: List[Dict[str, Any]], max_concurrent: int = 5) -> List[bool]:
        """
        批量发送消息
        
        Args:
            messages: 消息列表，每个消息包含 type, target_id, content 字段
            max_concurrent: 最大并发数
            
        Returns:
            每个消息的发送结果列表
        """
        # 创建信号量控制并发数
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def send_single_message(msg_data: Dict[str, Any]) -> bool:
            async with semaphore:
                msg = Message(
                    type=msg_data["type"],
                    target_id=msg_data["target_id"],
                    content=msg_data["content"],
                    max_retries=msg_data.get("max_retries", self.max_retries)
                )
                result = await self._send_with_retry(msg)
                return result.get("status") == "ok"
        
        # 并发发送所有消息
        tasks = [send_single_message(msg) for msg in messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"批量发送消息异常: {result}")
                processed_results.append(False)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def send_to_target_groups(self, message: str, max_retries: Optional[int] = None) -> Dict[int, bool]:
        """
        向所有目标群发送消息
        
        Args:
            message: 消息内容
            max_retries: 最大重试次数，默认使用配置值
            
        Returns:
            每个群的发送结果字典
        """
        results = {}
        for group_id in config.TARGET_GROUP_IDS:
            success = await self.send_group_message(group_id, message, max_retries)
            results[group_id] = success
        
        return results
    
    # ===========================================
    # 工具方法
    # ===========================================
    
    async def test_connection(self) -> bool:
        """测试连接是否正常"""
        try:
            result = await self.client.get_login_info()
            return result.get("status") == "ok"
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """获取限流状态"""
        now = time.time()
        recent_messages = [t for t in self._message_times if now - t < self.rate_limit_window]
        
        return {
            "enabled": self.rate_limit_enabled,
            "limit": self.rate_limit_count,
            "window": self.rate_limit_window,
            "current_count": len(recent_messages),
            "remaining": max(0, self.rate_limit_count - len(recent_messages))
        }


# 全局消息发送器实例
_global_sender: Optional[MessageSender] = None


def get_sender() -> MessageSender:
    """获取全局消息发送器实例"""
    global _global_sender
    if _global_sender is None:
        _global_sender = MessageSender()
    return _global_sender


async def close_sender():
    """关闭全局消息发送器"""
    global _global_sender
    if _global_sender:
        await _global_sender.client.close()
        _global_sender = None
