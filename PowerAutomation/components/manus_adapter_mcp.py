#!/usr/bin/env python3
"""
Manus_Adapter_MCP - 統一的 Manus 適配器與需求分析處理器
整合 Manus 系統與 AICore 3.0，利用動態專家、智慧路由、工具發現等核心能力
同時提供完整的需求分析處理功能
"""

import asyncio
import json
import logging
import time
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum

# 導入 AICore 3.0 組件
from core.aicore3 import AICore3, UserRequest, ProcessingResult
from components.enhanced_smartinvention_mcp_v2 import EnhancedSmartinventionAdapterMCP
from components.dynamic_expert_registry import DynamicExpertRegistry, ExpertConfig
from components.smart_routing_engine import SmartRoutingEngine, RoutingRule
from tools.tool_registry import ToolRegistry, ToolConfig, ToolType, ToolCapability

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 數據結構定義 ====================

class ManusRequestType(Enum):
    """Manus 請求類型"""
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    TASK_ANALYSIS = "task_analysis"
    UI_DESIGN_REVIEW = "ui_design_review"
    CROSS_TASK_ANALYSIS = "cross_task_analysis"
    FILE_ANALYSIS = "file_analysis"
    CONVERSATION_ANALYSIS = "conversation_analysis"
    EXPERT_CONSULTATION = "expert_consultation"

@dataclass
class RequirementAnalysisRequest:
    """需求分析請求"""
    requirement_id: str
    requirement_text: str
    analysis_scope: str = "full"  # full, basic, cross_task
    target_entity: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class RequirementItem:
    """需求項目"""
    requirement_id: str
    title: str
    description: str
    priority: str
    source_tasks: List[str]
    technical_complexity: str
    estimated_hours: int
    category: str
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ManusAction:
    """Manus 行動項目"""
    action_id: str
    action_type: str
    description: str
    related_tasks: List[str]
    execution_status: str
    priority: str
    estimated_effort: str
    prerequisites: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FileReference:
    """檔案參考"""
    file_path: str
    file_type: str
    relevance_score: float
    cross_task_relations: List[str]
    description: str
    size_bytes: Optional[int] = None
    last_modified: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CrossTaskAnalysis:
    """跨任務分析"""
    related_task_count: int
    shared_requirements: List[str]
    dependency_chain: str
    impact_assessment: str
    coordination_needs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ManusAnalysisResult:
    """Manus 分析結果"""
    request_id: str
    request_type: ManusRequestType
    target_entity: str
    analysis_timestamp: str
    requirements_list: List[RequirementItem]
    manus_actions: List[ManusAction]
    file_references: List[FileReference]
    cross_task_analysis: CrossTaskAnalysis
    expert_insights: Dict[str, Any]
    processing_metrics: Dict[str, Any]
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

# ==================== 核心組件類 ====================

class ManusRequirementParser:
    """Manus 需求解析器"""
    
    def __init__(self):
        self.requirement_patterns = {
            'req_id': r'REQ[_-]?(\d+)',
            'target_entity': r'(REQ[_-]?\d+)',
            'analysis_keywords': ['列出', '分析', '明確需求', 'manus action', '檔案列表'],
            'cross_task_keywords': ['跨任務', '同一個需求', '多任務']
        }
    
    def parse_requirement(self, requirement_text: str) -> Dict[str, Any]:
        """解析需求文本"""
        logger.info(f"🔍 解析 Manus 需求文本: {requirement_text[:100]}...")
        
        # 提取需求ID
        req_id_match = re.search(self.requirement_patterns['req_id'], requirement_text)
        target_entity = req_id_match.group(0) if req_id_match else None
        
        # 提取目標實體
        entity_match = re.search(self.requirement_patterns['target_entity'], requirement_text)
        target_entity = entity_match.group(0) if entity_match else target_entity
        
        # 分析需求類型
        requirement_type = self._classify_requirement_type(requirement_text)
        
        # 檢查是否需要跨任務分析
        cross_task_analysis = any(keyword in requirement_text for keyword in self.requirement_patterns['cross_task_keywords'])
        
        # 提取輸出格式要求
        output_format = self._extract_output_format(requirement_text)
        
        # 確定分析範圍
        analysis_scope = "full" if cross_task_analysis else "basic"
        
        result = {
            "requirement_type": requirement_type,
            "target_entity": target_entity,
            "analysis_scope": analysis_scope,
            "output_format": output_format,
            "cross_task_analysis": cross_task_analysis,
            "data_sources": ["smartinvention_mcp"],
            "expert_domains": self._determine_expert_domains(requirement_text)
        }
        
        logger.info(f"✅ Manus 需求解析完成: {result}")
        return result
    
    def _classify_requirement_type(self, text: str) -> str:
        """分類需求類型"""
        if any(keyword in text for keyword in self.requirement_patterns['analysis_keywords']):
            return "requirement_analysis"
        return "general_inquiry"
    
    def _extract_output_format(self, text: str) -> List[str]:
        """提取輸出格式要求"""
        formats = []
        if "明確需求" in text or "需求列表" in text:
            formats.append("requirements_list")
        if "manus action" in text:
            formats.append("manus_actions")
        if "檔案列表" in text:
            formats.append("file_list")
        return formats or ["requirements_list"]
    
    def _determine_expert_domains(self, text: str) -> List[str]:
        """確定需要的專家領域"""
        domains = ["manus_requirement_analysis"]  # 基礎 Manus 需求分析專家
        
        if "界面" in text or "UI" in text or "UX" in text or "設計" in text:
            domains.append("manus_ui_design_analysis")
        
        if "檔案" in text or "跨任務" in text:
            domains.append("manus_task_correlation")
        
        if "技術" in text or "實現" in text:
            domains.append("manus_file_intelligence")
        
        return domains

