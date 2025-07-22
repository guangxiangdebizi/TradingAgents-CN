# 🤖 LLM Service 架构设计

## 🎯 **设计目标**

### **核心需求**
1. **统一接口**: 为所有大模型提供标准化API
2. **多提供商支持**: OpenAI、DeepSeek、阿里百炼、Google Gemini等
3. **智能路由**: 根据任务类型自动选择最适合的模型
4. **成本控制**: Token统计、费用计算、配额管理
5. **高可用性**: 故障转移、负载均衡、降级策略

### **服务职责**
- 🔌 **模型适配**: 统一不同提供商的API差异
- 📊 **使用统计**: Token消耗、成本计算、性能监控
- ⚡ **智能调度**: 根据模型特点和任务需求智能路由
- 🛡️ **安全管理**: API密钥管理、访问控制、审计日志
- 🔄 **故障处理**: 自动重试、降级、熔断机制

## 🏗️ **架构设计**

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM Service                              │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   API Gateway   │  │  Model Router   │  │   Usage     │  │
│  │   统一入口       │  │   智能路由       │  │  Tracker    │  │
│  │                 │  │                 │  │  使用统计    │  │
│  │ • 认证授权      │  │ • 模型选择      │  │ • Token计数 │  │
│  │ • 请求验证      │  │ • 负载均衡      │  │ • 成本计算  │  │
│  │ • 限流控制      │  │ • 故障转移      │  │ • 配额管理  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
│           │                       │                │        │
│           └───────────────────────┼────────────────┘        │
│                                   │                         │
│  ┌─────────────────────────────────┼─────────────────────────┐ │
│  │              Model Adapters     │                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │ │
│  │  │   OpenAI    │  │  DeepSeek   │  │   DashScope     │  │ │
│  │  │   Adapter   │  │   Adapter   │  │   (阿里百炼)     │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │ │
│  │  │   Google    │  │   Claude    │  │    Custom       │  │ │
│  │  │   Gemini    │  │   Adapter   │  │   Adapters      │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                               │
                               │ HTTP API
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Client Services                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ TradingAgents   │  │ Analysis Engine │  │   Web UI    │  │
│  │     Core        │  │                 │  │             │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🔌 **统一API接口**

### **1. 聊天完成接口**
```http
POST /api/v1/chat/completions
Content-Type: application/json

{
  "model": "auto",  // 或指定具体模型
  "messages": [
    {"role": "system", "content": "你是一个专业的股票分析师"},
    {"role": "user", "content": "分析AAPL的投资价值"}
  ],
  "task_type": "financial_analysis",  // 任务类型，用于智能路由
  "max_tokens": 2000,
  "temperature": 0.1,
  "stream": false
}
```

### **2. 模型信息接口**
```http
GET /api/v1/models
```

### **3. 使用统计接口**
```http
GET /api/v1/usage/stats
GET /api/v1/usage/costs
```

## 🤖 **模型适配器设计**

### **基础适配器接口**
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, AsyncGenerator

class BaseLLMAdapter(ABC):
    """LLM适配器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = config.get("provider_name")
        self.model_name = config.get("model_name")
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
        
    @abstractmethod
    async def chat_completion(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """聊天完成"""
        pass
    
    @abstractmethod
    async def chat_completion_stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator:
        """流式聊天完成"""
        pass
    
    @abstractmethod
    def calculate_tokens(self, text: str) -> int:
        """计算Token数量"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass
```

### **DeepSeek适配器示例**
```python
class DeepSeekAdapter(BaseLLMAdapter):
    """DeepSeek模型适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url or "https://api.deepseek.com"
        )
    
    async def chat_completion(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """DeepSeek聊天完成"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 2000),
                temperature=kwargs.get("temperature", 0.1),
                stream=False
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "provider": "deepseek"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "deepseek"
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "deepseek",
            "model": self.model_name,
            "max_tokens": 32768,
            "supports_streaming": True,
            "cost_per_1k_tokens": {
                "input": 0.0014,  # $0.14/1M tokens
                "output": 0.0028  # $0.28/1M tokens
            },
            "strengths": ["中文理解", "代码生成", "推理能力"],
            "best_for": ["financial_analysis", "code_generation", "reasoning"]
        }
