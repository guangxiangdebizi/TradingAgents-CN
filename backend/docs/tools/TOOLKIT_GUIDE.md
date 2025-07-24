# Backend工具链管理指南

## 📋 **概述**

Backend项目的工具链系统基于tradingagents的设计理念，提供了完整的股票分析工具集，支持LLM Function Calling和智能工具调用。

## 🏗️ **架构设计**

### **核心组件**

```
ToolkitManager (基础工具管理)
    ├── DataTools (数据工具)
    ├── AnalysisTools (分析工具)
    ├── NewsTools (新闻工具)
    └── UnifiedTools (统一工具)

LLMToolkitManager (LLM集成管理)
    ├── 继承 ToolkitManager
    ├── LLM Function Schema生成
    ├── OpenAI Function Calling支持
    └── 智能工具路由
```

### **技术特点**

- ✅ **异步架构** - 支持高并发调用
- ✅ **LLM集成** - 支持Function Calling
- ✅ **统一接口** - 自动识别股票类型
- ✅ **完整日志** - 详细的调用日志
- ✅ **错误处理** - 完善的异常处理
- ✅ **缓存机制** - 内置数据缓存

## 🔧 **工具分类**

### **1. 数据工具 (DataTools)**

| 工具名称 | 描述 | 参数 | 返回值 |
|---------|------|------|--------|
| `get_stock_data` | 获取股票基础数据 | symbol, period | 股票基本信息 |
| `get_financial_data` | 获取财务数据 | symbol, statement_type | 财务报表数据 |
| `get_market_data` | 获取市场数据 | symbol, indicators | 市场指标数据 |

### **2. 分析工具 (AnalysisTools)**

| 工具名称 | 描述 | 参数 | 返回值 |
|---------|------|------|--------|
| `calculate_technical_indicators` | 计算技术指标 | data, indicators | 技术指标结果 |
| `perform_fundamental_analysis` | 基本面分析 | financial_data, market_data | 基本面分析报告 |
| `calculate_valuation` | 估值计算 | financial_data, method | 估值结果 |

### **3. 新闻工具 (NewsTools)**

| 工具名称 | 描述 | 参数 | 返回值 |
|---------|------|------|--------|
| `get_stock_news` | 获取股票新闻 | symbol, days | 新闻数据 |
| `analyze_sentiment` | 情感分析 | text, source | 情感分析结果 |

### **4. 统一工具 (UnifiedTools)** ⭐

| 工具名称 | 描述 | 参数 | 返回值 |
|---------|------|------|--------|
| `get_stock_market_data_unified` | 统一市场数据工具 | ticker, start_date, end_date | 完整市场分析报告 |
| `get_stock_fundamentals_unified` | 统一基本面工具 | ticker, start_date, end_date | 完整基本面分析报告 |
| `get_stock_news_unified` | 统一新闻工具 | ticker, days | 完整新闻情感分析报告 |

## 🚀 **使用方法**

### **1. 基础工具调用**

```python
from backend.analysis_engine.app.tools.toolkit_manager import ToolkitManager

# 初始化工具管理器
toolkit = ToolkitManager()
await toolkit.initialize()

# 调用工具
result = await toolkit.call_tool(
    tool_name="get_stock_data",
    parameters={"symbol": "000001", "period": "1y"}
)

print(result)
```

### **2. LLM集成调用**

```python
from backend.analysis_engine.app.tools.llm_toolkit_manager import LLMToolkitManager

# 初始化LLM工具管理器
llm_toolkit = LLMToolkitManager()
await llm_toolkit.initialize()

# 获取OpenAI Function格式的工具
functions = await llm_toolkit.get_openai_functions(category="unified")

# LLM调用工具
function_call = {
    "name": "get_stock_market_data_unified",
    "arguments": '{"ticker": "000001", "start_date": "2024-01-01", "end_date": "2024-12-31"}'
}

result = await llm_toolkit.call_llm_tool(function_call)
```

