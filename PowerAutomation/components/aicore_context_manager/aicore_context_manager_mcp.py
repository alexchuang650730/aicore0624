#!/usr/bin/env python3
"""
AICore Context Manager MCP
AICore 通用上下文管理 MCP

為整個 AICore 系統提供統一的上下文管理服務
支持多組件協作、智能上下文路由和動態上下文優化
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

# 導入子模組
from .rag_engine.universal_rag_engine import UniversalRAGEngine
from .conversation_manager.dialogue_context_manager import DialogueContextManager
from .lsp_integration.universal_lsp_adapter import UniversalLSPAdapter
from .utils.context_router import ContextRouter
from .utils.context_compressor import ContextCompressor

logger = logging.getLogger(__name__)

class ServiceType(Enum):
    """服務類型"""
    SMART_ROUTING = "smart_routing"
    CODE_GENERATION = "code_generation"
    TEST_FLOW = "test_flow"
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    DOCUMENTATION = "documentation"
    GENERAL = "general"

class ContextScope(Enum):
    """上下文範圍"""
    GLOBAL = "global"          # 全局上下文
    SYSTEM = "system"          # 系統級上下文
    SERVICE = "service"        # 服務級上下文
    SESSION = "session"        # 會話級上下文
    REQUEST = "request"        # 請求級上下文

@dataclass
class ContextRequest:
    """上下文請求"""
    request_id: str
    service_type: ServiceType
    scope: ContextScope
    query: str
    max_tokens: int = 8000
    include_history: bool = True
    include_project_context: bool = True
    session_id: Optional[str] = None
    project_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ContextResponse:
    """上下文響應"""
    request_id: str
    success: bool
    context_data: Dict[str, Any] = field(default_factory=dict)
    token_count: int = 0
    quality_score: float = 0.0
    sources: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

class AICoreContextManagerMCP:
    """AICore 上下文管理器 MCP"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = "AICore Context Manager MCP"
        self.version = "1.0.0"
        self.description = "Universal context management service for AICore system"
        
        # 初始化子組件
        self.rag_engine = None
        self.dialogue_manager = None
        self.lsp_adapter = None
        self.context_router = None
        self.context_compressor = None
        
        # 狀態管理
        self.initialized = False
        self.status = "initializing"
        
        # 服務註冊
        self.registered_services = {}
        self.active_sessions = {}
        
        # 性能統計
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_response_time": 0.0,
            "service_usage": {service.value: 0 for service in ServiceType},
            "scope_usage": {scope.value: 0 for scope in ContextScope},
            "total_tokens_served": 0
        }
        
        # 配置參數
        self.max_concurrent_requests = self.config.get("max_concurrent_requests", 100)
        self.default_token_limit = self.config.get("default_token_limit", 8000)
        self.session_timeout = self.config.get("session_timeout", 3600)
        
        logger.info(f"Initializing {self.name} v{self.version}")
    
    async def initialize(self) -> bool:
        """初始化 MCP 組件"""
        try:
            logger.info("Initializing AICore Context Manager MCP components...")
            
            # 初始化通用 RAG 引擎
            rag_config = self.config.get("rag_engine", {})
            self.rag_engine = UniversalRAGEngine(rag_config)
            await self.rag_engine.initialize()
            logger.info("✅ Universal RAG Engine initialized")
            
            # 初始化對話上下文管理器
            dialogue_config = self.config.get("dialogue_manager", {})
            self.dialogue_manager = DialogueContextManager(dialogue_config)
            await self.dialogue_manager.initialize()
            logger.info("✅ Dialogue Context Manager initialized")
            
            # 初始化通用 LSP 適配器
            lsp_config = self.config.get("lsp_adapter", {})
            self.lsp_adapter = UniversalLSPAdapter(lsp_config)
            await self.lsp_adapter.initialize()
            logger.info("✅ Universal LSP Adapter initialized")
            
            # 初始化上下文路由器
            router_config = self.config.get("context_router", {})
            self.context_router = ContextRouter(router_config)
            await self.context_router.initialize()
            logger.info("✅ Context Router initialized")
            
            # 初始化上下文壓縮器
            compressor_config = self.config.get("context_compressor", {})
            self.context_compressor = ContextCompressor(compressor_config)
            await self.context_compressor.initialize()
            logger.info("✅ Context Compressor initialized")
            
            self.initialized = True
            self.status = "ready"
            logger.info(f"🎉 {self.name} initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.name}: {e}")
            self.status = "error"
            return False
    
    async def register_service(self, service_name: str, service_type: ServiceType, 
                             service_config: Dict[str, Any] = None) -> bool:
        """註冊服務"""
        try:
            service_info = {
                "name": service_name,
                "type": service_type,
                "config": service_config or {},
                "registered_at": datetime.now(),
                "active": True
            }
            
            self.registered_services[service_name] = service_info
            logger.info(f"Service '{service_name}' registered as {service_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service '{service_name}': {e}")
            return False
    
    async def get_context(self, request: ContextRequest) -> ContextResponse:
        """獲取上下文"""
        if not self.initialized:
            return ContextResponse(
                request_id=request.request_id,
                success=False,
                error="Context Manager not initialized"
            )
        
        start_time = time.time()
        self.stats["total_requests"] += 1
        self.stats["service_usage"][request.service_type.value] += 1
        self.stats["scope_usage"][request.scope.value] += 1
        
        try:
            logger.info(f"Processing context request {request.request_id} for {request.service_type.value}")
            
            # 路由請求到合適的處理器
            context_data = await self.context_router.route_request(request)
            
            # 根據範圍構建上下文
            if request.scope == ContextScope.GLOBAL:
                context_data = await self._build_global_context(request, context_data)
            elif request.scope == ContextScope.SYSTEM:
                context_data = await self._build_system_context(request, context_data)
            elif request.scope == ContextScope.SERVICE:
                context_data = await self._build_service_context(request, context_data)
            elif request.scope == ContextScope.SESSION:
                context_data = await self._build_session_context(request, context_data)
            elif request.scope == ContextScope.REQUEST:
                context_data = await self._build_request_context(request, context_data)
            
            # 壓縮上下文（如果需要）
            if context_data.get("token_count", 0) > request.max_tokens:
                context_data = await self.context_compressor.compress(
                    context_data, request.max_tokens
                )
            
            # 計算質量分數
            quality_score = await self._calculate_context_quality(context_data, request)
            
            # 構建響應
            response = ContextResponse(
                request_id=request.request_id,
                success=True,
                context_data=context_data,
                token_count=context_data.get("token_count", 0),
                quality_score=quality_score,
                sources=context_data.get("sources", []),
                processing_time=time.time() - start_time,
                metadata={
                    "service_type": request.service_type.value,
                    "scope": request.scope.value,
                    "compressed": context_data.get("compressed", False)
                }
            )
            
            # 更新統計
            self.stats["successful_requests"] += 1
            self.stats["total_tokens_served"] += response.token_count
            self.stats["average_response_time"] = (
                (self.stats["average_response_time"] * (self.stats["total_requests"] - 1) + response.processing_time)
                / self.stats["total_requests"]
            )
            
            logger.info(f"✅ Context request {request.request_id} completed in {response.processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error processing context request {request.request_id}: {e}")
            return ContextResponse(
                request_id=request.request_id,
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    async def _build_global_context(self, request: ContextRequest, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """構建全局上下文"""
        logger.debug("Building global context")
        
        # 添加系統級信息
        global_context = {
            **base_context,
            "system_info": {
                "aicore_version": "0.6.24",
                "available_services": list(self.registered_services.keys()),
                "system_capabilities": [
                    "smart_routing",
                    "code_generation", 
                    "test_automation",
                    "requirement_analysis"
                ]
            }
        }
        
        # 添加全局知識庫信息
        if self.rag_engine:
            global_knowledge = await self.rag_engine.get_global_knowledge(request.query)
            global_context["global_knowledge"] = global_knowledge
        
        return global_context
    
    async def _build_system_context(self, request: ContextRequest, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """構建系統級上下文"""
        logger.debug("Building system context")
        
        system_context = {
            **base_context,
            "system_state": {
                "active_services": len([s for s in self.registered_services.values() if s["active"]]),
                "active_sessions": len(self.active_sessions),
                "system_load": await self._get_system_load(),
                "resource_usage": await self._get_resource_usage()
            }
        }
        
        return system_context
    
    async def _build_service_context(self, request: ContextRequest, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """構建服務級上下文"""
        logger.debug(f"Building service context for {request.service_type.value}")
        
        service_context = {**base_context}
        
        # 根據服務類型添加特定上下文
        if request.service_type == ServiceType.CODE_GENERATION:
            service_context.update(await self._get_code_generation_context(request))
        elif request.service_type == ServiceType.SMART_ROUTING:
            service_context.update(await self._get_smart_routing_context(request))
        elif request.service_type == ServiceType.TEST_FLOW:
            service_context.update(await self._get_test_flow_context(request))
        elif request.service_type == ServiceType.REQUIREMENT_ANALYSIS:
            service_context.update(await self._get_requirement_analysis_context(request))
        
        return service_context
    
    async def _build_session_context(self, request: ContextRequest, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """構建會話級上下文"""
        logger.debug(f"Building session context for session {request.session_id}")
        
        session_context = {**base_context}
        
        if request.session_id and request.include_history:
            # 獲取會話歷史
            session_history = await self.dialogue_manager.get_session_history(
                request.session_id, limit=10
            )
            session_context["session_history"] = session_history
            
            # 獲取會話摘要
            session_summary = await self.dialogue_manager.get_session_summary(request.session_id)
            session_context["session_summary"] = session_summary
        
        return session_context
    
    async def _build_request_context(self, request: ContextRequest, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """構建請求級上下文"""
        logger.debug("Building request context")
        
        request_context = {
            **base_context,
            "request_info": {
                "query": request.query,
                "timestamp": request.timestamp.isoformat(),
                "service_type": request.service_type.value,
                "metadata": request.metadata
            }
        }
        
        # 添加項目上下文（如果提供）
        if request.project_path and request.include_project_context:
            project_context = await self.lsp_adapter.get_project_context(request.project_path)
            request_context["project_context"] = project_context
        
        return request_context
    
    async def _get_code_generation_context(self, request: ContextRequest) -> Dict[str, Any]:
        """獲取代碼生成上下文"""
        context = {}
        
        # 獲取代碼相關的 RAG 信息
        if self.rag_engine:
            code_knowledge = await self.rag_engine.search_code_knowledge(request.query)
            context["code_knowledge"] = code_knowledge
        
        # 獲取編程最佳實踐
        context["best_practices"] = await self._get_coding_best_practices(request.query)
        
        return context
    
    async def _get_smart_routing_context(self, request: ContextRequest) -> Dict[str, Any]:
        """獲取智能路由上下文"""
        context = {}
        
        # 獲取路由歷史
        context["routing_history"] = await self._get_routing_history(request.session_id)
        
        # 獲取可用服務信息
        context["available_services"] = [
            {
                "name": name,
                "type": info["type"].value,
                "active": info["active"]
            }
            for name, info in self.registered_services.items()
        ]
        
        return context
    
    async def _get_test_flow_context(self, request: ContextRequest) -> Dict[str, Any]:
        """獲取測試流程上下文"""
        context = {}
        
        # 獲取測試相關知識
        if self.rag_engine:
            test_knowledge = await self.rag_engine.search_test_knowledge(request.query)
            context["test_knowledge"] = test_knowledge
        
        # 獲取測試模板
        context["test_templates"] = await self._get_test_templates()
        
        return context
    
    async def _get_requirement_analysis_context(self, request: ContextRequest) -> Dict[str, Any]:
        """獲取需求分析上下文"""
        context = {}
        
        # 獲取需求分析模板
        context["analysis_templates"] = await self._get_analysis_templates()
        
        # 獲取相關項目經驗
        if self.rag_engine:
            project_experience = await self.rag_engine.search_project_experience(request.query)
            context["project_experience"] = project_experience
        
        return context
    
    async def _calculate_context_quality(self, context_data: Dict[str, Any], request: ContextRequest) -> float:
        """計算上下文質量分數"""
        quality_factors = []
        
        # 完整性評分
        expected_keys = ["request_info"]
        if request.scope in [ContextScope.SESSION, ContextScope.SERVICE]:
            expected_keys.extend(["session_history", "service_context"])
        
        completeness = sum(1 for key in expected_keys if key in context_data) / len(expected_keys)
        quality_factors.append(completeness)
        
        # 相關性評分
        relevance = await self._calculate_relevance(context_data, request.query)
        quality_factors.append(relevance)
        
        # 新鮮度評分
        freshness = await self._calculate_freshness(context_data)
        quality_factors.append(freshness)
        
        # 多樣性評分
        diversity = await self._calculate_diversity(context_data)
        quality_factors.append(diversity)
        
        return sum(quality_factors) / len(quality_factors)
    
    async def _calculate_relevance(self, context_data: Dict[str, Any], query: str) -> float:
        """計算相關性"""
        # 簡化的相關性計算
        query_words = set(query.lower().split())
        context_text = json.dumps(context_data).lower()
        context_words = set(context_text.split())
        
        if not query_words:
            return 0.5
        
        intersection = query_words.intersection(context_words)
        return len(intersection) / len(query_words)
    
    async def _calculate_freshness(self, context_data: Dict[str, Any]) -> float:
        """計算新鮮度"""
        # 檢查時間戳信息
        now = datetime.now()
        timestamps = []
        
        def extract_timestamps(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if 'timestamp' in key.lower() or 'time' in key.lower():
                        try:
                            if isinstance(value, str):
                                timestamps.append(datetime.fromisoformat(value.replace('Z', '+00:00')))
                        except:
                            pass
                    elif isinstance(value, (dict, list)):
                        extract_timestamps(value)
            elif isinstance(data, list):
                for item in data:
                    extract_timestamps(item)
        
        extract_timestamps(context_data)
        
        if not timestamps:
            return 0.7  # 默認新鮮度
        
        # 計算平均時間差
        avg_age = sum((now - ts).total_seconds() for ts in timestamps) / len(timestamps)
        
        # 轉換為新鮮度分數（24小時內為1.0，線性衰減）
        hours_old = avg_age / 3600
        freshness = max(0.1, 1.0 - (hours_old / 24))
        
        return freshness
    
    async def _calculate_diversity(self, context_data: Dict[str, Any]) -> float:
        """計算多樣性"""
        # 計算上下文數據的多樣性
        unique_keys = set()
        
        def count_keys(data, prefix=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    full_key = f"{prefix}.{key}" if prefix else key
                    unique_keys.add(full_key)
                    if isinstance(value, (dict, list)):
                        count_keys(value, full_key)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    if isinstance(item, (dict, list)):
                        count_keys(item, f"{prefix}[{i}]")
        
        count_keys(context_data)
        
        # 基於唯一鍵的數量計算多樣性
        diversity = min(len(unique_keys) / 20, 1.0)  # 20個鍵為滿分
        return diversity
    
    async def _get_system_load(self) -> float:
        """獲取系統負載"""
        # 簡化的系統負載計算
        active_requests = self.stats["total_requests"] - self.stats["successful_requests"]
        load = min(active_requests / self.max_concurrent_requests, 1.0)
        return load
    
    async def _get_resource_usage(self) -> Dict[str, float]:
        """獲取資源使用情況"""
        return {
            "memory_usage": 0.6,  # 模擬值
            "cpu_usage": 0.4,
            "disk_usage": 0.3,
            "network_usage": 0.2
        }
    
    async def _get_coding_best_practices(self, query: str) -> List[str]:
        """獲取編程最佳實踐"""
        practices = [
            "Follow PEP 8 style guide for Python",
            "Write comprehensive docstrings",
            "Use meaningful variable names",
            "Implement proper error handling",
            "Write unit tests for functions",
            "Keep functions small and focused",
            "Use type hints for better code clarity"
        ]
        
        # 根據查詢過濾相關實踐
        relevant_practices = []
        query_lower = query.lower()
        
        for practice in practices:
            if any(word in practice.lower() for word in query_lower.split()):
                relevant_practices.append(practice)
        
        return relevant_practices[:5]  # 返回最多5個相關實踐
    
    async def _get_routing_history(self, session_id: Optional[str]) -> List[Dict[str, Any]]:
        """獲取路由歷史"""
        if not session_id:
            return []
        
        # 模擬路由歷史
        return [
            {
                "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "service": "code_generation",
                "query": "create a REST API",
                "success": True
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(),
                "service": "smart_routing",
                "query": "analyze requirements",
                "success": True
            }
        ]
    
    async def _get_test_templates(self) -> List[Dict[str, Any]]:
        """獲取測試模板"""
        return [
            {
                "name": "Unit Test Template",
                "language": "python",
                "framework": "pytest",
                "template": "def test_function():\n    assert True"
            },
            {
                "name": "Integration Test Template", 
                "language": "python",
                "framework": "pytest",
                "template": "def test_integration():\n    # Setup\n    # Execute\n    # Assert"
            }
        ]
    
    async def _get_analysis_templates(self) -> List[Dict[str, Any]]:
        """獲取分析模板"""
        return [
            {
                "name": "Requirement Analysis Template",
                "sections": ["Overview", "Functional Requirements", "Non-functional Requirements", "Constraints"],
                "format": "markdown"
            },
            {
                "name": "Technical Specification Template",
                "sections": ["Architecture", "Components", "APIs", "Database Design"],
                "format": "markdown"
            }
        ]
    
    async def create_session(self, service_type: ServiceType, metadata: Dict[str, Any] = None) -> str:
        """創建新會話"""
        session_id = f"session_{service_type.value}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        session_info = {
            "session_id": session_id,
            "service_type": service_type,
            "created_at": datetime.now(),
            "last_accessed": datetime.now(),
            "metadata": metadata or {},
            "active": True
        }
        
        self.active_sessions[session_id] = session_info
        
        # 通知對話管理器
        if self.dialogue_manager:
            await self.dialogue_manager.create_session(session_id, service_type.value)
        
        logger.info(f"Created session {session_id} for {service_type.value}")
        return session_id
    
    async def close_session(self, session_id: str) -> bool:
        """關閉會話"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["active"] = False
            
            # 通知對話管理器
            if self.dialogue_manager:
                await self.dialogue_manager.close_session(session_id)
            
            logger.info(f"Closed session {session_id}")
            return True
        
        return False
    
    async def cleanup_expired_sessions(self):
        """清理過期會話"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session_info in self.active_sessions.items():
            if session_info["active"]:
                time_diff = current_time - session_info["last_accessed"]
                if time_diff.total_seconds() > self.session_timeout:
                    expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self.close_session(session_id)
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        return len(expired_sessions)
    
    def get_status(self) -> Dict[str, Any]:
        """獲取 MCP 狀態"""
        return {
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "initialized": self.initialized,
            "registered_services": len(self.registered_services),
            "active_sessions": len([s for s in self.active_sessions.values() if s["active"]]),
            "stats": self.stats,
            "components": {
                "rag_engine": self.rag_engine.get_status() if self.rag_engine else "not_initialized",
                "dialogue_manager": self.dialogue_manager.get_status() if self.dialogue_manager else "not_initialized",
                "lsp_adapter": self.lsp_adapter.get_status() if self.lsp_adapter else "not_initialized",
                "context_router": self.context_router.get_status() if self.context_router else "not_initialized",
                "context_compressor": self.context_compressor.get_status() if self.context_compressor else "not_initialized"
            }
        }
    
    async def shutdown(self):
        """關閉 MCP"""
        logger.info("Shutting down AICore Context Manager MCP...")
        
        # 關閉所有活動會話
        for session_id in list(self.active_sessions.keys()):
            await self.close_session(session_id)
        
        # 關閉子組件
        if self.rag_engine:
            await self.rag_engine.shutdown()
        if self.dialogue_manager:
            await self.dialogue_manager.shutdown()
        if self.lsp_adapter:
            await self.lsp_adapter.shutdown()
        if self.context_router:
            await self.context_router.shutdown()
        if self.context_compressor:
            await self.context_compressor.shutdown()
        
        self.status = "shutdown"
        logger.info("AICore Context Manager MCP shut down")

# 工廠函數
async def create_aicore_context_manager_mcp(config: Dict[str, Any] = None) -> AICoreContextManagerMCP:
    """創建並初始化 AICore Context Manager MCP"""
    mcp = AICoreContextManagerMCP(config)
    await mcp.initialize()
    return mcp

if __name__ == "__main__":
    # 測試代碼
    async def test_mcp():
        config = {
            "rag_engine": {"max_chunk_size": 2000},
            "dialogue_manager": {"max_history": 100},
            "lsp_adapter": {"enabled": True}
        }
        
        mcp = await create_aicore_context_manager_mcp(config)
        
        # 註冊服務
        await mcp.register_service("smart_routing", ServiceType.SMART_ROUTING)
        await mcp.register_service("code_generation", ServiceType.CODE_GENERATION)
        
        # 創建會話
        session_id = await mcp.create_session(ServiceType.CODE_GENERATION)
        
        # 請求上下文
        request = ContextRequest(
            request_id="test-001",
            service_type=ServiceType.CODE_GENERATION,
            scope=ContextScope.SESSION,
            query="Create a REST API for user management",
            session_id=session_id
        )
        
        response = await mcp.get_context(request)
        print(f"Context response: {response.success}")
        print(f"Token count: {response.token_count}")
        print(f"Quality score: {response.quality_score}")
        
        # 關閉會話
        await mcp.close_session(session_id)
        
        # 關閉 MCP
        await mcp.shutdown()
    
    asyncio.run(test_mcp())

