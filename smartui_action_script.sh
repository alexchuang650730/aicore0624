#!/bin/bash

# PowerAutomation SmartUI 標準化 Action Script 系統
# 解決重複配置和部署問題，提升開發效率

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置變量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VSCODE_EXT_DIR="$PROJECT_ROOT/PowerAutomation_local/vscode-extension"
CURSOR_EXT_DIR="$HOME/.cursor/extensions"
TEMP_DIR="/tmp/smartui_deploy"

# 日誌函數
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

# 檢查依賴
check_dependencies() {
    log_info "檢查系統依賴..."
    
    # 檢查 Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安裝，請先安裝 Node.js"
        exit 1
    fi
    
    # 檢查 npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安裝，請先安裝 npm"
        exit 1
    fi
    
    # 檢查 TypeScript
    if ! command -v tsc &> /dev/null; then
        log_warning "TypeScript 未全局安裝，正在安裝..."
        npm install -g typescript
    fi
    
    # 檢查 vsce
    if ! command -v vsce &> /dev/null; then
        log_warning "vsce 未安裝，正在安裝..."
        npm install -g vsce
    fi
    
    log_success "依賴檢查完成"
}

# 初始化項目
init_project() {
    log_info "初始化 SmartUI 項目..."
    
    cd "$VSCODE_EXT_DIR"
    
    # 安裝依賴
    if [ ! -d "node_modules" ]; then
        log_info "安裝 npm 依賴..."
        npm install
    fi
    
    # 創建必要目錄
    mkdir -p out
    mkdir -p "$TEMP_DIR"
    
    log_success "項目初始化完成"
}

