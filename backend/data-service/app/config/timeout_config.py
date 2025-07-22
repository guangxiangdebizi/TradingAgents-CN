#!/usr/bin/env python3
"""
超时配置管理
"""

import os
from typing import Dict, Any

class TimeoutConfig:
    """超时配置类"""
    
    def __init__(self):
        # 数据源超时配置（秒）
        self.data_source_timeouts = {
            "tushare": int(os.getenv("TUSHARE_TIMEOUT", "60")),
            "akshare": int(os.getenv("AKSHARE_TIMEOUT", "120")),  # AKShare较慢
            "finnhub": int(os.getenv("FINNHUB_TIMEOUT", "60")),
            "yfinance": int(os.getenv("YFINANCE_TIMEOUT", "90")),  # YFinance有时很慢
            "baostock": int(os.getenv("BAOSTOCK_TIMEOUT", "90"))
        }
        
        # API请求超时配置（秒）
        self.api_timeouts = {
            "health_check": int(os.getenv("API_HEALTH_TIMEOUT", "30")),
            "stock_info": int(os.getenv("API_STOCK_INFO_TIMEOUT", "180")),  # 股票信息可能需要较长时间
            "stock_data": int(os.getenv("API_STOCK_DATA_TIMEOUT", "300")),  # 历史数据可能需要更长时间
            "enhanced_data": int(os.getenv("API_ENHANCED_DATA_TIMEOUT", "300")),  # 增强数据
            "cache_operation": int(os.getenv("API_CACHE_TIMEOUT", "60")),
            "error_handling": int(os.getenv("API_ERROR_TIMEOUT", "60"))
        }
        
        # 测试超时配置（秒）
        self.test_timeouts = {
            "basic_test": int(os.getenv("TEST_BASIC_TIMEOUT", "180")),
            "cache_test": int(os.getenv("TEST_CACHE_TIMEOUT", "180")),
            "market_detection": int(os.getenv("TEST_MARKET_TIMEOUT", "120")),
            "error_handling": int(os.getenv("TEST_ERROR_TIMEOUT", "60")),
            "formatted_api": int(os.getenv("TEST_FORMATTED_TIMEOUT", "180"))
        }
    
    def get_data_source_timeout(self, source: str) -> int:
        """获取数据源超时时间"""
        return self.data_source_timeouts.get(source.lower(), 60)
    
    def get_api_timeout(self, api_type: str) -> int:
        """获取API超时时间"""
        return self.api_timeouts.get(api_type.lower(), 60)
    
    def get_test_timeout(self, test_type: str) -> int:
        """获取测试超时时间"""
        return self.test_timeouts.get(test_type.lower(), 60)
    
    def update_timeout(self, category: str, key: str, value: int):
        """更新超时配置"""
        if category == "data_source":
            self.data_source_timeouts[key] = value
        elif category == "api":
            self.api_timeouts[key] = value
        elif category == "test":
            self.test_timeouts[key] = value
    
    def get_all_timeouts(self) -> Dict[str, Dict[str, int]]:
        """获取所有超时配置"""
        return {
            "data_source": self.data_source_timeouts,
            "api": self.api_timeouts,
            "test": self.test_timeouts
        }
    
    def print_config(self):
        """打印当前配置"""
        print("⏰ 当前超时配置:")
        print("=" * 50)
        
        print("📊 数据源超时 (秒):")
        for source, timeout in self.data_source_timeouts.items():
            print(f"  {source}: {timeout}s")
        
        print("\n🌐 API超时 (秒):")
        for api, timeout in self.api_timeouts.items():
            print(f"  {api}: {timeout}s")
        
        print("\n🧪 测试超时 (秒):")
        for test, timeout in self.test_timeouts.items():
            print(f"  {test}: {timeout}s")

# 全局超时配置实例
timeout_config = TimeoutConfig()

def get_timeout_config() -> TimeoutConfig:
    """获取超时配置实例"""
    return timeout_config

# 便捷函数
def get_data_source_timeout(source: str) -> int:
    """获取数据源超时时间"""
    return timeout_config.get_data_source_timeout(source)

def get_api_timeout(api_type: str) -> int:
    """获取API超时时间"""
    return timeout_config.get_api_timeout(api_type)

def get_test_timeout(test_type: str) -> int:
    """获取测试超时时间"""
    return timeout_config.get_test_timeout(test_type)

if __name__ == "__main__":
    # 测试配置
    config = get_timeout_config()
    config.print_config()
    
    print("\n💡 环境变量配置示例:")
    print("export AKSHARE_TIMEOUT=180")
    print("export API_STOCK_INFO_TIMEOUT=300")
    print("export TEST_BASIC_TIMEOUT=240")
