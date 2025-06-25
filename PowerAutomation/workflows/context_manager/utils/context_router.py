#!/usr/bin/env python3
"""
Context Router
上下文路由器

智能路由上下文請求到最合適的處理組件
根據請求類型、內容分析和系統負載進行動態路由決策
"""

import asyncio
import json
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from collections import defaultdict, deque
import re

logger = logging.getLogger(__name__)

class RequestType(Enum):
    """請求類型"""
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    DOCUMENTATION = "documentation"
    CONVERSATION = "conversation"
    PROJECT_ANALYSIS = "project_analysis"
    SYMBOL_LOOKUP = "symbol_lookup"
    ERROR_DIAGNOSIS = "error_diagnosis"
    TESTING = "testing"
    REFACTORING = "refactoring"
    GENERAL_QUERY = "general_query"

class RoutingStrategy(Enum):
    """路由策略"""
    PERFORMANCE_FIRST = "performance_first"    # 性能優先
    QUALITY_FIRST = "quality_first"            # 質量優先
    BALANCED = "balanced"                       # 平衡策略
    COST_OPTIMIZED = "cost_optimized"          # 成本優化
    SPECIALIZED = "specialized"                # 專業化路由

class ComponentType(Enum):
    """組件類型"""
    RAG_ENGINE = "rag_engine"
    LSP_ADAPTER = "lsp_adapter"
    DIALOGUE_MANAGER = "dialogue_manager"
    CODE_GENERATOR = "code_generator"
    KILOCODE_CLIENT = "kilocode_client"
    CONTEXT_COMPRESSOR = "context_compressor"

@dataclass
class RoutingRequest:
    """路由請求"""
    request_id: str
    request_type: RequestType
    content: str
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10, 10最高
    max_processing_time: float = 30.0  # 秒
    quality_threshold: float = 0.7
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ComponentProfile:
    """組件配置文件"""
    component_type: ComponentType
    component_id: str
    capabilities: List[RequestType]
    performance_score: float = 0.8  # 0-1
    quality_score: float = 0.8      # 0-1
    cost_score: float = 0.8         # 0-1
    current_load: float = 0.0       # 0-1
    max_concurrent: int = 10
    average_response_time: float = 1.0  # 秒
    success_rate: float = 0.95      # 0-1
    specializations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RoutingDecision:
    """路由決策"""
    request_id: str
    selected_components: List[Tuple[ComponentType, str]]  # (type, id)
    routing_strategy: RoutingStrategy
    confidence_score: float
    estimated_processing_time: float
    estimated_quality: float
    fallback_components: List[Tuple[ComponentType, str]] = field(default_factory=list)
    routing_metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

