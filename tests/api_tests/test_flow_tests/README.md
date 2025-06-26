# test_flow_mcp API 測試範例

這個目錄包含了 test_flow_mcp API 測試的完整範例實現，基於 [TEST_FLOW_API_TESTING_SOP.md](../TEST_FLOW_API_TESTING_SOP.md) 文檔中定義的標準操作程序。

## 📁 文件結構

```
test_flow_api_examples/
├── test_api_suite.py      # 主要測試套件
├── run_tests.py           # 測試執行腳本
├── test_config.json       # 測試配置文件
├── pytest.ini            # pytest 配置
├── requirements.txt       # Python 依賴包
├── README.md             # 本說明文件
└── test_results/         # 測試結果目錄（自動創建）
```

## 🚀 快速開始

### 1. 安裝依賴

```bash
# 創建虛擬環境（推薦）
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# 或
test_env\Scripts\activate     # Windows

# 安裝依賴包
pip install -r requirements.txt
```

### 2. 配置測試環境

編輯 `test_config.json` 文件，設置正確的 API 端點和認證信息：

```json
{
  "api_config": {
    "base_url": "http://127.0.0.1:8080",
    "api_key": "your_api_key_here",
    "timeout": 30
  }
}
```

### 3. 檢查環境

```bash
python run_tests.py --check-env
```

### 4. 執行測試

```bash
# 執行冒煙測試（快速驗證）
python run_tests.py --smoke

# 執行完整測試套件
python run_tests.py --full

# 執行所有測試類型
python run_tests.py --all
```

## 🧪 測試類型

### 冒煙測試 (Smoke Tests)
快速驗證核心功能是否正常工作：
```bash
python run_tests.py --smoke
```

### 回歸測試 (Regression Tests)
驗證修復後的功能是否正常：
```bash
python run_tests.py --regression
```

### 性能測試 (Performance Tests)
測試 API 的響應時間和併發處理能力：
```bash
python run_tests.py --performance
```

### 安全測試 (Security Tests)
驗證認證、授權和輸入驗證：
```bash
python run_tests.py --security
```

### 並行測試 (Parallel Tests)
使用多進程並行執行測試：
```bash
python run_tests.py --parallel 4
```

## 📊 測試報告

測試執行後會在 `test_results/` 目錄下生成多種格式的報告：

- `test_summary.json` - JSON 格式摘要
- `test_summary.md` - Markdown 格式摘要
- `*_test_results.xml` - JUnit XML 格式結果
- `*_execution.log` - 詳細執行日誌
- `full_test_report.html` - HTML 格式詳細報告

## 🔧 自定義測試

### 添加新的測試案例

在 `test_api_suite.py` 中添加新的測試方法：

```python
def test_custom_functionality(self, api_client):
    """自定義功能測試"""
    # 測試邏輯
    pass
```

### 修改測試配置

編輯 `test_config.json` 添加新的測試數據或配置：

```json
{
  "test_data": {
    "custom_scenarios": [
      "自定義測試場景1",
      "自定義測試場景2"
    ]
  }
}
```

### 使用 pytest 標記

為測試添加標記以便分類執行：

```python
@pytest.mark.smoke
def test_basic_functionality(self):
    pass

@pytest.mark.slow
def test_long_running_process(self):
    pass
```

然後使用標記執行特定測試：

```bash
pytest -m smoke  # 只執行冒煙測試
pytest -m "not slow"  # 排除慢速測試
```

## 🐛 故障排除

### 常見問題

1. **連接錯誤**
   - 檢查 `test_config.json` 中的 `base_url` 是否正確
   - 確認 test_flow_mcp 服務正在運行
   - 檢查網路連接和防火牆設置

2. **認證失敗**
   - 驗證 `api_key` 是否有效
   - 檢查 API Key 的權限設置
   - 確認認證頭格式正確

3. **測試超時**
   - 增加 `timeout` 配置值
   - 檢查系統負載和性能
   - 考慮使用並行測試減少總執行時間

4. **依賴包問題**
   - 更新 pip: `pip install --upgrade pip`
   - 重新安裝依賴: `pip install -r requirements.txt --force-reinstall`
   - 檢查 Python 版本兼容性

### 調試模式

啟用詳細日誌輸出：

```bash
pytest -v -s --tb=long test_api_suite.py
```

查看特定測試的詳細信息：

```bash
pytest -v -s test_api_suite.py::TestExecuteAPI::test_requirement_analysis_basic
```

## 📈 性能基準

### 響應時間基準
- 優秀: < 1.0 秒
- 良好: < 2.0 秒
- 可接受: < 5.0 秒
- 需改進: > 5.0 秒

### 成功率基準
- 優秀: > 99%
- 良好: > 95%
- 可接受: > 90%
- 需改進: < 90%

### 併發處理基準
- 輕負載: 5 併發用戶
- 中負載: 10 併發用戶
- 重負載: 20 併發用戶
- 壓力測試: 50+ 併發用戶

## 🔄 持續集成

### GitHub Actions 範例

```yaml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python run_tests.py --regression
```

### Jenkins Pipeline 範例

```groovy
pipeline {
    agent any
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh 'python run_tests.py --full'
            }
        }
        stage('Report') {
            steps {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'test_results',
                    reportFiles: 'full_test_report.html',
                    reportName: 'API Test Report'
                ])
            }
        }
    }
}
```

## 📚 相關文檔

- [TEST_FLOW_API_TESTING_SOP.md](../TEST_FLOW_API_TESTING_SOP.md) - 完整的 API 測試標準操作程序
- [pytest 官方文檔](https://docs.pytest.org/)
- [requests 庫文檔](https://requests.readthedocs.io/)
- [JSON Schema 驗證](https://python-jsonschema.readthedocs.io/)

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request 來改進這個測試框架。請確保：

1. 新增的測試案例有清晰的文檔說明
2. 遵循現有的代碼風格和命名規範
3. 更新相關的配置文件和文檔
4. 所有測試都能通過執行

## 📄 許可證

本項目遵循 MIT 許可證。詳見 LICENSE 文件。

