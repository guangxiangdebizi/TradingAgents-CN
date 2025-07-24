# Backend核心服务关系说明文档

## 📋 **概述**

本文档详细说明Backend项目中三大核心服务（Analysis Engine、Agent Service、LLM Service）之间的关系、调用流程和故障排查方法。

## 🏗️ **服务架构概览**

### **服务层次结构**

```
用户请求层
    ↓
业务逻辑层 (Analysis Engine :8002)
    ↓
智能体服务层 (Agent Service :8005)
    ↓
模型调用层 (LLM Service :8004)
```

### **端口分配**
- **Analysis Engine**: 8002 (分析引擎 + 图引擎)
- **Agent Service**: 8005 (智能体管理 + 辩论引擎)
- **LLM Service**: 8004 (大模型统一调用)
- **Data Service**: 8003 (数据服务)
- **API Gateway**: 8001 (统一入口)
- **Memory Service**: 8006 (内存和状态管理)

## 🔄 **服务间调用关系**

### **1. Analysis Engine → Agent Service**

#### **调用方式**
```python
# 位置: backend/analysis-engine/app/graphs/agent_nodes.py
class AgentNodes:
    def __init__(self):
        self.agent_service_url = "http://agent-service:8005"
    
    async def _call_agent_service(self, agent_type: str, action: str, data: Dict[str, Any]):
        url = f"{self.agent_service_url}/api/v1/agents/{agent_type}/{action}"
        async with self.session.post(url, json=data) as response:
            return await response.json()
```

#### **调用场景**
- **图节点执行**: 每个图节点调用对应的Agent
- **多轮辩论**: Bull/Bear研究员的辩论交互
- **风险分析**: 三方风险分析师的轮流分析

#### **API接口**
```
POST /api/v1/agents/{agent_type}/{action}

支持的agent_type:
- market_analyst (市场分析师)
- fundamentals_analyst (基本面分析师)
- news_analyst (新闻分析师)
- bull_researcher (多头研究员)
- bear_researcher (空头研究员)
- research_manager (研究经理)
- risky_analyst (激进分析师)
- safe_analyst (保守分析师)
- neutral_analyst (中性分析师)
- risk_manager (风险经理)
- trader (交易员)

支持的action:
- analyze (分析)
- research (研究)
- assess (评估)
- plan (计划)
- synthesize (综合)
```

### **2. Agent Service → LLM Service**

#### **调用方式**
```python
# 位置: backend/agent-service/app/agents/analysts/market_analyst.py
async def _generate_analysis_report(self, context, market_data, ...):
    response = await self.llm_client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model="deepseek-chat",
        temperature=0.1
    )
```

#### **调用场景**
- **智能体思考**: 每个Agent需要LLM进行推理
- **报告生成**: 生成各种分析报告
- **辩论对话**: 多轮辩论中的观点生成

#### **API接口**
```
POST /api/v1/chat/completions

请求格式:
{
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "分析内容"}
    ],
    "temperature": 0.1,
    "max_tokens": 1500
}

响应格式:
{
    "success": true,
    "content": "LLM生成的内容",
    "usage": {
        "prompt_tokens": 100,
        "completion_tokens": 200,
        "total_tokens": 300
    }
}
```

### **3. Analysis Engine → Data Service**

#### **调用方式**
```python
# 位置: backend/analysis-engine/app/tools/data_tools.py
async def get_stock_data(symbol: str):
    async with aiohttp.ClientSession() as session:
        url = f"http://data-service:8003/api/v1/stocks/{symbol}/data"
        async with session.get(url) as response:
            return await response.json()
```

#### **调用场景**
- **数据获取**: 获取股票基础数据、财务数据、新闻数据
- **工具调用**: 图引擎中的工具节点调用

## 📊 **完整调用流程**

### **股票分析完整流程**

