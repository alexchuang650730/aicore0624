#!/usr/bin/env python3
"""
Dialogue Context Manager
對話上下文管理器

管理多輪對話的上下文狀態，支持會話持久化、上下文壓縮和智能摘要
為 AICore 系統提供統一的對話管理能力
"""

import asyncio
import json
import logging
import time
import sqlite3
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

class MessageRole(Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"

class SessionStatus(Enum):
    """會話狀態"""
    ACTIVE = "active"
    IDLE = "idle"
    ARCHIVED = "archived"
    EXPIRED = "expired"

@dataclass
class DialogueMessage:
    """對話消息"""
    message_id: str
    session_id: str
    role: MessageRole
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    token_count: int = 0
    importance_score: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "session_id": self.session_id,
            "role": self.role.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "token_count": self.token_count,
            "importance_score": self.importance_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogueMessage':
        return cls(
            message_id=data["message_id"],
            session_id=data["session_id"],
            role=MessageRole(data["role"]),
            content=data["content"],
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            token_count=data.get("token_count", 0),
            importance_score=data.get("importance_score", 0.5)
        )

@dataclass
class DialogueSession:
    """對話會話"""
    session_id: str
    service_type: str
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    total_messages: int = 0
    total_tokens: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "service_type": self.service_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "total_messages": self.total_messages,
            "total_tokens": self.total_tokens,
            "metadata": self.metadata,
            "summary": self.summary
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogueSession':
        return cls(
            session_id=data["session_id"],
            service_type=data["service_type"],
            status=SessionStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            total_messages=data.get("total_messages", 0),
            total_tokens=data.get("total_tokens", 0),
            metadata=data.get("metadata", {}),
            summary=data.get("summary", "")
        )

class DialogueStorage:
    """對話存儲"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.db_path = self.config.get("db_path", "dialogue_storage.db")
        self.conn = None
        self.initialized = False
        
    async def initialize(self):
        """初始化存儲"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # 允許按列名訪問
            
            # 創建表結構
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS dialogue_sessions (
                    session_id TEXT PRIMARY KEY,
                    service_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    total_messages INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    metadata TEXT DEFAULT '{}',
                    summary TEXT DEFAULT ''
                )
            """)
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS dialogue_messages (
                    message_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    timestamp TEXT NOT NULL,
                    token_count INTEGER DEFAULT 0,
                    importance_score REAL DEFAULT 0.5,
                    FOREIGN KEY (session_id) REFERENCES dialogue_sessions (session_id)
                )
            """)
            
            # 創建索引
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_session_messages ON dialogue_messages(session_id, timestamp)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_session_status ON dialogue_sessions(status, last_activity)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_message_importance ON dialogue_messages(importance_score)")
            
            self.conn.commit()
            self.initialized = True
            logger.info("Dialogue storage initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize dialogue storage: {e}")
            raise
    
    async def save_session(self, session: DialogueSession):
        """保存會話"""
        if not self.initialized:
            await self.initialize()
        
        try:
            self.conn.execute("""
                INSERT OR REPLACE INTO dialogue_sessions 
                (session_id, service_type, status, created_at, last_activity, 
                 total_messages, total_tokens, metadata, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id,
                session.service_type,
                session.status.value,
                session.created_at.isoformat(),
                session.last_activity.isoformat(),
                session.total_messages,
                session.total_tokens,
                json.dumps(session.metadata),
                session.summary
            ))
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error saving session {session.session_id}: {e}")
            raise
    
    async def load_session(self, session_id: str) -> Optional[DialogueSession]:
        """加載會話"""
        if not self.initialized:
            await self.initialize()
        
        try:
            cursor = self.conn.execute("""
                SELECT * FROM dialogue_sessions WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data["metadata"] = json.loads(data["metadata"])
                return DialogueSession.from_dict(data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return None
    
    async def save_message(self, message: DialogueMessage):
        """保存消息"""
        if not self.initialized:
            await self.initialize()
        
        try:
            self.conn.execute("""
                INSERT OR REPLACE INTO dialogue_messages
                (message_id, session_id, role, content, metadata, timestamp, 
                 token_count, importance_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message.message_id,
                message.session_id,
                message.role.value,
                message.content,
                json.dumps(message.metadata),
                message.timestamp.isoformat(),
                message.token_count,
                message.importance_score
            ))
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error saving message {message.message_id}: {e}")
            raise
    
    async def load_messages(self, session_id: str, limit: int = None, 
                           offset: int = 0) -> List[DialogueMessage]:
        """加載消息"""
        if not self.initialized:
            await self.initialize()
        
        try:
            query = """
                SELECT * FROM dialogue_messages 
                WHERE session_id = ? 
                ORDER BY timestamp ASC
            """
            params = [session_id]
            
            if limit:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            
            cursor = self.conn.execute(query, params)
            messages = []
            
            for row in cursor.fetchall():
                data = dict(row)
                data["metadata"] = json.loads(data["metadata"])
                message = DialogueMessage.from_dict(data)
                messages.append(message)
            
            return messages
            
        except Exception as e:
            logger.error(f"Error loading messages for session {session_id}: {e}")
            return []
    
    async def get_recent_sessions(self, limit: int = 10, 
                                 status: SessionStatus = None) -> List[DialogueSession]:
        """獲取最近的會話"""
        if not self.initialized:
            await self.initialize()
        
        try:
            query = "SELECT * FROM dialogue_sessions"
            params = []
            
            if status:
                query += " WHERE status = ?"
                params.append(status.value)
            
            query += " ORDER BY last_activity DESC LIMIT ?"
            params.append(limit)
            
            cursor = self.conn.execute(query, params)
            sessions = []
            
            for row in cursor.fetchall():
                data = dict(row)
                data["metadata"] = json.loads(data["metadata"])
                session = DialogueSession.from_dict(data)
                sessions.append(session)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting recent sessions: {e}")
            return []
    
    async def cleanup_old_sessions(self, max_age_days: int = 30) -> int:
        """清理舊會話"""
        if not self.initialized:
            await self.initialize()
        
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            # 獲取要刪除的會話ID
            cursor = self.conn.execute("""
                SELECT session_id FROM dialogue_sessions 
                WHERE last_activity < ? AND status != 'active'
            """, (cutoff_date.isoformat(),))
            
            session_ids = [row[0] for row in cursor.fetchall()]
            
            if session_ids:
                # 刪除消息
                placeholders = ','.join(['?' for _ in session_ids])
                self.conn.execute(f"""
                    DELETE FROM dialogue_messages 
                    WHERE session_id IN ({placeholders})
                """, session_ids)
                
                # 刪除會話
                self.conn.execute(f"""
                    DELETE FROM dialogue_sessions 
                    WHERE session_id IN ({placeholders})
                """, session_ids)
                
                self.conn.commit()
            
            logger.info(f"Cleaned up {len(session_ids)} old sessions")
            return len(session_ids)
            
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")
            return 0

class DialogueSummarizer:
    """對話摘要器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_summary_length = self.config.get("max_summary_length", 500)
        self.summary_trigger_threshold = self.config.get("summary_trigger_threshold", 20)
        
    async def generate_summary(self, messages: List[DialogueMessage]) -> str:
        """生成對話摘要"""
        if not messages:
            return ""
        
        try:
            # 簡化的摘要生成邏輯
            # 在實際實現中，這裡可以使用更高級的 NLP 模型
            
            # 提取關鍵信息
            user_messages = [msg for msg in messages if msg.role == MessageRole.USER]
            assistant_messages = [msg for msg in messages if msg.role == MessageRole.ASSISTANT]
            
            # 統計信息
            total_messages = len(messages)
            conversation_duration = (messages[-1].timestamp - messages[0].timestamp).total_seconds() / 60
            
            # 提取主要話題
            topics = self._extract_topics(messages)
            
            # 構建摘要
            summary_parts = []
            summary_parts.append(f"對話包含 {total_messages} 條消息，持續約 {conversation_duration:.1f} 分鐘。")
            
            if topics:
                summary_parts.append(f"主要討論話題：{', '.join(topics[:3])}。")
            
            # 添加最後的交互
            if assistant_messages:
                last_assistant_msg = assistant_messages[-1]
                if len(last_assistant_msg.content) > 100:
                    last_content = last_assistant_msg.content[:100] + "..."
                else:
                    last_content = last_assistant_msg.content
                summary_parts.append(f"最後回應：{last_content}")
            
            summary = " ".join(summary_parts)
            
            # 限制長度
            if len(summary) > self.max_summary_length:
                summary = summary[:self.max_summary_length] + "..."
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "摘要生成失敗"
    
    def _extract_topics(self, messages: List[DialogueMessage]) -> List[str]:
        """提取對話話題"""
        topics = []
        
        # 簡化的話題提取
        all_content = " ".join([msg.content for msg in messages])
        words = all_content.lower().split()
        
        # 常見的技術關鍵詞
        tech_keywords = {
            "python", "javascript", "java", "api", "database", "web", "server",
            "function", "class", "method", "variable", "error", "bug", "test",
            "code", "programming", "development", "framework", "library"
        }
        
        # 統計關鍵詞頻率
        keyword_count = defaultdict(int)
        for word in words:
            clean_word = word.strip(".,!?;:")
            if clean_word in tech_keywords:
                keyword_count[clean_word] += 1
        
        # 返回最常見的話題
        sorted_topics = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
        topics = [topic for topic, count in sorted_topics[:5] if count > 1]
        
        return topics
    
    async def should_generate_summary(self, session: DialogueSession) -> bool:
        """判斷是否應該生成摘要"""
        return (
            session.total_messages >= self.summary_trigger_threshold and
            not session.summary
        )

class DialogueContextManager:
    """對話上下文管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = "Dialogue Context Manager"
        self.version = "1.0.0"
        
        # 初始化組件
        self.storage = DialogueStorage(self.config.get("storage", {}))
        self.summarizer = DialogueSummarizer(self.config.get("summarizer", {}))
        
        # 配置參數
        self.max_history_length = self.config.get("max_history_length", 100)
        self.session_timeout = self.config.get("session_timeout", 3600)  # 1小時
        self.auto_archive_days = self.config.get("auto_archive_days", 7)
        
        # 運行時狀態
        self.initialized = False
        self.active_sessions = {}  # session_id -> DialogueSession
        self.message_buffers = {}  # session_id -> deque of messages
        
        # 性能統計
        self.stats = {
            "total_sessions": 0,
            "active_sessions": 0,
            "total_messages": 0,
            "average_session_length": 0.0,
            "service_type_distribution": defaultdict(int)
        }
        
        logger.info(f"Initializing {self.name} v{self.version}")
    
    async def initialize(self):
        """初始化對話管理器"""
        try:
            logger.info("Initializing Dialogue Context Manager...")
            
            # 初始化存儲
            await self.storage.initialize()
            logger.info("✅ Dialogue storage initialized")
            
            # 加載活動會話
            await self._load_active_sessions()
            logger.info("✅ Active sessions loaded")
            
            self.initialized = True
            logger.info(f"🎉 {self.name} initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.name}: {e}")
            return False
    
    async def _load_active_sessions(self):
        """加載活動會話"""
        try:
            recent_sessions = await self.storage.get_recent_sessions(
                limit=50, status=SessionStatus.ACTIVE
            )
            
            for session in recent_sessions:
                # 檢查會話是否過期
                time_since_activity = datetime.now() - session.last_activity
                if time_since_activity.total_seconds() < self.session_timeout:
                    self.active_sessions[session.session_id] = session
                    
                    # 加載消息緩衝區
                    recent_messages = await self.storage.load_messages(
                        session.session_id, limit=self.max_history_length
                    )
                    self.message_buffers[session.session_id] = deque(
                        recent_messages, maxlen=self.max_history_length
                    )
                else:
                    # 標記為空閒
                    session.status = SessionStatus.IDLE
                    await self.storage.save_session(session)
            
            self.stats["active_sessions"] = len(self.active_sessions)
            logger.info(f"Loaded {len(self.active_sessions)} active sessions")
            
        except Exception as e:
            logger.error(f"Error loading active sessions: {e}")
    
    async def create_session(self, session_id: str, service_type: str, 
                           metadata: Dict[str, Any] = None) -> DialogueSession:
        """創建新會話"""
        try:
            session = DialogueSession(
                session_id=session_id,
                service_type=service_type,
                metadata=metadata or {}
            )
            
            # 保存到存儲
            await self.storage.save_session(session)
            
            # 添加到活動會話
            self.active_sessions[session_id] = session
            self.message_buffers[session_id] = deque(maxlen=self.max_history_length)
            
            # 更新統計
            self.stats["total_sessions"] += 1
            self.stats["active_sessions"] += 1
            self.stats["service_type_distribution"][service_type] += 1
            
            logger.info(f"Created session {session_id} for service {service_type}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating session {session_id}: {e}")
            raise
    
    async def add_message(self, session_id: str, role: MessageRole, content: str,
                         metadata: Dict[str, Any] = None) -> DialogueMessage:
        """添加消息到會話"""
        try:
            # 確保會話存在
            session = await self._get_or_create_session(session_id)
            
            # 創建消息
            message_id = f"{session_id}_{int(time.time())}_{hashlib.md5(content.encode()).hexdigest()[:8]}"
            message = DialogueMessage(
                message_id=message_id,
                session_id=session_id,
                role=role,
                content=content,
                metadata=metadata or {},
                token_count=len(content.split())
            )
            
            # 計算重要性分數
            message.importance_score = await self._calculate_importance(message)
            
            # 保存消息
            await self.storage.save_message(message)
            
            # 添加到緩衝區
            if session_id in self.message_buffers:
                self.message_buffers[session_id].append(message)
            else:
                self.message_buffers[session_id] = deque([message], maxlen=self.max_history_length)
            
            # 更新會話統計
            session.total_messages += 1
            session.total_tokens += message.token_count
            session.last_activity = datetime.now()
            
            # 檢查是否需要生成摘要
            if await self.summarizer.should_generate_summary(session):
                await self._update_session_summary(session_id)
            
            # 保存會話更新
            await self.storage.save_session(session)
            
            # 更新統計
            self.stats["total_messages"] += 1
            
            logger.debug(f"Added message {message_id} to session {session_id}")
            return message
            
        except Exception as e:
            logger.error(f"Error adding message to session {session_id}: {e}")
            raise
    
    async def get_session_history(self, session_id: str, limit: int = None,
                                 include_system: bool = False) -> List[DialogueMessage]:
        """獲取會話歷史"""
        try:
            # 首先嘗試從緩衝區獲取
            if session_id in self.message_buffers:
                messages = list(self.message_buffers[session_id])
            else:
                # 從存儲加載
                messages = await self.storage.load_messages(session_id, limit=limit or self.max_history_length)
            
            # 過濾系統消息（如果需要）
            if not include_system:
                messages = [msg for msg in messages if msg.role != MessageRole.SYSTEM]
            
            # 應用限制
            if limit and len(messages) > limit:
                messages = messages[-limit:]
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting session history for {session_id}: {e}")
            return []
    
    async def get_session_summary(self, session_id: str) -> str:
        """獲取會話摘要"""
        try:
            session = await self.storage.load_session(session_id)
            if session and session.summary:
                return session.summary
            
            # 如果沒有摘要，嘗試生成
            messages = await self.get_session_history(session_id)
            if messages:
                summary = await self.summarizer.generate_summary(messages)
                
                # 保存摘要
                if session:
                    session.summary = summary
                    await self.storage.save_session(session)
                
                return summary
            
            return ""
            
        except Exception as e:
            logger.error(f"Error getting session summary for {session_id}: {e}")
            return ""
    
    async def get_contextual_messages(self, session_id: str, query: str, 
                                    limit: int = 5) -> List[DialogueMessage]:
        """獲取與查詢相關的上下文消息"""
        try:
            messages = await self.get_session_history(session_id)
            if not messages:
                return []
            
            # 簡化的相關性計算
            query_words = set(query.lower().split())
            scored_messages = []
            
            for message in messages:
                message_words = set(message.content.lower().split())
                relevance = len(query_words.intersection(message_words)) / len(query_words) if query_words else 0
                
                if relevance > 0.1:  # 最小相關性閾值
                    scored_messages.append((message, relevance))
            
            # 按相關性排序
            scored_messages.sort(key=lambda x: x[1], reverse=True)
            
            # 返回最相關的消息
            return [msg for msg, score in scored_messages[:limit]]
            
        except Exception as e:
            logger.error(f"Error getting contextual messages: {e}")
            return []
    
    async def close_session(self, session_id: str):
        """關閉會話"""
        try:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.status = SessionStatus.IDLE
                session.last_activity = datetime.now()
                
                # 生成最終摘要
                if not session.summary:
                    await self._update_session_summary(session_id)
                
                # 保存會話
                await self.storage.save_session(session)
                
                # 從活動會話中移除
                del self.active_sessions[session_id]
                if session_id in self.message_buffers:
                    del self.message_buffers[session_id]
                
                # 更新統計
                self.stats["active_sessions"] -= 1
                
                logger.info(f"Closed session {session_id}")
            
        except Exception as e:
            logger.error(f"Error closing session {session_id}: {e}")
    
    async def _get_or_create_session(self, session_id: str) -> DialogueSession:
        """獲取或創建會話"""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # 嘗試從存儲加載
        session = await self.storage.load_session(session_id)
        if session:
            # 重新激活會話
            session.status = SessionStatus.ACTIVE
            self.active_sessions[session_id] = session
            return session
        
        # 創建新會話（使用默認服務類型）
        return await self.create_session(session_id, "general")
    
    async def _calculate_importance(self, message: DialogueMessage) -> float:
        """計算消息重要性分數"""
        importance = 0.5  # 基礎分數
        
        # 基於角色調整
        if message.role == MessageRole.USER:
            importance += 0.2  # 用戶消息更重要
        elif message.role == MessageRole.SYSTEM:
            importance -= 0.2  # 系統消息較不重要
        
        # 基於內容長度調整
        content_length = len(message.content)
        if content_length > 500:
            importance += 0.1
        elif content_length < 50:
            importance -= 0.1
        
        # 基於關鍵詞調整
        important_keywords = ["error", "問題", "help", "重要", "urgent", "bug"]
        content_lower = message.content.lower()
        
        for keyword in important_keywords:
            if keyword in content_lower:
                importance += 0.1
                break
        
        return max(0.0, min(1.0, importance))
    
    async def _update_session_summary(self, session_id: str):
        """更新會話摘要"""
        try:
            messages = await self.get_session_history(session_id)
            if messages:
                summary = await self.summarizer.generate_summary(messages)
                
                if session_id in self.active_sessions:
                    self.active_sessions[session_id].summary = summary
                
                # 也需要更新存儲中的會話
                session = await self.storage.load_session(session_id)
                if session:
                    session.summary = summary
                    await self.storage.save_session(session)
                
                logger.debug(f"Updated summary for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error updating session summary: {e}")
    
    async def cleanup_expired_sessions(self) -> int:
        """清理過期會話"""
        try:
            current_time = datetime.now()
            expired_sessions = []
            
            for session_id, session in self.active_sessions.items():
                time_since_activity = current_time - session.last_activity
                if time_since_activity.total_seconds() > self.session_timeout:
                    expired_sessions.append(session_id)
            
            # 關閉過期會話
            for session_id in expired_sessions:
                await self.close_session(session_id)
            
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            return len(expired_sessions)
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
    
    async def archive_old_sessions(self) -> int:
        """歸檔舊會話"""
        try:
            archived_count = await self.storage.cleanup_old_sessions(self.auto_archive_days)
            logger.info(f"Archived {archived_count} old sessions")
            return archived_count
            
        except Exception as e:
            logger.error(f"Error archiving old sessions: {e}")
            return 0
    
    def get_status(self) -> Dict[str, Any]:
        """獲取管理器狀態"""
        return {
            "name": self.name,
            "version": self.version,
            "initialized": self.initialized,
            "stats": dict(self.stats),
            "config": {
                "max_history_length": self.max_history_length,
                "session_timeout": self.session_timeout,
                "auto_archive_days": self.auto_archive_days
            },
            "active_sessions": list(self.active_sessions.keys()),
            "buffer_sizes": {sid: len(buf) for sid, buf in self.message_buffers.items()}
        }
    
    async def shutdown(self):
        """關閉管理器"""
        logger.info("Shutting down Dialogue Context Manager...")
        
        # 關閉所有活動會話
        for session_id in list(self.active_sessions.keys()):
            await self.close_session(session_id)
        
        # 關閉存儲連接
        if self.storage.conn:
            self.storage.conn.close()
        
        logger.info("Dialogue Context Manager shut down")

# 工廠函數
async def create_dialogue_context_manager(config: Dict[str, Any] = None) -> DialogueContextManager:
    """創建並初始化對話上下文管理器"""
    manager = DialogueContextManager(config)
    await manager.initialize()
    return manager

if __name__ == "__main__":
    # 測試代碼
    async def test_dialogue_manager():
        config = {
            "storage": {"db_path": "./test_dialogue.db"},
            "summarizer": {"max_summary_length": 300},
            "max_history_length": 50
        }
        
        manager = await create_dialogue_context_manager(config)
        
        # 創建測試會話
        session = await manager.create_session("test-session-001", "code_generation")
        print(f"Created session: {session.session_id}")
        
        # 添加測試消息
        await manager.add_message(
            session.session_id,
            MessageRole.USER,
            "Hello, I need help with Python programming."
        )
        
        await manager.add_message(
            session.session_id,
            MessageRole.ASSISTANT,
            "I'd be happy to help you with Python programming! What specific topic would you like to learn about?"
        )
        
        # 獲取會話歷史
        history = await manager.get_session_history(session.session_id)
        print(f"Session history: {len(history)} messages")
        
        # 獲取會話摘要
        summary = await manager.get_session_summary(session.session_id)
        print(f"Session summary: {summary}")
        
        # 獲取狀態
        status = manager.get_status()
        print(f"Manager status: {status['stats']}")
        
        # 關閉會話
        await manager.close_session(session.session_id)
        
        # 關閉管理器
        await manager.shutdown()
    
    asyncio.run(test_dialogue_manager())

