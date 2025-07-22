#!/usr/bin/env python3
"""
Alpha Vantage 数据源实现 - Yahoo Finance的优秀替代
"""

import asyncio
import logging
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .base import (
    BaseDataSource, DataSourceConfig, DataSourceType, MarketType, 
    DataCategory, DataSourceError, DataNotFoundError
)

logger = logging.getLogger(__name__)

class AlphaVantageDataSource(BaseDataSource):
    """Alpha Vantage 数据源 - 免费美股数据的优秀选择"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.timeout = getattr(config, 'timeout', 60)
        
        if not self.api_key:
            logger.warning("⚠️ Alpha Vantage API Key 未配置")
    
    @property
    def supported_markets(self) -> List[MarketType]:
        return [MarketType.US_STOCK]
    
    @property
    def supported_categories(self) -> List[DataCategory]:
        return [
            DataCategory.BASIC_INFO,
            DataCategory.PRICE_DATA,
            DataCategory.TECHNICAL_INDICATORS
        ]
    
    async def _make_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """发起API请求"""
        if not self.api_key:
            raise DataSourceError(self.source_type, "API Key 未配置")
        
        params['apikey'] = self.api_key
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 检查API错误
                        if "Error Message" in data:
                            raise DataNotFoundError(self.source_type, data["Error Message"])
                        
                        if "Note" in data:
                            # API频率限制
                            raise DataSourceError(self.source_type, f"API频率限制: {data['Note']}")
                        
                        return data
                    else:
                        raise DataSourceError(self.source_type, f"HTTP错误: {response.status}")
        
        except asyncio.TimeoutError:
            raise DataSourceError(self.source_type, f"请求超时 ({self.timeout}秒)")
        except Exception as e:
            raise DataSourceError(self.source_type, str(e))
    
    async def get_stock_info(self, symbol: str, market: MarketType) -> Optional[Dict[str, Any]]:
        """获取股票基本信息"""
        if market != MarketType.US_STOCK:
            return None
        
        try:
            self.record_request()
            
            # 使用 OVERVIEW 功能获取公司基本信息
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol.upper()
            }
            
            data = await self._make_request(params)
            
            if not data or 'Symbol' not in data:
                raise DataNotFoundError(self.source_type, f"股票信息未找到: {symbol}")
            
            # 转换为标准格式
            result = {
                "symbol": symbol.upper(),
                "name": data.get("Name"),
                "market": "美股",
                "exchange": data.get("Exchange"),
                "currency": data.get("Currency", "USD"),
                "country": data.get("Country"),
                "sector": data.get("Sector"),
                "industry": data.get("Industry"),
                "market_cap": self._safe_float(data.get("MarketCapitalization")),
                "pe_ratio": self._safe_float(data.get("PERatio")),
                "dividend_yield": self._safe_float(data.get("DividendYield")),
                "52_week_high": self._safe_float(data.get("52WeekHigh")),
                "52_week_low": self._safe_float(data.get("52WeekLow")),
                "description": data.get("Description"),
                "source": self.source_type.value,
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except (DataSourceError, DataNotFoundError):
            raise
        except Exception as e:
            logger.error(f"❌ Alpha Vantage 获取股票信息失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, str(e))
    
    async def get_stock_data(self, symbol: str, market: MarketType, 
                           start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取股票历史数据"""
        if market != MarketType.US_STOCK:
            return None
        
        try:
            self.record_request()
            
            # 使用 TIME_SERIES_DAILY 获取日线数据
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol.upper(),
                'outputsize': 'full'  # 获取完整历史数据
            }
            
            data = await self._make_request(params)
            
            time_series_key = "Time Series (Daily)"
            if time_series_key not in data:
                raise DataNotFoundError(self.source_type, f"历史数据未找到: {symbol}")
            
            time_series = data[time_series_key]
            
            # 转换为标准格式
            result = []
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            for date_str, values in time_series.items():
                date_dt = datetime.strptime(date_str, "%Y-%m-%d")
                
                # 过滤日期范围
                if start_dt <= date_dt <= end_dt:
                    record = {
                        "date": date_str,
                        "open": self._safe_float(values.get("1. open")),
                        "high": self._safe_float(values.get("2. high")),
                        "low": self._safe_float(values.get("3. low")),
                        "close": self._safe_float(values.get("4. close")),
                        "volume": self._safe_int(values.get("5. volume")),
                        "symbol": symbol.upper(),
                        "source": self.source_type.value
                    }
                    result.append(record)
            
            # 按日期排序
            result.sort(key=lambda x: x["date"])
            
            return result
            
        except (DataSourceError, DataNotFoundError):
            raise
        except Exception as e:
            logger.error(f"❌ Alpha Vantage 获取股票数据失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, str(e))
    
    async def get_real_time_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取实时报价"""
        try:
            self.record_request()
            
            # 使用 GLOBAL_QUOTE 获取实时报价
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol.upper()
            }
            
            data = await self._make_request(params)
            
            quote_key = "Global Quote"
            if quote_key not in data:
                raise DataNotFoundError(self.source_type, f"实时报价未找到: {symbol}")
            
            quote = data[quote_key]
            
            result = {
                "symbol": symbol.upper(),
                "current_price": self._safe_float(quote.get("05. price")),
                "change": self._safe_float(quote.get("09. change")),
                "change_percent": self._safe_float(quote.get("10. change percent", "").replace("%", "")),
                "open": self._safe_float(quote.get("02. open")),
                "high": self._safe_float(quote.get("03. high")),
                "low": self._safe_float(quote.get("04. low")),
                "previous_close": self._safe_float(quote.get("08. previous close")),
                "volume": self._safe_int(quote.get("06. volume")),
                "latest_trading_day": quote.get("07. latest trading day"),
                "source": self.source_type.value,
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except (DataSourceError, DataNotFoundError):
            raise
        except Exception as e:
            logger.error(f"❌ Alpha Vantage 获取实时报价失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, str(e))
    
    def _safe_float(self, value: Any) -> Optional[float]:
        """安全转换为浮点数"""
        if value is None or value == "":
            return None
        try:
            if isinstance(value, str):
                # 移除百分号等特殊字符
                value = value.replace("%", "").replace(",", "")
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value: Any) -> Optional[int]:
        """安全转换为整数"""
        if value is None or value == "":
            return None
        try:
            if isinstance(value, str):
                value = value.replace(",", "")
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    async def get_fundamentals(self, symbol: str, market: MarketType,
                             start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """获取基本面数据 (Alpha Vantage暂不支持)"""
        # Alpha Vantage的基本面数据在OVERVIEW中已包含
        return None

    async def get_news(self, symbol: str, market: MarketType,
                      start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取新闻数据 (Alpha Vantage暂不支持)"""
        # Alpha Vantage免费版不支持新闻数据
        return None

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 使用一个简单的查询测试API
            await self.get_real_time_quote("AAPL")
            return True
        except Exception:
            return False
