# Backend服务API调用示例

## 📋 **概述**

本文档提供Backend各服务间API调用的详细示例，帮助开发者理解服务间的交互方式。

## 🔄 **完整调用链示例**

### **股票分析完整流程**

#### **1. 用户发起分析请求**
```bash
# 通过API Gateway发起请求
curl -X POST http://localhost:8001/api/v1/analysis/comprehensive \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "000001",
    "company_name": "平安银行",
    "market": "CN",
    "analysis_type": "comprehensive"
  }'

# 响应
{
  "success": true,
  "data": {
    "analysis_id": "uuid-12345",
    "status": "started",
    "message": "分析已启动"
  }
}
```

#### **2. Analysis Engine内部图执行**
```python
# Analysis Engine内部调用
# 位置: backend/analysis-engine/app/graphs/trading_graph.py

async def analyze_stock(self, symbol: str, analysis_date: str = None):
    # 创建初始状态
    initial_state = self._create_initial_state(symbol, analysis_date)
    
    # 执行图
    final_state = await self.compiled_graph.ainvoke(initial_state)
    
    return self._process_final_state(final_state)
```

#### **3. 图节点调用Agent Service**
```python
# 市场分析师节点调用
# 位置: backend/analysis-engine/app/graphs/agent_nodes.py

async def market_analyst_node(self, state: GraphState) -> GraphState:
    # 调用Agent Service
    result = await self._call_agent_service(
        "market_analyst",
        "analyze", 
        {
            "symbol": state["symbol"],
            "analysis_type": "technical",
            "context": {
                "current_date": state["current_date"],
                "existing_data": state.get("stock_data")
            }
        }
    )
    
    # HTTP调用详情
    url = f"{self.agent_service_url}/api/v1/agents/market_analyst/analyze"
    # POST http://agent-service:8005/api/v1/agents/market_analyst/analyze
```

#### **4. Agent Service处理请求**
```python
# Agent Service API处理
# 位置: backend/agent-service/app/api/agents_api.py

@router.post("/agents/{agent_type}/{action}")
async def execute_agent_action(
    agent_type: str,
    action: str,
    request: Dict[str, Any]
):
    # 获取Agent Manager
    agent_manager = get_agent_manager()
    
    # 执行任务
    result = await agent_manager.execute_task(
        agent_type=AgentType(agent_type),
        task_type=TaskType(action),
        context=TaskContext(**request)
    )
    
    return {"success": True, "data": result}
```

#### **5. Agent调用LLM Service**
```python
# 市场分析师调用LLM
# 位置: backend/agent-service/app/agents/analysts/market_analyst.py

async def _generate_analysis_report(self, context, market_data, ...):
    prompt = self.analysis_template.format(
        symbol=context.symbol,
        company_name=context.company_name,
        market_data=market_data,
        # ...
    )
    
    # 调用LLM Service
    response = await self.llm_client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model="deepseek-chat",
        temperature=0.1
    )
    
    # HTTP调用详情
    # POST http://llm-service:8004/api/v1/chat/completions
```

#### **6. LLM Service处理请求**
```python
# LLM Service API处理
# 位置: backend/llm-service/app/main.py

@app.post("/api/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    # 模型路由
    adapter = model_router.get_adapter(request.model)
    
    # 调用适配器
    result = await adapter.chat_completion(
        messages=request.messages,
        max_tokens=request.max_tokens,
        temperature=request.temperature
    )
    
    return ChatCompletionResponse(**result)
```

## 🔍 **各服务API详细示例**

### **Analysis Engine API**

#### **启动分析**
```bash
POST http://localhost:8002/api/v1/analysis/graph/analyze
Content-Type: application/json

{
  "symbol": "000001",
  "analysis_type": "comprehensive",
  "config": {
    "max_debate_rounds": 3,
    "max_risk_rounds": 2,
    "selected_analysts": ["market", "fundamentals", "news"]
  }
}

# 响应
{
  "success": true,
  "data": {
    "analysis_id": "uuid-12345",
    "status": "running",
    "current_step": "market_analyst",
    "progress": {
      "completed_steps": 1,
      "total_steps": 12,
      "percentage": 8.3
    }
  }
}
```

