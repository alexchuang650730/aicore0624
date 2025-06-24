"""
PowerAutomation Local MCP Data Storage

數據存儲管理模組，提供文件系統組織、搜索索引、備份恢復等功能

Author: Manus AI
Version: 1.0.0
Date: 2025-06-23
"""

import asyncio
import json
import logging
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import sqlite3
import hashlib

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.exceptions import StorageError, async_handle_exceptions
from shared.utils import ensure_directory, calculate_file_hash, format_bytes


class DataStorage:
    """數據存儲管理模組"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        初始化Data Storage
        
        Args:
            config: 存儲配置
            logger: 日誌器
        """
        self.config = config
        self.logger = logger
        
        # 配置參數
        self.base_path = config.get("base_path", "/home/ubuntu/powerautomation_data")
        self.index_enabled = config.get("index_enabled", True)
        self.backup_enabled = config.get("backup_enabled", True)
        self.cleanup_days = config.get("cleanup_days", 30)
        self.compression_enabled = config.get("compression_enabled", True)
        self.max_file_size = config.get("max_file_size", "100MB")
        self.allowed_extensions = config.get("allowed_extensions", [".pdf", ".png", ".jpg", ".jpeg", ".txt", ".md", ".json", ".csv"])
        
        # 路徑配置
        self.paths = config.get("paths", {})
        
        # 數據庫連接
        self.db_connection = None
        
        # 狀態信息
        self.status = {
            "initialized": False,
            "running": False,
            "total_files": 0,
            "total_size": 0,
            "indexed_files": 0,
            "last_cleanup": None,
            "last_backup": None
        }
    
    async def initialize(self) -> bool:
        """
        初始化Data Storage
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.logger.info("正在初始化Data Storage...")
            
            # 創建目錄結構
            await self._create_directory_structure()
            
            # 初始化數據庫
            if self.index_enabled:
                await self._initialize_database()
            
            # 掃描現有文件
            await self._scan_existing_files()
            
            self.status["initialized"] = True
            self.logger.info("Data Storage初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"Data Storage初始化失敗: {e}")
            return False
    
    async def start(self) -> bool:
        """
        啟動Data Storage
        
        Returns:
            bool: 啟動是否成功
        """
        try:
            if not self.status["initialized"]:
                raise StorageError("Data Storage未初始化")
            
            self.logger.info("正在啟動Data Storage...")
            
            # 啟動後台任務
            asyncio.create_task(self._background_tasks())
            
            self.status["running"] = True
            self.logger.info("Data Storage已啟動")
            return True
            
        except Exception as e:
            self.logger.error(f"啟動Data Storage失敗: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        停止Data Storage
        
        Returns:
            bool: 停止是否成功
        """
        try:
            self.logger.info("正在停止Data Storage...")
            
            # 關閉數據庫連接
            if self.db_connection:
                self.db_connection.close()
                self.db_connection = None
            
            self.status["running"] = False
            self.logger.info("Data Storage已停止")
            return True
            
        except Exception as e:
            self.logger.error(f"停止Data Storage失敗: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """
        獲取Data Storage狀態
        
        Returns:
            Dict[str, Any]: 狀態信息
        """
        try:
            status = self.status.copy()
            
            # 添加存儲統計
            status["storage_stats"] = await self._get_storage_stats()
            
            # 添加配置信息
            status["config"] = {
                "base_path": self.base_path,
                "index_enabled": self.index_enabled,
                "backup_enabled": self.backup_enabled,
                "cleanup_days": self.cleanup_days,
                "max_file_size": self.max_file_size
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"獲取Storage狀態失敗: {e}")
            return {"error": str(e)}
    
    async def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理存儲請求
        
        Args:
            method: 方法名
            params: 參數
            
        Returns:
            Dict[str, Any]: 響應數據
        """
        try:
            self.logger.debug(f"處理Storage請求: {method}")
            
            # 路由到相應的方法
            if method == "search":
                query = params.get("query", "")
                results = await self.search_files(query)
                return {"results": results, "count": len(results)}
                
            elif method == "store_file":
                file_path = params.get("file_path", "")
                category = params.get("category", "files")
                result = await self.store_file(file_path, category)
                return {"success": result, "message": "文件存儲完成"}
                
            elif method == "get_file":
                file_id = params.get("file_id", "")
                file_info = await self.get_file(file_id)
                return {"file_info": file_info}
                
            elif method == "delete_file":
                file_id = params.get("file_id", "")
                result = await self.delete_file(file_id)
                return {"success": result, "message": "文件刪除完成"}
                
            elif method == "backup":
                result = await self.create_backup()
                return {"success": result, "message": "備份創建完成"}
                
            elif method == "cleanup":
                result = await self.cleanup_old_files()
                return {"success": result, "message": "清理完成"}
                
            else:
                raise StorageError(f"未知的Storage方法: {method}")
            
        except Exception as e:
            self.logger.error(f"處理Storage請求失敗: {e}")
            raise
    
    @async_handle_exceptions(default_return=[])
    async def search_files(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索文件
        
        Args:
            query: 搜索查詢
            
        Returns:
            List[Dict[str, Any]]: 搜索結果
        """
        try:
            if not self.index_enabled or not self.db_connection:
                return await self._simple_file_search(query)
            
            self.logger.info(f"搜索文件: {query}")
            
            # 構建SQL查詢
            sql = """
            SELECT file_id, file_name, file_path, category, size, created_at, modified_at
            FROM files 
            WHERE file_name LIKE ? OR content LIKE ?
            ORDER BY modified_at DESC
            LIMIT 100
            """
            
            search_pattern = f"%{query}%"
            cursor = self.db_connection.cursor()
            cursor.execute(sql, (search_pattern, search_pattern))
            
            results = []
            for row in cursor.fetchall():
                result = {
                    "file_id": row[0],
                    "file_name": row[1],
                    "file_path": row[2],
                    "category": row[3],
                    "size": row[4],
                    "size_formatted": format_bytes(row[4]),
                    "created_at": row[5],
                    "modified_at": row[6]
                }
                results.append(result)
            
            self.logger.info(f"搜索完成，找到 {len(results)} 個結果")
            return results
            
        except Exception as e:
            self.logger.error(f"搜索文件失敗: {e}")
            raise StorageError(f"搜索文件失敗: {e}", operation="search")
    
    @async_handle_exceptions(default_return=False)
    async def store_file(self, file_path: str, category: str = "files") -> bool:
        """
        存儲文件
        
        Args:
            file_path: 文件路徑
            category: 文件分類
            
        Returns:
            bool: 存儲是否成功
        """
        try:
            if not os.path.exists(file_path):
                raise StorageError(f"文件不存在: {file_path}")
            
            self.logger.info(f"存儲文件: {file_path} -> {category}")
            
            # 檢查文件大小
            file_size = os.path.getsize(file_path)
            max_size = self._parse_size(self.max_file_size)
            if file_size > max_size:
                raise StorageError(f"文件過大: {format_bytes(file_size)} > {self.max_file_size}")
            
            # 檢查文件擴展名
            file_ext = Path(file_path).suffix.lower()
            if self.allowed_extensions and file_ext not in self.allowed_extensions:
                raise StorageError(f"不支持的文件類型: {file_ext}")
            
            # 創建目標目錄
            category_path = self.paths.get(category, category)
            target_dir = os.path.join(self.base_path, category_path)
            ensure_directory(target_dir)
            
            # 生成唯一文件名
            file_name = Path(file_path).name
            file_hash = calculate_file_hash(file_path)
            unique_name = f"{file_hash}_{file_name}"
            target_path = os.path.join(target_dir, unique_name)
            
            # 複製文件
            shutil.copy2(file_path, target_path)
            
            # 更新索引
            if self.index_enabled:
                await self._index_file(target_path, category, file_hash)
            
            # 更新統計
            self.status["total_files"] += 1
            self.status["total_size"] += file_size
            
            self.logger.info(f"✅ 文件存儲成功: {target_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"存儲文件失敗: {e}")
            raise StorageError(f"存儲文件失敗: {e}", path=file_path, operation="store")
    
    @async_handle_exceptions(default_return=None)
    async def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        獲取文件信息
        
        Args:
            file_id: 文件ID
            
        Returns:
            Optional[Dict[str, Any]]: 文件信息
        """
        try:
            if not self.index_enabled or not self.db_connection:
                return None
            
            sql = "SELECT * FROM files WHERE file_id = ?"
            cursor = self.db_connection.cursor()
            cursor.execute(sql, (file_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            file_info = {
                "file_id": row[0],
                "file_name": row[1],
                "file_path": row[2],
                "category": row[3],
                "size": row[4],
                "size_formatted": format_bytes(row[4]),
                "hash": row[5],
                "content": row[6],
                "created_at": row[7],
                "modified_at": row[8]
            }
            
            return file_info
            
        except Exception as e:
            self.logger.error(f"獲取文件信息失敗: {e}")
            raise StorageError(f"獲取文件信息失敗: {e}", operation="get_file")
    
    @async_handle_exceptions(default_return=False)
    async def delete_file(self, file_id: str) -> bool:
        """
        刪除文件
        
        Args:
            file_id: 文件ID
            
        Returns:
            bool: 刪除是否成功
        """
        try:
            # 獲取文件信息
            file_info = await self.get_file(file_id)
            if not file_info:
                raise StorageError(f"文件不存在: {file_id}")
            
            file_path = file_info["file_path"]
            
            # 刪除物理文件
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # 從索引中刪除
            if self.index_enabled and self.db_connection:
                sql = "DELETE FROM files WHERE file_id = ?"
                cursor = self.db_connection.cursor()
                cursor.execute(sql, (file_id,))
                self.db_connection.commit()
            
            # 更新統計
            self.status["total_files"] -= 1
            self.status["total_size"] -= file_info["size"]
            
            self.logger.info(f"✅ 文件刪除成功: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"刪除文件失敗: {e}")
            raise StorageError(f"刪除文件失敗: {e}", operation="delete_file")
    
    @async_handle_exceptions(default_return=False)
    async def create_backup(self) -> bool:
        """
        創建備份
        
        Returns:
            bool: 備份是否成功
        """
        try:
            if not self.backup_enabled:
                return True
            
            self.logger.info("正在創建備份...")
            
            # 創建備份目錄
            backup_dir = os.path.join(self.base_path, self.paths.get("backups", "backups"))
            ensure_directory(backup_dir)
            
            # 生成備份文件名
            timestamp = int(time.time())
            backup_name = f"powerautomation_backup_{timestamp}.tar.gz"
            backup_path = os.path.join(backup_dir, backup_name)
            
            # 創建壓縮備份
            import tarfile
            with tarfile.open(backup_path, "w:gz") as tar:
                for category, path in self.paths.items():
                    if category != "backups":
                        full_path = os.path.join(self.base_path, path)
                        if os.path.exists(full_path):
                            tar.add(full_path, arcname=path)
            
            # 備份數據庫
            if self.index_enabled and self.db_connection:
                db_backup_path = os.path.join(backup_dir, f"database_backup_{timestamp}.db")
                shutil.copy2(os.path.join(self.base_path, "index.db"), db_backup_path)
            
            self.status["last_backup"] = time.time()
            self.logger.info(f"✅ 備份創建成功: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"創建備份失敗: {e}")
            raise StorageError(f"創建備份失敗: {e}", operation="backup")
    
    @async_handle_exceptions(default_return=False)
    async def cleanup_old_files(self) -> bool:
        """
        清理舊文件
        
        Returns:
            bool: 清理是否成功
        """
        try:
            self.logger.info("正在清理舊文件...")
            
            cutoff_time = time.time() - (self.cleanup_days * 24 * 3600)
            cleaned_count = 0
            
            # 清理臨時文件
            temp_dir = os.path.join(self.base_path, self.paths.get("temp", "temp"))
            if os.path.exists(temp_dir):
                for file_name in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file_name)
                    if os.path.isfile(file_path):
                        if os.path.getmtime(file_path) < cutoff_time:
                            os.remove(file_path)
                            cleaned_count += 1
            
            # 清理舊日誌
            log_dir = os.path.join(self.base_path, self.paths.get("logs", "logs"))
            if os.path.exists(log_dir):
                for file_name in os.listdir(log_dir):
                    if file_name.endswith(".log"):
                        file_path = os.path.join(log_dir, file_name)
                        if os.path.getmtime(file_path) < cutoff_time:
                            os.remove(file_path)
                            cleaned_count += 1
            
            # 清理舊備份
            backup_dir = os.path.join(self.base_path, self.paths.get("backups", "backups"))
            if os.path.exists(backup_dir):
                backup_files = []
                for file_name in os.listdir(backup_dir):
                    if file_name.startswith("powerautomation_backup_"):
                        file_path = os.path.join(backup_dir, file_name)
                        backup_files.append((file_path, os.path.getmtime(file_path)))
                
                # 保留最新的5個備份
                backup_files.sort(key=lambda x: x[1], reverse=True)
                for file_path, _ in backup_files[5:]:
                    os.remove(file_path)
                    cleaned_count += 1
            
            self.status["last_cleanup"] = time.time()
            self.logger.info(f"✅ 清理完成，刪除了 {cleaned_count} 個文件")
            return True
            
        except Exception as e:
            self.logger.error(f"清理文件失敗: {e}")
            raise StorageError(f"清理文件失敗: {e}", operation="cleanup")
    
    async def _create_directory_structure(self):
        """創建目錄結構"""
        try:
            # 創建基礎目錄
            ensure_directory(self.base_path)
            
            # 創建子目錄
            for category, path in self.paths.items():
                full_path = os.path.join(self.base_path, path)
                ensure_directory(full_path)
            
        except Exception as e:
            raise StorageError(f"創建目錄結構失敗: {e}")
    
    async def _initialize_database(self):
        """初始化數據庫"""
        try:
            db_path = os.path.join(self.base_path, "index.db")
            self.db_connection = sqlite3.connect(db_path)
            
            # 創建文件索引表
            sql = """
            CREATE TABLE IF NOT EXISTS files (
                file_id TEXT PRIMARY KEY,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                category TEXT NOT NULL,
                size INTEGER NOT NULL,
                hash TEXT NOT NULL,
                content TEXT,
                created_at REAL NOT NULL,
                modified_at REAL NOT NULL
            )
            """
            
            self.db_connection.execute(sql)
            
            # 創建索引
            self.db_connection.execute("CREATE INDEX IF NOT EXISTS idx_file_name ON files(file_name)")
            self.db_connection.execute("CREATE INDEX IF NOT EXISTS idx_category ON files(category)")
            self.db_connection.execute("CREATE INDEX IF NOT EXISTS idx_hash ON files(hash)")
            
            self.db_connection.commit()
            
        except Exception as e:
            raise StorageError(f"初始化數據庫失敗: {e}")
    
    async def _scan_existing_files(self):
        """掃描現有文件"""
        try:
            total_files = 0
            total_size = 0
            
            for category, path in self.paths.items():
                full_path = os.path.join(self.base_path, path)
                if os.path.exists(full_path):
                    for root, dirs, files in os.walk(full_path):
                        for file_name in files:
                            file_path = os.path.join(root, file_name)
                            if os.path.isfile(file_path):
                                total_files += 1
                                total_size += os.path.getsize(file_path)
            
            self.status["total_files"] = total_files
            self.status["total_size"] = total_size
            
        except Exception as e:
            self.logger.error(f"掃描現有文件失敗: {e}")
    
    async def _index_file(self, file_path: str, category: str, file_hash: str):
        """索引文件"""
        try:
            if not self.db_connection:
                return
            
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            created_at = os.path.getctime(file_path)
            modified_at = os.path.getmtime(file_path)
            
            # 生成文件ID
            file_id = hashlib.md5(f"{file_path}_{file_hash}".encode()).hexdigest()
            
            # 提取文件內容（如果是文本文件）
            content = ""
            try:
                if file_name.endswith(('.txt', '.md', '.json', '.csv')):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:10000]  # 只索引前10000字符
            except:
                pass
            
            # 插入或更新索引
            sql = """
            INSERT OR REPLACE INTO files 
            (file_id, file_name, file_path, category, size, hash, content, created_at, modified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            self.db_connection.execute(sql, (
                file_id, file_name, file_path, category, file_size,
                file_hash, content, created_at, modified_at
            ))
            self.db_connection.commit()
            
            self.status["indexed_files"] += 1
            
        except Exception as e:
            self.logger.error(f"索引文件失敗: {e}")
    
    async def _simple_file_search(self, query: str) -> List[Dict[str, Any]]:
        """簡單文件搜索（不使用數據庫）"""
        try:
            results = []
            
            for category, path in self.paths.items():
                full_path = os.path.join(self.base_path, path)
                if os.path.exists(full_path):
                    for root, dirs, files in os.walk(full_path):
                        for file_name in files:
                            if query.lower() in file_name.lower():
                                file_path = os.path.join(root, file_name)
                                file_size = os.path.getsize(file_path)
                                
                                result = {
                                    "file_id": hashlib.md5(file_path.encode()).hexdigest(),
                                    "file_name": file_name,
                                    "file_path": file_path,
                                    "category": category,
                                    "size": file_size,
                                    "size_formatted": format_bytes(file_size),
                                    "created_at": os.path.getctime(file_path),
                                    "modified_at": os.path.getmtime(file_path)
                                }
                                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"簡單文件搜索失敗: {e}")
            return []
    
    async def _get_storage_stats(self) -> Dict[str, Any]:
        """獲取存儲統計"""
        try:
            stats = {}
            
            for category, path in self.paths.items():
                full_path = os.path.join(self.base_path, path)
                if os.path.exists(full_path):
                    file_count = 0
                    total_size = 0
                    
                    for root, dirs, files in os.walk(full_path):
                        for file_name in files:
                            file_path = os.path.join(root, file_name)
                            if os.path.isfile(file_path):
                                file_count += 1
                                total_size += os.path.getsize(file_path)
                    
                    stats[category] = {
                        "file_count": file_count,
                        "total_size": total_size,
                        "total_size_formatted": format_bytes(total_size)
                    }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"獲取存儲統計失敗: {e}")
            return {}
    
    async def _background_tasks(self):
        """後台任務"""
        try:
            while self.status["running"]:
                # 每小時執行一次清理
                if self.status["last_cleanup"] is None or \
                   time.time() - self.status["last_cleanup"] > 3600:
                    await self.cleanup_old_files()
                
                # 每天執行一次備份
                if self.backup_enabled and \
                   (self.status["last_backup"] is None or \
                    time.time() - self.status["last_backup"] > 86400):
                    await self.create_backup()
                
                # 等待1小時
                await asyncio.sleep(3600)
                
        except Exception as e:
            self.logger.error(f"後台任務執行失敗: {e}")
    
    def _parse_size(self, size_str: str) -> int:
        """解析大小字符串為字節數"""
        size_str = size_str.upper().strip()
        
        if size_str.endswith('B'):
            size_str = size_str[:-1]
        
        multipliers = {
            'K': 1024,
            'M': 1024 ** 2,
            'G': 1024 ** 3,
            'T': 1024 ** 4
        }
        
        for suffix, multiplier in multipliers.items():
            if size_str.endswith(suffix):
                number = float(size_str[:-1])
                return int(number * multiplier)
        
        return int(float(size_str))

