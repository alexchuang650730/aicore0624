#!/usr/bin/env python3
"""
Context Manager for Enhanced Code Generation
增強代碼生成的上下文管理器

負責構建、管理和優化代碼生成所需的上下文信息
支持多層次上下文（即時、會話、項目、領域）和智能上下文壓縮
"""

import asyncio
import json
import logging
import time
import hashlib
import sqlite3
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class ContextLevel(Enum):
    """上下文層級"""
    IMMEDIATE = "immediate"      # 即時上下文（當前請求）
    SESSION = "session"          # 會話上下文（當前對話）
    PROJECT = "project"          # 項目上下文（當前項目）
    DOMAIN = "domain"           # 領域上下文（技術領域知識）
    GLOBAL = "global"           # 全局上下文（通用知識）

class ContextType(Enum):
    """上下文類型"""
    CODE_SNIPPET = "code_snippet"
    DOCUMENTATION = "documentation"
    ERROR_MESSAGE = "error_message"
    USER_INTENT = "user_intent"
    PROJECT_STRUCTURE = "project_structure"
    DEPENDENCY_INFO = "dependency_info"
    CONVERSATION_HISTORY = "conversation_history"
    DESIGN_DECISION = "design_decision"
    CODE_PATTERN = "code_pattern"
    PERFORMANCE_METRIC = "performance_metric"

@dataclass
class ContextItem:
    """上下文項目"""
    item_id: str
    content: str
    context_type: ContextType
    context_level: ContextLevel
    source: str
    relevance_score: float = 0.0
    importance_score: float = 0.0
    freshness_score: float = 1.0
    token_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "content": self.content,
            "context_type": self.context_type.value,
            "context_level": self.context_level.value,
            "source": self.source,
            "relevance_score": self.relevance_score,
            "importance_score": self.importance_score,
            "freshness_score": self.freshness_score,
            "token_count": self.token_count,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count
        }
    
    def update_access(self):
        """更新訪問信息"""
        self.last_accessed = datetime.now()
        self.access_count += 1
        
        # 更新新鮮度分數（隨時間衰減）
        time_diff = datetime.now() - self.created_at
        hours_passed = time_diff.total_seconds() / 3600
        self.freshness_score = max(0.1, 1.0 - (hours_passed / 168))  # 一週內線性衰減

@dataclass
class ContextWindow:
    """上下文窗口"""
    window_id: str
    items: List[ContextItem] = field(default_factory=list)
    max_tokens: int = 4000
    current_tokens: int = 0
    priority_weights: Dict[ContextLevel, float] = field(default_factory=lambda: {
        ContextLevel.IMMEDIATE: 1.0,
        ContextLevel.SESSION: 0.8,
        ContextLevel.PROJECT: 0.6,
        ContextLevel.DOMAIN: 0.4,
        ContextLevel.GLOBAL: 0.2
    })
    
    def add_item(self, item: ContextItem) -> bool:
        """添加上下文項目"""
        if self.current_tokens + item.token_count <= self.max_tokens:
            self.items.append(item)
            self.current_tokens += item.token_count
            return True
        return False
    
    def remove_item(self, item_id: str) -> bool:
        """移除上下文項目"""
        for i, item in enumerate(self.items):
            if item.item_id == item_id:
                self.current_tokens -= item.token_count
                del self.items[i]
                return True
        return False
    
    def get_utilization(self) -> float:
        """獲取利用率"""
        return self.current_tokens / self.max_tokens if self.max_tokens > 0 else 0.0
    
    def calculate_total_score(self) -> float:
        """計算總分數"""
        total_score = 0.0
        for item in self.items:
            level_weight = self.priority_weights.get(item.context_level, 0.1)
            item_score = (
                item.relevance_score * 0.4 +
                item.importance_score * 0.3 +
                item.freshness_score * 0.2 +
                (item.access_count / 10) * 0.1  # 訪問頻率
            ) * level_weight
            total_score += item_score
        return total_score

