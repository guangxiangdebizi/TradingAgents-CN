#!/usr/bin/env python3
"""
股票工具类 - Backend独立版本
不依赖tradingagents目录的代码
"""

import re
from enum import Enum
from typing import Dict, Any, Optional


class StockMarket(Enum):
    """股票市场枚举"""
    US = "US"           # 美股
    CHINA = "CHINA"     # A股
    HK = "HK"           # 港股
    UNKNOWN = "UNKNOWN" # 未知


class StockUtils:
    """股票工具类"""
    
    @staticmethod
    def identify_stock_market(symbol: str) -> StockMarket:
        """
        识别股票代码属于哪个市场
        
        Args:
            symbol: 股票代码
            
        Returns:
            StockMarket: 市场类型
        """
        if not symbol:
            return StockMarket.UNKNOWN
            
        symbol = symbol.upper().strip()
        
        # 美股模式：1-5个大写字母
        if re.match(r'^[A-Z]{1,5}$', symbol):
            return StockMarket.US
            
        # A股模式：6位数字 或 6位数字.SH/SZ
        if re.match(r'^\d{6}$', symbol) or re.match(r'^\d{6}\.(SH|SZ)$', symbol):
            return StockMarket.CHINA
            
        # 港股模式：1-5位数字 或 数字.HK
        if re.match(r'^\d{1,5}$', symbol) or re.match(r'^\d{1,5}\.HK$', symbol):
            return StockMarket.HK
            
        return StockMarket.UNKNOWN
    
    @staticmethod
    def get_market_info(symbol: str) -> Dict[str, Any]:
        """
        获取股票市场信息
        
        Args:
            symbol: 股票代码
            
        Returns:
            Dict: 包含市场信息的字典
        """
        market = StockUtils.identify_stock_market(symbol)
        
        return {
            "symbol": symbol,
            "market": market.value,
            "is_us": market == StockMarket.US,
            "is_china": market == StockMarket.CHINA,
            "is_hk": market == StockMarket.HK,
            "is_unknown": market == StockMarket.UNKNOWN
        }
    
    @staticmethod
    def is_us_stock(symbol: str) -> bool:
        """判断是否为美股"""
        return StockUtils.identify_stock_market(symbol) == StockMarket.US
    
    @staticmethod
    def is_china_stock(symbol: str) -> bool:
        """判断是否为A股"""
        return StockUtils.identify_stock_market(symbol) == StockMarket.CHINA
    
    @staticmethod
    def is_hk_stock(symbol: str) -> bool:
        """判断是否为港股"""
        return StockUtils.identify_stock_market(symbol) == StockMarket.HK


def get_stock_data_by_market(symbol: str, start_date: str, end_date: str) -> str:
    """
    根据市场类型获取股票数据
    
    Args:
        symbol: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        str: 股票数据或错误信息
    """
    market_info = StockUtils.get_market_info(symbol)
    
    if market_info['is_us']:
        # 美股数据 - 这里应该调用美股数据源
        return f"美股数据获取功能开发中: {symbol} ({start_date} 到 {end_date})"
    elif market_info['is_china']:
        # A股数据 - 这里应该调用A股数据源
        return f"A股数据获取功能开发中: {symbol} ({start_date} 到 {end_date})"
    elif market_info['is_hk']:
        # 港股数据 - 这里应该调用港股数据源
        return f"港股数据获取功能开发中: {symbol} ({start_date} 到 {end_date})"
    else:
        return f"❌ 无法识别股票市场: {symbol}"


if __name__ == "__main__":
    # 测试代码
    test_symbols = ["AAPL", "000001", "000001.SZ", "700", "700.HK", "INVALID"]
    
    for symbol in test_symbols:
        market_info = StockUtils.get_market_info(symbol)
        print(f"{symbol}: {market_info}")
