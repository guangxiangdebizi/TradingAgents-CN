#!/bin/bash

# TradingAgents 高并发系统启动脚本

set -e

echo "🚀 启动TradingAgents高并发系统"
echo "=================================="

# 检查Docker和Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 进入backend目录
cd "$(dirname "$0")/.."

echo "📁 当前目录: $(pwd)"

# 检查配置文件
if [ ! -f "docker-compose.concurrent.yml" ]; then
    echo "❌ 找不到docker-compose.concurrent.yml文件"
    exit 1
fi

if [ ! -f "nginx/nginx.conf" ]; then
    echo "❌ 找不到nginx/nginx.conf文件"
    exit 1
fi

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose -f docker-compose.concurrent.yml down --remove-orphans

# 清理旧的容器和网络
echo "🧹 清理旧资源..."
docker system prune -f

# 构建镜像
echo "🔨 构建Docker镜像..."
docker-compose -f docker-compose.concurrent.yml build --no-cache

# 启动基础服务
echo "🗄️ 启动数据库服务..."
docker-compose -f docker-compose.concurrent.yml up -d mongodb redis

# 等待数据库启动
echo "⏳ 等待数据库启动..."
sleep 30

# 检查数据库健康状态
echo "🏥 检查数据库健康状态..."
docker-compose -f docker-compose.concurrent.yml exec mongodb mongo --eval "db.adminCommand('ping')" || {
    echo "❌ MongoDB启动失败"
    exit 1
}

docker-compose -f docker-compose.concurrent.yml exec redis redis-cli ping || {
    echo "❌ Redis启动失败"
    exit 1
}

echo "✅ 数据库服务启动成功"

# 启动核心服务
echo "🔧 启动核心服务..."
docker-compose -f docker-compose.concurrent.yml up -d data-service llm-service memory-service

# 等待核心服务启动
echo "⏳ 等待核心服务启动..."
sleep 20

# 检查核心服务健康状态
echo "🏥 检查核心服务健康状态..."

# 检查Data Service
for i in {1..30}; do
    if curl -f http://localhost:8003/health &> /dev/null; then
        echo "✅ Data Service启动成功"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Data Service启动超时"
        exit 1
    fi
    sleep 2
done

# 检查LLM Service
for i in {1..30}; do
    if curl -f http://localhost:8004/health &> /dev/null; then
        echo "✅ LLM Service启动成功"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ LLM Service启动超时"
        exit 1
    fi
    sleep 2
done

# 检查Memory Service
for i in {1..30}; do
    if curl -f http://localhost:8006/health &> /dev/null; then
        echo "✅ Memory Service启动成功"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Memory Service启动超时"
        exit 1
    fi
    sleep 2
done

# 启动Analysis Engine实例
echo "🧠 启动Analysis Engine实例..."
docker-compose -f docker-compose.concurrent.yml up -d analysis-engine-1 analysis-engine-2 analysis-engine-3

# 等待Analysis Engine启动
echo "⏳ 等待Analysis Engine实例启动..."
sleep 30

# 检查Analysis Engine实例
echo "🏥 检查Analysis Engine实例健康状态..."

for instance in 8005 8015 8025; do
    for i in {1..30}; do
        if curl -f http://localhost:$instance/health &> /dev/null; then
            echo "✅ Analysis Engine (端口$instance) 启动成功"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "❌ Analysis Engine (端口$instance) 启动超时"
            exit 1
        fi
        sleep 2
    done
done

# 启动负载均衡器
echo "⚖️ 启动负载均衡器..."
docker-compose -f docker-compose.concurrent.yml up -d nginx-lb

# 等待负载均衡器启动
echo "⏳ 等待负载均衡器启动..."
sleep 10

# 检查负载均衡器
for i in {1..30}; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo "✅ 负载均衡器启动成功"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ 负载均衡器启动超时"
        exit 1
    fi
    sleep 2
done

# 启动任务调度器
echo "📅 启动任务调度器..."
docker-compose -f docker-compose.concurrent.yml up -d task-scheduler celery-worker celery-beat

# 启动监控服务
echo "📊 启动监控服务..."
docker-compose -f docker-compose.concurrent.yml up -d flower

# 等待所有服务启动
echo "⏳ 等待所有服务完全启动..."
sleep 20

# 最终健康检查
echo "🏥 执行最终健康检查..."

services=(
    "http://localhost:8000/health:负载均衡器"
    "http://localhost:8003/health:Data Service"
    "http://localhost:8004/health:LLM Service"
    "http://localhost:8006/health:Memory Service"
    "http://localhost:8005/health:Analysis Engine 1"
    "http://localhost:8015/health:Analysis Engine 2"
    "http://localhost:8025/health:Analysis Engine 3"
)

all_healthy=true
for service in "${services[@]}"; do
    url=$(echo $service | cut -d: -f1-2)
    name=$(echo $service | cut -d: -f3)
    
    if curl -f "$url" &> /dev/null; then
        echo "✅ $name: 健康"
    else
        echo "❌ $name: 不健康"
        all_healthy=false
    fi
done

if [ "$all_healthy" = true ]; then
    echo ""
    echo "🎉 TradingAgents高并发系统启动成功！"
    echo ""
    echo "📋 服务访问地址:"
    echo "   负载均衡器 (主入口): http://localhost:8000"
    echo "   Data Service: http://localhost:8003"
    echo "   LLM Service: http://localhost:8004"
    echo "   Memory Service: http://localhost:8006"
    echo "   Analysis Engine 1: http://localhost:8005"
    echo "   Analysis Engine 2: http://localhost:8015"
    echo "   Analysis Engine 3: http://localhost:8025"
    echo "   Flower监控: http://localhost:5555"
    echo ""
    echo "📊 系统统计: http://localhost:8000/api/v1/system/stats"
    echo "🏥 健康检查: http://localhost:8000/health"
    echo ""
    echo "🧪 运行性能测试:"
    echo "   cd backend && python tests/performance/test_concurrent_analysis.py"
    echo ""
    echo "📝 查看日志:"
    echo "   docker-compose -f docker-compose.concurrent.yml logs -f [service_name]"
    echo ""
    echo "🛑 停止系统:"
    echo "   docker-compose -f docker-compose.concurrent.yml down"
else
    echo ""
    echo "❌ 部分服务启动失败，请检查日志:"
    echo "   docker-compose -f docker-compose.concurrent.yml logs"
    exit 1
fi
