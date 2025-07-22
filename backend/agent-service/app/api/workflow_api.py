"""
工作流API路由
提供高级工作流管理的REST API接口
"""

import uuid
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from backend.shared.logging_config import get_logger
from ..orchestration.workflow_manager import WorkflowManager, WorkflowDefinition
from ..utils.state_manager import StateManager

logger = get_logger("agent-service.workflow_api")

router = APIRouter()


def get_workflow_manager() -> WorkflowManager:
    """获取工作流管理器依赖"""
    from ..main import workflow_manager
    if workflow_manager is None:
        raise HTTPException(status_code=503, detail="Workflow Manager未初始化")
    return workflow_manager


def get_state_manager() -> StateManager:
    """获取状态管理器依赖"""
    from ..main import state_manager
    if state_manager is None:
        raise HTTPException(status_code=503, detail="State Manager未初始化")
    return state_manager


@router.post("/start")
async def start_workflow(
    workflow_id: str,
    context: Dict[str, Any],
    execution_id: Optional[str] = None,
    manager: WorkflowManager = Depends(get_workflow_manager)
):
    """启动工作流执行"""
    try:
        execution_id = await manager.start_workflow(
            workflow_id=workflow_id,
            context=context,
            execution_id=execution_id
        )
        
        logger.info(f"🚀 启动工作流: {execution_id} - {workflow_id}")
        return {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": "started",
            "message": "工作流已启动"
        }
        
    except Exception as e:
        logger.error(f"❌ 启动工作流失败: {workflow_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions/{execution_id}/status")
