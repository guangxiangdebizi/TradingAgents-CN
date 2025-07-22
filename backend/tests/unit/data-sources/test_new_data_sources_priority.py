#!/usr/bin/env python3
"""
测试新数据源优先级和缓存清除功能
"""

import requests
import time
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class DataSourcePriorityTester:
    """数据源优先级测试器"""
    
    def __init__(self):
        self.data_service_url = "http://localhost:8002"
        self.test_symbols = ["AAPL", "MSFT", "GOOGL"]
    
    def test_data_source_initialization(self):
        """测试数据源初始化状态"""
        print("🔍 检查数据源初始化状态")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.data_service_url}/health", timeout=30)
            if response.status_code == 200:
                print("✅ Data Service 健康")
            else:
                print(f"❌ Data Service 不健康: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 无法连接到Data Service: {e}")
            return False
        
        return True
    
    def test_with_clear_cache(self, symbol: str):
        """测试清除缓存功能"""
        print(f"\n🗑️ 测试清除缓存功能: {symbol}")
        print("-" * 40)
        
        try:
            # 使用新的clear_all_cache参数
            response = requests.get(
                f"{self.data_service_url}/api/enhanced/stock/{symbol}",
                params={
                    "force_refresh": True,
                    "clear_all_cache": True,
                    "start_date": "2024-12-01",
                    "end_date": "2024-12-31"
                },
                timeout=180
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    result = data.get("data", {})
                    data_source = result.get("data_source", "unknown")
                    
                    print(f"✅ 清除缓存测试成功")
                    print(f"📊 股票代码: {result.get('symbol', 'N/A')}")
                    print(f"📡 使用的数据源: {data_source}")
                    print(f"🌍 市场类型: {result.get('market_type', 'N/A')}")
                    
                    # 检查是否使用了新数据源
                    if data_source in ["alpha_vantage", "twelve_data", "iex_cloud"]:
                        print(f"🎉 成功使用新数据源: {data_source}")
                        return True, data_source
                    else:
                        print(f"⚠️ 仍使用旧数据源: {data_source}")
                        return False, data_source
                else:
                    print(f"❌ API返回失败: {data.get('message', 'N/A')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"📄 响应内容: {response.text}")
            
        except Exception as e:
            print(f"❌ 清除缓存测试失败: {e}")
        
        return False, "unknown"
    
    def test_multiple_requests(self, symbol: str, count: int = 3):
        """测试多次请求，观察数据源使用情况"""
        print(f"\n🔄 测试多次请求: {symbol} ({count}次)")
        print("-" * 40)
        
        sources_used = []
        
        for i in range(count):
            try:
                print(f"  请求 {i+1}/{count}...", end=" ")
                
                # 每次都强制刷新，避免缓存影响
                response = requests.get(
                    f"{self.data_service_url}/api/enhanced/stock/{symbol}",
                    params={
                        "force_refresh": True,
                        "clear_all_cache": i == 0,  # 第一次清除所有缓存
                        "start_date": "2024-12-01",
                        "end_date": "2024-12-31"
                    },
                    timeout=120
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        result = data.get("data", {})
                        data_source = result.get("data_source", "unknown")
                        sources_used.append(data_source)
                        print(f"✅ {data_source}")
                    else:
                        print(f"❌ 失败: {data.get('message', 'N/A')}")
                        sources_used.append("failed")
                else:
                    print(f"❌ HTTP {response.status_code}")
                    sources_used.append("error")
                
                # 等待一段时间避免频率限制
                if i < count - 1:
                    time.sleep(3)
                
            except Exception as e:
                print(f"❌ 异常: {e}")
                sources_used.append("exception")
        
        # 统计结果
        print(f"\n📊 数据源使用统计:")
        source_counts = {}
        for source in sources_used:
            source_counts[source] = source_counts.get(source, 0) + 1
        
        for source, count in source_counts.items():
            print(f"  {source}: {count} 次")
        
        return sources_used
    
    def check_api_keys_status(self):
        """检查API密钥配置状态"""
        print("\n🔑 检查API密钥配置状态")
        print("=" * 50)
        
        api_keys = {
            'ALPHA_VANTAGE_API_KEY': 'Alpha Vantage',
            'TWELVE_DATA_API_KEY': 'Twelve Data',
            'IEX_CLOUD_API_KEY': 'IEX Cloud',
            'FINNHUB_API_KEY': 'FinnHub'
        }
        
        configured_count = 0
        for key, name in api_keys.items():
            value = os.getenv(key)
            if value and value != f"your_{key.lower()}_here":
                print(f"✅ {name}: 已配置")
                configured_count += 1
            else:
                print(f"❌ {name}: 未配置")
        
        print(f"\n📊 配置状态: {configured_count}/{len(api_keys)} 个API密钥已配置")
        
        if configured_count == 0:
            print("\n⚠️ 警告: 没有配置任何新的美股数据源API密钥")
            print("💡 建议运行: python backend/setup_api_keys.py")
            return False
        
        return configured_count > 0
    
    def test_data_source_priority_order(self):
        """测试数据源优先级顺序"""
        print("\n🎯 测试数据源优先级顺序")
        print("=" * 50)
        
        # 测试美股符号
        test_symbol = "AAPL"
        
        print(f"📊 测试股票: {test_symbol}")
        print("🔄 预期优先级顺序:")
        print("  1. Alpha Vantage")
        print("  2. Twelve Data")
        print("  3. IEX Cloud")
        print("  4. FinnHub")
        print("  5. YFinance")
        print("  6. AKShare")
        
        # 执行测试
        success, data_source = self.test_with_clear_cache(test_symbol)
        
        if success:
            print(f"\n🎉 成功使用新数据源: {data_source}")
            
            # 检查是否符合预期优先级
            if data_source == "alpha_vantage":
                print("✅ 使用了最高优先级数据源 (Alpha Vantage)")
            elif data_source == "twelve_data":
                print("✅ 使用了第二优先级数据源 (Twelve Data)")
            elif data_source == "iex_cloud":
                print("✅ 使用了第三优先级数据源 (IEX Cloud)")
            else:
                print(f"⚠️ 使用了较低优先级数据源: {data_source}")
        else:
            print(f"\n❌ 仍在使用旧数据源: {data_source}")
            print("💡 可能原因:")
            print("  1. 新数据源API密钥未配置")
            print("  2. 新数据源初始化失败")
            print("  3. 数据源优先级配置问题")
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("🧪 新数据源优先级综合测试")
        print("=" * 60)
        
        # 1. 检查服务状态
        if not self.test_data_source_initialization():
            print("\n❌ Data Service 不可用，无法继续测试")
            return
        
        # 2. 检查API密钥配置
        if not self.check_api_keys_status():
            print("\n⚠️ 建议先配置API密钥再进行测试")
        
        # 3. 测试数据源优先级
        self.test_data_source_priority_order()
        
        # 4. 测试多次请求
        print("\n" + "=" * 60)
        choice = input("❓ 是否进行多次请求测试？(这会发送多个请求) (y/N): ").strip().lower()
        if choice in ['y', 'yes']:
            self.test_multiple_requests("AAPL", 3)
        
        print("\n🎉 综合测试完成！")
        print("\n💡 总结:")
        print("1. 如果仍在使用旧数据源，请检查:")
        print("   - API密钥是否正确配置")
        print("   - Data Service是否重启以加载新配置")
        print("   - 新数据源是否初始化成功")
        print("2. 建议配置至少一个新数据源API密钥")
        print("3. 使用clear_all_cache=true参数可以强制清除缓存")

def main():
    """主函数"""
    tester = DataSourcePriorityTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
