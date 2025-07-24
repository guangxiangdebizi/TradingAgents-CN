"""
TradingAgents CLI Client - User Interactions
用户交互函数，与TradingAgents完全一致
"""

from datetime import datetime as dt
from typing import List
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from .core import AnalystType

console = Console()

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
    """选择API Gateway地址"""
    options = [
        {"name": "本地API Gateway | Local API Gateway", "url": "http://localhost:8000"},
        {"name": "远程API Gateway | Remote API Gateway", "url": "custom"}
    ]
    
    console.print("[bold]API Gateway选项 | API Gateway Options:[/bold]")
    for i, option in enumerate(options, 1):
        if option['url'] != "custom":
            console.print(f"  {i}. {option['name']} ({option['url']})")
        else:
            console.print(f"  {i}. {option['name']} (自定义URL | Custom URL)")

    while True:
        try:
            choice = IntPrompt.ask("选择API Gateway | Select API Gateway", default=1)
            if choice == 1:
                url = options[0]['url']
                console.print(f"[green]API Gateway URL: {url}[/green]")
                return url
            elif choice == 2:
                url = Prompt.ask("请输入API Gateway URL | Enter API Gateway URL").strip()
                if url:
                    console.print(f"[green]API Gateway URL: {url}[/green]")
                    return url
                else:
                    console.print("[red]URL不能为空 | URL cannot be empty[/red]")
            else:
                console.print("[red]无效选择，请重新输入 | Invalid choice, please try again[/red]")
        except Exception:
            console.print("[red]无效输入，请输入数字 | Invalid input, please enter a number[/red]")

async def select_llm_provider(client):
    """选择LLM提供商"""
    console.print("[bold]正在获取支持的LLM提供商... | Fetching supported LLM providers...[/bold]")

    # 从后台获取LLM提供商列表
    providers_result = await client.get_llm_providers()

    if not providers_result.get("success"):
        console.print(f"[yellow]⚠️ 无法从API Gateway获取LLM提供商: {providers_result.get('error', 'API不可用')}[/yellow]")
        console.print("[yellow]使用内置的LLM提供商列表 | Using built-in LLM providers list[/yellow]")
        # 使用默认提供商列表作为fallback
        providers = [
            {"id": "dashscope", "name": "阿里百炼 | Alibaba DashScope", "description": "阿里云通义千问系列模型"},
            {"id": "deepseek", "name": "DeepSeek", "description": "DeepSeek系列模型"},
            {"id": "openai", "name": "OpenAI", "description": "GPT系列模型"},
            {"id": "anthropic", "name": "Anthropic", "description": "Claude系列模型"},
            {"id": "google", "name": "Google", "description": "Gemini系列模型"}
        ]
    else:
        providers = providers_result.get("data", [])
        console.print(f"[green]✅ 从API Gateway获取到 {len(providers)} 个LLM提供商[/green]")

    if not providers:
        console.print("[red]没有可用的LLM提供商 | No available LLM providers[/red]")
        return None

    console.print("[bold]可选LLM提供商 | Available LLM Providers:[/bold]")
    for i, provider in enumerate(providers, 1):
        name = provider.get("name", provider.get("id", "Unknown"))
        description = provider.get("description", "")
        if description:
            console.print(f"  {i}. {name}")
            console.print(f"     [dim]{description}[/dim]")
        else:
            console.print(f"  {i}. {name}")

    while True:
        try:
            choice = IntPrompt.ask("选择LLM提供商 | Select LLM provider", default=1)
            if 1 <= choice <= len(providers):
                selected = providers[choice - 1]
                provider_name = selected.get("name", selected.get("id", "Unknown"))
                console.print(f"[green]已选择: {provider_name}[/green]")
                return selected
            else:
                console.print("[red]无效选择，请重新输入 | Invalid choice, please try again[/red]")
        except Exception:
            console.print("[red]无效输入，请输入数字 | Invalid input, please enter a number[/red]")

async def select_llm_model(client, provider):
    """选择LLM模型"""
    provider_id = provider.get("id")
    provider_name = provider.get("name", provider_id)

    console.print(f"[bold]正在获取{provider_name}的模型列表... | Fetching models for {provider_name}...[/bold]")

    # 从后台获取模型列表
    models_result = await client.get_llm_models(provider_id)

    if not models_result.get("success"):
        console.print(f"[yellow]⚠️ 无法从API Gateway获取模型列表: {models_result.get('error', 'API不可用')}[/yellow]")
        console.print(f"[yellow]使用内置的{provider_name}模型列表 | Using built-in {provider_name} models list[/yellow]")
        # 使用默认模型列表作为fallback
        default_models = {
            "dashscope": [
                {"id": "qwen-plus-latest", "name": "通义千问Plus (最新版)", "description": "高性能通用模型"},
                {"id": "qwen-turbo-latest", "name": "通义千问Turbo (最新版)", "description": "快速响应模型"},
                {"id": "qwen-max-latest", "name": "通义千问Max (最新版)", "description": "最强性能模型"}
            ],
            "deepseek": [
                {"id": "deepseek-chat", "name": "DeepSeek Chat", "description": "对话优化模型"},
                {"id": "deepseek-coder", "name": "DeepSeek Coder", "description": "代码优化模型"}
            ],
            "openai": [
                {"id": "gpt-4o", "name": "GPT-4o", "description": "最新多模态模型"},
                {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "高性能模型"},
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "经济实用模型"}
            ],
            "anthropic": [
                {"id": "claude-3-5-sonnet", "name": "Claude 3.5 Sonnet", "description": "最新版本"},
                {"id": "claude-3-opus", "name": "Claude 3 Opus", "description": "最强性能"},
                {"id": "claude-3-haiku", "name": "Claude 3 Haiku", "description": "快速响应"}
            ],
            "google": [
                {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "description": "高性能模型"},
                {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "description": "快速模型"}
            ]
        }
        models = default_models.get(provider_id, [])
    else:
        models = models_result.get("data", [])

    if not models:
        console.print(f"[red]{provider_name}没有可用的模型 | No available models for {provider_name}[/red]")
        return None

    console.print(f"[bold]{provider_name}可用模型 | Available Models for {provider_name}:[/bold]")
    for i, model in enumerate(models, 1):
        name = model.get("name", model.get("id", "Unknown"))
        description = model.get("description", "")
        if description:
            console.print(f"  {i}. {name}")
            console.print(f"     [dim]{description}[/dim]")
        else:
            console.print(f"  {i}. {name}")

    while True:
        try:
            choice = IntPrompt.ask(f"选择{provider_name}模型 | Select {provider_name} model", default=1)
            if 1 <= choice <= len(models):
                selected = models[choice - 1]
                model_name = selected.get("name", selected.get("id", "Unknown"))
                console.print(f"[green]已选择: {model_name}[/green]")
                return selected
            else:
                console.print("[red]无效选择，请重新输入 | Invalid choice, please try again[/red]")
        except Exception:
            console.print("[red]无效输入，请输入数字 | Invalid input, please enter a number[/red]")
