# PowerAutomation 快速開始指南

本指南將幫助您快速上手 PowerAutomation 項目。

## 🚀 環境準備

### 系統要求
- Python 3.8+
- Node.js 16+
- Git

### 安裝依賴
```bash
# 克隆項目
git clone https://github.com/alexchuang650730/aicore0624.git
cd aicore0624

# 安裝 Python 依賴
pip install -r requirements.txt

# 安裝 Node.js 依賴（如果需要）
cd powerautomation_web
npm install
```

## 🏗️ 核心組件

### PowerAutomation (雲端組件)
- **SmartInvention MCP**: Manus 數據收集和分析
- **Test Flow MCP**: 測試流程自動化
- **Manus Adapter MCP**: Manus 系統適配器

### PowerAutomation_local (端側組件)
- **本地自動化引擎**: 核心自動化功能
- **VSCode 擴展**: 開發工具整合
- **MCP 服務器**: 與雲端通信

## 🔧 配置

### 1. Manus 配置
編輯 `PowerAutomation/components/smartinvention_mcp/manus_config.json`:
```json
{
  "manus": {
    "login_email": "your_email@example.com",
    "login_password": "your_password"
  }
}
```

### 2. 啟動服務
```bash
# 啟動雲端組件
cd PowerAutomation
python -m components.smartinvention_mcp.main

# 啟動本地組件
cd PowerAutomation_local
python -m core.powerautomation_local_mcp
```

## 📚 更多資源

- [架構設計](../architecture/project-overview.md)
- [組件文檔](../components/)
- [API 參考](../integration/smartinvention_mcp_api_guide.md)
- [測試指南](../testing/)

## 🆘 常見問題

### Q: 如何配置 Manus 認證？
A: 請參考 [Manus 配置指南](../integration/smartinvention_mcp_api_guide.md)

### Q: 如何運行測試？
A: 請參考 [測試指南](../testing/)

### Q: 如何部署到生產環境？
A: 請參考 [部署指南](../deployment/)

---

*如有問題，請查看 [完整文檔](../README.md) 或提交 Issue。*

