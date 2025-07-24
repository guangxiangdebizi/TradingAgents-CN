#!/usr/bin/env python3
"""
OpenAI 适配器
"""

import logging
from typing import Dict, List, Any, Optional, AsyncGenerator
from .base import BaseLLMAdapter

logger = logging.getLogger(__name__)

class OpenAIAdapter(BaseLLMAdapter):
    """OpenAI 适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化OpenAI客户端"""
        try:
            from openai import AsyncOpenAI
            
            if self.api_key:
                self.client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                logger.info(f"✅ OpenAI客户端初始化成功: {self.model_name}")
            else:
                logger.warning("⚠️ OpenAI API密钥未配置")
                
        except ImportError:
            logger.error("❌ OpenAI包未安装，请运行: pip install openai")
            self.enabled = False
        except Exception as e:
            logger.error(f"❌ OpenAI客户端初始化失败: {e}")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """检查适配器是否可用"""
        return self.enabled and self.client is not None and self.api_key
    
    async def chat_completion(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """聊天完成"""
        if not self.is_enabled():
            return {
                "success": False,
                "error": "OpenAI适配器未启用或配置不完整"
            }
        
        try:
            # 提取参数
            max_tokens = kwargs.get("max_tokens", 2000)
            temperature = kwargs.get("temperature", 0.1)
            stream = kwargs.get("stream", False)
            
            # 构建请求参数
            request_params = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": stream
            }
            
            # 发送请求
            response = await self.client.chat.completions.create(**request_params)
            
            if response.choices:
                choice = response.choices[0]
                usage = response.usage
                
                return {
                    "success": True,
                    "content": choice.message.content,
                    "usage": {
                        "prompt_tokens": usage.prompt_tokens if usage else 0,
                        "completion_tokens": usage.completion_tokens if usage else 0,
                        "total_tokens": usage.total_tokens if usage else 0
                    },
                    "model": self.model_name,
                    "provider": "openai"
                }
            else:
                return {
                    "success": False,
                    "error": "OpenAI API返回空响应"
                }
                
        except Exception as e:
            logger.error(f"❌ OpenAI聊天完成失败: {e}")
            return {
                "success": False,
                "error": f"OpenAI请求失败: {str(e)}"
            }
    
    async def stream_chat_completion(self, messages: List[Dict], **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """流式聊天完成"""
        if not self.is_enabled():
            yield {
                "success": False,
                "error": "OpenAI适配器未启用或配置不完整"
            }
            return
        
        try:
            # 提取参数
            max_tokens = kwargs.get("max_tokens", 2000)
            temperature = kwargs.get("temperature", 0.1)
            
            # 构建请求参数
            request_params = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True
            }
            
            # 发送流式请求
            stream = await self.client.chat.completions.create(**request_params)
            
            async for chunk in stream:
                if chunk.choices:
                    choice = chunk.choices[0]
                    if choice.delta and choice.delta.content:
                        yield {
                            "success": True,
                            "content": choice.delta.content,
                            "delta": choice.delta.content,
                            "model": self.model_name,
                            "provider": "openai"
                        }
                    
        except Exception as e:
            logger.error(f"❌ OpenAI流式聊天失败: {e}")
            yield {
                "success": False,
                "error": f"OpenAI流式请求失败: {str(e)}"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        if not self.is_enabled():
            return {
                "status": "unhealthy",
                "provider": "openai",
                "model": self.model_name,
                "error": "适配器未启用或配置不完整"
            }
        
        try:
            # 发送简单的测试请求
            test_messages = [{"role": "user", "content": "Hello"}]
            
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=test_messages,
                max_tokens=10
            )
            
            if response.choices:
                return {
                    "status": "healthy",
                    "provider": "openai",
                    "model": self.model_name,
                    "api_key_configured": bool(self.api_key)
                }
            else:
                return {
                    "status": "unhealthy",
                    "provider": "openai",
                    "model": self.model_name,
                    "error": "API返回空响应"
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "openai",
                "model": self.model_name,
                "error": str(e)
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": "openai",
            "model": self.model_name,
            "type": "chat",
            "max_tokens": 4096,
            "supports_streaming": True,
            "supports_function_calling": True,
            "enabled": self.is_enabled()
        }
