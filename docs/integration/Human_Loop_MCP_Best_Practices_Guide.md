# Human Loop MCP 集成 - 實際使用示例和最佳實踐

## 概述

本指南提供 Enhanced VSCode Installer MCP 和 General Processor MCP 與 Human Loop MCP 集成的完整實際使用示例、最佳實踐和部署指南。

## 🚀 完整使用示例

### 示例1: 生產環境 VSIX 部署流程

```python
#!/usr/bin/env python3
"""
生產環境 VSIX 部署完整示例
展示 Enhanced VSCode Installer MCP 的實際使用
"""

import asyncio
import logging
from datetime import datetime
from PowerAutomation.components.human_loop_mcp_adapter import HumanLoopIntegrationMixin

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionVSIXDeployer(HumanLoopIntegrationMixin):
    """
    生產環境 VSIX 部署器
    """
    
    def __init__(self):
        super().__init__()
        self.workflow_id = "production_vsix_deployment"
        self.deployment_history = []
    
    async def deploy_to_production(self, vsix_info: dict) -> dict:
        """
        完整的生產環境部署流程
        """
        deployment_id = f"deploy_{int(datetime.now().timestamp())}"
        
        try:
            logger.info(f"開始生產環境部署: {deployment_id}")
            
            # 第1步: 預部署檢查
            pre_check = await self._pre_deployment_check(vsix_info)
            if not pre_check["passed"]:
                return {
                    "success": False,
                    "stage": "pre_check",
                    "reason": "預部署檢查失敗",
                    "details": pre_check
                }
            
            # 第2步: 人工確認部署
            deployment_approval = await self._request_production_deployment_approval(
                vsix_info, pre_check
            )
            
            if not deployment_approval.get("approved"):
                return {
                    "success": False,
                    "stage": "approval",
                    "reason": "部署未獲批准",
                    "details": deployment_approval
                }
            
            # 第3步: 執行部署
            deployment_result = await self._execute_production_deployment(
                vsix_info, deployment_approval, deployment_id
            )
            
            # 第4步: 部署後驗證
            verification_result = await self._post_deployment_verification(
                deployment_result
            )
            
            # 第5步: 人工驗收測試 (如果需要)
            if verification_result.get("requires_human_verification"):
                acceptance_result = await self._request_acceptance_testing(
                    deployment_result, verification_result
                )
                
                if not acceptance_result.get("accepted"):
                    # 回滾部署
                    rollback_result = await self._rollback_deployment(
                        deployment_id, acceptance_result
                    )
                    return {
                        "success": False,
                        "stage": "acceptance",
                        "reason": "驗收測試失敗",
                        "deployment_result": deployment_result,
                        "rollback_result": rollback_result
                    }
            
            # 記錄成功部署
            self.deployment_history.append({
                "deployment_id": deployment_id,
                "vsix_info": vsix_info,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            })
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "deployment_result": deployment_result,
                "verification_result": verification_result
            }
            
        except Exception as e:
            logger.error(f"部署過程發生異常: {str(e)}")
            
            # 請求異常處理策略
            exception_handling = await self._handle_deployment_exception(
                deployment_id, vsix_info, str(e)
            )
            
            return {
                "success": False,
                "stage": "exception",
                "error": str(e),
                "exception_handling": exception_handling
            }
    
    async def _request_production_deployment_approval(self, vsix_info: dict,
                                                    pre_check: dict) -> dict:
        """
        請求生產環境部署批准
        """
        # 構建詳細的部署信息
        message = f"""🚀 生產環境 VSIX 部署申請

📦 擴展信息:
  • 名稱: {vsix_info.get('name', 'Unknown')}
  • 版本: {vsix_info.get('version', 'Unknown')}
  • 文件大小: {vsix_info.get('size', 'Unknown')}
  • 發布日期: {vsix_info.get('release_date', 'Unknown')}

🔍 預部署檢查結果:
  • 兼容性檢查: {'✅ 通過' if pre_check.get('compatibility') else '❌ 失敗'}
  • 安全掃描: {'✅ 通過' if pre_check.get('security') else '❌ 失敗'}
  • 依賴檢查: {'✅ 通過' if pre_check.get('dependencies') else '❌ 失敗'}
  • 性能評估: {'✅ 通過' if pre_check.get('performance') else '❌ 失敗'}

⚠️ 風險評估:
  • 風險等級: {pre_check.get('risk_level', 'Unknown')}
  • 影響範圍: {pre_check.get('impact_scope', 'Unknown')}
  • 回滾難度: {pre_check.get('rollback_difficulty', 'Unknown')}

📋 部署計劃:
  • 預計停機時間: {pre_check.get('estimated_downtime', '< 5 分鐘')}
  • 部署窗口: {pre_check.get('deployment_window', '維護時段')}
  • 回滾計劃: {pre_check.get('rollback_plan', '自動回滾')}

確定要執行生產環境部署嗎？"""

        options = [
            {"value": "approve", "label": "✅ 批准部署"},
            {"value": "approve_with_monitoring", "label": "⚠️ 批准部署 (加強監控)"},
            {"value": "schedule_later", "label": "📅 安排稍後部署"},
            {"value": "request_changes", "label": "🔄 要求修改後重新提交"},
            {"value": "reject", "label": "❌ 拒絕部署"}
        ]
        
        approval_result = await self.request_human_confirmation(
            title="🚀 生產環境 VSIX 部署批准",
            message=message,
            options=options,
            timeout=1800  # 30分鐘超時
        )
        
        if not approval_result.get("success"):
            return {"approved": False, "reason": "批准請求失敗或超時"}
        
        choice = approval_result.get("response", {}).get("choice")
        
        if choice == "approve":
            return {"approved": True, "monitoring_level": "standard"}
        elif choice == "approve_with_monitoring":
            return {"approved": True, "monitoring_level": "enhanced"}
        elif choice == "schedule_later":
            return await self._request_deployment_schedule(vsix_info)
        elif choice == "request_changes":
            return await self._request_deployment_changes(vsix_info)
        else:  # reject
            return {"approved": False, "reason": "部署被拒絕"}
    
    async def _request_acceptance_testing(self, deployment_result: dict,
                                        verification_result: dict) -> dict:
        """
        請求驗收測試
        """
        message = f"""🧪 部署後驗收測試

✅ 自動驗證結果:
  • 服務狀態: {'正常' if verification_result.get('service_healthy') else '異常'}
  • 功能測試: {'通過' if verification_result.get('functional_tests') else '失敗'}
  • 性能測試: {'通過' if verification_result.get('performance_tests') else '失敗'}
  • 集成測試: {'通過' if verification_result.get('integration_tests') else '失敗'}

📊 部署統計:
  • 部署時間: {deployment_result.get('deployment_time', 'Unknown')}
  • 影響用戶: {deployment_result.get('affected_users', 'Unknown')}
  • 資源使用: {deployment_result.get('resource_usage', 'Unknown')}

⚠️ 需要人工驗證的項目:
  • 用戶界面檢查
  • 關鍵功能驗證
  • 用戶體驗評估

請進行人工驗收測試並確認結果:"""

        options = [
            {"value": "accept", "label": "✅ 驗收通過"},
            {"value": "accept_with_notes", "label": "⚠️ 有問題但可接受"},
            {"value": "reject", "label": "❌ 驗收失敗，需要回滾"},
            {"value": "need_more_time", "label": "⏰ 需要更多時間測試"}
        ]
        
        acceptance_result = await self.request_human_confirmation(
            title="🧪 生產環境部署驗收測試",
            message=message,
            options=options,
            timeout=3600  # 1小時超時
        )
        
        if not acceptance_result.get("success"):
            return {"accepted": False, "reason": "驗收測試超時"}
        
        choice = acceptance_result.get("response", {}).get("choice")
        
        if choice in ["accept", "accept_with_notes"]:
            return {"accepted": True, "result": choice}
        elif choice == "need_more_time":
            return await self._extend_testing_time()
        else:  # reject
            return {"accepted": False, "reason": "驗收測試失敗"}

# 使用示例
async def production_deployment_example():
    """
    生產環境部署示例
    """
    deployer = ProductionVSIXDeployer()
    
    vsix_info = {
        "name": "PowerAutomation",
        "version": "3.0.0",
        "size": "2.5MB",
        "release_date": "2024-06-24",
        "path": "/path/to/powerautomation-3.0.0.vsix"
    }
    
    result = await deployer.deploy_to_production(vsix_info)
    
    if result["success"]:
        print(f"✅ 部署成功: {result['deployment_id']}")
    else:
        print(f"❌ 部署失敗: {result['reason']}")
        print(f"失敗階段: {result['stage']}")
```

