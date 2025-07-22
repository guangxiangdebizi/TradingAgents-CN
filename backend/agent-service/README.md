# TradingAgents Agent Service

智能体服务是TradingAgents系统的核心组件，负责管理和编排所有智能体的协作分析。

## 🏗️ 架构概览

Agent Service采用微服务架构，包含以下核心组件：

### 智能体类型
- **分析师团队**
  - `FundamentalsAnalyst`: 基本面分析师
  - `MarketAnalyst`: 市场分析师  
  - `NewsAnalyst`: 新闻分析师
  - `SocialMediaAnalyst`: 社交媒体分析师

- **研究员团队**
  - `BullResearcher`: 看涨研究员
  - `BearResearcher`: 看跌研究员

- **管理层**
  - `ResearchManager`: 研究经理
  - `RiskManager`: 风险经理

- **交易执行**
  - `Trader`: 交易员

- **风险评估团队**
  - `RiskyDebator`: 激进辩论者
  - `SafeDebator`: 保守辩论者
  - `NeutralDebator`: 中性辩论者

### 核心引擎
- **AgentManager**: 智能体管理器，负责智能体注册、发现和生命周期管理
- **CollaborationEngine**: 协作引擎，负责智能体间的协作编排
- **DebateEngine**: 辩论引擎，负责智能体间的辩论协调
- **ConsensusAlgorithm**: 共识算法，负责智能体间的共识达成
- **StateManager**: 状态管理器，负责状态持久化和同步
- **MessageRouter**: 消息路由器，负责智能体间的消息传递

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
cd backend/agent-service
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 直接启动
python -m app.main

# 或使用uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8008 --reload
```

### 3. Docker部署

```bash
# 构建镜像
docker build -t tradingagents-agent-service .

# 运行容器
docker run -p 8008:8008 tradingagents-agent-service
```

### 4. 使用docker-compose

```bash
# 启动完整微服务栈
cd backend
docker-compose -f docker-compose.microservices.yml up agent-service
```

## 📡 API接口

### 智能体管理

```bash
# 获取智能体列表
GET /api/v1/agents/

# 获取特定智能体信息
GET /api/v1/agents/{agent_id}

# 注册新智能体
POST /api/v1/agents/register

# 注销智能体
DELETE /api/v1/agents/{agent_id}

# 获取系统状态
GET /api/v1/agents/system/status
```

### 任务执行

```bash
# 执行智能体任务
POST /api/v1/agents/execute

# 获取智能体状态
GET /api/v1/agents/{agent_id}/status

# 智能体健康检查
POST /api/v1/agents/{agent_id}/health-check
```

### 协作和辩论

```bash
# 启动协作
POST /api/v1/collaboration/start

# 获取协作状态
GET /api/v1/collaboration/{collaboration_id}/status

# 启动辩论
POST /api/v1/debate/start

# 获取辩论状态
GET /api/v1/debate/{debate_id}/status
```

## 🧪 测试

### 运行单元测试

```bash
# 运行基础功能测试
python test_agent_service.py

# 运行完整测试套件
pytest tests/
```

### 测试示例

```python
import asyncio
from app.agents.base_agent import AgentType, TaskContext
from app.agents.analysts.fundamentals_analyst import FundamentalsAnalyst

async def test_fundamentals_analysis():
    # 创建智能体
    analyst = FundamentalsAnalyst(AgentType.FUNDAMENTALS_ANALYST)
    
    # 创建任务上下文
    context = TaskContext(
        task_id="test_001",
        symbol="AAPL",
        company_name="Apple Inc.",
        market="US",
        analysis_date="2025-01-22"
    )
    
    # 执行任务
    result = await analyst.execute_task(context)
    print(f"分析结果: {result.status}")

# 运行测试
asyncio.run(test_fundamentals_analysis())
```

## 🔧 配置

### 环境变量

```bash
# 数据库配置
MONGODB_URL=mongodb://admin:password123@mongodb:27017/tradingagents?authSource=admin
REDIS_URL=redis://redis:6379/0

# 服务依赖
DATA_SERVICE_URL=http://data-service:8002
LLM_SERVICE_URL=http://llm-service:8004

# 日志配置
LOG_LEVEL=INFO
```

### 智能体权重配置

在`consensus_algorithm.py`中可以配置智能体权重：

```python
agent_weights = {
    "fundamentals_analyst": 1.2,
    "market_analyst": 1.1,
    "research_manager": 1.5,
    "risk_manager": 1.3,
    # ...
}
```

## 🔄 工作流

### 综合分析工作流

1. **数据收集**: 收集基础数据
2. **并行分析**: 基本面、技术面、新闻分析并行执行
3. **研究辩论**: 看涨/看跌研究员辩论
4. **管理审核**: 研究经理和风险经理审核
5. **最终决策**: 交易员制定最终决策

### 快速分析工作流

1. **市场分析**: 技术分析和趋势判断
2. **风险评估**: 风险经理评估风险水平

## 📊 监控和日志

### 健康检查

```bash
# 服务健康检查
curl http://localhost:8008/health

# 智能体健康检查
curl -X POST http://localhost:8008/api/v1/agents/{agent_id}/health-check
```

### 日志查看

```bash
# 查看服务日志
docker logs tradingagents-agent-service

# 实时日志
docker logs -f tradingagents-agent-service
```

## 🛠️ 开发指南

### 添加新智能体

1. 继承`BaseAgent`类
2. 实现`_define_capabilities()`方法
3. 实现`process_task()`方法
4. 在`AgentManager`中注册

```python
from app.agents.base_agent import BaseAgent, AgentType, AgentCapability

class CustomAnalyst(BaseAgent):
    def _define_capabilities(self):
        return [
            AgentCapability(
                name="custom_analysis",
                description="自定义分析",
                required_tools=["custom_tool"],
                supported_markets=["US", "CN", "HK"]
            )
        ]
    
    async def process_task(self, context):
        # 实现分析逻辑
        pass
```

### 扩展协作模式

在`CollaborationEngine`中添加新的工作流定义：

```python
"custom_workflow": {
    "name": "自定义工作流",
    "mode": CollaborationMode.SEQUENTIAL,
    "steps": [
        {
            "name": "step1",
            "agents": ["custom_analyst"],
            "parallel": False
        }
    ]
}
```

## 🔗 相关服务

- **Data Service**: 数据服务，提供市场数据
- **LLM Service**: 大语言模型服务，提供AI分析能力
- **Analysis Engine**: 分析引擎，协调整体分析流程

## 📝 许可证

本项目采用MIT许可证。详见LICENSE文件。
