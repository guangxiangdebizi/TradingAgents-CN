#!/usr/bin/env python3
"""
调试数据同步任务的测试脚本
"""

import asyncio
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any

class DataSyncDebugger:
    """数据同步调试器"""
    
    def __init__(self):
        self.data_service_url = "http://localhost:8002"
        self.task_scheduler_url = "http://localhost:8003"
        
    def test_data_service_health(self):
        """测试 Data Service 健康状态"""
        print("🔍 测试 Data Service 健康状态...")
        try:
            response = requests.get(f"{self.data_service_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Data Service 健康: {data}")
                return True
            else:
                print(f"❌ Data Service 不健康: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Data Service 连接失败: {e}")
            return False
    
    def test_task_scheduler_health(self):
        """测试 Task Scheduler 健康状态"""
        print("🔍 测试 Task Scheduler 健康状态...")
        try:
            response = requests.get(f"{self.task_scheduler_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Task Scheduler 健康: {data}")
                return True
            else:
                print(f"❌ Task Scheduler 不健康: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Task Scheduler 连接失败: {e}")
            return False
    
    def test_single_stock_data(self, symbol: str = "000858"):
        """测试单只股票数据获取"""
        print(f"📊 测试单只股票数据获取: {symbol}")
        
        try:
            # 测试股票信息
            response = requests.get(f"{self.data_service_url}/api/stock/info/{symbol}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 股票信息获取成功: {data.get('message', 'N/A')}")
            else:
                print(f"❌ 股票信息获取失败: HTTP {response.status_code}")
                print(f"   响应: {response.text}")
            
            # 测试股票数据
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            response = requests.post(f"{self.data_service_url}/api/stock/data", json={
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 股票数据获取成功: {data.get('message', 'N/A')}")
            else:
                print(f"❌ 股票数据获取失败: HTTP {response.status_code}")
                print(f"   响应: {response.text}")
                
        except Exception as e:
            print(f"❌ 测试股票数据失败: {e}")
    
    def test_batch_update_api(self):
        """测试批量更新 API"""
        print("🔄 测试批量更新 API...")
        
        try:
            # 准备测试数据
            test_data = {
                "symbols": ["000858", "000001"],
                "data_types": ["stock_info"],
                "start_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d")
            }
            
            response = requests.post(
                f"{self.data_service_url}/api/admin/batch-update",
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 批量更新成功: {data.get('message', 'N/A')}")
                if data.get('success') and 'data' in data:
                    summary = data['data'].get('summary', {})
                    print(f"   成功: {summary.get('successful', 0)}, 失败: {summary.get('failed', 0)}")
            else:
                print(f"❌ 批量更新失败: HTTP {response.status_code}")
                print(f"   响应: {response.text}")
                
        except Exception as e:
            print(f"❌ 测试批量更新失败: {e}")
    
    def trigger_manual_task(self, task_type: str = "sync-daily"):
        """手动触发任务"""
        print(f"⚡ 手动触发任务: {task_type}")
        
        try:
            if task_type == "sync-daily":
                response = requests.post(f"{self.task_scheduler_url}/api/tasks/data/sync-daily", json={
                    "symbols": ["000858", "000001"],
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
            elif task_type == "hot-stocks":
                response = requests.post(f"{self.task_scheduler_url}/api/tasks/data/update-hot-stocks")
            elif task_type == "custom-update":
                response = requests.post(f"{self.task_scheduler_url}/api/tasks/data/custom-update", json={
                    "symbols": ["000858"],
                    "data_types": ["stock_info", "stock_data"],
                    "start_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                    "end_date": datetime.now().strftime("%Y-%m-%d")
                })
            else:
                print(f"❌ 未知任务类型: {task_type}")
                return None
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get('data', {}).get('task_id')
                print(f"✅ 任务触发成功: {data.get('data', {}).get('message', 'N/A')}")
                print(f"   任务ID: {task_id}")
                return task_id
            else:
                print(f"❌ 任务触发失败: HTTP {response.status_code}")
                print(f"   响应: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 触发任务失败: {e}")
            return None
    
    def check_task_status(self, task_id: str):
        """检查任务状态"""
        print(f"📋 检查任务状态: {task_id}")
        
        try:
            response = requests.get(f"{self.task_scheduler_url}/api/tasks/{task_id}/result")
            if response.status_code == 200:
                data = response.json()
                task_data = data.get('data', {})
                status = task_data.get('status', 'UNKNOWN')
                result = task_data.get('result')
                
                print(f"   状态: {status}")
                if result:
                    print(f"   结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                return status
            else:
                print(f"❌ 获取任务状态失败: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 检查任务状态失败: {e}")
            return None
    
    def monitor_task(self, task_id: str, max_wait: int = 60):
        """监控任务执行"""
        print(f"👀 监控任务执行: {task_id} (最大等待 {max_wait} 秒)")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            status = self.check_task_status(task_id)
            
            if status in ['SUCCESS', 'FAILURE', 'REVOKED']:
                print(f"🏁 任务完成: {status}")
                break
            elif status == 'PENDING':
                print("⏳ 任务等待中...")
            elif status == 'PROGRESS':
                print("🔄 任务执行中...")
            else:
                print(f"❓ 未知状态: {status}")
            
            time.sleep(3)
        else:
            print("⏰ 监控超时")
    
    def test_data_statistics(self):
        """测试数据统计"""
        print("📊 测试数据统计...")
        
        try:
            response = requests.get(f"{self.data_service_url}/api/admin/statistics")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats = data.get('data', {})
                    print("✅ 数据统计:")
                    for key, value in stats.items():
                        print(f"   {key}: {value}")
                else:
                    print(f"❌ 获取统计失败: {data.get('message', 'Unknown error')}")
            else:
                print(f"❌ 获取统计失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试数据统计失败: {e}")
    
    def run_full_debug(self):
        """运行完整调试流程"""
        print("🚀 开始完整调试流程")
        print("=" * 50)
        
        # 1. 健康检查
        if not self.test_data_service_health():
            print("❌ Data Service 不可用，请先启动服务")
            return
        
        if not self.test_task_scheduler_health():
            print("❌ Task Scheduler 不可用，请先启动服务")
            return
        
        # 2. 测试单只股票数据
        self.test_single_stock_data("000858")
        
        # 3. 测试批量更新 API
        self.test_batch_update_api()
        
        # 4. 测试数据统计
        self.test_data_statistics()
        
        # 5. 手动触发任务并监控
        print("\n" + "=" * 50)
        print("🔄 测试手动任务触发")
        
        task_id = self.trigger_manual_task("custom-update")
        if task_id:
            self.monitor_task(task_id, max_wait=120)
        
        print("\n✅ 调试流程完成！")


def main():
    """主函数"""
    debugger = DataSyncDebugger()
    
    print("🔧 TradingAgents 数据同步调试工具")
    print("=" * 50)
    
    while True:
        print("\n请选择调试选项:")
        print("1. 运行完整调试流程")
        print("2. 测试服务健康状态")
        print("3. 测试单只股票数据")
        print("4. 测试批量更新 API")
        print("5. 手动触发每日同步任务")
        print("6. 手动触发热门股票更新")
        print("7. 手动触发自定义更新")
        print("8. 检查任务状态")
        print("9. 测试数据统计")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-9): ").strip()
        
        if choice == "1":
            debugger.run_full_debug()
        elif choice == "2":
            debugger.test_data_service_health()
            debugger.test_task_scheduler_health()
        elif choice == "3":
            symbol = input("请输入股票代码 (默认 000858): ").strip() or "000858"
            debugger.test_single_stock_data(symbol)
        elif choice == "4":
            debugger.test_batch_update_api()
        elif choice == "5":
            task_id = debugger.trigger_manual_task("sync-daily")
            if task_id:
                debugger.monitor_task(task_id)
        elif choice == "6":
            task_id = debugger.trigger_manual_task("hot-stocks")
            if task_id:
                debugger.monitor_task(task_id)
        elif choice == "7":
            task_id = debugger.trigger_manual_task("custom-update")
            if task_id:
                debugger.monitor_task(task_id)
        elif choice == "8":
            task_id = input("请输入任务ID: ").strip()
            if task_id:
                debugger.check_task_status(task_id)
        elif choice == "9":
            debugger.test_data_statistics()
        elif choice == "0":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选项，请重新选择")


if __name__ == "__main__":
    main()
