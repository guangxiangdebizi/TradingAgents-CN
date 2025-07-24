#!/usr/bin/env python3
"""
模型智能路由器
"""

import logging
from typing import Dict, List, Any
from ..adapters.base import BaseLLMAdapter

logger = logging.getLogger(__name__)

# 任务类型到模型的映射 (专注于股票分析和工具调用)
TASK_MODEL_MAPPING = {
    "financial_analysis": {
        "primary": ["deepseek-chat", "qwen-plus", "gpt-4", "gemini-pro"],
        "fallback": ["gpt-3.5-turbo", "qwen-turbo", "gemini-1.5-flash"]
    },
    "stock_analysis": {
        "primary": ["deepseek-chat", "qwen-plus", "gpt-4"],
        "fallback": ["gemini-pro", "gpt-3.5-turbo"]
    },
    "tool_calling": {
        "primary": ["gpt-4", "deepseek-chat", "qwen-plus"],
        "fallback": ["gemini-pro", "gpt-3.5-turbo"]
    },
    "data_extraction": {
        "primary": ["gpt-4", "qwen-plus", "gemini-pro"],
        "fallback": ["deepseek-chat", "gpt-3.5-turbo"]
    },
    "market_research": {
        "primary": ["qwen-plus", "deepseek-chat", "gpt-4"],
        "fallback": ["gemini-pro", "gpt-3.5-turbo"]
    },
    "reasoning": {
        "primary": ["deepseek-chat", "gpt-4", "gemini-pro"],
        "fallback": ["qwen-plus", "gpt-3.5-turbo"]
    },
    "chinese_tasks": {
        "primary": ["qwen-plus", "deepseek-chat", "qwen-turbo"],
        "fallback": ["gpt-4", "gemini-pro"]
    },
    "general": {
        "primary": ["deepseek-chat", "qwen-plus", "gpt-4", "gemini-pro"],
        "fallback": ["gpt-3.5-turbo", "qwen-turbo", "gemini-1.5-flash"]
    }
}

class ModelRouter:
    """智能模型路由器"""
    
    def __init__(self, adapters: Dict[str, BaseLLMAdapter]):
        self.adapters = adapters
        self.health_status = {}
        self.performance_metrics = {}
        
        logger.info(f"🎯 模型路由器初始化，支持模型: {list(adapters.keys())}")
    
    async def route_request(self, task_type: str = "general", model_preference: str = "auto") -> str:
        """
        路由请求到最适合的模型
        
        Args:
            task_type: 任务类型
            model_preference: 模型偏好，auto表示自动选择
            
        Returns:
            选中的模型名称
            
        Raises:
            Exception: 没有可用的模型
        """
        
        # 1. 如果指定了具体模型，优先使用
        if model_preference != "auto" and model_preference in self.adapters:
            if await self._is_model_healthy(model_preference):
                logger.info(f"🎯 使用指定模型: {model_preference}")
                return model_preference
            else:
                logger.warning(f"⚠️ 指定模型不健康，将自动选择: {model_preference}")
        
        # 2. 根据任务类型选择主要候选模型
        task_config = TASK_MODEL_MAPPING.get(task_type, TASK_MODEL_MAPPING["general"])
        primary_candidates = task_config.get("primary", [])
        
        # 3. 检查主要候选模型的健康状态
        for model in primary_candidates:
            if model in self.adapters and await self._is_model_healthy(model):
                logger.info(f"🎯 选择主要模型: {model} (任务类型: {task_type})")
                return model
        
        # 4. 使用备用模型
        fallback_candidates = task_config.get("fallback", [])
        for model in fallback_candidates:
            if model in self.adapters and await self._is_model_healthy(model):
                logger.info(f"🎯 选择备用模型: {model} (任务类型: {task_type})")
                return model
        
        # 5. 最后使用任何可用的模型
        for model, adapter in self.adapters.items():
            if await self._is_model_healthy(model):
                logger.info(f"🎯 选择可用模型: {model} (任务类型: {task_type})")
                return model
        
        # 6. 没有可用模型
        available_models = list(self.adapters.keys())
        raise Exception(f"没有可用的模型。任务类型: {task_type}, 可用模型: {available_models}")

    async def select_stock_analysis_model(self, analysis_type: str = "general") -> str:
        """
        为股票分析选择最佳模型

        Args:
            analysis_type: 分析类型 (technical, fundamental, sentiment, general)
        """
        # 根据分析类型选择最佳模型
        if analysis_type == "technical":
            # 技术分析：需要数学计算和图表理解
            preferred_models = ["gpt-4", "deepseek-chat", "qwen-plus"]
        elif analysis_type == "fundamental":
            # 基本面分析：需要财务数据理解
            preferred_models = ["deepseek-chat", "qwen-plus", "gpt-4"]
        elif analysis_type == "sentiment":
            # 情感分析：需要文本理解
            preferred_models = ["qwen-plus", "deepseek-chat", "gemini-pro"]
        else:
            # 通用股票分析
            preferred_models = ["deepseek-chat", "qwen-plus", "gpt-4", "gemini-pro"]

        # 选择第一个可用的模型
        for model in preferred_models:
            if model in self.adapters and await self._is_model_healthy(model):
                logger.info(f"🏦 选择股票分析模型: {model} (分析类型: {analysis_type})")
                return model

        # 降级到通用选择
        return await self.select_model("financial_analysis")

    async def _is_model_healthy(self, model: str) -> bool:
        """检查模型健康状态"""
        try:
            adapter = self.adapters.get(model)
            if not adapter:
                return False
            
            # 检查缓存的健康状态
            if model in self.health_status:
                return self.health_status[model]
            
            # 执行健康检查
            is_healthy = await adapter.health_check()
            self.health_status[model] = is_healthy
            
            return is_healthy
            
        except Exception as e:
            logger.warning(f"⚠️ 模型健康检查失败 {model}: {e}")
            self.health_status[model] = False
            return False
    
    async def get_model_recommendations(self, task_type: str) -> List[str]:
        """获取任务类型的推荐模型列表"""
        task_config = TASK_MODEL_MAPPING.get(task_type, TASK_MODEL_MAPPING["general"])
        
        recommendations = []
        
        # 添加主要推荐模型
        for model in task_config.get("primary", []):
            if model in self.adapters:
                is_healthy = await self._is_model_healthy(model)
                recommendations.append({
                    "model": model,
                    "priority": "primary",
                    "healthy": is_healthy,
                    "provider": self.adapters[model].provider_name
                })
        
        # 添加备用推荐模型
        for model in task_config.get("fallback", []):
            if model in self.adapters:
                is_healthy = await self._is_model_healthy(model)
                recommendations.append({
                    "model": model,
                    "priority": "fallback",
                    "healthy": is_healthy,
                    "provider": self.adapters[model].provider_name
                })
        
        return recommendations
    
    async def refresh_health_status(self):
        """刷新所有模型的健康状态"""
        logger.info("🔄 刷新模型健康状态...")
        
        self.health_status.clear()
        
        for model in self.adapters:
            await self._is_model_healthy(model)
        
        healthy_count = sum(1 for status in self.health_status.values() if status)
        total_count = len(self.health_status)
        
        logger.info(f"✅ 健康状态刷新完成: {healthy_count}/{total_count} 模型健康")
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """获取路由统计信息"""
        return {
            "total_models": len(self.adapters),
            "healthy_models": sum(1 for status in self.health_status.values() if status),
            "health_status": self.health_status.copy(),
            "supported_tasks": list(TASK_MODEL_MAPPING.keys()),
            "model_providers": {
                model: adapter.provider_name 
                for model, adapter in self.adapters.items()
            }
        }
