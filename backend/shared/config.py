"""
共享配置模块
"""

import os
from typing import Any, Dict
from functools import lru_cache


class Settings:
    """应用设置"""
    
    def __init__(self):
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        return {
            # 数据库配置
            'MONGODB_URL': os.getenv('MONGODB_URL', 'mongodb://localhost:27017'),
            'MONGODB_HOST': os.getenv('MONGODB_HOST', 'localhost'),
            'MONGODB_PORT': int(os.getenv('MONGODB_PORT', '27017')),
            'MONGODB_USERNAME': os.getenv('MONGODB_USERNAME'),
            'MONGODB_PASSWORD': os.getenv('MONGODB_PASSWORD'),
            'MONGODB_DATABASE': os.getenv('MONGODB_DATABASE', 'tradingagents'),
            
            # Redis配置
            'REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379'),
            'REDIS_HOST': os.getenv('REDIS_HOST', 'localhost'),
            'REDIS_PORT': int(os.getenv('REDIS_PORT', '6379')),
            'REDIS_DB': int(os.getenv('REDIS_DB', '0')),
            'REDIS_PASSWORD': os.getenv('REDIS_PASSWORD'),
            
            # API密钥
            'DASHSCOPE_API_KEY': os.getenv('DASHSCOPE_API_KEY'),
            'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
            'TUSHARE_TOKEN': os.getenv('TUSHARE_TOKEN'),
            'FINNHUB_API_KEY': os.getenv('FINNHUB_API_KEY'),
            
            # 日志配置
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
            'LOG_FILE': os.getenv('LOG_FILE'),
            
            # 其他配置
            'DEBUG': os.getenv('DEBUG', 'false').lower() == 'true',
            'ENVIRONMENT': os.getenv('ENVIRONMENT', 'development'),
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self._config[key] = value
    
    @property
    def mongodb_url(self) -> str:
        """MongoDB连接URL"""
        return self.get('MONGODB_URL')
    
    @property
    def redis_url(self) -> str:
        """Redis连接URL"""
        return self.get('REDIS_URL')
    
    @property
    def log_level(self) -> str:
        """日志级别"""
        return self.get('LOG_LEVEL', 'INFO')
    
    def is_debug(self) -> bool:
        """是否为调试模式"""
        return self.get('DEBUG', False)
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.get('ENVIRONMENT') == 'production'


@lru_cache()
def get_settings() -> Settings:
    """获取全局设置实例"""
    return Settings()


def get_service_config(service_name: str) -> Dict[str, Any]:
    """获取特定服务的配置"""
    settings = get_settings()
    
    return {
        'service_name': service_name,
        'host': settings.get(f"{service_name.upper()}_HOST", 'localhost'),
        'port': settings.get(f"{service_name.upper()}_PORT", 8000),
        'debug': settings.is_debug(),
        'log_level': settings.get('LOG_LEVEL', 'INFO'),
        'log_file': settings.get('LOG_FILE'),
        'redis_url': settings.get('REDIS_URL'),
        'mongodb_url': settings.get('MONGODB_URL'),
    }
