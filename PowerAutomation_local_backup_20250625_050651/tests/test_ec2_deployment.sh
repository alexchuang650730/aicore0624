#!/bin/bash

# PowerAutomation EC2 完整測試腳本
# 執行全面的功能測試和性能驗證

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 日誌函數
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_test() { echo -e "${PURPLE}[TEST]${NC} $1"; }
log_result() { echo -e "${CYAN}[RESULT]${NC} $1"; }

# 測試配置
APP_DIR="/home/ubuntu/powerautomation"
BASE_URL="http://localhost:5000"
HTTPS_URL="https://localhost"
TEST_RESULTS_FILE="/tmp/powerautomation_test_results.json"
PERFORMANCE_LOG="/tmp/powerautomation_performance.log"

# 測試計數器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 記錄測試結果
record_test() {
    local test_name="$1"
    local status="$2"
    local details="$3"
    local response_time="$4"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [[ "$status" == "PASS" ]]; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        log_success "✅ $test_name"
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        log_error "❌ $test_name"
    fi
    
    if [[ -n "$details" ]]; then
        log_result "   📝 $details"
    fi
    
    if [[ -n "$response_time" ]]; then
        log_result "   ⏱️  響應時間: ${response_time}ms"
    fi
    
    # 記錄到JSON文件
    echo "{\"test\":\"$test_name\",\"status\":\"$status\",\"details\":\"$details\",\"response_time\":\"$response_time\",\"timestamp\":\"$(date -Iseconds)\"}" >> "$TEST_RESULTS_FILE"
}

