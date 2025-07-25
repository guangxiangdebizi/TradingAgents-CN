"""
TradingAgents CLI Client - Core Components
"""

import asyncio
import json
import time
from datetime import datetime as dt
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum

import aiohttp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.align import Align
from rich import box

# 使用标准logging作为fallback
try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
    logger = logging.getLogger(__name__)

# 配置Rich控制台
console = Console()

# 分析师枚举 - 与TradingAgents完全一致
class AnalystType(Enum):
    MARKET_ANALYST = "market_analyst"
    FUNDAMENTALS_ANALYST = "fundamentals_analyst"
    NEWS_ANALYST = "news_analyst"
    SOCIAL_ANALYST = "social_analyst"

# 默认配置 - 连接到API Gateway
DEFAULT_CONFIG = {
    "max_debate_rounds": 3,
    "max_risk_discuss_rounds": 2,
    "backend_url": "http://localhost:8000",  # API Gateway端口
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
        self.console.print(f"[green]✅ ✅ {message}[/green]")
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
        self.console.print("─" * 60)

# 创建全局UI管理器
ui = CLIUserInterface()

# Backend API客户端
class BackendClient:
    """Backend API客户端 - 连接到API Gateway"""

    def __init__(self, base_url: str = "http://localhost:8000"):
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

    async def get_llm_providers(self) -> Dict[str, Any]:
        """获取支持的LLM提供商列表"""
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/llm/providers"
            ) as resp:
                return await resp.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_llm_models(self, provider: str) -> Dict[str, Any]:
        """获取指定提供商的模型列表"""
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/llm/providers/{provider}/models"
            ) as resp:
                return await resp.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
