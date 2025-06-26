"""
Manus Replay Chain Core Module
Manus 重放鏈結核心模組

Author: Manus AI
Version: 1.0.0
Date: 2025-06-24
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class TaskStatus(Enum):
    """任務狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ChainStatus(Enum):
    """鏈結狀態"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskNode:
    """任務節點"""
    task_id: str
    task_type: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    priority: int = 5
    status: TaskStatus = TaskStatus.PENDING
    created_time: float = field(default_factory=time.time)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class ReplayChain:
    """重放鏈結"""
    chain_id: str
    chain_name: str
    description: str
    nodes: List[TaskNode] = field(default_factory=list)
    status: ChainStatus = ChainStatus.CREATED
    created_time: float = field(default_factory=time.time)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReplayChainManager:
    """重放鏈結管理器"""
    
    def __init__(self):
        """初始化鏈結管理器"""
        self.logger = logging.getLogger(__name__)
        self.tasks: Dict[str, TaskNode] = {}
        self.chains: Dict[str, ReplayChain] = {}
        self.is_running = False
    
    async def add_task(self, task: TaskNode) -> bool:
        """
        添加任務
        
        Args:
            task: 任務節點
            
        Returns:
            是否成功添加
        """
        try:
            self.tasks[task.task_id] = task
            self.logger.info(f"任務已添加: {task.task_id}")
            return True
        except Exception as e:
            self.logger.error(f"添加任務失敗: {e}")
            return False
    
    async def create_chain(self, chain_name: str, task_ids: List[str], description: str = "") -> Optional[str]:
        """
        創建鏈結
        
        Args:
            chain_name: 鏈結名稱
            task_ids: 任務ID列表
            description: 鏈結描述
            
        Returns:
            鏈結ID或None
        """
        try:
            chain_id = str(uuid.uuid4())
            
            # 獲取任務節點
            nodes = []
            for task_id in task_ids:
                if task_id in self.tasks:
                    nodes.append(self.tasks[task_id])
                else:
                    self.logger.warning(f"任務不存在: {task_id}")
            
            if not nodes:
                self.logger.error("沒有有效的任務節點")
                return None
            
            # 創建鏈結
            chain = ReplayChain(
                chain_id=chain_id,
                chain_name=chain_name,
                description=description,
                nodes=nodes
            )
            
            self.chains[chain_id] = chain
            self.logger.info(f"鏈結已創建: {chain_id}")
            return chain_id
            
        except Exception as e:
            self.logger.error(f"創建鏈結失敗: {e}")
            return None
    
    async def auto_generate_chains(self) -> List[str]:
        """
        自動生成鏈結
        
        Returns:
            生成的鏈結ID列表
        """
        try:
            chain_ids = []
            
            # 簡單的自動生成邏輯：將所有任務放入一個鏈結
            if self.tasks:
                task_ids = list(self.tasks.keys())
                chain_id = await self.create_chain(
                    chain_name="Auto Generated Chain",
                    task_ids=task_ids,
                    description="自動生成的任務鏈結"
                )
                if chain_id:
                    chain_ids.append(chain_id)
            
            return chain_ids
            
        except Exception as e:
            self.logger.error(f"自動生成鏈結失敗: {e}")
            return []
    
    async def get_chain(self, chain_id: str) -> Optional[ReplayChain]:
        """
        獲取鏈結
        
        Args:
            chain_id: 鏈結ID
            
        Returns:
            鏈結對象或None
        """
        return self.chains.get(chain_id)
    
    async def execute_chain(self, chain_id: str) -> bool:
        """
        執行鏈結
        
        Args:
            chain_id: 鏈結ID
            
        Returns:
            是否成功執行
        """
        try:
            chain = self.chains.get(chain_id)
            if not chain:
                self.logger.error(f"鏈結不存在: {chain_id}")
                return False
            
            self.logger.info(f"開始執行鏈結: {chain_id}")
            chain.status = ChainStatus.RUNNING
            chain.start_time = time.time()
            
            # 模擬執行任務
            for task in chain.nodes:
                task.status = TaskStatus.RUNNING
                task.start_time = time.time()
                
                # 模擬任務執行時間
                await asyncio.sleep(0.1)
                
                task.status = TaskStatus.COMPLETED
                task.end_time = time.time()
                task.result = {"status": "success"}
            
            chain.status = ChainStatus.COMPLETED
            chain.end_time = time.time()
            
            self.logger.info(f"鏈結執行完成: {chain_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"執行鏈結失敗: {e}")
            if chain_id in self.chains:
                self.chains[chain_id].status = ChainStatus.FAILED
            return False
    
    async def cleanup(self):
        """清理資源"""
        try:
            self.logger.info("清理鏈結管理器...")
            self.is_running = False
            self.logger.info("✅ 鏈結管理器清理完成")
        except Exception as e:
            self.logger.error(f"清理鏈結管理器失敗: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """獲取狀態"""
        return {
            "is_running": self.is_running,
            "total_tasks": len(self.tasks),
            "total_chains": len(self.chains),
            "tasks": {task_id: task.status.value for task_id, task in self.tasks.items()},
            "chains": {chain_id: chain.status.value for chain_id, chain in self.chains.items()}
        }

