#!/usr/bin/env python3
"""
Human Loop MCP 集成示例
展示如何在現有的 PowerAutomation 組件中集成 Human Loop MCP 適配器

這個示例展示了三種集成方式：
1. 繼承 HumanLoopIntegrationMixin
2. 直接使用 HumanLoopMCPClient
3. 使用便利函數
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from human_loop_mcp_adapter import (
    HumanLoopMCPClient,
    HumanLoopIntegrationMixin,
    quick_confirmation,
    create_human_loop_client
)

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 示例1: 增強現有的 Enhanced VSCode Installer MCP
class EnhancedVSCodeInstallerMCPWithHumanLoop(HumanLoopIntegrationMixin):
    """
    增強的 VSCode Installer MCP，集成 Human Loop 功能
    繼承 HumanLoopIntegrationMixin 來獲得人機交互能力
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.config = config or {}
        self.workflow_id = "vscode_installer_workflow"
        
    async def deploy_vsix_with_human_confirmation(self, 
                                                vsix_path: str,
                                                target_environment: str = "development") -> Dict[str, Any]:
        """
        部署 VSIX 並請求人工確認
        
        Args:
            vsix_path: VSIX 文件路徑
            target_environment: 目標環境
            
        Returns:
            部署結果
        """
        logger.info(f"準備部署 VSIX: {vsix_path} 到 {target_environment}")
        
        # 如果是生產環境，請求人工確認
        if target_environment == "production":
            confirmation_result = await self.request_human_confirmation(
                title="生產環境部署確認",
                message=f"確定要將 {vsix_path} 部署到生產環境嗎？\n\n這是一個關鍵操作，請仔細確認。",
                options=[
                    {"value": "confirm", "label": "確認部署"},
                    {"value": "cancel", "label": "取消部署"},
                    {"value": "staging", "label": "改為部署到預發環境"}
                ],
                timeout=600  # 10分鐘超時
            )
            
            if not confirmation_result.get("success"):
                return {
                    "success": False,
                    "error": "人工確認失敗",
                    "details": confirmation_result
                }
            
            user_choice = confirmation_result.get("response", {}).get("choice")
            
            if user_choice == "cancel":
                return {
                    "success": False,
                    "message": "用戶取消部署",
                    "cancelled_by_user": True
                }
            elif user_choice == "staging":
                target_environment = "staging"
                logger.info("用戶選擇部署到預發環境")
        
        # 執行實際部署
        return await self._perform_deployment(vsix_path, target_environment)
    
    async def _perform_deployment(self, vsix_path: str, environment: str) -> Dict[str, Any]:
        """
        執行實際的部署操作
        
        Args:
            vsix_path: VSIX 文件路徑
            environment: 目標環境
            
        Returns:
            部署結果
        """
        # 模擬部署過程
        logger.info(f"開始部署 {vsix_path} 到 {environment}")
        
        # 這裡會是實際的部署邏輯
        await asyncio.sleep(2)  # 模擬部署時間
        
        return {
            "success": True,
            "message": f"成功部署到 {environment}",
            "vsix_path": vsix_path,
            "environment": environment,
            "deployment_id": f"deploy_{int(asyncio.get_event_loop().time())}"
        }

