"""
基础智能体类
定义所有智能体的基础结构和接口
"""

import uuid
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

from backend.shared.logging_config import get_logger

logger = get_logger("agent-service.base_agent")


class AgentType(Enum):
    """智能体类型枚举"""
    # 分析师团队
    FUNDAMENTALS_ANALYST = "fundamentals_analyst"
    MARKET_ANALYST = "market_analyst"
    NEWS_ANALYST = "news_analyst"
    SOCIAL_MEDIA_ANALYST = "social_media_analyst"
    
    # 研究员团队
    BULL_RESEARCHER = "bull_researcher"
    BEAR_RESEARCHER = "bear_researcher"
    
    # 管理层
    RESEARCH_MANAGER = "research_manager"
    RISK_MANAGER = "risk_manager"
    
    # 交易执行
    TRADER = "trader"
    
    # 风险评估团队
    RISKY_DEBATOR = "risky_debator"
    SAFE_DEBATOR = "safe_debator"
    NEUTRAL_DEBATOR = "neutral_debator"


class AgentStatus(Enum):
    """智能体状态枚举"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class TaskType(Enum):
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


@dataclass
class AgentCapability:
    """智能体能力定义"""
    name: str
    description: str
    required_tools: List[str] = field(default_factory=list)
    supported_markets: List[str] = field(default_factory=lambda: ["US", "CN", "HK"])
    max_concurrent_tasks: int = 1
    estimated_duration: int = 60  # 秒


@dataclass
class AgentMetrics:
    """智能体性能指标"""
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_duration: float = 0.0
    last_activity: Optional[datetime] = None
    uptime: float = 0.0
    
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


@dataclass
class TaskContext:
    """任务上下文"""
    task_id: str
    symbol: str
    company_name: str
    market: str
    analysis_date: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "symbol": self.symbol,
            "company_name": self.company_name,
            "market": self.market,
            "analysis_date": self.analysis_date,
            "parameters": self.parameters,
            "metadata": self.metadata
        }


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    agent_id: str
    agent_type: AgentType
    status: str
    result: Dict[str, Any]
    error: Optional[str] = None
    duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "duration": self.duration,
            "timestamp": self.timestamp.isoformat()
        }


class BaseAgent(ABC):
    """基础智能体抽象类"""
    
    def __init__(
        self,
        agent_type: AgentType,
        agent_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.agent_type = agent_type
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.capabilities = self._define_capabilities()
        self.metrics = AgentMetrics()
        self.current_tasks: Dict[str, TaskContext] = {}
        self.created_at = datetime.now()
        self.last_heartbeat = datetime.now()
        
        logger.info(f"🤖 创建智能体: {self.agent_type.value} (ID: {self.agent_id})")
    
    @abstractmethod
    def _define_capabilities(self) -> List[AgentCapability]:
        """定义智能体能力"""
        pass
    
    @abstractmethod
    async def process_task(self, context: TaskContext) -> TaskResult:
        """处理任务 - 子类必须实现"""
        pass
    
    async def execute_task(self, context: TaskContext) -> TaskResult:
        """执行任务的包装方法"""
        start_time = datetime.now()
        
        try:
            # 检查智能体状态
            if self.status == AgentStatus.OFFLINE:
                raise Exception("智能体离线")
            
            if self.status == AgentStatus.ERROR:
                raise Exception("智能体处于错误状态")
            
            # 检查并发限制
            max_concurrent = max(cap.max_concurrent_tasks for cap in self.capabilities)
            if len(self.current_tasks) >= max_concurrent:
                raise Exception(f"智能体繁忙，当前任务数: {len(self.current_tasks)}")
            
            # 更新状态
            self.status = AgentStatus.BUSY
            self.current_tasks[context.task_id] = context
            
            logger.info(f"🚀 {self.agent_type.value} 开始执行任务: {context.task_id}")
            
            # 执行任务
            result = await self.process_task(context)
            
            # 更新指标
            duration = (datetime.now() - start_time).total_seconds()
            self.metrics.total_tasks += 1
            self.metrics.successful_tasks += 1
            self.metrics.last_activity = datetime.now()
            
            # 更新平均持续时间
            if self.metrics.average_duration == 0:
                self.metrics.average_duration = duration
            else:
                self.metrics.average_duration = (
                    self.metrics.average_duration * (self.metrics.total_tasks - 1) + duration
                ) / self.metrics.total_tasks
            
            result.duration = duration
            
            logger.info(f"✅ {self.agent_type.value} 完成任务: {context.task_id} (耗时: {duration:.2f}s)")
            
            return result
            
        except Exception as e:
            # 更新错误指标
            duration = (datetime.now() - start_time).total_seconds()
            self.metrics.total_tasks += 1
            self.metrics.failed_tasks += 1
            self.metrics.last_activity = datetime.now()
            
            error_result = TaskResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status="error",
                result={},
                error=str(e),
                duration=duration
            )
            
            logger.error(f"❌ {self.agent_type.value} 任务失败: {context.task_id} - {e}")
            
            return error_result
            
        finally:
            # 清理任务状态
            if context.task_id in self.current_tasks:
                del self.current_tasks[context.task_id]
            
            # 更新状态
            if len(self.current_tasks) == 0:
                self.status = AgentStatus.IDLE
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 更新心跳
            self.last_heartbeat = datetime.now()
            
            # 检查状态
            if self.status == AgentStatus.ERROR:
                return False
            
            # 检查是否长时间无响应
            if self.metrics.last_activity is not None:
                time_since_activity = (datetime.now() - self.metrics.last_activity).total_seconds()
                if time_since_activity > 3600:  # 1小时无活动
                    logger.warning(f"⚠️ {self.agent_type.value} 长时间无活动: {time_since_activity:.0f}s")
            else:
                # 如果从未有活动，初始化last_activity
                self.metrics.last_activity = datetime.now()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ {self.agent_type.value} 健康检查失败: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "status": self.status.value,
            "capabilities": [cap.__dict__ for cap in self.capabilities],
            "metrics": self.metrics.__dict__,
            "current_tasks": len(self.current_tasks),
            "created_at": self.created_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat()
        }
    
    def can_handle_task(self, task_type, market: str = "US") -> bool:
        """检查是否能处理指定任务"""
        # 处理不同类型的task_type参数
        if hasattr(task_type, 'value'):
            task_type_str = task_type.value
        else:
            task_type_str = str(task_type)

        for capability in self.capabilities:
            if (task_type_str.lower() in capability.name.lower() and
                market in capability.supported_markets):
                return True
        return False
    
    def __str__(self) -> str:
        return f"Agent({self.agent_type.value}, {self.agent_id[:8]})"
    
    def __repr__(self) -> str:
        return self.__str__()
