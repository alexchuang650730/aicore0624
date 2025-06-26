# 需求分析集成測試案例說明

## 測試檔案
`test_requirement_analysis_integration.py`

## 測試目的
驗證 PowerAutomation 系統中需求分析工作流和 test_flow_mcp 集成的完整功能。

## 測試項目

### 1. 服務器連接性測試 (Server Connectivity Test)
**測試目標**: 檢查測試服務器是否能夠正常連接並返回狀態信息
- **測試地址**: `http://127.0.0.1:8080/api/status`
- **預期結果**: 返回 HTTP 200 狀態碼
- **驗證內容**: 服務器基本可用性

### 2. API Key 認證測試 (API Key Authentication Test)
**測試目標**: 驗證系統的 API Key 認證機制
- **無 API Key 測試**: 
  - 發送不帶 API Key 的請求
  - 預期結果: HTTP 401 Unauthorized
- **有效 API Key 測試**:
  - 使用開發者 API Key: `dev_407CYuVK...`
  - 預期結果: HTTP 200 OK
- **驗證內容**: 認證機制正常工作

### 3. 需求分析工作流測試 (Requirement Analysis Workflow Test)
**測試目標**: 測試系統處理需求分析請求的端到端流程
- **測試請求**: "我想要多了解本系統的架構和功能"
- **請求上下文**:
  - source: "vscode_vsix"
  - user_role: "developer"
  - workflow_type: "requirement_analysis"
  - test_scenario: "system_architecture_inquiry"
- **驗證內容**:
  - 響應包含必要欄位 ['success', 'user_role', 'message']
  - 正確識別為開發者角色
  - 包含處理結果

### 4. test_flow_mcp 集成測試 (test_flow_mcp Integration Test)
**測試目標**: 測試 test_flow_mcp 模塊在系統中的集成情況
- **測試請求**: "請分析當前系統的測試覆蓋率並提供改進建議"
- **請求上下文**:
  - source: "vscode_vsix"
  - user_role: "developer"
  - workflow_type: "test_flow_analysis"
  - target_component: "test_flow_mcp"
  - analysis_type: "coverage_analysis"
- **驗證內容**:
  - 觸發開發者模式
  - 響應包含測試相關關鍵詞 ['test', 'coverage', 'analysis', 'mcp', 'flow']

### 5. 開發者與使用者角色區分測試 (Developer vs. User Role Differentiation Test)
**測試目標**: 驗證系統正確區分開發者角色
- **測試請求**: "開發者測試請求"
- **請求上下文**: source: "vscode_vsix"
- **驗證內容**: 響應中正確識別 user_role 為 "developer"

## 測試配置

### 服務器設定
- **URL**: `http://127.0.0.1:8080`
- **API Key**: `dev_407CYuVKuP_s3hVqIhO4JZKqcE4-W9ocTgc_fldjxso`

### 測試流程
1. 依序執行 5 個測試項目
2. 每個測試間隔 1 秒
3. 記錄所有測試結果
4. 生成測試報告並保存為 JSON 文件

### 測試結果輸出
- **即時輸出**: 每個測試的通過/失敗狀態
- **最終報告**: 
  - 總測試數
  - 通過測試數
  - 失敗測試數
  - 成功率百分比
- **結果文件**: `requirement_analysis_test_results_YYYYMMDD_HHMMSS.json`

## 成功標準
所有 5 個測試項目都必須通過，整體成功率達到 100%。

## 測試重點
這個測試案例主要驗證：
1. **系統基礎功能**: 連接性和認證
2. **核心工作流**: 需求分析處理流程
3. **模塊集成**: test_flow_mcp 的正確集成
4. **角色管理**: 開發者角色的正確識別和處理

