"""
Memory Service客户端
与Memory Service通信的客户端
"""

import asyncio
import logging
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MemoryClient:
    """Memory Service客户端"""
    
    def __init__(self, memory_service_url: str = "http://localhost:8006"):
        self.memory_service_url = memory_service_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.initialized = False
    
    async def initialize(self):
        """初始化客户端"""
        try:
            logger.info("🧠 初始化Memory Service客户端...")
            
            # 创建HTTP会话
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # 测试连接
            await self.health_check()
            
            self.initialized = True
            logger.info("✅ Memory Service客户端初始化完成")
            
        except Exception as e:
            logger.error(f"❌ Memory Service客户端初始化失败: {e}")
            # 不抛出异常，允许系统在没有记忆功能的情况下运行
            self.initialized = False
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.session:
                return False
            
            async with self.session.get(f"{self.memory_service_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("status") == "healthy"
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ Memory Service健康检查失败: {e}")
            return False
    
    async def add_memory(self, collection_name: str, situation: str, 
                        recommendation: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """添加记忆"""
        if not self.initialized or not self.session:
            logger.debug("⚠️ Memory Service未初始化，跳过记忆添加")
            return None
        
        try:
            payload = {
                "collection_name": collection_name,
                "situation": situation,
                "recommendation": recommendation,
                "metadata": metadata or {}
            }
            
            async with self.session.post(
                f"{self.memory_service_url}/api/v1/memory/add",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.debug(f"✅ 记忆添加成功: {collection_name}")
                    return result.get("data")
                else:
                    logger.warning(f"⚠️ 记忆添加失败: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 记忆添加异常: {e}")
            return None
    
    async def search_memory(self, collection_name: str, query: str, 
                           n_results: int = 3, similarity_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """搜索记忆"""
        if not self.initialized or not self.session:
            logger.debug("⚠️ Memory Service未初始化，返回空记忆列表")
            return []
        
        try:
            payload = {
                "collection_name": collection_name,
                "query": query,
                "n_results": n_results,
                "similarity_threshold": similarity_threshold
            }
            
            async with self.session.post(
                f"{self.memory_service_url}/api/v1/memory/search",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    memories = result.get("results", [])
                    logger.debug(f"✅ 记忆搜索成功: {collection_name}, 找到{len(memories)}条记录")
                    return memories
                else:
                    logger.warning(f"⚠️ 记忆搜索失败: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ 记忆搜索异常: {e}")
            return []
    
    async def get_memories(self, collection_name: str, current_situation: str, 
                          n_matches: int = 2) -> List[Dict[str, Any]]:
        """获取相关记忆（兼容原TradingAgents接口）"""
        return await self.search_memory(
            collection_name=collection_name,
            query=current_situation,
            n_results=n_matches,
            similarity_threshold=0.0
        )
    
    async def add_situations_batch(self, collection_name: str, 
                                  situations_and_advice: List[tuple]) -> Optional[Dict[str, Any]]:
        """批量添加情况和建议"""
        if not self.initialized or not self.session:
            logger.debug("⚠️ Memory Service未初始化，跳过批量记忆添加")
            return None
        
        try:
            # 逐个添加（简化实现）
            results = []
            for situation, recommendation in situations_and_advice:
                result = await self.add_memory(
                    collection_name=collection_name,
                    situation=situation,
                    recommendation=recommendation
                )
                if result:
                    results.append(result)
            
            logger.debug(f"✅ 批量记忆添加完成: {collection_name}, 成功{len(results)}条")
            
            return {
                "collection_name": collection_name,
                "added_count": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ 批量记忆添加异常: {e}")
            return None
    
    async def create_collection(self, name: str, description: str = "", 
                               metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """创建记忆集合"""
        if not self.initialized or not self.session:
            logger.debug("⚠️ Memory Service未初始化，跳过集合创建")
            return None
        
        try:
            payload = {
                "name": name,
                "description": description,
                "metadata": metadata or {}
            }
            
            async with self.session.post(
                f"{self.memory_service_url}/api/v1/collections/create",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.debug(f"✅ 集合创建成功: {name}")
                    return result
                else:
                    logger.warning(f"⚠️ 集合创建失败: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 集合创建异常: {e}")
            return None
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """获取集合列表"""
        if not self.initialized or not self.session:
            logger.debug("⚠️ Memory Service未初始化，返回空集合列表")
            return []
        
        try:
            async with self.session.get(
                f"{self.memory_service_url}/api/v1/collections/list"
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    collections = result.get("collections", [])
                    logger.debug(f"✅ 获取集合列表成功: {len(collections)}个集合")
                    return collections
                else:
                    logger.warning(f"⚠️ 获取集合列表失败: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ 获取集合列表异常: {e}")
            return []
    
    async def get_collection_stats(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """获取集合统计信息"""
        if not self.initialized or not self.session:
            logger.debug("⚠️ Memory Service未初始化，跳过统计获取")
            return None
        
        try:
            async with self.session.get(
                f"{self.memory_service_url}/api/v1/collections/{collection_name}/stats"
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    stats = result.get("stats", {})
                    logger.debug(f"✅ 获取集合统计成功: {collection_name}")
                    return stats
                else:
                    logger.warning(f"⚠️ 获取集合统计失败: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 获取集合统计异常: {e}")
            return None
    
    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理Memory Service客户端资源...")
        
        if self.session:
            await self.session.close()
            self.session = None
        
        self.initialized = False
        
        logger.info("✅ Memory Service客户端资源清理完成")

# 全局Memory客户端实例
_memory_client: Optional[MemoryClient] = None

async def get_memory_client(memory_service_url: str = "http://localhost:8006") -> MemoryClient:
    """获取全局Memory客户端实例"""
    global _memory_client
    
    if _memory_client is None:
        _memory_client = MemoryClient(memory_service_url)
        await _memory_client.initialize()
    
    return _memory_client

async def cleanup_memory_client():
    """清理全局Memory客户端"""
    global _memory_client
    
    if _memory_client:
        await _memory_client.cleanup()
        _memory_client = None
