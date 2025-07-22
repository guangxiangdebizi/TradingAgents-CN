# 🔍 TradingAgents 服务发现架构设计

## 📍 **概述**

本文档定义了TradingAgents微服务架构中的服务发现方案，涵盖Kubernetes环境下的服务发现、负载均衡、故障转移和性能优化策略。

## 🎯 **设计目标**

### **核心要求**
- ✅ **高可用性**: 99.9%+ 服务可用性
- ✅ **低延迟**: 服务发现延迟 < 10ms
- ✅ **自动扩展**: 支持动态服务实例管理
- ✅ **故障隔离**: 单点故障不影响整体服务
- ✅ **负载均衡**: 智能流量分发
- ✅ **可观测性**: 完整的监控和追踪

### **技术约束**
- 主要部署在Kubernetes环境
- 支持混合云和多集群场景
- 兼容现有微服务架构
- 最小化运维复杂度

## 🏗️ **架构设计**

### **整体架构图**

```
┌─────────────────────────────────────────────────────────────┐
│                    Service Discovery Layer                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Client    │    │   Client    │    │   Client    │     │
│  │ Load Balancer│    │ Load Balancer│    │ Load Balancer│     │
│  └─────┬───────┘    └─────┬───────┘    └─────┬───────┘     │
│        │                  │                  │             │
│        └──────────────────┼──────────────────┘             │
│                           │                                │
│  ┌─────────────────────────▼─────────────────────────┐     │
│  │            Smart Service Discovery                │     │
│  │  • K8s Native Discovery                          │     │
│  │  • Intelligent Caching                           │     │
│  │  • Circuit Breaker                               │     │
│  │  • Health Monitoring                             │     │
│  └─────────────────────┬───────────────────────────┘     │
│                        │                                 │
├────────────────────────┼─────────────────────────────────┤
│                        │                                 │
│  ┌─────────────────────▼─────────────────────────┐       │
│  │              Kubernetes Services              │       │
│  │                                               │       │
│  │  analysis-engine-service ──┐                 │       │
│  │  data-service ──────────────┼─── Service     │       │
│  │  llm-service ───────────────┼─── Registry    │       │
│  │  memory-service ────────────┘                │       │
│  └─────────────────────┬───────────────────────────┘       │
│                        │                                 │
├────────────────────────┼─────────────────────────────────┤
│                        │                                 │
│  ┌─────────────────────▼─────────────────────────┐       │
│  │                Service Instances              │       │
│  │                                               │       │
│  │  [Pod1] [Pod2] [Pod3] ... [PodN]             │       │
│  │    ↕      ↕      ↕         ↕                 │       │
│  │  Auto-scaling based on metrics               │       │
│  └───────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 **核心组件**

### **1. Kubernetes原生服务发现**

#### **Service配置**
```yaml
# 标准ClusterIP Service
apiVersion: v1
kind: Service
metadata:
  name: analysis-engine-service
  labels:
    app: analysis-engine
    tier: compute
spec:
  selector:
    app: analysis-engine
  ports:
  - name: http
    port: 8005
    targetPort: 8005
    protocol: TCP
  type: ClusterIP
  sessionAffinity: None

---
# Headless Service (用于服务发现)
apiVersion: v1
kind: Service
metadata:
  name: analysis-engine-headless
  labels:
    app: analysis-engine
    type: headless
spec:
  clusterIP: None
  selector:
    app: analysis-engine
  ports:
  - name: http
    port: 8005
    targetPort: 8005
```

#### **EndpointSlice监控**
```yaml
# 自动创建的EndpointSlice
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: analysis-engine-service-abc123
  labels:
    kubernetes.io/service-name: analysis-engine-service
addressType: IPv4
endpoints:
- addresses:
  - "10.244.1.10"
  - "10.244.2.15"
  - "10.244.3.20"
  conditions:
    ready: true
    serving: true
    terminating: false
ports:
- name: http
  port: 8005
  protocol: TCP
```

### **2. 智能服务发现客户端**

#### **核心实现**
```python
import asyncio
import aiohttp
import time
import random
from typing import List, Dict, Optional
from kubernetes import client, config, watch
from dataclasses import dataclass
from enum import Enum

