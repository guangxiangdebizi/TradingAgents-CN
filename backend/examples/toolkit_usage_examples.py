#!/usr/bin/env python3
"""
Backend工具链使用示例
展示各种工具调用方式和最佳实践
"""

import asyncio
import logging
from datetime import datetime, timedelta

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def example_basic_toolkit():
    """基础工具链使用示例"""
    print("🔧 基础工具链使用示例")
    print("=" * 50)
    
    from backend.analysis_engine.app.tools import ToolkitManager
    
    # 初始化工具管理器
    toolkit = ToolkitManager()
    await toolkit.initialize()
    
    # 获取可用工具列表
    tools = await toolkit.get_available_tools()
    print(f"📋 可用工具数量: {len(tools)}")
    
    # 调用股票数据工具
    result = await toolkit.call_tool(
        tool_name="get_stock_data",
        parameters={"symbol": "000001", "period": "1y"}
    )
    
    if result["success"]:
        print("✅ 股票数据获取成功")
        print(f"⏱️ 耗时: {result['duration']:.2f}秒")
    else:
        print(f"❌ 股票数据获取失败: {result['error']}")
    
    # 清理资源
    await toolkit.cleanup()

async def example_llm_toolkit():
    """LLM集成工具链使用示例"""
    print("\n🤖 LLM集成工具链使用示例")
    print("=" * 50)
    
    from backend.analysis_engine.app.tools import LLMToolkitManager
    
    # 初始化LLM工具管理器
    llm_toolkit = LLMToolkitManager()
    await llm_toolkit.initialize()
    
    # 获取OpenAI Function格式的工具
    openai_functions = await llm_toolkit.get_openai_functions(category="unified")
    print(f"📋 OpenAI Function工具数量: {len(openai_functions)}")
    
    # 模拟LLM返回的函数调用
    function_call = {
        "name": "get_stock_market_data_unified",
        "arguments": '{"ticker": "000001", "start_date": "2024-01-01", "end_date": "2024-12-31"}'
    }
    
    # 调用LLM工具
    result = await llm_toolkit.call_llm_tool(function_call)
    
    if result["success"]:
        print("✅ LLM工具调用成功")
        print(f"⏱️ 耗时: {result['duration']:.2f}秒")
        print(f"📄 结果长度: {len(result['result'])}字符")
    else:
        print(f"❌ LLM工具调用失败: {result['error']}")
    
    # 获取任务推荐工具
    task_tools = await llm_toolkit.get_tools_for_task("stock_analysis")
    print(f"📊 股票分析推荐工具数量: {len(task_tools)}")
    
    # 清理资源
    await llm_toolkit.cleanup()

async def example_unified_tools():
    """统一工具使用示例"""
    print("\n⭐ 统一工具使用示例")
    print("=" * 50)
    
    from backend.analysis_engine.app.tools import UnifiedTools
    
    # 初始化统一工具
    unified_tools = UnifiedTools()
    await unified_tools.initialize()
    
    # 测试不同市场的股票
    test_stocks = [
        ("000001", "A股"),
        ("0700.HK", "港股"),
        ("AAPL", "美股")
    ]
    
    for ticker, market_name in test_stocks:
        print(f"\n📈 分析 {ticker} ({market_name})")
        
        try:
            # 调用统一市场数据工具
            result = await unified_tools.get_stock_market_data_unified(
                ticker=ticker,
                start_date="2024-01-01",
                end_date="2024-12-31"
            )
            
            print(f"✅ {market_name}数据获取成功")
            print(f"📄 报告长度: {len(result)}字符")
            
            # 显示报告摘要
            lines = result.split('\n')[:10]
            print("📋 报告摘要:")
            for line in lines:
                if line.strip():
                    print(f"  {line}")
            
        except Exception as e:
            print(f"❌ {market_name}数据获取失败: {e}")
    
    # 清理资源
    await unified_tools.cleanup()

async def example_concurrent_calls():
    """并发工具调用示例"""
    print("\n🚀 并发工具调用示例")
    print("=" * 50)
    
    from backend.analysis_engine.app.tools import LLMToolkitManager
    
    # 初始化工具管理器
    toolkit = LLMToolkitManager()
    await toolkit.initialize()
    
    # 准备并发调用的任务
    tasks = []
    stocks = ["000001", "000002", "000858"]
    
    for stock in stocks:
        task = toolkit.call_tool(
            tool_name="get_stock_market_data_unified",
            parameters={
                "ticker": stock,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
        )
        tasks.append(task)
    
    # 并发执行
    start_time = datetime.now()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = datetime.now()
    
    # 统计结果
    success_count = 0
    total_duration = (end_time - start_time).total_seconds()
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"❌ {stocks[i]} 调用失败: {result}")
        elif result.get("success"):
            success_count += 1
            print(f"✅ {stocks[i]} 调用成功 (耗时: {result['duration']:.2f}s)")
        else:
            print(f"❌ {stocks[i]} 调用失败: {result.get('error')}")
    
    print(f"\n📊 并发调用统计:")
    print(f"  总任务数: {len(tasks)}")
    print(f"  成功数量: {success_count}")
    print(f"  总耗时: {total_duration:.2f}秒")
    print(f"  平均耗时: {total_duration/len(tasks):.2f}秒/任务")
    
    # 清理资源
    await toolkit.cleanup()

