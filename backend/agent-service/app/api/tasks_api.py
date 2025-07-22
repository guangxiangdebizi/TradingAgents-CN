"""
任务API路由
提供任务管理和执行的REST API接口
"""

import uuid
import asyncio
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse

from backend.shared.logging_config import get_logger
from ..agents.agent_manager import AgentManager
from ..agents.base_agent import AgentType, TaskType
from ..models.task_models import (
    TaskRequest, TaskResponse, TaskContext, TaskResult, TaskStatus,
    BatchTaskRequest, BatchTaskResponse, TaskFilter, TaskSearchRequest, 
    TaskSearchResponse, TaskCancellationRequest, TaskRetryRequest
)
from ..utils.state_manager import StateManager

logger = get_logger("agent-service.tasks_api")

router = APIRouter()


def get_agent_manager() -> AgentManager:
    """获取智能体管理器依赖"""
    from ..main import agent_manager
    if agent_manager is None:
        raise HTTPException(status_code=503, detail="Agent Manager未初始化")
    return agent_manager


def get_state_manager() -> StateManager:
    """获取状态管理器依赖"""
    from ..main import state_manager
    if state_manager is None:
        raise HTTPException(status_code=503, detail="State Manager未初始化")
    return state_manager


@router.post("/", response_model=TaskResponse)
async def create_task(
    request: TaskRequest,
    background_tasks: BackgroundTasks,
    manager: AgentManager = Depends(get_agent_manager),
    state_manager: StateManager = Depends(get_state_manager)
):
    """创建并执行任务"""
    try:
        task_id = str(uuid.uuid4())
        
        # 创建任务响应
        task_response = TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            progress=0.0,
            current_step="初始化",
            results=[],
            final_result=None
        )
        
        # 保存任务状态
        await state_manager.save_task_state(task_id, task_response.dict())
        
        # 根据任务类型执行不同的处理逻辑
        if request.task_type == "single_analysis":
            background_tasks.add_task(
                _execute_single_analysis, 
                task_id, request, manager, state_manager
            )
        elif request.task_type == "comprehensive_analysis":
            background_tasks.add_task(
                _execute_comprehensive_analysis, 
                task_id, request, manager, state_manager
            )
        elif request.task_type == "debate_analysis":
            background_tasks.add_task(
                _execute_debate_analysis, 
                task_id, request, manager, state_manager
            )
        else:
            raise HTTPException(status_code=400, detail=f"不支持的任务类型: {request.task_type}")
        
        logger.info(f"📋 创建任务: {task_id} - {request.task_type}")
        return task_response
        
    except Exception as e:
        logger.error(f"❌ 创建任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    state_manager: StateManager = Depends(get_state_manager)
):
    """获取任务状态"""
    try:
        task_state = await state_manager.get_task_state(task_id)
        if not task_state:
            raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
        
        # 转换为TaskResponse模型
        task_response = TaskResponse(**task_state)
        
        logger.info(f"📋 获取任务状态: {task_id} - {task_response.status}")
        return task_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取任务状态失败: {task_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchTaskResponse)
async def create_batch_tasks(
    request: BatchTaskRequest,
    background_tasks: BackgroundTasks,
    manager: AgentManager = Depends(get_agent_manager),
    state_manager: StateManager = Depends(get_state_manager)
):
    """创建批量任务"""
    try:
        batch_response = BatchTaskResponse(
            batch_id=request.batch_id,
            total_tasks=len(request.tasks),
            completed_tasks=0,
            failed_tasks=0,
            progress=0.0,
            status="running",
            task_results=[]
        )
        
        # 保存批次状态
        await state_manager.save_task_state(f"batch_{request.batch_id}", batch_response.dict())
        
        # 启动批量任务执行
        background_tasks.add_task(
            _execute_batch_tasks,
            request, manager, state_manager
        )
        
        logger.info(f"📋 创建批量任务: {request.batch_id} - {len(request.tasks)}个任务")
        return batch_response
        
    except Exception as e:
        logger.error(f"❌ 创建批量任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch/{batch_id}", response_model=BatchTaskResponse)
