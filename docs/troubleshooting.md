# 故障排查（5 分钟内定位）

按顺序检查，每一步都能给出明确结果与下一步。

## 1. 无法连接 Lagrange（WS 失败）

### 1.1 检查 Lagrange 配置（权威）：`/opt/lagrange/appsettings.json`
```bash
# 检查关键配置项
cat /opt/lagrange/appsettings.json | grep -E "(Type|Host|Port|Suffix|HeartBeatEnable)"
```
必须确保：
- `Type=ForwardWebSocket`
- `Host=127.0.0.1` `Port=8080` `Suffix=/onebot/v11/ws`
- `HeartBeatEnable=true`
- `SignServerUrl` 设置为官方签名服务器

### 1.2 检查机器人 `.env` 配置
```bash
# 检查环境变量
cat /home/ubuntu/botbwiki/.env | grep ONEBOT_WS_URL
```
必须确保：
- `ONEBOT_WS_URL=ws://127.0.0.1:8080/onebot/v11/ws`
- NoneBot 驱动应为：`driver="~httpx+~websockets"`（见 `bot.py` 初始化）

### 1.3 检查服务状态与日志
```bash
# 检查服务状态
sudo systemctl status lagrange-onebot | cat
sudo systemctl status qq-bot | cat

# 查看实时日志
sudo journalctl -u lagrange-onebot -f
sudo journalctl -u qq-bot -f
```

### 1.4 检查端口占用/防火墙
```bash
# 检查端口占用
ss -tlnp | grep 8080 || true
sudo netstat -tlnp | grep 8080 || true
sudo lsof -i :8080 || true

# 检查防火墙状态
sudo ufw status || true
```

## 2. 机器人不回应

### 2.1 检查插件加载状态
```bash
# 查看机器人日志，确认插件加载成功
sudo journalctl -u qq-bot -n 50 | grep -E "(Succeeded to load plugin|Failed to load plugin)"
```

### 2.2 检查指令格式
- 指令格式是否正确（群聊测试 `gd词`、`m词`、`.rand`）
- 确认在群聊中使用，私聊默认不响应
- 检查指令前缀是否正确

### 2.3 查看详细日志
```bash
# 查看服务状态
sudo systemctl status qq-bot | cat

# 查看实时日志
sudo journalctl -u qq-bot -f

# 查看应用日志
tail -f /home/ubuntu/botbwiki/bot.log
```

## 3. 二维码或登录问题

### 3.1 启用控制台兼容模式
```bash
# 修改配置文件
sed -i 's/"ConsoleCompatibilityMode": false/"ConsoleCompatibilityMode": true/' /opt/lagrange/appsettings.json

# 重启 Lagrange
sudo systemctl restart lagrange-onebot
```

### 3.2 前台运行扫码
```bash
# 首启扫码不生效时，前台运行一次
cd /opt/lagrange && ./Lagrange.OneBot
```

### 3.3 检查登录状态
```bash
# 查看 Lagrange 日志，确认登录状态
sudo journalctl -u lagrange-onebot -n 20 | grep -E "(Login|Connect|QR)"
```

## 4. 端口冲突与修改

### 4.1 检查端口占用
```bash
# 检查 8080 是否被占用
ss -tlnp | grep 8080 || true
sudo netstat -tlnp | grep 8080 || true
sudo lsof -i :8080 || true
```

### 4.2 修改端口配置
若冲突，修改配置：
```bash
# 修改 Lagrange 配置
sed -i 's/"Port": 8080/"Port": 8081/' /opt/lagrange/appsettings.json

# 同步修改机器人配置
sed -i 's/8080/8081/g' /home/ubuntu/botbwiki/.env

# 重启服务
sudo systemctl restart lagrange-onebot qq-bot

# 验证修改
ss -tlnp | grep 8081 || true
```

## 5. 权限问题

### 5.1 VSCode 无法编辑文件
```bash
# 修改文件所有者
sudo chown $USER:$USER /opt/lagrange/appsettings.json
sudo chown $USER:$USER /home/ubuntu/botbwiki/.env

# 修改整个目录的所有者
sudo chown -R $USER:$USER /opt/lagrange
sudo chown -R $USER:$USER /home/ubuntu/botbwiki
```

### 5.2 检查文件权限
```bash
# 检查文件权限
ls -la /opt/lagrange/appsettings.json
ls -la /home/ubuntu/botbwiki/.env
ls -la /opt/lagrange/Lagrange.OneBot
```

## 6. Python 环境问题

### 6.1 虚拟环境问题
```bash
cd /home/ubuntu/botbwiki
source venv/bin/activate

# 验证虚拟环境
which python
which pip

# 重新安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

### 6.2 依赖冲突
```bash
# 检查依赖版本
pip list | grep -E "(nonebot|httpx|websockets)"

# 重新创建虚拟环境
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 7. 网络连接问题

### 7.1 检查网络连通性
```bash
# 检查本地连接
curl -I http://127.0.0.1:8080 || true

# 检查签名服务器连接
curl -I https://sign.lagrangecore.org/api/sign/39038 || true
```

### 7.2 防火墙配置
```bash
# 检查防火墙状态
sudo ufw status

# 开放必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 8080  # OneBot WebSocket
sudo ufw enable
```

## 8. 快速体检工具
```bash
cd /home/ubuntu/botbwiki
python check_env.py
python verify_config.py
```

## 9. 性能问题

### 9.1 资源使用检查
```bash
# 检查系统资源
htop
top
free -h
df -h

# 检查服务资源使用
sudo systemctl status lagrange-onebot qq-bot
```

### 9.2 日志轮转配置
```bash
# 配置日志轮转
sudo tee /etc/logrotate.d/qq-bot > /dev/null << 'EOF'
/home/ubuntu/botbwiki/bot.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 ubuntu ubuntu
}
EOF
```

## 10. 仍未解决？

### 10.1 收集诊断信息
```bash
# 收集系统信息
uname -a
python3 --version
systemctl --version

# 收集服务状态
sudo systemctl status lagrange-onebot qq-bot > /tmp/services_status.txt

# 收集日志
sudo journalctl -u lagrange-onebot -n 200 > /tmp/lagrange_logs.txt
sudo journalctl -u qq-bot -n 200 > /tmp/bot_logs.txt

# 收集配置（脱敏）
grep -v "password\|token\|key" /home/ubuntu/botbwiki/.env > /tmp/env_config.txt
```

### 10.2 提供信息
提供以下信息：
- 两份服务的 `systemctl status`
- 最近 200 行 `journalctl`
- `.env` 的关键项（脱敏）
- 系统版本和Python版本
- 错误日志的具体内容
