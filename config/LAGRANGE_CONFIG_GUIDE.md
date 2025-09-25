# Lagrange.OneBot 配置指南

## 配置文件说明

`lagrange-config-template.json` 是 Lagrange.OneBot 的配置文件模板，包含了完整的配置选项和详细注释。

## 配置步骤

### 1. 复制配置文件
```bash
# 复制模板到实际配置位置
sudo cp config/lagrange-config-template.json /opt/lagrange/appsettings.json
```

### 2. 修改配置
根据你的需求修改 `/opt/lagrange/appsettings.json` 中的配置项。

## 配置项详解

### 基础配置

#### 日志配置
```json
"Logging": {
  "LogLevel": {
    "Default": "Information",  // 日志级别：Debug, Information, Warning, Error
    "Microsoft": "Warning",
    "Microsoft.Hosting.Lifetime": "Information"
  }
}
```

#### 签名服务器配置（必须）
```json
"SignServerUrl": "https://sign.lagrangecore.org/api/sign/39038"  // 官方签名服务器
```

### 账号配置

#### 登录方式
- **扫码登录**：`"Uin": 0`（推荐）
- **密码登录**：设置 `"Uin": 你的QQ号` 和 `"Password": "你的密码"`

#### 协议类型
- `"Linux"`：Linux 协议（推荐）
- `"Android"`：Android 协议
- `"Windows"`：Windows 协议

### 服务实现配置

#### WebSocket 服务（用于 NoneBot2）
```json
{
  "Type": "ForwardWebSocket",
  "Host": "127.0.0.1",        // 127.0.0.1 仅本地访问，* 允许所有IP
  "Port": 8080,               // WebSocket 端口
  "Suffix": "/onebot/v11/ws", // WebSocket 路径
  "ReconnectInterval": 5000,  // 重连间隔（毫秒）
  "HeartBeatInterval": 5000,  // 心跳间隔（毫秒）
  "HeartBeatEnable": true,    // 启用心跳
  "AccessToken": ""           // 访问令牌（可选）
}
```

#### HTTP API 服务（用于直接调用）
```json
{
  "Type": "Http",
  "Host": "*",                // * 允许所有IP访问
  "Port": 8081,               // HTTP API 端口
  "AccessToken": ""           // 访问令牌（可选）
}
```

## 使用场景

### 场景1：仅使用 NoneBot2 框架
```json
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
  }
]
```

### 场景2：同时使用 NoneBot2 和 HTTP API
```json
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
    "Host": "*",
    "Port": 8081,
    "AccessToken": ""
  }
]
```

### 场景3：仅使用 HTTP API
```json
"Implementations": [
  {
    "Type": "Http",
    "Host": "*",
    "Port": 8081,
    "AccessToken": ""
  }
]
```

## 安全配置

### 访问令牌
为了安全起见，建议设置访问令牌：

```json
{
  "Type": "Http",
  "Host": "*",
  "Port": 8081,
  "AccessToken": "your_secret_token_here"
}
```

使用令牌时，需要在请求头中添加：
```bash
curl -X POST http://127.0.0.1:8081/send_private_msg \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_secret_token_here" \
  -d '{"user_id": 123456789, "message": "测试消息"}'
```

### 网络访问控制
- `"Host": "127.0.0.1"`：仅允许本地访问
- `"Host": "*"`：允许所有IP访问
- `"Host": "192.168.1.100"`：仅允许特定IP访问

## 云服务器配置

### 控制台兼容模式
在云服务器上，建议启用控制台兼容模式：

```json
"QrCode": {
  "ConsoleCompatibilityMode": true  // 云服务器建议设为true
}
```

### 防火墙配置
如果使用 HTTP API，需要开放对应端口：

```bash
# 开放 8081 端口（HTTP API）
sudo ufw allow 8081

# 开放 8080 端口（WebSocket，如果需要外部访问）
sudo ufw allow 8080
```

## 测试配置

### 测试 WebSocket 连接
```bash
# 检查端口是否监听
ss -tlnp | grep 8080
```

### 测试 HTTP API
```bash
# 测试获取登录信息
curl -X POST http://127.0.0.1:8081/get_login_info \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 常见问题

### 1. 端口冲突
如果端口被占用，可以修改配置中的端口号：
```json
"Port": 8082  // 改为其他端口
```

### 2. 连接失败
检查防火墙设置和网络配置：
```bash
# 检查防火墙状态
sudo ufw status

# 检查端口监听
ss -tlnp | grep 8081
```

### 3. 权限问题
确保配置文件权限正确：
```bash
sudo chown root:root /opt/lagrange/appsettings.json
sudo chmod 644 /opt/lagrange/appsettings.json
```

## 重启服务

修改配置后，需要重启 Lagrange.OneBot 服务：

```bash
sudo systemctl restart lagrange-onebot
```

## 验证配置

### 检查服务状态
```bash
sudo systemctl status lagrange-onebot
```

### 查看日志
```bash
sudo journalctl -u lagrange-onebot -f
```

### 测试 API 功能
```bash
# 使用我们提供的测试工具
python tools/simple_private_reply.py
python tools/lagrange_api_test.py basic
```

## 配置示例

### 完整配置示例
参考 `config/lagrange-config-template.json` 文件，其中包含了所有配置项的详细注释和说明。

### 最小配置示例
```json
{
  "SignServerUrl": "https://sign.lagrangecore.org/api/sign/39038",
  "Account": {
    "Uin": 0,
    "Protocol": "Linux",
    "AutoReconnect": true,
    "GetOptimumServer": true
  },
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
      "Host": "*",
      "Port": 8081,
      "AccessToken": ""
    }
  ]
}
```

这个最小配置包含了：
- 官方签名服务器
- 扫码登录
- Linux 协议
- WebSocket 服务（端口 8080）
- HTTP API 服务（端口 8081）
