@echo off
chcp 65001 >nul
echo ==========================================
echo    B站视频下载器 - 诊断工具
echo ==========================================
echo.

REM Python
echo [1] Python:
python --version 2>nul
if errorlevel 1 (
    echo     X Python 未安装或未添加到 PATH
    echo     请访问 https://www.python.org/downloads/ 安装 Python 3.10+
    pause
    exit /b 1
)

REM Python packages
echo.
echo [2] Python依赖:
python -c "import webview; print('     pywebview OK -', webview.__version__)" 2>nul || echo     X pywebview 未安装: pip install pywebview
python -c "import requests; print('     requests OK -', requests.__version__)" 2>nul || echo     X requests 未安装: pip install requests

REM Check for ffmpeg
echo.
echo [3] ffmpeg (用于合并DASH格式视频+音频):
ffmpeg -version 2>nul | findstr "ffmpeg version" || echo     ! ffmpeg 未安装 (DASH格式视频将无音频)

REM Frontend
echo.
echo [4] 前端构建产物:
if exist "dist\index.html" (
    echo     dist\index.html: OK
    for %%F in ("dist\index.html") do echo     大小: %%~zF bytes
) else (
    echo     X dist\index.html 不存在!
    echo       如果看到此错误，请先运行: npm install ^&^& npm run build
)

REM Backend
echo.
echo [5] 后端文件:
if exist "backend\main.py" (echo     backend\main.py: OK) else (echo     X 缺失)
if exist "backend\api.py" (echo     backend\api.py: OK) else (echo     X 缺失)
if exist "backend\bilibili_api.py" (echo     backend\bilibili_api.py: OK) else (echo     X 缺失)

REM Pycache check
echo.
echo [6] 清理旧缓存:
if exist "backend\__pycache__" (
    echo     ! 发现 backend\__pycache__ - 正在清理...
    rmdir /s /q "backend\__pycache__"
    echo     已清理
) else (
    echo     无旧缓存 (OK)
)

echo.
echo ==========================================
echo 环境检查完成。如果无 [X] 标记，可以运行 run.bat
echo ==========================================
pause
