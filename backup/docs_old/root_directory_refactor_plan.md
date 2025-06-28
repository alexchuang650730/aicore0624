# 根目錄重構計劃

## 📊 現狀分析

**根目錄文件統計：**
- 總文件數: 54 個
- 總目錄數: 15 個
- Python 文件: 8 個
- Shell 腳本: 15 個  
- Markdown 文件: 19 個
- JSON 文件: 5 個
- 日誌文件: 1 個
- PDF 文件: 1 個

## 🎯 重構目標

1. **保持核心文件在根目錄**
   - README.md (項目主要說明)
   - requirements.txt (依賴清單)
   - .gitignore (Git 忽略規則)

2. **按功能分類組織文件**
   - 部署相關 → `deployment/`
   - 文檔報告 → `docs/`
   - 腳本工具 → `scripts/`
   - 測試相關 → `tests/`
   - 開發相關 → `development/`

3. **移除無用文件**
   - 重複的備份文件
   - 過時的測試結果
   - 臨時文件

## 📁 文件分類計劃

### 🔧 部署相關文件 → `deployment/`
```
deploy_*.sh
mac_*.sh
ssh_remote_deployment.sh
setup_ec2_powerautomation_connection.sh
update_*.sh
alexchuang.pem (密鑰文件)
packages.microsoft.gpg
```

### 📚 文檔報告 → `docs/reports/`
```
*_Report*.md
*_Guide.md
*_Analysis.md
GitHub_Update_File_List*.md
human_loop_mcp_analysis.md
powerautomation_web_test_report.md
powerautomation_web_test_report.pdf
```

### 🧪 測試結果文件 → `tests/results/`
```
*.json (測試結果)
*.log (測試日誌)
enhanced_test_flow_mcp_v5_complete_report.json
```

### 🛠️ 開發工具 → `development/tools/`
```
aicore_*.py
deep_testing_framework.py
expert_invocation_system.py
incremental_optimization_system.py
mcp_functionality_verification.py
ec2_powerautomation_connection.py
real_mcp_connection_config.py
```

### 📋 SOP 文檔 → `docs/sop/`
```
TEST_FLOW_MCP_SOP.md
TEST_FLOW_API_TESTING_SOP.md
```

### 🗑️ 可移除的文件
```
PowerAutomation_local/ (備份目錄)
PowerAutomation_local_backup_20250625_050651/ (舊備份)
venv/ (虛擬環境，應該被 .gitignore)
build/ (編譯輸出)
wrangler.toml (Cloudflare 配置，可能不需要)
```

## 🚀 執行步驟

1. **創建目標目錄結構**
2. **移動文件到對應目錄**
3. **移除無用文件和目錄**
4. **更新 .gitignore**
5. **提交重構結果**

## ✅ 重構後的根目錄結構

```
aicore0624/
├── README.md                    # 項目說明
├── requirements.txt             # 依賴清單
├── .gitignore                   # Git 忽略規則
├── PowerAutomation/             # 核心系統
├── deployment/                  # 部署相關
│   ├── scripts/                 # 部署腳本
│   ├── configs/                 # 配置文件
│   └── keys/                    # 密鑰文件
├── docs/                        # 文檔
│   ├── sop/                     # 標準操作程序
│   ├── reports/                 # 報告文件
│   └── guides/                  # 指南文檔
├── development/                 # 開發相關
│   ├── tools/                   # 開發工具
│   ├── demos/                   # 示例代碼
│   └── experiments/             # 實驗性代碼
├── tests/                       # 測試相關
│   ├── results/                 # 測試結果
│   └── testcases/               # 測試案例
├── scripts/                     # 通用腳本
└── test_flow_api_examples/      # API 測試範例
```

## 📈 預期效果

- **根目錄文件數量**: 從 54 個減少到 < 10 個
- **目錄結構**: 更清晰的功能分類
- **維護性**: 更容易找到和管理文件
- **專業性**: 符合開源項目標準結構

