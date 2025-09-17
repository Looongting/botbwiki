#!/bin/bash
# 权限修复脚本
# 用于修复部署过程中可能出现的权限问题

set -e

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

# 检查目录是否存在
check_directory() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        log_error "目录不存在: $dir"
        return 1
    fi
    return 0
}

# 修复 Lagrange.OneBot 权限
fix_lagrange_permissions() {
    log_info "修复 Lagrange.OneBot 权限..."
    
    if check_directory "/opt/lagrange-onebot"; then
        # 修改所有者为当前用户
        sudo chown -R $USER:$USER /opt/lagrange-onebot
        
        # 设置执行权限
        sudo chmod +x /opt/lagrange-onebot/Lagrange.OneBot
        
        # 设置配置文件权限
        if [[ -f "/opt/lagrange-onebot/appsettings.json" ]]; then
            chmod 644 /opt/lagrange-onebot/appsettings.json
        fi
        
        log_success "Lagrange.OneBot 权限修复完成"
    fi
}

# 修复 QQ 机器人权限
fix_bot_permissions() {
    log_info "修复 QQ 机器人权限..."
    
    if check_directory "/opt/qq-bot"; then
        # 修改所有者为当前用户
        sudo chown -R $USER:$USER /opt/qq-bot
        
        # 设置虚拟环境权限
        if [[ -d "/opt/qq-bot/venv" ]]; then
            chmod +x /opt/qq-bot/venv/bin/python*
            chmod +x /opt/qq-bot/venv/bin/pip*
        fi
        
        # 设置启动脚本权限
        if [[ -f "/opt/qq-bot/start.py" ]]; then
            chmod 755 /opt/qq-bot/start.py
        fi
        
        # 设置环境变量文件权限
        if [[ -f "/opt/qq-bot/.env" ]]; then
            chmod 600 /opt/qq-bot/.env
        fi
        
        # 设置日志文件权限
        if [[ -f "/opt/qq-bot/bot.log" ]]; then
            chmod 644 /opt/qq-bot/bot.log
        fi
        
        log_success "QQ 机器人权限修复完成"
    fi
}

# 修复系统服务权限
fix_service_permissions() {
    log_info "检查系统服务权限..."
    
    # 检查服务文件是否存在
    if [[ -f "/etc/systemd/system/lagrange-onebot.service" ]]; then
        sudo chmod 644 /etc/systemd/system/lagrange-onebot.service
        log_success "lagrange-onebot.service 权限已修复"
    else
        log_warning "lagrange-onebot.service 文件不存在"
    fi
    
    if [[ -f "/etc/systemd/system/qq-bot.service" ]]; then
        sudo chmod 644 /etc/systemd/system/qq-bot.service
        log_success "qq-bot.service 权限已修复"
    else
        log_warning "qq-bot.service 文件不存在"
    fi
    
    # 重新加载 systemd
    sudo systemctl daemon-reload
    log_success "systemd 配置已重新加载"
}

# 显示权限信息
show_permissions() {
    log_info "当前权限信息："
    echo
    
    echo "Lagrange.OneBot 目录权限："
    if [[ -d "/opt/lagrange-onebot" ]]; then
        ls -la /opt/lagrange-onebot/ | head -10
    else
        echo "  目录不存在"
    fi
    
    echo
    echo "QQ 机器人目录权限："
    if [[ -d "/opt/qq-bot" ]]; then
        ls -la /opt/qq-bot/ | head -10
    else
        echo "  目录不存在"
    fi
    
    echo
    echo "系统服务文件权限："
    if [[ -f "/etc/systemd/system/lagrange-onebot.service" ]]; then
        ls -la /etc/systemd/system/lagrange-onebot.service
    fi
    if [[ -f "/etc/systemd/system/qq-bot.service" ]]; then
        ls -la /etc/systemd/system/qq-bot.service
    fi
}

# 主函数
main() {
    echo "=========================================="
    echo "         权限修复脚本"
    echo "=========================================="
    echo
    
    # 显示当前用户
    log_info "当前用户: $USER"
    log_info "用户组: $(groups $USER)"
    echo
    
    # 修复权限
    fix_lagrange_permissions
    fix_bot_permissions
    fix_service_permissions
    
    echo
    show_permissions
    
    echo
    log_success "权限修复完成！"
    
    echo
    echo "如果仍有权限问题，请检查："
    echo "1. 确保以正确的用户身份运行服务"
    echo "2. 检查 SELinux 或 AppArmor 设置（如果启用）"
    echo "3. 确保防火墙允许相应端口"
}

# 显示使用说明
show_usage() {
    echo "使用方法："
    echo "  $0 [选项]"
    echo
    echo "选项："
    echo "  -s, --show      仅显示当前权限信息"
    echo "  -h, --help      显示此帮助信息"
    echo
}

# 解析命令行参数
case "${1:-}" in
    -s|--show)
        show_permissions
        exit 0
        ;;
    -h|--help)
        show_usage
        exit 0
        ;;
    "")
        main
        ;;
    *)
        log_error "未知参数: $1"
        show_usage
        exit 1
        ;;
esac
