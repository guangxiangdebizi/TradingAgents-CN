#!/usr/bin/env python3
"""
验证数据源配置的脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.data_service.app.datasources.config import DataSourceConfigManager
from backend.data_service.app.datasources.base import DataSourceType, MarketType, DataCategory

def validate_configuration():
    """验证数据源配置"""
    print("🔧 验证数据源配置")
    print("=" * 50)
    
    # 1. 验证配置
    warnings = DataSourceConfigManager.validate_config()
    if warnings:
        print("⚠️ 配置警告:")
        for warning in warnings:
            print(f"   {warning}")
    else:
        print("✅ 配置验证通过")
    
    # 2. 显示API密钥状态
    print("\n🔑 API密钥状态:")
    print("-" * 30)
    api_keys = DataSourceConfigManager.get_api_keys()
    for source, key in api_keys.items():
        status = "✅ 已配置" if key else "❌ 未配置"
        print(f"   {source.upper()}: {status}")
    
    # 3. 显示数据源优先级
    print("\n📊 数据源优先级配置:")
    print("-" * 30)
    priority_config = DataSourceConfigManager.get_priority_config()
    
    for market in MarketType:
        print(f"\n📈 {market.value.upper()}:")
        for category in DataCategory:
            key = f"{market.value}_{category.value}"
            sources = priority_config.get(key, [])
            if sources:
                source_names = " → ".join([s.value for s in sources])
                print(f"   {category.value}: {source_names}")
    
    # 4. 显示频率限制
    print("\n⏱️ 频率限制配置:")
    print("-" * 30)
    rate_limits = DataSourceConfigManager.get_rate_limits()
    for source, limit in rate_limits.items():
        print(f"   {source.value}: {limit} 次/分钟")
    
    # 5. 显示超时配置
    print("\n⏰ 超时配置:")
    print("-" * 30)
    timeouts = DataSourceConfigManager.get_timeout_config()
    for source, timeout in timeouts.items():
        print(f"   {source.value}: {timeout} 秒")
    
    # 6. 显示缓存配置
    print("\n💾 缓存配置:")
    print("-" * 30)
    cache_config = DataSourceConfigManager.get_cache_config()
    for category, config in cache_config.items():
        print(f"   {category.value}:")
        print(f"     缓存时长: {config['cache_duration_hours']} 小时")
        print(f"     Redis TTL: {config['redis_ttl']} 秒")
        print(f"     MongoDB: {'启用' if config['enable_mongodb'] else '禁用'}")
    
    # 7. 显示重试配置
    print("\n🔄 重试配置:")
    print("-" * 30)
    retry_config = DataSourceConfigManager.get_retry_config()
    for source, config in retry_config.items():
        print(f"   {source.value}:")
        print(f"     最大重试: {config['max_retries']} 次")
        print(f"     重试延迟: {config['retry_delay']} 秒")
        print(f"     退避因子: {config['backoff_factor']}")
    
    # 8. 显示数据质量配置
    print("\n📏 数据质量配置:")
    print("-" * 30)
    quality_config = DataSourceConfigManager.get_data_quality_config()
    for key, value in quality_config.items():
        print(f"   {key}: {value}")
    
    # 9. 显示降级配置
    print("\n🔄 降级配置:")
    print("-" * 30)
    fallback_config = DataSourceConfigManager.get_fallback_config()
    for key, value in fallback_config.items():
        print(f"   {key}: {value}")
    
    print("\n🎉 配置验证完成！")

def check_environment_variables():
    """检查环境变量"""
    print("\n🌍 环境变量检查:")
    print("-" * 30)
    
    required_vars = {
        "TUSHARE_TOKEN": "Tushare API Token",
        "FINNHUB_API_KEY": "FinnHub API Key",
        "ALPHA_VANTAGE_API_KEY": "Alpha Vantage API Key (可选)",
        "QUANDL_API_KEY": "Quandl API Key (可选)"
    }
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # 只显示前几位和后几位，中间用*代替
            masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "*" * len(value)
            print(f"   ✅ {var}: {masked_value}")
        else:
            print(f"   ❌ {var}: 未设置 ({description})")

def generate_env_template():
    """生成环境变量模板"""
    print("\n📝 生成 .env 模板:")
    print("-" * 30)
    
    template = """# TradingAgents 数据源配置
# 请根据需要配置相应的API密钥

# Tushare Pro API Token (必需 - A股数据)
# 获取地址: https://tushare.pro/register
TUSHARE_TOKEN=your_tushare_token_here

# FinnHub API Key (推荐 - 美股数据)
# 获取地址: https://finnhub.io/register
FINNHUB_API_KEY=your_finnhub_api_key_here

# Alpha Vantage API Key (可选 - 美股数据)
# 获取地址: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here

# Quandl API Key (可选 - 经济数据)
# 获取地址: https://www.quandl.com/tools/api
QUANDL_API_KEY=your_quandl_api_key_here

# 数据库配置
MONGODB_URL=mongodb://localhost:27017/tradingagents
REDIS_URL=redis://localhost:6379/0

# Celery 配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
"""
    
    print(template)
    
    # 保存到文件
    env_file = Path(__file__).parent / ".env.datasources.example"
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(template)
    
    print(f"📁 模板已保存到: {env_file}")

def main():
    """主函数"""
    print("🔧 TradingAgents 数据源配置验证工具")
    print("=" * 50)
    
    # 验证配置
    validate_configuration()
    
    # 检查环境变量
    check_environment_variables()
    
    # 生成环境变量模板
    generate_env_template()
    
    print("\n💡 使用建议:")
    print("1. 配置必需的API密钥以获得最佳数据质量")
    print("2. FinnHub 对美股数据支持最好，建议优先配置")
    print("3. Tushare 对A股数据最全面，是A股分析的首选")
    print("4. 可以根据需要调整数据源优先级配置")
    print("5. 注意各数据源的频率限制，避免超限")

if __name__ == "__main__":
    main()
