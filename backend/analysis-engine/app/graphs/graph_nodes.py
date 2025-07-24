"""
图节点实现
定义分析图中的各个节点
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .graph_state import GraphState
from ..tools.toolkit_manager import ToolkitManager
from .agent_nodes import AgentNodes
from ..memory.memory_client import MemoryClient

logger = logging.getLogger(__name__)

class GraphNodes:
    """图节点类"""
    
    def __init__(self, toolkit_manager: ToolkitManager, agent_nodes: AgentNodes,
                 memory_client: Optional[MemoryClient] = None):
        self.toolkit_manager = toolkit_manager
        self.agent_nodes = agent_nodes
        self.memory_client = memory_client
        self.initialized = False
    
    async def initialize(self):
        """初始化图节点"""
        try:
            logger.info("🔗 初始化图节点...")
            
            self.initialized = True
            logger.info("✅ 图节点初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 图节点初始化失败: {e}")
            raise
    
    async def data_collection_node(self, state: GraphState) -> GraphState:
        """数据收集节点"""
        try:
            logger.info(f"📊 数据收集节点: {state['symbol']}")
            
            state["current_step"] = "data_collection"
            
            # 并行获取各种数据
            tasks = [
                self._get_stock_data(state["symbol"]),
                self._get_financial_data(state["symbol"]),
                self._get_market_data(state["symbol"]),
                self._get_news_data(state["symbol"])
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    state["errors"].append(f"数据获取失败: {str(result)}")
                    continue
                
                if i == 0:  # 股票数据
                    state["stock_data"] = result
                    # 更新公司名称
                    if result and result.get("success"):
                        company_name = result.get("company_name", state["symbol"])
                        state["company_name"] = company_name
                elif i == 1:  # 财务数据
                    state["financial_data"] = result
                elif i == 2:  # 市场数据
                    state["market_data"] = result
                elif i == 3:  # 新闻数据
                    state["news_data"] = result
            
            state["completed_steps"].append("data_collection")
            state["next_steps"] = ["analysis"]
            
            logger.info(f"✅ 数据收集完成: {state['symbol']}")
            
        except Exception as e:
            logger.error(f"❌ 数据收集失败: {e}")
            state["errors"].append(f"数据收集失败: {str(e)}")
        
        return state
    
    async def fundamentals_analyst_node(self, state: GraphState) -> GraphState:
        """基本面分析师节点"""
        try:
            logger.info(f"💰 基本面分析师节点: {state['symbol']}")
            
            state["current_step"] = "fundamentals_analysis"
            
            # 调用基本面分析师节点
            state = await self.agent_nodes.fundamentals_analyst_node(state)
            state["completed_steps"].append("fundamentals_analysis")
            
            logger.info(f"✅ 基本面分析完成: {state['symbol']}")
            
        except Exception as e:
            logger.error(f"❌ 基本面分析失败: {e}")
            state["errors"].append(f"基本面分析失败: {str(e)}")
        
        return state
    
    async def technical_analyst_node(self, state: GraphState) -> GraphState:
        """技术分析师节点"""
        try:
            logger.info(f"📈 技术分析师节点: {state['symbol']}")
            
            state["current_step"] = "technical_analysis"
            
            # 调用市场分析师节点（技术分析）
            state = await self.agent_nodes.market_analyst_node(state)
            state["completed_steps"].append("technical_analysis")
            
            logger.info(f"✅ 技术分析完成: {state['symbol']}")
            
        except Exception as e:
            logger.error(f"❌ 技术分析失败: {e}")
            state["errors"].append(f"技术分析失败: {str(e)}")
        
        return state
    
    async def news_analyst_node(self, state: GraphState) -> GraphState:
        """新闻分析师节点"""
        try:
            logger.info(f"📰 新闻分析师节点: {state['symbol']}")
            
            state["current_step"] = "news_analysis"
            
            # 调用新闻分析师节点
            state = await self.agent_nodes.news_analyst_node(state)
            state["completed_steps"].append("news_analysis")
            
            logger.info(f"✅ 新闻分析完成: {state['symbol']}")
            
        except Exception as e:
            logger.error(f"❌ 新闻分析失败: {e}")
            state["errors"].append(f"新闻分析失败: {str(e)}")
        
        return state
    
    async def bull_researcher_node(self, state: GraphState) -> GraphState:
        """看涨研究员节点"""
        try:
            logger.info(f"🚀 看涨研究员节点: {state['symbol']}")
            
            state["current_step"] = "bull_analysis"
            
            # 调用多头研究员节点
            state = await self.agent_nodes.bull_researcher_node(state)
            state["completed_steps"].append("bull_analysis")
            
            logger.info(f"✅ 看涨分析完成: {state['symbol']}")
            
        except Exception as e:
            logger.error(f"❌ 看涨分析失败: {e}")
            state["errors"].append(f"看涨分析失败: {str(e)}")
        
        return state
    
    async def bear_researcher_node(self, state: GraphState) -> GraphState:
        """看跌研究员节点"""
        try:
            logger.info(f"📉 看跌研究员节点: {state['symbol']}")
            
            state["current_step"] = "bear_analysis"
            
            # 调用空头研究员节点
            state = await self.agent_nodes.bear_researcher_node(state)
            state["completed_steps"].append("bear_analysis")
            
            logger.info(f"✅ 看跌分析完成: {state['symbol']}")
            
        except Exception as e:
            logger.error(f"❌ 看跌分析失败: {e}")
            state["errors"].append(f"看跌分析失败: {str(e)}")
        
        return state
    
    async def risk_manager_node(self, state: GraphState) -> GraphState:
        """风险管理师节点"""
        try:
            logger.info(f"🛡️ 风险管理师节点: {state['symbol']}")
            
            state["current_step"] = "risk_assessment"
            
            # 调用风险管理师节点
            state = await self.agent_nodes.risk_manager_node(state)
            state["completed_steps"].append("risk_assessment")
            
            logger.info(f"✅ 风险评估完成: {state['symbol']}")
            
        except Exception as e:
            logger.error(f"❌ 风险评估失败: {e}")
            state["errors"].append(f"风险评估失败: {str(e)}")
        
        return state
    
    async def research_manager_node(self, state: GraphState) -> GraphState:
        """研究主管节点"""
        try:
            logger.info(f"👔 研究主管节点: {state['symbol']}")
            
            state["current_step"] = "final_decision"
            
            # 调用研究经理节点
            state = await self.agent_nodes.research_manager_node(state)
            state["completed_steps"].append("final_decision")
            
            logger.info(f"✅ 最终决策完成: {state['symbol']}")
            
        except Exception as e:
            logger.error(f"❌ 最终决策失败: {e}")
            state["errors"].append(f"最终决策失败: {str(e)}")
        
        return state
    
    async def report_generator_node(self, state: GraphState) -> GraphState:
        """报告生成器节点"""
        try:
            logger.info(f"📄 报告生成器节点: {state['symbol']}")
            
            state["current_step"] = "report_generation"
            
            # 这里可以实现报告格式化和生成逻辑
            # 目前只是标记完成
            state["completed_steps"].append("report_generation")
            
            logger.info(f"✅ 报告生成完成: {state['symbol']}")
            
        except Exception as e:
            logger.error(f"❌ 报告生成失败: {e}")
            state["errors"].append(f"报告生成失败: {str(e)}")
        
        return state
    
    # 辅助方法
    async def _get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """获取股票数据"""
        return await self.toolkit_manager.call_tool(
            "get_stock_data",
            {"symbol": symbol, "period": "1y"}
        )
    
    async def _get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """获取财务数据"""
        return await self.toolkit_manager.call_tool(
            "get_financial_data",
            {"symbol": symbol, "statement_type": "income"}
        )
    
    async def _get_market_data(self, symbol: str) -> Dict[str, Any]:
        """获取市场数据"""
        return await self.toolkit_manager.call_tool(
            "get_market_data",
            {"symbol": symbol, "indicators": ["price", "volume", "market_cap"]}
        )
    
    async def _get_news_data(self, symbol: str) -> Dict[str, Any]:
        """获取新闻数据"""
        return await self.toolkit_manager.call_tool(
            "get_stock_news",
            {"symbol": symbol, "days": 30}
        )
    
    async def reload(self):
        """重新加载图节点"""
        logger.info("🔄 重新加载图节点...")
        # 图节点通常不需要特殊的重新加载逻辑
        logger.info("✅ 图节点重新加载完成")
    
    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理图节点资源...")
        self.initialized = False
        logger.info("✅ 图节点资源清理完成")
