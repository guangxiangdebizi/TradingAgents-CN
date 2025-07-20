#!/usr/bin/env python3
"""
API 测试脚本
用于测试后端微服务的各个接口
"""

import asyncio
import json
import time
from datetime import datetime
import httpx

# API 基础地址
API_BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def test_health_check(self):
        """测试健康检查"""
        print("🔍 测试健康检查...")
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            data = response.json()
            print(f"✅ 健康检查成功: {data}")
            return True
        except Exception as e:
            print(f"❌ 健康检查失败: {e}")
            return False
    
    async def test_system_status(self):
        """测试系统状态"""
        print("📊 测试系统状态...")
        try:
            response = await self.client.get(f"{self.base_url}/api/config/status")
            response.raise_for_status()
            data = response.json()
            print(f"✅ 系统状态: {data}")
            return True
        except Exception as e:
            print(f"❌ 系统状态失败: {e}")
            return False
    
    async def test_model_config(self):
        """测试模型配置"""
        print("🤖 测试模型配置...")
        try:
            response = await self.client.get(f"{self.base_url}/api/config/models")
            response.raise_for_status()
            data = response.json()
            print(f"✅ 模型配置: {data}")
            return True
        except Exception as e:
            print(f"❌ 模型配置失败: {e}")
            return False
    
    async def test_stock_info(self, symbol="000858"):
        """测试股票信息"""
        print(f"📈 测试股票信息: {symbol}")
        try:
            response = await self.client.get(f"{self.base_url}/api/stock/info/{symbol}")
            response.raise_for_status()
            data = response.json()
            print(f"✅ 股票信息: {data}")
            return True
        except Exception as e:
            print(f"❌ 股票信息失败: {e}")
            return False
    
    async def test_stock_data(self, symbol="000858"):
        """测试股票数据"""
        print(f"📊 测试股票数据: {symbol}")
        try:
            request_data = {
                "symbol": symbol,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
            response = await self.client.post(
                f"{self.base_url}/api/stock/data",
                json=request_data
            )
            response.raise_for_status()
            data = response.json()
            print(f"✅ 股票数据: {data}")
            return True
        except Exception as e:
            print(f"❌ 股票数据失败: {e}")
            return False
    
    async def test_analysis_workflow(self, symbol="000858"):
        """测试完整的分析流程"""
        print(f"🚀 测试分析流程: {symbol}")
        
        try:
            # 1. 启动分析
            analysis_request = {
                "stock_code": symbol,
                "market_type": "A股",
                "analysis_date": datetime.now().isoformat(),
                "research_depth": 3,
                "market_analyst": True,
                "social_analyst": False,
                "news_analyst": False,
                "fundamental_analyst": True,
                "llm_provider": "dashscope",
                "model_version": "plus-balanced",
                "enable_memory": True,
                "debug_mode": True,
                "max_output_length": 4000,
                "include_sentiment": True,
                "include_risk_assessment": True,
                "custom_prompt": "测试分析"
            }
            
            print("📤 启动分析...")
            response = await self.client.post(
                f"{self.base_url}/api/analysis/start",
                json=analysis_request
            )
            response.raise_for_status()
            start_data = response.json()
            
            if not start_data.get("success"):
                print(f"❌ 启动分析失败: {start_data}")
                return False
            
            analysis_id = start_data["data"]["analysis_id"]
            print(f"✅ 分析已启动: {analysis_id}")
            
            # 2. 轮询进度
            print("⏳ 监控分析进度...")
            max_attempts = 30  # 最多等待30次（约5分钟）
            attempt = 0
            
            while attempt < max_attempts:
                await asyncio.sleep(10)  # 等待10秒
                attempt += 1
                
                try:
                    response = await self.client.get(
                        f"{self.base_url}/api/analysis/{analysis_id}/progress"
                    )
                    response.raise_for_status()
                    progress_data = response.json()
                    
                    if progress_data.get("success"):
                        progress = progress_data["data"]
                        status = progress.get("status")
                        percentage = progress.get("progress_percentage", 0)
                        current_step = progress.get("current_step", "")
                        
                        print(f"📊 进度: {percentage}% - {current_step}")
                        
                        if status == "completed":
                            print("✅ 分析完成！")
                            break
                        elif status == "failed":
                            print(f"❌ 分析失败: {progress.get('error_message')}")
                            return False
                    
                except Exception as e:
                    print(f"⚠️ 获取进度失败: {e}")
                    continue
            
            if attempt >= max_attempts:
                print("⏰ 分析超时，但可能仍在后台运行")
                return False
            
            # 3. 获取结果
            print("📄 获取分析结果...")
            response = await self.client.get(
                f"{self.base_url}/api/analysis/{analysis_id}/result"
            )
            response.raise_for_status()
            result_data = response.json()
            
            if result_data.get("success"):
                result = result_data["data"]
                print(f"✅ 分析结果: {result.get('recommendation', 'N/A')}")
                print(f"   置信度: {result.get('confidence', 'N/A')}")
                print(f"   风险评分: {result.get('risk_score', 'N/A')}")
                return True
            else:
                print(f"❌ 获取结果失败: {result_data}")
                return False
                
        except Exception as e:
            print(f"❌ 分析流程失败: {e}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始 API 测试")
        print("=" * 50)
        
        tests = [
            ("健康检查", self.test_health_check()),
            ("系统状态", self.test_system_status()),
            ("模型配置", self.test_model_config()),
            ("股票信息", self.test_stock_info()),
            ("股票数据", self.test_stock_data()),
            ("分析流程", self.test_analysis_workflow()),
        ]
        
        results = []
        for test_name, test_coro in tests:
            print(f"\n🔬 {test_name}")
            print("-" * 30)
            try:
                result = await test_coro
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} 异常: {e}")
                results.append((test_name, False))
        
        # 汇总结果
        print("\n📋 测试结果汇总")
        print("=" * 50)
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n📊 总计: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有测试通过！")
        else:
            print("⚠️ 部分测试失败，请检查服务状态")
        
        return passed == total
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()

async def main():
    """主函数"""
    tester = APITester()
    
    try:
        success = await tester.run_all_tests()
        exit_code = 0 if success else 1
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
        exit_code = 1
    except Exception as e:
        print(f"\n💥 测试异常: {e}")
        exit_code = 1
    finally:
        await tester.close()
    
    exit(exit_code)

if __name__ == "__main__":
    asyncio.run(main())
