# Ubuntu 云服务器部署指南

## 服务器配置要求

### 推荐配置
- **CPU**: 2核
- **内存**: 2GB
- **硬盘**: 20GB+ SSD
- **带宽**: 3Mbps+
- **系统**: Ubuntu Server 18.04.1 LTS

### 最低配置
- **CPU**: 1核
- **内存**: 1GB
- **硬盘**: 10GB
- **带宽**: 1Mbps

## 部署步骤

### 1. 服务器初始化

```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y curl wget git vim unzip
```

### 2. 安装 Python 3.8+

```bash
# 添加 deadsnakes PPA
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# 安装 Python 3.8
sudo apt install -y python3.8 python3.8-venv python3.8-dev python3-pip

# 设置 Python 3.8 为默认版本
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

# 验证安装
python3 --version
pip3 --version
```

### 3. 下载 Lagrange.OneBot Linux 版本

```bash
# 创建应用目录
sudo mkdir -p /opt/lagrange-onebot
cd /opt/lagrange-onebot

# 下载最新版本 (请替换为实际的最新版本号)
wget https://github.com/LagrangeDev/Lagrange.Core/releases/download/v1.0.0/Lagrange.OneBot-linux-x64.zip

# 解压
unzip Lagrange.OneBot-linux-x64.zip

# 设置权限
sudo chmod +x Lagrange.OneBot
sudo chown -R $USER:$USER /opt/lagrange-onebot
```

### 4. 配置 Lagrange.OneBot

根据 [Lagrange 官方文档](https://lagrangedev.github.io/Lagrange.Doc/v1/Lagrange.OneBot/Config/)，创建正确的配置文件：

```bash
# 创建配置文件
cat > /opt/lagrange-onebot/appsettings.json << 'EOF'
{
    "$schema": "https://raw.githubusercontent.com/LagrangeDev/Lagrange.Core/master/Lagrange.OneBot/Resources/appsettings_schema.json",
    "Logging": {
        "LogLevel": {
            "Default": "Information"
        }
    },
    "SignServerUrl": "https://sign.lagrangecore.org/api/sign/30366",
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
        "ConsoleCompatibilityMode": true
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
EOF
```

**重要配置说明**：
- `SignServerUrl`: 必须设置为官方签名服务器
- `ConsoleCompatibilityMode`: 服务器部署设置为 `true`
- `HeartBeatEnable`: 必须设置为 `true`
- `Host`: 使用 `127.0.0.1` 而非 `0.0.0.0`（安全考虑）

### 5. 部署 Python 机器人

```bash
# 创建机器人目录
sudo mkdir -p /opt/qq-bot
cd /opt/qq-bot

# 克隆或上传机器人代码
# 方法1: 如果代码在 Git 仓库
# git clone <your-repo-url> .

# 方法2: 使用 scp 上传本地代码
# scp -r /path/to/local/bot user@server:/opt/qq-bot/

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 6. 配置环境变量

```bash
# 创建环境变量文件
cat > /opt/qq-bot/.env << 'EOF'
# Onebot 连接配置
ONEBOT_WS_URL=ws://127.0.0.1:8080/onebot/v11/ws
ONEBOT_HTTP_URL=http://127.0.0.1:8080

# 机器人配置
BOT_NAME=QQ机器人
BOT_MASTER_ID=0

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/opt/qq-bot/bot.log

# 短链服务配置
SHORTLINK_TIMEOUT=2
SHORTLINK_RETRY=1
EOF
```

### 7. 创建系统服务

#### Lagrange.OneBot 服务

```bash
sudo tee /etc/systemd/system/lagrange-onebot.service > /dev/null << 'EOF'
[Unit]
Description=Lagrange.OneBot Service
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/lagrange-onebot
ExecStart=/opt/lagrange-onebot/Lagrange.OneBot
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=lagrange-onebot

[Install]
WantedBy=multi-user.target
EOF
```

#### Python 机器人服务

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
WorkingDirectory=/opt/qq-bot
Environment=PATH=/opt/qq-bot/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=/opt/qq-bot/venv/bin/python start.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=qq-bot

[Install]
WantedBy=multi-user.target
EOF
```

### 8. 启动服务

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启动 Lagrange.OneBot
sudo systemctl enable lagrange-onebot
sudo systemctl start lagrange-onebot

# 启动 QQ 机器人
sudo systemctl enable qq-bot
sudo systemctl start qq-bot

# 检查服务状态
sudo systemctl status lagrange-onebot
sudo systemctl status qq-bot
```

### 9. 配置防火墙

```bash
# 开放必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 8080  # OneBot WebSocket
sudo ufw enable
```

## 管理命令

### 查看日志
```bash
# Lagrange.OneBot 日志
sudo journalctl -u lagrange-onebot -f

# QQ 机器人日志
sudo journalctl -u qq-bot -f

# 机器人应用日志
tail -f /opt/qq-bot/bot.log
```

### 重启服务
```bash
# 重启 Lagrange.OneBot
sudo systemctl restart lagrange-onebot

# 重启 QQ 机器人
sudo systemctl restart qq-bot
```

### 停止服务
```bash
# 停止服务
sudo systemctl stop lagrange-onebot
sudo systemctl stop qq-bot

# 禁用自启动
sudo systemctl disable lagrange-onebot
sudo systemctl disable qq-bot
```

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   sudo netstat -tlnp | grep 8080
   sudo lsof -i :8080
   ```

2. **权限问题**
   ```bash
   sudo chown -R $USER:$USER /opt/lagrange-onebot
   sudo chown -R $USER:$USER /opt/qq-bot
   ```

3. **VSCode 无法写入文件权限问题**
   
   **问题现象**：在 VSCode 中编辑 `/opt/` 目录下的文件时，出现 "permission denied" 错误提示。
   
   **原因分析**：文件属于 `root` 用户，而 VSCode 以普通用户身份运行。
   
   **解决方案**：
   ```bash
   # 方案1：修改文件所有者（推荐）
   sudo chown $USER:$USER /opt/lagrange-onebot/appsettings.json
   sudo chown $USER:$USER /opt/qq-bot/.env
   
   # 方案2：修改整个目录的所有者
   sudo chown -R $USER:$USER /opt/lagrange-onebot
   sudo chown -R $USER:$USER /opt/qq-bot
   
   # 方案3：临时使用 sudo 权限编辑（不推荐）
   sudo code /opt/lagrange-onebot/appsettings.json
   ```
   
   **验证修复**：
   ```bash
   # 检查文件权限
   ls -la /opt/lagrange-onebot/appsettings.json
   ls -la /opt/qq-bot/.env
   
   # 应该显示当前用户为所有者
   # -rw-r--r-- 1 ubuntu ubuntu 981 Sep 17 19:39 /opt/lagrange-onebot/appsettings.json
   ```

4. **Python 依赖问题**
   ```bash
   cd /opt/qq-bot
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### 调试模式

如果需要调试，可以手动运行：

```bash
# 手动运行 Lagrange.OneBot
cd /opt/lagrange-onebot
./Lagrange.OneBot

# 手动运行机器人
cd /opt/qq-bot
source venv/bin/activate
python start.py
```

## 安全建议

1. **修改默认端口**：将 8080 改为其他端口
2. **设置访问令牌**：在配置文件中设置 AccessToken
3. **定期更新**：保持系统和依赖包更新
4. **备份配置**：定期备份配置文件和数据库

## 性能优化

1. **调整日志级别**：生产环境使用 WARNING 或 ERROR
2. **限制日志大小**：配置日志轮转
3. **监控资源使用**：使用 htop 或 top 监控
4. **优化网络**：根据实际使用调整心跳间隔
