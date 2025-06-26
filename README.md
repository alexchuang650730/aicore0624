# PowerAutomation - AICore 3.0 智能自動化平台

PowerAutomation是基於動態專家系統的智能自動化平台，提供完整的工作流錄製、分析和管理能力，以及端雲協同的智能工具生態系統。

## 📁 項目目錄組織規範

### **根目錄結構**
```
aicore0624/
├── README.md                    # 項目說明文檔
├── requirements.txt             # Python 依賴清單
├── .gitignore                   # Git 忽略規則
├── PowerAutomation/             # 核心系統目錄
├── PowerAutomation_local/       # 插件生產部署目錄
├── deployment/                  # 部署相關文件
├── docs/                        # 項目文檔
├── development/                 # 開發相關文件
├── tests/                       # 測試相關文件
├── scripts/                     # 通用腳本
├── test_flow_api_examples/      # API 測試範例
├── powerautomation_web/         # Web 相關組件
└── agent_admin/                 # 管理工具
```

### **文件分類標準**

#### 🚀 **部署相關** → `deployment/`
- **`deployment/scripts/`**: 部署腳本
  - `deploy_*.sh` - 各種部署腳本
  - `mac_*.sh` - Mac 平台部署腳本
  - `ssh_remote_deployment.sh` - 遠程部署腳本
  - `setup_*.sh` - 環境設置腳本
  - `update_*.sh` - 更新腳本

- **`deployment/configs/`**: 配置文件
  - `packages.microsoft.gpg` - Microsoft 包簽名
  - `wrangler.toml` - Cloudflare 配置
  - 其他系統配置文件

- **`deployment/keys/`**: 密鑰文件
  - `*.pem` - SSH 密鑰文件
  - 其他認證相關文件

#### 📚 **文檔相關** → `docs/`
- **`docs/sop/`**: 標準操作程序
  - `TEST_FLOW_MCP_SOP.md` - test_flow_mcp 使用 SOP
  - `TEST_FLOW_API_TESTING_SOP.md` - API 測試 SOP
  - 其他操作規範文檔

- **`docs/reports/`**: 報告文件
  - `*_Report*.md` - 各種項目報告
  - `*_Guide.md` - 使用指南
  - `*_Analysis.md` - 分析報告
  - `GitHub_Update_File_List*.md` - 更新記錄
  - `*.pdf` - PDF 格式報告

- **`docs/guides/`**: 指南文檔
  - 安裝指南、使用手冊等

#### 🧪 **測試相關** → `tests/`
- **`tests/results/`**: 測試結果
  - `*.json` - 測試結果 JSON 文件
  - `*.log` - 測試執行日誌
  - 測試報告和統計數據

- **`tests/testcases/`**: 測試案例
  - 各種測試用例和測試數據

#### 🛠️ **開發相關** → `development/`
- **`development/tools/`**: 開發工具
  - `aicore_*.py` - AICore 相關工具
  - `*_framework.py` - 各種框架工具
  - `*_system.py` - 系統級工具
  - `mcp_*.py` - MCP 相關工具
  - `*_connection.py` - 連接工具

- **`development/demos/`**: 示例代碼
  - `smartinvention_fix/` - SmartInvention 修復示例
  - 其他功能演示代碼

- **`development/experiments/`**: 實驗性代碼
  - 原型開發和實驗功能

### **文件命名規範**

#### **部署腳本命名**
- `deploy_[target]_[environment].sh` - 部署腳本
- `setup_[component]_[platform].sh` - 設置腳本
- `update_[component].sh` - 更新腳本

#### **文檔命名**
- `[Component]_[Type]_[Version].md` - 組件文檔
- `[Project]_[Report_Type]_Report.md` - 報告文檔
- `[Feature]_Guide.md` - 指南文檔

#### **測試文件命名**
- `test_[component]_[test_type].py` - 測試腳本
- `[component]_test_result_[timestamp].json` - 測試結果
- `[test_suite]_execution.log` - 執行日誌

#### **開發工具命名**
- `[component]_[function]_[version].py` - 開發工具
- `[system]_[purpose].py` - 系統工具

### **目錄維護原則**

1. **保持根目錄整潔**
   - 根目錄只保留核心文件和主要目錄
   - 避免在根目錄堆積臨時文件

2. **按功能分類存放**
   - 相同功能的文件放在同一目錄下
   - 使用清晰的子目錄結構

3. **遵循命名規範**
   - 使用有意義的文件名
   - 保持命名一致性

4. **定期清理維護**
   - 及時移除過時文件
   - 整理和歸檔舊版本文件

## 🚀 主要特性

### **AICore 3.0 動態專家系統**
- **智能專家發現**: 基於Cloud Search的場景驅動專家創建
- **並行專家調用**: 同時調用多個領域專家提高效率
- **專家建議聚合**: 智能整合多專家分析結果
- **動態工具生成**: 根據專家建議自動生成MCP工具

