#!/usr/bin/env python3
"""
简单的私聊回复测试工具
演示如何使用 Lagrange.OneBot HTTP API 发送私聊消息
"""

import asyncio
import httpx
import json
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.config import config


async def send_private_message(user_id: int, message: str) -> dict:
    """
    发送私聊消息
    
    Args:
        user_id: 目标用户ID
        message: 消息内容
        
    Returns:
        API响应结果
    """
    api_url = f"{config.ONEBOT_HTTP_API_URL}/send_private_msg"
    
    payload = {
        "user_id": user_id,
        "message": message
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                api_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


async def main():
    """主函数"""
    print("🤖 简单私聊回复测试工具")
    print("=" * 40)
    
    # 检查配置
    if not config.TEST_USER_ID:
        print("❌ 错误: 未配置 TEST_USER_ID")
        print("请在 .env 文件中设置 TEST_USER_ID=测试对象的QQ号")
        return
    
    print(f"📡 API 地址: {config.ONEBOT_HTTP_API_URL}")
    print(f"👤 测试用户: {config.TEST_USER_ID}")
    print()
    
    # 发送测试消息
    test_message = "🤖 这是通过 HTTP API 发送的私聊测试消息！\n\n" \
                  "✅ 如果你收到这条消息，说明 HTTP API 调用成功！\n" \
                  "🕐 发送时间: " + str(asyncio.get_event_loop().time())
    
    print("📤 正在发送私聊消息...")
    result = await send_private_message(config.TEST_USER_ID, test_message)
    
    print("📋 发送结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result.get("status") == "ok":
        print("\n✅ 私聊消息发送成功！")
        print("请检查你的QQ是否收到消息。")
    else:
        print("\n❌ 私聊消息发送失败！")
        print("请检查:")
        print("1. Lagrange.OneBot 是否正在运行")
        print("2. HTTP API 地址是否正确")
        print("3. 机器人是否已登录")


if __name__ == "__main__":
    asyncio.run(main())
