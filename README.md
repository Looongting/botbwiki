# QQ 机器人项目

基于 Nonebot2 框架 + Onebot11 协议 + LagrangeCore 核心的 QQ 机器人，提供短链生成和随机数生成功能。

## 技术栈

- **框架**: Nonebot2
- **协议**: Onebot11
- **核心**: LagrangeCore
- **短链转换**: b23.tv-tools

## 功能特性

### 1. 多Wiki站点短链生成功能
- **触发方式**: 
  - 发送以 `gd` 开头的消息（格式：`gd检索词`）→ 访问恋与深空WIKI
  - 发送以 `m` 开头的消息（格式：`m检索词`）→ 访问米斯特利亚WIKI
- **功能描述**: 基于curid的超快速链接生成，无需第三方短链服务
- **示例**: 
  - 发送 `gd沈星回` → 生成恋与深空WIKI链接
  - 发送 `m瓦伦` → 生成米斯特利亚WIKI链接

### 2. 随机数生成功能
- **触发方式**: 发送 `.rand` 消息
- **功能描述**: 生成 1-100 之间的随机整数
- **示例**: 发送 `.rand` → 返回随机数

## 项目结构

```
bot/
├── README.md                    # 项目说明文档
├── pyproject.toml              # 项目配置文件
├── requirements.txt            # Python依赖包
├── .env.example                # 环境变量示例
├── .gitignore                  # Git忽略文件
├── start.py                    # 机器人启动脚本
├── bot.py                      # 机器人主程序
├── config.py                   # 配置文件
├── check_env.py                # 环境检查脚本
├── verify_config.py            # 配置验证脚本
├── lagrange-config-template.json # Lagrange配置模板
├── plugins/                    # 插件目录
│   ├── __init__.py
│   ├── shortlink.py            # 多Wiki站点短链生成插件
│   └── random.py               # 随机数生成插件
├── docs/                       # 文档目录
│   ├── usage.md                # 使用说明
│   ├── installation.md         # 安装指南
│   ├── quick-start.md          # 快速开始
│   ├── qq-bot-setup.md         # QQ机器人配置
│   ├── lagrange-config-guide.md # Lagrange配置指南
│   ├── ubuntu-deployment.md    # Ubuntu云服务器部署指南
│   └── git-deployment.md       # Git部署指南
├── scripts/                    # 部署脚本目录
│   └── install-ubuntu.sh       # Ubuntu一键部署脚本
└── Lagrange.OneBot/            # OneBot实现（需要单独下载）
    └── bin/Release/net9.0/win-x64/
        └── Lagrange.OneBot.exe
```

## 快速开始

### 1. 环境准备

