# TradingAgents Backend 微服务

基于 FastAPI 的微服务架构，为 TradingAgents-CN 前端提供 REST API 服务。

## 🏗️ 架构概览

```
Frontend (Vue 3) → API Gateway → Microservices
                                    ├── Analysis Engine
                                    ├── Data Service
                                    └── Task Manager (Phase 2)
```

## 📦 服务列表

### Phase 1 核心服务

| 服务名称 | 端口 | 描述 |
|---------|------|------|
| **API Gateway** | 8000 | 统一入口，路由和认证 |
| **Analysis Engine** | 8001 | 股票分析和AI模型调用 |
| **Data Service** | 8002 | 数据获取和缓存 |

### Phase 2 扩展服务（规划中）

| 服务名称 | 端口 | 描述 |
|---------|------|------|
| **Task Manager** | 8003 | 任务调度和监控 |
| **Report Service** | 8004 | 报告生成和导出 |
| **Config Service** | 8005 | 配置管理 |

## 🚀 快速开始

### 1. 环境准备

```bash
# 复制环境变量配置
cp .env.example .env

# 编辑配置文件，填入API密钥
vim .env
```

### 2. 使用 Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 本地开发模式

```bash
# 启动 Redis
docker run -d -p 6379:6379 redis:7-alpine

# 安装依赖并启动各服务
cd data-service && pip install -r requirements.txt && python app/main.py &
cd analysis-engine && pip install -r requirements.txt && python app/main.py &
cd api-gateway && pip install -r requirements.txt && python app/main.py &
```

## 📡 API 接口

### 健康检查

```bash
# 检查所有服务状态
curl http://localhost:8000/health
```

### 分析接口

```bash
# 开始分析
curl -X POST http://localhost:8000/api/analysis/start \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "000858",
    "market_type": "A股",
    "research_depth": 3,
    "market_analyst": true,
    "fundamental_analyst": true
  }'

# 查询进度
curl http://localhost:8000/api/analysis/{analysis_id}/progress

# 获取结果
curl http://localhost:8000/api/analysis/{analysis_id}/result
```

### 数据接口

```bash
# 获取股票信息
curl http://localhost:8000/api/stock/info/000858

# 获取历史数据
curl -X POST http://localhost:8000/api/stock/data \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "000858",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'
```

## 🔧 开发指南

### 添加新的API接口

1. **在对应服务中添加路由**
2. **在 API Gateway 中添加转发规则**
3. **更新共享模型（如需要）**
4. **编写测试用例**

### 服务间通信

使用 `BaseServiceClient` 进行服务间通信：

```python
from backend.shared.clients.base import BaseServiceClient

# 创建客户端
client = BaseServiceClient("data_service")

# 发送请求
response = await client.get("/api/stock/info/000858")
```

### 添加新的数据模型

在 `backend/shared/models/` 中定义：

```python
from pydantic import BaseModel, Field

class NewModel(BaseModel):
    field1: str = Field(..., description="字段描述")
    field2: int = Field(default=0, description="字段描述")
```

## 🐳 Docker 部署

### 构建镜像

```bash
# 构建所有服务镜像
docker-compose build

# 构建单个服务
docker-compose build api-gateway
```

### 生产环境部署

```bash
# 使用生产配置
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📊 监控和日志

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api-gateway
```

### 健康检查

每个服务都提供 `/health` 端点用于健康检查。

## 🔍 故障排除

### 常见问题

1. **服务启动失败**
   - 检查端口是否被占用
   - 确认环境变量配置正确
   - 查看服务日志

2. **Redis 连接失败**
   - 确认 Redis 服务正在运行
   - 检查 `REDIS_URL` 配置

3. **服务间通信失败**
   - 确认所有服务都已启动
   - 检查网络配置
   - 查看服务发现配置

### 调试模式

```bash
# 启用调试模式
export DEBUG=true
export LOG_LEVEL=DEBUG

# 重启服务
docker-compose restart
```

## 📚 相关文档

- [API 接口文档](http://localhost:8000/docs) - FastAPI 自动生成
- [前端对接指南](../frontend/README.md)
- [部署指南](./docs/deployment.md)
- [开发规范](./docs/development.md)
