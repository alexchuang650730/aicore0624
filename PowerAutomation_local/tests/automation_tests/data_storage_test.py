#!/usr/bin/env python3
"""
PowerAutomation 數據存儲驗證測試腳本
測試EC2路徑管理、檔案組織和搜尋索引功能
"""

import os
import json
import hashlib
import shutil
import sqlite3
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import unittest
from dataclasses import dataclass, asdict
import tempfile

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/data_storage_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestConfig:
    """測試配置"""
    base_path: str = "/home/ubuntu/powerautomation_data"
    test_data_path: str = "/home/ubuntu/test_data"
    backup_path: str = "/home/ubuntu/backup_data"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    index_update_interval: int = 5  # 5秒
    cleanup_on_exit: bool = True

@dataclass
class TaskData:
    """任務數據結構"""
    task_id: str
    title: str
    description: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    participants: List[str]
    files: List[str]
    conversations: List[str]

@dataclass
class ConversationData:
    """對話數據結構"""
    conversation_id: str
    task_id: str
    participants: List[str]
    messages: List[Dict]
    created_at: datetime
    updated_at: datetime

@dataclass
class FileData:
    """文件數據結構"""
    file_id: str
    filename: str
    file_type: str
    file_size: int
    task_id: str
    file_path: str
    checksum: str
    created_at: datetime
    metadata: Dict

