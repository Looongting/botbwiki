"""
短链生成插件
功能：将 #检索词 格式的消息转换为短链
"""

import re
import httpx
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.log import logger
from nonebot.rule import Rule
import asyncio
from typing import Optional
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config


def is_shortlink_command() -> Rule:
    """检查是否为短链生成命令"""
    def _check(event: GroupMessageEvent) -> bool:
        message = str(event.get_message()).strip()
        return message.startswith('gd') and len(message) > 2
    
    return Rule(_check)


# 创建消息处理器
shortlink_handler = on_message(rule=is_shortlink_command(), priority=5)


@shortlink_handler.handle()
async def handle_shortlink(bot: Bot, event: GroupMessageEvent):
    """处理短链生成请求"""
    try:
        # 提取消息内容
        message = str(event.get_message()).strip()
        
        # 提取检索词（去掉 gd 前缀）
        search_term = message[2:].strip()
        
        if not search_term:
            await shortlink_handler.finish("请输入有效的检索词，格式：gd检索词")
            return
        
        # 构建完整 URL
        full_url = f"https://wiki.biligame.com/mistria/{search_term}"
        
        # 生成短链
        short_url = await generate_short_url(full_url)
        
        # 准备回复消息
        if short_url:
            reply_message = f"短链生成成功：\n{short_url}"
        else:
            reply_message = f"短链生成失败，请直接访问：\n{full_url}"
        
        # 发送回复消息
        await shortlink_handler.finish(reply_message)
            
    except Exception as e:
        # 检查是否是 FinishedException，如果是则不需要处理
        if "FinishedException" in str(type(e)):
            return
        logger.error(f"短链生成插件错误: {e}")
        try:
            # 提供原始链接作为回退
            message = str(event.get_message()).strip()
            search_term = message[1:].strip()
            if search_term:
                full_url = f"https://wiki.biligame.com/mistria/{search_term}"
                await shortlink_handler.finish(f"短链生成过程中出现错误，请直接访问：\n{full_url}")
            else:
                await shortlink_handler.finish("短链生成过程中出现错误，请稍后重试")
        except:
            pass  # 如果已经 finish 过了，忽略错误


async def generate_short_url(url: str) -> Optional[str]:
    """
    使用多种短链服务生成短链，优先使用最快的服务
    
    Args:
        url: 需要转换的长链接
        
    Returns:
        短链地址，失败时返回 None
    """
    # 创建任务列表，按可靠性排序（b23.tv 经常连接失败，放在最后）
    tasks = [
        asyncio.create_task(try_tinyurl_service(url)),
        asyncio.create_task(try_is_gd_service(url)),
        asyncio.create_task(try_b23_tv_service(url))
    ]
    
    try:
        # 使用 asyncio.as_completed 获取第一个完成的任务
        for completed_task in asyncio.as_completed(tasks):
            try:
                result = await completed_task
                if result:
                    # 取消其他未完成的任务
                    for task in tasks:
                        if not task.done():
                            task.cancel()
                    return result
            except Exception as e:
                logger.warning(f"短链服务任务失败: {e}")
                continue
                
    except Exception as e:
        logger.error(f"短链生成服务调用失败: {e}")
    
    return None


async def try_b23_tv_service(url: str) -> Optional[str]:
    """尝试使用 b23.tv 服务"""
    try:
        async with httpx.AsyncClient(timeout=config.SHORTLINK_TIMEOUT) as client:
            # 使用 b23.tv 的 API
            response = await client.post(
                "https://api.b23.tv/shorten",
                json={"url": url},
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    short_url = data.get("data", {}).get("short_url")
                    if short_url:
                        logger.info(f"b23.tv 短链生成成功: {short_url}")
                        return short_url
                else:
                    logger.warning(f"b23.tv API 返回错误: {data.get('message')}")
            else:
                logger.warning(f"b23.tv API 返回状态码: {response.status_code}")
                
    except httpx.TimeoutException:
        logger.warning("b23.tv 服务超时")
    except httpx.ConnectError:
        logger.warning("b23.tv 服务连接失败（可能是网络问题或服务不可用）")
    except httpx.HTTPError as e:
        logger.warning(f"b23.tv HTTP 错误: {e}")
    except Exception as e:
        logger.warning(f"b23.tv 服务失败: {type(e).__name__}: {e}")
    
    return None


async def try_tinyurl_service(url: str) -> Optional[str]:
    """尝试使用 TinyURL 服务"""
    try:
        async with httpx.AsyncClient(timeout=config.SHORTLINK_TIMEOUT) as client:
            response = await client.get(
                f"https://tinyurl.com/api-create.php?url={url}",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            
            if response.status_code == 200:
                short_url = response.text.strip()
                if short_url.startswith("http") and "tinyurl.com" in short_url:
                    logger.info(f"TinyURL 短链生成成功: {short_url}")
                    return short_url
                else:
                    logger.warning(f"TinyURL 返回无效响应: {short_url}")
                    
    except httpx.TimeoutException:
        logger.warning("TinyURL 服务超时")
    except Exception as e:
        logger.warning(f"TinyURL 服务失败: {e}")
    
    return None


async def try_is_gd_service(url: str) -> Optional[str]:
    """尝试使用 is.gd 服务"""
    try:
        async with httpx.AsyncClient(timeout=config.SHORTLINK_TIMEOUT) as client:
            response = await client.get(
                f"https://is.gd/create.php?format=simple&url={url}",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            
            if response.status_code == 200:
                short_url = response.text.strip()
                if short_url.startswith("http") and "is.gd" in short_url:
                    logger.info(f"is.gd 短链生成成功: {short_url}")
                    return short_url
                else:
                    logger.warning(f"is.gd 返回无效响应: {short_url}")
                    
    except httpx.TimeoutException:
        logger.warning("is.gd 服务超时")
    except Exception as e:
        logger.warning(f"is.gd 服务失败: {e}")
    
    return None


