# Backend服务故障排查快速手册

## 🚨 **紧急故障排查流程**

### **第一步：服务状态检查**
```bash
# 快速检查所有服务状态
curl -s http://localhost:8001/health | jq .  # API Gateway
curl -s http://localhost:8002/health | jq .  # Analysis Engine
curl -s http://localhost:8003/health | jq .  # Data Service
curl -s http://localhost:8004/health | jq .  # LLM Service
curl -s http://localhost:8005/health | jq .  # Agent Service
curl -s http://localhost:8006/health | jq .  # Memory Service
```

### **第二步：Docker容器检查**
```bash
# 检查容器状态
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 检查容器资源使用
docker stats --no-stream

# 检查容器日志
docker logs --tail 50 backend-analysis-engine-1
docker logs --tail 50 backend-agent-service-1
docker logs --tail 50 backend-llm-service-1
```

## 🔍 **常见故障场景**

### **场景1：分析请求卡住不动**

#### **症状**
```
POST /api/v1/analysis/comprehensive
响应：202 Accepted
但是长时间没有结果返回
```

#### **排查步骤**
```bash
# 1. 检查分析状态
curl http://localhost:8002/api/v1/analysis/status/{analysis_id}

# 2. 检查图执行日志
docker logs backend-analysis-engine-1 | grep "图执行"

# 3. 检查Agent服务状态
curl http://localhost:8005/api/v1/agents/status

# 4. 检查LLM服务状态
curl http://localhost:8004/api/v1/models
```

#### **可能原因和解决方案**
| 原因 | 症状 | 解决方案 |
|------|------|----------|
| **图节点卡住** | 某个节点长时间执行 | 重启Analysis Engine |
| **Agent服务无响应** | Agent调用超时 | 检查Agent Service日志，重启服务 |
| **LLM调用失败** | API密钥失效或配额用完 | 检查API密钥和配额 |
| **数据库连接问题** | MongoDB/Redis连接失败 | 重启数据库服务 |

### **场景2：辩论无法结束**

#### **症状**
```
🗣️ 辩论第8轮开始
🗣️ 辩论第9轮开始
🗣️ 辩论第10轮开始
(超过预期的3轮)
```

#### **排查步骤**
```bash
# 1. 检查辩论状态
curl http://localhost:8002/api/v1/analysis/debug/debate-state

# 2. 检查条件逻辑
docker logs backend-analysis-engine-1 | grep "should_continue_debate"

# 3. 手动终止分析
curl -X POST http://localhost:8002/api/v1/analysis/{analysis_id}/cancel
```

#### **解决方案**
```python
# 临时修复：在ConditionalLogic中添加强制终止
def should_continue_debate(self, state):
    # 强制终止条件
    if self.debate_state["count"] >= 10:  # 绝对上限
        logger.warning("🚨 辩论轮数超限，强制终止")
        return "research_manager"
    
    # 正常逻辑...
```

### **场景3：LLM调用频繁失败**

#### **症状**
```
❌ LLM服务错误: 429 - Too Many Requests
❌ LLM服务错误: 401 - Unauthorized
❌ LLM服务错误: 500 - Internal Server Error
```

#### **排查步骤**
```bash
# 1. 检查API密钥
echo $DEEPSEEK_API_KEY
curl -H "Authorization: Bearer $DEEPSEEK_API_KEY" https://api.deepseek.com/v1/models

# 2. 检查使用统计
curl http://localhost:8004/api/v1/usage/stats

# 3. 检查模型可用性
curl http://localhost:8004/api/v1/models
```

#### **解决方案**
| 错误码 | 原因 | 解决方案 |
|--------|------|----------|
| **401** | API密钥无效 | 更新API密钥 |
| **429** | 请求频率过高 | 增加重试延迟，实现指数退避 |
| **500** | 模型服务异常 | 切换到备用模型 |
| **503** | 服务不可用 | 等待服务恢复或使用其他提供商 |

### **场景4：服务间连接失败**

#### **症状**
```
❌ Agent服务调用失败: market_analyst/analyze - Connection refused
❌ 连接LLM服务失败: http://llm-service:8004
```

#### **排查步骤**
```bash
# 1. 检查网络连接
docker exec backend-analysis-engine-1 ping agent-service
docker exec backend-agent-service-1 ping llm-service

# 2. 检查端口监听
docker exec backend-agent-service-1 netstat -tlnp | grep 8005
docker exec backend-llm-service-1 netstat -tlnp | grep 8004

# 3. 检查Docker网络
docker network ls
docker network inspect backend_default
```

#### **解决方案**
```bash
# 1. 重启相关服务
docker-compose restart agent-service llm-service

# 2. 重建Docker网络
docker-compose down
docker network prune
docker-compose up -d

# 3. 检查服务发现配置
# 确保使用正确的服务名而不是localhost
```

## 🛠️ **快速修复脚本**

