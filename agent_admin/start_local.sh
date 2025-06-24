#!/bin/bash

# Agentic Agent 本地啟動腳本

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 獲取腳本目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

log_info "🚀 啟動 Agentic Agent 管理中心"
log_info "項目路徑: $PROJECT_ROOT"

# 檢查Python
if ! command -v python3 &> /dev/null; then
    log_error "Python3 未安裝，請先安裝Python3"
    exit 1
fi

# 檢查pip
if ! command -v pip3 &> /dev/null; then
    log_error "pip3 未安裝，請先安裝pip3"
    exit 1
fi

# 進入後端目錄
cd "$PROJECT_ROOT/agent_admin/backend"

# 創建必要目錄
log_info "創建必要目錄..."
mkdir -p logs temp backups

# 檢查並安裝依賴
log_info "檢查Python依賴..."
if [ -f "requirements.txt" ]; then
    log_info "安裝Python依賴..."
    pip3 install -r requirements.txt --user
    log_success "依賴安裝完成"
else
    log_warning "requirements.txt 不存在，跳過依賴安裝"
fi

# 檢查端口
PORT=${PORT:-8080}
log_info "檢查端口 $PORT 是否可用..."

if netstat -tlnp 2>/dev/null | grep ":$PORT " > /dev/null; then
    log_warning "端口 $PORT 已被佔用"
    log_info "嘗試終止佔用進程..."
    pkill -f "python.*app.py" || true
    sleep 2
fi

# 設置環境變量
export PORT=$PORT
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

log_info "啟動配置:"
log_info "  端口: $PORT"
log_info "  工作目錄: $(pwd)"
log_info "  Python路徑: $PYTHONPATH"

# 啟動服務
log_success "🎉 啟動 Agentic Agent 管理中心..."
log_info "管理界面: http://localhost:$PORT"
log_info "健康檢查: http://localhost:$PORT/api/health"
log_info "按 Ctrl+C 停止服務"

echo ""
echo "=========================================="
echo "  Agentic Agent 管理中心"
echo "  增強版簡化Agent架構 + Kilo Code MCP"
echo "=========================================="
echo ""

# 啟動Flask應用
python3 app.py

