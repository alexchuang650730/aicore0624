# SmartInvention API 測試範例

這個目錄包含了 SmartInvention 對話歷史 API 和對比引擎的完整測試範例，仿照 `test_flow_api_examples` 的結構設計。

## 📋 目錄結構

```
smartinvention_api_examples/
├── test_api_suite.py          # 完整的測試套件
├── run_tests.py               # 測試執行腳本
├── test_config.json           # 測試配置文件
├── pytest.ini                 # pytest 配置
├── requirements.txt           # Python 依賴
├── README.md                  # 本文件
└── test_results/              # 測試結果目錄
    ├── *.json                 # JSON 格式報告
    ├── *.html                 # HTML 格式報告
    └── *.md                   # Markdown 格式報告
```

## 🚀 快速開始

### 0. API 配置

測試配置已設定為連接到我們的 EC2 實例：
- **API 基礎 URL**: `http://18.212.97.173:8000`
- **配置文件**: `test_config.json`

如果需要修改 API 地址，請編輯 `test_config.json` 中的 `base_url` 設定。

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 檢查環境

```bash
python run_tests.py --check-env
```

### 3. 運行測試

```bash
# 冒煙測試（快速驗證）
python run_tests.py --smoke

# 回歸測試（核心功能）
python run_tests.py --regression

# 性能測試
python run_tests.py --performance

# 集成測試
python run_tests.py --integration

# 完整測試套件
python run_tests.py --full
```

## 🧪 測試類型

### 基礎功能測試
- **健康檢查**: 驗證 API 服務可用性
- **獲取最新對話**: 測試對話歷史獲取功能
- **搜索對話**: 測試對話搜索和檢索
- **干預需求**: 測試需要人工干預的對話識別

### 核心功能測試
- **SmartInvention 處理**: 測試完整的處理流程
- **對話分析**: 測試對話內容分析功能
- **增量比對**: 測試與 Manus 的比對分析

### 集成測試
- **Manus 比對工作流程**: 測試與 Manus 的完整集成
- **HITL 中間件**: 測試 Human-in-the-Loop 審核功能

### 性能測試
- **併發請求**: 測試系統併發處理能力
- **大量數據處理**: 測試大量對話數據的處理性能

## 📊 API 端點

### 對話歷史相關
- `GET /api/conversations/latest` - 獲取最新對話
- `POST /api/sync/conversations` - 同步和搜索對話
- `GET /api/interventions/needed` - 獲取需要干預的對話

### SmartInvention 處理
- `POST /api/smartinvention/process` - 完整處理流程
- `GET /api/smartinvention/status` - 獲取處理狀態
- `POST /api/smartinvention/analyze` - 對話分析
- `POST /api/smartinvention/compare` - 增量比對

### 系統管理
- `GET /api/health` - 健康檢查

## 🔧 配置說明

### test_config.json 主要配置項

```json
{
  "api_config": {
    "base_url": "http://localhost:8000",
    "timeout": 30,
    "retry_attempts": 3
  },
  "test_data": {
    "sample_requests": [...],
    "search_keywords": [...],
    "contexts": [...]
  },
  "performance_benchmarks": {
    "response_time": {...},
    "throughput": {...}
  }
}
```

## 📈 測試報告

測試完成後會生成多種格式的報告：

### JSON 報告
- 完整的測試結果數據
- 適合程序化處理和 CI/CD 集成

### HTML 報告
- 可視化的測試結果展示
- 包含圖表和詳細信息
- 適合人工查看和分享

### Markdown 報告
- 文檔友好的格式
- 適合集成到項目文檔中

## 🎯 使用場景

### 開發階段
```bash
# 快速驗證功能
python run_tests.py --smoke

# 開發完成後的回歸測試
python run_tests.py --regression
```

### CI/CD 集成
```bash
# 在 CI 管道中運行
python run_tests.py --full --config ci_config.json
```

### 性能監控
```bash
# 定期性能測試
python run_tests.py --performance
```

### 發布前驗證
```bash
# 完整測試套件
python run_tests.py --full
```

## 🔍 故障排除

### 常見問題

**1. API 服務不可用**
```bash
# 檢查服務狀態
python run_tests.py --check-env

# 確認 PowerAutomation 系統運行
# 檢查端口 8000 是否開放
```

**2. 測試超時**
```bash
# 調整配置文件中的超時設置
# 檢查網絡連接
# 確認系統資源充足
```

**3. 依賴問題**
```bash
# 重新安裝依賴
pip install -r requirements.txt --upgrade

# 檢查 Python 版本（需要 3.8+）
python --version
```

### 調試模式

```bash
# 啟用詳細日誌
export LOG_LEVEL=DEBUG
python run_tests.py --full

# 使用 pytest 直接運行
pytest test_api_suite.py -v -s
```

## 📚 擴展測試

### 添加新測試

1. 在 `test_api_suite.py` 中添加新的測試方法
2. 更新 `test_config.json` 中的配置
3. 在 `run_tests.py` 中添加新的測試類型

### 自定義配置

```bash
# 使用自定義配置文件
python run_tests.py --full --config my_config.json
```

### 集成到現有測試框架

```python
from test_api_suite import SmartInventionAPITestSuite

# 在您的測試中使用
test_suite = SmartInventionAPITestSuite(custom_config)
results = await test_suite.run_all_tests()
```

## 🤝 與 test_flow_api_examples 的對比

| 特性 | test_flow_mcp | smartinvention_api |
|------|---------------|-------------------|
| 測試範圍 | 測試流程執行 | 對話歷史和比對引擎 |
| 主要功能 | 測試案例生成和執行 | 對話分析和增量比對 |
| 集成對象 | 測試框架 | Manus 和 HITL 系統 |
| 性能重點 | 測試執行效率 | 對話處理和比對速度 |

## 📞 支持

如果遇到問題或需要幫助：

1. 檢查本 README 的故障排除部分
2. 查看測試報告中的錯誤信息
3. 確認 PowerAutomation 系統正常運行
4. 聯繫開發團隊獲取支持

---

**注意**: 這個測試套件需要 PowerAutomation 系統運行並且 SmartInvention 組件正常工作。請確保在運行測試前系統已正確配置和啟動。

