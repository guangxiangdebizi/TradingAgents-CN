#!/usr/bin/env python3
"""
测试优先级配置是否正确更新
"""

import requests
import json
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_priority_config_file():
    """测试优先级配置文件"""
    print("📋 测试优先级配置文件")
    print("=" * 50)
    
    config_file = Path(__file__).parent / "data-service/app/datasources/priority_config.json"
    
    if not config_file.exists():
        print(f"❌ 配置文件不存在: {config_file}")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查当前配置文件
        current_profile = config.get("current_profile", "default")
        print(f"📊 当前配置文件: {current_profile}")
        
        # 检查默认配置的美股优先级
        default_priorities = config["priority_profiles"]["default"]["priorities"]
        us_basic_info = default_priorities.get("us_stock_basic_info", [])
        
        print(f"\n🇺🇸 美股基本信息优先级:")
        for i, source in enumerate(us_basic_info, 1):
            print(f"  {i}. {source}")
        
        # 检查是否包含新数据源
        new_sources = ["alpha_vantage", "twelve_data", "iex_cloud"]
        found_new_sources = []
        
        for source in new_sources:
            if source in us_basic_info:
                found_new_sources.append(source)
                position = us_basic_info.index(source) + 1
                print(f"  ✅ {source}: 第{position}位")
            else:
                print(f"  ❌ {source}: 未找到")
        
        print(f"\n📊 新数据源配置状态: {len(found_new_sources)}/{len(new_sources)} 个已配置")
        
        if len(found_new_sources) == len(new_sources):
            print("✅ 优先级配置文件已正确更新")
            return True
        else:
            print("❌ 优先级配置文件缺少新数据源")
            return False
            
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return False

def test_data_service_priority():
    """测试Data Service是否使用了新的优先级"""
    print("\n🚀 测试Data Service优先级")
    print("=" * 50)
    
    data_service_url = "http://localhost:8002"
    
    try:
        # 检查服务健康状态
        response = requests.get(f"{data_service_url}/health", timeout=10)
        if response.status_code != 200:
            print("❌ Data Service 不健康")
            return False
        
        print("✅ Data Service 健康")
        
        # 测试美股数据获取，观察使用的数据源
        print("\n📊 测试美股数据获取...")
        
        test_symbol = "AAPL"
        response = requests.get(
            f"{data_service_url}/api/enhanced/stock/{test_symbol}",
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
                
                print(f"✅ 数据获取成功")
                print(f"📡 使用的数据源: {data_source}")
                
                # 检查是否使用了新数据源
                new_sources = ["alpha_vantage", "twelve_data", "iex_cloud"]
                if data_source in new_sources:
                    print(f"🎉 成功使用新数据源: {data_source}")
                    return True
                else:
                    print(f"⚠️ 仍在使用旧数据源: {data_source}")
                    print("💡 可能原因:")
                    print("  1. Data Service 需要重启以加载新配置")
                    print("  2. 新数据源初始化失败")
                    print("  3. API密钥配置问题")
                    return False
            else:
                print(f"❌ API返回失败: {data.get('message', 'N/A')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
        
    except Exception as e:
        print(f"❌ 测试Data Service失败: {e}")
    
    return False

def test_data_source_initialization():
    """检查数据源初始化状态"""
    print("\n🔧 检查数据源初始化状态")
    print("=" * 50)
    
    print("💡 请检查Data Service启动日志中是否有以下信息:")
    print("  ✅ 数据源初始化成功: alpha_vantage")
    print("  ✅ 数据源初始化成功: twelve_data")
    print("  ✅ 数据源初始化成功: iex_cloud")
    print()
    print("如果看到以下错误:")
    print("  ❌ 数据源初始化失败 alpha_vantage: Can't instantiate abstract class...")
    print("  说明抽象方法问题尚未解决")
    print()
    print("如果看到:")
    print("  ⚠️ Alpha Vantage API Key 未配置")
    print("  说明环境变量加载有问题")

def show_next_steps():
    """显示下一步操作"""
    print("\n🔄 下一步操作建议")
    print("=" * 50)
    
    print("1. 🔄 重启Data Service:")
    print("   - 停止当前服务 (Ctrl+C)")
    print("   - 重新启动: python -m uvicorn app.main:app --host 0.0.0.0 --port 8002")
    print()
    print("2. 📋 观察启动日志:")
    print("   - 检查新数据源是否初始化成功")
    print("   - 检查API密钥是否正确加载")
    print()
    print("3. 🧪 运行测试:")
    print("   - python backend/test_new_data_sources_priority.py")
    print()
    print("4. 🔍 如果仍有问题:")
    print("   - 检查 backend/.env 文件中的API密钥")
    print("   - 确认抽象方法已正确实现")
    print("   - 查看详细的错误日志")

def main():
    """主函数"""
    print("🧪 优先级配置测试")
    print("=" * 60)
    
    # 1. 测试配置文件
    config_ok = test_priority_config_file()
    
    # 2. 测试Data Service
    if config_ok:
        service_ok = test_data_service_priority()
        
        if service_ok:
            print("\n🎉 测试成功！新数据源已正常工作")
        else:
            print("\n⚠️ 配置文件正确，但Data Service仍使用旧数据源")
    else:
        print("\n❌ 配置文件有问题，需要先修复")
    
    # 3. 显示初始化检查
    test_data_source_initialization()
    
    # 4. 显示下一步操作
    show_next_steps()

if __name__ == "__main__":
    main()
