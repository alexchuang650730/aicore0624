#!/bin/bash

# AIWeb + SmartUI 启动脚本
# PowerAutomation Local 组件

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
POWERAUTOMATION_LOCAL_DIR="$(dirname "$SCRIPT_DIR")"
LOGS_DIR="$SCRIPT_DIR/logs"

# 创建日志目录
mkdir -p "$LOGS_DIR"

echo "🚀 启动 AIWeb + SmartUI 服务 (PowerAutomation Local)"
echo "📁 工作目录: $SCRIPT_DIR"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# 激活虚拟环境并安装依赖
echo "📦 安装依赖..."
source "$SCRIPT_DIR/venv/bin/activate"
pip install -r "$SCRIPT_DIR/config/requirements.txt" > "$LOGS_DIR/pip_install.log" 2>&1

# 启动SmartUI后端 (MCP)
echo "📡 启动SmartUI MCP后端服务..."
cd "$SCRIPT_DIR"
nohup python3 backend/smartui_mcp.py > "$LOGS_DIR/smartui_backend.log" 2>&1 &
echo $! > "$LOGS_DIR/smartui_backend.pid"

# 启动SmartUI前端
echo "🌐 启动SmartUI前端服务..."
cd "$SCRIPT_DIR/frontend/smartui"
nohup python3 -m http.server 3000 > "$LOGS_DIR/smartui_frontend.log" 2>&1 &
echo $! > "$LOGS_DIR/smartui_frontend.pid"

# 启动AIWeb前端
echo "🌐 启动AIWeb前端服务..."
cd "$SCRIPT_DIR/frontend/aiweb"
nohup python3 -m http.server 8081 > "$LOGS_DIR/aiweb_frontend.log" 2>&1 &
echo $! > "$LOGS_DIR/aiweb_frontend.pid"

# 退出虚拟环境
deactivate

echo ""
echo "✅ 所有服务启动完成!"
echo "📍 AIWeb:    http://localhost:8081"
echo "📍 SmartUI:  http://localhost:3000"
echo "📍 后端API:  http://localhost:5001"
echo ""
echo "🔍 查看日志: tail -f $LOGS_DIR/*.log"
echo "🛑 停止服务: ./stop_aiweb_smartui.sh"