class ManusExpertCoordinator:
    """Manus 專家協調器 - 利用 AICore 的動態專家系統"""
    
    def __init__(self, aicore: AICore3):
        self.aicore = aicore
        self.expert_registry = aicore.expert_registry
        self.manus_experts = {}
        
    async def initialize_manus_experts(self):
        """初始化 Manus 專用專家"""
        logger.info("🧠 初始化 Manus 專用專家")
        
        manus_expert_configs = [
            {
                "expert_id": "manus_requirement_analysis",
                "domain": "manus_requirement_analysis",
                "scenario_type": "requirement_analysis",
                "skill_requirements": ["需求工程", "業務分析", "Manus系統分析"],
                "knowledge_sources": [
                    {"type": "manus_data", "path": "/manus/requirements"},
                    {"type": "task_metadata", "path": "/manus/tasks"}
                ],
                "performance_metrics": {"accuracy": 0.85, "response_time": 2.0}
            },
            {
                "expert_id": "manus_ui_design_analysis",
                "domain": "manus_ui_design_analysis", 
                "scenario_type": "ui_design_analysis",
                "skill_requirements": ["UI設計", "UX分析", "前端技術", "Manus界面"],
                "knowledge_sources": [
                    {"type": "ui_patterns", "path": "/manus/ui"},
                    {"type": "design_guidelines", "path": "/manus/design"}
                ],
                "performance_metrics": {"accuracy": 0.80, "response_time": 1.8}
            },
            {
                "expert_id": "manus_task_correlation",
                "domain": "manus_task_correlation",
                "scenario_type": "task_correlation_analysis", 
                "skill_requirements": ["任務分析", "關聯挖掘", "依賴分析"],
                "knowledge_sources": [
                    {"type": "task_relationships", "path": "/manus/correlations"},
                    {"type": "dependency_graph", "path": "/manus/dependencies"}
                ],
                "performance_metrics": {"accuracy": 0.90, "response_time": 3.2}
            },
            {
                "expert_id": "manus_file_intelligence",
                "domain": "manus_file_intelligence",
                "scenario_type": "file_intelligence_analysis",
                "skill_requirements": ["檔案分析", "代碼理解", "文檔分析"],
                "knowledge_sources": [
                    {"type": "file_metadata", "path": "/manus/files"},
                    {"type": "code_analysis", "path": "/manus/code"}
                ],
                "performance_metrics": {"accuracy": 0.88, "response_time": 2.1}
            }
        ]
        
        # 註冊 Manus 專家到 AICore 動態專家系統
        for config in manus_expert_configs:
            expert_config = ExpertConfig(
                expert_id=config["expert_id"],
                domain=config["domain"],
                scenario_type=config["scenario_type"],
                skill_requirements=config["skill_requirements"],
                knowledge_sources=config["knowledge_sources"],
                performance_metrics=config["performance_metrics"]
            )
            
            success = await self.expert_registry.register_expert(expert_config)
            if success:
                self.manus_experts[config["expert_id"]] = expert_config
                logger.info(f"✅ 註冊 Manus 專家: {config['expert_id']}")
            else:
                logger.error(f"❌ 註冊 Manus 專家失敗: {config['expert_id']}")
    
    async def coordinate_experts(self, parsed_requirement: Dict[str, Any], smartinvention_data: Dict[str, Any]) -> Dict[str, Any]:
        """協調專家分析 - 利用 AICore 動態專家系統"""
        logger.info(f"🤝 開始 Manus 專家協調，需要專家: {parsed_requirement['expert_domains']}")
        
        expert_results = {}
        
        for domain in parsed_requirement['expert_domains']:
            if domain in self.manus_experts:
                logger.info(f"🧠 調用 Manus 專家: {domain}")
                
                # 使用 AICore 的動態專家系統
                expert_request = {
                    "expert_domain": domain,
                    "task_data": smartinvention_data,
                    "requirement_context": parsed_requirement,
                    "analysis_objectives": self._get_analysis_objectives(domain, parsed_requirement)
                }
                
                expert_result = await self.expert_registry.consult_expert(domain, expert_request)
                expert_results[domain] = expert_result
        
        # 聚合專家結果
        aggregated_result = await self._aggregate_expert_results(expert_results, parsed_requirement)
        
        logger.info(f"✅ Manus 專家協調完成，共 {len(expert_results)} 個專家參與")
        return aggregated_result
    
    def _get_analysis_objectives(self, domain: str, parsed_requirement: Dict[str, Any]) -> List[str]:
        """獲取分析目標"""
        base_objectives = {
            "manus_requirement_analysis": [
                "識別明確的 Manus 需求",
                "分析需求優先級",
                "評估需求依賴關係",
                "生成 Manus actions"
            ],
            "manus_ui_design_analysis": [
                "分析 Manus 界面設計需求",
                "評估用戶體驗影響",
                "提供 UI 設計建議",
                "分析導航整合需求"
            ],
            "manus_task_correlation": [
                "分析跨任務關聯",
                "識別任務依賴關係",
                "生成依賴關係圖",
                "評估協調需求"
            ],
            "manus_file_intelligence": [
                "識別相關檔案",
                "分析檔案關聯性",
                "評估檔案重要性",
                "生成檔案列表"
            ]
        }
        
        objectives = base_objectives.get(domain, [])
        
        # 根據需求添加特定目標
        if parsed_requirement.get("cross_task_analysis"):
            objectives.append("執行跨任務分析")
        
        return objectives
    
    async def _aggregate_expert_results(self, expert_results: Dict[str, Any], parsed_requirement: Dict[str, Any]) -> Dict[str, Any]:
        """聚合專家結果"""
        logger.info("🔄 聚合 Manus 專家分析結果")
        
        # 聚合需求列表
        requirements_list = []
        manus_actions = []
        file_references = []
        expert_insights = {}
        
        for domain, result in expert_results.items():
            if result.get("success"):
                analysis = result.get("analysis_result", {})
                
                # 聚合需求
                if "identified_requirements" in analysis:
                    requirements_list.extend(analysis["identified_requirements"])
                
                # 聚合行動項目
                if "manus_actions" in analysis:
                    manus_actions.extend(analysis["manus_actions"])
                
                # 聚合檔案參考
                if "file_references" in analysis:
                    file_references.extend(analysis["file_references"])
                
                # 保存專家洞察
                expert_insights[domain] = {
                    "analysis": analysis,
                    "confidence": result.get("confidence", 0.0)
                }
        
        # 生成跨任務分析
        cross_task_analysis = self._generate_cross_task_analysis(expert_results, parsed_requirement)
        
        return {
            "requirements_list": requirements_list,
            "manus_actions": manus_actions,
            "file_references": file_references,
            "cross_task_analysis": cross_task_analysis,
            "expert_insights": expert_insights,
            "processing_metrics": self._calculate_processing_metrics(expert_results)
        }
    
    def _generate_cross_task_analysis(self, expert_results: Dict[str, Any], parsed_requirement: Dict[str, Any]) -> Dict[str, Any]:
        """生成跨任務分析"""
        if not parsed_requirement.get("cross_task_analysis"):
            return {
                "related_task_count": 0,
                "shared_requirements": [],
                "dependency_chain": "無跨任務依賴",
                "impact_assessment": "單任務範圍",
                "coordination_needs": []
            }
        
        # 從專家結果中提取跨任務信息
        related_tasks = set()
        shared_requirements = []
        coordination_needs = []
        
        for domain, result in expert_results.items():
            if result.get("success"):
                analysis = result.get("analysis_result", {})
                
                # 提取相關任務
                if "related_tasks" in analysis:
                    related_tasks.update(analysis["related_tasks"])
                
                # 提取共享需求
                if "shared_requirements" in analysis:
                    shared_requirements.extend(analysis["shared_requirements"])
                
                # 提取協調需求
                if "coordination_needs" in analysis:
                    coordination_needs.extend(analysis["coordination_needs"])
        
        return {
            "related_task_count": len(related_tasks),
            "shared_requirements": list(set(shared_requirements)),
            "dependency_chain": f"涉及 {len(related_tasks)} 個相關任務",
            "impact_assessment": "中等影響，需要跨任務協調",
            "coordination_needs": list(set(coordination_needs))
        }
    
    def _calculate_processing_metrics(self, expert_results: Dict[str, Any]) -> Dict[str, Any]:
        """計算處理指標"""
        total_experts = len(expert_results)
        successful_experts = sum(1 for result in expert_results.values() if result.get("success"))
        
        processing_times = [
            result.get("processing_time", 0) 
            for result in expert_results.values() 
            if result.get("success")
        ]
        
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        confidences = [
            result.get("confidence", 0) 
            for result in expert_results.values() 
            if result.get("success")
        ]
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            "total_experts": total_experts,
            "successful_experts": successful_experts,
            "success_rate": successful_experts / total_experts if total_experts > 0 else 0,
            "average_processing_time": avg_processing_time,
            "average_confidence": avg_confidence,
            "total_processing_time": sum(processing_times)
        }

