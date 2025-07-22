"""
数据同步相关的定时任务 - 调用微服务接口
"""
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
import httpx

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from celery import current_task
from tasks.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

# 服务端点配置
SERVICE_URLS = {
    "data_service": os.getenv("DATA_SERVICE_URL", "http://localhost:8002"),
    "analysis_engine": os.getenv("ANALYSIS_ENGINE_URL", "http://localhost:8001")
}

class ServiceClient:
    """微服务客户端"""

    def __init__(self):
        self.timeout = httpx.Timeout(30.0)

    async def call_service(self, service: str, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """调用微服务接口"""
        try:
            base_url = SERVICE_URLS.get(service)
            if not base_url:
                raise ValueError(f"未知服务: {service}")

            url = f"{base_url}{endpoint}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")

                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"调用服务失败: {service} {endpoint} - {e}")
            raise

# 全局客户端实例
service_client = ServiceClient()

def run_async_task(coro):
    """运行异步任务的辅助函数"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)

# 导入数据库访问层
try:
    from backend.shared.database.mongodb import get_db_manager, get_stock_repository

    async def get_async_db_manager():
        return await get_db_manager()

    async def get_async_stock_repository():
        return await get_stock_repository()

except ImportError:
    # 如果导入失败，使用模拟函数
    async def get_async_db_manager():
        return None

    async def get_async_stock_repository():
        return None

# 导入现有的数据获取逻辑
try:
    from tradingagents.dataflows.interface import (
        get_china_stock_data_unified,
        get_china_stock_info_unified,
        get_stock_fundamentals_unified,
        get_stock_news_unified
    )
except ImportError:
    # 如果导入失败，使用模拟函数
    def get_china_stock_data_unified(*args, **kwargs):
        return "模拟股票数据"
    
    def get_china_stock_info_unified(*args, **kwargs):
        return {"symbol": "000001", "name": "模拟股票"}
    
    def get_stock_fundamentals_unified(*args, **kwargs):
        return "模拟财务数据"
    
    def get_stock_news_unified(*args, **kwargs):
        return "模拟新闻数据"

# logger 已在上面定义


def run_async_task(coro):
    """运行异步任务的辅助函数"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


