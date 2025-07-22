#!/bin/bash
# TradingAgents 监控环境启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}🌸 TradingAgents 监控环境启动${NC}"
echo "================================"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装，请先安装 Docker${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose 未安装，请先安装 Docker Compose${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker 检查通过${NC}"

# 启动基础设施
echo -e "${BLUE}🚀 启动基础设施服务...${NC}"
docker-compose -f docker-compose.microservices.yml up -d redis mongodb

# 等待服务启动
echo -e "${YELLOW}⏳ 等待基础设施启动...${NC}"
sleep 5

# 启动微服务
echo -e "${BLUE}🚀 启动微服务...${NC}"
docker-compose -f docker-compose.microservices.yml up -d data-service task-scheduler

# 等待微服务启动
echo -e "${YELLOW}⏳ 等待微服务启动...${NC}"
sleep 10

# 启动 Celery 服务
echo -e "${BLUE}🚀 启动 Celery 服务...${NC}"
docker-compose -f docker-compose.microservices.yml up -d celery-worker celery-beat

# 等待 Celery 启动
echo -e "${YELLOW}⏳ 等待 Celery 启动...${NC}"
sleep 5

# 启动监控服务
echo -e "${PURPLE}🌸 启动 Flower 监控...${NC}"
docker-compose -f docker-compose.microservices.yml up -d flower

# 启动数据库管理工具
echo -e "${GREEN}🍃 启动 MongoDB Express...${NC}"
docker-compose -f docker-compose.microservices.yml up -d mongo-express

echo -e "${RED}🔴 启动 Redis Commander...${NC}"
docker-compose -f docker-compose.microservices.yml up -d redis-commander

# 等待所有服务启动
echo -e "${YELLOW}⏳ 等待所有服务启动完成...${NC}"
sleep 10

# 检查服务状态
echo -e "${BLUE}📋 检查服务状态...${NC}"
docker-compose -f docker-compose.microservices.yml ps

echo ""
echo -e "${GREEN}🎉 监控环境启动完成！${NC}"
echo ""
echo -e "${YELLOW}=== 🌐 监控界面访问地址 ===${NC}"
echo -e "${PURPLE}🌸 Flower (Celery监控):    http://localhost:5555${NC}"
echo -e "${GREEN}🍃 MongoDB Express:        http://localhost:8081${NC}"
echo -e "${RED}🔴 Redis Commander:        http://localhost:8082${NC}"
echo ""
echo -e "${YELLOW}=== 📚 API 文档地址 ===${NC}"
echo -e "${BLUE}🌐 API Gateway:            http://localhost:8000/docs${NC}"
echo -e "${BLUE}📊 Data Service:           http://localhost:8002/docs${NC}"
echo -e "${BLUE}⏰ Task Scheduler:         http://localhost:8003/docs${NC}"
echo ""
echo -e "${YELLOW}=== 🔧 调试工具 ===${NC}"
echo -e "${GREEN}💡 运行调试工具: python debug_data_sync.py${NC}"
echo -e "${GREEN}💡 监控 Celery: python scripts/monitor_celery.py${NC}"
echo ""
echo -e "${GREEN}🚀 现在可以开始调试定时同步数据了！${NC}"

# 询问是否打开监控界面
read -p "是否自动打开监控界面？(y/n): " open_browser
if [[ $open_browser =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🌐 正在打开监控界面...${NC}"
    
    # 检测操作系统并打开浏览器
    if command -v xdg-open > /dev/null; then
        xdg-open http://localhost:5555 &
        xdg-open http://localhost:8081 &
        xdg-open http://localhost:8082 &
        xdg-open http://localhost:8000/docs &
    elif command -v open > /dev/null; then
        open http://localhost:5555 &
        open http://localhost:8081 &
        open http://localhost:8082 &
        open http://localhost:8000/docs &
    else
        echo -e "${YELLOW}请手动打开浏览器访问上述地址${NC}"
    fi
fi

echo ""
echo -e "${GREEN}💡 提示:${NC}"
echo "  - 使用 Flower 监控任务执行状态"
echo "  - 使用 MongoDB Express 查看数据存储"
echo "  - 使用 Redis Commander 查看缓存数据"
echo "  - 使用 API 文档测试接口功能"
echo ""
echo -e "${YELLOW}  停止所有服务: docker-compose -f docker-compose.microservices.yml down${NC}"
