# 项目文档 v2（正式）

面向新手与运维的正式文档。目标：让你在 Ubuntu 上快速完成部署、验证与日常使用。

## 这是什么
- 一个基于 NoneBot2 + OneBot v11（Lagrange.OneBot）的 QQ 机器人
- 功能：多 Wiki 快捷链接、随机数等，插件可扩展

## 适用对象与平台
- 读者：初次部署者、维护者
- 平台：Linux/Ubuntu（本套文档不包含 Windows/PowerShell）

## 立即开始
- 从零到一（Ubuntu 单页教程）：`docs/v2/zero-to-one-ubuntu.md`
- 故障排查（5 分钟定位）：`docs/v2/troubleshooting.md`
- 群内使用说明：`docs/usage.md`

## 技术栈

- **框架**: Nonebot2
- **协议**: Onebot11
- **核心**: LagrangeCore
- **短链转换**: b23.tv-tools

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
- Lagrange（权威）：`/opt/lagrange/appsettings.json`
- 机器人环境变量模板：仓库根 `env.example`（复制为 `.env` 并按需最小化修改）

## 文档使用建议
- 你是新手：直接按“从零到一”单页顺序完成部署与验证
- 遇到问题：打开“故障排查”，按顺序定位
- 想查指令：打开“群内使用说明”

## TODO（待确认事项）
- [ ] 确认 Lagrange 自包含包解压后的实际目录结构（历史曾调整过）
- [ ] 如有差异，更新本 v2 文档中的解压与可执行路径说明

—— 完 ——
