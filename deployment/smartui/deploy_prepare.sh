#!/bin/bash

# SmartUI 权限管理系统部署脚本
# 目标服务器: 18.212.49.136
# 版本: 1.0.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# 配置
SERVER_HOST="18.212.49.136"
FRONTEND_PORT=3000
BACKEND_PORT=8081
PROJECT_NAME="smartui-permission"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${PURPLE}$1${NC}"
}

# 显示部署信息
show_deployment_info() {
    log_header "🚀 SmartUI 权限管理系统部署"
    echo "目标服务器: $SERVER_HOST"
    echo "前端端口: $FRONTEND_PORT"
    echo "后端端口: $BACKEND_PORT"
    echo "项目名称: $PROJECT_NAME"
    echo
}

# 准备部署文件
prepare_deployment() {
    log_header "📦 准备部署文件..."
    
    # 创建部署目录
    DEPLOY_DIR="/tmp/smartui-deploy-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$DEPLOY_DIR"
    
    # 复制项目文件
    log_info "复制项目文件..."
    cp -r /home/ubuntu/aicore0624/powerautomation_web/smartui "$DEPLOY_DIR/"
    cp -r /home/ubuntu/aicore0624/PowerAutomation/components/smartui_permission_mcp "$DEPLOY_DIR/"
    cp -r /home/ubuntu/aicore0624/deployment/smartui "$DEPLOY_DIR/config"
    
    # 创建生产环境配置
    log_info "创建生产环境配置..."
    cat > "$DEPLOY_DIR/smartui/.env.production" << EOF
VITE_API_BASE_URL=http://$SERVER_HOST:$BACKEND_PORT
VITE_AICORE_URL=http://$SERVER_HOST:8080
VITE_APP_TITLE=SmartUI 权限管理系统
VITE_APP_VERSION=1.0.0
EOF
    
    # 创建后端生产配置
    cat > "$DEPLOY_DIR/smartui_permission_mcp/config.py" << EOF
# 生产环境配置
import os

class ProductionConfig:
    HOST = '0.0.0.0'
    PORT = $BACKEND_PORT
    DEBUG = False
    
    # Redis 配置
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 1
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/smartui/permission_mcp.log'
    
    # API Keys
    API_KEY_ROLES = {
        'admin_qIFdydy7h_cZcop7uGNT73JRhjXQblHgWaRoDJMMz4U': 'admin',
        'dev_WqV-Kud9zmBOv_J_BtvMDJ5ZiPzibZR77o9mv-77Phg': 'developer',
        'user_Bx5z5aQbofp1fS1bNaXF-DTFnV_6X_iu6n7-7VTxi5k': 'user'
    }

config = ProductionConfig()
EOF
    
    log_success "部署文件准备完成: $DEPLOY_DIR"
    echo "$DEPLOY_DIR" > /tmp/smartui_deploy_dir
}

# 构建前端应用
build_frontend() {
    log_header "🏗️ 构建前端应用..."
    
    DEPLOY_DIR=$(cat /tmp/smartui_deploy_dir)
    cd "$DEPLOY_DIR/smartui"
    
    # 安装依赖
    log_info "安装前端依赖..."
    npm install --production
    
    # 构建应用
    log_info "构建生产版本..."
    npm run build
    
    log_success "前端应用构建完成"
}

# 创建系统服务文件
create_systemd_services() {
    log_header "⚙️ 创建系统服务..."
    
    DEPLOY_DIR=$(cat /tmp/smartui_deploy_dir)
    
    # 创建后端服务文件
    cat > "$DEPLOY_DIR/smartui-permission-backend.service" << EOF
[Unit]
Description=SmartUI Permission Management Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/smartui/backend
Environment=PYTHONPATH=/opt/smartui/backend
ExecStart=/usr/bin/python3 /opt/smartui/backend/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # 创建前端服务文件 (使用 serve)
    cat > "$DEPLOY_DIR/smartui-frontend.service" << EOF
[Unit]
Description=SmartUI Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/smartui/frontend
ExecStart=/usr/bin/npx serve -s dist -l $FRONTEND_PORT
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    log_success "系统服务文件创建完成"
}

# 创建 Nginx 配置
create_nginx_config() {
    log_header "🌐 创建 Nginx 配置..."
    
    DEPLOY_DIR=$(cat /tmp/smartui_deploy_dir)
    
    cat > "$DEPLOY_DIR/smartui.nginx.conf" << EOF
server {
    listen 80;
    server_name $SERVER_HOST smartui.aicore.dev;
    
    # 前端静态文件
    location / {
        proxy_pass http://localhost:$FRONTEND_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 后端 API
    location /api/ {
        proxy_pass http://localhost:$BACKEND_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # CORS 支持
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
        
        if (\$request_method = 'OPTIONS') {
            return 204;
        }
    }
    
    # 健康检查
    location /health {
        proxy_pass http://localhost:$BACKEND_PORT/health;
        proxy_set_header Host \$host;
    }
    
    # 日志配置
    access_log /var/log/nginx/smartui_access.log;
    error_log /var/log/nginx/smartui_error.log;
}
EOF
    
    log_success "Nginx 配置创建完成"
}

# 创建部署包
create_deployment_package() {
    log_header "📦 创建部署包..."
    
    DEPLOY_DIR=$(cat /tmp/smartui_deploy_dir)
    PACKAGE_NAME="smartui-permission-$(date +%Y%m%d-%H%M%S).tar.gz"
    
    cd "$(dirname $DEPLOY_DIR)"
    tar -czf "/tmp/$PACKAGE_NAME" "$(basename $DEPLOY_DIR)"
    
    log_success "部署包创建完成: /tmp/$PACKAGE_NAME"
    echo "/tmp/$PACKAGE_NAME" > /tmp/smartui_package_path
}

# 主函数
main() {
    show_deployment_info
    prepare_deployment
    build_frontend
    create_systemd_services
    create_nginx_config
    create_deployment_package
    
    PACKAGE_PATH=$(cat /tmp/smartui_package_path)
    
    log_success "🎉 部署文件准备完成！"
    echo
    echo "部署包位置: $PACKAGE_PATH"
    echo
    echo "下一步部署命令:"
    echo "1. 将部署包上传到服务器"
    echo "2. 在服务器上解压并安装"
    echo "3. 启动服务"
    echo
}

# 执行主函数
main "$@"