# HTTP請求測試函數
test_http_request() {
    local method="$1"
    local url="$2"
    local expected_status="$3"
    local test_name="$4"
    local data="$5"
    
    log_test "測試: $test_name"
    
    local start_time=$(date +%s%3N)
    local response
    local status_code
    local response_time
    
    if [[ "$method" == "GET" ]]; then
        response=$(curl -s -w "\n%{http_code}" -m 30 "$url" 2>/dev/null || echo -e "\n000")
    elif [[ "$method" == "POST" ]]; then
        if [[ -n "$data" ]]; then
            response=$(curl -s -w "\n%{http_code}" -m 30 -X POST -H "Content-Type: application/json" -d "$data" "$url" 2>/dev/null || echo -e "\n000")
        else
            response=$(curl -s -w "\n%{http_code}" -m 30 -X POST "$url" 2>/dev/null || echo -e "\n000")
        fi
    fi
    
    local end_time=$(date +%s%3N)
    response_time=$((end_time - start_time))
    
    status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n -1)
    
    if [[ "$status_code" == "$expected_status" ]]; then
        record_test "$test_name" "PASS" "狀態碼: $status_code" "$response_time"
        
        # 如果是JSON響應，嘗試解析
        if echo "$body" | jq . >/dev/null 2>&1; then
            local success=$(echo "$body" | jq -r '.success // "unknown"' 2>/dev/null)
            if [[ "$success" == "true" ]]; then
                log_result "   ✅ API響應成功"
            elif [[ "$success" == "false" ]]; then
                local error=$(echo "$body" | jq -r '.error // "未知錯誤"' 2>/dev/null)
                log_result "   ⚠️  API錯誤: $error"
            fi
        fi
    else
        record_test "$test_name" "FAIL" "期望狀態碼: $expected_status, 實際: $status_code" "$response_time"
        if [[ -n "$body" && ${#body} -lt 200 ]]; then
            log_result "   📄 響應內容: $body"
        fi
    fi
    
    # 記錄性能數據
    echo "$(date -Iseconds),$test_name,$response_time,$status_code" >> "$PERFORMANCE_LOG"
}

# 檢查服務狀態
check_service_status() {
    log_info "檢查服務狀態..."
    
    # 檢查PowerAutomation服務
    if systemctl is-active --quiet powerautomation; then
        record_test "PowerAutomation服務狀態" "PASS" "服務正在運行"
    else
        record_test "PowerAutomation服務狀態" "FAIL" "服務未運行"
    fi
    
    # 檢查Nginx服務
    if systemctl is-active --quiet nginx; then
        record_test "Nginx服務狀態" "PASS" "服務正在運行"
    else
        record_test "Nginx服務狀態" "FAIL" "服務未運行"
    fi
    
    # 檢查端口監聽
    if netstat -tlnp | grep -q ":5000"; then
        record_test "端口5000監聽" "PASS" "PowerAutomation端口正常"
    else
        record_test "端口5000監聽" "FAIL" "PowerAutomation端口未監聽"
    fi
    
    if netstat -tlnp | grep -q ":80\|:443"; then
        record_test "HTTP/HTTPS端口監聽" "PASS" "Nginx端口正常"
    else
        record_test "HTTP/HTTPS端口監聽" "FAIL" "Nginx端口未監聽"
    fi
}

# 基礎API測試
test_basic_apis() {
    log_info "執行基礎API測試..."
    
    # 健康檢查
    test_http_request "GET" "$BASE_URL/api/powerautomation/health" "200" "健康檢查API"
    
    # 系統狀態
    test_http_request "GET" "$BASE_URL/api/powerautomation/status" "200" "系統狀態API"
    
    # 系統啟動
    test_http_request "POST" "$BASE_URL/api/powerautomation/start" "200" "系統啟動API"
    
    # API信息
    test_http_request "GET" "$BASE_URL/api/info" "200" "API信息頁面"
    
    # 根路徑
    test_http_request "GET" "$BASE_URL/" "200" "根路徑訪問"
}

# TRAE功能測試
test_trae_functions() {
    log_info "執行TRAE功能測試..."
    
    # TRAE狀態
    test_http_request "GET" "$BASE_URL/api/powerautomation/trae/status" "200" "TRAE狀態檢查"
    
    # TRAE發送消息
    local trae_send_data='{"message":"EC2測試消息","repository":"smartinvention"}'
    test_http_request "POST" "$BASE_URL/api/powerautomation/trae/send" "200" "TRAE發送消息" "$trae_send_data"
    
    # TRAE數據同步
    local trae_sync_data='{"repository":"smartinvention","force":true}'
    test_http_request "POST" "$BASE_URL/api/powerautomation/trae/sync" "200" "TRAE數據同步" "$trae_sync_data"
}

# Manus功能測試
test_manus_functions() {
    log_info "執行Manus功能測試..."
    
    # Manus連接
    test_http_request "POST" "$BASE_URL/api/powerautomation/manus/connect" "200" "Manus連接"
    
    # Manus任務列表
    test_http_request "GET" "$BASE_URL/api/powerautomation/manus/tasks" "200" "Manus任務列表"
}

# 智能功能測試
test_intelligent_functions() {
    log_info "執行智能功能測試..."
    
    # 對話分析
    local analyze_data='{"messages":[{"role":"user","content":"我需要幫助部署PowerAutomation"},{"role":"assistant","content":"我可以幫助您部署PowerAutomation系統"}],"repository":"smartinvention","conversation_id":"ec2_test_001"}'
    test_http_request "POST" "$BASE_URL/api/powerautomation/analyze" "200" "對話分析" "$analyze_data"
    
    # 智能介入
    local intervene_data='{"type":"suggestion","target":"trae","message":"建議檢查EC2部署狀態","context":{"repository":"smartinvention","conversation_id":"ec2_test_001"}}'
    test_http_request "POST" "$BASE_URL/api/powerautomation/intervene" "200" "智能介入" "$intervene_data"
    
    # 倉庫列表
    test_http_request "GET" "$BASE_URL/api/powerautomation/repositories" "200" "倉庫列表"
}

# 系統測試
test_system_functions() {
    log_info "執行系統功能測試..."
    
    # 系統自檢
    local test_data='{"type":"full"}'
    test_http_request "POST" "$BASE_URL/api/powerautomation/test" "200" "系統自檢" "$test_data"
}

# 性能測試
test_performance() {
    log_info "執行性能測試..."
    
    local concurrent_requests=10
    local test_url="$BASE_URL/api/powerautomation/health"
    
    log_test "並發性能測試 ($concurrent_requests 個並發請求)"
    
    local start_time=$(date +%s%3N)
    
    # 並發請求
    for i in $(seq 1 $concurrent_requests); do
        curl -s "$test_url" >/dev/null &
    done
    
    # 等待所有請求完成
    wait
    
    local end_time=$(date +%s%3N)
    local total_time=$((end_time - start_time))
    local avg_time=$((total_time / concurrent_requests))
    
    if [[ $total_time -lt 5000 ]]; then  # 5秒內完成
        record_test "並發性能測試" "PASS" "$concurrent_requests 個請求在 ${total_time}ms 內完成" "$avg_time"
    else
        record_test "並發性能測試" "FAIL" "$concurrent_requests 個請求耗時 ${total_time}ms" "$avg_time"
    fi
}

# 負載測試
test_load() {
    log_info "執行負載測試..."
    
    if command -v ab >/dev/null 2>&1; then
        log_test "Apache Bench負載測試"
        
        local ab_result=$(ab -n 100 -c 10 -q "$BASE_URL/api/powerautomation/health" 2>/dev/null | grep "Requests per second\|Time per request")
        
        if [[ -n "$ab_result" ]]; then
            record_test "Apache Bench負載測試" "PASS" "$ab_result"
        else
            record_test "Apache Bench負載測試" "FAIL" "負載測試執行失敗"
        fi
    else
        log_warning "Apache Bench未安裝，跳過負載測試"
    fi
}

# SSL/HTTPS測試
test_ssl() {
    log_info "執行SSL/HTTPS測試..."
    
    # 檢查SSL證書
    if [[ -f "/etc/ssl/certs/powerautomation.crt" ]] || [[ -f "/etc/letsencrypt/live/*/fullchain.pem" ]]; then
        record_test "SSL證書檢查" "PASS" "SSL證書文件存在"
        
        # 測試HTTPS連接
        if curl -k -s "$HTTPS_URL/api/powerautomation/health" >/dev/null 2>&1; then
            record_test "HTTPS連接測試" "PASS" "HTTPS連接正常"
        else
            record_test "HTTPS連接測試" "FAIL" "HTTPS連接失敗"
        fi
    else
        record_test "SSL證書檢查" "FAIL" "SSL證書文件不存在"
    fi
}

# 日誌檢查
check_logs() {
    log_info "檢查系統日誌..."
    
    # 檢查PowerAutomation日誌
    if [[ -f "/var/log/powerautomation/error.log" ]]; then
        local error_count=$(grep -c "ERROR\|CRITICAL" /var/log/powerautomation/error.log 2>/dev/null || echo "0")
        if [[ $error_count -eq 0 ]]; then
            record_test "PowerAutomation錯誤日誌" "PASS" "無錯誤記錄"
        else
            record_test "PowerAutomation錯誤日誌" "FAIL" "發現 $error_count 個錯誤"
        fi
    else
        record_test "PowerAutomation錯誤日誌" "FAIL" "日誌文件不存在"
    fi
    
    # 檢查Nginx日誌
    if [[ -f "/var/log/nginx/powerautomation_error.log" ]]; then
        local nginx_errors=$(grep -c "error\|crit" /var/log/nginx/powerautomation_error.log 2>/dev/null || echo "0")
        if [[ $nginx_errors -eq 0 ]]; then
            record_test "Nginx錯誤日誌" "PASS" "無錯誤記錄"
        else
            record_test "Nginx錯誤日誌" "FAIL" "發現 $nginx_errors 個錯誤"
        fi
    else
        record_test "Nginx錯誤日誌" "FAIL" "日誌文件不存在"
    fi
}

# 安全檢查
security_check() {
    log_info "執行安全檢查..."
    
    # 檢查防火牆狀態
    if command -v ufw >/dev/null 2>&1; then
        if ufw status | grep -q "Status: active"; then
            record_test "防火牆狀態" "PASS" "防火牆已啟用"
        else
            record_test "防火牆狀態" "FAIL" "防火牆未啟用"
        fi
    else
        record_test "防火牆狀態" "FAIL" "防火牆未安裝"
    fi
    
    # 檢查文件權限
    if [[ -d "$APP_DIR" ]]; then
        local app_owner=$(stat -c '%U' "$APP_DIR")
        if [[ "$app_owner" == "ubuntu" ]]; then
            record_test "應用目錄權限" "PASS" "權限設置正確"
        else
            record_test "應用目錄權限" "FAIL" "權限設置錯誤: $app_owner"
        fi
    else
        record_test "應用目錄權限" "FAIL" "應用目錄不存在"
    fi
}

# 生成測試報告
generate_report() {
    log_info "生成測試報告..."
    
    local success_rate=0
    if [[ $TOTAL_TESTS -gt 0 ]]; then
        success_rate=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
    fi
    
    local report_file="/tmp/powerautomation_ec2_test_report.html"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>PowerAutomation EC2 測試報告</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .summary { background: #e8f5e8; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .fail { background: #ffe8e8; }
        .test-result { margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }
        .pass { border-left-color: #4CAF50; }
        .fail { border-left-color: #f44336; }
        .performance { background: #f0f8ff; padding: 15px; margin: 20px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>PowerAutomation EC2 測試報告</h1>
        <p>測試時間: $(date)</p>
        <p>測試環境: EC2 Ubuntu</p>
    </div>
    
    <div class="summary $([ $success_rate -lt 80 ] && echo 'fail')">
        <h2>測試總結</h2>
        <p><strong>總測試數:</strong> $TOTAL_TESTS</p>
        <p><strong>通過測試:</strong> $PASSED_TESTS</p>
        <p><strong>失敗測試:</strong> $FAILED_TESTS</p>
        <p><strong>成功率:</strong> $success_rate%</p>
    </div>
    
    <div class="performance">
        <h2>性能數據</h2>
        <p>詳細性能日誌: $PERFORMANCE_LOG</p>
    </div>
    
    <h2>詳細測試結果</h2>
EOF

    # 添加測試結果
    while IFS= read -r line; do
        local test_name=$(echo "$line" | jq -r '.test')
        local status=$(echo "$line" | jq -r '.status')
        local details=$(echo "$line" | jq -r '.details')
        local response_time=$(echo "$line" | jq -r '.response_time')
        
        local css_class="pass"
        local status_icon="✅"
        if [[ "$status" == "FAIL" ]]; then
            css_class="fail"
            status_icon="❌"
        fi
        
        cat >> "$report_file" << EOF
    <div class="test-result $css_class">
        <strong>$status_icon $test_name</strong><br>
        狀態: $status<br>
        詳情: $details<br>
        響應時間: ${response_time}ms
    </div>
EOF
    done < "$TEST_RESULTS_FILE"
    
    cat >> "$report_file" << EOF
</body>
</html>
EOF

    log_success "測試報告已生成: $report_file"
}

# 主函數
main() {
    log_info "開始PowerAutomation EC2完整測試..."
    
    # 初始化測試文件
    echo "" > "$TEST_RESULTS_FILE"
    echo "timestamp,test_name,response_time_ms,status_code" > "$PERFORMANCE_LOG"
    
    # 執行測試套件
    check_service_status
    test_basic_apis
    test_trae_functions
    test_manus_functions
    test_intelligent_functions
    test_system_functions
    test_performance
    test_load
    test_ssl
    check_logs
    security_check
    
    # 生成報告
    generate_report
    
    # 顯示最終結果
    echo
    log_info "==================== 測試完成 ===================="
    log_result "總測試數: $TOTAL_TESTS"
    log_result "通過測試: $PASSED_TESTS"
    log_result "失敗測試: $FAILED_TESTS"
    
    local success_rate=0
    if [[ $TOTAL_TESTS -gt 0 ]]; then
        success_rate=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
    fi
    
    log_result "成功率: $success_rate%"
    
    if [[ $success_rate -ge 90 ]]; then
        log_success "🎉 測試結果: 優秀 - 系統完全準備就緒！"
        exit 0
    elif [[ $success_rate -ge 80 ]]; then
        log_success "👍 測試結果: 良好 - 系統基本準備就緒"
        exit 0
    elif [[ $success_rate -ge 60 ]]; then
        log_warning "⚠️  測試結果: 一般 - 需要修復部分問題"
        exit 1
    else
        log_error "❌ 測試結果: 不合格 - 需要重大修復"
        exit 1
    fi
}

# 執行主函數
main "$@"

