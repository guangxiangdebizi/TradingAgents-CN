@echo off
REM 自动安装和启动 Flower 监控

echo 🌸 TradingAgents Flower 监控安装启动脚本
echo ==========================================

REM 检查虚拟环境
if not exist "env\Scripts\activate.bat" (
    echo ❌ 虚拟环境不存在，正在创建...
    python -m venv env
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call env\Scripts\activate
if errorlevel 1 (
    echo ❌ 激活虚拟环境失败
    pause
    exit /b 1
)

REM 升级 pip
echo 📦 升级 pip...
python -m pip install --upgrade pip

REM 安装基础依赖
echo 📦 安装基础依赖...
pip install redis celery

REM 尝试安装 Flower
echo 🌸 安装 Flower...
pip install flower
if errorlevel 1 (
    echo ⚠️ 标准安装失败，尝试其他方法...
    
    REM 尝试指定版本
    pip install flower==1.2.0
    if errorlevel 1 (
        echo ⚠️ 指定版本安装失败，尝试 Docker 方式...
        goto docker_flower
    )
)

REM 验证 Flower 安装
echo 🔍 验证 Flower 安装...
flower --version
if errorlevel 1 (
    echo ❌ Flower 安装验证失败，使用 Docker 方式
    goto docker_flower
)

echo ✅ Flower 安装成功！

REM 检查 Redis
echo 🔴 检查 Redis...
docker ps | findstr redis >nul
if errorlevel 1 (
    echo 🚀 启动 Redis...
    docker run -d --name redis -p 6379:6379 redis:alpine
    if errorlevel 1 (
        echo ❌ Redis 启动失败
        pause
        exit /b 1
    )
    timeout /t 3 /nobreak >nul
) else (
    echo ✅ Redis 已运行
)

REM 启动 Flower
echo 🌸 启动 Flower 监控...
cd task-scheduler
flower -A tasks.celery_app --port=5555 --broker=redis://localhost:6379/1 --url_prefix=flower
goto end

:docker_flower
echo 🐳 使用 Docker 启动 Flower...

REM 停止可能存在的 Flower 容器
docker stop flower 2>nul
docker rm flower 2>nul

REM 检查 Redis
docker ps | findstr redis >nul
if errorlevel 1 (
    echo 🚀 启动 Redis...
    docker run -d --name redis -p 6379:6379 redis:alpine
    timeout /t 3 /nobreak >nul
)

REM 启动 Flower 容器
echo 🌸 启动 Flower 容器...
docker run -d --name flower -p 5555:5555 ^
  -e CELERY_BROKER_URL=redis://host.docker.internal:6379/1 ^
  mher/flower:1.2.0

if errorlevel 1 (
    echo ❌ Docker Flower 启动失败
    pause
    exit /b 1
)

echo ✅ Flower 容器启动成功！

:end
echo.
echo 🎉 Flower 监控已启动！
echo.
echo 🌐 访问地址: http://localhost:5555
echo.
echo 💡 提示:
echo   - 确保 Celery Worker 正在运行
echo   - 确保 Redis 服务可用
echo   - 在 Flower 中可以监控所有任务状态
echo.

REM 等待几秒后自动打开浏览器
echo ⏳ 3秒后自动打开 Flower 监控界面...
timeout /t 3 /nobreak >nul
start http://localhost:5555

echo.
echo 🔧 如需启动其他服务，请运行:
echo   - Data Service: cd data-service ^&^& python -m uvicorn app.main:app --port 8002 --reload
echo   - Task Scheduler: cd task-scheduler ^&^& python -m uvicorn api.main:app --port 8003 --reload  
echo   - Celery Worker: cd task-scheduler ^&^& celery -A tasks.celery_app worker --loglevel=info
echo.
echo 🛑 停止服务:
echo   - 停止 Flower: Ctrl+C (如果是本地安装) 或 docker stop flower (如果是容器)
echo   - 停止 Redis: docker stop redis

pause
