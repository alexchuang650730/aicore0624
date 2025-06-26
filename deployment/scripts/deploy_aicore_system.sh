#!/bin/bash

# AICore Human-in-the-Loop Integration System 部署腳本
# 版本: 1.0.0
# 作者: AICore Team

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

# 檢查系統要求
check_system_requirements() {
    log_info "檢查系統要求..."
    
    # 檢查Python版本
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安裝"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    required_version="3.8"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        log_error "需要Python 3.8或更高版本，當前版本: $python_version"
        exit 1
    fi
    
    log_success "Python版本檢查通過: $python_version"
    
    # 檢查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安裝"
        exit 1
    fi
    
    # 檢查Git
    if ! command -v git &> /dev/null; then
        log_error "Git 未安裝"
        exit 1
    fi
    
    log_success "系統要求檢查完成"
}

# 安裝Python依賴
install_dependencies() {
    log_info "安裝Python依賴..."
    
    # 創建虛擬環境
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "虛擬環境創建完成"
    fi
    
    # 激活虛擬環境
    source venv/bin/activate
    
    # 升級pip
    pip install --upgrade pip
    
    # 安裝依賴
    cat > requirements.txt << EOF
aiohttp>=3.8.0
aiofiles>=0.8.0
pyyaml>=6.0
asyncio-mqtt>=0.11.0
psutil>=5.9.0
numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.0.0
matplotlib>=3.5.0
seaborn>=0.11.0
plotly>=5.0.0
fastapi>=0.68.0
uvicorn>=0.15.0
websockets>=10.0
redis>=4.0.0
sqlalchemy>=1.4.0
alembic>=1.7.0
pytest>=6.2.0
pytest-asyncio>=0.18.0
coverage>=6.0
black>=21.0.0
flake8>=4.0.0
mypy>=0.910
EOF
    
    pip install -r requirements.txt
    
    log_success "Python依賴安裝完成"
}

# 設置配置文件
setup_configuration() {
    log_info "設置配置文件..."
    
    # 創建配置目錄
    mkdir -p config
    mkdir -p logs
    mkdir -p data
    mkdir -p tests
    
    # 創建主配置文件
    cat > config/aicore_config.yaml << EOF
system:
  name: "AICore Human-in-the-Loop System"
  version: "1.0.0"
  environment: "production"
  debug: false

components:
  router:
    enabled: true
    confidence_threshold: 0.7
    fallback_strategy: "human_intervention"
  
  expert_system:
    enabled: true
    default_timeout: 1800
    max_concurrent_consultations: 5
  
  testing_framework:
    enabled: true
    test_data_path: "data/test_data"
    report_format: "json"
  
  optimization_system:
    enabled: true
    learning_rate: 0.01
    optimization_interval: 3600
    model_save_path: "data/models"
  
  human_loop_mcp:
    enabled: true
    url: "http://localhost:8096"
    timeout: 300
    retry_count: 3

workflows:
  default_timeout: 3600
  max_concurrent: 10
  retry_count: 3
  priority_levels: [1, 2, 3, 4, 5]

monitoring:
  health_check_interval: 60
  metrics_collection_interval: 30
  log_level: "INFO"
  log_rotation: true
  max_log_size: "100MB"

security:
  api_key_required: false
  rate_limiting: true
  max_requests_per_minute: 100
  cors_enabled: true
  allowed_origins: ["*"]

api:
  enabled: true
  host: "0.0.0.0"
  port: 8098
  workers: 4

database:
  url: "sqlite:///data/aicore.db"
  echo: false
  pool_size: 10

redis:
  enabled: false
  url: "redis://localhost:6379/0"

startup:
  run_tests: true
  load_test_data: true
  initialize_models: true
EOF
    
    log_success "配置文件設置完成"
}

# 初始化數據庫
initialize_database() {
    log_info "初始化數據庫..."
    
    # 創建數據庫初始化腳本
    cat > init_database.py << EOF
#!/usr/bin/env python3
import asyncio
import sqlite3
from pathlib import Path

async def init_database():
    """初始化SQLite數據庫"""
    db_path = Path("data/aicore.db")
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 創建工作流表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflows (
            id TEXT PRIMARY KEY,
            workflow_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            execution_time REAL,
            result TEXT
        )
    ''')
    
    # 創建路由決策表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS routing_decisions (
            id TEXT PRIMARY KEY,
            workflow_id TEXT,
            decision_type TEXT NOT NULL,
            confidence REAL NOT NULL,
            reasoning TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (workflow_id) REFERENCES workflows (id)
        )
    ''')
    
    # 創建專家諮詢表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expert_consultations (
            id TEXT PRIMARY KEY,
            workflow_id TEXT,
            expert_type TEXT NOT NULL,
            status TEXT NOT NULL,
            request_data TEXT,
            response_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (workflow_id) REFERENCES workflows (id)
        )
    ''')
    
    # 創建人工介入表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS human_interventions (
            id TEXT PRIMARY KEY,
            workflow_id TEXT,
            session_id TEXT,
            interaction_type TEXT NOT NULL,
            status TEXT NOT NULL,
            request_data TEXT,
            response_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (workflow_id) REFERENCES workflows (id)
        )
    ''')
    
    # 創建性能指標表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_type TEXT NOT NULL,
            value REAL NOT NULL,
            context TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 創建系統事件表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            event_data TEXT,
            severity TEXT DEFAULT 'INFO',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("數據庫初始化完成")

