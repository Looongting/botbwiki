# 开发指南

## 项目架构

### 目录结构
```
bot/
├── README.md                 # 项目说明文档
├── pyproject.toml           # 项目配置文件
├── requirements.txt         # Python 依赖列表
├── env.example              # 环境变量示例
├── config.py                # 配置管理模块
├── bot.py                   # 机器人主程序
├── start.py                 # 启动脚本
├── plugins/                 # 插件目录
│   ├── __init__.py
│   ├── shortlink.py         # 短链生成插件
│   └── random.py            # 随机数生成插件
└── docs/                    # 文档目录
    ├── usage.md             # 使用说明
    └── development.md       # 开发指南（本文件）
```

### 核心组件

1. **bot.py**: 机器人主程序，负责初始化和启动
2. **config.py**: 配置管理，统一管理所有配置项
3. **plugins/**: 插件目录，每个功能模块独立开发
4. **start.py**: 启动脚本，提供环境检查和友好启动体验

## 插件开发

### 插件结构

每个插件都是一个独立的 Python 模块，包含以下基本结构：

```python
"""
插件描述
功能：简要说明插件功能
"""

from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.log import logger
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# 创建处理器
handler = on_command("command", priority=5)

@handler.handle()
async def handle_command(bot: Bot, event: GroupMessageEvent):
    """处理命令"""
    try:
        # 插件逻辑
        pass
    except Exception as e:
        logger.error(f"插件错误: {e}")
        await handler.finish("处理失败，请稍后重试")
```

### 开发规范

1. **导入规范**：
   - 使用相对导入或添加项目根目录到 sys.path
   - 统一从 config 模块导入配置

2. **错误处理**：
   - 所有插件都必须包含 try-catch 错误处理
   - 记录详细错误日志
   - 向用户返回友好的错误信息

3. **日志记录**：
   - 使用 `logger.info()` 记录重要操作
   - 使用 `logger.error()` 记录错误信息
   - 避免使用 `print()` 输出调试信息

4. **消息处理**：
   - 仅响应群聊消息（GroupMessageEvent）
   - 使用合适的优先级（priority）
   - 及时调用 `finish()` 结束处理

### 添加新插件

1. 在 `plugins/` 目录下创建新的 Python 文件
2. 按照插件结构编写代码
3. 在 `bot.py` 中确保插件被自动加载
4. 更新文档说明新功能

## 配置管理

### 配置文件

所有配置项都在 `config.py` 中统一管理：

```python
class Config:
    # 连接配置
    ONEBOT_WS_URL: str = os.getenv("ONEBOT_WS_URL", "ws://127.0.0.1:8080/ws")
    
    # 功能配置
    SHORTLINK_TIMEOUT: int = int(os.getenv("SHORTLINK_TIMEOUT", "10"))
    
    # 其他配置...
```

### 环境变量

支持通过 `.env` 文件或系统环境变量配置：

```bash
# .env 文件示例
ONEBOT_WS_URL=ws://127.0.0.1:8080/ws
BOT_NAME=我的机器人
LOG_LEVEL=INFO
```

### 添加新配置

1. 在 `Config` 类中添加新的配置项
2. 在 `env.example` 中添加示例值
3. 在插件中使用 `config.配置项名` 访问

## 测试

### 功能测试

1. **短链生成测试**：
   - 发送 `#测试` 消息
   - 检查是否返回短链
   - 测试错误情况（如网络断开）

2. **随机数测试**：
   - 发送 `.rand` 消息
   - 检查返回的随机数是否在 1-100 范围内
   - 测试范围随机数功能

### 日志检查

查看 `bot.log` 文件确认：
- 机器人正常启动
- 插件正确加载
- 消息处理正常
- 错误信息详细

## 部署

### 开发环境

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境
cp env.example .env
# 编辑 .env 文件

# 启动机器人
python start.py
```

### 生产环境

1. 使用虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置系统服务（可选）：
   - 使用 systemd（Linux）
   - 使用 Windows 服务
   - 使用 Docker 容器

## 故障排除

### 常见问题

1. **插件未加载**：
   - 检查 `plugins/` 目录结构
   - 确认 `__init__.py` 文件存在
   - 查看启动日志

2. **配置不生效**：
   - 检查 `.env` 文件格式
   - 确认环境变量名称正确
   - 重启机器人

3. **网络连接问题**：
   - 检查 Onebot 服务是否运行
   - 确认连接地址和端口
   - 查看防火墙设置

### 调试技巧

1. **启用详细日志**：
   ```bash
   LOG_LEVEL=DEBUG python start.py
   ```

2. **单独测试插件**：
   - 创建测试脚本
   - 模拟消息事件
   - 验证插件逻辑

3. **使用断点调试**：
   - 在 IDE 中设置断点
   - 使用调试模式启动

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 编写代码和测试
4. 更新文档
5. 提交 Pull Request

### 代码规范

- 使用 Black 格式化代码
- 使用 isort 排序导入
- 遵循 PEP 8 规范
- 添加适当的注释和文档字符串
