# TradingAgents 数据管理系统

## 📋 概述

TradingAgents 数据管理系统采用智能缓存策略和定时任务调度，实现了高效的数据获取、存储和更新机制。

## 🏗️ 架构设计

### 核心组件

1. **Data Service (端口 8002)** - 数据获取和缓存服务
2. **Task Scheduler (端口 8003)** - 定时任务调度服务
3. **Data Manager** - 智能数据管理器
4. **Celery Worker** - 异步任务执行器
5. **Celery Beat** - 定时任务调度器

### 数据流程

```
用户请求 → API Gateway → Data Service → Data Manager → 缓存检查 → 数据源获取 → 缓存更新 → 返回数据
                                                    ↓
Task Scheduler → Celery Beat → Celery Worker → Data Service API → 批量更新
```

## 📊 数据源优先级

### 数据类型和优先级

| 数据类型 | 优先级 | 缓存时间 | 数据源优先级 |
|---------|--------|----------|-------------|
| 股票信息 | LOW | 1天 | Tushare → AKShare → YFinance |
| 股票数据 | MEDIUM | 1小时 | Tushare → AKShare → BaoStock |
| 基本面数据 | LOW | 6小时 | Tushare → AKShare |
| 新闻数据 | HIGH | 30分钟 | FinnHub → AKShare |

### 智能缓存策略

1. **多层缓存**: Redis (快速) + MongoDB (持久)
2. **过期检查**: 自动检查数据是否过期
3. **降级策略**: 数据源失败时使用过期缓存
4. **预热机制**: 提前加载热门股票数据

## ⏰ 定时任务调度

### 任务类型

#### 🔄 数据更新任务

| 任务名称 | 执行频率 | 执行时间 | 描述 |
|---------|---------|----------|------|
| 热门股票数据更新 | 每15分钟 | */15 * * * * | 更新热门股票的实时数据 |
| 历史数据同步 | 每日 | 02:00 | 同步前一交易日的历史数据 |
| 新闻数据更新 | 每30分钟 | */30 * * * * | 获取最新的股票新闻 |
| 基本面数据更新 | 每6小时 | 0 */6 * * * | 更新股票基本面数据 |
| 数据预热 | 每日 | 08:00 | 预热常用股票数据到缓存 |

#### 🧹 维护任务

| 任务名称 | 执行频率 | 执行时间 | 描述 |
|---------|---------|----------|------|
| 过期数据清理 | 每小时 | 0 * * * * | 清理过期的缓存数据 |
| 数据统计报告 | 每日 | 23:00 | 生成数据使用统计报告 |

### 任务队列

- **data_queue**: 数据相关任务
- **analysis_queue**: 分析相关任务  
- **maintenance_queue**: 维护相关任务
- **default**: 默认队列

## 🚀 快速启动

### 方式一：Docker Compose (推荐)

```bash
# Linux/Mac
cd backend
chmod +x scripts/start-microservices.sh
./scripts/start-microservices.sh

# Windows
cd backend
scripts\start-microservices.bat
```

### 方式二：手动启动

1. **启动基础设施**
```bash
docker-compose -f docker-compose.microservices.yml up -d redis mongodb
```

2. **启动微服务**
```bash
# Data Service
cd data-service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002

# Task Scheduler  
cd task-scheduler
python -m uvicorn api.main:app --host 0.0.0.0 --port 8003

# Celery Worker
cd task-scheduler
python start_worker.py

# Celery Beat
cd task-scheduler  
python start_scheduler.py
```

## 📡 API 接口

### Data Service 接口

#### 基础数据接口
- `GET /api/stock/info/{symbol}` - 获取股票信息
- `POST /api/stock/data` - 获取股票价格数据
- `POST /api/stock/fundamentals` - 获取基本面数据
- `POST /api/stock/news` - 获取股票新闻

#### 管理接口 (供 Task Scheduler 调用)
- `POST /api/admin/batch-update` - 批量更新数据
- `POST /api/admin/cleanup-cache` - 清理缓存
- `GET /api/admin/statistics` - 获取数据统计
- `POST /api/admin/preheat-cache` - 预热缓存

### Task Scheduler 接口

