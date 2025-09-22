# QQ机器人AI总结功能项目概览

**项目状态**: 🚨 核心功能阻塞中  
**创建时间**: 2025-09-23  
**最后更新**: 2025-09-23 02:45  

## 📋 项目需求

### 核心功能需求
实现QQ群聊消息的AI智能总结功能，用户可以通过命令获取指定时间段的群聊内容总结。

### 具体功能要求
1. **AI连接测试**: `?ai_test` - 验证AI服务连接状态
2. **AI对话功能**: `?ai <问题>` - 与AI进行简单对话
3. **群消息总结**: `?ai_summary [日期]` - 总结指定日期的群聊内容
4. **批量总结**: `?ai_auto <天数>` - 批量生成多天的总结（管理员功能）

### 目标用户场景
- **群管理员**: 快速了解群内讨论的主要话题
- **技术群**: 总结技术讨论要点和解决方案
- **日常群**: 回顾重要信息和活跃话题

## 🏗️ 系统架构

### 整体架构图
```
用户命令 → QQ群 → Lagrange.OneBot → NoneBot2机器人 → AI插件 → 火山引擎AI
    ↑                                                        ↓
    └─────────────── AI总结结果 ←─── 消息处理 ←─── 历史消息获取
```

### 核心组件
1. **Lagrange.OneBot**: QQ协议实现，提供WebSocket和HTTP API
2. **NoneBot2机器人**: 消息处理框架，插件系统
3. **AI插件**: 自定义插件，处理AI相关命令
4. **火山引擎AI**: 提供AI对话和总结能力
5. **消息存储**: 本地数据库存储历史消息（计划中）

### 数据流程
```
1. 用户发送: ?ai_summary 2025-09-22
2. 机器人接收命令并解析参数
3. 获取指定日期的群聊历史消息
4. 过滤和预处理消息内容
5. 调用AI API生成总结
6. 格式化总结结果并回复用户
7. 保存总结到本地文件
```

## ⚙️ 技术配置

### 环境要求
- **操作系统**: Ubuntu Linux
- **Python版本**: 3.12+
- **框架**: NoneBot2
- **AI服务**: 火山引擎AI (ARK API)

### 关键配置文件

#### 1. 环境变量配置 (`.env`)
```bash
# OneBot连接配置
ONEBOT_WS_URL=ws://127.0.0.1:8080/onebot/v11/ws
ONEBOT_HTTP_URL=http://127.0.0.1:8080

# 火山引擎AI配置
ARK_API_KEY=your_api_key_here
VOLC_AI_REGION=cn-beijing
VOLC_AI_ENDPOINT=ep-20250811175605-fxzbh
VOLC_AI_API_URL=https://ark.cn-beijing.volces.com/api/v3/chat/completions

# 目标群配置（支持多群）
TARGET_GROUP_IDS=[717421103,1059707281]

# AI功能配置
AI_SUMMARY_MAX_TOKENS=2000
AI_SUMMARY_TIMEOUT=30
AI_LOG_DIR=AI_LOG
```

#### 2. OneBot配置 (`/opt/lagrange/appsettings.json`)
```json
{
  "Implementations": [
    {
      "Type": "ForwardWebSocket",
      "Host": "127.0.0.1",
      "Port": 8080,
      "Suffix": "/onebot/v11/ws"
    },
    {
      "Type": "Http", 
      "Host": "127.0.0.1",
      "Port": 8081
    }
  ]
}
```

### 服务状态
- **lagrange-onebot.service**: OneBot协议服务
- **qq-bot.service**: NoneBot2机器人服务

## 📊 当前实现状态

### ✅ 已完成功能
1. **基础架构**: 
   - NoneBot2框架搭建完成
   - AI插件开发完成
   - 多群支持实现

2. **AI服务集成**:
   - 火山引擎AI API连接正常
   - `?ai_test` 命令工作正常
   - `?ai <问题>` 对话功能正常

3. **系统集成**:
   - WebSocket连接稳定
   - 命令识别和响应正常
   - 插件加载和运行正常

