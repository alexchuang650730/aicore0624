#!/bin/bash

# AICore + SmartUI 雲端部署腳本
# 支持 Docker Compose 和直接部署

set -e

echo "🚀 開始 AICore + SmartUI 雲端部署..."

# 檢查 Docker 是否安裝
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝，正在安裝..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker 安裝完成"
fi

# 檢查 Docker Compose 是否安裝
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安裝，正在安裝..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose 安裝完成"
fi

# 創建部署目錄
DEPLOY_DIR="/opt/aicore-smartui"
sudo mkdir -p $DEPLOY_DIR
sudo chown $USER:$USER $DEPLOY_DIR
cd $DEPLOY_DIR

# 複製部署文件
echo "📦 準備部署文件..."
cp /home/ubuntu/docker-compose.yml .
cp -r /home/ubuntu/aicore_deploy ./aicore
cp -r /home/ubuntu/smartui_deploy ./smartui

# 設置環境變量
echo "🔧 配置環境變量..."
cat > .env << EOF
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-your_anthropic_api_key_here}
REDIS_URL=redis://redis:6379
AICORE_PORT=8080
SMARTUI_PORT=3000
EOF

# 構建和啟動服務
echo "🏗️ 構建 Docker 鏡像..."
docker-compose build

echo "🚀 啟動服務..."
docker-compose up -d

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 30

# 檢查服務狀態
echo "🔍 檢查服務狀態..."
docker-compose ps

# 測試服務
echo "🧪 測試服務連接..."
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ AICore 服務正常運行"
else
    echo "❌ AICore 服務啟動失敗"
    docker-compose logs aicore
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ SmartUI 服務正常運行"
else
    echo "❌ SmartUI 服務啟動失敗"
    docker-compose logs smartui
fi

echo "🎉 部署完成！"
echo "📊 AICore API: http://localhost:8080"
echo "🎨 SmartUI 界面: http://localhost:3000"
echo "📋 查看日誌: docker-compose logs -f"
echo "🛑 停止服務: docker-compose down"

