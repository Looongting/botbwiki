# PowerShell 虚拟环境激活脚本
Write-Host "激活 Python 虚拟环境..." -ForegroundColor Green
& "venv\Scripts\Activate.ps1"
Write-Host "虚拟环境已激活！" -ForegroundColor Green
Write-Host "现在可以运行: python start.py" -ForegroundColor Yellow