if __name__ == "__main__":
    asyncio.run(init_database())
EOF
    
    python3 init_database.py
    log_success "數據庫初始化完成"
}

# 創建測試數據
create_test_data() {
    log_info "創建測試數據..."
    
    mkdir -p data/test_data
    
    # 創建測試工作流數據
    cat > data/test_data/test_workflows.json << EOF
[
    {
        "workflow_type": "deployment",
        "title": "Production Deployment",
        "description": "Deploy application to production environment",
        "parameters": {
            "environment": "production",
            "version": "2.1.0",
            "rollback_enabled": true
        },
        "metadata": {
            "complexity": "high",
            "risk_level": "medium",
            "estimated_duration": 1800
        }
    },
    {
        "workflow_type": "configuration",
        "title": "Database Configuration Update",
        "description": "Update database connection settings",
        "parameters": {
            "database": "primary",
            "connection_pool_size": 20,
            "timeout": 30
        },
        "metadata": {
            "complexity": "low",
            "risk_level": "low",
            "estimated_duration": 300
        }
    },
    {
        "workflow_type": "maintenance",
        "title": "System Maintenance",
        "description": "Perform routine system maintenance",
        "parameters": {
            "maintenance_type": "routine",
            "downtime_required": false
        },
        "metadata": {
            "complexity": "medium",
            "risk_level": "low",
            "estimated_duration": 900
        }
    }
]
EOF
    
    log_success "測試數據創建完成"
}

# 設置服務
setup_services() {
    log_info "設置系統服務..."
    
    # 創建啟動腳本
    cat > start_aicore.sh << 'EOF'
#!/bin/bash

# AICore系統啟動腳本

# 激活虛擬環境
source venv/bin/activate

# 設置環境變量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export AICORE_CONFIG_PATH="config/aicore_config.yaml"
export AICORE_LOG_LEVEL="INFO"

# 啟動系統
echo "啟動AICore Human-in-the-Loop Integration System..."
python3 aicore_master_system.py
EOF
    
    chmod +x start_aicore.sh
    
    # 創建停止腳本
    cat > stop_aicore.sh << 'EOF'
#!/bin/bash

# AICore系統停止腳本

echo "停止AICore系統..."

# 查找並終止AICore進程
pkill -f "aicore_master_system.py"

echo "AICore系統已停止"
EOF
    
    chmod +x stop_aicore.sh
    
    # 創建狀態檢查腳本
    cat > check_aicore_status.sh << 'EOF'
#!/bin/bash

# AICore系統狀態檢查腳本

echo "檢查AICore系統狀態..."

# 檢查進程
if pgrep -f "aicore_master_system.py" > /dev/null; then
    echo "✅ AICore系統正在運行"
    
    # 檢查API健康狀態
    if command -v curl &> /dev/null; then
        if curl -s http://localhost:8098/api/health > /dev/null; then
            echo "✅ API服務正常"
        else
            echo "❌ API服務異常"
        fi
    fi
else
    echo "❌ AICore系統未運行"
fi

# 檢查日誌文件
if [ -f "logs/aicore_system.log" ]; then
    echo "📋 最近的日誌條目:"
    tail -5 logs/aicore_system.log
fi
EOF
    
    chmod +x check_aicore_status.sh
    
    log_success "系統服務設置完成"
}

