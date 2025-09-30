# 免审权限管理功能使用指南

## 功能概述

免审权限管理功能允许群管理员为指定用户添加Wiki站点的免审权限，支持通过关键字触发，如：`?lysk免审 用户ID`。

## 主要特性

1. **权限验证**: 仅群管理员可执行免审权限操作
2. **智能UID提取**: 支持从消息内容和群昵称中自动提取用户ID
3. **多Wiki支持**: 可扩展支持多个Wiki站点的权限管理
4. **自动到期时间**: 权限自动设置为当前月份最后一天23:59到期
5. **智能回复**: 添加成功后引用用户消息并回复到期时间信息
6. **表情反馈**: 使用表情符号快速反馈操作结果
7. **安全认证**: 支持使用sessdata进行MediaWiki API认证

## 使用方法

### 基本命令格式

```
?lysk免审 [用户ID]
```

### 使用示例

1. **指定用户ID**：
   ```
   ?lysk免审 2342354
   ```
   为UID 2342354 添加恋与深空WIKI免审权限，权限到期时间为当月月末23:59

2. **从群昵称提取**：
   ```
   ?lysk免审
   ```
   从发送者的群昵称中提取UID并添加权限，权限到期时间为当月月末23:59

### 操作流程

1. **权限检查**: 验证发送者是否为群管理员
2. **UID提取**: 从消息内容或群昵称中提取用户ID
3. **到期时间计算**: 自动计算当前月份最后一天23:59作为权限到期时间
4. **API调用**: 通过MediaWiki API添加用户到指定用户组（带到期时间）
5. **结果反馈**: 使用表情符号反馈操作结果，并引用回复到期时间信息
   - ✅ 成功 - 发送成功表情并引用回复："本月权限新添就，感恩君力付春秋。过期时间为xxxx年xx月xx日 xx:xx"
   - ❌ 失败 - 发送失败表情
   - 引用回复提示修改群昵称（当无法提取UID时）

## 配置要求

### 环境变量配置

在`.env`文件中添加以下配置：

```bash
# Wiki API认证配置
WIKI_SESSDATA=your_sessdata_here
```

### 权限配置

在`config.py`中配置免审关键字和对应的用户组：

```python
# 免审权限配置 - 关键字到权限设置的映射
EXEMPTION_CONFIGS = {
    "?lysk免审": {
        "addgroup": "automoderated",    # 要添加的用户组
        "wiki": "lysk",                # 对应的wiki站点
        "checkPermission": True        # 是否需要权限验证
    }
}
```

### 扩展其他Wiki站点

要添加其他Wiki站点的免审权限支持，可以在配置中添加新的条目：

```python
EXEMPTION_CONFIGS = {
    "?lysk免审": {
        "addgroup": "automoderated",
        "wiki": "lysk",
        "checkPermission": True
    },
    "?mistria免审": {
        "addgroup": "automoderated",
        "wiki": "mistria",
        "checkPermission": True
    }
}
```

## 测试工具

使用提供的测试工具验证功能：

```bash
cd /home/ubuntu/botbwiki
python tools/test_exemption.py
```

测试工具会检查：
- 配置是否正确
- Wiki API连接是否正常
- CSRF token获取是否成功
- 用户组信息获取功能

## 注意事项

1. **权限要求**: 只有群管理员可以执行免审权限操作
2. **UID格式**: 用户ID必须是6位以上的数字
3. **网络要求**: 需要能够访问Wiki API端点
4. **认证配置**: 确保正确配置了WIKI_SESSDATA用于API认证
5. **错误处理**: 如果操作失败，机器人会发送❌表情；如果无法提取UID，会引用回复提示修改群昵称

## 故障排查

### 常见问题

1. **权限不足**：
   - 确保发送者是群管理员
   - 检查`checkPermission`配置

2. **UID提取失败**：
   - 确保消息中包含6位以上的数字
   - 检查群昵称是否包含UID

3. **API连接失败**：
   - 检查网络连接
   - 验证WIKI_SESSDATA配置
   - 运行测试工具检查API状态

4. **配置错误**：
   - 检查`EXEMPTION_CONFIGS`配置格式
   - 确保wiki名称与`WIKI_CONFIGS`中的映射正确

### 日志查看

查看机器人日志获取详细错误信息：

```bash
tail -f logs/bot.log
```

## 技术实现

### 核心模块

- `src/core/wiki_api.py`: MediaWiki API封装
- `plugins/exemption.py`: 免审权限插件主体
- `src/core/config.py`: 配置管理

### API端点

使用MediaWiki的`userrights` API：
- 获取CSRF token: `action=query&meta=tokens&type=userrights`
- 添加用户组: `action=userrights&add=group&user=userid&token=token`

### 安全机制

1. 群管理员权限验证
2. CSRF token保护
3. sessdata认证
4. 操作日志记录
