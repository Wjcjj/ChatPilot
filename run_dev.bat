@echo off
echo ==========================================
echo 🚀 Starting Chat Agent (Development Mode)
echo ==========================================

REM 切换到项目根目录
cd /d %~dp0

REM 确保 Docker 可用
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker not found. Please start Docker Desktop first.
    pause
    exit /b
)

REM 使用开发配置启动
docker-compose -f docker-compose.dev.yml up

pause
