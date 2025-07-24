#!/usr/bin/env python3
"""
Backend Trading CLI Client 使用示例
"""

import asyncio
import json
from datetime import datetime
from trading_cli import BackendClient, TradingCLI
from config import ConfigManager, HistoryManager, PresetManager

# 示例1: 基本使用
async def example_basic_usage():
    """基本使用示例"""
    print("🔍 示例1: 基本使用")
    
    async with BackendClient() as client:
        # 检查服务健康状态
        health = await client.health_check()
        print(f"服务状态: {health}")
        
        # 启动分析
        result = await client.start_analysis("000001")
        if result.get("success"):
            analysis_id = result["data"]["analysis_id"]
            print(f"分析已启动: {analysis_id}")
            
            # 等待分析完成 (简化版本)
            while True:
                status = await client.get_analysis_status(analysis_id)
                if status["data"]["status"] == "completed":
                    break
                elif status["data"]["status"] == "failed":
                    print("分析失败")
                    return
                
                await asyncio.sleep(2)
            
            # 获取结果
            result = await client.get_analysis_result(analysis_id)
            print(f"分析结果: {result['data']['result']['final_recommendation']}")

# 示例2: 批量分析
async def example_batch_analysis():
    """批量分析示例"""
    print("📊 示例2: 批量分析")
    
    symbols = ["000001", "000002", "600036", "600519"]
    
    async with BackendClient() as client:
        # 启动所有分析
        analysis_tasks = {}
        for symbol in symbols:
            result = await client.start_analysis(symbol)
            if result.get("success"):
                analysis_id = result["data"]["analysis_id"]
                analysis_tasks[symbol] = analysis_id
                print(f"✅ {symbol} 分析已启动: {analysis_id}")
        
        # 监控所有分析进度
        completed = set()
        while len(completed) < len(analysis_tasks):
            for symbol, analysis_id in analysis_tasks.items():
                if symbol in completed:
                    continue
                
                status = await client.get_analysis_status(analysis_id)
                current_status = status["data"]["status"]
                
                if current_status == "completed":
                    completed.add(symbol)
                    print(f"✅ {symbol} 分析完成")
                    
                    # 获取结果
                    result = await client.get_analysis_result(analysis_id)
                    recommendation = result["data"]["result"]["final_recommendation"]
                    print(f"   推荐: {recommendation['action']} (置信度: {recommendation['confidence']:.2%})")
                
                elif current_status == "failed":
                    completed.add(symbol)
                    print(f"❌ {symbol} 分析失败")
            
            await asyncio.sleep(3)

# 示例3: 自定义配置
async def example_custom_config():
    """自定义配置示例"""
    print("⚙️ 示例3: 自定义配置")
    
    # 创建自定义配置
    config_manager = ConfigManager()
    
    # 更新配置
    config_manager.update_config(
        backend_url="http://localhost:8001",
        max_debate_rounds=5,  # 增加辩论轮数
        max_risk_rounds=3,    # 增加风险分析轮数
        refresh_interval=1    # 更频繁的刷新
    )
    
    print(f"当前配置: {config_manager.get_config().dict()}")
    
    # 使用自定义配置进行分析
    async with BackendClient(config_manager.config.backend_url) as client:
        result = await client.start_analysis(
            "000001",
            analysis_type="comprehensive"
        )
        
        if result.get("success"):
            print(f"使用自定义配置启动分析: {result['data']['analysis_id']}")

# 示例4: 预设模式
def example_presets():
    """预设模式示例"""
    print("🎛️ 示例4: 预设模式")
    
    config_manager = ConfigManager()
    preset_manager = PresetManager()
    
    # 列出所有预设
    presets = preset_manager.list_presets()
    print(f"可用预设: {presets}")
    
    # 应用不同预设
    for preset_name in ["quick", "standard", "detailed"]:
        print(f"\n应用预设: {preset_name}")
        preset_manager.apply_preset(config_manager, preset_name)
        
        config = config_manager.get_config()
        print(f"  辩论轮数: {config.max_debate_rounds}")
        print(f"  风险轮数: {config.max_risk_rounds}")
        print(f"  刷新间隔: {config.refresh_interval}秒")

# 示例5: 历史记录管理
def example_history_management():
    """历史记录管理示例"""
    print("📝 示例5: 历史记录管理")
    
    history_manager = HistoryManager()
    
    # 添加一些示例记录
    history_manager.add_analysis("000001", "uuid-1", "completed")
    history_manager.add_analysis("000002", "uuid-2", "running")
    history_manager.add_analysis("000001", "uuid-3", "failed")
    
    # 获取最近的分析
    recent = history_manager.get_recent_analyses(5)
    print(f"最近分析: {len(recent)}条")
    for record in recent:
        print(f"  {record['symbol']} - {record['status']} ({record['start_time']})")
    
    # 获取特定股票的分析历史
    symbol_history = history_manager.get_analysis_by_symbol("000001")
    print(f"\n000001的分析历史: {len(symbol_history)}条")
    for record in symbol_history:
        print(f"  {record['analysis_id']} - {record['status']}")

# 示例6: 错误处理
async def example_error_handling():
    """错误处理示例"""
    print("🚨 示例6: 错误处理")
    
    # 使用错误的URL测试连接失败
    async with BackendClient("http://invalid-url:9999") as client:
        try:
            health = await client.health_check()
            if not health.get("success"):
                print(f"连接失败: {health.get('error')}")
        except Exception as e:
            print(f"异常: {e}")
    
    # 测试无效的分析ID
    async with BackendClient() as client:
        try:
            result = await client.get_analysis_status("invalid-uuid")
            if not result.get("success"):
                print(f"获取状态失败: {result.get('error')}")
        except Exception as e:
            print(f"异常: {e}")

