#!/bin/bash

# PowerAutomation VSIX Mac部署腳本
# 專為Mac環境設計的VSCode擴展部署腳本

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印帶顏色的消息
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

print_header() {
    echo -e "${BLUE}🚀 $1${NC}"
    echo "=" $(printf "%*s" ${#1} "" | tr ' ' '=')
}

# 主要配置
EXTENSION_NAME="PowerAutomation Local MCP"
EXTENSION_ID="powerautomation.powerautomation-local-mcp"
VSIX_FILE="PowerAutomation_local/vscode-extension/powerautomation-local-mcp-3.0.0.vsix"
DEPLOYMENT_LOG="mac_vsix_deployment_$(date +%Y%m%d_%H%M%S).log"

# 創建部署日誌
exec > >(tee -a "$DEPLOYMENT_LOG") 2>&1

print_header "PowerAutomation VSIX Mac部署開始"

print_info "部署時間: $(date)"
print_info "操作系統: $(uname -s) $(uname -r)"
print_info "架構: $(uname -m)"
print_info "工作目錄: $(pwd)"

# 步驟1: 環境檢查
print_header "步驟1: Mac環境檢查"

# 檢查是否為Mac系統
if [[ "$(uname -s)" != "Darwin" ]]; then
    print_error "此腳本僅適用於Mac系統"
    exit 1
fi
print_success "確認Mac環境"

# 檢查VSIX文件
if [ ! -f "$VSIX_FILE" ]; then
    print_error "VSIX文件不存在: $VSIX_FILE"
    print_info "請確保已從GitHub克隆完整的aicore0624倉庫"
    exit 1
fi

VSIX_SIZE=$(stat -f%z "$VSIX_FILE")
print_success "VSIX文件存在: $VSIX_FILE ($(($VSIX_SIZE / 1024))KB)"

# 步驟2: 檢查VS Code安裝
print_header "步驟2: VS Code安裝檢查"

# 檢查VS Code的多種安裝方式
VSCODE_COMMAND=""

# 方法1: 檢查PATH中的code命令
if command -v code &> /dev/null; then
    VSCODE_COMMAND="code"
    print_success "在PATH中找到VS Code命令"
elif [ -f "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" ]; then
    VSCODE_COMMAND="/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
    print_success "在Applications中找到VS Code"
elif [ -f "/usr/local/bin/code" ]; then
    VSCODE_COMMAND="/usr/local/bin/code"
    print_success "在/usr/local/bin中找到VS Code"
else
    print_error "未找到VS Code安裝"
    print_info "請安裝VS Code: https://code.visualstudio.com/download"
    print_info "或使用Homebrew: brew install --cask visual-studio-code"
    exit 1
fi

# 獲取VS Code版本
VSCODE_VERSION=$($VSCODE_COMMAND --version | head -n1)
print_success "VS Code版本: $VSCODE_VERSION"

# 步驟3: 檢查現有擴展
print_header "步驟3: 檢查現有擴展"

if $VSCODE_COMMAND --list-extensions | grep -q "$EXTENSION_ID"; then
    CURRENT_VERSION=$($VSCODE_COMMAND --list-extensions --show-versions | grep "$EXTENSION_ID" | cut -d'@' -f2)
    print_warning "PowerAutomation擴展已安裝: $CURRENT_VERSION"
    print_info "正在卸載舊版本..."
    $VSCODE_COMMAND --uninstall-extension "$EXTENSION_ID" || true
    print_success "舊版本已卸載"
else
    print_info "PowerAutomation擴展未安裝"
fi

# 步驟4: 安裝新擴展
print_header "步驟4: 安裝PowerAutomation擴展"

print_info "正在安裝: $VSIX_FILE"
if $VSCODE_COMMAND --install-extension "$VSIX_FILE" --force; then
    print_success "擴展安裝成功"
else
    print_error "擴展安裝失敗"
    exit 1
fi

# 步驟5: 驗證安裝
print_header "步驟5: 驗證安裝"

sleep 2  # 等待擴展註冊

if $VSCODE_COMMAND --list-extensions | grep -q "$EXTENSION_ID"; then
    INSTALLED_VERSION=$($VSCODE_COMMAND --list-extensions --show-versions | grep "$EXTENSION_ID" | cut -d'@' -f2)
    print_success "擴展驗證成功: $EXTENSION_ID@$INSTALLED_VERSION"
else
    print_error "擴展驗證失敗: 未找到已安裝的擴展"
    exit 1
fi

# 步驟6: 檢查擴展目錄
print_header "步驟6: 檢查擴展安裝目錄"

EXTENSIONS_DIR="$HOME/.vscode/extensions"
if [ -d "$EXTENSIONS_DIR" ]; then
    print_success "擴展目錄存在: $EXTENSIONS_DIR"
    
    # 查找PowerAutomation擴展目錄
    POWERAUTOMATION_DIR=$(find "$EXTENSIONS_DIR" -name "*powerautomation*" -type d | head -n1)
    if [ -n "$POWERAUTOMATION_DIR" ]; then
        print_success "PowerAutomation擴展目錄: $POWERAUTOMATION_DIR"
        
        # 檢查擴展文件
        if [ -f "$POWERAUTOMATION_DIR/package.json" ]; then
            print_success "擴展package.json存在"
        fi
    fi
else
    print_warning "擴展目錄不存在: $EXTENSIONS_DIR"
fi

# 步驟7: 生成Mac部署報告
print_header "步驟7: 生成Mac部署報告"

DEPLOYMENT_REPORT="mac_vsix_deployment_report_$(date +%Y%m%d_%H%M%S).json"

cat > "$DEPLOYMENT_REPORT" << EOF
{
  "deployment_info": {
    "timestamp": "$(date -Iseconds)",
    "deployment_id": "mac_deploy_$(date +%s)",
    "status": "success",
    "platform": "macOS"
  },
  "environment": {
    "os": "$(uname -s)",
    "os_version": "$(sw_vers -productVersion)",
    "architecture": "$(uname -m)",
    "vscode_command": "$VSCODE_COMMAND",
    "vscode_version": "$VSCODE_VERSION"
  },
  "extension": {
    "name": "$EXTENSION_NAME",
    "id": "$EXTENSION_ID",
    "version": "$INSTALLED_VERSION",
    "vsix_file": "$VSIX_FILE",
    "vsix_size": $VSIX_SIZE,
    "installation_path": "$POWERAUTOMATION_DIR"
  },
  "verification": {
    "installation_verified": true,
    "extension_listed": true,
    "package_json_exists": $([ -f "$POWERAUTOMATION_DIR/package.json" ] && echo "true" || echo "false")
  },
  "logs": {
    "deployment_log": "$DEPLOYMENT_LOG",
    "deployment_report": "$DEPLOYMENT_REPORT"
  }
}
EOF

print_success "Mac部署報告已生成: $DEPLOYMENT_REPORT"

# 步驟8: 顯示所有已安裝的擴展
print_header "步驟8: 已安裝的擴展列表"
$VSCODE_COMMAND --list-extensions --show-versions

# 步驟9: 提供後續操作建議
print_header "步驟9: 後續操作建議"

print_info "1. 重啟VS Code以確保擴展完全加載"
print_info "2. 打開VS Code命令面板 (Cmd+Shift+P)"
print_info "3. 搜索 'PowerAutomation' 查看可用命令"
print_info "4. 檢查擴展是否在擴展面板中顯示為已啟用"

# 最終成功消息
echo ""
print_success "🎉 PowerAutomation VSIX Mac部署完成!"
print_info "📋 部署日誌: $DEPLOYMENT_LOG"
print_info "📊 部署報告: $DEPLOYMENT_REPORT"
print_info "🔧 擴展ID: $EXTENSION_ID@$INSTALLED_VERSION"

# 可選: 自動打開VS Code
read -p "是否要自動打開VS Code? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "正在打開VS Code..."
    $VSCODE_COMMAND .
fi

exit 0

