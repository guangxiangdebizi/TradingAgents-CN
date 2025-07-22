#!/usr/bin/env python3
"""
YFinance 数据源实现
"""

import asyncio
import logging
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .base import (
    BaseDataSource, DataSourceConfig, DataSourceType, MarketType, 
    DataCategory, DataSourceError, DataNotFoundError, DataSourceStatus
)

logger = logging.getLogger(__name__)

class YFinanceDataSource(BaseDataSource):
    """YFinance 数据源"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self._client = None
        self._init_client()
    
    def _init_client(self):
        """初始化 YFinance 客户端"""
        try:
            import yfinance as yf
            self._client = yf
            logger.info("✅ YFinance 客户端初始化成功")
        except ImportError:
            logger.error("❌ YFinance 库未安装，请运行: pip install yfinance")
        except Exception as e:
            logger.error(f"❌ YFinance 客户端初始化失败: {e}")
    
    @property
    def supported_markets(self) -> List[MarketType]:
        return [MarketType.US_STOCK, MarketType.HK_STOCK]
    
    @property
    def supported_categories(self) -> List[DataCategory]:
        return [
            DataCategory.BASIC_INFO,
            DataCategory.PRICE_DATA,
            DataCategory.FUNDAMENTALS
        ]
    
    async def get_stock_info(self, symbol: str, market: MarketType) -> Optional[Dict[str, Any]]:
        """获取股票基本信息"""
        if not self._client:
            return None
        
        try:
            self.record_request()
            
            # 转换股票代码格式
            yf_symbol = self._convert_symbol(symbol, market)
            
            # 获取股票信息
            ticker = self._client.Ticker(yf_symbol)
            info = ticker.info
            
            if not info or not info.get("symbol"):
                raise DataNotFoundError(self.source_type, f"股票信息未找到: {symbol}")
            
            # 格式化返回数据
            result = {
                "symbol": symbol,
                "name": info.get("longName") or info.get("shortName"),
                "market": "美股" if market == MarketType.US_STOCK else "港股",
                "industry": info.get("industry"),
                "sector": info.get("sector"),
                "country": info.get("country"),
                "currency": info.get("currency"),
                "exchange": info.get("exchange"),
                "market_cap": info.get("marketCap"),
                "shares_outstanding": info.get("sharesOutstanding"),
                "float_shares": info.get("floatShares"),
                "beta": info.get("beta"),
                "pe_ratio": info.get("trailingPE"),
                "pb_ratio": info.get("priceToBook"),
                "dividend_yield": info.get("dividendYield"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "website": info.get("website"),
                "business_summary": info.get("businessSummary"),
                "source": self.source_type.value,
                "timestamp": datetime.now().isoformat()
            }
            
            self.reset_error_count()
            return result
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ YFinance 获取股票信息失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取股票信息失败: {e}", e)
    
    async def get_stock_data(self, symbol: str, market: MarketType, 
                           start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取股票价格数据"""
        if not self._client:
            return None
        
        try:
            self.record_request()
            
            # 转换股票代码格式
            yf_symbol = self._convert_symbol(symbol, market)
            
            # 获取历史数据
            ticker = self._client.Ticker(yf_symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                raise DataNotFoundError(self.source_type, f"股票数据未找到: {symbol}")
            
            # 转换为标准格式
            result = []
            for date, row in hist.iterrows():
                result.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]) if not pd.isna(row["Open"]) else None,
                    "high": float(row["High"]) if not pd.isna(row["High"]) else None,
                    "low": float(row["Low"]) if not pd.isna(row["Low"]) else None,
                    "close": float(row["Close"]) if not pd.isna(row["Close"]) else None,
                    "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else None,
                })
            
            # 按日期排序
            result.sort(key=lambda x: x["date"])
            
            self.reset_error_count()
            return result
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ YFinance 获取股票数据失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取股票数据失败: {e}", e)
    
    async def get_fundamentals(self, symbol: str, market: MarketType,
                             start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """获取基本面数据"""
        if not self._client:
            return None
        
        try:
            self.record_request()
            
            # 转换股票代码格式
            yf_symbol = self._convert_symbol(symbol, market)
            
            # 获取股票信息和财务数据
            ticker = self._client.Ticker(yf_symbol)
            info = ticker.info
            
            if not info:
                raise DataNotFoundError(self.source_type, f"基本面数据未找到: {symbol}")
            
            # 格式化返回数据
            result = {
                "symbol": symbol,
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "pb_ratio": info.get("priceToBook"),
                "ps_ratio": info.get("priceToSalesTrailing12Months"),
                "peg_ratio": info.get("pegRatio"),
                "roe": info.get("returnOnEquity"),
                "roa": info.get("returnOnAssets"),
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio"),
                "quick_ratio": info.get("quickRatio"),
                "gross_margin": info.get("grossMargins"),
                "operating_margin": info.get("operatingMargins"),
                "profit_margin": info.get("profitMargins"),
                "dividend_yield": info.get("dividendYield"),
                "payout_ratio": info.get("payoutRatio"),
                "beta": info.get("beta"),
                "eps_ttm": info.get("trailingEps"),
                "eps_forward": info.get("forwardEps"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "book_value": info.get("bookValue"),
                "price_to_book": info.get("priceToBook"),
                "enterprise_value": info.get("enterpriseValue"),
                "ebitda": info.get("ebitda"),
                "market_cap": info.get("marketCap"),
                "shares_outstanding": info.get("sharesOutstanding"),
                "source": self.source_type.value,
                "timestamp": datetime.now().isoformat()
            }
            
            self.reset_error_count()
            return result
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ YFinance 获取基本面数据失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取基本面数据失败: {e}", e)
    
    async def get_news(self, symbol: str, market: MarketType,
                      start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取新闻数据"""
        if not self._client:
            return None
        
        try:
            self.record_request()
            
            # 转换股票代码格式
            yf_symbol = self._convert_symbol(symbol, market)
            
            # 获取新闻数据
            ticker = self._client.Ticker(yf_symbol)
            news = ticker.news
            
            if not news:
                return []
            
            # 转换为标准格式
            result = []
            for item in news[:20]:  # 限制返回数量
                result.append({
                    "title": item.get("title"),
                    "content": item.get("summary", ""),
                    "publish_time": datetime.fromtimestamp(item.get("providerPublishTime", 0)).isoformat(),
                    "source": item.get("publisher"),
                    "url": item.get("link"),
                    "type": item.get("type"),
                    "timestamp": datetime.now().isoformat()
                })
            
            self.reset_error_count()
            return result
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ YFinance 获取新闻数据失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取新闻数据失败: {e}", e)
    
    def _convert_symbol(self, symbol: str, market: MarketType) -> str:
        """转换股票代码为 YFinance 格式"""
        if market == MarketType.US_STOCK:
            # 美股直接使用原始代码
            return symbol.upper()
        elif market == MarketType.HK_STOCK:
            # 港股需要添加 .HK 后缀
            if not symbol.endswith(".HK"):
                # 如果是5位数字，需要补零到4位
                if symbol.isdigit() and len(symbol) == 5:
                    symbol = symbol.zfill(4)
                return f"{symbol}.HK"
            return symbol
        else:
            return symbol
    
    async def health_check(self) -> bool:
        """健康检查"""
        if not self._client:
            return False
        
        try:
            # 尝试获取一个简单的数据
            ticker = self._client.Ticker("AAPL")
            info = ticker.info
            return bool(info and info.get("symbol"))
        except Exception as e:
            logger.error(f"❌ YFinance 健康检查失败: {e}")
            self.status = DataSourceStatus.ERROR
            return False
