#!/bin/bash
# Backend Trading CLI Client 启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查Python版本
check_python() {
    print_info "检查Python版本..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3未安装，请先安装Python 3.8+"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    required_version="3.8"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        print_error "Python版本过低: $python_version，需要3.8+"
        exit 1
    fi
    
    print_success "Python版本: $python_version"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖包..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt文件不存在"
        exit 1
    fi
    
    # 检查是否在虚拟环境中
    if [ -z "$VIRTUAL_ENV" ]; then
        print_warning "建议在虚拟环境中运行"
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "虚拟环境: $VIRTUAL_ENV"
    fi
    
    # 安装依赖
    print_info "安装依赖包..."
    pip install -r requirements.txt
    print_success "依赖包安装完成"
}

# 检查Backend服务
check_backend() {
    print_info "检查Backend服务连接..."
    
    backend_url=${TRADING_CLI_BACKEND_URL:-"http://localhost:8000"}
    
    if curl -s "$backend_url/health" > /dev/null 2>&1; then
        print_success "Backend服务连接正常: $backend_url"
    else
        print_warning "Backend服务连接失败: $backend_url"
        print_info "请确保Backend服务已启动，或设置正确的TRADING_CLI_BACKEND_URL环境变量"
    fi
}

# 创建配置文件
create_config() {
    config_file="$HOME/.trading_cli_config.json"
    
    if [ ! -f "$config_file" ]; then
        print_info "创建默认配置文件..."
        
        cat > "$config_file" << EOF
{
  "backend_url": "http://localhost:8000",
  "default_analysis_type": "comprehensive",
  "auto_refresh": true,
  "refresh_interval": 2,
  "max_wait_time": 300,
  "max_debate_rounds": 3,
  "max_risk_rounds": 2,
  "show_progress": true,
  "color_output": true,
  "save_history": true,
  "log_level": "INFO"
}
EOF
        print_success "配置文件已创建: $config_file"
    else
        print_success "配置文件已存在: $config_file"
    fi
}

# 显示帮助信息
show_help() {
    echo "Backend Trading CLI Client 启动脚本"
    echo ""
    echo "用法: $0 [选项] [参数]"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示帮助信息"
    echo "  -c, --check             只检查环境，不启动CLI"
    echo "  -i, --install           安装依赖包"
    echo "  -s, --symbol SYMBOL     直接分析指定股票"
    echo "  -u, --url URL           指定Backend服务URL"
    echo "  --setup                 完整环境设置"
    echo ""
    echo "环境变量:"
    echo "  TRADING_CLI_BACKEND_URL Backend服务URL"
    echo "  TRADING_CLI_LOG_LEVEL   日志级别"
    echo ""
    echo "示例:"
    echo "  $0                      启动交互模式"
    echo "  $0 -s 000001           直接分析平安银行"
    echo "  $0 -u http://remote:8000 指定远程API Gateway"
    echo "  $0 --setup             完整环境设置"
}

# 主函数
main() {
    local check_only=false
    local install_only=false
    local setup_mode=false
    local symbol=""
    local backend_url=""
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -c|--check)
                check_only=true
                shift
                ;;
            -i|--install)
                install_only=true
                shift
                ;;
            -s|--symbol)
                symbol="$2"
                shift 2
                ;;
            -u|--url)
                backend_url="$2"
                shift 2
                ;;
            --setup)
                setup_mode=true
                shift
                ;;
            *)
                print_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_info "Backend Trading CLI Client 启动中..."
    
    # 检查环境
    check_python
    
    if [ "$install_only" = true ] || [ "$setup_mode" = true ]; then
        check_dependencies
    fi
    
    if [ "$setup_mode" = true ]; then
        create_config
        check_backend
        print_success "环境设置完成!"
        exit 0
    fi
    
    if [ "$check_only" = true ]; then
        check_backend
        print_success "环境检查完成!"
        exit 0
    fi
    
    if [ "$install_only" = true ]; then
        print_success "依赖安装完成!"
        exit 0
    fi
    
    # 设置环境变量
    if [ -n "$backend_url" ]; then
        export TRADING_CLI_BACKEND_URL="$backend_url"
    fi
    
    # 检查Backend连接
    check_backend
    
    # 启动CLI
    print_info "启动TradingAgents CLI..."

    if [ -n "$symbol" ]; then
        print_info "直接分析模式: $symbol"
        # 注意：新的CLI不支持直接分析模式，会进入交互模式
        print_info "使用标准Python模块启动方式..."
        python3 -m app
    else
        print_info "交互模式"
        print_info "使用标准Python模块启动方式..."
        python3 -m app
    fi
}

# 错误处理
trap 'print_error "脚本执行失败"; exit 1' ERR

# 执行主函数
main "$@"
