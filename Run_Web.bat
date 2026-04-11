@echo off
chcp 65001 >nul
cd /d "%~dp0"
title PPT Report Generator v5.0 - Web Interface
cls
echo.
echo ========================================
echo   PPT Report Generator v5.0
echo   Web Interface
echo ========================================
echo.
echo Starting Web Interface...
echo.
echo Access: http://localhost:8501/
echo.
echo Press Ctrl+C to stop
echo.

:: 设置 Clash 代理（如果需要）
set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890

python -m streamlit run scripts\config_tool\app.py --server.port 8501 --server.address localhost
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start web interface
    echo.
    pause
)
