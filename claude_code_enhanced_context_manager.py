#!/usr/bin/env python3
"""
Claude Code Enhanced Context Manager
結合 Claude Code SDK (200K tokens) 與原有 Context Manager 功能
保持與 SmartInvention MCP 的兼容性
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Claude Code SDK 集成
try:
    from anthropic import Anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    logging.warning("Claude SDK not available, falling back to basic mode")

logger = logging.getLogger(__name__)

class ServiceType(Enum):
    """服務類型枚舉"""
    SMART_ROUTING = "smart_routing"
    CODE_GENERATION = "code_generation" 
    CODE_ANALYSIS = "code_analysis"
    TEST_FLOW = "test_flow"
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    CLAUDE_CODE_ENHANCED = "claude_code_enhanced"  # 新增

class ContextScope(Enum):
    """上下文作用域"""
    GLOBAL = "global"
    SYSTEM = "system"
    SERVICE = "service"
    SESSION = "session"
    REQUEST = "request"

@dataclass
class ContextEntry:
    """上下文條目"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    scope: ContextScope = ContextScope.REQUEST
    service_type: ServiceType = ServiceType.SMART_ROUTING
    token_count: int = 0
    priority: int = 1  # 1-10, 10 最高優先級

@dataclass
class ClaudeCodeAnalysisResult:
    """Claude Code 分析結果"""
    analysis: str
    suggestions: List[str]
    code_quality_score: float
    complexity_analysis: Dict[str, Any]
    token_usage: int
    confidence: float

