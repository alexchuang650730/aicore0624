"""
增強版Tool Registry - 完整版 (Updated for PowerAutomation 3.0)
Enhanced Tool Registry with Complete Smart Tool Engine Integration

整合Smart Tool Engine、雲端平台、智能路由引擎、成本優化
支持ACI.dev、MCP.so、Zapier三大雲端平台
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import json
import os
from datetime import datetime

# 導入原有的Tool Registry
from .tool_registry import ToolRegistry, ToolInfo, ToolType, ToolCapability

# 導入Smart Tool Engine組件
from .smart_tool_engine_mcp import (
    SmartToolEngineMCP,
    UnifiedToolRegistry,
    IntelligentRoutingEngine,
    CloudPlatformIntegration,
    CostTracker,
    PlatformType,
    CostType
)

logger = logging.getLogger(__name__)

class EnhancedToolType(Enum):
    """增強的工具類型"""
    # 原有類型
    MCP_SERVICE = "mcp_service"
    HTTP_API = "http_api"
    PYTHON_MODULE = "python_module"
    SHELL_COMMAND = "shell_command"
    
    # Smart Engine新增類型
    ACI_DEV_TOOL = "aci_dev_tool"
    MCP_SO_TOOL = "mcp_so_tool"
    ZAPIER_TOOL = "zapier_tool"
    UNIFIED_SMART_TOOL = "unified_smart_tool"
    
    # PowerAutomation 3.0 MCP組件類型
    MCP_COMPONENT = "mcp_component"
    GENERAL_PROCESSOR_MCP = "general_processor_mcp"
    TEST_FLOW_MCP = "test_flow_mcp"
    ADAPTER_MCP = "adapter_mcp"
    RECORDER_WORKFLOW_MCP = "recorder_workflow_mcp"
    DYNAMIC_EXPERT_MCP = "dynamic_expert_mcp"

class SmartToolInfo(ToolInfo):
    """增強的工具信息"""
    
    def __init__(self, id: str, name: str, type: EnhancedToolType, description: str, 
                 version: str = "1.0.0", capabilities: List[ToolCapability] = None,
                 platform: str = None, performance_metrics: Dict = None, 
                 cost_model: Dict = None, quality_scores: Dict = None,
                 tags: List[str] = None, supported_formats: List[str] = None):
        super().__init__(id, name, type, description, version, capabilities)
        
        # Smart Engine擴展屬性
        self.platform = platform or "local"
        self.tags = tags or []
        self.supported_formats = supported_formats or []
        
        self.performance_metrics = performance_metrics or {
            "avg_response_time": 1000,
            "success_rate": 0.95,
            "throughput": 100,
            "reliability_score": 0.9,
            "uptime": 0.99
        }
        
        self.cost_model = cost_model or {
            "type": "free",
            "cost_per_call": 0.0,
            "cost_per_mb": 0.0,
            "monthly_limit": -1,
            "daily_limit": -1,
            "currency": "USD",
            "billing_model": "per_call"
        }
        
        self.quality_scores = quality_scores or {
            "user_rating": 4.0,
            "documentation_quality": 0.8,
            "community_support": 0.7,
            "update_frequency": 0.8,
            "security_score": 0.9
        }
        
        # 使用統計
        self.usage_stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_cost": 0.0,
            "last_used": None,
            "avg_user_satisfaction": 0.0
        }

class EnhancedToolRegistry(ToolRegistry):
    """
    增強版Tool Registry - 完整版
    整合Smart Tool Engine的完整智能工具發現、選擇和管理能力
    支持雲端平台整合、成本優化、智能路由
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # 初始化Smart Tool Engine組件
        self.smart_engine = SmartToolEngineMCP()
        self.unified_registry = self.smart_engine.registry
        self.routing_engine = self.smart_engine.routing_engine
        self.cloud_integration = self.smart_engine.cloud_integration
        self.cost_tracker = self.smart_engine.registry.cost_tracker
        
        # 增強配置
        self.smart_config = config.get('smart_engine', {
            'enable_cloud_tools': True,
            'enable_intelligent_routing': True,
            'enable_cost_optimization': True,
            'enable_performance_monitoring': True,
            'max_cloud_tools': 100,
            'default_timeout': 30,
            'cost_budget': {
                'max_cost_per_call': 0.01,
                'monthly_budget': 100.0,
                'currency': 'USD'
            },
            'performance_requirements': {
                'min_success_rate': 0.90,
                'max_response_time': 5000,
                'min_throughput': 10
            },
            'cloud_platforms': {
                'aci_dev': {
                    'enabled': bool(os.getenv('ACI_DEV_API_KEY')),
                    'api_key': os.getenv('ACI_DEV_API_KEY'),
                    'priority': 1
                },
                'mcp_so': {
                    'enabled': bool(os.getenv('MCP_SO_API_KEY')),
                    'api_key': os.getenv('MCP_SO_API_KEY'),
                    'priority': 2
                },
                'zapier': {
                    'enabled': bool(os.getenv('ZAPIER_API_KEY')),
                    'api_key': os.getenv('ZAPIER_API_KEY'),
                    'priority': 3
                }
            }
        })
        
        # 統計信息
        self.enhanced_stats = {
            'smart_tools_discovered': 0,
            'intelligent_selections': 0,
            'cost_optimizations': 0,
            'performance_improvements': 0,
            'cloud_tools_used': 0,
            'total_cost_saved': 0.0,
            'avg_selection_time': 0.0,
            'platform_usage': {
                'aci_dev': 0,
                'mcp_so': 0,
                'zapier': 0,
                'local': 0
            }
        }
        
        # 緩存
        self.tool_cache = {}
        self.search_cache = {}
        self.cache_ttl = 300  # 5分鐘緩存
        
        logger.info("Enhanced Tool Registry initialized with complete Smart Tool Engine")
    
    async def initialize(self):
        """初始化增強版Tool Registry"""
        try:
            # 調用父類初始化
            await super().initialize()
            
            # 初始化Smart Tool Engine
            await self._initialize_smart_engine()
            
            # 同步工具到統一註冊表
            await self._sync_tools_to_unified_registry()
            
            # 發現雲端工具
            if self.smart_config['enable_cloud_tools']:
                await self._discover_and_register_cloud_tools()
            
            # 設置定期同步
            await self._setup_periodic_sync()
            
            logger.info("Enhanced Tool Registry initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Tool Registry: {e}")
            raise
    
    async def _initialize_smart_engine(self):
        """初始化Smart Tool Engine"""
        try:
            await self.smart_engine.initialize()
            
            # 獲取Smart Engine中的工具數量
            smart_tools = await self._get_all_smart_tools()
            self.enhanced_stats['smart_tools_discovered'] = len(smart_tools)
            
            logger.info(f"Smart Tool Engine initialized with {len(smart_tools)} tools")
            
        except Exception as e:
            logger.error(f"Failed to initialize Smart Tool Engine: {e}")
            raise
    
    async def _sync_tools_to_unified_registry(self):
        """同步本地工具到統一註冊表"""
        try:
            synced_count = 0
            for tool_id, tool_info in self.tools.items():
                # 將本地工具轉換為Smart Tool格式
                smart_tool_info = self._convert_to_smart_tool(tool_info)
                
                # 註冊到統一註冊表
                unified_tool_id = self.unified_registry.register_tool(smart_tool_info)
                
                # 更新緩存
                self.tool_cache[tool_id] = unified_tool_id
                synced_count += 1
                
                logger.debug(f"Synced tool {tool_id} to unified registry as {unified_tool_id}")
            
            logger.info(f"Synced {synced_count} local tools to unified registry")
                
        except Exception as e:
            logger.error(f"Failed to sync tools to unified registry: {e}")
    
    async def _discover_and_register_cloud_tools(self):
        """發現並註冊雲端工具"""
        try:
            total_discovered = 0
            
            for platform, config in self.smart_config['cloud_platforms'].items():
                if not config['enabled']:
                    logger.info(f"Platform {platform} disabled, skipping discovery")
                    continue
                
                try:
                    # 發現平台工具
                    tools = await self.cloud_integration.discover_tools_from_platform(platform)
                    
                    # 註冊到統一註冊表
                    for tool in tools:
                        self.unified_registry.register_tool(tool)
                        total_discovered += 1
                    
                    logger.info(f"Discovered and registered {len(tools)} tools from {platform}")
                    
                except Exception as e:
                    logger.warning(f"Failed to discover tools from {platform}: {e}")
            
            self.enhanced_stats['smart_tools_discovered'] += total_discovered
            logger.info(f"Total cloud tools discovered: {total_discovered}")
            
        except Exception as e:
            logger.error(f"Failed to discover cloud tools: {e}")
    
    async def _setup_periodic_sync(self):
        """設置定期同步"""
        # 這裡可以設置定期任務來同步雲端工具
        # 暫時跳過，可以在後續版本中實現
        pass
    
    def _convert_to_smart_tool(self, tool_info: ToolInfo) -> Dict:
        """將本地工具信息轉換為Smart Tool格式"""
        return {
            "name": tool_info.name,
            "description": tool_info.description,
            "category": "local_tool",
            "platform": "local",
            "platform_tool_id": tool_info.id,
            "mcp_endpoint": f"local://{tool_info.id}",
            "capabilities": [cap.name for cap in tool_info.capabilities],
            "input_schema": {"type": "object", "properties": {}},
            "output_schema": {"type": "object", "properties": {}},
            "version": tool_info.version,
            "tags": getattr(tool_info, 'tags', []),
            "supported_formats": getattr(tool_info, 'supported_formats', []),
            "avg_response_time": 500,
            "success_rate": 0.95,
            "cost_type": "free",
            "cost_per_call": 0.0,
            "user_rating": 4.0,
            "reliability_score": 0.9,
            "uptime": 0.99
        }
    
    async def find_optimal_tools(self, requirement: str, context: Dict = None) -> Dict:
        """
        使用智能引擎找到最優工具
        
        Args:
            requirement: 需求描述
            context: 上下文信息
            
        Returns:
            包含最優工具和備選方案的字典
        """
        start_time = time.time()
        
        try:
            context = context or {}
            
            # 檢查緩存
            cache_key = f"{requirement}:{hash(str(context))}"
            if cache_key in self.search_cache:
                cached_result = self.search_cache[cache_key]
                if time.time() - cached_result['timestamp'] < self.cache_ttl:
                    logger.debug(f"Returning cached result for: {requirement}")
                    return cached_result['result']
            
            # 添加預算約束
            if 'budget' not in context:
                context['budget'] = self.smart_config['cost_budget']
            
            # 添加性能要求
            if 'performance_requirements' not in context:
                context['performance_requirements'] = self.smart_config['performance_requirements']
            
            # 使用智能路由引擎選擇最優工具
            routing_result = self.routing_engine.select_optimal_tool(requirement, context)
            
            if routing_result['success']:
                self.enhanced_stats['intelligent_selections'] += 1
                
                # 記錄統計信息
                selected_tool = routing_result['selected_tool']
                self._update_selection_stats(selected_tool, context)
                
                # 緩存結果
                self.search_cache[cache_key] = {
                    'result': routing_result,
                    'timestamp': time.time()
                }
            
            # 更新平均選擇時間
            selection_time = time.time() - start_time
            self._update_avg_selection_time(selection_time)
            
            return routing_result
            
        except Exception as e:
            logger.error(f"Failed to find optimal tools: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback': await self._fallback_tool_selection(requirement)
            }
    
    def _update_selection_stats(self, selected_tool: Dict, context: Dict):
        """更新選擇統計信息"""
        # 成本優化統計
        if selected_tool['cost_model']['type'] == 'free':
            self.enhanced_stats['cost_optimizations'] += 1
        
        # 性能改進統計
        if selected_tool['performance_metrics']['success_rate'] > 0.95:
            self.enhanced_stats['performance_improvements'] += 1
        
        # 平台使用統計
        platform = selected_tool.get('platform', 'local')
        if platform in self.enhanced_stats['platform_usage']:
            self.enhanced_stats['platform_usage'][platform] += 1
        
        # 雲端工具使用統計
        if platform != 'local':
            self.enhanced_stats['cloud_tools_used'] += 1
        
        # 成本節省統計
        budget = context.get('budget', {})
        max_cost = budget.get('max_cost_per_call', 0.01)
        actual_cost = selected_tool['cost_model']['cost_per_call']
        if actual_cost < max_cost:
            cost_saved = max_cost - actual_cost
            self.enhanced_stats['total_cost_saved'] += cost_saved
    
    def _update_avg_selection_time(self, selection_time: float):
        """更新平均選擇時間"""
        current_avg = self.enhanced_stats['avg_selection_time']
        total_selections = self.enhanced_stats['intelligent_selections']
        
        if total_selections > 0:
            new_avg = ((current_avg * (total_selections - 1)) + selection_time) / total_selections
            self.enhanced_stats['avg_selection_time'] = new_avg
    
    async def _fallback_tool_selection(self, requirement: str) -> List[str]:
        """回退的工具選擇邏輯"""
        try:
            # 使用原有的工具發現邏輯作為回退
            return await super().find_tools_by_capability(requirement)
        except Exception as e:
            logger.error(f"Fallback tool selection failed: {e}")
            return []
    
    async def discover_cloud_tools(self, query: str, filters: Dict = None) -> List[Dict]:
        """
        發現雲端工具
        
        Args:
            query: 搜索查詢
            filters: 過濾條件
            
        Returns:
            匹配的雲端工具列表
        """
        try:
            if not self.smart_config['enable_cloud_tools']:
                logger.info("Cloud tools discovery disabled")
                return []
            
            # 使用Smart Engine的工具發現
            result = await self.smart_engine.process({
                "action": "discover_tools",
                "parameters": {
                    "query": query,
                    "filters": filters or {},
                    "limit": self.smart_config['max_cloud_tools']
                }
            })
            
            if result['success']:
                discovered_tools = result['tools']
                
                # 過濾雲端工具
                cloud_tools = [
                    tool for tool in discovered_tools 
                    if tool.get('platform', 'local') != 'local'
                ]
                
                logger.info(f"Discovered {len(cloud_tools)} cloud tools for query: {query}")
                return cloud_tools
            else:
                logger.warning(f"Cloud tool discovery failed: {result.get('error')}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to discover cloud tools: {e}")
            return []
    
    async def _get_all_smart_tools(self) -> List[Dict]:
        """獲取Smart Engine中的所有工具"""
        try:
            result = await self.smart_engine.process({
                "action": "discover_tools",
                "parameters": {
                    "query": "",  # 空查詢返回所有工具
                    "limit": 1000
                }
            })
            
            if result['success']:
                return result['tools']
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to get smart tools: {e}")
            return []
    
    async def register_smart_tool(self, tool_info: Dict) -> str:
        """
        註冊智能工具
        
        Args:
            tool_info: 工具信息字典
            
        Returns:
            工具ID
        """
        try:
            # 使用Smart Engine註冊工具
            result = await self.smart_engine.process({
                "action": "register_tool",
                "parameters": {
                    "tool_info": tool_info
                }
            })
            
            if result['success']:
                tool_id = result['tool_id']
                
                # 更新統計
                self.enhanced_stats['smart_tools_discovered'] += 1
                
                # 清除相關緩存
                self._clear_search_cache()
                
                logger.info(f"Smart tool registered: {tool_id}")
                return tool_id
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except Exception as e:
            logger.error(f"Failed to register smart tool: {e}")
            raise
    
    async def update_tool_performance(self, tool_id: str, execution_result: Dict):
        """
        更新工具性能統計
        
        Args:
            tool_id: 工具ID
            execution_result: 執行結果
        """
        try:
            # 使用Smart Engine更新統計
            await self.smart_engine.process({
                "action": "update_tool_stats",
                "parameters": {
                    "tool_id": tool_id,
                    "execution_result": execution_result
                }
            })
            
            # 更新本地統計
            if execution_result.get('success', False):
                platform = execution_result.get('platform', 'local')
                if platform in self.enhanced_stats['platform_usage']:
                    self.enhanced_stats['platform_usage'][platform] += 1
            
        except Exception as e:
            logger.error(f"Failed to update tool performance: {e}")
    
    def _clear_search_cache(self):
        """清除搜索緩存"""
        self.search_cache.clear()
        logger.debug("Search cache cleared")
    
    async def get_enhanced_stats(self) -> Dict:
        """獲取增強統計信息"""
        try:
            # 獲取Smart Engine統計
            smart_stats_result = await self.smart_engine.process({
                "action": "get_tool_stats",
                "parameters": {}
            })
            
            smart_stats = {}
            if smart_stats_result['success']:
                smart_stats = smart_stats_result.get('overall_stats', {})
            
            # 獲取成本統計
            budget_status = self.cost_tracker.check_budget(
                self.smart_config['cost_budget']['monthly_budget']
            )
            
            # 合併統計信息
            enhanced_stats = {
                **self.enhanced_stats,
                'smart_engine_stats': smart_stats,
                'budget_status': budget_status,
                'cache_stats': {
                    'search_cache_size': len(self.search_cache),
                    'tool_cache_size': len(self.tool_cache)
                },
                'platform_configs': {
                    platform: {'enabled': config['enabled']}
                    for platform, config in self.smart_config['cloud_platforms'].items()
                }
            }
            
            return enhanced_stats
            
        except Exception as e:
            logger.error(f"Failed to get enhanced stats: {e}")
            return self.enhanced_stats
    
    async def health_check_enhanced(self) -> Dict:
        """增強健康檢查"""
        try:
            # 基礎健康檢查
            base_health = await super().health_check()
            
            # Smart Engine健康檢查
            smart_engine_healthy = self.smart_engine.initialized
            
            # 雲端平台健康檢查
            platform_health = {}
            for platform, config in self.smart_config['cloud_platforms'].items():
                if config['enabled']:
                    # 簡單的連通性檢查
                    try:
                        tools = await self.cloud_integration.discover_tools_from_platform(platform, "test")
                        platform_health[platform] = True
                    except:
                        platform_health[platform] = False
                else:
                    platform_health[platform] = None  # 未啟用
            
            # 成本健康檢查
            budget_status = self.cost_tracker.check_budget(
                self.smart_config['cost_budget']['monthly_budget']
            )
            cost_healthy = not budget_status['over_budget']
            
            # 綜合健康狀態
            overall_healthy = (
                base_health['healthy'] and 
                smart_engine_healthy and 
                cost_healthy and
                any(platform_health.values())  # 至少一個平台健康
            )
            
            return {
                'healthy': overall_healthy,
                'base_registry': base_health,
                'smart_engine': smart_engine_healthy,
                'cloud_platforms': platform_health,
                'cost_status': {
                    'healthy': cost_healthy,
                    'budget_usage': budget_status['usage_percentage']
                },
                'enhanced_features': {
                    'intelligent_routing': self.smart_config['enable_intelligent_routing'],
                    'cost_optimization': self.smart_config['enable_cost_optimization'],
                    'cloud_integration': self.smart_config['enable_cloud_tools'],
                    'performance_monitoring': self.smart_config['enable_performance_monitoring']
                }
            }
            
        except Exception as e:
            logger.error(f"Enhanced health check failed: {e}")
            return {
                'healthy': False,
                'error': str(e)
            }
    
    async def optimize_tool_selection(self, requirement: str, context: Dict = None) -> Dict:
        """
        優化工具選擇 - 高級功能
        
        Args:
            requirement: 需求描述
            context: 上下文信息
            
        Returns:
            優化的工具選擇結果
        """
        try:
            # 基礎工具選擇
            base_result = await self.find_optimal_tools(requirement, context)
            
            if not base_result['success']:
                return base_result
            
            # 進一步優化
            selected_tool = base_result['selected_tool']
            alternatives = base_result.get('alternatives', [])
            
            # 成本優化
            if context and context.get('optimize_cost', True):
                cost_optimized = self._optimize_for_cost(selected_tool, alternatives)
                if cost_optimized:
                    selected_tool = cost_optimized
                    self.enhanced_stats['cost_optimizations'] += 1
            
            # 性能優化
            if context and context.get('optimize_performance', True):
                perf_optimized = self._optimize_for_performance(selected_tool, alternatives, context)
                if perf_optimized:
                    selected_tool = perf_optimized
                    self.enhanced_stats['performance_improvements'] += 1
            
            return {
                **base_result,
                'selected_tool': selected_tool,
                'optimization_applied': True,
                'optimization_reason': self._generate_optimization_reason(selected_tool)
            }
            
        except Exception as e:
            logger.error(f"Tool selection optimization failed: {e}")
            return await self.find_optimal_tools(requirement, context)
    
    def _optimize_for_cost(self, current_tool: Dict, alternatives: List[Dict]) -> Optional[Dict]:
        """成本優化"""
        current_cost = current_tool['cost_model']['cost_per_call']
        
        # 尋找更便宜的替代方案
        for alt in alternatives:
            alt_cost = alt['cost_model']['cost_per_call']
            alt_success_rate = alt['performance_metrics']['success_rate']
            
            # 如果替代方案更便宜且性能差異不大，則選擇它
            if (alt_cost < current_cost and 
                alt_success_rate >= current_tool['performance_metrics']['success_rate'] - 0.05):
                return alt
        
        return None
    
    def _optimize_for_performance(self, current_tool: Dict, alternatives: List[Dict], context: Dict) -> Optional[Dict]:
        """性能優化"""
        performance_req = context.get('performance_requirements', {})
        min_success_rate = performance_req.get('min_success_rate', 0.90)
        max_response_time = performance_req.get('max_response_time', 5000)
        
        current_success_rate = current_tool['performance_metrics']['success_rate']
        current_response_time = current_tool['performance_metrics']['avg_response_time']
        
        # 如果當前工具不滿足性能要求，尋找更好的替代方案
        if (current_success_rate < min_success_rate or 
            current_response_time > max_response_time):
            
            for alt in alternatives:
                alt_success_rate = alt['performance_metrics']['success_rate']
                alt_response_time = alt['performance_metrics']['avg_response_time']
                
                if (alt_success_rate >= min_success_rate and 
                    alt_response_time <= max_response_time):
                    return alt
        
        return None
    
    def _generate_optimization_reason(self, tool: Dict) -> str:
        """生成優化理由"""
        reasons = []
        
        cost_type = tool['cost_model']['type']
        if cost_type == 'free':
            reasons.append("選擇免費工具以降低成本")
        
        success_rate = tool['performance_metrics']['success_rate']
        if success_rate > 0.95:
            reasons.append(f"高成功率({success_rate:.1%})")
        
        response_time = tool['performance_metrics']['avg_response_time']
        if response_time < 2000:
            reasons.append("快速響應時間")
        
        platform = tool.get('platform', 'local')
        if platform == 'local':
            reasons.append("本地工具，無網絡依賴")
        
        return "優化原因: " + "、".join(reasons) if reasons else "已選擇最優工具"

# 導出主要類
__all__ = [
    'EnhancedToolRegistry',
    'EnhancedToolType', 
    'SmartToolInfo'
]

