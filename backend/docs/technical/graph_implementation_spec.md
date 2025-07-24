# Backend图实现技术规范

## 📋 **概述**

本文档提供Backend图实现的详细技术规范，包括代码结构、接口定义、状态管理和部署要求。

## 🏗️ **核心组件规范**

### **1. TradingGraph类规范**

#### **类定义**
```python
class TradingGraph:
    """Backend交易图引擎"""
    
    def __init__(self):
        self.graph: Optional[StateGraph] = None
        self.compiled_graph = None
        self.toolkit_manager: Optional[LLMToolkitManager] = None
        self.agent_nodes: Optional[AgentNodes] = None
        self.conditional_logic: Optional[ConditionalLogic] = None
        self.tool_nodes: Dict[str, ToolNode] = {}
        self.config: Dict[str, Any] = {}
```

#### **核心方法**
```python
async def initialize(self) -> None:
    """初始化图引擎"""
    
async def analyze_stock(self, symbol: str, analysis_date: str = None) -> Dict[str, Any]:
    """分析股票 - 主要入口点"""
    
async def get_graph_visualization(self) -> str:
    """获取图的可视化"""
    
async def cleanup(self) -> None:
    """清理资源"""
```

#### **配置规范**
```python
DEFAULT_CONFIG = {
    "max_debate_rounds": 3,
    "max_risk_rounds": 2,
    "selected_analysts": ["market", "fundamentals", "news", "social"],
    "timeout_per_node": 120,  # 秒
    "retry_attempts": 3,
    "enable_parallel": False
}
```

### **2. ConditionalLogic类规范**

#### **核心方法签名**
```python
def should_continue_market(self, state: GraphState) -> str:
    """返回: "tools_market" | "clear_market" """

def should_continue_fundamentals(self, state: GraphState) -> str:
    """返回: "tools_fundamentals" | "clear_fundamentals" """

def should_continue_news(self, state: GraphState) -> str:
    """返回: "tools_news" | "clear_news" """

def should_continue_social(self, state: GraphState) -> str:
    """返回: "tools_social" | "clear_social" """

def should_continue_debate(self, state: GraphState) -> str:
    """返回: "bull_researcher" | "bear_researcher" | "research_manager" """

def should_continue_risk_analysis(self, state: GraphState) -> str:
    """返回: "risky_analyst" | "safe_analyst" | "neutral_analyst" | "risk_manager" """
```

#### **状态追踪规范**
```python
# 辩论状态结构
debate_state = {
    "count": int,                    # 当前轮数
    "current_speaker": str,          # 当前发言者 ("bull" | "bear" | None)
    "bull_arguments": List[Dict],    # 多头论点历史
    "bear_arguments": List[Dict]     # 空头论点历史
}

# 风险分析状态结构
risk_state = {
    "count": int,                    # 当前轮数
    "current_speaker": str,          # 当前发言者 ("risky" | "safe" | "neutral" | None)
    "risky_arguments": List[Dict],   # 激进论点历史
    "safe_arguments": List[Dict],    # 保守论点历史
    "neutral_arguments": List[Dict]  # 中性论点历史
}
```

### **3. GraphState规范**

#### **必需字段**
```python
# 基本信息 (必需)
symbol: str                    # 股票代码，非空
company_name: str             # 公司名称
analysis_type: str            # 分析类型
current_date: str             # 当前日期 (YYYY-MM-DD格式)

# 执行状态 (必需)
current_step: str             # 当前步骤名称
completed_steps: List[str]    # 已完成步骤列表
next_steps: List[str]         # 下一步骤列表
messages: List[Dict[str, Any]] # 消息历史
errors: List[str]             # 错误列表
metadata: Dict[str, Any]      # 元数据
```

#### **可选字段**
```python
# 数据字段 (可选，根据分析进度填充)
stock_data: Optional[Dict[str, Any]]
financial_data: Optional[Dict[str, Any]]
market_data: Optional[Dict[str, Any]]
news_data: Optional[Dict[str, Any]]

# 分析结果 (可选，根据分析进度填充)
fundamentals_report: Optional[str]
technical_report: Optional[str]
news_report: Optional[str]
sentiment_report: Optional[str]

# 最终输出 (可选，分析完成后填充)
final_recommendation: Optional[Dict[str, Any]]
investment_plan: Optional[str]
risk_assessment: Optional[Dict[str, Any]]
```

### **4. AgentNodes类规范**

