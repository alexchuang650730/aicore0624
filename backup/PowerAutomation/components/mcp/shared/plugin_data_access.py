"""
插件數據訪問層 (Plugin Data Access Layer)
負責管理來自 VSCode 插件的代碼同步數據和相關操作
"""

import asyncio
import hashlib
import json
import logging
import sqlite3
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

@dataclass
class CodeProject:
    """代碼項目數據模型"""
    id: str
    user_id: str
    name: str
    version: Optional[str] = None
    language: Optional[str] = None
    git_branch: Optional[str] = None
    git_commit_hash: Optional[str] = None
    git_remote_url: Optional[str] = None
    project_root: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class CodeFile:
    """代碼文件數據模型"""
    id: str
    project_id: str
    file_path: str
    content_hash: str
    file_size: int = 0
    last_modified: Optional[datetime] = None
    status: str = "unchanged"  # added, modified, deleted, unchanged
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class SyncSession:
    """同步會話數據模型"""
    id: str
    user_id: str
    project_id: Optional[str] = None
    sync_type: str = "incremental"  # full, incremental
    files_count: int = 0
    files_added: int = 0
    files_modified: int = 0
    files_deleted: int = 0
    status: str = "pending"  # pending, processing, completed, failed
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class CodeSnapshot:
    """代碼快照數據模型"""
    project: CodeProject
    files: List[CodeFile]
    sync_session: SyncSession
    total_size: int = 0
    file_count: int = 0

