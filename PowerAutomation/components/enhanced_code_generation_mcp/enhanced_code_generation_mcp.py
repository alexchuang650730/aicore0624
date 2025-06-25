#!/usr/bin/env python3
"""
Enhanced Code Generation MCP with RAG and Serena LSP Integration
增強型代碼生成 MCP，整合 RAG 檢索和 Serena LSP 能力

提供上下文感知的智能代碼生成，支持項目風格學習和代碼模式識別
整合 KiloCode 作為高質量代碼生成的備選方案
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
from .rag_enhancement.code_rag_engine import CodeRAGEngine
from .lsp_integration.serena_lsp_adapter import SerenaLSPAdapter
from .kilocode_integration.kilocode_client import KiloCodeClient
from .utils.context_manager import ContextManager
from .utils.quality_evaluator import QualityEvaluator

logger = logging.getLogger(__name__)

class CodeGenerationStrategy(Enum):
    """代碼生成策略"""
    TEMPLATE_BASED = "template_based"
    RAG_ENHANCED = "rag_enhanced"
    LSP_GUIDED = "lsp_guided"
    HYBRID = "hybrid"
    KILOCODE_FALLBACK = "kilocode_fallback"

class RequestType(Enum):
    """請求類型"""
    GENERATE_CODE = "generate_code"
    ANALYZE_PROJECT = "analyze_project"
    REFACTOR_CODE = "refactor_code"
    OPTIMIZE_CODE = "optimize_code"
    GENERATE_TESTS = "generate_tests"
    GET_CONTEXT = "get_context"

@dataclass
class CodeGenerationRequest:
    """代碼生成請求"""
    request_id: str
    request_type: RequestType
    requirements: str
    language: str = "python"
    framework: Optional[str] = None
    project_path: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    strategy: CodeGenerationStrategy = CodeGenerationStrategy.HYBRID
    quality_threshold: float = 0.8
    max_context_tokens: int = 10000
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class CodeGenerationResponse:
    """代碼生成響應"""
    request_id: str
    success: bool
    generated_code: Optional[str] = None
    quality_score: float = 0.0
    strategy_used: Optional[CodeGenerationStrategy] = None
    context_used: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

class EnhancedCodeGenerationMCP:
    """增強型代碼生成 MCP"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = "Enhanced Code Generation MCP"
        self.version = "1.0.0"
        self.description = "AI-powered code generation with RAG and LSP integration"
        
        # 初始化子組件
        self.rag_engine = None
        self.lsp_adapter = None
        self.kilocode_client = None
        self.context_manager = None
        self.quality_evaluator = None
        
        # 狀態管理
        self.initialized = False
        self.status = "initializing"
        
        # 性能統計
        self.stats = {
            "total_requests": 0,
            "successful_generations": 0,
            "average_quality_score": 0.0,
            "strategy_usage": {
                "template_based": 0,
                "rag_enhanced": 0,
                "lsp_guided": 0,
                "hybrid": 0,
                "kilocode_fallback": 0
            }
        }
        
        logger.info(f"Initializing {self.name} v{self.version}")
    
    async def initialize(self) -> bool:
        """初始化 MCP 組件"""
        try:
            logger.info("Initializing Enhanced Code Generation MCP components...")
            
            # 初始化 RAG 引擎
            rag_config = self.config.get("rag_engine", {})
            self.rag_engine = CodeRAGEngine(rag_config)
            await self.rag_engine.initialize()
            logger.info("✅ RAG Engine initialized")
            
            # 初始化 LSP 適配器
            lsp_config = self.config.get("lsp_integration", {})
            self.lsp_adapter = SerenaLSPAdapter(lsp_config)
            await self.lsp_adapter.initialize()
            logger.info("✅ LSP Adapter initialized")
            
            # 初始化 KiloCode 客戶端
            kilocode_config = self.config.get("kilocode_integration", {})
            self.kilocode_client = KiloCodeClient(kilocode_config)
            await self.kilocode_client.initialize()
            logger.info("✅ KiloCode Client initialized")
            
            # 初始化上下文管理器
            context_config = self.config.get("context_manager", {})
            self.context_manager = ContextManager(context_config)
            await self.context_manager.initialize()
            logger.info("✅ Context Manager initialized")
            
            # 初始化質量評估器
            quality_config = self.config.get("quality_evaluator", {})
            self.quality_evaluator = QualityEvaluator(quality_config)
            await self.quality_evaluator.initialize()
            logger.info("✅ Quality Evaluator initialized")
            
            self.initialized = True
            self.status = "ready"
            logger.info(f"🎉 {self.name} initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.name}: {e}")
            self.status = "error"
            return False
    
    async def process_request(self, request: CodeGenerationRequest) -> CodeGenerationResponse:
        """處理代碼生成請求"""
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        try:
            logger.info(f"Processing request {request.request_id}: {request.request_type.value}")
            
            # 路由到對應的處理方法
            if request.request_type == RequestType.GENERATE_CODE:
                response = await self._generate_code(request)
            elif request.request_type == RequestType.ANALYZE_PROJECT:
                response = await self._analyze_project(request)
            elif request.request_type == RequestType.REFACTOR_CODE:
                response = await self._refactor_code(request)
            elif request.request_type == RequestType.OPTIMIZE_CODE:
                response = await self._optimize_code(request)
            elif request.request_type == RequestType.GENERATE_TESTS:
                response = await self._generate_tests(request)
            elif request.request_type == RequestType.GET_CONTEXT:
                response = await self._get_context(request)
            else:
                raise ValueError(f"Unknown request type: {request.request_type}")
            
            # 更新統計
            if response.success:
                self.stats["successful_generations"] += 1
                if response.strategy_used:
                    self.stats["strategy_usage"][response.strategy_used.value] += 1
            
            response.processing_time = time.time() - start_time
            logger.info(f"✅ Request {request.request_id} completed in {response.processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error processing request {request.request_id}: {e}")
            return CodeGenerationResponse(
                request_id=request.request_id,
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    async def _generate_code(self, request: CodeGenerationRequest) -> CodeGenerationResponse:
        """生成代碼"""
        logger.info(f"Generating code for: {request.requirements}")
        
        # 1. 構建上下文
        context = await self.context_manager.build_context(
            request.requirements,
            request.project_path,
            request.max_context_tokens
        )
        
        # 2. 選擇生成策略
        strategy = await self._select_generation_strategy(request, context)
        
        # 3. 執行代碼生成
        generated_code = await self._execute_generation_strategy(
            strategy, request, context
        )
        
        # 4. 質量評估
        quality_score = await self.quality_evaluator.evaluate_code(
            generated_code, request.language, context
        )
        
        # 5. 如果質量不達標，嘗試 KiloCode 回退
        if quality_score < request.quality_threshold and strategy != CodeGenerationStrategy.KILOCODE_FALLBACK:
            logger.info(f"Quality score {quality_score:.2f} below threshold {request.quality_threshold}, trying KiloCode fallback")
            kilocode_result = await self.kilocode_client.generate_code(request, context)
            if kilocode_result.success and kilocode_result.quality_score > quality_score:
                generated_code = kilocode_result.generated_code
                quality_score = kilocode_result.quality_score
                strategy = CodeGenerationStrategy.KILOCODE_FALLBACK
        
        return CodeGenerationResponse(
            request_id=request.request_id,
            success=True,
            generated_code=generated_code,
            quality_score=quality_score,
            strategy_used=strategy,
            context_used=context,
            metadata={
                "language": request.language,
                "framework": request.framework,
                "context_tokens": len(str(context))
            }
        )
    
    async def _select_generation_strategy(self, request: CodeGenerationRequest, context: Dict[str, Any]) -> CodeGenerationStrategy:
        """選擇代碼生成策略"""
        if request.strategy != CodeGenerationStrategy.HYBRID:
            return request.strategy
        
        # 智能策略選擇邏輯
        complexity_score = await self._assess_complexity(request.requirements)
        context_richness = len(str(context)) / 1000  # 簡化的上下文豐富度評估
        
        if complexity_score > 0.8 or context_richness > 10:
            return CodeGenerationStrategy.LSP_GUIDED
        elif context_richness > 5:
            return CodeGenerationStrategy.RAG_ENHANCED
        else:
            return CodeGenerationStrategy.TEMPLATE_BASED
    
    async def _execute_generation_strategy(self, strategy: CodeGenerationStrategy, 
                                         request: CodeGenerationRequest, 
                                         context: Dict[str, Any]) -> str:
        """執行代碼生成策略"""
        if strategy == CodeGenerationStrategy.TEMPLATE_BASED:
            return await self._generate_from_template(request, context)
        elif strategy == CodeGenerationStrategy.RAG_ENHANCED:
            return await self._generate_with_rag(request, context)
        elif strategy == CodeGenerationStrategy.LSP_GUIDED:
            return await self._generate_with_lsp(request, context)
        elif strategy == CodeGenerationStrategy.KILOCODE_FALLBACK:
            result = await self.kilocode_client.generate_code(request, context)
            return result.generated_code if result.success else ""
        else:
            # Hybrid 策略 - 結合多種方法
            return await self._generate_hybrid(request, context)
    
    async def _generate_from_template(self, request: CodeGenerationRequest, context: Dict[str, Any]) -> str:
        """基於模板生成代碼"""
        # 實現模板基礎的代碼生成
        logger.info("Generating code using template-based strategy")
        # TODO: 實現模板生成邏輯
        return f"# Template-based code generation for: {request.requirements}\n# TODO: Implement"
    
    async def _generate_with_rag(self, request: CodeGenerationRequest, context: Dict[str, Any]) -> str:
        """使用 RAG 增強生成代碼"""
        logger.info("Generating code using RAG-enhanced strategy")
        
        # 使用 RAG 引擎檢索相關代碼
        similar_code = await self.rag_engine.retrieve_similar_code(
            request.requirements, request.language, request.project_path
        )
        
        # 基於檢索結果生成代碼
        return await self.rag_engine.generate_code_with_context(
            request.requirements, similar_code, context
        )
    
    async def _generate_with_lsp(self, request: CodeGenerationRequest, context: Dict[str, Any]) -> str:
        """使用 LSP 引導生成代碼"""
        logger.info("Generating code using LSP-guided strategy")
        
        # 獲取項目結構和符號信息
        project_info = await self.lsp_adapter.analyze_project(request.project_path)
        
        # 基於項目信息生成代碼
        return await self.lsp_adapter.generate_code_with_project_context(
            request.requirements, project_info, context
        )
    
    async def _generate_hybrid(self, request: CodeGenerationRequest, context: Dict[str, Any]) -> str:
        """混合策略生成代碼"""
        logger.info("Generating code using hybrid strategy")
        
        # 結合 RAG 和 LSP 的信息
        rag_context = await self.rag_engine.retrieve_similar_code(
            request.requirements, request.language, request.project_path
        )
        lsp_context = await self.lsp_adapter.analyze_project(request.project_path)
        
        # 融合上下文信息生成代碼
        merged_context = {**context, "rag_context": rag_context, "lsp_context": lsp_context}
        
        return await self._generate_with_merged_context(request, merged_context)
    
    async def _generate_with_merged_context(self, request: CodeGenerationRequest, merged_context: Dict[str, Any]) -> str:
        """使用融合上下文生成代碼"""
        # TODO: 實現融合上下文的代碼生成邏輯
        return f"# Hybrid code generation for: {request.requirements}\n# TODO: Implement with merged context"
    
    async def _assess_complexity(self, requirements: str) -> float:
        """評估需求複雜度"""
        # 簡化的複雜度評估
        complexity_keywords = ["complex", "advanced", "integration", "architecture", "system", "multiple"]
        score = sum(1 for keyword in complexity_keywords if keyword.lower() in requirements.lower())
        return min(score / len(complexity_keywords), 1.0)
    
    async def _analyze_project(self, request: CodeGenerationRequest) -> CodeGenerationResponse:
        """分析項目"""
        logger.info(f"Analyzing project: {request.project_path}")
        
        # 使用 LSP 適配器分析項目
        analysis = await self.lsp_adapter.analyze_project(request.project_path)
        
        return CodeGenerationResponse(
            request_id=request.request_id,
            success=True,
            metadata={"analysis": analysis}
        )
    
    async def _refactor_code(self, request: CodeGenerationRequest) -> CodeGenerationResponse:
        """重構代碼"""
        logger.info("Refactoring code")
        # TODO: 實現代碼重構邏輯
        return CodeGenerationResponse(
            request_id=request.request_id,
            success=True,
            generated_code="# Refactored code placeholder"
        )
    
    async def _optimize_code(self, request: CodeGenerationRequest) -> CodeGenerationResponse:
        """優化代碼"""
        logger.info("Optimizing code")
        # TODO: 實現代碼優化邏輯
        return CodeGenerationResponse(
            request_id=request.request_id,
            success=True,
            generated_code="# Optimized code placeholder"
        )
    
    async def _generate_tests(self, request: CodeGenerationRequest) -> CodeGenerationResponse:
        """生成測試代碼"""
        logger.info("Generating test code")
        # TODO: 實現測試代碼生成邏輯
        return CodeGenerationResponse(
            request_id=request.request_id,
            success=True,
            generated_code="# Test code placeholder"
        )
    
    async def _get_context(self, request: CodeGenerationRequest) -> CodeGenerationResponse:
        """獲取上下文信息"""
        logger.info("Getting context information")
        
        context = await self.context_manager.build_context(
            request.requirements,
            request.project_path,
            request.max_context_tokens
        )
        
        return CodeGenerationResponse(
            request_id=request.request_id,
            success=True,
            metadata={"context": context}
        )
    
    def get_status(self) -> Dict[str, Any]:
        """獲取 MCP 狀態"""
        return {
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "initialized": self.initialized,
            "stats": self.stats,
            "components": {
                "rag_engine": self.rag_engine.get_status() if self.rag_engine else "not_initialized",
                "lsp_adapter": self.lsp_adapter.get_status() if self.lsp_adapter else "not_initialized",
                "kilocode_client": self.kilocode_client.get_status() if self.kilocode_client else "not_initialized",
                "context_manager": self.context_manager.get_status() if self.context_manager else "not_initialized",
                "quality_evaluator": self.quality_evaluator.get_status() if self.quality_evaluator else "not_initialized"
            }
        }

# 工廠函數
async def create_enhanced_code_generation_mcp(config: Dict[str, Any] = None) -> EnhancedCodeGenerationMCP:
    """創建並初始化 Enhanced Code Generation MCP"""
    mcp = EnhancedCodeGenerationMCP(config)
    await mcp.initialize()
    return mcp

if __name__ == "__main__":
    # 測試代碼
    async def test_mcp():
        config = {
            "rag_engine": {"max_chunk_size": 2000},
            "lsp_integration": {"server_port": 2087},
            "kilocode_integration": {"enabled": True}
        }
        
        mcp = await create_enhanced_code_generation_mcp(config)
        
        request = CodeGenerationRequest(
            request_id="test-001",
            request_type=RequestType.GENERATE_CODE,
            requirements="Create a REST API endpoint for user management",
            language="python",
            framework="flask"
        )
        
        response = await mcp.process_request(request)
        print(f"Generated code: {response.generated_code}")
        print(f"Quality score: {response.quality_score}")
        print(f"Strategy used: {response.strategy_used}")
    
    asyncio.run(test_mcp())

