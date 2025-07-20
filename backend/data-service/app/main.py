"""
Data Service - 数据服务
提供股票数据获取和缓存功能
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis
from typing import Optional, List

# 导入共享模块
from backend.shared.models.data import (
    StockDataRequest, StockInfo, StockPrice, MarketData, 
    NewsItem, FundamentalData, DataSourceStatus
)
from backend.shared.models.analysis import APIResponse, HealthCheck
from backend.shared.utils.logger import get_service_logger
from backend.shared.utils.config import get_service_config

# 导入现有的数据获取逻辑
from tradingagents.dataflows.interface import (
    get_china_stock_data_unified,
    get_china_stock_info_unified,
    get_china_stock_fundamentals_tushare,
    get_finnhub_news,
    get_hk_stock_data_unified,
    get_hk_stock_info_unified,
    get_stock_data_by_market
)

# 导入数据库访问层
from backend.shared.database.mongodb import get_db_manager, get_stock_repository

# 全局变量
logger = get_service_logger("data-service")
redis_client: Optional[redis.Redis] = None
db_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global redis_client, db_manager

    # 启动时初始化
    logger.info("🚀 Data Service 启动中...")

    # 初始化Redis连接
    config = get_service_config("data_service")
    try:
        redis_client = redis.from_url(config['redis_url'])
        await redis_client.ping()
        logger.info("✅ Redis 连接成功")
    except Exception as e:
        logger.warning(f"⚠️ Redis 连接失败: {e}")
        redis_client = None

    # 初始化MongoDB连接
    try:
        db_manager = await get_db_manager()
        if db_manager.is_connected():
            logger.info("✅ MongoDB 连接成功")
        else:
            logger.warning("⚠️ MongoDB 连接失败")
    except Exception as e:
        logger.warning(f"⚠️ MongoDB 初始化失败: {e}")
        db_manager = None

    logger.info("✅ Data Service 启动完成")

    yield

    # 关闭时清理
    logger.info("🛑 Data Service 关闭中...")
    if redis_client:
        await redis_client.close()
    if db_manager:
        await db_manager.disconnect()
    logger.info("✅ Data Service 已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="TradingAgents Data Service",
    description="股票数据获取和缓存服务",
    version="1.0.0",
    lifespan=lifespan
)

# 设置默认响应类，确保中文编码正确
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import json

class UTF8JSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            jsonable_encoder(content),
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")

app.default_response_class = UTF8JSONResponse

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_redis() -> Optional[redis.Redis]:
    """获取Redis客户端"""
    return redis_client


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """健康检查"""
    dependencies = {}
    
    # 检查Redis连接
    if redis_client:
        try:
            await redis_client.ping()
            dependencies["redis"] = "healthy"
        except Exception:
            dependencies["redis"] = "unhealthy"
    else:
        dependencies["redis"] = "not_configured"
    
    return HealthCheck(
        service_name="data-service",
        status="healthy",
        version="1.0.0",
        dependencies=dependencies
    )


@app.get("/api/stock/info/{symbol}", response_model=APIResponse)
async def get_stock_info(
    symbol: str,
    redis_client: Optional[redis.Redis] = Depends(get_redis)
):
    """获取股票基本信息"""
    try:
        logger.info(f"📊 获取股票信息: {symbol}")
        
        # 检查缓存
        cache_key = f"stock_info:{symbol}"
        if redis_client:
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                logger.debug(f"💾 从缓存获取股票信息: {symbol}")
                import json
                return APIResponse(
                    success=True,
                    message="获取股票信息成功（缓存）",
                    data=json.loads(cached_data)
                )
        
        # 从数据源获取
        info_data = get_china_stock_info_unified(symbol)
        
        if not info_data or "错误" in str(info_data):
            raise HTTPException(status_code=404, detail=f"未找到股票 {symbol} 的信息")
        
        # 解析数据（这里需要根据实际返回格式调整）
        stock_info = {
            "symbol": symbol,
            "name": "股票名称",  # 需要从info_data中解析
            "market": "A股",
            "industry": None,
            "sector": None,
            "market_cap": None,
            "currency": "CNY"
        }
        
        # 缓存数据
        if redis_client:
            import json
            await redis_client.setex(
                cache_key, 
                3600,  # 1小时缓存
                json.dumps(stock_info, ensure_ascii=False)
            )
        
        return APIResponse(
            success=True,
            message="获取股票信息成功",
            data=stock_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取股票信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取股票信息失败: {str(e)}")


@app.post("/api/stock/data", response_model=APIResponse)
async def get_stock_data(
    request: StockDataRequest,
    redis_client: Optional[redis.Redis] = Depends(get_redis)
):
    """获取股票历史数据"""
    try:
        logger.info(f"📈 获取股票数据: {request.symbol} ({request.start_date} - {request.end_date})")
        
        # 检查缓存
        cache_key = f"stock_data:{request.symbol}:{request.start_date}:{request.end_date}"
        if redis_client:
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                logger.debug(f"💾 从缓存获取股票数据: {request.symbol}")
                import json
                return APIResponse(
                    success=True,
                    message="获取股票数据成功（缓存）",
                    data=json.loads(cached_data)
                )
        
        # 从数据源获取
        stock_data = get_china_stock_data_unified(
            request.symbol,
            request.start_date,
            request.end_date
        )
        
        if not stock_data or "错误" in str(stock_data):
            raise HTTPException(status_code=404, detail=f"未找到股票 {request.symbol} 的数据")
        
        # 解析数据（这里需要根据实际返回格式调整）
        # 假设返回的是CSV格式的字符串，需要解析成结构化数据
        parsed_data = {
            "symbol": request.symbol,
            "data": stock_data,  # 暂时直接返回原始数据
            "start_date": request.start_date,
            "end_date": request.end_date
        }
        
        # 缓存数据
        if redis_client:
            import json
            await redis_client.setex(
                cache_key,
                1800,  # 30分钟缓存
                json.dumps(parsed_data, ensure_ascii=False)
            )
        
        return APIResponse(
            success=True,
            message="获取股票数据成功",
            data=parsed_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取股票数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取股票数据失败: {str(e)}")


@app.get("/api/stock/fundamentals/{symbol}", response_model=APIResponse)
async def get_stock_fundamentals(
    symbol: str,
    start_date: str,
    end_date: str,
    curr_date: str,
    redis_client: Optional[redis.Redis] = Depends(get_redis)
):
    """获取股票基本面数据"""
    try:
        logger.info(f"📊 获取基本面数据: {symbol}")
        
        # 检查缓存
        cache_key = f"fundamentals:{symbol}:{curr_date}"
        if redis_client:
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                logger.debug(f"💾 从缓存获取基本面数据: {symbol}")
                import json
                return APIResponse(
                    success=True,
                    message="获取基本面数据成功（缓存）",
                    data=json.loads(cached_data)
                )
        
        # 从数据源获取
        fundamentals_data = get_china_stock_fundamentals_tushare(symbol)
        
        if not fundamentals_data or "错误" in str(fundamentals_data):
            raise HTTPException(status_code=404, detail=f"未找到股票 {symbol} 的基本面数据")
        
        result_data = {
            "symbol": symbol,
            "data": fundamentals_data,
            "date": curr_date
        }
        
        # 缓存数据
        if redis_client:
            import json
            await redis_client.setex(
                cache_key,
                3600,  # 1小时缓存
                json.dumps(result_data, ensure_ascii=False)
            )
        
        return APIResponse(
            success=True,
            message="获取基本面数据成功",
            data=result_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取基本面数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取基本面数据失败: {str(e)}")


@app.get("/api/stock/news/{symbol}", response_model=APIResponse)
async def get_stock_news(
    symbol: str,
    redis_client: Optional[redis.Redis] = Depends(get_redis)
):
    """获取股票新闻"""
    try:
        logger.info(f"📰 获取股票新闻: {symbol}")
        
        # 检查缓存
        cache_key = f"news:{symbol}"
        if redis_client:
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                logger.debug(f"💾 从缓存获取股票新闻: {symbol}")
                import json
                return APIResponse(
                    success=True,
                    message="获取股票新闻成功（缓存）",
                    data=json.loads(cached_data)
                )
        
        # 从数据源获取 (使用实时新闻API)
        try:
            from tradingagents.dataflows.realtime_news_utils import get_realtime_stock_news
            from datetime import datetime
            curr_date = datetime.now().strftime('%Y-%m-%d')
            hours_back = 24 * 7  # 查看最近7天的新闻
            news_data = get_realtime_stock_news(symbol, curr_date, hours_back)
        except ImportError:
            # 备用方案：使用本地文件方式
            from datetime import datetime
            curr_date = datetime.now().strftime('%Y-%m-%d')
            look_back_days = 7
            news_data = get_finnhub_news(symbol, curr_date, look_back_days)
        
        if not news_data or "错误" in str(news_data):
            raise HTTPException(status_code=404, detail=f"未找到股票 {symbol} 的新闻")
        
        result_data = {
            "symbol": symbol,
            "news": news_data
        }
        
        # 缓存数据
        if redis_client:
            import json
            await redis_client.setex(
                cache_key,
                1800,  # 30分钟缓存
                json.dumps(result_data, ensure_ascii=False)
            )
        
        return APIResponse(
            success=True,
            message="获取股票新闻成功",
            data=result_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取股票新闻失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取股票新闻失败: {str(e)}")


@app.get("/api/data-sources/status", response_model=APIResponse)
async def get_data_sources_status():
    """获取数据源状态"""
    try:
        # 这里可以检查各个数据源的状态
        status_data = {
            "tushare": {"status": "healthy", "last_update": "2025-01-20T10:00:00Z"},
            "akshare": {"status": "healthy", "last_update": "2025-01-20T10:00:00Z"},
            "baostock": {"status": "healthy", "last_update": "2025-01-20T10:00:00Z"},
        }
        
        return APIResponse(
            success=True,
            message="获取数据源状态成功",
            data=status_data
        )
        
    except Exception as e:
        logger.error(f"❌ 获取数据源状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据源状态失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    config = get_service_config("data_service")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config['port'],
        reload=config['debug'],
        log_level=config['log_level'].lower()
    )
