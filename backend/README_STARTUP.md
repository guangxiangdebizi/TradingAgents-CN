# Backend微服务启动指引

## 📋 **服务概览**

Backend项目包含以下微服务，按推荐启动顺序排列：

| 服务名称 | 端口 | 目录 | 描述 |
|---------|------|------|------|
| Data Service | 8002 | `backend/data-service` | 数据服务（核心依赖） |
| Analysis Engine | 8001 | `backend/analysis-engine` | 分析引擎 |
| Task Scheduler | 8003 | `backend/task-scheduler/api` | 任务调度器 |
| LLM Service | 8004 | `backend/llm-service` | LLM服务 |
| Memory Service | 8006 | `backend/memory-service` | 内存服务 |
| Agent Service | 8008 | `backend/agent-service` | 智能体服务 |
| API Gateway | 8000 | `backend/api-gateway` | API网关（最后启动） |

## 🔧 **环境准备**

### 1. 激活虚拟环境
```bash
# 在项目根目录
.\env\Scripts\activate
```

### 2. 检查配置文件
确保 `backend/.backend_env` 文件存在且配置正确：
```bash
# 检查配置文件
cat backend/.backend_env
```

### 3. 检查数据库服务
确保MongoDB和Redis服务正在运行：
- MongoDB: `localhost:27017`
- Redis: `localhost:6379`

## 🚀 **启动步骤**

### 步骤1: 启动Data Service（必须首先启动）
```bash
cd backend/data-service
python -m app.main
```

**验证启动成功：**
- 看到 `✅ Data Service 启动完成`
- 访问 http://localhost:8002/health 返回200

### 步骤2: 启动Analysis Engine
```bash
# 新开终端窗口
cd backend/analysis-engine
python -m app.main
```

**验证启动成功：**
- 看到 `✅ Analysis Engine 启动完成`
- 访问 http://localhost:8001/health 返回200

### 步骤3: 启动Task Scheduler
```bash
# 新开终端窗口
cd backend/task-scheduler/api
python main.py
```

**验证启动成功：**
- 看到 `✅ Task Scheduler 启动完成`
- 访问 http://localhost:8003/health 返回200

### 步骤4: 启动LLM Service
```bash
# 新开终端窗口
cd backend/llm-service
python -m app.main
```

**验证启动成功：**
- 看到 `✅ LLM Service 启动完成`
- 访问 http://localhost:8004/health 返回200

### 步骤4: 启动Memory Service
```bash
# 新开终端窗口
cd backend/memory-service
python -m app.main
```

**验证启动成功：**
- 看到 `✅ Memory Service 启动完成`
- 访问 http://localhost:8006/health 返回200

### 步骤5: 启动Agent Service
```bash
# 新开终端窗口
cd backend/agent-service
python -m app.main
```

**验证启动成功：**
- 看到 `✅ Agent Service 启动完成`
- 访问 http://localhost:8008/health 返回200

### 步骤6: 启动API Gateway（最后启动）
```bash
# 新开终端窗口
cd backend/api-gateway
python -m app.main
```

**验证启动成功：**
- 看到 `✅ API Gateway 启动完成`
- 访问 http://localhost:8000/health 返回200
- 所有依赖服务状态为 "healthy"

## 🔍 **验证所有服务**

启动完成后，运行验证脚本：
```bash
cd backend
python -c "
import requests
services = [
    ('Data Service', 'http://localhost:8002/health'),
    ('Analysis Engine', 'http://localhost:8001/health'),
    ('LLM Service', 'http://localhost:8004/health'),
    ('Memory Service', 'http://localhost:8006/health'),
    ('Agent Service', 'http://localhost:8008/health'),
    ('API Gateway', 'http://localhost:8000/health')
]

print('🔍 验证所有服务状态:')
for name, url in services:
    try:
        response = requests.get(url, timeout=5)
        status = '✅ 正常' if response.status_code == 200 else f'❌ 错误({response.status_code})'
    except Exception as e:
        status = f'❌ 连接失败'
    print(f'  {name}: {status}')
"
```

## ❌ **常见问题**

### 1. 端口占用错误
```
ERROR: [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。
```

**解决方案：**
- 检查端口是否被占用：`netstat -ano | findstr :8002`
- 关闭占用端口的进程
- 或修改 `.backend_env` 中的端口配置

### 2. 配置文件未找到
```
⚠️ Backend环境文件不存在
```

**解决方案：**
- 确保 `backend/.backend_env` 文件存在
- 检查文件路径和权限

### 3. 数据库连接失败
```
❌ MongoDB 连接失败
❌ Redis 连接失败
```

**解决方案：**
- 启动MongoDB服务
- 启动Redis服务
- 检查 `.backend_env` 中的数据库配置

### 4. 服务间连接失败
```
⚠️ Data Service 连接失败
```

**解决方案：**
- 确保依赖服务已启动
- 检查服务端口配置
- 按推荐顺序启动服务

## 🛠️ **开发模式**

开发时可以使用以下命令启动单个服务：
```bash
# 启动时显示详细日志
cd backend/data-service
python -m app.main --log-level debug

# 或者使用uvicorn直接启动
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

## 🔄 **重启服务**

如果需要重启某个服务：
1. 在对应终端按 `Ctrl+C` 停止服务
2. 重新运行 `python -m app.main`

## 📊 **监控服务**

可以使用以下工具监控服务状态：
- 健康检查：访问各服务的 `/health` 端点
- 日志监控：查看各终端的输出日志
- 性能监控：访问 `/metrics` 端点（如果可用）

---

**注意：** 请按照推荐顺序启动服务，确保依赖关系正确建立。
