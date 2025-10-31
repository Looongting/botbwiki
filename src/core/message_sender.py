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
        
        # 转发消息配置
        self.forward_enabled = getattr(config, 'MESSAGE_FORWARD_ENABLED', True)
        self.forward_threshold = getattr(config, 'MESSAGE_FORWARD_THRESHOLD', 500)
        self.forward_max_length = getattr(config, 'MESSAGE_FORWARD_MAX_LENGTH', 2000)
        self.forward_max_count = getattr(config, 'MESSAGE_FORWARD_MAX_COUNT', 10)
        
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
    
    def _is_pure_text(self, message: str) -> bool:
        """判断是否为纯文本消息"""
        # 纯文本判断：不包含CQ码（图片、语音、@等特殊消息）
        # CQ码格式：[CQ:type,data=value]
        return '[CQ:' not in message
    
    def _split_long_text(self, text: str) -> List[str]:
        """将长文本切割为多个片段"""
        if len(text) <= self.forward_max_length:
            return [text]
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            # 计算当前片段的结束位置
            end_pos = min(current_pos + self.forward_max_length, len(text))
            
            # 如果不是最后一片，尝试在合适的位置断句
            if end_pos < len(text):
                # 寻找最近的句号、问号、感叹号或换行符
                for i in range(end_pos, max(current_pos + self.forward_max_length // 2, current_pos), -1):
                    if text[i] in ['。', '！', '？', '\n', '.', '!', '?']:
                        end_pos = i + 1
                        break
                else:
                    # 如果没找到合适的断句点，寻找空格
                    for i in range(end_pos, max(current_pos + self.forward_max_length // 2, current_pos), -1):
                        if text[i] in [' ', '\t']:
                            end_pos = i + 1
                            break
            
            chunk = text[current_pos:end_pos].strip()
            if chunk:
                chunks.append(chunk)
            
            current_pos = end_pos
            
            # 防止无限循环
            if len(chunks) >= self.forward_max_count:
                # 如果超过最大数量，将剩余内容作为最后一片
                remaining = text[current_pos:].strip()
                if remaining:
                    chunks.append(remaining[:self.forward_max_length] + "...")
                break
        
        return chunks
    
    async def _send_forward_message(self, group_id: int, messages: List[str]) -> bool:
        """发送转发消息"""
        try:
            # 构建转发消息数据 - 使用 OneBot 标准格式
            forward_data = {
                "group_id": group_id,
                "messages": []
            }
            
            # 为每条消息创建转发节点
            for i, message in enumerate(messages):
                node = {
                    "type": "node",
                    "data": {
                        "name": f"机器人消息 {i+1}",
                        "uin": str(config.BOT_MASTER_ID or 3330219965),  # 使用机器人QQ号，转为字符串
                        "content": message
                    }
                }
                forward_data["messages"].append(node)
            
            # 调用转发消息API
            result = await self.client.call_api("send_group_forward_msg", forward_data)
            
            if result.get("status") == "ok":
                logger.info(f"转发消息发送成功: group:{group_id}, 消息数:{len(messages)}")
                return True
            else:
                logger.error(f"转发消息发送失败: {result.get('error', '未知错误')}")
                # 如果转发失败，尝试使用合并转发的方式
                return await self._send_forward_message_alternative(group_id, messages)
                
        except Exception as e:
            logger.error(f"转发消息发送异常: {e}")
            return False
    
    async def _send_forward_message_alternative(self, group_id: int, messages: List[str]) -> bool:
        """备用转发消息发送方式 - 逐条发送带编号的消息"""
        try:
            logger.info("尝试使用备用转发方式：逐条发送带编号消息")
            
            success_count = 0
            for i, message in enumerate(messages):
                # 为每条消息添加编号
                numbered_message = f"【{i+1}/{len(messages)}】\n{message}"
                
                # 发送单条消息
                msg = Message(
                    type="group",
                    target_id=group_id,
                    content=numbered_message,
                    max_retries=self.max_retries
                )
                
                result = await self._send_with_retry(msg)
                if result.get("status") == "ok":
                    success_count += 1
                    # 短暂延迟，避免消息发送过快
                    await asyncio.sleep(0.5)
                else:
                    logger.warning(f"备用转发消息 {i+1} 发送失败: {result.get('error', '未知错误')}")
            
            if success_count == len(messages):
                logger.info(f"备用转发消息发送成功: group:{group_id}, 消息数:{len(messages)}")
                return True
            elif success_count > 0:
                logger.warning(f"备用转发消息部分成功: {success_count}/{len(messages)}")
                return True
            else:
                logger.error("备用转发消息全部发送失败")
                return False
                
        except Exception as e:
            logger.error(f"备用转发消息发送异常: {e}")
            return False
    
    async def _send_group_message_normal(self, group_id: int, message: str, max_retries: Optional[int] = None) -> bool:
        """普通群消息发送函数"""
        msg = Message(
            type="group",
            target_id=group_id,
            content=message,
            max_retries=max_retries or self.max_retries
        )
        
        result = await self._send_with_retry(msg)
        return result.get("status") == "ok"
    
    async def _send_group_forward_message(self, group_id: int, message: str) -> bool:
        """群组转发消息函数"""
        # 按最大长度切割文本
        chunks = self._split_text_by_max_length(message)
        
        logger.info(f"文本按最大长度{self.forward_max_length}切割为 {len(chunks)} 个片段")
        
        # 尝试发送转发消息
        if await self._send_forward_message(group_id, chunks):
            return True
        else:
            logger.warning("转发消息失败，回退到普通消息发送")
            # 转发失败，回退到普通消息发送
            return await self._send_group_message_normal(group_id, message)
    
    def _split_text_by_max_length(self, text: str) -> List[str]:
        """按最大长度切割文本"""
        if len(text) <= self.forward_max_length:
            return [text]
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            # 计算当前片段的结束位置，使用最大长度作为切割依据
            end_pos = min(current_pos + self.forward_max_length, len(text))
            
            # 如果不是最后一片，尝试在合适的位置断句
            if end_pos < len(text):
                # 寻找最近的句号、问号、感叹号或换行符
                for i in range(end_pos, max(current_pos + self.forward_max_length // 2, current_pos), -1):
                    if text[i] in ['。', '！', '？', '\n', '.', '!', '?']:
                        end_pos = i + 1
                        break
                else:
                    # 如果没找到合适的断句点，寻找空格
                    for i in range(end_pos, max(current_pos + self.forward_max_length // 2, current_pos), -1):
                        if text[i] in [' ', '\t']:
                            end_pos = i + 1
                            break
            
            chunk = text[current_pos:end_pos].strip()
            if chunk:
                chunks.append(chunk)
            
            current_pos = end_pos
            
            # 防止无限循环
            if len(chunks) >= self.forward_max_count:
                # 如果超过最大数量，将剩余内容作为最后一片
                remaining = text[current_pos:].strip()
                if remaining:
                    chunks.append(remaining[:self.forward_max_length] + "...")
                break
        
        return chunks
    
    async def _send_group_message_adaptive(self, group_id: int, message: str, max_retries: Optional[int] = None) -> bool:
        """自适应群消息发送函数：按字数调用不同的发送方式"""
        # 检查是否启用转发功能且为纯文本
        if (self.forward_enabled and 
            len(message) > self.forward_threshold):
            
            logger.info(f"检测到长文本消息，长度: {len(message)}，使用转发模式")
            return await self._send_group_forward_message(group_id, message)
        else:
            logger.info(f"使用普通消息模式，长度: {len(message)}")
            return await self._send_group_message_normal(group_id, message, max_retries)
    
    
    # ===========================================
    # 公共接口方法
    # ===========================================
    
    async def send_group_message(self, group_id: int, message: str, max_retries: Optional[int] = None) -> bool:
        """
        发送群消息，自适应选择发送方式
        
        Args:
            group_id: 群ID
            message: 消息内容
            max_retries: 最大重试次数，默认使用配置值
            
        Returns:
            发送是否成功
        """
        return await self._send_group_message_adaptive(group_id, message, max_retries)
    
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
    
    async def send_reply_with_reference(self, event: Union[GroupMessageEvent, PrivateMessageEvent], message: str, max_retries: Optional[int] = None) -> bool:
        """
        引用回复消息（检查原始消息是否存在，如果不存在则不发送）
        复用原有的发送消息函数，支持长文本自动转发
        
        Args:
            event: 消息事件
            message: 回复内容
            max_retries: 最大重试次数，默认使用配置值
            
        Returns:
            发送是否成功
        """
        try:
            # 检查原始消息是否存在
            message_id = event.message_id
            result = await self.client.get_msg(message_id)
            
            if result.get("status") != "ok":
                logger.warning(f"原始消息不存在或已被撤回/删除，消息ID: {message_id}")
                return False
            
            # 原始消息存在，发送引用回复
            if isinstance(event, GroupMessageEvent):
                return await self._send_group_reply_with_reference_optimized(event.group_id, message_id, message, max_retries)
            elif isinstance(event, PrivateMessageEvent):
                return await self._send_private_reply_with_reference_optimized(event.user_id, message_id, message, max_retries)
            else:
                logger.error(f"不支持的事件类型: {type(event)}")
                return False
                
        except Exception as e:
            logger.error(f"引用回复发送异常: {e}")
            return False
    
    async def _send_group_reply_with_reference_optimized(self, group_id: int, message_id: int, message: str, max_retries: Optional[int] = None) -> bool:
        """
        发送群组引用回复消息（优化版）
        复用原有的发送消息函数，支持长文本自动转发
        
        Args:
            group_id: 群ID
            message_id: 要引用的消息ID
            message: 回复内容
            max_retries: 最大重试次数
            
        Returns:
            发送是否成功
        """
        # 检查是否需要转发（长文本）
        if (self.forward_enabled and 
            len(message) > self.forward_threshold):
            
            logger.info(f"检测到长文本引用回复，长度: {len(message)}，先发送引用提示，然后转发")
            
            # 先发送引用回复提示
            reply_hint = f"[CQ:reply,id={message_id}]请查收"
            hint_msg = Message(
                type="group",
                target_id=group_id,
                content=reply_hint,
                max_retries=max_retries or self.max_retries
            )
            
            hint_result = await self._send_with_retry(hint_msg)
            if hint_result.get("status") != "ok":
                logger.warning(f"引用提示发送失败: {hint_result.get('error', '未知错误')}")
                # 如果提示发送失败，回退到普通引用回复
                return await self._send_group_reply_simple(group_id, message_id, message, max_retries)
            
            # 然后发送转发消息
            return await self._send_group_forward_message(group_id, message)
        else:
            # 短文本，直接发送引用回复
            return await self._send_group_reply_simple(group_id, message_id, message, max_retries)
    
    async def _send_private_reply_with_reference_optimized(self, user_id: int, message_id: int, message: str, max_retries: Optional[int] = None) -> bool:
        """
        发送私聊引用回复消息（优化版）
        私聊不支持转发，直接发送引用回复
        
        Args:
            user_id: 用户ID
            message_id: 要引用的消息ID
            message: 回复内容
            max_retries: 最大重试次数
            
        Returns:
            发送是否成功
        """
        return await self._send_private_reply_simple(user_id, message_id, message, max_retries)
    
    async def _send_group_reply_simple(self, group_id: int, message_id: int, message: str, max_retries: Optional[int] = None) -> bool:
        """
        发送简单的群组引用回复消息
        
        Args:
            group_id: 群ID
            message_id: 要引用的消息ID
            message: 回复内容
            max_retries: 最大重试次数
            
        Returns:
            发送是否成功
        """
        # 构建引用回复消息 - 使用OneBot标准的回复格式
        reply_message = f"[CQ:reply,id={message_id}]{message}"
        
        msg = Message(
            type="group",
            target_id=group_id,
            content=reply_message,
            max_retries=max_retries or self.max_retries
        )
        
        result = await self._send_with_retry(msg)
        return result.get("status") == "ok"
    
    async def _send_private_reply_simple(self, user_id: int, message_id: int, message: str, max_retries: Optional[int] = None) -> bool:
        """
        发送简单的私聊引用回复消息
        
        Args:
            user_id: 用户ID
            message_id: 要引用的消息ID
            message: 回复内容
            max_retries: 最大重试次数
            
        Returns:
            发送是否成功
        """
        # 构建引用回复消息 - 使用OneBot标准的回复格式
        reply_message = f"[CQ:reply,id={message_id}]{message}"
        
        msg = Message(
            type="private",
            target_id=user_id,
            content=reply_message,
            max_retries=max_retries or self.max_retries
        )
        
        result = await self._send_with_retry(msg)
        return result.get("status") == "ok"
    
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
    
    async def send_group_reaction(self, group_id: int, message_id: int, reaction_code: str = "👍", is_add: bool = True) -> bool:
        """
        发送群消息表情回复（兼容OneBot和NapCat）
        
        Args:
            group_id: 群ID
            message_id: 消息ID
            reaction_code: 表情代码，默认为👍
            is_add: 是否添加表情，False为移除表情
            
        Returns:
            发送是否成功
        """
        try:
            # 首先尝试使用OneBot的set_group_reaction
            result = await self.client.set_group_reaction(group_id, message_id, reaction_code, is_add)
            if result.get("status") == "ok":
                logger.info(f"表情回复发送成功(OneBot): group:{group_id}, message:{message_id}, reaction:{reaction_code}")
                return True
            else:
                logger.warning(f"OneBot表情回复失败: {result.get('error', '未知错误')}，尝试NapCat API")
                # 回退到NapCat的set_msg_emoji_like
                return await self._send_napcat_emoji_like(message_id, reaction_code)
        except Exception as e:
            logger.warning(f"OneBot表情回复异常: {e}，尝试NapCat API")
            # 回退到NapCat的set_msg_emoji_like
            return await self._send_napcat_emoji_like(message_id, reaction_code)
    
    async def _send_napcat_emoji_like(self, message_id: int, reaction_code: str) -> bool:
        """
        使用NapCat的set_msg_emoji_like发送表情回复
        
        Args:
            message_id: 消息ID
            reaction_code: 表情代码
            
        Returns:
            发送是否成功
        """
        try:
            # 将表情代码转换为emoji_id（这里使用简单的映射）
            emoji_id = self._convert_reaction_to_emoji_id(reaction_code)
            result = await self.client.set_msg_emoji_like(message_id, emoji_id)
            if result.get("status") == "ok":
                logger.info(f"表情回复发送成功(NapCat): message:{message_id}, emoji_id:{emoji_id}")
                return True
            else:
                logger.error(f"NapCat表情回复发送失败: {result.get('error', '未知错误')}")
                return False
        except Exception as e:
            logger.error(f"NapCat表情回复发送异常: {e}")
            return False
    
    def _convert_reaction_to_emoji_id(self, reaction_code: str) -> str:
        """
        将表情代码转换为NapCat的emoji_id
        
        Args:
            reaction_code: 表情代码
            
        Returns:
            emoji_id字符串
        """
        # 常用表情映射表（可以根据需要扩展）
        emoji_mapping = {
            "👍": "1",      # 点赞
            "❤️": "2",      # 爱心
            "😂": "3",      # 笑哭
            "😮": "4",      # 惊讶
            "😢": "5",      # 哭泣
            "🤖": "32",     # 机器人（AI相关）
            "✅": "124",    # 成功
            "❌": "10060",  # 失败
            "2": "2",       # 直接使用数字ID
            "32": "32",
            "124": "124",
            "10060": "10060"
        }
        
        # 如果是直接的emoji_id，直接返回
        if reaction_code.isdigit():
            return reaction_code
            
        # 查找映射表
        emoji_id = emoji_mapping.get(reaction_code, "1")  # 默认使用点赞
        logger.debug(f"表情代码转换: {reaction_code} -> {emoji_id}")
        return emoji_id
    
    async def send_reaction_to_event(self, event: Union[GroupMessageEvent, PrivateMessageEvent], reaction_code: str = "🤖") -> bool:
        """
        对事件消息发送表情回复
        
        Args:
            event: 消息事件
            reaction_code: 表情代码，默认为🤖
            
        Returns:
            发送是否成功
        """
        if isinstance(event, GroupMessageEvent):
            return await self.send_group_reaction(event.group_id, event.message_id, reaction_code)
        else:
            logger.warning("私聊消息不支持表情回复")
            return False
    
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
    
    def get_forward_status(self) -> Dict[str, Any]:
        """获取转发消息状态"""
        return {
            "enabled": self.forward_enabled,
            "threshold": self.forward_threshold,
            "max_length": self.forward_max_length,
            "max_count": self.forward_max_count
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
