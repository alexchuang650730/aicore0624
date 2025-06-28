# 自動化驗證協調器 Workflow MCP

## 🎯 **核心職責**

自動化驗證協調器是 PowerAutomation 系統中的**驗證門禁協調器**，專門負責：

- ✅ **協調驗證流程** - 確保所有操作都經過適當的驗證
- 🚫 **阻止未驗證操作** - 防止跳過關鍵驗證步驟
- 📊 **驗證結果分析** - 提供詳細的驗證報告和建議
- 🔄 **操作歷史追蹤** - 記錄所有驗證操作的歷史

## 🏗️ **架構設計**

### **職責邊界**
```
┌─────────────────────────────────────────────────────────┐
│                自動化驗證協調器                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │  驗證規則   │  │  結果分析   │  │  操作控制   │      │
│  │    管理     │  │    引擎     │  │    門禁     │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Test Flow   │      │ Deployment  │      │ Operations  │
│    MCP      │      │    MCP      │      │    MCP      │
└─────────────┘      └─────────────┘      └─────────────┘
```

### **與其他 MCP 的關係**
- **Test Flow MCP**: 處理功能測試和 API 配置檢查
- **Deployment MCP**: 處理實際的部署操作
- **Operations MCP**: 處理運維操作
- **驗證協調器**: 確保上述操作都經過驗證

## 🚀 **快速開始**

### **安裝依賴**
```bash
pip install asyncio logging dataclasses enum
```

### **基本使用**

#### **1. 部署前驗證**
```bash
python main.py deployment --context '{"environment": "production", "service": "api-server"}'
```

#### **2. 測試前驗證**
```bash
python main.py testing --context '{"test_suite": "integration", "environment": "staging"}'
```

#### **3. 運維操作驗證**
```bash
python main.py operations --context '{"operation": "maintenance", "window": "2025-06-26T02:00:00Z"}'
```

#### **4. 發布驗證**
```bash
python main.py release --context '{"version": "v1.2.0", "environment": "production"}'
```

### **查看狀態**

#### **操作歷史**
```bash
python main.py deployment --history
```

#### **被阻止的操作**
```bash
python main.py deployment --blocked
```

#### **解除操作阻止**
```bash
python main.py deployment --unblock deployment
```

## 📋 **驗證規則**

### **部署操作驗證規則**
1. **environment_readiness** - 環境就緒性檢查
   - 網絡連通性
   - 磁盤空間
   - 內存可用性
   - CPU 負載

2. **resource_availability** - 系統資源可用性檢查
   - CPU 核心數
   - 內存容量
   - 磁盤空間

3. **dependency_services** - 依賴服務狀態檢查
   - 數據庫連接
   - Redis 服務
   - 消息隊列
   - 外部 API

4. **security_compliance** - 安全合規性檢查
   - SSL 證書
   - 訪問權限
   - 漏洞掃描
   - 加密狀態

### **測試操作驗證規則**
1. **test_environment_isolation** - 測試環境隔離檢查
2. **test_data_preparation** - 測試數據準備檢查

### **運維操作驗證規則**
1. **system_health_baseline** - 系統健康基線檢查
2. **backup_verification** - 備份完整性驗證
3. **maintenance_window** - 維護窗口時間檢查

## 🔧 **配置說明**

### **驗證設置**
```json
{
  "verification_settings": {
    "default_timeout": 300,
    "max_retry_count": 3,
    "parallel_execution": false,
    "fail_fast": true,
    "require_all_critical": true
  }
}
```

### **集成配置**
```json
{
  "integration": {
    "test_flow_mcp": {
      "endpoint": "http://localhost:8301",
      "timeout": 120
    },
    "deployment_mcp": {
      "endpoint": "http://localhost:8305",
      "timeout": 300
    }
  }
}
```

## 📊 **驗證結果格式**

