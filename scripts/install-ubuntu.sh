#!/bin/bash
# Ubuntu 云服务器一键部署脚本
# 用于自动安装和配置 QQ 机器人环境

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为 root 用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用 root 用户运行此脚本"
        exit 1
    fi
}

# 检查系统版本
check_system() {
    log_info "检查系统版本..."
    
    if ! command -v lsb_release &> /dev/null; then
        sudo apt update
        sudo apt install -y lsb-release
    fi
    
    OS_VERSION=$(lsb_release -rs)
    OS_NAME=$(lsb_release -is)
    
    log_info "检测到系统: $OS_NAME $OS_VERSION"
    
    if [[ "$OS_NAME" != "Ubuntu" ]]; then
        log_error "此脚本仅支持 Ubuntu 系统"
        exit 1
    fi
}

# 更新系统
update_system() {
    log_info "更新系统包..."
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y curl wget git vim unzip software-properties-common
    log_success "系统更新完成"
}

# 安装 Python 3.8
install_python() {
    log_info "安装 Python 3.8..."
    
    # 添加 deadsnakes PPA
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    
    # 安装 Python 3.8
    sudo apt install -y python3.8 python3.8-venv python3.8-dev python3-pip
    
    # 设置 Python 3.8 为默认版本
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1
    
    # 验证安装
    PYTHON_VERSION=$(python3 --version)
    log_success "Python 安装完成: $PYTHON_VERSION"
}

# 下载 Lagrange.OneBot
download_lagrange() {
    log_info "下载 Lagrange.OneBot Linux 版本..."
    
    # 创建目录
    sudo mkdir -p /opt/lagrange-onebot
    cd /opt/lagrange-onebot
    
    # 获取最新版本号 (这里需要手动更新或使用 API)
    LAGRANGE_VERSION="1.0.0"  # 请替换为实际的最新版本
    
    # 下载文件
    DOWNLOAD_URL="https://github.com/LagrangeDev/Lagrange.Core/releases/download/v${LAGRANGE_VERSION}/Lagrange.OneBot-linux-x64.zip"
    
    log_info "正在下载: $DOWNLOAD_URL"
    wget -O lagrange.zip "$DOWNLOAD_URL"
    
    # 解压
    unzip lagrange.zip
    rm lagrange.zip
    
    # 设置权限
    sudo chmod +x Lagrange.OneBot
    sudo chown -R $USER:$USER /opt/lagrange-onebot
    
    log_success "Lagrange.OneBot 下载完成"
}

# 配置 Lagrange.OneBot
configure_lagrange() {
    log_info "配置 Lagrange.OneBot..."
    
    cat > /opt/lagrange-onebot/appsettings.json << 'EOF'
{
  "$schema": "https://raw.githubusercontent.com/LagrangeDev/Lagrange.Core/master/Lagrange.OneBot/Resources/appsettings_schema.json",
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  },
  "SignServerUrl": "https://sign.lagrangecore.org/api/sign",
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
      "Host": "0.0.0.0",
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
    
    log_success "Lagrange.OneBot 配置完成"
}

# 部署 Python 机器人
deploy_bot() {
    log_info "部署 Python 机器人..."
    
    # 创建目录
    sudo mkdir -p /opt/qq-bot
    cd /opt/qq-bot
    
    # 创建虚拟环境
    python3 -m venv venv
    source venv/bin/activate
    
    # 升级 pip
    pip install --upgrade pip
    
    log_success "Python 机器人环境准备完成"
    log_warning "请手动上传机器人代码到 /opt/qq-bot/ 目录"
    log_warning "然后运行: pip install -r requirements.txt"
}

# 创建环境变量文件
create_env_file() {
    log_info "创建环境变量文件..."
    
    cat > /opt/qq-bot/.env << 'EOF'
# Onebot 连接配置
ONEBOT_WS_URL=ws://127.0.0.1:8080/onebot/v11/ws
ONEBOT_HTTP_URL=http://127.0.0.0:8080

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
    
    log_success "环境变量文件创建完成"
}

# 创建系统服务
create_systemd_services() {
    log_info "创建系统服务..."
    
    # Lagrange.OneBot 服务
    sudo tee /etc/systemd/system/lagrange-onebot.service > /dev/null << 'EOF'
[Unit]
Description=Lagrange.OneBot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/lagrange-onebot
ExecStart=/opt/lagrange-onebot/Lagrange.OneBot
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Python 机器人服务
    sudo tee /etc/systemd/system/qq-bot.service > /dev/null << 'EOF'
[Unit]
Description=QQ Bot Service
After=network.target lagrange-onebot.service
Requires=lagrange-onebot.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/qq-bot
Environment=PATH=/opt/qq-bot/venv/bin
ExecStart=/opt/qq-bot/venv/bin/python start.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载 systemd
    sudo systemctl daemon-reload
    
    log_success "系统服务创建完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    # 检查 ufw 是否安装
    if ! command -v ufw &> /dev/null; then
        sudo apt install -y ufw
    fi
    
    # 配置防火墙规则
    sudo ufw allow 22    # SSH
    sudo ufw allow 8080  # OneBot WebSocket
    sudo ufw --force enable
    
    log_success "防火墙配置完成"
}

# 显示后续步骤
show_next_steps() {
    log_success "安装完成！"
    echo
    echo "后续步骤："
    echo "1. 上传机器人代码到 /opt/qq-bot/ 目录"
    echo "2. 安装 Python 依赖："
    echo "   cd /opt/qq-bot && source venv/bin/activate && pip install -r requirements.txt"
    echo "3. 配置 QQ 账号信息："
    echo "   sudo vim /opt/lagrange-onebot/appsettings.json"
    echo "4. 启动服务："
    echo "   sudo systemctl start lagrange-onebot"
    echo "   sudo systemctl start qq-bot"
    echo "5. 查看日志："
    echo "   sudo journalctl -u lagrange-onebot -f"
    echo "   sudo journalctl -u qq-bot -f"
    echo
    echo "管理命令："
    echo "   sudo systemctl status lagrange-onebot  # 查看状态"
    echo "   sudo systemctl restart lagrange-onebot # 重启服务"
    echo "   sudo systemctl stop lagrange-onebot    # 停止服务"
}

# 主函数
main() {
    echo "=========================================="
    echo "    QQ 机器人 Ubuntu 云服务器部署脚本"
    echo "=========================================="
    echo
    
    check_root
    check_system
    update_system
    install_python
    download_lagrange
    configure_lagrange
    deploy_bot
    create_env_file
    create_systemd_services
    configure_firewall
    show_next_steps
}

# 运行主函数
main "$@"