### **3. 统一工具调用**

```python
from backend.analysis_engine.app.tools.unified_tools import UnifiedTools

# 初始化统一工具
unified_tools = UnifiedTools()
await unified_tools.initialize()

# 调用统一工具（自动识别股票类型）
result = await unified_tools.get_stock_market_data_unified(
    ticker="000001",  # A股
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# 支持多种股票类型
result_hk = await unified_tools.get_stock_market_data_unified(
    ticker="0700.HK",  # 港股
    start_date="2024-01-01", 
    end_date="2024-12-31"
)

result_us = await unified_tools.get_stock_market_data_unified(
    ticker="AAPL",  # 美股
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

## 📊 **LLM Function Calling集成**

### **OpenAI格式示例**

```python
# 获取工具定义
tools = await llm_toolkit.get_openai_functions()

# 发送给LLM
messages = [
    {"role": "user", "content": "分析平安银行(000001)的市场表现"}
]

response = await openai_client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

# 处理工具调用
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        result = await llm_toolkit.call_llm_tool({
            "name": tool_call.function.name,
            "arguments": tool_call.function.arguments
        })
```

### **DeepSeek格式示例**

```python
# DeepSeek也支持相同的Function Calling格式
response = await deepseek_client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)
```

## 🔍 **日志系统**

### **工具调用日志**

```python
from backend.analysis_engine.app.tools.tool_logging import log_async_tool_call

@log_async_tool_call(tool_name="custom_tool", log_args=True, log_result=True)
async def my_custom_tool(symbol: str, period: str):
    # 工具实现
    return {"result": "success"}
```

### **分析流程日志**

```python
from backend.analysis_engine.app.tools.tool_logging import log_analysis_start, log_analysis_complete

# 记录分析开始
log_analysis_start("technical_analysis", "000001")

# 执行分析
result = await perform_analysis()

# 记录分析完成
log_analysis_complete("technical_analysis", "000001", duration=5.2)
```

## 🎯 **最佳实践**

### **1. 工具选择策略**

- **简单查询**: 使用基础工具
- **复杂分析**: 使用统一工具
- **LLM集成**: 使用LLM工具管理器
- **批量处理**: 使用异步并发调用

### **2. 错误处理**

```python
try:
    result = await toolkit.call_tool("get_stock_data", {"symbol": "000001"})
    if result["success"]:
        data = result["result"]
    else:
        logger.error(f"工具调用失败: {result['error']}")
except Exception as e:
    logger.error(f"工具调用异常: {e}")
```

### **3. 性能优化**

- 使用缓存避免重复调用
- 并发调用多个独立工具
- 合理设置超时时间
- 监控工具调用性能

## 🔧 **扩展开发**

### **添加新工具**

```python
class CustomTools:
    @log_async_tool_call(tool_name="custom_analysis")
    async def custom_analysis(self, symbol: str, method: str) -> Dict[str, Any]:
        """自定义分析工具"""
        # 实现自定义分析逻辑
        return {"result": "analysis_result"}

# 注册到工具管理器
toolkit._register_tool(
    name="custom_analysis",
    description="自定义分析工具",
    category="analysis",
    parameters={"symbol": "str", "method": "str"},
    function=custom_tools.custom_analysis
)
```

### **集成新的LLM提供商**

```python
# 在LLMToolkitManager中添加新的工具格式支持
async def get_claude_functions(self) -> List[Dict[str, Any]]:
    """获取Claude格式的工具定义"""
    # 实现Claude特定的工具格式
    pass
```

## 📚 **相关文档**

- [API文档](../api/tools_api.md)
- [配置指南](../configuration/tools_config.md)
- [故障排除](../troubleshooting/tools_issues.md)
- [性能优化](../performance/tools_optimization.md)

---

*本文档基于tradingagents的工具链设计，提供了完整的Backend工具链使用指南。*
