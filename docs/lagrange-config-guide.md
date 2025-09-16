# Lagrange.OneBot 配置详解

根据 [Lagrange.OneBot 官方文档](https://lagrangedev.github.io/Lagrange.Doc/v1/Lagrange.OneBot/Config/)，以下是 `appsettings.json` 配置文件的详细说明。

## 📋 完整配置文件示例

```json
{
  "$schema": "https://raw.githubusercontent.com/LagrangeDev/Lagrange.Core/master/Lagrange.OneBot/Resources/appsettings_schema.json",
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  },
  "SignServerUrl": "https://sign.lagrangecore.org/api/sign",
  "SignProxyUrl": "",
  "MusicSignServerUrl": "",
  "Account": {
    "Uin": 0,
    "Password": "",
    "Protocol": "Linux",
    "AutoReconnect": true,
    "GetOptimumServer": true
  },
  "Message": {
    "IgnoreSelf": true,
    "StringPost": false
  },
  "QrCode": {
    "ConsoleCompatibilityMode": false
  },
  "Implementations": [
    {
      "Type": "ReverseWebSocket",
      "Host": "127.0.0.1",
      "Port": 8080,
      "Suffix": "/onebot/v11/ws",
      "ReconnectInterval": 5000,
      "HeartBeatInterval": 5000,
      "HeartBeatEnable": true,
      "AccessToken": ""
    }
  ]
}
```

## 🔧 配置项详细说明

### 1. 日志设置 (Logging)

```json
"Logging": {
  "LogLevel": {
    "Default": "Information"  // 可选: Trace, Debug, Information, Warning, Error
  }
}
```

**说明**：
- `Information`: 正常使用时的日志级别
- `Trace`: 调试时使用，会输出最详细的日志
- 遇到问题时建议改为 `Trace` 以便排查

### 2. 签名服务器设置

```json
"SignServerUrl": "https://sign.lagrangecore.org/api/sign",
"SignProxyUrl": "",
"MusicSignServerUrl": ""
```

**说明**：
- `SignServerUrl`: 签名服务器地址，**必须填写**
- `SignProxyUrl`: 代理服务器地址（可选），仅支持 HTTP 代理
- `MusicSignServerUrl`: 音乐卡片签名服务器（可选）

### 3. 账号设置 (Account)

```json
"Account": {
  "Uin": 0,                    // 您的 QQ 号
  "Password": "",              // 密码（已不支持，留空）
  "Protocol": "Linux",         // 协议类型
  "AutoReconnect": true,       // 自动重连
  "GetOptimumServer": true     // 获取最优服务器
}
```

**填写说明**：
- `Uin`: 填写您的 QQ 号码（数字）
- `Password`: 留空（不再支持密码登录）
- `Protocol`: 推荐使用 `"Linux"`
- `AutoReconnect`: 建议设为 `true`
- `GetOptimumServer`: 建议设为 `true`

### 4. 消息设置 (Message)

```json
"Message": {
  "IgnoreSelf": true,          // 忽略机器人自身消息
  "StringPost": false          // 是否以 CQ 码形式上报
}
```

**说明**：
- `IgnoreSelf`: 建议设为 `true`，避免机器人响应自己的消息
- `StringPost`: 建议设为 `false`

### 5. 二维码设置 (QrCode)

```json
"QrCode": {
  "ConsoleCompatibilityMode": false  // 控制台兼容模式
}
```

**说明**：
- 如果二维码显示异常，可以设为 `true`

### 6. 服务实现 (Implementations)

这是最重要的部分，决定了如何与您的 Nonebot2 机器人连接。

#### 反向 WebSocket（推荐）

```json
{
  "Type": "ReverseWebSocket",
  "Host": "127.0.0.1",
  "Port": 8080,
  "Suffix": "/onebot/v11/ws",
  "ReconnectInterval": 5000,
  "HeartBeatInterval": 5000,
  "HeartBeatEnable": true,
  "AccessToken": ""
}
```

**说明**：
- `Host`: 保持 `"127.0.0.1"`
- `Port`: 保持 `8080`（与您的 Nonebot2 配置一致）
- `Suffix`: 保持 `"/onebot/v11/ws"`
- `AccessToken`: 如果您的 Nonebot2 设置了访问令牌，在这里填写

## 🚀 快速配置步骤

### 1. 使用配置生成器

访问 [Lagrange Config Generator](https://lagrangedev.github.io/Lagrange.Doc/v1/Lagrange.OneBot/Config/) 在线生成配置文件：

1. 在左侧表单中填写：
   - **Uin**: 您的 QQ 号
   - **Protocol**: 选择 "Linux"
   - 其他保持默认设置

2. 点击右侧的 "Copy to Clipboard" 按钮

3. 将内容保存为 `appsettings.json` 文件

### 2. 手动配置

如果您想手动配置，只需要修改以下关键字段：

```json
{
  "Account": {
    "Uin": 您的QQ号,  // 例如: 123456789
    "Protocol": "Linux"
  },
  "Implementations": [
    {
      "Type": "ReverseWebSocket",
      "Host": "127.0.0.1",
      "Port": 8080,
      "Suffix": "/onebot/v11/ws"
    }
  ]
}
```

## ⚠️ 重要注意事项

### 1. 签名服务器
- **必须配置** `SignServerUrl`
- 推荐使用官方提供的签名服务器
- 如果连接失败，可以尝试其他签名服务器

### 2. 协议选择
- 推荐使用 `"Linux"` 协议
- 避免使用 `"Android"` 协议（与某些签名服务器不兼容）

### 3. 端口配置
- 确保 `Port` 与您的 Nonebot2 配置一致
- 默认使用 `8080` 端口

### 4. 登录方式
- 推荐使用扫码登录
- 密码登录已不再支持

## 🔍 常见问题

### Q: 签名服务器连接失败
**A**: 尝试更换签名服务器地址，或检查网络连接

### Q: 二维码显示异常
**A**: 将 `ConsoleCompatibilityMode` 设为 `true`

### Q: 连接 Nonebot2 失败
**A**: 检查端口配置是否一致，确保 Nonebot2 已启动

### Q: 登录失败
**A**: 删除 `Keystore` 文件夹后重新扫码登录

## 📞 获取帮助

如果遇到问题：
1. 查看 [Lagrange 官方文档](https://lagrangedev.github.io/Lagrange.Doc/v1/Lagrange.OneBot/Config/)
2. 检查 GitHub Issues
3. 加入官方 Telegram 群组获取签名服务器信息

---

**配置完成后，您就可以启动 Lagrange.OneBot 并与您的 Nonebot2 机器人连接了！** 🎉
