"""
工作流管理API - 提供工作流调度和监控的REST接口
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..core.workflow_scheduler import WorkflowScheduler, TaskPriority, TaskStatus, WorkflowTask
from ..core.execution_monitor import ExecutionMonitor, Alert, SystemMetrics, PerformanceMetrics

logger = logging.getLogger("tradingagents.analysis-engine.workflow_api")

router = APIRouter(prefix="/api/workflow", tags=["workflow"])

# 依赖注入
def get_workflow_scheduler() -> WorkflowScheduler:
    """获取工作流调度器实例"""
    from ..enhanced_main import workflow_scheduler
    if not workflow_scheduler:
        raise HTTPException(status_code=503, detail="工作流调度器未初始化")
    return workflow_scheduler

def get_execution_monitor() -> ExecutionMonitor:
    """获取执行监控器实例"""
    from ..enhanced_main import execution_monitor
    if not execution_monitor:
        raise HTTPException(status_code=503, detail="执行监控器未初始化")
    return execution_monitor

# 任务管理端点
@router.post("/tasks/submit")
async def submit_task(
    symbol: str,
    task_type: str,
    priority: str = "normal",
    timeout_seconds: int = 300,
    metadata: Optional[Dict[str, Any]] = None,
    scheduler: WorkflowScheduler = Depends(get_workflow_scheduler)
):
    """提交工作流任务"""
    try:
        # 转换优先级
        priority_map = {
            "low": TaskPriority.LOW,
            "normal": TaskPriority.NORMAL,
            "high": TaskPriority.HIGH,
            "urgent": TaskPriority.URGENT
        }
        
        task_priority = priority_map.get(priority.lower(), TaskPriority.NORMAL)
        
        # 提交任务
        task_id = scheduler.submit_task(
            symbol=symbol,
            task_type=task_type,
            priority=task_priority,
            timeout_seconds=timeout_seconds,
            metadata=metadata or {}
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"任务已提交: {task_id}"
        }
        
    except Exception as e:
        logger.error(f"❌ 提交任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"提交任务失败: {str(e)}")

@router.get("/tasks/{task_id}")
async def get_task(
    task_id: str,
    scheduler: WorkflowScheduler = Depends(get_workflow_scheduler)
):
    """获取任务详情"""
    task = scheduler.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return {
        "task_id": task.task_id,
        "symbol": task.symbol,
        "task_type": task.task_type,
        "status": task.status.value,
        "priority": task.priority.value,
        "progress": task.progress,
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "error": task.error,
        "retry_count": task.retry_count,
        "metadata": task.metadata
    }

@router.get("/tasks")
async def list_tasks(
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    scheduler: WorkflowScheduler = Depends(get_workflow_scheduler)
):
    """获取任务列表"""
    try:
        tasks = list(scheduler.tasks.values())
        
        # 过滤条件
        if symbol:
            tasks = [t for t in tasks if t.symbol == symbol]
        
        if status:
            try:
                status_enum = TaskStatus(status.lower())
                tasks = [t for t in tasks if t.status == status_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"无效的状态值: {status}")
        
        # 按创建时间倒序排序
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # 限制数量
        tasks = tasks[:limit]
        
        # 转换为响应格式
        task_list = []
        for task in tasks:
            task_list.append({
                "task_id": task.task_id,
                "symbol": task.symbol,
                "task_type": task.task_type,
                "status": task.status.value,
                "priority": task.priority.value,
                "progress": task.progress,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "error": task.error
            })
        
        return {
            "tasks": task_list,
            "total": len(task_list)
        }
        
    except Exception as e:
        logger.error(f"❌ 获取任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")

@router.delete("/tasks/{task_id}")
async def cancel_task(
    task_id: str,
    scheduler: WorkflowScheduler = Depends(get_workflow_scheduler)
):
    """取消任务"""
    success = scheduler.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在或无法取消")
    
    return {
        "success": True,
        "message": f"任务已取消: {task_id}"
    }

# 监控端点
@router.get("/metrics/scheduler")
async def get_scheduler_metrics(
    scheduler: WorkflowScheduler = Depends(get_workflow_scheduler)
):
    """获取调度器指标"""
    metrics = scheduler.get_metrics()
    
    return {
        "total_tasks": metrics.total_tasks,
        "pending_tasks": metrics.pending_tasks,
        "running_tasks": metrics.running_tasks,
        "completed_tasks": metrics.completed_tasks,
        "failed_tasks": metrics.failed_tasks,
        "average_execution_time": metrics.average_execution_time,
        "success_rate": metrics.success_rate,
        "last_updated": metrics.last_updated.isoformat()
    }

@router.get("/metrics/system")
async def get_system_metrics(
    monitor: ExecutionMonitor = Depends(get_execution_monitor)
):
    """获取系统指标"""
    metrics = monitor.get_latest_system_metrics()
    if not metrics:
        raise HTTPException(status_code=404, detail="系统指标不可用")
    
    return {
        "cpu_usage": metrics.cpu_usage,
        "memory_usage": metrics.memory_usage,
        "disk_usage": metrics.disk_usage,
        "network_io": metrics.network_io,
        "active_connections": metrics.active_connections,
        "timestamp": metrics.timestamp.isoformat()
    }

@router.get("/metrics/performance")
async def get_performance_metrics(
    monitor: ExecutionMonitor = Depends(get_execution_monitor)
):
    """获取性能指标"""
    metrics = monitor.get_latest_performance_metrics()
    if not metrics:
        raise HTTPException(status_code=404, detail="性能指标不可用")
    
    return {
        "avg_response_time": metrics.avg_response_time,
        "throughput": metrics.throughput,
        "error_rate": metrics.error_rate,
        "queue_length": metrics.queue_length,
        "concurrent_tasks": metrics.concurrent_tasks,
        "timestamp": metrics.timestamp.isoformat()
    }

@router.get("/metrics/history")
async def get_metrics_history(
    metric_type: str = Query(..., description="指标类型: system 或 performance"),
    hours: int = Query(1, ge=1, le=24, description="历史时间范围（小时）"),
    monitor: ExecutionMonitor = Depends(get_execution_monitor)
):
    """获取指标历史"""
    try:
        if metric_type == "system":
            history = monitor.get_system_metrics_history(hours)
            return {
                "metric_type": "system",
                "hours": hours,
                "data": [
                    {
                        "cpu_usage": m.cpu_usage,
                        "memory_usage": m.memory_usage,
                        "disk_usage": m.disk_usage,
                        "timestamp": m.timestamp.isoformat()
                    }
                    for m in history
                ]
            }
        elif metric_type == "performance":
            history = monitor.get_performance_metrics_history(hours)
            return {
                "metric_type": "performance",
                "hours": hours,
                "data": [
                    {
                        "avg_response_time": m.avg_response_time,
                        "throughput": m.throughput,
                        "error_rate": m.error_rate,
                        "queue_length": m.queue_length,
                        "timestamp": m.timestamp.isoformat()
                    }
                    for m in history
                ]
            }
        else:
            raise HTTPException(status_code=400, detail="无效的指标类型，支持: system, performance")
            
    except Exception as e:
        logger.error(f"❌ 获取指标历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取指标历史失败: {str(e)}")

@router.get("/alerts")
async def get_alerts(
    active_only: bool = Query(True, description="只返回活跃告警"),
    monitor: ExecutionMonitor = Depends(get_execution_monitor)
):
    """获取告警列表"""
    try:
        if active_only:
            alerts = monitor.get_active_alerts()
        else:
            alerts = list(monitor.alerts.values())
        
        alert_list = []
        for alert in alerts:
            alert_list.append({
                "alert_id": alert.alert_id,
                "level": alert.level.value,
                "title": alert.title,
                "message": alert.message,
                "source": alert.source,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                "metadata": alert.metadata
            })
        
        return {
            "alerts": alert_list,
            "total": len(alert_list)
        }
        
    except Exception as e:
        logger.error(f"❌ 获取告警列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取告警列表失败: {str(e)}")

# 控制端点
@router.post("/scheduler/start")
async def start_scheduler(
    scheduler: WorkflowScheduler = Depends(get_workflow_scheduler)
):
    """启动调度器"""
    try:
        await scheduler.start()
        return {"success": True, "message": "调度器已启动"}
    except Exception as e:
        logger.error(f"❌ 启动调度器失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动调度器失败: {str(e)}")

@router.post("/scheduler/stop")
async def stop_scheduler(
    scheduler: WorkflowScheduler = Depends(get_workflow_scheduler)
):
    """停止调度器"""
    try:
        await scheduler.stop()
        return {"success": True, "message": "调度器已停止"}
    except Exception as e:
        logger.error(f"❌ 停止调度器失败: {e}")
        raise HTTPException(status_code=500, detail=f"停止调度器失败: {str(e)}")

@router.get("/status")
async def get_workflow_status(
    scheduler: WorkflowScheduler = Depends(get_workflow_scheduler),
    monitor: ExecutionMonitor = Depends(get_execution_monitor)
):
    """获取工作流系统状态"""
    try:
        scheduler_metrics = scheduler.get_metrics()
        system_metrics = monitor.get_latest_system_metrics()
        performance_metrics = monitor.get_latest_performance_metrics()
        active_alerts = monitor.get_active_alerts()
        
        return {
            "scheduler_running": scheduler.is_running,
            "monitor_running": monitor.is_monitoring,
            "scheduler_metrics": {
                "total_tasks": scheduler_metrics.total_tasks,
                "pending_tasks": scheduler_metrics.pending_tasks,
                "running_tasks": scheduler_metrics.running_tasks,
                "completed_tasks": scheduler_metrics.completed_tasks,
                "failed_tasks": scheduler_metrics.failed_tasks,
                "success_rate": scheduler_metrics.success_rate
            },
            "system_health": {
                "cpu_usage": system_metrics.cpu_usage if system_metrics else None,
                "memory_usage": system_metrics.memory_usage if system_metrics else None,
                "disk_usage": system_metrics.disk_usage if system_metrics else None
            },
            "performance": {
                "avg_response_time": performance_metrics.avg_response_time if performance_metrics else None,
                "throughput": performance_metrics.throughput if performance_metrics else None,
                "error_rate": performance_metrics.error_rate if performance_metrics else None
            },
            "alerts_count": len(active_alerts),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 获取工作流状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取工作流状态失败: {str(e)}")
