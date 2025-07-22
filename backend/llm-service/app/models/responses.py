#!/usr/bin/env python3
"""
LLM Service 响应模型
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    """聊天消息"""
    role: str
    content: str

class ChatChoice(BaseModel):
    """聊天选择"""
    index: int
    message: ChatMessage
    finish_reason: str

class UsageInfo(BaseModel):
    """使用信息"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    """聊天完成响应"""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: UsageInfo

class ModelInfo(BaseModel):
    """模型信息"""
    id: str
    object: str = "model"
    provider: str
    max_tokens: int
    supports_streaming: bool
    cost_per_1k_tokens: Dict[str, float]
    strengths: List[str]
    best_for: List[str]
    status: str

class ModelListResponse(BaseModel):
    """模型列表响应"""
    object: str = "list"
    data: List[ModelInfo]

class UsageStatsResponse(BaseModel):
    """使用统计响应"""
    success: bool
    data: Dict[str, Any]
