#!/bin/bash

# PowerAutomation SmartUI 一鍵部署到 Cursor
# 使用方法: ./deploy_to_cursor.sh

set -e

echo "🚀 PowerAutomation SmartUI 一鍵部署到 Cursor"
echo "=============================================="

# 執行完整部署流程
./smartui_action_script.sh all

echo ""
echo "✅ 部署完成！"
echo ""
echo "📋 接下來的步驟："
echo "1. 重啟 Cursor"
echo "2. 檢查插件是否已安裝"
echo "3. 使用快捷鍵開始體驗 SmartUI"
echo ""
echo "🎯 主要快捷鍵："
echo "  Cmd+Shift+D  - 切換到開發者模式"
echo "  Cmd+Shift+A  - Claude 需求分析"
echo "  Cmd+Shift+R  - Claude 代碼審查"
echo "  Cmd+Shift+G  - Claude 代碼生成"
echo ""

