# TEST_FLOW API 測試標準操作程序 (SOP)

**文檔版本**: v1.0  
**創建日期**: 2025-06-25  
**作者**: Manus AI  
**適用範圍**: PowerAutomation test_flow_mcp API 測試  
**文檔狀態**: 正式版本  

---

## 📋 文檔概述

本標準操作程序 (SOP) 旨在為 PowerAutomation 系統中的 test_flow_mcp 組件提供完整、系統化的 API 測試指導方針。文檔涵蓋從測試環境準備、測試案例設計、執行流程到結果分析的全生命週期管理，確保 API 測試的一致性、可重複性和高品質。

test_flow_mcp 作為 PowerAutomation 系統的核心測試流程管理組件，負責協調和執行各種測試工作流程，包括需求分析測試、集成測試、效能測試等多個層面。其 API 接口的穩定性和可靠性直接影響整個系統的測試品質和開發效率。因此，建立規範化的 API 測試流程對於保障系統品質具有重要意義。

本文檔遵循業界最佳實務，結合 PowerAutomation 系統的特殊需求，提供了詳細的操作指南、測試模板和故障排除方案。無論是新加入的測試工程師還是經驗豐富的開發人員，都可以通過本文檔快速掌握 test_flow API 測試的標準流程。

---

## 🎯 測試目標與範圍

### 主要測試目標

test_flow API 測試的核心目標是確保所有 API 端點在各種條件下都能正確、穩定地運行。具體包括功能正確性驗證、效能指標達標、安全性保障、相容性確認等多個維度。我們需要通過系統化的測試方法，發現潛在的缺陷和風險，並提供改進建議。

功能正確性驗證是最基礎也是最重要的測試目標。每個 API 端點都必須按照設計規範正確處理輸入參數，返回預期的結果格式，並正確處理各種異常情況。這包括正常流程測試、邊界值測試、異常處理測試等多個層面。

效能指標達標確保 API 在預期的負載條件下能夠維持良好的響應時間和吞吐量。我們需要測試不同併發級別下的 API 表現，識別效能瓶頸，並驗證系統的擴展性。

安全性保障涉及身份驗證、授權控制、數據保護等多個方面。我們需要確保 API 能夠正確處理各種安全威脅，保護敏感數據不被未授權訪問。

### 測試範圍定義

test_flow_mcp 的 API 測試範圍涵蓋所有對外暴露的 REST API 端點，包括但不限於測試案例管理、測試執行控制、結果查詢、系統狀態監控等功能模組。每個端點都需要進行全面的測試覆蓋，包括不同的 HTTP 方法、參數組合、認證狀態等。

核心 API 端點包括 `/api/test/execute`、`/api/test/status`、`/api/test/results`、`/api/system/health` 等。這些端點承載著系統的主要功能，需要重點關注其穩定性和效能表現。

輔助 API 端點如配置管理、日誌查詢、統計報告等，雖然不是核心業務流程，但同樣需要確保其正確性和可用性。

測試範圍還包括 API 之間的交互測試，驗證不同端點之間的數據一致性和業務邏輯的正確性。例如，測試執行後的狀態查詢應該反映實際的執行結果。

### 測試層級劃分

API 測試按照複雜度和依賴關係分為三個層級：單元級 API 測試、集成級 API 測試和端到端 API 測試。

單元級 API 測試專注於單個 API 端點的功能驗證，不涉及外部依賴。這類測試執行速度快，可以快速發現基礎功能問題。測試內容包括參數驗證、返回值格式檢查、錯誤處理等。

集成級 API 測試驗證多個 API 端點之間的協作關係，以及與外部系統的集成。這類測試需要搭建相對完整的測試環境，模擬真實的使用場景。

端到端 API 測試模擬完整的業務流程，從用戶請求到最終結果的全鏈路驗證。這類測試最接近實際使用情況，但執行時間較長，通常用於重要版本發布前的最終驗證。

---


## 🛠️ 測試環境準備

### 基礎環境需求

建立穩定可靠的測試環境是成功執行 API 測試的基礎。test_flow_mcp API 測試環境需要滿足特定的硬體和軟體需求，以確保測試結果的準確性和可重複性。

硬體環境方面，推薦使用至少 8GB RAM、4 核心 CPU 的服務器或虛擬機。存儲空間需要預留至少 50GB 用於系統運行、日誌存儲和測試數據管理。網路環境需要穩定的互聯網連接，支援 HTTPS 協議，並確保與 PowerAutomation 系統的其他組件能夠正常通信。

軟體環境包括作業系統、運行時環境、測試工具等多個層面。推薦使用 Ubuntu 22.04 LTS 或 CentOS 8 作為基礎作業系統，確保系統的穩定性和安全性。Python 3.11+ 作為主要的運行時環境，需要安裝相關的依賴包和測試框架。

Docker 容器化技術的使用可以大大簡化環境配置和管理。我們提供了標準的 Docker 鏡像，包含了所有必要的依賴和配置，可以快速部署一致的測試環境。

### PowerAutomation 系統配置

PowerAutomation 系統的正確配置是 API 測試的前提條件。系統配置包括核心服務啟動、組件註冊、權限設置等多個步驟。

首先需要確保 PowerAutomation 核心服務正常運行。這包括 AICore 引擎、MCP 協調器、數據存儲服務等核心組件。每個組件都需要進行健康檢查，確保其處於可用狀態。

```bash
# 檢查核心服務狀態
curl -X GET http://localhost:8080/api/system/health
curl -X GET http://localhost:8080/api/mcp/status
curl -X GET http://localhost:8080/api/storage/health
```

test_flow_mcp 組件需要正確註冊到系統中，並配置相應的權限和資源限制。組件配置文件通常位於 `PowerAutomation/config/` 目錄下，需要根據測試環境的具體情況進行調整。

數據庫配置是另一個重要環節。test_flow_mcp 依賴數據庫存儲測試案例、執行記錄、結果數據等信息。需要確保數據庫服務正常運行，並且 test_flow_mcp 具有適當的讀寫權限。

### API 認證配置

test_flow_mcp API 使用基於 API Key 的認證機制，確保只有授權的客戶端才能訪問 API 端點。認證配置包括 API Key 生成、權限分配、安全策略設置等步驟。

API Key 的生成需要遵循安全最佳實務，使用足夠長度的隨機字符串，並包含角色標識前綴。開發環境使用 `dev_` 前綴，測試環境使用 `test_` 前綴，生產環境使用 `prod_` 前綴。

```bash
# 生成測試用 API Key
export TEST_API_KEY="test_$(openssl rand -base64 32 | tr -d '=+/' | cut -c1-32)"
echo "Generated API Key: $TEST_API_KEY"
```

權限分配需要根據測試需求設置適當的訪問級別。一般測試場景下，API Key 需要具備讀取測試案例、執行測試、查詢結果等基本權限。對於安全性測試，可能需要配置受限權限的 API Key 來驗證授權控制的正確性。

安全策略包括請求頻率限制、IP 白名單、加密傳輸等多個方面。測試環境中可以適當放寬限制以便於測試執行，但仍需要保持基本的安全防護。

### 測試數據準備

測試數據的準備是 API 測試成功的關鍵因素之一。高質量的測試數據能夠幫助發現更多的潛在問題，提高測試的有效性。

測試數據包括正常數據、邊界數據、異常數據等多種類型。正常數據用於驗證 API 的基本功能，應該覆蓋常見的使用場景。邊界數據用於測試 API 對極值情況的處理能力，包括最大值、最小值、空值等。異常數據用於測試 API 的錯誤處理機制，包括格式錯誤、類型錯誤、邏輯錯誤等。

測試案例數據是 test_flow_mcp API 測試的核心。需要準備不同類型、不同複雜度的測試案例，涵蓋需求分析、功能測試、集成測試等多個場景。每個測試案例都應該包含完整的元數據，如案例名稱、描述、預期結果、執行條件等。

```json
{
  "test_case_id": "TC_REQ_ANALYSIS_001",
  "name": "需求分析基礎功能測試",
  "description": "驗證需求分析 API 的基本功能",
  "input_data": {
    "requirement_text": "用戶需要一個能夠自動分析代碼品質的功能",
    "analysis_type": "functional",
    "priority": "high"
  },
  "expected_output": {
    "analysis_result": {
      "feasibility": "high",
      "complexity": "medium",
      "estimated_effort": "5-8 hours"
    }
  }
}
```

測試環境數據需要與生產環境保持一定的相似性，但不能包含真實的敏感信息。可以使用數據脫敏技術生成仿真數據，或者使用專門的測試數據生成工具創建符合要求的測試數據集。

### 監控和日誌配置

完善的監控和日誌系統對於 API 測試的執行和問題診斷至關重要。需要配置適當的監控指標收集和日誌記錄機制。

