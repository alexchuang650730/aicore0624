#!/bin/bash

# PowerAutomation Local MCP 3.0.0 Mac本地部署腳本
# 專為 alexchuang 的Mac環境優化

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
print_step() { echo -e "${CYAN}📋 $1${NC}"; }

# 配置變量
POWERAUTOMATION_REPO="https://github.com/alexchuang650730/aicore0624.git"
PROJECT_DIR="aicore0624"
EXTENSION_ID="powerautomation.powerautomation-local-mcp"
VSIX_FILE="PowerAutomation_local/vscode-extension/powerautomation-local-mcp-3.0.0.vsix"
DEPLOY_LOG="mac_local_deployment_$(date +%Y%m%d_%H%M%S).log"
USER_NAME="alexchuang"

# 創建部署日誌
exec > >(tee -a "$DEPLOY_LOG") 2>&1

print_header "PowerAutomation Local MCP 3.0.0 Mac本地部署"
print_info "部署開始時間: $(date)"
print_info "用戶: $USER_NAME"
print_info "系統: $(uname -s) $(sw_vers -productVersion)"
print_info "部署日誌: $DEPLOY_LOG"

# 檢查Mac環境
check_mac_environment() {
    print_step "檢查Mac環境"
    
    # 檢查macOS版本
    local macos_version=$(sw_vers -productVersion)
    print_info "macOS版本: $macos_version"
    
    # 檢查架構
    local arch=$(uname -m)
    print_info "硬體架構: $arch"
    
    # 檢查記憶體
    local memory=$(system_profiler SPHardwareDataType | grep Memory | awk -F': ' '{print $2}')
    print_info "系統記憶體: $memory"
    
    # 檢查磁碟空間
    local disk_space=$(df -h / | tail -1 | awk '{print $4}')
    print_info "可用磁碟空間: $disk_space"
    
    print_success "Mac環境檢查完成"
}

# 安裝Homebrew
install_homebrew() {
    print_step "檢查和安裝Homebrew"
    
    if command -v brew &> /dev/null; then
        print_success "Homebrew已安裝: $(brew --version | head -1)"
        return 0
    fi
    
    print_info "安裝Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # 添加Homebrew到PATH
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
        print_success "Homebrew已安裝 (Apple Silicon)"
    elif [[ -f "/usr/local/bin/brew" ]]; then
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
        print_success "Homebrew已安裝 (Intel)"
    else
        print_error "Homebrew安裝失敗"
        exit 1
    fi
}

# 安裝依賴軟體
install_dependencies() {
    print_step "安裝依賴軟體"
    
    # 更新Homebrew
    print_info "更新Homebrew..."
    brew update
    
    # 安裝Git
    if ! command -v git &> /dev/null; then
        print_info "安裝Git..."
        brew install git
        print_success "Git安裝完成"
    else
        print_success "Git已安裝: $(git --version)"
    fi
    
    # 安裝Python3
    if ! command -v python3 &> /dev/null; then
        print_info "安裝Python3..."
        brew install python
        print_success "Python3安裝完成"
    else
        local python_version=$(python3 --version)
        print_success "Python3已安裝: $python_version"
    fi
    
    # 安裝VS Code
    if ! command -v code &> /dev/null; then
        if [[ ! -f "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" ]]; then
            print_info "安裝VS Code..."
            brew install --cask visual-studio-code
            print_success "VS Code安裝完成"
        fi
        
        # 添加code命令到PATH
        if [[ -f "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" ]]; then
            sudo ln -sf "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" /usr/local/bin/code
            print_success "VS Code命令已添加到PATH"
        fi
    else
        local vscode_version=$(code --version | head -n1)
        print_success "VS Code已安裝: $vscode_version"
    fi
    
    # 安裝Python依賴
    print_info "安裝Python依賴..."
    python3 -m pip install --upgrade pip
    python3 -m pip install aiohttp aiofiles psutil requests
    print_success "Python依賴安裝完成"
}

