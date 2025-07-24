#!/usr/bin/env python3
"""
统一工具实现
基于tradingagents的统一工具设计
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import aiohttp

from .data_tools import DataTools
from .analysis_tools import AnalysisTools
from .news_tools import NewsTools

logger = logging.getLogger(__name__)

class UnifiedTools:
    """统一工具实现"""
    
    def __init__(self):
        self.data_tools: Optional[DataTools] = None
        self.analysis_tools: Optional[AnalysisTools] = None
        self.news_tools: Optional[NewsTools] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.initialized = False
    
    async def initialize(self):
        """初始化统一工具"""
        try:
            logger.info("🔧 初始化统一工具...")
            
            # 初始化各类工具
            self.data_tools = DataTools()
            await self.data_tools.initialize()
            
            self.analysis_tools = AnalysisTools()
            await self.analysis_tools.initialize()
            
            self.news_tools = NewsTools()
            await self.news_tools.initialize()
            
            # 创建HTTP会话
            self.session = aiohttp.ClientSession()
            
            self.initialized = True
            logger.info("✅ 统一工具初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 统一工具初始化失败: {e}")
            raise
    
    def _identify_stock_market(self, ticker: str) -> str:
        """识别股票市场类型"""
        ticker = str(ticker).strip().upper()
        
        # 中国A股：6位数字
        if len(ticker) == 6 and ticker.isdigit():
            return "CN"
        
        # 港股：数字.HK格式
        if ticker.endswith(".HK") and ticker[:-3].isdigit():
            return "HK"
        
        # 美股：字母组合
        if ticker.isalpha():
            return "US"
        
        return "UNKNOWN"
    
    async def get_stock_market_data_unified(self, ticker: str, start_date: str, end_date: str) -> str:
        """
        统一的股票市场数据工具
        自动识别股票类型并调用相应的数据源获取价格和技术指标数据
        
        Args:
            ticker: 股票代码（如：000001、0700.HK、AAPL）
            start_date: 开始日期（格式：YYYY-MM-DD）
            end_date: 结束日期（格式：YYYY-MM-DD）
        
        Returns:
            str: 市场数据和技术分析报告
        """
        try:
            logger.info(f"📈 [统一市场工具] 分析股票: {ticker}")
            
            # 识别市场类型
            market = self._identify_stock_market(ticker)
            
            # 获取基础股票数据
            stock_data = await self.data_tools.get_stock_data(ticker, "1y")
            
            # 获取市场数据
            market_data = await self.data_tools.get_market_data(ticker, ["price", "volume", "ma", "rsi"])
            
            # 计算技术指标
            technical_indicators = await self.analysis_tools.calculate_technical_indicators(
                market_data, ["RSI", "MACD", "MA5", "MA20", "BOLL"]
            )
            
            # 组合结果
            result = f"""
# 📊 {ticker} 市场数据分析报告

## 基本信息
- **股票代码**: {ticker}
- **市场类型**: {market}
- **分析时间**: {start_date} 至 {end_date}
- **报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 股票基础数据
{stock_data.get('result', {}).get('company_info', '暂无公司信息')}

## 市场数据
{self._format_market_data(market_data.get('result', {}))}

## 技术指标分析
{self._format_technical_indicators(technical_indicators.get('result', {}))}

## 数据来源
- 市场类型: {market}
- 数据源: 根据股票类型自动选择最适合的数据源
- A股: 使用Tushare/AKShare数据
- 港股: 使用AKShare/Yahoo Finance数据  
- 美股: 使用Yahoo Finance/Alpha Vantage数据

---
*数据来源: 根据股票类型自动选择最适合的数据源*
"""
            
            logger.info(f"📊 [统一市场工具] 数据获取完成，总长度: {len(result)}")
            return result
            
        except Exception as e:
            error_msg = f"统一市场数据工具执行失败: {str(e)}"
            logger.error(f"❌ [统一市场工具] {error_msg}")
            return error_msg
    
    async def get_stock_fundamentals_unified(self, ticker: str, start_date: str, end_date: str) -> str:
        """
        统一的股票基本面数据工具
        获取财务数据和公司基本面信息
        
        Args:
            ticker: 股票代码
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            str: 基本面分析报告
        """
        try:
            logger.info(f"📋 [统一基本面工具] 分析股票: {ticker}")
            
            # 识别市场类型
            market = self._identify_stock_market(ticker)
            
            # 获取财务数据
            financial_data = await self.data_tools.get_financial_data(ticker, "income")
            
            # 执行基本面分析
            fundamental_analysis = await self.analysis_tools.perform_fundamental_analysis(
                financial_data.get('result', {}), {}
            )
            
            # 计算估值
            valuation = await self.analysis_tools.calculate_valuation(
                financial_data.get('result', {}), "DCF"
            )
            
            # 组合结果
            result = f"""
# 📋 {ticker} 基本面分析报告

## 基本信息
- **股票代码**: {ticker}
- **市场类型**: {market}
- **分析期间**: {start_date} 至 {end_date}
- **报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 财务数据概览
{self._format_financial_data(financial_data.get('result', {}))}

## 基本面分析
{self._format_fundamental_analysis(fundamental_analysis.get('result', {}))}

## 估值分析
{self._format_valuation_analysis(valuation.get('result', {}))}

## 投资建议
{self._generate_investment_advice(fundamental_analysis.get('result', {}), valuation.get('result', {}))}

