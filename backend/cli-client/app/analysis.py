"""
TradingAgents CLI Client - Analysis Execution
分析执行和监控模块
"""

import asyncio
import time
import json
from datetime import datetime as dt
from pathlib import Path
from typing import Dict, Any, List

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm
from rich import box

from .core import BackendClient, ui, console, AnalystType

async def run_analysis(symbol: str, market: str, analysis_date: str, selected_analysts: List[AnalystType],
                      max_debate_rounds: int, backend_url: str, llm_provider: Dict[str, Any],
                      llm_model: Dict[str, Any]):
    """运行分析 - 与TradingAgents的执行流程完全一致"""

    # 创建配置
    config = {
        "max_debate_rounds": max_debate_rounds,
        "max_risk_discuss_rounds": 2,
        "selected_analysts": [analyst.value for analyst in selected_analysts],
        "market": market,
        "analysis_date": analysis_date,
        "llm_provider": llm_provider.get("id"),
        "llm_model": llm_model.get("id"),
        "llm_config": {
            "provider": llm_provider,
            "model": llm_model
        }
    }
    
    ui.show_step_header(1, "连接API Gateway | Connecting to API Gateway")

    async with BackendClient(backend_url) as client:
        # 检查服务健康状态
        health = await client.health_check()
        # API Gateway返回格式: {"status": "healthy", ...} 或 {"success": False, "error": "..."}
        is_healthy = health.get("status") == "healthy" or health.get("success") == True
        if not is_healthy:
            ui.show_error(f"API Gateway连接失败: {health.get('error', 'Unknown error')}")
            ui.show_warning("这可能是因为:")
            ui.show_warning("  1. API Gateway服务未启动")
            ui.show_warning("  2. 端口配置错误 (应该是8000)")
            ui.show_warning("  3. 网络连接问题")
            ui.show_warning("  4. 防火墙阻止连接")

            # 提供解决建议
            console.print("\n[bold yellow]解决建议 | Troubleshooting:[/bold yellow]")
            console.print("1. 检查API Gateway是否运行:")
            console.print("   [dim]curl http://localhost:8000/health[/dim]")
            console.print("2. 检查Backend服务是否运行:")
            console.print("   [dim]curl http://localhost:8001/health[/dim]")
            console.print("3. 确认端口配置正确 (API Gateway: 8000)")
            console.print("4. 检查防火墙设置")

            from rich.prompt import Confirm
            if not Confirm.ask("\n是否继续尝试分析? | Continue with analysis anyway?", default=False):
                ui.show_warning("分析已取消 | Analysis cancelled")
                return

            ui.show_warning("继续分析，但可能会失败 | Continuing analysis, but it may fail")
        else:
            ui.show_success("API Gateway连接成功 | API Gateway connected successfully")
        
        ui.show_step_header(2, "启动分析 | Starting Analysis")
        ui.show_progress(f"正在为 {symbol} 启动综合分析...")
        
        # 启动分析
        result = await client.start_analysis(symbol, config)
        if not result.get("success"):
            ui.show_error(f"启动分析失败: {result.get('error', 'Unknown error')}")
            return
        
        analysis_id = result["data"]["analysis_id"]
        ui.show_success(f"分析已启动，ID: {analysis_id}")
        
        ui.show_step_header(3, "执行分析 | Executing Analysis")
        
        # 监控分析进度
        await monitor_analysis_progress(client, analysis_id)

