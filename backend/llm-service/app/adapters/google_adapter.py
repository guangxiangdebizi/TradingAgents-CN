#!/usr/bin/env python3
"""
Google Gemini 适配器
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator
from .base import BaseLLMAdapter

logger = logging.getLogger(__name__)

class GoogleAdapter(BaseLLMAdapter):
    """Google Gemini 适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化Google客户端"""
        try:
            import google.generativeai as genai
            
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.client = genai
                logger.info(f"✅ Google Gemini客户端初始化成功: {self.model_name}")
            else:
                logger.warning("⚠️ Google API密钥未配置")
                
        except ImportError:
            logger.error("❌ Google AI包未安装，请运行: pip install google-generativeai")
            self.enabled = False
        except Exception as e:
            logger.error(f"❌ Google客户端初始化失败: {e}")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """检查适配器是否可用"""
        return self.enabled and self.client is not None and self.api_key
    
    def _convert_messages_to_gemini_format(self, messages: List[Dict]) -> List[Dict]:
        """转换消息格式为Gemini格式"""
        gemini_messages = []
        
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            
            # Gemini使用不同的角色名称
            if role == "user":
                gemini_role = "user"
            elif role == "assistant":
                gemini_role = "model"
            elif role == "system":
                # Gemini没有system角色，将其转换为user消息
                gemini_role = "user"
                content = f"System: {content}"
            else:
                gemini_role = "user"
            
            gemini_messages.append({
                "role": gemini_role,
                "parts": [{"text": content}]
            })
        
        return gemini_messages
    
    async def chat_completion(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """聊天完成"""
        if not self.is_enabled():
            return {
                "success": False,
                "error": "Google适配器未启用或配置不完整"
            }
        
        try:
            # 提取参数
            max_tokens = kwargs.get("max_tokens", 2000)
            temperature = kwargs.get("temperature", 0.1)
            
            # 创建模型实例
            model = self.client.GenerativeModel(self.model_name)
            
            # 转换消息格式
            gemini_messages = self._convert_messages_to_gemini_format(messages)
            
            # 构建对话历史
            chat_history = gemini_messages[:-1] if len(gemini_messages) > 1 else []
            current_message = gemini_messages[-1]["parts"][0]["text"]
            
            # 配置生成参数
            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            }
            
            # 在线程池中执行同步调用
            if chat_history:
                chat = model.start_chat(history=chat_history)
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: chat.send_message(
                        current_message,
                        generation_config=generation_config
                    )
                )
            else:
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: model.generate_content(
                        current_message,
                        generation_config=generation_config
                    )
                )
            
            if response.text:
                return {
                    "success": True,
                    "content": response.text,
                    "usage": {
                        "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                        "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                        "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
                    },
                    "model": self.model_name,
                    "provider": "google"
                }
            else:
                return {
                    "success": False,
                    "error": "Google API返回空响应"
                }
                
        except Exception as e:
            logger.error(f"❌ Google聊天完成失败: {e}")
            return {
                "success": False,
                "error": f"Google请求失败: {str(e)}"
            }
    
    async def chat_completion_stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """流式聊天完成"""
        if not self.is_enabled():
            yield {
                "success": False,
                "error": "Google适配器未启用或配置不完整"
            }
            return
        
        try:
            # 提取参数
            max_tokens = kwargs.get("max_tokens", 2000)
            temperature = kwargs.get("temperature", 0.1)
            
            # 创建模型实例
            model = self.client.GenerativeModel(self.model_name)
            
            # 转换消息格式
            gemini_messages = self._convert_messages_to_gemini_format(messages)
            
            # 构建对话历史
            chat_history = gemini_messages[:-1] if len(gemini_messages) > 1 else []
            current_message = gemini_messages[-1]["parts"][0]["text"]
            
            # 配置生成参数
            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            }
            
            # 在线程池中执行同步调用
            if chat_history:
                chat = model.start_chat(history=chat_history)
                response_stream = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: chat.send_message(
                        current_message,
                        generation_config=generation_config,
                        stream=True
                    )
                )
            else:
                response_stream = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: model.generate_content(
                        current_message,
                        generation_config=generation_config,
                        stream=True
                    )
                )
            
            for chunk in response_stream:
                if chunk.text:
                    yield {
                        "success": True,
                        "content": chunk.text,
                        "delta": chunk.text,
                        "model": self.model_name,
                        "provider": "google"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Google流式聊天失败: {e}")
            yield {
                "success": False,
                "error": f"Google流式请求失败: {str(e)}"
            }

    def calculate_tokens(self, text: str) -> int:
        """计算Token数量 - 简单估算"""
        try:
            # 对于Gemini模型，使用类似GPT的估算方法
            # 大约4个字符=1个token（英文）
            # 中文字符按1:1计算
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
                "provider": "google",
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
                    "provider": "google",
                    "model": self.model_name,
                    "api_key_configured": True,
                    "client_initialized": True
                }
            else:
                return {
                    "status": "unhealthy",
                    "provider": "google",
                    "model": self.model_name,
                    "error": f"配置不完整 - API Key: {has_api_key}, Client: {has_client}"
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "google",
                "model": self.model_name,
                "error": f"健康检查异常: {str(e)}"
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": "google",
            "model": self.model_name,
            "type": "chat",
            "max_tokens": 8192,
            "supports_streaming": True,
            "supports_function_calling": True,
            "enabled": self.is_enabled()
        }
