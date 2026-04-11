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
echo 使用说明:
echo 1. Web 界面模式：python -m streamlit run scripts\config_tool\app.py --server.port 8501
echo 2. 直接生成模式：python scripts\generate_report.py [模板] [输出]
echo.
echo 示例:
echo   python scripts\generate_report.py 报告模板.pptx 我的报告.pptx
echo.
echo 按任意键退出...
pause >nul
