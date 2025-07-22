#!/usr/bin/env python3
"""
数据源基类和接口定义
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class DataSourceType(Enum):
    """数据源类型"""
    TUSHARE = "tushare"
    AKSHARE = "akshare"
    BAOSTOCK = "baostock"
    YFINANCE = "yfinance"
    FINNHUB = "finnhub"
    ALPHA_VANTAGE = "alpha_vantage"
    TWELVE_DATA = "twelve_data"

class MarketType(Enum):
    """市场类型"""
    A_SHARE = "a_share"      # A股
    US_STOCK = "us_stock"    # 美股
    HK_STOCK = "hk_stock"    # 港股
    CRYPTO = "crypto"        # 加密货币

class DataCategory(Enum):
    """数据类别"""
    BASIC_INFO = "basic_info"        # 基本信息
    PRICE_DATA = "price_data"        # 价格数据
    FUNDAMENTALS = "fundamentals"    # 基本面数据
    NEWS = "news"                    # 新闻数据
    TECHNICAL_INDICATORS = "technical_indicators"  # 技术指标
    TECHNICAL = "technical"          # 技术指标
    SENTIMENT = "sentiment"          # 情感数据

class DataSourceStatus(Enum):
    """数据源状态"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"

class DataSourceConfig:
    """数据源配置"""
    
    def __init__(self, 
                 source_type: DataSourceType,
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 rate_limit: int = 100,  # 每分钟请求数
                 timeout: int = 30,
                 retry_count: int = 3,
                 retry_delay: int = 1,
                 **kwargs):
        self.source_type = source_type
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.extra_config = kwargs

class BaseDataSource(ABC):
    """数据源基类"""
    
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.source_type = config.source_type
        self.status = DataSourceStatus.AVAILABLE
        self.last_request_time = None
        self.request_count = 0
        self.error_count = 0
        
    @property
    @abstractmethod
    def supported_markets(self) -> List[MarketType]:
        """支持的市场类型"""
        pass
    
    @property
    @abstractmethod
    def supported_categories(self) -> List[DataCategory]:
        """支持的数据类别"""
        pass
    
    @abstractmethod
    async def get_stock_info(self, symbol: str, market: MarketType) -> Optional[Dict[str, Any]]:
        """获取股票基本信息"""
        pass
    
    @abstractmethod
    async def get_stock_data(self, symbol: str, market: MarketType, 
                           start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取股票价格数据"""
        pass
    
    @abstractmethod
    async def get_fundamentals(self, symbol: str, market: MarketType,
                             start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """获取基本面数据"""
        pass
    
    @abstractmethod
    async def get_news(self, symbol: str, market: MarketType,
                      start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取新闻数据"""
        pass
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 子类可以重写此方法实现具体的健康检查
            return self.status == DataSourceStatus.AVAILABLE
        except Exception as e:
            logger.error(f"数据源健康检查失败 {self.source_type.value}: {e}")
            self.status = DataSourceStatus.ERROR
            return False
    
    def can_handle(self, market: MarketType, category: DataCategory) -> bool:
        """检查是否能处理指定市场和数据类别"""
        return (market in self.supported_markets and 
                category in self.supported_categories)
    
    def update_status(self, status: DataSourceStatus):
        """更新数据源状态"""
        self.status = status
        logger.info(f"数据源状态更新 {self.source_type.value}: {status.value}")
    
    def record_request(self):
        """记录请求"""
        self.last_request_time = datetime.now()
        self.request_count += 1
    
    def record_error(self):
        """记录错误"""
        self.error_count += 1
        if self.error_count > 5:  # 连续5次错误则标记为不可用
            self.status = DataSourceStatus.ERROR
    
    def reset_error_count(self):
        """重置错误计数"""
        self.error_count = 0
        if self.status == DataSourceStatus.ERROR:
            self.status = DataSourceStatus.AVAILABLE
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "source_type": self.source_type.value,
            "status": self.status.value,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "last_request_time": self.last_request_time.isoformat() if self.last_request_time else None,
            "supported_markets": [m.value for m in self.supported_markets],
            "supported_categories": [c.value for c in self.supported_categories]
        }

class DataSourceError(Exception):
    """数据源异常"""
    
    def __init__(self, source_type: DataSourceType, message: str, original_error: Exception = None):
        self.source_type = source_type
        self.message = message
        self.original_error = original_error
        super().__init__(f"[{source_type.value}] {message}")

class RateLimitError(DataSourceError):
    """频率限制异常"""
    pass

class DataNotFoundError(DataSourceError):
    """数据未找到异常"""
    pass

class AuthenticationError(DataSourceError):
    """认证异常"""
    pass
