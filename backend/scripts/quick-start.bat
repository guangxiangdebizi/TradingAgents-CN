@echo off
REM TradingAgents 后端系统快速启动脚本 (Windows)

setlocal enabledelayedexpansion

echo 🚀 TradingAgents 后端系统快速启动
echo ========================================

REM 检查是否在正确的目录
if not exist "docker-compose.yml" (
    echo ❌ 请在 backend 目录下运行此脚本
    pause
    exit /b 1
)

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
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

REM 检查环境变量文件
if not exist ".env" (
    echo ⚠️ .env 文件不存在，正在创建...
    copy .env.example .env
    echo ✅ 已创建 .env 文件，请编辑配置后重新运行
    echo 主要需要配置的API密钥：
    echo   - DASHSCOPE_API_KEY
    echo   - TUSHARE_TOKEN
    echo   - DEEPSEEK_API_KEY (可选)
    pause
    exit /b 1
)

echo 📦 检查系统环境...

REM 检查 Docker 是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未运行，请启动 Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker 环境检查通过

echo.
echo 请选择镜像源：
echo 1) 官方镜像源 (默认，海外用户推荐)
echo 2) 国内镜像源 (国内用户推荐)
set /p mirror_choice="请输入选择 (1-2): "

set CHINA_MIRROR=
if "%mirror_choice%"=="2" (
    echo 📊 使用国内镜像源...
    set CHINA_MIRROR=-f docker-compose.china.yml
) else (
    echo 📊 使用官方镜像源...
)

echo.
echo 请选择启动模式：
echo 1) 生产模式 (默认)
echo 2) 开发模式 (支持热重载)
echo 3) 开发模式 + 管理工具
set /p choice="请输入选择 (1-3): "

if "%choice%"=="2" (
    echo 📊 启动开发模式...
    set COMPOSE_CMD=docker-compose -f docker-compose.yml %CHINA_MIRROR% -f docker-compose.dev.yml
) else if "%choice%"=="3" (
    echo 📊 启动开发模式 + 管理工具...
    set COMPOSE_CMD=docker-compose -f docker-compose.yml %CHINA_MIRROR% -f docker-compose.dev.yml --profile dev-tools
) else (
    echo 📊 启动生产模式...
    set COMPOSE_CMD=docker-compose -f docker-compose.yml %CHINA_MIRROR%
)

echo.
echo 🛑 停止现有服务...
%COMPOSE_CMD% down >nul 2>&1

echo 📥 拉取Docker镜像（使用国内镜像源）...
echo 正在从阿里云镜像源拉取镜像，请稍候...
%COMPOSE_CMD% pull

echo 🔨 构建服务镜像...
%COMPOSE_CMD% build

echo 🚀 启动服务...
%COMPOSE_CMD% up -d

echo ⏳ 等待服务启动完成...
timeout /t 15 /nobreak >nul

echo 🔍 检查服务状态...

REM 检查服务健康状态
set services_ok=0
set total_services=0

echo 检查 API Gateway...
set /a total_services+=1
curl -s http://localhost:8000/health >nul 2>&1
if not errorlevel 1 (
    echo ✅ API Gateway 启动成功
    set /a services_ok+=1
) else (
    echo ❌ API Gateway 启动失败
)

echo 检查 Analysis Engine...
set /a total_services+=1
curl -s http://localhost:8001/health >nul 2>&1
if not errorlevel 1 (
    echo ✅ Analysis Engine 启动成功
    set /a services_ok+=1
) else (
    echo ❌ Analysis Engine 启动失败
)

echo 检查 Data Service...
set /a total_services+=1
curl -s http://localhost:8002/health >nul 2>&1
if not errorlevel 1 (
    echo ✅ Data Service 启动成功
    set /a services_ok+=1
) else (
    echo ❌ Data Service 启动失败
)

echo 检查 Task API...
set /a total_services+=1
curl -s http://localhost:8003/health >nul 2>&1
if not errorlevel 1 (
    echo ✅ Task API 启动成功
    set /a services_ok+=1
) else (
    echo ❌ Task API 启动失败
)

echo 检查 Flower...
set /a total_services+=1
curl -s http://localhost:5555 >nul 2>&1
if not errorlevel 1 (
    echo ✅ Flower 启动成功
    set /a services_ok+=1
) else (
    echo ❌ Flower 启动失败
)

echo.
echo ========================================

if %services_ok% equ %total_services% (
    echo 🎉 所有服务启动成功！
    echo.
    echo 📊 服务访问地址：
    echo   API Gateway:     http://localhost:8000
    echo   API 文档:        http://localhost:8000/docs
    echo   Analysis Engine: http://localhost:8001
    echo   Data Service:    http://localhost:8002
    echo   Task API:        http://localhost:8003
    echo   Flower 监控:     http://localhost:5555
    echo   MinIO 控制台:    http://localhost:9001
    
    if "%choice%"=="3" (
        echo   MongoDB 管理:    http://localhost:8081
        echo   Redis 管理:      http://localhost:8082
    )
    
    echo.
    echo 🔧 常用命令：
    echo   查看日志: docker-compose logs -f
    echo   停止服务: docker-compose down
    echo   重启服务: docker-compose restart
    echo   查看状态: docker-compose ps
    
    echo.
    echo 🧪 快速测试：
    echo   健康检查: curl http://localhost:8000/health
    echo   股票信息: curl http://localhost:8000/api/stock/info/000858
    echo   运行测试: python scripts/test-api.py
    
) else (
    echo ❌ 部分服务启动失败 (%services_ok%/%total_services%)
    echo.
    echo 🔍 故障排查：
    echo   查看日志: docker-compose logs service-name
    echo   查看状态: docker-compose ps
    echo   重启服务: docker-compose restart service-name
)

echo.
echo 📚 更多信息请查看: GETTING_STARTED.md
echo.

REM 询问是否打开浏览器
set /p open_browser="是否打开浏览器查看API文档？(y/N): "
if /i "%open_browser%"=="y" (
    start http://localhost:8000/docs
    start http://localhost:5555
)

echo 按任意键退出...
pause >nul
