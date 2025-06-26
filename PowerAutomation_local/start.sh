#!/bin/bash

# PowerAutomation Local MCP 啟動腳本
# 重構後版本 - 2025-06-25

# 激活虛擬環境
if [ -d "powerautomation_env" ]; then
    source powerautomation_env/bin/activate
else
    echo "❌ 虛擬環境不存在，請先運行 scripts/deploy/install.sh"
    exit 1
fi

# 啟動服務
echo "🚀 啟動 PowerAutomation Local MCP Adapter..."
echo "📁 使用重構後的項目結構"

# 檢查核心文件是否存在
if [ ! -f "core/mcp_server.py" ]; then
    echo "❌ 核心文件不存在，請檢查項目結構"
    exit 1
fi

# 啟動 MCP 服務器
python3 core/mcp_server.py

echo "✅ PowerAutomation MCP 服務器已啟動"

