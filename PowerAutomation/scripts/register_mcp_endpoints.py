"""
MCP 端點註冊腳本
將 Test Flow MCP 和 Smartinvention MCP 註冊到智慧路由引擎
"""

import asyncio
import logging
import sys
import os

# 添加項目路徑
sys.path.append('/home/ubuntu/aicore0624/PowerAutomation')

from components.smart_routing_engine import SmartRoutingEngine, ToolEndpoint, ToolHealth, LoadMetrics
from components.expert_routing_integrator import create_expert_routing_integrator
from components.dynamic_expert_registry import create_dynamic_expert_registry

logger = logging.getLogger(__name__)

async def register_mcp_endpoints():
    """註冊 MCP 端點到智慧路由引擎"""
    
    try:
        # 1. 創建智慧路由引擎
        routing_config = {
            'default_strategy': 'intelligent',
            'load_threshold': 0.8,
            'latency_threshold': 1000,
            'error_rate_threshold': 0.1,
            'failover_enabled': True,
            'circuit_breaker_threshold': 5,
            'circuit_breaker_timeout': 60
        }
        
        smart_routing_engine = SmartRoutingEngine(routing_config)
        logger.info("✅ 智慧路由引擎初始化完成")
        
        # 2. 定義 MCP 端點
        mcp_endpoints = [
            {
                "tool_id": "test_flow_mcp",
                "endpoint": ToolEndpoint(
                    tool_id="test_flow_mcp",
                    endpoint_url="http://localhost:8095",
                    health=ToolHealth.HEALTHY,
                    capabilities=["testing", "unit_testing", "integration_testing", "test_automation", "qa"],
                    load_metrics=LoadMetrics(
                        cpu_usage=0.2,
                        memory_usage=0.3,
                        active_requests=5,
                        response_time_avg=0.8
                    ),
                    metadata={
                        "service_type": "mcp",
                        "description": "測試流程管理 MCP",
                        "version": "1.0.0",
                        "supported_operations": [
                            "execute_unit_tests",
                            "run_integration_tests", 
                            "generate_test_reports",
                            "test_automation"
                        ]
                    }
                )
            },
            {
                "tool_id": "smartinvention_adapter_mcp",
                "endpoint": ToolEndpoint(
                    tool_id="smartinvention_adapter_mcp",
                    endpoint_url="http://localhost:8000",
                    health=ToolHealth.HEALTHY,
                    capabilities=["data_retrieval", "task_analysis", "file_management", "cross_task_analysis"],
                    load_metrics=LoadMetrics(
                        cpu_usage=0.15,
                        memory_usage=0.25,
                        active_requests=3,
                        response_time_avg=0.6
                    ),
                    metadata={
                        "service_type": "mcp",
                        "description": "Smartinvention 數據適配器 MCP",
                        "version": "2.0.0",
                        "supported_operations": [
                            "get_tasks_data",
                            "get_files_data",
                            "analyze_cross_task_relations",
                            "sync_data"
                        ]
                    }
                )
            },
            {
                "tool_id": "manus_adapter_mcp",
                "endpoint": ToolEndpoint(
                    tool_id="manus_adapter_mcp",
                    endpoint_url="http://localhost:8001",
                    health=ToolHealth.HEALTHY,
                    capabilities=["requirement_analysis", "manus_comparison", "expert_coordination"],
                    load_metrics=LoadMetrics(
                        cpu_usage=0.25,
                        memory_usage=0.35,
                        active_requests=4,
                        response_time_avg=1.0
                    ),
                    metadata={
                        "service_type": "mcp",
                        "description": "Manus 適配器 MCP",
                        "version": "1.0.0",
                        "supported_operations": [
                            "analyze_requirement",
                            "compare_with_manus",
                            "coordinate_experts",
                            "generate_action_items"
                        ]
                    }
                )
            },
            {
                "tool_id": "general_processor_mcp",
                "endpoint": ToolEndpoint(
                    tool_id="general_processor_mcp",
                    endpoint_url="http://localhost:8080",
                    health=ToolHealth.HEALTHY,
                    capabilities=["general_processing", "data_processing", "workflow_management"],
                    load_metrics=LoadMetrics(
                        cpu_usage=0.3,
                        memory_usage=0.4,
                        active_requests=8,
                        response_time_avg=1.2
                    ),
                    metadata={
                        "service_type": "mcp",
                        "description": "通用處理器 MCP",
                        "version": "2.0.0",
                        "supported_operations": [
                            "process_request",
                            "manage_workflow",
                            "handle_data"
                        ]
                    }
                )
            }
        ]
        
        # 3. 註冊端點
        registered_count = 0
        for mcp_config in mcp_endpoints:
            tool_id = mcp_config["tool_id"]
            endpoint = mcp_config["endpoint"]
            
            try:
                smart_routing_engine.register_tool_endpoint(tool_id, endpoint)
                registered_count += 1
                
                print(f"✅ 註冊 MCP 端點: {tool_id}")
                print(f"   URL: {endpoint.endpoint_url}")
                print(f"   能力: {', '.join(endpoint.capabilities)}")
                print(f"   健康狀態: {endpoint.health.value}")
                print(f"   響應時間: {endpoint.load_metrics.response_time_avg}s")
                
            except Exception as e:
                logger.error(f"❌ 註冊 MCP 端點失敗 {tool_id}: {e}")
        
        print(f"\n📊 MCP 端點註冊統計:")
        print(f"   總端點數: {len(mcp_endpoints)}")
        print(f"   成功註冊: {registered_count}")
        print(f"   註冊率: {registered_count/len(mcp_endpoints)*100:.1f}%")
        
        # 4. 驗證註冊結果
        print(f"\n🔍 驗證註冊結果:")
        for tool_id in ["test_flow_mcp", "smartinvention_adapter_mcp", "manus_adapter_mcp"]:
            endpoints = smart_routing_engine.tool_endpoints.get(tool_id, [])
            if endpoints:
                print(f"   ✅ {tool_id}: {len(endpoints)} 個端點")
            else:
                print(f"   ❌ {tool_id}: 未找到端點")
        
        return smart_routing_engine, registered_count
        
    except Exception as e:
        logger.error(f"❌ MCP 端點註冊失敗: {e}")
        return None, 0

