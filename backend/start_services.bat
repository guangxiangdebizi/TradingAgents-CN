@echo off
echo ========================================
echo Backend微服务启动脚本
echo ========================================

echo.
echo 检查虚拟环境...
if not exist "..\env\Scripts\activate.bat" (
    echo ❌ 虚拟环境不存在，请先创建虚拟环境
    pause
    exit /b 1
)

echo ✅ 虚拟环境已找到

echo.
echo 检查配置文件...
if not exist ".backend_env" (
    echo ❌ 配置文件 .backend_env 不存在
    pause
    exit /b 1
)

echo ✅ 配置文件已找到

echo.
echo 🚀 开始启动微服务...
echo.
echo 请按照以下顺序在新的终端窗口中启动服务：
echo.

echo 1. Data Service (端口 8002):
echo    cd backend\data-service
echo    python -m app.main
echo.

echo 2. Analysis Engine (端口 8001):
echo    cd backend\analysis-engine  
echo    python -m app.main
echo.

echo 3. LLM Service (端口 8004):
echo    cd backend\llm-service
echo    python -m app.main
echo.

echo 4. Memory Service (端口 8006):
echo    cd backend\memory-service
echo    python -m app.main
echo.

echo 5. Agent Service (端口 8008):
echo    cd backend\agent-service
echo    python -m app.main
echo.

echo 6. API Gateway (端口 8000) - 最后启动:
echo    cd backend\api-gateway
echo    python -m app.main
echo.

echo ========================================
echo 启动完成后，运行以下命令检查服务状态：
echo python check_services.py
echo ========================================

pause
