#!/usr/bin/env python3
"""
定时任务配置
配置 Celery Beat 的定时任务调度
"""

from celery.schedules import crontab

# Celery Beat 定时任务配置
CELERY_BEAT_SCHEDULE = {
    # 每15分钟更新热门股票数据
    'update-hot-stocks-every-15-minutes': {
        'task': 'tasks.data_tasks.update_hot_stocks_data',
        'schedule': crontab(minute='*/15'),  # 每15分钟执行一次
        'options': {
            'expires': 900,  # 15分钟后过期
        }
    },
    
    # 每小时清理过期数据
    'cleanup-expired-data-hourly': {
        'task': 'tasks.data_tasks.cleanup_expired_data',
        'schedule': crontab(minute=0),  # 每小时的0分执行
        'options': {
            'expires': 3600,  # 1小时后过期
        }
    },
    
    # 每天凌晨2点更新历史数据
    'sync-daily-data-at-2am': {
        'task': 'tasks.data_tasks.sync_daily_stock_data',
        'schedule': crontab(hour=2, minute=0),  # 每天凌晨2点执行
        'options': {
            'expires': 7200,  # 2小时后过期
        }
    },
    
    # 每天早上8点数据预热
    'preheat-cache-at-8am': {
        'task': 'tasks.data_tasks.preheat_cache',
        'schedule': crontab(hour=8, minute=0),  # 每天早上8点执行
        'options': {
            'expires': 3600,  # 1小时后过期
        }
    },
    
    # 每30分钟更新新闻数据
    'update-news-every-30-minutes': {
        'task': 'tasks.data_tasks.update_news_data',
        'schedule': crontab(minute='*/30'),  # 每30分钟执行一次
        'options': {
            'expires': 1800,  # 30分钟后过期
        }
    },
    
    # 每6小时更新基本面数据
    'update-fundamentals-every-6-hours': {
        'task': 'tasks.data_tasks.update_fundamentals_data',
        'schedule': crontab(minute=0, hour='*/6'),  # 每6小时执行一次
        'options': {
            'expires': 21600,  # 6小时后过期
        }
    },
    
    # 每天晚上11点生成数据报告
    'generate-data-report-at-11pm': {
        'task': 'tasks.data_tasks.generate_data_report',
        'schedule': crontab(hour=23, minute=0),  # 每天晚上11点执行
        'options': {
            'expires': 3600,  # 1小时后过期
        }
    },
    
    # 工作日交易时间内每5分钟更新实时数据（仅作示例，实际可能不需要）
    'update-realtime-data-trading-hours': {
        'task': 'tasks.data_tasks.update_hot_stocks_data',
        'schedule': crontab(
            minute='*/5',  # 每5分钟
            hour='9-15',   # 9点到15点
            day_of_week='1-5'  # 周一到周五
        ),
        'options': {
            'expires': 300,  # 5分钟后过期
        }
    },
    
    # 每周日凌晨3点进行深度数据清理
    'deep-cleanup-weekly': {
        'task': 'tasks.maintenance_tasks.deep_data_cleanup',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # 每周日凌晨3点
        'options': {
            'expires': 7200,  # 2小时后过期
        }
    },
    
    # 每月1号生成月度报告
    'generate-monthly-report': {
        'task': 'tasks.report_tasks.generate_monthly_report',
        'schedule': crontab(hour=1, minute=0, day_of_month=1),  # 每月1号凌晨1点
        'options': {
            'expires': 7200,  # 2小时后过期
        }
    }
}

# 时区设置
CELERY_TIMEZONE = 'Asia/Shanghai'

# 任务路由配置
CELERY_TASK_ROUTES = {
    # 数据任务路由到数据队列
    'tasks.data_tasks.*': {'queue': 'data_queue'},
    
    # 分析任务路由到分析队列
    'tasks.analysis_tasks.*': {'queue': 'analysis_queue'},
    
    # 报告任务路由到报告队列
    'tasks.report_tasks.*': {'queue': 'report_queue'},
    
    # 维护任务路由到维护队列
    'tasks.maintenance_tasks.*': {'queue': 'maintenance_queue'},
}

# 队列配置
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_QUEUES = {
    'default': {
        'exchange': 'default',
        'exchange_type': 'direct',
        'routing_key': 'default',
    },
    'data_queue': {
        'exchange': 'data',
        'exchange_type': 'direct',
        'routing_key': 'data',
    },
    'analysis_queue': {
        'exchange': 'analysis',
        'exchange_type': 'direct',
        'routing_key': 'analysis',
    },
    'report_queue': {
        'exchange': 'report',
        'exchange_type': 'direct',
        'routing_key': 'report',
    },
    'maintenance_queue': {
        'exchange': 'maintenance',
        'exchange_type': 'direct',
        'routing_key': 'maintenance',
    },
}

