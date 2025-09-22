"""
消息记录插件
用于记录群消息，为AI总结功能提供数据源
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
from pathlib import Path

from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.log import logger
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config


class MessageLogger:
    """消息记录器"""
    
    def __init__(self, db_path: str = "message_log.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建消息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    message TEXT NOT NULL,
                    message_type TEXT DEFAULT 'text',
                    timestamp INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_group_date 
                ON messages(group_id, date)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON messages(timestamp)
            ''')
            
            conn.commit()
            conn.close()
            logger.info("消息记录数据库初始化成功")
            
        except Exception as e:
            logger.error(f"初始化消息记录数据库失败: {e}")
    
    def log_message(self, group_id: int, user_id: int, username: str, 
                   message: str, message_type: str = "text", timestamp: int = None):
        """记录消息"""
        try:
            if timestamp is None:
                timestamp = int(datetime.now().timestamp())
            
            date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO messages (group_id, user_id, username, message, message_type, timestamp, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (group_id, user_id, username, message, message_type, timestamp, date))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"记录消息失败: {e}")
    
    def get_messages_by_date(self, group_id: int, date: str) -> List[Dict]:
        """获取指定群指定日期的消息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, username, message, message_type, timestamp
                FROM messages 
                WHERE group_id = ? AND date = ?
                ORDER BY timestamp ASC
            ''', (group_id, date))
            
            results = cursor.fetchall()
            conn.close()
            
            messages = []
            for row in results:
                user_id, username, message, message_type, timestamp = row
                messages.append({
                    'user_id': user_id,
                    'username': username,
                    'message': message,
                    'type': message_type,
                    'timestamp': timestamp,
                    'time': datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"获取消息失败: {e}")
            return []
    
    def get_messages_by_date_range(self, group_id: int, start_date: str, end_date: str) -> List[Dict]:
        """获取指定群指定日期范围的消息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, username, message, message_type, timestamp, date
                FROM messages 
                WHERE group_id = ? AND date BETWEEN ? AND ?
                ORDER BY timestamp ASC
            ''', (group_id, start_date, end_date))
            
            results = cursor.fetchall()
            conn.close()
            
            messages = []
            for row in results:
                user_id, username, message, message_type, timestamp, date = row
                messages.append({
                    'user_id': user_id,
                    'username': username,
                    'message': message,
                    'type': message_type,
                    'timestamp': timestamp,
                    'time': datetime.fromtimestamp(timestamp).strftime("%H:%M:%S"),
                    'date': date
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"获取消息失败: {e}")
            return []
    
    def get_message_stats(self, group_id: int, date: str) -> Dict:
        """获取消息统计信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 总消息数
            cursor.execute('''
                SELECT COUNT(*) FROM messages 
                WHERE group_id = ? AND date = ?
            ''', (group_id, date))
            total_messages = cursor.fetchone()[0]
            
            # 参与人数
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id) FROM messages 
                WHERE group_id = ? AND date = ?
            ''', (group_id, date))
            unique_users = cursor.fetchone()[0]
            
            # 最活跃用户
            cursor.execute('''
                SELECT username, COUNT(*) as msg_count
                FROM messages 
                WHERE group_id = ? AND date = ?
                GROUP BY user_id, username
                ORDER BY msg_count DESC
                LIMIT 5
            ''', (group_id, date))
            top_users = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_messages': total_messages,
                'unique_users': unique_users,
                'top_users': [{'username': username, 'count': count} for username, count in top_users]
            }
            
        except Exception as e:
            logger.error(f"获取消息统计失败: {e}")
            return {'total_messages': 0, 'unique_users': 0, 'top_users': []}


# 创建消息记录器实例
message_logger = MessageLogger()

# 创建消息处理器 - 使用最低优先级，不干扰命令处理
message_handler = on_message(priority=100)


@message_handler.handle()
async def handle_message(bot: Bot, event: GroupMessageEvent):
    """处理群消息并记录"""
    try:
        # 只记录目标群的消息
        if event.group_id != config.TARGET_GROUP_ID:
            return
        
        # 获取用户信息
        user_id = event.user_id
        username = event.sender.nickname or f"用户{user_id}"
        
        # 获取消息内容
        message_text = str(event.get_message())
        message_type = "text"
        
        # 记录消息
        message_logger.log_message(
            group_id=event.group_id,
            user_id=user_id,
            username=username,
            message=message_text,
            message_type=message_type,
            timestamp=event.time
        )
        
        # 只在调试模式下输出日志
        if config.LOG_LEVEL == "DEBUG":
            logger.debug(f"记录消息: {username} -> {message_text[:50]}...")
            
    except Exception as e:
        logger.error(f"消息记录处理错误: {e}")


# 导出消息记录器供其他模块使用
__all__ = ['message_logger', 'MessageLogger']
