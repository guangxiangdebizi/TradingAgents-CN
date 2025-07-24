"""
API Gateway - API网关服务
统一入口，路由请求到各个微服务
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import httpx
from typing import Optional, Dict, Any
from datetime import datetime

# 导入共享模块
from backend.shared.models.analysis import (
    AnalysisRequest, APIResponse, HealthCheck, ExportRequest
)
from backend.shared.models.data import StockDataRequest
from backend.shared.utils.logger import get_service_logger
from backend.shared.utils.config import get_service_config
from backend.shared.clients.base import BaseServiceClient

# 全局变量
logger = get_service_logger("api-gateway")
analysis_engine_client: Optional[BaseServiceClient] = None
data_service_client: Optional[BaseServiceClient] = None
llm_service_client: Optional[BaseServiceClient] = None
agent_service_client: Optional[BaseServiceClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global analysis_engine_client, data_service_client, llm_service_client, agent_service_client
    
    # 启动时初始化
    logger.info("🚀 API Gateway 启动中...")
    
    # 初始化服务客户端
    try:
        analysis_engine_client = BaseServiceClient("analysis_engine")
        data_service_client = BaseServiceClient("data_service")
        llm_service_client = BaseServiceClient("llm_service")
        agent_service_client = BaseServiceClient("agent_service")

        # 检查服务健康状态
        if await analysis_engine_client.health_check():
            logger.info("✅ Analysis Engine 连接成功")
        else:
            logger.warning("⚠️ Analysis Engine 连接失败")

        if await data_service_client.health_check():
            logger.info("✅ Data Service 连接成功")
        else:
            logger.warning("⚠️ Data Service 连接失败")

        if await llm_service_client.health_check():
            logger.info("✅ LLM Service 连接成功")
        else:
            logger.warning("⚠️ LLM Service 连接失败")

        if await agent_service_client.health_check():
            logger.info("✅ Agent Service 连接成功")
        else:
            logger.warning("⚠️ Agent Service 连接失败")
            
    except Exception as e:
        logger.warning(f"⚠️ 服务客户端初始化失败: {e}")
    
    logger.info("✅ API Gateway 启动完成")
    
    yield
    
    # 关闭时清理
    logger.info("🛑 API Gateway 关闭中...")
    if analysis_engine_client:
        await analysis_engine_client.close()
    if data_service_client:
        await data_service_client.close()
    logger.info("✅ API Gateway 已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="TradingAgents API Gateway",
    description="TradingAgents 微服务API网关",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    import time
    start_time = time.time()

    # 记录请求
    logger.info(f"📥 {request.method} {request.url.path}")

    # 处理请求
    response = await call_next(request)

    # 记录响应
    process_time = time.time() - start_time
    logger.info(f"📤 {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")

    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"❌ 未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "error_code": "INTERNAL_ERROR"
        }
    )


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """健康检查"""
    dependencies = {}
    
    # 检查各个服务的健康状态
    if analysis_engine_client:
        if await analysis_engine_client.health_check():
            dependencies["analysis_engine"] = "healthy"
        else:
            dependencies["analysis_engine"] = "unhealthy"
    else:
        dependencies["analysis_engine"] = "not_configured"
    
    if data_service_client:
        if await data_service_client.health_check():
            dependencies["data_service"] = "healthy"
        else:
            dependencies["data_service"] = "unhealthy"
    else:
        dependencies["data_service"] = "not_configured"

    if llm_service_client:
        if await llm_service_client.health_check():
            dependencies["llm_service"] = "healthy"
        else:
            dependencies["llm_service"] = "unhealthy"
    else:
        dependencies["llm_service"] = "not_configured"

    if agent_service_client:
        if await agent_service_client.health_check():
            dependencies["agent_service"] = "healthy"
        else:
            dependencies["agent_service"] = "unhealthy"
    else:
        dependencies["agent_service"] = "not_configured"

    return HealthCheck(
        service_name="api-gateway",
        status="healthy",
        version="1.0.0",
        dependencies=dependencies
    )


# ==================== 分析相关接口 ====================

@app.post("/api/analysis/start", response_model=APIResponse)
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """开始股票分析"""
    try:
        if not analysis_engine_client:
            raise HTTPException(status_code=503, detail="分析引擎服务不可用")

        logger.info(f"🚀 转发分析请求: {request.stock_code}")

        # 转发到分析引擎
        response = await analysis_engine_client.post(
            "/api/analysis/start",
            data=request.model_dump(mode='json')  # 使用json模式确保datetime序列化
        )

        return APIResponse(**response)

    except httpx.HTTPError as e:
        # 判断是否为连接错误或超时错误
        if isinstance(e, (httpx.ConnectError, httpx.TimeoutException)):
            logger.critical(f"🚨 严重告警: Agent Service不可达 - 无法启动分析")
            logger.critical(f"🚨 请检查Agent Service是否启动并可访问")
            logger.critical(f"🚨 错误详情: {type(e).__name__}: {str(e)}")
        else:
            logger.error(f"❌ 分析引擎请求失败: {e}")
        raise HTTPException(status_code=503, detail="分析引擎服务异常")
    except Exception as e:
        logger.error(f"❌ 启动分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动分析失败: {str(e)}")


@app.post("/api/v1/analysis/comprehensive", response_model=APIResponse)
async def start_comprehensive_analysis(request: Request):
    """启动综合分析 - CLI专用接口"""
    try:
        if not analysis_engine_client:
            raise HTTPException(status_code=503, detail="分析引擎服务不可用")

        # 获取请求体
        body = await request.json()
        symbol = body.get("symbol")
        config = body.get("config", {})

        logger.info(f"🚀 启动综合分析: {symbol}")
        logger.info(f"📋 分析配置: {config}")
        logger.info(f"📥 CLI原始请求体: {body}")

        # 构造分析请求 - 转换为分析引擎期望的格式
        selected_analysts = config.get("selected_analysts", ["market_analyst", "fundamentals_analyst"])

        # 转换市场类型 - 使用分析引擎期望的中文值
        market_type_map = {
            "CN": "A股",
            "US": "美股",
            "HK": "港股"
        }
        market_type = market_type_map.get(config.get("market", "CN"), "A股")

        # 转换LLM提供商 - 使用分析引擎期望的小写值
        llm_provider_map = {
            "dashscope": "dashscope",
            "deepseek": "deepseek",
            "openai": "openai",
            "google": "gemini",
            "anthropic": "anthropic"
        }
        llm_provider = llm_provider_map.get(config.get("llm_provider", "dashscope"), "dashscope")

        # 转换分析日期为datetime格式
        analysis_date = config.get("analysis_date")
        if analysis_date and isinstance(analysis_date, str):
            from datetime import datetime
            try:
                analysis_date = datetime.fromisoformat(analysis_date + "T00:00:00")
            except:
                analysis_date = datetime.now()
        else:
            analysis_date = datetime.now()

        analysis_request = {
            "stock_code": symbol,
            "market_type": market_type,
            "analysis_date": analysis_date.isoformat(),
            "research_depth": config.get("max_debate_rounds", 3),

            # 分析师选择
            "market_analyst": "market_analyst" in selected_analysts,
            "social_analyst": "social_analyst" in selected_analysts,
            "news_analyst": "news_analyst" in selected_analysts,
            "fundamental_analyst": "fundamentals_analyst" in selected_analysts,

            # LLM配置
            "llm_provider": llm_provider,
            "model_version": config.get("llm_model", "qwen-plus-latest"),
            "enable_memory": True,
            "debug_mode": False,
            "max_output_length": 4000,

            # 高级选项
            "include_sentiment": True,
            "include_risk_assessment": True,
            "custom_prompt": None
        }

        # 转发到分析引擎
        logger.info(f"📤 发送到分析引擎的请求: {analysis_request}")
        response = await analysis_engine_client.post(
            "/api/analysis/start",
            data=analysis_request
        )
        logger.info(f"📥 分析引擎响应: {response}")

        return APIResponse(**response)

    except httpx.HTTPError as e:
        logger.error(f"❌ 分析引擎请求失败: {e}")
        raise HTTPException(status_code=503, detail="分析引擎服务异常")
    except Exception as e:
        logger.error(f"❌ 启动综合分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动综合分析失败: {str(e)}")


@app.get("/api/analysis/{analysis_id}/progress", response_model=APIResponse)
async def get_analysis_progress(analysis_id: str):
    """获取分析进度"""
    try:
        if not analysis_engine_client:
            raise HTTPException(status_code=503, detail="分析引擎服务不可用")

        # 转发到分析引擎
        response = await analysis_engine_client.get(f"/api/analysis/{analysis_id}/progress")

        return APIResponse(**response)

    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="分析任务不存在")
        logger.error(f"❌ 分析引擎请求失败: {e}")
        raise HTTPException(status_code=503, detail="分析引擎服务异常")
    except Exception as e:
        logger.error(f"❌ 获取分析进度失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分析进度失败: {str(e)}")


@app.get("/api/v1/analysis/status/{analysis_id}", response_model=APIResponse)
async def get_analysis_status(analysis_id: str):
    """获取分析状态 - CLI专用接口"""
    try:
        if not analysis_engine_client:
            raise HTTPException(status_code=503, detail="分析引擎服务不可用")

        # 转发到分析引擎
        response = await analysis_engine_client.get(f"/api/analysis/{analysis_id}/progress")

        return APIResponse(**response)

    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="分析任务不存在")
        logger.error(f"❌ 分析引擎请求失败: {e}")
        raise HTTPException(status_code=503, detail="分析引擎服务异常")
    except Exception as e:
        logger.error(f"❌ 获取分析状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分析状态失败: {str(e)}")


@app.get("/api/analysis/{analysis_id}/result", response_model=APIResponse)
async def get_analysis_result(analysis_id: str):
    """获取分析结果"""
    try:
        if not analysis_engine_client:
            raise HTTPException(status_code=503, detail="分析引擎服务不可用")

        # 转发到分析引擎
        response = await analysis_engine_client.get(f"/api/analysis/{analysis_id}/result")

        return APIResponse(**response)

    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="分析结果不存在")
        logger.error(f"❌ 分析引擎请求失败: {e}")
        raise HTTPException(status_code=503, detail="分析引擎服务异常")
    except Exception as e:
        logger.error(f"❌ 获取分析结果失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分析结果失败: {str(e)}")


@app.get("/api/v1/analysis/result/{analysis_id}", response_model=APIResponse)
async def get_analysis_result_v1(analysis_id: str):
    """获取分析结果 - CLI专用接口"""
    try:
        if not analysis_engine_client:
            raise HTTPException(status_code=503, detail="分析引擎服务不可用")

        # 转发到分析引擎
        response = await analysis_engine_client.get(f"/api/analysis/{analysis_id}/result")

        return APIResponse(**response)

    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="分析结果不存在")
        logger.error(f"❌ 分析引擎请求失败: {e}")
        raise HTTPException(status_code=503, detail="分析引擎服务异常")
    except Exception as e:
        logger.error(f"❌ 获取分析结果失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分析结果失败: {str(e)}")


@app.delete("/api/analysis/{analysis_id}", response_model=APIResponse)
async def cancel_analysis(analysis_id: str):
    """取消分析任务"""
    try:
        if not analysis_engine_client:
            raise HTTPException(status_code=503, detail="分析引擎服务不可用")
        
        # 转发到分析引擎
        response = await analysis_engine_client.delete(f"/api/analysis/{analysis_id}")
        
        return APIResponse(**response)
        
    except httpx.HTTPError as e:
        logger.error(f"❌ 分析引擎请求失败: {e}")
        raise HTTPException(status_code=503, detail="分析引擎服务异常")
    except Exception as e:
        logger.error(f"❌ 取消分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"取消分析失败: {str(e)}")


# ==================== 数据相关接口 ====================

@app.get("/api/stock/info/{symbol}", response_model=APIResponse)
async def get_stock_info(symbol: str, force_refresh: bool = False):
    """获取股票基本信息"""
    try:
        if not data_service_client:
            raise HTTPException(status_code=503, detail="数据服务不可用")

        # 构建查询参数
        params = {}
        if force_refresh:
            params["force_refresh"] = force_refresh

        # 转发到数据服务
        response = await data_service_client.get(f"/api/stock/info/{symbol}", params=params)

        return APIResponse(**response)
        
    except httpx.HTTPError as e:
        if hasattr(e, 'response') and e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"未找到股票 {symbol} 的信息")
        # 判断是否为连接错误或超时错误
        if isinstance(e, (httpx.ConnectError, httpx.TimeoutException)):
            logger.critical(f"🚨 严重告警: Data Service不可达 - 无法获取股票信息")
            logger.critical(f"🚨 请检查Data Service是否启动并可访问")
            logger.critical(f"🚨 错误详情: {type(e).__name__}: {str(e)}")
        else:
            logger.error(f"❌ 数据服务请求失败: {e}")
        raise HTTPException(status_code=503, detail="数据服务异常")
    except Exception as e:
        logger.error(f"❌ 获取股票信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取股票信息失败: {str(e)}")


@app.post("/api/stock/data", response_model=APIResponse)
async def get_stock_data(request: StockDataRequest):
    """获取股票历史数据"""
    try:
        if not data_service_client:
            raise HTTPException(status_code=503, detail="数据服务不可用")
        
        # 转发到数据服务
        response = await data_service_client.post(
            "/api/stock/data",
            data=request.model_dump(mode='json')  # 使用json模式确保兼容性
        )
        
        return APIResponse(**response)
        
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"未找到股票 {request.symbol} 的数据")
        logger.error(f"❌ 数据服务请求失败: {e}")
        raise HTTPException(status_code=503, detail="数据服务异常")
    except Exception as e:
        logger.error(f"❌ 获取股票数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取股票数据失败: {str(e)}")


@app.get("/api/stock/fundamentals/{symbol}", response_model=APIResponse)
async def get_stock_fundamentals(
    symbol: str,
    start_date: str,
    end_date: str,
    curr_date: str,
    force_refresh: bool = False
):
    """获取股票基本面数据"""
    try:
        if not data_service_client:
            raise HTTPException(status_code=503, detail="数据服务不可用")

        # 构建查询参数
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "curr_date": curr_date
        }
        if force_refresh:
            params["force_refresh"] = force_refresh

        # 转发到数据服务
        response = await data_service_client.get(
            f"/api/stock/fundamentals/{symbol}",
            params=params
        )
        
        return APIResponse(**response)
        
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"未找到股票 {symbol} 的基本面数据")
        logger.error(f"❌ 数据服务请求失败: {e}")
        raise HTTPException(status_code=503, detail="数据服务异常")
    except Exception as e:
        logger.error(f"❌ 获取基本面数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取基本面数据失败: {str(e)}")


@app.get("/api/stock/news/{symbol}", response_model=APIResponse)
async def get_stock_news(
    symbol: str,
    limit: int = 10,
    days: int = 7,
    force_refresh: bool = False
):
    """获取股票新闻"""
    try:
        if not data_service_client:
            raise HTTPException(status_code=503, detail="数据服务不可用")

        # 构建查询参数
        params = {
            "limit": limit,
            "days": days
        }
        if force_refresh:
            params["force_refresh"] = force_refresh

        # 转发到数据服务
        response = await data_service_client.get(f"/api/stock/news/{symbol}", params=params)

        return APIResponse(**response)
        
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"未找到股票 {symbol} 的新闻")
        logger.error(f"❌ 数据服务请求失败: {e}")
        raise HTTPException(status_code=503, detail="数据服务异常")
    except Exception as e:
        logger.error(f"❌ 获取股票新闻失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取股票新闻失败: {str(e)}")


# ==================== 配置和状态接口 ====================

@app.get("/api/config/models", response_model=APIResponse)
async def get_model_config():
    """获取模型配置"""
    try:
        # 返回可用的模型配置
        models_config = {
            "llm_providers": [
                {"value": "dashscope", "label": "阿里百炼", "models": ["qwen-turbo", "qwen-plus-latest", "qwen-max"]},
                {"value": "deepseek", "label": "DeepSeek", "models": ["deepseek-chat", "deepseek-coder"]},
                {"value": "openai", "label": "OpenAI", "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]},
                {"value": "gemini", "label": "Google Gemini", "models": ["gemini-pro", "gemini-pro-vision"]},
            ],
            "market_types": [
                {"value": "A股", "label": "A股"},
                {"value": "美股", "label": "美股"},
                {"value": "港股", "label": "港股"},
            ]
        }
        
        return APIResponse(
            success=True,
            message="获取模型配置成功",
            data=models_config
        )
        
    except Exception as e:
        logger.error(f"❌ 获取模型配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取模型配置失败: {str(e)}")


@app.get("/api/config/status", response_model=APIResponse)
async def get_system_status():
    """获取系统状态"""
    try:
        # 检查各服务状态
        status = {
            "api_gateway": "healthy",
            "analysis_engine": "unknown",
            "data_service": "unknown",
        }
        
        if analysis_engine_client:
            if await analysis_engine_client.health_check():
                status["analysis_engine"] = "healthy"
            else:
                status["analysis_engine"] = "unhealthy"
        
        if data_service_client:
            if await data_service_client.health_check():
                status["data_service"] = "healthy"
            else:
                status["data_service"] = "unhealthy"
        
        return APIResponse(
            success=True,
            message="获取系统状态成功",
            data=status
        )
        
    except Exception as e:
        logger.error(f"❌ 获取系统状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统状态失败: {str(e)}")


# ==================== LLM服务路由 ====================

@app.get("/api/v1/llm/providers", response_model=APIResponse)
async def get_llm_providers():
    """获取LLM提供商列表"""
    try:
        # 返回支持的LLM提供商
        providers = [
            {
                "id": "dashscope",
                "name": "阿里百炼 | Alibaba DashScope",
                "description": "阿里云通义千问系列模型",
                "status": "available"
            },
            {
                "id": "deepseek",
                "name": "DeepSeek",
                "description": "DeepSeek系列模型",
                "status": "available"
            },
            {
                "id": "openai",
                "name": "OpenAI",
                "description": "GPT系列模型",
                "status": "available"
            },
            {
                "id": "anthropic",
                "name": "Anthropic",
                "description": "Claude系列模型",
                "status": "available"
            },
            {
                "id": "google",
                "name": "Google",
                "description": "Gemini系列模型",
                "status": "available"
            }
        ]

        return APIResponse(
            success=True,
            message="获取LLM提供商成功",
            data=providers
        )

    except Exception as e:
        logger.error(f"❌ 获取LLM提供商失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取LLM提供商失败: {str(e)}")


@app.get("/api/v1/llm/providers/{provider_id}/models", response_model=APIResponse)
async def get_llm_models(provider_id: str):
    """获取指定提供商的模型列表"""
    try:
        # 定义各提供商的模型列表
        models_map = {
            "dashscope": [
                {
                    "id": "qwen-plus-latest",
                    "name": "通义千问Plus (最新版)",
                    "description": "高性能通用模型，适合复杂分析任务",
                    "context_length": 32768,
                    "pricing": {"input": 0.004, "output": 0.012}
                },
                {
                    "id": "qwen-turbo-latest",
                    "name": "通义千问Turbo (最新版)",
                    "description": "快速响应模型，适合实时分析",
                    "context_length": 8192,
                    "pricing": {"input": 0.002, "output": 0.006}
                },
                {
                    "id": "qwen-max-latest",
                    "name": "通义千问Max (最新版)",
                    "description": "最强性能模型，适合深度分析",
                    "context_length": 32768,
                    "pricing": {"input": 0.02, "output": 0.06}
                }
            ],
            "deepseek": [
                {
                    "id": "deepseek-chat",
                    "name": "DeepSeek Chat",
                    "description": "对话优化模型，适合交互式分析",
                    "context_length": 32768,
                    "pricing": {"input": 0.0014, "output": 0.0028}
                },
                {
                    "id": "deepseek-coder",
                    "name": "DeepSeek Coder",
                    "description": "代码优化模型，适合技术分析",
                    "context_length": 16384,
                    "pricing": {"input": 0.0014, "output": 0.0028}
                }
            ],
            "openai": [
                {
                    "id": "gpt-4o",
                    "name": "GPT-4o",
                    "description": "最新多模态模型，支持文本和图像",
                    "context_length": 128000,
                    "pricing": {"input": 0.005, "output": 0.015}
                },
                {
                    "id": "gpt-4-turbo",
                    "name": "GPT-4 Turbo",
                    "description": "高性能模型，适合复杂推理",
                    "context_length": 128000,
                    "pricing": {"input": 0.01, "output": 0.03}
                },
                {
                    "id": "gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "description": "经济实用模型，适合基础分析",
                    "context_length": 16385,
                    "pricing": {"input": 0.0015, "output": 0.002}
                }
            ],
            "anthropic": [
                {
                    "id": "claude-3-5-sonnet",
                    "name": "Claude 3.5 Sonnet",
                    "description": "最新版本，平衡性能和速度",
                    "context_length": 200000,
                    "pricing": {"input": 0.003, "output": 0.015}
                },
                {
                    "id": "claude-3-opus",
                    "name": "Claude 3 Opus",
                    "description": "最强性能，适合复杂分析",
                    "context_length": 200000,
                    "pricing": {"input": 0.015, "output": 0.075}
                },
                {
                    "id": "claude-3-haiku",
                    "name": "Claude 3 Haiku",
                    "description": "快速响应，适合简单任务",
                    "context_length": 200000,
                    "pricing": {"input": 0.00025, "output": 0.00125}
                }
            ],
            "google": [
                {
                    "id": "gemini-1.5-pro",
                    "name": "Gemini 1.5 Pro",
                    "description": "高性能模型，支持长上下文",
                    "context_length": 1000000,
                    "pricing": {"input": 0.0035, "output": 0.0105}
                },
                {
                    "id": "gemini-1.5-flash",
                    "name": "Gemini 1.5 Flash",
                    "description": "快速模型，适合实时分析",
                    "context_length": 1000000,
                    "pricing": {"input": 0.00035, "output": 0.00105}
                }
            ]
        }

        if provider_id not in models_map:
            raise HTTPException(status_code=404, detail=f"未找到提供商: {provider_id}")

        models = models_map[provider_id]

        return APIResponse(
            success=True,
            message=f"获取{provider_id}模型列表成功",
            data=models
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取模型列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")


@app.post("/api/v1/chat/completions")
async def llm_chat_completions(request: Request):
    """LLM聊天完成接口"""
    try:
        if not llm_service_client:
            raise HTTPException(status_code=503, detail="LLM服务不可用")

        # 获取请求体并解析为JSON
        body = await request.body()

        # 转发请求到LLM服务
        response = await llm_service_client.post("/api/v1/chat/completions", raw_data=body, headers={"Content-Type": "application/json"})
        return response

    except Exception as e:
        # 判断是否为连接错误或超时错误
        if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
            logger.critical(f"🚨 严重告警: LLM Service不可达 - 无法处理对话请求")
            logger.critical(f"🚨 请检查LLM Service是否启动并可访问")
            logger.critical(f"🚨 错误详情: {type(e).__name__}: {str(e)}")
        else:
            logger.error(f"❌ LLM服务请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"LLM服务请求失败: {str(e)}")


# ==================== 市场数据路由 ====================

@app.get("/api/v1/market/data")
async def market_data(market: str, data_type: str = "US"):
    """获取市场数据"""
    try:
        if not data_service_client:
            raise HTTPException(status_code=503, detail="数据服务不可用")

        # 转发请求到数据服务，增加超时时间
        response = await data_service_client.get(f"/api/v1/market/data?market={market}&data_type={data_type}", timeout=60)
        return response

    except Exception as e:
        logger.error(f"❌ 市场数据请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"市场数据请求失败: {str(e)}")


@app.get("/api/v1/company/info")
async def company_info(symbol: str, market: str = "US"):
    """获取公司信息"""
    try:
        if not data_service_client:
            raise HTTPException(status_code=503, detail="数据服务不可用")

        response = await data_service_client.get(f"/api/v1/company/info?symbol={symbol}&market={market}", timeout=60)
        return response

    except Exception as e:
        logger.error(f"❌ 公司信息请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"公司信息请求失败: {str(e)}")


@app.get("/api/v1/financial/income")
async def financial_income(symbol: str, market: str = "US", period: str = "annual"):
    """获取损益表数据"""
    try:
        if not data_service_client:
            raise HTTPException(status_code=503, detail="数据服务不可用")

        response = await data_service_client.get(f"/api/v1/financial/income?symbol={symbol}&market={market}&period={period}", timeout=60)
        return response

    except Exception as e:
        logger.error(f"❌ 损益表请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"损益表请求失败: {str(e)}")


@app.get("/api/v1/market/history")
async def market_history(symbol: str, period: str = "1y", interval: str = "1d"):
    """获取价格历史数据"""
    try:
        if not data_service_client:
            raise HTTPException(status_code=503, detail="数据服务不可用")

        response = await data_service_client.get(f"/api/v1/market/history?symbol={symbol}&period={period}&interval={interval}", timeout=60)
        return response

    except Exception as e:
        logger.error(f"❌ 价格历史请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"价格历史请求失败: {str(e)}")


# ==================== Agent服务路由 ====================

@app.get("/api/v1/agents")
async def get_agents():
    """获取智能体列表"""
    try:
        if not agent_service_client:
            raise HTTPException(status_code=503, detail="Agent服务不可用")

        response = await agent_service_client.get("/api/v1/agents")
        return response

    except Exception as e:
        logger.error(f"❌ Agent服务请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"Agent服务请求失败: {str(e)}")


@app.get("/api/v1/tasks")
async def get_tasks():
    """获取任务列表"""
    try:
        if not agent_service_client:
            raise HTTPException(status_code=503, detail="Agent服务不可用")

        response = await agent_service_client.get("/api/v1/tasks")
        return response

    except Exception as e:
        logger.error(f"❌ Agent服务请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"Agent服务请求失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    import sys
    from pathlib import Path

    # 添加shared路径
    shared_path = Path(__file__).parent.parent.parent / "shared"
    sys.path.insert(0, str(shared_path))

    from utils.config import get_config

    config = get_config()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=config.get('API_GATEWAY_PORT', 8000),
        reload=config.get('DEBUG', False),
        log_level=config.get('LOG_LEVEL', 'INFO').lower()
    )
