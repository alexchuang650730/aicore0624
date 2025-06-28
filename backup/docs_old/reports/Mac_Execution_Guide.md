# PowerAutomation Mac環境執行指南

## 🎯 目標
在真實Mac環境中執行PowerAutomation VSIX部署和功能驗證測試

## 📋 前置要求

### 系統要求
- macOS 10.15 或更高版本
- 已安裝Git
- 已安裝VS Code
- 終端訪問權限

### 可選要求
- Homebrew (用於安裝VS Code，如果尚未安裝)
- SSH客戶端 (用於連接EC2，如果需要)

## 🚀 執行步驟

### 步驟1: 準備工作目錄
```bash
# 打開終端
# 創建工作目錄
mkdir -p ~/PowerAutomation
cd ~/PowerAutomation

# 克隆項目
git clone https://github.com/alexchuang650730/aicore0624.git
cd aicore0624
```

### 步驟2: 檢查VS Code安裝
```bash
# 檢查VS Code是否已安裝
which code

# 如果未安裝，使用Homebrew安裝
brew install --cask visual-studio-code

# 或者手動下載安裝
# https://code.visualstudio.com/download
```

### 步驟3: 執行Mac部署腳本
```bash
# 使部署腳本可執行
chmod +x deploy_vsix_mac.sh

# 執行Mac部署腳本
./deploy_vsix_mac.sh
```

### 步驟4: 執行Mac驗證測試
```bash
# 使測試腳本可執行
chmod +x mac_verification_test.sh

# 執行完整驗證測試
./mac_verification_test.sh
```

## 📊 預期輸出

### 成功部署輸出示例
```
🚀 PowerAutomation VSIX Mac部署開始
============================================================
✅ 確認Mac環境
✅ VSIX文件存在: PowerAutomation_local/vscode-extension/powerautomation-local-mcp-3.0.0.vsix (921KB)
✅ VS Code版本: 1.101.1
✅ 擴展安裝成功
✅ 擴展驗證成功: powerautomation.powerautomation-local-mcp@3.0.0
🎉 PowerAutomation VSIX Mac部署完成!
```

### 成功測試輸出示例
```
🚀 PowerAutomation Mac環境驗證測試開始
============================================================
✅ 確認Mac環境
✅ macOS版本: 14.5
✅ aicore0624項目已存在
✅ VSIX文件存在: PowerAutomation_local/vscode-extension/powerautomation-local-mcp-3.0.0.vsix (921KB)
✅ 在PATH中找到VS Code命令
✅ VS Code版本: 1.101.1
✅ 擴展安裝成功
✅ 擴展驗證成功: powerautomation.powerautomation-local-mcp@3.0.0
🎉 PowerAutomation Mac環境驗證測試完成!
```

## 🔧 故障排除

### 常見問題1: VS Code未找到
**錯誤**: `VS Code command not found in PATH`
**解決方案**:
```bash
# 方法1: 使用Homebrew安裝
brew install --cask visual-studio-code

# 方法2: 手動添加到PATH
export PATH="/Applications/Visual Studio Code.app/Contents/Resources/app/bin:$PATH"

# 方法3: 創建符號鏈接
sudo ln -s "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" /usr/local/bin/code
```

### 常見問題2: 權限問題
**錯誤**: `Permission denied`
**解決方案**:
```bash
# 給腳本執行權限
chmod +x deploy_vsix_mac.sh
chmod +x mac_verification_test.sh

# 如果仍有問題，檢查文件所有者
ls -la *.sh
```

### 常見問題3: Git未安裝
**錯誤**: `git: command not found`
**解決方案**:
```bash
# 安裝Xcode命令行工具
xcode-select --install

# 或使用Homebrew安裝Git
brew install git
```

### 常見問題4: VSIX文件不存在
**錯誤**: `VSIX文件不存在`
**解決方案**:
```bash
# 確保在正確目錄
pwd
ls -la PowerAutomation_local/vscode-extension/

# 重新克隆項目
git clone https://github.com/alexchuang650730/aicore0624.git
```

## 📁 生成的文件

執行完成後，將生成以下文件：

### 部署文件
- `mac_vsix_deployment_*.log` - 部署日誌
- `mac_vsix_deployment_report_*.json` - 部署報告

### 測試文件
- `mac_verification_test_*.log` - 測試日誌
- `mac_verification_report_*.json` - 驗證報告

## 🧪 驗證擴展功能

### 在VS Code中驗證
1. 打開VS Code
2. 按 `Cmd+Shift+P` 打開命令面板
3. 搜索 "PowerAutomation" 查看可用命令
4. 檢查擴展面板中是否顯示PowerAutomation擴展
5. 查看擴展是否已啟用

### 檢查擴展文件
```bash
# 查看擴展安裝目錄
ls -la ~/.vscode/extensions/*powerautomation*

# 檢查擴展配置
cat ~/.vscode/extensions/powerautomation.powerautomation-local-mcp-*/package.json
```

## 🔗 EC2連接測試 (可選)

如果您有EC2 SSH密鑰，可以測試與雲端的連接：

```bash
# 將SSH密鑰放在項目根目錄
cp /path/to/alexchuang.pem .
chmod 600 alexchuang.pem

# 測試EC2連接
ssh -i alexchuang.pem -o ConnectTimeout=10 ec2-user@18.212.97.173 "echo 'EC2連接測試成功'"
```

## 📋 檢查清單

執行前檢查：
- [ ] macOS系統 (10.15+)
- [ ] 已安裝Git
- [ ] 已安裝VS Code
- [ ] 終端可以訪問
- [ ] 網絡連接正常

執行後驗證：
- [ ] VSIX擴展已安裝
- [ ] 擴展在VS Code中可見
- [ ] 擴展功能可用
- [ ] 生成了部署報告
- [ ] 生成了測試報告

## 🆘 獲取幫助

如果遇到問題：

1. **檢查日誌文件** - 查看生成的 `.log` 文件
2. **查看報告文件** - 檢查 `.json` 報告文件
3. **重新執行** - 嘗試重新運行腳本
4. **聯繫支持** - 通過GitHub Issues報告問題

## 📞 聯繫信息

- **項目倉庫**: https://github.com/alexchuang650730/aicore0624
- **問題報告**: GitHub Issues
- **技術文檔**: 項目README.md

---

**執行指南版本**: v1.0  
**最後更新**: 2025年6月24日  
**適用平台**: macOS