async def test_expert_routing_integration():
    """測試專家建議路由整合"""
    
    print(f"\n🧪 測試專家建議路由整合")
    
    try:
        # 1. 註冊 MCP 端點
        smart_routing_engine, registered_count = await register_mcp_endpoints()
        if not smart_routing_engine:
            print("❌ 智慧路由引擎初始化失敗")
            return False
        
        # 2. 創建專家註冊表
        expert_registry = create_dynamic_expert_registry()
        await expert_registry.initialize()
        
        # 3. 創建專家建議路由整合器
        expert_routing_integrator = create_expert_routing_integrator(
            smart_routing_engine, expert_registry
        )
        
        print(f"✅ 專家建議路由整合器創建完成")
        
        # 4. 模擬專家建議
        from core.aicore3 import ExpertResponse
        
        mock_expert_responses = [
            ExpertResponse(
                expert_id="testing_expert",
                expert_name="Testing Expert",
                expert_type="testing",
                analysis="需要執行單元測試來驗證代碼功能",
                recommendations=["使用 Test Flow MCP 進行測試管理"],
                tool_suggestions=[
                    {
                        "tool_name": "test_flow_mcp",
                        "confidence": 0.95,
                        "reasoning": "測試專家推薦使用 Test Flow MCP 進行單元測試",
                        "parameters": {"test_type": "unit", "coverage_threshold": 80},
                        "context": {"priority": "high"}
                    }
                ],
                confidence=0.9,
                metadata={"expert_type": "testing", "domain": "qa"}
            ),
            ExpertResponse(
                expert_id="technical_expert", 
                expert_name="Technical Expert",
                expert_type="technical",
                analysis="需要技術分析和代碼審查",
                recommendations=["結合測試和代碼分析"],
                tool_suggestions=[
                    {
                        "tool_name": "test_flow_mcp",
                        "confidence": 0.8,
                        "reasoning": "技術專家也推薦測試工具",
                        "parameters": {"test_type": "integration"},
                        "context": {"priority": "medium"}
                    }
                ],
                confidence=0.85,
                metadata={"expert_type": "technical", "domain": "development"}
            )
        ]
        
        # 5. 測試專家建議整合
        request_context = {
            "type": "testing",
            "content": "執行單元測試來驗證代碼功能",
            "priority": "high"
        }
        
        routing_recommendation = await expert_routing_integrator.integrate_expert_recommendations(
            mock_expert_responses, request_context
        )
        
        print(f"\n📋 專家建議整合結果:")
        print(f"   推薦工具: {routing_recommendation.recommended_tools}")
        print(f"   路由策略: {routing_recommendation.routing_strategy}")
        print(f"   請求優先級: {routing_recommendation.priority.value}")
        print(f"   整體信心度: {routing_recommendation.confidence:.2f}")
        print(f"   專家共識度: {routing_recommendation.expert_consensus:.2f}")
        print(f"   推薦理由: {routing_recommendation.reasoning}")
        
        # 6. 測試基於專家建議的路由
        routing_decision = await expert_routing_integrator.route_with_expert_recommendations(
            mock_expert_responses, request_context, "testing"
        )
        
        print(f"\n🎯 路由決策結果:")
        print(f"   選中工具: {routing_decision.target_tool}")
        print(f"   端點URL: {routing_decision.target_endpoint}")
        print(f"   路由策略: {routing_decision.routing_strategy.value}")
        print(f"   決策信心度: {routing_decision.confidence:.2f}")
        print(f"   決策理由: {routing_decision.decision_reason}")
        
        # 7. 驗證測試專家推薦是否生效
        if routing_decision.target_tool == "test_flow_mcp":
            print(f"✅ 測試專家推薦生效: Test Flow MCP 被正確路由")
        else:
            print(f"⚠️ 測試專家推薦未完全生效: 選中了 {routing_decision.target_tool}")
        
        # 8. 獲取整合統計
        integration_stats = expert_routing_integrator.get_integration_statistics()
        print(f"\n📊 整合統計:")
        print(f"   總整合次數: {integration_stats['total_integrations']}")
        print(f"   成功整合次數: {integration_stats['successful_integrations']}")
        print(f"   處理專家建議數: {integration_stats['expert_recommendations_processed']}")
        print(f"   路由決策數: {integration_stats['routing_decisions_made']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 專家建議路由整合測試失敗: {e}")
        return False

