#!/bin/bash
# 服务部署脚本 - 设置 NapCat 和 QQ Bot 的 systemd 服务

echo "🚀 QQ 机器人服务部署脚本"
echo "=================================================="

# 切换到项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# 检查是否有 sudo 权限
if ! sudo -n true 2>/dev/null; then
    echo "❌ 需要 sudo 权限来安装系统服务"
    echo "   请运行: sudo $0"
    exit 1
fi

echo "📋 检查服务模板文件..."
NAPCAT_SERVICE="config/systemd-service-templates/napcat.service"
QQBOT_SERVICE="config/systemd-service-templates/qq-bot.service"

if [ ! -f "$NAPCAT_SERVICE" ]; then
    echo "❌ 找不到 NapCat 服务模板: $NAPCAT_SERVICE"
    exit 1
fi

if [ ! -f "$QQBOT_SERVICE" ]; then
    echo "❌ 找不到 QQ Bot 服务模板: $QQBOT_SERVICE"
    exit 1
fi

echo "📦 安装服务文件..."
# 复制服务文件到系统目录
sudo cp "$NAPCAT_SERVICE" /etc/systemd/system/
sudo cp "$QQBOT_SERVICE" /etc/systemd/system/

# 设置正确的权限
sudo chmod 644 /etc/systemd/system/napcat.service
sudo chmod 644 /etc/systemd/system/qq-bot.service

echo "🔄 重新加载 systemd..."
sudo systemctl daemon-reload

echo "🔧 启用服务..."
sudo systemctl enable napcat.service
sudo systemctl enable qq-bot.service

echo "✅ 服务安装完成！"
echo ""
echo "📖 使用说明："
echo "   启动服务: sudo systemctl start napcat && sudo systemctl start qq-bot"
echo "   停止服务: sudo systemctl stop qq-bot && sudo systemctl stop napcat"
echo "   查看状态: sudo systemctl status napcat qq-bot"
echo "   查看日志: sudo journalctl -u napcat -f"
echo "            sudo journalctl -u qq-bot -f"
echo ""
echo "⚠️  注意事项："
echo "   1. 首次启动前请确保已通过 WebUI 登录过 QQ"
echo "   2. 确保 onebot11_config.json 配置正确"
echo "   3. 确保虚拟环境和依赖已正确安装"
echo ""
echo "🎯 快速启动："
echo "   sudo systemctl start napcat"
echo "   sleep 10  # 等待 NapCat 启动"
echo "   sudo systemctl start qq-bot"