```
1. 用户请求
   POST /api/v1/analysis/comprehensive
   → API Gateway (8001)

2. 路由到分析引擎
   → Analysis Engine (8002)
   → TradingGraph.analyze_stock()

3. 图引擎执行
   → GraphState 初始化
   → 条件逻辑判断
   → 节点顺序执行

4. 分析师节点执行
   MarketAnalyst Node:
   → 调用 Agent Service (8005)
   → POST /api/v1/agents/market_analyst/analyze
   
   Agent Service:
   → AgentManager.execute_task()
   → MarketAnalyst.analyze()
   → 调用 LLM Service (8004)
   → POST /api/v1/chat/completions
   
   LLM Service:
   → ModelRouter 路由
   → DeepSeekAdapter 执行
   → 返回分析结果

5. 多轮辩论执行
   Bull Researcher Node:
   → 调用 Agent Service (8005)
   → BullResearcher.research()
   → 调用 LLM Service (8004)
   
   Bear Researcher Node:
   → 调用 Agent Service (8005)
   → BearResearcher.research()
   → 调用 LLM Service (8004)
   
   条件逻辑判断:
   → ConditionalLogic.should_continue_debate()
   → 决定继续辩论或结束

6. 风险分析执行
   (类似辩论流程，三方轮流分析)

7. 最终结果
   → 图引擎汇总所有结果
   → 返回完整分析报告
```

## 🔧 **配置和连接**

### **服务发现配置**

#### **Analysis Engine配置**
```python
# backend/analysis-engine/app/graphs/agent_nodes.py
class AgentNodes:
    def __init__(self):
        self.agent_service_url = "http://agent-service:8005"
        # Docker环境使用服务名，本地开发使用localhost
```

#### **Agent Service配置**
```python
# backend/agent-service/app/agents/base_agent.py
class BaseAgent:
    def __init__(self):
        self.llm_service_url = "http://llm-service:8004"
        # 通过环境变量或配置文件设置
```

#### **环境变量配置**
```bash
# Docker Compose环境
AGENT_SERVICE_URL=http://agent-service:8005
LLM_SERVICE_URL=http://llm-service:8004
DATA_SERVICE_URL=http://data-service:8003

# 本地开发环境
AGENT_SERVICE_URL=http://localhost:8005
LLM_SERVICE_URL=http://localhost:8004
DATA_SERVICE_URL=http://localhost:8003
```

### **连接池和超时配置**

#### **HTTP客户端配置**
```python
# 连接超时配置
timeout_config = {
    "total": 300,      # 总超时时间
    "connect": 30,     # 连接超时
    "read": 270        # 读取超时
}

# 重试配置
retry_config = {
    "max_retries": 3,
    "retry_delay": 5,
    "backoff_factor": 2
}
```

## 🚨 **故障排查指南**

### **常见问题和解决方案**

#### **1. 服务连接失败**

**症状**: 
```
❌ Agent服务调用失败: market_analyst/analyze - Connection refused
```

**排查步骤**:
```bash
# 1. 检查服务状态
docker ps | grep agent-service
docker logs backend-agent-service-1

# 2. 检查网络连接
docker exec -it backend-analysis-engine-1 ping agent-service
curl http://agent-service:8005/health

# 3. 检查端口映射
docker port backend-agent-service-1
```

**解决方案**:
- 确保Agent Service正常启动
- 检查Docker网络配置
- 验证服务发现配置

#### **2. LLM调用超时**

**症状**:
```
❌ LLM服务错误: 504 - Gateway Timeout
```

**排查步骤**:
```bash
# 1. 检查LLM服务状态
docker logs backend-llm-service-1

# 2. 检查模型配置
curl http://llm-service:8004/api/v1/models

# 3. 检查API密钥
echo $DEEPSEEK_API_KEY
```

**解决方案**:
- 增加超时时间配置
- 检查API密钥有效性
- 验证模型可用性

#### **3. 图执行卡住**

**症状**:
```
🔄 执行多头研究员节点
(长时间无响应)
```

**排查步骤**:
```bash
# 1. 检查图状态
curl http://analysis-engine:8002/api/v1/analysis/status/{analysis_id}

# 2. 检查Agent状态
curl http://agent-service:8005/api/v1/agents/status

# 3. 检查资源使用
docker stats
```

