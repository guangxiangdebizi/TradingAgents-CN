"""
Backend图状态定义
基于TradingAgents的状态结构，适配Backend的微服务架构
"""

from typing import Dict, List, Any, Optional, TypedDict, Annotated
from datetime import datetime
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    """Backend图状态定义"""

    # LangGraph必需字段
    messages: Annotated[List[BaseMessage], add_messages]  # 消息历史

    # 基本信息
    symbol: str                    # 股票代码
    company_name: str             # 公司名称
    analysis_type: str            # 分析类型
    current_date: str             # 当前日期

    # 原始数据
    stock_data: Optional[Dict[str, Any]]      # 股票基础数据
    financial_data: Optional[Dict[str, Any]]  # 财务数据
    market_data: Optional[Dict[str, Any]]     # 市场数据
    news_data: Optional[Dict[str, Any]]       # 新闻数据
    social_data: Optional[Dict[str, Any]]     # 社交媒体数据

    # 分析报告
    fundamentals_report: Optional[str]        # 基本面分析报告
    technical_report: Optional[str]           # 技术分析报告
    news_report: Optional[str]                # 新闻分析报告
    sentiment_report: Optional[str]           # 情感分析报告
    social_report: Optional[str]              # 社交媒体分析报告

    # 研究员观点
    bull_analysis: Optional[str]              # 多头分析
    bear_analysis: Optional[str]              # 空头分析

    # 风险管理
    risk_assessment: Optional[Dict[str, Any]] # 风险评估
    risky_analysis: Optional[str]             # 激进分析
    safe_analysis: Optional[str]              # 保守分析
    neutral_analysis: Optional[str]           # 中性分析

    # 最终决策
    final_recommendation: Optional[Dict[str, Any]]  # 最终推荐
    investment_plan: Optional[str]                  # 投资计划
    trade_decision: Optional[Dict[str, Any]]        # 交易决策

    # 辅助信息
    errors: List[str]                         # 错误信息
    warnings: List[str]                       # 警告信息
    metadata: Dict[str, Any]                  # 元数据

    # 执行状态
    current_step: str                         # 当前步骤
    completed_steps: List[str]                # 已完成步骤
    next_steps: List[str]                     # 下一步骤

    # 辩论状态
    debate_history: List[Dict[str, Any]]      # 辩论历史
    debate_summary: Optional[Dict[str, Any]]  # 辩论摘要

    # 风险分析状态
    risk_history: List[Dict[str, Any]]        # 风险分析历史
    risk_summary: Optional[Dict[str, Any]]    # 风险分析摘要

class DebateState(TypedDict):
    """辩论状态"""
    round_number: int                         # 当前轮数
    max_rounds: int                          # 最大轮数
    current_speaker: Optional[str]           # 当前发言者
    bull_arguments: List[Dict[str, Any]]     # 多头论点
    bear_arguments: List[Dict[str, Any]]     # 空头论点
    consensus_reached: bool                  # 是否达成共识
    consensus_score: float                   # 共识分数

def create_initial_state(
    symbol: str,
    analysis_type: str = "comprehensive",
    current_date: str = None
) -> GraphState:
    """创建初始状态"""
    if current_date is None:
        current_date = datetime.now().strftime("%Y-%m-%d")

    return GraphState(
        # 基本信息
        symbol=symbol,
        company_name=symbol,  # 初始值，后续可通过工具获取
        analysis_type=analysis_type,
        current_date=current_date,

        # 原始数据初始化为None
        stock_data=None,
        financial_data=None,
        market_data=None,
        news_data=None,
        social_data=None,

        # 分析报告初始化为None
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
        messages=[],  # 注意：这里应该在实际使用时用HumanMessage初始化
        errors=[],
        warnings=[],
        metadata={
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "backend_type": "microservices_graph"
        },

        # 执行状态
        current_step="initialization",
        completed_steps=[],
        next_steps=["market_analyst"],

        # 辩论状态
        debate_history=[],
        debate_summary=None,

        # 风险分析状态
        risk_history=[],
        risk_summary=None
    )
    current_step: str
    completed_steps: List[str]
    next_steps: List[str]

class AnalysisParameters(TypedDict):
    """分析参数"""
    
    # 分析配置
    enable_fundamentals: bool
    enable_technical: bool
    enable_news: bool
    enable_sentiment: bool
    enable_debate: bool
    enable_risk_assessment: bool
    
    # 模型配置
    model_name: str
    temperature: float
    max_tokens: int
    
    # 时间配置
    analysis_period: str
    lookback_days: int
    
    # 其他配置
    debug_mode: bool
    save_intermediate: bool


# 辅助函数
def update_state_step(state: GraphState, step: str, status: str = "running") -> GraphState:
    """更新状态步骤"""
    # 这里可以添加步骤跟踪逻辑
    # 目前简单返回原状态
    return state


def add_message(state: GraphState, role: str, content: str) -> GraphState:
    """添加消息到状态"""
    # 这里可以添加消息历史跟踪逻辑
    # 目前简单返回原状态
    return state
