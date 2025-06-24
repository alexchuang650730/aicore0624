# 📹 Workflow Recorder 使用指南

## 🎯 **概述**

Workflow Recorder是Agentic Agent管理中心的核心組件，用於錄製、分析和學習工作流操作序列。它可以自動捕獲用戶操作，轉化為結構化數據，並通過RL SRT進行智能學習。

## 🚀 **快速開始**

### 1. 啟動服務
```bash
cd /home/ubuntu/aicore0622/agent_admin
./start_local.sh
# 訪問: http://localhost:8081
```

### 2. 進入錄製界面
- 打開管理界面
- 點擊「工作流錄製」標籤
- 查看錄製狀態和會話列表

## 🎮 **前端界面使用**

### 錄製控制面板
```html
<!-- 錄製狀態顯示 -->
<div class="recording-status">
    <span id="recording-indicator">⚫ 未錄製</span>
    <span id="session-info">無活動會話</span>
</div>

<!-- 錄製控制按鈕 -->
<div class="recording-controls">
    <button id="start-recording">🔴 開始錄製</button>
    <button id="stop-recording" disabled>⏹️ 停止錄製</button>
    <button id="pause-recording" disabled>⏸️ 暫停錄製</button>
</div>

<!-- 會話配置 -->
<div class="session-config">
    <input type="text" id="session-name" placeholder="會話名稱">
    <select id="workflow-type">
        <option value="automation">自動化</option>
        <option value="form_filling">表單填寫</option>
        <option value="data_extraction">數據提取</option>
        <option value="testing">測試流程</option>
    </select>
    <textarea id="session-description" placeholder="會話描述"></textarea>
</div>
```

### JavaScript控制代碼
```javascript
// 開始錄製
async function startRecording() {
    const sessionName = document.getElementById('session-name').value || 'Unnamed Session';
    const workflowType = document.getElementById('workflow-type').value;
    const description = document.getElementById('session-description').value;
    
    try {
        const response = await fetch('/api/workflow/recording/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                session_name: sessionName,
                workflow_type: workflowType,
                description: description
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateRecordingStatus('recording', result.data);
            enableRecordingControls(true);
            console.log('錄製開始:', result.data);
        } else {
            alert('錄製開始失敗: ' + result.error);
        }
    } catch (error) {
        console.error('錄製開始錯誤:', error);
        alert('錄製開始錯誤: ' + error.message);
    }
}

// 停止錄製
async function stopRecording() {
    try {
        const response = await fetch('/api/workflow/recording/stop', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateRecordingStatus('stopped', result.data);
            enableRecordingControls(false);
            
            // 顯示學習結果
            if (result.data.learning_result) {
                displayLearningResults(result.data.learning_result);
            }
            
            // 刷新會話列表
            loadRecordingSessions();
            
            console.log('錄製完成:', result.data);
        } else {
            alert('錄製停止失敗: ' + result.error);
        }
    } catch (error) {
        console.error('錄製停止錯誤:', error);
        alert('錄製停止錯誤: ' + error.message);
    }
}

// 更新錄製狀態
function updateRecordingStatus(status, data) {
    const indicator = document.getElementById('recording-indicator');
    const sessionInfo = document.getElementById('session-info');
    
    switch (status) {
        case 'recording':
            indicator.innerHTML = '🔴 錄製中';
            indicator.className = 'recording-active';
            sessionInfo.innerHTML = `會話: ${data.session_name}`;
            break;
        case 'stopped':
            indicator.innerHTML = '⚫ 已停止';
            indicator.className = 'recording-stopped';
            sessionInfo.innerHTML = `完成: ${data.recorded_steps} 步驟`;
            break;
        default:
            indicator.innerHTML = '⚫ 未錄製';
            indicator.className = 'recording-idle';
            sessionInfo.innerHTML = '無活動會話';
    }
}

// 載入錄製會話列表
async function loadRecordingSessions() {
    try {
        const response = await fetch('/api/workflow/sessions');
        const result = await response.json();
        
        if (result.success) {
            displaySessionsList(result.data.sessions);
        }
    } catch (error) {
        console.error('載入會話列表錯誤:', error);
    }
}

// 顯示會話列表
function displaySessionsList(sessions) {
    const container = document.getElementById('sessions-list');
    container.innerHTML = '';
    
    sessions.forEach(session => {
        const sessionElement = document.createElement('div');
        sessionElement.className = 'session-item';
        sessionElement.innerHTML = `
            <div class="session-header">
                <h4>${session.session_name}</h4>
                <span class="session-status ${session.status}">${session.status}</span>
            </div>
            <div class="session-details">
                <p>類型: ${session.workflow_type}</p>
                <p>步驟: ${session.recorded_steps}</p>
                <p>時間: ${new Date(session.start_time).toLocaleString()}</p>
            </div>
            <div class="session-actions">
                <button onclick="viewSessionDetails('${session.session_id}')">查看詳情</button>
                <button onclick="replayWorkflow('${session.session_id}')">重放</button>
                <button onclick="analyzeSession('${session.session_id}')">分析</button>
            </div>
        `;
        container.appendChild(sessionElement);
    });
}
```

