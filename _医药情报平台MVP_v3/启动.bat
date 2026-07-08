@echo off
chcp 65001 >nul
echo ========================================
echo   医药情报平台 - 启动中...
echo ========================================
echo.

cd /d "%~dp0app"

where streamlit >nul 2>nul
if %errorlevel% neq 0 (
    echo [提示] 检测到尚未安装依赖，正在安装 streamlit 和 pandas...
    pip install streamlit pandas
    echo.
    echo [完成] 依赖安装完成，正在启动...
    echo.
)

streamlit run Home.py --server.port 8501

pause
