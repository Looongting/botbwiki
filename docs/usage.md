# 使用说明

本文档聚焦于"怎么用"。部署与配置请参阅《从零到一：Ubuntu 云服务器部署》（`docs/v2/zero-to-one-ubuntu.md`）。

## 前提

- 已完成部署，`Lagrange.OneBot` 与机器人均在运行
- 群聊中使用，私聊默认不响应
- 确保服务状态正常：
  ```bash
  sudo systemctl status lagrange-onebot | cat
  sudo systemctl status qq-bot | cat
  ```

## 指令一览

### 短链功能
- **恋与深空WIKI**：`gd检索词`
- **米斯特利亚WIKI**：`m检索词`

### 随机数功能
- **随机数（1-100）**：`.rand`
- **指定范围随机数**：`.randrange <最小值> <最大值>`

### AI功能
- **AI连接测试**：`?ai_test`
- **AI对话**：`?ai <问题>`
- **AI服务状态**：`?ai_status`
- **群消息总结**：`?ai_summary [日期]`（开发中）

## 使用示例

### 短链使用示例
```text
gd沈星回   # 机器人回复：沈星回：https://wiki.biligame.com/lysk/?curid=xxxx
m瓦伦     # 机器人回复：瓦伦：https://wiki.biligame.com/mistria/?curid=xxxx
```

### 随机数使用示例
```text
.rand                    # 机器人回复：随机数：42
.randrange 1 50         # 机器人回复：随机数：23
.randrange 100 1000     # 机器人回复：随机数：567
```

### AI功能使用示例
```text
?ai_test                 # 机器人回复：🤖 正在测试AI连接... ✅ AI测试成功！
?ai 今天天气怎么样？     # 机器人回复：🤖 AI正在思考... 🤖 AI回复：今天天气很好...
?ai_status              # 机器人回复：🤖 AI服务状态 触发词：?ai 默认服务：longcat...
?ai_summary             # 机器人回复：📊 正在分析群消息... 📋 群消息总结...
```

## 功能说明

### 短链功能特性
- **基于curid直达**：无需第三方短链服务，直接跳转到目标页面
- **支持缓存**：相同页面命中更快，提升响应速度
- **多WIKI支持**：支持恋与深空和米斯特利亚两个WIKI站点
- **智能检索**：支持模糊匹配，提高查找成功率

### 随机数功能特性
- **默认范围**：`.rand` 生成1-100之间的随机数
- **自定义范围**：`.randrange` 支持指定最小值和最大值
- **范围限制**：建议区间差 ≤ 10000，避免过大范围影响性能
- **即时响应**：本地生成，无需网络请求

### AI功能特性
- **多服务支持**：支持LongCat AI（默认）和火山引擎AI（备用）
- **智能对话**：支持各种问题咨询，自动添加prompt前缀
- **服务切换**：自动检测服务状态，支持备用服务切换
- **状态查询**：可查询当前AI服务配置和状态
- **消息总结**：支持群消息主题总结（开发中）

## 常见问题

### 1. 机器人没有响应

#### 检查服务状态
```bash
# 检查服务是否运行
sudo systemctl status lagrange-onebot | cat
sudo systemctl status qq-bot | cat
```

#### 查看应用日志
```bash
# 查看机器人日志
sudo journalctl -u qq-bot -f

# 查看应用日志
tail -f /home/ubuntu/botbwiki/bot.log
```

#### 可能原因
- 服务未启动或异常退出
- 插件加载失败
- 网络连接问题
- 配置错误

### 2. 短链功能失败

#### 检查网络连接
```bash
# 检查网络连通性
curl -I https://wiki.biligame.com/lysk/ || true
curl -I https://wiki.biligame.com/mistria/ || true
```

#### 可能原因
- 网络连接问题
- WIKI站点暂时不可用
- 检索词不存在或拼写错误
- 短链服务超时

#### 解决方案
- 稍后重试
- 检查检索词拼写
- 尝试使用更精确的检索词
- 查看机器人日志获取详细错误信息

