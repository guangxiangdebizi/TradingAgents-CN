#!/usr/bin/env python3
"""
TradingAgents CLI Client - Core Module
完全复制TradingAgents的命令行界面，调用Backend分析服务
"""

import asyncio
import json
import sys
import time
import datetime
from datetime import datetime as dt
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum
from functools import wraps

import typer
import aiohttp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.syntax import Syntax
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich.markdown import Markdown
from rich import box
from loguru import logger

# 配置Rich控制台
console = Console()

# 分析师枚举 - 与TradingAgents完全一致
class AnalystType(Enum):
    MARKET_ANALYST = "market_analyst"
    FUNDAMENTALS_ANALYST = "fundamentals_analyst"
    NEWS_ANALYST = "news_analyst"
    SOCIAL_ANALYST = "social_analyst"

# 默认配置 - 与TradingAgents一致
DEFAULT_CONFIG = {
    "max_debate_rounds": 3,
    "max_risk_discuss_rounds": 2,
    "backend_url": "http://localhost:8001",
    "results_dir": "results"
}

# CLI用户界面管理器 - 与TradingAgents完全一致
class CLIUserInterface:
    """CLI用户界面管理器：处理用户显示和进度提示"""

    def __init__(self):
        self.console = Console()
        self.logger = logger

    def show_user_message(self, message: str, style: str = ""):
        """显示用户消息"""
        if style:
            self.console.print(f"[{style}]{message}[/{style}]")
        else:
            self.console.print(message)

    def show_progress(self, message: str):
        """显示进度信息"""
        self.console.print(f"🔄 {message}")
        # 同时记录到日志文件
        self.logger.info(f"进度: {message}")

    def show_success(self, message: str):
        """显示成功信息"""
        self.console.print(f"[green]✅ {message}[/green]")
        self.logger.info(f"成功: {message}")

    def show_error(self, message: str):
        """显示错误信息"""
        self.console.print(f"[red]❌ {message}[/red]")
        self.logger.error(f"错误: {message}")

    def show_warning(self, message: str):
        """显示警告信息"""
        self.console.print(f"[yellow]⚠️ {message}[/yellow]")
        self.logger.warning(f"警告: {message}")

    def show_step_header(self, step: int, title: str):
        """显示步骤标题"""
        self.console.print(f"\n[bold blue]步骤 {step}: {title}[/bold blue]")

# 创建全局UI管理器
ui = CLIUserInterface()

# Backend API客户端
class BackendClient:
    """Backend API客户端"""

    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            async with self.session.get(f"{self.base_url}/health") as resp:
                return await resp.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def start_analysis(self, symbol: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """启动股票分析"""
        data = {
            "symbol": symbol,
            "analysis_type": "comprehensive",
            "config": config
        }

        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/analysis/comprehensive",
                json=data
            ) as resp:
                return await resp.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """获取分析状态"""
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/analysis/status/{analysis_id}"
            ) as resp:
                return await resp.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_analysis_result(self, analysis_id: str) -> Dict[str, Any]:
        """获取分析结果"""
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/analysis/result/{analysis_id}"
            ) as resp:
                return await resp.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

# 市场选择函数 - 与TradingAgents一致
def select_market():
    """选择股票市场"""
    markets = [
        {"name": "中国A股 | China A-shares", "code": "CN", "default": "000001"},
        {"name": "美国股票 | US Stocks", "code": "US", "default": "AAPL"},
        {"name": "香港股票 | Hong Kong Stocks", "code": "HK", "default": "00700"}
    ]

    console.print("[bold]可选市场 | Available Markets:[/bold]")
    for i, market in enumerate(markets, 1):
        console.print(f"  {i}. {market['name']}")

    while True:
        try:
            choice = IntPrompt.ask("请选择市场 | Select market", default=1)
            if 1 <= choice <= len(markets):
                selected = markets[choice - 1]
                console.print(f"[green]已选择: {selected['name']}[/green]")
                return selected
            else:
                console.print("[red]无效选择，请重新输入 | Invalid choice, please try again[/red]")
        except Exception:
            console.print("[red]无效输入，请输入数字 | Invalid input, please enter a number[/red]")

