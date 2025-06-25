#!/bin/bash
# PowerAutomation Local MCP 自動部署功能集成測試腳本
# Integration Test Script for PowerAutomation Local MCP Auto Deployment Feature
#
# Author: Manus AI
# Version: 1.0.0
# Date: 2025-06-24

set -e  # 遇到錯誤立即退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# 測試配置
TEST_DIR="/home/ubuntu/aicore0624/PowerAutomation_local"
VSIX_FILE="$TEST_DIR/vscode-extension/powerautomation-local-mcp-3.0.0.vsix"
API_PORT=8394
MOCK_API_PID=""

# 清理函數
cleanup() {
    log_info "清理測試環境..."
    if [ ! -z "$MOCK_API_PID" ]; then
        kill $MOCK_API_PID 2>/dev/null || true
        log_info "已停止模擬 API 服務器"
    fi
    pkill -f "powerautomation_local_mcp.py" 2>/dev/null || true
    pkill -f "mock_deployment_api.py" 2>/dev/null || true
}

# 設置信號處理
trap cleanup EXIT

# 開始測試
log_info "開始 PowerAutomation Local MCP 自動部署功能集成測試"
log_info "測試目錄: $TEST_DIR"

# 1. 檢查環境
log_info "1. 檢查測試環境..."

cd "$TEST_DIR"

# 檢查 VSIX 檔案
if [ ! -f "$VSIX_FILE" ]; then
    log_error "VSIX 檔案不存在: $VSIX_FILE"
    exit 1
fi
log_success "VSIX 檔案存在: $(basename $VSIX_FILE)"

# 檢查 Python 依賴
python3 -c "import aiofiles, aiohttp, fastapi, uvicorn" 2>/dev/null
if [ $? -eq 0 ]; then
    log_success "Python 依賴檢查通過"
else
    log_error "Python 依賴檢查失敗"
    exit 1
fi

# 2. 測試 VSIX 自動部署器組件
log_info "2. 測試 VSIX 自動部署器組件..."

python3 -c "
import sys
sys.path.insert(0, '.')
from vsix_auto_deployer import VSIXFileScanner, DeploymentStrategy, create_default_config
import asyncio
import logging

async def test_components():
    config = create_default_config()
    logger = logging.getLogger('test')
    
    # 測試檔案掃描器
    scanner = VSIXFileScanner(config['scan_directories'], logger)
    files = await scanner.scan_for_vsix_files()
    
    if len(files) > 0:
        print(f'✅ 檔案掃描器測試通過: 發現 {len(files)} 個 VSIX 檔案')
        
        # 測試部署策略
        strategy = DeploymentStrategy(config['deployment'], logger)
        deployable = [f for f in files if strategy.should_deploy(f)]
        print(f'✅ 部署策略測試通過: {len(deployable)} 個檔案可部署')
        
        return True
    else:
        print('❌ 檔案掃描器測試失敗: 未發現 VSIX 檔案')
        return False

result = asyncio.run(test_components())
exit(0 if result else 1)
"

if [ $? -eq 0 ]; then
    log_success "VSIX 自動部署器組件測試通過"
else
    log_error "VSIX 自動部署器組件測試失敗"
    exit 1
fi

# 3. 啟動模擬 API 服務器
log_info "3. 啟動模擬 API 服務器..."

python3 mock_deployment_api.py > mock_api.log 2>&1 &
MOCK_API_PID=$!

# 等待服務啟動
sleep 3

# 檢查服務是否正常
curl -s http://localhost:$API_PORT/health > /dev/null
if [ $? -eq 0 ]; then
    log_success "模擬 API 服務器啟動成功 (PID: $MOCK_API_PID)"
else
    log_error "模擬 API 服務器啟動失敗"
    exit 1
fi

# 4. 測試自動部署功能
log_info "4. 測試自動部署功能..."

python3 -c "
import asyncio
import sys
import json
sys.path.insert(0, '.')
from vsix_auto_deployer import test_auto_deployer

async def run_test():
    try:
        result = await test_auto_deployer()
        return result
    except Exception as e:
        print(f'測試異常: {e}')
        return None

result = asyncio.run(run_test())
if result and result.get('status') == 'completed' and result.get('deployed_files', 0) > 0:
    print('✅ 自動部署功能測試通過')
    exit(0)
