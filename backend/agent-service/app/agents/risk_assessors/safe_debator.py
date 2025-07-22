"""
保守辩论者智能体
在风险评估辩论中持保守观点
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.shared.logging_config import get_logger
from backend.shared.clients.llm_client import LLMClient

from ..base_agent import BaseAgent, AgentType, AgentCapability, TaskContext, TaskResult

logger = get_logger("agent-service.safe_debator")


class SafeDebator(BaseAgent):
    """保守辩论者智能体"""
    
    def __init__(self, agent_type: AgentType, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_type, agent_id, config)
        self.llm_client = LLMClient()
        
        logger.info(f"🏗️ 保守辩论者初始化完成: {self.agent_id}")
    
    def _define_capabilities(self) -> List[AgentCapability]:
        """定义智能体能力"""
        return [
            AgentCapability(
                name="safe_debate",
                description="保守辩论 - 在风险评估中提出保守观点",
                required_tools=["debate_analysis", "risk_modeling"],
                supported_markets=["US", "CN", "HK"],
                max_concurrent_tasks=2,
                estimated_duration=45
            )
        ]
    
    async def process_task(self, context: TaskContext) -> TaskResult:
        """处理保守辩论任务"""
        try:
            logger.info(f"🛡️ 开始保守辩论: {context.symbol}")
            
            # 模拟保守观点
            result = {
                "analysis_type": "safe_debate",
                "symbol": context.symbol,
                "position": "conservative",
                "stance": "稳健为主，控制风险",
                "arguments": [
                    "市场不确定性较高，应该谨慎行事",
                    "当前估值可能存在泡沫风险",
                    "保本比盈利更重要"
                ],
                "risk_tolerance": "low",
                "recommended_allocation": 0.05,
                "confidence": 0.7,
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
            logger.error(f"❌ 保守辩论失败: {context.symbol} - {e}")
            raise
