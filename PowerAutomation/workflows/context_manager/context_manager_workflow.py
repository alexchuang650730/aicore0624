#!/usr/bin/env python3
"""
Context Manager Workflow
上下文管理工作流

統一協調所有上下文管理組件，為 AICore 系統提供完整的上下文管理服務
整合 RAG 引擎、LSP 適配器、對話管理器、路由器和壓縮器
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

# 導入所有組件
from .engines.universal_rag_engine import UniversalRAGEngine, create_universal_rag_engine
from .core.conversation_manager.dialogue_context_manager import DialogueContextManager, create_dialogue_context_manager
from .adapters.universal_lsp_adapter import UniversalLSPAdapter, create_universal_lsp_adapter
from .utils.context_router import ContextRouter, RoutingRequest, RequestType, RoutingStrategy, create_context_router
from .utils.context_compressor import ContextCompressor, ContextItem, ContentType, CompressionStrategy, create_context_compressor

logger = logging.getLogger(__name__)

class WorkflowStage(Enum):
    """工作流階段"""
    INITIALIZATION = "initialization"
    REQUEST_ANALYSIS = "request_analysis"
    CONTEXT_RETRIEVAL = "context_retrieval"
    CONTEXT_ENHANCEMENT = "context_enhancement"
    CONTEXT_COMPRESSION = "context_compression"
    RESPONSE_GENERATION = "response_generation"
    CLEANUP = "cleanup"

class ServiceType(Enum):
    """服務類型"""
    CODE_GENERATION = "code_generation"
    SMART_ROUTING = "smart_routing"
    TEST_FLOW = "test_flow"
    GENERAL_AI = "general_ai"

@dataclass
class WorkflowRequest:
    """工作流請求"""
    request_id: str
    service_type: ServiceType
    request_type: RequestType
    content: str
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    max_tokens: int = 4000
    quality_threshold: float = 0.7
    priority: int = 5
    timeout: float = 30.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class WorkflowResponse:
    """工作流響應"""
    request_id: str
    success: bool
    enhanced_context: List[ContextItem] = field(default_factory=list)
    compressed_context: List[ContextItem] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    stages_completed: List[WorkflowStage] = field(default_factory=list)
    error_message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ComponentStatus:
    """組件狀態"""
    component_name: str
    status: str
    initialized: bool
    last_health_check: datetime
    error_count: int = 0
    success_count: int = 0

class ContextManagerWorkflow:
    """上下文管理工作流"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = "Context Manager Workflow"
        self.version = "1.0.0"
        
        # 組件實例
        self.rag_engine: Optional[UniversalRAGEngine] = None
        self.dialogue_manager: Optional[DialogueContextManager] = None
        self.lsp_adapter: Optional[UniversalLSPAdapter] = None
        self.context_router: Optional[ContextRouter] = None
        self.context_compressor: Optional[ContextCompressor] = None
        
        # 組件狀態
        self.component_status = {}
        
        # 配置參數
        self.enable_caching = self.config.get("enable_caching", True)
        self.cache_ttl = self.config.get("cache_ttl", 300)
        self.max_concurrent_requests = self.config.get("max_concurrent_requests", 10)
        self.health_check_interval = self.config.get("health_check_interval", 60)
        
        # 請求管理
        self.active_requests = {}
        self.request_queue = asyncio.Queue()
        self.request_semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        # 緩存
        self.workflow_cache = {}
        
        # 統計信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_processing_time": 0.0,
            "service_type_distribution": {st.value: 0 for st in ServiceType},
            "request_type_distribution": {rt.value: 0 for rt in RequestType},
            "stage_performance": {stage.value: {"count": 0, "total_time": 0.0} for stage in WorkflowStage}
        }
        
        # 狀態管理
        self.initialized = False
        self.status = "initializing"
        self.startup_time = datetime.now()
        
        # 健康檢查任務
        self.health_check_task = None
        
        logger.info(f"Initializing {self.name} v{self.version}")
    
    async def initialize(self):
        """初始化工作流"""
        try:
            logger.info("🚀 Starting Context Manager Workflow initialization...")
            
            # 初始化所有組件
            await self._initialize_components()
            
            # 啟動健康檢查
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            
            self.initialized = True
            self.status = "ready"
            
            logger.info(f"🎉 {self.name} initialization completed successfully!")
            logger.info(f"📊 Initialized components: {list(self.component_status.keys())}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.name}: {e}")
            self.status = "error"
            return False
    
    async def _initialize_components(self):
        """初始化所有組件"""
        initialization_tasks = []
        
        # RAG 引擎
        rag_config = self.config.get("rag_engine", {})
        initialization_tasks.append(self._initialize_rag_engine(rag_config))
        
        # 對話管理器
        dialogue_config = self.config.get("dialogue_manager", {})
        initialization_tasks.append(self._initialize_dialogue_manager(dialogue_config))
        
        # LSP 適配器
        lsp_config = self.config.get("lsp_adapter", {})
        initialization_tasks.append(self._initialize_lsp_adapter(lsp_config))
        
        # 上下文路由器
        router_config = self.config.get("context_router", {})
        initialization_tasks.append(self._initialize_context_router(router_config))
        
        # 上下文壓縮器
        compressor_config = self.config.get("context_compressor", {})
        initialization_tasks.append(self._initialize_context_compressor(compressor_config))
        
        # 並行初始化
        results = await asyncio.gather(*initialization_tasks, return_exceptions=True)
        
        # 檢查初始化結果
        component_names = ["RAG Engine", "Dialogue Manager", "LSP Adapter", "Context Router", "Context Compressor"]
        for i, (name, result) in enumerate(zip(component_names, results)):
            if isinstance(result, Exception):
                logger.error(f"❌ Failed to initialize {name}: {result}")
                self.component_status[name.lower().replace(" ", "_")] = ComponentStatus(
                    component_name=name,
                    status="error",
                    initialized=False,
                    last_health_check=datetime.now(),
                    error_count=1
                )
            else:
                logger.info(f"✅ {name} initialized successfully")
                self.component_status[name.lower().replace(" ", "_")] = ComponentStatus(
                    component_name=name,
                    status="ready",
                    initialized=True,
                    last_health_check=datetime.now(),
                    success_count=1
                )
    
    async def _initialize_rag_engine(self, config: Dict[str, Any]):
        """初始化 RAG 引擎"""
        self.rag_engine = await create_universal_rag_engine(config)
        return self.rag_engine
    
    async def _initialize_dialogue_manager(self, config: Dict[str, Any]):
        """初始化對話管理器"""
        self.dialogue_manager = await create_dialogue_context_manager(config)
        return self.dialogue_manager
    
    async def _initialize_lsp_adapter(self, config: Dict[str, Any]):
        """初始化 LSP 適配器"""
        self.lsp_adapter = await create_universal_lsp_adapter(config)
        return self.lsp_adapter
    
    async def _initialize_context_router(self, config: Dict[str, Any]):
        """初始化上下文路由器"""
        self.context_router = await create_context_router(config)
        return self.context_router
    
    async def _initialize_context_compressor(self, config: Dict[str, Any]):
        """初始化上下文壓縮器"""
        self.context_compressor = await create_context_compressor(config)
        return self.context_compressor
    
    async def process_request(self, request: WorkflowRequest) -> WorkflowResponse:
        """處理工作流請求"""
        if not self.initialized:
            raise RuntimeError("Context Manager Workflow not initialized")
        
        async with self.request_semaphore:
            return await self._process_request_internal(request)
    
    async def _process_request_internal(self, request: WorkflowRequest) -> WorkflowResponse:
        """內部請求處理邏輯"""
        start_time = time.time()
        request_id = request.request_id
        
        # 更新統計
        self.stats["total_requests"] += 1
        self.stats["service_type_distribution"][request.service_type.value] += 1
        self.stats["request_type_distribution"][request.request_type.value] += 1
        
        # 記錄活動請求
        self.active_requests[request_id] = {
            "request": request,
            "start_time": start_time,
            "current_stage": WorkflowStage.INITIALIZATION
        }
        
        response = WorkflowResponse(request_id=request_id, success=False)
        
        try:
            logger.info(f"🔄 Processing request {request_id} ({request.service_type.value}/{request.request_type.value})")
            
            # 檢查緩存
            cache_key = self._generate_cache_key(request)
            if self.enable_caching and cache_key in self.workflow_cache:
                cached_response = self.workflow_cache[cache_key]
                if datetime.now() - cached_response.timestamp < timedelta(seconds=self.cache_ttl):
                    logger.info(f"📋 Cache hit for request {request_id}")
                    return cached_response
            
            # 階段1：請求分析
            await self._execute_stage(WorkflowStage.REQUEST_ANALYSIS, request_id)
            routing_request = await self._analyze_request(request)
            response.stages_completed.append(WorkflowStage.REQUEST_ANALYSIS)
            
            # 階段2：上下文檢索
            await self._execute_stage(WorkflowStage.CONTEXT_RETRIEVAL, request_id)
            context_items = await self._retrieve_context(request, routing_request)
            response.stages_completed.append(WorkflowStage.CONTEXT_RETRIEVAL)
            
            # 階段3：上下文增強
            await self._execute_stage(WorkflowStage.CONTEXT_ENHANCEMENT, request_id)
            enhanced_items = await self._enhance_context(request, context_items)
            response.enhanced_context = enhanced_items
            response.stages_completed.append(WorkflowStage.CONTEXT_ENHANCEMENT)
            
            # 階段4：上下文壓縮
            await self._execute_stage(WorkflowStage.CONTEXT_COMPRESSION, request_id)
            compressed_items = await self._compress_context(request, enhanced_items)
            response.compressed_context = compressed_items
            response.stages_completed.append(WorkflowStage.CONTEXT_COMPRESSION)
            
            # 設置成功響應
            response.success = True
            response.metadata = {
                "original_context_items": len(context_items),
                "enhanced_context_items": len(enhanced_items),
                "compressed_context_items": len(compressed_items),
                "total_tokens": sum(item.token_count for item in compressed_items),
                "processing_stages": len(response.stages_completed)
            }
            
            # 更新統計
            self.stats["successful_requests"] += 1
            
            # 緩存響應
            if self.enable_caching:
                self.workflow_cache[cache_key] = response
            
            logger.info(f"✅ Request {request_id} processed successfully in {time.time() - start_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Error processing request {request_id}: {e}")
            response.error_message = str(e)
            self.stats["failed_requests"] += 1
        
        finally:
            # 清理活動請求
            if request_id in self.active_requests:
                del self.active_requests[request_id]
            
            # 更新處理時間統計
            processing_time = time.time() - start_time
            response.processing_time = processing_time
            
            self.stats["average_processing_time"] = (
                (self.stats["average_processing_time"] * (self.stats["total_requests"] - 1) + processing_time)
                / self.stats["total_requests"]
            )
        
        return response
    
    async def _execute_stage(self, stage: WorkflowStage, request_id: str):
        """執行工作流階段"""
        stage_start = time.time()
        
        if request_id in self.active_requests:
            self.active_requests[request_id]["current_stage"] = stage
        
        # 記錄階段性能
        stage_time = time.time() - stage_start
        stage_stats = self.stats["stage_performance"][stage.value]
        stage_stats["count"] += 1
        stage_stats["total_time"] += stage_time
        
        logger.debug(f"Stage {stage.value} completed for request {request_id} in {stage_time:.3f}s")
    
    async def _analyze_request(self, request: WorkflowRequest) -> RoutingRequest:
        """分析請求"""
        routing_request = RoutingRequest(
            request_id=request.request_id,
            request_type=request.request_type,
            content=request.content,
            context=request.context,
            metadata=request.metadata,
            priority=request.priority,
            max_processing_time=request.timeout
        )
        
        return routing_request
    
    async def _retrieve_context(self, request: WorkflowRequest, 
                              routing_request: RoutingRequest) -> List[ContextItem]:
        """檢索上下文"""
        context_items = []
        
        try:
            # 使用路由器決定檢索策略
            if self.context_router:
                routing_decision = await self.context_router.route_request(routing_request)
                
                # 根據路由決策檢索上下文
                for component_type, component_id in routing_decision.selected_components:
                    if component_id == "universal_rag" and self.rag_engine:
                        # RAG 檢索
                        rag_results = await self.rag_engine.search(
                            query=request.content,
                            search_type="hybrid",
                            max_results=10
                        )
                        
                        for result in rag_results:
                            context_item = ContextItem(
                                item_id=f"rag_{result.get('id', uuid.uuid4().hex[:8])}",
                                content=result.get("content", ""),
                                content_type=ContentType.REFERENCE,
                                relevance_score=result.get("score", 0.5),
                                metadata={"source": "rag_engine", "result": result}
                            )
                            context_items.append(context_item)
                    
                    elif component_id == "universal_lsp" and self.lsp_adapter:
                        # LSP 檢索
                        if "project_path" in request.context:
                            project_context = await self.lsp_adapter.analyze_project(
                                request.context["project_path"]
                            )
                            
                            lsp_item = ContextItem(
                                item_id=f"lsp_project_context",
                                content=json.dumps(project_context.__dict__, default=str),
                                content_type=ContentType.STRUCTURE,
                                importance_score=0.8,
                                metadata={"source": "lsp_adapter", "project_path": request.context["project_path"]}
                            )
                            context_items.append(lsp_item)
                    
                    elif component_id == "dialogue_context" and self.dialogue_manager:
                        # 對話上下文檢索
                        if "session_id" in request.context:
                            dialogue_context = await self.dialogue_manager.get_session_context(
                                request.context["session_id"]
                            )
                            
                            if dialogue_context:
                                dialogue_item = ContextItem(
                                    item_id=f"dialogue_context",
                                    content=json.dumps(dialogue_context, default=str),
                                    content_type=ContentType.CONVERSATION,
                                    importance_score=0.7,
                                    metadata={"source": "dialogue_manager", "session_id": request.context["session_id"]}
                                )
                                context_items.append(dialogue_item)
            
            logger.info(f"Retrieved {len(context_items)} context items for request {request.request_id}")
            
        except Exception as e:
            logger.error(f"Error retrieving context for request {request.request_id}: {e}")
        
        return context_items
    
    async def _enhance_context(self, request: WorkflowRequest, 
                             context_items: List[ContextItem]) -> List[ContextItem]:
        """增強上下文"""
        enhanced_items = context_items.copy()
        
        try:
            # 計算重要性分數
            if self.context_compressor:
                for item in enhanced_items:
                    if item.importance_score == 0.5:  # 默認值
                        item.importance_score = await self.context_compressor.importance_calculator.calculate_importance(
                            item, enhanced_items
                        )
            
            # 添加請求特定的上下文項目
            request_item = ContextItem(
                item_id="current_request",
                content=request.content,
                content_type=ContentType.CONVERSATION,
                importance_score=1.0,
                relevance_score=1.0,
                metadata={"source": "current_request", "service_type": request.service_type.value}
            )
            enhanced_items.insert(0, request_item)  # 放在最前面
            
            logger.info(f"Enhanced context with {len(enhanced_items)} items for request {request.request_id}")
            
        except Exception as e:
            logger.error(f"Error enhancing context for request {request.request_id}: {e}")
        
        return enhanced_items
    
    async def _compress_context(self, request: WorkflowRequest, 
                              context_items: List[ContextItem]) -> List[ContextItem]:
        """壓縮上下文"""
        if not self.context_compressor:
            return context_items
        
        try:
            # 根據服務類型選擇壓縮策略
            strategy = CompressionStrategy.HYBRID
            if request.service_type == ServiceType.CODE_GENERATION:
                strategy = CompressionStrategy.IMPORTANCE_BASED
            elif request.service_type == ServiceType.SMART_ROUTING:
                strategy = CompressionStrategy.SEMANTIC_CLUSTERING
            
            # 執行壓縮
            compression_result = await self.context_compressor.compress_context(
                context_items, request.max_tokens, strategy
            )
            
            logger.info(f"Compressed context from {compression_result.original_token_count} to {compression_result.compressed_token_count} tokens (ratio: {compression_result.compression_ratio:.2f})")
            
            return compression_result.compressed_items
            
        except Exception as e:
            logger.error(f"Error compressing context for request {request.request_id}: {e}")
            return context_items
    
    def _generate_cache_key(self, request: WorkflowRequest) -> str:
        """生成緩存鍵"""
        import hashlib
        key_data = {
            "service_type": request.service_type.value,
            "request_type": request.request_type.value,
            "content_hash": hashlib.md5(request.content.encode()).hexdigest()[:16],
            "max_tokens": request.max_tokens
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    async def _health_check_loop(self):
        """健康檢查循環"""
        while self.status != "shutdown":
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _perform_health_check(self):
        """執行健康檢查"""
        current_time = datetime.now()
        
        # 檢查各組件狀態
        components = [
            ("rag_engine", self.rag_engine),
            ("dialogue_manager", self.dialogue_manager),
            ("lsp_adapter", self.lsp_adapter),
            ("context_router", self.context_router),
            ("context_compressor", self.context_compressor)
        ]
        
        for name, component in components:
            if component and hasattr(component, 'get_status'):
                try:
                    status = component.get_status()
                    if name in self.component_status:
                        self.component_status[name].status = status.get("status", "unknown")
                        self.component_status[name].last_health_check = current_time
                        
                        if status.get("status") == "ready":
                            self.component_status[name].success_count += 1
                        else:
                            self.component_status[name].error_count += 1
                            
                except Exception as e:
                    logger.warning(f"Health check failed for {name}: {e}")
                    if name in self.component_status:
                        self.component_status[name].error_count += 1
        
        # 清理過期緩存
        if self.enable_caching:
            await self._cleanup_cache()
    
    async def _cleanup_cache(self):
        """清理過期緩存"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, response in self.workflow_cache.items():
            if current_time - response.timestamp > timedelta(seconds=self.cache_ttl):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.workflow_cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_status(self) -> Dict[str, Any]:
        """獲取工作流狀態"""
        uptime = datetime.now() - self.startup_time
        
        return {
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "initialized": self.initialized,
            "uptime_seconds": uptime.total_seconds(),
            "stats": dict(self.stats),
            "component_status": {
                name: {
                    "component_name": status.component_name,
                    "status": status.status,
                    "initialized": status.initialized,
                    "error_count": status.error_count,
                    "success_count": status.success_count,
                    "last_health_check": status.last_health_check.isoformat()
                }
                for name, status in self.component_status.items()
            },
            "active_requests": len(self.active_requests),
            "cache_stats": {
                "cache_size": len(self.workflow_cache),
                "cache_enabled": self.enable_caching
            },
            "config": {
                "max_concurrent_requests": self.max_concurrent_requests,
                "cache_ttl": self.cache_ttl,
                "health_check_interval": self.health_check_interval
            }
        }
    
    async def shutdown(self):
        """關閉工作流"""
        logger.info("🔄 Shutting down Context Manager Workflow...")
        
        self.status = "shutting_down"
        
        # 取消健康檢查任務
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        # 關閉所有組件
        shutdown_tasks = []
        
        if self.rag_engine:
            shutdown_tasks.append(self.rag_engine.shutdown())
        
        if self.dialogue_manager:
            shutdown_tasks.append(self.dialogue_manager.shutdown())
        
        if self.lsp_adapter:
            shutdown_tasks.append(self.lsp_adapter.shutdown())
        
        if self.context_router:
            shutdown_tasks.append(self.context_router.shutdown())
        
        if self.context_compressor:
            shutdown_tasks.append(self.context_compressor.shutdown())
        
        # 等待所有組件關閉
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        # 清理緩存和狀態
        self.workflow_cache.clear()
        self.active_requests.clear()
        self.component_status.clear()
        
        self.status = "shutdown"
        logger.info("✅ Context Manager Workflow shut down successfully")

# 工廠函數
async def create_context_manager_workflow(config: Dict[str, Any] = None) -> ContextManagerWorkflow:
    """創建並初始化上下文管理工作流"""
    workflow = ContextManagerWorkflow(config)
    await workflow.initialize()
    return workflow

# MCP 服務器接口
class ContextManagerMCPServer:
    """Context Manager MCP 服務器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.workflow: Optional[ContextManagerWorkflow] = None
        self.server_info = {
            "name": "context-manager-mcp",
            "version": "1.0.0",
            "description": "AICore Context Manager MCP Server"
        }
    
    async def initialize(self):
        """初始化 MCP 服務器"""
        self.workflow = await create_context_manager_workflow(self.config)
        return True
    
    async def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理 MCP 請求"""
        if not self.workflow:
            raise RuntimeError("Context Manager MCP Server not initialized")
        
        if method == "context_manager/process":
            # 處理上下文管理請求
            request = WorkflowRequest(
                request_id=params.get("request_id", str(uuid.uuid4())),
                service_type=ServiceType(params.get("service_type", "general_ai")),
                request_type=RequestType(params.get("request_type", "general_query")),
                content=params.get("content", ""),
                context=params.get("context", {}),
                metadata=params.get("metadata", {}),
                max_tokens=params.get("max_tokens", 4000),
                priority=params.get("priority", 5)
            )
            
            response = await self.workflow.process_request(request)
            
            return {
                "request_id": response.request_id,
                "success": response.success,
                "enhanced_context": [item.to_dict() for item in response.enhanced_context],
                "compressed_context": [item.to_dict() for item in response.compressed_context],
                "metadata": response.metadata,
                "processing_time": response.processing_time,
                "error_message": response.error_message
            }
        
        elif method == "context_manager/status":
            # 獲取狀態
            return self.workflow.get_status()
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def shutdown(self):
        """關閉 MCP 服務器"""
        if self.workflow:
            await self.workflow.shutdown()

if __name__ == "__main__":
    # 測試代碼
    async def test_context_manager_workflow():
        config = {
            "enable_caching": True,
            "cache_ttl": 300,
            "max_concurrent_requests": 5,
            "rag_engine": {
                "storage_path": "./test_rag_storage",
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            },
            "dialogue_manager": {
                "storage_path": "./test_dialogue_storage",
                "max_sessions": 100
            }
        }
        
        # 創建工作流
        workflow = await create_context_manager_workflow(config)
        
        # 創建測試請求
        request = WorkflowRequest(
            request_id="test-workflow-001",
            service_type=ServiceType.CODE_GENERATION,
            request_type=RequestType.CODE_GENERATION,
            content="Create a Python function to calculate prime numbers",
            context={"project_path": "/path/to/project"},
            max_tokens=2000,
            priority=7
        )
        
        # 處理請求
        response = await workflow.process_request(request)
        
        print(f"Workflow Response:")
        print(f"  Success: {response.success}")
        print(f"  Enhanced context items: {len(response.enhanced_context)}")
        print(f"  Compressed context items: {len(response.compressed_context)}")
        print(f"  Processing time: {response.processing_time:.2f}s")
        print(f"  Stages completed: {[stage.value for stage in response.stages_completed]}")
        
        if response.compressed_context:
            total_tokens = sum(item.token_count for item in response.compressed_context)
            print(f"  Total compressed tokens: {total_tokens}")
        
        # 獲取狀態
        status = workflow.get_status()
        print(f"\nWorkflow Status:")
        print(f"  Status: {status['status']}")
        print(f"  Total requests: {status['stats']['total_requests']}")
        print(f"  Success rate: {status['stats']['successful_requests']}/{status['stats']['total_requests']}")
        print(f"  Active requests: {status['active_requests']}")
        print(f"  Component status: {list(status['component_status'].keys())}")
        
        # 關閉工作流
        await workflow.shutdown()
    
    asyncio.run(test_context_manager_workflow())