**解决方案**:
- 检查条件逻辑是否正确
- 验证Agent响应格式
- 增加超时和重试机制

#### **4. 辩论无法结束**

**症状**:
```
🗣️ 辩论第10轮开始
(超过预期轮数)
```

**排查步骤**:
```python
# 检查条件逻辑
def should_continue_debate(self, state):
    print(f"当前轮数: {self.debate_state['count']}")
    print(f"最大轮数: {self.max_debate_rounds}")
    print(f"当前发言者: {self.debate_state['current_speaker']}")
```

**解决方案**:
- 检查辩论轮数计算逻辑
- 验证状态更新机制
- 添加强制终止条件

### **监控和日志**

#### **关键日志位置**
```
Analysis Engine: backend/analysis-engine/logs/
Agent Service: backend/agent-service/logs/
LLM Service: backend/llm-service/logs/
```

#### **关键监控指标**
```python
# 服务健康状态
GET /health

# 图执行状态
GET /api/v1/analysis/status/{analysis_id}

# Agent状态
GET /api/v1/agents/status

# LLM使用统计
GET /api/v1/usage/stats
```

## 🔄 **开发调试技巧**

### **本地开发环境**

#### **启动顺序**
```bash
# 1. 启动基础服务
docker-compose up -d redis mongodb

# 2. 启动LLM服务
cd llm-service && python -m uvicorn app.main:app --port 8004

# 3. 启动Agent服务
cd agent-service && python -m uvicorn app.main:app --port 8005

# 4. 启动Analysis Engine
cd analysis-engine && python -m uvicorn app.main:app --port 8002
```

#### **调试技巧**
```python
# 1. 启用详细日志
import logging
logging.getLogger().setLevel(logging.DEBUG)

# 2. 添加调试断点
import pdb; pdb.set_trace()

# 3. 模拟服务调用
async def test_agent_call():
    async with aiohttp.ClientSession() as session:
        response = await session.post(
            "http://localhost:8005/api/v1/agents/market_analyst/analyze",
            json={"symbol": "AAPL", "context": {}}
        )
        print(await response.json())
```

### **性能优化建议**

#### **连接池优化**
```python
# 使用连接池
connector = aiohttp.TCPConnector(
    limit=100,           # 总连接数限制
    limit_per_host=30,   # 每个主机连接数限制
    keepalive_timeout=30 # 保持连接时间
)
session = aiohttp.ClientSession(connector=connector)
```

#### **并发控制**
```python
# 使用信号量控制并发
semaphore = asyncio.Semaphore(10)

async def call_with_limit():
    async with semaphore:
        return await make_api_call()
```

## 📚 **相关文档**

- [图架构设计文档](graph_architecture_design.md)
- [图实现技术规范](../technical/graph_implementation_spec.md)
- [API参考文档](../api/)
- [部署指南](../deployment/deployment-guide.md)
- [故障排除指南](../troubleshooting/)

## 🔍 **服务依赖关系详解**

### **依赖层次图**

```
Level 1: 基础服务
├── Redis (缓存)
├── MongoDB (数据存储)
└── Data Service (数据接口)

Level 2: 核心服务
├── LLM Service (模型调用)
└── Memory Service (状态管理)

Level 3: 业务服务
├── Agent Service (智能体管理)
└── Task Scheduler (任务调度)

Level 4: 应用服务
├── Analysis Engine (分析引擎)
└── API Gateway (统一入口)
```

### **启动依赖顺序**

#### **必须的启动顺序**
```bash
# 1. 基础设施 (必须最先启动)
docker-compose up -d redis mongodb

# 2. 数据服务 (为其他服务提供数据)
docker-compose up -d data-service

# 3. LLM服务 (Agent服务依赖)
docker-compose up -d llm-service

# 4. 内存服务 (状态管理)
docker-compose up -d memory-service

# 5. Agent服务 (Analysis Engine依赖)
docker-compose up -d agent-service

# 6. 分析引擎 (业务核心)
docker-compose up -d analysis-engine

# 7. API网关 (对外接口)
docker-compose up -d api-gateway
```

