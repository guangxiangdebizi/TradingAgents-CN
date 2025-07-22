"""
智能体API路由
提供智能体管理和执行的REST API接口
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from backend.shared.logging_config import get_logger
from ..agents.agent_manager import AgentManager
from ..agents.base_agent import AgentType, TaskType
from ..models.agent_models import (
    AgentRequest, AgentResponse, AgentInfoModel, AgentRegistrationRequest, 
    AgentRegistrationResponse, SystemStatusModel, HealthCheckResponse
)
from ..models.task_models import TaskContext, TaskResult

logger = get_logger("agent-service.agents_api")

router = APIRouter()


def get_agent_manager() -> AgentManager:
    """获取智能体管理器依赖"""
    from ..main import agent_manager
    if agent_manager is None:
        raise HTTPException(status_code=503, detail="Agent Manager未初始化")
    return agent_manager


@router.get("/", response_model=List[AgentInfoModel])
async def list_agents(
    agent_type: Optional[str] = None,
    status: Optional[str] = None,
    manager: AgentManager = Depends(get_agent_manager)
):
    """获取智能体列表"""
    try:
        agents = []
        
        if agent_type:
            # 按类型过滤
            try:
                agent_type_enum = AgentType(agent_type)
                type_agents = await manager.get_agents_by_type(agent_type_enum)
                agents.extend(type_agents)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"无效的智能体类型: {agent_type}")
        else:
            # 获取所有智能体
            agents = list(manager.agents.values())
        
        # 按状态过滤
        if status:
            agents = [agent for agent in agents if agent.status.value == status]
        
        # 转换为响应模型
        agent_infos = []
        for agent in agents:
            agent_info = AgentInfoModel(
                agent_id=agent.agent_id,
                agent_type=agent.agent_type,
                status=agent.status,
                capabilities=[cap.__dict__ for cap in agent.capabilities],
                metrics=agent.metrics.__dict__,
                current_tasks=len(agent.current_tasks),
                created_at=agent.created_at,
                last_heartbeat=agent.last_heartbeat
            )
            agent_infos.append(agent_info)
        
        logger.info(f"📋 获取智能体列表: {len(agent_infos)}个智能体")
        return agent_infos
        
    except Exception as e:
        logger.error(f"❌ 获取智能体列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}", response_model=AgentInfoModel)
async def get_agent(
    agent_id: str,
    manager: AgentManager = Depends(get_agent_manager)
):
    """获取特定智能体信息"""
    try:
        agent = await manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"智能体不存在: {agent_id}")
        
        agent_info = AgentInfoModel(
            agent_id=agent.agent_id,
            agent_type=agent.agent_type,
            status=agent.status,
            capabilities=[cap.__dict__ for cap in agent.capabilities],
            metrics=agent.metrics.__dict__,
            current_tasks=len(agent.current_tasks),
            created_at=agent.created_at,
            last_heartbeat=agent.last_heartbeat
        )
        
        logger.info(f"📋 获取智能体信息: {agent_id}")
        return agent_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取智能体信息失败: {agent_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register", response_model=AgentRegistrationResponse)
async def register_agent(
    request: AgentRegistrationRequest,
    manager: AgentManager = Depends(get_agent_manager)
):
    """注册新智能体"""
    try:
        # 创建智能体实例
        agent_class = manager.agent_classes.get(request.agent_type)
        if not agent_class:
            raise HTTPException(status_code=400, detail=f"不支持的智能体类型: {request.agent_type}")
        
        agent = agent_class(
            agent_type=request.agent_type,
            config=request.config
        )
        
        # 注册智能体
        success = await manager.register_agent(agent)
        if not success:
            raise HTTPException(status_code=500, detail="智能体注册失败")
        
        response = AgentRegistrationResponse(
            agent_id=agent.agent_id,
            agent_type=request.agent_type,
            status="success",
            message=f"智能体注册成功: {agent.agent_id}"
        )
        
        logger.info(f"✅ 智能体注册成功: {agent.agent_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 智能体注册失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{agent_id}")
async def unregister_agent(
    agent_id: str,
    manager: AgentManager = Depends(get_agent_manager)
):
    """注销智能体"""
    try:
        success = await manager.unregister_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"智能体不存在: {agent_id}")
        
        logger.info(f"✅ 智能体注销成功: {agent_id}")
        return {"message": f"智能体注销成功: {agent_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 智能体注销失败: {agent_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute", response_model=AgentResponse)
async def execute_task(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    manager: AgentManager = Depends(get_agent_manager)
):
    """执行智能体任务"""
    try:
        # 创建任务上下文
        context = TaskContext(
            task_id=f"task_{request.symbol}_{request.analysis_date}_{hash(str(request.parameters))}",
            symbol=request.symbol,
            company_name=request.company_name,
            market=request.market,
            analysis_date=request.analysis_date,
            parameters=request.parameters,
            metadata=request.metadata
        )
        
        # 执行任务
        result = await manager.execute_task(
            agent_type=request.agent_type,
            task_type=request.task_type,
            context=context
        )
        
        # 转换为响应模型
        response = AgentResponse(
            task_id=result.task_id,
            agent_id=result.agent_id,
            agent_type=result.agent_type,
            status=result.status,
            result=result.result,
            error=result.error,
            duration=result.duration,
            timestamp=result.timestamp
        )
        
        logger.info(f"✅ 任务执行完成: {context.task_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ 任务执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/status")
async def get_agent_status(
    agent_id: str,
    manager: AgentManager = Depends(get_agent_manager)
):
    """获取智能体状态"""
    try:
        agent = await manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"智能体不存在: {agent_id}")
        
        status = agent.get_status()
        logger.info(f"📊 获取智能体状态: {agent_id}")
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取智能体状态失败: {agent_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/health-check")
async def agent_health_check(
    agent_id: str,
    manager: AgentManager = Depends(get_agent_manager)
):
    """智能体健康检查"""
    try:
        agent = await manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"智能体不存在: {agent_id}")
        
        is_healthy = await agent.health_check()
        
        response = HealthCheckResponse(
            status="healthy" if is_healthy else "unhealthy",
            components={"agent": is_healthy},
            details={
                "agent_id": agent_id,
                "agent_type": agent.agent_type.value,
                "current_status": agent.status.value,
                "current_tasks": len(agent.current_tasks),
                "last_activity": agent.metrics.last_activity.isoformat() if agent.metrics.last_activity else None
            }
        )
        
        logger.info(f"🏥 智能体健康检查: {agent_id} - {'健康' if is_healthy else '不健康'}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 智能体健康检查失败: {agent_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/status", response_model=SystemStatusModel)
async def get_system_status(
    manager: AgentManager = Depends(get_agent_manager)
):
    """获取系统状态"""
    try:
        status = await manager.get_system_status()
        
        system_status = SystemStatusModel(
            total_agents=status["total_agents"],
            active_agents=status["active_agents"],
            busy_agents=status["busy_agents"],
            error_agents=status["error_agents"],
            idle_agents=status["idle_agents"],
            type_statistics=status["type_statistics"]
        )
        
        logger.info(f"📊 获取系统状态: {status['total_agents']}个智能体")
        return system_status
        
    except Exception as e:
        logger.error(f"❌ 获取系统状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def get_agent_types():
    """获取支持的智能体类型"""
    try:
        agent_types = []
        for agent_type in AgentType:
            agent_types.append({
                "type": agent_type.value,
                "name": agent_type.name,
                "description": f"{agent_type.value}智能体"
            })
        
        logger.info(f"📋 获取智能体类型: {len(agent_types)}种类型")
        return {"agent_types": agent_types}
        
    except Exception as e:
        logger.error(f"❌ 获取智能体类型失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task-types")
async def get_task_types():
    """获取支持的任务类型"""
    try:
        task_types = []
        for task_type in TaskType:
            task_types.append({
                "type": task_type.value,
                "name": task_type.name,
                "description": f"{task_type.value}任务"
            })
        
        logger.info(f"📋 获取任务类型: {len(task_types)}种类型")
        return {"task_types": task_types}
        
    except Exception as e:
        logger.error(f"❌ 获取任务类型失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
