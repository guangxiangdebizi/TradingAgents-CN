"""
性能监控器
负责监控智能体和系统的性能指标
"""

import asyncio
import time
import psutil
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque

from backend.shared.logging_config import get_logger

logger = get_logger("agent-service.performance_monitor")


@dataclass
class PerformanceMetrics:
    """性能指标"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    memory_total: float
    disk_io_read: float
    disk_io_write: float
    network_io_sent: float
    network_io_recv: float
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    average_response_time: float


@dataclass
class AgentMetrics:
    """智能体指标"""
    agent_id: str
    agent_type: str
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    last_activity: Optional[datetime] = None
    error_rate: float = 0.0
    throughput: float = 0.0  # 任务/小时
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_tasks == 0:
            return 0.0
        return self.successful_tasks / self.total_tasks
    
    @property
    def average_duration(self) -> float:
        """平均执行时间"""
        if self.successful_tasks == 0:
            return 0.0
        return self.total_duration / self.successful_tasks
    
    @property
    def current_response_time(self) -> float:
        """当前响应时间"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
        
        # 系统指标历史
        self.system_metrics_history: deque = deque(maxlen=1000)
        
        # 智能体指标
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        
        # 任务统计
        self.task_stats = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "cancelled": 0,
            "timeout": 0
        }
        
        # 性能阈值
        self.thresholds = {
            "cpu_warning": 80.0,
            "cpu_critical": 95.0,
            "memory_warning": 80.0,
            "memory_critical": 95.0,
            "response_time_warning": 30.0,
            "response_time_critical": 60.0,
            "error_rate_warning": 0.1,
            "error_rate_critical": 0.2
        }
        
        # 监控任务
        self.monitoring_task: Optional[asyncio.Task] = None
        self.monitoring_interval = 30  # 秒
        
        # 告警历史
        self.alerts_history: deque = deque(maxlen=100)
        
        logger.info("🏗️ 性能监控器初始化")
    
    async def initialize(self):
        """初始化性能监控器"""
        try:
            # 启动监控任务
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("✅ 性能监控器初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 性能监控器初始化失败: {e}")
            raise
    
    async def record_task_start(self, agent_id: str, agent_type: str, task_id: str):
        """记录任务开始"""
        try:
            if agent_id not in self.agent_metrics:
                self.agent_metrics[agent_id] = AgentMetrics(
                    agent_id=agent_id,
                    agent_type=agent_type
                )
            
            metrics = self.agent_metrics[agent_id]
            metrics.last_activity = datetime.now()
            
            # 保存任务开始时间
            await self.state_manager.save_task_state(
                f"task_start_{task_id}",
                {"start_time": time.time(), "agent_id": agent_id}
            )
            
        except Exception as e:
            logger.error(f"❌ 记录任务开始失败: {agent_id} - {e}")
    
    async def record_task_completion(
        self, 
        agent_id: str, 
        task_id: str, 
        success: bool, 
        duration: Optional[float] = None
    ):
        """记录任务完成"""
        try:
            if agent_id not in self.agent_metrics:
                return
            
            metrics = self.agent_metrics[agent_id]
            metrics.total_tasks += 1
            
            # 计算执行时间
            if duration is None:
                task_start_data = await self.state_manager.get_task_state(f"task_start_{task_id}")
                if task_start_data:
                    start_time = task_start_data.get("start_time", time.time())
                    duration = time.time() - start_time
                else:
                    duration = 0.0
            
            if success:
                metrics.successful_tasks += 1
                metrics.total_duration += duration
                metrics.min_duration = min(metrics.min_duration, duration)
                metrics.max_duration = max(metrics.max_duration, duration)
                metrics.response_times.append(duration)
                self.task_stats["successful"] += 1
            else:
                metrics.failed_tasks += 1
                self.task_stats["failed"] += 1
            
            # 更新错误率
            metrics.error_rate = metrics.failed_tasks / metrics.total_tasks
            
            # 更新吞吐量（任务/小时）
            if metrics.last_activity:
                hours_since_start = (datetime.now() - metrics.last_activity).total_seconds() / 3600
                if hours_since_start > 0:
                    metrics.throughput = metrics.total_tasks / hours_since_start
            
            metrics.last_activity = datetime.now()
            self.task_stats["total"] += 1
            
            # 清理任务开始数据
            await self.state_manager.delete_state("task", f"task_start_{task_id}")
            
            # 检查性能告警
            await self._check_agent_alerts(agent_id, metrics)
            
        except Exception as e:
            logger.error(f"❌ 记录任务完成失败: {agent_id} - {e}")
    
    async def get_system_metrics(self) -> PerformanceMetrics:
        """获取系统性能指标"""
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            memory_total = memory.total / (1024 ** 3)  # GB
            
            # 磁盘IO
            disk_io = psutil.disk_io_counters()
            disk_io_read = disk_io.read_bytes / (1024 ** 2) if disk_io else 0  # MB
            disk_io_write = disk_io.write_bytes / (1024 ** 2) if disk_io else 0  # MB
            
            # 网络IO
            network_io = psutil.net_io_counters()
            network_io_sent = network_io.bytes_sent / (1024 ** 2) if network_io else 0  # MB
            network_io_recv = network_io.bytes_recv / (1024 ** 2) if network_io else 0  # MB
            
            # 任务统计
            active_tasks = sum(1 for metrics in self.agent_metrics.values() 
                             if metrics.last_activity and 
                             (datetime.now() - metrics.last_activity).total_seconds() < 300)
            
            # 平均响应时间
            all_response_times = []
            for metrics in self.agent_metrics.values():
                all_response_times.extend(metrics.response_times)
            
            avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0.0
            
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                memory_total=memory_total,
                disk_io_read=disk_io_read,
                disk_io_write=disk_io_write,
                network_io_sent=network_io_sent,
                network_io_recv=network_io_recv,
                active_tasks=active_tasks,
                completed_tasks=self.task_stats["successful"],
                failed_tasks=self.task_stats["failed"],
                average_response_time=avg_response_time
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ 获取系统指标失败: {e}")
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_usage=0.0, memory_usage=0.0, memory_total=0.0,
                disk_io_read=0.0, disk_io_write=0.0,
                network_io_sent=0.0, network_io_recv=0.0,
                active_tasks=0, completed_tasks=0, failed_tasks=0,
                average_response_time=0.0
            )
    
    async def get_agent_metrics(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """获取智能体指标"""
        try:
            if agent_id:
                metrics = self.agent_metrics.get(agent_id)
                if not metrics:
                    return {}
                
                return {
                    "agent_id": metrics.agent_id,
                    "agent_type": metrics.agent_type,
                    "total_tasks": metrics.total_tasks,
                    "successful_tasks": metrics.successful_tasks,
                    "failed_tasks": metrics.failed_tasks,
                    "success_rate": metrics.success_rate,
                    "error_rate": metrics.error_rate,
                    "average_duration": metrics.average_duration,
                    "min_duration": metrics.min_duration if metrics.min_duration != float('inf') else 0.0,
                    "max_duration": metrics.max_duration,
                    "current_response_time": metrics.current_response_time,
                    "throughput": metrics.throughput,
                    "last_activity": metrics.last_activity.isoformat() if metrics.last_activity else None
                }
            else:
                # 返回所有智能体的指标
                all_metrics = {}
                for agent_id, metrics in self.agent_metrics.items():
                    all_metrics[agent_id] = {
                        "agent_type": metrics.agent_type,
                        "total_tasks": metrics.total_tasks,
                        "success_rate": metrics.success_rate,
                        "error_rate": metrics.error_rate,
                        "average_duration": metrics.average_duration,
                        "throughput": metrics.throughput,
                        "last_activity": metrics.last_activity.isoformat() if metrics.last_activity else None
                    }
                
                return all_metrics
                
        except Exception as e:
            logger.error(f"❌ 获取智能体指标失败: {e}")
            return {}
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        try:
            system_metrics = await self.get_system_metrics()
            
            # 智能体统计
            total_agents = len(self.agent_metrics)
            active_agents = sum(1 for metrics in self.agent_metrics.values() 
                              if metrics.last_activity and 
                              (datetime.now() - metrics.last_activity).total_seconds() < 300)
            
            # 性能等级评估
            performance_grade = self._calculate_performance_grade(system_metrics)
            
            # 最近的告警
            recent_alerts = list(self.alerts_history)[-10:]
            
            summary = {
                "system_metrics": {
                    "cpu_usage": system_metrics.cpu_usage,
                    "memory_usage": system_metrics.memory_usage,
                    "memory_total": system_metrics.memory_total,
                    "average_response_time": system_metrics.average_response_time
                },
                "agent_statistics": {
                    "total_agents": total_agents,
                    "active_agents": active_agents,
                    "idle_agents": total_agents - active_agents
                },
                "task_statistics": self.task_stats.copy(),
                "performance_grade": performance_grade,
                "recent_alerts": recent_alerts,
                "timestamp": datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ 获取性能摘要失败: {e}")
            return {}
    
    def _calculate_performance_grade(self, metrics: PerformanceMetrics) -> str:
        """计算性能等级"""
        try:
            score = 100
            
            # CPU使用率扣分
            if metrics.cpu_usage > self.thresholds["cpu_critical"]:
                score -= 30
            elif metrics.cpu_usage > self.thresholds["cpu_warning"]:
                score -= 15
            
            # 内存使用率扣分
            if metrics.memory_usage > self.thresholds["memory_critical"]:
                score -= 30
            elif metrics.memory_usage > self.thresholds["memory_warning"]:
                score -= 15
            
            # 响应时间扣分
            if metrics.average_response_time > self.thresholds["response_time_critical"]:
                score -= 25
            elif metrics.average_response_time > self.thresholds["response_time_warning"]:
                score -= 10
            
            # 错误率扣分
            total_tasks = metrics.completed_tasks + metrics.failed_tasks
            if total_tasks > 0:
                error_rate = metrics.failed_tasks / total_tasks
                if error_rate > self.thresholds["error_rate_critical"]:
                    score -= 20
                elif error_rate > self.thresholds["error_rate_warning"]:
                    score -= 10
            
            # 等级划分
            if score >= 90:
                return "A"
            elif score >= 80:
                return "B"
            elif score >= 70:
                return "C"
            elif score >= 60:
                return "D"
            else:
                return "F"
                
        except Exception as e:
            logger.error(f"❌ 计算性能等级失败: {e}")
            return "Unknown"
    
    async def _check_agent_alerts(self, agent_id: str, metrics: AgentMetrics):
        """检查智能体告警"""
        try:
            alerts = []
            
            # 错误率告警
            if metrics.error_rate > self.thresholds["error_rate_critical"]:
                alerts.append({
                    "type": "error_rate_critical",
                    "agent_id": agent_id,
                    "value": metrics.error_rate,
                    "threshold": self.thresholds["error_rate_critical"],
                    "message": f"智能体 {agent_id} 错误率过高: {metrics.error_rate:.2%}"
                })
            elif metrics.error_rate > self.thresholds["error_rate_warning"]:
                alerts.append({
                    "type": "error_rate_warning",
                    "agent_id": agent_id,
                    "value": metrics.error_rate,
                    "threshold": self.thresholds["error_rate_warning"],
                    "message": f"智能体 {agent_id} 错误率偏高: {metrics.error_rate:.2%}"
                })
            
            # 响应时间告警
            if metrics.current_response_time > self.thresholds["response_time_critical"]:
                alerts.append({
                    "type": "response_time_critical",
                    "agent_id": agent_id,
                    "value": metrics.current_response_time,
                    "threshold": self.thresholds["response_time_critical"],
                    "message": f"智能体 {agent_id} 响应时间过长: {metrics.current_response_time:.2f}秒"
                })
            elif metrics.current_response_time > self.thresholds["response_time_warning"]:
                alerts.append({
                    "type": "response_time_warning",
                    "agent_id": agent_id,
                    "value": metrics.current_response_time,
                    "threshold": self.thresholds["response_time_warning"],
                    "message": f"智能体 {agent_id} 响应时间偏长: {metrics.current_response_time:.2f}秒"
                })
            
            # 记录告警
            for alert in alerts:
                alert["timestamp"] = datetime.now().isoformat()
                self.alerts_history.append(alert)
                logger.warning(f"⚠️ 性能告警: {alert['message']}")
                
        except Exception as e:
            logger.error(f"❌ 检查智能体告警失败: {agent_id} - {e}")
    
    async def _monitoring_loop(self):
        """监控循环"""
        while True:
            try:
                await asyncio.sleep(self.monitoring_interval)
                
                # 收集系统指标
                system_metrics = await self.get_system_metrics()
                self.system_metrics_history.append(system_metrics)
                
                # 检查系统告警
                await self._check_system_alerts(system_metrics)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 监控循环错误: {e}")
    
    async def _check_system_alerts(self, metrics: PerformanceMetrics):
        """检查系统告警"""
        try:
            alerts = []
            
            # CPU告警
            if metrics.cpu_usage > self.thresholds["cpu_critical"]:
                alerts.append({
                    "type": "cpu_critical",
                    "value": metrics.cpu_usage,
                    "threshold": self.thresholds["cpu_critical"],
                    "message": f"系统CPU使用率过高: {metrics.cpu_usage:.1f}%"
                })
            elif metrics.cpu_usage > self.thresholds["cpu_warning"]:
                alerts.append({
                    "type": "cpu_warning",
                    "value": metrics.cpu_usage,
                    "threshold": self.thresholds["cpu_warning"],
                    "message": f"系统CPU使用率偏高: {metrics.cpu_usage:.1f}%"
                })
            
            # 内存告警
            if metrics.memory_usage > self.thresholds["memory_critical"]:
                alerts.append({
                    "type": "memory_critical",
                    "value": metrics.memory_usage,
                    "threshold": self.thresholds["memory_critical"],
                    "message": f"系统内存使用率过高: {metrics.memory_usage:.1f}%"
                })
            elif metrics.memory_usage > self.thresholds["memory_warning"]:
                alerts.append({
                    "type": "memory_warning",
                    "value": metrics.memory_usage,
                    "threshold": self.thresholds["memory_warning"],
                    "message": f"系统内存使用率偏高: {metrics.memory_usage:.1f}%"
                })
            
            # 记录告警
            for alert in alerts:
                alert["timestamp"] = datetime.now().isoformat()
                self.alerts_history.append(alert)
                logger.warning(f"⚠️ 系统告警: {alert['message']}")
                
        except Exception as e:
            logger.error(f"❌ 检查系统告警失败: {e}")
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 检查监控任务状态
            if self.monitoring_task and self.monitoring_task.done():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 性能监控器健康检查失败: {e}")
            return False
    
    async def cleanup(self):
        """清理资源"""
        try:
            # 取消监控任务
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # 清理数据
            self.system_metrics_history.clear()
            self.agent_metrics.clear()
            self.alerts_history.clear()
            
            logger.info("✅ 性能监控器清理完成")
            
        except Exception as e:
            logger.error(f"❌ 性能监控器清理失败: {e}")
