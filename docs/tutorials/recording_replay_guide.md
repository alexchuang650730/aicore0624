# 錄製MCP和Replay分析功能使用指南

## 📋 概述

本系統提供完整的工作流錄製、重播分析和智能學習功能，整合了以下核心組件：

- **WorkflowRecorder** - 工作流錄製器
- **ReplayClassifier** - Replay分類器  
- **RL SRT Adapter** - 強化學習適配器
- **Enhanced Interaction Log Manager** - 增強交互日誌管理器

## 🎬 工作流錄製功能

### 1. 開始錄製

**API端點**: `POST /api/workflow/recording/start`

**請求參數**:
```json
{
  "session_name": "工作流名稱",
  "workflow_type": "工作流類型",
  "description": "工作流描述"
}
```

**工作流類型**:
- `form_filling` - 表單填寫
- `data_extraction` - 數據提取
- `navigation` - 頁面導航
- `automation` - 自動化操作
- `testing` - 測試流程

**示例**:
```bash
curl -X POST http://localhost:5000/api/workflow/recording/start \
  -H "Content-Type: application/json" \
  -d '{
    "session_name": "用戶註冊流程",
    "workflow_type": "form_filling",
    "description": "自動化用戶註冊表單填寫"
  }'
```

**響應**:
```json
{
  "success": true,
  "data": {
    "session_id": "workflow_abc123",
    "session_name": "用戶註冊流程",
    "status": "recording",
    "start_time": "2025-06-22T10:30:00Z"
  }
}
```

### 2. 停止錄製

**API端點**: `POST /api/workflow/recording/stop`

**示例**:
```bash
curl -X POST http://localhost:5000/api/workflow/recording/stop
```

**響應**:
```json
{
  "success": true,
  "data": {
    "session_id": "workflow_abc123",
    "status": "completed",
    "recorded_steps": 15,
    "workflow_file": "/recordings/workflow_abc123/workflow.json",
    "learning_result": {
      "training_samples": 12,
      "learning_score": 0.85
    }
  }
}
```

### 3. 檢查錄製狀態

**API端點**: `GET /api/workflow/recording/status`

**示例**:
```bash
curl http://localhost:5000/api/workflow/recording/status
```

## 🔄 Replay分析功能

### 1. 處理Manus Replay

**API端點**: `POST /api/replay/process`

**請求參數**:
```json
{
  "replay_url": "https://manus.im/share/4Zn26HUNIGO0Ot0bTpUDGI?replay=1"
}
```

**示例**:
```bash
curl -X POST http://localhost:5000/api/replay/process \
  -H "Content-Type: application/json" \
  -d '{
    "replay_url": "https://manus.im/share/4Zn26HUNIGO0Ot0bTpUDGI?replay=1"
  }'
```

**響應**:
```json
{
  "success": true,
  "data": {
    "replay_id": "4Zn26HUNIGO0Ot0bTpUDGI",
    "classification": {
      "primary_category": "high_quality_success",
      "success_rate": 0.95,
      "efficiency_score": 0.88,
      "learning_value": "high"
    },
    "learning_samples": 8,
    "recommendations": [
      "工作流執行效率很高",
      "建議作為最佳實踐模板"
    ]
  }
}
```

### 2. 分類Replay數據

**API端點**: `POST /api/replay/classify`

**請求參數**:
```json
{
  "replay_data": {
    "operations": [...],
    "context": {...}
  }
}
```

### 3. 獲取工作流推薦

**API端點**: `POST /api/workflow/recommend`

**請求參數**:
```json
{
  "context": {
    "current_page": "https://example.com/form",
    "task_type": "form_filling",
    "previous_actions": [...]
  }
}
```

**響應**:
```json
{
  "success": true,
  "data": {
    "recommended_action": {
      "action_type": "click",
      "selector": "input[name='email']",
      "confidence": 0.92
    },
    "alternative_actions": [...],
    "reasoning": "基於歷史成功案例推薦"
  }
}
```

## 📊 學習統計和反饋

### 1. 獲取學習統計

**API端點**: `GET /api/workflow/learning/statistics`

**示例**:
```bash
curl http://localhost:5000/api/workflow/learning/statistics
```

**響應**:
```json
{
  "success": true,
  "data": {
    "total_sessions": 45,
    "successful_sessions": 38,
    "success_rate": 0.84,
    "total_training_samples": 156,
    "learning_progress": {
      "form_filling": 0.89,
      "data_extraction": 0.76,
      "navigation": 0.82
    }
  }
}
```

### 2. 提供反饋

**API端點**: `POST /api/workflow/feedback`

**請求參數**:
```json
{
  "session_id": "workflow_abc123",
  "rating": 5,
  "feedback": "工作流執行完美，節省了大量時間",
  "suggestions": ["可以增加錯誤處理機制"]
}
```

## 🔧 高級功能

### 1. 批量處理Replay

```bash
# 處理多個replay URL
curl -X POST http://localhost:5000/api/replay/batch-process \
  -H "Content-Type: application/json" \
  -d '{
    "replay_urls": [
      "https://manus.im/share/url1?replay=1",
      "https://manus.im/share/url2?replay=1"
    ]
  }'
```

### 2. 導出學習數據

```bash
# 導出特定會話的學習數據
curl http://localhost:5000/api/workflow/export/workflow_abc123
```

### 3. 工作流模板管理

```bash
# 獲取工作流模板
curl http://localhost:5000/api/workflow/templates

# 創建新模板
curl -X POST http://localhost:5000/api/workflow/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "電商購物流程",
    "category": "automation",
    "steps": [...]
  }'
```

## 🚀 啟動服務

### 1. 啟動主服務

```bash
cd /home/ubuntu/aicore0622/agent_admin/backend
python app.py
```

### 2. 檢查服務狀態

```bash
curl http://localhost:5000/health
```

## 📝 注意事項

1. **錄製環境**: 需要安裝workflow-use工具
2. **Replay URL**: 支持Manus平台的replay連結
3. **學習數據**: 自動保存到`/recordings`目錄
4. **安全性**: 所有代碼執行都在沙盒環境中
5. **並發**: 同時只能有一個錄製會話

## 🔍 故障排除

### 常見問題

1. **錄製失敗**: 檢查workflow-use環境是否正確安裝
2. **Replay解析失敗**: 確認URL格式正確且可訪問
3. **學習數據不生成**: 檢查錄製會話是否成功完成
4. **推薦不準確**: 需要更多訓練數據來提升準確性

### 日誌查看

```bash
# 查看應用日誌
tail -f /var/log/agentic-agent.log

# 查看錄製日誌
tail -f /recordings/*/session.log
```

## 📈 性能優化

1. **批量處理**: 使用批量API處理多個replay
2. **緩存**: 重複的replay會使用緩存結果
3. **異步處理**: 大型工作流使用異步處理
4. **數據壓縮**: 自動壓縮歷史錄製數據

這個系統提供了完整的工作流錄製、分析和學習功能，可以持續改進自動化效果！

