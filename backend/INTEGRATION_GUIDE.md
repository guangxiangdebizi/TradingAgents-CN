# TradingAgents 微服务集成指南

## 🎯 集成概述

本指南介绍如何将Analysis Engine与Agent Service进行集成，实现多智能体协作分析功能。

## 🏗️ 架构概览

```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│  Analysis       │ ──────────────► │  Agent Service  │
│  Engine         │                │                 │
│  (集成版)        │                │  12种智能体      │
└─────────────────┘                │  工作流管理      │
         │                         │  性能监控        │
         │                         └─────────────────┘
         ▼
┌─────────────────┐
│  Redis          │
│  (状态存储)      │
└─────────────────┘
```

## 🚀 快速开始

### 1. 环境准备

确保已安装以下依赖：
- Docker & Docker Compose
- Python 3.10+
- Redis
- MongoDB (可选)

### 2. 启动服务

```bash
# 进入backend目录
cd backend

# 启动所有服务
docker-compose -f docker-compose.integration.yml up -d

# 查看服务状态
docker-compose -f docker-compose.integration.yml ps
```

### 3. 验证集成

```bash
# 运行集成测试
python test_integration.py

# 或使用Docker运行测试
docker-compose -f docker-compose.integration.yml --profile test up integration-test
```

## 📊 集成功能

### 1. 智能分析策略选择

Analysis Engine会根据请求参数自动选择最适合的分析策略：

- **工作流分析**: 研究深度≥4，选择分析师≥3
- **多智能体协作**: 研究深度≥3，选择分析师≥2  
- **辩论分析**: 选择分析师≥2
- **独立分析**: 其他情况或Agent Service不可用

### 2. 分析类型对比

| 分析类型 | 执行时间 | 分析深度 | 智能体数量 | 适用场景 |
|---------|---------|---------|-----------|---------|
| 独立分析 | 30-60秒 | 基础 | 0 | 快速分析 |
| 辩论分析 | 60-120秒 | 中等 | 2-3 | 观点对比 |
| 多智能体协作 | 120-180秒 | 较深 | 3-5 | 综合分析 |
| 工作流分析 | 180-300秒 | 深度 | 5-8 | 专业分析 |

### 3. API接口

#### 启动分析
```http
POST /api/analysis/start
Content-Type: application/json

{
  "stock_code": "000001",
  "market_type": "A股",
  "research_depth": 3,
  "market_analyst": true,
  "fundamental_analyst": true,
  "news_analyst": false,
  "social_analyst": false
}
```

#### 获取进度
```http
GET /api/analysis/{analysis_id}/progress
```

#### 获取结果
```http
GET /api/analysis/{analysis_id}/result
```

#### 获取分析能力
```http
GET /capabilities
```

## 🔧 配置说明

### Analysis Engine配置

在`backend/shared/config/`中配置：

```json
{
  "analysis_engine": {
    "agent_service_url": "http://localhost:8002",
    "agent_service_timeout": 300,
    "redis": {
      "host": "localhost",
      "port": 6379,
      "db": 0
    }
  }
}
```

### Agent Service配置

Agent Service会自动初始化以下组件：
- 12种专业智能体
- 工作流管理器
- 性能监控器
- 协作引擎
- 辩论引擎
- 共识算法

## 🧪 测试场景

### 1. 基础集成测试

```python
# 测试服务健康状态
await tester.test_services_health()

# 测试分析能力
await tester.test_analysis_capabilities()

# 测试集成分析
await tester.test_integrated_analysis("000001")
```

### 2. 工作流测试

```python
# 直接测试Agent Service工作流
await tester.test_workflow_direct()

# 测试多智能体协作
await tester.test_agent_service_direct()
```

### 3. 性能测试

```bash
# 并发分析测试
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/analysis/start \
    -H "Content-Type: application/json" \
    -d '{"stock_code": "00000'$i'", "research_depth": 3}' &
done
```

## 📈 监控和调试

### 1. 服务监控

```bash
# 查看Analysis Engine健康状态
curl http://localhost:8000/health

# 查看Agent Service健康状态  
curl http://localhost:8002/health

# 查看系统性能指标
curl http://localhost:8002/api/v1/monitoring/system/metrics
```

### 2. 日志查看

```bash
# Analysis Engine日志
docker logs tradingagents-analysis-engine

# Agent Service日志
docker logs tradingagents-agent-service

# 实时日志
docker-compose -f docker-compose.integration.yml logs -f
```

### 3. 调试技巧

1. **检查服务依赖**: 确保Redis和MongoDB正常运行
2. **验证网络连接**: 检查服务间网络连通性
3. **查看详细日志**: 设置LOG_LEVEL=DEBUG获取详细日志
4. **监控资源使用**: 使用性能监控API检查系统负载

## 🔄 故障排除

### 常见问题

1. **Agent Service连接失败**
   - 检查服务是否启动: `docker ps`
   - 验证网络连接: `curl http://localhost:8002/health`
   - 查看日志: `docker logs tradingagents-agent-service`

2. **分析超时**
   - 增加超时时间配置
   - 检查系统资源使用情况
   - 降低分析复杂度

3. **Redis连接问题**
   - 确认Redis服务状态
   - 检查连接配置
   - 验证网络连通性

### 性能优化

1. **资源配置**
   - 调整Docker容器内存限制
   - 优化Redis配置
   - 配置合适的并发数

2. **分析策略**
   - 根据需求选择合适的分析深度
   - 合理配置智能体选择
   - 使用缓存减少重复分析

## 🚀 部署建议

### 开发环境
- 使用Docker Compose快速启动
- 启用详细日志便于调试
- 配置热重载加速开发

### 生产环境
- 使用Kubernetes进行容器编排
- 配置负载均衡和自动扩缩容
- 设置监控告警和日志收集
- 使用外部Redis和MongoDB集群

## 📚 相关文档

- [Agent Service API文档](./agent-service/README.md)
- [Analysis Engine文档](./analysis-engine/README.md)
- [共享模块文档](./shared/README.md)
- [部署指南](./DEPLOYMENT.md)

## 🤝 贡献指南

1. Fork项目仓库
2. 创建功能分支
3. 提交代码变更
4. 运行集成测试
5. 提交Pull Request

---

**注意**: 这是一个集成指南，确保在生产环境中进行充分的测试和验证。
