"""
專家建議路由整合器
將專家建議轉換為智慧路由引擎的路由決策
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# 導入相關組件
from components.smart_routing_engine import SmartRoutingEngine, RoutingRequest, RoutingDecision, RequestPriority
from components.dynamic_expert_registry import DynamicExpertRegistry, ExpertProfile
from core.aicore3 import ExpertResponse

logger = logging.getLogger(__name__)

@dataclass
class ExpertToolRecommendation:
    """專家工具推薦"""
    expert_id: str                    # 專家ID
    tool_name: str                   # 工具名稱
    confidence: float                # 推薦信心度
    reasoning: str                   # 推薦理由
    priority: str                    # 優先級 (high/medium/low)
    parameters: Dict[str, Any]       # 建議參數
    context: Dict[str, Any]          # 上下文信息

@dataclass
class RoutingRecommendation:
    """路由推薦"""
    recommended_tools: List[str]     # 推薦工具列表
    routing_strategy: str            # 路由策略
    priority: RequestPriority        # 請求優先級
    confidence: float                # 整體信心度
    expert_consensus: float          # 專家共識度
    reasoning: List[str]             # 推薦理由列表

class ExpertRoutingIntegrator:
    """專家建議路由整合器"""
    
    def __init__(self, smart_routing_engine: SmartRoutingEngine, 
                 expert_registry: DynamicExpertRegistry):
        """初始化專家建議路由整合器"""
        self.smart_routing_engine = smart_routing_engine
        self.expert_registry = expert_registry
        
        # 配置參數
        self.min_confidence_threshold = 0.6
        self.consensus_threshold = 0.7
        self.max_tools_per_request = 3
        
        # 統計信息
        self.integration_stats = {
            'total_integrations': 0,
            'successful_integrations': 0,
            'expert_recommendations_processed': 0,
            'routing_decisions_made': 0,
            'average_consensus': 0.0
        }
        
        logger.info("✅ 專家建議路由整合器初始化完成")
    
    async def integrate_expert_recommendations(self, 
                                             expert_responses: List[ExpertResponse],
                                             request_context: Dict[str, Any]) -> RoutingRecommendation:
        """整合專家建議並生成路由推薦"""
        
        start_time = time.time()
        self.integration_stats['total_integrations'] += 1
        
        logger.info(f"🔗 開始整合專家建議，專家數量: {len(expert_responses)}")
        
        try:
            # 1. 提取專家工具推薦
            expert_tool_recommendations = await self._extract_expert_tool_recommendations(expert_responses)
            
            # 2. 分析專家共識
            consensus_analysis = await self._analyze_expert_consensus(expert_tool_recommendations)
            
            # 3. 生成路由推薦
            routing_recommendation = await self._generate_routing_recommendation(
                expert_tool_recommendations, consensus_analysis, request_context
            )
            
            # 4. 驗證路由推薦
            validated_recommendation = await self._validate_routing_recommendation(routing_recommendation)
            
            # 5. 更新統計
            self.integration_stats['successful_integrations'] += 1
            self.integration_stats['expert_recommendations_processed'] += len(expert_tool_recommendations)
            self.integration_stats['routing_decisions_made'] += 1
            
            processing_time = time.time() - start_time
            logger.info(f"✅ 專家建議整合完成: {processing_time:.2f}s, 推薦工具: {validated_recommendation.recommended_tools}")
            
            return validated_recommendation
            
        except Exception as e:
            logger.error(f"❌ 專家建議整合失敗: {e}")
            # 返回默認推薦
            return RoutingRecommendation(
                recommended_tools=[],
                routing_strategy="intelligent",
                priority=RequestPriority.NORMAL,
                confidence=0.0,
                expert_consensus=0.0,
                reasoning=[f"整合失敗: {str(e)}"]
            )
    
    async def _extract_expert_tool_recommendations(self, 
                                                 expert_responses: List[ExpertResponse]) -> List[ExpertToolRecommendation]:
        """提取專家工具推薦"""
        
        recommendations = []
        
        for expert_response in expert_responses:
            expert_id = expert_response.expert_id
            tool_suggestions = expert_response.tool_suggestions
            
            for tool_suggestion in tool_suggestions:
                tool_name = tool_suggestion.get('tool_name', '')
                confidence = tool_suggestion.get('confidence', 0.0)
                reasoning = tool_suggestion.get('reasoning', '')
                
                # 確定優先級
                priority = self._determine_tool_priority(confidence, tool_suggestion)
                
                recommendation = ExpertToolRecommendation(
                    expert_id=expert_id,
                    tool_name=tool_name,
                    confidence=confidence,
                    reasoning=reasoning,
                    priority=priority,
                    parameters=tool_suggestion.get('parameters', {}),
                    context=tool_suggestion.get('context', {})
                )
                
                recommendations.append(recommendation)
        
        logger.info(f"📋 提取專家工具推薦: {len(recommendations)} 個推薦")
        return recommendations
    
    def _determine_tool_priority(self, confidence: float, tool_suggestion: Dict[str, Any]) -> str:
        """確定工具優先級"""
        
        # 基於信心度
        if confidence >= 0.8:
            base_priority = "high"
        elif confidence >= 0.6:
            base_priority = "medium"
        else:
            base_priority = "low"
        
        # 基於工具類型調整
        tool_name = tool_suggestion.get('tool_name', '').lower()
        
        # 測試相關工具提高優先級
        if any(keyword in tool_name for keyword in ['test', 'testing', 'qa', 'quality']):
            if base_priority == "medium":
                base_priority = "high"
            elif base_priority == "low":
                base_priority = "medium"
        
        # 關鍵系統工具提高優先級
        if any(keyword in tool_name for keyword in ['critical', 'system', 'core']):
            base_priority = "high"
        
        return base_priority
    
    async def _analyze_expert_consensus(self, 
                                      recommendations: List[ExpertToolRecommendation]) -> Dict[str, Any]:
        """分析專家共識"""
        
        if not recommendations:
            return {"consensus_score": 0.0, "tool_consensus": {}, "priority_consensus": {}}
        
        # 統計工具推薦
        tool_votes = {}
        tool_confidences = {}
        priority_votes = {}
        
        for rec in recommendations:
            tool_name = rec.tool_name
            
            # 工具投票
            if tool_name not in tool_votes:
                tool_votes[tool_name] = 0
                tool_confidences[tool_name] = []
            
            tool_votes[tool_name] += 1
            tool_confidences[tool_name].append(rec.confidence)
            
            # 優先級投票
            if rec.priority not in priority_votes:
                priority_votes[rec.priority] = 0
            priority_votes[rec.priority] += 1
        
        # 計算工具共識
        total_recommendations = len(recommendations)
        tool_consensus = {}
        
        for tool_name, votes in tool_votes.items():
            consensus_score = votes / total_recommendations
            avg_confidence = sum(tool_confidences[tool_name]) / len(tool_confidences[tool_name])
            
            tool_consensus[tool_name] = {
                "votes": votes,
                "consensus_score": consensus_score,
                "average_confidence": avg_confidence,
                "weighted_score": consensus_score * avg_confidence
            }
        
        # 計算優先級共識
        priority_consensus = {}
        for priority, votes in priority_votes.items():
            priority_consensus[priority] = votes / total_recommendations
        
        # 計算整體共識分數
        if tool_consensus:
            max_consensus = max(tc["consensus_score"] for tc in tool_consensus.values())
            overall_consensus = max_consensus
        else:
            overall_consensus = 0.0
        
        logger.info(f"📊 專家共識分析: 整體共識={overall_consensus:.2f}, 工具數={len(tool_consensus)}")
        
        return {
            "consensus_score": overall_consensus,
            "tool_consensus": tool_consensus,
            "priority_consensus": priority_consensus
        }
    
    async def _generate_routing_recommendation(self, 
                                             recommendations: List[ExpertToolRecommendation],
                                             consensus_analysis: Dict[str, Any],
                                             request_context: Dict[str, Any]) -> RoutingRecommendation:
        """生成路由推薦"""
        
        tool_consensus = consensus_analysis.get("tool_consensus", {})
        priority_consensus = consensus_analysis.get("priority_consensus", {})
        overall_consensus = consensus_analysis.get("consensus_score", 0.0)
        
        # 選擇推薦工具
        recommended_tools = []
        reasoning = []
        
        # 按加權分數排序工具
        sorted_tools = sorted(
            tool_consensus.items(),
            key=lambda x: x[1]["weighted_score"],
            reverse=True
        )
        
        for tool_name, consensus_data in sorted_tools[:self.max_tools_per_request]:
            if consensus_data["average_confidence"] >= self.min_confidence_threshold:
                recommended_tools.append(tool_name)
                reasoning.append(
                    f"{tool_name}: {consensus_data['votes']}票, "
                    f"共識度={consensus_data['consensus_score']:.2f}, "
                    f"信心度={consensus_data['average_confidence']:.2f}"
                )
        
        # 確定路由策略
        routing_strategy = self._determine_routing_strategy(
            recommended_tools, consensus_analysis, request_context
        )
        
        # 確定請求優先級
        request_priority = self._determine_request_priority(priority_consensus, request_context)
        
        # 計算整體信心度
        if recommended_tools and tool_consensus:
            confidence = sum(
                tool_consensus[tool]["average_confidence"] 
                for tool in recommended_tools if tool in tool_consensus
            ) / len(recommended_tools)
        else:
            confidence = 0.0
        
        return RoutingRecommendation(
            recommended_tools=recommended_tools,
            routing_strategy=routing_strategy,
            priority=request_priority,
            confidence=confidence,
            expert_consensus=overall_consensus,
            reasoning=reasoning
        )
    
    def _determine_routing_strategy(self, 
                                  recommended_tools: List[str],
                                  consensus_analysis: Dict[str, Any],
                                  request_context: Dict[str, Any]) -> str:
        """確定路由策略"""
        
        # 基於工具數量
        if len(recommended_tools) == 1:
            return "direct"  # 直接路由
        elif len(recommended_tools) <= 2:
            return "intelligent"  # 智能路由
        else:
            return "load_balanced"  # 負載均衡
        
        # 基於共識度調整
        consensus_score = consensus_analysis.get("consensus_score", 0.0)
        if consensus_score >= 0.8:
            return "intelligent"  # 高共識使用智能路由
        elif consensus_score <= 0.4:
            return "round_robin"  # 低共識使用輪詢
        
        return "intelligent"
    
    def _determine_request_priority(self, 
                                  priority_consensus: Dict[str, float],
                                  request_context: Dict[str, Any]) -> RequestPriority:
        """確定請求優先級"""
        
        # 基於專家優先級共識
        if priority_consensus.get("high", 0) >= 0.5:
            return RequestPriority.HIGH
        elif priority_consensus.get("low", 0) >= 0.5:
            return RequestPriority.LOW
        else:
            return RequestPriority.NORMAL
        
        # 基於請求上下文調整
        request_type = request_context.get("type", "")
        if request_type in ["critical", "urgent", "emergency"]:
            return RequestPriority.CRITICAL
        elif request_type in ["testing", "validation", "qa"]:
            return RequestPriority.HIGH
        
        return RequestPriority.NORMAL
    
    async def _validate_routing_recommendation(self, 
                                             recommendation: RoutingRecommendation) -> RoutingRecommendation:
        """驗證路由推薦"""
        
        # 檢查推薦工具是否可用
        available_tools = []
        for tool_name in recommendation.recommended_tools:
            if await self._is_tool_available(tool_name):
                available_tools.append(tool_name)
            else:
                logger.warning(f"⚠️ 推薦工具不可用: {tool_name}")
        
        # 更新推薦
        if available_tools != recommendation.recommended_tools:
            recommendation.recommended_tools = available_tools
            recommendation.reasoning.append(f"過濾不可用工具，剩餘: {len(available_tools)} 個")
        
        # 如果沒有可用工具，降級處理
        if not available_tools:
            recommendation.confidence = 0.0
            recommendation.reasoning.append("沒有可用工具，需要回退處理")
        
        return recommendation
    
    async def _is_tool_available(self, tool_name: str) -> bool:
        """檢查工具是否可用"""
        try:
            # 檢查智慧路由引擎中是否有該工具的端點
            return tool_name in self.smart_routing_engine.tool_endpoints
        except Exception as e:
            logger.warning(f"檢查工具可用性失敗 {tool_name}: {e}")
            return False
    
    async def route_with_expert_recommendations(self, 
                                              expert_responses: List[ExpertResponse],
                                              request_context: Dict[str, Any],
                                              capability: str) -> RoutingDecision:
        """基於專家建議進行路由"""
        
        logger.info(f"🎯 基於專家建議進行路由: {capability}")
        
        try:
            # 1. 整合專家建議
            routing_recommendation = await self.integrate_expert_recommendations(
                expert_responses, request_context
            )
            
            # 2. 創建路由請求
            routing_request = RoutingRequest(
                request_id=f"expert_routing_{int(time.time())}",
                capability_required=capability,
                priority=routing_recommendation.priority,
                preferred_tools=routing_recommendation.recommended_tools,
                metadata={
                    "expert_driven": True,
                    "expert_consensus": routing_recommendation.expert_consensus,
                    "recommendation_confidence": routing_recommendation.confidence,
                    "context": request_context
                }
            )
            
            # 3. 執行路由決策
            routing_decision = await self.smart_routing_engine.route_request(routing_request)
            
            # 4. 增強路由決策信息
            if hasattr(routing_decision, 'metadata'):
                routing_decision.metadata.update({
                    "expert_recommendations": routing_recommendation.recommended_tools,
                    "expert_reasoning": routing_recommendation.reasoning,
                    "routing_strategy_used": routing_recommendation.routing_strategy
                })
            else:
                # 如果沒有 metadata 屬性，添加到 decision_reason
                routing_decision.decision_reason += f" | 專家推薦: {routing_recommendation.recommended_tools}"
            
            logger.info(f"✅ 專家建議路由完成: {routing_decision.target_tool}")
            return routing_decision
            
        except Exception as e:
            logger.error(f"❌ 專家建議路由失敗: {e}")
            # 回退到標準路由
            fallback_request = RoutingRequest(
                request_id=f"fallback_routing_{int(time.time())}",
                capability_required=capability,
                priority=RequestPriority.NORMAL,
                metadata={"context": request_context}
            )
            return await self.smart_routing_engine.route_request(fallback_request)
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """獲取整合統計信息"""
        return self.integration_stats.copy()

# 工廠函數
def create_expert_routing_integrator(smart_routing_engine: SmartRoutingEngine,
                                   expert_registry: DynamicExpertRegistry) -> ExpertRoutingIntegrator:
    """創建專家建議路由整合器"""
    return ExpertRoutingIntegrator(smart_routing_engine, expert_registry)

