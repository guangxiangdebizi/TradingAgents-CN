#!/usr/bin/env python3
"""
LLM集成的工具链管理器
基于tradingagents的设计，支持LLM Function Calling
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from .toolkit_manager import ToolkitManager, ToolInfo

logger = logging.getLogger(__name__)

class ToolCategory(Enum):
    """工具分类"""
    DATA = "data"
    ANALYSIS = "analysis"
    NEWS = "news"
    MARKET = "market"
    FUNDAMENTALS = "fundamentals"
    TECHNICAL = "technical"
    SENTIMENT = "sentiment"

@dataclass
class LLMToolSchema:
    """LLM工具模式定义"""
    type: str = "function"
    function: Dict[str, Any] = None

@dataclass
class FunctionSchema:
    """函数模式定义"""
    name: str
    description: str
    parameters: Dict[str, Any]

class LLMToolkitManager(ToolkitManager):
    """LLM集成的工具链管理器"""
    
    def __init__(self):
        super().__init__()
        self.llm_tools: Dict[str, LLMToolSchema] = {}
        self.tool_schemas: Dict[str, FunctionSchema] = {}
    
    async def initialize(self):
        """初始化工具链"""
        await super().initialize()
        
        # 生成LLM工具模式
        await self._generate_llm_schemas()
        
        logger.info(f"✅ LLM工具链初始化完成，共{len(self.llm_tools)}个LLM工具")
    
    async def _generate_llm_schemas(self):
        """生成LLM工具模式"""
        for tool_name, tool_info in self.tools.items():
            # 生成OpenAI Function Calling格式的模式
            function_schema = FunctionSchema(
                name=tool_name,
                description=tool_info.description,
                parameters=self._convert_to_json_schema(tool_info.parameters)
            )
            
            llm_tool_schema = LLMToolSchema(
                type="function",
                function=asdict(function_schema)
            )
            
            self.tool_schemas[tool_name] = function_schema
            self.llm_tools[tool_name] = llm_tool_schema
            
            logger.debug(f"📝 生成LLM工具模式: {tool_name}")
    
    def _convert_to_json_schema(self, parameters: Dict[str, str]) -> Dict[str, Any]:
        """转换参数为JSON Schema格式"""
        properties = {}
        required = []
        
        for param_name, param_type in parameters.items():
            if param_type == "str":
                properties[param_name] = {"type": "string"}
            elif param_type == "int":
                properties[param_name] = {"type": "integer"}
            elif param_type == "float":
                properties[param_name] = {"type": "number"}
            elif param_type == "bool":
                properties[param_name] = {"type": "boolean"}
            elif param_type == "list":
                properties[param_name] = {"type": "array"}
            elif param_type == "dict":
                properties[param_name] = {"type": "object"}
            else:
                properties[param_name] = {"type": "string"}
            
            required.append(param_name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
    
    async def get_llm_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取LLM工具列表"""
        tools = []
        
        for tool_name, llm_tool in self.llm_tools.items():
            if category:
                tool_info = self.tools.get(tool_name)
                if tool_info and tool_info.category != category:
                    continue
            
            tools.append(asdict(llm_tool))
        
        return tools
    
    async def get_openai_functions(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取OpenAI Function Calling格式的工具"""
        functions = []
        
        for tool_name, function_schema in self.tool_schemas.items():
            if category:
                tool_info = self.tools.get(tool_name)
                if tool_info and tool_info.category != category:
                    continue
            
            functions.append(asdict(function_schema))
        
        return functions
    
    async def call_llm_tool(self, function_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用LLM工具
        
        Args:
            function_call: LLM返回的函数调用信息
                {
                    "name": "tool_name",
                    "arguments": "{\"param1\": \"value1\"}"
                }
        """
        try:
            tool_name = function_call.get("name")
            arguments_str = function_call.get("arguments", "{}")
            
            # 解析参数
            try:
                arguments = json.loads(arguments_str)
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"参数解析失败: {e}",
                    "tool_name": tool_name
                }
            
            # 调用工具
            result = await self.call_tool(tool_name, arguments)
            
            # 添加LLM特定的信息
            result["function_call"] = function_call
            
            return result
            
        except Exception as e:
            logger.error(f"❌ LLM工具调用失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "function_call": function_call
            }
    
    async def get_unified_tools(self) -> Dict[str, Any]:
        """获取统一工具接口"""
        return {
            "stock_market_data_unified": {
                "name": "get_stock_market_data_unified",
                "description": "统一的股票市场数据工具，自动识别股票类型并获取价格和技术指标",
                "category": "market",
                "parameters": {
                    "ticker": "str",
                    "start_date": "str", 
                    "end_date": "str"
                }
            },
            "stock_fundamentals_unified": {
                "name": "get_stock_fundamentals_unified", 
                "description": "统一的股票基本面数据工具，获取财务数据和公司信息",
                "category": "fundamentals",
                "parameters": {
                    "ticker": "str",
                    "start_date": "str",
                    "end_date": "str"
                }
            },
            "stock_news_unified": {
                "name": "get_stock_news_unified",
                "description": "统一的股票新闻工具，获取相关新闻和情感分析",
                "category": "news", 
                "parameters": {
                    "ticker": "str",
                    "days": "int"
                }
            }
        }
    
    async def register_unified_tool(self, tool_name: str, description: str, 
                                  category: str, parameters: Dict[str, str], 
                                  function: Callable):
        """注册统一工具"""
        # 注册到基础工具链
        self._register_tool(tool_name, description, category, parameters, function)
        
        # 生成LLM模式
        function_schema = FunctionSchema(
            name=tool_name,
            description=description,
            parameters=self._convert_to_json_schema(parameters)
        )
        
        llm_tool_schema = LLMToolSchema(
            type="function",
            function=asdict(function_schema)
        )
        
        self.tool_schemas[tool_name] = function_schema
        self.llm_tools[tool_name] = llm_tool_schema
        
        logger.info(f"✅ 注册统一工具: {tool_name}")
    
    async def get_tools_for_task(self, task_type: str) -> List[Dict[str, Any]]:
        """根据任务类型获取推荐工具"""
        task_tool_mapping = {
            "stock_analysis": ["get_stock_market_data_unified", "get_stock_fundamentals_unified"],
            "technical_analysis": ["get_stock_data", "calculate_technical_indicators"],
            "fundamental_analysis": ["get_financial_data", "perform_fundamental_analysis"],
            "news_analysis": ["get_stock_news", "analyze_sentiment"],
            "market_research": ["get_market_data", "get_stock_news_unified"]
        }
        
        recommended_tools = task_tool_mapping.get(task_type, [])
        tools = []
        
        for tool_name in recommended_tools:
            if tool_name in self.llm_tools:
                tools.append(asdict(self.llm_tools[tool_name]))
        
        return tools
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        base_health = await super().get_available_tools()
        
        return {
            "status": "healthy" if self.initialized else "unhealthy",
            "total_tools": len(self.tools),
            "llm_tools": len(self.llm_tools),
            "categories": list(set(tool.category for tool in self.tools.values())),
            "unified_tools_available": len(await self.get_unified_tools()),
            "last_check": datetime.now().isoformat()
        }
