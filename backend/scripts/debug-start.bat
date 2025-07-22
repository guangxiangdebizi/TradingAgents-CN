@echo off
REM TradingAgents 调试启动脚本

echo 🔧 TradingAgents 调试模式启动
echo ================================

REM 检查虚拟环境
if not exist "env\Scripts\activate.bat" (
    echo ❌ 虚拟环境不存在，请先创建虚拟环境
    echo    python -m venv env
    echo    env\Scripts\activate
    echo    pip install -r requirements.txt
    pause
    exit /b 1
)

REM 启动 Redis（如果没有运行）
echo 🔍 检查 Redis 状态...
docker ps | findstr redis >nul
if errorlevel 1 (
    echo 🚀 启动 Redis...
    docker run -d --name redis -p 6379:6379 redis:alpine
    timeout /t 3 /nobreak >nul
) else (
    echo ✅ Redis 已运行
)

REM 设置环境变量
set CELERY_BROKER_URL=redis://localhost:6379/1
set CELERY_RESULT_BACKEND=redis://localhost:6379/2
set DATA_SERVICE_URL=http://localhost:8002
set ANALYSIS_ENGINE_URL=http://localhost:8001

echo.
echo 📋 启动选项:
echo 1. 启动 Data Service (端口 8002)
echo 2. 启动 Task Scheduler (端口 8003)
echo 3. 启动 Celery Worker (调试模式)
echo 4. 启动调试测试工具
echo 5. 启动所有服务 (推荐)
echo.

set /p choice="请选择启动选项 (1-5): "

if "%choice%"=="1" goto start_data_service
if "%choice%"=="2" goto start_task_scheduler
if "%choice%"=="3" goto start_celery_worker
if "%choice%"=="4" goto start_debug_tool
if "%choice%"=="5" goto start_all_services
goto invalid_choice

:start_data_service
echo 🚀 启动 Data Service...
cd data-service
call ..\env\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
goto end

:start_task_scheduler
echo 🚀 启动 Task Scheduler...
cd task-scheduler
call ..\env\Scripts\activate
python -m uvicorn api.main:app --host 0.0.0.0 --port 8003 --reload
goto end

:start_celery_worker
echo 🚀 启动 Celery Worker (调试模式)...
cd task-scheduler
call ..\env\Scripts\activate
celery -A tasks.celery_app worker --loglevel=debug --concurrency=1
goto end

:start_debug_tool
echo 🚀 启动调试测试工具...
call env\Scripts\activate
python debug_data_sync.py
goto end

:start_all_services
echo 🚀 启动所有服务...
echo.
echo 请在不同的终端窗口中运行以下命令:
echo.
echo 终端1 - Data Service:
echo   cd backend\data-service
echo   ..\env\Scripts\activate
echo   python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
echo.
echo 终端2 - Task Scheduler:
echo   cd backend\task-scheduler  
echo   ..\env\Scripts\activate
echo   python -m uvicorn api.main:app --host 0.0.0.0 --port 8003 --reload
echo.
echo 终端3 - Celery Worker:
echo   cd backend\task-scheduler
echo   ..\env\Scripts\activate
echo   set CELERY_BROKER_URL=redis://localhost:6379/1
echo   set CELERY_RESULT_BACKEND=redis://localhost:6379/2
echo   celery -A tasks.celery_app worker --loglevel=debug --concurrency=1
echo.
echo 终端4 - 调试工具:
echo   cd backend
echo   env\Scripts\activate
echo   python debug_data_sync.py
echo.
echo 💡 提示: 启动所有服务后，访问 http://localhost:8002/docs 查看 API 文档
goto end

:invalid_choice
echo ❌ 无效选项
goto end

:end
pause
