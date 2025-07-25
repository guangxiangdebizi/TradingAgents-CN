"""
基础智能体类
移植自tradingagents，定义智能体的基本结构和行为
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    基础智能体抽象类
    所有智能体都应该继承此类并实现核心方法
    """
    
    def __init__(self, 
                 name: str,
                 description: str,
                 llm_client=None,
                 data_client=None,
                 tools: Optional[List] = None):
        """
        初始化基础智能体
        
        Args:
            name: 智能体名称
            description: 智能体描述
            llm_client: LLM客户端（工具）
            data_client: 数据客户端（工具）
            tools: 其他工具列表
        """
        self.name = name
        self.description = description
        self.llm_client = llm_client
        self.data_client = data_client
        self.tools = tools or []
        self.logger = logging.getLogger(f"agent.{name}")
        
        # 智能体状态
        self.is_initialized = False
        self.last_analysis_time = None
        self.analysis_count = 0
    
    async def initialize(self):
        """初始化智能体"""
        try:
            self.logger.info(f"🤖 初始化智能体: {self.name}")
            await self._setup_tools()
            await self._load_prompts()
            self.is_initialized = True
            self.logger.info(f"✅ 智能体初始化完成: {self.name}")
        except Exception as e:
            self.logger.error(f"❌ 智能体初始化失败: {self.name} - {e}")
            raise
    
    @abstractmethod
    async def analyze(self, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行分析 - 子类必须实现
        
        Args:
            symbol: 股票代码
            context: 分析上下文
            
        Returns:
            分析结果
        """
        pass
    
    async def _setup_tools(self):
        """设置工具 - 子类可重写"""
        pass
    
    async def _load_prompts(self):
        """加载提示词模板 - 子类可重写"""
        pass
    
    def _log_analysis_start(self, symbol: str):
        """记录分析开始"""
        self.logger.info(f"🔍 [{self.name}] 开始分析: {symbol}")
        self.analysis_count += 1
    
    def _log_analysis_complete(self, symbol: str, result_summary: str = ""):
        """记录分析完成"""
        self.last_analysis_time = datetime.now()
        self.logger.info(f"✅ [{self.name}] 分析完成: {symbol} - {result_summary}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        return {
            "name": self.name,
            "description": self.description,
            "is_initialized": self.is_initialized,
            "analysis_count": self.analysis_count,
            "last_analysis_time": self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            "tools_count": len(self.tools)
        }
