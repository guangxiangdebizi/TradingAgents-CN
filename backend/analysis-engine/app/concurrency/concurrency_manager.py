"""
并发管理器
管理分析任务的并发执行、队列调度和资源控制
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import uuid
from dataclasses import dataclass, field
from collections import defaultdict
import time

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AnalysisTask:
    """分析任务"""
    task_id: str
    stock_code: str
    analysis_type: str
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 300  # 5分钟超时
    metadata: Dict[str, Any] = field(default_factory=dict)

class ConcurrencyManager:
    """并发管理器"""
    
    def __init__(self, max_concurrent_tasks: int = 10, max_queue_size: int = 100):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.max_queue_size = max_queue_size
        
        # 并发控制
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.running_tasks: Dict[str, AnalysisTask] = {}
        self.task_queue: List[AnalysisTask] = []
        self.completed_tasks: Dict[str, AnalysisTask] = {}
        
        # 统计信息
        self.stats = {
            "total_submitted": 0,
            "total_completed": 0,
            "total_failed": 0,
            "total_cancelled": 0,
            "current_running": 0,
            "current_queued": 0,
            "average_execution_time": 0.0,
            "peak_concurrent_tasks": 0
        }
        
        # 性能监控
        self.execution_times: List[float] = []
        self.start_time = datetime.now()
        
        # 任务处理器
        self.task_processor: Optional[Callable] = None
        
        logger.info(f"🔄 并发管理器初始化: 最大并发{max_concurrent_tasks}, 队列大小{max_queue_size}")
    
    def set_task_processor(self, processor: Callable):
        """设置任务处理器"""
        self.task_processor = processor
        logger.info("✅ 任务处理器已设置")
    
    async def submit_task(self, stock_code: str, analysis_type: str, 
                         priority: TaskPriority = TaskPriority.NORMAL,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """提交分析任务"""
        
        # 检查队列是否已满
        if len(self.task_queue) >= self.max_queue_size:
            raise Exception(f"任务队列已满 (最大{self.max_queue_size})")
        
        # 创建任务
        task_id = str(uuid.uuid4())
        task = AnalysisTask(
            task_id=task_id,
            stock_code=stock_code,
            analysis_type=analysis_type,
            priority=priority,
            metadata=metadata or {}
        )
        
        # 添加到队列
        self._add_to_queue(task)
        
        # 更新统计
        self.stats["total_submitted"] += 1
        self.stats["current_queued"] = len(self.task_queue)
        
        logger.info(f"📋 任务已提交: {task_id} - {stock_code} ({analysis_type})")
        
        # 尝试立即处理
        asyncio.create_task(self._process_queue())
        
        return task_id
    
    def _add_to_queue(self, task: AnalysisTask):
        """添加任务到队列（按优先级排序）"""
        self.task_queue.append(task)
        
        # 按优先级排序（优先级高的在前）
        self.task_queue.sort(key=lambda t: t.priority.value, reverse=True)
    
    async def _process_queue(self):
        """处理任务队列"""
        while self.task_queue and len(self.running_tasks) < self.max_concurrent_tasks:
            # 获取下一个任务
            task = self.task_queue.pop(0)
            
            # 启动任务
            asyncio.create_task(self._execute_task(task))
            
            # 更新统计
            self.stats["current_queued"] = len(self.task_queue)
    
    async def _execute_task(self, task: AnalysisTask):
        """执行单个任务"""
        async with self.semaphore:
            try:
                # 更新任务状态
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()
                self.running_tasks[task.task_id] = task
                
                # 更新统计
                self.stats["current_running"] = len(self.running_tasks)
                self.stats["peak_concurrent_tasks"] = max(
                    self.stats["peak_concurrent_tasks"],
                    len(self.running_tasks)
                )
                
                logger.info(f"🚀 开始执行任务: {task.task_id} - {task.stock_code}")
                
                # 执行任务（带超时）
                result = await asyncio.wait_for(
                    self._run_analysis_task(task),
                    timeout=task.timeout
                )
                
                # 任务完成
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.result = result
                
                # 记录执行时间
                execution_time = (task.completed_at - task.started_at).total_seconds()
                self.execution_times.append(execution_time)
                
                # 更新统计
                self.stats["total_completed"] += 1
                self._update_average_execution_time()
                
                logger.info(f"✅ 任务完成: {task.task_id} - 耗时{execution_time:.1f}s")
                
            except asyncio.TimeoutError:
                # 任务超时
                task.status = TaskStatus.FAILED
                task.error = f"任务超时 ({task.timeout}s)"
                task.completed_at = datetime.now()
                
                self.stats["total_failed"] += 1
                logger.error(f"⏰ 任务超时: {task.task_id}")
                
            except Exception as e:
                # 任务失败
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.completed_at = datetime.now()
                
                # 检查是否需要重试
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.status = TaskStatus.PENDING
                    task.started_at = None
                    task.completed_at = None
                    task.error = None
                    
                    # 重新加入队列
                    self._add_to_queue(task)
                    logger.warning(f"🔄 任务重试: {task.task_id} (第{task.retry_count}次)")
                else:
                    self.stats["total_failed"] += 1
                    logger.error(f"❌ 任务失败: {task.task_id} - {e}")
                
            finally:
                # 清理运行中的任务
                if task.task_id in self.running_tasks:
                    del self.running_tasks[task.task_id]
                
                # 移动到完成列表
                self.completed_tasks[task.task_id] = task
                
                # 更新统计
                self.stats["current_running"] = len(self.running_tasks)
                
                # 继续处理队列
                asyncio.create_task(self._process_queue())
    
    async def _run_analysis_task(self, task: AnalysisTask) -> Dict[str, Any]:
        """运行分析任务"""
        if not self.task_processor:
            raise Exception("任务处理器未设置")
        
        # 调用实际的分析处理器
        return await self.task_processor(
            stock_code=task.stock_code,
            analysis_type=task.analysis_type,
            metadata=task.metadata
        )
    
    def _update_average_execution_time(self):
        """更新平均执行时间"""
        if self.execution_times:
            self.stats["average_execution_time"] = sum(self.execution_times) / len(self.execution_times)
    
    async def get_task_status(self, task_id: str) -> Optional[AnalysisTask]:
        """获取任务状态"""
        # 检查运行中的任务
        if task_id in self.running_tasks:
            return self.running_tasks[task_id]
        
        # 检查完成的任务
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
        
        # 检查队列中的任务
        for task in self.task_queue:
            if task.task_id == task_id:
                return task
        
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        # 从队列中移除
        for i, task in enumerate(self.task_queue):
            if task.task_id == task_id:
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.now()
                self.task_queue.pop(i)
                self.completed_tasks[task_id] = task
                self.stats["total_cancelled"] += 1
                self.stats["current_queued"] = len(self.task_queue)
                logger.info(f"🚫 任务已取消: {task_id}")
                return True
        
        # 运行中的任务无法取消（可以考虑实现中断机制）
        if task_id in self.running_tasks:
            logger.warning(f"⚠️ 运行中的任务无法取消: {task_id}")
            return False
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            **self.stats,
            "uptime_seconds": uptime,
            "tasks_per_minute": (self.stats["total_completed"] / uptime * 60) if uptime > 0 else 0,
            "success_rate": (
                self.stats["total_completed"] / 
                (self.stats["total_completed"] + self.stats["total_failed"])
                if (self.stats["total_completed"] + self.stats["total_failed"]) > 0 else 0
            ),
            "queue_utilization": len(self.task_queue) / self.max_queue_size,
            "concurrency_utilization": len(self.running_tasks) / self.max_concurrent_tasks
        }
    
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        queue_by_priority = defaultdict(int)
        for task in self.task_queue:
            queue_by_priority[task.priority.name] += 1
        
        return {
            "total_queued": len(self.task_queue),
            "total_running": len(self.running_tasks),
            "queue_by_priority": dict(queue_by_priority),
            "running_tasks": [
                {
                    "task_id": task.task_id,
                    "stock_code": task.stock_code,
                    "analysis_type": task.analysis_type,
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "running_time": (
                        (datetime.now() - task.started_at).total_seconds() 
                        if task.started_at else 0
                    )
                }
                for task in self.running_tasks.values()
            ]
        }
    
    async def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """清理完成的任务"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for task_id, task in self.completed_tasks.items():
            if task.completed_at and task.completed_at < cutoff_time:
                to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.completed_tasks[task_id]
        
        if to_remove:
            logger.info(f"🧹 清理了{len(to_remove)}个过期任务")
    
    async def shutdown(self):
        """关闭并发管理器"""
        logger.info("🔄 关闭并发管理器...")
        
        # 取消所有队列中的任务
        for task in self.task_queue:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()
            self.completed_tasks[task.task_id] = task
        
        self.task_queue.clear()
        
        # 等待运行中的任务完成
        while self.running_tasks:
            logger.info(f"⏳ 等待{len(self.running_tasks)}个任务完成...")
            await asyncio.sleep(1)
        
        logger.info("✅ 并发管理器已关闭")

# 全局并发管理器实例
_concurrency_manager: Optional[ConcurrencyManager] = None

def get_concurrency_manager(max_concurrent_tasks: int = 10, max_queue_size: int = 100) -> ConcurrencyManager:
    """获取全局并发管理器实例"""
    global _concurrency_manager
    
    if _concurrency_manager is None:
        _concurrency_manager = ConcurrencyManager(max_concurrent_tasks, max_queue_size)
    
    return _concurrency_manager

async def shutdown_concurrency_manager():
    """关闭全局并发管理器"""
    global _concurrency_manager
    
    if _concurrency_manager:
        await _concurrency_manager.shutdown()
        _concurrency_manager = None