#### 手动触发任务
- `POST /api/tasks/data/sync-daily` - 触发每日数据同步
- `POST /api/tasks/data/update-hot-stocks` - 触发热门股票更新
- `POST /api/tasks/data/update-news` - 触发新闻更新
- `POST /api/tasks/data/preheat-cache` - 触发缓存预热
- `POST /api/tasks/data/cleanup-cache` - 触发缓存清理
- `POST /api/tasks/data/custom-update` - 自定义数据更新

#### 任务管理
- `GET /api/tasks/status` - 获取任务状态
- `GET /api/tasks/{task_id}/status` - 获取特定任务状态
- `DELETE /api/tasks/{task_id}` - 取消任务

## 🔧 配置说明

### 环境变量

```bash
# 数据库配置
MONGODB_URL=mongodb://localhost:27017/tradingagents
REDIS_URL=redis://localhost:6379/0

# Celery 配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# 服务地址
DATA_SERVICE_URL=http://localhost:8002
ANALYSIS_ENGINE_URL=http://localhost:8001
```

### 数据源配置

在 `.env` 文件中配置 API 密钥：

```bash
# Tushare
TUSHARE_TOKEN=your_tushare_token

# FinnHub
FINNHUB_API_KEY=your_finnhub_key

# 其他数据源配置...
```

## 📊 监控和管理

### 服务监控

- **Flower**: http://localhost:5555 - Celery 任务监控
- **MongoDB Express**: http://localhost:8081 - MongoDB 管理界面
- **Redis Commander**: http://localhost:8082 - Redis 管理界面

### 日志查看

```bash
# 查看所有服务日志
docker-compose -f docker-compose.microservices.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.microservices.yml logs -f data-service
docker-compose -f docker-compose.microservices.yml logs -f celery-worker
```

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8002/health  # Data Service
curl http://localhost:8003/health  # Task Scheduler

# 检查数据统计
curl http://localhost:8002/api/admin/statistics
```

## 🛠️ 开发和调试

### 添加新的定时任务

1. 在 `task-scheduler/tasks/data_tasks.py` 中添加任务函数
2. 在 `task-scheduler/tasks/schedule_config.py` 中配置调度
3. 在 `task-scheduler/api/main.py` 中添加手动触发接口

### 添加新的数据源

1. 在 `data-service/app/data_manager.py` 中添加数据源
2. 更新数据源优先级配置
3. 添加相应的 API 接口

### 性能优化

1. **缓存策略**: 根据数据更新频率调整缓存时间
2. **任务调度**: 避免高峰期执行重型任务
3. **数据源**: 合理设置请求间隔，避免 API 限制

## 🚨 故障排除

### 常见问题

1. **Redis 连接失败**
   - 检查 Redis 服务是否启动
   - 确认端口和密码配置

2. **MongoDB 连接失败**
   - 检查 MongoDB 服务状态
   - 确认用户名密码和数据库名

3. **Celery 任务不执行**
   - 检查 Celery Worker 是否运行
   - 查看 Celery Beat 调度状态

4. **数据获取失败**
   - 检查 API 密钥配置
   - 确认网络连接和数据源状态

### 重启服务

```bash
# 重启所有服务
docker-compose -f docker-compose.microservices.yml restart

# 重启特定服务
docker-compose -f docker-compose.microservices.yml restart data-service
docker-compose -f docker-compose.microservices.yml restart celery-worker
```

## 📈 扩展性

### 水平扩展

1. **增加 Worker 实例**
```bash
docker-compose -f docker-compose.microservices.yml up -d --scale celery-worker=3
```

2. **数据库分片**
   - MongoDB 分片配置
   - Redis 集群模式

3. **负载均衡**
   - Nginx 反向代理
   - API Gateway 负载均衡

### 垂直扩展

1. **增加资源配置**
2. **优化数据库索引**
3. **调整缓存策略**

---

## 📞 支持

如有问题，请查看：
- 📚 [完整文档](../README.md)
- 🐛 [问题反馈](https://github.com/hsliuping/TradingAgents-CN/issues)
- 💬 [讨论区](https://github.com/hsliuping/TradingAgents-CN/discussions)
