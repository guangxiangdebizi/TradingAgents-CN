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

# 加载环境变量 - 优先加载backend目录的.env，然后是项目根目录的.env
try:
    from dotenv import load_dotenv

    # 获取backend目录路径
    backend_dir = Path(__file__).parent.parent.parent

    # 优先加载backend目录的.env文件
    backend_env = backend_dir / ".env"
    if backend_env.exists():
        load_dotenv(backend_env, override=True)
        print(f"✅ 加载Backend环境变量: {backend_env}")

    # 然后加载项目根目录的.env文件（作为备用）
    root_env = project_root / ".env"
    if root_env.exists():
        load_dotenv(root_env, override=False)  # 不覆盖已有的环境变量
        print(f"✅ 加载项目根目录环境变量: {root_env}")

    if not backend_env.exists() and not root_env.exists():
        print("⚠️ 未找到.env文件，将使用系统环境变量")

except ImportError:
    print("⚠️ python-dotenv未安装，将使用系统环境变量")

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

# 导入国际化模块
from backend.shared.i18n import get_i18n_manager, _, SupportedLanguage
from backend.shared.i18n.middleware import I18nMiddleware, i18n_response
from backend.shared.i18n.utils import localize_stock_data, get_supported_languages
from backend.shared.i18n.logger import get_i18n_logger
from backend.shared.i18n.debug_middleware import (
    APIDebugMiddleware, PerformanceMonitorMiddleware, ValidationDebugMiddleware
)

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


def _parse_stock_data_to_structured_format(stock_data: str, symbol: str, start_date: str, end_date: str) -> dict:
    """
    解析股票数据字符串为结构化格式
    支持Markdown格式和表格数据的混合格式

    Args:
        stock_data: 格式化的股票数据字符串
        symbol: 股票代码
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        dict: 结构化的股票数据
    """
    try:
        # 初始化结果结构
        result = {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "close_prices": [],
            "volumes": [],
            "open_prices": [],
            "high_prices": [],
            "low_prices": [],
            "dates": [],
            "raw_data": stock_data
        }

        lines = stock_data.strip().split('\n')

        # 查找数据表格部分（通常在"最新交易数据"或"最新数据"之后）
        data_start_index = -1

        # 方法1：查找包含表格头部的行
        for i, line in enumerate(lines):
            # 查找包含列名的行（Tushare格式）
            if ('ts_code' in line and 'trade_date' in line) or \
               ('代码' in line and '日期' in line) or \
               ('open' in line and 'high' in line and 'low' in line and 'close' in line):
                data_start_index = i
                print(f"🔍 找到表格头部: {line}")
                break

        # 方法2：如果没找到标准头部，查找数据行模式
        if data_start_index == -1:
            for i, line in enumerate(lines):
                # 查找包含股票代码和数字的行（数据行特征）
                if symbol in line and any(char.isdigit() for char in line):
                    # 检查是否是表格数据行格式
                    parts = line.split()
                    if len(parts) >= 6:  # 至少包含代码、日期、开盘、最高、最低、收盘
                        data_start_index = i
                        print(f"🔍 找到数据行开始: {line}")
                        break

        if data_start_index == -1:
            print(f"⚠️ 无法找到数据表格: {symbol}")
            return result

        # 解析数据行
        for line in lines[data_start_index:]:
            if not line.strip() or line.startswith('#') or line.startswith('##'):
                continue

            # 跳过表格头部行
            if 'ts_code' in line or 'trade_date' in line or '代码' in line or '日期' in line:
                continue

            # 解析数据行（支持空格分隔和逗号分隔）
            parts = line.split() if ' ' in line else line.split(',')

            if len(parts) >= 6:  # 至少包含代码、日期、开盘、最高、最低、收盘
                try:
                    # Tushare格式: ts_code trade_date open high low close pre_close change pct_chg vol amount
                    if len(parts) >= 10:  # 完整的Tushare格式
                        ts_code = parts[0].strip()
                        trade_date = parts[1].strip()
                        open_price = float(parts[2].strip()) if parts[2].strip() and parts[2].strip() != 'NaN' else 0.0
                        high_price = float(parts[3].strip()) if parts[3].strip() and parts[3].strip() != 'NaN' else 0.0
                        low_price = float(parts[4].strip()) if parts[4].strip() and parts[4].strip() != 'NaN' else 0.0
                        close_price = float(parts[5].strip()) if parts[5].strip() and parts[5].strip() != 'NaN' else 0.0
                        volume = int(float(parts[9].strip())) if parts[9].strip() and parts[9].strip() != 'NaN' else 0

                        result["dates"].append(trade_date)
                        result["open_prices"].append(open_price)
                        result["high_prices"].append(high_price)
                        result["low_prices"].append(low_price)
                        result["close_prices"].append(close_price)
                        result["volumes"].append(volume)

                    else:  # 简化格式
                        date = parts[1].strip() if len(parts) > 1 else parts[0].strip()
                        open_price = float(parts[2].strip()) if len(parts) > 2 and parts[2].strip() and parts[2].strip() != 'NaN' else 0.0
                        high_price = float(parts[3].strip()) if len(parts) > 3 and parts[3].strip() and parts[3].strip() != 'NaN' else 0.0
                        low_price = float(parts[4].strip()) if len(parts) > 4 and parts[4].strip() and parts[4].strip() != 'NaN' else 0.0
                        close_price = float(parts[5].strip()) if len(parts) > 5 and parts[5].strip() and parts[5].strip() != 'NaN' else 0.0
                        volume = int(float(parts[6].strip())) if len(parts) > 6 and parts[6].strip() and parts[6].strip() != 'NaN' else 0

                        result["dates"].append(date)
                        result["open_prices"].append(open_price)
                        result["high_prices"].append(high_price)
                        result["low_prices"].append(low_price)
                        result["close_prices"].append(close_price)
                        result["volumes"].append(volume)

                except (ValueError, IndexError) as e:
                    print(f"⚠️ 解析数据行失败: {line} - {e}")
                    continue

        print(f"✅ 解析股票数据成功: {symbol}, 共{len(result['close_prices'])}条记录")
        return result

    except Exception as e:
        print(f"❌ 解析股票数据失败: {symbol} - {e}")
        import traceback
        print(f"❌ 详细错误: {traceback.format_exc()}")
        return {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "close_prices": [],
            "volumes": [],
            "open_prices": [],
            "high_prices": [],
            "low_prices": [],
            "dates": [],
            "raw_data": stock_data,
            "error": str(e)
        }


