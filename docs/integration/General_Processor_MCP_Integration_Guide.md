# General Processor MCP 集成使用指南

## 概述

General Processor MCP 是 PowerAutomation 中的通用任務處理器，負責處理各種類型的自動化任務。通過集成 Human Loop MCP，我們可以在處理複雜任務時引入人工智慧，確保任務處理的準確性和適應性。

## 🎯 集成目標

### 主要使用場景
1. **複雜任務策略選擇** - 高複雜度任務的處理策略決策
2. **異常情況處理** - 任務執行異常時的恢復策略
3. **資源分配決策** - 大型任務的資源分配策略
4. **優先級調整** - 任務隊列的優先級動態調整
5. **品質控制檢查** - 任務結果的人工品質驗證
6. **參數優化** - 任務參數的人工調優

### 集成原則
- **智能分流** - 使用 AICore 評估任務複雜度，決定是否需要人工介入
- **策略選擇** - 在多種處理策略中請求人工選擇最佳方案
- **異常處理** - 自動處理失敗時的人工決策支持
- **學習優化** - 收集人工決策數據，優化 AICore 的自動決策能力

## 🏗️ 集成架構

### 基本架構
```
General Processor MCP
├── 任務分析器 (AICore)
│   ├── 複雜度評估
│   ├── 資源需求分析
│   ├── 風險評估
│   └── 策略推薦
├── Human Loop 決策器 (新增)
│   ├── 策略選擇
│   ├── 參數確認
│   ├── 異常處理
│   └── 品質檢查
├── 執行引擎 (AICore)
│   ├── 任務調度
│   ├── 資源管理
│   ├── 進度監控
│   └── 結果收集
└── 學習系統 (AICore)
    ├── 決策記錄
    ├── 模式識別
    ├── 策略優化
    └── 性能提升
```

### 決策流程
```
任務請求
    ↓
AICore 任務分析
    ↓
複雜度 & 風險評估
    ↓
需要人工介入？
├── 否 → AICore 自動處理
└── 是 → Human Loop 決策
    ├── 策略選擇
    ├── 參數確認
    └── 執行批准
    ↓
AICore 執行決策
    ↓
結果驗證
    ↓
需要人工檢查？
├── 否 → 返回結果
└── 是 → Human Loop 品質檢查
    ↓
最終結果
```

## 💻 實現方式

### 方式1: 繼承 HumanLoopIntegrationMixin (推薦)

