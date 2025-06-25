#!/bin/bash

# Mac公網IP檢測和PowerAutomation配置腳本
# 檢測Mac公網IP並配置到PowerAutomation MCP服務中

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

print_header "Mac公網IP檢測和PowerAutomation配置"

# 檢測公網IP的多種方法
detect_public_ip() {
    print_info "檢測Mac公網IP地址..."
    
    local public_ip=""
    local detection_method=""
    
    # 方法1: 使用curl檢測
    print_info "嘗試方法1: curl ipinfo.io"
    if command -v curl &> /dev/null; then
        public_ip=$(curl -s --connect-timeout 10 ipinfo.io/ip 2>/dev/null || echo "")
        if [[ -n "$public_ip" && "$public_ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            detection_method="ipinfo.io"
            print_success "方法1成功: $public_ip"
        else
            print_warning "方法1失敗"
        fi
    fi
    
    # 方法2: 使用ifconfig.me
    if [[ -z "$public_ip" ]]; then
        print_info "嘗試方法2: curl ifconfig.me"
        public_ip=$(curl -s --connect-timeout 10 ifconfig.me 2>/dev/null || echo "")
        if [[ -n "$public_ip" && "$public_ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            detection_method="ifconfig.me"
            print_success "方法2成功: $public_ip"
        else
            print_warning "方法2失敗"
        fi
    fi
    
    # 方法3: 使用httpbin.org
    if [[ -z "$public_ip" ]]; then
        print_info "嘗試方法3: curl httpbin.org/ip"
        local response=$(curl -s --connect-timeout 10 httpbin.org/ip 2>/dev/null || echo "")
        if [[ -n "$response" ]]; then
            public_ip=$(echo "$response" | grep -o '"origin": "[^"]*"' | cut -d'"' -f4 | cut -d',' -f1)
            if [[ -n "$public_ip" && "$public_ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
                detection_method="httpbin.org"
                print_success "方法3成功: $public_ip"
            else
                print_warning "方法3失敗"
            fi
        else
            print_warning "方法3失敗"
        fi
    fi
    
    # 方法4: 使用icanhazip.com
    if [[ -z "$public_ip" ]]; then
        print_info "嘗試方法4: curl icanhazip.com"
        public_ip=$(curl -s --connect-timeout 10 icanhazip.com 2>/dev/null | tr -d '\n' || echo "")
        if [[ -n "$public_ip" && "$public_ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            detection_method="icanhazip.com"
            print_success "方法4成功: $public_ip"
        else
            print_warning "方法4失敗"
        fi
    fi
    
    if [[ -n "$public_ip" ]]; then
        echo "$public_ip|$detection_method"
    else
        echo "|failed"
    fi
}

# 檢測本地IP
detect_local_ip() {
    print_info "檢測Mac本地IP地址..."
    
    # 獲取主要網路介面的IP
    local local_ip=""
    
    # 方法1: 使用route命令找到預設路由的介面
    if command -v route &> /dev/null; then
        local default_interface=$(route get default 2>/dev/null | grep interface | awk '{print $2}')
        if [[ -n "$default_interface" ]]; then
            local_ip=$(ifconfig "$default_interface" 2>/dev/null | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | head -n1)
        fi
    fi
    
    # 方法2: 使用networksetup命令
    if [[ -z "$local_ip" ]] && command -v networksetup &> /dev/null; then
        local services=$(networksetup -listallnetworkservices | grep -v "An asterisk")
        while IFS= read -r service; do
            if [[ -n "$service" ]]; then
                local ip=$(networksetup -getinfo "$service" 2>/dev/null | grep "IP address" | awk '{print $3}')
                if [[ -n "$ip" && "$ip" != "none" && "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
                    local_ip="$ip"
                    break
                fi
            fi
        done <<< "$services"
    fi
    
    # 方法3: 使用ifconfig查找活躍介面
    if [[ -z "$local_ip" ]]; then
        local_ip=$(ifconfig | grep 'inet ' | grep -v '127.0.0.1' | grep -v '169.254' | awk '{print $2}' | head -n1)
    fi
    
    if [[ -n "$local_ip" ]]; then
        print_success "本地IP: $local_ip"
        echo "$local_ip"
    else
        print_warning "無法檢測本地IP"
        echo ""
    fi
}

# 檢測網路資訊
detect_network_info() {
    print_info "檢測網路資訊..."
    
    local network_info=""
    
    # 檢測ISP資訊
    if command -v curl &> /dev/null; then
        local isp_info=$(curl -s --connect-timeout 10 "ipinfo.io/json" 2>/dev/null || echo "")
        if [[ -n "$isp_info" ]]; then
            local city=$(echo "$isp_info" | grep '"city"' | cut -d'"' -f4)
            local region=$(echo "$isp_info" | grep '"region"' | cut -d'"' -f4)
            local country=$(echo "$isp_info" | grep '"country"' | cut -d'"' -f4)
            local org=$(echo "$isp_info" | grep '"org"' | cut -d'"' -f4)
            
            if [[ -n "$city" || -n "$region" || -n "$country" || -n "$org" ]]; then
                network_info="$city, $region, $country - $org"
                print_success "網路資訊: $network_info"
            fi
        fi
    fi
    
    echo "$network_info"
}

# 創建PowerAutomation網路配置
create_powerautomation_network_config() {
    local public_ip="$1"
    local local_ip="$2"
    local detection_method="$3"
    local network_info="$4"
    
    print_info "創建PowerAutomation網路配置..."
    
    local config_file="powerautomation_mac_network_config.json"
    
    cat > "$config_file" << EOF
{
  "network_config": {
    "timestamp": "$(date -Iseconds)",
    "config_id": "mac_network_$(date +%s)",
    "platform": "macOS",
    "hostname": "$(hostname)"
  },
  "ip_addresses": {
    "public_ip": "$public_ip",
    "local_ip": "$local_ip",
    "detection_method": "$detection_method",
    "detection_timestamp": "$(date -Iseconds)"
  },
  "network_info": {
    "location_and_isp": "$network_info",
    "mac_address": "$(ifconfig en0 2>/dev/null | grep ether | awk '{print $2}' || echo 'unknown')",
    "network_interface": "$(route get default 2>/dev/null | grep interface | awk '{print $2}' || echo 'unknown')"
  },
  "powerautomation_config": {
    "mcp_service_endpoint": "http://$local_ip:8080",
    "cloud_connection": {
      "ec2_endpoint": "18.212.97.173",
      "local_endpoint": "$public_ip",
      "connection_type": "bidirectional"
    },
    "security": {
      "allowed_ips": ["$public_ip", "$local_ip", "18.212.97.173"],
      "firewall_rules": {
        "inbound": ["8080", "8443"],
        "outbound": ["80", "443", "22"]
      }
    }
  },
  "mac_specific": {
    "os_version": "$(sw_vers -productVersion)",
    "architecture": "$(uname -m)",
    "system_info": "$(system_profiler SPHardwareDataType | grep 'Model Name' | awk -F': ' '{print $2}' || echo 'unknown')"
  }
}
EOF
    
    print_success "網路配置已創建: $config_file"
    echo "$config_file"
}

# 更新PowerAutomation MCP配置
update_mcp_config_with_network() {
    local public_ip="$1"
    local local_ip="$2"
    local config_file="$3"
    
    print_info "更新PowerAutomation MCP配置..."
    
    # 檢查是否存在aicore0624目錄
    if [[ -d "aicore0624" ]]; then
        cd aicore0624
        
        # 更新MCP配置
        if [[ -f "mac_integration_config.json" ]]; then
            # 備份原配置
            cp mac_integration_config.json mac_integration_config.json.backup
            
            # 使用Python更新配置
            python3 << EOF
import json

# 讀取現有配置
with open('mac_integration_config.json', 'r') as f:
    config = json.load(f)

# 添加網路配置
config['network'] = {
    'public_ip': '$public_ip',
    'local_ip': '$local_ip',
    'mcp_service_endpoint': 'http://$local_ip:8080',
    'cloud_connection': {
        'ec2_endpoint': '18.212.97.173',
        'local_endpoint': '$public_ip'
    }
}

# 更新MCP組件配置
for component in config.get('mcp_components', {}).values():
    if 'config' in component:
        component['config']['network'] = {
            'public_ip': '$public_ip',
            'local_ip': '$local_ip'
        }

# 保存更新的配置
with open('mac_integration_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("✅ MCP配置已更新")
EOF
            
            print_success "MCP配置已更新: aicore0624/mac_integration_config.json"
        else
            print_warning "MCP配置文件不存在，將在部署時創建"
        fi
        
        cd ..
    else
        print_warning "aicore0624目錄不存在，請先運行Mac集成部署腳本"
    fi
}

# 創建網路監控腳本
create_network_monitor() {
    local public_ip="$1"
    local local_ip="$2"
    
    print_info "創建網路監控腳本..."
    
    cat > "monitor_mac_network.sh" << EOF
#!/bin/bash

# Mac網路監控腳本 - 監控PowerAutomation網路連接

echo "🔍 監控Mac網路狀態..."

# 檢查公網IP變化
current_public_ip=\$(curl -s --connect-timeout 5 ipinfo.io/ip 2>/dev/null || echo "unknown")
echo "當前公網IP: \$current_public_ip"
echo "配置公網IP: $public_ip"

if [[ "\$current_public_ip" != "$public_ip" && "\$current_public_ip" != "unknown" ]]; then
    echo "⚠️ 公網IP已變化，需要更新PowerAutomation配置"
    echo "新IP: \$current_public_ip"
    echo "舊IP: $public_ip"
fi

# 檢查本地IP
current_local_ip=\$(ifconfig | grep 'inet ' | grep -v '127.0.0.1' | grep -v '169.254' | awk '{print \$2}' | head -n1)
echo "當前本地IP: \$current_local_ip"
echo "配置本地IP: $local_ip"

if [[ "\$current_local_ip" != "$local_ip" ]]; then
    echo "⚠️ 本地IP已變化，需要更新PowerAutomation配置"
fi

# 檢查EC2連接
echo "🔗 檢查EC2連接..."
if ping -c 1 18.212.97.173 &> /dev/null; then
    echo "✅ EC2連接正常"
else
    echo "❌ EC2連接失敗"
fi

# 檢查PowerAutomation服務
if [[ -d "aicore0624" ]]; then
    cd aicore0624
    if [[ -f "check_powerautomation_status.sh" ]]; then
        echo "🔍 檢查PowerAutomation狀態..."
        ./check_powerautomation_status.sh
    fi
    cd ..
fi

echo "🏆 網路監控完成"
EOF
    
    chmod +x monitor_mac_network.sh
    print_success "網路監控腳本已創建: monitor_mac_network.sh"
}

# 主執行流程
main() {
    print_header "開始Mac網路檢測和配置"
    
    # 檢測公網IP
    local ip_result=$(detect_public_ip)
    local public_ip=$(echo "$ip_result" | cut -d'|' -f1)
    local detection_method=$(echo "$ip_result" | cut -d'|' -f2)
    
    if [[ -n "$public_ip" && "$detection_method" != "failed" ]]; then
        print_success "🌐 您的Mac公網IP: $public_ip"
        print_info "檢測方法: $detection_method"
    else
        print_error "無法檢測公網IP，請檢查網路連接"
        print_info "您可以手動訪問 https://ipinfo.io 查看您的公網IP"
        exit 1
    fi
    
    # 檢測本地IP
    local local_ip=$(detect_local_ip)
    if [[ -n "$local_ip" ]]; then
        print_success "🏠 您的Mac本地IP: $local_ip"
    else
        print_warning "無法檢測本地IP"
        local_ip="unknown"
    fi
    
    # 檢測網路資訊
    local network_info=$(detect_network_info)
    
    # 創建網路配置
    local config_file=$(create_powerautomation_network_config "$public_ip" "$local_ip" "$detection_method" "$network_info")
    
    # 更新MCP配置
    update_mcp_config_with_network "$public_ip" "$local_ip" "$config_file"
    
    # 創建網路監控
    create_network_monitor "$public_ip" "$local_ip"
    
    print_header "Mac網路配置完成"
    print_success "🎉 您的Mac網路資訊已配置到PowerAutomation中!"
    print_info "📋 公網IP: $public_ip"
    print_info "📋 本地IP: $local_ip"
    print_info "📋 網路配置: $config_file"
    print_info "📋 監控腳本: monitor_mac_network.sh"
    
    print_header "重要資訊"
    print_warning "請記錄您的公網IP: $public_ip"
    print_info "此IP將用於PowerAutomation雲端連接配置"
    print_info "如果IP變化，請重新運行此腳本更新配置"
    
    # 顯示連接資訊
    print_header "PowerAutomation連接配置"
    print_info "🔗 EC2服務器: 18.212.97.173"
    print_info "🔗 您的Mac公網IP: $public_ip"
    print_info "🔗 您的Mac本地IP: $local_ip"
    print_info "🔗 MCP服務端點: http://$local_ip:8080"
}

# 執行主函數
main "$@"
EOF

chmod +x detect_mac_public_ip.sh
print_success "Mac公網IP檢測腳本已創建: detect_mac_public_ip.sh"

