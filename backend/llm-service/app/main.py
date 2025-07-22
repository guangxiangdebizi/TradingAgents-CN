#!/usr/bin/env python3
"""
LLM Service - 大模型统一调用服务
提供标准化的大模型API接口
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis.asyncio as redis

# 导入适配器和路由器
from .adapters.factory import get_adapter_factory
from .routing.model_router import ModelRouter
from .tracking.usage_tracker import UsageTracker
from .prompts.prompt_manager import get_prompt_manager
from .models.requests import ChatCompletionRequest, ModelListRequest
from .models.responses import ChatCompletionResponse, ModelListResponse, UsageStatsResponse
from .config.settings import LLM_SERVICE_CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="LLM Service",
    description="大模型统一调用服务",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
redis_client: Optional[redis.Redis] = None
adapter_factory = None
model_router = None
usage_tracker = None
prompt_manager = None

@app.on_event("startup")
async def startup_event():
    """启动事件"""
    global redis_client, adapter_factory, model_router, usage_tracker, prompt_manager

    logger.info("🚀 启动LLM Service...")

    # 初始化Redis连接
    try:
        redis_client = redis.Redis(
            host=LLM_SERVICE_CONFIG.get("redis_host", "localhost"),
            port=LLM_SERVICE_CONFIG.get("redis_port", 6379),
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("✅ Redis连接成功")
    except Exception as e:
        logger.warning(f"⚠️ Redis连接失败: {e}")
        redis_client = None

    # 初始化提示词管理器
    prompt_manager = await get_prompt_manager()
    logger.info("✅ 提示词管理器初始化完成")

    # 初始化适配器工厂
    adapter_factory = get_adapter_factory()
    logger.info("✅ 适配器工厂初始化完成")

    # 初始化模型路由器
    adapters = await adapter_factory.get_all_adapters()
    model_router = ModelRouter(adapters)
    logger.info(f"✅ 模型路由器初始化完成，支持{len(adapters)}个模型")

    # 初始化使用统计器
    usage_tracker = UsageTracker(redis_client=redis_client)
    logger.info("✅ 使用统计器初始化完成")

    logger.info("🎉 LLM Service启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    global redis_client
    
    logger.info("🛑 关闭LLM Service...")
    
    if redis_client:
        await redis_client.close()
        logger.info("✅ Redis连接已关闭")
    
    logger.info("👋 LLM Service已关闭")

# 依赖注入
async def get_redis() -> Optional[redis.Redis]:
    """获取Redis客户端"""
    return redis_client

async def get_model_router() -> ModelRouter:
    """获取模型路由器"""
    if not model_router:
        raise HTTPException(status_code=503, detail="模型路由器未初始化")
    return model_router

async def get_usage_tracker() -> UsageTracker:
    """获取使用统计器"""
    if not usage_tracker:
        raise HTTPException(status_code=503, detail="使用统计器未初始化")
    return usage_tracker

async def get_prompt_manager():
    """获取提示词管理器"""
    if not prompt_manager:
        raise HTTPException(status_code=503, detail="提示词管理器未初始化")
    return prompt_manager

# ===== API接口 =====

@app.get("/health")
async def health_check():
    """健康检查"""
    dependencies = {}
    
    # 检查Redis
    if redis_client:
        try:
            await redis_client.ping()
            dependencies["redis"] = "connected"
        except Exception:
            dependencies["redis"] = "disconnected"
    else:
        dependencies["redis"] = "not_configured"
    
    # 检查模型适配器
    if model_router:
        healthy_models = []
        for model_name, adapter in model_router.adapters.items():
            try:
                if await adapter.health_check():
                    healthy_models.append(model_name)
            except Exception:
                pass
        dependencies["models"] = f"{len(healthy_models)} healthy"
    else:
        dependencies["models"] = "not_initialized"
    
    return {
        "status": "healthy",
        "service": "llm-service",
        "timestamp": datetime.now().isoformat(),
        "dependencies": dependencies
    }

@app.post("/api/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest,
    background_tasks: BackgroundTasks,
    router: ModelRouter = Depends(get_model_router),
    tracker: UsageTracker = Depends(get_usage_tracker),
    prompt_mgr = Depends(get_prompt_manager)
):
    """聊天完成接口"""
    try:
        start_time = datetime.now()
        
        # 1. 路由到最适合的模型
        selected_model = await router.route_request(
            task_type=request.task_type,
            model_preference=request.model
        )
        
        logger.info(f"🎯 路由到模型: {selected_model} (任务类型: {request.task_type})")
        
        # 2. 获取适配器
        adapter = router.adapters[selected_model]

        # 3. 处理提示词（如果需要）
        messages_to_send = request.messages

        # 如果消息只有一条用户消息，尝试使用提示词模板
        if (len(request.messages) == 1 and
            request.messages[0].get("role") == "user" and
            hasattr(request, 'use_prompt_template') and
            getattr(request, 'use_prompt_template', True)):

            try:
                # 提取用户输入
                user_input = request.messages[0].get("content", "")

                # 使用提示词管理器格式化消息
                formatted_messages = prompt_mgr.format_messages(
                    model=selected_model,
                    task_type=request.task_type,
                    variables={"user_input": user_input},
                    language="zh"
                )

                if formatted_messages:
                    messages_to_send = formatted_messages
                    logger.info(f"🎯 使用提示词模板: {selected_model} - {request.task_type}")

            except Exception as e:
                logger.warning(f"⚠️ 提示词处理失败，使用原始消息: {e}")

        # 4. 调用模型
        result = await adapter.chat_completion(
            messages=messages_to_send,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=request.stream
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=f"模型调用失败: {result.get('error')}")
        
        # 4. 构建响应
        response = ChatCompletionResponse(
            id=f"chatcmpl-{int(datetime.now().timestamp())}",
            object="chat.completion",
            created=int(start_time.timestamp()),
            model=selected_model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result["content"]
                },
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": result.get("usage", {}).get("prompt_tokens", 0),
                "completion_tokens": result.get("usage", {}).get("completion_tokens", 0),
                "total_tokens": result.get("usage", {}).get("total_tokens", 0)
            }
        )
        
        # 5. 后台记录使用统计
        background_tasks.add_task(
            tracker.track_usage,
            user_id=request.user_id or "anonymous",
            model=selected_model,
            task_type=request.task_type,
            usage=response.usage,
            duration=(datetime.now() - start_time).total_seconds()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 聊天完成失败: {e}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")

@app.get("/api/v1/models", response_model=ModelListResponse)
async def list_models(
    router: ModelRouter = Depends(get_model_router)
):
    """获取可用模型列表"""
    try:
        models = []
        
        for model_name, adapter in router.adapters.items():
            try:
                model_info = adapter.get_model_info()
                is_healthy = await adapter.health_check()
                
                models.append({
                    "id": model_name,
                    "object": "model",
                    "provider": model_info.get("provider", "unknown"),
                    "max_tokens": model_info.get("max_tokens", 4096),
                    "supports_streaming": model_info.get("supports_streaming", False),
                    "cost_per_1k_tokens": model_info.get("cost_per_1k_tokens", {}),
                    "strengths": model_info.get("strengths", []),
                    "best_for": model_info.get("best_for", []),
                    "status": "healthy" if is_healthy else "unhealthy"
                })
            except Exception as e:
                logger.warning(f"⚠️ 获取模型信息失败 {model_name}: {e}")
        
        return ModelListResponse(
            object="list",
            data=models
        )
        
    except Exception as e:
        logger.error(f"❌ 获取模型列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")

@app.get("/api/v1/usage/stats", response_model=UsageStatsResponse)
async def get_usage_stats(
    user_id: Optional[str] = None,
    model: Optional[str] = None,
    days: int = 7,
    tracker: UsageTracker = Depends(get_usage_tracker)
):
    """获取使用统计"""
    try:
        stats = await tracker.get_usage_stats(
            user_id=user_id,
            model=model,
            days=days
        )
        
        return UsageStatsResponse(
            success=True,
            data=stats
        )
        
    except Exception as e:
        logger.error(f"❌ 获取使用统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取使用统计失败: {str(e)}")

@app.get("/api/v1/prompts/templates")
async def list_prompt_templates(
    model_type: Optional[str] = None,
    task_type: Optional[str] = None,
    language: Optional[str] = None,
    prompt_mgr = Depends(get_prompt_manager)
):
    """获取提示词模板列表"""
    try:
        templates = prompt_mgr.list_templates(
            model_type=model_type,
            task_type=task_type,
            language=language
        )

        return {
            "success": True,
            "data": [template.to_dict() for template in templates],
            "total": len(templates)
        }

    except Exception as e:
        logger.error(f"❌ 获取提示词模板失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取提示词模板失败: {str(e)}")

@app.get("/api/v1/prompts/stats")
async def get_prompt_stats(prompt_mgr = Depends(get_prompt_manager)):
    """获取提示词统计信息"""
    try:
        stats = prompt_mgr.get_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"❌ 获取提示词统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取提示词统计失败: {str(e)}")

@app.post("/api/v1/admin/reload-models")
async def reload_models():
    """重新加载模型适配器"""
    global model_router

    try:
        # 重新初始化适配器
        adapters = await adapter_factory.get_all_adapters()
        model_router = ModelRouter(adapters)

        logger.info(f"✅ 模型重新加载完成，支持{len(adapters)}个模型")

        return {
            "success": True,
            "message": f"成功重新加载{len(adapters)}个模型",
            "models": list(adapters.keys())
        }

    except Exception as e:
        logger.error(f"❌ 重新加载模型失败: {e}")
        raise HTTPException(status_code=500, detail=f"重新加载模型失败: {str(e)}")

@app.post("/api/v1/admin/reload-prompts")
async def reload_prompts(prompt_mgr = Depends(get_prompt_manager)):
    """重新加载提示词模板"""
    try:
        await prompt_mgr.reload_templates()
        stats = prompt_mgr.get_stats()

        logger.info(f"✅ 提示词重新加载完成，共{stats['total_templates']}个模板")

        return {
            "success": True,
            "message": f"成功重新加载{stats['total_templates']}个提示词模板",
            "stats": stats
        }

    except Exception as e:
        logger.error(f"❌ 重新加载提示词失败: {e}")
        raise HTTPException(status_code=500, detail=f"重新加载提示词失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
