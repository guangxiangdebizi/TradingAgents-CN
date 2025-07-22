#!/usr/bin/env python3
"""
验证JSON配置文件语法
"""

import json
import sys
from pathlib import Path

def validate_priority_config():
    """验证优先级配置文件"""
    print("🔍 验证优先级配置文件")
    print("=" * 50)
    
    config_file = Path(__file__).parent / "data-service/app/datasources/priority_config.json"
    
    if not config_file.exists():
        print(f"❌ 配置文件不存在: {config_file}")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ JSON语法正确")
        
        # 检查基本结构
        if "current_profile" not in config:
            print("❌ 缺少 current_profile 字段")
            return False
        
        if "priority_profiles" not in config:
            print("❌ 缺少 priority_profiles 字段")
            return False
        
        if "data_source_info" not in config:
            print("❌ 缺少 data_source_info 字段")
            return False
        
        print("✅ 基本结构正确")
        
        # 检查当前配置文件
        current_profile = config["current_profile"]
        print(f"📊 当前配置文件: {current_profile}")
        
        if current_profile not in config["priority_profiles"]:
            print(f"❌ 当前配置文件 {current_profile} 不存在")
            return False
        
        # 检查美股优先级配置
        default_priorities = config["priority_profiles"][current_profile]["priorities"]
        us_basic_info = default_priorities.get("us_stock_basic_info", [])
        
        print(f"\n🇺🇸 美股基本信息优先级:")
        for i, source in enumerate(us_basic_info, 1):
            print(f"  {i}. {source}")
        
        # 检查数据源信息
        data_source_info = config["data_source_info"]
        print(f"\n📋 已配置的数据源:")
        for source_name, info in data_source_info.items():
            print(f"  ✅ {source_name}: {info.get('name', 'N/A')}")
        
        # 检查是否有无效的数据源引用
        all_sources = set(data_source_info.keys())
        invalid_sources = []
        
        for profile_name, profile in config["priority_profiles"].items():
            priorities = profile.get("priorities", {})
            for priority_key, source_list in priorities.items():
                for source in source_list:
                    if source not in all_sources:
                        invalid_sources.append((profile_name, priority_key, source))
        
        if invalid_sources:
            print(f"\n❌ 发现无效的数据源引用:")
            for profile, key, source in invalid_sources:
                print(f"  {profile}.{key}: {source}")
            return False
        else:
            print(f"\n✅ 所有数据源引用都有效")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON语法错误: {e}")
        print(f"   行号: {e.lineno}, 列号: {e.colno}")
        return False
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 JSON配置文件验证")
    print("=" * 60)
    
    success = validate_priority_config()
    
    if success:
        print("\n🎉 配置文件验证成功！")
        print("✅ JSON语法正确")
        print("✅ 结构完整")
        print("✅ 数据源引用有效")
    else:
        print("\n❌ 配置文件验证失败！")
        print("💡 请修复上述问题后重试")
        sys.exit(1)

if __name__ == "__main__":
    main()
