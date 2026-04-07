@echo off
chcp 65001 >nul
cd /d "%~dp0"
title FanRuan PPT Report Generator v4.5
cls
echo.
echo ========================================
echo   FanRuan PPT Report Generator v4.5
echo ========================================
echo.
echo Starting...
echo.
powershell -ExecutionPolicy Bypass -NoProfile -File "Run.ps1"
if errorlevel 1 (
    echo.
    echo [ERROR] Execution failed, check logs
    echo.
    pause
)
