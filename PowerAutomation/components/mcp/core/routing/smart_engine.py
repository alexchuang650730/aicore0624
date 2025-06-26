"""
PowerAutomation Local MCP Adapter - 智慧路由功能
Smart Routing Engine Implementation

根據負載和可用性進行智能路由決策
"""

import asyncio
import json
import logging
import time
import statistics
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import random

logger = logging.getLogger(__name__)

class RoutingStrategy(Enum):
    """路由策略枚舉"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"
    RESOURCE_BASED = "resource_based"
    INTELLIGENT = "intelligent"

class ToolHealth(Enum):
    """工具健康狀態"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNAVAILABLE = "unavailable"

class RequestPriority(Enum):
    """請求優先級"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class LoadMetrics:
    """負載指標"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    active_requests: int = 0
    queue_length: int = 0
    response_time_avg: float = 0.0
    response_time_p95: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ToolEndpoint:
    """工具端點"""
    tool_id: str
    endpoint_url: str
    weight: float = 1.0
    max_connections: int = 100
    current_connections: int = 0
    health: ToolHealth = ToolHealth.HEALTHY
    load_metrics: LoadMetrics = field(default_factory=LoadMetrics)
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RoutingRequest:
    """路由請求"""
    request_id: str
    capability_required: str
    priority: RequestPriority = RequestPriority.NORMAL
    timeout: float = 30.0
    retry_count: int = 3
    preferred_tools: List[str] = field(default_factory=list)
    excluded_tools: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RoutingDecision:
    """路由決策"""
    target_tool: str
    target_endpoint: str
    confidence: float
    load_factor: float
    latency_estimate: float
    fallback_options: List[str] = field(default_factory=list)
    decision_reason: str = ""
    routing_strategy: RoutingStrategy = RoutingStrategy.INTELLIGENT
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RoutingResult:
    """路由結果"""
    request_id: str
    decision: RoutingDecision
    execution_time: float
    success: bool
    error_message: str = ""
    response_data: Any = None
    timestamp: datetime = field(default_factory=datetime.now)

