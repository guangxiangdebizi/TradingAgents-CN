@echo off
REM TradingAgents 后端微服务测试启动脚本

echo ========================================
echo TradingAgents 后端微服务测试工具
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或不在PATH中
    pause
    exit /b 1
)

REM 检查PowerShell
powershell -Command "Get-Host" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ PowerShell不可用
    pause
    exit /b 1
)

echo 请选择测试方式:
echo 1. Python完整测试 (推荐)
echo 2. PowerShell快速测试
echo 3. 仅健康检查
echo 4. 仅数据服务测试
echo 5. 仅LLM服务测试
echo 6. 仅网关测试
echo.

set /p choice=请输入选择 (1-6): 

if "%choice%"=="1" (
    echo 🚀 启动Python完整测试...
    cd /d "%~dp0"
    python test_microservices.py
) else if "%choice%"=="2" (
    echo 🚀 启动PowerShell快速测试...
    cd /d "%~dp0"
    powershell -ExecutionPolicy Bypass -File test_microservices.ps1 -TestType all
) else if "%choice%"=="3" (
    echo 🚀 启动健康检查测试...
    cd /d "%~dp0"
    powershell -ExecutionPolicy Bypass -File test_microservices.ps1 -TestType health
) else if "%choice%"=="4" (
    echo 🚀 启动数据服务测试...
    cd /d "%~dp0"
    powershell -ExecutionPolicy Bypass -File test_microservices.ps1 -TestType data
) else if "%choice%"=="5" (
    echo 🚀 启动LLM服务测试...
    cd /d "%~dp0"
    powershell -ExecutionPolicy Bypass -File test_microservices.ps1 -TestType llm
) else if "%choice%"=="6" (
    echo 🚀 启动网关测试...
    cd /d "%~dp0"
    powershell -ExecutionPolicy Bypass -File test_microservices.ps1 -TestType gateway
) else (
    echo ❌ 无效选择
    pause
    exit /b 1
)

echo.
echo 测试完成! 查看 ../docs/test/ 目录下的测试报告
pause