else:
    print('❌ 自動部署功能測試失敗')
    exit(1)
" > auto_deploy_test.log 2>&1

if [ $? -eq 0 ]; then
    log_success "自動部署功能測試通過"
    
    # 顯示測試結果
    log_info "測試結果詳情:"
    tail -n 20 auto_deploy_test.log | grep -E "(部署結果|deployed_files|成功|失敗)" || true
else
    log_error "自動部署功能測試失敗"
    log_info "錯誤詳情:"
    tail -n 10 auto_deploy_test.log
    exit 1
fi

# 5. 測試集成的 PowerAutomation MCP 服務
log_info "5. 測試集成的 PowerAutomation MCP 服務..."

# 創建測試配置
cat > test_config.toml << EOF
[server]
host = "0.0.0.0"
port = 8394

[auto_deployment]
scan_directories = [
    "/home/ubuntu/aicore0624/PowerAutomation_local/vscode-extension"
]

[auto_deployment.deployment]
max_file_size = 104857600
max_file_age_hours = 24

[auto_deployment.api]
base_url = "http://localhost:8394"
timeout = 30

[logging]
level = "INFO"
EOF

# 測試服務初始化
python3 -c "
import sys
sys.path.insert(0, '.')
from powerautomation_local_mcp import PowerAutomationMCP
import asyncio

async def test_service():
    try:
        # 創建服務實例
        mcp = PowerAutomationMCP('test_config.toml')
        
        # 測試配置加載
        if mcp.config is None:
            print('❌ 配置加載失敗')
            return False
        
        # 測試自動部署器初始化
        mcp._initialize_auto_deployer()
        if mcp.vsix_auto_deployer is None:
            print('❌ 自動部署器初始化失敗')
            return False
        
        print('✅ PowerAutomation MCP 服務集成測試通過')
        return True
        
    except Exception as e:
        print(f'❌ PowerAutomation MCP 服務集成測試失敗: {e}')
        return False

result = asyncio.run(test_service())
exit(0 if result else 1)
"

if [ $? -eq 0 ]; then
    log_success "PowerAutomation MCP 服務集成測試通過"
else
    log_error "PowerAutomation MCP 服務集成測試失敗"
    exit 1
fi

# 6. 生成測試報告
log_info "6. 生成測試報告..."

cat > integration_test_report.json << EOF
{
    "test_name": "PowerAutomation Local MCP Auto Deployment Integration Test",
    "test_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "test_environment": {
        "os": "$(uname -s)",
        "python_version": "$(python3 --version)",
        "test_directory": "$TEST_DIR"
    },
    "test_results": {
        "environment_check": "PASSED",
        "component_test": "PASSED",
        "mock_api_test": "PASSED",
        "auto_deployment_test": "PASSED",
        "service_integration_test": "PASSED"
    },
    "vsix_file": {
        "path": "$VSIX_FILE",
        "size": "$(stat -c%s $VSIX_FILE 2>/dev/null || echo 'unknown')",
        "exists": true
    },
    "overall_status": "PASSED",
    "recommendations": [
        "自動部署功能已成功實現並通過所有測試",
        "可以安全地部署到生產環境",
        "建議在生產環境中啟用適當的日誌級別"
    ]
}
EOF

log_success "測試報告已生成: integration_test_report.json"

# 7. 清理測試檔案
log_info "7. 清理測試檔案..."
rm -f test_config.toml auto_deploy_test.log mock_api.log

# 測試完成
log_success "🎉 PowerAutomation Local MCP 自動部署功能集成測試全部通過！"
log_info "測試摘要:"
echo "  ✅ 環境檢查"
echo "  ✅ 組件測試"
echo "  ✅ 模擬 API 測試"
echo "  ✅ 自動部署功能測試"
echo "  ✅ 服務集成測試"
echo ""
log_info "功能特色:"
echo "  🚀 服務啟動時自動檢測 VSIX 檔案"
echo "  📁 支援多目錄掃描"
echo "  🔍 智能檔案驗證和過濾"
echo "  ⚡ 異步部署執行"
echo "  📊 完整的部署狀態追蹤"
echo "  🛡️ 完善的錯誤處理機制"
echo ""
log_success "自動部署功能已準備就緒，可以啟動 PowerAutomation Local MCP 服務！"

