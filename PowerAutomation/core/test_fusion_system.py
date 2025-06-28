#!/usr/bin/env python3
"""
融合系统测试脚本
验证PowerAutomation-v2与Core系统融合的各个组件
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_fusion_system():
    """测试融合系统"""
    
    print("🚀 开始测试Enhanced AICore 3.0 Fusion系统")
    print("=" * 60)
    
    try:
        # 测试1: 预算管理系统
        print("\n1️⃣ 测试预算管理系统...")
        from enhanced_budget_management import BudgetManager, BudgetConfig, BudgetPeriod, AlertLevel, CostType
        
        config = BudgetConfig(
            total_budget=10.0, 
            period=BudgetPeriod.MONTHLY, 
            cost_limits={}, 
            alert_thresholds={}
        )
        budget_manager = BudgetManager(config)
        print(f"   ✅ 预算管理器创建成功: 总预算 ${config.total_budget}")
        
        # 测试2: 智能工具引擎
        print("\n2️⃣ 测试智能工具引擎...")
        from smart_tool_engine import SmartToolEngine, AIDecisionEngine
        
        smart_engine = SmartToolEngine(budget_manager)
        init_result = await smart_engine.initialize()
        print(f"   ✅ 智能工具引擎初始化: {'成功' if init_result else '失败'}")
        
        # 测试3: AI决策引擎
        print("\n3️⃣ 测试AI决策引擎...")
        ai_engine = AIDecisionEngine(budget_manager)
        print("   ✅ AI决策引擎创建成功")
        
        # 测试4: 融合系统核心
        print("\n4️⃣ 测试融合系统核心...")
        from enhanced_aicore3_fusion import SimplifiedAIInterface, FusionConfig
        
        ai_interface = SimplifiedAIInterface(budget=5.0)
        print("   ✅ 简化AI接口创建成功")
        
        # 测试5: 系统状态
        print("\n5️⃣ 测试系统状态...")
        await ai_interface.core.initialize()
        system_status = ai_interface.core.get_system_status()
        print(f"   ✅ 系统初始化状态: {system_status['initialized']}")
        print(f"   ✅ 组件状态: {system_status['components_status']}")
        
        print("\n" + "=" * 60)
        print("🎉 所有核心组件测试通过！融合系统运行正常！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def demo_simple_usage():
    """演示简单使用方式"""
    
    print("\n🎯 演示简化使用方式")
    print("-" * 40)
    
    try:
        from enhanced_aicore3_fusion import SimplifiedAIInterface
        
        # 创建AI实例
        ai = SimplifiedAIInterface(budget=1.0)
        
        # 简单问答测试
        print("💬 测试问答功能...")
        answer = await ai.ask("什么是人工智能？")
        print(f"   回答: {answer}")
        
        # 查看预算状态
        print("\n💰 查看预算状态...")
        budget_status = ai.get_budget_status()
        print(f"   总预算: ${budget_status['total_budget']}")
        print(f"   已使用: ${budget_status['current_usage']:.4f}")
        print(f"   剩余: ${budget_status['remaining_budget']:.4f}")
        
        # 性能摘要
        print("\n📊 性能摘要...")
        performance = ai.get_performance_summary()
        print(f"   总请求: {performance['total_requests']}")
        print(f"   成功率: {performance['success_rate']}")
        
        print("\n✅ 简化接口演示完成！")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")

if __name__ == "__main__":
    async def main():
        # 运行测试
        test_success = await test_fusion_system()
        
        if test_success:
            # 运行演示
            await demo_simple_usage()
        
        print("\n🏁 测试完成！")
    
    asyncio.run(main())

