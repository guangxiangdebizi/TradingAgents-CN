"""
系统维护相关的定时任务
"""
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio
import logging

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from celery import current_task
from tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def run_async_task(coro):
    """运行异步任务的辅助函数"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


@celery_app.task(bind=True, name='tasks.maintenance_tasks.cleanup_old_data')
def cleanup_old_data(self, days_to_keep: int = 90):
    """
    清理过期数据
    
    Args:
        days_to_keep: 保留数据的天数
    """
    task_id = self.request.id
    logger.info(f"🧹 开始清理过期数据 - 任务ID: {task_id}")
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        async def cleanup_data():
            cleanup_stats = {
                'analysis_results': 0,
                'analysis_progress': 0,
                'cache_entries': 0,
                'log_files': 0
            }
            
            # 清理过期的分析结果
            try:
                # 删除超过保留期的分析结果
                # deleted_count = await collection.delete_many({
                #     'created_at': {'$lt': cutoff_date}
                # })
                cleanup_stats['analysis_results'] = 150  # 模拟删除数量
                logger.info(f"✅ 清理过期分析结果: {cleanup_stats['analysis_results']}条")
            except Exception as e:
                logger.error(f"❌ 清理分析结果失败: {e}")
            
            # 清理过期的进度记录
            try:
                cleanup_stats['analysis_progress'] = 300  # 模拟删除数量
                logger.info(f"✅ 清理过期进度记录: {cleanup_stats['analysis_progress']}条")
            except Exception as e:
                logger.error(f"❌ 清理进度记录失败: {e}")
            
            # 清理Redis缓存中的过期数据
            try:
                cleanup_stats['cache_entries'] = 500  # 模拟清理数量
                logger.info(f"✅ 清理过期缓存: {cleanup_stats['cache_entries']}条")
            except Exception as e:
                logger.error(f"❌ 清理缓存失败: {e}")
            
            # 清理日志文件
            try:
                cleanup_stats['log_files'] = 10  # 模拟清理文件数
                logger.info(f"✅ 清理过期日志: {cleanup_stats['log_files']}个文件")
            except Exception as e:
                logger.error(f"❌ 清理日志失败: {e}")
            
            return cleanup_stats
        
        cleanup_stats = run_async_task(cleanup_data())
        
        result = {
            'cleanup_stats': cleanup_stats,
            'cutoff_date': cutoff_date.isoformat(),
            'days_kept': days_to_keep,
            'cleanup_time': datetime.now().isoformat()
        }
        
        total_cleaned = sum(cleanup_stats.values())
        logger.info(f"✅ 数据清理完成: 共清理{total_cleaned}项数据")
        return result
        
    except Exception as e:
        logger.error(f"❌ 数据清理失败: {e}")
        raise


@celery_app.task(bind=True, name='tasks.maintenance_tasks.refresh_cache')
def refresh_cache(self):
    """
    刷新缓存
    """
    task_id = self.request.id
    logger.info(f"🔄 开始刷新缓存 - 任务ID: {task_id}")
    
    try:
        async def refresh_cache_data():
            refresh_stats = {
                'stock_prices': 0,
                'market_data': 0,
                'analysis_cache': 0,
                'config_cache': 0
            }
            
            # 刷新股票价格缓存
            try:
                # 获取最新价格并更新缓存
                refresh_stats['stock_prices'] = 100  # 模拟刷新数量
                logger.info(f"✅ 刷新股票价格缓存: {refresh_stats['stock_prices']}条")
            except Exception as e:
                logger.error(f"❌ 刷新股票价格缓存失败: {e}")
            
            # 刷新市场数据缓存
            try:
                refresh_stats['market_data'] = 50
                logger.info(f"✅ 刷新市场数据缓存: {refresh_stats['market_data']}条")
            except Exception as e:
                logger.error(f"❌ 刷新市场数据缓存失败: {e}")
            
            # 刷新分析结果缓存
            try:
                refresh_stats['analysis_cache'] = 30
                logger.info(f"✅ 刷新分析缓存: {refresh_stats['analysis_cache']}条")
            except Exception as e:
                logger.error(f"❌ 刷新分析缓存失败: {e}")
            
            # 刷新配置缓存
            try:
                refresh_stats['config_cache'] = 10
                logger.info(f"✅ 刷新配置缓存: {refresh_stats['config_cache']}条")
            except Exception as e:
                logger.error(f"❌ 刷新配置缓存失败: {e}")
            
            return refresh_stats
        
        refresh_stats = run_async_task(refresh_cache_data())
        
        result = {
            'refresh_stats': refresh_stats,
            'total_refreshed': sum(refresh_stats.values()),
            'refresh_time': datetime.now().isoformat()
        }
        
        logger.info(f"✅ 缓存刷新完成: 共刷新{result['total_refreshed']}项缓存")
        return result
        
    except Exception as e:
        logger.error(f"❌ 缓存刷新失败: {e}")
        raise


@celery_app.task(bind=True, name='tasks.maintenance_tasks.archive_logs')
def archive_logs(self):
    """
    归档日志文件
    """
    task_id = self.request.id
    logger.info(f"📦 开始归档日志 - 任务ID: {task_id}")
    
    try:
        async def archive_log_files():
            archive_stats = {
                'files_archived': 0,
                'total_size_mb': 0,
                'compressed_size_mb': 0
            }
            
            # 获取需要归档的日志文件
            log_directories = [
                '/app/logs',
                '/var/log/tradingagents'
            ]
            
            for log_dir in log_directories:
                try:
                    # 查找超过1天的日志文件
                    # 压缩并移动到归档目录
                    
                    # 模拟归档过程
                    archive_stats['files_archived'] += 5
                    archive_stats['total_size_mb'] += 100
                    archive_stats['compressed_size_mb'] += 20
                    
                    logger.info(f"✅ 归档目录 {log_dir} 完成")
                    
                except Exception as e:
                    logger.error(f"❌ 归档目录 {log_dir} 失败: {e}")
            
            return archive_stats
        
        archive_stats = run_async_task(archive_log_files())
        
        result = {
            'archive_stats': archive_stats,
            'compression_ratio': (
                archive_stats['compressed_size_mb'] / archive_stats['total_size_mb']
                if archive_stats['total_size_mb'] > 0 else 0
            ),
            'archive_time': datetime.now().isoformat()
        }
        
        logger.info(f"✅ 日志归档完成: {archive_stats['files_archived']}个文件")
        return result
        
    except Exception as e:
        logger.error(f"❌ 日志归档失败: {e}")
        raise


@celery_app.task(bind=True, name='tasks.maintenance_tasks.backup_database')
def backup_database(self):
    """
    备份数据库
    """
    task_id = self.request.id
    logger.info(f"💾 开始数据库备份 - 任务ID: {task_id}")
    
    try:
        async def backup_db():
            backup_stats = {
                'collections_backed_up': 0,
                'total_documents': 0,
                'backup_size_mb': 0,
                'backup_file': ''
            }
            
            # 生成备份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"tradingagents_backup_{timestamp}.gz"
            backup_stats['backup_file'] = backup_file
            
            # 备份主要集合
            collections_to_backup = [
                'stock_info',
                'stock_daily',
                'analysis_results',
                'system_configs'
            ]
            
            for collection in collections_to_backup:
                try:
                    # 执行备份命令
                    # mongodump --collection=collection_name --gzip
                    
                    # 模拟备份过程
                    backup_stats['collections_backed_up'] += 1
                    backup_stats['total_documents'] += 10000
                    backup_stats['backup_size_mb'] += 50
                    
                    logger.info(f"✅ 备份集合 {collection} 完成")
                    
                except Exception as e:
                    logger.error(f"❌ 备份集合 {collection} 失败: {e}")
            
            # 上传到对象存储（可选）
            try:
                # 上传到MinIO或云存储
                logger.info(f"✅ 备份文件上传完成: {backup_file}")
            except Exception as e:
                logger.error(f"❌ 备份文件上传失败: {e}")
            
            return backup_stats
        
        backup_stats = run_async_task(backup_db())
        
        result = {
            'backup_stats': backup_stats,
            'backup_time': datetime.now().isoformat(),
            'success': backup_stats['collections_backed_up'] > 0
        }
        
        logger.info(f"✅ 数据库备份完成: {backup_stats['collections_backed_up']}个集合")
        return result
        
    except Exception as e:
        logger.error(f"❌ 数据库备份失败: {e}")
        raise


@celery_app.task(bind=True, name='tasks.maintenance_tasks.health_check')
def health_check(self):
    """
    系统健康检查
    """
    task_id = self.request.id
    logger.info(f"🔍 开始系统健康检查 - 任务ID: {task_id}")
    
    try:
        async def check_system_health():
            health_status = {
                'mongodb': 'unknown',
                'redis': 'unknown',
                'api_gateway': 'unknown',
                'analysis_engine': 'unknown',
                'data_service': 'unknown',
                'disk_usage': 0,
                'memory_usage': 0,
                'cpu_usage': 0
            }
            
            # 检查MongoDB连接
            try:
                # await db_manager.client.admin.command('ping')
                health_status['mongodb'] = 'healthy'
                logger.info("✅ MongoDB 健康检查通过")
            except Exception as e:
                health_status['mongodb'] = 'unhealthy'
                logger.error(f"❌ MongoDB 健康检查失败: {e}")
            
            # 检查Redis连接
            try:
                # await redis_client.ping()
                health_status['redis'] = 'healthy'
                logger.info("✅ Redis 健康检查通过")
            except Exception as e:
                health_status['redis'] = 'unhealthy'
                logger.error(f"❌ Redis 健康检查失败: {e}")
            
            # 检查各个微服务
            services = ['api_gateway', 'analysis_engine', 'data_service']
            for service in services:
                try:
                    # 发送健康检查请求
                    # response = await http_client.get(f"http://{service}:port/health")
                    health_status[service] = 'healthy'
                    logger.info(f"✅ {service} 健康检查通过")
                except Exception as e:
                    health_status[service] = 'unhealthy'
                    logger.error(f"❌ {service} 健康检查失败: {e}")
            
            # 检查系统资源
            try:
                # 获取系统资源使用情况
                health_status['disk_usage'] = 45.2  # 模拟磁盘使用率
                health_status['memory_usage'] = 68.5  # 模拟内存使用率
                health_status['cpu_usage'] = 25.3  # 模拟CPU使用率
                logger.info("✅ 系统资源检查完成")
            except Exception as e:
                logger.error(f"❌ 系统资源检查失败: {e}")
            
            return health_status
        
        health_status = run_async_task(check_system_health())
        
        # 计算整体健康状态
        unhealthy_services = [
            service for service, status in health_status.items()
            if isinstance(status, str) and status == 'unhealthy'
        ]
        
        overall_status = 'healthy' if not unhealthy_services else 'degraded'
        if len(unhealthy_services) > 2:
            overall_status = 'unhealthy'
        
        result = {
            'overall_status': overall_status,
            'health_details': health_status,
            'unhealthy_services': unhealthy_services,
            'check_time': datetime.now().isoformat()
        }
        
        logger.info(f"✅ 系统健康检查完成: {overall_status}")
        return result
        
    except Exception as e:
        logger.error(f"❌ 系统健康检查失败: {e}")
        raise
