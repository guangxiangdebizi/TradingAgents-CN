#!/usr/bin/env python3
"""
TradingAgents 微服务集成测试
测试完整的微服务架构，包括 API Gateway、Analysis Engine 和 Data Service
"""

import asyncio
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import httpx
import pytest
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

console = Console()

class MicroservicesTestSuite:
    """微服务集成测试套件"""
    
    def __init__(self):
        self.base_urls = {
            "api_gateway": "http://localhost:8000",
            "analysis_engine": "http://localhost:8001", 
            "data_service": "http://localhost:8002"
        }
        self.test_results = []
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_test_result(self, test_name: str, success: bool, message: str, response_time: float = 0):
        """记录测试结果"""
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "message": message,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        })
        
        status = "✅ PASS" if success else "❌ FAIL"
        console.print(f"{status} {test_name}: {message} ({response_time:.2f}s)")
    
    async def test_service_health(self, service_name: str, url: str) -> bool:
        """测试服务健康检查"""
        try:
            start_time = time.time()
            response = await self.client.get(f"{url}/health")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(
                    f"{service_name} 健康检查",
                    True,
                    f"状态: {data.get('status', 'unknown')}",
                    response_time
                )
                return True
            else:
                self.log_test_result(
                    f"{service_name} 健康检查",
                    False,
                    f"HTTP {response.status_code}",
                    response_time
                )
                return False
        except Exception as e:
            self.log_test_result(
                f"{service_name} 健康检查",
                False,
                f"连接失败: {str(e)}",
                0
            )
            return False
    
    async def test_stock_info(self, symbol: str = "000858") -> bool:
        """测试股票信息接口"""
        try:
            start_time = time.time()
            response = await self.client.get(f"{self.base_urls['api_gateway']}/api/stock/info/{symbol}")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test_result(
                        f"股票信息查询 ({symbol})",
                        True,
                        f"获取成功: {data['data'].get('name', 'N/A')}",
                        response_time
                    )
                    return True
            
            self.log_test_result(
                f"股票信息查询 ({symbol})",
                False,
                f"HTTP {response.status_code}",
                response_time
            )
            return False
        except Exception as e:
            self.log_test_result(
                f"股票信息查询 ({symbol})",
                False,
                f"请求失败: {str(e)}",
                0
            )
            return False
    
    async def test_stock_fundamentals(self, symbol: str = "000858") -> bool:
        """测试股票基本面接口"""
        try:
            start_time = time.time()
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            url = f"{self.base_urls['api_gateway']}/api/stock/fundamentals/{symbol}"
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "curr_date": end_date
            }
            
            response = await self.client.get(url, params=params)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test_result(
                        f"基本面数据查询 ({symbol})",
                        True,
                        "数据获取成功",
                        response_time
                    )
                    return True
            
            self.log_test_result(
                f"基本面数据查询 ({symbol})",
                False,
                f"HTTP {response.status_code}",
                response_time
            )
            return False
        except Exception as e:
            self.log_test_result(
                f"基本面数据查询 ({symbol})",
                False,
                f"请求失败: {str(e)}",
                0
            )
            return False
    
    async def test_stock_news(self, symbol: str = "AAPL") -> bool:
        """测试股票新闻接口"""
        try:
            start_time = time.time()
            response = await self.client.get(f"{self.base_urls['api_gateway']}/api/stock/news/{symbol}")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test_result(
                        f"股票新闻查询 ({symbol})",
                        True,
                        "新闻获取成功",
                        response_time
                    )
                    return True
            
            self.log_test_result(
                f"股票新闻查询 ({symbol})",
                False,
                f"HTTP {response.status_code}",
                response_time
            )
            return False
        except Exception as e:
            self.log_test_result(
                f"股票新闻查询 ({symbol})",
                False,
                f"请求失败: {str(e)}",
                0
            )
            return False
    
    async def test_analysis_workflow(self, symbol: str = "000858") -> bool:
        """测试完整的分析工作流"""
        try:
            # 1. 启动分析
            analysis_request = {
                "stock_code": symbol,
                "analysis_date": datetime.now().isoformat(),
                "llm_provider": "deepseek",
                "model_version": "deepseek-chat",
                "enable_memory": False,
                "debug_mode": True,
                "max_output_length": 2000,
                "include_sentiment": True,
                "include_risk_assessment": True,
                "market_analyst": True,
                "social_analyst": False,
                "news_analyst": True,
                "fundamental_analyst": True
            }
            
            start_time = time.time()
            response = await self.client.post(
                f"{self.base_urls['api_gateway']}/api/analysis/start",
                json=analysis_request
            )
            
            if response.status_code != 200:
                self.log_test_result(
                    f"分析工作流 ({symbol})",
                    False,
                    f"启动分析失败: HTTP {response.status_code}",
                    time.time() - start_time
                )
                return False
            
            data = response.json()
            if not data.get("success"):
                self.log_test_result(
                    f"分析工作流 ({symbol})",
                    False,
                    f"启动分析失败: {data.get('message', 'Unknown error')}",
                    time.time() - start_time
                )
                return False
            
            analysis_id = data["data"]["analysis_id"]
            
            # 2. 监控分析进度
            max_wait_time = 300  # 5分钟超时
            check_interval = 5   # 每5秒检查一次
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"正在分析 {symbol}...", total=None)
                
                for _ in range(max_wait_time // check_interval):
                    await asyncio.sleep(check_interval)
                    
                    # 检查进度
                    progress_response = await self.client.get(
                        f"{self.base_urls['api_gateway']}/api/analysis/{analysis_id}/progress"
                    )
                    
                    if progress_response.status_code == 200:
                        progress_data = progress_response.json()
                        if progress_data.get("success"):
                            status = progress_data["data"]["status"]
                            progress.update(task, description=f"分析状态: {status}")
                            
                            if status in ["completed", "failed"]:
                                break
                    
                    # 检查结果
                    result_response = await self.client.get(
                        f"{self.base_urls['api_gateway']}/api/analysis/{analysis_id}/result"
                    )
                    
                    if result_response.status_code == 200:
                        result_data = result_response.json()
                        if result_data.get("success") and result_data["data"].get("status") == "completed":
                            total_time = time.time() - start_time
                            self.log_test_result(
                                f"分析工作流 ({symbol})",
                                True,
                                f"分析完成，耗时 {total_time:.1f}s",
                                total_time
                            )
                            return True
            
            # 超时
            self.log_test_result(
                f"分析工作流 ({symbol})",
                False,
                "分析超时",
                time.time() - start_time
            )
            return False
            
        except Exception as e:
            self.log_test_result(
                f"分析工作流 ({symbol})",
                False,
                f"分析失败: {str(e)}",
                0
            )
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        console.print(Panel.fit("🧪 TradingAgents 微服务集成测试", style="bold blue"))
        
        # 1. 健康检查测试
        console.print("\n📋 [bold]服务健康检查[/bold]")
        health_results = []
        for service_name, url in self.base_urls.items():
            result = await self.test_service_health(service_name, url)
            health_results.append(result)
        
        if not all(health_results):
            console.print("❌ 部分服务不健康，跳过后续测试")
            return
        
        # 2. 数据接口测试
        console.print("\n📊 [bold]数据接口测试[/bold]")
        await self.test_stock_info("000858")  # A股
        await self.test_stock_info("AAPL")    # 美股
        await self.test_stock_fundamentals("000858")
        await self.test_stock_news("AAPL")
        
        # 3. 分析工作流测试（可选，耗时较长）
        console.print("\n🤖 [bold]分析工作流测试[/bold]")
        console.print("⚠️  此测试可能需要几分钟时间...")
        await self.test_analysis_workflow("000858")
        
        # 4. 生成测试报告
        self.generate_test_report()
    
    def generate_test_report(self):
        """生成测试报告"""
        console.print("\n📈 [bold]测试报告[/bold]")
        
        # 统计
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        # 创建表格
        table = Table(title="测试结果汇总")
        table.add_column("测试项目", style="cyan")
        table.add_column("状态", style="green")
        table.add_column("消息", style="yellow")
        table.add_column("响应时间", style="magenta")
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            table.add_row(
                result["test_name"],
                status,
                result["message"],
                f"{result['response_time']:.2f}s"
            )
        
        console.print(table)
        
        # 总结
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        console.print(f"\n📊 [bold]测试总结[/bold]")
        console.print(f"总测试数: {total_tests}")
        console.print(f"通过: {passed_tests}")
        console.print(f"失败: {failed_tests}")
        console.print(f"成功率: {success_rate:.1f}%")
        
        # 保存报告
        report_file = f"backend/tests/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": success_rate
                },
                "results": self.test_results
            }, f, ensure_ascii=False, indent=2)
        
        console.print(f"📄 详细报告已保存到: {report_file}")


async def main():
    """主函数"""
    async with MicroservicesTestSuite() as test_suite:
        await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
