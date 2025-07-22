"""
协作API路由
提供智能体协作和工作流管理的REST API接口
"""

import uuid
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from backend.shared.logging_config import get_logger
from ..orchestration.collaboration_engine import CollaborationEngine
from ..models.agent_models import CollaborationRequest, CollaborationResponse
from ..utils.state_manager import StateManager

logger = get_logger("agent-service.collaboration_api")

router = APIRouter()


def get_collaboration_engine() -> CollaborationEngine:
    """获取协作引擎依赖"""
    from ..main import collaboration_engine
    if collaboration_engine is None:
        raise HTTPException(status_code=503, detail="Collaboration Engine未初始化")
    return collaboration_engine


def get_state_manager() -> StateManager:
    """获取状态管理器依赖"""
    from ..main import state_manager
    if state_manager is None:
        raise HTTPException(status_code=503, detail="State Manager未初始化")
    return state_manager


@router.post("/start", response_model=CollaborationResponse)
async def start_collaboration(
    request: CollaborationRequest,
    background_tasks: BackgroundTasks,
    engine: CollaborationEngine = Depends(get_collaboration_engine)
):
    """启动智能体协作"""
    try:
        # 启动协作
        collaboration_id = await engine.start_collaboration(
            workflow_type=request.workflow_type,
            context=request.context,
            participants=request.participants
        )
        
        # 创建响应
        response = CollaborationResponse(
            collaboration_id=collaboration_id,
            workflow_type=request.workflow_type,
            status="running",
            steps=[],
            final_result={}
        )
        
        logger.info(f"🤝 启动协作: {collaboration_id} - {request.workflow_type}")
        return response
        
    except Exception as e:
        logger.error(f"❌ 启动协作失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{collaboration_id}/status")
