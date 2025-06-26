"""
增強的對比引擎 (Enhanced Comparison Engine)
支持多數據源（Manus + Plugin）的對比分析
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict

# 導入數據提供者
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

try:
    from data_provider import DataProvider, UserContext, ComparisonContext, ConversationHistory
    from plugin_data_access import PluginDataAccess, CodeSnapshot
except ImportError:
    # 如果相對導入失敗，嘗試絕對導入
    try:
        from ..shared.data_provider import DataProvider, UserContext, ComparisonContext, ConversationHistory
        from ..shared.plugin_data_access import PluginDataAccess, CodeSnapshot
    except ImportError:
        # 最後嘗試直接導入
        from PowerAutomation.components.mcp.shared.data_provider import DataProvider, UserContext, ComparisonContext, ConversationHistory
        from PowerAutomation.components.mcp.shared.plugin_data_access import PluginDataAccess, CodeSnapshot

logger = logging.getLogger(__name__)

class ComparisonType(Enum):
    """對比類型"""
    CONVERSATION_ANALYSIS = "conversation_analysis"
    CODE_QUALITY = "code_quality"
    PERFORMANCE_BENCHMARK = "performance_benchmark"
    BEST_PRACTICES = "best_practices"
    COMPREHENSIVE = "comprehensive"

class AnalysisDepth(Enum):
    """分析深度"""
    SHALLOW = "shallow"      # 快速分析
    MEDIUM = "medium"        # 標準分析
    DEEP = "deep"           # 深度分析

@dataclass
class ComparisonRequest:
    """對比請求"""
    user_id: str
    request_id: str
    comparison_type: ComparisonType
    analysis_depth: AnalysisDepth = AnalysisDepth.MEDIUM
    include_code_context: bool = True
    include_conversation_history: bool = True
    custom_criteria: Optional[Dict[str, Any]] = None

@dataclass
class ComparisonResult:
    """對比結果"""
    comparison_id: str
    user_id: str
    request_id: str
    comparison_type: ComparisonType
    overall_score: float
    confidence_score: float
    analysis_results: Dict[str, Any]
    recommendations: List[str]
    gaps_identified: List[Dict[str, Any]]
    improvement_suggestions: List[str]
    execution_time: float
    timestamp: datetime
    metadata: Dict[str, Any]

class EnhancedComparisonAnalysisEngine:
    """增強的對比分析引擎"""
    
    def __init__(self, data_provider: DataProvider = None, config: Dict[str, Any] = None):
        """
        初始化增強的對比分析引擎
        
        Args:
            data_provider: 數據提供者實例
            config: 配置參數
        """
        self.data_provider = data_provider or DataProvider()
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 配置參數
        self.default_analysis_depth = AnalysisDepth.MEDIUM
        self.max_conversation_history = self.config.get('max_conversation_history', 20)
        self.max_code_files = self.config.get('max_code_files', 100)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        
        self.logger.info("Enhanced Comparison Analysis Engine initialized")
    
    async def analyze_comparison(self, request: ComparisonRequest) -> ComparisonResult:
        """
        執行對比分析
        
        Args:
            request: 對比請求
            
        Returns:
            ComparisonResult: 對比結果
        """
        start_time = time.time()
        comparison_id = f"comp_{request.request_id}_{int(start_time)}"
        
        self.logger.info(f"Starting comparison analysis: {comparison_id}")
        
        try:
            # 獲取對比數據
            comparison_context = await self.data_provider.get_comparison_data(
                request.user_id, request.request_id
            )
            
            # 根據對比類型執行分析
            analysis_results = await self._execute_analysis(request, comparison_context)
            
            # 計算總體分數和信心分數
            overall_score, confidence_score = self._calculate_scores(analysis_results, request)
            
            # 生成建議和改進意見
            recommendations = self._generate_recommendations(analysis_results, comparison_context)
            gaps_identified = self._identify_gaps(analysis_results, comparison_context)
            improvement_suggestions = self._generate_improvements(analysis_results, comparison_context)
            
            execution_time = time.time() - start_time
            
            result = ComparisonResult(
                comparison_id=comparison_id,
                user_id=request.user_id,
                request_id=request.request_id,
                comparison_type=request.comparison_type,
                overall_score=overall_score,
                confidence_score=confidence_score,
                analysis_results=analysis_results,
                recommendations=recommendations,
                gaps_identified=gaps_identified,
                improvement_suggestions=improvement_suggestions,
                execution_time=execution_time,
                timestamp=datetime.now(),
                metadata={
                    "analysis_depth": request.analysis_depth.value,
                    "data_sources_used": self._get_data_sources_metadata(comparison_context),
                    "engine_version": "enhanced_v1.0"
                }
            )
            
            self.logger.info(f"Comparison analysis completed: {comparison_id}, "
                           f"score: {overall_score:.2f}, confidence: {confidence_score:.2f}, "
                           f"time: {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Comparison analysis failed: {comparison_id}, error: {e}")
            
            return ComparisonResult(
                comparison_id=comparison_id,
                user_id=request.user_id,
                request_id=request.request_id,
                comparison_type=request.comparison_type,
                overall_score=0.0,
                confidence_score=0.0,
                analysis_results={"error": str(e)},
                recommendations=["檢查系統狀態", "重試分析"],
                gaps_identified=[],
                improvement_suggestions=[],
                execution_time=execution_time,
                timestamp=datetime.now(),
                metadata={"error": str(e)}
            )
    
    async def _execute_analysis(self, request: ComparisonRequest, 
                               comparison_context: ComparisonContext) -> Dict[str, Any]:
        """執行具體的分析邏輯"""
        
        analysis_results = {}
        
        if request.comparison_type == ComparisonType.CONVERSATION_ANALYSIS:
            analysis_results = await self._analyze_conversations(request, comparison_context)
        
        elif request.comparison_type == ComparisonType.CODE_QUALITY:
            analysis_results = await self._analyze_code_quality(request, comparison_context)
        
        elif request.comparison_type == ComparisonType.PERFORMANCE_BENCHMARK:
            analysis_results = await self._analyze_performance(request, comparison_context)
        
        elif request.comparison_type == ComparisonType.BEST_PRACTICES:
            analysis_results = await self._analyze_best_practices(request, comparison_context)
        
        elif request.comparison_type == ComparisonType.COMPREHENSIVE:
            analysis_results = await self._analyze_comprehensive(request, comparison_context)
        
        else:
            analysis_results = {"error": f"Unsupported comparison type: {request.comparison_type}"}
        
        return analysis_results
    
    async def _analyze_conversations(self, request: ComparisonRequest, 
                                   context: ComparisonContext) -> Dict[str, Any]:
        """分析對話歷史"""
        
        conversations = context.user_context.conversations
        manus_standards = context.manus_standards
        
        analysis = {
            "conversation_count": len(conversations),
            "total_messages": sum(conv.total_messages for conv in conversations),
            "avg_relevance_score": sum(conv.relevant_score for conv in conversations) / len(conversations) if conversations else 0,
            "topic_distribution": self._analyze_topic_distribution(conversations),
            "quality_metrics": self._calculate_conversation_quality(conversations, manus_standards),
            "patterns_identified": self._identify_conversation_patterns(conversations),
            "manus_alignment": self._check_manus_alignment(conversations, manus_standards)
        }
        
        return analysis
    
    async def _analyze_code_quality(self, request: ComparisonRequest, 
                                   context: ComparisonContext) -> Dict[str, Any]:
        """分析代碼質量"""
        
        code_snapshot = context.user_context.code_snapshot
        manus_standards = context.manus_standards
        
        if not code_snapshot:
            return {"error": "No code snapshot available"}
        
        analysis = {
            "project_info": {
                "name": code_snapshot.project.name,
                "language": code_snapshot.project.language,
                "file_count": code_snapshot.file_count,
                "total_size": code_snapshot.total_size
            },
            "code_metrics": await self._calculate_code_metrics(code_snapshot),
            "quality_score": self._calculate_code_quality_score(code_snapshot, manus_standards),
            "standards_compliance": self._check_coding_standards(code_snapshot, manus_standards),
            "security_analysis": self._analyze_code_security(code_snapshot),
            "maintainability": self._assess_maintainability(code_snapshot)
        }
        
        return analysis
    
    async def _analyze_performance(self, request: ComparisonRequest, 
                                 context: ComparisonContext) -> Dict[str, Any]:
        """分析性能基準"""
        
        user_context = context.user_context
        manus_standards = context.manus_standards
        
        analysis = {
            "context_performance": {
                "context_score": user_context.context_score,
                "data_completeness": self._calculate_data_completeness(user_context),
                "response_quality": self._assess_response_quality(user_context)
            },
            "benchmark_comparison": self._compare_with_benchmarks(user_context, manus_standards),
            "efficiency_metrics": self._calculate_efficiency_metrics(user_context),
            "optimization_opportunities": self._identify_optimization_opportunities(user_context)
        }
        
        return analysis
    
    async def _analyze_best_practices(self, request: ComparisonRequest, 
                                    context: ComparisonContext) -> Dict[str, Any]:
        """分析最佳實踐遵循情況"""
        
        user_context = context.user_context
        manus_standards = context.manus_standards
        
        analysis = {
            "practices_assessment": self._assess_best_practices(user_context, manus_standards),
            "compliance_score": self._calculate_compliance_score(user_context, manus_standards),
            "deviation_analysis": self._analyze_deviations(user_context, manus_standards),
            "improvement_areas": self._identify_improvement_areas(user_context, manus_standards)
        }
        
        return analysis
    
    async def _analyze_comprehensive(self, request: ComparisonRequest, 
                                   context: ComparisonContext) -> Dict[str, Any]:
        """綜合分析"""
        
        # 執行所有類型的分析
        conversation_analysis = await self._analyze_conversations(request, context)
        code_analysis = await self._analyze_code_quality(request, context)
        performance_analysis = await self._analyze_performance(request, context)
        practices_analysis = await self._analyze_best_practices(request, context)
        
        # 綜合評估
        comprehensive_analysis = {
            "conversation_analysis": conversation_analysis,
            "code_quality_analysis": code_analysis,
            "performance_analysis": performance_analysis,
            "best_practices_analysis": practices_analysis,
            "overall_assessment": self._generate_overall_assessment([
                conversation_analysis, code_analysis, performance_analysis, practices_analysis
            ]),
            "cross_domain_insights": self._generate_cross_domain_insights([
                conversation_analysis, code_analysis, performance_analysis, practices_analysis
            ])
        }
        
        return comprehensive_analysis
    
    def _calculate_scores(self, analysis_results: Dict[str, Any], 
                         request: ComparisonRequest) -> tuple[float, float]:
        """計算總體分數和信心分數"""
        
        if "error" in analysis_results:
            return 0.0, 0.0
        
        # 根據分析類型計算分數
        if request.comparison_type == ComparisonType.CONVERSATION_ANALYSIS:
            overall_score = analysis_results.get("quality_metrics", {}).get("overall_score", 0.0)
            confidence_score = analysis_results.get("avg_relevance_score", 0.0)
        
        elif request.comparison_type == ComparisonType.CODE_QUALITY:
            overall_score = analysis_results.get("quality_score", 0.0)
            confidence_score = min(analysis_results.get("project_info", {}).get("file_count", 0) / 50, 1.0)
        
        elif request.comparison_type == ComparisonType.PERFORMANCE_BENCHMARK:
            overall_score = analysis_results.get("context_performance", {}).get("context_score", 0.0)
            confidence_score = analysis_results.get("context_performance", {}).get("data_completeness", 0.0)
        
        elif request.comparison_type == ComparisonType.BEST_PRACTICES:
            overall_score = analysis_results.get("compliance_score", 0.0)
            confidence_score = 0.8  # 固定信心分數
        
        elif request.comparison_type == ComparisonType.COMPREHENSIVE:
            # 綜合分析的分數計算
            sub_scores = []
            for key in ["conversation_analysis", "code_quality_analysis", "performance_analysis", "best_practices_analysis"]:
                sub_analysis = analysis_results.get(key, {})
                if not sub_analysis.get("error"):
                    sub_scores.append(self._extract_score_from_analysis(sub_analysis))
            
            overall_score = sum(sub_scores) / len(sub_scores) if sub_scores else 0.0
            confidence_score = len(sub_scores) / 4.0  # 基於可用分析的比例
        
        else:
            overall_score = 0.5  # 默認分數
            confidence_score = 0.5
        
        return min(overall_score, 1.0), min(confidence_score, 1.0)
    
    def _extract_score_from_analysis(self, analysis: Dict[str, Any]) -> float:
        """從分析結果中提取分數"""
        
        # 嘗試多個可能的分數字段
        score_fields = ["overall_score", "quality_score", "context_score", "compliance_score"]
        
        for field in score_fields:
            if field in analysis:
                return analysis[field]
            
            # 嘗試嵌套字段
            for key, value in analysis.items():
                if isinstance(value, dict) and field in value:
                    return value[field]
        
        return 0.5  # 默認分數
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any], 
                                context: ComparisonContext) -> List[str]:
        """生成建議"""
        
        recommendations = []
        
        # 基於分析結果生成建議
        if "conversation_analysis" in analysis_results:
            conv_analysis = analysis_results["conversation_analysis"]
            if conv_analysis.get("avg_relevance_score", 0) < 0.7:
                recommendations.append("建議提高對話相關性，專注於核心問題")
            
            if conv_analysis.get("conversation_count", 0) < 5:
                recommendations.append("建議增加對話歷史以提供更好的上下文")
        
        if "code_quality_analysis" in analysis_results:
            code_analysis = analysis_results["code_quality_analysis"]
            if not code_analysis.get("error"):
                quality_score = code_analysis.get("quality_score", 0)
                if quality_score < 0.7:
                    recommendations.append("建議改進代碼質量，遵循編碼標準")
                
                if code_analysis.get("project_info", {}).get("file_count", 0) > 100:
                    recommendations.append("項目規模較大，建議進行模塊化重構")
        
        if "performance_analysis" in analysis_results:
            perf_analysis = analysis_results["performance_analysis"]
            context_score = perf_analysis.get("context_performance", {}).get("context_score", 0)
            if context_score < 0.6:
                recommendations.append("建議優化上下文質量以提升分析準確性")
        
        # 通用建議
        if not recommendations:
            recommendations.append("系統運行良好，建議保持當前最佳實踐")
        
        return recommendations
    
    def _identify_gaps(self, analysis_results: Dict[str, Any], 
                      context: ComparisonContext) -> List[Dict[str, Any]]:
        """識別差距"""
        
        gaps = []
        
        # 對話歷史差距
        conversations = context.user_context.conversations
        if len(conversations) < 3:
            gaps.append({
                "type": "conversation_history",
                "severity": "medium",
                "description": "對話歷史不足，可能影響上下文理解",
                "current_value": len(conversations),
                "recommended_value": "至少3個對話"
            })
        
        # 代碼上下文差距
        code_snapshot = context.user_context.code_snapshot
        if not code_snapshot:
            gaps.append({
                "type": "code_context",
                "severity": "high",
                "description": "缺少代碼上下文，無法進行代碼相關分析",
                "current_value": "無",
                "recommended_value": "至少一個項目快照"
            })
        elif code_snapshot.file_count < 5:
            gaps.append({
                "type": "code_completeness",
                "severity": "low",
                "description": "代碼文件數量較少，可能影響分析完整性",
                "current_value": code_snapshot.file_count,
                "recommended_value": "至少5個文件"
            })
        
        return gaps
    
    def _generate_improvements(self, analysis_results: Dict[str, Any], 
                             context: ComparisonContext) -> List[str]:
        """生成改進建議"""
        
        improvements = []
        
        # 基於上下文分數生成改進建議
        context_score = context.user_context.context_score
        if context_score < 0.5:
            improvements.append("增加對話互動頻率以建立更豐富的上下文")
            improvements.append("提供更多代碼示例和項目信息")
        elif context_score < 0.8:
            improvements.append("優化對話質量，提供更具體的需求描述")
            improvements.append("保持代碼同步的及時性")
        
        # 基於分析結果生成改進建議
        if "code_quality_analysis" in analysis_results:
            code_analysis = analysis_results["code_quality_analysis"]
            if not code_analysis.get("error"):
                improvements.append("實施代碼審查流程以提升代碼質量")
                improvements.append("使用自動化工具進行代碼質量檢查")
        
        return improvements
    
    def _get_data_sources_metadata(self, context: ComparisonContext) -> Dict[str, Any]:
        """獲取數據源元數據"""
        
        return {
            "conversations_count": len(context.user_context.conversations),
            "code_snapshot_available": context.user_context.code_snapshot is not None,
            "code_files_count": context.user_context.code_snapshot.file_count if context.user_context.code_snapshot else 0,
            "request_history_count": len(context.user_context.request_history),
            "manus_standards_available": bool(context.manus_standards),
            "context_quality_score": context.user_context.context_score
        }
    
    # 輔助方法（簡化實現）
    def _analyze_topic_distribution(self, conversations: List[ConversationHistory]) -> Dict[str, int]:
        """分析話題分佈"""
        topics = {}
        for conv in conversations:
            topic = conv.context.get("topic", "unknown") if conv.context else "unknown"
            topics[topic] = topics.get(topic, 0) + 1
        return topics
    
    def _calculate_conversation_quality(self, conversations: List[ConversationHistory], 
                                      manus_standards: Dict[str, Any]) -> Dict[str, float]:
        """計算對話質量"""
        if not conversations:
            return {"overall_score": 0.0}
        
        avg_relevance = sum(conv.relevant_score for conv in conversations) / len(conversations)
        avg_length = sum(conv.total_messages for conv in conversations) / len(conversations)
        
        return {
            "overall_score": (avg_relevance + min(avg_length / 10, 1.0)) / 2,
            "relevance_score": avg_relevance,
            "engagement_score": min(avg_length / 10, 1.0)
        }
    
    def _identify_conversation_patterns(self, conversations: List[ConversationHistory]) -> List[str]:
        """識別對話模式"""
        patterns = []
        
        if len(conversations) > 5:
            patterns.append("高頻互動用戶")
        
        topics = self._analyze_topic_distribution(conversations)
        if len(topics) > 3:
            patterns.append("多領域興趣")
        
        return patterns
    
    def _check_manus_alignment(self, conversations: List[ConversationHistory], 
                             manus_standards: Dict[str, Any]) -> Dict[str, Any]:
        """檢查與 Manus 標準的對齊"""
        return {
            "alignment_score": 0.8,  # 模擬分數
            "compliant_conversations": len(conversations),
            "non_compliant_conversations": 0
        }
    
    async def _calculate_code_metrics(self, code_snapshot: CodeSnapshot) -> Dict[str, Any]:
        """計算代碼指標"""
        return {
            "lines_of_code": code_snapshot.total_size // 50,  # 估算
            "file_diversity": len(set(f.file_path.split('.')[-1] for f in code_snapshot.files)),
            "avg_file_size": code_snapshot.total_size // code_snapshot.file_count if code_snapshot.file_count > 0 else 0
        }
    
    def _calculate_code_quality_score(self, code_snapshot: CodeSnapshot, 
                                    manus_standards: Dict[str, Any]) -> float:
        """計算代碼質量分數"""
        # 簡化的質量評分
        base_score = 0.7
        
        # 基於文件數量調整
        if code_snapshot.file_count > 20:
            base_score += 0.1
        
        # 基於項目語言調整
        if code_snapshot.project.language in ["Python", "JavaScript", "TypeScript"]:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _check_coding_standards(self, code_snapshot: CodeSnapshot, 
                              manus_standards: Dict[str, Any]) -> Dict[str, Any]:
        """檢查編碼標準"""
        return {
            "standards_compliance": 0.85,
            "violations_found": 2,
            "recommendations": ["使用一致的命名規範", "添加更多註釋"]
        }
    
    def _analyze_code_security(self, code_snapshot: CodeSnapshot) -> Dict[str, Any]:
        """分析代碼安全性"""
        return {
            "security_score": 0.8,
            "vulnerabilities_found": 0,
            "security_recommendations": ["實施輸入驗證", "使用安全的加密方法"]
        }
    
    def _assess_maintainability(self, code_snapshot: CodeSnapshot) -> Dict[str, Any]:
        """評估可維護性"""
        return {
            "maintainability_score": 0.75,
            "complexity_level": "medium",
            "refactoring_suggestions": ["提取重複代碼", "簡化複雜函數"]
        }
    
    def _calculate_data_completeness(self, user_context: UserContext) -> float:
        """計算數據完整性"""
        completeness = 0.0
        
        if user_context.conversations:
            completeness += 0.4
        
        if user_context.code_snapshot:
            completeness += 0.4
        
        if user_context.request_history:
            completeness += 0.2
        
        return completeness
    
    def _assess_response_quality(self, user_context: UserContext) -> float:
        """評估響應質量"""
        if not user_context.conversations:
            return 0.0
        
        return sum(conv.relevant_score for conv in user_context.conversations) / len(user_context.conversations)
    
    def _compare_with_benchmarks(self, user_context: UserContext, 
                               manus_standards: Dict[str, Any]) -> Dict[str, Any]:
        """與基準進行比較"""
        return {
            "benchmark_score": user_context.context_score,
            "above_average": user_context.context_score > 0.6,
            "percentile": int(user_context.context_score * 100)
        }
    
    def _calculate_efficiency_metrics(self, user_context: UserContext) -> Dict[str, Any]:
        """計算效率指標"""
        return {
            "context_efficiency": user_context.context_score,
            "data_utilization": self._calculate_data_completeness(user_context),
            "response_effectiveness": self._assess_response_quality(user_context)
        }
    
    def _identify_optimization_opportunities(self, user_context: UserContext) -> List[str]:
        """識別優化機會"""
        opportunities = []
        
        if user_context.context_score < 0.7:
            opportunities.append("提升上下文質量")
        
        if not user_context.code_snapshot:
            opportunities.append("添加代碼上下文")
        
        if len(user_context.conversations) < 5:
            opportunities.append("增加對話歷史")
        
        return opportunities
    
    def _assess_best_practices(self, user_context: UserContext, 
                             manus_standards: Dict[str, Any]) -> Dict[str, Any]:
        """評估最佳實踐"""
        return {
            "practices_followed": ["定期同步", "詳細描述需求"],
            "practices_missing": ["代碼註釋", "測試覆蓋"],
            "overall_compliance": 0.75
        }
    
    def _calculate_compliance_score(self, user_context: UserContext, 
                                  manus_standards: Dict[str, Any]) -> float:
        """計算合規分數"""
        return 0.8  # 模擬分數
    
    def _analyze_deviations(self, user_context: UserContext, 
                          manus_standards: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析偏差"""
        return [
            {
                "type": "documentation",
                "severity": "low",
                "description": "文檔不夠詳細"
            }
        ]
    
    def _identify_improvement_areas(self, user_context: UserContext, 
                                  manus_standards: Dict[str, Any]) -> List[str]:
        """識別改進領域"""
        return ["代碼文檔", "測試覆蓋率", "錯誤處理"]
    
    def _generate_overall_assessment(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成總體評估"""
        return {
            "overall_health": "good",
            "key_strengths": ["良好的對話互動", "代碼結構清晰"],
            "key_weaknesses": ["測試覆蓋不足", "文檔需要改進"],
            "priority_actions": ["增加單元測試", "完善API文檔"]
        }
    
    def _generate_cross_domain_insights(self, analyses: List[Dict[str, Any]]) -> List[str]:
        """生成跨領域洞察"""
        return [
            "對話質量與代碼質量呈正相關",
            "頻繁的代碼同步有助於提升上下文準確性",
            "多樣化的話題討論促進了全面的需求理解"
        ]

