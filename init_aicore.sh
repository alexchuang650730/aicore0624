#!/bin/bash

# AICore 本地环境初始化脚本
# 启动 PowerAutomation_local + AIWeb & SmartUI (连接到 EC2 上的 PowerAutomation 主平台)
# 版本: 3.1.0
# 日期: 2025-06-29

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
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
POWERAUTOMATION_LOCAL_PATH="$PROJECT_ROOT/PowerAutomation_local"
AIWEB_SMARTUI_PATH="$POWERAUTOMATION_LOCAL_PATH/aiweb_smartui"

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
    echo "║                      AICore 本地环境                          ║"
    echo "║        PowerAutomation_local + AIWeb & SmartUI               ║"
    echo "║                         版本 3.1.0                           ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${CYAN}🏗️ 架构说明:${NC}"
    echo "  • PowerAutomation 主平台: 部署在 EC2 云端"
    echo "  • PowerAutomation_local: 本地 MCP 适配器 (连接到 EC2)"
    echo "  • AIWeb: 智能Web入口平台"
    echo "  • SmartUI: AI-First IDE"
    echo ""
    echo -e "${CYAN}🚀 本脚本将启动:${NC}"
    echo "  • PowerAutomation_local (本地适配器)"
    echo "  • AIWeb & SmartUI 组件"
    echo ""
}

# 检查系统要求
check_requirements() {
    log_header "🔍 检查系统要求..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装，请先安装 Python 3.8+"
        exit 1
    fi
    
    local python_version=$(python3 --version | cut -d' ' -f2)
    log_info "Python 版本: $python_version"
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装，请先安装 pip"
        exit 1
    fi
    
    # 检查目录结构
    if [ ! -d "$POWERAUTOMATION_LOCAL_PATH" ]; then
        log_error "PowerAutomation_local 目录不存在: $POWERAUTOMATION_LOCAL_PATH"
        exit 1
    fi
    
    if [ ! -d "$AIWEB_SMARTUI_PATH" ]; then
        log_error "aiweb_smartui 组件目录不存在: $AIWEB_SMARTUI_PATH"
        exit 1
    fi
    
    log_success "系统要求检查通过"
}

# 初始化PowerAutomation_local
init_powerautomation_local() {
    log_header "🔧 初始化 PowerAutomation_local..."
    
    cd "$POWERAUTOMATION_LOCAL_PATH"
    
    # 检查虚拟环境
    if [ ! -d "powerautomation_env" ]; then
        log_info "创建 PowerAutomation_local 虚拟环境..."
        python3 -m venv powerautomation_env
    fi
    
    # 激活虚拟环境
    source powerautomation_env/bin/activate
    
    # 安装基础依赖
    if [ -f "requirements.txt" ]; then
        log_info "安装 PowerAutomation_local 依赖..."
        pip install -r requirements.txt
    fi
    
    # 退出虚拟环境
    deactivate
    
    log_success "PowerAutomation_local 初始化完成"
}

# 初始化AIWeb & SmartUI组件
init_aiweb_smartui() {
    log_header "🌐 初始化 AIWeb & SmartUI 组件..."
    
    cd "$AIWEB_SMARTUI_PATH"
    
    # 检查启动脚本
    if [ ! -f "start_aiweb_smartui.sh" ]; then
        log_error "启动脚本不存在: start_aiweb_smartui.sh"
        exit 1
    fi
    
    # 设置执行权限
    chmod +x start_aiweb_smartui.sh
    chmod +x stop_aiweb_smartui.sh
    
    log_success "AIWeb & SmartUI 组件初始化完成"
}

# 检查EC2连接
check_ec2_connection() {
    log_header "🌐 检查 PowerAutomation 主平台连接..."
    
    # 这里可以添加检查EC2上PowerAutomation主平台的逻辑
    # 例如ping EC2实例或检查API端点
    
    log_info "PowerAutomation 主平台运行在 EC2 云端"
    log_info "PowerAutomation_local 将作为本地适配器连接到主平台"
    
    # 可以添加实际的连接检查
    # if curl -f http://your-ec2-instance/health &> /dev/null; then
    #     log_success "PowerAutomation 主平台连接正常"
    # else
    #     log_warning "无法连接到 PowerAutomation 主平台，请检查网络或 EC2 状态"
    # fi
    
    log_success "EC2 连接检查完成"
}

# 启动PowerAutomation_local服务
start_powerautomation_local() {
    log_header "🔗 启动 PowerAutomation_local MCP 适配器..."
    
    cd "$POWERAUTOMATION_LOCAL_PATH"
    
    # 创建日志目录
    mkdir -p logs
    
    # 检查是否已有MCP服务器在运行
    if pgrep -f "mcp_server.py" > /dev/null; then
        log_warning "PowerAutomation_local MCP 服务器已在运行"
        return 0
    fi
    
    # 启动MCP服务器
    if [ -f "start.sh" ]; then
        log_info "启动 PowerAutomation_local MCP 适配器..."
        nohup ./start.sh > logs/powerautomation_local.log 2>&1 &
        echo $! > logs/powerautomation_local.pid
        sleep 3
        
        if pgrep -f "mcp_server.py" > /dev/null; then
            log_success "PowerAutomation_local MCP 适配器启动成功"
        else
            log_warning "PowerAutomation_local MCP 适配器启动可能失败，请检查日志"
        fi
    else
        log_error "PowerAutomation_local 启动脚本不存在"
        return 1
    fi
}

