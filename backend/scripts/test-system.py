#!/usr/bin/env python3
"""
TradingAgents 系统测试脚本
测试基础服务和应用服务是否正常工作
"""

import asyncio
import httpx
import pymongo
import redis
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class SystemTester:
    """系统测试类"""
    
    def __init__(self):
        self.mongodb_url = "mongodb://admin:tradingagents123@localhost:27017/tradingagents?authSource=admin"
        self.redis_url = "redis://localhost:6379"
        self.services = {
            "data-service": "http://localhost:8002",
            "analysis-engine": "http://localhost:8001", 
            "api-gateway": "http://localhost:8000"
        }
    
    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{'='*60}")
        print(f"🔧 {title}")
        print(f"{'='*60}")
    
    def print_result(self, test_name: str, success: bool, details: str = ""):
        """打印测试结果"""
        icon = "✅" if success else "❌"
        print(f"{icon} {test_name:30} {details}")
    
    def test_mongodb(self):
        """测试 MongoDB 连接"""
        self.print_header("MongoDB 连接测试")
        
        try:
            client = pymongo.MongoClient(self.mongodb_url, serverSelectionTimeoutMS=5000)
            
            # 测试连接
            client.admin.command('hello')
            self.print_result("MongoDB 连接", True, "连接成功")
            
            # 测试数据库操作
            db = client.tradingagents
            test_collection = db.test_collection
            
            # 插入测试数据
            test_doc = {"test": "data", "timestamp": datetime.now()}
            result = test_collection.insert_one(test_doc)
            self.print_result("数据插入", True, f"ID: {result.inserted_id}")
            
            # 查询测试数据
            found_doc = test_collection.find_one({"_id": result.inserted_id})
            self.print_result("数据查询", found_doc is not None, "查询成功")
            
            # 删除测试数据
            test_collection.delete_one({"_id": result.inserted_id})
            self.print_result("数据删除", True, "删除成功")
            
            client.close()
            return True
            
        except Exception as e:
            self.print_result("MongoDB 连接", False, f"错误: {e}")
            return False
    
    def test_redis(self):
        """测试 Redis 连接"""
        self.print_header("Redis 连接测试")
        
        try:
            r = redis.from_url(self.redis_url, socket_timeout=5)
            
            # 测试连接
            pong = r.ping()
            self.print_result("Redis 连接", pong, "PONG 响应正常")
            
            # 测试数据操作
            test_key = "test:key"
            test_value = "test_value"
            
            # 设置值
            r.set(test_key, test_value, ex=60)
            self.print_result("数据设置", True, f"设置 {test_key}")
            
            # 获取值
            retrieved_value = r.get(test_key)
            success = retrieved_value.decode() == test_value if retrieved_value else False
            self.print_result("数据获取", success, f"获取 {retrieved_value}")
            
            # 删除值
            r.delete(test_key)
            self.print_result("数据删除", True, "删除成功")
            
            return True
            
        except Exception as e:
            self.print_result("Redis 连接", False, f"错误: {e}")
            return False
    
    async def test_http_services(self):
        """测试 HTTP 服务"""
        self.print_header("HTTP 服务测试")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for service_name, base_url in self.services.items():
                try:
                    # 测试健康检查
                    health_url = f"{base_url}/health"
                    response = await client.get(health_url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        service_status = data.get("status", "unknown")
                        self.print_result(f"{service_name} 健康检查", True, f"状态: {service_status}")
                        
                        # 测试根路径
                        try:
                            root_response = await client.get(base_url)
                            if root_response.status_code in [200, 404]:  # 404 也算正常，说明服务在运行
                                self.print_result(f"{service_name} 根路径", True, f"HTTP {root_response.status_code}")
                            else:
                                self.print_result(f"{service_name} 根路径", False, f"HTTP {root_response.status_code}")
                        except Exception as e:
                            self.print_result(f"{service_name} 根路径", False, f"错误: {e}")
                    else:
                        self.print_result(f"{service_name} 健康检查", False, f"HTTP {response.status_code}")
                        
                except Exception as e:
                    self.print_result(f"{service_name} 连接", False, f"错误: {e}")
    
    async def test_api_functionality(self):
        """测试 API 功能"""
        self.print_header("API 功能测试")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 测试 API Gateway
            try:
                # 测试配置接口
                config_url = "http://localhost:8000/api/config/status"
                response = await client.get(config_url)
                
                if response.status_code == 200:
                    self.print_result("配置状态接口", True, "响应正常")
                else:
                    self.print_result("配置状态接口", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.print_result("配置状态接口", False, f"错误: {e}")
            
            # 测试股票信息接口（如果 data-service 运行）
            try:
                stock_url = "http://localhost:8000/api/stock/info/000858"
                response = await client.get(stock_url)
                
                if response.status_code == 200:
                    data = response.json()
                    stock_name = data.get("name", "未知")
                    self.print_result("股票信息接口", True, f"股票: {stock_name}")
                else:
                    self.print_result("股票信息接口", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.print_result("股票信息接口", False, f"错误: {e}")
    
    def test_environment(self):
        """测试环境配置"""
        self.print_header("环境配置测试")
        
        # 检查 Python 版本
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        python_ok = sys.version_info >= (3, 10)
        self.print_result("Python 版本", python_ok, f"v{python_version}")
        
        # 检查环境变量
        env_vars = [
            "PYTHONPATH",
            "MONGODB_URL", 
            "REDIS_URL",
            "DASHSCOPE_API_KEY",
            "TUSHARE_TOKEN"
        ]
        
        for var in env_vars:
            value = os.environ.get(var, "")
            configured = bool(value and "your_" not in value)
            status = "已配置" if configured else "未配置"
            self.print_result(f"环境变量 {var}", configured, status)
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🔍 TradingAgents 系统测试")
        print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 环境测试
        self.test_environment()
        
        # 数据库测试
        mongodb_ok = self.test_mongodb()
        redis_ok = self.test_redis()
        
        # HTTP 服务测试
        await self.test_http_services()
        
        # API 功能测试
        if mongodb_ok and redis_ok:
            await self.test_api_functionality()
        else:
            print("\n⚠️ 跳过 API 功能测试（数据库连接失败）")
        
        # 总结
        self.print_header("测试总结")
        print("✅ 基础服务测试完成")
        print("📋 如果有失败项目，请检查：")
        print("   1. Docker 服务是否正常运行")
        print("   2. 应用服务是否已启动")
        print("   3. 环境变量是否正确配置")
        print("   4. 网络连接是否正常")
        
        print(f"\n📚 详细说明请查看: LOCAL_DEVELOPMENT.md")

async def main():
    """主函数"""
    tester = SystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
