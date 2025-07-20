#!/usr/bin/env python3
"""
TradingAgents 微服务快速 API 测试
快速测试所有微服务的基本功能
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any

class QuickAPITest:
    """快速 API 测试类"""
    
    def __init__(self):
        self.base_urls = {
            "api_gateway": "http://localhost:8000",
            "analysis_engine": "http://localhost:8001", 
            "data_service": "http://localhost:8002"
        }
        self.session = requests.Session()
        self.session.timeout = 10
        
    def test_health_check(self, service_name: str, url: str) -> bool:
        """测试健康检查"""
        try:
            print(f"🔍 测试 {service_name} 健康检查...")
            response = self.session.get(f"{url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {service_name}: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ {service_name}: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ {service_name}: 连接失败 - {e}")
            return False
    
    def test_stock_info(self, symbol: str = "000858") -> bool:
        """测试股票信息接口"""
        try:
            print(f"📊 测试股票信息查询: {symbol}")
            response = self.session.get(f"{self.base_urls['api_gateway']}/api/stock/info/{symbol}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    stock_name = data['data'].get('name', 'N/A')
                    print(f"✅ 股票信息: {symbol} - {stock_name}")
                    return True
                else:
                    print(f"❌ 股票信息查询失败: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ 股票信息查询: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 股票信息查询失败: {e}")
            return False
    
    def test_stock_fundamentals(self, symbol: str = "000858") -> bool:
        """测试股票基本面接口"""
        try:
            print(f"📈 测试基本面数据查询: {symbol}")
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            url = f"{self.base_urls['api_gateway']}/api/stock/fundamentals/{symbol}"
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "curr_date": end_date
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ 基本面数据: {symbol} - 获取成功")
                    return True
                else:
                    print(f"❌ 基本面数据查询失败: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ 基本面数据查询: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 基本面数据查询失败: {e}")
            return False
    
    def test_stock_news(self, symbol: str = "AAPL") -> bool:
        """测试股票新闻接口"""
        try:
            print(f"📰 测试股票新闻查询: {symbol}")
            response = self.session.get(f"{self.base_urls['api_gateway']}/api/stock/news/{symbol}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ 股票新闻: {symbol} - 获取成功")
                    return True
                else:
                    print(f"❌ 股票新闻查询失败: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ 股票新闻查询: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 股票新闻查询失败: {e}")
            return False
    
    def test_data_sources_status(self) -> bool:
        """测试数据源状态"""
        try:
            print("🔧 测试数据源状态...")
            response = self.session.get(f"{self.base_urls['api_gateway']}/api/data-sources/status")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ 数据源状态: 获取成功")
                    # 显示数据源状态
                    sources = data.get('data', {})
                    for source, status in sources.items():
                        if isinstance(status, dict):
                            print(f"   - {source}: {status.get('status', 'unknown')}")
                        else:
                            print(f"   - {source}: {status}")
                    return True
                else:
                    print(f"❌ 数据源状态查询失败: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ 数据源状态查询: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 数据源状态查询失败: {e}")
            return False
    
    def test_model_config(self) -> bool:
        """测试模型配置接口"""
        try:
            print("🤖 测试模型配置...")
            response = self.session.get(f"{self.base_urls['api_gateway']}/api/config/models")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ 模型配置: 获取成功")
                    return True
                else:
                    print(f"❌ 模型配置查询失败: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ 模型配置查询: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 模型配置查询失败: {e}")
            return False
    
    def run_quick_tests(self):
        """运行快速测试"""
        print("🧪 TradingAgents 微服务快速 API 测试")
        print("=" * 50)
        
        results = []
        
        # 1. 健康检查
        print("\n📋 服务健康检查")
        print("-" * 30)
        for service_name, url in self.base_urls.items():
            result = self.test_health_check(service_name, url)
            results.append(("健康检查", service_name, result))
        
        # 检查是否所有服务都健康
        if not all(result[2] for result in results if result[0] == "健康检查"):
            print("\n❌ 部分服务不健康，跳过后续测试")
            return
        
        # 2. 数据接口测试
        print("\n📊 数据接口测试")
        print("-" * 30)
        
        # 股票信息
        result = self.test_stock_info("000858")  # A股
        results.append(("数据接口", "股票信息(A股)", result))
        
        result = self.test_stock_info("AAPL")    # 美股
        results.append(("数据接口", "股票信息(美股)", result))
        
        # 基本面数据
        result = self.test_stock_fundamentals("000858")
        results.append(("数据接口", "基本面数据", result))
        
        # 股票新闻
        result = self.test_stock_news("AAPL")
        results.append(("数据接口", "股票新闻", result))
        
        # 数据源状态
        result = self.test_data_sources_status()
        results.append(("数据接口", "数据源状态", result))
        
        # 3. 配置接口测试
        print("\n⚙️ 配置接口测试")
        print("-" * 30)
        
        result = self.test_model_config()
        results.append(("配置接口", "模型配置", result))
        
        # 4. 生成测试报告
        print("\n📈 测试结果汇总")
        print("=" * 50)
        
        total_tests = len(results)
        passed_tests = sum(1 for _, _, success in results if success)
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for category, test_name, success in results:
                if not success:
                    print(f"   - {category}: {test_name}")
        
        # 保存简单报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": passed_tests/total_tests*100
            },
            "results": [
                {"category": cat, "test_name": name, "success": success}
                for cat, name, success in results
            ]
        }
        
        report_file = f"backend/tests/quick_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 测试报告已保存到: {report_file}")
        
        if passed_tests == total_tests:
            print("\n🎉 所有测试通过！微服务架构运行正常！")
        else:
            print(f"\n⚠️ 有 {failed_tests} 个测试失败，请检查相关服务")


def main():
    """主函数"""
    test = QuickAPITest()
    test.run_quick_tests()


if __name__ == "__main__":
    main()
