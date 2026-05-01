#Requires -Version 5.1
$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   B站视频下载器 - Windows 打包脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[错误] 未检测到 Python，请先安装 Python 3.10+" -ForegroundColor Red
    pause
    exit 1
}

# Check Node.js
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Host "[错误] 未检测到 Node.js，请先安装 Node.js 18+" -ForegroundColor Red
    pause
    exit 1
}

# Install Python dependencies
Write-Host "[1/4] 安装 Python 依赖..." -ForegroundColor Yellow
& python -m pip install -r (Join-Path $PSScriptRoot ".." "requirements.txt")
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] Python依赖安装失败" -ForegroundColor Red
    pause
    exit 1
}

# Build frontend
Write-Host "[2/4] 构建前端界面..." -ForegroundColor Yellow
$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Push-Location $projectRoot
& npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] npm install 失败" -ForegroundColor Red
    pause
    exit 1
}

& npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] 前端构建失败" -ForegroundColor Red
    pause
    exit 1
}
Pop-Location

# Check PyInstaller
Write-Host "[3/4] 检查 PyInstaller..." -ForegroundColor Yellow
$pyi = Get-Command pyinstaller -ErrorAction SilentlyContinue
if (-not $pyi) {
    Write-Host "安装 PyInstaller..." -ForegroundColor Yellow
    & python -m pip install pyinstaller
}

# Build executable
Write-Host "[4/4] 打包可执行文件..." -ForegroundColor Yellow
$mainPy = Join-Path $projectRoot "backend" "main.py"
& pyinstaller --noconfirm --onefile --windowed --name "B站视频下载器" `
    --add-data "dist;dist" `
    --add-data "backend;backend" `
    --hidden-import backend.bilibili_api `
    --hidden-import backend.download_manager `
    --hidden-import backend.database `
    --hidden-import backend.api `
    --hidden-import backend `
    --hidden-import requests `
    --hidden-import urllib3 `
    --hidden-import certifi `
    --hidden-import charset_normalizer `
    --hidden-import idna `
    --collect-all requests `
    $mainPy

if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] 打包失败" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "   打包完成！" -ForegroundColor Green
Write-Host "   可执行文件位于: dist\B站视频下载器.exe" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
pause
