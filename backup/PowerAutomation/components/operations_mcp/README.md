# 通用運維 MCP (Operations MCP)

## 🎯 **核心功能**

專門負責執行各種類型的運維操作，與自動化驗證協調器配合，確保運維操作前已通過驗證。

## ⚙️ **支持的運維操作類型**

### 📊 **系統監控 (System Monitoring)**
- CPU、內存、磁盤使用率監控
- 系統負載監控
- 自動告警生成
- 性能指標收集

### 🔄 **服務重啟 (Service Restart)**
- 單個或批量服務重啟
- 重啟狀態驗證
- 重啟日誌記錄
- 失敗自動重試

### 🗄️ **數據庫維護 (Database Maintenance)**
- 數據庫備份
- 索引優化
- 數據清理
- 性能調優

### 📝 **日誌輪轉 (Log Rotation)**
- 自動日誌歸檔
- 磁盤空間管理
- 日誌壓縮
- 清理過期日誌

### 💾 **備份操作 (Backup Operation)**
- 系統備份
- 數據備份
- 配置備份
- 備份驗證

### 🔒 **安全掃描 (Security Scan)**
- 漏洞掃描
- 配置檢查
- 權限審計
- 合規性檢查

### ⚡ **性能調優 (Performance Tuning)**
- 系統參數優化
- 資源配置調整
- 性能基準測試
- 瓶頸分析

### 🏥 **健康檢查 (Health Check)**
- 服務狀態檢查
- 連通性測試
- 響應時間測試
- 整體健康評分

### 🚨 **告警管理 (Alert Management)**
- 告警規則配置
- 告警通知發送
- 告警歷史記錄
- 告警統計分析

### 📈 **容量規劃 (Capacity Planning)**
- 資源使用趨勢分析
- 容量預測
- 擴容建議
- 成本優化建議

## 🛠️ **使用方法**

### **CLI 接口**

```bash
# 執行系統監控
python main.py execute \
  --name "daily-monitoring" \
  --type "system_monitoring" \
  --systems "web-server-1" "web-server-2" \
  --priority "normal"

# 重啟服務
python main.py execute \
  --name "restart-nginx" \
  --type "service_restart" \
  --systems "web-server-1" \
  --parameters '{"service_name": "nginx"}' \
  --priority "high"

# 數據庫維護
python main.py execute \
  --name "db-backup" \
  --type "database_maintenance" \
  --systems "db-server-1" \
  --parameters '{"maintenance_type": "backup"}' \
  --priority "critical"

# 健康檢查
python main.py execute \
  --name "health-check" \
  --type "health_check" \
  --systems "web-server-1" "api-server-1" \
  --priority "normal"

# 查看操作歷史
python main.py history

# 查看活躍操作
python main.py status

# 查看系統指標
python main.py monitor
```

### **Python API**

```python
from main import OperationsMCP, OperationConfig, OperationType, OperationPriority

# 創建運維 MCP 實例
operations_mcp = OperationsMCP()

# 配置運維操作
config = OperationConfig(
    name="system-health-check",
    type=OperationType.HEALTH_CHECK,
    priority=OperationPriority.NORMAL,
    description="定期系統健康檢查",
    target_systems=["web-server-1", "api-server-1"],
    parameters={},
    timeout=300,
    notification_channels=["email", "slack"]
)

# 執行運維操作
result = await operations_mcp.execute_operation(config)
print(f"操作狀態: {result.status}")
print(f"健康分數: {result.metrics}")
```

## ⚙️ **配置選項**

### **運維操作配置 (OperationConfig)**

```python
@dataclass
class OperationConfig:
    name: str                           # 操作名稱
    type: OperationType                 # 操作類型
    priority: OperationPriority         # 優先級
    description: str                    # 操作描述
    target_systems: List[str]           # 目標系統
    parameters: Dict[str, Any]          # 操作參數
    timeout: int = 300                  # 超時時間
    retry_count: int = 2                # 重試次數
    maintenance_window: str = None      # 維護窗口
    notification_channels: List[str] = None # 通知渠道
    rollback_enabled: bool = True       # 是否啟用回滾
```

### **系統配置**

```json
{
  "monitoring_interval": 60,
  "max_concurrent_operations": 5,
  "default_timeout": 300,
  "log_retention_days": 30,
  "backup_retention_days": 90,
  "alert_thresholds": {
    "cpu_usage": 80,
    "memory_usage": 85,
    "disk_usage": 90,
    "response_time": 5000
  },
  "notification_channels": {
    "email": "admin@company.com",
    "slack": "#ops-alerts",
    "webhook": "http://localhost:8000/alerts"
  },
  "maintenance_windows": {
    "daily": "02:00-04:00",
    "weekly": "Sunday 01:00-05:00",
    "monthly": "First Sunday 00:00-06:00"
  }
}
```

## 🔄 **運維操作流程**

