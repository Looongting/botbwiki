# NapCat 虚拟显示环境配置指南

本指南详细说明如何在 Linux 无头服务器上配置 NapCat 的虚拟显示环境，解决 NapCat 启动和配置加载问题。

## 概述

NapCat 基于 NTQQ 客户端，在 Linux 无头服务器环境中需要虚拟显示服务器才能正常运行。本文档总结了完整的配置流程和常见问题解决方案。

## 核心问题

### 1. 虚拟显示依赖
- NapCat 需要图形界面环境才能启动
- Linux 服务器通常没有显示器和图形界面
- 需要使用 Xvfb 提供虚拟显示环境

### 2. 配置文件加载问题
- NapCat 首次启动会生成空的配置文件
- 需要手动复制正确的配置文件到指定位置
- 配置文件路径与 QQ 账号相关

## 环境要求

### 系统要求
- Ubuntu 20.04+ 或其他 Linux 发行版
- 已安装 NapCat
- 具有 sudo 权限

### 必需软件包
```bash
# 安装虚拟显示服务器
sudo apt update
sudo apt install -y xvfb

# 验证安装
which Xvfb
```

## 配置步骤

### 1. 安装和启动 Xvfb

#### 手动启动方式
```bash
# 启动虚拟显示服务器
Xvfb :1 -screen 0 1x1x8 +extension GLX +render > /dev/null 2>&1 &

# 设置显示环境变量
export DISPLAY=:1
```

#### 自动化脚本方式
在启动脚本中添加 Xvfb 检查和启动功能：

```bash
# 检查和启动 Xvfb 的函数
start_xvfb() {
    echo "🖥️  启动虚拟显示服务器..."
    
    # 检查 Xvfb 是否已安装
    if ! command -v Xvfb &> /dev/null; then
        echo "⚠️  Xvfb 未安装，正在安装..."
        sudo apt update && sudo apt install -y xvfb
    fi
    
    # 检查 Xvfb 是否已在运行
    if pgrep -f "Xvfb :1" > /dev/null; then
        echo "✅ Xvfb 已在运行"
    else
        echo "🚀 启动 Xvfb 虚拟显示服务器..."
        Xvfb :1 -screen 0 1x1x8 +extension GLX +render > /dev/null 2>&1 &
        sleep 2
        echo "✅ Xvfb 启动完成"
    fi
}
```

### 2. 配置 NapCat 启动命令

#### 基本启动命令
```bash
# 设置环境变量并启动 NapCat
export DISPLAY=:1
cd /home/ubuntu/Napcat/opt/QQ
LD_PRELOAD=./libnapcat_launcher.so ./qq --no-sandbox
```

#### 快速登录方式
```bash
# 使用已保存的登录信息快速启动
export DISPLAY=:1
cd /home/ubuntu/Napcat/opt/QQ
LD_PRELOAD=./libnapcat_launcher.so ./qq --no-sandbox -q [QQ号]
```

### 3. 配置文件管理

#### 配置文件位置
```
/home/ubuntu/Napcat/opt/QQ/resources/app/app_launcher/napcat/config/
├── onebot11_[QQ号].json     # OneBot V11 协议配置
├── napcat_[QQ号].json       # NapCat 主配置
└── webui.json               # Web 管理界面配置
```

#### 正确的 OneBot 配置
创建或更新 `onebot11_[QQ号].json`：

```json
{
  "_comment": "NapCat OneBot V11 配置 - 虚拟显示环境",
  "network": {
    "httpServers": [
      {
        "_comment": "HTTP API 服务器配置",
        "enable": true,
        "host": "127.0.0.1",
        "port": 8080,
        "secret": "",
        "enableHeart": true,
        "enablePost": true,
        "enableCors": true
      }
    ],
    "httpSseServers": [],
    "httpClients": [],
    "websocketServers": [
      {
        "_comment": "WebSocket 服务器配置",
        "enable": true,
        "host": "127.0.0.1",
        "port": 8081,
        "path": "/onebot/v11/ws",
        "secret": "",
        "enableHeart": true
      }
    ],
    "websocketClients": [],
    "plugins": []
  },
  "musicSignUrl": "",
  "enableLocalFile2Url": false,
  "parseMultMsg": false
}
```

#### 配置文件复制脚本
```bash
#!/bin/bash
# 复制配置文件到 NapCat 目录

QQ_NUMBER="your_qq_number"
SOURCE_CONFIG="/path/to/your/onebot11_config.json"
TARGET_CONFIG="/home/ubuntu/Napcat/opt/QQ/resources/app/app_launcher/napcat/config/onebot11_${QQ_NUMBER}.json"

# 复制配置文件
cp "$SOURCE_CONFIG" "$TARGET_CONFIG"
echo "配置文件已复制到: $TARGET_CONFIG"
```