- Python 3.8 或更高版本
- **QQ 机器人本体**（需要单独安装）：
  - [LagrangeCore](https://github.com/ClosureMk/LagrangeCore/releases)（推荐）
  - [go-cqhttp](https://github.com/Mrs4s/go-cqhttp/releases)
  - 或其他 Onebot 实现
- 网络连接（用于短链生成）

### 部署方式选择

#### 本地部署（Windows）
适合个人使用，配置简单，适合初学者。

#### 云服务器部署（Ubuntu）
适合长期运行，稳定性更好，支持 24/7 运行。

**推荐配置**：
- CPU: 2核
- 内存: 2GB
- 硬盘: 20GB+ SSD
- 带宽: 3Mbps+
- 系统: Ubuntu Server 18.04.1 LTS

详细部署指南请参考：
- [Ubuntu 云服务器部署指南](docs/ubuntu-deployment.md)
- [Git 部署指南](docs/git-deployment.md)

### 2. 创建虚拟环境并安装依赖

```bash
# 克隆项目（如果从 Git 获取）
git clone <repository-url>
cd bot

# 创建 Python 虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows (PowerShell):
venv\Scripts\activate
# Windows (CMD):
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# 升级 pip
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

#### 快速激活脚本

项目提供了便捷的激活脚本：

- **Windows CMD**: 双击 `activate.bat`
- **Windows PowerShell**: 运行 `.\activate.ps1`

### 3. 配置环境

```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑 .env 文件，配置相关参数
# 主要需要配置 Onebot 连接地址
```

### 4. 启动机器人

#### 方式一：使用启动脚本（推荐）
```bash
python start.py
```

#### 方式二：直接启动
```bash
python bot.py
```

### 5. 环境检查

运行环境检查脚本确保一切正常：

```bash
python check_env.py
```

### 6. 配置 QQ 机器人本体

**重要**：您还需要安装 QQ 机器人本体才能与 QQ 群交互。

请参考 [QQ 机器人配置指南](docs/qq-bot-setup.md) 完成以下步骤：
1. 下载并配置 LagrangeCore 或其他 Onebot 实现
2. 启动 Onebot 服务
3. 重新启动您的机器人

### 7. 验证功能

启动成功后，您会看到类似以下的输出：
```
🤖 QQ 机器人启动器
==================================================
🔍 检查运行环境...
✅ Python 版本: 3.12.4
✅ 项目文件完整

📋 当前配置:
   机器人名称: QQ机器人
   Onebot WebSocket URL: ws://127.0.0.1:8080/ws
   Onebot HTTP URL: http://127.0.0.1:8080
   日志级别: INFO
   日志文件: bot.log

🚀 正在启动机器人...
   按 Ctrl+C 停止机器人
==================================================
09-16 22:37:56 [SUCCESS] nonebot | NoneBot is initializing...
09-16 22:37:57 [SUCCESS] nonebot | Succeeded to load plugin "shortlink"
09-16 22:37:57 [SUCCESS] nonebot | Succeeded to load plugin "random"
```

在 QQ 群中测试以下命令：
- 发送 `gd测试` 测试短链生成功能
- 发送 `.rand` 测试随机数生成功能

## 开发说明

### 插件开发

所有功能插件位于 `plugins/` 目录下，每个插件都是独立的模块。

### 错误处理

- 短链生成失败时会返回友好的错误提示
- 随机数生成保证良好的随机性

### 消息监听

机器人仅响应群聊中符合指定格式的指令，不会响应私聊消息。

## 更新日志

- v1.1.0: 添加云服务器部署支持
  - 新增 Ubuntu 云服务器部署指南
  - 提供一键部署脚本 `scripts/install-ubuntu.sh`
  - 支持 systemd 服务管理，实现开机自启
  - 优化了 Linux 环境下的配置和运行
  - 添加了防火墙配置和系统服务管理
  - 支持 Git 部署，实现代码版本控制和自动化部署
  - 提供完整的 Git 部署指南和最佳实践
- v1.0.9: 支持多Wiki站点配置
  - 添加了多Wiki站点支持，通过配置项管理关键字和对应的Wiki URL
  - 支持 `gd` 关键字访问恋与深空WIKI (https://wiki.biligame.com/lysk)
  - 支持 `m` 关键字访问米斯特利亚WIKI (https://wiki.biligame.com/mistria)
  - 实现了智能前缀识别，自动选择对应的Wiki站点
  - 优化了缓存机制，不同Wiki站点的curid分别缓存
  - 可通过配置文件轻松添加更多Wiki站点
- v1.0.8: 实现基于curid的超快速链接生成
  - 添加了 MediaWiki API 集成，直接获取页面的 curid
  - 使用 curid 参数创建直接跳转链接，无需第三方短链服务
  - 实现了 curid 缓存机制，相同页面的 curid 会被缓存
  - 优化了服务优先级：curid方式 > 传统短链服务
  - 响应时间大幅提升，curid方式通常在 0.5 秒内完成
- v1.0.7: 优化短链生成系统
  - 实现了智能缓存机制，相同URL的短链会被缓存1小时
  - 添加了 v.gd、0x0.st 等更多快速可靠的短链服务
  - 优化了服务优先级，使用真正有效的短链服务
  - 移除了无用的本地短链服务，确保所有生成的短链都能正常跳转
  - 总响应时间控制在 3 秒内，缓存命中 < 0.01 秒
- v1.0.6: 平衡短链生成性能和成功率
  - 调整超时时间到合理范围（2-3秒），确保短链服务有足够时间完成
  - 保持快速回退机制，总超时时间控制在 3 秒内
  - 优化了网络连接设置，使用连接池提高效率
  - 平衡了响应速度和成功率，避免过度优化导致服务失败
  - 响应时间控制在 2-3 秒内，成功率显著提升
- v1.0.5: 大幅优化短链生成性能
  - 将超时时间从 5 秒优化到 0.5 秒，总响应时间控制在 1 秒内
  - 实现了快速回退机制，确保即使所有服务失败也能在 1 秒内回复
  - 优化了网络连接设置，使用连接池和更高效的请求配置
  - 添加了总超时控制，防止长时间等待
  - 响应时间从 5+ 秒优化到 1 秒内
- v1.0.4: 更改短链生成触发词
  - 将触发词从 `#` 改为 `gd`，现在使用 `gd检索词` 格式
  - 更新了所有相关文档和错误提示信息
  - 保持了所有其他功能的稳定性
- v1.0.3: 改进短链服务稳定性和错误处理
  - 优化了短链服务优先级，将更可靠的 TinyURL 和 is.gd 服务放在前面
  - 改进了 b23.tv 服务的错误处理，提供更详细的错误信息
  - 识别并处理 b23.tv 服务的连接问题（DNS 解析和网络连接问题）
  - 确保即使 b23.tv 服务不可用，其他服务仍能正常工作
- v1.0.2: 优化短链生成性能和用户体验
  - 修复了生成多个短链的问题，现在只返回第一个成功的短链
  - 优化了短链服务调用策略，使用 `asyncio.as_completed` 实现真正的"最快响应"
  - 减少了超时时间从 10 秒到 5 秒，提升响应速度
  - 简化了消息发送逻辑，避免 `FinishedException` 错误
  - 响应时间从 10+ 秒优化到 4-5 秒
- v1.0.1: 修复短链生成插件的错误处理问题，改进服务稳定性和用户体验
  - 修复了 `FinishedException` 错误导致的机器人无响应问题
  - 改进了短链服务的错误处理和超时设置
  - 添加了更好的回退机制，当短链生成失败时提供原始链接
  - 优化了并行短链服务调用，提高响应速度
- v1.0.0: 初始版本，实现基础短链生成和随机数功能

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目。

## 许可证

MIT License
