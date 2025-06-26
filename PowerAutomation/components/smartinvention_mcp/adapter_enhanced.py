"""
Enhanced Smartinvention_Adapter MCP組件
整合Manus任務收集和data storage功能，完全雲側處理
Version: 3.0.0 - 包含Manus TaskID管理和雲端存儲
"""

import asyncio
import json
import logging
import os
import aiohttp
import aiofiles
import hashlib
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import subprocess

# MCP基礎類 - 直接實現
class MCPComponent:
    """MCP組件基礎類"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.version = "3.0.0"
        self.name = self.__class__.__name__
        self.initialized = False
    
    async def initialize(self) -> Dict[str, Any]:
        """初始化組件"""
        self.initialized = True
        return {
            "success": True,
            "component": self.name,
            "version": self.version
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        return {
            "success": True,
            "healthy": self.initialized,
            "component": self.name,
            "version": self.version
        }

@dataclass
class ManusTaskData:
    """Manus任務數據模型"""
    task_id: str
    name: str
    date: str
    replay_link: str
    category: str
    files: List[str]
    description: str
    cluster_name: str = ""
    importance_level: int = 1
    created_at: str = ""

@dataclass
class TaskClusterInfo:
    """任務聚類信息"""
    cluster_id: str
    cluster_name: str
    task_count: int
    importance_level: int
    description: str
    tasks: List[ManusTaskData]

class ManusTaskCollector:
    """Manus任務收集器 - 雲端版本"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = config.get('manus_base_url', 'https://manus.im')
        self.session = None
        
        # 聚類關鍵詞配置
        self.cluster_keywords = {
            "OCR_Commercial": [
                "ocr", "optical character recognition", "文字識別", "字符識別",
                "pdf轉markdown", "文檔識別", "表格識別", "商業化", "commercial"
            ],
            "MCP_Architecture": [
                "mcp", "model context protocol", "架構", "architecture", 
                "系統設計", "端雲協同", "智慧路由", "memory system"
            ],
            "AI_Model_Comparison": [
                "gemini", "claude", "ai比較", "模型比較", "性能對比",
                "ai output", "模型評估", "benchmark"
            ],
            "VSCode_Extension": [
                "vscode", "extension", "插件", "擴展", "vsix",
                "powerautomation", "開發工具"
            ],
            "UI_UX_Design": [
                "ui", "ux", "界面", "用戶體驗", "導航", "設計",
                "前端", "界面優化", "用戶界面"
            ],
            "Enterprise_Solutions": [
                "企業", "enterprise", "商業", "business", "解決方案",
                "產品流程", "業務流程", "企業級"
            ]
        }
        
        # 重要性權重
        self.importance_weights = {
            "OCR_Commercial": 5,
            "MCP_Architecture": 4,
            "Enterprise_Solutions": 4,
            "AI_Model_Comparison": 3,
            "VSCode_Extension": 2,
            "UI_UX_Design": 1
        }
    
    async def initialize_session(self):
        """初始化HTTP會話"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """關閉HTTP會話"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def collect_manus_tasks(self, app_url: str) -> Dict[str, Any]:
        """
        收集Manus任務 - 雲端版本
        """
        try:
            await self.initialize_session()
            
            # 模擬任務收集 (實際實現需要瀏覽器自動化)
            tasks = await self._simulate_task_collection()
            
            # 執行聚類分析
            clusters = await self._perform_clustering_analysis(tasks)
            
            # 分配TaskID
            task_groups = await self._assign_task_ids(clusters)
            
            return {
                "success": True,
                "total_tasks": len(tasks),
                "clusters_count": len(clusters),
                "task_groups": task_groups,
                "collection_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Manus任務收集失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "collection_time": datetime.now().isoformat()
            }
    
    async def _simulate_task_collection(self) -> List[ManusTaskData]:
        """模擬任務收集 (實際實現需要瀏覽器自動化)"""
        # 基於之前收集的數據創建任務列表
        tasks = [
            ManusTaskData(
                task_id="task_001",
                name="如何將智慧下載移至導航欄并移除原功能",
                date="Sun",
                replay_link="https://manus.im/share/GrrtiY4cAAEVpH3RxpJDDb?replay=1",
                category="UI/UX設計",
                files=[],
                description="UI/UX功能調整，導航欄優化"
            ),
            ManusTaskData(
                task_id="task_002", 
                name="Comparing Gemini AI Output with Personal Ability",
                date="Sun",
                replay_link="https://manus.im/share/ogbxIEerutqP7e4NgIB7oQ?replay=1",
                category="AI模型比較",
                files=[],
                description="AI模型性能對比分析，Gemini vs 個人能力評估"
            ),
            ManusTaskData(
                task_id="task_003",
                name="Developer Flow MCP",
                date="Fri", 
                replay_link="https://manus.im/share/uuX3KzwzsthCSgqmbQbgOz?replay=1",
                category="系統開發",
                files=[],
                description="保險核保OCR分析，臺銀人壽業務SOP，核保流程人力需求評估"
            ),
            ManusTaskData(
                task_id="task_004",
                name="No1 OCR Agent",
                date="6/15",
                replay_link="https://manus.im/share/ACCK5jiliUduoV8omBZ6dR?replay=1",
                category="OCR技術",
                files=[
                    "pdf2markdown_evaluation.json",
                    "test_pdf2markdown.py", 
                    "zhang_jiaquan_5d_evaluation.json",
                    "zhang_jiaquan_5d_evaluation.py",
                    "test_mmbench.py",
                    "README",
                    "zhang_jiaquan_chinese_ocr_complete.txt",
                    "page_3_chinese_ocr_detail.txt",
                    "page_4_chinese_ocr_detail.txt",
                    "page_1_chinese_ocr_detail.txt"
                ],
                description="PDF轉Markdown、OCR識別、表格識別、版面分析，多技術融合文檔處理"
            )
        ]
        
        return tasks
    
    async def _perform_clustering_analysis(self, tasks: List[ManusTaskData]) -> Dict[str, List[ManusTaskData]]:
        """執行聚類分析"""
        try:
            clusters = {}
            
            for task in tasks:
                cluster_name = self._classify_task_by_keywords(task)
                if cluster_name not in clusters:
                    clusters[cluster_name] = []
                clusters[cluster_name].append(task)
            
            self.logger.info(f"聚類分析完成，共生成 {len(clusters)} 個聚類")
            return clusters
            
        except Exception as e:
            self.logger.error(f"聚類分析失敗: {e}")
            return {}
    
    def _classify_task_by_keywords(self, task: ManusTaskData) -> str:
        """基於關鍵詞對任務進行分類"""
        try:
            task_text = f"{task.name} {task.description} {task.category}".lower()
            
            # 計算每個聚類的匹配分數
            cluster_scores = {}
            for cluster_name, keywords in self.cluster_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword.lower() in task_text:
                        score += 1
                cluster_scores[cluster_name] = score
            
            # 找出最高分的聚類
            if cluster_scores:
                best_cluster = max(cluster_scores, key=cluster_scores.get)
                if cluster_scores[best_cluster] > 0:
                    return best_cluster
            
            return "General_Tasks"
            
        except Exception as e:
            self.logger.error(f"任務分類失敗: {e}")
            return "General_Tasks"
    
    async def _assign_task_ids(self, clusters: Dict[str, List[ManusTaskData]]) -> Dict[str, TaskClusterInfo]:
        """為每個聚類分配TaskID"""
        try:
            task_groups = {}
            task_id_counter = 1
            
            # 按重要性排序聚類
            sorted_clusters = sorted(
                clusters.items(),
                key=lambda x: self.importance_weights.get(x[0].split('_')[0], 0),
                reverse=True
            )
            
            for cluster_name, cluster_tasks in sorted_clusters:
                # 生成TaskID
                task_id = f"TASK_{task_id_counter:03d}"
                task_id_counter += 1
                
                # 創建聚類信息
                cluster_info = TaskClusterInfo(
                    cluster_id=task_id,
                    cluster_name=cluster_name,
                    task_count=len(cluster_tasks),
                    importance_level=self.importance_weights.get(cluster_name.split('_')[0], 1),
                    description=self._generate_cluster_description(cluster_name, cluster_tasks),
                    tasks=cluster_tasks
                )
                
                task_groups[task_id] = cluster_info
            
            self.logger.info(f"成功分配 {len(task_groups)} 個TaskID")
            return task_groups
            
        except Exception as e:
            self.logger.error(f"TaskID分配失敗: {e}")
            return {}
    
    def _generate_cluster_description(self, cluster_name: str, tasks: List[ManusTaskData]) -> str:
        """生成聚類描述"""
        base_descriptions = {
            "OCR_Commercial": "OCR商業化技術實現，包含文字識別、文檔處理、表格識別等核心功能",
            "MCP_Architecture": "MCP架構設計與實現，端雲協同系統、智慧路由、Memory System整合",
            "AI_Model_Comparison": "AI模型性能比較與評估，包含Gemini、Claude等主流模型對比分析",
            "VSCode_Extension": "VSCode擴展開發，PowerAutomation插件功能實現與優化",
            "UI_UX_Design": "用戶界面與體驗設計，前端功能優化與界面改進",
            "Enterprise_Solutions": "企業級解決方案，業務流程自動化與產品管理系統",
            "General_Tasks": "通用任務與其他功能實現"
        }
        
        base_desc = base_descriptions.get(cluster_name.split('_')[0], "相關技術任務群組")
        task_names = [task.name for task in tasks[:3]]
        if len(tasks) > 3:
            task_names.append(f"等{len(tasks)}個任務")
        
        return f"{base_desc}。包含任務：{', '.join(task_names)}"

