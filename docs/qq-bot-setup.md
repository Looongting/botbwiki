# QQ 机器人完整配置指南

## 🤖 当前状态

您已经成功启动了 **Nonebot2 框架**，但还需要配置 **QQ 机器人本体** 才能与 QQ 群交互。

## 📋 需要安装的组件

### 1. LagrangeCore（推荐）

LagrangeCore 是一个高性能的 Onebot 实现，支持 QQ 协议。

#### 下载 LagrangeCore
1. 访问 [LagrangeCore 发布页面](https://github.com/ClosureMk/LagrangeCore/releases)
2. 下载适合您系统的版本（Windows x64）
3. 解压到任意目录

#### 配置 LagrangeCore
1. 创建配置文件 `config.json`：
```json
{
  "account": {
    "uin": "您的QQ号",
    "password": "您的QQ密码",
    "protocol": 2
  },
  "server": {
    "host": "127.0.0.1",
    "port": 8080
  },
  "log": {
    "level": "info"
  }
}
```

2. 启动 LagrangeCore：
```bash
./LagrangeCore.exe
```

### 2. 其他 Onebot 实现

#### go-cqhttp
- 下载地址：https://github.com/Mrs4s/go-cqhttp/releases
- 配置简单，功能完整

#### mirai
- 基于 Java 的 QQ 机器人框架
- 功能强大但配置复杂

## 🔗 连接配置

### 1. 确保端口一致

检查您的 `.env` 文件：
```bash
ONEBOT_WS_URL=ws://127.0.0.1:8080/ws
ONEBOT_HTTP_URL=http://127.0.0.1:8080
```

### 2. 启动顺序

1. **先启动 Onebot 实现**（如 LagrangeCore）
2. **再启动 Nonebot2 框架**（您的机器人）

### 3. 验证连接

启动后应该看到类似输出：
```
[INFO] 连接到 Onebot 服务成功
[INFO] 机器人已上线
```

## 🧪 测试功能

连接成功后，在 QQ 群中测试：

### 短链生成
```
#测试
#瓦伦
```

### 随机数生成
```
.rand
.randrange 1 50
```

## ⚠️ 注意事项

### 1. QQ 账号安全
- 建议使用小号测试
- 避免频繁操作导致账号被限制
- 遵守 QQ 使用条款

### 2. 网络环境
- 确保网络连接稳定
- 某些网络环境可能需要代理

### 3. 协议版本
- 不同 Onebot 实现支持的协议版本可能不同
- 建议使用最新版本

## 🆘 常见问题

### Q: 连接失败
**A**: 检查：
1. Onebot 服务是否启动
2. 端口是否被占用
3. 防火墙设置

### Q: 机器人无响应
**A**: 检查：
1. QQ 账号是否正常登录
2. 群聊权限设置
3. 机器人是否被禁言

### Q: 功能不工作
**A**: 检查：
1. 插件是否正确加载
2. 消息格式是否正确
3. 日志文件中的错误信息

## 📞 获取帮助

如果遇到问题：
1. 查看 LagrangeCore 官方文档
2. 检查 Nonebot2 官方文档
3. 查看项目日志文件
4. 在相关社区寻求帮助

## 🎯 下一步

1. **下载并配置 LagrangeCore**
2. **启动 Onebot 服务**
3. **重新启动您的机器人**
4. **在 QQ 群中测试功能**

完成这些步骤后，您就拥有了一个完整的 QQ 机器人！🎉
