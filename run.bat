@echo off
chcp 65001 >nul
echo [B站视频下载器] 正在启动...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+ 并添加到 PATH
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Install dependencies if needed
echo [1/2] 检查依赖...
python -c "import webview, requests" >nul 2>&1
if errorlevel 1 (
    echo 正在安装 Python 依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [2/2] 启动应用...
python backend\main.py
if errorlevel 1 (
    echo.
    echo [错误] 应用异常退出
    pause
    exit /b 1
)
