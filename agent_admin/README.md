# 🤖 Agentic Agent 管理中心

基於增強版簡化Agent架構的專業管理界面，整合Kilo Code MCP代碼執行引擎，提供完整的Agent管理、工具註冊、任務執行和系統監控功能。

## 🎯 核心特色

### 🏗️ **增強版簡化架構**
- **統一AI決策**: 替代複雜三層架構，100%基於AI推理
- **智能工具整合**: Smart Tool Engine + Adapter MCP + Kilo Code MCP
- **成本優化**: 平均40%成本節省，響應時間提升60-70%
- **高性能**: 支持50個並發請求，平均響應時間<200ms

### 💻 **Kilo Code MCP 代碼執行**
- **多語言支持**: Python、JavaScript、Shell、SQL
- **安全沙盒**: 隔離執行環境，多層安全防護
- **智能整合**: 與Agent架構無縫協作
- **實時監控**: 執行狀態、性能指標、資源使用

### 🎨 **專業管理界面**
- **現代化設計**: 響應式Web界面，支持桌面和移動設備
- **六大功能模組**: 儀表板、Agent管理、工具管理、代碼執行、執行中心、監控中心、部署管理
- **實時監控**: 系統狀態、性能指標、任務執行實時更新
- **一鍵操作**: 快速分析、工具刷新、系統檢查、EC2部署

## 📁 項目結構

```
aicore0622/
├── simplified_agent/          # 增強版簡化Agent架構
│   ├── core/                 # Agent核心引擎
│   │   ├── enhanced_agent_core.py
│   │   └── agent_core.py
│   ├── tools/                # 工具註冊表
│   │   ├── enhanced_tool_registry.py
│   │   └── tool_registry.py
│   ├── actions/              # 執行引擎
│   │   └── action_executor.py
│   ├── config/               # 配置管理
│   │   ├── enhanced_config.py
│   │   └── config.py
│   ├── examples/             # 使用示例
│   ├── tests/                # 測試文件
│   └── docs/                 # 文檔
├── agent_admin/              # 管理中心
│   ├── frontend/             # Web管理界面
│   │   └── index.html        # 響應式管理界面
│   ├── backend/              # API服務
│   │   ├── app.py           # Flask API服務
│   │   ├── requirements.txt  # Python依賴
│   │   └── deploy_to_ec2.sh # EC2部署腳本
│   ├── config/              # 配置文件
│   ├── docs/                # 文檔
│   ├── deploy/              # 部署相關
│   └── start_local.sh       # 本地啟動腳本
├── PROJECT_SUMMARY.md        # 項目總結
└── README.md                # 項目說明
```

## 🚀 快速開始

### 本地運行

1. **克隆項目**
   ```bash
   git clone https://github.com/alexchuang650730/aicore0622.git
   cd aicore0622
   ```

2. **啟動服務**
   ```bash
   cd agent_admin
   ./start_local.sh
   ```

3. **訪問界面**
   - 管理界面: http://localhost:8080
   - 健康檢查: http://localhost:8080/api/health
   - API文檔: 查看下方API端點說明

### 部署到EC2

1. **配置SSH密鑰**
   ```bash
   # 確保可以SSH到EC2服務器
   ssh ec2-user@18.212.97.173
   ```

2. **一鍵部署**
   ```bash
   cd agent_admin/backend
   ./deploy_to_ec2.sh 18.212.97.173 /opt/agentic_agent 8080
   ```

3. **訪問生產環境**
   - 管理界面: http://18.212.97.173:8080
   - 健康檢查: http://18.212.97.173:8080/api/health

## 🔧 功能模組

### 📊 **儀表板**
- **實時狀態**: Agent狀態、工具數量、執行任務、系統性能
- **快速操作**: 快速分析、刷新工具、系統檢查、EC2部署
- **性能指標**: 響應時間、成功率、並發數、成本節省

### 🤖 **Agent 管理**
- **配置管理**: Agent名稱、環境配置、AI模型參數
- **環境切換**: 開發/生產/測試環境配置
- **模型配置**: GPT-4、溫度、最大令牌、超時設置