系統監控包括 CPU 使用率、內存使用率、磁盤 I/O、網路流量等基礎指標。這些指標可以幫助識別系統資源瓶頸，評估 API 的效能表現。

應用監控專注於 API 層面的指標，包括請求響應時間、吞吐量、錯誤率、併發數等。這些指標直接反映 API 的服務質量和用戶體驗。

```bash
# 配置 Prometheus 監控
cat > prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'test-flow-mcp'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/api/metrics'
    scrape_interval: 10s
EOF
```

日誌配置需要平衡詳細程度和性能影響。測試環境中可以啟用較為詳細的日誌級別，記錄 API 請求的完整信息，包括請求參數、處理過程、響應結果等。日誌格式應該統一，便於後續的分析和處理。

結構化日誌格式如 JSON 可以提高日誌的可讀性和可分析性。每條日誌記錄都應該包含時間戳、日誌級別、組件名稱、請求 ID、具體消息等基本信息。

---


## 📚 API 端點詳細說明

### 核心測試執行 API

test_flow_mcp 的核心功能通過一系列 REST API 端點對外提供服務。這些端點承載著測試流程的主要業務邏輯，是 API 測試的重點關注對象。

#### POST /api/test/execute

測試執行端點是 test_flow_mcp 最重要的 API 之一，負責接收測試請求並啟動相應的測試流程。該端點支援多種測試類型，包括需求分析測試、功能測試、集成測試、效能測試等。

請求格式採用 JSON 結構，包含測試類型、測試參數、執行選項等信息。系統會根據請求內容自動選擇合適的測試引擎和執行策略。

```json
{
  "test_type": "requirement_analysis",
  "test_parameters": {
    "requirement_text": "實現用戶登錄功能，支援郵箱和手機號登錄",
    "analysis_depth": "detailed",
    "include_security_check": true
  },
  "execution_options": {
    "timeout": 300,
    "priority": "high",
    "notification_enabled": true
  }
}
```

響應格式包含測試任務 ID、執行狀態、預估完成時間等信息。客戶端可以使用任務 ID 來查詢測試進度和獲取最終結果。

```json
{
  "success": true,
  "task_id": "task_20250625_115530_001",
  "status": "running",
  "estimated_completion": "2025-06-25T12:00:30Z",
  "message": "測試任務已成功啟動"
}
```

該端點的測試重點包括參數驗證、任務創建、狀態管理、錯誤處理等方面。需要驗證不同測試類型的正確處理，以及異常情況下的錯誤響應。

#### GET /api/test/status/{task_id}

測試狀態查詢端點用於獲取指定測試任務的當前執行狀態。該端點支援實時狀態查詢，客戶端可以通過輪詢方式監控測試進度。

路徑參數 `task_id` 是測試任務的唯一標識符，由測試執行端點返回。系統會根據任務 ID 查找對應的測試實例，並返回詳細的狀態信息。

響應內容包括任務基本信息、執行進度、當前階段、錯誤信息等。對於長時間運行的測試任務，還會提供階段性的進度報告。

```json
{
  "success": true,
  "task_id": "task_20250625_115530_001",
  "status": "running",
  "progress": {
    "current_stage": "requirement_parsing",
    "completion_percentage": 35,
    "stages_completed": ["initialization", "validation"],
    "stages_remaining": ["analysis", "report_generation"]
  },
  "execution_time": 180,
  "estimated_remaining": 120
}
```

狀態查詢的測試需要覆蓋不同的任務狀態，包括排隊中、執行中、已完成、失敗、取消等。還需要測試無效任務 ID 的處理，以及併發查詢的正確性。

#### GET /api/test/results/{task_id}

測試結果獲取端點用於檢索已完成測試任務的詳細結果。該端點只對狀態為 "completed" 的任務返回結果數據，對於未完成的任務會返回相應的狀態信息。

結果數據的格式根據測試類型而有所不同，但都遵循統一的結構規範。基本結構包括任務元數據、執行摘要、詳細結果、建議和附件等部分。

```json
{
  "success": true,
  "task_id": "task_20250625_115530_001",
  "test_type": "requirement_analysis",
  "execution_summary": {
    "start_time": "2025-06-25T11:55:30Z",
    "end_time": "2025-06-25T12:00:30Z",
    "duration": 300,
    "status": "completed"
  },
  "results": {
    "analysis_score": 85,
    "feasibility": "high",
    "complexity_estimate": "medium",
    "identified_risks": [
      "需要考慮多因素認證的實現複雜度",
      "手機號驗證可能涉及第三方服務依賴"
    ],
    "recommendations": [
      "建議優先實現郵箱登錄功能",
      "手機號登錄可以作為第二階段功能"
    ]
  }
}
```

結果獲取的測試需要驗證不同測試類型的結果格式，確保數據的完整性和正確性。還需要測試大型結果數據的傳輸效率，以及結果數據的持久化存儲。

### 系統管理 API

系統管理 API 提供了監控、配置、維護等功能，是確保 test_flow_mcp 穩定運行的重要工具。

#### GET /api/system/health

系統健康檢查端點提供了 test_flow_mcp 組件的整體健康狀態信息。該端點通常用於負載均衡器的健康檢查，以及監控系統的狀態監控。

健康檢查包括多個維度的狀態驗證，如服務可用性、依賴組件狀態、資源使用情況、關鍵功能可用性等。每個維度都有相應的檢查邏輯和閾值設定。

```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2025-06-25T12:00:00Z",
  "components": {
    "database": {
      "status": "healthy",
      "response_time": 15,
      "connection_pool": "8/20"
    },
    "mcp_coordinator": {
      "status": "healthy",
      "last_heartbeat": "2025-06-25T11:59:55Z"
    },
    "test_engines": {
      "status": "healthy",
      "active_tasks": 3,
      "queue_length": 1
    }
  },
  "system_metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 68.7,
    "disk_usage": 23.1
  }
}
```

健康檢查的測試需要模擬各種系統狀態，包括正常狀態、警告狀態、異常狀態等。還需要驗證在組件故障情況下的狀態報告準確性。

#### GET /api/system/metrics

系統指標端點提供了詳細的性能和運行指標，用於監控系統的運行狀況和性能表現。指標數據通常以 Prometheus 格式輸出，便於與監控系統集成。

指標類型包括計數器、儀表盤、直方圖、摘要等，涵蓋了 API 請求量、響應時間、錯誤率、資源使用率等多個維度。

```
# HELP test_flow_api_requests_total Total number of API requests
# TYPE test_flow_api_requests_total counter
test_flow_api_requests_total{method="POST",endpoint="/api/test/execute"} 1247
test_flow_api_requests_total{method="GET",endpoint="/api/test/status"} 3891

# HELP test_flow_api_request_duration_seconds API request duration
# TYPE test_flow_api_request_duration_seconds histogram
test_flow_api_request_duration_seconds_bucket{le="0.1"} 892
test_flow_api_request_duration_seconds_bucket{le="0.5"} 1456
test_flow_api_request_duration_seconds_bucket{le="1.0"} 1678
```

指標端點的測試需要驗證指標數據的準確性和完整性，確保所有重要的運行指標都被正確記錄和輸出。

### 配置管理 API

配置管理 API 允許動態調整 test_flow_mcp 的運行參數，無需重啟服務即可生效。這對於測試環境的靈活配置和生產環境的運行時調優都非常重要。

#### GET /api/config

配置查詢端點返回當前的系統配置信息。為了安全考慮，敏感配置項（如密碼、密鑰等）會被遮罩處理。

```json
{
  "success": true,
  "config": {
    "test_execution": {
      "max_concurrent_tasks": 10,
      "default_timeout": 300,
      "retry_attempts": 3
    },
    "api_settings": {
      "rate_limit": 100,
      "max_request_size": "10MB",
      "cors_enabled": true
    },
    "logging": {
      "level": "INFO",
      "max_file_size": "100MB",
      "retention_days": 30
    }
  }
}
```

#### PUT /api/config

配置更新端點允許修改系統配置。更新操作需要適當的權限驗證，並且會進行配置值的有效性檢查。

```json
{
  "test_execution": {
    "max_concurrent_tasks": 15,
    "default_timeout": 600
  },
  "logging": {
    "level": "DEBUG"
  }
}
```

配置管理 API 的測試需要驗證權限控制、參數驗證、配置生效等功能。還需要測試無效配置的處理和配置回滾機制。

---


## 🎨 測試案例設計

### 測試案例分類體系

有效的測試案例設計是 API 測試成功的關鍵。test_flow_mcp API 測試案例按照不同的維度進行分類，形成完整的測試覆蓋體系。

