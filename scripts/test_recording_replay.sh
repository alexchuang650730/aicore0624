#!/bin/bash

# 錄製MCP和Replay分析功能測試腳本
# 使用curf工具進行API測試

BASE_URL="http://localhost:5000"
echo "🎬 測試錄製MCP和Replay分析功能"
echo "=================================="

# 檢查服務狀態
echo "1. 檢查服務健康狀態..."
curl -s "$BASE_URL/health" | jq '.'

echo -e "\n2. 檢查錄製狀態..."
curl -s "$BASE_URL/api/workflow/recording/status" | jq '.'

echo -e "\n3. 開始錄製工作流..."
curl -s -X POST "$BASE_URL/api/workflow/recording/start" \
  -H "Content-Type: application/json" \
  -d '{
    "session_name": "測試表單填寫",
    "workflow_type": "form_filling", 
    "description": "自動化表單填寫測試"
  }' | jq '.'

echo -e "\n4. 等待5秒模擬錄製過程..."
sleep 5

echo -e "\n5. 停止錄製..."
curl -s -X POST "$BASE_URL/api/workflow/recording/stop" | jq '.'

echo -e "\n6. 測試Replay處理..."
curl -s -X POST "$BASE_URL/api/replay/process" \
  -H "Content-Type: application/json" \
  -d '{
    "replay_url": "https://manus.im/share/4Zn26HUNIGO0Ot0bTpUDGI?replay=1"
  }' | jq '.'

echo -e "\n7. 測試Replay分類..."
curl -s -X POST "$BASE_URL/api/replay/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "replay_data": {
      "operations": [
        {"action_type": "click", "target": "button", "success": true},
        {"action_type": "type", "target": "input", "value": "test", "success": true}
      ],
      "context": {"task_type": "form_filling"}
    }
  }' | jq '.'

echo -e "\n8. 測試工作流推薦..."
curl -s -X POST "$BASE_URL/api/workflow/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "context": {
      "current_page": "https://example.com/form",
      "task_type": "form_filling"
    }
  }' | jq '.'

echo -e "\n9. 獲取學習統計..."
curl -s "$BASE_URL/api/workflow/learning/statistics" | jq '.'

echo -e "\n10. 提供反饋..."
curl -s -X POST "$BASE_URL/api/workflow/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "rating": 5,
    "feedback": "測試成功"
  }' | jq '.'

echo -e "\n✅ 測試完成！"
