#!/bin/bash

# Human Loop MCP 核心集成 - 簡化更新腳本
# 只更新 2 個核心檔案，不修改任何現有代碼

set -e

# 顏色定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo "Human Loop MCP 核心集成 - 簡化更新"
echo "只更新 2 個檔案，利用 AICore 現有能力"
echo -e "==========================================${NC}"
echo ""

# 檢查檔案存在性
echo -e "${BLUE}[檢查]${NC} 驗證要更新的檔案..."

files_to_check=(
    "PowerAutomation/components/human_loop_mcp_adapter.py"
    "PowerAutomation/components/human_loop_integration_examples.py"
    "GitHub_Update_File_List_Final.md"
)

missing_files=()

for file in "${files_to_check[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}✅${NC} $file"
    else
        echo -e "${YELLOW}❌${NC} $file (檔案不存在)"
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -gt 0 ]]; then
    echo ""
    echo -e "${YELLOW}[警告]${NC} 以下檔案不存在:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo "請確認檔案已正確創建。"
    exit 1
fi

echo ""
echo -e "${GREEN}[成功]${NC} 所有檔案檢查通過"
echo ""

# 顯示更新摘要
echo -e "${BLUE}[摘要]${NC} 即將更新的檔案:"
echo ""
echo "🚀 核心適配器:"
echo "  ✅ PowerAutomation/components/human_loop_mcp_adapter.py"
echo "     - 極簡 Human Loop MCP 集成適配器"
echo "     - 提供確認、選擇、輸入等交互接口"
echo "     - HumanLoopIntegrationMixin 供現有組件繼承"
echo ""
echo "📖 集成示例:"
echo "  ✅ PowerAutomation/components/human_loop_integration_examples.py"
echo "     - 完整的集成示例和使用指南"
echo "     - 涵蓋各種現有組件的集成方式"
echo ""
echo "📋 更新文檔:"
echo "  ✅ GitHub_Update_File_List_Final.md"
echo "     - 最終簡化版檔案清單"
echo ""
echo "🎯 設計原則確認:"
echo "  ✅ 只集成 Human Loop MCP 核心能力"
echo "  ✅ 利用 AICore 現有服務器和功能"
echo "  ✅ 不重複實現智能路由、專家系統等"
echo "  ✅ 極簡設計：僅 2 個核心檔案"
echo ""

# 確認更新
read -p "確認更新到 GitHub? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}[取消]${NC} 更新已取消"
    exit 0
fi

echo ""
echo -e "${BLUE}[執行]${NC} 開始 Git 更新..."

# 檢查 Git 狀態
if ! git status &> /dev/null; then
    echo -e "${YELLOW}[錯誤]${NC} 當前目錄不是 Git 倉庫"
    exit 1
fi

# 添加檔案
echo -e "${BLUE}[Git]${NC} 添加檔案到暫存區..."
git add PowerAutomation/components/human_loop_mcp_adapter.py
git add PowerAutomation/components/human_loop_integration_examples.py
git add GitHub_Update_File_List_Final.md

# 檢查是否有變更
if git diff --cached --quiet; then
    echo -e "${YELLOW}[提示]${NC} 沒有檔案變更，跳過提交"
else
    # 提交變更
    echo -e "${BLUE}[Git]${NC} 提交變更..."
    git commit -m "feat: Add Human Loop MCP core integration adapter

- Add human_loop_mcp_adapter.py: 極簡 Human Loop MCP 集成適配器
  * 提供與 Human Loop MCP 服務的通信接口
  * HumanLoopIntegrationMixin 供現有組件繼承
  * 支持確認、選擇、輸入等多種交互類型
  * 便利函數支持快速集成

- Add human_loop_integration_examples.py: 完整集成示例
  * Enhanced VSCode Installer MCP 集成示例
  * General Processor MCP 集成示例
  * 簡單工作流和批量操作示例
  * 展示三種集成方式：Mixin、客戶端、便利函數

- Add GitHub_Update_File_List_Final.md: 最終簡化版檔案清單

設計原則：
- 只專注於 Human Loop MCP 核心集成能力
- 利用 AICore 現有的智能路由、專家系統、測試框架功能
- 極簡設計：僅 2 個核心檔案，~900 行代碼
- 零侵入性：完全不修改現有代碼
- 輕量級適配器：職責單一，易於維護"

    echo -e "${GREEN}[成功]${NC} 提交完成"
fi

# 詢問是否推送
echo ""
read -p "是否立即推送到 GitHub? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}[Git]${NC} 推送到 GitHub..."
    git push origin main
    echo -e "${GREEN}[成功]${NC} 推送完成"
else
    echo -e "${YELLOW}[提示]${NC} 跳過推送，您可以稍後手動推送:"
    echo "  git push origin main"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Human Loop MCP 核心集成更新完成！"
echo -e "==========================================${NC}"
echo ""
echo "📊 更新統計:"
echo "  - 新增檔案: 2 個"
echo "  - 修改檔案: 0 個"
echo "  - 總代碼行數: ~900 行"
echo "  - 設計原則: 極簡、零侵入、充分利用 AICore"
echo ""
echo "🚀 下一步:"
echo "  1. 在現有組件中導入適配器:"
echo "     from PowerAutomation.components.human_loop_mcp_adapter import HumanLoopIntegrationMixin"
echo ""
echo "  2. 繼承 Mixin 獲得人機交互能力:"
echo "     class YourComponent(HumanLoopIntegrationMixin):"
echo ""
echo "  3. 確保 Human Loop MCP 服務運行:"
echo "     http://localhost:8096"
echo ""
echo "  4. 查看完整示例:"
echo "     PowerAutomation/components/human_loop_integration_examples.py"
echo ""
echo -e "${GREEN}[完成]${NC} Human Loop MCP 核心集成已成功更新到 GitHub！"

