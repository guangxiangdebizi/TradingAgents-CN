#!/usr/bin/env python3
"""
TradingAgents 测试运行器
提供多种测试选项
"""

import sys
import os
import argparse
import asyncio

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def run_quick_test():
    """运行快速测试"""
    from backend.tests.quick_api_test import main as quick_main
    quick_main()

async def run_integration_test():
    """运行集成测试"""
    from backend.tests.test_microservices_integration import main as integration_main
    await integration_main()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='TradingAgents 微服务测试运行器')
    parser.add_argument(
        '--type', 
        choices=['quick', 'integration', 'all'],
        default='quick',
        help='测试类型 (默认: quick)'
    )
    
    args = parser.parse_args()
    
    print("🧪 TradingAgents 微服务测试运行器")
    print("=" * 50)
    
    if args.type in ['quick', 'all']:
        print("\n🚀 运行快速 API 测试...")
        try:
            run_quick_test()
        except Exception as e:
            print(f"❌ 快速测试失败: {e}")
    
    if args.type in ['integration', 'all']:
        print("\n🔄 运行集成测试...")
        try:
            asyncio.run(run_integration_test())
        except Exception as e:
            print(f"❌ 集成测试失败: {e}")
    
    print("\n✅ 测试完成！")

if __name__ == "__main__":
    main()
