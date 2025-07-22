#!/usr/bin/env python3
"""
诊断数据源失败的具体原因
"""

import asyncio
import sys
import os
import requests
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
try:
    from dotenv import load_dotenv
    backend_dir = Path(__file__).parent
    backend_env = backend_dir / ".env"
    if backend_env.exists():
        load_dotenv(backend_env, override=True)
        print(f"✅ 加载环境变量: {backend_env}")
except ImportError:
    print("⚠️ python-dotenv未安装")

async def test_alpha_vantage_direct():
    """直接测试Alpha Vantage API"""
    print("\n🔍 直接测试Alpha Vantage API")
    print("-" * 40)
    
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print("❌ Alpha Vantage API Key 未配置")
        return False
    
    print(f"🔑 API Key: {api_key[:8]}...")
    
    try:
        # 测试实时报价
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': 'AAPL',
            'apikey': api_key
        }
        
        print("📊 测试实时报价...")
        response = requests.get(url, params=params, timeout=30)
        print(f"  HTTP状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  响应数据: {data}")
            
            if "Global Quote" in data:
                quote = data["Global Quote"]
                price = quote.get("05. price", "N/A")
                print(f"  ✅ AAPL价格: ${price}")
                return True
            elif "Note" in data:
                print(f"  ⚠️ API频率限制: {data['Note']}")
                return False
            elif "Error Message" in data:
                print(f"  ❌ API错误: {data['Error Message']}")
                return False
            else:
                print(f"  ❌ 未知响应格式")
                return False
        else:
            print(f"  ❌ HTTP错误: {response.status_code}")
            print(f"  响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Alpha Vantage测试失败: {e}")
        return False

async def test_twelve_data_direct():
    """直接测试Twelve Data API"""
    print("\n🔍 直接测试Twelve Data API")
    print("-" * 40)
    
    api_key = os.getenv("TWELVE_DATA_API_KEY")
    if not api_key:
        print("❌ Twelve Data API Key 未配置")
        return False
    
    print(f"🔑 API Key: {api_key[:8]}...")
    
    try:
        # 测试实时报价
        url = "https://api.twelvedata.com/quote"
        params = {
            'symbol': 'AAPL',
            'apikey': api_key
        }
        
        print("📊 测试实时报价...")
        response = requests.get(url, params=params, timeout=30)
        print(f"  HTTP状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  响应数据: {data}")
            
            if "code" in data and data["code"] != 200:
                if data["code"] == 429:
                    print(f"  ⚠️ API频率限制: {data.get('message', 'Rate limit')}")
                elif data["code"] == 401:
                    print(f"  ❌ API Key无效: {data.get('message', 'Invalid key')}")
                else:
                    print(f"  ❌ API错误 {data['code']}: {data.get('message', 'Unknown')}")
                return False
            elif "close" in data:
                price = data.get("close", "N/A")
                print(f"  ✅ AAPL价格: ${price}")
                return True
            else:
                print(f"  ❌ 未知响应格式")
                return False
        else:
            print(f"  ❌ HTTP错误: {response.status_code}")
            print(f"  响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Twelve Data测试失败: {e}")
        return False

async def test_finnhub_direct():
    """直接测试FinnHub API"""
    print("\n🔍 直接测试FinnHub API")
    print("-" * 40)
    
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        print("❌ FinnHub API Key 未配置")
        return False
    
    print(f"🔑 API Key: {api_key[:8]}...")
    
    try:
        # 测试股票信息
        url = "https://finnhub.io/api/v1/stock/profile2"
        params = {
            'symbol': 'AAPL',
            'token': api_key
        }
        
        print("📊 测试股票信息...")
        response = requests.get(url, params=params, timeout=30)
        print(f"  HTTP状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  响应数据: {data}")
            
            if data and "name" in data:
                name = data.get("name", "N/A")
                print(f"  ✅ AAPL公司: {name}")
                return True
            else:
                print(f"  ❌ 数据为空或格式错误")
                return False
        else:
            print(f"  ❌ HTTP错误: {response.status_code}")
            print(f"  响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FinnHub测试失败: {e}")
        return False