#### **节点方法签名**
```python
async def {agent_type}_node(self, state: GraphState) -> GraphState:
    """
    Agent节点标准签名
    
    参数:
        state: 当前图状态
    
    返回:
        更新后的图状态
    
    异常处理:
        - 捕获所有异常并记录到state["errors"]
        - 确保返回有效的GraphState
    """
```

#### **微服务调用规范**
```python
async def _call_agent_service(
    self, 
    agent_type: str, 
    action: str, 
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    微服务调用标准方法
    
    参数:
        agent_type: Agent类型 ("market_analyst", "bull_researcher", etc.)
        action: 操作类型 ("analyze", "research", "assess", etc.)
        data: 请求数据
    
    返回:
        {
            "success": bool,
            "data": Any,
            "error": Optional[str]
        }
    """
```

## 🔄 **执行流程规范**

### **节点执行标准**

#### **1. 节点入口检查**
```python
async def node_function(state: GraphState) -> GraphState:
    # 1. 日志记录
    logger.info(f"🔄 执行{node_name}节点")
    
    # 2. 状态验证
    if not state.get("symbol"):
        state["errors"].append("缺少股票代码")
        return state
    
    # 3. 执行逻辑
    try:
        # 节点具体逻辑
        pass
    except Exception as e:
        # 4. 异常处理
        error_msg = f"{node_name}节点异常: {e}"
        state["errors"].append(error_msg)
        logger.error(f"❌ {error_msg}")
    
    # 5. 状态更新
    update_state_step(state, node_name)
    
    return state
```

#### **2. 微服务调用标准**
```python
# 调用微服务
result = await self._call_agent_service(
    agent_type="market_analyst",
    action="analyze",
    data={
        "symbol": state["symbol"],
        "context": {
            "current_date": state["current_date"],
            "existing_data": state.get("stock_data")
        }
    }
)

# 结果处理
if result.get("success"):
    # 成功处理
    state["technical_report"] = result.get("analysis", "")
    add_message(state, "market_analyst", result.get("analysis", ""), "analysis")
    logger.info("✅ 市场分析完成")
else:
    # 失败处理
    error_msg = f"市场分析失败: {result.get('error', 'Unknown error')}"
    state["errors"].append(error_msg)
    logger.error(f"❌ {error_msg}")
```

### **条件逻辑标准**

#### **1. 工具调用条件**
```python
def should_continue_{analyst_type}(self, state: GraphState) -> str:
    """
    工具调用条件检查标准
    
    检查顺序:
    1. 数据完整性检查
    2. 分析完成度检查
    3. 错误状态检查
    
    返回:
        "tools_{analyst_type}" - 需要调用工具
        "clear_{analyst_type}" - 分析完成，清理消息
    """
    
    # 检查是否需要数据
    if not state.get("required_data"):
        return f"tools_{analyst_type}"
    
    # 检查分析是否完成
    if not state.get("analysis_report"):
        return f"tools_{analyst_type}"
    
    # 分析完成
    return f"clear_{analyst_type}"
```

#### **2. 辩论条件**
```python
def should_continue_debate(self, state: GraphState) -> str:
    """
    辩论条件检查标准
    
    检查顺序:
    1. 轮数限制检查
    2. 共识检查
    3. 发言者轮换
    
    返回:
        "bull_researcher" - 轮到多头发言
        "bear_researcher" - 轮到空头发言
        "research_manager" - 结束辩论
    """
    
    # 检查轮数限制
    if self.debate_state["count"] >= 2 * self.max_debate_rounds:
        self._reset_debate_state()
        return "research_manager"
    
    # 检查共识 (可选)
    if self.check_early_consensus(state):
        self._reset_debate_state()
        return "research_manager"
    
    # 轮换发言者
    current_speaker = self.debate_state.get("current_speaker")
    if current_speaker == "bear":
        self.debate_state["current_speaker"] = "bull"
        self.debate_state["count"] += 1
        return "bull_researcher"
    else:
        self.debate_state["current_speaker"] = "bear"
        return "bear_researcher"
```

## 📊 **状态管理规范**

### **状态更新标准**

#### **1. 步骤更新**
```python
def update_state_step(state: GraphState, step_name: str) -> GraphState:
    """标准状态步骤更新"""
    
    # 添加到已完成步骤
    if step_name not in state["completed_steps"]:
        state["completed_steps"].append(step_name)
    
    # 更新当前步骤
    state["current_step"] = step_name
    
    # 更新时间戳
    state["metadata"]["last_updated"] = datetime.now().isoformat()
    
    return state
```