## 🔧 **API使用方法**

### 1. 開始錄製
```bash
curl -X POST http://localhost:8081/api/workflow/recording/start \
  -H "Content-Type: application/json" \
  -d '{
    "session_name": "表單填寫演示",
    "workflow_type": "form_filling",
    "description": "演示如何自動填寫用戶註冊表單"
  }'
```

**響應示例:**
```json
{
  "success": true,
  "data": {
    "session_id": "session_1703234567890",
    "session_name": "表單填寫演示",
    "status": "recording",
    "start_time": "2025-06-22T10:30:00Z"
  }
}
```

### 2. 檢查錄製狀態
```bash
curl http://localhost:8081/api/workflow/recording/status
```

**響應示例:**
```json
{
  "success": true,
  "data": {
    "is_recording": true,
    "current_session": {
      "session_id": "session_1703234567890",
      "session_name": "表單填寫演示",
      "status": "recording",
      "recorded_steps": 5,
      "start_time": "2025-06-22T10:30:00Z"
    },
    "total_sessions": 12,
    "recent_sessions": [...]
  }
}
```

### 3. 停止錄製
```bash
curl -X POST http://localhost:8081/api/workflow/recording/stop \
  -H "Content-Type: application/json"
```

**響應示例:**
```json
{
  "success": true,
  "data": {
    "session": {
      "session_id": "session_1703234567890",
      "session_name": "表單填寫演示",
      "status": "completed",
      "recorded_steps": 8,
      "workflow_file": "/tmp/workflows/session_1703234567890.workflow.json"
    },
    "learning_result": {
      "patterns_learned": 3,
      "strategies_optimized": 2,
      "confidence_score": 0.85
    },
    "log_result": {
      "interactions_logged": 8,
      "features_extracted": 15
    }
  }
}
```

### 4. 獲取會話列表
```bash
curl http://localhost:8081/api/workflow/sessions
```

### 5. 查看會話詳情
```bash
curl http://localhost:8081/api/workflow/sessions/session_1703234567890
```

### 6. 重放工作流
```bash
curl -X POST http://localhost:8081/api/workflow/sessions/session_1703234567890/replay \
  -H "Content-Type: application/json" \
  -d '{
    "variables": {
      "email": "test@example.com",
      "password": "newpassword123"
    }
  }'
```

## 🎯 **工作流類型**

### 1. **automation** - 通用自動化
- 適用於各種自動化任務
- 默認配置，適合大多數場景

### 2. **form_filling** - 表單填寫
- 專門針對表單操作優化
- 自動識別輸入字段和提交按鈕

### 3. **data_extraction** - 數據提取
- 適用於網頁數據抓取
- 重點記錄數據定位和提取操作

### 4. **testing** - 測試流程
- 用於UI測試錄製
- 包含斷言和驗證步驟

### 5. **navigation** - 導航操作
- 專注於頁面導航和鏈接點擊
- 適合網站瀏覽流程錄製

## 📊 **錄製數據格式**

### Workflow文件結構
```json
{
  "session_id": "session_1703234567890",
  "session_name": "表單填寫演示",
  "workflow_type": "form_filling",
  "description": "演示如何自動填寫用戶註冊表單",
  "start_time": "2025-06-22T10:30:00Z",
  "end_time": "2025-06-22T10:32:15Z",
  "total_duration": 135.5,
  "steps": [
    {
      "step_id": 1,
      "timestamp": "2025-06-22T10:30:05Z",
      "action_type": "navigate",
      "target": "https://example.com/register",
      "success": true,
      "duration": 2.1,
      "screenshot": "step_001.png",
      "metadata": {
        "page_title": "用戶註冊",
        "url": "https://example.com/register"
      }
    },
    {
      "step_id": 2,
      "timestamp": "2025-06-22T10:30:07Z",
      "action_type": "click",
      "target": "input[name='email']",
      "success": true,
      "duration": 0.3,
      "screenshot": "step_002.png"
    },
    {
      "step_id": 3,
      "timestamp": "2025-06-22T10:30:08Z",
      "action_type": "type",
      "target": "input[name='email']",
      "value": "user@example.com",
      "success": true,
      "duration": 1.2,
      "screenshot": "step_003.png"
    }
  ],
  "quality_metrics": {
    "completion_rate": 1.0,
    "efficiency_score": 0.85,
    "reliability_score": 0.92,
    "maintainability_score": 0.78
  },
  "learning_insights": {
    "identified_patterns": ["efficient_form_filling", "stable_selectors"],
    "optimization_opportunities": ["reduce_wait_times"],
    "success_factors": ["clear_element_targeting", "appropriate_timing"]
  }
}
```

