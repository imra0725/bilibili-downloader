@echo off
chcp 65001 >nul
echo ==========================================
echo    B站视频下载器 - Windows 打包脚本
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

REM Check if Node.js is installed (for frontend build)
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

REM Install Python dependencies
echo [1/4] 安装 Python 依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] Python依赖安装失败
    pause
    exit /b 1
)

REM Install frontend dependencies and build
echo [2/4] 构建前端界面...
cd /d "%~dp0"
call npm install
if errorlevel 1 (
    echo [错误] npm install 失败
    pause
    exit /b 1
)

call npm run build
if errorlevel 1 (
    echo [错误] 前端构建失败
    pause
    exit /b 1
)

REM Install PyInstaller if not present
echo [3/4] 检查 PyInstaller...
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo 安装 PyInstaller...
    pip install pyinstaller
)

REM Build executable
echo [4/4] 打包可执行文件...
pyinstaller --noconfirm --onefile --windowed --name "B站视频下载器" ^
    --add-data "dist;dist" ^
    --add-data "backend;backend" ^
    --hidden-import backend.bilibili_api ^
    --hidden-import backend.download_manager ^
    --hidden-import backend.database ^
    --hidden-import backend.api ^
    --hidden-import backend ^
    --hidden-import requests ^
    --hidden-import urllib3 ^
    --hidden-import certifi ^
    --hidden-import charset_normalizer ^
    --hidden-import idna ^
    --collect-all requests ^
    backend\main.py

if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo ==========================================
echo    打包完成！
echo    可执行文件位于: dist\B站视频下载器.exe
echo ==========================================
pause
