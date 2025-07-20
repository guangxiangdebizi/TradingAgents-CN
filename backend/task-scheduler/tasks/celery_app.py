"""
Celery 应用配置
"""
import os
from celery import Celery
from celery.schedules import crontab

# 创建 Celery 应用
celery_app = Celery('tradingagents')

# 配置 Celery
celery_app.conf.update(
    # Broker 配置
    broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2'),
    
    # 任务配置
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    
    # Worker 配置
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # 结果过期时间
    result_expires=3600,
    
    # 任务路由
    task_routes={
        'tasks.data_tasks.*': {'queue': 'data'},
        'tasks.analysis_tasks.*': {'queue': 'analysis'},
        'tasks.maintenance_tasks.*': {'queue': 'maintenance'},
    },
    
    # 定时任务配置
    beat_schedule={
        # ==================== 数据同步任务 ====================
        
        # 每日股票数据拉取（交易日收盘后）
        'sync-daily-stock-data': {
            'task': 'tasks.data_tasks.sync_daily_stock_data',
            'schedule': crontab(hour=16, minute=30),  # 16:30
            'options': {'queue': 'data'}
        },
        
        # 实时价格更新（交易时间）
        'update-realtime-prices': {
            'task': 'tasks.data_tasks.update_realtime_prices',
            'schedule': crontab(minute='*/5'),  # 每5分钟
            'options': {'queue': 'data'}
        },
        
        # 财务数据同步（每周一）
        'sync-financial-data': {
            'task': 'tasks.data_tasks.sync_financial_data',
            'schedule': crontab(hour=2, minute=0, day_of_week=1),  # 周一 02:00
            'options': {'queue': 'data'}
        },
        
        # 新闻数据抓取（每小时）
        'fetch-news-data': {
            'task': 'tasks.data_tasks.fetch_news_data',
            'schedule': crontab(minute=0),  # 每小时整点
            'options': {'queue': 'data'}
        },
        
        # ==================== 分析任务 ====================
        
        # 技术指标计算（每日收盘后）
        'calculate-technical-indicators': {
            'task': 'tasks.analysis_tasks.calculate_technical_indicators',
            'schedule': crontab(hour=17, minute=0),  # 17:00
            'options': {'queue': 'analysis'}
        },
        
        # 市场情绪分析（每日）
        'analyze-market-sentiment': {
            'task': 'tasks.analysis_tasks.analyze_market_sentiment',
            'schedule': crontab(hour=18, minute=0),  # 18:00
            'options': {'queue': 'analysis'}
        },
        
        # 风险评估更新（每周日）
        'update-risk-assessment': {
            'task': 'tasks.analysis_tasks.update_risk_assessment',
            'schedule': crontab(hour=3, minute=0, day_of_week=0),  # 周日 03:00
            'options': {'queue': 'analysis'}
        },
        
        # 热门股票分析（每日）
        'analyze-trending-stocks': {
            'task': 'tasks.analysis_tasks.analyze_trending_stocks',
            'schedule': crontab(hour=19, minute=0),  # 19:00
            'options': {'queue': 'analysis'}
        },
        
        # ==================== 维护任务 ====================
        
        # 数据清理（每周日凌晨）
        'cleanup-old-data': {
            'task': 'tasks.maintenance_tasks.cleanup_old_data',
            'schedule': crontab(hour=1, minute=0, day_of_week=0),  # 周日 01:00
            'options': {'queue': 'maintenance'}
        },
        
        # 缓存刷新（每小时）
        'refresh-cache': {
            'task': 'tasks.maintenance_tasks.refresh_cache',
            'schedule': crontab(minute=30),  # 每小时30分
            'options': {'queue': 'maintenance'}
        },
        
        # 日志归档（每日凌晨）
        'archive-logs': {
            'task': 'tasks.maintenance_tasks.archive_logs',
            'schedule': crontab(hour=0, minute=30),  # 00:30
            'options': {'queue': 'maintenance'}
        },
        
        # 数据库备份（每日凌晨）
        'backup-database': {
            'task': 'tasks.maintenance_tasks.backup_database',
            'schedule': crontab(hour=2, minute=0),  # 02:00
            'options': {'queue': 'maintenance'}
        },
        
        # 健康检查（每10分钟）
        'health-check': {
            'task': 'tasks.maintenance_tasks.health_check',
            'schedule': crontab(minute='*/10'),  # 每10分钟
            'options': {'queue': 'maintenance'}
        },
        
        # ==================== 报告任务 ====================
        
        # 每日市场报告（交易日晚上）
        'generate-daily-market-report': {
            'task': 'tasks.report_tasks.generate_daily_market_report',
            'schedule': crontab(hour=20, minute=0),  # 20:00
            'options': {'queue': 'analysis'}
        },
        
        # 每周投资组合报告（周日）
        'generate-weekly-portfolio-report': {
            'task': 'tasks.report_tasks.generate_weekly_portfolio_report',
            'schedule': crontab(hour=21, minute=0, day_of_week=0),  # 周日 21:00
            'options': {'queue': 'analysis'}
        },
    }
)

# 自动发现任务
celery_app.autodiscover_tasks([
    'tasks.data_tasks',
    'tasks.analysis_tasks', 
    'tasks.maintenance_tasks',
    'tasks.report_tasks'
])

# 任务失败重试配置
celery_app.conf.task_annotations = {
    '*': {
        'rate_limit': '10/s',
        'time_limit': 30 * 60,  # 30分钟超时
        'soft_time_limit': 25 * 60,  # 25分钟软超时
    },
    'tasks.data_tasks.*': {
        'rate_limit': '5/s',
        'retry_kwargs': {'max_retries': 3, 'countdown': 60},
    },
    'tasks.analysis_tasks.*': {
        'rate_limit': '2/s',
        'retry_kwargs': {'max_retries': 2, 'countdown': 300},
    }
}

if __name__ == '__main__':
    celery_app.start()