class PathManager:
    """路徑管理器"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.base_path = Path(config.base_path)
        
    def initialize_directory_structure(self) -> bool:
        """初始化目錄結構"""
        try:
            directories = [
                "tasks",
                "conversations/by_date",
                "conversations/by_participant", 
                "conversations/global_index",
                "files/by_type/documents",
                "files/by_type/images",
                "files/by_type/code_files",
                "files/by_type/links",
                "files/by_task",
                "metadata/search_index",
                "metadata/statistics",
                "metadata/cache",
                "logs"
            ]
            
            for directory in directories:
                dir_path = self.base_path / directory
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"創建目錄: {dir_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"初始化目錄結構失敗: {e}")
            return False
    
    def generate_task_path(self, task_id: str) -> Path:
        """生成任務路徑"""
        return self.base_path / "tasks" / task_id
    
    def generate_conversation_path(self, conversation_id: str, created_at: datetime) -> Path:
        """生成對話路徑"""
        date_path = created_at.strftime("%Y/%m/%d")
        return self.base_path / "conversations" / "by_date" / date_path / f"{conversation_id}.json"
    
    def generate_file_path(self, file_data: FileData) -> Path:
        """生成文件路徑"""
        type_mapping = {
            'pdf': 'documents',
            'doc': 'documents', 
            'docx': 'documents',
            'xls': 'documents',
            'xlsx': 'documents',
            'jpg': 'images',
            'jpeg': 'images',
            'png': 'images',
            'gif': 'images',
            'py': 'code_files',
            'js': 'code_files',
            'html': 'code_files',
            'css': 'code_files',
            'url': 'links'
        }
        
        file_ext = file_data.filename.split('.')[-1].lower()
        file_type_dir = type_mapping.get(file_ext, 'documents')
        
        return self.base_path / "files" / "by_type" / file_type_dir / file_data.filename
    
    def create_file_links(self, file_data: FileData, primary_path: Path) -> List[Path]:
        """創建文件鏈接"""
        links = []
        
        # 按任務分類的鏈接
        task_link_dir = self.base_path / "files" / "by_task" / file_data.task_id
        task_link_dir.mkdir(parents=True, exist_ok=True)
        task_link_path = task_link_dir / file_data.filename
        
        try:
            if not task_link_path.exists():
                os.link(str(primary_path), str(task_link_path))
                links.append(task_link_path)
                logger.info(f"創建任務鏈接: {task_link_path}")
        except Exception as e:
            logger.warning(f"創建任務鏈接失敗: {e}")
        
        return links

class DataStorage:
    """數據存儲管理器"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.path_manager = PathManager(config)
        self.db_path = Path(config.base_path) / "metadata" / "data_storage.db"
        self._init_database()
    
    def _init_database(self):
        """初始化數據庫"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # 任務表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT,
                    priority TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    participants TEXT,
                    metadata TEXT
                )
            ''')
            
            # 對話表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    task_id TEXT,
                    participants TEXT,
                    message_count INTEGER,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    file_path TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks (task_id)
                )
            ''')
            
            # 文件表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    file_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_type TEXT,
                    file_size INTEGER,
                    task_id TEXT,
                    file_path TEXT,
                    checksum TEXT,
                    created_at TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks (task_id)
                )
            ''')
            
            # 索引表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_type TEXT,
                    content_id TEXT,
                    keywords TEXT,
                    content_text TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("數據庫初始化完成")
    
    def store_task(self, task_data: TaskData) -> bool:
        """存儲任務數據"""
        try:
            # 創建任務目錄
            task_path = self.path_manager.generate_task_path(task_data.task_id)
            task_path.mkdir(parents=True, exist_ok=True)
            
            # 創建子目錄
            (task_path / "conversations").mkdir(exist_ok=True)
            (task_path / "files").mkdir(exist_ok=True)
            (task_path / "analysis").mkdir(exist_ok=True)
            
            # 保存任務元數據
            metadata_file = task_path / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(task_data), f, ensure_ascii=False, indent=2, default=str)
            
            # 存儲到數據庫
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO tasks 
                    (task_id, title, description, status, priority, created_at, updated_at, participants, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task_data.task_id,
                    task_data.title,
                    task_data.description,
                    task_data.status,
                    task_data.priority,
                    task_data.created_at,
                    task_data.updated_at,
                    json.dumps(task_data.participants),
                    str(metadata_file)
                ))
                conn.commit()
            
            logger.info(f"任務數據存儲成功: {task_data.task_id}")
            return True
            
        except Exception as e:
            logger.error(f"存儲任務數據失敗: {e}")
            return False
    
    def store_conversation(self, conversation_data: ConversationData) -> bool:
        """存儲對話數據"""
        try:
            # 生成對話文件路徑
            conv_path = self.path_manager.generate_conversation_path(
                conversation_data.conversation_id, 
                conversation_data.created_at
            )
            conv_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存對話數據
            with open(conv_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(conversation_data), f, ensure_ascii=False, indent=2, default=str)
            
            # 在任務目錄中創建鏈接
            if conversation_data.task_id:
                task_conv_dir = self.path_manager.generate_task_path(conversation_data.task_id) / "conversations"
                task_conv_path = task_conv_dir / f"{conversation_data.conversation_id}.json"
                
                if not task_conv_path.exists():
                    os.link(str(conv_path), str(task_conv_path))
            
            # 存儲到數據庫
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO conversations 
                    (conversation_id, task_id, participants, message_count, created_at, updated_at, file_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    conversation_data.conversation_id,
                    conversation_data.task_id,
                    json.dumps(conversation_data.participants),
                    len(conversation_data.messages),
                    conversation_data.created_at,
                    conversation_data.updated_at,
                    str(conv_path)
                ))
                conn.commit()
            
            logger.info(f"對話數據存儲成功: {conversation_data.conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"存儲對話數據失敗: {e}")
            return False
    
    def store_file(self, file_data: FileData, source_path: str) -> bool:
        """存儲文件數據"""
        try:
            # 生成文件路徑
            target_path = self.path_manager.generate_file_path(file_data)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 複製文件
            shutil.copy2(source_path, target_path)
            
            # 計算校驗和
            checksum = self._calculate_checksum(target_path)
            file_data.checksum = checksum
            file_data.file_path = str(target_path)
            
            # 創建鏈接
            self.path_manager.create_file_links(file_data, target_path)
            
            # 存儲到數據庫
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO files 
                    (file_id, filename, file_type, file_size, task_id, file_path, checksum, created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_data.file_id,
                    file_data.filename,
                    file_data.file_type,
                    file_data.file_size,
                    file_data.task_id,
                    file_data.file_path,
                    file_data.checksum,
                    file_data.created_at,
                    json.dumps(file_data.metadata)
                ))
                conn.commit()
            
            logger.info(f"文件數據存儲成功: {file_data.filename}")
            return True
            
        except Exception as e:
            logger.error(f"存儲文件數據失敗: {e}")
            return False
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """計算文件校驗和"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def verify_data_integrity(self) -> Dict[str, Any]:
        """驗證數據完整性"""
        results = {
            "total_files": 0,
            "verified_files": 0,
            "corrupted_files": [],
            "missing_files": [],
            "orphaned_files": [],
            "database_consistency": True
        }
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT file_id, file_path, checksum FROM files")
                files = cursor.fetchall()
                
                results["total_files"] = len(files)
                
                for file_id, file_path, stored_checksum in files:
                    if not os.path.exists(file_path):
                        results["missing_files"].append(file_id)
                        continue
                    
                    current_checksum = self._calculate_checksum(Path(file_path))
                    if current_checksum == stored_checksum:
                        results["verified_files"] += 1
                    else:
                        results["corrupted_files"].append(file_id)
            
            logger.info(f"數據完整性驗證完成: {results}")
            return results
            
        except Exception as e:
            logger.error(f"數據完整性驗證失敗: {e}")
            results["database_consistency"] = False
            return results

