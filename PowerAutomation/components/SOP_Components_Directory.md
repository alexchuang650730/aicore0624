# PowerAutomation Components 目錄標準操作程序 (SOP)

## 📋 目錄概述

`PowerAutomation/components/` 目錄專門用於存放**功能明確、一看就知道用途的工具組件**。這些組件是 PowerAutomation 系統的具體功能實現，每個組件都有清晰的職責和用途。

## 🎯 設計原則

### 1. 功能明確性
- **一看就懂**：從組件名稱就能清楚知道其功能
- **單一職責**：每個組件專注於一個特定的功能領域
- **用途清晰**：避免抽象或模糊的命名

### 2. 組件分類
- **MCP 組件**：使用 `_mcp` 後綴，實現 MCP (Model Context Protocol) 接口
- **適配器組件**：連接不同系統或服務的橋樑
- **工具組件**：提供特定功能的實用工具

### 3. 目錄結構
```
PowerAutomation/components/
├── __init__.py                    # Python 包初始化文件
├── SOP_Components_Directory.md    # 本 SOP 文檔
├── [component_name_mcp]/          # MCP 組件目錄
├── [tool_name]/                   # 工具組件目錄
└── [adapter_name]/                # 適配器組件目錄
```

## 📁 當前組件清單

### MCP 組件 (11個)
- `claude_sdk_mcp/` - 智能代码分析和专家咨询系统，基于Claude API的MCP组件
- `cloud_search_mcp/` - 雲端搜索工具，負責動態場景發現
- `code_generation_mcp/` - 代碼生成工作流工具
- `human_loop_mcp/` - 人工循環適配器
- `local_adapter_mcp/` - 本地適配器，含心跳管理功能
- `manus_adapter_mcp/` - Manus 系統適配器
- `recorder_workflow_mcp/` - 錄製工作流工具
- `smartinvention_mcp/` - SmartInvention 適配器
- `test_flow_mcp/` - 測試流程工具
- `vscode_installer_mcp/` - VSCode 安裝工具
- `vsix_deployer_mcp/` - VSIX 部署工具

## 🔧 組件開發規範

### 1. 命名規範
- **MCP 組件**：使用 `[功能名]_mcp` 格式
- **適配器組件**：使用 `[系統名]_adapter` 格式
- **工具組件**：使用描述性名稱，如 `[功能]_tool`

### 2. 目錄結構規範
每個組件目錄應包含：
```
component_name/
├── main.py                # 主要實現文件
├── README.md             # 組件說明文檔
├── config.json           # 配置文件（如需要）
└── examples/             # 使用範例（如需要）
```

### 3. 代碼規範
- **文檔字符串**：每個組件必須有清晰的文檔說明
- **類型提示**：使用 Python 類型提示提高代碼可讀性
- **錯誤處理**：實現適當的異常處理機制
- **日誌記錄**：使用統一的日誌格式

### 4. MCP 組件特殊要求
- 必須實現 MCP 接口規範
- 類名使用 `[ComponentName]MCP` 格式
- 提供標準的 MCP 方法：`initialize()`, `process()`, `cleanup()`

## 🚫 不適合放在 components 目錄的內容

### 1. 核心處理邏輯
- 通用處理器 → 應放在 `core/` 目錄
- 動態生成器 → 應放在 `core/` 目錄
- 場景分析器 → 應放在 `core/` 目錄

### 2. 配置和部署
- 部署腳本 → 應放在 `deployment/` 目錄
- 環境配置 → 應放在 `config/` 目錄

### 3. 測試相關
- 測試案例 → 應放在 `tests/` 目錄
- 測試工具 → 應放在 `tests/tools/` 目錄

### 4. 文檔和資源
- 系統文檔 → 應放在 `docs/` 目錄
- 靜態資源 → 應放在 `assets/` 目錄

## 📝 組件添加流程

### 1. 需求分析
- 確認組件功能是否明確且單一
- 檢查是否已有類似功能的組件
- 確定組件類型（MCP、適配器、工具）

### 2. 設計階段
- 定義組件接口和 API
- 設計配置參數和依賴關係
- 規劃測試策略

### 3. 實現階段
- 按照命名規範創建目錄
- 實現核心功能和接口
- 編寫文檔和使用範例

### 4. 測試階段
- 單元測試覆蓋
- 集成測試驗證
- 性能測試評估

### 5. 部署階段
- 更新 `__init__.py` 文件
- 更新本 SOP 文檔
- 提交代碼並創建 PR

## 🔄 組件維護規範

### 1. 版本管理
- 使用語義化版本號
- 重大更改需要向後兼容性考慮
- 維護變更日誌

### 2. 文檔更新
- 功能變更時同步更新文檔
- 保持 README.md 的準確性
- 更新使用範例

### 3. 依賴管理
- 最小化外部依賴
- 定期更新依賴版本
- 處理依賴衝突

### 4. 性能監控
- 監控組件性能指標
- 優化資源使用
- 處理內存洩漏

## 🚨 注意事項

### 1. 安全考慮
- 輸入驗證和清理
- 權限控制和訪問限制
- 敏感信息保護

### 2. 錯誤處理
- 優雅的錯誤處理
- 詳細的錯誤日誌
- 用戶友好的錯誤信息

### 3. 兼容性
- Python 版本兼容性
- 跨平台兼容性
- API 向後兼容性

## 📚 相關文檔

- [PowerAutomation 架構文檔](../docs/architecture.md)
- [MCP 協議規範](../docs/mcp_protocol.md)
- [開發者指南](../docs/developer_guide.md)
- [測試指南](../tests/README.md)

## 📞 聯繫方式

如有疑問或建議，請聯繫：
- 項目維護者：[維護者信息]
- 技術支持：[支持渠道]
- 問題報告：[Issue 追蹤系統]

---

**最後更新時間**：2024-06-26  
**版本**：v1.0  
**維護者**：PowerAutomation Team

