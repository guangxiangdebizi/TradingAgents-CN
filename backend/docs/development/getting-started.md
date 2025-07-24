# TradingAgents 后端系统 - 启动和调试指南

本文档将指导您如何启动、调试和测试 TradingAgents 后端微服务系统。

## 📋 系统概览

### 🏗️ 架构组件

```
TradingAgents 后端系统
├── API Gateway (8000)      # 统一入口
├── Analysis Engine (8001)  # 分析引擎
├── Data Service (8002)     # 数据服务
├── Task Scheduler (8003)   # 任务管理
├── MongoDB (27017)         # 主数据库
├── Redis (6379)           # 缓存和消息队列
├── MinIO (9000/9001)      # 对象存储
├── Celery Worker          # 任务执行器
├── Celery Beat            # 定时调度器
└── Flower (5555)          # 任务监控
```

### 📊 端口分配

| 服务 | 端口 | 用途 |
|------|------|------|
| API Gateway | 8000 | 前端统一入口 |
| Analysis Engine | 8001 | 股票分析服务 |
| Data Service | 8002 | 数据获取服务 |
| Task API | 8003 | 任务管理接口 |
| Flower | 5555 | 任务监控界面 |
| MongoDB | 27017 | 数据库 |
| Redis | 6379 | 缓存/消息队列 |
| MinIO | 9000 | 对象存储 |
| MinIO Console | 9001 | 存储管理界面 |

## 🚀 快速启动

### 方式一：Docker Compose（推荐）

#### 1. 环境准备

```bash
# 克隆项目（如果还没有）
git clone https://github.com/your-repo/TradingAgents-CN.git
cd TradingAgents-CN

# 进入后端目录
cd backend

# 复制环境变量配置
cp .backend_env.example .backend_env

# 编辑配置文件，填入您的API密钥
vim .backend_env  # 或使用其他编辑器
```

#### 2. 配置 API 密钥

编辑 `.backend_env` 文件，填入必要的API密钥：

```bash
# 必填项
DASHSCOPE_API_KEY=your_dashscope_api_key_here
TUSHARE_TOKEN=your_tushare_token_here

# 可选项
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
FINNHUB_API_KEY=your_finnhub_api_key_here
```

#### 3. 启动系统

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看启动日志
docker-compose logs -f
```

#### 4. 验证启动

```bash
# 等待服务启动（约30秒）
sleep 30

# 检查服务健康状态
curl http://localhost:8000/health  # API Gateway
curl http://localhost:8001/health  # Analysis Engine
curl http://localhost:8002/health  # Data Service
curl http://localhost:8003/health  # Task API
```

### 方式二：本地开发模式

#### 1. 环境准备

```bash
# 确保Python 3.10+
python --version

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r shared/requirements.txt
```

#### 2. 启动基础服务

```bash
# 启动 MongoDB
docker run -d --name tradingagents-mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=tradingagents123 \
  mongo:7

# 启动 Redis
docker run -d --name tradingagents-redis \
  -p 6379:6379 \
  redis:7-alpine

# 启动 MinIO
docker run -d --name tradingagents-minio \
  -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=admin \
  -e MINIO_ROOT_PASSWORD=tradingagents123 \
  minio/minio server /data --console-address ":9001"
```

#### 3. 启动微服务

```bash
# 终端1: 启动 Data Service
cd data-service
pip install -r requirements.txt
python app/main.py

# 终端2: 启动 Analysis Engine
cd analysis-engine
pip install -r requirements.txt
python app/main.py

# 终端3: 启动 API Gateway
cd api-gateway
pip install -r requirements.txt
python app/main.py

# 终端4: 启动 Celery Worker
cd task-scheduler
pip install -r requirements.txt
celery -A tasks.celery_app worker --loglevel=info

# 终端5: 启动 Celery Beat
cd task-scheduler
celery -A tasks.celery_app beat --loglevel=info

# 终端6: 启动 Flower
cd task-scheduler
celery -A tasks.celery_app flower --port=5555
```

## 🔍 系统验证

### 1. 健康检查

```bash
# 检查所有服务健康状态
curl http://localhost:8000/health

# 预期响应
{
  "service_name": "api-gateway",
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "analysis_engine": "healthy",
    "data_service": "healthy"
  }
}
```

### 2. 功能测试

```bash
# 测试股票信息查询
curl http://localhost:8000/api/stock/info/000858

# 测试分析任务提交
curl -X POST http://localhost:8000/api/analysis/start \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "000858",
    "market_type": "A股",
    "research_depth": 3,
    "market_analyst": true,
    "fundamental_analyst": true
  }'
```

### 3. 运行测试脚本

```bash
# 运行API测试
python scripts/test-api.py

# 运行MongoDB性能测试
python scripts/test-mongodb-performance.py
```

## 🌐 访问界面

启动成功后，您可以访问以下界面：

| 界面 | 地址 | 用途 |
|------|------|------|
| **API 文档** | http://localhost:8000/docs | FastAPI 自动生成的接口文档 |
| **Flower 监控** | http://localhost:5555 | Celery 任务监控界面 |
| **MinIO 控制台** | http://localhost:9001 | 对象存储管理界面 |

### API 文档界面

访问 http://localhost:8000/docs 可以看到：
- 所有API接口列表
- 接口参数说明
- 在线测试功能
- 响应示例

### Flower 任务监控

访问 http://localhost:5555 可以看到：
- 实时任务执行状态
- Worker 状态监控
- 任务执行历史
- 队列长度统计

## 🐛 调试指南

### 1. 查看日志

#### Docker 环境

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api-gateway
docker-compose logs -f analysis-engine
docker-compose logs -f data-service
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat

# 查看最近100行日志
docker-compose logs --tail=100 api-gateway
```