1. **配置驗證** - 檢查運維操作配置的有效性
2. **維護窗口檢查** - 確保在允許的維護時間內
3. **並發控制** - 防止過多並發操作
4. **操作執行** - 根據類型執行具體運維操作
5. **指標收集** - 收集操作前後的系統指標
6. **結果分析** - 分析操作結果並生成建議
7. **通知發送** - 向相關人員發送操作結果通知

## 📊 **監控和告警**

### **系統指標監控**
- **CPU 使用率** - 實時監控處理器負載
- **內存使用率** - 監控內存消耗情況
- **磁盤使用率** - 監控存儲空間使用
- **網絡流量** - 監控網絡 I/O 狀況
- **響應時間** - 監控服務響應性能

### **告警規則**
```python
alert_thresholds = {
    "cpu_usage": 80,      # CPU 使用率超過 80% 告警
    "memory_usage": 85,   # 內存使用率超過 85% 告警
    "disk_usage": 90,     # 磁盤使用率超過 90% 告警
    "response_time": 5000 # 響應時間超過 5 秒告警
}
```

### **通知渠道**
- **郵件通知** - 發送詳細的操作報告
- **Slack 通知** - 實時告警和狀態更新
- **Webhook** - 集成第三方監控系統
- **短信通知** - 緊急情況快速通知

## 🔒 **安全和合規**

### **操作權限控制**
- 基於角色的訪問控制
- 操作審計日誌
- 敏感操作二次確認
- 操作時間窗口限制

### **數據安全**
- 備份數據加密
- 傳輸數據加密
- 訪問日誌記錄
- 合規性檢查

## 🎯 **與 PowerAutomation 集成**

### **與驗證協調器配合**
```python
# 運維操作前自動調用驗證協調器
verification_result = await verification_coordinator.coordinate_verification(
    "operations", operations_context
)

if verification_result["overall_status"] == "PASSED":
    # 執行運維操作
    operation_result = await operations_mcp.execute_operation(config)
else:
    # 阻止運維操作
    raise Exception("運維操作前驗證失敗")
```

### **與部署 MCP 協作**
- 部署後自動執行健康檢查
- 部署失敗時自動執行回滾操作
- 部署成功後更新監控配置

### **質量門禁遵循**
- ✅ 運維操作前強制驗證
- ✅ 操作失敗自動告警
- ✅ 完整操作審計
- ✅ 「若交付不成功，不同意離開」

## 📈 **運維最佳實踐**

### **1. 預防性維護**
- 定期執行系統健康檢查
- 主動監控系統指標
- 及時處理告警信息
- 定期備份重要數據

### **2. 自動化運維**
- 自動化日常運維任務
- 設置智能告警規則
- 實施自動故障恢復
- 建立運維知識庫

### **3. 容量管理**
- 監控資源使用趨勢
- 提前規劃容量擴展
- 優化資源配置
- 控制運維成本

### **4. 安全運維**
- 定期安全掃描
- 及時更新安全補丁
- 監控異常訪問
- 備份安全策略

## 🔧 **擴展和定制**

### **添加新的運維操作類型**
```python
class CustomOperationType(Enum):
    CUSTOM_MAINTENANCE = "custom_maintenance"

# 實現對應的運維方法
async def _execute_custom_maintenance(self, operation_id, config, logs, alerts):
    # 自定義運維邏輯
    pass
```

### **自定義告警規則**
```python
def add_custom_alert_rule(self, rule_name, condition, action):
    """添加自定義告警規則"""
    self.alert_rules.append({
        "name": rule_name,
        "condition": condition,
        "action": action
    })
```

## 🚨 **故障排除**

### **常見問題**

1. **操作超時**
   - 檢查網絡連接
   - 增加超時時間
   - 檢查系統負載

2. **權限不足**
   - 檢查操作權限
   - 驗證用戶角色
   - 查看審計日誌

3. **資源不足**
   - 檢查系統資源
   - 清理臨時文件
   - 優化資源配置

### **日誌分析**
```bash
# 查看運維日誌
grep "operation_id" /var/log/operations.log

# 分析失敗原因
grep "ERROR\|FAILED" /var/log/operations.log

# 監控系統指標
tail -f /var/log/system-metrics.log
```

## 📊 **運維指標和 KPI**

### **關鍵指標**
- **系統可用性** - 服務正常運行時間百分比
- **故障恢復時間** - 從故障發生到恢復的平均時間
- **運維效率** - 自動化運維任務比例
- **安全事件** - 安全漏洞和事件數量

### **性能指標**
- **響應時間** - 系統響應用戶請求的時間
- **吞吐量** - 系統處理請求的能力
- **資源利用率** - CPU、內存、磁盤使用效率
- **錯誤率** - 系統錯誤發生的頻率

## 🔗 **相關組件**

- **自動化驗證協調器** - 運維前驗證
- **部署 MCP** - 部署操作執行
- **Test Flow MCP** - 功能測試
- **監控系統** - 系統監控
- **告警系統** - 異常告警

