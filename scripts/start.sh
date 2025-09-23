#!/bin/bash
# Linux 机器人启动脚本
# 自动激活虚拟环境并启动机器人

echo "🤖 QQ 机器人启动脚本"
echo "=================================================="

# 切换到项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# 检查是否在正确的目录
if [ ! -f "main.py" ]; then
    echo "❌ 错误：找不到 main.py 文件"
    echo "   当前目录：$(pwd)"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 错误：虚拟环境不存在"
    echo "   正在创建虚拟环境..."
    python -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 创建虚拟环境失败"
        exit 1
    fi
fi

# 激活虚拟环境
echo "🔍 激活虚拟环境..."
source venv/bin/activate

# 检查并安装依赖
echo "🔍 检查依赖包..."
if ! python -c "import nonebot2" 2>/dev/null; then
    echo "⚠️  依赖包未安装，正在安装..."
    pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖包安装失败"
        exit 1
    fi
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "⚠️  配置文件不存在，正在创建..."
    if [ -f "config/env.example" ]; then
        cp config/env.example .env
        echo "✅ 已创建 .env 文件，请编辑配置后重新运行"
        echo "   主要配置项："
        echo "   - ONEBOT_WS_URL: Onebot WebSocket 连接地址"
        echo "   - ONEBOT_HTTP_URL: Onebot HTTP 连接地址"
        exit 0
    else
        echo "❌ 找不到 config/env.example 文件"
        exit 1
    fi
fi

echo "✅ 环境检查完成"
echo "🚀 正在启动机器人..."
echo "   按 Ctrl+C 停止机器人"
echo "=================================================="

# 启动机器人
python main.py