class RequestAnalyzer:
    """請求分析器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # 關鍵詞模式
        self.patterns = {
            RequestType.CODE_GENERATION: [
                r"生成|create|generate|write.*code|implement|build",
                r"function|class|method|api|endpoint",
                r"需要.*代碼|寫.*程式"
            ],
            RequestType.CODE_ANALYSIS: [
                r"分析|analyze|review|examine|inspect",
                r"代碼|code|程式|script",
                r"bug|error|問題|issue"
            ],
            RequestType.DOCUMENTATION: [
                r"文檔|documentation|doc|說明|manual",
                r"如何|how to|教學|tutorial",
                r"解釋|explain|describe"
            ],
            RequestType.CONVERSATION: [
                r"聊天|chat|對話|conversation",
                r"你好|hello|hi|嗨",
                r"謝謝|thank|感謝"
            ],
            RequestType.PROJECT_ANALYSIS: [
                r"項目|project|專案|repository",
                r"結構|structure|architecture|框架",
                r"概覽|overview|summary"
            ],
            RequestType.SYMBOL_LOOKUP: [
                r"定義|definition|宣告|declaration",
                r"符號|symbol|變數|variable|函數|function",
                r"在哪|where|位置|location"
            ],
            RequestType.ERROR_DIAGNOSIS: [
                r"錯誤|error|bug|exception|問題",
                r"修復|fix|solve|debug|調試",
                r"為什麼|why|原因|cause"
            ],
            RequestType.TESTING: [
                r"測試|test|testing|單元測試|unit test",
                r"驗證|verify|validate|check",
                r"測試案例|test case"
            ],
            RequestType.REFACTORING: [
                r"重構|refactor|重寫|rewrite|優化|optimize",
                r"改進|improve|enhance|clean up",
                r"重新設計|redesign"
            ]
        }
        
        # 編譯正則表達式
        self.compiled_patterns = {}
        for request_type, patterns in self.patterns.items():
            self.compiled_patterns[request_type] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    async def analyze_request(self, request: RoutingRequest) -> Dict[str, Any]:
        """分析請求"""
        analysis = {
            "detected_type": request.request_type,
            "confidence": 0.5,
            "complexity": 0.5,
            "urgency": 0.5,
            "language": "unknown",
            "domain": "general",
            "keywords": [],
            "estimated_tokens": 0
        }
        
        content = request.content.lower()
        
        # 類型檢測
        type_scores = {}
        for request_type, patterns in self.compiled_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(pattern.findall(content))
                score += matches * 0.2
            
            if score > 0:
                type_scores[request_type] = min(score, 1.0)
        
        if type_scores:
            detected_type = max(type_scores, key=type_scores.get)
            analysis["detected_type"] = detected_type
            analysis["confidence"] = type_scores[detected_type]
        
        # 複雜度分析
        analysis["complexity"] = await self._analyze_complexity(request)
        
        # 緊急度分析
        analysis["urgency"] = await self._analyze_urgency(request)
        
        # 語言檢測
        analysis["language"] = await self._detect_language(request)
        
        # 領域檢測
        analysis["domain"] = await self._detect_domain(request)
        
        # 關鍵詞提取
        analysis["keywords"] = await self._extract_keywords(request)
        
        # Token 估算
        analysis["estimated_tokens"] = len(request.content.split())
        
        return analysis
    
    async def _analyze_complexity(self, request: RoutingRequest) -> float:
        """分析複雜度"""
        complexity = 0.5
        content = request.content.lower()
        
        # 基於長度
        if len(request.content) > 1000:
            complexity += 0.2
        elif len(request.content) < 100:
            complexity -= 0.1
        
        # 基於技術關鍵詞
        tech_keywords = [
            "algorithm", "architecture", "design pattern", "optimization",
            "performance", "scalability", "distributed", "microservice",
            "database", "api", "framework", "library"
        ]
        
        tech_count = sum(1 for keyword in tech_keywords if keyword in content)
        complexity += tech_count * 0.1
        
        # 基於代碼複雜度指標
        if any(keyword in content for keyword in ["class", "function", "method", "inheritance"]):
            complexity += 0.1
        
        return max(0.0, min(1.0, complexity))
    
    async def _analyze_urgency(self, request: RoutingRequest) -> float:
        """分析緊急度"""
        urgency = 0.5
        content = request.content.lower()
        
        # 緊急關鍵詞
        urgent_keywords = [
            "urgent", "emergency", "critical", "asap", "immediately",
            "緊急", "立即", "馬上", "重要", "關鍵"
        ]
        
        if any(keyword in content for keyword in urgent_keywords):
            urgency += 0.3
        
        # 錯誤相關
        error_keywords = ["error", "bug", "crash", "fail", "broken", "錯誤", "故障"]
        if any(keyword in content for keyword in error_keywords):
            urgency += 0.2
        
        # 基於優先級
        urgency += (request.priority - 5) * 0.1
        
        return max(0.0, min(1.0, urgency))
    
    async def _detect_language(self, request: RoutingRequest) -> str:
        """檢測編程語言"""
        content = request.content.lower()
        
        language_indicators = {
            "python": ["python", "py", "def ", "import ", "class ", "self"],
            "javascript": ["javascript", "js", "function", "var ", "let ", "const ", "=>"],
            "typescript": ["typescript", "ts", "interface", "type ", "enum"],
            "java": ["java", "public class", "private ", "public ", "static"],
            "rust": ["rust", "fn ", "let mut", "impl ", "struct"],
            "go": ["golang", "go", "func ", "package ", "import"],
            "cpp": ["c++", "cpp", "#include", "std::", "namespace"],
            "csharp": ["c#", "csharp", "using ", "namespace ", "public class"]
        }
        
        for language, indicators in language_indicators.items():
            if any(indicator in content for indicator in indicators):
                return language
        
        return "unknown"
    
    async def _detect_domain(self, request: RoutingRequest) -> str:
        """檢測領域"""
        content = request.content.lower()
        
        domain_keywords = {
            "web_development": ["web", "html", "css", "frontend", "backend", "api", "rest"],
            "data_science": ["data", "analysis", "machine learning", "ai", "pandas", "numpy"],
            "mobile_development": ["mobile", "android", "ios", "react native", "flutter"],
            "devops": ["docker", "kubernetes", "ci/cd", "deployment", "infrastructure"],
            "database": ["database", "sql", "nosql", "mongodb", "postgresql", "mysql"],
            "testing": ["test", "testing", "unit test", "integration", "qa"],
            "security": ["security", "authentication", "authorization", "encryption", "vulnerability"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in content for keyword in keywords):
                return domain
        
        return "general"
    
    async def _extract_keywords(self, request: RoutingRequest) -> List[str]:
        """提取關鍵詞"""
        content = request.content.lower()
        words = re.findall(r'\b\w+\b', content)
        
        # 過濾停用詞
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "have",
            "has", "had", "do", "does", "did", "will", "would", "could", "should",
            "我", "你", "他", "她", "它", "我們", "你們", "他們", "的", "了", "在", "是"
        }
        
        # 統計詞頻
        word_count = defaultdict(int)
        for word in words:
            if len(word) > 2 and word not in stop_words:
                word_count[word] += 1
        
        # 返回最常見的關鍵詞
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:10]]

class LoadBalancer:
    """負載均衡器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.component_loads = defaultdict(float)
        self.component_queues = defaultdict(int)
        self.load_history = defaultdict(lambda: deque(maxlen=100))
        
    def get_component_load(self, component_type: ComponentType, component_id: str) -> float:
        """獲取組件負載"""
        key = f"{component_type.value}_{component_id}"
        return self.component_loads.get(key, 0.0)
    
    def update_component_load(self, component_type: ComponentType, component_id: str, load: float):
        """更新組件負載"""
        key = f"{component_type.value}_{component_id}"
        self.component_loads[key] = load
        self.load_history[key].append((datetime.now(), load))
    
    def get_least_loaded_component(self, components: List[ComponentProfile]) -> Optional[ComponentProfile]:
        """獲取負載最低的組件"""
        if not components:
            return None
        
        min_load = float('inf')
        selected_component = None
        
        for component in components:
            current_load = self.get_component_load(component.component_type, component.component_id)
            adjusted_load = current_load + (component.current_load * 0.5)  # 考慮組件自身負載
            
            if adjusted_load < min_load:
                min_load = adjusted_load
                selected_component = component
        
        return selected_component
    
    def predict_processing_time(self, component: ComponentProfile, request_complexity: float) -> float:
        """預測處理時間"""
        base_time = component.average_response_time
        load_factor = 1.0 + component.current_load
        complexity_factor = 1.0 + request_complexity
        
        return base_time * load_factor * complexity_factor

