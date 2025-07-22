"""
监控API路由
提供性能监控和系统状态的REST API接口
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from backend.shared.logging_config import get_logger
from ..utils.performance_monitor import PerformanceMonitor

logger = get_logger("agent-service.monitoring_api")

router = APIRouter()


def get_performance_monitor() -> PerformanceMonitor:
    """获取性能监控器依赖"""
    from ..main import performance_monitor
    if performance_monitor is None:
        raise HTTPException(status_code=503, detail="Performance Monitor未初始化")
    return performance_monitor


@router.get("/system/metrics")
async def get_system_metrics(
    monitor: PerformanceMonitor = Depends(get_performance_monitor)
):
    """获取系统性能指标"""
    try:
        metrics = await monitor.get_system_metrics()
        
        # 转换为可序列化的格式
        metrics_dict = {
            "timestamp": metrics.timestamp.isoformat(),
            "cpu_usage": metrics.cpu_usage,
            "memory_usage": metrics.memory_usage,
            "memory_total": metrics.memory_total,
            "disk_io": {
                "read_mb": metrics.disk_io_read,
                "write_mb": metrics.disk_io_write
            },
            "network_io": {
                "sent_mb": metrics.network_io_sent,
                "recv_mb": metrics.network_io_recv
            },
            "tasks": {
                "active": metrics.active_tasks,
                "completed": metrics.completed_tasks,
                "failed": metrics.failed_tasks
            },
            "average_response_time": metrics.average_response_time
        }
        
        logger.info("📊 获取系统性能指标")
        return metrics_dict
        
    except Exception as e:
        logger.error(f"❌ 获取系统性能指标失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/metrics")
async def get_agents_metrics(
    agent_id: Optional[str] = Query(None, description="特定智能体ID"),
    monitor: PerformanceMonitor = Depends(get_performance_monitor)
):
    """获取智能体性能指标"""
    try:
        metrics = await monitor.get_agent_metrics(agent_id)
        
        logger.info(f"📊 获取智能体性能指标: {agent_id or 'all'}")
        return {"agent_metrics": metrics}
        
    except Exception as e:
        logger.error(f"❌ 获取智能体性能指标失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_performance_summary(
    monitor: PerformanceMonitor = Depends(get_performance_monitor)
):
    """获取性能摘要"""
    try:
        summary = await monitor.get_performance_summary()
        
        logger.info("📊 获取性能摘要")
        return summary
        
    except Exception as e:
        logger.error(f"❌ 获取性能摘要失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts(
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    alert_type: Optional[str] = Query(None, description="告警类型过滤"),
    monitor: PerformanceMonitor = Depends(get_performance_monitor)
):
    """获取性能告警"""
    try:
        # 获取告警历史
        all_alerts = list(monitor.alerts_history)
        
        # 按类型过滤
        if alert_type:
            all_alerts = [alert for alert in all_alerts if alert.get("type") == alert_type]
        
        # 按时间倒序排列并限制数量
        all_alerts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        limited_alerts = all_alerts[:limit]
        
        logger.info(f"📊 获取性能告警: {len(limited_alerts)}条")
        return {
            "alerts": limited_alerts,
            "total_count": len(all_alerts),
            "returned_count": len(limited_alerts)
        }
        
    except Exception as e:
        logger.error(f"❌ 获取性能告警失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/thresholds")
async def get_performance_thresholds(
    monitor: PerformanceMonitor = Depends(get_performance_monitor)
):
    """获取性能阈值配置"""
    try:
        thresholds = monitor.thresholds.copy()
        
        logger.info("📊 获取性能阈值配置")
        return {"thresholds": thresholds}
        
    except Exception as e:
        logger.error(f"❌ 获取性能阈值配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/thresholds")
async def update_performance_thresholds(
    thresholds: Dict[str, float],
    monitor: PerformanceMonitor = Depends(get_performance_monitor)
):
    """更新性能阈值配置"""
    try:
        # 验证阈值键
        valid_keys = set(monitor.thresholds.keys())
        invalid_keys = set(thresholds.keys()) - valid_keys
        
        if invalid_keys:
            raise HTTPException(
                status_code=400, 
                detail=f"无效的阈值键: {list(invalid_keys)}"
            )
        
        # 更新阈值
        monitor.thresholds.update(thresholds)
        
        logger.info(f"📊 更新性能阈值配置: {list(thresholds.keys())}")
        return {
            "message": "性能阈值配置已更新",
            "updated_thresholds": thresholds,
            "current_thresholds": monitor.thresholds
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 更新性能阈值配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/system")
async def get_system_metrics_history(
    hours: int = Query(1, ge=1, le=24, description="历史数据小时数"),
    monitor: PerformanceMonitor = Depends(get_performance_monitor)
):
    """获取系统指标历史"""
    try:
        # 获取历史数据
        history = list(monitor.system_metrics_history)
        
        # 按时间过滤
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_history = [
            {
                "timestamp": metrics.timestamp.isoformat(),
                "cpu_usage": metrics.cpu_usage,
                "memory_usage": metrics.memory_usage,
                "average_response_time": metrics.average_response_time,
                "active_tasks": metrics.active_tasks
            }
            for metrics in history
            if metrics.timestamp >= cutoff_time
        ]
        
        logger.info(f"📊 获取系统指标历史: {len(filtered_history)}条记录")
        return {
            "history": filtered_history,
            "hours": hours,
            "total_records": len(filtered_history)
        }
        
    except Exception as e:
        logger.error(f"❌ 获取系统指标历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}/performance")
async def get_agent_performance_detail(
    agent_id: str,
    monitor: PerformanceMonitor = Depends(get_performance_monitor)
):
    """获取智能体详细性能信息"""
    try:
        metrics = await monitor.get_agent_metrics(agent_id)
        
        if not metrics:
            raise HTTPException(status_code=404, detail=f"智能体不存在: {agent_id}")
        
        # 获取智能体的响应时间历史
        agent_metrics_obj = monitor.agent_metrics.get(agent_id)
        response_time_history = list(agent_metrics_obj.response_times) if agent_metrics_obj else []
        
        detailed_metrics = {
            **metrics,
            "response_time_history": response_time_history,
            "performance_trend": _calculate_performance_trend(response_time_history),
            "health_status": _assess_agent_health(metrics)
        }
        
        logger.info(f"📊 获取智能体详细性能: {agent_id}")
        return detailed_metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取智能体详细性能失败: {agent_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_monitoring_dashboard(
    monitor: PerformanceMonitor = Depends(get_performance_monitor)
):
    """获取监控仪表盘数据"""
    try:
        # 获取各种监控数据
        system_metrics = await monitor.get_system_metrics()
        performance_summary = await monitor.get_performance_summary()
        recent_alerts = list(monitor.alerts_history)[-5:]
        
        # 智能体状态统计
        agent_status_stats = _calculate_agent_status_stats(monitor.agent_metrics)
        
        # 任务趋势数据
        task_trends = _calculate_task_trends(monitor.task_stats)
        
        dashboard_data = {
            "system_overview": {
                "cpu_usage": system_metrics.cpu_usage,
                "memory_usage": system_metrics.memory_usage,
                "active_tasks": system_metrics.active_tasks,
                "average_response_time": system_metrics.average_response_time
            },
            "performance_grade": performance_summary.get("performance_grade", "Unknown"),
            "agent_statistics": performance_summary.get("agent_statistics", {}),
            "task_statistics": performance_summary.get("task_statistics", {}),
            "recent_alerts": recent_alerts,
            "agent_status_stats": agent_status_stats,
            "task_trends": task_trends,
            "timestamp": system_metrics.timestamp.isoformat()
        }
        
        logger.info("📊 获取监控仪表盘数据")
        return dashboard_data
        
    except Exception as e:
        logger.error(f"❌ 获取监控仪表盘数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/load")
async def simulate_load_test(
    duration_seconds: int = Query(60, ge=10, le=300, description="测试持续时间"),
    concurrent_tasks: int = Query(5, ge=1, le=20, description="并发任务数"),
    monitor: PerformanceMonitor = Depends(get_performance_monitor)
):
    """模拟负载测试"""
    try:
        import asyncio
        import random
        
        async def simulate_task(task_id: int):
            """模拟任务执行"""
            agent_id = f"test_agent_{random.randint(1, 3)}"
            agent_type = "test_analyst"
            
            # 记录任务开始
            await monitor.record_task_start(agent_id, agent_type, f"load_test_{task_id}")
            
            # 模拟任务执行时间
            execution_time = random.uniform(1, 10)
            await asyncio.sleep(execution_time)
            
            # 模拟成功/失败
            success = random.random() > 0.1  # 90%成功率
            
            # 记录任务完成
            await monitor.record_task_completion(
                agent_id, f"load_test_{task_id}", success, execution_time
            )
            
            return {"task_id": task_id, "success": success, "duration": execution_time}
        
        # 启动负载测试
        start_time = asyncio.get_event_loop().time()
        task_counter = 0
        results = []
        
        while (asyncio.get_event_loop().time() - start_time) < duration_seconds:
            # 创建并发任务
            tasks = []
            for i in range(concurrent_tasks):
                task = asyncio.create_task(simulate_task(task_counter + i))
                tasks.append(task)
            
            # 等待任务完成
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend([r for r in batch_results if not isinstance(r, Exception)])
            
            task_counter += concurrent_tasks
            
            # 短暂休息
            await asyncio.sleep(1)
        
        # 统计结果
        successful_tasks = len([r for r in results if r.get("success")])
        failed_tasks = len(results) - successful_tasks
        avg_duration = sum(r.get("duration", 0) for r in results) / len(results) if results else 0
        
        test_summary = {
            "duration_seconds": duration_seconds,
            "concurrent_tasks": concurrent_tasks,
            "total_tasks": len(results),
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": successful_tasks / len(results) if results else 0,
            "average_duration": avg_duration,
            "tasks_per_second": len(results) / duration_seconds if duration_seconds > 0 else 0
        }
        
        logger.info(f"🧪 负载测试完成: {len(results)}个任务")
        return test_summary
        
    except Exception as e:
        logger.error(f"❌ 负载测试失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _calculate_performance_trend(response_times: List[float]) -> str:
    """计算性能趋势"""
    if len(response_times) < 10:
        return "insufficient_data"
    
    # 比较前半部分和后半部分的平均值
    mid_point = len(response_times) // 2
    first_half_avg = sum(response_times[:mid_point]) / mid_point
    second_half_avg = sum(response_times[mid_point:]) / (len(response_times) - mid_point)
    
    if second_half_avg > first_half_avg * 1.1:
        return "degrading"
    elif second_half_avg < first_half_avg * 0.9:
        return "improving"
    else:
        return "stable"


def _assess_agent_health(metrics: Dict[str, Any]) -> str:
    """评估智能体健康状态"""
    success_rate = metrics.get("success_rate", 0)
    error_rate = metrics.get("error_rate", 0)
    response_time = metrics.get("current_response_time", 0)
    
    if success_rate > 0.95 and error_rate < 0.05 and response_time < 10:
        return "excellent"
    elif success_rate > 0.9 and error_rate < 0.1 and response_time < 20:
        return "good"
    elif success_rate > 0.8 and error_rate < 0.2 and response_time < 30:
        return "fair"
    else:
        return "poor"


def _calculate_agent_status_stats(agent_metrics: Dict[str, Any]) -> Dict[str, int]:
    """计算智能体状态统计"""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    active_threshold = timedelta(minutes=5)
    
    stats = {
        "total": len(agent_metrics),
        "active": 0,
        "idle": 0,
        "error": 0
    }
    
    for metrics in agent_metrics.values():
        if metrics.last_activity:
            time_since_activity = now - metrics.last_activity
            if time_since_activity <= active_threshold:
                stats["active"] += 1
            else:
                stats["idle"] += 1
        else:
            stats["idle"] += 1
        
        if metrics.error_rate > 0.1:
            stats["error"] += 1
    
    return stats


def _calculate_task_trends(task_stats: Dict[str, int]) -> Dict[str, Any]:
    """计算任务趋势"""
    total = task_stats.get("total", 0)
    successful = task_stats.get("successful", 0)
    failed = task_stats.get("failed", 0)
    
    return {
        "total_tasks": total,
        "success_rate": successful / total if total > 0 else 0,
        "failure_rate": failed / total if total > 0 else 0,
        "trend": "stable"  # 简化实现
    }
