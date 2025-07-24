"""
工作流调度器 - 管理分析任务的调度和执行监控
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json

logger = logging.getLogger("tradingagents.analysis-engine.workflow_scheduler")

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"         # 等待执行
    RUNNING = "running"         # 正在执行
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"          # 执行失败
    CANCELLED = "cancelled"     # 已取消
    TIMEOUT = "timeout"        # 执行超时

class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class WorkflowTask:
    """工作流任务"""
    task_id: str
    symbol: str
    task_type: str              # 任务类型：analysis, debate, risk_assessment
    priority: TaskPriority
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0       # 进度百分比 (0-100)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timeout_seconds: int = 300  # 默认5分钟超时
    retry_count: int = 0
    max_retries: int = 3
    dependencies: List[str] = field(default_factory=list)  # 依赖的任务ID
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowMetrics:
    """工作流指标"""
    total_tasks: int = 0
    pending_tasks: int = 0
    running_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_execution_time: float = 0.0
    success_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

class WorkflowScheduler:
    """工作流调度器"""
    
    def __init__(self, max_concurrent_tasks: int = 5):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.tasks: Dict[str, WorkflowTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_queue: List[str] = []  # 按优先级排序的任务队列
        self.metrics = WorkflowMetrics()
        self.is_running = False
        self._scheduler_task: Optional[asyncio.Task] = None
        
        # 任务执行器映射
        self.task_executors: Dict[str, Callable] = {}
        
        # 事件回调
        self.event_callbacks: Dict[str, List[Callable]] = {
            "task_started": [],
            "task_completed": [],
            "task_failed": [],
            "task_timeout": []
        }
    
    def register_executor(self, task_type: str, executor: Callable):
        """注册任务执行器"""
        self.task_executors[task_type] = executor
        logger.info(f"📋 注册任务执行器: {task_type}")
    
    def register_callback(self, event: str, callback: Callable):
        """注册事件回调"""
        if event in self.event_callbacks:
            self.event_callbacks[event].append(callback)
            logger.info(f"📞 注册事件回调: {event}")
    
    async def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("⚠️ 调度器已在运行")
            return
        
        self.is_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("🚀 工作流调度器启动")
    
    async def stop(self):
        """停止调度器"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 取消所有运行中的任务
        for task_id, task in self.running_tasks.items():
            task.cancel()
            self.tasks[task_id].status = TaskStatus.CANCELLED
        
        # 停止调度器循环
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🛑 工作流调度器停止")
    
    def submit_task(
        self,
        symbol: str,
        task_type: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        scheduled_at: Optional[datetime] = None,
        timeout_seconds: int = 300,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """提交任务"""
        task_id = str(uuid.uuid4())
        
        task = WorkflowTask(
            task_id=task_id,
            symbol=symbol,
            task_type=task_type,
            priority=priority,
            created_at=datetime.now(),
            scheduled_at=scheduled_at,
            timeout_seconds=timeout_seconds,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        
        self.tasks[task_id] = task
        self._add_to_queue(task_id)
        self._update_metrics()
        
        logger.info(f"📝 提交任务: {task_id} ({task_type}, {symbol})")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[WorkflowTask]:
        """获取任务信息"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_symbol(self, symbol: str) -> List[WorkflowTask]:
        """获取指定股票的所有任务"""
        return [task for task in self.tasks.values() if task.symbol == symbol]
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[WorkflowTask]:
        """获取指定状态的任务"""
        return [task for task in self.tasks.values() if task.status == status]
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status == TaskStatus.RUNNING:
            # 取消正在运行的任务
            running_task = self.running_tasks.get(task_id)
            if running_task:
                running_task.cancel()
        elif task.status == TaskStatus.PENDING:
            # 从队列中移除
            if task_id in self.task_queue:
                self.task_queue.remove(task_id)
        
        task.status = TaskStatus.CANCELLED
        self._update_metrics()
        
        logger.info(f"❌ 取消任务: {task_id}")
        return True
    
    def get_metrics(self) -> WorkflowMetrics:
        """获取工作流指标"""
        self._update_metrics()
        return self.metrics
    
    async def _scheduler_loop(self):
        """调度器主循环"""
        while self.is_running:
            try:
                await self._process_queue()
                await self._check_timeouts()
                await self._cleanup_completed_tasks()
                await asyncio.sleep(1)  # 每秒检查一次
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 调度器循环出错: {e}")
                await asyncio.sleep(5)  # 出错后等待5秒再继续
    
    async def _process_queue(self):
        """处理任务队列"""
        if len(self.running_tasks) >= self.max_concurrent_tasks:
            return
        
        # 找到可以执行的任务
        ready_tasks = []
        for task_id in self.task_queue:
            task = self.tasks[task_id]
            
            # 检查调度时间
            if task.scheduled_at and task.scheduled_at > datetime.now():
                continue
            
            # 检查依赖
            if self._check_dependencies(task):
                ready_tasks.append(task_id)
        
        # 按优先级排序
        ready_tasks.sort(key=lambda tid: self.tasks[tid].priority.value, reverse=True)
        
        # 执行任务
        for task_id in ready_tasks:
            if len(self.running_tasks) >= self.max_concurrent_tasks:
                break
            
            await self._execute_task(task_id)
    
    def _check_dependencies(self, task: WorkflowTask) -> bool:
        """检查任务依赖是否满足"""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    async def _execute_task(self, task_id: str):
        """执行任务"""
        task = self.tasks[task_id]
        executor = self.task_executors.get(task.task_type)
        
        if not executor:
            task.status = TaskStatus.FAILED
            task.error = f"未找到任务执行器: {task.task_type}"
            logger.error(f"❌ {task.error}")
            return
        
        # 从队列中移除
        if task_id in self.task_queue:
            self.task_queue.remove(task_id)
        
        # 更新任务状态
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        # 创建执行任务
        execution_task = asyncio.create_task(self._run_task_with_timeout(task, executor))
        self.running_tasks[task_id] = execution_task
        
        # 触发事件回调
        await self._trigger_callbacks("task_started", task)
        
        logger.info(f"🚀 开始执行任务: {task_id} ({task.task_type})")
    
    async def _run_task_with_timeout(self, task: WorkflowTask, executor: Callable):
        """带超时的任务执行"""
        try:
            # 执行任务
            result = await asyncio.wait_for(
                executor(task),
                timeout=task.timeout_seconds
            )
            
            # 任务成功完成
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            task.progress = 100.0
            
            await self._trigger_callbacks("task_completed", task)
            logger.info(f"✅ 任务完成: {task.task_id}")
            
        except asyncio.TimeoutError:
            # 任务超时
            task.status = TaskStatus.TIMEOUT
            task.error = f"任务执行超时 ({task.timeout_seconds}s)"
            
            await self._trigger_callbacks("task_timeout", task)
            logger.error(f"⏰ 任务超时: {task.task_id}")
            
        except Exception as e:
            # 任务执行失败
            task.status = TaskStatus.FAILED
            task.error = str(e)
            
            # 检查是否需要重试
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                self._add_to_queue(task.task_id)
                logger.warning(f"🔄 任务重试: {task.task_id} (第{task.retry_count}次)")
            else:
                await self._trigger_callbacks("task_failed", task)
                logger.error(f"❌ 任务失败: {task.task_id} - {e}")
        
        finally:
            # 清理运行中的任务
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
    
    async def _check_timeouts(self):
        """检查任务超时"""
        current_time = datetime.now()
        
        for task_id, task in list(self.running_tasks.items()):
            workflow_task = self.tasks[task_id]
            if workflow_task.started_at:
                elapsed = (current_time - workflow_task.started_at).total_seconds()
                if elapsed > workflow_task.timeout_seconds:
                    task.cancel()
    
    async def _cleanup_completed_tasks(self):
        """清理已完成的任务（可选：保留最近的任务）"""
        # 保留最近24小时的任务
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        completed_tasks = [
            task_id for task_id, task in self.tasks.items()
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
            and task.completed_at and task.completed_at < cutoff_time
        ]
        
        for task_id in completed_tasks:
            del self.tasks[task_id]
    
    def _add_to_queue(self, task_id: str):
        """添加任务到队列"""
        if task_id not in self.task_queue:
            self.task_queue.append(task_id)
            # 按优先级排序
            self.task_queue.sort(key=lambda tid: self.tasks[tid].priority.value, reverse=True)
    
    def _update_metrics(self):
        """更新工作流指标"""
        self.metrics.total_tasks = len(self.tasks)
        self.metrics.pending_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
        self.metrics.running_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.RUNNING])
        self.metrics.completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        self.metrics.failed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
        
        # 计算成功率
        total_finished = self.metrics.completed_tasks + self.metrics.failed_tasks
        if total_finished > 0:
            self.metrics.success_rate = self.metrics.completed_tasks / total_finished * 100
        
        # 计算平均执行时间
        completed_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED and t.started_at and t.completed_at]
        if completed_tasks:
            total_time = sum((t.completed_at - t.started_at).total_seconds() for t in completed_tasks)
            self.metrics.average_execution_time = total_time / len(completed_tasks)
        
        self.metrics.last_updated = datetime.now()
    
    async def _trigger_callbacks(self, event: str, task: WorkflowTask):
        """触发事件回调"""
        for callback in self.event_callbacks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(task)
                else:
                    callback(task)
            except Exception as e:
                logger.error(f"❌ 事件回调出错 ({event}): {e}")
