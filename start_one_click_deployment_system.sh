#!/bin/bash

# PowerAutomation 一键部署系统启动脚本
# 启动整合了部署协调功能的主平台系统

echo "🚀 启动 PowerAutomation 一键部署系统..."
echo "=================================================="

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python3"
    exit 1
fi

# 检查必要的依赖
echo "📦 检查依赖包..."
python3 -c "import flask, aiohttp, paramiko" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ 缺少必要依赖，正在安装..."
    pip3 install flask flask-cors aiohttp paramiko
fi

# 设置环境变量
export AUTO_DEPLOY_ON_STARTUP=false  # 默认不自动部署
export PYTHONPATH="${PYTHONPATH}:$(pwd)/PowerAutomation/components"

# 检查配置文件
CONFIG_FILE="PowerAutomation/components/deployment_mcp/remote_environments.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 配置文件不存在: $CONFIG_FILE"
    echo "请确保部署环境配置文件存在"
    exit 1
fi

echo "✅ 配置文件检查通过"

# 启动主平台系统
echo "🌐 启动 PowerAutomation 一键部署主平台..."
echo "   访问地址: http://localhost:8080"
echo "   API 文档: http://localhost:8080/api/system/status"
echo ""
echo "📋 可用的 API 端点:"
echo "   - POST /api/deployment/one-click     # 触发一键部署"
echo "   - GET  /api/deployment/status        # 获取部署状态"
echo "   - GET  /api/deployment/history       # 获取部署历史"
echo "   - GET  /api/deployment/environments  # 获取环境配置"
echo "   - POST /api/deployment/test-connection # 测试部署连接"
echo "   - GET  /api/system/status            # 系统状态"
echo "   - GET  /api/system/health            # 健康检查"
echo ""
echo "🔑 API Key 信息将在启动后显示"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=================================================="

# 启动服务
cd PowerAutomation/servers
python3 fully_integrated_system_with_deployment.py