## 🔄 **學習循環整合**

### 自動學習流程
```
1. 錄製完成 → 2. 數據解析 → 3. 模式識別 → 4. RL SRT學習 → 5. 策略優化
```

### 學習結果應用
```javascript
// 獲取基於學習的推薦
async function getWorkflowRecommendation(context) {
    const response = await fetch('/api/workflow/recommend', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            context: {
                task_type: 'form_filling',
                complexity: 'medium',
                environment_type: 'web_browser'
            }
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        console.log('推薦動作:', result.data.recommended_action);
        console.log('信心分數:', result.data.confidence_score);
        console.log('推理過程:', result.data.reasoning);
    }
}
```

## 🎮 **實際使用示例**

### 示例1: 錄製表單填寫流程
```javascript
// 1. 開始錄製
await startRecording({
    session_name: "用戶註冊流程",
    workflow_type: "form_filling",
    description: "錄製完整的用戶註冊操作序列"
});

// 2. 執行實際操作
// - 導航到註冊頁面
// - 填寫表單字段
// - 提交表單
// - 驗證結果

// 3. 停止錄製
const result = await stopRecording();

// 4. 查看學習結果
console.log('學習到的模式:', result.learning_result.patterns_learned);
```

### 示例2: 重放已錄製的工作流
```javascript
// 重放工作流並使用新的變量
await replayWorkflow('session_1703234567890', {
    variables: {
        email: 'newuser@example.com',
        password: 'securepassword456',
        firstName: 'John',
        lastName: 'Doe'
    }
});
```

### 示例3: 分析錄製會話
```javascript
// 獲取會話詳細分析
const sessionDetails = await getSessionDetails('session_1703234567890');

console.log('質量指標:', sessionDetails.quality_metrics);
console.log('學習洞察:', sessionDetails.learning_insights);
console.log('優化建議:', sessionDetails.optimization_suggestions);
```

## 🔧 **高級配置**

### 錄製選項配置
```javascript
const recordingOptions = {
    capture_screenshots: true,      // 捕獲截圖
    record_network: false,          // 記錄網絡請求
    include_timing: true,           // 包含時間信息
    auto_wait_detection: true,      // 自動等待檢測
    element_highlighting: false,    // 元素高亮
    quality_analysis: true,         // 質量分析
    learning_integration: true      // 學習整合
};
```

### 自定義工作流類型
```javascript
// 註冊自定義工作流類型
const customWorkflowType = {
    id: 'ecommerce_checkout',
    name: '電商結帳流程',
    description: '專門用於電商網站的結帳流程錄製',
    patterns: ['add_to_cart', 'checkout', 'payment'],
    optimization_focus: ['conversion_rate', 'user_experience']
};
```

## 📈 **性能監控**

### 錄製性能指標
- **錄製開銷**: < 5% CPU使用率
- **存儲需求**: 每分鐘約1-2MB
- **實時處理**: 延遲 < 100ms
- **學習延遲**: 錄製完成後2-5秒

### 質量保證
- **自動質量檢查**: 每個步驟的成功率驗證
- **完整性驗證**: 確保錄製數據完整
- **一致性檢查**: 驗證操作序列邏輯性

## 🎯 **最佳實踐**

### 錄製建議
1. **清晰命名**: 使用描述性的會話名稱
2. **適當分段**: 將複雜流程分解為多個會話
3. **包含驗證**: 錄製結果驗證步驟
4. **避免干擾**: 錄製時避免不相關操作

### 學習優化
1. **多樣化數據**: 錄製不同場景和變體
2. **質量優先**: 專注於高質量的操作序列
3. **及時反饋**: 使用學習結果改進後續錄製
4. **持續迭代**: 定期更新和優化工作流

**🎊 現在您可以開始使用Workflow Recorder來錄製、學習和優化您的工作流程了！**

