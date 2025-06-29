#!/bin/bash

# AIWeb + SmartUI 停止脚本
# PowerAutomation Local 组件

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOGS_DIR="$SCRIPT_DIR/logs"

echo "🛑 停止 AIWeb + SmartUI 服务..."

# 停止所有服务
for service in smartui_backend smartui_frontend aiweb_frontend; do
    if [ -f "$LOGS_DIR/${service}.pid" ]; then
        pid=$(cat "$LOGS_DIR/${service}.pid")
        if kill "$pid" 2>/dev/null; then
            echo "✅ 已停止 $service (PID: $pid)"
        else
            echo "⚠️ 无法停止 $service (PID: $pid)"
        fi
        rm -f "$LOGS_DIR/${service}.pid"
    else
        echo "ℹ️ $service 未运行"
    fi
done

# 强制清理残留进程
echo "🧹 清理残留进程..."
pkill -f "smartui_mcp.py" 2>/dev/null || true
pkill -f "http.server.*3000" 2>/dev/null || true
pkill -f "http.server.*8081" 2>/dev/null || true

echo "✅ 所有服务已停止"

