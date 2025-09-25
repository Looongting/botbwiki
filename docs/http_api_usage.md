# HTTP API 使用指南

本文档介绍如何使用 Lagrange.OneBot 的 HTTP API 功能，包括配置、调用方法和实际应用场景。

## 概述

HTTP API 是 Lagrange.OneBot 提供的另一种通信方式，与 WebSocket 方式相比，它更适合：
- 主动发送消息
- 系统集成
- 特殊功能测试
- 调试和验证

**重要**：HTTP API 和 WebSocket 可以同时使用，不会冲突！

## 配置启用

### 1. 修改 Lagrange 配置

在 `/opt/lagrange/appsettings.json` 中添加 HTTP API 配置：

```json
{
  "Implementations": [
    {
      "Type": "ForwardWebSocket",
      "Host": "127.0.0.1",
      "Port": 8080,
      "Suffix": "/onebot/v11/ws",
      "ReconnectInterval": 5000,
      "HeartBeatInterval": 5000,
      "HeartBeatEnable": true,
      "AccessToken": ""
    },
    {
      "Type": "Http",
      "Host": "127.0.0.1",
      "Port": 8080,
      "AccessToken": ""
    }
  ]
}
```

### 2. 配置环境变量

在项目根目录的 `.env` 文件中添加：

```env
# OneBot HTTP API 地址
ONEBOT_HTTP_URL=http://127.0.0.1:8080

# 测试用配置（可选）
TEST_USER_ID=123456789
TEST_GROUP_ID=123456789
```

### 3. 重启服务

```bash
sudo systemctl restart lagrange-onebot
```

## API 调用方法

### 基础调用格式

所有 HTTP API 调用都使用 POST 方法，请求格式如下：

```http
POST http://127.0.0.1:8080/{action}
Content-Type: application/json

{
  "参数名": "参数值"
}
```

### 常用 API 接口

#### 1. 发送私聊消息

```http
POST http://127.0.0.1:8080/send_private_msg
Content-Type: application/json

{
  "user_id": 123456789,
  "message": "你好，这是测试消息！"
}
```

#### 2. 发送群消息

```http
POST http://127.0.0.1:8080/send_group_msg
Content-Type: application/json

{
  "group_id": 123456789,
  "message": "大家好，这是群消息测试！"
}
```

#### 3. 获取登录信息

```http
POST http://127.0.0.1:8080/get_login_info
Content-Type: application/json

{}
```

#### 4. 获取群列表

```http
POST http://127.0.0.1:8080/get_group_list
Content-Type: application/json

{}
```

#### 5. 获取好友列表

```http
POST http://127.0.0.1:8080/get_friend_list
Content-Type: application/json

{}
```

#### 6. 获取群成员列表

```http
POST http://127.0.0.1:8080/get_group_member_list
Content-Type: application/json

{
  "group_id": 123456789
}
```

## Python 代码示例

### 基础客户端类

```python
import asyncio
import httpx
import json
from typing import Dict, Any

class LagrangeAPIClient:
    """Lagrange.OneBot HTTP API 客户端"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8080"):
        self.base_url = base_url
        
    async def call_api(self, action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """调用 OneBot API"""
        if params is None:
            params = {}
            
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/{action}",
                    json=params,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    return response.json()
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
    
    async def send_private_msg(self, user_id: int, message: str) -> Dict[str, Any]:
        """发送私聊消息"""
        return await self.call_api("send_private_msg", {
            "user_id": user_id,
            "message": message
        })
    
    async def send_group_msg(self, group_id: int, message: str) -> Dict[str, Any]:
        """发送群消息"""
        return await self.call_api("send_group_msg", {
            "group_id": group_id,
            "message": message
        })
    
    async def get_login_info(self) -> Dict[str, Any]:
        """获取登录信息"""
        return await self.call_api("get_login_info")
    
    async def get_friend_list(self) -> Dict[str, Any]:
        """获取好友列表"""
        return await self.call_api("get_friend_list")
    
    async def get_group_list(self) -> Dict[str, Any]:
        """获取群列表"""
        return await self.call_api("get_group_list")
    
    async def get_group_member_list(self, group_id: int) -> Dict[str, Any]:
        """获取群成员列表"""
        return await self.call_api("get_group_member_list", {
            "group_id": group_id
        })
```

### 使用示例