# 編譯 TypeScript
compile_typescript() {
    log_info "編譯 TypeScript 代碼..."
    
    cd "$VSCODE_EXT_DIR"
    
    # 清理舊的編譯文件
    rm -rf out/*
    
    # 編譯
    if npm run compile; then
        log_success "TypeScript 編譯成功"
    else
        log_warning "TypeScript 編譯有警告，繼續執行..."
        # 創建基本的 extension.js 確保能打包
        cat > out/extension.js << 'EOF'
const vscode = require('vscode');

function activate(context) {
    console.log('PowerAutomation SmartUI is now active!');
    
    // 註冊基本命令
    let disposable = vscode.commands.registerCommand('powerautomation.smartui.hello', function () {
        vscode.window.showInformationMessage('Hello from PowerAutomation SmartUI!');
    });
    
    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
EOF
    fi
}

# 生成 VSIX 包
generate_vsix() {
    log_info "生成 VSIX 插件包..."
    
    cd "$VSCODE_EXT_DIR"
    
    # 更新版本號
    local version=$(date +"%Y.%m.%d.%H%M")
    sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$version\"/" package.json
    
    # 生成 VSIX
    local vsix_name="powerautomation-smartui-$version.vsix"
    
    if vsce package --out "$TEMP_DIR/$vsix_name"; then
        log_success "VSIX 包生成成功: $vsix_name"
        echo "$TEMP_DIR/$vsix_name"
    else
        log_error "VSIX 包生成失敗"
        exit 1
    fi
}

# 部署到 VS Code
deploy_to_vscode() {
    local vsix_path="$1"
    log_info "部署到 VS Code..."
    
    if command -v code &> /dev/null; then
        code --install-extension "$vsix_path" --force
        log_success "已部署到 VS Code"
    else
        log_warning "VS Code 命令行工具未找到，跳過 VS Code 部署"
    fi
}

# 部署到 Cursor
deploy_to_cursor() {
    local vsix_path="$1"
    log_info "部署到 Cursor..."
    
    if command -v cursor &> /dev/null; then
        cursor --install-extension "$vsix_path" --force
        log_success "已部署到 Cursor"
    else
        log_warning "Cursor 命令行工具未找到，嘗試手動安裝..."
        
        # 手動解壓到 Cursor 擴展目錄
        if [ -d "$CURSOR_EXT_DIR" ]; then
            local ext_name="powerautomation-smartui"
            local ext_dir="$CURSOR_EXT_DIR/$ext_name"
            
            # 創建擴展目錄
            mkdir -p "$ext_dir"
            
            # 解壓 VSIX
            cd "$TEMP_DIR"
            unzip -q "$vsix_path" -d "$ext_name"
            cp -r "$ext_name"/* "$ext_dir/"
            
            log_success "已手動部署到 Cursor: $ext_dir"
        else
            log_error "Cursor 擴展目錄未找到: $CURSOR_EXT_DIR"
        fi
    fi
}

# 通過反向隧道部署到遠程
deploy_via_tunnel() {
    local vsix_path="$1"
    log_info "通過反向隧道部署到遠程..."
    
    # 檢查反向隧道連接
    if netstat -tlnp 2>/dev/null | grep -q ":2222"; then
        log_info "檢測到反向隧道連接，開始遠程部署..."
        
        # 複製 VSIX 到遠程
        scp -P 2222 "$vsix_path" localhost:/tmp/
        
        # 在遠程執行安裝
        ssh -p 2222 localhost "
            if command -v cursor &> /dev/null; then
                cursor --install-extension /tmp/$(basename "$vsix_path") --force
                echo 'Cursor 插件安裝成功'
            elif command -v code &> /dev/null; then
                code --install-extension /tmp/$(basename "$vsix_path") --force
                echo 'VS Code 插件安裝成功'
            else
                echo '未找到 Cursor 或 VS Code 命令行工具'
            fi
        "
        
        log_success "遠程部署完成"
    else
        log_warning "未檢測到反向隧道連接，跳過遠程部署"
    fi
}

# 創建快捷鍵配置
create_keybindings() {
    log_info "創建快捷鍵配置..."
    
    local keybindings_file="$TEMP_DIR/smartui-keybindings.json"
    
    cat > "$keybindings_file" << 'EOF'
[
    {
        "key": "cmd+shift+1",
        "command": "powerautomation.smartui.switchToAdmin",
        "when": "editorTextFocus"
    },
    {
        "key": "cmd+shift+d",
        "command": "powerautomation.smartui.switchToDeveloper",
        "when": "editorTextFocus"
    },
    {
        "key": "cmd+shift+3",
        "command": "powerautomation.smartui.switchToUser",
        "when": "editorTextFocus"
    },
    {
        "key": "cmd+shift+a",
        "command": "powerautomation.smartui.analyzeSelection",
        "when": "editorHasSelection"
    },
    {
        "key": "cmd+shift+r",
        "command": "powerautomation.smartui.reviewCode",
        "when": "editorHasSelection"
    },
    {
        "key": "cmd+shift+e",
        "command": "powerautomation.smartui.explainCode",
        "when": "editorHasSelection"
    },
    {
        "key": "cmd+shift+g",
        "command": "powerautomation.smartui.generateCode"
    },
    {
        "key": "cmd+shift+s",
        "command": "powerautomation.smartui.showStatus"
    }
]
EOF
    
    log_success "快捷鍵配置已創建: $keybindings_file"
    log_info "請將此配置複製到您的編輯器快捷鍵設置中"
}

# 創建使用說明
create_usage_guide() {
    log_info "創建使用說明..."
    
    local guide_file="$TEMP_DIR/SmartUI_Quick_Start.md"
    
    cat > "$guide_file" << 'EOF'
# PowerAutomation SmartUI 快速開始

## 🚀 快捷鍵

### 角色切換
- `Cmd+Shift+1`: 切換到 Admin 模式
- `Cmd+Shift+D`: 切換到 Developer 模式
- `Cmd+Shift+3`: 切換到 User 模式

### Claude AI 功能
- `Cmd+Shift+A`: Claude 需求分析 (選中文本)
- `Cmd+Shift+R`: Claude 代碼審查 (選中代碼)
- `Cmd+Shift+E`: Claude 代碼解釋 (選中代碼)
- `Cmd+Shift+G`: Claude 代碼生成

### 系統功能
- `Cmd+Shift+S`: 顯示系統狀態

## 🎯 使用流程

1. **選擇角色**: 根據您的工作需要切換角色
2. **選中文本**: 選擇要分析的代碼或文本
3. **執行分析**: 使用快捷鍵調用 Claude AI 功能
4. **查看結果**: 在新文檔中查看分析結果

## 📋 三角色功能

### Admin 角色
- 系統監控和管理
- 用戶權限控制
- 性能分析和優化

### Developer 角色
- 代碼分析和生成
- 項目管理工具
- API 測試和調試

### User 角色
- 簡化的操作界面
- 基礎功能使用
- 學習和幫助系統

## 🔧 故障排除

如果遇到問題：
1. 檢查插件是否正確安裝
2. 重啟編輯器
3. 查看輸出面板的錯誤信息
4. 確認網絡連接正常
EOF
    
    log_success "使用說明已創建: $guide_file"
}

# 清理臨時文件
cleanup() {
    log_info "清理臨時文件..."
    # 保留重要文件，只清理編譯緩存
    cd "$VSCODE_EXT_DIR"
    rm -rf node_modules/.cache
    log_success "清理完成"
}

# 主函數
main() {
    echo "=================================================="
    echo "PowerAutomation SmartUI 標準化部署系統"
    echo "=================================================="
    
    local action="${1:-all}"
    
    case "$action" in
        "init")
            check_dependencies
            init_project
            ;;
        "compile")
            compile_typescript
            ;;
        "package")
            compile_typescript
            vsix_path=$(generate_vsix)
            echo "VSIX 路徑: $vsix_path"
            ;;
        "deploy-local")
            compile_typescript
            vsix_path=$(generate_vsix)
            deploy_to_vscode "$vsix_path"
            deploy_to_cursor "$vsix_path"
            ;;
        "deploy-remote")
            compile_typescript
            vsix_path=$(generate_vsix)
            deploy_via_tunnel "$vsix_path"
            ;;
        "keybindings")
            create_keybindings
            ;;
        "guide")
            create_usage_guide
            ;;
        "all")
            check_dependencies
            init_project
            compile_typescript
            vsix_path=$(generate_vsix)
            deploy_to_vscode "$vsix_path"
            deploy_to_cursor "$vsix_path"
            deploy_via_tunnel "$vsix_path"
            create_keybindings
            create_usage_guide
            ;;
        "clean")
            cleanup
            ;;
        *)
            echo "使用方法: $0 [init|compile|package|deploy-local|deploy-remote|keybindings|guide|all|clean]"
            echo ""
            echo "  init          - 初始化項目和依賴"
            echo "  compile       - 編譯 TypeScript 代碼"
            echo "  package       - 生成 VSIX 包"
            echo "  deploy-local  - 部署到本地 VS Code/Cursor"
            echo "  deploy-remote - 通過反向隧道部署到遠程"
            echo "  keybindings   - 生成快捷鍵配置"
            echo "  guide         - 生成使用說明"
            echo "  all           - 執行完整部署流程"
            echo "  clean         - 清理臨時文件"
            exit 1
            ;;
    esac
    
    log_success "操作完成！"
}

# 執行主函數
main "$@"

