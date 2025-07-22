#!/usr/bin/env python3
"""
Twelve Data 数据源实现 - Yahoo Finance的优秀替代
免费版：每天800次请求，支持全球市场
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

class TwelveDataSource(BaseDataSource):
    """Twelve Data 数据源 - 支持全球市场的金融数据API"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = "https://api.twelvedata.com"
        self.timeout = getattr(config, 'timeout', 60)
        
        if not self.api_key:
            logger.warning("⚠️ Twelve Data API Key 未配置")
    
    @property
    def supported_markets(self) -> List[MarketType]:
        return [MarketType.US_STOCK, MarketType.HK_STOCK]  # 支持美股和港股
    
    @property
    def supported_categories(self) -> List[DataCategory]:
        return [
            DataCategory.BASIC_INFO,
            DataCategory.PRICE_DATA,
            DataCategory.TECHNICAL_INDICATORS,
            DataCategory.NEWS
        ]
    
    async def _make_request(self, endpoint: str, params: Dict[str, str] = None) -> Any:
        """发起API请求"""
        if not self.api_key:
            raise DataSourceError(self.source_type, "API Key 未配置")
        
        if params is None:
            params = {}
        
        params['apikey'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 检查API错误
                        if isinstance(data, dict):
                            if "code" in data and data["code"] != 200:
                                if data["code"] == 429:
                                    raise DataSourceError(self.source_type, "API频率限制")
                                elif data["code"] == 401:
                                    raise DataSourceError(self.source_type, "API Key无效")
                                elif data["code"] == 404:
                                    raise DataNotFoundError(self.source_type, data.get("message", "数据未找到"))
                                else:
                                    raise DataSourceError(self.source_type, data.get("message", f"API错误: {data['code']}"))
                            
                            if "status" in data and data["status"] == "error":
                                raise DataSourceError(self.source_type, data.get("message", "API请求失败"))
                        
                        return data
                    elif response.status == 429:
                        raise DataSourceError(self.source_type, "API频率限制")
                    elif response.status == 401:
                        raise DataSourceError(self.source_type, "API Key无效")
                    elif response.status == 404:
                        raise DataNotFoundError(self.source_type, "数据未找到")
                    else:
                        raise DataSourceError(self.source_type, f"HTTP错误: {response.status}")
        
        except asyncio.TimeoutError:
            raise DataSourceError(self.source_type, f"请求超时 ({self.timeout}秒)")
        except (DataSourceError, DataNotFoundError):
            raise
        except Exception as e:
            raise DataSourceError(self.source_type, str(e))
    
    async def get_stock_info(self, symbol: str, market: MarketType) -> Optional[Dict[str, Any]]:
        """获取股票基本信息"""
        if market not in [MarketType.US_STOCK, MarketType.HK_STOCK]:
            return None
        
        try:
            self.record_request()
            
            # 获取股票基本信息
            params = {
                'symbol': symbol.upper(),
                'exchange': self._get_exchange_for_market(market)
            }
            
            # 移除空值参数
            params = {k: v for k, v in params.items() if v}
            
            data = await self._make_request("profile", params)
            
            if not data:
                raise DataNotFoundError(self.source_type, f"股票信息未找到: {symbol}")
            
            # 转换为标准格式
            result = {
                "symbol": symbol.upper(),
                "name": data.get("name"),
                "market": "美股" if market == MarketType.US_STOCK else "港股",
                "exchange": data.get("exchange"),
                "currency": data.get("currency"),
                "country": data.get("country"),
                "sector": data.get("sector"),
                "industry": data.get("industry"),
                "website": data.get("website"),
                "description": data.get("description"),
                "employees": data.get("employees"),
                "market_cap": data.get("market_cap"),
                "source": self.source_type.value,
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except (DataSourceError, DataNotFoundError):
            raise
        except Exception as e:
            logger.error(f"❌ Twelve Data 获取股票信息失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, str(e))
    
    async def get_stock_data(self, symbol: str, market: MarketType, 
                           start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取股票历史数据"""
        if market not in [MarketType.US_STOCK, MarketType.HK_STOCK]:
            return None
        
        try:
            self.record_request()
            
            # 计算日期范围
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            # 构建请求参数
            params = {
                'symbol': symbol.upper(),
                'interval': '1day',
                'start_date': start_date,
                'end_date': end_date,
                'format': 'JSON'
            }
            
            # 添加交易所信息（如果需要）
            exchange = self._get_exchange_for_market(market)
            if exchange:
                params['exchange'] = exchange
            
            data = await self._make_request("time_series", params)
            
            if not data or "values" not in data:
                raise DataNotFoundError(self.source_type, f"历史数据未找到: {symbol}")
            
            values = data["values"]
            if not values:
                raise DataNotFoundError(self.source_type, f"历史数据为空: {symbol}")
            
            # 转换为标准格式
            result = []
            for record in values:
                formatted_record = {
                    "date": record.get("datetime"),
                    "open": self._safe_float(record.get("open")),
                    "high": self._safe_float(record.get("high")),
                    "low": self._safe_float(record.get("low")),
                    "close": self._safe_float(record.get("close")),
                    "volume": self._safe_int(record.get("volume")),
                    "symbol": symbol.upper(),
                    "source": self.source_type.value
                }
                result.append(formatted_record)
            
            # 按日期排序（Twelve Data通常返回倒序）
            result.sort(key=lambda x: x["date"])
            
            return result
            
        except (DataSourceError, DataNotFoundError):
            raise
        except Exception as e:
            logger.error(f"❌ Twelve Data 获取股票数据失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, str(e))
    
    async def get_real_time_quote(self, symbol: str, market: MarketType = MarketType.US_STOCK) -> Optional[Dict[str, Any]]:
        """获取实时报价"""
        try:
            self.record_request()
            
            # 构建请求参数
            params = {
                'symbol': symbol.upper()
            }
            
            # 添加交易所信息（如果需要）
            exchange = self._get_exchange_for_market(market)
            if exchange:
                params['exchange'] = exchange
            
            data = await self._make_request("quote", params)
            
            if not data:
                raise DataNotFoundError(self.source_type, f"实时报价未找到: {symbol}")
            
            result = {
                "symbol": symbol.upper(),
                "name": data.get("name"),
                "current_price": self._safe_float(data.get("close")),
                "change": self._safe_float(data.get("change")),
                "change_percent": self._safe_float(data.get("percent_change")),
                "open": self._safe_float(data.get("open")),
                "high": self._safe_float(data.get("high")),
                "low": self._safe_float(data.get("low")),
                "previous_close": self._safe_float(data.get("previous_close")),
                "volume": self._safe_int(data.get("volume")),
                "exchange": data.get("exchange"),
                "currency": data.get("currency"),
                "is_market_open": data.get("is_market_open"),
                "source": self.source_type.value,
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except (DataSourceError, DataNotFoundError):
            raise
        except Exception as e:
            logger.error(f"❌ Twelve Data 获取实时报价失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, str(e))
    
    def _get_exchange_for_market(self, market: MarketType) -> Optional[str]:
        """根据市场类型获取交易所代码"""
        if market == MarketType.US_STOCK:
            return None  # 美股通常不需要指定交易所
        elif market == MarketType.HK_STOCK:
            return "HKEX"  # 港交所
        else:
            return None
    
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
        """获取基本面数据 (Twelve Data暂不支持)"""
        # Twelve Data的基本面数据在profile中已包含
        return None

    async def get_news(self, symbol: str, market: MarketType,
                      start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取新闻数据 (Twelve Data暂不支持)"""
        # Twelve Data免费版不支持新闻数据
        return None

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 使用一个简单的查询测试API
            await self.get_real_time_quote("AAPL", MarketType.US_STOCK)
            return True
        except Exception:
            return False
