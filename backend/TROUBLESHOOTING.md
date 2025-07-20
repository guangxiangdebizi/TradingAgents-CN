# TradingAgents 故障排除指南

本文档提供常见问题的解决方案和调试技巧。

## 🔧 快速诊断工具

### 自动诊断脚本

```bash
# 运行完整系统诊断
python scripts/debug-tools.py

# 只检查服务健康状态
python scripts/debug-tools.py --action health

# 只测试API接口
python scripts/debug-tools.py --action api

# 查看特定服务日志
python scripts/debug-tools.py --action logs --service api-gateway --lines 100
```

### 手动检查命令

```bash
# 检查容器状态
docker-compose ps

# 查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api-gateway

# 检查网络连接
docker network ls
docker network inspect backend_tradingagents-network
```

## ❌ 常见问题及解决方案

### 1. 🚀 启动问题

#### 问题：容器启动失败

**症状：**
```bash
docker-compose up -d
# 某些容器显示 "Exited (1)"
```

**诊断：**
```bash
# 查看失败容器的日志
docker-compose logs container-name

# 查看容器详细信息
docker inspect container-name
```

**常见原因及解决方案：**

1. **端口被占用**
   ```bash
   # 查找占用端口的进程
   netstat -tulpn | grep :8000
   # 或 Windows
   netstat -ano | findstr :8000
   
   # 停止占用进程
   sudo kill -9 PID
   # 或 Windows
   taskkill /PID PID /F
   ```

2. **环境变量未配置**
   ```bash
   # 检查 .env 文件是否存在
   ls -la .env
   
   # 复制示例配置
   cp .env.example .env
   
   # 编辑配置文件
   vim .env
   ```

3. **Docker资源不足**
   ```bash
   # 清理未使用的资源
   docker system prune -f
   
   # 增加Docker内存限制（Docker Desktop设置）
   # 推荐至少4GB内存
   ```

#### 问题：MongoDB 初始化失败

**症状：**
```
tradingagents-mongodb | Error: Authentication failed
```

**解决方案：**
```bash
# 停止服务并清理数据卷
docker-compose down -v

# 重新启动
docker-compose up -d mongodb

# 等待MongoDB完全启动
sleep 30

# 检查MongoDB状态
docker exec tradingagents-mongodb mongosh --eval "db.hello()"
```

### 2. 🌐 网络连接问题

#### 问题：服务间无法通信

**症状：**
```
Connection refused to http://analysis-engine:8001
```

**诊断：**
```bash
# 检查网络配置
docker network inspect backend_tradingagents-network

# 测试容器间连接
docker exec tradingagents-api-gateway ping analysis-engine
```

**解决方案：**
```bash
# 重新创建网络
docker-compose down
docker network prune -f
docker-compose up -d
```

#### 问题：外部API无法访问

**症状：**
```
curl: (7) Failed to connect to localhost port 8000
```

**解决方案：**
```bash
# 检查容器是否运行
docker-compose ps

# 检查端口映射
docker port tradingagents-api-gateway

# 检查防火墙设置
sudo ufw status  # Linux
# 或检查Windows防火墙设置
```

### 3. 💾 数据库问题

#### 问题：MongoDB 连接失败

**症状：**
```
pymongo.errors.ServerSelectionTimeoutError
```

**诊断：**
```bash
# 检查MongoDB容器状态
docker-compose ps mongodb

# 测试MongoDB连接
docker exec tradingagents-mongodb mongosh --eval "db.hello()"

# 检查MongoDB日志
docker-compose logs mongodb
```

**解决方案：**
```bash
# 重启MongoDB
docker-compose restart mongodb

# 如果持续失败，重新初始化
docker-compose down
docker volume rm backend_mongodb_data
docker-compose up -d mongodb
```

#### 问题：Redis 连接失败

**症状：**
```
redis.exceptions.ConnectionError
```

**解决方案：**
```bash
# 测试Redis连接
docker exec tradingagents-redis redis-cli ping

# 重启Redis
docker-compose restart redis

# 检查Redis配置
docker exec tradingagents-redis redis-cli CONFIG GET "*"
```

### 4. 🔑 API密钥问题

#### 问题：API调用失败

**症状：**
```
{"error": "API key not configured"}
```

**解决方案：**
```bash
# 检查环境变量
docker-compose exec api-gateway env | grep API_KEY

# 更新 .env 文件
vim .env

# 重启服务使配置生效
docker-compose restart
```

#### 问题：数据获取失败

**症状：**
```
{"error": "Tushare token invalid"}
```