class CloudDataStorage:
    """雲端數據存儲 - 整合EC2存儲功能"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 存儲配置
        self.storage_config = config.get('storage', {
            'base_path': '/home/ec2-user/smartinvention_mcp',
            'tasks_path': '/home/ec2-user/smartinvention_mcp/tasks',
            'backup_enabled': True,
            'compression_enabled': True
        })
        
        # EC2連接配置
        self.ec2_config = config.get('ec2', {
            'host': '18.212.97.173',
            'user': 'ec2-user',
            'key_path': '/home/ubuntu/alexchuang.pem'
        })
    
    async def upload_task_groups_to_ec2(self, task_groups: Dict[str, TaskClusterInfo]) -> Dict[str, Any]:
        """上傳TaskID群組到EC2"""
        try:
            self.logger.info("開始上傳TaskID群組到EC2...")
            
            # 創建本地臨時目錄
            temp_dir = Path("/tmp/manus_upload")
            temp_dir.mkdir(exist_ok=True)
            
            # 為每個TaskID創建目錄結構和文件
            upload_results = {}
            for task_id, cluster_info in task_groups.items():
                result = await self._create_taskid_structure(temp_dir, task_id, cluster_info)
                upload_results[task_id] = result
            
            # 上傳到EC2
            ec2_result = await self._upload_to_ec2(temp_dir)
            
            # 清理臨時目錄
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return {
                "success": True,
                "task_groups_uploaded": len(task_groups),
                "upload_results": upload_results,
                "ec2_result": ec2_result,
                "upload_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"上傳TaskID群組失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "upload_time": datetime.now().isoformat()
            }
    
    async def _create_taskid_structure(self, base_dir: Path, task_id: str, cluster_info: TaskClusterInfo) -> Dict[str, Any]:
        """為TaskID創建目錄結構"""
        try:
            task_dir = base_dir / task_id
            
            # 創建標準目錄結構
            directories = [
                "conversations_analysis/raw_conversations",
                "conversations_analysis/processed_analysis", 
                "conversations_analysis/insights_summary",
                "corrected_files/original_files",
                "corrected_files/corrected_versions",
                "corrected_files/optimization_notes",
                "reports/technical_analysis",
                "reports/implementation_guide",
                "reports/best_practices",
                "metadata"
            ]
            
            for dir_path in directories:
                (task_dir / dir_path).mkdir(parents=True, exist_ok=True)
            
            # 創建任務信息文件
            task_info = {
                "task_id": task_id,
                "cluster_name": cluster_info.cluster_name,
                "description": cluster_info.description,
                "task_count": cluster_info.task_count,
                "importance_level": cluster_info.importance_level,
                "tasks": [
                    {
                        "name": task.name,
                        "date": task.date,
                        "replay_link": task.replay_link,
                        "category": task.category,
                        "files": task.files,
                        "description": task.description
                    }
                    for task in cluster_info.tasks
                ],
                "created_at": datetime.now().isoformat(),
                "status": "initialized"
            }
            
            # 保存任務信息
            info_file = task_dir / "metadata" / "task_info.json"
            async with aiofiles.open(info_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(task_info, indent=2, ensure_ascii=False))
            
            # 創建README文件
            readme_content = f"""# {task_id}: {cluster_info.cluster_name}

