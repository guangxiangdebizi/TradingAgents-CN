"""
基于图的分析器
集成工具链和多智能体协作的分析引擎
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..tools.toolkit_manager import ToolkitManager
from ..graphs.analysis_graph import AnalysisGraph
from ..agents.agent_factory import AgentFactory
from ..memory.memory_client import get_memory_client, MemoryClient

logger = logging.getLogger(__name__)

class GraphAnalyzer:
    """基于图的分析器"""
    
    def __init__(self, memory_service_url: str = "http://localhost:8006"):
        self.toolkit_manager: Optional[ToolkitManager] = None
        self.analysis_graph: Optional[AnalysisGraph] = None
        self.agent_factory: Optional[AgentFactory] = None
        self.memory_client: Optional[MemoryClient] = None
        self.memory_service_url = memory_service_url
        self.initialized = False
    
    async def initialize(self):
        """初始化分析器"""
        try:
            logger.info("🔗 初始化基于图的分析器...")
            
            # 初始化工具链管理器
            self.toolkit_manager = ToolkitManager()
            await self.toolkit_manager.initialize()
            
            # 初始化智能体工厂
            self.agent_factory = AgentFactory()
            await self.agent_factory.initialize()
            
            # 初始化Memory客户端
            self.memory_client = await get_memory_client(self.memory_service_url)
            logger.info("✅ Memory客户端初始化完成")

            # 初始化分析图
            self.analysis_graph = AnalysisGraph(
                toolkit_manager=self.toolkit_manager,
                agent_factory=self.agent_factory,
                memory_client=self.memory_client
            )
            await self.analysis_graph.initialize()

            self.initialized = True
            logger.info("✅ 基于图的分析器初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 基于图的分析器初始化失败: {e}")
            raise
    
    async def analyze_stock(self, symbol: str, analysis_type: str = "comprehensive", 
                           parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """分析股票"""
        if not self.initialized:
            await self.initialize()
        
        try:
            logger.info(f"📊 开始图分析: {symbol} - {analysis_type}")
            
            # 执行分析图
            result = await self.analysis_graph.execute_analysis(
                symbol=symbol,
                analysis_type=analysis_type,
                parameters=parameters
            )
            
            logger.info(f"✅ 图分析完成: {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 图分析失败: {symbol} - {e}")
            return {
                "success": False,
                "symbol": symbol,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        if not self.initialized:
            await self.initialize()
        
        return await self.toolkit_manager.call_tool(tool_name, parameters)
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        if not self.initialized:
            await self.initialize()
        
        return await self.toolkit_manager.get_available_tools()
    
    async def get_available_agents(self) -> List[Dict[str, Any]]:
        """获取可用智能体列表"""
        if not self.initialized:
            await self.initialize()
        
        return await self.agent_factory.get_available_agents()
    
    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理图分析器资源...")
        
        if self.analysis_graph:
            await self.analysis_graph.cleanup()
        
        if self.toolkit_manager:
            await self.toolkit_manager.cleanup()
        
        if self.agent_factory:
            await self.agent_factory.cleanup()
        
        self.initialized = False
        
        logger.info("✅ 图分析器资源清理完成")
