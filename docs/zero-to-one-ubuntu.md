# 从零到一：Ubuntu 云服务器部署（单页）

只需按顺序执行本页步骤，即可在 Ubuntu 上完成部署与验证。默认环境：Ubuntu 20.04/22.04，已具备 sudo 权限与网络。

## 服务器配置要求

### 推荐配置
- **CPU**: 2核
- **内存**: 2GB
- **硬盘**: 20GB+ SSD
- **带宽**: 3Mbps+
- **系统**: Ubuntu Server 18.04.1 LTS 或更高版本

### 最低配置
- **CPU**: 1核
- **内存**: 1GB
- **硬盘**: 10GB
- **带宽**: 1Mbps

## 1. 准备环境
```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y python3 python3-venv python3-pip python3-dev git curl wget unzip vim

# 安装 Python 3.8+（如果系统版本较低）
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.8 python3.8-venv python3.8-dev

# 设置 Python 3.8 为默认版本（可选）
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

# 验证安装
python3 --version
pip3 --version
```

## 2. 一分钟架构（先给结论）
- Lagrange.OneBot：在本机 8080 提供 OneBot v11 WebSocket 服务（`ws://127.0.0.1:8080/onebot/v11/ws`）
- 机器人（NoneBot2）：作为 WebSocket 客户端连接上面地址即可工作
- 仅监听 127.0.0.1，避免暴露公网；HTTP 8081 可选（调试/健康检查）

## 3. 安装 Lagrange.OneBot（/opt/lagrange）
```bash
cd /opt
sudo mkdir -p lagrange

# 使用 xget 加速下载自包含包（云上推荐）
wget "https://xget.xi-xu.me/gh/LagrangeDev/Lagrange.Core/releases/download/nightly/Lagrange.OneBot_linux-x64_net9.0_SelfContained.tar.gz"

# 解压到 /opt/lagrange 目录
tar -xzf Lagrange.OneBot_linux-x64_net9.0_SelfContained.tar.gz -C lagrange
sudo chown -R $USER:$USER /opt/lagrange
sudo chmod +x /opt/lagrange/Lagrange.OneBot

# 首次启动一次生成 appsettings.json，然后 Ctrl+C 退出
cd /opt/lagrange
timeout 5s ./Lagrange.OneBot
```

### 3.1 配置 Lagrange.OneBot

**重要说明**：Lagrange.OneBot 需要先启动一次来生成默认配置文件，然后使用项目提供的配置模板进行更新。

```bash
# 使用项目提供的配置模板更新 appsettings.json
# 主要需要更新的配置项：

# 1. 设置官方签名服务器
sed -i 's/"SignServerUrl": ""/"SignServerUrl": "https:\/\/sign.lagrangecore.org\/api\/sign\/39038"/' appsettings.json

# 2. 启用控制台兼容模式（云服务器部署必需）
sed -i 's/"ConsoleCompatibilityMode": false/"ConsoleCompatibilityMode": true/' appsettings.json

# 3. 启用心跳检测
sed -i '/"HeartBeatInterval": 5000,/a\            "HeartBeatEnable": true,' appsettings.json
```

**重要配置说明**：
- `SignServerUrl`: 必须设置为官方签名服务器 `https://sign.lagrangecore.org/api/sign/39038`
- `ConsoleCompatibilityMode`: 云服务器部署默认设置为 `false`，当二维码无法正常显示再改为true的兼容模式
- `HeartBeatEnable`: 必须设置为 `true` 保持连接稳定
- `Host`: 使用 `127.0.0.1` 而非 `0.0.0.0`（安全考虑）

### 3.2 验证配置
```bash
# 使用项目提供的配置验证脚本
cd /home/ubuntu/botbwiki
python3 verify_config.py
```

- 配置文件（权威）：`/opt/lagrange/appsettings.json`
- 需要检查的关键项：
  - Implementations.Type = ForwardWebSocket
  - Host = 127.0.0.1，Port = 8080，Suffix = /onebot/v11/ws
  - HeartBeatEnable = true
- 如需参考模板，请看仓库根：`lagrange-config-template.json`

## 4. 部署机器人（/home/ubuntu/botbwiki）

**重要提醒：所有Python相关操作都必须在虚拟环境中进行，避免污染系统环境！**

```bash
# 创建机器人目录
cd /home/ubuntu
git clone <your-repo-url> botbwiki
cd botbwiki

# 创建虚拟环境（必须！）
python3 -m venv venv

# 激活虚拟环境（必须！）
source venv/bin/activate

# 验证虚拟环境（应该显示虚拟环境路径）
which python
which pip

# 安装依赖（在虚拟环境中）
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.1 配置环境变量

```bash
# 复制环境变量示例并按需最小修改
cp env.example .env
# 核心：ONEBOT_WS_URL 指向 Lagrange 的 WebSocket 服务
# ONEBOT_WS_URL=ws://127.0.0.1:8080/onebot/v11/ws

