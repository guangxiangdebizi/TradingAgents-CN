"""
记忆管理器
管理智能体的历史记忆和经验学习
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from ..vector_db.chroma_manager import ChromaManager
from ..embedding.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class MemoryManager:
    """记忆管理器"""
    
    def __init__(self, chroma_manager: ChromaManager, embedding_service: EmbeddingService):
        self.chroma_manager = chroma_manager
        self.embedding_service = embedding_service
        self.collections: Dict[str, Any] = {}
        self.initialized = False
    
    async def initialize(self):
        """初始化记忆管理器"""
        try:
            logger.info("🧠 初始化记忆管理器...")
            
            # 预创建常用的记忆集合
            await self._create_default_collections()
            
            self.initialized = True
            logger.info("✅ 记忆管理器初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 记忆管理器初始化失败: {e}")
            raise
    
    async def _create_default_collections(self):
        """创建默认的记忆集合"""
        default_collections = [
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
            }
        ]
        
        for collection_info in default_collections:
            try:
                await self.create_collection(
                    name=collection_info["name"],
                    description=collection_info["description"],
                    metadata=collection_info["metadata"]
                )
            except Exception as e:
                # 集合可能已存在，继续创建其他集合
                logger.debug(f"集合 {collection_info['name']} 可能已存在: {e}")
    
    async def create_collection(self, name: str, description: str = "", 
                               metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """创建记忆集合"""
        try:
            logger.info(f"📚 创建记忆集合: {name}")
            
            # 使用ChromaDB创建集合
            collection = await self.chroma_manager.get_or_create_collection(name)
            
            # 缓存集合信息
            self.collections[name] = {
                "collection": collection,
                "description": description,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat(),
                "count": 0
            }
            
            logger.info(f"✅ 记忆集合创建完成: {name}")
            return self.collections[name]
            
        except Exception as e:
            logger.error(f"❌ 记忆集合创建失败: {name} - {e}")
            raise
    
    async def add_memory(self, collection_name: str, situation: str, 
                        recommendation: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """添加记忆"""
        try:
            logger.info(f"💾 添加记忆到集合: {collection_name}")
            
            # 获取或创建集合
            if collection_name not in self.collections:
                await self.create_collection(collection_name)
            
            collection_info = self.collections[collection_name]
            collection = collection_info["collection"]
            
            # 生成Embedding
            embedding = await self.embedding_service.generate_embedding(situation)
            
            # 生成唯一ID
            memory_id = str(uuid.uuid4())
            
            # 准备元数据
            memory_metadata = {
                "recommendation": recommendation,
                "timestamp": datetime.now().isoformat(),
                "collection_name": collection_name
            }
            if metadata:
                memory_metadata.update(metadata)
            
            # 添加到ChromaDB
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: collection.add(
                    documents=[situation],
                    metadatas=[memory_metadata],
                    embeddings=[embedding],
                    ids=[memory_id]
                )
            )
            
            # 更新计数
            collection_info["count"] += 1
            
            logger.info(f"✅ 记忆添加完成: {collection_name} - {memory_id}")
            
            return {
                "memory_id": memory_id,
                "situation": situation,
                "recommendation": recommendation,
                "metadata": memory_metadata,
                "collection_name": collection_name
            }
            
        except Exception as e:
            logger.error(f"❌ 记忆添加失败: {collection_name} - {e}")
            raise
    
    async def search_memory(self, collection_name: str, query: str, 
                           n_results: int = 3, similarity_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """搜索记忆"""
        try:
            logger.info(f"🔍 搜索记忆: {collection_name}")
            
            # 检查集合是否存在
            if collection_name not in self.collections:
                logger.warning(f"⚠️ 集合不存在: {collection_name}")
                return []
            
            collection = self.collections[collection_name]["collection"]
            
            # 生成查询Embedding
            query_embedding = await self.embedding_service.generate_embedding(query)
            
            # 执行相似性搜索
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    include=["metadatas", "documents", "distances"]
                )
            )
            
            # 处理搜索结果
            matched_memories = []
            
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    distance = results["distances"][0][i]
                    similarity_score = 1 - distance  # 距离转相似度
                    
                    # 过滤低相似度结果
                    if similarity_score >= similarity_threshold:
                        memory = {
                            "matched_situation": results["documents"][0][i],
                            "recommendation": results["metadatas"][0][i]["recommendation"],
                            "similarity_score": similarity_score,
                            "metadata": results["metadatas"][0][i],
                            "distance": distance
                        }
                        matched_memories.append(memory)
            
            logger.info(f"✅ 记忆搜索完成: {collection_name}, 找到{len(matched_memories)}条记录")
            return matched_memories
            
        except Exception as e:
            logger.error(f"❌ 记忆搜索失败: {collection_name} - {e}")
            return []
    
    async def add_situations_batch(self, collection_name: str, 
                                  situations_and_advice: List[tuple]) -> Dict[str, Any]:
        """批量添加情况和建议"""
        try:
            logger.info(f"📦 批量添加记忆: {collection_name}, 数量: {len(situations_and_advice)}")
            
            results = []
            for situation, recommendation in situations_and_advice:
                result = await self.add_memory(
                    collection_name=collection_name,
                    situation=situation,
                    recommendation=recommendation
                )
                results.append(result)
            
            logger.info(f"✅ 批量添加完成: {collection_name}")
            
            return {
                "collection_name": collection_name,
                "added_count": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ 批量添加失败: {collection_name} - {e}")
            raise
    
    async def get_memories(self, collection_name: str, current_situation: str, 
                          n_matches: int = 2) -> List[Dict[str, Any]]:
        """获取相关记忆（兼容原TradingAgents接口）"""
        return await self.search_memory(
            collection_name=collection_name,
            query=current_situation,
            n_results=n_matches,
            similarity_threshold=0.0
        )
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """获取所有集合列表"""
        collections_list = []
        
        for name, info in self.collections.items():
            collections_list.append({
                "name": name,
                "description": info.get("description", ""),
                "metadata": info.get("metadata", {}),
                "created_at": info.get("created_at", ""),
                "count": info.get("count", 0)
            })
        
        return collections_list
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """获取集合统计信息"""
        if collection_name not in self.collections:
            raise ValueError(f"集合不存在: {collection_name}")
        
        collection_info = self.collections[collection_name]
        collection = collection_info["collection"]
        
        # 获取实际计数
        try:
            actual_count = await asyncio.get_event_loop().run_in_executor(
                None, lambda: collection.count()
            )
            collection_info["count"] = actual_count
        except Exception as e:
            logger.warning(f"⚠️ 获取集合计数失败: {e}")
            actual_count = collection_info.get("count", 0)
        
        return {
            "name": collection_name,
            "description": collection_info.get("description", ""),
            "count": actual_count,
            "metadata": collection_info.get("metadata", {}),
            "created_at": collection_info.get("created_at", "")
        }
    
    async def delete_collection(self, collection_name: str):
        """删除集合"""
        try:
            logger.info(f"🗑️ 删除记忆集合: {collection_name}")
            
            if collection_name in self.collections:
                # 从ChromaDB删除
                await self.chroma_manager.delete_collection(collection_name)
                
                # 从缓存中移除
                del self.collections[collection_name]
                
                logger.info(f"✅ 记忆集合删除完成: {collection_name}")
            else:
                logger.warning(f"⚠️ 集合不存在: {collection_name}")
                
        except Exception as e:
            logger.error(f"❌ 记忆集合删除失败: {collection_name} - {e}")
            raise
    
    async def reload(self):
        """重新加载记忆管理器"""
        logger.info("🔄 重新加载记忆管理器...")
        
        # 重新加载Embedding服务
        await self.embedding_service.reload()
        
        # 重新加载ChromaDB管理器
        await self.chroma_manager.reload()
        
        # 重新创建默认集合
        await self._create_default_collections()
        
        logger.info("✅ 记忆管理器重新加载完成")
    
    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理记忆管理器资源...")
        
        self.collections.clear()
        self.initialized = False
        
        logger.info("✅ 记忆管理器资源清理完成")
