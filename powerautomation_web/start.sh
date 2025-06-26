#!/bin/bash

# PowerAutomation Web 啟動腳本
# 版本: 1.0.0
# 更新時間: 2024-06-25

echo "🚀 PowerAutomation Web 系統啟動中..."

# 檢查 Node.js 是否安裝
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安裝，請先安裝 Node.js"
    exit 1
fi

# 檢查 npm 是否安裝
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安裝，請先安裝 npm"
    exit 1
fi

# 獲取腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 工作目錄: $SCRIPT_DIR"

# 檢查項目結構
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 項目結構不完整，請檢查 backend 和 frontend 目錄"
    exit 1
fi

# 函數：檢查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  端口 $port 已被占用"
        return 1
    fi
    return 0
}

# 函數：啟動後端服務
start_backend() {
    echo "🔧 啟動後端服務..."
    cd "$SCRIPT_DIR/backend"
    
    # 檢查依賴是否安裝
    if [ ! -d "node_modules" ]; then
        echo "📦 安裝後端依賴..."
        npm install
        if [ $? -ne 0 ]; then
            echo "❌ 後端依賴安裝失敗"
            exit 1
        fi
    fi
    
    # 檢查端口
    if ! check_port 3001; then
        echo "❌ 後端端口 3001 被占用，請先關閉占用該端口的程序"
        exit 1
    fi
    
    # 啟動後端服務
    echo "🚀 啟動後端服務 (端口: 3001)..."
    npm start &
    BACKEND_PID=$!
    
    # 等待後端服務啟動
    sleep 3
    
    # 檢查後端服務是否正常啟動
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ 後端服務啟動失敗"
        exit 1
    fi
    
    echo "✅ 後端服務啟動成功 (PID: $BACKEND_PID)"
}

# 函數：啟動前端服務
start_frontend() {
    echo "🎨 啟動前端服務..."
    cd "$SCRIPT_DIR/frontend"
    
    # 檢查依賴是否安裝
    if [ ! -d "node_modules" ]; then
        echo "📦 安裝前端依賴..."
        npm install
        if [ $? -ne 0 ]; then
            echo "❌ 前端依賴安裝失敗"
            exit 1
        fi
    fi
    
    # 檢查端口
    if ! check_port 3000; then
        echo "⚠️  前端端口 3000 被占用，嘗試使用其他端口..."
        export PORT=3002
    fi
    
    # 啟動前端服務
    echo "🚀 啟動前端服務 (端口: ${PORT:-3000})..."
    npm run dev &
    FRONTEND_PID=$!
    
    # 等待前端服務啟動
    sleep 5
    
    # 檢查前端服務是否正常啟動
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ 前端服務啟動失敗"
        exit 1
    fi
    
    echo "✅ 前端服務啟動成功 (PID: $FRONTEND_PID)"
}

# 函數：優雅關閉服務
cleanup() {
    echo ""
    echo "🛑 正在關閉服務..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ 後端服務已關閉"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ 前端服務已關閉"
    fi
    
    echo "👋 PowerAutomation Web 系統已關閉"
    exit 0
}

# 設置信號處理
trap cleanup SIGINT SIGTERM

# 解析命令行參數
case "${1:-all}" in
    "backend")
        start_backend
        echo "🎯 僅啟動後端服務，按 Ctrl+C 停止"
        wait $BACKEND_PID
        ;;
    "frontend")
        start_frontend
        echo "🎯 僅啟動前端服務，按 Ctrl+C 停止"
        wait $FRONTEND_PID
        ;;
    "all"|"")
        start_backend
        start_frontend
        
        echo ""
        echo "🎉 PowerAutomation Web 系統啟動完成！"
        echo ""
        echo "📍 訪問地址:"
        echo "   前端: http://localhost:${PORT:-3000}"
        echo "   後端: http://localhost:3001"
        echo ""
        echo "🔑 測試賬號:"
        echo "   管理員: admin_qIFdydy7h_cZcop7uGNT73JRhjXQblHgWaRoDJMMz4U"
        echo "   開發者: dev_WqV-Kud9zmBOv_J_BtvMDJ5ZiPzibZR77o9mv-77Phg"
        echo "   用戶:   user_Bx5z5aQbofp1fS1bNaXF-DTFnV_6X_iu6n7-7VTxi5k"
        echo ""
        echo "📖 使用說明:"
        echo "   - 選擇用戶類型進行登錄"
        echo "   - 管理員和開發者使用 API Key 登錄"
        echo "   - 普通用戶可使用郵箱或 OAuth 登錄"
        echo ""
        echo "🛑 按 Ctrl+C 停止所有服務"
        
        # 等待服務運行
        wait
        ;;
    *)
        echo "使用方法: $0 [all|backend|frontend]"
        echo "  all      - 啟動前後端服務 (默認)"
        echo "  backend  - 僅啟動後端服務"
        echo "  frontend - 僅啟動前端服務"
        exit 1
        ;;
esac

