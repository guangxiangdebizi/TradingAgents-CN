"""
分析图实现
基于LangGraph的多智能体协作工作流
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .graph_state import GraphState, AnalysisParameters
from .graph_nodes import GraphNodes
from ..tools.toolkit_manager import ToolkitManager
from ..agents.agent_factory import AgentFactory
from ..memory.memory_client import MemoryClient

logger = logging.getLogger(__name__)

class AnalysisGraph:
    """分析图类"""
    
    def __init__(self, toolkit_manager: ToolkitManager, agent_factory: AgentFactory,
                 memory_client: Optional[MemoryClient] = None):
        self.toolkit_manager = toolkit_manager
        self.agent_factory = agent_factory
        self.memory_client = memory_client
        self.graph_nodes: Optional[GraphNodes] = None
        self.initialized = False
    
    async def initialize(self):
        """初始化分析图"""
        try:
            logger.info("🔗 初始化分析图...")
            
            # 初始化图节点
            self.graph_nodes = GraphNodes(
                toolkit_manager=self.toolkit_manager,
                agent_factory=self.agent_factory,
                memory_client=self.memory_client
            )
            await self.graph_nodes.initialize()
            
            self.initialized = True
            logger.info("✅ 分析图初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 分析图初始化失败: {e}")
            raise
    
    async def execute_analysis(self, symbol: str, analysis_type: str = "comprehensive", 
                             parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行分析"""
        if not self.initialized:
            raise RuntimeError("分析图未初始化")
        
        try:
            logger.info(f"🚀 开始执行分析: {symbol} - {analysis_type}")
            
            # 初始化状态
            state = await self._initialize_state(symbol, analysis_type, parameters)
            
            # 根据分析类型选择执行路径
            if analysis_type == "fundamentals":
                result = await self._execute_fundamentals_analysis(state)
            elif analysis_type == "technical":
                result = await self._execute_technical_analysis(state)
            elif analysis_type == "comprehensive":
                result = await self._execute_comprehensive_analysis(state)
            elif analysis_type == "debate":
                result = await self._execute_debate_analysis(state)
            else:
                raise ValueError(f"不支持的分析类型: {analysis_type}")
            
            logger.info(f"✅ 分析执行完成: {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 分析执行失败: {symbol} - {e}")
            return {
                "success": False,
                "symbol": symbol,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _initialize_state(self, symbol: str, analysis_type: str, 
                               parameters: Optional[Dict[str, Any]]) -> GraphState:
        """初始化分析状态"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # 默认参数
        default_params = {
            "enable_fundamentals": True,
            "enable_technical": True,
            "enable_news": True,
            "enable_sentiment": True,
            "enable_debate": analysis_type == "comprehensive" or analysis_type == "debate",
            "enable_risk_assessment": True,
            "model_name": "deepseek-chat",
            "temperature": 0.1,
            "max_tokens": 1500,
            "analysis_period": "1y",
            "lookback_days": 30,
            "debug_mode": False,
            "save_intermediate": True
        }
        
        if parameters:
            default_params.update(parameters)
        
        state: GraphState = {
            "symbol": symbol,
            "company_name": symbol,  # 将在数据获取阶段更新
            "analysis_type": analysis_type,
            "current_date": current_date,
            "stock_data": None,
            "financial_data": None,
            "market_data": None,
            "news_data": None,
            "fundamentals_report": None,
            "technical_report": None,
            "news_report": None,
            "sentiment_report": None,
            "bull_analysis": None,
            "bear_analysis": None,
            "risk_assessment": None,
            "final_recommendation": None,
            "investment_plan": None,
            "messages": [],
            "errors": [],
            "metadata": default_params,
            "current_step": "initialization",
            "completed_steps": [],
            "next_steps": ["data_collection"]
        }
        
        return state
    
    async def _execute_fundamentals_analysis(self, state: GraphState) -> Dict[str, Any]:
        """执行基本面分析"""
        logger.info("📊 执行基本面分析流程")
        
        # 1. 数据收集
        state = await self.graph_nodes.data_collection_node(state)
        
        # 2. 基本面分析
        state = await self.graph_nodes.fundamentals_analyst_node(state)
        
        # 3. 风险评估（如果启用）
        if state["metadata"].get("enable_risk_assessment"):
            state = await self.graph_nodes.risk_manager_node(state)
        
        # 4. 生成最终报告
        state = await self.graph_nodes.report_generator_node(state)
        
        return self._format_analysis_result(state)
    
    async def _execute_technical_analysis(self, state: GraphState) -> Dict[str, Any]:
        """执行技术分析"""
        logger.info("📈 执行技术分析流程")
        
        # 1. 数据收集
        state = await self.graph_nodes.data_collection_node(state)
        
        # 2. 技术分析
        state = await self.graph_nodes.technical_analyst_node(state)
        
        # 3. 风险评估（如果启用）
        if state["metadata"].get("enable_risk_assessment"):
            state = await self.graph_nodes.risk_manager_node(state)
        
        # 4. 生成最终报告
        state = await self.graph_nodes.report_generator_node(state)
        
        return self._format_analysis_result(state)
    
    async def _execute_comprehensive_analysis(self, state: GraphState) -> Dict[str, Any]:
        """执行综合分析"""
        logger.info("🔍 执行综合分析流程")
        
        # 1. 数据收集
        state = await self.graph_nodes.data_collection_node(state)
        
        # 2. 并行执行各种分析
        analysis_tasks = []
        
        if state["metadata"].get("enable_fundamentals"):
            analysis_tasks.append(self.graph_nodes.fundamentals_analyst_node(state.copy()))
        
        if state["metadata"].get("enable_technical"):
            analysis_tasks.append(self.graph_nodes.technical_analyst_node(state.copy()))
        
        if state["metadata"].get("enable_news"):
            analysis_tasks.append(self.graph_nodes.news_analyst_node(state.copy()))
        
        # 等待所有分析完成
        if analysis_tasks:
            analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # 合并分析结果
            for result in analysis_results:
                if isinstance(result, Exception):
                    state["errors"].append(str(result))
                    continue
                
                # 合并分析报告
                if result.get("fundamentals_report"):
                    state["fundamentals_report"] = result["fundamentals_report"]
                if result.get("technical_report"):
                    state["technical_report"] = result["technical_report"]
                if result.get("news_report"):
                    state["news_report"] = result["news_report"]
        
        # 3. 辩论阶段（如果启用）
        if state["metadata"].get("enable_debate"):
            # 看涨研究员
            state = await self.graph_nodes.bull_researcher_node(state)
            
            # 看跌研究员
            state = await self.graph_nodes.bear_researcher_node(state)
        
        # 4. 风险管理
        if state["metadata"].get("enable_risk_assessment"):
            state = await self.graph_nodes.risk_manager_node(state)
        
        # 5. 研究主管决策
        state = await self.graph_nodes.research_manager_node(state)
        
        # 6. 生成最终报告
        state = await self.graph_nodes.report_generator_node(state)
        
        return self._format_analysis_result(state)
    
    async def _execute_debate_analysis(self, state: GraphState) -> Dict[str, Any]:
        """执行辩论分析"""
        logger.info("🗣️ 执行辩论分析流程")
        
        # 1. 数据收集
        state = await self.graph_nodes.data_collection_node(state)
        
        # 2. 基础分析
        state = await self.graph_nodes.fundamentals_analyst_node(state)
        state = await self.graph_nodes.technical_analyst_node(state)
        
        # 3. 多轮辩论
        max_rounds = 3
        for round_num in range(max_rounds):
            logger.info(f"🔄 辩论第{round_num + 1}轮")
            
            # 看涨观点
            state = await self.graph_nodes.bull_researcher_node(state)
            
            # 看跌观点
            state = await self.graph_nodes.bear_researcher_node(state)
            
            # 检查是否达成共识
            if await self._check_consensus(state):
                logger.info("✅ 辩论达成共识")
                break
        
        # 4. 研究主管最终决策
        state = await self.graph_nodes.research_manager_node(state)
        
        # 5. 生成最终报告
        state = await self.graph_nodes.report_generator_node(state)
        
        return self._format_analysis_result(state)
    
    async def _check_consensus(self, state: GraphState) -> bool:
        """检查是否达成共识"""
        # 简化的共识检查逻辑
        bull_analysis = state.get("bull_analysis", "")
        bear_analysis = state.get("bear_analysis", "")
        
        if not bull_analysis or not bear_analysis:
            return False
        
        # 检查观点是否趋于一致
        # 这里可以实现更复杂的共识检查逻辑
        return len(state.get("completed_steps", [])) >= 5
    
    def _format_analysis_result(self, state: GraphState) -> Dict[str, Any]:
        """格式化分析结果"""
        return {
            "success": True,
            "symbol": state["symbol"],
            "company_name": state["company_name"],
            "analysis_type": state["analysis_type"],
            "reports": {
                "fundamentals": state.get("fundamentals_report"),
                "technical": state.get("technical_report"),
                "news": state.get("news_report"),
                "sentiment": state.get("sentiment_report"),
                "bull_analysis": state.get("bull_analysis"),
                "bear_analysis": state.get("bear_analysis"),
                "risk_assessment": state.get("risk_assessment"),
                "final_recommendation": state.get("final_recommendation"),
                "investment_plan": state.get("investment_plan")
            },
            "data": {
                "stock_data": state.get("stock_data"),
                "financial_data": state.get("financial_data"),
                "market_data": state.get("market_data"),
                "news_data": state.get("news_data")
            },
            "metadata": {
                "completed_steps": state.get("completed_steps", []),
                "errors": state.get("errors", []),
                "analysis_date": state["current_date"],
                "parameters": state.get("metadata", {})
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """获取分析图状态"""
        return {
            "initialized": self.initialized,
            "toolkit_manager": self.toolkit_manager is not None,
            "agent_factory": self.agent_factory is not None,
            "graph_nodes": self.graph_nodes is not None,
            "timestamp": datetime.now().isoformat()
        }
    
    async def reload(self):
        """重新加载分析图"""
        logger.info("🔄 重新加载分析图...")
        
        if self.graph_nodes:
            await self.graph_nodes.reload()
        
        logger.info("✅ 分析图重新加载完成")
    
    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理分析图资源...")
        
        if self.graph_nodes:
            await self.graph_nodes.cleanup()
        
        self.initialized = False
        
        logger.info("✅ 分析图资源清理完成")