@celery_app.task(bind=True, name='tasks.data_tasks.sync_daily_stock_data')
def sync_daily_stock_data(self, symbols: List[str] = None, date: str = None):
    """
    同步每日股票数据 - 调用 data-service 接口

    Args:
        symbols: 股票代码列表，为空则同步热门股票
        date: 指定日期，为空则使用昨日
    """
    task_id = self.request.id
    logger.info(f"🚀 开始同步每日股票数据 - 任务ID: {task_id}")

    try:
        # 设置默认参数
        if date is None:
            target_date = datetime.now() - timedelta(days=1)
            end_date = target_date.strftime('%Y-%m-%d')
            start_date = end_date
        else:
            start_date = date
            end_date = date

        if symbols is None:
            # 热门股票列表
            symbols = ['000858', '000001', '000002', '600036', '600519', '000725']

        logger.info(f"📊 同步参数: 日期={start_date}, 股票数量={len(symbols)}")

        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': len(symbols), 'status': '开始同步数据'}
        )

        async def sync_data():
            # 调用 data-service 批量更新接口
            result = await service_client.call_service(
                "data_service",
                "/api/admin/batch-update",
                "POST",
                {
                    "symbols": symbols,
                    "data_types": ["stock_info", "stock_data"],
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            return result

        # 执行异步任务
        result = run_async_task(sync_data())

        if result.get("success"):
            data = result.get("data", {})
            summary = data.get("summary", {})

            response = {
                'date': start_date,
                'total_symbols': len(symbols),
                'success_count': summary.get("successful", 0),
                'error_count': summary.get("failed", 0),
                'completion_time': datetime.now().isoformat(),
                'details': data.get("details", [])
            }

            logger.info(f"✅ 每日股票数据同步完成: 成功{summary.get('successful', 0)}个, 失败{summary.get('failed', 0)}个")
            return response
        else:
            raise Exception(f"数据同步失败: {result.get('message', 'Unknown error')}")

    except Exception as e:
        logger.error(f"❌ 每日股票数据同步失败: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'traceback': str(e)}
        )
        raise

@celery_app.task(bind=True, name='tasks.data_tasks.update_hot_stocks_data')
def update_hot_stocks_data(self):
    """更新热门股票数据"""
    task_id = self.request.id
    logger.info(f"🔄 开始更新热门股票数据 - 任务ID: {task_id}")

    try:
        # 热门股票列表
        hot_stocks = {
            "A股": ["000858", "000001", "000002", "600036", "600519", "000725"],
            "美股": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"],
            "港股": ["00700", "09988", "03690", "00941", "02318", "01024"]
        }

        # 准备批量更新请求
        all_symbols = []
        for market, symbols in hot_stocks.items():
            all_symbols.extend(symbols[:3])  # 每个市场取前3只

        # 设置日期范围
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        async def update_data():
            return await service_client.call_service(
                "data_service",
                "/api/admin/batch-update",
                "POST",
                {
                    "symbols": all_symbols,
                    "data_types": ["stock_info", "stock_data"],
                    "start_date": start_date,
                    "end_date": end_date
                }
            )

        # 运行异步任务
        result = run_async_task(update_data())

        logger.info(f"✅ 热门股票数据更新完成: {result.get('message', 'Unknown')}")

        return {
            "task_id": task_id,
            "status": "completed",
            "symbols_count": len(all_symbols),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 更新热门股票数据失败: {e}")
        raise


@celery_app.task(bind=True, name='tasks.data_tasks.update_news_data')
def update_news_data(self):
    """更新新闻数据"""
    task_id = self.request.id
    logger.info(f"📰 开始更新新闻数据 - 任务ID: {task_id}")

    try:
        # 主要关注美股新闻
        news_symbols = ["AAPL", "MSFT", "GOOGL"]

        async def update_data():
            return await service_client.call_service(
                "data_service",
                "/api/admin/batch-update",
                "POST",
                {
                    "symbols": news_symbols,
                    "data_types": ["news"]
                }
            )

        result = run_async_task(update_data())

        logger.info(f"✅ 新闻数据更新完成: {result.get('message', 'Unknown')}")

        return {
            "task_id": task_id,
            "status": "completed",
            "symbols_count": len(news_symbols),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 更新新闻数据失败: {e}")
        raise

@celery_app.task(bind=True, name='tasks.data_tasks.preheat_cache')
def preheat_cache(self):
    """数据预热"""
    task_id = self.request.id
    logger.info(f"🔥 开始数据预热 - 任务ID: {task_id}")

    try:
        # 预热股票列表
        preheat_symbols = ["000858", "000001", "AAPL", "MSFT"]

        async def preheat_data():
            return await service_client.call_service(
                "data_service",
                "/api/admin/preheat-cache",
                "POST",
                preheat_symbols
            )

        result = run_async_task(preheat_data())

        logger.info(f"✅ 数据预热完成: {result.get('message', 'Unknown')}")

        return {
            "task_id": task_id,
            "status": "completed",
            "symbols_count": len(preheat_symbols),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 数据预热失败: {e}")
        raise

@celery_app.task(bind=True, name='tasks.data_tasks.cleanup_expired_data')
def cleanup_expired_data(self):
    """清理过期数据"""
    task_id = self.request.id
    logger.info(f"🧹 开始清理过期数据 - 任务ID: {task_id}")

    try:
        async def cleanup_data():
            return await service_client.call_service(
                "data_service",
                "/api/admin/cleanup-cache",
                "POST",
                {
                    "data_types": None,  # 清理所有类型
                    "older_than_hours": 24
                }
            )

        result = run_async_task(cleanup_data())

        logger.info(f"✅ 过期数据清理完成: {result.get('message', 'Unknown')}")

        return {
            "task_id": task_id,
            "status": "completed",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 清理过期数据失败: {e}")
        raise


@celery_app.task(bind=True, name='tasks.data_tasks.update_fundamentals_data')
def update_fundamentals_data(self):
    """更新基本面数据"""
    task_id = self.request.id
    logger.info(f"📊 开始更新基本面数据 - 任务ID: {task_id}")

    try:
        # 主要更新A股基本面数据
        symbols = ["000858", "000001", "600036"]

        # 设置日期范围
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

        async def update_data():
            return await service_client.call_service(
                "data_service",
                "/api/admin/batch-update",
                "POST",
                {
                    "symbols": symbols,
                    "data_types": ["fundamentals"],
                    "start_date": start_date,
                    "end_date": end_date
                }
            )

        result = run_async_task(update_data())

        logger.info(f"✅ 基本面数据更新完成: {result.get('message', 'Unknown')}")

        return {
            "task_id": task_id,
            "status": "completed",
            "symbols_count": len(symbols),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 更新基本面数据失败: {e}")
        raise

@celery_app.task(bind=True, name='tasks.data_tasks.generate_data_report')
def generate_data_report(self):
    """生成数据统计报告"""
    task_id = self.request.id
    logger.info(f"📋 开始生成数据报告 - 任务ID: {task_id}")

    try:
        async def get_statistics():
            return await service_client.call_service(
                "data_service",
                "/api/admin/statistics",
                "GET"
            )

        result = run_async_task(get_statistics())

        # 这里可以将统计结果保存到数据库或发送报告
        logger.info(f"✅ 数据报告生成完成")

        return {
            "task_id": task_id,
            "status": "completed",
            "statistics": result.get("data", {}),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 生成数据报告失败: {e}")
        raise

# 自定义任务：批量更新指定股票数据
@celery_app.task(bind=True, name='tasks.data_tasks.update_custom_stocks_data')
def update_custom_stocks_data(self, symbols: List[str], data_types: List[str], start_date: str = None, end_date: str = None):
    """自定义批量更新股票数据"""
    task_id = self.request.id
    logger.info(f"🔄 开始自定义更新 - 任务ID: {task_id}: {len(symbols)} 只股票, 数据类型: {data_types}")

    try:
        # 设置默认日期
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        async def update_data():
            return await service_client.call_service(
                "data_service",
                "/api/admin/batch-update",
                "POST",
                {
                    "symbols": symbols,
                    "data_types": data_types,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )

        result = run_async_task(update_data())

        logger.info(f"✅ 自定义更新完成: {result.get('message', 'Unknown')}")

        return {
            "task_id": task_id,
            "status": "completed",
            "symbols_count": len(symbols),
            "data_types": data_types,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 自定义更新失败: {e}")
        raise
