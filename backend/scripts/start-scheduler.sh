#!/bin/bash

# TradingAgents 定时任务系统启动脚本

set -e

echo "🕐 启动 TradingAgents 定时任务系统"
echo "========================================"

# 检查环境变量
if [ -z "$CELERY_BROKER_URL" ]; then
    echo "⚠️ CELERY_BROKER_URL 未设置，使用默认值"
    export CELERY_BROKER_URL="redis://localhost:6379/1"
fi

if [ -z "$CELERY_RESULT_BACKEND" ]; then
    echo "⚠️ CELERY_RESULT_BACKEND 未设置，使用默认值"
    export CELERY_RESULT_BACKEND="redis://localhost:6379/2"
fi

# 进入任务调度目录
cd "$(dirname "$0")/../task-scheduler"

echo "📦 安装依赖..."
pip install -r requirements.txt

echo "🚀 启动服务..."

# 启动 Celery Worker（后台）
echo "🔧 启动 Celery Worker..."
celery -A tasks.celery_app worker --loglevel=info --concurrency=4 --detach

# 启动 Celery Beat（后台）
echo "⏰ 启动 Celery Beat..."
celery -A tasks.celery_app beat --loglevel=info --detach

# 启动 Flower 监控（后台）
echo "🌸 启动 Flower 监控..."
celery -A tasks.celery_app flower --port=5555 --detach

# 启动任务管理 API
echo "🌐 启动任务管理 API..."
python api/main.py &

echo ""
echo "✅ 定时任务系统启动完成！"
echo "========================================"
echo "🌸 Flower 监控:     http://localhost:5555"
echo "🌐 任务管理 API:    http://localhost:8003"
echo "📊 API 文档:        http://localhost:8003/docs"
echo ""
echo "📋 常用命令:"
echo "  查看任务状态: celery -A tasks.celery_app inspect active"
echo "  停止所有服务: pkill -f celery"
echo "  重启 Worker:  celery -A tasks.celery_app worker --loglevel=info"
echo ""

# 等待用户输入
read -p "按 Enter 键查看日志，Ctrl+C 退出..."

# 显示日志
tail -f /var/log/celery/*.log