# 示例2: 增強現有的 General Processor MCP
class GeneralProcessorMCPWithHumanLoop:
    """
    General Processor MCP，使用直接客戶端方式集成 Human Loop
    """
    
    def __init__(self, mcp_url: str = "http://localhost:8096"):
        self.human_loop_client = HumanLoopMCPClient(mcp_url)
        self.workflow_id = "general_processor_workflow"
    
    async def process_complex_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理複雜任務，在需要時請求人工介入
        
        Args:
            task_data: 任務數據
            
        Returns:
            處理結果
        """
        task_type = task_data.get("type", "unknown")
        complexity = task_data.get("complexity", "low")
        
        logger.info(f"處理任務: {task_type}, 複雜度: {complexity}")
        
        # 如果是高複雜度任務，請求人工選擇處理策略
        if complexity == "high":
            strategy_result = await self.human_loop_client.create_interaction_session({
                "interaction_type": "selection",
                "title": "處理策略選擇",
                "message": f"檢測到高複雜度任務: {task_type}\n\n請選擇處理策略:",
                "options": [
                    {"value": "auto", "label": "自動處理 (可能需要更長時間)"},
                    {"value": "manual", "label": "手動處理 (需要專家介入)"},
                    {"value": "defer", "label": "延後處理 (等待更好時機)"}
                ],
                "timeout": 300
            })
            
            if strategy_result.get("success"):
                session_id = strategy_result.get("session_id")
                response_result = await self.human_loop_client.wait_for_user_response(session_id)
                
                if response_result.get("success"):
                    strategy = response_result.get("response", {}).get("choice", "auto")
                    logger.info(f"用戶選擇處理策略: {strategy}")
                    
                    return await self._execute_strategy(task_data, strategy)
                else:
                    logger.warning("用戶未響應策略選擇，使用默認自動處理")
                    return await self._execute_strategy(task_data, "auto")
            else:
                logger.error("創建策略選擇會話失敗，使用默認自動處理")
                return await self._execute_strategy(task_data, "auto")
        else:
            # 低複雜度任務直接自動處理
            return await self._execute_strategy(task_data, "auto")
    
    async def _execute_strategy(self, task_data: Dict[str, Any], strategy: str) -> Dict[str, Any]:
        """
        執行選定的處理策略
        
        Args:
            task_data: 任務數據
            strategy: 處理策略
            
        Returns:
            執行結果
        """
        logger.info(f"執行策略: {strategy}")
        
        if strategy == "auto":
            # 自動處理邏輯
            await asyncio.sleep(1)  # 模擬處理時間
            return {
                "success": True,
                "strategy": strategy,
                "message": "自動處理完成",
                "result": {"processed": True, "method": "automatic"}
            }
        elif strategy == "manual":
            # 手動處理邏輯
            return {
                "success": True,
                "strategy": strategy,
                "message": "已轉交專家手動處理",
                "result": {"processed": False, "method": "manual", "status": "pending_expert"}
            }
        elif strategy == "defer":
            # 延後處理邏輯
            return {
                "success": True,
                "strategy": strategy,
                "message": "任務已延後處理",
                "result": {"processed": False, "method": "deferred", "status": "scheduled"}
            }
        else:
            return {
                "success": False,
                "error": f"未知策略: {strategy}"
            }

# 示例3: 使用便利函數的簡單集成
class SimpleWorkflowWithHumanLoop:
    """
    簡單工作流，使用便利函數集成 Human Loop
    """
    
    async def execute_critical_operation(self, operation_name: str) -> Dict[str, Any]:
        """
        執行關鍵操作，使用便利函數請求確認
        
        Args:
            operation_name: 操作名稱
            
        Returns:
            執行結果
        """
        logger.info(f"準備執行關鍵操作: {operation_name}")
        
        # 使用便利函數請求確認
        confirmed = await quick_confirmation(
            title="關鍵操作確認",
            message=f"即將執行關鍵操作: {operation_name}\n\n此操作可能影響系統穩定性，確定要繼續嗎？",
            timeout=180  # 3分鐘超時
        )
        
        if confirmed:
            logger.info(f"用戶確認，執行操作: {operation_name}")
            # 執行實際操作
            await asyncio.sleep(1)  # 模擬操作時間
            return {
                "success": True,
                "operation": operation_name,
                "message": "操作執行成功",
                "confirmed_by_user": True
            }
        else:
            logger.info(f"用戶拒絕或超時，取消操作: {operation_name}")
            return {
                "success": False,
                "operation": operation_name,
                "message": "操作被用戶取消或超時",
                "confirmed_by_user": False
            }

# 示例4: 批量操作的人工介入
class BatchOperationWithHumanLoop:
    """
    批量操作，展示複雜的人機交互場景
    """
    
    def __init__(self):
        self.human_loop_client = None
    
    async def _ensure_client(self):
        """確保客戶端已初始化"""
        if not self.human_loop_client:
            self.human_loop_client = await create_human_loop_client()
    
    async def process_batch_deployment(self, deployments: list) -> Dict[str, Any]:
        """
        處理批量部署，在關鍵點請求人工介入
        
        Args:
            deployments: 部署列表
            
        Returns:
            批量處理結果
        """
        await self._ensure_client()
        
        results = []
        failed_deployments = []
        
        for i, deployment in enumerate(deployments):
            logger.info(f"處理部署 {i+1}/{len(deployments)}: {deployment.get('name')}")
            
            # 如果是關鍵部署，請求確認
            if deployment.get("critical", False):
                confirmation_result = await self.human_loop_client.create_interaction_session({
                    "interaction_type": "confirmation",
                    "title": f"關鍵部署確認 ({i+1}/{len(deployments)})",
                    "message": f"即將部署關鍵組件: {deployment.get('name')}\n\n"
                              f"環境: {deployment.get('environment')}\n"
                              f"版本: {deployment.get('version')}\n\n"
                              f"這是關鍵部署，確定要繼續嗎？",
                    "options": [
                        {"value": "confirm", "label": "確認部署"},
                        {"value": "skip", "label": "跳過此部署"},
                        {"value": "abort", "label": "中止所有部署"}
                    ],
                    "timeout": 300
                })
                
                if confirmation_result.get("success"):
                    session_id = confirmation_result.get("session_id")
                    response_result = await self.human_loop_client.wait_for_user_response(session_id)
                    
                    if response_result.get("success"):
                        choice = response_result.get("response", {}).get("choice")
                        
                        if choice == "abort":
                            logger.info("用戶選擇中止所有部署")
                            return {
                                "success": False,
                                "message": "用戶中止批量部署",
                                "completed_deployments": results,
                                "aborted_at": i
                            }
                        elif choice == "skip":
                            logger.info(f"用戶選擇跳過部署: {deployment.get('name')}")
                            results.append({
                                "deployment": deployment,
                                "status": "skipped",
                                "reason": "用戶跳過"
                            })
                            continue
                        # choice == "confirm" 繼續執行
                    else:
                        logger.warning("用戶未響應，跳過關鍵部署")
                        failed_deployments.append(deployment)
                        continue
                else:
                    logger.error("創建確認會話失敗，跳過關鍵部署")
                    failed_deployments.append(deployment)
                    continue
            
            # 執行部署
            try:
                result = await self._execute_single_deployment(deployment)
                results.append({
                    "deployment": deployment,
                    "status": "completed",
                    "result": result
                })
            except Exception as e:
                logger.error(f"部署失敗: {deployment.get('name')} - {str(e)}")
                failed_deployments.append(deployment)
                results.append({
                    "deployment": deployment,
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "success": len(failed_deployments) == 0,
            "total_deployments": len(deployments),
            "completed_deployments": len([r for r in results if r["status"] == "completed"]),
            "failed_deployments": len(failed_deployments),
            "skipped_deployments": len([r for r in results if r["status"] == "skipped"]),
            "results": results,
            "failed_items": failed_deployments
        }
    
    async def _execute_single_deployment(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行單個部署
        
        Args:
            deployment: 部署配置
            
        Returns:
            部署結果
        """
        # 模擬部署過程
        await asyncio.sleep(0.5)  # 模擬部署時間
        
        return {
            "deployment_id": f"deploy_{int(asyncio.get_event_loop().time())}",
            "name": deployment.get("name"),
            "environment": deployment.get("environment"),
            "version": deployment.get("version"),
            "status": "deployed"
        }

