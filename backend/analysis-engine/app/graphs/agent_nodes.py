#!/usr/bin/env python3
"""
Backend Agent节点实现
基于TradingAgents的Agent节点，适配Backend的微服务架构
"""

import logging
import aiohttp
from typing import Dict, Any, Optional
from .graph_state import GraphState, update_state_step, add_message

# 导入Agent Service的枚举类型
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from backend.agent_service.app.models.agent_models import AgentTypeEnum, TaskTypeEnum
except ImportError:
    # 如果无法导入，使用字符串常量
    print("⚠️ 无法导入Agent Service枚举，使用字符串常量")
    class AgentTypeEnum:
        BULL_RESEARCHER = "bull_researcher"
        BEAR_RESEARCHER = "bear_researcher"
        NEWS_ANALYST = "news_analyst"
        MARKET_ANALYST = "market_analyst"
        FUNDAMENTALS_ANALYST = "fundamentals_analyst"
        SOCIAL_MEDIA_ANALYST = "social_media_analyst"
        RESEARCH_MANAGER = "research_manager"
        RISK_MANAGER = "risk_manager"
        TRADER = "trader"
        RISKY_DEBATOR = "risky_debator"
        SAFE_DEBATOR = "safe_debator"
        NEUTRAL_DEBATOR = "neutral_debator"

    class TaskTypeEnum:
        BULL_RESEARCH = "bull_research"
        BEAR_RESEARCH = "bear_research"
        NEWS_ANALYSIS = "news_analysis"
        FUNDAMENTALS_ANALYSIS = "fundamentals_analysis"
        TECHNICAL_ANALYSIS = "technical_analysis"
        SENTIMENT_ANALYSIS = "sentiment_analysis"
        RESEARCH_MANAGEMENT = "research_management"
        RISK_ASSESSMENT = "risk_assessment"
        TRADING_DECISION = "trading_decision"
        DEBATE_PARTICIPATION = "debate_participation"

logger = logging.getLogger(__name__)

