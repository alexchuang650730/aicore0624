"""
增強的上下文管理器 (Enhanced Context Manager)
專門處理代碼和對話上下文，優化上下文長度和相關性
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from .data_provider import DataProvider, UserContext, ComparisonContext
    from .plugin_data_access import PluginDataAccess, CodeSnapshot
except ImportError:
    from data_provider import DataProvider, UserContext, ComparisonContext
    from plugin_data_access import PluginDataAccess, CodeSnapshot

logger = logging.getLogger(__name__)

class ContextType(Enum):
    """上下文類型"""
    CODE = "code"
    CONVERSATION = "conversation"
    MIXED = "mixed"
    COMPREHENSIVE = "comprehensive"

class ContextPriority(Enum):
    """上下文優先級"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ContextRequest:
    """上下文請求"""
    user_id: str
    request_id: str
    context_type: ContextType
    priority: ContextPriority = ContextPriority.MEDIUM
    max_context_length: int = 8000  # 字符數
    include_recent_only: bool = False
    time_window_hours: int = 24
    custom_filters: Optional[Dict[str, Any]] = None

@dataclass
class ContextSegment:
    """上下文片段"""
    segment_id: str
    content: str
    context_type: ContextType
    relevance_score: float
    timestamp: datetime
    source: str
    metadata: Dict[str, Any]
    token_count: int

@dataclass
class OptimizedContext:
    """優化後的上下文"""
    request_id: str
    user_id: str
    total_segments: int
    total_tokens: int
    segments: List[ContextSegment]
    optimization_strategy: str
    relevance_threshold: float
    context_summary: str
    generation_time: float
    metadata: Dict[str, Any]

