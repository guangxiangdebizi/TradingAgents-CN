"""
配置管理工具
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any
from functools import lru_cache


class Config:
    """配置管理类"""
    
    def __init__(self):
        self._config = {}
        self._load_backend_env_files()
        self._load_env_config()

    def _load_backend_env_files(self):
        """加载backend环境配置文件"""
        # 获取backend目录路径
        backend_dir = Path(__file__).parent.parent.parent
        backend_env_file = backend_dir / ".backend_env"

        if backend_env_file.exists():
            print(f"✅ 加载Backend环境变量: {backend_env_file}")
            self._load_env_file(backend_env_file)
        else:
            print(f"⚠️ Backend环境文件不存在: {backend_env_file}")

    def _load_env_file(self, env_file_path: Path):
        """加载指定的.env文件"""
        try:
            with open(env_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # 移除引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        os.environ[key] = value
        except Exception as e:
            print(f"❌ 加载环境文件失败 {env_file_path}: {e}")

    def _load_env_config(self):
        """从环境变量加载配置"""
        # 服务配置
        self._config.update({
            # 服务端口
            'API_GATEWAY_PORT': int(os.getenv('API_GATEWAY_PORT', '8000')),
            'ANALYSIS_ENGINE_PORT': int(os.getenv('ANALYSIS_ENGINE_PORT', '8002')),
            'DATA_SERVICE_PORT': int(os.getenv('DATA_SERVICE_PORT', '8002')),
            'TASK_SCHEDULER_PORT': int(os.getenv('TASK_SCHEDULER_PORT', '8003')),
            'LLM_SERVICE_PORT': int(os.getenv('LLM_SERVICE_PORT', '8004')),
            'MEMORY_SERVICE_PORT': int(os.getenv('MEMORY_SERVICE_PORT', '8006')),
            'AGENT_SERVICE_PORT': int(os.getenv('AGENT_SERVICE_PORT', '8008')),

            # 服务地址
            'API_GATEWAY_HOST': os.getenv('API_GATEWAY_HOST', 'localhost'),
            'ANALYSIS_ENGINE_HOST': os.getenv('ANALYSIS_ENGINE_HOST', 'localhost'),
            'DATA_SERVICE_HOST': os.getenv('DATA_SERVICE_HOST', 'localhost'),
            'TASK_SCHEDULER_HOST': os.getenv('TASK_SCHEDULER_HOST', 'localhost'),
            'LLM_SERVICE_HOST': os.getenv('LLM_SERVICE_HOST', 'localhost'),
            'MEMORY_SERVICE_HOST': os.getenv('MEMORY_SERVICE_HOST', 'localhost'),
            'AGENT_SERVICE_HOST': os.getenv('AGENT_SERVICE_HOST', 'localhost'),
            
            # 数据库配置
            'REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379'),
            'MONGODB_URL': os.getenv('MONGODB_URL', 'mongodb://localhost:27017/tradingagents'),
            
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
        })
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self._config[key] = value
    
    def get_service_url(self, service_name: str) -> str:
        """获取服务URL"""
        # 标准化服务名称：将连字符转换为下划线
        normalized_service_name = service_name.replace('-', '_').upper()

        host_key = f"{normalized_service_name}_HOST"
        port_key = f"{normalized_service_name}_PORT"

        host = self.get(host_key, 'localhost')

        # 为不同服务设置正确的默认端口
        default_ports = {
            'API_GATEWAY': 8000,
            'ANALYSIS_ENGINE': 8001,
            'DATA_SERVICE': 8002,
            'TASK_SCHEDULER': 8003,
            'LLM_SERVICE': 8004,
            'AGENT_SERVICE': 8008,  # 修复：Agent Service实际端口是8008
            'MEMORY_SERVICE': 8006,
        }

        default_port = default_ports.get(normalized_service_name, 8000)
        port = self.get(port_key, default_port)

        return f"http://{host}:{port}"
    
    def get_database_config(self) -> Dict[str, str]:
        """获取数据库配置"""
        return {
            'redis_url': self.get('REDIS_URL'),
            'mongodb_url': self.get('MONGODB_URL'),
        }
    
    def get_api_keys(self) -> Dict[str, Optional[str]]:
        """获取API密钥配置"""
        return {
            'dashscope': self.get('DASHSCOPE_API_KEY'),
            'deepseek': self.get('DEEPSEEK_API_KEY'),
            'openai': self.get('OPENAI_API_KEY'),
            'google': self.get('GOOGLE_API_KEY'),
            'tushare': self.get('TUSHARE_TOKEN'),
            'finnhub': self.get('FINNHUB_API_KEY'),
        }
    
    def is_debug(self) -> bool:
        """是否为调试模式"""
        return self.get('DEBUG', False)
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.get('ENVIRONMENT') == 'production'


@lru_cache()
def get_config() -> Config:
    """获取全局配置实例"""
    return Config()


def get_service_config(service_name: str) -> Dict[str, Any]:
    """获取特定服务的配置"""
    config = get_config()
    
    return {
        'service_name': service_name,
        'host': config.get(f"{service_name.upper()}_HOST", 'localhost'),
        'port': config.get(f"{service_name.upper()}_PORT", 8000),
        'debug': config.is_debug(),
        'log_level': config.get('LOG_LEVEL', 'INFO'),
        'log_file': config.get('LOG_FILE'),
        'redis_url': config.get('REDIS_URL'),
        'mongodb_url': config.get('MONGODB_URL'),
    }
