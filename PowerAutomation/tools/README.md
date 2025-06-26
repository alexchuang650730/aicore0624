# Human Loop Integration Tool for PowerAutomation

## 概述

Human Loop Integration Tool 是一個為 PowerAutomation 設計的獨立工具，實現智能化的人機協作決策系統。該工具**不修改 AICore 核心組件**，而是作為獨立的工具集成到 PowerAutomation 生態系統中。

## 設計原則

### 🎯 核心原則
- **非侵入性**: 不修改 AICore 核心組件
- **獨立運行**: 作為獨立服務運行
- **API 集成**: 通過 HTTP API 與現有系統集成
- **可插拔架構**: 可以隨時啟用或禁用

### 🏗️ 架構設計
```
PowerAutomation
├── core/                    # AICore 核心組件 (不修改)
│   ├── aicore2.py
│   ├── aicore3.py
│   └── ...
├── components/              # 現有組件 (不修改)
│   ├── enhanced_vscode_installer_mcp.py
│   └── ...
└── tools/                   # 新增工具目錄
    ├── human_loop_integration_tool.py      # 主工具
    ├── human_loop_integration_server.py    # API 服務器
    ├── human_loop_integration_config.json  # 配置文件
    └── examples/                           # 集成示例
```

## 功能特色

### 🧠 智能路由決策
- **自動處理**: 低複雜度、低風險的操作
- **人工介入**: 高複雜度、高風險的操作
- **專家諮詢**: 需要專業知識的技術決策
- **條件處理**: 基於測試結果的動態決策

### 🔗 Human Loop MCP 集成
- **無縫集成**: 與 Human Loop MCP 服務無縫對接
- **多種交互**: 支持確認、輸入、選擇、確認等交互類型
- **會話管理**: 自動創建和管理 MCP 會話
- **超時處理**: 可配置的超時和重試機制

### 👨‍💼 專家系統
- **技術專家**: 部署和配置問題
- **API 專家**: 接口設計和集成
- **業務專家**: 業務邏輯和流程
- **數據專家**: 數據處理和分析
- **集成專家**: 系統集成和架構
- **安全專家**: 安全評估和合規
- **性能專家**: 性能優化和調優

### 🧪 深度測試框架
- **單元測試**: 組件功能驗證
- **集成測試**: 系統間交互測試
- **安全測試**: 安全漏洞掃描
- **性能測試**: 負載和響應時間測試

### 📈 增量優化
- **機器學習**: 基於歷史數據的決策優化
- **自適應調整**: 動態調整決策閾值
- **性能預測**: 預測操作成功率和執行時間

## 安裝和部署

### 快速部署
```bash
# 1. 進入 aicore0624 項目目錄
cd aicore0624

# 2. 運行部署腳本
chmod +x deploy_human_loop_integration_tool.sh
./deploy_human_loop_integration_tool.sh
```

### 手動安裝
```bash
# 1. 創建虛擬環境
python3 -m venv venv
source venv/bin/activate

# 2. 安裝依賴
pip install -r PowerAutomation/tools/requirements.txt

# 3. 啟動服務
./PowerAutomation/tools/start_human_loop_integration.sh
```

## 使用方式

### 1. 啟動服務
```bash
# 啟動 Human Loop Integration Tool
./PowerAutomation/tools/start_human_loop_integration.sh

# 檢查服務狀態
./PowerAutomation/tools/check_human_loop_integration.sh
```

### 2. API 使用
```python
import aiohttp
import asyncio

async def create_workflow():
    workflow_data = {
        "title": "VSIX 部署",
        "description": "部署 PowerAutomation VSIX 到 VS Code",
        "parameters": {
            "target": "vscode",
            "version": "3.0.0"
        },
        "metadata": {
            "workflow_type": "deployment",
            "environment": "production"
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8098/api/workflows",
            json=workflow_data
        ) as response:
            result = await response.json()
            print(f"結果: {result}")

asyncio.run(create_workflow())
```

### 3. 與 PowerAutomation 集成
```python
# 在現有的 PowerAutomation 組件中
class EnhancedVSCodeInstallerMCP:
    def __init__(self):
        self.human_loop_api = "http://localhost:8098"
    
    async def deploy_with_human_loop(self, deployment_params):
        # 創建工作流
        workflow_data = {
            "title": "VSIX 部署",
            "description": "智能部署 VSIX 擴展",
            "parameters": deployment_params,
            "metadata": {
                "workflow_type": "deployment",
                "environment": deployment_params.get("environment", "development")
            }
        }
        
        # 發送到 Human Loop Integration Tool
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.human_loop_api}/api/workflows",
                json=workflow_data
            ) as response:
                return await response.json()
```

## API 接口

### 健康檢查
```http
GET /api/health
```

### 創建工作流
```http
POST /api/workflows
Content-Type: application/json

{
    "title": "工作流標題",
    "description": "工作流描述",
    "parameters": {},
    "metadata": {}
}
```