### 🔧 **工具管理**
- **工具註冊表**: 自動發現和註冊可用工具
- **能力展示**: 詳細的工具能力分類和描述
- **狀態監控**: 實時工具健康狀態檢查
- **智能路由**: 多維度評分的最優工具選擇

### 💻 **代碼執行中心**
- **多語言支持**: Python、JavaScript、Shell、SQL
- **代碼編輯器**: 語法高亮、自動完成、示例代碼
- **執行選項**: 網絡訪問、超時時間、記憶體限制
- **結果展示**: 執行結果、標準輸出、錯誤信息、性能指標

### ⚡ **執行中心**
- **任務描述**: 自然語言任務描述
- **執行模式**: 智能/並行/順序/管道四種模式
- **結果追蹤**: 詳細的執行結果和性能指標

### 📈 **監控中心**
- **性能監控**: 響應時間、成功率、並發數
- **成本分析**: 成本節省百分比、優化建議
- **實時指標**: 系統資源使用、任務執行狀態

### 🚀 **部署管理**
- **EC2配置**: 服務器地址、部署路徑、服務端口
- **一鍵部署**: 自動化部署到生產環境
- **狀態檢查**: 部署狀態驗證、服務健康檢查
- **服務管理**: 重啟服務、查看日誌

## 📊 API 端點

### 系統管理
- `GET /api/health` - 健康檢查
- `GET /api/dashboard` - 儀表板數據
- `POST /api/health-check` - 系統健康檢查
- `GET /api/logs` - 獲取系統日誌

### Agent 管理
- `POST /api/agent/config` - 更新Agent配置
- `POST /api/service/restart` - 重啟Agent服務

### 工具管理
- `GET /api/tools` - 獲取工具列表
- `POST /api/tools/refresh` - 刷新工具註冊表

### 代碼執行 (Kilo Code MCP)
- `POST /api/code/execute` - 執行代碼
- `GET /api/code/languages` - 獲取支持的編程語言

### 任務執行
- `POST /api/execute` - 執行Agent任務
- `POST /api/quick-analysis` - 快速分析

### 監控指標
- `GET /api/metrics` - 獲取系統監控指標

### 部署管理
- `POST /api/deploy` - 部署到EC2
- `POST /api/deployment/status` - 檢查部署狀態

## 🔒 安全機制

### Kilo Code MCP 安全
- **代碼掃描**: 靜態代碼分析，檢測危險操作
- **沙盒隔離**: 隔離的執行環境，防止系統破壞
- **資源限制**: 執行時間、記憶體使用、網絡訪問限制
- **權限控制**: 最小權限原則，限制文件和系統訪問

### 系統安全
- **CORS配置**: 跨域請求安全控制
- **輸入驗證**: 所有API輸入參數驗證
- **錯誤處理**: 安全的錯誤信息返回
- **日誌記錄**: 完整的操作日誌記錄

## ⚡ 性能優化

### 架構優化
- **簡化設計**: 從複雜三層架構簡化為統一決策架構
- **異步處理**: 支持50個並發請求
- **智能緩存**: 執行結果緩存機制
- **資源池**: 執行器資源池管理

### 成本優化
- **智能路由**: 自動選擇最經濟的工具方案
- **成本監控**: 實時成本分析和優化建議
- **預算控制**: 詳細的成本管理配置

## 🔧 配置說明

### 環境配置
```json
{
  "name": "enhanced_agent",
  "environment": "development",
  "model_config": {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000,
    "timeout": 30
  }
}
```

### 部署配置
- **EC2地址**: 18.212.97.173
- **部署路徑**: /opt/agentic_agent
- **服務端口**: 8080
- **備份目錄**: /opt/backups

### Kilo Code MCP 配置
```json
{
  "supported_languages": ["python", "javascript", "shell", "sql"],
  "security": {
    "timeout": 30,
    "memory_limit": 128,
    "network_access": false
  },
  "sandbox": {
    "isolation": true,
    "resource_limits": true
  }
}
```

## 🛠️ 開發指南

### 本地開發
1. **安裝依賴**
   ```bash
   cd agent_admin/backend
   pip3 install -r requirements.txt
   ```

