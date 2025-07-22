"""
风险经理智能体
负责风险评估和风险控制建议
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.shared.logging_config import get_logger
from backend.shared.clients.llm_client import LLMClient

from ..base_agent import BaseAgent, AgentType, AgentCapability, TaskContext, TaskResult

logger = get_logger("agent-service.risk_manager")


class RiskManager(BaseAgent):
    """风险经理智能体"""
    
    def __init__(self, agent_type: AgentType, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_type, agent_id, config)
        self.llm_client = LLMClient()
        
        logger.info(f"🏗️ 风险经理初始化完成: {self.agent_id}")
    
    def _define_capabilities(self) -> List[AgentCapability]:
        """定义智能体能力"""
        return [
            AgentCapability(
                name="risk_assessment",
                description="风险评估 - 评估投资风险和制定风控策略",
                required_tools=["risk_analysis", "var_calculation"],
                supported_markets=["US", "CN", "HK"],
                max_concurrent_tasks=2,
                estimated_duration=100
            )
        ]
    
    async def process_task(self, context: TaskContext) -> TaskResult:
        """处理风险管理任务"""
        try:
            logger.info(f"🛡️ 开始风险评估: {context.symbol}")
            
            # 模拟风险评估结果
            result = {
                "analysis_type": "risk_assessment",
                "symbol": context.symbol,
                "overall_risk_level": "medium",
                "risk_score": 0.6,
                "var_1day": 0.02,
                "var_1week": 0.05,
                "max_drawdown": 0.15,
                "risk_factors": [
                    "市场波动风险",
                    "行业竞争风险",
                    "流动性风险"
                ],
                "risk_mitigation": [
                    "设置止损位",
                    "分散投资",
                    "定期评估"
                ],
                "position_sizing": "建议仓位不超过5%",
                "stop_loss": 0.10,
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
            logger.error(f"❌ 风险评估失败: {context.symbol} - {e}")
            raise
