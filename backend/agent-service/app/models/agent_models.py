"""
智能体相关的数据模型
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class AgentTypeEnum(str, Enum):
    """智能体类型枚举"""
    FUNDAMENTALS_ANALYST = "fundamentals_analyst"
    MARKET_ANALYST = "market_analyst"
    NEWS_ANALYST = "news_analyst"
    SOCIAL_MEDIA_ANALYST = "social_media_analyst"
    BULL_RESEARCHER = "bull_researcher"
    BEAR_RESEARCHER = "bear_researcher"
    RESEARCH_MANAGER = "research_manager"
    RISK_MANAGER = "risk_manager"
    TRADER = "trader"
    RISKY_DEBATOR = "risky_debator"
    SAFE_DEBATOR = "safe_debator"
    NEUTRAL_DEBATOR = "neutral_debator"


class AgentStatusEnum(str, Enum):
    """智能体状态枚举"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class TaskTypeEnum(str, Enum):
    """任务类型枚举"""
    FUNDAMENTALS_ANALYSIS = "fundamentals_analysis"
    TECHNICAL_ANALYSIS = "technical_analysis"
    NEWS_ANALYSIS = "news_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    BULL_RESEARCH = "bull_research"
    BEAR_RESEARCH = "bear_research"
    RISK_ASSESSMENT = "risk_assessment"
    RESEARCH_MANAGEMENT = "research_management"
    TRADING_DECISION = "trading_decision"
    DEBATE_PARTICIPATION = "debate_participation"


class AgentCapabilityModel(BaseModel):
    """智能体能力模型"""
    name: str = Field(..., description="能力名称")
    description: str = Field(..., description="能力描述")
    required_tools: List[str] = Field(default_factory=list, description="所需工具")
    supported_markets: List[str] = Field(default_factory=lambda: ["US", "CN", "HK"], description="支持的市场")
    max_concurrent_tasks: int = Field(default=1, description="最大并发任务数")
    estimated_duration: int = Field(default=60, description="预估执行时间（秒）")


class AgentMetricsModel(BaseModel):
    """智能体性能指标模型"""
    total_tasks: int = Field(default=0, description="总任务数")
    successful_tasks: int = Field(default=0, description="成功任务数")
    failed_tasks: int = Field(default=0, description="失败任务数")
    average_duration: float = Field(default=0.0, description="平均执行时间")
    last_activity: Optional[datetime] = Field(default=None, description="最后活动时间")
    uptime: float = Field(default=0.0, description="运行时间")
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_tasks == 0:
            return 0.0
        return self.successful_tasks / self.total_tasks
    
    @property
    def failure_rate(self) -> float:
        """失败率"""
        if self.total_tasks == 0:
            return 0.0
        return self.failed_tasks / self.total_tasks


class AgentInfoModel(BaseModel):
    """智能体信息模型"""
    agent_id: str = Field(..., description="智能体ID")
    agent_type: AgentTypeEnum = Field(..., description="智能体类型")
    status: AgentStatusEnum = Field(..., description="智能体状态")
    capabilities: List[AgentCapabilityModel] = Field(default_factory=list, description="智能体能力")
    metrics: AgentMetricsModel = Field(default_factory=AgentMetricsModel, description="性能指标")
    current_tasks: int = Field(default=0, description="当前任务数")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    last_heartbeat: datetime = Field(default_factory=datetime.now, description="最后心跳时间")


class AgentRequest(BaseModel):
    """智能体请求模型"""
    agent_type: AgentTypeEnum = Field(..., description="智能体类型")
    task_type: TaskTypeEnum = Field(..., description="任务类型")
    symbol: str = Field(..., description="股票代码")
    company_name: str = Field(..., description="公司名称")
    market: str = Field(default="US", description="市场")
    analysis_date: str = Field(..., description="分析日期")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="任务参数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    priority: str = Field(default="normal", description="任务优先级")
    timeout: int = Field(default=300, description="超时时间（秒）")


