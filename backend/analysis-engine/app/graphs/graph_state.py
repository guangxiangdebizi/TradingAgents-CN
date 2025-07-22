"""
图状态定义
定义分析图中的状态结构
"""

from typing import Dict, List, Any, Optional, TypedDict
from datetime import datetime

class GraphState(TypedDict):
    """分析图状态"""
    
    # 基本信息
    symbol: str
    company_name: str
    analysis_type: str
    current_date: str
    
    # 数据
    stock_data: Optional[Dict[str, Any]]
    financial_data: Optional[Dict[str, Any]]
    market_data: Optional[Dict[str, Any]]
    news_data: Optional[Dict[str, Any]]
    
    # 分析结果
    fundamentals_report: Optional[str]
    technical_report: Optional[str]
    news_report: Optional[str]
    sentiment_report: Optional[str]
    
    # 研究员观点
    bull_analysis: Optional[str]
    bear_analysis: Optional[str]
    
    # 风险管理
    risk_assessment: Optional[str]
    
    # 最终决策
    final_recommendation: Optional[str]
    investment_plan: Optional[str]
    
    # 辅助信息
    messages: List[Dict[str, Any]]
    errors: List[str]
    metadata: Dict[str, Any]
    
    # 执行状态
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
