# 数据库访问层

from .mongodb import MongoDBManager, get_db_manager

# 为了兼容性，提供别名
DatabaseManager = MongoDBManager

__all__ = [
    'MongoDBManager',
    'DatabaseManager',
    'get_db_manager'
]
