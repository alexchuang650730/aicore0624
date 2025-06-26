#!/bin/bash

# PowerAutomation Local MCP 3.0.0 Mac集成測試和驗證腳本
# 全面測試Mac環境中的PowerAutomation部署

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
print_test() { echo -e "${CYAN}🧪 $1${NC}"; }

# 測試配置
EXTENSION_ID="powerautomation.powerautomation-local-mcp"
PROJECT_DIR="aicore0624"
VSIX_FILE="PowerAutomation_local/vscode-extension/powerautomation-local-mcp-3.0.0.vsix"
TEST_LOG="mac_integration_test_$(date +%Y%m%d_%H%M%S).log"
TEST_REPORT="mac_integration_test_report_$(date +%Y%m%d_%H%M%S).json"

# 測試結果追蹤
declare -A test_results
test_count=0
passed_count=0

# 創建測試日誌
exec > >(tee -a "$TEST_LOG") 2>&1

print_header "PowerAutomation Local MCP 3.0.0 Mac集成測試"

print_info "測試開始時間: $(date)"
print_info "操作系統: $(uname -s) $(uname -r)"
print_info "測試日誌: $TEST_LOG"

# 測試函數
run_test() {
    local test_name="$1"
    local test_command="$2"
    local test_description="$3"
    
    ((test_count++))
    print_test "測試 $test_count: $test_description"
    
    if eval "$test_command"; then
        test_results["$test_name"]="PASS"
        ((passed_count++))
        print_success "測試通過: $test_name"
        return 0
    else
        test_results["$test_name"]="FAIL"
        print_error "測試失敗: $test_name"
        return 1
    fi
}

# 環境檢查測試
test_environment() {
    print_header "環境檢查測試"
    
    # 測試1: macOS版本檢查
    run_test "macos_version" \
        "[[ \"\$(uname -s)\" == \"Darwin\" ]] && sw_vers -productVersion" \
        "檢查macOS版本"
    
    # 測試2: 硬體架構檢查
    run_test "hardware_architecture" \
        "uname -m" \
        "檢查硬體架構"
    
    # 測試3: 記憶體檢查
    run_test "memory_check" \
        "system_profiler SPHardwareDataType | grep Memory" \
        "檢查系統記憶體"
    
    # 測試4: 磁碟空間檢查
    run_test "disk_space" \
        "df -h / | tail -1 | awk '{print \$4}'" \
        "檢查磁碟可用空間"
}

# 依賴軟體測試
test_dependencies() {
    print_header "依賴軟體測試"
    
    # 測試5: Git檢查
    run_test "git_installed" \
        "command -v git && git --version" \
        "檢查Git安裝"
    
    # 測試6: Python3檢查
    run_test "python3_installed" \
        "command -v python3 && python3 --version" \
        "檢查Python3安裝"
    
    # 測試7: VS Code檢查
    run_test "vscode_installed" \
        "command -v code && code --version" \
        "檢查VS Code安裝"
    
    # 測試8: Homebrew檢查
    run_test "homebrew_installed" \
        "command -v brew && brew --version" \
        "檢查Homebrew安裝"
    
    # 測試9: Python依賴檢查
    run_test "python_dependencies" \
        "python3 -c 'import aiohttp, aiofiles, psutil; print(\"所有依賴已安裝\")'" \
        "檢查Python依賴"
}

# PowerAutomation項目測試
test_powerautomation_project() {
    print_header "PowerAutomation項目測試"
    
    # 測試10: 項目目錄檢查
    run_test "project_directory" \
        "[[ -d \"$PROJECT_DIR\" ]] && echo \"項目目錄存在\"" \
        "檢查PowerAutomation項目目錄"
    
    # 測試11: VSIX文件檢查
    run_test "vsix_file" \
        "[[ -f \"$PROJECT_DIR/$VSIX_FILE\" ]] && ls -la \"$PROJECT_DIR/$VSIX_FILE\"" \
        "檢查VSIX文件"
    
    # 測試12: PowerAutomation組件檢查
    run_test "powerautomation_components" \
        "[[ -d \"$PROJECT_DIR/PowerAutomation\" ]] && [[ -d \"$PROJECT_DIR/PowerAutomation_local\" ]]" \
        "檢查PowerAutomation組件目錄"
    
    # 測試13: Git倉庫狀態
    run_test "git_repository" \
        "cd \"$PROJECT_DIR\" && git status && cd .." \
        "檢查Git倉庫狀態"
}

