#!/bin/bash

echo "🚀 安裝 PowerAutomation Local MCP Adapter..."

# 檢查 Python 版本
python3 --version || {
    echo "❌ Python 3 未安裝，請先安裝 Python 3.8+"
    exit 1
}

# 創建虛擬環境
echo "📦 創建虛擬環境..."
python3 -m venv powerautomation_env
source powerautomation_env/bin/activate

# 安裝依賴
echo "📥 安裝依賴包..."
pip install --upgrade pip
pip install -r requirements.txt

# 安裝 Playwright 瀏覽器
echo "🌐 安裝 Playwright 瀏覽器..."
playwright install chromium

# 運行測試
echo "🧪 運行基本測試..."
python3 basic_test.py

echo "✅ 安裝完成！"
echo "使用方法:"
echo "  source powerautomation_env/bin/activate"
echo "  python3 powerautomation_local_mcp.py"