**解决方案：**
1. 验证API密钥有效性
2. 检查API配额是否用完
3. 确认网络连接正常

### 5. 📊 性能问题

#### 问题：API响应缓慢

**诊断：**
```bash
# 运行性能测试
python scripts/debug-tools.py --action perf

# 检查容器资源使用
docker stats

# 查看系统负载
top  # Linux
# 或任务管理器 (Windows)
```

**解决方案：**
```bash
# 增加Worker并发数
# 编辑 docker-compose.yml
# celery-worker:
#   command: celery -A tasks.celery_app worker --concurrency=8

# 优化数据库连接池
# 编辑服务配置，增加连接池大小

# 启用Redis缓存
# 确保Redis正常运行并配置正确
```

#### 问题：内存使用过高

**解决方案：**
```bash
# 限制容器内存使用
# 在 docker-compose.yml 中添加：
# deploy:
#   resources:
#     limits:
#       memory: 1G

# 清理缓存
docker exec tradingagents-redis redis-cli FLUSHDB

# 重启服务
docker-compose restart
```

### 6. 🕐 定时任务问题

#### 问题：定时任务不执行

**诊断：**
```bash
# 检查Celery Beat状态
docker-compose logs celery-beat

# 检查Celery Worker状态
docker-compose logs celery-worker

# 查看Flower监控
open http://localhost:5555
```

**解决方案：**
```bash
# 重启定时任务服务
docker-compose restart celery-beat celery-worker

# 清空任务队列
docker exec tradingagents-redis redis-cli FLUSHDB

# 手动执行任务测试
curl -X POST http://localhost:8003/api/tasks/run \
  -H "Content-Type: application/json" \
  -d '{"task_name": "tasks.maintenance_tasks.health_check"}'
```

#### 问题：任务执行失败

**诊断：**
```bash
# 查看任务执行历史
curl http://localhost:8003/api/tasks/history

# 查看具体任务结果
curl http://localhost:8003/api/tasks/{task_id}/result
```

## 🔍 高级调试技巧

### 1. 进入容器调试

```bash
# 进入API Gateway容器
docker exec -it tradingagents-api-gateway bash

# 进入MongoDB容器
docker exec -it tradingagents-mongodb mongosh

# 进入Redis容器
docker exec -it tradingagents-redis redis-cli
```

### 2. 查看详细日志

```bash
# 实时查看所有日志
docker-compose logs -f --tail=100

# 查看特定时间段的日志
docker-compose logs --since="2025-01-20T10:00:00" api-gateway

# 保存日志到文件
docker-compose logs > system.log 2>&1
```

### 3. 网络调试

```bash
# 测试容器间网络连接
docker exec tradingagents-api-gateway curl http://data-service:8002/health

# 查看网络配置
docker exec tradingagents-api-gateway cat /etc/hosts

# 测试DNS解析
docker exec tradingagents-api-gateway nslookup mongodb
```

### 4. 数据库调试

```bash
# MongoDB 查询调试
docker exec tradingagents-mongodb mongosh tradingagents --eval "
  db.stock_info.find().limit(5);
  db.analysis_results.countDocuments();
"

# Redis 调试
docker exec tradingagents-redis redis-cli --eval "
  return redis.call('INFO', 'memory')
"
```

## 🆘 获取帮助

### 1. 收集诊断信息

运行以下命令收集系统信息：

```bash
# 生成诊断报告
python scripts/debug-tools.py > diagnosis.txt 2>&1

# 收集日志
docker-compose logs > logs.txt 2>&1

# 收集系统信息
docker-compose ps > containers.txt
docker system df > docker-info.txt
```

### 2. 常用资源

- **项目文档**: [GETTING_STARTED.md](./GETTING_STARTED.md)
- **API文档**: http://localhost:8000/docs
- **Celery文档**: https://docs.celeryproject.org/
- **FastAPI文档**: https://fastapi.tiangolo.com/
- **MongoDB文档**: https://docs.mongodb.com/
- **Redis文档**: https://redis.io/documentation

### 3. 报告问题

如果问题仍未解决，请提供以下信息：

1. **系统环境**：操作系统、Docker版本
2. **错误信息**：完整的错误日志
3. **重现步骤**：详细的操作步骤
4. **配置信息**：相关的配置文件（隐藏敏感信息）
5. **诊断报告**：运行 `debug-tools.py` 的输出

---

💡 **提示**: 大多数问题都可以通过重启相关服务解决。如果问题持续存在，请按照本指南逐步排查。
