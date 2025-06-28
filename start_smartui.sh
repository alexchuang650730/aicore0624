#!/bin/bash

# SmartUI 权限管理系统快速启动脚本
# 版本: 1.0.0
# 日期: 2025-06-28

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_ROOT="/home/ubuntu/aicore0624"
SMARTUI_PATH="$PROJECT_ROOT/powerautomation_web/smartui"
PERMISSION_MCP_PATH="$PROJECT_ROOT/PowerAutomation/components/smartui_permission_mcp"

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

log_header() {
    echo -e "${PURPLE}$1${NC}"
}

# 显示欢迎信息
show_welcome() {
    clear
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    SmartUI 权限管理系统                        ║"
    echo "║                      快速启动脚本                             ║"
    echo "║                                                              ║"
    echo "║  🧠 SmartUI + Claude Code SDK                                ║"
    echo "║  🔐 基于角色的权限管理                                         ║"
    echo "║  📁 完整的文件管理界面                                         ║"
    echo "║  ⚡ 200K Tokens 上下文能力                                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
}

# 检查系统要求
check_requirements() {
    log_header "🔍 检查系统要求..."
    
    # 检查 Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log_success "Python 版本: $PYTHON_VERSION"
    else
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查 Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        log_success "Node.js 版本: $NODE_VERSION"
    else
        log_error "Node.js 未安装"
        exit 1
    fi
    
    # 检查 npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        log_success "npm 版本: $NPM_VERSION"
    else
        log_error "npm 未安装"
        exit 1
    fi
    
    # 检查 Redis (可选)
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null; then
            log_success "Redis 连接正常"
        else
            log_warning "Redis 未运行，将使用无缓存模式"
        fi
    else
        log_warning "Redis 未安装，将使用无缓存模式"
    fi
    
    echo
}

# 检查项目结构
check_project_structure() {
    log_header "📁 检查项目结构..."
    
    if [ ! -d "$PROJECT_ROOT" ]; then
        log_error "项目根目录不存在: $PROJECT_ROOT"
        exit 1
    fi
    log_success "项目根目录: $PROJECT_ROOT"
    
    if [ ! -d "$SMARTUI_PATH" ]; then
        log_error "SmartUI 目录不存在: $SMARTUI_PATH"
        exit 1
    fi
    log_success "SmartUI 目录: $SMARTUI_PATH"
    
    if [ ! -d "$PERMISSION_MCP_PATH" ]; then
        log_error "权限管理 MCP 目录不存在: $PERMISSION_MCP_PATH"
        exit 1
    fi
    log_success "权限管理 MCP 目录: $PERMISSION_MCP_PATH"
    
    echo
}

# 安装依赖
install_dependencies() {
    log_header "📦 安装依赖..."
    
    # 安装 Python 依赖
    log_info "安装 Python 依赖..."
    cd "$PERMISSION_MCP_PATH"
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    else
        pip3 install flask flask-cors redis
    fi
    log_success "Python 依赖安装完成"
    
    # 安装 Node.js 依赖
    log_info "安装 Node.js 依赖..."
    cd "$SMARTUI_PATH"
    if [ ! -d "node_modules" ]; then
        npm install
    else
        log_info "Node.js 依赖已存在，跳过安装"
    fi
    log_success "Node.js 依赖安装完成"
    
    echo
}

# 配置权限管理系统
configure_permissions() {
    log_header "⚙️ 配置权限管理系统..."
    
    # 检查权限管理 MCP 配置
    if [ -f "$PERMISSION_MCP_PATH/main.py" ]; then
        log_success "权限管理 MCP 配置文件存在"
    else
        log_error "权限管理 MCP 配置文件不存在"
        exit 1
    fi
    
    # 显示 API Keys
    log_info "API Keys 配置:"
    echo -e "${CYAN}管理员:${NC} admin_qIFdydy7h_cZcop7uGNT73JRhjXQblHgWaRoDJMMz4U"
    echo -e "${CYAN}开发者:${NC} dev_WqV-Kud9zmBOv_J_BtvMDJ5ZiPzibZR77o9mv-77Phg"
    echo -e "${CYAN}用户:${NC} user_Bx5z5aQbofp1fS1bNaXF-DTFnV_6X_iu6n7-7VTxi5k"
    
    echo
}

