#!/bin/bash

# Python LSP MCP 启动脚本
# 用于启动 Python Language Server Protocol MCP 组件

set -e

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPONENT_DIR="$SCRIPT_DIR"
CONFIG_FILE="$COMPONENT_DIR/config/lsp_config.json"

# 颜色输出
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

# 检查 Python 环境
check_python() {
    log_info "检查 Python 环境..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_success "Python 版本: $PYTHON_VERSION"
}

# 安装依赖
install_dependencies() {
    log_info "安装 Python LSP 依赖..."
    
    # 检查并安装 python-lsp-server
    if ! python3 -c "import pylsp" &> /dev/null; then
        log_info "安装 python-lsp-server..."
        python3 -m pip install "python-lsp-server[all]" websockets
    else
        log_success "python-lsp-server 已安装"
    fi
    
    # 检查并安装 websockets
    if ! python3 -c "import websockets" &> /dev/null; then
        log_info "安装 websockets..."
        python3 -m pip install websockets
    else
        log_success "websockets 已安装"
    fi
}

# 启动服务
start_service() {
    log_info "启动 Python LSP MCP 服务..."
    
    cd "$COMPONENT_DIR"
    
    # 设置环境变量
    export PYTHONPATH="$COMPONENT_DIR:$PYTHONPATH"
    
    # 启动服务
    if [ -f "$CONFIG_FILE" ]; then
        python3 main.py --config "$CONFIG_FILE" "$@"
    else
        python3 main.py "$@"
    fi
}

# 停止服务
stop_service() {
    log_info "停止 Python LSP MCP 服务..."
    
    # 查找并终止进程
    PIDS=$(pgrep -f "python.*main.py" || true)
    
    if [ -n "$PIDS" ]; then
        echo "$PIDS" | xargs kill -TERM
        sleep 2
        
        # 强制终止仍在运行的进程
        PIDS=$(pgrep -f "python.*main.py" || true)
        if [ -n "$PIDS" ]; then
            echo "$PIDS" | xargs kill -KILL
        fi
        
        log_success "Python LSP MCP 服务已停止"
    else
        log_warning "未找到运行中的 Python LSP MCP 服务"
    fi
}

# 检查服务状态
check_status() {
    log_info "检查 Python LSP MCP 服务状态..."
    
    PIDS=$(pgrep -f "python.*main.py" || true)
    
    if [ -n "$PIDS" ]; then
        log_success "Python LSP MCP 服务正在运行 (PID: $PIDS)"
        
        # 检查端口
        PORT=${1:-8081}
        if netstat -tuln | grep ":$PORT " > /dev/null; then
            log_success "LSP 服务端口 $PORT 正在监听"
        else
            log_warning "LSP 服务端口 $PORT 未在监听"
        fi
    else
        log_warning "Python LSP MCP 服务未运行"
    fi
}

# 重启服务
restart_service() {
    log_info "重启 Python LSP MCP 服务..."
    stop_service
    sleep 1
    start_service "$@"
}

# 显示帮助
show_help() {
    echo "Python LSP MCP 启动脚本"
    echo ""
    echo "用法: $0 {start|stop|restart|status|install|help} [选项]"
    echo ""
    echo "命令:"
    echo "  start     启动 LSP 服务"
    echo "  stop      停止 LSP 服务"
    echo "  restart   重启 LSP 服务"
    echo "  status    检查服务状态"
    echo "  install   安装依赖"
    echo "  help      显示此帮助信息"
    echo ""
    echo "选项:"
    echo "  --port PORT     指定服务端口 (默认: 8081)"
    echo "  --debug         启用调试模式"
    echo "  --config FILE   指定配置文件路径"
    echo ""
    echo "示例:"
    echo "  $0 start --port 8082 --debug"
    echo "  $0 restart --config /path/to/config.json"
}

# 主函数
main() {
    case "${1:-help}" in
        start)
            check_python
            install_dependencies
            shift
            start_service "$@"
            ;;
        stop)
            stop_service
            ;;
        restart)
            check_python
            install_dependencies
            shift
            restart_service "$@"
            ;;
        status)
            check_status "${2:-8081}"
            ;;
        install)
            check_python
            install_dependencies
            log_success "依赖安装完成"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"

