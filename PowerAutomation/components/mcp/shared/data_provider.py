"""
數據提供者抽象層 (Data Provider Abstraction Layer)
負責聚合來自 Manus 和插件數據庫的數據，為對比引擎提供統一的數據接口
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

try:
    from .plugin_data_access import PluginDataAccess, CodeSnapshot, CodeProject, CodeFile, SyncSession
except ImportError:
    from plugin_data_access import PluginDataAccess, CodeSnapshot, CodeProject, CodeFile, SyncSession

logger = logging.getLogger(__name__)

@dataclass
class ConversationHistory:
    """對話歷史數據模型（與 Manus 兼容）"""
    conversation_id: str
    messages: List[Dict[str, Any]]
    participants: List[str]
    timestamp_range: Dict[str, str]
    total_messages: int
    relevant_score: float
    context: Optional[Dict[str, Any]] = None

@dataclass
class UserContext:
    """用戶上下文數據模型"""
    user_id: str
    conversations: List[ConversationHistory]
    code_snapshot: Optional[CodeSnapshot]
    request_history: List[Dict[str, Any]]
    last_activity: datetime
    context_score: float = 0.0

@dataclass
class ComparisonContext:
    """對比上下文數據模型"""
    user_context: UserContext
    current_request: Dict[str, Any]
    manus_standards: Dict[str, Any]
    comparison_metadata: Dict[str, Any]

class ManusDataAccessMock:
    """Manus 數據訪問模擬類（用於開發階段）"""
    
    async def get_conversations(self, user_id: str, timestamp: float = None) -> List[ConversationHistory]:
        """獲取用戶對話歷史"""
        # 模擬數據，實際應該連接到真實的 Manus 數據庫
        mock_conversations = [
            ConversationHistory(
                conversation_id=f"conv_{user_id}_001",
                messages=[
                    {"role": "user", "content": "請幫我生成一個用戶登錄功能的測試案例"},
                    {"role": "assistant", "content": "我來為您生成用戶登錄功能的測試案例..."}
                ],
                participants=[user_id, "assistant"],
                timestamp_range={"start": "2025-06-25T10:00:00Z", "end": "2025-06-25T10:05:00Z"},
                total_messages=2,
                relevant_score=0.85,
                context={"topic": "testing", "domain": "authentication"}
            ),
            ConversationHistory(
                conversation_id=f"conv_{user_id}_002",
                messages=[
                    {"role": "user", "content": "如何設計一個 RESTful API 來管理用戶數據？"},
                    {"role": "assistant", "content": "設計 RESTful API 需要考慮以下幾個方面..."}
                ],
                participants=[user_id, "assistant"],
                timestamp_range={"start": "2025-06-25T11:00:00Z", "end": "2025-06-25T11:10:00Z"},
                total_messages=2,
                relevant_score=0.75,
                context={"topic": "api_design", "domain": "backend"}
            )
        ]
        
        if timestamp:
            # 過濾時間戳之前的對話
            cutoff_time = datetime.fromtimestamp(timestamp).isoformat() + "Z"
            mock_conversations = [
                conv for conv in mock_conversations 
                if conv.timestamp_range["start"] <= cutoff_time
            ]
        
        return mock_conversations
    
    async def get_analysis_results(self, user_id: str, request_id: str) -> Dict[str, Any]:
        """獲取 Manus 分析結果"""
        return {
            "analysis_id": f"analysis_{request_id}",
            "user_id": user_id,
            "request_id": request_id,
            "confidence_score": 0.82,
            "recommendations": [
                "建議使用 JWT 進行身份驗證",
                "實施輸入驗證和清理",
                "添加速率限制保護"
            ],
            "best_practices": [
                "使用 HTTPS 加密傳輸",
                "實施適當的錯誤處理",
                "記錄安全相關事件"
            ],
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    async def get_standards(self) -> Dict[str, Any]:
        """獲取 Manus 標準"""
        return {
            "coding_standards": {
                "python": {
                    "style_guide": "PEP 8",
                    "naming_convention": "snake_case",
                    "max_line_length": 88
                },
                "javascript": {
                    "style_guide": "Airbnb",
                    "naming_convention": "camelCase",
                    "max_line_length": 100
                }
            },
            "security_standards": {
                "authentication": ["JWT", "OAuth2", "Session-based"],
                "encryption": ["AES-256", "RSA-2048"],
                "input_validation": ["sanitization", "type_checking", "length_limits"]
            },
            "testing_standards": {
                "coverage_threshold": 80,
                "test_types": ["unit", "integration", "e2e"],
                "frameworks": {
                    "python": ["pytest", "unittest"],
                    "javascript": ["jest", "mocha", "cypress"]
                }
            }
        }

class DataProvider:
    """數據提供者類 - 聚合多個數據源"""
    
    def __init__(self, manus_data_access=None, plugin_data_access: PluginDataAccess = None):
        """
        初始化數據提供者
        
        Args:
            manus_data_access: Manus 數據訪問實例
            plugin_data_access: 插件數據訪問實例
        """
        self.manus_access = manus_data_access or ManusDataAccessMock()
        self.plugin_access = plugin_data_access or PluginDataAccess()
        
        logger.info("DataProvider initialized with Manus and Plugin data access")
    
    async def get_user_full_context(self, user_id: str, timestamp: float = None) -> UserContext:
        """
        獲取用戶的完整上下文
        
        Args:
            user_id: 用戶 ID
            timestamp: 時間戳，如果為 None 則獲取最新的
            
        Returns:
            UserContext: 用戶上下文對象
        """
        try:
            # 並行獲取數據
            conversations_task = self.manus_access.get_conversations(user_id, timestamp)
            code_snapshot_task = self.plugin_access.get_user_code_snapshot(user_id, timestamp)
            
            conversations, code_snapshot = await asyncio.gather(
                conversations_task, 
                code_snapshot_task,
                return_exceptions=True
            )
            
            # 處理異常
            if isinstance(conversations, Exception):
                logger.error(f"Failed to get conversations: {conversations}")
                conversations = []
            
            if isinstance(code_snapshot, Exception):
                logger.error(f"Failed to get code snapshot: {code_snapshot}")
                code_snapshot = None
            
            # 獲取請求歷史（模擬）
            request_history = await self._get_request_history(user_id, timestamp)
            
            # 計算上下文分數
            context_score = self._calculate_context_score(conversations, code_snapshot, request_history)
            
            user_context = UserContext(
                user_id=user_id,
                conversations=conversations or [],
                code_snapshot=code_snapshot,
                request_history=request_history,
                last_activity=datetime.now(),
                context_score=context_score
            )
            
            logger.info(f"Retrieved full context for user {user_id}: "
                       f"{len(conversations or [])} conversations, "
                       f"{'code snapshot available' if code_snapshot else 'no code snapshot'}, "
                       f"context score: {context_score:.2f}")
            
            return user_context
            
        except Exception as e:
            logger.error(f"Failed to get user full context: {e}")
            # 返回空的上下文而不是拋出異常
            return UserContext(
                user_id=user_id,
                conversations=[],
                code_snapshot=None,
                request_history=[],
                last_activity=datetime.now(),
                context_score=0.0
            )
    
    async def get_comparison_data(self, user_id: str, request_id: str) -> ComparisonContext:
        """
        獲取對比分析所需的數據
        
        Args:
            user_id: 用戶 ID
            request_id: 請求 ID
            
        Returns:
            ComparisonContext: 對比上下文對象
        """
        try:
            # 獲取用戶上下文
            user_context = await self.get_user_full_context(user_id)
            
            # 獲取當前請求信息（模擬）
            current_request = await self._get_current_request(request_id)
            
            # 獲取 Manus 標準
            manus_standards = await self.manus_access.get_standards()
            
            # 構建對比元數據
            comparison_metadata = {
                "comparison_id": f"comp_{request_id}_{int(time.time())}",
                "user_id": user_id,
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "context_quality": user_context.context_score,
                "data_sources": {
                    "manus_conversations": len(user_context.conversations),
                    "code_files": user_context.code_snapshot.file_count if user_context.code_snapshot else 0,
                    "request_history": len(user_context.request_history)
                }
            }
            
            return ComparisonContext(
                user_context=user_context,
                current_request=current_request,
                manus_standards=manus_standards,
                comparison_metadata=comparison_metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to get comparison data: {e}")
            raise
    
    async def save_user_request_data(self, user_request: Dict[str, Any]) -> str:
        """
        保存用戶請求數據
        
        Args:
            user_request: 用戶請求對象
            
        Returns:
            str: 保存操作的結果 ID
        """
        try:
            user_id = user_request.get('metadata', {}).get('user_id')
            if not user_id:
                raise ValueError("User ID not found in request metadata")
            
            # 檢查是否包含代碼同步數據
            context = user_request.get('context', {})
            code_sync_data = context.get('code_sync_data')
            
            result_ids = []
            
            if code_sync_data:
                # 保存代碼同步數據
                sync_session_id = await self.plugin_access.save_code_sync_data(user_id, code_sync_data)
                result_ids.append(f"sync_session:{sync_session_id}")
                
                # 保存請求上下文關聯
                await self._save_request_context(user_request, sync_session_id)
                result_ids.append(f"request_context:{user_request.get('id')}")
            
            # 保存到 Manus（如果需要）
            # manus_result = await self.manus_access.save_request(user_request)
            # result_ids.append(f"manus:{manus_result}")
            
            logger.info(f"User request data saved: {', '.join(result_ids)}")
            return ','.join(result_ids)
            
        except Exception as e:
            logger.error(f"Failed to save user request data: {e}")
            raise
    
    async def search_user_context(self, user_id: str, query: str, context_type: str = "all") -> Dict[str, Any]:
        """
        搜索用戶上下文
        
        Args:
            user_id: 用戶 ID
            query: 搜索查詢
            context_type: 上下文類型 ("conversations", "code", "all")
            
        Returns:
            Dict: 搜索結果
        """
        try:
            results = {
                "query": query,
                "user_id": user_id,
                "context_type": context_type,
                "results": {
                    "conversations": [],
                    "code_files": [],
                    "total_matches": 0
                },
                "search_time": time.time()
            }
            
            if context_type in ["conversations", "all"]:
                # 搜索對話歷史
                conversations = await self.manus_access.get_conversations(user_id)
                conversation_matches = self._search_conversations(conversations, query)
                results["results"]["conversations"] = conversation_matches
            
            if context_type in ["code", "all"]:
                # 搜索代碼文件
                code_matches = await self.plugin_access.search_code_files(user_id, query)
                results["results"]["code_files"] = code_matches
            
            # 計算總匹配數
            results["results"]["total_matches"] = (
                len(results["results"]["conversations"]) + 
                len(results["results"]["code_files"])
            )
            
            results["search_time"] = time.time() - results["search_time"]
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search user context: {e}")
            return {
                "query": query,
                "user_id": user_id,
                "context_type": context_type,
                "results": {"conversations": [], "code_files": [], "total_matches": 0},
                "error": str(e)
            }
    
    async def get_context_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        獲取用戶上下文統計信息
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            Dict: 統計信息
        """
        try:
            # 獲取對話統計
            conversations = await self.manus_access.get_conversations(user_id)
            conversation_stats = {
                "total_conversations": len(conversations),
                "total_messages": sum(conv.total_messages for conv in conversations),
                "avg_relevance_score": sum(conv.relevant_score for conv in conversations) / len(conversations) if conversations else 0
            }
            
            # 獲取代碼統計
            projects = await self.plugin_access.get_user_projects(user_id)
            code_stats = {
                "total_projects": len(projects),
                "total_files": sum(p.get('file_count', 0) for p in projects),
                "total_size": sum(p.get('total_size', 0) for p in projects)
            }
            
            # 獲取最新活動
            code_snapshot = await self.plugin_access.get_user_code_snapshot(user_id)
            last_code_activity = code_snapshot.sync_session.created_at if code_snapshot else None
            
            return {
                "user_id": user_id,
                "conversation_stats": conversation_stats,
                "code_stats": code_stats,
                "last_conversation": conversations[0].timestamp_range["end"] if conversations else None,
                "last_code_activity": last_code_activity.isoformat() if last_code_activity else None,
                "context_completeness": self._calculate_context_completeness(conversation_stats, code_stats),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get context statistics: {e}")
            return {"user_id": user_id, "error": str(e)}
    
    def _calculate_context_score(self, conversations: List[ConversationHistory], 
                                code_snapshot: Optional[CodeSnapshot], 
                                request_history: List[Dict[str, Any]]) -> float:
        """計算上下文分數"""
        score = 0.0
        
        # 對話質量分數 (40%)
        if conversations:
            avg_relevance = sum(conv.relevant_score for conv in conversations) / len(conversations)
            conversation_score = min(len(conversations) / 10, 1.0) * avg_relevance
            score += conversation_score * 0.4
        
        # 代碼上下文分數 (40%)
        if code_snapshot:
            file_score = min(code_snapshot.file_count / 50, 1.0)
            size_score = min(code_snapshot.total_size / (1024 * 1024), 1.0)  # 1MB 為滿分
            code_score = (file_score + size_score) / 2
            score += code_score * 0.4
        
        # 請求歷史分數 (20%)
        if request_history:
            history_score = min(len(request_history) / 20, 1.0)
            score += history_score * 0.2
        
        return min(score, 1.0)
    
    def _calculate_context_completeness(self, conversation_stats: Dict, code_stats: Dict) -> float:
        """計算上下文完整性"""
        completeness = 0.0
        
        # 對話完整性
        if conversation_stats["total_conversations"] > 0:
            completeness += 0.5
        
        # 代碼完整性
        if code_stats["total_projects"] > 0:
            completeness += 0.5
        
        return completeness
    
    def _search_conversations(self, conversations: List[ConversationHistory], query: str) -> List[Dict[str, Any]]:
        """搜索對話歷史"""
        matches = []
        query_lower = query.lower()
        
        for conv in conversations:
            for message in conv.messages:
                if query_lower in message.get('content', '').lower():
                    matches.append({
                        "conversation_id": conv.conversation_id,
                        "message_content": message.get('content', '')[:200],
                        "relevance_score": conv.relevant_score,
                        "timestamp": conv.timestamp_range["start"]
                    })
                    break  # 只取第一個匹配的消息
        
        return matches
    
    async def _get_request_history(self, user_id: str, timestamp: float = None) -> List[Dict[str, Any]]:
        """獲取請求歷史（模擬）"""
        # 實際實現應該從數據庫獲取
        return [
            {
                "request_id": f"req_{user_id}_001",
                "content": "請幫我生成一個用戶登錄功能",
                "timestamp": "2025-06-25T09:00:00Z",
                "status": "completed"
            },
            {
                "request_id": f"req_{user_id}_002",
                "content": "如何優化數據庫查詢性能",
                "timestamp": "2025-06-25T10:30:00Z",
                "status": "completed"
            }
        ]
    
    async def _get_current_request(self, request_id: str) -> Dict[str, Any]:
        """獲取當前請求信息（模擬）"""
        return {
            "request_id": request_id,
            "content": "請分析這個代碼的安全性問題",
            "timestamp": datetime.now().isoformat(),
            "status": "processing",
            "metadata": {
                "priority": "normal",
                "source": "vscode_plugin"
            }
        }
    
    async def _save_request_context(self, user_request: Dict[str, Any], sync_session_id: str):
        """保存請求上下文關聯"""
        # 實際實現應該保存到數據庫
        logger.info(f"Request context saved: {user_request.get('id')} -> {sync_session_id}")
        pass