def test_data_service_logs():
    """检查Data Service的详细日志"""
    print("\n📋 Data Service启动日志检查")
    print("-" * 40)
    
    print("💡 请检查Data Service启动时的日志，查找以下信息:")
    print()
    print("🔍 数据源初始化日志:")
    print("  ✅ 数据源初始化成功: alpha_vantage")
    print("  ✅ 数据源初始化成功: twelve_data")
    print("  ❌ 数据源初始化失败 alpha_vantage: ...")
    print("  ❌ 数据源初始化失败 twelve_data: ...")
    print()
    print("🔍 环境变量加载日志:")
    print("  ✅ 加载Backend环境变量: ...")
    print("  ⚠️ Alpha Vantage API Key 未配置")
    print("  ⚠️ Twelve Data API Key 未配置")
    print()
    print("🔍 数据源尝试日志:")
    print("  🔍 尝试数据源 alpha_vantage 获取股票信息: AAPL")
    print("  ❌ Alpha Vantage 获取股票信息失败 AAPL: ...")
    print("  🔍 尝试数据源 twelve_data 获取股票信息: AAPL")
    print("  ❌ Twelve Data 获取股票信息失败 AAPL: ...")

def test_data_service_api():
    """测试Data Service API的详细响应"""
    print("\n🚀 测试Data Service API详细响应")
    print("-" * 40)
    
    data_service_url = "http://localhost:8002"
    
    try:
        # 测试健康检查
        print("📊 测试健康检查...")
        response = requests.get(f"{data_service_url}/health", timeout=10)
        print(f"  健康检查: HTTP {response.status_code}")
        
        if response.status_code != 200:
            print("❌ Data Service 不健康，无法继续测试")
            return
        
        # 测试增强API，获取详细错误信息
        print("\n📊 测试增强API...")
        response = requests.get(
            f"{data_service_url}/api/enhanced/stock/AAPL",
            params={
                "force_refresh": True,
                "clear_all_cache": True
            },
            timeout=120
        )
        
        print(f"  API响应: HTTP {response.status_code}")
        
        if response.status_code == 500:
            try:
                error_data = response.json()
                print(f"  错误详情: {error_data}")
            except:
                print(f"  错误文本: {response.text}")
        elif response.status_code == 200:
            data = response.json()
            if data.get("success"):
                result = data.get("data", {})
                data_source = result.get("data_source", "unknown")
                print(f"  ✅ 成功，数据源: {data_source}")
            else:
                print(f"  ❌ 失败: {data.get('message', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 测试Data Service API失败: {e}")

async def main():
    """主函数"""
    print("🔍 数据源失败诊断")
    print("=" * 60)
    
    # 1. 直接测试各个数据源API
    alpha_ok = await test_alpha_vantage_direct()
    twelve_ok = await test_twelve_data_direct()
    finnhub_ok = await test_finnhub_direct()
    
    print(f"\n📊 直接API测试结果:")
    print(f"  Alpha Vantage: {'✅' if alpha_ok else '❌'}")
    print(f"  Twelve Data: {'✅' if twelve_ok else '❌'}")
    print(f"  FinnHub: {'✅' if finnhub_ok else '❌'}")
    
    # 2. 检查Data Service日志
    test_data_service_logs()
    
    # 3. 测试Data Service API
    test_data_service_api()
    
    print(f"\n🎯 诊断总结:")
    if alpha_ok or twelve_ok:
        print("✅ 至少有一个新数据源API可以直接访问")
        print("💡 问题可能在于:")
        print("  1. Data Service 没有正确加载新数据源")
        print("  2. 数据源初始化时出现错误")
        print("  3. 优先级配置没有生效")
        print("\n🔧 建议:")
        print("  1. 重启Data Service并观察启动日志")
        print("  2. 检查是否有抽象方法错误")
        print("  3. 确认环境变量正确加载")
    else:
        print("❌ 所有数据源API都无法直接访问")
        print("💡 问题可能在于:")
        print("  1. API密钥无效或过期")
        print("  2. 网络连接问题")
        print("  3. API服务暂时不可用")
        print("\n🔧 建议:")
        print("  1. 检查API密钥是否正确")
        print("  2. 尝试使用浏览器直接访问API")
        print("  3. 检查网络连接和防火墙设置")

if __name__ == "__main__":
    asyncio.run(main())