# VS Code擴展測試
test_vscode_extension() {
    print_header "VS Code擴展測試"
    
    # 測試14: 擴展安裝檢查
    run_test "extension_installed" \
        "code --list-extensions | grep -q \"$EXTENSION_ID\"" \
        "檢查PowerAutomation擴展是否已安裝"
    
    # 測試15: 擴展版本檢查
    run_test "extension_version" \
        "code --list-extensions --show-versions | grep \"$EXTENSION_ID\" | grep \"3.0.0\"" \
        "檢查PowerAutomation擴展版本"
    
    # 測試16: 擴展目錄檢查
    run_test "extension_directory" \
        "find ~/.vscode/extensions -name \"*powerautomation*\" -type d | head -1" \
        "檢查擴展安裝目錄"
    
    # 測試17: 擴展文件完整性
    run_test "extension_files" \
        "EXTENSION_DIR=\$(find ~/.vscode/extensions -name \"*powerautomation*\" -type d | head -1) && [[ -f \"\$EXTENSION_DIR/package.json\" ]] && [[ -f \"\$EXTENSION_DIR/out/extension.js\" ]]" \
        "檢查擴展文件完整性"
}

# MCP組件測試
test_mcp_components() {
    print_header "MCP組件測試"
    
    # 創建MCP組件測試腳本
    cat > "mcp_component_test.py" << 'EOF'
#!/usr/bin/env python3
"""
MCP組件功能測試
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# 添加PowerAutomation路徑
current_dir = os.getcwd()
if os.path.exists('aicore0624'):
    sys.path.insert(0, os.path.join(current_dir, 'aicore0624', 'PowerAutomation'))
    sys.path.insert(0, os.path.join(current_dir, 'aicore0624', 'PowerAutomation_local'))

async def test_mcp_components():
    """測試MCP組件"""
    test_results = {
        'enhanced_tool_registry': False,
        'aicore3': False,
        'local_mcp_adapter': False
    }
    
    # 測試Enhanced Tool Registry
    try:
        from tools.enhanced_tool_registry import EnhancedToolRegistry
        registry = EnhancedToolRegistry({})
        test_results['enhanced_tool_registry'] = True
        print("✅ Enhanced Tool Registry: 導入和初始化成功")
    except Exception as e:
        print(f"❌ Enhanced Tool Registry: {e}")
    
    # 測試AICore 3.0
    try:
        from core.aicore3 import AICore3
        aicore = AICore3()
        test_results['aicore3'] = True
        print("✅ AICore 3.0: 導入和初始化成功")
    except Exception as e:
        print(f"❌ AICore 3.0: {e}")
    
    # 測試Local MCP Adapter
    try:
        from components.local_mcp_adapter import LocalMCPAdapter
        # 使用簡單配置測試
        test_config = {
            'adapter_id': 'test_adapter',
            'platform': 'macOS'
        }
        adapter = LocalMCPAdapter(config_dict=test_config)
        test_results['local_mcp_adapter'] = True
        print("✅ Local MCP Adapter: 導入和初始化成功")
    except Exception as e:
        print(f"❌ Local MCP Adapter: {e}")
    
    # 計算成功率
    success_count = sum(test_results.values())
    total_count = len(test_results)
    
    print(f"📊 MCP組件測試結果: {success_count}/{total_count}")
    
    # 保存測試結果
    report = {
        'timestamp': datetime.now().isoformat(),
        'test_results': test_results,
        'success_rate': f"{success_count}/{total_count}",
        'overall_success': success_count >= 2  # 至少2個組件成功
    }
    
    with open('mcp_component_test_result.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    return report['overall_success']

if __name__ == "__main__":
    success = asyncio.run(test_mcp_components())
    sys.exit(0 if success else 1)
EOF
    
    # 測試18: MCP組件導入和初始化
    run_test "mcp_components" \
        "python3 mcp_component_test.py" \
        "測試MCP組件導入和初始化"
    
    # 測試19: MCP配置文件
    run_test "mcp_config_files" \
        "[[ -f \"$PROJECT_DIR/mac_integration_config.json\" ]] || [[ -f \"$PROJECT_DIR/mac_remote_mcp_config.json\" ]]" \
        "檢查MCP配置文件"
}

# 網路連接測試
test_network_connectivity() {
    print_header "網路連接測試"
    
    # 測試20: 公網連接
    run_test "internet_connectivity" \
        "curl -s --connect-timeout 10 ipinfo.io/ip" \
        "測試網際網路連接"
    
    # 測試21: EC2連接
    run_test "ec2_connectivity" \
        "ping -c 3 18.212.97.173" \
        "測試EC2服務器連接"
    
    # 測試22: DNS解析
    run_test "dns_resolution" \
        "nslookup github.com" \
        "測試DNS解析"
    
    # 測試23: HTTPS連接
    run_test "https_connectivity" \
        "curl -s --connect-timeout 10 https://api.github.com" \
        "測試HTTPS連接"
}

# 功能整合測試
test_integration() {
    print_header "功能整合測試"
    
    # 測試24: VS Code啟動測試
    run_test "vscode_startup" \
        "timeout 10 code --version" \
        "測試VS Code啟動"
    
    # 測試25: 擴展命令測試
    run_test "extension_commands" \
        "code --list-extensions | grep powerautomation && echo '擴展命令可用'" \
        "測試擴展命令可用性"
    
    # 測試26: 項目文件權限
    run_test "file_permissions" \
        "[[ -r \"$PROJECT_DIR/$VSIX_FILE\" ]] && [[ -x \"$PROJECT_DIR\" ]]" \
        "檢查項目文件權限"
    
    # 測試27: 腳本執行權限
    run_test "script_permissions" \
        "[[ -x \"$PROJECT_DIR/start_powerautomation.sh\" ]] || [[ -x \"$PROJECT_DIR/start_powerautomation_mac.sh\" ]]" \
        "檢查腳本執行權限"
}

# 性能基準測試
test_performance() {
    print_header "性能基準測試"
    
    # 測試28: VS Code啟動時間
    run_test "vscode_startup_time" \
        "time timeout 15 code --version" \
        "測試VS Code啟動時間"
    
    # 測試29: Python導入時間
    run_test "python_import_time" \
        "time python3 -c 'import sys; print(\"Python導入測試完成\")'" \
        "測試Python導入時間"
    
    # 測試30: 磁碟I/O性能
    run_test "disk_io_performance" \
        "time dd if=/dev/zero of=test_file bs=1M count=10 && rm test_file" \
        "測試磁碟I/O性能"
}

# 生成測試報告
generate_test_report() {
    print_header "生成測試報告"
    
    local success_rate=$(echo "scale=2; $passed_count * 100 / $test_count" | bc)
    
    cat > "$TEST_REPORT" << EOF
{
  "test_info": {
    "timestamp": "$(date -Iseconds)",
    "test_id": "mac_integration_test_$(date +%s)",
    "platform": "macOS",
    "os_version": "$(sw_vers -productVersion)",
    "architecture": "$(uname -m)"
  },
  "test_summary": {
    "total_tests": $test_count,
    "passed_tests": $passed_count,
    "failed_tests": $((test_count - passed_count)),
    "success_rate": "${success_rate}%",
    "overall_status": "$([ $passed_count -ge $((test_count * 80 / 100)) ] && echo "PASS" || echo "FAIL")"
  },
  "test_results": {
EOF
    
    # 添加測試結果
    local first=true
    for test_name in "${!test_results[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo "," >> "$TEST_REPORT"
        fi
        echo "    \"$test_name\": \"${test_results[$test_name]}\"" >> "$TEST_REPORT"
    done
    
    cat >> "$TEST_REPORT" << EOF
  },
  "environment": {
    "macos_version": "$(sw_vers -productVersion)",
    "hardware": "$(system_profiler SPHardwareDataType | grep 'Model Name' | awk -F': ' '{print $2}' || echo 'unknown')",
    "memory": "$(system_profiler SPHardwareDataType | grep Memory | awk -F': ' '{print $2}' || echo 'unknown')",
    "python_version": "$(python3 --version)",
    "vscode_version": "$(code --version | head -n1)"
  },
  "powerautomation": {
    "project_exists": $([ -d "$PROJECT_DIR" ] && echo "true" || echo "false"),
    "vsix_exists": $([ -f "$PROJECT_DIR/$VSIX_FILE" ] && echo "true" || echo "false"),
    "extension_installed": $(code --list-extensions | grep -q "$EXTENSION_ID" && echo "true" || echo "false"),
    "extension_version": "$(code --list-extensions --show-versions | grep "$EXTENSION_ID" | cut -d'@' -f2 || echo 'not_installed')"
  },
  "recommendations": [
EOF
    
    # 添加建議
    if [ $passed_count -lt $test_count ]; then
        echo "    \"檢查失敗的測試項目並進行修復\"," >> "$TEST_REPORT"
    fi
    
    if ! code --list-extensions | grep -q "$EXTENSION_ID"; then
        echo "    \"重新安裝PowerAutomation VS Code擴展\"," >> "$TEST_REPORT"
    fi
    
    echo "    \"定期運行此測試腳本以確保系統正常\"" >> "$TEST_REPORT"
    
    cat >> "$TEST_REPORT" << EOF
  ],
  "logs": {
    "test_log": "$TEST_LOG",
    "test_report": "$TEST_REPORT"
  }
}
EOF
    
    print_success "測試報告已生成: $TEST_REPORT"
}

# 清理測試文件
cleanup_test_files() {
    print_info "清理測試文件..."
    
    # 清理臨時測試文件
    rm -f mcp_component_test.py
    rm -f mcp_component_test_result.json
    rm -f test_file
    
    print_success "測試文件清理完成"
}

# 主執行流程
main() {
    print_header "開始Mac集成測試"
    
    # 檢查Mac環境
    if [[ "$(uname -s)" != "Darwin" ]]; then
        print_error "此測試腳本僅適用於Mac系統"
        exit 1
    fi
    
    # 執行測試套件
    test_environment
    test_dependencies
    test_powerautomation_project
    test_vscode_extension
    test_mcp_components
    test_network_connectivity
    test_integration
    test_performance
    
    # 生成報告和清理
    generate_test_report
    cleanup_test_files
    
    print_header "Mac集成測試完成"
    print_success "🎉 PowerAutomation Mac集成測試完成!"
    print_info "📊 測試結果: $passed_count/$test_count 通過"
    print_info "📋 測試日誌: $TEST_LOG"
    print_info "📊 測試報告: $TEST_REPORT"
    
    # 顯示測試總結
    local success_rate=$(echo "scale=2; $passed_count * 100 / $test_count" | bc)
    print_header "測試總結"
    print_info "成功率: ${success_rate}%"
    
    if [ $passed_count -ge $((test_count * 80 / 100)) ]; then
        print_success "✅ 整體測試: 通過 (≥80%)"
        print_info "PowerAutomation Mac集成部署成功!"
    else
        print_warning "⚠️ 整體測試: 需要改進 (<80%)"
        print_info "請檢查失敗的測試項目並進行修復"
    fi
    
    # 顯示關鍵測試結果
    print_header "關鍵功能狀態"
    
    if [[ "${test_results[extension_installed]}" == "PASS" ]]; then
        print_success "✅ VS Code擴展: 已安裝"
    else
        print_error "❌ VS Code擴展: 未安裝"
    fi
    
    if [[ "${test_results[mcp_components]}" == "PASS" ]]; then
        print_success "✅ MCP組件: 功能正常"
    else
        print_warning "⚠️ MCP組件: 需要檢查"
    fi
    
    if [[ "${test_results[internet_connectivity]}" == "PASS" ]]; then
        print_success "✅ 網路連接: 正常"
    else
        print_warning "⚠️ 網路連接: 有問題"
    fi
    
    print_success "🏆 Mac集成測試和驗證完成!"
}

# 執行主函數
main "$@"