# 全局变量
logger = get_service_logger("data-service")
debug_logger = get_i18n_logger("data-service-debug")
redis_client: Optional[redis.Redis] = None
db_manager = None
data_manager_instance = None
enhanced_data_manager_instance = None


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


def get_data_manager():
    """获取数据管理器实例"""
    global data_manager_instance
    if data_manager_instance is None:
        # 导入并初始化数据管理器
        try:
            from .data_manager import DataManager
            from pymongo import MongoClient
            import redis

            # 创建数据库连接 (带认证)
            mongodb_client = MongoClient("mongodb://admin:tradingagents123@localhost:27017/tradingagents?authSource=admin")
            redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

            # 获取当前语言设置
            current_language = get_i18n_manager().get_language()

            # 创建数据管理器实例
            data_manager_instance = DataManager(mongodb_client, redis_client, current_language)
            logger.info("✅ 数据管理器初始化成功")
        except Exception as e:
            logger.error(f"❌ 数据管理器初始化失败: {e}")
            raise HTTPException(status_code=500, detail=f"数据管理器初始化失败: {str(e)}")

    return data_manager_instance


def get_enhanced_data_manager():
    """获取增强数据管理器实例"""
    global enhanced_data_manager_instance
    if enhanced_data_manager_instance is None:
        try:
            from .enhanced_data_manager import EnhancedDataManager
            from pymongo import MongoClient
            import redis

            # 创建数据库连接 (带认证)
            mongodb_client = MongoClient("mongodb://admin:tradingagents123@localhost:27017/tradingagents?authSource=admin")
            redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

            # 获取当前语言设置
            current_language = get_i18n_manager().get_language()

            # 创建增强数据管理器实例
            enhanced_data_manager_instance = EnhancedDataManager(mongodb_client, redis_client, current_language)
            logger.info("✅ 增强数据管理器初始化成功")
        except Exception as e:
            logger.error(f"❌ 增强数据管理器初始化失败: {e}")
            raise HTTPException(status_code=500, detail=f"增强数据管理器初始化失败: {str(e)}")

    return enhanced_data_manager_instance


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

# 添加调试中间件（开发环境）
import os
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"

if DEBUG_MODE:
    # API调试中间件
    app.add_middleware(
        APIDebugMiddleware,
        enable_debug=True,
        log_headers=True,
        log_body=True
    )

    # 性能监控中间件
    app.add_middleware(PerformanceMonitorMiddleware, enable_monitoring=True)

    # 验证调试中间件
    app.add_middleware(ValidationDebugMiddleware, enable_validation_debug=True)

# 添加国际化中间件
app.add_middleware(I18nMiddleware, auto_detect=True)

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

# ===== 国际化接口 =====

@app.get("/api/i18n/languages", response_model=APIResponse)
async def get_supported_languages_api():
    """获取支持的语言列表"""
    try:
        languages = get_supported_languages()
        return i18n_response.success_response("api.success.languages", languages)
    except Exception as e:
        logger.error(f"❌ 获取语言列表失败: {e}")
        return i18n_response.error_response("api.error.internal_error")

@app.get("/api/i18n/current", response_model=APIResponse)
async def get_current_language():
    """获取当前语言"""
    try:
        i18n_manager = get_i18n_manager()
        current_lang = i18n_manager.get_language()

        return i18n_response.success_response("api.success.current_language", {
            "language": current_lang.value,
            "name": i18n_manager.get_available_languages().get(current_lang.value, current_lang.value)
        })
    except Exception as e:
        logger.error(f"❌ 获取当前语言失败: {e}")
        return i18n_response.error_response("api.error.internal_error")

@app.post("/api/i18n/set-language", response_model=APIResponse)
async def set_language(request: dict):
    """设置语言"""
    try:
        language = request.get("language")
        if not language:
            return i18n_response.error_response("api.validation.required_field")

        i18n_manager = get_i18n_manager()
        if i18n_manager.set_language(language):
            return i18n_response.success_response("api.success.language_set", {
                "language": i18n_manager.get_language().value
            })
        else:
            return i18n_response.error_response("api.error.invalid_language")
    except Exception as e:
        logger.error(f"❌ 设置语言失败: {e}")
        return i18n_response.error_response("api.error.internal_error")

