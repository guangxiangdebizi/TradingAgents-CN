"""
激进辩论者智能体
在风险评估辩论中持激进观点
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.shared.logging_config import get_logger
from backend.shared.clients.llm_client import LLMClient

from ..base_agent import BaseAgent, AgentType, AgentCapability, TaskContext, TaskResult

logger = get_logger("agent-service.risky_debator")


class RiskyDebator(BaseAgent):
    """激进辩论者智能体"""
    
    def __init__(self, agent_type: AgentType, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_type, agent_id, config)
        self.llm_client = LLMClient()
        
        logger.info(f"🏗️ 激进辩论者初始化完成: {self.agent_id}")
    
    def _define_capabilities(self) -> List[AgentCapability]:
        """定义智能体能力"""
        return [
            AgentCapability(
                name="risk_assessment",
                description="风险评估 - 激进辩论，在风险评估中提出激进观点",
                required_tools=["debate_analysis", "risk_modeling"],
                supported_markets=["US", "CN", "HK"],
                max_concurrent_tasks=2,
                estimated_duration=45
            )
        ]
    
    async def process_task(self, context: TaskContext) -> TaskResult:
        """处理激进辩论任务"""
        try:
            logger.info(f"🔥 开始激进辩论: {context.symbol}")
            
            # 模拟激进观点
            result = {
                "analysis_type": "risky_debate",
                "symbol": context.symbol,
                "position": "aggressive",
                "stance": "高风险高回报",
                "arguments": [
                    "市场机会稍纵即逝，应该果断行动",
                    "当前估值仍有上升空间",
                    "风险可以通过技术手段控制"
                ],
                "risk_tolerance": "high",
                "recommended_allocation": 0.15,
                "confidence": 0.8,
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
            logger.error(f"❌ 激进辩论失败: {context.symbol} - {e}")
            raise