#### **2. 消息添加**
```python
def add_message(
    state: GraphState, 
    agent_type: str, 
    content: str, 
    message_type: str = "analysis"
) -> GraphState:
    """标准消息添加"""
    
    message = {
        "agent_type": agent_type,
        "agent_name": f"{agent_type}_agent",
        "message_type": message_type,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "metadata": {}
    }
    
    state["messages"].append(message)
    return state
```

#### **3. 辩论历史管理**
```python
def add_debate_entry(
    state: GraphState, 
    speaker: str, 
    content: str
) -> GraphState:
    """添加辩论条目"""
    
    debate_entry = {
        "speaker": speaker,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "round": len(state.get("debate_history", [])) + 1
    }
    
    if "debate_history" not in state:
        state["debate_history"] = []
    
    state["debate_history"].append(debate_entry)
    return state
```

## 🔧 **API接口规范**

### **分析接口**
```python
POST /api/v1/analysis/graph/analyze
Content-Type: application/json

# 请求体
{
    "symbol": "000001",                    # 必需: 股票代码
    "analysis_type": "comprehensive",     # 可选: 分析类型
    "analysis_date": "2024-01-22",       # 可选: 分析日期
    "config": {                           # 可选: 配置参数
        "max_debate_rounds": 3,
        "max_risk_rounds": 2,
        "selected_analysts": ["market", "fundamentals", "news"]
    }
}

# 响应体
{
    "success": true,
    "data": {
        "analysis_id": "uuid",
        "symbol": "000001",
        "status": "completed",
        "result": {
            "final_recommendation": {...},
            "investment_plan": "...",
            "risk_assessment": {...},
            "reports": {...},
            "debate_summary": {...},
            "risk_summary": {...}
        },
        "metadata": {
            "start_time": "2024-01-22T10:00:00Z",
            "end_time": "2024-01-22T10:05:30Z",
            "duration": 330,
            "total_steps": 15,
            "completed_steps": 15
        }
    }
}
```

### **状态查询接口**
```python
GET /api/v1/analysis/graph/status/{analysis_id}

# 响应体
{
    "success": true,
    "data": {
        "analysis_id": "uuid",
        "status": "running",           # running | completed | failed
        "current_step": "bull_researcher",
        "progress": {
            "completed_steps": 8,
            "total_steps": 15,
            "percentage": 53.3
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

### **可视化接口**
```python
GET /api/v1/analysis/graph/visualization

# 响应体
{
    "success": true,
    "data": {
        "mermaid_diagram": "graph TD\n    A[Start] --> B[Market Analyst]\n    ...",
        "execution_path": [
            "market_analyst",
            "fundamentals_analyst", 
            "bull_researcher",
            "bear_researcher",
            "research_manager"
        ],
        "node_status": {
            "market_analyst": "completed",
            "fundamentals_analyst": "completed",
            "bull_researcher": "running"
        }
    }
}
```

## 🚀 **部署规范**

### **环境要求**
```yaml
# 最低要求
python: ">=3.10"
memory: "2GB"
cpu: "2 cores"

# 推荐配置
python: "3.11"
memory: "4GB"
cpu: "4 cores"

# 依赖包
dependencies:
  - langgraph>=0.0.40
  - langchain>=0.1.0
  - aiohttp>=3.8.0
  - pydantic>=2.0.0
```

### **配置文件**
```yaml
# config/graph_config.yaml
graph:
  max_debate_rounds: 3
  max_risk_rounds: 2
  timeout_per_node: 120
  retry_attempts: 3
  enable_parallel: false

services:
  agent_service_url: "http://agent-service:8005"
  llm_service_url: "http://llm-service:8004"
  data_service_url: "http://data-service:8003"

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### **监控指标**
```python
# 关键监控指标
metrics = {
    "graph_execution_time": "图执行总时间",
    "node_execution_time": "单个节点执行时间", 
    "debate_rounds_count": "辩论轮数统计",
    "risk_analysis_rounds_count": "风险分析轮数统计",
    "error_rate": "错误率",
    "success_rate": "成功率",
    "concurrent_executions": "并发执行数"
}
```

---

*本技术规范为Backend图实现提供详细的开发和部署指导，确保实现的一致性和质量。*
