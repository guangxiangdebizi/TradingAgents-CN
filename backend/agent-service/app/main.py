"""
Agent Service - 智能体服务
负责管理和编排所有智能体的核心微服务
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.shared.logging_config import get_logger
from backend.shared.config import get_settings
from backend.shared.database import get_database_manager
from backend.shared.redis_client import get_redis_client

from .agents.agent_manager import AgentManager
from .orchestration.collaboration_engine import CollaborationEngine
from .orchestration.debate_engine import DebateEngine
from .orchestration.consensus_algorithm import ConsensusAlgorithm
from .models.agent_models import AgentRequest, AgentResponse, DebateRequest, DebateResponse
from .models.task_models import TaskRequest, TaskResponse, TaskStatus
from .utils.state_manager import StateManager
from .utils.message_router import MessageRouter

logger = get_logger("agent-service")
settings = get_settings()

# 全局组件
agent_manager: Optional[AgentManager] = None
collaboration_engine: Optional[CollaborationEngine] = None
debate_engine: Optional[DebateEngine] = None
consensus_algorithm: Optional[ConsensusAlgorithm] = None
state_manager: Optional[StateManager] = None
message_router: Optional[MessageRouter] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global agent_manager, collaboration_engine, debate_engine, consensus_algorithm
    global state_manager, message_router
    
    logger.info("🚀 启动Agent Service...")
    
    try:
        # 初始化数据库连接
        db_manager = get_database_manager()
        redis_client = get_redis_client()
        
        # 初始化状态管理器
        state_manager = StateManager(db_manager, redis_client)
        await state_manager.initialize()
        
        # 初始化消息路由器
        message_router = MessageRouter(redis_client)
        await message_router.initialize()
        
        # 初始化智能体管理器
        agent_manager = AgentManager(db_manager, redis_client, state_manager)
        await agent_manager.initialize()
        
        # 初始化协作引擎
        collaboration_engine = CollaborationEngine(
            agent_manager, state_manager, message_router
        )
        await collaboration_engine.initialize()
        
        # 初始化辩论引擎
        debate_engine = DebateEngine(
            agent_manager, state_manager, message_router
        )
        await debate_engine.initialize()
        
        # 初始化共识算法
        consensus_algorithm = ConsensusAlgorithm(
            agent_manager, state_manager
        )
        await consensus_algorithm.initialize()
        
        logger.info("✅ Agent Service启动完成")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Agent Service启动失败: {e}")
        raise
    finally:
        logger.info("🔄 关闭Agent Service...")
        
        # 清理资源
        if consensus_algorithm:
            await consensus_algorithm.cleanup()
        if debate_engine:
            await debate_engine.cleanup()
        if collaboration_engine:
            await collaboration_engine.cleanup()
        if agent_manager:
            await agent_manager.cleanup()
        if message_router:
            await message_router.cleanup()
        if state_manager:
            await state_manager.cleanup()
        
        logger.info("✅ Agent Service关闭完成")


# 创建FastAPI应用
app = FastAPI(
    title="TradingAgents - Agent Service",
    description="智能体服务 - 负责管理和编排所有智能体",
    version="0.1.7",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 依赖注入
def get_agent_manager() -> AgentManager:
    if agent_manager is None:
        raise HTTPException(status_code=503, detail="Agent Manager未初始化")
    return agent_manager


def get_collaboration_engine() -> CollaborationEngine:
    if collaboration_engine is None:
        raise HTTPException(status_code=503, detail="Collaboration Engine未初始化")
    return collaboration_engine


def get_debate_engine() -> DebateEngine:
    if debate_engine is None:
        raise HTTPException(status_code=503, detail="Debate Engine未初始化")
    return debate_engine


def get_consensus_algorithm() -> ConsensusAlgorithm:
    if consensus_algorithm is None:
        raise HTTPException(status_code=503, detail="Consensus Algorithm未初始化")
    return consensus_algorithm


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "TradingAgents Agent Service",
        "version": "0.1.7",
        "status": "running",
        "description": "智能体服务 - 负责管理和编排所有智能体"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查各组件状态
        components_status = {
            "agent_manager": agent_manager is not None and await agent_manager.health_check(),
            "collaboration_engine": collaboration_engine is not None and await collaboration_engine.health_check(),
            "debate_engine": debate_engine is not None and await debate_engine.health_check(),
            "consensus_algorithm": consensus_algorithm is not None and await consensus_algorithm.health_check(),
            "state_manager": state_manager is not None and await state_manager.health_check(),
            "message_router": message_router is not None and await message_router.health_check()
        }

        all_healthy = all(components_status.values())

        return {
            "status": "healthy" if all_healthy else "degraded",
            "components": components_status,
            "timestamp": "2025-01-22T10:00:00Z"
        }
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2025-01-22T10:00:00Z"
            }
        )


# API路由
from .api.agents_api import router as agents_router
from .api.tasks_api import router as tasks_router
from .api.collaboration_api import router as collaboration_router
from .api.debate_api import router as debate_router

app.include_router(agents_router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(collaboration_router, prefix="/api/v1/collaboration", tags=["collaboration"])
app.include_router(debate_router, prefix="/api/v1/debate", tags=["debate"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8008,
        reload=True,
        log_level="info"
    )
