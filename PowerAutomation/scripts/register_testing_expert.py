"""
測試專家註冊腳本
將測試專家註冊到 AICore 動態專家註冊表中
"""

import asyncio
import logging
import sys
import os

# 添加項目路徑
sys.path.append('/home/ubuntu/aicore0624/PowerAutomation')

from components.dynamic_expert_registry import create_dynamic_expert_registry
from components.testing_expert_config import create_testing_expert

logger = logging.getLogger(__name__)

async def register_testing_expert():
    """註冊測試專家到動態專家註冊表"""
    
    try:
        # 1. 創建動態專家註冊中心
        expert_registry = create_dynamic_expert_registry()
        await expert_registry.initialize()
        
        logger.info("✅ 動態專家註冊中心初始化完成")
        
        # 2. 創建測試專家
        testing_expert = create_testing_expert()
        
        logger.info(f"✅ 測試專家配置創建完成: {testing_expert.name}")
        
        # 3. 註冊測試專家
        registered_expert = await expert_registry.register_expert_directly(testing_expert)
        
        logger.info(f"🎉 測試專家註冊成功: {registered_expert.id}")
        
        # 4. 驗證註冊結果
        retrieved_expert = await expert_registry.get_expert_by_id("testing_expert")
        if retrieved_expert:
            logger.info(f"✅ 驗證成功: 測試專家已成功註冊到系統")
            
            # 顯示專家信息
            print(f"\n📋 測試專家信息:")
            print(f"ID: {retrieved_expert.id}")
            print(f"名稱: {retrieved_expert.name}")
            print(f"類型: {retrieved_expert.type.value}")
            print(f"狀態: {retrieved_expert.status.value}")
            print(f"專業領域: {', '.join(retrieved_expert.specializations)}")
            print(f"能力數量: {len(retrieved_expert.capabilities)}")
            
            # 顯示核心能力
            print(f"\n🎯 核心能力:")
            for capability in retrieved_expert.capabilities[:5]:  # 顯示前5個能力
                print(f"  - {capability.name}: {capability.description}")
            
            # 顯示工具推薦
            tool_recommendations = retrieved_expert.knowledge_base.get("tool_recommendations", [])
            if tool_recommendations:
                print(f"\n🔧 工具推薦:")
                for tool in tool_recommendations:
                    print(f"  - {tool['tool_name']}: {tool.get('confidence', 0):.2f} 信心度")
                    print(f"    觸發關鍵字: {', '.join(tool.get('trigger_keywords', [])[:5])}")
        else:
            logger.error("❌ 驗證失敗: 無法從系統中檢索測試專家")
            return False
        
        # 5. 測試專家查找功能
        testing_experts = await expert_registry.get_experts_by_domain("testing")
        logger.info(f"✅ 測試領域專家數量: {len(testing_experts)}")
        
        qa_experts = await expert_registry.get_experts_by_capability("quality_assurance")
        logger.info(f"✅ 質量保證能力專家數量: {len(qa_experts)}")
        
        # 6. 顯示統計信息
        stats = expert_registry.get_expert_statistics()
        print(f"\n📊 專家註冊統計:")
        print(f"總專家數: {stats['total_experts']}")
        print(f"活躍專家數: {stats['active_experts']}")
        print(f"領域數: {stats['domains']}")
        print(f"能力數: {stats['capabilities']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 測試專家註冊失敗: {e}")
        return False

async def test_testing_expert_recommendations():
    """測試測試專家的工具推薦功能"""
    
    from components.testing_expert_config import (
        get_testing_expert_tool_recommendations,
        should_recommend_test_flow_mcp
    )
    
    # 測試用例
    test_cases = [
        {
            "content": "我需要執行單元測試來驗證代碼功能",
            "expected": True
        },
        {
            "content": "請幫我進行性能測試和負載測試",
            "expected": True
        },
        {
            "content": "需要自動化測試框架來提高測試效率",
            "expected": True
        },
        {
            "content": "請分析用戶界面設計需求",
            "expected": False
        },
        {
            "content": "幫我查詢數據庫中的用戶信息",
            "expected": False
        }
    ]
    
    print(f"\n🧪 測試專家推薦功能測試:")
    
    for i, test_case in enumerate(test_cases, 1):
        content = test_case["content"]
        expected = test_case["expected"]
        
        # 測試工具推薦
        recommendations = get_testing_expert_tool_recommendations(content)
        has_recommendations = len(recommendations) > 0
        
        # 測試推薦判斷
        should_recommend = should_recommend_test_flow_mcp({"content": content})
        
        # 驗證結果
        result = has_recommendations == expected and should_recommend == expected
        status = "✅ 通過" if result else "❌ 失敗"
        
        print(f"  測試 {i}: {status}")
        print(f"    輸入: {content}")
        print(f"    預期: {'推薦' if expected else '不推薦'} Test Flow MCP")
        print(f"    實際: {'推薦' if has_recommendations else '不推薦'} Test Flow MCP")
        
        if has_recommendations:
            rec = recommendations[0]
            print(f"    信心度: {rec.get('confidence', 0):.2f}")
            print(f"    匹配關鍵字: {', '.join(rec.get('matched_keywords', [])[:3])}")
        print()
    
    return True

async def main():
    """主函數"""
    
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 開始註冊測試專家到 AICore 系統")
    
    # 1. 註冊測試專家
    success = await register_testing_expert()
    if not success:
        print("❌ 測試專家註冊失敗")
        return
    
    # 2. 測試推薦功能
    await test_testing_expert_recommendations()
    
    print("🎉 測試專家註冊和測試完成！")
    print("\n📝 下一步:")
    print("1. 測試專家已成功註冊到 AICore 動態專家註冊表")
    print("2. 測試專家會自動識別測試相關請求")
    print("3. 當識別到測試需求時，會推薦使用 Test Flow MCP")
    print("4. 智慧路由引擎將根據專家建議進行路由決策")

if __name__ == "__main__":
    asyncio.run(main())

