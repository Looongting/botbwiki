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
from typing import Optional, Dict, Tuple
import sys
import os
import hashlib
import time

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# 简单的内存缓存
url_cache: Dict[str, tuple] = {}  # {url_hash: (short_url, timestamp)}
curid_cache: Dict[str, str] = {}  # {page_title: curid}
CACHE_EXPIRE_TIME = 3600  # 缓存1小时


def is_shortlink_command() -> Rule:
    """检查是否为短链生成命令"""
    def _check(event: GroupMessageEvent) -> bool:
        message = str(event.get_message()).strip()
        # 检查是否以配置的关键字开头
        for prefix in config.WIKI_CONFIGS.keys():
            if message.startswith(prefix) and len(message) > len(prefix):
                return True
        return False
    
    return Rule(_check)


# 创建消息处理器
shortlink_handler = on_message(rule=is_shortlink_command(), priority=5)


@shortlink_handler.handle()
async def handle_shortlink(bot: Bot, event: GroupMessageEvent):
    """处理短链生成请求"""
    try:
        # 提取消息内容
        message = str(event.get_message()).strip()
        
        # 识别使用的前缀和对应的wiki配置
        wiki_config = None
        prefix = None
        for p in config.WIKI_CONFIGS.keys():
            if message.startswith(p) and len(message) > len(p):
                prefix = p
                wiki_config = config.WIKI_CONFIGS[p]
                break
        
        if not wiki_config:
            await shortlink_handler.finish("不支持的关键字，请使用配置的关键字")
            return
        
        # 提取检索词（去掉前缀）
        search_term = message[len(prefix):].strip()
        
        if not search_term:
            await shortlink_handler.finish(f"请输入有效的检索词，格式：{prefix}检索词")
            return
        
        # 构建完整 URL
        full_url = f"{wiki_config['url']}/{search_term}"
        
        # 首先尝试使用 curid 方式（最快最可靠）
        try:
            curid_url = await asyncio.wait_for(create_curid_redirect_url(search_term, wiki_config), timeout=2.0)
            if curid_url:
                short_url = curid_url
                logger.info(f"使用curid方式生成链接: {short_url}")
            else:
                # 如果 curid 失败，回退到传统短链服务
                short_url = await asyncio.wait_for(generate_short_url(full_url), timeout=3.0)
        except asyncio.TimeoutError:
            short_url = None
            logger.warning("链接生成总超时，返回原始链接")
        
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
    # 检查缓存
    url_hash = hashlib.md5(url.encode()).hexdigest()
    current_time = time.time()
    
    if url_hash in url_cache:
        cached_short_url, timestamp = url_cache[url_hash]
        if current_time - timestamp < CACHE_EXPIRE_TIME:
            logger.info(f"使用缓存短链: {cached_short_url}")
            return cached_short_url
        else:
            # 缓存过期，删除
            del url_cache[url_hash]
    
    # 创建任务列表，使用真正有效的短链服务
    tasks = [
        asyncio.create_task(asyncio.wait_for(try_vgd_service(url), timeout=1.0)),
        asyncio.create_task(asyncio.wait_for(try_tinyurl_service(url), timeout=1.5)),
        asyncio.create_task(asyncio.wait_for(try_is_gd_service(url), timeout=1.5)),
        asyncio.create_task(asyncio.wait_for(try_0x0_service(url), timeout=1.0)),
        asyncio.create_task(asyncio.wait_for(try_b23_tv_service(url), timeout=2.0))
    ]
    
    try:
        # 使用 asyncio.as_completed 获取第一个完成的任务
        for completed_task in asyncio.as_completed(tasks):
            try:
                result = await completed_task
                if result:
                    # 缓存结果
                    url_cache[url_hash] = (result, current_time)
                    logger.info(f"短链生成成功并缓存: {result}")
                    
                    # 取消其他未完成的任务
                    for task in tasks:
                        if not task.done():
                            task.cancel()
                    return result
            except asyncio.TimeoutError:
                logger.warning("短链服务超时，尝试下一个服务")
                continue
            except Exception as e:
                logger.warning(f"短链服务任务失败: {e}")
                continue
                
    except Exception as e:
        logger.error(f"短链生成服务调用失败: {e}")
    
    return None


