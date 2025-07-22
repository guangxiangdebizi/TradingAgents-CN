#!/usr/bin/env python3
"""
修复Yahoo Finance访问问题的测试脚本
"""

import sys
import os
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_yfinance_fix():
    """测试修复后的Yahoo Finance"""
    print("🔧 测试Yahoo Finance修复方案")
    print("=" * 50)
    
    try:
        import yfinance as yf
        
        # 方案1: 不使用自定义session，让yfinance自己处理
        print("📊 方案1: 使用默认yfinance配置...")
        try:
            ticker = yf.Ticker("AAPL")
            
            # 测试基本信息
            print("  🏢 获取基本信息...")
            info = ticker.info
            if info and len(info) > 5:
                company_name = info.get('longName', info.get('shortName', 'N/A'))
                print(f"    ✅ 公司名称: {company_name}")
                print(f"    💰 市值: {info.get('marketCap', 'N/A')}")
                print(f"    🏭 行业: {info.get('industry', 'N/A')}")
            else:
                print("    ❌ 基本信息获取失败或数据不完整")
            
            # 测试历史数据
            print("  📈 获取历史数据...")
            hist = ticker.history(period="5d")  # 只获取5天数据
            if not hist.empty:
                print(f"    ✅ 历史数据: {len(hist)} 条记录")
                print(f"    📊 最新价格: ${hist['Close'].iloc[-1]:.2f}")
                print(f"    📅 日期范围: {hist.index[0].strftime('%Y-%m-%d')} 到 {hist.index[-1].strftime('%Y-%m-%d')}")
                return True
            else:
                print("    ❌ 历史数据为空")
                
        except Exception as e:
            print(f"    ❌ 方案1失败: {e}")
        
        # 方案2: 尝试安装和使用curl_cffi
        print("\n📊 方案2: 检查curl_cffi依赖...")
        try:
            import curl_cffi
            print("    ✅ curl_cffi已安装")
            
            # 重新测试yfinance
            ticker = yf.Ticker("AAPL")
            hist = ticker.history(period="1d")
            if not hist.empty:
                print(f"    ✅ 使用curl_cffi成功: ${hist['Close'].iloc[-1]:.2f}")
                return True
            else:
                print("    ❌ 即使有curl_cffi也失败")
                
        except ImportError:
            print("    ⚠️ curl_cffi未安装")
            print("    💡 建议安装: pip install curl_cffi")
        except Exception as e:
            print(f"    ❌ curl_cffi方案失败: {e}")
        
        return False
        
    except ImportError:
        print("❌ yfinance库未安装")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_alternative_free_apis():
    """测试其他免费API"""
    print("\n🌐 测试其他免费美股API")
    print("=" * 50)
    
    # Alpha Vantage (需要免费API Key)
    print("📊 Alpha Vantage API测试...")
    alpha_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if alpha_key:
        try:
            import requests
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': 'AAPL',
                'apikey': alpha_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                quote = data.get('Global Quote', {})
                if quote:
                    price = quote.get('05. price', 'N/A')
                    print(f"    ✅ Alpha Vantage成功: AAPL = ${price}")
                else:
                    print("    ❌ Alpha Vantage响应格式异常")
            else:
                print(f"    ❌ Alpha Vantage HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"    ❌ Alpha Vantage异常: {e}")
    else:
        print("    ⚠️ 未配置ALPHA_VANTAGE_API_KEY")
        print("    💡 可在 https://www.alphavantage.co/support/#api-key 免费获取")
    
    # IEX Cloud (需要API Key，有免费额度)
    print("\n📊 IEX Cloud API测试...")
    iex_token = os.getenv("IEX_CLOUD_API_KEY")
    if iex_token:
        try:
            import requests
            url = f"https://cloud.iexapis.com/stable/stock/AAPL/quote"
            params = {'token': iex_token}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                price = data.get('latestPrice', 'N/A')
                company_name = data.get('companyName', 'N/A')
                print(f"    ✅ IEX Cloud成功: {company_name} = ${price}")
            else:
                print(f"    ❌ IEX Cloud HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"    ❌ IEX Cloud异常: {e}")
    else:
        print("    ⚠️ 未配置IEX_CLOUD_API_KEY")
        print("    💡 可在 https://iexcloud.io/ 免费获取")

def install_curl_cffi():
    """尝试安装curl_cffi"""
    print("\n🔧 尝试安装curl_cffi依赖")
    print("=" * 50)
    
    try:
        import subprocess
        import sys
        
        print("📦 正在安装curl_cffi...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "curl_cffi"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ curl_cffi安装成功")
            return True
        else:
            print(f"❌ curl_cffi安装失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 安装超时")
        return False
    except Exception as e:
        print(f"❌ 安装异常: {e}")
        return False

def main():
    """主函数"""
    print("🔧 Yahoo Finance修复测试")
    print("=" * 60)
    
    # 1. 测试当前yfinance状态
    yf_success = test_yfinance_fix()
    
    # 2. 如果失败，尝试安装curl_cffi
    if not yf_success:
        print("\n🔄 yfinance失败，尝试安装curl_cffi...")
        if install_curl_cffi():
            print("\n🔄 重新测试yfinance...")
            yf_success = test_yfinance_fix()
    
    # 3. 测试其他免费API
    test_alternative_free_apis()
    
    # 4. 总结建议
    print("\n💡 总结和建议")
    print("=" * 50)
    
    if yf_success:
        print("✅ Yahoo Finance已修复，可以正常使用")
    else:
        print("❌ Yahoo Finance仍然无法使用")
        print("🔧 建议解决方案:")
        print("1. 手动安装: pip install curl_cffi")
        print("2. 升级yfinance: pip install --upgrade yfinance")
        print("3. 使用其他数据源 (FinnHub, Alpha Vantage, IEX)")
        print("4. 等待Yahoo Finance恢复访问")
    
    print("\n🎯 当前可用的美股数据源:")
    print("✅ FinnHub (实时报价和基本信息)")
    print("✅ TradingAgents优化接口")
    if yf_success:
        print("✅ Yahoo Finance (已修复)")
    else:
        print("❌ Yahoo Finance (需要修复)")
    
    print("\n🎉 修复测试完成！")

if __name__ == "__main__":
    main()
