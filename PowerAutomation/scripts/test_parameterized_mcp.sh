#!/bin/bash

# 參數化MCP API 測試腳本
BASE_URL="http://127.0.0.1:5001"

echo "🚀 參數化MCP API 測試開始"
echo "================================"

# 1. 健康檢查
echo "📡 1. 健康檢查"
curl -X GET "$BASE_URL/health" | jq '.'

echo -e "\n================================"

# 2. 獲取專家列表
echo "👨‍💼 2. 專家列表"
curl -X GET "$BASE_URL/api/experts" | jq '.'

echo -e "\n================================"

# 3. 識別專家測試
echo "🧠 3. 識別專家 - 保險SOP"
curl -X POST "$BASE_URL/api/identify" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "臺銀人壽保單行政作業核保流程分析"
  }' | jq '.'

echo -e "\n================================"

# 4. 處理保險業務請求
echo "🏦 4. 處理保險業務請求"
curl -X POST "$BASE_URL/api/process" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "臺銀人壽保單行政作業SOP大概要花多少人處理表單，自動化比率在業界有多高，表單OCR用人來審核在整個SOP流程所佔的人月大概是多少？"
  }' | jq '.'

echo -e "\n================================"

# 5. 演示請求 - 保險
echo "🎯 5. 演示請求 - 保險"
curl -X POST "$BASE_URL/api/demo" \
  -H "Content-Type: application/json" \
  -d '{"type": "insurance"}' | jq '.'

echo -e "\n================================"

# 6. 演示請求 - 行政
echo "📋 6. 演示請求 - 行政"
curl -X POST "$BASE_URL/api/demo" \
  -H "Content-Type: application/json" \
  -d '{"type": "admin"}' | jq '.'

echo -e "\n================================"

# 7. 演示請求 - 核保
echo "🔍 7. 演示請求 - 核保"
curl -X POST "$BASE_URL/api/demo" \
  -H "Content-Type: application/json" \
  -d '{"type": "underwriting"}' | jq '.'

echo -e "\n================================"

# 8. 演示請求 - 理賠
echo "💰 8. 演示請求 - 理賠"
curl -X POST "$BASE_URL/api/demo" \
  -H "Content-Type: application/json" \
  -d '{"type": "claims"}' | jq '.'

echo -e "\n================================"

echo "✅ 參數化MCP API測試完成！"