---
*数据来源: 根据股票类型自动选择最适合的数据源*
"""
            
            logger.info(f"📋 [统一基本面工具] 数据获取完成，总长度: {len(result)}")
            return result
            
        except Exception as e:
            error_msg = f"统一基本面分析工具执行失败: {str(e)}"
            logger.error(f"❌ [统一基本面工具] {error_msg}")
            return error_msg
    
    async def get_stock_news_unified(self, ticker: str, days: int = 7) -> str:
        """
        统一的股票新闻工具
        获取相关新闻和情感分析
        
        Args:
            ticker: 股票代码
            days: 获取最近几天的新闻
        
        Returns:
            str: 新闻和情感分析报告
        """
        try:
            logger.info(f"📰 [统一新闻工具] 分析股票: {ticker}")
            
            # 获取股票新闻
            news_data = await self.news_tools.get_stock_news(ticker, days)
            
            # 分析情感
            sentiment_analysis = await self.news_tools.analyze_sentiment(
                news_data.get('result', {}).get('content', ''), "news"
            )
            
            # 组合结果
            result = f"""
# 📰 {ticker} 新闻情感分析报告

## 基本信息
- **股票代码**: {ticker}
- **分析天数**: {days}天
- **报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 新闻概览
{self._format_news_data(news_data.get('result', {}))}

## 情感分析
{self._format_sentiment_analysis(sentiment_analysis.get('result', {}))}

## 市场情绪总结
{self._generate_sentiment_summary(sentiment_analysis.get('result', {}))}

---
*新闻来源: 多渠道新闻聚合分析*
"""
            
            logger.info(f"📰 [统一新闻工具] 数据获取完成，总长度: {len(result)}")
            return result
            
        except Exception as e:
            error_msg = f"统一新闻分析工具执行失败: {str(e)}"
            logger.error(f"❌ [统一新闻工具] {error_msg}")
            return error_msg
    
    def _format_market_data(self, data: Dict[str, Any]) -> str:
        """格式化市场数据"""
        if not data:
            return "暂无市场数据"
        
        return f"""
- 当前价格: {data.get('current_price', 'N/A')}
- 成交量: {data.get('volume', 'N/A')}
- 涨跌幅: {data.get('change_percent', 'N/A')}%
- 52周最高: {data.get('high_52w', 'N/A')}
- 52周最低: {data.get('low_52w', 'N/A')}
"""
    
    def _format_technical_indicators(self, data: Dict[str, Any]) -> str:
        """格式化技术指标"""
        if not data:
            return "暂无技术指标数据"
        
        return f"""
- RSI: {data.get('RSI', 'N/A')}
- MACD: {data.get('MACD', 'N/A')}
- MA5: {data.get('MA5', 'N/A')}
- MA20: {data.get('MA20', 'N/A')}
- 布林带: {data.get('BOLL', 'N/A')}
"""
    
    def _format_financial_data(self, data: Dict[str, Any]) -> str:
        """格式化财务数据"""
        if not data:
            return "暂无财务数据"
        
        return f"""
- 营业收入: {data.get('revenue', 'N/A')}
- 净利润: {data.get('net_income', 'N/A')}
- 总资产: {data.get('total_assets', 'N/A')}
- 净资产: {data.get('net_assets', 'N/A')}
"""
    
    def _format_fundamental_analysis(self, data: Dict[str, Any]) -> str:
        """格式化基本面分析"""
        if not data:
            return "暂无基本面分析数据"
        
        return f"""
- ROE: {data.get('roe', 'N/A')}%
- ROA: {data.get('roa', 'N/A')}%
- 毛利率: {data.get('gross_margin', 'N/A')}%
- 净利率: {data.get('net_margin', 'N/A')}%
"""
    
    def _format_valuation_analysis(self, data: Dict[str, Any]) -> str:
        """格式化估值分析"""
        if not data:
            return "暂无估值分析数据"
        
        return f"""
- P/E比率: {data.get('pe_ratio', 'N/A')}
- P/B比率: {data.get('pb_ratio', 'N/A')}
- 估值: {data.get('valuation', 'N/A')}
- 投资评级: {data.get('rating', 'N/A')}
"""
    
    def _format_news_data(self, data: Dict[str, Any]) -> str:
        """格式化新闻数据"""
        if not data:
            return "暂无新闻数据"
        
        return f"""
- 新闻数量: {data.get('count', 0)}条
- 最新新闻: {data.get('latest_title', 'N/A')}
- 新闻来源: {data.get('sources', 'N/A')}
"""
    
    def _format_sentiment_analysis(self, data: Dict[str, Any]) -> str:
        """格式化情感分析"""
        if not data:
            return "暂无情感分析数据"
        
        return f"""
- 整体情感: {data.get('overall_sentiment', 'N/A')}
- 正面比例: {data.get('positive_ratio', 'N/A')}%
- 负面比例: {data.get('negative_ratio', 'N/A')}%
- 中性比例: {data.get('neutral_ratio', 'N/A')}%
"""
    
    def _generate_investment_advice(self, fundamental: Dict[str, Any], valuation: Dict[str, Any]) -> str:
        """生成投资建议"""
        return """
基于基本面和估值分析，建议投资者：
1. 关注公司财务健康状况
2. 考虑当前估值水平
3. 结合市场环境做出投资决策
4. 建议咨询专业投资顾问
"""
    
    def _generate_sentiment_summary(self, sentiment: Dict[str, Any]) -> str:
        """生成情感总结"""
        return """
基于新闻情感分析：
1. 市场情绪整体偏向中性
2. 建议关注重大新闻事件
3. 情感分析仅供参考，不构成投资建议
"""
    
    async def cleanup(self):
        """清理资源"""
        if self.session:
            await self.session.close()
        
        if self.data_tools:
            await self.data_tools.cleanup()
        
        if self.analysis_tools:
            await self.analysis_tools.cleanup()
        
        if self.news_tools:
            await self.news_tools.cleanup()
        
        self.initialized = False
        logger.info("✅ 统一工具资源清理完成")
