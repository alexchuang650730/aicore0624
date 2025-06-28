"""
Domain MCP Registry - 領域MCP註冊表核心實現
"""

import asyncio
import hashlib
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
from abc import ABC, abstractmethod
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

@dataclass
class DomainInfo:
    """領域信息"""
    domain_id: str
    domain_name: str
    capabilities: List[str]
    confidence_threshold: float = 0.6
    keywords: List[str] = field(default_factory=list)
    description: str = ""
    max_processing_time: int = 30
    cache_enabled: bool = True

@dataclass
class DomainMatch:
    """領域匹配結果"""
    domain_id: str
    confidence: float
    mcp_instance: Any
    match_reasons: List[str] = field(default_factory=list)

@dataclass
class DomainResult:
    """領域處理結果"""
    domain_id: str
    result_type: str
    content: Any
    confidence: float
    processing_time: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

@dataclass
class Conflict:
    """結果衝突"""
    conflict_type: str
    result1: DomainResult
    result2: DomainResult
    severity: float
    description: str

class BaseDomainMCP(ABC):
    """Domain MCP基礎類"""
    
    def __init__(self, domain_id: str, domain_name: str, capabilities: List[str], confidence_threshold: float = 0.6):
        self.domain_id = domain_id
        self.domain_name = domain_name
        self.capabilities = capabilities
        self.confidence_threshold = confidence_threshold
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'avg_processing_time': 0.0,
            'avg_confidence': 0.0
        }
    
    @abstractmethod
    async def process_domain_request(self, request: str, domain_context: Dict, confidence: float) -> DomainResult:
        """處理領域特定請求"""
        pass
    
    async def health_check(self) -> bool:
        """健康檢查"""
        return True
    
    def update_metrics(self, processing_time: float, confidence: float, success: bool):
        """更新性能指標"""
        self.performance_metrics['total_requests'] += 1
        if success:
            self.performance_metrics['successful_requests'] += 1
        
        # 更新平均處理時間
        total = self.performance_metrics['total_requests']
        current_avg_time = self.performance_metrics['avg_processing_time']
        self.performance_metrics['avg_processing_time'] = (
            (current_avg_time * (total - 1) + processing_time) / total
        )
        
        # 更新平均信心度
        current_avg_conf = self.performance_metrics['avg_confidence']
        self.performance_metrics['avg_confidence'] = (
            (current_avg_conf * (total - 1) + confidence) / total
        )

class DomainRoutingEngine:
    """領域路由引擎"""
    
    def __init__(self):
        self.domain_embeddings = {}
        self.keyword_mappings = {}
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.domain_vectors = {}
        self.is_trained = False
    
    async def train_routing_model(self, domain_infos: Dict[str, DomainInfo]):
        """訓練路由模型"""
        logger.info("開始訓練Domain路由模型...")
        
        # 準備訓練數據
        domain_texts = []
        domain_ids = []
        
        for domain_id, info in domain_infos.items():
            # 組合領域描述文本
            domain_text = f"{info.description} {' '.join(info.capabilities)} {' '.join(info.keywords)}"
            domain_texts.append(domain_text)
            domain_ids.append(domain_id)
            
            # 構建關鍵詞映射
            self.keyword_mappings[domain_id] = {}
            for keyword in info.keywords:
                self.keyword_mappings[domain_id][keyword.lower()] = 1.0
            
            for capability in info.capabilities:
                for word in capability.lower().split():
                    self.keyword_mappings[domain_id][word] = 0.8
        
        # 訓練TF-IDF向量化器
        if domain_texts:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(domain_texts)
            
            # 存儲每個領域的向量
            for i, domain_id in enumerate(domain_ids):
                self.domain_vectors[domain_id] = tfidf_matrix[i].toarray()[0]
        
        self.is_trained = True
        logger.info(f"Domain路由模型訓練完成，支持 {len(domain_ids)} 個領域")
    
    async def analyze_domain_relevance(self, request: str) -> Dict[str, float]:
        """分析請求的領域相關性"""
        if not self.is_trained:
            logger.warning("路由模型未訓練，返回空結果")
            return {}
        
        # 1. 關鍵詞分析
        keyword_scores = await self._analyze_keywords(request)
        
        # 2. TF-IDF語義分析
        tfidf_scores = await self._analyze_tfidf_similarity(request)
        
        # 3. 綜合評分
        final_scores = {}
        all_domains = set(keyword_scores.keys()) | set(tfidf_scores.keys())
        
        for domain_id in all_domains:
            keyword_score = keyword_scores.get(domain_id, 0)
            tfidf_score = tfidf_scores.get(domain_id, 0)
            
            # 加權組合
            final_scores[domain_id] = keyword_score * 0.4 + tfidf_score * 0.6
        
        return final_scores
    
    async def _analyze_keywords(self, request: str) -> Dict[str, float]:
        """關鍵詞分析"""
        scores = {}
        request_lower = request.lower()
        
        for domain_id, keywords in self.keyword_mappings.items():
            score = 0
            matched_keywords = []
            
            for keyword, weight in keywords.items():
                if keyword in request_lower:
                    score += weight
                    matched_keywords.append(keyword)
            
            # 歸一化分數
            if keywords:
                max_possible_score = sum(keywords.values())
                scores[domain_id] = min(score / max_possible_score, 1.0)
            else:
                scores[domain_id] = 0
        
        return scores
    
    async def _analyze_tfidf_similarity(self, request: str) -> Dict[str, float]:
        """TF-IDF語義相似度分析"""
        if not self.domain_vectors:
            return {}
        
        try:
            # 將請求轉換為TF-IDF向量
            request_vector = self.tfidf_vectorizer.transform([request]).toarray()[0]
            
            scores = {}
            for domain_id, domain_vector in self.domain_vectors.items():
                # 計算餘弦相似度
                similarity = cosine_similarity([request_vector], [domain_vector])[0][0]
                scores[domain_id] = max(0, similarity)  # 確保非負
            
            return scores
        
        except Exception as e:
            logger.error(f"TF-IDF分析失敗: {e}")
            return {}