class SearchIndexer:
    """搜尋索引器"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.index_path = Path(config.base_path) / "metadata" / "search_index"
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.db_path = Path(config.base_path) / "metadata" / "data_storage.db"
    
    def build_content_index(self) -> bool:
        """建立內容索引"""
        try:
            index_data = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "total_documents": 0,
                "terms": {}
            }
            
            # 索引任務內容
            self._index_tasks(index_data)
            
            # 索引對話內容
            self._index_conversations(index_data)
            
            # 索引文件內容
            self._index_files(index_data)
            
            # 保存索引
            index_file = self.index_path / "content_index.json"
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"內容索引建立完成: {index_data['total_documents']} 個文檔")
            return True
            
        except Exception as e:
            logger.error(f"建立內容索引失敗: {e}")
            return False
    
    def _index_tasks(self, index_data: Dict):
        """索引任務內容"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT task_id, title, description FROM tasks")
            tasks = cursor.fetchall()
            
            for task_id, title, description in tasks:
                content = f"{title} {description or ''}"
                self._add_to_index(index_data, task_id, content, "task")
                index_data["total_documents"] += 1
    
    def _index_conversations(self, index_data: Dict):
        """索引對話內容"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT conversation_id, file_path FROM conversations")
            conversations = cursor.fetchall()
            
            for conv_id, file_path in conversations:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            conv_data = json.load(f)
                            
                        content = ""
                        for message in conv_data.get("messages", []):
                            content += f" {message.get('content', '')}"
                        
                        self._add_to_index(index_data, conv_id, content, "conversation")
                        index_data["total_documents"] += 1
                        
                    except Exception as e:
                        logger.warning(f"索引對話失敗 {conv_id}: {e}")
    
    def _index_files(self, index_data: Dict):
        """索引文件內容"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_id, filename, file_path, file_type FROM files")
            files = cursor.fetchall()
            
            for file_id, filename, file_path, file_type in files:
                content = filename  # 基本索引文件名
                
                # 對於文本文件，嘗試索引內容
                if file_type in ['txt', 'md', 'py', 'js', 'html', 'css']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                            content += f" {file_content}"
                    except Exception as e:
                        logger.warning(f"讀取文件內容失敗 {file_id}: {e}")
                
                self._add_to_index(index_data, file_id, content, "file")
                index_data["total_documents"] += 1
    
    def _add_to_index(self, index_data: Dict, doc_id: str, content: str, doc_type: str):
        """添加到索引"""
        # 簡單的分詞（實際應用中應使用專業的分詞器）
        words = content.lower().split()
        
        for word in words:
            if len(word) < 2:  # 忽略太短的詞
                continue
                
            if word not in index_data["terms"]:
                index_data["terms"][word] = {
                    "frequency": 0,
                    "documents": []
                }
            
            index_data["terms"][word]["frequency"] += 1
            if doc_id not in index_data["terms"][word]["documents"]:
                index_data["terms"][word]["documents"].append(doc_id)
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """搜尋功能"""
        try:
            index_file = self.index_path / "content_index.json"
            if not index_file.exists():
                return []
            
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            query_words = query.lower().split()
            matching_docs = {}
            
            for word in query_words:
                if word in index_data["terms"]:
                    for doc_id in index_data["terms"][word]["documents"]:
                        if doc_id not in matching_docs:
                            matching_docs[doc_id] = 0
                        matching_docs[doc_id] += 1
            
            # 按匹配度排序
            sorted_docs = sorted(matching_docs.items(), key=lambda x: x[1], reverse=True)
            
            results = []
            for doc_id, score in sorted_docs[:limit]:
                results.append({
                    "document_id": doc_id,
                    "relevance_score": score,
                    "max_score": len(query_words)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"搜尋失敗: {e}")
            return []

class DataStorageTestSuite(unittest.TestCase):
    """數據存儲測試套件"""
    
    @classmethod
    def setUpClass(cls):
        """測試套件初始化"""
        cls.config = TestConfig()
        cls.data_storage = DataStorage(cls.config)
        cls.search_indexer = SearchIndexer(cls.config)
        
        # 初始化目錄結構
        cls.data_storage.path_manager.initialize_directory_structure()
        
        # 創建測試數據
        cls._create_test_data()
    
    @classmethod
    def _create_test_data(cls):
        """創建測試數據"""
        # 創建測試文件
        test_data_dir = Path(cls.config.test_data_path)
        test_data_dir.mkdir(exist_ok=True)
        
        # 創建各種類型的測試文件
        test_files = [
            ("test_document.txt", "這是一個測試文檔，包含PowerAutomation相關內容。"),
            ("test_code.py", "# PowerAutomation Python測試代碼\nprint('Hello World')"),
            ("test_data.json", '{"name": "PowerAutomation", "version": "2.0"}')
        ]
        
        for filename, content in test_files:
            file_path = test_data_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def test_01_directory_structure(self):
        """測試目錄結構創建"""
        base_path = Path(self.config.base_path)
        
        required_dirs = [
            "tasks",
            "conversations",
            "files",
            "metadata",
            "logs"
        ]
        
        for dir_name in required_dirs:
            dir_path = base_path / dir_name
            self.assertTrue(dir_path.exists(), f"目錄不存在: {dir_path}")
            self.assertTrue(dir_path.is_dir(), f"不是目錄: {dir_path}")
    
    def test_02_task_storage(self):
        """測試任務存儲"""
        task_data = TaskData(
            task_id="test_task_001",
            title="PowerAutomation測試任務",
            description="這是一個測試任務，用於驗證數據存儲功能",
            status="in_progress",
            priority="high",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            participants=["user1", "user2"],
            files=[],
            conversations=[]
        )
        
        result = self.data_storage.store_task(task_data)
        self.assertTrue(result, "任務存儲失敗")
        
        # 驗證任務目錄創建
        task_path = self.data_storage.path_manager.generate_task_path(task_data.task_id)
        self.assertTrue(task_path.exists(), "任務目錄未創建")
        
        # 驗證元數據文件
        metadata_file = task_path / "metadata.json"
        self.assertTrue(metadata_file.exists(), "任務元數據文件未創建")
    
    def test_03_conversation_storage(self):
        """測試對話存儲"""
        conversation_data = ConversationData(
            conversation_id="test_conv_001",
            task_id="test_task_001",
            participants=["user1", "user2"],
            messages=[
                {"sender": "user1", "content": "PowerAutomation功能測試", "timestamp": datetime.now().isoformat()},
                {"sender": "user2", "content": "收到，開始測試", "timestamp": datetime.now().isoformat()}
            ],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        result = self.data_storage.store_conversation(conversation_data)
        self.assertTrue(result, "對話存儲失敗")
        
        # 驗證對話文件創建
        conv_path = self.data_storage.path_manager.generate_conversation_path(
            conversation_data.conversation_id,
            conversation_data.created_at
        )
        self.assertTrue(conv_path.exists(), "對話文件未創建")
    
    def test_04_file_storage(self):
        """測試文件存儲"""
        test_file_path = Path(self.config.test_data_path) / "test_document.txt"
        
        file_data = FileData(
            file_id="test_file_001",
            filename="test_document.txt",
            file_type="txt",
            file_size=os.path.getsize(test_file_path),
            task_id="test_task_001",
            file_path="",
            checksum="",
            created_at=datetime.now(),
            metadata={"source": "test", "category": "document"}
        )
        
        result = self.data_storage.store_file(file_data, str(test_file_path))
        self.assertTrue(result, "文件存儲失敗")
        
        # 驗證文件複製
        target_path = self.data_storage.path_manager.generate_file_path(file_data)
        self.assertTrue(target_path.exists(), "文件未正確複製")
    
    def test_05_data_integrity(self):
        """測試數據完整性"""
        results = self.data_storage.verify_data_integrity()
        
        self.assertTrue(results["database_consistency"], "數據庫一致性檢查失敗")
        self.assertEqual(len(results["corrupted_files"]), 0, "發現損壞文件")
        self.assertEqual(len(results["missing_files"]), 0, "發現丟失文件")
    
    def test_06_search_index_building(self):
        """測試搜尋索引建立"""
        result = self.search_indexer.build_content_index()
        self.assertTrue(result, "搜尋索引建立失敗")
        
        # 驗證索引文件創建
        index_file = self.search_indexer.index_path / "content_index.json"
        self.assertTrue(index_file.exists(), "索引文件未創建")
        
        # 驗證索引內容
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        self.assertGreater(index_data["total_documents"], 0, "索引文檔數量為0")
        self.assertGreater(len(index_data["terms"]), 0, "索引詞彙數量為0")
    
    def test_07_search_functionality(self):
        """測試搜尋功能"""
        # 搜尋PowerAutomation相關內容
        results = self.search_indexer.search("PowerAutomation")
        self.assertGreater(len(results), 0, "搜尋結果為空")
        
        # 驗證搜尋結果格式
        for result in results:
            self.assertIn("document_id", result, "搜尋結果缺少document_id")
            self.assertIn("relevance_score", result, "搜尋結果缺少relevance_score")
    
    def test_08_performance_metrics(self):
        """測試性能指標"""
        start_time = time.time()
        
        # 測試大量數據的處理性能
        for i in range(100):
            task_data = TaskData(
                task_id=f"perf_task_{i:03d}",
                title=f"性能測試任務 {i}",
                description="性能測試用的任務數據",
                status="completed",
                priority="medium",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                participants=["test_user"],
                files=[],
                conversations=[]
            )
            self.data_storage.store_task(task_data)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 驗證性能指標
        self.assertLess(processing_time, 30, f"處理100個任務耗時過長: {processing_time:.2f}秒")
        
        # 測試搜尋性能
        start_time = time.time()
        results = self.search_indexer.search("性能測試")
        end_time = time.time()
        search_time = end_time - start_time
        
        self.assertLess(search_time, 1, f"搜尋耗時過長: {search_time:.2f}秒")
    
    @classmethod
    def tearDownClass(cls):
        """測試套件清理"""
        if cls.config.cleanup_on_exit:
            # 清理測試數據
            if os.path.exists(cls.config.base_path):
                shutil.rmtree(cls.config.base_path)
            if os.path.exists(cls.config.test_data_path):
                shutil.rmtree(cls.config.test_data_path)
            logger.info("測試數據清理完成")

def run_data_storage_tests():
    """運行數據存儲測試"""
    logger.info("開始運行PowerAutomation數據存儲測試")
    
    # 創建測試套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(DataStorageTestSuite)
    
    # 運行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 生成測試報告
    test_report = {
        "total_tests": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "success_rate": (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun if result.testsRun > 0 else 0,
        "execution_time": time.time(),
        "details": {
            "failures": [{"test": str(test), "error": error} for test, error in result.failures],
            "errors": [{"test": str(test), "error": error} for test, error in result.errors]
        }
    }
    
    # 保存測試報告
    report_file = "/home/ubuntu/data_storage_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(test_report, f, ensure_ascii=False, indent=2, default=str)
    
    logger.info(f"測試完成，成功率: {test_report['success_rate']:.2%}")
    logger.info(f"測試報告已保存: {report_file}")
    
    return test_report

if __name__ == "__main__":
    # 運行測試
    report = run_data_storage_tests()
    
    # 打印測試結果摘要
    print(f"\n{'='*50}")
    print("PowerAutomation 數據存儲測試結果摘要")
    print(f"{'='*50}")
    print(f"總測試數: {report['total_tests']}")
    print(f"失敗數: {report['failures']}")
    print(f"錯誤數: {report['errors']}")
    print(f"成功率: {report['success_rate']:.2%}")
    print(f"{'='*50}")

