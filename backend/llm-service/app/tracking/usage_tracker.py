#!/usr/bin/env python3
"""
使用统计和成本跟踪器
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import redis.asyncio as redis

logger = logging.getLogger(__name__)

# 模型定价配置 (USD per 1K tokens)
MODEL_PRICING = {
    "deepseek-chat": {
        "input_cost_per_1k": 0.0014,
        "output_cost_per_1k": 0.0028
    },
    "deepseek-coder": {
        "input_cost_per_1k": 0.0014,
        "output_cost_per_1k": 0.0028
    },
    "gpt-4": {
        "input_cost_per_1k": 0.03,
        "output_cost_per_1k": 0.06
    },
    "gpt-3.5-turbo": {
        "input_cost_per_1k": 0.0015,
        "output_cost_per_1k": 0.002
    },
    "qwen-plus": {
        "input_cost_per_1k": 0.004,
        "output_cost_per_1k": 0.012
    }
}

class UsageTracker:
    """使用统计和成本跟踪器"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
    
    async def track_usage(self, user_id: str, model: str, task_type: str, 
                         usage: Dict[str, int], duration: float):
        """
        记录使用情况
        
        Args:
            user_id: 用户ID
            model: 模型名称
            task_type: 任务类型
            usage: 使用统计 {prompt_tokens, completion_tokens, total_tokens}
            duration: 请求耗时(秒)
        """
        try:
            timestamp = datetime.now()
            
            # 计算成本
            cost = self._calculate_cost(model, usage)
            
            # 构建使用记录
            usage_record = {
                "user_id": user_id,
                "model": model,
                "task_type": task_type,
                "timestamp": timestamp.isoformat(),
                "usage": usage,
                "cost": cost,
                "duration": duration
            }
            
            # 记录到Redis (如果可用)
            if self.redis:
                await self._save_to_redis(usage_record)
            
            # 记录到日志
            logger.info(f"📊 使用记录: {user_id} | {model} | {task_type} | "
                       f"tokens: {usage.get('total_tokens', 0)} | "
                       f"cost: ${cost:.6f} | duration: {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ 记录使用统计失败: {e}")
    
    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        """计算使用成本"""
        pricing = MODEL_PRICING.get(model, {})
        
        if not pricing:
            logger.warning(f"⚠️ 模型 {model} 没有定价信息")
            return 0.0
        
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        
        input_cost = input_tokens * pricing.get("input_cost_per_1k", 0) / 1000
        output_cost = output_tokens * pricing.get("output_cost_per_1k", 0) / 1000
        
        return input_cost + output_cost
    
    async def _save_to_redis(self, usage_record: Dict[str, Any]):
        """保存到Redis"""
        try:
            # 使用时间戳作为键的一部分，便于按时间查询
            timestamp = datetime.fromisoformat(usage_record["timestamp"])
            date_key = timestamp.strftime("%Y-%m-%d")
            hour_key = timestamp.strftime("%Y-%m-%d:%H")
            
            # 保存详细记录
            record_key = f"llm:usage:detail:{timestamp.isoformat()}"
            await self.redis.setex(record_key, 86400 * 7, json.dumps(usage_record))  # 保存7天
            
            # 更新日统计
            daily_key = f"llm:usage:daily:{date_key}"
            await self._update_aggregated_stats(daily_key, usage_record, 86400 * 30)  # 保存30天
            
            # 更新小时统计
            hourly_key = f"llm:usage:hourly:{hour_key}"
            await self._update_aggregated_stats(hourly_key, usage_record, 86400 * 7)  # 保存7天
            
            # 更新用户统计
            user_key = f"llm:usage:user:{usage_record['user_id']}:{date_key}"
            await self._update_aggregated_stats(user_key, usage_record, 86400 * 30)  # 保存30天
            
            # 更新模型统计
            model_key = f"llm:usage:model:{usage_record['model']}:{date_key}"
            await self._update_aggregated_stats(model_key, usage_record, 86400 * 30)  # 保存30天
            
        except Exception as e:
            logger.error(f"❌ 保存到Redis失败: {e}")
    
    async def _update_aggregated_stats(self, key: str, usage_record: Dict[str, Any], ttl: int):
        """更新聚合统计"""
        try:
            # 获取现有统计
            existing_data = await self.redis.get(key)
            if existing_data:
                stats = json.loads(existing_data)
            else:
                stats = {
                    "total_requests": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "total_duration": 0.0,
                    "models": {},
                    "task_types": {}
                }
            
            # 更新统计
            usage = usage_record["usage"]
            stats["total_requests"] += 1
            stats["total_tokens"] += usage.get("total_tokens", 0)
            stats["total_cost"] += usage_record["cost"]
            stats["total_duration"] += usage_record["duration"]
            
            # 更新模型统计
            model = usage_record["model"]
            if model not in stats["models"]:
                stats["models"][model] = {"requests": 0, "tokens": 0, "cost": 0.0}
            stats["models"][model]["requests"] += 1
            stats["models"][model]["tokens"] += usage.get("total_tokens", 0)
            stats["models"][model]["cost"] += usage_record["cost"]
            
            # 更新任务类型统计
            task_type = usage_record["task_type"]
            if task_type not in stats["task_types"]:
                stats["task_types"][task_type] = {"requests": 0, "tokens": 0, "cost": 0.0}
            stats["task_types"][task_type]["requests"] += 1
            stats["task_types"][task_type]["tokens"] += usage.get("total_tokens", 0)
            stats["task_types"][task_type]["cost"] += usage_record["cost"]
            
            # 保存更新后的统计
            await self.redis.setex(key, ttl, json.dumps(stats))
            
        except Exception as e:
            logger.error(f"❌ 更新聚合统计失败: {e}")
    
    async def get_usage_stats(self, user_id: Optional[str] = None, 
                             model: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """
        获取使用统计
        
        Args:
            user_id: 用户ID (可选)
            model: 模型名称 (可选)
            days: 统计天数
            
        Returns:
            统计数据
        """
        if not self.redis:
            return {"error": "Redis not available"}
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            stats = {
                "period": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "days": days
                },
                "total": {
                    "requests": 0,
                    "tokens": 0,
                    "cost": 0.0,
                    "duration": 0.0
                },
                "daily": [],
                "models": {},
                "task_types": {}
            }
            
            # 按天统计
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                
                # 构建查询键
                if user_id:
                    key = f"llm:usage:user:{user_id}:{date_str}"
                elif model:
                    key = f"llm:usage:model:{model}:{date_str}"
                else:
                    key = f"llm:usage:daily:{date_str}"
                
                # 获取当天统计
                daily_data = await self.redis.get(key)
                if daily_data:
                    daily_stats = json.loads(daily_data)
                    
                    # 累加总计
                    stats["total"]["requests"] += daily_stats.get("total_requests", 0)
                    stats["total"]["tokens"] += daily_stats.get("total_tokens", 0)
                    stats["total"]["cost"] += daily_stats.get("total_cost", 0.0)
                    stats["total"]["duration"] += daily_stats.get("total_duration", 0.0)
                    
                    # 添加每日数据
                    stats["daily"].append({
                        "date": date_str,
                        "requests": daily_stats.get("total_requests", 0),
                        "tokens": daily_stats.get("total_tokens", 0),
                        "cost": daily_stats.get("total_cost", 0.0),
                        "duration": daily_stats.get("total_duration", 0.0)
                    })
                    
                    # 合并模型统计
                    for model_name, model_stats in daily_stats.get("models", {}).items():
                        if model_name not in stats["models"]:
                            stats["models"][model_name] = {"requests": 0, "tokens": 0, "cost": 0.0}
                        stats["models"][model_name]["requests"] += model_stats.get("requests", 0)
                        stats["models"][model_name]["tokens"] += model_stats.get("tokens", 0)
                        stats["models"][model_name]["cost"] += model_stats.get("cost", 0.0)
                    
                    # 合并任务类型统计
                    for task_type, task_stats in daily_stats.get("task_types", {}).items():
                        if task_type not in stats["task_types"]:
                            stats["task_types"][task_type] = {"requests": 0, "tokens": 0, "cost": 0.0}
                        stats["task_types"][task_type]["requests"] += task_stats.get("requests", 0)
                        stats["task_types"][task_type]["tokens"] += task_stats.get("tokens", 0)
                        stats["task_types"][task_type]["cost"] += task_stats.get("cost", 0.0)
                
                current_date += timedelta(days=1)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ 获取使用统计失败: {e}")
            return {"error": str(e)}
