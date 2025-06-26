# PowerAutomation SmartUI Fusion 使用指南

## 🎯 概述

PowerAutomation SmartUI Fusion 是一個革命性的智慧 UI 系統，整合了 Claude SDK、三角色支持和智能決策引擎，為 VS Code 開發者提供前所未有的智能化開發體驗。

## 🚀 快速開始

### 1. 安裝插件

```bash
# 在 EC2 端編譯插件
cd /home/ubuntu/aicore0624/PowerAutomation_local/vscode-extension
npm install
npm run compile

# 通過反向隧道部署到 Mac
./auto_deploy_vsix_tunnel.sh
```

### 2. 角色切換

SmartUI 支持三種角色，每種角色有不同的功能和界面：

#### 👑 Admin 角色
- **快捷鍵**: `Cmd+Shift+1` (Mac) / `Ctrl+Shift+1` (Windows)
- **功能**: 系統管理、用戶管理、性能監控、安全審計

#### 👨‍💻 Developer 角色  
- **快捷鍵**: `Cmd+Shift+D` (Mac) / `Ctrl+Shift+D` (Windows)
- **功能**: 代碼分析、Claude 整合、項目管理、API 測試

#### 👤 User 角色
- **快捷鍵**: `Cmd+Shift+3` (Mac) / `Ctrl+Shift+3` (Windows)  
- **功能**: 簡化聊天、基礎分析、幫助系統

### 3. Claude AI 功能

#### 需求分析
- **快捷鍵**: `Cmd+Shift+A` (Mac) / `Ctrl+Shift+A` (Windows)
- **使用**: 選中文本 → 右鍵 → "SmartUI Claude 分析" → "Claude 需求分析"

#### 代碼審查
- **快捷鍵**: `Cmd+Shift+R` (Mac) / `Ctrl+Shift+R` (Windows)
- **使用**: 選中代碼 → 執行命令 → 獲得詳細審查報告

#### 代碼解釋
- **快捷鍵**: `Cmd+Shift+E` (Mac) / `Ctrl+Shift+E` (Windows)
- **使用**: 選中複雜代碼 → 執行命令 → 獲得清晰解釋

#### 代碼生成
- **快捷鍵**: `Cmd+Shift+G` (Mac) / `Ctrl+Shift+G` (Windows)
- **使用**: 輸入需求描述 → 執行命令 → 獲得生成的代碼

## 🧠 智能功能

### 1. 智能決策引擎

SmartUI 使用 5 種決策策略：

- **規則策略**: 基於預定義規則的快速決策
- **機器學習策略**: 基於歷史數據的智能預測
- **用戶行為策略**: 基於用戶習慣的個性化決策
- **角色策略**: 基於當前角色的專業化決策
- **混合策略**: 綜合多種策略的最優決策

### 2. 用戶行為分析

系統會自動分析：
- 操作效率和模式
- 功能使用頻率
- 會話時間和習慣
- 個性化偏好

### 3. 實時推薦系統

基於分析結果提供：
- 功能推薦
- 效率優化建議
- 學習資源推薦
- 工作流程優化

## 📊 系統監控

### 查看系統狀態
```
命令面板 → "PowerAutomation: 顯示系統狀態"
```

### 查看用戶分析
```
命令面板 → "PowerAutomation: 顯示用戶分析"
```

### 查看智能推薦
```
命令面板 → "PowerAutomation: 顯示智能推薦"
```

## ⚙️ 配置選項

在 VS Code 設置中可以配置：

```json
{
  "powerautomation.smartui.defaultRole": "developer",
  "powerautomation.smartui.enableRealTimeAnalysis": true,
  "powerautomation.smartui.enableSmartSuggestions": true,
  "powerautomation.smartui.autoSwitchRole": false,
  "powerautomation.smartui.analysisLanguage": "zh-CN",
  "powerautomation.smartui.theme": "auto"
}
```

## 🔧 故障排除

### 常見問題

1. **Claude 分析失敗**
   - 檢查網絡連接
   - 確認 API Key 配置正確
   - 查看輸出面板的錯誤信息

2. **角色切換無效**
   - 重啟 VS Code
   - 檢查插件是否正確安裝
   - 查看控制台錯誤信息

3. **智能推薦不準確**
   - 使用一段時間讓系統學習
   - 檢查用戶行為數據是否正常收集
   - 嘗試重置用戶分析數據

### 日誌查看

打開 VS Code 輸出面板，選擇 "PowerAutomation SmartUI" 查看詳細日誌。

## 🎯 最佳實踐

### 1. 角色使用建議

- **Admin**: 用於系統管理和監控任務
- **Developer**: 用於日常開發和代碼分析
- **User**: 用於學習和基礎操作

### 2. Claude 功能使用技巧

- 選擇有意義的代碼片段進行分析
- 提供清晰的需求描述
- 利用不同角色獲得不同視角的分析

### 3. 效率優化

- 使用快捷鍵提高操作效率
- 定期查看智能推薦
- 根據用戶分析調整工作習慣

## 🔄 更新和維護

### 插件更新
```bash
# 在 EC2 端更新代碼
cd /home/ubuntu/aicore0624
git pull origin smartui

# 重新編譯和部署
cd PowerAutomation_local/vscode-extension
npm run compile
./auto_deploy_vsix_tunnel.sh
```

### 數據備份
系統會自動保存用戶分析數據和配置，無需手動備份。

## 📞 支持

如有問題，請：
1. 查看輸出面板日誌
2. 檢查系統狀態
3. 重啟 VS Code 插件
4. 聯繫技術支持

---

**PowerAutomation SmartUI Fusion v1.0.0**  
*讓 AI 成為您的開發夥伴* 🚀

