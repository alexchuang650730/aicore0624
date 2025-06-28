#!/bin/bash

# PowerAutomation v2.0 部署脚本
# 支持开发、测试、生产环境的一键部署

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

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "依赖检查完成"
}

# 环境配置
setup_environment() {
    local env=${1:-development}
    log_info "配置 $env 环境..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            log_warning "已创建 .env 文件，请根据需要修改配置"
        else
            log_error ".env.example 文件不存在"
            exit 1
        fi
    fi
    
    # 设置环境变量
    export ENVIRONMENT=$env
    
    log_success "环境配置完成"
}

# 构建镜像
build_images() {
    log_info "构建 Docker 镜像..."
    
    docker-compose build --parallel
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    local env=${1:-development}
    log_info "启动 $env 环境服务..."
    
    if [ "$env" = "development" ]; then
        docker-compose up -d
    else
        docker-compose -f docker-compose.yml -f docker-compose.$env.yml up -d
    fi
    
    log_success "服务启动完成"
    
    # 显示服务状态
    show_status
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    docker-compose down
    
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    
    stop_services
    start_services $1
    
    log_success "服务重启完成"
}

# 显示服务状态
show_status() {
    log_info "服务状态:"
    docker-compose ps
    
    echo ""
    log_info "服务访问地址:"
    echo "  🚀 AI Core Service:      http://localhost:8080"
    echo "  🧠 Context Manager:      http://localhost:8081"
    echo "  🔍 Code Analyzer:        http://localhost:8082"
    echo "  🎯 Smart Router:         http://localhost:8083"
    echo "  🧪 Test Flow:            http://localhost:8084"
    echo "  📊 Grafana Dashboard:    http://localhost:3000 (admin/admin)"
    echo "  📈 Prometheus:           http://localhost:9090"
    echo "  🔍 Jaeger Tracing:       http://localhost:16686"
}

# 查看日志
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f $service
    fi
}

# 清理资源
cleanup() {
    log_warning "清理 Docker 资源..."
    
    docker-compose down -v --remove-orphans
    docker system prune -f
    
    log_success "清理完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    local services=("ai-core" "context-manager" "code-analyzer" "smart-router" "test-flow")
    local ports=(8080 8081 8082 8083 8084)
    
    for i in "${!services[@]}"; do
        local service=${services[$i]}
        local port=${ports[$i]}
        
        if curl -f -s http://localhost:$port/health > /dev/null; then
            log_success "$service 服务健康"
        else
            log_error "$service 服务异常"
        fi
    done
}

# 数据库迁移
migrate_database() {
    log_info "执行数据库迁移..."
    
    docker-compose exec ai-core python -m alembic upgrade head
    
    log_success "数据库迁移完成"
}

# 显示帮助信息
show_help() {
    echo "PowerAutomation v2.0 部署脚本"
    echo ""
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  dev                    启动开发环境"
    echo "  test                   启动测试环境"
    echo "  prod                   启动生产环境"
    echo "  build                  构建 Docker 镜像"
    echo "  start [env]            启动服务"
    echo "  stop                   停止服务"
    echo "  restart [env]          重启服务"
    echo "  status                 显示服务状态"
    echo "  logs [service]         查看日志"
    echo "  health                 健康检查"
    echo "  migrate                数据库迁移"
    echo "  cleanup                清理资源"
    echo "  help                   显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 dev                 # 启动开发环境"
    echo "  $0 build               # 构建镜像"
    echo "  $0 logs ai-core        # 查看 AI Core 服务日志"
    echo "  $0 health              # 执行健康检查"
}

# 主函数
main() {
    case "${1:-help}" in
        "dev")
            check_dependencies
            setup_environment "development"
            build_images
            start_services "development"
            ;;
        "test")
            check_dependencies
            setup_environment "testing"
            build_images
            start_services "testing"
            ;;
        "prod")
            check_dependencies
            setup_environment "production"
            build_images
            start_services "production"
            ;;
        "build")
            check_dependencies
            build_images
            ;;
        "start")
            check_dependencies
            start_services $2
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services $2
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs $2
            ;;
        "health")
            health_check
            ;;
        "migrate")
            migrate_database
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"

