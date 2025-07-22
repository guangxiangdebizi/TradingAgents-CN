# TradingAgents 后端微服务测试脚本 (PowerShell版本)

param(
    [string]$TestType = "all",  # all, health, data, llm, analysis, gateway, integration
    [string]$OutputFile = ""
)

# 如果没有指定输出文件，使用默认路径
if ([string]::IsNullOrEmpty($OutputFile)) {
    $OutputFile = "../docs/test/test_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
}

# 配置
$BaseUrls = @{
    "api_gateway" = "http://localhost:8000"
    "analysis_engine" = "http://localhost:8001"
    "data_service" = "http://localhost:8002"
    "task_scheduler" = "http://localhost:8003"
    "llm_service" = "http://localhost:8004"
    "memory_service" = "http://localhost:8006"
    "agent_service" = "http://localhost:8008"
}

$TestStocks = @("000001", "600519", "000002")
$Results = @()

# 辅助函数
function Write-TestLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "INFO" { "White" }
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        default { "White" }
    }
    Write-Host "[$timestamp] $Message" -ForegroundColor $color
}

function Record-TestResult {
    param(
        [string]$TestName,
        [bool]$Passed,
        [string]$Message,
        [hashtable]$Details = @{}
    )
    
    $script:Results += @{
        test_name = $TestName
        passed = $Passed
        message = $Message
        details = $Details
        timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
    }
}

