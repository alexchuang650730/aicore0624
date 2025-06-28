# 通用部署 MCP (Deployment MCP)

## 🎯 **核心功能**

專門負責執行各種類型的部署操作，與自動化驗證協調器配合，確保部署前已通過驗證。

## 🚀 **支持的部署類型**

- **Web Application** - Web 應用程序部署
- **API Service** - API 服務部署
- **Database** - 數據庫部署
- **Microservice** - 微服務部署
- **Static Site** - 靜態網站部署
- **Container** - 容器化應用部署
- **Serverless** - 無服務器函數部署

## 📋 **支持的部署策略**

### 🔵 **藍綠部署 (Blue-Green)**
- 零停機部署
- 快速回滾能力
- 適用於生產環境

### 🔄 **滾動更新 (Rolling Update)**
- 逐步替換實例
- 保持服務可用性
- 適用於多實例服務

### 🐤 **金絲雀部署 (Canary)**
- 小流量驗證
- 風險控制
- 適用於新功能發布

### 🔄 **重建部署 (Recreate)**
- 簡單直接
- 短暫停機
- 適用於開發環境

### 🧪 **A/B 測試部署**
- 並行版本測試
- 數據驅動決策
- 適用於功能驗證

## 🛠️ **使用方法**

### **CLI 接口**

```bash
# 部署 Web 應用（藍綠策略）
python main.py deploy \
  --name "my-web-app" \
  --type "web_application" \
  --strategy "blue_green" \
  --source "/path/to/app" \
  --environment "production" \
  --version "v1.2.0" \
  --replicas 3

# 部署 API 服務（滾動更新）
python main.py deploy \
  --name "user-api" \
  --type "api_service" \
  --strategy "rolling_update" \
  --source "/path/to/api" \
  --environment "staging" \
  --version "v2.1.0" \
  --replicas 5

# 查看部署歷史
python main.py history

# 查看活躍部署
python main.py status

# 回滾部署
python main.py rollback --deployment-id "my-web-app_1750966000"
```

### **Python API**

```python
from main import DeploymentMCP, DeploymentConfig, DeploymentType, DeploymentStrategy

# 創建部署 MCP 實例
deployment_mcp = DeploymentMCP()

# 配置部署
config = DeploymentConfig(
    name="my-service",
    type=DeploymentType.API_SERVICE,
    strategy=DeploymentStrategy.BLUE_GREEN,
    source_path="/path/to/service",
    target_environment="production",
    version="v1.0.0",
    replicas=3,
    health_check_url="http://my-service/health",
    rollback_enabled=True
)

# 執行部署
result = await deployment_mcp.deploy(config)
print(f"部署狀態: {result.status}")
print(f"部署端點: {result.endpoints}")
```

## ⚙️ **配置選項**

### **部署配置 (DeploymentConfig)**

```python
@dataclass
class DeploymentConfig:
    name: str                    # 部署名稱
    type: DeploymentType        # 部署類型
    strategy: DeploymentStrategy # 部署策略
    source_path: str            # 源代碼路徑
    target_environment: str     # 目標環境
    version: str                # 版本號
    replicas: int = 1           # 副本數量
    health_check_url: str = None # 健康檢查 URL
    rollback_enabled: bool = True # 是否啟用回滾
    timeout: int = 600          # 超時時間（秒）
    environment_variables: Dict = None # 環境變量
    dependencies: List[str] = None     # 依賴服務
```

### **系統配置**

```json
{
  "deployment_root": "/tmp/deployments",
  "backup_root": "/tmp/deployment_backups",
  "max_concurrent_deployments": 3,
  "default_timeout": 600,
  "health_check_timeout": 120,
  "rollback_retention_days": 30
}
```

## 🔄 **部署流程**

1. **驗證配置** - 檢查部署配置的有效性
2. **並發檢查** - 確保不超過最大並發部署限制
3. **創建快照** - 為回滾創建當前狀態快照
4. **執行策略** - 根據選擇的策略執行部署
5. **健康檢查** - 驗證部署後的服務健康狀態
6. **記錄歷史** - 保存部署結果和日誌

## 🔒 **安全特性**

- **回滾機制** - 自動和手動回滾支持
- **健康檢查** - 部署後自動驗證服務狀態
- **並發控制** - 防止過多並發部署影響系統
- **操作日誌** - 完整的部署過程記錄
- **快照備份** - 部署前狀態保存

## 🎯 **與 PowerAutomation 集成**

### **與驗證協調器配合**
```python
# 部署前自動調用驗證協調器
verification_result = await verification_coordinator.coordinate_verification(
    "deployment", deployment_context
)

if verification_result["overall_status"] == "PASSED":
    # 執行部署
    deployment_result = await deployment_mcp.deploy(config)
else:
    # 阻止部署
    raise Exception("部署前驗證失敗")
```

### **質量門禁遵循**
- ✅ 部署前強制驗證
- ✅ 失敗自動回滾
- ✅ 完整操作追蹤
- ✅ 「若交付不成功，不同意離開」

## 📊 **監控和告警**

- **部署狀態監控** - 實時跟蹤部署進度
- **性能指標收集** - 部署後系統性能監控
- **異常告警** - 部署失敗或異常自動告警
- **歷史分析** - 部署成功率和趨勢分析

## 🔧 **擴展和定制**

### **添加新的部署類型**
```python
class CustomDeploymentType(Enum):
    CUSTOM_APP = "custom_app"

# 實現對應的部署方法
async def _deploy_custom_app(self, deployment_id, config, logs):
    # 自定義部署邏輯
    pass
```

### **添加新的部署策略**
```python
async def _deploy_custom_strategy(self, deployment_id, config, logs):
    # 自定義策略邏輯
    pass
```

## 🚨 **故障排除**

### **常見問題**

1. **部署超時**
   - 檢查網絡連接
   - 增加超時時間
   - 檢查資源可用性

2. **健康檢查失敗**
   - 驗證健康檢查 URL
   - 檢查服務啟動時間
   - 查看應用日誌

3. **回滾失敗**
   - 檢查快照完整性
   - 驗證回滾權限
   - 手動恢復備份

### **日誌分析**
```bash
# 查看部署日誌
grep "deployment_id" /var/log/deployment.log

# 分析失敗原因
grep "ERROR\|FAILED" /var/log/deployment.log
```

## 📈 **最佳實踐**

1. **選擇合適的部署策略**
   - 生產環境：藍綠或金絲雀
   - 測試環境：滾動更新或重建
   - 開發環境：重建

2. **設置健康檢查**
   - 提供準確的健康檢查端點
   - 設置合理的檢查超時時間
   - 包含關鍵依賴檢查

3. **啟用回滾機制**
   - 始終啟用自動回滾
   - 定期測試回滾流程
   - 保持足夠的備份保留期

4. **監控部署指標**
   - 跟蹤部署成功率
   - 監控部署時間
   - 分析失敗原因

## 🔗 **相關組件**

- **自動化驗證協調器** - 部署前驗證
- **運維 MCP** - 部署後運維
- **Test Flow MCP** - 功能測試
- **監控系統** - 部署監控

