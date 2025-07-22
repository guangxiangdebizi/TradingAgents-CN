#!/usr/bin/env python3
"""
LLM Service 配置
"""

import os

# LLM Service配置
LLM_SERVICE_CONFIG = {
    # 服务配置
    "service_name": "llm-service",
    "service_port": int(os.getenv("LLM_SERVICE_PORT", "8004")),
    "debug": os.getenv("DEBUG", "false").lower() == "true",
    
    # Redis配置
    "redis_host": os.getenv("REDIS_HOST", "localhost"),
    "redis_port": int(os.getenv("REDIS_PORT", "6379")),
    "redis_db": int(os.getenv("REDIS_DB", "0")),
    
    # 模型配置
    "default_max_tokens": int(os.getenv("DEFAULT_MAX_TOKENS", "2000")),
    "default_temperature": float(os.getenv("DEFAULT_TEMPERATURE", "0.1")),
    "health_check_timeout": int(os.getenv("HEALTH_CHECK_TIMEOUT", "10")),
    
    # 限流配置
    "rate_limit_enabled": os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
    "rate_limit_requests_per_minute": int(os.getenv("RATE_LIMIT_RPM", "60")),
    
    # 日志配置
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "log_requests": os.getenv("LOG_REQUESTS", "true").lower() == "true",
    
    # 统计配置
    "enable_usage_tracking": os.getenv("ENABLE_USAGE_TRACKING", "true").lower() == "true",
    "usage_stats_retention_days": int(os.getenv("USAGE_STATS_RETENTION_DAYS", "30"))
}
