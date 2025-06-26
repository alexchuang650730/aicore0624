# Tests

這個目錄包含所有 PowerAutomation 相關項目的測試文件，服務於：

- **powerautomation** - 核心 PowerAutomation 系統
- **powerautomation_web** - Web 版本
- **powerautomation_local** - 本地版本

## 目錄結構

```
tests/
├── api_tests/              # API 接口功能測試
│   ├── admin_tests/        # 管理員角色 API 測試
│   ├── developer_tests/    # 開發者角色 API 測試
│   ├── user_tests/         # 使用者角色 API 測試
│   ├── smartinvention_examples/  # SmartInvention API 範例
│   └── run_all_api_tests.py      # 統一 API 測試運行器
├── ui_operation_tests/     # UI 界面操作測試
├── ui_usability_tests/     # UI 易用性測試
├── templates/              # 測試模板
├── generators/             # 測試生成器
├── testcases/              # 測試案例
└── results/                # 測試結果
```

## 三種測試分類

### 1. API 測試 (api_tests/)
- **目的**: 測試接口功能和數據交互
- **內容**: REST API、GraphQL、WebSocket 等接口測試
- **角色分類**: 
  - `admin_tests/` - 管理員權限 API
  - `developer_tests/` - 開發者權限 API  
  - `user_tests/` - 一般使用者權限 API
- **範例**: SmartInvention API 使用範例

### 2. UI 操作測試 (ui_operation_tests/)
- **目的**: 測試界面操作和功能流程
- **內容**: 按鈕點擊、表單提交、頁面導航等操作測試
- **技術**: Selenium、Playwright 等自動化工具

### 3. UI 易用性測試 (ui_usability_tests/)
- **目的**: 測試用戶體驗和界面易用性
- **內容**: 用戶流程、界面響應、可訪問性等測試
- **重點**: 真實用戶場景和體驗評估

## 主要測試案例

### 需求分析集成測試
- **路徑**: `testcases/requirement_analysis/`
- **主文件**: `test_requirement_analysis_integration.py`
- **功能**: 測試 test_flow_mcp 的需求分析工作流
- **支持**: 所有 PowerAutomation 實體

### SmartInvention API 測試
- **路徑**: `api_tests/smartinvention_examples/`
- **主文件**: `test_api_suite.py`
- **功能**: 完整的 SmartInvention API 測試套件
- **配置**: `test_config.json`

## 運行測試

```shell
# API 測試
cd tests/api_tests/
python run_all_api_tests.py

# SmartInvention API 測試
cd tests/api_tests/smartinvention_examples/
python run_tests.py

# 需求分析測試
cd tests/testcases/requirement_analysis/
python test_requirement_analysis_integration.py

# UI 操作測試
cd tests/ui_operation_tests/
# (待實現)

# UI 易用性測試
cd tests/ui_usability_tests/
# (待實現)
```

## 測試結果

測試結果會自動保存到相應目錄下的 JSON 文件中，命名格式：
- `{test_name}_test_results_{timestamp}.json`

## 配置

測試配置支持多個 PowerAutomation 實體：
- 通過環境變量或配置文件指定目標實體
- 自動適配不同實體的 API 端點和認證方式

## 測試原則

**拋棄傳統無意義分類：**
- ❌ unit test - 大多是 mock test，測假數據
- ❌ integration test - 很少真正集成多個系統
- ❌ e2e test - 從來不是真正的端到端

**採用實用分類：**
- ✅ API 測試 - 真實的 API 調用和響應
- ✅ UI 操作測試 - 真實的界面操作和用戶行為
- ✅ UI 易用性測試 - 真實的用戶體驗和使用場景

