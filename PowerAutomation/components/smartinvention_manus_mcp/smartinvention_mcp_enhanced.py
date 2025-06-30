#!/usr/bin/env python3
"""
SmartInvention MCP Enhanced - Manus Mode
增强版SmartInvention MCP，专为Manus模式设计
实现文件checkin状态检查、Agent目录管理、SmartUI集成

Version: 3.0.0 - Manus Mode
Author: Manus AI
Date: 2025-01-01
"""

import asyncio
import json
import logging
import os
import aiohttp
import aiofiles
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import subprocess
import hashlib
import time

# 导入现有的SmartInvention组件
import sys
sys.path.append('/home/ubuntu/aicore0624/backup/PowerAutomation/components/smartinvention_mcp')

from main import SmartinventionAdapterMCP, ConversationStorage, ConversationProcessor
from manus_integration import ManusIntegration

@dataclass
class FileCheckinStatus:
    """文件checkin状态数据模型"""
    file_path: str
    file_name: str
    task_id: str
    checkin_status: str  # 'checked_in', 'pending', 'modified', 'unknown'
    last_modified: datetime
    file_hash: str
    checkin_user: Optional[str] = None
    checkin_time: Optional[datetime] = None
    pending_changes: List[str] = field(default_factory=list)

@dataclass
class AgentInfo:
    """Agent信息数据模型"""
    agent_id: str
    agent_name: str
    agent_type: str  # 'human', 'ai', 'system'
    task_id: str
    created_at: datetime
    last_active: datetime
    conversation_count: int = 0
    modification_count: int = 0

