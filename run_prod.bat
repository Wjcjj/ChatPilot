@echo off
echo ==========================================
echo 🚀 Starting Chat Agent (Production Mode)
echo ==========================================

cd /d %~dp0

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker not found. Please start Docker Desktop first.
    pause
    exit /b
)

REM 使用生产配置启动，并构建镜像
docker-compose -f docker-compose.yml up --build -d

echo ✅ Chat Agent running in production mode!
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000/docs
pause
