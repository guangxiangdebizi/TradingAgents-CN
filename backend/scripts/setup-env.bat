@echo off
REM 设置本地开发环境变量

echo 🔧 设置 TradingAgents 本地开发环境变量
echo ========================================

REM 设置 Python 路径
set PYTHONPATH=%cd%\..\..
echo ✅ PYTHONPATH=%PYTHONPATH%

REM 设置数据库连接
set MONGODB_URL=mongodb://admin:tradingagents123@localhost:27017/tradingagents?authSource=admin
set REDIS_URL=redis://localhost:6379
echo ✅ 数据库连接已配置

REM 设置服务 URL
set DATA_SERVICE_URL=http://localhost:8002
set ANALYSIS_ENGINE_URL=http://localhost:8001
set TASK_API_URL=http://localhost:8003
echo ✅ 服务 URL 已配置

REM 设置调试模式
set DEBUG=true
set LOG_LEVEL=DEBUG
echo ✅ 调试模式已启用

echo.
echo 📋 当前环境变量：
echo   PYTHONPATH=%PYTHONPATH%
echo   MONGODB_URL=%MONGODB_URL%
echo   REDIS_URL=%REDIS_URL%
echo   DATA_SERVICE_URL=%DATA_SERVICE_URL%
echo   ANALYSIS_ENGINE_URL=%ANALYSIS_ENGINE_URL%
echo   DEBUG=%DEBUG%

echo.
echo 🚀 现在可以启动应用服务：
echo   cd data-service
echo   python app/main.py
echo.
echo   cd analysis-engine  
echo   python app/main.py
echo.
echo   cd api-gateway
echo   python app/main.py

echo.
echo 💡 提示：请确保已经激活虚拟环境并安装了依赖包
echo   env\Scripts\activate
echo   pip install -r requirements.txt
