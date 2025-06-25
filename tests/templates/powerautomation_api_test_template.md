# PowerAutomation API 集成測試用例

基於三種使用者角色的 API 操作測試，分為開發者、使用者、管理員三大類。

## API型測試用例范例

### 測試用例 1: 開發者 test_flow_mcp 集成測試

**測試類型**: API型測試  
**業務模塊**: PowerAutomation Core, test_flow_mcp  
**測試ID**: PA_DEV_TF_001  

**測試描述**:  
驗證開發者使用 test_flow_mcp 進行問題診斷、代碼分析和獲取修復建議的完整 CRUD 流程。

**測試目的**:  
- 驗證開發者角色的 test_flow_mcp 集成功能
- 確保四階段處理流程正常運行
- 驗證分析結果的完整性和準確性

**環境前置條件**:
```yaml
硬件環境:
  - 設備類型: 任何支持 Python 的計算機
  - 內存: >=4GB

軟件環境:
  - Python版本: >=3.8
  - 測試庫: requests, json, time
  - PowerAutomation服務器: 運行中

網絡環境:
  - 網絡連接: 穩定
  - 服務器可訪問性: http://127.0.0.1:8080

權限要求:
  - 開發者 API Key: dev_407CYuVKuP_s3hVqIhO4JZKqcE4-W9ocTgc_fldjxso
```

**測試前置條件**:
- PowerAutomation 測試服務器已啟動並運行
- test_flow_mcp 模塊已正確集成並啟用
- 開發者 API Key 有效且具備相應權限

**測試步驟與API檢查點**:

1. **步驟1 (Create)**: 提交 test_flow_mcp 分析請求
   - **操作**: POST /api/process
   - **請求體**: 
     ```json
     {
       "request": "請分析當前系統的測試覆蓋率並提供改進建議",
       "context": {
         "source": "vscode_vsix",
         "user_role": "developer",
         "workflow_type": "test_flow_analysis",
         "target_component": "test_flow_mcp",
         "analysis_type": "coverage_analysis"
       }
     }
     ```
   - **Headers**: X-API-Key: dev_407CYuVKuP_s3hVqIhO4JZKqcE4-W9ocTgc_fldjxso
   - **🔍 檢查點1**: HTTP 狀態碼為 200
   - **驗證**: 請求成功提交，開始分析處理

2. **步驟2 (Read)**: 獲取分析報告
   - **操作**: 從步驟1的響應中提取分析結果
   - **🔍 檢查點2**: 響應包含 test_flow_analysis 字段
   - **🔍 檢查點3**: 包含四階段處理結果：
     - requirement_sync (需求同步引擎)
     - comparison_analysis (比較分析引擎)
     - evaluation_report (評估報告生成器)
     - code_fixes (Code Fix Adapter)
   - **驗證**: 分析結果結構完整，內容符合預期

3. **步驟3 (Validate)**: 驗證分析結果質量
   - **操作**: 檢查響應中的關鍵字段
   - **🔍 檢查點4**: user_role 識別為 "developer"
   - **🔍 檢查點5**: 響應包含測試相關關鍵詞 ['test', 'coverage', 'analysis', 'mcp', 'flow']
   - **🔍 檢查點6**: recommendations 字段不為空
   - **🔍 檢查點7**: code_fixes 字段包含具體修復建議
   - **驗證**: 分析結果質量符合開發者需求

**預期結果**:
- **檢查點1**: HTTP 200 OK，請求成功處理
- **檢查點2**: 響應包含完整的 test_flow_analysis 結構
- **檢查點3**: 四階段處理結果完整：
  ```json
  {
    "requirement_sync": {"sync_status": "completed", "requirement_id": "req_xxx"},
    "comparison_analysis": {"differences_identified": 3, "improvement_areas": ["code_quality", "test_coverage", "documentation"]},
    "evaluation_report": {"executive_summary": "系統需求分析完成", "detailed_findings": [...], "priority_recommendations": [...]},
    "code_fixes": [{"file_path": "/path/to/file", "fix_type": "error_handling", "suggested_code": "..."}]
  }
  ```
- **檢查點4**: user_role 正確識別為 "developer"
- **檢查點5**: 響應內容包含測試相關關鍵詞
- **檢查點6**: recommendations 包含具體改進建議
- **檢查點7**: code_fixes 包含可執行的代碼修復方案

