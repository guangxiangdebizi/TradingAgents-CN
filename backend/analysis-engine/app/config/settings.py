"""
Analysis Engine配置设置
"""

import os
from typing import Dict, Any

# Analysis Engine配置
ANALYSIS_ENGINE_CONFIG: Dict[str, Any] = {
    # 服务配置
    "host": os.getenv("ANALYSIS_ENGINE_HOST", "0.0.0.0"),
    "port": int(os.getenv("ANALYSIS_ENGINE_PORT", "8005")),
    "debug": os.getenv("ANALYSIS_ENGINE_DEBUG", "false").lower() == "true",
    
    # 依赖服务URL
    "llm_service_url": os.getenv("LLM_SERVICE_URL", "http://localhost:8004"),
    "data_service_url": os.getenv("DATA_SERVICE_URL", "http://localhost:8003"),
    
    # 分析配置
    "default_analysis_type": os.getenv("DEFAULT_ANALYSIS_TYPE", "comprehensive"),
    "max_concurrent_analyses": int(os.getenv("MAX_CONCURRENT_ANALYSES", "5")),
    "analysis_timeout": int(os.getenv("ANALYSIS_TIMEOUT", "300")),  # 5分钟
    
    # 工具配置
    "tool_cache_ttl": int(os.getenv("TOOL_CACHE_TTL", "300")),  # 5分钟
    "max_tool_retries": int(os.getenv("MAX_TOOL_RETRIES", "3")),
    
    # 智能体配置
    "default_model": os.getenv("DEFAULT_MODEL", "deepseek-chat"),
    "default_temperature": float(os.getenv("DEFAULT_TEMPERATURE", "0.1")),
    "default_max_tokens": int(os.getenv("DEFAULT_MAX_TOKENS", "1500")),
    
    # 日志配置
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "log_format": os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
}
