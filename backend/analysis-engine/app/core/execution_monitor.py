"""
执行监控器 - 监控分析任务的执行状态和性能
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import psutil
import time

from .workflow_scheduler import WorkflowTask, TaskStatus, WorkflowScheduler

logger = logging.getLogger("tradingagents.analysis-engine.execution_monitor")

class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class SystemMetrics:
    """系统指标"""
    cpu_usage: float = 0.0          # CPU使用率
    memory_usage: float = 0.0       # 内存使用率
    disk_usage: float = 0.0         # 磁盘使用率
    network_io: Dict[str, float] = field(default_factory=dict)  # 网络IO
    active_connections: int = 0      # 活跃连接数
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PerformanceMetrics:
    """性能指标"""
    avg_response_time: float = 0.0   # 平均响应时间
    throughput: float = 0.0          # 吞吐量（任务/秒）
    error_rate: float = 0.0          # 错误率
    queue_length: int = 0            # 队列长度
    concurrent_tasks: int = 0        # 并发任务数
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Alert:
    """告警信息"""
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    source: str                      # 告警来源
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ExecutionMonitor:
    """执行监控器"""
    
    def __init__(self, scheduler: WorkflowScheduler):
        self.scheduler = scheduler
        self.is_monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        # 指标存储
        self.system_metrics_history: List[SystemMetrics] = []
        self.performance_metrics_history: List[PerformanceMetrics] = []
        self.alerts: Dict[str, Alert] = {}
        
        # 监控配置
        self.config = {
            "metrics_retention_hours": 24,      # 指标保留时间
            "collection_interval": 30,          # 收集间隔（秒）
            "alert_thresholds": {
                "cpu_usage": 80.0,              # CPU使用率告警阈值
                "memory_usage": 85.0,           # 内存使用率告警阈值
                "disk_usage": 90.0,             # 磁盘使用率告警阈值
                "error_rate": 10.0,             # 错误率告警阈值
                "avg_response_time": 300.0,     # 平均响应时间告警阈值
                "queue_length": 50              # 队列长度告警阈值
            }
        }
        
        # 性能统计
        self.task_start_times: Dict[str, datetime] = {}
        self.completed_tasks_count = 0
        self.failed_tasks_count = 0
        self.last_throughput_calculation = datetime.now()
        
        # 注册调度器事件回调
        self._register_scheduler_callbacks()
    
    def _register_scheduler_callbacks(self):
        """注册调度器事件回调"""
        self.scheduler.register_callback("task_started", self._on_task_started)
        self.scheduler.register_callback("task_completed", self._on_task_completed)
        self.scheduler.register_callback("task_failed", self._on_task_failed)
        self.scheduler.register_callback("task_timeout", self._on_task_timeout)
    
    async def start(self):
        """启动监控"""
        if self.is_monitoring:
            logger.warning("⚠️ 执行监控器已在运行")
            return
        
        self.is_monitoring = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("📊 执行监控器启动")
    
    async def stop(self):
        """停止监控"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("📊 执行监控器停止")
    
    async def _monitoring_loop(self):
        """监控主循环"""
        while self.is_monitoring:
            try:
                # 收集系统指标
                await self._collect_system_metrics()
                
                # 收集性能指标
                await self._collect_performance_metrics()
                
                # 检查告警条件
                await self._check_alerts()
                
                # 清理历史数据
                await self._cleanup_old_data()
                
                await asyncio.sleep(self.config["collection_interval"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 监控循环出错: {e}")
                await asyncio.sleep(10)
    
    async def _collect_system_metrics(self):
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            
            # 网络IO
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            # 活跃连接数（简化实现）
            active_connections = len(psutil.net_connections())
            
            metrics = SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io,
                active_connections=active_connections
            )
            
            self.system_metrics_history.append(metrics)
            
        except Exception as e:
            logger.error(f"❌ 收集系统指标失败: {e}")
    
    async def _collect_performance_metrics(self):
        """收集性能指标"""
        try:
            # 获取调度器指标
            scheduler_metrics = self.scheduler.get_metrics()
            
            # 计算平均响应时间
            avg_response_time = scheduler_metrics.average_execution_time
            
            # 计算吞吐量
            current_time = datetime.now()
            time_diff = (current_time - self.last_throughput_calculation).total_seconds()
            if time_diff > 0:
                throughput = self.completed_tasks_count / time_diff
            else:
                throughput = 0.0
            
            # 重置计数器
            self.completed_tasks_count = 0
            self.last_throughput_calculation = current_time
            
            # 计算错误率
            total_finished = scheduler_metrics.completed_tasks + scheduler_metrics.failed_tasks
            if total_finished > 0:
                error_rate = (scheduler_metrics.failed_tasks / total_finished) * 100
            else:
                error_rate = 0.0
            
            # 队列长度和并发任务数
            queue_length = scheduler_metrics.pending_tasks
            concurrent_tasks = scheduler_metrics.running_tasks
            
            metrics = PerformanceMetrics(
                avg_response_time=avg_response_time,
                throughput=throughput,
                error_rate=error_rate,
                queue_length=queue_length,
                concurrent_tasks=concurrent_tasks
            )
            
            self.performance_metrics_history.append(metrics)
            
        except Exception as e:
            logger.error(f"❌ 收集性能指标失败: {e}")
    
    async def _check_alerts(self):
        """检查告警条件"""
        if not self.system_metrics_history or not self.performance_metrics_history:
            return
        
        latest_system = self.system_metrics_history[-1]
        latest_performance = self.performance_metrics_history[-1]
        thresholds = self.config["alert_thresholds"]
        
        # 检查系统指标告警
        await self._check_threshold_alert(
            "cpu_usage", latest_system.cpu_usage, thresholds["cpu_usage"],
            f"CPU使用率过高: {latest_system.cpu_usage:.1f}%"
        )
        
        await self._check_threshold_alert(
            "memory_usage", latest_system.memory_usage, thresholds["memory_usage"],
            f"内存使用率过高: {latest_system.memory_usage:.1f}%"
        )
        
        await self._check_threshold_alert(
            "disk_usage", latest_system.disk_usage, thresholds["disk_usage"],
            f"磁盘使用率过高: {latest_system.disk_usage:.1f}%"
        )
        
        # 检查性能指标告警
        await self._check_threshold_alert(
            "error_rate", latest_performance.error_rate, thresholds["error_rate"],
            f"错误率过高: {latest_performance.error_rate:.1f}%"
        )
        
        await self._check_threshold_alert(
            "avg_response_time", latest_performance.avg_response_time, thresholds["avg_response_time"],
            f"平均响应时间过长: {latest_performance.avg_response_time:.1f}s"
        )
        
        await self._check_threshold_alert(
            "queue_length", latest_performance.queue_length, thresholds["queue_length"],
            f"任务队列过长: {latest_performance.queue_length} 个任务"
        )
    
    async def _check_threshold_alert(self, metric_name: str, current_value: float, threshold: float, message: str):
        """检查阈值告警"""
        alert_id = f"threshold_{metric_name}"
        
        if current_value > threshold:
            # 触发告警
            if alert_id not in self.alerts or self.alerts[alert_id].resolved:
                level = AlertLevel.WARNING if current_value < threshold * 1.2 else AlertLevel.ERROR
                
                alert = Alert(
                    alert_id=alert_id,
                    level=level,
                    title=f"{metric_name.upper()} 阈值告警",
                    message=message,
                    source="execution_monitor",
                    timestamp=datetime.now(),
                    metadata={"current_value": current_value, "threshold": threshold}
                )
                
                self.alerts[alert_id] = alert
                logger.warning(f"⚠️ 触发告警: {message}")
        else:
            # 解决告警
            if alert_id in self.alerts and not self.alerts[alert_id].resolved:
                self.alerts[alert_id].resolved = True
                self.alerts[alert_id].resolved_at = datetime.now()
                logger.info(f"✅ 告警已解决: {metric_name}")
    
    async def _cleanup_old_data(self):
        """清理历史数据"""
        cutoff_time = datetime.now() - timedelta(hours=self.config["metrics_retention_hours"])
        
        # 清理系统指标
        self.system_metrics_history = [
            m for m in self.system_metrics_history if m.timestamp > cutoff_time
        ]
        
        # 清理性能指标
        self.performance_metrics_history = [
            m for m in self.performance_metrics_history if m.timestamp > cutoff_time
        ]
        
        # 清理已解决的告警
        resolved_alerts = [
            alert_id for alert_id, alert in self.alerts.items()
            if alert.resolved and alert.resolved_at and alert.resolved_at < cutoff_time
        ]
        
        for alert_id in resolved_alerts:
            del self.alerts[alert_id]
    
    # 事件回调方法
    async def _on_task_started(self, task: WorkflowTask):
        """任务开始回调"""
        self.task_start_times[task.task_id] = datetime.now()
    
    async def _on_task_completed(self, task: WorkflowTask):
        """任务完成回调"""
        self.completed_tasks_count += 1
        if task.task_id in self.task_start_times:
            del self.task_start_times[task.task_id]
    
    async def _on_task_failed(self, task: WorkflowTask):
        """任务失败回调"""
        self.failed_tasks_count += 1
        if task.task_id in self.task_start_times:
            del self.task_start_times[task.task_id]
        
        # 创建任务失败告警
        alert = Alert(
            alert_id=f"task_failed_{task.task_id}",
            level=AlertLevel.ERROR,
            title="任务执行失败",
            message=f"任务 {task.task_id} ({task.task_type}) 执行失败: {task.error}",
            source="task_execution",
            timestamp=datetime.now(),
            metadata={"task_id": task.task_id, "task_type": task.task_type, "symbol": task.symbol}
        )
        
        self.alerts[alert.alert_id] = alert
    
    async def _on_task_timeout(self, task: WorkflowTask):
        """任务超时回调"""
        if task.task_id in self.task_start_times:
            del self.task_start_times[task.task_id]
        
        # 创建任务超时告警
        alert = Alert(
            alert_id=f"task_timeout_{task.task_id}",
            level=AlertLevel.WARNING,
            title="任务执行超时",
            message=f"任务 {task.task_id} ({task.task_type}) 执行超时",
            source="task_execution",
            timestamp=datetime.now(),
            metadata={"task_id": task.task_id, "task_type": task.task_type, "symbol": task.symbol}
        )
        
        self.alerts[alert.alert_id] = alert
    
    # 查询方法
    def get_latest_system_metrics(self) -> Optional[SystemMetrics]:
        """获取最新系统指标"""
        return self.system_metrics_history[-1] if self.system_metrics_history else None
    
    def get_latest_performance_metrics(self) -> Optional[PerformanceMetrics]:
        """获取最新性能指标"""
        return self.performance_metrics_history[-1] if self.performance_metrics_history else None
    
    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_system_metrics_history(self, hours: int = 1) -> List[SystemMetrics]:
        """获取系统指标历史"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [m for m in self.system_metrics_history if m.timestamp > cutoff_time]
    
    def get_performance_metrics_history(self, hours: int = 1) -> List[PerformanceMetrics]:
        """获取性能指标历史"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [m for m in self.performance_metrics_history if m.timestamp > cutoff_time]
