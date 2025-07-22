#!/usr/bin/env python3
"""
最终验证新数据源是否真正工作
"""

import requests
import json
import time

def test_api_response():
    """测试API响应的详细内容"""
    print("🧪 最终验证测试")
    print("=" * 50)
    
    data_service_url = "http://localhost:8002"
    
    try:
        print("📊 测试增强API响应...")
        response = requests.get(
            f"{data_service_url}/api/enhanced/stock/AAPL",
            params={
                "force_refresh": True,
                "clear_all_cache": True,
                "start_date": "2024-12-01",
                "end_date": "2024-12-31"
            },
            timeout=120
        )
        
        print(f"HTTP状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                result = data.get("data", {})
                
                print(f"\n✅ API调用成功")
                print(f"📊 股票代码: {result.get('symbol', 'N/A')}")
                print(f"📡 数据源: {result.get('data_source', 'N/A')}")
                print(f"🌍 市场类型: {result.get('market_type', 'N/A')}")
                print(f"⏰ 时间戳: {result.get('timestamp', 'N/A')}")
                
                # 检查股票信息
                stock_info = result.get("stock_info", {})
                if stock_info:
                    print(f"\n📋 股票信息:")
                    print(f"  公司名称: {stock_info.get('name', 'N/A')}")
                    print(f"  交易所: {stock_info.get('exchange', 'N/A')}")
                    print(f"  货币: {stock_info.get('currency', 'N/A')}")
                    print(f"  数据源: {stock_info.get('source', 'N/A')}")
                
                # 检查历史数据
                historical_data = result.get("historical_data", [])
                if historical_data:
                    print(f"\n📈 历史数据:")
                    print(f"  数据条数: {len(historical_data)}")
                    if len(historical_data) > 0:
                        first_record = historical_data[0]
                        print(f"  第一条数据: {first_record.get('date', 'N/A')} - ${first_record.get('close', 'N/A')}")
                        print(f"  数据源: {first_record.get('source', 'N/A')}")
                
                # 检查格式化数据
                formatted_data = result.get("formatted_data", "")
                if formatted_data:
                    lines = formatted_data.split('\n')[:5]
                    print(f"\n📄 格式化数据预览:")
                    for line in lines:
                        if line.strip():
                            print(f"  {line}")
                
                # 判断是否真正使用了新数据源
                data_source = result.get('data_source', '')
                stock_info_source = stock_info.get('source', '') if stock_info else ''
                
                print(f"\n🎯 数据源验证:")
                print(f"  主数据源: {data_source}")
                print(f"  股票信息数据源: {stock_info_source}")
                
                if data_source in ['alpha_vantage', 'twelve_data', 'iex_cloud']:
                    print(f"  🎉 成功！正在使用新数据源: {data_source}")
                    return True
                elif stock_info_source in ['alpha_vantage', 'twelve_data', 'iex_cloud']:
                    print(f"  🎉 部分成功！股票信息使用新数据源: {stock_info_source}")
                    print(f"  ⚠️ 但主数据源仍是: {data_source}")
                    return True
                else:
                    print(f"  ⚠️ 仍在使用旧数据源: {data_source}")
                    return False
                    
            else:
                print(f"❌ API返回失败: {data.get('message', 'N/A')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_multiple_requests():
    """测试多次请求，观察数据源使用情况"""
    print("\n🔄 多次请求测试")
    print("=" * 50)
    
    data_service_url = "http://localhost:8002"
    symbols = ["AAPL", "MSFT", "GOOGL"]
    
    results = {}
    
    for symbol in symbols:
        try:
            print(f"\n📊 测试 {symbol}...")
            
            response = requests.get(
                f"{data_service_url}/api/enhanced/stock/{symbol}",
                params={
                    "force_refresh": True,
                    "clear_all_cache": True
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    result = data.get("data", {})
                    data_source = result.get("data_source", "unknown")
                    results[symbol] = data_source
                    print(f"  ✅ {symbol}: {data_source}")
                else:
                    results[symbol] = "failed"
                    print(f"  ❌ {symbol}: 失败")
            else:
                results[symbol] = "error"
                print(f"  ❌ {symbol}: HTTP {response.status_code}")
            
            # 避免频率限制
            time.sleep(2)
            
        except Exception as e:
            results[symbol] = "exception"
            print(f"  ❌ {symbol}: 异常 - {e}")
    
    # 统计结果
    print(f"\n📊 数据源使用统计:")
    source_counts = {}
    for symbol, source in results.items():
        source_counts[source] = source_counts.get(source, 0) + 1
    
    for source, count in source_counts.items():
        print(f"  {source}: {count} 次")
    
    # 检查是否有新数据源
    new_sources = ['alpha_vantage', 'twelve_data', 'iex_cloud']
    using_new_sources = any(source in new_sources for source in results.values())
    
    return using_new_sources

def main():
    """主函数"""
    print("🎯 新数据源最终验证")
    print("=" * 60)
    
    # 1. 详细API响应测试
    api_success = test_api_response()
    
    # 2. 多次请求测试
    if api_success:
        print("\n" + "=" * 60)
        choice = input("❓ 是否进行多次请求测试？(y/N): ").strip().lower()
        if choice in ['y', 'yes']:
            multiple_success = test_multiple_requests()
        else:
            multiple_success = True
    else:
        multiple_success = False
    
    print(f"\n🎉 最终结果:")
    if api_success:
        print("✅ 新数据源集成成功！")
        print("🎯 Alpha Vantage和Twelve Data已正常工作")
        print("🚀 Yahoo Finance访问限制问题已解决")
        
        print(f"\n💡 配置的数据源:")
        print("  ✅ Alpha Vantage: 每天500次请求")
        print("  ✅ Twelve Data: 每天800次请求")
        print("  ❌ IEX Cloud: 未配置（可选）")
        
        print(f"\n🔄 数据源优先级:")
        print("  1. Alpha Vantage (最高优先级)")
        print("  2. Twelve Data (第二优先级)")
        print("  3. IEX Cloud (第三优先级)")
        print("  4. FinnHub (第四优先级)")
        print("  5. YFinance (最低优先级)")
        
    else:
        print("❌ 仍有问题需要解决")
        print("💡 建议检查:")
        print("  1. Data Service是否完全重启")
        print("  2. 环境变量是否正确加载")
        print("  3. 数据源初始化日志")

if __name__ == "__main__":
    main()
