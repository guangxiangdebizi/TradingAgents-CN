#!/usr/bin/env python3
"""
FinnHub 数据源实现
"""

import asyncio
import logging
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .base import (
    BaseDataSource, DataSourceConfig, DataSourceType, MarketType,
    DataCategory, DataSourceError, RateLimitError, DataNotFoundError,
    AuthenticationError, DataSourceStatus
)

logger = logging.getLogger(__name__)

class FinnHubDataSource(BaseDataSource):
    """FinnHub 数据源"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.base_url = "https://finnhub.io/api/v1"
        self.api_key = config.api_key
        self._client = None
        self._init_client()
    
    def _init_client(self):
        """初始化 HTTP 客户端"""
        try:
            if not self.api_key:
                logger.warning("⚠️ FinnHub API Key 未配置")
                return
            
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout),
                headers={
                    "X-Finnhub-Token": self.api_key
                }
            )
            logger.info("✅ FinnHub 客户端初始化成功")
        except Exception as e:
            logger.error(f"❌ FinnHub 客户端初始化失败: {e}")
    
    @property
    def supported_markets(self) -> List[MarketType]:
        return [MarketType.US_STOCK]
    
    @property
    def supported_categories(self) -> List[DataCategory]:
        return [
            DataCategory.BASIC_INFO,
            DataCategory.PRICE_DATA,
            DataCategory.FUNDAMENTALS,
            DataCategory.NEWS
        ]
    
    async def get_stock_info(self, symbol: str, market: MarketType) -> Optional[Dict[str, Any]]:
        """获取股票基本信息"""
        if not self._client or market != MarketType.US_STOCK:
            return None
        
        try:
            self.record_request()
            
            # 获取公司基本信息
            url = f"{self.base_url}/stock/profile2"
            params = {"symbol": symbol.upper()}
            
            response = await self._client.get(url, params=params)
            await self._handle_response(response)
            
            data = response.json()
            
            if not data or not data.get("name"):
                raise DataNotFoundError(self.source_type, f"股票信息未找到: {symbol}")
            
            # 格式化返回数据
            result = {
                "symbol": symbol.upper(),
                "name": data.get("name"),
                "market": "美股",
                "industry": data.get("finnhubIndustry"),
                "sector": data.get("ggroup"),
                "country": data.get("country"),
                "currency": data.get("currency"),
                "exchange": data.get("exchange"),
                "ipo_date": data.get("ipo"),
                "market_cap": data.get("marketCapitalization"),
                "shares_outstanding": data.get("shareOutstanding"),
                "logo": data.get("logo"),
                "weburl": data.get("weburl"),
                "phone": data.get("phone"),
                "source": self.source_type.value,
                "timestamp": datetime.now().isoformat()
            }
            
            self.reset_error_count()
            return result
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ FinnHub 获取股票信息失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取股票信息失败: {e}", e)
    
    async def get_stock_data(self, symbol: str, market: MarketType, 
                           start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取股票价格数据"""
        if not self._client or market != MarketType.US_STOCK:
            return None
        
        try:
            self.record_request()
            
            # 转换日期为时间戳
            start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
            end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
            
            # 获取股票价格数据
            url = f"{self.base_url}/stock/candle"
            params = {
                "symbol": symbol.upper(),
                "resolution": "D",  # 日线数据
                "from": start_timestamp,
                "to": end_timestamp
            }
            
            response = await self._client.get(url, params=params)
            await self._handle_response(response)
            
            data = response.json()
            
            if data.get("s") != "ok" or not data.get("c"):
                raise DataNotFoundError(self.source_type, f"股票数据未找到: {symbol}")
            
            # 转换为标准格式
            result = []
            timestamps = data.get("t", [])
            opens = data.get("o", [])
            highs = data.get("h", [])
            lows = data.get("l", [])
            closes = data.get("c", [])
            volumes = data.get("v", [])
            
            for i in range(len(timestamps)):
                date_str = datetime.fromtimestamp(timestamps[i]).strftime("%Y-%m-%d")
                result.append({
                    "date": date_str,
                    "open": float(opens[i]) if i < len(opens) else None,
                    "high": float(highs[i]) if i < len(highs) else None,
                    "low": float(lows[i]) if i < len(lows) else None,
                    "close": float(closes[i]) if i < len(closes) else None,
                    "volume": int(volumes[i]) if i < len(volumes) else None,
                })
            
            # 按日期排序
            result.sort(key=lambda x: x["date"])
            
            self.reset_error_count()
            return result
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ FinnHub 获取股票数据失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取股票数据失败: {e}", e)
    
    async def get_fundamentals(self, symbol: str, market: MarketType,
                             start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """获取基本面数据"""
        if not self._client or market != MarketType.US_STOCK:
            return None
        
        try:
            self.record_request()
            
            # 获取基本财务指标
            url = f"{self.base_url}/stock/metric"
            params = {"symbol": symbol.upper(), "metric": "all"}
            
            response = await self._client.get(url, params=params)
            await self._handle_response(response)
            
            data = response.json()
            
            if not data or not data.get("metric"):
                raise DataNotFoundError(self.source_type, f"基本面数据未找到: {symbol}")
            
            metrics = data.get("metric", {})
            
            # 格式化返回数据
            result = {
                "symbol": symbol.upper(),
                "pe_ratio": metrics.get("peBasicExclExtraTTM"),
                "pb_ratio": metrics.get("pbQuarterly"),
                "roe": metrics.get("roeRfy"),
                "roa": metrics.get("roaRfy"),
                "debt_to_equity": metrics.get("totalDebt/totalEquityQuarterly"),
                "current_ratio": metrics.get("currentRatioQuarterly"),
                "quick_ratio": metrics.get("quickRatioQuarterly"),
                "gross_margin": metrics.get("grossMarginTTM"),
                "operating_margin": metrics.get("operatingMarginTTM"),
                "net_margin": metrics.get("netProfitMarginTTM"),
                "dividend_yield": metrics.get("dividendYieldIndicatedAnnual"),
                "eps_ttm": metrics.get("epsExclExtraItemsTTM"),
                "revenue_growth": metrics.get("revenueGrowthTTMYoy"),
                "earnings_growth": metrics.get("epsGrowthTTMYoy"),
                "beta": metrics.get("beta"),
                "market_cap": metrics.get("marketCapitalization"),
                "enterprise_value": metrics.get("enterpriseValue"),
                "source": self.source_type.value,
                "timestamp": datetime.now().isoformat()
            }
            
            self.reset_error_count()
            return result
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ FinnHub 获取基本面数据失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取基本面数据失败: {e}", e)
    
    async def get_news(self, symbol: str, market: MarketType,
                      start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取新闻数据"""
        if not self._client or market != MarketType.US_STOCK:
            return None
        
        try:
            self.record_request()
            
            # 转换日期格式
            from_date = start_date
            to_date = end_date
            
            # 获取公司新闻
            url = f"{self.base_url}/company-news"
            params = {
                "symbol": symbol.upper(),
                "from": from_date,
                "to": to_date
            }
            
            response = await self._client.get(url, params=params)
            await self._handle_response(response)
            
            data = response.json()
            
            if not data:
                return []
            
            # 转换为标准格式
            result = []
            for item in data[:20]:  # 限制返回数量
                result.append({
                    "title": item.get("headline"),
                    "content": item.get("summary", ""),
                    "publish_time": datetime.fromtimestamp(item.get("datetime", 0)).isoformat(),
                    "source": item.get("source"),
                    "url": item.get("url"),
                    "category": item.get("category"),
                    "image": item.get("image"),
                    "sentiment": {
                        "bearish": item.get("sentiment", {}).get("bearishPercent"),
                        "bullish": item.get("sentiment", {}).get("bullishPercent"),
                        "neutral": item.get("sentiment", {}).get("neutralPercent")
                    },
                    "timestamp": datetime.now().isoformat()
                })
            
            self.reset_error_count()
            return result
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ FinnHub 获取新闻数据失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取新闻数据失败: {e}", e)
    
    async def _handle_response(self, response: httpx.Response):
        """处理HTTP响应"""
        if response.status_code == 401:
            raise AuthenticationError(self.source_type, "API密钥无效或未授权")
        elif response.status_code == 429:
            raise RateLimitError(self.source_type, "API调用频率超限")
        elif response.status_code != 200:
            raise DataSourceError(self.source_type, f"HTTP错误: {response.status_code}")
        
        # 检查是否返回了错误信息
        try:
            data = response.json()
            if isinstance(data, dict) and data.get("error"):
                raise DataSourceError(self.source_type, f"API错误: {data['error']}")
        except:
            pass  # 忽略JSON解析错误
    
    async def health_check(self) -> bool:
        """健康检查"""
        if not self._client or not self.api_key:
            return False
        
        try:
            # 尝试获取一个简单的数据
            url = f"{self.base_url}/stock/profile2"
            params = {"symbol": "AAPL"}
            
            response = await self._client.get(url, params=params)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ FinnHub 健康检查失败: {e}")
            self.status = DataSourceStatus.ERROR
            return False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
