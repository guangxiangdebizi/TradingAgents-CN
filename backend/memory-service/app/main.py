#!/usr/bin/env python3
"""
Memory Service - 记忆服务
基于Embedding的智能记忆系统，为TradingAgents提供历史经验存储和检索
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

# 导入核心模块
from .memory.memory_manager import MemoryManager
from .embedding.embedding_service import EmbeddingService
from .vector_db.chroma_manager import ChromaManager
from .models.requests import (
    AddMemoryRequest, SearchMemoryRequest, 
    CreateCollectionRequest, EmbeddingRequest
)
from .models.responses import (
    MemoryResponse, SearchResponse, 
    EmbeddingResponse, CollectionResponse
)
from .config.settings import MEMORY_SERVICE_CONFIG
from .utils.logger import get_logger

# 配置日志
logger = get_logger("memory_service")

# 创建FastAPI应用
app = FastAPI(
    title="Memory Service",
    description="TradingAgents记忆服务 - 基于Embedding的智能记忆系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
memory_manager: Optional[MemoryManager] = None
embedding_service: Optional[EmbeddingService] = None
chroma_manager: Optional[ChromaManager] = None

@app.on_event("startup")
async def startup_event():
    """启动事件"""
    global memory_manager, embedding_service, chroma_manager
    
    logger.info("🧠 启动Memory Service...")
    
    # 初始化ChromaDB管理器
    chroma_manager = ChromaManager()
    await chroma_manager.initialize()
    logger.info("✅ ChromaDB管理器初始化完成")
    
    # 初始化Embedding服务
    embedding_service = EmbeddingService()
    await embedding_service.initialize()
    logger.info("✅ Embedding服务初始化完成")
    
    # 初始化记忆管理器
    memory_manager = MemoryManager(
        chroma_manager=chroma_manager,
        embedding_service=embedding_service
    )
    await memory_manager.initialize()
    logger.info("✅ 记忆管理器初始化完成")
    
    logger.info("🎉 Memory Service启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("🔄 关闭Memory Service...")
    
    if memory_manager:
        await memory_manager.cleanup()
    
    if embedding_service:
        await embedding_service.cleanup()
    
    if chroma_manager:
        await chroma_manager.cleanup()
    
    logger.info("✅ Memory Service已关闭")

# 依赖注入
async def get_memory_manager() -> MemoryManager:
    """获取记忆管理器"""
    if not memory_manager:
        raise HTTPException(status_code=503, detail="记忆管理器未初始化")
    return memory_manager

async def get_embedding_service() -> EmbeddingService:
    """获取Embedding服务"""
    if not embedding_service:
        raise HTTPException(status_code=503, detail="Embedding服务未初始化")
    return embedding_service

# API路由

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "memory-service",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "memory_manager": memory_manager is not None,
            "embedding_service": embedding_service is not None,
            "chroma_manager": chroma_manager is not None
        }
    }

@app.post("/api/v1/memory/add", response_model=MemoryResponse)
async def add_memory(
    request: AddMemoryRequest,
    background_tasks: BackgroundTasks,
    manager: MemoryManager = Depends(get_memory_manager)
):
    """添加记忆"""
    try:
        logger.info(f"💾 添加记忆: {request.collection_name}")
        
        result = await manager.add_memory(
            collection_name=request.collection_name,
            situation=request.situation,
            recommendation=request.recommendation,
            metadata=request.metadata
        )
        
        logger.info(f"✅ 记忆添加完成: {request.collection_name}")
        
        return MemoryResponse(
            success=True,
            message="记忆添加成功",
            data=result,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ 记忆添加失败: {e}")
        raise HTTPException(status_code=500, detail=f"记忆添加失败: {str(e)}")

@app.post("/api/v1/memory/search", response_model=SearchResponse)
async def search_memory(
    request: SearchMemoryRequest,
    manager: MemoryManager = Depends(get_memory_manager)
):
    """搜索记忆"""
    try:
        logger.info(f"🔍 搜索记忆: {request.collection_name}")
        
        results = await manager.search_memory(
            collection_name=request.collection_name,
            query=request.query,
            n_results=request.n_results,
            similarity_threshold=request.similarity_threshold
        )
        
        logger.info(f"✅ 记忆搜索完成: {request.collection_name}, 找到{len(results)}条记录")
        
        return SearchResponse(
            success=True,
            results=results,
            total=len(results),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ 记忆搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"记忆搜索失败: {str(e)}")

@app.post("/api/v1/embedding/generate", response_model=EmbeddingResponse)
async def generate_embedding(
    request: EmbeddingRequest,
    service: EmbeddingService = Depends(get_embedding_service)
):
    """生成Embedding"""
    try:
        logger.info(f"🔢 生成Embedding: {request.provider}")
        
        embedding = await service.generate_embedding(
            text=request.text,
            provider=request.provider,
            model=request.model
        )
        
        logger.info(f"✅ Embedding生成完成: 维度{len(embedding)}")
        
        return EmbeddingResponse(
            success=True,
            embedding=embedding,
            dimension=len(embedding),
            provider=request.provider,
            model=request.model,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Embedding生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding生成失败: {str(e)}")

@app.post("/api/v1/collections/create", response_model=CollectionResponse)
async def create_collection(
    request: CreateCollectionRequest,
    manager: MemoryManager = Depends(get_memory_manager)
):
    """创建记忆集合"""
    try:
        logger.info(f"📚 创建记忆集合: {request.name}")
        
        collection = await manager.create_collection(
            name=request.name,
            description=request.description,
            metadata=request.metadata
        )
        
        logger.info(f"✅ 记忆集合创建完成: {request.name}")
        
        return CollectionResponse(
            success=True,
            collection_name=request.name,
            description=request.description,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ 记忆集合创建失败: {e}")
        raise HTTPException(status_code=500, detail=f"记忆集合创建失败: {str(e)}")

@app.get("/api/v1/collections/list")
async def list_collections(
    manager: MemoryManager = Depends(get_memory_manager)
):
    """获取记忆集合列表"""
    try:
        collections = await manager.list_collections()
        
        return {
            "success": True,
            "collections": collections,
            "total": len(collections),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 获取集合列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取集合列表失败: {str(e)}")

@app.get("/api/v1/collections/{collection_name}/stats")
async def get_collection_stats(
    collection_name: str,
    manager: MemoryManager = Depends(get_memory_manager)
):
    """获取集合统计信息"""
    try:
        stats = await manager.get_collection_stats(collection_name)
        
        return {
            "success": True,
            "collection_name": collection_name,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 获取集合统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取集合统计失败: {str(e)}")

@app.delete("/api/v1/collections/{collection_name}")
async def delete_collection(
    collection_name: str,
    manager: MemoryManager = Depends(get_memory_manager)
):
    """删除记忆集合"""
    try:
        logger.info(f"🗑️ 删除记忆集合: {collection_name}")
        
        await manager.delete_collection(collection_name)
        
        logger.info(f"✅ 记忆集合删除完成: {collection_name}")
        
        return {
            "success": True,
            "message": f"集合 {collection_name} 删除成功",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 记忆集合删除失败: {e}")
        raise HTTPException(status_code=500, detail=f"记忆集合删除失败: {str(e)}")

@app.post("/api/v1/admin/reload")
async def reload_service():
    """重新加载服务"""
    try:
        logger.info("🔄 重新加载Memory Service...")
        
        if memory_manager:
            await memory_manager.reload()
        
        if embedding_service:
            await embedding_service.reload()
        
        logger.info("✅ Memory Service重新加载完成")
        
        return {
            "success": True,
            "message": "服务重新加载完成",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 服务重新加载失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务重新加载失败: {str(e)}")

if __name__ == "__main__":
    import sys
    from pathlib import Path

    # 添加shared路径
    shared_path = Path(__file__).parent.parent.parent / "shared"
    sys.path.insert(0, str(shared_path))

    from utils.config import get_config

    config = get_config()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=config.get('MEMORY_SERVICE_PORT', 8006),
        reload=config.get('DEBUG', False),
        log_level=config.get('LOG_LEVEL', 'INFO').lower()
    )
