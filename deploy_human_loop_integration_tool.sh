#!/bin/bash

# Human Loop Integration Tool 部署腳本
# 作為獨立工具集成到PowerAutomation，不修改AICore核心

set -e

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

# 檢查是否在正確的目錄
check_directory() {
    if [[ ! -d "PowerAutomation" ]]; then
        log_error "請在aicore0624項目根目錄中運行此腳本"
        exit 1
    fi
    
    if [[ ! -d "PowerAutomation/tools" ]]; then
        log_info "創建PowerAutomation/tools目錄"
        mkdir -p PowerAutomation/tools
    fi
}

# 檢查Python環境
check_python() {
    log_info "檢查Python環境..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3未安裝，請先安裝Python3"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    required_version="3.8"
    
    if [[ $(echo "$python_version >= $required_version" | bc -l) -eq 0 ]]; then
        log_error "需要Python 3.8或更高版本，當前版本: $python_version"
        exit 1
    fi
    
    log_success "Python環境檢查通過: $(python3 --version)"
}

# 安裝依賴
install_dependencies() {
    log_info "安裝Human Loop Integration Tool依賴..."
    
    # 檢查是否有虛擬環境
    if [[ ! -d "venv" ]]; then
        log_info "創建Python虛擬環境..."
        python3 -m venv venv
    fi
    
    # 激活虛擬環境
    source venv/bin/activate
    
    # 升級pip
    pip install --upgrade pip
    
    # 安裝依賴
    cat > PowerAutomation/tools/requirements.txt << EOF
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
aiohttp>=3.9.0
pydantic>=2.5.0
sqlite3
asyncio
pathlib
typing
enum34
dataclasses
python-multipart
EOF
    
    pip install -r PowerAutomation/tools/requirements.txt
    
    log_success "依賴安裝完成"
}

# 創建啟動腳本
create_startup_scripts() {
    log_info "創建啟動腳本..."
    
    # 創建啟動腳本
    cat > PowerAutomation/tools/start_human_loop_integration.sh << 'EOF'
#!/bin/bash

# Human Loop Integration Tool 啟動腳本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "啟動Human Loop Integration Tool..."
echo "項目根目錄: $PROJECT_ROOT"
echo "工具目錄: $SCRIPT_DIR"

# 激活虛擬環境
if [[ -f "$PROJECT_ROOT/venv/bin/activate" ]]; then
    source "$PROJECT_ROOT/venv/bin/activate"
    echo "虛擬環境已激活"
else
    echo "警告: 未找到虛擬環境"
fi

# 切換到工具目錄
cd "$SCRIPT_DIR"

# 檢查配置文件
if [[ ! -f "human_loop_integration_config.json" ]]; then
    echo "警告: 配置文件不存在，將使用默認配置"
fi

# 啟動服務器
echo "啟動Human Loop Integration Tool API服務器..."
python3 human_loop_integration_server.py --host 0.0.0.0 --port 8098

EOF
    
    chmod +x PowerAutomation/tools/start_human_loop_integration.sh
    
    # 創建停止腳本
    cat > PowerAutomation/tools/stop_human_loop_integration.sh << 'EOF'
#!/bin/bash

# Human Loop Integration Tool 停止腳本

echo "停止Human Loop Integration Tool..."

# 查找並停止進程
PID=$(ps aux | grep "human_loop_integration_server.py" | grep -v grep | awk '{print $2}')

if [[ -n "$PID" ]]; then
    echo "找到進程 PID: $PID"
    kill -TERM $PID
    sleep 2
    
    # 檢查是否還在運行
    if ps -p $PID > /dev/null; then
        echo "強制停止進程..."
        kill -KILL $PID
    fi
    
    echo "Human Loop Integration Tool已停止"
else
    echo "Human Loop Integration Tool未運行"
fi

EOF
    
    chmod +x PowerAutomation/tools/stop_human_loop_integration.sh
    
    # 創建狀態檢查腳本
    cat > PowerAutomation/tools/check_human_loop_integration.sh << 'EOF'
#!/bin/bash

# Human Loop Integration Tool 狀態檢查腳本

echo "檢查Human Loop Integration Tool狀態..."

# 檢查進程
PID=$(ps aux | grep "human_loop_integration_server.py" | grep -v grep | awk '{print $2}')

if [[ -n "$PID" ]]; then
    echo "✅ Human Loop Integration Tool正在運行 (PID: $PID)"
    
    # 檢查API健康狀態
    echo "檢查API健康狀態..."
    if command -v curl &> /dev/null; then
        response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8098/api/health)
        if [[ "$response" == "200" ]]; then
            echo "✅ API健康檢查通過"
        else
            echo "❌ API健康檢查失敗 (HTTP $response)"
        fi
    else
        echo "⚠️  curl未安裝，無法檢查API狀態"
    fi
    
    # 顯示服務信息
    echo ""
    echo "服務信息:"
    echo "  - API地址: http://localhost:8098"
    echo "  - 健康檢查: http://localhost:8098/api/health"
    echo "  - API文檔: http://localhost:8098/docs"
    echo "  - 配置文件: PowerAutomation/tools/human_loop_integration_config.json"
    echo "  - 數據庫: human_loop_integration.db"
    