```python
from PowerAutomation.components.human_loop_mcp_adapter import HumanLoopIntegrationMixin
import asyncio
from typing import Dict, List, Any, Optional
from enum import Enum

class TaskComplexity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class GeneralProcessorMCP(HumanLoopIntegrationMixin):
    """
    通用任務處理器，集成 Human Loop 功能
    """
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.workflow_id = "general_processor_workflow"
        
        # AICore 相關配置
        self.complexity_threshold = 0.7  # 複雜度閾值
        self.auto_retry_limit = 3  # 自動重試次數
        self.human_intervention_enabled = True
        
        # 任務隊列
        self.task_queue = []
        self.processing_tasks = {}
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理單個任務
        
        Args:
            task_data: 任務數據
            
        Returns:
            處理結果
        """
        task_id = task_data.get("task_id", f"task_{int(asyncio.get_event_loop().time())}")
        
        try:
            # 1. 使用 AICore 分析任務
            analysis_result = await self._aicore_analyze_task(task_data)
            
            # 2. 評估是否需要人工介入
            intervention_needed = await self._should_request_human_intervention(
                task_data, analysis_result
            )
            
            if intervention_needed:
                # 3. 請求人工決策
                human_decision = await self._request_task_processing_strategy(
                    task_data, analysis_result
                )
                
                if not human_decision.get("approved"):
                    return {
                        "success": False,
                        "task_id": task_id,
                        "status": TaskStatus.CANCELLED.value,
                        "reason": "human_cancelled",
                        "message": human_decision.get("message", "用戶取消任務")
                    }
                
                # 應用人工決策
                processing_strategy = human_decision.get("strategy", "default")
                processing_params = human_decision.get("params", {})
            else:
                # 使用 AICore 推薦的策略
                processing_strategy = analysis_result.get("recommended_strategy", "default")
                processing_params = analysis_result.get("recommended_params", {})
            
            # 4. 使用 AICore 執行任務
            execution_result = await self._aicore_execute_task(
                task_data, processing_strategy, processing_params, analysis_result
            )
            
            # 5. 檢查是否需要品質驗證
            if await self._should_request_quality_check(execution_result, analysis_result):
                quality_check = await self._request_quality_verification(
                    task_data, execution_result
                )
                
                if not quality_check.get("approved"):
                    # 品質檢查失敗，請求處理策略
                    retry_decision = await self._request_retry_strategy(
                        task_data, execution_result, quality_check
                    )
                    
                    if retry_decision.get("retry"):
                        # 重新處理
                        return await self.process_task({
                            **task_data,
                            "retry_count": task_data.get("retry_count", 0) + 1,
                            "previous_result": execution_result,
                            "quality_feedback": quality_check
                        })
                    else:
                        return {
                            "success": False,
                            "task_id": task_id,
                            "status": TaskStatus.FAILED.value,
                            "reason": "quality_check_failed",
                            "execution_result": execution_result,
                            "quality_check": quality_check
                        }
                
                # 品質檢查通過，更新結果
                execution_result["quality_verified"] = True
                execution_result["quality_check"] = quality_check
            
            return {
                "success": True,
                "task_id": task_id,
                "status": TaskStatus.COMPLETED.value,
                "result": execution_result,
                "processing_strategy": processing_strategy,
                "human_intervention": intervention_needed
            }
            
        except Exception as e:
            # 異常處理
            return await self._handle_task_exception(task_data, str(e))
    
    async def process_batch_tasks(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量處理任務
        """
        if len(tasks) > 20:  # 大批量任務
            # 請求批量處理策略
            batch_strategy = await self._request_batch_processing_strategy(tasks)
            
            if not batch_strategy.get("approved"):
                return {
                    "success": False,
                    "reason": "batch_cancelled",
                    "message": "用戶取消批量處理"
                }
            
            strategy = batch_strategy.get("strategy", "sequential")
            max_parallel = batch_strategy.get("max_parallel", 5)
            
            return await self._execute_batch_strategy(tasks, strategy, max_parallel)
        else:
            # 小批量，直接順序處理
            return await self._execute_batch_strategy(tasks, "sequential", 1)
    
    async def _should_request_human_intervention(self, task_data: Dict[str, Any],
                                               analysis: Dict[str, Any]) -> bool:
        """
        使用 AICore 決定是否需要人工介入
        """
        # 高複雜度任務
        if analysis.get("complexity_score", 0) > self.complexity_threshold:
            return True
        
        # 關鍵任務
        if task_data.get("priority") == "critical":
            return True
        
        # 新類型任務 (AICore 信心度低)
        if analysis.get("confidence_score", 1.0) < 0.6:
            return True
        
        # 資源需求超過閾值
        if analysis.get("resource_score", 0) > 0.8:
            return True
        
        # 有風險警告
        if analysis.get("risk_warnings"):
            return True
        
        return False
    
    async def _request_task_processing_strategy(self, task_data: Dict[str, Any],
                                              analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        請求任務處理策略
        """
        # 構建策略選擇消息
        message = self._build_strategy_message(task_data, analysis)
        
        # 構建策略選項
        options = self._build_strategy_options(task_data, analysis)
        
        # 請求人工選擇
        strategy_result = await self.request_human_selection(
            title=f"任務處理策略 - {task_data.get('type', 'Unknown')}",
            message=message,
            options=options,
            timeout=300
        )
        
        if not strategy_result.get("success"):
            return {
                "approved": False,
                "message": "策略選擇失敗或超時"
            }
        
        strategy_choice = strategy_result.get("response", {}).get("choice")
        
        if strategy_choice == "cancel":
            return {
                "approved": False,
                "message": "用戶取消任務處理"
            }
        elif strategy_choice == "custom":
            # 請求自定義參數
            return await self._request_custom_parameters(task_data, analysis)
        else:
            return {
                "approved": True,
                "strategy": strategy_choice,
                "params": self._get_strategy_params(strategy_choice, analysis)
            }
    
    async def _request_custom_parameters(self, task_data: Dict[str, Any],
                                       analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        請求自定義處理參數
        """
        # 構建參數輸入字段
        fields = [
            {
                "name": "processing_mode",
                "label": "處理模式",
                "type": "select",
                "options": ["fast", "balanced", "thorough"],
                "default": "balanced",
                "required": True
            },
            {
                "name": "max_retries",
                "label": "最大重試次數",
                "type": "number",
                "min": 0,
                "max": 10,
                "default": 3,
                "required": True
            },
            {
                "name": "timeout_seconds",
                "label": "超時時間 (秒)",
                "type": "number",
                "min": 30,
                "max": 3600,
                "default": 300,
                "required": True
            },
            {
                "name": "resource_limit",
                "label": "資源限制 (%)",
                "type": "number",
                "min": 10,
                "max": 100,
                "default": 80,
                "required": True
            },
            {
                "name": "special_instructions",
                "label": "特殊指令",
                "type": "textarea",
                "placeholder": "輸入任何特殊處理指令...",
                "required": False
            }
        ]
        
        params_result = await self.request_human_input(
            title="自定義處理參數",
            message=f"請為任務 '{task_data.get('type')}' 設置自定義處理參數:",
            fields=fields,
            timeout=600
        )
        
        if not params_result.get("success"):
            return {
                "approved": False,
                "message": "參數設置失敗或超時"
            }
        
        custom_params = params_result.get("response", {})
        
        return {
            "approved": True,
            "strategy": "custom",
            "params": custom_params
        }
    
    async def _request_quality_verification(self, task_data: Dict[str, Any],
                                          execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        請求品質驗證
        """
        message = self._build_quality_check_message(task_data, execution_result)
        
        options = [
            {"value": "approve", "label": "品質合格，批准結果"},
            {"value": "reject", "label": "品質不合格，需要重新處理"},
            {"value": "modify", "label": "需要微調，提供修改建議"}
        ]
        
        quality_result = await self.request_human_confirmation(
            title=f"品質檢查 - {task_data.get('type', 'Unknown')}",
            message=message,
            options=options,
            timeout=300
        )
        
        if not quality_result.get("success"):
            return {
                "approved": False,
                "message": "品質檢查失敗或超時"
            }
        
        choice = quality_result.get("response", {}).get("choice")
        
        if choice == "approve":
            return {
                "approved": True,
                "quality_score": 1.0,
                "feedback": "人工驗證通過"
            }
        elif choice == "modify":
            # 請求修改建議
            return await self._request_modification_suggestions(task_data, execution_result)
        else:  # reject
            return {
                "approved": False,
                "quality_score": 0.0,
                "feedback": "人工驗證不通過，需要重新處理"
            }
    
    async def _request_batch_processing_strategy(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        請求批量處理策略
        """
        task_types = {}
        for task in tasks:
            task_type = task.get("type", "unknown")
            task_types[task_type] = task_types.get(task_type, 0) + 1
        
        type_summary = "\n".join([f"  • {t}: {c} 個" for t, c in task_types.items()])
        
        message = f"""即將批量處理 {len(tasks)} 個任務:

📊 任務類型分布:
{type_summary}

⚠️ 批量處理注意事項:
• 並行處理速度快但可能消耗更多資源
• 順序處理穩定但耗時較長
• 分批處理是平衡方案

請選擇處理策略:"""
        
        options = [
            {"value": "sequential", "label": "順序處理 (穩定，較慢)"},
            {"value": "parallel", "label": "並行處理 (快速，高資源消耗)"},
            {"value": "batch", "label": "分批處理 (平衡方案)"},
            {"value": "selective", "label": "選擇性處理 (手動選擇任務)"},
            {"value": "cancel", "label": "取消批量處理"}
        ]
        
        strategy_result = await self.request_human_selection(
            title=f"批量處理策略 ({len(tasks)} 個任務)",
            message=message,
            options=options,
            timeout=300
        )
        
        if not strategy_result.get("success"):
            return {"approved": False, "message": "策略選擇失敗"}
        
        choice = strategy_result.get("response", {}).get("choice")
        
        if choice == "cancel":
            return {"approved": False, "message": "用戶取消批量處理"}
        elif choice == "selective":
            return await self._request_selective_processing(tasks)
        else:
            # 請求並行度設置
            if choice in ["parallel", "batch"]:
                parallel_params = await self._request_parallel_parameters(len(tasks))
                return {
                    "approved": True,
                    "strategy": choice,
                    "max_parallel": parallel_params.get("max_parallel", 5)
                }
            else:
                return {
                    "approved": True,
                    "strategy": choice,
                    "max_parallel": 1
                }
    
    def _build_strategy_message(self, task_data: Dict[str, Any], 
                              analysis: Dict[str, Any]) -> str:
        """
        構建策略選擇消息
        """
        message_parts = [
            f"任務處理策略選擇",
            f"",
            f"📋 任務信息:",
            f"  • 類型: {task_data.get('type', 'Unknown')}",
            f"  • 優先級: {task_data.get('priority', 'Normal')}",
            f"  • 預估時間: {analysis.get('estimated_duration', 'Unknown')}",
            f"",
            f"🧠 AICore 分析:",
            f"  • 複雜度分數: {analysis.get('complexity_score', 0):.2f}",
            f"  • 信心度: {analysis.get('confidence_score', 0):.2f}",
            f"  • 資源需求: {analysis.get('resource_score', 0):.2f}",
        ]
        
        if analysis.get("risk_warnings"):
            message_parts.extend([
                f"",
                f"⚠️ 風險警告:",
            ])
            for warning in analysis["risk_warnings"]:
                message_parts.append(f"  • {warning}")
        
        if analysis.get("recommended_strategy"):
            message_parts.extend([
                f"",
                f"💡 AICore 推薦策略: {analysis['recommended_strategy']}"
            ])
        
        message_parts.extend([
            f"",
            f"請選擇處理策略:"
        ])
        
        return "\n".join(message_parts)
    
    def _build_strategy_options(self, task_data: Dict[str, Any],
                              analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        構建策略選項
        """
        options = [
            {"value": "fast", "label": "快速處理 (優先速度)"},
            {"value": "balanced", "label": "平衡處理 (速度與品質並重)"},
            {"value": "thorough", "label": "深度處理 (優先品質)"},
            {"value": "custom", "label": "自定義參數"},
            {"value": "cancel", "label": "取消處理"}
        ]
        
        # 根據任務類型添加特殊選項
        task_type = task_data.get("type", "")
        if "data" in task_type.lower():
            options.insert(-2, {"value": "data_optimized", "label": "數據優化處理"})
        elif "api" in task_type.lower():
            options.insert(-2, {"value": "api_optimized", "label": "API 優化處理"})
        
        return options
    
    # AICore 集成方法
    async def _aicore_analyze_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用 AICore 分析任務
        """
        # 模擬 AICore 任務分析
        task_type = task_data.get("type", "unknown")
        data_size = len(str(task_data.get("data", "")))
        
        # 計算複雜度分數
        complexity_score = 0.3  # 基礎複雜度
        
        if "complex" in task_type.lower():
            complexity_score += 0.4
        if data_size > 1000:
            complexity_score += 0.2
        if task_data.get("priority") == "critical":
            complexity_score += 0.1
        
        # 計算信心度
        confidence_score = 0.9
        if task_type == "unknown":
            confidence_score -= 0.3
        if not task_data.get("data"):
            confidence_score -= 0.2
        
        # 風險警告
        risk_warnings = []
        if complexity_score > 0.8:
            risk_warnings.append("高複雜度任務，建議仔細監控")
        if data_size > 10000:
            risk_warnings.append("大數據量處理，注意資源消耗")
        
        return {
            "complexity_score": complexity_score,
            "confidence_score": confidence_score,
            "resource_score": min(complexity_score + 0.1, 1.0),
            "estimated_duration": f"{int(complexity_score * 300)} 秒",
            "recommended_strategy": "balanced" if complexity_score < 0.7 else "thorough",
            "risk_warnings": risk_warnings if risk_warnings else None,
            "analysis_timestamp": "2024-06-24T12:00:00Z"
        }
    
    async def _aicore_execute_task(self, task_data: Dict[str, Any], strategy: str,
                                 params: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用 AICore 執行任務
        """
        # 模擬任務執行
        execution_time = analysis.get("estimated_duration", "60 秒")
        await asyncio.sleep(2)  # 模擬執行時間
        
        # 根據策略調整結果
        quality_score = 0.8
        if strategy == "thorough":
            quality_score = 0.95
        elif strategy == "fast":
            quality_score = 0.7
        
        return {
            "execution_id": f"exec_{int(asyncio.get_event_loop().time())}",
            "strategy_used": strategy,
            "parameters_used": params,
            "execution_time": execution_time,
            "quality_score": quality_score,
            "output_data": {"processed": True, "result": "任務執行完成"},
            "resource_usage": {"cpu": "45%", "memory": "2.1GB", "time": execution_time},
            "execution_timestamp": "2024-06-24T12:02:00Z"
        }
```