@app.get("/api/i18n/stats", response_model=APIResponse)
async def get_translation_stats():
    """获取翻译统计信息"""
    try:
        i18n_manager = get_i18n_manager()
        stats = i18n_manager.get_translation_stats()
        return i18n_response.success_response("api.success.translation_stats", stats)
    except Exception as e:
        logger.error(f"❌ 获取翻译统计失败: {e}")
        return i18n_response.error_response("api.error.internal_error")

@app.post("/api/i18n/set-log-language", response_model=APIResponse)
async def set_log_language(request: dict):
    """设置日志语言"""
    try:
        language = request.get("language")
        if not language:
            return i18n_response.error_response("api.validation.required_field")

        # 设置全局语言
        i18n_manager = get_i18n_manager()
        if not i18n_manager.set_language(language):
            return i18n_response.error_response("api.error.invalid_language")

        # 设置数据管理器日志语言
        data_manager = get_data_manager()
        data_manager.set_log_language(i18n_manager.get_language())

        return i18n_response.success_response("api.success.log_language_set", {
            "language": i18n_manager.get_language().value
        })
    except Exception as e:
        logger.error(f"❌ 设置日志语言失败: {e}")
        return i18n_response.error_response("api.error.internal_error")

@app.get("/api/stock/info/{symbol}", response_model=APIResponse)
async def get_stock_info(
    symbol: str,
    force_refresh: bool = False,  # 添加强制刷新参数
    redis_client: Optional[redis.Redis] = Depends(get_redis)
):
    """获取股票基本信息"""
    try:
        # Debug: 记录API调用开始
        debug_logger.debug_api_request_received("GET", f"/api/stock/info/{symbol}")
        debug_logger.debug_validation_start("symbol")

        if not symbol or len(symbol.strip()) == 0:
            debug_logger.debug_validation_failed("symbol", "empty_or_invalid")
            raise HTTPException(status_code=400, detail="股票代码不能为空")

        debug_logger.debug_validation_passed("symbol")
        logger.info(f"📊 获取股票信息: {symbol}")

        # 检查缓存
        cache_key = f"stock_info:{symbol}"
        debug_logger.debug_cache_check_start(symbol, "stock_info")

        # 检查缓存（除非强制刷新）
        if redis_client and not force_refresh:
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                debug_logger.debug_cache_check_result("hit", symbol)
                logger.debug(f"💾 从缓存获取股票信息: {symbol}")
                import json

                debug_logger.debug_api_response_prepared(200)
                return APIResponse(
                    success=True,
                    message="获取股票信息成功（缓存）",
                    data=json.loads(cached_data)
                )

        if force_refresh:
            logger.info(f"🔄 强制刷新股票信息: {symbol}")

        debug_logger.debug_cache_check_result("miss", symbol)
        
        # 从数据源获取
        debug_logger.debug_data_source_select("china_stock_unified", symbol)
        debug_logger.debug_data_source_call("china_stock_unified", f"stock_info/{symbol}")

        info_data = get_china_stock_info_unified(symbol)

        if not info_data or "错误" in str(info_data):
            debug_logger.debug_data_source_response("china_stock_unified", "error", 0)
            raise HTTPException(status_code=404, detail=f"未找到股票 {symbol} 的信息")

        debug_logger.debug_data_source_response("china_stock_unified", "success", len(str(info_data)))

        # 解析数据（从Tushare返回的数据中提取）
        debug_logger.debug_data_transform_start("raw_response", "stock_info")

        # 调试：打印info_data的类型和内容
        logger.info(f"🔍 [调试] info_data类型: {type(info_data)}")
        logger.info(f"🔍 [调试] info_data内容: {info_data}")

        # 从info_data中提取实际数据
        if isinstance(info_data, str) and "股票名称:" in info_data:
            # 解析字符串格式的数据
            lines = info_data.split('\n')
            name = "未知股票"
            area = None
            industry = None
            market = "A股"

            for line in lines:
                if "股票名称:" in line:
                    name = line.split(':')[1].strip()
                elif "所属地区:" in line:
                    area = line.split(':')[1].strip()
                elif "所属行业:" in line:
                    industry = line.split(':')[1].strip()
                elif "上市市场:" in line:
                    market = line.split(':')[1].strip()

            stock_info = {
                "symbol": symbol,
                "name": name,
                "market": market,
                "industry": industry,
                "sector": area,
                "market_cap": None,
                "currency": "CNY"
            }
        elif isinstance(info_data, list) and len(info_data) > 0:
            # 处理列表格式的数据
            data = info_data[0]  # 取第一条记录
            stock_info = {
                "symbol": symbol,
                "name": data.get("name", "未知股票"),
                "market": data.get("market", "A股"),
                "industry": data.get("industry"),
                "sector": data.get("area"),  # 使用area作为sector
                "market_cap": None,  # Tushare基础信息中没有市值
                "currency": "CNY"
            }
        else:
            # 如果数据格式不对，使用默认值
            stock_info = {
                "symbol": symbol,
                "name": "未知股票",
                "market": "A股",
                "industry": None,
                "sector": None,
                "market_cap": None,
                "currency": "CNY"
            }
        debug_logger.debug_data_transform_end(1)

        # 详细调试：打印最终的stock_info内容
        logger.info(f"🔍 [最终结果] stock_info内容: {stock_info}")

        # 缓存数据
        if redis_client:
            debug_logger.debug_cache_save_start(symbol, "stock_info")
            import json
            await redis_client.setex(
                cache_key,
                3600,  # 1小时缓存
                json.dumps(stock_info, ensure_ascii=False)
            )
            debug_logger.debug_cache_save_end(symbol, 3600)

        # 本地化数据
        debug_logger.debug_data_transform_start("stock_info", "localized_data")
        localized_data = localize_stock_data(stock_info)
        debug_logger.debug_data_transform_end(1)

        # Debug: 记录响应准备
        debug_logger.debug_api_response_prepared(200)

        # 使用国际化响应
        return i18n_response.success_response("api.success.stock_info", localized_data)
        
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
        logger.info(f"🔍 调用数据源获取: {request.symbol}")
        stock_data = get_china_stock_data_unified(
            request.symbol,
            request.start_date,
            request.end_date
        )

        logger.info(f"🔍 原始数据类型: {type(stock_data)}")
        logger.info(f"🔍 原始数据长度: {len(str(stock_data)) if stock_data else 0}")
        logger.info(f"🔍 原始数据完整内容: {str(stock_data) if stock_data else 'None'}")

        if not stock_data or "错误" in str(stock_data):
            raise HTTPException(status_code=404, detail=f"未找到股票 {request.symbol} 的数据")

        # 解析数据为结构化格式
        logger.info(f"🔍 开始解析数据为结构化格式: {request.symbol}")
        parsed_data = _parse_stock_data_to_structured_format(
            stock_data, request.symbol, request.start_date, request.end_date
        )

        logger.info(f"🔍 解析后数据类型: {type(parsed_data)}")
        logger.info(f"🔍 解析后数据键: {list(parsed_data.keys()) if isinstance(parsed_data, dict) else 'Not a dict'}")
        if isinstance(parsed_data, dict):
            logger.info(f"🔍 close_prices数量: {len(parsed_data.get('close_prices', []))}")
            logger.info(f"🔍 volumes数量: {len(parsed_data.get('volumes', []))}")
        logger.info(f"🔍 解析后数据: {str(parsed_data)[:300]}")
        
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
        data_manager = get_data_manager()
        status_data = await data_manager.health_check_data_sources()

        return APIResponse(
            success=True,
            message="获取数据源状态成功",
            data=status_data
        )

    except Exception as e:
        logger.error(f"❌ 获取数据源状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据源状态失败: {str(e)}")

