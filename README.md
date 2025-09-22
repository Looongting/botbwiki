# 项目文档 v2（正式）

面向新手与运维的正式文档。目标：让你在 Ubuntu 上快速完成部署、验证与日常使用。

## 这是什么
- 一个基于 NoneBot2 + OneBot v11（Lagrange.OneBot）的 QQ 机器人
- 功能：多 Wiki 快捷链接、随机数等，插件可扩展
- 主要特性：
  - 恋与深空WIKI快捷链接（`gd检索词`）
  - 米斯特利亚WIKI快捷链接（`m检索词`）
  - 随机数生成（`.rand`、`.randrange`）
  - AI总结功能（`.ai_test`、`.ai`、`.ai_summary`）
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
- **AI服务**: 火山引擎AI（消息总结和对话功能）
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
  - AI配置：`VOLC_AI_ACCESS_KEY`、`VOLC_AI_SECRET_KEY`（火山引擎AI密钥）

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

## AI功能说明

⚠️ **重要提示**: AI总结功能目前存在技术问题，详见 `AI_SUMMARY_PROJECT_OVERVIEW.md`

### 可用命令
- `?ai_test` - 测试AI连接是否正常 ✅
- `?ai <问题>` - 与AI进行简单对话 ✅
- `?ai_summary [日期]` - 总结指定日期的群消息 ❌ (开发中)
- `?ai_auto <天数>` - 批量生成总结 ❌ (开发中)

### 配置要求
1. **火山引擎AI账号**：需要注册火山引擎账号并开通AI服务
2. **API密钥**：配置ARK_API_KEY到.env文件
3. **目标群配置**：支持多群配置，格式：`TARGET_GROUP_IDS=[群ID1,群ID2]`

### 详细文档
- `AI_SUMMARY_PROJECT_OVERVIEW.md` - 完整项目概览和技术细节
- `docs/ai_usage.md` - 用户使用指南
- `CORE_ISSUES_ANALYSIS.md` - 当前问题分析
3. **环境变量**：在`.env`文件中配置AI相关参数

### 配置示例
```bash
# 火山引擎AI配置
VOLC_AI_ACCESS_KEY=your_access_key_here
VOLC_AI_SECRET_KEY=your_secret_key_here
VOLC_AI_REGION=cn-beijing
VOLC_AI_ENDPOINT=ep-20250811175605-fxzbh
AI_SUMMARY_MAX_TOKENS=2000
AI_SUMMARY_TIMEOUT=30
```

### 安装步骤
1. **确保虚拟环境已创建**：运行 `./install.sh`
2. **安装AI依赖**：运行 `./install_ai_deps.sh`
3. **配置AI密钥**：在 `.env` 文件中添加上述配置
4. **测试功能**：运行 `python test_ai.py`
5. **启动机器人**：运行 `./start.sh`

## 安全建议
1. **修改默认端口**：将8080改为其他端口
2. **设置访问令牌**：在配置文件中设置AccessToken
3. **保护AI密钥**：妥善保管火山引擎AI的ACCESS_KEY和SECRET_KEY
4. **定期更新**：保持系统和依赖包更新
5. **备份配置**：定期备份配置文件和数据库
6. **权限管理**：确保文件权限正确，避免权限问题