class ContextRouter:
    """上下文路由器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = "Context Router"
        self.version = "1.0.0"
        
        # 初始化子組件
        self.analyzer = RequestAnalyzer(self.config.get("analyzer", {}))
        self.load_balancer = LoadBalancer(self.config.get("load_balancer", {}))
        
        # 組件註冊表
        self.components = {}  # component_id -> ComponentProfile
        self.component_handlers = {}  # component_id -> handler_function
        
        # 路由策略
        self.default_strategy = RoutingStrategy(
            self.config.get("default_strategy", "balanced")
        )
        
        # 配置參數
        self.max_fallback_attempts = self.config.get("max_fallback_attempts", 3)
        self.routing_timeout = self.config.get("routing_timeout", 5.0)
        self.enable_caching = self.config.get("enable_caching", True)
        self.cache_ttl = self.config.get("cache_ttl", 300)
        
        # 路由緩存
        self.routing_cache = {}
        
        # 統計信息
        self.stats = {
            "total_requests": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_routing_time": 0.0,
            "strategy_usage": {strategy.value: 0 for strategy in RoutingStrategy},
            "component_usage": defaultdict(int)
        }
        
        # 狀態管理
        self.initialized = False
        self.status = "initializing"
        
        logger.info(f"Initializing {self.name} v{self.version}")
    
    async def initialize(self):
        """初始化路由器"""
        try:
            logger.info("Initializing Context Router...")
            
            # 註冊默認組件配置
            await self._register_default_components()
            
            self.initialized = True
            self.status = "ready"
            
            logger.info(f"🎉 {self.name} initialization completed with {len(self.components)} components")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.name}: {e}")
            self.status = "error"
            return False
    
    async def _register_default_components(self):
        """註冊默認組件"""
        # RAG 引擎
        rag_profile = ComponentProfile(
            component_type=ComponentType.RAG_ENGINE,
            component_id="universal_rag",
            capabilities=[
                RequestType.CODE_ANALYSIS,
                RequestType.DOCUMENTATION,
                RequestType.GENERAL_QUERY,
                RequestType.PROJECT_ANALYSIS
            ],
            performance_score=0.8,
            quality_score=0.9,
            cost_score=0.7,
            specializations=["semantic_search", "code_retrieval", "documentation"]
        )
        await self.register_component(rag_profile)
        
        # LSP 適配器
        lsp_profile = ComponentProfile(
            component_type=ComponentType.LSP_ADAPTER,
            component_id="universal_lsp",
            capabilities=[
                RequestType.SYMBOL_LOOKUP,
                RequestType.PROJECT_ANALYSIS,
                RequestType.CODE_ANALYSIS,
                RequestType.REFACTORING
            ],
            performance_score=0.9,
            quality_score=0.95,
            cost_score=0.8,
            specializations=["project_analysis", "symbol_resolution", "code_navigation"]
        )
        await self.register_component(lsp_profile)
        
        # 對話管理器
        dialogue_profile = ComponentProfile(
            component_type=ComponentType.DIALOGUE_MANAGER,
            component_id="dialogue_context",
            capabilities=[
                RequestType.CONVERSATION,
                RequestType.GENERAL_QUERY
            ],
            performance_score=0.9,
            quality_score=0.8,
            cost_score=0.9,
            specializations=["conversation", "context_management", "session_handling"]
        )
        await self.register_component(dialogue_profile)
        
        # KiloCode 客戶端
        kilocode_profile = ComponentProfile(
            component_type=ComponentType.KILOCODE_CLIENT,
            component_id="kilocode_integration",
            capabilities=[
                RequestType.CODE_GENERATION,
                RequestType.CODE_ANALYSIS,
                RequestType.REFACTORING
            ],
            performance_score=0.7,
            quality_score=0.95,
            cost_score=0.6,
            specializations=["high_quality_code", "complex_generation", "enterprise_patterns"]
        )
        await self.register_component(kilocode_profile)
    
    async def register_component(self, component: ComponentProfile, 
                               handler: Callable = None):
        """註冊組件"""
        component_id = component.component_id
        self.components[component_id] = component
        
        if handler:
            self.component_handlers[component_id] = handler
        
        logger.info(f"Registered component: {component_id} ({component.component_type.value})")
    
    async def unregister_component(self, component_id: str):
        """註銷組件"""
        if component_id in self.components:
            del self.components[component_id]
        
        if component_id in self.component_handlers:
            del self.component_handlers[component_id]
        
        logger.info(f"Unregistered component: {component_id}")
    
    async def route_request(self, request: RoutingRequest, 
                           strategy: RoutingStrategy = None) -> RoutingDecision:
        """路由請求"""
        if not self.initialized:
            raise RuntimeError("Context Router not initialized")
        
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        try:
            strategy = strategy or self.default_strategy
            self.stats["strategy_usage"][strategy.value] += 1
            
            # 檢查緩存
            cache_key = self._generate_cache_key(request, strategy)
            if self.enable_caching and cache_key in self.routing_cache:
                cached_decision = self.routing_cache[cache_key]
                if datetime.now() - cached_decision.timestamp < timedelta(seconds=self.cache_ttl):
                    self.stats["cache_hits"] += 1
                    logger.debug(f"Cache hit for request {request.request_id}")
                    return cached_decision
            
            self.stats["cache_misses"] += 1
            
            # 分析請求
            analysis = await self.analyzer.analyze_request(request)
            
            # 選擇候選組件
            candidates = await self._select_candidates(request, analysis)
            
            if not candidates:
                raise RuntimeError(f"No suitable components found for request type: {request.request_type}")
            
            # 應用路由策略
            decision = await self._apply_routing_strategy(
                request, analysis, candidates, strategy
            )
            
            # 緩存決策
            if self.enable_caching:
                self.routing_cache[cache_key] = decision
            
            # 更新統計
            self.stats["successful_routes"] += 1
            routing_time = time.time() - start_time
            self.stats["average_routing_time"] = (
                (self.stats["average_routing_time"] * (self.stats["successful_routes"] - 1) + routing_time)
                / self.stats["successful_routes"]
            )
            
            # 更新組件使用統計
            for component_type, component_id in decision.selected_components:
                self.stats["component_usage"][component_id] += 1
            
            logger.info(f"Routed request {request.request_id} to {len(decision.selected_components)} components in {routing_time:.3f}s")
            return decision
            
        except Exception as e:
            logger.error(f"Error routing request {request.request_id}: {e}")
            self.stats["failed_routes"] += 1
            
            # 返回默認路由決策
            return RoutingDecision(
                request_id=request.request_id,
                selected_components=[],
                routing_strategy=strategy,
                confidence_score=0.0,
                estimated_processing_time=0.0,
                estimated_quality=0.0,
                routing_metadata={"error": str(e)}
            )
    
    async def _select_candidates(self, request: RoutingRequest, 
                               analysis: Dict[str, Any]) -> List[ComponentProfile]:
        """選擇候選組件"""
        candidates = []
        detected_type = analysis.get("detected_type", request.request_type)
        
        for component in self.components.values():
            # 檢查能力匹配
            if detected_type in component.capabilities:
                candidates.append(component)
            # 檢查專業化匹配
            elif any(spec in analysis.get("keywords", []) for spec in component.specializations):
                candidates.append(component)
        
        # 按質量分數排序
        candidates.sort(key=lambda c: c.quality_score, reverse=True)
        
        return candidates
    
    async def _apply_routing_strategy(self, request: RoutingRequest, 
                                    analysis: Dict[str, Any],
                                    candidates: List[ComponentProfile],
                                    strategy: RoutingStrategy) -> RoutingDecision:
        """應用路由策略"""
        if strategy == RoutingStrategy.PERFORMANCE_FIRST:
            return await self._performance_first_routing(request, analysis, candidates)
        elif strategy == RoutingStrategy.QUALITY_FIRST:
            return await self._quality_first_routing(request, analysis, candidates)
        elif strategy == RoutingStrategy.COST_OPTIMIZED:
            return await self._cost_optimized_routing(request, analysis, candidates)
        elif strategy == RoutingStrategy.SPECIALIZED:
            return await self._specialized_routing(request, analysis, candidates)
        else:  # BALANCED
            return await self._balanced_routing(request, analysis, candidates)
    
    async def _performance_first_routing(self, request: RoutingRequest,
                                       analysis: Dict[str, Any],
                                       candidates: List[ComponentProfile]) -> RoutingDecision:
        """性能優先路由"""
        # 選擇性能最好且負載最低的組件
        best_component = self.load_balancer.get_least_loaded_component(candidates)
        
        if not best_component:
            best_component = max(candidates, key=lambda c: c.performance_score)
        
        estimated_time = self.load_balancer.predict_processing_time(
            best_component, analysis.get("complexity", 0.5)
        )
        
        return RoutingDecision(
            request_id=request.request_id,
            selected_components=[(best_component.component_type, best_component.component_id)],
            routing_strategy=RoutingStrategy.PERFORMANCE_FIRST,
            confidence_score=0.8,
            estimated_processing_time=estimated_time,
            estimated_quality=best_component.quality_score,
            fallback_components=[(c.component_type, c.component_id) for c in candidates[1:3]],
            routing_metadata={"selection_criteria": "performance_and_load"}
        )
    
    async def _quality_first_routing(self, request: RoutingRequest,
                                   analysis: Dict[str, Any],
                                   candidates: List[ComponentProfile]) -> RoutingDecision:
        """質量優先路由"""
        # 選擇質量最高的組件
        best_component = max(candidates, key=lambda c: c.quality_score)
        
        estimated_time = self.load_balancer.predict_processing_time(
            best_component, analysis.get("complexity", 0.5)
        )
        
        return RoutingDecision(
            request_id=request.request_id,
            selected_components=[(best_component.component_type, best_component.component_id)],
            routing_strategy=RoutingStrategy.QUALITY_FIRST,
            confidence_score=0.9,
            estimated_processing_time=estimated_time,
            estimated_quality=best_component.quality_score,
            fallback_components=[(c.component_type, c.component_id) for c in candidates[1:3]],
            routing_metadata={"selection_criteria": "quality_score"}
        )
    
    async def _cost_optimized_routing(self, request: RoutingRequest,
                                    analysis: Dict[str, Any],
                                    candidates: List[ComponentProfile]) -> RoutingDecision:
        """成本優化路由"""
        # 選擇成本效益最好的組件
        best_component = max(candidates, key=lambda c: c.cost_score)
        
        estimated_time = self.load_balancer.predict_processing_time(
            best_component, analysis.get("complexity", 0.5)
        )
        
        return RoutingDecision(
            request_id=request.request_id,
            selected_components=[(best_component.component_type, best_component.component_id)],
            routing_strategy=RoutingStrategy.COST_OPTIMIZED,
            confidence_score=0.7,
            estimated_processing_time=estimated_time,
            estimated_quality=best_component.quality_score,
            fallback_components=[(c.component_type, c.component_id) for c in candidates[1:3]],
            routing_metadata={"selection_criteria": "cost_efficiency"}
        )
    
    async def _specialized_routing(self, request: RoutingRequest,
                                 analysis: Dict[str, Any],
                                 candidates: List[ComponentProfile]) -> RoutingDecision:
        """專業化路由"""
        # 選擇最匹配專業化的組件
        keywords = analysis.get("keywords", [])
        domain = analysis.get("domain", "general")
        
        scored_candidates = []
        for candidate in candidates:
            specialization_score = 0
            
            # 檢查專業化匹配
            for spec in candidate.specializations:
                if spec in keywords or spec == domain:
                    specialization_score += 1
            
            # 檢查領域匹配
            if domain in candidate.specializations:
                specialization_score += 2
            
            scored_candidates.append((candidate, specialization_score))
        
        # 按專業化分數排序
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        best_component = scored_candidates[0][0] if scored_candidates else candidates[0]
        
        estimated_time = self.load_balancer.predict_processing_time(
            best_component, analysis.get("complexity", 0.5)
        )
        
        return RoutingDecision(
            request_id=request.request_id,
            selected_components=[(best_component.component_type, best_component.component_id)],
            routing_strategy=RoutingStrategy.SPECIALIZED,
            confidence_score=0.85,
            estimated_processing_time=estimated_time,
            estimated_quality=best_component.quality_score,
            fallback_components=[(c.component_type, c.component_id) for c in candidates[1:3]],
            routing_metadata={"selection_criteria": "specialization_match"}
        )
    
    async def _balanced_routing(self, request: RoutingRequest,
                              analysis: Dict[str, Any],
                              candidates: List[ComponentProfile]) -> RoutingDecision:
        """平衡路由"""
        # 綜合考慮性能、質量、成本和負載
        scored_candidates = []
        
        for candidate in candidates:
            # 計算綜合分數
            performance_weight = 0.3
            quality_weight = 0.4
            cost_weight = 0.2
            load_weight = 0.1
            
            current_load = self.load_balancer.get_component_load(
                candidate.component_type, candidate.component_id
            )
            load_score = 1.0 - current_load  # 負載越低分數越高
            
            composite_score = (
                candidate.performance_score * performance_weight +
                candidate.quality_score * quality_weight +
                candidate.cost_score * cost_weight +
                load_score * load_weight
            )
            
            scored_candidates.append((candidate, composite_score))
        
        # 按綜合分數排序
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        best_component = scored_candidates[0][0]
        
        estimated_time = self.load_balancer.predict_processing_time(
            best_component, analysis.get("complexity", 0.5)
        )
        
        return RoutingDecision(
            request_id=request.request_id,
            selected_components=[(best_component.component_type, best_component.component_id)],
            routing_strategy=RoutingStrategy.BALANCED,
            confidence_score=0.8,
            estimated_processing_time=estimated_time,
            estimated_quality=best_component.quality_score,
            fallback_components=[(c.component_type, c.component_id) for c in candidates[1:3]],
            routing_metadata={"selection_criteria": "balanced_score"}
        )
    
    def _generate_cache_key(self, request: RoutingRequest, strategy: RoutingStrategy) -> str:
        """生成緩存鍵"""
        key_data = {
            "request_type": request.request_type.value,
            "content_hash": hashlib.md5(request.content.encode()).hexdigest()[:16],
            "strategy": strategy.value,
            "priority": request.priority
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    async def update_component_performance(self, component_id: str, 
                                         processing_time: float,
                                         success: bool,
                                         quality_score: float = None):
        """更新組件性能指標"""
        if component_id not in self.components:
            return
        
        component = self.components[component_id]
        
        # 更新平均響應時間
        alpha = 0.1  # 學習率
        component.average_response_time = (
            (1 - alpha) * component.average_response_time + 
            alpha * processing_time
        )
        
        # 更新成功率
        component.success_rate = (
            (1 - alpha) * component.success_rate + 
            alpha * (1.0 if success else 0.0)
        )
        
        # 更新質量分數
        if quality_score is not None:
            component.quality_score = (
                (1 - alpha) * component.quality_score + 
                alpha * quality_score
            )
        
        logger.debug(f"Updated performance for component {component_id}")
    
    async def cleanup_cache(self) -> int:
        """清理過期緩存"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, decision in self.routing_cache.items():
            if current_time - decision.timestamp > timedelta(seconds=self.cache_ttl):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.routing_cache[key]
        
        logger.info(f"Cleaned up {len(expired_keys)} expired routing cache entries")
        return len(expired_keys)
    
    def get_status(self) -> Dict[str, Any]:
        """獲取路由器狀態"""
        return {
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "initialized": self.initialized,
            "stats": dict(self.stats),
            "components": {
                comp_id: {
                    "type": comp.component_type.value,
                    "capabilities": [cap.value for cap in comp.capabilities],
                    "performance_score": comp.performance_score,
                    "quality_score": comp.quality_score,
                    "current_load": self.load_balancer.get_component_load(comp.component_type, comp_id)
                }
                for comp_id, comp in self.components.items()
            },
            "cache_stats": {
                "cache_size": len(self.routing_cache),
                "cache_hit_rate": self.stats["cache_hits"] / max(1, self.stats["cache_hits"] + self.stats["cache_misses"])
            }
        }
    
    async def shutdown(self):
        """關閉路由器"""
        logger.info("Shutting down Context Router...")
        
        # 清理緩存
        self.routing_cache.clear()
        
        # 清理組件註冊
        self.components.clear()
        self.component_handlers.clear()
        
        self.status = "shutdown"
        logger.info("Context Router shut down")

