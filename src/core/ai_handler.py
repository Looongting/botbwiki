"""
统一的AI处理器 - 消除重复代码，提供统一的AI交互逻辑
"""

import asyncio
from typing import Optional
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.log import logger

from .config import config
from .message_sender import MessageSender


class AIHandler:
    """统一的AI处理器 - 处理所有AI相关的交互逻辑"""
    
    def __init__(self, ai_manager, message_sender: MessageSender):
        self.ai_manager = ai_manager
        self.message_sender = message_sender
    
    async def process_ai_request(
        self, 
        event: GroupMessageEvent, 
        trigger_prefix: str, 
        service_name: Optional[str] = None,
        service_display_name: Optional[str] = None
    ) -> bool:
        """
        统一的AI请求处理逻辑
        
        Args:
            event: 群消息事件
            trigger_prefix: 触发前缀（如 "?ai", "?lc" 等）
            service_name: 指定的AI服务名称，None表示使用默认服务
            service_display_name: 服务显示名称，用于用户提示
            
        Returns:
            bool: 处理是否成功
        """
        try:
            # 提取用户问题
            message = str(event.get_message()).strip()
            
            # 处理不同的消息格式
            if message == trigger_prefix:
                # 用户只发送了触发词，没有问题内容
                user_question = ""
            elif message.startswith(trigger_prefix + " "):
                # 标准格式：触发词 + 空格 + 问题
                user_question = message[len(trigger_prefix):].strip()
            else:
                # 其他情况（理论上不应该到这里）
                user_question = message[len(trigger_prefix):].strip()
            
            # 验证输入
            if not user_question:
                await self._send_usage_help(event, trigger_prefix)
                return True
            
            # 确定AI服务和显示名称
            actual_service, display_name = await self._determine_ai_service(service_name, service_display_name)
            if not actual_service:
                await self.message_sender.send_reply_with_reference(event, "❌ 没有可用的AI服务，请检查配置")
                return False
            
            # 发送表情回复（替代原来的文字提示）
            # 根据不同的AI服务使用不同的表情ID
            reaction_id = await self._get_ai_reaction_id(actual_service)
            await self.message_sender.send_reaction_to_event(event, reaction_id)
            
            # 构建消息
            full_question = f"{config.AI_PROMPT_PREFIX}{user_question}"
            messages = [{"role": "user", "content": full_question}]
            
            # 调用AI服务
            result = await self._call_ai_with_fallback(messages, actual_service, display_name)
            
            # 发送结果
            if result:
                await self.message_sender.send_reply_with_reference(
                    event, 
                    f"🤖 {display_name}回复：\n{result}"
                )
                return True
            else:
                await self.message_sender.send_reply_with_reference(
                    event, 
                    f"❌ {display_name}暂时无法回复，请稍后重试"
                )
                return False
                
        except asyncio.TimeoutError:
            await self.message_sender.send_reply_with_reference(event, "⏰ AI响应超时，请稍后重试")
            return False
        except Exception as e:
            # 忽略FinishedException，这是NoneBot正常的结束异常
            if "FinishedException" not in str(type(e)):
                logger.error(f"AI处理器错误: {e}")
                await self.message_sender.send_reply_with_reference(event, "❌ AI服务异常，请稍后重试")
            return False
    
    async def _send_usage_help(self, event: GroupMessageEvent, trigger_prefix: str):
        """发送使用说明"""
        await self.message_sender.send_reply_with_reference(
            event,
            f"用法：{trigger_prefix} <你的问题>\n"
            f"例如：{trigger_prefix} 今天天气怎么样？"
        )
    
    async def _determine_ai_service(self, service_name: Optional[str], service_display_name: Optional[str]) -> tuple[Optional[str], str]:
        """
        确定要使用的AI服务和显示名称
        
        Returns:
            (service_name, display_name): 服务名称和显示名称的元组
        """
        if service_name:
            # 使用指定的服务
            service_config = config.AI_SERVICES.get(service_name, {})
            if not service_config.get("api_key"):
                return None, ""
            
            display_name = service_display_name or service_config.get('name', service_name)
            return service_name, display_name
        else:
            # 使用默认服务
            default_service = config.default_ai_service
            if not default_service:
                return None, ""
            
            service_config = config.AI_SERVICES.get(default_service, {})
            display_name = service_config.get('name', default_service)
            return default_service, display_name
    
    async def _get_ai_reaction_id(self, service_name: str) -> str:
        """
        获取AI服务对应的表情ID
        
        Args:
            service_name: AI服务名称
            
        Returns:
            表情ID字符串
        """
        service_config = config.AI_SERVICES.get(service_name, {})
        reaction_id = service_config.get('reaction_id', '2')  # 默认使用ID 2
        logger.info(f"AI服务 {service_name} 使用表情ID: {reaction_id}")
        return reaction_id
    
    async def _call_ai_with_fallback(self, messages: list, primary_service: str, display_name: str) -> Optional[str]:
        """
        调用AI服务，支持自动降级到备用服务
        
        Args:
            messages: 消息列表
            primary_service: 主要使用的服务
            display_name: 服务显示名称（用于日志）
            
        Returns:
            AI回复内容，失败时返回None
        """
        # 首先尝试主要服务
        logger.info(f"尝试使用主要AI服务: {primary_service}")
        result = await self.ai_manager.chat_completion(messages, primary_service)
        
        if result:
            return result
        
        # 主要服务失败，尝试其他可用服务
        available_services = self.ai_manager.get_available_services()
        logger.info(f"主要服务失败，尝试备用服务。可用服务: {available_services}")
        
        for backup_service in available_services:
            if backup_service != primary_service:
                logger.info(f"尝试使用备用AI服务: {backup_service}")
                result = await self.ai_manager.chat_completion(messages, backup_service)
                if result:
                    # 记录使用了备用服务
                    backup_display_name = config.AI_SERVICES.get(backup_service, {}).get('name', backup_service)
                    logger.info(f"备用服务 {backup_service} 成功响应，原服务: {primary_service}")
                    return result
        
        # 所有服务都失败
        logger.error(f"所有AI服务都失败，主要服务: {primary_service}, 尝试的备用服务: {[s for s in available_services if s != primary_service]}")
        return None
    
    async def test_ai_connection(self, event: GroupMessageEvent, service_name: Optional[str] = None) -> bool:
        """
        测试AI服务连接
        
        Args:
            event: 群消息事件
            service_name: 指定测试的服务，None表示测试默认服务
            
        Returns:
            bool: 测试是否成功
        """
        try:
            await self.message_sender.send_reply(event, "🤖 正在测试AI连接...")
            
            # 确定要测试的服务
            test_service, display_name = await self._determine_ai_service(service_name, None)
            if not test_service:
                await self.message_sender.send_reply(event, "❌ 没有可用的AI服务，请检查配置")
                return False
            
            # 执行连接测试
            success, message = await self.ai_manager.test_connection(test_service)
            
            if success:
                await self.message_sender.send_reply(
                    event, 
                    f"✅ AI测试成功！\n\n使用的服务: {display_name}\nAI回复：{message}"
                )
                return True
            else:
                # 尝试其他可用服务
                available_services = self.ai_manager.get_available_services()
                if len(available_services) > 1:
                    for backup_service in available_services:
                        if backup_service != test_service:
                            success, message = await self.ai_manager.test_connection(backup_service)
                            if success:
                                backup_display_name = config.AI_SERVICES.get(backup_service, {}).get('name', backup_service)
                                await self.message_sender.send_reply(
                                    event, 
                                    f"⚠️ 默认AI服务失败，但备用服务可用\n\n使用的服务: {backup_display_name}\nAI回复：{message}"
                                )
                                return True
                
                await self.message_sender.send_reply(event, f"❌ AI测试失败\n\n错误信息：{message}")
                return False
                
        except Exception as e:
            # 忽略FinishedException，这是NoneBot正常的结束异常
            if "FinishedException" not in str(type(e)):
                logger.error(f"AI测试错误: {e}")
                await self.message_sender.send_reply(event, "❌ AI测试失败，请稍后重试")
            return False
    
    async def get_ai_status(self, event: GroupMessageEvent) -> bool:
        """
        获取AI服务状态
        
        Args:
            event: 群消息事件
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 获取可用服务
            available_services = self.ai_manager.get_available_services()
            
            status_info = f"🤖 AI服务状态\n\n"
            status_info += f"默认触发词：{config.AI_TRIGGER_PREFIX}\n"
            
            # 显示所有AI服务状态
            for service_name, service_config in config.AI_SERVICES.items():
                service_display_name = service_config.get('name', service_name)
                trigger = service_config.get('trigger', '')
                has_api_key = bool(service_config.get('api_key', ''))
                
                status = "✅ 可用" if has_api_key else "❌ 未配置API密钥"
                
                status_info += f"• {service_display_name}: {status}"
                if trigger:
                    status_info += f" ({trigger})"
                status_info += "\n"
            
            status_info += f"\n可用服务：{', '.join([config.AI_SERVICES.get(s, {}).get('name', s) for s in available_services]) if available_services else '无'}\n"
            
            if available_services:
                status_info += f"\n使用方法：\n"
                status_info += f"• {config.AI_TRIGGER_PREFIX} <问题> - 使用默认AI\n"
                for service_name in available_services:
                    service_config = config.AI_SERVICES.get(service_name, {})
                    trigger = service_config.get('trigger', '')
                    service_display_name = service_config.get('name', service_name)
                    if trigger:
                        status_info += f"• {trigger} <问题> - 使用{service_display_name}\n"
            else:
                status_info += "\n⚠️ 当前没有可用的AI服务，请检查配置"
            
            await self.message_sender.send_reply(event, status_info)
            return True
            
        except Exception as e:
            # 忽略FinishedException，这是NoneBot正常的结束异常
            if "FinishedException" not in str(type(e)):
                logger.error(f"AI状态查询错误: {e}")
                await self.message_sender.send_reply(event, "❌ 查询AI状态失败")
            return False
