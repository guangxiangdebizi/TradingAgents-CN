"""
MongoDB 数据访问层
提供统一的数据库操作接口
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
import pymongo
from bson import ObjectId
import pandas as pd

from ..utils.logger import get_service_logger
from ..utils.config import get_config

logger = get_service_logger("mongodb")


class MongoDBManager:
    """MongoDB 管理器"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.config = get_config()
        self._connected = False
    
    async def connect(self) -> bool:
        """连接到 MongoDB"""
        try:
            # 优先使用完整的 MONGODB_URL
            mongodb_url = self.config.get('MONGODB_URL')

            # 如果没有完整URL，从分开的配置项构建
            if not mongodb_url:
                host = self.config.get('MONGODB_HOST', 'localhost')
                port = self.config.get('MONGODB_PORT', '27017')
                username = self.config.get('MONGODB_USERNAME')
                password = self.config.get('MONGODB_PASSWORD')
                database = self.config.get('MONGODB_DATABASE', 'tradingagents')
                auth_source = self.config.get('MONGODB_AUTH_SOURCE', 'admin')

                if username and password:
                    mongodb_url = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource={auth_source}"
                else:
                    mongodb_url = f"mongodb://{host}:{port}/{database}"

            if not mongodb_url:
                logger.error("❌ MongoDB 配置不完整")
                return False

            # 调试：打印连接字符串（隐藏密码）
            safe_url = mongodb_url.replace(password or '', '***') if password else mongodb_url
            logger.info(f"🔗 尝试连接MongoDB: {safe_url}")
            
            # 创建客户端
            self.client = AsyncIOMotorClient(
                mongodb_url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=5
            )
            
            # 测试连接
            await self.client.admin.command('ping')
            
            # 获取数据库
            self.db = self.client.tradingagents
            self._connected = True
            
            logger.info("✅ MongoDB 连接成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ MongoDB 连接失败: {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """断开 MongoDB 连接"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("🔌 MongoDB 连接已断开")
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected
    
    def get_collection(self, collection_name: str) -> Optional[AsyncIOMotorCollection]:
        """获取集合"""
        if not self.is_connected() or self.db is None:
            return None
        return self.db[collection_name]


class StockDataRepository:
    """股票数据仓库"""
    
    def __init__(self, db_manager: MongoDBManager):
        self.db_manager = db_manager
        self.logger = get_service_logger("stock-repo")
    
    async def save_stock_info(self, stock_info: Dict[str, Any]) -> bool:
        """保存股票基本信息"""
        try:
            collection = self.db_manager.get_collection('stock_info')
            if not collection:
                return False
            
            # 添加时间戳
            stock_info['updated_at'] = datetime.now()
            if 'created_at' not in stock_info:
                stock_info['created_at'] = datetime.now()
            
            # 使用 upsert 更新或插入
            result = await collection.replace_one(
                {'symbol': stock_info['symbol']},
                stock_info,
                upsert=True
            )
            
            self.logger.info(f"💾 保存股票信息: {stock_info['symbol']}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 保存股票信息失败: {e}")
            return False
    
    async def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取股票基本信息"""
        try:
            collection = self.db_manager.get_collection('stock_info')
            if not collection:
                return None
            
            result = await collection.find_one({'symbol': symbol})
            if result:
                # 转换 ObjectId 为字符串
                result['_id'] = str(result['_id'])
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ 获取股票信息失败: {e}")
            return None
    
    async def save_stock_daily_data(self, symbol: str, data: List[Dict[str, Any]]) -> bool:
        """保存股票日线数据"""
        try:
            collection = self.db_manager.get_collection('stock_daily')
            if not collection:
                return False
            
            # 准备批量操作
            operations = []
            for record in data:
                record['symbol'] = symbol
                record['created_at'] = datetime.now()
                
                # 使用 upsert 避免重复数据
                operations.append(
                    pymongo.ReplaceOne(
                        {
                            'symbol': symbol,
                            'trade_date': record['trade_date']
                        },
                        record,
                        upsert=True
                    )
                )
            
            if operations:
                result = await collection.bulk_write(operations)
                self.logger.info(f"💾 保存日线数据: {symbol} - {len(operations)}条记录")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ 保存日线数据失败: {e}")
            return False
    
    async def get_stock_daily_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """获取股票日线数据"""
        try:
            collection = self.db_manager.get_collection('stock_daily')
            if not collection:
                return []
            
            # 构建查询条件
            query = {
                'symbol': symbol,
                'trade_date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            # 执行查询
            cursor = collection.find(query).sort('trade_date', 1).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # 转换 ObjectId
            for result in results:
                result['_id'] = str(result['_id'])
            
            self.logger.info(f"📊 获取日线数据: {symbol} - {len(results)}条记录")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ 获取日线数据失败: {e}")
            return []
    
    async def get_latest_stock_prices(self, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """获取最新股价"""
        try:
            collection = self.db_manager.get_collection('stock_latest_prices')
            if not collection:
                return []
            
            # 构建查询条件
            query = {}
            if symbols:
                query['symbol'] = {'$in': symbols}
            
            # 执行查询
            cursor = collection.find(query)
            results = await cursor.to_list(length=None)
            
            # 转换 ObjectId
            for result in results:
                if '_id' in result:
                    result['_id'] = str(result['_id'])
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ 获取最新股价失败: {e}")
            return []


class AnalysisRepository:
    """分析结果仓库"""
    
    def __init__(self, db_manager: MongoDBManager):
        self.db_manager = db_manager
        self.logger = get_service_logger("analysis-repo")
    
    async def save_analysis_result(self, analysis_result: Dict[str, Any]) -> bool:
        """保存分析结果"""
        try:
            collection = self.db_manager.get_collection('analysis_results')
            if not collection:
                return False
            
            # 添加时间戳
            analysis_result['created_at'] = datetime.now()
            analysis_result['updated_at'] = datetime.now()
            
            # 使用 upsert 更新或插入
            result = await collection.replace_one(
                {'analysis_id': analysis_result['analysis_id']},
                analysis_result,
                upsert=True
            )
            
            self.logger.info(f"💾 保存分析结果: {analysis_result['analysis_id']}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 保存分析结果失败: {e}")
            return False
    
    async def get_analysis_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """获取分析结果"""
        try:
            collection = self.db_manager.get_collection('analysis_results')
            if not collection:
                return None
            
            result = await collection.find_one({'analysis_id': analysis_id})
            if result:
                result['_id'] = str(result['_id'])
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ 获取分析结果失败: {e}")
            return None
    
    async def get_analysis_history(
        self,
        stock_code: str = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """获取分析历史"""
        try:
            collection = self.db_manager.get_collection('analysis_results')
            if not collection:
                return []
            
            # 构建查询条件
            query = {}
            if stock_code:
                query['stock_code'] = stock_code
            
            # 执行查询
            cursor = collection.find(query).sort('created_at', -1).skip(skip).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # 转换 ObjectId
            for result in results:
                result['_id'] = str(result['_id'])
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ 获取分析历史失败: {e}")
            return []


# 全局数据库管理器实例
_db_manager: Optional[MongoDBManager] = None


async def get_db_manager() -> MongoDBManager:
    """获取数据库管理器实例"""
    global _db_manager
    
    if _db_manager is None:
        _db_manager = MongoDBManager()
        await _db_manager.connect()
    
    return _db_manager


async def get_stock_repository() -> StockDataRepository:
    """获取股票数据仓库"""
    db_manager = await get_db_manager()
    return StockDataRepository(db_manager)


async def get_analysis_repository() -> AnalysisRepository:
    """获取分析结果仓库"""
    db_manager = await get_db_manager()
    return AnalysisRepository(db_manager)
