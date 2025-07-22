"""
Memory Service配置
"""

import os
from typing import Dict, Any

# Memory Service配置
MEMORY_SERVICE_CONFIG = {
    # 服务配置
    "host": os.getenv("MEMORY_SERVICE_HOST", "0.0.0.0"),
    "port": int(os.getenv("MEMORY_SERVICE_PORT", "8006")),
    "debug": os.getenv("MEMORY_SERVICE_DEBUG", "false").lower() == "true",
    
    # ChromaDB配置
    "chroma": {
        "db_path": os.getenv("CHROMA_DB_PATH", "./data/chroma_db"),
        "host": os.getenv("CHROMA_HOST", "localhost"),
        "port": int(os.getenv("CHROMA_PORT", "8000")),
        "persistent": os.getenv("CHROMA_PERSISTENT", "true").lower() == "true",
        "reset_on_start": os.getenv("CHROMA_RESET_ON_START", "false").lower() == "true"
    },
    
    # Embedding配置
    "embedding": {
        "default_provider": os.getenv("DEFAULT_EMBEDDING_PROVIDER", "dashscope"),
        "default_model": os.getenv("DEFAULT_EMBEDDING_MODEL", "text-embedding-v3"),
        "timeout": int(os.getenv("EMBEDDING_TIMEOUT", "30")),
        "retry_attempts": int(os.getenv("EMBEDDING_RETRY_ATTEMPTS", "3")),
        "batch_size": int(os.getenv("EMBEDDING_BATCH_SIZE", "100"))
    },
    
    # 记忆配置
    "memory": {
        "default_similarity_threshold": float(os.getenv("DEFAULT_SIMILARITY_THRESHOLD", "0.0")),
        "max_search_results": int(os.getenv("MAX_SEARCH_RESULTS", "20")),
        "auto_cleanup": os.getenv("MEMORY_AUTO_CLEANUP", "true").lower() == "true",
        "cleanup_interval": int(os.getenv("MEMORY_CLEANUP_INTERVAL", "3600")),  # 秒
        "max_memory_age": int(os.getenv("MAX_MEMORY_AGE", "2592000"))  # 30天
    },
    
    # 缓存配置
    "cache": {
        "enable_embedding_cache": os.getenv("ENABLE_EMBEDDING_CACHE", "true").lower() == "true",
        "cache_ttl": int(os.getenv("CACHE_TTL", "3600")),  # 1小时
        "max_cache_size": int(os.getenv("MAX_CACHE_SIZE", "10000"))
    },
    
    # 日志配置
    "logging": {
        "level": os.getenv("LOG_LEVEL", "INFO"),
        "format": os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
        "file": os.getenv("LOG_FILE", "memory_service.log"),
        "max_size": int(os.getenv("LOG_MAX_SIZE", "10485760")),  # 10MB
        "backup_count": int(os.getenv("LOG_BACKUP_COUNT", "5"))
    },
    
    # 性能配置
    "performance": {
        "max_concurrent_requests": int(os.getenv("MAX_CONCURRENT_REQUESTS", "100")),
        "request_timeout": int(os.getenv("REQUEST_TIMEOUT", "60")),
        "worker_threads": int(os.getenv("WORKER_THREADS", "4")),
        "enable_async": os.getenv("ENABLE_ASYNC", "true").lower() == "true"
    },
    
    # 安全配置
    "security": {
        "enable_auth": os.getenv("ENABLE_AUTH", "false").lower() == "true",
        "api_key": os.getenv("MEMORY_SERVICE_API_KEY"),
        "allowed_origins": os.getenv("ALLOWED_ORIGINS", "*").split(","),
        "rate_limit": int(os.getenv("RATE_LIMIT", "1000"))  # 每分钟请求数
    },
    
    # 监控配置
    "monitoring": {
        "enable_metrics": os.getenv("ENABLE_METRICS", "true").lower() == "true",
        "metrics_port": int(os.getenv("METRICS_PORT", "8007")),
        "health_check_interval": int(os.getenv("HEALTH_CHECK_INTERVAL", "30")),
        "enable_tracing": os.getenv("ENABLE_TRACING", "false").lower() == "true"
    }
}

