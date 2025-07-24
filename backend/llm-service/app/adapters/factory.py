#!/usr/bin/env python3
"""
LLM适配器工厂
"""

import os
import logging
from typing import Dict, Any, Optional
from .base import BaseLLMAdapter
from .deepseek_adapter import DeepSeekAdapter
from .dashscope_adapter import DashScopeAdapter
from .google_adapter import GoogleAdapter
from .openai_adapter import OpenAIAdapter

logger = logging.getLogger(__name__)

class AdapterFactory:
    """LLM适配器工厂"""
    
    def __init__(self):
        self.adapter_classes = {
            "deepseek": DeepSeekAdapter,
            "dashscope": DashScopeAdapter,
            "google": GoogleAdapter,
            "openai": OpenAIAdapter,
        }
    
    async def create_adapter(self, provider: str, config: Dict[str, Any]) -> Optional[BaseLLMAdapter]:
        """创建适配器实例"""
        try:
            adapter_class = self.adapter_classes.get(provider)
            if not adapter_class:
                logger.warning(f"⚠️ 不支持的提供商: {provider}")
                return None
            
            adapter = adapter_class(config)
            
            # 检查适配器是否可用
            if not adapter.is_enabled():
                logger.warning(f"⚠️ 适配器未启用: {provider}")
                return None
            
            logger.info(f"✅ 创建适配器成功: {provider}:{config.get('model_name')}")
            return adapter
            
        except Exception as e:
            logger.error(f"❌ 创建适配器失败 {provider}: {e}")
            return None
    
    async def get_all_adapters(self) -> Dict[str, BaseLLMAdapter]:
        """获取所有可用的适配器"""
        adapters = {}
        
        # 从环境变量和配置中获取模型配置
        model_configs = self._get_model_configs()
        
        for model_id, config in model_configs.items():
            provider = config.get("provider_name")
            adapter = await self.create_adapter(provider, config)
            
            if adapter:
                adapters[model_id] = adapter
        
        logger.info(f"✅ 初始化完成，共{len(adapters)}个可用适配器")
        return adapters
    
    def _get_model_configs(self) -> Dict[str, Dict[str, Any]]:
        """获取模型配置"""
        configs = {}
        
        # DeepSeek配置
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_api_key:
            configs["deepseek-chat"] = {
                "provider_name": "deepseek",
                "model_name": "deepseek-chat",
                "api_key": deepseek_api_key,
                "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
                "enabled": True
            }
            

        
        # OpenAI配置
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            configs["gpt-4"] = {
                "provider_name": "openai",
                "model_name": "gpt-4",
                "api_key": openai_api_key,
                "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                "enabled": True
            }

            configs["gpt-3.5-turbo"] = {
                "provider_name": "openai",
                "model_name": "gpt-3.5-turbo",
                "api_key": openai_api_key,
                "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                "enabled": True
            }

        # DashScope配置
        dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
        if dashscope_api_key:
            configs["qwen-plus"] = {
                "provider_name": "dashscope",
                "model_name": "qwen-plus",
                "api_key": dashscope_api_key,
                "enabled": True
            }

            configs["qwen-turbo"] = {
                "provider_name": "dashscope",
                "model_name": "qwen-turbo",
                "api_key": dashscope_api_key,
                "enabled": True
            }



        # Google配置
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if google_api_key:
            configs["gemini-pro"] = {
                "provider_name": "google",
                "model_name": "gemini-pro",
                "api_key": google_api_key,
                "enabled": True
            }

            configs["gemini-1.5-flash"] = {
                "provider_name": "google",
                "model_name": "gemini-1.5-flash",
                "api_key": google_api_key,
                "enabled": True
            }
        
        return configs

# 全局工厂实例
_factory_instance: Optional[AdapterFactory] = None

def get_adapter_factory() -> AdapterFactory:
    """获取适配器工厂实例（单例模式）"""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = AdapterFactory()
    return _factory_instance