# 主要示例函數
async def main():
    """主要示例函數"""
    
    print("=== Human Loop MCP 集成示例 ===\n")
    
    # 示例1: Enhanced VSCode Installer MCP
    print("1. Enhanced VSCode Installer MCP 示例")
    vscode_installer = EnhancedVSCodeInstallerMCPWithHumanLoop()
    
    # 測試開發環境部署（不需要確認）
    dev_result = await vscode_installer.deploy_vsix_with_human_confirmation(
        "powerautomation-3.0.0.vsix", 
        "development"
    )
    print(f"開發環境部署結果: {dev_result}")
    
    # 測試生產環境部署（需要確認）
    # 注意：這會創建實際的人機交互會話
    # prod_result = await vscode_installer.deploy_vsix_with_human_confirmation(
    #     "powerautomation-3.0.0.vsix", 
    #     "production"
    # )
    # print(f"生產環境部署結果: {prod_result}")
    
    print("\n" + "="*50 + "\n")
    
    # 示例2: General Processor MCP
    print("2. General Processor MCP 示例")
    processor = GeneralProcessorMCPWithHumanLoop()
    
    # 測試低複雜度任務
    low_task = {
        "type": "data_processing",
        "complexity": "low",
        "data": {"records": 100}
    }
    low_result = await processor.process_complex_task(low_task)
    print(f"低複雜度任務結果: {low_result}")
    
    # 測試高複雜度任務（會請求人工選擇）
    # high_task = {
    #     "type": "system_migration",
    #     "complexity": "high",
    #     "data": {"systems": ["db", "cache", "api"]}
    # }
    # high_result = await processor.process_complex_task(high_task)
    # print(f"高複雜度任務結果: {high_result}")
    
    print("\n" + "="*50 + "\n")
    
    # 示例3: 簡單工作流
    print("3. 簡單工作流示例")
    simple_workflow = SimpleWorkflowWithHumanLoop()
    
    # 測試關鍵操作（會請求確認）
    # operation_result = await simple_workflow.execute_critical_operation("系統重啟")
    # print(f"關鍵操作結果: {operation_result}")
    
    print("\n" + "="*50 + "\n")
    
    # 示例4: 批量操作
    print("4. 批量操作示例")
    batch_processor = BatchOperationWithHumanLoop()
    
    # 測試批量部署
    deployments = [
        {"name": "component-a", "environment": "production", "version": "1.0.0", "critical": False},
        {"name": "core-system", "environment": "production", "version": "2.0.0", "critical": True},
        {"name": "component-b", "environment": "production", "version": "1.5.0", "critical": False}
    ]
    
    # batch_result = await batch_processor.process_batch_deployment(deployments)
    # print(f"批量部署結果: {batch_result}")
    
    print("示例完成！")
    print("\n注意：帶有人機交互的示例已被註釋，需要 Human Loop MCP 服務運行才能測試。")

if __name__ == "__main__":
    asyncio.run(main())