function Test-ServiceHealth {
    param([string]$ServiceName, [string]$BaseUrl)
    
    try {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get -TimeoutSec 10
        $stopwatch.Stop()
        
        if ($response.success -eq $true) {
            Record-TestResult -TestName "Health-$ServiceName" -Passed $true -Message "服务正常 ($($stopwatch.ElapsedMilliseconds)ms)" -Details @{
                response_time = $stopwatch.ElapsedMilliseconds
                data = $response
            }
            Write-TestLog "✅ $ServiceName 健康检查通过" -Level "SUCCESS"
            return $true
        } else {
            Record-TestResult -TestName "Health-$ServiceName" -Passed $false -Message "健康检查失败" -Details @{data = $response}
            Write-TestLog "❌ $ServiceName 健康检查失败" -Level "ERROR"
            return $false
        }
    }
    catch {
        Record-TestResult -TestName "Health-$ServiceName" -Passed $false -Message "连接失败: $($_.Exception.Message)" -Details @{error = $_.Exception.Message}
        Write-TestLog "❌ $ServiceName 连接失败: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Test-StockInfo {
    param([string]$Symbol, [string]$BaseUrl)
    
    try {
        $url = "$BaseUrl/api/stock/info/$Symbol"
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 15
        $stopwatch.Stop()
        
        if ($response.success -eq $true -and $response.data.name -ne "未知股票") {
            Record-TestResult -TestName "StockInfo-$Symbol" -Passed $true -Message "数据完整 ($($stopwatch.ElapsedMilliseconds)ms)" -Details @{
                response_time = $stopwatch.ElapsedMilliseconds
                stock_name = $response.data.name
            }
            Write-TestLog "✅ $Symbol 股票信息查询成功: $($response.data.name)" -Level "SUCCESS"
            return $true
        } else {
            Record-TestResult -TestName "StockInfo-$Symbol" -Passed $false -Message "数据不完整或为空" -Details @{data = $response}
            Write-TestLog "⚠️ $Symbol 股票信息不完整" -Level "WARNING"
            return $false
        }
    }
    catch {
        Record-TestResult -TestName "StockInfo-$Symbol" -Passed $false -Message "请求失败: $($_.Exception.Message)" -Details @{error = $_.Exception.Message}
        Write-TestLog "❌ $Symbol 股票信息查询失败: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Test-CacheMechanism {
    param([string]$Symbol, [string]$BaseUrl)
    
    try {
        $url = "$BaseUrl/api/stock/info/$Symbol"
        
        # 第一次请求
        $stopwatch1 = [System.Diagnostics.Stopwatch]::StartNew()
        $response1 = Invoke-RestMethod -Uri $url -Method Get
        $stopwatch1.Stop()
        
        # 第二次请求（应该从缓存）
        $stopwatch2 = [System.Diagnostics.Stopwatch]::StartNew()
        $response2 = Invoke-RestMethod -Uri $url -Method Get
        $stopwatch2.Stop()
        
        # 强制刷新请求
        $stopwatch3 = [System.Diagnostics.Stopwatch]::StartNew()
        $response3 = Invoke-RestMethod -Uri "$url?force_refresh=true" -Method Get
        $stopwatch3.Stop()
        
        $dataConsistent = $response1.data.name -eq $response2.data.name

        if ($dataConsistent) {
            Record-TestResult -TestName "Cache-$Symbol" -Passed $true -Message "缓存正常 (首次:$($stopwatch1.ElapsedMilliseconds)ms, 缓存:$($stopwatch2.ElapsedMilliseconds)ms, 刷新:$($stopwatch3.ElapsedMilliseconds)ms)" -Details @{
                first_time = $stopwatch1.ElapsedMilliseconds
                second_time = $stopwatch2.ElapsedMilliseconds
                refresh_time = $stopwatch3.ElapsedMilliseconds
                data_consistent = $dataConsistent
            }
            Write-TestLog "✅ $Symbol 缓存机制正常" -Level "SUCCESS"
            return $true
        } else {
            Record-TestResult -TestName "Cache-$Symbol" -Passed $false -Message "缓存数据不一致" -Details @{
                first_time = $stopwatch1.ElapsedMilliseconds
                second_time = $stopwatch2.ElapsedMilliseconds
                refresh_time = $stopwatch3.ElapsedMilliseconds
                data_consistent = $dataConsistent
            }
            Write-TestLog "⚠️ $Symbol 缓存数据不一致" -Level "WARNING"
            return $false
        }
    }
    catch {
        Record-TestResult -TestName "Cache-$Symbol" -Passed $false -Message "测试失败: $($_.Exception.Message)" -Details @{error = $_.Exception.Message}
        Write-TestLog "❌ $Symbol 缓存测试失败: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Test-LLMModels {
    param([string]$BaseUrl)
    
    try {
        $url = "$BaseUrl/api/v1/models"
        $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 10
        
        if ($response.success -eq $true -and $response.data.Count -gt 0) {
            Record-TestResult -TestName "LLM-Models" -Passed $true -Message "发现 $($response.data.Count) 个模型" -Details @{models = $response.data}
            Write-TestLog "✅ LLM模型列表获取成功: $($response.data.Count)个模型" -Level "SUCCESS"
            return $true
        } else {
            Record-TestResult -TestName "LLM-Models" -Passed $false -Message "未发现可用模型" -Details @{data = $response}
            Write-TestLog "❌ 未发现可用LLM模型" -Level "ERROR"
            return $false
        }
    }
    catch {
        Record-TestResult -TestName "LLM-Models" -Passed $false -Message "请求失败: $($_.Exception.Message)" -Details @{error = $_.Exception.Message}
        Write-TestLog "❌ LLM模型列表获取失败: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Test-LLMChat {
    param([string]$BaseUrl)
    
    try {
        $url = "$BaseUrl/api/v1/chat/completions"
        $body = @{
            messages = @(
                @{
                    role = "user"
                    content = "请简单介绍一下股票投资的基本概念"
                }
            )
            model = "deepseek-chat"
            temperature = 0.7
            max_tokens = 100
        } | ConvertTo-Json -Depth 3
        
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-RestMethod -Uri $url -Method Post -Body $body -ContentType "application/json" -TimeoutSec 30
        $stopwatch.Stop()
        
        if ($response.success -eq $true -and $response.data) {
            Record-TestResult -TestName "LLM-Chat" -Passed $true -Message "聊天成功 ($($stopwatch.ElapsedMilliseconds)ms)" -Details @{
                response_time = $stopwatch.ElapsedMilliseconds
                response_length = $response.data.ToString().Length
            }
            Write-TestLog "✅ LLM聊天功能正常" -Level "SUCCESS"
            return $true
        } else {
            Record-TestResult -TestName "LLM-Chat" -Passed $false -Message "响应格式异常" -Details @{data = $response}
            Write-TestLog "❌ LLM聊天响应异常" -Level "ERROR"
            return $false
        }
    }
    catch {
        Record-TestResult -TestName "LLM-Chat" -Passed $false -Message "请求失败: $($_.Exception.Message)" -Details @{error = $_.Exception.Message}
        Write-TestLog "❌ LLM聊天测试失败: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Test-GatewayStockInfo {
    param([string]$Symbol, [string]$BaseUrl)
    
    try {
        $url = "$BaseUrl/api/stock/info/$Symbol"
        $response1 = Invoke-RestMethod -Uri $url -Method Get
        $response2 = Invoke-RestMethod -Uri "$url?force_refresh=true" -Method Get
        
        if ($response1.success -eq $true -and $response2.success -eq $true) {
            Record-TestResult -TestName "Gateway-$Symbol" -Passed $true -Message "网关路由正常" -Details @{
                normal_request = $response1.data.name
                refresh_request = $response2.data.name
            }
            Write-TestLog "✅ 网关路由测试成功: $Symbol" -Level "SUCCESS"
            return $true
        } else {
            Record-TestResult -TestName "Gateway-$Symbol" -Passed $false -Message "网关路由异常" -Details @{
                response1 = $response1
                response2 = $response2
            }
            Write-TestLog "❌ 网关路由测试失败: $Symbol" -Level "ERROR"
            return $false
        }
    }
    catch {
        Record-TestResult -TestName "Gateway-$Symbol" -Passed $false -Message "请求失败: $($_.Exception.Message)" -Details @{error = $_.Exception.Message}
        Write-TestLog "❌ 网关测试失败: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

# 主测试函数
function Start-HealthTests {
    Write-TestLog "📋 TC001: 系统健康检查测试" -Level "INFO"
    foreach ($service in $BaseUrls.GetEnumerator()) {
        Test-ServiceHealth -ServiceName $service.Key -BaseUrl $service.Value
    }
}

function Start-DataServiceTests {
    Write-TestLog "📊 TC002: 数据服务测试" -Level "INFO"
    foreach ($stock in $TestStocks) {
        Test-StockInfo -Symbol $stock -BaseUrl $BaseUrls["data_service"]
        Test-CacheMechanism -Symbol $stock -BaseUrl $BaseUrls["data_service"]
    }
}

function Start-LLMServiceTests {
    Write-TestLog "🤖 TC003: LLM服务测试" -Level "INFO"
    Test-LLMModels -BaseUrl $BaseUrls["llm_service"]
    Test-LLMChat -BaseUrl $BaseUrls["llm_service"]
}

function Start-GatewayTests {
    Write-TestLog "🌐 TC005: API网关测试" -Level "INFO"
    Test-GatewayStockInfo -Symbol $TestStocks[0] -BaseUrl $BaseUrls["api_gateway"]
}

function Generate-TestReport {
    $totalTests = $Results.Count
    $passedTests = ($Results | Where-Object { $_.passed -eq $true }).Count
    $failedTests = $totalTests - $passedTests
    $passRate = if ($totalTests -gt 0) { [math]::Round(($passedTests / $totalTests) * 100, 1) } else { 0 }
    
    $report = @{
        test_summary = @{
            total_tests = $totalTests
            passed_tests = $passedTests
            failed_tests = $failedTests
            pass_rate = "$passRate%"
            test_time = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        }
        test_results = $Results
    }
    
    # 确保输出目录存在
    $outputDir = Split-Path $OutputFile -Parent
    if (!(Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }
    
    # 保存报告
    $report | ConvertTo-Json -Depth 4 | Out-File -FilePath $OutputFile -Encoding UTF8
    
    # 打印摘要
    Write-TestLog "📊 测试报告摘要:" -Level "INFO"
    Write-TestLog "   总测试数: $totalTests" -Level "INFO"
    Write-TestLog "   通过数: $passedTests" -Level "SUCCESS"
    Write-TestLog "   失败数: $failedTests" -Level $(if ($failedTests -gt 0) { "ERROR" } else { "INFO" })
    Write-TestLog "   通过率: $passRate%" -Level "INFO"
    Write-TestLog "   报告文件: $OutputFile" -Level "INFO"
    
    # 打印失败的测试
    if ($failedTests -gt 0) {
        Write-TestLog "❌ 失败的测试:" -Level "ERROR"
        $Results | Where-Object { $_.passed -eq $false } | ForEach-Object {
            Write-TestLog "   - $($_.test_name): $($_.message)" -Level "ERROR"
        }
    }
}

# 主执行逻辑
Write-TestLog "🚀 开始TradingAgents后端微服务测试..." -Level "INFO"
Write-TestLog "测试类型: $TestType" -Level "INFO"

switch ($TestType.ToLower()) {
    "health" { Start-HealthTests }
    "data" { Start-DataServiceTests }
    "llm" { Start-LLMServiceTests }
    "gateway" { Start-GatewayTests }
    "all" {
        Start-HealthTests
        Start-DataServiceTests
        Start-LLMServiceTests
        Start-GatewayTests
    }
    default {
        Write-TestLog "未知的测试类型: $TestType" -Level "ERROR"
        Write-TestLog "可用类型: all, health, data, llm, gateway" -Level "INFO"
        exit 1
    }
}

Generate-TestReport
Write-TestLog "🎉 测试完成!" -Level "SUCCESS"
