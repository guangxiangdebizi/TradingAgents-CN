# 🛠️ 服务发现实施指南

## 📋 **快速开始**

### **前置条件**
- Kubernetes集群 (v1.20+)
- kubectl配置正确
- Python 3.10+
- 基础的K8s知识

### **5分钟快速部署**

#### **1. 克隆代码**
```bash
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN/backend
```

#### **2. 部署基础服务**
```bash
# 创建命名空间
kubectl create namespace trading-system

# 部署配置
kubectl apply -f k8s/configmaps/service-discovery-config.yaml

# 部署服务
kubectl apply -f k8s/services/
```

#### **3. 验证部署**
```bash
# 检查服务状态
kubectl get services -n trading-system

# 检查端点
kubectl get endpointslices -n trading-system

# 测试服务发现
python scripts/test-service-discovery.py
```

## 🔧 **详细实施步骤**

### **步骤1: 准备Kubernetes环境**

#### **创建命名空间和RBAC**
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: trading-system
  labels:
    name: trading-system

---
# ServiceAccount for service discovery
apiVersion: v1
kind: ServiceAccount
metadata:
  name: service-discovery
  namespace: trading-system

---
# ClusterRole for reading services and endpoints
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: service-discovery-reader
rules:
- apiGroups: [""]
  resources: ["services", "endpoints"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["discovery.k8s.io"]
  resources: ["endpointslices"]
  verbs: ["get", "list", "watch"]

---
# Bind the role to the service account
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: service-discovery-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: service-discovery-reader
subjects:
- kind: ServiceAccount
  name: service-discovery
  namespace: trading-system
```

#### **部署命令**
```bash
kubectl apply -f k8s/namespace.yaml
```

### **步骤2: 配置服务发现**

#### **创建ConfigMap**
```yaml
# k8s/configmaps/service-discovery-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: service-discovery-config
  namespace: trading-system
data:
  config.yaml: |
    service_discovery:
      namespace: trading-system
      cache_ttl: 30
      load_balancing:
        algorithm: health_aware
        health_check:
          enabled: true
          interval: 10
          timeout: 5
      services:
        analysis-engine:
          service_name: analysis-engine-service
          port: 8005
          health_path: /health
        data-service:
          service_name: data-service
          port: 8003
          health_path: /health
        llm-service:
          service_name: llm-service
          port: 8004
          health_path: /health
        memory-service:
          service_name: memory-service
          port: 8006
          health_path: /health
```

### **步骤3: 部署微服务**

#### **Analysis Engine服务**
```yaml
# k8s/services/analysis-engine.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: analysis-engine
  namespace: trading-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: analysis-engine
  template:
    metadata:
      labels:
        app: analysis-engine
    spec:
      serviceAccountName: service-discovery
      containers:
      - name: analysis-engine
        image: tradingagents/analysis-engine:latest
        ports:
        - name: http
          containerPort: 8005
        - name: metrics
          containerPort: 9090
        env:
        - name: NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi

---
apiVersion: v1
kind: Service
metadata:
  name: analysis-engine-service
  namespace: trading-system
  labels:
    app: analysis-engine
spec:
  selector:
    app: analysis-engine
  ports:
  - name: http
    port: 8005
    targetPort: http
  - name: metrics
    port: 9090
    targetPort: metrics
  type: ClusterIP
```

### **步骤4: 集成服务发现客户端**

#### **安装依赖**
```bash
pip install kubernetes aiohttp
```

#### **客户端代码示例**
```python
# client/service_discovery_client.py
import asyncio
from service_discovery import get_service_discovery

class TradingAgentsClient:
    def __init__(self, namespace="trading-system"):
        self.sd = get_service_discovery(namespace)
    
    async def submit_analysis(self, stock_code: str):
        """提交分析任务"""
        try:
            result = await self.sd.call_service(
                service_name="analysis-engine",
                path="/api/v1/analysis/submit",
                method="POST",
                data={
                    "stock_code": stock_code,
                    "analysis_type": "comprehensive"
                }
            )
            return result
        except Exception as e:
            print(f"分析提交失败: {e}")
            raise

# 使用示例
async def main():
    client = TradingAgentsClient()
    
    # 提交分析任务
    result = await client.submit_analysis("AAPL")
    print(f"任务ID: {result['data']['task_id']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### **步骤5: 监控和验证**

#### **部署Prometheus监控**
```yaml
# k8s/monitoring/prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: trading-system
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'service-discovery'
      kubernetes_sd_configs:
      - role: endpoints
        namespaces:
          names:
          - trading-system
      relabel_configs:
      - source_labels: [__meta_kubernetes_service_name]
        action: keep
        regex: .*-service
```

#### **验证脚本**
```python
# scripts/verify-service-discovery.py
import asyncio
import sys
from service_discovery import get_service_discovery

async def verify_service_discovery():
    """验证服务发现功能"""
    print("🔍 验证服务发现功能...")
    
    sd = get_service_discovery("trading-system")
    
    # 测试服务列表
    services = ["analysis-engine", "data-service", "llm-service", "memory-service"]
    
    for service_name in services:
        try:
            print(f"\n📋 测试服务: {service_name}")
            
            # 发现服务实例
            instances = await sd.discover_service_instances(service_name)
            print(f"   发现实例数: {len(instances)}")
            
            if instances:
                # 测试健康检查
                result = await sd.call_service(service_name, "/health")
                print(f"   健康检查: ✅ {result.get('status', 'unknown')}")
            else:
                print(f"   健康检查: ❌ 无可用实例")
                
        except Exception as e:
            print(f"   错误: ❌ {e}")
    
    # 显示指标
    metrics = sd.get_metrics()
    print(f"\n📊 服务发现指标:")
    print(f"   缓存命中率: {metrics['cache_hit_rate']:.2%}")
    print(f"   失败率: {metrics['failure_rate']:.2%}")
    print(f"   缓存服务数: {metrics['cached_services']}")

if __name__ == "__main__":
    asyncio.run(verify_service_discovery())
```

## 🚨 **故障排除**

### **常见问题**

#### **问题1: 服务发现返回空列表**
```bash
# 排查步骤
kubectl get services -n trading-system
kubectl get endpointslices -n trading-system
kubectl describe service analysis-engine-service -n trading-system

# 检查Pod标签
kubectl get pods -n trading-system --show-labels
```

#### **问题2: 权限错误**
```bash
# 检查ServiceAccount
kubectl get serviceaccount -n trading-system
kubectl describe clusterrolebinding service-discovery-binding

# 测试权限
kubectl auth can-i get services --as=system:serviceaccount:trading-system:service-discovery
```

#### **问题3: 网络连通性问题**
```bash
# 创建调试Pod
kubectl run debug --image=nicolaka/netshoot -n trading-system -it --rm

# 在Pod内测试
nslookup analysis-engine-service.trading-system.svc.cluster.local
curl http://analysis-engine-service:8005/health
```

### **调试工具**

#### **服务发现调试脚本**
```python
# scripts/debug-service-discovery.py
import asyncio
from kubernetes import client, config

async def debug_service_discovery():
    """调试服务发现"""
    config.load_kube_config()
    v1 = client.CoreV1Api()
    discovery_v1 = client.DiscoveryV1Api()
    
    namespace = "trading-system"
    service_name = "analysis-engine-service"
    
    print(f"🔍 调试服务: {service_name}")
    
    # 检查Service
    try:
        service = v1.read_namespaced_service(service_name, namespace)
        print(f"✅ Service存在: {service.metadata.name}")
        print(f"   Selector: {service.spec.selector}")
        print(f"   Ports: {[p.port for p in service.spec.ports]}")
    except Exception as e:
        print(f"❌ Service不存在: {e}")
        return
    
    # 检查EndpointSlice
    try:
        endpoint_slices = discovery_v1.list_namespaced_endpoint_slice(
            namespace=namespace,
            label_selector=f"kubernetes.io/service-name={service_name}"
        )
        
        print(f"✅ EndpointSlice数量: {len(endpoint_slices.items)}")
        
        for slice_obj in endpoint_slices.items:
            print(f"   Slice: {slice_obj.metadata.name}")
            for endpoint in slice_obj.endpoints:
                print(f"     地址: {endpoint.addresses}")
                print(f"     就绪: {endpoint.conditions.ready}")
                
    except Exception as e:
        print(f"❌ EndpointSlice错误: {e}")

if __name__ == "__main__":
    asyncio.run(debug_service_discovery())
```

## 📈 **性能优化**

### **缓存优化**
```python
# 配置缓存参数
SERVICE_DISCOVERY_CONFIG = {
    "cache_ttl": 30,        # 缓存30秒
    "preload_services": [   # 预加载常用服务
        "analysis-engine",
        "data-service"
    ],
    "background_refresh": True  # 后台刷新
}
```

### **连接池优化**
```python
# 使用连接池
import aiohttp

connector = aiohttp.TCPConnector(
    limit=100,              # 总连接数限制
    limit_per_host=20,      # 每个主机连接数限制
    keepalive_timeout=30,   # 保持连接时间
    enable_cleanup_closed=True
)

session = aiohttp.ClientSession(connector=connector)
```

## 🎯 **生产部署清单**

### **部署前检查**
- [ ] Kubernetes集群版本 >= 1.20
- [ ] RBAC权限配置正确
- [ ] 网络策略允许服务间通信
- [ ] 监控系统已部署
- [ ] 日志收集已配置

### **部署步骤**
1. [ ] 部署命名空间和RBAC
2. [ ] 部署ConfigMap配置
3. [ ] 部署微服务
4. [ ] 验证服务发现功能
5. [ ] 配置监控和告警
6. [ ] 执行压力测试
7. [ ] 制定应急预案

### **验收标准**
- [ ] 所有服务健康检查通过
- [ ] 服务发现延迟 < 10ms
- [ ] 缓存命中率 > 90%
- [ ] 负载均衡工作正常
- [ ] 监控指标正常
- [ ] 故障转移测试通过

这个实施指南提供了完整的服务发现部署流程，确保您能够快速、正确地实施服务发现方案！🚀
