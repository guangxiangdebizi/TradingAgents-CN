"""
数据工具
提供股票数据获取功能
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import aiohttp
import pandas as pd

logger = logging.getLogger(__name__)

class DataTools:
    """数据工具类"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.data_service_url = "http://localhost:8003"  # Data Service URL
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5分钟缓存
    
    async def initialize(self):
        """初始化数据工具"""
        try:
            logger.info("📊 初始化数据工具...")
            
            # 创建HTTP会话
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # 测试数据服务连接
            await self._test_data_service()
            
            logger.info("✅ 数据工具初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 数据工具初始化失败: {e}")
            raise
    
    async def _test_data_service(self):
        """测试数据服务连接"""
        try:
            if self.session:
                async with self.session.get(f"{self.data_service_url}/health") as response:
                    if response.status == 200:
                        logger.info("✅ 数据服务连接正常")
                    else:
                        logger.warning(f"⚠️ 数据服务响应异常: {response.status}")
        except Exception as e:
            logger.warning(f"⚠️ 数据服务连接失败: {e}")
    
    def _get_cache_key(self, method: str, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [method]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        return ":".join(key_parts)
    
    def _is_cache_valid(self, cache_time: datetime) -> bool:
        """检查缓存是否有效"""
        return (datetime.now() - cache_time).total_seconds() < self.cache_ttl
    
    async def get_stock_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """获取股票基础数据"""
        cache_key = self._get_cache_key("stock_data", symbol=symbol, period=period)
        
        # 检查缓存
        if cache_key in self.cache:
            cache_data, cache_time = self.cache[cache_key]
            if self._is_cache_valid(cache_time):
                logger.debug(f"📋 使用缓存数据: {symbol}")
                return cache_data
        
        try:
            logger.info(f"📈 获取股票数据: {symbol}")
            
            if self.session:
                # 调用数据服务API
                params = {"symbol": symbol, "period": period}
                async with self.session.get(
                    f"{self.data_service_url}/api/v1/stock/data",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 缓存结果
                        self.cache[cache_key] = (data, datetime.now())
                        
                        return data
                    else:
                        error_text = await response.text()
                        raise Exception(f"数据服务错误: {response.status} - {error_text}")
            else:
                # 模拟数据（当数据服务不可用时）
                return await self._get_mock_stock_data(symbol, period)
                
        except Exception as e:
            logger.error(f"❌ 获取股票数据失败: {symbol} - {e}")
            # 返回模拟数据作为降级处理
            return await self._get_mock_stock_data(symbol, period)
    
    async def get_financial_data(self, symbol: str, statement_type: str = "income") -> Dict[str, Any]:
        """获取财务数据"""
        cache_key = self._get_cache_key("financial_data", symbol=symbol, statement_type=statement_type)
        
        # 检查缓存
        if cache_key in self.cache:
            cache_data, cache_time = self.cache[cache_key]
            if self._is_cache_valid(cache_time):
                logger.debug(f"📋 使用缓存财务数据: {symbol}")
                return cache_data
        
        try:
            logger.info(f"💰 获取财务数据: {symbol} - {statement_type}")
            
            if self.session:
                # 调用数据服务API
                params = {"symbol": symbol, "statement_type": statement_type}
                async with self.session.get(
                    f"{self.data_service_url}/api/v1/stock/financial",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 缓存结果
                        self.cache[cache_key] = (data, datetime.now())
                        
                        return data
                    else:
                        error_text = await response.text()
                        raise Exception(f"数据服务错误: {response.status} - {error_text}")
            else:
                # 模拟数据
                return await self._get_mock_financial_data(symbol, statement_type)
                
        except Exception as e:
            logger.error(f"❌ 获取财务数据失败: {symbol} - {e}")
            return await self._get_mock_financial_data(symbol, statement_type)
    
    async def get_market_data(self, symbol: str, indicators: List[str] = None) -> Dict[str, Any]:
        """获取市场数据"""
        if indicators is None:
            indicators = ["price", "volume", "market_cap"]
        
        cache_key = self._get_cache_key("market_data", symbol=symbol, indicators=",".join(indicators))
        
        # 检查缓存
        if cache_key in self.cache:
            cache_data, cache_time = self.cache[cache_key]
            if self._is_cache_valid(cache_time):
                logger.debug(f"📋 使用缓存市场数据: {symbol}")
                return cache_data
        
        try:
            logger.info(f"📊 获取市场数据: {symbol}")
            
            if self.session:
                # 调用数据服务API
                params = {"symbol": symbol, "indicators": ",".join(indicators)}
                async with self.session.get(
                    f"{self.data_service_url}/api/v1/stock/market",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 缓存结果
                        self.cache[cache_key] = (data, datetime.now())
                        
                        return data
                    else:
                        error_text = await response.text()
                        raise Exception(f"数据服务错误: {response.status} - {error_text}")
            else:
                # 模拟数据
                return await self._get_mock_market_data(symbol, indicators)
                
        except Exception as e:
            logger.error(f"❌ 获取市场数据失败: {symbol} - {e}")
            return await self._get_mock_market_data(symbol, indicators)
    
    async def _get_mock_stock_data(self, symbol: str, period: str) -> Dict[str, Any]:
        """获取模拟股票数据"""
        return {
            "success": True,
            "symbol": symbol,
            "period": period,
            "data": {
                "current_price": 150.00,
                "previous_close": 148.50,
                "change": 1.50,
                "change_percent": 1.01,
                "volume": 1000000,
                "market_cap": 2500000000,
                "pe_ratio": 25.5,
                "pb_ratio": 3.2,
                "dividend_yield": 2.1
            },
            "timestamp": datetime.now().isoformat(),
            "source": "mock"
        }
    
    async def _get_mock_financial_data(self, symbol: str, statement_type: str) -> Dict[str, Any]:
        """获取模拟财务数据"""
        return {
            "success": True,
            "symbol": symbol,
            "statement_type": statement_type,
            "data": {
                "revenue": 50000000000,
                "net_income": 5000000000,
                "total_assets": 100000000000,
                "total_debt": 30000000000,
                "shareholders_equity": 70000000000,
                "operating_cash_flow": 8000000000,
                "free_cash_flow": 6000000000
            },
            "timestamp": datetime.now().isoformat(),
            "source": "mock"
        }
    
    async def _get_mock_market_data(self, symbol: str, indicators: List[str]) -> Dict[str, Any]:
        """获取模拟市场数据"""
        return {
            "success": True,
            "symbol": symbol,
            "indicators": indicators,
            "data": {
                "price": 150.00,
                "volume": 1000000,
                "market_cap": 2500000000,
                "beta": 1.2,
                "volatility": 0.25,
                "rsi": 65.5,
                "macd": 2.1,
                "moving_average_50": 145.0,
                "moving_average_200": 140.0
            },
            "timestamp": datetime.now().isoformat(),
            "source": "mock"
        }
    
    async def reload(self):
        """重新加载数据工具"""
        logger.info("🔄 重新加载数据工具...")
        
        # 清空缓存
        self.cache.clear()
        
        # 重新测试连接
        await self._test_data_service()
        
        logger.info("✅ 数据工具重新加载完成")
    
    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理数据工具资源...")
        
        if self.session:
            await self.session.close()
            self.session = None
        
        self.cache.clear()
        
        logger.info("✅ 数据工具资源清理完成")
