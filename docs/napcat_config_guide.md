# NapCat 配置指南

本指南详细说明如何正确配置 NapCat 以避免常见的端口冲突问题。

## 概述

NapCat 是一个基于 NTQQ 的 OneBot V11 协议实现，支持 HTTP 和 WebSocket 两种通信方式。正确的端口配置是确保机器人正常工作的关键。

## 核心原则

### 1. 端口分离原则
- **HTTP 服务器**：用于机器人发送 API 请求（如发送消息、获取信息）
- **WebSocket 服务器**：用于接收事件推送（如收到消息、群成员变化）
- **关键要求**：HTTP 和 WebSocket 必须使用不同端口，避免冲突

### 2. 推荐端口配置
- HTTP API：`8080` 端口
- WebSocket：`8081` 端口

## 配置文件位置

NapCat 的配置文件通常位于：
```
/root/Napcat/opt/QQ/resources/app/app_launcher/napcat/config/
```

主要配置文件：
- `onebot11_[QQ号].json` - OneBot V11 协议配置
- `napcat_[QQ号].json` - NapCat 主配置
- `webui.json` - Web 管理界面配置

## 正确的 OneBot 配置示例

### onebot11_[QQ号].json
```json
{
  "network": {
    "httpServers": [
      {
        "enable": true,
        "host": "127.0.0.1",
        "port": 8080,
        "secret": "",
        "enableHeart": true,
        "enablePost": true,
        "enableWebsocket": false
      }
    ],
    "httpSseServers": [],
    "httpClients": [],
    "websocketServers": [
      {
        "enable": true,
        "host": "127.0.0.1",
        "port": 8081,
        "path": "/onebot/v11/ws",
        "secret": "",
        "enableHeart": true
      }
    ],
    "websocketClients": [],
    "plugins": []
  },
  "musicSignUrl": "",
  "enableLocalFile2Url": false,
  "parseMultMsg": false
}
```

### 关键配置说明

#### HTTP 服务器配置
- `enable: true` - 启用 HTTP 服务器
- `port: 8080` - HTTP API 端口
- `enablePost: true` - **必须启用**，否则无法接收 POST 请求
- `enableWebsocket: false` - **必须禁用**，避免与 WebSocket 服务器冲突

#### WebSocket 服务器配置
- `enable: true` - 启用 WebSocket 服务器
- `port: 8081` - WebSocket 端口，必须与 HTTP 端口不同
- `path: "/onebot/v11/ws"` - WebSocket 路径

## 机器人端配置

### .env 文件配置
```bash
# OneBot 连接配置
# WebSocket 用于接收消息事件（端口 8081）
ONEBOT_WS_URL=ws://127.0.0.1:8081/onebot/v11/ws
ONEBOT_WS_URLS=["ws://127.0.0.1:8081/onebot/v11/ws"]

# HTTP API 用于发送消息和调用接口（端口 8080）
ONEBOT_HTTP_URL=http://127.0.0.1:8080
ONEBOT_HTTP_API_URL=http://127.0.0.1:8080
```

## 常见问题与解决方案

### 问题 1：HTTP 426 Upgrade Required
**症状**：机器人收到消息但不回复，API 调用返回 `HTTP 426: Upgrade Required`

**原因**：HTTP 和 WebSocket 服务配置在同一端口

**解决方案**：
1. 检查 `onebot11_[QQ号].json` 配置
2. 确保 HTTP 和 WebSocket 使用不同端口
3. 确保 HTTP 服务器的 `enableWebsocket` 为 `false`

### 问题 2：WebSocket 连接失败
**症状**：机器人日志显示 WebSocket 连接失败

**原因**：机器人配置的 WebSocket URL 端口不正确

**解决方案**：
1. 检查 `.env` 文件中的 `ONEBOT_WS_URL`
2. 确保端口与 NapCat WebSocket 服务器端口一致

### 问题 3：enablePost 为 false
**症状**：HTTP API 无法正常工作

**原因**：`enablePost` 设置为 `false`

**解决方案**：
1. 修改 `onebot11_[QQ号].json`
2. 设置 `enablePost: true`
3. 重启 NapCat

## 配置验证

### 1. 检查端口监听状态
```bash
# 检查端口是否正确监听
ss -tlnp | grep -E "(8080|8081)"

# 应该看到：
# 127.0.0.1:8080 LISTEN (HTTP)
# 127.0.0.1:8081 LISTEN (WebSocket)
```

### 2. 测试 HTTP API
```bash
curl -X POST http://127.0.0.1:8080/get_status \
     -H "Content-Type: application/json" \
     -d "{}"

# 正确响应示例：
# {"status":"ok","retcode":0,"data":{"online":true,"good":true}}
```

### 3. 检查机器人连接状态
查看机器人日志，应该看到：
```
[INFO] nonebot | OneBot V11 | Bot [QQ号] connected
```

## 最佳实践

### 1. 配置文件管理
- 修改配置前先备份
- 使用版本控制管理配置文件
- 记录每次配置变更的原因

### 2. 端口规划
- 为不同服务预留端口范围
- 避免使用系统保留端口
- 文档化端口分配方案

### 3. 安全考虑
- 仅在必要时开放外部访问
- 使用 secret 进行身份验证
- 定期检查端口开放状态

### 4. 监控与维护
- 定期检查服务状态
- 监控端口占用情况
- 及时处理配置冲突

## 故障排查流程

1. **检查配置文件**：确认端口配置正确
2. **验证端口状态**：检查端口是否正常监听
3. **测试 API 连通性**：使用 curl 测试 HTTP API
4. **查看日志**：检查 NapCat 和机器人日志
5. **重启服务**：必要时重启 NapCat 和机器人

## 参考资源

- [NapCat 官方文档](https://napneko.github.io/NapCatQQ/)
- [OneBot V11 协议规范](https://onebot.dev/)
- [NoneBot2 文档](https://nonebot.dev/)

---

**注意**：本指南基于 NapCat 的常见配置场景编写，具体配置可能因版本和环境而异。遇到问题时，请参考最新的官方文档。