async def get_batch_tasks(
    batch_id: str,
    state_manager: StateManager = Depends(get_state_manager)
):
    """获取批量任务状态"""
    try:
        batch_state = await state_manager.get_task_state(f"batch_{batch_id}")
        if not batch_state:
            raise HTTPException(status_code=404, detail=f"批量任务不存在: {batch_id}")
        
        batch_response = BatchTaskResponse(**batch_state)
        
        logger.info(f"📋 获取批量任务状态: {batch_id}")
        return batch_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取批量任务状态失败: {batch_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=TaskSearchResponse)
async def search_tasks(
    request: TaskSearchRequest,
    state_manager: StateManager = Depends(get_state_manager)
):
    """搜索任务"""
    try:
        # 构建过滤条件
        filters = {}
        if request.filters.status:
            filters["status"] = {"$in": [s.value for s in request.filters.status]}
        if request.filters.symbols:
            filters["symbol"] = {"$in": request.filters.symbols}
        if request.filters.markets:
            filters["market"] = {"$in": request.filters.markets}
        
        # 从状态管理器搜索
        tasks = await state_manager.get_states_by_filter("task", filters)
        
        # 分页处理
        total_count = len(tasks)
        start_index = request.filters.offset
        end_index = start_index + request.filters.limit
        paginated_tasks = tasks[start_index:end_index]
        
        # 转换为TaskResponse
        task_responses = []
        for task_data in paginated_tasks:
            try:
                task_response = TaskResponse(**task_data)
                task_responses.append(task_response)
            except Exception as e:
                logger.warning(f"⚠️ 跳过无效任务数据: {e}")
        
        response = TaskSearchResponse(
            total_count=total_count,
            tasks=task_responses,
            has_more=end_index < total_count,
            next_offset=end_index if end_index < total_count else None
        )
        
        logger.info(f"🔍 搜索任务: 找到{total_count}个结果，返回{len(task_responses)}个")
        return response
        
    except Exception as e:
        logger.error(f"❌ 搜索任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    request: TaskCancellationRequest,
    state_manager: StateManager = Depends(get_state_manager)
):
    """取消任务"""
    try:
        task_state = await state_manager.get_task_state(task_id)
        if not task_state:
            raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
        
        # 更新任务状态为取消
        task_state["status"] = TaskStatus.CANCELLED.value
        task_state["error"] = request.reason or "用户取消"
        
        await state_manager.save_task_state(task_id, task_state)
        
        logger.info(f"🚫 取消任务: {task_id} - {request.reason}")
        return {"message": f"任务已取消: {task_id}", "reason": request.reason}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 取消任务失败: {task_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/retry")
async def retry_task(
    task_id: str,
    request: TaskRetryRequest,
    background_tasks: BackgroundTasks,
    manager: AgentManager = Depends(get_agent_manager),
    state_manager: StateManager = Depends(get_state_manager)
):
    """重试任务"""
    try:
        task_state = await state_manager.get_task_state(task_id)
        if not task_state:
            raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
        
        # 重置任务状态
        task_state["status"] = TaskStatus.PENDING.value
        task_state["progress"] = 0.0
        task_state["error"] = None
        task_state["results"] = []
        
        # 更新参数（如果提供）
        if request.parameters:
            task_state.setdefault("parameters", {}).update(request.parameters)
        
        await state_manager.save_task_state(task_id, task_state)
        
        # 重新执行任务
        # 这里需要根据原始任务类型重新执行
        # 简化实现，实际应该保存原始请求信息
        
        logger.info(f"🔄 重试任务: {task_id}")
        return {"message": f"任务重试已启动: {task_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 重试任务失败: {task_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _execute_single_analysis(
    task_id: str,
    request: TaskRequest,
    manager: AgentManager,
    state_manager: StateManager
):
    """执行单一分析任务"""
    try:
        # 更新任务状态
        await _update_task_status(task_id, TaskStatus.RUNNING, 0.1, "开始分析", state_manager)
        
        # 确定分析类型和智能体
        analysis_type = request.analysis_types[0] if request.analysis_types else "fundamentals_analysis"
        agent_type = _get_agent_type_for_analysis(analysis_type)
        
        # 创建任务上下文
        context = TaskContext(
            task_id=task_id,
            symbol=request.symbol,
            company_name=request.company_name,
            market=request.market,
            analysis_date=request.analysis_date,
            parameters=request.parameters,
            metadata=request.metadata
        )
        
        # 执行分析
        await _update_task_status(task_id, TaskStatus.RUNNING, 0.5, f"执行{analysis_type}", state_manager)
        
        result = await manager.execute_task(agent_type, analysis_type, context)
        
        # 更新最终结果
        await _update_task_status(
            task_id, TaskStatus.COMPLETED, 1.0, "分析完成", 
            state_manager, [result], result.result
        )
        
    except Exception as e:
        logger.error(f"❌ 单一分析任务失败: {task_id} - {e}")
        await _update_task_status(
            task_id, TaskStatus.FAILED, 0.0, "分析失败", 
            state_manager, error=str(e)
        )


async def _execute_comprehensive_analysis(
    task_id: str,
    request: TaskRequest,
    manager: AgentManager,
    state_manager: StateManager
):
    """执行综合分析任务"""
    try:
        # 更新任务状态
        await _update_task_status(task_id, TaskStatus.RUNNING, 0.1, "开始综合分析", state_manager)
        
        # 定义分析步骤
        analysis_steps = request.analysis_types or [
            "fundamentals_analysis", "technical_analysis", "news_analysis"
        ]
        
        results = []
        total_steps = len(analysis_steps)
        
        # 逐步执行分析
        for i, analysis_type in enumerate(analysis_steps):
            progress = 0.1 + (i / total_steps) * 0.8
            await _update_task_status(
                task_id, TaskStatus.RUNNING, progress, 
                f"执行{analysis_type} ({i+1}/{total_steps})", state_manager
            )
            
            agent_type = _get_agent_type_for_analysis(analysis_type)
            context = TaskContext(
                task_id=f"{task_id}_{i}",
                symbol=request.symbol,
                company_name=request.company_name,
                market=request.market,
                analysis_date=request.analysis_date,
                parameters=request.parameters,
                metadata=request.metadata
            )
            
            result = await manager.execute_task(agent_type, analysis_type, context)
            results.append(result)
        
        # 聚合结果
        await _update_task_status(task_id, TaskStatus.RUNNING, 0.95, "聚合分析结果", state_manager)
        
        final_result = await _aggregate_analysis_results(results)
        
        # 完成任务
        await _update_task_status(
            task_id, TaskStatus.COMPLETED, 1.0, "综合分析完成",
            state_manager, results, final_result
        )
        
    except Exception as e:
        logger.error(f"❌ 综合分析任务失败: {task_id} - {e}")
        await _update_task_status(
            task_id, TaskStatus.FAILED, 0.0, "综合分析失败",
            state_manager, error=str(e)
        )


async def _execute_debate_analysis(
    task_id: str,
    request: TaskRequest,
    manager: AgentManager,
    state_manager: StateManager
):
    """执行辩论分析任务"""
    try:
        # 更新任务状态
        await _update_task_status(task_id, TaskStatus.RUNNING, 0.1, "开始辩论分析", state_manager)
        
        # 获取辩论引擎
        from ..main import debate_engine
        if not debate_engine:
            raise Exception("辩论引擎未初始化")
        
        # 启动辩论
        participants = ["bull_researcher", "bear_researcher", "neutral_debator"]
        context = {
            "symbol": request.symbol,
            "company_name": request.company_name,
            "market": request.market,
            "analysis_date": request.analysis_date
        }
        
        await _update_task_status(task_id, TaskStatus.RUNNING, 0.3, "启动辩论", state_manager)
        
        debate_id = await debate_engine.start_debate(
            topic=f"{request.symbol} 投资决策辩论",
            participants=participants,
            context=context
        )
        
        # 等待辩论完成
        await _update_task_status(task_id, TaskStatus.RUNNING, 0.8, "等待辩论完成", state_manager)
        
        # 简化实现：等待一段时间后获取结果
        await asyncio.sleep(5)
        
        debate_result = await debate_engine.get_debate_status(debate_id)
        
        # 完成任务
        await _update_task_status(
            task_id, TaskStatus.COMPLETED, 1.0, "辩论分析完成",
            state_manager, [], debate_result
        )
        
    except Exception as e:
        logger.error(f"❌ 辩论分析任务失败: {task_id} - {e}")
        await _update_task_status(
            task_id, TaskStatus.FAILED, 0.0, "辩论分析失败",
            state_manager, error=str(e)
        )


async def _execute_batch_tasks(
    request: BatchTaskRequest,
    manager: AgentManager,
    state_manager: StateManager
):
    """执行批量任务"""
    try:
        batch_id = request.batch_id
        tasks = request.tasks
        
        if request.execution_mode == "parallel":
            # 并行执行
            semaphore = asyncio.Semaphore(request.max_concurrent)
            task_coroutines = []
            
            for task_request in tasks:
                async def execute_single_task(req):
                    async with semaphore:
                        task_id = str(uuid.uuid4())
                        await _execute_single_analysis(task_id, req, manager, state_manager)
                        return task_id
                
                task_coroutines.append(execute_single_task(task_request))
            
            # 等待所有任务完成
            await asyncio.gather(*task_coroutines, return_exceptions=True)
        else:
            # 顺序执行
            for task_request in tasks:
                task_id = str(uuid.uuid4())
                await _execute_single_analysis(task_id, task_request, manager, state_manager)
        
        # 更新批次状态
        batch_state = await state_manager.get_task_state(f"batch_{batch_id}")
        if batch_state:
            batch_state["status"] = "completed"
            batch_state["completed_tasks"] = len(tasks)
            batch_state["progress"] = 1.0
            await state_manager.save_task_state(f"batch_{batch_id}", batch_state)
        
    except Exception as e:
        logger.error(f"❌ 批量任务执行失败: {request.batch_id} - {e}")


def _get_agent_type_for_analysis(analysis_type: str) -> AgentType:
    """根据分析类型获取智能体类型"""
    mapping = {
        "fundamentals_analysis": AgentType.FUNDAMENTALS_ANALYST,
        "technical_analysis": AgentType.MARKET_ANALYST,
        "news_analysis": AgentType.NEWS_ANALYST,
        "sentiment_analysis": AgentType.SOCIAL_MEDIA_ANALYST,
        "bull_research": AgentType.BULL_RESEARCHER,
        "bear_research": AgentType.BEAR_RESEARCHER,
        "risk_assessment": AgentType.RISK_MANAGER
    }
    return mapping.get(analysis_type, AgentType.FUNDAMENTALS_ANALYST)


async def _update_task_status(
    task_id: str,
    status: TaskStatus,
    progress: float,
    current_step: str,
    state_manager: StateManager,
    results: Optional[List[TaskResult]] = None,
    final_result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
):
    """更新任务状态"""
    try:
        task_state = await state_manager.get_task_state(task_id)
        if not task_state:
            task_state = {
                "task_id": task_id,
                "status": status.value,
                "progress": progress,
                "current_step": current_step,
                "results": [],
                "final_result": None,
                "error": None
            }
        
        task_state.update({
            "status": status.value,
            "progress": progress,
            "current_step": current_step
        })
        
        if results:
            task_state["results"] = [r.dict() for r in results]
        
        if final_result:
            task_state["final_result"] = final_result
        
        if error:
            task_state["error"] = error
        
        await state_manager.save_task_state(task_id, task_state)
        
    except Exception as e:
        logger.error(f"❌ 更新任务状态失败: {task_id} - {e}")


async def _aggregate_analysis_results(results: List[TaskResult]) -> Dict[str, Any]:
    """聚合分析结果"""
    try:
        # 简化的结果聚合
        aggregated = {
            "summary": "综合分析结果",
            "total_analyses": len(results),
            "successful_analyses": len([r for r in results if r.status == "success"]),
            "recommendations": [],
            "confidence_scores": [],
            "key_insights": []
        }
        
        for result in results:
            if result.status == "success" and result.result:
                # 提取推荐
                if "recommendation" in result.result:
                    aggregated["recommendations"].append(result.result["recommendation"])
                
                # 提取置信度
                if "confidence_score" in result.result:
                    aggregated["confidence_scores"].append(result.result["confidence_score"])
                
                # 提取关键洞察
                if "key_insights" in result.result:
                    aggregated["key_insights"].extend(result.result["key_insights"])
        
        # 计算平均置信度
        if aggregated["confidence_scores"]:
            aggregated["average_confidence"] = sum(aggregated["confidence_scores"]) / len(aggregated["confidence_scores"])
        else:
            aggregated["average_confidence"] = 0.0
        
        return aggregated
        
    except Exception as e:
        logger.error(f"❌ 聚合分析结果失败: {e}")
        return {"error": str(e)}