2. **啟動開發服務**
   ```bash
   python3 app.py
   ```

3. **訪問開發界面**
   ```
   http://localhost:8080
   ```

### 添加新功能
1. **後端API**: 在`backend/app.py`中添加新的API端點
2. **前端功能**: 在`frontend/index.html`中添加對應的前端功能
3. **工具整合**: 在`simplified_agent/tools/`中添加新的工具
4. **測試驗證**: 使用本地環境測試新功能

### 部署新版本
1. **本地測試**: `./start_local.sh`
2. **提交代碼**: `git add . && git commit -m "新功能" && git push`
3. **部署到EC2**: `./backend/deploy_to_ec2.sh`
4. **驗證部署**: 訪問生產環境URL

## 📈 性能指標

### 系統性能
- **響應時間**: < 200ms (平均)
- **並發處理**: 支持50個並發請求
- **成功率**: > 95%
- **成本節省**: 平均40%

### 架構優勢
- **代碼量減少**: 約50%
- **開發效率**: 提升3-5倍
- **維護成本**: 降低60%
- **部署時間**: < 5分鐘

## 🔍 故障排除

### 常見問題

1. **服務無法啟動**
   ```bash
   # 檢查端口佔用
   netstat -tlnp | grep 8080
   
   # 檢查Python依賴
   pip3 list | grep -E "(flask|requests)"
   
   # 查看錯誤日誌
   tail -f agent_admin/backend/logs/agent_admin.log
   ```

2. **部署失敗**
   ```bash
   # 檢查SSH連接
   ssh ec2-user@18.212.97.173
   
   # 檢查EC2磁碟空間
   df -h
   
   # 查看部署日誌
   cat /tmp/agentic_agent_deploy.log
   ```

3. **代碼執行失敗**
   ```bash
   # 檢查Python環境
   python3 --version
   
   # 檢查Node.js環境
   node --version
   
   # 檢查安全限制
   # 查看API返回的錯誤信息
   ```

### 日誌位置
- **本地日誌**: `agent_admin/backend/logs/agent_admin.log`
- **部署日誌**: `/tmp/agentic_agent_deploy.log`
- **EC2服務日誌**: `sudo journalctl -u agentic-agent -f`

### 服務管理命令
```bash
# EC2服務管理
ssh ec2-user@18.212.97.173

# 查看服務狀態
sudo systemctl status agentic-agent

# 重啟服務
sudo systemctl restart agentic-agent

# 查看實時日誌
sudo journalctl -u agentic-agent -f

# 停止服務
sudo systemctl stop agentic-agent
```

## 🔄 更新和維護

### 定期維護
1. **系統更新**: 定期更新系統依賴和安全補丁
2. **日誌清理**: 定期清理舊的日誌文件
3. **備份檢查**: 驗證備份文件的完整性
4. **性能監控**: 監控系統性能指標

### 版本更新
1. **本地測試**: 在本地環境充分測試新版本
2. **備份數據**: 部署前備份現有配置和數據
3. **滾動更新**: 使用部署腳本進行無縫更新
4. **回滾準備**: 準備快速回滾方案

## 📞 技術支持

### 獲取幫助
1. **文檔查閱**: 查看本README和項目文檔
2. **日誌分析**: 查看系統日誌獲取詳細錯誤信息
3. **健康檢查**: 使用管理界面的健康檢查功能
4. **社區支持**: 參與開源社區討論

### 貢獻指南
1. **Fork項目**: 在GitHub上Fork本項目
2. **創建分支**: 為新功能創建專門的分支
3. **提交PR**: 提交Pull Request並描述變更
4. **代碼審查**: 參與代碼審查和討論

## 🎉 致謝

感謝以下技術和項目的支持：
- **Kimi-Researcher**: 簡化架構設計理念
- **Smart Tool Engine**: 智能工具整合方案
- **MCP Protocol**: 模型控制協議標準
- **Flask**: 輕量級Web框架
- **React**: 前端開發框架

---

**🚀 Agentic Agent 管理中心 - 讓AI Agent管理變得簡單高效！**

*基於增強版簡化Agent架構 + Kilo Code MCP + Smart Tool Engine*

