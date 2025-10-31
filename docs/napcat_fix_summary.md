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

### 4. Systemd 服务配置

#### 问题表现
- 关闭 IDE 或终端后机器人停止工作
- 需要手动启动，无法开机自启
- 进程管理不便

#### 解决方案

##### 4.1 使用现有脚本配置服务
```bash
# 运行服务配置脚本
cd /home/ubuntu/botbwiki/botbwiki
./scripts/setup-services.sh

# 启动服务
sudo systemctl start napcat
sudo systemctl start qq-bot

# 检查服务状态
sudo systemctl status napcat
sudo systemctl status qq-bot
```

##### 4.2 服务配置文件位置
- **模板文件**：`/home/ubuntu/botbwiki/botbwiki/config/systemd-service-templates/`
  - `napcat.service` - NapCat 服务配置
  - `qq-bot.service` - QQ Bot 服务配置
- **系统服务文件**：`/etc/systemd/system/`

##### 4.3 关键配置要点
```ini
# napcat.service 关键配置
[Unit]
Description=NapCat QQ Bot Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Napcat/opt/QQ
ExecStartPre=/bin/bash -c 'pgrep -f "Xvfb :1" || (Xvfb :1 -screen 0 1x1x8 +extension GLX +render > /dev/null 2>&1 &)'
ExecStart=/bin/bash -c 'export DISPLAY=:1 && LD_PRELOAD=./libnapcat_launcher.so ./qq --no-sandbox -q 3330219965'
Restart=always
Environment=NAPCAT_CONFIG_PATH=/home/ubuntu/botbwiki/onebot11_config.json

[Install]
WantedBy=multi-user.target
```

##### 4.4 快速登录配置修复
**问题**：systemd 服务模板缺少 QQ 号参数导致无法快速登录

**解决**：在 `napcat.service` 的 `ExecStart` 中添加 `-q [QQ号]` 参数
```bash
# 修复前
ExecStart=/bin/bash -c 'export DISPLAY=:1 && LD_PRELOAD=./libnapcat_launcher.so ./qq --no-sandbox'

# 修复后
ExecStart=/bin/bash -c 'export DISPLAY=:1 && LD_PRELOAD=./libnapcat_launcher.so ./qq --no-sandbox -q 3330219965'
```

### 5. 重复进程问题

#### 问题表现
- 机器人回复消息2次
- 同一条消息被处理多次

#### 问题原因
多个机器人进程同时运行：
1. **Screen 会话中的机器人** - 手动启动的进程
2. **Systemd 服务中的机器人** - 服务管理的进程

#### 解决方案

##### 5.1 检查重复进程
```bash
# 检查所有机器人相关进程
ps aux | grep -E "(python.*main.py|qq.*no-sandbox)" | grep -v grep

# 检查 screen 会话
screen -ls
```

##### 5.2 清理重复进程
```bash
# 停止 screen 会话中的机器人
screen -S [session_name] -X quit

# 或者直接杀死进程
pkill -f "python.*main.py"
```

##### 5.3 验证单一进程
```bash
# 确认只有一个机器人进程
ps aux | grep "python.*main.py" | grep -v grep

# 确认 screen 会话已清理
screen -ls
```

#### 最佳实践
- **统一使用 systemd 管理**：避免手动启动和服务启动混用
- **启动前检查**：确保没有其他实例在运行
- **进程监控**：定期检查进程状态，避免重复启动

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

## 修复历史

### 2025-10-31 - 初始虚拟显示环境修复
- **修复版本**：NapCat 4.8.124
- **主要问题**：虚拟显示环境配置、配置文件修复、快速登录配置
- **解决方案**：Xvfb 配置、配置文件复制、启动参数优化

### 2025-11-01 - Systemd 服务配置与重复进程修复
- **修复版本**：NapCat 4.8.124
- **主要问题**：
  1. 关闭 IDE 后机器人停止工作
  2. 机器人回复消息2次（重复进程问题）
  3. Systemd 服务缺少快速登录参数
- **解决方案**：
  1. 配置 systemd 服务实现开机自启和独立运行
  2. 清理重复的 screen 会话进程
  3. 修复服务模板中的快速登录参数
- **关键改进**：
  - 实现了真正的后台服务管理
  - 解决了进程冲突导致的重复回复问题
  - 优化了快速登录配置

**适用环境**：Ubuntu 20.04+ 无头服务器

### 2025-01-15 - 表情回复功能兼容性修复
- **修复版本**：NapCat 4.8.124
- **主要问题**：
  1. OneBot 11 标准的 `set_group_reaction` API 在 NapCat 中不被支持
  2. 机器人发送表情回复时出现 `HTTP 426: Upgrade Required` 错误
  3. AI处理器和权限管理插件的表情回复功能失效
- **错误表现**：
  ```
  HTTP 426: Upgrade Required - 调用 set_group_reaction API 失败
  ```
- **根本原因**：
  - NapCat 作为 OneBot 11 协议的实现，并未完全支持所有标准 API
  - `set_group_reaction` 属于 OneBot 11 标准但 NapCat 未实现的 API
  - 需要使用 NapCat 特有的 `set_msg_emoji_like` API 作为替代方案
- **解决方案**：
  1. **添加 NapCat 兼容 API**：
     - 在 `http_client.py` 中添加 `set_msg_emoji_like` 方法
     - 参数：`message_id` (number), `emoji_id` (string)
  2. **实现兼容性回退机制**：
     - 修改 `message_sender.py` 中的 `send_group_reaction` 方法
     - 优先尝试 OneBot 标准的 `set_group_reaction`
     - 失败时自动回退到 NapCat 的 `set_msg_emoji_like`
     - 添加表情ID映射转换功能
  3. **恢复表情回复功能**：
     - 恢复 AI 处理器中的表情回复（替代之前的文字提示）
     - 恢复权限管理插件中的表情回复（成功/失败状态指示）
- **技术实现**：
  ```python
  # 兼容性方法实现
  async def send_group_reaction(self, group_id: int, message_id: int, code: str) -> bool:
      try:
          # 优先尝试 OneBot 标准 API
          await self.http_client.set_group_reaction(group_id, message_id, code, True)
          return True
      except Exception as e:
          # 回退到 NapCat 特有 API
          try:
              emoji_id = self._convert_reaction_to_emoji_id(code)
              await self._send_napcat_emoji_like(message_id, emoji_id)
              return True
          except Exception as fallback_e:
              logger.error(f"表情回复完全失败: OneBot={e}, NapCat={fallback_e}")
              return False
  ```
- **表情ID映射**：
  - OneBot 反应码 → NapCat 表情ID
  - 例如：`"32"` (疑问) → `"32"`, `"124"` (OK) → `"124"`
  - 支持自定义映射扩展
- **测试验证**：
  - AI 对话触发时正常显示思考表情
  - 权限管理操作正常显示成功/失败表情
  - 兼容性回退机制工作正常
- **关键改进**：
  - 实现了 OneBot 11 和 NapCat 的双重兼容
  - 保持了原有功能体验的完整性
  - 提供了可扩展的表情映射机制
  - 增强了错误处理和日志记录

**适用环境**：Ubuntu 20.04+ 无头服务器