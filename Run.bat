@echo off
chcp 65001 >nul
cd /d "%~dp0"
title PPT Report Generator v5.0
cls
echo.
echo ========================================
echo   PPT Report Generator v5.0
echo ========================================
echo.
echo Starting Web Interface...
echo.
echo Access: http://localhost:8501/
echo.
echo Press Ctrl+C to stop
echo.
python -m streamlit run scripts\config_tool\app.py --server.port 8501 --server.address localhost
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start web interface
    echo.
    pause
)
