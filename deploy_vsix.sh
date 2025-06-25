#!/bin/bash

# PowerAutomation VSIX 部署腳本
# 自動化部署最新的PowerAutomation VSCode擴展

set -e

echo "🚀 開始PowerAutomation VSIX部署流程..."

# 配置變量
VSIX_FILE="PowerAutomation_local/vscode-extension/powerautomation-local-mcp-3.0.0.vsix"
EXTENSION_ID="powerautomation.powerautomation-local-mcp"
DEPLOYMENT_LOG="vsix_deployment_$(date +%Y%m%d_%H%M%S).log"

# 創建部署日誌
exec > >(tee -a "$DEPLOYMENT_LOG") 2>&1

echo "📅 部署時間: $(date)"
echo "📁 工作目錄: $(pwd)"
echo "📦 VSIX文件: $VSIX_FILE"

# 步驟1: 檢查環境
echo ""
echo "=== 步驟1: 環境檢查 ==="

# 檢查VSIX文件是否存在
if [ ! -f "$VSIX_FILE" ]; then
    echo "❌ 錯誤: VSIX文件不存在: $VSIX_FILE"
    exit 1
fi
echo "✅ VSIX文件存在: $VSIX_FILE"

# 檢查文件大小
VSIX_SIZE=$(stat -c%s "$VSIX_FILE")
echo "📊 VSIX文件大小: $VSIX_SIZE bytes ($(($VSIX_SIZE / 1024))KB)"

# 檢查VS Code是否安裝
if ! command -v code &> /dev/null; then
    echo "❌ 錯誤: VS Code未安裝或不在PATH中"
    echo "正在嘗試安裝VS Code..."
    
    # 安裝VS Code
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
    sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
    sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
    sudo apt update
    sudo apt install -y code
    
    if ! command -v code &> /dev/null; then
        echo "❌ VS Code安裝失敗"
        exit 1
    fi
fi

VSCODE_VERSION=$(code --version | head -n1)
echo "✅ VS Code已安裝: $VSCODE_VERSION"

# 步驟2: 檢查現有擴展
echo ""
echo "=== 步驟2: 檢查現有擴展 ==="

if code --list-extensions | grep -q "$EXTENSION_ID"; then
    CURRENT_VERSION=$(code --list-extensions --show-versions | grep "$EXTENSION_ID" | cut -d'@' -f2)
    echo "⚠️  PowerAutomation擴展已安裝: $CURRENT_VERSION"
    echo "正在卸載舊版本..."
    code --uninstall-extension "$EXTENSION_ID" || true
else
    echo "ℹ️  PowerAutomation擴展未安裝"
fi

# 步驟3: 安裝新擴展
echo ""
echo "=== 步驟3: 安裝PowerAutomation擴展 ==="

echo "正在安裝: $VSIX_FILE"
if code --install-extension "$VSIX_FILE" --force; then
    echo "✅ 擴展安裝成功"
else
    echo "❌ 擴展安裝失敗"
    exit 1
fi

# 步驟4: 驗證安裝
echo ""
echo "=== 步驟4: 驗證安裝 ==="

if code --list-extensions | grep -q "$EXTENSION_ID"; then
    INSTALLED_VERSION=$(code --list-extensions --show-versions | grep "$EXTENSION_ID" | cut -d'@' -f2)
    echo "✅ 擴展驗證成功: $EXTENSION_ID@$INSTALLED_VERSION"
else
    echo "❌ 擴展驗證失敗: 未找到已安裝的擴展"
    exit 1
fi

# 步驟5: 生成部署報告
echo ""
echo "=== 步驟5: 生成部署報告 ==="

DEPLOYMENT_REPORT="vsix_deployment_report_$(date +%Y%m%d_%H%M%S).json"

cat > "$DEPLOYMENT_REPORT" << EOF
{
  "deployment_info": {
    "timestamp": "$(date -Iseconds)",
    "deployment_id": "deploy_$(date +%s)",
    "status": "success"
  },
  "environment": {
    "os": "$(uname -s)",
    "architecture": "$(uname -m)",
    "vscode_version": "$VSCODE_VERSION"
  },
  "extension": {
    "name": "PowerAutomation Local MCP",
    "id": "$EXTENSION_ID",
    "version": "$INSTALLED_VERSION",
    "vsix_file": "$VSIX_FILE",
    "vsix_size": $VSIX_SIZE
  },
  "verification": {
    "installation_verified": true,
    "extension_listed": true
  },
  "logs": {
    "deployment_log": "$DEPLOYMENT_LOG",
    "deployment_report": "$DEPLOYMENT_REPORT"
  }
}
EOF

echo "📋 部署報告已生成: $DEPLOYMENT_REPORT"

# 步驟6: 顯示所有已安裝的擴展
echo ""
echo "=== 步驟6: 已安裝的擴展列表 ==="
code --list-extensions --show-versions

echo ""
echo "🎉 PowerAutomation VSIX部署完成!"
echo "📋 部署日誌: $DEPLOYMENT_LOG"
echo "📊 部署報告: $DEPLOYMENT_REPORT"
echo "🔧 擴展ID: $EXTENSION_ID@$INSTALLED_VERSION"

# 返回成功狀態
exit 0

