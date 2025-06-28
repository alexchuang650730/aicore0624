# AICore + SmartUI 雲端部署指南

## 🎯 部署概述

本指南提供將 AICore MCP 服務器和 SmartUI 前端部署到雲端的完整方案，支持 AWS EC2、Azure VM、GCP Compute Engine 等平台。

## 📦 部署包內容

### AICore 服務器
- **端口**: 8080
- **技術棧**: FastAPI + Uvicorn + Redis
- **功能**: Claude Code SDK + SmartInvention MCP
- **健康檢查**: `/health`

### SmartUI 前端
- **端口**: 3000 (Nginx)
- **技術棧**: React + Vite + Nginx
- **功能**: GitHub 文件瀏覽 + AI 對話 + 代碼編輯
- **API 代理**: 自動代理到 AICore

## 🚀 快速部署 (Docker Compose)

### 1. 準備環境
```bash
# 在雲端服務器上執行
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安裝 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 上傳部署文件
```bash
# 將以下文件上傳到雲端服務器
- docker-compose.yml
- aicore_deploy/ (完整目錄)
- smartui_deploy/ (完整目錄)
- deploy_to_cloud.sh
```

### 3. 執行部署
```bash
# 設置 Anthropic API Key
export ANTHROPIC_API_KEY="your_api_key_here"

# 執行部署腳本
./deploy_to_cloud.sh
```

### 4. 驗證部署
```bash
# 檢查服務狀態
docker-compose ps

# 測試 AICore API
curl http://localhost:8080/health

# 測試 SmartUI
curl http://localhost:3000
```

## 🌐 AWS EC2 部署

### 1. 創建 EC2 實例
```bash
# 推薦配置
- 實例類型: t3.medium (2 vCPU, 4GB RAM)
- 操作系統: Amazon Linux 2 或 Ubuntu 20.04
- 存儲: 20GB gp3
- 安全組: 開放 22, 80, 3000, 8080 端口
```

### 2. 配置安全組
```bash
# 入站規則
SSH (22)     - 您的 IP
HTTP (80)    - 0.0.0.0/0
Custom (3000) - 0.0.0.0/0  # SmartUI
Custom (8080) - 0.0.0.0/0  # AICore API
```

### 3. 部署命令
```bash
# 連接到 EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# 上傳部署文件 (使用 scp 或 git clone)
scp -i your-key.pem -r ./deployment-files ec2-user@your-ec2-ip:~/

# 執行部署
cd ~/deployment-files
./deploy_to_cloud.sh
```

## 🔧 Azure VM 部署

### 1. 創建虛擬機
```bash
# Azure CLI 命令
az vm create \
  --resource-group myResourceGroup \
  --name aicore-smartui-vm \
  --image UbuntuLTS \
  --size Standard_B2s \
  --admin-username azureuser \
  --generate-ssh-keys
```

### 2. 開放端口
```bash
az vm open-port --port 80 --resource-group myResourceGroup --name aicore-smartui-vm
az vm open-port --port 3000 --resource-group myResourceGroup --name aicore-smartui-vm
az vm open-port --port 8080 --resource-group myResourceGroup --name aicore-smartui-vm
```

## ☁️ GCP Compute Engine 部署

### 1. 創建實例
```bash
gcloud compute instances create aicore-smartui-vm \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB
```

### 2. 配置防火牆
```bash
gcloud compute firewall-rules create allow-aicore-smartui \
  --allow tcp:80,tcp:3000,tcp:8080 \
  --source-ranges 0.0.0.0/0
```

## 🔍 監控和維護

### 查看日誌
```bash
# 查看所有服務日誌
docker-compose logs -f

# 查看特定服務日誌
docker-compose logs -f aicore
docker-compose logs -f smartui
docker-compose logs -f redis
```

### 重啟服務
```bash
# 重啟所有服務
docker-compose restart

# 重啟特定服務
docker-compose restart aicore
docker-compose restart smartui
```

### 更新部署
```bash
# 拉取最新代碼
git pull

# 重新構建和部署
docker-compose down
docker-compose build
docker-compose up -d
```

## 🛡️ 安全配置

### 1. 環境變量
```bash
# 創建 .env 文件
ANTHROPIC_API_KEY=your_secure_api_key
REDIS_PASSWORD=your_redis_password
JWT_SECRET=your_jwt_secret
```

### 2. HTTPS 配置 (可選)
```bash
# 使用 Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. 防火牆配置
```bash
# Ubuntu UFW
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## 📊 性能優化

### 1. Redis 配置
```bash
# 在 docker-compose.yml 中添加
redis:
  command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

### 2. Nginx 優化
```bash
# 在 nginx.conf 中添加
worker_processes auto;
worker_connections 1024;
gzip on;
gzip_types text/plain application/json application/javascript text/css;
```

## 🔗 訪問地址

部署完成後，您可以通過以下地址訪問：

- **SmartUI 界面**: `http://your-server-ip:3000`
- **AICore API**: `http://your-server-ip:8080`
- **健康檢查**: `http://your-server-ip:8080/health`
- **Redis 監控**: `http://your-server-ip:8080/api/cache/stats`

## 🆘 故障排除

### 常見問題

1. **服務無法啟動**
   ```bash
   docker-compose logs service-name
   ```

2. **端口被占用**
   ```bash
   sudo netstat -tlnp | grep :8080
   sudo kill -9 PID
   ```

3. **內存不足**
   ```bash
   free -h
   docker system prune -a
   ```

4. **API 連接失敗**
   - 檢查防火牆設置
   - 確認服務器 IP 地址
   - 驗證 CORS 配置

## 📞 支持

如需技術支持，請檢查：
1. 服務日誌: `docker-compose logs`
2. 系統資源: `htop` 或 `top`
3. 網絡連接: `curl -v http://localhost:8080/health`