class DomainMCPRegistry:
    """領域MCP註冊表"""
    
    def __init__(self):
        self.domain_mcps = {}
        self.domain_infos = {}
        self.routing_engine = DomainRoutingEngine()
        self.performance_monitor = DomainPerformanceMonitor()
        self.result_cache = DomainResultCache()
        self.parallel_processor = ParallelDomainProcessor()
    
    async def register_domain_mcp(self, domain_info: DomainInfo, mcp_instance: BaseDomainMCP):
        """註冊領域MCP"""
        logger.info(f"註冊Domain MCP: {domain_info.domain_id} - {domain_info.domain_name}")
        
        self.domain_mcps[domain_info.domain_id] = {
            'instance': mcp_instance,
            'info': domain_info,
            'registered_at': time.time()
        }
        
        self.domain_infos[domain_info.domain_id] = domain_info
        
        # 重新訓練路由模型
        await self.routing_engine.train_routing_model(self.domain_infos)
        
        logger.info(f"Domain MCP {domain_info.domain_id} 註冊成功")
    
    async def route_request(self, request: str, max_domains: int = 3) -> List[DomainMatch]:
        """智能路由請求到適合的Domain MCP"""
        if not self.domain_mcps:
            return []
        
        # 分析領域相關性
        domain_scores = await self.routing_engine.analyze_domain_relevance(request)
        
        matches = []
        for domain_id, score in domain_scores.items():
            if domain_id in self.domain_mcps:
                domain_info = self.domain_infos[domain_id]
                
                if score >= domain_info.confidence_threshold:
                    matches.append(DomainMatch(
                        domain_id=domain_id,
                        confidence=score,
                        mcp_instance=self.domain_mcps[domain_id]['instance'],
                        match_reasons=[f"相關性分數: {score:.3f}"]
                    ))
        
        # 按信心度排序並限制數量
        matches.sort(key=lambda x: x.confidence, reverse=True)
        return matches[:max_domains]
    
    async def process_request_with_domains(self, request: str, context: Dict = None) -> List[DomainResult]:
        """使用Domain MCP處理請求"""
        # 1. 路由到合適的Domain MCP
        domain_matches = await self.route_request(request)
        
        if not domain_matches:
            logger.info("沒有找到匹配的Domain MCP")
            return []
        
        # 2. 檢查緩存
        request_hash = self._generate_request_hash(request)
        cached_results = []
        uncached_matches = []
        
        for match in domain_matches:
            cached_result = await self.result_cache.get_cached_result(request_hash, match.domain_id)
            if cached_result:
                cached_results.append(cached_result)
            else:
                uncached_matches.append(match)
        
        # 3. 並行處理未緩存的請求
        new_results = []
        if uncached_matches:
            new_results = await self.parallel_processor.process_domains_parallel(
                request, uncached_matches, context or {}
            )
            
            # 緩存新結果
            for result in new_results:
                await self.result_cache.cache_result(request_hash, result.domain_id, result)
        
        # 4. 合併結果
        all_results = cached_results + new_results
        
        # 5. 記錄性能指標
        for result in all_results:
            await self.performance_monitor.record_domain_request(
                result.domain_id,
                result.processing_time,
                result.confidence,
                True
            )
        
        return all_results
    
    def _generate_request_hash(self, request: str) -> str:
        """生成請求哈希"""
        return hashlib.md5(request.encode('utf-8')).hexdigest()
    
    async def get_registry_status(self) -> Dict:
        """獲取註冊表狀態"""
        status = {
            'total_domains': len(self.domain_mcps),
            'domains': {},
            'routing_engine_trained': self.routing_engine.is_trained
        }
        
        for domain_id, domain_data in self.domain_mcps.items():
            instance = domain_data['instance']
            info = domain_data['info']
            
            # 健康檢查
            is_healthy = await instance.health_check()
            
            status['domains'][domain_id] = {
                'name': info.domain_name,
                'capabilities': info.capabilities,
                'confidence_threshold': info.confidence_threshold,
                'is_healthy': is_healthy,
                'performance_metrics': instance.performance_metrics,
                'registered_at': domain_data['registered_at']
            }
        
        return status