功能性測試案例專注於驗證 API 的業務邏輯正確性。這類測試案例基於需求規格和 API 文檔設計，確保每個端點都能按照預期處理各種輸入並返回正確的結果。功能性測試是最基礎也是最重要的測試類型，通常佔整個測試案例集的 60-70%。

非功能性測試案例關注 API 的性能、安全性、可用性等品質屬性。這類測試案例包括負載測試、壓力測試、安全測試、相容性測試等。雖然數量相對較少，但對於保證系統的整體品質同樣重要。

邊界測試案例專門針對輸入參數的邊界值進行測試。這包括最大值、最小值、空值、null 值、特殊字符等各種邊界情況。邊界測試能夠發現許多隱藏的缺陷，特別是在參數驗證和錯誤處理方面。

異常測試案例模擬各種異常情況，驗證 API 的錯誤處理能力。這包括無效參數、網路異常、系統故障、資源不足等情況。良好的異常處理能夠提高系統的穩定性和用戶體驗。

### 正向測試案例設計

正向測試案例驗證 API 在正常條件下的功能表現。這類測試案例使用有效的輸入參數，期望得到成功的響應結果。

#### 基礎功能測試案例

基礎功能測試驗證每個 API 端點的核心功能。以測試執行 API 為例，基礎功能測試需要涵蓋不同測試類型的執行請求。

```json
{
  "test_case_id": "TC_EXEC_001",
  "name": "需求分析測試執行",
  "description": "驗證需求分析類型的測試執行功能",
  "api_endpoint": "POST /api/test/execute",
  "request_data": {
    "test_type": "requirement_analysis",
    "test_parameters": {
      "requirement_text": "用戶希望能夠快速搜索產品信息",
      "analysis_depth": "standard"
    },
    "execution_options": {
      "timeout": 180,
      "priority": "medium"
    }
  },
  "expected_response": {
    "status_code": 200,
    "response_body": {
      "success": true,
      "task_id": "string",
      "status": "running",
      "estimated_completion": "datetime"
    }
  },
  "validation_rules": [
    "task_id 應為非空字符串",
    "status 應為 'running' 或 'queued'",
    "estimated_completion 應為有效的 ISO 8601 時間格式"
  ]
}
```

每個基礎功能測試案例都需要明確定義輸入數據、預期輸出、驗證規則等要素。輸入數據應該代表典型的使用場景，預期輸出應該符合 API 規格說明。

#### 參數組合測試案例

參數組合測試驗證不同參數組合下的 API 行為。由於 API 通常支援多個可選參數，需要測試各種參數組合的正確性。

```json
{
  "test_case_id": "TC_EXEC_002",
  "name": "完整參數組合測試",
  "description": "驗證包含所有可選參數的測試執行",
  "request_data": {
    "test_type": "integration_test",
    "test_parameters": {
      "target_components": ["component_a", "component_b"],
      "test_scenarios": ["scenario_1", "scenario_2"],
      "environment": "staging",
      "data_set": "sample_data_v2"
    },
    "execution_options": {
      "timeout": 600,
      "priority": "high",
      "notification_enabled": true,
      "parallel_execution": false,
      "retry_on_failure": true,
      "max_retries": 2
    }
  },
  "expected_response": {
    "status_code": 200,
    "response_body": {
      "success": true,
      "task_id": "string",
      "status": "running"
    }
  }
}
```

參數組合測試需要考慮參數之間的相互影響和約束關係。某些參數組合可能是無效的，需要相應的測試案例來驗證錯誤處理。

#### 數據類型測試案例

數據類型測試驗證 API 對不同數據類型的正確處理。這包括字符串、數字、布爾值、數組、對象等各種 JSON 數據類型。

```json
{
  "test_case_id": "TC_EXEC_003",
  "name": "數據類型驗證測試",
  "description": "驗證不同數據類型參數的正確處理",
  "test_variations": [
    {
      "variation_name": "字符串參數",
      "request_data": {
        "test_type": "functional_test",
        "test_parameters": {
          "test_name": "用戶登錄功能測試",
          "description": "驗證用戶登錄的各種場景"
        }
      }
    },
    {
      "variation_name": "數值參數",
      "request_data": {
        "test_type": "performance_test",
        "test_parameters": {
          "concurrent_users": 100,
          "test_duration": 300,
          "ramp_up_time": 60
        }
      }
    },
    {
      "variation_name": "布爾參數",
      "request_data": {
        "test_type": "security_test",
        "test_parameters": {
          "include_authentication": true,
          "test_authorization": false,
          "check_input_validation": true
        }
      }
    }
  ]
}
```

### 負向測試案例設計

負向測試案例驗證 API 在異常條件下的行為表現。這類測試案例使用無效或異常的輸入，期望得到適當的錯誤響應。

#### 參數驗證測試案例

參數驗證測試確保 API 能夠正確識別和處理無效的輸入參數。這是 API 安全性和穩定性的重要保障。

```json
{
  "test_case_id": "TC_EXEC_NEG_001",
  "name": "缺少必需參數測試",
  "description": "驗證缺少必需參數時的錯誤處理",
  "request_data": {
    "test_parameters": {
      "requirement_text": "用戶登錄功能"
    }
  },
  "expected_response": {
    "status_code": 400,
    "response_body": {
      "success": false,
      "error_code": "MISSING_REQUIRED_PARAMETER",
      "message": "缺少必需參數: test_type",
      "details": {
        "missing_parameters": ["test_type"]
      }
    }
  }
}
```

參數驗證測試需要覆蓋各種無效參數情況，包括缺少必需參數、參數類型錯誤、參數值超出範圍、參數格式不正確等。

#### 業務邏輯錯誤測試案例

業務邏輯錯誤測試驗證 API 對業務規則違反的處理。這類測試案例模擬違反業務約束的請求，確保 API 能夠正確識別並返回相應的錯誤信息。

```json
{
  "test_case_id": "TC_EXEC_NEG_002",
  "name": "無效測試類型測試",
  "description": "驗證不支援的測試類型的錯誤處理",
  "request_data": {
    "test_type": "unsupported_test_type",
    "test_parameters": {
      "requirement_text": "測試需求"
    }
  },
  "expected_response": {
    "status_code": 400,
    "response_body": {
      "success": false,
      "error_code": "INVALID_TEST_TYPE",
      "message": "不支援的測試類型: unsupported_test_type",
      "details": {
        "supported_types": [
          "requirement_analysis",
          "functional_test",
          "integration_test",
          "performance_test"
        ]
      }
    }
  }
}
```

#### 系統狀態錯誤測試案例

系統狀態錯誤測試模擬系統處於異常狀態時的 API 行為。這包括系統過載、資源不足、依賴服務不可用等情況。

```json
{
  "test_case_id": "TC_EXEC_NEG_003",
  "name": "系統過載測試",
  "description": "驗證系統達到最大併發限制時的處理",
  "preconditions": [
    "系統當前併發任務數已達到上限"
  ],
  "request_data": {
    "test_type": "requirement_analysis",
    "test_parameters": {
      "requirement_text": "新的測試需求"
    }
  },
  "expected_response": {
    "status_code": 503,
    "response_body": {
      "success": false,
      "error_code": "SERVICE_UNAVAILABLE",
      "message": "系統當前負載過高，請稍後重試",
      "details": {
        "retry_after": 60,
        "current_queue_length": 25
      }
    }
  }
}
```

### 邊界值測試案例設計

邊界值測試專注於輸入參數的邊界條件，這些條件往往是缺陷的高發區域。邊界值測試需要考慮數值邊界、字符串長度邊界、數組大小邊界等多個方面。

#### 數值邊界測試

數值邊界測試驗證 API 對數值參數邊界值的處理。這包括最大值、最小值、零值、負值等情況。

```json
{
  "test_case_id": "TC_BOUNDARY_001",
  "name": "超時參數邊界測試",
  "description": "驗證超時參數的邊界值處理",
  "test_variations": [
    {
      "variation_name": "最小值",
      "request_data": {
        "test_type": "requirement_analysis",
        "test_parameters": {
          "requirement_text": "測試需求"
        },
        "execution_options": {
          "timeout": 1
        }
      },
      "expected_response": {
        "status_code": 200
      }
    },
    {
      "variation_name": "最大值",
      "request_data": {
        "execution_options": {
          "timeout": 3600
        }
      },
      "expected_response": {
        "status_code": 200
      }
    },
    {
      "variation_name": "超出最大值",
      "request_data": {
        "execution_options": {
          "timeout": 3601
        }
      },
      "expected_response": {
        "status_code": 400,
        "response_body": {
          "error_code": "PARAMETER_OUT_OF_RANGE"
        }
      }
    }
  ]
}
```

#### 字符串長度邊界測試

字符串長度邊界測試驗證 API 對字符串參數長度限制的處理。這對於防止緩衝區溢出和資源耗盡攻擊非常重要。