class PluginDataAccess:
    """插件數據訪問類"""
    
    def __init__(self, db_path: str = None):
        """
        初始化插件數據訪問層
        
        Args:
            db_path: 數據庫文件路徑，如果為 None 則使用默認路徑
        """
        if db_path is None:
            db_path = "/home/ubuntu/aicore0624/data/plugin.db"
        
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        """確保數據庫目錄存在"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def _init_database(self):
        """初始化數據庫表結構"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 直接創建基本表結構（SQLite 版本）
                self._create_basic_tables(conn)
                conn.commit()
                logger.info("Plugin database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize plugin database: {e}")
            raise
    
    def _adapt_sql_for_sqlite(self, sql_content: str) -> str:
        """將 MySQL SQL 語法適配為 SQLite"""
        # 移除 MySQL 特定的語法
        adaptations = [
            ('LONGTEXT', 'TEXT'),
            ('VARCHAR(255)', 'TEXT'),
            ('VARCHAR(50)', 'TEXT'),
            ('VARCHAR(20)', 'TEXT'),
            ('DECIMAL(5,4)', 'REAL'),
            ('JSON', 'TEXT'),
            ('INDEX ', '-- INDEX '),  # SQLite 使用 CREATE INDEX
            ('FOREIGN KEY', '-- FOREIGN KEY'),  # 簡化外鍵約束
            ('ON DELETE CASCADE', ''),
            ('ON DELETE SET NULL', ''),
            ('UNIQUE KEY', 'UNIQUE'),
            ('FULLTEXT', '-- FULLTEXT'),
            ('DELIMITER $$', ''),
            ('$$', ''),
            ('DELIMITER ;', ''),
        ]
        
        for old, new in adaptations:
            sql_content = sql_content.replace(old, new)
        
        return sql_content
    
    def _create_basic_tables(self, conn: sqlite3.Connection):
        """創建基本表結構（SQLite 版本）"""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS code_projects (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                version TEXT,
                language TEXT,
                git_branch TEXT,
                git_commit_hash TEXT,
                git_remote_url TEXT,
                project_root TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS code_files (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                file_path TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                file_size INTEGER DEFAULT 0,
                last_modified TIMESTAMP,
                status TEXT DEFAULT 'unchanged',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS code_file_contents (
                content_hash TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                content_size INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sync_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                project_id TEXT,
                sync_type TEXT DEFAULT 'incremental',
                files_count INTEGER DEFAULT 0,
                files_added INTEGER DEFAULT 0,
                files_modified INTEGER DEFAULT 0,
                files_deleted INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_request_contexts (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                request_id TEXT NOT NULL,
                project_id TEXT,
                sync_session_id TEXT,
                context_type TEXT DEFAULT 'code_sync',
                context_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        for table_sql in tables:
            conn.execute(table_sql)
    
    def _generate_id(self) -> str:
        """生成唯一 ID"""
        return str(uuid.uuid4())
    
    def _calculate_content_hash(self, content: str) -> str:
        """計算內容的 MD5 哈希值"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    async def save_code_sync_data(self, user_id: str, code_sync_data: Dict[str, Any]) -> str:
        """
        保存代碼同步數據
        
        Args:
            user_id: 用戶 ID
            code_sync_data: 代碼同步數據
            
        Returns:
            sync_session_id: 同步會話 ID
        """
        try:
            # 創建同步會話
            sync_session_id = self._generate_id()
            sync_session = SyncSession(
                id=sync_session_id,
                user_id=user_id,
                sync_type=code_sync_data.get('sync_type', 'incremental'),
                status='processing',
                created_at=datetime.now()
            )
            
            # 處理項目信息
            project_metadata = code_sync_data.get('project_metadata', {})
            project_id = self._generate_id()
            
            project = CodeProject(
                id=project_id,
                user_id=user_id,
                name=project_metadata.get('name', 'Unknown Project'),
                version=project_metadata.get('version'),
                language=project_metadata.get('language'),
                git_branch=project_metadata.get('git_info', {}).get('branch'),
                git_commit_hash=project_metadata.get('git_info', {}).get('commit_hash'),
                git_remote_url=project_metadata.get('git_info', {}).get('remote_url'),
                project_root=code_sync_data.get('project_root'),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 更新同步會話的項目 ID
            sync_session.project_id = project_id
            
            # 處理文件數據
            files_data = code_sync_data.get('files', [])
            code_files = []
            files_added = 0
            files_modified = 0
            files_deleted = 0
            
            with sqlite3.connect(self.db_path) as conn:
                # 保存項目
                await self._save_project(conn, project)
                
                # 保存文件
                for file_data in files_data:
                    file_content = file_data.get('content', '')
                    content_hash = file_data.get('checksum') or self._calculate_content_hash(file_content)
                    
                    # 保存文件內容（去重）
                    await self._save_file_content(conn, content_hash, file_content)
                    
                    # 創建文件記錄
                    code_file = CodeFile(
                        id=self._generate_id(),
                        project_id=project_id,
                        file_path=file_data.get('path', ''),
                        content_hash=content_hash,
                        file_size=len(file_content.encode('utf-8')),
                        last_modified=datetime.fromtimestamp(file_data.get('last_modified', time.time())),
                        status=file_data.get('status', 'unchanged'),
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    code_files.append(code_file)
                    await self._save_file(conn, code_file)
                    
                    # 統計文件狀態
                    if code_file.status == 'added':
                        files_added += 1
                    elif code_file.status == 'modified':
                        files_modified += 1
                    elif code_file.status == 'deleted':
                        files_deleted += 1
                
                # 更新同步會話統計
                sync_session.files_count = len(code_files)
                sync_session.files_added = files_added
                sync_session.files_modified = files_modified
                sync_session.files_deleted = files_deleted
                sync_session.status = 'completed'
                sync_session.completed_at = datetime.now()
                
                # 保存同步會話
                await self._save_sync_session(conn, sync_session)
                
                conn.commit()
                
            logger.info(f"Code sync data saved successfully. Session ID: {sync_session_id}")
            return sync_session_id
            
        except Exception as e:
            logger.error(f"Failed to save code sync data: {e}")
            # 更新同步會話狀態為失敗
            try:
                with sqlite3.connect(self.db_path) as conn:
                    sync_session.status = 'failed'
                    sync_session.error_message = str(e)
                    sync_session.completed_at = datetime.now()
                    await self._save_sync_session(conn, sync_session)
                    conn.commit()
            except:
                pass
            raise
    
    async def _save_project(self, conn: sqlite3.Connection, project: CodeProject):
        """保存項目到數據庫"""
        conn.execute("""
            INSERT OR REPLACE INTO code_projects 
            (id, user_id, name, version, language, git_branch, git_commit_hash, 
             git_remote_url, project_root, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project.id, project.user_id, project.name, project.version,
            project.language, project.git_branch, project.git_commit_hash,
            project.git_remote_url, project.project_root,
            project.created_at, project.updated_at
        ))
    
    async def _save_file(self, conn: sqlite3.Connection, code_file: CodeFile):
        """保存文件到數據庫"""
        conn.execute("""
            INSERT OR REPLACE INTO code_files 
            (id, project_id, file_path, content_hash, file_size, 
             last_modified, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            code_file.id, code_file.project_id, code_file.file_path,
            code_file.content_hash, code_file.file_size,
            code_file.last_modified, code_file.status,
            code_file.created_at, code_file.updated_at
        ))
    
    async def _save_file_content(self, conn: sqlite3.Connection, content_hash: str, content: str):
        """保存文件內容到數據庫（去重）"""
        # 檢查內容是否已存在
        cursor = conn.execute("SELECT content_hash FROM code_file_contents WHERE content_hash = ?", (content_hash,))
        if cursor.fetchone() is None:
            conn.execute("""
                INSERT INTO code_file_contents (content_hash, content, content_size, created_at)
                VALUES (?, ?, ?, ?)
            """, (content_hash, content, len(content.encode('utf-8')), datetime.now()))
    
    async def _save_sync_session(self, conn: sqlite3.Connection, sync_session: SyncSession):
        """保存同步會話到數據庫"""
        conn.execute("""
            INSERT OR REPLACE INTO sync_sessions 
            (id, user_id, project_id, sync_type, files_count, files_added, 
             files_modified, files_deleted, status, error_message, 
             created_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sync_session.id, sync_session.user_id, sync_session.project_id,
            sync_session.sync_type, sync_session.files_count,
            sync_session.files_added, sync_session.files_modified,
            sync_session.files_deleted, sync_session.status,
            sync_session.error_message, sync_session.created_at,
            sync_session.completed_at
        ))
    
    async def get_user_code_snapshot(self, user_id: str, timestamp: float = None) -> Optional[CodeSnapshot]:
        """
        獲取用戶的代碼快照
        
        Args:
            user_id: 用戶 ID
            timestamp: 時間戳，如果為 None 則獲取最新的
            
        Returns:
            CodeSnapshot: 代碼快照對象，如果不存在則返回 None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # 獲取最新的同步會話
                if timestamp:
                    cursor = conn.execute("""
                        SELECT * FROM sync_sessions 
                        WHERE user_id = ? AND created_at <= ? AND status = 'completed'
                        ORDER BY created_at DESC LIMIT 1
                    """, (user_id, datetime.fromtimestamp(timestamp)))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM sync_sessions 
                        WHERE user_id = ? AND status = 'completed'
                        ORDER BY created_at DESC LIMIT 1
                    """, (user_id,))
                
                session_row = cursor.fetchone()
                if not session_row:
                    return None
                
                sync_session = SyncSession(**dict(session_row))
                
                # 獲取項目信息
                cursor = conn.execute("SELECT * FROM code_projects WHERE id = ?", (sync_session.project_id,))
                project_row = cursor.fetchone()
                if not project_row:
                    return None
                
                project = CodeProject(**dict(project_row))
                
                # 獲取文件列表
                cursor = conn.execute("""
                    SELECT * FROM code_files 
                    WHERE project_id = ? 
                    ORDER BY file_path
                """, (sync_session.project_id,))
                
                files = [CodeFile(**dict(row)) for row in cursor.fetchall()]
                
                # 計算統計信息
                total_size = sum(f.file_size for f in files)
                file_count = len(files)
                
                return CodeSnapshot(
                    project=project,
                    files=files,
                    sync_session=sync_session,
                    total_size=total_size,
                    file_count=file_count
                )
                
        except Exception as e:
            logger.error(f"Failed to get user code snapshot: {e}")
            return None
    
    async def search_code_files(self, user_id: str, query: str, project_id: str = None) -> List[Dict[str, Any]]:
        """
        搜索代碼文件
        
        Args:
            user_id: 用戶 ID
            query: 搜索查詢
            project_id: 項目 ID（可選）
            
        Returns:
            List[Dict]: 搜索結果列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # 構建搜索條件
                where_conditions = ["p.user_id = ?"]
                params = [user_id]
                
                if project_id:
                    where_conditions.append("p.id = ?")
                    params.append(project_id)
                
                # 搜索文件路徑和內容
                where_conditions.append("(f.file_path LIKE ? OR c.content LIKE ?)")
                search_pattern = f"%{query}%"
                params.extend([search_pattern, search_pattern])
                
                where_clause = " AND ".join(where_conditions)
                
                cursor = conn.execute(f"""
                    SELECT 
                        f.id as file_id,
                        f.file_path,
                        f.content_hash,
                        f.file_size,
                        f.last_modified,
                        f.status,
                        p.id as project_id,
                        p.name as project_name,
                        p.language,
                        SUBSTR(c.content, 1, 200) as content_snippet
                    FROM code_files f
                    JOIN code_projects p ON f.project_id = p.id
                    LEFT JOIN code_file_contents c ON f.content_hash = c.content_hash
                    WHERE {where_clause}
                    ORDER BY f.last_modified DESC
                    LIMIT 50
                """, params)
                
                results = []
                for row in cursor.fetchall():
                    result = dict(row)
                    # 計算相關性分數（簡單實現）
                    relevance_score = self._calculate_relevance_score(query, result)
                    result['relevance_score'] = relevance_score
                    results.append(result)
                
                # 按相關性排序
                results.sort(key=lambda x: x['relevance_score'], reverse=True)
                
                return results
                
        except Exception as e:
            logger.error(f"Failed to search code files: {e}")
            return []
    
    def _calculate_relevance_score(self, query: str, result: Dict[str, Any]) -> float:
        """計算搜索結果的相關性分數"""
        score = 0.0
        query_lower = query.lower()
        
        # 文件路徑匹配
        if query_lower in result['file_path'].lower():
            score += 0.5
        
        # 內容匹配
        if result['content_snippet'] and query_lower in result['content_snippet'].lower():
            score += 0.3
        
        # 文件類型匹配
        if result['language'] and query_lower in result['language'].lower():
            score += 0.2
        
        return min(score, 1.0)
    
    async def get_project_history(self, user_id: str, project_id: str) -> List[Dict[str, Any]]:
        """
        獲取項目的同步歷史
        
        Args:
            user_id: 用戶 ID
            project_id: 項目 ID
            
        Returns:
            List[Dict]: 同步歷史列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT * FROM sync_sessions 
                    WHERE user_id = ? AND project_id = ?
                    ORDER BY created_at DESC
                """, (user_id, project_id))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get project history: {e}")
            return []
    
    async def get_file_content(self, content_hash: str) -> Optional[str]:
        """
        根據內容哈希獲取文件內容
        
        Args:
            content_hash: 內容哈希值
            
        Returns:
            str: 文件內容，如果不存在則返回 None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT content FROM code_file_contents WHERE content_hash = ?", (content_hash,))
                row = cursor.fetchone()
                return row[0] if row else None
                
        except Exception as e:
            logger.error(f"Failed to get file content: {e}")
            return None
    
    async def get_user_projects(self, user_id: str) -> List[Dict[str, Any]]:
        """
        獲取用戶的所有項目
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            List[Dict]: 項目列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT 
                        p.*,
                        COUNT(f.id) as file_count,
                        SUM(f.file_size) as total_size,
                        MAX(s.created_at) as last_sync
                    FROM code_projects p
                    LEFT JOIN code_files f ON p.id = f.project_id
                    LEFT JOIN sync_sessions s ON p.id = s.project_id
                    WHERE p.user_id = ?
                    GROUP BY p.id
                    ORDER BY p.updated_at DESC
                """, (user_id,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get user projects: {e}")
            return []
    
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """
        清理舊數據
        
        Args:
            days_to_keep: 保留天數
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            with sqlite3.connect(self.db_path) as conn:
                # 刪除舊的同步會話
                cursor = conn.execute("""
                    DELETE FROM sync_sessions 
                    WHERE created_at < ? AND status IN ('completed', 'failed')
                """, (cutoff_date,))
                
                deleted_sessions = cursor.rowcount
                
                # 清理孤立的文件內容
                conn.execute("""
                    DELETE FROM code_file_contents 
                    WHERE content_hash NOT IN (
                        SELECT DISTINCT content_hash FROM code_files
                    )
                """)
                
                conn.commit()
                logger.info(f"Cleaned up {deleted_sessions} old sync sessions")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            raise