# 示例7: 实时监控
async def example_real_time_monitoring():
    """实时监控示例"""
    print("📡 示例7: 实时监控")
    
    async with BackendClient() as client:
        # 启动分析
        result = await client.start_analysis("000001")
        if not result.get("success"):
            print("启动分析失败")
            return
        
        analysis_id = result["data"]["analysis_id"]
        print(f"开始监控分析: {analysis_id}")
        
        start_time = datetime.now()
        last_step = ""
        
        while True:
            status = await client.get_analysis_status(analysis_id)
            if not status.get("success"):
                print("获取状态失败")
                break
            
            data = status["data"]
            current_status = data["status"]
            current_step = data.get("current_step", "unknown")
            
            # 显示进度变化
            if current_step != last_step:
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"[{elapsed:.1f}s] 步骤变更: {last_step} → {current_step}")
                last_step = current_step
            
            # 显示辩论状态
            if "debate_status" in data:
                debate = data["debate_status"]
                print(f"  🗣️ 辩论: 第{debate['current_round']}/{debate['max_rounds']}轮, 发言者: {debate['current_speaker']}")
            
            # 显示进度
            if "progress" in data:
                progress = data["progress"]
                print(f"  📊 进度: {progress['percentage']:.1f}% ({progress['completed_steps']}/{progress['total_steps']})")
            
            # 检查完成状态
            if current_status in ["completed", "failed"]:
                print(f"分析{current_status}: {analysis_id}")
                break
            
            await asyncio.sleep(2)

# 示例8: 结果分析和导出
async def example_result_analysis():
    """结果分析和导出示例"""
    print("📈 示例8: 结果分析和导出")
    
    async with BackendClient() as client:
        # 假设我们有一个已完成的分析ID
        # 在实际使用中，这应该是真实的分析ID
        analysis_id = "example-completed-analysis"
        
        try:
            result = await client.get_analysis_result(analysis_id)
            if result.get("success"):
                data = result["data"]["result"]
                
                # 分析结果
                print("📊 分析结果摘要:")
                
                if "final_recommendation" in data:
                    rec = data["final_recommendation"]
                    print(f"  推荐动作: {rec.get('action', 'N/A')}")
                    print(f"  置信度: {rec.get('confidence', 0):.2%}")
                    print(f"  目标价格: {rec.get('target_price', 'N/A')}")
                
                if "risk_assessment" in data:
                    risk = data["risk_assessment"]
                    print(f"  风险等级: {risk.get('risk_level', 'N/A')}")
                    print(f"  风险分数: {risk.get('risk_score', 0):.2f}")
                
                if "debate_summary" in data:
                    debate = data["debate_summary"]
                    print(f"  辩论轮数: {debate.get('total_rounds', 0)}")
                    print(f"  达成共识: {'是' if debate.get('consensus_reached') else '否'}")
                
                # 导出结果
                export_data = {
                    "analysis_id": analysis_id,
                    "timestamp": datetime.now().isoformat(),
                    "result": data
                }
                
                with open(f"analysis_result_{analysis_id}.json", "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                print(f"结果已导出到: analysis_result_{analysis_id}.json")
                
        except Exception as e:
            print(f"获取结果失败: {e}")

# 示例9: 交互式CLI模拟
async def example_interactive_simulation():
    """交互式CLI模拟示例"""
    print("🎮 示例9: 交互式CLI模拟")
    
    # 模拟用户命令序列
    commands = [
        "health",
        "analyze 000001",
        "config",
        "set max_debate_rounds 5",
        "analyze 000002"
    ]
    
    cli = TradingCLI()
    
    for command in commands:
        print(f"\n> {command}")
        
        # 这里只是演示命令解析，实际的CLI会有完整的命令处理
        parts = command.split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == "health":
            health_ok = await cli.check_backend_health()
            print(f"健康检查: {'✅' if health_ok else '❌'}")
        
        elif cmd == "analyze":
            if args:
                print(f"启动分析: {args[0]}")
                # 在实际CLI中会调用 cli.analyze_stock(args[0])
        
        elif cmd == "config":
            print("显示配置...")
            # 在实际CLI中会调用 cli.display_config()
        
        elif cmd == "set":
            if len(args) >= 2:
                key, value = args[0], args[1]
                print(f"设置配置: {key} = {value}")
                # 在实际CLI中会更新配置

# 主函数
async def main():
    """运行所有示例"""
    print("🚀 Backend Trading CLI Client 使用示例\n")
    
    examples = [
        ("基本使用", example_basic_usage),
        ("批量分析", example_batch_analysis),
        ("自定义配置", example_custom_config),
        ("预设模式", example_presets),
        ("历史记录管理", example_history_management),
        ("错误处理", example_error_handling),
        ("实时监控", example_real_time_monitoring),
        ("结果分析和导出", example_result_analysis),
        ("交互式CLI模拟", example_interactive_simulation)
    ]
    
    for name, example_func in examples:
        print(f"\n{'='*50}")
        print(f"运行示例: {name}")
        print('='*50)
        
        try:
            if asyncio.iscoroutinefunction(example_func):
                await example_func()
            else:
                example_func()
        except Exception as e:
            print(f"❌ 示例执行失败: {e}")
        
        print(f"\n示例 '{name}' 完成")

if __name__ == "__main__":
    # 运行所有示例
    asyncio.run(main())
    
    print("\n🎉 所有示例运行完成!")
    print("\n💡 提示:")
    print("  - 这些示例展示了CLI客户端的各种使用方式")
    print("  - 在实际使用中，请确保Backend服务正在运行")
    print("  - 可以根据需要修改配置和参数")
    print("  - 更多详细信息请参考README.md")
