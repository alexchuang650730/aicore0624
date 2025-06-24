#!/bin/bash

# 激活虛擬環境
if [ -d "powerautomation_env" ]; then
    source powerautomation_env/bin/activate
else
    echo "❌ 虛擬環境不存在，請先運行 install.sh"
    exit 1
fi

# 啟動服務
echo "🚀 啟動 PowerAutomation Local MCP Adapter..."
python3 powerautomation_local_mcp.py
