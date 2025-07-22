"""
ChromaDB管理器
管理向量数据库的连接和操作
"""

import asyncio
import logging
import threading
import os
from typing import Dict, List, Any, Optional
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

class ChromaManager:
    """ChromaDB管理器 - 单例模式"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ChromaManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        
        self.client = None
        self.collections: Dict[str, Any] = {}
        self.initialized = False
        self.db_path = os.getenv('CHROMA_DB_PATH', './data/chroma_db')
        self.host = os.getenv('CHROMA_HOST', 'localhost')
        self.port = int(os.getenv('CHROMA_PORT', '8000'))
        self.use_persistent = os.getenv('CHROMA_PERSISTENT', 'true').lower() == 'true'
    
    async def initialize(self):
        """初始化ChromaDB连接"""
        if self.initialized:
            return
        
        try:
            logger.info("🗄️ 初始化ChromaDB连接...")
            
            if self.use_persistent:
                # 使用持久化存储
                logger.info(f"📁 使用持久化存储: {self.db_path}")
                
                # 确保目录存在
                os.makedirs(self.db_path, exist_ok=True)
                
                self.client = chromadb.PersistentClient(
                    path=self.db_path,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
            else:
                # 尝试连接到ChromaDB服务器
                try:
                    logger.info(f"🌐 连接到ChromaDB服务器: {self.host}:{self.port}")
                    self.client = chromadb.HttpClient(
                        host=self.host,
                        port=self.port,
                        settings=Settings(
                            anonymized_telemetry=False
                        )
                    )
                    
                    # 测试连接
                    await asyncio.get_event_loop().run_in_executor(
                        None, lambda: self.client.heartbeat()
                    )
                    
                except Exception as e:
                    logger.warning(f"⚠️ ChromaDB服务器连接失败，降级到持久化存储: {e}")
                    
                    # 降级到持久化存储
                    os.makedirs(self.db_path, exist_ok=True)
                    self.client = chromadb.PersistentClient(
                        path=self.db_path,
                        settings=Settings(
                            anonymized_telemetry=False,
                            allow_reset=True
                        )
                    )
            
            # 测试客户端
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.client.list_collections()
            )
            
            self.initialized = True
            logger.info("✅ ChromaDB连接初始化完成")
            
        except Exception as e:
            logger.error(f"❌ ChromaDB初始化失败: {e}")
            raise
    
    async def get_or_create_collection(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """获取或创建集合"""
        if not self.initialized:
            await self.initialize()
        
        # 检查缓存
        if name in self.collections:
            return self.collections[name]
        
        try:
            with self._lock:
                # 双重检查锁定
                if name in self.collections:
                    return self.collections[name]
                
                logger.info(f"📚 获取或创建集合: {name}")
                
                # 尝试获取现有集合
                try:
                    collection = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: self.client.get_collection(name)
                    )
                    logger.info(f"📖 找到现有集合: {name}")
                    
                except Exception:
                    # 集合不存在，创建新集合
                    logger.info(f"📝 创建新集合: {name}")
                    
                    collection_metadata = metadata or {}
                    collection_metadata.update({
                        "created_at": str(asyncio.get_event_loop().time()),
                        "service": "memory-service"
                    })
                    
                    collection = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self.client.create_collection(
                            name=name,
                            metadata=collection_metadata
                        )
                    )
                
                # 缓存集合
                self.collections[name] = collection
                logger.info(f"✅ 集合准备完成: {name}")
                
                return collection
                
        except Exception as e:
            logger.error(f"❌ 集合操作失败: {name} - {e}")
            raise
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """列出所有集合"""
        if not self.initialized:
            await self.initialize()
        
        try:
            collections = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.client.list_collections()
            )
            
            collections_info = []
            for collection in collections:
                info = {
                    "name": collection.name,
                    "metadata": collection.metadata,
                    "count": collection.count()
                }
                collections_info.append(info)
            
            return collections_info
            
        except Exception as e:
            logger.error(f"❌ 列出集合失败: {e}")
            return []
    
    async def delete_collection(self, name: str):
        """删除集合"""
        if not self.initialized:
            await self.initialize()
        
        try:
            logger.info(f"🗑️ 删除集合: {name}")
            
            # 从ChromaDB删除
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.client.delete_collection(name)
            )
            
            # 从缓存中移除
            if name in self.collections:
                del self.collections[name]
            
            logger.info(f"✅ 集合删除完成: {name}")
            
        except Exception as e:
            logger.error(f"❌ 集合删除失败: {name} - {e}")
            raise
    
    async def get_collection_info(self, name: str) -> Dict[str, Any]:
        """获取集合信息"""
        if not self.initialized:
            await self.initialize()
        
        try:
            collection = await self.get_or_create_collection(name)
            
            info = {
                "name": collection.name,
                "metadata": collection.metadata,
                "count": await asyncio.get_event_loop().run_in_executor(
                    None, lambda: collection.count()
                )
            }
            
            return info
            
        except Exception as e:
            logger.error(f"❌ 获取集合信息失败: {name} - {e}")
            raise
    
    async def reset_database(self):
        """重置数据库（谨慎使用）"""
        if not self.initialized:
            await self.initialize()
        
        try:
            logger.warning("⚠️ 重置ChromaDB数据库")
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.client.reset()
            )
            
            # 清空缓存
            self.collections.clear()
            
            logger.info("✅ 数据库重置完成")
            
        except Exception as e:
            logger.error(f"❌ 数据库重置失败: {e}")
            raise
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        if not self.initialized:
            await self.initialize()
        
        try:
            collections = await self.list_collections()
            
            total_documents = sum(col["count"] for col in collections)
            
            stats = {
                "total_collections": len(collections),
                "total_documents": total_documents,
                "collections": collections,
                "db_path": self.db_path if self.use_persistent else f"{self.host}:{self.port}",
                "storage_type": "persistent" if self.use_persistent else "server"
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ 获取数据库统计失败: {e}")
            return {}
    
    async def reload(self):
        """重新加载ChromaDB连接"""
        logger.info("🔄 重新加载ChromaDB连接...")
        
        # 清空缓存
        self.collections.clear()
        
        # 重新初始化
        self.initialized = False
        await self.initialize()
        
        logger.info("✅ ChromaDB连接重新加载完成")
    
    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理ChromaDB资源...")
        
        self.collections.clear()
        
        if self.client:
            # ChromaDB客户端通常不需要显式关闭
            self.client = None
        
        self.initialized = False
        
        logger.info("✅ ChromaDB资源清理完成")
