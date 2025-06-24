# -*- coding: utf-8 -*-
"""
統一MCP協同框架 - 核心實現

這個框架解決了所有MCP組件間的硬編碼依賴問題，
實現了動態服務發現、事件驅動協同和配置驅動組合。

作者: Agentic Agent Team
版本: 1.0.0
日期: 2025-06-22
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from pathlib import Path

# ==================== 核心枚舉和數據結構 ====================

class MCPServiceType(Enum):
    """MCP服務類型"""
    DATA_PROCESSOR = "data_processor"      # 數據處理器
    LEARNING_ENGINE = "learning_engine"    # 學習引擎
    RECORDER = "recorder"                  # 錄製器
    CLASSIFIER = "classifier"              # 分類器
    EXECUTOR = "executor"                  # 執行器
    ANALYZER = "analyzer"                  # 分析器
    ADAPTER = "adapter"                    # 適配器

class MCPCapability(Enum):
    """MCP能力標識"""
    # 數據處理能力
    PARSE_REPLAY_DATA = "parse_replay_data"
    PROCESS_WORKFLOW = "process_workflow"
    EXTRACT_FEATURES = "extract_features"
    STANDARDIZE_DATA = "standardize_data"
    
    # 學習能力
    PATTERN_RECOGNITION = "pattern_recognition"
    STRATEGY_OPTIMIZATION = "strategy_optimization"
    RECOMMENDATION = "recommendation"
    FEEDBACK_PROCESSING = "feedback_processing"
    
    # 錄製能力
    WORKFLOW_RECORDING = "workflow_recording"
    SESSION_MANAGEMENT = "session_management"
    QUALITY_ASSESSMENT = "quality_assessment"
    
    # 分類能力
    INTELLIGENT_CLASSIFICATION = "intelligent_classification"
    QUALITY_EVALUATION = "quality_evaluation"
    PATTERN_IDENTIFICATION = "pattern_identification"
    
    # 執行能力
    CODE_EXECUTION = "code_execution"
    TASK_AUTOMATION = "task_automation"
    WORKFLOW_REPLAY = "workflow_replay"

class MCPEventType(Enum):
    """MCP事件類型"""
    SERVICE_REGISTERED = "service_registered"
    SERVICE_STARTED = "service_started"
    SERVICE_STOPPED = "service_stopped"
    SERVICE_ERROR = "service_error"
    
    REQUEST_STARTED = "request_started"
    REQUEST_COMPLETED = "request_completed"
    REQUEST_FAILED = "request_failed"
    
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    
    DATA_PROCESSED = "data_processed"
    LEARNING_COMPLETED = "learning_completed"
    RECOMMENDATION_GENERATED = "recommendation_generated"

@dataclass
class MCPServiceInfo:
    """MCP服務信息"""
    service_id: str
    service_name: str
    service_type: MCPServiceType
    capabilities: List[MCPCapability]
    version: str
    description: str
    instance: Any = None
    dependencies: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    status: str = "inactive"
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)
    request_count: int = 0
    error_count: int = 0

@dataclass
class MCPEvent:
    """MCP事件"""
    event_type: MCPEventType
    event_id: str
    source_service: str
    timestamp: float
    data: Any
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MCPRequest:
    """MCP請求"""
    request_id: str
    capability: MCPCapability
    request_type: str
    data: Any
    context: Dict[str, Any]
    timestamp: float
    source_service: Optional[str] = None
    target_service: Optional[str] = None

@dataclass
class MCPResponse:
    """MCP響應"""
    request_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0
    service_id: str = ""
    timestamp: float = field(default_factory=time.time)

# ==================== 核心接口 ====================

class MCPServiceInterface(ABC):
    """MCP服務統一接口"""
    
    @abstractmethod
    def get_service_info(self) -> MCPServiceInfo:
        """獲取服務信息"""
        pass
    
    @abstractmethod
    async def initialize(self, registry: 'MCPServiceRegistry') -> bool:
        """初始化服務"""
        pass
    
    @abstractmethod
    async def process_request(self, request: MCPRequest) -> MCPResponse:
        """處理請求"""
        pass
    
    @abstractmethod
    async def handle_event(self, event: MCPEvent) -> None:
        """處理事件"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """關閉服務"""
        pass

# ==================== 事件總線 ====================

class MCPEventBus:
    """MCP事件總線"""
    
    def __init__(self):
        self.subscribers: Dict[MCPEventType, List[Callable]] = {}
        self.event_history: List[MCPEvent] = []
        self.max_history = 1000
        self.logger = logging.getLogger(__name__)
    
    def subscribe(self, event_type: MCPEventType, callback: Callable[[MCPEvent], None]) -> None:
        """訂閱事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        self.logger.debug(f"事件訂閱: {event_type.value}")
    
    def unsubscribe(self, event_type: MCPEventType, callback: Callable) -> None:
        """取消訂閱"""
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            self.logger.debug(f"取消事件訂閱: {event_type.value}")
    
    async def publish(self, event: MCPEvent) -> None:
        """發布事件"""
        # 記錄事件歷史
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # 通知訂閱者
        if event.event_type in self.subscribers:
            for callback in self.subscribers[event.event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    self.logger.error(f"事件處理失敗: {event.event_type.value} - {e}")
    
    def get_event_history(self, event_type: Optional[MCPEventType] = None, 
                         limit: int = 100) -> List[MCPEvent]:
        """獲取事件歷史"""
        events = self.event_history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]

