# Git 部署指南

使用 Git 进行代码部署是最佳实践，可以实现版本控制、代码同步和自动化部署。

## 部署流程

### 1. 本地准备

#### 提交代码到 Git 仓库

```bash
# 添加新文件
git add docs/ubuntu-deployment.md
git add scripts/
git add PROJECT_CLEANUP.md

# 提交更改
git commit -m "feat: 添加 Ubuntu 云服务器部署支持

- 新增 Ubuntu 云服务器部署指南
- 提供一键部署脚本 scripts/install-ubuntu.sh
- 支持 systemd 服务管理
- 添加防火墙配置和系统服务管理"

# 推送到远程仓库
git push origin main
```

#### 创建发布标签（可选）

```bash
# 创建版本标签
git tag -a v1.1.0 -m "版本 1.1.0: 添加云服务器部署支持"

# 推送标签
git push origin v1.1.0
```

### 2. 云服务器部署

#### 方法一：使用部署脚本（推荐）

```bash
# 下载并运行部署脚本
curl -fsSL https://raw.githubusercontent.com/your-username/your-repo/main/scripts/install-ubuntu.sh | bash

# 或者先下载脚本再运行
wget https://raw.githubusercontent.com/your-username/your-repo/main/scripts/install-ubuntu.sh
chmod +x install-ubuntu.sh
./install-ubuntu.sh
```

#### 方法二：手动部署

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/your-repo.git /opt/qq-bot
cd /opt/qq-bot

# 2. 运行部署脚本
chmod +x scripts/install-ubuntu.sh
./scripts/install-ubuntu.sh

# 3. 安装 Python 依赖
source venv/bin/activate
pip install -r requirements.txt

# 4. 配置环境变量
cp env.example .env
vim .env  # 编辑配置

# 5. 启动服务
sudo systemctl start lagrange-onebot
sudo systemctl start qq-bot
```

### 3. 代码更新流程

#### 本地开发

```bash
# 1. 修改代码
# 2. 测试功能
# 3. 提交更改
git add .
git commit -m "feat: 添加新功能"
git push origin main
```

#### 服务器更新

```bash
# 1. 进入项目目录
cd /opt/qq-bot

# 2. 拉取最新代码
git pull origin main

# 3. 更新依赖（如果有新依赖）
source venv/bin/activate
pip install -r requirements.txt

# 4. 重启服务
sudo systemctl restart qq-bot
```

## 自动化部署

### 使用 GitHub Actions（推荐）

创建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to Server

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /opt/qq-bot
          git pull origin main
          source venv/bin/activate
          pip install -r requirements.txt
          sudo systemctl restart qq-bot
```

### 使用 Webhook

在服务器上创建 webhook 监听器：

```bash
# 安装 webhook 工具
sudo apt install webhook

# 创建 webhook 配置
sudo mkdir -p /etc/webhook
sudo tee /etc/webhook/hooks.json > /dev/null << 'EOF'
[
  {
    "id": "qq-bot-deploy",
    "execute-command": "/opt/qq-bot/scripts/deploy.sh",
    "command-working-directory": "/opt/qq-bot"
  }
]
EOF

# 创建部署脚本
sudo tee /opt/qq-bot/scripts/deploy.sh > /dev/null << 'EOF'
#!/bin/bash
cd /opt/qq-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart qq-bot
EOF

sudo chmod +x /opt/qq-bot/scripts/deploy.sh

# 启动 webhook 服务
sudo systemctl enable webhook
sudo systemctl start webhook
```

## 分支管理策略

### 推荐分支结构

```
main          # 生产环境分支
├── develop   # 开发分支
├── feature/* # 功能分支
└── hotfix/*  # 热修复分支
```

### 分支使用流程

```bash
# 1. 创建功能分支
git checkout -b feature/new-plugin

# 2. 开发功能
# ... 编写代码 ...

# 3. 提交到功能分支
git add .
git commit -m "feat: 添加新插件"
git push origin feature/new-plugin

# 4. 合并到开发分支
git checkout develop
git merge feature/new-plugin
git push origin develop

# 5. 测试通过后合并到主分支
git checkout main
git merge develop
git push origin main
```

## 环境配置管理

### 使用环境变量

```bash
# 开发环境
cp env.example .env.development

# 生产环境
cp env.example .env.production

# 在部署脚本中指定环境
export NODE_ENV=production
```

### 配置文件模板

```bash
# 创建配置模板
cp config.py config.py.template

# 在部署时替换敏感信息
sed -i 's/{{BOT_MASTER_ID}}/123456789/g' config.py
```

## 回滚策略

### 快速回滚

```bash
# 1. 查看提交历史
git log --oneline

# 2. 回滚到指定版本
git reset --hard <commit-hash>

# 3. 强制推送（谨慎使用）
git push --force origin main

# 4. 重启服务
sudo systemctl restart qq-bot
```

### 使用标签回滚

```bash
# 1. 查看标签
git tag -l

# 2. 回滚到指定标签
git checkout v1.0.9

# 3. 创建新分支
git checkout -b rollback-v1.0.9

# 4. 合并到主分支
git checkout main
git merge rollback-v1.0.9
```

## 最佳实践

### 1. 提交规范

```bash
# 使用约定式提交
git commit -m "feat: 添加新功能"
git commit -m "fix: 修复bug"
git commit -m "docs: 更新文档"
git commit -m "style: 代码格式调整"
git commit -m "refactor: 重构代码"
git commit -m "test: 添加测试"
git commit -m "chore: 构建过程或辅助工具的变动"
```

### 2. 版本管理

```bash
# 使用语义化版本
# 主版本号.次版本号.修订号
# 1.0.0 -> 1.1.0 -> 1.1.1

# 创建版本标签
git tag -a v1.1.0 -m "版本 1.1.0"
git push origin v1.1.0
```

### 3. 安全考虑

- 不要在代码中硬编码敏感信息
- 使用环境变量管理配置
- 定期更新依赖包
- 使用 HTTPS 克隆仓库
- 设置 SSH 密钥认证

### 4. 监控和日志

```bash
# 查看服务状态
sudo systemctl status qq-bot

# 查看日志
sudo journalctl -u qq-bot -f

# 查看应用日志
tail -f /opt/qq-bot/bot.log
```

## 故障排除

### 常见问题

1. **Git 拉取失败**
   ```bash
   # 检查网络连接
   ping github.com
   
   # 检查 Git 配置
   git config --list
   ```

2. **权限问题**
   ```bash
   # 修复文件权限
   sudo chown -R $USER:$USER /opt/qq-bot
   chmod +x scripts/*.sh
   ```

3. **依赖安装失败**
   ```bash
   # 更新 pip
   pip install --upgrade pip
   
   # 清理缓存
   pip cache purge
   ```

4. **服务启动失败**
   ```bash
   # 查看详细错误
   sudo journalctl -u qq-bot --no-pager
   
   # 手动测试
   cd /opt/qq-bot
   source venv/bin/activate
   python start.py
   ```

使用 Git 部署可以让您的机器人项目更加专业和可维护！