```json
{
  "test_case_id": "TC_BOUNDARY_002",
  "name": "需求文本長度邊界測試",
  "description": "驗證需求文本參數的長度限制",
  "test_variations": [
    {
      "variation_name": "空字符串",
      "request_data": {
        "test_type": "requirement_analysis",
        "test_parameters": {
          "requirement_text": ""
        }
      },
      "expected_response": {
        "status_code": 400,
        "response_body": {
          "error_code": "EMPTY_PARAMETER"
        }
      }
    },
    {
      "variation_name": "最大長度",
      "request_data": {
        "test_parameters": {
          "requirement_text": "A".repeat(10000)
        }
      },
      "expected_response": {
        "status_code": 200
      }
    },
    {
      "variation_name": "超出最大長度",
      "request_data": {
        "test_parameters": {
          "requirement_text": "A".repeat(10001)
        }
      },
      "expected_response": {
        "status_code": 400,
        "response_body": {
          "error_code": "PARAMETER_TOO_LONG"
        }
      }
    }
  ]
}
```

### 安全性測試案例設計

安全性測試案例驗證 API 的安全防護機制，包括身份驗證、授權控制、輸入驗證、數據保護等方面。

#### 身份驗證測試案例

身份驗證測試確保只有提供有效憑證的客戶端才能訪問 API 端點。

```json
{
  "test_case_id": "TC_SECURITY_001",
  "name": "API Key 驗證測試",
  "description": "驗證 API Key 身份驗證機制",
  "test_variations": [
    {
      "variation_name": "有效 API Key",
      "request_headers": {
        "X-API-Key": "test_valid_api_key_12345"
      },
      "expected_response": {
        "status_code": 200
      }
    },
    {
      "variation_name": "無效 API Key",
      "request_headers": {
        "X-API-Key": "invalid_api_key"
      },
      "expected_response": {
        "status_code": 401,
        "response_body": {
          "error_code": "INVALID_API_KEY"
        }
      }
    },
    {
      "variation_name": "缺少 API Key",
      "request_headers": {},
      "expected_response": {
        "status_code": 401,
        "response_body": {
          "error_code": "MISSING_API_KEY"
        }
      }
    }
  ]
}
```

#### 輸入驗證安全測試案例

輸入驗證安全測試檢查 API 對惡意輸入的防護能力，包括 SQL 注入、XSS 攻擊、命令注入等。

```json
{
  "test_case_id": "TC_SECURITY_002",
  "name": "惡意輸入防護測試",
  "description": "驗證對惡意輸入的防護機制",
  "test_variations": [
    {
      "variation_name": "SQL 注入嘗試",
      "request_data": {
        "test_type": "requirement_analysis",
        "test_parameters": {
          "requirement_text": "'; DROP TABLE users; --"
        }
      },
      "expected_response": {
        "status_code": 400,
        "response_body": {
          "error_code": "INVALID_INPUT"
        }
      }
    },
    {
      "variation_name": "腳本注入嘗試",
      "request_data": {
        "test_parameters": {
          "requirement_text": "<script>alert('XSS')</script>"
        }
      },
      "expected_response": {
        "status_code": 400
      }
    }
  ]
}
```

---


## 🚀 測試執行流程

### 測試執行策略

test_flow_mcp API 測試的執行需要遵循系統化的策略，確保測試的全面性、效率性和可靠性。測試執行策略包括測試順序規劃、資源分配、並行執行、錯誤處理等多個方面。

測試執行順序應該遵循由簡到繁、由基礎到高級的原則。首先執行基礎功能測試，確保核心 API 端點的基本功能正常。然後執行參數驗證測試，驗證輸入處理的正確性。接下來是業務邏輯測試，確保複雜場景下的功能正確性。最後執行性能測試和安全測試，驗證非功能性需求。

這種分層執行策略的好處是能夠快速發現基礎問題，避免在有基礎缺陷的情況下浪費時間執行高級測試。同時，分層執行也便於問題的定位和修復。

資源分配需要考慮測試環境的硬體限制和測試案例的資源需求。CPU 密集型的測試案例應該避免同時執行，以免相互影響測試結果。網路 I/O 密集型的測試可以適當並行，但需要控制併發數量以避免網路擁塞。

### 自動化測試執行

自動化測試是 API 測試的主要執行方式，能夠提高測試效率、減少人為錯誤、支援持續集成等。test_flow_mcp API 測試的自動化執行基於 Python 測試框架實現。

#### 測試框架配置

測試框架採用 pytest 作為核心引擎，結合 requests 庫進行 HTTP 請求處理，使用 jsonschema 進行響應驗證。框架配置文件定義了測試環境、認證信息、超時設置等基本參數。

```python
# conftest.py - pytest 配置文件
import pytest
import requests
import json
from datetime import datetime

@pytest.fixture(scope="session")
def api_client():
    """API 客戶端配置"""
    return {
        'base_url': 'http://localhost:8080',
        'api_key': 'test_api_key_12345',
        'timeout': 30,
        'headers': {
            'Content-Type': 'application/json',
            'X-API-Key': 'test_api_key_12345'
        }
    }

@pytest.fixture(scope="session")
def test_data():
    """測試數據配置"""
    with open('test_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@pytest.fixture(autouse=True)
def test_logging(request):
    """測試日誌記錄"""
    test_name = request.node.name
    start_time = datetime.now()
    
    print(f"\n開始執行測試: {test_name}")
    
    def finalizer():
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"測試完成: {test_name}, 耗時: {duration:.2f}秒")
    
    request.addfinalizer(finalizer)
```

#### 測試案例實現

每個測試案例都實現為獨立的 Python 函數，使用 pytest 的裝飾器進行標記和參數化。測試函數包含請求構造、API 調用、響應驗證等步驟。

```python
# test_api_execute.py - 測試執行 API 測試案例
import pytest
import requests
import json
from jsonschema import validate

class TestExecuteAPI:
    """測試執行 API 測試類"""
    
    def test_requirement_analysis_execution(self, api_client, test_data):
        """需求分析測試執行"""
        # 構造請求數據
        request_data = {
            "test_type": "requirement_analysis",
            "test_parameters": {
                "requirement_text": "用戶需要登錄功能",
                "analysis_depth": "standard"
            },
            "execution_options": {
                "timeout": 300,
                "priority": "medium"
            }
        }
        
        # 發送 API 請求
        response = requests.post(
            f"{api_client['base_url']}/api/test/execute",
            headers=api_client['headers'],
            json=request_data,
            timeout=api_client['timeout']
        )
        
        # 驗證響應狀態碼
        assert response.status_code == 200, f"期望狀態碼 200，實際 {response.status_code}"
        
        # 驗證響應格式
        response_data = response.json()
        expected_schema = {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "task_id": {"type": "string"},
                "status": {"type": "string", "enum": ["running", "queued"]},
                "estimated_completion": {"type": "string"}
            },
            "required": ["success", "task_id", "status"]
        }
        
        validate(instance=response_data, schema=expected_schema)
        
        # 驗證業務邏輯
        assert response_data['success'] is True
        assert len(response_data['task_id']) > 0
        assert response_data['status'] in ['running', 'queued']
        
        # 保存任務 ID 用於後續測試
        return response_data['task_id']
    
    @pytest.mark.parametrize("test_type,expected_status", [
        ("requirement_analysis", 200),
        ("functional_test", 200),
        ("integration_test", 200),
        ("performance_test", 200)
    ])
    def test_different_test_types(self, api_client, test_type, expected_status):
        """不同測試類型的執行測試"""
        request_data = {
            "test_type": test_type,
            "test_parameters": {
                "requirement_text": f"測試 {test_type} 功能"
            }
        }
        
        response = requests.post(
            f"{api_client['base_url']}/api/test/execute",
            headers=api_client['headers'],
            json=request_data,
            timeout=api_client['timeout']
        )
        
        assert response.status_code == expected_status
        
        if expected_status == 200:
            response_data = response.json()
            assert response_data['success'] is True
            assert 'task_id' in response_data
```

#### 負向測試案例實現

負向測試案例專門驗證錯誤處理邏輯，確保 API 在異常情況下能夠返回適當的錯誤信息。

