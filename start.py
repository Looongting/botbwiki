#!/usr/bin/env python3
"""
机器人启动脚本
提供更友好的启动体验
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import config
from nonebot.log import logger


def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查 Python 版本
    if sys.version_info < (3, 8):
        print("❌ Python 版本过低，需要 Python 3.8 或更高版本")
        return False
    
    print(f"✅ Python 版本: {sys.version}")
    
    # 检查必要的文件
    required_files = ["bot.py", "config.py", "plugins/shortlink.py", "plugins/random.py"]
    for file_path in required_files:
        if not (project_root / file_path).exists():
            print(f"❌ 缺少必要文件: {file_path}")
            return False
    
    print("✅ 项目文件完整")
    
    # 检查环境变量文件
    env_file = project_root / ".env"
    env_example = project_root / "env.example"
    
    if not env_file.exists() and env_example.exists():
        print("⚠️  未找到 .env 文件，请复制 env.example 为 .env 并配置相关参数")
        print("   或者使用默认配置继续运行")
    
    return True


def print_config_info():
    """打印配置信息"""
    print("\n📋 当前配置:")
    print(f"   机器人名称: {config.BOT_NAME}")
    print(f"   Onebot WebSocket URL: {config.ONEBOT_WS_URL}")
    print(f"   Onebot HTTP URL: {config.ONEBOT_HTTP_URL}")
    print(f"   日志级别: {config.LOG_LEVEL}")
    print(f"   日志文件: {config.LOG_FILE}")


def main():
    """主函数"""
    print("🤖 QQ 机器人启动器")
    print("=" * 50)
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请修复问题后重试")
        sys.exit(1)
    
    # 打印配置信息
    print_config_info()
    
    print("\n🚀 正在启动机器人...")
    print("   按 Ctrl+C 停止机器人")
    print("=" * 50)
    
    try:
        # 导入并运行机器人
        import bot
    except KeyboardInterrupt:
        print("\n👋 机器人已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        logger.error(f"机器人启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
