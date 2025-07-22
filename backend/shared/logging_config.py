"""
共享日志配置模块 - 兼容版本
为了兼容不同的导入路径，这里重新导出utils.logger中的函数
"""

# 从utils.logger导入实际的实现
from .utils.logger import get_service_logger, setup_logger

# 为了兼容性，提供get_logger别名
def get_logger(name: str):
    """获取日志记录器（兼容性函数）"""
    return get_service_logger(name)

# 导出所有函数
__all__ = [
    'get_logger',
    'get_service_logger',
    'setup_logger'
]