def get_ticker(market):
    """获取股票代码"""
    while True:
        ticker = Prompt.ask(
            f"请输入{market['name']}股票代码 | Enter {market['name']} ticker symbol",
            default=market['default']
        ).strip().upper()

        if ticker:
            console.print(f"[green]股票代码: {ticker}[/green]")
            return ticker
        else:
            console.print("[red]股票代码不能为空 | Ticker symbol cannot be empty[/red]")

def get_analysis_date():
    """获取分析日期"""
    default_date = dt.now().strftime("%Y-%m-%d")

    while True:
        date_str = Prompt.ask(
            "请输入分析日期 (YYYY-MM-DD) | Enter analysis date (YYYY-MM-DD)",
            default=default_date
        ).strip()

        try:
            # 验证日期格式
            dt.strptime(date_str, "%Y-%m-%d")
            console.print(f"[green]分析日期: {date_str}[/green]")
            return date_str
        except ValueError:
            console.print("[red]日期格式错误，请使用 YYYY-MM-DD 格式 | Invalid date format, please use YYYY-MM-DD[/red]")

def select_analysts():
    """选择分析师团队"""
    analysts = [
        AnalystType.MARKET_ANALYST,
        AnalystType.FUNDAMENTALS_ANALYST,
        AnalystType.NEWS_ANALYST,
        AnalystType.SOCIAL_ANALYST
    ]

    analyst_names = {
        AnalystType.MARKET_ANALYST: "市场分析师 | Market Analyst",
        AnalystType.FUNDAMENTALS_ANALYST: "基本面分析师 | Fundamentals Analyst",
        AnalystType.NEWS_ANALYST: "新闻分析师 | News Analyst",
        AnalystType.SOCIAL_ANALYST: "社交媒体分析师 | Social Media Analyst"
    }

    console.print("[bold]可选分析师 | Available Analysts:[/bold]")
    for i, analyst in enumerate(analysts, 1):
        console.print(f"  {i}. {analyst_names[analyst]}")

    console.print("\n[dim]请输入分析师编号，用逗号分隔 (例如: 1,2,3) | Enter analyst numbers separated by commas (e.g., 1,2,3)[/dim]")
    console.print("[dim]直接按回车选择所有分析师 | Press Enter to select all analysts[/dim]")

    while True:
        choice = Prompt.ask("选择分析师 | Select analysts", default="1,2,3,4").strip()

        if not choice:
            choice = "1,2,3,4"

        try:
            indices = [int(x.strip()) for x in choice.split(",")]
            selected_analysts = []

            for idx in indices:
                if 1 <= idx <= len(analysts):
                    selected_analysts.append(analysts[idx - 1])
                else:
                    raise ValueError(f"无效的分析师编号: {idx}")

            if selected_analysts:
                return selected_analysts
            else:
                console.print("[red]请至少选择一个分析师 | Please select at least one analyst[/red]")

        except ValueError as e:
            console.print(f"[red]输入错误: {e} | Input error: {e}[/red]")

def select_research_depth():
    """选择研究深度"""
    depths = [
        {"name": "快速分析 | Quick Analysis", "rounds": 1},
        {"name": "标准分析 | Standard Analysis", "rounds": 3},
        {"name": "深度分析 | Deep Analysis", "rounds": 5}
    ]

    console.print("[bold]研究深度选项 | Research Depth Options:[/bold]")
    for i, depth in enumerate(depths, 1):
        console.print(f"  {i}. {depth['name']} ({depth['rounds']} 轮辩论 | {depth['rounds']} debate rounds)")

    while True:
        try:
            choice = IntPrompt.ask("选择研究深度 | Select research depth", default=2)
            if 1 <= choice <= len(depths):
                selected = depths[choice - 1]
                console.print(f"[green]已选择: {selected['name']}[/green]")
                return selected['rounds']
            else:
                console.print("[red]无效选择，请重新输入 | Invalid choice, please try again[/red]")
        except Exception:
            console.print("[red]无效输入，请输入数字 | Invalid input, please enter a number[/red]")

