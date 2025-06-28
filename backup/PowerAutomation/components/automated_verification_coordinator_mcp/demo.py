#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動化驗證協調器演示腳本
Demo script for Automated Verification Coordinator MCP

展示如何使用自動化驗證協調器來確保操作前的驗證
"""

import asyncio
import json
from main import AutomatedVerificationCoordinator, OperationType

async def demo_deployment_verification():
    """演示部署驗證流程"""
    print("🚀 演示部署驗證流程")
    print("=" * 50)
    
    coordinator = AutomatedVerificationCoordinator()
    
    # 部署上下文
    deployment_context = {
        "environment": "production",
        "service": "api-server",
        "version": "v1.2.0",
        "replicas": 3
    }
    
    print(f"📋 部署上下文: {json.dumps(deployment_context, indent=2, ensure_ascii=False)}")
    print()
    
    # 執行部署驗證
    result = await coordinator.coordinate_verification(
        OperationType.DEPLOYMENT, 
        deployment_context
    )
    
    print("📊 驗證結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    return result

async def demo_testing_verification():
    """演示測試驗證流程"""
    print("🧪 演示測試驗證流程")
    print("=" * 50)
    
    coordinator = AutomatedVerificationCoordinator()
    
    # 測試上下文
    testing_context = {
        "test_suite": "integration",
        "environment": "staging",
        "test_data": "sample_dataset_v1"
    }
    
    print(f"📋 測試上下文: {json.dumps(testing_context, indent=2, ensure_ascii=False)}")
    print()
    
    # 執行測試驗證
    result = await coordinator.coordinate_verification(
        OperationType.TESTING,
        testing_context
    )
    
    print("📊 驗證結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    return result

async def demo_operations_verification():
    """演示運維驗證流程"""
    print("⚙️ 演示運維驗證流程")
    print("=" * 50)
    
    coordinator = AutomatedVerificationCoordinator()
    
    # 運維上下文
    operations_context = {
        "operation": "database_maintenance",
        "maintenance_window": "2025-06-26T02:00:00Z",
        "duration": "2 hours",
        "affected_services": ["api-server", "web-app"]
    }
    
    print(f"📋 運維上下文: {json.dumps(operations_context, indent=2, ensure_ascii=False)}")
    print()
    
    # 執行運維驗證
    result = await coordinator.coordinate_verification(
        OperationType.OPERATIONS,
        operations_context
    )
    
    print("📊 驗證結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    return result

async def demo_release_verification():
    """演示發布驗證流程"""
    print("🎯 演示發布驗證流程")
    print("=" * 50)
    
    coordinator = AutomatedVerificationCoordinator()
    
    # 發布上下文
    release_context = {
        "release_version": "v2.0.0",
        "environment": "production",
        "features": ["user_authentication", "payment_gateway"],
        "rollback_plan": "automatic",
        "monitoring": "enhanced"
    }
    
    print(f"📋 發布上下文: {json.dumps(release_context, indent=2, ensure_ascii=False)}")
    print()
    
    # 執行發布驗證
    result = await coordinator.coordinate_verification(
        OperationType.RELEASE,
        release_context
    )
    
    print("📊 驗證結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    return result

async def demo_verification_history():
    """演示驗證歷史查看"""
    print("📚 演示驗證歷史查看")
    print("=" * 50)
    
    coordinator = AutomatedVerificationCoordinator()
    
    # 先執行一些驗證操作來生成歷史
    await coordinator.coordinate_verification(OperationType.TESTING, {"test": "demo"})
    await coordinator.coordinate_verification(OperationType.DEPLOYMENT, {"deploy": "demo"})
    
    # 查看歷史
    history = coordinator.get_operation_history(limit=10)
    
    print("📊 操作歷史:")
    print(json.dumps(history, indent=2, ensure_ascii=False))
    print()

async def demo_blocked_operations():
    """演示操作阻止機制"""
    print("🚫 演示操作阻止機制")
    print("=" * 50)
    
    coordinator = AutomatedVerificationCoordinator()
    
    # 查看當前被阻止的操作
    blocked = coordinator.get_blocked_operations()
    print(f"🚫 當前被阻止的操作: {blocked}")
    
    # 手動阻止一個操作
    coordinator.blocked_operations.add(OperationType.DEPLOYMENT)
    print("➕ 手動阻止部署操作")
    
    # 嘗試執行被阻止的操作
    result = await coordinator.coordinate_verification(
        OperationType.DEPLOYMENT,
        {"test": "blocked"}
    )
    
    print("📊 被阻止操作的結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 解除阻止
    success = coordinator.unblock_operation("deployment")
    print(f"✅ 解除阻止結果: {success}")
    
    # 再次查看被阻止的操作
    blocked = coordinator.get_blocked_operations()
    print(f"🚫 解除後被阻止的操作: {blocked}")
    print()

async def demo_comprehensive_workflow():
    """演示完整的工作流程"""
    print("🔄 演示完整的工作流程")
    print("=" * 60)
    
    print("這個演示展示了一個典型的發布流程中的驗證協調:")
    print("1. 測試驗證 → 2. 部署驗證 → 3. 發布驗證 → 4. 運維驗證")
    print()
    
    # 1. 測試驗證
    print("🧪 步驟 1: 測試驗證")
    test_result = await demo_testing_verification()
    
    if test_result.get("overall_status") != "PASSED":
        print("❌ 測試驗證失敗，停止流程")
        return
    
    print("✅ 測試驗證通過，繼續部署驗證")
    print()
    
    # 2. 部署驗證
    print("🚀 步驟 2: 部署驗證")
    deploy_result = await demo_deployment_verification()
    
    if deploy_result.get("overall_status") != "PASSED":
        print("❌ 部署驗證失敗，停止流程")
        return
    
    print("✅ 部署驗證通過，繼續發布驗證")
    print()
    
    # 3. 發布驗證
    print("🎯 步驟 3: 發布驗證")
    release_result = await demo_release_verification()
    
    if release_result.get("overall_status") != "PASSED":
        print("❌ 發布驗證失敗，停止流程")
        return
    
    print("✅ 發布驗證通過，繼續運維驗證")
    print()
    
    # 4. 運維驗證
    print("⚙️ 步驟 4: 運維驗證")
    ops_result = await demo_operations_verification()
    
    if ops_result.get("overall_status") != "PASSED":
        print("❌ 運維驗證失敗")
        return
    
    print("✅ 所有驗證通過，發布流程完成！")
    print()
    
    # 顯示完整的操作歷史
    await demo_verification_history()

async def main():
    """主演示函數"""
    print("🎭 自動化驗證協調器演示")
    print("=" * 60)
    print()
    
    demos = [
        ("基礎驗證演示", [
            demo_deployment_verification,
            demo_testing_verification,
            demo_operations_verification,
            demo_release_verification
        ]),
        ("高級功能演示", [
            demo_verification_history,
            demo_blocked_operations
        ]),
        ("完整工作流演示", [
            demo_comprehensive_workflow
        ])
    ]
    
    for category, demo_functions in demos:
        print(f"📂 {category}")
        print("-" * 40)
        
        for demo_func in demo_functions:
            try:
                await demo_func()
                print("✅ 演示完成")
                print()
            except Exception as e:
                print(f"❌ 演示失敗: {str(e)}")
                print()
        
        print()
    
    print("🎉 所有演示完成！")
    print()
    print("💡 使用提示:")
    print("- 在實際使用中，驗證規則會調用真實的系統檢查")
    print("- 可以通過配置文件自定義驗證規則和超時設置")
    print("- 支持與其他 MCP 組件集成，形成完整的自動化流程")
    print("- 遵循 PowerAutomation 質量門禁規範，確保系統可靠性")

if __name__ == "__main__":
    asyncio.run(main())

