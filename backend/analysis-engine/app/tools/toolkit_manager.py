"""
工具链管理器
统一管理所有分析工具
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from .data_tools import DataTools
from .analysis_tools import AnalysisTools
from .news_tools import NewsTools

logger = logging.getLogger(__name__)

@dataclass
class ToolInfo:
    """工具信息"""
    name: str
    description: str
    category: str
    parameters: Dict[str, Any]
    function: Callable

class ToolkitManager:
    """工具链管理器"""
    
    def __init__(self):
        self.tools: Dict[str, ToolInfo] = {}
        self.data_tools: Optional[DataTools] = None
        self.analysis_tools: Optional[AnalysisTools] = None
        self.news_tools: Optional[NewsTools] = None
        self.initialized = False
    
    async def initialize(self):
        """初始化工具链"""
        try:
            logger.info("🔧 初始化工具链管理器...")
            
            # 初始化各类工具
            self.data_tools = DataTools()
            await self.data_tools.initialize()
            
            self.analysis_tools = AnalysisTools()
            await self.analysis_tools.initialize()
            
            self.news_tools = NewsTools()
            await self.news_tools.initialize()
            
            # 注册所有工具
            await self._register_tools()
            
            self.initialized = True
            logger.info(f"✅ 工具链初始化完成，共注册{len(self.tools)}个工具")
            
        except Exception as e:
            logger.error(f"❌ 工具链初始化失败: {e}")
            raise
    
    async def _register_tools(self):
        """注册所有工具"""
        
        # 注册数据工具
        if self.data_tools:
            self._register_tool(
                "get_stock_data",
                "获取股票基础数据",
                "data",
                {"symbol": "str", "period": "str"},
                self.data_tools.get_stock_data
            )
            
            self._register_tool(
                "get_financial_data",
                "获取财务数据",
                "data",
                {"symbol": "str", "statement_type": "str"},
                self.data_tools.get_financial_data
            )
            
            self._register_tool(
                "get_market_data",
                "获取市场数据",
                "data",
                {"symbol": "str", "indicators": "list"},
                self.data_tools.get_market_data
            )
        
        # 注册分析工具
        if self.analysis_tools:
            self._register_tool(
                "calculate_technical_indicators",
                "计算技术指标",
                "analysis",
                {"data": "dict", "indicators": "list"},
                self.analysis_tools.calculate_technical_indicators
            )
            
            self._register_tool(
                "perform_fundamental_analysis",
                "执行基本面分析",
                "analysis",
                {"financial_data": "dict", "market_data": "dict"},
                self.analysis_tools.perform_fundamental_analysis
            )
            
            self._register_tool(
                "calculate_valuation",
                "计算估值",
                "analysis",
                {"financial_data": "dict", "method": "str"},
                self.analysis_tools.calculate_valuation
            )
        
        # 注册新闻工具
        if self.news_tools:
            self._register_tool(
                "get_stock_news",
                "获取股票新闻",
                "news",
                {"symbol": "str", "days": "int"},
                self.news_tools.get_stock_news
            )
            
            self._register_tool(
                "analyze_sentiment",
                "分析情绪",
                "news",
                {"text": "str", "source": "str"},
                self.news_tools.analyze_sentiment
            )
    
    def _register_tool(self, name: str, description: str, category: str, 
                      parameters: Dict[str, Any], function: Callable):
        """注册单个工具"""
        tool_info = ToolInfo(
            name=name,
            description=description,
            category=category,
            parameters=parameters,
            function=function
        )
        self.tools[name] = tool_info
        logger.debug(f"📝 注册工具: {name}")
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        if not self.initialized:
            raise RuntimeError("工具链未初始化")
        
        if tool_name not in self.tools:
            raise ValueError(f"工具不存在: {tool_name}")
        
        tool = self.tools[tool_name]
        
        try:
            logger.info(f"🔧 调用工具: {tool_name}")
            start_time = datetime.now()
            
            # 调用工具函数
            if asyncio.iscoroutinefunction(tool.function):
                result = await tool.function(**parameters)
            else:
                result = tool.function(**parameters)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ 工具调用完成: {tool_name} ({duration:.2f}s)")
            
            return {
                "success": True,
                "tool_name": tool_name,
                "result": result,
                "duration": duration,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 工具调用失败: {tool_name} - {e}")
            return {
                "success": False,
                "tool_name": tool_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        tools_list = []
        
        for name, tool in self.tools.items():
            tools_list.append({
                "name": name,
                "description": tool.description,
                "category": tool.category,
                "parameters": tool.parameters
            })
        
        return tools_list
    
    async def get_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """按类别获取工具"""
        tools_list = []
        
        for name, tool in self.tools.items():
            if tool.category == category:
                tools_list.append({
                    "name": name,
                    "description": tool.description,
                    "parameters": tool.parameters
                })
        
        return tools_list
    
    async def reload(self):
        """重新加载工具链"""
        logger.info("🔄 重新加载工具链...")
        
        # 清空现有工具
        self.tools.clear()
        
        # 重新初始化
        if self.data_tools:
            await self.data_tools.reload()
        
        if self.analysis_tools:
            await self.analysis_tools.reload()
        
        if self.news_tools:
            await self.news_tools.reload()
        
        # 重新注册工具
        await self._register_tools()
        
        logger.info(f"✅ 工具链重新加载完成，共{len(self.tools)}个工具")
    
    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理工具链资源...")
        
        if self.data_tools:
            await self.data_tools.cleanup()
        
        if self.analysis_tools:
            await self.analysis_tools.cleanup()
        
        if self.news_tools:
            await self.news_tools.cleanup()
        
        self.tools.clear()
        self.initialized = False
        
        logger.info("✅ 工具链资源清理完成")
