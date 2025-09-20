# 使用说明

本文档聚焦于“怎么用”。部署与配置请参阅《Ubuntu 云服务器部署指南》（`docs/ubuntu-deployment.md`）。

## 前提

- 已完成部署，`Lagrange.OneBot` 与机器人均在运行
- 群聊中使用，私聊默认不响应

## 指令一览

- 短链（恋与深空WIKI）：`gd检索词`
- 短链（米斯特利亚WIKI）：`m检索词`
- 随机数：`.rand`（1-100）
- 指定范围随机数：`.randrange <最小值> <最大值>`

## 使用示例

```text
gd沈星回   # 机器人回复：沈星回：https://wiki.biligame.com/lysk/?curid=xxxx
m瓦伦     # 机器人回复：瓦伦：https://wiki.biligame.com/mistria/?curid=xxxx
.rand
.randrange 1 50
```

## 说明

- 短链接口基于 curid 直达页，无需第三方短链
- 支持缓存，相同页面命中更快
- `.randrange` 的区间差建议 ≤ 10000

## 常见问题

1) 没有响应
- 检查服务是否运行：
```bash
sudo systemctl status lagrange-onebot | cat
sudo systemctl status qq-bot | cat
```
- 查看应用日志：
```bash
tail -n 200 bot.log
```

2) 短链失败
- 检查网络；稍后重试

3) 指令报错
- 确认格式：`gd词`、`m词`、`.rand`、`.randrange A B`
- 回复格式：`检索词：链接`

—— 完 ——
