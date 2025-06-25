# AICore Human-in-the-Loop Integration System 完整指南

## 🎯 系統概述

AICore Human-in-the-Loop Integration System 是一個智能化的人機協作平台，整合了動態路由、專家調用、深度測試和增量優化功能，實現了與Human Loop MCP的無縫集成。

### 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                    AICore Master Controller                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Dynamic   │  │   Expert    │  │   Testing   │         │
│  │   Router    │  │   System    │  │  Framework  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │Optimization │  │ Human Loop  │  │  Web API    │         │
│  │   System    │  │    MCP      │  │   Server    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速開始

### 1. 系統部署

```bash
# 克隆項目
git clone https://github.com/alexchuang650730/aicore0624.git
cd aicore0624

# 執行部署腳本
chmod +x deploy_aicore_system.sh
./deploy_aicore_system.sh
```

### 2. 啟動系統

```bash
# 啟動AICore系統
./start_aicore.sh

# 檢查系統狀態
./check_aicore_status.sh
```

### 3. 驗證安裝

```bash
# 健康檢查
curl http://localhost:8098/api/health

# 系統狀態
curl http://localhost:8098/api/status
```

## 📋 核心組件詳解

### 1. 動態路由系統 (AICore Dynamic Router)

**功能**: 智能決策工作流處理方式
- 自動處理 (Automatic)
- 人工介入 (Human Required)
- 專家諮詢 (Expert Consultation)
- 條件處理 (Conditional)

**配置示例**:
```yaml
components:
  router:
    enabled: true
    confidence_threshold: 0.7
    fallback_strategy: "human_intervention"
```

**使用方式**:
```python
from aicore_dynamic_router import AICoreDynamicRouter, RoutingContext

router = AICoreDynamicRouter()
context = RoutingContext(
    request_id="req_001",
    workflow_id="wf_001",
    operation_type="deployment",
    metadata={"complexity": "high", "risk_level": "medium"}
)

decision = await router.route_request(context)
print(f"路由決策: {decision.decision_type}")
```

### 2. 專家調用機制 (Expert Invocation System)

**功能**: 智能專家系統調用和管理
- 技術專家 (Technical Expert)
- API專家 (API Expert)
- 業務專家 (Business Expert)
- 數據專家 (Data Expert)
- 集成專家 (Integration Expert)
- 安全專家 (Security Expert)
- 性能專家 (Performance Expert)

**使用示例**:
```python
from expert_invocation_system import ExpertInvocationSystem, ConsultationRequest, ExpertType

expert_system = ExpertInvocationSystem()
request = ConsultationRequest(
    request_id="expert_001",
    workflow_id="wf_001",
    expert_type=ExpertType.TECHNICAL,
    title="部署風險評估",
    description="評估生產環境部署的技術風險",
    context={"environment": "production", "version": "2.1.0"}
)

consultation_id = await expert_system.request_consultation(request)
```

### 3. 深度測試框架 (Deep Testing Framework)

**功能**: 全面的系統測試和驗證
- 單元測試 (Unit Tests)
- 集成測試 (Integration Tests)
- 性能測試 (Performance Tests)
- 安全測試 (Security Tests)
- 負載測試 (Load Tests)

**測試執行**:
```python
from deep_testing_framework import DeepTestingFramework

testing_framework = DeepTestingFramework()

# 運行所有測試
results = await testing_framework.run_all_tests()

# 生成報告
report = testing_framework.generate_report("json")
```

### 4. 增量優化系統 (Incremental Optimization System)

**功能**: 持續學習和系統優化
- 路由決策優化
- 性能指標收集
- 模型訓練和更新
- 預測分析

**優化配置**:
```yaml
components:
  optimization_system:
    enabled: true
    learning_rate: 0.01
    optimization_interval: 3600
    model_save_path: "data/models"
```

### 5. Human Loop MCP 集成

**功能**: 無縫的人機交互
- 會話管理
- 多種交互類型
- 超時處理
- 狀態追蹤

