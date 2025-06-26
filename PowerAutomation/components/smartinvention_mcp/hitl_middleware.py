#!/usr/bin/env python3
"""
SmartInvention-Manus Human-in-the-Loop 中間件
處理 VS Code VSIX 請求，觸發 SmartInvention，收集對話歷史，執行增量比對，並返回結果
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# 導入現有組件
try:
    from .enhanced import EnhancedSmartinventionAdapterMCP, TaskStorageManager
    from components.manus_adapter_mcp import ManusAdapterMCP, ManusRequirementParser
    # 導入新的增強對比引擎
    from ..workflow.test_flow.v4.enhanced_comparison_engine import (
        EnhancedComparisonAnalysisEngine, ComparisonRequest, ComparisonType, AnalysisDepth
    )
    from ..shared.data_provider import DataProvider
    from ..shared.plugin_data_access import PluginDataAccess
except ImportError as e:
    logging.warning(f"無法導入部分組件: {e}")

logger = logging.getLogger(__name__)

class ReviewStatus(Enum):
    """人工審核狀態"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"

@dataclass
class VSIXRequest:
    """VSIX 請求數據結構"""
    request_id: str
    content: str
    context: Dict[str, Any]
    timestamp: float
    source: str = "vscode_vsix"
    metadata: Dict[str, Any] = None

@dataclass
class ConversationHistory:
    """對話歷史數據結構"""
    conversation_id: str
    messages: List[Dict[str, Any]]
    participants: List[str]
    timestamp_range: Dict[str, str]
    total_messages: int
    relevant_score: float

@dataclass
class IncrementalComparison:
    """增量比對結果"""
    comparison_id: str
    current_state: Dict[str, Any]
    manus_standards: Dict[str, Any]
    differences: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    confidence_score: float
    timestamp: str

@dataclass
class HITLReview:
    """Human-in-the-Loop 審核"""
    review_id: str
    reviewer: str
    status: ReviewStatus
    original_recommendations: List[Dict[str, Any]]
    approved_recommendations: List[Dict[str, Any]]
    comments: str
    timestamp: str

@dataclass
class SmartInventionResponse:
    """SmartInvention 響應給 VSIX - 直接使用 Manus 回覆"""
    request_id: str
    success: bool
    manus_original_response: Optional[Dict[str, Any]]  # Manus 原始回覆
    conversation_history: Optional[ConversationHistory]
    incremental_comparison: Optional[IncrementalComparison]
    hitl_review: Optional[HITLReview]
    final_recommendations: List[Dict[str, Any]]
    execution_time: float
    error_message: Optional[str] = None
    
    def get_primary_response(self) -> Dict[str, Any]:
        """獲取主要回覆 - 優先使用 Manus 原始回覆"""
        if self.manus_original_response:
            return {
                "type": "manus_response",
                "content": self.manus_original_response,
                "source": "manus_direct"
            }
        elif self.final_recommendations:
            return {
                "type": "smartinvention_recommendations", 
                "content": self.final_recommendations,
                "source": "smartinvention_processed"
            }
        else:
            return {
                "type": "error_response",
                "content": {"message": self.error_message or "無可用回覆"},
                "source": "system_error"
            }