#### **健康检查验证**
```bash
# 验证服务启动顺序
curl http://localhost:8003/health  # Data Service
curl http://localhost:8004/health  # LLM Service
curl http://localhost:8006/health  # Memory Service
curl http://localhost:8005/health  # Agent Service
curl http://localhost:8002/health  # Analysis Engine
curl http://localhost:8001/health  # API Gateway
```

## 🔄 **数据流向分析**

### **请求数据流**

```
用户请求 → API Gateway → Analysis Engine → Agent Service → LLM Service
    ↓           ↓              ↓              ↓           ↓
  路由分发   图引擎调度    智能体管理    Agent执行   模型推理
    ↓           ↓              ↓              ↓           ↓
  参数验证   状态管理      任务分配      提示构建    结果生成
```

### **状态数据流**

```
GraphState → AgentNodes → Agent Service → TaskContext → LLM Service
    ↓            ↓            ↓             ↓            ↓
  图状态     节点状态    智能体状态    任务上下文   模型状态
    ↓            ↓            ↓             ↓            ↓
Memory Service ← State Manager ← Agent Manager ← Task Manager ← Usage Tracker
```

### **结果数据流**

```
LLM Response → Agent Result → Node Result → Graph Result → API Response
     ↓             ↓            ↓            ↓            ↓
  模型输出     智能体结果   节点输出     图执行结果   最终响应
     ↓             ↓            ↓            ↓            ↓
  格式化       结果处理     状态更新     结果汇总     响应格式化
```

## 🛠️ **开发环境配置**

### **Docker Compose配置**

#### **开发环境配置文件**
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  analysis-engine:
    build: ./analysis-engine
    ports:
      - "8002:8002"
    environment:
      - AGENT_SERVICE_URL=http://agent-service:8005
      - LLM_SERVICE_URL=http://llm-service:8004
      - DATA_SERVICE_URL=http://data-service:8003
      - MEMORY_SERVICE_URL=http://memory-service:8006
    depends_on:
      - agent-service
      - data-service
    volumes:
      - ./analysis-engine:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

  agent-service:
    build: ./agent-service
    ports:
      - "8005:8005"
    environment:
      - LLM_SERVICE_URL=http://llm-service:8004
      - MEMORY_SERVICE_URL=http://memory-service:8006
    depends_on:
      - llm-service
      - memory-service
    volumes:
      - ./agent-service:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload

  llm-service:
    build: ./llm-service
    ports:
      - "8004:8004"
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./llm-service:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

### **本地开发脚本**

#### **启动脚本**
```bash
#!/bin/bash
# scripts/start-dev.sh

echo "🚀 启动Backend开发环境..."

# 检查环境变量
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ 请设置DEEPSEEK_API_KEY环境变量"
    exit 1
fi

# 启动基础服务
echo "📦 启动基础服务..."
docker-compose -f docker-compose.dev.yml up -d redis mongodb

# 等待基础服务启动
sleep 5

# 启动业务服务
echo "🔧 启动业务服务..."
docker-compose -f docker-compose.dev.yml up -d data-service llm-service memory-service

# 等待服务启动
sleep 10

# 启动核心服务
echo "🎯 启动核心服务..."
docker-compose -f docker-compose.dev.yml up -d agent-service analysis-engine

# 等待服务启动
sleep 10

# 启动API网关
echo "🌐 启动API网关..."
docker-compose -f docker-compose.dev.yml up -d api-gateway

echo "✅ 开发环境启动完成!"
echo "📊 服务状态检查..."

# 健康检查
services=("data-service:8003" "llm-service:8004" "agent-service:8005" "analysis-engine:8002" "api-gateway:8001")
for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)

    if curl -s http://localhost:$port/health > /dev/null; then
        echo "✅ $name (端口 $port) - 健康"
    else
        echo "❌ $name (端口 $port) - 异常"
    fi
done
```

