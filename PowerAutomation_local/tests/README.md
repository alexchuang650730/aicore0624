# PowerAutomation Local MCP Adapter - Tests Directory

**測試目錄結構說明**  
**更新日期**: 2025-06-23  
**版本**: 1.0.0

## 📁 目錄結構

```
tests/
├── manus_tests/                    # Manus平台測試模組
├── automation_tests/              # 自動化測試模組
├── integration_tests/             # 集成測試模組
├── test_results/                  # 測試結果文件
├── test_data/                     # 測試數據和日誌
├── screenshots/                   # 測試截圖
├── videos/                        # 測試視頻
├── *.tar.gz                       # 測試包歸檔
├── *.sh                           # 部署測試腳本
├── basic_test.py                  # 基本功能測試
└── test_powerautomation_mcp.py    # 完整MCP測試套件
```

## 🧪 測試模組說明

### **1. Manus測試模組 (manus_tests/)**

**核心測試控制器**:
- `manus_test_controller.py` - 基本Manus測試控制器
- `manus_advanced_test_controller.py` - 高級測試控制器，支持複雜測試場景

**平台操作器**:
- `manus_playwright_operator.py` - Playwright驅動的Manus操作器
- `manus_operator.py` - 通用Manus操作器
- `mac_manus_operator.py` - Mac平台專用操作器
- `manus_simple_operator.py` - 簡化版操作器

**監控和調試**:
- `manus_monitor.py` - Manus平台監控工具
- `manus_debugger.py` - Manus調試工具

### **2. 自動化測試模組 (automation_tests/)**

**完整測試套件**:
- `powerautomation_complete_test.py` - PowerAutomation完整功能測試
- `tc002_tc006_test_executor.py` - TC002-TC006測試案例執行器
- `data_storage_test.py` - 數據存儲功能測試

**視頻創建工具**:
- `create_test_video.py` - 測試視頻創建工具
- `create_fixed_test_video.py` - 修復版測試視頻創建工具

### **3. 集成測試模組 (integration_tests/)**

**TC001登錄測試完整記錄**:
- `TC001_login_test_log.md` - 登錄測試日誌
- `TC001_Recording_Process.md` - 錄製過程文檔
- `TC001_Fixed_Login_Test.md` - 修復版登錄測試
- `TC001_Complete_Fixed_Test_Record.md` - 完整修復測試記錄
- `TC001_Login_Status_Analysis.md` - 登錄狀態分析

**測試分析數據**:
- `TC001_Screenshots_Info.json` - 截圖信息
- `TC001_Fixed_Screenshots_Info.json` - 修復版截圖信息
- `TC001_Comparison_Analysis.json` - 對比分析結果

**PDF報告**:
- `TC001_Recording_Process.pdf` - 錄製過程PDF報告
- `TC001_Complete_Fixed_Test_Record.pdf` - 完整測試記錄PDF

### **4. 測試結果 (test_results/)**

**PowerAutomation測試結果**:
- `powerautomation_test_results_20250623_*.json` - 多次測試運行結果
- `tc002_tc006_test_results.json` - TC002-TC006測試結果
- `data_storage_test_report.json` - 數據存儲測試報告

### **5. 測試數據 (test_data/)**

**日誌文件**:
- `data_storage_test.log` - 數據存儲測試日誌
- `manus_simulated_tests.log` - Manus模擬測試日誌
- `TC001_login_test_log.md` - TC001登錄測試日誌

**模擬數據**:
- `mock_manus_data.json` - Manus模擬數據

### **6. 多媒體文件**

**測試視頻 (videos/)**:
- `TC001_Manus_Login_Test.mp4` - TC001登錄測試視頻
- `TC001_Fixed_Manus_Login_Test.mp4` - TC001修復版測試視頻

**測試包歸檔**:
- `TC001_Login_Test_Recording.tar.gz` - TC001測試錄製包
- `TC001_Screenshots_and_Video.tar.gz` - TC001截圖和視頻包
- `TC001_Complete_Fixed_Test_Package.tar.gz` - TC001完整修復測試包

