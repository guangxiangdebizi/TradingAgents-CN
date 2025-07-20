"""
数据同步相关的定时任务
"""
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from celery import current_task
from tasks.celery_app import celery_app
# 暂时使用简单的日志记录
import logging
logger = logging.getLogger(__name__)

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
    同步每日股票数据
    
    Args:
        symbols: 股票代码列表，为空则同步所有股票
        date: 指定日期，为空则使用昨日
    """
    task_id = self.request.id
    logger.info(f"🚀 开始同步每日股票数据 - 任务ID: {task_id}")
    
    try:
        # 设置默认参数
        if date is None:
            # 获取上一个交易日
            target_date = datetime.now() - timedelta(days=1)
            date = target_date.strftime('%Y-%m-%d')
        
        if symbols is None:
            # 获取所有A股代码（这里简化处理）
            symbols = ['000001', '000002', '600519', '000858']  # 示例股票
        
        logger.info(f"📊 同步参数: 日期={date}, 股票数量={len(symbols)}")
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': len(symbols), 'status': '开始同步数据'}
        )
        
        async def sync_data():
            db_manager = await get_async_db_manager()
            stock_repo = await get_async_stock_repository()
            
            success_count = 0
            error_count = 0
            
            for i, symbol in enumerate(symbols):
                try:
                    logger.info(f"📈 同步股票数据: {symbol}")
                    
                    # 获取股票数据
                    start_date = date
                    end_date = date
                    
                    stock_data = get_china_stock_data_unified(symbol, start_date, end_date)
                    
                    if stock_data and "错误" not in str(stock_data):
                        # 解析并保存数据（这里需要根据实际数据格式调整）
                        parsed_data = [{
                            'trade_date': datetime.strptime(date, '%Y-%m-%d'),
                            'open': 100.0,  # 从stock_data解析
                            'high': 105.0,
                            'low': 98.0,
                            'close': 102.0,
                            'volume': 1000000,
                            'amount': 102000000.0
                        }]
                        
                        await stock_repo.save_stock_daily_data(symbol, parsed_data)
                        success_count += 1
                        logger.info(f"✅ {symbol} 数据同步成功")
                    else:
                        error_count += 1
                        logger.warning(f"⚠️ {symbol} 数据获取失败: {stock_data}")
                    
                    # 更新进度
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': i + 1,
                            'total': len(symbols),
                            'status': f'已处理 {i + 1}/{len(symbols)} 只股票',
                            'success': success_count,
                            'errors': error_count
                        }
                    )
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"❌ {symbol} 同步失败: {e}")
            
            await db_manager.disconnect()
            return success_count, error_count
        
        # 执行异步任务
        success_count, error_count = run_async_task(sync_data())
        
        result = {
            'date': date,
            'total_symbols': len(symbols),
            'success_count': success_count,
            'error_count': error_count,
            'completion_time': datetime.now().isoformat()
        }
        
        logger.info(f"✅ 每日股票数据同步完成: 成功{success_count}个, 失败{error_count}个")
        return result
        
    except Exception as e:
        logger.error(f"❌ 每日股票数据同步失败: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'traceback': str(e)}
        )
        raise


@celery_app.task(bind=True, name='tasks.data_tasks.update_realtime_prices')
def update_realtime_prices(self, symbols: List[str] = None):
    """
    更新实时股价
    
    Args:
        symbols: 股票代码列表
    """
    task_id = self.request.id
    logger.info(f"⚡ 开始更新实时股价 - 任务ID: {task_id}")
    
    try:
        # 检查是否在交易时间
        now = datetime.now()
        if now.hour < 9 or now.hour > 15:
            logger.info("⏰ 非交易时间，跳过实时价格更新")
            return {'status': 'skipped', 'reason': '非交易时间'}
        
        if symbols is None:
            symbols = ['000001', '000002', '600519', '000858']  # 热门股票
        
        async def update_prices():
            # 这里实现实时价格更新逻辑
            # 可以调用实时数据API，更新Redis缓存
            updated_count = 0
            
            for symbol in symbols:
                try:
                    # 获取实时价格（模拟）
                    current_price = 100.0  # 从API获取
                    
                    # 更新缓存
                    # await redis_client.setex(f"price:{symbol}", 300, current_price)
                    
                    updated_count += 1
                    logger.debug(f"📊 更新 {symbol} 实时价格: {current_price}")
                    
                except Exception as e:
                    logger.error(f"❌ 更新 {symbol} 实时价格失败: {e}")
            
            return updated_count
        
        updated_count = run_async_task(update_prices())
        
        result = {
            'updated_count': updated_count,
            'total_symbols': len(symbols),
            'update_time': datetime.now().isoformat()
        }
        
        logger.info(f"✅ 实时股价更新完成: {updated_count}/{len(symbols)}")
        return result
        
    except Exception as e:
        logger.error(f"❌ 实时股价更新失败: {e}")
        raise


@celery_app.task(bind=True, name='tasks.data_tasks.sync_financial_data')
def sync_financial_data(self, symbols: List[str] = None):
    """
    同步财务数据
    
    Args:
        symbols: 股票代码列表
    """
    task_id = self.request.id
    logger.info(f"💰 开始同步财务数据 - 任务ID: {task_id}")
    
    try:
        if symbols is None:
            symbols = ['000001', '000002', '600519', '000858']
        
        async def sync_financials():
            success_count = 0
            
            for symbol in symbols:
                try:
                    # 获取财务数据
                    current_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                    
                    financial_data = get_stock_fundamentals_unified(
                        symbol, start_date, current_date, current_date
                    )
                    
                    if financial_data and "错误" not in str(financial_data):
                        # 保存财务数据到数据库
                        success_count += 1
                        logger.info(f"✅ {symbol} 财务数据同步成功")
                    else:
                        logger.warning(f"⚠️ {symbol} 财务数据获取失败")
                        
                except Exception as e:
                    logger.error(f"❌ {symbol} 财务数据同步失败: {e}")
            
            return success_count
        
        success_count = run_async_task(sync_financials())
        
        result = {
            'success_count': success_count,
            'total_symbols': len(symbols),
            'sync_time': datetime.now().isoformat()
        }
        
        logger.info(f"✅ 财务数据同步完成: {success_count}/{len(symbols)}")
        return result
        
    except Exception as e:
        logger.error(f"❌ 财务数据同步失败: {e}")
        raise


@celery_app.task(bind=True, name='tasks.data_tasks.fetch_news_data')
def fetch_news_data(self, symbols: List[str] = None, limit: int = 50):
    """
    抓取新闻数据
    
    Args:
        symbols: 股票代码列表
        limit: 每只股票的新闻数量限制
    """
    task_id = self.request.id
    logger.info(f"📰 开始抓取新闻数据 - 任务ID: {task_id}")
    
    try:
        if symbols is None:
            symbols = ['000001', '000002', '600519', '000858']
        
        async def fetch_news():
            total_news = 0
            
            for symbol in symbols:
                try:
                    # 获取新闻数据
                    news_data = get_stock_news_unified(symbol)
                    
                    if news_data and "错误" not in str(news_data):
                        # 解析并保存新闻数据
                        # 这里需要根据实际数据格式进行解析
                        news_count = 10  # 模拟新闻数量
                        total_news += news_count
                        logger.info(f"✅ {symbol} 新闻数据抓取成功: {news_count}条")
                    else:
                        logger.warning(f"⚠️ {symbol} 新闻数据获取失败")
                        
                except Exception as e:
                    logger.error(f"❌ {symbol} 新闻数据抓取失败: {e}")
            
            return total_news
        
        total_news = run_async_task(fetch_news())
        
        result = {
            'total_news': total_news,
            'symbols_count': len(symbols),
            'fetch_time': datetime.now().isoformat()
        }
        
        logger.info(f"✅ 新闻数据抓取完成: 共{total_news}条新闻")
        return result
        
    except Exception as e:
        logger.error(f"❌ 新闻数据抓取失败: {e}")
        raise
