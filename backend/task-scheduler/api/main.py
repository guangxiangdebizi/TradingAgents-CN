"""
任务管理 API 服务
提供定时任务的管理和监控接口
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from tasks.celery_app import celery_app
from tasks import data_tasks, analysis_tasks, maintenance_tasks, report_tasks

# 创建FastAPI应用
app = FastAPI(
    title="TradingAgents Task Scheduler API",
    description="定时任务管理和监控API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "task-scheduler",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/tasks/status")
async def get_task_status():
    """获取任务系统状态"""
    try:
        # 获取Celery状态
        inspect = celery_app.control.inspect()
        
        # 获取活跃任务
        active_tasks = inspect.active()
        
        # 获取已注册任务
        registered_tasks = inspect.registered()
        
        # 获取队列状态
        stats = inspect.stats()
        
        return {
            "success": True,
            "data": {
                "active_tasks": active_tasks,
                "registered_tasks": registered_tasks,
                "worker_stats": stats,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")


@app.get("/api/tasks/scheduled")
async def get_scheduled_tasks():
    """获取定时任务列表"""
    try:
        # 获取定时任务配置
        beat_schedule = celery_app.conf.beat_schedule
        
        scheduled_tasks = []
        for task_name, config in beat_schedule.items():
            scheduled_tasks.append({
                "name": task_name,
                "task": config["task"],
                "schedule": str(config["schedule"]),
                "options": config.get("options", {}),
                "enabled": True  # 这里可以从数据库获取实际状态
            })
        
        return {
            "success": True,
            "data": {
                "scheduled_tasks": scheduled_tasks,
                "total_count": len(scheduled_tasks)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取定时任务失败: {str(e)}")


@app.post("/api/tasks/run")
async def run_task_manually(task_request: Dict[str, Any]):
    """手动执行任务"""
    try:
        task_name = task_request.get("task_name")
        task_args = task_request.get("args", [])
        task_kwargs = task_request.get("kwargs", {})
        
        if not task_name:
            raise HTTPException(status_code=400, detail="任务名称不能为空")
        
        # 执行任务
        result = celery_app.send_task(
            task_name,
            args=task_args,
            kwargs=task_kwargs
        )
        
        return {
            "success": True,
            "data": {
                "task_id": result.id,
                "task_name": task_name,
                "status": "submitted",
                "submitted_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行任务失败: {str(e)}")


@app.get("/api/tasks/{task_id}/result")
async def get_task_result(task_id: str):
    """获取任务执行结果"""
    try:
        result = celery_app.AsyncResult(task_id)
        
        return {
            "success": True,
            "data": {
                "task_id": task_id,
                "status": result.status,
                "result": result.result,
                "traceback": result.traceback,
                "date_done": result.date_done.isoformat() if result.date_done else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务结果失败: {str(e)}")


@app.post("/api/tasks/data/sync-daily")
async def sync_daily_data(request: Dict[str, Any]):
    """手动同步每日数据"""
    try:
        symbols = request.get("symbols")
        date = request.get("date")
        
        result = data_tasks.sync_daily_stock_data.delay(symbols, date)
        
        return {
            "success": True,
            "data": {
                "task_id": result.id,
                "message": "每日数据同步任务已提交"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交同步任务失败: {str(e)}")


@app.post("/api/tasks/analysis/batch")
async def batch_analysis(request: Dict[str, Any]):
    """批量股票分析"""
    try:
        symbols = request.get("symbols", [])
        analysis_config = request.get("config", {})
        
        if not symbols:
            raise HTTPException(status_code=400, detail="股票代码列表不能为空")
        
        result = analysis_tasks.batch_stock_analysis.delay(symbols, analysis_config)
        
        return {
            "success": True,
            "data": {
                "task_id": result.id,
                "message": f"批量分析任务已提交，共{len(symbols)}只股票"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交批量分析任务失败: {str(e)}")


@app.post("/api/tasks/reports/daily")
async def generate_daily_report(request: Dict[str, Any]):
    """生成每日报告"""
    try:
        date = request.get("date")
        
        result = report_tasks.generate_daily_market_report.delay(date)
        
        return {
            "success": True,
            "data": {
                "task_id": result.id,
                "message": "每日报告生成任务已提交"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交报告生成任务失败: {str(e)}")


@app.post("/api/tasks/maintenance/cleanup")
async def cleanup_data(request: Dict[str, Any]):
    """数据清理"""
    try:
        days_to_keep = request.get("days_to_keep", 90)
        
        result = maintenance_tasks.cleanup_old_data.delay(days_to_keep)
        
        return {
            "success": True,
            "data": {
                "task_id": result.id,
                "message": f"数据清理任务已提交，保留{days_to_keep}天数据"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交数据清理任务失败: {str(e)}")


@app.get("/api/tasks/history")
async def get_task_history(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None
):
    """获取任务执行历史"""
    try:
        # 这里需要从数据库或Redis获取任务历史
        # 暂时返回模拟数据
        
        task_history = [
            {
                "task_id": "abc123",
                "task_name": "sync_daily_stock_data",
                "status": "SUCCESS",
                "started_at": "2025-01-20T16:30:00Z",
                "completed_at": "2025-01-20T16:35:00Z",
                "duration": 300,
                "result": {"success_count": 100, "error_count": 0}
            },
            {
                "task_id": "def456",
                "task_name": "calculate_technical_indicators",
                "status": "SUCCESS",
                "started_at": "2025-01-20T17:00:00Z",
                "completed_at": "2025-01-20T17:10:00Z",
                "duration": 600,
                "result": {"success_count": 95, "error_count": 5}
            }
        ]
        
        # 根据状态过滤
        if status:
            task_history = [t for t in task_history if t["status"] == status]
        
        # 分页
        total = len(task_history)
        task_history = task_history[offset:offset + limit]
        
        return {
            "success": True,
            "data": {
                "tasks": task_history,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务历史失败: {str(e)}")


@app.get("/api/tasks/metrics")
async def get_task_metrics():
    """获取任务执行指标"""
    try:
        # 获取任务执行统计
        metrics = {
            "today": {
                "total_tasks": 45,
                "successful_tasks": 42,
                "failed_tasks": 3,
                "success_rate": 93.3
            },
            "this_week": {
                "total_tasks": 315,
                "successful_tasks": 298,
                "failed_tasks": 17,
                "success_rate": 94.6
            },
            "task_types": {
                "data_sync": {"count": 150, "success_rate": 96.0},
                "analysis": {"count": 80, "success_rate": 92.5},
                "maintenance": {"count": 60, "success_rate": 98.3},
                "reports": {"count": 25, "success_rate": 88.0}
            },
            "avg_execution_time": {
                "data_sync": 180,  # 秒
                "analysis": 450,
                "maintenance": 120,
                "reports": 300
            }
        }
        
        return {
            "success": True,
            "data": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务指标失败: {str(e)}")


# ===== 新增数据任务管理接口 =====

@app.post("/api/tasks/data/update-hot-stocks")
async def trigger_hot_stocks_update():
    """手动触发热门股票数据更新"""
    try:
        result = data_tasks.update_hot_stocks_data.delay()

        return {
            "success": True,
            "data": {
                "task_id": result.id,
                "message": "热门股票数据更新任务已提交"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动热门股票数据更新失败: {str(e)}")

@app.post("/api/tasks/data/update-news")
async def trigger_news_update():
    """手动触发新闻数据更新"""
    try:
        result = data_tasks.update_news_data.delay()

        return {
            "success": True,
            "data": {
                "task_id": result.id,
                "message": "新闻数据更新任务已提交"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动新闻数据更新失败: {str(e)}")

@app.post("/api/tasks/data/preheat-cache")
async def trigger_cache_preheat():
    """手动触发缓存预热"""
    try:
        result = data_tasks.preheat_cache.delay()

        return {
            "success": True,
            "data": {
                "task_id": result.id,
                "message": "缓存预热任务已提交"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动缓存预热失败: {str(e)}")

@app.post("/api/tasks/data/cleanup-cache")
async def trigger_cache_cleanup():
    """手动触发缓存清理"""
    try:
        result = data_tasks.cleanup_expired_data.delay()

        return {
            "success": True,
            "data": {
                "task_id": result.id,
                "message": "缓存清理任务已提交"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动缓存清理失败: {str(e)}")

@app.post("/api/tasks/data/custom-update")
async def trigger_custom_update(request: Dict[str, Any]):
    """手动触发自定义数据更新"""
    try:
        symbols = request.get("symbols", [])
        data_types = request.get("data_types", [])
        start_date = request.get("start_date")
        end_date = request.get("end_date")

        if not symbols:
            raise HTTPException(status_code=400, detail="股票代码列表不能为空")
        if not data_types:
            raise HTTPException(status_code=400, detail="数据类型列表不能为空")

        result = data_tasks.update_custom_stocks_data.delay(
            symbols=symbols,
            data_types=data_types,
            start_date=start_date,
            end_date=end_date
        )

        return {
            "success": True,
            "data": {
                "task_id": result.id,
                "message": f"自定义数据更新任务已提交: {len(symbols)} 只股票",
                "symbols_count": len(symbols),
                "data_types": data_types
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动自定义数据更新失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
