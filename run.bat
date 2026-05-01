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

REM Clean pycache to avoid stale compiled code
echo [2/2] 清理旧缓存...
if exist "backend\__pycache__" (
    rmdir /s /q "backend\__pycache__" 2>nul
)

echo 启动应用...
echo.
REM -u = unbuffered output so errors show immediately
python -u backend\main.py
if errorlevel 1 (
    echo.
    echo [错误] 应用异常退出 (代码: %errorlevel%)
    echo 如果窗口一闪而过，请运行 test.bat 检查环境
    pause
    exit /b 1
)
