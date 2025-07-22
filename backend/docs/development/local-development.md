# TradingAgents 本地开发指南

由于网络环境限制，推荐使用本地开发模式来启动和调试系统。

## 🚀 快速开始

### 1. 启动基础服务（Docker）

```bash
# 启动 MongoDB、Redis、MinIO
cd backend
docker-compose -f docker-compose.simple.yml up -d

# 验证服务状态
docker ps
curl http://localhost:9001  # MinIO 控制台
```

### 2. 本地启动应用服务

#### 准备 Python 环境

```bash
# 确保 Python 3.10+
python --version

# 创建虚拟环境（如果还没有）
python -m venv env

# 激活虚拟环境
# Windows:
env\Scripts\activate
# Linux/Mac:
source env/bin/activate

# 配置国内 pip 源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
```

#### 启动 Data Service

```bash
# 终端 1: Data Service
cd data-service
pip install -r requirements.txt
set PYTHONPATH=%cd%\..\..  # Windows
# export PYTHONPATH=$(pwd)/../..  # Linux/Mac
set MONGODB_URL=mongodb://admin:tradingagents123@localhost:27017/tradingagents?authSource=admin
set REDIS_URL=redis://localhost:6379
python app/main.py
```

#### 启动 Analysis Engine

```bash
# 终端 2: Analysis Engine
cd analysis-engine
pip install -r requirements.txt
set PYTHONPATH=%cd%\..\..  # Windows
set MONGODB_URL=mongodb://admin:tradingagents123@localhost:27017/tradingagents?authSource=admin
set REDIS_URL=redis://localhost:6379
set DATA_SERVICE_URL=http://localhost:8002
python app/main.py
```

#### 启动 API Gateway

```bash
# 终端 3: API Gateway
cd api-gateway
pip install -r requirements.txt
set PYTHONPATH=%cd%\..\..  # Windows
set MONGODB_URL=mongodb://admin:tradingagents123@localhost:27017/tradingagents?authSource=admin
set REDIS_URL=redis://localhost:6379
set ANALYSIS_ENGINE_URL=http://localhost:8001
set DATA_SERVICE_URL=http://localhost:8002
python app/main.py
```

## 🔧 环境变量配置

创建 `.env` 文件（如果还没有）：

```bash
# 复制示例配置
cp .env.example .env
```

编辑 `.env` 文件，添加必要的 API 密钥：

```env
# 必需的 API 密钥
DASHSCOPE_API_KEY=your_dashscope_api_key_here
TUSHARE_TOKEN=your_tushare_token_here

# 可选的 API 密钥
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
FINNHUB_API_KEY=your_finnhub_api_key_here

# 数据库连接（本地开发）
MONGODB_URL=mongodb://admin:tradingagents123@localhost:27017/tradingagents?authSource=admin
REDIS_URL=redis://localhost:6379
```

## 🧪 验证服务

### 检查基础服务

```bash
# MongoDB
docker exec tradingagents-mongodb mongosh --eval "db.hello()"

# Redis
docker exec tradingagents-redis redis-cli ping

# MinIO（浏览器访问）
# http://localhost:9001
# 用户名: admin
# 密码: tradingagents123
```

### 检查应用服务

```bash
# Data Service
curl http://localhost:8002/health

# Analysis Engine
curl http://localhost:8001/health

# API Gateway
curl http://localhost:8000/health
curl http://localhost:8000/docs  # API 文档
```

### 功能测试

```bash
# 测试股票信息查询
curl http://localhost:8000/api/stock/info/000858

# 测试分析任务
curl -X POST http://localhost:8000/api/analysis/start \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "000858",
    "market_type": "A股",
    "research_depth": 3
  }'
```

## 🔍 调试技巧

### 1. 查看日志

应用服务的日志直接在终端显示，可以实时查看错误信息。

### 2. 调试模式

在启动应用时添加调试参数：

```bash
# 启用调试模式
set DEBUG=true
set LOG_LEVEL=DEBUG
python app/main.py
```

### 3. 代码热重载

使用 uvicorn 的 reload 功能：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### 4. 数据库调试

```bash
# 连接 MongoDB
docker exec -it tradingagents-mongodb mongosh
use tradingagents
show collections
db.stock_info.find().limit(5)

# 连接 Redis
docker exec -it tradingagents-redis redis-cli
keys *
get stock_info:000858
```

## 🛠️ 常见问题

### 1. 模块导入错误

```bash
ModuleNotFoundError: No module named 'backend'
```

**解决方案：**
```bash
# 确保设置了正确的 PYTHONPATH
set PYTHONPATH=%cd%\..\..  # Windows
export PYTHONPATH=$(pwd)/../..  # Linux/Mac
```

### 2. 数据库连接失败

```bash
pymongo.errors.ServerSelectionTimeoutError
```

**解决方案：**
```bash
# 检查 Docker 服务是否运行
docker ps

# 重启数据库服务
docker-compose -f docker-compose.simple.yml restart mongodb
```

### 3. 端口被占用

```bash
OSError: [Errno 48] Address already in use
```

**解决方案：**
```bash
# 查找占用端口的进程
netstat -ano | findstr :8002  # Windows
lsof -i :8002  # Linux/Mac

# 停止进程或使用其他端口
```

### 4. pip 安装失败

**解决方案：**
```bash
# 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ package_name

# 或者配置永久镜像源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
```

## 📊 性能优化

### 1. 减少依赖

如果某些包安装困难，可以临时注释掉 requirements.txt 中的非必需依赖。

### 2. 使用缓存

```bash
# 启用 pip 缓存
pip install --cache-dir ./pip-cache -r requirements.txt
```

### 3. 离线安装

```bash
# 下载包到本地
pip download -r requirements.txt -d ./packages

# 离线安装
pip install --find-links ./packages -r requirements.txt --no-index
```

## 🎯 开发工作流

### 1. 日常开发

```bash
# 1. 启动基础服务
docker-compose -f docker-compose.simple.yml up -d

# 2. 激活虚拟环境
env\Scripts\activate

# 3. 启动需要的应用服务
cd data-service && python app/main.py

# 4. 开发和测试
# 修改代码，服务会自动重载（如果使用 --reload）

# 5. 停止服务
# Ctrl+C 停止应用服务
docker-compose -f docker-compose.simple.yml down  # 停止基础服务
```

### 2. 测试流程

```bash
# 1. 运行单元测试
python -m pytest tests/

# 2. 运行集成测试
python scripts/test-api.py

# 3. 手动测试
curl http://localhost:8000/health
```

## 🚀 部署准备

当本地开发完成后，可以：

1. **构建 Docker 镜像**（网络条件好时）
2. **推送到私有镜像仓库**
3. **在生产环境拉取部署**

---

💡 **提示**: 本地开发模式可以避免网络问题，提高开发效率。基础服务使用 Docker，应用服务本地运行，既保证了环境一致性，又便于调试。
