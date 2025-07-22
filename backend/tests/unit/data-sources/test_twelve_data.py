#!/usr/bin/env python3
"""
测试Twelve Data数据源 - 专门测试新添加的Twelve Data API
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

class TwelveDataTester:
    """Twelve Data数据源测试器"""
    
    def __init__(self):
        self.data_service_url = "http://localhost:8002"
        self.test_symbols = ["AAPL", "MSFT", "GOOGL"]
    
    def check_api_key(self):
        """检查Twelve Data API密钥配置"""
        print("🔑 检查Twelve Data API密钥配置")
        print("=" * 50)
        
        api_key = os.getenv("TWELVE_DATA_API_KEY")
        if api_key:
            print(f"✅ Twelve Data API Key: 已配置 ({api_key[:8]}...)")
            return True
        else:
            print("❌ Twelve Data API Key: 未配置")
            print("💡 获取地址: https://twelvedata.com/")
            print("📋 获取步骤:")
            print("   1. 访问 https://twelvedata.com/")
            print("   2. 点击 'Get free API key'")
            print("   3. 注册账户并验证邮箱")
            print("   4. 登录后在控制台获取API Key")
            print("   5. 设置环境变量: TWELVE_DATA_API_KEY=your_key_here")
            return False
    
    def test_direct_twelve_data_api(self):
        """直接测试Twelve Data API"""
        print("\n🌐 直接测试Twelve Data API")
        print("=" * 50)
        
        api_key = os.getenv("TWELVE_DATA_API_KEY")
        if not api_key:
            print("❌ 未配置Twelve Data API Key，跳过测试")
            return False
        
        try:
            # 测试实时报价
            print("📊 测试Twelve Data实时报价...")
            url = "https://api.twelvedata.com/quote"
            params = {
                'symbol': 'AAPL',
                'apikey': api_key
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                
                if "code" in data and data["code"] != 200:
                    if data["code"] == 429:
                        print(f"  ⚠️ API频率限制: {data.get('message', 'Rate limit exceeded')}")
                    elif data["code"] == 401:
                        print(f"  ❌ API Key无效: {data.get('message', 'Invalid API key')}")
                    else:
                        print(f"  ❌ API错误 {data['code']}: {data.get('message', 'Unknown error')}")
                elif "close" in data:
                    price = data.get("close", "N/A")
                    change = data.get("change", "N/A")
                    percent_change = data.get("percent_change", "N/A")
                    
                    print(f"  ✅ AAPL价格: ${price}")
                    print(f"  📈 涨跌: ${change} ({percent_change}%)")
                    print(f"  📊 开盘: ${data.get('open', 'N/A')}")
                    print(f"  📊 最高: ${data.get('high', 'N/A')}")
                    print(f"  📊 最低: ${data.get('low', 'N/A')}")
                    print(f"  📊 成交量: {data.get('volume', 'N/A')}")
                else:
                    print(f"  ❌ 未知响应格式: {data}")
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
                print(f"  📄 响应内容: {response.text}")
            
            # 测试股票基本信息
            print("\n📊 测试Twelve Data股票基本信息...")
            url = "https://api.twelvedata.com/profile"
            params = {
                'symbol': 'AAPL',
                'apikey': api_key
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                
                if "name" in data:
                    print(f"  ✅ 公司名称: {data.get('name', 'N/A')}")
                    print(f"  🏭 行业: {data.get('industry', 'N/A')}")
                    print(f"  🏢 部门: {data.get('sector', 'N/A')}")
                    print(f"  🌍 国家: {data.get('country', 'N/A')}")
                    print(f"  💰 市值: {data.get('market_cap', 'N/A')}")
                else:
                    print(f"  ❌ 基本信息获取失败: {data}")
            else:
                print(f"  ❌ 基本信息HTTP错误: {response.status_code}")
            
            # 测试历史数据
            print("\n📊 测试Twelve Data历史数据...")
            url = "https://api.twelvedata.com/time_series"
            params = {
                'symbol': 'AAPL',
                'interval': '1day',
                'start_date': '2024-12-01',
                'end_date': '2024-12-31',
                'format': 'JSON',
                'apikey': api_key
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                
                if "values" in data and data["values"]:
                    values = data["values"]
                    print(f"  ✅ 历史数据: {len(values)} 条记录")
                    
                    # 显示最新的几条数据
                    for i, record in enumerate(values[:3]):
                        date = record.get("datetime", "N/A")
                        close = record.get("close", "N/A")
                        volume = record.get("volume", "N/A")
                        print(f"    {date}: ${close} (成交量: {volume})")
                else:
                    print(f"  ❌ 历史数据获取失败: {data}")
            else:
                print(f"  ❌ 历史数据HTTP错误: {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"❌ Twelve Data测试失败: {e}")
            return False
    
    def test_enhanced_api_with_twelve_data(self):
        """测试增强API使用Twelve Data"""
        print("\n🚀 测试增强API使用Twelve Data")
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
                    
                    # 检查是否使用了Twelve Data
                    if data_source == "twelve_data":
                        print(f"🎉 成功使用Twelve Data数据源！")
                        
                        # 显示格式化数据预览
                        formatted_data = result.get("formatted_data", "")
                        if formatted_data:
                            lines = formatted_data.split('\n')[:10]
                            print(f"\n📋 Twelve Data格式化数据预览:")
                            for line in lines:
                                print(f"  {line}")
                        
                        return True
                    else:
                        print(f"⚠️ 使用了其他数据源: {data_source}")
                        print(f"💡 可能原因: Twelve Data API Key未配置或优先级较低")
                else:
                    print(f"❌ API返回失败: {data.get('message', 'N/A')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"📄 响应内容: {response.text}")
            
        except Exception as e:
            print(f"❌ 增强API测试失败: {e}")
        
        return False
    
    def test_twelve_data_rate_limits(self):
        """测试Twelve Data频率限制"""
        print("\n⏱️ 测试Twelve Data频率限制")
        print("=" * 50)
        
        api_key = os.getenv("TWELVE_DATA_API_KEY")
        if not api_key:
            print("❌ 未配置Twelve Data API Key，跳过测试")
            return
        
        print("📊 连续请求测试 (免费版每分钟8次请求)...")
        
        success_count = 0
        rate_limit_hit = False
        
        for i in range(10):  # 尝试10次请求
            try:
                print(f"  请求 {i+1}/10...", end=" ")
                
                url = "https://api.twelvedata.com/quote"
                params = {
                    'symbol': 'AAPL',
                    'apikey': api_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if "code" in data and data["code"] == 429:
                        print("❌ 频率限制")
                        rate_limit_hit = True
                        break
                    elif "close" in data:
                        print("✅ 成功")
                        success_count += 1
                    else:
                        print(f"⚠️ 异常响应: {data}")
                else:
                    print(f"❌ HTTP {response.status_code}")
                
                # 等待一段时间避免过快请求
                time.sleep(8)  # 等待8秒，理论上每分钟可以请求7-8次
                
            except Exception as e:
                print(f"❌ 异常: {e}")
        
        print(f"\n📊 测试结果:")
        print(f"  成功请求: {success_count} 次")
        print(f"  是否遇到频率限制: {'是' if rate_limit_hit else '否'}")
        
        if success_count >= 7:
            print("✅ Twelve Data API工作正常")
        elif rate_limit_hit:
            print("⚠️ 遇到频率限制，这是正常的（免费版限制）")
        else:
            print("❌ API可能存在问题")
    
    def run_full_test(self):
        """运行完整测试"""
        print("🌟 Twelve Data数据源专项测试")
        print("=" * 60)
        
        # 1. 检查API密钥
        has_key = self.check_api_key()
        
        if not has_key:
            print("\n❌ 无法进行测试，请先配置Twelve Data API Key")
            return
        
        # 2. 直接测试API
        api_success = self.test_direct_twelve_data_api()
        
        if not api_success:
            print("\n❌ 直接API测试失败，跳过后续测试")
            return
        
        # 3. 测试增强API
        self.test_enhanced_api_with_twelve_data()
        
        # 4. 测试频率限制
        print("\n" + "=" * 60)
        choice = input("❓ 是否测试频率限制？(这会发送多个请求) (y/N): ").strip().lower()
        if choice in ['y', 'yes']:
            self.test_twelve_data_rate_limits()
        
        print("\n🎉 Twelve Data测试完成！")
        print("\n💡 总结:")
        print("✅ Twelve Data特点:")
        print("   - 每天800次请求，每分钟8次请求")
        print("   - 支持全球市场（美股、港股等）")
        print("   - 访问稳定，在中国地区可正常使用")
        print("   - API设计简洁，响应速度快")
        print("   - 是Yahoo Finance的优秀替代方案")

def main():
    """主函数"""
    tester = TwelveDataTester()
    tester.run_full_test()

if __name__ == "__main__":
    main()
