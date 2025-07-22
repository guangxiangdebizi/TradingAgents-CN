"""
负载均衡器
管理多个Analysis Engine实例的负载分发
"""

import asyncio
import logging
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import random
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class InstanceStatus(Enum):
    """实例状态"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class LoadBalanceStrategy(Enum):
    """负载均衡策略"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RANDOM = "random"
    HEALTH_AWARE = "health_aware"

@dataclass
class AnalysisEngineInstance:
    """Analysis Engine实例"""
    instance_id: str
    host: str
    port: int
    weight: int = 1
    status: InstanceStatus = InstanceStatus.UNKNOWN
    current_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    last_health_check: Optional[datetime] = None
    response_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    
    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return (self.total_requests - self.failed_requests) / self.total_requests
    
    @property
    def is_healthy(self) -> bool:
        return self.status == InstanceStatus.HEALTHY

class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, strategy: LoadBalanceStrategy = LoadBalanceStrategy.HEALTH_AWARE):
        self.strategy = strategy
        self.instances: Dict[str, AnalysisEngineInstance] = {}
        self.round_robin_index = 0
        self.session: Optional[aiohttp.ClientSession] = None
        self.health_check_interval = 30  # 30秒健康检查间隔
        self.health_check_timeout = 10   # 10秒健康检查超时
        self.health_check_task: Optional[asyncio.Task] = None
        
        logger.info(f"🔄 负载均衡器初始化: 策略={strategy.value}")
    
    async def initialize(self):
        """初始化负载均衡器"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        # 启动健康检查任务
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info("✅ 负载均衡器初始化完成")
    
    def add_instance(self, instance_id: str, host: str, port: int, weight: int = 1):
        """添加Analysis Engine实例"""
        instance = AnalysisEngineInstance(
            instance_id=instance_id,
            host=host,
            port=port,
            weight=weight
        )
        
        self.instances[instance_id] = instance
        logger.info(f"➕ 添加实例: {instance_id} ({host}:{port}) 权重={weight}")
    
    def remove_instance(self, instance_id: str):
        """移除Analysis Engine实例"""
        if instance_id in self.instances:
            del self.instances[instance_id]
            logger.info(f"➖ 移除实例: {instance_id}")
    
    async def select_instance(self) -> Optional[AnalysisEngineInstance]:
        """根据负载均衡策略选择实例"""
        healthy_instances = [
            instance for instance in self.instances.values()
            if instance.is_healthy
        ]
        
        if not healthy_instances:
            logger.warning("⚠️ 没有健康的实例可用")
            return None
        
        if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._round_robin_select(healthy_instances)
        elif self.strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(healthy_instances)
        elif self.strategy == LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(healthy_instances)
        elif self.strategy == LoadBalanceStrategy.RANDOM:
            return self._random_select(healthy_instances)
        elif self.strategy == LoadBalanceStrategy.HEALTH_AWARE:
            return self._health_aware_select(healthy_instances)
        else:
            return healthy_instances[0]
    
    def _round_robin_select(self, instances: List[AnalysisEngineInstance]) -> AnalysisEngineInstance:
        """轮询选择"""
        instance = instances[self.round_robin_index % len(instances)]
        self.round_robin_index += 1
        return instance
    
    def _least_connections_select(self, instances: List[AnalysisEngineInstance]) -> AnalysisEngineInstance:
        """最少连接选择"""
        return min(instances, key=lambda x: x.current_connections)
    
    def _weighted_round_robin_select(self, instances: List[AnalysisEngineInstance]) -> AnalysisEngineInstance:
        """加权轮询选择"""
        total_weight = sum(instance.weight for instance in instances)
        if total_weight == 0:
            return instances[0]
        
        # 简化的加权轮询实现
        weights = [instance.weight for instance in instances]
        return random.choices(instances, weights=weights)[0]
    
    def _random_select(self, instances: List[AnalysisEngineInstance]) -> AnalysisEngineInstance:
        """随机选择"""
        return random.choice(instances)
    
    def _health_aware_select(self, instances: List[AnalysisEngineInstance]) -> AnalysisEngineInstance:
        """健康感知选择（综合考虑响应时间、成功率、连接数）"""
        def score(instance: AnalysisEngineInstance) -> float:
            # 计算综合得分（越低越好）
            response_score = instance.response_time
            connection_score = instance.current_connections * 0.1
            success_score = (1 - instance.success_rate) * 10
            cpu_score = instance.cpu_usage * 0.01
            memory_score = instance.memory_usage * 0.01
            
            return response_score + connection_score + success_score + cpu_score + memory_score
        
        return min(instances, key=score)
    
    async def forward_request(self, path: str, method: str = "POST", 
                             data: Optional[Dict[str, Any]] = None,
                             params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """转发请求到选定的实例"""
        instance = await self.select_instance()
        if not instance:
            raise Exception("没有可用的Analysis Engine实例")
        
        # 增加连接计数
        instance.current_connections += 1
        instance.total_requests += 1
        
        try:
            start_time = time.time()
            
            # 构建完整URL
            url = f"{instance.url}{path}"
            
            # 发送请求
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            ) as response:
                response_time = time.time() - start_time
                instance.response_time = response_time
                
                if response.status == 200:
                    result = await response.json()
                    logger.debug(f"✅ 请求成功: {instance.instance_id} - {response_time:.3f}s")
                    return result
                else:
                    instance.failed_requests += 1
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            instance.failed_requests += 1
            logger.error(f"❌ 请求失败: {instance.instance_id} - {e}")
            raise
        finally:
            # 减少连接计数
            instance.current_connections = max(0, instance.current_connections - 1)
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 健康检查异常: {e}")
                await asyncio.sleep(5)
    
    async def _perform_health_checks(self):
        """执行健康检查"""
        if not self.session:
            return
        
        tasks = []
        for instance in self.instances.values():
            task = asyncio.create_task(self._check_instance_health(instance))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_instance_health(self, instance: AnalysisEngineInstance):
        """检查单个实例健康状态"""
        try:
            start_time = time.time()
            
            async with self.session.get(
                f"{instance.url}/health",
                timeout=aiohttp.ClientTimeout(total=self.health_check_timeout)
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    health_data = await response.json()
                    
                    # 更新实例状态
                    instance.status = InstanceStatus.HEALTHY
                    instance.response_time = response_time
                    instance.last_health_check = datetime.now()
                    
                    # 更新系统指标（如果有的话）
                    if "cpu_usage" in health_data:
                        instance.cpu_usage = health_data["cpu_usage"]
                    if "memory_usage" in health_data:
                        instance.memory_usage = health_data["memory_usage"]
                    
                    logger.debug(f"💚 健康检查通过: {instance.instance_id} - {response_time:.3f}s")
                else:
                    instance.status = InstanceStatus.UNHEALTHY
                    logger.warning(f"💛 健康检查失败: {instance.instance_id} - HTTP {response.status}")
                    
        except Exception as e:
            instance.status = InstanceStatus.UNHEALTHY
            instance.last_health_check = datetime.now()
            logger.warning(f"❤️ 健康检查异常: {instance.instance_id} - {e}")
    
    def get_instance_stats(self) -> Dict[str, Any]:
        """获取实例统计信息"""
        stats = {
            "total_instances": len(self.instances),
            "healthy_instances": sum(1 for i in self.instances.values() if i.is_healthy),
            "unhealthy_instances": sum(1 for i in self.instances.values() if not i.is_healthy),
            "total_connections": sum(i.current_connections for i in self.instances.values()),
            "total_requests": sum(i.total_requests for i in self.instances.values()),
            "total_failed_requests": sum(i.failed_requests for i in self.instances.values()),
            "instances": []
        }
        
        for instance in self.instances.values():
            stats["instances"].append({
                "instance_id": instance.instance_id,
                "url": instance.url,
                "status": instance.status.value,
                "weight": instance.weight,
                "current_connections": instance.current_connections,
                "total_requests": instance.total_requests,
                "failed_requests": instance.failed_requests,
                "success_rate": instance.success_rate,
                "response_time": instance.response_time,
                "cpu_usage": instance.cpu_usage,
                "memory_usage": instance.memory_usage,
                "last_health_check": instance.last_health_check.isoformat() if instance.last_health_check else None
            })
        
        return stats
    
    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理负载均衡器资源...")
        
        # 停止健康检查任务
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        # 关闭HTTP会话
        if self.session:
            await self.session.close()
            self.session = None
        
        logger.info("✅ 负载均衡器资源清理完成")

# 全局负载均衡器实例
_load_balancer: Optional[LoadBalancer] = None

def get_load_balancer(strategy: LoadBalanceStrategy = LoadBalanceStrategy.HEALTH_AWARE) -> LoadBalancer:
    """获取全局负载均衡器实例"""
    global _load_balancer
    
    if _load_balancer is None:
        _load_balancer = LoadBalancer(strategy)
    
    return _load_balancer

async def cleanup_load_balancer():
    """清理全局负载均衡器"""
    global _load_balancer
    
    if _load_balancer:
        await _load_balancer.cleanup()
        _load_balancer = None
