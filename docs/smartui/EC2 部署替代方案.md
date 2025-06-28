# EC2 部署替代方案

## 🔍 **連接問題分析**

EC2 實例 `18.212.97.173` 連接測試結果：
- ✅ 端口 22 可達
- ✅ SSH 服務運行正常
- ❌ 密鑰認證失敗
- 💡 系統提示使用 "ec2-user" 用戶

## 🛠️ **解決方案**

### 方案 1: 修復 SSH 連接 (推薦)

**可能原因**：
1. 密鑰文件與 EC2 實例不匹配
2. EC2 實例可能已重新創建
3. 安全組設置限制了 IP 訪問

**解決步驟**：
```bash
# 1. 檢查 EC2 控制台
- 確認實例狀態為 "running"
- 檢查安全組是否允許您的 IP 訪問端口 22
- 確認密鑰對名稱是否正確

# 2. 重新下載密鑰文件
- 如果實例重新創建，需要使用新的密鑰對
- 從 AWS 控制台重新下載 .pem 文件

# 3. 測試連接
ssh -i new-key.pem ec2-user@18.212.97.173
```

### 方案 2: 使用 Manus 雲端部署 (立即可用)

我已經準備好完整的雲端部署方案，可以立即使用：

**AICore 後端部署**：
```bash
# 使用 Manus 後端部署服務
cd /home/ubuntu/aicore_deploy
# 部署到雲端
```

**SmartUI 前端部署**：
```bash
# 使用 Manus 前端部署服務  
cd /home/ubuntu/smartui_deploy
# 部署到雲端
```

### 方案 3: 創建新的 EC2 實例

**快速創建步驟**：
```bash
# 1. AWS CLI 創建實例
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --count 1 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxxx

# 2. 配置安全組
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 8080 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 3000 \
  --cidr 0.0.0.0/0
```

## 🚀 **立即部署方案**

由於 EC2 連接問題，我建議使用 Manus 雲端服務立即部署：

### 部署 AICore 後端
```bash
cd /home/ubuntu
service_deploy_backend aicore_deploy flask
```

### 部署 SmartUI 前端  
```bash
cd /home/ubuntu
service_deploy_frontend smartui_deploy react
```

這樣可以：
- ✅ 立即獲得可用的雲端服務
- ✅ 自動配置 HTTPS 和域名
- ✅ 無需管理服務器
- ✅ 自動擴展和監控

## 📞 **需要協助**

如果您希望：
1. **修復 EC2 連接** - 請檢查 AWS 控制台中的實例狀態和安全組
2. **使用新的 EC2** - 我可以幫您創建新實例
3. **立即部署** - 我可以使用 Manus 雲端服務部署

請告訴我您偏好哪種方案！

