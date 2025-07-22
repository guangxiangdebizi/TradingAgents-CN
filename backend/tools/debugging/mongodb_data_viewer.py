#!/usr/bin/env python3
"""
MongoDB 数据查看工具
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from pymongo import MongoClient
    import redis
except ImportError:
    print("❌ 请安装依赖: pip install pymongo redis")
    sys.exit(1)

class MongoDBDataViewer:
    """MongoDB 数据查看器"""
    
    def __init__(self):
        try:
            # 连接 MongoDB (带认证)
            self.mongodb = MongoClient("mongodb://admin:tradingagents123@localhost:27017/tradingagents?authSource=admin")
            self.db = self.mongodb.tradingagents

            # 连接 Redis
            self.redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            sys.exit(1)
    
    def show_collections_info(self):
        """显示集合信息"""
        print("📊 MongoDB 集合信息")
        print("=" * 50)
        
        collections = self.db.list_collection_names()
        
        for collection_name in collections:
            collection = self.db[collection_name]
            count = collection.count_documents({})
            print(f"📋 {collection_name}: {count} 条记录")
            
            # 显示最新的一条记录
            if count > 0:
                latest = collection.find_one(sort=[("_id", -1)])
                if latest:
                    # 移除 _id 字段以便显示
                    latest.pop("_id", None)
                    print(f"   最新记录: {json.dumps(latest, default=str, ensure_ascii=False)[:100]}...")
        
        print(f"\n📊 总计: {len(collections)} 个集合")
    
    def show_cached_data(self):
        """显示缓存数据"""
        print("\n📦 缓存数据详情")
        print("=" * 50)
        
        # MongoDB 缓存
        cached_data = list(self.db.cached_data.find().sort("timestamp", -1))
        print(f"📋 MongoDB 缓存: {len(cached_data)} 条记录")
        
        for data in cached_data[:10]:  # 显示最新10条
            print(f"  🔹 {data.get('symbol')} - {data.get('data_type')}")
            print(f"     来源: {data.get('source')}")
            print(f"     时间: {data.get('timestamp')}")
            print(f"     过期: {data.get('expires_at')}")
            print()
        
        # Redis 缓存
        try:
            redis_keys = self.redis.keys("data:*")
            print(f"🔴 Redis 缓存: {len(redis_keys)} 个键")
            
            for key in redis_keys[:10]:  # 显示前10个
                ttl = self.redis.ttl(key)
                print(f"  🔹 {key} (TTL: {ttl}秒)")
        except Exception as e:
            print(f"❌ Redis 查询失败: {e}")
    
    def show_stock_data(self, symbol: str = None):
        """显示股票数据"""
        print(f"\n📈 股票数据 {f'({symbol})' if symbol else ''}")
        print("=" * 50)
        
        query = {"symbol": symbol} if symbol else {}
        
        # 股票信息
        stock_info = list(self.db.stock_info.find(query).limit(5))
        print(f"📋 股票信息: {len(stock_info)} 条记录")
        for info in stock_info:
            data = info.get("data", {})
            print(f"  🔹 {info.get('symbol')}: {data.get('name', 'N/A')}")
            print(f"     来源: {info.get('source', 'N/A')}")
            print(f"     更新: {info.get('updated_at', 'N/A')}")
        
        # 股票价格数据
        stock_data = list(self.db.stock_data.find(query).sort("date", -1).limit(10))
        print(f"\n📊 股票价格数据: {len(stock_data)} 条记录")
        for data in stock_data:
            print(f"  🔹 {data.get('symbol')} - {data.get('date')}")
            print(f"     开盘: {data.get('open')}, 收盘: {data.get('close')}")
            print(f"     成交量: {data.get('volume')}")
            print(f"     来源: {data.get('source', 'N/A')}")
        
        # 基本面数据
        fundamentals = list(self.db.fundamentals.find(query).sort("report_date", -1).limit(5))
        print(f"\n💰 基本面数据: {len(fundamentals)} 条记录")
        for fund in fundamentals:
            data = fund.get("data", {})
            print(f"  🔹 {fund.get('symbol')} - {fund.get('report_date')}")
            print(f"     ROE: {data.get('roe', 'N/A')}, PE: {data.get('pe_ratio', 'N/A')}")
            print(f"     来源: {fund.get('source', 'N/A')}")
        
        # 新闻数据
        news = list(self.db.news.find(query).sort("publish_time", -1).limit(5))
        print(f"\n📰 新闻数据: {len(news)} 条记录")
        for item in news:
            print(f"  🔹 {item.get('symbol')}: {item.get('title', 'N/A')[:50]}...")
            print(f"     发布: {item.get('publish_time', 'N/A')}")
            print(f"     来源: {item.get('source', 'N/A')}")
    
    def show_data_statistics(self):
        """显示数据统计"""
        print("\n📊 数据统计")
        print("=" * 50)
        
        # 按数据源统计
        print("📋 按数据源统计:")
        pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        for collection_name in ["stock_info", "stock_data", "fundamentals", "news"]:
            collection = self.db[collection_name]
            results = list(collection.aggregate(pipeline))
            if results:
                print(f"  {collection_name}:")
                for result in results:
                    print(f"    {result['_id']}: {result['count']} 条")
        
        # 按股票统计
        print("\n📈 按股票统计 (Top 10):")
        for collection_name in ["stock_info", "stock_data"]:
            collection = self.db[collection_name]
            pipeline = [
                {"$group": {"_id": "$symbol", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            results = list(collection.aggregate(pipeline))
            if results:
                print(f"  {collection_name}:")
                for result in results:
                    print(f"    {result['_id']}: {result['count']} 条")
        
        # 按日期统计
        print("\n📅 最近数据更新:")
        for collection_name in ["stock_info", "stock_data", "fundamentals", "news"]:
            collection = self.db[collection_name]
            latest = collection.find_one(sort=[("updated_at", -1)])
            if latest:
                print(f"  {collection_name}: {latest.get('updated_at', 'N/A')}")
    
    def cleanup_test_data(self):
        """清理测试数据"""
        print("\n🧹 清理测试数据")
        print("=" * 50)
        
        # 清理过期缓存
        cutoff_date = datetime.now() - timedelta(days=1)
        
        collections_to_clean = ["cached_data"]
        
        for collection_name in collections_to_clean:
            collection = self.db[collection_name]
            result = collection.delete_many({
                "expires_at": {"$lt": cutoff_date}
            })
            print(f"📋 {collection_name}: 清理了 {result.deleted_count} 条过期记录")
        
        # 清理 Redis 过期键
        try:
            redis_keys = self.redis.keys("data:*")
            expired_count = 0
            for key in redis_keys:
                ttl = self.redis.ttl(key)
                if ttl == -2:  # 键已过期
                    self.redis.delete(key)
                    expired_count += 1
            print(f"🔴 Redis: 清理了 {expired_count} 个过期键")
        except Exception as e:
            print(f"❌ Redis 清理失败: {e}")
    
    def export_data(self, symbol: str, output_file: str):
        """导出数据"""
        print(f"\n📤 导出 {symbol} 的数据到 {output_file}")
        print("=" * 50)
        
        export_data = {
            "symbol": symbol,
            "export_time": datetime.now().isoformat(),
            "stock_info": None,
            "stock_data": [],
            "fundamentals": [],
            "news": []
        }
        
        # 导出股票信息
        stock_info = self.db.stock_info.find_one({"symbol": symbol})
        if stock_info:
            stock_info.pop("_id", None)
            export_data["stock_info"] = stock_info
        
        # 导出股票数据
        stock_data = list(self.db.stock_data.find({"symbol": symbol}).sort("date", -1))
        for data in stock_data:
            data.pop("_id", None)
            export_data["stock_data"].append(data)
        
        # 导出基本面数据
        fundamentals = list(self.db.fundamentals.find({"symbol": symbol}).sort("report_date", -1))
        for data in fundamentals:
            data.pop("_id", None)
            export_data["fundamentals"].append(data)
        
        # 导出新闻数据
        news = list(self.db.news.find({"symbol": symbol}).sort("publish_time", -1).limit(50))
        for data in news:
            data.pop("_id", None)
            export_data["news"].append(data)
        
        # 保存到文件
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"✅ 导出完成:")
            print(f"   股票信息: {'有' if export_data['stock_info'] else '无'}")
            print(f"   股票数据: {len(export_data['stock_data'])} 条")
            print(f"   基本面数据: {len(export_data['fundamentals'])} 条")
            print(f"   新闻数据: {len(export_data['news'])} 条")
            
        except Exception as e:
            print(f"❌ 导出失败: {e}")

def main():
    """主函数"""
    viewer = MongoDBDataViewer()
    
    if len(sys.argv) < 2:
        print("🔍 TradingAgents MongoDB 数据查看工具")
        print("=" * 50)
        print("使用方法:")
        print("  python mongodb_data_viewer.py <命令> [参数]")
        print("")
        print("可用命令:")
        print("  info              - 显示集合信息")
        print("  cache             - 显示缓存数据")
        print("  stock [symbol]    - 显示股票数据")
        print("  stats             - 显示数据统计")
        print("  cleanup           - 清理测试数据")
        print("  export <symbol> <file> - 导出股票数据")
        print("")
        print("示例:")
        print("  python mongodb_data_viewer.py info")
        print("  python mongodb_data_viewer.py stock 000858")
        print("  python mongodb_data_viewer.py export 000858 data.json")
        return
    
    command = sys.argv[1].lower()
    
    if command == "info":
        viewer.show_collections_info()
    elif command == "cache":
        viewer.show_cached_data()
    elif command == "stock":
        symbol = sys.argv[2] if len(sys.argv) > 2 else None
        viewer.show_stock_data(symbol)
    elif command == "stats":
        viewer.show_data_statistics()
    elif command == "cleanup":
        viewer.cleanup_test_data()
    elif command == "export":
        if len(sys.argv) < 4:
            print("❌ 请指定股票代码和输出文件")
            return
        symbol = sys.argv[2]
        output_file = sys.argv[3]
        viewer.export_data(symbol, output_file)
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()
