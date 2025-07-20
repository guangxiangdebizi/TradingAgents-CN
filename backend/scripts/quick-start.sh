#!/bin/bash

# TradingAgents 后端系统快速启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 检查端口是否被占用
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "端口 $1 已被占用"
        return 1
    fi
    return 0
}

# 等待服务启动
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1

    print_step "等待 $service_name 启动..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            print_message "$service_name 启动成功！"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name 启动超时"
    return 1
}

# 主函数
main() {
    echo "🚀 TradingAgents 后端系统快速启动"
    echo "========================================"
    
    # 检查必要的命令
    print_step "检查系统环境..."
    check_command "docker"
    check_command "docker-compose"
    check_command "curl"
    
    # 检查是否在正确的目录
    if [ ! -f "docker-compose.yml" ]; then
        print_error "请在 backend 目录下运行此脚本"
        exit 1
    fi
    
    # 检查环境变量文件
    if [ ! -f ".env" ]; then
        print_warning ".env 文件不存在，正在创建..."
        cp .env.example .env
        print_message "已创建 .env 文件，请编辑配置后重新运行"
        print_message "主要需要配置的API密钥："
        echo "  - DASHSCOPE_API_KEY"
        echo "  - TUSHARE_TOKEN"
        echo "  - DEEPSEEK_API_KEY (可选)"
        exit 1
    fi
    
    # 检查关键端口
    print_step "检查端口占用..."
    ports=(8000 8001 8002 8003 5555 27017 6379 9000 9001)
    occupied_ports=()
    
    for port in "${ports[@]}"; do
        if ! check_port $port; then
            occupied_ports+=($port)
        fi
    done
    
    if [ ${#occupied_ports[@]} -gt 0 ]; then
        print_warning "以下端口被占用: ${occupied_ports[*]}"
        read -p "是否继续启动？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_message "启动已取消"
            exit 1
        fi
    fi
    
    # 选择镜像源
    echo ""
    echo "请选择镜像源："
    echo "1) 官方镜像源 (默认，海外用户推荐)"
    echo "2) 国内镜像源 (国内用户推荐)"
    read -p "请输入选择 (1-2): " -n 1 -r
    echo ""

    CHINA_MIRROR=""
    case $REPLY in
        2)
            print_message "使用国内镜像源..."
            CHINA_MIRROR="-f docker-compose.china.yml"
            ;;
        *)
            print_message "使用官方镜像源..."
            ;;
    esac

    # 选择启动模式
    echo ""
    echo "请选择启动模式："
    echo "1) 生产模式 (默认)"
    echo "2) 开发模式 (支持热重载)"
    echo "3) 开发模式 + 管理工具"
    read -p "请输入选择 (1-3): " -n 1 -r
    echo ""

    case $REPLY in
        2)
            print_message "启动开发模式..."
            COMPOSE_CMD="docker-compose -f docker-compose.yml $CHINA_MIRROR -f docker-compose.dev.yml"
            ;;
        3)
            print_message "启动开发模式 + 管理工具..."
            COMPOSE_CMD="docker-compose -f docker-compose.yml $CHINA_MIRROR -f docker-compose.dev.yml --profile dev-tools"
            ;;
        *)
            print_message "启动生产模式..."
            COMPOSE_CMD="docker-compose -f docker-compose.yml $CHINA_MIRROR"
            ;;
    esac
    
    # 停止现有服务
    print_step "停止现有服务..."
    $COMPOSE_CMD down > /dev/null 2>&1 || true
    
    # 拉取最新镜像
    print_step "拉取Docker镜像（使用国内镜像源）..."
    print_message "正在从阿里云镜像源拉取镜像，请稍候..."
    $COMPOSE_CMD pull
    
    # 构建服务
    print_step "构建服务镜像..."
    $COMPOSE_CMD build
    
    # 启动服务
    print_step "启动服务..."
    $COMPOSE_CMD up -d
    
    # 等待服务启动
    print_step "等待服务启动完成..."
    sleep 10
    
    # 检查服务状态
    print_step "检查服务状态..."
    
    services=(
        "http://localhost:27017|MongoDB"
        "http://localhost:6379|Redis"
        "http://localhost:8000/health|API Gateway"
        "http://localhost:8001/health|Analysis Engine"
        "http://localhost:8002/health|Data Service"
        "http://localhost:8003/health|Task API"
        "http://localhost:5555|Flower"
    )
    
    failed_services=()
    
    for service in "${services[@]}"; do
        IFS='|' read -r url name <<< "$service"
        if ! wait_for_service "$url" "$name"; then
            failed_services+=("$name")
        fi
    done
    
    echo ""
    echo "========================================"
    
    if [ ${#failed_services[@]} -eq 0 ]; then
        print_message "🎉 所有服务启动成功！"
        
        echo ""
        echo "📊 服务访问地址："
        echo "  API Gateway:     http://localhost:8000"
        echo "  API 文档:        http://localhost:8000/docs"
        echo "  Analysis Engine: http://localhost:8001"
        echo "  Data Service:    http://localhost:8002"
        echo "  Task API:        http://localhost:8003"
        echo "  Flower 监控:     http://localhost:5555"
        echo "  MinIO 控制台:    http://localhost:9001"
        
        if [[ $REPLY == "3" ]]; then
            echo "  MongoDB 管理:    http://localhost:8081"
            echo "  Redis 管理:      http://localhost:8082"
        fi
        
        echo ""
        echo "🔧 常用命令："
        echo "  查看日志: docker-compose logs -f"
        echo "  停止服务: docker-compose down"
        echo "  重启服务: docker-compose restart"
        echo "  查看状态: docker-compose ps"
        
        echo ""
        echo "🧪 快速测试："
        echo "  健康检查: curl http://localhost:8000/health"
        echo "  股票信息: curl http://localhost:8000/api/stock/info/000858"
        echo "  运行测试: python scripts/test-api.py"
        
    else
        print_error "以下服务启动失败: ${failed_services[*]}"
        echo ""
        echo "🔍 故障排查："
        echo "  查看日志: docker-compose logs service-name"
        echo "  查看状态: docker-compose ps"
        echo "  重启服务: docker-compose restart service-name"
    fi
    
    echo ""
    echo "📚 更多信息请查看: GETTING_STARTED.md"
}

# 捕获中断信号
trap 'print_warning "启动已中断"; exit 1' INT

# 运行主函数
main "$@"
