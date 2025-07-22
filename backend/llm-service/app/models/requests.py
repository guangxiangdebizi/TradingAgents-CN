#!/usr/bin/env python3
"""
LLM Service 请求模型
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="消息角色: system, user, assistant")
    content: str = Field(..., description="消息内容")

class ChatCompletionRequest(BaseModel):
    """聊天完成请求"""
    model: str = Field(default="auto", description="模型名称，auto表示自动选择")
    messages: List[ChatMessage] = Field(..., description="聊天消息列表")
    task_type: str = Field(default="general", description="任务类型，用于智能路由")
    max_tokens: int = Field(default=2000, description="最大生成token数")
    temperature: float = Field(default=0.1, description="温度参数")
    stream: bool = Field(default=False, description="是否流式返回")
    user_id: Optional[str] = Field(default=None, description="用户ID，用于统计")

class ModelListRequest(BaseModel):
    """模型列表请求"""
    include_unhealthy: bool = Field(default=False, description="是否包含不健康的模型")

class UsageStatsRequest(BaseModel):
    """使用统计请求"""
    user_id: Optional[str] = Field(default=None, description="用户ID")
    model: Optional[str] = Field(default=None, description="模型名称")
    days: int = Field(default=7, description="统计天数")
    group_by: str = Field(default="day", description="分组方式: hour, day, week")
