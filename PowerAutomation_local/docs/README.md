# PowerAutomation Local MCP v3.1.1

> 新一代AI驅動自動化平台 - 重構版本  
> 三角色權限系統 + 智慧登錄 + 清晰項目結構

[![Version](https://img.shields.io/badge/version-3.1.1-blue.svg)](https://github.com/alexchuang650730/aicore0624)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-VS%20Code-orange.svg)](https://code.visualstudio.com/)

## 🎯 項目概述

PowerAutomation Local MCP v3.1.1 是一個完全重構的AI驅動自動化平台，提供：

- **🔐 三角色權限系統**: 管理員、開發者、用戶的差異化體驗
- **🎨 智慧登錄界面**: 兩套獨立的UI系統
- **📁 清晰項目結構**: 功能模塊化組織
- **🔌 VS Code 深度整合**: 無縫的開發體驗
- **🤖 MCP 協議支援**: 與 Manus 平台完美對接

## 📁 項目結構

```
PowerAutomation_local/
├── core/                           # 🔧 核心組件
│   ├── server/                     # 服務器管理組件
│   ├── shared/                     # 共享工具和異常處理
│   ├── mcp_server.py              # MCP 服務器主文件
│   └── powerautomation_local_mcp.py # 本地 MCP 實現
├── vscode-extension/               # 📦 VS Code 擴展 (v3.1.1)
│   ├── src/                       # TypeScript 源代碼
│   ├── out/                       # 編譯後的 JavaScript
│   ├── *.vsix                     # 打包的擴展文件
│   └── package.json               # 擴展配置
├── extension/                      # 🔌 擴展管理器
├── tests/                          # 🧪 測試文件
├── scripts/                        # 📜 腳本工具
│   ├── deploy/                    # 部署相關腳本
│   └── dev/                       # 開發工具
├── docs/                           # 📖 文檔
├── config/                         # ⚙️ 配置文件
└── start.sh                       # 🚀 啟動腳本
```

## 🚀 快速開始

### 1. 安裝依賴

```bash
# 運行安裝腳本
./scripts/deploy/install.sh

# 或手動安裝
pip install -r config/requirements.txt
```

### 2. 啟動服務

```bash
# 啟動 PowerAutomation MCP 服務器
./start.sh

# 或直接啟動核心服務
python core/mcp_server.py
```

### 3. 安裝 VS Code 擴展

```bash
# 自動部署擴展
python scripts/deploy/vsix_auto_deployer.py

# 或手動安裝
code --install-extension vscode-extension/powerautomation-local-mcp-3.1.1.vsix
```

## 🔐 三角色權限系統

### 🔴 管理員 (Admin)
- **API Key**: `admin_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **權限**: 完整系統權限，用戶管理，系統配置
- **界面**: 紅色專業主題，完整管理功能

### 🟡 開發者 (Developer)
- **API Key**: `dev_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **權限**: 開發工具，API 訪問，調試功能
- **界面**: 橙色開發主題，專業工具集

### 🟢 用戶 (User)
- **登錄方式**: OAuth (GitHub/Google/Microsoft) 或郵箱登錄
- **API Key**: 系統自動生成 `user_` 開頭的 Key
- **權限**: 基礎功能，聊天，文件管理
- **界面**: 藍色友好主題，簡潔易用

## 🎨 智慧登錄系統

### 用戶界面
- OAuth 多平台登錄
- 郵箱密碼登錄
- 自動生成 API Key
- 簡潔友好的設計

### 高級界面
- API Key 直接登錄
- 本地開發模式
- MCP 端點配置
- 專業的管理工具

## 🔧 核心功能

### MCP 服務器
- **文件**: `core/mcp_server.py`
- **功能**: MCP 協議通信，請求處理
- **端口**: 5000 (HTTP), 5001 (WebSocket)

### VS Code 擴展
- **版本**: v3.1.1
- **功能**: 三角色認證，智慧UI，權限控制
- **文件**: `vscode-extension/powerautomation-local-mcp-3.1.1.vsix`

### 自動化測試
- **目錄**: `tests/`
- **功能**: 完整的測試套件，自動化驗證
- **支援**: 截圖，視頻錄製，測試報告

## 📜 腳本工具

### 部署腳本 (`scripts/deploy/`)
- `vsix_auto_deployer.py` - VSIX 自動部署器
- `test_auto_deployment.sh` - 自動部署測試
- `package_project.sh` - 項目打包腳本
- `install.sh` - 環境安裝腳本

### 開發工具 (`scripts/dev/`)
- `basic_test.py` - 基礎功能測試
- `test_powerautomation_mcp.py` - MCP 協議測試
- `mock_deployment_api.py` - 模擬部署 API
- `cli.py` - 命令行工具

## ⚙️ 配置管理

### 主配置文件
- **文件**: `config/config.toml`
- **格式**: TOML
- **內容**: 服務器、認證、路徑、功能開關等

### 關鍵配置項
```toml
[extension.auth]
enable_role_system = true          # 啟用角色系統
admin_key_prefix = "admin_"        # 管理員 Key 前綴
developer_key_prefix = "dev_"      # 開發者 Key 前綴
user_key_prefix = "user_"          # 用戶 Key 前綴

[features]
three_role_auth = true             # 三角色認證系統
smart_login = true                 # 智慧登錄
web_interface = false              # 網頁界面 (待整合)
```

## 🧪 測試與驗證

### 運行測試
```bash
# 基礎功能測試
python scripts/dev/basic_test.py

# MCP 協議測試
python scripts/dev/test_powerautomation_mcp.py

# 完整測試套件
cd tests && python -m pytest
```

### 測試覆蓋
- ✅ MCP 協議通信
- ✅ 三角色認證系統
- ✅ VS Code 擴展功能
- ✅ 自動化測試流程
- ✅ 文件管理和存儲

## 📖 文檔資源

### 核心文檔 (`docs/`)
- `INSTALLATION_GUIDE.md` - 詳細安裝指南
- `DELIVERY_REPORT.md` - 項目交付報告
- `README_v3.0.0.md` - 舊版本文檔

### 在線資源
- [GitHub 倉庫](https://github.com/alexchuang650730/aicore0624)
- [Manus 平台](https://manus.im)
- [VS Code 擴展市場](https://marketplace.visualstudio.com/)

## 🔄 版本歷史

### v3.1.1 (2025-06-25) - 重構版本
- ✨ 完全重構項目結構
- 🔐 實現三角色權限系統
- 🎨 智慧登錄界面
- 📁 清晰的功能分離
- 🧹 清理無用文件和目錄

### v3.1.0 (2025-06-25)
- 🔐 智慧登錄系統
- 🎯 用戶權限管理
- 🔧 MCP 服務整合

### v3.0.0 (2025-06-23)
- 🚀 初始版本發布
- 🤖 MCP 協議支援
- 🔌 VS Code 擴展

## 🤝 貢獻指南

### 開發環境設置
1. 克隆倉庫：`git clone https://github.com/alexchuang650730/aicore0624.git`
2. 進入目錄：`cd aicore0624/PowerAutomation_local`
3. 安裝依賴：`./scripts/deploy/install.sh`
4. 啟動服務：`./start.sh`

### 提交規範
- `feat:` 新功能
- `fix:` 錯誤修復
- `docs:` 文檔更新
- `refactor:` 代碼重構
- `test:` 測試相關

## 📞 支援與反饋

### 聯繫方式
- **GitHub Issues**: [提交問題](https://github.com/alexchuang650730/aicore0624/issues)
- **Email**: chuang.hsiaoyen@gmail.com
- **Manus 平台**: [在線支援](https://manus.im)

### 常見問題
1. **Q**: 如何切換用戶角色？
   **A**: 使用不同前綴的 API Key 或重新登錄選擇角色

2. **Q**: 擴展安裝失敗怎麼辦？
   **A**: 檢查 VS Code 版本，運行 `scripts/deploy/vsix_auto_deployer.py`

3. **Q**: MCP 服務器無法啟動？
   **A**: 檢查端口占用，確認配置文件路徑正確

## 📄 授權協議

本項目採用 MIT 授權協議。詳見 [LICENSE](LICENSE) 文件。

---

**PowerAutomation Team**  
© 2025 - 新一代AI驅動自動化平台

