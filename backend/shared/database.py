"""
共享数据库模块
"""

from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from .config import get_settings
from .logging_config import get_logger

logger = get_logger("database")


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self._connected = False
    
    async def connect(self) -> bool:
        """连接到数据库"""
        try:
            mongodb_url = self.settings.mongodb_url
            if not mongodb_url:
                logger.error("❌ MongoDB URL 未配置")
                return False
            
            # 创建客户端
            self.client = AsyncIOMotorClient(
                mongodb_url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=5
            )
            
            # 测试连接
            await self.client.admin.command('ping')
            
            # 获取数据库
            database_name = self.settings.get('MONGODB_DATABASE', 'tradingagents')
            self.db = self.client[database_name]
            self._connected = True
            
            logger.info("✅ MongoDB 连接成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ MongoDB 连接失败: {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """断开数据库连接"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("🔌 MongoDB 连接已断开")
    
    def get_collection(self, name: str) -> Optional[AsyncIOMotorCollection]:
        """获取集合"""
        if not self._connected or not self.db:
            logger.error("❌ 数据库未连接")
            return None
        return self.db[name]
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.client:
                return False
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"❌ 数据库健康检查失败: {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected


# 全局数据库管理器实例
_database_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    global _database_manager
    
    if _database_manager is None:
        _database_manager = DatabaseManager()
    
    return _database_manager


async def init_database() -> DatabaseManager:
    """初始化数据库连接"""
    db_manager = get_database_manager()
    await db_manager.connect()
    return db_manager