class ContextCompressor:
    """上下文壓縮器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.compression_ratio = self.config.get("compression_ratio", 0.7)
        self.min_importance_threshold = self.config.get("min_importance_threshold", 0.3)
        
    async def compress_context(self, items: List[ContextItem], target_tokens: int) -> List[ContextItem]:
        """壓縮上下文"""
        if not items:
            return []
        
        # 計算當前總 token 數
        current_tokens = sum(item.token_count for item in items)
        
        if current_tokens <= target_tokens:
            return items
        
        # 按重要性排序
        sorted_items = sorted(items, key=self._calculate_item_priority, reverse=True)
        
        # 選擇最重要的項目
        selected_items = []
        selected_tokens = 0
        
        for item in sorted_items:
            if selected_tokens + item.token_count <= target_tokens:
                selected_items.append(item)
                selected_tokens += item.token_count
            elif selected_tokens < target_tokens * 0.9:  # 允許一些彈性
                # 嘗試截斷內容
                available_tokens = target_tokens - selected_tokens
                if available_tokens > 100:  # 最小有用長度
                    truncated_item = self._truncate_item(item, available_tokens)
                    if truncated_item:
                        selected_items.append(truncated_item)
                        break
        
        logger.info(f"Compressed context from {len(items)} items ({current_tokens} tokens) to {len(selected_items)} items ({selected_tokens} tokens)")
        return selected_items
    
    def _calculate_item_priority(self, item: ContextItem) -> float:
        """計算項目優先級"""
        # 基礎分數
        base_score = (
            item.relevance_score * 0.35 +
            item.importance_score * 0.25 +
            item.freshness_score * 0.2 +
            min(item.access_count / 5, 1.0) * 0.2  # 訪問頻率，最大1.0
        )
        
        # 上下文層級權重
        level_weights = {
            ContextLevel.IMMEDIATE: 1.2,
            ContextLevel.SESSION: 1.0,
            ContextLevel.PROJECT: 0.8,
            ContextLevel.DOMAIN: 0.6,
            ContextLevel.GLOBAL: 0.4
        }
        
        level_weight = level_weights.get(item.context_level, 0.5)
        
        # 類型權重
        type_weights = {
            ContextType.USER_INTENT: 1.2,
            ContextType.ERROR_MESSAGE: 1.1,
            ContextType.CODE_SNIPPET: 1.0,
            ContextType.DESIGN_DECISION: 0.9,
            ContextType.DOCUMENTATION: 0.8,
            ContextType.PROJECT_STRUCTURE: 0.7,
            ContextType.CONVERSATION_HISTORY: 0.6
        }
        
        type_weight = type_weights.get(item.context_type, 0.5)
        
        return base_score * level_weight * type_weight
    
    def _truncate_item(self, item: ContextItem, max_tokens: int) -> Optional[ContextItem]:
        """截斷項目內容"""
        if item.token_count <= max_tokens:
            return item
        
        # 估算截斷比例（簡化：假設平均每個 token 4 個字符）
        chars_per_token = 4
        max_chars = max_tokens * chars_per_token
        
        if len(item.content) <= max_chars:
            return item
        
        # 智能截斷：保留開頭和結尾
        if item.context_type == ContextType.CODE_SNIPPET:
            # 代碼片段：保留函數簽名和主要邏輯
            lines = item.content.split('\n')
            if len(lines) > 10:
                keep_lines = max_chars // 50  # 估算能保留的行數
                truncated_content = '\n'.join(lines[:keep_lines//2] + ['...'] + lines[-keep_lines//2:])
            else:
                truncated_content = item.content[:max_chars] + "..."
        else:
            # 其他類型：簡單截斷
            truncated_content = item.content[:max_chars] + "..."
        
        # 創建截斷後的項目
        truncated_item = ContextItem(
            item_id=item.item_id + "_truncated",
            content=truncated_content,
            context_type=item.context_type,
            context_level=item.context_level,
            source=item.source,
            relevance_score=item.relevance_score * 0.9,  # 略微降低相關性
            importance_score=item.importance_score,
            freshness_score=item.freshness_score,
            token_count=max_tokens,
            metadata={**item.metadata, "truncated": True},
            created_at=item.created_at,
            last_accessed=item.last_accessed,
            access_count=item.access_count
        )
        
        return truncated_item

class ContextStorage:
    """上下文存儲"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.db_path = self.config.get("db_path", "context_storage.db")
        self.conn = None
        
    async def initialize(self):
        """初始化存儲"""
        self.conn = sqlite3.connect(self.db_path)
        
        # 創建表結構
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS context_items (
                item_id TEXT PRIMARY KEY,
                content TEXT,
                context_type TEXT,
                context_level TEXT,
                source TEXT,
                relevance_score REAL,
                importance_score REAL,
                freshness_score REAL,
                token_count INTEGER,
                metadata TEXT,
                created_at TEXT,
                last_accessed TEXT,
                access_count INTEGER
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS context_sessions (
                session_id TEXT PRIMARY KEY,
                items TEXT,
                created_at TEXT,
                last_updated TEXT
            )
        """)
        
        # 創建索引
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_context_level ON context_items(context_level)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_context_type ON context_items(context_type)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_relevance_score ON context_items(relevance_score)")
        
        self.conn.commit()
        logger.info("Context storage initialized")
    
    async def store_item(self, item: ContextItem):
        """存儲上下文項目"""
        self.conn.execute("""
            INSERT OR REPLACE INTO context_items 
            (item_id, content, context_type, context_level, source, relevance_score, 
             importance_score, freshness_score, token_count, metadata, created_at, 
             last_accessed, access_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.item_id, item.content, item.context_type.value, item.context_level.value,
            item.source, item.relevance_score, item.importance_score, item.freshness_score,
            item.token_count, json.dumps(item.metadata), item.created_at.isoformat(),
            item.last_accessed.isoformat(), item.access_count
        ))
        self.conn.commit()
    
    async def load_items(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[ContextItem]:
        """加載上下文項目"""
        query = "SELECT * FROM context_items"
        params = []
        
        if filters:
            conditions = []
            if "context_level" in filters:
                conditions.append("context_level = ?")
                params.append(filters["context_level"])
            if "context_type" in filters:
                conditions.append("context_type = ?")
                params.append(filters["context_type"])
            if "min_relevance" in filters:
                conditions.append("relevance_score >= ?")
                params.append(filters["min_relevance"])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY relevance_score DESC, last_accessed DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.execute(query, params)
        items = []
        
        for row in cursor.fetchall():
            item = ContextItem(
                item_id=row[0],
                content=row[1],
                context_type=ContextType(row[2]),
                context_level=ContextLevel(row[3]),
                source=row[4],
                relevance_score=row[5],
                importance_score=row[6],
                freshness_score=row[7],
                token_count=row[8],
                metadata=json.loads(row[9]) if row[9] else {},
                created_at=datetime.fromisoformat(row[10]),
                last_accessed=datetime.fromisoformat(row[11]),
                access_count=row[12]
            )
            items.append(item)
        
        return items
    
    async def update_access(self, item_id: str):
        """更新訪問記錄"""
        self.conn.execute("""
            UPDATE context_items 
            SET last_accessed = ?, access_count = access_count + 1
            WHERE item_id = ?
        """, (datetime.now().isoformat(), item_id))
        self.conn.commit()
    
    async def cleanup_old_items(self, max_age_days: int = 30):
        """清理舊項目"""
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        self.conn.execute("""
            DELETE FROM context_items 
            WHERE created_at < ? AND access_count < 2
        """, (cutoff_date.isoformat(),))
        
        deleted_count = self.conn.total_changes
        self.conn.commit()
        
        logger.info(f"Cleaned up {deleted_count} old context items")
        return deleted_count

class ContextManager:
    """上下文管理器主類"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.storage = ContextStorage(self.config.get("storage", {}))
        self.compressor = ContextCompressor(self.config.get("compressor", {}))
        
        # 配置參數
        self.max_context_tokens = self.config.get("max_context_tokens", 8000)
        self.session_timeout = self.config.get("session_timeout", 3600)  # 1小時
        self.cleanup_interval = self.config.get("cleanup_interval", 86400)  # 1天
        
        # 運行時狀態
        self.initialized = False
        self.current_sessions = {}  # session_id -> ContextWindow
        self.last_cleanup = datetime.now()
        
        # 性能統計
        self.stats = {
            "total_contexts_built": 0,
            "total_items_processed": 0,
            "compression_events": 0,
            "cache_hits": 0,
            "average_build_time": 0.0
        }
    
    async def initialize(self):
        """初始化上下文管理器"""
        try:
            await self.storage.initialize()
            self.initialized = True
            logger.info("Context Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Context Manager: {e}")
            raise
    
    async def build_context(self, query: str, project_path: Optional[str] = None, 
                          max_tokens: int = None, session_id: str = None) -> Dict[str, Any]:
        """構建上下文"""
        if not self.initialized:
            raise RuntimeError("Context Manager not initialized")
        
        start_time = time.time()
        self.stats["total_contexts_built"] += 1
        
        max_tokens = max_tokens or self.max_context_tokens
        session_id = session_id or f"session_{int(time.time())}"
        
        try:
            # 創建上下文窗口
            context_window = ContextWindow(
                window_id=f"context_{session_id}_{int(time.time())}",
                max_tokens=max_tokens
            )
            
            # 收集各層級的上下文
            context_items = []
            
            # 1. 即時上下文（當前查詢）
            immediate_items = await self._build_immediate_context(query, project_path)
            context_items.extend(immediate_items)
            
            # 2. 會話上下文
            if session_id in self.current_sessions:
                session_items = await self._build_session_context(session_id)
                context_items.extend(session_items)
            
            # 3. 項目上下文
            if project_path:
                project_items = await self._build_project_context(project_path, query)
                context_items.extend(project_items)
            
            # 4. 領域上下文
            domain_items = await self._build_domain_context(query)
            context_items.extend(domain_items)
            
            # 5. 全局上下文
            global_items = await self._build_global_context(query)
            context_items.extend(global_items)
            
            # 計算相關性分數
            for item in context_items:
                item.relevance_score = await self._calculate_relevance(item, query)
            
            # 壓縮上下文
            if sum(item.token_count for item in context_items) > max_tokens:
                context_items = await self.compressor.compress_context(context_items, max_tokens)
                self.stats["compression_events"] += 1
            
            # 構建最終上下文
            for item in context_items:
                if context_window.add_item(item):
                    item.update_access()
                    await self.storage.update_access(item.item_id)
                else:
                    break
            
            # 更新會話
            self.current_sessions[session_id] = context_window
            
            # 構建返回結果
            result = {
                "session_id": session_id,
                "total_tokens": context_window.current_tokens,
                "utilization": context_window.get_utilization(),
                "items_count": len(context_window.items),
                "context_by_level": self._group_context_by_level(context_window.items),
                "context_by_type": self._group_context_by_type(context_window.items),
                "quality_score": context_window.calculate_total_score(),
                "metadata": {
                    "query": query,
                    "project_path": project_path,
                    "build_time": time.time() - start_time
                }
            }
            
            # 更新統計
            self.stats["total_items_processed"] += len(context_items)
            build_time = time.time() - start_time
            self.stats["average_build_time"] = (
                (self.stats["average_build_time"] * (self.stats["total_contexts_built"] - 1) + build_time)
                / self.stats["total_contexts_built"]
            )
            
            logger.info(f"Built context with {len(context_window.items)} items ({context_window.current_tokens} tokens) in {build_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error building context: {e}")
            raise
    
    async def _build_immediate_context(self, query: str, project_path: Optional[str]) -> List[ContextItem]:
        """構建即時上下文"""
        items = []
        
        # 用戶意圖
        intent_item = ContextItem(
            item_id=f"intent_{hashlib.md5(query.encode()).hexdigest()[:8]}",
            content=query,
            context_type=ContextType.USER_INTENT,
            context_level=ContextLevel.IMMEDIATE,
            source="user_query",
            importance_score=1.0,
            token_count=len(query.split())
        )
        items.append(intent_item)
        
        return items
    
    async def _build_session_context(self, session_id: str) -> List[ContextItem]:
        """構建會話上下文"""
        items = []
        
        if session_id in self.current_sessions:
            session_window = self.current_sessions[session_id]
            # 獲取會話中的重要項目
            for item in session_window.items[-5:]:  # 最近5個項目
                if item.importance_score > 0.5:
                    session_item = ContextItem(
                        item_id=f"session_{item.item_id}",
                        content=item.content,
                        context_type=ContextType.CONVERSATION_HISTORY,
                        context_level=ContextLevel.SESSION,
                        source=f"session_{session_id}",
                        importance_score=item.importance_score * 0.8,
                        token_count=item.token_count
                    )
                    items.append(session_item)
        
        return items
    
    async def _build_project_context(self, project_path: str, query: str) -> List[ContextItem]:
        """構建項目上下文"""
        items = []
        
        # 從存儲中加載項目相關的上下文
        project_items = await self.storage.load_items({
            "context_level": ContextLevel.PROJECT.value,
            "min_relevance": 0.3
        }, limit=20)
        
        # 過濾與查詢相關的項目
        relevant_items = []
        for item in project_items:
            if project_path in item.source or self._is_query_relevant(item.content, query):
                relevant_items.append(item)
        
        return relevant_items[:10]  # 限制數量
    
    async def _build_domain_context(self, query: str) -> List[ContextItem]:
        """構建領域上下文"""
        items = []
        
        # 檢測技術領域
        domains = self._detect_technical_domains(query)
        
        for domain in domains:
            domain_items = await self.storage.load_items({
                "context_level": ContextLevel.DOMAIN.value,
                "context_type": ContextType.DOCUMENTATION.value
            }, limit=5)
            
            # 過濾與領域相關的項目
            for item in domain_items:
                if domain.lower() in item.content.lower():
                    items.append(item)
        
        return items[:5]  # 限制數量
    
    async def _build_global_context(self, query: str) -> List[ContextItem]:
        """構建全局上下文"""
        items = []
        
        # 加載通用的最佳實踐和模式
        global_items = await self.storage.load_items({
            "context_level": ContextLevel.GLOBAL.value,
            "min_relevance": 0.5
        }, limit=3)
        
        return global_items
    
    def _detect_technical_domains(self, query: str) -> List[str]:
        """檢測技術領域"""
        domains = []
        query_lower = query.lower()
        
        domain_keywords = {
            "web_development": ["web", "http", "api", "rest", "frontend", "backend"],
            "database": ["database", "sql", "query", "table", "schema"],
            "machine_learning": ["ml", "ai", "model", "training", "prediction"],
            "devops": ["deploy", "docker", "kubernetes", "ci/cd", "pipeline"],
            "security": ["security", "auth", "encryption", "vulnerability"],
            "testing": ["test", "unit", "integration", "mock", "assert"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                domains.append(domain)
        
        return domains
    
    def _is_query_relevant(self, content: str, query: str) -> bool:
        """檢查內容是否與查詢相關"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        intersection = query_words.intersection(content_words)
        return len(intersection) / len(query_words) > 0.2 if query_words else False
    
    async def _calculate_relevance(self, item: ContextItem, query: str) -> float:
        """計算相關性分數"""
        # 簡化的相關性計算
        query_words = set(query.lower().split())
        content_words = set(item.content.lower().split())
        
        if not query_words:
            return 0.0
        
        intersection = query_words.intersection(content_words)
        jaccard_similarity = len(intersection) / len(query_words.union(content_words))
        
        # 根據上下文類型調整
        type_multipliers = {
            ContextType.USER_INTENT: 1.0,
            ContextType.CODE_SNIPPET: 0.9,
            ContextType.ERROR_MESSAGE: 0.8,
            ContextType.DOCUMENTATION: 0.7,
            ContextType.CONVERSATION_HISTORY: 0.6
        }
        
        multiplier = type_multipliers.get(item.context_type, 0.5)
        return jaccard_similarity * multiplier
    
    def _group_context_by_level(self, items: List[ContextItem]) -> Dict[str, int]:
        """按層級分組上下文"""
        groups = defaultdict(int)
        for item in items:
            groups[item.context_level.value] += 1
        return dict(groups)
    
    def _group_context_by_type(self, items: List[ContextItem]) -> Dict[str, int]:
        """按類型分組上下文"""
        groups = defaultdict(int)
        for item in items:
            groups[item.context_type.value] += 1
        return dict(groups)
    
    async def add_context_item(self, item: ContextItem):
        """添加上下文項目"""
        await self.storage.store_item(item)
        logger.debug(f"Added context item: {item.item_id}")
    
    async def get_session_context(self, session_id: str) -> Optional[ContextWindow]:
        """獲取會話上下文"""
        return self.current_sessions.get(session_id)
    
    async def cleanup_expired_sessions(self):
        """清理過期會話"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, window in self.current_sessions.items():
            # 檢查最後訪問時間
            if hasattr(window, 'last_accessed'):
                time_diff = current_time - window.last_accessed
                if time_diff.total_seconds() > self.session_timeout:
                    expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.current_sessions[session_id]
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        return len(expired_sessions)
    
    async def periodic_cleanup(self):
        """定期清理"""
        current_time = datetime.now()
        if (current_time - self.last_cleanup).total_seconds() > self.cleanup_interval:
            await self.cleanup_expired_sessions()
            await self.storage.cleanup_old_items()
            self.last_cleanup = current_time
    
    def get_status(self) -> Dict[str, Any]:
        """獲取狀態"""
        return {
            "initialized": self.initialized,
            "active_sessions": len(self.current_sessions),
            "stats": self.stats,
            "config": {
                "max_context_tokens": self.max_context_tokens,
                "session_timeout": self.session_timeout
            }
        }
    
    async def shutdown(self):
        """關閉管理器"""
        if self.storage and self.storage.conn:
            self.storage.conn.close()
        logger.info("Context Manager shut down")

# 工廠函數
async def create_context_manager(config: Dict[str, Any] = None) -> ContextManager:
    """創建並初始化上下文管理器"""
    manager = ContextManager(config)
    await manager.initialize()
    return manager

