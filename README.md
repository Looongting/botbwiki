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
botbwiki/                       # 机器人项目目录
├── README.md                   # 项目说明文档
├── pyproject.toml             # 项目配置文件
├── requirements.txt           # Python依赖包
├── .env                       # 环境变量配置（需要创建）
├── .env.example               # 环境变量示例
├── .gitignore                 # Git忽略文件
├── start.py                   # 机器人启动脚本
├── bot.py                     # 机器人主程序
├── config.py                  # 配置文件
├── check_env.py               # 环境检查脚本
├── verify_config.py           # 配置验证脚本
├── lagrange-config-template.json # Lagrange配置模板
├── activate.sh                # Linux 环境激活脚本
├── start.sh                   # Linux 一键启动脚本
├── install.sh                 # Linux 一键安装脚本
├── plugins/                   # 插件目录
│   ├── __init__.py
│   ├── shortlink.py           # 多Wiki站点短链生成插件
│   └── random.py              # 随机数生成插件
├── docs/                      # 文档目录
│   └── ubuntu-deployment.md   # Ubuntu云服务器部署指南
├── scripts/                   # 部署脚本目录
│   ├── install-ubuntu.sh      # Ubuntu一键部署脚本
│   └── fix-permissions.sh     # 权限修复脚本
├── systemd-service-templates/ # 系统服务模板目录
│   ├── lagrange-onebot.service # Lagrange.OneBot服务模板
│   └── qq-bot.service         # QQ机器人服务模板
└── venv/                      # Python虚拟环境

/opt/lagrange/                 # Lagrange.OneBot 安装目录
├── Lagrange.OneBot            # 可执行文件
├── appsettings.json           # 配置文件
├── device.json                # 设备信息
├── keystore.json              # 登录凭据
├── lagrange-0-db/             # 数据库目录
└── qr-0.png                   # 二维码文件（登录时生成）

/etc/systemd/system/           # 系统服务配置
├── lagrange-onebot.service    # Lagrange.OneBot 系统服务
└── qq-bot.service             # QQ机器人系统服务
```

## 快速开始

### 1. 环境准备

- Python 3.8 或更高版本
- **QQ 机器人本体**（需要单独安装）：
  - [LagrangeCore](https://github.com/ClosureMk/LagrangeCore/releases)（推荐）
  - [go-cqhttp](https://github.com/Mrs4s/go-cqhttp/releases)
  - 或其他 Onebot 实现
- 网络连接（用于短链生成）
- **下载加速工具**（可选但推荐）：
  - [Xget](https://github.com/xixu-me/Xget) - 超高性能的开发者资源访问加速引擎，特别适合下载大型文件

### 部署方式选择

#### 本地部署（Linux）
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

#### 权限问题修复

如果在部署过程中遇到权限问题，可以使用权限修复脚本：

```bash
# 修复所有权限问题
bash scripts/fix-permissions.sh

# 仅查看当前权限状态
bash scripts/fix-permissions.sh --show
```

### 2. 创建虚拟环境并安装依赖

#### 方法一：一键安装（推荐）

```bash
# 克隆项目（如果从 Git 获取）
git clone <repository-url>
cd botbwiki

# 运行一键安装脚本
./install.sh
```

#### 方法二：手动安装

```bash
# 克隆项目（如果从 Git 获取）
git clone <repository-url>
cd botbwiki

# 创建 Python 虚拟环境
python3 -m venv venv

# 激活虚拟环境（必须使用 source 命令）
source venv/bin/activate

# 升级 pip
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

#### 快速启动脚本

项目提供了便捷的 Linux 脚本：

- **一键启动**: `./start.sh` - 自动激活环境并启动机器人
- **环境激活**: `source ./activate.sh` - 激活虚拟环境（必须使用 source 命令）
- **一键安装**: `./install.sh` - 自动安装所有依赖

**重要提醒**：激活虚拟环境时必须使用 `source ./activate.sh` 或 `. ./activate.sh`，直接运行 `./activate.sh` 无法在当前shell中激活虚拟环境。

### 3. 配置环境

```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑 .env 文件，配置相关参数
# 主要需要配置 Onebot 连接地址
```

### 4. 启动机器人

#### 方式一：使用一键启动脚本（推荐）
```bash
./start.sh
```

#### 方式二：使用启动脚本
```bash
python start.py
```

#### 方式三：直接启动
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

#### 使用 Lagrange.OneBot（推荐）

1. **下载和安装**：
   ```bash
   # 下载 Lagrange.OneBot 到 /opt 目录
   cd /opt
   wget "https://xget.xi-xu.me/gh/LagrangeDev/Lagrange.Core/releases/download/nightly/Lagrange.OneBot_linux-x64_net9.0_SelfContained.tar.gz"
   
   # 解压到 lagrange 目录
   tar -xzf Lagrange.OneBot_linux-x64_net9.0_SelfContained.tar.gz -C lagrange
   cd lagrange
   
   # 设置执行权限
   chmod +x Lagrange.OneBot
   ```

