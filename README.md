# 项目文档 v2（正式）

面向新手与运维的正式文档。目标：让你在 Ubuntu 上快速完成部署、验证与日常使用。

## 这是什么
- 一个基于 NoneBot2 + OneBot v11（Lagrange.OneBot）的 QQ 机器人
- 功能：多 Wiki 快捷链接、随机数等，插件可扩展
- 主要特性：
  - WIKI快捷链接（`检索词`）基于 curid 直达页，无需第三方短链
  - 随机数生成（`.rand`、`.randrange`）
  - AI对话功能（`?ai 问题`）
  - AI总结功能（`.ai_test`、`.ai`、`.ai_summary`）
  - 免审权限管理（`?lysk免审 用户ID`）- 支持多用户组、灵活权限时间配置
  - 自适应消息发送（长文本自动转发，短文本普通发送）
  - 支持缓存，相同页面命中更快


## 适用对象与平台
- 读者：初次部署者、维护者
- 平台：Linux/Ubuntu（本套文档不包含 Windows/PowerShell）
- 服务器配置要求：
  - **推荐配置**：2核CPU、2GB内存、20GB+ SSD、3Mbps+带宽
  - **最低配置**：1核CPU、1GB内存、10GB硬盘、1Mbps带宽
  - **系统**：Ubuntu Server 24 或更高版本

## 项目结构

```
botbwiki/
├── main.py                     # 项目主入口文件
├── check_env.py               # 环境检查入口
├── requirements.txt           # Python依赖
├── pyproject.toml            # 项目配置
├── README.md                 # 项目文档
├── src/                      # 源代码目录
│   └── core/                # 核心模块
│       ├── config.py        # 配置管理
│       ├── check_env.py     # 环境检查
│       ├── verify_config.py # 配置验证
│       ├── ai_prompts.py    # AI提示词
│       ├── ai_summary_manager.py # AI总结管理
│       ├── http_client.py   # HTTP API 客户端
│       ├── message_sender.py # 统一消息发送器
│       └── wiki_api.py      # Wiki API 封装模块
├── plugins/                  # 插件目录
│   ├── shortlink.py         # 短链功能
│   ├── random.py            # 随机数功能
│   ├── ai_summary.py        # AI总结功能
│   ├── ai_test_simple.py    # AI测试功能
│   ├── ai_chat.py           # AI对话功能（已优化为HTTP API）
│   ├── group_summary.py     # 群消息总结插件（已修复历史消息获取问题）
│   └── exemption.py         # 免审权限管理插件
├── config/                   # 配置文件目录
│   ├── env.example          # 环境变量模板
│   ├── lagrange-config-template.json # Lagrange配置模板
│   └── systemd-service-templates/     # 系统服务模板
├── tools/                    # 工具目录
│   ├── test_message_sender.py # 消息发送器测试工具
│   ├── test_exemption.py    # 免审权限插件测试工具
│   └── ...                  # 其他工具
├── scripts/                  # 脚本目录
│   ├── start.sh             # 启动脚本
│   ├── install.sh           # 安装脚本
│   ├── install_ai_deps.sh   # AI依赖安装
│   └── fix-permissions.sh   # 权限修复
├── docs/                     # 文档目录
│   ├── zero-to-one-ubuntu.md # 部署教程
│   ├── troubleshooting.md   # 故障排查
│   ├── usage.md             # 使用说明（包含AI功能）
│   └── http_api_usage.md    # HTTP API使用指南
├── logs/                     # 日志目录
├── data/                     # 数据目录
└── venv/                     # 虚拟环境
```

## 立即开始
- 从零到一（Ubuntu 单页教程）：`docs/zero-to-one-ubuntu.md`
- 故障排查（5 分钟定位）：`docs/troubleshooting.md`
- 群内使用说明：`docs/usage.md`
- HTTP API 使用指南：`docs/http_api_usage.md`
- 群消息总结使用指南：`docs/group_summary_usage.md`
- 免审权限管理使用指南：`docs/exemption_usage.md`