### 示例2: 複雜數據處理工作流

```python
#!/usr/bin/env python3
"""
複雜數據處理工作流示例
展示 General Processor MCP 的實際使用
"""

import asyncio
import logging
from typing import List, Dict, Any
from PowerAutomation.components.human_loop_mcp_adapter import HumanLoopIntegrationMixin

logger = logging.getLogger(__name__)

class DataProcessingWorkflow(HumanLoopIntegrationMixin):
    """
    複雜數據處理工作流
    """
    
    def __init__(self):
        super().__init__()
        self.workflow_id = "data_processing_workflow"
        self.processing_history = []
    
    async def process_large_dataset(self, dataset_info: dict) -> dict:
        """
        處理大型數據集
        """
        workflow_id = f"workflow_{int(datetime.now().timestamp())}"
        
        try:
            logger.info(f"開始數據處理工作流: {workflow_id}")
            
            # 第1步: 數據集分析
            analysis_result = await self._analyze_dataset(dataset_info)
            
            # 第2步: 處理策略決策
            if analysis_result.get("complexity_score", 0) > 0.7:
                strategy_decision = await self._request_processing_strategy(
                    dataset_info, analysis_result
                )
                
                if not strategy_decision.get("approved"):
                    return {
                        "success": False,
                        "reason": "處理策略未獲批准",
                        "details": strategy_decision
                    }
                
                processing_strategy = strategy_decision.get("strategy")
                processing_params = strategy_decision.get("params", {})
            else:
                # 低複雜度，使用默認策略
                processing_strategy = "auto"
                processing_params = {}
            
            # 第3步: 執行數據處理
            processing_result = await self._execute_data_processing(
                dataset_info, processing_strategy, processing_params, workflow_id
            )
            
            # 第4步: 結果品質檢查
            if processing_result.get("quality_score", 1.0) < 0.8:
                quality_check = await self._request_quality_review(
                    dataset_info, processing_result
                )
                
                if not quality_check.get("approved"):
                    # 重新處理或調整參數
                    return await self._handle_quality_issues(
                        dataset_info, processing_result, quality_check, workflow_id
                    )
            
            # 第5步: 結果交付確認
            delivery_confirmation = await self._request_delivery_confirmation(
                processing_result
            )
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "processing_result": processing_result,
                "delivery_confirmation": delivery_confirmation
            }
            
        except Exception as e:
            logger.error(f"數據處理工作流異常: {str(e)}")
            
            exception_handling = await self._handle_processing_exception(
                workflow_id, dataset_info, str(e)
            )
            
            return {
                "success": False,
                "error": str(e),
                "exception_handling": exception_handling
            }
    
    async def _request_processing_strategy(self, dataset_info: dict,
                                         analysis: dict) -> dict:
        """
        請求數據處理策略
        """
        message = f"""📊 大型數據集處理策略選擇

📋 數據集信息:
  • 名稱: {dataset_info.get('name', 'Unknown')}
  • 大小: {dataset_info.get('size', 'Unknown')}
  • 記錄數: {dataset_info.get('record_count', 'Unknown')}
  • 數據類型: {dataset_info.get('data_type', 'Unknown')}

🧠 複雜度分析:
  • 複雜度分數: {analysis.get('complexity_score', 0):.2f}
  • 預估處理時間: {analysis.get('estimated_time', 'Unknown')}
  • 資源需求: {analysis.get('resource_requirement', 'Unknown')}
  • 風險等級: {analysis.get('risk_level', 'Unknown')}

⚠️ 特殊考慮:
  • 數據敏感性: {analysis.get('data_sensitivity', 'Unknown')}
  • 合規要求: {analysis.get('compliance_requirements', 'None')}
  • 性能要求: {analysis.get('performance_requirements', 'Standard')}

請選擇處理策略:"""

        options = [
            {"value": "fast_parallel", "label": "🚀 快速並行處理 (高資源消耗)"},
            {"value": "balanced_batch", "label": "⚖️ 平衡分批處理 (推薦)"},
            {"value": "conservative_sequential", "label": "🐌 保守順序處理 (穩定)"},
            {"value": "custom_optimized", "label": "🎯 自定義優化處理"},
            {"value": "defer_processing", "label": "⏰ 延後處理 (非高峰時段)"}
        ]
        
        strategy_result = await self.request_human_selection(
            title="📊 數據處理策略選擇",
            message=message,
            options=options,
            timeout=600
        )
        
        if not strategy_result.get("success"):
            return {"approved": False, "reason": "策略選擇失敗或超時"}
        
        choice = strategy_result.get("response", {}).get("choice")
        
        if choice == "custom_optimized":
            return await self._request_custom_processing_params(dataset_info, analysis)
        elif choice == "defer_processing":
            return await self._request_processing_schedule(dataset_info)
        else:
            return {
                "approved": True,
                "strategy": choice,
                "params": self._get_strategy_default_params(choice)
            }
    
    async def _request_quality_review(self, dataset_info: dict,
                                    processing_result: dict) -> dict:
        """
        請求品質審查
        """
        quality_metrics = processing_result.get("quality_metrics", {})
        
        message = f"""🔍 數據處理品質審查

📊 處理結果統計:
  • 處理記錄數: {processing_result.get('processed_records', 'Unknown')}
  • 成功率: {quality_metrics.get('success_rate', 'Unknown')}
  • 錯誤率: {quality_metrics.get('error_rate', 'Unknown')}
  • 處理時間: {processing_result.get('processing_time', 'Unknown')}

📈 品質指標:
  • 數據完整性: {quality_metrics.get('data_integrity', 'Unknown')}
  • 數據準確性: {quality_metrics.get('data_accuracy', 'Unknown')}
  • 格式一致性: {quality_metrics.get('format_consistency', 'Unknown')}
  • 業務規則符合性: {quality_metrics.get('business_rule_compliance', 'Unknown')}

⚠️ 發現的問題:
{self._format_quality_issues(quality_metrics.get('issues', []))}

請審查處理結果並決定:"""

        options = [
            {"value": "approve", "label": "✅ 品質合格，批准結果"},
            {"value": "approve_with_notes", "label": "⚠️ 有小問題但可接受"},
            {"value": "request_fixes", "label": "🔧 要求修復問題"},
            {"value": "reject_reprocess", "label": "❌ 拒絕結果，重新處理"}
        ]
        
        quality_result = await self.request_human_confirmation(
            title="🔍 數據處理品質審查",
            message=message,
            options=options,
            timeout=900
        )
        
        if not quality_result.get("success"):
            return {"approved": False, "reason": "品質審查超時"}
        
        choice = quality_result.get("response", {}).get("choice")
        
        if choice in ["approve", "approve_with_notes"]:
            return {"approved": True, "quality_level": choice}
        elif choice == "request_fixes":
            return await self._request_fix_specifications(processing_result)
        else:  # reject_reprocess
            return {"approved": False, "reason": "品質不合格，需要重新處理"}

# 使用示例
async def data_processing_example():
    """
    數據處理工作流示例
    """
    processor = DataProcessingWorkflow()
    
    dataset_info = {
        "name": "Customer Analytics Dataset",
        "size": "15GB",
        "record_count": "10M",
        "data_type": "Mixed (JSON, CSV, Parquet)",
        "source": "Multiple APIs and Databases"
    }
    
    result = await processor.process_large_dataset(dataset_info)
    
    if result["success"]:
        print(f"✅ 數據處理完成: {result['workflow_id']}")
    else:
        print(f"❌ 數據處理失敗: {result['reason']}")
```

