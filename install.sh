#!/bin/bash
# Linux 一键安装脚本
# 自动安装依赖、配置环境并启动机器人

echo "🤖 QQ 机器人一键安装脚本"
echo "=================================================="

# 检查 Python 版本
echo "🔍 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3"
    echo "   请先安装 Python 3.8 或更高版本"
    echo "   Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "   CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python 版本: $PYTHON_VERSION"

# 检查是否在正确的目录
if [ ! -f "start.py" ]; then
    echo "❌ 错误：请在项目根目录下运行此脚本"
    echo "   当前目录：$(pwd)"
    echo "   请切换到包含 start.py 的目录"
    exit 1
fi

# 创建虚拟环境
echo "🔍 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "⚠️  虚拟环境已存在，是否重新创建？(y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
    fi
else
    python3 -m venv venv
fi

if [ $? -ne 0 ]; then
    echo "❌ 创建虚拟环境失败"
    exit 1
fi

# 激活虚拟环境
echo "🔍 激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "🔍 升级 pip..."
python -m pip install --upgrade pip

# 安装依赖
echo "🔍 安装项目依赖..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖包安装失败"
        exit 1
    fi
else
    echo "❌ 找不到 requirements.txt 文件"
    exit 1
fi

# 创建配置文件
echo "🔍 配置环境变量..."
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ 已创建 .env 配置文件"
        echo "⚠️  请编辑 .env 文件配置相关参数："
        echo "   - ONEBOT_WS_URL: Onebot WebSocket 连接地址"
        echo "   - ONEBOT_HTTP_URL: Onebot HTTP 连接地址"
        echo "   - BOT_NAME: 机器人名称"
        echo "   - LOG_LEVEL: 日志级别"
    else
        echo "❌ 找不到 env.example 文件"
        exit 1
    fi
else
    echo "✅ 配置文件已存在"
fi

# 设置脚本权限
echo "🔍 设置脚本权限..."
chmod +x activate.sh start.sh install.sh 2>/dev/null

# 运行环境检查
echo "🔍 运行环境检查..."
python check_env.py

echo ""
echo "✅ 安装完成！"
echo "=================================================="
echo "📋 使用说明："
echo "   1. 编辑 .env 文件配置参数"
echo "   2. 运行 ./start.sh 启动机器人"
echo "   3. 或运行 ./activate.sh 激活环境后手动启动"
echo ""
echo "🔧 常用命令："
echo "   ./start.sh          # 一键启动"
echo "   ./activate.sh       # 激活环境"
echo "   python start.py     # 直接启动"
echo "   python check_env.py # 环境检查"
echo "=================================================="