#### **查询分析状态**
```bash
GET http://localhost:8002/api/v1/analysis/status/uuid-12345

# 响应
{
  "success": true,
  "data": {
    "analysis_id": "uuid-12345",
    "status": "running",
    "current_step": "bull_researcher",
    "progress": {
      "completed_steps": 6,
      "total_steps": 12,
      "percentage": 50.0
    },
    "debate_status": {
      "current_round": 2,
      "max_rounds": 3,
      "current_speaker": "bull_researcher"
    },
    "errors": [],
    "warnings": []
  }
}
```

#### **获取分析结果**
```bash
GET http://localhost:8002/api/v1/analysis/result/uuid-12345

# 响应
{
  "success": true,
  "data": {
    "analysis_id": "uuid-12345",
    "symbol": "000001",
    "status": "completed",
    "result": {
      "final_recommendation": {
        "action": "buy",
        "confidence": 0.75,
        "target_price": 15.50,
        "reasoning": "基于多轮辩论和风险分析的综合建议"
      },
      "investment_plan": "建议分批买入，控制仓位在5%以内",
      "risk_assessment": {
        "risk_level": "medium",
        "risk_score": 0.6,
        "key_risks": ["市场波动", "行业政策变化"]
      },
      "reports": {
        "fundamentals": "基本面分析报告...",
        "technical": "技术分析报告...",
        "news": "新闻分析报告...",
        "sentiment": "情感分析报告..."
      },
      "debate_summary": {
        "total_rounds": 3,
        "consensus_reached": true,
        "final_stance": "moderately_bullish"
      }
    }
  }
}
```

### **Agent Service API**

#### **执行智能体任务**
```bash
POST http://localhost:8005/api/v1/agents/market_analyst/analyze
Content-Type: application/json

{
  "symbol": "000001",
  "analysis_type": "technical",
  "context": {
    "current_date": "2024-01-22",
    "market": "CN",
    "existing_data": {}
  }
}

# 响应
{
  "success": true,
  "data": {
    "agent_id": "market_analyst_001",
    "agent_type": "market_analyst",
    "task_id": "task_12345",
    "status": "completed",
    "result": {
      "analysis": "技术分析报告内容...",
      "market_data": {
        "current_price": 14.25,
        "volume": 1234567,
        "technical_indicators": {
          "rsi": 65.5,
          "macd": 0.15,
          "ma20": 14.10
        }
      },
      "confidence_score": 0.8
    },
    "execution_time": 15.5,
    "timestamp": "2024-01-22T10:30:00Z"
  }
}
```

#### **启动辩论**
```bash
POST http://localhost:8005/api/v1/debate/start
Content-Type: application/json

{
  "topic": "000001投资决策",
  "participants": ["bull_researcher", "bear_researcher"],
  "context": {
    "symbol": "000001",
    "company_name": "平安银行",
    "market": "CN",
    "analysis_date": "2024-01-22"
  },
  "rules": {
    "max_rounds": 3,
    "timeout_per_round": 120
  }
}

# 响应
{
  "success": true,
  "data": {
    "debate_id": "debate_12345",
    "status": "running",
    "topic": "000001投资决策",
    "participants": ["bull_researcher", "bear_researcher"],
    "current_round": 1,
    "max_rounds": 3
  }
}
```

#### **查询辩论状态**
```bash
GET http://localhost:8005/api/v1/debate/debate_12345/status

# 响应
{
  "success": true,
  "data": {
    "debate_id": "debate_12345",
    "status": "running",
    "current_round": 2,
    "current_speaker": "bear_researcher",
    "rounds": [
      {
        "round_number": 1,
        "bull_argument": "多头观点...",
        "bear_argument": "空头观点...",
        "timestamp": "2024-01-22T10:35:00Z"
      }
    ],
    "consensus": null
  }
}
```

### **LLM Service API**

#### **聊天完成**
```bash
POST http://localhost:8004/api/v1/chat/completions
Content-Type: application/json

{
  "model": "deepseek-chat",
  "messages": [
    {
      "role": "user", 
      "content": "请分析平安银行(000001)的技术指标"
    }
  ],
  "max_tokens": 1500,
  "temperature": 0.1
}

# 响应
{
  "success": true,
  "data": {
    "content": "基于技术指标分析，平安银行当前...",
    "usage": {
      "prompt_tokens": 25,
      "completion_tokens": 150,
      "total_tokens": 175
    },
    "model": "deepseek-chat",
    "finish_reason": "stop"
  }
}
```