2. **首次配置和登录**：
   ```bash
   # 首次启动会生成配置文件appsettings.json
   # 然后中止进程，先去修改appsettings.json
   # 修改配置后，再次启动，需要扫码登录
   cd /opt/lagrange
   ./Lagrange.OneBot
   
   # 看到二维码后，用手机QQ扫描登录
   # 登录成功后按 Ctrl+C 停止程序
   ```

3. **关键配置说明**：
   
   **appsettings.json 配置**：
   ```json
   {
     "SignServerUrl": "https://sign.lagrangecore.org/api/sign/39038",
     "Account": {
       "Uin": 0,  // 登录后会自动设置为您的QQ号
       "Protocol": "Linux",
       "AutoReconnect": true,
       "GetOptimumServer": true
     },
     "QrCode": {
       "ConsoleCompatibilityMode": false  // 云服务器建议设为 true
     },
     "Implementations": [
       {
         "Type": "ForwardWebSocket",
         "Host": "127.0.0.1",
         "Port": 8080,  // 重要：这是 Lagrange 提供的 WebSocket 服务端口
         "Suffix": "/onebot/v11/ws",
         "ReconnectInterval": 5000,
         "HeartBeatInterval": 5000,
         "HeartBeatEnable": true
       }
     ]
   }
   ```

4. **端口配置说明**：
   
   **正确的架构**：
   - **Lagrange.OneBot**：作为 QQ 客户端，在 8080 端口提供 WebSocket 服务
   - **QQ机器人（NoneBot）**：作为 WebSocket 客户端，连接到 Lagrange 的 8080 端口
   
   **环境变量配置**（.env 文件）：
   ```bash
   # Onebot 连接配置 - 连接到 Lagrange 的 WebSocket 服务
   ONEBOT_WS_URL=ws://127.0.0.1:8080/onebot/v11/ws
   ONEBOT_HTTP_URL=http://127.0.0.1:8080
   
   # Nonebot2 服务器配置 - 机器人自己的 HTTP 服务端口（避免冲突）
   HOST=127.0.0.1
   PORT=8081  # 注意：这里不能是 8080，避免与 Lagrange 冲突
   ```

5. **常见问题解决**：
   
   **问题1：端口冲突**
   - 症状：Lagrange 启动失败或机器人无法连接
   - 解决：确保 Lagrange 使用 8080 端口，机器人使用 8081 端口
   
   **问题2：登录失败**
   - 症状：显示 "All login failed!" 错误
   - 解决：检查 `Account.Uin` 是否正确设置，或重新扫码登录
   
   **问题3：WebSocket 连接失败**
   - 症状：Lagrange 显示 "Reconnecting" 循环
   - 解决：确保机器人服务已启动，且配置的 WebSocket URL 正确

详细部署与配置请参阅 `docs/ubuntu-deployment.md`。

### 7. 系统服务配置（推荐）

为了确保机器人可以持续运行，不受远程连接影响，建议配置为系统服务：

1. **创建 systemd 服务文件**：
   ```bash
   # Lagrange.OneBot 服务
   sudo tee /etc/systemd/system/lagrange-onebot.service > /dev/null << 'EOF'
   [Unit]
   Description=Lagrange.OneBot Service
   After=network.target
   Wants=network-online.target

   [Service]
   Type=simple
   User=ubuntu
   Group=ubuntu
   WorkingDirectory=/opt/lagrange
   ExecStart=/opt/lagrange/Lagrange.OneBot
   Restart=always
   RestartSec=10
   StandardOutput=journal
   StandardError=journal
   SyslogIdentifier=lagrange-onebot

   # 环境变量
   Environment=DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1
   Environment=DOTNET_BUNDLE_EXTRACT_BASE_DIR=/tmp/lagrange-extract

   # 安全设置
   NoNewPrivileges=false
   ProtectSystem=false
   ProtectHome=false

   # 资源限制
   MemoryMax=512M
   TasksMax=100

   [Install]
   WantedBy=multi-user.target
   EOF
   ```

2. **QQ机器人服务**：
   ```bash
   # QQ机器人服务
   sudo tee /etc/systemd/system/qq-bot.service > /dev/null << 'EOF'
   [Unit]
   Description=QQ Bot Service
   After=network.target lagrange-onebot.service
   Wants=network-online.target
   Requires=lagrange-onebot.service

   [Service]
   Type=simple
   User=ubuntu
   Group=ubuntu
   WorkingDirectory=/home/ubuntu/botbwiki
   Environment=PATH=/home/ubuntu/botbwiki/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
   ExecStart=/bin/bash -c 'cd /home/ubuntu/botbwiki && source venv/bin/activate && python start.py'
   Restart=always
   RestartSec=10
   StandardOutput=journal
   StandardError=journal
   SyslogIdentifier=qq-bot

   # 安全设置
   NoNewPrivileges=false
   ProtectSystem=false
   ProtectHome=false

   # 资源限制
   MemoryMax=256M
   TasksMax=50

   [Install]
   WantedBy=multi-user.target
   EOF
   ```

