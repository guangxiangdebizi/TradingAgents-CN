"""
TradingAgents CLI Client - UI Components
界面显示组件，与TradingAgents完全一致
"""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.align import Align

console = Console()

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
