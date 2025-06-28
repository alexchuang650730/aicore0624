# EC2 連接故障排除指南

## 🔍 **當前狀況**

**目標 EC2**: `ec2-user@18.212.97.173`
**問題**: 密鑰認證失敗 (Permission denied)
**密鑰文件**: 格式正確的 RSA 私鑰

## 🛠️ **解決方案**

### 方案 1: AWS 控制台檢查

**步驟**：
1. 登錄 AWS 控制台
2. 進入 EC2 服務
3. 找到 IP 為 `18.212.97.173` 的實例
4. 檢查以下信息：
   - 實例狀態是否為 "running"
   - 關聯的密鑰對名稱
   - 安全組是否允許您的 IP 訪問端口 22
   - 實例是否最近重新啟動過

### 方案 2: 使用 AWS Session Manager

**優勢**: 無需 SSH 密鑰，直接瀏覽器連接

**步驟**：
1. 在 AWS 控制台中找到您的 EC2 實例
2. 選擇實例，點擊 "Connect"
3. 選擇 "Session Manager" 標籤
4. 點擊 "Connect" 按鈕
5. 在瀏覽器終端中執行部署命令

### 方案 3: 重新創建密鑰對

**如果密鑰對不匹配**：
1. 在 AWS 控制台創建新的密鑰對
2. 停止 EC2 實例
3. 分離當前實例
4. 創建 AMI 快照
5. 使用新密鑰對啟動新實例

### 方案 4: 使用 EC2 Instance Connect

**如果實例支持**：
```bash
# 使用 AWS CLI
aws ec2-instance-connect send-ssh-public-key \
    --instance-id i-1234567890abcdef0 \
    --availability-zone us-east-1a \
    --instance-os-user ec2-user \
    --ssh-public-key file://~/.ssh/id_rsa.pub
```

## 📦 **部署包準備**

**無論使用哪種連接方式，部署包已準備就緒**：

### 文件清單
- `aicore-smartui-ec2-final.tar.gz` - 完整部署包
- `ec2_deployment_package.sh` - 一鍵部署腳本
- `docker-compose.yml` - 包含您的 API Key
- 完整的 AICore 和 SmartUI 代碼

### 上傳方式

**方式 1: SCP 上傳（需要 SSH 連接）**
```bash
scp -i /tmp/alexchuang_ec2.pem aicore-smartui-ec2-final.tar.gz ec2-user@18.212.97.173:~/
```

**方式 2: AWS S3 中轉**
```bash
# 1. 上傳到 S3
aws s3 cp aicore-smartui-ec2-final.tar.gz s3://your-bucket/

# 2. 在 EC2 中下載
aws s3 cp s3://your-bucket/aicore-smartui-ec2-final.tar.gz ~/
```

**方式 3: 直接在 EC2 中下載**
```bash
# 如果有公開下載鏈接
wget https://your-download-link/aicore-smartui-ec2-final.tar.gz
```

## 🚀 **部署命令（連接成功後執行）**

### 1. 基本環境準備
```bash
# 更新系統
sudo yum update -y

# 安裝必要工具
sudo yum install -y git curl wget unzip docker

# 啟動 Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# 安裝 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 部署 AICore + SmartUI
```bash
# 解壓部署包
tar -xzf aicore-smartui-ec2-final.tar.gz

# 執行部署腳本
chmod +x ec2_deployment_package.sh
./ec2_deployment_package.sh

# 或手動部署
docker-compose build
docker-compose up -d
```

### 3. 驗證部署
```bash
# 檢查服務狀態
docker-compose ps

# 測試 API
curl http://localhost:8080/health

# 測試前端
curl http://localhost:3000

# 獲取公網訪問地址
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "SmartUI: http://$EC2_IP:3000"
echo "AICore: http://$EC2_IP:8080"
```

## 🔧 **手動部署（如果腳本失敗）**

### Docker Compose 內容
```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  aicore:
    build: ./aicore_deploy
    ports:
      - "8080:8080"
    environment:
      - ANTHROPIC_API_KEY=your-anthropic-api-key-here
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  smartui:
    build: ./smartui_deploy
    ports:
      - "3000:80"
    depends_on:
      - aicore
```

### 手動構建命令
```bash
# 構建 AICore
cd aicore_deploy
docker build -t aicore .

# 構建 SmartUI
cd ../smartui_deploy
docker build -t smartui .

# 啟動 Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 啟動 AICore
docker run -d --name aicore -p 8080:8080 \
  -e ANTHROPIC_API_KEY="your-anthropic-api-key-here" \
  -e REDIS_URL="redis://redis:6379" \
  --link redis:redis aicore

# 啟動 SmartUI
docker run -d --name smartui -p 3000:80 \
  --link aicore:aicore smartui
```

## 📞 **需要協助**

如果仍然遇到問題，請提供：
1. AWS 控制台中實例的詳細信息截圖
2. 安全組配置截圖
3. 嘗試連接時的完整錯誤信息
4. 實例的密鑰對名稱

我可以幫助您：
- 診斷具體的連接問題
- 提供替代的連接方法
- 協助完成部署過程
- 優化配置設置

## 🎯 **預期結果**

部署成功後，您將獲得：
- **SmartUI 界面**: `http://18.212.97.173:3000`
- **AICore API**: `http://18.212.97.173:8080`
- **完整的 AI IDE 功能**
- **真實的 Claude Code SDK 集成**

