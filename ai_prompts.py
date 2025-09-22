"""
AI总结功能的Prompt模板
专门针对MediaWiki技术问题讨论的总结
"""

from datetime import datetime
from typing import List, Dict


class MediaWikiSummaryPrompts:
    """MediaWiki技术问题总结的Prompt模板"""
    
    @staticmethod
    def get_daily_summary_prompt(messages: List[Dict], date: str) -> str:
        """
        生成每日MediaWiki技术问题总结的prompt
        
        Args:
            messages: 消息列表，每个消息包含时间、发送者、内容等
            date: 总结的日期
            
        Returns:
            完整的prompt字符串
        """
        
        # 构建消息内容，使用正确的字段名
        messages_text = ""
        for msg in messages:
            time_str = msg.get('time', '')  # 格式化后的时间字符串
            username = msg.get('username', f"用户{msg.get('user_id', 0)}")
            message = msg.get('message', '')
            datetime_str = msg.get('datetime', '')  # 完整的日期时间
            
            # 使用更清晰的格式
            messages_text += f"[{datetime_str}] {username}: {message}\n"
        
        # 统计基本信息
        total_messages = len(messages)
        unique_users = len(set(msg.get('username', '') for msg in messages))
        
        prompt = f"""你是一个专业的群聊内容分析师。请分析以下{date}的群聊记录，共{total_messages}条消息，{unique_users}人参与讨论。

群聊记录：
{messages_text}

请按照以下格式进行总结：

## 📊 今日讨论概览
- 总消息数：{total_messages}条
- 参与讨论人数：{unique_users}人
- 主要讨论时间段：[根据消息时间分析活跃时段]

## 💬 主要话题
请识别并总结讨论中的主要话题，按重要性排序：

### 话题1：[话题标题]
- **讨论内容**：[简要描述讨论的核心内容]
- **参与者**：[主要参与讨论的用户]
- **关键观点**：[讨论中的重要观点或结论]
- **讨论热度**：[高/中/低，基于消息数量和参与度]

### 话题2：[话题标题]
[同上格式，如果有多个话题的话]

## 🔍 技术问题与解决方案
如果讨论中涉及技术问题，请列出：

### 问题：[问题描述]
- **问题详情**：[具体问题描述]
- **解决方案**：[讨论中提到的解决方案]
- **状态**：[已解决/讨论中/待跟进]

## 🎯 重点信息
- **最活跃的讨论**：[参与人数最多或消息最多的话题]
- **重要决定或结论**：[如果有达成共识或做出决定]
- **需要跟进的事项**：[未完成或需要后续处理的内容]

## 👥 活跃用户
- **发言最多**：[发言次数最多的用户及发言数]
- **贡献突出**：[提供有价值信息或解决方案的用户]

## 📝 其他值得关注的内容
[其他有价值的讨论内容、有趣的话题或重要信息]

请确保总结内容客观准确，突出重点，如果当天讨论内容较少或主要是日常聊天，请如实反映。"""

        return prompt
    
    @staticmethod
    def get_weekly_summary_prompt(summaries: List[str], week_range: str) -> str:
        """
        生成周总结的prompt
        
        Args:
            summaries: 每日总结列表
            week_range: 周范围
            
        Returns:
            周总结prompt
        """
        
        summaries_text = "\n\n".join([f"## {i+1}日总结\n{summary}" for i, summary in enumerate(summaries)])
        
        prompt = f"""你是一个专业的MediaWiki技术问题分析师。请基于以下{week_range}的每日总结，生成周总结报告。

每日总结内容：
{summaries_text}

请按照以下格式生成周总结：

## 📊 本周技术讨论概览
- 总讨论天数：X天
- 总问题数：X个
- 已解决问题：X个
- 待解决问题：X个

## 🔥 本周热点问题
[列出本周讨论最热烈的问题]

## 🎯 问题分类统计
- **扩展问题**：X个
- **模板问题**：X个
- **权限问题**：X个
- **性能问题**：X个
- **其他问题**：X个

## 🏆 本周技术亮点
[总结本周的技术创新和解决方案]

## 📈 趋势分析
- **问题趋势**：[问题类型的变化趋势]
- **技术发展**：[技术讨论的发展方向]
- **用户活跃度**：[用户参与度的变化]

## 🔮 下周关注重点
[基于本周讨论，预测下周可能关注的技术问题]

请确保周总结具有前瞻性和指导性。"""

        return prompt


class SummaryTemplates:
    """总结模板类"""
    
    @staticmethod
    def format_message_for_ai(message_data: Dict) -> str:
        """
        格式化消息数据为AI可读的格式
        
        Args:
            message_data: 消息数据字典
            
        Returns:
            格式化后的消息字符串
        """
        timestamp = message_data.get('time', '')
        sender = message_data.get('sender', '')
        content = message_data.get('content', '')
        message_type = message_data.get('type', 'text')
        
        if message_type == 'text':
            return f"[{timestamp}] {sender}: {content}"
        elif message_type == 'image':
            return f"[{timestamp}] {sender}: [发送了图片]"
        elif message_type == 'file':
            return f"[{timestamp}] {sender}: [发送了文件: {content}]"
        else:
            return f"[{timestamp}] {sender}: [{message_type}消息]"
    
    @staticmethod
    def create_summary_filename(date: datetime) -> str:
        """
        创建总结文件名
        
        Args:
            date: 日期对象
            
        Returns:
            文件名
        """
        return f"summary_{date.strftime('%Y%m%d')}.md"
    
    @staticmethod
    def create_weekly_summary_filename(start_date: datetime, end_date: datetime) -> str:
        """
        创建周总结文件名
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            文件名
        """
        return f"weekly_summary_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.md"
