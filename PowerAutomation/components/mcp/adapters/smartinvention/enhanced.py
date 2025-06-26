#!/usr/bin/env python3
"""
Enhanced Smartinvention MCP - 增強版智能發明MCP
提供完整的任務管理API功能，包括任務列表、存儲位置、對話歷史和檔案搜尋
"""

import asyncio
import json
import logging
import os
import aiohttp
import aiofiles
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import paramiko
import re

@dataclass
class TaskInfo:
    """任務信息模型"""
    task_id: str
    task_name: str
    cluster_name: str
    description: str
    status: str
    created_at: str
    storage_path: str
    conversations_count: int = 0
    files_count: int = 0
    metadata: Dict = field(default_factory=dict)

@dataclass
class ConversationInfo:
    """對話信息模型"""
    conversation_id: str
    task_id: str
    file_path: str
    timestamp: str
    participants: List[str] = field(default_factory=list)
    message_count: int = 0
    topics: List[str] = field(default_factory=list)
    summary: str = ""

@dataclass
class FileInfo:
    """檔案信息模型"""
    file_id: str
    task_id: str
    file_path: str
    file_name: str
    file_type: str
    file_size: int
    created_at: str
    modified_at: str
    category: str = ""

class TaskStorageManager:
    """任務存儲管理器"""
    
    def __init__(self, ec2_config: Dict):
        self.ec2_config = ec2_config
        self.ssh_client = None
        self.logger = logging.getLogger(__name__)
        self.base_path = "/home/ec2-user/smartinvention_mcp/tasks"
        
    async def connect_ec2(self) -> Dict[str, Any]:
        """連接到EC2"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.ssh_client.connect(
                hostname=self.ec2_config.get("host", "18.212.97.173"),
                username=self.ec2_config.get("username", "ec2-user"),
                key_filename=self.ec2_config.get("key_file", "/home/ubuntu/alexchuang.pem"),
                timeout=30
            )
            
            return {"success": True, "message": "EC2連接成功"}
            
        except Exception as e:
            self.logger.error(f"EC2連接失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def disconnect_ec2(self):
        """斷開EC2連接"""
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """執行SSH命令"""
        try:
            if not self.ssh_client:
                connect_result = await self.connect_ec2()
                if not connect_result["success"]:
                    return connect_result
            
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            return {
                "success": True,
                "output": output,
                "error": error,
                "command": command
            }
            
        except Exception as e:
            self.logger.error(f"命令執行失敗: {e}")
            return {"success": False, "error": str(e)}

class TaskListAPI:
    """任務列表API"""
    
    def __init__(self, storage_manager: TaskStorageManager):
        self.storage_manager = storage_manager
        self.logger = logging.getLogger(__name__)
    
    async def get_all_tasks(self) -> Dict[str, Any]:
        """獲取所有任務列表"""
        try:
            # 獲取任務聚類分析文件
            command = f"cat {self.storage_manager.base_path}/manus_task_clustering_analysis_*.json"
            result = await self.storage_manager.execute_command(command)
            
            if not result["success"]:
                return {"success": False, "error": "無法讀取任務數據"}
            
            # 解析任務數據
            task_data = json.loads(result["output"])
            task_groups = task_data.get("task_groups", {})
            
            tasks = []
            for task_id, task_info in task_groups.items():
                # 獲取任務存儲路徑
                storage_path = f"{self.storage_manager.base_path}/{task_id}"
                
                # 統計對話和檔案數量
                conversations_count = await self._count_conversations(task_id)
                files_count = await self._count_files(task_id)
                
                task = TaskInfo(
                    task_id=task_id,
                    task_name=task_info.get("cluster_name", ""),
                    cluster_name=task_info.get("cluster_name", ""),
                    description=task_info.get("description", ""),
                    status=task_info.get("status", "unknown"),
                    created_at=task_info.get("created_at", ""),
                    storage_path=storage_path,
                    conversations_count=conversations_count,
                    files_count=files_count,
                    metadata=task_info
                )
                tasks.append(task)
            
            return {
                "success": True,
                "tasks": [task.__dict__ for task in tasks],
                "total_count": len(tasks),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"獲取任務列表失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_task_by_id(self, task_id: str) -> Dict[str, Any]:
        """根據ID獲取特定任務"""
        try:
            all_tasks_result = await self.get_all_tasks()
            if not all_tasks_result["success"]:
                return all_tasks_result
            
            for task in all_tasks_result["tasks"]:
                if task["task_id"] == task_id:
                    return {
                        "success": True,
                        "task": task,
                        "timestamp": datetime.now().isoformat()
                    }
            
            return {
                "success": False,
                "error": f"任務 {task_id} 不存在"
            }
            
        except Exception as e:
            self.logger.error(f"獲取任務失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_tasks(self, keyword: str) -> Dict[str, Any]:
        """搜尋任務"""
        try:
            all_tasks_result = await self.get_all_tasks()
            if not all_tasks_result["success"]:
                return all_tasks_result
            
            matched_tasks = []
            for task in all_tasks_result["tasks"]:
                if (keyword.lower() in task["task_name"].lower() or 
                    keyword.lower() in task["description"].lower()):
                    matched_tasks.append(task)
            
            return {
                "success": True,
                "tasks": matched_tasks,
                "total_count": len(matched_tasks),
                "search_keyword": keyword,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"搜尋任務失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def _count_conversations(self, task_id: str) -> int:
        """統計任務的對話數量"""
        try:
            command = f"find {self.storage_manager.base_path}/{task_id}/conversations_analysis/raw_conversations -name '*.json' 2>/dev/null | wc -l"
            result = await self.storage_manager.execute_command(command)
            
            if result["success"]:
                return int(result["output"].strip())
            return 0
            
        except:
            return 0
    
    async def _count_files(self, task_id: str) -> int:
        """統計任務的檔案數量"""
        try:
            command = f"find {self.storage_manager.base_path}/{task_id} -type f 2>/dev/null | wc -l"
            result = await self.storage_manager.execute_command(command)
            
            if result["success"]:
                return int(result["output"].strip())
            return 0
            
        except:
            return 0

class ConversationAPI:
    """對話歷史API"""
    
    def __init__(self, storage_manager: TaskStorageManager):
        self.storage_manager = storage_manager
        self.logger = logging.getLogger(__name__)
    
    async def get_task_conversations(self, task_id: str) -> Dict[str, Any]:
        """獲取任務的所有對話"""
        try:
            conversations_path = f"{self.storage_manager.base_path}/{task_id}/conversations_analysis/raw_conversations"
            
            # 列出所有對話文件
            command = f"find {conversations_path} -name '*.json' 2>/dev/null"
            result = await self.storage_manager.execute_command(command)
            
            if not result["success"]:
                return {"success": False, "error": "無法讀取對話目錄"}
            
            conversation_files = result["output"].strip().split('\n')
            conversations = []
            
            for file_path in conversation_files:
                if file_path:  # 確保不是空行
                    conversation_info = await self._parse_conversation_file(task_id, file_path)
                    if conversation_info:
                        conversations.append(conversation_info)
            
            return {
                "success": True,
                "task_id": task_id,
                "conversations": conversations,
                "total_count": len(conversations),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"獲取對話失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_conversation_content(self, task_id: str, conversation_id: str) -> Dict[str, Any]:
        """獲取特定對話的內容"""
        try:
            conversations_result = await self.get_task_conversations(task_id)
            if not conversations_result["success"]:
                return conversations_result
            
            # 找到對應的對話
            target_conversation = None
            for conv in conversations_result["conversations"]:
                if conv["conversation_id"] == conversation_id:
                    target_conversation = conv
                    break
            
            if not target_conversation:
                return {"success": False, "error": f"對話 {conversation_id} 不存在"}
            
            # 讀取對話內容
            command = f"cat '{target_conversation['file_path']}'"
            result = await self.storage_manager.execute_command(command)
            
            if not result["success"]:
                return {"success": False, "error": "無法讀取對話內容"}
            
            try:
                conversation_content = json.loads(result["output"])
            except:
                conversation_content = {"raw_content": result["output"]}
            
            return {
                "success": True,
                "task_id": task_id,
                "conversation_id": conversation_id,
                "conversation_info": target_conversation,
                "content": conversation_content,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"獲取對話內容失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_conversations(self, task_id: str, keyword: str) -> Dict[str, Any]:
        """搜尋任務中的對話"""
        try:
            conversations_path = f"{self.storage_manager.base_path}/{task_id}/conversations_analysis/raw_conversations"
            
            # 搜尋包含關鍵詞的對話文件
            command = f"grep -r -l '{keyword}' {conversations_path} 2>/dev/null"
            result = await self.storage_manager.execute_command(command)
            
            if not result["success"]:
                return {"success": True, "conversations": [], "total_count": 0}
            
            matched_files = result["output"].strip().split('\n')
            conversations = []
            
            for file_path in matched_files:
                if file_path:
                    conversation_info = await self._parse_conversation_file(task_id, file_path)
                    if conversation_info:
                        conversations.append(conversation_info)
            
            return {
                "success": True,
                "task_id": task_id,
                "search_keyword": keyword,
                "conversations": conversations,
                "total_count": len(conversations),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"搜尋對話失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def _parse_conversation_file(self, task_id: str, file_path: str) -> Optional[Dict]:
        """解析對話文件信息"""
        try:
            # 獲取文件基本信息
            command = f"stat '{file_path}' --format='%Y %s'"
            result = await self.storage_manager.execute_command(command)
            
            if not result["success"]:
                return None
            
            stat_info = result["output"].strip().split()
            modified_time = datetime.fromtimestamp(int(stat_info[0])).isoformat()
            file_size = int(stat_info[1])
            
            # 生成對話ID
            conversation_id = Path(file_path).stem
            
            return {
                "conversation_id": conversation_id,
                "task_id": task_id,
                "file_path": file_path,
                "timestamp": modified_time,
                "file_size": file_size,
                "participants": [],  # 可以通過解析文件內容獲取
                "message_count": 0,  # 可以通過解析文件內容獲取
                "topics": [],
                "summary": ""
            }
            
        except Exception as e:
            self.logger.error(f"解析對話文件失敗: {e}")
            return None

class FileAPI:
    """檔案管理API"""
    
    def __init__(self, storage_manager: TaskStorageManager):
        self.storage_manager = storage_manager
        self.logger = logging.getLogger(__name__)
    
    async def get_task_files(self, task_id: str) -> Dict[str, Any]:
        """獲取任務的所有檔案"""
        try:
            task_path = f"{self.storage_manager.base_path}/{task_id}"
            
            # 列出所有檔案
            command = f"find {task_path} -type f 2>/dev/null"
            result = await self.storage_manager.execute_command(command)
            
            if not result["success"]:
                return {"success": False, "error": "無法讀取檔案目錄"}
            
            file_paths = result["output"].strip().split('\n')
            files = []
            
            for file_path in file_paths:
                if file_path:
                    file_info = await self._parse_file_info(task_id, file_path)
                    if file_info:
                        files.append(file_info)
            
            return {
                "success": True,
                "task_id": task_id,
                "files": files,
                "total_count": len(files),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"獲取檔案列表失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_file_content(self, task_id: str, file_path: str) -> Dict[str, Any]:
        """獲取檔案內容"""
        try:
            # 檢查檔案是否存在
            command = f"test -f '{file_path}' && echo 'exists' || echo 'not_exists'"
            result = await self.storage_manager.execute_command(command)
            
            if result["output"].strip() != "exists":
                return {"success": False, "error": "檔案不存在"}
            
            # 讀取檔案內容
            command = f"cat '{file_path}'"
            result = await self.storage_manager.execute_command(command)
            
            if not result["success"]:
                return {"success": False, "error": "無法讀取檔案內容"}
            
            # 嘗試解析JSON，如果失敗則返回原始內容
            try:
                content = json.loads(result["output"])
                content_type = "json"
            except:
                content = result["output"]
                content_type = "text"
            
            return {
                "success": True,
                "task_id": task_id,
                "file_path": file_path,
                "content_type": content_type,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"獲取檔案內容失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_files(self, task_id: str, keyword: str) -> Dict[str, Any]:
        """搜尋任務中的檔案"""
        try:
            task_path = f"{self.storage_manager.base_path}/{task_id}"
            
            # 搜尋檔案名包含關鍵詞的檔案
            command = f"find {task_path} -type f -name '*{keyword}*' 2>/dev/null"
            result = await self.storage_manager.execute_command(command)
            
            matched_files = []
            if result["success"] and result["output"].strip():
                file_paths = result["output"].strip().split('\n')
                for file_path in file_paths:
                    if file_path:
                        file_info = await self._parse_file_info(task_id, file_path)
                        if file_info:
                            matched_files.append(file_info)
            
            # 搜尋檔案內容包含關鍵詞的檔案
            command = f"grep -r -l '{keyword}' {task_path} 2>/dev/null"
            result = await self.storage_manager.execute_command(command)
            
            if result["success"] and result["output"].strip():
                content_matched_paths = result["output"].strip().split('\n')
                for file_path in content_matched_paths:
                    if file_path:
                        # 避免重複
                        if not any(f["file_path"] == file_path for f in matched_files):
                            file_info = await self._parse_file_info(task_id, file_path)
                            if file_info:
                                file_info["match_type"] = "content"
                                matched_files.append(file_info)
            
            return {
                "success": True,
                "task_id": task_id,
                "search_keyword": keyword,
                "files": matched_files,
                "total_count": len(matched_files),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"搜尋檔案失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def _parse_file_info(self, task_id: str, file_path: str) -> Optional[Dict]:
        """解析檔案信息"""
        try:
            # 獲取檔案統計信息
            command = f"stat '{file_path}' --format='%Y %Z %s'"
            result = await self.storage_manager.execute_command(command)
            
            if not result["success"]:
                return None
            
            stat_info = result["output"].strip().split()
            modified_time = datetime.fromtimestamp(int(stat_info[0])).isoformat()
            created_time = datetime.fromtimestamp(int(stat_info[1])).isoformat()
            file_size = int(stat_info[2])
            
            file_name = Path(file_path).name
            file_type = Path(file_path).suffix.lower()
            
            # 根據路徑確定檔案類別
            category = "unknown"
            if "conversations_analysis" in file_path:
                category = "conversation"
            elif "corrected_files" in file_path:
                category = "corrected"
            elif "reports" in file_path:
                category = "report"
            elif "metadata" in file_path:
                category = "metadata"
            
            return {
                "file_id": f"{task_id}_{Path(file_path).stem}",
                "task_id": task_id,
                "file_path": file_path,
                "file_name": file_name,
                "file_type": file_type,
                "file_size": file_size,
                "created_at": created_time,
                "modified_at": modified_time,
                "category": category
            }
            
        except Exception as e:
            self.logger.error(f"解析檔案信息失敗: {e}")
            return None

class EnhancedSmartinventionMCP:
    """增強版Smartinvention MCP"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化EC2配置
        ec2_config = {
            "host": "18.212.97.173",
            "username": "ec2-user",
            "key_file": "/home/ubuntu/alexchuang.pem"
        }
        
        # 初始化管理器和API
        self.storage_manager = TaskStorageManager(ec2_config)
        self.task_api = TaskListAPI(self.storage_manager)
        self.conversation_api = ConversationAPI(self.storage_manager)
        self.file_api = FileAPI(self.storage_manager)
        
        self.version = "3.0.0"
        self.name = "EnhancedSmartinventionMCP"
    
    async def initialize(self) -> Dict[str, Any]:
        """初始化MCP"""
        try:
            # 測試EC2連接
            connect_result = await self.storage_manager.connect_ec2()
            
            return {
                "success": True,
                "component": self.name,
                "version": self.version,
                "ec2_connected": connect_result["success"],
                "available_apis": [
                    "get_all_tasks",
                    "get_task_by_id", 
                    "search_tasks",
                    "get_task_conversations",
                    "get_conversation_content",
                    "search_conversations",
                    "get_task_files",
                    "get_file_content",
                    "search_files"
                ],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"初始化失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        try:
            # 測試EC2連接
            connect_result = await self.storage_manager.connect_ec2()
            
            return {
                "success": True,
                "healthy": connect_result["success"],
                "component": self.name,
                "version": self.version,
                "ec2_status": "connected" if connect_result["success"] else "disconnected",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # 任務API方法
    async def get_all_tasks(self) -> Dict[str, Any]:
        """獲取所有任務列表"""
        return await self.task_api.get_all_tasks()
    
    async def get_task_by_id(self, task_id: str) -> Dict[str, Any]:
        """根據ID獲取特定任務"""
        return await self.task_api.get_task_by_id(task_id)
    
    async def search_tasks(self, keyword: str) -> Dict[str, Any]:
        """搜尋任務"""
        return await self.task_api.search_tasks(keyword)
    
    # 對話API方法
    async def get_task_conversations(self, task_id: str) -> Dict[str, Any]:
        """獲取任務的所有對話"""
        return await self.conversation_api.get_task_conversations(task_id)
    
    async def get_conversation_content(self, task_id: str, conversation_id: str) -> Dict[str, Any]:
        """獲取特定對話的內容"""
        return await self.conversation_api.get_conversation_content(task_id, conversation_id)
    
    async def search_conversations(self, task_id: str, keyword: str) -> Dict[str, Any]:
        """搜尋任務中的對話"""
        return await self.conversation_api.search_conversations(task_id, keyword)
    
    # 檔案API方法
    async def get_task_files(self, task_id: str) -> Dict[str, Any]:
        """獲取任務的所有檔案"""
        return await self.file_api.get_task_files(task_id)
    
    async def get_file_content(self, task_id: str, file_path: str) -> Dict[str, Any]:
        """獲取檔案內容"""
        return await self.file_api.get_file_content(task_id, file_path)
    
    async def search_files(self, task_id: str, keyword: str) -> Dict[str, Any]:
        """搜尋任務中的檔案"""
        return await self.file_api.search_files(task_id, keyword)
    
    async def cleanup(self):
        """清理資源"""
        await self.storage_manager.disconnect_ec2()

# 使用示例
async def main():
    """使用示例"""
    # 初始化MCP
    mcp = EnhancedSmartinventionMCP()
    
    try:
        # 初始化
        init_result = await mcp.initialize()
        print("初始化結果:", json.dumps(init_result, indent=2, ensure_ascii=False))
        
        if init_result["success"]:
            # 獲取所有任務
            tasks_result = await mcp.get_all_tasks()
            print("\n任務列表:", json.dumps(tasks_result, indent=2, ensure_ascii=False))
            
            # 如果有任務，獲取第一個任務的詳細信息
            if tasks_result["success"] and tasks_result["tasks"]:
                first_task_id = tasks_result["tasks"][0]["task_id"]
                
                # 獲取任務對話
                conversations_result = await mcp.get_task_conversations(first_task_id)
                print(f"\n任務 {first_task_id} 的對話:", json.dumps(conversations_result, indent=2, ensure_ascii=False))
                
                # 獲取任務檔案
                files_result = await mcp.get_task_files(first_task_id)
                print(f"\n任務 {first_task_id} 的檔案:", json.dumps(files_result, indent=2, ensure_ascii=False))
        
    finally:
        # 清理資源
        await mcp.cleanup()

if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(level=logging.INFO)
    
    # 運行示例
    asyncio.run(main())

