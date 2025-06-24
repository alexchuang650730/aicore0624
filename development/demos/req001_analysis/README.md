# REQ_001 分析演示

## 概述

本目錄包含針對 REQ_001 (用戶界面設計需求) 的完整分析演示，展示如何使用 Manus_Adapter_MCP 和 AICore 3.0 來處理具體的需求分析任務。

## 🎯 演示目標

處理用戶需求：
> "首先先針對 REQ_001: 用戶界面設計需求 列出我的明確需求 及manus action 包含相關的檔案列表 注意同一個需求可能跨任務"

## 📁 文件說明

### 核心文件

- **`req001_demo.py`** - 主演示腳本
  - 完整的 REQ_001 分析演示
  - 展示 Manus_Adapter_MCP 的各種能力
  - 生成詳細的分析報告

- **`req001_aicore_processor.py`** - REQ_001 專用處理器
  - 針對 REQ_001 優化的處理邏輯
  - 專門的需求解析和分析功能

### 測試和文檔

- **`test_aicore_requirement_processor.py`** - 測試套件
  - 需求處理器的完整測試
  - 5個測試方法，100% 通過率

- **`aicore_requirement_processor_design.md`** - 設計文檔
  - 詳細的架構設計說明
  - 組件交互流程圖

- **`aicore_requirement_processor_test_report_*.json`** - 測試報告
  - 詳細的測試執行結果
  - 性能指標和統計數據

## 🚀 快速運行

### 1. 環境準備

```bash
# 確保在正確的目錄
cd /path/to/aicore0624/development/demos/req001_analysis

# 設置 Python 路徑
export PYTHONPATH=$PYTHONPATH:../../../:../../../PowerAutomation
```

### 2. 運行演示

```bash
# 運行完整演示
python req001_demo.py
```

### 3. 運行測試

```bash
# 運行測試套件
python test_aicore_requirement_processor.py
```

## 📊 預期輸出

### REQ_001 分析結果

演示將輸出以下結構化結果：

```
🎯 REQ_001: 用戶界面設計需求 - 分析結果
================================================================================
📋 目標實體: REQ_001
⚡ 處理時間: X.XX秒
🎯 信心度: 0.XX

📝 明確需求列表 (X 項):
  1. 智慧下載導航欄整合需求
  2. 用戶界面響應式設計需求
  3. 導航欄可用性優化需求
  4. 界面一致性設計需求
  5. 用戶體驗流暢性需求

🚀 Manus Actions (X 項):
  1. 實施導航欄智慧下載功能
  2. 優化界面響應式布局
  3. 進行用戶體驗測試
  4. 更新設計規範文檔
  5. 協調跨團隊設計評審

📁 相關檔案列表 (X 項):
  1. /manus/ui/navigation_bar.jsx
  2. /manus/design/ui_guidelines.md
  3. /manus/requirements/req_001_spec.md
  4. /manus/tests/ui_integration_tests.py
  5. /manus/docs/design_review_notes.md

🔗 跨任務分析:
  - 關聯任務: TASK_003 (下載功能實現)
  - 依賴關係: TASK_006 (用戶認證系統)
  - 影響範圍: 前端界面、用戶體驗、系統整合

🧠 專家洞察:
  📊 manus_ui_design_analysis:
    - 分析: 針對 REQ_001 的 requirement_analysis 分析
    - 信心度: 0.85
  📊 manus_requirement_analysis:
    - 分析: 基於需求分解和優先級評估的專業分析
    - 信心度: 0.85
```

### Manus Adapter 狀態

```
📊 Manus_Adapter_MCP 狀態
============================================================
  adapter_status: active
  registered_experts: 4
  registered_tools: 3
  aicore_connected: True
  expert_registry_available: True
  routing_engine_available: True
  tool_registry_available: True
  cache_size: 0
  version: 1.0.0
```

### AICore 系統統計

```
📈 AICore 3.0 系統統計
============================================================
⚡ 性能指標:
  - total_requests: X
  - successful_requests: X
  - average_response_time: X.XX
  - expert_hit_rate: X.XX
  - dynamic_tools_generated: X

👥 專家系統:
  - 總專家數: X
  - 活躍專家數: X

🏥 系統健康:
  - total_experts: X
  - active_experts: X
  - success_rate: X.XX
  - average_response_time: X.XX
```

## 🔧 自定義配置

### 修改分析參數

在 `req001_demo.py` 中修改以下參數：

```python
# 修改需求文本
requirement_text = "您的自定義需求..."

# 修改上下文
context = {
    "project": "your_project",
    "priority": "high|medium|low",
    "analysis_type": "comprehensive|basic",
    "cross_task_analysis": True|False
}
```

### 添加自定義專家

在 REQ_001 處理器中添加專門的專家：

```python
custom_expert_config = {
    "domain": "req001_specific_domain",
    "scenario_type": "req001_scenario",
    "skill_requirements": ["req001_skill1", "req001_skill2"],
    "knowledge_sources": [
        {"type": "req001_data", "path": "/path/to/req001/data"}
    ]
}
```

## 📈 性能基準

### 目標性能指標

- **總處理時間**: < 3 秒
- **需求解析時間**: < 0.5 秒
- **專家分析時間**: < 1 秒
- **工具執行時間**: < 1 秒
- **結果聚合時間**: < 0.5 秒
- **整體信心度**: > 85%

### 實際測試結果

運行演示後，檢查生成的 `req001_demo_results_*.json` 文件獲取詳細的性能數據。

## 🧪 測試覆蓋

### 測試項目

1. **需求解析器測試** - 驗證需求文本解析功能
2. **專家協調器測試** - 驗證專家選擇和協調邏輯
3. **模擬數據獲取測試** - 驗證數據獲取和處理
4. **結果格式化測試** - 驗證輸出格式和結構
5. **端到端處理測試** - 驗證完整處理流程

### 測試結果

```
✅ 測試通過: 5/5
✅ 成功率: 100.0%
✅ 平均執行時間: X.XX秒
```

## 🔍 故障排除

### 常見問題

1. **模塊導入錯誤**
   ```bash
   # 解決方案：設置正確的 Python 路徑
   export PYTHONPATH=$PYTHONPATH:../../../:../../../PowerAutomation
   ```

2. **AICore 初始化失敗**
   ```bash
   # 檢查依賴組件
   python -c "from core.aicore3 import create_aicore3; print('OK')"
   ```

3. **專家註冊失敗**
   ```bash
   # 檢查專家註冊中心狀態
   # 查看詳細錯誤日誌
   ```

### 調試模式

啟用詳細日誌：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 相關資源

- [Manus_Adapter_MCP 源碼](../../../PowerAutomation/components/manus_adapter_mcp.py)
- [需求分析處理器源碼](../../../PowerAutomation/components/aicore_requirement_processor_mcp.py)
- [AICore 3.0 核心](../../../PowerAutomation/core/aicore3.py)
- [設計文檔](aicore_requirement_processor_design.md)

## 🎯 下一步

1. **擴展需求類型** - 添加更多 Manus 需求類型支持
2. **優化性能** - 提升處理速度和準確性
3. **增強專家** - 添加更多專業領域專家
4. **完善工具** - 開發更多分析和處理工具
5. **集成測試** - 與實際 Manus 系統集成測試

---

**注意**: 本演示展示了 Manus_Adapter_MCP 的核心能力，實際使用時請根據具體需求進行調整和優化。

