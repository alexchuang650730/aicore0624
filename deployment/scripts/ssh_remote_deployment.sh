#!/bin/bash

# PowerAutomation Local MCP 3.0.0 SSH遠程部署腳本
# 通過SSH連接到用戶Mac並執行完整部署

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_header() { echo -e "${PURPLE}🚀 $1${NC}"; echo "=" $(printf "%*s" ${#1} "" | tr ' ' '='); }

# SSH連接配置 (需要用戶提供)
MAC_HOST=""
MAC_USER=""
MAC_PASSWORD=""
SSH_KEY=""
SSH_PORT="22"

# 部署配置
POWERAUTOMATION_REPO="https://github.com/alexchuang650730/aicore0624.git"
PROJECT_DIR="aicore0624"
EXTENSION_ID="powerautomation.powerautomation-local-mcp"
VSIX_FILE="PowerAutomation_local/vscode-extension/powerautomation-local-mcp-3.0.0.vsix"
REMOTE_DEPLOY_LOG="ssh_remote_deployment_$(date +%Y%m%d_%H%M%S).log"

# 創建部署日誌
exec > >(tee -a "$REMOTE_DEPLOY_LOG") 2>&1

print_header "PowerAutomation SSH遠程部署"

# 獲取用戶Mac連接資訊
get_mac_connection_info() {
    print_header "獲取Mac連接資訊"
    
    if [[ -z "$MAC_HOST" ]]; then
        read -p "請輸入您的Mac公網IP或域名: " MAC_HOST
    fi
    
    if [[ -z "$MAC_USER" ]]; then
        read -p "請輸入您的Mac用戶名: " MAC_USER
    fi
    
    # 選擇認證方式
    echo "請選擇SSH認證方式:"
    echo "1) 密碼認證"
    echo "2) SSH金鑰認證"
    read -p "請選擇 (1 或 2): " auth_method
    
    case $auth_method in
        1)
            read -s -p "請輸入您的Mac密碼: " MAC_PASSWORD
            echo
            ;;
        2)
            read -p "請輸入SSH私鑰文件路徑: " SSH_KEY
            if [[ ! -f "$SSH_KEY" ]]; then
                print_error "SSH金鑰文件不存在: $SSH_KEY"
                exit 1
            fi
            ;;
        *)
            print_error "無效選擇"
            exit 1
            ;;
    esac
    
    print_success "Mac連接資訊已獲取"
    print_info "主機: $MAC_HOST"
    print_info "用戶: $MAC_USER"
    print_info "認證: $([ -n "$SSH_KEY" ] && echo "SSH金鑰" || echo "密碼")"
}

# 測試SSH連接
test_ssh_connection() {
    print_header "測試SSH連接"
    
    local ssh_cmd=""
    if [[ -n "$SSH_KEY" ]]; then
        ssh_cmd="ssh -i $SSH_KEY -p $SSH_PORT -o ConnectTimeout=10 -o StrictHostKeyChecking=no $MAC_USER@$MAC_HOST"
    else
        ssh_cmd="sshpass -p '$MAC_PASSWORD' ssh -p $SSH_PORT -o ConnectTimeout=10 -o StrictHostKeyChecking=no $MAC_USER@$MAC_HOST"
    fi
    
    print_info "測試連接到 $MAC_USER@$MAC_HOST..."
    
    if $ssh_cmd "echo 'SSH連接測試成功' && uname -a"; then
        print_success "SSH連接測試成功"
        return 0
    else
        print_error "SSH連接測試失敗"
        print_info "請檢查:"
        print_info "1. Mac是否已啟用SSH (系統偏好設定 > 共享 > 遠程登錄)"
        print_info "2. 網路連接是否正常"
        print_info "3. 用戶名和密碼/金鑰是否正確"
        print_info "4. 防火牆設置是否允許SSH連接"
        return 1
    fi
}

