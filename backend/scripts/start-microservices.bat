@echo off
REM TradingAgents 微服务架构启动脚本 (Windows)

setlocal enabledelayedexpansion

echo 🚀 TradingAgents 微服务架构启动脚本
echo ======================================

REM 检查 Docker 和 Docker Compose
echo [INFO] 检查依赖...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker 未安装，请先安装 Docker Desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose 未安装，请先安装 Docker Compose
    pause
    exit /b 1
)

echo [SUCCESS] 依赖检查通过

REM 创建必要的目录
echo [INFO] 创建必要的目录...
if not exist "logs" mkdir logs
if not exist "data\mongodb" mkdir data\mongodb
if not exist "data\redis" mkdir data\redis
if not exist "data\celery" mkdir data\celery
echo [SUCCESS] 目录创建完成

REM 启动基础设施服务
echo [INFO] 启动基础设施服务 (Redis, MongoDB)...
docker-compose -f docker-compose.microservices.yml up -d redis mongodb

REM 等待服务启动
echo [INFO] 等待基础设施服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
docker-compose -f docker-compose.microservices.yml ps redis | findstr "Up" >nul
if errorlevel 1 (
    echo [ERROR] Redis 启动失败
    pause
    exit /b 1
) else (
    echo [SUCCESS] Redis 启动成功
)

docker-compose -f docker-compose.microservices.yml ps mongodb | findstr "Up" >nul
if errorlevel 1 (
    echo [ERROR] MongoDB 启动失败
    pause
    exit /b 1
) else (
    echo [SUCCESS] MongoDB 启动成功
)

REM 启动微服务
echo [INFO] 启动微服务...

echo [INFO] 启动 Data Service...
docker-compose -f docker-compose.microservices.yml up -d data-service
timeout /t 5 /nobreak >nul

echo [INFO] 启动 Analysis Engine...
docker-compose -f docker-compose.microservices.yml up -d analysis-engine
timeout /t 5 /nobreak >nul

echo [INFO] 启动 Task Scheduler...
docker-compose -f docker-compose.microservices.yml up -d task-scheduler
timeout /t 5 /nobreak >nul

echo [INFO] 启动 API Gateway...
docker-compose -f docker-compose.microservices.yml up -d api-gateway
timeout /t 5 /nobreak >nul

echo [SUCCESS] 微服务启动完成

REM 启动 Celery 服务
echo [INFO] 启动 Celery 服务...

echo [INFO] 启动 Celery Worker...
docker-compose -f docker-compose.microservices.yml up -d celery-worker
timeout /t 3 /nobreak >nul

echo [INFO] 启动 Celery Beat...
docker-compose -f docker-compose.microservices.yml up -d celery-beat
timeout /t 3 /nobreak >nul

echo [SUCCESS] Celery 服务启动完成

REM 启动监控服务
echo [INFO] 启动监控服务...
docker-compose -f docker-compose.microservices.yml up -d flower
echo [SUCCESS] 监控服务启动完成

REM 检查服务状态
echo [INFO] 检查服务状态...
echo.
echo === 服务状态 ===
docker-compose -f docker-compose.microservices.yml ps

echo.
echo === 服务访问地址 ===
echo 🌐 API Gateway:     http://localhost:8000
echo 📊 Data Service:    http://localhost:8002
echo 🤖 Analysis Engine: http://localhost:8001
echo ⏰ Task Scheduler:  http://localhost:8003
echo 🌸 Flower Monitor:  http://localhost:5555
echo 🍃 MongoDB Admin:   http://localhost:8081
echo 🔴 Redis Commander: http://localhost:8082
echo.
echo === API 文档 ===
echo 📚 API Gateway Docs:     http://localhost:8000/docs
echo 📚 Data Service Docs:    http://localhost:8002/docs
echo 📚 Analysis Engine Docs: http://localhost:8001/docs
echo 📚 Task Scheduler Docs:  http://localhost:8003/docs

echo.
echo [SUCCESS] 🎉 TradingAgents 微服务架构启动完成！
echo.
echo 💡 提示：
echo    - 使用 'docker-compose -f docker-compose.microservices.yml logs -f' 查看日志
echo    - 使用 'docker-compose -f docker-compose.microservices.yml down' 停止所有服务
echo    - 使用 'docker-compose -f docker-compose.microservices.yml restart ^<service^>' 重启特定服务

pause
