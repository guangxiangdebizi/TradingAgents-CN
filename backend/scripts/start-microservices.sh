#!/bin/bash
"""
启动 TradingAgents 微服务架构
"""

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 和 Docker Compose
check_dependencies() {
    log_info "检查依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p logs
    mkdir -p data/mongodb
    mkdir -p data/redis
    mkdir -p data/celery
    
    log_success "目录创建完成"
}

# 启动基础设施服务
start_infrastructure() {
    log_info "启动基础设施服务 (Redis, MongoDB)..."
    
    docker-compose -f docker-compose.microservices.yml up -d redis mongodb
    
    # 等待服务启动
    log_info "等待基础设施服务启动..."
    sleep 10
    
    # 检查服务状态
    if docker-compose -f docker-compose.microservices.yml ps redis | grep -q "Up"; then
        log_success "Redis 启动成功"
    else
        log_error "Redis 启动失败"
        exit 1
    fi
    
    if docker-compose -f docker-compose.microservices.yml ps mongodb | grep -q "Up"; then
        log_success "MongoDB 启动成功"
    else
        log_error "MongoDB 启动失败"
        exit 1
    fi
}

# 启动微服务
start_microservices() {
    log_info "启动微服务..."
    
    # 启动数据服务
    log_info "启动 Data Service..."
    docker-compose -f docker-compose.microservices.yml up -d data-service
    sleep 5
    
    # 启动分析引擎
    log_info "启动 Analysis Engine..."
    docker-compose -f docker-compose.microservices.yml up -d analysis-engine
    sleep 5
    
    # 启动任务调度器
    log_info "启动 Task Scheduler..."
    docker-compose -f docker-compose.microservices.yml up -d task-scheduler
    sleep 5
    
    # 启动 API 网关
    log_info "启动 API Gateway..."
    docker-compose -f docker-compose.microservices.yml up -d api-gateway
    sleep 5
    
    log_success "微服务启动完成"
}

# 启动 Celery 服务
start_celery() {
    log_info "启动 Celery 服务..."
    
    # 启动 Celery Worker
    log_info "启动 Celery Worker..."
    docker-compose -f docker-compose.microservices.yml up -d celery-worker
    sleep 3
    
    # 启动 Celery Beat
    log_info "启动 Celery Beat..."
    docker-compose -f docker-compose.microservices.yml up -d celery-beat
    sleep 3
    
    log_success "Celery 服务启动完成"
}

# 启动监控服务
start_monitoring() {
    log_info "启动监控服务..."
    
    docker-compose -f docker-compose.microservices.yml up -d flower
    
    log_success "监控服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    echo ""
    echo "=== 服务状态 ==="
    docker-compose -f docker-compose.microservices.yml ps
    
    echo ""
    echo "=== 服务访问地址 ==="
    echo "🌐 API Gateway:     http://localhost:8000"
    echo "📊 Data Service:    http://localhost:8002"
    echo "🤖 Analysis Engine: http://localhost:8001"
    echo "⏰ Task Scheduler:  http://localhost:8003"
    echo "🌸 Flower Monitor:  http://localhost:5555"
    echo "🍃 MongoDB Admin:   http://localhost:8081"
    echo "🔴 Redis Commander: http://localhost:8082"
    echo ""
    echo "=== API 文档 ==="
    echo "📚 API Gateway Docs:     http://localhost:8000/docs"
    echo "📚 Data Service Docs:    http://localhost:8002/docs"
    echo "📚 Analysis Engine Docs: http://localhost:8001/docs"
    echo "📚 Task Scheduler Docs:  http://localhost:8003/docs"
}

# 主函数
main() {
    echo "🚀 TradingAgents 微服务架构启动脚本"
    echo "======================================"
    
    check_dependencies
    create_directories
    
    log_info "开始启动微服务架构..."
    
    start_infrastructure
    start_microservices
    start_celery
    start_monitoring
    
    check_services
    
    log_success "🎉 TradingAgents 微服务架构启动完成！"
    
    echo ""
    echo "💡 提示："
    echo "   - 使用 'docker-compose -f docker-compose.microservices.yml logs -f' 查看日志"
    echo "   - 使用 'docker-compose -f docker-compose.microservices.yml down' 停止所有服务"
    echo "   - 使用 'docker-compose -f docker-compose.microservices.yml restart <service>' 重启特定服务"
}

# 处理中断信号
trap 'log_warning "脚本被中断"; exit 1' INT TERM

# 运行主函数
main "$@"
