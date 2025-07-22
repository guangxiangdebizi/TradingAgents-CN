#!/usr/bin/env python3
"""
启动 Celery Worker
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tasks.celery_app import celery_app

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """启动 Celery Worker"""
    logger.info("🚀 启动 TradingAgents 任务工作器...")
    
    # 检查环境变量
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
    
    logger.info(f"📡 Broker URL: {broker_url}")
    logger.info(f"💾 Result Backend: {result_backend}")
    
    # 获取队列参数
    queues = os.getenv('CELERY_QUEUES', 'data,analysis,maintenance,default')
    concurrency = int(os.getenv('CELERY_CONCURRENCY', '4'))
    
    logger.info(f"📋 处理队列: {queues}")
    logger.info(f"🔄 并发数: {concurrency}")
    
    # 启动 Celery Worker
    try:
        celery_app.start([
            'celery',
            'worker',
            '--app=tasks.celery_app:celery_app',
            f'--queues={queues}',
            f'--concurrency={concurrency}',
            '--loglevel=info',
            '--pidfile=/tmp/celeryworker.pid'
        ])
    except KeyboardInterrupt:
        logger.info("⏹️ 工作器已停止")
    except Exception as e:
        logger.error(f"❌ 工作器启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
