#!/usr/bin/env python3
"""
数据源配置管理
"""

import os
from typing import Dict, List, Any
from .base import DataSourceType, MarketType, DataCategory

class DataSourceConfigManager:
    """数据源配置管理器"""
    
    @staticmethod
    def get_api_keys() -> Dict[str, str]:
        """获取所有API密钥"""
        return {
            "tushare": os.getenv("TUSHARE_TOKEN", ""),
            "finnhub": os.getenv("FINNHUB_API_KEY", ""),
            "alpha_vantage": os.getenv("ALPHA_VANTAGE_API_KEY", ""),
            "quandl": os.getenv("QUANDL_API_KEY", ""),
        }
    
    @staticmethod
    def get_priority_config() -> Dict[str, List[DataSourceType]]:
        """获取数据源优先级配置"""
        return {
            # A股数据源优先级
            f"{MarketType.A_SHARE.value}_{DataCategory.BASIC_INFO.value}": [
                DataSourceType.TUSHARE, 
                DataSourceType.AKSHARE
            ],
            f"{MarketType.A_SHARE.value}_{DataCategory.PRICE_DATA.value}": [
                DataSourceType.TUSHARE, 
                DataSourceType.AKSHARE, 
                DataSourceType.BAOSTOCK
            ],
            f"{MarketType.A_SHARE.value}_{DataCategory.FUNDAMENTALS.value}": [
                DataSourceType.TUSHARE, 
                DataSourceType.AKSHARE
            ],
            f"{MarketType.A_SHARE.value}_{DataCategory.NEWS.value}": [
                DataSourceType.AKSHARE
            ],
            
            # 港股数据源优先级
            f"{MarketType.HK_STOCK.value}_{DataCategory.BASIC_INFO.value}": [
                DataSourceType.AKSHARE, 
                DataSourceType.YFINANCE
            ],
            f"{MarketType.HK_STOCK.value}_{DataCategory.PRICE_DATA.value}": [
                DataSourceType.AKSHARE, 
                DataSourceType.YFINANCE
            ],
            f"{MarketType.HK_STOCK.value}_{DataCategory.NEWS.value}": [
                DataSourceType.AKSHARE
            ],
            
            # 美股数据源优先级
            f"{MarketType.US_STOCK.value}_{DataCategory.BASIC_INFO.value}": [
                DataSourceType.FINNHUB,
                DataSourceType.YFINANCE,
                DataSourceType.AKSHARE
            ],
            f"{MarketType.US_STOCK.value}_{DataCategory.PRICE_DATA.value}": [
                DataSourceType.FINNHUB,
                DataSourceType.YFINANCE,
                DataSourceType.AKSHARE
            ],
            f"{MarketType.US_STOCK.value}_{DataCategory.FUNDAMENTALS.value}": [
                DataSourceType.FINNHUB,
                DataSourceType.YFINANCE
            ],
            f"{MarketType.US_STOCK.value}_{DataCategory.NEWS.value}": [
                DataSourceType.FINNHUB,
                DataSourceType.AKSHARE
            ],
        }
    
    @staticmethod
    def get_rate_limits() -> Dict[DataSourceType, int]:
        """获取各数据源的频率限制（每分钟请求数）"""
        return {
            DataSourceType.TUSHARE: 200,      # Tushare Pro 每分钟200次
            DataSourceType.AKSHARE: 100,      # AKShare 建议每分钟100次
            DataSourceType.BAOSTOCK: 60,      # BaoStock 每分钟60次
            DataSourceType.YFINANCE: 30,      # Yahoo Finance 限制较严，每分钟30次
            DataSourceType.FINNHUB: 60,       # FinnHub 免费版每分钟60次，付费版更高
            DataSourceType.BAOSTOCK: 60,      # BaoStock 免费，每分钟60次
        }
    
    @staticmethod
    def get_timeout_config() -> Dict[DataSourceType, int]:
        """获取各数据源的超时配置（秒）"""
        return {
            DataSourceType.TUSHARE: 30,
            DataSourceType.AKSHARE: 30,
            DataSourceType.BAOSTOCK: 20,
            DataSourceType.YFINANCE: 15,
            DataSourceType.FINNHUB: 20,
            DataSourceType.BAOSTOCK: 30,
        }
    
    @staticmethod
    def get_retry_config() -> Dict[DataSourceType, Dict[str, int]]:
        """获取各数据源的重试配置"""
        return {
            DataSourceType.TUSHARE: {
                "max_retries": 3,
                "retry_delay": 2,
                "backoff_factor": 2
            },
            DataSourceType.AKSHARE: {
                "max_retries": 2,
                "retry_delay": 1,
                "backoff_factor": 1.5
            },
            DataSourceType.BAOSTOCK: {
                "max_retries": 2,
                "retry_delay": 1,
                "backoff_factor": 1.5
            },
            DataSourceType.YFINANCE: {
                "max_retries": 3,
                "retry_delay": 1,
                "backoff_factor": 2
            },
            DataSourceType.FINNHUB: {
                "max_retries": 2,
                "retry_delay": 2,
                "backoff_factor": 2
            },
            DataSourceType.BAOSTOCK: {
                "max_retries": 2,
                "retry_delay": 1,
                "backoff_factor": 1.5
            },
        }
    
    @staticmethod
    def get_cache_config() -> Dict[DataCategory, Dict[str, Any]]:
        """获取各数据类别的缓存配置"""
        return {
            DataCategory.BASIC_INFO: {
                "cache_duration_hours": 24,    # 基本信息缓存24小时
                "redis_ttl": 86400,            # Redis TTL 24小时
                "enable_mongodb": True         # 启用MongoDB持久化
            },
            DataCategory.PRICE_DATA: {
                "cache_duration_hours": 1,     # 价格数据缓存1小时
                "redis_ttl": 3600,             # Redis TTL 1小时
                "enable_mongodb": True         # 启用MongoDB持久化
            },
            DataCategory.FUNDAMENTALS: {
                "cache_duration_hours": 6,     # 基本面数据缓存6小时
                "redis_ttl": 21600,            # Redis TTL 6小时
                "enable_mongodb": True         # 启用MongoDB持久化
            },
            DataCategory.NEWS: {
                "cache_duration_hours": 0.5,   # 新闻数据缓存30分钟
                "redis_ttl": 1800,             # Redis TTL 30分钟
                "enable_mongodb": False        # 不启用MongoDB持久化
            },
            DataCategory.TECHNICAL: {
                "cache_duration_hours": 2,     # 技术指标缓存2小时
                "redis_ttl": 7200,             # Redis TTL 2小时
                "enable_mongodb": False        # 不启用MongoDB持久化
            },
        }
    
    @staticmethod
    def get_data_quality_config() -> Dict[str, Any]:
        """获取数据质量配置"""
        return {
            "min_data_points": 5,              # 最少数据点数
            "max_missing_ratio": 0.2,          # 最大缺失比例
            "price_change_threshold": 0.5,     # 价格变化阈值（50%）
            "volume_change_threshold": 10.0,   # 成交量变化阈值（10倍）
            "enable_data_validation": True,    # 启用数据验证
            "enable_outlier_detection": True,  # 启用异常值检测
        }
    
    @staticmethod
    def get_fallback_config() -> Dict[str, Any]:
        """获取降级配置"""
        return {
            "enable_fallback": True,           # 启用降级
            "max_fallback_age_hours": 24,     # 最大降级数据年龄（小时）
            "fallback_warning_threshold": 6,   # 降级警告阈值（小时）
            "enable_legacy_tools": True,      # 启用原有工具降级
        }
    
    @classmethod
    def get_full_config(cls) -> Dict[str, Any]:
        """获取完整配置"""
        return {
            "api_keys": cls.get_api_keys(),
            "priority": cls.get_priority_config(),
            "rate_limits": cls.get_rate_limits(),
            "timeouts": cls.get_timeout_config(),
            "retries": cls.get_retry_config(),
            "cache": cls.get_cache_config(),
            "data_quality": cls.get_data_quality_config(),
            "fallback": cls.get_fallback_config(),
        }
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """验证配置"""
        warnings = []
        
        # 检查API密钥
        api_keys = cls.get_api_keys()
        if not api_keys.get("tushare"):
            warnings.append("⚠️ TUSHARE_TOKEN 未配置，Tushare数据源将不可用")
        
        if not api_keys.get("finnhub"):
            warnings.append("⚠️ FINNHUB_API_KEY 未配置，FinnHub数据源将不可用")
        
        # 检查优先级配置
        priority_config = cls.get_priority_config()
        if not priority_config:
            warnings.append("⚠️ 数据源优先级配置为空")
        
        return warnings
