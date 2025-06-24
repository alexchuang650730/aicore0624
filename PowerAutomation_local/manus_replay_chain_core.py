"""
Manus Replay Chain System - 核心實現
實現任務整合和鏈結邏輯的核心模組

Author: Manus AI
Version: 1.0.0
Date: 2025-06-23
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering
import networkx as nx


class TaskStatus(Enum):
    """任務狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class ChainStatus(Enum):
    """鏈結狀態"""
    CREATED = "created"
    OPTIMIZING = "optimizing"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskNode:
    """任務節點 - Replay鏈結的基本單元"""
    task_id: str
    task_type: str
    description: str
    parameters: Dict[str, Any]
    priority: int = 5
    estimated_duration: float = 30.0
    dependencies: List[str] = field(default_factory=list)
    outputs: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskNode':
        """從字典創建"""
        data['status'] = TaskStatus(data['status'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class TaskSimilarity:
    """任務相似性分析結果"""
    task1_id: str
    task2_id: str
    similarity_score: float
    similarity_factors: Dict[str, float]
    recommended_chain: bool
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        data = asdict(self)
        data['analysis_timestamp'] = self.analysis_timestamp.isoformat()
        return data


@dataclass
class ReplayChain:
    """Replay鏈結 - 相關任務的執行序列"""
    chain_id: str
    chain_name: str
    description: str
    nodes: List[TaskNode] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)
    shared_context: Dict[str, Any] = field(default_factory=dict)
    total_estimated_duration: float = 0.0
    optimization_score: float = 0.0
    status: ChainStatus = ChainStatus.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    success_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_node(self, node: TaskNode):
        """添加任務節點"""
        self.nodes.append(node)
        self.total_estimated_duration += node.estimated_duration
        self.updated_at = datetime.now()
    
    def remove_node(self, task_id: str):
        """移除任務節點"""
        self.nodes = [node for node in self.nodes if node.task_id != task_id]
        self.execution_order = [tid for tid in self.execution_order if tid != task_id]
        self._recalculate_duration()
    
    def _recalculate_duration(self):
        """重新計算總執行時間"""
        self.total_estimated_duration = sum(node.estimated_duration for node in self.nodes)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        data = asdict(self)
        data['nodes'] = [node.to_dict() for node in self.nodes]
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['last_executed'] = self.last_executed.isoformat() if self.last_executed else None
        return data


@dataclass
class TaskExecutionResult:
    """任務執行結果"""
    task_id: str
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    success: bool = False
    error_message: Optional[str] = None
    outputs: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)


@dataclass
class ChainExecutionResult:
    """鏈結執行結果"""
    chain_id: str
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: float = 0.0
    node_results: List[TaskExecutionResult] = field(default_factory=list)
    success: bool = False
    error_message: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)


