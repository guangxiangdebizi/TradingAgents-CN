"""
TradingAgents CLI Client - Main Entry Point
主入口文件，与TradingAgents完全一致的交互流程
"""

import asyncio
import sys
import logging
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from rich import box

# 使用标准logging作为fallback
try:
    from loguru import logger
except ImportError:
    # 如果loguru不可用，使用标准logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
    logger = logging.getLogger(__name__)

from .ui import display_welcome, create_question_box
from .interactions import (
    select_market, get_ticker, get_analysis_date,
    select_analysts, select_research_depth, select_backend_url,
    select_llm_provider, select_llm_model
)
from .analysis import run_analysis
from .core import ui

console = Console()

async def main():
    """主函数 - 与TradingAgents的交互流程完全一致"""
    
    # 设置日志
    try:
        # 如果是loguru
        if hasattr(logger, 'remove'):
            logger.remove()
            logger.add(
                "trading_cli.log",
                level="INFO",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
                rotation="10 MB"
            )
    except:
        # 使用标准logging
        logging.basicConfig(
            filename="trading_cli.log",
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s"
        )
    
    try:
        # 显示欢迎界面
        display_welcome()
        
        # 步骤1: 选择市场
        console.print(create_question_box(
            "步骤 1/8: 选择股票市场 | Step 1/8: Select Stock Market",
            "请选择您要分析的股票市场 | Please select the stock market you want to analyze"
        ))
        market = select_market()

        # 步骤2: 输入股票代码
        console.print(create_question_box(
            "步骤 2/8: 输入股票代码 | Step 2/8: Enter Stock Ticker",
            f"请输入{market['name']}的股票代码 | Please enter the stock ticker for {market['name']}"
        ))
        symbol = get_ticker(market)

        # 步骤3: 选择分析日期
        console.print(create_question_box(
            "步骤 3/8: 选择分析日期 | Step 3/8: Select Analysis Date",
            "请选择分析日期 | Please select the analysis date"
        ))
        analysis_date = get_analysis_date()

        # 步骤4: 选择分析师团队
        console.print(create_question_box(
            "步骤 4/8: 选择分析师团队 | Step 4/8: Select Analyst Team",
            "请选择参与分析的分析师 | Please select the analysts to participate in the analysis"
        ))
        selected_analysts = select_analysts()

        # 步骤5: 选择研究深度
        console.print(create_question_box(
            "步骤 5/8: 选择研究深度 | Step 5/8: Select Research Depth",
            "请选择研究深度（辩论轮数）| Please select the research depth (debate rounds)"
        ))
        max_debate_rounds = select_research_depth()

        # 步骤6: 选择API Gateway
        console.print(create_question_box(
            "步骤 6/8: 选择API Gateway | Step 6/8: Select API Gateway",
            "请选择API Gateway地址 | Please select the API Gateway URL"
        ))
        backend_url = select_backend_url()

        # 创建临时客户端用于获取LLM信息
        from .core import BackendClient
        temp_client = BackendClient(backend_url)
        await temp_client.__aenter__()

        try:
            # 步骤7: 选择LLM提供商
            console.print(create_question_box(
                "步骤 7/8: 选择LLM提供商 | Step 7/8: Select LLM Provider",
                "请选择要使用的大语言模型提供商 | Please select the LLM provider to use"
            ))
            selected_provider = await select_llm_provider(temp_client)

            if not selected_provider:
                console.print("[red]无法获取LLM提供商，分析终止 | Cannot get LLM providers, analysis terminated[/red]")
                return

            # 步骤8: 选择LLM模型
            console.print(create_question_box(
                "步骤 8/8: 选择LLM模型 | Step 8/8: Select LLM Model",
                f"请选择{selected_provider.get('name', 'LLM')}的具体模型 | Please select the specific model"
            ))
            selected_model = await select_llm_model(temp_client, selected_provider)

            if not selected_model:
                console.print("[red]无法获取LLM模型，分析终止 | Cannot get LLM models, analysis terminated[/red]")
                return

        finally:
            await temp_client.__aexit__(None, None, None)

        # 显示配置摘要
        console.print("\n" + "="*60)
        console.print("[bold]配置摘要 | Configuration Summary[/bold]")
        console.print("="*60)
        
        summary_table = Table(box=box.SIMPLE)
        summary_table.add_column("配置项 | Item", style="cyan")
        summary_table.add_column("值 | Value", style="white")
        
        summary_table.add_row("股票市场 | Market", market['name'])
        summary_table.add_row("股票代码 | Symbol", symbol)
        summary_table.add_row("分析日期 | Date", analysis_date)
        summary_table.add_row("分析师团队 | Analysts", f"{len(selected_analysts)} 位分析师 | {len(selected_analysts)} analysts")
        summary_table.add_row("辩论轮数 | Debate Rounds", str(max_debate_rounds))
        summary_table.add_row("API Gateway", backend_url)
        summary_table.add_row("LLM提供商 | LLM Provider", selected_provider.get('name', 'Unknown'))
        summary_table.add_row("LLM模型 | LLM Model", selected_model.get('name', 'Unknown'))
        
        console.print(summary_table)
        console.print("="*60)
        
        # 确认开始分析
        if not Confirm.ask("\n开始分析? | Start analysis?", default=True):
            console.print("[yellow]分析已取消 | Analysis cancelled[/yellow]")
            return
        
        # 执行分析
        await run_analysis(
            symbol=symbol,
            market=market['code'],
            analysis_date=analysis_date,
            selected_analysts=selected_analysts,
            max_debate_rounds=max_debate_rounds,
            backend_url=backend_url,
            llm_provider=selected_provider,
            llm_model=selected_model
        )
        
    except KeyboardInterrupt:
        console.print("\n[yellow]用户中断程序 | User interrupted the program[/yellow]")
    except Exception as e:
        # 判断是否为连接错误或超时错误
        if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
            logger.critical(f"🚨 严重告警: 无法连接到后端服务")
            logger.critical(f"🚨 请检查Agent Service是否启动并可访问")
            logger.critical(f"🚨 错误详情: {type(e).__name__}: {str(e)}")
            ui.show_error(f"服务连接失败: {e}")
        else:
            ui.show_error(f"程序执行错误: {e}")
            logger.exception("程序异常")

def cli_main():
    """CLI入口点"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 再见! | Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[red]❌ 程序错误: {e}[/red]")

if __name__ == "__main__":
    cli_main()
