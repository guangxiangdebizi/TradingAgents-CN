@echo off
REM TradingAgents CLI Client 简单启动脚本

echo.
echo ========================================
echo TradingAgents CLI Client 启动脚本
echo ========================================
echo.

REM 检查Python
echo 检查Python版本...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Python未安装，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo.

REM 检查requirements.txt
if not exist "requirements.txt" (
    echo 错误: requirements.txt文件不存在
    echo 请确保在正确的目录中运行此脚本
    pause
    exit /b 1
)

REM 安装依赖
echo 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖包安装失败
    echo 请检查网络连接或Python环境
    pause
    exit /b 1
)

echo.
echo 依赖包安装完成!
echo.

REM 检查app模块
if not exist "app" (
    echo 错误: app模块不存在
    echo 请确保在正确的目录中运行此脚本
    pause
    exit /b 1
)

REM 启动CLI
echo 启动TradingAgents CLI...
echo.
echo 使用标准Python模块启动方式...
python -m app

echo.
echo 程序已退出
pause
