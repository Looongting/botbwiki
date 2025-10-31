#!/bin/bash
# 后台启动脚本 - 支持多种方式在后台运行机器人

echo "🤖 QQ 机器人后台启动脚本"
echo "=================================================="

# 切换到项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# 启动虚拟显示服务器 (NapCat 需要)
start_xvfb() {
    echo "🖥️  启动虚拟显示服务器..."
    
    # 检查 Xvfb 是否已安装
    if ! command -v Xvfb &> /dev/null; then
        echo "❌ Xvfb 未安装，正在安装..."
        sudo apt update && sudo apt install -y xvfb
    fi
    
    # 检查是否已有 Xvfb 进程在运行
    if pgrep -f "Xvfb :1" > /dev/null; then
        echo "✅ Xvfb 已在运行"
    else
        echo "🚀 启动 Xvfb..."
        Xvfb :1 -screen 0 1x1x8 +extension GLX +render > /dev/null 2>&1 &
        sleep 2
        echo "✅ Xvfb 启动完成"
    fi
}

# 显示使用方法
show_usage() {
    echo "使用方法: $0 [方式]"
    echo ""
    echo "可用方式:"
    echo "  systemd  - 使用 systemd 服务 (推荐，需要 sudo)"
    echo "  screen   - 使用 screen 会话"
    echo "  tmux     - 使用 tmux 会话"
    echo "  nohup    - 使用 nohup 后台运行"
    echo ""
    echo "示例:"
    echo "  $0 systemd"
    echo "  $0 screen"
    exit 1
}

# 检查参数
if [ $# -eq 0 ]; then
    show_usage
fi

METHOD="$1"

case "$METHOD" in
    "systemd")
        echo "🔧 使用 systemd 服务启动..."
        
        # 检查服务是否已安装
        if [ ! -f "/etc/systemd/system/napcat.service" ]; then
            echo "⚠️  systemd 服务未安装，正在安装..."
            if [ -f "scripts/setup-services.sh" ]; then
                sudo scripts/setup-services.sh
            else
                echo "❌ 找不到服务安装脚本"
                exit 1
            fi
        fi
        
        echo "🚀 启动 NapCat 服务..."
        sudo systemctl start napcat
        
        echo "⏳ 等待 NapCat 启动..."
        sleep 10
        
        echo "🚀 启动 QQ Bot 服务..."
        sudo systemctl start qq-bot
        
        echo "✅ 服务启动完成！"
        echo ""
        echo "📊 查看状态: sudo systemctl status napcat qq-bot"
        echo "📋 查看日志: sudo journalctl -u qq-bot -f"
        ;;
        
    "screen")
        echo "🖥️  使用 screen 会话启动..."
        
        # 检查 screen 是否安装
        if ! command -v screen &> /dev/null; then
            echo "❌ screen 未安装，正在安装..."
            sudo apt update && sudo apt install -y screen
        fi
        
        # 启动虚拟显示服务器
        start_xvfb
        
        # 启动 NapCat
        echo "🚀 在 screen 中启动 NapCat..."
        screen -dmS napcat bash -c "export DISPLAY=:1 && cd /home/ubuntu/Napcat/opt/QQ && LD_PRELOAD=./libnapcat_launcher.so ./qq --no-sandbox"
        
        sleep 10
        
        # 启动 QQ Bot
        echo "🚀 在 screen 中启动 QQ Bot..."
        screen -dmS qqbot bash -c "cd $PROJECT_ROOT && source venv/bin/activate && python main.py"
        
        echo "✅ 启动完成！"
        echo ""
        echo "📊 查看会话: screen -ls"
        echo "🔗 连接到 NapCat: screen -r napcat"
        echo "🔗 连接到 QQ Bot: screen -r qqbot"
        echo "🚪 退出会话: Ctrl+A, D"
        ;;
        
    "tmux")
        echo "🖥️  使用 tmux 会话启动..."
        
        # 检查 tmux 是否安装
        if ! command -v tmux &> /dev/null; then
            echo "❌ tmux 未安装，正在安装..."
            sudo apt update && sudo apt install -y tmux
        fi
        
        # 启动虚拟显示服务器
        start_xvfb
        
        # 启动 NapCat
        echo "🚀 在 tmux 中启动 NapCat..."
        tmux new-session -d -s napcat -c "/home/ubuntu/Napcat/opt/QQ" "export DISPLAY=:1 && LD_PRELOAD=./libnapcat_launcher.so ./qq --no-sandbox"
        
        sleep 10
        
        # 启动 QQ Bot
        echo "🚀 在 tmux 中启动 QQ Bot..."
        tmux new-session -d -s qqbot -c "$PROJECT_ROOT" "source venv/bin/activate && python main.py"
        
        echo "✅ 启动完成！"
        echo ""
        echo "📊 查看会话: tmux ls"
        echo "🔗 连接到 NapCat: tmux attach -t napcat"
        echo "🔗 连接到 QQ Bot: tmux attach -t qqbot"
        echo "🚪 退出会话: Ctrl+B, D"
        ;;
        
    "nohup")
        echo "🔄 使用 nohup 后台启动..."
        
        # 启动虚拟显示服务器
        start_xvfb
        
        # 启动 NapCat
        echo "🚀 后台启动 NapCat..."
        cd /home/ubuntu/Napcat/opt/QQ
        export DISPLAY=:1
        nohup env LD_PRELOAD=./libnapcat_launcher.so ./qq --no-sandbox > napcat.log 2>&1 &
        NAPCAT_PID=$!
        echo "NapCat PID: $NAPCAT_PID"
        
        sleep 10
        
        # 启动 QQ Bot
        echo "🚀 后台启动 QQ Bot..."
        cd "$PROJECT_ROOT"
        source venv/bin/activate
        nohup python main.py > qqbot.log 2>&1 &
        QQBOT_PID=$!
        echo "QQ Bot PID: $QQBOT_PID"
        
        echo "✅ 启动完成！"
        echo ""
        echo "📋 进程信息:"
        echo "   NapCat PID: $NAPCAT_PID"
        echo "   QQ Bot PID: $QQBOT_PID"
        echo ""
        echo "📊 查看进程: ps aux | grep -E '(qq|python.*main.py)'"
        echo "📋 查看日志: tail -f /home/ubuntu/Napcat/opt/QQ/napcat.log"
        echo "            tail -f $PROJECT_ROOT/qqbot.log"
        echo "🛑 停止进程: kill $NAPCAT_PID $QQBOT_PID"
        ;;
        
    *)
        echo "❌ 未知的启动方式: $METHOD"
        show_usage
        ;;
esac