async def get_page_curid(page_title: str, wiki_config: dict) -> Optional[str]:
    """通过 MediaWiki API 获取页面的 curid"""
    # 检查缓存（使用wiki名称作为缓存键的一部分）
    cache_key = f"{wiki_config['name']}:{page_title}"
    if cache_key in curid_cache:
        logger.info(f"使用缓存的curid: {curid_cache[cache_key]}")
        return curid_cache[cache_key]
    
    try:
        # MediaWiki API 端点
        api_url = wiki_config['api_url']
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            # 获取页面信息
            params = {
                "action": "query",
                "format": "json",
                "titles": page_title,
                "prop": "info"
            }
            
            response = await client.get(api_url, params=params, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            if response.status_code == 200:
                data = response.json()
                
                if "query" in data and "pages" in data["query"]:
                    pages = data["query"]["pages"]
                    
                    for page_id, page_info in pages.items():
                        if page_id != "-1":  # 页面存在
                            # 缓存结果
                            curid_cache[cache_key] = page_id
                            logger.info(f"获取到curid: {page_id} (页面: {page_title}, Wiki: {wiki_config['name']})")
                            return page_id
                        else:
                            logger.warning(f"页面不存在: {page_title} (Wiki: {wiki_config['name']})")
                            return None
                else:
                    logger.warning("API响应格式错误")
                    return None
            else:
                logger.warning(f"API请求失败: {response.status_code}")
                return None
                
    except Exception as e:
        logger.warning(f"获取curid失败: {e}")
        return None


async def create_curid_redirect_url(page_title: str, wiki_config: dict) -> Optional[str]:
    """创建基于curid的自动跳转URL"""
    curid = await get_page_curid(page_title, wiki_config)
    if curid:
        # 直接返回带curid的URL，这样更简单可靠
        curid_url = f"{wiki_config['url']}/index.php?curid={curid}"
        logger.info(f"创建curid跳转URL: {curid_url}")
        return curid_url
    
    return None


async def try_vgd_service(url: str) -> Optional[str]:
    """尝试使用 v.gd 服务（通常很快且可靠）"""
    try:
        async with httpx.AsyncClient(
            timeout=config.SHORTLINK_TIMEOUT,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            response = await client.get(
                "https://v.gd/create.php",
                params={"format": "simple", "url": url},
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            
            if response.status_code == 200:
                short_url = response.text.strip()
                if short_url.startswith("http") and "v.gd" in short_url:
                    logger.info(f"v.gd 短链生成成功: {short_url}")
                    return short_url
                else:
                    logger.warning(f"v.gd 返回无效响应: {short_url}")
                    
    except httpx.TimeoutException:
        logger.warning("v.gd 服务超时")
    except Exception as e:
        logger.warning(f"v.gd 服务失败: {e}")
    
    return None


async def try_0x0_service(url: str) -> Optional[str]:
    """尝试使用 0x0.st 服务（通常很快）"""
    try:
        async with httpx.AsyncClient(
            timeout=config.SHORTLINK_TIMEOUT,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            response = await client.post(
                "https://0x0.st",
                data={"shorten": url},
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            
            if response.status_code == 200:
                short_url = response.text.strip()
                if short_url.startswith("http") and "0x0.st" in short_url:
                    logger.info(f"0x0.st 短链生成成功: {short_url}")
                    return short_url
                else:
                    logger.warning(f"0x0.st 返回无效响应: {short_url}")
                    
    except httpx.TimeoutException:
        logger.warning("0x0.st 服务超时")
    except Exception as e:
        logger.warning(f"0x0.st 服务失败: {e}")
    
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
        async with httpx.AsyncClient(
            timeout=config.SHORTLINK_TIMEOUT,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        ) as client:
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
        async with httpx.AsyncClient(
            timeout=config.SHORTLINK_TIMEOUT,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        ) as client:
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


