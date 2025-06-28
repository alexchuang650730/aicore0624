# test_flow_mcp 對比引擎測試用例

## 測試目標
使用 test_flow_mcp 現有對比引擎，量化比較「我們的 action vs Manus action」的差異和改進

---

## 對比測試用例 CMP-001: 技術需求分析對比

### 測試輸入
```
需求描述: "開發一個在線教育平台，需要支持視頻直播、互動白板、作業提交、成績管理、支付系統等功能"
```

### 對比設置
```json
{
  "test_id": "CMP-001",
  "comparison_type": "action_vs_action",
  "input": "開發一個在線教育平台，需要支持視頻直播、互動白板、作業提交、成績管理、支付系統等功能",
  "context": {
    "user_role": "developer",
    "task_type": "requirement_analysis",
    "comparison_target": "capability_improvement"
  },
  "systems_to_compare": {
    "system_a": {
      "name": "our_action",
      "description": "Claude SDK 集成後的系統",
      "endpoint": "/api/claude_code/analyze"
    },
    "system_b": {
      "name": "manus_action", 
      "description": "原始 Manus 系統",
      "endpoint": "/api/process"
    }
  }
}
```

---

## 對比測試用例 CMP-002: 代碼生成能力對比

### 測試輸入
```
需求描述: "幫我寫一個 React 組件，實現用戶登錄表單，包括用戶名、密碼輸入，記住密碼功能，以及表單驗證"
```

### 對比設置
```json
{
  "test_id": "CMP-002", 
  "comparison_type": "code_generation",
  "input": "幫我寫一個 React 組件，實現用戶登錄表單，包括用戶名、密碼輸入，記住密碼功能，以及表單驗證",
  "context": {
    "user_role": "developer",
    "task_type": "code_generation",
    "technology": "react"
  },
  "evaluation_criteria": [
    "代碼完整性",
    "代碼質量", 
    "最佳實踐遵循",
    "功能實現度",
    "可執行性"
  ]
}
```

---

## 對比測試用例 CMP-003: 架構諮詢對比

### 測試輸入
```
需求描述: "我們公司要從單體架構遷移到微服務，有 50 萬用戶，日活 10 萬，主要是電商業務，該如何規劃？"
```

### 對比設置
```json
{
  "test_id": "CMP-003",
  "comparison_type": "architecture_consultation", 
  "input": "我們公司要從單體架構遷移到微服務，有 50 萬用戶，日活 10 萬，主要是電商業務，該如何規劃？",
  "context": {
    "user_role": "architect",
    "task_type": "architecture_design",
    "business_context": "ecommerce"
  },
  "evaluation_criteria": [
    "方案可行性",
    "技術深度",
    "業務理解",
    "實施指導",
    "風險評估"
  ]
}
```

---

## 對比測試用例 CMP-004: 問題診斷對比

### 測試輸入
```
問題描述: "我的 Node.js 應用記憶體使用量持續增長，最終導致 OOM，該如何排查和解決？"
```

### 對比設置
```json
{
  "test_id": "CMP-004",
  "comparison_type": "problem_diagnosis",
  "input": "我的 Node.js 應用記憶體使用量持續增長，最終導致 OOM，該如何排查和解決？",
  "context": {
    "user_role": "developer",
    "task_type": "troubleshooting",
    "technology": "nodejs"
  },
  "evaluation_criteria": [
    "問題分析準確性",
    "診斷步驟完整性", 
    "解決方案實用性",
    "預防措施建議",
    "工具推薦"
  ]
}
```

---

## 對比測試用例 CMP-005: 性能優化建議對比

### 測試輸入
```
場景描述: "我的 React 應用首屏載入時間 5 秒，用戶體驗很差，請幫我分析優化方案"
```

### 對比設置
```json
{
  "test_id": "CMP-005",
  "comparison_type": "performance_optimization",
  "input": "我的 React 應用首屏載入時間 5 秒，用戶體驗很差，請幫我分析優化方案", 
  "context": {
    "user_role": "frontend_developer",
    "task_type": "performance_tuning",
    "technology": "react"
  },
  "evaluation_criteria": [
    "優化策略全面性",
    "技術方案可行性",
    "優先級排序合理性", 
    "量化指標提供",
    "實施難度評估"
  ]
}
```

---

## test_flow_mcp 對比引擎調用方式

### 調用格式
```json
{
  "request": "使用對比引擎分析以下兩個系統的回應差異",
  "context": {
    "source": "comparison_test",
    "workflow_type": "test_flow_comparison",
    "comparison_engine": "enabled"
  },
  "test_case": {
    "input": "測試輸入內容",
    "system_a_response": "我們系統的回應",
    "system_b_response": "Manus 系統的回應",
    "evaluation_criteria": ["標準1", "標準2", "標準3"]
  }
}
```

### 預期輸出格式
```json
{
  "comparison_result": {
    "overall_score": {
      "system_a": 8.5,
      "system_b": 6.2,
      "improvement": "+37%"
    },
    "detailed_analysis": {
      "strengths_a": ["優勢1", "優勢2"],
      "strengths_b": ["優勢1", "優勢2"], 
      "weaknesses_a": ["劣勢1"],
      "weaknesses_b": ["劣勢1", "劣勢2"]
    },
    "recommendation": "改進建議"
  }
}
```

---

## 測試執行計劃

### 第一階段：基礎對比測試
1. CMP-001: 需求分析能力對比
2. CMP-002: 代碼生成能力對比

### 第二階段：高級能力對比  
3. CMP-003: 架構諮詢能力對比
4. CMP-004: 問題診斷能力對比
5. CMP-005: 性能優化建議對比

### 第三階段：綜合分析
- 彙總所有對比結果
- 分析改進趨勢
- 生成能力提升報告

### 成功標準
- 我們的 action 在所有測試中平均得分 > Manus action
- 至少 3 個測試用例顯示顯著改進（>20%）
- 對比引擎能夠識別出具體的改進點

