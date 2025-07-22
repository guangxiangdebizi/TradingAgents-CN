#!/usr/bin/env python3
"""
测试新的美股数据源 - Alpha Vantage 和 IEX Cloud
"""

import asyncio
import sys
import os
import requests
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class NewUSDataSourceTester:
    """新美股数据源测试器"""
    
    def __init__(self):
        self.data_service_url = "http://localhost:8002"
        self.test_symbols = ["AAPL", "MSFT", "GOOGL"]
    
    def check_api_keys(self):
        """检查新数据源的API密钥配置"""
        print("🔑 检查新美股数据源API密钥配置")
        print("=" * 50)
        
        # Alpha Vantage API Key
        alpha_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if alpha_key:
            print(f"✅ Alpha Vantage API Key: 已配置 ({alpha_key[:8]}...)")
        else:
            print("❌ Alpha Vantage API Key: 未配置")
            print("💡 获取地址: https://www.alphavantage.co/support/#api-key")
        
        # IEX Cloud API Key
        iex_key = os.getenv("IEX_CLOUD_API_KEY")
        if iex_key:
            print(f"✅ IEX Cloud API Key: 已配置 ({iex_key[:8]}...)")
        else:
            print("❌ IEX Cloud API Key: 未配置")
            print("💡 获取地址: https://iexcloud.io/")
        
        return alpha_key is not None, iex_key is not None
    
    def test_direct_alpha_vantage(self):
        """直接测试Alpha Vantage API"""
        print("\n🌐 直接测试Alpha Vantage API")
        print("=" * 50)
        
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not api_key:
            print("❌ 未配置Alpha Vantage API Key，跳过测试")
            return False
        
        try:
            # 测试实时报价
            print("📊 测试Alpha Vantage实时报价...")
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': 'AAPL',
                'apikey': api_key
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                
                if "Global Quote" in data:
                    quote = data["Global Quote"]
                    price = quote.get("05. price", "N/A")
                    change = quote.get("09. change", "N/A")
                    print(f"  ✅ AAPL价格: ${price}")
                    print(f"  📈 涨跌: ${change}")
                elif "Note" in data:
                    print(f"  ⚠️ API频率限制: {data['Note']}")
                elif "Error Message" in data:
                    print(f"  ❌ API错误: {data['Error Message']}")
                else:
                    print(f"  ❌ 未知响应格式: {data}")
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
            
            # 测试公司信息
            print("\n📊 测试Alpha Vantage公司信息...")
            params = {
                'function': 'OVERVIEW',
                'symbol': 'AAPL',
                'apikey': api_key
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                
                if "Symbol" in data:
                    print(f"  ✅ 公司名称: {data.get('Name', 'N/A')}")
                    print(f"  🏭 行业: {data.get('Industry', 'N/A')}")
                    print(f"  💰 市值: {data.get('MarketCapitalization', 'N/A')}")
                else:
                    print(f"  ❌ 公司信息获取失败: {data}")
            
            return True
            
        except Exception as e:
            print(f"❌ Alpha Vantage测试失败: {e}")
            return False
    
    def test_direct_iex_cloud(self):
        """直接测试IEX Cloud API"""
        print("\n🌐 直接测试IEX Cloud API")
        print("=" * 50)
        
        api_key = os.getenv("IEX_CLOUD_API_KEY")
        if not api_key:
            print("❌ 未配置IEX Cloud API Key，跳过测试")
            return False
        
        try:
            # 测试实时报价
            print("📊 测试IEX Cloud实时报价...")
            url = f"https://cloud.iexapis.com/stable/stock/AAPL/quote"
            params = {'token': api_key}
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                
                price = data.get("latestPrice", "N/A")
                change = data.get("change", "N/A")
                company_name = data.get("companyName", "N/A")
                
                print(f"  ✅ {company_name}: ${price}")
                print(f"  📈 涨跌: ${change}")
                print(f"  📊 市值: {data.get('marketCap', 'N/A')}")
                print(f"  📈 PE比率: {data.get('peRatio', 'N/A')}")
            elif response.status_code == 402:
                print(f"  ❌ API配额不足")
            elif response.status_code == 429:
                print(f"  ❌ API频率限制")
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
            
            # 测试公司信息
            print("\n📊 测试IEX Cloud公司信息...")
            url = f"https://cloud.iexapis.com/stable/stock/AAPL/company"
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                
                print(f"  ✅ 公司名称: {data.get('companyName', 'N/A')}")
                print(f"  🏭 行业: {data.get('industry', 'N/A')}")
                print(f"  🌍 国家: {data.get('country', 'N/A')}")
                print(f"  👥 员工数: {data.get('employees', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"❌ IEX Cloud测试失败: {e}")
            return False
    
    def test_enhanced_api_with_new_sources(self):
        """测试增强API使用新数据源"""
        print("\n🚀 测试增强API使用新数据源")
        print("=" * 50)
        
        try:
            # 强制刷新以确保使用最新的数据源优先级
            response = requests.get(
                f"{self.data_service_url}/api/enhanced/stock/AAPL",
                params={
                    "force_refresh": True,
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
                    
                    print(f"✅ 增强API调用成功")
                    print(f"📊 股票代码: {result.get('symbol', 'N/A')}")
                    print(f"📡 使用的数据源: {data_source}")
                    print(f"🌍 市场类型: {result.get('market_type', 'N/A')}")
                    
                    # 检查是否使用了新的数据源
                    if data_source in ["alpha_vantage", "iex_cloud"]:
                        print(f"🎉 成功使用新数据源: {data_source}")
                    elif data_source == "finnhub":
                        print(f"⚠️ 使用了FinnHub数据源，新数据源可能未配置")
                    else:
                        print(f"⚠️ 使用了其他数据源: {data_source}")
                    
                    # 显示格式化数据预览
                    formatted_data = result.get("formatted_data", "")
                    if formatted_data:
                        lines = formatted_data.split('\n')[:8]
                        print(f"\n📋 格式化数据预览:")
                        for line in lines:
                            print(f"  {line}")
                    
                    return True
                else:
                    print(f"❌ API返回失败: {data.get('message', 'N/A')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"📄 响应内容: {response.text}")
            
        except Exception as e:
            print(f"❌ 增强API测试失败: {e}")
        
        return False
    
    def test_data_source_priority(self):
        """测试数据源优先级"""
        print("\n🎯 测试数据源优先级")
        print("=" * 50)
        
        # 测试多个股票，观察使用的数据源
        for symbol in self.test_symbols:
            try:
                print(f"\n📊 测试股票: {symbol}")
                
                response = requests.get(
                    f"{self.data_service_url}/api/enhanced/stock/{symbol}",
                    params={"force_refresh": True},
                    timeout=120
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        result = data.get("data", {})
                        data_source = result.get("data_source", "unknown")
                        print(f"  📡 数据源: {data_source}")
                        
                        # 统计数据源使用情况
                        if not hasattr(self, 'source_stats'):
                            self.source_stats = {}
                        
                        self.source_stats[data_source] = self.source_stats.get(data_source, 0) + 1
                    else:
                        print(f"  ❌ 获取失败: {data.get('message', 'N/A')}")
                else:
                    print(f"  ❌ HTTP错误: {response.status_code}")
                
                # 避免频率限制
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ 测试异常: {e}")
        
        # 显示统计结果
        if hasattr(self, 'source_stats'):
            print(f"\n📊 数据源使用统计:")
            for source, count in self.source_stats.items():
                print(f"  {source}: {count} 次")
    
    def run_full_test(self):
        """运行完整测试"""
        print("🆕 新美股数据源测试")
        print("=" * 60)
        
        # 1. 检查API密钥
        has_alpha, has_iex = self.check_api_keys()
        
        # 2. 直接测试API
        if has_alpha:
            self.test_direct_alpha_vantage()
        
        if has_iex:
            self.test_direct_iex_cloud()
        
        # 3. 测试增强API
        self.test_enhanced_api_with_new_sources()
        
        # 4. 测试数据源优先级
        self.test_data_source_priority()
        
        print("\n🎉 新美股数据源测试完成！")
        print("\n💡 总结:")
        if has_alpha:
            print("✅ Alpha Vantage: 已配置，可以使用")
        else:
            print("❌ Alpha Vantage: 未配置API Key")
        
        if has_iex:
            print("✅ IEX Cloud: 已配置，可以使用")
        else:
            print("❌ IEX Cloud: 未配置API Key")
        
        print("\n🔧 配置建议:")
        if not has_alpha:
            print("1. 获取Alpha Vantage免费API Key: https://www.alphavantage.co/support/#api-key")
            print("   export ALPHA_VANTAGE_API_KEY=your_key_here")
        
        if not has_iex:
            print("2. 获取IEX Cloud免费API Key: https://iexcloud.io/")
            print("   export IEX_CLOUD_API_KEY=your_key_here")

def main():
    """主函数"""
    tester = NewUSDataSourceTester()
    tester.run_full_test()

if __name__ == "__main__":
    main()