# 任务优先级配置
CELERY_TASK_DEFAULT_PRIORITY = 5
CELERY_TASK_PRIORITY_MAPPING = {
    # 高优先级任务
    'tasks.data_tasks.update_hot_stocks_data': 8,
    'tasks.data_tasks.preheat_cache': 8,
    
    # 中优先级任务
    'tasks.data_tasks.sync_daily_stock_data': 6,
    'tasks.data_tasks.update_news_data': 6,
    'tasks.data_tasks.update_fundamentals_data': 6,
    
    # 低优先级任务
    'tasks.data_tasks.cleanup_expired_data': 3,
    'tasks.data_tasks.generate_data_report': 3,
    'tasks.maintenance_tasks.deep_data_cleanup': 2,
    'tasks.report_tasks.generate_monthly_report': 2,
}

# 任务重试配置
CELERY_TASK_DEFAULT_RETRY_DELAY = 60  # 默认重试延迟60秒
CELERY_TASK_MAX_RETRIES = 3  # 默认最大重试3次

CELERY_TASK_RETRY_CONFIG = {
    'tasks.data_tasks.update_hot_stocks_data': {
        'max_retries': 2,
        'retry_delay': 30,
    },
    'tasks.data_tasks.sync_daily_stock_data': {
        'max_retries': 3,
        'retry_delay': 120,
    },
    'tasks.data_tasks.update_news_data': {
        'max_retries': 2,
        'retry_delay': 60,
    },
    'tasks.data_tasks.cleanup_expired_data': {
        'max_retries': 1,
        'retry_delay': 300,
    },
}

# 任务超时配置（秒）
CELERY_TASK_TIME_LIMIT = 3600  # 默认1小时超时
CELERY_TASK_SOFT_TIME_LIMIT = 3300  # 软超时55分钟

CELERY_TASK_TIME_LIMITS = {
    'tasks.data_tasks.update_hot_stocks_data': 1800,  # 30分钟
    'tasks.data_tasks.sync_daily_stock_data': 7200,   # 2小时
    'tasks.data_tasks.update_news_data': 900,         # 15分钟
    'tasks.data_tasks.update_fundamentals_data': 3600, # 1小时
    'tasks.data_tasks.cleanup_expired_data': 1800,    # 30分钟
    'tasks.data_tasks.preheat_cache': 600,            # 10分钟
    'tasks.data_tasks.generate_data_report': 1200,    # 20分钟
}

# 任务结果过期时间（秒）
CELERY_RESULT_EXPIRES = 86400  # 24小时

# 任务序列化配置
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

# 工作进程配置
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # 每个工作进程预取1个任务
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000  # 每个子进程最多处理1000个任务后重启

# 监控配置
CELERY_SEND_TASK_EVENTS = True
CELERY_SEND_EVENTS = True

# 日志配置
CELERY_WORKER_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
CELERY_WORKER_TASK_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

def get_celery_config():
    """获取 Celery 配置"""
    return {
        'beat_schedule': CELERY_BEAT_SCHEDULE,
        'timezone': CELERY_TIMEZONE,
        'task_routes': CELERY_TASK_ROUTES,
        'task_default_queue': CELERY_TASK_DEFAULT_QUEUE,
        'task_queues': CELERY_TASK_QUEUES,
        'task_default_priority': CELERY_TASK_DEFAULT_PRIORITY,
        'task_default_retry_delay': CELERY_TASK_DEFAULT_RETRY_DELAY,
        'task_max_retries': CELERY_TASK_MAX_RETRIES,
        'task_time_limit': CELERY_TASK_TIME_LIMIT,
        'task_soft_time_limit': CELERY_TASK_SOFT_TIME_LIMIT,
        'result_expires': CELERY_RESULT_EXPIRES,
        'task_serializer': CELERY_TASK_SERIALIZER,
        'result_serializer': CELERY_RESULT_SERIALIZER,
        'accept_content': CELERY_ACCEPT_CONTENT,
        'worker_prefetch_multiplier': CELERY_WORKER_PREFETCH_MULTIPLIER,
        'worker_max_tasks_per_child': CELERY_WORKER_MAX_TASKS_PER_CHILD,
        'send_task_events': CELERY_SEND_TASK_EVENTS,
        'send_events': CELERY_SEND_EVENTS,
        'worker_log_format': CELERY_WORKER_LOG_FORMAT,
        'worker_task_log_format': CELERY_WORKER_TASK_LOG_FORMAT,
    }
