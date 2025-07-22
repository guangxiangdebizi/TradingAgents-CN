#!/usr/bin/env python3
"""
Celery 任务监控脚本
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from backend.task_scheduler.tasks.celery_app import celery_app
except ImportError:
    print("❌ 无法导入 Celery 应用，请检查路径和依赖")
    sys.exit(1)

class CeleryMonitor:
    """Celery 监控器"""
    
    def __init__(self):
        self.celery_app = celery_app
    
    def get_worker_stats(self):
        """获取 Worker 统计信息"""
        try:
            inspect = self.celery_app.control.inspect()
            
            # 获取活跃的 workers
            active_workers = inspect.active()
            scheduled_tasks = inspect.scheduled()
            reserved_tasks = inspect.reserved()
            stats = inspect.stats()
            
            return {
                "active_workers": active_workers,
                "scheduled_tasks": scheduled_tasks,
                "reserved_tasks": reserved_tasks,
                "stats": stats
            }
        except Exception as e:
            print(f"❌ 获取 Worker 统计失败: {e}")
            return None
    
    def get_task_info(self, task_id: str):
        """获取任务信息"""
        try:
            result = self.celery_app.AsyncResult(task_id)
            return {
                "task_id": task_id,
                "status": result.status,
                "result": result.result,
                "traceback": result.traceback,
                "date_done": result.date_done.isoformat() if result.date_done else None
            }
        except Exception as e:
            print(f"❌ 获取任务信息失败: {e}")
            return None
    
    def list_registered_tasks(self):
        """列出已注册的任务"""
        try:
            inspect = self.celery_app.control.inspect()
            registered = inspect.registered()
            return registered
        except Exception as e:
            print(f"❌ 获取已注册任务失败: {e}")
            return None
    
    def show_worker_status(self):
        """显示 Worker 状态"""
        print("🔍 Worker 状态检查")
        print("=" * 50)
        
        stats = self.get_worker_stats()
        if not stats:
            print("❌ 无法获取 Worker 状态")
            return
        
        # 显示活跃 Workers
        active_workers = stats.get("active_workers", {})
        if active_workers:
            print(f"✅ 活跃 Workers: {len(active_workers)}")
            for worker, tasks in active_workers.items():
                print(f"   📋 {worker}: {len(tasks)} 个活跃任务")
                for task in tasks:
                    print(f"      - {task['name']} ({task['id'][:8]}...)")
        else:
            print("⚠️ 没有活跃的 Workers")
        
        # 显示预定任务
        scheduled_tasks = stats.get("scheduled_tasks", {})
        if scheduled_tasks:
            print(f"\n⏰ 预定任务:")
            for worker, tasks in scheduled_tasks.items():
                if tasks:
                    print(f"   📋 {worker}: {len(tasks)} 个预定任务")
        
        # 显示 Worker 统计
        worker_stats = stats.get("stats", {})
        if worker_stats:
            print(f"\n📊 Worker 统计:")
            for worker, stat in worker_stats.items():
                print(f"   📋 {worker}:")
                print(f"      - 总任务数: {stat.get('total', 'N/A')}")
                print(f"      - 进程池: {stat.get('pool', {}).get('max-concurrency', 'N/A')}")
    
    def show_registered_tasks(self):
        """显示已注册的任务"""
        print("📋 已注册的任务")
        print("=" * 50)
        
        registered = self.list_registered_tasks()
        if not registered:
            print("❌ 无法获取已注册任务")
            return
        
        for worker, tasks in registered.items():
            print(f"📋 {worker}:")
            for task in sorted(tasks):
                print(f"   - {task}")
    
    def monitor_tasks(self, interval: int = 5):
        """持续监控任务"""
        print(f"👀 开始监控任务 (每 {interval} 秒刷新)")
        print("按 Ctrl+C 停止监控")
        print("=" * 50)
        
        try:
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')
                print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.show_worker_status()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n⏹️ 监控已停止")
    
    def test_task_submission(self):
        """测试任务提交"""
        print("🧪 测试任务提交")
        print("=" * 50)
        
        try:
            # 测试提交一个简单的数据任务
            from backend.task_scheduler.tasks.data_tasks import update_hot_stocks_data
            
            print("📤 提交测试任务: update_hot_stocks_data")
            result = update_hot_stocks_data.delay()
            
            print(f"✅ 任务已提交: {result.id}")
            print("⏳ 等待任务完成...")
            
            # 监控任务状态
            for i in range(30):  # 最多等待30秒
                status = result.status
                print(f"   状态: {status}")
                
                if status in ['SUCCESS', 'FAILURE', 'REVOKED']:
                    break
                
                time.sleep(1)
            
            if result.ready():
                print(f"🏁 任务完成: {result.status}")
                if result.successful():
                    print(f"📊 结果: {result.result}")
                else:
                    print(f"❌ 错误: {result.traceback}")
            else:
                print("⏰ 任务仍在执行中")
                
        except Exception as e:
            print(f"❌ 测试任务提交失败: {e}")


def main():
    """主函数"""
    monitor = CeleryMonitor()
    
    print("🔧 Celery 任务监控工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 显示 Worker 状态")
        print("2. 显示已注册任务")
        print("3. 持续监控任务")
        print("4. 测试任务提交")
        print("5. 查询特定任务状态")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-5): ").strip()
        
        if choice == "1":
            monitor.show_worker_status()
        elif choice == "2":
            monitor.show_registered_tasks()
        elif choice == "3":
            interval = input("监控间隔 (秒，默认5): ").strip()
            interval = int(interval) if interval.isdigit() else 5
            monitor.monitor_tasks(interval)
        elif choice == "4":
            monitor.test_task_submission()
        elif choice == "5":
            task_id = input("请输入任务ID: ").strip()
            if task_id:
                info = monitor.get_task_info(task_id)
                if info:
                    print(f"📋 任务信息:")
                    print(json.dumps(info, indent=2, ensure_ascii=False))
        elif choice == "0":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选项，请重新选择")


if __name__ == "__main__":
    main()
