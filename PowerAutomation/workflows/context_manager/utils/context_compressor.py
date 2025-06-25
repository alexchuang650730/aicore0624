#!/usr/bin/env python3
"""
Context Compressor
上下文壓縮器

智能壓縮和優化上下文數據，確保在 token 限制內提供最相關和最重要的信息
支持多種壓縮策略：重要性排序、語義聚類、摘要生成、動態截斷等
"""

import asyncio
import json
import logging
import time
import hashlib
import re
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from collections import defaultdict, Counter
import math

logger = logging.getLogger(__name__)

class CompressionStrategy(Enum):
    """壓縮策略"""
    IMPORTANCE_BASED = "importance_based"      # 基於重要性
    SEMANTIC_CLUSTERING = "semantic_clustering" # 語義聚類
    SUMMARIZATION = "summarization"            # 摘要生成
    DYNAMIC_TRUNCATION = "dynamic_truncation"  # 動態截斷
    HYBRID = "hybrid"                          # 混合策略

class ContentType(Enum):
    """內容類型"""
    CODE = "code"
    DOCUMENTATION = "documentation"
    CONVERSATION = "conversation"
    METADATA = "metadata"
    STRUCTURE = "structure"
    REFERENCE = "reference"

@dataclass
class ContextItem:
    """上下文項目"""
    item_id: str
    content: str
    content_type: ContentType
    importance_score: float = 0.5  # 0-1
    relevance_score: float = 0.5   # 0-1
    token_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # 依賴的其他項目ID
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.token_count == 0:
            self.token_count = len(self.content.split())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "content": self.content,
            "content_type": self.content_type.value,
            "importance_score": self.importance_score,
            "relevance_score": self.relevance_score,
            "token_count": self.token_count,
            "metadata": self.metadata,
            "dependencies": self.dependencies,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class CompressionResult:
    """壓縮結果"""
    original_items: List[ContextItem]
    compressed_items: List[ContextItem]
    original_token_count: int
    compressed_token_count: int
    compression_ratio: float
    strategy_used: CompressionStrategy
    quality_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

