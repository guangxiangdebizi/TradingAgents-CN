#!/usr/bin/env python3
"""
深入调试Data Service内部状态
"""

import asyncio
import sys
import os
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

async def test_data_source_factory():
    """测试数据源工厂"""
    print("\n🏭 测试数据源工厂")
    print("-" * 40)
    
    try:
        # 导入数据源工厂
        sys.path.insert(0, str(Path(__file__).parent / "data-service"))
        from app.datasources.factory import get_data_source_factory
        from app.datasources.base import DataSourceType, MarketType
        
        # 获取工厂实例
        factory = get_data_source_factory()
        print("✅ 数据源工厂创建成功")
        
        # 检查已注册的数据源
        print("\n📋 已注册的数据源:")
        for source_type in DataSourceType:
            try:
                source = factory.get_data_source(source_type)
                if source:
                    print(f"  ✅ {source_type.value}: 初始化成功")
                else:
                    print(f"  ❌ {source_type.value}: 未初始化")
            except Exception as e:
                print(f"  ❌ {source_type.value}: 初始化失败 - {e}")
        
        # 测试美股数据源优先级
        print("\n🇺🇸 测试美股数据源优先级:")
        try:
            result = await factory.get_stock_info("AAPL", MarketType.US_STOCK)
            if result:
                data_source = result.get("source", "unknown")
                print(f"  ✅ 成功获取数据，使用数据源: {data_source}")
                return True
            else:
                print(f"  ❌ 获取数据失败: 返回None")
        except Exception as e:
            print(f"  ❌ 获取数据异常: {e}")
            import traceback
            traceback.print_exc()
        
        return False
        
    except Exception as e:
        print(f"❌ 数据源工厂测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_individual_data_sources():
    """测试单个数据源"""
    print("\n🔍 测试单个数据源")
    print("-" * 40)
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "data-service"))
        from app.datasources.base import DataSourceType, MarketType, DataSourceConfig
        from app.datasources.alpha_vantage_source import AlphaVantageDataSource
        from app.datasources.twelve_data_source import TwelveDataSource
        
        # 测试Alpha Vantage
        print("\n📊 测试Alpha Vantage数据源:")
        try:
            config = DataSourceConfig(
                source_type=DataSourceType.ALPHA_VANTAGE,
                api_key=os.getenv("ALPHA_VANTAGE_API_KEY"),
                rate_limit=5,
                timeout=60
            )
            
            alpha_source = AlphaVantageDataSource(config)
            print(f"  ✅ Alpha Vantage实例创建成功")
            print(f"  🔑 API Key: {config.api_key[:8] if config.api_key else 'None'}...")
            
            # 测试获取股票信息
            result = await alpha_source.get_stock_info("AAPL", MarketType.US_STOCK)
            if result:
                print(f"  ✅ 获取股票信息成功: {result.get('name', 'N/A')}")
            else:
                print(f"  ❌ 获取股票信息失败")
                
        except Exception as e:
            print(f"  ❌ Alpha Vantage测试失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试Twelve Data
        print("\n📊 测试Twelve Data数据源:")
        try:
            config = DataSourceConfig(
                source_type=DataSourceType.TWELVE_DATA,
                api_key=os.getenv("TWELVE_DATA_API_KEY"),
                rate_limit=8,
                timeout=60
            )
            
            twelve_source = TwelveDataSource(config)
            print(f"  ✅ Twelve Data实例创建成功")
            print(f"  🔑 API Key: {config.api_key[:8] if config.api_key else 'None'}...")
            
            # 测试获取股票信息
            result = await twelve_source.get_stock_info("AAPL", MarketType.US_STOCK)
            if result:
                print(f"  ✅ 获取股票信息成功: {result.get('name', 'N/A')}")
            else:
                print(f"  ❌ 获取股票信息失败")
                
        except Exception as e:
            print(f"  ❌ Twelve Data测试失败: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ 单个数据源测试失败: {e}")
        import traceback
        traceback.print_exc()

def check_environment_variables():
    """检查环境变量"""
    print("\n🔑 检查环境变量")
    print("-" * 40)
    
    required_vars = {
        'ALPHA_VANTAGE_API_KEY': 'Alpha Vantage',
        'TWELVE_DATA_API_KEY': 'Twelve Data',
        'IEX_CLOUD_API_KEY': 'IEX Cloud',
        'FINNHUB_API_KEY': 'FinnHub'
    }
    
    for var, name in required_vars.items():
        value = os.getenv(var)
        if value and value.strip():
            print(f"  ✅ {name}: {value[:8]}...")
        else:
            print(f"  ❌ {name}: 未配置或为空")

def check_import_issues():
    """检查导入问题"""
    print("\n📦 检查导入问题")
    print("-" * 40)
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "data-service"))
        
        print("  🔍 测试基础导入...")
        from app.datasources.base import DataSourceType, MarketType, DataSourceConfig
        print("    ✅ 基础类导入成功")
        
        print("  🔍 测试Alpha Vantage导入...")
        from app.datasources.alpha_vantage_source import AlphaVantageDataSource
        print("    ✅ Alpha Vantage导入成功")
        
        print("  🔍 测试Twelve Data导入...")
        from app.datasources.twelve_data_source import TwelveDataSource
        print("    ✅ Twelve Data导入成功")
        
        print("  🔍 测试IEX Cloud导入...")
        from app.datasources.iex_cloud_source import IEXCloudDataSource
        print("    ✅ IEX Cloud导入成功")
        
        print("  🔍 测试工厂导入...")
        from app.datasources.factory import get_data_source_factory
        print("    ✅ 数据源工厂导入成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_enhanced_data_manager():
    """测试增强数据管理器"""
    print("\n🚀 测试增强数据管理器")
    print("-" * 40)
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "data-service"))
        from app.enhanced_data_manager import EnhancedDataManager
        
        # 创建增强数据管理器实例
        manager = EnhancedDataManager()
        print("  ✅ 增强数据管理器创建成功")
        
        # 测试获取股票数据
        print("  🔍 测试获取股票数据...")
        result = await manager.get_enhanced_stock_data(
            symbol="AAPL",
            start_date="2024-12-01",
            end_date="2024-12-31",
            force_refresh=True
        )
        
        if result:
            data_source = result.get("data_source", "unknown")
            print(f"  ✅ 获取数据成功，数据源: {data_source}")
            return True
        else:
            print(f"  ❌ 获取数据失败")
            return False
            
    except Exception as e:
        print(f"  ❌ 增强数据管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("🔍 Data Service内部状态深度诊断")
    print("=" * 60)
    
    # 1. 检查环境变量
    check_environment_variables()
    
    # 2. 检查导入问题
    import_ok = check_import_issues()
    
    if not import_ok:
        print("\n❌ 导入失败，无法继续测试")
        return
    
    # 3. 测试单个数据源
    await test_individual_data_sources()
    
    # 4. 测试数据源工厂
    factory_ok = await test_data_source_factory()
    
    # 5. 测试增强数据管理器
    if factory_ok:
        await test_enhanced_data_manager()
    
    print(f"\n🎯 诊断总结:")
    print("如果上述测试都成功，但Data Service API仍然失败，")
    print("问题可能在于:")
    print("1. Data Service没有正确加载新的代码")
    print("2. 缓存或配置文件没有刷新")
    print("3. 进程间的环境变量传递问题")
    print("\n🔧 建议:")
    print("1. 完全停止Data Service进程")
    print("2. 清除所有Python缓存: find . -name '*.pyc' -delete")
    print("3. 重新启动Data Service")
    print("4. 检查进程是否真的重启了")

if __name__ == "__main__":
    asyncio.run(main())
