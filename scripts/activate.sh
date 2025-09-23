#!/bin/bash
# Linux 虚拟环境激活脚本
# 用于激活 Python 虚拟环境并启动机器人

# 检查是否直接运行脚本（而不是通过source）
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    echo "❌ 错误：请使用 source ./activate.sh 来激活虚拟环境"
    echo "   直接运行 ./activate.sh 无法在当前shell中激活虚拟环境"
    echo ""
    echo "✅ 正确的使用方式："
    echo "   source ./activate.sh"
    echo "   或者"
    echo "   . ./activate.sh"
    exit 1
fi

echo "🤖 QQ 机器人环境激活脚本"
echo "=================================================="

# 检查是否在正确的目录
if [ ! -f "start.py" ]; then
    echo "❌ 错误：请在项目根目录下运行此脚本"
    echo "   当前目录：$(pwd)"
    echo "   请切换到包含 start.py 的目录"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 错误：虚拟环境不存在"
    echo "   请先运行：python -m venv venv"
    exit 1
fi

echo "🔍 检查虚拟环境..."
if [ ! -f "venv/bin/activate" ]; then
    echo "❌ 错误：虚拟环境损坏"
    echo "   请重新创建虚拟环境：rm -rf venv && python -m venv venv"
    exit 1
fi

echo "✅ 激活 Python 虚拟环境..."
source venv/bin/activate

# 检查依赖是否安装
echo "🔍 检查依赖包..."
if ! python -c "import nonebot2" 2>/dev/null; then
    echo "⚠️  警告：依赖包未安装或版本不匹配"
    echo "   正在安装依赖包..."
    pip install -r requirements.txt
fi

echo "✅ 虚拟环境已激活！"
echo "📋 当前环境信息："
echo "   Python 版本: $(python --version)"
echo "   虚拟环境: $(which python)"
echo ""
echo "🚀 现在可以运行以下命令："
echo "   python start.py    # 启动机器人"
echo "   python check_env.py # 检查环境"
echo "   deactivate         # 退出虚拟环境"
echo "=================================================="