### 獲取工作流狀態
```http
GET /api/workflows/{workflow_id}
```

### 獲取決策歷史
```http
GET /api/decisions/history?limit=10
```

### 獲取統計信息
```http
GET /api/stats
```

## 配置

### 配置文件: `PowerAutomation/tools/human_loop_integration_config.json`
```json
{
    "database_path": "human_loop_integration.db",
    "human_loop_mcp_url": "http://localhost:8096",
    "aicore_api_url": "http://localhost:8080",
    "decision_thresholds": {
        "complexity_threshold": 0.7,
        "risk_threshold": 0.6,
        "confidence_threshold": 0.8
    }
}
```

### 決策閾值調整
- `complexity_threshold`: 複雜度閾值 (0-1)
- `risk_threshold`: 風險閾值 (0-1)
- `confidence_threshold`: 信心度閾值 (0-1)

## 決策邏輯

### 路由決策流程
```
工作流輸入
    ↓
計算複雜度分數
    ↓
計算風險分數
    ↓
預測信心度
    ↓
決策邏輯:
├── 高複雜度 + 高風險 → 人工介入
├── 高複雜度 → 專家諮詢
├── 低信心度 → 條件處理
└── 其他 → 自動處理
```

### 複雜度計算因子
- 參數數量
- 工作流類型
- 依賴關係數量
- 環境複雜度

### 風險計算因子
- 環境風險 (開發 < 測試 < 預發 < 生產)
- 操作風險 (讀取 < 寫入 < 刪除 < 部署)
- 數據敏感性
- 系統影響程度

## 監控和日誌

### 日誌文件
- `human_loop_integration.log`: 主要日誌
- `human_loop_integration.db`: SQLite 數據庫

### 監控指標
- 工作流總數
- 成功率
- 決策類型分布
- 平均複雜度/風險/信心度分數
- 最近活動統計

## 故障排除

### 常見問題

#### 1. 服務無法啟動
```bash
# 檢查 Python 環境
python3 --version

# 檢查依賴
pip list | grep fastapi

# 檢查端口占用
lsof -i :8098
```

#### 2. Human Loop MCP 連接失敗
```bash
# 檢查 Human Loop MCP 服務
curl http://localhost:8096/health

# 檢查配置
cat PowerAutomation/tools/human_loop_integration_config.json
```

#### 3. 數據庫錯誤
```bash
# 重新初始化數據庫
rm human_loop_integration.db
./PowerAutomation/tools/start_human_loop_integration.sh
```

### 調試模式
```bash
# 啟動調試模式
python3 PowerAutomation/tools/human_loop_integration_server.py --reload --log-level debug
```

## 開發和擴展

### 添加新的專家類型
```python
class CustomExpert:
    def get_recommendation(self, context, decision):
        # 自定義專家邏輯
        return {
            'expert_type': 'custom',
            'confidence': 0.8,
            'recommendation': 'proceed',
            'reasoning': '自定義專家評估'
        }
```

### 添加新的測試類型
```python
async def custom_test(self, context):
    # 自定義測試邏輯
    return {
        'test_type': 'custom',
        'passed': True,
        'message': '自定義測試通過'
    }
```

### 自定義決策邏輯
```python
def custom_decision_logic(self, complexity, risk, confidence):
    # 自定義決策邏輯
    if custom_condition:
        return DecisionType.CUSTOM
    return DecisionType.AUTOMATIC
```

## 與現有系統的集成點

### 1. Enhanced VSCode Installer MCP
```python
# 在 enhanced_vscode_installer_mcp.py 中添加
async def deploy_with_intelligence(self, params):
    # 調用 Human Loop Integration Tool
    result = await self.human_loop_client.create_workflow({
        "title": "VSIX 智能部署",
        "parameters": params
    })
    return result
```

### 2. General Processor MCP
```python
# 在 general_processor_mcp.py 中添加
async def process_with_human_loop(self, task):
    # 根據任務複雜度決定處理方式
    workflow_result = await self.human_loop_client.create_workflow({
        "title": "任務處理",
        "parameters": task
    })
    return workflow_result
```

### 3. Smart Routing Engine
```python
# 在 smart_routing_engine.py 中添加
async def route_with_intelligence(self, request):
    # 使用 Human Loop Integration Tool 進行智能路由
    decision = await self.human_loop_client.get_routing_decision(request)
    return decision
```

## 版本歷史

### v1.0.0 (2024-06-24)
- 初始版本
- 智能路由決策系統
- Human Loop MCP 集成
- 專家系統框架
- 深度測試框架
- 增量優化系統
- HTTP API 接口
- 完整的部署和集成方案

## 許可證

本工具遵循與 PowerAutomation 項目相同的許可證。

## 貢獻

歡迎提交 Issue 和 Pull Request 來改進這個工具。

## 聯繫方式

如有問題或建議，請通過 PowerAutomation 項目的官方渠道聯繫。

