# 项目文档 v2（正式）

面向新手与运维的正式文档。目标：让你在 Ubuntu 上快速完成部署、验证与日常使用。

## 这是什么
- 一个基于 NoneBot2 + OneBot v11（Lagrange.OneBot）的 QQ 机器人
- 功能：多 Wiki 快捷链接、随机数等，插件可扩展
- 主要特性：
  - 恋与深空WIKI快捷链接（`gd检索词`）
  - 米斯特利亚WIKI快捷链接（`m检索词`）
  - 随机数生成（`.rand`、`.randrange`）
  - 支持缓存，相同页面命中更快
  - 基于 curid 直达页，无需第三方短链

## 适用对象与平台
- 读者：初次部署者、维护者
- 平台：Linux/Ubuntu（本套文档不包含 Windows/PowerShell）
- 服务器配置要求：
  - **推荐配置**：2核CPU、2GB内存、20GB+ SSD、3Mbps+带宽
  - **最低配置**：1核CPU、1GB内存、10GB硬盘、1Mbps带宽
  - **系统**：Ubuntu Server 18.04.1 LTS 或更高版本

## 立即开始
- 从零到一（Ubuntu 单页教程）：`docs/zero-to-one-ubuntu.md`
- 故障排查（5 分钟定位）：`docs/troubleshooting.md`
- 群内使用说明：`docs/usage.md`

## 技术栈

- **框架**: NoneBot2（Python异步机器人框架）
- **协议**: OneBot v11（QQ机器人通信协议）
- **核心**: Lagrange.OneBot（QQ客户端实现）
- **短链转换**: 基于curid的直达链接，无需第三方短链服务
- **Python版本**: 3.8+（推荐使用虚拟环境）
- **系统服务**: systemd（服务化管理）

## 端口配置说明

**重要**：为了避免端口冲突，系统使用以下端口分配：

- **8080端口**：Lagrange.OneBot WebSocket服务器
  - 提供OneBot v11 WebSocket服务
  - 路径：`ws://127.0.0.1:8080/onebot/v11/ws`
  
- **8081端口**：NoneBot2 HTTP服务器（可选）
  - 仅用于健康检查和调试
  - 实际通信通过WebSocket进行

**架构**：QQ机器人作为WebSocket客户端连接到Lagrange.OneBot的8080端口，而不是自己启动HTTP服务器。

## 配置唯一来源（Single Source of Truth）
- **Lagrange配置（权威）**：`/opt/lagrange/appsettings.json`
  - 必须设置：`SignServerUrl` 为官方签名服务器
  - 云服务器部署：`ConsoleCompatibilityMode=true`
  - 连接稳定：`HeartBeatEnable=true`
  - 安全考虑：`Host=127.0.0.1`（非0.0.0.0）
- **机器人环境变量模板**：仓库根 `env.example`（复制为 `.env` 并按需最小化修改）
  - 核心配置：`ONEBOT_WS_URL=ws://127.0.0.1:8080/onebot/v11/ws`
  - 日志配置：`LOG_LEVEL=INFO`
  - 短链配置：`SHORTLINK_TIMEOUT=2`、`SHORTLINK_RETRY=1`

## 文档使用建议
- **你是新手**：直接按"从零到一"单页顺序完成部署与验证
- **遇到问题**：打开"故障排查"，按顺序定位
- **想查指令**：打开"群内使用说明"
- **日常维护**：使用systemd命令管理服务，查看日志排查问题

## 管理命令速查

### 服务管理
```bash
# 查看服务状态
sudo systemctl status lagrange-onebot | cat
sudo systemctl status qq-bot | cat

# 重启服务
sudo systemctl restart lagrange-onebot
sudo systemctl restart qq-bot

# 查看日志
sudo journalctl -u lagrange-onebot -f
sudo journalctl -u qq-bot -f
```

### 故障排查
```bash
# 检查端口占用
ss -tlnp | grep 8080 || true

# 检查防火墙状态
sudo ufw status || true

# 验证配置
cd /home/ubuntu/botbwiki
python check_env.py
python verify_config.py
```

## 安全建议
1. **修改默认端口**：将8080改为其他端口
2. **设置访问令牌**：在配置文件中设置AccessToken
3. **定期更新**：保持系统和依赖包更新
4. **备份配置**：定期备份配置文件和数据库
5. **权限管理**：确保文件权限正确，避免权限问题