# 编辑环境变量文件
cat > .env << 'EOF'
# Onebot 连接配置
ONEBOT_WS_URL=ws://127.0.0.1:8080/onebot/v11/ws
ONEBOT_HTTP_URL=http://127.0.0.1:8080

# 机器人配置
BOT_NAME=QQ机器人
BOT_MASTER_ID=0

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/home/ubuntu/botbwiki/bot.log

# 短链服务配置
SHORTLINK_TIMEOUT=2
SHORTLINK_RETRY=1
EOF
```

> 说明：配置详情以仓库根 `env.example` 为准；仅在 `.env` 中修改你需要的最少项。

## 5. 先跑起来（前台验证）
```bash
python start.py
```
成功信号：
- 日志出现 NoneBot 初始化完成与插件加载成功
- 日志出现 `Bot <QQ号> connected`（连接 Lagrange 成功）

Ctrl+C 停止后继续下一步。

## 6. 服务化（systemd）
创建 Lagrange.OneBot 服务：
```bash
sudo tee /etc/systemd/system/lagrange-onebot.service > /dev/null << 'EOF'
[Unit]
Description=Lagrange.OneBot Service
After=network.target

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

[Install]
WantedBy=multi-user.target
EOF
```

创建机器人服务（统一使用 /home/ubuntu/botbwiki，删除 /opt/qq-bot 相关残留）：
```bash
sudo tee /etc/systemd/system/qq-bot.service > /dev/null << 'EOF'
[Unit]
Description=QQ Bot Service
After=network.target lagrange-onebot.service
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

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable lagrange-onebot qq-bot
sudo systemctl start lagrange-onebot qq-bot
```

## 7. 验证（打勾清单）
```bash
sudo systemctl status lagrange-onebot | cat
sudo systemctl status qq-bot | cat
sudo journalctl -u lagrange-onebot -f
sudo journalctl -u qq-bot -f
```
- [ ] 两个服务 Active: active (running)
- [ ] Lagrange 日志出现 Connect(...)
- [ ] 机器人日志出现 `Bot <QQ号> connected`

QQ群内测试：
- `gd检索词`、`m检索词`
- `.rand`

## 8. 配置防火墙
```bash
# 开放必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 8080  # OneBot WebSocket
sudo ufw enable
```

## 9. 常见问题（最常见的4条）
- **连接不上**：确认 `/opt/lagrange/appsettings.json` 为 ForwardWebSocket，`.env` 的 `ONEBOT_WS_URL` 指向 8080
- **不回应**：查看机器人日志，确认插件加载成功与指令格式正确
- **二维码问题**：将 `ConsoleCompatibilityMode` 设为 true 后重启 Lagrange
- **端口冲突**：确认 8080 未被占用（`ss -tlnp | grep 8080`）或改端口后同步更新 `.env`

### 9.1 权限问题
**问题现象**：在 VSCode 中编辑 `/opt/` 目录下的文件时，出现 "permission denied" 错误提示。

**原因分析**：文件属于 `root` 用户，而 VSCode 以普通用户身份运行。

**解决方案**：
```bash
# 方案1：修改文件所有者（推荐）
sudo chown $USER:$USER /opt/lagrange/appsettings.json
sudo chown $USER:$USER /home/ubuntu/botbwiki/.env

# 方案2：修改整个目录的所有者
sudo chown -R $USER:$USER /opt/lagrange
sudo chown -R $USER:$USER /home/ubuntu/botbwiki

# 验证修复
ls -la /opt/lagrange/appsettings.json
ls -la /home/ubuntu/botbwiki/.env
```

### 9.2 Python 依赖问题
```bash
cd /home/ubuntu/botbwiki
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 9.3 调试模式
如果需要调试，可以手动运行：
```bash
# 手动运行 Lagrange.OneBot
cd /opt/lagrange
./Lagrange.OneBot

# 手动运行机器人
cd /home/ubuntu/botbwiki
source venv/bin/activate
python start.py
```

## 10. 后续
- **配置细节**：以实际文件为准 → `/opt/lagrange/appsettings.json`、仓库根 `env.example`
- **更多排错**：见 `docs/v2/troubleshooting.md`
- **性能优化**：
  - 调整日志级别：生产环境使用 WARNING 或 ERROR
  - 限制日志大小：配置日志轮转
  - 监控资源使用：使用 htop 或 top 监控
  - 优化网络：根据实际使用调整心跳间隔
