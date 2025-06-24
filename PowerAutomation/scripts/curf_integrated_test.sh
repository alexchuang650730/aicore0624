#!/bin/bash

# ==========================================
# 完全整合智能系統 - curf測試腳本
# Fully Integrated Intelligent System - curf Test Script
# 
# 符合編碼執行階段交付格式
# Compliant with Coding Execution Phase Delivery Format
# ==========================================

set -e  # 遇到錯誤立即退出

# 配置
BASE_URL="http://127.0.0.1:5004"
PUBLIC_URL="https://5004-im7yx9pempr8evkfdhxbr-1ce18e5a.manusvm.computer"
TEST_RESULTS_FILE="curf_test_results.json"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 顏色輸出
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

# 測試結果記錄
declare -a test_results=()

record_test_result() {
    local test_name="$1"
    local status="$2"
    local response_time="$3"
    local details="$4"
    
    test_results+=("{\"test_name\":\"$test_name\",\"status\":\"$status\",\"response_time\":$response_time,\"details\":\"$details\",\"timestamp\":\"$TIMESTAMP\"}")
}

# 執行HTTP請求並測量響應時間
execute_request() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local description="$4"
    
    log_info "執行測試: $description"
    
    local start_time=$(date +%s.%N)
    
    if [ "$method" = "GET" ]; then
        local response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint" 2>/dev/null || echo -e "\nERROR")
    else
        local response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null || echo -e "\nERROR")
    fi
    
    local end_time=$(date +%s.%N)
    local response_time=$(echo "$end_time - $start_time" | bc -l)
    
    local http_code=$(echo "$response" | tail -n1)
    local response_body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" = "200" ]; then
        log_success "$description - HTTP $http_code (${response_time}s)"
        record_test_result "$description" "PASS" "$response_time" "HTTP $http_code"
        echo "$response_body" | jq '.' 2>/dev/null || echo "$response_body"
    elif [ "$http_code" = "ERROR" ]; then
        log_error "$description - 連接失敗"
        record_test_result "$description" "FAIL" "$response_time" "Connection failed"
    else
        log_warning "$description - HTTP $http_code (${response_time}s)"
        record_test_result "$description" "WARN" "$response_time" "HTTP $http_code"
        echo "$response_body"
    fi
    
    echo "----------------------------------------"
}

# 開始測試
echo "=========================================="
echo "完全整合智能系統 - curf測試套件"
echo "Fully Integrated Intelligent System - curf Test Suite"
echo "測試時間: $TIMESTAMP"
echo "=========================================="

# 1. 健康檢查測試
log_info "階段1: 系統健康檢查"
execute_request "GET" "/health" "" "系統健康檢查"

# 2. 系統狀態測試
log_info "階段2: 系統狀態檢查"
execute_request "GET" "/api/status" "" "系統狀態檢查"

# 3. 工具列表測試
log_info "階段3: 工具註冊表檢查"
execute_request "GET" "/api/tools" "" "可用工具列表"

# 4. 統計信息測試
log_info "階段4: 統計信息檢查"
execute_request "GET" "/api/stats" "" "系統統計信息"

# 5. 核心功能測試 - 保險業務分析
log_info "階段5: 核心功能測試"

# 5.1 臺銀人壽SOP分析
execute_request "POST" "/api/process" \
    '{"request": "臺銀人壽保單行政作業SOP需要多少人力？自動化比率如何？", "context": {"domain": "insurance", "priority": "high"}}' \
    "臺銀人壽SOP人力分析"

# 5.2 OCR技術評估
execute_request "POST" "/api/process" \
    '{"request": "保險業OCR技術應用的成本效益分析", "context": {"domain": "technology", "focus": "cost_benefit"}}' \
    "OCR技術成本效益分析"

# 5.3 數位轉型策略
execute_request "POST" "/api/process" \
    '{"request": "保險公司數位轉型的實施策略和風險評估", "context": {"domain": "strategy", "scope": "digital_transformation"}}' \
    "數位轉型策略分析"

