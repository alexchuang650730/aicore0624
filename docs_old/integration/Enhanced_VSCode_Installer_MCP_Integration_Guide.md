# Enhanced VSCode Installer MCP 集成使用指南

## 概述

Enhanced VSCode Installer MCP 是 PowerAutomation 中負責 VSCode 擴展安裝和管理的核心組件。通過集成 Human Loop MCP，我們可以在關鍵操作點引入人工決策，確保部署的安全性和可控性。

## 🎯 集成目標

### 主要使用場景
1. **生產環境部署確認** - 部署到生產環境前需要人工確認
2. **版本衝突解決** - 當檢測到版本衝突時請求人工選擇
3. **批量安裝策略** - 大量擴展安裝時的策略選擇
4. **錯誤恢復決策** - 安裝失敗時的恢復策略選擇
5. **配置參數確認** - 關鍵配置參數的人工驗證

### 集成原則
- **利用 AICore 現有能力** - 使用 AICore 的智能分析和決策功能
- **人機協作** - 在 AICore 不確定時引入人工判斷
- **非侵入性** - 不修改現有的核心邏輯
- **可配置** - 可以根據環境和策略啟用/禁用人工介入

## 🏗️ 集成架構

### 基本架構
```
Enhanced VSCode Installer MCP
├── AICore 智能分析 (現有功能)
│   ├── 環境檢測
│   ├── 版本分析
│   ├── 衝突檢測
│   └── 風險評估
├── Human Loop 集成 (新增)
│   ├── 確認對話框
│   ├── 選擇列表
│   ├── 參數輸入
│   └── 文件上傳
└── 執行引擎 (現有功能)
    ├── VSIX 安裝
    ├── 配置管理
    ├── 狀態監控
    └── 錯誤處理
```

### 決策流程
```
VSIX 部署請求
    ↓
AICore 環境分析
    ↓
風險評估 (AICore)
    ↓
是否需要人工介入？
├── 否 → 直接執行 (AICore)
└── 是 → Human Loop 交互
    ↓
用戶決策
    ↓
AICore 執行用戶決策
    ↓
返回結果
```

## 💻 實現方式

### 方式1: 繼承 HumanLoopIntegrationMixin (推薦)

