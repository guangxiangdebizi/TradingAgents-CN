"""
中性辩论者智能体
在风险评估辩论中持中性观点
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.shared.logging_config import get_logger
from backend.shared.clients.llm_client import LLMClient

from ..base_agent import BaseAgent, AgentType, AgentCapability, TaskContext, TaskResult

logger = get_logger("agent-service.neutral_debator")


class NeutralDebator(BaseAgent):
    """中性辩论者智能体"""
    
    def __init__(self, agent_type: AgentType, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_type, agent_id, config)
        self.llm_client = LLMClient()
        
        logger.info(f"🏗️ 中性辩论者初始化完成: {self.agent_id}")
    
    def _define_capabilities(self) -> List[AgentCapability]:
        """定义智能体能力"""
        return [
            AgentCapability(
                name="neutral_debate",
                description="中性辩论 - 在风险评估中提出平衡观点",
                required_tools=["debate_analysis", "risk_modeling"],
                supported_markets=["US", "CN", "HK"],
                max_concurrent_tasks=2,
                estimated_duration=45
            )
        ]
    
    async def process_task(self, context: TaskContext) -> TaskResult:
        """处理中性辩论任务"""
        try:
            logger.info(f"⚖️ 开始中性辩论: {context.symbol}")
            
            # 模拟中性观点
            result = {
                "analysis_type": "neutral_debate",
                "symbol": context.symbol,
                "position": "neutral",
                "stance": "平衡风险与收益",
                "arguments": [
                    "需要综合考虑多方面因素",
                    "风险和机会并存",
                    "建议采用分散化策略"
                ],
                "risk_tolerance": "medium",
                "recommended_allocation": 0.08,
                "confidence": 0.6,
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
            logger.error(f"❌ 中性辩论失败: {context.symbol} - {e}")
            raise