```python
async def main():
    # 创建客户端
    client = LagrangeAPIClient()
    
    # 获取登录信息
    login_info = await client.get_login_info()
    print(f"登录信息: {login_info}")
    
    # 发送私聊消息
    result = await client.send_private_msg(
        user_id=123456789,
        message="你好，这是通过 HTTP API 发送的消息！"
    )
    print(f"发送结果: {result}")
    
    # 发送群消息
    result = await client.send_group_msg(
        group_id=123456789,
        message="大家好，这是群消息！"
    )
    print(f"发送结果: {result}")

# 运行示例
asyncio.run(main())
```

## 测试工具

项目提供了完整的测试工具来验证 HTTP API 功能：

### 1. 完整功能测试

```bash
# 基础 API 测试（获取登录信息、群列表、好友列表）
python tools/lagrange_api_test.py basic

# 发送消息测试
python tools/lagrange_api_test.py send

# 获取群成员测试
python tools/lagrange_api_test.py members

# 交互式测试模式
python tools/lagrange_api_test.py interactive
```

### 2. 简单私聊测试

```bash
python tools/simple_private_reply.py
```

### 3. 交互式命令

在交互式模式下，可以使用以下命令：

```
send_group <群ID> <消息>     # 发送群消息
send_private <用户ID> <消息>  # 发送私聊消息
login_info                 # 获取登录信息
group_list                 # 获取群列表
friend_list                # 获取好友列表
members <群ID>             # 获取群成员列表
help                       # 显示帮助
quit                       # 退出
```

## 响应格式

### 成功响应

```json
{
  "status": "ok",
  "data": {
    "message_id": 123456
  }
}
```

### 失败响应

```json
{
  "status": "failed",
  "retcode": 10001,
  "msg": "错误信息"
}
```

## 常见问题

### 1. 连接失败

**问题**：HTTP API 调用返回连接错误

**解决方案**：
- 检查 Lagrange.OneBot 是否正在运行
- 确认 HTTP API 配置已启用
- 验证端口号是否正确（默认 8080）

### 2. 权限不足

**问题**：发送消息失败，提示权限不足

**解决方案**：
- 确认机器人已加入目标群
- 检查机器人是否有发送消息的权限
- 验证用户ID或群ID是否正确

### 3. 消息发送失败

**问题**：API 调用成功但消息未发送

**解决方案**：
- 检查消息内容是否包含敏感词
- 确认目标用户或群组存在
- 查看 Lagrange.OneBot 日志排查问题

## 最佳实践

### 1. 错误处理

```python
async def safe_send_message(client, user_id, message):
    """安全发送消息，包含错误处理"""
    try:
        result = await client.send_private_msg(user_id, message)
        if result.get("status") == "ok":
            print("消息发送成功")
            return True
        else:
            print(f"消息发送失败: {result.get('msg', '未知错误')}")
            return False
    except Exception as e:
        print(f"发送消息时发生异常: {e}")
        return False
```

### 2. 频率控制

```python
import asyncio

async def send_with_rate_limit(client, messages, delay=1.0):
    """带频率限制的消息发送"""
    for message in messages:
        await client.send_private_msg(user_id, message)
        await asyncio.sleep(delay)  # 避免发送过快
```

### 3. 批量操作

```python
async def send_to_multiple_groups(client, group_ids, message):
    """向多个群发送消息"""
    tasks = []
    for group_id in group_ids:
        task = client.send_group_msg(group_id, message)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## 与 WebSocket 的协同使用

HTTP API 和 WebSocket 可以同时使用：

- **WebSocket**：用于接收消息事件（NoneBot2 处理）
- **HTTP API**：用于主动发送消息

这种组合方式可以充分发挥两种通信方式的优势：

```python
# 在 NoneBot2 插件中使用 HTTP API
from nonebot import get_driver
from src.core.config import config

async def send_notification(message: str):
    """发送通知消息"""
    client = LagrangeAPIClient(config.ONEBOT_HTTP_URL)
    
    # 向所有目标群发送通知
    for group_id in config.TARGET_GROUP_IDS:
        await client.send_group_msg(group_id, message)
```

## 总结

HTTP API 为 Lagrange.OneBot 提供了灵活的通信方式，特别适合：

- ✅ 主动发送消息
- ✅ 系统集成
- ✅ 功能测试
- ✅ 调试验证

通过合理使用 HTTP API，可以构建更强大和灵活的机器人应用。