## 🎯 最佳實踐

### 1. 人機交互設計原則

#### 清晰的信息呈現
```python
def build_clear_message(context: dict) -> str:
    """
    構建清晰的交互消息
    """
    return f"""
🎯 操作概要: {context['operation']}

📋 關鍵信息:
  • 影響範圍: {context['scope']}
  • 風險等級: {context['risk_level']}
  • 預估時間: {context['estimated_time']}

⚠️ 注意事項:
{format_warnings(context['warnings'])}

💡 建議: {context['recommendation']}

請做出決策:
"""
```

#### 合理的選項設計
```python
def build_smart_options(context: dict) -> list:
    """
    構建智能選項
    """
    base_options = [
        {"value": "approve", "label": "✅ 批准"},
        {"value": "cancel", "label": "❌ 取消"}
    ]
    
    # 根據上下文添加額外選項
    if context.get("has_alternatives"):
        base_options.insert(-1, {
            "value": "alternative", 
            "label": "🔄 選擇替代方案"
        })
    
    if context.get("can_modify"):
        base_options.insert(-1, {
            "value": "modify", 
            "label": "⚙️ 修改參數"
        })
    
    return base_options
```

### 2. 超時和重試策略

```python
class TimeoutStrategy:
    """
    超時策略管理
    """
    
    @staticmethod
    def get_timeout(interaction_type: str, complexity: str) -> int:
        """
        根據交互類型和複雜度確定超時時間
        """
        base_timeouts = {
            "confirmation": 300,    # 5分鐘
            "selection": 600,       # 10分鐘
            "input": 900,          # 15分鐘
            "quality_check": 1800   # 30分鐘
        }
        
        complexity_multipliers = {
            "low": 1.0,
            "medium": 1.5,
            "high": 2.0,
            "critical": 3.0
        }
        
        base_timeout = base_timeouts.get(interaction_type, 300)
        multiplier = complexity_multipliers.get(complexity, 1.0)
        
        return int(base_timeout * multiplier)
    
    @staticmethod
    async def with_retry(func, max_retries: int = 2):
        """
        帶重試的執行
        """
        for attempt in range(max_retries + 1):
            try:
                result = await func()
                if result.get("success"):
                    return result
                
                if attempt < max_retries:
                    logger.warning(f"嘗試 {attempt + 1} 失敗，重試中...")
                    await asyncio.sleep(5)  # 等待5秒後重試
                
            except Exception as e:
                if attempt < max_retries:
                    logger.error(f"嘗試 {attempt + 1} 異常: {str(e)}，重試中...")
                    await asyncio.sleep(5)
                else:
                    raise
        
        return {"success": False, "reason": "所有重試都失敗"}
```