#### **获取可用模型**
```bash
GET http://localhost:8004/api/v1/models

# 响应
{
  "success": true,
  "data": {
    "models": [
      {
        "id": "deepseek-chat",
        "provider": "DeepSeek",
        "status": "available",
        "context_length": 128000,
        "supports_tools": true
      },
      {
        "id": "gpt-4",
        "provider": "OpenAI", 
        "status": "available",
        "context_length": 8192,
        "supports_tools": true
      }
    ]
  }
}
```

#### **使用统计**
```bash
GET http://localhost:8004/api/v1/usage/stats

# 响应
{
  "success": true,
  "data": {
    "total_requests": 1250,
    "total_tokens": 125000,
    "requests_by_model": {
      "deepseek-chat": 1000,
      "gpt-4": 250
    },
    "tokens_by_model": {
      "deepseek-chat": 100000,
      "gpt-4": 25000
    },
    "average_response_time": 2.5,
    "error_rate": 0.02
  }
}
```

## 🔧 **调试和测试工具**

### **服务连通性测试**
```bash
#!/bin/bash
# scripts/test-connectivity.sh

echo "🔍 测试服务间连通性..."

# 测试Analysis Engine -> Agent Service
echo "📊 测试Analysis Engine -> Agent Service"
docker exec backend-analysis-engine-1 curl -s http://agent-service:8005/health

# 测试Agent Service -> LLM Service  
echo "🤖 测试Agent Service -> LLM Service"
docker exec backend-agent-service-1 curl -s http://llm-service:8004/health

# 测试完整调用链
echo "🔄 测试完整调用链"
curl -X POST http://localhost:8002/api/v1/analysis/test \
  -H "Content-Type: application/json" \
  -d '{"symbol": "TEST", "test_mode": true}'
```

### **性能测试脚本**
```bash
#!/bin/bash
# scripts/performance-test.sh

echo "⚡ 性能测试开始..."

# 并发分析测试
for i in {1..10}; do
  curl -X POST http://localhost:8002/api/v1/analysis/comprehensive \
    -H "Content-Type: application/json" \
    -d "{\"symbol\": \"TEST$i\", \"test_mode\": true}" &
done

wait
echo "✅ 并发测试完成"

# 响应时间测试
time curl -X POST http://localhost:8002/api/v1/analysis/comprehensive \
  -H "Content-Type: application/json" \
  -d '{"symbol": "PERF_TEST", "test_mode": true}'
```

### **API测试集合**
```python
# tests/api_integration_test.py
import asyncio
import aiohttp
import pytest

class TestServiceIntegration:
    
    async def test_full_analysis_flow(self):
        """测试完整分析流程"""
        async with aiohttp.ClientSession() as session:
            # 1. 启动分析
            async with session.post(
                "http://localhost:8002/api/v1/analysis/comprehensive",
                json={"symbol": "TEST001", "test_mode": True}
            ) as resp:
                result = await resp.json()
                analysis_id = result["data"]["analysis_id"]
            
            # 2. 等待完成
            while True:
                async with session.get(
                    f"http://localhost:8002/api/v1/analysis/status/{analysis_id}"
                ) as resp:
                    status = await resp.json()
                    if status["data"]["status"] == "completed":
                        break
                await asyncio.sleep(1)
            
            # 3. 获取结果
            async with session.get(
                f"http://localhost:8002/api/v1/analysis/result/{analysis_id}"
            ) as resp:
                result = await resp.json()
                assert result["success"] == True
                assert "final_recommendation" in result["data"]["result"]

    async def test_agent_service_direct(self):
        """测试Agent Service直接调用"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8005/api/v1/agents/market_analyst/analyze",
                json={
                    "symbol": "TEST002",
                    "analysis_type": "technical",
                    "context": {"test_mode": True}
                }
            ) as resp:
                result = await resp.json()
                assert result["success"] == True
                assert "analysis" in result["data"]["result"]

    async def test_llm_service_direct(self):
        """测试LLM Service直接调用"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8004/api/v1/chat/completions",
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 50
                }
            ) as resp:
                result = await resp.json()
                assert result["success"] == True
                assert "content" in result["data"]
```

---

*本文档提供Backend服务API调用的完整示例，帮助开发者理解和调试服务间交互。*
