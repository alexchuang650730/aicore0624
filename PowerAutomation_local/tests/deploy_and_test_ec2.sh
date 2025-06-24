#!/bin/bash

# PowerAutomation 一鍵部署腳本
# 執行完整的EC2部署流程

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${PURPLE}[STEP]${NC} $1"; }

# 配置變量
DOMAIN="${1:-$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'localhost')}"
EMAIL="${2:-admin@example.com}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 檢查是否為EC2環境
check_ec2_environment() {
    log_step "檢查EC2環境..."
    
    if curl -s --max-time 3 http://169.254.169.254/latest/meta-data/ >/dev/null 2>&1; then
        local instance_id=$(curl -s http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null)
        local region=$(curl -s http://169.254.169.254/latest/meta-data/placement/region 2>/dev/null)
        local public_ip=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null)
        
        log_success "檢測到EC2環境"
        log_info "實例ID: $instance_id"
        log_info "區域: $region"
        log_info "公網IP: $public_ip"
        
        # 如果沒有提供域名，使用公網IP
        if [[ "$DOMAIN" == "localhost" && -n "$public_ip" ]]; then
            DOMAIN="$public_ip"
            log_info "使用公網IP作為域名: $DOMAIN"
        fi
    else
        log_warning "未檢測到EC2環境，繼續本地部署"
    fi
}

# 設置腳本權限
setup_permissions() {
    log_step "設置腳本權限..."
    
    chmod +x "$SCRIPT_DIR"/*.sh
    log_success "腳本權限設置完成"
}

# 執行基礎部署
run_base_deployment() {
    log_step "執行基礎部署..."
    
    if [[ -f "$SCRIPT_DIR/deploy_powerautomation_ec2.sh" ]]; then
        "$SCRIPT_DIR/deploy_powerautomation_ec2.sh"
        log_success "基礎部署完成"
    else
        log_error "基礎部署腳本不存在"
        exit 1
    fi
}

# 配置系統服務
setup_services() {
    log_step "配置系統服務..."
    
    if [[ -f "$SCRIPT_DIR/setup_service.sh" ]]; then
        "$SCRIPT_DIR/setup_service.sh"
        log_success "系統服務配置完成"
    else
        log_error "服務配置腳本不存在"
        exit 1
    fi
}

# 配置Nginx
setup_nginx() {
    log_step "配置Nginx..."
    
    if [[ -f "$SCRIPT_DIR/setup_nginx.sh" ]]; then
        "$SCRIPT_DIR/setup_nginx.sh" "$DOMAIN" "$EMAIL"
        log_success "Nginx配置完成"
    else
        log_error "Nginx配置腳本不存在"
        exit 1
    fi
}

# 啟動服務
start_services() {
    log_step "啟動PowerAutomation服務..."
    
    # 啟動PowerAutomation服務
    sudo systemctl start powerautomation
    sudo systemctl enable powerautomation
    
    # 等待服務啟動
    sleep 10
    
    # 檢查服務狀態
    if systemctl is-active --quiet powerautomation; then
        log_success "PowerAutomation服務啟動成功"
    else
        log_error "PowerAutomation服務啟動失敗"
        sudo systemctl status powerautomation
        exit 1
    fi
    
    # 重啟Nginx
    sudo systemctl restart nginx
    
    if systemctl is-active --quiet nginx; then
        log_success "Nginx服務運行正常"
    else
        log_error "Nginx服務啟動失敗"
        sudo systemctl status nginx
        exit 1
    fi
}

# 執行測試
run_tests() {
    log_step "執行完整測試..."
    
    if [[ -f "$SCRIPT_DIR/test_ec2_deployment.sh" ]]; then
        if "$SCRIPT_DIR/test_ec2_deployment.sh"; then
            log_success "所有測試通過！"
            return 0
        else
            log_error "測試失敗！"
            return 1
        fi
    else
        log_error "測試腳本不存在"
        return 1
    fi
}

# 顯示部署信息
show_deployment_info() {
    log_step "部署信息總結..."
    
    echo
    echo "==================== 部署完成 ===================="
    echo
    log_success "PowerAutomation已成功部署到EC2！"
    echo
    log_info "訪問地址:"
    log_info "  HTTP:  http://$DOMAIN"
    log_info "  HTTPS: https://$DOMAIN"
    log_info "  API:   http://$DOMAIN/api/powerautomation/health"
    echo
    log_info "服務管理命令:"
    log_info "  sudo systemctl status powerautomation    # 查看狀態"
    log_info "  sudo systemctl restart powerautomation   # 重啟服務"
    log_info "  sudo systemctl logs powerautomation      # 查看日誌"
    echo
    log_info "日誌文件位置:"
    log_info "  應用日誌: /var/log/powerautomation/"
    log_info "  Nginx日誌: /var/log/nginx/"
    echo
    log_info "配置文件位置:"
    log_info "  應用配置: /home/ubuntu/powerautomation/smartinvention/powerautomation_server/.env"
    log_info "  Nginx配置: /etc/nginx/sites-available/powerautomation"
    echo
}

# 主函數
main() {
    log_info "開始PowerAutomation EC2一鍵部署..."
    echo
    
    if [[ $# -lt 1 ]]; then
        log_info "用法: $0 [domain] [email]"
        log_info "示例: $0 powerautomation.yourdomain.com admin@yourdomain.com"
        log_info "如果不提供域名，將自動使用EC2公網IP"
        echo
    fi
    
    # 執行部署步驟
    check_ec2_environment
    setup_permissions
    run_base_deployment
    setup_services
    setup_nginx
    start_services
    
    # 執行測試
    if run_tests; then
        show_deployment_info
        log_success "🎉 PowerAutomation EC2部署和測試完全成功！"
        exit 0
    else
        log_error "❌ 部署測試失敗，請檢查日誌並修復問題"
        log_info "查看詳細錯誤信息:"
        log_info "  sudo journalctl -u powerautomation -f"
        log_info "  sudo tail -f /var/log/powerautomation/error.log"
        exit 1
    fi
}

# 執行主函數
main "$@"

