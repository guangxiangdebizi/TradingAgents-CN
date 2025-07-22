"""
数据服务客户端
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, date
from .base import BaseServiceClient
from ..utils.logger import get_service_logger

logger = get_service_logger("data-client")


class DataClient(BaseServiceClient):
    """数据服务客户端"""
    
    def __init__(self, base_url: Optional[str] = None):
        super().__init__("data-service", base_url)
    
    async def get_stock_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "1d",
        **kwargs
    ) -> Dict[str, Any]:
        """
        获取股票数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 数据周期
            **kwargs: 其他参数
        
        Returns:
            股票数据
        """
        try:
            params = {
                "symbol": symbol,
                "period": period,
                **kwargs
            }
            
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            
            self.logger.debug(f"Getting stock data: {symbol}")
            response = await self.get("/api/v1/stock/data", params)
            
            self.logger.debug(f"Stock data response: {response.get('success', False)}")
            return response
            
        except Exception as e:
            self.logger.error(f"Get stock data failed: {e}")
            raise
    
    async def get_market_data(
        self,
        market: str = "A",
        data_type: str = "basic",
        **kwargs
    ) -> Dict[str, Any]:
        """
        获取市场数据
        
        Args:
            market: 市场类型 (A, HK, US)
            data_type: 数据类型
            **kwargs: 其他参数
        
        Returns:
            市场数据
        """
        try:
            params = {
                "market": market,
                "data_type": data_type,
                **kwargs
            }
            
            self.logger.debug(f"Getting market data: {market}")
            response = await self.get("/api/v1/market/data", params)
            
            self.logger.debug(f"Market data response: {response.get('success', False)}")
            return response
            
        except Exception as e:
            self.logger.error(f"Get market data failed: {e}")
            raise
    
    async def get_financial_data(
        self,
        symbol: str,
        report_type: str = "annual",
        **kwargs
    ) -> Dict[str, Any]:
        """
        获取财务数据
        
        Args:
            symbol: 股票代码
            report_type: 报告类型
            **kwargs: 其他参数
        
        Returns:
            财务数据
        """
        try:
            params = {
                "symbol": symbol,
                "report_type": report_type,
                **kwargs
            }
            
            self.logger.debug(f"Getting financial data: {symbol}")
            response = await self.get("/api/v1/financial/data", params)
            
            self.logger.debug(f"Financial data response: {response.get('success', False)}")
            return response
            
        except Exception as e:
            self.logger.error(f"Get financial data failed: {e}")
            raise
    
    async def get_news_data(
        self,
        symbol: Optional[str] = None,
        category: str = "all",
        limit: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        获取新闻数据
        
        Args:
            symbol: 股票代码（可选）
            category: 新闻类别
            limit: 数量限制
            **kwargs: 其他参数
        
        Returns:
            新闻数据
        """
        try:
            params = {
                "category": category,
                "limit": limit,
                **kwargs
            }
            
            if symbol:
                params["symbol"] = symbol
            
            self.logger.debug(f"Getting news data: {symbol or 'all'}")
            response = await self.get("/api/v1/news/data", params)
            
            self.logger.debug(f"News data response: {response.get('success', False)}")
            return response
            
        except Exception as e:
            self.logger.error(f"Get news data failed: {e}")
            raise
    
    async def search_stocks(
        self,
        query: str,
        market: str = "A",
        limit: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        搜索股票
        
        Args:
            query: 搜索关键词
            market: 市场类型
            limit: 数量限制
            **kwargs: 其他参数
        
        Returns:
            搜索结果
        """
        try:
            params = {
                "query": query,
                "market": market,
                "limit": limit,
                **kwargs
            }
            
            self.logger.debug(f"Searching stocks: {query}")
            response = await self.get("/api/v1/stocks/search", params)
            
            self.logger.debug(f"Stock search response: {response.get('success', False)}")
            return response
            
        except Exception as e:
            self.logger.error(f"Stock search failed: {e}")
            raise


# 全局数据客户端实例
_data_client: Optional[DataClient] = None


def get_data_client(base_url: Optional[str] = None) -> DataClient:
    """
    获取数据客户端实例
    
    Args:
        base_url: 数据服务的基础URL
    
    Returns:
        数据客户端实例
    """
    global _data_client
    
    if _data_client is None:
        _data_client = DataClient(base_url)
    
    return _data_client


async def close_data_client():
    """关闭数据客户端"""
    global _data_client
    
    if _data_client:
        await _data_client.close()
        _data_client = None
