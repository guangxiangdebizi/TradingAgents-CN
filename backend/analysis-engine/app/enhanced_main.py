"""
Enhanced Analysis Engine - 增强版分析引擎服务
支持高并发、负载均衡和智能任务调度
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# 导入并发管理模块
from .concurrency.concurrency_manager import get_concurrency_manager, TaskPriority, ConcurrencyManager
from .concurrency.load_balancer import get_load_balancer, LoadBalancer, LoadBalanceStrategy

# 导入工作流管理模块
from .core.workflow_scheduler import WorkflowScheduler, TaskPriority as WorkflowTaskPriority
from .core.execution_monitor import ExecutionMonitor

# 导入分析模块
from .analysis.graph_analyzer import GraphAnalyzer
from .models.requests import AnalysisRequest, AnalysisParameters
from .models.responses import APIResponse, AnalysisStatus
from .config.settings import ANALYSIS_ENGINE_CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局变量
graph_analyzer: Optional[GraphAnalyzer] = None
concurrency_manager: Optional[ConcurrencyManager] = None
load_balancer: Optional[LoadBalancer] = None
workflow_scheduler: Optional[WorkflowScheduler] = None
execution_monitor: Optional[ExecutionMonitor] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global graph_analyzer, concurrency_manager, load_balancer, workflow_scheduler, execution_monitor
    
    # 启动时初始化
    logger.info("🚀 Enhanced Analysis Engine 启动中...")
    
    try:
        # 初始化并发管理器
        max_concurrent = ANALYSIS_ENGINE_CONFIG.get("max_concurrent_analyses", 10)
        max_queue_size = ANALYSIS_ENGINE_CONFIG.get("max_queue_size", 100)
        
        concurrency_manager = get_concurrency_manager(max_concurrent, max_queue_size)
        logger.info(f"✅ 并发管理器初始化完成: 最大并发{max_concurrent}")
        
        # 初始化负载均衡器
        load_balancer = get_load_balancer(LoadBalanceStrategy.HEALTH_AWARE)
        await load_balancer.initialize()
        
        # 添加本地实例到负载均衡器
        local_host = ANALYSIS_ENGINE_CONFIG.get("host", "localhost")
        local_port = ANALYSIS_ENGINE_CONFIG.get("port", 8005)
        load_balancer.add_instance("local", local_host, local_port, weight=1)
        
        logger.info("✅ 负载均衡器初始化完成")
        
        # 初始化图分析器
        memory_service_url = ANALYSIS_ENGINE_CONFIG.get("memory_service_url", "http://localhost:8006")
        graph_analyzer = GraphAnalyzer(memory_service_url)
        await graph_analyzer.initialize()
        
        # 设置任务处理器
        concurrency_manager.set_task_processor(process_analysis_task)

        logger.info("✅ 图分析器初始化完成")

        # 初始化工作流调度器
        max_concurrent_workflows = ANALYSIS_ENGINE_CONFIG.get("max_concurrent_workflows", 3)
        workflow_scheduler = WorkflowScheduler(max_concurrent_workflows)

        # 注册任务执行器
        workflow_scheduler.register_executor("analysis", execute_analysis_workflow)
        workflow_scheduler.register_executor("debate", execute_debate_workflow)
        workflow_scheduler.register_executor("risk_assessment", execute_risk_assessment_workflow)

        await workflow_scheduler.start()
        logger.info("✅ 工作流调度器初始化完成")

        # 初始化执行监控器
        execution_monitor = ExecutionMonitor(workflow_scheduler)
        await execution_monitor.start()
        logger.info("✅ 执行监控器初始化完成")
        
        logger.info("🎉 Enhanced Analysis Engine 启动完成")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        raise
    finally:
        # 关闭时清理
        logger.info("🔄 Enhanced Analysis Engine 关闭中...")
        
        if concurrency_manager:
            await concurrency_manager.shutdown()
        
        if load_balancer:
            await load_balancer.cleanup()
        
        if graph_analyzer:
            await graph_analyzer.cleanup()

        if execution_monitor:
            await execution_monitor.stop()

        if workflow_scheduler:
            await workflow_scheduler.stop()

        logger.info("✅ Enhanced Analysis Engine 已关闭")

# 创建FastAPI应用
app = FastAPI(
    title="Enhanced Analysis Engine",
    description="增强版股票分析引擎 - 支持高并发和负载均衡",
    version="2.0.0",
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

# 导入并注册API路由
from .api.workflow_api import router as workflow_router
app.include_router(workflow_router)

# 依赖注入
async def get_concurrency_mgr() -> ConcurrencyManager:
    """获取并发管理器"""
    if not concurrency_manager:
        raise HTTPException(status_code=503, detail="并发管理器未初始化")
    return concurrency_manager

async def get_load_bal() -> LoadBalancer:
    """获取负载均衡器"""
    if not load_balancer:
        raise HTTPException(status_code=503, detail="负载均衡器未初始化")
    return load_balancer

# 任务处理器
async def process_analysis_task(stock_code: str, analysis_type: str, 
                               metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """处理分析任务"""
    if not graph_analyzer:
        raise Exception("图分析器未初始化")
    
    logger.info(f"🔍 开始分析: {stock_code} ({analysis_type})")
    
    # 执行分析
    result = await graph_analyzer.analyze_stock(
        symbol=stock_code,
        analysis_type=analysis_type
    )
    
    logger.info(f"✅ 分析完成: {stock_code}")
    return result

# API路由

@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查各组件状态
        components = {
            "concurrency_manager": concurrency_manager is not None,
            "load_balancer": load_balancer is not None,
            "graph_analyzer": graph_analyzer is not None and graph_analyzer.initialized
        }
        
        # 获取系统统计
        stats = {}
        if concurrency_manager:
            stats["concurrency"] = concurrency_manager.get_statistics()
        
        if load_balancer:
            stats["load_balancer"] = load_balancer.get_instance_stats()
        
        return {
            "status": "healthy" if all(components.values()) else "unhealthy",
            "service": "enhanced-analysis-engine",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "components": components,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/v1/analysis/submit", response_model=APIResponse)
async def submit_analysis(
    request: AnalysisRequest,
    priority: str = "normal",
    mgr: ConcurrencyManager = Depends(get_concurrency_mgr)
):
    """提交分析任务（高并发版本）"""
    try:
        # 解析优先级
        priority_map = {
            "low": TaskPriority.LOW,
            "normal": TaskPriority.NORMAL,
            "high": TaskPriority.HIGH,
            "urgent": TaskPriority.URGENT
        }
        task_priority = priority_map.get(priority.lower(), TaskPriority.NORMAL)
        
        # 提交任务到并发管理器
        task_id = await mgr.submit_task(
            stock_code=request.stock_code,
            analysis_type=request.analysis_type,
            priority=task_priority,
            metadata={
                "user_id": getattr(request, "user_id", None),
                "request_time": datetime.now().isoformat(),
                "parameters": request.parameters.dict() if request.parameters else {}
            }
        )
        
        logger.info(f"📋 分析任务已提交: {task_id} - {request.stock_code} (优先级: {priority})")
        
        return APIResponse(
            success=True,
            message="分析任务已提交到队列",
            data={
                "task_id": task_id,
                "stock_code": request.stock_code,
                "analysis_type": request.analysis_type,
                "priority": priority,
                "estimated_wait_time": await _estimate_wait_time(mgr)
            }
        )
        
    except Exception as e:
        logger.error(f"❌ 提交分析任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"提交任务失败: {str(e)}")

@app.get("/api/v1/analysis/status/{task_id}")
async def get_task_status(
    task_id: str,
    mgr: ConcurrencyManager = Depends(get_concurrency_mgr)
):
    """获取任务状态"""
    try:
        task = await mgr.get_task_status(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 计算执行时间
        execution_time = None
        if task.started_at and task.completed_at:
            execution_time = (task.completed_at - task.started_at).total_seconds()
        elif task.started_at:
            execution_time = (datetime.now() - task.started_at).total_seconds()
        
        return {
            "task_id": task.task_id,
            "stock_code": task.stock_code,
            "analysis_type": task.analysis_type,
            "status": task.status.value,
            "priority": task.priority.name,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "execution_time": execution_time,
            "retry_count": task.retry_count,
            "result": task.result,
            "error": task.error
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取任务状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")

@app.delete("/api/v1/analysis/cancel/{task_id}")
async def cancel_task(
    task_id: str,
    mgr: ConcurrencyManager = Depends(get_concurrency_mgr)
):
    """取消任务"""
    try:
        success = await mgr.cancel_task(task_id)
        
        if success:
            return {"message": f"任务 {task_id} 已取消"}
        else:
            raise HTTPException(status_code=400, detail="任务无法取消（可能已在执行中）")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 取消任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")

@app.get("/api/v1/system/stats")
async def get_system_stats(
    mgr: ConcurrencyManager = Depends(get_concurrency_mgr),
    lb: LoadBalancer = Depends(get_load_bal)
):
    """获取系统统计信息"""
    try:
        return {
            "concurrency": mgr.get_statistics(),
            "queue": mgr.get_queue_status(),
            "load_balancer": lb.get_instance_stats(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 获取系统统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")

@app.post("/api/v1/admin/cleanup")
async def cleanup_completed_tasks(
    max_age_hours: int = 24,
    mgr: ConcurrencyManager = Depends(get_concurrency_mgr)
):
    """清理完成的任务"""
    try:
        await mgr.cleanup_completed_tasks(max_age_hours)
        return {"message": f"已清理超过{max_age_hours}小时的完成任务"}
        
    except Exception as e:
        logger.error(f"❌ 清理任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"清理失败: {str(e)}")

@app.post("/api/v1/admin/load_balancer/add_instance")
async def add_instance(
    instance_id: str,
    host: str,
    port: int,
    weight: int = 1,
    lb: LoadBalancer = Depends(get_load_bal)
):
    """添加Analysis Engine实例"""
    try:
        lb.add_instance(instance_id, host, port, weight)
        return {"message": f"实例 {instance_id} 已添加"}
        
    except Exception as e:
        logger.error(f"❌ 添加实例失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加实例失败: {str(e)}")

@app.delete("/api/v1/admin/load_balancer/remove_instance/{instance_id}")
async def remove_instance(
    instance_id: str,
    lb: LoadBalancer = Depends(get_load_bal)
):
    """移除Analysis Engine实例"""
    try:
        lb.remove_instance(instance_id)
        return {"message": f"实例 {instance_id} 已移除"}
        
    except Exception as e:
        logger.error(f"❌ 移除实例失败: {e}")
        raise HTTPException(status_code=500, detail=f"移除实例失败: {str(e)}")

# 辅助函数
async def _estimate_wait_time(mgr: ConcurrencyManager) -> float:
    """估算等待时间"""
    stats = mgr.get_statistics()
    queue_size = stats["current_queued"]
    avg_execution_time = stats["average_execution_time"]
    concurrent_tasks = stats["current_running"]
    max_concurrent = mgr.max_concurrent_tasks
    
    if queue_size == 0:
        return 0.0
    
    # 简单估算：队列任务数 / 可用并发数 * 平均执行时间
    available_slots = max(1, max_concurrent - concurrent_tasks)
    estimated_time = (queue_size / available_slots) * max(avg_execution_time, 30)
    
    return estimated_time

# 工作流执行器函数
async def execute_analysis_workflow(task):
    """执行分析工作流"""
    try:
        logger.info(f"🔍 执行分析工作流: {task.symbol}")

        # 使用图分析器执行完整分析
        if graph_analyzer:
            result = await graph_analyzer.analyze_stock(
                symbol=task.symbol,
                analysis_date=datetime.now().strftime("%Y-%m-%d"),
                **task.metadata
            )
            return result
        else:
            raise Exception("图分析器未初始化")

    except Exception as e:
        logger.error(f"❌ 分析工作流执行失败: {e}")
        raise

async def execute_debate_workflow(task):
    """执行辩论工作流"""
    try:
        logger.info(f"🎭 执行辩论工作流: {task.symbol}")

        # 这里可以实现专门的辩论流程
        # 目前使用图分析器的辩论功能
        if graph_analyzer:
            result = await graph_analyzer.analyze_stock(
                symbol=task.symbol,
                analysis_date=datetime.now().strftime("%Y-%m-%d"),
                focus="debate",
                **task.metadata
            )
            return result
        else:
            raise Exception("图分析器未初始化")

    except Exception as e:
        logger.error(f"❌ 辩论工作流执行失败: {e}")
        raise

async def execute_risk_assessment_workflow(task):
    """执行风险评估工作流"""
    try:
        logger.info(f"⚠️ 执行风险评估工作流: {task.symbol}")

        # 这里可以实现专门的风险评估流程
        if graph_analyzer:
            result = await graph_analyzer.analyze_stock(
                symbol=task.symbol,
                analysis_date=datetime.now().strftime("%Y-%m-%d"),
                focus="risk_assessment",
                **task.metadata
            )
            return result
        else:
            raise Exception("图分析器未初始化")

    except Exception as e:
        logger.error(f"❌ 风险评估工作流执行失败: {e}")
        raise

if __name__ == "__main__":
    # 获取配置
    host = ANALYSIS_ENGINE_CONFIG.get("host", "0.0.0.0")
    port = ANALYSIS_ENGINE_CONFIG.get("port", 8005)
    debug = ANALYSIS_ENGINE_CONFIG.get("debug", False)
    
    logger.info(f"🚀 启动Enhanced Analysis Engine: {host}:{port}")
    
    uvicorn.run(
        "enhanced_main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
