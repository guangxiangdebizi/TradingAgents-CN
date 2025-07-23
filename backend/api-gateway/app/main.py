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
        logger.error(f"❌ 分析引擎请求失败: {e}")
        raise HTTPException(status_code=503, detail="分析引擎服务异常")
    except Exception as e:
        logger.error(f"❌ 启动分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动分析失败: {str(e)}")


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
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"未找到股票 {symbol} 的信息")
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

@app.post("/api/v1/chat/completions")
async def llm_chat_completions(request: Request):
    """LLM聊天完成接口"""
    try:
        if not llm_service_client:
            raise HTTPException(status_code=503, detail="LLM服务不可用")

        # 获取请求体并解析为JSON
        body = await request.body()

        # 转发请求到LLM服务
        response = await llm_service_client.post("/api/v1/chat/completions", data=body, headers={"Content-Type": "application/json"})
        return response

    except Exception as e:
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