else
    echo "❌ Human Loop Integration Tool未運行"
    echo ""
    echo "啟動命令: ./PowerAutomation/tools/start_human_loop_integration.sh"
fi

EOF
    
    chmod +x PowerAutomation/tools/check_human_loop_integration.sh
    
    log_success "啟動腳本創建完成"
}

# 創建systemd服務文件（可選）
create_systemd_service() {
    log_info "創建systemd服務文件..."
    
    USER=$(whoami)
    PROJECT_PATH=$(pwd)
    
    cat > PowerAutomation/tools/human-loop-integration.service << EOF
[Unit]
Description=Human Loop Integration Tool for PowerAutomation
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_PATH/PowerAutomation/tools
Environment=PATH=$PROJECT_PATH/venv/bin
ExecStart=$PROJECT_PATH/venv/bin/python human_loop_integration_server.py --host 0.0.0.0 --port 8098
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    log_info "systemd服務文件已創建: PowerAutomation/tools/human-loop-integration.service"
    log_info "要安裝為系統服務，請運行:"
    log_info "  sudo cp PowerAutomation/tools/human-loop-integration.service /etc/systemd/system/"
    log_info "  sudo systemctl daemon-reload"
    log_info "  sudo systemctl enable human-loop-integration"
    log_info "  sudo systemctl start human-loop-integration"
}