class LoadBalanceAlgorithm(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_RANDOM = "weighted_random"
    HEALTH_AWARE = "health_aware"

@dataclass
class ServiceInstance:
    """服务实例"""
    host: str
    port: int
    weight: int = 1
    healthy: bool = True
    connections: int = 0
    response_time: float = 0.0
    last_check: float = 0.0
    failure_count: int = 0

class SmartServiceDiscovery:
    """智能服务发现客户端"""
    
    def __init__(self, namespace: str = "default", 
                 cache_ttl: int = 30,
                 algorithm: LoadBalanceAlgorithm = LoadBalanceAlgorithm.HEALTH_AWARE):
        self.namespace = namespace
        self.cache_ttl = cache_ttl
        self.algorithm = algorithm
        
        # 初始化K8s客户端
        try:
            config.load_incluster_config()  # Pod内运行
        except:
            config.load_kube_config()  # 本地开发
        
        self.v1 = client.CoreV1Api()
        self.discovery_v1 = client.DiscoveryV1Api()
        
        # 缓存和状态
        self.service_cache: Dict[str, List[ServiceInstance]] = {}
        self.cache_timestamps: Dict[str, float] = {}
        self.circuit_breakers: Dict[str, Dict] = {}
        
        # 监控指标
        self.metrics = {
            "discovery_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "service_calls": 0,
            "failures": 0
        }
    
    async def discover_service_instances(self, service_name: str, 
                                       force_refresh: bool = False) -> List[ServiceInstance]:
        """发现服务实例"""
        self.metrics["discovery_calls"] += 1
        
        # 检查缓存
        if not force_refresh and self._is_cache_valid(service_name):
            self.metrics["cache_hits"] += 1
            return self.service_cache[service_name]
        
        self.metrics["cache_misses"] += 1
        
        try:
            # 从K8s获取EndpointSlice
            endpoint_slices = self.discovery_v1.list_namespaced_endpoint_slice(
                namespace=self.namespace,
                label_selector=f"kubernetes.io/service-name={service_name}"
            )
            
            instances = []
            for slice_obj in endpoint_slices.items:
                for endpoint in slice_obj.endpoints:
                    if endpoint.conditions.ready:
                        for address in endpoint.addresses:
                            for port in slice_obj.ports:
                                instances.append(ServiceInstance(
                                    host=address,
                                    port=port.port,
                                    healthy=True
                                ))
            
            # 更新缓存
            self.service_cache[service_name] = instances
            self.cache_timestamps[service_name] = time.time()
            
            return instances
            
        except Exception as e:
            logger.error(f"服务发现失败 {service_name}: {e}")
            # 返回缓存的实例（如果有）
            return self.service_cache.get(service_name, [])
    
    def _is_cache_valid(self, service_name: str) -> bool:
        """检查缓存是否有效"""
        if service_name not in self.cache_timestamps:
            return False
        
        age = time.time() - self.cache_timestamps[service_name]
        return age < self.cache_ttl
    
    async def select_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """选择服务实例"""
        instances = await self.discover_service_instances(service_name)
        
        # 过滤健康实例
        healthy_instances = [i for i in instances if i.healthy and not self._is_circuit_open(i)]
        
        if not healthy_instances:
            return None
        
        # 根据算法选择实例
        if self.algorithm == LoadBalanceAlgorithm.ROUND_ROBIN:
            return self._round_robin_select(service_name, healthy_instances)
        elif self.algorithm == LoadBalanceAlgorithm.LEAST_CONNECTIONS:
            return min(healthy_instances, key=lambda x: x.connections)
        elif self.algorithm == LoadBalanceAlgorithm.WEIGHTED_RANDOM:
            return self._weighted_random_select(healthy_instances)
        elif self.algorithm == LoadBalanceAlgorithm.HEALTH_AWARE:
            return self._health_aware_select(healthy_instances)
        else:
            return random.choice(healthy_instances)
    
    def _health_aware_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """健康感知选择"""
        def score(instance: ServiceInstance) -> float:
            # 综合评分：响应时间 + 连接数 + 失败率
            time_score = instance.response_time
            conn_score = instance.connections * 0.1
            failure_score = instance.failure_count * 2.0
            
            return time_score + conn_score + failure_score
        
        return min(instances, key=score)
    
    def _weighted_random_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """加权随机选择"""
        weights = [i.weight for i in instances]
        return random.choices(instances, weights=weights)[0]
    
    def _round_robin_select(self, service_name: str, instances: List[ServiceInstance]) -> ServiceInstance:
        """轮询选择"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = {"index": 0}
        
        index = self.circuit_breakers[service_name]["index"]
        selected = instances[index % len(instances)]
        self.circuit_breakers[service_name]["index"] = index + 1
        
        return selected
    
    def _is_circuit_open(self, instance: ServiceInstance) -> bool:
        """检查熔断器状态"""
        # 简单熔断逻辑：连续失败5次则熔断30秒
        if instance.failure_count >= 5:
            if time.time() - instance.last_check < 30:
                return True
            else:
                # 重置熔断器
                instance.failure_count = 0
                return False
        return False
    
    async def call_service(self, service_name: str, path: str = "/", 
                          method: str = "GET", data: Optional[Dict] = None,
                          timeout: int = 30, retries: int = 3) -> Dict:
        """调用服务"""
        self.metrics["service_calls"] += 1
        
        last_exception = None
        
        for attempt in range(retries):
            instance = await self.select_instance(service_name)
            
            if not instance:
                raise Exception(f"没有可用的{service_name}实例")
            
            try:
                # 增加连接计数
                instance.connections += 1
                start_time = time.time()
                
                url = f"http://{instance.host}:{instance.port}{path}"
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                    async with session.request(method, url, json=data) as response:
                        # 记录响应时间
                        instance.response_time = time.time() - start_time
                        instance.last_check = time.time()
                        
                        if response.status == 200:
                            # 成功调用，重置失败计数
                            instance.failure_count = 0
                            result = await response.json()
                            return result
                        else:
                            raise aiohttp.ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=response.status
                            )
                            
            except Exception as e:
                # 记录失败
                instance.failure_count += 1
                instance.last_check = time.time()
                last_exception = e
                
                if attempt < retries - 1:
                    # 指数退避
                    await asyncio.sleep(2 ** attempt)
                
            finally:
                # 减少连接计数
                instance.connections = max(0, instance.connections - 1)
        
        # 所有重试都失败
        self.metrics["failures"] += 1
        raise last_exception or Exception(f"调用{service_name}失败")
    
    async def health_check_loop(self, interval: int = 10):
        """健康检查循环"""
        while True:
            try:
                for service_name, instances in self.service_cache.items():
                    for instance in instances:
                        try:
                            start_time = time.time()
                            url = f"http://{instance.host}:{instance.port}/health"
                            
                            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                                async with session.get(url) as response:
                                    instance.healthy = response.status == 200
                                    instance.response_time = time.time() - start_time
                                    
                        except Exception:
                            instance.healthy = False
                            instance.failure_count += 1
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"健康检查异常: {e}")
                await asyncio.sleep(5)
    
    def get_metrics(self) -> Dict:
        """获取监控指标"""
        cache_hit_rate = (
            self.metrics["cache_hits"] / max(1, self.metrics["discovery_calls"])
        )
        
        failure_rate = (
            self.metrics["failures"] / max(1, self.metrics["service_calls"])
        )
        
        return {
            **self.metrics,
            "cache_hit_rate": cache_hit_rate,
            "failure_rate": failure_rate,
            "cached_services": len(self.service_cache),
            "total_instances": sum(len(instances) for instances in self.service_cache.values())
        }

# 全局服务发现实例
_service_discovery: Optional[SmartServiceDiscovery] = None

def get_service_discovery(namespace: str = "default", 
                         algorithm: LoadBalanceAlgorithm = LoadBalanceAlgorithm.HEALTH_AWARE) -> SmartServiceDiscovery:
    """获取全局服务发现实例"""
    global _service_discovery
    
    if _service_discovery is None:
        _service_discovery = SmartServiceDiscovery(namespace=namespace, algorithm=algorithm)
        # 启动健康检查
        asyncio.create_task(_service_discovery.health_check_loop())
    
    return _service_discovery
```

### **3. 配置管理**

#### **ConfigMap配置**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: service-discovery-config
  namespace: trading-system
data:
  config.yaml: |
    service_discovery:
      # 基础配置
      namespace: trading-system
      cache_ttl: 30
      default_timeout: 30
      max_retries: 3
      
      # 负载均衡配置
      load_balancing:
        algorithm: health_aware  # round_robin, least_connections, weighted_random, health_aware
        health_check:
          enabled: true
          interval: 10
          timeout: 5
          failure_threshold: 3
      
      # 熔断器配置
      circuit_breaker:
        failure_threshold: 5
        recovery_timeout: 30
        half_open_max_calls: 3
      
      # 服务配置
      services:
        analysis-engine:
          service_name: analysis-engine-service
          port: 8005
          health_path: /health
          weight: 1
          timeout: 300  # 分析任务超时时间长
          
        data-service:
          service_name: data-service
          port: 8003
          health_path: /health
          weight: 1
          timeout: 30
          
        llm-service:
          service_name: llm-service
          port: 8004
          health_path: /health
          weight: 1
          timeout: 60
          
        memory-service:
          service_name: memory-service
          port: 8006
          health_path: /health
          weight: 1
          timeout: 30
      
      # 监控配置
      monitoring:
        metrics_enabled: true
        metrics_interval: 60
        log_level: INFO
        
      # 缓存配置
      cache:
        enabled: true
        ttl: 30
        max_size: 1000
        cleanup_interval: 300
```

## 📊 **使用示例**

### **1. 基础使用**
```python
import asyncio
from service_discovery import get_service_discovery, LoadBalanceAlgorithm

async def main():
    # 获取服务发现实例
    sd = get_service_discovery(
        namespace="trading-system",
        algorithm=LoadBalanceAlgorithm.HEALTH_AWARE
    )
    
    # 调用Analysis Engine
    try:
        result = await sd.call_service(
            service_name="analysis-engine",
            path="/api/v1/analysis/submit",
            method="POST",
            data={
                "stock_code": "AAPL",
                "analysis_type": "comprehensive"
            }
        )
        print(f"分析任务提交成功: {result}")
        
    except Exception as e:
        print(f"调用失败: {e}")
    
    # 获取监控指标
    metrics = sd.get_metrics()
    print(f"服务发现指标: {metrics}")

if __name__ == "__main__":
    asyncio.run(main())
```

### **2. 高级使用**
```python
class TradingAgentsClient:
    """TradingAgents客户端"""
    
    def __init__(self, namespace: str = "trading-system"):
        self.sd = get_service_discovery(namespace)
    
    async def submit_analysis(self, stock_code: str, analysis_type: str, priority: str = "normal"):
        """提交分析任务"""
        return await self.sd.call_service(
            service_name="analysis-engine",
            path="/api/v1/analysis/submit",
            method="POST",
            data={
                "stock_code": stock_code,
                "analysis_type": analysis_type
            },
            timeout=300  # 5分钟超时
        )
    
    async def get_stock_data(self, symbol: str, period: str = "1y"):
        """获取股票数据"""
        return await self.sd.call_service(
            service_name="data-service",
            path="/api/v1/data/stock",
            method="GET",
            data={"symbol": symbol, "period": period}
        )
    
    async def search_memory(self, collection: str, query: str):
        """搜索记忆"""
        return await self.sd.call_service(
            service_name="memory-service",
            path="/api/v1/memory/search",
            method="POST",
            data={
                "collection_name": collection,
                "query": query,
                "n_results": 3
            }
        )
    
    async def batch_analysis(self, stock_codes: List[str], max_concurrent: int = 5):
        """批量分析"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_single(code):
            async with semaphore:
                return await self.submit_analysis(code, "comprehensive")
        
        tasks = [analyze_single(code) for code in stock_codes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
```

## 🔄 **部署和运维**

### **1. 部署清单**
```bash
# 部署服务发现配置
kubectl apply -f service-discovery-config.yaml

# 部署服务
kubectl apply -f analysis-engine-service.yaml
kubectl apply -f data-service.yaml
kubectl apply -f llm-service.yaml
kubectl apply -f memory-service.yaml

# 验证服务发现
kubectl get services -n trading-system
kubectl get endpointslices -n trading-system
```

### **2. 监控和告警**
```yaml
# Prometheus监控规则
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: service-discovery-alerts
spec:
  groups:
  - name: service-discovery
    rules:
    - alert: ServiceDiscoveryHighFailureRate
      expr: service_discovery_failure_rate > 0.1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "服务发现失败率过高"
        description: "服务发现失败率 {{ $value }} 超过10%"
    
    - alert: ServiceInstancesLow
      expr: service_discovery_healthy_instances < 2
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "可用服务实例不足"
        description: "服务 {{ $labels.service }} 只有 {{ $value }} 个健康实例"
```

### **3. 故障排除**
```bash
# 检查服务状态
kubectl get services -n trading-system
kubectl describe service analysis-engine-service -n trading-system

# 检查端点
kubectl get endpointslices -n trading-system
kubectl describe endpointslice analysis-engine-service-xxx -n trading-system

# 检查Pod状态
kubectl get pods -l app=analysis-engine -n trading-system
kubectl logs -l app=analysis-engine -n trading-system

# 测试服务连通性
kubectl run test-pod --image=curlimages/curl -it --rm -- /bin/sh
curl http://analysis-engine-service:8005/health
```

## 📈 **性能优化**

### **1. 缓存策略**
- **本地缓存**: 30秒TTL，减少K8s API调用
- **预热缓存**: 启动时预加载常用服务
- **异步更新**: 后台异步更新缓存

### **2. 负载均衡优化**
- **健康感知**: 综合响应时间、连接数、失败率
- **权重调整**: 根据实例性能动态调整权重
- **亲和性**: 优先选择同节点/同区域实例

### **3. 监控指标**
```python
# 关键指标
- service_discovery_calls_total: 服务发现调用次数
- service_discovery_cache_hit_rate: 缓存命中率
- service_discovery_failure_rate: 失败率
- service_call_duration_seconds: 服务调用延迟
- service_instances_healthy: 健康实例数
- circuit_breaker_state: 熔断器状态
```

## 🎯 **最佳实践**

### **1. 服务设计**
- 实现标准的`/health`和`/ready`端点
- 优雅关闭，处理SIGTERM信号
- 合理设置资源限制和请求

### **2. 客户端使用**
- 使用连接池减少连接开销
- 实现指数退避重试策略
- 设置合理的超时时间

### **3. 运维管理**
- 定期检查服务发现指标
- 监控服务实例健康状态
- 及时处理告警和异常

## 🚀 **实施路线图**

### **阶段1: 基础实施 (1-2周)**
```
目标: 实现K8s原生服务发现
任务:
- [ ] 部署K8s Services和EndpointSlices
- [ ] 实现基础服务发现客户端
- [ ] 集成到现有微服务
- [ ] 基础监控和日志

验收标准:
- 所有服务可通过服务名访问
- 服务发现延迟 < 50ms
- 基础负载均衡工作正常
```

### **阶段2: 智能增强 (2-3周)**
```
目标: 添加智能负载均衡和缓存
任务:
- [ ] 实现多种负载均衡算法
- [ ] 添加本地缓存机制
- [ ] 集成健康检查
- [ ] 实现熔断器模式

验收标准:
- 缓存命中率 > 80%
- 健康检查自动故障转移
- 熔断器正确工作
```

### **阶段3: 高级特性 (2-3周)**
```
目标: 完善监控和运维能力
任务:
- [ ] 完整的Prometheus指标
- [ ] Grafana监控面板
- [ ] 告警规则配置
- [ ] 性能优化和调优

验收标准:
- 完整的监控体系
- 自动告警机制
- 性能达到设计目标
```

### **阶段4: 生产就绪 (1-2周)**
```
目标: 生产环境部署和验证
任务:
- [ ] 生产环境部署
- [ ] 压力测试验证
- [ ] 故障演练
- [ ] 文档和培训

验收标准:
- 通过生产环境验证
- 运维团队培训完成
- 应急预案就绪
```

## 📚 **参考资料**

### **相关文档**
- [Kubernetes Service发现官方文档](https://kubernetes.io/docs/concepts/services-networking/service/)
- [EndpointSlice API参考](https://kubernetes.io/docs/reference/kubernetes-api/service-resources/endpoint-slice-v1/)
- [微服务架构设计文档](./microservices-architecture.md)
- [高并发分析架构文档](./concurrent-analysis-architecture.md)

### **最佳实践指南**
- [服务网格vs服务发现选择指南](https://kubernetes.io/blog/2018/11/07/grpc-load-balancing-on-kubernetes-without-tears/)
- [Kubernetes网络故障排除](https://kubernetes.io/docs/tasks/debug-application-cluster/debug-service/)
- [微服务监控最佳实践](https://prometheus.io/docs/practices/naming/)

### **工具和资源**
- [kubectl命令参考](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Prometheus监控配置](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
- [Grafana面板模板](https://grafana.com/grafana/dashboards/)

## 🔧 **附录**

### **A. 完整配置示例**

#### **A.1 Kubernetes Manifests**
```yaml
# 完整的服务配置文件
# 文件: k8s/services/analysis-engine.yaml
apiVersion: v1
kind: Service
metadata:
  name: analysis-engine-service
  namespace: trading-system
  labels:
    app: analysis-engine
    component: compute
    version: v2.0
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
spec:
  selector:
    app: analysis-engine
  ports:
  - name: http
    port: 8005
    targetPort: http
    protocol: TCP
  - name: metrics
    port: 9090
    targetPort: metrics
    protocol: TCP
  type: ClusterIP
  sessionAffinity: None
  publishNotReadyAddresses: false
```

#### **A.2 监控配置**
```yaml
# Prometheus ServiceMonitor
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: service-discovery-monitor
  namespace: trading-system
spec:
  selector:
    matchLabels:
      app: analysis-engine
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### **B. 故障排除清单**

#### **B.1 常见问题**
```
问题: 服务发现返回空列表
排查:
1. 检查Service是否存在: kubectl get svc
2. 检查Selector是否匹配: kubectl describe svc
3. 检查Pod标签: kubectl get pods --show-labels
4. 检查EndpointSlice: kubectl get endpointslices

问题: 负载均衡不均匀
排查:
1. 检查实例健康状态
2. 查看负载均衡算法配置
3. 检查实例权重设置
4. 监控连接数分布

问题: 服务调用超时
排查:
1. 检查网络连通性
2. 查看服务响应时间
3. 检查资源使用情况
4. 验证超时配置
```

#### **B.2 调试命令**
```bash
# 服务发现调试
kubectl get services -n trading-system -o wide
kubectl get endpointslices -n trading-system
kubectl describe endpointslice <name> -n trading-system

# 网络连通性测试
kubectl run debug-pod --image=nicolaka/netshoot -it --rm
nslookup analysis-engine-service.trading-system.svc.cluster.local
curl -v http://analysis-engine-service:8005/health

# 日志查看
kubectl logs -l app=analysis-engine -n trading-system --tail=100
kubectl logs -l app=analysis-engine -n trading-system -f
```

### **C. 性能基准**

#### **C.1 性能目标**
```
服务发现延迟: < 10ms (P99)
缓存命中率: > 90%
服务调用成功率: > 99.9%
故障转移时间: < 30s
负载均衡偏差: < 10%
```

#### **C.2 压力测试**
```python
# 性能测试脚本示例
import asyncio
import time
from service_discovery import get_service_discovery

async def benchmark_service_discovery():
    sd = get_service_discovery()

    # 预热
    for _ in range(100):
        await sd.discover_service_instances("analysis-engine")

    # 性能测试
    start_time = time.time()
    tasks = []

    for _ in range(1000):
        task = sd.discover_service_instances("analysis-engine")
        tasks.append(task)

    await asyncio.gather(*tasks)

    duration = time.time() - start_time
    qps = 1000 / duration

    print(f"QPS: {qps:.2f}")
    print(f"平均延迟: {duration/1000*1000:.2f}ms")

    # 获取指标
    metrics = sd.get_metrics()
    print(f"缓存命中率: {metrics['cache_hit_rate']:.2%}")

if __name__ == "__main__":
    asyncio.run(benchmark_service_discovery())
```

这个服务发现方案为TradingAgents提供了企业级的服务治理能力，支持高可用、高性能的微服务通信！🚀