### ❌ 核心阻塞问题

#### 问题1: OneBot HTTP API调用失败
```
现象: HTTP API返回400错误
影响: 无法获取群聊历史消息
测试: curl -X POST http://127.0.0.1:8080/get_group_msg_history
结果: HTTP/1.1 400 Bad Request
```

#### 问题2: 消息获取流程断裂
```
期望流程: 获取历史消息 → AI处理 → 生成总结
实际状况: [无法获取] → AI处理 → 生成总结
核心问题: 第一步"获取历史消息"失败
```

#### 问题3: 缺少本地消息缓存
```
当前状态: 完全依赖OneBot API获取消息
风险: API限制、网络问题导致功能不可用
需求: 实现本地消息存储和缓存机制
```

## 🔧 相关文件结构

```
/home/ubuntu/botbwiki/
├── bot.py                     # 机器人主程序
├── config.py                  # 配置管理
├── .env                       # 环境变量配置
├── plugins/
│   ├── ai_summary.py          # AI功能插件（核心）
│   └── ai_test_simple.py      # AI测试插件
├── ai_summary_manager.py      # AI总结管理器
├── ai_prompts.py             # AI提示词模板
├── test_ai.py                # AI功能测试脚本
├── AI_LOG/                   # AI总结结果存储目录
├── docs/
│   ├── ai_usage.md           # AI功能使用说明
│   └── AI_FEATURE_SUMMARY.md # 功能总结文档
└── requirements.txt          # Python依赖
```

## 🚨 当前急需解决的问题

### 优先级1: 修复消息获取
- **问题**: OneBot HTTP API调用失败
- **影响**: 核心AI总结功能完全不可用
- **需要**: 调研OneBot API文档，找到正确调用方式

### 优先级2: 实现消息缓存
- **问题**: 缺少本地消息存储
- **影响**: 依赖不稳定的API调用
- **需要**: 设计并实现消息数据库存储

### 优先级3: 完整流程测试
- **问题**: 端到端功能未验证
- **影响**: 不确定完整功能是否可用
- **需要**: 在真实环境中测试完整工作流

## 📋 解决方案思路

### 方案1: 修复HTTP API调用
- 调研Lagrange.OneBot官方文档
- 测试不同的API端点和参数格式
- 检查认证和权限配置

### 方案2: 实时消息收集+本地存储
- 通过WebSocket实时收集群消息
- 存储到本地SQLite数据库
- AI总结时从本地数据库查询

### 方案3: 混合架构
- WebSocket用于实时通信和命令响应
- HTTP API用于历史数据获取（修复后）
- 本地数据库作为缓存和备份

## 🎯 成功标准

### 功能验证
- [ ] `?ai_test` 返回正常响应
- [ ] `?ai 问题` 可以正常对话
- [ ] `?ai_summary` 可以生成真实的群聊总结
- [ ] `?ai_auto 7` 可以批量生成7天的总结

### 性能要求
- 消息获取响应时间 < 5秒
- AI总结生成时间 < 30秒
- 系统稳定运行，无频繁错误

### 数据质量
- 获取的消息完整准确
- AI总结内容相关且有价值
- 总结格式清晰易读

## 📞 技术支持信息

### 相关API文档
- [Lagrange.OneBot文档](https://github.com/LagrangeDev/Lagrange.Core)
- [OneBot标准](https://onebot.dev/)
- [火山引擎AI API](https://www.volcengine.com/docs/82379)

### 调试命令
```bash
# 检查服务状态
sudo systemctl status lagrange-onebot qq-bot

# 查看日志
sudo journalctl -u qq-bot -f

# 测试API
curl -X POST http://127.0.0.1:8080/get_login_info -H "Content-Type: application/json" -d '{}'
```

---

**重要提示**: 这是一个正在开发中的项目，核心功能（AI总结）目前由于消息获取问题而无法正常工作。新的对话应该首先关注解决OneBot HTTP API调用问题。
