#!/bin/bash

# Agentic Agent 一鍵部署腳本
# 支持部署到EC2服務器

set -e  # 遇到錯誤立即退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日誌函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 檢查參數
if [ $# -lt 3 ]; then
    log_error "使用方法: $0 <EC2_HOST> <DEPLOY_PATH> <PORT>"
    log_info "例如: $0 18.212.97.173 /opt/agentic_agent 8080"
    exit 1
fi

EC2_HOST="$1"
DEPLOY_PATH="$2"
PORT="$3"
EC2_USER="ec2-user"
PROJECT_NAME="agentic_agent"
BACKUP_DIR="/opt/backups"
LOG_FILE="/tmp/agentic_agent_deploy.log"

log_info "開始部署 Agentic Agent 管理中心"
log_info "目標服務器: $EC2_HOST"
log_info "部署路徑: $DEPLOY_PATH"
log_info "服務端口: $PORT"

# 創建日誌文件
echo "部署開始時間: $(date)" > "$LOG_FILE"

# 檢查SSH連接
log_info "檢查SSH連接..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes "$EC2_USER@$EC2_HOST" exit 2>/dev/null; then
    log_error "無法連接到EC2服務器 $EC2_HOST"
    log_info "請確保:"
    log_info "1. SSH密鑰已正確配置"
    log_info "2. 安全組允許SSH連接"
    log_info "3. EC2實例正在運行"
    exit 1
fi
log_success "SSH連接正常"

# 準備本地項目文件
log_info "準備項目文件..."
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMP_DIR="/tmp/${PROJECT_NAME}_$(date +%s)"
mkdir -p "$TEMP_DIR"

# 複製項目文件
cp -r "$PROJECT_ROOT"/* "$TEMP_DIR/" 2>/dev/null || true
cp -r "$PROJECT_ROOT"/../simplified_agent "$TEMP_DIR/" 2>/dev/null || true

# 創建部署包
DEPLOY_PACKAGE="/tmp/${PROJECT_NAME}_deploy.tar.gz"
log_info "創建部署包: $DEPLOY_PACKAGE"
tar -czf "$DEPLOY_PACKAGE" -C "$TEMP_DIR" . >> "$LOG_FILE" 2>&1

# 清理臨時目錄
rm -rf "$TEMP_DIR"

log_success "部署包創建完成"

# 在EC2上執行部署
log_info "開始遠程部署..."

ssh "$EC2_USER@$EC2_HOST" << EOF
set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "\${BLUE}[INFO]\${NC} \$1"; }
log_success() { echo -e "\${GREEN}[SUCCESS]\${NC} \$1"; }
log_warning() { echo -e "\${YELLOW}[WARNING]\${NC} \$1"; }
log_error() { echo -e "\${RED}[ERROR]\${NC} \$1"; }

log_info "在EC2服務器上開始部署..."

# 檢查並安裝依賴
log_info "檢查系統依賴..."

# 檢查Python3
if ! command -v python3 &> /dev/null; then
    log_info "安裝Python3..."
    sudo yum update -y
    sudo yum install -y python3 python3-pip
fi

# 檢查Node.js
if ! command -v node &> /dev/null; then
    log_info "安裝Node.js..."
    curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
    sudo yum install -y nodejs
fi

# 檢查Git
if ! command -v git &> /dev/null; then
    log_info "安裝Git..."
    sudo yum install -y git
fi

log_success "系統依賴檢查完成"

# 創建備份
if [ -d "$DEPLOY_PATH" ]; then
    log_info "備份現有部署..."
    sudo mkdir -p "$BACKUP_DIR"
    BACKUP_NAME="${PROJECT_NAME}_backup_\$(date +%Y%m%d_%H%M%S)"
    sudo cp -r "$DEPLOY_PATH" "$BACKUP_DIR/\$BACKUP_NAME" || true
    log_success "備份完成: $BACKUP_DIR/\$BACKUP_NAME"
fi

# 創建部署目錄
log_info "創建部署目錄..."
sudo mkdir -p "$DEPLOY_PATH"
sudo chown \$USER:wheel "$DEPLOY_PATH" 2>/dev/null || sudo chown \$USER:ec2-user "$DEPLOY_PATH"

# 停止現有服務
log_info "停止現有服務..."
sudo pkill -f "python.*app.py" || true
sudo pkill -f "gunicorn.*app:app" || true
sleep 2

log_success "遠程環境準備完成"
EOF

if [ $? -ne 0 ]; then
    log_error "遠程環境準備失敗"
    exit 1
fi

# 上傳部署包
log_info "上傳部署包到EC2..."
scp "$DEPLOY_PACKAGE" "$EC2_USER@$EC2_HOST:/tmp/" >> "$LOG_FILE" 2>&1

if [ $? -ne 0 ]; then
    log_error "部署包上傳失敗"
    exit 1
fi

log_success "部署包上傳完成"

# 解壓和配置
log_info "解壓和配置應用..."

ssh "$EC2_USER@$EC2_HOST" << EOF
set -e

log_info() { echo -e "\033[0;34m[INFO]\033[0m \$1"; }
log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m \$1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m \$1"; }

# 解壓部署包
log_info "解壓部署包..."
cd "$DEPLOY_PATH"
tar -xzf "/tmp/${PROJECT_NAME}_deploy.tar.gz"

# 設置權限
chmod +x backend/app.py 2>/dev/null || true
chmod +x backend/deploy_to_ec2.sh 2>/dev/null || true

# 安裝Python依賴
log_info "安裝Python依賴..."
cd backend
python3 -m pip install --user -r requirements.txt

# 創建日誌目錄
mkdir -p logs temp backups

# 創建systemd服務文件
log_info "創建系統服務..."
sudo tee /etc/systemd/system/agentic-agent.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=Agentic Agent Management Center
After=network.target

[Service]
Type=simple
User=$EC2_USER
WorkingDirectory=$DEPLOY_PATH/backend
Environment=PATH=/home/$EC2_USER/.local/bin:\$PATH
Environment=PORT=$PORT
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# 重新載入systemd並啟動服務
sudo systemctl daemon-reload
sudo systemctl enable agentic-agent
sudo systemctl start agentic-agent

log_success "服務配置完成"
EOF

if [ $? -ne 0 ]; then
    log_error "應用配置失敗"
    exit 1
fi

# 等待服務啟動
log_info "等待服務啟動..."
sleep 5

# 驗證部署
log_info "驗證部署狀態..."

# 檢查服務狀態
ssh "$EC2_USER@$EC2_HOST" << EOF
log_info() { echo -e "\033[0;34m[INFO]\033[0m \$1"; }
log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m \$1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m \$1"; }

# 檢查服務狀態
if sudo systemctl is-active --quiet agentic-agent; then
    log_success "Agentic Agent 服務運行正常"
    sudo systemctl status agentic-agent --no-pager -l
else
    log_error "Agentic Agent 服務啟動失敗"
    sudo systemctl status agentic-agent --no-pager -l
    sudo journalctl -u agentic-agent --no-pager -l -n 20
    exit 1
fi

# 檢查端口監聽
if netstat -tlnp | grep ":$PORT " > /dev/null; then
    log_success "服務正在監聽端口 $PORT"
else
    log_warning "端口 $PORT 可能未正確監聽"
fi
EOF

# 測試HTTP連接
log_info "測試HTTP連接..."
sleep 3

if curl -s --connect-timeout 10 "http://$EC2_HOST:$PORT/api/health" > /dev/null; then
    log_success "HTTP服務響應正常"
else
    log_warning "HTTP服務可能未完全啟動，請稍後再試"
fi

# 清理本地臨時文件
rm -f "$DEPLOY_PACKAGE"

# 部署完成
log_success "🎉 Agentic Agent 部署完成！"
echo ""
log_info "部署信息:"
log_info "  服務器地址: $EC2_HOST"
log_info "  部署路徑: $DEPLOY_PATH"
log_info "  服務端口: $PORT"
log_info "  管理界面: http://$EC2_HOST:$PORT"
log_info "  健康檢查: http://$EC2_HOST:$PORT/api/health"
echo ""
log_info "服務管理命令:"
log_info "  查看狀態: ssh $EC2_USER@$EC2_HOST 'sudo systemctl status agentic-agent'"
log_info "  重啟服務: ssh $EC2_USER@$EC2_HOST 'sudo systemctl restart agentic-agent'"
log_info "  查看日誌: ssh $EC2_USER@$EC2_HOST 'sudo journalctl -u agentic-agent -f'"
echo ""
log_info "部署日誌已保存到: $LOG_FILE"

echo "部署完成時間: $(date)" >> "$LOG_FILE"