# 運行測試
run_tests() {
    log_info "運行系統測試..."
    
    # 激活虛擬環境
    source venv/bin/activate
    
    # 創建簡單的測試腳本
    cat > test_system.py << EOF
#!/usr/bin/env python3
import asyncio
import json
import sys
from pathlib import Path

# 添加當前目錄到Python路徑
sys.path.insert(0, str(Path(__file__).parent))

async def test_system_components():
    """測試系統組件"""
    print("🧪 開始系統組件測試...")
    
    try:
        # 測試導入
        from aicore_dynamic_router import AICoreDynamicRouter
        from expert_invocation_system import ExpertInvocationSystem
        from deep_testing_framework import DeepTestingFramework
        from incremental_optimization_system import IncrementalOptimizationSystem
        from aicore_master_system import AICoreMasterController
        
        print("✅ 所有模組導入成功")
        
        # 測試路由器
        router = AICoreDynamicRouter()
        print("✅ 動態路由器初始化成功")
        
        # 測試專家系統
        expert_system = ExpertInvocationSystem()
        print("✅ 專家系統初始化成功")
        
        # 測試框架
        testing_framework = DeepTestingFramework()
        print("✅ 測試框架初始化成功")
        
        # 測試優化系統
        optimization_system = IncrementalOptimizationSystem()
        print("✅ 優化系統初始化成功")
        
        # 測試主控制器
        controller = AICoreMasterController("config/aicore_config.yaml")
        print("✅ 主控制器初始化成功")
        
        print("🎉 所有系統組件測試通過!")
        return True
        
    except Exception as e:
        print(f"❌ 系統測試失敗: {e}")
        return False

async def main():
    success = await test_system_components()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
EOF
    
    python3 test_system.py
    
    if [ $? -eq 0 ]; then
        log_success "系統測試通過"
    else
        log_error "系統測試失敗"
        exit 1
    fi
}

# 生成部署報告
generate_deployment_report() {
    log_info "生成部署報告..."
    
    cat > deployment_report.md << EOF
# AICore Human-in-the-Loop Integration System 部署報告

## 部署信息
- **部署時間**: $(date)
- **系統版本**: 1.0.0
- **部署環境**: $(uname -a)
- **Python版本**: $(python3 --version)

## 已安裝組件
- ✅ 動態路由系統 (AICore Dynamic Router)
- ✅ 專家調用機制 (Expert Invocation System)
- ✅ 深度測試框架 (Deep Testing Framework)
- ✅ 增量優化系統 (Incremental Optimization System)
- ✅ 主控制器 (Master Controller)
- ✅ Web API服務器

## 配置文件
- **主配置**: config/aicore_config.yaml
- **數據庫**: data/aicore.db
- **日誌目錄**: logs/
- **測試數據**: data/test_data/

## 服務腳本
- **啟動**: ./start_aicore.sh
- **停止**: ./stop_aicore.sh
- **狀態檢查**: ./check_aicore_status.sh

## API端點
- **健康檢查**: http://localhost:8098/api/health
- **系統狀態**: http://localhost:8098/api/status
- **工作流管理**: http://localhost:8098/api/workflows
- **測試執行**: http://localhost:8098/api/tests/run

## Human-in-the-Loop MCP集成
- **MCP服務地址**: http://localhost:8096
- **支持的交互類型**: approval, input, selection, confirmation
- **會話管理**: 自動創建和管理人工介入會話
- **超時處理**: 可配置的會話超時和重試機制

## 使用指南

### 啟動系統
\`\`\`bash
./start_aicore.sh
\`\`\`

### 檢查狀態
\`\`\`bash
./check_aicore_status.sh
\`\`\`

### 創建工作流
\`\`\`bash
curl -X POST http://localhost:8098/api/workflows \\
  -H "Content-Type: application/json" \\
  -d '{
    "workflow_type": "deployment",
    "title": "Test Deployment",
    "description": "Test deployment workflow",
    "parameters": {"environment": "staging"},
    "metadata": {"complexity": "medium"}
  }'
\`\`\`

### 運行測試
\`\`\`bash
curl -X POST http://localhost:8098/api/tests/run
\`\`\`

## 監控和維護
- **日誌文件**: logs/aicore_system.log
- **性能指標**: 通過API端點獲取
- **數據庫備份**: 定期備份data/aicore.db
- **配置更新**: 修改config/aicore_config.yaml後重啟系統

## 故障排除
1. **系統無法啟動**: 檢查Python依賴和配置文件
2. **API無響應**: 檢查端口8098是否被占用
3. **MCP連接失敗**: 確保Human Loop MCP服務在端口8096運行
4. **數據庫錯誤**: 檢查data/目錄權限和磁盤空間

## 下一步
1. 配置Human Loop MCP服務
2. 自定義工作流類型和專家類型
3. 設置監控和告警
4. 配置生產環境安全設置

部署完成! 🎉
EOF
    
    log_success "部署報告已生成: deployment_report.md"
}

# 主函數
main() {
    echo "🚀 開始部署AICore Human-in-the-Loop Integration System"
    echo "=================================================="
    
    check_system_requirements
    install_dependencies
    setup_configuration
    initialize_database
    create_test_data
    setup_services
    run_tests
    generate_deployment_report
    
    echo "=================================================="
    log_success "AICore系統部署完成!"
    echo ""
    echo "📋 下一步操作:"
    echo "1. 啟動系統: ./start_aicore.sh"
    echo "2. 檢查狀態: ./check_aicore_status.sh"
    echo "3. 查看報告: cat deployment_report.md"
    echo "4. 訪問API: http://localhost:8098/api/health"
    echo ""
    echo "📚 詳細文檔請查看 deployment_report.md"
}

# 執行主函數
main "$@"

