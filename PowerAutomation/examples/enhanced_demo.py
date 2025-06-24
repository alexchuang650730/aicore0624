# -*- coding: utf-8 -*-
"""
增強版簡化Agent架構 - 完整使用示例
Enhanced Simplified Agent Architecture - Complete Usage Examples
"""

import asyncio
import logging
from typing import Dict, Any

# 導入增強版組件
from ..core.enhanced_agent_core import EnhancedAgentCore, create_enhanced_agent_core
from ..tools.enhanced_tool_registry import EnhancedToolRegistry, create_enhanced_tool_registry
from ..actions.action_executor import ActionExecutor
from ..config.enhanced_config import create_enhanced_config
from ..core.agent_core import AgentRequest, Priority

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedAgentDemo:
    """增強版Agent演示類"""
    
    def __init__(self):
        self.agent_core = None
        self.tool_registry = None
        self.action_executor = None
        self.config = None
    
    async def initialize(self, environment: str = 'development'):
        """初始化增強版Agent"""
        try:
            # 載入配置
            self.config = create_enhanced_config(environment)
            logger.info(f"Configuration loaded for environment: {environment}")
            
            # 創建Tool Registry
            self.tool_registry = await create_enhanced_tool_registry(self.config)
            logger.info("Enhanced Tool Registry created")
            
            # 創建Action Executor
            self.action_executor = ActionExecutor(self.config)
            logger.info("Action Executor created")
            
            # 創建Agent Core
            self.agent_core = await create_enhanced_agent_core(
                self.config, 
                self.tool_registry, 
                self.action_executor
            )
            logger.info("Enhanced Agent Core created")
            
            logger.info("Enhanced Agent initialization completed successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Agent: {e}")
            raise
    
    async def demo_basic_analysis(self):
        """演示基本分析功能"""
        print("\n🔍 演示：基本分析功能")
        print("=" * 50)
        
        request = AgentRequest(
            content="請分析當前系統的運行狀態和性能指標",
            priority=Priority.MEDIUM,
            context={
                'analysis_type': 'system_monitoring',
                'detail_level': 'comprehensive'
            }
        )
        
        response = await self.agent_core.process_request(request)
        
        print(f"請求ID: {response.request_id}")
        print(f"狀態: {response.status}")
        print(f"執行時間: {response.execution_time:.2f}秒")
        print(f"使用工具: {response.tools_used}")
        print(f"信心度: {response.confidence:.2f}")
        
        if response.metadata:
            print(f"增強處理: {response.metadata.get('enhanced_processing', False)}")
            print(f"Smart Engine使用: {response.metadata.get('smart_engine_used', False)}")
        
        return response
    
    async def demo_smart_tool_selection(self):
        """演示智能工具選擇"""
        print("\n🧠 演示：智能工具選擇")
        print("=" * 50)
        
        # 測試不同類型的需求
        test_cases = [
            {
                'content': '搜索最新的AI技術趨勢',
                'expected_type': 'search'
            },
            {
                'content': '分析用戶界面的可用性問題',
                'expected_type': 'analysis'
            },
            {
                'content': '監控服務器性能指標',
                'expected_type': 'monitoring'
            }
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n測試案例 {i}: {case['content']}")
            
            # 使用智能工具選擇
            optimal_tools = await self.tool_registry.find_optimal_tools(
                case['content'],
                {'prefer_free': True, 'max_cost': 0.01}
            )
            
            if optimal_tools['success']:
                selected_tool = optimal_tools['selected_tool']
                print(f"  選擇工具: {selected_tool['name']}")
                print(f"  平台: {selected_tool.get('platform', 'unknown')}")
                print(f"  成本類型: {selected_tool['cost_model']['type']}")
                print(f"  成功率: {selected_tool['performance_metrics']['success_rate']:.2%}")
                
                alternatives = optimal_tools.get('alternatives', [])
                if alternatives:
                    print(f"  備選方案: {len(alternatives)}個")
            else:
                print(f"  工具選擇失敗: {optimal_tools.get('error', 'Unknown error')}")
    
    async def demo_cost_optimization(self):
        """演示成本優化"""
        print("\n💰 演示：成本優化")
        print("=" * 50)
        
        # 測試成本敏感的請求
        request = AgentRequest(
            content="進行深度市場分析和競爭對手研究",
            priority=Priority.HIGH,
            context={
                'budget_limit': 5.0,
                'prefer_free': True,
                'max_cost': 0.005,
                'quality_critical': False
            }
        )
        
        # 使用優化工具選擇
        optimization_result = await self.tool_registry.optimize_tool_selection(
            request.content,
            {
                'max_cost': 0.005,
                'min_success_rate': 0.9,
                'max_response_time': 3000
            }
        )
        
        if optimization_result['success']:
            selected_tool = optimization_result['selected_tool']
            print(f"優化選擇: {selected_tool['name']}")
            print(f"成本: {selected_tool['cost_model']['cost_per_call']}")
            print(f"性能: {selected_tool['performance_metrics']['avg_response_time']}ms")
            
            suggestions = optimization_result.get('optimization_suggestions', [])
            if suggestions:
                print("優化建議:")
                for suggestion in suggestions:
                    print(f"  - {suggestion}")
        else:
            print(f"優化失敗: {optimization_result.get('error')}")
    
    async def demo_adapter_integration(self):
        """演示Adapter MCP整合"""
        print("\n🔌 演示：Adapter MCP整合")
        print("=" * 50)
        
        # 測試不同的adapter功能
        adapter_tests = [
            {
                'name': '高級分析',
                'content': '分析產品銷售數據的趨勢和模式',
                'expected_adapter': 'advanced_analysis'
            },
            {
                'name': '雲端搜索',
                'content': '搜索關於機器學習的最新研究論文',
                'expected_adapter': 'cloud_search'
            },
            {
                'name': 'UI分析',
                'content': '評估網站首頁的用戶體驗設計',
                'expected_adapter': 'smartui'
            }
        ]
        
        for test in adapter_tests:
            print(f"\n測試 {test['name']}: {test['content']}")
            
            request = AgentRequest(
                content=test['content'],
                priority=Priority.MEDIUM,
                context={'prefer_adapters': True}
            )
            
            response = await self.agent_core.process_request(request)
            
            print(f"  狀態: {response.status}")
            print(f"  執行時間: {response.execution_time:.2f}秒")
            
            if response.metadata:
                adapter_used = any('adapter' in tool.lower() for tool in response.tools_used)
                print(f"  使用Adapter: {adapter_used}")
    
    async def demo_performance_monitoring(self):
        """演示性能監控"""
        print("\n📊 演示：性能監控")
        print("=" * 50)
        
        # 獲取增強統計信息
        agent_stats = self.agent_core.get_enhanced_status()
        registry_stats = self.tool_registry.get_enhanced_stats()
        
        print("Agent Core統計:")
        print(f"  智能決策次數: {agent_stats['enhanced_stats']['smart_decisions']}")
        print(f"  成本優化次數: {agent_stats['enhanced_stats']['cost_optimizations']}")
        print(f"  性能改進次數: {agent_stats['enhanced_stats']['performance_improvements']}")
        print(f"  回退激活次數: {agent_stats['enhanced_stats']['fallback_activations']}")
        
        print("\nTool Registry統計:")
        print(f"  發現的智能工具: {registry_stats['enhanced_features']['smart_tools_discovered']}")
        print(f"  智能選擇次數: {registry_stats['enhanced_features']['intelligent_selections']}")
        print(f"  Adapter工具使用: {registry_stats['enhanced_features'].get('adapter_tool_usage', 0)}")
        
        # 健康檢查
        health_status = await self.tool_registry.health_check_enhanced()
        print(f"\n系統健康狀態: {'✅ 正常' if health_status['overall_health'] else '❌ 異常'}")
    
    async def demo_error_handling(self):
        """演示錯誤處理和回退機制"""
        print("\n🛡️ 演示：錯誤處理和回退機制")
        print("=" * 50)
        
        # 測試無效請求
        invalid_request = AgentRequest(
            content="",  # 空內容
            priority=Priority.LOW
        )
        
        response = await self.agent_core.process_request(invalid_request)
        print(f"空請求處理: {response.status}")
        
        # 測試超時請求
        timeout_request = AgentRequest(
            content="執行一個需要很長時間的複雜分析",
            priority=Priority.URGENT,
            timeout=1  # 1秒超時
        )
        
        response = await self.agent_core.process_request(timeout_request)
        print(f"超時請求處理: {response.status}")
        
        # 檢查回退統計
        stats = self.agent_core.get_enhanced_status()
        print(f"回退激活次數: {stats['enhanced_stats']['fallback_activations']}")
    
    async def run_complete_demo(self):
        """運行完整演示"""
        print("🚀 增強版簡化Agent架構 - 完整演示")
        print("=" * 60)
        
        try:
            # 初始化
            await self.initialize()
            
            # 運行各種演示
            await self.demo_basic_analysis()
            await self.demo_smart_tool_selection()
            await self.demo_cost_optimization()
            await self.demo_adapter_integration()
            await self.demo_performance_monitoring()
            await self.demo_error_handling()
            
            print("\n✅ 所有演示完成！")
            
        except Exception as e:
            logger.error(f"演示運行失敗: {e}")
            print(f"\n❌ 演示失敗: {e}")

# 快捷使用函數
async def quick_analysis(content: str, environment: str = 'development') -> Dict[str, Any]:
    """
    快速分析函數
    
    Args:
        content: 分析內容
        environment: 環境配置
        
    Returns:
        分析結果
    """
    demo = EnhancedAgentDemo()
    await demo.initialize(environment)
    
    request = AgentRequest(content=content, priority=Priority.MEDIUM)
    response = await demo.agent_core.process_request(request)
    
    return {
        'success': response.status.value == 'completed',
        'result': response.result,
        'execution_time': response.execution_time,
        'tools_used': response.tools_used,
        'confidence': response.confidence
    }

async def quick_search(query: str, environment: str = 'development') -> Dict[str, Any]:
    """
    快速搜索函數
    
    Args:
        query: 搜索查詢
        environment: 環境配置
        
    Returns:
        搜索結果
    """
    demo = EnhancedAgentDemo()
    await demo.initialize(environment)
    
    # 使用智能工具選擇進行搜索
    result = await demo.tool_registry.find_optimal_tools(
        f"搜索: {query}",
        {'prefer_free': True}
    )
    
    return result

async def quick_monitor(target: str = "system", environment: str = 'development') -> Dict[str, Any]:
    """
    快速監控函數
    
    Args:
        target: 監控目標
        environment: 環境配置
        
    Returns:
        監控結果
    """
    demo = EnhancedAgentDemo()
    await demo.initialize(environment)
    
    request = AgentRequest(
        content=f"監控{target}的狀態和性能",
        priority=Priority.HIGH,
        context={'monitoring_target': target}
    )
    
    response = await demo.agent_core.process_request(request)
    
    return {
        'success': response.status.value == 'completed',
        'monitoring_data': response.result,
        'tools_used': response.tools_used
    }

# 主程序
async def main():
    """主演示程序"""
    demo = EnhancedAgentDemo()
    await demo.run_complete_demo()

if __name__ == "__main__":
    asyncio.run(main())