@app.get("/api/data-sources/stats", response_model=APIResponse)
async def get_data_sources_stats():
    """获取数据源统计信息"""
    try:
        data_manager = get_data_manager()
        factory = data_manager.data_source_factory
        stats_data = factory.get_source_stats()

        return APIResponse(
            success=True,
            message="获取数据源统计成功",
            data=stats_data
        )

    except Exception as e:
        logger.error(f"❌ 获取数据源统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据源统计失败: {str(e)}")

@app.post("/api/data-sources/health-check", response_model=APIResponse)
async def trigger_health_check():
    """手动触发数据源健康检查"""
    try:
        data_manager = get_data_manager()
        health_status = await data_manager.health_check_data_sources()

        return APIResponse(
            success=True,
            message="数据源健康检查完成",
            data=health_status
        )

    except Exception as e:
        logger.error(f"❌ 数据源健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"数据源健康检查失败: {str(e)}")

# ===== 数据源优先级管理接口 =====

@app.get("/api/data-sources/priority/profiles", response_model=APIResponse)
async def get_priority_profiles():
    """获取所有优先级配置文件"""
    try:
        data_manager = get_data_manager()
        factory = data_manager.data_source_factory
        profiles = factory.get_available_priority_profiles()

        return APIResponse(
            success=True,
            message="获取优先级配置文件成功",
            data=profiles
        )

    except Exception as e:
        logger.error(f"❌ 获取优先级配置文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取优先级配置文件失败: {str(e)}")

@app.get("/api/data-sources/priority/current", response_model=APIResponse)
async def get_current_priority_profile():
    """获取当前使用的优先级配置文件"""
    try:
        data_manager = get_data_manager()
        factory = data_manager.data_source_factory
        current_profile = factory.get_current_priority_profile()

        return APIResponse(
            success=True,
            message="获取当前优先级配置成功",
            data={"current_profile": current_profile}
        )

    except Exception as e:
        logger.error(f"❌ 获取当前优先级配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取当前优先级配置失败: {str(e)}")

@app.post("/api/data-sources/priority/switch", response_model=APIResponse)
async def switch_priority_profile(request: dict):
    """切换优先级配置文件"""
    try:
        profile_name = request.get("profile_name")
        if not profile_name:
            raise HTTPException(status_code=400, detail="缺少 profile_name 参数")

        data_manager = get_data_manager()
        factory = data_manager.data_source_factory

        if factory.set_priority_profile(profile_name):
            return APIResponse(
                success=True,
                message=f"成功切换到配置文件: {profile_name}",
                data={"new_profile": profile_name}
            )
        else:
            raise HTTPException(status_code=400, detail=f"配置文件不存在: {profile_name}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 切换优先级配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"切换优先级配置失败: {str(e)}")

@app.post("/api/data-sources/priority/reload", response_model=APIResponse)
async def reload_priority_config():
    """重新加载优先级配置"""
    try:
        data_manager = get_data_manager()
        factory = data_manager.data_source_factory

        if factory.reload_priority_config():
            return APIResponse(
                success=True,
                message="优先级配置重新加载成功",
                data={}
            )
        else:
            raise HTTPException(status_code=500, detail="重新加载配置失败")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 重新加载优先级配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"重新加载优先级配置失败: {str(e)}")

# ===== 本地数据管理接口 =====

@app.get("/api/local-data/summary", response_model=APIResponse)
async def get_local_data_summary():
    """获取本地数据存储摘要"""
    try:
        data_manager = get_data_manager()
        summary = await data_manager.get_local_data_summary()

        return APIResponse(
            success=True,
            message="获取本地数据摘要成功",
            data=summary
        )

    except Exception as e:
        logger.error(f"❌ 获取本地数据摘要失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取本地数据摘要失败: {str(e)}")

@app.get("/api/local-data/history/{symbol}", response_model=APIResponse)
async def get_symbol_data_history(symbol: str):
    """获取特定股票的数据历史"""
    try:
        data_manager = get_data_manager()
        history = await data_manager.get_symbol_data_history(symbol)

        return APIResponse(
            success=True,
            message=f"获取 {symbol} 数据历史成功",
            data=history
        )

    except Exception as e:
        logger.error(f"❌ 获取股票数据历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取股票数据历史失败: {str(e)}")

@app.post("/api/local-data/cleanup", response_model=APIResponse)
async def cleanup_old_data(request: dict):
    """清理旧数据"""
    try:
        days = request.get("days", 30)
        if not isinstance(days, int) or days < 1:
            raise HTTPException(status_code=400, detail="days 参数必须是大于0的整数")

        data_manager = get_data_manager()
        cleanup_stats = await data_manager.cleanup_old_data(days)

        return APIResponse(
            success=True,
            message=f"清理 {days} 天前的旧数据成功",
            data=cleanup_stats
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 清理旧数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"清理旧数据失败: {str(e)}")

@app.post("/api/local-data/force-refresh", response_model=APIResponse)
async def force_refresh_data(request: dict):
    """强制刷新数据（忽略缓存）"""
    try:
        symbol = request.get("symbol")
        data_type = request.get("data_type")

        if not symbol or not data_type:
            raise HTTPException(status_code=400, detail="缺少 symbol 或 data_type 参数")

        # 验证数据类型
        try:
            from .data_manager import DataType
            dt = DataType(data_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的数据类型: {data_type}")

        data_manager = get_data_manager()

        # 准备额外参数
        kwargs = {}
        if dt in [DataType.STOCK_DATA, DataType.FUNDAMENTALS]:
            kwargs["start_date"] = request.get("start_date", "2024-01-01")
            kwargs["end_date"] = request.get("end_date", "2024-12-31")
        elif dt == DataType.NEWS:
            kwargs["start_date"] = request.get("start_date", "2024-01-01")
            kwargs["end_date"] = request.get("end_date", "2024-12-31")

        success, data = await data_manager.force_refresh_data(symbol, dt, **kwargs)

        if success:
            return APIResponse(
                success=True,
                message=f"强制刷新 {symbol} {data_type} 数据成功",
                data={"symbol": symbol, "data_type": data_type, "refreshed": True}
            )
        else:
            raise HTTPException(status_code=500, detail="数据刷新失败")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 强制刷新数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"强制刷新数据失败: {str(e)}")


# ===== 以下是供 task-scheduler 调用的管理接口 =====

from pydantic import BaseModel
from typing import List

class BatchUpdateRequest(BaseModel):
    symbols: List[str]
    data_types: List[str]  # ["stock_info", "stock_data", "fundamentals", "news"]
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class CacheCleanupRequest(BaseModel):
    data_types: Optional[List[str]] = None  # 指定清理的数据类型，None表示全部
    older_than_hours: Optional[int] = 24    # 清理多少小时前的数据

@app.post("/api/admin/batch-update", response_model=APIResponse)
async def batch_update_data(
    request: BatchUpdateRequest,
    redis_client: Optional[redis.Redis] = Depends(get_redis)
):
    """批量更新数据 - 供调度器调用"""
    try:
        logger.info(f"🔄 批量更新数据: {len(request.symbols)} 只股票, 数据类型: {request.data_types}")

        results = []
        total_success = 0
        total_failed = 0

        for symbol in request.symbols:
            symbol_results = {"symbol": symbol, "updates": []}

            for data_type in request.data_types:
                try:
                    if data_type == "stock_info":
                        # 更新股票信息
                        info_data = get_china_stock_info_unified(symbol)
                        if info_data and "错误" not in str(info_data):
                            # 缓存数据
                            if redis_client:
                                cache_key = f"stock_info:{symbol}"
                                stock_info = {
                                    "symbol": symbol,
                                    "name": "股票名称",
                                    "market": "A股",
                                    "data": info_data
                                }
                                import json
                                await redis_client.setex(
                                    cache_key, 3600,
                                    json.dumps(stock_info, ensure_ascii=False)
                                )
                            symbol_results["updates"].append({
                                "data_type": data_type,
                                "success": True
                            })
                            total_success += 1
                        else:
                            symbol_results["updates"].append({
                                "data_type": data_type,
                                "success": False,
                                "error": "数据获取失败"
                            })
                            total_failed += 1

                    elif data_type == "stock_data":
                        # 更新股票数据
                        start_date = request.start_date or "2025-01-01"
                        end_date = request.end_date or "2025-01-20"

                        stock_data = get_china_stock_data_unified(symbol, start_date, end_date)
                        if stock_data and "错误" not in str(stock_data):
                            # 缓存数据
                            if redis_client:
                                cache_key = f"stock_data:{symbol}:{start_date}:{end_date}"
                                parsed_data = {
                                    "symbol": symbol,
                                    "data": stock_data,
                                    "start_date": start_date,
                                    "end_date": end_date
                                }
                                import json
                                await redis_client.setex(
                                    cache_key, 1800,
                                    json.dumps(parsed_data, ensure_ascii=False)
                                )
                            symbol_results["updates"].append({
                                "data_type": data_type,
                                "success": True
                            })
                            total_success += 1
                        else:
                            symbol_results["updates"].append({
                                "data_type": data_type,
                                "success": False,
                                "error": "数据获取失败"
                            })
                            total_failed += 1

                    elif data_type == "fundamentals":
                        # 更新基本面数据
                        fundamentals_data = get_china_stock_fundamentals_tushare(symbol)
                        if fundamentals_data and "错误" not in str(fundamentals_data):
                            # 缓存数据
                            if redis_client:
                                from datetime import datetime
                                curr_date = datetime.now().strftime("%Y-%m-%d")
                                cache_key = f"fundamentals:{symbol}:{curr_date}"
                                result_data = {
                                    "symbol": symbol,
                                    "data": fundamentals_data,
                                    "date": curr_date
                                }
                                import json
                                await redis_client.setex(
                                    cache_key, 3600,
                                    json.dumps(result_data, ensure_ascii=False)
                                )
                            symbol_results["updates"].append({
                                "data_type": data_type,
                                "success": True
                            })
                            total_success += 1
                        else:
                            symbol_results["updates"].append({
                                "data_type": data_type,
                                "success": False,
                                "error": "数据获取失败"
                            })
                            total_failed += 1

                    elif data_type == "news":
                        # 更新新闻数据
                        try:
                            from tradingagents.dataflows.realtime_news_utils import get_realtime_stock_news
                            from datetime import datetime
                            curr_date = datetime.now().strftime('%Y-%m-%d')
                            hours_back = 24 * 7
                            news_data = get_realtime_stock_news(symbol, curr_date, hours_back)
                        except ImportError:
                            from datetime import datetime
                            curr_date = datetime.now().strftime('%Y-%m-%d')
                            look_back_days = 7
                            news_data = get_finnhub_news(symbol, curr_date, look_back_days)

                        if news_data and "错误" not in str(news_data):
                            # 缓存数据
                            if redis_client:
                                cache_key = f"news:{symbol}"
                                result_data = {
                                    "symbol": symbol,
                                    "news": news_data
                                }
                                import json
                                await redis_client.setex(
                                    cache_key, 1800,
                                    json.dumps(result_data, ensure_ascii=False)
                                )
                            symbol_results["updates"].append({
                                "data_type": data_type,
                                "success": True
                            })
                            total_success += 1
                        else:
                            symbol_results["updates"].append({
                                "data_type": data_type,
                                "success": False,
                                "error": "数据获取失败"
                            })
                            total_failed += 1

                    # 避免请求过于频繁
                    import asyncio
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.warning(f"⚠️ 更新失败: {symbol} - {data_type} - {e}")
                    symbol_results["updates"].append({
                        "data_type": data_type,
                        "success": False,
                        "error": str(e)
                    })
                    total_failed += 1

            results.append(symbol_results)

        return APIResponse(
            success=True,
            message=f"批量更新完成: 成功 {total_success}, 失败 {total_failed}",
            data={
                "summary": {
                    "total_symbols": len(request.symbols),
                    "total_updates": total_success + total_failed,
                    "successful": total_success,
                    "failed": total_failed
                },
                "details": results
            }
        )

    except Exception as e:
        logger.error(f"❌ 批量更新数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量更新数据失败: {str(e)}")

@app.post("/api/admin/cleanup-cache", response_model=APIResponse)
async def cleanup_cache(
    request: CacheCleanupRequest,
    redis_client: Optional[redis.Redis] = Depends(get_redis)
):
    """清理缓存数据 - 供调度器调用"""
    try:
        logger.info("🧹 开始清理缓存数据")

        if not redis_client:
            return APIResponse(
                success=False,
                message="Redis 未连接，无法清理缓存"
            )

        cleaned_count = 0

        # 获取所有缓存键
        if request.data_types:
            # 清理指定类型的缓存
            for data_type in request.data_types:
                pattern = f"{data_type}:*"
                keys = await redis_client.keys(pattern)
                if keys:
                    deleted = await redis_client.delete(*keys)
                    cleaned_count += deleted
                    logger.info(f"清理 {data_type} 缓存: {deleted} 个键")
        else:
            # 清理所有数据缓存
            patterns = ["stock_info:*", "stock_data:*", "fundamentals:*", "news:*"]
            for pattern in patterns:
                keys = await redis_client.keys(pattern)
                if keys:
                    deleted = await redis_client.delete(*keys)
                    cleaned_count += deleted
                    logger.info(f"清理 {pattern} 缓存: {deleted} 个键")

        return APIResponse(
            success=True,
            message=f"缓存清理完成，清理了 {cleaned_count} 个缓存项",
            data={"cleaned_count": cleaned_count}
        )

    except Exception as e:
        logger.error(f"❌ 清理缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"清理缓存失败: {str(e)}")

@app.get("/api/admin/statistics", response_model=APIResponse)
async def get_data_statistics(
    redis_client: Optional[redis.Redis] = Depends(get_redis)
):
    """获取数据统计信息 - 供调度器调用"""
    try:
        stats = {}

        if redis_client:
            # Redis 统计
            info = await redis_client.info()
            stats["redis"] = {
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }

            # 缓存数据统计
            cache_stats = {}
            data_types = ["stock_info", "stock_data", "fundamentals", "news"]
            for data_type in data_types:
                pattern = f"{data_type}:*"
                keys = await redis_client.keys(pattern)
                cache_stats[data_type] = len(keys)

            stats["cache_counts"] = cache_stats
        else:
            stats["redis"] = "not_connected"

        # MongoDB 统计（如果连接）
        if db_manager and db_manager.is_connected():
            # 这里可以添加 MongoDB 统计信息
            stats["mongodb"] = {
                "status": "connected",
                "collections": []  # 可以添加集合统计
            }
        else:
            stats["mongodb"] = "not_connected"

        return APIResponse(
            success=True,
            message="数据统计获取成功",
            data=stats
        )

    except Exception as e:
        logger.error(f"❌ 获取数据统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据统计失败: {str(e)}")

@app.post("/api/admin/preheat-cache", response_model=APIResponse)
async def preheat_cache(
    symbols: List[str],
    redis_client: Optional[redis.Redis] = Depends(get_redis)
):
    """预热缓存 - 供调度器调用"""
    try:
        logger.info(f"🔥 开始预热缓存: {len(symbols)} 只股票")

        preheated_count = 0

        for symbol in symbols:
            try:
                # 预热股票信息
                info_data = get_china_stock_info_unified(symbol)
                if info_data and "错误" not in str(info_data) and redis_client:
                    cache_key = f"stock_info:{symbol}"
                    stock_info = {
                        "symbol": symbol,
                        "name": "股票名称",
                        "market": "A股",
                        "data": info_data
                    }
                    import json
                    await redis_client.setex(
                        cache_key, 3600,
                        json.dumps(stock_info, ensure_ascii=False)
                    )
                    preheated_count += 1

                # 避免请求过于频繁
                import asyncio
                await asyncio.sleep(1)

            except Exception as e:
                logger.warning(f"⚠️ 预热失败: {symbol} - {e}")

        return APIResponse(
            success=True,
            message=f"缓存预热完成: {preheated_count} 只股票",
            data={"preheated_count": preheated_count}
        )

    except Exception as e:
        logger.error(f"❌ 缓存预热失败: {e}")
        raise HTTPException(status_code=500, detail=f"缓存预热失败: {str(e)}")


# ===== 增强数据接口 =====

@app.get("/api/enhanced/stock/{symbol}", response_model=APIResponse)
async def get_enhanced_stock_data(
    symbol: str,
    start_date: str = "2024-12-01",
    end_date: str = "2024-12-31",
    force_refresh: bool = False,
    clear_all_cache: bool = False
):
    """
    获取增强的股票数据 - 集成TradingAgents优秀实现

    Args:
        symbol: 股票代码 (如: AAPL, 000858, 00700)
        start_date: 开始日期
        end_date: 结束日期
        force_refresh: 是否强制刷新缓存
        clear_all_cache: 是否清除所有缓存（包括数据源缓存）
    """
    try:
        # Debug: 记录API调用
        debug_logger.debug_api_request_received("GET", f"/api/enhanced/stock/{symbol}")
        debug_logger.debug_validation_start("symbol")

        if not symbol or len(symbol.strip()) == 0:
            debug_logger.debug_validation_failed("symbol", "empty_or_invalid")
            raise HTTPException(status_code=400, detail="股票代码不能为空")

        debug_logger.debug_validation_passed("symbol")

        # 获取增强数据管理器
        enhanced_manager = get_enhanced_data_manager()

        # 如果需要清除所有缓存，先清除数据源缓存
        if clear_all_cache:
            try:
                # 清除数据源工厂的缓存
                from .datasources.factory import get_data_source_factory
                factory = get_data_source_factory()
                # 这里可以添加清除数据源缓存的逻辑
                logger.info(f"🗑️ 清除所有缓存: {symbol}")
                force_refresh = True  # 同时强制刷新
            except Exception as e:
                logger.warning(f"⚠️ 清除缓存失败: {e}")

        # 获取增强股票数据
        result = await enhanced_manager.get_enhanced_stock_data(
            symbol=symbol.upper(),
            start_date=start_date,
            end_date=end_date,
            force_refresh=force_refresh
        )

        debug_logger.debug_api_response_prepared(200)

        # 使用国际化响应
        return i18n_response.success_response("api.success.enhanced_stock_data", result)

    except HTTPException:
        raise
    except Exception as e:
        debug_logger.debug("log.debug.api.internal_error", symbol=symbol, error=str(e))
        logger.error(f"❌ 获取增强股票数据失败: {symbol} - {e}")
        raise HTTPException(status_code=500, detail=f"获取增强股票数据失败: {str(e)}")


@app.get("/api/enhanced/stock/{symbol}/formatted")
async def get_enhanced_stock_data_formatted(
    symbol: str,
    start_date: str = "2024-12-01",
    end_date: str = "2024-12-31",
    force_refresh: bool = False
):
    """
    获取增强的股票数据 - 返回格式化的文本数据 (TradingAgents风格)
    """
    try:
        # 获取增强数据管理器
        enhanced_manager = get_enhanced_data_manager()

        # 获取增强股票数据
        result = await enhanced_manager.get_enhanced_stock_data(
            symbol=symbol.upper(),
            start_date=start_date,
            end_date=end_date,
            force_refresh=force_refresh
        )

        # 返回格式化的文本数据
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            content=result.get("formatted_data", "数据获取失败"),
            media_type="text/plain; charset=utf-8"
        )

    except Exception as e:
        logger.error(f"❌ 获取格式化股票数据失败: {symbol} - {e}")
        return PlainTextResponse(
            content=f"❌ 获取股票数据失败: {str(e)}",
            media_type="text/plain; charset=utf-8"
        )


# ===== v1 API兼容性端点 (用于智能体调用) =====

@app.get("/api/v1/market/data", response_model=APIResponse)
async def get_market_data_v1(
    market: str,
    data_type: str = "US",
    redis_client: Optional[redis.Redis] = Depends(get_redis)
):
    """获取市场数据 (v1兼容接口)"""
    try:
        # 将v1参数映射到现有的股票信息接口
        return await get_stock_info(market, force_refresh=False, redis_client=redis_client)
    except Exception as e:
        logger.error(f"❌ 获取市场数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取市场数据失败: {str(e)}")

@app.get("/api/v1/company/info", response_model=APIResponse)
async def get_company_info_v1(
    symbol: str,
    redis_client: Optional[redis.Redis] = Depends(get_redis)
):
    """获取公司信息 (v1兼容接口)"""
    try:
        # 映射到现有的股票信息接口
        return await get_stock_info(symbol, force_refresh=False, redis_client=redis_client)
    except Exception as e:
        logger.error(f"❌ 获取公司信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取公司信息失败: {str(e)}")

@app.get("/api/v1/financial/income", response_model=APIResponse)
async def get_financial_income_v1(
    symbol: str,
    period: str = "annual",
    redis_client: Optional[redis.Redis] = Depends(get_redis)
):
    """获取损益表数据 (v1兼容接口)"""
    try:
        # 映射到现有的基本面数据接口
        # 使用默认的日期范围
        start_date = "2023-01-01"
        end_date = "2024-12-31"
        curr_date = "2024-12-31"
        return await get_stock_fundamentals(symbol, start_date, end_date, curr_date, redis_client=redis_client)
    except Exception as e:
        logger.error(f"❌ 获取损益表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取损益表失败: {str(e)}")

@app.get("/api/v1/market/history", response_model=APIResponse)
async def get_market_history_v1(
    symbol: str,
    period: str = "1y",
    interval: str = "1d",
    redis_client: Optional[redis.Redis] = Depends(get_redis)
):
    """获取价格历史数据 (v1兼容接口)"""
    try:
        # 使用独立的市场判断逻辑
        import sys
        from pathlib import Path

        # 添加shared路径
        shared_path = Path(__file__).parent.parent.parent / "shared"
        sys.path.insert(0, str(shared_path))

        from utils.stock_utils import StockUtils
        from datetime import datetime

        current_date = datetime.now().strftime("%Y-%m-%d")
        start_date = "2024-01-01"  # 默认开始日期

        # 判断市场类型
        market_info = StockUtils.get_market_info(symbol)

        if market_info['is_us']:
            # 美股：目前返回占位符，后续可接入美股数据源
            return APIResponse(
                success=True,
                message=f"获取{symbol}价格历史成功",
                data={
                    "symbol": symbol,
                    "market": "US",
                    "start_date": start_date,
                    "end_date": current_date,
                    "period": period,
                    "interval": interval,
                    "message": "美股数据接口开发中，请使用现有的股票数据接口"
                }
            )
        elif market_info['is_china'] or market_info['is_hk']:
            # A股/港股：调用现有的股票数据接口
            request = StockDataRequest(
                symbol=symbol,
                start_date=start_date,
                end_date=current_date,
                period=interval
            )
            return await get_stock_data(request, redis_client=redis_client)
        else:
            # 未知市场
            return APIResponse(
                success=False,
                message=f"无法识别股票市场: {symbol}",
                data={"symbol": symbol, "market": "UNKNOWN"}
            )
    except Exception as e:
        logger.error(f"❌ 获取价格历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取价格历史失败: {str(e)}")


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
        port=config.get('DATA_SERVICE_PORT', 8002),
        reload=False,  # 暂时关闭reload避免频繁监控日志
        log_level=config.get('LOG_LEVEL', 'INFO').lower(),
        reload_excludes=[
            "logs/*",
            "results/*",
            "data/*",
            "*/__pycache__/*",
            "*.log",
            "*.pyc"
        ]
    )