### 3. 錯誤處理和恢復

```python
class ErrorRecoveryHandler:
    """
    錯誤恢復處理器
    """
    
    async def handle_interaction_failure(self, interaction_context: dict, 
                                       error: str) -> dict:
        """
        處理交互失敗
        """
        recovery_options = [
            {"value": "retry", "label": "🔄 重試交互"},
            {"value": "skip", "label": "⏭️ 跳過此步驟"},
            {"value": "fallback", "label": "🔙 使用默認選項"},
            {"value": "escalate", "label": "📞 上報處理"}
        ]
        
        recovery_result = await self.request_human_selection(
            title="❌ 交互失敗恢復",
            message=f"交互過程發生錯誤: {error}\n\n請選擇恢復策略:",
            options=recovery_options,
            timeout=300
        )
        
        if recovery_result.get("success"):
            choice = recovery_result.get("response", {}).get("choice")
            return await self._execute_recovery_strategy(choice, interaction_context)
        
        # 默認使用回退策略
        return {"strategy": "fallback", "reason": "無法獲取恢復指令"}
    
    async def _execute_recovery_strategy(self, strategy: str, 
                                       context: dict) -> dict:
        """
        執行恢復策略
        """
        if strategy == "retry":
            return {"strategy": "retry", "max_attempts": 2}
        elif strategy == "skip":
            return {"strategy": "skip", "continue": True}
        elif strategy == "fallback":
            return {"strategy": "fallback", "use_default": True}
        else:  # escalate
            return {"strategy": "escalate", "notify_admin": True}
```