### **服务重启脚本**
```bash
#!/bin/bash
# scripts/quick-fix.sh

echo "🔧 Backend快速修复脚本"

# 检查参数
if [ $# -eq 0 ]; then
    echo "用法: $0 [service_name|all]"
    echo "服务名: analysis-engine, agent-service, llm-service, all"
    exit 1
fi

SERVICE=$1

case $SERVICE in
    "analysis-engine")
        echo "🔄 重启Analysis Engine..."
        docker-compose restart analysis-engine
        sleep 10
        curl -s http://localhost:8002/health
        ;;
    "agent-service")
        echo "🔄 重启Agent Service..."
        docker-compose restart agent-service
        sleep 10
        curl -s http://localhost:8005/health
        ;;
    "llm-service")
        echo "🔄 重启LLM Service..."
        docker-compose restart llm-service
        sleep 10
        curl -s http://localhost:8004/health
        ;;
    "all")
        echo "🔄 重启所有核心服务..."
        docker-compose restart llm-service agent-service analysis-engine
        sleep 20
        echo "📊 健康检查..."
        curl -s http://localhost:8004/health | jq .status
        curl -s http://localhost:8005/health | jq .status
        curl -s http://localhost:8002/health | jq .status
        ;;
    *)
        echo "❌ 未知服务: $SERVICE"
        exit 1
        ;;
esac

echo "✅ 修复完成"
```

### **日志收集脚本**
```bash
#!/bin/bash
# scripts/collect-logs.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="logs_$TIMESTAMP"

echo "📋 收集故障日志到 $LOG_DIR"

mkdir -p $LOG_DIR

# 收集Docker日志
docker logs backend-analysis-engine-1 > $LOG_DIR/analysis-engine.log 2>&1
docker logs backend-agent-service-1 > $LOG_DIR/agent-service.log 2>&1
docker logs backend-llm-service-1 > $LOG_DIR/llm-service.log 2>&1
docker logs backend-data-service-1 > $LOG_DIR/data-service.log 2>&1

# 收集系统信息
docker ps > $LOG_DIR/docker-ps.txt
docker stats --no-stream > $LOG_DIR/docker-stats.txt
docker network ls > $LOG_DIR/docker-networks.txt

# 收集健康检查
curl -s http://localhost:8002/health > $LOG_DIR/analysis-engine-health.json 2>&1
curl -s http://localhost:8005/health > $LOG_DIR/agent-service-health.json 2>&1
curl -s http://localhost:8004/health > $LOG_DIR/llm-service-health.json 2>&1

# 打包日志
tar -czf logs_$TIMESTAMP.tar.gz $LOG_DIR
rm -rf $LOG_DIR

echo "✅ 日志已收集到 logs_$TIMESTAMP.tar.gz"
```

## 📊 **监控和告警**

### **关键监控指标**
```python
# 服务健康监控
health_checks = {
    "analysis_engine": "http://localhost:8002/health",
    "agent_service": "http://localhost:8005/health", 
    "llm_service": "http://localhost:8004/health"
}

# 性能监控
performance_metrics = {
    "response_time_p95": "95%响应时间",
    "error_rate": "错误率",
    "concurrent_requests": "并发请求数",
    "memory_usage": "内存使用率",
    "cpu_usage": "CPU使用率"
}

# 业务监控
business_metrics = {
    "analysis_success_rate": "分析成功率",
    "debate_completion_rate": "辩论完成率",
    "llm_call_success_rate": "LLM调用成功率"
}
```

### **告警规则**
```yaml
# prometheus/alerts.yml
groups:
  - name: backend_services
    rules:
      - alert: ServiceDown
        expr: up{job="backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Backend服务下线"
          description: "{{ $labels.instance }} 服务已下线超过1分钟"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "错误率过高"
          description: "{{ $labels.service }} 错误率超过10%"

      - alert: LLMCallFailure
        expr: rate(llm_calls_failed_total[5m]) > 0.2
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "LLM调用失败率过高"
          description: "LLM调用失败率超过20%"
```

## 🔧 **预防性维护**

### **定期检查清单**
```bash
# 每日检查
□ 检查所有服务健康状态
□ 检查错误日志
□ 检查资源使用情况
□ 检查LLM API配额

# 每周检查
□ 清理旧日志文件
□ 检查数据库性能
□ 更新依赖包
□ 备份重要配置

# 每月检查
□ 性能基准测试
□ 安全漏洞扫描
□ 容量规划评估
□ 灾难恢复演练
```

### **自动化维护脚本**
```bash
#!/bin/bash
# scripts/maintenance.sh

echo "🔧 执行预防性维护..."

# 清理旧日志
find ./logs -name "*.log" -mtime +7 -delete

# 清理Docker资源
docker system prune -f

# 检查磁盘空间
df -h | grep -E "(8[0-9]|9[0-9])%" && echo "⚠️ 磁盘空间不足"

# 检查内存使用
free -m | awk 'NR==2{printf "内存使用: %.2f%%\n", $3*100/$2}'

# 更新健康检查
./scripts/health-check.sh

echo "✅ 维护完成"
```

## 📞 **紧急联系和升级**

### **故障升级流程**
```
Level 1: 自动修复 (脚本自动处理)
    ↓ (5分钟内无法解决)
Level 2: 开发团队 (手动干预)
    ↓ (30分钟内无法解决)
Level 3: 架构师 (架构级问题)
    ↓ (2小时内无法解决)
Level 4: 技术总监 (业务影响严重)
```

### **紧急操作手册**
```bash
# 紧急停止所有服务
docker-compose down

# 紧急重启所有服务
docker-compose up -d

# 紧急切换到维护模式
curl -X POST http://localhost:8001/api/v1/maintenance/enable

# 紧急数据备份
./scripts/emergency-backup.sh
```

---

*本手册提供Backend服务故障的快速排查和修复方法。紧急情况下请按照升级流程联系相关人员。*