class ImportanceCalculator:
    """重要性計算器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # 重要性權重
        self.content_type_weights = {
            ContentType.CODE: 0.9,
            ContentType.DOCUMENTATION: 0.7,
            ContentType.CONVERSATION: 0.6,
            ContentType.METADATA: 0.4,
            ContentType.STRUCTURE: 0.8,
            ContentType.REFERENCE: 0.5
        }
        
        # 關鍵詞權重
        self.keyword_weights = {
            "error": 1.5,
            "bug": 1.4,
            "critical": 1.6,
            "important": 1.3,
            "main": 1.2,
            "key": 1.2,
            "primary": 1.2,
            "function": 1.1,
            "class": 1.1,
            "method": 1.1,
            "api": 1.2,
            "interface": 1.2
        }
    
    async def calculate_importance(self, item: ContextItem, 
                                 context: List[ContextItem] = None) -> float:
        """計算項目重要性"""
        importance = 0.5  # 基礎分數
        
        # 內容類型權重
        type_weight = self.content_type_weights.get(item.content_type, 0.5)
        importance *= type_weight
        
        # 內容長度因子
        length_factor = min(1.0, item.token_count / 100)  # 100 tokens 為標準
        importance += length_factor * 0.1
        
        # 關鍵詞分析
        keyword_score = await self._analyze_keywords(item.content)
        importance += keyword_score * 0.2
        
        # 依賴關係分析
        if context:
            dependency_score = await self._analyze_dependencies(item, context)
            importance += dependency_score * 0.15
        
        # 新鮮度因子
        freshness_score = await self._calculate_freshness(item)
        importance += freshness_score * 0.1
        
        # 相關性因子（如果已設置）
        importance += item.relevance_score * 0.1
        
        return max(0.0, min(1.0, importance))
    
    async def _analyze_keywords(self, content: str) -> float:
        """分析關鍵詞"""
        content_lower = content.lower()
        score = 0.0
        
        for keyword, weight in self.keyword_weights.items():
            if keyword in content_lower:
                score += weight * 0.1
        
        return min(1.0, score)
    
    async def _analyze_dependencies(self, item: ContextItem, 
                                  context: List[ContextItem]) -> float:
        """分析依賴關係"""
        if not item.dependencies:
            return 0.0
        
        # 計算被依賴的程度
        dependency_count = 0
        for other_item in context:
            if item.item_id in other_item.dependencies:
                dependency_count += 1
        
        # 被依賴越多，重要性越高
        return min(1.0, dependency_count * 0.2)
    
    async def _calculate_freshness(self, item: ContextItem) -> float:
        """計算新鮮度"""
        age = datetime.now() - item.timestamp
        age_hours = age.total_seconds() / 3600
        
        # 24小時內為最新，之後逐漸衰減
        if age_hours <= 24:
            return 1.0
        elif age_hours <= 168:  # 一週內
            return 1.0 - (age_hours - 24) / 144
        else:
            return 0.1  # 最低新鮮度

class SemanticClustering:
    """語義聚類"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.similarity_threshold = self.config.get("similarity_threshold", 0.7)
        
    async def cluster_items(self, items: List[ContextItem]) -> List[List[ContextItem]]:
        """聚類項目"""
        if not items:
            return []
        
        clusters = []
        processed = set()
        
        for i, item in enumerate(items):
            if item.item_id in processed:
                continue
            
            # 創建新聚類
            cluster = [item]
            processed.add(item.item_id)
            
            # 尋找相似項目
            for j, other_item in enumerate(items[i+1:], i+1):
                if other_item.item_id in processed:
                    continue
                
                similarity = await self._calculate_similarity(item, other_item)
                if similarity >= self.similarity_threshold:
                    cluster.append(other_item)
                    processed.add(other_item.item_id)
            
            clusters.append(cluster)
        
        return clusters
    
    async def _calculate_similarity(self, item1: ContextItem, item2: ContextItem) -> float:
        """計算相似度"""
        # 簡化的相似度計算
        
        # 內容類型相似度
        type_similarity = 1.0 if item1.content_type == item2.content_type else 0.5
        
        # 詞匯相似度
        words1 = set(item1.content.lower().split())
        words2 = set(item2.content.lower().split())
        
        if not words1 and not words2:
            word_similarity = 1.0
        elif not words1 or not words2:
            word_similarity = 0.0
        else:
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            word_similarity = intersection / union if union > 0 else 0.0
        
        # 元數據相似度
        metadata_similarity = await self._calculate_metadata_similarity(
            item1.metadata, item2.metadata
        )
        
        # 綜合相似度
        similarity = (
            type_similarity * 0.3 +
            word_similarity * 0.5 +
            metadata_similarity * 0.2
        )
        
        return similarity
    
    async def _calculate_metadata_similarity(self, meta1: Dict[str, Any], 
                                          meta2: Dict[str, Any]) -> float:
        """計算元數據相似度"""
        if not meta1 and not meta2:
            return 1.0
        if not meta1 or not meta2:
            return 0.0
        
        common_keys = set(meta1.keys()).intersection(set(meta2.keys()))
        if not common_keys:
            return 0.0
        
        matches = 0
        for key in common_keys:
            if meta1[key] == meta2[key]:
                matches += 1
        
        return matches / len(common_keys)