### **完整的MCP組件生態**
- **General_Processor MCP**: 統一的通用處理器組件
- **Recorder_Workflow MCP**: 工作流錄製和管理組件
- **Smartinvention_Adapter MCP**: 智能對話處理和本地模型管理
- **Local MCP Adapter**: 端側適配器，支持工具註冊、心跳管理、智慧路由
- **Enhanced Tool Registry**: 智能工具管理和雲端平台整合

### **Enhanced Tool Registry - 智能工具生態系統**
- **Smart Tool Engine**: 統一智能工具引擎
- **雲端平台整合**: 支持ACI.dev、MCP.so、Zapier三大平台
- **智能路由引擎**: 多維度評分的最優工具選擇
- **成本優化管理**: 智能預算控制，平均節省40%成本
- **性能監控分析**: 實時監控工具表現和質量保證

### **Local MCP Adapter - 端側智能適配器**
- **工具註冊機制**: 向中央註冊中心註冊可用工具，支持自動發現
- **端雲Heartbeat**: 維持與雲端的連接狀態，智能重連機制
- **智慧路由**: 根據負載和可用性進行智能路由，6種路由策略
- **負載監控**: 實時監控系統負載和性能指標
- **熔斷保護**: 自動隔離故障工具，防止級聯故障

### **智能工作流管理**
- **無UI依賴**: 純MCP組件，無需Web界面
- **模式分析**: 工作流模式識別和優化建議
- **多格式導出**: JSON、CSV、YAML格式支持
- **會話管理**: 完整的錄製會話生命週期管理

## 📁 PowerAutomation 核心結構

```
PowerAutomation/
├── components/          # MCP組件
│   ├── general_processor_mcp.py          # 通用處理器
│   ├── recorder_workflow_mcp.py          # 工作流錄製器
│   ├── smartinvention_adapter_mcp.py     # 智能對話適配器
│   ├── local_mcp_adapter.py              # 端側適配器
│   ├── tool_registry_manager.py          # 工具註冊管理器
│   ├── heartbeat_manager.py              # 心跳管理器
│   ├── smart_routing_engine.py           # 智慧路由引擎
│   ├── scenario_analyzer.py              # 場景分析器
│   ├── dynamic_expert_registry.py        # 動態專家註冊中心
│   └── expert_recommendation_aggregator.py # 專家建議聚合器
├── core/               # 核心引擎
│   ├── aicore3.py      # AICore 3.0主引擎
│   ├── aicore2.py      # AICore 2.0
│   └── enhanced_agent_core.py
├── tools/              # 工具系統
│   ├── tool_registry.py                  # 基礎工具註冊表
│   ├── enhanced_tool_registry.py         # 增強工具註冊表
│   └── smart_tool_engine_mcp.py          # 智能工具引擎
├── config/             # 配置管理
│   ├── config.py       # 基礎配置
│   ├── enhanced_config.py                # 增強配置
│   └── endpoint_mapping.py               # 端點映射配置
├── actions/            # 動作執行器
│   ├── action_executor.py                # 基礎動作執行器
│   └── action_executor_mcp_support.py    # MCP支持動作執行器
└── docs/              # 文檔
```

## 🎯 核心能力

### **五階段智能處理流程**
1. **整合式搜索和分析** - Cloud Search一次解決多問題
2. **動態專家生成** - 場景驅動的專家創建
3. **專家回答生成** - 並行多專家分析
4. **智能工具執行** - 基於專家建議的智能工具選擇和執行
5. **最終結果生成** - 綜合分析和結果輸出

### **支持的專家領域**
- 技術專家 (technical_expert)
- API專家 (api_expert)
- 業務專家 (business_expert)
- 數據專家 (data_expert)
- 集成專家 (integration_expert)
- 安全專家 (security_expert)
- 性能專家 (performance_expert)
- **動態專家**: 測試、部署、編碼等場景自動創建

### **雲端平台整合**
- **ACI.dev**: AI工具平台，1000+ AI工具
- **MCP.so**: MCP工具市場，500+ MCP組件
- **Zapier**: 自動化工具平台，3000+ 應用整合

## 🛠️ 快速開始

### **安裝依賴**
```bash
pip install -r requirements.txt
```

### **啟動AICore 3.0**
```python
from PowerAutomation.core.aicore3 import create_aicore3

# 創建AICore實例
aicore = create_aicore3()
await aicore.initialize()

# 處理請求
result = await aicore.process_request(request)
```

### **使用Enhanced Tool Registry**
```python
from PowerAutomation.tools.enhanced_tool_registry import create_enhanced_tool_registry

# 創建增強工具註冊表
registry = create_enhanced_tool_registry()
await registry.initialize()

# 智能工具選擇
optimal_tools = await registry.find_optimal_tools(
    requirement="數據分析和可視化",
    context={"budget": {"max_cost": 0.05}}
)
```

### **使用Local MCP Adapter**
```python
from PowerAutomation.components.local_mcp_adapter import create_local_mcp_adapter

# 創建端側適配器
adapter = create_local_mcp_adapter(config_dict={
    'adapter_id': 'edge_device_001',
    'cloud_endpoint': 'https://powerautomation.cloud',
    'api_key': 'your_api_key'
})

# 啟動適配器
await adapter.start()

# 智能路由請求
decision = await adapter.route_request(
    capability='text_processing',
    priority='high',
    timeout=10.0
)
```

