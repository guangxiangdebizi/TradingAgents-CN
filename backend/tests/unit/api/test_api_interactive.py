#!/usr/bin/env python3
"""
交互式API测试工具
"""

import requests
import json
import time
from datetime import datetime

class DataSourceAPITester:
    """数据源API交互式测试器"""
    
    def __init__(self):
        self.base_url = "http://localhost:8002"
    
    def test_health(self):
        """测试健康检查"""
        print("🏥 健康检查")
        print("-" * 40)
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 服务状态: {data.get('status', 'unknown')}")
                
                dependencies = data.get('dependencies', {})
                for dep, status in dependencies.items():
                    print(f"  📦 {dep}: {status}")
                return True
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def test_data_sources_status(self):
        """测试数据源状态"""
        print("\n🔧 数据源状态")
        print("-" * 40)
        
        try:
            response = requests.get(f"{self.base_url}/api/data-sources/status", timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    sources = data.get('data', {})
                    print(f"📊 数据源状态:")
                    for source, info in sources.items():
                        status = info.get('status', 'unknown')
                        emoji = "✅" if status == "available" else "❌"
                        print(f"  {emoji} {source}: {status}")
                    return True
                else:
                    print(f"❌ API失败: {data.get('message', 'N/A')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        return False
    
    def test_priority_config(self):
        """测试优先级配置"""
        print("\n⚙️ 优先级配置")
        print("-" * 40)
        
        try:
            response = requests.get(f"{self.base_url}/api/data-sources/priority/current", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    config = data.get('data', {})
                    current_profile = config.get('current_profile', 'unknown')
                    priorities = config.get('priorities', {})
                    
                    print(f"📋 当前配置: {current_profile}")
                    
                    us_basic = priorities.get('us_stock_basic_info', [])
                    if us_basic:
                        print(f"🇺🇸 美股基本信息优先级:")
                        for i, source in enumerate(us_basic, 1):
                            print(f"  {i}. {source}")
                    return True
                else:
                    print(f"❌ API失败: {data.get('message', 'N/A')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        return False
    
    def test_enhanced_api(self, symbol="AAPL"):
        """测试增强API"""
        print(f"\n🚀 增强API测试: {symbol}")
        print("-" * 40)
        
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/api/enhanced/stock/{symbol}",
                params={
                    "force_refresh": True,
                    "clear_all_cache": True,
                    "start_date": "2024-12-01",
                    "end_date": "2024-12-31"
                },
                timeout=120
            )
            end_time = time.time()
            
            print(f"⏱️ 响应时间: {end_time - start_time:.2f}秒")
            print(f"📡 HTTP状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data.get('data', {})
                    
                    print(f"✅ 请求成功")
                    print(f"📊 股票代码: {result.get('symbol', 'N/A')}")
                    print(f"📡 数据源: {result.get('data_source', 'N/A')}")
                    print(f"🌍 市场类型: {result.get('market_type', 'N/A')}")
                    
                    # 检查股票信息
                    stock_info = result.get('stock_info', {})
                    if stock_info:
                        print(f"🏢 公司名称: {stock_info.get('name', 'N/A')}")
                        print(f"💱 交易所: {stock_info.get('exchange', 'N/A')}")
                    
                    # 检查历史数据
                    historical_data = result.get('historical_data', [])
                    if historical_data:
                        print(f"📈 历史数据: {len(historical_data)} 条记录")
                    
                    return True
                else:
                    print(f"❌ API失败: {data.get('message', 'N/A')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"📄 响应内容: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        return False
    
    def test_multiple_symbols(self):
        """测试多个股票代码"""
        print(f"\n🔄 多股票测试")
        print("-" * 40)
        
        symbols = ["AAPL", "MSFT", "000001", "00700"]
        results = {}
        
        for symbol in symbols:
            try:
                print(f"\n📊 测试 {symbol}...")
                
                response = requests.get(
                    f"{self.base_url}/api/enhanced/stock/{symbol}",
                    params={"force_refresh": True},
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        result = data.get('data', {})
                        data_source = result.get('data_source', 'unknown')
                        market_type = result.get('market_type', 'unknown')
                        results[symbol] = f"{data_source} ({market_type})"
                        print(f"  ✅ {symbol}: {data_source} ({market_type})")
                    else:
                        results[symbol] = "failed"
                        print(f"  ❌ {symbol}: 失败")
                else:
                    results[symbol] = f"HTTP {response.status_code}"
                    print(f"  ❌ {symbol}: HTTP {response.status_code}")
                
                # 避免频率限制
                time.sleep(1)
                
            except Exception as e:
                results[symbol] = f"异常: {str(e)}"
                print(f"  ❌ {symbol}: 异常 - {e}")
        
        # 显示汇总
        print(f"\n📊 测试汇总:")
        for symbol, result in results.items():
            print(f"  {symbol}: {result}")
        
        return results
    
    def interactive_menu(self):
        """交互式菜单"""
        while True:
            print("\n" + "=" * 60)
            print("🧪 Data Source API 交互式测试工具")
            print("=" * 60)
            print("1. 🏥 健康检查")
            print("2. 🔧 数据源状态")
            print("3. ⚙️ 优先级配置")
            print("4. 🚀 增强API测试 (AAPL)")
            print("5. 📊 自定义股票测试")
            print("6. 🔄 多股票测试")
            print("7. 📋 查看API文档")
            print("0. 🚪 退出")
            print("-" * 60)
            
            try:
                choice = input("请选择操作 (0-7): ").strip()
                
                if choice == "0":
                    print("👋 再见！")
                    break
                elif choice == "1":
                    self.test_health()
                elif choice == "2":
                    self.test_data_sources_status()
                elif choice == "3":
                    self.test_priority_config()
                elif choice == "4":
                    self.test_enhanced_api("AAPL")
                elif choice == "5":
                    symbol = input("请输入股票代码: ").strip().upper()
                    if symbol:
                        self.test_enhanced_api(symbol)
                    else:
                        print("❌ 股票代码不能为空")
                elif choice == "6":
                    self.test_multiple_symbols()
                elif choice == "7":
                    self.show_api_docs()
                else:
                    print("❌ 无效选择，请重试")
                
                input("\n按回车键继续...")
                
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 操作失败: {e}")
                input("\n按回车键继续...")
    
    def show_api_docs(self):
        """显示API文档"""
        print("\n📋 API文档")
        print("-" * 40)
        print("📄 完整API文档: backend/DATA_SOURCE_API_REFERENCE.md")
        print()
        print("🔗 常用API端点:")
        print(f"  健康检查: {self.base_url}/health")
        print(f"  数据源状态: {self.base_url}/api/data-sources/status")
        print(f"  优先级配置: {self.base_url}/api/data-sources/priority/current")
        print(f"  增强API: {self.base_url}/api/enhanced/stock/{{symbol}}")
        print()
        print("💡 推荐使用增强API获取股票数据")
        print("🔧 使用 force_refresh=true 获取最新数据")
        print("🗑️ 使用 clear_all_cache=true 强制使用新数据源")
    
    def run_quick_test(self):
        """快速测试"""
        print("🚀 快速测试模式")
        print("=" * 60)
        
        # 1. 健康检查
        if not self.test_health():
            print("❌ 服务不可用，测试终止")
            return
        
        # 2. 数据源状态
        self.test_data_sources_status()
        
        # 3. 优先级配置
        self.test_priority_config()
        
        # 4. 增强API测试
        self.test_enhanced_api("AAPL")
        
        print("\n🎉 快速测试完成！")

def main():
    """主函数"""
    tester = DataSourceAPITester()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        tester.run_quick_test()
    else:
        tester.interactive_menu()

if __name__ == "__main__":
    main()