# 启动服务
start_services() {
    log_header "🚀 启动服务..."
    
    # 创建日志目录
    mkdir -p "$PROJECT_ROOT/logs"
    
    # 启动权限管理 MCP
    log_info "启动权限管理 MCP (端口 8081)..."
    cd "$PERMISSION_MCP_PATH"
    python3 main.py > "$PROJECT_ROOT/logs/permission_mcp.log" 2>&1 &
    PERMISSION_PID=$!
    echo $PERMISSION_PID > "$PROJECT_ROOT/logs/permission_mcp.pid"
    sleep 3
    
    # 检查权限管理服务
    if curl -f http://localhost:8081/health &> /dev/null; then
        log_success "权限管理 MCP 启动成功 (PID: $PERMISSION_PID)"
    else
        log_error "权限管理 MCP 启动失败"
        exit 1
    fi
    
    # 启动 SmartUI 前端
    log_info "启动 SmartUI 前端 (端口 5173)..."
    cd "$SMARTUI_PATH"
    npm run dev > "$PROJECT_ROOT/logs/smartui_frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$PROJECT_ROOT/logs/smartui_frontend.pid"
    sleep 5
    
    log_success "SmartUI 前端启动成功 (PID: $FRONTEND_PID)"
    
    echo
}

# 验证部署
verify_deployment() {
    log_header "✅ 验证部署..."
    
    # 检查权限管理服务
    log_info "检查权限管理服务..."
    if curl -f http://localhost:8081/health &> /dev/null; then
        log_success "权限管理服务正常"
    else
        log_error "权限管理服务异常"
        return 1
    fi
    
    # 测试 API Key 验证
    log_info "测试 API Key 验证..."
    ADMIN_TEST=$(curl -s -X POST http://localhost:8081/api/auth/verify \
        -H "Content-Type: application/json" \
        -d '{"api_key": "admin_qIFdydy7h_cZcop7uGNT73JRhjXQblHgWaRoDJMMz4U"}' \
        | grep -o '"authenticated":true' || echo "")
    
    if [ -n "$ADMIN_TEST" ]; then
        log_success "管理员 API Key 验证通过"
    else
        log_error "管理员 API Key 验证失败"
        return 1
    fi
    
    # 检查前端服务
    log_info "检查前端服务..."
    if curl -f http://localhost:5173 &> /dev/null; then
        log_success "前端服务正常"
    else
        log_warning "前端服务可能还在启动中..."
    fi
    
    echo
}

# 显示访问信息
show_access_info() {
    log_header "🌐 访问信息"
    
    echo -e "${CYAN}SmartUI 前端界面:${NC}"
    echo "  http://localhost:5173"
    echo
    
    echo -e "${CYAN}权限管理 API:${NC}"
    echo "  http://localhost:8081"
    echo
    
    echo -e "${CYAN}测试账号:${NC}"
    echo -e "  ${GREEN}管理员:${NC} admin_qIFdydy7h_cZcop7uGNT73JRhjXQblHgWaRoDJMMz4U"
    echo -e "  ${BLUE}开发者:${NC} dev_WqV-Kud9zmBOv_J_BtvMDJ5ZiPzibZR77o9mv-77Phg"
    echo -e "  ${YELLOW}用户:${NC} user_Bx5z5aQbofp1fS1bNaXF-DTFnV_6X_iu6n7-7VTxi5k"
    echo
    
    echo -e "${CYAN}日志文件:${NC}"
    echo "  权限管理: $PROJECT_ROOT/logs/permission_mcp.log"
    echo "  前端服务: $PROJECT_ROOT/logs/smartui_frontend.log"
    echo
}

