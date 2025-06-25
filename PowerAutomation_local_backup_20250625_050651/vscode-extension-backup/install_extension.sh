#!/bin/bash

echo "🔌 安裝 PowerAutomation VSCode 擴展..."

# 檢查 Node.js
node --version || {
    echo "❌ Node.js 未安裝，請先安裝 Node.js 16+"
    exit 1
}

# 安裝依賴
echo "📦 安裝依賴..."
npm install

# 編譯 TypeScript
echo "🔨 編譯 TypeScript..."
npm run compile

# 安裝 vsce 工具
echo "🛠️ 安裝 vsce 工具..."
npm install -g vsce

# 打包擴展
echo "📦 打包擴展..."
vsce package

# 安裝擴展
echo "🔌 安裝擴展到 VSCode..."
code --install-extension *.vsix

echo "✅ VSCode 擴展安裝完成！"