## 技术栈

- **框架**: NoneBot2（Python异步机器人框架）
- **协议**: OneBot v11（QQ机器人通信协议）
- **核心**: Lagrange.OneBot（QQ客户端实现）
- **短链转换**: 基于curid的直达链接，无需第三方短链服务
- **AI服务**: 火山引擎AI（消息总结和对话功能）
- **Python版本**: 3.8+（推荐使用虚拟环境）
- **系统服务**: systemd（服务化管理）

## 实现方式

- **主要方式**：NoneBot2 + WebSocket（事件驱动，推荐）
- **HTTP API**：支持直接调用，详见 `docs/http_api_usage.md`

## 端口配置说明

**重要**：为了避免端口冲突，系统使用以下端口分配：

- **8080端口**：Lagrange.OneBot WebSocket服务器
  - 提供OneBot v11 WebSocket服务
  - 路径：`ws://127.0.0.1:8080/onebot/v11/ws`
  
- **8081端口**：NoneBot2 HTTP服务器（可选）
  - 仅用于健康检查和调试
  - 实际通信通过WebSocket进行

**架构**：QQ机器人作为WebSocket客户端连接到Lagrange.OneBot的8080端口，而不是自己启动HTTP服务器。

## 配置唯一来源（Single Source of Truth）
- **Lagrange配置（权威）**：`/opt/lagrange/appsettings.json`
  - 必须设置：`SignServerUrl` 为官方签名服务器
  - 云服务器部署：`ConsoleCompatibilityMode=true`
  - 连接稳定：`HeartBeatEnable=true`
  - 安全考虑：`Host=127.0.0.1`（非0.0.0.0）
  - **HTTP API支持**：添加 `"Type": "Http"` 配置启用 HTTP API
- **机器人环境变量模板**：`config/env.example`（复制为项目根目录 `.env` 并按需最小化修改）
  - 核心配置：`ONEBOT_WS_URL=ws://127.0.0.1:8080/onebot/v11/ws`
  - 日志配置：`LOG_LEVEL=INFO`
  - 短链配置：`SHORTLINK_TIMEOUT=2`、`SHORTLINK_RETRY=1`
  - AI配置：`VOLC_AI_ACCESS_KEY`、`VOLC_AI_SECRET_KEY`（火山引擎AI密钥）

### 配置文件说明
- **配置模板**：`config/lagrange-config-template.json` - 包含详细注释的完整配置模板
- **配置指南**：`config/LAGRANGE_CONFIG_GUIDE.md` - 详细的配置说明和使用指南
- **HTTP API 测试工具**：`tools/` 目录下的测试工具，用于验证 HTTP API 功能

## 文档使用建议
- **你是新手**：直接按"从零到一"单页顺序完成部署与验证
- **遇到问题**：打开"故障排查"，按顺序定位
- **想查指令**：打开"群内使用说明"
- **日常维护**：使用systemd命令管理服务，查看日志排查问题

## 管理命令速查

### 服务管理
```bash
# 查看服务状态
sudo systemctl status lagrange-onebot | cat
sudo systemctl status qq-bot | cat

# 重启服务
sudo systemctl restart lagrange-onebot
sudo systemctl restart qq-bot

# 查看日志
sudo journalctl -u lagrange-onebot -f
sudo journalctl -u qq-bot -f
```

### 故障排查
```bash
# 检查端口占用
ss -tlnp | grep 8080 || true

# 检查防火墙状态
sudo ufw status || true

# 验证配置
cd /home/ubuntu/botbwiki
python check_env.py
python -m src.core.verify_config
```

## AI功能说明

✅ **群消息总结功能**: 新增群消息总结插件，支持自动提取技术答疑和知识共享内容

