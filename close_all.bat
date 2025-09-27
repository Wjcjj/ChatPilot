@echo off
echo ==========================================
echo 🛑 Stopping all Chat Agent containers
echo ==========================================

cd /d %~dp0

docker-compose -f docker-compose.yml down
docker-compose -f docker-compose.dev.yml down

echo ✅ All Chat Agent containers stopped.
pause
