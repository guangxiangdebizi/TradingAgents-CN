@echo off
REM TradingAgents CLI Client Windows启动脚本
setlocal enabledelayedexpansion

REM 简化的消息显示函数
echo.
echo ========================================
echo TradingAgents CLI Client 启动脚本
echo ========================================
echo.

:check_python
REM 检查Python版本
echo 检查Python版本...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Python未安装，请先安装Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo Python版本: !python_version!
goto :eof

:check_dependencies
REM 检查依赖
echo.
echo 检查依赖包...

if not exist "requirements.txt" (
    echo 错误: requirements.txt文件不存在
    pause
    exit /b 1
)

REM 检查是否在虚拟环境中
if "%VIRTUAL_ENV%"=="" (
    echo 警告: 建议在虚拟环境中运行
    set /p continue="是否继续? (y/N): "
    if /i not "!continue!"=="y" exit /b 1
) else (
    echo 虚拟环境: %VIRTUAL_ENV%
)

REM 安装依赖
echo 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖包安装失败
    pause
    exit /b 1
)
echo 依赖包安装完成
goto :eof

:check_backend
REM 检查Backend服务
echo.
echo 检查Backend服务连接...

if "%TRADING_CLI_BACKEND_URL%"=="" (
    set backend_url=http://localhost:8001
) else (
    set backend_url=%TRADING_CLI_BACKEND_URL%
)

curl -s "!backend_url!/health" >nul 2>&1
if errorlevel 1 (
    echo 警告: Backend服务连接失败: !backend_url!
    echo 请确保Backend服务已启动，或设置正确的TRADING_CLI_BACKEND_URL环境变量
) else (
    echo Backend服务连接正常: !backend_url!
)
goto :eof

:create_config
REM 创建配置文件
set config_file=%USERPROFILE%\.trading_cli_config.json

if not exist "!config_file!" (
    echo 创建默认配置文件...

    (
        echo {
        echo   "backend_url": "http://localhost:8000",
        echo   "default_analysis_type": "comprehensive",
        echo   "auto_refresh": true,
        echo   "refresh_interval": 2,
        echo   "max_wait_time": 300,
        echo   "max_debate_rounds": 3,
        echo   "max_risk_rounds": 2,
        echo   "show_progress": true,
        echo   "color_output": true,
        echo   "save_history": true,
        echo   "log_level": "INFO"
        echo }
    ) > "!config_file!"

    echo 配置文件已创建: !config_file!
) else (
    echo 配置文件已存在: !config_file!
)
goto :eof

:show_help
REM 显示帮助信息
echo TradingAgents CLI Client Windows启动脚本
echo.
echo 用法: %~nx0 [选项]
echo.
echo 选项:
echo   -h, --help              显示帮助信息
echo   -c, --check             只检查环境，不启动CLI
echo   -i, --install           安装依赖包
echo   --setup                 完整环境设置
echo.
echo 环境变量:
echo   TRADING_CLI_BACKEND_URL Backend服务URL
echo   TRADING_CLI_LOG_LEVEL   日志级别
echo.
echo 示例:
echo   %~nx0                      启动交互模式
echo   %~nx0 --setup             完整环境设置
pause
exit /b 0

REM 解析命令行参数
set check_only=false
set install_only=false
set setup_mode=false

if "%1"=="-h" goto :show_help
if "%1"=="--help" goto :show_help
if "%1"=="-c" set check_only=true
if "%1"=="--check" set check_only=true
if "%1"=="-i" set install_only=true
if "%1"=="--install" set install_only=true
if "%1"=="--setup" set setup_mode=true

echo TradingAgents CLI Client 启动中...

REM 检查环境
call :check_python
if errorlevel 1 goto :end

if "%install_only%"=="true" (
    call :check_dependencies
    if errorlevel 1 goto :end
    echo 依赖安装完成!
    goto :end
)

if "%setup_mode%"=="true" (
    call :check_dependencies
    if errorlevel 1 goto :end
    call :create_config
    call :check_backend
    echo 环境设置完成!
    goto :end
)

if "%check_only%"=="true" (
    call :check_backend
    echo 环境检查完成!
    goto :end
)

REM 检查Backend连接
call :check_backend

REM 启动CLI
echo.
echo 启动TradingAgents CLI...
python trading_cli.py

:end
echo.
echo 按任意键退出...
pause >nul
