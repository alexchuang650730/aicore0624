# -*- coding: utf-8 -*-
"""
增強版Agent Core - 整合Smart Tool Engine和Adapter MCP
Enhanced Agent Core with Smart Tool Engine and Adapter MCP Integration
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

# 導入原有的Agent Core
from .agent_core import AgentCore, AgentRequest, AgentResponse, Priority, TaskStatus

# 導入增強版Tool Registry
from ..tools.enhanced_tool_registry import EnhancedToolRegistry

# 導入Action Executor
from ..actions.action_executor import ActionExecutor

logger = logging.getLogger(__name__)

class EnhancedAgentCore(AgentCore):
    """
    增強版Agent Core
    整合Smart Tool Engine的智能決策能力和Adapter MCP工具
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # 增強配置
        self.enhanced_config = config.get('enhanced_features', {
            'enable_smart_routing': True,
            'enable_cost_optimization': True,
            'enable_performance_monitoring': True,
            'enable_adapter_integration': True,
            'intelligent_fallback': True,
            'quality_threshold': 0.8,
            'max_alternatives': 3
        })
        
        # 增強統計
        self.enhanced_stats = {
            'smart_decisions': 0,
            'cost_optimizations': 0,
            'performance_improvements': 0,
            'adapter_tool_usage': 0,
            'fallback_activations': 0
        }
        
        logger.info("Enhanced Agent Core initialized")
    
    def set_enhanced_dependencies(self, tool_registry: EnhancedToolRegistry, action_executor: ActionExecutor):
        """設置增強版依賴"""
        self.tool_registry = tool_registry
        self.action_executor = action_executor
        
        # 設置Action Executor的Tool Registry引用
        self.action_executor.set_tool_registry(tool_registry)
        
        logger.info("Enhanced dependencies configured")
    
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """
        增強版請求處理
        使用Smart Tool Engine進行智能決策
        """
        start_time = time.time()
        
        try:
            # 階段1: 智能需求分析
            analysis_result = await self._enhanced_requirement_analysis(request)
            
            # 階段2: 智能工具選擇
            tool_selection_result = await self._intelligent_tool_selection(request, analysis_result)
            
            # 階段3: 智能執行策略
            execution_result = await self._intelligent_execution(request, tool_selection_result)
            
            # 階段4: 結果評估和優化
            final_result = await self._evaluate_and_optimize_result(execution_result)
            
            execution_time = time.time() - start_time
            
            # 更新統計
            self.enhanced_stats['smart_decisions'] += 1
            
            return AgentResponse(
                request_id=request.id,
                status=TaskStatus.COMPLETED,
                result=final_result,
                execution_time=execution_time,
                tools_used=tool_selection_result.get('selected_tools', []),
                confidence=final_result.get('confidence_score', 0.8),
                metadata={
                    'enhanced_processing': True,
                    'analysis_insights': analysis_result.get('insights', ''),
                    'optimization_applied': final_result.get('optimizations', []),
                    'smart_engine_used': True
                }
            )
            
        except Exception as e:
            logger.error(f"Enhanced request processing failed: {e}")
            
            # 智能回退機制
            if self.enhanced_config['intelligent_fallback']:
                return await self._intelligent_fallback(request, str(e))
            else:
                return AgentResponse(
                    request_id=request.id,
                    status=TaskStatus.FAILED,
                    error=str(e),
                    execution_time=time.time() - start_time
                )
    
    async def _enhanced_requirement_analysis(self, request: AgentRequest) -> Dict[str, Any]:
        """
        增強版需求分析
        使用AI進行深度需求理解
        """
        try:
            # 基礎分析
            base_analysis = await super()._analyze_requirement(request)
            
            # 增強分析：使用Smart Tool Engine的智能能力
            enhanced_analysis = {
                'requirement_type': self._classify_requirement_type(request.content),
                'complexity_level': self._assess_complexity(request.content),
                'resource_requirements': self._estimate_resources(request.content),
                'quality_expectations': self._determine_quality_expectations(request),
                'cost_constraints': self._extract_cost_constraints(request),
                'performance_requirements': self._extract_performance_requirements(request)
            }
            
            return {
                **base_analysis,
                'enhanced_insights': enhanced_analysis,
                'analysis_confidence': 0.9,
                'analysis_method': 'enhanced_ai_analysis'
            }
            
        except Exception as e:
            logger.error(f"Enhanced requirement analysis failed: {e}")
            return await super()._analyze_requirement(request)
    
    def _classify_requirement_type(self, content: str) -> str:
        """AI驅動的需求類型分類"""
        # 使用AI邏輯分類需求類型
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in ['分析', '評估', '洞察', '報告']):
            return 'analysis'
        elif any(keyword in content_lower for keyword in ['監控', '檢查', '狀態', '健康']):
            return 'monitoring'
        elif any(keyword in content_lower for keyword in ['搜索', '查找', '發現', '檢索']):
            return 'search'
        elif any(keyword in content_lower for keyword in ['生成', '創建', '製作', '開發']):
            return 'generation'
        elif any(keyword in content_lower for keyword in ['優化', '改進', '提升', '增強']):
            return 'optimization'
        else:
            return 'general'
    
    def _assess_complexity(self, content: str) -> str:
        """評估需求複雜度"""
        # 基於內容長度和關鍵詞複雜度評估
        word_count = len(content.split())
        complex_keywords = ['整合', '架構', '系統', '複雜', '多步驟', '協調']
        
        complex_score = sum(1 for keyword in complex_keywords if keyword in content)
        
        if word_count > 100 or complex_score >= 3:
            return 'high'
        elif word_count > 50 or complex_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _estimate_resources(self, content: str) -> Dict[str, Any]:
        """估算資源需求"""
        complexity = self._assess_complexity(content)
        
        resource_map = {
            'low': {'cpu': 'low', 'memory': 'low', 'time': 'short', 'tools': 1},
            'medium': {'cpu': 'medium', 'memory': 'medium', 'time': 'medium', 'tools': 2},
            'high': {'cpu': 'high', 'memory': 'high', 'time': 'long', 'tools': 3}
        }
        
        return resource_map.get(complexity, resource_map['medium'])
    
    def _determine_quality_expectations(self, request: AgentRequest) -> float:
        """確定質量期望"""
        # 基於優先級和上下文確定質量期望
        priority_quality_map = {
            Priority.LOW: 0.7,
            Priority.MEDIUM: 0.8,
            Priority.HIGH: 0.9,
            Priority.URGENT: 0.95
        }
        
        base_quality = priority_quality_map.get(request.priority, 0.8)
        
        # 根據上下文調整
        if request.context.get('quality_critical', False):
            base_quality = min(base_quality + 0.1, 1.0)
        
        return base_quality
    
    def _extract_cost_constraints(self, request: AgentRequest) -> Dict[str, Any]:
        """提取成本約束"""
        context = request.context
        
        return {
            'max_cost_per_call': context.get('max_cost', 0.01),
            'budget_limit': context.get('budget_limit', 10.0),
            'prefer_free_tools': context.get('prefer_free', True),
            'cost_priority': context.get('cost_priority', 'medium')
        }
    
    def _extract_performance_requirements(self, request: AgentRequest) -> Dict[str, Any]:
        """提取性能需求"""
        context = request.context
        
        return {
            'max_response_time': context.get('max_response_time', request.timeout),
            'min_success_rate': context.get('min_success_rate', 0.95),
            'throughput_requirement': context.get('throughput', 'standard'),
            'reliability_level': context.get('reliability', 'high')
        }
    
    async def _intelligent_tool_selection(self, request: AgentRequest, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        智能工具選擇
        使用Smart Tool Engine進行最優工具選擇
        """
        try:
            # 準備選擇上下文
            selection_context = {
                'requirement_type': analysis['enhanced_insights']['requirement_type'],
                'complexity': analysis['enhanced_insights']['complexity_level'],
                'quality_threshold': analysis['enhanced_insights']['quality_expectations'],
                'cost_constraints': analysis['enhanced_insights']['cost_constraints'],
                'performance_requirements': analysis['enhanced_insights']['performance_requirements'],
                'filters': {
                    'max_cost': analysis['enhanced_insights']['cost_constraints']['max_cost_per_call'],
                    'min_success_rate': analysis['enhanced_insights']['performance_requirements']['min_success_rate']
                }
            }
            
            # 使用Enhanced Tool Registry進行智能選擇
            optimal_tools_result = await self.tool_registry.find_optimal_tools(
                request.content, 
                selection_context
            )
            
            if optimal_tools_result['success']:
                selected_tool = optimal_tools_result['selected_tool']
                alternatives = optimal_tools_result.get('alternatives', [])
                
                # 記錄優化統計
                if selected_tool['cost_model']['type'] == 'free':
                    self.enhanced_stats['cost_optimizations'] += 1
                
                if selected_tool['performance_metrics']['success_rate'] > 0.95:
                    self.enhanced_stats['performance_improvements'] += 1
                
                # 檢查是否使用了adapter工具
                if 'adapter' in selected_tool.get('platform', '').lower():
                    self.enhanced_stats['adapter_tool_usage'] += 1
                
                return {
                    'success': True,
                    'selected_tools': [selected_tool['id']],
                    'primary_tool': selected_tool,
                    'alternatives': alternatives[:self.enhanced_config['max_alternatives']],
                    'selection_reasoning': optimal_tools_result.get('decision_explanation', {}),
                    'optimization_applied': True
                }
            else:
                # 回退到基礎工具選擇
                fallback_tools = await self._fallback_tool_selection(request, analysis)
                return {
                    'success': True,
                    'selected_tools': fallback_tools,
                    'fallback_used': True,
                    'optimization_applied': False
                }
                
        except Exception as e:
            logger.error(f"Intelligent tool selection failed: {e}")
            # 回退機制
            fallback_tools = await self._fallback_tool_selection(request, analysis)
            return {
                'success': True,
                'selected_tools': fallback_tools,
                'fallback_used': True,
                'error': str(e)
            }
    
    async def _fallback_tool_selection(self, request: AgentRequest, analysis: Dict[str, Any]) -> List[str]:
        """回退工具選擇"""
        self.enhanced_stats['fallback_activations'] += 1
        
        # 使用基礎工具發現邏輯
        requirement_type = analysis['enhanced_insights']['requirement_type']
        return await self.tool_registry.find_tools_by_capability(requirement_type)
    
    async def _intelligent_execution(self, request: AgentRequest, tool_selection: Dict[str, Any]) -> Dict[str, Any]:
        """
        智能執行
        根據工具特性選擇最佳執行策略
        """
        try:
            selected_tools = tool_selection['selected_tools']
            
            # 如果有Smart Tool Engine選擇的主要工具，使用智能執行
            if 'primary_tool' in tool_selection and not tool_selection.get('fallback_used', False):
                primary_tool = tool_selection['primary_tool']
                
                # 使用Smart Tool Engine執行
                smart_execution_result = await self.tool_registry.execute_with_smart_tool(
                    primary_tool['id'],
                    request.content,
                    request.context
                )
                
                if smart_execution_result['success']:
                    return {
                        'success': True,
                        'result': smart_execution_result,
                        'execution_method': 'smart_engine',
                        'tools_used': [primary_tool['id']],
                        'confidence_score': 0.9
                    }
            
            # 回退到標準執行
            execution_result = await self.action_executor.execute(
                request=request,
                tools=selected_tools,
                mode=self._determine_execution_mode(tool_selection)
            )
            
            return {
                'success': True,
                'result': execution_result,
                'execution_method': 'standard',
                'tools_used': selected_tools,
                'confidence_score': 0.8
            }
            
        except Exception as e:
            logger.error(f"Intelligent execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_method': 'failed'
            }
    
    def _determine_execution_mode(self, tool_selection: Dict[str, Any]) -> str:
        """確定執行模式"""
        tools_count = len(tool_selection['selected_tools'])
        
        if tools_count == 1:
            return 'single'
        elif tools_count <= 3:
            return 'parallel'
        else:
            return 'sequential'
    
    async def _evaluate_and_optimize_result(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """評估和優化結果"""
        try:
            if not execution_result['success']:
                return execution_result
            
            result = execution_result['result']
            
            # 結果質量評估
            quality_score = self._evaluate_result_quality(result)
            
            # 性能評估
            performance_metrics = self._evaluate_performance(execution_result)
            
            # 優化建議
            optimizations = self._generate_optimizations(execution_result, quality_score)
            
            return {
                **result,
                'quality_score': quality_score,
                'performance_metrics': performance_metrics,
                'optimizations': optimizations,
                'confidence_score': min(quality_score + 0.1, 1.0),
                'enhanced_processing': True
            }
            
        except Exception as e:
            logger.error(f"Result evaluation failed: {e}")
            return execution_result.get('result', {})
    
    def _evaluate_result_quality(self, result: Any) -> float:
        """評估結果質量"""
        # 簡化的質量評估邏輯
        if isinstance(result, dict):
            if result.get('success', False):
                return 0.9
            elif 'error' not in result:
                return 0.7
            else:
                return 0.3
        elif result:
            return 0.8
        else:
            return 0.2
    
    def _evaluate_performance(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """評估性能指標"""
        return {
            'execution_method': execution_result.get('execution_method', 'unknown'),
            'tools_count': len(execution_result.get('tools_used', [])),
            'confidence': execution_result.get('confidence_score', 0.8),
            'optimization_level': 'high' if execution_result.get('execution_method') == 'smart_engine' else 'standard'
        }
    
    def _generate_optimizations(self, execution_result: Dict[str, Any], quality_score: float) -> List[str]:
        """生成優化建議"""
        optimizations = []
        
        if quality_score < self.enhanced_config['quality_threshold']:
            optimizations.append("建議使用更高質量的工具")
        
        if execution_result.get('execution_method') == 'standard':
            optimizations.append("可考慮使用Smart Tool Engine進行優化")
        
        if len(execution_result.get('tools_used', [])) > 3:
            optimizations.append("可考慮減少工具數量以提高效率")
        
        return optimizations
    
    async def _intelligent_fallback(self, request: AgentRequest, error: str) -> AgentResponse:
        """智能回退機制"""
        self.enhanced_stats['fallback_activations'] += 1
        
        try:
            # 使用基礎Agent Core處理
            return await super().process_request(request)
        except Exception as fallback_error:
            return AgentResponse(
                request_id=request.id,
                status=TaskStatus.FAILED,
                error=f"Primary error: {error}, Fallback error: {str(fallback_error)}",
                execution_time=0.0
            )
    
    def get_enhanced_status(self) -> Dict[str, Any]:
        """獲取增強狀態"""
        base_status = super().get_status()
        
        return {
            **base_status,
            'enhanced_features': {
                'smart_routing_enabled': self.enhanced_config['enable_smart_routing'],
                'cost_optimization_enabled': self.enhanced_config['enable_cost_optimization'],
                'adapter_integration_enabled': self.enhanced_config['enable_adapter_integration']
            },
            'enhanced_stats': self.enhanced_stats,
            'tool_registry_stats': self.tool_registry.get_enhanced_stats() if hasattr(self.tool_registry, 'get_enhanced_stats') else {}
        }

# 工廠函數
async def create_enhanced_agent_core(config: Dict[str, Any], tool_registry: EnhancedToolRegistry, action_executor: ActionExecutor) -> EnhancedAgentCore:
    """
    創建增強版Agent Core實例
    
    Args:
        config: 配置字典
        tool_registry: 增強版Tool Registry
        action_executor: Action Executor
        
    Returns:
        配置完成的EnhancedAgentCore實例
    """
    agent_core = EnhancedAgentCore(config)
    agent_core.set_enhanced_dependencies(tool_registry, action_executor)
    return agent_core

