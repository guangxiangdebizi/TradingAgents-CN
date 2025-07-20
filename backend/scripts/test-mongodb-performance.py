#!/usr/bin/env python3
"""
MongoDB 性能测试脚本
测试股票数据存储和查询性能
"""

import asyncio
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.shared.database.mongodb import get_db_manager, get_stock_repository


class MongoDBPerformanceTester:
    """MongoDB 性能测试器"""
    
    def __init__(self):
        self.db_manager = None
        self.stock_repo = None
    
    async def setup(self):
        """初始化"""
        print("🔧 初始化测试环境...")
        self.db_manager = await get_db_manager()
        self.stock_repo = await get_stock_repository()
        
        if not self.db_manager.is_connected():
            print("❌ MongoDB 连接失败")
            return False
        
        print("✅ MongoDB 连接成功")
        return True
    
    def generate_test_data(self, symbol: str, days: int = 365) -> List[Dict[str, Any]]:
        """生成测试数据"""
        data = []
        base_price = 100.0
        current_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            # 模拟股价波动
            change = random.uniform(-0.05, 0.05)  # ±5% 波动
            base_price *= (1 + change)
            
            # 生成OHLC数据
            open_price = base_price
            high_price = open_price * (1 + random.uniform(0, 0.03))
            low_price = open_price * (1 - random.uniform(0, 0.03))
            close_price = open_price + (high_price - low_price) * random.uniform(-0.5, 0.5)
            
            volume = random.randint(1000000, 10000000)
            amount = volume * close_price
            
            data.append({
                'trade_date': current_date + timedelta(days=i),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume,
                'amount': round(amount, 2)
            })
        
        return data
    
    async def test_write_performance(self, num_stocks: int = 100, days_per_stock: int = 365):
        """测试写入性能"""
        print(f"\n📝 测试写入性能: {num_stocks}只股票 × {days_per_stock}天")
        
        start_time = time.time()
        total_records = 0
        
        for i in range(num_stocks):
            symbol = f"TEST{i:06d}"
            
            # 生成测试数据
            data = self.generate_test_data(symbol, days_per_stock)
            
            # 写入数据库
            success = await self.stock_repo.save_stock_daily_data(symbol, data)
            
            if success:
                total_records += len(data)
                if (i + 1) % 10 == 0:
                    print(f"  已处理: {i + 1}/{num_stocks} 只股票")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ 写入完成:")
        print(f"  总记录数: {total_records:,}")
        print(f"  耗时: {duration:.2f}秒")
        print(f"  写入速度: {total_records/duration:.0f} 记录/秒")
        
        return total_records, duration
    
    async def test_read_performance(self, num_queries: int = 100):
        """测试读取性能"""
        print(f"\n📖 测试读取性能: {num_queries}次查询")
        
        # 准备查询参数
        queries = []
        for i in range(num_queries):
            symbol = f"TEST{random.randint(0, 99):06d}"
            start_date = datetime.now() - timedelta(days=random.randint(30, 365))
            end_date = start_date + timedelta(days=random.randint(30, 90))
            queries.append((symbol, start_date, end_date))
        
        # 执行查询
        start_time = time.time()
        total_records = 0
        
        for i, (symbol, start_date, end_date) in enumerate(queries):
            data = await self.stock_repo.get_stock_daily_data(symbol, start_date, end_date)
            total_records += len(data)
            
            if (i + 1) % 20 == 0:
                print(f"  已查询: {i + 1}/{num_queries}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ 查询完成:")
        print(f"  查询次数: {num_queries}")
        print(f"  返回记录数: {total_records:,}")
        print(f"  耗时: {duration:.2f}秒")
        print(f"  查询速度: {num_queries/duration:.1f} 查询/秒")
        print(f"  平均每查询: {duration/num_queries*1000:.1f}毫秒")
        
        return num_queries, total_records, duration
    
    async def test_aggregation_performance(self):
        """测试聚合查询性能"""
        print(f"\n📊 测试聚合查询性能")
        
        collection = self.db_manager.get_collection('stock_daily')
        if not collection:
            print("❌ 无法获取集合")
            return
        
        # 测试1: 计算平均价格
        print("  测试1: 计算所有股票平均价格...")
        start_time = time.time()
        
        pipeline = [
            {
                '$group': {
                    '_id': '$symbol',
                    'avg_price': {'$avg': '$close'},
                    'max_price': {'$max': '$high'},
                    'min_price': {'$min': '$low'},
                    'total_volume': {'$sum': '$volume'}
                }
            },
            {'$sort': {'avg_price': -1}},
            {'$limit': 10}
        ]
        
        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=10)
        
        duration1 = time.time() - start_time
        print(f"    耗时: {duration1:.3f}秒, 结果: {len(results)}条")
        
        # 测试2: 按月统计
        print("  测试2: 按月统计交易量...")
        start_time = time.time()
        
        pipeline = [
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$trade_date'},
                        'month': {'$month': '$trade_date'}
                    },
                    'total_volume': {'$sum': '$volume'},
                    'avg_price': {'$avg': '$close'},
                    'stock_count': {'$addToSet': '$symbol'}
                }
            },
            {
                '$project': {
                    'year_month': '$_id',
                    'total_volume': 1,
                    'avg_price': 1,
                    'stock_count': {'$size': '$stock_count'}
                }
            },
            {'$sort': {'year_month.year': -1, 'year_month.month': -1}},
            {'$limit': 12}
        ]
        
        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=12)
        
        duration2 = time.time() - start_time
        print(f"    耗时: {duration2:.3f}秒, 结果: {len(results)}条")
        
        print(f"✅ 聚合查询完成:")
        print(f"  平均聚合时间: {(duration1 + duration2)/2:.3f}秒")
    
    async def test_index_performance(self):
        """测试索引性能"""
        print(f"\n🔍 测试索引性能")
        
        collection = self.db_manager.get_collection('stock_daily')
        if not collection:
            print("❌ 无法获取集合")
            return
        
        # 查看现有索引
        indexes = await collection.list_indexes().to_list(length=None)
        print(f"  现有索引数量: {len(indexes)}")
        for idx in indexes:
            print(f"    - {idx.get('name', 'unknown')}: {idx.get('key', {})}")
        
        # 测试查询性能（有索引）
        symbol = "TEST000001"
        start_date = datetime.now() - timedelta(days=90)
        end_date = datetime.now()
        
        print(f"  测试查询: {symbol} 最近90天数据")
        
        start_time = time.time()
        data = await self.stock_repo.get_stock_daily_data(symbol, start_date, end_date)
        duration = time.time() - start_time
        
        print(f"    查询结果: {len(data)}条记录")
        print(f"    查询耗时: {duration*1000:.1f}毫秒")
    
    async def cleanup_test_data(self):
        """清理测试数据"""
        print(f"\n🧹 清理测试数据...")
        
        collection = self.db_manager.get_collection('stock_daily')
        if not collection:
            return
        
        # 删除测试数据
        result = await collection.delete_many({'symbol': {'$regex': '^TEST'}})
        print(f"✅ 删除了 {result.deleted_count} 条测试记录")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 MongoDB 性能测试开始")
        print("=" * 50)
        
        if not await self.setup():
            return
        
        try:
            # 写入性能测试
            await self.test_write_performance(num_stocks=50, days_per_stock=365)
            
            # 读取性能测试
            await self.test_read_performance(num_queries=100)
            
            # 聚合查询测试
            await self.test_aggregation_performance()
            
            # 索引性能测试
            await self.test_index_performance()
            
        finally:
            # 清理测试数据
            await self.cleanup_test_data()
            
            # 断开连接
            if self.db_manager:
                await self.db_manager.disconnect()
        
        print("\n🎉 性能测试完成！")


async def main():
    """主函数"""
    tester = MongoDBPerformanceTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