# 工廠函數
async def create_context_router(config: Dict[str, Any] = None) -> ContextRouter:
    """創建並初始化上下文路由器"""
    router = ContextRouter(config)
    await router.initialize()
    return router

if __name__ == "__main__":
    # 測試代碼
    async def test_context_router():
        config = {
            "default_strategy": "balanced",
            "enable_caching": True,
            "cache_ttl": 300
        }
        
        router = await create_context_router(config)
        
        # 創建測試請求
        request = RoutingRequest(
            request_id="test-request-001",
            request_type=RequestType.CODE_GENERATION,
            content="Create a Python function to calculate fibonacci numbers",
            priority=7
        )
        
        # 路由請求
        decision = await router.route_request(request)
        print(f"Routing decision: {len(decision.selected_components)} components selected")
        print(f"Confidence: {decision.confidence_score:.2f}")
        print(f"Estimated time: {decision.estimated_processing_time:.2f}s")
        print(f"Selected components: {[comp[1] for comp in decision.selected_components]}")
        
        # 獲取狀態
        status = router.get_status()
        print(f"Router status: {status['status']}")
        print(f"Total requests: {status['stats']['total_requests']}")
        print(f"Registered components: {list(status['components'].keys())}")
        
        # 關閉路由器
        await router.shutdown()
    
    asyncio.run(test_context_router())