### 方式2: 直接使用客戶端

```python
from PowerAutomation.components.human_loop_mcp_adapter import HumanLoopMCPClient

class GeneralProcessorMCPDirect:
    """
    使用直接客戶端方式的通用處理器
    """
    
    def __init__(self, mcp_url="http://localhost:8096"):
        self.human_loop_client = HumanLoopMCPClient(mcp_url)
        self.workflow_id = "general_processor_direct"
    
    async def handle_task_exception(self, task_data: Dict[str, Any], 
                                  error: str) -> Dict[str, Any]:
        """
        處理任務異常，請求人工決策
        """
        recovery_session = await self.human_loop_client.create_interaction_session({
            "interaction_type": "selection",
            "title": f"任務異常處理 - {task_data.get('type', 'Unknown')}",
            "message": f"任務執行遇到異常:\n\n錯誤信息: {error}\n\n請選擇處理方式:",
            "options": [
                {"value": "retry", "label": "重試任務"},
                {"value": "skip", "label": "跳過任務"},
                {"value": "modify", "label": "修改參數後重試"},
                {"value": "escalate", "label": "上報給專家處理"}
            ],
            "timeout": 300
        })
        
        if recovery_session.get("success"):
            session_id = recovery_session.get("session_id")
            response = await self.human_loop_client.wait_for_user_response(session_id)
            
            if response.get("success"):
                choice = response.get("response", {}).get("choice")
                return await self._execute_recovery_strategy(task_data, error, choice)
        
        # 默認跳過任務
        return {"success": False, "action": "skipped", "reason": "無法獲取人工決策"}
```