```python
class TestExecuteAPINegative:
    """測試執行 API 負向測試類"""
    
    def test_missing_required_parameter(self, api_client):
        """缺少必需參數測試"""
        request_data = {
            "test_parameters": {
                "requirement_text": "測試需求"
            }
            # 故意省略 test_type 參數
        }
        
        response = requests.post(
            f"{api_client['base_url']}/api/test/execute",
            headers=api_client['headers'],
            json=request_data,
            timeout=api_client['timeout']
        )
        
        assert response.status_code == 400
        response_data = response.json()
        assert response_data['success'] is False
        assert 'error_code' in response_data
        assert response_data['error_code'] == 'MISSING_REQUIRED_PARAMETER'
    
    def test_invalid_api_key(self, api_client):
        """無效 API Key 測試"""
        invalid_headers = api_client['headers'].copy()
        invalid_headers['X-API-Key'] = 'invalid_key'
        
        request_data = {
            "test_type": "requirement_analysis",
            "test_parameters": {
                "requirement_text": "測試需求"
            }
        }
        
        response = requests.post(
            f"{api_client['base_url']}/api/test/execute",
            headers=invalid_headers,
            json=request_data,
            timeout=api_client['timeout']
        )
        
        assert response.status_code == 401
        response_data = response.json()
        assert response_data['success'] is False
        assert response_data['error_code'] == 'INVALID_API_KEY'
    
    @pytest.mark.parametrize("invalid_input", [
        "",  # 空字符串
        "A" * 10001,  # 超長字符串
        "<script>alert('xss')</script>",  # XSS 攻擊
        "'; DROP TABLE users; --"  # SQL 注入
    ])
    def test_invalid_requirement_text(self, api_client, invalid_input):
        """無效需求文本測試"""
        request_data = {
            "test_type": "requirement_analysis",
            "test_parameters": {
                "requirement_text": invalid_input
            }
        }
        
        response = requests.post(
            f"{api_client['base_url']}/api/test/execute",
            headers=api_client['headers'],
            json=request_data,
            timeout=api_client['timeout']
        )
        
        assert response.status_code == 400
        response_data = response.json()
        assert response_data['success'] is False
        assert 'error_code' in response_data
```

### 手動測試執行

雖然自動化測試是主要的執行方式，但某些場景仍需要手動測試來補充。手動測試主要用於探索性測試、用戶體驗驗證、複雜場景調試等。

#### 手動測試工具

手動測試推薦使用 Postman 或 curl 命令行工具。Postman 提供了友好的圖形界面，便於測試案例的組織和執行。curl 命令行工具適合快速驗證和腳本化執行。

Postman 集合配置示例：

```json
{
  "info": {
    "name": "test_flow_mcp API Tests",
    "description": "PowerAutomation test_flow_mcp API 手動測試集合"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8080"
    },
    {
      "key": "api_key",
      "value": "test_api_key_12345"
    }
  ],
  "item": [
    {
      "name": "Execute Test",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          },
          {
            "key": "X-API-Key",
            "value": "{{api_key}}"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"test_type\": \"requirement_analysis\",\n  \"test_parameters\": {\n    \"requirement_text\": \"用戶登錄功能需求\"\n  }\n}"
        },
        "url": {
          "raw": "{{base_url}}/api/test/execute",
          "host": ["{{base_url}}"],
          "path": ["api", "test", "execute"]
        }
      },
      "response": []
    }
  ]
}
```

#### curl 命令示例

curl 命令適合快速驗證和自動化腳本集成：

```bash
#!/bin/bash
# test_flow_api_manual_test.sh

BASE_URL="http://localhost:8080"
API_KEY="test_api_key_12345"

echo "=== test_flow_mcp API 手動測試 ==="

# 測試 1: 執行需求分析測試
echo "測試 1: 執行需求分析測試"
TASK_ID=$(curl -s -X POST \
  "${BASE_URL}/api/test/execute" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "test_type": "requirement_analysis",
    "test_parameters": {
      "requirement_text": "用戶需要能夠重置密碼的功能"
    }
  }' | jq -r '.task_id')

echo "任務 ID: $TASK_ID"

# 測試 2: 查詢測試狀態
echo "測試 2: 查詢測試狀態"
sleep 2
curl -s -X GET \
  "${BASE_URL}/api/test/status/${TASK_ID}" \
  -H "X-API-Key: ${API_KEY}" | jq '.'

# 測試 3: 系統健康檢查
echo "測試 3: 系統健康檢查"
curl -s -X GET \
  "${BASE_URL}/api/system/health" \
  -H "X-API-Key: ${API_KEY}" | jq '.'

# 測試 4: 錯誤處理測試
echo "測試 4: 錯誤處理測試 - 無效 API Key"
curl -s -X POST \
  "${BASE_URL}/api/test/execute" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: invalid_key" \
  -d '{
    "test_type": "requirement_analysis",
    "test_parameters": {
      "requirement_text": "測試需求"
    }
  }' | jq '.'

echo "=== 手動測試完成 ==="
```

### 測試數據管理

測試數據的有效管理對於測試執行的成功至關重要。測試數據包括輸入數據、預期輸出、測試配置等多個方面。

#### 測試數據組織結構

測試數據按照功能模組和測試類型進行組織，形成層次化的目錄結構：

```
test_data/
├── execute_api/
│   ├── positive_cases.json
│   ├── negative_cases.json
│   └── boundary_cases.json
├── status_api/
│   ├── valid_task_ids.json
│   └── invalid_task_ids.json
├── results_api/
│   └── completed_tasks.json
└── common/
    ├── api_keys.json
    └── system_config.json
```

每個 JSON 文件包含相應類型的測試數據：

```json
{
  "positive_cases": [
    {
      "case_id": "PC_001",
      "name": "標準需求分析",
      "input": {
        "test_type": "requirement_analysis",
        "test_parameters": {
          "requirement_text": "用戶希望能夠快速搜索商品",
          "analysis_depth": "standard"
        }
      },
      "expected": {
        "status_code": 200,
        "success": true,
        "has_task_id": true
      }
    },
    {
      "case_id": "PC_002",
      "name": "詳細需求分析",
      "input": {
        "test_type": "requirement_analysis",
        "test_parameters": {
          "requirement_text": "實現用戶個人資料管理功能，包括頭像上傳、信息修改、隱私設置",
          "analysis_depth": "detailed",
          "include_security_check": true
        }
      },
      "expected": {
        "status_code": 200,
        "success": true,
        "has_task_id": true
      }
    }
  ]
}
```

#### 動態測試數據生成

對於某些測試場景，需要動態生成測試數據以避免數據污染和提高測試的獨立性。

```python
import uuid
import random
from datetime import datetime, timedelta

class TestDataGenerator:
    """測試數據生成器"""
    
    @staticmethod
    def generate_requirement_text(complexity="medium"):
        """生成需求文本"""
        templates = {
            "simple": [
                "用戶需要{feature}功能",
                "系統應該支援{feature}",
                "實現{feature}模組"
            ],
            "medium": [
                "用戶希望能夠{action}，並且{constraint}",
                "系統需要提供{feature}功能，支援{scenario}場景",
                "實現{feature}，包括{details}"
            ],
            "complex": [
                "用戶在{context}情況下需要{feature}功能，要求{performance}，同時考慮{security}",
                "系統應該提供{feature}，支援{scenario1}和{scenario2}，並且{constraint}"
            ]
        }
        
        placeholders = {
            "feature": ["登錄", "搜索", "支付", "評論", "分享"],
            "action": ["快速找到商品", "管理個人信息", "查看訂單歷史"],
            "constraint": ["響應時間小於2秒", "支援移動端", "確保數據安全"],
            "scenario": ["多用戶併發", "離線使用", "跨平台同步"],
            "details": ["密碼重置", "郵箱驗證", "第三方登錄"],
            "context": ["高併發", "弱網路", "移動端"],
            "performance": ["高可用性", "快速響應", "低延遲"],
            "security": ["數據加密", "權限控制", "審計日誌"],
            "scenario1": ["Web端訪問", "移動端使用"],
            "scenario2": ["API調用", "批量處理"]
        }
        
        template = random.choice(templates[complexity])
        
        # 替換佔位符
        for key, values in placeholders.items():
            if f"{{{key}}}" in template:
                template = template.replace(f"{{{key}}}", random.choice(values))
        
        return template
    
    @staticmethod
    def generate_task_id():
        """生成任務 ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = str(uuid.uuid4())[:8]
        return f"task_{timestamp}_{random_suffix}"
    
    @staticmethod
    def generate_api_key(role="test"):
        """生成 API Key"""
        random_part = str(uuid.uuid4()).replace('-', '')[:32]
        return f"{role}_{random_part}"
```

### 並行測試執行

為了提高測試效率，支援並行執行多個測試案例。但並行執行需要考慮測試之間的相互影響和資源競爭。

#### pytest 並行配置

使用 pytest-xdist 插件實現並行測試執行：

```bash
# 安裝並行測試插件
pip install pytest-xdist

# 並行執行測試
pytest -n 4 tests/  # 使用 4 個進程並行執行
pytest -n auto tests/  # 自動檢測 CPU 核心數
```

並行測試配置文件：

