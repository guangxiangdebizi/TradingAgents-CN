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
backend_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_root))

from backend.shared.utils.logger import get_service_logger
from backend.shared.utils.config import get_service_config
from backend.shared.database.mongodb import get_db_manager
import redis.asyncio as redis

# 导入核心组件
from .agents.agent_manager import AgentManager
from .utils.state_manager import StateManager
# 暂时注释掉其他复杂组件，先启用基础功能
# from .orchestration.collaboration_engine import CollaborationEngine
# from .orchestration.debate_engine import DebateEngine
# from .orchestration.consensus_algorithm import ConsensusAlgorithm
# from .models.agent_models import AgentRequest, AgentResponse, DebateRequest, DebateResponse
# from .models.task_models import TaskRequest, TaskResponse, TaskStatus
# from .utils.state_manager import StateManager
# from .utils.message_router import MessageRouter
# from .utils.performance_monitor import PerformanceMonitor
# from .orchestration.workflow_manager import WorkflowManager

logger = get_service_logger("agent-service")
service_config = get_service_config("agent-service")

# 全局组件
agent_manager: Optional[AgentManager] = None
state_manager: Optional[StateManager] = None
collaboration_engine: Optional[Any] = None
debate_engine: Optional[Any] = None
consensus_algorithm: Optional[Any] = None
state_manager: Optional[Any] = None
message_router: Optional[Any] = None
workflow_manager: Optional[Any] = None
performance_monitor: Optional[Any] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global agent_manager, collaboration_engine, debate_engine, consensus_algorithm
    global state_manager, message_router, workflow_manager, performance_monitor
    
    logger.info("🚀 启动Agent Service...")
    
    try:
        # 初始化数据库连接
        db_manager = await get_db_manager()

        # 初始化Redis连接
        redis_client = None
        try:
            redis_client = redis.from_url(service_config['redis_url'])
            await redis_client.ping()
            logger.info("✅ Redis 连接成功")
        except Exception as e:
            logger.warning(f"⚠️ Redis 连接失败: {e}")
            redis_client = None
        
        # 初始化StateManager
        try:
            global state_manager, agent_manager
            state_manager = StateManager(db_manager, redis_client)
            await state_manager.initialize()
            logger.info("✅ StateManager 初始化成功")

            # 初始化AgentManager
            agent_manager = AgentManager(db_manager, redis_client, state_manager)
            await agent_manager.initialize()
            logger.info("✅ AgentManager 初始化成功")
        except Exception as e:
            logger.error(f"❌ 组件初始化失败: {e}")
            state_manager = None
            agent_manager = None

        # 初始化其他组件
        if agent_manager is not None and state_manager is not None:
            try:
                # 导入组件类
                from .utils.message_router import MessageRouter
                from .utils.performance_monitor import PerformanceMonitor
                from .orchestration.collaboration_engine import CollaborationEngine
                from .orchestration.debate_engine import DebateEngine
                from .orchestration.consensus_algorithm import ConsensusAlgorithm
                from .orchestration.workflow_manager import WorkflowManager

                # 初始化MessageRouter
                global message_router
                message_router = MessageRouter(redis_client)
                await message_router.initialize()
                logger.info("✅ MessageRouter 初始化成功")

                # 初始化PerformanceMonitor
                global performance_monitor
                performance_monitor = PerformanceMonitor(state_manager)
                await performance_monitor.initialize()
                logger.info("✅ PerformanceMonitor 初始化成功")

                # 初始化CollaborationEngine
                global collaboration_engine
                collaboration_engine = CollaborationEngine(agent_manager, state_manager, message_router)
                await collaboration_engine.initialize()
                logger.info("✅ CollaborationEngine 初始化成功")

                # 初始化DebateEngine
                global debate_engine
                debate_engine = DebateEngine(agent_manager, state_manager, message_router)
                await debate_engine.initialize()
                logger.info("✅ DebateEngine 初始化成功")

                # 初始化ConsensusAlgorithm
                global consensus_algorithm
                consensus_algorithm = ConsensusAlgorithm(agent_manager, state_manager)
                await consensus_algorithm.initialize()
                logger.info("✅ ConsensusAlgorithm 初始化成功")

                # 初始化WorkflowManager
                global workflow_manager
                workflow_manager = WorkflowManager(agent_manager, state_manager, collaboration_engine)
                await workflow_manager.initialize()
                logger.info("✅ WorkflowManager 初始化成功")

                logger.info("✅ 所有组件初始化成功")

            except Exception as e:
                logger.error(f"❌ 高级组件初始化失败: {e}")
                # 设置为None以确保健康检查正确反映状态
                collaboration_engine = None
                debate_engine = None
                consensus_algorithm = None
                message_router = None
                workflow_manager = None
                performance_monitor = None
        else:
            logger.info("⚠️ 使用简化模式启动，部分功能暂不可用")

        logger.info("✅ Agent Service启动完成")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Agent Service启动失败: {e}")
        raise
    finally:
        logger.info("🔄 关闭Agent Service...")
        
        # 清理资源
        if redis_client:
            await redis_client.close()
        if db_manager:
            await db_manager.disconnect()
        
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


