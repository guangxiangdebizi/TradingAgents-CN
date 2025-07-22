"""
响应模型定义
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class AnalysisResponse(BaseModel):
    """分析响应模型"""
    
    success: bool = Field(..., description="是否成功")
    symbol: str = Field(..., description="股票代码")
    analysis_type: str = Field(..., description="分析类型")
    result: Optional[Dict[str, Any]] = Field(default=None, description="分析结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    timestamp: str = Field(..., description="时间戳")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "symbol": "AAPL",
                "analysis_type": "comprehensive",
                "result": {
                    "reports": {
                        "fundamentals": "基本面分析报告...",
                        "technical": "技术分析报告...",
                        "final_recommendation": "最终投资建议..."
                    },
                    "data": {
                        "stock_data": {},
                        "financial_data": {}
                    }
                },
                "timestamp": "2025-01-22T10:00:00Z"
            }
        }

class ToolCallResponse(BaseModel):
    """工具调用响应模型"""
    
    success: bool = Field(..., description="是否成功")
    tool_name: str = Field(..., description="工具名称")
    result: Optional[Dict[str, Any]] = Field(default=None, description="调用结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    timestamp: str = Field(..., description="时间戳")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "tool_name": "get_stock_data",
                "result": {
                    "symbol": "AAPL",
                    "data": {
                        "current_price": 150.00,
                        "change": 1.50,
                        "change_percent": 1.01
                    }
                },
                "timestamp": "2025-01-22T10:00:00Z"
            }
        }
