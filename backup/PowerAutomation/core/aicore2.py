"""
AICore 2.0 - 六階段處理流程與專家系統整合
Enhanced AICore with Six-Stage Processing and Expert System Integration
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
from tools.tool_registry import ToolRegistry
from actions.action_executor import ActionExecutor

logger = logging.getLogger(__name__)

class ExpertType(Enum):
    """領域專家類型"""
    TECHNICAL_EXPERT = "technical_expert"
    BUSINESS_EXPERT = "business_expert"
    DATA_EXPERT = "data_expert"
    INTEGRATION_EXPERT = "integration_expert"
    API_EXPERT = "api_expert"
    SECURITY_EXPERT = "security_expert"
    PERFORMANCE_EXPERT = "performance_expert"

class ProcessingStage(Enum):
    """處理階段"""
    BACKGROUND_SEARCH = "background_search"
    EXPERT_IDENTIFICATION = "expert_identification"
    EXPERT_RESPONSE_GENERATION = "expert_response_generation"
    EXPERT_AGGREGATION = "expert_aggregation"
    INTELLIGENT_TOOL_EXECUTION = "intelligent_tool_execution"
    FINAL_RESULT_GENERATION = "final_result_generation"

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
    expert_type: ExpertType
    analysis: str
    recommendations: List[str]
    tool_suggestions: List[Dict[str, Any]]
    confidence: float
    next_action: str = None
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

class MCPClient:
    """MCP客戶端，負責與各種MCP服務通信"""
    
    def __init__(self):
        self.service_endpoints = {
            'cloud_search': 'http://localhost:8080/search',
            'expert_identification': 'http://localhost:8081/identify',
            'expert_generation': 'http://localhost:8082/generate',
            'aggregation': 'http://localhost:8083/aggregate'
        }
        self.mock_mode = True  # 開發階段使用模擬模式
    
    async def search_background_info(self, params: Dict) -> Dict:
        """搜索背景信息"""
        if self.mock_mode:
            return {
                "results": [
                    f"相關搜索結果1: {params.get('query', '')}",
                    f"相關搜索結果2: {params.get('query', '')}"
                ],
                "documents": ["文檔1", "文檔2"],
                "context": {"enriched": True, "relevance_score": 0.85}
            }
        # 實際MCP調用邏輯
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(self.service_endpoints['cloud_search'], json=params) as response:
        #         return await response.json()
    
    async def identify_experts(self, params: Dict) -> Dict:
        """識別相關專家"""
        content = params.get("request_content", "")
        context = params.get("context", {})
        
        # 智能專家識別邏輯
        experts = []
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in ["api", "接口", "interface"]):
            experts.append("api_expert")
        if any(keyword in content_lower for keyword in ["集成", "整合", "integration"]):
            experts.append("integration_expert")
        if any(keyword in content_lower for keyword in ["技術", "代碼", "technical", "code"]):
            experts.append("technical_expert")
        if any(keyword in content_lower for keyword in ["業務", "需求", "business", "requirement"]):
            experts.append("business_expert")
        if any(keyword in content_lower for keyword in ["數據", "分析", "data", "analysis"]):
            experts.append("data_expert")
        if any(keyword in content_lower for keyword in ["安全", "security"]):
            experts.append("security_expert")
        if any(keyword in content_lower for keyword in ["性能", "優化", "performance"]):
            experts.append("performance_expert")
        
        return {
            "recommended_experts": experts or ["technical_expert"],
            "confidence": 0.9,
            "reasoning": f"基於內容分析識別出 {len(experts)} 位相關專家"
        }
    
    async def generate_expert_response(self, params: Dict) -> Dict:
        """生成專家回答"""
        expert_type = params.get("expert_type")
        content = params.get("request_content")
        context = params.get("context", {})
        
        # 模擬不同專家的回答
        expert_responses = {
            "technical_expert": {
                "analysis": f"作為技術專家，我分析了請求：{content[:100]}...\n\n從技術角度來看，這個問題涉及系統架構、代碼實現和技術選型。建議採用模塊化設計，確保代碼的可維護性和擴展性。",
                "recommendations": [
                    "採用微服務架構提高系統可擴展性",
                    "實施代碼審查和自動化測試",
                    "使用容器化技術簡化部署",
                    "建立監控和日誌系統"
                ],
                "tool_suggestions": [
                    {"tool_name": "general_processor_mcp", "mode": "text", "reason": "需要技術文檔分析", "priority": "high"},
                    {"tool_name": "test_flow_mcp", "reason": "需要技術測試驗證", "priority": "medium"}
                ],
                "confidence": 0.92
            },
            "api_expert": {
                "analysis": f"作為API專家，我建議：{content[:100]}...\n\nAPI設計需要考慮RESTful原則、版本控制、安全性和性能優化。建議使用標準的HTTP狀態碼和錯誤處理機制。",
                "recommendations": [
                    "遵循RESTful API設計原則",
                    "實施API版本控制策略",
                    "添加API認證和授權機制",
                    "實現API限流和監控"
                ],
                "tool_suggestions": [
                    {"tool_name": "general_processor_mcp", "mode": "json", "reason": "需要API數據處理", "priority": "high"},
                    {"tool_name": "test_flow_mcp", "reason": "需要API測試", "priority": "high"}
                ],
                "confidence": 0.88
            },
            "business_expert": {
                "analysis": f"從業務角度分析：{content[:100]}...\n\n需要考慮業務需求、用戶體驗和商業價值。建議進行需求分析和用戶調研，確保解決方案符合業務目標。",
                "recommendations": [
                    "進行詳細的需求分析",
                    "考慮用戶體驗和界面設計",
                    "評估商業價值和投資回報",
                    "制定項目時間線和里程碑"
                ],
                "tool_suggestions": [
                    {"tool_name": "general_processor_mcp", "mode": "general", "reason": "需要業務分析處理", "priority": "medium"}
                ],
                "confidence": 0.85
            },
            "data_expert": {
                "analysis": f"數據專家分析：{content[:100]}...\n\n數據處理需要考慮數據質量、存儲效率和分析性能。建議建立數據治理框架和數據質量監控機制。",
                "recommendations": [
                    "建立數據質量監控體系",
                    "實施數據備份和恢復策略",
                    "優化數據存儲和查詢性能",
                    "確保數據安全和隱私保護"
                ],
                "tool_suggestions": [
                    {"tool_name": "general_processor_mcp", "mode": "json", "reason": "需要數據結構分析", "priority": "high"},
                    {"tool_name": "file_processor_adapter_mcp", "reason": "需要數據文件處理", "priority": "medium"}
                ],
                "confidence": 0.90
            },
            "integration_expert": {
                "analysis": f"集成專家建議：{content[:100]}...\n\n系統集成需要考慮接口標準化、數據一致性和錯誤處理。建議採用事件驅動架構和異步處理機制。",
                "recommendations": [
                    "標準化系統間接口協議",
                    "實施數據一致性檢查",
                    "建立錯誤處理和重試機制",
                    "使用消息隊列處理異步任務"
                ],
                "tool_suggestions": [
                    {"tool_name": "general_processor_mcp", "mode": "auto", "reason": "需要集成數據處理", "priority": "high"},
                    {"tool_name": "test_flow_mcp", "reason": "需要集成測試", "priority": "high"}
                ],
                "confidence": 0.87
            }
        }
        
        default_response = {
            "analysis": f"作為{expert_type}專家的分析...",
            "recommendations": ["通用建議1", "通用建議2"],
            "tool_suggestions": [
                {"tool_name": "general_processor_mcp", "mode": "auto", "reason": "通用處理需求", "priority": "medium"}
            ],
            "confidence": 0.8
        }
        
        return expert_responses.get(expert_type, default_response)
    
    async def aggregate_responses(self, params: Dict) -> Dict:
        """聚合專家回答"""
        expert_responses = params.get("expert_responses", [])
        
        if not expert_responses:
            return {
                "aggregated_analysis": "無專家回答可聚合",
                "consensus_recommendations": [],
                "confidence_score": 0.0
            }
        
        # 聚合分析
        all_analyses = [resp.get("analysis", "") for resp in expert_responses]
        all_recommendations = []
        confidence_scores = []
        
        for resp in expert_responses:
            all_recommendations.extend(resp.get("recommendations", []))
            confidence_scores.append(resp.get("confidence", 0.8))
        
        # 去重建議
        unique_recommendations = list(dict.fromkeys(all_recommendations))
        
        # 計算平均信心度
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return {
            "aggregated_analysis": f"綜合 {len(expert_responses)} 位專家的分析結果",
            "consensus_recommendations": unique_recommendations[:10],  # 取前10個建議
            "confidence_score": round(avg_confidence, 2),
            "expert_count": len(expert_responses),
            "recommendation_count": len(unique_recommendations)
        }

class AICore2:
    """
    AICore 2.0 - 六階段處理流程與專家系統整合
    
    六個處理階段：
    1. 搜索背景信息
    2. 識別領域專家
    3. 生成專家回答 (並行)
    4. 聚合專家建議
    5. 智能工具選擇和執行
    6. 生成最終結果
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # 初始化組件
        self.mcp_client = MCPClient()
        self.general_processor = create_general_processor_mcp()
        self.tool_registry = ToolRegistry()
        self.action_executor = ActionExecutor()
        
        # 執行統計
        self.execution_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_execution_time': 0.0,
            'stage_performance': {stage.value: {'count': 0, 'avg_time': 0.0} for stage in ProcessingStage},
            'expert_usage_stats': {expert.value: 0 for expert in ExpertType},
            'tool_usage_stats': {},
            'confidence_distribution': {'high': 0, 'medium': 0, 'low': 0}
        }
        
        logger.info("AICore 2.0 初始化完成 - 六階段處理流程已就緒")
    
    async def initialize(self):
        """初始化AICore系統"""
        logger.info("🚀 初始化AICore 2.0系統...")
        
        # 初始化Tool Registry
        await self.tool_registry.initialize()
        
        # Action Executor不需要初始化方法，直接跳過
        logger.info("✅ Action Executor 已就緒")
        
        logger.info("✅ AICore 2.0系統初始化完成")
    
    async def process_request(self, request: UserRequest) -> ProcessingResult:
        """
        處理用戶請求的主要入口點
        實現六階段處理流程
        """
        start_time = time.time()
        stage_results = {}
        
        logger.info(f"🚀 AICore 2.0 開始處理請求: {request.id}")
        
        try:
            # 階段1: 搜索背景信息
            stage_results['background_search'] = await self._stage1_search_background_info(request)
            
            # 階段2: 識別領域專家
            stage_results['expert_identification'] = await self._stage2_identify_expert_domains(
                request, stage_results['background_search']
            )
            
            # 階段3: 生成專家回答 (並行)
            stage_results['expert_response_generation'] = await self._stage3_generate_expert_responses(
                request, stage_results['expert_identification']['experts']
            )
            
            # 階段4: 聚合專家建議
            stage_results['expert_aggregation'] = await self._stage4_aggregate_expert_analysis(
                stage_results['expert_response_generation']['expert_responses']
            )
            
            # 階段5: 智能工具選擇和執行
            stage_results['intelligent_tool_execution'] = await self._stage5_execute_intelligent_tools(
                request, stage_results['expert_response_generation']['expert_responses']
            )
            
            # 階段6: 生成最終結果
            final_result = await self._stage6_generate_final_result(
                request, stage_results, start_time
            )
            
            # 更新統計
            self._update_execution_stats(final_result, stage_results)
            
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
    
    async def _stage1_search_background_info(self, request: UserRequest) -> Dict[str, Any]:
        """階段1: 搜索背景信息"""
        stage_start = time.time()
        logger.info(f"🔍 階段1: 搜索背景信息 - {request.id}")
        
        search_params = {
            "query": request.content,
            "context": request.context,
            "max_results": 10,
            "include_context": True
        }
        
        search_result = await self.mcp_client.search_background_info(search_params)
        
        stage_time = time.time() - stage_start
        self._update_stage_stats(ProcessingStage.BACKGROUND_SEARCH, stage_time)
        
        return {
            "search_results": search_result.get("results", []),
            "relevant_documents": search_result.get("documents", []),
            "context_enrichment": search_result.get("context", {}),
            "stage_execution_time": stage_time,
            "relevance_score": search_result.get("context", {}).get("relevance_score", 0.0)
        }
    
    async def _stage2_identify_expert_domains(self, request: UserRequest, background_info: Dict) -> Dict[str, Any]:
        """階段2: 識別領域專家"""
        stage_start = time.time()
        logger.info(f"🎯 階段2: 識別領域專家 - {request.id}")
        
        identification_params = {
            "request_content": request.content,
            "context": request.context,
            "background_info": background_info
        }
        
        expert_identification = await self.mcp_client.identify_experts(identification_params)
        
        # 解析專家類型
        expert_types = []
        for expert_name in expert_identification.get("recommended_experts", []):
            try:
                expert_type = ExpertType(expert_name)
                expert_types.append(expert_type)
            except ValueError:
                logger.warning(f"未知專家類型: {expert_name}")
        
        # 確保至少有一個專家
        if not expert_types:
            expert_types = [ExpertType.TECHNICAL_EXPERT]
        
        stage_time = time.time() - stage_start
        self._update_stage_stats(ProcessingStage.EXPERT_IDENTIFICATION, stage_time)
        
        logger.info(f"📋 識別到專家: {[e.value for e in expert_types]}")
        
        return {
            "experts": expert_types,
            "identification_confidence": expert_identification.get("confidence", 0.8),
            "reasoning": expert_identification.get("reasoning", ""),
            "stage_execution_time": stage_time,
            "expert_count": len(expert_types)
        }
    
    async def _stage3_generate_expert_responses(self, request: UserRequest, experts: List[ExpertType]) -> Dict[str, Any]:
        """階段3: 生成專家回答 (並行)"""
        stage_start = time.time()
        logger.info(f"🎭 階段3: 生成專家回答 - {request.id}")
        
        # 並行調用多個專家
        expert_tasks = []
        for expert_type in experts:
            task = self._call_domain_expert(expert_type, request)
            expert_tasks.append(task)
        
        expert_responses = await asyncio.gather(*expert_tasks, return_exceptions=True)
        
        # 處理異常結果
        valid_responses = []
        for i, response in enumerate(expert_responses):
            if isinstance(response, Exception):
                logger.error(f"專家 {experts[i].value} 調用失敗: {response}")
            else:
                valid_responses.append(response)
        
        stage_time = time.time() - stage_start
        self._update_stage_stats(ProcessingStage.EXPERT_RESPONSE_GENERATION, stage_time)
        
        logger.info(f"✅ 獲得 {len(valid_responses)} 個有效專家回答")
        
        return {
            "expert_responses": valid_responses,
            "total_experts_called": len(experts),
            "successful_responses": len(valid_responses),
            "stage_execution_time": stage_time,
            "parallel_efficiency": len(valid_responses) / len(experts) if experts else 0.0
        }
    
    async def _call_domain_expert(self, expert_type: ExpertType, request: UserRequest) -> ExpertResponse:
        """調用特定領域專家"""
        expert_start = time.time()
        logger.info(f"👨‍💼 調用 {expert_type.value} 專家")
        
        expert_params = {
            "expert_type": expert_type.value,
            "request_content": request.content,
            "context": request.context
        }
        
        expert_result = await self.mcp_client.generate_expert_response(expert_params)
        
        processing_time = time.time() - expert_start
        
        # 更新專家使用統計
        self.execution_stats['expert_usage_stats'][expert_type.value] += 1
        
        return ExpertResponse(
            expert_type=expert_type,
            analysis=expert_result.get("analysis", ""),
            recommendations=expert_result.get("recommendations", []),
            tool_suggestions=expert_result.get("tool_suggestions", []),
            confidence=expert_result.get("confidence", 0.8),
            next_action=expert_result.get("next_action"),
            processing_time=processing_time,
            metadata={
                "expert_call_time": processing_time,
                "recommendation_count": len(expert_result.get("recommendations", [])),
                "tool_suggestion_count": len(expert_result.get("tool_suggestions", []))
            }
        )
    
    async def _stage4_aggregate_expert_analysis(self, expert_responses: List[ExpertResponse]) -> Dict[str, Any]:
        """階段4: 聚合專家建議"""
        stage_start = time.time()
        logger.info(f"🔄 階段4: 聚合專家建議")
        
        if not expert_responses:
            return {
                "aggregated_analysis": "無專家回答可聚合",
                "consensus_recommendations": [],
                "confidence_score": 0.0,
                "stage_execution_time": 0.0
            }
        
        # 準備聚合參數
        aggregation_params = {
            "expert_responses": [
                {
                    "expert_type": resp.expert_type.value,
                    "analysis": resp.analysis,
                    "recommendations": resp.recommendations,
                    "confidence": resp.confidence
                }
                for resp in expert_responses
            ]
        }
        
        aggregation_result = await self.mcp_client.aggregate_responses(aggregation_params)
        
        stage_time = time.time() - stage_start
        self._update_stage_stats(ProcessingStage.EXPERT_AGGREGATION, stage_time)
        
        return {
            **aggregation_result,
            "stage_execution_time": stage_time,
            "expert_response_count": len(expert_responses)
        }
    
    async def _stage5_execute_intelligent_tools(self, request: UserRequest, expert_responses: List[ExpertResponse]) -> Dict[str, Any]:
        """階段5: 智能工具選擇和執行"""
        stage_start = time.time()
        logger.info(f"🛠️ 階段5: 智能工具選擇和執行")
        
        # 從專家建議中提取工具建議
        tool_suggestions = []
        for expert_response in expert_responses:
            tool_suggestions.extend(expert_response.tool_suggestions)
        
        # 智能工具選擇
        selected_tools = await self._intelligent_tool_selection(request, tool_suggestions)
        
        # 並行執行工具
        execution_results = []
        for tool_config in selected_tools:
            try:
                if tool_config.get("tool_name") == "general_processor_mcp":
                    # 調用General_Processor MCP
                    result = await self._execute_general_processor(request, tool_config, expert_responses)
                    execution_results.append(result)
                else:
                    # 調用其他工具
                    result = await self._execute_other_tool(tool_config, request)
                    execution_results.append(result)
                    
                # 更新工具使用統計
                tool_name = tool_config.get("tool_name", "unknown")
                self.execution_stats['tool_usage_stats'][tool_name] = (
                    self.execution_stats['tool_usage_stats'].get(tool_name, 0) + 1
                )
                
            except Exception as e:
                logger.error(f"工具執行失敗: {tool_config.get('tool_name')}, 錯誤: {e}")
                execution_results.append({
                    "tool_name": tool_config.get("tool_name"),
                    "success": False,
                    "error": str(e),
                    "execution_time": 0.0
                })
        
        stage_time = time.time() - stage_start
        self._update_stage_stats(ProcessingStage.INTELLIGENT_TOOL_EXECUTION, stage_time)
        
        return {
            "tool_execution_results": execution_results,
            "tools_selected": len(selected_tools),
            "successful_executions": len([r for r in execution_results if r.get("success", False)]),
            "stage_execution_time": stage_time,
            "execution_efficiency": len([r for r in execution_results if r.get("success", False)]) / len(selected_tools) if selected_tools else 0.0
        }
    
    async def _intelligent_tool_selection(self, request: UserRequest, tool_suggestions: List[Dict]) -> List[Dict[str, Any]]:
        """智能工具選擇邏輯"""
        selected_tools = []
        tool_priorities = {}
        
        # 分析工具建議
        for suggestion in tool_suggestions:
            tool_name = suggestion.get("tool_name", "general_processor_mcp")
            reason = suggestion.get("reason", "")
            priority = suggestion.get("priority", "medium")
            mode = suggestion.get("mode", "auto")
            
            # 累積工具優先級
            if tool_name not in tool_priorities:
                tool_priorities[tool_name] = {"count": 0, "priority_sum": 0, "modes": [], "reasons": []}
            
            tool_priorities[tool_name]["count"] += 1
            tool_priorities[tool_name]["priority_sum"] += {"high": 3, "medium": 2, "low": 1}.get(priority, 2)
            tool_priorities[tool_name]["modes"].append(mode)
            tool_priorities[tool_name]["reasons"].append(reason)
        
        # 選擇工具
        for tool_name, stats in tool_priorities.items():
            avg_priority = stats["priority_sum"] / stats["count"]
            most_common_mode = max(set(stats["modes"]), key=stats["modes"].count) if stats["modes"] else "auto"
            
            selected_tools.append({
                "tool_name": tool_name,
                "mode": most_common_mode,
                "priority": "high" if avg_priority >= 2.5 else "medium" if avg_priority >= 1.5 else "low",
                "suggestion_count": stats["count"],
                "reasons": stats["reasons"]
            })
        
        # 確保至少有General_Processor MCP
        if not any(tool["tool_name"] == "general_processor_mcp" for tool in selected_tools):
            selected_tools.append({
                "tool_name": "general_processor_mcp",
                "mode": "general",
                "priority": "high",
                "suggestion_count": 1,
                "reasons": ["默認通用處理"]
            })
        
        # 按優先級排序
        priority_order = {"high": 3, "medium": 2, "low": 1}
        selected_tools.sort(key=lambda x: priority_order.get(x["priority"], 0), reverse=True)
        
        logger.info(f"🎯 選擇工具: {[t['tool_name'] for t in selected_tools]}")
        return selected_tools
    
    async def _execute_general_processor(self, request: UserRequest, tool_config: Dict, expert_responses: List[ExpertResponse]) -> Dict[str, Any]:
        """執行General_Processor MCP"""
        logger.info(f"⚙️ 執行 General_Processor MCP")
        
        # 準備處理數據
        processing_data = {
            "content": request.content,
            "context": request.context,
            "expert_insights": [
                {
                    "expert_type": resp.expert_type.value,
                    "analysis": resp.analysis,
                    "recommendations": resp.recommendations,
                    "confidence": resp.confidence
                }
                for resp in expert_responses
            ],
            "metadata": {
                "request_id": request.id,
                "expert_count": len(expert_responses),
                "processing_timestamp": time.time()
            }
        }
        
        # 調用General_Processor MCP
        mode = tool_config.get("mode", "auto")
        options = {
            "priority": tool_config.get("priority", "medium"),
            "reasons": tool_config.get("reasons", [])
        }
        
        result = await self.general_processor.process(processing_data, mode, options)
        
        return {
            "tool_name": "general_processor_mcp",
            "mode_used": result.mode_used,
            "success": result.success,
            "output": result.data,
            "execution_time": result.execution_time,
            "metadata": result.metadata
        }
    
    async def _execute_other_tool(self, tool_config: Dict, request: UserRequest) -> Dict[str, Any]:
        """執行其他工具"""
        tool_name = tool_config.get("tool_name")
        logger.info(f"🔧 執行工具: {tool_name}")
        
        # 模擬工具執行
        execution_time = 0.5  # 模擬執行時間
        await asyncio.sleep(execution_time)
        
        return {
            "tool_name": tool_name,
            "success": True,
            "output": f"{tool_name} 成功處理了請求: {request.content[:50]}...",
            "execution_time": execution_time,
            "metadata": {
                "tool_config": tool_config,
                "request_id": request.id
            }
        }
    
    async def _stage6_generate_final_result(self, request: UserRequest, stage_results: Dict, start_time: float) -> ProcessingResult:
        """階段6: 生成最終結果"""
        stage_start = time.time()
        logger.info(f"📊 階段6: 生成最終結果")
        
        execution_time = time.time() - start_time
        
        # 提取專家回答
        expert_responses = stage_results.get('expert_response_generation', {}).get('expert_responses', [])
        
        # 提取工具執行結果
        tool_results = stage_results.get('intelligent_tool_execution', {}).get('tool_execution_results', [])
        
        # 聚合所有結果生成最終回答
        final_answer_parts = []
        
        # 添加背景信息摘要
        background_info = stage_results.get('background_search', {})
        if background_info.get('relevance_score', 0) > 0.7:
            final_answer_parts.append(f"**背景分析**: 基於相關度 {background_info.get('relevance_score', 0):.2f} 的背景信息分析")
        
        # 添加專家分析
        expert_aggregation = stage_results.get('expert_aggregation', {})
        if expert_aggregation.get('expert_count', 0) > 0:
            final_answer_parts.append(f"**專家分析**: 綜合了 {expert_aggregation.get('expert_count')} 位專家的專業意見")
            
            # 添加共識建議
            consensus_recommendations = expert_aggregation.get('consensus_recommendations', [])
            if consensus_recommendations:
                final_answer_parts.append(f"**專家建議**:\n" + "\n".join([f"• {rec}" for rec in consensus_recommendations[:5]]))
        
        # 添加工具執行結果
        successful_tools = [result for result in tool_results if result.get("success")]
        if successful_tools:
            final_answer_parts.append(f"**處理結果**: 成功執行了 {len(successful_tools)} 個處理工具")
            
            for tool_result in successful_tools[:3]:  # 只顯示前3個結果
                tool_name = tool_result.get("tool_name", "unknown")
                output = tool_result.get("output", "")
                if isinstance(output, dict):
                    summary = output.get("processing_result", {}).get("message", "處理完成")
                else:
                    summary = str(output)[:100] + "..." if len(str(output)) > 100 else str(output)
                final_answer_parts.append(f"**{tool_name}**: {summary}")
        
        # 生成最終回答
        final_answer = "\n\n".join(final_answer_parts) if final_answer_parts else "處理完成，但未生成具體結果。"
        
        # 計算總體信心度
        expert_confidence = expert_aggregation.get('confidence_score', 0.0)
        tool_success_rate = len(successful_tools) / len(tool_results) if tool_results else 1.0
        total_confidence = (expert_confidence * 0.7 + tool_success_rate * 0.3)
        
        stage_time = time.time() - stage_start
        self._update_stage_stats(ProcessingStage.FINAL_RESULT_GENERATION, stage_time)
        
        return ProcessingResult(
            request_id=request.id,
            success=True,
            stage_results=stage_results,
            expert_analysis=expert_responses,
            tool_execution_results=tool_results,
            final_answer=final_answer,
            confidence=round(total_confidence, 2),
            execution_time=execution_time,
            metadata={
                "processing_stages": len(stage_results),
                "experts_consulted": [resp.expert_type.value for resp in expert_responses],
                "tools_executed": [result["tool_name"] for result in tool_results],
                "stage_breakdown": {stage: result.get("stage_execution_time", 0.0) for stage, result in stage_results.items()},
                "quality_metrics": {
                    "expert_confidence": expert_confidence,
                    "tool_success_rate": tool_success_rate,
                    "overall_confidence": total_confidence
                }
            }
        )
    
    def _update_stage_stats(self, stage: ProcessingStage, execution_time: float):
        """更新階段統計"""
        stage_stats = self.execution_stats['stage_performance'][stage.value]
        stage_stats['count'] += 1
        
        # 更新平均時間
        current_avg = stage_stats['avg_time']
        count = stage_stats['count']
        stage_stats['avg_time'] = (current_avg * (count - 1) + execution_time) / count
    
    def _update_execution_stats(self, result: ProcessingResult, stage_results: Dict):
        """更新執行統計"""
        self.execution_stats['total_requests'] += 1
        
        if result.success:
            self.execution_stats['successful_requests'] += 1
        else:
            self.execution_stats['failed_requests'] += 1
        
        # 更新平均執行時間
        current_avg = self.execution_stats['average_execution_time']
        total_requests = self.execution_stats['total_requests']
        self.execution_stats['average_execution_time'] = (
            (current_avg * (total_requests - 1) + result.execution_time) / total_requests
        )
        
        # 更新信心度分布
        confidence = result.confidence
        if confidence >= 0.8:
            self.execution_stats['confidence_distribution']['high'] += 1
        elif confidence >= 0.6:
            self.execution_stats['confidence_distribution']['medium'] += 1
        else:
            self.execution_stats['confidence_distribution']['low'] += 1
    
    async def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        return {
            "system_info": {
                "name": "AICore 2.0",
                "version": "2.0.0",
                "description": "六階段處理流程與專家系統整合",
                "uptime": "running"
            },
            "execution_statistics": self.execution_stats,
            "component_status": {
                "general_processor_mcp": await self.general_processor.health_check(),
                "tool_registry": "healthy",
                "action_executor": "healthy",
                "mcp_client": "healthy"
            },
            "performance_metrics": {
                "success_rate": self.execution_stats['successful_requests'] / max(self.execution_stats['total_requests'], 1),
                "average_execution_time": self.execution_stats['average_execution_time'],
                "stage_performance": self.execution_stats['stage_performance']
            }
        }
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """獲取系統能力"""
        general_processor_capabilities = await self.general_processor.get_capabilities()
        
        return {
            "processing_stages": [stage.value for stage in ProcessingStage],
            "expert_types": [expert.value for expert in ExpertType],
            "core_capabilities": {
                "six_stage_processing": "六階段智能處理流程",
                "expert_system_integration": "多領域專家系統整合",
                "intelligent_tool_selection": "智能工具選擇和執行",
                "parallel_processing": "並行專家調用和工具執行",
                "adaptive_confidence": "自適應信心度評估"
            },
            "integrated_components": {
                "general_processor_mcp": general_processor_capabilities,
                "tool_registry": "工具註冊和發現系統",
                "action_executor": "動作執行引擎",
                "mcp_client": "MCP服務客戶端"
            }
        }

