#!/usr/bin/env python3
"""
测试Analysis Engine的详细日志输出
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'analysis-engine'))

async def test_detailed_logging():
    """测试详细的分析日志"""
    print("🔄 测试Analysis Engine详细日志输出...")
    
    try:
        # 导入TradingGraph
        from app.graphs.trading_graph import TradingGraph
        
        # 创建图实例
        graph = TradingGraph()
        
        # 初始化图
        print("🔧 初始化图引擎...")
        await graph.initialize()
        
        # 创建进度回调
        async def progress_callback(step: str, progress: int, message: str):
            print(f"📊 进度回调: [{progress}%] {step}: {message}")
        
        # 执行分析
        print("🚀 开始执行股票分析...")
        result = await graph.analyze_stock(
            symbol="000002",
            analysis_date="2025-07-25",
            progress_callback=progress_callback
        )
        
        print(f"✅ 分析完成，结果: {result}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_detailed_logging())