# 創建集成示例
create_integration_examples() {
    log_info "創建集成示例..."
    
    mkdir -p PowerAutomation/tools/examples
    
    # Python集成示例
    cat > PowerAutomation/tools/examples/integration_example.py << 'EOF'
#!/usr/bin/env python3
"""
Human Loop Integration Tool 集成示例
展示如何在PowerAutomation中使用Human Loop Integration Tool
"""

import asyncio
import aiohttp
import json
from datetime import datetime

class PowerAutomationIntegration:
    """PowerAutomation與Human Loop Integration Tool的集成類"""
    
    def __init__(self, human_loop_api_url="http://localhost:8098"):
        self.human_loop_api_url = human_loop_api_url
    
    async def execute_workflow_with_human_loop(self, workflow_data):
        """執行工作流，使用Human Loop Integration Tool進行智能路由"""
        
        async with aiohttp.ClientSession() as session:
            # 發送工作流到Human Loop Integration Tool
            async with session.post(
                f"{self.human_loop_api_url}/api/workflows",
                json=workflow_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"工作流處理結果: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    return result
                else:
                    error_text = await response.text()
                    print(f"錯誤: {response.status} - {error_text}")
                    return None
    
    async def check_service_health(self):
        """檢查Human Loop Integration Tool服務健康狀態"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.human_loop_api_url}/api/health"
                ) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        print(f"服務健康狀態: {json.dumps(health_data, indent=2, ensure_ascii=False)}")
                        return True
                    else:
                        print(f"健康檢查失敗: {response.status}")
                        return False
        except Exception as e:
            print(f"無法連接到Human Loop Integration Tool: {str(e)}")
            return False

async def main():
    """主函數 - 示例用法"""
    
    # 創建集成實例
    integration = PowerAutomationIntegration()
    
    # 檢查服務健康狀態
    print("=== 檢查服務健康狀態 ===")
    health_ok = await integration.check_service_health()
    
    if not health_ok:
        print("Human Loop Integration Tool服務未運行，請先啟動服務")
        return
    
    # 示例工作流1: 簡單部署（應該自動執行）
    print("\n=== 示例1: 簡單部署工作流 ===")
    simple_workflow = {
        "title": "簡單VSIX部署",
        "description": "在開發環境部署PowerAutomation VSIX",
        "parameters": {
            "target": "vscode",
            "version": "3.0.0",
            "environment": "development"
        },
        "metadata": {
            "workflow_type": "deployment",
            "environment": "development",
            "operation_type": "deploy",
            "data_sensitivity": "low",
            "system_impact": "low"
        }
    }
    
    await integration.execute_workflow_with_human_loop(simple_workflow)
    
    # 示例工作流2: 生產環境部署（應該需要人工介入）
    print("\n=== 示例2: 生產環境部署工作流 ===")
    production_workflow = {
        "title": "生產環境VSIX部署",
        "description": "在生產環境部署PowerAutomation VSIX",
        "parameters": {
            "target": "vscode",
            "version": "3.0.0",
            "environment": "production"
        },
        "metadata": {
            "workflow_type": "deployment",
            "environment": "production",
            "operation_type": "deploy",
            "data_sensitivity": "medium",
            "system_impact": "high",
            "dependencies": ["vscode", "python", "mcp"]
        }
    }
    
    await integration.execute_workflow_with_human_loop(production_workflow)
    
    # 示例工作流3: 複雜集成（應該需要專家諮詢）
    print("\n=== 示例3: 複雜集成工作流 ===")
    complex_workflow = {
        "title": "複雜系統集成",
        "description": "集成多個MCP組件和外部API",
        "parameters": {
            "components": ["mcp1", "mcp2", "api1", "api2"],
            "integration_type": "full",
            "environment": "staging"
        },
        "metadata": {
            "workflow_type": "system_integration",
            "environment": "staging",
            "operation_type": "configure",
            "data_sensitivity": "high",
            "system_impact": "medium",
            "dependencies": ["mcp", "api", "database", "cache"]
        }
    }
    
    await integration.execute_workflow_with_human_loop(complex_workflow)

if __name__ == "__main__":
    asyncio.run(main())
EOF
    
    # Shell集成示例
    cat > PowerAutomation/tools/examples/integration_example.sh << 'EOF'
#!/bin/bash

# Human Loop Integration Tool Shell集成示例

HUMAN_LOOP_API="http://localhost:8098"

# 檢查服務狀態
check_service() {
    echo "檢查Human Loop Integration Tool服務狀態..."
    
    if command -v curl &> /dev/null; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$HUMAN_LOOP_API/api/health")
        if [[ "$response" == "200" ]]; then
            echo "✅ 服務正常運行"
            return 0
        else
            echo "❌ 服務異常 (HTTP $response)"
            return 1
        fi
    else
        echo "❌ curl未安裝"
        return 1
    fi
}

# 創建工作流
create_workflow() {
    local title="$1"
    local description="$2"
    local environment="$3"
    
    echo "創建工作流: $title"
    
    workflow_data=$(cat << EOF
{
    "title": "$title",
    "description": "$description",
    "parameters": {
        "target": "vscode",
        "version": "3.0.0",
        "environment": "$environment"
    },
    "metadata": {
        "workflow_type": "deployment",
        "environment": "$environment",
        "operation_type": "deploy",
        "data_sensitivity": "low",
        "system_impact": "medium"
    }
}
EOF
)
    
    if command -v curl &> /dev/null; then
        response=$(curl -s -X POST "$HUMAN_LOOP_API/api/workflows" \
            -H "Content-Type: application/json" \
            -d "$workflow_data")
        
        echo "工作流結果:"
        echo "$response" | python3 -m json.tool
    else
        echo "❌ curl未安裝，無法發送請求"
    fi
}

# 主函數
main() {
    echo "=== Human Loop Integration Tool Shell集成示例 ==="
    
    # 檢查服務
    if ! check_service; then
        echo "請先啟動Human Loop Integration Tool服務"
        echo "運行: ./PowerAutomation/tools/start_human_loop_integration.sh"
        exit 1
    fi
    
    echo ""
    echo "=== 創建示例工作流 ==="
    
    # 開發環境部署
    create_workflow "開發環境部署" "在開發環境部署VSIX" "development"
    
    echo ""
    echo "=== 獲取決策歷史 ==="
    
    if command -v curl &> /dev/null; then
        curl -s "$HUMAN_LOOP_API/api/decisions/history?limit=5" | python3 -m json.tool
    fi
    
    echo ""
    echo "=== 獲取統計信息 ==="
    
    if command -v curl &> /dev/null; then
        curl -s "$HUMAN_LOOP_API/api/stats" | python3 -m json.tool
    fi
}

main "$@"
EOF
    
    chmod +x PowerAutomation/tools/examples/integration_example.py
    chmod +x PowerAutomation/tools/examples/integration_example.sh
    
    log_success "集成示例創建完成"
}

# 運行測試
run_tests() {
    log_info "運行Human Loop Integration Tool測試..."
    
    # 激活虛擬環境
    source venv/bin/activate
    
    # 切換到工具目錄
    cd PowerAutomation/tools
    
    # 運行基本測試
    python3 -c "
import asyncio
from human_loop_integration_tool import HumanLoopIntegrationTool, WorkflowContext
from datetime import datetime

async def test():
    print('測試Human Loop Integration Tool...')
    
    # 創建工具實例
    tool = HumanLoopIntegrationTool()
    print('✅ 工具初始化成功')
    
    # 創建測試工作流
    context = WorkflowContext(
        workflow_id='test_001',
        title='測試工作流',
        description='基本功能測試',
        parameters={'test': True},
        metadata={'workflow_type': 'testing', 'environment': 'development'},
        created_at=datetime.now()
    )
    
    # 處理工作流
    result = await tool.process_workflow(context)
    print(f'✅ 工作流處理成功: {result[\"status\"]}')
    
    print('✅ 所有測試通過')

asyncio.run(test())
"
    
    if [[ $? -eq 0 ]]; then
        log_success "測試通過"
    else
        log_error "測試失敗"
        return 1
    fi
    
    cd ../..
}

# 主部署流程
main() {
    echo "=========================================="
    echo "Human Loop Integration Tool 部署腳本"
    echo "版本: 1.0.0"
    echo "=========================================="
    echo ""
    
    log_info "開始部署Human Loop Integration Tool..."
    
    # 檢查目錄
    check_directory
    
    # 檢查Python環境
    check_python
    
    # 安裝依賴
    install_dependencies
    
    # 創建啟動腳本
    create_startup_scripts
    
    # 創建systemd服務文件
    create_systemd_service
    
    # 創建集成示例
    create_integration_examples
    
    # 運行測試
    run_tests
    
    echo ""
    echo "=========================================="
    log_success "Human Loop Integration Tool 部署完成！"
    echo "=========================================="
    echo ""
    echo "📋 部署摘要:"
    echo "  ✅ 工具文件: PowerAutomation/tools/human_loop_integration_tool.py"
    echo "  ✅ API服務器: PowerAutomation/tools/human_loop_integration_server.py"
    echo "  ✅ 配置文件: PowerAutomation/tools/human_loop_integration_config.json"
    echo "  ✅ 啟動腳本: PowerAutomation/tools/start_human_loop_integration.sh"
    echo "  ✅ 停止腳本: PowerAutomation/tools/stop_human_loop_integration.sh"
    echo "  ✅ 狀態檢查: PowerAutomation/tools/check_human_loop_integration.sh"
    echo "  ✅ 集成示例: PowerAutomation/tools/examples/"
    echo ""
    echo "🚀 快速開始:"
    echo "  1. 啟動服務: ./PowerAutomation/tools/start_human_loop_integration.sh"
    echo "  2. 檢查狀態: ./PowerAutomation/tools/check_human_loop_integration.sh"
    echo "  3. 運行示例: python3 PowerAutomation/tools/examples/integration_example.py"
    echo "  4. API文檔: http://localhost:8098/docs"
    echo ""
    echo "🔧 集成方式:"
    echo "  - 作為獨立工具運行，不修改AICore核心"
    echo "  - 通過HTTP API與PowerAutomation集成"
    echo "  - 支持智能路由決策和Human Loop MCP集成"
    echo "  - 提供專家系統和深度測試框架"
    echo ""
    echo "📖 更多信息請查看: PowerAutomation/tools/README.md"
}

# 執行主函數
main "$@"