**MCP集成示例**:
```python
from aicore_master_system import HumanLoopMCPClient

async with HumanLoopMCPClient("http://localhost:8096") as client:
    session_id = await client.create_session({
        "interaction_data": {
            "interaction_type": "approval",
            "title": "部署確認",
            "message": "是否確認部署到生產環境？",
            "timeout": 300
        }
    })
    
    response = await client.wait_for_response(session_id)
```

## 🔧 工作流管理

### 創建工作流

```bash
curl -X POST http://localhost:8098/api/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "deployment",
    "title": "生產環境部署",
    "description": "部署應用到生產環境",
    "parameters": {
      "environment": "production",
      "version": "2.1.0",
      "rollback_enabled": true
    },
    "metadata": {
      "complexity": "high",
      "risk_level": "medium",
      "estimated_duration": 1800
    },
    "timeout": 3600
  }'
```

### 查詢工作流狀態

```bash
curl http://localhost:8098/api/workflows/{workflow_id}
```

### 工作流類型

1. **DEPLOYMENT** - 部署工作流
2. **CONFIGURATION** - 配置工作流
3. **MAINTENANCE** - 維護工作流
4. **MONITORING** - 監控工作流
5. **TESTING** - 測試工作流
6. **OPTIMIZATION** - 優化工作流

## 📊 監控和分析

### 系統狀態監控

```python
# 獲取系統狀態
status = controller.get_system_status()
print(f"系統狀態: {status['system']['status']}")
print(f"運行時間: {status['system']['uptime_seconds']}秒")
print(f"活動工作流: {status['workflows']['active_count']}")
```

### 性能指標

```python
# 收集性能指標
optimization_system.collect_performance_metric(
    metric_id="api_response_time",
    metric_type="latency",
    value=150.5,
    context={"endpoint": "/api/workflows"}
)
```

### 健康檢查

```bash
# API健康檢查
curl http://localhost:8098/api/health

# 系統組件健康檢查
./check_aicore_status.sh
```

## 🔒 安全配置

### API安全

```yaml
security:
  api_key_required: true
  rate_limiting: true
  max_requests_per_minute: 100
  cors_enabled: true
  allowed_origins: ["https://yourdomain.com"]
```

### 數據庫安全

```yaml
database:
  url: "postgresql://user:password@localhost/aicore"
  ssl_mode: "require"
  connection_timeout: 30
```

## 🛠️ 自定義和擴展

### 添加新的專家類型

```python
class CustomExpertType(Enum):
    CUSTOM_EXPERT = "custom_expert"

# 註冊自定義專家
expert_system.register_expert_type(
    expert_type=CustomExpertType.CUSTOM_EXPERT,
    handler=custom_expert_handler
)
```

### 自定義路由策略

```python
class CustomRoutingStrategy:
    async def evaluate(self, context: RoutingContext) -> RoutingDecision:
        # 自定義路由邏輯
        if context.metadata.get("priority") == "urgent":
            return RoutingDecision(
                decision_type=DecisionType.HUMAN_REQUIRED,
                confidence=0.9,
                reasoning="緊急請求需要人工處理"
            )
        return await self.default_strategy(context)

# 註冊自定義策略
router.register_strategy("custom", CustomRoutingStrategy())
```

### 添加新的測試類型

```python
class CustomTestSuite(TestSuite):
    async def run_custom_tests(self):
        # 自定義測試邏輯
        pass

# 註冊測試套件
testing_framework.register_test_suite("custom", CustomTestSuite())
```

## 📈 優化建議

### 性能優化

1. **數據庫優化**
   - 使用連接池
   - 添加適當索引
   - 定期清理歷史數據

2. **緩存策略**
   - Redis緩存熱點數據
   - 路由決策緩存
   - 專家回應緩存

3. **並發處理**
   - 調整工作線程數
   - 使用異步處理
   - 實現請求隊列

### 可靠性提升