async def monitor_analysis_progress(client: BackendClient, analysis_id: str):
    """监控分析进度 - 与TradingAgents的进度显示一致"""
    
    start_time = time.time()
    last_step = ""
    debate_round = 0
    risk_round = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=True
    ) as progress:
        
        task = progress.add_task("分析进行中...", total=100)
        
        while True:
            try:
                status_result = await client.get_analysis_status(analysis_id)
                
                if not status_result.get("success"):
                    ui.show_error(f"获取状态失败: {status_result.get('error')}")
                    break
                
                data = status_result["data"]
                current_status = data["status"]
                current_step = data.get("current_step", "unknown")
                
                # 更新进度条
                if "progress" in data:
                    percentage = data["progress"]["percentage"]
                    progress.update(task, completed=percentage, description=f"当前步骤: {current_step}")
                
                # 显示步骤变化
                if current_step != last_step and current_step != "unknown":
                    elapsed = time.time() - start_time
                    ui.show_progress(f"[{elapsed:.1f}s] 执行步骤: {current_step}")
                    last_step = current_step
                
                # 显示辩论进度 - 与TradingAgents一致
                if "debate_status" in data:
                    debate = data["debate_status"]
                    current_round = debate["current_round"]
                    if current_round != debate_round:
                        debate_round = current_round
                        speaker = debate["current_speaker"]
                        ui.show_progress(f"🗣️ 投资辩论 第{current_round}/{debate['max_rounds']}轮 - {speaker}")
                
                # 显示风险分析进度
                if "risk_status" in data:
                    risk = data["risk_status"]
                    current_round = risk["current_round"]
                    if current_round != risk_round:
                        risk_round = current_round
                        speaker = risk["current_speaker"]
                        ui.show_progress(f"⚠️ 风险分析 第{current_round}/{risk['max_rounds']}轮 - {speaker}")
                
                # 检查完成状态
                if current_status == "completed":
                    progress.update(task, completed=100, description="分析完成!")
                    ui.show_success("✅ 分析完成!")
                    
                    # 获取并显示结果
                    await display_analysis_results(client, analysis_id)
                    break
                    
                elif current_status == "failed":
                    ui.show_error("❌ 分析失败")
                    if "errors" in data and data["errors"]:
                        for error in data["errors"]:
                            ui.show_error(f"  • {error}")
                    break
                
                # 等待下次检查
                await asyncio.sleep(2)
                
            except Exception as e:
                # 判断是否为连接错误或超时错误
                if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
                    logger.critical(f"🚨 严重告警: 无法连接到Agent Service监控分析进度")
                    logger.critical(f"🚨 请检查Agent Service是否启动并可访问")
                    logger.critical(f"🚨 错误详情: {type(e).__name__}: {str(e)}")
                    ui.show_error(f"服务连接失败，无法监控分析进度: {e}")
                else:
                    ui.show_error(f"监控分析进度时发生错误: {e}")
                break

