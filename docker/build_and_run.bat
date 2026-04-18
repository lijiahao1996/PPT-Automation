@echo off
chcp 65001 >nul
echo ========================================
echo   Docker 构建和启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查 Docker 是否运行...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker 未运行，请先启动 Docker Desktop
    pause
    exit /b 1
)
echo [OK] Docker 运行正常
echo.

echo [2/3] 构建 Docker 镜像...
docker-compose build
if %errorlevel% neq 0 (
    echo [ERROR] 镜像构建失败
    pause
    exit /b 1
)
echo [OK] 镜像构建成功
echo.

echo [3/3] 启动容器...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] 容器启动失败
    pause
    exit /b 1
)
echo [OK] 容器启动成功
echo.

echo ========================================
echo   启动完成！
echo ========================================
echo.
echo 访问地址: http://localhost:8501
echo.
echo 查看日志: docker-compose logs -f
echo 停止服务: docker-compose down
echo.
pause