```ini
# pytest.ini
[tool:pytest]
addopts = -v --tb=short --strict-markers
markers =
    smoke: 冒煙測試
    regression: 回歸測試
    performance: 性能測試
    security: 安全測試
    slow: 慢速測試
    parallel: 可並行執行的測試
    sequential: 需要順序執行的測試

# 並行執行配置
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

#### 測試隔離策略

並行測試需要確保測試之間的隔離，避免相互影響：

```python
import threading
from contextlib import contextmanager

class TestIsolation:
    """測試隔離管理"""
    
    _locks = {}
    _lock = threading.Lock()
    
    @classmethod
    @contextmanager
    def resource_lock(cls, resource_name):
        """資源鎖定上下文管理器"""
        with cls._lock:
            if resource_name not in cls._locks:
                cls._locks[resource_name] = threading.Lock()
            resource_lock = cls._locks[resource_name]
        
        with resource_lock:
            yield
    
    @staticmethod
    def generate_unique_test_data():
        """生成唯一的測試數據"""
        thread_id = threading.current_thread().ident
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"test_data_{thread_id}_{timestamp}"

# 使用示例
def test_concurrent_execution(api_client):
    """併發執行測試"""
    with TestIsolation.resource_lock("api_execution"):
        unique_data = TestIsolation.generate_unique_test_data()
        
        request_data = {
            "test_type": "requirement_analysis",
            "test_parameters": {
                "requirement_text": f"測試需求 {unique_data}"
            }
        }
        
        response = requests.post(
            f"{api_client['base_url']}/api/test/execute",
            headers=api_client['headers'],
            json=request_data
        )
        
        assert response.status_code == 200
```

---


## 📊 結果分析與報告

### 測試結果收集

測試結果的系統化收集是後續分析和報告的基礎。test_flow_mcp API 測試結果包括執行狀態、響應數據、性能指標、錯誤信息等多個維度的數據。

#### 結果數據結構

測試結果採用標準化的數據結構進行存儲，便於後續的分析和處理。每個測試案例的執行結果都包含完整的上下文信息。

```json
{
  "test_execution_id": "exec_20250625_120000_001",
  "execution_timestamp": "2025-06-25T12:00:00Z",
  "test_suite": "test_flow_mcp_api",
  "environment": "staging",
  "test_results": [
    {
      "test_case_id": "TC_EXEC_001",
      "test_name": "需求分析測試執行",
      "test_category": "functional",
      "execution_status": "passed",
      "start_time": "2025-06-25T12:00:01Z",
      "end_time": "2025-06-25T12:00:03Z",
      "duration": 2.15,
      "request_data": {
        "test_type": "requirement_analysis",
        "test_parameters": {
          "requirement_text": "用戶登錄功能需求"
        }
      },
      "response_data": {
        "status_code": 200,
        "response_body": {
          "success": true,
          "task_id": "task_20250625_120001_abc123",
          "status": "running"
        },
        "response_headers": {
          "Content-Type": "application/json",
          "X-Response-Time": "1.85s"
        }
      },
      "assertions": [
        {
          "assertion": "status_code == 200",
          "result": "passed"
        },
        {
          "assertion": "response_body.success == true",
          "result": "passed"
        },
        {
          "assertion": "response_body.task_id is not empty",
          "result": "passed"
        }
      ],
      "performance_metrics": {
        "response_time": 1.85,
        "request_size": 156,
        "response_size": 234
      }
    }
  ],
  "summary": {
    "total_tests": 45,
    "passed": 42,
    "failed": 2,
    "skipped": 1,
    "pass_rate": 93.33,
    "total_duration": 125.67,
    "average_response_time": 2.79
  }
}
```

#### 實時結果收集

測試執行過程中需要實時收集結果數據，支援測試進度監控和即時問題發現。

```python
import json
import time
from datetime import datetime
from pathlib import Path

class TestResultCollector:
    """測試結果收集器"""
    
    def __init__(self, output_dir="test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.current_execution = None
        self.results = []
    
    def start_execution(self, test_suite_name, environment="test"):
        """開始測試執行"""
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(self) % 1000:03d}"
        
        self.current_execution = {
            "test_execution_id": execution_id,
            "execution_timestamp": datetime.now().isoformat(),
            "test_suite": test_suite_name,
            "environment": environment,
            "test_results": [],
            "start_time": time.time()
        }
        
        return execution_id
    
    def record_test_result(self, test_case_id, test_name, category, 
                          status, duration, request_data, response_data, 
                          assertions=None, performance_metrics=None):
        """記錄測試結果"""
        if not self.current_execution:
            raise ValueError("必須先調用 start_execution()")
        
        result = {
            "test_case_id": test_case_id,
            "test_name": test_name,
            "test_category": category,
            "execution_status": status,
            "start_time": datetime.now().isoformat(),
            "duration": duration,
            "request_data": request_data,
            "response_data": response_data,
            "assertions": assertions or [],
            "performance_metrics": performance_metrics or {}
        }
        
        self.current_execution["test_results"].append(result)
        
        # 實時保存結果
        self._save_intermediate_results()
    
    def finish_execution(self):
        """完成測試執行"""
        if not self.current_execution:
            return None
        
        # 計算摘要統計
        results = self.current_execution["test_results"]
        total_tests = len(results)
        passed = sum(1 for r in results if r["execution_status"] == "passed")
        failed = sum(1 for r in results if r["execution_status"] == "failed")
        skipped = sum(1 for r in results if r["execution_status"] == "skipped")
        
        total_duration = sum(r["duration"] for r in results)
        avg_response_time = sum(
            r["performance_metrics"].get("response_time", 0) 
            for r in results if r["performance_metrics"]
        ) / max(total_tests, 1)
        
        self.current_execution["summary"] = {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": (passed / max(total_tests, 1)) * 100,
            "total_duration": total_duration,
            "average_response_time": avg_response_time
        }
        
        # 保存最終結果
        output_file = self.output_dir / f"{self.current_execution['test_execution_id']}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_execution, f, indent=2, ensure_ascii=False)
        
        execution_result = self.current_execution
        self.current_execution = None
        
        return execution_result
    
    def _save_intermediate_results(self):
        """保存中間結果"""
        if self.current_execution:
            temp_file = self.output_dir / f"{self.current_execution['test_execution_id']}_temp.json"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_execution, f, indent=2, ensure_ascii=False)
```

### 性能分析

API 性能分析是測試結果分析的重要組成部分，幫助識別性能瓶頸和優化機會。

#### 響應時間分析

響應時間是 API 性能的核心指標，需要從多個維度進行分析。

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self, test_results):
        self.test_results = test_results
        self.response_times = self._extract_response_times()
    
    def _extract_response_times(self):
        """提取響應時間數據"""
        times = []
        for result in self.test_results:
            if result.get("performance_metrics", {}).get("response_time"):
                times.append(result["performance_metrics"]["response_time"])
        return times
    
    def calculate_statistics(self):
        """計算統計指標"""
        if not self.response_times:
            return {}
        
        times = np.array(self.response_times)
        
        return {
            "count": len(times),
            "mean": np.mean(times),
            "median": np.median(times),
            "std": np.std(times),
            "min": np.min(times),
            "max": np.max(times),
            "p95": np.percentile(times, 95),
            "p99": np.percentile(times, 99),
            "coefficient_of_variation": np.std(times) / np.mean(times) if np.mean(times) > 0 else 0
        }
    
    def analyze_trends(self):
        """分析性能趨勢"""
        if len(self.response_times) < 10:
            return {"trend": "insufficient_data"}
        
        # 線性回歸分析趨勢
        x = np.arange(len(self.response_times))
        y = np.array(self.response_times)
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        trend_analysis = {
            "slope": slope,
            "r_squared": r_value ** 2,
            "p_value": p_value,
            "trend_direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
            "trend_significance": "significant" if p_value < 0.05 else "not_significant"
        }
        
        return trend_analysis
    
    def identify_outliers(self, method="iqr"):
        """識別異常值"""
        if not self.response_times:
            return []
        
        times = np.array(self.response_times)
        
        if method == "iqr":
            q1 = np.percentile(times, 25)
            q3 = np.percentile(times, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = []
            for i, time in enumerate(times):
                if time < lower_bound or time > upper_bound:
                    outliers.append({
                        "index": i,
                        "value": time,
                        "type": "low" if time < lower_bound else "high"
                    })
            
            return outliers
        
        elif method == "zscore":
            z_scores = np.abs(stats.zscore(times))
            outliers = []
            for i, (time, z_score) in enumerate(zip(times, z_scores)):
                if z_score > 3:  # 3-sigma rule
                    outliers.append({
                        "index": i,
                        "value": time,
                        "z_score": z_score
                    })
            
            return outliers
    
    def generate_performance_report(self):
        """生成性能報告"""
        stats = self.calculate_statistics()
        trends = self.analyze_trends()
        outliers = self.identify_outliers()
        
        report = {
            "summary": {
                "total_requests": stats.get("count", 0),
                "average_response_time": stats.get("mean", 0),
                "median_response_time": stats.get("median", 0),
                "p95_response_time": stats.get("p95", 0),
                "p99_response_time": stats.get("p99", 0)
            },
            "performance_grade": self._calculate_performance_grade(stats),
            "trend_analysis": trends,
            "outliers": {
                "count": len(outliers),
                "details": outliers[:10]  # 只顯示前10個異常值
            },
            "recommendations": self._generate_recommendations(stats, trends, outliers)
        }
        
        return report
    
    def _calculate_performance_grade(self, stats):
        """計算性能等級"""
        if not stats or stats.get("mean", 0) == 0:
            return "N/A"
        
        mean_time = stats["mean"]
        p95_time = stats.get("p95", mean_time)
        
        if mean_time <= 1.0 and p95_time <= 2.0:
            return "A"  # 優秀
        elif mean_time <= 2.0 and p95_time <= 5.0:
            return "B"  # 良好
        elif mean_time <= 5.0 and p95_time <= 10.0:
            return "C"  # 一般
        else:
            return "D"  # 需要改進
    
    def _generate_recommendations(self, stats, trends, outliers):
        """生成優化建議"""
        recommendations = []
        
        if stats.get("mean", 0) > 5.0:
            recommendations.append("平均響應時間較高，建議檢查系統性能瓶頸")
        
        if stats.get("coefficient_of_variation", 0) > 0.5:
            recommendations.append("響應時間變異性較大，建議檢查系統穩定性")
        
        if trends.get("trend_direction") == "increasing" and trends.get("trend_significance") == "significant":
            recommendations.append("響應時間呈上升趨勢，建議監控系統資源使用情況")
        
        if len(outliers) > len(self.response_times) * 0.05:  # 超過5%的異常值
            recommendations.append("存在較多異常響應時間，建議檢查特定請求的處理邏輯")
        
        return recommendations
```