def select_backend_url():
    """选择Backend服务地址"""
    options = [
        {"name": "本地服务 | Local Service", "url": "http://localhost:8001"},
        {"name": "远程服务 | Remote Service", "url": "custom"}
    ]

    console.print("[bold]Backend服务选项 | Backend Service Options:[/bold]")
    for i, option in enumerate(options, 1):
        if option['url'] != "custom":
            console.print(f"  {i}. {option['name']} ({option['url']})")
        else:
            console.print(f"  {i}. {option['name']} (自定义URL | Custom URL)")

    while True:
        try:
            choice = IntPrompt.ask("选择Backend服务 | Select Backend service", default=1)
            if choice == 1:
                url = options[0]['url']
                console.print(f"[green]Backend URL: {url}[/green]")
                return url
            elif choice == 2:
                url = Prompt.ask("请输入Backend服务URL | Enter Backend service URL").strip()
                if url:
                    console.print(f"[green]Backend URL: {url}[/green]")
                    return url
                else:
                    console.print("[red]URL不能为空 | URL cannot be empty[/red]")
            else:
                console.print("[red]无效选择，请重新输入 | Invalid choice, please try again[/red]")
        except Exception:
            console.print("[red]无效输入，请输入数字 | Invalid input, please enter a number[/red]")
def display_welcome():
    """显示欢迎界面 - 与TradingAgents完全一致"""
    try:
        # 尝试读取ASCII艺术字
        ascii_file = Path(__file__).parent / "ascii_art.txt"
        if ascii_file.exists():
            with open(ascii_file, 'r', encoding='utf-8') as f:
                welcome_ascii = f.read()
        else:
            welcome_ascii = "TradingAgents"
    except FileNotFoundError:
        welcome_ascii = "TradingAgents"

    # 创建欢迎框内容
    welcome_content = f"{welcome_ascii}\n"
    welcome_content += "[bold green]TradingAgents: 多智能体大语言模型金融交易框架 - CLI[/bold green]\n"
    welcome_content += "[bold green]Multi-Agents LLM Financial Trading Framework - CLI[/bold green]\n\n"
    welcome_content += "[bold]工作流程 | Workflow Steps:[/bold]\n"
    welcome_content += "I. 分析师团队 | Analyst Team → II. 研究团队 | Research Team → III. 交易员 | Trader → IV. 风险管理 | Risk Management → V. 投资组合管理 | Portfolio Management\n\n"
    welcome_content += (
        "[dim]Built by Backend Team (Based on TradingAgents)[/dim]"
    )

    # 创建并居中显示欢迎框
    welcome_box = Panel(
        welcome_content,
        border_style="green",
        padding=(1, 2),
        title="欢迎使用 TradingAgents | Welcome to TradingAgents",
        subtitle="多智能体大语言模型金融交易框架 | Multi-Agents LLM Financial Trading Framework",
    )
    console.print(Align.center(welcome_box))
    console.print()  # 添加空行

def create_question_box(title, prompt, default=None):
    """创建问题框"""
    box_content = f"[bold]{title}[/bold]\n"
    box_content += f"[dim]{prompt}[/dim]"
    if default:
        box_content += f"\n[dim]Default: {default}[/dim]"
    return Panel(box_content, border_style="blue", padding=(1, 2))
    