class EnhancedContextManager:
    """增強的上下文管理器"""
    
    def __init__(self, data_provider: DataProvider = None, config: Dict[str, Any] = None):
        """
        初始化增強的上下文管理器
        
        Args:
            data_provider: 數據提供者實例
            config: 配置參數
        """
        self.data_provider = data_provider or DataProvider()
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 配置參數
        self.default_max_context_length = self.config.get('max_context_length', 8000)
        self.relevance_threshold = self.config.get('relevance_threshold', 0.3)
        self.max_segments = self.config.get('max_segments', 50)
        self.token_estimation_ratio = self.config.get('token_estimation_ratio', 4)  # 字符:token 比例
        
        # 上下文優化策略
        self.optimization_strategies = {
            'relevance_based': self._optimize_by_relevance,
            'time_based': self._optimize_by_time,
            'mixed_strategy': self._optimize_mixed,
            'comprehensive': self._optimize_comprehensive
        }
        
        self.logger.info("Enhanced Context Manager initialized")
    
    async def get_optimized_context(self, request: ContextRequest) -> OptimizedContext:
        """
        獲取優化後的上下文
        
        Args:
            request: 上下文請求
            
        Returns:
            OptimizedContext: 優化後的上下文
        """
        start_time = time.time()
        
        self.logger.info(f"Getting optimized context for user {request.user_id}, "
                        f"type: {request.context_type.value}, priority: {request.priority.value}")
        
        try:
            # 獲取原始上下文數據
            user_context = await self.data_provider.get_user_full_context(request.user_id)
            
            # 生成上下文片段
            segments = await self._generate_context_segments(request, user_context)
            
            # 選擇優化策略
            optimization_strategy = self._select_optimization_strategy(request, segments)
            
            # 執行上下文優化
            optimized_segments = await self.optimization_strategies[optimization_strategy](
                request, segments
            )
            
            # 計算總 token 數
            total_tokens = sum(segment.token_count for segment in optimized_segments)
            
            # 生成上下文摘要
            context_summary = self._generate_context_summary(optimized_segments)
            
            generation_time = time.time() - start_time
            
            optimized_context = OptimizedContext(
                request_id=request.request_id,
                user_id=request.user_id,
                total_segments=len(optimized_segments),
                total_tokens=total_tokens,
                segments=optimized_segments,
                optimization_strategy=optimization_strategy,
                relevance_threshold=self.relevance_threshold,
                context_summary=context_summary,
                generation_time=generation_time,
                metadata={
                    "original_segments_count": len(segments),
                    "compression_ratio": len(optimized_segments) / len(segments) if segments else 0,
                    "context_type": request.context_type.value,
                    "priority": request.priority.value,
                    "user_context_score": user_context.context_score
                }
            )
            
            self.logger.info(f"Context optimization completed: {len(optimized_segments)} segments, "
                           f"{total_tokens} tokens, strategy: {optimization_strategy}, "
                           f"time: {generation_time:.2f}s")
            
            return optimized_context
            
        except Exception as e:
            generation_time = time.time() - start_time
            self.logger.error(f"Failed to get optimized context: {e}")
            
            return OptimizedContext(
                request_id=request.request_id,
                user_id=request.user_id,
                total_segments=0,
                total_tokens=0,
                segments=[],
                optimization_strategy="error",
                relevance_threshold=0.0,
                context_summary=f"Error: {str(e)}",
                generation_time=generation_time,
                metadata={"error": str(e)}
            )
    
    async def _generate_context_segments(self, request: ContextRequest, 
                                       user_context: UserContext) -> List[ContextSegment]:
        """生成上下文片段"""
        
        segments = []
        
        # 處理對話上下文
        if request.context_type in [ContextType.CONVERSATION, ContextType.MIXED, ContextType.COMPREHENSIVE]:
            conversation_segments = await self._generate_conversation_segments(request, user_context)
            segments.extend(conversation_segments)
        
        # 處理代碼上下文
        if request.context_type in [ContextType.CODE, ContextType.MIXED, ContextType.COMPREHENSIVE]:
            code_segments = await self._generate_code_segments(request, user_context)
            segments.extend(code_segments)
        
        # 按時間戳排序
        segments.sort(key=lambda x: x.timestamp, reverse=True)
        
        return segments
    
    async def _generate_conversation_segments(self, request: ContextRequest, 
                                            user_context: UserContext) -> List[ContextSegment]:
        """生成對話上下文片段"""
        
        segments = []
        
        for i, conversation in enumerate(user_context.conversations):
            # 時間窗口過濾
            if request.include_recent_only:
                conv_time = datetime.fromisoformat(conversation.timestamp_range["start"].replace('Z', '+00:00'))
                if datetime.now() - conv_time > timedelta(hours=request.time_window_hours):
                    continue
            
            # 為每個對話創建片段
            for j, message in enumerate(conversation.messages):
                content = message.get('content', '')
                if not content:
                    continue
                
                segment = ContextSegment(
                    segment_id=f"conv_{conversation.conversation_id}_{j}",
                    content=content,
                    context_type=ContextType.CONVERSATION,
                    relevance_score=conversation.relevant_score,
                    timestamp=datetime.fromisoformat(conversation.timestamp_range["start"].replace('Z', '+00:00')),
                    source=f"conversation_{conversation.conversation_id}",
                    metadata={
                        "conversation_id": conversation.conversation_id,
                        "message_index": j,
                        "role": message.get('role', 'unknown'),
                        "total_messages": conversation.total_messages,
                        "participants": conversation.participants
                    },
                    token_count=len(content) // self.token_estimation_ratio
                )
                
                segments.append(segment)
        
        return segments
    
    async def _generate_code_segments(self, request: ContextRequest, 
                                    user_context: UserContext) -> List[ContextSegment]:
        """生成代碼上下文片段"""
        
        segments = []
        
        if not user_context.code_snapshot:
            return segments
        
        code_snapshot = user_context.code_snapshot
        
        # 為每個代碼文件創建片段
        for i, code_file in enumerate(code_snapshot.files):
            # 時間窗口過濾
            if request.include_recent_only and code_file.last_modified:
                if datetime.now() - code_file.last_modified > timedelta(hours=request.time_window_hours):
                    continue
            
            # 獲取文件內容
            file_content = await self.data_provider.plugin_access.get_file_content(code_file.content_hash)
            if not file_content:
                continue
            
            # 計算相關性分數（基於文件類型、大小等）
            relevance_score = self._calculate_code_relevance(code_file, request)
            
            segment = ContextSegment(
                segment_id=f"code_{code_file.id}",
                content=f"File: {code_file.file_path}\n\n{file_content}",
                context_type=ContextType.CODE,
                relevance_score=relevance_score,
                timestamp=code_file.last_modified or datetime.now(),
                source=f"code_file_{code_file.id}",
                metadata={
                    "file_id": code_file.id,
                    "file_path": code_file.file_path,
                    "file_size": code_file.file_size,
                    "status": code_file.status,
                    "project_id": code_file.project_id,
                    "project_name": code_snapshot.project.name,
                    "language": code_snapshot.project.language
                },
                token_count=len(file_content) // self.token_estimation_ratio
            )
            
            segments.append(segment)
        
        return segments
    
    def _calculate_code_relevance(self, code_file, request: ContextRequest) -> float:
        """計算代碼文件的相關性分數"""
        
        relevance = 0.5  # 基礎分數
        
        # 基於文件狀態調整
        if code_file.status == 'modified':
            relevance += 0.3
        elif code_file.status == 'added':
            relevance += 0.2
        
        # 基於文件大小調整（適中大小的文件更相關）
        if 100 < code_file.file_size < 10000:
            relevance += 0.1
        elif code_file.file_size > 50000:
            relevance -= 0.1
        
        # 基於文件類型調整
        file_ext = code_file.file_path.split('.')[-1].lower()
        important_extensions = ['py', 'js', 'ts', 'java', 'cpp', 'c', 'go', 'rs']
        if file_ext in important_extensions:
            relevance += 0.1
        
        return min(relevance, 1.0)
    
    def _select_optimization_strategy(self, request: ContextRequest, 
                                    segments: List[ContextSegment]) -> str:
        """選擇優化策略"""
        
        if request.priority == ContextPriority.CRITICAL:
            return 'comprehensive'
        elif request.context_type == ContextType.CODE:
            return 'relevance_based'
        elif request.context_type == ContextType.CONVERSATION:
            return 'time_based'
        elif request.include_recent_only:
            return 'time_based'
        else:
            return 'mixed_strategy'
    
    async def _optimize_by_relevance(self, request: ContextRequest, 
                                   segments: List[ContextSegment]) -> List[ContextSegment]:
        """基於相關性優化"""
        
        # 過濾低相關性片段
        filtered_segments = [s for s in segments if s.relevance_score >= self.relevance_threshold]
        
        # 按相關性排序
        filtered_segments.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # 限制長度
        return self._limit_context_length(filtered_segments, request.max_context_length)
    
    async def _optimize_by_time(self, request: ContextRequest, 
                              segments: List[ContextSegment]) -> List[ContextSegment]:
        """基於時間優化"""
        
        # 按時間排序（最新的優先）
        segments.sort(key=lambda x: x.timestamp, reverse=True)
        
        # 限制長度
        return self._limit_context_length(segments, request.max_context_length)
    
    async def _optimize_mixed(self, request: ContextRequest, 
                            segments: List[ContextSegment]) -> List[ContextSegment]:
        """混合策略優化"""
        
        # 計算綜合分數（相關性 + 時間新鮮度）
        now = datetime.now()
        for segment in segments:
            time_diff = (now - segment.timestamp).total_seconds() / 3600  # 小時
            time_score = max(0, 1 - time_diff / 168)  # 一週內的時間分數
            segment.relevance_score = (segment.relevance_score * 0.7) + (time_score * 0.3)
        
        # 按綜合分數排序
        segments.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # 限制長度
        return self._limit_context_length(segments, request.max_context_length)
    
    async def _optimize_comprehensive(self, request: ContextRequest, 
                                    segments: List[ContextSegment]) -> List[ContextSegment]:
        """綜合策略優化"""
        
        # 確保包含不同類型的上下文
        conversation_segments = [s for s in segments if s.context_type == ContextType.CONVERSATION]
        code_segments = [s for s in segments if s.context_type == ContextType.CODE]
        
        # 分別優化不同類型的片段
        optimized_conversations = await self._optimize_by_time(request, conversation_segments)
        optimized_code = await self._optimize_by_relevance(request, code_segments)
        
        # 合併並平衡
        max_conv_length = request.max_context_length // 2
        max_code_length = request.max_context_length // 2
        
        final_conversations = self._limit_context_length(optimized_conversations, max_conv_length)
        final_code = self._limit_context_length(optimized_code, max_code_length)
        
        # 合併結果
        result = final_conversations + final_code
        result.sort(key=lambda x: x.timestamp, reverse=True)
        
        return result
    
    def _limit_context_length(self, segments: List[ContextSegment], 
                            max_length: int) -> List[ContextSegment]:
        """限制上下文長度"""
        
        result = []
        current_length = 0
        
        for segment in segments:
            if current_length + segment.token_count <= max_length:
                result.append(segment)
                current_length += segment.token_count
            else:
                # 如果單個片段太長，嘗試截斷
                if not result and segment.token_count > max_length:
                    truncated_content = segment.content[:max_length * self.token_estimation_ratio]
                    truncated_segment = ContextSegment(
                        segment_id=segment.segment_id + "_truncated",
                        content=truncated_content + "...[truncated]",
                        context_type=segment.context_type,
                        relevance_score=segment.relevance_score,
                        timestamp=segment.timestamp,
                        source=segment.source,
                        metadata={**segment.metadata, "truncated": True},
                        token_count=max_length
                    )
                    result.append(truncated_segment)
                break
        
        return result
    
    def _generate_context_summary(self, segments: List[ContextSegment]) -> str:
        """生成上下文摘要"""
        
        if not segments:
            return "無可用上下文"
        
        conversation_count = len([s for s in segments if s.context_type == ContextType.CONVERSATION])
        code_count = len([s for s in segments if s.context_type == ContextType.CODE])
        
        summary_parts = []
        
        if conversation_count > 0:
            summary_parts.append(f"{conversation_count} 個對話片段")
        
        if code_count > 0:
            summary_parts.append(f"{code_count} 個代碼片段")
        
        avg_relevance = sum(s.relevance_score for s in segments) / len(segments)
        
        summary = f"包含 {', '.join(summary_parts)}，平均相關性: {avg_relevance:.2f}"
        
        # 添加時間範圍信息
        if segments:
            latest = max(s.timestamp for s in segments)
            earliest = min(s.timestamp for s in segments)
            time_span = (latest - earliest).days
            if time_span > 0:
                summary += f"，時間跨度: {time_span} 天"
        
        return summary
    
    async def get_context_statistics(self, user_id: str) -> Dict[str, Any]:
        """獲取用戶上下文統計信息"""
        
        try:
            user_context = await self.data_provider.get_user_full_context(user_id)
            
            stats = {
                "user_id": user_id,
                "context_score": user_context.context_score,
                "conversations": {
                    "count": len(user_context.conversations),
                    "total_messages": sum(conv.total_messages for conv in user_context.conversations),
                    "avg_relevance": sum(conv.relevant_score for conv in user_context.conversations) / len(user_context.conversations) if user_context.conversations else 0
                },
                "code_context": {
                    "available": user_context.code_snapshot is not None,
                    "file_count": user_context.code_snapshot.file_count if user_context.code_snapshot else 0,
                    "total_size": user_context.code_snapshot.total_size if user_context.code_snapshot else 0,
                    "project_name": user_context.code_snapshot.project.name if user_context.code_snapshot else None
                },
                "request_history": {
                    "count": len(user_context.request_history)
                },
                "last_activity": user_context.last_activity.isoformat(),
                "generated_at": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get context statistics: {e}")
            return {"user_id": user_id, "error": str(e)}
    
    async def optimize_context_for_request(self, user_id: str, request_content: str, 
                                         max_length: int = None) -> OptimizedContext:
        """為特定請求優化上下文"""
        
        # 分析請求內容以確定最佳上下文類型
        context_type = self._analyze_request_context_type(request_content)
        
        # 確定優先級
        priority = self._determine_request_priority(request_content)
        
        request = ContextRequest(
            user_id=user_id,
            request_id=f"req_{int(time.time())}",
            context_type=context_type,
            priority=priority,
            max_context_length=max_length or self.default_max_context_length,
            include_recent_only=True,
            time_window_hours=48  # 48小時內的上下文
        )
        
        return await self.get_optimized_context(request)
    
    def _analyze_request_context_type(self, request_content: str) -> ContextType:
        """分析請求內容以確定上下文類型"""
        
        content_lower = request_content.lower()
        
        code_keywords = ['代碼', 'code', '函數', 'function', '類', 'class', '方法', 'method', 
                        '變量', 'variable', '算法', 'algorithm', '調試', 'debug', '錯誤', 'error']
        
        conversation_keywords = ['討論', 'discuss', '解釋', 'explain', '建議', 'suggest', 
                               '意見', 'opinion', '想法', 'idea', '問題', 'question']
        
        code_score = sum(1 for keyword in code_keywords if keyword in content_lower)
        conversation_score = sum(1 for keyword in conversation_keywords if keyword in content_lower)
        
        if code_score > conversation_score * 1.5:
            return ContextType.CODE
        elif conversation_score > code_score * 1.5:
            return ContextType.CONVERSATION
        else:
            return ContextType.MIXED
    
    def _determine_request_priority(self, request_content: str) -> ContextPriority:
        """確定請求優先級"""
        
        content_lower = request_content.lower()
        
        high_priority_keywords = ['緊急', 'urgent', '重要', 'important', '關鍵', 'critical', 
                                '錯誤', 'error', '故障', 'failure', '問題', 'problem']
        
        if any(keyword in content_lower for keyword in high_priority_keywords):
            return ContextPriority.HIGH
        elif len(request_content) > 500:  # 長請求通常更重要
            return ContextPriority.MEDIUM
        else:
            return ContextPriority.LOW

