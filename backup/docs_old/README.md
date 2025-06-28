# PowerAutomation 文檔中心

歡迎來到 PowerAutomation 3.0.0 的文檔中心！這裡包含了完整的使用指南、集成文檔和最佳實踐。

## 📚 文檔目錄

### 🔧 集成指南 (`integration/`)

#### Human Loop MCP 集成系列
- **[Enhanced VSCode Installer MCP 集成指南](integration/Enhanced_VSCode_Installer_MCP_Integration_Guide.md)**
  - VSCode 擴展部署的人機交互集成
  - 生產環境部署確認、版本衝突解決
  - 完整的部署流程和風險控制

- **[General Processor MCP 集成指南](integration/General_Processor_MCP_Integration_Guide.md)**
  - 通用任務處理器的人機交互集成
  - 複雜任務策略選擇、異常處理決策
  - 批量處理和品質控制

- **[Human Loop MCP 最佳實踐指南](integration/Human_Loop_MCP_Best_Practices_Guide.md)**
  - 完整的實際使用示例
  - 生產環境部署流程、複雜數據處理工作流
  - 最佳實踐、錯誤處理、監控方案

### 🎬 工作流指南
- **[Recording Replay Guide](recording_replay_guide.md)**
  - 工作流錄製和重放功能指南

## 🎯 快速開始

### Human Loop MCP 集成
如果您想在 PowerAutomation 中集成人機交互功能：

1. **閱讀基礎概念**: 從 [Human Loop MCP 最佳實踐指南](integration/Human_Loop_MCP_Best_Practices_Guide.md) 開始
2. **選擇集成組件**: 
   - VSCode 擴展相關：[Enhanced VSCode Installer MCP 集成指南](integration/Enhanced_VSCode_Installer_MCP_Integration_Guide.md)
   - 通用任務處理：[General Processor MCP 集成指南](integration/General_Processor_MCP_Integration_Guide.md)
3. **實施集成**: 按照指南中的代碼示例進行集成

### 基本集成示例
```python
# 快速集成 Human Loop MCP
from PowerAutomation.components.human_loop_mcp_adapter import HumanLoopIntegrationMixin

class YourComponent(HumanLoopIntegrationMixin):
    async def your_method(self):
        # 在需要人工確認時
        result = await self.request_human_confirmation(
            title="操作確認",
            message="確定要執行此操作嗎？"
        )
        
        if result.get("success"):
            # 使用 AICore 現有功能執行操作
            return await self.aicore_execute()
```

## 🏗️ 架構設計原則

### Human Loop MCP 集成原則
✅ **充分利用 AICore** - 所有智能分析、決策推薦都使用 AICore 現有功能  
✅ **人機協作** - 在 AICore 不確定或高風險時引入人工判斷  
✅ **非侵入性集成** - 通過 Mixin 和客戶端方式，不修改現有代碼  
✅ **靈活配置** - 可根據環境和需求調整人工介入策略

### 集成方式
1. **繼承 Mixin** (推薦) - 最簡單的集成方式
2. **直接使用客戶端** - 更靈活的控制方式  
3. **便利函數** - 快速實現特定功能

## 📊 文檔統計

| 類別 | 文檔數量 | 總字數 | 說明 |
|------|----------|--------|------|
| 集成指南 | 3 個 | ~73,000 字 | Human Loop MCP 完整集成方案 |
| 工作流指南 | 1 個 | ~6,000 字 | Recording Replay 功能 |
| **總計** | **4 個** | **~79,000 字** | **完整文檔體系** |

## 🔗 相關資源

### 核心組件
- **PowerAutomation Core**: AICore 3.0.0 智能決策引擎
- **Human Loop MCP**: 人機交互服務 (http://localhost:8096)
- **Enhanced VSCode Installer MCP**: VSCode 擴展管理組件
- **General Processor MCP**: 通用任務處理組件

### 外部連結
- **GitHub 倉庫**: https://github.com/alexchuang650730/aicore0624
- **Human Loop MCP 原始項目**: https://github.com/alexchuang650730/aicore0615/tree/main/mcp/adapter/human_loop_mcp

## 📝 文檔維護

### 更新記錄
- **2024-06-24**: 新增 Human Loop MCP 集成指南系列
- **2024-06-24**: 創建文檔中心索引

### 貢獻指南
1. 所有文檔使用 Markdown 格式
2. 放置在對應的分類目錄中
3. 更新此 README.md 索引
4. 提交到 GitHub 倉庫

## 🆘 獲取幫助

如果您在使用過程中遇到問題：

1. **查閱相關文檔** - 首先查看對應的集成指南
2. **檢查配置** - 確認 Human Loop MCP 服務運行正常
3. **查看示例** - 參考最佳實踐指南中的完整示例
4. **檢查日誌** - 查看 PowerAutomation 和 Human Loop MCP 的日誌

---

**PowerAutomation 3.0.0** - 基於動態專家系統的智能自動化平台  
*讓 AI 更智能，讓人機協作更高效*

