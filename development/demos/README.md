# Development Demos - Manus_Adapter_MCP 整合演示

## 概述

本目錄包含 Manus_Adapter_MCP 與 AICore 3.0 整合的演示和測試應用。展示如何利用 AICore 的核心能力（動態專家、智慧路由、工具發現）來處理 Manus 系統的需求分析。

## 🏗️ 架構設計

### 核心架構
```
AICore 3.0 (核心系統)
├── Manus_Adapter_MCP (增量更新)
│   ├── 動態專家協調 (Dynamic Expert Registry)
│   ├── 智慧路由選擇 (Smart Routing Engine)
│   └── 工具自動發現 (Tool Registry & Discovery)
│
PowerAutomation/components/ (通用組件)
├── manus_adapter_mcp.py (Manus 適配器)
├── aicore_requirement_processor_mcp.py (需求分析處理器)
│
development/demos/ (演示應用)
├── req001_analysis/ (REQ_001 具體分析)
└── manus_examples/ (其他 Manus 示例)
```

### 設計原則

1. **增量更新**: Manus_Adapter_MCP 作為 AICore 的增量更新，不破壞原有架構
2. **能力復用**: 充分利用 AICore 的動態專家、智慧路由、工具發現等核心能力
3. **分層架構**: 核心組件、通用組件、演示應用分層組織
4. **可擴展性**: 支持新的 Manus 需求類型和分析場景

## 📁 目錄結構

```
development/demos/
├── README.md                          # 本文檔
├── req001_analysis/                   # REQ_001 分析演示
│   ├── req001_demo.py                 # 主演示腳本
│   ├── req001_aicore_processor.py     # REQ_001 專用處理器
│   ├── test_aicore_requirement_processor.py  # 測試文件
│   ├── aicore_requirement_processor_design.md  # 設計文檔
│   └── aicore_requirement_processor_test_report_*.json  # 測試報告
└── manus_examples/                    # 其他 Manus 示例
    └── (待添加更多示例)
```

## 🚀 快速開始

### 1. 環境準備

確保您已經安裝了必要的依賴：

```bash
# 進入項目根目錄
cd /path/to/aicore0624

# 確保 Python 路徑正確
export PYTHONPATH=$PYTHONPATH:$(pwd):$(pwd)/PowerAutomation
```

### 2. 運行 REQ_001 演示

```bash
# 進入演示目錄
cd development/demos/req001_analysis

# 運行演示腳本
python req001_demo.py
```

### 3. 預期輸出

演示腳本將展示：

- ✅ Manus_Adapter_MCP 初始化和註冊
- ✅ REQ_001 需求分析處理
- ✅ 明確需求列表生成
- ✅ Manus actions 提取
- ✅ 相關檔案列表
- ✅ 跨任務關聯分析
- ✅ 專家洞察和建議

## 🎯 核心功能演示

### REQ_001 需求分析

**輸入需求**:
```
"首先先針對 REQ_001: 用戶界面設計需求 列出我的明確需求 及manus action 包含相關的檔案列表 注意同一個需求可能跨任務"
```

**輸出結果**:
- 📋 明確需求列表
- 🚀 Manus Actions
- 📁 相關檔案列表
- 🔗 跨任務分析
- 🧠 專家洞察

### Manus_Adapter_MCP 能力

1. **動態專家協調**
   - 自動註冊 Manus 專用專家
   - 根據需求類型選擇合適專家
   - 並行專家分析和建議聚合

2. **智慧路由**
   - 基於需求類型的智能路由
   - 負載均衡和性能優化
   - 故障轉移和容錯處理

3. **工具發現**
   - 自動發現和註冊 Manus 工具
   - 動態工具匹配和選擇
   - 工具執行和結果聚合

## 🔧 API 使用示例

### 基本需求分析

```python
from core.aicore3 import create_aicore3

# 初始化 AICore
aicore = create_aicore3()
await aicore.initialize()

# 處理 Manus 需求
result = await aicore.process_manus_requirement(
    requirement_text="針對 REQ_001: 用戶界面設計需求...",
    target_entity="REQ_001",
    context={"project": "manus_system", "priority": "high"}
)

# 獲取結果
if result["success"]:
    analysis = result["analysis_result"]
    requirements_list = analysis["requirements_list"]
    manus_actions = analysis["manus_actions"]
    file_references = analysis["file_references"]
```

