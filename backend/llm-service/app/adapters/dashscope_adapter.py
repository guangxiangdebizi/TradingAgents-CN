#!/usr/bin/env python3
"""
阿里百炼 DashScope 适配器
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator
from .base import BaseLLMAdapter

logger = logging.getLogger(__name__)

class DashScopeAdapter(BaseLLMAdapter):
    """阿里百炼 DashScope 适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化DashScope客户端"""
        try:
            import dashscope
            from dashscope import Generation
            
            if self.api_key:
                dashscope.api_key = self.api_key
                self.client = Generation
                logger.info(f"✅ DashScope客户端初始化成功: {self.model_name}")
            else:
                logger.warning("⚠️ DashScope API密钥未配置")
                
        except ImportError:
            logger.error("❌ DashScope包未安装，请运行: pip install dashscope")
            self.enabled = False
        except Exception as e:
            logger.error(f"❌ DashScope客户端初始化失败: {e}")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """检查适配器是否可用"""
        return self.enabled and self.client is not None and self.api_key
    
    async def chat_completion(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """聊天完成"""
        if not self.is_enabled():
            return {
                "success": False,
                "error": "DashScope适配器未启用或配置不完整"
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
                "result_format": "message",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": stream
            }
            
            # 在线程池中执行同步调用
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.call(**request_params)
            )
            
            if response.status_code == 200:
                output = response.output
                usage = response.usage
                
                return {
                    "success": True,
                    "content": output.choices[0].message.content,
                    "usage": {
                        "prompt_tokens": usage.input_tokens,
                        "completion_tokens": usage.output_tokens,
                        "total_tokens": usage.total_tokens
                    },
                    "model": self.model_name,
                    "provider": "dashscope"
                }
            else:
                return {
                    "success": False,
                    "error": f"DashScope API错误: {response.message}"
                }
                
        except Exception as e:
            logger.error(f"❌ DashScope聊天完成失败: {e}")
            return {
                "success": False,
                "error": f"DashScope请求失败: {str(e)}"
            }
    
    async def chat_completion_stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """流式聊天完成"""
        if not self.is_enabled():
            yield {
                "success": False,
                "error": "DashScope适配器未启用或配置不完整"
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
                "result_format": "message",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True,
                "incremental_output": True
            }
            
            # 在线程池中执行同步调用
            responses = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.call(**request_params)
            )
            
            for response in responses:
                if response.status_code == 200:
                    output = response.output
                    if output.choices:
                        content = output.choices[0].message.content
                        yield {
                            "success": True,
                            "content": content,
                            "delta": content,
                            "model": self.model_name,
                            "provider": "dashscope"
                        }
                else:
                    yield {
                        "success": False,
                        "error": f"DashScope流式API错误: {response.message}"
                    }
                    break
                    
        except Exception as e:
            logger.error(f"❌ DashScope流式聊天失败: {e}")
            yield {
                "success": False,
                "error": f"DashScope流式请求失败: {str(e)}"
            }

    def calculate_tokens(self, text: str) -> int:
        """计算Token数量 - 简单估算"""
        try:
            # 对于中文文本，大约1个字符=1个token
            # 对于英文文本，大约4个字符=1个token
            # 这里使用简单的估算方法
            chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
            english_chars = len(text) - chinese_chars

            # 中文字符按1:1计算，英文字符按4:1计算
            estimated_tokens = chinese_chars + (english_chars // 4)
            return max(estimated_tokens, 1)  # 至少返回1个token

        except Exception as e:
            logger.warning(f"⚠️ Token计算失败: {e}")
            # 如果计算失败，使用简单的字符数除以4的方法
            return max(len(text) // 4, 1)

    async def health_check(self) -> Dict[str, Any]:
        """健康检查 - 只检查配置，不做实际API调用"""
        if not self.is_enabled():
            return {
                "status": "unhealthy",
                "provider": "dashscope",
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
                    "provider": "dashscope",
                    "model": self.model_name,
                    "api_key_configured": True,
                    "client_initialized": True
                }
            else:
                return {
                    "status": "unhealthy",
                    "provider": "dashscope",
                    "model": self.model_name,
                    "error": f"配置不完整 - API Key: {has_api_key}, Client: {has_client}"
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "dashscope",
                "model": self.model_name,
                "error": f"健康检查异常: {str(e)}"
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": "dashscope",
            "model": self.model_name,
            "type": "chat",
            "max_tokens": 8192,
            "supports_streaming": True,
            "supports_function_calling": True,
            "enabled": self.is_enabled()
        }
