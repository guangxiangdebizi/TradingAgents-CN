"""
请求模型定义
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class AnalysisRequest(BaseModel):
    """分析请求模型"""
    
    symbol: str = Field(..., description="股票代码")
    analysis_type: str = Field(
        default="comprehensive",
        description="分析类型: fundamentals, technical, comprehensive, debate"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="分析参数"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "AAPL",
                "analysis_type": "comprehensive",
                "parameters": {
                    "enable_fundamentals": True,
                    "enable_technical": True,
                    "enable_debate": True,
                    "model_name": "deepseek-chat"
                }
            }
        }

class ToolCallRequest(BaseModel):
    """工具调用请求模型"""
    
    tool_name: str = Field(..., description="工具名称")
    parameters: Dict[str, Any] = Field(..., description="工具参数")
    
    class Config:
        schema_extra = {
            "example": {
                "tool_name": "get_stock_data",
                "parameters": {
                    "symbol": "AAPL",
                    "period": "1y"
                }
            }
        }
