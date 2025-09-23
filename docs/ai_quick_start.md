# AI功能快速开始

## 5分钟配置AI功能

### 1. 选择AI服务

推荐使用**LongCat AI**（默认），成本低、响应快：

```bash
# 在.env文件中添加
LONGCAT_API_KEY=your_longcat_api_key_here
DEFAULT_AI_SERVICE=longcat
```

或者使用**火山引擎AI**作为备用：

```bash
# 在.env文件中添加
ARK_API_KEY=your_volc_api_key_here
DEFAULT_AI_SERVICE=volc
```

### 2. 配置触发词（可选）

默认触发词是`?ai`，可以自定义：

```bash
# 自定义触发词
AI_TRIGGER_PREFIX=@ai
```

### 3. 重启机器人

```bash
sudo systemctl restart qq-bot
```

### 4. 测试功能

在群内发送：

```
?ai_test          # 测试连接
?ai_status        # 查看状态
?ai 你好          # 开始对话
```

## 常见问题

### Q: 如何获取LongCat API Key？
A: 访问 https://longcat.chat/platform ，使用美团App扫码登录后申请API密钥

### Q: 如何切换AI服务？
A: 修改`.env`文件中的`DEFAULT_AI_SERVICE`为`longcat`或`volc`

### Q: 支持多个AI服务同时使用吗？
A: 是的，系统会自动切换到可用的备用服务

### Q: 如何自定义触发词？
A: 修改`.env`文件中的`AI_TRIGGER_PREFIX`

## 完整配置示例

```bash
# AI功能配置
AI_TRIGGER_PREFIX=?ai
DEFAULT_AI_SERVICE=longcat
AI_SUMMARY_MAX_TOKENS=2000
AI_SUMMARY_TIMEOUT=30

# LongCat AI配置（推荐）
LONGCAT_API_KEY=your_longcat_api_key_here
LONGCAT_API_URL=https://api.longcat.chat/openai
LONGCAT_MODEL=LongCat-Flash-Chat

# 火山引擎AI配置（备用）
ARK_API_KEY=your_volc_api_key_here
VOLC_AI_REGION=cn-beijing
VOLC_AI_ENDPOINT=ep-20250811175605-fxzbh

# 群组配置
TARGET_GROUP_IDS=[717421103,1059707281,123456789]
```