**失敗判斷標準**:
- HTTP 狀態碼不是 200
- 響應結構不完整或缺少關鍵字段
- 四階段處理結果任一階段失敗
- 角色識別錯誤
- 分析結果質量不符合預期

---

### 測試用例 2: 使用者 SmartInvention-Manus HITL 測試

**測試類型**: API型測試  
**業務模塊**: PowerAutomation Core, SmartInvention-Manus HITL  
**測試ID**: PA_USER_SM_001  

**測試描述**:  
驗證使用者通過 SmartInvention-Manus HITL 流程處理常規請求的完整流程。

**測試目的**:  
- 驗證使用者角色的 HITL 流程
- 確保人工審核機制正常工作
- 驗證請求處理結果的準確性

**環境前置條件**:
```yaml
硬件環境:
  - 設備類型: 任何支持 Python 的計算機
  - 內存: >=4GB

軟件環境:
  - Python版本: >=3.8
  - 測試庫: requests, json, time
  - PowerAutomation服務器: 運行中

網絡環境:
  - 網絡連接: 穩定
  - 服務器可訪問性: http://127.0.0.1:8080

權限要求:
  - 使用者 API Key: user_RcmKEIPfGCQrA6sSohzn5NDXYMsS5mkyP9jPhM3llTw
```

**測試前置條件**:
- PowerAutomation 測試服務器已啟動並運行
- SmartInvention-Manus HITL 模塊已正確集成並啟用
- 使用者 API Key 有效且具備相應權限

**測試步驟與API檢查點**:

1. **步驟1 (Create)**: 提交常規請求
   - **操作**: POST /api/process
   - **請求體**: 
     ```json
     {
       "request": "我需要一份關於人工智能發展趨勢的詳細報告",
       "context": {
         "source": "web_interface",
         "user_role": "user",
         "workflow_type": "general_inquiry",
         "priority": "normal"
       }
     }
     ```
   - **Headers**: X-API-Key: user_RcmKEIPfGCQrA6sSohzn5NDXYMsS5mkyP9jPhM3llTw
   - **🔍 檢查點1**: HTTP 狀態碼為 200
   - **驗證**: 請求成功提交，進入 HITL 處理流程

2. **步驟2 (Read)**: 獲取處理結果
   - **操作**: 從步驟1的響應中提取處理結果
   - **🔍 檢查點2**: 響應包含 result 字段
   - **🔍 檢查點3**: 包含 metadata 字段，顯示 HITL 狀態
   - **🔍 檢查點4**: 包含 manus_direct_response 字段
   - **驗證**: 處理結果結構完整

3. **步驟3 (Validate)**: 驗證 HITL 流程
   - **操作**: 檢查響應中的 HITL 相關字段
   - **🔍 檢查點5**: user_role 識別為 "user"
   - **🔍 檢查點6**: system_type 為 "smartinvention_manus_integrated"
   - **🔍 檢查點7**: tools_used 包含 ['smartinvention_mcp', 'manus_adapter', 'hitl_review']
   - **🔍 檢查點8**: manus_direct_available 為 true
   - **驗證**: HITL 流程正確執行

**預期結果**:
- **檢查點1**: HTTP 200 OK，請求成功處理
- **檢查點2**: 響應包含完整的處理結果
- **檢查點3**: metadata 包含 HITL 狀態信息：
  ```json
  {
    "hitl_status": "completed",
    "review_required": false,
    "processing_mode": "user_mode",
    "manus_direct_available": true
  }
  ```
- **檢查點4**: manus_direct_response 包含 Manus 的直接回覆
- **檢查點5**: user_role 正確識別為 "user"
- **檢查點6**: system_type 正確顯示集成狀態
- **檢查點7**: tools_used 顯示正確的工具鏈
- **檢查點8**: Manus 直接回覆可用

**失敗判斷標準**:
- HTTP 狀態碼不是 200
- 響應結構不完整或缺少關鍵字段
- HITL 流程未正確執行
- 角色識別錯誤
- Manus 回覆不可用或內容不符合預期

---

### 測試用例 3: 管理員系統監控測試

**測試類型**: API型測試  
**業務模塊**: PowerAutomation Core, System Management  
**測試ID**: PA_ADMIN_SYS_001  

**測試描述**:  
驗證管理員獲取系統狀態、統計信息和執行系統管理操作的能力。

**測試目的**:  
- 驗證管理員角色的系統監控功能
- 確保系統狀態信息準確性
- 驗證管理員權限和操作能力

