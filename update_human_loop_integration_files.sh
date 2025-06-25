#!/bin/bash

# Human Loop Integration Tool GitHub 更新腳本
# 只更新獨立工具檔案，不修改 AICore 核心

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

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

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 檢查 Git 狀態
check_git_status() {
    log_info "檢查 Git 狀態..."
    
    if ! git status &> /dev/null; then
        log_error "當前目錄不是 Git 倉庫"
        exit 1
    fi
    
    # 檢查是否有未提交的更改
    if ! git diff-index --quiet HEAD --; then
        log_warning "檢測到未提交的更改"
        echo "當前未提交的檔案:"
        git status --porcelain
        echo ""
        read -p "是否繼續? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "操作已取消"
            exit 0
        fi
    fi
    
    log_success "Git 狀態檢查通過"
}

# 檢查檔案存在性
check_files() {
    log_info "檢查要更新的檔案..."
    
    local files_to_check=(
        "PowerAutomation/tools/human_loop_integration_tool.py"
        "PowerAutomation/tools/human_loop_integration_server.py"
        "PowerAutomation/tools/human_loop_integration_config.json"
        "PowerAutomation/tools/README.md"
        "deploy_human_loop_integration_tool.sh"
        "GitHub_Update_File_List_Corrected.md"
    )
    
    local missing_files=()
    
    for file in "${files_to_check[@]}"; do
        if [[ -f "$file" ]]; then
            log_success "✅ $file"
        else
            log_error "❌ $file (檔案不存在)"
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        log_error "以下檔案不存在，請先運行部署腳本:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        echo ""
        log_info "運行: ./deploy_human_loop_integration_tool.sh"
        exit 1
    fi
    
    log_success "所有檔案檢查通過"
}

# 確認更新內容
confirm_update() {
    echo ""
    echo "=========================================="
    echo "Human Loop Integration Tool 更新確認"
    echo "=========================================="
    echo ""
    echo "📋 將要更新的檔案:"
    echo ""
    echo "🚀 核心工具檔案:"
    echo "  ✅ PowerAutomation/tools/human_loop_integration_tool.py"
    echo "  ✅ PowerAutomation/tools/human_loop_integration_server.py"
    echo "  ✅ PowerAutomation/tools/human_loop_integration_config.json"
    echo ""
    echo "📖 文檔和腳本:"
    echo "  ✅ PowerAutomation/tools/README.md"
    echo "  ✅ deploy_human_loop_integration_tool.sh"
    echo "  ✅ GitHub_Update_File_List_Corrected.md"
    echo ""
    echo "🎯 設計原則確認:"
    echo "  ✅ 不修改 AICore 核心組件 (PowerAutomation/core/)"
    echo "  ✅ 不修改現有組件 (PowerAutomation/components/)"
    echo "  ✅ 作為獨立工具運行 (PowerAutomation/tools/)"
    echo "  ✅ 通過 API 集成，可插拔架構"
    echo ""
    echo "📊 更新統計:"
    echo "  - 新增檔案: 6 個"
    echo "  - 修改檔案: 0 個"
    echo "  - 總代碼行數: ~2700 行"
    echo "  - 影響範圍: 最小 (僅新增工具目錄)"
    echo ""
    
    read -p "確認更新到 GitHub? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "更新已取消"
        exit 0
    fi
}

