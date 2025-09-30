"""
MediaWiki API 交互模块
用于处理与MediaWiki API的所有交互，包括用户信息查询、权限操作等
"""

import requests
import asyncio
from typing import Optional, List, Dict, Any
from nonebot.log import logger
from .config import config
import urllib.parse


class WikiAPI:
    """MediaWiki API 交互类"""
    
    def __init__(self, wiki_name: str):
        """
        初始化Wiki API客户端
        
        Args:
            wiki_name: Wiki名称，对应WIKI_CONFIGS中的键
        """
        self.wiki_name = wiki_name
        
        # 根据wiki名称映射到对应的配置
        wiki_mapping = {
            "lysk": "gd",  # lysk对应gd配置
            "mistria": "?m",  # mistria对应?m配置
            "tools": "?t"  # tools对应?t配置
        }
        
        config_key = wiki_mapping.get(wiki_name)
        if not config_key:
            raise ValueError(f"不支持的wiki名称: {wiki_name}")
        
        wiki_config = config.WIKI_CONFIGS.get(config_key)
        if not wiki_config:
            raise ValueError(f"Wiki configuration for '{wiki_name}' not found.")
        
        self.api_url = wiki_config["api_url"]
        self.sessdata = config.WIKI_SESSDATA
        self._session = requests.Session()
        if self.sessdata:
            self._session.cookies.update({'SESSDATA': self.sessdata})
    
    async def _make_request(self, params: Dict[str, Any], method: str = "GET") -> Optional[Dict[str, Any]]:
        """
        统一的API请求方法
        
        Args:
            params: 请求参数
            method: 请求方法 (GET/POST)
            
        Returns:
            API响应数据，失败时返回None
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            # 在线程池中执行同步请求
            loop = asyncio.get_event_loop()
            if method.upper() == "POST":
                response = await loop.run_in_executor(
                    None, 
                    lambda: self._session.post(self.api_url, data=params, headers=headers, timeout=15)
                )
            else:
                response = await loop.run_in_executor(
                    None,
                    lambda: self._session.get(self.api_url, params=params, headers=headers, timeout=15)
                )
            
            if response.status_code == 200:
                data = response.json()
                if "error" in data:
                    error = data["error"]
                    logger.error(f"API错误: {error.get('code', 'unknown')} - {error.get('info', 'unknown')} - {self.wiki_name}")
                    return None
                return data
            else:
                logger.error(f"API请求失败: {response.status_code} - {self.wiki_name}")
                return None
                
        except Exception as e:
            logger.error(f"API请求异常: {e} - {self.wiki_name}")
            return None
    
    async def get_csrf_token(self) -> Optional[str]:
        """
        获取CSRF token用于API调用
        
        Returns:
            CSRF token字符串，失败时返回None
        """
        params = {
            "action": "query",
            "format": "json",
            "meta": "tokens",
            "type": "csrf"
        }
        
        data = await self._make_request(params)
        if data and "query" in data and "tokens" in data["query"]:
            token = data["query"]["tokens"].get("csrftoken")
            if token:
                # 处理token中的转义字符
                token = token.replace("\\", "")
                logger.info(f"成功获取CSRF token: {self.wiki_name}")
                return token
            else:
                logger.warning(f"API响应中未找到csrftoken: {self.wiki_name}")
        else:
            logger.warning(f"获取CSRF token失败: {self.wiki_name}")
        
        return None
    
    async def get_userrights_token(self) -> Optional[str]:
        """
        获取用户权限操作专用token
        
        Returns:
            userrights token字符串，失败时返回None
        """
        params = {
            "action": "query",
            "format": "json",
            "meta": "tokens",
            "type": "userrights"
        }
        
        data = await self._make_request(params)
        if data and "query" in data and "tokens" in data["query"]:
            token = data["query"]["tokens"].get("userrightstoken")
            if token:
                # 使用原始token，不进行任何处理（根据测试，原始token包含+号是成功的）
                logger.info(f"成功获取userrights token: {self.wiki_name}")
                return token
            else:
                logger.warning(f"API响应中未找到userrightstoken: {self.wiki_name}")
        else:
            logger.warning(f"获取userrights token失败: {self.wiki_name}")
        
        return None
    
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID或用户名
            
        Returns:
            用户信息字典，失败时返回None
        """
        params = {
            "action": "query",
            "format": "json",
            "list": "users",
            "ususers": user_id,
            "usprop": "groups|rights"
        }
        
        data = await self._make_request(params)
        if data and "query" in data and "users" in data["query"]:
            users = data["query"]["users"]
            if users and len(users) > 0:
                user_info = users[0]
                if "missing" not in user_info:
                    logger.info(f"获取用户 {user_id} 信息成功: {self.wiki_name}")
                    return user_info
                else:
                    logger.warning(f"用户 {user_id} 不存在: {self.wiki_name}")
            else:
                logger.warning(f"未找到用户 {user_id}: {self.wiki_name}")
        else:
            logger.warning(f"获取用户 {user_id} 信息失败: {self.wiki_name}")
        
        return None
    
    async def get_user_groups(self, user_id: str) -> Optional[List[str]]:
        """
        获取用户所属的用户组
        
        Args:
            user_id: 用户ID或用户名
            
        Returns:
            用户组列表，失败时返回None
        """
        user_info = await self.get_user_info(user_id)
        if user_info:
            groups = user_info.get("groups", [])
            logger.info(f"获取用户 {user_id} 的用户组: {groups} - {self.wiki_name}")
            return groups
        return None
    
    async def add_user_to_group(self, user_id: str, group: str, reason: str = "机器人自动添加") -> bool:
        """
        将用户添加到指定用户组
        
        Args:
            user_id: 用户ID（可以是用户名或用户ID）
            group: 用户组名称
            reason: 操作原因
            
        Returns:
            操作是否成功
        """
        # 获取userrights token
        token = await self.get_userrights_token()
        if not token:
            logger.error(f"无法获取userrights token，无法执行用户权限操作: {self.wiki_name}")
            return False
        
        # 构建请求参数
        params = {
            "action": "userrights",
            "format": "json",
            "user": user_id,
            "add": group,
            "reason": reason,
            "token": token
        }
        
        data = await self._make_request(params, method="POST")
        if data and "userrights" in data:
            result = data["userrights"]
            added = result.get("added", [])
            removed = result.get("removed", [])
            
            # 如果用户已经在组中，added会是空列表，但这不是错误
            if group in added:
                logger.info(f"成功将用户 {user_id} 添加到 {group} 组: {self.wiki_name}")
                return True
            elif not added and not removed:
                # 用户已经在组中，操作成功但没有变化
                logger.info(f"用户 {user_id} 已经在 {group} 组中: {self.wiki_name}")
                return True
            else:
                logger.warning(f"用户 {user_id} 添加 {group} 组失败: {self.wiki_name}")
        else:
            logger.error(f"用户权限操作失败: {self.wiki_name}")
        
        return False
    
    async def remove_user_from_group(self, user_id: str, group: str, reason: str = "机器人自动移除") -> bool:
        """
        将用户从指定用户组移除
        
        Args:
            user_id: 用户ID（可以是用户名或用户ID）
            group: 用户组名称
            reason: 操作原因
            
        Returns:
            操作是否成功
        """
        # 获取userrights token
        token = await self.get_userrights_token()
        if not token:
            logger.error(f"无法获取userrights token，无法执行用户权限操作: {self.wiki_name}")
            return False
        
        # 构建请求参数
        params = {
            "action": "userrights",
            "format": "json",
            "user": user_id,
            "remove": group,
            "reason": reason,
            "token": token
        }
        
        data = await self._make_request(params, method="POST")
        if data and "userrights" in data:
            result = data["userrights"]
            removed = result.get("removed", [])
            if group in removed:
                logger.info(f"成功将用户 {user_id} 从 {group} 组移除: {self.wiki_name}")
                return True
            else:
                logger.warning(f"用户 {user_id} 从 {group} 组移除失败: {self.wiki_name}")
        else:
            logger.error(f"用户权限操作失败: {self.wiki_name}")
        
        return False
    
    async def close(self):
        """关闭HTTP客户端"""
        self._session.close()


# 全局Wiki API实例管理
_wiki_apis: Dict[str, WikiAPI] = {}


def get_wiki_api(wiki_name: str) -> WikiAPI:
    """
    获取Wiki API实例（单例模式）
    
    Args:
        wiki_name: Wiki名称
        
    Returns:
        WikiAPI实例
    """
    if wiki_name not in _wiki_apis:
        _wiki_apis[wiki_name] = WikiAPI(wiki_name)
    return _wiki_apis[wiki_name]


async def close_all_wiki_apis():
    """关闭所有Wiki API实例"""
    for api in _wiki_apis.values():
        await api.close()
    _wiki_apis.clear()