"""
智能体模块 - 完整的业务实体实现
移植自tradingagents，包含完整的分析逻辑
"""

# 基础智能体
from .base import BaseAgent

# 分析师智能体
from .analysts.market_analyst import MarketAnalyst
from .analysts.fundamentals_analyst import FundamentalsAnalyst
from .analysts.news_analyst import NewsAnalyst
from .analysts.social_analyst import SocialAnalyst

# 研究员智能体
from .researchers.bull_researcher import BullResearcher
from .researchers.bear_researcher import BearResearcher
from .researchers.research_manager import ResearchManager

# 交易员智能体
from .traders.trader import Trader

# 风险管理智能体
from .managers.risk_manager import RiskManager
from .managers.portfolio_manager import PortfolioManager

__all__ = [
    "BaseAgent",
    "MarketAnalyst",
    "FundamentalsAnalyst",
    "NewsAnalyst",
    "SocialAnalyst",
    "BullResearcher",
    "BearResearcher",
    "ResearchManager",
    "Trader",
    "RiskManager",
    "PortfolioManager"
]
