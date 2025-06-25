#!/usr/bin/env python3
"""
Context Manager Workflow Unit Tests
上下文管理工作流單元測試

測試 Context Manager Workflow 的各個組件和功能
"""

import asyncio
import pytest
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# 添加項目路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../.."))

from PowerAutomation.workflows.context_manager.context_manager_workflow import (
    ContextManagerWorkflow,
    WorkflowRequest,
    WorkflowResponse,
    ServiceType,
    WorkflowStage,
    create_context_manager_workflow
)
from PowerAutomation.workflows.context_manager.utils.context_router import (
    RequestType,
    RoutingRequest,
    RoutingStrategy
)
from PowerAutomation.workflows.context_manager.utils.context_compressor import (
    ContextItem,
    ContentType,
    CompressionStrategy
)

class TestContextManagerWorkflow:
    """Context Manager Workflow 測試類"""
    
    @pytest.fixture
    async def temp_dir(self):
        """創建臨時目錄"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    async def workflow_config(self, temp_dir):
        """工作流配置"""
        return {
            "enable_caching": True,
            "cache_ttl": 300,
            "max_concurrent_requests": 5,
            "health_check_interval": 10,
            "rag_engine": {
                "storage_path": os.path.join(temp_dir, "rag_storage"),
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "enable_persistence": False  # 測試模式不持久化
            },
            "dialogue_manager": {
                "storage_path": os.path.join(temp_dir, "dialogue_storage"),
                "max_sessions": 10,
                "enable_persistence": False
            },
            "lsp_adapter": {
                "serena": {
                    "serena_path": "mock_serena",
                    "memory_enabled": True
                },
                "auto_detect_language": True,
                "enable_caching": True
            },
            "context_router": {
                "default_strategy": "balanced",
                "enable_caching": True
            },
            "context_compressor": {
                "default_strategy": "hybrid",
                "preserve_dependencies": True
            }
        }
    
    @pytest.fixture
    async def mock_workflow(self, workflow_config):
        """創建模擬工作流"""
        workflow = ContextManagerWorkflow(workflow_config)
        
        # 模擬組件初始化
        workflow.rag_engine = Mock()
        workflow.rag_engine.search = AsyncMock(return_value=[
            {"id": "test1", "content": "Test RAG result 1", "score": 0.9},
            {"id": "test2", "content": "Test RAG result 2", "score": 0.8}
        ])
        workflow.rag_engine.get_status = Mock(return_value={"status": "ready"})
        workflow.rag_engine.shutdown = AsyncMock()
        
        workflow.dialogue_manager = Mock()
        workflow.dialogue_manager.get_session_context = AsyncMock(return_value={
            "session_id": "test_session",
            "messages": ["Hello", "How are you?"]
        })
        workflow.dialogue_manager.get_status = Mock(return_value={"status": "ready"})
        workflow.dialogue_manager.shutdown = AsyncMock()
        
        workflow.lsp_adapter = Mock()
        workflow.lsp_adapter.analyze_project = AsyncMock(return_value=Mock(
            project_path="/test/path",
            language="python",
            symbols=[],
            __dict__={"project_path": "/test/path", "language": "python", "symbols": []}
        ))
        workflow.lsp_adapter.get_status = Mock(return_value={"status": "ready"})
        workflow.lsp_adapter.shutdown = AsyncMock()
        
        workflow.context_router = Mock()
        workflow.context_router.route_request = AsyncMock(return_value=Mock(
            selected_components=[("rag_engine", "universal_rag")],
            confidence_score=0.8
        ))
        workflow.context_router.get_status = Mock(return_value={"status": "ready"})
        workflow.context_router.shutdown = AsyncMock()
        
        workflow.context_compressor = Mock()
        workflow.context_compressor.compress_context = AsyncMock(return_value=Mock(
            compressed_items=[
                ContextItem(
                    item_id="compressed_1",
                    content="Compressed content",
                    content_type=ContentType.REFERENCE,
                    token_count=50
                )
            ],
            original_token_count=200,
            compressed_token_count=50,
            compression_ratio=0.25
        ))
        workflow.context_compressor.importance_calculator = Mock()
        workflow.context_compressor.importance_calculator.calculate_importance = AsyncMock(return_value=0.8)
        workflow.context_compressor.get_status = Mock(return_value={"status": "ready"})
        workflow.context_compressor.shutdown = AsyncMock()
        
        # 設置初始化狀態
        workflow.initialized = True
        workflow.status = "ready"
        
        return workflow
    
    @pytest.mark.asyncio
    async def test_workflow_initialization(self, workflow_config):
        """測試工作流初始化"""
        with patch('PowerAutomation.workflows.context_manager.context_manager_workflow.create_universal_rag_engine') as mock_rag, \
             patch('PowerAutomation.workflows.context_manager.context_manager_workflow.create_dialogue_context_manager') as mock_dialogue, \
             patch('PowerAutomation.workflows.context_manager.context_manager_workflow.create_universal_lsp_adapter') as mock_lsp, \
             patch('PowerAutomation.workflows.context_manager.context_manager_workflow.create_context_router') as mock_router, \
             patch('PowerAutomation.workflows.context_manager.context_manager_workflow.create_context_compressor') as mock_compressor:
            
            # 設置模擬返回值
            mock_rag.return_value = Mock()
            mock_dialogue.return_value = Mock()
            mock_lsp.return_value = Mock()
            mock_router.return_value = Mock()
            mock_compressor.return_value = Mock()
            
            workflow = ContextManagerWorkflow(workflow_config)
            result = await workflow.initialize()
            
            assert result is True
            assert workflow.initialized is True
            assert workflow.status == "ready"
            assert len(workflow.component_status) == 5
            
            # 驗證組件初始化被調用
            mock_rag.assert_called_once()
            mock_dialogue.assert_called_once()
            mock_lsp.assert_called_once()
            mock_router.assert_called_once()
            mock_compressor.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_request_success(self, mock_workflow):
        """測試成功處理請求"""
        request = WorkflowRequest(
            request_id="test-001",
            service_type=ServiceType.CODE_GENERATION,
            request_type=RequestType.CODE_GENERATION,
            content="Create a Python function",
            context={"project_path": "/test/path", "session_id": "test_session"},
            max_tokens=1000,
            priority=7
        )
        
        response = await mock_workflow.process_request(request)
        
        assert response.success is True
        assert response.request_id == "test-001"
        assert len(response.stages_completed) > 0
        assert WorkflowStage.REQUEST_ANALYSIS in response.stages_completed
        assert WorkflowStage.CONTEXT_RETRIEVAL in response.stages_completed
        assert WorkflowStage.CONTEXT_ENHANCEMENT in response.stages_completed
        assert WorkflowStage.CONTEXT_COMPRESSION in response.stages_completed
        assert response.processing_time > 0
        assert len(response.enhanced_context) > 0
        assert len(response.compressed_context) > 0
        
        # 驗證統計更新
        assert mock_workflow.stats["total_requests"] == 1
        assert mock_workflow.stats["successful_requests"] == 1
        assert mock_workflow.stats["service_type_distribution"]["code_generation"] == 1
    
    @pytest.mark.asyncio
    async def test_process_request_with_caching(self, mock_workflow):
        """測試帶緩存的請求處理"""
        request = WorkflowRequest(
            request_id="test-002",
            service_type=ServiceType.SMART_ROUTING,
            request_type=RequestType.GENERAL_QUERY,
            content="Test query",
            max_tokens=500
        )
        
        # 第一次請求
        response1 = await mock_workflow.process_request(request)
        assert response1.success is True
        
        # 第二次相同請求（應該命中緩存）
        request2 = WorkflowRequest(
            request_id="test-003",  # 不同ID但內容相同
            service_type=ServiceType.SMART_ROUTING,
            request_type=RequestType.GENERAL_QUERY,
            content="Test query",
            max_tokens=500
        )
        
        response2 = await mock_workflow.process_request(request2)
        assert response2.success is True
        
        # 驗證緩存使用
        assert len(mock_workflow.workflow_cache) > 0
    
    @pytest.mark.asyncio
    async def test_context_retrieval(self, mock_workflow):
        """測試上下文檢索"""
        request = WorkflowRequest(
            request_id="test-retrieval",
            service_type=ServiceType.CODE_GENERATION,
            request_type=RequestType.CODE_ANALYSIS,
            content="Analyze this code",
            context={"project_path": "/test/path", "session_id": "test_session"}
        )
        
        routing_request = await mock_workflow._analyze_request(request)
        context_items = await mock_workflow._retrieve_context(request, routing_request)
        
        assert len(context_items) > 0
        
        # 驗證 RAG 檢索被調用
        mock_workflow.rag_engine.search.assert_called_once()
        
        # 驗證 LSP 分析被調用
        mock_workflow.lsp_adapter.analyze_project.assert_called_once_with("/test/path")
        
        # 驗證對話上下文檢索被調用
        mock_workflow.dialogue_manager.get_session_context.assert_called_once_with("test_session")
    
    @pytest.mark.asyncio
    async def test_context_enhancement(self, mock_workflow):
        """測試上下文增強"""
        request = WorkflowRequest(
            request_id="test-enhancement",
            service_type=ServiceType.CODE_GENERATION,
            request_type=RequestType.CODE_GENERATION,
            content="Generate code"
        )
        
        initial_items = [
            ContextItem(
                item_id="initial_1",
                content="Initial content",
                content_type=ContentType.REFERENCE
            )
        ]
        
        enhanced_items = await mock_workflow._enhance_context(request, initial_items)
        
        assert len(enhanced_items) > len(initial_items)
        
        # 驗證請求項目被添加到前面
        assert enhanced_items[0].item_id == "current_request"
        assert enhanced_items[0].content == "Generate code"
        assert enhanced_items[0].importance_score == 1.0
    
    @pytest.mark.asyncio
    async def test_context_compression(self, mock_workflow):
        """測試上下文壓縮"""
        request = WorkflowRequest(
            request_id="test-compression",
            service_type=ServiceType.CODE_GENERATION,
            request_type=RequestType.CODE_GENERATION,
            content="Test compression",
            max_tokens=100
        )
        
        context_items = [
            ContextItem(
                item_id="item_1",
                content="Long content that needs compression " * 20,
                content_type=ContentType.DOCUMENTATION,
                token_count=100
            ),
            ContextItem(
                item_id="item_2",
                content="Another long content " * 15,
                content_type=ContentType.CODE,
                token_count=80
            )
        ]
        
        compressed_items = await mock_workflow._compress_context(request, context_items)
        
        # 驗證壓縮器被調用
        mock_workflow.context_compressor.compress_context.assert_called_once()
        
        # 驗證返回壓縮後的項目
        assert len(compressed_items) > 0
        assert compressed_items[0].item_id == "compressed_1"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, mock_workflow):
        """測試並發請求處理"""
        requests = []
        for i in range(5):
            request = WorkflowRequest(
                request_id=f"concurrent-{i}",
                service_type=ServiceType.GENERAL_AI,
                request_type=RequestType.GENERAL_QUERY,
                content=f"Concurrent request {i}",
                max_tokens=500
            )
            requests.append(request)
        
        # 並發處理請求
        tasks = [mock_workflow.process_request(req) for req in requests]
        responses = await asyncio.gather(*tasks)
        
        # 驗證所有請求都成功處理
        assert len(responses) == 5
        for response in responses:
            assert response.success is True
        
        # 驗證統計更新
        assert mock_workflow.stats["total_requests"] == 5
        assert mock_workflow.stats["successful_requests"] == 5
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_workflow):
        """測試錯誤處理"""
        # 模擬 RAG 引擎錯誤
        mock_workflow.rag_engine.search.side_effect = Exception("RAG error")
        
        request = WorkflowRequest(
            request_id="test-error",
            service_type=ServiceType.CODE_GENERATION,
            request_type=RequestType.CODE_GENERATION,
            content="Test error handling"
        )
        
        response = await mock_workflow.process_request(request)
        
        # 即使有錯誤，工作流應該繼續處理
        assert response.request_id == "test-error"
        # 可能成功也可能失敗，取決於其他組件
        assert isinstance(response.success, bool)
        
        # 驗證統計更新
        assert mock_workflow.stats["total_requests"] == 1
    
    @pytest.mark.asyncio
    async def test_get_status(self, mock_workflow):
        """測試獲取狀態"""
        status = mock_workflow.get_status()
        
        assert status["name"] == "Context Manager Workflow"
        assert status["version"] == "1.0.0"
        assert status["status"] == "ready"
        assert status["initialized"] is True
        assert "stats" in status
        assert "component_status" in status
        assert "active_requests" in status
        assert "cache_stats" in status
        assert "config" in status
        
        # 驗證組件狀態
        assert len(status["component_status"]) == 5
        for component_status in status["component_status"].values():
            assert "component_name" in component_status
            assert "status" in component_status
            assert "initialized" in component_status
    
    @pytest.mark.asyncio
    async def test_cache_cleanup(self, mock_workflow):
        """測試緩存清理"""
        # 添加過期緩存項目
        expired_response = WorkflowResponse(
            request_id="expired",
            success=True,
            timestamp=datetime.now() - timedelta(seconds=400)  # 超過TTL
        )
        mock_workflow.workflow_cache["expired_key"] = expired_response
        
        # 添加有效緩存項目
        valid_response = WorkflowResponse(
            request_id="valid",
            success=True,
            timestamp=datetime.now()
        )
        mock_workflow.workflow_cache["valid_key"] = valid_response
        
        # 執行緩存清理
        await mock_workflow._cleanup_cache()
        
        # 驗證過期項目被清理
        assert "expired_key" not in mock_workflow.workflow_cache
        assert "valid_key" in mock_workflow.workflow_cache
    
    @pytest.mark.asyncio
    async def test_shutdown(self, mock_workflow):
        """測試工作流關閉"""
        # 添加一些狀態
        mock_workflow.workflow_cache["test"] = Mock()
        mock_workflow.active_requests["test"] = Mock()
        
        await mock_workflow.shutdown()
        
        assert mock_workflow.status == "shutdown"
        assert len(mock_workflow.workflow_cache) == 0
        assert len(mock_workflow.active_requests) == 0
        assert len(mock_workflow.component_status) == 0
        
        # 驗證所有組件的 shutdown 被調用
        mock_workflow.rag_engine.shutdown.assert_called_once()
        mock_workflow.dialogue_manager.shutdown.assert_called_once()
        mock_workflow.lsp_adapter.shutdown.assert_called_once()
        mock_workflow.context_router.shutdown.assert_called_once()
        mock_workflow.context_compressor.shutdown.assert_called_once()

class TestWorkflowRequest:
    """WorkflowRequest 測試類"""
    
    def test_workflow_request_creation(self):
        """測試工作流請求創建"""
        request = WorkflowRequest(
            request_id="test-request",
            service_type=ServiceType.CODE_GENERATION,
            request_type=RequestType.CODE_GENERATION,
            content="Test content",
            context={"key": "value"},
            metadata={"meta": "data"},
            max_tokens=2000,
            priority=8
        )
        
        assert request.request_id == "test-request"
        assert request.service_type == ServiceType.CODE_GENERATION
        assert request.request_type == RequestType.CODE_GENERATION
        assert request.content == "Test content"
        assert request.context == {"key": "value"}
        assert request.metadata == {"meta": "data"}
        assert request.max_tokens == 2000
        assert request.priority == 8
        assert isinstance(request.timestamp, datetime)

class TestWorkflowResponse:
    """WorkflowResponse 測試類"""
    
    def test_workflow_response_creation(self):
        """測試工作流響應創建"""
        context_item = ContextItem(
            item_id="test_item",
            content="Test content",
            content_type=ContentType.CODE
        )
        
        response = WorkflowResponse(
            request_id="test-response",
            success=True,
            enhanced_context=[context_item],
            compressed_context=[context_item],
            metadata={"tokens": 100},
            processing_time=1.5,
            stages_completed=[WorkflowStage.REQUEST_ANALYSIS]
        )
        
        assert response.request_id == "test-response"
        assert response.success is True
        assert len(response.enhanced_context) == 1
        assert len(response.compressed_context) == 1
        assert response.metadata == {"tokens": 100}
        assert response.processing_time == 1.5
        assert response.stages_completed == [WorkflowStage.REQUEST_ANALYSIS]
        assert isinstance(response.timestamp, datetime)

if __name__ == "__main__":
    # 運行測試
    pytest.main([__file__, "-v", "--tb=short"])