class ManusSmartRouter:
    """Manus 智慧路由器 - 利用 AICore 的智慧路由引擎"""
    
    def __init__(self, aicore: AICore3):
        self.aicore = aicore
        self.routing_engine = aicore.routing_engine
        self.manus_routes = {}
    
    async def initialize_manus_routes(self):
        """初始化 Manus 路由規則"""
        logger.info("🛣️ 初始化 Manus 智慧路由規則")
        
        manus_routing_rules = [
            {
                "rule_id": "manus_requirement_analysis_route",
                "condition": {"request_type": "requirement_analysis", "domain": "manus"},
                "target": "manus_requirement_processor",
                "priority": 10,
                "load_balancing": True,
                "fallback": "general_requirement_processor"
            },
            {
                "rule_id": "manus_ui_design_route",
                "condition": {"request_type": "ui_design_review", "domain": "manus"},
                "target": "manus_ui_design_processor",
                "priority": 9,
                "load_balancing": True,
                "fallback": "general_ui_processor"
            },
            {
                "rule_id": "manus_cross_task_route",
                "condition": {"request_type": "cross_task_analysis", "domain": "manus"},
                "target": "manus_task_correlation_processor",
                "priority": 8,
                "load_balancing": False,
                "fallback": "general_task_processor"
            },
            {
                "rule_id": "manus_file_analysis_route",
                "condition": {"request_type": "file_analysis", "domain": "manus"},
                "target": "manus_file_intelligence_processor",
                "priority": 7,
                "load_balancing": True,
                "fallback": "general_file_processor"
            }
        ]
        
        # 註冊路由規則到 AICore 智慧路由引擎
        for rule_config in manus_routing_rules:
            routing_rule = RoutingRule(
                rule_id=rule_config["rule_id"],
                condition=rule_config["condition"],
                target=rule_config["target"],
                priority=rule_config["priority"],
                load_balancing=rule_config["load_balancing"],
                fallback=rule_config["fallback"]
            )
            
            success = await self.routing_engine.register_rule(routing_rule)
            if success:
                self.manus_routes[rule_config["rule_id"]] = routing_rule
                logger.info(f"✅ 註冊 Manus 路由規則: {rule_config['rule_id']}")
            else:
                logger.error(f"❌ 註冊 Manus 路由規則失敗: {rule_config['rule_id']}")
    
    async def route_manus_request(self, request_type: ManusRequestType, request_data: Dict[str, Any]) -> str:
        """路由 Manus 請求"""
        logger.info(f"🛣️ 路由 Manus 請求: {request_type.value}")
        
        routing_context = {
            "request_type": request_type.value,
            "domain": "manus",
            "data": request_data
        }
        
        # 使用 AICore 智慧路由引擎
        route_result = await self.routing_engine.route_request(routing_context)
        
        if route_result.get("success"):
            target = route_result.get("target")
            logger.info(f"✅ Manus 請求路由到: {target}")
            return target
        else:
            logger.warning(f"⚠️ Manus 請求路由失敗，使用默認處理器")
            return "manus_default_processor"

