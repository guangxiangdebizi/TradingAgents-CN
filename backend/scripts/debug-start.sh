#!/bin/bash
# TradingAgents 调试启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 TradingAgents 调试模式启动${NC}"
echo "================================"

# 检查虚拟环境
if [ ! -f "env/bin/activate" ]; then
    echo -e "${RED}❌ 虚拟环境不存在，请先创建虚拟环境${NC}"
    echo "   python -m venv env"
    echo "   source env/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# 启动 Redis（如果没有运行）
echo -e "${BLUE}🔍 检查 Redis 状态...${NC}"
if ! docker ps | grep -q redis; then
    echo -e "${BLUE}🚀 启动 Redis...${NC}"
    docker run -d --name redis -p 6379:6379 redis:alpine
    sleep 3
else
    echo -e "${GREEN}✅ Redis 已运行${NC}"
fi

# 设置环境变量
export CELERY_BROKER_URL=redis://localhost:6379/1
export CELERY_RESULT_BACKEND=redis://localhost:6379/2
export DATA_SERVICE_URL=http://localhost:8002
export ANALYSIS_ENGINE_URL=http://localhost:8001

echo ""
echo "📋 启动选项:"
echo "1. 启动 Data Service (端口 8002)"
echo "2. 启动 Task Scheduler (端口 8003)"
echo "3. 启动 Celery Worker (调试模式)"
echo "4. 启动调试测试工具"
echo "5. 启动所有服务 (推荐)"
echo ""

read -p "请选择启动选项 (1-5): " choice

case $choice in
    1)
        echo -e "${BLUE}🚀 启动 Data Service...${NC}"
        cd data-service
        source ../env/bin/activate
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
        ;;
    2)
        echo -e "${BLUE}🚀 启动 Task Scheduler...${NC}"
        cd task-scheduler
        source ../env/bin/activate
        python -m uvicorn api.main:app --host 0.0.0.0 --port 8003 --reload
        ;;
    3)
        echo -e "${BLUE}🚀 启动 Celery Worker (调试模式)...${NC}"
        cd task-scheduler
        source ../env/bin/activate
        celery -A tasks.celery_app worker --loglevel=debug --concurrency=1
        ;;
    4)
        echo -e "${BLUE}🚀 启动调试测试工具...${NC}"
        source env/bin/activate
        python debug_data_sync.py
        ;;
    5)
        echo -e "${BLUE}🚀 启动所有服务...${NC}"
        echo ""
        echo "请在不同的终端窗口中运行以下命令:"
        echo ""
        echo -e "${YELLOW}终端1 - Data Service:${NC}"
        echo "  cd backend/data-service"
        echo "  source ../env/bin/activate"
        echo "  python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload"
        echo ""
        echo -e "${YELLOW}终端2 - Task Scheduler:${NC}"
        echo "  cd backend/task-scheduler"
        echo "  source ../env/bin/activate"
        echo "  python -m uvicorn api.main:app --host 0.0.0.0 --port 8003 --reload"
        echo ""
        echo -e "${YELLOW}终端3 - Celery Worker:${NC}"
        echo "  cd backend/task-scheduler"
        echo "  source ../env/bin/activate"
        echo "  export CELERY_BROKER_URL=redis://localhost:6379/1"
        echo "  export CELERY_RESULT_BACKEND=redis://localhost:6379/2"
        echo "  celery -A tasks.celery_app worker --loglevel=debug --concurrency=1"
        echo ""
        echo -e "${YELLOW}终端4 - 调试工具:${NC}"
        echo "  cd backend"
        echo "  source env/bin/activate"
        echo "  python debug_data_sync.py"
        echo ""
        echo -e "${GREEN}💡 提示: 启动所有服务后，访问 http://localhost:8002/docs 查看 API 文档${NC}"
        ;;
    *)
        echo -e "${RED}❌ 无效选项${NC}"
        ;;
esac
