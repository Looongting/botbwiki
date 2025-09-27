#!/usr/bin/env python3
"""
调试群消息内容
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.http_client import get_client
from src.core.config import config


async def debug_messages():
    """调试群消息内容"""
    print("🔍 调试群消息内容...\n")
    
    test_group_id = config.TEST_GROUP_ID
    print(f"📋 测试群ID: {test_group_id}")
    
    try:
        client = get_client()
        result = await client.get_group_msg_history(test_group_id)
        
        if result.get("status") != "ok":
            print(f"❌ 获取历史消息失败: {result.get('error', '未知错误')}")
            return
        
        messages = result.get("data", {}).get("messages", [])
        print(f"✅ 获取到 {len(messages)} 条历史消息\n")
        
        # 显示前10条消息的完整内容
        print("📝 前10条消息内容:")
        for i, msg in enumerate(messages[:10]):
            content = msg.get("content", "")
            time_str = datetime.fromtimestamp(msg.get("time", 0)).strftime("%Y-%m-%d %H:%M:%S")
            user_id = msg.get("user_id", "未知")
            message_type = msg.get("message_type", "text")
            
            print(f"\n{i+1}. [{time_str}] 用户{user_id} ({message_type}):")
            print(f"   内容: {content}")
            
            # 检查是否包含技术关键词
            tech_keywords = ["python", "代码", "编程", "bug", "错误", "函数", "变量", "API", "数据库", "服务器", "配置", "安装", "运行", "编译", "部署", "git", "github", "docker", "linux", "windows", "mac", "开发", "测试", "调试", "优化", "性能", "内存", "CPU", "网络", "协议", "框架", "库", "包", "依赖", "版本", "更新", "升级", "修复", "问题", "解决", "方案", "方法", "技巧", "经验", "教程", "文档", "手册", "指南"]
            
            content_lower = content.lower()
            found_keywords = [kw for kw in tech_keywords if kw in content_lower]
            if found_keywords:
                print(f"   🔧 技术关键词: {', '.join(found_keywords)}")
        
        # 统计技术相关内容
        print(f"\n📊 消息分析:")
        tech_count = 0
        for msg in messages:
            content = msg.get("content", "").lower()
            if any(kw in content for kw in tech_keywords):
                tech_count += 1
        
        print(f"   总消息数: {len(messages)}")
        print(f"   可能包含技术内容的消息数: {tech_count}")
        print(f"   技术内容比例: {tech_count/len(messages)*100:.1f}%")
        
    except Exception as e:
        print(f"❌ 调试过程中发生异常: {e}")


if __name__ == "__main__":
    asyncio.run(debug_messages())
