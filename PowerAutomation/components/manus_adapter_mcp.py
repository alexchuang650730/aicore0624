#!/usr/bin/env python3
"""
Manus_Adapter_MCP - Manus 系統適配器
利用 AICore 的領域專家、智慧路由、工具發現等核心能力
為 Manus 系統提供智能化的需求處理和任務分析服務
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

# 導入 AICore 核心組件
from components.dynamic_expert_registry import (
    DynamicExpertRegistry, ExpertRegistrationRequest, ExpertProfile, 
    ExpertType, ExpertStatus, ExpertCapability
)
from components.smart_routing_engine import (
    SmartRoutingEngine, RoutingRequest, RoutingDecision, 
    RequestPriority, RoutingStrategy
)
from tools.tool_registry import (
    ToolRegistry, ToolInfo, ToolCapability, ToolType, ToolStatus
)
from components.expert_recommendation_aggregator import (
    ExpertRecommendationAggregator, AggregationStrategy, AggregatedRecommendation
)

logger = logging.getLogger(__name__)

class ManusRequestType(Enum):
    """Manus 請求類型"""
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    TASK_ANALYSIS = "task_analysis"
    UI_DESIGN_REVIEW = "ui_design_review"
    CROSS_TASK_ANALYSIS = "cross_task_analysis"
    FILE_ANALYSIS = "file_analysis"
    CONVERSATION_ANALYSIS = "conversation_analysis"
    EXPERT_CONSULTATION = "expert_consultation"

class ManusAnalysisScope(Enum):
    """Manus 分析範圍"""
    SINGLE_TASK = "single_task"
    MULTI_TASK = "multi_task"
    CROSS_PROJECT = "cross_project"
    FULL_SYSTEM = "full_system"

@dataclass
class ManusRequest:
    """Manus 請求數據結構"""
    request_id: str
    request_type: ManusRequestType
    content: str
    target_entity: str  # REQ_001, TASK_001 等
    analysis_scope: ManusAnalysisScope
    context: Dict[str, Any]
    priority: RequestPriority = RequestPriority.NORMAL
    expected_outputs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ManusExpertRequest:
    """Manus 專家請求"""
    domain: str
    scenario_type: str
    skill_requirements: List[str]
    knowledge_sources: List[Dict]
    manus_context: Dict[str, Any]
    target_entity: str
    analysis_depth: str = "comprehensive"

@dataclass
class ManusAnalysisResult:
    """Manus 分析結果"""
    request_id: str
    analysis_type: str
    target_entity: str
    expert_insights: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    file_references: List[Dict[str, Any]]
    cross_task_relations: Dict[str, Any]
    confidence_score: float
    processing_time: float
    metadata: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

class ManusAdapterMCP:
    """
    Manus 適配器 MCP
    
    核心功能:
    1. 利用 AICore 動態專家系統進行智能分析
    2. 通過智慧路由選擇最佳處理工具
    3. 使用工具發現機制自動匹配合適的分析工具
    4. 提供 Manus 系統專用的分析和建議服務
    """
    
    def __init__(self, aicore_instance=None):
        self.aicore = aicore_instance
        self.expert_registry: Optional[DynamicExpertRegistry] = None
        self.routing_engine: Optional[SmartRoutingEngine] = None
        self.tool_registry: Optional[ToolRegistry] = None
        self.recommendation_aggregator: Optional[ExpertRecommendationAggregator] = None
        
        # Manus 專用配置
        self.manus_experts = {}
        self.manus_tools = {}
        self.analysis_cache = {}
        
        logger.info("🔧 Manus_Adapter_MCP 初始化")
    
    async def initialize(self):
        """初始化 Manus 適配器"""
        logger.info("🚀 初始化 Manus_Adapter_MCP")
        
        try:
            # 1. 初始化 AICore 組件
            if self.aicore:
                self.expert_registry = self.aicore.dynamic_expert_registry
                self.routing_engine = getattr(self.aicore, 'routing_engine', None)
                self.tool_registry = self.aicore.tool_registry
                self.recommendation_aggregator = self.aicore.expert_recommendation_aggregator
            
            # 2. 註冊 Manus 專用專家
            await self._register_manus_experts()
            
            # 3. 註冊 Manus 專用工具
            await self._register_manus_tools()
            
            # 4. 配置智慧路由規則
            await self._configure_manus_routing()
            
            logger.info("✅ Manus_Adapter_MCP 初始化完成")
            
        except Exception as e:
            logger.error(f"❌ Manus_Adapter_MCP 初始化失敗: {e}")
            raise
    
    async def _register_manus_experts(self):
        """註冊 Manus 專用專家"""
        logger.info("👥 註冊 Manus 專用專家")
        
        manus_expert_configs = [
            {
                "domain": "manus_requirement_analysis",
                "scenario_type": "requirement_decomposition",
                "skill_requirements": [
                    "需求分析", "需求分解", "需求優先級評估",
                    "跨任務關聯分析", "需求可行性評估"
                ],
                "knowledge_sources": [
                    {"type": "manus_database", "path": "/manus/requirements"},
                    {"type": "task_history", "path": "/manus/tasks"},
                    {"type": "conversation_logs", "path": "/manus/conversations"}
                ]
            },
            {
                "domain": "manus_ui_design_analysis",
                "scenario_type": "ui_design_review",
                "skill_requirements": [
                    "UI/UX設計", "界面可用性分析", "設計一致性檢查",
                    "用戶體驗評估", "設計規範遵循"
                ],
                "knowledge_sources": [
                    {"type": "design_guidelines", "path": "/manus/design"},
                    {"type": "ui_components", "path": "/manus/components"},
                    {"type": "user_feedback", "path": "/manus/feedback"}
                ]
            },
            {
                "domain": "manus_task_correlation",
                "scenario_type": "cross_task_analysis",
                "skill_requirements": [
                    "任務關聯分析", "依賴關係識別", "影響評估",
                    "協調需求分析", "資源衝突檢測"
                ],
                "knowledge_sources": [
                    {"type": "task_dependencies", "path": "/manus/dependencies"},
                    {"type": "resource_allocation", "path": "/manus/resources"},
                    {"type": "timeline_analysis", "path": "/manus/timelines"}
                ]
            },
            {
                "domain": "manus_file_intelligence",
                "scenario_type": "file_content_analysis",
                "skill_requirements": [
                    "檔案內容分析", "文檔結構解析", "關聯性評估",
                    "版本變更分析", "內容品質評估"
                ],
                "knowledge_sources": [
                    {"type": "file_metadata", "path": "/manus/files"},
                    {"type": "content_patterns", "path": "/manus/patterns"},
                    {"type": "version_history", "path": "/manus/versions"}
                ]
            }
        ]
        
        for config in manus_expert_configs:
            try:
                if self.expert_registry:
                    request = ExpertRegistrationRequest(
                        domain=config["domain"],
                        scenario_type=config["scenario_type"],
                        skill_requirements=config["skill_requirements"],
                        knowledge_sources=config["knowledge_sources"],
                        priority=3,
                        context={"adapter": "manus", "version": "1.0"},
                        requester="manus_adapter_mcp"
                    )
                    
                    expert = await self.expert_registry.register_dynamic_expert(request)
                    self.manus_experts[config["domain"]] = expert
                    logger.info(f"✅ 註冊專家: {config['domain']}")
                
            except Exception as e:
                logger.error(f"❌ 註冊專家失敗 {config['domain']}: {e}")
    
    async def _register_manus_tools(self):
        """註冊 Manus 專用工具"""
        logger.info("🔧 註冊 Manus 專用工具")
        
        manus_tools = [
            {
                "id": "manus_smartinvention_connector",
                "name": "Manus Smartinvention 連接器",
                "type": ToolType.MCP_SERVICE,
                "description": "連接 Smartinvention MCP 獲取任務數據",
                "capabilities": [
                    ToolCapability(
                        name="task_data_retrieval",
                        description="獲取任務數據和元信息",
                        input_types=["task_id", "query_params"],
                        output_types=["task_info", "metadata"]
                    ),
                    ToolCapability(
                        name="conversation_analysis",
                        description="分析任務對話歷史",
                        input_types=["task_id", "conversation_filters"],
                        output_types=["conversation_summary", "insights"]
                    )
                ],
                "endpoint": "smartinvention_mcp_v2",
                "tags": ["manus", "data_source", "smartinvention"]
            },
            {
                "id": "manus_requirement_processor",
                "name": "Manus 需求處理器",
                "type": ToolType.PYTHON_MODULE,
                "description": "處理和分析 Manus 需求",
                "capabilities": [
                    ToolCapability(
                        name="requirement_parsing",
                        description="解析自然語言需求",
                        input_types=["requirement_text", "context"],
                        output_types=["structured_requirements", "analysis"]
                    ),
                    ToolCapability(
                        name="cross_task_analysis",
                        description="跨任務關聯分析",
                        input_types=["task_list", "requirement_id"],
                        output_types=["correlation_matrix", "dependencies"]
                    )
                ],
                "module_path": "components.aicore_requirement_processor_mcp",
                "tags": ["manus", "requirement", "analysis"]
            },
            {
                "id": "manus_expert_coordinator",
                "name": "Manus 專家協調器",
                "type": ToolType.PYTHON_MODULE,
                "description": "協調多個專家進行綜合分析",
                "capabilities": [
                    ToolCapability(
                        name="expert_orchestration",
                        description="協調專家分析流程",
                        input_types=["analysis_request", "expert_list"],
                        output_types=["coordinated_analysis", "expert_insights"]
                    )
                ],
                "module_path": "components.expert_recommendation_aggregator",
                "tags": ["manus", "expert", "coordination"]
            }
        ]
        
        for tool_config in manus_tools:
            try:
                if self.tool_registry:
                    tool_info = ToolInfo(**tool_config)
                    await self.tool_registry.register_tool(tool_info)
                    self.manus_tools[tool_config["id"]] = tool_info
                    logger.info(f"✅ 註冊工具: {tool_config['name']}")
                
            except Exception as e:
                logger.error(f"❌ 註冊工具失敗 {tool_config['id']}: {e}")
    
    async def _configure_manus_routing(self):
        """配置 Manus 專用路由規則"""
        logger.info("🛣️ 配置 Manus 智慧路由規則")
        
        if self.routing_engine:
            # 配置基於需求類型的路由規則
            routing_rules = {
                ManusRequestType.REQUIREMENT_ANALYSIS: {
                    "preferred_experts": ["manus_requirement_analysis"],
                    "preferred_tools": ["manus_requirement_processor"],
                    "strategy": RoutingStrategy.INTELLIGENT
                },
                ManusRequestType.UI_DESIGN_REVIEW: {
                    "preferred_experts": ["manus_ui_design_analysis"],
                    "preferred_tools": ["manus_smartinvention_connector"],
                    "strategy": RoutingStrategy.LEAST_RESPONSE_TIME
                },
                ManusRequestType.CROSS_TASK_ANALYSIS: {
                    "preferred_experts": ["manus_task_correlation"],
                    "preferred_tools": ["manus_requirement_processor", "manus_expert_coordinator"],
                    "strategy": RoutingStrategy.RESOURCE_BASED
                }
            }
            
            # 這裡可以配置路由引擎的規則
            # 實際實現取決於 SmartRoutingEngine 的 API
            logger.info("✅ Manus 路由規則配置完成")
    
    async def process_manus_request(self, request: ManusRequest) -> ManusAnalysisResult:
        """處理 Manus 請求"""
        logger.info(f"🎯 處理 Manus 請求: {request.request_type.value}")
        
        start_time = time.time()
        
        try:
            # 1. 智慧路由 - 選擇最佳專家和工具
            routing_decision = await self._route_manus_request(request)
            
            # 2. 動態專家分析
            expert_insights = await self._get_expert_analysis(request, routing_decision)
            
            # 3. 工具執行和數據獲取
            tool_results = await self._execute_manus_tools(request, routing_decision)
            
            # 4. 結果聚合和建議生成
            aggregated_result = await self._aggregate_manus_results(
                request, expert_insights, tool_results
            )
            
            processing_time = time.time() - start_time
            
            result = ManusAnalysisResult(
                request_id=request.request_id,
                analysis_type=request.request_type.value,
                target_entity=request.target_entity,
                expert_insights=expert_insights,
                recommendations=aggregated_result.get("recommendations", []),
                file_references=aggregated_result.get("file_references", []),
                cross_task_relations=aggregated_result.get("cross_task_relations", {}),
                confidence_score=aggregated_result.get("confidence_score", 0.0),
                processing_time=processing_time,
                metadata=aggregated_result.get("metadata", {})
            )
            
            logger.info(f"✅ Manus 請求處理完成: {processing_time:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"❌ Manus 請求處理失敗: {e}")
            raise
    
    async def _route_manus_request(self, request: ManusRequest) -> Dict[str, Any]:
        """為 Manus 請求進行智慧路由"""
        logger.info(f"🛣️ 為請求進行智慧路由: {request.target_entity}")
        
        if self.routing_engine:
            routing_request = RoutingRequest(
                request_id=request.request_id,
                capability_required=request.request_type.value,
                priority=request.priority,
                metadata={"manus_context": request.context}
            )
            
            # 這裡調用智慧路由引擎
            # 實際實現取決於 SmartRoutingEngine 的 API
            routing_decision = {
                "selected_experts": self._select_experts_for_request(request),
                "selected_tools": self._select_tools_for_request(request),
                "routing_strategy": "intelligent"
            }
        else:
            # 回退到基本路由
            routing_decision = {
                "selected_experts": self._select_experts_for_request(request),
                "selected_tools": self._select_tools_for_request(request),
                "routing_strategy": "fallback"
            }
        
        return routing_decision
    
    def _select_experts_for_request(self, request: ManusRequest) -> List[str]:
        """為請求選擇合適的專家"""
        expert_mapping = {
            ManusRequestType.REQUIREMENT_ANALYSIS: ["manus_requirement_analysis"],
            ManusRequestType.UI_DESIGN_REVIEW: ["manus_ui_design_analysis"],
            ManusRequestType.CROSS_TASK_ANALYSIS: ["manus_task_correlation"],
            ManusRequestType.FILE_ANALYSIS: ["manus_file_intelligence"]
        }
        
        return expert_mapping.get(request.request_type, ["manus_requirement_analysis"])
    
    def _select_tools_for_request(self, request: ManusRequest) -> List[str]:
        """為請求選擇合適的工具"""
        tool_mapping = {
            ManusRequestType.REQUIREMENT_ANALYSIS: ["manus_requirement_processor"],
            ManusRequestType.UI_DESIGN_REVIEW: ["manus_smartinvention_connector"],
            ManusRequestType.CROSS_TASK_ANALYSIS: ["manus_requirement_processor", "manus_expert_coordinator"],
            ManusRequestType.FILE_ANALYSIS: ["manus_smartinvention_connector"]
        }
        
        return tool_mapping.get(request.request_type, ["manus_requirement_processor"])
    
    async def _get_expert_analysis(self, request: ManusRequest, routing_decision: Dict) -> Dict[str, Any]:
        """獲取專家分析"""
        logger.info("🧠 獲取專家分析")
        
        expert_insights = {}
        selected_experts = routing_decision.get("selected_experts", [])
        
        for expert_domain in selected_experts:
            if expert_domain in self.manus_experts:
                expert = self.manus_experts[expert_domain]
                
                # 模擬專家分析過程
                # 實際實現會調用專家的分析方法
                insight = {
                    "expert_id": expert.id,
                    "expert_name": expert.name,
                    "analysis": f"針對 {request.target_entity} 的 {request.request_type.value} 分析",
                    "recommendations": [
                        f"建議1: 基於 {expert_domain} 的專業分析",
                        f"建議2: 考慮 {request.analysis_scope.value} 的影響範圍"
                    ],
                    "confidence": 0.85,
                    "processing_time": 0.5
                }
                
                expert_insights[expert_domain] = insight
        
        return expert_insights
    
    async def _execute_manus_tools(self, request: ManusRequest, routing_decision: Dict) -> Dict[str, Any]:
        """執行 Manus 工具"""
        logger.info("🔧 執行 Manus 工具")
        
        tool_results = {}
        selected_tools = routing_decision.get("selected_tools", [])
        
        for tool_id in selected_tools:
            if tool_id in self.manus_tools:
                tool = self.manus_tools[tool_id]
                
                # 模擬工具執行
                # 實際實現會調用具體的工具
                result = {
                    "tool_id": tool_id,
                    "tool_name": tool.name,
                    "execution_result": f"執行 {tool.name} 處理 {request.target_entity}",
                    "data": {
                        "processed_entity": request.target_entity,
                        "analysis_scope": request.analysis_scope.value,
                        "findings": ["發現1", "發現2", "發現3"]
                    },
                    "execution_time": 0.3,
                    "status": "success"
                }
                
                tool_results[tool_id] = result
        
        return tool_results
    
    async def _aggregate_manus_results(self, request: ManusRequest, expert_insights: Dict, tool_results: Dict) -> Dict[str, Any]:
        """聚合 Manus 分析結果"""
        logger.info("📊 聚合分析結果")
        
        if self.recommendation_aggregator:
            # 使用 AICore 的建議聚合器
            # 實際實現會調用聚合器的方法
            pass
        
        # 基本聚合邏輯
        recommendations = []
        file_references = []
        cross_task_relations = {}
        
        # 從專家洞察中提取建議
        for expert_domain, insight in expert_insights.items():
            recommendations.extend(insight.get("recommendations", []))
        
        # 從工具結果中提取數據
        for tool_id, result in tool_results.items():
            data = result.get("data", {})
            if "findings" in data:
                recommendations.extend(data["findings"])
        
        # 計算信心度
        confidence_scores = [insight.get("confidence", 0.0) for insight in expert_insights.values()]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return {
            "recommendations": recommendations,
            "file_references": file_references,
            "cross_task_relations": cross_task_relations,
            "confidence_score": avg_confidence,
            "metadata": {
                "expert_count": len(expert_insights),
                "tool_count": len(tool_results),
                "analysis_scope": request.analysis_scope.value
            }
        }
    
    async def analyze_requirement(self, requirement_text: str, target_entity: str, context: Dict = None) -> ManusAnalysisResult:
        """分析需求 - 便捷方法"""
        request = ManusRequest(
            request_id=f"req_{int(time.time())}",
            request_type=ManusRequestType.REQUIREMENT_ANALYSIS,
            content=requirement_text,
            target_entity=target_entity,
            analysis_scope=ManusAnalysisScope.MULTI_TASK,
            context=context or {},
            expected_outputs=["requirements_list", "manus_actions", "file_list"]
        )
        
        return await self.process_manus_request(request)
    
    async def get_manus_status(self) -> Dict[str, Any]:
        """獲取 Manus 適配器狀態"""
        return {
            "adapter_status": "active",
            "registered_experts": len(self.manus_experts),
            "registered_tools": len(self.manus_tools),
            "aicore_connected": self.aicore is not None,
            "expert_registry_available": self.expert_registry is not None,
            "routing_engine_available": self.routing_engine is not None,
            "tool_registry_available": self.tool_registry is not None,
            "cache_size": len(self.analysis_cache),
            "version": "1.0.0"
        }

# 工廠函數
def create_manus_adapter_mcp(aicore_instance=None) -> ManusAdapterMCP:
    """創建 Manus 適配器 MCP 實例"""
    return ManusAdapterMCP(aicore_instance)

# 測試和演示
async def main():
    """主函數 - 演示 Manus_Adapter_MCP 功能"""
    logger.info("🚀 啟動 Manus_Adapter_MCP 演示")
    
    try:
        # 創建適配器
        adapter = create_manus_adapter_mcp()
        
        # 初始化
        await adapter.initialize()
        
        # 測試需求分析
        result = await adapter.analyze_requirement(
            requirement_text="針對 REQ_001: 用戶界面設計需求 列出明確需求及manus action，包含相關檔案列表，注意跨任務情況",
            target_entity="REQ_001",
            context={"project": "manus_system", "priority": "high"}
        )
        
        print("\n" + "="*60)
        print("🎯 Manus_Adapter_MCP 分析結果")
        print("="*60)
        print(f"目標實體: {result.target_entity}")
        print(f"分析類型: {result.analysis_type}")
        print(f"信心度: {result.confidence_score:.2f}")
        print(f"處理時間: {result.processing_time:.2f}秒")
        print(f"專家洞察數量: {len(result.expert_insights)}")
        print(f"建議數量: {len(result.recommendations)}")
        
        # 獲取狀態
        status = await adapter.get_manus_status()
        print(f"\n📊 適配器狀態:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        print("\n✅ Manus_Adapter_MCP 演示完成")
        
    except Exception as e:
        logger.error(f"❌ 演示失敗: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

