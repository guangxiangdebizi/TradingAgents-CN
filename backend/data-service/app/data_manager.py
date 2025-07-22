#!/usr/bin/env python3
"""
数据管理器 - 智能数据获取和缓存策略
支持多数据源优先级、本地缓存、定时更新
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from pymongo import MongoClient
import redis

# 导入国际化日志
from backend.shared.i18n.logger import get_i18n_logger, get_compatible_logger
from backend.shared.i18n.config import SupportedLanguage

# 初始化国际化日志
i18n_logger = get_i18n_logger("data-manager")
logger = get_compatible_logger("data-manager")  # 兼容现有代码
# 注意：我们现在使用新的数据源工厂，不再依赖原项目的统一工具
from .datasources.factory import get_data_source_factory, DataSourceFactory
from .datasources.base import MarketType, DataCategory

logger = logging.getLogger(__name__)

class DataSource(Enum):
    """数据源枚举"""
    TUSHARE = "tushare"
    AKSHARE = "akshare"
    BAOSTOCK = "baostock"
    YFINANCE = "yfinance"
    FINNHUB = "finnhub"

class DataType(Enum):
    """数据类型枚举"""
    STOCK_INFO = "stock_info"
    STOCK_DATA = "stock_data"
    FUNDAMENTALS = "fundamentals"
    NEWS = "news"

class DataPriority(Enum):
    """数据优先级"""
    HIGH = 1      # 实时数据，缓存5分钟
    MEDIUM = 2    # 日内数据，缓存1小时
    LOW = 3       # 历史数据，缓存1天

@dataclass
class DataConfig:
    """数据配置"""
    data_type: DataType
    priority: DataPriority
    cache_duration: timedelta
    sources: List[DataSource]  # 按优先级排序
    update_interval: timedelta  # 定时更新间隔

@dataclass
class CachedData:
    """缓存数据结构"""
    symbol: str
    data_type: str
    data: Any
    source: str
    timestamp: datetime
    expires_at: datetime
    version: str = "1.0"

class DataManager:
    """智能数据管理器"""

    def __init__(self, mongodb_client: MongoClient, redis_client: redis.Redis, language: SupportedLanguage = None):
        self.mongodb = mongodb_client
        self.redis = redis_client
        self.db = mongodb_client.tradingagents

        # 设置日志语言
        if language:
            i18n_logger.set_language(language)

        # 记录初始化日志
        i18n_logger.manager_initialized()

        # 初始化数据源工厂
        self.data_source_factory = get_data_source_factory()

        # 数据配置
        self.data_configs = {
            DataType.STOCK_INFO: DataConfig(
                data_type=DataType.STOCK_INFO,
                priority=DataPriority.LOW,
                cache_duration=timedelta(days=1),
                sources=[DataSource.TUSHARE, DataSource.AKSHARE, DataSource.YFINANCE],
                update_interval=timedelta(hours=24)
            ),
            DataType.STOCK_DATA: DataConfig(
                data_type=DataType.STOCK_DATA,
                priority=DataPriority.MEDIUM,
                cache_duration=timedelta(hours=1),
                sources=[DataSource.TUSHARE, DataSource.AKSHARE, DataSource.BAOSTOCK],
                update_interval=timedelta(minutes=15)
            ),
            DataType.FUNDAMENTALS: DataConfig(
                data_type=DataType.FUNDAMENTALS,
                priority=DataPriority.LOW,
                cache_duration=timedelta(hours=6),
                sources=[DataSource.TUSHARE, DataSource.AKSHARE],
                update_interval=timedelta(hours=6)
            ),
            DataType.NEWS: DataConfig(
                data_type=DataType.NEWS,
                priority=DataPriority.HIGH,
                cache_duration=timedelta(minutes=30),
                sources=[DataSource.FINNHUB, DataSource.AKSHARE],
                update_interval=timedelta(minutes=30)
            )
        }
        
        # 初始化集合索引
        self._init_indexes()

    def set_log_language(self, language: SupportedLanguage):
        """设置日志语言"""
        i18n_logger.set_language(language)
        i18n_logger.info("log.data_manager.language_set", language=language.value)

    def _init_indexes(self):
        """初始化数据库索引"""
        try:
            # 缓存数据索引
            self.db.cached_data.create_index([
                ("symbol", 1), ("data_type", 1)
            ], unique=True)
            self.db.cached_data.create_index("expires_at")
            
            # 历史数据索引
            self.db.stock_data.create_index([
                ("symbol", 1), ("date", -1)
            ])
            self.db.stock_info.create_index("symbol", unique=True)
            self.db.fundamentals.create_index([
                ("symbol", 1), ("date", -1)
            ])
            self.db.news.create_index([
                ("symbol", 1), ("timestamp", -1)
            ])
            
            logger.info("✅ 数据库索引初始化完成")
        except Exception as e:
            logger.error(f"❌ 数据库索引初始化失败: {e}")
    
    async def get_data(self, symbol: str, data_type: DataType, **kwargs) -> Tuple[bool, Any]:
        """
        智能获取数据
        
        Args:
            symbol: 股票代码
            data_type: 数据类型
            **kwargs: 额外参数
            
        Returns:
            (success, data): 成功标志和数据
        """
        try:
            # 记录开始处理请求
            i18n_logger.processing_request(symbol, data_type.value)
            start_time = time.time()

            # Debug: 记录查询开始
            i18n_logger.debug_query_start("data_request", symbol)

            # 1. 检查缓存
            i18n_logger.debug_cache_check_start(symbol, data_type.value)
            cached_data = await self._get_cached_data(symbol, data_type)

            if cached_data and not self._is_expired(cached_data):
                i18n_logger.debug_cache_check_result("hit", symbol)
                i18n_logger.cache_hit(symbol, data_type.value)
                duration = int((time.time() - start_time) * 1000)
                i18n_logger.debug_query_end("data_request", duration)
                i18n_logger.request_completed(symbol, duration)
                return True, cached_data.data

            if cached_data:
                i18n_logger.debug_cache_check_result("expired", symbol)
                i18n_logger.cache_expired(symbol, data_type.value)
            else:
                i18n_logger.debug_cache_check_result("miss", symbol)
                i18n_logger.cache_miss(symbol, data_type.value)

            # 2. 从数据源获取
            i18n_logger.debug("log.debug.data.fetch_start", symbol=symbol, data_type=data_type.value)
            success, fresh_data = await self._fetch_from_sources(symbol, data_type, **kwargs)

            if not success:
                i18n_logger.debug("log.debug.data.fetch_failed", symbol=symbol, data_type=data_type.value)
                # 如果获取失败，返回过期的缓存数据（如果有）
                if cached_data:
                    i18n_logger.fallback_triggered("data_fetch_failed")
                    duration = int((time.time() - start_time) * 1000)
                    i18n_logger.debug_query_end("data_request", duration)
                    i18n_logger.request_completed(symbol, duration)
                    return True, cached_data.data
                i18n_logger.request_failed(symbol, "no_data_available")
                return False, None

            i18n_logger.debug("log.debug.data.fetch_success", symbol=symbol, data_type=data_type.value)

            # 3. 保存到缓存和数据库
            i18n_logger.debug("log.debug.data.save_start", symbol=symbol, data_type=data_type.value)
            await self._save_data(symbol, data_type, fresh_data)
            i18n_logger.debug("log.debug.data.save_end", symbol=symbol, data_type=data_type.value)

            duration = int((time.time() - start_time) * 1000)
            i18n_logger.debug_query_end("data_request", duration)
            i18n_logger.data_fetched(symbol, "data_source_factory")
            i18n_logger.request_completed(symbol, duration)
            return True, fresh_data
            
        except Exception as e:
            logger.error(f"❌ 数据获取失败: {symbol} - {data_type.value} - {e}")
            return False, None
    
    async def _get_cached_data(self, symbol: str, data_type: DataType) -> Optional[CachedData]:
        """获取缓存数据"""
        try:
            # 先检查 Redis
            redis_key = f"data:{symbol}:{data_type.value}"
            i18n_logger.debug("log.debug.data.redis_check", cache_key=redis_key)

            redis_data = self.redis.get(redis_key)
            if redis_data:
                i18n_logger.debug("log.debug.data.redis_hit", cache_key=redis_key)
                data_dict = json.loads(redis_data)

                # 确保datetime字段正确解析
                if 'timestamp' in data_dict and isinstance(data_dict['timestamp'], str):
                    data_dict['timestamp'] = datetime.fromisoformat(data_dict['timestamp'].replace('Z', '+00:00'))
                if 'expires_at' in data_dict and isinstance(data_dict['expires_at'], str):
                    data_dict['expires_at'] = datetime.fromisoformat(data_dict['expires_at'].replace('Z', '+00:00'))

                return CachedData(**data_dict)

            i18n_logger.debug("log.debug.data.redis_miss", cache_key=redis_key)

            # 再检查 MongoDB
            i18n_logger.debug("log.debug.data.mongo_check", symbol=symbol, data_type=data_type.value)
            doc = self.db.cached_data.find_one({
                "symbol": symbol,
                "data_type": data_type.value
            })

            if doc:
                i18n_logger.debug("log.debug.data.mongo_hit", symbol=symbol, data_type=data_type.value)
                doc.pop("_id", None)
                cached_data = CachedData(**doc)

                # 同步到 Redis
                ttl = int(self.data_configs[data_type].cache_duration.total_seconds())
                i18n_logger.debug_cache_save_start(symbol, data_type.value)
                self.redis.setex(
                    redis_key,
                    ttl,
                    json.dumps(asdict(cached_data), default=str)
                )
                i18n_logger.debug_cache_save_end(symbol, ttl)
                
                return cached_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 获取缓存数据失败: {e}")
            return None
    
    def _is_expired(self, cached_data: CachedData) -> bool:
        """检查数据是否过期"""
        return datetime.now() > cached_data.expires_at
    
    async def _fetch_from_sources(self, symbol: str, data_type: DataType, **kwargs) -> Tuple[bool, Any]:
        """从数据源获取数据"""
        try:
            # 检测市场类型
            market_type = self.data_source_factory.detect_market_type(symbol)
            logger.info(f"🔍 检测到市场类型: {market_type.value} for {symbol}")

            # 使用数据源工厂获取数据
            if data_type == DataType.STOCK_INFO:
                data = await self.data_source_factory.get_stock_info(symbol, market_type)
                category = DataCategory.BASIC_INFO

            elif data_type == DataType.STOCK_DATA:
                start_date = kwargs.get('start_date')
                end_date = kwargs.get('end_date')
                data = await self.data_source_factory.get_stock_data(symbol, market_type, start_date, end_date)
                category = DataCategory.PRICE_DATA

            elif data_type == DataType.FUNDAMENTALS:
                start_date = kwargs.get('start_date')
                end_date = kwargs.get('end_date')
                data = await self.data_source_factory.get_fundamentals(symbol, market_type, start_date, end_date)
                category = DataCategory.FUNDAMENTALS

            elif data_type == DataType.NEWS:
                start_date = kwargs.get('start_date', (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
                end_date = kwargs.get('end_date', datetime.now().strftime('%Y-%m-%d'))
                data = await self.data_source_factory.get_news(symbol, market_type, start_date, end_date)
                category = DataCategory.NEWS

            else:
                logger.error(f"❌ 不支持的数据类型: {data_type.value}")
                return False, None

            if data:
                logger.info(f"✅ 数据源工厂获取成功: {symbol} - {data_type.value}")
                return True, {
                    "source": "data_source_factory",
                    "market_type": market_type.value,
                    "category": category.value,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.warning(f"⚠️ 数据源工厂未获取到数据: {symbol} - {data_type.value}")

                # 降级到原有的统一工具
                return await self._fetch_from_legacy_tools(symbol, data_type, **kwargs)

        except Exception as e:
            logger.error(f"❌ 数据源工厂获取失败: {symbol} - {data_type.value} - {e}")
            # 降级到原有的统一工具
            return await self._fetch_from_legacy_tools(symbol, data_type, **kwargs)

    async def _fetch_from_legacy_tools(self, symbol: str, data_type: DataType, **kwargs) -> Tuple[bool, Any]:
        """从原有统一工具获取数据（降级方案）"""
        try:
            logger.info(f"🔄 使用原有统一工具获取数据: {symbol} - {data_type.value}")

            # 根据数据类型调用相应的获取函数
            if data_type == DataType.STOCK_INFO:
                data = get_stock_info(symbol)
            elif data_type == DataType.STOCK_DATA:
                start_date = kwargs.get('start_date')
                end_date = kwargs.get('end_date')
                data = get_stock_data(symbol, start_date, end_date)
            elif data_type == DataType.FUNDAMENTALS:
                start_date = kwargs.get('start_date')
                end_date = kwargs.get('end_date')
                curr_date = kwargs.get('curr_date')
                data = get_stock_fundamentals(symbol, start_date, end_date, curr_date)
            elif data_type == DataType.NEWS:
                curr_date = kwargs.get('curr_date', datetime.now().strftime('%Y-%m-%d'))
                hours_back = kwargs.get('hours_back', 24)
                data = get_stock_news(symbol, curr_date, hours_back)
            else:
                return False, None

            if data:
                logger.info(f"✅ 原有统一工具获取成功: {symbol} - {data_type.value}")
                return True, {
                    "source": "legacy_unified_tools",
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ 原有统一工具也无法获取数据: {symbol} - {data_type.value}")
                return False, None

        except Exception as e:
            logger.error(f"❌ 原有统一工具获取失败: {symbol} - {data_type.value} - {e}")
            return False, None
    
    async def _save_data(self, symbol: str, data_type: DataType, data: Any):
        """保存数据到缓存和数据库"""
        try:
            config = self.data_configs[data_type]
            now = datetime.now()
            expires_at = now + config.cache_duration

            # 确保数据格式正确
            if isinstance(data, dict):
                source = data.get("source", "unknown")
                actual_data = data.get("data", data)
            else:
                source = "unknown"
                actual_data = data

            cached_data = CachedData(
                symbol=symbol,
                data_type=data_type.value,
                data=data,  # 保存完整的数据结构
                source=source,
                timestamp=now,
                expires_at=expires_at
            )

            # 保存到 MongoDB 缓存表
            try:
                self.db.cached_data.replace_one(
                    {"symbol": symbol, "data_type": data_type.value},
                    asdict(cached_data),
                    upsert=True
                )
                logger.info(f"✅ MongoDB 缓存保存成功: {symbol} - {data_type.value}")
            except Exception as e:
                logger.error(f"❌ MongoDB 缓存保存失败: {e}")

            # 保存到 Redis
            try:
                redis_key = f"data:{symbol}:{data_type.value}"
                self.redis.setex(
                    redis_key,
                    int(config.cache_duration.total_seconds()),
                    json.dumps(asdict(cached_data), default=str)
                )
                logger.info(f"✅ Redis 缓存保存成功: {symbol} - {data_type.value}")
            except Exception as e:
                logger.error(f"❌ Redis 缓存保存失败: {e}")

            # 保存到历史数据表
            await self._save_historical_data(symbol, data_type, data)

            logger.info(f"✅ 数据保存完成: {symbol} - {data_type.value}")

        except Exception as e:
            logger.error(f"❌ 数据保存失败: {symbol} - {data_type.value} - {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
    
    async def _save_historical_data(self, symbol: str, data_type: DataType, data: Any):
        """保存历史数据到专门的历史数据表"""
        try:
            # 提取实际数据
            if isinstance(data, dict):
                actual_data = data.get("data", data)
                source = data.get("source", "unknown")
                market_type = data.get("market_type", "unknown")
            else:
                actual_data = data
                source = "unknown"
                market_type = "unknown"

            now = datetime.now()

            if data_type == DataType.STOCK_INFO:
                # 股票基本信息
                try:
                    self.db.stock_info.replace_one(
                        {"symbol": symbol},
                        {
                            "symbol": symbol,
                            "data": actual_data,
                            "source": source,
                            "market_type": market_type,
                            "updated_at": now,
                            "created_at": now
                        },
                        upsert=True
                    )
                    logger.info(f"✅ 股票信息历史数据保存成功: {symbol}")
                except Exception as e:
                    logger.error(f"❌ 股票信息历史数据保存失败: {e}")

            elif data_type == DataType.STOCK_DATA:
                # 股票价格数据按日期存储
                try:
                    if isinstance(actual_data, list):
                        saved_count = 0
                        for record in actual_data:
                            if isinstance(record, dict) and record.get("date"):
                                self.db.stock_data.replace_one(
                                    {"symbol": symbol, "date": record.get("date")},
                                    {
                                        "symbol": symbol,
                                        "date": record.get("date"),
                                        "open": record.get("open"),
                                        "high": record.get("high"),
                                        "low": record.get("low"),
                                        "close": record.get("close"),
                                        "volume": record.get("volume"),
                                        "amount": record.get("amount"),
                                        "source": source,
                                        "market_type": market_type,
                                        "updated_at": now,
                                        "created_at": now
                                    },
                                    upsert=True
                                )
                                saved_count += 1
                        logger.info(f"✅ 股票价格历史数据保存成功: {symbol}, {saved_count} 条记录")
                    else:
                        logger.warning(f"⚠️ 股票价格数据格式不正确: {symbol}")
                except Exception as e:
                    logger.error(f"❌ 股票价格历史数据保存失败: {e}")

            elif data_type == DataType.FUNDAMENTALS:
                # 基本面数据
                try:
                    report_date = actual_data.get("report_date") if isinstance(actual_data, dict) else now.strftime("%Y-%m-%d")
                    self.db.fundamentals.replace_one(
                        {"symbol": symbol, "report_date": report_date},
                        {
                            "symbol": symbol,
                            "report_date": report_date,
                            "data": actual_data,
                            "source": source,
                            "market_type": market_type,
                            "updated_at": now,
                            "created_at": now
                        },
                        upsert=True
                    )
                    logger.info(f"✅ 基本面历史数据保存成功: {symbol}")
                except Exception as e:
                    logger.error(f"❌ 基本面历史数据保存失败: {e}")

            elif data_type == DataType.NEWS:
                # 新闻数据
                try:
                    if isinstance(actual_data, list):
                        saved_count = 0
                        for news_item in actual_data:
                            if isinstance(news_item, dict):
                                # 使用新闻标题和发布时间作为唯一标识
                                title = news_item.get("title", "")
                                publish_time = news_item.get("publish_time", now.isoformat())

                                self.db.news.replace_one(
                                    {"symbol": symbol, "title": title, "publish_time": publish_time},
                                    {
                                        "symbol": symbol,
                                        "title": title,
                                        "content": news_item.get("content", ""),
                                        "publish_time": publish_time,
                                        "source": news_item.get("source", source),
                                        "url": news_item.get("url", ""),
                                        "market_type": market_type,
                                        "updated_at": now,
                                        "created_at": now
                                    },
                                    upsert=True
                                )
                                saved_count += 1
                        logger.info(f"✅ 新闻历史数据保存成功: {symbol}, {saved_count} 条记录")
                    else:
                        logger.warning(f"⚠️ 新闻数据格式不正确: {symbol}")
                except Exception as e:
                    logger.error(f"❌ 新闻历史数据保存失败: {e}")

        except Exception as e:
            logger.error(f"❌ 历史数据保存失败: {symbol} - {data_type.value} - {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
    
    async def cleanup_expired_data(self):
        """清理过期数据"""
        try:
            now = datetime.now()
            
            # 清理 MongoDB 过期缓存
            result = self.db.cached_data.delete_many({
                "expires_at": {"$lt": now}
            })
            
            if result.deleted_count > 0:
                logger.info(f"🧹 清理过期缓存数据: {result.deleted_count} 条")
            
            # 清理旧的新闻数据（保留30天）
            old_news_date = now - timedelta(days=30)
            result = self.db.news.delete_many({
                "timestamp": {"$lt": old_news_date}
            })
            
            if result.deleted_count > 0:
                logger.info(f"🧹 清理旧新闻数据: {result.deleted_count} 条")
                
        except Exception as e:
            logger.error(f"❌ 清理过期数据失败: {e}")
    
    async def get_data_statistics(self) -> Dict[str, Any]:
        """获取数据统计信息"""
        try:
            stats = {}

            # 缓存数据统计
            for data_type in DataType:
                count = self.db.cached_data.count_documents({
                    "data_type": data_type.value
                })
                stats[f"cached_{data_type.value}"] = count

            # 历史数据统计
            stats["historical_stock_info"] = self.db.stock_info.count_documents({})
            stats["historical_stock_data"] = self.db.stock_data.count_documents({})
            stats["historical_fundamentals"] = self.db.fundamentals.count_documents({})
            stats["historical_news"] = self.db.news.count_documents({})

            # Redis 统计
            redis_info = self.redis.info()
            stats["redis_used_memory"] = redis_info.get("used_memory_human", "N/A")
            stats["redis_connected_clients"] = redis_info.get("connected_clients", 0)

            # 数据源统计
            stats["data_sources"] = self.data_source_factory.get_source_stats()

            return stats

        except Exception as e:
            logger.error(f"❌ 获取数据统计失败: {e}")
            return {}

    async def health_check_data_sources(self) -> Dict[str, Any]:
        """检查所有数据源健康状态"""
        try:
            return await self.data_source_factory.health_check_all()
        except Exception as e:
            logger.error(f"❌ 数据源健康检查失败: {e}")
            return {}

    async def get_local_data_summary(self) -> Dict[str, Any]:
        """获取本地数据存储摘要"""
        try:
            summary = {
                "cached_data": {},
                "historical_data": {},
                "database_info": {}
            }

            # 缓存数据统计
            for data_type in DataType:
                count = self.db.cached_data.count_documents({
                    "data_type": data_type.value
                })
                summary["cached_data"][data_type.value] = count

            # 历史数据统计
            summary["historical_data"]["stock_info"] = self.db.stock_info.count_documents({})
            summary["historical_data"]["stock_data"] = self.db.stock_data.count_documents({})
            summary["historical_data"]["fundamentals"] = self.db.fundamentals.count_documents({})
            summary["historical_data"]["news"] = self.db.news.count_documents({})

            # 数据库信息
            db_stats = self.mongodb.admin.command("dbstats")
            summary["database_info"] = {
                "database_name": "tradingagents",
                "collections": db_stats.get("collections", 0),
                "data_size": db_stats.get("dataSize", 0),
                "storage_size": db_stats.get("storageSize", 0),
                "indexes": db_stats.get("indexes", 0)
            }

            # Redis 信息
            redis_info = self.redis.info()
            summary["redis_info"] = {
                "used_memory": redis_info.get("used_memory_human", "N/A"),
                "connected_clients": redis_info.get("connected_clients", 0),
                "total_commands_processed": redis_info.get("total_commands_processed", 0)
            }

            return summary

        except Exception as e:
            logger.error(f"❌ 获取本地数据摘要失败: {e}")
            return {}

    async def get_symbol_data_history(self, symbol: str) -> Dict[str, Any]:
        """获取特定股票的数据历史"""
        try:
            history = {
                "symbol": symbol,
                "stock_info": None,
                "stock_data": [],
                "fundamentals": [],
                "news": [],
                "cached_data": []
            }

            # 股票基本信息
            stock_info = self.db.stock_info.find_one({"symbol": symbol})
            if stock_info:
                history["stock_info"] = {
                    "data": stock_info.get("data"),
                    "source": stock_info.get("source"),
                    "updated_at": stock_info.get("updated_at")
                }

            # 股票价格数据（最近30天）
            stock_data = list(self.db.stock_data.find(
                {"symbol": symbol}
            ).sort("date", -1).limit(30))

            for record in stock_data:
                history["stock_data"].append({
                    "date": record.get("date"),
                    "open": record.get("open"),
                    "high": record.get("high"),
                    "low": record.get("low"),
                    "close": record.get("close"),
                    "volume": record.get("volume"),
                    "source": record.get("source"),
                    "updated_at": record.get("updated_at")
                })

            # 基本面数据
            fundamentals = list(self.db.fundamentals.find(
                {"symbol": symbol}
            ).sort("report_date", -1).limit(10))

            for record in fundamentals:
                history["fundamentals"].append({
                    "report_date": record.get("report_date"),
                    "data": record.get("data"),
                    "source": record.get("source"),
                    "updated_at": record.get("updated_at")
                })

            # 新闻数据（最近20条）
            news = list(self.db.news.find(
                {"symbol": symbol}
            ).sort("publish_time", -1).limit(20))

            for record in news:
                history["news"].append({
                    "title": record.get("title"),
                    "content": record.get("content", "")[:200] + "...",  # 截取前200字符
                    "publish_time": record.get("publish_time"),
                    "source": record.get("source"),
                    "url": record.get("url")
                })

            # 缓存数据
            cached_data = list(self.db.cached_data.find({"symbol": symbol}))
            for record in cached_data:
                history["cached_data"].append({
                    "data_type": record.get("data_type"),
                    "source": record.get("source"),
                    "timestamp": record.get("timestamp"),
                    "expires_at": record.get("expires_at")
                })

            return history

        except Exception as e:
            logger.error(f"❌ 获取股票数据历史失败: {symbol} - {e}")
            return {}

    async def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """清理旧数据"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cleanup_stats = {
                "cached_data": 0,
                "news": 0,
                "old_stock_data": 0
            }

            # 清理过期缓存数据
            result = self.db.cached_data.delete_many({
                "expires_at": {"$lt": cutoff_date}
            })
            cleanup_stats["cached_data"] = result.deleted_count

            # 清理旧新闻数据
            result = self.db.news.delete_many({
                "created_at": {"$lt": cutoff_date}
            })
            cleanup_stats["news"] = result.deleted_count

            # 清理过旧的股票数据（保留最近1年）
            old_cutoff = datetime.now() - timedelta(days=365)
            result = self.db.stock_data.delete_many({
                "updated_at": {"$lt": old_cutoff}
            })
            cleanup_stats["old_stock_data"] = result.deleted_count

            logger.info(f"✅ 数据清理完成: {cleanup_stats}")
            return cleanup_stats

        except Exception as e:
            logger.error(f"❌ 数据清理失败: {e}")
            return {}

    async def force_refresh_data(self, symbol: str, data_type: DataType, **kwargs) -> Tuple[bool, Any]:
        """强制刷新数据（忽略缓存）"""
        try:
            logger.info(f"🔄 强制刷新数据: {symbol} - {data_type.value}")

            # 直接从数据源获取
            success, fresh_data = await self._fetch_from_sources(symbol, data_type, **kwargs)
            if not success:
                return False, None

            # 保存到缓存和数据库
            await self._save_data(symbol, data_type, fresh_data)

            logger.info(f"✅ 强制刷新成功: {symbol} - {data_type.value}")
            return True, fresh_data

        except Exception as e:
            logger.error(f"❌ 强制刷新失败: {symbol} - {data_type.value} - {e}")
            return False, None


# 全局数据管理器实例
data_manager: Optional[DataManager] = None

def get_data_manager() -> DataManager:
    """获取数据管理器实例"""
    global data_manager
    if data_manager is None:
        raise RuntimeError("数据管理器未初始化")
    return data_manager

def init_data_manager(mongodb_client: MongoClient, redis_client: redis.Redis):
    """初始化数据管理器"""
    global data_manager
    data_manager = DataManager(mongodb_client, redis_client)
    logger.info("✅ 数据管理器初始化完成")