#### 吞吐量分析

吞吐量分析評估 API 在不同負載條件下的處理能力。

```python
class ThroughputAnalyzer:
    """吞吐量分析器"""
    
    def __init__(self, test_results, time_window=60):
        self.test_results = test_results
        self.time_window = time_window  # 時間窗口（秒）
    
    def calculate_throughput_over_time(self):
        """計算時間序列吞吐量"""
        # 按時間排序測試結果
        sorted_results = sorted(
            self.test_results,
            key=lambda x: x.get("start_time", "")
        )
        
        if not sorted_results:
            return []
        
        # 計算每個時間窗口的吞吐量
        throughput_data = []
        window_start = sorted_results[0]["start_time"]
        window_requests = 0
        
        for result in sorted_results:
            result_time = result["start_time"]
            
            # 檢查是否需要開始新的時間窗口
            if self._time_diff(window_start, result_time) >= self.time_window:
                throughput_data.append({
                    "window_start": window_start,
                    "requests_per_second": window_requests / self.time_window,
                    "total_requests": window_requests
                })
                
                window_start = result_time
                window_requests = 1
            else:
                window_requests += 1
        
        # 處理最後一個窗口
        if window_requests > 0:
            window_duration = min(self.time_window, 
                                self._time_diff(window_start, sorted_results[-1]["start_time"]))
            throughput_data.append({
                "window_start": window_start,
                "requests_per_second": window_requests / max(window_duration, 1),
                "total_requests": window_requests
            })
        
        return throughput_data
    
    def _time_diff(self, start_time, end_time):
        """計算時間差（秒）"""
        # 簡化實現，實際應該解析 ISO 時間格式
        return 60  # 假設值
```

### 錯誤分析

錯誤分析幫助識別 API 的穩定性問題和改進機會。

#### 錯誤分類統計

```python
class ErrorAnalyzer:
    """錯誤分析器"""
    
    def __init__(self, test_results):
        self.test_results = test_results
        self.failed_tests = [r for r in test_results if r.get("execution_status") == "failed"]
    
    def categorize_errors(self):
        """錯誤分類統計"""
        error_categories = {
            "http_errors": {},
            "timeout_errors": 0,
            "connection_errors": 0,
            "validation_errors": 0,
            "business_logic_errors": 0,
            "unknown_errors": 0
        }
        
        for test in self.failed_tests:
            response_data = test.get("response_data", {})
            status_code = response_data.get("status_code")
            
            if status_code:
                if status_code >= 500:
                    error_type = "server_errors"
                elif status_code >= 400:
                    error_type = "client_errors"
                else:
                    error_type = "other_http_errors"
                
                if error_type not in error_categories["http_errors"]:
                    error_categories["http_errors"][error_type] = {}
                
                if status_code not in error_categories["http_errors"][error_type]:
                    error_categories["http_errors"][error_type][status_code] = 0
                
                error_categories["http_errors"][error_type][status_code] += 1
            
            # 分析錯誤原因
            error_message = response_data.get("response_body", {}).get("message", "")
            if "timeout" in error_message.lower():
                error_categories["timeout_errors"] += 1
            elif "connection" in error_message.lower():
                error_categories["connection_errors"] += 1
            elif "validation" in error_message.lower():
                error_categories["validation_errors"] += 1
            elif response_data.get("response_body", {}).get("error_code"):
                error_categories["business_logic_errors"] += 1
            else:
                error_categories["unknown_errors"] += 1
        
        return error_categories
    
    def identify_error_patterns(self):
        """識別錯誤模式"""
        patterns = []
        
        # 分析錯誤的時間分佈
        error_times = [test.get("start_time") for test in self.failed_tests]
        if len(error_times) > 1:
            # 檢查是否有錯誤集中的時間段
            patterns.append({
                "type": "temporal_clustering",
                "description": "錯誤在特定時間段集中出現",
                "details": self._analyze_temporal_clustering(error_times)
            })
        
        # 分析錯誤的 API 端點分佈
        endpoint_errors = {}
        for test in self.failed_tests:
            endpoint = test.get("request_data", {}).get("endpoint", "unknown")
            endpoint_errors[endpoint] = endpoint_errors.get(endpoint, 0) + 1
        
        if endpoint_errors:
            patterns.append({
                "type": "endpoint_distribution",
                "description": "錯誤在不同 API 端點的分佈",
                "details": endpoint_errors
            })
        
        return patterns
    
    def _analyze_temporal_clustering(self, error_times):
        """分析時間聚集性"""
        # 簡化實現
        return {
            "total_errors": len(error_times),
            "time_span": "分析時間跨度",
            "clustering_detected": len(error_times) > 5
        }
    
    def generate_error_report(self):
        """生成錯誤報告"""
        categories = self.categorize_errors()
        patterns = self.identify_error_patterns()
        
        total_tests = len(self.test_results)
        failed_tests = len(self.failed_tests)
        error_rate = (failed_tests / max(total_tests, 1)) * 100
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "failed_tests": failed_tests,
                "error_rate": error_rate,
                "error_grade": self._calculate_error_grade(error_rate)
            },
            "error_categories": categories,
            "error_patterns": patterns,
            "top_errors": self._get_top_errors(),
            "recommendations": self._generate_error_recommendations(categories, patterns)
        }
        
        return report
    
    def _calculate_error_grade(self, error_rate):
        """計算錯誤等級"""
        if error_rate == 0:
            return "A"
        elif error_rate <= 1:
            return "B"
        elif error_rate <= 5:
            return "C"
        else:
            return "D"
    
    def _get_top_errors(self, limit=5):
        """獲取最常見的錯誤"""
        error_counts = {}
        
        for test in self.failed_tests:
            error_code = test.get("response_data", {}).get("response_body", {}).get("error_code", "UNKNOWN")
            error_message = test.get("response_data", {}).get("response_body", {}).get("message", "")
            
            error_key = f"{error_code}: {error_message[:100]}"
            error_counts[error_key] = error_counts.get(error_key, 0) + 1
        
        # 按出現次數排序
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"error": error, "count": count}
            for error, count in sorted_errors[:limit]
        ]
    
    def _generate_error_recommendations(self, categories, patterns):
        """生成錯誤改進建議"""
        recommendations = []
        
        # 基於錯誤類別的建議
        http_errors = categories.get("http_errors", {})
        if "server_errors" in http_errors:
            recommendations.append("存在服務器錯誤，建議檢查後端服務穩定性")
        
        if "client_errors" in http_errors:
            recommendations.append("存在客戶端錯誤，建議檢查請求參數驗證邏輯")
        
        if categories.get("timeout_errors", 0) > 0:
            recommendations.append("存在超時錯誤，建議優化響應時間或調整超時設置")
        
        # 基於錯誤模式的建議
        for pattern in patterns:
            if pattern["type"] == "temporal_clustering":
                recommendations.append("錯誤在時間上聚集，建議檢查系統在特定時間段的負載情況")
        
        return recommendations
```