class ClaudeCodeEnhancedContextManager:
    """Claude Code 增強的上下文管理器"""
    
    def __init__(self, 
                 max_context_tokens: int = 200000,  # Claude Code 的 200K 上下文
                 claude_api_key: Optional[str] = None,
                 fallback_max_tokens: int = 8000):  # 原有 Context Manager 的容量
        
        self.max_context_tokens = max_context_tokens
        self.fallback_max_tokens = fallback_max_tokens
        self.context_entries: List[ContextEntry] = []
        self.session_contexts: Dict[str, List[ContextEntry]] = {}
        
        # Claude Code SDK 初始化
        self.claude_client = None
        if CLAUDE_AVAILABLE and claude_api_key:
            try:
                self.claude_client = Anthropic(api_key=claude_api_key)
                logger.info("Claude Code SDK initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Claude SDK: {e}")
                self.claude_client = None
        
        # 統計信息
        self.stats = {
            "total_requests": 0,
            "claude_code_requests": 0,
            "fallback_requests": 0,
            "average_response_time": 0.0,
            "token_usage": 0
        }
    
    def is_claude_code_available(self) -> bool:
        """檢查 Claude Code 是否可用"""
        return self.claude_client is not None
    
    async def add_context(self, 
                         content: str,
                         service_type: ServiceType = ServiceType.SMART_ROUTING,
                         scope: ContextScope = ContextScope.REQUEST,
                         metadata: Optional[Dict[str, Any]] = None,
                         session_id: Optional[str] = None) -> str:
        """添加上下文條目"""
        
        entry = ContextEntry(
            content=content,
            metadata=metadata or {},
            scope=scope,
            service_type=service_type,
            token_count=self._estimate_tokens(content)
        )
        
        # 添加到全局上下文
        self.context_entries.append(entry)
        
        # 添加到會話上下文
        if session_id:
            if session_id not in self.session_contexts:
                self.session_contexts[session_id] = []
            self.session_contexts[session_id].append(entry)
        
        # 管理上下文大小
        await self._manage_context_size()
        
        logger.info(f"Added context entry {entry.id} for service {service_type.value}")
        return entry.id
    
    async def get_context(self, 
                         service_type: ServiceType,
                         scope: Optional[ContextScope] = None,
                         session_id: Optional[str] = None,
                         include_history: bool = True,
                         include_project_context: bool = True) -> Dict[str, Any]:
        """獲取上下文"""
        
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        try:
            # 收集相關上下文
            relevant_contexts = self._collect_relevant_contexts(
                service_type, scope, session_id, include_history, include_project_context
            )
            
            # 如果是代碼相關請求且 Claude Code 可用，使用增強分析
            if (service_type in [ServiceType.CODE_ANALYSIS, ServiceType.CODE_GENERATION, ServiceType.CLAUDE_CODE_ENHANCED] 
                and self.is_claude_code_available()):
                
                result = await self._get_claude_code_enhanced_context(relevant_contexts, service_type)
                self.stats["claude_code_requests"] += 1
                
            else:
                # 使用原有邏輯 (兼容 SmartInvention MCP)
                result = await self._get_standard_context(relevant_contexts, service_type)
                self.stats["fallback_requests"] += 1
            
            # 更新統計
            response_time = time.time() - start_time
            self.stats["average_response_time"] = (
                (self.stats["average_response_time"] * (self.stats["total_requests"] - 1) + response_time) 
                / self.stats["total_requests"]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            # 降級到基本模式
            return await self._get_fallback_context(service_type)
    
    async def _get_claude_code_enhanced_context(self, 
                                              contexts: List[ContextEntry], 
                                              service_type: ServiceType) -> Dict[str, Any]:
        """使用 Claude Code 獲取增強上下文"""
        
        # 構建 Claude Code 分析請求
        context_text = "\n".join([entry.content for entry in contexts])
        
        try:
            # 使用 Claude Code 進行深度分析
            analysis_result = await self._analyze_with_claude_code(context_text, service_type)
            
            return {
                "context_type": "claude_code_enhanced",
                "service_type": service_type.value,
                "max_tokens": self.max_context_tokens,
                "contexts": [
                    {
                        "id": entry.id,
                        "content": entry.content,
                        "metadata": entry.metadata,
                        "timestamp": entry.timestamp.isoformat(),
                        "token_count": entry.token_count
                    } for entry in contexts
                ],
                "claude_analysis": {
                    "analysis": analysis_result.analysis,
                    "suggestions": analysis_result.suggestions,
                    "code_quality_score": analysis_result.code_quality_score,
                    "complexity_analysis": analysis_result.complexity_analysis,
                    "confidence": analysis_result.confidence
                },
                "total_tokens": sum(entry.token_count for entry in contexts) + analysis_result.token_usage,
                "enhanced_capabilities": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Claude Code analysis failed: {e}")
            # 降級到標準模式
            return await self._get_standard_context(contexts, service_type)
    
    async def _analyze_with_claude_code(self, 
                                       context_text: str, 
                                       service_type: ServiceType) -> ClaudeCodeAnalysisResult:
        """使用 Claude Code 進行分析"""
        
        # 構建分析提示
        analysis_prompt = self._build_claude_analysis_prompt(context_text, service_type)
        
        try:
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",  # 使用最新的 Claude 模型
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ]
            )
            
            # 解析 Claude 響應
            analysis_text = response.content[0].text
            
            # 提取結構化信息 (簡化版，實際應該更複雜)
            return ClaudeCodeAnalysisResult(
                analysis=analysis_text,
                suggestions=self._extract_suggestions(analysis_text),
                code_quality_score=self._calculate_quality_score(analysis_text),
                complexity_analysis=self._analyze_complexity(analysis_text),
                token_usage=response.usage.input_tokens + response.usage.output_tokens,
                confidence=0.9  # 簡化版
            )
            
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise
    
    def _build_claude_analysis_prompt(self, context_text: str, service_type: ServiceType) -> str:
        """構建 Claude 分析提示"""
        
        base_prompt = f"""
作為專業的代碼分析專家，請分析以下內容：

服務類型: {service_type.value}
上下文內容:
{context_text}

請提供：
1. 詳細的代碼分析
2. 改進建議
3. 代碼質量評分 (1-10)
4. 複雜度分析
5. 潛在問題識別

請以結構化的方式回應，包含具體的技術建議。
"""
        
        # 根據服務類型定制提示
        if service_type == ServiceType.CODE_GENERATION:
            base_prompt += "\n特別關注代碼生成的最佳實踐和模式。"
        elif service_type == ServiceType.CODE_ANALYSIS:
            base_prompt += "\n特別關注代碼質量、性能和可維護性。"
        elif service_type == ServiceType.REQUIREMENT_ANALYSIS:
            base_prompt += "\n特別關注需求的完整性和可實現性。"
        
        return base_prompt
    
    async def _get_standard_context(self, 
                                   contexts: List[ContextEntry], 
                                   service_type: ServiceType) -> Dict[str, Any]:
        """獲取標準上下文 (兼容原有 Context Manager)"""
        
        return {
            "context_type": "standard",
            "service_type": service_type.value,
            "max_tokens": self.fallback_max_tokens,
            "contexts": [
                {
                    "id": entry.id,
                    "content": entry.content,
                    "metadata": entry.metadata,
                    "timestamp": entry.timestamp.isoformat(),
                    "token_count": entry.token_count
                } for entry in contexts[-10:]  # 限制條目數量
            ],
            "total_tokens": sum(entry.token_count for entry in contexts[-10:]),
            "enhanced_capabilities": False,
            "timestamp": datetime.now().isoformat()
        }
    
    def _collect_relevant_contexts(self, 
                                  service_type: ServiceType,
                                  scope: Optional[ContextScope],
                                  session_id: Optional[str],
                                  include_history: bool,
                                  include_project_context: bool) -> List[ContextEntry]:
        """收集相關上下文"""
        
        relevant_contexts = []
        
        # 收集全局上下文
        for entry in self.context_entries:
            if (entry.service_type == service_type or 
                entry.scope == ContextScope.GLOBAL or
                (scope and entry.scope == scope)):
                relevant_contexts.append(entry)
        
        # 收集會話上下文
        if session_id and session_id in self.session_contexts:
            relevant_contexts.extend(self.session_contexts[session_id])
        
        # 按優先級和時間排序
        relevant_contexts.sort(key=lambda x: (x.priority, x.timestamp), reverse=True)
        
        return relevant_contexts
    
    async def _manage_context_size(self):
        """管理上下文大小"""
        
        total_tokens = sum(entry.token_count for entry in self.context_entries)
        
        if total_tokens > self.max_context_tokens:
            # 移除最舊的低優先級條目
            self.context_entries.sort(key=lambda x: (x.priority, x.timestamp))
            
            while total_tokens > self.max_context_tokens * 0.8:  # 保留 80% 空間
                if self.context_entries:
                    removed = self.context_entries.pop(0)
                    total_tokens -= removed.token_count
                    logger.info(f"Removed context entry {removed.id} to manage size")
                else:
                    break
    
    def _estimate_tokens(self, text: str) -> int:
        """估算 token 數量"""
        # 簡化版估算，實際應該使用 tiktoken
        return len(text.split()) * 1.3  # 粗略估算
    
    def _extract_suggestions(self, analysis_text: str) -> List[str]:
        """從分析文本中提取建議"""
        # 簡化版實現
        lines = analysis_text.split('\n')
        suggestions = []
        for line in lines:
            if '建議' in line or 'suggest' in line.lower():
                suggestions.append(line.strip())
        return suggestions[:5]  # 限制數量
    
    def _calculate_quality_score(self, analysis_text: str) -> float:
        """計算代碼質量評分"""
        # 簡化版實現
        positive_keywords = ['good', 'excellent', 'well', '良好', '優秀']
        negative_keywords = ['bad', 'poor', 'issue', '問題', '錯誤']
        
        positive_count = sum(1 for keyword in positive_keywords if keyword in analysis_text.lower())
        negative_count = sum(1 for keyword in negative_keywords if keyword in analysis_text.lower())
        
        base_score = 7.0
        score = base_score + (positive_count * 0.5) - (negative_count * 0.3)
        return max(1.0, min(10.0, score))
    
    def _analyze_complexity(self, analysis_text: str) -> Dict[str, Any]:
        """分析複雜度"""
        # 簡化版實現
        return {
            "cyclomatic_complexity": "medium",
            "cognitive_complexity": "low",
            "maintainability_index": 75.0,
            "technical_debt": "low"
        }
    
    async def _get_fallback_context(self, service_type: ServiceType) -> Dict[str, Any]:
        """降級上下文"""
        return {
            "context_type": "fallback",
            "service_type": service_type.value,
            "max_tokens": self.fallback_max_tokens,
            "contexts": [],
            "total_tokens": 0,
            "enhanced_capabilities": False,
            "error": "Failed to get enhanced context",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return {
            **self.stats,
            "context_entries_count": len(self.context_entries),
            "session_count": len(self.session_contexts),
            "claude_code_available": self.is_claude_code_available(),
            "max_context_tokens": self.max_context_tokens
        }

# 兼容性接口 (保持與 SmartInvention MCP 的兼容)
class ContextManager(ClaudeCodeEnhancedContextManager):
    """兼容性包裝器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("Context Manager initialized with Claude Code enhancement")

# 測試函數
async def test_claude_code_enhanced_context_manager():
    """測試 Claude Code Enhanced Context Manager"""
    
    manager = ClaudeCodeEnhancedContextManager()
    
    # 添加測試上下文
    await manager.add_context(
        "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
        ServiceType.CODE_ANALYSIS
    )
    
    # 獲取增強上下文
    context = await manager.get_context(ServiceType.CODE_ANALYSIS)
    
    print("Context Manager Test Results:")
    print(f"Context Type: {context['context_type']}")
    print(f"Enhanced Capabilities: {context['enhanced_capabilities']}")
    print(f"Total Tokens: {context['total_tokens']}")
    
    # 統計信息
    stats = manager.get_stats()
    print(f"Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(test_claude_code_enhanced_context_manager())