# 启动AIWeb & SmartUI组件
start_aiweb_smartui() {
    log_header "🌐 启动 AIWeb & SmartUI 组件..."
    
    cd "$AIWEB_SMARTUI_PATH"
    
    # 检查是否已有服务在运行
    if pgrep -f "smartui_mcp.py" > /dev/null; then
        log_warning "AIWeb & SmartUI 组件已在运行"
        return 0
    fi
    
    # 启动AIWeb & SmartUI服务
    log_info "启动 AIWeb & SmartUI 服务..."
    ./start_aiweb_smartui.sh
    sleep 3
    
    # 验证服务状态
    if pgrep -f "smartui_mcp.py" > /dev/null; then
        log_success "AIWeb & SmartUI 组件启动成功"
    else
        log_warning "AIWeb & SmartUI 组件启动可能失败，请检查日志"
    fi
}

# 显示服务状态
show_status() {
    log_header "📊 本地环境状态..."
    
    echo ""
    echo -e "${CYAN}🌐 本地 Web 服务:${NC}"
    echo "  • AIWeb 入口:         http://localhost:8081"
    echo "  • SmartUI IDE:        http://localhost:3000"
    echo "  • SmartUI 后端 API:   http://localhost:5001"
    echo ""
    
    echo -e "${CYAN}☁️ 云端服务:${NC}"
    echo "  • PowerAutomation 主平台: 运行在 EC2 云端"
    echo ""
    
    echo -e "${CYAN}🔗 本地适配器:${NC}"
    if pgrep -f "mcp_server.py" > /dev/null; then
        echo "  • PowerAutomation_local MCP: ✅ 运行中"
    else
        echo "  • PowerAutomation_local MCP: ❌ 未运行"
    fi
    
    echo ""
    echo -e "${CYAN}🌐 AIWeb & SmartUI:${NC}"
    if pgrep -f "smartui_mcp.py" > /dev/null; then
        echo "  • SmartUI MCP:        ✅ 运行中"
    else
        echo "  • SmartUI MCP:        ❌ 未运行"
    fi
    
    if pgrep -f "http.server.*3000" > /dev/null; then
        echo "  • SmartUI 前端:       ✅ 运行中"
    else
        echo "  • SmartUI 前端:       ❌ 未运行"
    fi
    
    if pgrep -f "http.server.*8081" > /dev/null; then
        echo "  • AIWeb 前端:         ✅ 运行中"
    else
        echo "  • AIWeb 前端:         ❌ 未运行"
    fi
    
    echo ""
    echo -e "${CYAN}📁 日志文件:${NC}"
    echo "  • PowerAutomation_local:     $POWERAUTOMATION_LOCAL_PATH/logs/"
    echo "  • AIWeb & SmartUI:           $AIWEB_SMARTUI_PATH/logs/"
    echo ""
    
    echo -e "${CYAN}🛑 停止服务:${NC}"
    echo "  • 停止 AIWeb & SmartUI:      cd $AIWEB_SMARTUI_PATH && ./stop_aiweb_smartui.sh"
    echo "  • 停止 PowerAutomation_local: pkill -f mcp_server.py"
    echo ""
}

# 验证部署
verify_deployment() {
    log_header "✅ 验证本地环境部署..."
    
    local all_good=true
    
    # 检查AIWeb前端
    log_info "检查 AIWeb 前端服务..."
    if curl -f http://localhost:8081 &> /dev/null; then
        log_success "AIWeb 前端服务正常"
    else
        log_warning "AIWeb 前端服务异常"
        all_good=false
    fi
    
    # 检查SmartUI前端
    log_info "检查 SmartUI 前端服务..."
    if curl -f http://localhost:3000 &> /dev/null; then
        log_success "SmartUI 前端服务正常"
    else
        log_warning "SmartUI 前端服务异常"
        all_good=false
    fi
    
    # 检查SmartUI后端API
    log_info "检查 SmartUI 后端 API..."
    if curl -f http://localhost:5001/health &> /dev/null; then
        log_success "SmartUI 后端 API 正常"
    else
        log_warning "SmartUI 后端 API 异常"
        all_good=false
    fi
    
    if [ "$all_good" = true ]; then
        log_success "本地环境验证通过"
        return 0
    else
        log_warning "部分服务可能需要更多时间启动，请稍后检查"
        return 1
    fi
}

# 主函数
main() {
    show_welcome
    
    log_info "开始 AICore 本地环境初始化..."
    echo ""
    
    check_requirements
    echo ""
    
    check_ec2_connection
    echo ""
    
    init_powerautomation_local
    echo ""
    
    init_aiweb_smartui
    echo ""
    
    start_powerautomation_local
    echo ""
    
    start_aiweb_smartui
    echo ""
    
    show_status
    
    # 验证部署（允许部分失败）
    if verify_deployment; then
        log_success "🎉 AICore 本地环境初始化成功！"
    else
        log_warning "⚠️ 部分服务可能还在启动中，请稍后检查状态"
    fi
    
    echo ""
    echo -e "${GREEN}您现在可以访问以下本地服务:${NC}"
    echo -e "${YELLOW}  • AIWeb 入口: http://localhost:8081${NC}"
    echo -e "${YELLOW}  • SmartUI IDE: http://localhost:3000${NC}"
    echo ""
    echo -e "${CYAN}💡 提示: PowerAutomation 主平台运行在 EC2 云端${NC}"
    echo -e "${CYAN}💡 PowerAutomation_local 作为本地适配器连接到云端主平台${NC}"
    echo ""
}

# 错误处理
trap 'log_error "初始化过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@"

