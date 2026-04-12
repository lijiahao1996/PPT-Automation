@echo off
chcp 65001 >nul
cd /d "%~dp0"
title PPT Report Generator v6.0

echo.
echo ========================================
echo   PPT Report Generator v6.0
echo   Streamlit Web Interface
echo ========================================
echo.
echo Starting web interface...
echo.
echo Access: http://localhost:8501/
echo.
echo Press Ctrl+C to stop
echo.

python -m streamlit run app.py --server.port 8501 --server.address localhost

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start web interface
    echo.
    echo Please install dependencies:
    echo   pip install -r ..\..\requirements.txt
    echo.
    pause
)