```python
from PowerAutomation.components.human_loop_mcp_adapter import HumanLoopIntegrationMixin

class EnhancedVSCodeInstallerMCP(HumanLoopIntegrationMixin):
    """
    增強的 VSCode Installer MCP，集成 Human Loop 功能
    """
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.workflow_id = "vscode_installer_workflow"
        
        # AICore 相關配置 (使用現有功能)
        self.aicore_enabled = True
        self.risk_threshold = 0.7  # 風險閾值
        self.auto_approve_dev = True  # 開發環境自動批准
    
    async def deploy_vsix(self, vsix_path: str, target_environment: str = "development", 
                         options: dict = None) -> dict:
        """
        部署 VSIX 擴展
        
        Args:
            vsix_path: VSIX 文件路徑
            target_environment: 目標環境 (development/staging/production)
            options: 部署選項
            
        Returns:
            部署結果
        """
        options = options or {}
        
        # 1. 使用 AICore 進行環境分析
        analysis_result = await self._aicore_analyze_environment(
            vsix_path, target_environment, options
        )
        
        # 2. 使用 AICore 進行風險評估
        risk_assessment = await self._aicore_assess_risk(
            analysis_result, target_environment
        )
        
        # 3. 決定是否需要人工介入
        if await self._should_request_human_approval(risk_assessment, target_environment):
            # 請求人工確認
            approval_result = await self._request_deployment_approval(
                vsix_path, target_environment, analysis_result, risk_assessment
            )
            
            if not approval_result.get("approved"):
                return {
                    "success": False,
                    "reason": "deployment_cancelled",
                    "message": approval_result.get("message", "用戶取消部署"),
                    "user_decision": approval_result
                }
            
            # 用戶可能修改了部署參數
            if approval_result.get("modified_options"):
                options.update(approval_result["modified_options"])
                target_environment = approval_result.get("target_environment", target_environment)
        
        # 4. 使用 AICore 執行部署
        return await self._aicore_execute_deployment(
            vsix_path, target_environment, options, risk_assessment
        )
    
    async def _should_request_human_approval(self, risk_assessment: dict, 
                                           environment: str) -> bool:
        """
        使用 AICore 決定是否需要人工批准
        """
        # 生產環境總是需要確認
        if environment == "production":
            return True
        
        # 高風險操作需要確認
        if risk_assessment.get("risk_score", 0) > self.risk_threshold:
            return True
        
        # 檢測到衝突需要確認
        if risk_assessment.get("conflicts"):
            return True
        
        # 關鍵配置變更需要確認
        if risk_assessment.get("critical_changes"):
            return True
        
        return False
    
    async def _request_deployment_approval(self, vsix_path: str, environment: str,
                                         analysis: dict, risk: dict) -> dict:
        """
        請求部署批准
        """
        # 構建確認消息
        message = self._build_approval_message(vsix_path, environment, analysis, risk)
        
        # 構建選項
        options = [
            {"value": "approve", "label": "批准部署"},
            {"value": "cancel", "label": "取消部署"}
        ]
        
        # 如果是生產環境，提供降級選項
        if environment == "production":
            options.insert(1, {"value": "staging", "label": "改為部署到預發環境"})
        
        # 如果有衝突，提供解決選項
        if risk.get("conflicts"):
            options.insert(-1, {"value": "resolve", "label": "解決衝突後部署"})
        
        # 請求人工確認
        confirmation_result = await self.request_human_confirmation(
            title=f"VSIX 部署確認 - {environment.upper()}",
            message=message,
            options=options,
            timeout=600  # 10分鐘超時
        )
        
        if not confirmation_result.get("success"):
            return {
                "approved": False,
                "message": "確認請求失敗或超時",
                "error": confirmation_result.get("error")
            }
        
        user_choice = confirmation_result.get("response", {}).get("choice")
        
        if user_choice == "approve":
            return {"approved": True, "choice": "approve"}
        elif user_choice == "staging":
            return {
                "approved": True,
                "choice": "staging",
                "target_environment": "staging",
                "message": "用戶選擇部署到預發環境"
            }
        elif user_choice == "resolve":
            # 請求衝突解決策略
            return await self._request_conflict_resolution(risk.get("conflicts"))
        else:  # cancel
            return {
                "approved": False,
                "choice": "cancel",
                "message": "用戶取消部署"
            }
    
    async def _request_conflict_resolution(self, conflicts: list) -> dict:
        """
        請求衝突解決策略
        """
        conflict_descriptions = []
        for conflict in conflicts:
            conflict_descriptions.append(
                f"• {conflict.get('type')}: {conflict.get('description')}"
            )
        
        message = f"檢測到以下衝突:\n\n" + "\n".join(conflict_descriptions) + "\n\n請選擇解決策略:"
        
        options = [
            {"value": "force", "label": "強制覆蓋 (風險較高)"},
            {"value": "backup", "label": "備份後覆蓋 (推薦)"},
            {"value": "skip", "label": "跳過衝突項目"},
            {"value": "cancel", "label": "取消部署"}
        ]
        
        resolution_result = await self.request_human_selection(
            title="衝突解決策略",
            message=message,
            options=options,
            timeout=300
        )
        
        if not resolution_result.get("success"):
            return {"approved": False, "message": "衝突解決請求失敗"}
        
        strategy = resolution_result.get("response", {}).get("choice")
        
        if strategy == "cancel":
            return {"approved": False, "message": "用戶取消部署"}
        else:
            return {
                "approved": True,
                "choice": "resolve",
                "modified_options": {"conflict_resolution": strategy},
                "message": f"用戶選擇衝突解決策略: {strategy}"
            }
    
    def _build_approval_message(self, vsix_path: str, environment: str,
                              analysis: dict, risk: dict) -> str:
        """
        構建批准確認消息
        """
        message_parts = [
            f"準備部署 VSIX 擴展到 {environment.upper()} 環境",
            f"",
            f"📦 擴展信息:",
            f"  • 文件: {vsix_path}",
            f"  • 版本: {analysis.get('version', 'Unknown')}",
            f"  • 大小: {analysis.get('size', 'Unknown')}",
            f"",
            f"🎯 目標環境:",
            f"  • 環境: {environment}",
            f"  • VSCode 版本: {analysis.get('vscode_version', 'Unknown')}",
            f"",
            f"⚠️ 風險評估:",
            f"  • 風險等級: {risk.get('risk_level', 'Unknown')}",
            f"  • 風險分數: {risk.get('risk_score', 0):.2f}",
        ]
        
        # 添加衝突信息
        if risk.get("conflicts"):
            message_parts.extend([
                f"",
                f"🔥 檢測到衝突:",
            ])
            for conflict in risk["conflicts"]:
                message_parts.append(f"  • {conflict.get('description')}")
        
        # 添加關鍵變更信息
        if risk.get("critical_changes"):
            message_parts.extend([
                f"",
                f"🚨 關鍵變更:",
            ])
            for change in risk["critical_changes"]:
                message_parts.append(f"  • {change}")
        
        message_parts.extend([
            f"",
            f"確定要繼續部署嗎？"
        ])
        
        return "\n".join(message_parts)
    
    # AICore 集成方法 (使用現有功能)
    async def _aicore_analyze_environment(self, vsix_path: str, environment: str, 
                                        options: dict) -> dict:
        """
        使用 AICore 分析部署環境
        """
        # 這裡調用 AICore 的現有環境分析功能
        # 實際實現會調用 AICore 的 API 或方法
        
        # 模擬 AICore 分析結果
        return {
            "vsix_path": vsix_path,
            "environment": environment,
            "version": "3.0.0",
            "size": "2.5MB",
            "vscode_version": "1.85.0",
            "dependencies": ["extension-a", "extension-b"],
            "permissions": ["file-system", "network"],
            "analysis_timestamp": "2024-06-24T12:00:00Z"
        }
    
    async def _aicore_assess_risk(self, analysis: dict, environment: str) -> dict:
        """
        使用 AICore 評估部署風險
        """
        # 這裡調用 AICore 的現有風險評估功能
        
        # 模擬風險評估結果
        risk_score = 0.3  # 基礎風險
        
        # 生產環境風險更高
        if environment == "production":
            risk_score += 0.4
        
        # 檢查是否有衝突
        conflicts = []
        if analysis.get("dependencies"):
            # 模擬檢測到依賴衝突
            conflicts.append({
                "type": "dependency_conflict",
                "description": "extension-a 版本衝突 (當前: 1.0.0, 需要: 2.0.0)"
            })
            risk_score += 0.2
        
        # 檢查關鍵變更
        critical_changes = []
        if "file-system" in analysis.get("permissions", []):
            critical_changes.append("需要文件系統訪問權限")
            risk_score += 0.1
        
        risk_level = "low"
        if risk_score > 0.7:
            risk_level = "high"
        elif risk_score > 0.4:
            risk_level = "medium"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "conflicts": conflicts if conflicts else None,
            "critical_changes": critical_changes if critical_changes else None,
            "assessment_timestamp": "2024-06-24T12:00:00Z"
        }
    
    async def _aicore_execute_deployment(self, vsix_path: str, environment: str,
                                       options: dict, risk_assessment: dict) -> dict:
        """
        使用 AICore 執行實際部署
        """
        # 這裡調用 AICore 的現有部署功能
        
        # 模擬部署過程
        import asyncio
        await asyncio.sleep(2)  # 模擬部署時間
        
        return {
            "success": True,
            "deployment_id": f"deploy_{int(asyncio.get_event_loop().time())}",
            "vsix_path": vsix_path,
            "environment": environment,
            "version": "3.0.0",
            "status": "deployed",
            "deployment_time": "2024-06-24T12:02:00Z",
            "risk_assessment": risk_assessment,
            "options_used": options
        }
```