class AgentResponse(BaseModel):
    """智能体响应模型"""
    task_id: str = Field(..., description="任务ID")
    agent_id: str = Field(..., description="智能体ID")
    agent_type: AgentTypeEnum = Field(..., description="智能体类型")
    status: str = Field(..., description="执行状态")
    result: Dict[str, Any] = Field(default_factory=dict, description="执行结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    duration: float = Field(default=0.0, description="执行时间")
    timestamp: datetime = Field(default_factory=datetime.now, description="完成时间")


class DebateRequest(BaseModel):
    """辩论请求模型"""
    debate_id: str = Field(..., description="辩论ID")
    topic: str = Field(..., description="辩论主题")
    participants: List[AgentTypeEnum] = Field(..., description="参与者类型")
    context: Dict[str, Any] = Field(default_factory=dict, description="辩论上下文")
    rules: Dict[str, Any] = Field(default_factory=dict, description="辩论规则")
    max_rounds: int = Field(default=3, description="最大轮数")
    timeout_per_round: int = Field(default=120, description="每轮超时时间（秒）")


class DebateRound(BaseModel):
    """辩论轮次模型"""
    round_number: int = Field(..., description="轮次编号")
    agent_id: str = Field(..., description="发言智能体ID")
    agent_type: AgentTypeEnum = Field(..., description="智能体类型")
    position: str = Field(..., description="立场（bull/bear/neutral）")
    argument: str = Field(..., description="论点")
    evidence: List[str] = Field(default_factory=list, description="证据")
    timestamp: datetime = Field(default_factory=datetime.now, description="发言时间")
    duration: float = Field(default=0.0, description="发言时长")


class DebateResponse(BaseModel):
    """辩论响应模型"""
    debate_id: str = Field(..., description="辩论ID")
    status: str = Field(..., description="辩论状态")
    topic: str = Field(..., description="辩论主题")
    participants: List[str] = Field(..., description="参与者ID")
    rounds: List[DebateRound] = Field(default_factory=list, description="辩论轮次")
    consensus: Optional[Dict[str, Any]] = Field(default=None, description="共识结果")
    final_decision: Optional[Dict[str, Any]] = Field(default=None, description="最终决策")
    total_duration: float = Field(default=0.0, description="总时长")
    started_at: datetime = Field(default_factory=datetime.now, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")


class CollaborationRequest(BaseModel):
    """协作请求模型"""
    collaboration_id: str = Field(..., description="协作ID")
    workflow_type: str = Field(..., description="工作流类型")
    participants: List[AgentTypeEnum] = Field(..., description="参与智能体类型")
    context: Dict[str, Any] = Field(default_factory=dict, description="协作上下文")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="协作参数")
    execution_mode: str = Field(default="sequential", description="执行模式（sequential/parallel）")
    timeout: int = Field(default=600, description="总超时时间（秒）")


class CollaborationStep(BaseModel):
    """协作步骤模型"""
    step_id: str = Field(..., description="步骤ID")
    step_name: str = Field(..., description="步骤名称")
    agent_type: AgentTypeEnum = Field(..., description="执行智能体类型")
    agent_id: str = Field(..., description="执行智能体ID")
    status: str = Field(..., description="步骤状态")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="输入数据")
    output_data: Dict[str, Any] = Field(default_factory=dict, description="输出数据")
    error: Optional[str] = Field(default=None, description="错误信息")
    started_at: datetime = Field(default_factory=datetime.now, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    duration: float = Field(default=0.0, description="执行时长")


class CollaborationResponse(BaseModel):
    """协作响应模型"""
    collaboration_id: str = Field(..., description="协作ID")
    workflow_type: str = Field(..., description="工作流类型")
    status: str = Field(..., description="协作状态")
    steps: List[CollaborationStep] = Field(default_factory=list, description="执行步骤")
    final_result: Dict[str, Any] = Field(default_factory=dict, description="最终结果")
    total_duration: float = Field(default=0.0, description="总执行时长")
    started_at: datetime = Field(default_factory=datetime.now, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")


class SystemStatusModel(BaseModel):
    """系统状态模型"""
    total_agents: int = Field(..., description="总智能体数")
    active_agents: int = Field(..., description="活跃智能体数")
    busy_agents: int = Field(..., description="繁忙智能体数")
    error_agents: int = Field(..., description="错误智能体数")
    idle_agents: int = Field(..., description="空闲智能体数")
    type_statistics: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="类型统计")
    timestamp: datetime = Field(default_factory=datetime.now, description="统计时间")


class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="健康状态")
    components: Dict[str, bool] = Field(default_factory=dict, description="组件状态")
    timestamp: datetime = Field(default_factory=datetime.now, description="检查时间")
    details: Optional[Dict[str, Any]] = Field(default=None, description="详细信息")


class AgentRegistrationRequest(BaseModel):
    """智能体注册请求模型"""
    agent_type: AgentTypeEnum = Field(..., description="智能体类型")
    config: Dict[str, Any] = Field(default_factory=dict, description="配置参数")
    capabilities: List[AgentCapabilityModel] = Field(default_factory=list, description="智能体能力")


class AgentRegistrationResponse(BaseModel):
    """智能体注册响应模型"""
    agent_id: str = Field(..., description="智能体ID")
    agent_type: AgentTypeEnum = Field(..., description="智能体类型")
    status: str = Field(..., description="注册状态")
    message: str = Field(..., description="注册消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="注册时间")