# ==================== 依賴解析器 ====================

class MCPDependencyResolver:
    """MCP依賴解析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def resolve_dependencies(self, services: Dict[str, MCPServiceInfo]) -> List[str]:
        """解析服務依賴順序 - 拓撲排序"""
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(service_id: str):
            if service_id in temp_visited:
                raise ValueError(f"檢測到循環依賴: {service_id}")
            
            if service_id not in visited:
                temp_visited.add(service_id)
                
                service_info = services.get(service_id)
                if service_info:
                    for dep in service_info.dependencies:
                        if dep in services:
                            visit(dep)
                
                temp_visited.remove(service_id)
                visited.add(service_id)
                result.append(service_id)
        
        # 處理所有服務
        for service_id in services:
            if service_id not in visited:
                try:
                    visit(service_id)
                except ValueError as e:
                    self.logger.error(f"依賴解析失敗: {e}")
                    # 跳過有循環依賴的服務
                    continue
        
        return result
    
    def validate_dependencies(self, services: Dict[str, MCPServiceInfo]) -> Dict[str, List[str]]:
        """驗證依賴關係"""
        issues = {}
        
        for service_id, service_info in services.items():
            service_issues = []
            
            for dep in service_info.dependencies:
                if dep not in services:
                    service_issues.append(f"缺少依賴服務: {dep}")
            
            if service_issues:
                issues[service_id] = service_issues
        
        return issues

# ==================== 服務選擇器 ====================

class MCPServiceSelector:
    """MCP服務選擇器"""
    
    def __init__(self):
        self.selection_strategies = {
            'round_robin': self._round_robin_select,
            'least_loaded': self._least_loaded_select,
            'fastest_response': self._fastest_response_select,
            'highest_success_rate': self._highest_success_rate_select
        }
        self.round_robin_counters: Dict[MCPCapability, int] = {}
    
    def select_service(self, services: List[MCPServiceInfo], 
                      strategy: str = 'round_robin') -> Optional[MCPServiceInfo]:
        """選擇最佳服務"""
        if not services:
            return None
        
        # 過濾活躍服務
        active_services = [s for s in services if s.status == "active"]
        if not active_services:
            return None
        
        # 應用選擇策略
        selector = self.selection_strategies.get(strategy, self._round_robin_select)
        return selector(active_services)
    
    def _round_robin_select(self, services: List[MCPServiceInfo]) -> MCPServiceInfo:
        """輪詢選擇"""
        if not services:
            return None
        
        # 使用第一個服務的能力作為鍵
        capability = services[0].capabilities[0] if services[0].capabilities else None
        if capability not in self.round_robin_counters:
            self.round_robin_counters[capability] = 0
        
        selected = services[self.round_robin_counters[capability] % len(services)]
        self.round_robin_counters[capability] += 1
        
        return selected
    
    def _least_loaded_select(self, services: List[MCPServiceInfo]) -> MCPServiceInfo:
        """最少負載選擇"""
        return min(services, key=lambda s: s.request_count)
    
    def _fastest_response_select(self, services: List[MCPServiceInfo]) -> MCPServiceInfo:
        """最快響應選擇"""
        # 簡化實現，實際應該基於歷史響應時間
        return min(services, key=lambda s: s.last_active)
    
    def _highest_success_rate_select(self, services: List[MCPServiceInfo]) -> MCPServiceInfo:
        """最高成功率選擇"""
        def success_rate(service: MCPServiceInfo) -> float:
            total = service.request_count
            if total == 0:
                return 1.0  # 新服務給予最高優先級
            return 1.0 - (service.error_count / total)
        
        return max(services, key=success_rate)

# ==================== 核心註冊中心 ====================

class MCPServiceRegistry:
    """MCP服務註冊中心"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.services: Dict[str, MCPServiceInfo] = {}
        self.capability_map: Dict[MCPCapability, List[str]] = {}
        self.event_bus = MCPEventBus()
        self.dependency_resolver = MCPDependencyResolver()
        self.service_selector = MCPServiceSelector()
        self.logger = logging.getLogger(__name__)
        
        # 配置
        self.selection_strategy = self.config.get('selection_strategy', 'round_robin')
        self.health_check_interval = self.config.get('health_check_interval', 60)
        self.max_retry_attempts = self.config.get('max_retry_attempts', 3)
        
        # 啟動健康檢查任務
        self._health_check_task = None
    
    async def start(self) -> None:
        """啟動註冊中心"""
        self.logger.info("🚀 MCP服務註冊中心啟動")
        
        # 啟動健康檢查
        self._health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def stop(self) -> None:
        """停止註冊中心"""
        self.logger.info("🛑 MCP服務註冊中心停止")
        
        # 停止健康檢查
        if self._health_check_task:
            self._health_check_task.cancel()
        
        # 關閉所有服務
        for service_info in self.services.values():
            try:
                await service_info.instance.shutdown()
            except Exception as e:
                self.logger.error(f"服務關閉失敗: {service_info.service_id} - {e}")
    
    def register_service(self, service: MCPServiceInterface) -> bool:
        """註冊MCP服務"""
        try:
            service_info = service.get_service_info()
            service_info.instance = service
            
            # 檢查服務ID唯一性
            if service_info.service_id in self.services:
                self.logger.warning(f"服務 {service_info.service_id} 已存在，將被覆蓋")
            
            # 註冊服務
            self.services[service_info.service_id] = service_info
            
            # 更新能力映射
            for capability in service_info.capabilities:
                if capability not in self.capability_map:
                    self.capability_map[capability] = []
                if service_info.service_id not in self.capability_map[capability]:
                    self.capability_map[capability].append(service_info.service_id)
            
            # 發布註冊事件
            asyncio.create_task(self.event_bus.publish(MCPEvent(
                event_type=MCPEventType.SERVICE_REGISTERED,
                event_id=f"reg_{service_info.service_id}_{int(time.time())}",
                source_service=service_info.service_id,
                timestamp=time.time(),
                data={"service_info": service_info}
            )))
            
            self.logger.info(f"✅ 服務註冊成功: {service_info.service_name} ({service_info.service_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 服務註冊失敗: {e}")
            return False
    
    def unregister_service(self, service_id: str) -> bool:
        """註銷MCP服務"""
        try:
            if service_id not in self.services:
                self.logger.warning(f"服務 {service_id} 不存在")
                return False
            
            service_info = self.services[service_id]
            
            # 從能力映射中移除
            for capability in service_info.capabilities:
                if capability in self.capability_map:
                    if service_id in self.capability_map[capability]:
                        self.capability_map[capability].remove(service_id)
                    if not self.capability_map[capability]:
                        del self.capability_map[capability]
            
            # 移除服務
            del self.services[service_id]
            
            self.logger.info(f"✅ 服務註銷成功: {service_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 服務註銷失敗: {e}")
            return False
    
    def get_services_by_capability(self, capability: MCPCapability) -> List[MCPServiceInfo]:
        """根據能力獲取服務列表"""
        service_ids = self.capability_map.get(capability, [])
        return [self.services[sid] for sid in service_ids if sid in self.services]
    
    def get_service(self, service_id: str) -> Optional[MCPServiceInfo]:
        """獲取指定服務"""
        return self.services.get(service_id)
    
    async def initialize_all_services(self) -> Dict[str, bool]:
        """初始化所有服務"""
        results = {}
        
        # 驗證依賴關係
        dependency_issues = self.dependency_resolver.validate_dependencies(self.services)
        if dependency_issues:
            self.logger.warning(f"發現依賴問題: {dependency_issues}")
        
        # 解析初始化順序
        try:
            init_order = self.dependency_resolver.resolve_dependencies(self.services)
        except Exception as e:
            self.logger.error(f"依賴解析失敗: {e}")
            init_order = list(self.services.keys())  # 回退到簡單順序
        
        # 按順序初始化服務
        for service_id in init_order:
            if service_id not in self.services:
                continue
                
            service_info = self.services[service_id]
            try:
                self.logger.info(f"初始化服務: {service_info.service_name}")
                success = await service_info.instance.initialize(self)
                service_info.status = "active" if success else "failed"
                results[service_id] = success
                
                # 發布事件
                event_type = MCPEventType.SERVICE_STARTED if success else MCPEventType.SERVICE_ERROR
                await self.event_bus.publish(MCPEvent(
                    event_type=event_type,
                    event_id=f"init_{service_id}_{int(time.time())}",
                    source_service=service_id,
                    timestamp=time.time(),
                    data={"success": success}
                ))
                
                if success:
                    self.logger.info(f"✅ 服務初始化成功: {service_info.service_name}")
                else:
                    self.logger.error(f"❌ 服務初始化失敗: {service_info.service_name}")
                    
            except Exception as e:
                self.logger.error(f"❌ 服務初始化異常: {service_info.service_name} - {e}")
                service_info.status = "error"
                results[service_id] = False
        
        return results
    
    async def request_service(self, capability: MCPCapability, request_type: str, 
                            data: Any, context: Dict[str, Any] = None) -> MCPResponse:
        """請求具有指定能力的服務"""
        request_id = f"req_{int(time.time() * 1000)}"
        start_time = time.time()
        
        # 創建請求對象
        request = MCPRequest(
            request_id=request_id,
            capability=capability,
            request_type=request_type,
            data=data,
            context=context or {},
            timestamp=start_time
        )
        
        # 發布請求開始事件
        await self.event_bus.publish(MCPEvent(
            event_type=MCPEventType.REQUEST_STARTED,
            event_id=f"req_start_{request_id}",
            source_service="registry",
            timestamp=start_time,
            data={"request": request}
        ))
        
        try:
            # 獲取可用服務
            services = self.get_services_by_capability(capability)
            if not services:
                raise ValueError(f"沒有找到具有能力 {capability.value} 的服務")
            
            # 選擇最佳服務
            selected_service = self.service_selector.select_service(services, self.selection_strategy)
            if not selected_service or selected_service.status != "active":
                raise RuntimeError(f"沒有可用的服務處理請求: {capability.value}")
            
            # 更新請求信息
            request.target_service = selected_service.service_id
            
            # 執行請求
            response = await selected_service.instance.process_request(request)
            response.execution_time = time.time() - start_time
            response.service_id = selected_service.service_id
            
            # 更新服務統計
            selected_service.request_count += 1
            selected_service.last_active = time.time()
            if not response.success:
                selected_service.error_count += 1
            
            # 發布完成事件
            event_type = MCPEventType.REQUEST_COMPLETED if response.success else MCPEventType.REQUEST_FAILED
            await self.event_bus.publish(MCPEvent(
                event_type=event_type,
                event_id=f"req_end_{request_id}",
                source_service=selected_service.service_id,
                timestamp=time.time(),
                data={"request": request, "response": response}
            ))
            
            return response
            
        except Exception as e:
            # 創建錯誤響應
            error_response = MCPResponse(
                request_id=request_id,
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
            
            # 發布失敗事件
            await self.event_bus.publish(MCPEvent(
                event_type=MCPEventType.REQUEST_FAILED,
                event_id=f"req_fail_{request_id}",
                source_service="registry",
                timestamp=time.time(),
                data={"request": request, "error": str(e)}
            ))
            
            return error_response
    
    async def _health_check_loop(self) -> None:
        """健康檢查循環"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"健康檢查失敗: {e}")
    
    async def _perform_health_checks(self) -> None:
        """執行健康檢查"""
        for service_id, service_info in self.services.items():
            if service_info.status == "active":
                try:
                    health_result = await service_info.instance.health_check()
                    if not health_result.get('healthy', False):
                        service_info.status = "unhealthy"
                        self.logger.warning(f"服務健康檢查失敗: {service_id}")
                except Exception as e:
                    service_info.status = "error"
                    self.logger.error(f"服務健康檢查異常: {service_id} - {e}")
    
    def get_registry_status(self) -> Dict[str, Any]:
        """獲取註冊中心狀態"""
        return {
            "total_services": len(self.services),
            "active_services": len([s for s in self.services.values() if s.status == "active"]),
            "capabilities": len(self.capability_map),
            "total_requests": sum(s.request_count for s in self.services.values()),
            "total_errors": sum(s.error_count for s in self.services.values()),
            "services": {
                sid: {
                    "name": info.service_name,
                    "type": info.service_type.value,
                    "status": info.status,
                    "capabilities": [c.value for c in info.capabilities],
                    "request_count": info.request_count,
                    "error_count": info.error_count,
                    "last_active": info.last_active
                }
                for sid, info in self.services.items()
            }
        }

# ==================== 全局實例 ====================

# 創建全局註冊中心實例
mcp_registry = MCPServiceRegistry()

# 導出主要類和實例
__all__ = [
    'MCPServiceType', 'MCPCapability', 'MCPEventType',
    'MCPServiceInfo', 'MCPEvent', 'MCPRequest', 'MCPResponse',
    'MCPServiceInterface', 'MCPEventBus', 'MCPServiceRegistry',
    'mcp_registry'
]