class ParallelDomainProcessor:
    """並行領域處理器"""
    
    def __init__(self, max_concurrent_domains: int = 3):
        self.max_concurrent_domains = max_concurrent_domains
        self.semaphore = asyncio.Semaphore(max_concurrent_domains)
    
    async def process_domains_parallel(self, request: str, domain_matches: List[DomainMatch], context: Dict) -> List[DomainResult]:
        """並行處理多個領域"""
        # 限制並發數量
        selected_matches = domain_matches[:self.max_concurrent_domains]
        
        # 創建並行任務
        tasks = []
        for match in selected_matches:
            task = self._process_single_domain(request, match, context)
            tasks.append(task)
        
        # 並行執行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 過濾成功結果
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Domain {selected_matches[i].domain_id} 處理失敗: {result}")
            else:
                successful_results.append(result)
        
        return successful_results
    
    async def _process_single_domain(self, request: str, match: DomainMatch, context: Dict) -> DomainResult:
        """處理單個領域"""
        async with self.semaphore:
            start_time = time.time()
            
            try:
                result = await match.mcp_instance.process_domain_request(
                    request=request,
                    domain_context=context,
                    confidence=match.confidence
                )
                
                processing_time = time.time() - start_time
                result.processing_time = processing_time
                
                # 更新MCP實例的性能指標
                match.mcp_instance.update_metrics(processing_time, match.confidence, True)
                
                return result
                
            except Exception as e:
                processing_time = time.time() - start_time
                match.mcp_instance.update_metrics(processing_time, match.confidence, False)
                raise e

class DomainResultCache:
    """領域結果緩存"""
    
    def __init__(self, cache_ttl: int = 3600):  # 1小時緩存
        self.cache = {}
        self.cache_ttl = cache_ttl
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    async def get_cached_result(self, request_hash: str, domain_id: str) -> Optional[DomainResult]:
        """獲取緩存結果"""
        cache_key = f"{domain_id}:{request_hash}"
        
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            if time.time() - cached_item['timestamp'] < self.cache_ttl:
                self.cache_stats['hits'] += 1
                return cached_item['result']
            else:
                # 緩存過期，刪除
                del self.cache[cache_key]
                self.cache_stats['evictions'] += 1
        
        self.cache_stats['misses'] += 1
        return None
    
    async def cache_result(self, request_hash: str, domain_id: str, result: DomainResult):
        """緩存結果"""
        # 檢查該領域是否啟用緩存
        if hasattr(result, 'cache_enabled') and not result.cache_enabled:
            return
        
        cache_key = f"{domain_id}:{request_hash}"
        self.cache[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }
    
    def get_cache_stats(self) -> Dict:
        """獲取緩存統計"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = self.cache_stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'hit_rate': hit_rate,
            'total_entries': len(self.cache),
            'stats': self.cache_stats
        }

class DomainPerformanceMonitor:
    """Domain MCP性能監控"""
    
    def __init__(self):
        self.metrics = {
            'request_count': defaultdict(int),
            'processing_time': defaultdict(list),
            'confidence_scores': defaultdict(list),
            'success_rate': defaultdict(list),
            'error_count': defaultdict(int)
        }
    
    async def record_domain_request(self, domain_id: str, processing_time: float, confidence: float, success: bool):
        """記錄領域請求指標"""
        self.metrics['request_count'][domain_id] += 1
        self.metrics['processing_time'][domain_id].append(processing_time)
        self.metrics['confidence_scores'][domain_id].append(confidence)
        self.metrics['success_rate'][domain_id].append(1 if success else 0)
        
        if not success:
            self.metrics['error_count'][domain_id] += 1
    
    async def get_domain_statistics(self, domain_id: str) -> Dict:
        """獲取領域統計信息"""
        if domain_id not in self.metrics['request_count']:
            return {}
        
        processing_times = self.metrics['processing_time'][domain_id]
        confidence_scores = self.metrics['confidence_scores'][domain_id]
        success_rates = self.metrics['success_rate'][domain_id]
        
        return {
            'total_requests': self.metrics['request_count'][domain_id],
            'avg_processing_time': sum(processing_times) / len(processing_times) if processing_times else 0,
            'max_processing_time': max(processing_times) if processing_times else 0,
            'min_processing_time': min(processing_times) if processing_times else 0,
            'avg_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            'success_rate': sum(success_rates) / len(success_rates) if success_rates else 0,
            'error_count': self.metrics['error_count'][domain_id],
            'error_rate': self.metrics['error_count'][domain_id] / self.metrics['request_count'][domain_id]
        }
    
    async def get_overall_statistics(self) -> Dict:
        """獲取整體統計信息"""
        all_stats = {}
        for domain_id in self.metrics['request_count'].keys():
            all_stats[domain_id] = await self.get_domain_statistics(domain_id)
        
        # 計算整體指標
        total_requests = sum(self.metrics['request_count'].values())
        total_errors = sum(self.metrics['error_count'].values())
        
        return {
            'domains': all_stats,
            'overall': {
                'total_requests': total_requests,
                'total_errors': total_errors,
                'overall_error_rate': total_errors / total_requests if total_requests > 0 else 0,
                'active_domains': len(all_stats)
            }
        }