```

## 🧠 **智能路由策略**

### **任务类型映射**
```python
TASK_MODEL_MAPPING = {
    "financial_analysis": {
        "primary": ["deepseek-chat", "gpt-4"],
        "fallback": ["qwen-plus", "gpt-3.5-turbo"]
    },
    "code_generation": {
        "primary": ["deepseek-coder", "gpt-4"],
        "fallback": ["qwen-coder", "claude-3"]
    },
    "data_extraction": {
        "primary": ["gpt-4", "qwen-plus"],
        "fallback": ["gpt-3.5-turbo", "deepseek-chat"]
    },
    "translation": {
        "primary": ["qwen-plus", "gpt-4"],
        "fallback": ["deepseek-chat"]
    }
}
```

### **智能路由器**
```python
class ModelRouter:
    """智能模型路由器"""
    
    def __init__(self, adapters: Dict[str, BaseLLMAdapter]):
        self.adapters = adapters
        self.health_status = {}
        self.performance_metrics = {}
    
    async def route_request(self, task_type: str, model_preference: str = "auto") -> str:
        """路由请求到最适合的模型"""
        
        # 1. 如果指定了具体模型，直接使用
        if model_preference != "auto" and model_preference in self.adapters:
            if await self._is_model_healthy(model_preference):
                return model_preference
        
        # 2. 根据任务类型选择模型
        candidates = TASK_MODEL_MAPPING.get(task_type, {}).get("primary", [])
        
        # 3. 检查模型健康状态和性能
        for model in candidates:
            if model in self.adapters and await self._is_model_healthy(model):
                return model
        
        # 4. 使用备用模型
        fallback_models = TASK_MODEL_MAPPING.get(task_type, {}).get("fallback", [])
        for model in fallback_models:
            if model in self.adapters and await self._is_model_healthy(model):
                return model
        
        # 5. 最后使用任何可用的模型
        for model, adapter in self.adapters.items():
            if await self._is_model_healthy(model):
                return model
        
        raise Exception("没有可用的模型")
    
    async def _is_model_healthy(self, model: str) -> bool:
        """检查模型健康状态"""
        try:
            adapter = self.adapters[model]
            return await adapter.health_check()
        except Exception:
            return False
```

## 📊 **使用统计和成本控制**

### **使用统计器**
```python
class UsageTracker:
    """使用统计器"""
    
    def __init__(self, redis_client=None, mongodb_client=None):
        self.redis = redis_client
        self.mongodb = mongodb_client
    
    async def track_usage(self, user_id: str, model: str, usage: Dict[str, int]):
        """记录使用情况"""
        timestamp = datetime.now()
        
        # 计算成本
        cost = self._calculate_cost(model, usage)
        
        # 记录到Redis (实时统计)
        if self.redis:
            await self._update_redis_stats(user_id, model, usage, cost)
        
        # 记录到MongoDB (持久化)
        if self.mongodb:
            await self._save_usage_record(user_id, model, usage, cost, timestamp)
    
    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        """计算使用成本"""
        model_pricing = MODEL_PRICING.get(model, {})
        
        input_cost = usage.get("prompt_tokens", 0) * model_pricing.get("input_cost_per_1k", 0) / 1000
        output_cost = usage.get("completion_tokens", 0) * model_pricing.get("output_cost_per_1k", 0) / 1000
        
        return input_cost + output_cost
```

## 🚀 **服务部署**

### **Docker配置**
```dockerfile
# backend/llm-service/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/

EXPOSE 8004

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
```

### **Docker Compose集成**
```yaml
# docker-compose.microservices.yml
services:
  llm-service:
    build: ./llm-service
    ports: ["8004:8004"]
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    depends_on: [redis, mongodb]
    
  analysis-engine:
    build: ./analysis-engine
    environment:
      - LLM_SERVICE_URL=http://llm-service:8004
    depends_on: [llm-service, data-service]
```

## 🔧 **客户端调用示例**

### **Analysis Engine中的调用**
```python
class LLMClient:
    """LLM服务客户端"""
    
    def __init__(self, llm_service_url: str):
        self.base_url = llm_service_url
    
    async def analyze_stock(self, symbol: str, data: str) -> str:
        """调用LLM进行股票分析"""
        messages = [
            {"role": "system", "content": "你是一个专业的股票分析师"},
            {"role": "user", "content": f"请分析{symbol}的投资价值：\n{data}"}
        ]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/v1/chat/completions",
                json={
                    "messages": messages,
                    "task_type": "financial_analysis",
                    "max_tokens": 2000,
                    "temperature": 0.1
                }
            ) as response:
                result = await response.json()
                return result.get("content", "")
```

## 💡 **扩展优势**

1. **🔌 易于集成新模型**: 只需实现BaseLLMAdapter接口
2. **📊 统一监控**: 所有模型的使用情况集中管理
3. **💰 成本优化**: 根据任务选择最经济的模型
4. **⚡ 性能优化**: 智能路由到最快的可用模型
5. **🛡️ 安全管理**: API密钥集中管理，访问控制
6. **🔄 高可用**: 自动故障转移，降级策略

这样的设计让大模型调用变得标准化、可管理、可扩展！🚀