### 方式2: 直接使用客戶端

```python
from PowerAutomation.components.human_loop_mcp_adapter import HumanLoopMCPClient

class EnhancedVSCodeInstallerMCPDirect:
    """
    使用直接客戶端方式的 VSCode Installer MCP
    """
    
    def __init__(self, mcp_url="http://localhost:8096"):
        self.human_loop_client = HumanLoopMCPClient(mcp_url)
        self.workflow_id = "vscode_installer_direct"
    
    async def install_extension_batch(self, extensions: list) -> dict:
        """
        批量安裝擴展，請求人工選擇安裝策略
        """
        if len(extensions) > 10:  # 大批量安裝
            # 請求安裝策略
            strategy_session = await self.human_loop_client.create_interaction_session({
                "interaction_type": "selection",
                "title": f"批量安裝策略 ({len(extensions)} 個擴展)",
                "message": f"即將安裝 {len(extensions)} 個 VSCode 擴展，請選擇安裝策略:",
                "options": [
                    {"value": "sequential", "label": "順序安裝 (穩定但較慢)"},
                    {"value": "parallel", "label": "並行安裝 (快速但可能有衝突)"},
                    {"value": "batch", "label": "分批安裝 (平衡方案)"},
                    {"value": "selective", "label": "選擇性安裝 (手動選擇)"}
                ],
                "timeout": 300
            })
            
            if strategy_session.get("success"):
                session_id = strategy_session.get("session_id")
                response = await self.human_loop_client.wait_for_user_response(session_id)
                
                if response.get("success"):
                    strategy = response.get("response", {}).get("choice", "sequential")
                    return await self._execute_installation_strategy(extensions, strategy)
        
        # 默認順序安裝
        return await self._execute_installation_strategy(extensions, "sequential")
```