async def example_error_handling():
    """错误处理示例"""
    print("\n⚠️ 错误处理示例")
    print("=" * 50)
    
    from backend.analysis_engine.app.tools import ToolkitManager
    
    toolkit = ToolkitManager()
    await toolkit.initialize()
    
    # 测试不存在的工具
    try:
        result = await toolkit.call_tool(
            tool_name="non_existent_tool",
            parameters={}
        )
    except ValueError as e:
        print(f"✅ 正确捕获工具不存在错误: {e}")
    
    # 测试无效参数
    result = await toolkit.call_tool(
        tool_name="get_stock_data",
        parameters={"invalid_param": "value"}
    )
    
    if not result["success"]:
        print(f"✅ 正确处理无效参数: {result['error']}")
    
    # 测试网络超时等异常
    try:
        result = await toolkit.call_tool(
            tool_name="get_market_data",
            parameters={"symbol": "INVALID_SYMBOL", "indicators": ["RSI"]}
        )
        
        if not result["success"]:
            print(f"✅ 正确处理数据获取失败: {result['error']}")
    except Exception as e:
        print(f"✅ 正确捕获异常: {e}")
    
    await toolkit.cleanup()

async def example_logging_and_monitoring():
    """日志和监控示例"""
    print("\n📊 日志和监控示例")
    print("=" * 50)
    
    from backend.analysis_engine.app.tools.tool_logging import (
        log_tool_usage, log_analysis_start, log_analysis_complete
    )
    
    # 记录工具使用
    log_tool_usage("get_stock_data", symbol="000001", user_id="test_user")
    
    # 记录分析流程
    log_analysis_start("technical_analysis", "000001", analyst="test_analyst")
    
    # 模拟分析过程
    await asyncio.sleep(1)
    
    log_analysis_complete("technical_analysis", "000001", duration=1.0, status="success")
    
    print("✅ 日志记录完成，请查看日志输出")

async def example_custom_tool():
    """自定义工具示例"""
    print("\n🔧 自定义工具示例")
    print("=" * 50)
    
    from backend.analysis_engine.app.tools import ToolkitManager
    from backend.analysis_engine.app.tools.tool_logging import log_async_tool_call
    
    # 定义自定义工具
    @log_async_tool_call(tool_name="custom_analysis", log_args=True)
    async def custom_analysis_tool(symbol: str, method: str) -> dict:
        """自定义分析工具"""
        await asyncio.sleep(0.5)  # 模拟分析过程
        
        return {
            "symbol": symbol,
            "method": method,
            "result": f"使用{method}方法分析{symbol}的结果",
            "score": 85.5,
            "recommendation": "买入"
        }
    
    # 初始化工具管理器
    toolkit = ToolkitManager()
    await toolkit.initialize()
    
    # 注册自定义工具
    toolkit._register_tool(
        name="custom_analysis",
        description="自定义股票分析工具",
        category="analysis",
        parameters={"symbol": "str", "method": "str"},
        function=custom_analysis_tool
    )
    
    # 调用自定义工具
    result = await toolkit.call_tool(
        tool_name="custom_analysis",
        parameters={"symbol": "000001", "method": "技术分析"}
    )
    
    if result["success"]:
        print("✅ 自定义工具调用成功")
        print(f"📄 分析结果: {result['result']}")
    else:
        print(f"❌ 自定义工具调用失败: {result['error']}")
    
    await toolkit.cleanup()

async def main():
    """主函数 - 运行所有示例"""
    print("🎯 Backend工具链使用示例")
    print("=" * 60)
    
    examples = [
        example_basic_toolkit,
        example_llm_toolkit,
        example_unified_tools,
        example_concurrent_calls,
        example_error_handling,
        example_logging_and_monitoring,
        example_custom_tool
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            logger.error(f"示例执行失败: {example.__name__} - {e}")
        
        # 等待一下再执行下一个示例
        await asyncio.sleep(1)
    
    print("\n🎉 所有示例执行完成!")

if __name__ == "__main__":
    asyncio.run(main())