#### 本地环境

```bash
# 服务日志直接在终端显示
# 可以调整日志级别
export LOG_LEVEL=DEBUG
python app/main.py
```

### 2. 数据库调试

#### MongoDB

```bash
# 连接到MongoDB
docker exec -it tradingagents-mongodb mongosh

# 使用数据库
use tradingagents

# 查看集合
show collections

# 查询数据
db.stock_info.find().limit(5)
db.analysis_results.find().sort({created_at: -1}).limit(5)
```

#### Redis

```bash
# 连接到Redis
docker exec -it tradingagents-redis redis-cli

# 查看所有键
KEYS *

# 查看特定键
GET stock_info:000858
HGETALL analysis_progress:some-id
```

### 3. 任务调试

#### 查看任务状态

```bash
# 查看活跃任务
celery -A tasks.celery_app inspect active

# 查看已注册任务
celery -A tasks.celery_app inspect registered

# 查看Worker统计
celery -A tasks.celery_app inspect stats
```

#### 手动执行任务

```bash
# 手动执行数据同步任务
curl -X POST http://localhost:8003/api/tasks/data/sync-daily \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["000858"], "date": "2025-01-20"}'

# 查看任务结果
curl http://localhost:8003/api/tasks/{task_id}/result
```

### 4. 性能调试

#### 监控资源使用

```bash
# 查看容器资源使用
docker stats

# 查看特定容器资源
docker stats tradingagents-api-gateway
```

#### 数据库性能

```bash
# MongoDB 性能测试
python scripts/test-mongodb-performance.py

# 查看MongoDB状态
docker exec tradingagents-mongodb mongosh --eval "db.serverStatus()"
```

## ❌ 常见问题排查

### 1. 服务启动失败

**问题：** 容器启动失败
```bash
# 查看详细错误
docker-compose logs service-name

# 常见原因：
# - 端口被占用
# - 环境变量未配置
# - 依赖服务未启动
```

**解决方案：**
```bash
# 检查端口占用
netstat -tulpn | grep :8000

# 停止占用端口的进程
sudo kill -9 PID

# 重新启动
docker-compose up -d
```

### 2. API 调用失败

**问题：** 接口返回500错误
```bash
# 查看API Gateway日志
docker-compose logs -f api-gateway

# 查看后端服务日志
docker-compose logs -f analysis-engine
docker-compose logs -f data-service
```

**解决方案：**
```bash
# 检查服务健康状态
curl http://localhost:8000/health

# 检查环境变量配置
docker-compose exec api-gateway env | grep API_KEY
```

### 3. 数据库连接失败

**问题：** MongoDB/Redis 连接失败
```bash
# 检查数据库服务状态
docker-compose ps mongodb redis

# 测试连接
docker exec tradingagents-mongodb mongosh --eval "db.hello()"
docker exec tradingagents-redis redis-cli ping
```

**解决方案：**
```bash
# 重启数据库服务
docker-compose restart mongodb redis

# 检查网络连接
docker network ls
docker network inspect backend_tradingagents-network
```

### 4. 任务执行失败

**问题：** Celery 任务不执行或失败
```bash
# 检查Worker状态
docker-compose logs -f celery-worker

# 检查Beat调度器
docker-compose logs -f celery-beat

# 查看Flower监控
open http://localhost:5555
```

**解决方案：**
```bash
# 重启任务服务
docker-compose restart celery-worker celery-beat

# 清空任务队列
docker exec tradingagents-redis redis-cli FLUSHDB
```

## 🔧 开发技巧

### 1. 热重载开发

```bash
# 使用开发模式启动（支持代码热重载）
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 或者本地开发模式
export DEBUG=true
python app/main.py
```

### 2. 调试模式

```bash
# 启用调试日志
export LOG_LEVEL=DEBUG

# 启用详细错误信息
export DEBUG=true

# 禁用缓存（开发时）
export DISABLE_CACHE=true
```

### 3. 数据重置

```bash
# 清空所有数据（谨慎使用）
docker-compose down -v

# 重新初始化
docker-compose up -d
```

## 📚 下一步

系统启动成功后，您可以：

1. **前端对接** - 启动前端项目，连接到后端API
2. **数据配置** - 配置数据源API密钥，开始数据同步
3. **任务调度** - 设置定时任务，自动化数据处理
4. **监控告警** - 配置监控和告警系统
5. **生产部署** - 准备Kubernetes部署配置

## 🆘 获取帮助

如果遇到问题：

1. **查看日志** - 首先查看相关服务的日志
2. **检查配置** - 确认环境变量和配置正确
3. **测试连接** - 验证网络和数据库连接
4. **重启服务** - 尝试重启相关服务
5. **查看文档** - 参考各组件的官方文档

---

🎉 **恭喜！** 您已经成功启动了 TradingAgents 后端系统！