#### **停止脚本**
```bash
#!/bin/bash
# scripts/stop-dev.sh

echo "🛑 停止Backend开发环境..."

# 停止所有服务
docker-compose -f docker-compose.dev.yml down

# 清理资源
docker system prune -f

echo "✅ 开发环境已停止"
```

### **调试配置**

#### **VSCode调试配置**
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Analysis Engine",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/analysis-engine/app/main.py",
            "console": "integratedTerminal",
            "env": {
                "AGENT_SERVICE_URL": "http://localhost:8005",
                "LLM_SERVICE_URL": "http://localhost:8004",
                "DATA_SERVICE_URL": "http://localhost:8003"
            },
            "args": ["--host", "0.0.0.0", "--port", "8002"]
        },
        {
            "name": "Debug Agent Service",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/agent-service/app/main.py",
            "console": "integratedTerminal",
            "env": {
                "LLM_SERVICE_URL": "http://localhost:8004",
                "MEMORY_SERVICE_URL": "http://localhost:8006"
            },
            "args": ["--host", "0.0.0.0", "--port", "8005"]
        },
        {
            "name": "Debug LLM Service",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/llm-service/app/main.py",
            "console": "integratedTerminal",
            "env": {
                "DEEPSEEK_API_KEY": "${env:DEEPSEEK_API_KEY}"
            },
            "args": ["--host", "0.0.0.0", "--port", "8004"]
        }
    ]
}
```

## 📈 **性能监控和优化**

### **关键性能指标**

#### **服务级别指标**
```python
# 响应时间监控
response_time_metrics = {
    "analysis_engine_response_time": "分析引擎响应时间",
    "agent_service_response_time": "智能体服务响应时间",
    "llm_service_response_time": "LLM服务响应时间",
    "graph_execution_time": "图执行总时间",
    "debate_round_time": "单轮辩论时间"
}

# 吞吐量监控
throughput_metrics = {
    "requests_per_second": "每秒请求数",
    "concurrent_analyses": "并发分析数",
    "agent_utilization": "智能体利用率",
    "llm_calls_per_minute": "每分钟LLM调用数"
}

# 错误率监控
error_metrics = {
    "service_error_rate": "服务错误率",
    "timeout_rate": "超时率",
    "llm_failure_rate": "LLM调用失败率",
    "graph_failure_rate": "图执行失败率"
}
```

#### **业务级别指标**
```python
# 分析质量指标
quality_metrics = {
    "debate_rounds_avg": "平均辩论轮数",
    "consensus_rate": "共识达成率",
    "analysis_completion_rate": "分析完成率",
    "recommendation_confidence": "推荐置信度"
}
```

### **性能优化策略**

#### **连接池优化**
```python
# Analysis Engine中的连接池配置
class ServiceConnections:
    def __init__(self):
        self.agent_service_pool = aiohttp.TCPConnector(
            limit=50,              # 总连接数
            limit_per_host=20,     # 每主机连接数
            keepalive_timeout=60,  # 保持连接时间
            enable_cleanup_closed=True
        )

        self.session = aiohttp.ClientSession(
            connector=self.agent_service_pool,
            timeout=aiohttp.ClientTimeout(total=300)
        )
```

#### **缓存策略**
```python
# LLM结果缓存
class LLMCache:
    def __init__(self):
        self.redis_client = redis.Redis()
        self.cache_ttl = 3600  # 1小时

    async def get_cached_response(self, prompt_hash: str):
        return await self.redis_client.get(f"llm_cache:{prompt_hash}")

    async def cache_response(self, prompt_hash: str, response: str):
        await self.redis_client.setex(
            f"llm_cache:{prompt_hash}",
            self.cache_ttl,
            response
        )
```

#### **负载均衡**
```python
# Agent负载均衡
class AgentLoadBalancer:
    def select_agent(self, available_agents: List[BaseAgent]) -> BaseAgent:
        # 基于当前负载选择最优Agent
        return min(available_agents, key=lambda a: a.current_load)
```

---

*本文档提供Backend核心服务关系的完整说明，为开发和运维提供参考。如有问题请参考相关文档或联系开发团队。*