class FileCheckinManager:
    """文件checkin状态管理器"""
    
    def __init__(self, data_dir: str = "/tmp/smartinvention_checkin"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    async def check_file_checkin_status(self, files: List[Dict]) -> List[FileCheckinStatus]:
        """检查文件的checkin状态"""
        checkin_statuses = []
        
        for file_info in files:
            try:
                file_path = file_info.get("url", "")
                file_name = file_info.get("name", "unknown")
                task_id = file_info.get("task_id", "")
                
                # 计算文件哈希（模拟）
                file_hash = hashlib.md5(f"{file_path}{file_name}".encode()).hexdigest()
                
                # 检查checkin状态（基于文件名和路径模式）
                status = await self._determine_checkin_status(file_path, file_name)
                
                # 获取最后修改时间
                last_modified = datetime.fromtimestamp(file_info.get("downloaded_at", time.time()))
                
                # 检查待处理的更改
                pending_changes = await self._check_pending_changes(file_path, file_name)
                
                checkin_status = FileCheckinStatus(
                    file_path=file_path,
                    file_name=file_name,
                    task_id=task_id,
                    checkin_status=status,
                    last_modified=last_modified,
                    file_hash=file_hash,
                    pending_changes=pending_changes
                )
                
                checkin_statuses.append(checkin_status)
                
            except Exception as e:
                self.logger.error(f"检查文件checkin状态失败: {e}")
                continue
        
        # 保存checkin状态记录
        await self._save_checkin_records(checkin_statuses)
        
        return checkin_statuses
    
    async def _determine_checkin_status(self, file_path: str, file_name: str) -> str:
        """确定文件的checkin状态"""
        # 基于文件扩展名和路径模式判断状态
        if any(ext in file_name.lower() for ext in ['.tmp', '.bak', '.draft']):
            return 'pending'
        elif any(keyword in file_path.lower() for keyword in ['work-in-progress', 'draft', 'temp']):
            return 'pending'
        elif any(keyword in file_path.lower() for keyword in ['completed', 'final', 'release']):
            return 'checked_in'
        elif any(ext in file_name.lower() for ext in ['.py', '.js', '.html', '.css']):
            # 代码文件默认需要检查修改状态
            return 'modified'
        else:
            return 'unknown'
    
    async def _check_pending_changes(self, file_path: str, file_name: str) -> List[str]:
        """检查待处理的更改"""
        pending_changes = []
        
        # 模拟检查常见的待处理更改
        if '.py' in file_name:
            pending_changes.extend(['代码格式化', '类型注解', '文档字符串'])
        elif '.js' in file_name:
            pending_changes.extend(['ESLint检查', '代码压缩', '测试覆盖'])
        elif '.html' in file_name:
            pending_changes.extend(['HTML验证', '响应式检查', 'SEO优化'])
        
        return pending_changes
    
    async def _save_checkin_records(self, checkin_statuses: List[FileCheckinStatus]):
        """保存checkin状态记录"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"checkin_status_{timestamp}.json"
            filepath = self.data_dir / filename
            
            # 转换为可序列化的格式
            records = []
            for status in checkin_statuses:
                record = {
                    "file_path": status.file_path,
                    "file_name": status.file_name,
                    "task_id": status.task_id,
                    "checkin_status": status.checkin_status,
                    "last_modified": status.last_modified.isoformat(),
                    "file_hash": status.file_hash,
                    "checkin_user": status.checkin_user,
                    "checkin_time": status.checkin_time.isoformat() if status.checkin_time else None,
                    "pending_changes": status.pending_changes
                }
                records.append(record)
            
            data = {
                "records": records,
                "timestamp": datetime.now().isoformat(),
                "total_files": len(records),
                "status_summary": self._generate_status_summary(checkin_statuses)
            }
            
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            
            self.logger.info(f"已保存 {len(records)} 个文件的checkin状态到 {filename}")
            
        except Exception as e:
            self.logger.error(f"保存checkin记录失败: {e}")
    
    def _generate_status_summary(self, checkin_statuses: List[FileCheckinStatus]) -> Dict[str, int]:
        """生成状态汇总"""
        summary = {}
        for status in checkin_statuses:
            status_key = status.checkin_status
            summary[status_key] = summary.get(status_key, 0) + 1
        return summary
    
    async def get_checkin_summary(self, task_ids: List[str] = None) -> Dict[str, Any]:
        """获取checkin状态汇总"""
        try:
            # 读取最新的checkin记录
            checkin_files = list(self.data_dir.glob("checkin_status_*.json"))
            if not checkin_files:
                return {"error": "没有找到checkin记录"}
            
            # 获取最新的记录文件
            latest_file = max(checkin_files, key=lambda x: x.stat().st_mtime)
            
            async with aiofiles.open(latest_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
            
            records = data.get("records", [])
            
            # 如果指定了task_ids，则过滤记录
            if task_ids:
                records = [r for r in records if r.get("task_id") in task_ids]
            
            # 生成汇总信息
            summary = {
                "total_files": len(records),
                "status_distribution": {},
                "pending_changes_count": 0,
                "last_updated": data.get("timestamp"),
                "task_breakdown": {}
            }
            
            for record in records:
                status = record.get("checkin_status", "unknown")
                summary["status_distribution"][status] = summary["status_distribution"].get(status, 0) + 1
                
                if record.get("pending_changes"):
                    summary["pending_changes_count"] += len(record["pending_changes"])
                
                task_id = record.get("task_id", "unknown")
                if task_id not in summary["task_breakdown"]:
                    summary["task_breakdown"][task_id] = {"files": 0, "pending": 0, "checked_in": 0}
                
                summary["task_breakdown"][task_id]["files"] += 1
                if status == "pending":
                    summary["task_breakdown"][task_id]["pending"] += 1
                elif status == "checked_in":
                    summary["task_breakdown"][task_id]["checked_in"] += 1
            
            return summary
            
        except Exception as e:
            self.logger.error(f"获取checkin汇总失败: {e}")
            return {"error": str(e)}

class AgentDirectoryManager:
    """Agent目录管理器"""
    
    def __init__(self, base_dir: str = "/tmp/smartinvention_agents"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.agents_registry = {}
    
    async def create_agent_directory(self, task_id: str, agent_info: Dict) -> str:
        """为任务创建agent目录"""
        try:
            agent_id = agent_info.get("id", f"agent_{int(time.time())}")
            agent_name = agent_info.get("name", "unknown_agent")
            
            # 创建agent目录结构
            agent_dir = self.base_dir / f"task_{task_id}" / f"agent_{agent_id}"
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建子目录
            (agent_dir / "conversations").mkdir(exist_ok=True)
            (agent_dir / "modifications").mkdir(exist_ok=True)
            (agent_dir / "files").mkdir(exist_ok=True)
            (agent_dir / "logs").mkdir(exist_ok=True)
            
            # 保存agent配置
            agent_config = {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "agent_type": agent_info.get("type", "ai"),
                "task_id": task_id,
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "directory_structure": {
                    "conversations": "对话记录",
                    "modifications": "修改记录",
                    "files": "相关文件",
                    "logs": "操作日志"
                }
            }
            
            config_file = agent_dir / "agent_config.json"
            async with aiofiles.open(config_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(agent_config, ensure_ascii=False, indent=2))
            
            # 注册agent
            self.agents_registry[agent_id] = {
                "directory": str(agent_dir),
                "config": agent_config,
                "last_updated": datetime.now()
            }
            
            self.logger.info(f"已创建Agent目录: {agent_dir}")
            return str(agent_dir)
            
        except Exception as e:
            self.logger.error(f"创建Agent目录失败: {e}")
            raise
    
    async def save_agent_conversations(self, agent_dir: str, conversations: List[Dict]):
        """保存agent的对话记录"""
        try:
            conversations_dir = Path(agent_dir) / "conversations"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversations_{timestamp}.json"
            filepath = conversations_dir / filename
            
            data = {
                "conversations": conversations,
                "count": len(conversations),
                "timestamp": datetime.now().isoformat(),
                "agent_directory": agent_dir
            }
            
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            
            self.logger.info(f"已保存 {len(conversations)} 条对话记录到 {filename}")
            
        except Exception as e:
            self.logger.error(f"保存Agent对话记录失败: {e}")
    
    async def save_agent_modifications(self, agent_dir: str, modifications: List[Dict]):
        """保存agent的修改记录"""
        try:
            modifications_dir = Path(agent_dir) / "modifications"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"modifications_{timestamp}.json"
            filepath = modifications_dir / filename
            
            data = {
                "modifications": modifications,
                "count": len(modifications),
                "timestamp": datetime.now().isoformat(),
                "agent_directory": agent_dir
            }
            
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            
            self.logger.info(f"已保存 {len(modifications)} 条修改记录到 {filename}")
            
        except Exception as e:
            self.logger.error(f"保存Agent修改记录失败: {e}")
    
    async def track_task_modifications(self, task_id: str, manus_integration: ManusIntegration) -> List[Dict]:
        """追踪任务的修改记录"""
        try:
            modifications = []
            
            # 模拟从Manus获取修改记录
            # 在实际实现中，这里会通过manus_integration获取真实数据
            sample_modifications = [
                {
                    "timestamp": datetime.now().isoformat(),
                    "user": "AI Agent",
                    "action": "文件创建",
                    "details": f"创建了任务 {task_id} 的相关文件",
                    "file_path": f"/task_{task_id}/main.py",
                    "change_type": "create"
                },
                {
                    "timestamp": (datetime.now()).isoformat(),
                    "user": "Human User",
                    "action": "代码修改",
                    "details": f"修改了任务 {task_id} 的核心逻辑",
                    "file_path": f"/task_{task_id}/main.py",
                    "change_type": "modify"
                }
            ]
            
            modifications.extend(sample_modifications)
            
            self.logger.info(f"追踪到任务 {task_id} 的 {len(modifications)} 条修改记录")
            return modifications
            
        except Exception as e:
            self.logger.error(f"追踪任务修改记录失败: {e}")
            return []
    
    async def get_agent_summary(self, task_id: str = None) -> Dict[str, Any]:
        """获取agent汇总信息"""
        try:
            summary = {
                "total_agents": len(self.agents_registry),
                "agents": [],
                "task_distribution": {},
                "last_updated": datetime.now().isoformat()
            }
            
            for agent_id, agent_data in self.agents_registry.items():
                config = agent_data["config"]
                agent_task_id = config.get("task_id")
                
                # 如果指定了task_id，则过滤
                if task_id and agent_task_id != task_id:
                    continue
                
                agent_summary = {
                    "agent_id": agent_id,
                    "agent_name": config.get("agent_name"),
                    "agent_type": config.get("agent_type"),
                    "task_id": agent_task_id,
                    "directory": agent_data["directory"],
                    "created_at": config.get("created_at"),
                    "last_active": config.get("last_active")
                }
                
                summary["agents"].append(agent_summary)
                
                # 统计任务分布
                if agent_task_id not in summary["task_distribution"]:
                    summary["task_distribution"][agent_task_id] = 0
                summary["task_distribution"][agent_task_id] += 1
            
            return summary
            
        except Exception as e:
            self.logger.error(f"获取Agent汇总失败: {e}")
            return {"error": str(e)}

class SmartinventionManusModeMCP(SmartinventionAdapterMCP):
    """SmartInvention Manus模式MCP - 增强版"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name = "SmartinventionManusModeMCP"
        self.version = "3.0.0"
        
        # 初始化新的管理器
        self.checkin_manager = FileCheckinManager()
        self.agent_manager = AgentDirectoryManager()
        
    async def initialize(self) -> Dict[str, Any]:
        """初始化增强版MCP"""
        try:
            # 调用父类初始化
            result = await super().initialize()
            
            # 添加Manus模式特性
            result["manus_mode"] = "enabled"
            result["features"] = [
                "file_checkin_tracking",
                "agent_directory_management", 
                "modification_tracking",
                "smartui_integration"
            ]
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "component": self.name,
                "version": self.version
            }
    
    async def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理增强版请求"""
        try:
            # 处理新的Manus模式方法
            if method == "get_latest_tasks_with_checkin":
                return await self.get_latest_tasks_with_checkin(params)
            
            elif method == "save_tasks_complete_history":
                return await self.save_tasks_complete_history(params)
            
            elif method == "get_checkin_summary":
                task_ids = params.get("task_ids", [])
                summary = await self.checkin_manager.get_checkin_summary(task_ids)
                return {"success": True, "summary": summary}
            
            elif method == "get_agent_summary":
                task_id = params.get("task_id")
                summary = await self.agent_manager.get_agent_summary(task_id)
                return {"success": True, "summary": summary}
            
            else:
                # 调用父类方法处理其他请求
                return await super().handle_request(method, params)
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_latest_tasks_with_checkin(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取最新5个任务及其文件checkin状态"""
        try:
            limit = params.get("limit", 5)
            
            # 获取任务列表
            tasks_result = await super().handle_request("get_tasks", {})
            all_tasks = tasks_result.get("tasks", [])
            
            # 获取最新的任务
            latest_tasks = sorted(all_tasks, 
                                key=lambda x: x.get("extracted_at", 0), 
                                reverse=True)[:limit]
            
            # 为每个任务获取文件和checkin状态
            for task in latest_tasks:
                task_id = task.get("title", "")
                
                # 获取任务文件
                files_result = await super().handle_request("download_files", {"task_id": task_id})
                files = files_result.get("files", [])
                
                # 检查checkin状态
                checkin_statuses = await self.checkin_manager.check_file_checkin_status(files)
                
                # 转换为字典格式
                files_with_status = []
                for status in checkin_statuses:
                    file_dict = {
                        "file_path": status.file_path,
                        "file_name": status.file_name,
                        "checkin_status": status.checkin_status,
                        "last_modified": status.last_modified.isoformat(),
                        "file_hash": status.file_hash,
                        "pending_changes": status.pending_changes
                    }
                    files_with_status.append(file_dict)
                
                task["files"] = files_with_status
                
                # 生成checkin汇总
                task["checkin_summary"] = {
                    "total_files": len(files_with_status),
                    "checked_in": len([f for f in files_with_status if f["checkin_status"] == "checked_in"]),
                    "pending": len([f for f in files_with_status if f["checkin_status"] == "pending"]),
                    "modified": len([f for f in files_with_status if f["checkin_status"] == "modified"]),
                    "unknown": len([f for f in files_with_status if f["checkin_status"] == "unknown"])
                }
            
            return {
                "success": True,
                "tasks": latest_tasks,
                "count": len(latest_tasks),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取任务checkin状态失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def save_tasks_complete_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """保存五个任务的完整历史记录"""
        try:
            # 获取最新任务
            tasks_result = await self.get_latest_tasks_with_checkin(params)
            if not tasks_result.get("success"):
                return tasks_result
            
            latest_tasks = tasks_result.get("tasks", [])
            
            saved_tasks = []
            
            for task in latest_tasks:
                task_id = task.get("title", "")
                
                # 获取任务相关的对话
                conversations_result = await super().handle_request("get_conversations", {"limit": 100})
                all_conversations = conversations_result.get("conversations", [])
                
                # 过滤任务相关的对话（简单的关键词匹配）
                task_conversations = [conv for conv in all_conversations 
                                    if task_id.lower() in conv.get("text", "").lower()]
                
                # 获取任务的修改记录
                modifications = await self.agent_manager.track_task_modifications(task_id, self.conversation_processor.manus_integration)
                
                # 识别参与的agents（从对话中提取）
                agents = self.extract_agents_from_conversations(task_conversations)
                
                # 为每个agent创建目录并保存数据
                agent_directories = []
                for agent in agents:
                    agent_dir = await self.agent_manager.create_agent_directory(task_id, agent)
                    agent_directories.append(agent_dir)
                    
                    # 过滤该agent的对话
                    agent_conversations = [conv for conv in task_conversations 
                                         if agent.get("name", "").lower() in conv.get("text", "").lower()]
                    
                    # 过滤该agent的修改记录
                    agent_modifications = [mod for mod in modifications 
                                         if mod.get("user") == agent.get("name")]
                    
                    # 保存数据
                    await self.agent_manager.save_agent_conversations(agent_dir, agent_conversations)
                    await self.agent_manager.save_agent_modifications(agent_dir, agent_modifications)
                
                # 保存任务级别的汇总信息
                task_summary = {
                    "task_id": task_id,
                    "task_info": task,
                    "total_conversations": len(task_conversations),
                    "total_modifications": len(modifications),
                    "agents_count": len(agents),
                    "agent_directories": agent_directories,
                    "saved_at": datetime.now().isoformat()
                }
                
                saved_tasks.append(task_summary)
            
            return {
                "success": True,
                "saved_tasks": saved_tasks,
                "count": len(saved_tasks),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"保存任务完整历史失败: {e}")
            return {"success": False, "error": str(e)}
    
    def extract_agents_from_conversations(self, conversations: List[Dict]) -> List[Dict]:
        """从对话中提取agents信息"""
        agents = []
        agent_names = set()
        
        for conv in conversations:
            text = conv.get("text", "")
            
            # 简单的agent识别逻辑
            if "AI" in text or "助手" in text or "agent" in text.lower():
                if "AI Agent" not in agent_names:
                    agents.append({
                        "id": "ai_agent_1",
                        "name": "AI Agent",
                        "type": "ai"
                    })
                    agent_names.add("AI Agent")
            
            if "用户" in text or "user" in text.lower() or "人工" in text:
                if "Human User" not in agent_names:
                    agents.append({
                        "id": "human_user_1", 
                        "name": "Human User",
                        "type": "human"
                    })
                    agent_names.add("Human User")
        
        # 如果没有识别到agents，添加默认的
        if not agents:
            agents.append({
                "id": "default_agent",
                "name": "Default Agent", 
                "type": "system"
            })
        
        return agents

# 导出主要类
__all__ = ["SmartinventionManusModeMCP", "FileCheckinManager", "AgentDirectoryManager"]

