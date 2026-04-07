@echo off
cd /d "%~dp0"
title PPT Config Tool
cls
echo ========================================
echo   PPT Configuration Tool
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python first:
    echo   https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Check if streamlit is installed
python -m streamlit --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Streamlit not installed, installing now...
    echo.
    python -m pip install streamlit pandas openpyxl xlsxwriter -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    if errorlevel 1 (
        echo.
        echo [ERROR] Installation failed!
        echo.
        echo Please try:
        echo   1. Run as Administrator
        echo   2. Check network connection
        echo   3. Install Python packages manually:
        echo      pip install streamlit pandas openpyxl xlsxwriter
        echo.
        pause
        exit /b 1
    )
    
    echo.
    echo [OK] Installation complete!
    echo.
) else (
    echo [OK] Streamlit detected
    echo.
)

echo Starting Streamlit...
echo.

REM Try different ports if 8501 is busy
for %%p in (8501 8502 8503 8504 8505) do (
    netstat -ano | findstr ":%%p " >nul 2>&1
    if errorlevel 1 (
        set PORT=%%p
        goto :found_port
    )
)

echo [ERROR] No available ports (8501-8505)!
echo Please close other applications using these ports.
pause
exit /b 1

:found_port
echo [OK] Using port %PORT%
echo.
echo Browser will open: http://localhost:%PORT%
echo.
echo Press Ctrl+C to stop
echo.

python -m streamlit run "%~dp0app.py" --server.port %PORT% --server.headless true --server.address localhost
