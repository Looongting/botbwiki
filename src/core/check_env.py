#!/usr/bin/env python3
"""
环境检查脚本
检查 Python 环境和依赖是否正确安装
"""

import sys
import importlib
from pathlib import Path


def check_python_version():
    """检查 Python 版本"""
    print("🐍 检查 Python 版本...")
    version = sys.version_info
    if version >= (3, 8):
        print(f"✅ Python 版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print("   需要 Python 3.8 或更高版本")
        return False


def check_virtual_env():
    """检查是否在虚拟环境中"""
    print("\n🔧 检查虚拟环境...")
    # 检查多种虚拟环境标识
    in_venv = (
        hasattr(sys, 'real_prefix') or  # virtualenv
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or  # venv
        (hasattr(sys, '_venv') and sys._venv) or  # pyenv
        'venv' in sys.prefix or 'virtualenv' in sys.prefix  # 路径包含标识
    )
    
    if in_venv:
        print("✅ 正在虚拟环境中运行")
        return True
    else:
        print("⚠️  未检测到虚拟环境")
        print("   建议使用虚拟环境运行项目")
        # 不强制要求虚拟环境，只是建议
        return True


def check_required_packages():
    """检查必需的包"""
    print("\n📦 检查必需的包...")
    
    required_packages = [
        ('nonebot2[fastapi]', 'nonebot'),
        ('nonebot_adapter_onebot', 'nonebot.adapters.onebot'),
        ('httpx', 'httpx'),
        ('pydantic', 'pydantic'),
        ('python_dotenv', 'dotenv'),
        ('loguru', 'loguru'),
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn')
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            importlib.import_module(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - 未安装")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n❌ 缺少以下包: {', '.join(missing_packages)}")
        print("   请运行: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ 所有必需的包都已安装")
        return True


def check_project_files():
    """检查项目文件"""
    print("\n📁 检查项目文件...")
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent.parent
    
    required_files = [
        'main.py',
        'src/core/config.py',
        'requirements.txt',
        'plugins/__init__.py',
        'plugins/shortlink.py',
        'plugins/random.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 文件不存在")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ 缺少以下文件: {', '.join(missing_files)}")
        return False
    else:
        print("\n✅ 所有项目文件都存在")
        return True


def main():
    """主函数"""
    print("🔍 QQ 机器人环境检查")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_virtual_env(),
        check_required_packages(),
        check_project_files()
    ]
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 环境检查通过！可以启动机器人了")
        print("\n启动命令:")
        print("  python main.py")
        print("  或使用: ./scripts/start.sh")
    else:
        print("❌ 环境检查失败，请修复问题后重试")
        sys.exit(1)


if __name__ == "__main__":
    main()