async def display_analysis_results(client: BackendClient, analysis_id: str):
    """显示分析结果 - 与TradingAgents的结果显示完全一致"""
    
    ui.show_step_header(4, "分析结果 | Analysis Results")
    
    try:
        result = await client.get_analysis_result(analysis_id)

        if not result.get("success"):
            ui.show_error(f"获取结果失败: {result.get('error')}")
            return

        # 检查数据结构并适配
        if "result" in result["data"]:
            data = result["data"]["result"]
        else:
            # 如果没有result键，直接使用data
            data = result["data"]
        
        # 显示最终投资建议
        if "final_recommendation" in data:
            rec = data["final_recommendation"]
            
            # 创建投资建议表格
            rec_table = Table(title="🎯 最终投资建议 | Final Investment Recommendation", box=box.ROUNDED)
            rec_table.add_column("项目 | Item", style="cyan", no_wrap=True)
            rec_table.add_column("值 | Value", style="white")
            
            rec_table.add_row("投资动作 | Action", rec.get('action', 'N/A'))
            rec_table.add_row("置信度 | Confidence", f"{rec.get('confidence', 0):.2%}")
            if rec.get('target_price'):
                rec_table.add_row("目标价格 | Target Price", str(rec.get('target_price')))
            rec_table.add_row("推理依据 | Reasoning", rec.get('reasoning', 'N/A'))
            
            console.print(rec_table)
        
        # 显示投资计划
        if "investment_plan" in data and data["investment_plan"]:
            plan_panel = Panel(
                data["investment_plan"],
                title="📋 投资计划 | Investment Plan",
                border_style="blue"
            )
            console.print(plan_panel)
        
        # 显示风险评估
        if "risk_assessment" in data:
            risk = data["risk_assessment"]
            
            risk_table = Table(title="⚠️ 风险评估 | Risk Assessment", box=box.ROUNDED)
            risk_table.add_column("风险项目 | Risk Item", style="yellow", no_wrap=True)
            risk_table.add_column("评估结果 | Assessment", style="white")
            
            risk_table.add_row("风险等级 | Risk Level", risk.get('risk_level', 'N/A'))
            risk_table.add_row("风险分数 | Risk Score", f"{risk.get('risk_score', 0):.2f}")
            if risk.get('key_risks'):
                risk_table.add_row("关键风险 | Key Risks", ', '.join(risk.get('key_risks', [])))
            
            console.print(risk_table)
        
        # 显示辩论摘要
        if "debate_summary" in data:
            debate = data["debate_summary"]
            
            debate_table = Table(title="🗣️ 辩论摘要 | Debate Summary", box=box.ROUNDED)
            debate_table.add_column("辩论项目 | Debate Item", style="green", no_wrap=True)
            debate_table.add_column("结果 | Result", style="white")
            
            debate_table.add_row("辩论轮数 | Total Rounds", str(debate.get('total_rounds', 0)))
            debate_table.add_row("达成共识 | Consensus Reached", '是 | Yes' if debate.get('consensus_reached') else '否 | No')
            debate_table.add_row("最终立场 | Final Stance", debate.get('final_stance', 'N/A'))
            
            console.print(debate_table)
        
        # 询问是否查看详细报告
        if Confirm.ask("是否查看详细分析报告? | View detailed analysis reports?"):
            await display_detailed_reports(data.get("reports", {}))
        
        # 询问是否保存结果
        if Confirm.ask("是否保存分析结果? | Save analysis results?"):
            await save_analysis_results(analysis_id, data)
        
        ui.show_success("分析完成! | Analysis completed!")
        
    except Exception as e:
        # 判断是否为连接错误或超时错误
        if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
            logger.critical(f"🚨 严重告警: 无法连接到Agent Service获取分析结果")
            logger.critical(f"🚨 请检查Agent Service是否启动并可访问")
            logger.critical(f"🚨 错误详情: {type(e).__name__}: {str(e)}")
            ui.show_error(f"服务连接失败，无法获取分析结果: {e}")
        else:
            ui.show_error(f"显示结果时发生错误: {e}")

async def display_detailed_reports(reports: Dict[str, str]):
    """显示详细报告"""
    report_names = {
        "fundamentals": "基本面分析报告 | Fundamentals Analysis Report",
        "technical": "技术分析报告 | Technical Analysis Report", 
        "news": "新闻分析报告 | News Analysis Report",
        "sentiment": "情感分析报告 | Sentiment Analysis Report"
    }
    
    for report_type, content in reports.items():
        if content:
            report_title = report_names.get(report_type, f"{report_type.title()} Report")
            
            # 截断长内容
            display_content = content[:1000] + "..." if len(content) > 1000 else content
            
            report_panel = Panel(
                display_content,
                title=f"📄 {report_title}",
                border_style="cyan"
            )
            console.print(report_panel)
            
            if len(content) > 1000:
                if Confirm.ask(f"查看完整的{report_type}报告? | View complete {report_type} report?"):
                    console.print(content)

async def save_analysis_results(analysis_id: str, data: Dict[str, Any]):
    """保存分析结果"""
    try:
        # 创建结果目录
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        # 生成文件名
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{analysis_id}_{timestamp}.json"
        filepath = results_dir / filename
        
        # 保存结果
        save_data = {
            "analysis_id": analysis_id,
            "timestamp": dt.now().isoformat(),
            "result": data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        ui.show_success(f"结果已保存到: {filepath}")
        
    except Exception as e:
        ui.show_error(f"保存结果失败: {e}")
