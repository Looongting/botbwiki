#!/usr/bin/env python3
"""
检查机器人连接状态
"""

import asyncio
import websockets
import httpx
import json
from datetime import datetime


async def check_websocket_connection():
    """检查 WebSocket 连接"""
    try:
        async with websockets.connect("ws://127.0.0.1:8080/onebot/v11/ws") as websocket:
            print("✅ WebSocket 连接成功！")
            return True
    except Exception as e:
        print(f"❌ WebSocket 连接失败: {e}")
        return False


async def check_http_connection():
    """检查 HTTP 连接"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8080/")
            if response.status_code == 200:
                print("✅ HTTP 连接成功！")
                return True
            else:
                print(f"❌ HTTP 连接失败，状态码: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ HTTP 连接失败: {e}")
        return False


async def get_bot_info():
    """获取机器人信息"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://127.0.0.1:8080/",
                json={
                    "action": "get_login_info",
                    "params": {}
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    bot_info = data.get("data", {})
                    print(f"✅ 机器人信息获取成功！")
                    print(f"   机器人昵称: {bot_info.get('nickname', '未知')}")
                    print(f"   机器人 QQ 号: {bot_info.get('user_id', '未知')}")
                    return True
                else:
                    print(f"❌ 获取机器人信息失败: {data.get('message', '未知错误')}")
                    return False
            else:
                print(f"❌ HTTP 请求失败，状态码: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ 获取机器人信息失败: {e}")
        return False


async def main():
    """主函数"""
    print("🔍 检查机器人连接状态")
    print("=" * 50)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查连接
    ws_ok = await check_websocket_connection()
    http_ok = await check_http_connection()
    
    if ws_ok and http_ok:
        print("\n🎉 连接检查通过！")
        print("正在获取机器人信息...")
        await get_bot_info()
        print("\n✅ 您的 QQ 机器人已经准备就绪！")
        print("现在可以在 QQ 群中测试以下命令：")
        print("  - 发送 #测试 测试短链生成功能")
        print("  - 发送 .rand 测试随机数生成功能")
    else:
        print("\n❌ 连接检查失败！")
        print("请确保：")
        print("  1. Lagrange.OneBot 正在运行")
        print("  2. 端口 8080 没有被其他程序占用")
        print("  3. 防火墙没有阻止连接")


if __name__ == "__main__":
    asyncio.run(main())