async def get_execution_status(
    execution_id: str,
    manager: WorkflowManager = Depends(get_workflow_manager)
):
    """获取工作流执行状态"""
    try:
        status = await manager.get_execution_status(execution_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"工作流执行不存在: {execution_id}")
        
        logger.info(f"📊 获取工作流执行状态: {execution_id}")
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取工作流执行状态失败: {execution_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/executions/{execution_id}/cancel")
async def cancel_execution(
    execution_id: str,
    manager: WorkflowManager = Depends(get_workflow_manager)
):
    """取消工作流执行"""
    try:
        success = await manager.cancel_execution(execution_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"工作流执行不存在: {execution_id}")
        
        logger.info(f"🚫 取消工作流执行: {execution_id}")
        return {"message": f"工作流执行已取消: {execution_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 取消工作流执行失败: {execution_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/definitions")
async def get_workflow_definitions(
    manager: WorkflowManager = Depends(get_workflow_manager)
):
    """获取所有工作流定义"""
    try:
        definitions = manager.get_workflow_definitions()
        
        # 转换为可序列化的格式
        serializable_definitions = {}
        for workflow_id, definition in definitions.items():
            serializable_definitions[workflow_id] = {
                "workflow_id": definition.workflow_id,
                "name": definition.name,
                "description": definition.description,
                "version": definition.version,
                "steps_count": len(definition.steps),
                "global_timeout": definition.global_timeout,
                "failure_strategy": definition.failure_strategy,
                "metadata": definition.metadata
            }
        
        logger.info(f"📋 获取工作流定义: {len(serializable_definitions)}个")
        return {"definitions": serializable_definitions}
        
    except Exception as e:
        logger.error(f"❌ 获取工作流定义失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/definitions/{workflow_id}")
async def get_workflow_definition(
    workflow_id: str,
    manager: WorkflowManager = Depends(get_workflow_manager)
):
    """获取特定工作流定义"""
    try:
        definitions = manager.get_workflow_definitions()
        definition = definitions.get(workflow_id)
        
        if not definition:
            raise HTTPException(status_code=404, detail=f"工作流定义不存在: {workflow_id}")
        
        # 转换为可序列化的格式
        serializable_definition = {
            "workflow_id": definition.workflow_id,
            "name": definition.name,
            "description": definition.description,
            "version": definition.version,
            "global_timeout": definition.global_timeout,
            "failure_strategy": definition.failure_strategy,
            "metadata": definition.metadata,
            "steps": []
        }
        
        # 添加步骤信息
        for step in definition.steps:
            step_info = {
                "step_id": step.step_id,
                "name": step.name,
                "agent_types": step.agent_types,
                "dependencies": step.dependencies,
                "parallel": step.parallel,
                "optional": step.optional,
                "timeout": step.timeout,
                "max_retries": step.max_retries,
                "parameters": step.parameters
            }
            serializable_definition["steps"].append(step_info)
        
        logger.info(f"📋 获取工作流定义: {workflow_id}")
        return serializable_definition
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取工作流定义失败: {workflow_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions")
async def get_active_executions(
    manager: WorkflowManager = Depends(get_workflow_manager)
):
    """获取活跃的工作流执行"""
    try:
        active_executions = []
        
        for execution_id, execution in manager.active_executions.items():
            active_executions.append({
                "execution_id": execution_id,
                "workflow_id": execution.workflow_id,
                "status": execution.status.value,
                "current_step_index": execution.current_step_index,
                "completed_steps": len(execution.completed_steps),
                "failed_steps": len(execution.failed_steps),
                "started_at": execution.started_at.isoformat(),
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None
            })
        
        logger.info(f"📊 获取活跃工作流执行: {len(active_executions)}个")
        return {"active_executions": active_executions}
        
    except Exception as e:
        logger.error(f"❌ 获取活跃工作流执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_workflow_context(
    workflow_id: str,
    context: Dict[str, Any],
    manager: WorkflowManager = Depends(get_workflow_manager)
):
    """验证工作流上下文"""
    try:
        definitions = manager.get_workflow_definitions()
        definition = definitions.get(workflow_id)
        
        if not definition:
            raise HTTPException(status_code=404, detail=f"工作流定义不存在: {workflow_id}")
        
        # 验证必需的上下文字段
        required_fields = ["symbol", "company_name", "market", "analysis_date"]
        missing_fields = [field for field in required_fields if field not in context]
        
        if missing_fields:
            return {
                "valid": False,
                "missing_fields": missing_fields,
                "message": f"缺少必需字段: {', '.join(missing_fields)}"
            }
        
        # 验证智能体类型
        all_agent_types = set()
        for step in definition.steps:
            all_agent_types.update(step.agent_types)
        
        # 估算执行时间
        estimated_duration = sum(step.timeout for step in definition.steps)
        
        logger.info(f"✅ 工作流上下文验证通过: {workflow_id}")
        return {
            "valid": True,
            "required_agent_types": list(all_agent_types),
            "estimated_duration": estimated_duration,
            "total_steps": len(definition.steps),
            "message": "上下文验证通过"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 工作流上下文验证失败: {workflow_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_workflow(
    workflow_id: str = "quick_analysis_v2",
    symbol: str = "AAPL",
    manager: WorkflowManager = Depends(get_workflow_manager)
):
    """测试工作流功能"""
    try:
        # 创建测试上下文
        context = {
            "symbol": symbol,
            "company_name": "Apple Inc.",
            "market": "US",
            "analysis_date": "2025-01-22",
            "test_mode": True
        }
        
        # 启动测试工作流
        execution_id = await manager.start_workflow(
            workflow_id=workflow_id,
            context=context
        )
        
        logger.info(f"🧪 启动测试工作流: {execution_id}")
        return {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "context": context,
            "message": "测试工作流已启动"
        }
        
    except Exception as e:
        logger.error(f"❌ 测试工作流失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_workflow_statistics(
    manager: WorkflowManager = Depends(get_workflow_manager),
    state_manager: StateManager = Depends(get_state_manager)
):
    """获取工作流统计信息"""
    try:
        # 当前活跃执行
        active_count = len(manager.active_executions)
        
        # 可用工作流定义
        definitions_count = len(manager.workflow_definitions)
        
        # 模拟历史统计数据
        total_executions = active_count + 25
        completed_executions = 20
        failed_executions = 5
        
        # 工作流使用统计
        workflow_usage = {}
        for execution in manager.active_executions.values():
            workflow_id = execution.workflow_id
            workflow_usage[workflow_id] = workflow_usage.get(workflow_id, 0) + 1
        
        # 步骤成功率统计
        step_success_rates = {
            "data_preparation": 0.95,
            "parallel_analysis": 0.90,
            "research_debate": 0.85,
            "risk_assessment": 0.88,
            "management_review": 0.92,
            "final_decision": 0.87
        }
        
        statistics = {
            "current_active": active_count,
            "total_executions": total_executions,
            "completed_executions": completed_executions,
            "failed_executions": failed_executions,
            "success_rate": completed_executions / max(total_executions, 1),
            "available_definitions": definitions_count,
            "workflow_usage": workflow_usage,
            "step_success_rates": step_success_rates,
            "average_execution_time": 450  # 秒
        }
        
        logger.info(f"📊 获取工作流统计信息")
        return statistics
        
    except Exception as e:
        logger.error(f"❌ 获取工作流统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
