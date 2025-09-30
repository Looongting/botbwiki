"""
免审权限插件
功能：为指定用户添加wiki的面审权限
支持通过关键字触发，如：?lysk免审 用户ID
"""

import re
import sys
import os
from datetime import datetime, timedelta
from calendar import monthrange
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.log import logger
from nonebot.rule import Rule
from typing import Optional

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.config import config
from src.core.message_sender import get_sender
from src.core.wiki_api import get_wiki_api


def get_month_end_time() -> str:
    """
    获取当前月份最后一天的23:59时间，格式为ISO 8601
    
    Returns:
        ISO 8601格式的时间字符串 (YYYY-MM-DDTHH:MM:SSZ)
    """
    now = datetime.now()
    # 获取当前月份的最后一天
    last_day = monthrange(now.year, now.month)[1]
    
    # 创建当前月份最后一天23:59的时间
    month_end = datetime(now.year, now.month, last_day, 23, 59, 0)
    
    # 转换为ISO 8601格式
    return month_end.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_expiry_time_by_addtime(add_time: str) -> Optional[str]:
    """
    根据addTime配置获取到期时间
    
    Args:
        add_time: 时间类型配置 ("curMonth" 或 "ever")
        
    Returns:
        ISO 8601格式的时间字符串，永久权限返回None
    """
    if add_time == "curMonth":
        return get_month_end_time()
    elif add_time == "ever":
        return None  # 永久权限不需要到期时间
    else:
        # 默认使用月末时间
        logger.warning(f"未知的addTime配置: {add_time}，使用默认的curMonth")
        return get_month_end_time()


def format_expiry_time_display(expiry_time: str) -> str:
    """
    格式化到期时间显示
    
    Args:
        expiry_time: ISO 8601格式的时间字符串
        
    Returns:
        格式化的时间显示字符串
    """
    try:
        # 解析ISO 8601时间
        dt = datetime.strptime(expiry_time, "%Y-%m-%dT%H:%M:%SZ")
        # 格式化为中文显示
        return dt.strftime("%Y年%m月%d日 %H:%M")
    except ValueError:
        return expiry_time


def is_exemption_command() -> Rule:
    """检查是否为免审权限命令"""
    def _check(event: GroupMessageEvent) -> bool:
        # 检查是否在目标群中
        if event.group_id not in config.TARGET_GROUP_IDS:
            return False
        
        message = str(event.get_message()).strip()
        
        # 检查是否以配置的免审关键字开头
        for keyword in config.EXEMPTION_CONFIGS.keys():
            if message.startswith(keyword):
                return True
        
        return False
    
    return Rule(_check)


# 创建消息处理器
exemption_handler = on_message(rule=is_exemption_command(), priority=3)


@exemption_handler.handle()
async def handle_exemption(bot: Bot, event: GroupMessageEvent):
    """处理免审权限请求"""
    try:
        # 获取消息发送器
        message_sender = get_sender()
        
        # 提取消息内容
        message = str(event.get_message()).strip()
        
        # 识别使用的关键字和对应的配置
        exemption_config = None
        keyword = None
        for k in config.EXEMPTION_CONFIGS.keys():
            if message.startswith(k):
                keyword = k
                exemption_config = config.EXEMPTION_CONFIGS[k]
                break
        
        if not exemption_config:
            await message_sender.send_reply(event, "不支持的关键字，请使用配置的关键字")
            return
        
        # 检查是否需要权限验证
        if exemption_config.get("checkPermission", False):
            # 检查发送者是否为群管理员
            if not await _check_user_permission(bot, event):
                # 发送错误表情 - 使用系统表情ID 123 (NO)
                await message_sender.send_reaction_to_event(event, "10060")
                logger.warning(f"用户 {event.user_id} 无权限执行免审操作")
                return
        
        # 提取用户ID
        user_id = await _extract_user_id(message, keyword, event, bot)
        if not user_id:
            # 引用回复提示修改群昵称
            await message_sender.send_reply_with_reference(event, "请修改群昵称带uid")
            return
        
        # 执行免审权限添加
        success, expiry_time, added_groups = await _add_exemption_permission(user_id, exemption_config, event)
        
        if success:
            # 发送成功表情 - 使用系统表情ID 124 (OK)
            await message_sender.send_reaction_to_event(event, "124")
            
            # 获取addTime配置并构建成功消息
            add_time = exemption_config.get("addTime", "curMonth")
            slogan = config.ADD_TIME_SLOGAN.get(add_time, "权限添加成功")
            
            # 构建成功消息
            if expiry_time:
                expiry_display = format_expiry_time_display(expiry_time)
                success_message = f"{slogan}过期时间为{expiry_display}，"
            else:
                success_message = slogan
            
            # 添加用户组信息
            if added_groups:
                groups_info = "、".join(added_groups)
                success_message += f"已添加用户组：{groups_info}"
            
            await message_sender.send_reply_with_reference(event, success_message)
            
            logger.info(f"成功为用户 {user_id} 添加免审权限: {exemption_config['wiki']}, 用户组: {added_groups}, 到期时间: {expiry_time or '永久'}")
        else:
            # 引用回复失败消息
            await message_sender.send_reply_with_reference(event, "权限添加失败")
            logger.error(f"为用户 {user_id} 添加免审权限失败: {exemption_config['wiki']}")
            
    except Exception as e:
        # 检查是否是 FinishedException，如果是则不需要处理
        if "FinishedException" in str(type(e)):
            return
        logger.error(f"免审权限插件错误: {e}")
        # 引用回复异常信息
        try:
            message_sender = get_sender()
            await message_sender.send_reply_with_reference(event, "出现异常问题")
        except:
            pass