# API密钥配置
API_KEYS = {
    "dashscope": os.getenv("DASHSCOPE_API_KEY"),
    "openai": os.getenv("OPENAI_API_KEY"),
    "deepseek": os.getenv("DEEPSEEK_API_KEY"),
    "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    "google": os.getenv("GOOGLE_API_KEY")
}

# 默认集合配置
DEFAULT_COLLECTIONS = [
    {
        "name": "bull_memory",
        "description": "看涨分析师的历史记忆",
        "metadata": {"agent_type": "bull_researcher", "category": "investment"}
    },
    {
        "name": "bear_memory",
        "description": "看跌分析师的历史记忆", 
        "metadata": {"agent_type": "bear_researcher", "category": "investment"}
    },
    {
        "name": "trader_memory",
        "description": "交易员的历史记忆",
        "metadata": {"agent_type": "trader", "category": "trading"}
    },
    {
        "name": "risk_manager_memory",
        "description": "风险管理师的历史记忆",
        "metadata": {"agent_type": "risk_manager", "category": "risk"}
    },
    {
        "name": "research_manager_memory",
        "description": "研究主管的历史记忆",
        "metadata": {"agent_type": "research_manager", "category": "management"}
    },
    {
        "name": "fundamentals_memory",
        "description": "基本面分析的历史记忆",
        "metadata": {"agent_type": "fundamentals_analyst", "category": "analysis"}
    },
    {
        "name": "technical_memory",
        "description": "技术分析的历史记忆",
        "metadata": {"agent_type": "technical_analyst", "category": "analysis"}
    },
    {
        "name": "news_memory",
        "description": "新闻分析的历史记忆",
        "metadata": {"agent_type": "news_analyst", "category": "analysis"}
    },
    {
        "name": "market_memory",
        "description": "市场分析的历史记忆",
        "metadata": {"agent_type": "market_analyst", "category": "analysis"}
    }
]

# Embedding模型配置
EMBEDDING_MODELS = {
    "dashscope": {
        "models": ["text-embedding-v3", "text-embedding-v2"],
        "default": "text-embedding-v3",
        "dimension": 1536,
        "max_tokens": 8192
    },
    "openai": {
        "models": ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
        "default": "text-embedding-3-small",
        "dimension": 1536,
        "max_tokens": 8191
    },
    "deepseek": {
        "models": ["text-embedding-3-small"],
        "default": "text-embedding-3-small", 
        "dimension": 1536,
        "max_tokens": 8191
    },
    "ollama": {
        "models": ["nomic-embed-text", "all-minilm"],
        "default": "nomic-embed-text",
        "dimension": 768,
        "max_tokens": 2048
    }
}

def get_config() -> Dict[str, Any]:
    """获取完整配置"""
    return MEMORY_SERVICE_CONFIG

def get_embedding_config(provider: str) -> Dict[str, Any]:
    """获取Embedding配置"""
    return EMBEDDING_MODELS.get(provider, {})

def validate_config() -> bool:
    """验证配置"""
    try:
        # 检查必要的配置项
        required_keys = ["host", "port", "chroma", "embedding", "memory"]
        for key in required_keys:
            if key not in MEMORY_SERVICE_CONFIG:
                raise ValueError(f"缺少必要配置: {key}")
        
        # 检查端口范围
        port = MEMORY_SERVICE_CONFIG["port"]
        if not (1 <= port <= 65535):
            raise ValueError(f"端口号无效: {port}")
        
        # 检查ChromaDB路径
        chroma_path = MEMORY_SERVICE_CONFIG["chroma"]["db_path"]
        if not chroma_path:
            raise ValueError("ChromaDB路径不能为空")
        
        return True
        
    except Exception as e:
        print(f"配置验证失败: {e}")
        return False