# 工廠函數
def create_aicore2(config: Dict[str, Any] = None) -> AICore2:
    """創建AICore 2.0實例"""
    return AICore2(config)

# 示例使用
async def example_usage():
    """示例用法"""
    # 創建AICore 2.0實例
    aicore = create_aicore2()
    await aicore.initialize()
    
    # 創建用戶請求
    request = UserRequest(
        id="req_001",
        content="我需要分析API接口的性能問題，並提供優化建議",
        context={
            "api_endpoint": "/api/users",
            "current_response_time": "2.5s",
            "expected_response_time": "500ms",
            "user_count": 1000
        }
    )
    
    print("🚀 開始處理用戶請求...")
    
    # 處理請求
    result = await aicore.process_request(request)
    
    # 輸出結果
    print(f"\n📊 處理結果:")
    print(f"成功: {result.success}")
    print(f"執行時間: {result.execution_time:.2f}s")
    print(f"信心度: {result.confidence:.2f}")
    print(f"專家數量: {len(result.expert_analysis)}")
    print(f"工具執行: {len(result.tool_execution_results)}")
    print(f"\n最終回答:\n{result.final_answer}")
    
    # 獲取系統狀態
    status = await aicore.get_system_status()
    print(f"\n📈 系統統計:")
    print(f"總請求數: {status['execution_statistics']['total_requests']}")
    print(f"成功率: {status['performance_metrics']['success_rate']:.2%}")

if __name__ == "__main__":
    asyncio.run(example_usage())

