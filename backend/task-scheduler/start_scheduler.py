#!/usr/bin/env python3
"""
启动 Celery Beat 调度器
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
    """启动 Celery Beat 调度器"""
    logger.info("🚀 启动 TradingAgents 任务调度器...")
    
    # 检查环境变量
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
    
    logger.info(f"📡 Broker URL: {broker_url}")
    logger.info(f"💾 Result Backend: {result_backend}")
    
    # 启动 Celery Beat
    try:
        import subprocess
        import sys

        # 使用当前Python环境的celery命令 (Celery 5.0+ 语法)
        celery_cmd = [
            sys.executable, '-m', 'celery',
            '--app=tasks.celery_app:celery_app',
            'beat',
            '--loglevel=info',
            '--schedule=./celerybeat-schedule',
            '--pidfile=./celerybeat.pid'
        ]

        logger.info(f"🚀 执行命令: {' '.join(celery_cmd)}")
        subprocess.run(celery_cmd, check=True)

    except KeyboardInterrupt:
        logger.info("⏹️ 调度器已停止")
    except Exception as e:
        logger.error(f"❌ 调度器启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
