# PowerAutomation Tests

這個目錄包含 PowerAutomation 項目的所有測試文件。

## 目錄結構

- `testcases/` - 測試案例目錄
  - `requirement_analysis/` - 需求分析相關測試
    - `test_requirement_analysis_integration.py` - 主要集成測試腳本
    - `requirement_analysis_test_results_*.json` - 測試結果文件

## 主要測試

### 需求分析集成測試
- **文件**: `testcases/requirement_analysis/test_requirement_analysis_integration.py`
- **功能**: 測試 test_flow_mcp 的需求分析工作流
- **包含**: API Key 驗證、服務器連接、四階段處理流程測試

## 運行測試

```bash
cd PowerAutomation/tests/testcases/requirement_analysis/
python test_requirement_analysis_integration.py
```

測試結果會自動保存到同目錄下的 JSON 文件中。
