# -*- coding: utf-8 -*-
"""
增強版簡化Agent架構 - 測試套件
Enhanced Simplified Agent Architecture - Test Suite
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

# 導入測試目標
from ..core.enhanced_agent_core import EnhancedAgentCore
from ..tools.enhanced_tool_registry import EnhancedToolRegistry
from ..actions.action_executor import ActionExecutor
from ..config.enhanced_config import create_enhanced_config
from ..core.agent_core import AgentRequest, Priority, TaskStatus

class TestEnhancedAgentCore:
    """增強版Agent Core測試"""
    
    @pytest.fixture
    async def agent_setup(self):
        """測試設置"""
        config = create_enhanced_config('testing')
        
        # 創建模擬的依賴
        tool_registry = Mock(spec=EnhancedToolRegistry)
        action_executor = Mock(spec=ActionExecutor)
        
        # 設置模擬方法
        tool_registry.find_optimal_tools = AsyncMock(return_value={
            'success': True,
            'selected_tool': {
                'id': 'test_tool',
                'name': 'Test Tool',
                'platform': 'test',
                'cost_model': {'type': 'free', 'cost_per_call': 0.0},
                'performance_metrics': {'success_rate': 0.95, 'avg_response_time': 1000},
                'quality_scores': {'user_rating': 4.5}
            },
            'alternatives': []
        })
        
        tool_registry.execute_with_smart_tool = AsyncMock(return_value={
            'success': True,
            'result': {'analysis': 'Test analysis result'},
            'execution_time': 1.5
        })
        
        action_executor.execute = AsyncMock(return_value={
            'success': True,
            'result': 'Test execution result',
            'execution_time': 2.0
        })
        
        # 創建Agent Core
        agent_core = EnhancedAgentCore(config)
        agent_core.set_enhanced_dependencies(tool_registry, action_executor)
        
        return {
            'agent_core': agent_core,
            'tool_registry': tool_registry,
            'action_executor': action_executor,
            'config': config
        }
    
    @pytest.mark.asyncio
    async def test_basic_request_processing(self, agent_setup):
        """測試基本請求處理"""
        setup = await agent_setup
        agent_core = setup['agent_core']
        
        request = AgentRequest(
            content="測試分析請求",
            priority=Priority.MEDIUM
        )
        
        response = await agent_core.process_request(request)
        
        assert response.request_id == request.id
        assert response.status == TaskStatus.COMPLETED
        assert response.execution_time > 0
        assert response.confidence > 0
    
    @pytest.mark.asyncio
    async def test_intelligent_tool_selection(self, agent_setup):
        """測試智能工具選擇"""
        setup = await agent_setup
        agent_core = setup['agent_core']
        tool_registry = setup['tool_registry']
        
        request = AgentRequest(
            content="進行深度分析",
            priority=Priority.HIGH,
            context={'quality_critical': True}
        )
        
        response = await agent_core.process_request(request)
        
        # 驗證工具選擇被調用
        tool_registry.find_optimal_tools.assert_called_once()
        
        # 驗證響應
        assert response.status == TaskStatus.COMPLETED
        assert response.metadata['enhanced_processing'] == True
    
    @pytest.mark.asyncio
    async def test_cost_optimization(self, agent_setup):
        """測試成本優化"""
        setup = await agent_setup
        agent_core = setup['agent_core']
        
        request = AgentRequest(
            content="成本敏感的分析",
            priority=Priority.LOW,
            context={
                'max_cost': 0.001,
                'prefer_free': True
            }
        )
        
        response = await agent_core.process_request(request)
        
        # 驗證成本優化統計
        stats = agent_core.get_enhanced_status()
        assert stats['enhanced_stats']['smart_decisions'] > 0
    
    @pytest.mark.asyncio
    async def test_fallback_mechanism(self, agent_setup):
        """測試回退機制"""
        setup = await agent_setup
        agent_core = setup['agent_core']
        tool_registry = setup['tool_registry']
        
        # 模擬工具選擇失敗
        tool_registry.find_optimal_tools.side_effect = Exception("Tool selection failed")
        
        request = AgentRequest(
            content="測試回退機制",
            priority=Priority.MEDIUM
        )
        
        response = await agent_core.process_request(request)
        
        # 驗證回退統計
        stats = agent_core.get_enhanced_status()
        assert stats['enhanced_stats']['fallback_activations'] > 0
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, agent_setup):
        """測試性能監控"""
        setup = await agent_setup
        agent_core = setup['agent_core']
        
        # 執行多個請求
        requests = [
            AgentRequest(content=f"請求 {i}", priority=Priority.MEDIUM)
            for i in range(3)
        ]
        
        for request in requests:
            await agent_core.process_request(request)
        
        # 檢查統計信息
        stats = agent_core.get_enhanced_status()
        assert stats['enhanced_stats']['smart_decisions'] == 3

class TestEnhancedToolRegistry:
    """增強版Tool Registry測試"""
    
    @pytest.fixture
    def registry_setup(self):
        """Registry測試設置"""
        config = create_enhanced_config('testing')
        config['smart_engine']['enable_cloud_tools'] = False  # 測試環境禁用
        
        return config
    
    @pytest.mark.asyncio
    async def test_tool_discovery(self, registry_setup):
        """測試工具發現"""
        with patch('..tools.enhanced_tool_registry.SmartToolEngineMCP') as mock_engine:
            # 模擬Smart Tool Engine
            mock_instance = Mock()
            mock_instance.process.return_value = {
                'success': True,
                'tools': [
                    {
                        'id': 'test_tool_1',
                        'name': 'Test Tool 1',
                        'capabilities': ['analysis']
                    }
                ]
            }
            mock_engine.return_value = mock_instance
            
            registry = EnhancedToolRegistry(registry_setup)
            await registry.initialize()
            
            # 測試工具發現
            tools = await registry._discover_smart_tools()
            assert len(tools) > 0
            assert tools[0]['id'] == 'test_tool_1'
    
    @pytest.mark.asyncio
    async def test_optimal_tool_selection(self, registry_setup):
        """測試最優工具選擇"""
        with patch('..tools.enhanced_tool_registry.SmartToolEngineMCP') as mock_engine:
            # 模擬路由引擎
            mock_instance = Mock()
            mock_routing = Mock()
            mock_routing.select_optimal_tool.return_value = {
                'success': True,
                'selected_tool': {
                    'id': 'optimal_tool',
                    'name': 'Optimal Tool',
                    'cost_model': {'type': 'free'},
                    'performance_metrics': {'success_rate': 0.98}
                }
            }
            mock_instance.execution_engine.routing_engine = mock_routing
            mock_engine.return_value = mock_instance
            
            registry = EnhancedToolRegistry(registry_setup)
            await registry.initialize()
            
            # 測試最優選擇
            result = await registry.find_optimal_tools("測試需求")
            assert result['success'] == True
            assert result['selected_tool']['id'] == 'optimal_tool'

class TestIntegration:
    """整合測試"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """端到端工作流測試"""
        config = create_enhanced_config('testing')
        
        with patch('..tools.enhanced_tool_registry.SmartToolEngineMCP'):
            # 創建完整的系統
            tool_registry = EnhancedToolRegistry(config)
            await tool_registry.initialize()
            
            action_executor = ActionExecutor(config)
            
            agent_core = EnhancedAgentCore(config)
            agent_core.set_enhanced_dependencies(tool_registry, action_executor)
            
            # 執行端到端測試
            request = AgentRequest(
                content="執行完整的分析工作流",
                priority=Priority.HIGH,
                context={'test_mode': True}
            )
            
            start_time = time.time()
            response = await agent_core.process_request(request)
            end_time = time.time()
            
            # 驗證結果
            assert response.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
            assert response.execution_time > 0
            assert end_time - start_time < 30  # 不應超過30秒
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """並發請求測試"""
        config = create_enhanced_config('testing')
        config['agent_core']['max_concurrent_requests'] = 3
        
        with patch('..tools.enhanced_tool_registry.SmartToolEngineMCP'):
            # 創建系統
            tool_registry = EnhancedToolRegistry(config)
            await tool_registry.initialize()
            
            action_executor = ActionExecutor(config)
            
            agent_core = EnhancedAgentCore(config)
            agent_core.set_enhanced_dependencies(tool_registry, action_executor)
            
            # 創建並發請求
            requests = [
                AgentRequest(
                    content=f"並發請求 {i}",
                    priority=Priority.MEDIUM
                )
                for i in range(5)
            ]
            
            # 並發執行
            tasks = [
                agent_core.process_request(request)
                for request in requests
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 驗證結果
            successful_responses = [
                r for r in responses 
                if not isinstance(r, Exception) and r.status == TaskStatus.COMPLETED
            ]
            
            assert len(successful_responses) > 0  # 至少有一些成功

class TestPerformance:
    """性能測試"""
    
    @pytest.mark.asyncio
    async def test_response_time(self):
        """響應時間測試"""
        config = create_enhanced_config('testing')
        
        with patch('..tools.enhanced_tool_registry.SmartToolEngineMCP'):
            tool_registry = EnhancedToolRegistry(config)
            await tool_registry.initialize()
            
            action_executor = ActionExecutor(config)
            agent_core = EnhancedAgentCore(config)
            agent_core.set_enhanced_dependencies(tool_registry, action_executor)
            
            request = AgentRequest(
                content="性能測試請求",
                priority=Priority.MEDIUM
            )
            
            start_time = time.time()
            response = await agent_core.process_request(request)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # 驗證響應時間在合理範圍內
            assert response_time < 10.0  # 不應超過10秒
            assert response.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """記憶體使用測試"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        config = create_enhanced_config('testing')
        
        with patch('..tools.enhanced_tool_registry.SmartToolEngineMCP'):
            # 創建多個實例
            instances = []
            for i in range(10):
                tool_registry = EnhancedToolRegistry(config)
                await tool_registry.initialize()
                
                action_executor = ActionExecutor(config)
                agent_core = EnhancedAgentCore(config)
                agent_core.set_enhanced_dependencies(tool_registry, action_executor)
                
                instances.append((tool_registry, action_executor, agent_core))
            
            current_memory = process.memory_info().rss
            memory_increase = current_memory - initial_memory
            
            # 記憶體增長應該在合理範圍內（小於100MB）
            assert memory_increase < 100 * 1024 * 1024

# 測試配置
pytest_plugins = ['pytest_asyncio']

# 運行測試的主函數
def run_tests():
    """運行所有測試"""
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--asyncio-mode=auto'
    ])

if __name__ == "__main__":
    run_tests()

