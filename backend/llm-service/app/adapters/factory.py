#!/usr/bin/env python3
"""
LLM适配器工厂
"""

import os
import logging
from typing import Dict, Any, Optional
from .base import BaseLLMAdapter
from .deepseek_adapter import DeepSeekAdapter

logger = logging.getLogger(__name__)

class AdapterFactory:
    """LLM适配器工厂"""
    
    def __init__(self):
        self.adapter_classes = {
            "deepseek": DeepSeekAdapter,
            # 后续添加更多适配器
            # "openai": OpenAIAdapter,
            # "dashscope": DashScopeAdapter,
            # "gemini": GeminiAdapter,
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
            
            configs["deepseek-coder"] = {
                "provider_name": "deepseek",
                "model_name": "deepseek-coder",
                "api_key": deepseek_api_key,
                "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
                "enabled": True
            }
        
        # TODO: 添加其他模型配置
        # OpenAI配置
        # openai_api_key = os.getenv("OPENAI_API_KEY")
        # if openai_api_key:
        #     configs["gpt-4"] = {
        #         "provider_name": "openai",
        #         "model_name": "gpt-4",
        #         "api_key": openai_api_key,
        #         "enabled": True
        #     }
        
        # DashScope配置
        # dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
        # if dashscope_api_key:
        #     configs["qwen-plus"] = {
        #         "provider_name": "dashscope",
        #         "model_name": "qwen-plus",
        #         "api_key": dashscope_api_key,
        #         "enabled": True
        #     }
        
        return configs

# 全局工厂实例
_factory_instance: Optional[AdapterFactory] = None

def get_adapter_factory() -> AdapterFactory:
    """获取适配器工厂实例（单例模式）"""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = AdapterFactory()
    return _factory_instance
