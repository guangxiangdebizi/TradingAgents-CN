#!/usr/bin/env python3
"""
LLM适配器基类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, AsyncGenerator
import logging

logger = logging.getLogger(__name__)

class BaseLLMAdapter(ABC):
    """LLM适配器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = config.get("provider_name")
        self.model_name = config.get("model_name")
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
        self.enabled = config.get("enabled", True)
        
        # 验证必需的配置
        self._validate_config()
    
    def _validate_config(self):
        """验证配置"""
        if not self.provider_name:
            raise ValueError("provider_name is required")
        if not self.model_name:
            raise ValueError("model_name is required")
        if not self.api_key:
            logger.warning(f"⚠️ {self.provider_name} API key not configured")
    
    @abstractmethod
    async def chat_completion(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        聊天完成
        
        Args:
            messages: 聊天消息列表
            **kwargs: 其他参数
            
        Returns:
            {
                "success": bool,
                "content": str,
                "usage": {
                    "prompt_tokens": int,
                    "completion_tokens": int,
                    "total_tokens": int
                },
                "model": str,
                "provider": str,
                "error": str  # 如果失败
            }
        """
        pass
    
    @abstractmethod
    async def chat_completion_stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator:
        """流式聊天完成"""
        pass
    
    @abstractmethod
    def calculate_tokens(self, text: str) -> int:
        """计算Token数量"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            {
                "provider": str,
                "model": str,
                "max_tokens": int,
                "supports_streaming": bool,
                "cost_per_1k_tokens": {
                    "input": float,
                    "output": float
                },
                "strengths": List[str],
                "best_for": List[str]
            }
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass
    
    def is_enabled(self) -> bool:
        """检查是否启用"""
        return self.enabled and bool(self.api_key)
    
    def get_identifier(self) -> str:
        """获取适配器标识符"""
        return f"{self.provider_name}:{self.model_name}"
    
    async def _handle_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """处理错误"""
        error_msg = str(error)
        logger.error(f"❌ {self.get_identifier()} {operation} 失败: {error_msg}")
        
        return {
            "success": False,
            "error": error_msg,
            "provider": self.provider_name,
            "model": self.model_name
        }
    
    def _format_success_response(self, content: str, usage: Dict[str, int]) -> Dict[str, Any]:
        """格式化成功响应"""
        return {
            "success": True,
            "content": content,
            "usage": usage,
            "model": self.model_name,
            "provider": self.provider_name
        }