class PerformanceTracker:
    """性能追蹤器"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.response_times: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}
        self.request_counts: Dict[str, int] = {}
        self.last_reset = datetime.now()
    
    def record_response_time(self, tool_id: str, response_time: float):
        """記錄響應時間"""
        if tool_id not in self.response_times:
            self.response_times[tool_id] = []
        
        self.response_times[tool_id].append(response_time)
        
        # 保持窗口大小
        if len(self.response_times[tool_id]) > self.window_size:
            self.response_times[tool_id].pop(0)
    
    def record_error(self, tool_id: str):
        """記錄錯誤"""
        self.error_counts[tool_id] = self.error_counts.get(tool_id, 0) + 1
    
    def record_request(self, tool_id: str):
        """記錄請求"""
        self.request_counts[tool_id] = self.request_counts.get(tool_id, 0) + 1
    
    def get_average_response_time(self, tool_id: str) -> float:
        """獲取平均響應時間"""
        if tool_id not in self.response_times or not self.response_times[tool_id]:
            return 0.0
        return statistics.mean(self.response_times[tool_id])
    
    def get_p95_response_time(self, tool_id: str) -> float:
        """獲取95百分位響應時間"""
        if tool_id not in self.response_times or not self.response_times[tool_id]:
            return 0.0
        
        times = sorted(self.response_times[tool_id])
        index = int(len(times) * 0.95)
        return times[min(index, len(times) - 1)]
    
    def get_error_rate(self, tool_id: str) -> float:
        """獲取錯誤率"""
        errors = self.error_counts.get(tool_id, 0)
        requests = self.request_counts.get(tool_id, 0)
        
        if requests == 0:
            return 0.0
        
        return errors / requests
    
    def get_throughput(self, tool_id: str) -> float:
        """獲取吞吐量（請求/秒）"""
        requests = self.request_counts.get(tool_id, 0)
        time_elapsed = (datetime.now() - self.last_reset).total_seconds()
        
        if time_elapsed == 0:
            return 0.0
        
        return requests / time_elapsed
    
    def reset_stats(self):
        """重置統計"""
        self.error_counts.clear()
        self.request_counts.clear()
        self.last_reset = datetime.now()

class LoadBalancer:
    """負載均衡器"""
    
    def __init__(self, strategy: RoutingStrategy = RoutingStrategy.INTELLIGENT):
        self.strategy = strategy
        self.round_robin_index = 0
    
    def select_endpoint(self, endpoints: List[ToolEndpoint], request: RoutingRequest) -> Optional[ToolEndpoint]:
        """選擇端點"""
        if not endpoints:
            return None
        
        # 過濾可用端點
        available_endpoints = [ep for ep in endpoints if ep.health != ToolHealth.UNAVAILABLE]
        
        if not available_endpoints:
            return None
        
        # 根據策略選擇
        if self.strategy == RoutingStrategy.ROUND_ROBIN:
            return self._round_robin_select(available_endpoints)
        elif self.strategy == RoutingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(available_endpoints)
        elif self.strategy == RoutingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(available_endpoints)
        elif self.strategy == RoutingStrategy.LEAST_RESPONSE_TIME:
            return self._least_response_time_select(available_endpoints)
        elif self.strategy == RoutingStrategy.RESOURCE_BASED:
            return self._resource_based_select(available_endpoints)
        elif self.strategy == RoutingStrategy.INTELLIGENT:
            return self._intelligent_select(available_endpoints, request)
        else:
            return available_endpoints[0]
    
    def _round_robin_select(self, endpoints: List[ToolEndpoint]) -> ToolEndpoint:
        """輪詢選擇"""
        endpoint = endpoints[self.round_robin_index % len(endpoints)]
        self.round_robin_index += 1
        return endpoint
    
    def _least_connections_select(self, endpoints: List[ToolEndpoint]) -> ToolEndpoint:
        """最少連接選擇"""
        return min(endpoints, key=lambda ep: ep.current_connections)
    
    def _weighted_round_robin_select(self, endpoints: List[ToolEndpoint]) -> ToolEndpoint:
        """加權輪詢選擇"""
        total_weight = sum(ep.weight for ep in endpoints)
        if total_weight == 0:
            return endpoints[0]
        
        # 生成隨機數選擇
        rand = random.uniform(0, total_weight)
        current_weight = 0
        
        for endpoint in endpoints:
            current_weight += endpoint.weight
            if rand <= current_weight:
                return endpoint
        
        return endpoints[-1]
    
    def _least_response_time_select(self, endpoints: List[ToolEndpoint]) -> ToolEndpoint:
        """最少響應時間選擇"""
        return min(endpoints, key=lambda ep: ep.load_metrics.response_time_avg)
    
    def _resource_based_select(self, endpoints: List[ToolEndpoint]) -> ToolEndpoint:
        """基於資源選擇"""
        def resource_score(ep: ToolEndpoint) -> float:
            # 計算資源分數（越低越好）
            cpu_score = ep.load_metrics.cpu_usage / 100.0
            memory_score = ep.load_metrics.memory_usage / 100.0
            connection_score = ep.current_connections / max(ep.max_connections, 1)
            
            return cpu_score + memory_score + connection_score
        
        return min(endpoints, key=resource_score)
    
    def _intelligent_select(self, endpoints: List[ToolEndpoint], request: RoutingRequest) -> ToolEndpoint:
        """智能選擇"""
        def intelligent_score(ep: ToolEndpoint) -> float:
            # 多維度評分
            scores = []
            
            # 健康狀態分數
            health_scores = {
                ToolHealth.HEALTHY: 1.0,
                ToolHealth.WARNING: 0.7,
                ToolHealth.CRITICAL: 0.3,
                ToolHealth.UNAVAILABLE: 0.0
            }
            scores.append(health_scores[ep.health])
            
            # 負載分數（反向）
            load_score = 1.0 - (ep.load_metrics.cpu_usage / 100.0)
            scores.append(load_score)
            
            # 響應時間分數（反向）
            max_response_time = max((e.load_metrics.response_time_avg for e in endpoints), default=1.0)
            if max_response_time > 0:
                response_score = 1.0 - (ep.load_metrics.response_time_avg / max_response_time)
            else:
                response_score = 1.0
            scores.append(response_score)
            
            # 錯誤率分數（反向）
            error_score = 1.0 - ep.load_metrics.error_rate
            scores.append(error_score)
            
            # 連接數分數（反向）
            connection_score = 1.0 - (ep.current_connections / max(ep.max_connections, 1))
            scores.append(connection_score)
            
            # 優先級調整
            if request.priority == RequestPriority.CRITICAL:
                # 關鍵請求優先考慮健康狀態和響應時間
                weights = [0.4, 0.2, 0.3, 0.05, 0.05]
            elif request.priority == RequestPriority.HIGH:
                weights = [0.3, 0.2, 0.25, 0.15, 0.1]
            else:
                weights = [0.2, 0.25, 0.2, 0.2, 0.15]
            
            # 計算加權分數
            weighted_score = sum(score * weight for score, weight in zip(scores, weights))
            
            # 添加隨機因子避免總是選擇同一個端點
            random_factor = random.uniform(0.95, 1.05)
            
            return weighted_score * random_factor
        
        return max(endpoints, key=intelligent_score)

class CircuitBreaker:
    """熔斷器"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call_allowed(self) -> bool:
        """檢查是否允許調用"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if self.last_failure_time and \
               (datetime.now() - self.last_failure_time).total_seconds() > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        elif self.state == "HALF_OPEN":
            return True
        
        return False
    
    def record_success(self):
        """記錄成功"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """記錄失敗"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

