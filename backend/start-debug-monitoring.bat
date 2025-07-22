@echo off
REM 快速启动调试和监控环境

echo 🌸 TradingAgents 调试监控环境
echo ===============================

REM 检查虚拟环境
if not exist "env\Scripts\activate.bat" (
    echo ❌ 虚拟环境不存在，正在创建...
    python -m venv env
    call env\Scripts\activate
    pip install -r requirements.txt
    pip install flower
) else (
    echo ✅ 虚拟环境已存在
)

REM 启动 Redis
echo 🔴 启动 Redis...
docker ps | findstr redis >nul
if errorlevel 1 (
    docker run -d --name redis -p 6379:6379 redis:alpine
    echo ✅ Redis 已启动
) else (
    echo ✅ Redis 已运行
)

REM 等待 Redis 启动
timeout /t 3 /nobreak >nul

REM 设置环境变量
set CELERY_BROKER_URL=redis://localhost:6379/1
set CELERY_RESULT_BACKEND=redis://localhost:6379/2
set DATA_SERVICE_URL=http://localhost:8002

echo.
echo 🚀 现在需要在不同终端窗口启动以下服务:
echo.
echo === 终端 1: Data Service ===
echo cd backend\data-service
echo ..\env\Scripts\activate
echo python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
echo.
echo === 终端 2: Task Scheduler ===
echo cd backend\task-scheduler
echo ..\env\Scripts\activate
echo python -m uvicorn api.main:app --host 0.0.0.0 --port 8003 --reload
echo.
echo === 终端 3: Celery Worker ===
echo cd backend\task-scheduler
echo ..\env\Scripts\activate
echo set CELERY_BROKER_URL=redis://localhost:6379/1
echo set CELERY_RESULT_BACKEND=redis://localhost:6379/2
echo celery -A tasks.celery_app worker --loglevel=info --concurrency=1
echo.
echo === 终端 4: Flower 监控 ===
echo cd backend\task-scheduler
echo ..\env\Scripts\activate
echo flower -A tasks.celery_app --port=5555 --broker=redis://localhost:6379/1
echo.
echo === 终端 5: 调试工具 ===
echo cd backend
echo env\Scripts\activate
echo python debug_data_sync.py
echo.

REM 询问是否自动打开新终端
set /p auto_start="是否自动打开新终端窗口？(y/n): "
if /i "%auto_start%"=="y" (
    echo 🚀 正在启动服务...
    
    REM 启动 Data Service
    start "Data Service" cmd /k "cd data-service && ..\env\Scripts\activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload"
    
    REM 等待一下
    timeout /t 2 /nobreak >nul
    
    REM 启动 Task Scheduler
    start "Task Scheduler" cmd /k "cd task-scheduler && ..\env\Scripts\activate && python -m uvicorn api.main:app --host 0.0.0.0 --port 8003 --reload"
    
    REM 等待一下
    timeout /t 2 /nobreak >nul
    
    REM 启动 Celery Worker
    start "Celery Worker" cmd /k "cd task-scheduler && ..\env\Scripts\activate && set CELERY_BROKER_URL=redis://localhost:6379/1 && set CELERY_RESULT_BACKEND=redis://localhost:6379/2 && celery -A tasks.celery_app worker --loglevel=info --concurrency=1"
    
    REM 等待一下
    timeout /t 3 /nobreak >nul
    
    REM 启动 Flower
    start "Flower Monitor" cmd /k "cd task-scheduler && ..\env\Scripts\activate && flower -A tasks.celery_app --port=5555 --broker=redis://localhost:6379/1"
    
    REM 等待一下
    timeout /t 2 /nobreak >nul
    
    REM 启动调试工具
    start "Debug Tool" cmd /k "env\Scripts\activate && python debug_data_sync.py"
    
    echo ✅ 所有服务已启动！
    echo.
    echo 等待 10 秒后自动打开监控界面...
    timeout /t 10 /nobreak >nul
    
    REM 打开监控界面
    start http://localhost:5555
    start http://localhost:8002/docs
    start http://localhost:8003/docs
)

echo.
echo 🌐 监控界面地址:
echo   🌸 Flower 监控: http://localhost:5555
echo   📊 Data Service API: http://localhost:8002/docs
echo   ⏰ Task Scheduler API: http://localhost:8003/docs
echo.
echo 💡 调试提示:
echo   1. 等待所有服务启动完成（约30秒）
echo   2. 访问 Flower 查看 Worker 状态
echo   3. 使用调试工具手动触发任务
echo   4. 在 Flower 中观察任务执行情况
echo.
echo 🛑 停止服务: docker stop redis

pause