async def get_collaboration_status(
    collaboration_id: str,
    engine: CollaborationEngine = Depends(get_collaboration_engine)
):
    """获取协作状态"""
    try:
        status = await engine.get_collaboration_status(collaboration_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"协作不存在: {collaboration_id}")
        
        logger.info(f"📊 获取协作状态: {collaboration_id}")
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取协作状态失败: {collaboration_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{collaboration_id}/cancel")
async def cancel_collaboration(
    collaboration_id: str,
    engine: CollaborationEngine = Depends(get_collaboration_engine)
):
    """取消协作"""
    try:
        success = await engine.cancel_collaboration(collaboration_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"协作不存在: {collaboration_id}")
        
        logger.info(f"🚫 取消协作: {collaboration_id}")
        return {"message": f"协作已取消: {collaboration_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 取消协作失败: {collaboration_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows")
async def get_available_workflows(
    engine: CollaborationEngine = Depends(get_collaboration_engine)
):
    """获取可用的工作流"""
    try:
        workflows = []
        for workflow_id, workflow_def in engine.workflow_definitions.items():
            workflows.append({
                "workflow_id": workflow_id,
                "name": workflow_def["name"],
                "mode": workflow_def["mode"].value,
                "steps": len(workflow_def["steps"]),
                "description": f"包含{len(workflow_def['steps'])}个步骤的{workflow_def['name']}"
            })
        
        logger.info(f"📋 获取可用工作流: {len(workflows)}个")
        return {"workflows": workflows}
        
    except Exception as e:
        logger.error(f"❌ 获取可用工作流失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}")
async def get_workflow_definition(
    workflow_id: str,
    engine: CollaborationEngine = Depends(get_collaboration_engine)
):
    """获取工作流定义"""
    try:
        workflow_def = engine.workflow_definitions.get(workflow_id)
        if not workflow_def:
            raise HTTPException(status_code=404, detail=f"工作流不存在: {workflow_id}")
        
        # 转换为可序列化的格式
        serializable_def = {
            "workflow_id": workflow_id,
            "name": workflow_def["name"],
            "mode": workflow_def["mode"].value,
            "steps": workflow_def["steps"]
        }
        
        logger.info(f"📋 获取工作流定义: {workflow_id}")
        return serializable_def
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取工作流定义失败: {workflow_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active")
async def get_active_collaborations(
    engine: CollaborationEngine = Depends(get_collaboration_engine)
):
    """获取活跃的协作"""
    try:
        active_collaborations = []
        
        for collaboration_id, collaboration in engine.active_collaborations.items():
            active_collaborations.append({
                "collaboration_id": collaboration_id,
                "workflow_type": collaboration["workflow_type"],
                "status": collaboration["status"],
                "current_step": collaboration["current_step"],
                "started_at": collaboration["started_at"].isoformat(),
                "participants": collaboration.get("participants", [])
            })
        
        logger.info(f"📊 获取活跃协作: {len(active_collaborations)}个")
        return {"active_collaborations": active_collaborations}
        
    except Exception as e:
        logger.error(f"❌ 获取活跃协作失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/validate")
async def validate_workflow_context(
    workflow_id: str,
    context: Dict[str, Any],
    engine: CollaborationEngine = Depends(get_collaboration_engine)
):
    """验证工作流上下文"""
    try:
        workflow_def = engine.workflow_definitions.get(workflow_id)
        if not workflow_def:
            raise HTTPException(status_code=404, detail=f"工作流不存在: {workflow_id}")
        
        # 验证必需的上下文字段
        required_fields = ["symbol", "company_name", "market", "analysis_date"]
        missing_fields = [field for field in required_fields if field not in context]
        
        if missing_fields:
            return {
                "valid": False,
                "missing_fields": missing_fields,
                "message": f"缺少必需字段: {', '.join(missing_fields)}"
            }
        
        # 验证智能体可用性
        all_agents = []
        for step in workflow_def["steps"]:
            all_agents.extend(step["agents"])
        
        # 这里可以添加更多验证逻辑
        
        logger.info(f"✅ 工作流上下文验证通过: {workflow_id}")
        return {
            "valid": True,
            "required_agents": list(set(all_agents)),
            "estimated_duration": len(workflow_def["steps"]) * 60,  # 估算时间
            "message": "上下文验证通过"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 工作流上下文验证失败: {workflow_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_collaboration_statistics(
    engine: CollaborationEngine = Depends(get_collaboration_engine),
    state_manager: StateManager = Depends(get_state_manager)
):
    """获取协作统计信息"""
    try:
        # 当前活跃协作
        active_count = len(engine.active_collaborations)
        
        # 从状态管理器获取历史统计
        # 这里简化实现，实际应该从数据库查询
        total_collaborations = active_count + 10  # 模拟数据
        completed_collaborations = 8
        failed_collaborations = 2
        
        # 工作流使用统计
        workflow_usage = {}
        for collaboration in engine.active_collaborations.values():
            workflow_type = collaboration["workflow_type"]
            workflow_usage[workflow_type] = workflow_usage.get(workflow_type, 0) + 1
        
        statistics = {
            "current_active": active_count,
            "total_collaborations": total_collaborations,
            "completed_collaborations": completed_collaborations,
            "failed_collaborations": failed_collaborations,
            "success_rate": completed_collaborations / max(total_collaborations, 1),
            "workflow_usage": workflow_usage,
            "available_workflows": len(engine.workflow_definitions)
        }
        
        logger.info(f"📊 获取协作统计信息")
        return statistics
        
    except Exception as e:
        logger.error(f"❌ 获取协作统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_collaboration(
    workflow_type: str = "quick_analysis",
    symbol: str = "AAPL",
    engine: CollaborationEngine = Depends(get_collaboration_engine)
):
    """测试协作功能"""
    try:
        # 创建测试上下文
        context = {
            "symbol": symbol,
            "company_name": "Apple Inc.",
            "market": "US",
            "analysis_date": "2025-01-22",
            "test_mode": True
        }
        
        # 启动测试协作
        collaboration_id = await engine.start_collaboration(
            workflow_type=workflow_type,
            context=context
        )
        
        logger.info(f"🧪 启动测试协作: {collaboration_id}")
        return {
            "collaboration_id": collaboration_id,
            "workflow_type": workflow_type,
            "context": context,
            "message": "测试协作已启动"
        }
        
    except Exception as e:
        logger.error(f"❌ 测试协作失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