# 在Mac上執行遠程命令
execute_remote_command() {
    local command="$1"
    local description="$2"
    
    if [[ -n "$description" ]]; then
        print_info "$description"
    fi
    
    local ssh_cmd=""
    if [[ -n "$SSH_KEY" ]]; then
        ssh_cmd="ssh -i $SSH_KEY -p $SSH_PORT -o StrictHostKeyChecking=no $MAC_USER@$MAC_HOST"
    else
        ssh_cmd="sshpass -p '$MAC_PASSWORD' ssh -p $SSH_PORT -o StrictHostKeyChecking=no $MAC_USER@$MAC_HOST"
    fi
    
    if $ssh_cmd "$command"; then
        return 0
    else
        print_error "遠程命令執行失敗: $command"
        return 1
    fi
}

# 傳輸文件到Mac
transfer_file_to_mac() {
    local local_file="$1"
    local remote_path="$2"
    local description="$3"
    
    if [[ -n "$description" ]]; then
        print_info "$description"
    fi
    
    local scp_cmd=""
    if [[ -n "$SSH_KEY" ]]; then
        scp_cmd="scp -i $SSH_KEY -P $SSH_PORT -o StrictHostKeyChecking=no"
    else
        scp_cmd="sshpass -p '$MAC_PASSWORD' scp -P $SSH_PORT -o StrictHostKeyChecking=no"
    fi
    
    if $scp_cmd "$local_file" "$MAC_USER@$MAC_HOST:$remote_path"; then
        print_success "文件傳輸成功: $local_file -> $remote_path"
        return 0
    else
        print_error "文件傳輸失敗: $local_file"
        return 1
    fi
}

# 檢查Mac環境
check_mac_environment() {
    print_header "檢查Mac環境"
    
    # 檢查macOS版本
    execute_remote_command "sw_vers" "檢查macOS版本"
    
    # 檢查是否已安裝必要軟體
    execute_remote_command "command -v git && echo 'Git已安裝' || echo 'Git未安裝'" "檢查Git"
    execute_remote_command "command -v python3 && python3 --version || echo 'Python3未安裝'" "檢查Python3"
    execute_remote_command "command -v code && code --version || echo 'VS Code未安裝'" "檢查VS Code"
    execute_remote_command "command -v brew && echo 'Homebrew已安裝' || echo 'Homebrew未安裝'" "檢查Homebrew"
}

