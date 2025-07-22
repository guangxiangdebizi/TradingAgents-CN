#!/usr/bin/env python3
"""
测试环境变量加载情况
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_env_loading():
    """测试环境变量加载"""
    print("🔍 环境变量加载测试")
    print("=" * 60)
    
    # 检查.env文件存在情况
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent
    
    backend_env = backend_dir / ".env"
    root_env = project_root / ".env"
    
    print("📁 .env文件检查:")
    print(f"  Backend .env: {backend_env} - {'✅ 存在' if backend_env.exists() else '❌ 不存在'}")
    print(f"  项目根目录 .env: {root_env} - {'✅ 存在' if root_env.exists() else '❌ 不存在'}")
    
    # 加载环境变量
    try:
        from dotenv import load_dotenv
        
        if backend_env.exists():
            load_dotenv(backend_env, override=True)
            print(f"✅ 已加载Backend .env文件")
        
        if root_env.exists():
            load_dotenv(root_env, override=False)
            print(f"✅ 已加载项目根目录 .env文件")
            
    except ImportError:
        print("❌ python-dotenv未安装")
        return False
    
    # 检查关键API密钥
    print("\n🔑 API密钥检查:")
    api_keys = {
        'ALPHA_VANTAGE_API_KEY': 'Alpha Vantage',
        'TWELVE_DATA_API_KEY': 'Twelve Data',
        'IEX_CLOUD_API_KEY': 'IEX Cloud',
        'FINNHUB_API_KEY': 'FinnHub',
        'TUSHARE_TOKEN': 'Tushare'
    }
    
    configured_count = 0
    for key, name in api_keys.items():
        value = os.getenv(key)
        if value and value != f"your_{key.lower()}_here":
            print(f"  ✅ {name}: 已配置 ({value[:8]}...)")
            configured_count += 1
        else:
            print(f"  ❌ {name}: 未配置")
    
    print(f"\n📊 配置状态: {configured_count}/{len(api_keys)} 个API密钥已配置")
    
    # 检查其他重要环境变量
    print("\n⚙️ 其他环境变量:")
    other_vars = {
        'MONGODB_URL': 'MongoDB连接',
        'REDIS_URL': 'Redis连接',
        'DEBUG': '调试模式',
        'LOG_LEVEL': '日志级别'
    }
    
    for key, desc in other_vars.items():
        value = os.getenv(key)
        if value:
            # 对于敏感信息，只显示部分内容
            if 'URL' in key and '@' in value:
                # 隐藏密码部分
                display_value = value.split('@')[0].split('//')[0] + '//***@' + value.split('@')[1]
            else:
                display_value = value
            print(f"  ✅ {desc}: {display_value}")
        else:
            print(f"  ❌ {desc}: 未设置")
    
    return configured_count > 0

def test_data_source_env_vars():
    """专门测试数据源相关的环境变量"""
    print("\n🌐 数据源环境变量详细检查")
    print("=" * 60)
    
    # 模拟Data Service的环境变量加载
    print("📋 模拟Data Service环境变量加载过程:")
    
    # 检查新数据源API密钥
    new_sources = {
        'ALPHA_VANTAGE_API_KEY': {
            'name': 'Alpha Vantage',
            'description': '免费版每天500次请求'
        },
        'TWELVE_DATA_API_KEY': {
            'name': 'Twelve Data', 
            'description': '免费版每天800次请求'
        },
        'IEX_CLOUD_API_KEY': {
            'name': 'IEX Cloud',
            'description': '免费版每月100,000次请求'
        }
    }
    
    print("\n🆕 新美股数据源API密钥:")
    new_configured = 0
    for key, info in new_sources.items():
        value = os.getenv(key)
        if value and value != f"your_{key.lower()}_here":
            print(f"  ✅ {info['name']}: 已配置")
            print(f"      {info['description']}")
            new_configured += 1
        else:
            print(f"  ❌ {info['name']}: 未配置")
            print(f"      {info['description']}")
    
    print(f"\n📊 新数据源配置状态: {new_configured}/{len(new_sources)} 个已配置")
    
    if new_configured == 0:
        print("\n⚠️ 警告: 没有配置任何新的美股数据源API密钥")
        print("💡 这就是为什么Data Service仍在使用旧数据源的原因")
        print("\n🔧 解决方案:")
        print("1. 运行: python backend/setup_api_keys.py")
        print("2. 或手动编辑 backend/.env 文件")
        print("3. 重启Data Service")
        return False
    
    return True

def show_env_file_priority():
    """显示环境变量文件优先级"""
    print("\n📋 环境变量文件加载优先级")
    print("=" * 60)
    
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent
    
    print("🔄 Data Service环境变量加载顺序:")
    print("1. backend/.env (最高优先级)")
    print("2. 项目根目录/.env (备用)")
    print("3. 系统环境变量 (最低优先级)")
    
    print(f"\n📁 文件路径:")
    print(f"  Backend: {backend_dir / '.env'}")
    print(f"  项目根目录: {project_root / '.env'}")
    
    print(f"\n💡 建议:")
    print("- 将新的API密钥配置到 backend/.env 文件中")
    print("- 这样可以确保Data Service能够正确加载")

def main():
    """主函数"""
    print("🧪 TradingAgents 环境变量加载测试")
    print("=" * 70)
    
    # 1. 基本环境变量测试
    has_config = test_env_loading()
    
    # 2. 数据源环境变量测试
    has_new_sources = test_data_source_env_vars()
    
    # 3. 显示优先级说明
    show_env_file_priority()
    
    print("\n🎯 总结:")
    if has_config and has_new_sources:
        print("✅ 环境变量配置完整，新数据源应该可以正常工作")
    elif has_config:
        print("⚠️ 基本配置正常，但缺少新数据源API密钥")
    else:
        print("❌ 环境变量配置不完整")
    
    print("\n🔄 下一步:")
    if not has_new_sources:
        print("1. 配置新数据源API密钥")
        print("2. 重启Data Service")
        print("3. 运行测试验证")
    else:
        print("1. 重启Data Service以加载新配置")
        print("2. 运行: python backend/test_new_data_sources_priority.py")

if __name__ == "__main__":
    main()