**環境前置條件**:
```yaml
硬件環境:
  - 設備類型: 任何支持 Python 的計算機
  - 內存: >=4GB

軟件環境:
  - Python版本: >=3.8
  - 測試庫: requests, json, time
  - PowerAutomation服務器: 運行中

網絡環境:
  - 網絡連接: 穩定
  - 服務器可訪問性: http://127.0.0.1:8080

權限要求:
  - 管理員 API Key: admin_pth4jG-nVjvGaTZA2URN7SyHu-o7wBaeLOYbMrLMKkc
```

**測試前置條件**:
- PowerAutomation 測試服務器已啟動並運行
- 管理員 API Key 有效且具備最高權限
- 系統已有一定的運行數據

**測試步驟與API檢查點**:

1. **步驟1 (Read)**: 獲取系統狀態
   - **操作**: GET /api/status
   - **Headers**: X-API-Key: admin_pth4jG-nVjvGaTZA2URN7SyHu-o7wBaeLOYbMrLMKkc
   - **🔍 檢查點1**: HTTP 狀態碼為 200
   - **🔍 檢查點2**: 響應包含系統運行時間
   - **🔍 檢查點3**: 響應包含 API Keys 統計
   - **🔍 檢查點4**: 響應包含功能特性列表
   - **驗證**: 系統狀態信息完整且準確

2. **步驟2 (Validate)**: 驗證管理員權限
   - **操作**: 檢查響應中的管理員專屬信息
   - **🔍 檢查點5**: 響應包含詳細的系統配置信息
   - **🔍 檢查點6**: 響應包含各模塊的運行狀態
   - **🔍 檢查點7**: 響應包含錯誤日誌統計
   - **🔍 檢查點8**: 響應包含性能指標
   - **驗證**: 管理員能夠獲取完整的系統監控信息

3. **步驟3 (Monitor)**: 監控系統健康狀態
   - **操作**: 分析系統狀態響應中的健康指標
   - **🔍 檢查點9**: test_flow_mcp 模塊狀態為 enabled
   - **🔍 檢查點10**: smartinvention_mcp 模塊狀態為 enabled
   - **🔍 檢查點11**: 系統運行時間 > 0
   - **🔍 檢查點12**: 錯誤率在可接受範圍內
   - **驗證**: 系統整體健康狀態良好

**預期結果**:
- **檢查點1**: HTTP 200 OK，管理員權限驗證成功
- **檢查點2**: 系統運行時間信息準確
- **檢查點3**: API Keys 統計信息：
  ```json
  {
    "api_keys_count": 3,
    "active_keys": ["dev_xxx", "user_xxx", "admin_xxx"],
    "key_permissions": {...}
  }
  ```
- **檢查點4**: 功能特性列表完整
- **檢查點5**: 詳細系統配置信息可見
- **檢查點6**: 各模塊運行狀態正常
- **檢查點7**: 錯誤日誌統計可用
- **檢查點8**: 性能指標在正常範圍
- **檢查點9-10**: 核心模塊狀態為 enabled
- **檢查點11**: 系統運行時間合理
- **檢查點12**: 系統健康狀態良好

**失敗判斷標準**:
- HTTP 狀態碼不是 200
- 管理員權限驗證失敗
- 系統狀態信息不完整或不準確
- 核心模塊狀態異常
- 系統健康指標超出正常範圍

---

## 測試用例格式說明

### 標準化字段
- **測試類型**: API型測試
- **業務模塊**: 對應的功能模塊
- **測試ID**: 格式為 PA_[角色]_[模塊]_[序號]
- **測試描述**: 簡明扼要說明測試內容
- **測試目的**: 明確測試要達到的目標
- **環境前置條件**: YAML格式的環境要求
- **測試前置條件**: 測試開始前需要滿足的狀態
- **測試步驟與API檢查點**: 詳細的API操作步驟和驗證點
- **預期結果**: 每個檢查點的具體期望
- **失敗判斷標準**: 明確的失敗條件

### API檢查點規範
- 使用 🔍 符號標識API檢查點
- 每個關鍵API操作都有對應的驗證
- 檢查點包含HTTP狀態碼、響應結構、數據內容等多層驗證
- 支持JSON響應的深度驗證

### 角色權限標準
- **開發者**: 專注於 test_flow_mcp 功能測試
- **使用者**: 專注於 SmartInvention-Manus HITL 流程測試
- **管理員**: 專注於系統監控和管理功能測試

這個範例將作為後續Python腳本生成的標準模板。