### 測試報告生成

測試報告是測試結果的最終呈現形式，需要清晰、準確、易於理解。

#### HTML 報告生成

```python
from jinja2 import Template
import base64
import io

class HTMLReportGenerator:
    """HTML 報告生成器"""
    
    def __init__(self):
        self.template = self._get_html_template()
    
    def generate_report(self, test_results, performance_analysis, error_analysis):
        """生成 HTML 報告"""
        
        # 準備報告數據
        report_data = {
            "execution_info": {
                "execution_id": test_results.get("test_execution_id", "N/A"),
                "timestamp": test_results.get("execution_timestamp", "N/A"),
                "environment": test_results.get("environment", "N/A"),
                "test_suite": test_results.get("test_suite", "N/A")
            },
            "summary": test_results.get("summary", {}),
            "performance": performance_analysis,
            "errors": error_analysis,
            "test_details": test_results.get("test_results", [])
        }
        
        # 生成圖表
        charts = self._generate_charts(report_data)
        report_data["charts"] = charts
        
        # 渲染 HTML
        html_content = self.template.render(**report_data)
        
        return html_content
    
    def _generate_charts(self, report_data):
        """生成圖表"""
        charts = {}
        
        # 測試結果分佈餅圖
        summary = report_data["summary"]
        if summary:
            charts["test_distribution"] = self._create_pie_chart(
                labels=["通過", "失敗", "跳過"],
                values=[summary.get("passed", 0), summary.get("failed", 0), summary.get("skipped", 0)],
                title="測試結果分佈"
            )
        
        # 響應時間分佈直方圖
        performance = report_data["performance"]
        if performance and "response_times" in performance:
            charts["response_time_distribution"] = self._create_histogram(
                data=performance["response_times"],
                title="響應時間分佈",
                xlabel="響應時間 (秒)",
                ylabel="頻次"
            )
        
        return charts
    
    def _create_pie_chart(self, labels, values, title):
        """創建餅圖"""
        # 使用 matplotlib 生成圖表並轉換為 base64
        plt.figure(figsize=(8, 6))
        plt.pie(values, labels=labels, autopct='%1.1f%%')
        plt.title(title)
        
        # 保存到內存
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        img_buffer.seek(0)
        
        # 轉換為 base64
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{img_base64}"
    
    def _create_histogram(self, data, title, xlabel, ylabel):
        """創建直方圖"""
        plt.figure(figsize=(10, 6))
        plt.hist(data, bins=20, alpha=0.7, edgecolor='black')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True, alpha=0.3)
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        img_buffer.seek(0)
        
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{img_base64}"
    
    def _get_html_template(self):
        """獲取 HTML 模板"""
        template_str = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>test_flow_mcp API 測試報告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .summary-card { background-color: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
        .summary-card h3 { margin: 0 0 10px 0; color: #333; }
        .summary-card .value { font-size: 2em; font-weight: bold; color: #007bff; }
        .chart-container { margin: 30px 0; text-align: center; }
        .chart-container img { max-width: 100%; height: auto; }
        .section { margin: 30px 0; }
        .section h2 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .test-details { overflow-x: auto; }
        .test-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .test-table th, .test-table td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        .test-table th { background-color: #f8f9fa; font-weight: bold; }
        .status-passed { color: #28a745; font-weight: bold; }
        .status-failed { color: #dc3545; font-weight: bold; }
        .status-skipped { color: #ffc107; font-weight: bold; }
        .recommendations { background-color: #e7f3ff; padding: 20px; border-radius: 8px; margin-top: 20px; }
        .recommendations ul { margin: 10px 0; padding-left: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>test_flow_mcp API 測試報告</h1>
            <p>執行時間: {{ execution_info.timestamp }}</p>
            <p>測試環境: {{ execution_info.environment }} | 測試套件: {{ execution_info.test_suite }}</p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <h3>總測試數</h3>
                <div class="value">{{ summary.total_tests }}</div>
            </div>
            <div class="summary-card">
                <h3>通過率</h3>
                <div class="value">{{ "%.1f"|format(summary.pass_rate) }}%</div>
            </div>
            <div class="summary-card">
                <h3>平均響應時間</h3>
                <div class="value">{{ "%.2f"|format(summary.average_response_time) }}s</div>
            </div>
            <div class="summary-card">
                <h3>總執行時間</h3>
                <div class="value">{{ "%.1f"|format(summary.total_duration) }}s</div>
            </div>
        </div>
        
        {% if charts.test_distribution %}
        <div class="chart-container">
            <h2>測試結果分佈</h2>
            <img src="{{ charts.test_distribution }}" alt="測試結果分佈圖">
        </div>
        {% endif %}
        
        <div class="section">
            <h2>性能分析</h2>
            <p><strong>性能等級:</strong> {{ performance.performance_grade }}</p>
            <p><strong>平均響應時間:</strong> {{ "%.3f"|format(performance.summary.average_response_time) }} 秒</p>
            <p><strong>95% 響應時間:</strong> {{ "%.3f"|format(performance.summary.p95_response_time) }} 秒</p>
            
            {% if performance.recommendations %}
            <div class="recommendations">
                <h3>性能優化建議</h3>
                <ul>
                {% for rec in performance.recommendations %}
                    <li>{{ rec }}</li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>錯誤分析</h2>
            <p><strong>錯誤率:</strong> {{ "%.2f"|format(errors.summary.error_rate) }}%</p>
            <p><strong>錯誤等級:</strong> {{ errors.summary.error_grade }}</p>
            
            {% if errors.top_errors %}
            <h3>主要錯誤</h3>
            <ul>
            {% for error in errors.top_errors %}
                <li>{{ error.error }} ({{ error.count }} 次)</li>
            {% endfor %}
            </ul>
            {% endif %}
            
            {% if errors.recommendations %}
            <div class="recommendations">
                <h3>錯誤改進建議</h3>
                <ul>
                {% for rec in errors.recommendations %}
                    <li>{{ rec }}</li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>測試詳情</h2>
            <div class="test-details">
                <table class="test-table">
                    <thead>
                        <tr>
                            <th>測試案例</th>
                            <th>狀態</th>
                            <th>響應時間</th>
                            <th>HTTP 狀態碼</th>
                            <th>執行時間</th>
                        </tr>
                    </thead>
                    <tbody>
                    {% for test in test_details %}
                        <tr>
                            <td>{{ test.test_name }}</td>
                            <td class="status-{{ test.execution_status }}">{{ test.execution_status.upper() }}</td>
                            <td>{{ "%.3f"|format(test.performance_metrics.response_time or 0) }}s</td>
                            <td>{{ test.response_data.status_code or 'N/A' }}</td>
                            <td>{{ "%.2f"|format(test.duration) }}s</td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        return Template(template_str)
```

#### JSON 報告生成

```python
class JSONReportGenerator:
    """JSON 報告生成器"""
    
    def generate_report(self, test_results, performance_analysis, error_analysis):
        """生成 JSON 格式報告"""
        
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_version": "1.0",
                "generator": "test_flow_mcp_api_tester"
            },
            "execution_info": test_results.get("execution_info", {}),
            "test_summary": test_results.get("summary", {}),
            "performance_analysis": performance_analysis,
            "error_analysis": error_analysis,
            "detailed_results": test_results.get("test_results", []),
            "recommendations": {
                "performance": performance_analysis.get("recommendations", []),
                "errors": error_analysis.get("recommendations", []),
                "overall": self._generate_overall_recommendations(
                    test_results.get("summary", {}),
                    performance_analysis,
                    error_analysis
                )
            }
        }
        
        return report
    
    def _generate_overall_recommendations(self, summary, performance, errors):
        """生成整體建議"""
        recommendations = []
        
        # 基於通過率的建議
        pass_rate = summary.get("pass_rate", 0)
        if pass_rate < 90:
            recommendations.append("測試通過率較低，建議優先修復失敗的測試案例")
        elif pass_rate < 95:
            recommendations.append("測試通過率良好，建議繼續改進剩餘問題")
        else:
            recommendations.append("測試通過率優秀，建議保持當前品質水準")
        
        # 基於性能等級的建議
        perf_grade = performance.get("performance_grade", "N/A")
        if perf_grade in ["C", "D"]:
            recommendations.append("API 性能需要改進，建議進行性能優化")
        elif perf_grade == "B":
            recommendations.append("API 性能良好，可考慮進一步優化")
        
        # 基於錯誤率的建議
        error_rate = errors.get("summary", {}).get("error_rate", 0)
        if error_rate > 5:
            recommendations.append("錯誤率較高，建議重點關注錯誤處理和系統穩定性")
        
        return recommendations
```

---