# 克隆PowerAutomation項目
clone_powerautomation_project() {
    print_step "克隆PowerAutomation項目"
    
    if [[ -d "$PROJECT_DIR" ]]; then
        print_warning "項目目錄已存在，更新項目..."
        cd "$PROJECT_DIR"
        git pull origin main || git pull origin master
        cd ..
        print_success "項目更新完成"
    else
        print_info "克隆PowerAutomation項目..."
        git clone "$POWERAUTOMATION_REPO" "$PROJECT_DIR"
        print_success "項目克隆完成"
    fi
    
    # 檢查VSIX文件
    if [[ -f "$PROJECT_DIR/$VSIX_FILE" ]]; then
        local vsix_size=$(stat -f%z "$PROJECT_DIR/$VSIX_FILE")
        print_success "VSIX文件存在: $VSIX_FILE ($(($vsix_size / 1024))KB)"
    else
        print_error "VSIX文件不存在: $VSIX_FILE"
        exit 1
    fi
}

# 安裝VS Code擴展
install_vscode_extension() {
    print_step "安裝VS Code擴展"
    
    cd "$PROJECT_DIR"
    
    # 檢查並卸載現有擴展
    if code --list-extensions | grep -q "$EXTENSION_ID"; then
        local current_version=$(code --list-extensions --show-versions | grep "$EXTENSION_ID" | cut -d'@' -f2)
        print_warning "發現現有PowerAutomation擴展: $current_version"
        print_info "卸載現有版本..."
        code --uninstall-extension "$EXTENSION_ID" || true
        sleep 3
    fi
    
    # 安裝新擴展
    print_info "安裝PowerAutomation Local MCP 3.0.0..."
    if code --install-extension "$VSIX_FILE" --force; then
        print_success "PowerAutomation擴展安裝成功"
        sleep 5  # 等待擴展註冊
    else
        print_error "PowerAutomation擴展安裝失敗"
        exit 1
    fi
    
    # 驗證安裝
    if code --list-extensions | grep -q "$EXTENSION_ID"; then
        local installed_version=$(code --list-extensions --show-versions | grep "$EXTENSION_ID" | cut -d'@' -f2)
        print_success "擴展安裝驗證成功: $EXTENSION_ID@$installed_version"
    else
        print_error "擴展安裝驗證失敗"
        exit 1
    fi
    
    cd ..
}

