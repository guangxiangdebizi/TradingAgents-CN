#!/usr/bin/env python3
"""
分析引擎配置
"""

import os

# 分析引擎配置
ANALYSIS_CONFIG = {
    # 服务配置
    "data_service_url": os.getenv("DATA_SERVICE_URL", "http://localhost:8002"),
    "tradingagents_api_url": os.getenv("TRADINGAGENTS_API_URL", "http://localhost:8000"),
    
    # 分析配置
    "analysis_timeout": int(os.getenv("ANALYSIS_TIMEOUT", "120")),
    "enable_local_analysis": os.getenv("ENABLE_LOCAL_ANALYSIS", "true").lower() == "true",
    "enable_tradingagents_api": os.getenv("ENABLE_TRADINGAGENTS_API", "true").lower() == "true",
    
    # 技术分析参数
    "sma_short_period": int(os.getenv("SMA_SHORT_PERIOD", "5")),
    "sma_long_period": int(os.getenv("SMA_LONG_PERIOD", "10")),
    "historical_days": int(os.getenv("HISTORICAL_DAYS", "30")),
    
    # 缓存配置
    "cache_analysis_results": os.getenv("CACHE_ANALYSIS_RESULTS", "true").lower() == "true",
    "cache_ttl_seconds": int(os.getenv("CACHE_TTL_SECONDS", "3600")),
    
    # 日志配置
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "enable_debug": os.getenv("ENABLE_DEBUG", "false").lower() == "true"
}
