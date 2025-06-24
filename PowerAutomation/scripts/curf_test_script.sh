#!/bin/bash

# Domain MCP API 測試腳本
# 使用curf測試所有API端點

BASE_URL="http://127.0.0.1:5000"

echo "🚀 Domain MCP API 測試開始"
echo "================================"

# 1. 健康檢查
echo "📡 1. 健康檢查"
curl -X GET "$BASE_URL/health" \
  -H "Content-Type: application/json" \
  | jq '.'

echo -e "\n================================"

# 2. 系統狀態
echo "📊 2. 系統狀態"
curl -X GET "$BASE_URL/api/status" \
  -H "Content-Type: application/json" \
  | jq '.'

echo -e "\n================================"

# 3. 專家列表
echo "👨‍💼 3. 專家列表"
curl -X GET "$BASE_URL/api/experts" \
  -H "Content-Type: application/json" \
  | jq '.'

echo -e "\n================================"

# 4. 智能分類測試 - 保險SOP分析
echo "🧠 4. 智能分類 - 保險SOP分析"
curl -X POST "$BASE_URL/api/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "分析臺銀人壽保單行政作業SOP，評估核保流程人力需求、自動化比率和OCR審核人月投入",
    "context": {
      "domain": "insurance",
      "document_type": "SOP",
      "analysis_type": "workforce_automation"
    }
  }' | jq '.'

echo -e "\n================================"

# 5. 處理請求 - 保險業務分析
echo "⚙️ 5. 處理請求 - 保險業務分析"
curl -X POST "$BASE_URL/api/process" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "這份臺銀人壽保單行政作業SOP大概要花多少人處理表單，自動化比率在業界有多高，表單OCR用人來審核在整個SOP流程所佔的人月大概是多少？",
    "context": {
      "industry": "life_insurance",
      "company": "Taiwan Bank Life Insurance",
      "document": "保單行政作業業務SOP",
      "analysis_focus": ["workforce_estimation", "automation_rate", "OCR_review_effort"]
    }
  }' | jq '.'

echo -e "\n================================"

# 6. 自我進化測試
echo "🧬 6. 自我進化測試"
curl -X POST "$BASE_URL/api/evolve" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "保險業核保流程自動化分析",
    "performance": 0.65
  }' | jq '.'

echo -e "\n================================"

# 7. 演示請求 - 業務類型
echo "🎯 7. 演示請求 - 業務分析"
curl -X POST "$BASE_URL/api/demo" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "business"
  }' | jq '.'

echo -e "\n================================"

# 8. 專業保險分析請求
echo "🏦 8. 專業保險分析"
curl -X POST "$BASE_URL/api/process" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "根據保險業界標準，分析核保作業流程的人力配置效率，包括：1)每月處理保單數量與人力比例 2)OCR技術在表單處理中的應用率 3)人工審核與自動化審核的成本效益比較 4)業界最佳實務的自動化程度",
    "context": {
      "industry_standards": true,
      "benchmarking": true,
      "cost_benefit_analysis": true
    }
  }' | jq '.'

echo -e "\n================================"

# 9. 邀請保險專家
echo "👨‍💼 9. 邀請保險專家"
curl -X POST "$BASE_URL/api/experts/invite" \
  -H "Content-Type: application/json" \
  -d '{
    "expert_type": "保險核保專家",
    "expertise_areas": ["核保流程", "風險評估", "自動化系統"],
    "task_description": "分析保險公司核保作業的人力需求和自動化程度"
  }' | jq '.'

echo -e "\n================================"

echo "✅ 所有API測試完成！"

