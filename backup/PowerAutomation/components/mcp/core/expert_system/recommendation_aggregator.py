"""
專家建議聚合器
Expert Recommendation Aggregator
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AggregationStrategy(Enum):
    """聚合策略"""
    CONSENSUS = "consensus"          # 共識聚合
    WEIGHTED = "weighted"            # 加權聚合
    PRIORITY = "priority"            # 優先級聚合
    HYBRID = "hybrid"               # 混合聚合

@dataclass
class AggregatedRecommendation:
    """聚合後的建議"""
    category: str                    # 建議類別
    recommendation: str              # 建議內容
    confidence: float               # 信心度
    supporting_experts: List[str]    # 支持的專家
    priority: int                   # 優先級
    implementation_steps: List[str]  # 實施步驟
    required_tools: List[str]       # 需要的工具
    metadata: Dict[str, Any]        # 元數據

@dataclass
class AggregationResult:
    """聚合結果"""
    aggregated_recommendations: List[AggregatedRecommendation]
    consensus_level: float          # 共識程度
    conflict_areas: List[str]       # 衝突領域
    tool_requirements: Dict[str, Any]  # 工具需求
    implementation_plan: Dict[str, Any]  # 實施計劃
    metadata: Dict[str, Any]

class ExpertRecommendationAggregator:
    """專家建議聚合器"""
    
    def __init__(self):
        self.aggregation_strategies = {
            AggregationStrategy.CONSENSUS: self._consensus_aggregation,
            AggregationStrategy.WEIGHTED: self._weighted_aggregation,
            AggregationStrategy.PRIORITY: self._priority_aggregation,
            AggregationStrategy.HYBRID: self._hybrid_aggregation
        }
    
    async def aggregate_expert_analysis(self, expert_responses: List, 
                                      strategy: AggregationStrategy = AggregationStrategy.HYBRID) -> AggregationResult:
        """聚合專家分析"""
        logger.info(f"🔄 開始聚合 {len(expert_responses)} 個專家建議，策略: {strategy.value}")
        
        if not expert_responses:
            return AggregationResult(
                aggregated_recommendations=[],
                consensus_level=0.0,
                conflict_areas=[],
                tool_requirements={},
                implementation_plan={},
                metadata={"error": "沒有專家回應可聚合"}
            )
        
        # 預處理專家回應
        processed_responses = await self._preprocess_expert_responses(expert_responses)
        
        # 執行聚合策略
        aggregation_func = self.aggregation_strategies[strategy]
        aggregation_result = await aggregation_func(processed_responses)
        
        # 生成工具需求
        tool_requirements = await self._generate_tool_requirements(aggregation_result)
        
        # 生成實施計劃
        implementation_plan = await self._generate_implementation_plan(aggregation_result)
        
        # 檢測衝突
        conflict_areas = await self._detect_conflicts(processed_responses)
        
        # 計算共識程度
        consensus_level = await self._calculate_consensus_level(processed_responses)
        
        result = AggregationResult(
            aggregated_recommendations=aggregation_result,
            consensus_level=consensus_level,
            conflict_areas=conflict_areas,
            tool_requirements=tool_requirements,
            implementation_plan=implementation_plan,
            metadata={
                "strategy_used": strategy.value,
                "expert_count": len(expert_responses),
                "processing_time": 0.0
            }
        )
        
        logger.info(f"✅ 聚合完成，生成 {len(aggregation_result)} 個聚合建議")
        return result
    
    async def _preprocess_expert_responses(self, expert_responses: List) -> List[Dict]:
        """預處理專家回應"""
        processed = []
        
        for response in expert_responses:
            # 提取關鍵信息
            processed_response = {
                "expert_id": response.expert_id,
                "expert_name": response.expert_name,
                "expert_type": response.expert_type,
                "confidence": response.confidence,
                "analysis": response.analysis,
                "recommendations": response.recommendations,
                "tool_suggestions": response.tool_suggestions,
                "categories": await self._categorize_recommendations(response.recommendations),
                "keywords": await self._extract_keywords(response.analysis),
                "priority_indicators": await self._extract_priority_indicators(response.recommendations)
            }
            processed.append(processed_response)
        
        return processed
    
    async def _categorize_recommendations(self, recommendations: List[str]) -> Dict[str, List[str]]:
        """分類建議"""
        categories = {
            "implementation": [],
            "testing": [],
            "deployment": [],
            "security": [],
            "performance": [],
            "monitoring": [],
            "documentation": [],
            "best_practices": []
        }
        
        category_keywords = {
            "implementation": ["實現", "開發", "編碼", "程式", "代碼"],
            "testing": ["測試", "驗證", "檢查", "品質"],
            "deployment": ["部署", "發布", "上線", "生產"],
            "security": ["安全", "認證", "授權", "加密"],
            "performance": ["性能", "優化", "效率", "速度"],
            "monitoring": ["監控", "日誌", "追蹤", "觀察"],
            "documentation": ["文檔", "說明", "記錄", "註釋"],
            "best_practices": ["最佳實踐", "建議", "規範", "標準"]
        }
        
        for recommendation in recommendations:
            rec_lower = recommendation.lower()
            categorized = False
            
            for category, keywords in category_keywords.items():
                if any(keyword in rec_lower for keyword in keywords):
                    categories[category].append(recommendation)
                    categorized = True
                    break
            
            if not categorized:
                categories["best_practices"].append(recommendation)
        
        return {k: v for k, v in categories.items() if v}
    
    async def _extract_keywords(self, analysis: str) -> List[str]:
        """提取關鍵詞"""
        # 簡化的關鍵詞提取
        common_words = {"的", "是", "在", "有", "和", "與", "或", "但", "如果", "因為", "所以"}
        words = analysis.split()
        keywords = [word for word in words if len(word) > 2 and word not in common_words]
        return keywords[:10]  # 返回前10個關鍵詞
    
    async def _extract_priority_indicators(self, recommendations: List[str]) -> Dict[str, int]:
        """提取優先級指標"""
        priority_keywords = {
            "critical": ["緊急", "關鍵", "重要", "必須", "立即"],
            "high": ["建議", "應該", "需要", "推薦"],
            "medium": ["可以", "考慮", "可能", "或許"],
            "low": ["選擇性", "可選", "額外", "補充"]
        }
        
        priority_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for recommendation in recommendations:
            rec_lower = recommendation.lower()
            for priority, keywords in priority_keywords.items():
                if any(keyword in rec_lower for keyword in keywords):
                    priority_counts[priority] += 1
        
        return priority_counts
    
    async def _consensus_aggregation(self, processed_responses: List[Dict]) -> List[AggregatedRecommendation]:
        """共識聚合策略"""
        # 找出所有專家都同意的建議
        all_categories = set()
        for response in processed_responses:
            all_categories.update(response["categories"].keys())
        
        aggregated = []
        
        for category in all_categories:
            # 收集該類別的所有建議
            category_recommendations = []
            supporting_experts = []
            
            for response in processed_responses:
                if category in response["categories"]:
                    category_recommendations.extend(response["categories"][category])
                    supporting_experts.append(response["expert_name"])
            
            if len(supporting_experts) >= len(processed_responses) * 0.5:  # 至少50%專家支持
                # 合併相似建議
                merged_recommendation = await self._merge_similar_recommendations(category_recommendations)
                
                aggregated.append(AggregatedRecommendation(
                    category=category,
                    recommendation=merged_recommendation,
                    confidence=len(supporting_experts) / len(processed_responses),
                    supporting_experts=supporting_experts,
                    priority=self._calculate_category_priority(category),
                    implementation_steps=await self._generate_implementation_steps(merged_recommendation),
                    required_tools=await self._identify_required_tools(merged_recommendation),
                    metadata={"aggregation_method": "consensus"}
                ))
        
        return sorted(aggregated, key=lambda x: x.priority, reverse=True)
    
    async def _weighted_aggregation(self, processed_responses: List[Dict]) -> List[AggregatedRecommendation]:
        """加權聚合策略"""
        # 基於專家信心度進行加權
        category_weights = {}
        category_recommendations = {}
        
        for response in processed_responses:
            weight = response["confidence"]
            
            for category, recommendations in response["categories"].items():
                if category not in category_weights:
                    category_weights[category] = 0
                    category_recommendations[category] = []
                
                category_weights[category] += weight
                category_recommendations[category].extend(recommendations)
        
        aggregated = []
        total_weight = sum(category_weights.values())
        
        for category, weight in category_weights.items():
            if weight > 0:
                normalized_confidence = weight / total_weight
                merged_recommendation = await self._merge_similar_recommendations(category_recommendations[category])
                
                aggregated.append(AggregatedRecommendation(
                    category=category,
                    recommendation=merged_recommendation,
                    confidence=normalized_confidence,
                    supporting_experts=[r["expert_name"] for r in processed_responses if category in r["categories"]],
                    priority=self._calculate_category_priority(category),
                    implementation_steps=await self._generate_implementation_steps(merged_recommendation),
                    required_tools=await self._identify_required_tools(merged_recommendation),
                    metadata={"aggregation_method": "weighted", "weight": weight}
                ))
        
        return sorted(aggregated, key=lambda x: x.confidence, reverse=True)
    
    async def _priority_aggregation(self, processed_responses: List[Dict]) -> List[AggregatedRecommendation]:
        """優先級聚合策略"""
        # 基於優先級指標進行聚合
        priority_scores = {}
        category_recommendations = {}
        
        for response in processed_responses:
            priority_indicators = response["priority_indicators"]
            
            for category, recommendations in response["categories"].items():
                if category not in priority_scores:
                    priority_scores[category] = 0
                    category_recommendations[category] = []
                
                # 計算優先級分數
                score = (priority_indicators.get("critical", 0) * 4 +
                        priority_indicators.get("high", 0) * 3 +
                        priority_indicators.get("medium", 0) * 2 +
                        priority_indicators.get("low", 0) * 1)
                
                priority_scores[category] += score
                category_recommendations[category].extend(recommendations)
        
        aggregated = []
        max_score = max(priority_scores.values()) if priority_scores else 1
        
        for category, score in priority_scores.items():
            if score > 0:
                normalized_confidence = score / max_score
                merged_recommendation = await self._merge_similar_recommendations(category_recommendations[category])
                
                aggregated.append(AggregatedRecommendation(
                    category=category,
                    recommendation=merged_recommendation,
                    confidence=normalized_confidence,
                    supporting_experts=[r["expert_name"] for r in processed_responses if category in r["categories"]],
                    priority=score,
                    implementation_steps=await self._generate_implementation_steps(merged_recommendation),
                    required_tools=await self._identify_required_tools(merged_recommendation),
                    metadata={"aggregation_method": "priority", "priority_score": score}
                ))
        
        return sorted(aggregated, key=lambda x: x.priority, reverse=True)
    
    async def _hybrid_aggregation(self, processed_responses: List[Dict]) -> List[AggregatedRecommendation]:
        """混合聚合策略"""
        # 結合共識、加權和優先級
        consensus_result = await self._consensus_aggregation(processed_responses)
        weighted_result = await self._weighted_aggregation(processed_responses)
        priority_result = await self._priority_aggregation(processed_responses)
        
        # 合併結果
        hybrid_result = {}
        
        # 處理共識結果
        for rec in consensus_result:
            hybrid_result[rec.category] = rec
            hybrid_result[rec.category].metadata["consensus_score"] = rec.confidence
        
        # 整合加權結果
        for rec in weighted_result:
            if rec.category in hybrid_result:
                hybrid_result[rec.category].confidence = (
                    hybrid_result[rec.category].confidence * 0.4 + rec.confidence * 0.6
                )
                hybrid_result[rec.category].metadata["weighted_score"] = rec.confidence
            else:
                hybrid_result[rec.category] = rec
                hybrid_result[rec.category].metadata["weighted_score"] = rec.confidence
        
        # 整合優先級結果
        for rec in priority_result:
            if rec.category in hybrid_result:
                hybrid_result[rec.category].priority = max(
                    hybrid_result[rec.category].priority, rec.priority
                )
                hybrid_result[rec.category].metadata["priority_score"] = rec.priority
            else:
                hybrid_result[rec.category] = rec
                hybrid_result[rec.category].metadata["priority_score"] = rec.priority
        
        # 重新計算最終分數
        for rec in hybrid_result.values():
            consensus_score = rec.metadata.get("consensus_score", 0.5)
            weighted_score = rec.metadata.get("weighted_score", 0.5)
            priority_score = rec.metadata.get("priority_score", 5) / 10.0  # 正規化到0-1
            
            rec.confidence = (consensus_score * 0.3 + weighted_score * 0.4 + priority_score * 0.3)
            rec.metadata["aggregation_method"] = "hybrid"
            rec.metadata["final_score"] = rec.confidence
        
        return sorted(hybrid_result.values(), key=lambda x: x.confidence, reverse=True)
    
    async def _merge_similar_recommendations(self, recommendations: List[str]) -> str:
        """合併相似建議"""
        if not recommendations:
            return ""
        
        if len(recommendations) == 1:
            return recommendations[0]
        
        # 簡化的合併邏輯
        merged = f"綜合建議：{recommendations[0]}"
        if len(recommendations) > 1:
            merged += f"，同時考慮{len(recommendations)-1}個相關建議"
        
        return merged
    
    def _calculate_category_priority(self, category: str) -> int:
        """計算類別優先級"""
        priority_map = {
            "security": 10,
            "implementation": 9,
            "testing": 8,
            "performance": 7,
            "deployment": 6,
            "monitoring": 5,
            "documentation": 4,
            "best_practices": 3
        }
        return priority_map.get(category, 5)
    
    async def _generate_implementation_steps(self, recommendation: str) -> List[str]:
        """生成實施步驟"""
        # 基於建議內容生成實施步驟
        steps = [
            "1. 分析當前狀況和需求",
            f"2. 根據建議制定實施計劃：{recommendation[:50]}...",
            "3. 準備必要的工具和資源",
            "4. 執行實施計劃",
            "5. 測試和驗證結果",
            "6. 監控和優化"
        ]
        return steps
    
    async def _identify_required_tools(self, recommendation: str) -> List[str]:
        """識別需要的工具"""
        tools = []
        rec_lower = recommendation.lower()
        
        tool_keywords = {
            "general_processor_mcp": ["處理", "分析", "綜合"],
            "test_flow_mcp": ["測試", "驗證", "檢查"],
            "system_monitor_adapter_mcp": ["監控", "觀察", "追蹤"],
            "file_processor_adapter_mcp": ["文件", "檔案", "處理"]
        }
        
        for tool, keywords in tool_keywords.items():
            if any(keyword in rec_lower for keyword in keywords):
                tools.append(tool)
        
        return tools
    
    async def _generate_tool_requirements(self, aggregated_recommendations: List[AggregatedRecommendation]) -> Dict[str, Any]:
        """生成工具需求"""
        tool_requirements = {
            "required_tools": set(),
            "tool_priorities": {},
            "dynamic_tools_needed": [],
            "flow_mcp_requirements": [],
            "adapter_mcp_requirements": []
        }
        
        for rec in aggregated_recommendations:
            # 收集所有需要的工具
            tool_requirements["required_tools"].update(rec.required_tools)
            
            # 設置工具優先級
            for tool in rec.required_tools:
                if tool not in tool_requirements["tool_priorities"]:
                    tool_requirements["tool_priorities"][tool] = 0
                tool_requirements["tool_priorities"][tool] += rec.priority
            
            # 檢查是否需要動態生成Flow MCP
            if rec.category in ["implementation", "testing", "deployment"]:
                flow_requirement = {
                    "category": rec.category,
                    "recommendation": rec.recommendation,
                    "steps": rec.implementation_steps,
                    "confidence": rec.confidence
                }
                tool_requirements["flow_mcp_requirements"].append(flow_requirement)
            
            # 檢查是否需要動態生成Adapter MCP
            if rec.category in ["monitoring", "performance", "security"]:
                adapter_requirement = {
                    "category": rec.category,
                    "recommendation": rec.recommendation,
                    "target_system": self._extract_target_system(rec.recommendation),
                    "confidence": rec.confidence
                }
                tool_requirements["adapter_mcp_requirements"].append(adapter_requirement)
        
        # 轉換set為list
        tool_requirements["required_tools"] = list(tool_requirements["required_tools"])
        
        return tool_requirements
    
    def _extract_target_system(self, recommendation: str) -> str:
        """提取目標系統"""
        system_keywords = {
            "database": ["資料庫", "數據庫", "database", "sql"],
            "web_server": ["網頁", "web", "server", "伺服器"],
            "api": ["api", "接口", "介面"],
            "file_system": ["文件", "檔案", "file"],
            "network": ["網路", "網絡", "network"]
        }
        
        rec_lower = recommendation.lower()
        for system, keywords in system_keywords.items():
            if any(keyword in rec_lower for keyword in keywords):
                return system
        
        return "general"
    
    async def _generate_implementation_plan(self, aggregated_recommendations: List[AggregatedRecommendation]) -> Dict[str, Any]:
        """生成實施計劃"""
        plan = {
            "phases": [],
            "timeline": {},
            "dependencies": {},
            "resource_requirements": {}
        }
        
        # 按優先級分組
        high_priority = [r for r in aggregated_recommendations if r.priority >= 8]
        medium_priority = [r for r in aggregated_recommendations if 5 <= r.priority < 8]
        low_priority = [r for r in aggregated_recommendations if r.priority < 5]
        
        # 生成階段
        if high_priority:
            plan["phases"].append({
                "phase": "immediate",
                "recommendations": [r.category for r in high_priority],
                "duration": "1-2 days"
            })
        
        if medium_priority:
            plan["phases"].append({
                "phase": "short_term",
                "recommendations": [r.category for r in medium_priority],
                "duration": "1-2 weeks"
            })
        
        if low_priority:
            plan["phases"].append({
                "phase": "long_term",
                "recommendations": [r.category for r in low_priority],
                "duration": "1-2 months"
            })
        
        return plan
    
    async def _detect_conflicts(self, processed_responses: List[Dict]) -> List[str]:
        """檢測衝突"""
        conflicts = []
        
        # 檢查相同類別的不同建議
        category_experts = {}
        for response in processed_responses:
            for category in response["categories"]:
                if category not in category_experts:
                    category_experts[category] = []
                category_experts[category].append(response["expert_name"])
        
        # 如果某個類別有多個專家但建議差異很大，標記為衝突
        for category, experts in category_experts.items():
            if len(experts) > 1 and len(set(experts)) == len(experts):
                conflicts.append(f"{category}領域專家意見分歧")
        
        return conflicts
    
    async def _calculate_consensus_level(self, processed_responses: List[Dict]) -> float:
        """計算共識程度"""
        if not processed_responses:
            return 0.0
        
        # 計算專家在各類別上的一致性
        all_categories = set()
        for response in processed_responses:
            all_categories.update(response["categories"].keys())
        
        consensus_scores = []
        for category in all_categories:
            experts_with_category = sum(1 for r in processed_responses if category in r["categories"])
            consensus_score = experts_with_category / len(processed_responses)
            consensus_scores.append(consensus_score)
        
        return sum(consensus_scores) / len(consensus_scores) if consensus_scores else 0.0

def create_expert_recommendation_aggregator() -> ExpertRecommendationAggregator:
    """創建專家建議聚合器"""
    return ExpertRecommendationAggregator()