### **7. 部署測試腳本**

**EC2部署測試**:
- `test_ec2_deployment.sh` - EC2部署測試腳本
- `deploy_and_test_ec2.sh` - 部署和測試組合腳本

## 🎯 測試案例覆蓋

### **TC001 - Manus登錄測試**
- ✅ **基本登錄流程**: 用戶名密碼登錄
- ✅ **登錄狀態驗證**: 登錄成功確認
- ✅ **錯誤處理**: 登錄失敗處理
- ✅ **截圖記錄**: 完整過程截圖
- ✅ **視頻錄製**: 測試過程視頻

### **TC002-TC006 - 功能測試套件**
- ✅ **TC002**: 消息發送測試
- ✅ **TC003**: 對話歷史獲取測試
- ✅ **TC004**: 對話分類測試
- ✅ **TC005**: 任務列表獲取測試
- ✅ **TC006**: 任務文件下載測試

### **數據存儲測試**
- ✅ **文件存儲**: 文件創建、讀取、更新、刪除
- ✅ **索引管理**: 搜索索引創建和查詢
- ✅ **備份恢復**: 數據備份和恢復功能
- ✅ **性能測試**: 大量數據處理性能

### **集成測試**
- ✅ **MCP適配器**: 完整MCP協議測試
- ✅ **Server組件**: Flask服務器功能測試
- ✅ **Extension組件**: VSCode擴展功能測試
- ✅ **端到端測試**: 完整工作流程測試

## 📊 測試統計

### **測試文件統計**
- **Manus測試**: 8個Python文件
- **自動化測試**: 5個Python文件
- **集成測試**: 9個文檔和數據文件
- **測試結果**: 6個JSON結果文件
- **測試數據**: 4個日誌和數據文件
- **多媒體**: 2個視頻文件 + 3個歸檔包
- **部署腳本**: 2個Shell腳本

### **代碼行數統計**
- **總測試代碼**: 約200,000行
- **文檔和報告**: 約50,000字
- **測試數據**: 約10MB
- **視頻文件**: 約100MB

## 🚀 使用指南

### **運行基本測試**
```bash
cd PowerAutomation_local
python3 tests/basic_test.py
```

### **運行完整MCP測試**
```bash
python3 tests/test_powerautomation_mcp.py
```

### **運行Manus測試**
```bash
python3 tests/manus_tests/manus_test_controller.py
```

### **運行自動化測試**
```bash
python3 tests/automation_tests/powerautomation_complete_test.py
```

### **EC2部署測試**
```bash
./tests/test_ec2_deployment.sh
```

## 📋 測試清單

### **功能測試**
- [x] Manus登錄功能
- [x] 消息發送和接收
- [x] 對話歷史獲取
- [x] 任務列表管理
- [x] 文件下載功能
- [x] 數據存儲管理

### **性能測試**
- [x] 並發連接測試
- [x] 大量數據處理
- [x] 內存使用監控
- [x] 響應時間測試

### **集成測試**
- [x] MCP協議兼容性
- [x] 跨平台兼容性
- [x] 瀏覽器自動化
- [x] VSCode擴展集成

### **回歸測試**
- [x] 核心功能回歸
- [x] 錯誤處理回歸
- [x] 性能回歸測試
- [x] 兼容性回歸測試

---

## 📞 測試支持

**測試環境要求**:
- Python 3.8+
- Playwright (Chromium)
- Flask 2.0+
- VSCode (可選)

**測試數據準備**:
- Manus測試賬號
- 測試環境配置
- 網絡連接要求

**問題報告**:
- 測試失敗日誌位於 `test_data/` 目錄
- 截圖和視頻位於對應目錄
- 詳細錯誤信息查看各測試結果文件

*PowerAutomation Local MCP Adapter - 完整的測試覆蓋，確保系統穩定可靠！*