## 任務群組信息

- **TaskID**: {task_id}
- **群組名稱**: {cluster_info.cluster_name}
- **重要性等級**: {cluster_info.importance_level}
- **任務數量**: {cluster_info.task_count}
- **創建時間**: {datetime.now().isoformat()}

## 描述

{cluster_info.description}

## 任務列表

{chr(10).join(f"- {task.name} ({task.date})" for task in cluster_info.tasks)}

## 目錄結構

```
{task_id}/
├── conversations_analysis/     # 對話分析結果
│   ├── raw_conversations/     # 原始對話數據
│   ├── processed_analysis/    # 處理後的分析結果
│   └── insights_summary/      # 洞察總結報告
├── corrected_files/           # 修正檔案
│   ├── original_files/        # 原始檔案
│   ├── corrected_versions/    # 修正版本
│   └── optimization_notes/    # 優化說明
├── reports/                   # 技術報告
│   ├── technical_analysis/    # 技術分析報告
│   ├── implementation_guide/  # 實施指南
│   └── best_practices/        # 最佳實踐文檔
└── metadata/                  # 元數據信息
    ├── task_info.json        # 任務基本信息
    ├── progress_tracking.json # 進度追蹤
    └── resource_inventory.json # 資源清單
```
"""
            
            readme_file = task_dir / "README.md"
            async with aiofiles.open(readme_file, 'w', encoding='utf-8') as f:
                await f.write(readme_content)
            
            return {
                "success": True,
                "task_id": task_id,
                "directories_created": len(directories),
                "files_created": 2
            }
            
        except Exception as e:
            self.logger.error(f"創建TaskID結構失敗 {task_id}: {e}")
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e)
            }
    
    async def _upload_to_ec2(self, local_dir: Path) -> Dict[str, Any]:
        """上傳到EC2服務器"""
        try:
            host = self.ec2_config['host']
            user = self.ec2_config['user']
            key_path = self.ec2_config['key_path']
            remote_path = self.storage_config['tasks_path']
            
            # 使用rsync上傳
            cmd = [
                'rsync', '-avz', '--progress',
                '-e', f'ssh -i {key_path} -o StrictHostKeyChecking=no',
                f'{local_dir}/',
                f'{user}@{host}:{remote_path}/'
            ]
            
            self.logger.info(f"執行上傳命令: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "stdout": stdout.decode(),
                    "remote_path": remote_path
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode(),
                    "stdout": stdout.decode()
                }
                
        except Exception as e:
            self.logger.error(f"EC2上傳失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def save_analysis_results(self, analysis_data: Dict, metadata: Dict) -> str:
        """保存分析結果到雲端"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"manus_analysis_{timestamp}.json"
            
            # 準備保存數據
            save_data = {
                "metadata": metadata,
                "analysis_data": analysis_data,
                "save_time": datetime.now().isoformat(),
                "version": "3.0.0"
            }
            
            # 本地保存
            local_path = f"/tmp/{filename}"
            async with aiofiles.open(local_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(save_data, indent=2, ensure_ascii=False))
            
            # 上傳到EC2
            await self._upload_single_file_to_ec2(local_path, filename)
            
            self.logger.info(f"分析結果已保存: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"保存分析結果失敗: {e}")
            raise
    
    async def _upload_single_file_to_ec2(self, local_file: str, remote_filename: str):
        """上傳單個文件到EC2"""
        try:
            host = self.ec2_config['host']
            user = self.ec2_config['user']
            key_path = self.ec2_config['key_path']
            remote_path = f"{self.storage_config['tasks_path']}/{remote_filename}"
            
            cmd = [
                'scp', '-i', key_path, '-o', 'StrictHostKeyChecking=no',
                local_file,
                f'{user}@{host}:{remote_path}'
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"SCP上傳失敗，返回碼: {process.returncode}")
                
        except Exception as e:
            self.logger.error(f"單文件上傳失敗: {e}")
            raise

class SmartinventionAdapterMCP(MCPComponent):
    """增強版Smartinvention適配器 - 包含Manus功能"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.version = "3.0.0"
        
        # 初始化子組件
        self.manus_collector = ManusTaskCollector(config or {})
        self.cloud_storage = CloudDataStorage(config or {})
        
        # 原有的對話處理功能保持不變
        self.conversation_storage = ConversationStorage(
            config.get('data_dir', '/tmp/smartinvention_data')
        )
        self.conversation_processor = ConversationProcessor(config or {})
    
    async def initialize(self) -> Dict[str, Any]:
        """初始化組件"""
        try:
            # 初始化基礎組件
            base_result = await super().initialize()
            
            # 初始化Manus收集器
            await self.manus_collector.initialize_session()
            
            self.logger.info("SmartinventionAdapterMCP v3.0.0 初始化完成")
            
            return {
                **base_result,
                "manus_collector": "initialized",
                "cloud_storage": "initialized",
                "features": [
                    "conversation_processing",
                    "manus_task_collection", 
                    "cloud_data_storage",
                    "taskid_management"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"初始化失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def collect_and_store_manus_tasks(self, app_url: str) -> Dict[str, Any]:
        """收集並存儲Manus任務 - 主要API"""
        try:
            self.logger.info("開始收集和存儲Manus任務...")
            
            # 收集任務
            collection_result = await self.manus_collector.collect_manus_tasks(app_url)
            
            if not collection_result.get("success"):
                return collection_result
            
            # 上傳到雲端存儲
            task_groups = collection_result.get("task_groups", {})
            storage_result = await self.cloud_storage.upload_task_groups_to_ec2(task_groups)
            
            # 保存分析結果
            analysis_filename = await self.cloud_storage.save_analysis_results(
                collection_result,
                {
                    "operation": "manus_task_collection",
                    "app_url": app_url,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return {
                "success": True,
                "collection_result": collection_result,
                "storage_result": storage_result,
                "analysis_filename": analysis_filename,
                "summary": {
                    "total_tasks": collection_result.get("total_tasks", 0),
                    "clusters_count": collection_result.get("clusters_count", 0),
                    "task_groups_uploaded": storage_result.get("task_groups_uploaded", 0)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"收集和存儲Manus任務失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_taskid_status(self) -> Dict[str, Any]:
        """獲取TaskID狀態"""
        try:
            # 這裡可以實現從EC2獲取TaskID狀態的邏輯
            # 目前返回模擬數據
            return {
                "success": True,
                "taskids": {
                    "TASK_001": {"status": "initialized", "cluster": "UI_UX_Design"},
                    "TASK_002": {"status": "initialized", "cluster": "AI_Model_Comparison"},
                    "TASK_003": {"status": "initialized", "cluster": "MCP_Architecture"},
                    "TASK_004": {"status": "initialized", "cluster": "OCR_Commercial"}
                },
                "total_taskids": 9,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"獲取TaskID狀態失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # 保持原有的對話處理功能
    async def process_conversation_sync(self, conversations: List[Dict], metadata: Dict) -> Dict:
        """處理對話同步請求"""
        return await self.conversation_processor.process_conversation_sync(conversations, metadata)
    
    async def get_latest_conversations(self, limit: int = 10) -> Dict:
        """獲取最新對話"""
        return await self.conversation_processor.get_latest_conversations(limit)
    
    async def get_interventions_needed(self) -> Dict:
        """獲取需要介入的對話"""
        return await self.conversation_processor.get_interventions_needed()
    
    async def cleanup(self):
        """清理資源"""
        try:
            await self.manus_collector.close_session()
            self.logger.info("SmartinventionAdapterMCP 資源清理完成")
        except Exception as e:
            self.logger.error(f"資源清理失敗: {e}")

# 原有的其他類保持不變...
class ConversationStorage:
    """對話數據存儲 - 整合原EC2存儲邏輯"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.logs_dir = self.data_dir / "logs"
        
        # 確保目錄存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
    
    async def save_conversations(self, conversations: List[Dict], metadata: Dict) -> str:
        """保存對話數據"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversations_{timestamp}.json"
            filepath = self.data_dir / filename
            
            # 準備保存數據
            save_data = {
                "metadata": metadata,
                "conversations": conversations,
                "total_count": len(conversations),
                "save_time": datetime.now().isoformat(),
                "file_version": "1.0"
            }
            
            # 保存到文件
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(save_data, indent=2, ensure_ascii=False))
            
            self.logger.info(f"保存 {len(conversations)} 條對話到 {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"保存對話失敗: {e}")
            raise

class ConversationProcessor:
    """對話處理器 - 整合原EC2對話分析功能"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.storage = ConversationStorage(config.get('data_dir', '/tmp/smartinvention_data'))
        self.logger = logging.getLogger(__name__)
    
    async def process_conversation_sync(self, conversations: List[Dict], metadata: Dict) -> Dict:
        """處理對話同步請求"""
        try:
            self.logger.info(f"處理對話同步請求: {len(conversations)} 條對話")
            
            # 保存對話數據
            filename = await self.storage.save_conversations(conversations, metadata)
            
            return {
                "success": True,
                "conversations_saved": len(conversations),
                "filename": filename,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"對話同步處理失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_latest_conversations(self, limit: int = 10) -> Dict:
        """獲取最新對話"""
        try:
            # 實現獲取最新對話的邏輯
            return {
                "success": True,
                "conversations": [],
                "count": 0,
                "limit": limit,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"獲取最新對話失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_interventions_needed(self) -> Dict:
        """獲取需要介入的對話"""
        try:
            # 實現獲取介入需求的邏輯
            return {
                "success": True,
                "interventions": [],
                "count": 0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"獲取介入需求失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# 主要導出
__all__ = [
    'SmartinventionAdapterMCP',
    'ManusTaskCollector', 
    'CloudDataStorage',
    'ManusTaskData',
    'TaskClusterInfo'
]

if __name__ == "__main__":
    # 測試代碼
    async def test_mcp():
        config = {
            'data_dir': '/tmp/test_smartinvention',
            'storage': {
                'base_path': '/home/ec2-user/smartinvention_mcp',
                'tasks_path': '/home/ec2-user/smartinvention_mcp/tasks'
            },
            'ec2': {
                'host': '18.212.97.173',
                'user': 'ec2-user',
                'key_path': '/home/ubuntu/alexchuang.pem'
            }
        }
        
        mcp = SmartinventionAdapterMCP(config)
        
        # 初始化
        init_result = await mcp.initialize()
        print("初始化結果:", init_result)
        
        # 測試Manus任務收集
        collection_result = await mcp.collect_and_store_manus_tasks("https://manus.im/app/test")
        print("收集結果:", collection_result)
        
        # 清理
        await mcp.cleanup()
    
    # 運行測試
    # asyncio.run(test_mcp())

