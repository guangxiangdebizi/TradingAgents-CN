"""
Embedding服务
支持多种Embedding模型提供商
"""

import asyncio
import logging
import os
from typing import List, Optional, Dict, Any
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Embedding服务"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = "dashscope"
        self.default_model = "text-embedding-v3"
        self.session: Optional[aiohttp.ClientSession] = None
        self.initialized = False
    
    async def initialize(self):
        """初始化Embedding服务"""
        try:
            logger.info("🔢 初始化Embedding服务...")
            
            # 创建HTTP会话
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # 初始化各种提供商
            await self._initialize_providers()
            
            self.initialized = True
            logger.info("✅ Embedding服务初始化完成")
            
        except Exception as e:
            logger.error(f"❌ Embedding服务初始化失败: {e}")
            raise
    
    async def _initialize_providers(self):
        """初始化Embedding提供商"""
        
        # 阿里百炼 DashScope
        dashscope_key = os.getenv('DASHSCOPE_API_KEY')
        if dashscope_key:
            try:
                import dashscope
                from dashscope import TextEmbedding
                
                dashscope.api_key = dashscope_key
                self.providers["dashscope"] = {
                    "client": dashscope,
                    "embedding_func": TextEmbedding,
                    "model": "text-embedding-v3",
                    "available": True
                }
                logger.info("✅ DashScope Embedding已配置")
            except ImportError:
                logger.warning("⚠️ DashScope包未安装")
                self.providers["dashscope"] = {"available": False}
        
        # OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            try:
                from openai import AsyncOpenAI
                
                self.providers["openai"] = {
                    "client": AsyncOpenAI(api_key=openai_key),
                    "model": "text-embedding-3-small",
                    "available": True
                }
                logger.info("✅ OpenAI Embedding已配置")
            except ImportError:
                logger.warning("⚠️ OpenAI包未安装")
                self.providers["openai"] = {"available": False}
        
        # DeepSeek
        deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        if deepseek_key:
            try:
                from openai import AsyncOpenAI
                
                self.providers["deepseek"] = {
                    "client": AsyncOpenAI(
                        api_key=deepseek_key,
                        base_url="https://api.deepseek.com"
                    ),
                    "model": "text-embedding-3-small",
                    "available": True
                }
                logger.info("✅ DeepSeek Embedding已配置")
            except ImportError:
                logger.warning("⚠️ DeepSeek配置失败")
                self.providers["deepseek"] = {"available": False}
        
        # 本地Ollama
        try:
            from openai import AsyncOpenAI

            self.providers["ollama"] = {
                "client": AsyncOpenAI(
                    base_url="http://localhost:11434/v1",
                    api_key="ollama"  # Ollama不需要真实API key
                ),
                "model": "nomic-embed-text",
                "available": True
            }
            logger.info("✅ Ollama Embedding已配置")
        except Exception:
            self.providers["ollama"] = {"available": False}
        
        # 检查是否有可用的提供商
        available_providers = [name for name, info in self.providers.items() if info.get("available")]
        if not available_providers:
            logger.warning("⚠️ 没有可用的Embedding提供商，将使用零向量")
            self.default_provider = "zero"
        else:
            # 设置默认提供商
            if "dashscope" in available_providers:
                self.default_provider = "dashscope"
            elif "openai" in available_providers:
                self.default_provider = "openai"
            else:
                self.default_provider = available_providers[0]
            
            logger.info(f"🎯 默认Embedding提供商: {self.default_provider}")
    
    async def generate_embedding(self, text: str, provider: Optional[str] = None, 
                                model: Optional[str] = None) -> List[float]:
        """生成文本的Embedding向量"""
        if not self.initialized:
            raise RuntimeError("Embedding服务未初始化")
        
        # 使用默认提供商
        if not provider:
            provider = self.default_provider
        
        # 特殊处理：零向量提供商
        if provider == "zero" or provider not in self.providers:
            logger.debug(f"⚠️ 使用零向量: {provider}")
            return [0.0] * 1024  # 返回1024维零向量
        
        provider_info = self.providers[provider]
        if not provider_info.get("available"):
            logger.warning(f"⚠️ 提供商不可用，使用零向量: {provider}")
            return [0.0] * 1024
        
        try:
            if provider == "dashscope":
                return await self._generate_dashscope_embedding(text, model)
            elif provider in ["openai", "deepseek"]:
                return await self._generate_openai_embedding(text, provider, model)
            elif provider == "ollama":
                return await self._generate_ollama_embedding(text, model)
            else:
                raise ValueError(f"不支持的提供商: {provider}")
                
        except Exception as e:
            logger.error(f"❌ Embedding生成失败: {provider} - {e}")
            # 降级到零向量
            logger.warning(f"⚠️ 降级到零向量")
            return [0.0] * 1024
    
    async def _generate_dashscope_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """生成DashScope Embedding"""
        provider_info = self.providers["dashscope"]
        TextEmbedding = provider_info["embedding_func"]
        
        if not model:
            model = provider_info["model"]
        
        # 在线程池中执行同步调用
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: TextEmbedding.call(model=model, input=text)
        )
        
        if response.status_code == 200:
            return response.output['embeddings'][0]['embedding']
        else:
            raise Exception(f"DashScope API错误: {response.status_code}")
    
    async def _generate_openai_embedding(self, text: str, provider: str, model: Optional[str] = None) -> List[float]:
        """生成OpenAI/DeepSeek Embedding"""
        provider_info = self.providers[provider]
        client = provider_info["client"]
        
        if not model:
            model = provider_info["model"]
        
        response = await client.embeddings.create(
            model=model,
            input=text
        )
        
        return response.data[0].embedding
    
    async def _generate_ollama_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """生成Ollama Embedding"""
        provider_info = self.providers["ollama"]
        client = provider_info["client"]
        
        if not model:
            model = provider_info["model"]
        
        response = await client.embeddings.create(
            model=model,
            input=text
        )
        
        return response.data[0].embedding
    
    async def get_available_providers(self) -> Dict[str, Any]:
        """获取可用的提供商列表"""
        available = {}
        
        for name, info in self.providers.items():
            if info.get("available"):
                available[name] = {
                    "model": info.get("model"),
                    "status": "available"
                }
            else:
                available[name] = {
                    "status": "unavailable"
                }
        
        return available
    
    async def test_provider(self, provider: str) -> Dict[str, Any]:
        """测试提供商连接"""
        try:
            test_text = "这是一个测试文本"
            start_time = datetime.now()
            
            embedding = await self.generate_embedding(test_text, provider)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return {
                "provider": provider,
                "status": "success",
                "dimension": len(embedding),
                "duration": duration,
                "test_text": test_text
            }
            
        except Exception as e:
            return {
                "provider": provider,
                "status": "failed",
                "error": str(e)
            }
    
    async def reload(self):
        """重新加载Embedding服务"""
        logger.info("🔄 重新加载Embedding服务...")
        
        # 重新初始化提供商
        await self._initialize_providers()
        
        logger.info("✅ Embedding服务重新加载完成")
    
    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理Embedding服务资源...")
        
        if self.session:
            await self.session.close()
            self.session = None
        
        self.providers.clear()
        self.initialized = False
        
        logger.info("✅ Embedding服务资源清理完成")