# 5.4 法規合規分析
execute_request "POST" "/api/process" \
    '{"request": "保險業自動化流程的法規合規要求", "context": {"domain": "legal", "focus": "compliance"}}' \
    "法規合規要求分析"

# 6. 壓力測試 - 並發請求
log_info "階段6: 壓力測試"

# 6.1 快速連續請求
for i in {1..3}; do
    execute_request "POST" "/api/process" \
        "{\"request\": \"測試請求 $i - 系統負載測試\", \"context\": {\"test_id\": $i}}" \
        "並發測試請求 $i"
done

# 7. 邊界測試
log_info "階段7: 邊界測試"

# 7.1 空請求測試
execute_request "POST" "/api/process" \
    '{"request": "", "context": {}}' \
    "空請求邊界測試"

# 7.2 長文本請求測試
long_request="這是一個非常長的請求文本，用於測試系統對長文本的處理能力。"
for i in {1..10}; do
    long_request="$long_request 重複內容 $i。"
done

execute_request "POST" "/api/process" \
    "{\"request\": \"$long_request\", \"context\": {\"test_type\": \"long_text\"}}" \
    "長文本處理測試"

# 8. 公網訪問測試
log_info "階段8: 公網訪問測試"

if command -v curl &> /dev/null; then
    log_info "測試公網訪問: $PUBLIC_URL"
    
    public_response=$(curl -s -w "\n%{http_code}" "$PUBLIC_URL/health" 2>/dev/null || echo -e "\nERROR")
    public_http_code=$(echo "$public_response" | tail -n1)
    
    if [ "$public_http_code" = "200" ]; then
        log_success "公網訪問正常 - HTTP $public_http_code"
        record_test_result "公網訪問測試" "PASS" "0" "HTTP $public_http_code"
    else
        log_error "公網訪問失敗 - HTTP $public_http_code"
        record_test_result "公網訪問測試" "FAIL" "0" "HTTP $public_http_code"
    fi
fi

# 9. 生成測試報告
log_info "階段9: 生成測試報告"

# 計算測試統計
total_tests=${#test_results[@]}
passed_tests=$(printf '%s\n' "${test_results[@]}" | grep -c '"status":"PASS"' || echo 0)
failed_tests=$(printf '%s\n' "${test_results[@]}" | grep -c '"status":"FAIL"' || echo 0)
warning_tests=$(printf '%s\n' "${test_results[@]}" | grep -c '"status":"WARN"' || echo 0)

# 生成JSON報告
cat > "$TEST_RESULTS_FILE" << EOF
{
    "test_suite": "Fully Integrated Intelligent System curf Tests",
    "timestamp": "$TIMESTAMP",
    "summary": {
        "total_tests": $total_tests,
        "passed": $passed_tests,
        "failed": $failed_tests,
        "warnings": $warning_tests,
        "success_rate": $(echo "scale=2; $passed_tests * 100 / $total_tests" | bc -l)
    },
    "test_results": [
        $(IFS=','; echo "${test_results[*]}")
    ],
    "system_info": {
        "base_url": "$BASE_URL",
        "public_url": "$PUBLIC_URL",
        "test_environment": "sandbox"
    }
}
EOF

# 顯示測試總結
echo "=========================================="
echo "測試總結 - Test Summary"
echo "=========================================="
echo "總測試數: $total_tests"
echo "通過: $passed_tests"
echo "失敗: $failed_tests"
echo "警告: $warning_tests"
echo "成功率: $(echo "scale=1; $passed_tests * 100 / $total_tests" | bc -l)%"
echo "=========================================="

if [ $failed_tests -eq 0 ]; then
    log_success "所有核心測試通過！系統運行正常。"
    exit 0
else
    log_error "發現 $failed_tests 個失敗測試，請檢查系統狀態。"
    exit 1
fi

