"""
AICore 3.0 - 動態專家系統整合版
Enhanced AICore with Dynamic Expert System Integration
"""

import asyncio
import time
import logging
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

# 導入組件
from components.general_processor_mcp import GeneralProcessorMCP, create_general_processor_mcp
from components.dynamic_expert_registry import (
    DynamicExpertRegistry, create_dynamic_expert_registry,
    ExpertRegistrationRequest, ExpertProfile, ExpertStatus, ExpertType as DynamicExpertType
)
from components.expert_recommendation_aggregator import (
    ExpertRecommendationAggregator, create_expert_recommendation_aggregator,
    AggregationStrategy, AggregatedRecommendation, AggregationResult
)
from components.dynamic_mcp_generator import (
    DynamicMCPGenerator, create_dynamic_mcp_generator,
    MCPToolType, MCPToolSpec, DynamicMCPRequest
)
from tools.tool_registry import ToolRegistry
from actions.action_executor import ActionExecutor

logger = logging.getLogger(__name__)

class ProcessingStage(Enum):
    """處理階段 - 6階段完整流程"""
    INTEGRATED_SEARCH_ANALYSIS = "integrated_search_analysis"      # 整合式搜索和分析
    DYNAMIC_EXPERT_GENERATION = "dynamic_expert_generation"        # 動態專家生成
    EXPERT_RESPONSE_GENERATION = "expert_response_generation"      # 專家回答生成
    EXPERT_RECOMMENDATION_AGGREGATION = "expert_recommendation_aggregation"  # 專家建議聚合
    DYNAMIC_TOOL_GENERATION = "dynamic_tool_generation"           # 動態工具生成和執行
    FINAL_RESULT_GENERATION = "final_result_generation"           # 最終結果生成

