#!/usr/bin/env python3
"""
美股数据源专项测试脚本
"""

import asyncio
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 添加 backend 目录到路径
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# 添加 data-service/app 目录到路径
data_service_app_path = backend_path / "data-service" / "app"
sys.path.insert(0, str(data_service_app_path))

class USStockSourceTester:
    """美股数据源测试器"""
    
    def __init__(self):
        self.test_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
        self.start_date = "2024-12-01"
        self.end_date = "2024-12-31"
        
    def check_api_keys(self):
        """检查API密钥配置"""
        print("🔑 检查美股数据源API密钥配置")
        print("=" * 50)
        
        # FinnHub API Key
        finnhub_key = os.getenv("FINNHUB_API_KEY")
        if finnhub_key:
            print(f"✅ FinnHub API Key: 已配置 ({finnhub_key[:8]}...)")
        else:
            print("❌ FinnHub API Key: 未配置")
        
        # Yahoo Finance (无需API Key)
        print("✅ Yahoo Finance: 无需API Key")
        
        # AKShare (无需API Key)
        print("✅ AKShare: 无需API Key")
        
        return finnhub_key is not None
    
    def test_finnhub_direct(self):
        """直接测试FinnHub API"""
        print("\n🌐 直接测试FinnHub API")
        print("=" * 50)
        
        try:
            import finnhub
            
            api_key = os.getenv("FINNHUB_API_KEY")
            if not api_key:
                print("❌ 未配置FINNHUB_API_KEY，跳过测试")
                return False
            
            client = finnhub.Client(api_key=api_key)
            
            for symbol in self.test_symbols[:2]:  # 只测试前两个，避免API限制
                try:
                    print(f"\n📊 测试股票: {symbol}")
                    
                    # 测试实时报价
                    print("  🔍 获取实时报价...")
                    quote = client.quote(symbol)
                    if quote and 'c' in quote:
                        print(f"    ✅ 当前价格: ${quote['c']:.2f}")
                        print(f"    📈 涨跌: ${quote.get('d', 0):.2f} ({quote.get('dp', 0):.2f}%)")
                    else:
                        print("    ❌ 实时报价获取失败")
                        continue
                    
                    # 测试公司信息
                    print("  🏢 获取公司信息...")
                    profile = client.company_profile2(symbol=symbol)
                    if profile and 'name' in profile:
                        print(f"    ✅ 公司名称: {profile['name']}")
                        print(f"    🏭 行业: {profile.get('finnhubIndustry', 'N/A')}")
                        print(f"    🌍 国家: {profile.get('country', 'N/A')}")
                    else:
                        print("    ❌ 公司信息获取失败")
                    
                    # 测试历史数据
                    print("  📈 获取历史数据...")
                    try:
                        from datetime import datetime
                        start_timestamp = int(datetime.strptime("2024-12-01", "%Y-%m-%d").timestamp())
                        end_timestamp = int(datetime.strptime("2024-12-31", "%Y-%m-%d").timestamp())
                        
                        candles = client.stock_candles(symbol, 'D', start_timestamp, end_timestamp)
                        if candles and candles.get('s') == 'ok' and candles.get('c'):
                            print(f"    ✅ 历史数据: {len(candles['c'])} 条记录")
                            print(f"    📊 价格范围: ${min(candles['l']):.2f} - ${max(candles['h']):.2f}")
                        else:
                            print("    ❌ 历史数据获取失败")
                    except Exception as e:
                        print(f"    ❌ 历史数据获取异常: {e}")
                    
                    # 等待避免API限制
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"    ❌ {symbol} 测试失败: {e}")
            
            print("\n✅ FinnHub API 测试完成")
            return True
            
        except ImportError:
            print("❌ finnhub 库未安装")
            return False
        except Exception as e:
            print(f"❌ FinnHub API 测试失败: {e}")
            return False
    
    def test_yfinance_direct(self):
        """直接测试Yahoo Finance"""
        print("\n🌐 直接测试Yahoo Finance")
        print("=" * 50)
        
        try:
            import yfinance as yf
            
            for symbol in self.test_symbols[:2]:  # 只测试前两个
                try:
                    print(f"\n📊 测试股票: {symbol}")
                    
                    # 创建ticker对象
                    ticker = yf.Ticker(symbol)
                    
                    # 测试基本信息
                    print("  🏢 获取基本信息...")
                    try:
                        info = ticker.info
                        if info and 'longName' in info:
                            print(f"    ✅ 公司名称: {info['longName']}")
                            print(f"    💰 市值: {info.get('marketCap', 'N/A')}")
                            print(f"    🏭 行业: {info.get('industry', 'N/A')}")
                        else:
                            print("    ⚠️ 基本信息获取部分失败")
                    except Exception as e:
                        print(f"    ❌ 基本信息获取失败: {e}")
                    
                    # 测试历史数据
                    print("  📈 获取历史数据...")
                    try:
                        hist = ticker.history(start=self.start_date, end=self.end_date)
                        if not hist.empty:
                            print(f"    ✅ 历史数据: {len(hist)} 条记录")
                            print(f"    📊 价格范围: ${hist['Low'].min():.2f} - ${hist['High'].max():.2f}")
                            print(f"    📅 日期范围: {hist.index[0].strftime('%Y-%m-%d')} 到 {hist.index[-1].strftime('%Y-%m-%d')}")
                        else:
                            print("    ❌ 历史数据为空")
                    except Exception as e:
                        print(f"    ❌ 历史数据获取失败: {e}")
                    
                    # 等待避免频率限制
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"    ❌ {symbol} 测试失败: {e}")
            
            print("\n✅ Yahoo Finance 测试完成")
            return True
            
        except ImportError:
            print("❌ yfinance 库未安装")
            return False
        except Exception as e:
            print(f"❌ Yahoo Finance 测试失败: {e}")
            return False
    
    def test_akshare_us_stocks(self):
        """测试AKShare美股数据"""
        print("\n🌐 测试AKShare美股数据")
        print("=" * 50)
        
        try:
            import akshare as ak
            
            # 测试美股实时数据
            print("📊 获取美股实时数据...")
            try:
                us_spot = ak.stock_us_spot_em()
                if not us_spot.empty:
                    print(f"✅ 美股实时数据: {len(us_spot)} 只股票")
                    
                    # 查找测试股票
                    for symbol in self.test_symbols[:2]:
                        stock_data = us_spot[us_spot['代码'] == symbol]
                        if not stock_data.empty:
                            stock_info = stock_data.iloc[0]
                            print(f"  📈 {symbol}: {stock_info['名称']} - ${stock_info['最新价']:.2f}")
                        else:
                            print(f"  ❌ {symbol}: 未找到数据")
                else:
                    print("❌ 美股实时数据为空")
            except Exception as e:
                print(f"❌ 美股实时数据获取失败: {e}")
            
            # 测试美股历史数据
            print("\n📈 测试美股历史数据...")
            for symbol in self.test_symbols[:1]:  # 只测试一个
                try:
                    print(f"  测试 {symbol} 历史数据...")
                    # AKShare的美股历史数据接口
                    hist_data = ak.stock_us_hist(symbol=symbol, period="daily", start_date="20241201", end_date="20241231")
                    if not hist_data.empty:
                        print(f"    ✅ {symbol} 历史数据: {len(hist_data)} 条记录")
                        print(f"    📊 价格范围: ${hist_data['最低'].min():.2f} - ${hist_data['最高'].max():.2f}")
                    else:
                        print(f"    ❌ {symbol} 历史数据为空")
                except Exception as e:
                    print(f"    ❌ {symbol} 历史数据获取失败: {e}")
                
                time.sleep(1)  # 避免频率限制
            
            print("\n✅ AKShare 美股测试完成")
            return True
            
        except ImportError:
            print("❌ akshare 库未安装")
            return False
        except Exception as e:
            print(f"❌ AKShare 测试失败: {e}")
            return False
    
    async def test_backend_data_sources(self):
        """测试backend数据源"""
        print("\n🔧 测试Backend数据源")
        print("=" * 50)
        
        try:
            from datasources.factory import init_data_source_factory
            from datasources.base import MarketType, DataCategory
            
            # 初始化数据源工厂
            factory = init_data_source_factory()
            
            # 测试FinnHub数据源
            print("📊 测试FinnHub数据源...")
            try:
                finnhub_source = factory.get_source("finnhub")
                if finnhub_source:
                    # 测试股票信息
                    symbol = "AAPL"
                    stock_info = await finnhub_source.get_stock_info(symbol, MarketType.US_STOCK)
                    if stock_info:
                        print(f"  ✅ FinnHub股票信息: {stock_info.get('name', 'N/A')}")
                    else:
                        print("  ❌ FinnHub股票信息获取失败")
                    
                    # 测试股票数据
                    stock_data = await finnhub_source.get_stock_data(symbol, MarketType.US_STOCK, self.start_date, self.end_date)
                    if stock_data:
                        print(f"  ✅ FinnHub股票数据: {len(stock_data)} 条记录")
                    else:
                        print("  ❌ FinnHub股票数据获取失败")
                else:
                    print("  ❌ FinnHub数据源不可用")
            except Exception as e:
                print(f"  ❌ FinnHub数据源测试失败: {e}")
            
            # 测试YFinance数据源
            print("\n📊 测试YFinance数据源...")
            try:
                yfinance_source = factory.get_source("yfinance")
                if yfinance_source:
                    symbol = "AAPL"
                    stock_info = await yfinance_source.get_stock_info(symbol, MarketType.US_STOCK)
                    if stock_info:
                        print(f"  ✅ YFinance股票信息: {stock_info.get('name', 'N/A')}")
                    else:
                        print("  ❌ YFinance股票信息获取失败")
                    
                    stock_data = await yfinance_source.get_stock_data(symbol, MarketType.US_STOCK, self.start_date, self.end_date)
                    if stock_data:
                        print(f"  ✅ YFinance股票数据: {len(stock_data)} 条记录")
                    else:
                        print("  ❌ YFinance股票数据获取失败")
                else:
                    print("  ❌ YFinance数据源不可用")
            except Exception as e:
                print(f"  ❌ YFinance数据源测试失败: {e}")
            
            # 测试AKShare数据源
            print("\n📊 测试AKShare数据源...")
            try:
                akshare_source = factory.get_source("akshare")
                if akshare_source:
                    symbol = "AAPL"
                    stock_info = await akshare_source.get_stock_info(symbol, MarketType.US_STOCK)
                    if stock_info:
                        print(f"  ✅ AKShare股票信息: {stock_info.get('name', 'N/A')}")
                    else:
                        print("  ❌ AKShare股票信息获取失败")
                    
                    stock_data = await akshare_source.get_stock_data(symbol, MarketType.US_STOCK, self.start_date, self.end_date)
                    if stock_data:
                        print(f"  ✅ AKShare股票数据: {len(stock_data)} 条记录")
                    else:
                        print("  ❌ AKShare股票数据获取失败")
                else:
                    print("  ❌ AKShare数据源不可用")
            except Exception as e:
                print(f"  ❌ AKShare数据源测试失败: {e}")
            
            print("\n✅ Backend数据源测试完成")
            return True
            
        except Exception as e:
            print(f"❌ Backend数据源测试失败: {e}")
            return False
    
    def test_tradingagents_sources(self):
        """测试tradingagents目录中的数据源"""
        print("\n🎯 测试TradingAgents数据源")
        print("=" * 50)
        
        try:
            # 添加tradingagents路径
            tradingagents_path = project_root / "tradingagents"
            sys.path.insert(0, str(tradingagents_path))
            
            # 测试优化的美股数据获取
            print("📊 测试优化美股数据获取...")
            try:
                from dataflows.optimized_us_data import get_us_stock_data_cached
                
                symbol = "AAPL"
                result = get_us_stock_data_cached(symbol, self.start_date, self.end_date, force_refresh=True)
                
                if result and "❌" not in result:
                    print(f"  ✅ 优化美股数据获取成功")
                    print(f"  📄 数据长度: {len(result)} 字符")
                    print(f"  📋 数据预览: {result[:200]}...")
                else:
                    print(f"  ❌ 优化美股数据获取失败")
                    print(f"  📄 返回内容: {result}")
            except Exception as e:
                print(f"  ❌ 优化美股数据获取异常: {e}")
            
            # 测试Yahoo Finance接口
            print("\n📊 测试Yahoo Finance接口...")
            try:
                from dataflows.interface import get_YFin_data_online
                
                symbol = "AAPL"
                result = get_YFin_data_online(symbol, self.start_date, self.end_date)
                
                if result and "No data found" not in result:
                    print(f"  ✅ Yahoo Finance接口成功")
                    print(f"  📄 数据长度: {len(result)} 字符")
                    lines = result.split('\n')
                    data_lines = [line for line in lines if ',' in line and not line.startswith('#')]
                    print(f"  📊 数据行数: {len(data_lines)} 条记录")
                else:
                    print(f"  ❌ Yahoo Finance接口失败")
                    print(f"  📄 返回内容: {result}")
            except Exception as e:
                print(f"  ❌ Yahoo Finance接口异常: {e}")
            
            print("\n✅ TradingAgents数据源测试完成")
            return True
            
        except Exception as e:
            print(f"❌ TradingAgents数据源测试失败: {e}")
            return False
    
    def run_full_test(self):
        """运行完整的美股数据源测试"""
        print("🇺🇸 美股数据源专项测试")
        print("=" * 60)
        
        # 1. 检查API密钥
        has_finnhub_key = self.check_api_keys()
        
        # 2. 直接测试各个数据源
        print("\n" + "=" * 60)
        print("🔍 直接测试各个数据源API")
        
        if has_finnhub_key:
            self.test_finnhub_direct()
        else:
            print("\n⚠️ 跳过FinnHub测试（未配置API Key）")
        
        self.test_yfinance_direct()
        self.test_akshare_us_stocks()
        
        # 3. 测试backend数据源
        print("\n" + "=" * 60)
        print("🔧 测试Backend集成数据源")
        try:
            asyncio.run(self.test_backend_data_sources())
        except Exception as e:
            print(f"❌ Backend数据源测试失败: {e}")
        
        # 4. 测试tradingagents数据源
        print("\n" + "=" * 60)
        print("🎯 测试TradingAgents集成数据源")
        self.test_tradingagents_sources()
        
        print("\n" + "=" * 60)
        print("🎉 美股数据源测试完成！")
        print("\n💡 建议:")
        print("1. 如果FinnHub失败，检查API Key配置和配额")
        print("2. 如果Yahoo Finance失败，可能是频率限制，稍后重试")
        print("3. 如果AKShare失败，检查网络连接和库版本")
        print("4. 建议配置多个数据源作为备用方案")

def main():
    """主函数"""
    tester = USStockSourceTester()
    tester.run_full_test()

if __name__ == "__main__":
    main()
