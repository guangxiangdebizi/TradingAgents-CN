#!/usr/bin/env python3
"""
智能美股数据源测试脚本 - 包含重试机制和错误分析
"""

import sys
import os
import time
import random
import requests
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class SmartUSStockTester:
    """智能美股数据源测试器"""
    
    def __init__(self):
        self.test_symbols = ["AAPL"]  # 只测试一个股票，减少请求
        self.start_date = "2024-12-01"
        self.end_date = "2024-12-31"
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
    
    def check_network_and_ip(self):
        """检查网络状态和IP信息"""
        print("🌐 检查网络状态和IP信息")
        print("=" * 50)
        
        try:
            # 检查基本网络连接
            response = requests.get("https://httpbin.org/ip", timeout=10)
            if response.status_code == 200:
                ip_info = response.json()
                print(f"✅ 网络连接正常")
                print(f"📍 当前IP: {ip_info.get('origin', 'N/A')}")
            else:
                print(f"⚠️ 网络连接异常: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ 网络连接失败: {e}")
        
        try:
            # 检查是否能访问Yahoo Finance
            response = requests.get("https://finance.yahoo.com", timeout=10, 
                                  headers={'User-Agent': random.choice(self.user_agents)})
            print(f"📊 Yahoo Finance访问: HTTP {response.status_code}")
            
            # 检查是否能访问FinnHub
            response = requests.get("https://finnhub.io", timeout=10)
            print(f"📈 FinnHub访问: HTTP {response.status_code}")
            
        except Exception as e:
            print(f"❌ 网站访问测试失败: {e}")
    
    def test_yfinance_with_retry(self, max_retries=3, wait_time=30):
        """带重试机制的Yahoo Finance测试"""
        print(f"\n🔄 Yahoo Finance智能重试测试 (最多{max_retries}次)")
        print("=" * 50)
        
        for attempt in range(max_retries):
            try:
                print(f"\n📊 第 {attempt + 1} 次尝试...")
                
                # 随机等待时间，避免被检测为机器人
                if attempt > 0:
                    wait = wait_time + random.randint(5, 15)
                    print(f"⏳ 等待 {wait} 秒后重试...")
                    time.sleep(wait)
                
                import yfinance as yf
                
                # 使用随机User-Agent
                session = requests.Session()
                session.headers.update({'User-Agent': random.choice(self.user_agents)})
                
                symbol = "AAPL"
                print(f"  🎯 测试股票: {symbol}")
                
                # 创建ticker对象，使用自定义session
                ticker = yf.Ticker(symbol, session=session)
                
                # 测试基本信息（较少触发限制）
                print("  📋 获取基本信息...")
                try:
                    info = ticker.info
                    if info and len(info) > 5:  # 检查是否有实际数据
                        company_name = info.get('longName', info.get('shortName', 'N/A'))
                        print(f"    ✅ 公司名称: {company_name}")
                        print(f"    💰 市值: {info.get('marketCap', 'N/A')}")
                        return True  # 成功获取数据，退出重试
                    else:
                        print("    ⚠️ 基本信息数据不完整")
                except Exception as e:
                    print(f"    ❌ 基本信息获取失败: {e}")
                
                # 如果基本信息失败，尝试历史数据
                print("  📈 尝试获取少量历史数据...")
                try:
                    # 只获取最近5天的数据，减少请求负担
                    recent_date = datetime.now() - timedelta(days=5)
                    hist = ticker.history(period="5d")
                    
                    if not hist.empty:
                        print(f"    ✅ 历史数据: {len(hist)} 条记录")
                        print(f"    📊 最新价格: ${hist['Close'].iloc[-1]:.2f}")
                        return True
                    else:
                        print("    ❌ 历史数据为空")
                except Exception as e:
                    print(f"    ❌ 历史数据获取失败: {e}")
                
            except Exception as e:
                print(f"  ❌ 第 {attempt + 1} 次尝试失败: {e}")
                
                # 分析错误类型
                error_str = str(e).lower()
                if "rate limit" in error_str or "too many requests" in error_str:
                    print("  🚫 确认是频率限制错误")
                elif "timeout" in error_str:
                    print("  ⏰ 网络超时错误")
                elif "connection" in error_str:
                    print("  🌐 网络连接错误")
                else:
                    print("  ❓ 未知错误类型")
        
        print(f"\n❌ Yahoo Finance在 {max_retries} 次尝试后仍然失败")
        return False
    
    def test_alternative_yfinance_methods(self):
        """测试Yahoo Finance的替代方法"""
        print(f"\n🔧 测试Yahoo Finance替代方法")
        print("=" * 50)
        
        symbol = "AAPL"
        
        # 方法1: 使用不同的数据接口
        try:
            print("📊 方法1: 使用Yahoo Finance的CSV接口...")
            
            # 构造Yahoo Finance的CSV下载URL
            import urllib.parse
            from datetime import datetime
            
            # 转换日期为时间戳
            start_timestamp = int(datetime.strptime("2024-12-01", "%Y-%m-%d").timestamp())
            end_timestamp = int(datetime.strptime("2024-12-31", "%Y-%m-%d").timestamp())
            
            csv_url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}"
            params = {
                'period1': start_timestamp,
                'period2': end_timestamp,
                'interval': '1d',
                'events': 'history'
            }
            
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/csv,application/csv',
                'Referer': 'https://finance.yahoo.com/'
            }
            
            response = requests.get(csv_url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                csv_data = response.text
                lines = csv_data.strip().split('\n')
                if len(lines) > 1:  # 有数据行
                    print(f"    ✅ CSV接口成功: {len(lines)-1} 条数据")
                    print(f"    📄 数据预览: {lines[1]}")  # 显示第一行数据
                    return True
                else:
                    print("    ❌ CSV数据为空")
            else:
                print(f"    ❌ CSV接口失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ CSV接口异常: {e}")
        
        # 方法2: 使用Yahoo Finance的JSON API
        try:
            print("\n📊 方法2: 使用Yahoo Finance的JSON API...")
            
            json_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                'period1': start_timestamp,
                'period2': end_timestamp,
                'interval': '1d'
            }
            
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'application/json',
                'Referer': 'https://finance.yahoo.com/'
            }
            
            response = requests.get(json_url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                json_data = response.json()
                chart = json_data.get('chart', {})
                result = chart.get('result', [])
                
                if result and len(result) > 0:
                    timestamps = result[0].get('timestamp', [])
                    indicators = result[0].get('indicators', {})
                    quote = indicators.get('quote', [{}])[0] if indicators.get('quote') else {}
                    
                    if timestamps and quote.get('close'):
                        print(f"    ✅ JSON API成功: {len(timestamps)} 条数据")
                        print(f"    📊 最新价格: ${quote['close'][-1]:.2f}")
                        return True
                    else:
                        print("    ❌ JSON数据结构异常")
                else:
                    print("    ❌ JSON响应无数据")
            else:
                print(f"    ❌ JSON API失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ JSON API异常: {e}")
        
        return False
    
    def test_finnhub_quota_info(self):
        """检查FinnHub配额信息"""
        print(f"\n📊 检查FinnHub配额信息")
        print("=" * 50)
        
        try:
            import finnhub
            
            api_key = os.getenv("FINNHUB_API_KEY")
            if not api_key:
                print("❌ 未配置FINNHUB_API_KEY")
                return False
            
            client = finnhub.Client(api_key=api_key)
            
            # 获取API使用情况（如果有的话）
            try:
                # 尝试一个简单的请求来检查配额
                quote = client.quote("AAPL")
                if quote and 'c' in quote:
                    print(f"✅ FinnHub API正常工作")
                    print(f"📊 AAPL当前价格: ${quote['c']:.2f}")
                    
                    # 检查响应头中的配额信息
                    print("📋 API配额信息:")
                    print("   注意: FinnHub免费版限制:")
                    print("   - 每分钟60次请求")
                    print("   - 历史数据需要付费订阅")
                    print("   - 实时数据和基本信息免费")
                    
                    return True
                else:
                    print("❌ FinnHub API响应异常")
                    return False
                    
            except Exception as e:
                error_str = str(e)
                if "403" in error_str:
                    print("❌ FinnHub 403错误: 可能是免费配额限制")
                    print("💡 建议: 升级到付费计划或使用其他数据源")
                elif "429" in error_str:
                    print("❌ FinnHub 429错误: 请求频率过高")
                    print("💡 建议: 降低请求频率")
                else:
                    print(f"❌ FinnHub API错误: {e}")
                return False
                
        except ImportError:
            print("❌ finnhub库未安装")
            return False
        except Exception as e:
            print(f"❌ FinnHub测试失败: {e}")
            return False
    
    def suggest_solutions(self):
        """提供解决方案建议"""
        print(f"\n💡 解决方案建议")
        print("=" * 50)
        
        print("🔧 针对频率限制问题:")
        print("1. 等待更长时间 (1-2小时) 后重试")
        print("2. 使用VPN更换IP地址")
        print("3. 配置代理服务器")
        print("4. 使用多个数据源轮换")
        
        print("\n📊 数据源替代方案:")
        print("1. Alpha Vantage (免费API)")
        print("2. IEX Cloud (部分免费)")
        print("3. Quandl/NASDAQ Data Link")
        print("4. 本地数据文件")
        
        print("\n⚙️ 技术优化:")
        print("1. 实现请求缓存机制")
        print("2. 添加随机延迟")
        print("3. 使用会话池")
        print("4. 实现指数退避重试")
        
        print("\n🎯 当前可用方案:")
        print("1. ✅ FinnHub实时数据 (基本信息和报价)")
        print("2. ✅ TradingAgents优化接口 (已验证可用)")
        print("3. ⚠️ Yahoo Finance (需要等待或技术优化)")
        print("4. ❌ AKShare美股 (数据格式问题)")
    
    def run_smart_test(self):
        """运行智能测试"""
        print("🧠 智能美股数据源测试")
        print("=" * 60)
        
        # 1. 网络和IP检查
        self.check_network_and_ip()
        
        # 2. FinnHub配额检查
        self.test_finnhub_quota_info()
        
        # 3. Yahoo Finance智能重试
        yf_success = self.test_yfinance_with_retry()
        
        # 4. 如果常规方法失败，尝试替代方法
        if not yf_success:
            print("\n🔄 常规方法失败，尝试替代方法...")
            self.test_alternative_yfinance_methods()
        
        # 5. 提供解决方案
        self.suggest_solutions()
        
        print("\n🎉 智能测试完成！")

def main():
    """主函数"""
    tester = SmartUSStockTester()
    tester.run_smart_test()

if __name__ == "__main__":
    main()