### 4. 監控和日誌

```python
class HumanLoopMonitor:
    """
    Human Loop 監控器
    """
    
    def __init__(self):
        self.metrics = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "timeout_interactions": 0,
            "cancelled_interactions": 0,
            "average_response_time": 0
        }
    
    async def log_interaction_start(self, interaction_id: str, 
                                  interaction_type: str, context: dict):
        """
        記錄交互開始
        """
        logger.info(f"Human Loop 交互開始: {interaction_id}")
        logger.info(f"類型: {interaction_type}")
        logger.info(f"上下文: {context}")
        
        self.metrics["total_interactions"] += 1
    
    async def log_interaction_end(self, interaction_id: str, 
                                result: dict, duration: float):
        """
        記錄交互結束
        """
        logger.info(f"Human Loop 交互結束: {interaction_id}")
        logger.info(f"結果: {result.get('status', 'unknown')}")
        logger.info(f"耗時: {duration:.2f} 秒")
        
        # 更新指標
        if result.get("success"):
            self.metrics["successful_interactions"] += 1
        elif result.get("status") == "timeout":
            self.metrics["timeout_interactions"] += 1
        elif result.get("status") == "cancelled":
            self.metrics["cancelled_interactions"] += 1
        
        # 更新平均響應時間
        self._update_average_response_time(duration)
    
    def get_metrics_summary(self) -> dict:
        """
        獲取指標摘要
        """
        total = self.metrics["total_interactions"]
        if total == 0:
            return {"message": "暫無交互數據"}
        
        success_rate = self.metrics["successful_interactions"] / total * 100
        timeout_rate = self.metrics["timeout_interactions"] / total * 100
        cancel_rate = self.metrics["cancelled_interactions"] / total * 100
        
        return {
            "total_interactions": total,
            "success_rate": f"{success_rate:.1f}%",
            "timeout_rate": f"{timeout_rate:.1f}%",
            "cancel_rate": f"{cancel_rate:.1f}%",
            "average_response_time": f"{self.metrics['average_response_time']:.1f}s"
        }
```

