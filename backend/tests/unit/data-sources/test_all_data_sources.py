#!/usr/bin/env python3
"""
测试所有数据源的完整脚本
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 添加 backend 目录到路径
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# 添加 data-service/app 目录到路径
data_service_app_path = backend_path / "data-service" / "app"
sys.path.insert(0, str(data_service_app_path))

# 直接导入
from datasources.factory import init_data_source_factory
from datasources.base import MarketType, DataCategory, DataSourceType

async def test_individual_data_sources():
    """测试各个数据源"""
    print("🧪 测试各个数据源")
    print("=" * 50)
    
    # 初始化数据源工厂
    factory = init_data_source_factory()
    
    # 测试数据
    test_cases = [
        {
            "name": "A股测试",
            "symbol": "000858",
            "market": MarketType.A_SHARE,
            "expected_sources": [DataSourceType.TUSHARE, DataSourceType.AKSHARE, DataSourceType.BAOSTOCK]
        },
        {
            "name": "美股测试", 
            "symbol": "AAPL",
            "market": MarketType.US_STOCK,
            "expected_sources": [DataSourceType.FINNHUB, DataSourceType.YFINANCE]
        },
        {
            "name": "港股测试",
            "symbol": "00700",
            "market": MarketType.HK_STOCK,
            "expected_sources": [DataSourceType.AKSHARE, DataSourceType.YFINANCE]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📊 {test_case['name']}: {test_case['symbol']}")
        print("-" * 30)
        
        # 测试基本信息
        print("🔍 测试基本信息...")
        available_sources = factory.get_available_sources(test_case['market'], DataCategory.BASIC_INFO)
        print(f"   可用数据源: {[s.source_type.value for s in available_sources]}")
        
        try:
            result = await factory.get_stock_info(test_case['symbol'], test_case['market'])
            if result:
                print(f"   ✅ 成功: {result.get('name', 'N/A')} - 来源: {result.get('source', 'N/A')}")
            else:
                print(f"   ❌ 失败: 无法获取基本信息")
        except Exception as e:
            print(f"   ❌ 异常: {e}")
        
        # 测试价格数据
        print("📈 测试价格数据...")
        available_sources = factory.get_available_sources(test_case['market'], DataCategory.PRICE_DATA)
        print(f"   可用数据源: {[s.source_type.value for s in available_sources]}")
        
        try:
            result = await factory.get_stock_data(
                test_case['symbol'], 
                test_case['market'], 
                "2024-01-01", 
                "2024-01-10"
            )
            if result:
                print(f"   ✅ 成功: 获取到 {len(result)} 条数据")
            else:
                print(f"   ❌ 失败: 无法获取价格数据")
        except Exception as e:
            print(f"   ❌ 异常: {e}")

async def test_data_source_priority():
    """测试数据源优先级"""
    print("\n🎯 测试数据源优先级")
    print("=" * 50)
    
    factory = init_data_source_factory()
    
    # 测试不同市场和数据类型的优先级
    test_priorities = [
        (MarketType.A_SHARE, DataCategory.BASIC_INFO, "A股基本信息"),
        (MarketType.A_SHARE, DataCategory.PRICE_DATA, "A股价格数据"),
        (MarketType.US_STOCK, DataCategory.BASIC_INFO, "美股基本信息"),
        (MarketType.US_STOCK, DataCategory.PRICE_DATA, "美股价格数据"),
        (MarketType.HK_STOCK, DataCategory.BASIC_INFO, "港股基本信息"),
        (MarketType.HK_STOCK, DataCategory.PRICE_DATA, "港股价格数据"),
    ]
    
    for market, category, description in test_priorities:
        sources = factory.get_available_sources(market, category)
        source_names = [s.source_type.value for s in sources]
        print(f"📋 {description}: {' → '.join(source_names) if source_names else '无可用数据源'}")

async def test_data_source_health():
    """测试数据源健康状态"""
    print("\n🔍 测试数据源健康状态")
    print("=" * 50)
    
    factory = init_data_source_factory()
    health_status = await factory.health_check_all()
    
    for source, status in health_status.items():
        status_icon = "✅" if status.get('status') == 'healthy' else "❌"
        print(f"   {status_icon} {source}: {status.get('status', 'unknown')}")
        
        if 'stats' in status:
            stats = status['stats']
            print(f"      请求次数: {stats.get('request_count', 0)}")
            print(f"      错误次数: {stats.get('error_count', 0)}")

async def test_market_detection():
    """测试市场类型检测"""
    print("\n🌍 测试市场类型检测")
    print("=" * 50)
    
    factory = init_data_source_factory()
    
    test_symbols = [
        ("000858", "A股"),
        ("600036", "A股"),
        ("AAPL", "美股"),
        ("MSFT", "美股"),
        ("00700", "港股"),
        ("09988", "港股"),
    ]
    
    for symbol, expected in test_symbols:
        detected = factory.detect_market_type(symbol)
        status = "✅" if detected.value in expected else "❌"
        print(f"   {status} {symbol} -> {detected.value} (期望: {expected})")

async def benchmark_data_sources():
    """基准测试数据源性能"""
    print("\n⚡ 数据源性能基准测试")
    print("=" * 50)
    
    factory = init_data_source_factory()
    
    # 测试A股数据获取性能
    symbol = "000858"
    market = MarketType.A_SHARE
    
    print(f"📊 测试股票: {symbol}")
    
    # 获取可用数据源
    sources = factory.get_available_sources(market, DataCategory.BASIC_INFO)
    
    for source in sources:
        print(f"\n🔍 测试数据源: {source.source_type.value}")
        
        start_time = asyncio.get_event_loop().time()
        try:
            result = await source.get_stock_info(symbol, market)
            end_time = asyncio.get_event_loop().time()
            
            if result:
                print(f"   ✅ 成功 - 耗时: {end_time - start_time:.2f}秒")
                print(f"   📋 股票名称: {result.get('name', 'N/A')}")
            else:
                print(f"   ❌ 失败 - 耗时: {end_time - start_time:.2f}秒")
                
        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            print(f"   ❌ 异常 - 耗时: {end_time - start_time:.2f}秒")
            print(f"   错误: {e}")

def show_data_source_summary():
    """显示数据源总结"""
    print("\n📊 数据源总结")
    print("=" * 50)
    
    summary = {
        "Tushare": {
            "市场": "A股",
            "特点": "专业、全面、高质量",
            "需要": "API Token",
            "限制": "200次/分钟"
        },
        "FinnHub": {
            "市场": "美股",
            "特点": "专业、实时、情感分析",
            "需要": "API Key",
            "限制": "60次/分钟"
        },
        "AKShare": {
            "市场": "A股、港股、美股",
            "特点": "开源、免费、多市场",
            "需要": "无",
            "限制": "100次/分钟"
        },
        "BaoStock": {
            "市场": "A股",
            "特点": "免费、历史数据丰富",
            "需要": "无",
            "限制": "60次/分钟"
        },
        "YFinance": {
            "市场": "美股、港股",
            "特点": "免费、基本面数据丰富",
            "需要": "无",
            "限制": "30次/分钟（较严）"
        }
    }
    
    for source, info in summary.items():
        print(f"\n📈 {source}:")
        for key, value in info.items():
            print(f"   {key}: {value}")

async def main():
    """主函数"""
    print("🧪 TradingAgents 完整数据源测试")
    print("=" * 50)
    
    # 检查环境变量
    print("🔑 检查API密钥配置:")
    tushare_key = os.getenv("TUSHARE_TOKEN")
    finnhub_key = os.getenv("FINNHUB_API_KEY")
    
    print(f"   Tushare: {'✅ 已配置' if tushare_key else '❌ 未配置'}")
    print(f"   FinnHub: {'✅ 已配置' if finnhub_key else '❌ 未配置'}")
    print(f"   AKShare: ✅ 无需配置")
    print(f"   BaoStock: ✅ 无需配置")
    print(f"   YFinance: ✅ 无需配置")
    
    # 运行测试
    await test_market_detection()
    await test_data_source_priority()
    await test_data_source_health()
    await test_individual_data_sources()
    await benchmark_data_sources()
    
    # 显示总结
    show_data_source_summary()
    
    print("\n🎉 所有测试完成！")
    print("\n💡 使用建议:")
    print("1. 配置 Tushare Token 以获得最佳A股数据")
    print("2. 配置 FinnHub API Key 以获得最佳美股数据")
    print("3. AKShare 和 BaoStock 可作为免费备选方案")
    print("4. 注意各数据源的频率限制，避免超限")

if __name__ == "__main__":
    asyncio.run(main())