@dataclass
class UserRequest:
    """用戶請求數據結構"""
    id: str
    content: str
    context: Dict[str, Any]
    priority: str = "normal"
    metadata: Dict[str, Any] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class ExpertResponse:
    """專家響應數據結構"""
    expert_id: str
    expert_name: str
    expert_type: str
    analysis: str
    recommendations: List[str]
    tool_suggestions: List[Dict[str, Any]]
    confidence: float
    processing_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ProcessingResult:
    """處理結果數據結構"""
    request_id: str
    success: bool
    stage_results: Dict[str, Any]
    expert_analysis: List[ExpertResponse]
    tool_execution_results: List[Dict[str, Any]]
    final_answer: str
    confidence: float
    execution_time: float
    metadata: Dict[str, Any]
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class IntegratedCloudSearch:
    """整合式Cloud Search引擎"""
    
    def __init__(self):
        self.mock_mode = True  # 開發階段使用模擬模式
    
    async def integrated_search(self, params: Dict) -> Dict:
        """整合式搜索 - 一次搜索解決多個目標"""
        primary_query = params["primary_query"]
        context = params.get("context", {})
        objectives = params.get("search_objectives", [])
        
        logger.info(f"🔍 執行整合式搜索: {primary_query}")
        
        if self.mock_mode:
            return await self._mock_integrated_search(primary_query, context, objectives)
        else:
            return await self._real_integrated_search(primary_query, context, objectives)
    
    async def _mock_integrated_search(self, query: str, context: Dict, objectives: List[str]) -> Dict:
        """模擬整合式搜索"""
        
        # 模擬背景信息搜索結果
        background_results = {
            "documents": [
                f"相關文檔1: {query} 的技術實現指南",
                f"相關文檔2: {query} 的最佳實踐",
                f"相關文檔3: {query} 的案例研究"
            ],
            "context_enrichment": {
                "technologies": self._extract_technologies(query),
                "domains": self._extract_domains(query),
                "complexity": self._assess_complexity(query)
            },
            "relevance_score": 0.85
        }
        
        # 模擬專家識別結果
        expert_results = {
            "detected_domains": self._detect_expert_domains(query),
            "expert_requirements": self._generate_expert_requirements(query),
            "dynamic_experts_needed": len(self._detect_expert_domains(query)) > 2,
            "complexity_level": self._assess_complexity(query)
        }
        
        # 模擬場景分析結果
        scenario_results = {
            "scenario_type": self._classify_scenario(query),
            "use_cases": self._extract_use_cases(query),
            "patterns": self._extract_patterns(query),
            "recommendations": self._generate_recommendations(query)
        }
        
        return {
            "background": background_results,
            "experts": expert_results,
            "scenario": scenario_results,
            "metadata": {
                "search_time": time.time(),
                "objectives_completed": len(objectives),
                "total_results": 15
            }
        }
    
    def _extract_technologies(self, query: str) -> List[str]:
        """提取技術關鍵詞"""
        tech_keywords = {
            "python": ["python", "django", "flask", "fastapi"],
            "javascript": ["javascript", "react", "vue", "node"],
            "testing": ["test", "pytest", "selenium", "cypress"],
            "deployment": ["deploy", "docker", "kubernetes", "ci/cd"],
            "database": ["database", "sql", "mongodb", "redis"]
        }
        
        detected = []
        query_lower = query.lower()
        
        for tech, keywords in tech_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected.append(tech)
        
        return detected
    
    def _extract_domains(self, query: str) -> List[str]:
        """提取業務領域"""
        domain_keywords = {
            "web_development": ["web", "website", "frontend", "backend"],
            "data_analysis": ["data", "analysis", "analytics", "visualization"],
            "testing": ["test", "qa", "quality", "automation"],
            "deployment": ["deploy", "devops", "infrastructure", "production"],
            "security": ["security", "auth", "encryption", "vulnerability"]
        }
        
        detected = []
        query_lower = query.lower()
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected.append(domain)
        
        return detected
    
    def _assess_complexity(self, query: str) -> str:
        """評估複雜度"""
        complexity_indicators = {
            "HIGH": ["enterprise", "large scale", "distributed", "microservice", "complex"],
            "MEDIUM": ["integration", "multiple", "several", "moderate"],
            "LOW": ["simple", "basic", "single", "straightforward"]
        }
        
        query_lower = query.lower()
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                return level
        
        return "MEDIUM"
    
    def _detect_expert_domains(self, query: str) -> List[str]:
        """檢測需要的專家領域"""
        expert_patterns = {
            "testing": ["test", "qa", "quality assurance", "automation", "bug"],
            "deployment": ["deploy", "devops", "ci/cd", "infrastructure", "production"],
            "coding": ["code", "programming", "development", "implement"],
            "debugging": ["debug", "error", "exception", "troubleshoot"],
            "architecture": ["architecture", "design", "system design", "scalability"],
            "performance": ["performance", "optimization", "speed", "latency"],
            "security": ["security", "authentication", "encryption", "vulnerability"],
            "data_analysis": ["data", "analysis", "analytics", "visualization"],
            "integration": ["integration", "api", "interface", "connector"],
            "monitoring": ["monitoring", "logging", "observability", "metrics"]
        }
        
        detected = []
        query_lower = query.lower()
        
        for domain, patterns in expert_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                detected.append(domain)
        
        return detected or ["coding"]  # 默認需要編程專家
    
    def _generate_expert_requirements(self, query: str) -> List[Dict]:
        """生成專家需求"""
        domains = self._detect_expert_domains(query)
        technologies = self._extract_technologies(query)
        complexity = self._assess_complexity(query)
        
        requirements = []
        
        for domain in domains:
            requirement = {
                "domain": domain,
                "scenario_type": self._map_domain_to_scenario(domain),
                "skill_level": self._determine_skill_level(complexity),
                "specific_skills": self._get_domain_skills(domain, technologies),
                "priority": self._calculate_domain_priority(domain),
                "knowledge_sources": [
                    {"type": "search_result", "content": f"{domain} best practices for {query}"},
                    {"type": "documentation", "content": f"{domain} implementation guide"},
                    {"type": "example", "content": f"{domain} code examples"}
                ]
            }
            requirements.append(requirement)
        
        return requirements
    
    def _map_domain_to_scenario(self, domain: str) -> str:
        """將領域映射到場景類型"""
        mapping = {
            "testing": "TESTING",
            "deployment": "DEPLOYMENT",
            "coding": "CODING",
            "debugging": "DEBUGGING",
            "architecture": "ARCHITECTURE",
            "performance": "PERFORMANCE",
            "security": "SECURITY",
            "data_analysis": "DATA_ANALYSIS",
            "integration": "INTEGRATION",
            "monitoring": "MONITORING"
        }
        return mapping.get(domain, "GENERAL")
    
    def _determine_skill_level(self, complexity: str) -> str:
        """確定技能等級"""
        mapping = {
            "HIGH": "expert",
            "MEDIUM": "advanced",
            "LOW": "intermediate"
        }
        return mapping.get(complexity, "intermediate")
    
    def _get_domain_skills(self, domain: str, technologies: List[str]) -> List[str]:
        """獲取領域技能"""
        base_skills = {
            "testing": ["unit_testing", "integration_testing", "test_automation"],
            "deployment": ["ci_cd", "containerization", "infrastructure_as_code"],
            "coding": ["clean_code", "design_patterns", "algorithms"],
            "debugging": ["troubleshooting", "log_analysis", "performance_profiling"],
            "architecture": ["system_design", "scalability", "microservices"],
            "performance": ["optimization", "caching", "load_testing"],
            "security": ["authentication", "authorization", "encryption"],
            "data_analysis": ["data_processing", "visualization", "statistics"],
            "integration": ["api_design", "message_queues", "webhooks"],
            "monitoring": ["logging", "metrics", "alerting"]
        }
        
        skills = base_skills.get(domain, ["general"])
        skills.extend(technologies)  # 添加技術相關技能
        
        return skills
    
    def _calculate_domain_priority(self, domain: str) -> int:
        """計算領域優先級"""
        priority_map = {
            "security": 10,
            "performance": 9,
            "testing": 8,
            "deployment": 8,
            "architecture": 7,
            "coding": 7,
            "debugging": 6,
            "integration": 6,
            "data_analysis": 5,
            "monitoring": 5
        }
        return priority_map.get(domain, 5)
    
    def _classify_scenario(self, query: str) -> str:
        """分類場景類型"""
        domains = self._detect_expert_domains(query)
        if domains:
            return self._map_domain_to_scenario(domains[0])
        return "GENERAL"
    
    def _extract_use_cases(self, query: str) -> List[str]:
        """提取使用案例"""
        return [
            f"Use case 1: {query} implementation",
            f"Use case 2: {query} optimization",
            f"Use case 3: {query} troubleshooting"
        ]
    
    def _extract_patterns(self, query: str) -> List[str]:
        """提取模式"""
        return [
            f"Pattern 1: Standard {query} approach",
            f"Pattern 2: Advanced {query} techniques"
        ]
    
    def _generate_recommendations(self, query: str) -> List[str]:
        """生成建議"""
        return [
            f"建議1: 遵循 {query} 最佳實踐",
            f"建議2: 考慮 {query} 的性能優化",
            f"建議3: 實施 {query} 的安全措施"
        ]

