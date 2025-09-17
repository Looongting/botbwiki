# 故障排查（5 分钟内定位）

按顺序检查，每一步都能给出明确结果与下一步。

## 1. 无法连接 Lagrange（WS 失败）
1) Lagrange 配置（权威）：`/opt/lagrange/appsettings.json`
   - `Type=ForwardWebSocket`
   - `Host=127.0.0.1` `Port=8080` `Suffix=/onebot/v11/ws`
   - `HeartBeatEnable=true`
2) 机器人 `.env`
   - `ONEBOT_WS_URL=ws://127.0.0.1:8080/onebot/v11/ws`
   - NoneBot 驱动应为：`driver="~httpx+~websockets"`（见 `bot.py` 初始化）
3) 服务状态与日志
```bash
sudo systemctl status lagrange-onebot | cat
sudo journalctl -u lagrange-onebot -f
```
4) 端口占用/防火墙
```bash
ss -tlnp | grep 8080 || true
sudo ufw status || true
```

## 2. 机器人不回应
- 插件是否加载成功（日志有 `Succeeded to load plugin`）
- 指令格式是否正确（群聊测试 `gd词`、`m词`、`.rand`）
- 查看机器人日志：
```bash
sudo systemctl status qq-bot | cat
sudo journalctl -u qq-bot -f
```

## 3. 二维码或登录问题
- 将 `ConsoleCompatibilityMode=true` 后重启 Lagrange：
```bash
sudo systemctl restart lagrange-onebot
```
- 首启扫码不生效时，前台运行一次：
```bash
cd /opt/lagrange && ./Lagrange.OneBot
```

## 4. 端口冲突与修改
- 检查 8080 是否被占用；若冲突，修改 `/opt/lagrange/appsettings.json` 的 `Port`，并同步 `.env` 的 `ONEBOT_WS_URL`
- 重启后验证：
```bash
sudo systemctl restart lagrange-onebot qq-bot
ss -tlnp | grep 8080 || true
```

## 5. 快速体检工具
```bash
cd /home/ubuntu/botbwiki
python check_env.py
python verify_config.py
```

## 6. 仍未解决？
- 提供以下信息：两份服务的 `systemctl status`、最近 200 行 `journalctl`、`.env` 的关键项（脱敏）。
