#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PowerAutomation 三件套協同工作演示
Demonstration of PowerAutomation Three-Component Integration

演示自動化驗證協調器、部署 MCP 和運維 MCP 如何協同工作
確保每個操作都經過適當的驗證

作者: PowerAutomation Team
創建時間: 2025-06-26
版本: 1.0.0
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# 添加組件路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'automated_verification_coordinator_mcp'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'deployment_mcp'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'operations_mcp'))

# 導入組件
from automated_verification_coordinator_mcp.main import AutomatedVerificationCoordinator
from deployment_mcp.main import DeploymentMCP, DeploymentConfig, DeploymentType, DeploymentStrategy
from operations_mcp.main import OperationsMCP, OperationConfig, OperationType, OperationPriority

class PowerAutomationIntegrationDemo:
    """PowerAutomation 集成演示"""
    
    def __init__(self):
        self.verification_coordinator = AutomatedVerificationCoordinator()
        self.deployment_mcp = DeploymentMCP()
        self.operations_mcp = OperationsMCP()
        
        print("🚀 PowerAutomation 三件套初始化完成")
        print("📋 組件列表:")
        print("  1. 自動化驗證協調器 - 確保操作前驗證")
        print("  2. 部署 MCP - 執行部署操作")
        print("  3. 運維 MCP - 執行運維操作")
        print()
    
    async def demo_complete_deployment_workflow(self):
        """演示完整的部署工作流"""
        print("=" * 60)
        print("🎯 演示：完整的部署工作流")
        print("=" * 60)
        
        # 1. 部署前驗證
        print("\n📋 步驟 1: 部署前驗證")
        print("-" * 40)
        
        deployment_context = {
            "service_name": "user-api",
            "environment": "production",
            "version": "v2.1.0",
            "strategy": "blue_green",
            "replicas": 3
        }
        
        verification_result = await self.verification_coordinator.coordinate_verification(
            "deployment", deployment_context
        )
        
        print(f"✅ 驗證結果: {verification_result['overall_status']}")
        print(f"📊 成功率: {verification_result['success_rate']}%")
        
        if verification_result["overall_status"] != "PASSED":
            print("❌ 部署前驗證失敗，停止部署流程")
            return
        
        # 2. 執行部署
        print("\n📋 步驟 2: 執行部署")
        print("-" * 40)
        
        deployment_config = DeploymentConfig(
            name="user-api",
            type=DeploymentType.API_SERVICE,
            strategy=DeploymentStrategy.BLUE_GREEN,
            source_path="/tmp/user-api-source",
            target_environment="production",
            version="v2.1.0",
            replicas=3,
            health_check_url="http://user-api.prod/health",
            rollback_enabled=True
        )
        
        deployment_result = await self.deployment_mcp.deploy(deployment_config)
        
        print(f"✅ 部署結果: {deployment_result.status.value}")
        print(f"⏱️ 部署耗時: {deployment_result.execution_time:.2f} 秒")
        print(f"🌐 部署端點: {deployment_result.endpoints}")
        
        if deployment_result.status.value != "completed":
            print("❌ 部署失敗，停止後續流程")
            return
        
        # 3. 部署後運維檢查
        print("\n📋 步驟 3: 部署後運維檢查")
        print("-" * 40)
        
        # 3.1 運維前驗證
        operations_context = {
            "operation": "post_deployment_check",
            "target_service": "user-api",
            "environment": "production"
        }
        
        ops_verification_result = await self.verification_coordinator.coordinate_verification(
            "operations", operations_context
        )
        
        print(f"✅ 運維驗證結果: {ops_verification_result['overall_status']}")
        
        if ops_verification_result["overall_status"] == "PASSED":
            # 3.2 執行健康檢查
            health_check_config = OperationConfig(
                name="post-deployment-health-check",
                type=OperationType.HEALTH_CHECK,
                priority=OperationPriority.HIGH,
                description="部署後健康檢查",
                target_systems=["user-api-prod"],
                parameters={"check_type": "comprehensive"},
                timeout=120
            )
            
            health_result = await self.operations_mcp.execute_operation(health_check_config)
            
            print(f"✅ 健康檢查結果: {health_result.status.value}")
            print(f"📊 系統指標: {json.dumps(health_result.metrics, indent=2, ensure_ascii=False)}")
            
            if health_result.recommendations:
                print("💡 運維建議:")
                for rec in health_result.recommendations:
                    print(f"  - {rec}")
        
        print("\n🎉 完整部署工作流演示完成！")
    
    async def demo_operations_workflow(self):
        """演示運維工作流"""
        print("\n" + "=" * 60)
        print("🛠️ 演示：運維工作流")
        print("=" * 60)
        
        # 1. 系統監控
        print("\n📋 步驟 1: 系統監控")
        print("-" * 40)
        
        monitoring_context = {
            "monitoring_type": "system_health",
            "systems": ["web-server-1", "api-server-1", "db-server-1"],
            "check_interval": 60
        }
        
        monitoring_verification = await self.verification_coordinator.coordinate_verification(
            "operations", monitoring_context
        )
        
        if monitoring_verification["overall_status"] == "PASSED":
            monitoring_config = OperationConfig(
                name="system-monitoring",
                type=OperationType.SYSTEM_MONITORING,
                priority=OperationPriority.NORMAL,
                description="定期系統監控",
                target_systems=["web-server-1", "api-server-1", "db-server-1"],
                parameters={"monitoring_duration": 30},
                timeout=60
            )
            
            monitoring_result = await self.operations_mcp.execute_operation(monitoring_config)
            print(f"✅ 監控結果: {monitoring_result.status.value}")
            
            # 檢查是否有告警
            if monitoring_result.alerts_generated:
                print("🚨 生成的告警:")
                for alert in monitoring_result.alerts_generated:
                    print(f"  - {alert}")
        
        # 2. 數據庫維護
        print("\n📋 步驟 2: 數據庫維護")
        print("-" * 40)
        
        db_maintenance_context = {
            "maintenance_type": "backup",
            "database": "user_db",
            "maintenance_window": "02:00-04:00"
        }
        
        db_verification = await self.verification_coordinator.coordinate_verification(
            "operations", db_maintenance_context
        )
        
        if db_verification["overall_status"] == "PASSED":
            db_config = OperationConfig(
                name="database-backup",
                type=OperationType.DATABASE_MAINTENANCE,
                priority=OperationPriority.HIGH,
                description="數據庫備份操作",
                target_systems=["db-server-1"],
                parameters={"maintenance_type": "backup"},
                timeout=300
            )
            
            db_result = await self.operations_mcp.execute_operation(db_config)
            print(f"✅ 數據庫維護結果: {db_result.status.value}")
        
        print("\n🎉 運維工作流演示完成！")
    
    async def demo_failure_scenario(self):
        """演示失敗場景處理"""
        print("\n" + "=" * 60)
        print("⚠️ 演示：失敗場景處理")
        print("=" * 60)
        
        # 模擬驗證失敗場景
        print("\n📋 場景 1: 驗證失敗阻止部署")
        print("-" * 40)
        
        # 創建一個會失敗的驗證上下文
        invalid_context = {
            "service_name": "invalid-service",
            "environment": "production",
            "version": "",  # 空版本號會導致驗證失敗
            "strategy": "unknown_strategy"
        }
        
        try:
            verification_result = await self.verification_coordinator.coordinate_verification(
                "deployment", invalid_context
            )
            
            if verification_result["overall_status"] != "PASSED":
                print("✅ 驗證正確地阻止了無效的部署")
                print("📋 失敗原因:")
                for failure in verification_result.get("critical_failures", []):
                    print(f"  - {failure}")
            
        except Exception as e:
            print(f"✅ 驗證正確地捕獲了異常: {str(e)}")
        
        print("\n🎉 失敗場景處理演示完成！")
    
    async def demo_integration_summary(self):
        """演示集成總結"""
        print("\n" + "=" * 60)
        print("📊 PowerAutomation 三件套集成總結")
        print("=" * 60)
        
        print("\n🎯 核心價值:")
        print("  1. ✅ 確保每次操作前都經過驗證")
        print("  2. 🚫 阻止未通過驗證的操作執行")
        print("  3. 📊 提供完整的操作審計和追蹤")
        print("  4. 🔄 支持自動化的故障恢復")
        print("  5. 💡 提供智能的運維建議")
        
        print("\n🏗️ 架構優勢:")
        print("  1. 📦 職責清晰分離")
        print("  2. 🔗 組件間松耦合")
        print("  3. 🔧 易於擴展和定制")
        print("  4. 🛡️ 內建安全和質量保證")
        print("  5. 📈 支持持續改進")
        
        print("\n🎪 工作流程:")
        print("  驗證協調器 → 部署/運維 MCP → 結果反饋 → 持續改進")
        
        print("\n💪 PowerAutomation 原則:")
        print('  "若交付不成功，不同意離開；若格式不正確或結果不好，不同意 review checkin"')
        
        # 獲取統計信息
        verification_history = self.verification_coordinator.get_operation_history()
        deployment_history = self.deployment_mcp.get_deployment_history()
        operations_history = self.operations_mcp.get_operation_history()
        
        print(f"\n📈 演示統計:")
        print(f"  - 驗證操作: {len(verification_history)} 次")
        print(f"  - 部署操作: {len(deployment_history)} 次")
        print(f"  - 運維操作: {len(operations_history)} 次")
        
        print("\n🚀 系統已準備好投入生產使用！")

async def main():
    """主演示函數"""
    print("🎪 PowerAutomation 三件套協同工作演示")
    print("=" * 60)
    print("演示如何通過自動化驗證協調器確保部署和運維操作的質量")
    print()
    
    demo = PowerAutomationIntegrationDemo()
    
    try:
        # 演示完整的部署工作流
        await demo.demo_complete_deployment_workflow()
        
        # 演示運維工作流
        await demo.demo_operations_workflow()
        
        # 演示失敗場景處理
        await demo.demo_failure_scenario()
        
        # 演示集成總結
        await demo.demo_integration_summary()
        
    except Exception as e:
        print(f"❌ 演示過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 PowerAutomation 三件套演示完成！")
    print("💡 提示: 在實際使用中，這些組件將與真實的系統和服務集成")

if __name__ == "__main__":
    asyncio.run(main())

