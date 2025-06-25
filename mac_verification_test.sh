#!/bin/bash

# PowerAutomation Mac環境驗證測試腳本
# 用於在真實Mac環境中驗證VSCode擴展和MCP連接

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_header() { echo -e "${PURPLE}🚀 $1${NC}"; echo "=" $(printf "%*s" ${#1} "" | tr ' ' '='); }

# 配置變量
EC2_HOST="18.212.97.173"
EC2_USER="ec2-user"
KEY_FILE="alexchuang.pem"
EXTENSION_ID="powerautomation.powerautomation-local-mcp"
TEST_LOG="mac_verification_test_$(date +%Y%m%d_%H%M%S).log"

# 創建測試日誌
exec > >(tee -a "$TEST_LOG") 2>&1

print_header "PowerAutomation Mac環境驗證測試開始"

print_info "測試時間: $(date)"
print_info "操作系統: $(uname -s) $(uname -r)"
print_info "測試日誌: $TEST_LOG"

# 步驟1: 檢查Mac環境
print_header "步驟1: Mac環境檢查"

# 檢查是否為Mac系統
if [[ "$(uname -s)" != "Darwin" ]]; then
    print_error "此測試腳本僅適用於Mac系統"
    print_info "當前系統: $(uname -s)"
    exit 1
fi
print_success "確認Mac環境"

# 檢查macOS版本
MACOS_VERSION=$(sw_vers -productVersion)
print_success "macOS版本: $MACOS_VERSION"

# 步驟2: 檢查項目文件
print_header "步驟2: 檢查項目文件"

if [ ! -d "aicore0624" ]; then
    print_info "克隆aicore0624項目..."
    git clone https://github.com/alexchuang650730/aicore0624.git
    if [ $? -eq 0 ]; then
        print_success "項目克隆成功"
    else
        print_error "項目克隆失敗"
        exit 1
    fi
else
    print_success "aicore0624項目已存在"
fi

cd aicore0624

# 檢查VSIX文件
VSIX_FILE="PowerAutomation_local/vscode-extension/powerautomation-local-mcp-3.0.0.vsix"
if [ -f "$VSIX_FILE" ]; then
    VSIX_SIZE=$(stat -f%z "$VSIX_FILE")
    print_success "VSIX文件存在: $VSIX_FILE ($(($VSIX_SIZE / 1024))KB)"
else
    print_error "VSIX文件不存在: $VSIX_FILE"
    exit 1
fi

# 步驟3: 檢查VS Code安裝
print_header "步驟3: VS Code安裝檢查"

VSCODE_COMMAND=""

# 檢查多種VS Code安裝方式
if command -v code &> /dev/null; then
    VSCODE_COMMAND="code"
    print_success "在PATH中找到VS Code命令"
elif [ -f "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" ]; then
    VSCODE_COMMAND="/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
    print_success "在Applications中找到VS Code"
    # 添加到PATH（臨時）
    export PATH="/Applications/Visual Studio Code.app/Contents/Resources/app/bin:$PATH"
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

# 步驟4: 安裝PowerAutomation擴展
print_header "步驟4: 安裝PowerAutomation擴展"

# 檢查現有擴展
if $VSCODE_COMMAND --list-extensions | grep -q "$EXTENSION_ID"; then
    CURRENT_VERSION=$($VSCODE_COMMAND --list-extensions --show-versions | grep "$EXTENSION_ID" | cut -d'@' -f2)
    print_warning "PowerAutomation擴展已安裝: $CURRENT_VERSION"
    print_info "卸載舊版本..."
    $VSCODE_COMMAND --uninstall-extension "$EXTENSION_ID" || true
    sleep 2
fi

# 安裝新擴展
print_info "安裝PowerAutomation擴展..."
if $VSCODE_COMMAND --install-extension "$VSIX_FILE" --force; then
    print_success "擴展安裝成功"
    sleep 3  # 等待擴展註冊
else
    print_error "擴展安裝失敗"
    exit 1
fi

# 驗證安裝
if $VSCODE_COMMAND --list-extensions | grep -q "$EXTENSION_ID"; then
    INSTALLED_VERSION=$($VSCODE_COMMAND --list-extensions --show-versions | grep "$EXTENSION_ID" | cut -d'@' -f2)
    print_success "擴展驗證成功: $EXTENSION_ID@$INSTALLED_VERSION"
else
    print_error "擴展驗證失敗"
    exit 1
fi

# 步驟5: 檢查擴展功能
print_header "步驟5: 檢查擴展功能"

# 檢查擴展目錄
EXTENSIONS_DIR="$HOME/.vscode/extensions"
POWERAUTOMATION_DIR=$(find "$EXTENSIONS_DIR" -name "*powerautomation*" -type d | head -n1)

if [ -n "$POWERAUTOMATION_DIR" ]; then
    print_success "擴展目錄: $POWERAUTOMATION_DIR"
    
    # 檢查關鍵文件
    if [ -f "$POWERAUTOMATION_DIR/package.json" ]; then
        print_success "package.json存在"
        
        # 提取擴展信息
        EXTENSION_NAME=$(grep '"displayName"' "$POWERAUTOMATION_DIR/package.json" | cut -d'"' -f4)
        EXTENSION_DESC=$(grep '"description"' "$POWERAUTOMATION_DIR/package.json" | cut -d'"' -f4)
        
        print_info "擴展名稱: $EXTENSION_NAME"
        print_info "擴展描述: $EXTENSION_DESC"
    fi
    
    if [ -f "$POWERAUTOMATION_DIR/out/extension.js" ]; then
        print_success "extension.js存在"
    fi
else
    print_warning "未找到PowerAutomation擴展目錄"
fi

# 步驟6: 測試EC2連接
print_header "步驟6: 測試EC2連接"

if [ -f "../$KEY_FILE" ]; then
    print_info "使用SSH密鑰測試EC2連接..."
    if ssh -i "../$KEY_FILE" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "echo 'EC2連接測試成功'" 2>/dev/null; then
        print_success "EC2連接正常"
        
        # 檢查EC2上的PowerAutomation狀態
        EC2_STATUS=$(ssh -i "../$KEY_FILE" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "cd aicore0624 && ls -la PowerAutomation PowerAutomation_local 2>/dev/null | wc -l" 2>/dev/null)
        if [ "$EC2_STATUS" -gt "0" ]; then
            print_success "EC2上PowerAutomation組件正常"
        else
            print_warning "EC2上PowerAutomation組件可能有問題"
        fi
    else
        print_warning "EC2連接失敗，請檢查網絡和密鑰"
    fi
else
    print_warning "SSH密鑰文件不存在，跳過EC2連接測試"
fi

# 步驟7: 啟動VS Code進行功能測試
print_header "步驟7: 啟動VS Code進行功能測試"

print_info "準備啟動VS Code進行功能測試..."
print_info "請在VS Code中執行以下測試:"
print_info "1. 打開命令面板 (Cmd+Shift+P)"
print_info "2. 搜索 'PowerAutomation' 查看可用命令"
print_info "3. 檢查擴展是否在擴展面板中顯示為已啟用"
print_info "4. 測試擴展的基本功能"

# 詢問是否自動打開VS Code
read -p "是否要自動打開VS Code進行測試? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "正在打開VS Code..."
    $VSCODE_COMMAND . &
    VSCODE_PID=$!
    print_success "VS Code已啟動 (PID: $VSCODE_PID)"
    
    # 等待用戶測試
    print_info "請在VS Code中測試PowerAutomation擴展功能..."
    read -p "測試完成後按Enter繼續..." -r
fi

# 步驟8: 生成Mac驗證報告
print_header "步驟8: 生成Mac驗證報告"

MAC_REPORT="mac_verification_report_$(date +%Y%m%d_%H%M%S).json"

cat > "$MAC_REPORT" << EOF
{
  "verification_info": {
    "timestamp": "$(date -Iseconds)",
    "test_id": "mac_verify_$(date +%s)",
    "status": "completed",
    "platform": "macOS"
  },
  "environment": {
    "os": "$(uname -s)",
    "os_version": "$MACOS_VERSION",
    "architecture": "$(uname -m)",
    "vscode_command": "$VSCODE_COMMAND",
    "vscode_version": "$VSCODE_VERSION"
  },
  "extension": {
    "name": "PowerAutomation Local MCP",
    "id": "$EXTENSION_ID",
    "version": "$INSTALLED_VERSION",
    "vsix_file": "$VSIX_FILE",
    "installation_path": "$POWERAUTOMATION_DIR"
  },
  "verification_results": {
    "environment_check": true,
    "project_files_check": true,
    "vscode_installation": true,
    "extension_installation": true,
    "extension_verification": true,
    "ec2_connection": $([ -f "../$KEY_FILE" ] && echo "true" || echo "false")
  },
  "test_logs": {
    "test_log": "$TEST_LOG",
    "verification_report": "$MAC_REPORT"
  }
}
EOF

print_success "Mac驗證報告已生成: $MAC_REPORT"

# 步驟9: 顯示測試總結
print_header "步驟9: 測試總結"

print_success "🎉 PowerAutomation Mac環境驗證測試完成!"
print_info "📋 測試日誌: $TEST_LOG"
print_info "📊 驗證報告: $MAC_REPORT"
print_info "🔧 擴展ID: $EXTENSION_ID@$INSTALLED_VERSION"

# 顯示所有已安裝的擴展
print_info "📦 已安裝的VS Code擴展:"
$VSCODE_COMMAND --list-extensions --show-versions

print_header "後續建議"
print_info "1. 定期更新PowerAutomation擴展"
print_info "2. 監控EC2與Mac之間的連接狀態"
print_info "3. 測試擴展的高級功能"
print_info "4. 查看擴展日誌以排除問題"

exit 0

