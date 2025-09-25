# Lagrange.OneBot API 测试工具

这个目录包含了用于测试 Lagrange.OneBot HTTP API 的工具。

## 工具说明

### 1. `lagrange_api_test.py` - 完整 API 测试工具

这是一个功能完整的测试工具，支持多种测试模式：

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

**功能包括：**
- ✅ 获取登录信息
- ✅ 获取群列表
- ✅ 获取好友列表
- ✅ 获取群成员列表
- ✅ 发送群消息
- ✅ 发送私聊消息
- ✅ 交互式命令界面

### 2. `simple_private_reply.py` - 简单私聊回复测试

这是一个简单的测试工具，专门用于测试私聊消息发送：

```bash
python tools/simple_private_reply.py
```

**功能：**
- ✅ 发送私聊测试消息
- ✅ 显示发送结果
- ✅ 错误诊断提示

## 使用前提

1. **确保 Lagrange.OneBot 正在运行**
2. **确保 HTTP API 已启用**
3. **配置正确的 API 地址**（在 `.env` 文件中设置 `ONEBOT_HTTP_URL`）
4. **配置机器人主人ID**（在 `.env` 文件中设置 `BOT_MASTER_ID`）

## 配置示例

在 `.env` 文件中添加：

```env
# OneBot HTTP API 地址
ONEBOT_HTTP_URL=http://127.0.0.1:8080

# 机器人主人ID（用于私聊测试）
BOT_MASTER_ID=123456789
```

## 两种实现方式对比

### 当前方式：NoneBot2 + WebSocket
- **优点：**
  - 事件驱动，自动处理消息
  - 框架成熟，插件生态丰富
  - 代码结构清晰，易于维护
  - 自动重连和错误处理

- **缺点：**
  - 依赖框架，学习成本较高
  - 灵活性相对较低

### 直接 HTTP API 调用
- **优点：**
  - 直接控制，灵活性高
  - 不依赖特定框架
  - 可以精确控制 API 调用时机
  - 适合特殊需求或集成到其他系统

- **缺点：**
  - 需要手动处理事件监听
  - 需要自己实现重连和错误处理
  - 代码量相对较大

## 推荐使用场景

- **日常机器人开发**：推荐使用 NoneBot2 + WebSocket 方式
- **特殊功能测试**：可以使用 HTTP API 直接调用
- **系统集成**：如果要将机器人功能集成到其他系统，可以使用 HTTP API
- **调试和测试**：使用这些测试工具验证 API 功能

## 注意事项

1. **同时使用**：WebSocket 和 HTTP API 可以同时使用，不冲突
2. **权限检查**：确保机器人有发送消息的权限
3. **频率限制**：注意 API 调用频率，避免被限制
4. **错误处理**：实际使用时需要完善的错误处理机制
