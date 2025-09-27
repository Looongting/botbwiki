#!/usr/bin/env python3
"""
调试AI响应内容
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.ai_manager import ai_manager


async def debug_ai_response():
    """调试AI响应"""
    print("🔍 调试AI响应内容...\n")
    
    # 测试简单的消息
    test_messages = [
        {"role": "user", "content": "你好，请简单介绍一下自己"}
    ]
    
    print("1️⃣ 测试简单对话...")
    result = await ai_manager.chat_completion(test_messages)
    print(f"AI回复: '{result}'")
    print(f"回复长度: {len(result) if result else 0}")
    print()
    
    # 测试群聊总结
    test_chat = """[10:30:15] 用户123456: 大家好，我想问一下Python的异步编程怎么用？
[10:31:20] 用户789012: 可以用asyncio库，async/await语法
[10:32:05] 用户123456: 能举个具体例子吗？
[10:33:10] 用户789012: 比如这样：async def main(): await asyncio.sleep(1)
[10:34:15] 用户345678: 还有aiohttp可以用来做异步HTTP请求
[10:35:20] 用户123456: 谢谢大家，我试试看"""
    
    prompt = f"""你是一个专业的技术内容分析师。请分析以下群聊记录，提取其中的技术答疑和知识共享内容。

分析要求：
1. 识别所有技术相关的讨论内容（编程、工具使用、问题解决等）
2. 将相同主题的内容合并到一起
3. 提取具体的解决方案、建议和知识点
4. 忽略纯闲聊、表情包、问候等非技术内容
5. 每个主题要包含清晰的名称和具体的方案列表

群聊记录：
{test_chat}

请严格按照以下JSON格式回复，不要添加任何其他文字：
[
  {{
    "name": "具体的技术主题名称",
    "方案": [
      "具体的解决方案或知识点1",
      "具体的解决方案或知识点2"
    ]
  }}
]

如果群聊中没有技术内容，请返回空数组：[]"""
    
    print("2️⃣ 测试群聊总结...")
    summary_messages = [
        {"role": "user", "content": prompt}
    ]
    
    result = await ai_manager.chat_completion(summary_messages)
    print(f"AI回复: '{result}'")
    print(f"回复长度: {len(result) if result else 0}")
    
    if result:
        print("\n📊 回复内容分析:")
        print(f"   是否包含JSON: {'[' in result and ']' in result}")
        print(f"   是否为空: {result.strip() == ''}")
        print(f"   是否只有空格: {result.strip() == ''}")
        print(f"   前50个字符: '{result[:50]}'")
        print(f"   后50个字符: '{result[-50:]}'")


if __name__ == "__main__":
    asyncio.run(debug_ai_response())
