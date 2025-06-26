#!/bin/bash

# SmartUI 智能部署腳本
# 多種部署方式，自動選擇最佳方案

set -e

PROJECT_ROOT="/home/ubuntu/aicore0624"
VSIX_DIR="$PROJECT_ROOT/PowerAutomation_local/vscode-extension"
LOG_FILE="/tmp/smartui_deploy.log"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日誌函數
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

# 檢測反向隧道連接
check_tunnel() {
    log "檢測反向隧道連接..."
    for i in {1..3}; do
        if ssh -p 2222 -o ConnectTimeout=3 localhost "echo 'tunnel_ok'" >/dev/null 2>&1; then
            success "反向隧道連接正常"
            return 0
        fi
        warning "嘗試 $i/3 失敗，等待 2 秒..."
        sleep 2
    done
    error "反向隧道連接失敗"
    return 1
}

# 通過反向隧道部署
deploy_via_tunnel() {
    log "嘗試通過反向隧道部署..."
    
    if ! check_tunnel; then
        return 1
    fi
    
    cd "$VSIX_DIR"
    LATEST_VSIX=$(ls -t *.vsix 2>/dev/null | head -1)
    
    if [[ -z "$LATEST_VSIX" ]]; then
        error "未找到 VSIX 文件"
        return 1
    fi
    
    log "部署文件: $LATEST_VSIX"
    
    # 複製文件到 Mac
    if scp -P 2222 -o ConnectTimeout=10 "$LATEST_VSIX" localhost:/tmp/ >/dev/null 2>&1; then
        success "文件傳輸成功"
    else
        error "文件傳輸失敗"
        return 1
    fi
    
    # 安裝到 Cursor
    if ssh -p 2222 localhost "cursor --install-extension /tmp/$LATEST_VSIX --force" >/dev/null 2>&1; then
        success "Cursor 插件安裝成功"
        return 0
    else
        error "Cursor 插件安裝失敗"
        return 1
    fi
}

# 通過 HTTP 服務部署
deploy_via_http() {
    log "嘗試通過 HTTP 服務部署..."
    
    cd "$VSIX_DIR"
    LATEST_VSIX=$(ls -t *.vsix 2>/dev/null | head -1)
    
    if [[ -z "$LATEST_VSIX" ]]; then
        error "未找到 VSIX 文件"
        return 1
    fi
    
    # 啟動臨時 HTTP 服務
    log "啟動 HTTP 文件服務..."
    python3 -m http.server 8080 --directory "$VSIX_DIR" >/dev/null 2>&1 &
    HTTP_PID=$!
    
    sleep 2
    
    # 獲取 EC2 公網 IP
    EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")
    
    success "HTTP 服務已啟動: http://$EC2_IP:8080/$LATEST_VSIX"
    log "請在 Mac 端執行以下命令："
    echo -e "${BLUE}curl -O http://$EC2_IP:8080/$LATEST_VSIX${NC}"
    echo -e "${BLUE}cursor --install-extension $LATEST_VSIX --force${NC}"
    
    # 等待用戶確認
    read -p "按 Enter 鍵停止 HTTP 服務..."
    kill $HTTP_PID 2>/dev/null
    
    return 0
}

# 通過 GitHub Release 部署
deploy_via_github() {
    log "嘗試通過 GitHub Release 部署..."
    
    cd "$PROJECT_ROOT"
    
    # 檢查是否有 gh CLI
    if ! command -v gh >/dev/null 2>&1; then
        warning "GitHub CLI 未安裝，跳過此方式"
        return 1
    fi
    
    cd "$VSIX_DIR"
    LATEST_VSIX=$(ls -t *.vsix 2>/dev/null | head -1)
    
    if [[ -z "$LATEST_VSIX" ]]; then
        error "未找到 VSIX 文件"
        return 1
    fi
    
    VERSION="v$(date +%Y.%m.%d.%H%M)"
    
    log "創建 GitHub Release: $VERSION"
    if gh release create "$VERSION" "$LATEST_VSIX" --title "SmartUI $VERSION" --notes "自動發布的 SmartUI 版本" >/dev/null 2>&1; then
        success "GitHub Release 創建成功"
        log "下載鏈接: https://github.com/alexchuang650730/aicore0624/releases/latest"
        return 0
    else
        error "GitHub Release 創建失敗"
        return 1
    fi
}

# 本地網絡共享部署
deploy_via_local() {
    log "嘗試通過本地網絡共享部署..."
    
    cd "$VSIX_DIR"
    LATEST_VSIX=$(ls -t *.vsix 2>/dev/null | head -1)
    
    if [[ -z "$LATEST_VSIX" ]]; then
        error "未找到 VSIX 文件"
        return 1
    fi
    
    # 複製到共享目錄
    SHARE_DIR="/tmp/smartui_share"
    mkdir -p "$SHARE_DIR"
    cp "$LATEST_VSIX" "$SHARE_DIR/"
    
    success "文件已複製到: $SHARE_DIR/$LATEST_VSIX"
    log "請手動將此文件傳輸到 Mac 端並安裝"
    
    return 0
}

# 主部署函數
main() {
    log "🚀 SmartUI 智能部署開始..."
    log "日誌文件: $LOG_FILE"
    
    # 部署方式優先級
    deploy_methods=(
        "deploy_via_tunnel:反向隧道部署"
        "deploy_via_http:HTTP 服務部署"
        "deploy_via_github:GitHub Release 部署"
        "deploy_via_local:本地共享部署"
    )
    
    for method_info in "${deploy_methods[@]}"; do
        method_name="${method_info%%:*}"
        method_desc="${method_info##*:}"
        
        log "嘗試: $method_desc"
        
        if $method_name; then
            success "🎉 部署成功！使用方式: $method_desc"
            log "SmartUI 已成功部署到 Cursor"
            exit 0
        else
            warning "$method_desc 失敗，嘗試下一種方式..."
        fi
        
        echo ""
    done
    
    error "所有部署方式都失敗了"
    log "請檢查日誌文件: $LOG_FILE"
    exit 1
}

# 執行主函數
main "$@"