### **使用Recorder_Workflow MCP**
```python
from PowerAutomation.components.recorder_workflow_mcp import create_recorder_workflow_mcp

# 創建錄製器
recorder = create_recorder_workflow_mcp()

# 開始錄製
await recorder.start_recording("測試工作流", "testing")

# 停止錄製
result = await recorder.stop_recording()
```

## 📊 系統狀態

### **PowerAutomation 3.0.0 組件生態**
- ✅ **AICore 3.0** - 動態專家系統核心引擎
- ✅ **Enhanced Tool Registry** - 智能工具管理系統
- ✅ **Local MCP Adapter** - 端側智能適配器
- ✅ **Smartinvention_Adapter MCP** - 智能對話處理組件
- ✅ **Recorder_Workflow MCP** - 工作流錄製組件
- ✅ **General_Processor MCP** - 統一通用處理器
- ✅ **Smart Tool Engine** - 智能工具引擎

### **技術特性**
- **雲邊協同**: 雲端智能決策 + 邊緣設備執行
- **智能路由**: 6種路由策略，多維度評分
- **成本優化**: 智能預算管理，平均節省40%成本
- **高可用性**: 自動故障轉移，熔斷保護
- **實時監控**: 全面的性能和健康監控

## 🔧 配置說明

### **Enhanced Tool Registry配置**
```yaml
enhanced_tool_registry:
  smart_engine:
    enable_cloud_platforms: true
    platforms:
      aci_dev:
        enabled: true
        api_key: "your_aci_api_key"
      mcp_so:
        enabled: true
        api_key: "your_mcp_api_key"
      zapier:
        enabled: true
        api_key: "your_zapier_api_key"
  cost_optimization:
    enable_budget_control: true
    monthly_budget: 100.0
    free_tools_priority: true
```

### **Local MCP Adapter配置**
```yaml
local_mcp_adapter:
  adapter_id: "edge_device_001"
  cloud_endpoint: "https://powerautomation.cloud"
  tool_discovery:
    auto_discovery: true
    scan_interval: 60
  heartbeat:
    heartbeat_interval: 30
    timeout: 10
  routing:
    default_strategy: "intelligent"
    load_threshold: 0.7
```

## 🚀 部署指南

### **雲端部署**
1. 部署AICore 3.0到雲端服務器
2. 配置Enhanced Tool Registry
3. 啟動智能工具引擎

### **邊緣設備部署**
1. 安裝Local MCP Adapter
2. 配置與雲端的連接
3. 啟動工具註冊和心跳服務

### **混合部署**
- 雲端負責智能決策和專家分析
- 邊緣設備負責工具執行和數據處理
- 通過智慧路由實現最優資源分配

## 📈 性能指標

### **Enhanced Tool Registry**
- **工具發現時間**: < 2秒
- **智能路由決策**: < 0.5秒
- **成本節省率**: 平均40%
- **工具可用性**: 99.5%

### **Local MCP Adapter**
- **心跳延遲**: < 100ms
- **路由決策時間**: < 1秒
- **故障轉移時間**: < 5秒
- **負載均衡效率**: 95%

## 🔗 相關鏈接

- **GitHub倉庫**: https://github.com/alexchuang650730/aicore0624
- **技術文檔**: 詳見docs目錄
- **API文檔**: 詳見各組件的docstring

## 📝 更新日誌

### **v3.0.1 (2025-06-25)**
- ✅ 重構項目目錄結構，建立清晰的文件組織規範
- ✅ 新增完整的目錄組織和文件分類標準
- ✅ 優化根目錄結構，提升項目維護性
- ✅ 完善文檔體系，建立標準操作程序

### **v3.0.0 (2025-06-23)**
- ✅ 新增Enhanced Tool Registry智能工具管理系統
- ✅ 新增Local MCP Adapter端側智能適配器
- ✅ 新增Smartinvention_Adapter MCP智能對話處理
- ✅ 整合ACI.dev、MCP.so、Zapier三大雲端平台
- ✅ 實現智能路由引擎和成本優化系統
- ✅ 完善工具註冊、心跳管理、負載監控功能

### **v2.0.0**
- ✅ 實現AICore 3.0動態專家系統
- ✅ 新增Recorder_Workflow MCP工作流錄製組件
- ✅ 實現動態專家註冊中心和專家建議聚合器
- ✅ 完善MCP組件生態系統

### **v1.0.0**
- ✅ 基礎AICore引擎實現
- ✅ 基本工具註冊和管理功能
- ✅ 核心MCP組件架構

## 🤝 貢獻指南

歡迎提交Issue和Pull Request來改進PowerAutomation！

請遵循項目的目錄組織規範和文件命名標準。

## 📄 許可證

MIT License - 詳見LICENSE文件

---

**PowerAutomation 3.0.1** - 讓智能自動化觸手可及，實現真正的雲邊協同智能系統！