async def run_analysis(symbol: str, market: str, analysis_date: str, selected_analysts: List[AnalystType],
                      max_debate_rounds: int, backend_url: str):
    """运行分析 - 与TradingAgents的执行流程完全一致"""

    # 创建配置
    config = {
        "max_debate_rounds": max_debate_rounds,
        "max_risk_discuss_rounds": 2,
        "selected_analysts": [analyst.value for analyst in selected_analysts],
        "market": market,
        "analysis_date": analysis_date
    }

    ui.show_step_header(1, "连接Backend服务 | Connecting to Backend Service")

    async with BackendClient(backend_url) as client:
        # 检查服务健康状态
        health = await client.health_check()
        if not health.get("success"):
            ui.show_error(f"Backend服务连接失败: {health.get('error', 'Unknown error')}")
            return

        ui.show_success("Backend服务连接成功 | Backend service connected successfully")

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

        data = result["data"]["result"]

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
    
    def display_help(self):
        """显示帮助信息"""
        help_table = Table(title="可用命令")
        help_table.add_column("命令", style="cyan", no_wrap=True)
        help_table.add_column("描述", style="white")
        help_table.add_column("示例", style="yellow")
        
        commands = [
            ("analyze <股票代码>", "启动股票分析", "analyze 000001"),
            ("status <分析ID>", "查看分析状态", "status uuid-12345"),
            ("result <分析ID>", "获取分析结果", "result uuid-12345"),
            ("cancel <分析ID>", "取消分析", "cancel uuid-12345"),
            ("health", "检查服务健康状态", "health"),
            ("config", "显示当前配置", "config"),
            ("set <key> <value>", "设置配置项", "set backend_url http://localhost:8001"),
            ("history", "显示分析历史", "history"),
            ("help", "显示帮助信息", "help"),
            ("exit", "退出程序", "exit")
        ]
        
        for cmd, desc, example in commands:
            help_table.add_row(cmd, desc, example)
        
        console.print(help_table)
    
    def display_config(self):
        """显示当前配置"""
        config_table = Table(title="当前配置")
        config_table.add_column("配置项", style="cyan")
        config_table.add_column("值", style="white")
        
        for key, value in self.config.items():
            config_table.add_row(key, str(value))
        
        console.print(config_table)
    
    async def analyze_stock(self, symbol: str):
        """分析股票"""
        console.print(f"\n🔍 开始分析股票: [bold cyan]{symbol}[/bold cyan]")
        
        # 启动分析
        async with BackendClient(self.config["backend_url"]) as client:
            result = await client.start_analysis(symbol, self.config["default_analysis_type"])
            
            if not result.get("success"):
                console.print(f"❌ 启动分析失败: {result.get('error', 'Unknown error')}", style="red")
                return
            
            analysis_id = result["data"]["analysis_id"]
            console.print(f"✅ 分析已启动，ID: [bold yellow]{analysis_id}[/bold yellow]")
            
            # 监控分析进度
            await self.monitor_analysis(client, analysis_id)
    
    async def monitor_analysis(self, client: BackendClient, analysis_id: str):
        """监控分析进度"""
        start_time = time.time()
        max_wait = self.config["max_wait_time"]
        refresh_interval = self.config["refresh_interval"]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("分析进行中...", total=100)
            
            while True:
                # 检查超时
                if time.time() - start_time > max_wait:
                    console.print(f"⏰ 分析超时 ({max_wait}秒)，请稍后查看结果", style="yellow")
                    break
                
                # 获取状态
                status_result = await client.get_analysis_status(analysis_id)
                
                if not status_result.get("success"):
                    console.print(f"❌ 获取状态失败: {status_result.get('error')}", style="red")
                    break
                
                status_data = status_result["data"]
                current_status = status_data["status"]
                
                # 更新进度
                if "progress" in status_data:
                    percentage = status_data["progress"]["percentage"]
                    current_step = status_data.get("current_step", "unknown")
                    progress.update(task, completed=percentage, description=f"当前步骤: {current_step}")
                
                # 显示辩论状态
                if "debate_status" in status_data:
                    debate = status_data["debate_status"]
                    console.print(f"🗣️ 辩论状态: 第{debate['current_round']}/{debate['max_rounds']}轮, 当前发言者: {debate['current_speaker']}")
                
                # 检查完成状态
                if current_status == "completed":
                    progress.update(task, completed=100, description="分析完成!")
                    console.print("✅ 分析完成!", style="green")
                    
                    # 获取并显示结果
                    await self.display_analysis_result(client, analysis_id)
                    break
                elif current_status == "failed":
                    console.print("❌ 分析失败", style="red")
                    if "errors" in status_data and status_data["errors"]:
                        for error in status_data["errors"]:
                            console.print(f"  • {error}", style="red")
                    break
                
                # 等待下次刷新
                await asyncio.sleep(refresh_interval)
    
    async def display_analysis_result(self, client: BackendClient, analysis_id: str):
        """显示分析结果"""
        result = await client.get_analysis_result(analysis_id)
        
        if not result.get("success"):
            console.print(f"❌ 获取结果失败: {result.get('error')}", style="red")
            return
        
        data = result["data"]["result"]
        
        # 显示最终推荐
        if "final_recommendation" in data:
            rec = data["final_recommendation"]
            
            # 推荐面板
            rec_text = f"""
动作: {rec.get('action', 'N/A')}
置信度: {rec.get('confidence', 0):.2%}
目标价格: {rec.get('target_price', 'N/A')}
推理: {rec.get('reasoning', 'N/A')}
            """.strip()
            
            rec_panel = Panel(
                rec_text,
                title="[bold green]最终投资建议[/bold green]",
                border_style="green"
            )
            console.print(rec_panel)
        
        # 显示投资计划
        if "investment_plan" in data:
            plan_panel = Panel(
                data["investment_plan"],
                title="[bold blue]投资计划[/bold blue]",
                border_style="blue"
            )
            console.print(plan_panel)
        
        # 显示风险评估
        if "risk_assessment" in data:
            risk = data["risk_assessment"]
            risk_text = f"""
风险等级: {risk.get('risk_level', 'N/A')}
风险分数: {risk.get('risk_score', 0):.2f}
关键风险: {', '.join(risk.get('key_risks', []))}
            """.strip()
            
            risk_panel = Panel(
                risk_text,
                title="[bold red]风险评估[/bold red]",
                border_style="red"
            )
            console.print(risk_panel)
        
        # 显示辩论摘要
        if "debate_summary" in data:
            debate = data["debate_summary"]
            debate_text = f"""
辩论轮数: {debate.get('total_rounds', 0)}
达成共识: {'是' if debate.get('consensus_reached') else '否'}
最终立场: {debate.get('final_stance', 'N/A')}
            """.strip()
            
            debate_panel = Panel(
                debate_text,
                title="[bold yellow]辩论摘要[/bold yellow]",
                border_style="yellow"
            )
            console.print(debate_panel)
        
        # 询问是否查看详细报告
        if Confirm.ask("是否查看详细分析报告?"):
            await self.display_detailed_reports(data.get("reports", {}))
    
    async def display_detailed_reports(self, reports: Dict[str, str]):
        """显示详细报告"""
        for report_type, content in reports.items():
            if content:
                report_panel = Panel(
                    content[:500] + "..." if len(content) > 500 else content,
                    title=f"[bold cyan]{report_type.title()}分析报告[/bold cyan]",
                    border_style="cyan"
                )
                console.print(report_panel)
                
                if len(content) > 500:
                    if Confirm.ask(f"查看完整的{report_type}报告?"):
                        console.print(content)
    
    async def run_interactive(self):
        """运行交互式命令行"""
        self.display_welcome()
        
        # 检查Backend连接
        if not await self.check_backend_health():
            if not Confirm.ask("Backend服务连接失败，是否继续?"):
                return
        
        console.print("\n💡 输入 'help' 查看可用命令，输入 'exit' 退出程序\n")
        
        while True:
            try:
                # 获取用户输入
                command = Prompt.ask("[bold green]trading-cli[/bold green]").strip()
                
                if not command:
                    continue
                
                # 解析命令
                parts = command.split()
                cmd = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                # 执行命令
                if cmd == "exit" or cmd == "quit":
                    console.print("👋 再见!", style="blue")
                    break
                elif cmd == "help":
                    self.display_help()
                elif cmd == "health":
                    await self.check_backend_health()
                elif cmd == "config":
                    self.display_config()
                elif cmd == "analyze":
                    if not args:
                        console.print("❌ 请提供股票代码", style="red")
                        continue
                    await self.analyze_stock(args[0])
                elif cmd == "status":
                    if not args:
                        console.print("❌ 请提供分析ID", style="red")
                        continue
                    await self.show_analysis_status(args[0])
                elif cmd == "result":
                    if not args:
                        console.print("❌ 请提供分析ID", style="red")
                        continue
                    await self.show_analysis_result(args[0])
                elif cmd == "cancel":
                    if not args:
                        console.print("❌ 请提供分析ID", style="red")
                        continue
                    await self.cancel_analysis(args[0])
                elif cmd == "set":
                    if len(args) < 2:
                        console.print("❌ 用法: set <key> <value>", style="red")
                        continue
                    self.config[args[0]] = args[1]
                    self.save_config()
                    console.print(f"✅ 已设置 {args[0]} = {args[1]}", style="green")
                else:
                    console.print(f"❌ 未知命令: {cmd}. 输入 'help' 查看可用命令", style="red")
                
            except KeyboardInterrupt:
                console.print("\n👋 再见!", style="blue")
                break
            except Exception as e:
                console.print(f"❌ 命令执行错误: {e}", style="red")
    
    async def show_analysis_status(self, analysis_id: str):
        """显示分析状态"""
        async with BackendClient(self.config["backend_url"]) as client:
            result = await client.get_analysis_status(analysis_id)
            
            if not result.get("success"):
                console.print(f"❌ 获取状态失败: {result.get('error')}", style="red")
                return
            
            data = result["data"]
            
            # 创建状态表格
            status_table = Table(title=f"分析状态 - {analysis_id}")
            status_table.add_column("项目", style="cyan")
            status_table.add_column("值", style="white")
            
            status_table.add_row("状态", data.get("status", "unknown"))
            status_table.add_row("当前步骤", data.get("current_step", "unknown"))
            
            if "progress" in data:
                progress_data = data["progress"]
                status_table.add_row("进度", f"{progress_data.get('percentage', 0):.1f}%")
                status_table.add_row("已完成步骤", f"{progress_data.get('completed_steps', 0)}/{progress_data.get('total_steps', 0)}")
            
            console.print(status_table)
    
    async def show_analysis_result(self, analysis_id: str):
        """显示分析结果"""
        async with BackendClient(self.config["backend_url"]) as client:
            await self.display_analysis_result(client, analysis_id)
    
    async def cancel_analysis(self, analysis_id: str):
        """取消分析"""
        async with BackendClient(self.config["backend_url"]) as client:
            result = await client.cancel_analysis(analysis_id)
            
            if result.get("success"):
                console.print(f"✅ 分析 {analysis_id} 已取消", style="green")
            else:
                console.print(f"❌ 取消分析失败: {result.get('error')}", style="red")

