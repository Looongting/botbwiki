# 从零到一：Ubuntu 云服务器部署（单页）

只需按顺序执行本页步骤，即可在 Ubuntu 上完成部署与验证。默认环境：Ubuntu 20.04/22.04，已具备 sudo 权限与网络。

## 1. 准备环境
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git curl wget unzip
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
./Lagrange.OneBot
```

- 配置文件（权威）：`/opt/lagrange/appsettings.json`
- 需要检查的关键项（只列字段，不贴整段）：
  - Implementations.Type = ForwardWebSocket
  - Host = 127.0.0.1，Port = 8080，Suffix = /onebot/v11/ws
  - HeartBeatEnable = true
- 如需参考模板，请看仓库根：`lagrange-config-template.json`

## 4. 部署机器人（/home/ubuntu/botbwiki）
```bash
cd /home/ubuntu
git clone <your-repo-url> botbwiki
cd botbwiki

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 复制环境变量示例并按需最小修改
cp env.example .env
# 核心：ONEBOT_WS_URL 指向 Lagrange 的 WebSocket 服务
# ONEBOT_WS_URL=ws://127.0.0.1:8080/onebot/v11/ws
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

## 8. 常见问题（最常见的4条）
- 连接不上：确认 `/opt/lagrange/appsettings.json` 为 ForwardWebSocket，`.env` 的 `ONEBOT_WS_URL` 指向 8080
- 不回应：查看机器人日志，确认插件加载成功与指令格式正确
- 二维码问题：将 `ConsoleCompatibilityMode` 设为 true 后重启 Lagrange
- 端口冲突：确认 8080 未被占用（`ss -tlnp | grep 8080`）或改端口后同步更新 `.env`

## 9. 后续
- 配置细节：以实际文件为准 → `/opt/lagrange/appsettings.json`、仓库根 `env.example`
- 更多排错：见 `docs/v2/troubleshooting.md`
