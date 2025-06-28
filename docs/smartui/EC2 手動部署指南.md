# EC2 手動部署指南

## 🎯 目標
在 EC2 上部署 AICore + SmartUI，使用您提供的 Anthropic API Key。

## 🔧 方案選擇

### 方案 1: 修復現有 EC2 連接

**問題診斷**：
- EC2 實例 `18.212.97.173` 可達
- SSH 服務正常運行
- 密鑰認證失敗

**可能原因**：
1. 密鑰文件與實例不匹配
2. 實例可能已重新創建
3. 安全組限制了訪問

**解決步驟**：
```bash
# 1. 檢查 AWS 控制台
- 登錄 AWS 控制台
- 確認實例 i-xxx 狀態為 "running"
- 檢查關聯的密鑰對名稱
- 確認安全組允許您的 IP 訪問端口 22

# 2. 重新下載密鑰
- 如果密鑰對不匹配，重新下載正確的 .pem 文件
- 或者創建新的密鑰對並重新啟動實例

# 3. 測試連接
ssh -i correct-key.pem ec2-user@18.212.97.173
```

### 方案 2: 創建新的 EC2 實例

**使用提供的腳本**：
```bash
# 1. 配置 AWS CLI（如果未配置）
aws configure
# 輸入您的 AWS Access Key ID
# 輸入您的 AWS Secret Access Key
# 輸入區域：us-east-1
# 輸入輸出格式：json

# 2. 創建新實例
./create_new_ec2.sh

# 3. 等待創建完成並獲取連接信息
```

**手動創建（AWS 控制台）**：
1. 登錄 AWS 控制台
2. 進入 EC2 服務
3. 點擊 "Launch Instance"
4. 選擇 Amazon Linux 2 AMI
5. 選擇 t3.medium 實例類型
6. 配置安全組：
   - SSH (22): 0.0.0.0/0
   - Custom TCP (8080): 0.0.0.0/0
   - Custom TCP (3000): 0.0.0.0/0
7. 創建或選擇密鑰對
8. 啟動實例

### 方案 3: 使用 AWS Session Manager

**無需 SSH 密鑰的連接方式**：
```bash
# 1. 在 AWS 控制台中
- 進入 EC2 實例頁面
- 選擇您的實例
- 點擊 "Connect"
- 選擇 "Session Manager"
- 點擊 "Connect"

# 2. 在瀏覽器終端中執行部署
sudo yum update -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
# ... 繼續部署步驟
```

## 📦 部署步驟（連接成功後）

### 1. 上傳部署文件
```bash
# 從本地上傳到 EC2
scp -i your-key.pem aicore-smartui-ec2-complete.tar.gz ec2-user@YOUR_EC2_IP:~/
```

### 2. 連接到 EC2
```bash
ssh -i your-key.pem ec2-user@YOUR_EC2_IP
```

### 3. 解壓和部署
```bash
# 解壓部署包
tar -xzf aicore-smartui-ec2-complete.tar.gz

# 設置 API Key
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"

# 執行部署腳本
./ec2_deployment_package.sh
```

### 4. 配置環境變量
```bash
# 創建 .env 文件
cat > .env << EOF
ANTHROPIC_API_KEY=your-anthropic-api-key-here
REDIS_URL=redis://redis:6379
AICORE_PORT=8080
SMARTUI_PORT=3000
HOST=0.0.0.0
EOF
```

### 5. 啟動服務
```bash
# 使用 Docker Compose 啟動
docker-compose up -d

# 檢查服務狀態
docker-compose ps
docker-compose logs -f
```

## 🔍 驗證部署

### 檢查服務
```bash
# 測試 AICore API
curl http://localhost:8080/health

# 測試 SmartUI
curl http://localhost:3000

# 檢查 Docker 容器
docker ps
```

### 外部訪問
```bash
# 獲取 EC2 公網 IP
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "AICore API: http://$EC2_IP:8080"
echo "SmartUI 界面: http://$EC2_IP:3000"
```

## 🛠️ 故障排除

### 常見問題

**1. Docker 安裝失敗**
```bash
# 手動安裝 Docker
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
```

**2. 端口無法訪問**
```bash
# 檢查安全組設置
# 確保開放了 8080 和 3000 端口

# 檢查防火牆
sudo systemctl status firewalld
sudo firewall-cmd --list-all
```

**3. 服務啟動失敗**
```bash
# 查看詳細日誌
docker-compose logs aicore
docker-compose logs smartui
docker-compose logs redis

# 重新構建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📞 需要協助

如果遇到問題，請提供：
1. 錯誤信息截圖
2. `docker-compose logs` 輸出
3. EC2 實例 ID 和區域
4. 安全組配置截圖

我可以幫助您：
- 診斷連接問題
- 創建新的 EC2 實例
- 調試部署錯誤
- 優化配置設置

