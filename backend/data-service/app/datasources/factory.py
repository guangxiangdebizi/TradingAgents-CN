#!/usr/bin/env python3
"""
数据源工厂类 - 统一管理所有数据源
"""

import os
import logging
from typing import Dict, List, Optional, Any, Type
from datetime import datetime, timedelta
from .base import (
    BaseDataSource, DataSourceConfig, DataSourceType, MarketType,
    DataCategory, DataSourceStatus, DataSourceError
)
from .tushare_source import TushareDataSource
from .akshare_source import AKShareDataSource
from .finnhub_source import FinnHubDataSource
from .baostock_source import BaoStockDataSource
from .yfinance_source import YFinanceDataSource
from .alpha_vantage_source import AlphaVantageDataSource
from .twelve_data_source import TwelveDataSource
from .config import DataSourceConfigManager
from .priority_manager import get_priority_manager

logger = logging.getLogger(__name__)

class DataSourceFactory:
    """数据源工厂类"""
    
    # 注册的数据源类
    _source_classes: Dict[DataSourceType, Type[BaseDataSource]] = {
        DataSourceType.TUSHARE: TushareDataSource,
        DataSourceType.AKSHARE: AKShareDataSource,
        DataSourceType.FINNHUB: FinnHubDataSource,
        DataSourceType.BAOSTOCK: BaoStockDataSource,
        DataSourceType.YFINANCE: YFinanceDataSource,
        DataSourceType.ALPHA_VANTAGE: AlphaVantageDataSource,
        DataSourceType.TWELVE_DATA: TwelveDataSource,
    }
    
    def __init__(self):
        self._sources: Dict[DataSourceType, BaseDataSource] = {}
        self._priority_config = self._load_priority_config()
        self._init_sources()
    
    def _load_priority_config(self) -> Dict[str, List[DataSourceType]]:
        """加载数据源优先级配置"""
        priority_manager = get_priority_manager()
        return priority_manager.get_priority_config()
    
    def _init_sources(self):
        """初始化所有数据源"""
        # Tushare 配置
        tushare_config = DataSourceConfig(
            source_type=DataSourceType.TUSHARE,
            api_key=os.getenv("TUSHARE_TOKEN"),
            rate_limit=200,  # 每分钟200次
            timeout=60  # 增加到60秒
        )
        
        # AKShare 配置
        akshare_config = DataSourceConfig(
            source_type=DataSourceType.AKSHARE,
            rate_limit=100,  # 每分钟100次
            timeout=120  # 增加到120秒，因为AKShare有时响应较慢
        )

        # FinnHub 配置
        finnhub_config = DataSourceConfig(
            source_type=DataSourceType.FINNHUB,
            api_key=os.getenv("FINNHUB_API_KEY"),
            rate_limit=60,   # 每分钟60次
            timeout=60  # 增加到60秒
        )

        # BaoStock 配置
        baostock_config = DataSourceConfig(
            source_type=DataSourceType.BAOSTOCK,
            rate_limit=60,   # 每分钟60次
            timeout=90  # 增加到90秒
        )

        # YFinance 配置
        yfinance_config = DataSourceConfig(
            source_type=DataSourceType.YFINANCE,
            rate_limit=30,   # 每分钟30次（限制较严）
            timeout=90  # 增加到90秒，因为YFinance有时很慢
        )

        # Alpha Vantage 配置
        alpha_vantage_config = DataSourceConfig(
            source_type=DataSourceType.ALPHA_VANTAGE,
            api_key=os.getenv("ALPHA_VANTAGE_API_KEY"),
            rate_limit=5,    # 每分钟5次（免费版限制）
            timeout=60
        )

        # Twelve Data 配置
        twelve_data_config = DataSourceConfig(
            source_type=DataSourceType.TWELVE_DATA,
            api_key=os.getenv("TWELVE_DATA_API_KEY"),
            rate_limit=8,    # 免费版每分钟8次请求
            timeout=60
        )

        # 初始化数据源实例
        configs = {
            DataSourceType.TUSHARE: tushare_config,
            DataSourceType.AKSHARE: akshare_config,
            DataSourceType.FINNHUB: finnhub_config,
            DataSourceType.BAOSTOCK: baostock_config,
            DataSourceType.YFINANCE: yfinance_config,
            DataSourceType.ALPHA_VANTAGE: alpha_vantage_config,
            DataSourceType.TWELVE_DATA: twelve_data_config,
        }
        
        for source_type, config in configs.items():
            try:
                source_class = self._source_classes.get(source_type)
                if source_class:
                    source = source_class(config)
                    self._sources[source_type] = source
                    logger.info(f"✅ 数据源初始化成功: {source_type.value}")
            except Exception as e:
                logger.error(f"❌ 数据源初始化失败 {source_type.value}: {e}")
    
    def get_data_source(self, source_type: DataSourceType) -> Optional[BaseDataSource]:
        """获取指定类型的数据源"""
        return self._sources.get(source_type)

    def get_available_sources(self, market: MarketType, category: DataCategory) -> List[BaseDataSource]:
        """获取可用的数据源列表（按优先级排序）"""
        priority_key = f"{market.value}_{category.value}"
        priority_list = self._priority_config.get(priority_key, [])

        available_sources = []
        for source_type in priority_list:
            source = self._sources.get(source_type)
            if source and source.can_handle(market, category) and source.status == DataSourceStatus.AVAILABLE:
                available_sources.append(source)

        return available_sources
    
    async def get_stock_info(self, symbol: str, market: MarketType) -> Optional[Dict[str, Any]]:
        """获取股票基本信息"""
        sources = self.get_available_sources(market, DataCategory.BASIC_INFO)
        
        for source in sources:
            try:
                logger.info(f"🔍 尝试数据源 {source.source_type.value} 获取股票信息: {symbol}")
                result = await source.get_stock_info(symbol, market)
                if result:
                    logger.info(f"✅ 数据源 {source.source_type.value} 获取成功")
                    return result
            except Exception as e:
                logger.warning(f"⚠️ 数据源 {source.source_type.value} 获取失败: {e}")
                continue
        
        logger.error(f"❌ 所有数据源都无法获取股票信息: {symbol}")
        return None
    
    async def get_stock_data(self, symbol: str, market: MarketType, 
                           start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取股票价格数据"""
        sources = self.get_available_sources(market, DataCategory.PRICE_DATA)
        
        for source in sources:
            try:
                logger.info(f"🔍 尝试数据源 {source.source_type.value} 获取股票数据: {symbol}")
                result = await source.get_stock_data(symbol, market, start_date, end_date)
                if result:
                    logger.info(f"✅ 数据源 {source.source_type.value} 获取成功，数据量: {len(result)}")
                    return result
            except Exception as e:
                logger.warning(f"⚠️ 数据源 {source.source_type.value} 获取失败: {e}")
                continue
        
        logger.error(f"❌ 所有数据源都无法获取股票数据: {symbol}")
        return None
    
    async def get_fundamentals(self, symbol: str, market: MarketType,
                             start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """获取基本面数据"""
        sources = self.get_available_sources(market, DataCategory.FUNDAMENTALS)
        
        for source in sources:
            try:
                logger.info(f"🔍 尝试数据源 {source.source_type.value} 获取基本面数据: {symbol}")
                result = await source.get_fundamentals(symbol, market, start_date, end_date)
                if result:
                    logger.info(f"✅ 数据源 {source.source_type.value} 获取成功")
                    return result
            except Exception as e:
                logger.warning(f"⚠️ 数据源 {source.source_type.value} 获取失败: {e}")
                continue
        
        logger.error(f"❌ 所有数据源都无法获取基本面数据: {symbol}")
        return None
    
    async def get_news(self, symbol: str, market: MarketType,
                      start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取新闻数据"""
        sources = self.get_available_sources(market, DataCategory.NEWS)
        
        for source in sources:
            try:
                logger.info(f"🔍 尝试数据源 {source.source_type.value} 获取新闻数据: {symbol}")
                result = await source.get_news(symbol, market, start_date, end_date)
                if result:
                    logger.info(f"✅ 数据源 {source.source_type.value} 获取成功，新闻数量: {len(result)}")
                    return result
            except Exception as e:
                logger.warning(f"⚠️ 数据源 {source.source_type.value} 获取失败: {e}")
                continue
        
        logger.error(f"❌ 所有数据源都无法获取新闻数据: {symbol}")
        return None
    
    async def health_check_all(self) -> Dict[str, Any]:
        """检查所有数据源健康状态"""
        health_status = {}
        
        for source_type, source in self._sources.items():
            try:
                is_healthy = await source.health_check()
                health_status[source_type.value] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "stats": source.get_stats()
                }
            except Exception as e:
                health_status[source_type.value] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return health_status
    
    def get_source_stats(self) -> Dict[str, Any]:
        """获取所有数据源统计信息"""
        stats = {}
        for source_type, source in self._sources.items():
            stats[source_type.value] = source.get_stats()
        return stats

    def reload_priority_config(self) -> bool:
        """重新加载优先级配置"""
        try:
            priority_manager = get_priority_manager()
            priority_manager.load_config()
            self._priority_config = self._load_priority_config()
            logger.info("✅ 优先级配置重新加载成功")
            return True
        except Exception as e:
            logger.error(f"❌ 重新加载优先级配置失败: {e}")
            return False

    def get_current_priority_profile(self) -> str:
        """获取当前使用的优先级配置文件"""
        priority_manager = get_priority_manager()
        return priority_manager.get_current_profile()

    def set_priority_profile(self, profile_name: str) -> bool:
        """设置优先级配置文件"""
        try:
            priority_manager = get_priority_manager()
            if priority_manager.set_current_profile(profile_name):
                self._priority_config = self._load_priority_config()
                logger.info(f"✅ 切换到优先级配置: {profile_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 设置优先级配置失败: {e}")
            return False

    def get_available_priority_profiles(self) -> Dict[str, Any]:
        """获取所有可用的优先级配置文件"""
        priority_manager = get_priority_manager()
        return priority_manager.get_available_profiles()

    def set_custom_priority(self, market: MarketType, category: DataCategory,
                          sources: List[str]) -> bool:
        """设置自定义优先级"""
        try:
            priority_manager = get_priority_manager()
            if priority_manager.set_priority_for_category(market, category, sources):
                self._priority_config = self._load_priority_config()
                logger.info(f"✅ 设置自定义优先级: {market.value}_{category.value}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 设置自定义优先级失败: {e}")
            return False
    
    def detect_market_type(self, symbol: str) -> MarketType:
        """根据股票代码检测市场类型"""
        symbol = symbol.upper().strip()
        
        # A股判断
        if (symbol.isdigit() and len(symbol) == 6):
            return MarketType.A_SHARE
        
        # 港股判断
        if symbol.isdigit() and len(symbol) == 5:
            return MarketType.HK_STOCK
        
        # 美股判断（字母开头）
        if symbol.isalpha():
            return MarketType.US_STOCK
        
        # 默认返回A股
        return MarketType.A_SHARE
    
    @classmethod
    def register_source(cls, source_type: DataSourceType, source_class: Type[BaseDataSource]):
        """注册新的数据源类"""
        cls._source_classes[source_type] = source_class
        logger.info(f"✅ 注册数据源类: {source_type.value}")


# 全局数据源工厂实例
_factory_instance: Optional[DataSourceFactory] = None

def get_data_source_factory() -> DataSourceFactory:
    """获取数据源工厂实例（单例模式）"""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = DataSourceFactory()
    return _factory_instance

def init_data_source_factory() -> DataSourceFactory:
    """初始化数据源工厂"""
    global _factory_instance
    _factory_instance = DataSourceFactory()
    logger.info("✅ 数据源工厂初始化完成")
    return _factory_instance
