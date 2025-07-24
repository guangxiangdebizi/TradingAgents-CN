#!/usr/bin/env python3
"""
Backend交易图引擎
基于TradingAgents的图结构，使用微服务架构实现
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END, START
from langchain_core.messages import HumanMessage

from .graph_state import GraphState
from .conditional_logic import ConditionalLogic
from .agent_nodes import AgentNodes
# 移除 LLMToolkitManager，我们使用 Agent Service

logger = logging.getLogger(__name__)

class TradingGraph:
    """Backend交易图引擎"""
    
    def __init__(self):
        self.graph: Optional[StateGraph] = None
        self.compiled_graph = None
        # 移除 toolkit_manager，我们使用 Agent Service
        self.agent_nodes: Optional[AgentNodes] = None
        self.conditional_logic: Optional[ConditionalLogic] = None
        # 移除 ToolNode，我们使用 Agent Service
        
        # 配置参数
        self.config = {
            "max_debate_rounds": 3,
            "max_risk_rounds": 2,
            "selected_analysts": ["market", "fundamentals", "news", "social"]
        }
    
    async def initialize(self):
        """初始化图引擎"""
        try:
            logger.info("🔧 初始化Backend交易图引擎...")
            
            # 移除工具管理器初始化，我们使用 Agent Service
            
            # 初始化条件逻辑
            self.conditional_logic = ConditionalLogic(
                max_debate_rounds=self.config["max_debate_rounds"],
                max_risk_rounds=self.config["max_risk_rounds"]
            )
            
            # 初始化Agent节点
            self.agent_nodes = AgentNodes()
            await self.agent_nodes.initialize()
            
            # 构建图
            self.graph = self._build_graph()
            self.compiled_graph = self.graph.compile()
            
            logger.info("✅ Backend交易图引擎初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 图引擎初始化失败: {e}")
            raise
    
    # 移除 _create_tool_nodes 方法，我们使用 Agent Service
    
    def _build_graph(self) -> StateGraph:
        """构建交易决策图"""
        logger.info("🏗️ 构建交易决策图...")
        
        # 创建状态图
        workflow = StateGraph(GraphState)
        
        # 添加分析师节点
        self._add_analyst_nodes(workflow)
        
        # 添加研究员节点
        self._add_researcher_nodes(workflow)
        
        # 添加风险分析节点
        self._add_risk_nodes(workflow)
        
        # 移除工具节点，我们使用 Agent Service
        
        # 添加边和条件逻辑
        self._add_edges(workflow)
        
        logger.info("✅ 交易决策图构建完成")
        return workflow
    
    def _add_analyst_nodes(self, workflow: StateGraph):
        """添加分析师节点"""
        selected_analysts = self.config["selected_analysts"]
        
        for analyst_type in selected_analysts:
            # 添加分析师节点
            workflow.add_node(
                f"{analyst_type}_analyst",
                self.agent_nodes.get_analyst_node(analyst_type)
            )
            # 移除消息清理节点，我们使用 Agent Service
    
    def _add_researcher_nodes(self, workflow: StateGraph):
        """添加研究员节点"""
        workflow.add_node("bull_researcher", self.agent_nodes.bull_researcher_node)
        workflow.add_node("bear_researcher", self.agent_nodes.bear_researcher_node)
        workflow.add_node("research_manager", self.agent_nodes.research_manager_node)
    
    def _add_risk_nodes(self, workflow: StateGraph):
        """添加风险分析节点"""
        workflow.add_node("risky_analyst", self.agent_nodes.risky_analyst_node)
        workflow.add_node("safe_analyst", self.agent_nodes.safe_analyst_node)
        workflow.add_node("neutral_analyst", self.agent_nodes.neutral_analyst_node)
        workflow.add_node("risk_manager", self.agent_nodes.risk_manager_node)
        workflow.add_node("trader", self.agent_nodes.trader_node)
    
    # 移除 _add_tool_nodes 方法，我们使用 Agent Service
    
    def _add_edges(self, workflow: StateGraph):
        """添加边和条件逻辑"""
        selected_analysts = self.config["selected_analysts"]
        
        # 设置起始点
        if selected_analysts:
            first_analyst = f"{selected_analysts[0]}_analyst"
            workflow.add_edge(START, first_analyst)
        
        # 添加分析师之间的直接连接（移除工具节点）
        for i, analyst_type in enumerate(selected_analysts):
            analyst_node = f"{analyst_type}_analyst"

            # 直接连接到下一个分析师或研究员
            if i < len(selected_analysts) - 1:
                next_analyst = f"{selected_analysts[i+1]}_analyst"
                workflow.add_edge(analyst_node, next_analyst)
            else:
                # 最后一个分析师连接到多头研究员
                workflow.add_edge(analyst_node, "bull_researcher")
        
        # 添加辩论的条件边
        workflow.add_conditional_edges(
            "bull_researcher",
            self.conditional_logic.should_continue_debate,
            {
                "bull_researcher": "bull_researcher",
                "bear_researcher": "bear_researcher",
                "research_manager": "research_manager"
            }
        )
        
        workflow.add_conditional_edges(
            "bear_researcher",
            self.conditional_logic.should_continue_debate,
            {
                "bull_researcher": "bull_researcher",
                "bear_researcher": "bear_researcher",
                "research_manager": "research_manager"
            }
        )
        
        # 研究经理 -> 交易员
        workflow.add_edge("research_manager", "trader")
        
        # 交易员 -> 风险分析
        workflow.add_edge("trader", "risky_analyst")
        
        # 添加风险分析的条件边
        workflow.add_conditional_edges(
            "risky_analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "risky_analyst": "risky_analyst",
                "safe_analyst": "safe_analyst",
                "neutral_analyst": "neutral_analyst",
                "risk_manager": "risk_manager"
            }
        )
        
        workflow.add_conditional_edges(
            "safe_analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "risky_analyst": "risky_analyst",
                "safe_analyst": "safe_analyst",
                "neutral_analyst": "neutral_analyst",
                "risk_manager": "risk_manager"
            }
        )
        
        workflow.add_conditional_edges(
            "neutral_analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "risky_analyst": "risky_analyst",
                "safe_analyst": "safe_analyst",
                "neutral_analyst": "neutral_analyst",
                "risk_manager": "risk_manager"
            }
        )
        
        # 风险经理 -> 结束
        workflow.add_edge("risk_manager", END)
    
    async def analyze_stock(self, symbol: str, analysis_date: str = None) -> Dict[str, Any]:
        """分析股票 - 主要入口点"""
        logger.info(f"🔍 TradingGraph.analyze_stock 被调用")
        logger.info(f"🔍 参数: symbol={symbol}, analysis_date={analysis_date}")

        if not self.compiled_graph:
            logger.error("❌ 图引擎未初始化")
            raise RuntimeError("图引擎未初始化")

        if analysis_date is None:
            analysis_date = datetime.now().strftime("%Y-%m-%d")
            logger.info(f"🔍 使用默认分析日期: {analysis_date}")

        logger.info(f"📊 开始图分析: {symbol}")

        # 创建初始状态
        logger.info(f"🔍 创建初始状态...")
        initial_state = self._create_initial_state(symbol, analysis_date)
        logger.info(f"🔍 初始状态创建完成: {initial_state}")

        try:
            # 执行图，设置递归限制
            logger.info(f"🔍 开始执行图分析...")
            logger.info(f"🔍 调用 compiled_graph.ainvoke(initial_state)")

            # 按照原始 TradingAgents 的方式设置递归限制
            config = {"recursion_limit": 100}
            final_state = await self.compiled_graph.ainvoke(initial_state, config=config)
            logger.info(f"🔍 图执行完成，最终状态: {final_state}")

            # 处理结果
            logger.info(f"🔍 处理最终状态...")
            result = self._process_final_state(final_state)
            logger.info(f"🔍 结果处理完成: {result}")

            logger.info(f"✅ 图分析完成: {symbol}")
            return result

        except Exception as e:
            logger.error(f"❌ 图分析失败: {symbol} - {e}")
            logger.error(f"❌ 错误类型: {type(e).__name__}")
            logger.error(f"❌ 错误详情: {str(e)}")
            import traceback
            logger.error(f"❌ 错误堆栈: {traceback.format_exc()}")
            raise
    
    def _create_initial_state(self, symbol: str, analysis_date: str) -> GraphState:
        """创建初始状态"""
        logger.info(f"🔍 _create_initial_state 被调用")
        logger.info(f"🔍 参数: symbol={symbol}, analysis_date={analysis_date}")

        state = GraphState(
            # LangGraph必需字段
            messages=[HumanMessage(content=f"开始分析股票 {symbol}")],

            symbol=symbol,
            company_name=symbol,  # 可以后续通过工具获取公司名称
            analysis_type="comprehensive",
            current_date=analysis_date,
            
            # 数据初始化为None
            stock_data=None,
            financial_data=None,
            market_data=None,
            news_data=None,
            social_data=None,

            # 报告初始化为None
            fundamentals_report=None,
            technical_report=None,
            news_report=None,
            sentiment_report=None,
            social_report=None,

            # 研究员观点初始化为None
            bull_analysis=None,
            bear_analysis=None,

            # 风险管理初始化为None
            risk_assessment=None,
            risky_analysis=None,
            safe_analysis=None,
            neutral_analysis=None,

            # 最终决策初始化为None
            final_recommendation=None,
            investment_plan=None,
            trade_decision=None,
            
            # 辅助信息
            errors=[],
            warnings=[],
            metadata={
                "start_time": datetime.now().isoformat(),
                "graph_version": "1.0.0"
            },
            
            # 执行状态
            current_step="start",
            completed_steps=[],
            next_steps=["market_analyst"],

            # 辩论状态
            debate_history=[],
            debate_summary=None,

            # 风险分析状态
            risk_history=[],
            risk_summary=None
        )

        logger.info(f"🔍 初始状态创建完成: symbol={state['symbol']}, current_date={state['current_date']}")
        return state
    
    def _process_final_state(self, final_state: GraphState) -> Dict[str, Any]:
        """处理最终状态"""
        logger.info(f"🔍 _process_final_state 被调用")
        logger.info(f"🔍 最终状态: symbol={final_state.get('symbol')}, current_step={final_state.get('current_step')}")
        logger.info(f"🔍 完成的步骤: {final_state.get('completed_steps', [])}")
        logger.info(f"🔍 错误列表: {final_state.get('errors', [])}")

        result = {
            "symbol": final_state["symbol"],
            "analysis_date": final_state["current_date"],
            "final_recommendation": final_state["final_recommendation"],
            "investment_plan": final_state["investment_plan"],
            "risk_assessment": final_state["risk_assessment"],
            "reports": {
                "fundamentals": final_state["fundamentals_report"],
                "technical": final_state["technical_report"],
                "news": final_state["news_report"],
                "sentiment": final_state["sentiment_report"]
            },
            "research": {
                "bull_analysis": final_state["bull_analysis"],
                "bear_analysis": final_state["bear_analysis"]
            },
            "metadata": final_state["metadata"],
            "completed_steps": final_state["completed_steps"]
        }

        logger.info(f"🔍 结果处理完成: {result}")
        return result
    
    async def get_graph_visualization(self) -> str:
        """获取图的可视化"""
        if not self.compiled_graph:
            return "图未初始化"
        
        try:
            return self.compiled_graph.get_graph().draw_mermaid()
        except Exception as e:
            logger.error(f"生成图可视化失败: {e}")
            return f"可视化生成失败: {e}"
    
    async def cleanup(self):
        """清理资源"""
        # 移除 toolkit_manager 清理，我们使用 Agent Service
        
        if self.agent_nodes:
            await self.agent_nodes.cleanup()
        
        logger.info("✅ 图引擎资源清理完成")
