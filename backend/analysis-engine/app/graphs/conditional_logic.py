#!/usr/bin/env python3
"""
Backend条件逻辑
基于TradingAgents的条件逻辑，适配Backend的状态结构
"""

import logging
from typing import Dict, Any, List
from .graph_state import GraphState

logger = logging.getLogger(__name__)

class ConditionalLogic:
    """Backend条件逻辑处理器"""
    
    def __init__(self, max_debate_rounds: int = 3, max_risk_rounds: int = 2):
        self.max_debate_rounds = max_debate_rounds
        self.max_risk_rounds = max_risk_rounds
        
        # 辩论状态追踪
        self.debate_state = {
            "count": 0,
            "current_speaker": None,
            "bull_arguments": [],
            "bear_arguments": []
        }
        
        # 风险分析状态追踪
        self.risk_state = {
            "count": 0,
            "current_speaker": None,
            "risky_arguments": [],
            "safe_arguments": [],
            "neutral_arguments": []
        }
    
    def should_continue_market(self, state: GraphState) -> str:
        """判断市场分析是否继续"""
        logger.debug("🔍 检查市场分析是否需要继续")
        
        # 检查是否需要更多数据
        if not state.get("stock_data") or not state.get("market_data"):
            logger.debug("📊 需要获取市场数据")
            return "tools_market"
        
        # 检查分析是否完成
        if not state.get("technical_report"):
            logger.debug("📈 需要完成技术分析")
            return "tools_market"
        
        logger.debug("✅ 市场分析完成")
        return "clear_market"
    
    def should_continue_fundamentals(self, state: GraphState) -> str:
        """判断基本面分析是否继续"""
        logger.debug("🔍 检查基本面分析是否需要继续")
        
        # 检查是否需要财务数据
        if not state.get("financial_data"):
            logger.debug("📋 需要获取财务数据")
            return "tools_fundamentals"
        
        # 检查基本面报告是否完成
        if not state.get("fundamentals_report"):
            logger.debug("📊 需要完成基本面分析")
            return "tools_fundamentals"
        
        logger.debug("✅ 基本面分析完成")
        return "clear_fundamentals"
    
    def should_continue_news(self, state: GraphState) -> str:
        """判断新闻分析是否继续"""
        logger.debug("🔍 检查新闻分析是否需要继续")
        
        # 检查是否需要新闻数据
        if not state.get("news_data"):
            logger.debug("📰 需要获取新闻数据")
            return "tools_news"
        
        # 检查新闻报告是否完成
        if not state.get("news_report") or not state.get("sentiment_report"):
            logger.debug("📝 需要完成新闻分析")
            return "tools_news"
        
        logger.debug("✅ 新闻分析完成")
        return "clear_news"
    
    def should_continue_social(self, state: GraphState) -> str:
        """判断社交媒体分析是否继续"""
        logger.debug("🔍 检查社交媒体分析是否需要继续")
        
        # 简化实现：直接完成
        logger.debug("✅ 社交媒体分析完成")
        return "clear_social"
    
    def should_continue_debate(self, state: GraphState) -> str:
        """判断投资辩论是否继续"""
        logger.debug(f"🗣️ 检查投资辩论是否继续 (当前轮数: {self.debate_state['count']})")
        
        # 检查是否达到最大轮数
        if self.debate_state["count"] >= 2 * self.max_debate_rounds:
            logger.info(f"🏁 投资辩论达到最大轮数 ({self.max_debate_rounds})，结束辩论")
            self._reset_debate_state()
            return "research_manager"
        
        # 检查当前发言者，决定下一个发言者
        current_speaker = self.debate_state.get("current_speaker")
        
        if current_speaker is None or current_speaker == "bear":
            # 轮到多头发言
            self.debate_state["current_speaker"] = "bull"
            self.debate_state["count"] += 1
            logger.debug(f"🐂 轮到多头研究员发言 (第{self.debate_state['count']}轮)")
            return "bull_researcher"
        else:
            # 轮到空头发言
            self.debate_state["current_speaker"] = "bear"
            logger.debug(f"🐻 轮到空头研究员发言 (第{self.debate_state['count']}轮)")
            return "bear_researcher"
    
    def should_continue_risk_analysis(self, state: GraphState) -> str:
        """判断风险分析是否继续"""
        logger.debug(f"⚠️ 检查风险分析是否继续 (当前轮数: {self.risk_state['count']})")
        
        # 检查是否达到最大轮数
        if self.risk_state["count"] >= 3 * self.max_risk_rounds:
            logger.info(f"🏁 风险分析达到最大轮数 ({self.max_risk_rounds})，结束分析")
            self._reset_risk_state()
            return "risk_manager"
        
        # 检查当前发言者，决定下一个发言者
        current_speaker = self.risk_state.get("current_speaker")
        
        if current_speaker is None or current_speaker == "neutral":
            # 轮到激进分析师
            self.risk_state["current_speaker"] = "risky"
            self.risk_state["count"] += 1
            logger.debug(f"🔥 轮到激进分析师发言 (第{self.risk_state['count']}轮)")
            return "risky_analyst"
        elif current_speaker == "risky":
            # 轮到保守分析师
            self.risk_state["current_speaker"] = "safe"
            logger.debug(f"🛡️ 轮到保守分析师发言 (第{self.risk_state['count']}轮)")
            return "safe_analyst"
        else:  # current_speaker == "safe"
            # 轮到中性分析师
            self.risk_state["current_speaker"] = "neutral"
            logger.debug(f"⚖️ 轮到中性分析师发言 (第{self.risk_state['count']}轮)")
            return "neutral_analyst"
    
    def _reset_debate_state(self):
        """重置辩论状态"""
        self.debate_state = {
            "count": 0,
            "current_speaker": None,
            "bull_arguments": [],
            "bear_arguments": []
        }
        logger.debug("🔄 辩论状态已重置")
    
    def _reset_risk_state(self):
        """重置风险分析状态"""
        self.risk_state = {
            "count": 0,
            "current_speaker": None,
            "risky_arguments": [],
            "safe_arguments": [],
            "neutral_arguments": []
        }
        logger.debug("🔄 风险分析状态已重置")
    
    def get_debate_summary(self) -> Dict[str, Any]:
        """获取辩论摘要"""
        return {
            "debate_rounds": self.debate_state["count"],
            "max_debate_rounds": self.max_debate_rounds,
            "bull_arguments_count": len(self.debate_state["bull_arguments"]),
            "bear_arguments_count": len(self.debate_state["bear_arguments"]),
            "current_speaker": self.debate_state["current_speaker"]
        }
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """获取风险分析摘要"""
        return {
            "risk_rounds": self.risk_state["count"],
            "max_risk_rounds": self.max_risk_rounds,
            "risky_arguments_count": len(self.risk_state["risky_arguments"]),
            "safe_arguments_count": len(self.risk_state["safe_arguments"]),
            "neutral_arguments_count": len(self.risk_state["neutral_arguments"]),
            "current_speaker": self.risk_state["current_speaker"]
        }
    
    def add_debate_argument(self, speaker: str, argument: str):
        """添加辩论论点"""
        if speaker == "bull":
            self.debate_state["bull_arguments"].append({
                "round": self.debate_state["count"],
                "argument": argument,
                "timestamp": logger.info.__globals__.get('datetime', __import__('datetime')).datetime.now().isoformat()
            })
        elif speaker == "bear":
            self.debate_state["bear_arguments"].append({
                "round": self.debate_state["count"],
                "argument": argument,
                "timestamp": logger.info.__globals__.get('datetime', __import__('datetime')).datetime.now().isoformat()
            })
        
        logger.debug(f"📝 添加{speaker}论点: {argument[:50]}...")
    
    def add_risk_argument(self, speaker: str, argument: str):
        """添加风险分析论点"""
        argument_data = {
            "round": self.risk_state["count"],
            "argument": argument,
            "timestamp": logger.info.__globals__.get('datetime', __import__('datetime')).datetime.now().isoformat()
        }
        
        if speaker == "risky":
            self.risk_state["risky_arguments"].append(argument_data)
        elif speaker == "safe":
            self.risk_state["safe_arguments"].append(argument_data)
        elif speaker == "neutral":
            self.risk_state["neutral_arguments"].append(argument_data)
        
        logger.debug(f"📝 添加{speaker}风险论点: {argument[:50]}...")
    
    def check_early_consensus(self, state: GraphState) -> bool:
        """检查是否可以提前达成共识"""
        # 简化实现：基于论点的相似性判断
        # 实际实现可以使用更复杂的算法
        
        bull_args = self.debate_state["bull_arguments"]
        bear_args = self.debate_state["bear_arguments"]
        
        # 如果双方论点数量相近且都有足够的论点，可能达成共识
        if len(bull_args) >= 2 and len(bear_args) >= 2:
            # 这里可以添加更复杂的共识检查逻辑
            # 比如使用LLM判断论点的一致性
            return False
        
        return False
    
    def get_execution_path(self) -> List[str]:
        """获取执行路径"""
        path = []
        
        # 分析师阶段
        path.extend(["market_analyst", "fundamentals_analyst", "news_analyst"])
        
        # 辩论阶段
        for i in range(self.debate_state["count"]):
            if i % 2 == 0:
                path.append("bull_researcher")
            else:
                path.append("bear_researcher")
        
        path.append("research_manager")
        path.append("trader")
        
        # 风险分析阶段
        for i in range(self.risk_state["count"]):
            if i % 3 == 0:
                path.append("risky_analyst")
            elif i % 3 == 1:
                path.append("safe_analyst")
            else:
                path.append("neutral_analyst")
        
        path.append("risk_manager")
        
        return path