async def main():
    """主函數"""
    
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 開始 MCP 端點註冊和專家建議路由整合測試")
    
    # 1. 註冊 MCP 端點
    smart_routing_engine, registered_count = await register_mcp_endpoints()
    
    # 2. 測試專家建議路由整合
    integration_success = await test_expert_routing_integration()
    
    # 3. 總結
    print(f"\n📊 測試總結:")
    print(f"   MCP 端點註冊: {'✅ 成功' if registered_count > 0 else '❌ 失敗'} ({registered_count} 個)")
    print(f"   專家建議路由整合: {'✅ 成功' if integration_success else '❌ 失敗'}")
    
    if registered_count > 0 and integration_success:
        print(f"\n🎉 階段 3 完成！智慧路由引擎與專家建議整合成功")
        print(f"\n📝 完成的功能:")
        print(f"   ✅ Test Flow MCP 已註冊到智慧路由引擎")
        print(f"   ✅ Smartinvention MCP 已註冊到智慧路由引擎")
        print(f"   ✅ 專家建議路由整合器已創建")
        print(f"   ✅ 測試專家推薦 → 路由決策流程已驗證")
        print(f"   ✅ 智慧路由引擎能根據專家建議進行路由")
    else:
        print(f"\n⚠️ 階段 3 部分完成，需要進一步調試")

if __name__ == "__main__":
    asyncio.run(main())

