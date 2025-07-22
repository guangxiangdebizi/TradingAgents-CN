#!/usr/bin/env python3
"""
测试数据持久化功能的脚本
"""

import asyncio
import sys
import requests
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class DataPersistenceTester:
    """数据持久化测试器"""
    
    def __init__(self):
        self.data_service_url = "http://localhost:8002"
    
    def test_service_health(self):
        """测试服务健康状态"""
        print("🔍 测试 Data Service 健康状态...")
        try:
            response = requests.get(f"{self.data_service_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Data Service 健康")
                return True
            else:
                print(f"❌ Data Service 不健康: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Data Service 连接失败: {e}")
            return False
    
    def test_data_retrieval_and_storage(self):
        """测试数据获取和存储"""
        print("\n📊 测试数据获取和存储...")
        print("-" * 40)
        
        test_symbols = ["000858", "AAPL"]
        
        for symbol in test_symbols:
            print(f"\n🔍 测试股票: {symbol}")
            
            # 1. 获取股票信息
            print("  📋 获取股票信息...")
            try:
                response = requests.get(f"{self.data_service_url}/api/stock/info/{symbol}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"    ✅ 成功: {data.get('message', 'N/A')}")
                    else:
                        print(f"    ❌ 失败: {data.get('message', 'N/A')}")
                else:
                    print(f"    ❌ HTTP错误: {response.status_code}")
            except Exception as e:
                print(f"    ❌ 异常: {e}")
            
            # 2. 获取股票数据
            print("  📈 获取股票数据...")
            try:
                response = requests.post(f"{self.data_service_url}/api/stock/data", json={
                    "symbol": symbol,
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-10"
                })
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"    ✅ 成功: {data.get('message', 'N/A')}")
                    else:
                        print(f"    ❌ 失败: {data.get('message', 'N/A')}")
                else:
                    print(f"    ❌ HTTP错误: {response.status_code}")
            except Exception as e:
                print(f"    ❌ 异常: {e}")
            
            # 等待一下，让数据保存完成
            time.sleep(2)
    
    def test_local_data_summary(self):
        """测试本地数据摘要"""
        print("\n📊 测试本地数据摘要...")
        print("-" * 40)
        
        try:
            response = requests.get(f"{self.data_service_url}/api/local-data/summary")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    summary = data.get("data", {})
                    print("✅ 本地数据摘要:")
                    
                    # 缓存数据
                    cached_data = summary.get("cached_data", {})
                    print("  📦 缓存数据:")
                    for data_type, count in cached_data.items():
                        print(f"    {data_type}: {count} 条")
                    
                    # 历史数据
                    historical_data = summary.get("historical_data", {})
                    print("  📚 历史数据:")
                    for data_type, count in historical_data.items():
                        print(f"    {data_type}: {count} 条")
                    
                    # 数据库信息
                    db_info = summary.get("database_info", {})
                    print("  🗄️ 数据库信息:")
                    print(f"    数据库: {db_info.get('database_name', 'N/A')}")
                    print(f"    集合数: {db_info.get('collections', 0)}")
                    print(f"    数据大小: {db_info.get('data_size', 0)} 字节")
                    
                    # Redis 信息
                    redis_info = summary.get("redis_info", {})
                    print("  🔴 Redis 信息:")
                    print(f"    内存使用: {redis_info.get('used_memory', 'N/A')}")
                    print(f"    连接数: {redis_info.get('connected_clients', 0)}")
                    
                else:
                    print(f"❌ 获取摘要失败: {data.get('message', 'N/A')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    def test_symbol_data_history(self, symbol: str = "000858"):
        """测试股票数据历史"""
        print(f"\n📚 测试股票数据历史: {symbol}")
        print("-" * 40)
        
        try:
            response = requests.get(f"{self.data_service_url}/api/local-data/history/{symbol}")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    history = data.get("data", {})
                    print(f"✅ {symbol} 数据历史:")
                    
                    # 股票信息
                    stock_info = history.get("stock_info")
                    if stock_info:
                        print(f"  📋 股票信息: 已保存 (来源: {stock_info.get('source', 'N/A')})")
                    else:
                        print("  📋 股票信息: 无数据")
                    
                    # 股票数据
                    stock_data = history.get("stock_data", [])
                    print(f"  📈 股票数据: {len(stock_data)} 条记录")
                    if stock_data:
                        latest = stock_data[0]
                        print(f"    最新: {latest.get('date')} - 收盘价: {latest.get('close')}")
                    
                    # 基本面数据
                    fundamentals = history.get("fundamentals", [])
                    print(f"  💰 基本面数据: {len(fundamentals)} 条记录")
                    
                    # 新闻数据
                    news = history.get("news", [])
                    print(f"  📰 新闻数据: {len(news)} 条记录")
                    
                    # 缓存数据
                    cached_data = history.get("cached_data", [])
                    print(f"  📦 缓存数据: {len(cached_data)} 条记录")
                    for cache in cached_data:
                        print(f"    {cache.get('data_type')}: {cache.get('source')} (过期: {cache.get('expires_at')})")
                    
                else:
                    print(f"❌ 获取历史失败: {data.get('message', 'N/A')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    def test_force_refresh(self, symbol: str = "000858"):
        """测试强制刷新数据"""
        print(f"\n🔄 测试强制刷新数据: {symbol}")
        print("-" * 40)
        
        try:
            response = requests.post(f"{self.data_service_url}/api/local-data/force-refresh", json={
                "symbol": symbol,
                "data_type": "stock_info"
            })
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ 强制刷新成功: {data.get('message', 'N/A')}")
                else:
                    print(f"❌ 强制刷新失败: {data.get('message', 'N/A')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"响应: {response.text}")
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    def test_data_cleanup(self):
        """测试数据清理"""
        print("\n🧹 测试数据清理...")
        print("-" * 40)
        
        try:
            response = requests.post(f"{self.data_service_url}/api/local-data/cleanup", json={
                "days": 60  # 清理60天前的数据
            })
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    cleanup_stats = data.get("data", {})
                    print("✅ 数据清理完成:")
                    for key, count in cleanup_stats.items():
                        print(f"  {key}: 清理了 {count} 条记录")
                else:
                    print(f"❌ 数据清理失败: {data.get('message', 'N/A')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    def run_full_test(self):
        """运行完整测试"""
        print("🧪 TradingAgents 数据持久化测试")
        print("=" * 50)
        
        # 1. 健康检查
        if not self.test_service_health():
            print("❌ 服务不可用，请先启动 Data Service")
            return
        
        # 2. 测试数据获取和存储
        self.test_data_retrieval_and_storage()
        
        # 3. 测试本地数据摘要
        self.test_local_data_summary()
        
        # 4. 测试股票数据历史
        self.test_symbol_data_history("000858")
        
        # 5. 测试强制刷新
        self.test_force_refresh("000858")
        
        # 6. 再次查看数据摘要
        print("\n📊 刷新后的数据摘要:")
        self.test_local_data_summary()
        
        # 7. 测试数据清理
        self.test_data_cleanup()
        
        print("\n🎉 数据持久化测试完成！")

def main():
    """主函数"""
    tester = DataPersistenceTester()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "summary":
            tester.test_local_data_summary()
        elif command == "history":
            symbol = sys.argv[2] if len(sys.argv) > 2 else "000858"
            tester.test_symbol_data_history(symbol)
        elif command == "refresh":
            symbol = sys.argv[2] if len(sys.argv) > 2 else "000858"
            tester.test_force_refresh(symbol)
        elif command == "cleanup":
            tester.test_data_cleanup()
        else:
            print("❌ 未知命令")
    else:
        tester.run_full_test()

if __name__ == "__main__":
    main()
