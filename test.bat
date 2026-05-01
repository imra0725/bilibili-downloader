@echo off
chcp 65001 >nul
echo ==========================================
echo    B站视频下载器 - 环境诊断工具
echo ==========================================
echo.

REM Python
echo [1] Python 版本:
python --version 2>nul
if errorlevel 1 (
    echo     X Python 未安装或未添加到 PATH
    echo     请访问 https://www.python.org/downloads/ 安装 Python 3.10+
) else (
    echo     路径: 
    where python 2>nul
)
echo.

REM pip
echo [2] pip 版本:
python -m pip --version 2>nul
if errorlevel 1 (
    echo     X pip 未安装
)
echo.

REM Python packages
echo [3] Python 依赖检查:
python -c "import webview; print('    pywebview:', webview.__version__)" 2>nul || echo     X pywebview 未安装 (pip install pywebview)
python -c "import requests; print('    requests:', requests.__version__)" 2>nul || echo     X requests 未安装 (pip install requests)
python -c "import tkinter; print('    tkinter: OK')" 2>nul || echo     ! tkinter 不可用 (文件夹选择功能将失效)
echo.

REM Node.js
echo [4] Node.js 版本:
node --version 2>nul
if errorlevel 1 (
    echo     X Node.js 未安装 (仅打包时需要)
)
echo.

REM Frontend build
echo [5] 前端构建产物:
if exist "dist\index.html" (
    echo     路径: %CD%\dist\index.html
    echo     大小: 
    dir "dist\index.html" | findstr "index.html"
) else (
    echo     X dist\index.html 不存在，请先运行 npm run build
)
echo.

REM Project structure
echo [6] 项目结构检查:
if exist "backend\main.py" (
    echo     backend\main.py: OK
) else (
    echo     X backend\main.py 不存在
)
if exist "backend\api.py" (
    echo     backend\api.py: OK
) else (
    echo     X backend\api.py 不存在
)
if exist "run.bat" (
    echo     run.bat: OK
) else (
    echo     X run.bat 不存在
)
echo.

echo ==========================================
echo 诊断完成。若上方无 [X] 标记，可直接运行 run.bat
echo ==========================================
pause