class AgentNodes:
    """Backend Agent节点管理器"""
    
    def __init__(self):
        self.agent_service_url = "http://localhost:8008"  # 修复：使用正确的本地端口
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """初始化Agent节点"""
        self.session = aiohttp.ClientSession()
        logger.info("✅ Agent节点管理器初始化完成")
    
    async def cleanup(self):
        """清理资源"""
        if self.session:
            await self.session.close()
        logger.info("✅ Agent节点资源清理完成")
    
    async def _call_agent_service(self, agent_type, task_type, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用Agent服务"""
        try:
            # 使用Agent Service的通用执行端点
            url = f"{self.agent_service_url}/api/v1/agents/execute"

            # 构造Agent Service期望的AgentRequest格式
            request_data = {
                "agent_type": agent_type.value if hasattr(agent_type, 'value') else str(agent_type),
                "task_type": task_type.value if hasattr(task_type, 'value') else str(task_type),
                "symbol": data.get("symbol", "000001"),
                "company_name": data.get("company_name", data.get("symbol", "000001")),
                "market": data.get("market", "CN"),  # 中国A股
                "analysis_date": data.get("analysis_date", "2025-07-23"),
                "parameters": data.get("parameters", {}),
                "metadata": data.get("metadata", {}),
                "priority": "normal",
                "timeout": 300
            }

            # 添加调试日志
            logger.info(f"🔍 发送Agent Service请求: agent_type={agent_type}, task_type={task_type}")
            logger.info(f"🔍 请求数据: {request_data}")

            async with self.session.post(url, json=request_data) as response:
                logger.info(f"🔍 Agent Service响应状态: {response.status}")

                if response.status == 200:
                    agent_response = await response.json()
                    logger.info(f"🔍 Agent Service响应内容: {agent_response}")

                    # 检查响应状态
                    status = agent_response.get("status")
                    result_content = agent_response.get("result")
                    error_content = agent_response.get("error")

                    logger.info(f"🔍 响应状态: {status}")
                    logger.info(f"🔍 结果内容长度: {len(result_content) if result_content else 0}")
                    logger.info(f"🔍 错误内容: {error_content}")

                    # 转换Agent Service响应格式为内部期望格式
                    # 检查多种可能的成功状态
                    if status in ["completed", "success"] and result_content:
                        result = {
                            "success": True,
                            "analysis": result_content,
                            "task_id": agent_response.get("task_id"),
                            "agent_type": agent_response.get("agent_type"),
                            "duration": agent_response.get("duration", 0)
                        }
                        logger.info(f"✅ Agent Service调用成功: {agent_type}/{task_type}")
                        logger.info(f"🔍 转换后的结果: success=True, analysis_length={len(result_content)}")
                        return result
                    elif status in ["completed", "success"] and not result_content:
                        error_msg = "Agent任务完成但结果为空"
                        logger.error(f"❌ Agent任务状态异常: {status} - {error_msg}")
                        return {
                            "success": False,
                            "error": error_msg
                        }
                    else:
                        error_msg = agent_response.get("error", "Agent任务未完成")
                        logger.error(f"❌ Agent任务状态异常: {status} - {error_msg}")
                        return {
                            "success": False,
                            "error": error_msg
                        }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Agent服务调用失败: {agent_type}/{task_type} - HTTP {response.status}")
                    logger.error(f"❌ 错误响应内容: {error_text}")
                    return {"success": False, "error": error_text}

        except Exception as e:
            logger.error(f"❌ Agent服务调用异常: {agent_type}/{task_type} - {e}")
            # 添加严重告警日志
            logger.error(f"🚨 严重告警: Agent Service不可达 - {agent_type}/{task_type}")
            logger.error(f"🚨 请检查Agent Service是否启动并可访问")
            logger.error(f"🚨 错误详情: {type(e).__name__}: {e}")
            return {"success": False, "error": str(e)}
    
    # 分析师节点
    async def market_analyst_node(self, state: GraphState) -> GraphState:
        """市场分析师节点"""
        logger.info("📈 执行市场分析师节点")
        logger.info(f"🔍 market_analyst_node 被调用")
        logger.info(f"🔍 输入状态: symbol={state.get('symbol')}, current_date={state.get('current_date')}")

        try:
            # 调用Agent服务
            logger.info(f"🔍 准备调用 _call_agent_service...")
            result = await self._call_agent_service(
                AgentTypeEnum.MARKET_ANALYST,
                TaskTypeEnum.TECHNICAL_ANALYSIS,
                {
                    "symbol": state["symbol"],
                    "company_name": state["company_name"],
                    "analysis_date": state["current_date"],
                    "market": "CN",
                    "parameters": {
                        "analysis_type": "technical"
                    },
                    "metadata": {
                        "existing_data": state.get("stock_data")
                    }
                }
            )
            logger.info(f"🔍 _call_agent_service 返回结果: {result}")
            
            logger.info(f"🔍 市场分析师节点收到结果: {result}")

            if result.get("success"):
                analysis_content = result.get("analysis", "")
                logger.info(f"✅ 市场分析成功，内容长度: {len(analysis_content)}")

                # 更新状态
                state["technical_report"] = analysis_content
                state["market_data"] = result.get("market_data", {})

                # 添加消息
                add_message(state, "market_analyst", analysis_content)
                logger.info(f"✅ 市场分析结果已添加到状态中")
            else:
                error_msg = result.get("error", "未知错误")
                logger.error(f"❌ 市场分析失败: {error_msg}")
                state["errors"].append(f"市场分析失败: {error_msg}")

            logger.info("✅ 市场分析完成")
            
            # 更新步骤
            update_state_step(state, "market_analyst")
            
        except Exception as e:
            error_msg = f"市场分析师节点异常: {e}"
            state["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        return state
    
    async def fundamentals_analyst_node(self, state: GraphState) -> GraphState:
        """基本面分析师节点"""
        logger.info("📋 执行基本面分析师节点")
        
        try:
            result = await self._call_agent_service(
                AgentTypeEnum.FUNDAMENTALS_ANALYST,
                TaskTypeEnum.FUNDAMENTALS_ANALYSIS,
                {
                    "symbol": state["symbol"],
                    "company_name": state["company_name"],
                    "analysis_date": state["current_date"],
                    "market": "CN",
                    "parameters": {
                        "analysis_type": "fundamental"
                    },
                    "metadata": {
                        "existing_data": state.get("financial_data")
                    }
                }
            )
            
            if result.get("success"):
                state["fundamentals_report"] = result.get("analysis", "")
                state["financial_data"] = result.get("financial_data", {})
                add_message(state, "fundamentals_analyst", result.get("analysis", ""))
                logger.info("✅ 基本面分析完成")
            else:
                error_msg = f"基本面分析失败: {result.get('error', 'Unknown error')}"
                state["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")
            
            update_state_step(state, "fundamentals_analyst")
            
        except Exception as e:
            error_msg = f"基本面分析师节点异常: {e}"
            state["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        return state
    
    async def news_analyst_node(self, state: GraphState) -> GraphState:
        """新闻分析师节点"""
        logger.info("📰 执行新闻分析师节点")
        
        try:
            result = await self._call_agent_service(
                AgentTypeEnum.NEWS_ANALYST,
                TaskTypeEnum.NEWS_ANALYSIS,
                {
                    "symbol": state["symbol"],
                    "analysis_type": "news_sentiment",
                    "context": {
                        "current_date": state["current_date"],
                        "days": 7
                    }
                }
            )
            
            if result.get("success"):
                state["news_report"] = result.get("analysis", "")
                state["sentiment_report"] = result.get("sentiment_analysis", "")
                state["news_data"] = result.get("news_data", {})
                add_message(state, "news_analyst", result.get("analysis", ""))
                logger.info("✅ 新闻分析完成")
            else:
                error_msg = f"新闻分析失败: {result.get('error', 'Unknown error')}"
                state["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")
            
            update_state_step(state, "news_analyst")
            
        except Exception as e:
            error_msg = f"新闻分析师节点异常: {e}"
            state["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        return state
    
    async def social_analyst_node(self, state: GraphState) -> GraphState:
        """社交媒体分析师节点"""
        logger.info("📱 执行社交媒体分析师节点")
        
        try:
            result = await self._call_agent_service(
                AgentTypeEnum.SOCIAL_MEDIA_ANALYST,
                TaskTypeEnum.SENTIMENT_ANALYSIS,
                {
                    "symbol": state["symbol"],
                    "analysis_type": "social_sentiment",
                    "context": {
                        "current_date": state["current_date"],
                        "platforms": ["reddit", "twitter"]
                    }
                }
            )
            
            if result.get("success"):
                state["social_report"] = result.get("analysis", "")
                state["social_data"] = result.get("social_data", {})
                add_message(state, "social_analyst", result.get("analysis", ""))
                logger.info("✅ 社交媒体分析完成")
            else:
                error_msg = f"社交媒体分析失败: {result.get('error', 'Unknown error')}"
                state["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")
            
            update_state_step(state, "social_analyst")
            
        except Exception as e:
            error_msg = f"社交媒体分析师节点异常: {e}"
            state["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        return state
    
    # 研究员节点
    async def bull_researcher_node(self, state: GraphState) -> GraphState:
        """多头研究员节点"""
        logger.info("🐂 执行多头研究员节点")
        
        try:
            # 收集所有分析报告作为上下文
            context = {
                "technical_report": state.get("technical_report"),
                "fundamentals_report": state.get("fundamentals_report"),
                "news_report": state.get("news_report"),
                "sentiment_report": state.get("sentiment_report"),
                "social_report": state.get("social_report"),
                "debate_history": state.get("debate_history", [])
            }
            
            result = await self._call_agent_service(
                AgentTypeEnum.BULL_RESEARCHER,
                TaskTypeEnum.BULL_RESEARCH,
                {
                    "symbol": state["symbol"],
                    "research_type": "bull_case",
                    "context": context
                }
            )
            
            if result.get("success"):
                state["bull_analysis"] = result.get("research", "")
                
                # 添加到辩论历史
                debate_entry = {
                    "speaker": "bull_researcher",
                    "content": result.get("research", ""),
                    "timestamp": logger.info.__globals__.get('datetime', __import__('datetime')).datetime.now().isoformat(),
                    "round": len(state.get("debate_history", [])) + 1
                }
                
                if "debate_history" not in state:
                    state["debate_history"] = []
                state["debate_history"].append(debate_entry)
                
                add_message(state, "bull_researcher", result.get("research", ""))
                logger.info("✅ 多头研究完成")
            else:
                error_msg = f"多头研究失败: {result.get('error', 'Unknown error')}"
                state["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")
            
            update_state_step(state, "bull_researcher")
            
        except Exception as e:
            error_msg = f"多头研究员节点异常: {e}"
            state["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        return state
    
    async def bear_researcher_node(self, state: GraphState) -> GraphState:
        """空头研究员节点"""
        logger.info("🐻 执行空头研究员节点")
        
        try:
            context = {
                "technical_report": state.get("technical_report"),
                "fundamentals_report": state.get("fundamentals_report"),
                "news_report": state.get("news_report"),
                "sentiment_report": state.get("sentiment_report"),
                "social_report": state.get("social_report"),
                "debate_history": state.get("debate_history", []),
                "bull_analysis": state.get("bull_analysis")  # 反驳多头观点
            }
            
            result = await self._call_agent_service(
                AgentTypeEnum.BEAR_RESEARCHER,
                TaskTypeEnum.BEAR_RESEARCH,
                {
                    "symbol": state["symbol"],
                    "research_type": "bear_case",
                    "context": context
                }
            )
            
            if result.get("success"):
                state["bear_analysis"] = result.get("research", "")
                
                # 添加到辩论历史
                debate_entry = {
                    "speaker": "bear_researcher",
                    "content": result.get("research", ""),
                    "timestamp": logger.info.__globals__.get('datetime', __import__('datetime')).datetime.now().isoformat(),
                    "round": len(state.get("debate_history", [])) + 1
                }
                
                if "debate_history" not in state:
                    state["debate_history"] = []
                state["debate_history"].append(debate_entry)
                
                add_message(state, "bear_researcher", result.get("research", ""))
                logger.info("✅ 空头研究完成")
            else:
                error_msg = f"空头研究失败: {result.get('error', 'Unknown error')}"
                state["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")
            
            update_state_step(state, "bear_researcher")
            
        except Exception as e:
            error_msg = f"空头研究员节点异常: {e}"
            state["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        return state
    
    async def research_manager_node(self, state: GraphState) -> GraphState:
        """研究经理节点"""
        logger.info("👔 执行研究经理节点")
        
        try:
            # 综合所有分析和研究
            context = {
                "all_reports": {
                    "technical": state.get("technical_report"),
                    "fundamentals": state.get("fundamentals_report"),
                    "news": state.get("news_report"),
                    "sentiment": state.get("sentiment_report"),
                    "social": state.get("social_report")
                },
                "research": {
                    "bull_analysis": state.get("bull_analysis"),
                    "bear_analysis": state.get("bear_analysis")
                },
                "debate_history": state.get("debate_history", [])
            }
            
            result = await self._call_agent_service(
                AgentTypeEnum.RESEARCH_MANAGER,
                TaskTypeEnum.RESEARCH_MANAGEMENT,
                {
                    "symbol": state["symbol"],
                    "synthesis_type": "investment_recommendation",
                    "context": context
                }
            )
            
            if result.get("success"):
                state["investment_plan"] = result.get("investment_plan", "")
                state["final_recommendation"] = result.get("recommendation", {})
                
                # 生成辩论摘要
                state["debate_summary"] = {
                    "total_rounds": len(state.get("debate_history", [])),
                    "consensus_reached": result.get("consensus_reached", False),
                    "final_stance": result.get("final_stance", "neutral")
                }
                
                add_message(state, "research_manager", result.get("investment_plan", ""))
                logger.info("✅ 研究经理综合完成")
            else:
                error_msg = f"研究经理综合失败: {result.get('error', 'Unknown error')}"
                state["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")
            
            update_state_step(state, "research_manager")
            
        except Exception as e:
            error_msg = f"研究经理节点异常: {e}"
            state["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        return state
    
    # 风险分析节点
    async def risky_analyst_node(self, state: GraphState) -> GraphState:
        """激进分析师节点"""
        logger.info("🔥 执行激进分析师节点")
        
        try:
            context = {
                "investment_plan": state.get("investment_plan"),
                "final_recommendation": state.get("final_recommendation"),
                "risk_history": state.get("risk_history", [])
            }
            
            result = await self._call_agent_service(
                AgentTypeEnum.RISKY_DEBATOR,
                TaskTypeEnum.RISK_ASSESSMENT,
                {
                    "symbol": state["symbol"],
                    "risk_type": "aggressive",
                    "context": context
                }
            )
            
            if result.get("success"):
                state["risky_analysis"] = result.get("analysis", "")
                
                # 添加到风险分析历史
                risk_entry = {
                    "speaker": "risky_analyst",
                    "content": result.get("analysis", ""),
                    "timestamp": logger.info.__globals__.get('datetime', __import__('datetime')).datetime.now().isoformat(),
                    "round": len(state.get("risk_history", [])) + 1
                }
                
                if "risk_history" not in state:
                    state["risk_history"] = []
                state["risk_history"].append(risk_entry)
                
                add_message(state, "risky_analyst", result.get("analysis", ""))
                logger.info("✅ 激进风险分析完成")
            else:
                error_msg = f"激进风险分析失败: {result.get('error', 'Unknown error')}"
                state["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")
            
            update_state_step(state, "risky_analyst")
            
        except Exception as e:
            error_msg = f"激进分析师节点异常: {e}"
            state["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        return state
    
    async def safe_analyst_node(self, state: GraphState) -> GraphState:
        """保守分析师节点"""
        logger.info("🛡️ 执行保守分析师节点")
        
        try:
            context = {
                "investment_plan": state.get("investment_plan"),
                "final_recommendation": state.get("final_recommendation"),
                "risk_history": state.get("risk_history", []),
                "risky_analysis": state.get("risky_analysis")
            }
            
            result = await self._call_agent_service(
                AgentTypeEnum.SAFE_DEBATOR,
                TaskTypeEnum.RISK_ASSESSMENT,
                {
                    "symbol": state["symbol"],
                    "risk_type": "conservative",
                    "context": context
                }
            )
            
            if result.get("success"):
                state["safe_analysis"] = result.get("analysis", "")
                
                risk_entry = {
                    "speaker": "safe_analyst",
                    "content": result.get("analysis", ""),
                    "timestamp": logger.info.__globals__.get('datetime', __import__('datetime')).datetime.now().isoformat(),
                    "round": len(state.get("risk_history", [])) + 1
                }
                
                if "risk_history" not in state:
                    state["risk_history"] = []
                state["risk_history"].append(risk_entry)
                
                add_message(state, "safe_analyst", result.get("analysis", ""))
                logger.info("✅ 保守风险分析完成")
            else:
                error_msg = f"保守风险分析失败: {result.get('error', 'Unknown error')}"
                state["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")
            
            update_state_step(state, "safe_analyst")
            
        except Exception as e:
            error_msg = f"保守分析师节点异常: {e}"
            state["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        return state
    
    async def neutral_analyst_node(self, state: GraphState) -> GraphState:
        """中性分析师节点"""
        logger.info("⚖️ 执行中性分析师节点")
        
        try:
            context = {
                "investment_plan": state.get("investment_plan"),
                "final_recommendation": state.get("final_recommendation"),
                "risk_history": state.get("risk_history", []),
                "risky_analysis": state.get("risky_analysis"),
                "safe_analysis": state.get("safe_analysis")
            }
            
            result = await self._call_agent_service(
                AgentTypeEnum.NEUTRAL_DEBATOR,
                TaskTypeEnum.RISK_ASSESSMENT,
                {
                    "symbol": state["symbol"],
                    "risk_type": "balanced",
                    "context": context
                }
            )
            
            if result.get("success"):
                state["neutral_analysis"] = result.get("analysis", "")
                
                risk_entry = {
                    "speaker": "neutral_analyst",
                    "content": result.get("analysis", ""),
                    "timestamp": logger.info.__globals__.get('datetime', __import__('datetime')).datetime.now().isoformat(),
                    "round": len(state.get("risk_history", [])) + 1
                }
                
                if "risk_history" not in state:
                    state["risk_history"] = []
                state["risk_history"].append(risk_entry)
                
                add_message(state, "neutral_analyst", result.get("analysis", ""))
                logger.info("✅ 中性风险分析完成")
            else:
                error_msg = f"中性风险分析失败: {result.get('error', 'Unknown error')}"
                state["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")
            
            update_state_step(state, "neutral_analyst")
            
        except Exception as e:
            error_msg = f"中性分析师节点异常: {e}"
            state["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        return state
    
    async def risk_manager_node(self, state: GraphState) -> GraphState:
        """风险经理节点"""
        logger.info("⚠️ 执行风险经理节点")
        
        try:
            context = {
                "investment_plan": state.get("investment_plan"),
                "final_recommendation": state.get("final_recommendation"),
                "risk_analyses": {
                    "risky": state.get("risky_analysis"),
                    "safe": state.get("safe_analysis"),
                    "neutral": state.get("neutral_analysis")
                },
                "risk_history": state.get("risk_history", [])
            }
            
            result = await self._call_agent_service(
                AgentTypeEnum.RISK_MANAGER,
                TaskTypeEnum.RISK_ASSESSMENT,
                {
                    "symbol": state["symbol"],
                    "assessment_type": "comprehensive_risk",
                    "context": context
                }
            )
            
            if result.get("success"):
                state["risk_assessment"] = result.get("risk_assessment", {})
                
                # 生成风险分析摘要
                state["risk_summary"] = {
                    "total_rounds": len(state.get("risk_history", [])),
                    "risk_level": result.get("risk_level", "medium"),
                    "final_risk_score": result.get("risk_score", 0.5)
                }
                
                add_message(state, "risk_manager", str(result.get("risk_assessment", {})))
                logger.info("✅ 风险经理评估完成")
            else:
                error_msg = f"风险经理评估失败: {result.get('error', 'Unknown error')}"
                state["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")
            
            update_state_step(state, "risk_manager")
            
        except Exception as e:
            error_msg = f"风险经理节点异常: {e}"
            state["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        return state
    
    async def trader_node(self, state: GraphState) -> GraphState:
        """交易员节点"""
        logger.info("💼 执行交易员节点")
        
        try:
            context = {
                "investment_plan": state.get("investment_plan"),
                "final_recommendation": state.get("final_recommendation")
            }
            
            result = await self._call_agent_service(
                AgentTypeEnum.TRADER,
                TaskTypeEnum.TRADING_DECISION,
                {
                    "symbol": state["symbol"],
                    "plan_type": "execution_plan",
                    "context": context
                }
            )
            
            if result.get("success"):
                state["trade_decision"] = result.get("trade_plan", {})
                add_message(state, "trader", str(result.get("trade_plan", {})))
                logger.info("✅ 交易员计划完成")
            else:
                error_msg = f"交易员计划失败: {result.get('error', 'Unknown error')}"
                state["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")
            
            update_state_step(state, "trader")
            
        except Exception as e:
            error_msg = f"交易员节点异常: {e}"
            state["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
        
        return state
    
    # 辅助节点
    def get_analyst_node(self, analyst_type: str):
        """获取分析师节点"""
        node_mapping = {
            "market": self.market_analyst_node,
            "fundamentals": self.fundamentals_analyst_node,
            "news": self.news_analyst_node,
            "social": self.social_analyst_node
        }
        return node_mapping.get(analyst_type)
    
    def get_clear_node(self, analyst_type: str):
        """获取清理节点"""
        async def clear_node(state: GraphState) -> GraphState:
            """清理消息节点"""
            logger.debug(f"🧹 清理{analyst_type}分析师消息")
            # 这里可以添加消息清理逻辑
            # 目前只是标记步骤完成
            update_state_step(state, f"clear_{analyst_type}")
            return state
        
        return clear_node
