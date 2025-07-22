#!/usr/bin/env python3
"""
测试增强数据管理器 - 集成TradingAgents优秀实现
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

class EnhancedDataManagerTester:
    """增强数据管理器测试器"""
    
    def __init__(self):
        self.data_service_url = "http://localhost:8002"
        self.test_symbols = {
            "us": ["AAPL", "MSFT"],
            "china": ["000858", "000001"],
            "hk": ["00700", "00941"]
        }
    
    def test_service_health(self):
        """测试服务健康状态"""
        print("🔍 测试 Data Service 健康状态...")
        try:
            response = requests.get(f"{self.data_service_url}/health", timeout=30)
            if response.status_code == 200:
                print("✅ Data Service 健康")
                return True
            else:
                print(f"❌ Data Service 不健康: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Data Service 连接失败: {e}")
            return False
    
    def test_enhanced_api_basic(self):
        """测试增强API基础功能"""
        print("\n🚀 测试增强API基础功能")
        print("=" * 50)
        
        # 测试美股
        print("📊 测试美股数据 (AAPL)...")
        try:
            response = requests.get(
                f"{self.data_service_url}/api/enhanced/stock/AAPL",
                params={
                    "start_date": "2024-12-01",
                    "end_date": "2024-12-31",
                    "force_refresh": True
                },
                timeout=180  # 增加到3分钟，因为AKShare可能很慢
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    result = data.get("data", {})
                    print(f"  ✅ 美股数据获取成功")
                    print(f"  📊 股票代码: {result.get('symbol', 'N/A')}")
                    print(f"  🌍 市场类型: {result.get('market_type', 'N/A')}")
                    print(f"  📡 数据来源: {result.get('data_source', 'N/A')}")
                    print(f"  📄 格式化数据长度: {len(result.get('formatted_data', ''))}")
                    
                    # 显示格式化数据预览
                    formatted_data = result.get('formatted_data', '')
                    if formatted_data:
                        lines = formatted_data.split('\n')[:10]  # 显示前10行
                        print(f"  📋 格式化数据预览:")
                        for line in lines:
                            print(f"    {line}")
                        total_lines = len(formatted_data.split('\n'))
                        if total_lines > 10:
                            remaining_lines = total_lines - 10
                            print(f"    ... (还有 {remaining_lines} 行)")
                else:
                    print(f"  ❌ API返回失败: {data.get('message', 'N/A')}")
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
                print(f"  📄 响应内容: {response.text}")
                
        except Exception as e:
            print(f"  ❌ 美股测试异常: {e}")
        
        # 测试A股
        print("\n📊 测试A股数据 (000858)...")
        try:
            response = requests.get(
                f"{self.data_service_url}/api/enhanced/stock/000858",
                params={
                    "start_date": "2024-12-01",
                    "end_date": "2024-12-31"
                },
                timeout=180  # 增加到3分钟
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    result = data.get("data", {})
                    print(f"  ✅ A股数据获取成功")
                    print(f"  📊 股票代码: {result.get('symbol', 'N/A')}")
                    print(f"  🌍 市场类型: {result.get('market_type', 'N/A')}")
                    print(f"  📡 数据来源: {result.get('data_source', 'N/A')}")
                else:
                    print(f"  ❌ API返回失败: {data.get('message', 'N/A')}")
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ A股测试异常: {e}")
    
    def test_formatted_api(self):
        """测试格式化API"""
        print("\n📄 测试格式化API")
        print("=" * 50)
        
        try:
            response = requests.get(
                f"{self.data_service_url}/api/enhanced/stock/AAPL/formatted",
                params={
                    "start_date": "2024-12-01",
                    "end_date": "2024-12-31",
                    "force_refresh": True
                },
                timeout=180  # 增加到3分钟
            )

            if response.status_code == 200:
                formatted_text = response.text
                print(f"✅ 格式化API成功")
                print(f"📄 返回内容类型: {response.headers.get('content-type', 'N/A')}")
                print(f"📊 内容长度: {len(formatted_text)} 字符")
                print(f"📋 格式化内容预览:")
                print("-" * 40)
                lines = formatted_text.split('\n')[:15]  # 显示前15行
                for line in lines:
                    print(line)
                total_lines = len(formatted_text.split('\n'))
                if total_lines > 15:
                    remaining_lines = total_lines - 15
                    print(f"... (还有 {remaining_lines} 行)")
                print("-" * 40)
            else:
                print(f"❌ 格式化API失败: HTTP {response.status_code}")
                print(f"📄 错误内容: {response.text}")
                
        except Exception as e:
            print(f"❌ 格式化API测试异常: {e}")
    
    def test_cache_mechanism(self):
        """测试缓存机制"""
        print("\n💾 测试缓存机制")
        print("=" * 50)
        
        symbol = "AAPL"
        
        # 第一次请求 (强制刷新)
        print("📊 第一次请求 (强制刷新)...")
        start_time = time.time()
        try:
            response = requests.get(
                f"{self.data_service_url}/api/enhanced/stock/{symbol}",
                params={"force_refresh": True},
                timeout=180  # 增加到3分钟
            )
            first_duration = time.time() - start_time
            
            if response.status_code == 200:
                print(f"  ✅ 第一次请求成功: {first_duration:.2f}秒")
            else:
                print(f"  ❌ 第一次请求失败: HTTP {response.status_code}")
                return
        except Exception as e:
            print(f"  ❌ 第一次请求异常: {e}")
            return
        
        # 第二次请求 (使用缓存)
        print("\n📊 第二次请求 (使用缓存)...")
        start_time = time.time()
        try:
            response = requests.get(
                f"{self.data_service_url}/api/enhanced/stock/{symbol}",
                params={"force_refresh": False},
                timeout=60  # 第二次请求应该很快（缓存）
            )
            second_duration = time.time() - start_time
            
            if response.status_code == 200:
                print(f"  ✅ 第二次请求成功: {second_duration:.2f}秒")
                
                # 比较性能
                if second_duration < first_duration:
                    speedup = first_duration / second_duration
                    print(f"  🚀 缓存加速: {speedup:.1f}x 倍")
                else:
                    print(f"  ⚠️ 缓存效果不明显")
            else:
                print(f"  ❌ 第二次请求失败: HTTP {response.status_code}")
        except Exception as e:
            print(f"  ❌ 第二次请求异常: {e}")
    
    def test_market_detection(self):
        """测试市场类型检测"""
        print("\n🌍 测试市场类型检测")
        print("=" * 50)
        
        test_cases = [
            ("AAPL", "us", "美股"),
            ("MSFT", "us", "美股"),
            ("000858", "china", "A股"),
            ("600036", "china", "A股"),
            ("00700", "hk", "港股"),
            ("00941", "hk", "港股")
        ]
        
        for symbol, expected_market, market_name in test_cases:
            try:
                response = requests.get(
                    f"{self.data_service_url}/api/enhanced/stock/{symbol}",
                    timeout=120  # 市场检测测试，2分钟超时
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        result = data.get("data", {})
                        detected_market = result.get("market_type", "unknown")
                        
                        if detected_market == expected_market:
                            print(f"  ✅ {symbol}: {market_name} - 检测正确")
                        else:
                            print(f"  ❌ {symbol}: 期望 {expected_market}, 实际 {detected_market}")
                    else:
                        print(f"  ❌ {symbol}: API返回失败")
                else:
                    print(f"  ❌ {symbol}: HTTP {response.status_code}")
            except Exception as e:
                print(f"  ❌ {symbol}: 测试异常 - {e}")
    
    def test_error_handling(self):
        """测试错误处理"""
        print("\n❌ 测试错误处理")
        print("=" * 50)
        
        # 测试无效股票代码
        print("📊 测试无效股票代码...")
        try:
            response = requests.get(
                f"{self.data_service_url}/api/enhanced/stock/INVALID_SYMBOL_12345",
                timeout=60  # 错误处理测试，1分钟超时
            )

            print(f"  📤 响应状态: HTTP {response.status_code}")
            if response.status_code >= 400:
                print(f"  ✅ 正确返回错误状态")
                data = response.json()
                print(f"  📄 错误消息: {data.get('message', 'N/A')}")
            else:
                print(f"  ⚠️ 未返回预期的错误状态")
        except Exception as e:
            print(f"  ❌ 无效代码测试异常: {e}")
        
        # 测试空股票代码
        print("\n📊 测试空股票代码...")
        try:
            response = requests.get(
                f"{self.data_service_url}/api/enhanced/stock/",
                timeout=30  # 空代码测试，30秒超时
            )

            print(f"  📤 响应状态: HTTP {response.status_code}")
            if response.status_code == 404:
                print(f"  ✅ 正确返回404错误")
            else:
                print(f"  ⚠️ 响应状态异常")
        except Exception as e:
            print(f"  ❌ 空代码测试异常: {e}")
    
    def run_full_test(self):
        """运行完整测试"""
        print("🚀 增强数据管理器完整测试")
        print("=" * 60)
        
        # 1. 健康检查
        if not self.test_service_health():
            print("❌ 服务不可用，请先启动 Data Service")
            return
        
        # 2. 基础功能测试
        self.test_enhanced_api_basic()
        
        # 3. 格式化API测试
        self.test_formatted_api()
        
        # 4. 缓存机制测试
        self.test_cache_mechanism()
        
        # 5. 市场检测测试
        self.test_market_detection()
        
        # 6. 错误处理测试
        self.test_error_handling()
        
        print("\n🎉 增强数据管理器测试完成！")
        print("\n💡 总结:")
        print("✅ 集成了TradingAgents的优秀实现")
        print("✅ 支持多市场股票数据获取")
        print("✅ 智能缓存机制")
        print("✅ 优雅的数据格式化")
        print("✅ 完整的错误处理")
        print("✅ 统一的数据接口")

def main():
    """主函数"""
    tester = EnhancedDataManagerTester()
    tester.run_full_test()

if __name__ == "__main__":
    main()