class ContentSummarizer:
    """內容摘要器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_summary_ratio = self.config.get("max_summary_ratio", 0.3)  # 最多壓縮到30%
        
    async def summarize_items(self, items: List[ContextItem], 
                            target_tokens: int) -> List[ContextItem]:
        """摘要項目列表"""
        if not items:
            return []
        
        summarized_items = []
        
        for item in items:
            if item.token_count <= target_tokens:
                summarized_items.append(item)
            else:
                # 需要摘要
                summary_item = await self._summarize_single_item(item, target_tokens)
                summarized_items.append(summary_item)
        
        return summarized_items
    
    async def _summarize_single_item(self, item: ContextItem, 
                                   target_tokens: int) -> ContextItem:
        """摘要單個項目"""
        try:
            if item.content_type == ContentType.CODE:
                summary_content = await self._summarize_code(item.content, target_tokens)
            elif item.content_type == ContentType.DOCUMENTATION:
                summary_content = await self._summarize_documentation(item.content, target_tokens)
            elif item.content_type == ContentType.CONVERSATION:
                summary_content = await self._summarize_conversation(item.content, target_tokens)
            else:
                summary_content = await self._generic_summarize(item.content, target_tokens)
            
            # 創建摘要項目
            summary_item = ContextItem(
                item_id=f"{item.item_id}_summary",
                content=summary_content,
                content_type=item.content_type,
                importance_score=item.importance_score,
                relevance_score=item.relevance_score,
                metadata={**item.metadata, "is_summary": True, "original_tokens": item.token_count},
                dependencies=item.dependencies
            )
            
            return summary_item
            
        except Exception as e:
            logger.error(f"Error summarizing item {item.item_id}: {e}")
            # 返回截斷版本
            return await self._truncate_item(item, target_tokens)
    
    async def _summarize_code(self, code: str, target_tokens: int) -> str:
        """摘要代碼"""
        lines = code.split('\n')
        
        # 提取重要部分：函數定義、類定義、重要註釋
        important_lines = []
        for line in lines:
            stripped = line.strip()
            if (stripped.startswith('def ') or 
                stripped.startswith('class ') or
                stripped.startswith('import ') or
                stripped.startswith('from ') or
                stripped.startswith('#') and len(stripped) > 10):
                important_lines.append(line)
        
        # 如果重要行太多，進一步篩選
        summary = '\n'.join(important_lines)
        if len(summary.split()) > target_tokens:
            # 只保留函數和類定義
            essential_lines = [line for line in important_lines 
                             if line.strip().startswith(('def ', 'class '))]
            summary = '\n'.join(essential_lines)
        
        return summary if summary else code[:target_tokens*5]  # 粗略估算字符數
    
    async def _summarize_documentation(self, doc: str, target_tokens: int) -> str:
        """摘要文檔"""
        # 提取標題和重要段落
        lines = doc.split('\n')
        important_lines = []
        
        for line in lines:
            stripped = line.strip()
            # 標題行（以#開頭或全大寫）
            if (stripped.startswith('#') or 
                (stripped.isupper() and len(stripped) > 5) or
                any(keyword in stripped.lower() for keyword in ['important', 'note', 'warning', 'example'])):
                important_lines.append(line)
        
        summary = '\n'.join(important_lines)
        
        # 如果還是太長，截斷
        if len(summary.split()) > target_tokens:
            words = summary.split()[:target_tokens]
            summary = ' '.join(words) + '...'
        
        return summary if summary else doc[:target_tokens*5]
    
    async def _summarize_conversation(self, conversation: str, target_tokens: int) -> str:
        """摘要對話"""
        # 提取關鍵交互
        lines = conversation.split('\n')
        key_exchanges = []
        
        for line in lines:
            stripped = line.strip()
            # 問題和重要回答
            if (stripped.startswith(('Q:', 'A:', 'User:', 'Assistant:')) or
                any(keyword in stripped.lower() for keyword in ['問題', 'question', 'error', 'solution'])):
                key_exchanges.append(line)
        
        summary = '\n'.join(key_exchanges)
        
        if len(summary.split()) > target_tokens:
            words = summary.split()[:target_tokens]
            summary = ' '.join(words) + '...'
        
        return summary if summary else conversation[:target_tokens*5]
    
    async def _generic_summarize(self, content: str, target_tokens: int) -> str:
        """通用摘要"""
        # 簡單的截斷策略，保留開頭和結尾
        words = content.split()
        if len(words) <= target_tokens:
            return content
        
        # 保留前70%和後30%
        front_tokens = int(target_tokens * 0.7)
        back_tokens = target_tokens - front_tokens
        
        front_part = ' '.join(words[:front_tokens])
        back_part = ' '.join(words[-back_tokens:]) if back_tokens > 0 else ''
        
        return f"{front_part}... {back_part}" if back_part else front_part
    
    async def _truncate_item(self, item: ContextItem, target_tokens: int) -> ContextItem:
        """截斷項目"""
        words = item.content.split()[:target_tokens]
        truncated_content = ' '.join(words)
        if len(item.content.split()) > target_tokens:
            truncated_content += '...'
        
        return ContextItem(
            item_id=f"{item.item_id}_truncated",
            content=truncated_content,
            content_type=item.content_type,
            importance_score=item.importance_score * 0.8,  # 略微降低重要性
            relevance_score=item.relevance_score,
            metadata={**item.metadata, "is_truncated": True},
            dependencies=item.dependencies
        )

class ContextCompressor:
    """上下文壓縮器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = "Context Compressor"
        self.version = "1.0.0"
        
        # 初始化子組件
        self.importance_calculator = ImportanceCalculator(self.config.get("importance", {}))
        self.semantic_clustering = SemanticClustering(self.config.get("clustering", {}))
        self.content_summarizer = ContentSummarizer(self.config.get("summarizer", {}))
        
        # 配置參數
        self.default_strategy = CompressionStrategy(
            self.config.get("default_strategy", "hybrid")
        )
        self.min_compression_ratio = self.config.get("min_compression_ratio", 0.1)
        self.max_compression_ratio = self.config.get("max_compression_ratio", 0.8)
        self.preserve_dependencies = self.config.get("preserve_dependencies", True)
        
        # 統計信息
        self.stats = {
            "total_compressions": 0,
            "total_items_processed": 0,
            "total_tokens_saved": 0,
            "average_compression_ratio": 0.0,
            "strategy_usage": {strategy.value: 0 for strategy in CompressionStrategy},
            "content_type_distribution": {ct.value: 0 for ct in ContentType}
        }
        
        # 狀態管理
        self.initialized = False
        self.status = "ready"  # 壓縮器不需要複雜初始化
        
        logger.info(f"Initializing {self.name} v{self.version}")
    
    async def compress_context(self, items: List[ContextItem], 
                             target_tokens: int,
                             strategy: CompressionStrategy = None) -> CompressionResult:
        """壓縮上下文"""
        start_time = time.time()
        strategy = strategy or self.default_strategy
        
        self.stats["total_compressions"] += 1
        self.stats["total_items_processed"] += len(items)
        self.stats["strategy_usage"][strategy.value] += 1
        
        # 統計內容類型分佈
        for item in items:
            self.stats["content_type_distribution"][item.content_type.value] += 1
        
        try:
            original_token_count = sum(item.token_count for item in items)
            
            if original_token_count <= target_tokens:
                # 不需要壓縮
                return CompressionResult(
                    original_items=items,
                    compressed_items=items,
                    original_token_count=original_token_count,
                    compressed_token_count=original_token_count,
                    compression_ratio=1.0,
                    strategy_used=strategy,
                    quality_score=1.0,
                    processing_time=time.time() - start_time
                )
            
            # 應用壓縮策略
            compressed_items = await self._apply_compression_strategy(
                items, target_tokens, strategy
            )
            
            compressed_token_count = sum(item.token_count for item in compressed_items)
            compression_ratio = compressed_token_count / original_token_count if original_token_count > 0 else 1.0
            
            # 計算質量分數
            quality_score = await self._calculate_quality_score(items, compressed_items)
            
            # 更新統計
            tokens_saved = original_token_count - compressed_token_count
            self.stats["total_tokens_saved"] += tokens_saved
            
            # 更新平均壓縮比
            self.stats["average_compression_ratio"] = (
                (self.stats["average_compression_ratio"] * (self.stats["total_compressions"] - 1) + compression_ratio)
                / self.stats["total_compressions"]
            )
            
            result = CompressionResult(
                original_items=items,
                compressed_items=compressed_items,
                original_token_count=original_token_count,
                compressed_token_count=compressed_token_count,
                compression_ratio=compression_ratio,
                strategy_used=strategy,
                quality_score=quality_score,
                metadata={
                    "tokens_saved": tokens_saved,
                    "items_removed": len(items) - len(compressed_items)
                },
                processing_time=time.time() - start_time
            )
            
            logger.info(f"Compressed {len(items)} items ({original_token_count} tokens) to {len(compressed_items)} items ({compressed_token_count} tokens), ratio: {compression_ratio:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error compressing context: {e}")
            # 返回原始項目作為回退
            return CompressionResult(
                original_items=items,
                compressed_items=items,
                original_token_count=sum(item.token_count for item in items),
                compressed_token_count=sum(item.token_count for item in items),
                compression_ratio=1.0,
                strategy_used=strategy,
                quality_score=0.0,
                metadata={"error": str(e)},
                processing_time=time.time() - start_time
            )
    
    async def _apply_compression_strategy(self, items: List[ContextItem],
                                        target_tokens: int,
                                        strategy: CompressionStrategy) -> List[ContextItem]:
        """應用壓縮策略"""
        if strategy == CompressionStrategy.IMPORTANCE_BASED:
            return await self._importance_based_compression(items, target_tokens)
        elif strategy == CompressionStrategy.SEMANTIC_CLUSTERING:
            return await self._semantic_clustering_compression(items, target_tokens)
        elif strategy == CompressionStrategy.SUMMARIZATION:
            return await self._summarization_compression(items, target_tokens)
        elif strategy == CompressionStrategy.DYNAMIC_TRUNCATION:
            return await self._dynamic_truncation_compression(items, target_tokens)
        else:  # HYBRID
            return await self._hybrid_compression(items, target_tokens)
    
    async def _importance_based_compression(self, items: List[ContextItem],
                                          target_tokens: int) -> List[ContextItem]:
        """基於重要性的壓縮"""
        # 計算重要性分數
        for item in items:
            if item.importance_score == 0.5:  # 默認值，需要重新計算
                item.importance_score = await self.importance_calculator.calculate_importance(item, items)
        
        # 按重要性排序
        sorted_items = sorted(items, key=lambda x: x.importance_score, reverse=True)
        
        # 選擇項目直到達到目標token數
        selected_items = []
        current_tokens = 0
        
        for item in sorted_items:
            if current_tokens + item.token_count <= target_tokens:
                selected_items.append(item)
                current_tokens += item.token_count
            elif current_tokens < target_tokens * 0.9:  # 還有10%空間，嘗試摘要
                remaining_tokens = target_tokens - current_tokens
                if remaining_tokens > 20:  # 至少20個token才值得摘要
                    summarized_items = await self.content_summarizer.summarize_items([item], remaining_tokens)
                    if summarized_items:
                        selected_items.extend(summarized_items)
                        current_tokens += sum(si.token_count for si in summarized_items)
                break
        
        return selected_items
    
    async def _semantic_clustering_compression(self, items: List[ContextItem],
                                             target_tokens: int) -> List[ContextItem]:
        """基於語義聚類的壓縮"""
        # 聚類項目
        clusters = await self.semantic_clustering.cluster_items(items)
        
        compressed_items = []
        current_tokens = 0
        
        # 處理每個聚類
        for cluster in clusters:
            if current_tokens >= target_tokens:
                break
            
            # 選擇聚類中最重要的項目
            cluster_sorted = sorted(cluster, key=lambda x: x.importance_score, reverse=True)
            
            # 嘗試添加聚類中的項目
            for item in cluster_sorted:
                if current_tokens + item.token_count <= target_tokens:
                    compressed_items.append(item)
                    current_tokens += item.token_count
                    break  # 每個聚類只選一個代表
        
        return compressed_items
    
    async def _summarization_compression(self, items: List[ContextItem],
                                       target_tokens: int) -> List[ContextItem]:
        """基於摘要的壓縮"""
        # 計算每個項目的目標token數
        total_original_tokens = sum(item.token_count for item in items)
        compression_ratio = target_tokens / total_original_tokens if total_original_tokens > 0 else 1.0
        
        summarized_items = []
        
        for item in items:
            target_item_tokens = max(10, int(item.token_count * compression_ratio))
            summarized = await self.content_summarizer.summarize_items([item], target_item_tokens)
            summarized_items.extend(summarized)
        
        return summarized_items
    
    async def _dynamic_truncation_compression(self, items: List[ContextItem],
                                            target_tokens: int) -> List[ContextItem]:
        """動態截斷壓縮"""
        # 按重要性和相關性的組合分數排序
        def combined_score(item):
            return (item.importance_score * 0.6 + item.relevance_score * 0.4)
        
        sorted_items = sorted(items, key=combined_score, reverse=True)
        
        compressed_items = []
        current_tokens = 0
        
        for item in sorted_items:
            if current_tokens + item.token_count <= target_tokens:
                compressed_items.append(item)
                current_tokens += item.token_count
            else:
                # 嘗試截斷
                remaining_tokens = target_tokens - current_tokens
                if remaining_tokens > 20:
                    truncated_item = await self.content_summarizer._truncate_item(item, remaining_tokens)
                    compressed_items.append(truncated_item)
                    current_tokens += truncated_item.token_count
                break
        
        return compressed_items
    
    async def _hybrid_compression(self, items: List[ContextItem],
                                target_tokens: int) -> List[ContextItem]:
        """混合壓縮策略"""
        # 第一階段：基於重要性初步篩選
        high_importance_items = [item for item in items if item.importance_score > 0.7]
        medium_importance_items = [item for item in items if 0.4 <= item.importance_score <= 0.7]
        low_importance_items = [item for item in items if item.importance_score < 0.4]
        
        compressed_items = []
        current_tokens = 0
        
        # 優先保留高重要性項目
        for item in sorted(high_importance_items, key=lambda x: x.importance_score, reverse=True):
            if current_tokens + item.token_count <= target_tokens:
                compressed_items.append(item)
                current_tokens += item.token_count
        
        # 對中等重要性項目進行摘要
        remaining_tokens = target_tokens - current_tokens
        if remaining_tokens > 0 and medium_importance_items:
            medium_target = int(remaining_tokens * 0.7)  # 分配70%給中等重要性
            summarized_medium = await self.content_summarizer.summarize_items(
                medium_importance_items, medium_target
            )
            
            for item in summarized_medium:
                if current_tokens + item.token_count <= target_tokens:
                    compressed_items.append(item)
                    current_tokens += item.token_count
        
        # 如果還有空間，添加低重要性項目的摘要
        remaining_tokens = target_tokens - current_tokens
        if remaining_tokens > 20 and low_importance_items:
            # 選擇最相關的低重要性項目
            relevant_low_items = sorted(low_importance_items, 
                                      key=lambda x: x.relevance_score, reverse=True)[:3]
            
            for item in relevant_low_items:
                if current_tokens + 20 <= target_tokens:  # 每個至少20 tokens
                    item_target = min(remaining_tokens, item.token_count // 2)
                    if item_target >= 20:
                        summarized = await self.content_summarizer.summarize_items([item], item_target)
                        if summarized:
                            compressed_items.extend(summarized)
                            current_tokens += sum(si.token_count for si in summarized)
                            remaining_tokens = target_tokens - current_tokens
        
        return compressed_items
    
    async def _calculate_quality_score(self, original_items: List[ContextItem],
                                     compressed_items: List[ContextItem]) -> float:
        """計算壓縮質量分數"""
        if not original_items:
            return 1.0
        
        # 重要性保留率
        original_importance = sum(item.importance_score for item in original_items)
        compressed_importance = sum(item.importance_score for item in compressed_items)
        importance_retention = compressed_importance / original_importance if original_importance > 0 else 1.0
        
        # 內容類型多樣性保留
        original_types = set(item.content_type for item in original_items)
        compressed_types = set(item.content_type for item in compressed_items)
        type_retention = len(compressed_types) / len(original_types) if original_types else 1.0
        
        # 依賴關係保留（如果啟用）
        dependency_score = 1.0
        if self.preserve_dependencies:
            dependency_score = await self._calculate_dependency_preservation(original_items, compressed_items)
        
        # 綜合質量分數
        quality_score = (
            importance_retention * 0.5 +
            type_retention * 0.3 +
            dependency_score * 0.2
        )
        
        return max(0.0, min(1.0, quality_score))
    
    async def _calculate_dependency_preservation(self, original_items: List[ContextItem],
                                               compressed_items: List[ContextItem]) -> float:
        """計算依賴關係保留率"""
        compressed_ids = set(item.item_id for item in compressed_items)
        
        preserved_dependencies = 0
        total_dependencies = 0
        
        for item in compressed_items:
            for dep_id in item.dependencies:
                total_dependencies += 1
                if dep_id in compressed_ids:
                    preserved_dependencies += 1
        
        return preserved_dependencies / total_dependencies if total_dependencies > 0 else 1.0
    
    def get_status(self) -> Dict[str, Any]:
        """獲取壓縮器狀態"""
        return {
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "initialized": True,
            "stats": dict(self.stats),
            "config": {
                "default_strategy": self.default_strategy.value,
                "min_compression_ratio": self.min_compression_ratio,
                "max_compression_ratio": self.max_compression_ratio,
                "preserve_dependencies": self.preserve_dependencies
            }
        }
    
    async def shutdown(self):
        """關閉壓縮器"""
        logger.info("Shutting down Context Compressor...")
        self.status = "shutdown"
        logger.info("Context Compressor shut down")

# 工廠函數
async def create_context_compressor(config: Dict[str, Any] = None) -> ContextCompressor:
    """創建上下文壓縮器"""
    compressor = ContextCompressor(config)
    return compressor

if __name__ == "__main__":
    # 測試代碼
    async def test_context_compressor():
        config = {
            "default_strategy": "hybrid",
            "preserve_dependencies": True,
            "min_compression_ratio": 0.1,
            "max_compression_ratio": 0.8
        }
        
        compressor = await create_context_compressor(config)
        
        # 創建測試項目
        test_items = [
            ContextItem(
                item_id="code_1",
                content="def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
                content_type=ContentType.CODE,
                importance_score=0.9,
                relevance_score=0.8
            ),
            ContextItem(
                item_id="doc_1",
                content="This function calculates fibonacci numbers using recursion. It's a classic example but not efficient for large numbers.",
                content_type=ContentType.DOCUMENTATION,
                importance_score=0.6,
                relevance_score=0.7
            ),
            ContextItem(
                item_id="conv_1",
                content="User: How do I optimize this fibonacci function?\nAssistant: You can use dynamic programming or memoization to avoid recalculating the same values.",
                content_type=ContentType.CONVERSATION,
                importance_score=0.7,
                relevance_score=0.9
            )
        ]
        
        # 測試壓縮
        result = await compressor.compress_context(test_items, target_tokens=50)
        
        print(f"Compression result:")
        print(f"  Original items: {len(result.original_items)}")
        print(f"  Compressed items: {len(result.compressed_items)}")
        print(f"  Original tokens: {result.original_token_count}")
        print(f"  Compressed tokens: {result.compressed_token_count}")
        print(f"  Compression ratio: {result.compression_ratio:.2f}")
        print(f"  Quality score: {result.quality_score:.2f}")
        print(f"  Strategy used: {result.strategy_used.value}")
        
        # 獲取狀態
        status = compressor.get_status()
        print(f"Compressor status: {status['stats']}")
        
        # 關閉壓縮器
        await compressor.shutdown()
    
    asyncio.run(test_context_compressor())

