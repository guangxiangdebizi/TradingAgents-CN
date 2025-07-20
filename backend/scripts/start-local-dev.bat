@echo off
REM TradingAgents 本地开发启动脚本

echo 🚀 TradingAgents 本地开发模式启动
echo ========================================

REM 检查是否在正确的目录
if not exist "docker-compose.simple.yml" (
    echo ❌ 请在 backend 目录下运行此脚本
    pause
    exit /b 1
)

REM 检查 Docker 是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未运行，请启动 Docker Desktop
    pause
    exit /b 1
)

echo 📦 启动基础服务（MongoDB, Redis, MinIO）...
docker-compose -f docker-compose.simple.yml up -d

echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

echo 🔍 检查基础服务状态...
docker exec tradingagents-mongodb mongosh --eval "db.hello()" >nul 2>&1
if not errorlevel 1 (
    echo ✅ MongoDB 运行正常
) else (
    echo ❌ MongoDB 启动失败
)

docker exec tradingagents-redis redis-cli ping >nul 2>&1
if not errorlevel 1 (
    echo ✅ Redis 运行正常
) else (
    echo ❌ Redis 启动失败
)

curl -s http://localhost:9001 >nul 2>&1
if not errorlevel 1 (
    echo ✅ MinIO 运行正常
) else (
    echo ❌ MinIO 启动失败
)

echo.
echo 🌐 服务访问地址：
echo   MongoDB:     localhost:27017
echo   Redis:       localhost:6379
echo   MinIO 控制台: http://localhost:9001
echo   用户名/密码:  admin/tradingagents123

echo.
echo 📋 下一步操作：
echo   1. 激活虚拟环境: env\Scripts\activate
echo   2. 配置环境变量: 编辑 .env 文件
echo   3. 启动应用服务: 
echo      cd data-service
echo      python app/main.py
echo.
echo   详细说明请查看: LOCAL_DEVELOPMENT.md

echo.
echo 🔧 常用命令：
echo   停止基础服务: docker-compose -f docker-compose.simple.yml down
echo   查看服务日志: docker-compose -f docker-compose.simple.yml logs
echo   查看容器状态: docker ps

echo.
pause