# 安裝依賴軟體
install_dependencies_on_mac() {
    print_header "在Mac上安裝依賴軟體"
    
    # 安裝Homebrew (如果未安裝)
    execute_remote_command "
        if ! command -v brew &> /dev/null; then
            echo '安裝Homebrew...'
            /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"
            
            # 添加Homebrew到PATH
            if [[ -f \"/opt/homebrew/bin/brew\" ]]; then
                echo 'eval \"\$(/opt/homebrew/bin/brew shellenv)\"' >> ~/.zprofile
                eval \"\$(/opt/homebrew/bin/brew shellenv)\"
            elif [[ -f \"/usr/local/bin/brew\" ]]; then
                echo 'eval \"\$(/usr/local/bin/brew shellenv)\"' >> ~/.zprofile
                eval \"\$(/usr/local/bin/brew shellenv)\"
            fi
        else
            echo 'Homebrew已安裝'
        fi
    " "安裝Homebrew"
    
    # 安裝Git
    execute_remote_command "
        if ! command -v git &> /dev/null; then
            echo '安裝Git...'
            brew install git
        else
            echo 'Git已安裝'
        fi
    " "安裝Git"
    
    # 安裝Python3
    execute_remote_command "
        if ! command -v python3 &> /dev/null; then
            echo '安裝Python3...'
            brew install python
        else
            echo 'Python3已安裝'
        fi
    " "安裝Python3"
    
    # 安裝VS Code
    execute_remote_command "
        if ! command -v code &> /dev/null; then
            if [[ ! -f \"/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code\" ]]; then
                echo '安裝VS Code...'
                brew install --cask visual-studio-code
            fi
            
            # 添加code命令到PATH
            if [[ -f \"/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code\" ]]; then
                sudo ln -sf \"/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code\" /usr/local/bin/code
            fi
        else
            echo 'VS Code已安裝'
        fi
    " "安裝VS Code"
    
    # 安裝Python依賴
    execute_remote_command "
        echo '安裝Python依賴...'
        python3 -m pip install --upgrade pip
        python3 -m pip install aiohttp aiofiles psutil requests
    " "安裝Python依賴"
}

# 部署PowerAutomation項目
deploy_powerautomation_project() {
    print_header "部署PowerAutomation項目"
    
    # 克隆或更新項目
    execute_remote_command "
        if [[ -d \"$PROJECT_DIR\" ]]; then
            echo '更新PowerAutomation項目...'
            cd \"$PROJECT_DIR\"
            git pull origin main || git pull origin master
            cd ..
        else
            echo '克隆PowerAutomation項目...'
            git clone \"$POWERAUTOMATION_REPO\" \"$PROJECT_DIR\"
        fi
    " "克隆/更新PowerAutomation項目"
    
    # 檢查VSIX文件
    execute_remote_command "
        if [[ -f \"$PROJECT_DIR/$VSIX_FILE\" ]]; then
            echo 'VSIX文件存在'
            ls -la \"$PROJECT_DIR/$VSIX_FILE\"
        else
            echo 'VSIX文件不存在'
            exit 1
        fi
    " "檢查VSIX文件"
}

# 安裝VS Code擴展
install_vscode_extension_remote() {
    print_header "安裝VS Code擴展"
    
    execute_remote_command "
        cd \"$PROJECT_DIR\"
        
        # 檢查並卸載現有擴展
        if code --list-extensions | grep -q \"$EXTENSION_ID\"; then
            echo '卸載現有PowerAutomation擴展...'
            code --uninstall-extension \"$EXTENSION_ID\" || true
            sleep 3
        fi
        
        # 安裝新擴展
        echo '安裝PowerAutomation Local MCP 3.0.0...'
        if code --install-extension \"$VSIX_FILE\" --force; then
            echo 'PowerAutomation擴展安裝成功'
            sleep 5
        else
            echo 'PowerAutomation擴展安裝失敗'
            exit 1
        fi
        
        # 驗證安裝
        if code --list-extensions | grep -q \"$EXTENSION_ID\"; then
            INSTALLED_VERSION=\$(code --list-extensions --show-versions | grep \"$EXTENSION_ID\" | cut -d'@' -f2)
            echo \"擴展安裝驗證成功: $EXTENSION_ID@\$INSTALLED_VERSION\"
        else
            echo '擴展安裝驗證失敗'
            exit 1
        fi
        
        cd ..
    " "安裝VS Code擴展"
}

# 配置MCP組件
configure_mcp_components_remote() {
    print_header "配置MCP組件"
    
    # 創建MCP配置腳本並傳輸到Mac
    cat > "remote_mcp_config.py" << 'EOF'
#!/usr/bin/env python3
"""
遠程MCP組件配置腳本
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# 添加PowerAutomation路徑
sys.path.insert(0, 'PowerAutomation')
sys.path.insert(0, 'PowerAutomation_local')

async def configure_mcp_components():
    """配置MCP組件"""
    print("🔧 配置MCP組件...")
    
    config = {
        "mcp_config": {
            "timestamp": datetime.now().isoformat(),
            "config_id": f"remote_mcp_{int(datetime.now().timestamp())}",
            "platform": "macOS",
            "deployment_type": "ssh_remote"
        },
        "components": {
            "local_adapter": {
                "enabled": True,
                "real_mode": True,
                "config": {
                    "adapter_id": f"mac_adapter_{int(datetime.now().timestamp())}",
                    "platform": "macOS"
                }
            },
            "tool_registry": {
                "enabled": True,
                "real_mode": True,
                "config": {
                    "smart_engine": True,
                    "cloud_platforms": True
                }
            },
            "aicore": {
                "enabled": True,
                "real_mode": True,
                "config": {
                    "dynamic_experts": True,
                    "cloud_search": True
                }
            }
        }
    }
    
    # 保存配置
    with open('mac_remote_mcp_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ MCP配置已創建: mac_remote_mcp_config.json")
    
    # 測試組件導入
    test_results = {}
    
    try:
        from tools.enhanced_tool_registry import EnhancedToolRegistry
        registry = EnhancedToolRegistry({})
        test_results['tool_registry'] = True
        print("✅ Enhanced Tool Registry: 導入和初始化成功")
    except Exception as e:
        test_results['tool_registry'] = False
        print(f"⚠️ Enhanced Tool Registry: {e}")
    
    try:
        from core.aicore3 import AICore3
        aicore = AICore3()
        test_results['aicore'] = True
        print("✅ AICore 3.0: 導入和初始化成功")
    except Exception as e:
        test_results['aicore'] = False
        print(f"⚠️ AICore 3.0: {e}")
    
    # 生成測試報告
    report = {
        "test_timestamp": datetime.now().isoformat(),
        "platform": "macOS",
        "deployment_type": "ssh_remote",
        "test_results": test_results,
        "success_rate": f"{sum(test_results.values())}/{len(test_results)}"
    }
    
    with open('mac_remote_mcp_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📊 MCP組件測試: {sum(test_results.values())}/{len(test_results)} 成功")
    print("📋 測試報告: mac_remote_mcp_test_report.json")
    
    return sum(test_results.values()) > 0

if __name__ == "__main__":
    success = asyncio.run(configure_mcp_components())
    sys.exit(0 if success else 1)
EOF
    
    # 傳輸配置腳本到Mac
    transfer_file_to_mac "remote_mcp_config.py" "$PROJECT_DIR/remote_mcp_config.py" "傳輸MCP配置腳本"
    
    # 在Mac上執行配置
    execute_remote_command "
        cd \"$PROJECT_DIR\"
        python3 remote_mcp_config.py
        cd ..
    " "執行MCP組件配置"
}

# 創建啟動和管理腳本
create_management_scripts() {
    print_header "創建管理腳本"
    
    execute_remote_command "
        cd \"$PROJECT_DIR\"
        
        # 創建啟動腳本
        cat > 'start_powerautomation.sh' << 'SCRIPT_EOF'
#!/bin/bash
echo '🚀 啟動PowerAutomation Local MCP 3.0.0...'

# 檢查VS Code擴展
if code --list-extensions | grep -q 'powerautomation.powerautomation-local-mcp'; then
    echo '✅ PowerAutomation擴展已安裝'
else
    echo '❌ PowerAutomation擴展未安裝'
    exit 1
fi

# 啟動VS Code
echo '🚀 啟動VS Code...'
code .

echo '✅ PowerAutomation已啟動'
echo '💡 在VS Code中按 Cmd+Shift+P 搜索 PowerAutomation 使用功能'
SCRIPT_EOF
        
        chmod +x start_powerautomation.sh
        
        # 創建狀態檢查腳本
        cat > 'check_status.sh' << 'SCRIPT_EOF'
#!/bin/bash
echo '🔍 檢查PowerAutomation狀態...'

# 檢查VS Code擴展
if code --list-extensions | grep -q 'powerautomation.powerautomation-local-mcp'; then
    VERSION=\$(code --list-extensions --show-versions | grep 'powerautomation.powerautomation-local-mcp' | cut -d'@' -f2)
    echo \"✅ PowerAutomation擴展: v\$VERSION\"
else
    echo '❌ PowerAutomation擴展未安裝'
fi

# 檢查配置文件
if [[ -f 'mac_remote_mcp_config.json' ]]; then
    echo '✅ MCP配置文件: 存在'
else
    echo '❌ MCP配置文件: 不存在'
fi

# 檢查測試報告
if [[ -f 'mac_remote_mcp_test_report.json' ]]; then
    echo '✅ MCP測試報告: 存在'
    cat mac_remote_mcp_test_report.json | grep success_rate
else
    echo '❌ MCP測試報告: 不存在'
fi

echo '🏆 狀態檢查完成'
SCRIPT_EOF
        
        chmod +x check_status.sh
        
        cd ..
    " "創建管理腳本"
}

# 生成部署報告
generate_deployment_report() {
    print_header "生成部署報告"
    
    local report_file="ssh_remote_deployment_report_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" << EOF
{
  "deployment_info": {
    "timestamp": "$(date -Iseconds)",
    "deployment_id": "ssh_remote_$(date +%s)",
    "status": "completed",
    "deployment_type": "ssh_remote_deployment",
    "target_platform": "macOS"
  },
  "connection_info": {
    "mac_host": "$MAC_HOST",
    "mac_user": "$MAC_USER",
    "ssh_port": "$SSH_PORT",
    "auth_method": "$([ -n "$SSH_KEY" ] && echo "ssh_key" || echo "password")"
  },
  "deployment_results": {
    "ssh_connection": "success",
    "environment_check": "completed",
    "dependencies_installed": "completed",
    "project_deployed": "completed",
    "vscode_extension_installed": "completed",
    "mcp_components_configured": "completed",
    "management_scripts_created": "completed"
  },
  "powerautomation": {
    "project_dir": "$PROJECT_DIR",
    "extension_id": "$EXTENSION_ID",
    "extension_version": "3.0.0",
    "vsix_file": "$VSIX_FILE"
  },
  "next_steps": [
    "SSH到Mac執行: cd $PROJECT_DIR && ./start_powerautomation.sh",
    "或在Mac本地執行啟動腳本",
    "在VS Code中使用Cmd+Shift+P搜索PowerAutomation命令",
    "執行 ./check_status.sh 檢查狀態"
  ],
  "logs": {
    "deployment_log": "$REMOTE_DEPLOY_LOG",
    "deployment_report": "$report_file"
  }
}
EOF
    
    print_success "部署報告已生成: $report_file"
}

# 主執行流程
main() {
    print_header "開始SSH遠程部署"
    
    # 檢查必要工具
    if ! command -v sshpass &> /dev/null && [[ -z "$SSH_KEY" ]]; then
        print_warning "sshpass未安裝，將僅支持SSH金鑰認證"
        print_info "安裝sshpass: sudo apt-get install sshpass (Ubuntu) 或 brew install sshpass (Mac)"
    fi
    
    # 獲取連接資訊
    get_mac_connection_info
    
    # 測試SSH連接
    if ! test_ssh_connection; then
        exit 1
    fi
    
    # 執行部署步驟
    check_mac_environment
    install_dependencies_on_mac
    deploy_powerautomation_project
    install_vscode_extension_remote
    configure_mcp_components_remote
    create_management_scripts
    generate_deployment_report
    
    print_header "SSH遠程部署完成"
    print_success "🎉 PowerAutomation Local MCP 3.0.0 已成功部署到您的Mac!"
    print_info "📋 部署日誌: $REMOTE_DEPLOY_LOG"
    print_info "🔗 Mac連接: $MAC_USER@$MAC_HOST"
    
    print_header "使用方式"
    print_info "1. SSH到您的Mac: ssh $MAC_USER@$MAC_HOST"
    print_info "2. 進入項目目錄: cd $PROJECT_DIR"
    print_info "3. 啟動PowerAutomation: ./start_powerautomation.sh"
    print_info "4. 檢查狀態: ./check_status.sh"
    
    print_success "✅ SSH遠程部署成功完成!"
}

# 執行主函數
main "$@"

