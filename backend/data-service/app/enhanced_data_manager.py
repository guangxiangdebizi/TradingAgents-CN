#!/usr/bin/env python3
"""
增强的数据管理器 - 集成TradingAgents的优秀实现
"""

import os
import time
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import asyncio

# 导入现有的数据管理器
from .data_manager import DataManager, DataType, CachedData
from .datasources.factory import init_data_source_factory
from .datasources.base import MarketType, DataCategory

# 导入国际化日志
from backend.shared.i18n.logger import get_i18n_logger

class EnhancedDataManager(DataManager):
    """
    增强的数据管理器
    集成TradingAgents的优秀实现：智能缓存、优雅格式化、智能降级
    """
    
    def __init__(self, mongodb_client=None, redis_client=None, language=None):
        super().__init__(mongodb_client, redis_client, language)
        
        # 增强功能初始化
        self.enhanced_cache_dir = Path("data/enhanced_cache")
        self.enhanced_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建分类缓存目录
        self.us_stock_cache = self.enhanced_cache_dir / "us_stocks"
        self.china_stock_cache = self.enhanced_cache_dir / "china_stocks"
        self.hk_stock_cache = self.enhanced_cache_dir / "hk_stocks"
        
        for cache_dir in [self.us_stock_cache, self.china_stock_cache, self.hk_stock_cache]:
            cache_dir.mkdir(exist_ok=True)
        
        # 数据源工厂
        from .datasources.factory import get_data_source_factory
        self.data_source_factory = get_data_source_factory()
        
        # 增强日志器
        self.enhanced_logger = get_i18n_logger("enhanced-data-manager", language)
        
        self.enhanced_logger.info("log.data_manager.enhanced_initialized")
    
    def _generate_enhanced_cache_key(self, symbol: str, data_type: str, 
                                   start_date: str, end_date: str, 
                                   market_type: str = "us") -> str:
        """生成增强缓存键"""
        key_data = f"{symbol}_{data_type}_{start_date}_{end_date}_{market_type}"
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    def _get_enhanced_cache_path(self, symbol: str, market_type: str) -> Path:
        """获取增强缓存路径"""
        if market_type == "us":
            return self.us_stock_cache
        elif market_type == "china":
            return self.china_stock_cache
        elif market_type == "hk":
            return self.hk_stock_cache
        else:
            return self.enhanced_cache_dir
    
    async def get_enhanced_stock_data(self, symbol: str, start_date: str, end_date: str,
                                    force_refresh: bool = False) -> Dict[str, Any]:
        """
        获取增强的股票数据 - 集成TradingAgents的优秀实现
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            force_refresh: 是否强制刷新
            
        Returns:
            包含格式化数据和元数据的字典
        """
        start_time = time.time()
        
        # 检测市场类型
        market_type = self._detect_market_type(symbol)
        self.enhanced_logger.debug_data_source_select(f"market_detection", symbol)
        
        # 生成缓存键
        cache_key = self._generate_enhanced_cache_key(symbol, "stock_data", start_date, end_date, market_type)
        cache_path = self._get_enhanced_cache_path(symbol, market_type)
        cache_file = cache_path / f"{cache_key}.json"
        
        # 检查缓存（除非强制刷新）
        if not force_refresh and cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                
                # 检查缓存是否过期（1小时）
                cache_time = datetime.fromisoformat(cached_data.get('timestamp', ''))
                if datetime.now() - cache_time < timedelta(hours=1):
                    self.enhanced_logger.cache_hit(symbol, "enhanced_stock_data")
                    duration = int((time.time() - start_time) * 1000)
                    self.enhanced_logger.request_completed(symbol, duration)
                    return cached_data
                else:
                    self.enhanced_logger.cache_expired(symbol, "enhanced_stock_data")
            except Exception as e:
                self.enhanced_logger.debug("log.debug.data.cache_read_error", error=str(e))
        
        self.enhanced_logger.cache_miss(symbol, "enhanced_stock_data")
        
        # 从数据源获取数据
        try:
            if market_type == "us":
                result = await self._get_enhanced_us_stock_data(symbol, start_date, end_date)
            elif market_type == "china":
                result = await self._get_enhanced_china_stock_data(symbol, start_date, end_date)
            elif market_type == "hk":
                result = await self._get_enhanced_hk_stock_data(symbol, start_date, end_date)
            else:
                raise ValueError(f"Unsupported market type: {market_type}")
            
            # 保存到增强缓存
            result['timestamp'] = datetime.now().isoformat()
            result['cache_key'] = cache_key
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            self.enhanced_logger.cache_updated(symbol, "enhanced_stock_data")
            
            duration = int((time.time() - start_time) * 1000)
            self.enhanced_logger.request_completed(symbol, duration)
            
            return result
            
        except Exception as e:
            self.enhanced_logger.request_failed(symbol, str(e))
            raise
    
    async def _get_enhanced_us_stock_data(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取增强的美股数据 - 使用数据源工厂的智能优先级"""
        self.enhanced_logger.debug_data_source_select("enhanced_us_pipeline", symbol)

        # 使用数据源工厂的智能优先级获取股票信息
        try:
            # 获取股票基本信息（会自动使用最高优先级的可用数据源）
            stock_info = await self.data_source_factory.get_stock_info(symbol, MarketType.US_STOCK)

            if stock_info:
                # 从返回的数据中获取实际使用的数据源
                actual_data_source = stock_info.get('source', 'unknown')

                # 尝试获取历史数据
                stock_data = None
                try:
                    stock_data = await self.data_source_factory.get_stock_data(symbol, MarketType.US_STOCK, start_date, end_date)
                except Exception as e:
                    self.enhanced_logger.debug("log.debug.data.history_error", error=str(e))

                # 格式化为TradingAgents风格的输出
                formatted_data = self._format_us_stock_data_tradingagents_style(
                    symbol, stock_info, start_date, end_date, actual_data_source, stock_data
                )

                self.enhanced_logger.data_fetched(symbol, actual_data_source)
                return {
                    "success": True,
                    "symbol": symbol,
                    "market_type": "us",
                    "data_source": actual_data_source,
                    "stock_info": stock_info,
                    "historical_data": stock_data or [],
                    "formatted_data": formatted_data,
                    "raw_data": {"info": stock_info, "history": stock_data},
                    "start_date": start_date,
                    "end_date": end_date
                }
            else:
                raise Exception("No stock info available from any data source")

        except Exception as e:
            self.enhanced_logger.debug("log.debug.data.all_sources_failed", error=str(e))
            raise Exception(f"All US stock data sources failed: {str(e)}")
        except Exception as e:
            self.enhanced_logger.debug("log.debug.data.yfinance_error", error=str(e))

        # 优先级3: AKShare备用 (如果前面的数据源都失败)
        try:
            self.enhanced_logger.debug_data_source_call("akshare", f"us_stock/{symbol}")
            # 注意：这里可能需要特殊处理，因为AKShare的美股支持有限
            # 暂时跳过AKShare美股，因为测试显示有问题
            self.enhanced_logger.debug("log.debug.data.akshare_us_skipped", reason="known_issues")
        except Exception as e:
            self.enhanced_logger.debug("log.debug.data.akshare_error", error=str(e))
        except Exception as e:
            self.enhanced_logger.debug("log.debug.data.akshare_error", error=str(e))
        
        # 所有数据源都失败
        raise Exception("All US stock data sources failed")
    
    async def _get_enhanced_china_stock_data(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取增强的A股数据"""
        self.enhanced_logger.debug_data_source_select("enhanced_china_pipeline", symbol)
        
        # 使用现有的A股数据获取逻辑
        success, data = await self.get_data(symbol, DataType.STOCK_INFO)
        
        if success and data:
            formatted_data = self._format_china_stock_data_tradingagents_style(
                symbol, data, start_date, end_date
            )
            
            return {
                "success": True,
                "symbol": symbol,
                "market_type": "china",
                "data_source": "unified_china",
                "formatted_data": formatted_data,
                "raw_data": data,
                "start_date": start_date,
                "end_date": end_date
            }
        else:
            raise Exception("China stock data fetch failed")
    
    async def _get_enhanced_hk_stock_data(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取增强的港股数据"""
        self.enhanced_logger.debug_data_source_select("enhanced_hk_pipeline", symbol)

        # 港股数据获取逻辑 - 使用工厂方法
        try:
            stock_info = await self.data_source_factory.get_stock_info(symbol, MarketType.HK_STOCK)

            if stock_info:
                formatted_data = self._format_hk_stock_data_tradingagents_style(
                    symbol, stock_info, start_date, end_date
                )

                return {
                    "success": True,
                    "symbol": symbol,
                    "market_type": "hk",
                    "data_source": "unified_hk",
                    "formatted_data": formatted_data,
                    "raw_data": stock_info,
                    "start_date": start_date,
                    "end_date": end_date
                }
        except Exception as e:
            self.enhanced_logger.debug("log.debug.data.hk_error", error=str(e))

        raise Exception("HK stock data fetch failed")
    
    def _detect_market_type(self, symbol: str) -> str:
        """检测股票市场类型"""
        symbol = symbol.upper().strip()
        
        # A股判断
        if (symbol.startswith(('00', '30', '60')) and len(symbol) == 6 and symbol.isdigit()) or \
           symbol.startswith(('SZ', 'SH')):
            return "china"
        
        # 港股判断
        if (symbol.startswith('0') and len(symbol) == 5 and symbol.isdigit()) or \
           symbol.endswith('.HK'):
            return "hk"
        
        # 默认美股
        return "us"
    
    def _format_us_stock_data_tradingagents_style(self, symbol: str, stock_info: Dict[str, Any], 
                                                 start_date: str, end_date: str, 
                                                 data_source: str, stock_data: List = None) -> str:
        """格式化美股数据为TradingAgents风格"""
        company_name = stock_info.get('name', symbol)
        current_price = stock_info.get('current_price', 0)
        change = stock_info.get('change', 0)
        change_percent = stock_info.get('change_percent', 0)
        
        formatted_data = f"""# {symbol.upper()} 美股数据分析

## 📊 实时行情
- 股票名称: {company_name}
- 当前价格: ${current_price:.2f}
- 涨跌额: ${change:+.2f}
- 涨跌幅: {change_percent:+.2f}%
- 开盘价: ${stock_info.get('open', 0):.2f}
- 最高价: ${stock_info.get('high', 0):.2f}
- 最低价: ${stock_info.get('low', 0):.2f}
- 前收盘: ${stock_info.get('previous_close', 0):.2f}
- 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 数据概览
- 数据期间: {start_date} 至 {end_date}
- 数据来源: {data_source.upper()} API
- 市场类型: 美股 (US Stock)
- 货币单位: USD"""

        if stock_data and len(stock_data) > 0:
            formatted_data += f"""
- 历史数据: {len(stock_data)} 条记录
- 数据完整性: ✅ 完整"""
        else:
            formatted_data += """
- 历史数据: 实时数据
- 数据完整性: ⚠️ 仅实时"""

        formatted_data += f"""

## 🎯 技术指标
- 当前价位相对位置: {self._calculate_price_position(current_price, stock_info):.1f}%
- 日内振幅: {self._calculate_daily_amplitude(stock_info):.2f}%

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
数据来源: Enhanced Data Manager v2.0
"""
        return formatted_data
    
    def _format_china_stock_data_tradingagents_style(self, symbol: str, stock_info: Dict[str, Any], 
                                                   start_date: str, end_date: str) -> str:
        """格式化A股数据为TradingAgents风格"""
        # 类似美股格式，但适配A股特点
        return f"""# {symbol} A股数据分析

## 📊 实时行情
- 股票名称: {stock_info.get('name', symbol)}
- 当前价格: ¥{stock_info.get('current_price', 0):.2f}
- 涨跌额: ¥{stock_info.get('change', 0):+.2f}
- 涨跌幅: {stock_info.get('change_percent', 0):+.2f}%
- 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 数据概览
- 数据期间: {start_date} 至 {end_date}
- 数据来源: 统一A股数据源
- 市场类型: A股 (China A-Share)
- 货币单位: CNY

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
数据来源: Enhanced Data Manager v2.0
"""
    
    def _format_hk_stock_data_tradingagents_style(self, symbol: str, stock_info: Dict[str, Any], 
                                                 start_date: str, end_date: str) -> str:
        """格式化港股数据为TradingAgents风格"""
        return f"""# {symbol} 港股数据分析

## 📊 实时行情
- 股票名称: {stock_info.get('name', symbol)}
- 当前价格: HK${stock_info.get('current_price', 0):.2f}
- 涨跌额: HK${stock_info.get('change', 0):+.2f}
- 涨跌幅: {stock_info.get('change_percent', 0):+.2f}%
- 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 数据概览
- 数据期间: {start_date} 至 {end_date}
- 数据来源: AKShare港股数据
- 市场类型: 港股 (Hong Kong Stock)
- 货币单位: HKD

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
数据来源: Enhanced Data Manager v2.0
"""
    
    def _calculate_price_position(self, current_price: float, stock_info: Dict[str, Any]) -> float:
        """计算当前价位相对位置"""
        high = stock_info.get('high', current_price)
        low = stock_info.get('low', current_price)
        
        if high == low:
            return 50.0
        
        return ((current_price - low) / (high - low)) * 100
    
    def _calculate_daily_amplitude(self, stock_info: Dict[str, Any]) -> float:
        """计算日内振幅"""
        high = stock_info.get('high', 0)
        low = stock_info.get('low', 0)
        previous_close = stock_info.get('previous_close', 1)
        
        if previous_close == 0:
            return 0.0
        
        return ((high - low) / previous_close) * 100