### 最新更新
- **2025-01-XX**: 修复免审权限到期时间时区计算问题
  - 修复了月末权限到期时间计算错误的问题（之前显示为下月1日07:59，现在正确显示为当月31日23:59）
  - 正确处理中国时区（UTC+8）到UTC时间的转换
  - 确保权限到期时间准确对应当月最后一天的23:59（本地时间）
  - 添加时区转换逻辑，避免时区偏移导致的8小时误差
  - 修复QQ机器人回复中的时间显示，将UTC时间正确转换为本地时间显示给用户
- **2025-01-XX**: 优化免审权限操作原因处理机制
  - 修改免审权限添加逻辑，将详细操作原因保留在机器人日志中
  - Wiki的添加操作原因改为使用配置的slogan（如"本月权限新添就，感君劳苦付春秋。"）
  - 提升日志可追溯性，同时保持Wiki操作记录的简洁性
  - 详细原因格式：`机器人自动添加免审权限 (操作者: {user_id}, 群: {group_id})`
- **2025-01-XX**: 修复免审插件表情回复问题
  - 修复了免审插件中emoji表情（❌、✅）无法正常显示的问题
  - 将emoji表情改为系统表情ID：成功使用124（OK），失败使用123（NO）
  - 根据QQ机器人表情对象文档，系统表情（类型1）比emoji表情（类型2）兼容性更好
  - 现在权限验证失败时会正确显示NO表情，操作成功时显示OK表情
- **2025-01-XX**: 优化AI触发响应机制，将文字提示改为表情回复
  - 新增表情回复API支持（基于Lagrange.OneBot的set_group_reaction接口）
  - 修改AI处理器，识别到AI触发时立即发送🤖表情回复
  - 保持原有流程：等待AI回复后引用用户信息并发送"请查收"消息
  - 提升用户体验，减少文字干扰，使用更直观的表情反馈
- **2025-09-26**: 重构AI服务配置系统，支持多AI服务独立触发和手动启用控制
  - 修改AI服务的enabled配置为用户手动配置（不再根据API_KEY自动判断）
  - 为每个AI服务添加独立的trigger_prefix（?lc、?volc、?glm）
  - 优化?ai命令逻辑，使用第一个启用的AI服务作为默认模型
  - 新增根据trigger_prefix获取AI服务的方法
- **2025-09-26**: 修复了群消息总结插件中的历史消息获取问题，现在可以正确获取指定日期的消息记录
- **2025-09-26**: 修正了HTTP客户端API调用参数，使用正确的`message_id`和`count`参数替代错误的`message_seq`参数
- **2025-09-26**: 优化了消息获取逻辑，通过多次调用API获取更多历史消息，解决了查询历史日期时返回空结果的问题
- **2025-09-26**: 简化了时区计算逻辑，API返回的是本地时间戳，无需复杂的时区转换

### 可用命令
- `?ai <问题>` - 与AI进行智能对话（使用第一个启用的AI服务）✅
- `?lc <问题>` - 使用LongCat AI对话 ✅
- `?volc <问题>` - 使用火山引擎AI对话 ✅
- `?glm <问题>` - 使用智谱AI GLM对话 ✅
- `?ai_test` - 测试AI连接是否正常 ✅
- `?ai_status` - 查询AI服务状态 ✅
- `?ai_daySum [日期]` - 日总结指令，总结指定日期的群消息 ✅
- `群总结 [日期]` - 总结指定日期的群消息 ✅
- `批量总结 <天数>` - 批量生成最近N天的总结 ✅
- `查看总结 [日期]` - 查看指定日期的总结结果 ✅
- `?lysk免审 <用户ID>` - 为指定用户添加恋与深空WIKI免审权限（支持多用户组、灵活时间配置） ✅

### 配置要求
1. **AI服务账号**：支持多种AI服务，包括LongCat AI、火山引擎AI、智谱AI GLM等
2. **API密钥**：配置对应AI服务的API密钥到.env文件
3. **服务启用**：通过对应的`_ENABLED`环境变量手动启用AI服务
4. **目标群配置**：支持多群配置，格式：`TARGET_GROUP_IDS=[群ID1,群ID2]`
5. **触发词配置**：每个AI服务都有独立的触发前缀，默认`?ai`使用第一个启用的服务
6. **AI Prompt配置**：支持自动添加prompt前缀，可通过`AI_PROMPT_PREFIX`自定义