3. **启用和启动服务**：
   ```bash
   # 重新加载 systemd 配置
   sudo systemctl daemon-reload
   
   # 启用开机自启
   sudo systemctl enable lagrange-onebot.service
   sudo systemctl enable qq-bot.service
   
   # 启动服务
   sudo systemctl start lagrange-onebot.service
   sudo systemctl start qq-bot.service
   
   # 检查服务状态
   sudo systemctl status lagrange-onebot.service
   sudo systemctl status qq-bot.service
   ```

4. **服务管理命令**：
   ```bash
   # 查看服务状态
   sudo systemctl status lagrange-onebot.service
   sudo systemctl status qq-bot.service
   
   # 重启服务
   sudo systemctl restart lagrange-onebot.service
   sudo systemctl restart qq-bot.service
   
   # 停止服务
   sudo systemctl stop lagrange-onebot.service
   sudo systemctl stop qq-bot.service
   
   # 查看服务日志
   sudo journalctl -u lagrange-onebot.service -f
   sudo journalctl -u qq-bot.service -f
   ```

### 8. 验证功能

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

## 项目维护

### 项目清理

项目已进行过全面清理，删除了以下不必要的文件：

- **Python缓存文件**: 清理了 `__pycache__` 目录和 `.pyc` 文件
- **日志文件**: 清理了运行时的日志文件 (`bot.log`, `bot_output.log`)
- **测试脚本**: 删除了过时的测试脚本和临时文件
- **临时文件**: 清理了所有临时文件和备份文件

### 环境检查

项目提供了完整的环境检查工具：

```bash
# 检查Python环境和依赖
python check_env.py

# 验证Lagrange配置
python verify_config.py
```

## 更新日志

- v1.1.8: 完善配置文档和端口说明
  - 详细说明了 Lagrange.OneBot 的配置流程和关键配置项
  - 添加了端口配置说明，明确架构和避免冲突的方法
  - 提供了完整的 systemd 服务配置示例
  - 添加了常见问题的解决方案
  - 更新了项目结构说明，反映清理后的目录布局
  - 提供了详细的服务管理命令
- v1.1.7: 优化目录结构和清理重复文件
  - 清理了/opt目录下的重复Lagrange.OneBot安装
  - 将成功的配置移动到简洁的/opt/lagrange路径
  - 更新了systemd服务配置，使用新的简化路径
  - 删除了不必要的重复目录，节省磁盘空间
  - 保持了所有功能的正常运行
- v1.1.6: 完善systemd服务部署
  - 修复了systemd服务配置中的权限问题
  - 解决了Lagrange.OneBot的DOTNET_BUNDLE_EXTRACT_BASE_DIR环境变量问题
  - 优化了QQ机器人服务的启动方式，使用bash脚本确保虚拟环境正确激活
  - 两个服务现在都可以作为系统服务正常运行，支持开机自启
  - 机器人现在可以持续运行，不受远程连接状态影响
- v1.1.5: 修复虚拟环境激活脚本
  - 修复 `activate.sh` 脚本无法在当前shell中激活虚拟环境的问题
  - 添加执行方式检测，提示用户使用正确的 `source` 命令
  - 更新文档说明，明确激活虚拟环境的正确方式
  - 改进用户体验，避免常见的激活失败问题
- v1.1.4: Linux 兼容性改进
  - 添加 Linux 一键安装脚本 `install.sh`
  - 添加 Linux 一键启动脚本 `start.sh`
  - 添加 Linux 环境激活脚本 `activate.sh`
  - 移除 Windows 专用脚本，全面支持 Linux 环境
  - 更新文档，优化 Linux 部署体验
  - 改进脚本错误处理和用户提示
- v1.1.3: 优化 Lagrange 下载体验
  - 添加 Xget 加速下载支持，解决 Lagrange 文件较大下载缓慢的问题
  - 更新下载说明，使用最新的 nightly 版本和 Xget 加速链接
  - 在环境准备部分添加 Xget 工具介绍，提升用户体验
- v1.1.2: 项目清理和维护
  - 清理了Python缓存文件和临时文件
  - 删除了过时的测试脚本和日志文件
  - 优化了项目结构，保持代码库整洁
  - 更新了项目文档，添加维护说明
- v1.1.1: 完善部署配置和权限管理
  - 更新官方签名服务器地址为 `https://sign.lagrangecore.org/api/sign/30366`
  - 完善 Lagrange 配置模板，确保云服务器部署兼容性
  - 添加权限修复脚本 `scripts/fix-permissions.sh`
  - 改进 systemd 服务配置，使用非特权用户运行
  - 添加系统服务模板文件，便于自定义配置
  - 优化安装脚本的用户权限和安全设置
  - 完善环境变量配置，添加更多可配置项
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
