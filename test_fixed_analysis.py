#!/usr/bin/env python3
"""
测试修复后的Analysis Engine
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'analysis-engine'))

async def test_fixed_analysis():
    """测试修复后的分析功能"""
    print("🔄 测试修复后的Analysis Engine...")
    
    try:
        # 导入TradingGraph
        from app.graphs.trading_graph import TradingGraph
        
        # 创建图实例
        graph = TradingGraph()
        
        # 初始化图
        print("🔧 初始化图引擎...")
        await graph.initialize()
        print("✅ 图引擎初始化完成")
        
        # 创建进度回调
        async def progress_callback(step: str, progress: int, message: str):
            print(f"📊 进度: [{progress}%] {step}: {message}")
        
        # 执行分析
        print("🚀 开始执行股票分析...")
        result = await graph.analyze_stock(
            symbol="000001",
            analysis_date="2025-07-25",
            progress_callback=progress_callback
        )
        
        print(f"✅ 分析完成")
        print(f"📊 结果类型: {type(result)}")
        print(f"📋 结果概要: {str(result)[:200]}...")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fixed_analysis())
