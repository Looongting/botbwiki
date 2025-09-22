#!/bin/bash
# AI功能依赖安装脚本

echo "🤖 开始安装AI功能依赖..."

# 检查是否在项目目录
if [ ! -f "start.py" ]; then
    echo "❌ 错误：请在项目根目录下运行此脚本"
    echo "   当前目录：$(pwd)"
    echo "   请切换到包含 start.py 的目录"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 错误：未找到虚拟环境"
    echo "   请先运行 ./install.sh 创建虚拟环境"
    exit 1
fi

# 激活虚拟环境
echo "🔍 激活虚拟环境..."
source venv/bin/activate

if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 虚拟环境已激活: $VIRTUAL_ENV"
else
    echo "❌ 虚拟环境激活失败"
    exit 1
fi

# 安装新依赖
echo "📦 安装火山引擎AI SDK..."
pip install volcengine-python-sdk>=1.0.0

echo "📦 安装时间处理库..."
pip install python-dateutil>=2.8.0

# 更新requirements.txt
echo "📝 更新requirements.txt..."
pip freeze > requirements.txt

echo "✅ AI功能依赖安装完成！"
echo ""
echo "📋 下一步操作："
echo "1. 在.env文件中配置火山引擎AI密钥"
echo "2. 运行测试脚本: python test_ai.py"
echo "3. 重启机器人服务"
echo ""
echo "🔧 配置示例："
echo "VOLC_AI_ACCESS_KEY=your_access_key_here"
echo "VOLC_AI_SECRET_KEY=your_secret_key_here"
echo ""
echo "💡 提示："
echo "   - 使用 ./activate.sh 激活虚拟环境"
echo "   - 使用 ./start.sh 启动机器人"
