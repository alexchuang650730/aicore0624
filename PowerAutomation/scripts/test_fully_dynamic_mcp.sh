#!/bin/bash

# 完全動態MCP API 測試腳本
BASE_URL="http://127.0.0.1:5002"

echo "🚀 完全動態MCP API 測試開始"
echo "================================"

# 1. 健康檢查
echo "📡 1. 健康檢查"
curl -X GET "$BASE_URL/health" | jq '.'

echo -e "\n================================"

# 2. 系統狀態
echo "📊 2. 系統狀態"
curl -X GET "$BASE_URL/api/status" | jq '.'

echo -e "\n================================"

# 3. Cloud Search MCP測試
echo "🔍 3. Cloud Search MCP"
curl -X POST "$BASE_URL/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "臺銀人壽保單行政作業SOP"
  }' | jq '.'

echo -e "\n================================"

# 4. 識別專業領域
echo "🧠 4. 識別專業領域"
curl -X POST "$BASE_URL/api/identify" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "臺銀人壽保單行政作業SOP大概要花多少人處理表單，自動化比率在業界有多高？",
    "context": "保險業務流程分析"
  }' | jq '.'

echo -e "\n================================"

# 5. 完全動態處理 - 保險業務分析
echo "🏦 5. 完全動態處理 - 保險業務"
curl -X POST "$BASE_URL/api/process" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "臺銀人壽保單行政作業SOP大概要花多少人處理表單，自動化比率在業界有多高，表單OCR用人來審核在整個SOP流程所佔的人月大概是多少？"
  }' | jq '.'

echo -e "\n================================"

# 6. 演示請求 - 保險
echo "🎯 6. 演示請求 - 保險"
curl -X POST "$BASE_URL/api/demo" \
  -H "Content-Type: application/json" \
  -d '{"type": "insurance"}' | jq '.'

echo -e "\n================================"

# 7. 演示請求 - 技術
echo "💻 7. 演示請求 - 技術"
curl -X POST "$BASE_URL/api/demo" \
  -H "Content-Type: application/json" \
  -d '{"type": "technology"}' | jq '.'

echo -e "\n================================"

# 8. 演示請求 - 管理
echo "📋 8. 演示請求 - 管理"
curl -X POST "$BASE_URL/api/demo" \
  -H "Content-Type: application/json" \
  -d '{"type": "management"}' | jq '.'

echo -e "\n================================"

# 9. 複雜查詢測試
echo "🔬 9. 複雜查詢測試"
curl -X POST "$BASE_URL/api/process" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "保險業如何運用AI技術提升核保效率，同時確保風險控制和法規合規？請從技術、業務和管理三個角度分析。"
  }' | jq '.'

echo -e "\n================================"

echo "✅ 完全動態MCP API測試完成！"
echo ""
echo "🎯 測試重點："
echo "- Cloud Search MCP功能"
echo "- 動態領域識別"
echo "- 零硬編碼專家調用"
echo "- 智能回答聚合"
echo "- 完整工作流程"