class AICore3:
    """AICore 3.0 - 動態專家系統整合版"""
    
    def __init__(self):
        """初始化AICore 3.0"""
        logger.info("🚀 初始化AICore 3.0 - 動態專家系統")
        
        # 核心組件
        self.general_processor = create_general_processor_mcp()
        self.dynamic_expert_registry = create_dynamic_expert_registry()
        self.expert_aggregator = create_expert_recommendation_aggregator()
        self.dynamic_mcp_generator = create_dynamic_mcp_generator()
        self.integrated_search = IntegratedCloudSearch()
        
        # 工具和執行器
        self.tool_registry = ToolRegistry()
        self.action_executor = ActionExecutor()
        
        # Smartinvention Adapter MCP
        from components.smartinvention_adapter_mcp import SmartinventionAdapterMCP
        self.smartinvention_adapter = None  # 延遲初始化
        
        # 統計和監控
        self.stage_statistics = {}
        self.expert_usage_stats = {}
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_response_time": 0.0,
            "expert_hit_rate": 0.0,
            "dynamic_tools_generated": 0
        }
        
        logger.info("🚀 AICore 3.0 初始化完成 - 動態專家系統已啟用")    
    async def initialize(self):
        """初始化AICore 3.0"""
        logger.info("🔧 初始化AICore 3.0組件...")
        
        try:
            # 初始化工具註冊表
            await self.tool_registry.initialize()
            
            # 初始化動態專家註冊中心
            await self.dynamic_expert_registry.initialize()
            
            # 初始化Smartinvention Adapter MCP
            if self.smartinvention_adapter is None:
                from components.smartinvention_adapter_mcp import SmartinventionAdapterMCP
                smartinvention_config = {
                    'data_dir': '/tmp/smartinvention_data',
                    'sync_interval': 30,
                    'max_retries': 3,
                    'local_endpoint': 'http://localhost:8000',
                    'cloud_endpoint': 'http://18.212.97.173:8000'
                }
                self.smartinvention_adapter = SmartinventionAdapterMCP(smartinvention_config)
                await self.smartinvention_adapter.initialize()
                logger.info("✅ Smartinvention Adapter MCP 初始化完成")
            
            # 初始化統計
            for stage in ProcessingStage:
                self.stage_statistics[stage.value] = {
                    "count": 0,
                    "total_time": 0.0,
                    "average_time": 0.0,
                    "success_rate": 0.0
                }
            
            logger.info("✅ AICore 3.0 初始化完成")
            
        except Exception as e:
            logger.error(f"❌ AICore 3.0 初始化失敗: {e}")
            raise
    
    async def process_request(self, request: UserRequest) -> ProcessingResult:
        """處理用戶請求 - 5階段動態專家流程"""
        start_time = time.time()
        stage_results = {}
        
        logger.info(f"🎯 開始處理請求: {request.id}")
        
        try:
            # 階段1: 整合式搜索和分析
            stage_results['integrated_search'] = await self._stage1_integrated_search_and_analysis(request)
            
            # 階段2: 動態專家生成
            stage_results['dynamic_expert_generation'] = await self._stage2_dynamic_expert_generation(
                request, stage_results['integrated_search']
            )
            
            # 階段3: 專家回答生成 (並行)
            stage_results['expert_response_generation'] = await self._stage3_expert_response_generation(
                request, stage_results['dynamic_expert_generation']['selected_experts']
            )
            
            # 階段4: 智能工具執行
            stage_results['intelligent_tool_execution'] = await self._stage4_intelligent_tool_execution(
                request, stage_results['expert_response_generation']['expert_responses']
            )
            
            # 階段5: 最終結果生成
            final_result = await self._stage5_final_result_generation(
                request, stage_results, start_time
            )
            
            # 更新統計
            await self._update_execution_stats(final_result, stage_results)
            
            logger.info(f"✅ 請求處理完成: {request.id}, 耗時: {final_result.execution_time:.2f}s")
            return final_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ 請求處理失敗: {request.id}, 錯誤: {e}")
            
            return ProcessingResult(
                request_id=request.id,
                success=False,
                stage_results=stage_results,
                expert_analysis=[],
                tool_execution_results=[],
                final_answer=f"處理失敗: {str(e)}",
                confidence=0.0,
                execution_time=execution_time,
                metadata={"error": str(e), "failed_stage": len(stage_results)}
            )
    
    async def _stage1_integrated_search_and_analysis(self, request: UserRequest) -> Dict[str, Any]:
        """階段1: 整合式搜索和分析"""
        stage_start = time.time()
        logger.info(f"🔍 階段1: 整合式搜索和分析 - {request.id}")
        
        # 執行整合式搜索
        search_result = await self.integrated_search.integrated_search({
            "primary_query": request.content,
            "context": request.context,
            "search_objectives": [
                "background_information",
                "expert_identification",
                "scenario_analysis"
            ]
        })
        
        stage_time = time.time() - stage_start
        await self._update_stage_stats(ProcessingStage.INTEGRATED_SEARCH_ANALYSIS, stage_time)
        
        logger.info(f"📊 搜索完成，發現 {len(search_result['experts']['detected_domains'])} 個專家領域")
        
        return {
            "background_info": search_result["background"],
            "expert_analysis": search_result["experts"],
            "scenario_context": search_result["scenario"],
            "search_metadata": search_result["metadata"],
            "stage_execution_time": stage_time
        }
    
    async def _stage2_dynamic_expert_generation(self, request: UserRequest, 
                                              search_results: Dict[str, Any]) -> Dict[str, Any]:
        """階段2: 動態專家生成"""
        stage_start = time.time()
        logger.info(f"🧠 階段2: 動態專家生成 - {request.id}")
        
        expert_analysis = search_results["expert_analysis"]
        scenario_context = search_results["scenario_context"]
        
        # 獲取現有專家
        existing_experts = await self.dynamic_expert_registry.find_experts_for_scenario({
            "type": scenario_context["scenario_type"],
            "domains": expert_analysis["detected_domains"],
            "complexity": expert_analysis["complexity_level"]
        })
        
        # 註冊新的動態專家（如果需要）
        new_experts = []
        if expert_analysis.get("dynamic_experts_needed", False):
            for requirement in expert_analysis["expert_requirements"]:
                try:
                    registration_request = ExpertRegistrationRequest(
                        domain=requirement["domain"],
                        scenario_type=requirement["scenario_type"],
                        skill_requirements=requirement["specific_skills"],
                        knowledge_sources=requirement["knowledge_sources"],
                        priority=requirement["priority"],
                        context=request.context,
                        requester=f"request_{request.id}"
                    )
                    
                    # 檢查是否已有類似專家
                    similar_expert = await self.dynamic_expert_registry._find_similar_expert(registration_request)
                    if not similar_expert:
                        new_expert = await self.dynamic_expert_registry.register_dynamic_expert(registration_request)
                        new_experts.append(new_expert)
                        logger.info(f"✨ 創建新專家: {new_expert.name}")
                    else:
                        logger.info(f"🔄 使用現有專家: {similar_expert.name}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ 專家創建失敗: {requirement['domain']}, 錯誤: {e}")
        
        # 選擇最終專家組合
        all_experts = existing_experts + new_experts
        selected_experts = await self._select_optimal_expert_combination(
            all_experts, expert_analysis, scenario_context
        )
        
        stage_time = time.time() - stage_start
        await self._update_stage_stats(ProcessingStage.DYNAMIC_EXPERT_GENERATION, stage_time)
        
        logger.info(f"👥 專家選擇完成，共選中 {len(selected_experts)} 位專家")
        
        return {
            "existing_experts": len(existing_experts),
            "new_experts": len(new_experts),
            "selected_experts": selected_experts,
            "expert_selection_reasoning": self._generate_selection_reasoning(selected_experts),
            "stage_execution_time": stage_time
        }
    
    async def _stage3_expert_response_generation(self, request: UserRequest, 
                                               selected_experts: List[ExpertProfile]) -> Dict[str, Any]:
        """階段3: 專家回答生成 (並行)"""
        stage_start = time.time()
        logger.info(f"🎭 階段3: 專家回答生成 - {request.id}")
        
        # 並行生成專家回答
        expert_tasks = []
        for expert in selected_experts:
            task = asyncio.create_task(
                self._generate_expert_response(expert, request)
            )
            expert_tasks.append(task)
        
        # 等待所有專家回答完成
        expert_responses = []
        for i, task in enumerate(expert_tasks):
            try:
                response = await task
                expert_responses.append(response)
                logger.info(f"✅ 專家 {selected_experts[i].name} 回答完成")
            except Exception as e:
                logger.error(f"❌ 專家 {selected_experts[i].name} 回答失敗: {e}")
                # 創建錯誤回答
                error_response = ExpertResponse(
                    expert_id=selected_experts[i].id,
                    expert_name=selected_experts[i].name,
                    expert_type=selected_experts[i].type.value,
                    analysis=f"專家回答生成失敗: {str(e)}",
                    recommendations=[],
                    tool_suggestions=[],
                    confidence=0.0,
                    metadata={"error": str(e)}
                )
                expert_responses.append(error_response)
        
        # 更新專家使用統計
        for expert in selected_experts:
            await self._update_expert_usage_stats(expert.id)
        
        stage_time = time.time() - stage_start
        await self._update_stage_stats(ProcessingStage.EXPERT_RESPONSE_GENERATION, stage_time)
        
        logger.info(f"📝 專家回答生成完成，共 {len(expert_responses)} 個回答")
        
        return {
            "expert_responses": expert_responses,
            "parallel_execution_time": stage_time,
            "expert_count": len(selected_experts),
            "success_rate": len([r for r in expert_responses if r.confidence > 0]) / len(expert_responses)
        }
    
    async def _stage4_intelligent_tool_execution(self, request: UserRequest, 
                                                expert_responses: List[ExpertResponse]) -> Dict[str, Any]:
        """階段4: 智能工具執行"""
        stage_start = time.time()
        logger.info(f"🛠️ 階段4: 智能工具執行 - {request.id}")
        
        # 收集所有專家的工具建議
        all_tool_suggestions = []
        for response in expert_responses:
            all_tool_suggestions.extend(response.tool_suggestions)
        
        # 智能選擇工具
        selected_tools = await self._intelligent_tool_selection(all_tool_suggestions, request)
        
        # 執行選中的工具
        tool_execution_results = []
        for tool_suggestion in selected_tools:
            try:
                result = await self._execute_tool(tool_suggestion, request)
                tool_execution_results.append(result)
                logger.info(f"🔧 工具執行完成: {tool_suggestion['tool_name']}")
            except Exception as e:
                logger.error(f"❌ 工具執行失敗: {tool_suggestion['tool_name']}, 錯誤: {e}")
                tool_execution_results.append({
                    "tool_name": tool_suggestion['tool_name'],
                    "success": False,
                    "error": str(e),
                    "result": None
                })
        
        stage_time = time.time() - stage_start
        await self._update_stage_stats(ProcessingStage.INTELLIGENT_TOOL_EXECUTION, stage_time)
        
        logger.info(f"⚙️ 工具執行完成，共執行 {len(tool_execution_results)} 個工具")
        
        return {
            "tool_suggestions": all_tool_suggestions,
            "selected_tools": selected_tools,
            "execution_results": tool_execution_results,
            "stage_execution_time": stage_time,
            "tool_success_rate": len([r for r in tool_execution_results if r.get("success", False)]) / len(tool_execution_results) if tool_execution_results else 0
        }
    
    async def _stage5_final_result_generation(self, request: UserRequest, 
                                            stage_results: Dict[str, Any], 
                                            start_time: float) -> ProcessingResult:
        """階段5: 最終結果生成"""
        stage_start = time.time()
        logger.info(f"📋 階段5: 最終結果生成 - {request.id}")
        
        # 聚合所有專家分析
        expert_responses = stage_results['expert_response_generation']['expert_responses']
        tool_results = stage_results['intelligent_tool_execution']['execution_results']
        
        # 生成綜合分析
        comprehensive_analysis = await self._generate_comprehensive_analysis(
            expert_responses, tool_results, request
        )
        
        # 計算整體信心度
        overall_confidence = await self._calculate_overall_confidence(
            expert_responses, tool_results, stage_results
        )
        
        # 生成最終答案
        final_answer = await self._generate_final_answer(
            comprehensive_analysis, expert_responses, tool_results
        )
        
        execution_time = time.time() - start_time
        stage_time = time.time() - stage_start
        await self._update_stage_stats(ProcessingStage.FINAL_RESULT_GENERATION, stage_time)
        
        logger.info(f"🎉 最終結果生成完成，信心度: {overall_confidence:.2f}")
        
        return ProcessingResult(
            request_id=request.id,
            success=True,
            stage_results=stage_results,
            expert_analysis=expert_responses,
            tool_execution_results=tool_results,
            final_answer=final_answer,
            confidence=overall_confidence,
            execution_time=execution_time,
            metadata={
                "comprehensive_analysis": comprehensive_analysis,
                "stage_count": len(stage_results),
                "expert_count": len(expert_responses),
                "tool_count": len(tool_results),
                "processing_stages": list(stage_results.keys())
            }
        )
    
    # 輔助方法
    async def _select_optimal_expert_combination(self, experts: List[ExpertProfile], 
                                               expert_analysis: Dict, 
                                               scenario_context: Dict) -> List[ExpertProfile]:
        """選擇最優專家組合"""
        if not experts:
            return []
        
        # 按性能和相關性排序
        scored_experts = []
        for expert in experts:
            score = await self._calculate_expert_score(expert, expert_analysis, scenario_context)
            scored_experts.append((expert, score))
        
        # 排序並選擇前N個
        scored_experts.sort(key=lambda x: x[1], reverse=True)
        
        # 根據複雜度確定專家數量
        max_experts = {
            "LOW": 2,
            "MEDIUM": 3,
            "HIGH": 4,
            "CRITICAL": 5
        }.get(expert_analysis.get("complexity_level", "MEDIUM"), 3)
        
        selected = [expert for expert, score in scored_experts[:max_experts]]
        return selected
    
    async def _calculate_expert_score(self, expert: ExpertProfile, 
                                    expert_analysis: Dict, 
                                    scenario_context: Dict) -> float:
        """計算專家分數"""
        score = 0.0
        
        # 性能分數 (40%)
        performance_score = (
            expert.performance_metrics.get("success_rate", 0.8) * 0.4 +
            expert.performance_metrics.get("accuracy", 0.8) * 0.3 +
            expert.performance_metrics.get("user_satisfaction", 0.8) * 0.3
        )
        score += performance_score * 0.4
        
        # 領域匹配分數 (30%)
        domain_match = 0.0
        for domain in expert_analysis.get("detected_domains", []):
            if domain in expert.specializations:
                domain_match += 1.0
        domain_score = min(1.0, domain_match / len(expert_analysis.get("detected_domains", [1])))
        score += domain_score * 0.3
        
        # 能力匹配分數 (20%)
        capability_match = 0.0
        expert_capabilities = [cap.name for cap in expert.capabilities]
        for req in expert_analysis.get("expert_requirements", []):
            for skill in req.get("specific_skills", []):
                if skill in expert_capabilities:
                    capability_match += 1.0
        
        total_required_skills = sum(len(req.get("specific_skills", [])) for req in expert_analysis.get("expert_requirements", []))
        capability_score = min(1.0, capability_match / max(1, total_required_skills))
        score += capability_score * 0.2
        
        # 使用頻率分數 (10%)
        usage_count = expert.performance_metrics.get("usage_count", 0)
        usage_score = min(1.0, usage_count / 100.0)  # 100次使用為滿分
        score += usage_score * 0.1
        
        return score
    
    def _generate_selection_reasoning(self, experts: List[ExpertProfile]) -> str:
        """生成專家選擇理由"""
        if not experts:
            return "未找到合適的專家"
        
        reasoning = f"選擇了 {len(experts)} 位專家：\n"
        for expert in experts:
            reasoning += f"- {expert.name}: 專精於 {', '.join(expert.specializations)}\n"
        
        return reasoning
    
    async def _generate_expert_response(self, expert: ExpertProfile, request: UserRequest) -> ExpertResponse:
        """生成專家回答"""
        response_start = time.time()
        
        try:
            # 基於專家知識庫生成回答
            analysis = await self._generate_expert_analysis(expert, request)
            recommendations = await self._generate_expert_recommendations(expert, request)
            tool_suggestions = await self._generate_expert_tool_suggestions(expert, request)
            confidence = await self._calculate_expert_confidence(expert, request)
            
            # 更新專家性能
            performance_data = {
                "success": True,
                "response_time": time.time() - response_start,
                "context": {"request_id": request.id}
            }
            await self.dynamic_expert_registry.update_expert_performance(expert.id, performance_data)
            
            return ExpertResponse(
                expert_id=expert.id,
                expert_name=expert.name,
                expert_type=expert.type.value,
                analysis=analysis,
                recommendations=recommendations,
                tool_suggestions=tool_suggestions,
                confidence=confidence,
                processing_time=time.time() - response_start,
                metadata={
                    "expert_specializations": expert.specializations,
                    "capability_count": len(expert.capabilities)
                }
            )
            
        except Exception as e:
            # 更新失敗性能
            performance_data = {
                "success": False,
                "response_time": time.time() - response_start,
                "error": str(e),
                "context": {"request_id": request.id}
            }
            await self.dynamic_expert_registry.update_expert_performance(expert.id, performance_data)
            raise
    
    async def _generate_expert_analysis(self, expert: ExpertProfile, request: UserRequest) -> str:
        """生成專家分析"""
        # 基於專家知識庫和能力生成分析
        analysis = f"作為 {expert.name}，我分析了您的請求：{request.content[:100]}...\n\n"
        
        # 添加專業領域分析
        for specialization in expert.specializations:
            analysis += f"從 {specialization} 角度來看，"
            
            # 基於知識庫內容
            knowledge_content = expert.knowledge_base.get("content", [])
            if knowledge_content:
                analysis += f"根據相關知識和最佳實踐，{knowledge_content[0][:100]}...\n"
            else:
                analysis += f"建議採用標準的 {specialization} 方法來解決這個問題。\n"
        
        # 添加能力相關分析
        relevant_capabilities = [cap for cap in expert.capabilities if any(keyword in request.content.lower() for keyword in cap.keywords)]
        if relevant_capabilities:
            analysis += f"\n基於我在 {', '.join([cap.name for cap in relevant_capabilities])} 方面的專業能力，"
            analysis += "我建議採用以下方法來實現您的需求。"
        
        return analysis
    
    async def _generate_expert_recommendations(self, expert: ExpertProfile, request: UserRequest) -> List[str]:
        """生成專家建議"""
        recommendations = []
        
        # 基於專家能力生成建議
        for capability in expert.capabilities:
            if any(keyword in request.content.lower() for keyword in capability.keywords):
                recommendations.append(f"建議使用 {capability.name} 相關的最佳實踐")
        
        # 基於專業領域生成建議
        for specialization in expert.specializations:
            recommendations.append(f"從 {specialization} 角度，建議進行詳細的需求分析")
        
        # 基於知識庫生成建議
        best_practices = expert.knowledge_base.get("best_practices", [])
        for practice in best_practices[:2]:  # 最多2個最佳實踐
            recommendations.append(practice)
        
        return recommendations[:5]  # 最多5個建議
    
    async def _generate_expert_tool_suggestions(self, expert: ExpertProfile, request: UserRequest) -> List[Dict[str, Any]]:
        """生成專家工具建議"""
        suggestions = []
        
        # 基於專家類型推薦工具
        if expert.type == DynamicExpertType.DYNAMIC_EXPERT:
            # 動態專家推薦General Processor
            suggestions.append({
                "tool_name": "general_processor_mcp",
                "mode": "auto",
                "reason": f"需要 {expert.name} 的專業處理",
                "priority": "high",
                "confidence": expert.performance_metrics.get("success_rate", 0.8)
            })
        
        # 基於專業領域推薦工具
        for specialization in expert.specializations:
            if specialization == "testing":
                suggestions.append({
                    "tool_name": "test_flow_mcp",
                    "reason": "需要測試相關功能",
                    "priority": "medium"
                })
            elif specialization in ["monitoring", "system"]:
                suggestions.append({
                    "tool_name": "system_monitor_adapter_mcp",
                    "reason": "需要系統監控功能",
                    "priority": "medium"
                })
        
        return suggestions
    
    async def _calculate_expert_confidence(self, expert: ExpertProfile, request: UserRequest) -> float:
        """計算專家信心度"""
        confidence = expert.performance_metrics.get("success_rate", 0.8)
        
        # 基於能力匹配調整信心度
        matching_capabilities = 0
        for capability in expert.capabilities:
            if any(keyword in request.content.lower() for keyword in capability.keywords):
                matching_capabilities += 1
                confidence += capability.confidence * 0.1
        
        # 基於知識庫豐富度調整
        knowledge_richness = len(expert.knowledge_base.get("content", []))
        confidence += min(0.1, knowledge_richness * 0.02)
        
        return min(0.95, confidence)
    
    async def _intelligent_tool_selection(self, tool_suggestions: List[Dict], request: UserRequest) -> List[Dict]:
        """智能工具選擇"""
        if not tool_suggestions:
            return []
        
        # 按優先級和信心度排序
        def tool_score(suggestion):
            priority_score = {"high": 3, "medium": 2, "low": 1}.get(suggestion.get("priority", "medium"), 2)
            confidence_score = suggestion.get("confidence", 0.8)
            return priority_score + confidence_score
        
        sorted_suggestions = sorted(tool_suggestions, key=tool_score, reverse=True)
        
        # 去重（相同工具只選一個）
        selected_tools = []
        used_tools = set()
        
        for suggestion in sorted_suggestions:
            tool_name = suggestion["tool_name"]
            if tool_name not in used_tools:
                selected_tools.append(suggestion)
                used_tools.add(tool_name)
        
        return selected_tools[:3]  # 最多選擇3個工具
    
    async def _execute_tool(self, tool_suggestion: Dict, request: UserRequest) -> Dict:
        """執行工具"""
        tool_name = tool_suggestion["tool_name"]
        
        try:
            if tool_name == "general_processor_mcp":
                mode = tool_suggestion.get("mode", "auto")
                result = await self.general_processor.process(request.content, mode=mode)
                return {
                    "tool_name": tool_name,
                    "success": True,
                    "result": result,
                    "mode": mode
                }
            else:
                # 其他工具通過action_executor執行
                result = await self.action_executor.execute_action({
                    "tool_name": tool_name,
                    "parameters": {"content": request.content}
                })
                return {
                    "tool_name": tool_name,
                    "success": True,
                    "result": result
                }
                
        except Exception as e:
            return {
                "tool_name": tool_name,
                "success": False,
                "error": str(e),
                "result": None
            }
    
    async def _generate_comprehensive_analysis(self, expert_responses: List[ExpertResponse], 
                                             tool_results: List[Dict], 
                                             request: UserRequest) -> str:
        """生成綜合分析"""
        analysis = f"基於 {len(expert_responses)} 位專家的分析和 {len(tool_results)} 個工具的執行結果：\n\n"
        
        # 專家分析摘要
        analysis += "## 專家分析摘要\n"
        for response in expert_responses:
            analysis += f"**{response.expert_name}** (信心度: {response.confidence:.2f}):\n"
            analysis += f"{response.analysis[:200]}...\n\n"
        
        # 工具執行摘要
        if tool_results:
            analysis += "## 工具執行結果\n"
            for result in tool_results:
                status = "✅ 成功" if result.get("success", False) else "❌ 失敗"
                analysis += f"- {result['tool_name']}: {status}\n"
        
        return analysis
    
    async def _calculate_overall_confidence(self, expert_responses: List[ExpertResponse], 
                                          tool_results: List[Dict], 
                                          stage_results: Dict) -> float:
        """計算整體信心度"""
        if not expert_responses:
            return 0.0
        
        # 專家信心度平均值
        expert_confidence = sum(r.confidence for r in expert_responses) / len(expert_responses)
        
        # 工具成功率
        tool_success_rate = 0.0
        if tool_results:
            successful_tools = len([r for r in tool_results if r.get("success", False)])
            tool_success_rate = successful_tools / len(tool_results)
        
        # 階段完成度
        stage_completion = len(stage_results) / 5.0  # 5個階段
        
        # 綜合計算
        overall_confidence = (
            expert_confidence * 0.6 +
            tool_success_rate * 0.3 +
            stage_completion * 0.1
        )
        
        return min(0.95, overall_confidence)
    
    async def _generate_final_answer(self, comprehensive_analysis: str, 
                                   expert_responses: List[ExpertResponse], 
                                   tool_results: List[Dict]) -> str:
        """生成最終答案"""
        answer = "## 綜合解決方案\n\n"
        answer += comprehensive_analysis + "\n"
        
        # 整合專家建議
        all_recommendations = []
        for response in expert_responses:
            all_recommendations.extend(response.recommendations)
        
        if all_recommendations:
            answer += "## 專家建議\n"
            for i, rec in enumerate(all_recommendations[:5], 1):  # 最多5個建議
                answer += f"{i}. {rec}\n"
        
        # 添加工具執行結果
        successful_tools = [r for r in tool_results if r.get("success", False)]
        if successful_tools:
            answer += "\n## 執行結果\n"
            for result in successful_tools:
                if result.get("result"):
                    answer += f"- {result['tool_name']}: 執行成功\n"
        
        answer += "\n## 總結\n"
        answer += f"基於 {len(expert_responses)} 位專家的專業分析，我們為您提供了上述綜合解決方案。"
        
        return answer
    
    # 統計和監控方法
    async def _update_stage_stats(self, stage: ProcessingStage, execution_time: float):
        """更新階段統計"""
        stats = self.stage_statistics[stage.value]
        stats["count"] += 1
        stats["total_time"] += execution_time
        stats["average_time"] = stats["total_time"] / stats["count"]
    
    async def _update_expert_usage_stats(self, expert_id: str):
        """更新專家使用統計"""
        if expert_id not in self.expert_usage_stats:
            self.expert_usage_stats[expert_id] = {"usage_count": 0, "last_used": datetime.now()}
        
        self.expert_usage_stats[expert_id]["usage_count"] += 1
        self.expert_usage_stats[expert_id]["last_used"] = datetime.now()
    
    async def _update_execution_stats(self, result: ProcessingResult, stage_results: Dict):
        """更新執行統計"""
        self.performance_metrics["total_requests"] += 1
        
        if result.success:
            self.performance_metrics["successful_requests"] += 1
        
        # 更新平均響應時間
        current_avg = self.performance_metrics["average_response_time"]
        total_requests = self.performance_metrics["total_requests"]
        self.performance_metrics["average_response_time"] = (
            (current_avg * (total_requests - 1) + result.execution_time) / total_requests
        )
        
        # 更新專家命中率
        expert_count = len(result.expert_analysis)
        if expert_count > 0:
            successful_experts = len([e for e in result.expert_analysis if e.confidence > 0.5])
            expert_hit_rate = successful_experts / expert_count
            current_hit_rate = self.performance_metrics["expert_hit_rate"]
            self.performance_metrics["expert_hit_rate"] = (
                (current_hit_rate * (total_requests - 1) + expert_hit_rate) / total_requests
            )
    
    async def get_system_statistics(self) -> Dict[str, Any]:
        """獲取系統統計信息"""
        expert_stats = await self.dynamic_expert_registry.get_expert_statistics()
        
        return {
            "performance_metrics": self.performance_metrics,
            "stage_statistics": self.stage_statistics,
            "expert_usage_stats": self.expert_usage_stats,
            "expert_registry_stats": expert_stats,
            "system_health": {
                "total_experts": expert_stats["total_experts"],
                "active_experts": expert_stats["by_status"].get("active", 0),
                "success_rate": self.performance_metrics["successful_requests"] / max(1, self.performance_metrics["total_requests"]),
                "average_response_time": self.performance_metrics["average_response_time"]
            }
        }