## 启动脚本集成

### 修改 start-background.sh

在现有的启动脚本中集成虚拟显示环境支持：

```bash
# 在 screen 启动部分添加
start_xvfb
echo "🚀 在 screen 中启动 NapCat..."
screen -dmS napcat bash -c "cd /home/ubuntu/Napcat/opt/QQ && export DISPLAY=:1 && LD_PRELOAD=./libnapcat_launcher.so ./qq --no-sandbox"

# 在 tmux 启动部分添加
start_xvfb
echo "🚀 在 tmux 中启动 NapCat..."
tmux new-session -d -s napcat "cd /home/ubuntu/Napcat/opt/QQ && export DISPLAY=:1 && LD_PRELOAD=./libnapcat_launcher.so ./qq --no-sandbox"

# 在 nohup 启动部分添加
start_xvfb
echo "🚀 使用 nohup 启动 NapCat..."
cd /home/ubuntu/Napcat/opt/QQ
nohup bash -c "export DISPLAY=:1 && LD_PRELOAD=./libnapcat_launcher.so ./qq --no-sandbox" > napcat.log 2>&1 &
```

### systemd 服务配置

修改 `napcat.service` 模板：

```ini
[Unit]
Description=NapCat QQ Bot Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Napcat/opt/QQ
ExecStartPre=/bin/bash -c 'if ! pgrep -f "Xvfb :1" > /dev/null; then Xvfb :1 -screen 0 1x1x8 +extension GLX +render > /dev/null 2>&1 & sleep 2; fi'
ExecStart=/bin/bash -c 'export DISPLAY=:1 && LD_PRELOAD=./libnapcat_launcher.so ./qq --no-sandbox'
Restart=always
RestartSec=10

# 环境变量
Environment=DISPLAY=:1
Environment=XVFB_WHD=1x1x8
Environment=QT_QPA_PLATFORM=offscreen

# 安全设置
NoNewPrivileges=true
PrivateTmp=true

# 资源限制
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
```

## 故障排查

### 1. 检查虚拟显示服务器状态

```bash
# 检查 Xvfb 进程
ps aux | grep Xvfb

# 检查显示环境变量
echo $DISPLAY

# 测试虚拟显示
xdpyinfo -display :1
```

### 2. 检查 NapCat 启动状态

```bash
# 检查 NapCat 进程
ps aux | grep qq

# 检查端口监听
netstat -tlnp | grep -E "(8080|8081)"

# 查看 NapCat 日志
tail -f /home/ubuntu/Napcat/opt/QQ/resources/app/app_launcher/napcat/logs/*.log
```

### 3. 常见问题解决

#### 问题 1：NapCat 无法启动
**症状**：启动命令执行后进程立即退出

**解决方案**：
1. 检查 Xvfb 是否正常运行
2. 确认 DISPLAY 环境变量设置正确
3. 检查 NapCat 文件权限

#### 问题 2：配置文件不生效
**症状**：NapCat 启动但 WebSocket 服务未启动

**解决方案**：
1. 检查配置文件是否存在于正确路径
2. 验证配置文件 JSON 格式正确性
3. 确认 QQ 号码与配置文件名匹配

#### 问题 3：重复登录提示
**症状**：每次启动都要求扫码登录

**解决方案**：
1. 使用快速登录参数 `-q [QQ号]`
2. 检查登录数据目录权限
3. 确认 QQ 配置目录完整性

## 最佳实践

### 1. 自动化部署
- 使用脚本自动安装和配置 Xvfb
- 集成配置文件管理到部署流程
- 提供一键启动和停止脚本

### 2. 监控和维护
- 定期检查 Xvfb 进程状态
- 监控 NapCat 服务健康状态
- 备份重要配置文件

### 3. 安全考虑
- 限制虚拟显示服务器访问权限
- 定期更新系统和依赖包
- 使用非 root 用户运行服务

## 参考资源

- [NapCat 官方文档](https://napneko.github.io/NapCatQQ/)
- [Xvfb 官方文档](https://www.x.org/releases/X11R7.6/doc/man/man1/Xvfb.1.xhtml)
- [Linux 虚拟显示配置指南](https://wiki.archlinux.org/title/Xvfb)

---

**更新日期**：2025-10-31  
**版本**：1.0  
**适用于**：NapCat 4.8.124+, Ubuntu 20.04+