### 群消息总结功能详细说明

#### 功能特性
1. **智能提取**: 自动识别群聊中的技术答疑和知识共享内容
2. **主题合并**: 将相同主题的讨论内容合并整理
3. **结构化输出**: 生成标准JSON格式的总结报告
4. **批量处理**: 支持批量总结多天的群消息
5. **历史查看**: 可随时查看已生成的总结结果
6. **静默处理**: 总结过程不会向群内发送消息，仅记录到日志

#### 使用示例
```
?ai_daySum               # 总结今天的消息（静默处理，仅记录日志）
?ai_daySum 20250925      # 总结指定日期的消息（YYYYMMDD格式）
?ai_daySum 今天          # 总结今天的消息
?ai_daySum 昨天          # 总结昨天的消息
群总结                    # 总结昨天的消息（静默处理，仅记录日志）
群总结 2024-01-15        # 总结指定日期的消息
群总结 今天              # 总结今天的消息
批量总结 7               # 批量总结最近7天的消息（静默处理，仅记录日志）
查看总结 2024-01-15      # 查看指定日期的总结结果（静默处理，仅记录日志）
```

**注意**: 所有群消息总结相关命令现在都采用静默处理模式，不会向群内发送任何消息，所有处理结果和状态信息都会记录到日志文件中。

#### 数据存储
- **原始记录**: `./data/history/{群ID}-{日期}.json`
- **总结结果**: `./data/daySummary/{群ID}-{日期}-summary.json`

### 免审权限管理功能详细说明

#### 功能特性
1. **权限验证**: 仅群管理员可执行免审权限操作
2. **智能UID提取**: 支持从消息内容和群昵称中自动提取用户ID
3. **多Wiki支持**: 可扩展支持多个Wiki站点的权限管理
4. **多用户组支持**: 支持同时添加多个用户组到同一用户
5. **灵活时间配置**: 支持月末权限（curMonth）和永久权限（ever）两种模式
6. **智能回复**: 添加成功后引用用户消息并回复详细信息
7. **表情反馈**: 使用表情符号快速反馈操作结果
8. **安全认证**: 支持使用sessdata进行MediaWiki API认证

#### 使用示例
```
?lysk免审 2342354                    # 为UID 2342354 添加恋与深空WIKI免审权限
?lysk免审                            # 从发送者的群昵称中提取UID并添加权限
?lysk管理 1234567                    # 为UID 1234567 添加管理权限（多个用户组）
?lyskbili 9876543                    # 为UID 9876543 添加bilibili权限（永久）
```

#### 操作流程
1. **权限检查**: 验证发送者是否为群管理员（根据配置决定）
2. **UID提取**: 从消息内容或群昵称中提取用户ID
3. **时间计算**: 根据addTime配置计算权限到期时间
4. **多组添加**: 循环添加配置中的所有用户组
5. **结果反馈**: 使用表情符号反馈操作结果，并引用回复详细信息

#### 配置要求
1. **环境变量**: 在`.env`文件中配置`WIKI_SESSDATA`用于API认证
2. **权限配置**: 在`config.py`中配置免审关键字和对应的用户组
3. **群管理员权限**: 根据配置决定是否需要群管理员权限

#### 配置示例
```python
# config.py 中的免审权限配置
EXEMPTION_CONFIGS = {
    "?lysk免审": {
        "addgroup": ["automoderated"],    # 要添加的用户组（支持数组）
        "wiki": "lysk",                  # 对应的wiki站点
        "checkPermission": False,         # 是否需要权限验证
        "addTime": "curMonth"            # 权限时间类型：curMonth(月末) 或 ever(永久)
    },
    "?lysk管理": {
        "addgroup": ["interface-admin", "sysop"],  # 多个用户组
        "wiki": "lysk",
        "checkPermission": True,          # 需要管理员权限
        "addTime": "curMonth"
    },
    "?lyskbili": {
        "addgroup": ["bilibili"],
        "wiki": "lysk",
        "checkPermission": False,
        "addTime": "ever"                # 永久权限
    }
}

# 权限时间提示语配置
ADD_TIME_SLOGAN = {
    "curMonth": "本月权限新添就，感君劳苦付春秋。",
    "ever": "一纸权限伴久长，百科万象任徜徉。"
}

# .env 文件中的认证配置
WIKI_SESSDATA=your_sessdata_here
```

