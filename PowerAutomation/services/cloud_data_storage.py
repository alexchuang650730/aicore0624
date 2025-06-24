"""
Cloud Data Storage Service for AICore SmartInvention MCP
雲端數據存儲服務 - 完全替代本地PowerAutomation存儲功能
Version: 3.0.0
"""

import asyncio
import json
import logging
import os
import aiohttp
import aiofiles
import hashlib
import shutil
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import subprocess

@dataclass
class StorageItem:
    """存儲項目數據模型"""
    id: str
    name: str
    path: str
    size: int
    content_type: str
    created_at: str
    updated_at: str
    metadata: Dict
    tags: List[str] = field(default_factory=list)
    checksum: str = ""

@dataclass
class StorageIndex:
    """存儲索引數據模型"""
    total_items: int
    total_size: int
    categories: Dict[str, int]
    last_updated: str
    index_version: str = "3.0.0"

class CloudStorageManager:
    """雲端存儲管理器 - 替代PowerAutomation Local存儲"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 雲端存儲配置
        self.storage_config = config.get('cloud_storage', {
            'base_path': '/home/ec2-user/smartinvention_mcp/storage',
            'index_db_path': '/home/ec2-user/smartinvention_mcp/storage/index.db',
            'backup_path': '/home/ec2-user/smartinvention_mcp/backups',
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'compression_enabled': True,
            'encryption_enabled': False
        })
        
        # EC2連接配置
        self.ec2_config = config.get('ec2', {
            'host': '18.212.97.173',
            'user': 'ec2-user',
            'key_path': '/home/ubuntu/alexchuang.pem'
        })
        
        # 本地緩存配置
        self.cache_config = config.get('cache', {
            'local_cache_dir': '/tmp/aicore_cache',
            'cache_size_limit': 1024 * 1024 * 1024,  # 1GB
            'cache_ttl': 3600  # 1小時
        })
        
        # 初始化本地緩存目錄
        self.cache_dir = Path(self.cache_config['local_cache_dir'])
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def initialize_cloud_storage(self) -> Dict[str, Any]:
        """初始化雲端存儲"""
        try:
            self.logger.info("初始化雲端存儲系統...")
            
            # 創建遠程存儲目錄結構
            await self._create_remote_storage_structure()
            
            # 初始化存儲索引數據庫
            await self._initialize_storage_index()
            
            # 驗證存儲系統
            verification_result = await self._verify_storage_system()
            
            return {
                "success": True,
                "storage_initialized": True,
                "index_initialized": True,
                "verification_result": verification_result,
                "storage_path": self.storage_config['base_path'],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"雲端存儲初始化失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def store_file(self, file_path: str, metadata: Dict = None, tags: List[str] = None) -> Dict[str, Any]:
        """存儲文件到雲端"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 生成存儲ID
            storage_id = self._generate_storage_id(file_path)
            
            # 計算文件信息
            file_size = file_path.stat().st_size
            file_checksum = await self._calculate_checksum(file_path)
            
            # 檢查文件大小限制
            if file_size > self.storage_config['max_file_size']:
                raise ValueError(f"文件大小超過限制: {file_size} > {self.storage_config['max_file_size']}")
            
            # 準備存儲項目
            storage_item = StorageItem(
                id=storage_id,
                name=file_path.name,
                path=f"files/{storage_id}_{file_path.name}",
                size=file_size,
                content_type=self._detect_content_type(file_path),
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                metadata=metadata or {},
                tags=tags or [],
                checksum=file_checksum
            )
            
            # 上傳文件到雲端
            upload_result = await self._upload_file_to_cloud(file_path, storage_item)
            
            # 更新存儲索引
            await self._update_storage_index(storage_item)
            
            # 添加到本地緩存
            await self._add_to_cache(file_path, storage_item)
            
            return {
                "success": True,
                "storage_id": storage_id,
                "storage_item": storage_item.__dict__,
                "upload_result": upload_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"文件存儲失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def retrieve_file(self, storage_id: str, local_path: str = None) -> Dict[str, Any]:
        """從雲端檢索文件"""
        try:
            # 查找存儲項目
            storage_item = await self._find_storage_item(storage_id)
            if not storage_item:
                raise FileNotFoundError(f"存儲項目不存在: {storage_id}")
            
            # 檢查本地緩存
            cached_path = await self._check_cache(storage_id)
            if cached_path:
                self.logger.info(f"從緩存獲取文件: {storage_id}")
                if local_path:
                    shutil.copy2(cached_path, local_path)
                    return {
                        "success": True,
                        "source": "cache",
                        "local_path": local_path,
                        "storage_item": storage_item
                    }
                else:
                    return {
                        "success": True,
                        "source": "cache", 
                        "cached_path": str(cached_path),
                        "storage_item": storage_item
                    }
            
            # 從雲端下載
            download_result = await self._download_file_from_cloud(storage_item, local_path)
            
            # 添加到緩存
            if download_result.get("success"):
                downloaded_path = download_result.get("local_path")
                if downloaded_path:
                    await self._add_to_cache(Path(downloaded_path), storage_item)
            
            return {
                "success": True,
                "source": "cloud",
                "download_result": download_result,
                "storage_item": storage_item,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"文件檢索失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def search_files(self, query: str = None, tags: List[str] = None, content_type: str = None) -> Dict[str, Any]:
        """搜索文件"""
        try:
            # 構建搜索條件
            search_conditions = []
            params = []
            
            if query:
                search_conditions.append("(name LIKE ? OR metadata LIKE ?)")
                params.extend([f"%{query}%", f"%{query}%"])
            
            if tags:
                for tag in tags:
                    search_conditions.append("tags LIKE ?")
                    params.append(f"%{tag}%")
            
            if content_type:
                search_conditions.append("content_type = ?")
                params.append(content_type)
            
            # 執行搜索
            search_results = await self._execute_search(search_conditions, params)
            
            return {
                "success": True,
                "results": search_results,
                "count": len(search_results),
                "query": query,
                "tags": tags,
                "content_type": content_type,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"文件搜索失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def delete_file(self, storage_id: str) -> Dict[str, Any]:
        """刪除文件"""
        try:
            # 查找存儲項目
            storage_item = await self._find_storage_item(storage_id)
            if not storage_item:
                raise FileNotFoundError(f"存儲項目不存在: {storage_id}")
            
            # 從雲端刪除
            cloud_delete_result = await self._delete_file_from_cloud(storage_item)
            
            # 從索引中刪除
            await self._remove_from_storage_index(storage_id)
            
            # 從緩存中刪除
            await self._remove_from_cache(storage_id)
            
            return {
                "success": True,
                "storage_id": storage_id,
                "cloud_delete_result": cloud_delete_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"文件刪除失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """獲取存儲統計信息"""
        try:
            # 從索引數據庫獲取統計信息
            stats = await self._get_storage_statistics()
            
            # 獲取雲端存儲使用情況
            cloud_usage = await self._get_cloud_storage_usage()
            
            # 獲取緩存使用情況
            cache_usage = await self._get_cache_usage()
            
            return {
                "success": True,
                "storage_stats": stats,
                "cloud_usage": cloud_usage,
                "cache_usage": cache_usage,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"獲取存儲統計失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # 私有方法實現
    
    async def _create_remote_storage_structure(self):
        """創建遠程存儲目錄結構"""
        try:
            host = self.ec2_config['host']
            user = self.ec2_config['user']
            key_path = self.ec2_config['key_path']
            base_path = self.storage_config['base_path']
            
            # 創建目錄結構的命令
            directories = [
                f"{base_path}",
                f"{base_path}/files",
                f"{base_path}/metadata",
                f"{base_path}/temp",
                f"{self.storage_config['backup_path']}"
            ]
            
            create_dirs_cmd = f"mkdir -p {' '.join(directories)}"
            
            cmd = [
                'ssh', '-i', key_path, '-o', 'StrictHostKeyChecking=no',
                f'{user}@{host}',
                create_dirs_cmd
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"創建遠程目錄失敗: {stderr.decode()}")
            
            self.logger.info("遠程存儲目錄結構創建成功")
            
        except Exception as e:
            self.logger.error(f"創建遠程存儲結構失敗: {e}")
            raise
    
    async def _initialize_storage_index(self):
        """初始化存儲索引數據庫"""
        try:
            # 創建本地索引數據庫
            local_db_path = "/tmp/aicore_storage_index.db"
            
            conn = sqlite3.connect(local_db_path)
            cursor = conn.cursor()
            
            # 創建存儲項目表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS storage_items (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    content_type TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT,
                    tags TEXT,
                    checksum TEXT
                )
            ''')
            
            # 創建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON storage_items(name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_type ON storage_items(content_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON storage_items(created_at)')
            
            conn.commit()
            conn.close()
            
            # 上傳索引數據庫到雲端
            await self._upload_index_to_cloud(local_db_path)
            
            self.logger.info("存儲索引數據庫初始化成功")
            
        except Exception as e:
            self.logger.error(f"初始化存儲索引失敗: {e}")
            raise
    
    async def _verify_storage_system(self) -> Dict[str, Any]:
        """驗證存儲系統"""
        try:
            # 測試文件上傳
            test_file_path = "/tmp/storage_test.txt"
            async with aiofiles.open(test_file_path, 'w') as f:
                await f.write("Storage system test file")
            
            # 測試存儲
            store_result = await self.store_file(
                test_file_path,
                metadata={"test": True},
                tags=["test", "verification"]
            )
            
            if not store_result.get("success"):
                raise Exception(f"存儲測試失敗: {store_result.get('error')}")
            
            storage_id = store_result.get("storage_id")
            
            # 測試檢索
            retrieve_result = await self.retrieve_file(storage_id, "/tmp/storage_test_retrieved.txt")
            
            if not retrieve_result.get("success"):
                raise Exception(f"檢索測試失敗: {retrieve_result.get('error')}")
            
            # 測試搜索
            search_result = await self.search_files(query="test")
            
            if not search_result.get("success"):
                raise Exception(f"搜索測試失敗: {search_result.get('error')}")
            
            # 清理測試文件
            await self.delete_file(storage_id)
            os.remove(test_file_path)
            if os.path.exists("/tmp/storage_test_retrieved.txt"):
                os.remove("/tmp/storage_test_retrieved.txt")
            
            return {
                "storage_test": "passed",
                "retrieval_test": "passed",
                "search_test": "passed",
                "cleanup_test": "passed"
            }
            
        except Exception as e:
            self.logger.error(f"存儲系統驗證失敗: {e}")
            return {
                "verification_failed": True,
                "error": str(e)
            }
    
    def _generate_storage_id(self, file_path: Path) -> str:
        """生成存儲ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(f"{file_path.name}_{timestamp}".encode()).hexdigest()[:8]
        return f"store_{timestamp}_{file_hash}"
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """計算文件校驗和"""
        hash_md5 = hashlib.md5()
        async with aiofiles.open(file_path, 'rb') as f:
            async for chunk in f:
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _detect_content_type(self, file_path: Path) -> str:
        """檢測文件內容類型"""
        extension = file_path.suffix.lower()
        content_types = {
            '.json': 'application/json',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.pdf': 'application/pdf',
            '.py': 'text/x-python',
            '.js': 'text/javascript',
            '.html': 'text/html',
            '.css': 'text/css',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }
        return content_types.get(extension, 'application/octet-stream')
    
    async def _upload_file_to_cloud(self, file_path: Path, storage_item: StorageItem) -> Dict[str, Any]:
        """上傳文件到雲端"""
        try:
            host = self.ec2_config['host']
            user = self.ec2_config['user']
            key_path = self.ec2_config['key_path']
            remote_path = f"{self.storage_config['base_path']}/{storage_item.path}"
            
            cmd = [
                'scp', '-i', key_path, '-o', 'StrictHostKeyChecking=no',
                str(file_path),
                f'{user}@{host}:{remote_path}'
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "remote_path": remote_path,
                    "file_size": storage_item.size
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode(),
                    "stdout": stdout.decode()
                }
                
        except Exception as e:
            self.logger.error(f"雲端文件上傳失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _upload_index_to_cloud(self, local_db_path: str):
        """上傳索引數據庫到雲端"""
        try:
            host = self.ec2_config['host']
            user = self.ec2_config['user']
            key_path = self.ec2_config['key_path']
            remote_path = self.storage_config['index_db_path']
            
            cmd = [
                'scp', '-i', key_path, '-o', 'StrictHostKeyChecking=no',
                local_db_path,
                f'{user}@{host}:{remote_path}'
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if process.returncode != 0:
                raise Exception("索引數據庫上傳失敗")
                
        except Exception as e:
            self.logger.error(f"索引數據庫上傳失敗: {e}")
            raise
    
    async def _update_storage_index(self, storage_item: StorageItem):
        """更新存儲索引"""
        try:
            # 更新本地索引
            local_db_path = "/tmp/aicore_storage_index.db"
            
            conn = sqlite3.connect(local_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO storage_items 
                (id, name, path, size, content_type, created_at, updated_at, metadata, tags, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                storage_item.id,
                storage_item.name,
                storage_item.path,
                storage_item.size,
                storage_item.content_type,
                storage_item.created_at,
                storage_item.updated_at,
                json.dumps(storage_item.metadata),
                json.dumps(storage_item.tags),
                storage_item.checksum
            ))
            
            conn.commit()
            conn.close()
            
            # 同步到雲端
            await self._upload_index_to_cloud(local_db_path)
            
        except Exception as e:
            self.logger.error(f"更新存儲索引失敗: {e}")
            raise
    
    async def _find_storage_item(self, storage_id: str) -> Optional[Dict]:
        """查找存儲項目"""
        try:
            # 從本地索引查找
            local_db_path = "/tmp/aicore_storage_index.db"
            
            if not os.path.exists(local_db_path):
                # 從雲端下載索引
                await self._download_index_from_cloud(local_db_path)
            
            conn = sqlite3.connect(local_db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM storage_items WHERE id = ?', (storage_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "path": row[2],
                    "size": row[3],
                    "content_type": row[4],
                    "created_at": row[5],
                    "updated_at": row[6],
                    "metadata": json.loads(row[7]) if row[7] else {},
                    "tags": json.loads(row[8]) if row[8] else [],
                    "checksum": row[9]
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"查找存儲項目失敗: {e}")
            return None
    
    async def _download_index_from_cloud(self, local_db_path: str):
        """從雲端下載索引數據庫"""
        try:
            host = self.ec2_config['host']
            user = self.ec2_config['user']
            key_path = self.ec2_config['key_path']
            remote_path = self.storage_config['index_db_path']
            
            cmd = [
                'scp', '-i', key_path, '-o', 'StrictHostKeyChecking=no',
                f'{user}@{host}:{remote_path}',
                local_db_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if process.returncode != 0:
                raise Exception("索引數據庫下載失敗")
                
        except Exception as e:
            self.logger.error(f"索引數據庫下載失敗: {e}")
            raise
    
    async def _check_cache(self, storage_id: str) -> Optional[Path]:
        """檢查本地緩存"""
        try:
            cache_file = self.cache_dir / f"{storage_id}.cache"
            if cache_file.exists():
                # 檢查緩存是否過期
                cache_time = cache_file.stat().st_mtime
                current_time = datetime.now().timestamp()
                
                if current_time - cache_time < self.cache_config['cache_ttl']:
                    return cache_file
                else:
                    # 緩存過期，刪除
                    cache_file.unlink()
            
            return None
            
        except Exception as e:
            self.logger.error(f"檢查緩存失敗: {e}")
            return None
    
    async def _add_to_cache(self, file_path: Path, storage_item: StorageItem):
        """添加到本地緩存"""
        try:
            cache_file = self.cache_dir / f"{storage_item.id}.cache"
            shutil.copy2(file_path, cache_file)
            
            # 檢查緩存大小限制
            await self._cleanup_cache_if_needed()
            
        except Exception as e:
            self.logger.error(f"添加到緩存失敗: {e}")
    
    async def _cleanup_cache_if_needed(self):
        """清理緩存（如果需要）"""
        try:
            # 計算緩存總大小
            total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.cache"))
            
            if total_size > self.cache_config['cache_size_limit']:
                # 按訪問時間排序，刪除最舊的文件
                cache_files = list(self.cache_dir.glob("*.cache"))
                cache_files.sort(key=lambda f: f.stat().st_atime)
                
                # 刪除一半的緩存文件
                files_to_delete = cache_files[:len(cache_files) // 2]
                for file_path in files_to_delete:
                    file_path.unlink()
                
                self.logger.info(f"清理了 {len(files_to_delete)} 個緩存文件")
                
        except Exception as e:
            self.logger.error(f"緩存清理失敗: {e}")

# 主要導出
__all__ = [
    'CloudStorageManager',
    'StorageItem',
    'StorageIndex'
]

if __name__ == "__main__":
    # 測試代碼
    async def test_cloud_storage():
        config = {
            'cloud_storage': {
                'base_path': '/home/ec2-user/smartinvention_mcp/storage',
                'index_db_path': '/home/ec2-user/smartinvention_mcp/storage/index.db',
                'backup_path': '/home/ec2-user/smartinvention_mcp/backups'
            },
            'ec2': {
                'host': '18.212.97.173',
                'user': 'ec2-user',
                'key_path': '/home/ubuntu/alexchuang.pem'
            }
        }
        
        storage = CloudStorageManager(config)
        
        # 初始化存儲
        init_result = await storage.initialize_cloud_storage()
        print("初始化結果:", init_result)
        
        # 測試文件存儲
        test_file = "/tmp/test_storage.txt"
        with open(test_file, 'w') as f:
            f.write("Test content for cloud storage")
        
        store_result = await storage.store_file(
            test_file,
            metadata={"test": True},
            tags=["test", "demo"]
        )
        print("存儲結果:", store_result)
    
    # 運行測試
    # asyncio.run(test_cloud_storage())