1. **錯誤處理**
   - 實現重試機制
   - 添加熔斷器
   - 優雅降級

2. **監控告警**
   - 設置關鍵指標告警
   - 日誌聚合分析
   - 健康檢查自動化

3. **備份恢復**
   - 定期數據備份
   - 配置文件版本控制
   - 災難恢復計劃

## 🔧 故障排除

### 常見問題

1. **系統無法啟動**
   ```bash
   # 檢查Python環境
   python3 --version
   source venv/bin/activate
   
   # 檢查依賴
   pip list
   
   # 檢查配置文件
   cat config/aicore_config.yaml
   ```

2. **API無響應**
   ```bash
   # 檢查端口占用
   lsof -i :8098
   
   # 檢查進程狀態
   ps aux | grep aicore
   
   # 查看日誌
   tail -f logs/aicore_system.log
   ```

3. **MCP連接失敗**
   ```bash
   # 檢查MCP服務
   curl http://localhost:8096/api/health
   
   # 檢查網路連接
   telnet localhost 8096
   ```

4. **數據庫錯誤**
   ```bash
   # 檢查數據庫文件
   ls -la data/aicore.db
   
   # 檢查權限
   chmod 644 data/aicore.db
   
   # 重新初始化
   python3 init_database.py
   ```

### 日誌分析

```bash
# 查看錯誤日誌
grep "ERROR" logs/aicore_system.log

# 查看警告日誌
grep "WARNING" logs/aicore_system.log

# 實時監控日誌
tail -f logs/aicore_system.log | grep -E "(ERROR|WARNING)"
```

## 📚 API參考

### 健康檢查
- **GET** `/api/health` - 系統健康檢查

### 系統狀態
- **GET** `/api/status` - 獲取系統狀態

### 工作流管理
- **POST** `/api/workflows` - 創建工作流
- **GET** `/api/workflows/{id}` - 獲取工作流狀態
- **DELETE** `/api/workflows/{id}` - 取消工作流

### 測試執行
- **POST** `/api/tests/run` - 運行系統測試
- **GET** `/api/tests/results` - 獲取測試結果

### 專家諮詢
- **POST** `/api/experts/consult` - 請求專家諮詢
- **GET** `/api/experts/consultations/{id}` - 獲取諮詢狀態

## 🎯 最佳實踐

### 工作流設計

1. **明確的工作流定義**
   - 清晰的標題和描述
   - 完整的參數定義
   - 適當的超時設置

2. **合理的路由策略**
   - 基於複雜度的路由
   - 風險評估導向
   - 性能考量

3. **有效的錯誤處理**
   - 詳細的錯誤信息
   - 自動重試機制
   - 優雅降級

### 系統維護

1. **定期備份**
   - 數據庫備份
   - 配置文件備份
   - 日誌歸檔

2. **性能監控**
   - 關鍵指標監控
   - 趨勢分析
   - 容量規劃

3. **安全更新**
   - 依賴包更新
   - 安全補丁
   - 配置審查

## 🚀 未來發展

### 計劃功能

1. **增強的AI能力**
   - 更智能的路由決策
   - 自動化專家選擇
   - 預測性維護

2. **更豐富的集成**
   - 更多MCP適配器
   - 第三方服務集成
   - 雲原生支持

3. **高級分析**
   - 實時儀表板
   - 預測分析
   - 業務智能

### 社區貢獻

歡迎貢獻代碼、文檔和想法！

- GitHub: https://github.com/alexchuang650730/aicore0624
- Issues: 報告問題和建議
- Pull Requests: 提交代碼改進

---

## 📞 支持和聯繫

如果您在使用過程中遇到問題或有任何建議，請通過以下方式聯繫我們：

- 📧 Email: support@aicore.dev
- 💬 Discord: AICore Community
- 📖 文檔: https://docs.aicore.dev
- 🐛 問題報告: https://github.com/alexchuang650730/aicore0624/issues

感謝您使用AICore Human-in-the-Loop Integration System！🎉