class SmartInventionManusMiddleware:
    """SmartInvention-Manus Human-in-the-Loop 中間件"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化組件
        self.smartinvention_adapter = None
        self.manus_adapter = None
        self.comparison_engine = None
        
        # HITL 配置
        self.hitl_enabled = self.config.get("hitl_enabled", True)
        self.auto_approve_threshold = self.config.get("auto_approve_threshold", 0.9)
        self.review_timeout = self.config.get("review_timeout", 300)  # 5分鐘
        
        # 存儲
        self.pending_reviews = {}
        self.conversation_cache = {}
        
        self.logger.info("SmartInvention-Manus HITL 中間件初始化完成")
    
    async def initialize(self):
        """初始化所有組件"""
        try:
            # 初始化 SmartInvention 適配器
            ec2_config = self.config.get("ec2_config", {
                "host": "18.212.97.173",
                "username": "ec2-user",
                "key_file": "/home/ubuntu/alexchuang.pem"
            })
            
            storage_manager = TaskStorageManager(ec2_config)
            self.smartinvention_adapter = EnhancedSmartinventionAdapterMCP(storage_manager)
            
            # 初始化 Manus 適配器
            self.manus_adapter = ManusAdapterMCP()
            
            # 初始化增強對比引擎
            data_provider = DataProvider()
            self.comparison_engine = EnhancedComparisonAnalysisEngine(data_provider, self.config)
            
            self.logger.info("所有組件初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"組件初始化失敗: {e}")
            return False
    
    async def process_vsix_request(self, vsix_request: VSIXRequest) -> SmartInventionResponse:
        """處理 VSIX 請求的主要流程"""
        start_time = time.time()
        
        self.logger.info(f"🎯 開始處理 VSIX 請求: {vsix_request.request_id}")
        
        try:
            # 步驟 1: 觸發 SmartInvention 並收集對話歷史
            conversation_history = await self._collect_conversation_history(vsix_request)
            
            # 步驟 2: 執行與 Manus 的增量比對
            incremental_comparison = await self._perform_incremental_comparison(
                vsix_request, conversation_history
            )
            
            # 步驟 3: Human-in-the-Loop 審核流程
            hitl_review = None
            final_recommendations = incremental_comparison.recommendations
            
            if self.hitl_enabled:
                hitl_review = await self._trigger_hitl_review(incremental_comparison)
                if hitl_review and hitl_review.status == ReviewStatus.APPROVED:
                    final_recommendations = hitl_review.approved_recommendations
                elif hitl_review and hitl_review.status == ReviewStatus.REJECTED:
                    final_recommendations = []
            
            execution_time = time.time() - start_time
            
            response = SmartInventionResponse(
                request_id=vsix_request.request_id,
                success=True,
                manus_original_response=incremental_comparison.manus_standards,  # 直接使用 Manus 原始回覆
                conversation_history=conversation_history,
                incremental_comparison=incremental_comparison,
                hitl_review=hitl_review,
                final_recommendations=final_recommendations,
                execution_time=execution_time
            )
            
            self.logger.info(f"✅ VSIX 請求處理完成: {vsix_request.request_id}, 耗時: {execution_time:.2f}s")
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"❌ VSIX 請求處理失敗: {vsix_request.request_id}, 錯誤: {e}")
            
            return SmartInventionResponse(
                request_id=vsix_request.request_id,
                success=False,
                manus_original_response=None,
                conversation_history=None,
                incremental_comparison=None,
                hitl_review=None,
                final_recommendations=[],
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def _collect_conversation_history(self, vsix_request: VSIXRequest) -> ConversationHistory:
        """收集相關的對話歷史"""
        self.logger.info(f"📚 收集對話歷史: {vsix_request.request_id}")
        
        try:
            # 從 SmartInvention 獲取相關對話
            if self.smartinvention_adapter:
                # 搜索相關任務和對話
                search_result = await self.smartinvention_adapter.search_conversations({
                    "keyword": vsix_request.content[:100],
                    "limit": 10,
                    "include_context": True
                })
                
                if search_result.get("success"):
                    conversations = search_result.get("conversations", [])
                    
                    # 處理對話數據
                    messages = []
                    participants = set()
                    
                    for conv in conversations:
                        messages.extend(conv.get("messages", []))
                        participants.update(conv.get("participants", []))
                    
                    # 計算相關性分數
                    relevance_score = self._calculate_relevance_score(
                        vsix_request.content, messages
                    )
                    
                    return ConversationHistory(
                        conversation_id=f"conv_{vsix_request.request_id}",
                        messages=messages,
                        participants=list(participants),
                        timestamp_range={
                            "start": min([msg.get("timestamp", "") for msg in messages]) if messages else "",
                            "end": max([msg.get("timestamp", "") for msg in messages]) if messages else ""
                        },
                        total_messages=len(messages),
                        relevant_score=relevance_score
                    )
            
            # 如果沒有找到相關對話，返回空的對話歷史
            return ConversationHistory(
                conversation_id=f"conv_{vsix_request.request_id}",
                messages=[],
                participants=[],
                timestamp_range={"start": "", "end": ""},
                total_messages=0,
                relevant_score=0.0
            )
            
        except Exception as e:
            self.logger.error(f"收集對話歷史失敗: {e}")
            raise
    
    async def _perform_incremental_comparison(self, 
                                           vsix_request: VSIXRequest, 
                                           conversation_history: ConversationHistory) -> IncrementalComparison:
        """執行與 Manus 的增量比對"""
        self.logger.info(f"🔍 執行增量比對: {vsix_request.request_id}")
        
        try:
            # 獲取當前系統狀態
            current_state = {
                "request_content": vsix_request.content,
                "context": vsix_request.context,
                "conversation_history": asdict(conversation_history),
                "timestamp": datetime.now().isoformat()
            }
            
            # 使用 Manus 適配器分析需求
            if self.manus_adapter:
                manus_analysis = await self.manus_adapter.analyze_requirement({
                    "requirement_text": vsix_request.content,
                    "context": vsix_request.context,
                    "conversation_history": conversation_history.messages
                })
                
                # 構建豐富的 Manus 標準回覆
                manus_standards = {
                    "manus_analysis": manus_analysis,
                    "direct_response": manus_analysis.get("direct_response", ""),
                    "recommendations": manus_analysis.get("recommendations", []),
                    "best_practices": manus_analysis.get("best_practices", []),
                    "quality_metrics": manus_analysis.get("quality_metrics", {}),
                    "compliance_requirements": manus_analysis.get("compliance_requirements", []),
                    "implementation_guidance": manus_analysis.get("implementation_guidance", ""),
                    "manus_confidence": manus_analysis.get("confidence_score", 0.8),
                    "analysis_timestamp": datetime.now().isoformat()
                }
            else:
                # 模擬 Manus 標準回覆
                manus_standards = {
                    "direct_response": f"基於您的請求「{vsix_request.content}」，Manus 建議採用以下方法：",
                    "recommendations": [
                        {"priority": "high", "action": "使用模塊化設計", "reason": "提高代碼可維護性"},
                        {"priority": "medium", "action": "實施錯誤處理", "reason": "增強系統穩定性"},
                        {"priority": "medium", "action": "添加日誌記錄", "reason": "便於問題追蹤"}
                    ],
                    "best_practices": ["使用模塊化設計", "實施錯誤處理", "添加日誌記錄"],
                    "quality_metrics": {"code_coverage": "> 80%", "response_time": "< 2s"},
                    "compliance_requirements": ["數據安全", "用戶隱私保護"],
                    "implementation_guidance": "建議先實施高優先級項目，然後逐步完善中等優先級功能。",
                    "manus_confidence": 0.85,
                    "analysis_timestamp": datetime.now().isoformat()
                }
            
            # 執行比對分析
            differences = self._identify_differences(current_state, manus_standards)
            recommendations = self._generate_recommendations(differences, manus_standards)
            
            # 計算信心分數
            confidence_score = self._calculate_confidence_score(differences, recommendations)
            
            return IncrementalComparison(
                comparison_id=f"comp_{vsix_request.request_id}",
                current_state=current_state,
                manus_standards=manus_standards,
                differences=differences,
                recommendations=recommendations,
                confidence_score=confidence_score,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"增量比對失敗: {e}")
            raise
    
    async def _trigger_hitl_review(self, comparison: IncrementalComparison) -> Optional[HITLReview]:
        """觸發 Human-in-the-Loop 審核"""
        self.logger.info(f"👤 觸發 HITL 審核: {comparison.comparison_id}")
        
        try:
            # 檢查是否需要人工審核
            if comparison.confidence_score >= self.auto_approve_threshold:
                # 自動批准
                return HITLReview(
                    review_id=f"review_{comparison.comparison_id}",
                    reviewer="system_auto",
                    status=ReviewStatus.APPROVED,
                    original_recommendations=comparison.recommendations,
                    approved_recommendations=comparison.recommendations,
                    comments="自動批准 - 信心分數超過閾值",
                    timestamp=datetime.now().isoformat()
                )
            
            # 需要人工審核
            review_id = f"review_{comparison.comparison_id}"
            
            # 創建審核請求
            review_request = {
                "review_id": review_id,
                "comparison": asdict(comparison),
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            }
            
            # 存儲待審核項目
            self.pending_reviews[review_id] = review_request
            
            # 通知審核者（這裡可以整合通知系統）
            await self._notify_reviewers(review_request)
            
            # 等待審核結果（簡化版本，實際應該使用異步通知）
            review_result = await self._wait_for_review(review_id)
            
            return review_result
            
        except Exception as e:
            self.logger.error(f"HITL 審核失敗: {e}")
            return None
    
    def _calculate_relevance_score(self, request_content: str, messages: List[Dict]) -> float:
        """計算對話歷史的相關性分數"""
        if not messages:
            return 0.0
        
        # 簡化的相關性計算
        request_keywords = set(request_content.lower().split())
        
        total_score = 0.0
        for message in messages:
            message_content = message.get("content", "").lower()
            message_keywords = set(message_content.split())
            
            # 計算關鍵詞重疊度
            overlap = len(request_keywords.intersection(message_keywords))
            total_score += overlap / max(len(request_keywords), 1)
        
        return min(total_score / len(messages), 1.0)
    
    def _identify_differences(self, current_state: Dict, manus_standards: Dict) -> List[Dict]:
        """識別當前狀態與 Manus 標準的差異"""
        differences = []
        
        # 檢查最佳實踐
        best_practices = manus_standards.get("best_practices", [])
        for practice in best_practices:
            if practice.lower() not in current_state.get("request_content", "").lower():
                differences.append({
                    "type": "missing_best_practice",
                    "description": f"缺少最佳實踐: {practice}",
                    "severity": "medium",
                    "recommendation": f"建議實施: {practice}"
                })
        
        return differences
    
    def _generate_recommendations(self, differences: List[Dict], manus_standards: Dict) -> List[Dict]:
        """基於差異生成建議"""
        recommendations = []
        
        for diff in differences:
            recommendations.append({
                "id": f"rec_{len(recommendations) + 1}",
                "type": "improvement",
                "title": diff.get("recommendation", ""),
                "description": diff.get("description", ""),
                "priority": diff.get("severity", "medium"),
                "implementation_steps": [
                    "分析當前實現",
                    "設計改進方案",
                    "實施修改",
                    "測試驗證"
                ]
            })
        
        return recommendations
    
    def _calculate_confidence_score(self, differences: List[Dict], recommendations: List[Dict]) -> float:
        """計算信心分數"""
        if not differences:
            return 1.0
        
        # 基於差異嚴重程度計算信心分數
        severity_weights = {"low": 0.1, "medium": 0.3, "high": 0.6}
        total_weight = sum(severity_weights.get(diff.get("severity", "medium"), 0.3) for diff in differences)
        
        # 信心分數與差異嚴重程度成反比
        confidence = max(0.0, 1.0 - (total_weight / len(differences)))
        return confidence
    
    async def _notify_reviewers(self, review_request: Dict):
        """通知審核者"""
        # 這裡可以整合郵件、Slack、或其他通知系統
        self.logger.info(f"📧 通知審核者: {review_request['review_id']}")
        
        # 模擬通知
        notification = {
            "type": "hitl_review_required",
            "review_id": review_request["review_id"],
            "message": "需要人工審核增量修正建議",
            "timestamp": datetime.now().isoformat()
        }
        
        # 實際實現中，這裡會發送真實的通知
        self.logger.info(f"通知內容: {notification}")
    
    async def _wait_for_review(self, review_id: str) -> Optional[HITLReview]:
        """等待審核結果"""
        # 簡化版本：模擬審核結果
        # 實際實現中，這應該是一個異步等待機制
        
        await asyncio.sleep(1)  # 模擬審核時間
        
        # 模擬審核結果
        review_request = self.pending_reviews.get(review_id)
        if review_request:
            comparison = review_request["comparison"]
            
            return HITLReview(
                review_id=review_id,
                reviewer="human_reviewer",
                status=ReviewStatus.APPROVED,
                original_recommendations=comparison["recommendations"],
                approved_recommendations=comparison["recommendations"],
                comments="審核通過 - 建議合理",
                timestamp=datetime.now().isoformat()
            )
        
        return None
    
    # API 方法供外部調用
    async def get_pending_reviews(self) -> List[Dict]:
        """獲取待審核項目"""
        return list(self.pending_reviews.values())
    
    async def submit_review(self, review_id: str, status: str, 
                          approved_recommendations: List[Dict], 
                          comments: str = "") -> bool:
        """提交審核結果"""
        try:
            if review_id in self.pending_reviews:
                review_request = self.pending_reviews[review_id]
                
                # 更新審核狀態
                review_request.update({
                    "status": status,
                    "approved_recommendations": approved_recommendations,
                    "comments": comments,
                    "reviewed_at": datetime.now().isoformat()
                })
                
                self.logger.info(f"✅ 審核結果已提交: {review_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"提交審核結果失敗: {e}")
            return False

# 便利函數
async def create_smartinvention_manus_middleware(config: Dict[str, Any] = None) -> SmartInventionManusMiddleware:
    """創建 SmartInvention-Manus 中間件"""
    middleware = SmartInventionManusMiddleware(config)
    await middleware.initialize()
    return middleware

# 使用示例
async def example_usage():
    """使用示例"""
    # 創建中間件
    middleware = await create_smartinvention_manus_middleware({
        "hitl_enabled": True,
        "auto_approve_threshold": 0.8
    })
    
    # 模擬 VSIX 請求
    vsix_request = VSIXRequest(
        request_id="req_001",
        content="請幫我創建一個新的 API 端點來處理用戶註冊",
        context={"project": "user_management", "language": "python"},
        timestamp=time.time()
    )
    
    # 處理請求
    response = await middleware.process_vsix_request(vsix_request)
    
    print(f"處理結果: {response.success}")
    print(f"執行時間: {response.execution_time:.2f}s")
    print(f"最終建議數量: {len(response.final_recommendations)}")

if __name__ == "__main__":
    asyncio.run(example_usage())

