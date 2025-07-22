#!/usr/bin/env python3
"""
并发分析性能测试
测试Enhanced Analysis Engine的并发处理能力
"""

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any
from datetime import datetime
import json

class ConcurrentAnalysisTest:
    """并发分析测试类"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session: aiohttp.ClientSession = None
        self.results: List[Dict[str, Any]] = []
    
    async def initialize(self):
        """初始化测试环境"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=300)  # 5分钟超时
        )
        print("🔧 测试环境初始化完成")
    
    async def cleanup(self):
        """清理测试环境"""
        if self.session:
            await self.session.close()
        print("🧹 测试环境清理完成")
    
    async def submit_analysis_task(self, stock_code: str, analysis_type: str = "comprehensive",
                                  priority: str = "normal") -> Dict[str, Any]:
        """提交分析任务"""
        start_time = time.time()
        
        try:
            # 提交任务
            async with self.session.post(
                f"{self.base_url}/api/v1/analysis/submit",
                json={
                    "stock_code": stock_code,
                    "analysis_type": analysis_type,
                    "parameters": {}
                },
                params={"priority": priority}
            ) as response:
                submit_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    task_id = data["data"]["task_id"]
                    
                    # 等待任务完成
                    result = await self._wait_for_completion(task_id)
                    
                    total_time = time.time() - start_time
                    
                    return {
                        "stock_code": stock_code,
                        "task_id": task_id,
                        "submit_time": submit_time,
                        "total_time": total_time,
                        "status": "success",
                        "result": result
                    }
                else:
                    error_text = await response.text()
                    return {
                        "stock_code": stock_code,
                        "submit_time": submit_time,
                        "total_time": time.time() - start_time,
                        "status": "failed",
                        "error": f"HTTP {response.status}: {error_text}"
                    }
                    
        except Exception as e:
            return {
                "stock_code": stock_code,
                "submit_time": 0,
                "total_time": time.time() - start_time,
                "status": "error",
                "error": str(e)
            }
    
    async def _wait_for_completion(self, task_id: str, max_wait: int = 300) -> Dict[str, Any]:
        """等待任务完成"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                async with self.session.get(
                    f"{self.base_url}/api/v1/analysis/status/{task_id}"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        status = data["status"]
                        
                        if status == "completed":
                            return data
                        elif status == "failed":
                            return {"error": data.get("error", "Unknown error")}
                        elif status == "cancelled":
                            return {"error": "Task was cancelled"}
                        
                        # 任务还在进行中，等待一下
                        await asyncio.sleep(2)
                    else:
                        await asyncio.sleep(2)
                        
            except Exception as e:
                print(f"⚠️ 检查任务状态时出错: {e}")
                await asyncio.sleep(2)
        
        return {"error": "Task timeout"}
    
    async def test_single_analysis(self, stock_code: str = "AAPL"):
        """测试单个分析"""
        print(f"\n🧪 测试单个分析: {stock_code}")
        
        result = await self.submit_analysis_task(stock_code)
        
        print(f"📊 结果:")
        print(f"   状态: {result['status']}")
        print(f"   提交时间: {result['submit_time']:.3f}s")
        print(f"   总时间: {result['total_time']:.3f}s")
        
        if result['status'] != 'success':
            print(f"   错误: {result.get('error', 'Unknown')}")
        
        return result
    
    async def test_concurrent_analysis(self, stock_codes: List[str], 
                                     max_concurrent: int = 10):
        """测试并发分析"""
        print(f"\n🚀 测试并发分析: {len(stock_codes)}个股票, 最大并发{max_concurrent}")
        
        # 创建信号量控制并发数
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_submit(stock_code: str):
            async with semaphore:
                return await self.submit_analysis_task(stock_code)
        
        # 并发执行
        start_time = time.time()
        tasks = [limited_submit(code) for code in stock_codes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # 统计结果
        successful = [r for r in results if isinstance(r, dict) and r.get('status') == 'success']
        failed = [r for r in results if isinstance(r, dict) and r.get('status') != 'success']
        errors = [r for r in results if isinstance(r, Exception)]
        
        print(f"\n📊 并发测试结果:")
        print(f"   总任务数: {len(stock_codes)}")
        print(f"   成功: {len(successful)}")
        print(f"   失败: {len(failed)}")
        print(f"   异常: {len(errors)}")
        print(f"   总时间: {total_time:.3f}s")
        print(f"   平均时间: {total_time/len(stock_codes):.3f}s")
        
        if successful:
            submit_times = [r['submit_time'] for r in successful]
            total_times = [r['total_time'] for r in successful]
            
            print(f"\n⏱️ 时间统计 (成功任务):")
            print(f"   提交时间 - 平均: {statistics.mean(submit_times):.3f}s, "
                  f"中位数: {statistics.median(submit_times):.3f}s")
            print(f"   总时间 - 平均: {statistics.mean(total_times):.3f}s, "
                  f"中位数: {statistics.median(total_times):.3f}s")
            print(f"   最快: {min(total_times):.3f}s, 最慢: {max(total_times):.3f}s")
        
        # 保存结果
        self.results.extend([r for r in results if isinstance(r, dict)])
        
        return {
            "total_tasks": len(stock_codes),
            "successful": len(successful),
            "failed": len(failed),
            "errors": len(errors),
            "total_time": total_time,
            "average_time": total_time / len(stock_codes),
            "results": results
        }
    
    async def test_load_balancer_health(self):
        """测试负载均衡器健康状态"""
        print(f"\n🏥 测试负载均衡器健康状态")
        
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 负载均衡器状态: {data.get('status', 'unknown')}")
                    
                    # 显示组件状态
                    components = data.get('components', {})
                    for component, status in components.items():
                        status_icon = "✅" if status else "❌"
                        print(f"   {status_icon} {component}: {'健康' if status else '不健康'}")
                    
                    # 显示统计信息
                    stats = data.get('stats', {})
                    if 'concurrency' in stats:
                        conc_stats = stats['concurrency']
                        print(f"\n📊 并发统计:")
                        print(f"   当前运行: {conc_stats.get('current_running', 0)}")
                        print(f"   当前队列: {conc_stats.get('current_queued', 0)}")
                        print(f"   总完成: {conc_stats.get('total_completed', 0)}")
                        print(f"   成功率: {conc_stats.get('success_rate', 0):.1%}")
                    
                    return data
                else:
                    print(f"❌ 健康检查失败: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return None
    
    async def test_system_stats(self):
        """测试系统统计信息"""
        print(f"\n📈 获取系统统计信息")
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/system/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # 显示并发统计
                    if 'concurrency' in data:
                        conc = data['concurrency']
                        print(f"🔄 并发统计:")
                        print(f"   最大并发: {conc.get('peak_concurrent_tasks', 0)}")
                        print(f"   平均执行时间: {conc.get('average_execution_time', 0):.1f}s")
                        print(f"   每分钟任务数: {conc.get('tasks_per_minute', 0):.1f}")
                        print(f"   队列利用率: {conc.get('queue_utilization', 0):.1%}")
                        print(f"   并发利用率: {conc.get('concurrency_utilization', 0):.1%}")
                    
                    # 显示负载均衡统计
                    if 'load_balancer' in data:
                        lb = data['load_balancer']
                        print(f"\n⚖️ 负载均衡统计:")
                        print(f"   总实例: {lb.get('total_instances', 0)}")
                        print(f"   健康实例: {lb.get('healthy_instances', 0)}")
                        print(f"   总连接: {lb.get('total_connections', 0)}")
                        print(f"   总请求: {lb.get('total_requests', 0)}")
                    
                    return data
                else:
                    print(f"❌ 获取统计失败: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            print(f"❌ 获取统计异常: {e}")
            return None
    
    def save_results(self, filename: str = None):
        """保存测试结果"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"concurrent_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 测试结果已保存到: {filename}")

