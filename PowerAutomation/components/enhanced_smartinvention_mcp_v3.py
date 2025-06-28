"""
Enhanced Smartinvention MCP v3 - 整合 Claude Code SDK
提供完整的任務管理API功能，並整合 Claude Code SDK 的智能需求分析能力
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

# 導入 Claude Code 適配器
from claude_code_adapter_mcp import (
    claude_code_adapter, 
    ClaudeCodeTaskType, 
    ClaudeCodeRole,
    RequirementAnalysisResult
)

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TaskInfo:
    """任務信息模型（擴展版）"""
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
    # Claude Code 擴展字段
    claude_analysis: Optional[Dict[str, Any]] = None
    requirement_quality_score: float = 0.0
    ai_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    last_analysis_timestamp: Optional[str] = None

@dataclass
class ConversationInfo:
    """對話信息模型（擴展版）"""
    conversation_id: str
    task_id: str
    file_path: str
    timestamp: str
    participants: List[str] = field(default_factory=list)
    message_count: int = 0
    topics: List[str] = field(default_factory=list)
    summary: str = ""
    # Claude Code 擴展字段
    ai_analysis: Optional[Dict[str, Any]] = None
    extracted_requirements: List[str] = field(default_factory=list)
    sentiment_analysis: Optional[Dict[str, Any]] = None

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

class EnhancedTaskStorageManager:
    """增強版任務存儲管理器"""
    
    def __init__(self, ec2_config: Dict):
        self.ec2_config = ec2_config
        self.ssh_client = None
        self.logger = logging.getLogger(__name__)
        self.base_path = "/home/ec2-user/smartinvention_mcp/tasks"
        self.claude_adapter = claude_code_adapter
        
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
    
    async def save_claude_analysis(self, task_id: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """保存 Claude Code 分析結果"""
        try:
            analysis_path = f"{self.base_path}/{task_id}/claude_analysis"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"claude_analysis_{timestamp}.json"
            
            # 創建目錄
            mkdir_command = f"mkdir -p {analysis_path}"
            await self.execute_command(mkdir_command)
            
            # 保存分析結果
            analysis_file = f"{analysis_path}/{filename}"
            save_command = f"echo '{json.dumps(analysis_data, ensure_ascii=False)}' > {analysis_file}"
            result = await self.execute_command(save_command)
            
            if result["success"]:
                return {
                    "success": True,
                    "file_path": analysis_file,
                    "timestamp": timestamp
                }
            else:
                return {"success": False, "error": result["error"]}
                
        except Exception as e:
            self.logger.error(f"保存 Claude 分析失敗: {e}")
            return {"success": False, "error": str(e)}

class EnhancedTaskListAPI:
    """增強版任務列表API"""
    
    def __init__(self, storage_manager: EnhancedTaskStorageManager):
        self.storage_manager = storage_manager
        self.logger = logging.getLogger(__name__)
        self.claude_adapter = claude_code_adapter
    
    async def get_all_tasks(self, include_ai_analysis: bool = True) -> Dict[str, Any]:
        """獲取所有任務列表（包含AI分析）"""
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
                
                # 創建任務對象
                task = TaskInfo(
                    task_id=task_id,
                    task_name=task_info.get("cluster_name", ""),
                    cluster_name=task_info.get("cluster_name", ""),
                    description=task_info.get("description", ""),
                    status=task_info.get("status", "active"),
                    created_at=task_info.get("created_at", ""),
                    storage_path=storage_path,
                    conversations_count=conversations_count,
                    files_count=files_count,
                    metadata=task_info.get("metadata", {})
                )
                
                # 如果需要AI分析，則進行Claude Code分析
                if include_ai_analysis:
                    ai_analysis = await self._get_or_create_ai_analysis(task)
                    task.claude_analysis = ai_analysis.get("analysis")
                    task.requirement_quality_score = ai_analysis.get("quality_score", 0.0)
                    task.ai_suggestions = ai_analysis.get("suggestions", [])
                    task.last_analysis_timestamp = ai_analysis.get("timestamp")
                
                tasks.append(task)
            
            return {
                "success": True,
                "tasks": [task.__dict__ for task in tasks],
                "total_count": len(tasks),
                "timestamp": datetime.now().isoformat(),
                "ai_analysis_enabled": include_ai_analysis
            }
            
        except Exception as e:
            self.logger.error(f"獲取任務列表失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_or_create_ai_analysis(self, task: TaskInfo) -> Dict[str, Any]:
        """獲取或創建AI分析"""
        try:
            # 檢查是否已有分析結果
            analysis_path = f"{task.storage_path}/claude_analysis"
            check_command = f"ls -la {analysis_path}/claude_analysis_*.json 2>/dev/null | tail -1"
            result = await self.storage_manager.execute_command(check_command)
            
            # 如果有現有分析且不超過24小時，則使用現有結果
            if result["success"] and result["output"].strip():
                try:
                    latest_file = result["output"].strip().split()[-1]
                    read_command = f"cat {latest_file}"
                    read_result = await self.storage_manager.execute_command(read_command)
                    
                    if read_result["success"]:
                        existing_analysis = json.loads(read_result["output"])
                        analysis_time = datetime.fromisoformat(existing_analysis.get("timestamp", ""))
                        time_diff = datetime.now() - analysis_time
                        
                        # 如果分析結果不超過24小時，直接返回
                        if time_diff.total_seconds() < 86400:  # 24小時
                            return existing_analysis
                except Exception as e:
                    self.logger.warning(f"讀取現有分析失敗: {e}")
            
            # 創建新的AI分析
            return await self._create_new_ai_analysis(task)
            
        except Exception as e:
            self.logger.error(f"獲取AI分析失敗: {e}")
            return {
                "analysis": None,
                "quality_score": 0.0,
                "suggestions": [],
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def _create_new_ai_analysis(self, task: TaskInfo) -> Dict[str, Any]:
        """創建新的AI分析"""
        try:
            # 構建分析內容
            analysis_content = f"""
            任務名稱: {task.task_name}
            任務描述: {task.description}
            聚類名稱: {task.cluster_name}
            對話數量: {task.conversations_count}
            檔案數量: {task.files_count}
            """
            
            # 調用 Claude Code 進行需求分析
            analysis_result = await self.claude_adapter.analyze_requirements(
                content=analysis_content,
                user_role="manager",  # 默認使用管理者角色進行任務級分析
                project_context={
                    "task_id": task.task_id,
                    "storage_path": task.storage_path,
                    "metadata": task.metadata
                }
            )
            
            if analysis_result["success"]:
                # 獲取質量建議
                suggestions_result = await self.claude_adapter.get_requirement_suggestions(
                    requirement_text=analysis_content,
                    focus_area="all"
                )
                
                # 驗證需求質量
                quality_result = await self.claude_adapter.validate_requirement_quality(
                    requirement_text=analysis_content
                )
                
                ai_analysis = {
                    "analysis": analysis_result.get("analysis_result"),
                    "quality_score": quality_result.get("overall_score", 0.0),
                    "suggestions": suggestions_result.get("suggestions", []),
                    "timestamp": datetime.now().isoformat(),
                    "processing_time": analysis_result.get("processing_time", 0),
                    "confidence_score": analysis_result.get("confidence_score", 0)
                }
                
                # 保存分析結果
                await self.storage_manager.save_claude_analysis(task.task_id, ai_analysis)
                
                return ai_analysis
            else:
                return {
                    "analysis": None,
                    "quality_score": 0.0,
                    "suggestions": [],
                    "timestamp": datetime.now().isoformat(),
                    "error": analysis_result.get("error", "分析失敗")
                }
                
        except Exception as e:
            self.logger.error(f"創建AI分析失敗: {e}")
            return {
                "analysis": None,
                "quality_score": 0.0,
                "suggestions": [],
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def _count_conversations(self, task_id: str) -> int:
        """統計對話數量"""
        try:
            conversations_path = f"{self.storage_manager.base_path}/{task_id}/conversations_analysis/raw_conversations"
            command = f"find {conversations_path} -name '*.json' 2>/dev/null | wc -l"
            result = await self.storage_manager.execute_command(command)
            
            if result["success"]:
                return int(result["output"].strip())
            return 0
            
        except Exception:
            return 0
    
    async def _count_files(self, task_id: str) -> int:
        """統計檔案數量"""
        try:
            files_path = f"{self.storage_manager.base_path}/{task_id}/files"
            command = f"find {files_path} -type f 2>/dev/null | wc -l"
            result = await self.storage_manager.execute_command(command)
            
            if result["success"]:
                return int(result["output"].strip())
            return 0
            
        except Exception:
            return 0

class EnhancedConversationAPI:
    """增強版對話API"""
    
    def __init__(self, storage_manager: EnhancedTaskStorageManager):
        self.storage_manager = storage_manager
        self.logger = logging.getLogger(__name__)
        self.claude_adapter = claude_code_adapter
    
    async def get_task_conversations(self, task_id: str, include_ai_analysis: bool = True) -> Dict[str, Any]:
        """獲取任務的所有對話（包含AI分析）"""
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
                    conversation_info = await self._parse_conversation_file(task_id, file_path, include_ai_analysis)
                    if conversation_info:
                        conversations.append(conversation_info)
            
            return {
                "success": True,
                "task_id": task_id,
                "conversations": conversations,
                "total_count": len(conversations),
                "timestamp": datetime.now().isoformat(),
                "ai_analysis_enabled": include_ai_analysis
            }
            
        except Exception as e:
            self.logger.error(f"獲取對話失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def _parse_conversation_file(self, task_id: str, file_path: str, include_ai_analysis: bool = True) -> Optional[ConversationInfo]:
        """解析對話文件（包含AI分析）"""
        try:
            # 讀取對話文件
            read_command = f"cat {file_path}"
            result = await self.storage_manager.execute_command(read_command)
            
            if not result["success"]:
                return None
            
            conversation_data = json.loads(result["output"])
            
            # 提取基本信息
            conversation_id = Path(file_path).stem
            timestamp = conversation_data.get("timestamp", "")
            participants = conversation_data.get("participants", [])
            messages = conversation_data.get("messages", [])
            
            # 創建對話信息對象
            conversation_info = ConversationInfo(
                conversation_id=conversation_id,
                task_id=task_id,
                file_path=file_path,
                timestamp=timestamp,
                participants=participants,
                message_count=len(messages),
                topics=conversation_data.get("topics", []),
                summary=conversation_data.get("summary", "")
            )
            
            # 如果需要AI分析
            if include_ai_analysis:
                ai_analysis = await self._analyze_conversation_with_claude(conversation_data)
                conversation_info.ai_analysis = ai_analysis.get("analysis")
                conversation_info.extracted_requirements = ai_analysis.get("requirements", [])
                conversation_info.sentiment_analysis = ai_analysis.get("sentiment")
            
            return conversation_info
            
        except Exception as e:
            self.logger.error(f"解析對話文件失敗: {e}")
            return None
    
    async def _analyze_conversation_with_claude(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用 Claude Code 分析對話"""
        try:
            # 提取對話內容
            messages = conversation_data.get("messages", [])
            conversation_text = "\n".join([
                f"{msg.get('sender', 'Unknown')}: {msg.get('content', '')}"
                for msg in messages
            ])
            
            # 進行需求分析
            analysis_result = await self.claude_adapter.analyze_requirements(
                content=conversation_text,
                user_role="developer",  # 對話分析使用開發者角色
                project_context={
                    "conversation_id": conversation_data.get("id", ""),
                    "participants": conversation_data.get("participants", []),
                    "timestamp": conversation_data.get("timestamp", "")
                }
            )
            
            if analysis_result["success"]:
                analysis_data = analysis_result.get("analysis_result", {})
                
                return {
                    "analysis": analysis_data.get("analysis"),
                    "requirements": analysis_data.get("analysis", {}).get("functional_requirements", []),
                    "sentiment": {
                        "overall_tone": "neutral",  # 可以擴展為真實的情感分析
                        "key_concerns": [],
                        "satisfaction_level": 0.7
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "analysis": None,
                    "requirements": [],
                    "sentiment": None,
                    "error": analysis_result.get("error", "分析失敗")
                }
                
        except Exception as e:
            self.logger.error(f"Claude 對話分析失敗: {e}")
            return {
                "analysis": None,
                "requirements": [],
                "sentiment": None,
                "error": str(e)
            }

class EnhancedSmartInventionMCPv3:
    """增強版 SmartInvention MCP v3 - 整合 Claude Code SDK"""
    
    def __init__(self, ec2_config: Dict = None):
        self.name = "enhanced_smartinvention_mcp_v3"
        self.version = "3.0.0"
        self.description = "整合 Claude Code SDK 的增強版智能發明MCP"
        
        # 默認EC2配置
        self.ec2_config = ec2_config or {
            "host": "18.212.97.173",
            "username": "ec2-user",
            "key_file": "/home/ubuntu/alexchuang.pem"
        }
        
        # 初始化組件
        self.storage_manager = EnhancedTaskStorageManager(self.ec2_config)
        self.task_api = EnhancedTaskListAPI(self.storage_manager)
        self.conversation_api = EnhancedConversationAPI(self.storage_manager)
        self.claude_adapter = claude_code_adapter
        
        # 註冊工具
        self.tools = self._register_tools()
        
        self.logger = logging.getLogger(__name__)
    
    def _register_tools(self) -> Dict[str, Dict[str, Any]]:
        """註冊MCP工具"""
        return {
            "get_all_tasks": {
                "description": "獲取所有任務列表（包含AI分析）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "include_ai_analysis": {
                            "type": "boolean",
                            "description": "是否包含AI分析結果",
                            "default": True
                        }
                    }
                }
            },
            "get_task_conversations": {
                "description": "獲取任務的所有對話（包含AI分析）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "任務ID"
                        },
                        "include_ai_analysis": {
                            "type": "boolean",
                            "description": "是否包含AI分析結果",
                            "default": True
                        }
                    },
                    "required": ["task_id"]
                }
            },
            "analyze_task_requirements": {
                "description": "使用 Claude Code 分析任務需求",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "任務ID"
                        },
                        "user_role": {
                            "type": "string",
                            "enum": ["user", "developer", "manager"],
                            "description": "分析角色",
                            "default": "manager"
                        },
                        "force_refresh": {
                            "type": "boolean",
                            "description": "是否強制重新分析",
                            "default": False
                        }
                    },
                    "required": ["task_id"]
                }
            },
            "get_requirement_suggestions": {
                "description": "獲取需求改進建議",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "任務ID"
                        },
                        "focus_area": {
                            "type": "string",
                            "enum": ["completeness", "clarity", "feasibility", "all"],
                            "description": "關注領域",
                            "default": "all"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        }
    
    async def initialize(self) -> Dict[str, Any]:
        """初始化MCP"""
        try:
            # 初始化 Claude Code 適配器
            claude_init = await self.claude_adapter.initialize()
            if not claude_init:
                self.logger.warning("Claude Code 適配器初始化失敗，將使用降級模式")
            
            # 測試EC2連接
            connection_result = await self.storage_manager.connect_ec2()
            if connection_result["success"]:
                await self.storage_manager.disconnect_ec2()
            
            self.logger.info("Enhanced SmartInvention MCP v3 初始化成功")
            return {
                "success": True,
                "name": self.name,
                "version": self.version,
                "claude_code_enabled": claude_init,
                "ec2_connection": connection_result["success"]
            }
            
        except Exception as e:
            self.logger.error(f"MCP初始化失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_all_tasks(self, include_ai_analysis: bool = True) -> Dict[str, Any]:
        """獲取所有任務列表"""
        return await self.task_api.get_all_tasks(include_ai_analysis)
    
    async def get_task_conversations(self, task_id: str, include_ai_analysis: bool = True) -> Dict[str, Any]:
        """獲取任務對話"""
        return await self.conversation_api.get_task_conversations(task_id, include_ai_analysis)
    
    async def analyze_task_requirements(self, task_id: str, user_role: str = "manager", 
                                      force_refresh: bool = False) -> Dict[str, Any]:
        """分析任務需求"""
        try:
            # 獲取任務信息
            tasks_result = await self.task_api.get_all_tasks(include_ai_analysis=False)
            if not tasks_result["success"]:
                return tasks_result
            
            # 找到目標任務
            target_task = None
            for task in tasks_result["tasks"]:
                if task["task_id"] == task_id:
                    target_task = TaskInfo(**task)
                    break
            
            if not target_task:
                return {"success": False, "error": f"任務 {task_id} 不存在"}
            
            # 如果強制刷新或沒有現有分析，則創建新分析
            if force_refresh or not target_task.claude_analysis:
                analysis_result = await self.task_api._create_new_ai_analysis(target_task)
                return {
                    "success": True,
                    "task_id": task_id,
                    "analysis": analysis_result,
                    "refreshed": True
                }
            else:
                return {
                    "success": True,
                    "task_id": task_id,
                    "analysis": {
                        "analysis": target_task.claude_analysis,
                        "quality_score": target_task.requirement_quality_score,
                        "suggestions": target_task.ai_suggestions,
                        "timestamp": target_task.last_analysis_timestamp
                    },
                    "refreshed": False
                }
                
        except Exception as e:
            self.logger.error(f"任務需求分析失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_requirement_suggestions(self, task_id: str, focus_area: str = "all") -> Dict[str, Any]:
        """獲取需求建議"""
        try:
            # 獲取任務信息
            tasks_result = await self.task_api.get_all_tasks(include_ai_analysis=True)
            if not tasks_result["success"]:
                return tasks_result
            
            # 找到目標任務
            target_task = None
            for task in tasks_result["tasks"]:
                if task["task_id"] == task_id:
                    target_task = task
                    break
            
            if not target_task:
                return {"success": False, "error": f"任務 {task_id} 不存在"}
            
            # 構建需求文本
            requirement_text = f"""
            任務名稱: {target_task['task_name']}
            任務描述: {target_task['description']}
            """
            
            # 獲取建議
            suggestions_result = await self.claude_adapter.get_requirement_suggestions(
                requirement_text=requirement_text,
                focus_area=focus_area
            )
            
            return {
                "success": True,
                "task_id": task_id,
                "suggestions": suggestions_result,
                "focus_area": focus_area
            }
            
        except Exception as e:
            self.logger.error(f"獲取需求建議失敗: {e}")
            return {"success": False, "error": str(e)}
    
    def get_tool_info(self) -> Dict[str, Any]:
        """獲取工具信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "tools": self.tools,
            "claude_code_enabled": bool(self.claude_adapter),
            "capabilities": [
                "任務管理",
                "對話分析", 
                "檔案管理",
                "AI需求分析",
                "智能建議生成",
                "質量評估"
            ]
        }

# 全局實例
enhanced_smartinvention_mcp_v3 = EnhancedSmartInventionMCPv3()

async def main():
    """測試主函數"""
    # 初始化MCP
    init_result = await enhanced_smartinvention_mcp_v3.initialize()
    print("初始化結果:")
    print(json.dumps(init_result, indent=2, ensure_ascii=False))
    
    # 測試獲取任務列表
    tasks_result = await enhanced_smartinvention_mcp_v3.get_all_tasks(include_ai_analysis=True)
    print("\n任務列表結果:")
    print(json.dumps(tasks_result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())

