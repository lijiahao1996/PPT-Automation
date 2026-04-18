@echo off
chcp 65001 >nul

echo.
echo ========================================
echo   PPT Report Generator v6.0
echo   Local Debug Mode
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Checking dependencies...
python -m pip install -r requirements.txt -q

echo.
echo [OK] Starting web interface...
echo.
echo Access: http://localhost:8501/
echo.
echo Press Ctrl+C to stop
echo.

python -m streamlit run scripts/config_tool/app.py --server.port 8501 --server.address localhost

pause