async def main():
    """主测试函数"""
    print("🚀 Enhanced Analysis Engine 并发性能测试")
    print("=" * 60)
    
    # 测试配置
    BASE_URL = "http://localhost:8000"  # Nginx负载均衡器地址
    TEST_STOCKS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX", "CRM", "ORCL"]
    
    test = ConcurrentAnalysisTest(BASE_URL)
    
    try:
        await test.initialize()
        
        # 1. 健康检查
        await test.test_load_balancer_health()
        
        # 2. 系统统计
        await test.test_system_stats()
        
        # 3. 单个分析测试
        await test.test_single_analysis("AAPL")
        
        # 4. 小规模并发测试
        print(f"\n" + "="*60)
        await test.test_concurrent_analysis(TEST_STOCKS[:3], max_concurrent=3)
        
        # 5. 中等规模并发测试
        print(f"\n" + "="*60)
        await test.test_concurrent_analysis(TEST_STOCKS[:5], max_concurrent=5)
        
        # 6. 大规模并发测试
        print(f"\n" + "="*60)
        await test.test_concurrent_analysis(TEST_STOCKS, max_concurrent=10)
        
        # 7. 最终统计
        await test.test_system_stats()
        
        # 保存结果
        test.save_results()
        
        print(f"\n🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await test.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