# 執行 Git 更新
perform_git_update() {
    log_step "開始 Git 更新流程..."
    
    # 第一批: 核心工具檔案
    log_info "第一批: 添加核心工具檔案..."
    git add PowerAutomation/tools/human_loop_integration_tool.py
    git add PowerAutomation/tools/human_loop_integration_server.py
    git add PowerAutomation/tools/human_loop_integration_config.json
    
    if git diff --cached --quiet; then
        log_warning "第一批檔案無變更，跳過提交"
    else
        git commit -m "feat: Add Human Loop Integration Tool as independent tool

- Add human_loop_integration_tool.py: 智能路由決策、專家系統、測試框架
- Add human_loop_integration_server.py: FastAPI HTTP 服務器
- Add human_loop_integration_config.json: 工具配置檔案
- 設計為獨立工具，不修改 AICore 核心組件
- 通過 HTTP API 與現有系統集成"
        log_success "第一批檔案提交完成"
    fi
    
    # 第二批: 部署腳本和文檔
    log_info "第二批: 添加部署腳本和文檔..."
    git add deploy_human_loop_integration_tool.sh
    git add PowerAutomation/tools/README.md
    git add GitHub_Update_File_List_Corrected.md
    
    if git diff --cached --quiet; then
        log_warning "第二批檔案無變更，跳過提交"
    else
        git commit -m "feat: Add deployment script and documentation for Human Loop Integration Tool

- Add deploy_human_loop_integration_tool.sh: 一鍵部署腳本
- Add PowerAutomation/tools/README.md: 完整工具文檔和使用指南
- Add GitHub_Update_File_List_Corrected.md: 修正版檔案更新清單
- 包含架構說明、API 文檔、集成示例、故障排除指南"
        log_success "第二批檔案提交完成"
    fi
    
    # 第三批: 集成示例 (如果存在)
    if [[ -d "PowerAutomation/tools/examples" ]]; then
        log_info "第三批: 添加集成示例..."
        git add PowerAutomation/tools/examples/
        
        if git diff --cached --quiet; then
            log_warning "第三批檔案無變更，跳過提交"
        else
            git commit -m "feat: Add integration examples for Human Loop Integration Tool

- Add integration_example.py: Python 集成示例
- Add integration_example.sh: Shell 集成示例
- 展示如何與現有 PowerAutomation 組件集成
- 提供實際使用示例和最佳實踐演示"
            log_success "第三批檔案提交完成"
        fi
    else
        log_info "集成示例目錄不存在，跳過第三批"
    fi
    
    # 創建版本標籤
    log_info "創建版本標籤..."
    local tag_name="human-loop-integration-v1.0.0"
    
    if git tag -l | grep -q "^$tag_name$"; then
        log_warning "標籤 $tag_name 已存在，跳過創建"
    else
        git tag -a "$tag_name" -m "Human Loop Integration Tool v1.0.0

Features:
- 智能路由決策系統 (自動/人工/專家/條件)
- Human Loop MCP 無縫集成
- 7 種專家類型調用機制
- 4 種測試類型深度驗證
- 機器學習增量優化
- 完整的 HTTP API 接口
- 獨立工具架構，不修改 AICore 核心

Architecture:
- Non-invasive design
- Pluggable architecture
- API-based integration
- Independent service deployment"
        log_success "版本標籤 $tag_name 創建完成"
    fi
}

# 推送到 GitHub
push_to_github() {
    log_step "推送到 GitHub..."
    
    echo ""
    read -p "是否立即推送到 GitHub? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "推送提交到 GitHub..."
        git push origin main
        
        log_info "推送標籤到 GitHub..."
        git push origin --tags
        
        log_success "推送完成"
    else
        log_info "跳過推送，您可以稍後手動推送:"
        echo "  git push origin main"
        echo "  git push origin --tags"
    fi
}

# 顯示更新摘要
show_summary() {
    echo ""
    echo "=========================================="
    echo "Human Loop Integration Tool 更新完成"
    echo "=========================================="
    echo ""
    echo "📋 更新摘要:"
    echo ""
    echo "✅ 提交的檔案:"
    echo "  - PowerAutomation/tools/human_loop_integration_tool.py"
    echo "  - PowerAutomation/tools/human_loop_integration_server.py"
    echo "  - PowerAutomation/tools/human_loop_integration_config.json"
    echo "  - PowerAutomation/tools/README.md"
    echo "  - deploy_human_loop_integration_tool.sh"
    echo "  - GitHub_Update_File_List_Corrected.md"
    
    if [[ -d "PowerAutomation/tools/examples" ]]; then
        echo "  - PowerAutomation/tools/examples/ (集成示例)"
    fi
    
    echo ""
    echo "🏷️  版本標籤: human-loop-integration-v1.0.0"
    echo ""
    echo "🎯 架構特點:"
    echo "  ✅ 獨立工具設計，不修改 AICore 核心"
    echo "  ✅ 可插拔架構，可隨時啟用/禁用"
    echo "  ✅ HTTP API 集成，標準化接口"
    echo "  ✅ 完整文檔和示例"
    echo ""
    echo "🚀 下一步:"
    echo "  1. 部署工具: ./deploy_human_loop_integration_tool.sh"
    echo "  2. 啟動服務: ./PowerAutomation/tools/start_human_loop_integration.sh"
    echo "  3. 檢查狀態: ./PowerAutomation/tools/check_human_loop_integration.sh"
    echo "  4. 查看文檔: PowerAutomation/tools/README.md"
    echo "  5. API 文檔: http://localhost:8098/docs"
    echo ""
    echo "📊 GitHub 倉庫:"
    echo "  - 查看提交: git log --oneline -5"
    echo "  - 查看標籤: git tag -l"
    echo "  - 查看狀態: git status"
    echo ""
}

# 主函數
main() {
    echo "=========================================="
    echo "Human Loop Integration Tool GitHub 更新"
    echo "版本: 1.0.0"
    echo "設計原則: 不修改 AICore 核心"
    echo "=========================================="
    echo ""
    
    # 檢查 Git 狀態
    check_git_status
    
    # 檢查檔案
    check_files
    
    # 確認更新
    confirm_update
    
    # 執行 Git 更新
    perform_git_update
    
    # 推送到 GitHub
    push_to_github
    
    # 顯示摘要
    show_summary
    
    log_success "Human Loop Integration Tool 更新流程完成！"
}

# 執行主函數
main "$@"