### **成功響應**
```json
{
  "operation_id": "deployment_1719408000",
  "operation_type": "deployment",
  "overall_status": "PASSED",
  "success_rate": 100.0,
  "summary": {
    "total_rules": 4,
    "passed": 4,
    "failed": 0,
    "skipped": 0
  },
  "critical_failures": [],
  "results": [
    {
      "rule_name": "environment_readiness",
      "status": "passed",
      "message": "環境就緒性檢查通過",
      "execution_time": 2.5,
      "timestamp": "2025-06-26T15:20:00Z"
    }
  ],
  "recommendations": [
    "✅ 所有驗證通過，可以安全進行操作"
  ]
}
```

### **失敗響應**
```json
{
  "operation_id": "deployment_1719408000",
  "operation_type": "deployment", 
  "overall_status": "FAILED",
  "success_rate": 75.0,
  "summary": {
    "total_rules": 4,
    "passed": 3,
    "failed": 1,
    "skipped": 0
  },
  "critical_failures": ["security_compliance"],
  "recommendations": [
    "🚨 存在關鍵驗證失敗，建議修復後重新驗證",
    "  - 修復 security_compliance: SSL 證書已過期"
  ]
}
```

## 🔄 **工作流程**

### **驗證協調流程**
```
1. 接收操作請求
   ↓
2. 檢查操作是否被阻止
   ↓
3. 獲取適用的驗證規則
   ↓
4. 按依賴關係排序規則
   ↓
5. 執行驗證規則
   ↓
6. 分析驗證結果
   ↓
7. 生成建議和報告
   ↓
8. 更新操作歷史
   ↓
9. 更新阻止狀態
```

### **驗證規則執行**
```
1. 檢查依賴條件
   ↓
2. 執行驗證方法
   ↓
3. 處理重試邏輯
   ↓
4. 記錄執行結果
   ↓
5. 判斷是否繼續
```

## 🛡️ **安全特性**

### **訪問控制**
- 身份驗證要求
- 操作權限檢查
- 審計日誌記錄

### **操作阻止機制**
- 自動阻止失敗的操作類型
- 手動阻止/解除功能
- 阻止狀態持久化

## 📈 **監控和告警**

### **操作監控**
- 驗證執行時間
- 成功率統計
- 失敗模式分析

### **告警機制**
- 關鍵驗證失敗告警
- 系統異常告警
- 性能閾值告警

## 🔧 **擴展開發**

### **添加新的驗證規則**
```python
async def _verify_custom_rule(self, context: Dict[str, Any]) -> tuple:
    """自定義驗證規則"""
    # 實現驗證邏輯
    success = True  # 驗證結果
    message = "驗證通過"  # 結果消息
    details = {}  # 詳細信息
    
    return success, message, details
```

### **集成外部服務**
```python
async def _call_external_service(self, service_url: str, data: dict) -> dict:
    """調用外部服務進行驗證"""
    # 實現外部服務調用
    pass
```

## 📝 **最佳實踐**

### **驗證規則設計**
1. **單一職責** - 每個規則只檢查一個方面
2. **明確依賴** - 清楚定義規則間的依賴關係
3. **合理超時** - 設置適當的超時時間
4. **詳細日誌** - 提供足夠的調試信息

### **錯誤處理**
1. **優雅降級** - 非關鍵規則失敗不應阻止整個流程
2. **重試機制** - 對臨時性錯誤進行重試
3. **清晰消息** - 提供可操作的錯誤信息

### **性能優化**
1. **並行執行** - 無依賴的規則可以並行執行
2. **結果緩存** - 緩存驗證結果避免重複檢查
3. **資源管理** - 合理管理系統資源使用

## 🤝 **與 PowerAutomation 系統集成**

### **遵循 PowerAutomation 規範**
- ✅ 每個 MCP 都有獨立的 CLI 接口
- ✅ 所有工具在使用前都在工具表中註冊
- ✅ 通過 workflow_mcp 管理核心工作流
- ✅ 遵循質量門禁規範：「若交付不成功，不同意離開」

### **集成點**
1. **與 Test Flow MCP 協作** - 避免重複的 API 配置檢查
2. **與 Deployment MCP 協作** - 確保部署前驗證完成
3. **與 Operations MCP 協作** - 確保運維操作安全執行

---

*遵循 PowerAutomation 質量門禁規範：「若交付不成功，不同意離開；若格式不正確或結果不好，不同意 review checkin」*