def get_collaboration_engine() -> Any:
    if collaboration_engine is None:
        raise HTTPException(status_code=503, detail="Collaboration Engine未初始化")
    return collaboration_engine


def get_debate_engine() -> Any:
    if debate_engine is None:
        raise HTTPException(status_code=503, detail="Debate Engine未初始化")
    return debate_engine


def get_consensus_algorithm() -> Any:
    if consensus_algorithm is None:
        raise HTTPException(status_code=503, detail="Consensus Algorithm未初始化")
    return consensus_algorithm


def get_workflow_manager() -> Any:
    if workflow_manager is None:
        raise HTTPException(status_code=503, detail="Workflow Manager未初始化")
    return workflow_manager


def get_performance_monitor() -> Any:
    if performance_monitor is None:
        raise HTTPException(status_code=503, detail="Performance Monitor未初始化")
    return performance_monitor


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
        # 检查核心组件状态（只检查已实现的组件）
        core_components = {
            "agent_manager": agent_manager is not None and await agent_manager.health_check(),
            "state_manager": state_manager is not None and await state_manager.health_check(),
        }

        # 检查可选组件状态（未实现的组件不影响整体健康状态）
        optional_components = {
            "collaboration_engine": collaboration_engine is not None and (await collaboration_engine.health_check() if collaboration_engine else False),
            "debate_engine": debate_engine is not None and (await debate_engine.health_check() if debate_engine else False),
            "consensus_algorithm": consensus_algorithm is not None and (await consensus_algorithm.health_check() if consensus_algorithm else False),
            "message_router": message_router is not None and (await message_router.health_check() if message_router else False),
            "workflow_manager": workflow_manager is not None and (await workflow_manager.health_check() if workflow_manager else False),
            "performance_monitor": performance_monitor is not None and (await performance_monitor.health_check() if performance_monitor else False)
        }

        # 合并所有组件状态
        components_status = {**core_components, **optional_components}

        # 只要核心组件健康就认为服务健康
        core_healthy = all(core_components.values())
        all_healthy = core_healthy

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
from .api.workflow_api import router as workflow_router
from .api.monitoring_api import router as monitoring_router

app.include_router(agents_router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(collaboration_router, prefix="/api/v1/collaboration", tags=["collaboration"])
app.include_router(debate_router, prefix="/api/v1/debate", tags=["debate"])
app.include_router(workflow_router, prefix="/api/v1/workflows", tags=["workflows"])
app.include_router(monitoring_router, prefix="/api/v1/monitoring", tags=["monitoring"])


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
        port=config.get('AGENT_SERVICE_PORT', 8008),
        reload=config.get('DEBUG', False),
        log_level=config.get('LOG_LEVEL', 'INFO').lower()
    )
