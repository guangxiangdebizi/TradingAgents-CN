#!/usr/bin/env python3
"""
数据源优先级配置演示脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.data_service.app.datasources.factory import init_data_source_factory
from backend.data_service.app.datasources.base import MarketType, DataCategory

async def demo_priority_management():
    """演示优先级管理功能"""
    print("🎯 TradingAgents 数据源优先级管理演示")
    print("=" * 50)
    
    # 初始化数据源工厂
    factory = init_data_source_factory()
    
    # 1. 显示当前配置
    print("\n📊 当前优先级配置:")
    print("-" * 30)
    current_profile = factory.get_current_priority_profile()
    print(f"当前配置文件: {current_profile}")
    
    # 2. 显示所有可用配置文件
    print("\n📋 可用配置文件:")
    print("-" * 30)
    profiles = factory.get_available_priority_profiles()
    for name, info in profiles.items():
        status = "✅ 当前" if info["is_current"] else "  "
        print(f"{status} {name}: {info['name']}")
        if info.get("description"):
            print(f"     {info['description']}")
    
    # 3. 演示切换到 AKShare 优先配置
    print(f"\n🔄 切换到 'akshare_first' 配置:")
    print("-" * 30)
    
    if "akshare_first" in profiles:
        if factory.set_priority_profile("akshare_first"):
            print("✅ 成功切换到 AKShare 优先配置")
            
            # 测试 A股数据获取
            print("\n📈 测试 A股数据获取 (AKShare 优先):")
            symbol = "000858"
            market = MarketType.A_SHARE
            
            try:
                result = await factory.get_stock_info(symbol, market)
                if result:
                    print(f"✅ 成功获取 {symbol} 信息:")
                    print(f"   股票名称: {result.get('name', 'N/A')}")
                    print(f"   数据来源: {result.get('source', 'N/A')}")
                else:
                    print(f"❌ 获取 {symbol} 信息失败")
            except Exception as e:
                print(f"❌ 获取数据异常: {e}")
        else:
            print("❌ 切换配置失败")
    else:
        print("⚠️ 'akshare_first' 配置不存在，跳过演示")
    
    # 4. 演示自定义优先级设置
    print(f"\n🎯 演示自定义优先级设置:")
    print("-" * 30)
    
    # 设置 A股基本信息优先级为: akshare -> baostock -> tushare
    custom_sources = ["akshare", "baostock", "tushare"]
    if factory.set_custom_priority(MarketType.A_SHARE, DataCategory.BASIC_INFO, custom_sources):
        print(f"✅ 成功设置 A股基本信息优先级: {' → '.join(custom_sources)}")
        
        # 测试自定义优先级
        print("\n📊 测试自定义优先级:")
        sources = factory.get_available_sources(MarketType.A_SHARE, DataCategory.BASIC_INFO)
        source_names = [s.source_type.value for s in sources]
        print(f"   实际优先级: {' → '.join(source_names)}")
    else:
        print("❌ 设置自定义优先级失败")
    
    # 5. 切换回默认配置
    print(f"\n🔄 切换回默认配置:")
    print("-" * 30)
    
    if factory.set_priority_profile("default"):
        print("✅ 成功切换回默认配置")
        
        # 显示默认配置的优先级
        print("\n📊 默认配置的 A股基本信息优先级:")
        sources = factory.get_available_sources(MarketType.A_SHARE, DataCategory.BASIC_INFO)
        source_names = [s.source_type.value for s in sources]
        print(f"   优先级: {' → '.join(source_names)}")
    else:
        print("❌ 切换回默认配置失败")

def show_usage_examples():
    """显示使用示例"""
    print("\n💡 使用示例:")
    print("=" * 50)
    
    print("\n1. 命令行管理工具:")
    print("   # 显示当前配置")
    print("   python manage_data_source_priority.py show")
    print("")
    print("   # 切换到 AKShare 优先配置")
    print("   python manage_data_source_priority.py switch akshare_first")
    print("")
    print("   # 交互式设置自定义优先级")
    print("   python manage_data_source_priority.py custom")
    print("")
    print("   # 列出所有配置文件")
    print("   python manage_data_source_priority.py list")
    
    print("\n2. API 接口:")
    print("   # 获取所有配置文件")
    print("   GET /api/data-sources/priority/profiles")
    print("")
    print("   # 切换配置文件")
    print("   POST /api/data-sources/priority/switch")
    print("   {\"profile_name\": \"akshare_first\"}")
    print("")
    print("   # 重新加载配置")
    print("   POST /api/data-sources/priority/reload")
    
    print("\n3. 配置文件位置:")
    print("   backend/data-service/app/datasources/priority_config.json")
    
    print("\n4. 预设配置文件:")
    print("   - default: 默认平衡配置")
    print("   - akshare_first: AKShare 优先配置 ⭐")
    print("   - professional: 专业付费数据源优先")
    print("   - free_only: 只使用免费数据源")
    print("   - speed_first: 速度优先配置")

async def main():
    """主函数"""
    # 运行演示
    await demo_priority_management()
    
    # 显示使用示例
    show_usage_examples()
    
    print("\n🎉 演示完成！")
    print("\n📝 总结:")
    print("✅ 支持多种预设配置文件")
    print("✅ 支持动态切换优先级配置")
    print("✅ 支持自定义优先级设置")
    print("✅ 支持命令行和 API 管理")
    print("✅ 配置持久化保存")

if __name__ == "__main__":
    asyncio.run(main())