## 🚀 使用示例

### 基本使用
```python
# 初始化處理器
processor = GeneralProcessorMCP()

# 處理簡單任務 (通常不需要人工介入)
simple_task = {
    "task_id": "task_001",
    "type": "data_processing",
    "priority": "normal",
    "data": {"records": 100}
}
result = await processor.process_task(simple_task)

# 處理複雜任務 (會請求人工策略選擇)
complex_task = {
    "task_id": "task_002", 
    "type": "complex_analysis",
    "priority": "critical",
    "data": {"large_dataset": "..."}
}
result = await processor.process_task(complex_task)
```

### 批量處理
```python
# 批量任務處理
tasks = [
    {"type": "data_processing", "data": {"records": 50}},
    {"type": "api_integration", "data": {"endpoints": 10}},
    {"type": "report_generation", "data": {"templates": 5}}
]

batch_result = await processor.process_batch_tasks(tasks)
```

### 異常處理
```python
# 帶異常處理的任務
try:
    result = await processor.process_task(risky_task)
except Exception as e:
    recovery_result = await processor.handle_task_exception(risky_task, str(e))
```

## 📋 配置選項

### 環境變量
```bash
# 複雜度閾值
export COMPLEXITY_THRESHOLD="0.7"

# 自動重試限制
export AUTO_RETRY_LIMIT="3"

# 啟用人工介入
export HUMAN_INTERVENTION_ENABLED="true"

# 品質檢查閾值
export QUALITY_CHECK_THRESHOLD="0.8"
```

### 配置文件
```yaml
# general_processor_config.yaml
processing:
  complexity_threshold: 0.7
  auto_retry_limit: 3
  human_intervention_enabled: true
  
quality_control:
  enabled: true
  threshold: 0.8
  require_verification_critical: true
  
batch_processing:
  max_parallel_tasks: 10
  batch_size: 50
  timeout_per_task: 300
```

這就是 General Processor MCP 的完整集成使用方式！接下來我將提供實際使用示例和最佳實踐。

