#!/usr/bin/env python3
"""
BaoStock 数据源实现
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .base import (
    BaseDataSource, DataSourceConfig, DataSourceType, MarketType, 
    DataCategory, DataSourceError, DataNotFoundError, DataSourceStatus
)

logger = logging.getLogger(__name__)

class BaoStockDataSource(BaseDataSource):
    """BaoStock 数据源"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self._client = None
        self._is_logged_in = False
        self._init_client()
    
    def _init_client(self):
        """初始化 BaoStock 客户端"""
        try:
            import baostock as bs
            self._client = bs
            logger.info("✅ BaoStock 客户端初始化成功")
        except ImportError:
            logger.error("❌ BaoStock 库未安装，请运行: pip install baostock")
        except Exception as e:
            logger.error(f"❌ BaoStock 客户端初始化失败: {e}")
    
    async def _ensure_login(self):
        """确保已登录 BaoStock"""
        if not self._client:
            raise DataSourceError(self.source_type, "BaoStock 客户端未初始化")
        
        if not self._is_logged_in:
            try:
                # BaoStock 登录
                lg = self._client.login()
                if lg.error_code != '0':
                    raise DataSourceError(self.source_type, f"BaoStock 登录失败: {lg.error_msg}")
                self._is_logged_in = True
                logger.info("✅ BaoStock 登录成功")
            except Exception as e:
                logger.error(f"❌ BaoStock 登录失败: {e}")
                raise DataSourceError(self.source_type, f"BaoStock 登录失败: {e}", e)
    
    async def _logout(self):
        """登出 BaoStock"""
        if self._client and self._is_logged_in:
            try:
                self._client.logout()
                self._is_logged_in = False
                logger.info("✅ BaoStock 登出成功")
            except Exception as e:
                logger.warning(f"⚠️ BaoStock 登出失败: {e}")
    
    @property
    def supported_markets(self) -> List[MarketType]:
        return [MarketType.A_SHARE]
    
    @property
    def supported_categories(self) -> List[DataCategory]:
        return [
            DataCategory.BASIC_INFO,
            DataCategory.PRICE_DATA
        ]
    
    async def get_stock_info(self, symbol: str, market: MarketType) -> Optional[Dict[str, Any]]:
        """获取股票基本信息"""
        if not self._client or market != MarketType.A_SHARE:
            return None
        
        try:
            await self._ensure_login()
            self.record_request()
            
            # 转换股票代码格式
            bs_symbol = self._convert_symbol(symbol)
            
            # 获取股票基本信息
            rs = self._client.query_stock_basic(code=bs_symbol)
            if rs.error_code != '0':
                raise DataNotFoundError(self.source_type, f"股票信息查询失败: {rs.error_msg}")
            
            # 转换结果
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                raise DataNotFoundError(self.source_type, f"股票信息未找到: {symbol}")
            
            # 取第一条记录
            stock_data = data_list[0]
            
            # 格式化返回数据
            result = {
                "symbol": symbol,
                "name": stock_data[1] if len(stock_data) > 1 else None,  # code_name
                "market": "A股",
                "industry": stock_data[4] if len(stock_data) > 4 else None,  # industry
                "area": stock_data[5] if len(stock_data) > 5 else None,  # area
                "list_date": stock_data[6] if len(stock_data) > 6 else None,  # ipoDate
                "outDate": stock_data[7] if len(stock_data) > 7 else None,  # outDate
                "type": stock_data[8] if len(stock_data) > 8 else None,  # type
                "status": stock_data[9] if len(stock_data) > 9 else None,  # status
                "source": self.source_type.value,
                "timestamp": datetime.now().isoformat()
            }
            
            self.reset_error_count()
            return result
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ BaoStock 获取股票信息失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取股票信息失败: {e}", e)
        finally:
            await self._logout()
    
    async def get_stock_data(self, symbol: str, market: MarketType, 
                           start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取股票价格数据"""
        if not self._client or market != MarketType.A_SHARE:
            return None
        
        try:
            await self._ensure_login()
            self.record_request()
            
            # 转换股票代码格式
            bs_symbol = self._convert_symbol(symbol)
            
            # 获取日K线数据
            rs = self._client.query_history_k_data_plus(
                bs_symbol,
                "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                start_date=start_date,
                end_date=end_date,
                frequency="d",  # 日线
                adjustflag="3"  # 不复权
            )
            
            if rs.error_code != '0':
                raise DataNotFoundError(self.source_type, f"股票数据查询失败: {rs.error_msg}")
            
            # 转换结果
            data_list = []
            while (rs.error_code == '0') & rs.next():
                row_data = rs.get_row_data()
                if len(row_data) >= 6:  # 确保有足够的数据
                    data_list.append({
                        "date": row_data[0],  # date
                        "open": float(row_data[2]) if row_data[2] and row_data[2] != '' else None,  # open
                        "high": float(row_data[3]) if row_data[3] and row_data[3] != '' else None,  # high
                        "low": float(row_data[4]) if row_data[4] and row_data[4] != '' else None,   # low
                        "close": float(row_data[5]) if row_data[5] and row_data[5] != '' else None, # close
                        "volume": int(float(row_data[7])) if row_data[7] and row_data[7] != '' else None,  # volume
                        "amount": float(row_data[8]) if row_data[8] and row_data[8] != '' else None,  # amount
                        "preclose": float(row_data[6]) if row_data[6] and row_data[6] != '' else None,  # preclose
                        "pct_change": float(row_data[12]) if len(row_data) > 12 and row_data[12] and row_data[12] != '' else None,  # pctChg
                        "turnover": float(row_data[10]) if len(row_data) > 10 and row_data[10] and row_data[10] != '' else None,  # turn
                    })
            
            if not data_list:
                raise DataNotFoundError(self.source_type, f"股票数据未找到: {symbol}")
            
            # 按日期排序
            data_list.sort(key=lambda x: x["date"])
            
            self.reset_error_count()
            return data_list
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ BaoStock 获取股票数据失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取股票数据失败: {e}", e)
        finally:
            await self._logout()
    
    async def get_fundamentals(self, symbol: str, market: MarketType,
                             start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """获取基本面数据 - BaoStock 基本面数据有限"""
        if not self._client or market != MarketType.A_SHARE:
            return None
        
        try:
            await self._ensure_login()
            self.record_request()
            
            # 转换股票代码格式
            bs_symbol = self._convert_symbol(symbol)
            
            # 获取季频盈利能力
            rs = self._client.query_profit_data(
                code=bs_symbol,
                year=datetime.now().year,
                quarter=4  # 年报数据
            )
            
            if rs.error_code != '0':
                logger.warning(f"⚠️ BaoStock 基本面数据查询失败: {rs.error_msg}")
                return None
            
            # 转换结果
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                return None
            
            # 取最新的数据
            latest_data = data_list[0]
            
            # 格式化返回数据（BaoStock 基本面数据字段有限）
            result = {
                "symbol": symbol,
                "year": latest_data[1] if len(latest_data) > 1 else None,
                "quarter": latest_data[2] if len(latest_data) > 2 else None,
                "roe": float(latest_data[3]) if len(latest_data) > 3 and latest_data[3] and latest_data[3] != '' else None,  # ROE
                "roa": float(latest_data[4]) if len(latest_data) > 4 and latest_data[4] and latest_data[4] != '' else None,  # ROA
                "gross_margin": float(latest_data[5]) if len(latest_data) > 5 and latest_data[5] and latest_data[5] != '' else None,  # 毛利率
                "net_margin": float(latest_data[6]) if len(latest_data) > 6 and latest_data[6] and latest_data[6] != '' else None,  # 净利率
                "source": self.source_type.value,
                "timestamp": datetime.now().isoformat()
            }
            
            self.reset_error_count()
            return result
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ BaoStock 获取基本面数据失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取基本面数据失败: {e}", e)
        finally:
            await self._logout()
    
    async def get_news(self, symbol: str, market: MarketType,
                      start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取新闻数据 - BaoStock 不支持新闻数据"""
        return None
    
    def _convert_symbol(self, symbol: str) -> str:
        """转换股票代码为 BaoStock 格式"""
        if "." in symbol:
            return symbol
        
        # A股代码转换
        if symbol.startswith("00") or symbol.startswith("30"):
            return f"sz.{symbol}"  # 深交所
        elif symbol.startswith("60") or symbol.startswith("68"):
            return f"sh.{symbol}"  # 上交所
        else:
            return symbol
    
    async def health_check(self) -> bool:
        """健康检查"""
        if not self._client:
            return False
        
        try:
            # 尝试登录和获取一个简单的数据
            await self._ensure_login()
            
            # 获取交易日历作为健康检查
            rs = self._client.query_trade_dates(start_date="2024-01-01", end_date="2024-01-02")
            is_healthy = rs.error_code == '0'
            
            await self._logout()
            return is_healthy
            
        except Exception as e:
            logger.error(f"❌ BaoStock 健康检查失败: {e}")
            self.status = DataSourceStatus.ERROR
            return False
    
    def __del__(self):
        """析构函数，确保登出"""
        if hasattr(self, '_client') and self._client and self._is_logged_in:
            try:
                self._client.logout()
            except:
                pass
