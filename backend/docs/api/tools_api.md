# 工具链API文档

## 📋 **API概述**

Backend工具链提供了RESTful API接口，支持通过HTTP调用各种股票分析工具。

## 🔗 **基础URL**

```
http://localhost:8002/api/v1/tools
```

## 🛠️ **API端点**

### **1. 获取可用工具列表**

```http
GET /api/v1/tools/list
```

**响应示例:**
```json
{
  "success": true,
  "tools": [
    {
      "name": "get_stock_market_data_unified",
      "description": "统一的股票市场数据工具",
      "category": "unified",
      "parameters": {
        "ticker": "str",
        "start_date": "str",
        "end_date": "str"
      }
    }
  ],
  "total": 12
}
```

### **2. 按类别获取工具**

```http
GET /api/v1/tools/category/{category}
```

**参数:**
- `category`: 工具类别 (data, analysis, news, unified)

**响应示例:**
```json
{
  "success": true,
  "category": "unified",
  "tools": [
    {
      "name": "get_stock_market_data_unified",
      "description": "统一的股票市场数据工具",
      "parameters": {
        "ticker": "str",
        "start_date": "str", 
        "end_date": "str"
      }
    }
  ]
}
```

### **3. 调用工具**

```http
POST /api/v1/tools/call
```

**请求体:**
```json
{
  "tool_name": "get_stock_market_data_unified",
  "parameters": {
    "ticker": "000001",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }
}
```

**响应示例:**
```json
{
  "success": true,
  "tool_name": "get_stock_market_data_unified",
  "result": "# 📊 000001 市场数据分析报告\n\n## 基本信息\n...",
  "duration": 2.34,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **4. 获取LLM工具格式**

```http
GET /api/v1/tools/llm/openai
```

**查询参数:**
- `category` (可选): 工具类别筛选

**响应示例:**
```json
{
  "success": true,
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_stock_market_data_unified",
        "description": "统一的股票市场数据工具",
        "parameters": {
          "type": "object",
          "properties": {
            "ticker": {"type": "string"},
            "start_date": {"type": "string"},
            "end_date": {"type": "string"}
          },
          "required": ["ticker", "start_date", "end_date"]
        }
      }
    }
  ]
}
```

### **5. LLM工具调用**

```http
POST /api/v1/tools/llm/call
```

**请求体:**
```json
{
  "function_call": {
    "name": "get_stock_market_data_unified",
    "arguments": "{\"ticker\": \"000001\", \"start_date\": \"2024-01-01\", \"end_date\": \"2024-12-31\"}"
  }
}
```

**响应示例:**
```json
{
  "success": true,
  "tool_name": "get_stock_market_data_unified",
  "result": "# 📊 000001 市场数据分析报告\n...",
  "duration": 2.34,
  "timestamp": "2024-01-15T10:30:00Z",
  "function_call": {
    "name": "get_stock_market_data_unified",
    "arguments": "{\"ticker\": \"000001\", \"start_date\": \"2024-01-01\", \"end_date\": \"2024-12-31\"}"
  }
}
```

### **6. 健康检查**

```http
GET /api/v1/tools/health
```

**响应示例:**
```json
{
  "status": "healthy",
  "total_tools": 12,
  "llm_tools": 12,
  "categories": ["data", "analysis", "news", "unified"],
  "unified_tools_available": 3,
  "last_check": "2024-01-15T10:30:00Z"
}
```

### **7. 根据任务获取推荐工具**

```http
GET /api/v1/tools/task/{task_type}
```

**参数:**
- `task_type`: 任务类型 (stock_analysis, technical_analysis, fundamental_analysis, news_analysis)

**响应示例:**
```json
{
  "success": true,
  "task_type": "stock_analysis",
  "recommended_tools": [
    {
      "type": "function",
      "function": {
        "name": "get_stock_market_data_unified",
        "description": "统一的股票市场数据工具",
        "parameters": {...}
      }
    }
  ]
}
```

## 🔧 **统一工具API**

### **市场数据分析**

```http
POST /api/v1/tools/unified/market
```

**请求体:**
```json
{
  "ticker": "000001",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

### **基本面分析**

```http
POST /api/v1/tools/unified/fundamentals
```

**请求体:**
```json
{
  "ticker": "000001",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

### **新闻情感分析**

```http
POST /api/v1/tools/unified/news
```

**请求体:**
```json
{
  "ticker": "000001",
  "days": 7
}
```

## 📊 **错误处理**

### **错误响应格式**

```json
{
  "success": false,
  "error": "工具不存在: invalid_tool_name",
  "error_code": "TOOL_NOT_FOUND",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **常见错误码**

| 错误码 | 描述 | HTTP状态码 |
|--------|------|-----------|
| `TOOL_NOT_FOUND` | 工具不存在 | 404 |
| `INVALID_PARAMETERS` | 参数无效 | 400 |
| `TOOL_EXECUTION_FAILED` | 工具执行失败 | 500 |
| `TOOLKIT_NOT_INITIALIZED` | 工具链未初始化 | 503 |
| `RATE_LIMIT_EXCEEDED` | 请求频率超限 | 429 |

## 🔐 **认证和授权**

### **API密钥认证**

```http
Authorization: Bearer your_api_key_here
```

### **请求限制**

- 每分钟最多60次请求
- 单次请求超时30秒
- 并发请求限制10个

## 📈 **使用示例**

### **Python客户端**

```python
import aiohttp
import asyncio

async def call_tool_api():
    async with aiohttp.ClientSession() as session:
        # 调用统一市场数据工具
        async with session.post(
            "http://localhost:8002/api/v1/tools/call",
            json={
                "tool_name": "get_stock_market_data_unified",
                "parameters": {
                    "ticker": "000001",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31"
                }
            }
        ) as response:
            result = await response.json()
            print(result)

asyncio.run(call_tool_api())
```

### **JavaScript客户端**

```javascript
async function callToolAPI() {
    const response = await fetch('http://localhost:8002/api/v1/tools/call', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            tool_name: 'get_stock_market_data_unified',
            parameters: {
                ticker: '000001',
                start_date: '2024-01-01',
                end_date: '2024-12-31'
            }
        })
    });
    
    const result = await response.json();
    console.log(result);
}
```

### **cURL示例**

```bash
# 获取工具列表
curl -X GET "http://localhost:8002/api/v1/tools/list"

# 调用工具
curl -X POST "http://localhost:8002/api/v1/tools/call" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_stock_market_data_unified",
    "parameters": {
      "ticker": "000001",
      "start_date": "2024-01-01",
      "end_date": "2024-12-31"
    }
  }'

# 获取LLM工具格式
curl -X GET "http://localhost:8002/api/v1/tools/llm/openai?category=unified"
```

## 🔄 **WebSocket支持**

### **实时工具调用**

```javascript
const ws = new WebSocket('ws://localhost:8002/api/v1/tools/ws');

ws.onopen = function() {
    // 发送工具调用请求
    ws.send(JSON.stringify({
        action: 'call_tool',
        tool_name: 'get_stock_market_data_unified',
        parameters: {
            ticker: '000001',
            start_date: '2024-01-01',
            end_date: '2024-12-31'
        }
    }));
};

ws.onmessage = function(event) {
    const result = JSON.parse(event.data);
    console.log('工具调用结果:', result);
};
```

## 📚 **相关文档**

- [工具链指南](../tools/TOOLKIT_GUIDE.md)
- [配置文档](../configuration/tools_config.md)
- [SDK文档](../sdk/tools_sdk.md)

---

*完整的工具链API文档，支持多种调用方式和集成场景。*
