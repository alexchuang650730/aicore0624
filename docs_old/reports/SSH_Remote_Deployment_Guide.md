# PowerAutomation Local MCP 3.0.0 SSH遠程部署方案

## 🎯 SSH遠程部署概述

通過SSH連接到您的Mac，我可以直接執行PowerAutomation Local MCP 3.0.0的完整部署，包括：
- 直接安裝VSIX到您的VS Code
- 配置真實MCP組件
- 設置網路連接
- 創建自動化腳本

## 🔧 SSH連接設置步驟

### 步驟1: 在您的Mac上啟用SSH
```bash
# 在您的Mac終端執行
sudo systemsetup -setremotelogin on

# 檢查SSH狀態
sudo systemsetup -getremotelogin
```

### 步驟2: 創建部署用戶 (建議)
```bash
# 創建專用部署用戶 (可選，更安全)
sudo dscl . -create /Users/powerautomation
sudo dscl . -create /Users/powerautomation UserShell /bin/bash
sudo dscl . -create /Users/powerautomation RealName "PowerAutomation Deploy"
sudo dscl . -create /Users/powerautomation UniqueID 1001
sudo dscl . -create /Users/powerautomation PrimaryGroupID 20
sudo dscl . -create /Users/powerautomation NFSHomeDirectory /Users/powerautomation
sudo dscl . -passwd /Users/powerautomation [設置密碼]

# 或者使用您現有的用戶帳號
```

### 步驟3: 配置SSH金鑰認證 (推薦)
```bash
# 在您的Mac上生成SSH金鑰對
ssh-keygen -t rsa -b 4096 -C "powerautomation-deploy"

# 將公鑰添加到authorized_keys
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 步驟4: 獲取您的Mac連接資訊
```bash
# 獲取您的公網IP
curl ipinfo.io/ip

# 獲取您的本地IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# 獲取您的用戶名
whoami

# 檢查SSH端口 (通常是22)
sudo lsof -i :22
```

## 🚀 遠程部署執行方案

### 方案A: 使用密碼認證
```bash
# 我將使用以下命令連接您的Mac
ssh [您的用戶名]@[您的公網IP]

# 連接資訊格式
ssh username@xxx.xxx.xxx.xxx
```

### 方案B: 使用SSH金鑰認證 (更安全)
```bash
# 您需要提供私鑰文件
ssh -i /path/to/private_key [您的用戶名]@[您的公網IP]
```

## 📋 遠程部署腳本

讓我創建一個專門的SSH遠程部署腳本：