class SmartRoutingEngine:
    """智慧路由引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.default_strategy = RoutingStrategy(config.get('default_strategy', 'intelligent'))
        
        # 核心組件
        self.load_balancer = LoadBalancer(self.default_strategy)
        self.performance_tracker = PerformanceTracker(config.get('performance_window', 100))
        
        # 工具端點管理
        self.tool_endpoints: Dict[str, List[ToolEndpoint]] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # 路由統計
        self.routing_stats = {
            'total_requests': 0,
            'successful_routes': 0,
            'failed_routes': 0,
            'average_decision_time': 0.0,
            'strategy_usage': {strategy.value: 0 for strategy in RoutingStrategy}
        }
        
        # 配置參數
        self.load_threshold = config.get('load_threshold', 0.8)
        self.latency_threshold = config.get('latency_threshold', 1000)  # ms
        self.error_rate_threshold = config.get('error_rate_threshold', 0.1)
        self.failover_enabled = config.get('failover_enabled', True)
        
        # 回調函數
        self.route_callbacks: List[Callable] = []
        
        logger.info(f"智慧路由引擎初始化完成 - 策略: {self.default_strategy.value}")
    
    def add_route_callback(self, callback: Callable):
        """添加路由回調"""
        self.route_callbacks.append(callback)
    
    def register_tool_endpoint(self, tool_id: str, endpoint: ToolEndpoint):
        """註冊工具端點"""
        if tool_id not in self.tool_endpoints:
            self.tool_endpoints[tool_id] = []
        
        self.tool_endpoints[tool_id].append(endpoint)
        
        # 創建熔斷器
        if endpoint.endpoint_url not in self.circuit_breakers:
            self.circuit_breakers[endpoint.endpoint_url] = CircuitBreaker(
                failure_threshold=self.config.get('circuit_breaker_threshold', 5),
                recovery_timeout=self.config.get('circuit_breaker_timeout', 60)
            )
        
        logger.info(f"註冊工具端點: {tool_id} -> {endpoint.endpoint_url}")
    
    def unregister_tool_endpoint(self, tool_id: str, endpoint_url: str):
        """取消註冊工具端點"""
        if tool_id in self.tool_endpoints:
            self.tool_endpoints[tool_id] = [
                ep for ep in self.tool_endpoints[tool_id] 
                if ep.endpoint_url != endpoint_url
            ]
            
            if not self.tool_endpoints[tool_id]:
                del self.tool_endpoints[tool_id]
        
        logger.info(f"取消註冊工具端點: {tool_id} -> {endpoint_url}")
    
    async def route_request(self, request: RoutingRequest) -> RoutingDecision:
        """路由請求"""
        start_time = time.time()
        
        try:
            # 更新統計
            self.routing_stats['total_requests'] += 1
            
            # 查找可用工具
            available_tools = await self._find_available_tools(request.capability_required)
            
            if not available_tools:
                raise Exception(f"沒有可用的工具支持能力: {request.capability_required}")
            
            # 過濾首選和排除的工具
            filtered_tools = self._filter_tools(available_tools, request)
            
            if not filtered_tools:
                # 如果過濾後沒有工具，回退到所有可用工具
                filtered_tools = available_tools
                logger.warning("首選工具不可用，回退到所有可用工具")
            
            # 評估工具負載和可用性
            evaluated_tools = await self._evaluate_tools(filtered_tools)
            
            # 選擇最佳工具
            decision = await self._make_routing_decision(evaluated_tools, request)
            
            # 更新統計
            decision_time = time.time() - start_time
            self._update_routing_stats(decision, decision_time)
            
            # 通知回調
            await self._notify_route_callbacks(request, decision)
            
            logger.debug(f"路由決策完成: {request.request_id} -> {decision.target_tool} ({decision_time:.3f}s)")
            
            return decision
            
        except Exception as e:
            self.routing_stats['failed_routes'] += 1
            logger.error(f"路由請求失敗: {e}")
            raise
    
    async def _find_available_tools(self, capability: str) -> List[str]:
        """查找支持指定能力的可用工具"""
        available_tools = []
        
        for tool_id, endpoints in self.tool_endpoints.items():
            # 檢查是否有端點支持該能力
            for endpoint in endpoints:
                if capability in endpoint.capabilities and endpoint.health != ToolHealth.UNAVAILABLE:
                    # 檢查熔斷器狀態
                    circuit_breaker = self.circuit_breakers.get(endpoint.endpoint_url)
                    if not circuit_breaker or circuit_breaker.call_allowed():
                        available_tools.append(tool_id)
                        break
        
        return available_tools
    
    def _filter_tools(self, tools: List[str], request: RoutingRequest) -> List[str]:
        """過濾工具"""
        filtered = tools.copy()
        
        # 應用首選工具
        if request.preferred_tools:
            preferred = [tool for tool in filtered if tool in request.preferred_tools]
            if preferred:
                filtered = preferred
        
        # 排除指定工具
        if request.excluded_tools:
            filtered = [tool for tool in filtered if tool not in request.excluded_tools]
        
        return filtered
    
    async def _evaluate_tools(self, tools: List[str]) -> List[Tuple[str, float]]:
        """評估工具並返回評分"""
        evaluated = []
        
        for tool_id in tools:
            try:
                score = await self._calculate_tool_score(tool_id)
                evaluated.append((tool_id, score))
            except Exception as e:
                logger.warning(f"評估工具失敗 {tool_id}: {e}")
                evaluated.append((tool_id, 0.0))
        
        # 按分數排序（降序）
        evaluated.sort(key=lambda x: x[1], reverse=True)
        
        return evaluated
    
    async def _calculate_tool_score(self, tool_id: str) -> float:
        """計算工具評分"""
        if tool_id not in self.tool_endpoints:
            return 0.0
        
        endpoints = self.tool_endpoints[tool_id]
        if not endpoints:
            return 0.0
        
        # 計算所有端點的平均分數
        total_score = 0.0
        valid_endpoints = 0
        
        for endpoint in endpoints:
            if endpoint.health == ToolHealth.UNAVAILABLE:
                continue
            
            # 健康狀態分數
            health_scores = {
                ToolHealth.HEALTHY: 1.0,
                ToolHealth.WARNING: 0.7,
                ToolHealth.CRITICAL: 0.3,
                ToolHealth.UNAVAILABLE: 0.0
            }
            health_score = health_scores[endpoint.health]
            
            # 負載分數
            load_score = max(0.0, 1.0 - endpoint.load_metrics.cpu_usage / 100.0)
            
            # 響應時間分數
            response_time_score = max(0.0, 1.0 - endpoint.load_metrics.response_time_avg / self.latency_threshold)
            
            # 錯誤率分數
            error_rate_score = max(0.0, 1.0 - endpoint.load_metrics.error_rate / self.error_rate_threshold)
            
            # 連接數分數
            connection_score = max(0.0, 1.0 - endpoint.current_connections / max(endpoint.max_connections, 1))
            
            # 綜合分數
            endpoint_score = (
                health_score * 0.3 +
                load_score * 0.25 +
                response_time_score * 0.2 +
                error_rate_score * 0.15 +
                connection_score * 0.1
            )
            
            total_score += endpoint_score
            valid_endpoints += 1
        
        if valid_endpoints == 0:
            return 0.0
        
        return total_score / valid_endpoints
    
    async def _make_routing_decision(self, evaluated_tools: List[Tuple[str, float]], request: RoutingRequest) -> RoutingDecision:
        """做出路由決策"""
        if not evaluated_tools:
            raise Exception("沒有可用的工具")
        
        # 選擇最佳工具
        best_tool_id, best_score = evaluated_tools[0]
        
        # 獲取最佳端點
        endpoints = self.tool_endpoints[best_tool_id]
        best_endpoint = self.load_balancer.select_endpoint(endpoints, request)
        
        if not best_endpoint:
            raise Exception(f"工具 {best_tool_id} 沒有可用端點")
        
        # 準備回退選項
        fallback_options = [tool_id for tool_id, _ in evaluated_tools[1:3]]  # 取前2個作為回退
        
        # 估算延遲
        latency_estimate = best_endpoint.load_metrics.response_time_avg
        
        # 計算負載因子
        load_factor = (
            best_endpoint.load_metrics.cpu_usage +
            best_endpoint.load_metrics.memory_usage +
            (best_endpoint.current_connections / max(best_endpoint.max_connections, 1)) * 100
        ) / 3
        
        # 決策原因
        decision_reason = f"選擇 {best_tool_id} (評分: {best_score:.3f}, 負載: {load_factor:.1f}%, 延遲: {latency_estimate:.0f}ms)"
        
        return RoutingDecision(
            target_tool=best_tool_id,
            target_endpoint=best_endpoint.endpoint_url,
            confidence=best_score,
            load_factor=load_factor / 100.0,
            latency_estimate=latency_estimate,
            fallback_options=fallback_options,
            decision_reason=decision_reason,
            routing_strategy=self.default_strategy
        )
    
    def _update_routing_stats(self, decision: RoutingDecision, decision_time: float):
        """更新路由統計"""
        self.routing_stats['successful_routes'] += 1
        
        # 更新平均決策時間
        total_successful = self.routing_stats['successful_routes']
        current_avg = self.routing_stats['average_decision_time']
        self.routing_stats['average_decision_time'] = (
            current_avg * (total_successful - 1) + decision_time
        ) / total_successful
        
        # 更新策略使用統計
        self.routing_stats['strategy_usage'][decision.routing_strategy.value] += 1
    
    async def _notify_route_callbacks(self, request: RoutingRequest, decision: RoutingDecision):
        """通知路由回調"""
        for callback in self.route_callbacks:
            try:
                await callback(request, decision)
            except Exception as e:
                logger.error(f"路由回調執行失敗: {e}")
    
    async def update_tool_metrics(self, tool_id: str, endpoint_url: str, metrics: LoadMetrics):
        """更新工具指標"""
        if tool_id in self.tool_endpoints:
            for endpoint in self.tool_endpoints[tool_id]:
                if endpoint.endpoint_url == endpoint_url:
                    endpoint.load_metrics = metrics
                    
                    # 更新健康狀態
                    endpoint.health = self._calculate_health_status(metrics)
                    break
    
    def _calculate_health_status(self, metrics: LoadMetrics) -> ToolHealth:
        """計算健康狀態"""
        # 檢查各項指標
        issues = 0
        
        if metrics.cpu_usage > self.load_threshold * 100:
            issues += 1
        
        if metrics.memory_usage > self.load_threshold * 100:
            issues += 1
        
        if metrics.response_time_avg > self.latency_threshold:
            issues += 1
        
        if metrics.error_rate > self.error_rate_threshold:
            issues += 2  # 錯誤率權重更高
        
        # 根據問題數量確定健康狀態
        if issues == 0:
            return ToolHealth.HEALTHY
        elif issues <= 1:
            return ToolHealth.WARNING
        elif issues <= 3:
            return ToolHealth.CRITICAL
        else:
            return ToolHealth.UNAVAILABLE
    
    async def record_execution_result(self, tool_id: str, endpoint_url: str, 
                                    execution_time: float, success: bool):
        """記錄執行結果"""
        # 更新性能追蹤
        self.performance_tracker.record_request(tool_id)
        self.performance_tracker.record_response_time(tool_id, execution_time)
        
        if not success:
            self.performance_tracker.record_error(tool_id)
        
        # 更新熔斷器
        circuit_breaker = self.circuit_breakers.get(endpoint_url)
        if circuit_breaker:
            if success:
                circuit_breaker.record_success()
            else:
                circuit_breaker.record_failure()
        
        # 更新端點連接數
        if tool_id in self.tool_endpoints:
            for endpoint in self.tool_endpoints[tool_id]:
                if endpoint.endpoint_url == endpoint_url:
                    endpoint.current_connections = max(0, endpoint.current_connections - 1)
                    break
    
    def get_tool_statistics(self, tool_id: str) -> Dict[str, Any]:
        """獲取工具統計"""
        return {
            'average_response_time': self.performance_tracker.get_average_response_time(tool_id),
            'p95_response_time': self.performance_tracker.get_p95_response_time(tool_id),
            'error_rate': self.performance_tracker.get_error_rate(tool_id),
            'throughput': self.performance_tracker.get_throughput(tool_id),
            'request_count': self.performance_tracker.request_counts.get(tool_id, 0),
            'error_count': self.performance_tracker.error_counts.get(tool_id, 0)
        }
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """獲取路由統計"""
        success_rate = 0.0
        if self.routing_stats['total_requests'] > 0:
            success_rate = (self.routing_stats['successful_routes'] / 
                          self.routing_stats['total_requests']) * 100
        
        return {
            **self.routing_stats,
            'success_rate': success_rate,
            'total_tools': len(self.tool_endpoints),
            'total_endpoints': sum(len(endpoints) for endpoints in self.tool_endpoints.values()),
            'healthy_endpoints': sum(
                len([ep for ep in endpoints if ep.health == ToolHealth.HEALTHY])
                for endpoints in self.tool_endpoints.values()
            )
        }
    
    def get_tool_endpoints_status(self) -> Dict[str, Any]:
        """獲取工具端點狀態"""
        status = {}
        
        for tool_id, endpoints in self.tool_endpoints.items():
            tool_status = {
                'total_endpoints': len(endpoints),
                'endpoints': []
            }
            
            for endpoint in endpoints:
                endpoint_status = {
                    'url': endpoint.endpoint_url,
                    'health': endpoint.health.value,
                    'current_connections': endpoint.current_connections,
                    'max_connections': endpoint.max_connections,
                    'weight': endpoint.weight,
                    'load_metrics': {
                        'cpu_usage': endpoint.load_metrics.cpu_usage,
                        'memory_usage': endpoint.load_metrics.memory_usage,
                        'response_time_avg': endpoint.load_metrics.response_time_avg,
                        'error_rate': endpoint.load_metrics.error_rate,
                        'active_requests': endpoint.load_metrics.active_requests
                    }
                }
                
                # 添加熔斷器狀態
                circuit_breaker = self.circuit_breakers.get(endpoint.endpoint_url)
                if circuit_breaker:
                    endpoint_status['circuit_breaker'] = {
                        'state': circuit_breaker.state,
                        'failure_count': circuit_breaker.failure_count
                    }
                
                tool_status['endpoints'].append(endpoint_status)
            
            status[tool_id] = tool_status
        
        return status

# 創建智慧路由引擎的工廠函數
def create_smart_routing_engine(config: Dict[str, Any]) -> SmartRoutingEngine:
    """創建智慧路由引擎實例"""
    return SmartRoutingEngine(config)

# 導出主要類和函數
__all__ = [
    'SmartRoutingEngine',
    'LoadBalancer',
    'PerformanceTracker',
    'CircuitBreaker',
    'ToolEndpoint',
    'RoutingRequest',
    'RoutingDecision',
    'RoutingResult',
    'LoadMetrics',
    'RoutingStrategy',
    'ToolHealth',
    'RequestPriority',
    'create_smart_routing_engine'
]