async def main():
    """主函数 - 与TradingAgents的交互流程完全一致"""

    # 设置日志
    logger.remove()
    logger.add(
        "trading_cli.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation="10 MB"
    )

    try:
        # 显示欢迎界面
        display_welcome()

        # 步骤1: 选择市场
        console.print(create_question_box(
            "步骤 1/6: 选择股票市场 | Step 1/6: Select Stock Market",
            "请选择您要分析的股票市场 | Please select the stock market you want to analyze"
        ))
        market = select_market()

        # 步骤2: 输入股票代码
        console.print(create_question_box(
            "步骤 2/6: 输入股票代码 | Step 2/6: Enter Stock Ticker",
            f"请输入{market['name']}的股票代码 | Please enter the stock ticker for {market['name']}"
        ))
        symbol = get_ticker(market)

        # 步骤3: 选择分析日期
        console.print(create_question_box(
            "步骤 3/6: 选择分析日期 | Step 3/6: Select Analysis Date",
            "请选择分析日期 | Please select the analysis date"
        ))
        analysis_date = get_analysis_date()

        # 步骤4: 选择分析师团队
        console.print(create_question_box(
            "步骤 4/6: 选择分析师团队 | Step 4/6: Select Analyst Team",
            "请选择参与分析的分析师 | Please select the analysts to participate in the analysis"
        ))
        selected_analysts = select_analysts()

        # 步骤5: 选择研究深度
        console.print(create_question_box(
            "步骤 5/6: 选择研究深度 | Step 5/6: Select Research Depth",
            "请选择研究深度（辩论轮数）| Please select the research depth (debate rounds)"
        ))
        max_debate_rounds = select_research_depth()

        # 步骤6: 选择Backend服务
        console.print(create_question_box(
            "步骤 6/6: 选择Backend服务 | Step 6/6: Select Backend Service",
            "请选择Backend服务地址 | Please select the Backend service URL"
        ))
        backend_url = select_backend_url()

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
        summary_table.add_row("Backend服务 | Backend", backend_url)

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
            backend_url=backend_url
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]用户中断程序 | User interrupted the program[/yellow]")
    except Exception as e:
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