### 3. 指令格式错误

#### 正确格式
- **短链**：`gd词`、`m词`（注意：gd和m后面直接跟检索词，无空格）
- **随机数**：`.rand`、`.randrange A B`（注意：点号开头，randrange需要两个参数）

#### 常见错误
- `gd 沈星回`（错误：gd后面有空格）
- `rand`（错误：缺少点号前缀）
- `.randrange 50`（错误：缺少最大值参数）
- `.randrange 100 50`（错误：最小值大于最大值）

#### 回复格式
- **短链**：`检索词：链接`
- **随机数**：`随机数：数字`

### 4. AI功能问题

#### AI连接失败
**可能原因**：
- API密钥配置错误
- 网络连接问题
- AI服务异常

**解决方法**：
1. 检查`.env`文件中的AI密钥配置
2. 运行`?ai_test`测试连接
3. 查看机器人日志获取详细错误信息

#### AI回复超时
**可能原因**：
- 网络延迟
- AI服务负载高
- 请求内容过长

**解决方法**：
1. 简化问题内容
2. 稍后重试
3. 检查网络连接

### 5. 权限问题

#### 检查文件权限
```bash
# 检查配置文件权限
ls -la /home/ubuntu/botbwiki/.env
ls -la /opt/lagrange/appsettings.json
```

#### 修复权限
```bash
# 修改文件所有者
sudo chown $USER:$USER /home/ubuntu/botbwiki/.env
sudo chown $USER:$USER /opt/lagrange/appsettings.json
```

## 高级使用

### 批量测试
```bash
# 测试短链功能
echo "gd测试" | nc localhost 8080
echo "m测试" | nc localhost 8080

# 测试随机数功能
echo ".rand" | nc localhost 8080
echo ".randrange 1 10" | nc localhost 8080

# 测试AI功能
echo "?ai_test" | nc localhost 8080
echo "?ai 你好" | nc localhost 8080
echo "?ai_status" | nc localhost 8080
```

### 日志分析
```bash
# 查看短链请求日志
grep "短链" /home/ubuntu/botbwiki/bot.log

# 查看随机数请求日志
grep "随机数" /home/ubuntu/botbwiki/bot.log

# 查看AI功能日志
grep "AI" /home/ubuntu/botbwiki/bot.log
grep "ai_test\|ai_status" /home/ubuntu/botbwiki/bot.log

# 查看错误日志
grep "ERROR" /home/ubuntu/botbwiki/bot.log
```

### 性能监控
```bash
# 监控服务资源使用
htop
top -p $(pgrep -f "Lagrange.OneBot\|start.py")

# 监控网络连接
ss -tlnp | grep 8080
netstat -an | grep 8080
```

## 故障排查

如果遇到问题，请按以下顺序排查：

1. **检查服务状态**：确认两个服务都在运行
2. **查看日志**：检查系统日志和应用日志
3. **验证配置**：确认配置文件正确
4. **测试网络**：检查网络连接
5. **重启服务**：尝试重启相关服务

详细故障排查请参考：`docs/v2/troubleshooting.md`

## 更新和维护

### 更新机器人代码
```bash
cd /home/ubuntu/botbwiki
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart qq-bot
```

### 更新 Lagrange.OneBot
```bash
cd /opt/lagrange
# 下载新版本
wget "https://xget.xi-xu.me/gh/LagrangeDev/Lagrange.Core/releases/download/nightly/Lagrange.OneBot_linux-x64_net9.0_SelfContained.tar.gz"
# 备份配置
cp appsettings.json appsettings.json.bak
# 解压新版本
tar -xzf Lagrange.OneBot_linux-x64_net9.0_SelfContained.tar.gz
# 恢复配置
cp appsettings.json.bak appsettings.json
# 重启服务
sudo systemctl restart lagrange-onebot
```

### 备份配置
```bash
# 备份配置文件
cp /opt/lagrange/appsettings.json /home/ubuntu/backup/
cp /home/ubuntu/botbwiki/.env /home/ubuntu/backup/
```

—— 完 ——
