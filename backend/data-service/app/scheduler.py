#!/usr/bin/env python3
"""
数据定时调度器
负责定时更新历史数据、清理过期数据、数据预热等任务
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from .data_manager import DataManager, DataType

logger = logging.getLogger(__name__)

class DataScheduler:
    """数据定时调度器"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
        # 热门股票列表（用于数据预热）
        self.hot_stocks = {
            "A股": ["000858", "000001", "000002", "600036", "600519", "000725"],
            "美股": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"],
            "港股": ["00700", "09988", "03690", "00941", "02318", "01024"]
        }
    
    def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("⚠️ 调度器已在运行")
            return
        
        try:
            # 添加定时任务
            self._add_scheduled_jobs()
            
            # 启动调度器
            self.scheduler.start()
            self.is_running = True
            
            logger.info("🚀 数据调度器启动成功")
            
        except Exception as e:
            logger.error(f"❌ 数据调度器启动失败: {e}")
    
    def stop(self):
        """停止调度器"""
        if not self.is_running:
            return
        
        try:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("⏹️ 数据调度器已停止")
        except Exception as e:
            logger.error(f"❌ 数据调度器停止失败: {e}")
    
    def _add_scheduled_jobs(self):
        """添加定时任务"""
        
        # 1. 每15分钟更新热门股票的实时数据
        self.scheduler.add_job(
            self._update_hot_stocks_data,
            trigger=IntervalTrigger(minutes=15),
            id="update_hot_stocks",
            name="更新热门股票数据",
            max_instances=1
        )
        
        # 2. 每小时清理过期数据
        self.scheduler.add_job(
            self._cleanup_expired_data,
            trigger=IntervalTrigger(hours=1),
            id="cleanup_expired",
            name="清理过期数据",
            max_instances=1
        )
        
        # 3. 每天凌晨2点更新历史数据
        self.scheduler.add_job(
            self._update_historical_data,
            trigger=CronTrigger(hour=2, minute=0),
            id="update_historical",
            name="更新历史数据",
            max_instances=1
        )
        
        # 4. 每天早上8点预热数据
        self.scheduler.add_job(
            self._preheat_data,
            trigger=CronTrigger(hour=8, minute=0),
            id="preheat_data",
            name="数据预热",
            max_instances=1
        )
        
        # 5. 每30分钟更新新闻数据
        self.scheduler.add_job(
            self._update_news_data,
            trigger=IntervalTrigger(minutes=30),
            id="update_news",
            name="更新新闻数据",
            max_instances=1
        )
        
        # 6. 每6小时更新基本面数据
        self.scheduler.add_job(
            self._update_fundamentals_data,
            trigger=IntervalTrigger(hours=6),
            id="update_fundamentals",
            name="更新基本面数据",
            max_instances=1
        )
        
        # 7. 每天晚上11点生成数据统计报告
        self.scheduler.add_job(
            self._generate_data_report,
            trigger=CronTrigger(hour=23, minute=0),
            id="generate_report",
            name="生成数据报告",
            max_instances=1
        )
        
        logger.info("✅ 定时任务添加完成")
    
    async def _update_hot_stocks_data(self):
        """更新热门股票数据"""
        try:
            logger.info("📊 开始更新热门股票数据")
            
            total_updated = 0
            for market, symbols in self.hot_stocks.items():
                for symbol in symbols:
                    try:
                        # 更新股票数据
                        end_date = datetime.now().strftime("%Y-%m-%d")
                        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                        
                        success, _ = await self.data_manager.get_data(
                            symbol=symbol,
                            data_type=DataType.STOCK_DATA,
                            start_date=start_date,
                            end_date=end_date
                        )
                        
                        if success:
                            total_updated += 1
                            
                        # 避免请求过于频繁
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        logger.warning(f"⚠️ 更新股票数据失败: {symbol} - {e}")
            
            logger.info(f"✅ 热门股票数据更新完成: {total_updated} 只股票")
            
        except Exception as e:
            logger.error(f"❌ 更新热门股票数据失败: {e}")
    
    async def _cleanup_expired_data(self):
        """清理过期数据"""
        try:
            logger.info("🧹 开始清理过期数据")
            await self.data_manager.cleanup_expired_data()
            logger.info("✅ 过期数据清理完成")
        except Exception as e:
            logger.error(f"❌ 清理过期数据失败: {e}")
    
    async def _update_historical_data(self):
        """更新历史数据"""
        try:
            logger.info("📈 开始更新历史数据")
            
            # 更新过去30天的数据
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            total_updated = 0
            for market, symbols in self.hot_stocks.items():
                for symbol in symbols:
                    try:
                        # 更新股票信息
                        success, _ = await self.data_manager.get_data(
                            symbol=symbol,
                            data_type=DataType.STOCK_INFO
                        )
                        if success:
                            total_updated += 1
                        
                        # 更新历史价格数据
                        success, _ = await self.data_manager.get_data(
                            symbol=symbol,
                            data_type=DataType.STOCK_DATA,
                            start_date=start_date,
                            end_date=end_date
                        )
                        if success:
                            total_updated += 1
                        
                        await asyncio.sleep(2)  # 避免请求过于频繁
                        
                    except Exception as e:
                        logger.warning(f"⚠️ 更新历史数据失败: {symbol} - {e}")
            
            logger.info(f"✅ 历史数据更新完成: {total_updated} 个数据集")
            
        except Exception as e:
            logger.error(f"❌ 更新历史数据失败: {e}")
    
    async def _preheat_data(self):
        """数据预热 - 提前加载常用数据到缓存"""
        try:
            logger.info("🔥 开始数据预热")
            
            total_preheated = 0
            for market, symbols in self.hot_stocks.items():
                for symbol in symbols[:3]:  # 每个市场预热前3只股票
                    try:
                        # 预热股票信息
                        success, _ = await self.data_manager.get_data(
                            symbol=symbol,
                            data_type=DataType.STOCK_INFO
                        )
                        if success:
                            total_preheated += 1
                        
                        # 预热最近数据
                        end_date = datetime.now().strftime("%Y-%m-%d")
                        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                        
                        success, _ = await self.data_manager.get_data(
                            symbol=symbol,
                            data_type=DataType.STOCK_DATA,
                            start_date=start_date,
                            end_date=end_date
                        )
                        if success:
                            total_preheated += 1
                        
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        logger.warning(f"⚠️ 数据预热失败: {symbol} - {e}")
            
            logger.info(f"✅ 数据预热完成: {total_preheated} 个数据集")
            
        except Exception as e:
            logger.error(f"❌ 数据预热失败: {e}")
    
    async def _update_news_data(self):
        """更新新闻数据"""
        try:
            logger.info("📰 开始更新新闻数据")
            
            total_updated = 0
            # 只更新美股新闻（新闻API主要支持美股）
            for symbol in self.hot_stocks["美股"][:3]:
                try:
                    success, _ = await self.data_manager.get_data(
                        symbol=symbol,
                        data_type=DataType.NEWS,
                        curr_date=datetime.now().strftime("%Y-%m-%d"),
                        hours_back=24
                    )
                    
                    if success:
                        total_updated += 1
                    
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"⚠️ 更新新闻数据失败: {symbol} - {e}")
            
            logger.info(f"✅ 新闻数据更新完成: {total_updated} 只股票")
            
        except Exception as e:
            logger.error(f"❌ 更新新闻数据失败: {e}")
    
    async def _update_fundamentals_data(self):
        """更新基本面数据"""
        try:
            logger.info("📊 开始更新基本面数据")
            
            total_updated = 0
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            
            # 主要更新A股基本面数据
            for symbol in self.hot_stocks["A股"][:3]:
                try:
                    success, _ = await self.data_manager.get_data(
                        symbol=symbol,
                        data_type=DataType.FUNDAMENTALS,
                        start_date=start_date,
                        end_date=end_date,
                        curr_date=end_date
                    )
                    
                    if success:
                        total_updated += 1
                    
                    await asyncio.sleep(3)
                    
                except Exception as e:
                    logger.warning(f"⚠️ 更新基本面数据失败: {symbol} - {e}")
            
            logger.info(f"✅ 基本面数据更新完成: {total_updated} 只股票")
            
        except Exception as e:
            logger.error(f"❌ 更新基本面数据失败: {e}")
    
    async def _generate_data_report(self):
        """生成数据统计报告"""
        try:
            logger.info("📋 开始生成数据报告")
            
            stats = await self.data_manager.get_data_statistics()
            
            # 记录统计信息
            logger.info("📊 数据统计报告:")
            for key, value in stats.items():
                logger.info(f"   {key}: {value}")
            
            # 保存到数据库
            self.data_manager.db.data_reports.insert_one({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "timestamp": datetime.now(),
                "statistics": stats
            })
            
            logger.info("✅ 数据报告生成完成")
            
        except Exception as e:
            logger.error(f"❌ 生成数据报告失败: {e}")
    
    def get_job_status(self) -> List[Dict[str, Any]]:
        """获取任务状态"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs
    
    async def run_job_manually(self, job_id: str) -> bool:
        """手动运行任务"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                self.scheduler.modify_job(job_id, next_run_time=datetime.now())
                logger.info(f"✅ 手动触发任务: {job_id}")
                return True
            else:
                logger.warning(f"⚠️ 任务不存在: {job_id}")
                return False
        except Exception as e:
            logger.error(f"❌ 手动运行任务失败: {job_id} - {e}")
            return False


# 全局调度器实例
scheduler: Optional[DataScheduler] = None

def get_scheduler() -> DataScheduler:
    """获取调度器实例"""
    global scheduler
    if scheduler is None:
        raise RuntimeError("调度器未初始化")
    return scheduler

def init_scheduler(data_manager: DataManager):
    """初始化调度器"""
    global scheduler
    scheduler = DataScheduler(data_manager)
    logger.info("✅ 数据调度器初始化完成")
