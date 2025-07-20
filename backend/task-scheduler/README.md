# TradingAgents 定时任务系统

基于 Celery 的分布式定时任务系统，为 TradingAgents 提供数据同步、分析计算、系统维护等定时任务功能。

## 🏗️ 系统架构

```
定时任务系统
├── Celery Beat     # 定时任务调度器
├── Celery Worker   # 任务执行器
├── Redis           # 消息队列和结果存储
├── Flower          # 任务监控界面
└── Task API        # 任务管理接口
```

## 📋 任务类型

### 🔄 数据同步任务
- **每日股票数据拉取** - 交易日 16:30
- **实时价格更新** - 交易时间每5分钟
- **财务数据同步** - 每周一 02:00
- **新闻数据抓取** - 每小时整点

### 📊 分析任务
- **技术指标计算** - 每日 17:00
- **市场情绪分析** - 每日 18:00
- **风险评估更新** - 每周日 03:00
- **热门股票分析** - 每日 19:00

### 🧹 维护任务
- **数据清理** - 每周日 01:00
- **缓存刷新** - 每小时30分
- **日志归档** - 每日 00:30
- **数据库备份** - 每日 02:00
- **健康检查** - 每10分钟

### 📄 报告任务
- **每日市场报告** - 每日 20:00
- **每周投资组合报告** - 周日 21:00

## 🚀 快速开始

### 1. 使用 Docker Compose（推荐）

```bash
# 启动完整系统
cd backend
docker-compose up -d

# 查看任务状态
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat
```

### 2. 本地开发模式

```bash
# 安装依赖
cd backend/task-scheduler
pip install -r requirements.txt

# 启动 Redis
docker run -d -p 6379:6379 redis:7-alpine

# 启动 Worker
celery -A tasks.celery_app worker --loglevel=info

# 启动 Beat（新终端）
celery -A tasks.celery_app beat --loglevel=info

# 启动 Flower（新终端）
celery -A tasks.celery_app flower --port=5555

# 启动任务管理 API（新终端）
python api/main.py
```

### 3. 使用启动脚本

```bash
# Linux/Mac
chmod +x backend/scripts/start-scheduler.sh
./backend/scripts/start-scheduler.sh

# Windows
# 使用 Docker Compose 方式
```

## 🌐 访问界面

| 服务 | 地址 | 描述 |
|------|------|------|
| **Flower 监控** | http://localhost:5555 | 任务执行监控 |
| **任务管理 API** | http://localhost:8003 | 任务管理接口 |
| **API 文档** | http://localhost:8003/docs | 接口文档 |

## 📡 API 接口

### 任务状态查询

```bash
# 获取任务系统状态
curl http://localhost:8003/api/tasks/status

# 获取定时任务列表
curl http://localhost:8003/api/tasks/scheduled

# 获取任务执行历史
curl http://localhost:8003/api/tasks/history
```

### 手动执行任务

```bash
# 手动同步每日数据
curl -X POST http://localhost:8003/api/tasks/data/sync-daily \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["000858", "600519"], "date": "2025-01-20"}'

# 批量股票分析
curl -X POST http://localhost:8003/api/tasks/analysis/batch \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["000858", "600519"],
    "config": {
      "llm_provider": "dashscope",
      "research_depth": 3
    }
  }'

# 生成每日报告
curl -X POST http://localhost:8003/api/tasks/reports/daily \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-01-20"}'
```

### 查询任务结果

```bash
# 获取任务执行结果
curl http://localhost:8003/api/tasks/{task_id}/result

# 获取任务执行指标
curl http://localhost:8003/api/tasks/metrics
```

## ⚙️ 配置说明

### 环境变量

```bash
# Celery 配置
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# 数据库配置
MONGODB_URL=mongodb://admin:password@mongodb:27017/tradingagents?authSource=admin
REDIS_URL=redis://redis:6379

# API 密钥
DASHSCOPE_API_KEY=your_api_key
DEEPSEEK_API_KEY=your_api_key
TUSHARE_TOKEN=your_token
```

### 定时任务配置

定时任务在 `tasks/celery_app.py` 中的 `beat_schedule` 配置：

```python
'sync-daily-stock-data': {
    'task': 'tasks.data_tasks.sync_daily_stock_data',
    'schedule': crontab(hour=16, minute=30),  # 16:30
    'options': {'queue': 'data'}
}
```

### 任务队列配置

- **data** - 数据同步任务
- **analysis** - 分析计算任务  
- **maintenance** - 系统维护任务

## 🔧 开发指南

### 添加新的定时任务

1. **创建任务函数**

```python
# tasks/my_tasks.py
from tasks.celery_app import celery_app

@celery_app.task(bind=True, name='tasks.my_tasks.my_new_task')
def my_new_task(self, param1, param2):
    """新的定时任务"""
    try:
        # 任务逻辑
        result = do_something(param1, param2)
        return result
    except Exception as e:
        logger.error(f"任务执行失败: {e}")
        raise
```

2. **添加定时配置**

```python
# tasks/celery_app.py
beat_schedule = {
    'my-new-task': {
        'task': 'tasks.my_tasks.my_new_task',
        'schedule': crontab(hour=10, minute=0),  # 每日10:00
        'options': {'queue': 'my_queue'}
    }
}
```

3. **注册任务模块**

```python
# tasks/celery_app.py
celery_app.autodiscover_tasks([
    'tasks.data_tasks',
    'tasks.analysis_tasks',
    'tasks.maintenance_tasks',
    'tasks.report_tasks',
    'tasks.my_tasks'  # 新增
])
```

### 任务最佳实践

1. **错误处理**
   - 使用 try-catch 包装任务逻辑
   - 记录详细的错误日志
   - 设置合理的重试策略

2. **进度跟踪**
   - 使用 `self.update_state()` 更新任务进度
   - 提供有意义的状态信息

3. **资源管理**
   - 及时释放数据库连接
   - 避免内存泄漏
   - 设置任务超时时间

## 📊 监控和调试

### Flower 监控界面

访问 http://localhost:5555 查看：
- 任务执行状态
- Worker 状态
- 队列长度
- 执行时间统计

### 命令行工具

```bash
# 查看活跃任务
celery -A tasks.celery_app inspect active

# 查看已注册任务
celery -A tasks.celery_app inspect registered

# 查看 Worker 统计
celery -A tasks.celery_app inspect stats

# 清空队列
celery -A tasks.celery_app purge

# 重启 Worker
celery -A tasks.celery_app control shutdown
```

### 日志查看

```bash
# Docker 环境
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat

# 本地环境
tail -f /var/log/celery/worker.log
tail -f /var/log/celery/beat.log
```

## 🔍 故障排除

### 常见问题

1. **任务不执行**
   - 检查 Celery Beat 是否运行
   - 确认任务时间配置正确
   - 查看 Worker 日志

2. **任务执行失败**
   - 检查任务代码逻辑
   - 确认依赖服务可用
   - 查看错误日志

3. **Redis 连接失败**
   - 确认 Redis 服务运行
   - 检查连接配置
   - 验证网络连通性

### 性能优化

1. **Worker 配置**
   - 调整并发数量
   - 设置合理的预取数量
   - 使用多个队列分离任务

2. **任务优化**
   - 避免长时间运行的任务
   - 使用批处理减少数据库连接
   - 合理使用缓存

## 📚 相关文档

- [Celery 官方文档](https://docs.celeryproject.org/)
- [Redis 文档](https://redis.io/documentation)
- [Flower 文档](https://flower.readthedocs.io/)
- [Crontab 表达式](https://crontab.guru/)