async def _check_user_permission(bot: Bot, event: GroupMessageEvent) -> bool:
    """
    检查用户是否有权限执行免审操作
    
    Args:
        bot: 机器人实例
        event: 群消息事件
        
    Returns:
        是否有权限
    """
    try:
        # 获取群成员信息
        group_member_info = await bot.get_group_member_info(
            group_id=event.group_id,
            user_id=event.user_id,
            no_cache=True
        )
        
        if group_member_info:
            # 检查用户角色
            role = group_member_info.get("role", "")
            # 群主(owner)和管理员(admin)有权限
            return role in ["owner", "admin"]
        else:
            logger.warning(f"无法获取用户 {event.user_id} 的群成员信息")
            return False
            
    except Exception as e:
        logger.error(f"检查用户权限异常: {e}")
        return False


async def _extract_user_id(message: str, keyword: str, event: GroupMessageEvent, bot: Bot) -> Optional[str]:
    """
    从消息中提取用户ID
    
    Args:
        message: 原始消息
        keyword: 使用的关键字
        event: 群消息事件
        bot: 机器人实例
        
    Returns:
        用户ID字符串，无法提取时返回None
    """
    try:
        # 方法1：从消息中提取UID
        # 格式：关键字 uid，例如：?lysk免审 2342354
        content = message[len(keyword):].strip()
        
        # 使用正则表达式提取数字UID
        uid_match = re.search(r'\b(\d{6,})\b', content)
        if uid_match:
            uid = uid_match.group(1)
            logger.info(f"从消息中提取到UID: {uid}")
            return uid
        
        # 方法2：从群昵称中提取UID
        logger.info(f"消息中未找到UID，尝试从群昵称提取: {event.user_id}")
        
        # 获取发送者的群昵称
        try:
            group_member_info = await bot.get_group_member_info(
                group_id=event.group_id,
                user_id=event.user_id,
                no_cache=True
            )
            
            if group_member_info:
                card = group_member_info.get("card", "")  # 群昵称
                nickname = group_member_info.get("nickname", "")  # QQ昵称
                
                # 优先从群昵称中提取
                for name in [card, nickname]:
                    if name:
                        uid_match = re.search(r'\b(\d{6,})\b', name)
                        if uid_match:
                            uid = uid_match.group(1)
                            logger.info(f"从群昵称 '{name}' 中提取到UID: {uid}")
                            return uid
                
                logger.warning(f"群昵称和QQ昵称中均未找到UID: card='{card}', nickname='{nickname}'")
            else:
                logger.warning(f"无法获取用户 {event.user_id} 的群成员信息")
                
        except Exception as e:
            logger.error(f"获取群成员信息异常: {e}")
        
        return None
        
    except Exception as e:
        logger.error(f"提取用户ID异常: {e}")
        return None


async def _add_exemption_permission(user_id: str, exemption_config: dict, event: GroupMessageEvent) -> tuple[bool, Optional[str], list]:
    """
    为用户添加免审权限
    
    Args:
        user_id: 用户ID
        exemption_config: 免审配置
        event: 群消息事件
        
    Returns:
        (操作是否成功, 到期时间字符串, 成功添加的用户组列表)
    """
    try:
        # 获取wiki名称和用户组
        wiki_name = exemption_config.get("wiki")
        addgroup = exemption_config.get("addgroup")
        add_time = exemption_config.get("addTime", "curMonth")
        
        if not wiki_name or not addgroup:
            logger.error(f"免审配置不完整: {exemption_config}")
            return False, None, []
        
        # 处理addgroup格式，支持多种配置方式
        if isinstance(addgroup, str):
            # 如果是字符串，检查是否包含|分隔符
            if "|" in addgroup:
                # 使用|分隔的多个用户组
                addgroup = addgroup.split("|")
            else:
                # 单个用户组
                addgroup = [addgroup]
        elif isinstance(addgroup, list):
            # 已经是列表格式，直接使用
            pass
        else:
            logger.error(f"不支持的addgroup格式: {addgroup}")
            return False, None, []
        
        # 创建Wiki API实例
        wiki_api = get_wiki_api(wiki_name)
        
        # 测试连接（通过获取用户信息验证）
        test_user_info = await wiki_api.get_user_info(user_id)
        if not test_user_info:
            logger.error(f"Wiki API连接失败: {wiki_name}")
            return False, None, []
        
        # 根据addTime配置计算到期时间
        expiry_time = get_expiry_time_by_addtime(add_time)
        
        # 构建操作原因
        reason = f"机器人自动添加免审权限 (操作者: {event.user_id}, 群: {event.group_id})"
        
        # 执行添加用户组操作 - 支持多个用户组
        # 根据API文档，使用|分隔多个用户组，一次API调用完成
        groups_str = "|".join(addgroup)
        success = await wiki_api.add_user_to_group(user_id, groups_str, reason, expiry_time)
        
        if success:
            logger.info(f"免审权限添加完成: 用户 {user_id}, 成功添加用户组: {addgroup}, 到期时间: {expiry_time or '永久'}")
            return True, expiry_time, addgroup
        else:
            logger.error(f"免审权限添加失败: 用户 {user_id}, 用户组: {addgroup}")
            return False, None, []
        
    except Exception as e:
        logger.error(f"添加免审权限异常: {e}")
        return False, None, []
