"""
數據提供者抽象層 (Data Provider Abstraction Layer)
負責聚合來自 Manus 和插件數據庫的數據，為對比引擎提供統一的數據接口
Version: 2.1.0 - 集成真實Manus數據抓取
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

# 導入 SmartinventionAdapterMCP
try:
    from ...smartinvention_mcp.main import SmartinventionAdapterMCP
except ImportError:
    # 回退導入
    SmartinventionAdapterMCP = None

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

class ManusDataAccess:
    """真實的 Manus 數據訪問類 - 使用 SmartinventionAdapterMCP"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化 Manus 數據訪問
        
        Args:
            config: Manus 配置
        """
        self.config = config or {}
        self.smartinvention_mcp = None
        self.initialized = False
        
        # 如果 SmartinventionAdapterMCP 可用，則初始化
        if SmartinventionAdapterMCP:
            self.smartinvention_mcp = SmartinventionAdapterMCP(config)
    
    async def initialize(self) -> bool:
        """初始化 Manus 數據訪問"""
        try:
            if self.smartinvention_mcp:
                result = await self.smartinvention_mcp.initialize()
                self.initialized = result.get("success", False)
                if self.initialized:
                    logger.info("ManusDataAccess 初始化成功，使用真實 Manus 數據")
                else:
                    logger.warning("ManusDataAccess 初始化失敗，將使用回退模式")
            else:
                logger.warning("SmartinventionAdapterMCP 不可用，使用回退模式")
                self.initialized = False
            
            return self.initialized
            
        except Exception as e:
            logger.error(f"ManusDataAccess 初始化失敗: {e}")
            self.initialized = False
            return False
    
    async def get_conversations(self, user_id: str, timestamp: float = None) -> List[ConversationHistory]:
        """獲取用戶對話歷史"""
        try:
            if not self.initialized or not self.smartinvention_mcp:
                return await self._get_fallback_conversations(user_id, timestamp)
            
            # 從真實 Manus 獲取對話數據
            result = await self.smartinvention_mcp.handle_request("get_conversations", {
                "user_id": user_id,
                "timestamp": timestamp,
                "limit": 50
            })
            
            if not result.get("success", True):
                logger.warning(f"獲取 Manus 對話失敗: {result.get('error')}")
                return await self._get_fallback_conversations(user_id, timestamp)
            
            conversations_data = result.get("conversations", [])
            
            # 轉換為 ConversationHistory 對象
            conversations = []
            for conv_data in conversations_data:
                conversation = ConversationHistory(
                    conversation_id=conv_data.get("id", f"conv_{user_id}_{len(conversations)}"),
                    messages=conv_data.get("messages", []),
                    participants=conv_data.get("participants", [user_id]),
                    timestamp_range={
                        "start": conv_data.get("timestamp", datetime.now().isoformat()),
                        "end": conv_data.get("timestamp", datetime.now().isoformat())
                    },
                    total_messages=len(conv_data.get("messages", [])),
                    relevant_score=conv_data.get("relevant_score", 0.8),
                    context=conv_data.get("metadata", {})
                )
                conversations.append(conversation)
            
            logger.info(f"從 Manus 獲取了 {len(conversations)} 個對話記錄")
            return conversations
            
        except Exception as e:
            logger.error(f"獲取 Manus 對話失敗: {e}")
            return await self._get_fallback_conversations(user_id, timestamp)
    
    async def get_analysis_results(self, user_id: str, request_id: str) -> Dict[str, Any]:
        """獲取 Manus 分析結果"""
        try:
            if not self.initialized or not self.smartinvention_mcp:
                return await self._get_fallback_analysis(user_id, request_id)
            
            # 從真實 Manus 獲取分析數據
            result = await self.smartinvention_mcp.handle_request("get_analysis", {
                "user_id": user_id,
                "request_id": request_id
            })
            
            if result.get("success", True):
                return result.get("analysis", {})
            else:
                return await self._get_fallback_analysis(user_id, request_id)
                
        except Exception as e:
            logger.error(f"獲取 Manus 分析失敗: {e}")
            return await self._get_fallback_analysis(user_id, request_id)
    
    async def get_standards(self) -> Dict[str, Any]:
        """獲取 Manus 標準"""
        try:
            if not self.initialized or not self.smartinvention_mcp:
                return await self._get_fallback_standards()
            
            # 從真實 Manus 獲取標準數據
            result = await self.smartinvention_mcp.handle_request("get_manus_standards", {})
            
            if result.get("success", True):
                standards = result.get("standards", {})
                logger.info(f"從 Manus 獲取標準數據，包含 {len(standards)} 個類別")
                return standards
            else:
                logger.warning("獲取 Manus 標準失敗，使用回退標準")
                return await self._get_fallback_standards()
                
        except Exception as e:
            logger.error(f"獲取 Manus 標準失敗: {e}")
            return await self._get_fallback_standards()
    
    async def _get_fallback_conversations(self, user_id: str, timestamp: float = None) -> List[ConversationHistory]:
        """回退對話數據"""
        mock_conversations = [
            ConversationHistory(
                conversation_id=f"fallback_conv_{user_id}_001",
                messages=[
                    {"role": "user", "content": "請幫我生成一個用戶登錄功能的測試案例"},
                    {"role": "assistant", "content": "我來為您生成用戶登錄功能的測試案例..."}
                ],
                participants=[user_id, "assistant"],
                timestamp_range={"start": "2025-06-25T10:00:00Z", "end": "2025-06-25T10:05:00Z"},
                total_messages=2,
                relevant_score=0.85,
                context={"topic": "testing", "domain": "authentication", "source": "fallback"}
            )
        ]
        
        if timestamp:
            cutoff_time = datetime.fromtimestamp(timestamp).isoformat() + "Z"
            mock_conversations = [
                conv for conv in mock_conversations 
                if conv.timestamp_range["start"] <= cutoff_time
            ]
        
        return mock_conversations
    
    async def _get_fallback_analysis(self, user_id: str, request_id: str) -> Dict[str, Any]:
        """回退分析數據"""
        return {
            "analysis_id": f"fallback_analysis_{request_id}",
            "user_id": user_id,
            "request_id": request_id,
            "confidence_score": 0.5,
            "recommendations": ["使用回退分析數據"],
            "best_practices": ["建議配置真實的 Manus 集成"],
            "analysis_timestamp": datetime.now().isoformat(),
            "data_source": "fallback"
        }
    
    async def _get_fallback_standards(self) -> Dict[str, Any]:
        """回退標準數據"""
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
            },
            "data_source": "fallback",
            "last_updated": datetime.now().isoformat()
        }

# 保留舊的 ManusDataAccessMock 類以向後兼容
class ManusDataAccessMock(ManusDataAccess):
    """Manus 數據訪問模擬類（向後兼容）"""
    
    def __init__(self):
        super().__init__()
        self.initialized = False  # 強制使用回退模式
        logger.info("使用 ManusDataAccessMock（向後兼容模式）")

class DataProvider:
    """數據提供者類 - 聚合多個數據源"""
    
    def __init__(self, manus_data_access=None, plugin_data_access: PluginDataAccess = None, manus_config: Dict[str, Any] = None):
        """
        初始化數據提供者
        
        Args:
            manus_data_access: Manus 數據訪問實例
            plugin_data_access: 插件數據訪問實例
            manus_config: Manus 配置
        """
        if manus_data_access is None:
            # 使用真實的 ManusDataAccess
            self.manus_access = ManusDataAccess(manus_config)
        else:
            self.manus_access = manus_data_access
            
        self.plugin_access = plugin_data_access or PluginDataAccess()
        self._initialized = False
        
        logger.info("DataProvider 初始化，使用真實 Manus 數據訪問")
    
    async def initialize(self) -> bool:
        """初始化數據提供者"""
        try:
            # 初始化 Manus 數據訪問
            manus_init = await self.manus_access.initialize()
            
            self._initialized = True
            logger.info(f"DataProvider 初始化完成，Manus 集成: {'成功' if manus_init else '回退模式'}")
            return True
            
        except Exception as e:
            logger.error(f"DataProvider 初始化失敗: {e}")
            self._initialized = False
            return False
    
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
            # 確保已初始化
            if not self._initialized:
                await self.initialize()
            
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
            
            logger.info(f"獲取用戶 {user_id} 的完整上下文，包含 {len(conversations or [])} 個對話")
            return user_context
            
        except Exception as e:
            logger.error(f"獲取用戶上下文失敗: {e}")
            # 返回基本的用戶上下文
            return UserContext(
                user_id=user_id,
                conversations=[],
                code_snapshot=None,
                request_history=[],
                last_activity=datetime.now(),
                context_score=0.0
            )
    
    async def get_comparison_data(self, user_id: str, current_request: Dict[str, Any]) -> ComparisonContext:
        """
        獲取對比數據
        
        Args:
            user_id: 用戶 ID
            current_request: 當前請求
            
        Returns:
            ComparisonContext: 對比上下文對象
        """
        try:
            # 獲取用戶上下文
            user_context = await self.get_user_full_context(user_id)
            
            # 獲取 Manus 標準
            manus_standards = await self.manus_access.get_standards()
            
            # 構建對比上下文
            comparison_context = ComparisonContext(
                user_context=user_context,
                current_request=current_request,
                manus_standards=manus_standards,
                comparison_metadata={
                    "timestamp": datetime.now().isoformat(),
                    "data_source": "real_manus" if self.manus_access.initialized else "fallback",
                    "context_quality": user_context.context_score
                }
            )
            
            logger.info(f"構建對比上下文，數據源: {comparison_context.comparison_metadata['data_source']}")
            return comparison_context
            
        except Exception as e:
            logger.error(f"獲取對比數據失敗: {e}")
            raise
    
    async def _get_request_history(self, user_id: str, timestamp: float = None) -> List[Dict[str, Any]]:
        """獲取請求歷史（模擬實現）"""
        return [
            {
                "request_id": f"req_{user_id}_001",
                "timestamp": "2025-06-25T09:00:00Z",
                "method": "generate_test_case",
                "parameters": {"feature": "user_login"},
                "status": "completed"
            }
        ]
    
    def _calculate_context_score(self, conversations: List[ConversationHistory], 
                                code_snapshot: Optional[CodeSnapshot], 
                                request_history: List[Dict[str, Any]]) -> float:
        """計算上下文分數"""
        score = 0.0
        
        # 對話質量分數
        if conversations:
            avg_relevance = sum(conv.relevant_score for conv in conversations) / len(conversations)
            score += avg_relevance * 0.4
        
        # 代碼快照分數
        if code_snapshot and code_snapshot.projects:
            score += 0.3
        
        # 請求歷史分數
        if request_history:
            score += min(len(request_history) * 0.1, 0.3)
        
        return min(score, 1.0)

# 導出主要類
__all__ = ["DataProvider", "ManusDataAccess", "ManusDataAccessMock", "ConversationHistory", "UserContext", "ComparisonContext"]

