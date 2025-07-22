@echo off
REM TradingAgents 监控环境启动脚本

echo 🌸 TradingAgents 监控环境启动
echo ================================

REM 检查 Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker 检查通过

REM 启动基础设施
echo 🚀 启动基础设施服务...
docker-compose -f docker-compose.microservices.yml up -d redis mongodb

REM 等待服务启动
echo ⏳ 等待基础设施启动...
timeout /t 5 /nobreak >nul

REM 启动微服务
echo 🚀 启动微服务...
docker-compose -f docker-compose.microservices.yml up -d data-service task-scheduler

REM 等待微服务启动
echo ⏳ 等待微服务启动...
timeout /t 10 /nobreak >nul

REM 启动 Celery 服务
echo 🚀 启动 Celery 服务...
docker-compose -f docker-compose.microservices.yml up -d celery-worker celery-beat

REM 等待 Celery 启动
echo ⏳ 等待 Celery 启动...
timeout /t 5 /nobreak >nul

REM 启动监控服务
echo 🌸 启动 Flower 监控...
docker-compose -f docker-compose.microservices.yml up -d flower

REM 启动数据库管理工具
echo 🍃 启动 MongoDB Express...
docker-compose -f docker-compose.microservices.yml up -d mongo-express

echo 🔴 启动 Redis Commander...
docker-compose -f docker-compose.microservices.yml up -d redis-commander

REM 等待所有服务启动
echo ⏳ 等待所有服务启动完成...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 📋 检查服务状态...
docker-compose -f docker-compose.microservices.yml ps

echo.
echo 🎉 监控环境启动完成！
echo.
echo === 🌐 监控界面访问地址 ===
echo 🌸 Flower (Celery监控):    http://localhost:5555
echo 🍃 MongoDB Express:        http://localhost:8081
echo 🔴 Redis Commander:        http://localhost:8082
echo.
echo === 📚 API 文档地址 ===
echo 🌐 API Gateway:            http://localhost:8000/docs
echo 📊 Data Service:           http://localhost:8002/docs
echo ⏰ Task Scheduler:         http://localhost:8003/docs
echo.
echo === 🔧 调试工具 ===
echo 💡 运行调试工具: python debug_data_sync.py
echo 💡 监控 Celery: python scripts\monitor_celery.py
echo.
echo 🚀 现在可以开始调试定时同步数据了！

REM 询问是否打开监控界面
set /p open_browser="是否自动打开监控界面？(y/n): "
if /i "%open_browser%"=="y" (
    echo 🌐 正在打开监控界面...
    start http://localhost:5555
    start http://localhost:8081
    start http://localhost:8082
    start http://localhost:8000/docs
)

echo.
echo 💡 提示:
echo   - 使用 Flower 监控任务执行状态
echo   - 使用 MongoDB Express 查看数据存储
echo   - 使用 Redis Commander 查看缓存数据
echo   - 使用 API 文档测试接口功能
echo.
echo   停止所有服务: docker-compose -f docker-compose.microservices.yml down

pause