class TaskSimilarityAnalyzer:
    """任務相似性分析器"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.logger = logging.getLogger(__name__)
    
    def analyze_similarity(self, task1: TaskNode, task2: TaskNode) -> TaskSimilarity:
        """分析兩個任務的相似性"""
        try:
            # 計算各種相似性因子
            factors = {}
            
            # 1. 時間相似性
            factors['temporal_similarity'] = self._calculate_temporal_similarity(task1, task2)
            
            # 2. 內容相似性
            factors['content_similarity'] = self._calculate_content_similarity(task1, task2)
            
            # 3. 操作相似性
            factors['operation_similarity'] = self._calculate_operation_similarity(task1, task2)
            
            # 4. 參數相似性
            factors['parameter_similarity'] = self._calculate_parameter_similarity(task1, task2)
            
            # 5. 依賴相似性
            factors['dependency_similarity'] = self._calculate_dependency_similarity(task1, task2)
            
            # 計算總相似性分數
            weights = {
                'temporal_similarity': 0.2,
                'content_similarity': 0.3,
                'operation_similarity': 0.25,
                'parameter_similarity': 0.15,
                'dependency_similarity': 0.1
            }
            
            similarity_score = sum(
                factors[factor] * weights[factor] 
                for factor in factors
            )
            
            # 判斷是否推薦組成鏈結
            recommended_chain = similarity_score > 0.6
            
            return TaskSimilarity(
                task1_id=task1.task_id,
                task2_id=task2.task_id,
                similarity_score=similarity_score,
                similarity_factors=factors,
                recommended_chain=recommended_chain
            )
            
        except Exception as e:
            self.logger.error(f"分析任務相似性失敗: {e}")
            return TaskSimilarity(
                task1_id=task1.task_id,
                task2_id=task2.task_id,
                similarity_score=0.0,
                similarity_factors={},
                recommended_chain=False
            )
    
    def _calculate_temporal_similarity(self, task1: TaskNode, task2: TaskNode) -> float:
        """計算時間相似性"""
        time_diff = abs((task1.created_at - task2.created_at).total_seconds())
        # 使用指數衰減函數，5分鐘內的任務相似性最高
        return np.exp(-time_diff / 300)  # 300秒 = 5分鐘
    
    def _calculate_content_similarity(self, task1: TaskNode, task2: TaskNode) -> float:
        """計算內容相似性"""
        try:
            # 組合任務描述和參數文本
            text1 = f"{task1.description} {json.dumps(task1.parameters, ensure_ascii=False)}"
            text2 = f"{task2.description} {json.dumps(task2.parameters, ensure_ascii=False)}"
            
            # 使用TF-IDF向量化
            vectors = self.vectorizer.fit_transform([text1, text2])
            similarity_matrix = cosine_similarity(vectors)
            
            return float(similarity_matrix[0, 1])
            
        except Exception:
            return 0.0
    
    def _calculate_operation_similarity(self, task1: TaskNode, task2: TaskNode) -> float:
        """計算操作相似性"""
        if task1.task_type == task2.task_type:
            return 1.0
        
        # 定義操作類型的相似性映射
        operation_groups = {
            'auth': ['login', 'logout', 'authenticate'],
            'message': ['send_message', 'get_messages', 'delete_message'],
            'conversation': ['get_conversations', 'create_conversation', 'join_conversation'],
            'task': ['get_tasks', 'create_task', 'update_task', 'delete_task'],
            'file': ['download_files', 'upload_files', 'delete_files']
        }
        
        # 查找任務類型所屬的組
        group1 = None
        group2 = None
        
        for group, operations in operation_groups.items():
            if task1.task_type in operations:
                group1 = group
            if task2.task_type in operations:
                group2 = group
        
        if group1 and group2 and group1 == group2:
            return 0.8  # 同組操作有較高相似性
        
        return 0.0
    
    def _calculate_parameter_similarity(self, task1: TaskNode, task2: TaskNode) -> float:
        """計算參數相似性"""
        try:
            params1 = set(task1.parameters.keys())
            params2 = set(task2.parameters.keys())
            
            if not params1 and not params2:
                return 1.0
            
            if not params1 or not params2:
                return 0.0
            
            # 使用Jaccard係數
            intersection = len(params1.intersection(params2))
            union = len(params1.union(params2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_dependency_similarity(self, task1: TaskNode, task2: TaskNode) -> float:
        """計算依賴相似性"""
        try:
            deps1 = set(task1.dependencies)
            deps2 = set(task2.dependencies)
            
            if not deps1 and not deps2:
                return 1.0
            
            if not deps1 or not deps2:
                return 0.0
            
            # 使用Jaccard係數
            intersection = len(deps1.intersection(deps2))
            union = len(deps1.union(deps2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception:
            return 0.0


class ChainGenerator:
    """鏈結生成器"""
    
    def __init__(self):
        self.similarity_analyzer = TaskSimilarityAnalyzer()
        self.logger = logging.getLogger(__name__)
    
    def generate_chains(self, tasks: List[TaskNode]) -> List[ReplayChain]:
        """生成任務鏈結"""
        try:
            if len(tasks) < 2:
                return []
            
            self.logger.info(f"開始為 {len(tasks)} 個任務生成鏈結...")
            
            # 1. 計算任務相似性矩陣
            similarity_matrix = self._build_similarity_matrix(tasks)
            
            # 2. 執行聚類分析
            clusters = self._perform_clustering(tasks, similarity_matrix)
            
            # 3. 為每個聚類生成鏈結
            chains = []
            for cluster_id, cluster_tasks in clusters.items():
                if len(cluster_tasks) > 1:  # 只有多個任務才生成鏈結
                    chain = self._create_chain_from_cluster(cluster_tasks)
                    if chain:
                        chains.append(chain)
            
            self.logger.info(f"成功生成 {len(chains)} 個鏈結")
            return chains
            
        except Exception as e:
            self.logger.error(f"生成鏈結失敗: {e}")
            return []
    
    def _build_similarity_matrix(self, tasks: List[TaskNode]) -> np.ndarray:
        """構建相似性矩陣"""
        n = len(tasks)
        matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                similarity = self.similarity_analyzer.analyze_similarity(tasks[i], tasks[j])
                matrix[i, j] = similarity.similarity_score
                matrix[j, i] = similarity.similarity_score
        
        return matrix
    
    def _perform_clustering(self, tasks: List[TaskNode], similarity_matrix: np.ndarray) -> Dict[int, List[TaskNode]]:
        """執行聚類分析"""
        try:
            # 轉換相似性矩陣為距離矩陣
            distance_matrix = 1 - similarity_matrix
            
            # 使用DBSCAN聚類（避免ward linkage的歐幾里得距離要求）
            from sklearn.cluster import DBSCAN
            
            clustering = DBSCAN(
                eps=0.5,  # 鄰域半徑
                min_samples=2,  # 最小樣本數
                metric='precomputed'
            )
            
            cluster_labels = clustering.fit_predict(distance_matrix)
            
            # 組織聚類結果
            clusters = {}
            for i, label in enumerate(cluster_labels):
                if label == -1:  # 噪聲點，單獨成組
                    clusters[f"noise_{i}"] = [tasks[i]]
                else:
                    if label not in clusters:
                        clusters[label] = []
                    clusters[label].append(tasks[i])
            
            return clusters
            
        except Exception as e:
            self.logger.error(f"聚類分析失敗: {e}")
            # 返回每個任務單獨成為一個聚類
            return {i: [task] for i, task in enumerate(tasks)}
    
    def _create_chain_from_cluster(self, tasks: List[TaskNode]) -> Optional[ReplayChain]:
        """從聚類創建鏈結"""
        try:
            # 生成鏈結ID和名稱
            chain_id = f"chain_{uuid.uuid4().hex[:8]}"
            chain_name = self._generate_chain_name(tasks)
            description = self._generate_chain_description(tasks)
            
            # 創建鏈結
            chain = ReplayChain(
                chain_id=chain_id,
                chain_name=chain_name,
                description=description
            )
            
            # 添加任務節點
            for task in tasks:
                chain.add_node(task)
            
            # 優化執行順序
            chain.execution_order = self._optimize_execution_order(tasks)
            
            # 計算優化分數
            chain.optimization_score = self._calculate_optimization_score(chain)
            
            # 設置狀態為就緒
            chain.status = ChainStatus.READY
            
            return chain
            
        except Exception as e:
            self.logger.error(f"創建鏈結失敗: {e}")
            return None
    
    def _generate_chain_name(self, tasks: List[TaskNode]) -> str:
        """生成鏈結名稱"""
        # 提取主要操作類型
        operation_types = [task.task_type for task in tasks]
        unique_types = list(set(operation_types))
        
        if len(unique_types) == 1:
            return f"{unique_types[0]}_chain_{len(tasks)}tasks"
        else:
            return f"mixed_chain_{len(tasks)}tasks"
    
    def _generate_chain_description(self, tasks: List[TaskNode]) -> str:
        """生成鏈結描述"""
        operation_counts = {}
        for task in tasks:
            operation_counts[task.task_type] = operation_counts.get(task.task_type, 0) + 1
        
        descriptions = []
        for op_type, count in operation_counts.items():
            if count == 1:
                descriptions.append(f"1個{op_type}任務")
            else:
                descriptions.append(f"{count}個{op_type}任務")
        
        return f"包含{', '.join(descriptions)}的自動化鏈結"
    
    def _optimize_execution_order(self, tasks: List[TaskNode]) -> List[str]:
        """優化執行順序"""
        try:
            # 創建依賴圖
            graph = nx.DiGraph()
            
            # 添加節點
            for task in tasks:
                graph.add_node(task.task_id, task=task)
            
            # 添加依賴邊
            for task in tasks:
                for dep_id in task.dependencies:
                    if dep_id in [t.task_id for t in tasks]:
                        graph.add_edge(dep_id, task.task_id)
            
            # 檢查是否有循環依賴
            if not nx.is_directed_acyclic_graph(graph):
                self.logger.warning("檢測到循環依賴，使用優先級排序")
                return self._sort_by_priority(tasks)
            
            # 拓撲排序
            try:
                topo_order = list(nx.topological_sort(graph))
                return topo_order
            except nx.NetworkXError:
                return self._sort_by_priority(tasks)
            
        except Exception as e:
            self.logger.error(f"優化執行順序失敗: {e}")
            return self._sort_by_priority(tasks)
    
    def _sort_by_priority(self, tasks: List[TaskNode]) -> List[str]:
        """按優先級排序"""
        sorted_tasks = sorted(tasks, key=lambda t: (-t.priority, t.created_at))
        return [task.task_id for task in sorted_tasks]
    
    def _calculate_optimization_score(self, chain: ReplayChain) -> float:
        """計算優化分數"""
        try:
            # 時間節省因子（假設獨立執行需要額外的初始化時間）
            independent_time = sum(node.estimated_duration + 10 for node in chain.nodes)  # 每個任務額外10秒初始化
            chain_time = chain.total_estimated_duration + 10  # 鏈結只需要一次初始化
            time_saving_factor = max(0, (independent_time - chain_time) / independent_time)
            
            # 資源效率因子（基於任務數量）
            resource_efficiency_factor = min(1.0, len(chain.nodes) / 10)  # 最多10個任務達到最高效率
            
            # 用戶體驗因子（減少用戶干預次數）
            user_experience_factor = min(1.0, (len(chain.nodes) - 1) / len(chain.nodes))
            
            # 成功概率因子（基於任務類型的歷史成功率，這裡使用默認值）
            success_probability_factor = 0.9  # 默認90%成功率
            
            # 計算總分
            optimization_score = (
                time_saving_factor * 0.4 +
                resource_efficiency_factor * 0.3 +
                user_experience_factor * 0.2 +
                success_probability_factor * 0.1
            )
            
            return round(optimization_score, 3)
            
        except Exception as e:
            self.logger.error(f"計算優化分數失敗: {e}")
            return 0.0


class SharedContext:
    """共享上下文管理器"""
    
    def __init__(self):
        self.browser_session = None
        self.authentication_state = {}
        self.cached_data = {}
        self.performance_metrics = {}
        self.logger = logging.getLogger(__name__)
    
    async def get_browser_session(self):
        """獲取共享瀏覽器會話"""
        if not self.browser_session:
            self.browser_session = await self._create_browser_session()
        return self.browser_session
    
    async def _create_browser_session(self):
        """創建瀏覽器會話"""
        from playwright.async_api import async_playwright
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=False,
            slow_mo=1000
        )
        return browser
    
    async def cache_data(self, key: str, data: Any, ttl: int = 3600):
        """緩存數據"""
        self.cached_data[key] = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl
        }
        self.logger.debug(f"緩存數據: {key}")
    
    async def get_cached_data(self, key: str) -> Optional[Any]:
        """獲取緩存數據"""
        if key in self.cached_data:
            cache_entry = self.cached_data[key]
            if time.time() - cache_entry['timestamp'] < cache_entry['ttl']:
                return cache_entry['data']
            else:
                del self.cached_data[key]
                self.logger.debug(f"緩存過期，刪除: {key}")
        return None
    
    async def set_authentication_state(self, service: str, state: Dict[str, Any]):
        """設置認證狀態"""
        self.authentication_state[service] = {
            'state': state,
            'timestamp': time.time()
        }
        self.logger.debug(f"設置認證狀態: {service}")
    
    async def get_authentication_state(self, service: str) -> Optional[Dict[str, Any]]:
        """獲取認證狀態"""
        if service in self.authentication_state:
            auth_entry = self.authentication_state[service]
            # 認證狀態1小時內有效
            if time.time() - auth_entry['timestamp'] < 3600:
                return auth_entry['state']
            else:
                del self.authentication_state[service]
                self.logger.debug(f"認證狀態過期，刪除: {service}")
        return None
    
    async def cleanup(self):
        """清理資源"""
        if self.browser_session:
            await self.browser_session.close()
            self.browser_session = None
        
        self.cached_data.clear()
        self.authentication_state.clear()
        self.logger.info("共享上下文已清理")


class ChainExecutor:
    """鏈結執行器"""
    
    def __init__(self, shared_context: SharedContext):
        self.shared_context = shared_context
        self.logger = logging.getLogger(__name__)
        self.running_executions = {}
    
    async def execute_chain(self, chain: ReplayChain) -> ChainExecutionResult:
        """執行鏈結"""
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now()
        
        self.logger.info(f"開始執行鏈結: {chain.chain_id} (執行ID: {execution_id})")
        
        # 創建執行結果對象
        result = ChainExecutionResult(
            chain_id=chain.chain_id,
            execution_id=execution_id,
            start_time=start_time
        )
        
        # 記錄執行
        self.running_executions[execution_id] = {
            'chain': chain,
            'result': result,
            'start_time': start_time
        }
        
        try:
            # 更新鏈結狀態
            chain.status = ChainStatus.EXECUTING
            
            # 按順序執行任務
            for task_id in chain.execution_order:
                task_node = next((node for node in chain.nodes if node.task_id == task_id), None)
                if not task_node:
                    continue
                
                # 執行任務
                task_result = await self._execute_task(task_node, execution_id)
                result.node_results.append(task_result)
                
                # 如果任務失敗且是關鍵任務，停止執行
                if not task_result.success and task_node.priority >= 8:
                    result.success = False
                    result.error_message = f"關鍵任務失敗: {task_result.error_message}"
                    break
            
            # 計算總體結果
            if result.error_message is None:
                successful_tasks = sum(1 for tr in result.node_results if tr.success)
                result.success = successful_tasks >= len(result.node_results) * 0.8  # 80%成功率
            
            # 更新鏈結狀態
            chain.status = ChainStatus.COMPLETED if result.success else ChainStatus.FAILED
            chain.last_executed = datetime.now()
            chain.execution_count += 1
            
            # 更新成功率
            if chain.execution_count > 0:
                if result.success:
                    chain.success_rate = (chain.success_rate * (chain.execution_count - 1) + 1) / chain.execution_count
                else:
                    chain.success_rate = (chain.success_rate * (chain.execution_count - 1)) / chain.execution_count
            
        except Exception as e:
            self.logger.error(f"執行鏈結失敗: {e}")
            result.success = False
            result.error_message = str(e)
            chain.status = ChainStatus.FAILED
        
        finally:
            # 完成執行
            result.end_time = datetime.now()
            result.total_duration = (result.end_time - result.start_time).total_seconds()
            
            # 清理執行記錄
            if execution_id in self.running_executions:
                del self.running_executions[execution_id]
            
            self.logger.info(f"鏈結執行完成: {chain.chain_id}, 成功: {result.success}, 耗時: {result.total_duration:.2f}秒")
        
        return result
    
    async def _execute_task(self, task_node: TaskNode, execution_id: str) -> TaskExecutionResult:
        """執行單個任務"""
        start_time = datetime.now()
        
        self.logger.info(f"執行任務: {task_node.task_id} ({task_node.task_type})")
        
        # 創建任務執行結果
        task_result = TaskExecutionResult(
            task_id=task_node.task_id,
            execution_id=execution_id,
            start_time=start_time
        )
        
        try:
            # 更新任務狀態
            task_node.status = TaskStatus.RUNNING
            
            # 根據任務類型執行相應操作
            if task_node.task_type == "manus_login":
                task_result.outputs = await self._execute_manus_login(task_node)
            elif task_node.task_type == "send_message":
                task_result.outputs = await self._execute_send_message(task_node)
            elif task_node.task_type == "get_conversations":
                task_result.outputs = await self._execute_get_conversations(task_node)
            elif task_node.task_type == "get_tasks":
                task_result.outputs = await self._execute_get_tasks(task_node)
            elif task_node.task_type == "download_files":
                task_result.outputs = await self._execute_download_files(task_node)
            else:
                raise ValueError(f"不支持的任務類型: {task_node.task_type}")
            
            # 任務成功
            task_result.success = True
            task_node.status = TaskStatus.COMPLETED
            task_node.outputs = task_result.outputs
            
        except Exception as e:
            self.logger.error(f"任務執行失敗: {task_node.task_id}, 錯誤: {e}")
            task_result.success = False
            task_result.error_message = str(e)
            task_node.status = TaskStatus.FAILED
        
        finally:
            # 完成任務
            task_result.end_time = datetime.now()
            task_result.duration = (task_result.end_time - task_result.start_time).total_seconds()
            task_node.updated_at = datetime.now()
        
        return task_result
    
    async def _execute_manus_login(self, task_node: TaskNode) -> Dict[str, Any]:
        """執行Manus登錄任務"""
        # 檢查是否已有認證狀態
        auth_state = await self.shared_context.get_authentication_state("manus")
        if auth_state:
            self.logger.info("使用緩存的認證狀態")
            return {"status": "already_logged_in", "cached": True}
        
        # 執行登錄邏輯（這裡是模擬實現）
        await asyncio.sleep(2)  # 模擬登錄時間
        
        # 設置認證狀態
        auth_state = {
            "logged_in": True,
            "user_id": "test_user",
            "session_token": "mock_token_123"
        }
        await self.shared_context.set_authentication_state("manus", auth_state)
        
        return {"status": "login_success", "user_id": "test_user"}
    
    async def _execute_send_message(self, task_node: TaskNode) -> Dict[str, Any]:
        """執行發送消息任務"""
        message = task_node.parameters.get("message", "")
        if not message:
            raise ValueError("消息內容不能為空")
        
        # 檢查認證狀態
        auth_state = await self.shared_context.get_authentication_state("manus")
        if not auth_state:
            raise ValueError("未登錄，無法發送消息")
        
        # 執行發送消息邏輯（模擬實現）
        await asyncio.sleep(1)  # 模擬發送時間
        
        return {
            "status": "message_sent",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _execute_get_conversations(self, task_node: TaskNode) -> Dict[str, Any]:
        """執行獲取對話任務"""
        # 檢查緩存
        cached_conversations = await self.shared_context.get_cached_data("conversations")
        if cached_conversations:
            self.logger.info("使用緩存的對話數據")
            return {"conversations": cached_conversations, "cached": True}
        
        # 檢查認證狀態
        auth_state = await self.shared_context.get_authentication_state("manus")
        if not auth_state:
            raise ValueError("未登錄，無法獲取對話")
        
        # 執行獲取對話邏輯（模擬實現）
        await asyncio.sleep(1.5)  # 模擬獲取時間
        
        conversations = [
            {"id": "conv_1", "title": "測試對話1", "last_message": "Hello"},
            {"id": "conv_2", "title": "測試對話2", "last_message": "World"}
        ]
        
        # 緩存結果
        await self.shared_context.cache_data("conversations", conversations, ttl=300)  # 5分鐘緩存
        
        return {"conversations": conversations, "count": len(conversations)}
    
    async def _execute_get_tasks(self, task_node: TaskNode) -> Dict[str, Any]:
        """執行獲取任務列表任務"""
        # 檢查緩存
        cached_tasks = await self.shared_context.get_cached_data("tasks")
        if cached_tasks:
            self.logger.info("使用緩存的任務數據")
            return {"tasks": cached_tasks, "cached": True}
        
        # 檢查認證狀態
        auth_state = await self.shared_context.get_authentication_state("manus")
        if not auth_state:
            raise ValueError("未登錄，無法獲取任務")
        
        # 執行獲取任務邏輯（模擬實現）
        await asyncio.sleep(2)  # 模擬獲取時間
        
        tasks = [
            {"id": "task_1", "title": "測試任務1", "status": "pending"},
            {"id": "task_2", "title": "測試任務2", "status": "completed"},
            {"id": "task_3", "title": "測試任務3", "status": "running"}
        ]
        
        # 緩存結果
        await self.shared_context.cache_data("tasks", tasks, ttl=600)  # 10分鐘緩存
        
        return {"tasks": tasks, "count": len(tasks)}
    
    async def _execute_download_files(self, task_node: TaskNode) -> Dict[str, Any]:
        """執行下載文件任務"""
        task_id = task_node.parameters.get("task_id", "")
        
        # 檢查認證狀態
        auth_state = await self.shared_context.get_authentication_state("manus")
        if not auth_state:
            raise ValueError("未登錄，無法下載文件")
        
        # 執行下載文件邏輯（模擬實現）
        await asyncio.sleep(3)  # 模擬下載時間
        
        files = [
            {"name": "document1.pdf", "size": 1024000, "path": "/tmp/document1.pdf"},
            {"name": "image1.png", "size": 512000, "path": "/tmp/image1.png"}
        ]
        
        return {
            "files": files,
            "count": len(files),
            "total_size": sum(f["size"] for f in files)
        }
    
    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """獲取執行狀態"""
        if execution_id in self.running_executions:
            execution = self.running_executions[execution_id]
            elapsed_time = (datetime.now() - execution['start_time']).total_seconds()
            
            return {
                "execution_id": execution_id,
                "chain_id": execution['chain'].chain_id,
                "status": execution['chain'].status.value,
                "elapsed_time": elapsed_time,
                "completed_tasks": len(execution['result'].node_results),
                "total_tasks": len(execution['chain'].nodes)
            }
        
        return None
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """取消執行"""
        if execution_id in self.running_executions:
            execution = self.running_executions[execution_id]
            execution['chain'].status = ChainStatus.CANCELLED
            
            # 取消所有待執行的任務
            for node in execution['chain'].nodes:
                if node.status == TaskStatus.PENDING:
                    node.status = TaskStatus.CANCELLED
            
            self.logger.info(f"執行已取消: {execution_id}")
            return True
        
        return False


class ReplayChainManager:
    """Replay鏈結管理器"""
    
    def __init__(self):
        self.chains = {}  # chain_id -> ReplayChain
        self.tasks = {}   # task_id -> TaskNode
        self.chain_generator = ChainGenerator()
        self.shared_context = SharedContext()
        self.executor = ChainExecutor(self.shared_context)
        self.logger = logging.getLogger(__name__)
    
    async def add_task(self, task_node: TaskNode) -> str:
        """添加任務"""
        self.tasks[task_node.task_id] = task_node
        self.logger.info(f"添加任務: {task_node.task_id} ({task_node.task_type})")
        return task_node.task_id
    
    async def create_chain_from_tasks(self, task_ids: List[str], chain_name: Optional[str] = None) -> Optional[str]:
        """從指定任務創建鏈結"""
        try:
            # 獲取任務節點
            tasks = []
            for task_id in task_ids:
                if task_id in self.tasks:
                    tasks.append(self.tasks[task_id])
                else:
                    self.logger.warning(f"任務不存在: {task_id}")
            
            if len(tasks) < 2:
                self.logger.warning("至少需要2個任務才能創建鏈結")
                return None
            
            # 生成鏈結
            chains = self.chain_generator.generate_chains(tasks)
            if not chains:
                self.logger.warning("無法生成鏈結")
                return None
            
            # 使用第一個生成的鏈結
            chain = chains[0]
            if chain_name:
                chain.chain_name = chain_name
            
            # 保存鏈結
            self.chains[chain.chain_id] = chain
            
            self.logger.info(f"創建鏈結成功: {chain.chain_id}")
            return chain.chain_id
            
        except Exception as e:
            self.logger.error(f"創建鏈結失敗: {e}")
            return None
    
    async def auto_generate_chains(self) -> List[str]:
        """自動生成鏈結"""
        try:
            # 獲取所有待處理的任務
            pending_tasks = [task for task in self.tasks.values() if task.status == TaskStatus.PENDING]
            
            if len(pending_tasks) < 2:
                return []
            
            # 生成鏈結
            chains = self.chain_generator.generate_chains(pending_tasks)
            
            # 保存鏈結
            chain_ids = []
            for chain in chains:
                self.chains[chain.chain_id] = chain
                chain_ids.append(chain.chain_id)
            
            self.logger.info(f"自動生成 {len(chain_ids)} 個鏈結")
            return chain_ids
            
        except Exception as e:
            self.logger.error(f"自動生成鏈結失敗: {e}")
            return []
    
    async def execute_chain(self, chain_id: str) -> Optional[ChainExecutionResult]:
        """執行鏈結"""
        if chain_id not in self.chains:
            self.logger.error(f"鏈結不存在: {chain_id}")
            return None
        
        chain = self.chains[chain_id]
        return await self.executor.execute_chain(chain)
    
    async def get_chain(self, chain_id: str) -> Optional[ReplayChain]:
        """獲取鏈結"""
        return self.chains.get(chain_id)
    
    async def list_chains(self) -> List[ReplayChain]:
        """列出所有鏈結"""
        return list(self.chains.values())
    
    async def delete_chain(self, chain_id: str) -> bool:
        """刪除鏈結"""
        if chain_id in self.chains:
            del self.chains[chain_id]
            self.logger.info(f"刪除鏈結: {chain_id}")
            return True
        return False
    
    async def get_task(self, task_id: str) -> Optional[TaskNode]:
        """獲取任務"""
        return self.tasks.get(task_id)
    
    async def list_tasks(self) -> List[TaskNode]:
        """列出所有任務"""
        return list(self.tasks.values())
    
    async def cleanup(self):
        """清理資源"""
        await self.shared_context.cleanup()
        self.logger.info("Replay鏈結管理器已清理")


# 使用示例
async def example_usage():
    """使用示例"""
    # 創建管理器
    manager = ReplayChainManager()
    
    try:
        # 創建一些測試任務
        task1 = TaskNode(
            task_id="task_001",
            task_type="manus_login",
            description="登錄Manus平台",
            parameters={"email": "test@example.com", "password": "password"},
            priority=9
        )
        
        task2 = TaskNode(
            task_id="task_002",
            task_type="send_message",
            description="發送測試消息",
            parameters={"message": "Hello, this is a test message"},
            dependencies=["task_001"],
            priority=7
        )
        
        task3 = TaskNode(
            task_id="task_003",
            task_type="get_conversations",
            description="獲取對話列表",
            parameters={},
            dependencies=["task_001"],
            priority=6
        )
        
        task4 = TaskNode(
            task_id="task_004",
            task_type="get_tasks",
            description="獲取任務列表",
            parameters={},
            dependencies=["task_001"],
            priority=5
        )
        
        # 添加任務
        await manager.add_task(task1)
        await manager.add_task(task2)
        await manager.add_task(task3)
        await manager.add_task(task4)
        
        # 自動生成鏈結
        chain_ids = await manager.auto_generate_chains()
        print(f"生成的鏈結: {chain_ids}")
        
        # 執行第一個鏈結
        if chain_ids:
            chain_id = chain_ids[0]
            result = await manager.execute_chain(chain_id)
            
            if result:
                print(f"鏈結執行結果:")
                print(f"  成功: {result.success}")
                print(f"  耗時: {result.total_duration:.2f}秒")
                print(f"  完成任務: {len(result.node_results)}")
                
                for task_result in result.node_results:
                    print(f"    任務 {task_result.task_id}: {'成功' if task_result.success else '失敗'}")
    
    finally:
        # 清理資源
        await manager.cleanup()


if __name__ == "__main__":
    # 配置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 運行示例
    asyncio.run(example_usage())

