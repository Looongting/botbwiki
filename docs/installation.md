# 安装指南

## 系统要求

- **操作系统**: Windows 10/11, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.8 或更高版本
- **内存**: 至少 512MB 可用内存
- **网络**: 稳定的网络连接（用于短链生成功能）

## 详细安装步骤

### 1. 检查 Python 环境

首先确认您的系统已安装 Python 3.8 或更高版本：

```bash
python --version
# 或
python3 --version
```

如果未安装 Python，请访问 [Python 官网](https://www.python.org/downloads/) 下载并安装。

### 2. 获取项目代码

#### 方式一：从 Git 仓库克隆
```bash
git clone <repository-url>
cd bot
```

#### 方式二：下载 ZIP 文件
1. 下载项目 ZIP 文件
2. 解压到目标目录
3. 进入项目目录

### 3. 创建虚拟环境

**为什么使用虚拟环境？**
- 避免依赖冲突
- 保持系统 Python 环境干净
- 便于项目管理和部署

#### Windows
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# PowerShell:
venv\Scripts\activate
# CMD:
venv\Scripts\activate.bat
```

#### macOS/Linux
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

**激活成功的标志**：命令行提示符前会出现 `(venv)` 标识。

### 4. 升级 pip

```bash
python -m pip install --upgrade pip
```

### 5. 安装项目依赖

```bash
pip install -r requirements.txt
```

**依赖包说明**：
- `nonebot2`: 机器人框架核心
- `nonebot-adapter-onebot`: Onebot 协议适配器
- `httpx`: HTTP 客户端库
- `pydantic`: 数据验证库
- `python-dotenv`: 环境变量管理
- `loguru`: 日志库

### 6. 配置环境变量

```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑 .env 文件
# Windows:
notepad .env
# macOS/Linux:
nano .env
```

**主要配置项**：
```bash
# Onebot 连接配置
ONEBOT_WS_URL=ws://127.0.0.1:8080/ws
ONEBOT_HTTP_URL=http://127.0.0.1:8080

# 机器人配置
BOT_NAME=QQ机器人
BOT_MASTER_ID=123456789

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=bot.log
```

### 7. 环境检查

运行环境检查脚本：

```bash
python check_env.py
```

**检查项目**：
- Python 版本
- 虚拟环境状态
- 依赖包安装情况
- 项目文件完整性

### 8. 启动机器人

#### 方式一：使用启动脚本（推荐）
```bash
python start.py
```

#### 方式二：直接启动
```bash
python bot.py
```

## 快速激活脚本

项目提供了便捷的激活脚本，方便日常使用：

### Windows

#### CMD 用户
双击 `activate.bat` 文件，会自动：
1. 激活虚拟环境
2. 打开命令行窗口
3. 显示使用提示

#### PowerShell 用户
```bash
.\activate.ps1
```

### macOS/Linux
```bash
# 创建激活脚本
cat > activate.sh << 'EOF'
#!/bin/bash
echo "激活 Python 虚拟环境..."
source venv/bin/activate
echo "虚拟环境已激活！"
echo "现在可以运行: python start.py"
EOF

chmod +x activate.sh
./activate.sh
```

## 常见问题

### Q: 虚拟环境激活失败
**A**: 检查以下几点：
1. 确认 Python 版本 >= 3.8
2. 检查虚拟环境是否创建成功
3. 确认激活脚本路径正确

### Q: 依赖安装失败
**A**: 尝试以下解决方案：
1. 升级 pip: `python -m pip install --upgrade pip`
2. 使用国内镜像: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/`
3. 检查网络连接

### Q: 环境检查失败
**A**: 根据错误信息：
1. 缺少包：重新运行 `pip install -r requirements.txt`
2. 文件缺失：检查项目完整性
3. Python 版本：升级到 3.8+

### Q: 机器人启动失败
**A**: 检查配置：
1. 确认 `.env` 文件配置正确
2. 检查 Onebot 服务是否运行
3. 查看日志文件 `bot.log`

## 卸载

如需完全卸载项目：

```bash
# 停用虚拟环境
deactivate

# 删除虚拟环境目录
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows

# 删除项目目录
rm -rf bot  # macOS/Linux
rmdir /s bot  # Windows
```

## 更新

更新项目依赖：

```bash
# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 更新依赖
pip install --upgrade -r requirements.txt
```

## 生产环境部署

### 使用 systemd (Linux)

1. 创建服务文件：
```bash
sudo nano /etc/systemd/system/qq-bot.service
```

2. 添加服务配置：
```ini
[Unit]
Description=QQ Bot Service
After=network.target

[Service]
Type=simple
User=bot
WorkingDirectory=/path/to/bot
Environment=PATH=/path/to/bot/venv/bin
ExecStart=/path/to/bot/venv/bin/python start.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. 启动服务：
```bash
sudo systemctl enable qq-bot
sudo systemctl start qq-bot
```

### 使用 Docker

1. 创建 Dockerfile：
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "start.py"]
```

2. 构建和运行：
```bash
docker build -t qq-bot .
docker run -d --name qq-bot qq-bot
```