### 直接調用 Manus Adapter

```python
# 直接使用 Manus Adapter
manus_adapter = aicore.manus_adapter

# 需求分析
result = await manus_adapter.analyze_requirement(
    requirement_text="...",
    target_entity="REQ_001",
    context={}
)

# 獲取狀態
status = await manus_adapter.get_manus_status()
```

### HTTP API 端點

```python
# UI 設計審查
result = await aicore.handle_manus_request(
    "/api/manus/ui/review",
    {
        "ui_component": "REQ_001_NavigationBar",
        "design_requirements": ["智慧下載整合", "用戶友好"],
        "context": {"project": "manus_ui"}
    }
)

# 跨任務分析
result = await aicore.handle_manus_request(
    "/api/manus/cross-task/analyze",
    {
        "task_list": ["TASK_001", "TASK_003", "TASK_006"],
        "analysis_focus": "dependencies",
        "context": {"scope": "ui_requirements"}
    }
)
```

## 📊 性能指標

### 預期性能

- **需求分析響應時間**: < 2 秒
- **專家協調時間**: < 1 秒
- **工具執行時間**: < 0.5 秒
- **整體信心度**: > 85%

### 監控指標

- 總請求數
- 成功請求數
- 平均響應時間
- 專家命中率
- 動態工具生成數

## 🧪 測試

### 運行測試

```bash
# 運行需求處理器測試
python test_aicore_requirement_processor.py

# 運行 REQ_001 演示測試
python req001_demo.py
```

### 測試覆蓋

- ✅ 需求解析器測試
- ✅ 專家協調器測試
- ✅ 模擬數據獲取測試
- ✅ 結果格式化測試
- ✅ 端到端處理流程測試

## 📝 開發指南

### 添加新的需求類型

1. 在 `ManusRequestType` 枚舉中添加新類型
2. 在 `_register_manus_experts()` 中註冊相關專家
3. 在 `_register_manus_tools()` 中註冊相關工具
4. 在路由規則中配置處理策略

### 添加新的專家

```python
expert_config = {
    "domain": "new_domain",
    "scenario_type": "new_scenario",
    "skill_requirements": ["skill1", "skill2"],
    "knowledge_sources": [{"type": "source_type", "path": "/path"}]
}
```

### 添加新的工具

```python
tool_config = {
    "id": "new_tool_id",
    "name": "New Tool Name",
    "type": ToolType.PYTHON_MODULE,
    "description": "Tool description",
    "capabilities": [ToolCapability(...)],
    "module_path": "path.to.module"
}
```

## 🔍 故障排除

### 常見問題

1. **初始化失敗**
   - 檢查 Python 路徑設置
   - 確認所有依賴已安裝
   - 檢查 AICore 組件是否正常

2. **專家註冊失敗**
   - 檢查專家配置格式
   - 確認知識源路徑存在
   - 檢查專家註冊中心狀態

3. **工具執行失敗**
   - 檢查工具註冊狀態
   - 確認工具模塊路徑正確
   - 檢查工具依賴是否滿足

### 調試模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 啟用詳細日誌
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
```

## 📚 相關文檔

- [AICore 3.0 架構文檔](../../PowerAutomation/docs/)
- [Manus_Adapter_MCP 設計文檔](req001_analysis/aicore_requirement_processor_design.md)
- [需求分析處理器文檔](../../PowerAutomation/components/aicore_requirement_processor_mcp.py)
- [動態專家系統文檔](../../PowerAutomation/components/dynamic_expert_registry.py)

## 🤝 貢獻指南

1. Fork 項目
2. 創建功能分支
3. 添加測試
4. 更新文檔
5. 提交 Pull Request

## 📄 許可證

本項目遵循 MIT 許可證。

## 📞 聯繫方式

如有問題或建議，請聯繫開發團隊。

---

**注意**: 本演示僅用於展示 Manus_Adapter_MCP 與 AICore 3.0 的整合能力，實際生產環境使用前請進行充分測試。