#### 总结格式
```json
[
  {
    "name": "讨论主题名称",
    "方案": [
      "具体方案1",
      "具体方案2"
    ]
  }
]
```

### 详细文档
- `AI_SUMMARY_PROJECT_OVERVIEW.md` - 完整项目概览和技术细节
- `docs/ai_usage.md` - 用户使用指南
- `CORE_ISSUES_ANALYSIS.md` - 当前问题分析
3. **环境变量**：在`.env`文件中配置AI相关参数

### 配置示例

#### AI服务配置（新版结构化配置）

系统现在使用统一的字典结构管理多个AI服务，配置更加灵活和可扩展：

```bash
# AI功能基础配置
AI_TRIGGER_PREFIX=?ai                    # AI对话触发词（使用第一个启用的服务）
AI_DAY_SUMMARY_PREFIX=?ai_daySum         # 日总结触发词
AI_PROMPT_PREFIX=请不要使用markdown语法，回复token控制在2000以内。用户问题：
AI_SUMMARY_MAX_TOKENS=2000              # AI回复最大token数
AI_SUMMARY_TIMEOUT=30                   # AI请求超时时间（秒）

# LongCat AI服务配置
LONGCAT_API_KEY=your_longcat_api_key_here
LONGCAT_ENABLED=true                     # 手动启用LongCat AI（触发词：?lc）

# 火山引擎AI服务配置  
ARK_API_KEY=your_volc_api_key_here
VOLC_ENABLED=true                        # 手动启用火山引擎AI（触发词：?volc）

# 智谱AI GLM服务配置
GLM_API_KEY=your_glm_api_key_here
GLM_ENABLED=true                         # 手动启用智谱AI（触发词：?glm）

# 未来可以添加更多AI服务，如：
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_ENABLED=true
# CLAUDE_API_KEY=your_claude_api_key_here
# CLAUDE_ENABLED=true
```

#### 配置特性

1. **手动启用**：每个AI服务需要通过对应的`_ENABLED`环境变量手动启用
2. **独立触发**：每个AI服务都有独立的触发前缀（如`?lc`、`?volc`、`?glm`）
3. **智能回退**：`?ai`命令使用第一个启用的AI服务，如果该服务未开放则提示用户
4. **易于扩展**：添加新AI服务只需在配置中添加相应字段
5. **灵活控制**：可以根据需要启用或禁用特定的AI服务

### 快速启动

```bash
# 1. 启动机器人（推荐）
python main.py

# 2. 或使用脚本启动（包含环境检查）
./scripts/start.sh

# 3. 检查环境
python check_env.py
```

### 安装步骤
1. **确保虚拟环境已创建**：运行 `./scripts/install.sh`
2. **安装AI依赖**：运行 `./scripts/install_ai_deps.sh`
3. **配置AI密钥**：复制 `config/env.example` 为 `.env` 并添加上述配置
4. **测试功能**：运行 `python check_env.py`
5. **启动机器人**：运行 `python main.py`

## 安全建议
1. **修改默认端口**：将8080改为其他端口
2. **设置访问令牌**：在配置文件中设置AccessToken
3. **保护AI密钥**：妥善保管火山引擎AI的ACCESS_KEY和SECRET_KEY
4. **定期更新**：保持系统和依赖包更新
5. **备份配置**：定期备份配置文件和数据库
6. **权限管理**：确保文件权限正确，避免权限问题
