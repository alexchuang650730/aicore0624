# Tests

這個目錄包含所有 PowerAutomation 相關項目的測試文件，服務於：

- **powerautomation** - 核心 PowerAutomation 系統
- **powerautomation_web** - Web 版本
- **powerautomation_local** - 本地版本

## 目錄結構

```
tests/
├── testcases/           # 測試案例目錄
│   └── requirement_analysis/  # 需求分析相關測試
├── integration/         # 集成測試 (待添加)
├── unit/               # 單元測試 (待添加)
└── e2e/                # 端到端測試 (待添加)
```

## 主要測試案例

### 需求分析集成測試
- **路徑**: `testcases/requirement_analysis/`
- **主文件**: `test_requirement_analysis_integration.py`
- **功能**: 測試 test_flow_mcp 的需求分析工作流
- **支持**: 所有 PowerAutomation 實體

## 運行測試

```bash
# 需求分析測試
cd tests/testcases/requirement_analysis/
python test_requirement_analysis_integration.py

# 未來的測試類型
cd tests/integration/    # 集成測試
cd tests/unit/          # 單元測試
cd tests/e2e/           # 端到端測試
```

## 測試結果

測試結果會自動保存到相應目錄下的 JSON 文件中，命名格式：
- `{test_name}_test_results_{timestamp}.json`

## 配置

測試配置支持多個 PowerAutomation 實體：
- 通過環境變量或配置文件指定目標實體
- 自動適配不同實體的 API 端點和認證方式
