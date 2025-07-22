"""
看跌研究员智能体
负责从谨慎角度进行风险研究
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.shared.logging_config import get_logger
from backend.shared.clients.llm_client import LLMClient
from backend.shared.clients.data_client import DataClient

from ..base_agent import BaseAgent, AgentType, AgentCapability, TaskContext, TaskResult

logger = get_logger("agent-service.bear_researcher")


class BearResearcher(BaseAgent):
    """看跌研究员智能体"""
    
    def __init__(self, agent_type: AgentType, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_type, agent_id, config)
        self.llm_client = LLMClient()
        self.data_client = DataClient()
        
        logger.info(f"🏗️ 看跌研究员初始化完成: {self.agent_id}")
    
    def _define_capabilities(self) -> List[AgentCapability]:
        """定义智能体能力"""
        return [
            AgentCapability(
                name="bear_research",
                description="看跌研究 - 从谨慎角度分析投资风险",
                required_tools=["get_market_data", "get_financial_data"],
                supported_markets=["US", "CN", "HK"],
                max_concurrent_tasks=2,
                estimated_duration=90
            )
        ]
    
    async def process_task(self, context: TaskContext) -> TaskResult:
        """处理看跌研究任务"""
        try:
            logger.info(f"📉 开始看跌研究: {context.symbol}")
            
            # 模拟看跌研究结果
            result = {
                "analysis_type": "bear_research",
                "symbol": context.symbol,
                "recommendation": "sell",
                "confidence": 0.7,
                "target_price": 90.0,
                "downside_risk": 0.20,
                "bear_factors": [
                    "估值过高",
                    "竞争加剧",
                    "宏观经济风险",
                    "监管压力增加"
                ],
                "risk_catalysts": ["监管变化", "竞争对手威胁"],
                "time_horizon": "3-6个月",
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
            logger.error(f"❌ 看跌研究失败: {context.symbol} - {e}")
            raise
