#!/usr/bin/env python3
"""
环境检查脚本入口
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.check_env import main

if __name__ == "__main__":
    main()