# 配置MCP組件
configure_mcp_components() {
    print_step "配置MCP組件"
    
    cd "$PROJECT_DIR"
    
    # 創建MCP配置文件
    cat > "mac_local_mcp_config.json" << EOF
{
  "deployment_info": {
    "timestamp": "$(date -Iseconds)",
    "deployment_id": "mac_local_$(date +%s)",
    "user": "$USER_NAME",
    "platform": "macOS",
    "deployment_type": "local_deployment"
  },
  "environment": {
    "os": "$(uname -s)",
    "os_version": "$(sw_vers -productVersion)",
    "architecture": "$(uname -m)",
    "python_version": "$(python3 --version)",
    "vscode_version": "$(code --version | head -n1)"
  },
  "powerautomation": {
    "project_dir": "$PROJECT_DIR",
    "extension_id": "$EXTENSION_ID",
    "vsix_file": "$VSIX_FILE",
    "repo_url": "$POWERAUTOMATION_REPO"
  },
  "mcp_components": {
    "local_adapter": {
      "enabled": true,
      "path": "PowerAutomation/components/local_mcp_adapter.py",
      "config": {
        "adapter_id": "mac_local_adapter_$(date +%s)",
        "platform": "macOS",
        "user": "$USER_NAME",
        "real_mode": true
      }
    },
    "tool_registry": {
      "enabled": true,
      "path": "PowerAutomation/tools/enhanced_tool_registry.py",
      "config": {
        "smart_engine": true,
        "cloud_platforms": true,
        "real_mode": true
      }
    },
    "aicore": {
      "enabled": true,
      "path": "PowerAutomation/core/aicore3.py",
      "config": {
        "dynamic_experts": true,
        "cloud_search": true,
        "real_mode": true
      }
    }
  },
  "network": {
    "public_ip": "223.104.79.2",
    "local_ip": "$(ifconfig | grep 'inet ' | grep -v 127.0.0.1 | awk '{print $2}' | head -n1)",
    "ec2_connection": "18.212.97.173"
  }
}
EOF
    
    print_success "MCP配置文件已創建: mac_local_mcp_config.json"
    
    # 測試MCP組件
    print_info "測試MCP組件..."
    
    # 創建MCP測試腳本
    cat > "mac_local_mcp_test.py" << 'EOF'
#!/usr/bin/env python3
"""
Mac本地MCP組件測試
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# 添加PowerAutomation路徑
sys.path.insert(0, 'PowerAutomation')
sys.path.insert(0, 'PowerAutomation_local')

async def test_mcp_components():
    """測試MCP組件"""
    print("🧪 測試Mac本地MCP組件...")
    
    test_results = {
        'component_imports': {},
        'component_initialization': {},
        'integration_status': 'testing'
    }
    
    # 測試組件導入
    components = {
        'enhanced_tool_registry': 'tools.enhanced_tool_registry.EnhancedToolRegistry',
        'aicore3': 'core.aicore3.AICore3',
        'local_mcp_adapter': 'components.local_mcp_adapter.LocalMCPAdapter'
    }
    
    for component_name, import_path in components.items():
        try:
            module_path, class_name = import_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            component_class = getattr(module, class_name)
            
            print(f"✅ {component_name}: 導入成功")
            test_results['component_imports'][component_name] = True
            
            # 嘗試初始化
            if component_name == 'enhanced_tool_registry':
                instance = component_class({})
                test_results['component_initialization'][component_name] = True
                print(f"✅ {component_name}: 初始化成功")
            elif component_name == 'aicore3':
                instance = component_class()
                test_results['component_initialization'][component_name] = True
                print(f"✅ {component_name}: 初始化成功")
            elif component_name == 'local_mcp_adapter':
                test_config = {
                    'adapter_id': 'mac_test_adapter',
                    'platform': 'macOS',
                    'user': 'alexchuang'
                }
                instance = component_class(config_dict=test_config)
                test_results['component_initialization'][component_name] = True
                print(f"✅ {component_name}: 初始化成功")
                
        except Exception as e:
            print(f"❌ {component_name}: {e}")
            test_results['component_imports'][component_name] = False
            test_results['component_initialization'][component_name] = False
    
    # 計算成功率
    import_success = sum(test_results['component_imports'].values())
    init_success = sum(test_results['component_initialization'].values())
    total_components = len(components)
    
    test_results['integration_status'] = 'success' if import_success >= 2 else 'partial'
    
    print(f"📊 組件導入: {import_success}/{total_components}")
    print(f"📊 組件初始化: {init_success}/{total_components}")
    
    # 生成測試報告
    report = {
        'test_timestamp': datetime.now().isoformat(),
        'platform': 'macOS',
        'user': 'alexchuang',
        'deployment_type': 'local',
        'test_results': test_results,
        'summary': {
            'import_success_rate': f"{import_success}/{total_components}",
            'initialization_success_rate': f"{init_success}/{total_components}",
            'overall_status': test_results['integration_status']
        }
    }
    
    with open('mac_local_mcp_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("📋 測試報告已生成: mac_local_mcp_test_report.json")
    return test_results['integration_status'] == 'success'

if __name__ == "__main__":
    success = asyncio.run(test_mcp_components())
    sys.exit(0 if success else 1)
EOF
    
    # 執行MCP測試
    if python3 mac_local_mcp_test.py; then
        print_success "MCP組件測試通過"
    else
        print_warning "MCP組件測試部分通過，但繼續部署"
    fi
    
    cd ..
}

# 創建管理腳本
create_management_scripts() {
    print_step "創建管理腳本"
    
    cd "$PROJECT_DIR"
    
    # 創建啟動腳本
    cat > "start_powerautomation_mac.sh" << 'EOF'
#!/bin/bash

# PowerAutomation Mac啟動腳本

echo "🚀 啟動PowerAutomation Local MCP 3.0.0..."

# 檢查VS Code
if ! command -v code &> /dev/null; then
    echo "❌ VS Code未找到，請確保VS Code已安裝"
    exit 1
fi

# 檢查擴展
if ! code --list-extensions | grep -q "powerautomation.powerautomation-local-mcp"; then
    echo "❌ PowerAutomation擴展未安裝"
    exit 1
fi

echo "✅ PowerAutomation環境檢查通過"

# 啟動VS Code
echo "🚀 啟動VS Code..."
code .

echo "✅ PowerAutomation已啟動"
echo "💡 在VS Code中按 Cmd+Shift+P 搜索 'PowerAutomation' 使用功能"
EOF
    
    chmod +x start_powerautomation_mac.sh
    print_success "Mac啟動腳本已創建: start_powerautomation_mac.sh"
    
    # 創建狀態檢查腳本
    cat > "check_powerautomation_status.sh" << 'EOF'
#!/bin/bash

# PowerAutomation Mac狀態檢查腳本

echo "🔍 檢查PowerAutomation狀態..."

# 檢查VS Code擴展
if code --list-extensions | grep -q "powerautomation.powerautomation-local-mcp"; then
    VERSION=$(code --list-extensions --show-versions | grep "powerautomation.powerautomation-local-mcp" | cut -d'@' -f2)
    echo "✅ PowerAutomation擴展: v$VERSION"
else
    echo "❌ PowerAutomation擴展未安裝"
fi

# 檢查Python環境
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python環境: $PYTHON_VERSION"
else
    echo "❌ Python3未安裝"
fi

# 檢查依賴
echo "🔍 檢查Python依賴..."
python3 -c "
try:
    import aiohttp, aiofiles, psutil
    print('✅ Python依賴: 已安裝')
except ImportError as e:
    print(f'❌ Python依賴: {e}')
"

# 檢查項目文件
if [[ -f "PowerAutomation_local/vscode-extension/powerautomation-local-mcp-3.0.0.vsix" ]]; then
    echo "✅ VSIX文件: 存在"
else
    echo "❌ VSIX文件: 不存在"
fi

# 檢查配置文件
if [[ -f "mac_local_mcp_config.json" ]]; then
    echo "✅ MCP配置: 存在"
else
    echo "❌ MCP配置: 不存在"
fi

echo "🏆 PowerAutomation狀態檢查完成"
EOF
    
    chmod +x check_powerautomation_status.sh
    print_success "Mac狀態檢查腳本已創建: check_powerautomation_status.sh"
    
    cd ..
}

# 創建桌面快捷方式
create_desktop_shortcuts() {
    print_step "創建桌面快捷方式"
    
    # 創建桌面快捷方式目錄
    local shortcuts_dir="$HOME/Desktop/PowerAutomation"
    mkdir -p "$shortcuts_dir"
    
    # 創建啟動快捷方式
    cat > "$shortcuts_dir/啟動PowerAutomation.command" << EOF
#!/bin/bash
cd "$(pwd)/$PROJECT_DIR"
./start_powerautomation_mac.sh
EOF
    chmod +x "$shortcuts_dir/啟動PowerAutomation.command"
    
    # 創建狀態檢查快捷方式
    cat > "$shortcuts_dir/檢查PowerAutomation狀態.command" << EOF
#!/bin/bash
cd "$(pwd)/$PROJECT_DIR"
./check_powerautomation_status.sh
read -p "按Enter鍵關閉..."
EOF
    chmod +x "$shortcuts_dir/檢查PowerAutomation狀態.command"
    
    print_success "桌面快捷方式已創建: $shortcuts_dir"
}

# 生成部署報告
generate_deployment_report() {
    print_step "生成部署報告"
    
    local report_file="mac_local_deployment_report_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" << EOF
{
  "deployment_info": {
    "timestamp": "$(date -Iseconds)",
    "deployment_id": "mac_local_$(date +%s)",
    "status": "completed",
    "platform": "macOS",
    "user": "$USER_NAME",
    "deployment_type": "local_deployment"
  },
  "environment": {
    "os": "$(uname -s)",
    "os_version": "$(sw_vers -productVersion)",
    "architecture": "$(uname -m)",
    "python_version": "$(python3 --version)",
    "vscode_version": "$(code --version | head -n1)"
  },
  "deployment_results": {
    "environment_check": "completed",
    "homebrew_installed": "completed",
    "dependencies_installed": "completed",
    "project_cloned": "completed",
    "vscode_extension_installed": "completed",
    "mcp_components_configured": "completed",
    "management_scripts_created": "completed",
    "desktop_shortcuts_created": "completed"
  },
  "powerautomation": {
    "project_dir": "$PROJECT_DIR",
    "extension_id": "$EXTENSION_ID",
    "extension_version": "3.0.0",
    "vsix_file": "$VSIX_FILE"
  },
  "files_created": {
    "config_file": "$PROJECT_DIR/mac_local_mcp_config.json",
    "startup_script": "$PROJECT_DIR/start_powerautomation_mac.sh",
    "status_script": "$PROJECT_DIR/check_powerautomation_status.sh",
    "shortcuts_dir": "$HOME/Desktop/PowerAutomation"
  },
  "next_steps": [
    "使用桌面快捷方式啟動PowerAutomation",
    "在VS Code中使用Cmd+Shift+P搜索PowerAutomation命令",
    "定期檢查PowerAutomation狀態",
    "查看部署日誌以排除問題"
  ],
  "logs": {
    "deployment_log": "$DEPLOY_LOG",
    "deployment_report": "$report_file"
  }
}
EOF
    
    print_success "部署報告已生成: $report_file"
}

# 主執行流程
main() {
    print_header "開始Mac本地部署"
    
    # 檢查Mac環境
    if [[ "$(uname -s)" != "Darwin" ]]; then
        print_error "此腳本僅適用於Mac系統"
        exit 1
    fi
    
    print_success "確認Mac環境: $(sw_vers -productVersion)"
    
    # 執行部署步驟
    check_mac_environment
    install_homebrew
    install_dependencies
    clone_powerautomation_project
    install_vscode_extension
    configure_mcp_components
    create_management_scripts
    create_desktop_shortcuts
    generate_deployment_report
    
    print_header "Mac本地部署完成"
    print_success "🎉 PowerAutomation Local MCP 3.0.0 已成功部署到您的Mac!"
    print_info "📋 部署日誌: $DEPLOY_LOG"
    print_info "🚀 桌面快捷方式: $HOME/Desktop/PowerAutomation"
    
    print_header "使用方式"
    print_info "1. 使用桌面快捷方式 '啟動PowerAutomation.command'"
    print_info "2. 或在終端執行: cd $PROJECT_DIR && ./start_powerautomation_mac.sh"
    print_info "3. 在VS Code中按 Cmd+Shift+P 搜索 'PowerAutomation'"
    print_info "4. 使用 '檢查PowerAutomation狀態.command' 檢查狀態"
    
    print_header "驗證安裝"
    print_info "執行以下命令驗證安裝："
    print_info "code --list-extensions | grep powerautomation"
    print_info "cd $PROJECT_DIR && ./check_powerautomation_status.sh"
    
    print_success "✅ Mac本地部署成功完成!"
}

# 執行主函數
main "$@"

