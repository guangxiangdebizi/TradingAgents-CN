#!/usr/bin/env python3
"""
测试数据源工厂的脚本
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.data_service.app.datasources.factory import init_data_source_factory
from backend.data_service.app.datasources.base import MarketType, DataCategory

async def test_data_sources():
    """测试数据源工厂"""
    print("🧪 测试数据源工厂")
    print("=" * 50)
    
    # 初始化数据源工厂
    factory = init_data_source_factory()
    
    # 测试股票代码
    test_symbols = {
        "A股": ["000858", "000001", "600036"],
        "港股": ["00700", "09988"],
        "美股": ["AAPL", "MSFT"]
    }
    
    # 1. 测试市场类型检测
    print("\n📊 测试市场类型检测")
    print("-" * 30)
    for market_name, symbols in test_symbols.items():
        for symbol in symbols:
            market_type = factory.detect_market_type(symbol)
            print(f"   {symbol} -> {market_type.value}")
    
    # 2. 测试数据源健康检查
    print("\n🔍 测试数据源健康检查")
    print("-" * 30)
    health_status = await factory.health_check_all()
    for source, status in health_status.items():
        print(f"   {source}: {status.get('status', 'unknown')}")
    
    # 3. 测试获取股票信息
    print("\n📈 测试获取股票信息")
    print("-" * 30)
    
    # 测试A股
    try:
        symbol = "000858"
        market_type = MarketType.A_SHARE
        print(f"🔍 获取 {symbol} 股票信息...")
        
        stock_info = await factory.get_stock_info(symbol, market_type)
        if stock_info:
            print(f"✅ 成功: {stock_info.get('name', 'N/A')} - {stock_info.get('source', 'N/A')}")
        else:
            print(f"❌ 失败: 无法获取股票信息")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    # 测试美股
    try:
        symbol = "AAPL"
        market_type = MarketType.US_STOCK
        print(f"🔍 获取 {symbol} 股票信息...")
        
        stock_info = await factory.get_stock_info(symbol, market_type)
        if stock_info:
            print(f"✅ 成功: {stock_info.get('name', 'N/A')} - {stock_info.get('source', 'N/A')}")
        else:
            print(f"❌ 失败: 无法获取股票信息")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    # 4. 测试获取股票数据
    print("\n📊 测试获取股票数据")
    print("-" * 30)
    
    try:
        symbol = "000858"
        market_type = MarketType.A_SHARE
        start_date = "2024-01-01"
        end_date = "2024-01-10"
        print(f"🔍 获取 {symbol} 股票数据 ({start_date} 到 {end_date})...")
        
        stock_data = await factory.get_stock_data(symbol, market_type, start_date, end_date)
        if stock_data:
            print(f"✅ 成功: 获取到 {len(stock_data)} 条数据")
            if stock_data:
                print(f"   示例数据: {stock_data[0]}")
        else:
            print(f"❌ 失败: 无法获取股票数据")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    # 5. 测试获取基本面数据
    print("\n💰 测试获取基本面数据")
    print("-" * 30)
    
    try:
        symbol = "000858"
        market_type = MarketType.A_SHARE
        start_date = "2023-01-01"
        end_date = "2024-01-01"
        print(f"🔍 获取 {symbol} 基本面数据...")
        
        fundamentals = await factory.get_fundamentals(symbol, market_type, start_date, end_date)
        if fundamentals:
            print(f"✅ 成功: {fundamentals.get('source', 'N/A')}")
            print(f"   ROE: {fundamentals.get('roe', 'N/A')}")
            print(f"   ROA: {fundamentals.get('roa', 'N/A')}")
        else:
            print(f"❌ 失败: 无法获取基本面数据")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    # 6. 测试获取新闻数据
    print("\n📰 测试获取新闻数据")
    print("-" * 30)
    
    try:
        symbol = "000858"
        market_type = MarketType.A_SHARE
        start_date = "2024-01-01"
        end_date = "2024-01-10"
        print(f"🔍 获取 {symbol} 新闻数据...")
        
        news_data = await factory.get_news(symbol, market_type, start_date, end_date)
        if news_data:
            print(f"✅ 成功: 获取到 {len(news_data)} 条新闻")
            if news_data:
                print(f"   示例新闻: {news_data[0].get('title', 'N/A')}")
        else:
            print(f"❌ 失败: 无法获取新闻数据")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    # 7. 显示数据源统计
    print("\n📊 数据源统计信息")
    print("-" * 30)
    stats = factory.get_source_stats()
    for source, stat in stats.items():
        print(f"   {source}:")
        print(f"     状态: {stat.get('status', 'N/A')}")
        print(f"     请求次数: {stat.get('request_count', 0)}")
        print(f"     错误次数: {stat.get('error_count', 0)}")
        print(f"     支持市场: {stat.get('supported_markets', [])}")
        print(f"     支持类别: {stat.get('supported_categories', [])}")
    
    print("\n🎉 数据源工厂测试完成！")

def main():
    """主函数"""
    print("🧪 TradingAgents 数据源工厂测试")
    print("=" * 50)
    
    # 设置环境变量（如果需要）
    if not os.getenv("TUSHARE_TOKEN"):
        print("⚠️ 警告: TUSHARE_TOKEN 环境变量未设置，Tushare 数据源可能无法正常工作")

    if not os.getenv("FINNHUB_API_KEY"):
        print("⚠️ 警告: FINNHUB_API_KEY 环境变量未设置，FinnHub 数据源可能无法正常工作")

    print("💡 提示: BaoStock 和 AKShare 无需API密钥，可直接使用")
    
    # 运行测试
    asyncio.run(test_data_sources())

if __name__ == "__main__":
    main()