# 工廠函數
def create_aicore3() -> AICore3:
    """創建AICore 3.0實例"""
    return AICore3()

# 使用示例
async def main():
    """使用示例"""
    # 創建AICore 3.0
    aicore = create_aicore3()
    await aicore.initialize()
    
    # 創建測試請求
    request = UserRequest(
        id="test_001",
        content="我需要為我的Python Web應用實現自動化測試，包括單元測試和集成測試",
        context={
            "technology": "python",
            "framework": "flask",
            "urgency": "high"
        }
    )
    
    # 處理請求
    result = await aicore.process_request(request)
    
    # 輸出結果
    print(f"處理結果: {result.success}")
    print(f"執行時間: {result.execution_time:.2f}s")
    print(f"信心度: {result.confidence:.2f}")
    print(f"專家數量: {len(result.expert_analysis)}")
    print(f"最終答案: {result.final_answer[:200]}...")
    
    # 獲取系統統計
    stats = await aicore.get_system_statistics()
    print(f"系統統計: {stats['system_health']}")

if __name__ == "__main__":
    asyncio.run(main())


    # Smartinvention Adapter API端點處理方法
    async def handle_smartinvention_request(self, endpoint: str, request_data: Dict) -> Dict:
        """處理Smartinvention相關請求 - 接手原EC2端口"""
        try:
            if self.smartinvention_adapter is None:
                return {
                    "success": False,
                    "error": "Smartinvention Adapter未初始化",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 根據端點路由到對應的處理方法
            if endpoint == "/api/sync/conversations":
                return await self.smartinvention_adapter.process_conversation_sync(request_data)
            
            elif endpoint == "/api/conversations/latest":
                return await self.smartinvention_adapter.get_latest_conversations(request_data)
            
            elif endpoint == "/api/interventions/needed":
                return await self.smartinvention_adapter.get_interventions_needed(request_data)
            
            elif endpoint == "/api/health":
                return await self.smartinvention_adapter.health_check()
            
            elif endpoint == "/api/statistics":
                return await self.smartinvention_adapter.get_statistics()
            
            elif endpoint == "/api/local-models/connect":
                return await self.smartinvention_adapter.connect_local_model(request_data)
            
            elif endpoint == "/api/local-models/query":
                return await self.smartinvention_adapter.query_local_model(request_data)
            
            elif endpoint == "/api/local-models/status":
                return await self.smartinvention_adapter.get_model_status(request_data)
            
            elif endpoint == "/api/sync/start":
                return await self.smartinvention_adapter.start_sync(request_data)
            
            elif endpoint == "/api/sync/status":
                return await self.smartinvention_adapter.get_sync_status(request_data)
            
            else:
                return {
                    "success": False,
                    "error": f"未知的Smartinvention端點: {endpoint}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"處理Smartinvention請求失敗 {endpoint}: {e}")
            return {
                "success": False,
                "error": str(e),
                "endpoint": endpoint,
                "timestamp": datetime.now().isoformat()
            }
    
    async def handle_unified_request(self, endpoint: str, request_data: Dict) -> Dict:
        """統一請求處理 - 整合AICore和Smartinvention端點"""
        from config.endpoint_mapping import is_smartinvention_endpoint, is_aicore_endpoint
        
        try:
            if is_smartinvention_endpoint(endpoint):
                # 處理Smartinvention相關請求
                return await self.handle_smartinvention_request(endpoint, request_data)
            
            elif is_aicore_endpoint(endpoint):
                # 處理AICore核心請求
                return await self.handle_aicore_request(endpoint, request_data)
            
            else:
                return {
                    "success": False,
                    "error": f"未知端點: {endpoint}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"統一請求處理失敗 {endpoint}: {e}")
            return {
                "success": False,
                "error": str(e),
                "endpoint": endpoint,
                "timestamp": datetime.now().isoformat()
            }
    
    async def handle_aicore_request(self, endpoint: str, request_data: Dict) -> Dict:
        """處理AICore核心請求"""
        try:
            if endpoint == "/api/aicore/process":
                # 處理核心請求
                user_request = UserRequest(
                    id=request_data.get("id", f"req_{int(time.time())}"),
                    content=request_data.get("content", ""),
                    context=request_data.get("context", {}),
                    priority=request_data.get("priority", "normal")
                )
                result = await self.process_request(user_request)
                return {
                    "success": result.success,
                    "result": asdict(result),
                    "timestamp": datetime.now().isoformat()
                }
            
            elif endpoint == "/api/aicore/status":
                return await self.get_system_status()
            
            elif endpoint == "/api/aicore/experts":
                experts = await self.dynamic_expert_registry.get_all_experts()
                return {
                    "success": True,
                    "experts": [asdict(expert) for expert in experts],
                    "count": len(experts),
                    "timestamp": datetime.now().isoformat()
                }
            
            elif endpoint == "/api/aicore/tools":
                tools = await self.tool_registry.get_all_tools()
                return {
                    "success": True,
                    "tools": [asdict(tool) for tool in tools],
                    "count": len(tools),
                    "timestamp": datetime.now().isoformat()
                }
            
            else:
                return {
                    "success": False,
                    "error": f"未知的AICore端點: {endpoint}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"處理AICore請求失敗 {endpoint}: {e}")
            return {
                "success": False,
                "error": str(e),
                "endpoint": endpoint,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_system_status(self) -> Dict:
        """獲取系統整體狀態"""
        try:
            # 獲取各組件狀態
            smartinvention_health = await self.smartinvention_adapter.health_check() if self.smartinvention_adapter else {"healthy": False}
            
            # 獲取專家和工具統計
            experts = await self.dynamic_expert_registry.get_all_experts()
            tools = await self.tool_registry.get_all_tools()
            
            return {
                "success": True,
                "system_status": {
                    "aicore_version": "3.0.0",
                    "components": {
                        "dynamic_expert_registry": True,
                        "tool_registry": True,
                        "smartinvention_adapter": smartinvention_health.get("healthy", False),
                        "general_processor": True,
                        "expert_aggregator": True
                    },
                    "statistics": {
                        "total_experts": len(experts),
                        "total_tools": len(tools),
                        "total_requests": self.performance_metrics["total_requests"],
                        "successful_requests": self.performance_metrics["successful_requests"],
                        "average_response_time": self.performance_metrics["average_response_time"]
                    },
                    "smartinvention_status": smartinvention_health
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"獲取系統狀態失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# 創建AICore 3.0實例的工廠函數
def create_aicore3() -> AICore3:
    """創建AICore 3.0實例"""
    return AICore3()

# 導出主要類和函數
__all__ = [
    "AICore3",
    "UserRequest", 
    "ExpertResponse",
    "ProcessingResult",
    "ProcessingStage",
    "create_aicore3"
]