# 显示管理命令
show_management_commands() {
    log_header "🛠️ 管理命令"
    
    echo -e "${CYAN}停止服务:${NC}"
    echo "  ./start_smartui.sh stop"
    echo
    
    echo -e "${CYAN}重启服务:${NC}"
    echo "  ./start_smartui.sh restart"
    echo
    
    echo -e "${CYAN}查看状态:${NC}"
    echo "  ./start_smartui.sh status"
    echo
    
    echo -e "${CYAN}查看日志:${NC}"
    echo "  tail -f $PROJECT_ROOT/logs/permission_mcp.log"
    echo "  tail -f $PROJECT_ROOT/logs/smartui_frontend.log"
    echo
}

# 停止服务
stop_services() {
    log_header "🛑 停止服务..."
    
    # 停止权限管理 MCP
    if [ -f "$PROJECT_ROOT/logs/permission_mcp.pid" ]; then
        PERMISSION_PID=$(cat "$PROJECT_ROOT/logs/permission_mcp.pid")
        if kill -0 $PERMISSION_PID 2>/dev/null; then
            kill $PERMISSION_PID
            log_success "权限管理 MCP 已停止 (PID: $PERMISSION_PID)"
        fi
        rm -f "$PROJECT_ROOT/logs/permission_mcp.pid"
    fi
    
    # 停止前端服务
    if [ -f "$PROJECT_ROOT/logs/smartui_frontend.pid" ]; then
        FRONTEND_PID=$(cat "$PROJECT_ROOT/logs/smartui_frontend.pid")
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            log_success "SmartUI 前端已停止 (PID: $FRONTEND_PID)"
        fi
        rm -f "$PROJECT_ROOT/logs/smartui_frontend.pid"
    fi
    
    # 清理端口
    pkill -f "python3 main.py" 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
    
    log_success "所有服务已停止"
}

# 检查服务状态
check_status() {
    log_header "📊 服务状态"
    
    # 检查权限管理 MCP
    if [ -f "$PROJECT_ROOT/logs/permission_mcp.pid" ]; then
        PERMISSION_PID=$(cat "$PROJECT_ROOT/logs/permission_mcp.pid")
        if kill -0 $PERMISSION_PID 2>/dev/null; then
            log_success "权限管理 MCP 运行中 (PID: $PERMISSION_PID)"
        else
            log_error "权限管理 MCP 已停止"
        fi
    else
        log_error "权限管理 MCP 未运行"
    fi
    
    # 检查前端服务
    if [ -f "$PROJECT_ROOT/logs/smartui_frontend.pid" ]; then
        FRONTEND_PID=$(cat "$PROJECT_ROOT/logs/smartui_frontend.pid")
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            log_success "SmartUI 前端运行中 (PID: $FRONTEND_PID)"
        else
            log_error "SmartUI 前端已停止"
        fi
    else
        log_error "SmartUI 前端未运行"
    fi
    
    # 检查端口占用
    echo
    log_info "端口占用情况:"
    netstat -tlnp 2>/dev/null | grep -E ":(8081|5173)" || echo "  未发现相关端口占用"
}

# 主函数
main() {
    case "${1:-start}" in
        "start")
            show_welcome
            check_requirements
            check_project_structure
            install_dependencies
            configure_permissions
            start_services
            
            if verify_deployment; then
                log_success "🎉 SmartUI 权限管理系统启动成功！"
                show_access_info
                show_management_commands
            else
                log_error "部署验证失败，请检查日志"
                exit 1
            fi
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            main start
            ;;
        "status")
            check_status
            ;;
        "help"|"-h"|"--help")
            echo "SmartUI 权限管理系统启动脚本"
            echo
            echo "用法: $0 [命令]"
            echo
            echo "命令:"
            echo "  start    启动服务 (默认)"
            echo "  stop     停止服务"
            echo "  restart  重启服务"
            echo "  status   查看状态"
            echo "  help     显示帮助"
            ;;
        *)
            log_error "未知命令: $1"
            echo "使用 '$0 help' 查看帮助"
            exit 1
            ;;
    esac
}

# 信号处理
trap 'echo; log_warning "收到中断信号，正在停止服务..."; stop_services; exit 0' INT TERM

# 执行主函数
main "$@"