## 🚀 使用示例

### 基本使用
```python
# 初始化組件
installer = EnhancedVSCodeInstallerMCP()

# 部署到開發環境 (通常不需要人工確認)
dev_result = await installer.deploy_vsix(
    "powerautomation-3.0.0.vsix",
    "development"
)

# 部署到生產環境 (會請求人工確認)
prod_result = await installer.deploy_vsix(
    "powerautomation-3.0.0.vsix", 
    "production"
)
```

### 高級使用
```python
# 帶選項的部署
result = await installer.deploy_vsix(
    "powerautomation-3.0.0.vsix",
    "production",
    options={
        "backup_existing": True,
        "rollback_on_failure": True,
        "notification_channels": ["slack", "email"]
    }
)

# 批量安裝
extensions = [
    "ms-python.python",
    "ms-vscode.vscode-typescript-next",
    "esbenp.prettier-vscode"
]
batch_result = await installer.install_extension_batch(extensions)
```

## 📋 配置選項

### 環境變量
```bash
# Human Loop MCP 服務 URL
export HUMAN_LOOP_MCP_URL="http://localhost:8096"

# 啟用/禁用人工介入
export HUMAN_LOOP_ENABLED="true"

# 風險閾值設置
export RISK_THRESHOLD="0.7"

# 自動批准開發環境
export AUTO_APPROVE_DEV="true"
```

### 配置文件
```yaml
# vscode_installer_config.yaml
human_loop:
  enabled: true
  mcp_url: "http://localhost:8096"
  timeout: 600
  
risk_assessment:
  threshold: 0.7
  auto_approve_dev: true
  require_approval_production: true
  
deployment:
  backup_existing: true
  rollback_on_failure: true
  max_parallel_installs: 5
```

## 🔍 監控和日誌

### 日誌示例
```
[2024-06-24 12:00:00] INFO: 開始部署 VSIX: powerautomation-3.0.0.vsix
[2024-06-24 12:00:01] INFO: AICore 環境分析完成，風險分數: 0.8
[2024-06-24 12:00:02] INFO: 創建人工確認會話: session-12345
[2024-06-24 12:05:30] INFO: 用戶確認部署，選擇: approve
[2024-06-24 12:05:31] INFO: 開始執行部署...
[2024-06-24 12:07:45] INFO: 部署完成，ID: deploy_1719230865
```

### 監控指標
- 部署成功率
- 人工介入頻率
- 平均確認時間
- 風險評估準確性
- 用戶決策分布

這就是 Enhanced VSCode Installer MCP 的完整集成使用方式！接下來我將介紹 General Processor MCP 的集成方式。

