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
    
    log_success "Lagrange.OneBot 配置完成"
}

# 部署 Python 机器人
deploy_bot() {
    log_info "部署 Python 机器人..."
    
    # 检查是否提供了 Git 仓库地址
    if [[ -n "$GIT_REPO" ]]; then
        log_info "从 Git 仓库克隆代码: $GIT_REPO"
        
        # 克隆仓库
        sudo rm -rf /opt/qq-bot
        sudo git clone "$GIT_REPO" /opt/qq-bot
        sudo chown -R $USER:$USER /opt/qq-bot
        cd /opt/qq-bot
        
        # 检查是否有指定分支
        if [[ -n "$GIT_BRANCH" ]]; then
            git checkout "$GIT_BRANCH"
        fi
        
        log_success "代码克隆完成"
    else
        log_info "创建机器人目录..."
        
        # 创建目录
        sudo mkdir -p /opt/qq-bot
        cd /opt/qq-bot
        
        log_warning "未提供 Git 仓库地址，请手动上传代码到 /opt/qq-bot/ 目录"
    fi
    
    # 创建虚拟环境
    python3 -m venv venv
    source venv/bin/activate
    
    # 升级 pip
    pip install --upgrade pip
    
    # 安装依赖（如果存在 requirements.txt）
    if [[ -f "requirements.txt" ]]; then
        log_info "安装 Python 依赖..."
        pip install -r requirements.txt
        log_success "依赖安装完成"
    else
        log_warning "未找到 requirements.txt 文件"
    fi
    
    log_success "Python 机器人环境准备完成"
}

# 创建环境变量文件
create_env_file() {
    log_info "创建环境变量文件..."
    
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
Wants=network-online.target

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

# 环境变量
Environment=DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1

# 安全设置
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/lagrange-onebot

# 资源限制
MemoryMax=512M
TasksMax=100

[Install]
WantedBy=multi-user.target
EOF

    # Python 机器人服务
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
WorkingDirectory=/opt/qq-bot
Environment=PATH=/opt/qq-bot/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=/opt/qq-bot/venv/bin/python start.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=qq-bot

# 安全设置
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/qq-bot

# 资源限制
MemoryMax=256M
TasksMax=50

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
    
    if [[ -n "$GIT_REPO" ]]; then
        echo "✅ 代码已从 Git 仓库克隆"
        echo "✅ Python 依赖已安装"
    else
        echo "1. 上传机器人代码到 /opt/qq-bot/ 目录"
        echo "2. 安装 Python 依赖："
        echo "   cd /opt/qq-bot && source venv/bin/activate && pip install -r requirements.txt"
    fi
    
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
    echo
    echo "代码更新："
    echo "   cd /opt/qq-bot && git pull origin main"
    echo "   source venv/bin/activate && pip install -r requirements.txt"
    echo "   sudo systemctl restart qq-bot"
}

# 显示使用说明
show_usage() {
    echo "使用方法："
    echo "  $0 [选项]"
    echo
    echo "选项："
    echo "  -r, --repo URL      Git 仓库地址"
    echo "  -b, --branch NAME   指定分支名称 (默认: main)"
    echo "  -h, --help          显示此帮助信息"
    echo
    echo "示例："
    echo "  $0 -r https://github.com/username/repo.git"
    echo "  $0 -r https://github.com/username/repo.git -b develop"
    echo
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -r|--repo)
                GIT_REPO="$2"
                shift 2
                ;;
            -b|--branch)
                GIT_BRANCH="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# 主函数
main() {
    echo "=========================================="
    echo "    QQ 机器人 Ubuntu 云服务器部署脚本"
    echo "=========================================="
    echo
    
    # 解析命令行参数
    parse_args "$@"
    
    # 显示配置信息
    if [[ -n "$GIT_REPO" ]]; then
        log_info "Git 仓库: $GIT_REPO"
        if [[ -n "$GIT_BRANCH" ]]; then
            log_info "分支: $GIT_BRANCH"
        else
            log_info "分支: main (默认)"
        fi
    else
        log_info "部署模式: 手动上传代码"
    fi
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
