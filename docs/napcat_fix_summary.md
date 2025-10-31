# NapCat 虚拟显示环境修复总结

本文档总结了 NapCat 在 Linux 无头服务器环境中的配置问题及其解决方案。

## 问题背景

### 初始状态
- NapCat 进程运行但 WebSocket 服务未启动
- 端口 8081 未监听
- 机器人无法连接到 NapCat
- 配置文件存在但内容不正确

### 核心问题
1. **虚拟显示环境缺失**：NapCat 基于 NTQQ 客户端，需要图形界面环境
2. **配置文件问题**：自动生成的配置文件 WebSocket 服务器配置为空
3. **启动方式问题**：未使用快速登录导致重复扫码

## 解决方案

### 1. 虚拟显示环境配置

#### 问题表现
- NapCat 启动失败或立即退出
- 日志显示图形界面相关错误

#### 解决步骤
```bash
# 安装 Xvfb 虚拟显示服务器
sudo apt update && sudo apt install -y xvfb

# 启动虚拟显示服务器
Xvfb :1 -screen 0 1x1x8 +extension GLX +render > /dev/null 2>&1 &

# 设置环境变量
export DISPLAY=:1

# 验证虚拟显示运行状态
ps aux | grep "Xvfb :1" | grep -v grep
```

#### 关键配置
- 显示编号：`:1`
- 屏幕配置：`1x1x8`（最小化资源占用）
- 扩展支持：`+extension GLX +render`

### 2. 配置文件修复

#### 问题表现
- NapCat 启动但 WebSocket 服务未启动
- 配置文件中 `websocketServers` 字段为空数组

#### 配置文件位置
```
/home/ubuntu/Napcat/opt/QQ/resources/app/app_launcher/napcat/config/onebot11_[QQ号].json
```

#### 正确配置内容
```json
{
  "network": {
    "httpServers": [
      {
        "enable": true,
        "host": "127.0.0.1",
        "port": 8080,
        "secret": "",
        "enableHeart": true,
        "enablePost": true,
        "enableCors": true
      }
    ],
    "websocketServers": [
      {
        "enable": true,
        "host": "127.0.0.1",
        "port": 8081,
        "path": "/onebot/v11/ws",
        "secret": "",
        "enableHeart": true
      }
    ]
  }
}
```

#### 修复步骤
```bash
# 复制正确的配置文件
cp /home/ubuntu/botbwiki/botbwiki/onebot11_config.json \
   /home/ubuntu/Napcat/opt/QQ/resources/app/app_launcher/napcat/config/onebot11_[QQ号].json

# 重启 NapCat 进程
pkill -f "qq --no-sandbox"
```

### 3. 快速登录配置

#### 问题表现
- 每次启动都要求扫码登录
- 已有登录数据但未被使用

#### 解决方案
```bash
# 使用快速登录参数启动
cd /home/ubuntu/Napcat/opt/QQ
export DISPLAY=:1
LD_PRELOAD=./libnapcat_launcher.so ./qq --no-sandbox -q [QQ号]
```

#### 登录数据位置
```
/home/ubuntu/.config/QQ/
├── nt_qq/                    # QQ 登录数据
├── nt_qq_[hash]/            # 特定实例数据
└── NapCat/                  # NapCat 配置数据
```

## 启动脚本优化

### 集成虚拟显示检查
```bash
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

### 完整启动流程
```bash
# 1. 启动虚拟显示服务器
start_xvfb

# 2. 启动 NapCat（使用快速登录）
echo "🚀 在 screen 中启动 NapCat..."
screen -dmS napcat bash -c "cd /home/ubuntu/Napcat/opt/QQ && export DISPLAY=:1 && LD_PRELOAD=./libnapcat_launcher.so ./qq --no-sandbox -q [QQ号]"

# 3. 等待服务启动
sleep 5

# 4. 验证服务状态
netstat -tlnp | grep -E "(8080|8081)"
```

## 验证步骤

### 1. 检查虚拟显示
```bash
# 检查 Xvfb 进程
ps aux | grep "Xvfb :1" | grep -v grep

# 检查环境变量
echo $DISPLAY

# 测试虚拟显示
xdpyinfo -display :1
```

### 2. 检查 NapCat 服务
```bash
# 检查进程状态
ps aux | grep qq | grep -v grep

# 检查端口监听
netstat -tlnp | grep -E "(8080|8081)"

# 检查日志
tail -f /home/ubuntu/Napcat/opt/QQ/resources/app/app_launcher/napcat/logs/*.log
```

### 3. 测试机器人连接
```bash
# 查看机器人日志
tail -f /home/ubuntu/botbwiki/botbwiki/bot.log

# 发送测试消息到群聊
# 例如：gd 测试
```

## 关键发现

### 1. 配置文件生成机制
- NapCat 首次启动会为每个 QQ 号生成独立的配置文件
- 文件名格式：`onebot11_[QQ号].json`
- 初始生成的配置文件 WebSocket 服务器配置为空

### 2. 虚拟显示依赖
- NapCat 基于 NTQQ 客户端，必须有图形界面环境
- Xvfb 提供最小化的虚拟显示环境
- 环境变量 `DISPLAY=:1` 必须正确设置

### 3. 快速登录优势
- 避免重复扫码登录
- 使用已保存的登录数据
- 启动参数：`-q [QQ号]`

### 4. 端口分离原则
- HTTP API：8080 端口
- WebSocket：8081 端口
- 避免端口冲突和协议混用

## 最佳实践

### 1. 自动化部署
- 脚本化虚拟显示环境配置
- 自动复制正确的配置文件
- 集成健康检查和重启机制

### 2. 监控和维护
- 定期检查 Xvfb 进程状态
- 监控 NapCat 服务健康状态
- 备份重要配置文件

### 3. 故障排查
- 按层次检查：虚拟显示 → NapCat 进程 → 配置文件 → 网络连接
- 使用日志文件定位具体问题
- 验证每个组件的独立功能

## 相关文档

- [NapCat 虚拟显示环境配置指南](./napcat_virtual_display_setup.md)
- [NapCat 配置指南](./napcat_config_guide.md)
- [故障排查指南](./troubleshooting.md)

---

**修复完成时间**：2025-10-31  
**修复版本**：NapCat 4.8.124  
**适用环境**：Ubuntu 20.04+ 无头服务器