"""
日志工具
"""

import logging
import sys
from typing import Optional

def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """获取日志器"""
    
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # 创建处理器
        handler = logging.StreamHandler(sys.stdout)
        
        # 设置格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(handler)
        
        # 设置级别
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    return logger
