@echo off
echo ==========================================
echo 🧹 Stopping Chat Agent and Removing Volumes
echo ==========================================

cd /d %~dp0

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker not found. Please start Docker Desktop first.
    pause
    exit /b
)

REM 停止容器并删除 volumes（包括 runtime_data 中的内容）
docker-compose down -v

echo ✅ Chat Agent stopped and volumes removed.
pause