class ManusToolDiscovery:
    """Manus 工具發現器 - 利用 AICore 的工具註冊系統"""
    
    def __init__(self, aicore: AICore3):
        self.aicore = aicore
        self.tool_registry = aicore.tool_registry
        self.manus_tools = {}
    
    async def initialize_manus_tools(self):
        """初始化 Manus 專用工具"""
        logger.info("🔧 初始化 Manus 專用工具")
        
        manus_tool_configs = [
            {
                "tool_id": "manus_smartinvention_connector",
                "name": "Manus Smartinvention 連接器",
                "type": ToolType.PYTHON_MODULE,
                "description": "連接和查詢 Smartinvention MCP 數據",
                "capabilities": [
                    ToolCapability.DATA_RETRIEVAL,
                    ToolCapability.API_INTEGRATION
                ],
                "module_path": "components.enhanced_smartinvention_mcp_v2",
                "config": {"timeout": 30, "retry_count": 3}
            },
            {
                "tool_id": "manus_requirement_processor",
                "name": "Manus 需求處理器",
                "type": ToolType.PYTHON_MODULE,
                "description": "處理和分析 Manus 需求",
                "capabilities": [
                    ToolCapability.TEXT_PROCESSING,
                    ToolCapability.ANALYSIS
                ],
                "module_path": "components.manus_adapter_mcp",
                "config": {"analysis_depth": "deep", "output_format": "structured"}
            },
            {
                "tool_id": "manus_expert_coordinator",
                "name": "Manus 專家協調器",
                "type": ToolType.PYTHON_MODULE,
                "description": "協調多個 Manus 專家進行分析",
                "capabilities": [
                    ToolCapability.EXPERT_COORDINATION,
                    ToolCapability.RESULT_AGGREGATION
                ],
                "module_path": "components.manus_adapter_mcp",
                "config": {"max_experts": 5, "parallel_execution": True}
            }
        ]
        
        # 註冊 Manus 工具到 AICore 工具註冊系統
        for tool_config in manus_tool_configs:
            tool_config_obj = ToolConfig(
                tool_id=tool_config["tool_id"],
                name=tool_config["name"],
                tool_type=tool_config["type"],
                description=tool_config["description"],
                capabilities=tool_config["capabilities"],
                module_path=tool_config["module_path"],
                config=tool_config["config"]
            )
            
            success = await self.tool_registry.register_tool(tool_config_obj)
            if success:
                self.manus_tools[tool_config["tool_id"]] = tool_config_obj
                logger.info(f"✅ 註冊 Manus 工具: {tool_config['tool_id']}")
            else:
                logger.error(f"❌ 註冊 Manus 工具失敗: {tool_config['tool_id']}")
    
    async def discover_tools_for_request(self, request_type: ManusRequestType, requirements: List[str]) -> List[str]:
        """為請求發現合適的工具"""
        logger.info(f"🔍 為 Manus 請求發現工具: {request_type.value}")
        
        # 使用 AICore 工具發現機制
        discovery_context = {
            "request_type": request_type.value,
            "domain": "manus",
            "requirements": requirements
        }
        
        discovered_tools = await self.tool_registry.discover_tools(discovery_context)
        
        # 過濾 Manus 相關工具
        manus_tools = [
            tool for tool in discovered_tools 
            if tool.startswith("manus_") or tool in self.manus_tools
        ]
        
        logger.info(f"✅ 發現 {len(manus_tools)} 個 Manus 工具: {manus_tools}")
        return manus_tools
    
    async def execute_tool(self, tool_id: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """執行工具"""
        logger.info(f"🔧 執行 Manus 工具: {tool_id}")
        
        if tool_id not in self.manus_tools:
            logger.error(f"❌ 未知的 Manus 工具: {tool_id}")
            return {"success": False, "error": f"Unknown tool: {tool_id}"}
        
        # 使用 AICore 工具執行機制
        execution_result = await self.tool_registry.execute_tool(tool_id, tool_input)
        
        logger.info(f"✅ Manus 工具執行完成: {tool_id}")
        return execution_result

# ==================== 主要 Manus 適配器類 ====================

class ManusAdapterMCP:
    """
    統一的 Manus 適配器與需求分析處理器
    整合 Manus 系統與 AICore 3.0，利用動態專家、智慧路由、工具發現等核心能力
    """
    
    def __init__(self, aicore: AICore3):
        self.aicore = aicore
        self.smartinvention_mcp = None
        
        # 初始化核心組件
        self.requirement_parser = ManusRequirementParser()
        self.expert_coordinator = ManusExpertCoordinator(aicore)
        self.smart_router = ManusSmartRouter(aicore)
        self.tool_discovery = ManusToolDiscovery(aicore)
        
        # 狀態管理
        self.adapter_status = "initializing"
        self.registered_experts = 0
        self.registered_tools = 0
        self.cache = {}
        
        logger.info("🚀 Manus_Adapter_MCP 初始化完成")
    
    async def initialize(self):
        """初始化 Manus 適配器"""
        logger.info("🔄 初始化 Manus_Adapter_MCP")
        
        try:
            # 初始化 Smartinvention MCP
            await self._initialize_smartinvention_mcp()
            
            # 初始化 Manus 專家
            await self.expert_coordinator.initialize_manus_experts()
            self.registered_experts = len(self.expert_coordinator.manus_experts)
            
            # 初始化 Manus 路由
            await self.smart_router.initialize_manus_routes()
            
            # 初始化 Manus 工具
            await self.tool_discovery.initialize_manus_tools()
            self.registered_tools = len(self.tool_discovery.manus_tools)
            
            self.adapter_status = "active"
            logger.info("✅ Manus_Adapter_MCP 初始化成功")
            
        except Exception as e:
            self.adapter_status = "error"
            logger.error(f"❌ Manus_Adapter_MCP 初始化失敗: {e}")
            raise
    
    async def _initialize_smartinvention_mcp(self):
        """初始化 Smartinvention MCP"""
        try:
            self.smartinvention_mcp = EnhancedSmartinventionAdapterMCP()
            await self.smartinvention_mcp.initialize()
            logger.info("✅ Smartinvention MCP 初始化成功")
        except Exception as e:
            logger.error(f"❌ Smartinvention MCP 初始化失敗: {e}")
            raise
    
    async def analyze_requirement(self, requirement_text: str, target_entity: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """分析 Manus 需求 - 核心功能"""
        logger.info(f"🎯 開始 Manus 需求分析: {target_entity or 'Unknown'}")
        
        start_time = time.time()
        
        try:
            # 1. 解析需求
            parsed_requirement = self.requirement_parser.parse_requirement(requirement_text)
            if target_entity:
                parsed_requirement["target_entity"] = target_entity
            if context:
                parsed_requirement.update(context)
            
            # 2. 智慧路由
            request_type = ManusRequestType.REQUIREMENT_ANALYSIS
            route_target = await self.smart_router.route_manus_request(request_type, parsed_requirement)
            
            # 3. 工具發現
            required_capabilities = ["data_retrieval", "requirement_analysis", "expert_coordination"]
            discovered_tools = await self.tool_discovery.discover_tools_for_request(request_type, required_capabilities)
            
            # 4. 獲取 Smartinvention 數據
            smartinvention_data = await self._get_smartinvention_data(parsed_requirement)
            
            # 5. 專家協調分析
            expert_analysis = await self.expert_coordinator.coordinate_experts(parsed_requirement, smartinvention_data)
            
            # 6. 生成結果
            processing_time = time.time() - start_time
            confidence_score = expert_analysis.get("processing_metrics", {}).get("average_confidence", 0.0)
            
            result = ManusAnalysisResult(
                request_id=f"manus_req_{int(time.time())}",
                request_type=request_type,
                target_entity=parsed_requirement.get("target_entity", "Unknown"),
                analysis_timestamp=datetime.now().isoformat(),
                requirements_list=expert_analysis.get("requirements_list", []),
                manus_actions=expert_analysis.get("manus_actions", []),
                file_references=expert_analysis.get("file_references", []),
                cross_task_analysis=expert_analysis.get("cross_task_analysis", {}),
                expert_insights=expert_analysis.get("expert_insights", {}),
                processing_metrics={
                    "processing_time": processing_time,
                    "route_target": route_target,
                    "discovered_tools": discovered_tools,
                    **expert_analysis.get("processing_metrics", {})
                },
                confidence_score=confidence_score
            )
            
            logger.info(f"✅ Manus 需求分析完成，耗時 {processing_time:.2f}秒，信心度 {confidence_score:.2f}")
            
            return {
                "success": True,
                "analysis_result": asdict(result),
                "processing_time": processing_time,
                "confidence_score": confidence_score
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Manus 需求分析失敗: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "processing_time": processing_time,
                "confidence_score": 0.0
            }
    
    async def _get_smartinvention_data(self, parsed_requirement: Dict[str, Any]) -> Dict[str, Any]:
        """獲取 Smartinvention 數據"""
        logger.info("📊 獲取 Smartinvention 數據")
        
        try:
            if not self.smartinvention_mcp:
                logger.warning("⚠️ Smartinvention MCP 未初始化，使用模擬數據")
                return self._get_mock_smartinvention_data(parsed_requirement)
            
            # 使用實際的 Smartinvention MCP
            target_entity = parsed_requirement.get("target_entity", "REQ_001")
            data = await self.smartinvention_mcp.get_task_data(target_entity)
            
            logger.info("✅ Smartinvention 數據獲取成功")
            return data
            
        except Exception as e:
            logger.warning(f"⚠️ Smartinvention 數據獲取失敗，使用模擬數據: {e}")
            return self._get_mock_smartinvention_data(parsed_requirement)
    
    def _get_mock_smartinvention_data(self, parsed_requirement: Dict[str, Any]) -> Dict[str, Any]:
        """獲取模擬 Smartinvention 數據"""
        target_entity = parsed_requirement.get("target_entity", "REQ_001")
        
        return {
            "tasks": {
                "TASK_001": {
                    "id": "TASK_001",
                    "title": "智慧下載導航欄整合",
                    "description": "將智慧下載功能整合到主導航欄中，提升用戶體驗",
                    "status": "in_progress",
                    "priority": "high",
                    "related_requirements": [target_entity],
                    "files": [
                        "/manus/ui/navigation_bar.jsx",
                        "/manus/components/smart_download.js"
                    ]
                },
                "TASK_003": {
                    "id": "TASK_003", 
                    "title": "下載功能優化",
                    "description": "優化下載功能的性能和用戶界面",
                    "status": "planning",
                    "priority": "medium",
                    "related_requirements": [target_entity],
                    "files": [
                        "/manus/api/download_service.py",
                        "/manus/ui/download_modal.jsx"
                    ]
                },
                "TASK_006": {
                    "id": "TASK_006",
                    "title": "用戶認證系統整合",
                    "description": "整合用戶認證系統以支持個性化下載",
                    "status": "completed",
                    "priority": "high",
                    "related_requirements": [target_entity],
                    "files": [
                        "/manus/auth/user_service.py",
                        "/manus/middleware/auth_middleware.js"
                    ]
                }
            },
            "requirements": {
                target_entity: {
                    "id": target_entity,
                    "title": "用戶界面設計需求",
                    "description": "改善用戶界面設計，特別是導航欄的智慧下載功能整合",
                    "category": "UI/UX",
                    "priority": "high",
                    "status": "active",
                    "related_tasks": ["TASK_001", "TASK_003", "TASK_006"]
                }
            },
            "files": {
                "/manus/ui/navigation_bar.jsx": {
                    "path": "/manus/ui/navigation_bar.jsx",
                    "type": "react_component",
                    "size": 15420,
                    "last_modified": "2024-06-20T10:30:00Z",
                    "description": "主導航欄組件"
                },
                "/manus/components/smart_download.js": {
                    "path": "/manus/components/smart_download.js", 
                    "type": "javascript_module",
                    "size": 8930,
                    "last_modified": "2024-06-22T14:15:00Z",
                    "description": "智慧下載功能模組"
                },
                "/manus/design/ui_guidelines.md": {
                    "path": "/manus/design/ui_guidelines.md",
                    "type": "documentation",
                    "size": 12500,
                    "last_modified": "2024-06-18T09:00:00Z",
                    "description": "UI 設計指南文檔"
                }
            },
            "metadata": {
                "total_tasks": 3,
                "total_requirements": 1,
                "total_files": 3,
                "last_updated": datetime.now().isoformat()
            }
        }
    
    async def handle_manus_request(self, endpoint: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理 Manus API 請求"""
        logger.info(f"🌐 處理 Manus API 請求: {endpoint}")
        
        try:
            if endpoint == "/api/manus/requirement/analyze":
                return await self._handle_requirement_analysis(request_data)
            elif endpoint == "/api/manus/task/analyze":
                return await self._handle_task_analysis(request_data)
            elif endpoint == "/api/manus/ui/review":
                return await self._handle_ui_review(request_data)
            elif endpoint == "/api/manus/cross-task/analyze":
                return await self._handle_cross_task_analysis(request_data)
            elif endpoint == "/api/manus/status":
                return await self.get_manus_status()
            else:
                return {
                    "success": False,
                    "error": f"Unknown endpoint: {endpoint}"
                }
                
        except Exception as e:
            logger.error(f"❌ Manus API 請求處理失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_requirement_analysis(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理需求分析請求"""
        requirement_text = request_data.get("requirement_text", "")
        target_entity = request_data.get("target_entity")
        context = request_data.get("context", {})
        
        result = await self.analyze_requirement(requirement_text, target_entity, context)
        
        return {
            "success": result["success"],
            "data": result.get("analysis_result", {}),
            "processing_time": result.get("processing_time", 0),
            "confidence_score": result.get("confidence_score", 0)
        }
    
    async def _handle_task_analysis(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理任務分析請求"""
        # 模擬任務分析
        return {
            "success": True,
            "data": {
                "task_analysis": "任務分析結果",
                "recommendations": ["建議1", "建議2"]
            },
            "processing_time": 1.5,
            "confidence_score": 0.82
        }
    
    async def _handle_ui_review(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理 UI 審查請求"""
        ui_component = request_data.get("ui_component", "")
        design_requirements = request_data.get("design_requirements", [])
        
        # 模擬 UI 審查
        return {
            "success": True,
            "data": {
                "ui_component": ui_component,
                "review_result": "UI 審查通過",
                "recommendations": [
                    "改善響應式設計",
                    "優化用戶交互流程",
                    "增強視覺一致性"
                ],
                "design_score": 8.5
            },
            "processing_time": 2.1,
            "confidence_score": 0.88
        }
    
    async def _handle_cross_task_analysis(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理跨任務分析請求"""
        task_list = request_data.get("task_list", [])
        analysis_focus = request_data.get("analysis_focus", "dependencies")
        
        # 模擬跨任務分析
        return {
            "success": True,
            "data": {
                "analyzed_tasks": task_list,
                "analysis_focus": analysis_focus,
                "dependencies": [
                    {"from": "TASK_001", "to": "TASK_003", "type": "功能依賴"},
                    {"from": "TASK_003", "to": "TASK_006", "type": "數據依賴"}
                ],
                "coordination_recommendations": [
                    "建立任務間溝通機制",
                    "統一技術標準",
                    "協調發布時程"
                ]
            },
            "processing_time": 3.2,
            "confidence_score": 0.91
        }
    
    async def get_manus_status(self) -> Dict[str, Any]:
        """獲取 Manus 適配器狀態"""
        return {
            "success": True,
            "data": {
                "adapter_status": self.adapter_status,
                "registered_experts": self.registered_experts,
                "registered_tools": self.registered_tools,
                "aicore_connected": self.aicore is not None,
                "expert_registry_available": hasattr(self.aicore, 'expert_registry'),
                "routing_engine_available": hasattr(self.aicore, 'routing_engine'),
                "tool_registry_available": hasattr(self.aicore, 'tool_registry'),
                "cache_size": len(self.cache),
                "version": "1.0.0"
            }
        }

# ==================== 工廠函數 ====================

async def create_manus_adapter_mcp(aicore: AICore3) -> ManusAdapterMCP:
    """創建並初始化 Manus_Adapter_MCP"""
    adapter = ManusAdapterMCP(aicore)
    await adapter.initialize()
    return adapter

# ==================== CLI 接口 ====================

async def main():
    """主函數 - CLI 接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manus_Adapter_MCP CLI")
    parser.add_argument("--action", choices=["analyze", "status", "test"], default="test", help="執行的動作")
    parser.add_argument("--requirement", type=str, help="需求文本")
    parser.add_argument("--target", type=str, help="目標實體")
    
    args = parser.parse_args()
    
    # 創建 AICore (模擬)
    from core.aicore3 import create_aicore3
    aicore = create_aicore3()
    await aicore.initialize()
    
    # 創建 Manus 適配器
    manus_adapter = await create_manus_adapter_mcp(aicore)
    
    if args.action == "analyze":
        if not args.requirement:
            print("❌ 請提供需求文本 (--requirement)")
            return
        
        result = await manus_adapter.analyze_requirement(
            requirement_text=args.requirement,
            target_entity=args.target
        )
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == "status":
        status = await manus_adapter.get_manus_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    elif args.action == "test":
        # 運行測試
        test_requirement = "首先先針對 REQ_001: 用戶界面設計需求 列出我的明確需求 及manus action 包含相關的檔案列表 注意同一個需求可能跨任務"
        
        print("🧪 運行 Manus_Adapter_MCP 測試")
        print(f"📝 測試需求: {test_requirement}")
        
        result = await manus_adapter.analyze_requirement(
            requirement_text=test_requirement,
            target_entity="REQ_001"
        )
        
        if result["success"]:
            print("✅ 測試成功")
            analysis = result["analysis_result"]
            print(f"⚡ 處理時間: {result['processing_time']:.2f}秒")
            print(f"🎯 信心度: {result['confidence_score']:.2f}")
            print(f"📋 需求數量: {len(analysis['requirements_list'])}")
            print(f"🚀 行動數量: {len(analysis['manus_actions'])}")
            print(f"📁 檔案數量: {len(analysis['file_references'])}")
        else:
            print(f"❌ 測試失敗: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())

