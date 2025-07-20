@echo off
REM TradingAgents Backend 开发环境启动脚本 (Windows)

echo 🚀 启动 TradingAgents Backend 开发环境
echo ========================================

REM 检查是否存在 .env 文件
if not exist ".env" (
    echo ⚠️ 未找到 .env 文件，正在复制示例配置...
    copy .env.example .env
    echo ✅ 已创建 .env 文件，请编辑配置后重新运行
    pause
    exit /b 1
)

REM 检查 Docker 是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未运行，请先启动 Docker
    pause
    exit /b 1
)

REM 检查 Docker Compose 是否可用
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ docker-compose 未安装
    pause
    exit /b 1
)

echo 📦 启动服务...

REM 启动服务
docker-compose up -d

echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 📊 检查服务状态...
docker-compose ps

REM 健康检查
echo 🔍 执行健康检查...

REM 检查 API Gateway
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ❌ API Gateway (8000) - 异常
) else (
    echo ✅ API Gateway (8000) - 健康
)

REM 检查 Analysis Engine
curl -s http://localhost:8001/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Analysis Engine (8001) - 异常
) else (
    echo ✅ Analysis Engine (8001) - 健康
)

REM 检查 Data Service
curl -s http://localhost:8002/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Data Service (8002) - 异常
) else (
    echo ✅ Data Service (8002) - 健康
)

echo.
echo 🎉 Backend 服务启动完成！
echo ========================================
echo 📡 API Gateway:     http://localhost:8000
echo 📊 API 文档:        http://localhost:8000/docs
echo 🔍 Analysis Engine: http://localhost:8001
echo 📈 Data Service:    http://localhost:8002
echo.
echo 📋 常用命令:
echo   查看日志: docker-compose logs -f
echo   停止服务: docker-compose down
echo   重启服务: docker-compose restart
echo.
pause
