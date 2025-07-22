#!/usr/bin/env python3
"""
AKShare 数据源实现
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .base import (
    BaseDataSource, DataSourceConfig, DataSourceType, MarketType, 
    DataCategory, DataSourceError, DataNotFoundError
)

logger = logging.getLogger(__name__)

class AKShareDataSource(BaseDataSource):
    """AKShare 数据源"""

    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self._client = None
        # 设置默认超时时间（秒）
        self.timeout = getattr(config, 'timeout', 60)  # 默认60秒
        self._init_client()
    
    def _init_client(self):
        """初始化 AKShare 客户端"""
        try:
            import akshare as ak
            self._client = ak
            logger.info("✅ AKShare 客户端初始化成功")
        except ImportError:
            logger.error("❌ AKShare 库未安装")
        except Exception as e:
            logger.error(f"❌ AKShare 客户端初始化失败: {e}")

    async def _execute_with_timeout(self, func, *args, **kwargs):
        """带超时的异步执行AKShare函数"""
        try:
            # 在线程池中执行同步函数，避免阻塞事件循环
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, func, *args, **kwargs),
                timeout=self.timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"❌ AKShare 请求超时 ({self.timeout}秒): {func.__name__}")
            raise DataSourceError(self.source_type, f"请求超时 ({self.timeout}秒)")
        except Exception as e:
            logger.error(f"❌ AKShare 请求失败: {func.__name__} - {e}")
            raise DataSourceError(self.source_type, str(e))

    @property
    def supported_markets(self) -> List[MarketType]:
        return [MarketType.A_SHARE, MarketType.HK_STOCK, MarketType.US_STOCK]
    
    @property
    def supported_categories(self) -> List[DataCategory]:
        return [
            DataCategory.BASIC_INFO,
            DataCategory.PRICE_DATA,
            DataCategory.NEWS
        ]
    
    async def get_stock_info(self, symbol: str, market: MarketType) -> Optional[Dict[str, Any]]:
        """获取股票基本信息"""
        if not self._client:
            return None
        
        try:
            self.record_request()
            
            if market == MarketType.A_SHARE:
                # A股股票信息 - 使用超时执行
                df = await self._execute_with_timeout(
                    self._client.stock_individual_info_em,
                    symbol=symbol
                )
                if df.empty:
                    raise DataNotFoundError(self.source_type, f"A股信息未找到: {symbol}")
                
                # 转换为字典格式
                info_dict = {}
                for _, row in df.iterrows():
                    info_dict[row['item']] = row['value']
                
                result = {
                    "symbol": symbol,
                    "name": info_dict.get("股票简称"),
                    "market": "A股",
                    "industry": info_dict.get("所属行业"),
                    "area": info_dict.get("所属地域"),
                    "list_date": info_dict.get("上市时间"),
                    "total_share": info_dict.get("总股本"),
                    "float_share": info_dict.get("流通股本"),
                    "source": self.source_type.value,
                    "timestamp": datetime.now().isoformat()
                }
                
            elif market == MarketType.HK_STOCK:
                # 港股信息 - 使用超时执行
                df = await self._execute_with_timeout(self._client.stock_hk_spot_em)
                stock_info = df[df['代码'] == symbol]
                if stock_info.empty:
                    raise DataNotFoundError(self.source_type, f"港股信息未找到: {symbol}")
                
                info = stock_info.iloc[0]
                result = {
                    "symbol": symbol,
                    "name": info.get("名称"),
                    "market": "港股",
                    "current_price": float(info.get("最新价")) if info.get("最新价") else None,
                    "change": float(info.get("涨跌额")) if info.get("涨跌额") else None,
                    "change_pct": float(info.get("涨跌幅")) if info.get("涨跌幅") else None,
                    "source": self.source_type.value,
                    "timestamp": datetime.now().isoformat()
                }
                
            elif market == MarketType.US_STOCK:
                # 美股信息 - 使用超时执行
                df = await self._execute_with_timeout(self._client.stock_us_spot_em)
                stock_info = df[df['代码'] == symbol]
                if stock_info.empty:
                    raise DataNotFoundError(self.source_type, f"美股信息未找到: {symbol}")
                
                info = stock_info.iloc[0]
                result = {
                    "symbol": symbol,
                    "name": info.get("名称"),
                    "market": "美股",
                    "current_price": float(info.get("最新价")) if info.get("最新价") else None,
                    "change": float(info.get("涨跌额")) if info.get("涨跌额") else None,
                    "change_pct": float(info.get("涨跌幅")) if info.get("涨跌幅") else None,
                    "source": self.source_type.value,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return None
            
            self.reset_error_count()
            return result
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ AKShare 获取股票信息失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取股票信息失败: {e}", e)
    
    async def get_stock_data(self, symbol: str, market: MarketType, 
                           start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取股票价格数据"""
        if not self._client:
            return None
        
        try:
            self.record_request()
            
            if market == MarketType.A_SHARE:
                # A股历史数据
                df = self._client.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=start_date.replace("-", ""),
                    end_date=end_date.replace("-", ""),
                    adjust=""
                )
            elif market == MarketType.HK_STOCK:
                # 港股历史数据
                df = self._client.stock_hk_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=start_date.replace("-", ""),
                    end_date=end_date.replace("-", ""),
                    adjust="qfq"
                )
            elif market == MarketType.US_STOCK:
                # 美股历史数据
                df = self._client.stock_us_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=start_date.replace("-", ""),
                    end_date=end_date.replace("-", ""),
                    adjust=""
                )
            else:
                return None
            
            if df.empty:
                raise DataNotFoundError(self.source_type, f"股票数据未找到: {symbol}")
            
            # 转换为标准格式
            result = []
            for _, row in df.iterrows():
                date_str = row["日期"].strftime("%Y-%m-%d") if hasattr(row["日期"], 'strftime') else str(row["日期"])
                result.append({
                    "date": date_str,
                    "open": float(row["开盘"]) if row["开盘"] else None,
                    "high": float(row["最高"]) if row["最高"] else None,
                    "low": float(row["最低"]) if row["最低"] else None,
                    "close": float(row["收盘"]) if row["收盘"] else None,
                    "volume": int(row["成交量"]) if row["成交量"] else None,
                    "amount": float(row["成交额"]) if "成交额" in row and row["成交额"] else None,
                })
            
            # 按日期排序
            result.sort(key=lambda x: x["date"])
            
            self.reset_error_count()
            return result
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ AKShare 获取股票数据失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取股票数据失败: {e}", e)
    
    async def get_fundamentals(self, symbol: str, market: MarketType,
                             start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """获取基本面数据 - AKShare 基本面数据有限"""
        if not self._client or market != MarketType.A_SHARE:
            return None
        
        try:
            self.record_request()
            
            # 获取财务指标
            df = self._client.stock_financial_abstract_ths(symbol=symbol)
            if df.empty:
                raise DataNotFoundError(self.source_type, f"基本面数据未找到: {symbol}")
            
            # 转换为字典格式
            financial_dict = {}
            for _, row in df.iterrows():
                financial_dict[row['指标名称']] = row['指标数值']
            
            result = {
                "symbol": symbol,
                "pe_ratio": financial_dict.get("市盈率"),
                "pb_ratio": financial_dict.get("市净率"),
                "roe": financial_dict.get("净资产收益率"),
                "debt_ratio": financial_dict.get("资产负债率"),
                "gross_margin": financial_dict.get("毛利率"),
                "net_margin": financial_dict.get("净利率"),
                "source": self.source_type.value,
                "timestamp": datetime.now().isoformat()
            }
            
            self.reset_error_count()
            return result
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ AKShare 获取基本面数据失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取基本面数据失败: {e}", e)
    
    async def get_news(self, symbol: str, market: MarketType,
                      start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取新闻数据"""
        if not self._client:
            return None
        
        try:
            self.record_request()
            
            # 获取股票新闻
            df = self._client.stock_news_em(symbol=symbol)
            if df.empty:
                return []
            
            # 转换为标准格式
            result = []
            for _, row in df.iterrows():
                result.append({
                    "title": row.get("新闻标题"),
                    "content": row.get("新闻内容", ""),
                    "publish_time": row.get("发布时间"),
                    "source": row.get("新闻来源", "东方财富"),
                    "url": row.get("新闻链接"),
                    "timestamp": datetime.now().isoformat()
                })
            
            self.reset_error_count()
            return result[:20]  # 限制返回数量
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ AKShare 获取新闻数据失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取新闻数据失败: {e}", e)
    
    async def health_check(self) -> bool:
        """健康检查"""
        if not self._client:
            return False
        
        try:
            # 尝试获取一个简单的数据
            df = self._client.tool_trade_date_hist_sina()
            return not df.empty
        except Exception as e:
            logger.error(f"❌ AKShare 健康检查失败: {e}")
            self.status = DataSourceStatus.ERROR
            return False
