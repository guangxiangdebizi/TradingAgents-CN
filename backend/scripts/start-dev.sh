#!/bin/bash

# TradingAgents Backend 开发环境启动脚本

set -e

echo "🚀 启动 TradingAgents Backend 开发环境"
echo "========================================"

# 检查是否存在 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️ 未找到 .env 文件，正在复制示例配置..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请编辑配置后重新运行"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 检查 Docker Compose 是否可用
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose 未安装"
    exit 1
fi

echo "📦 启动服务..."

# 启动服务
docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 健康检查
echo "🔍 执行健康检查..."

# 检查 API Gateway
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API Gateway (8000) - 健康"
else
    echo "❌ API Gateway (8000) - 异常"
fi

# 检查 Analysis Engine
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Analysis Engine (8001) - 健康"
else
    echo "❌ Analysis Engine (8001) - 异常"
fi

# 检查 Data Service
if curl -s http://localhost:8002/health > /dev/null; then
    echo "✅ Data Service (8002) - 健康"
else
    echo "❌ Data Service (8002) - 异常"
fi

echo ""
echo "🎉 Backend 服务启动完成！"
echo "========================================"
echo "📡 API Gateway:     http://localhost:8000"
echo "📊 API 文档:        http://localhost:8000/docs"
echo "🔍 Analysis Engine: http://localhost:8001"
echo "📈 Data Service:    http://localhost:8002"
echo ""
echo "📋 常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo ""