### 5. 配置管理

```python
# human_loop_config.py
class HumanLoopConfig:
    """
    Human Loop 配置管理
    """
    
    def __init__(self, config_file: str = None):
        self.config = self._load_config(config_file)
    
    def _load_config(self, config_file: str) -> dict:
        """
        加載配置
        """
        default_config = {
            "human_loop": {
                "enabled": True,
                "mcp_url": "http://localhost:8096",
                "default_timeout": 300,
                "max_retries": 2
            },
            "thresholds": {
                "complexity_threshold": 0.7,
                "risk_threshold": 0.6,
                "quality_threshold": 0.8
            },
            "environments": {
                "development": {
                    "auto_approve": True,
                    "require_confirmation": False
                },
                "staging": {
                    "auto_approve": False,
                    "require_confirmation": True
                },
                "production": {
                    "auto_approve": False,
                    "require_confirmation": True,
                    "require_quality_check": True
                }
            }
        }
        
        if config_file:
            # 從文件加載配置
            import yaml
            with open(config_file, 'r') as f:
                file_config = yaml.safe_load(f)
            
            # 合併配置
            return self._merge_configs(default_config, file_config)
        
        return default_config
    
    def get_environment_config(self, environment: str) -> dict:
        """
        獲取環境配置
        """
        return self.config["environments"].get(environment, {})
    
    def should_request_human_approval(self, environment: str, 
                                    complexity: float, risk: float) -> bool:
        """
        判斷是否需要人工批准
        """
        env_config = self.get_environment_config(environment)
        
        # 檢查環境配置
        if env_config.get("auto_approve", False):
            return False
        
        if env_config.get("require_confirmation", False):
            return True
        
        # 檢查閾值
        thresholds = self.config["thresholds"]
        if complexity > thresholds["complexity_threshold"]:
            return True
        
        if risk > thresholds["risk_threshold"]:
            return True
        
        return False
```

## 📋 部署檢查清單

### 部署前檢查
- [ ] Human Loop MCP 服務運行正常 (http://localhost:8096)
- [ ] 適配器文件已正確放置在 PowerAutomation/components/
- [ ] 環境變量已正確配置
- [ ] 配置文件已根據環境調整
- [ ] 日誌系統已配置
- [ ] 監控指標已設置

### 功能測試
- [ ] 基本確認交互測試
- [ ] 選擇列表交互測試
- [ ] 參數輸入交互測試
- [ ] 超時處理測試
- [ ] 錯誤恢復測試
- [ ] 並發交互測試

### 性能測試
- [ ] 響應時間測試
- [ ] 並發用戶測試
- [ ] 長時間運行測試
- [ ] 資源使用監控
- [ ] 內存洩漏檢查

### 安全檢查
- [ ] 輸入驗證測試
- [ ] 權限控制測試
- [ ] 數據加密檢查
- [ ] 審計日誌驗證

這就是完整的實際使用示例和最佳實踐指南！

