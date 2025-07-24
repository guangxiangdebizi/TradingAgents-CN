"""
研究经理智能体
负责协调和整合各分析师的研究结果
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.shared.logging_config import get_logger
from backend.shared.clients.llm_client import LLMClient

from ..base_agent import BaseAgent, AgentType, AgentCapability, TaskContext, TaskResult

logger = get_logger("agent-service.research_manager")


class ResearchManager(BaseAgent):
    """研究经理智能体"""
    
    def __init__(self, agent_type: AgentType, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_type, agent_id, config)
        self.llm_client = LLMClient()
        
        logger.info(f"🏗️ 研究经理初始化完成: {self.agent_id}")
    
    def _define_capabilities(self) -> List[AgentCapability]:
        """定义智能体能力"""
        return [
            AgentCapability(
                name="research_management",
                description="研究管理 - 整合和协调各分析师的研究结果",
                required_tools=["aggregate_analysis", "quality_control"],
                supported_markets=["US", "CN", "HK"],
                max_concurrent_tasks=1,
                estimated_duration=120
            )
        ]
    
    async def process_task(self, context: TaskContext) -> TaskResult:
        """处理研究管理任务"""
        try:
            logger.info(f"👔 开始研究管理: {context.symbol}")
            
            # 模拟研究管理结果
            result = {
                "analysis_type": "research_management",
                "symbol": context.symbol,
                "overall_recommendation": "buy",
                "confidence": 0.75,
                "research_quality_score": 0.85,
                "consensus_strength": 0.8,
                "key_insights": [
                    "基本面分析显示公司财务健康",
                    "技术分析表明上涨趋势",
                    "新闻情感整体积极"
                ],
                "risk_assessment": "中等风险",
                "action_plan": "建议分批买入",
                "analyst_id": self.agent_id,
                "timestamp": datetime.now().isoformat()
            }
            
            return TaskResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status="success",
                result=result
            )
            
        except Exception as e:
            logger.error(f"❌ 研究管理失败: {context.symbol} - {e}")
            raise
