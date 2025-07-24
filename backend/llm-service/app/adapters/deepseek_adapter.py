#!/usr/bin/env python3
"""
DeepSeek适配器
"""

import asyncio
from typing import Dict, List, Any, AsyncGenerator
import tiktoken
import logging

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

from .base import BaseLLMAdapter

logger = logging.getLogger(__name__)

class DeepSeekAdapter(BaseLLMAdapter):
    """DeepSeek模型适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package is required for DeepSeek adapter")
        
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url or "https://api.deepseek.com"
        )
        
        # 初始化tokenizer
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.tokenizer = None
            logger.warning("⚠️ tiktoken初始化失败，将使用估算方式计算token")
    
    async def chat_completion(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """DeepSeek聊天完成"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 2000),
                temperature=kwargs.get("temperature", 0.1),
                stream=False
            )
            
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            return self._format_success_response(
                content=response.choices[0].message.content,
                usage=usage
            )
            
        except Exception as e:
            return await self._handle_error(e, "chat_completion")
    
    async def chat_completion_stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator:
        """DeepSeek流式聊天完成"""
        try:
            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 2000),
                temperature=kwargs.get("temperature", 0.1),
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield {
                        "success": True,
                        "content": chunk.choices[0].delta.content,
                        "provider": self.provider_name,
                        "model": self.model_name
                    }
                    
        except Exception as e:
            yield await self._handle_error(e, "chat_completion_stream")
    
    def calculate_tokens(self, text: str) -> int:
        """计算Token数量"""
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except Exception:
                pass
        
        # 估算方式：中文约1.5字符/token，英文约4字符/token
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        other_chars = len(text) - chinese_chars
        
        return int(chinese_chars / 1.5 + other_chars / 4)
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取DeepSeek模型信息"""
        return {
            "provider": "deepseek",
            "model": self.model_name,
            "max_tokens": 32768,
            "supports_streaming": True,
            "cost_per_1k_tokens": {
                "input": 0.0014,  # $0.14/1M tokens
                "output": 0.0028  # $0.28/1M tokens
            },
            "strengths": ["中文理解", "代码生成", "推理能力", "数学计算"],
            "best_for": ["financial_analysis", "code_generation", "reasoning", "chinese_tasks"]
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查 - 只检查配置，不做实际API调用"""
        if not self.is_enabled():
            return {
                "status": "unhealthy",
                "provider": "deepseek",
                "model": self.model_name,
                "error": "适配器未启用或配置不完整"
            }

        # 只检查配置是否完整，不做实际API调用
        try:
            has_api_key = bool(self.api_key)
            has_client = self.client is not None

            if has_api_key and has_client:
                return {
                    "status": "healthy",
                    "provider": "deepseek",
                    "model": self.model_name,
                    "api_key_configured": True,
                    "client_initialized": True
                }
            else:
                return {
                    "status": "unhealthy",
                    "provider": "deepseek",
                    "model": self.model_name,
                    "error": f"配置不完整 - API Key: {has_api_key}, Client: {has_client}"
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "deepseek",
                "model": self.model_name,
                "error": f"健康检查异常: {str(e)}"
            }
