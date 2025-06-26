"""
增強服務註冊機制組件
從aicore0620 mcp_coordinator_server.py借鑒集中式註冊表概念
結合動態發現和靜態註冊的優勢
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import uuid

logger = logging.getLogger(__name__)

class ServiceRegistryType(Enum):
    """服務註冊表類型"""
    DYNAMIC = "dynamic"      # 動態發現的服務
    STATIC = "static"        # 靜態配置的服務
    HYBRID = "hybrid"        # 混合模式

class ServiceHealthStatus(Enum):
    """服務健康狀態"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

class ServicePriority(Enum):
    """服務優先級"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

@dataclass
class ServiceEndpoint:
    """服務端點信息"""
    endpoint_id: str
    url: str
    protocol: str = "http"
    port: Optional[int] = None
    path: str = "/"
    health_check_path: str = "/health"
    timeout: float = 30.0
    retry_count: int = 3
    
    def get_full_url(self) -> str:
        """獲取完整URL"""
        if self.port:
            return f"{self.protocol}://{self.url}:{self.port}{self.path}"
        return f"{self.protocol}://{self.url}{self.path}"
    
    def get_health_check_url(self) -> str:
        """獲取健康檢查URL"""
        if self.port:
            return f"{self.protocol}://{self.url}:{self.port}{self.health_check_path}"
        return f"{self.protocol}://{self.url}{self.health_check_path}"

@dataclass
class ServiceMetrics:
    """服務指標"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    uptime: timedelta = field(default_factory=lambda: timedelta(0))
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    
    def get_success_rate(self) -> float:
        """獲取成功率"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

@dataclass
class EnhancedServiceInfo:
    """增強的服務信息"""
    service_id: str
    name: str
    description: str
    service_type: str
    version: str
    registry_type: ServiceRegistryType
    priority: ServicePriority = ServicePriority.NORMAL
    
    # 端點信息
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    primary_endpoint: Optional[ServiceEndpoint] = None
    
    # 能力和配置
    capabilities: List[str] = field(default_factory=list)
    supported_actions: List[str] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    
    # 狀態和健康
    health_status: ServiceHealthStatus = ServiceHealthStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    health_check_interval: int = 30  # 秒
    
    # 指標和統計
    metrics: ServiceMetrics = field(default_factory=ServiceMetrics)
    
    # 註冊信息
    registration_time: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    registered_by: str = ""
    
    # 依賴和關係
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    
    # 元數據
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "service_id": self.service_id,
            "name": self.name,
            "description": self.description,
            "service_type": self.service_type,
            "version": self.version,
            "registry_type": self.registry_type.value,
            "priority": self.priority.value,
            "endpoints": [
                {
                    "endpoint_id": ep.endpoint_id,
                    "url": ep.get_full_url(),
                    "health_check_url": ep.get_health_check_url(),
                    "timeout": ep.timeout,
                    "retry_count": ep.retry_count
                } for ep in self.endpoints
            ],
            "capabilities": self.capabilities,
            "supported_actions": self.supported_actions,
            "health_status": self.health_status.value,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate": self.metrics.get_success_rate(),
                "avg_response_time": self.metrics.avg_response_time,
                "uptime": str(self.metrics.uptime)
            },
            "registration_time": self.registration_time.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "tags": self.tags
        }

class EnhancedServiceRegistry:
    """增強的服務註冊表"""
    
    def __init__(self, registry_id: Optional[str] = None):
        self.registry_id = registry_id or f"registry_{uuid.uuid4().hex[:8]}"
        self.services: Dict[str, EnhancedServiceInfo] = {}
        self.service_groups: Dict[str, List[str]] = {}  # 服務分組
        self.running = False
        
        # 統計信息
        self.stats = {
            "total_services": 0,
            "healthy_services": 0,
            "unhealthy_services": 0,
            "dynamic_services": 0,
            "static_services": 0,
            "last_health_check": None
        }
        
        logger.info(f"增強服務註冊表初始化完成 - ID: {self.registry_id}")
    
    async def start(self):
        """啟動註冊表"""
        if self.running:
            logger.warning("服務註冊表已在運行中")
            return
        
        self.running = True
        logger.info("啟動增強服務註冊表...")
        
        # 啟動健康檢查任務
        asyncio.create_task(self._health_check_loop())
        
        # 啟動統計更新任務
        asyncio.create_task(self._stats_update_loop())
        
        logger.info("增強服務註冊表啟動完成")
    
    async def stop(self):
        """停止註冊表"""
        if not self.running:
            return
        
        self.running = False
        logger.info("停止增強服務註冊表...")
        
        # 等待所有任務完成
        await asyncio.sleep(1)
        
        logger.info("增強服務註冊表已停止")
    
    def register_service(self, service_info: EnhancedServiceInfo) -> bool:
        """註冊服務"""
        try:
            # 檢查服務是否已存在
            if service_info.service_id in self.services:
                logger.warning(f"服務已存在，將更新: {service_info.service_id}")
                return self.update_service(service_info)
            
            # 設置註冊時間
            service_info.registration_time = datetime.now()
            service_info.last_updated = datetime.now()
            
            # 添加到註冊表
            self.services[service_info.service_id] = service_info
            
            # 更新統計
            self._update_stats()
            
            logger.info(f"服務註冊成功: {service_info.name} ({service_info.service_id})")
            return True
            
        except Exception as e:
            logger.error(f"服務註冊失敗: {e}")
            return False
    
    def unregister_service(self, service_id: str) -> bool:
        """取消註冊服務"""
        try:
            if service_id not in self.services:
                logger.warning(f"服務不存在: {service_id}")
                return False
            
            service_name = self.services[service_id].name
            del self.services[service_id]
            
            # 從服務分組中移除
            for group_name, service_list in self.service_groups.items():
                if service_id in service_list:
                    service_list.remove(service_id)
            
            # 更新統計
            self._update_stats()
            
            logger.info(f"服務取消註冊成功: {service_name} ({service_id})")
            return True
            
        except Exception as e:
            logger.error(f"服務取消註冊失敗: {e}")
            return False
    
    def update_service(self, service_info: EnhancedServiceInfo) -> bool:
        """更新服務信息"""
        try:
            if service_info.service_id not in self.services:
                logger.warning(f"服務不存在，將創建新服務: {service_info.service_id}")
                return self.register_service(service_info)
            
            # 保留原有的註冊時間和指標
            existing_service = self.services[service_info.service_id]
            service_info.registration_time = existing_service.registration_time
            service_info.metrics = existing_service.metrics
            service_info.last_updated = datetime.now()
            
            # 更新服務信息
            self.services[service_info.service_id] = service_info
            
            logger.info(f"服務更新成功: {service_info.name} ({service_info.service_id})")
            return True
            
        except Exception as e:
            logger.error(f"服務更新失敗: {e}")
            return False
    
    def get_service(self, service_id: str) -> Optional[EnhancedServiceInfo]:
        """獲取服務信息"""
        return self.services.get(service_id)
    
    def list_services(self, 
                     service_type: Optional[str] = None,
                     registry_type: Optional[ServiceRegistryType] = None,
                     health_status: Optional[ServiceHealthStatus] = None,
                     tags: Optional[List[str]] = None) -> List[EnhancedServiceInfo]:
        """列出服務"""
        services = list(self.services.values())
        
        # 按服務類型過濾
        if service_type:
            services = [s for s in services if s.service_type == service_type]
        
        # 按註冊類型過濾
        if registry_type:
            services = [s for s in services if s.registry_type == registry_type]
        
        # 按健康狀態過濾
        if health_status:
            services = [s for s in services if s.health_status == health_status]
        
        # 按標籤過濾
        if tags:
            services = [s for s in services if any(tag in s.tags for tag in tags)]
        
        return services
    
    def create_service_group(self, group_name: str, service_ids: List[str]) -> bool:
        """創建服務分組"""
        try:
            # 驗證所有服務都存在
            for service_id in service_ids:
                if service_id not in self.services:
                    logger.error(f"服務不存在: {service_id}")
                    return False
            
            self.service_groups[group_name] = service_ids
            logger.info(f"服務分組創建成功: {group_name} ({len(service_ids)} 個服務)")
            return True
            
        except Exception as e:
            logger.error(f"創建服務分組失敗: {e}")
            return False
    
    def get_service_group(self, group_name: str) -> List[EnhancedServiceInfo]:
        """獲取服務分組"""
        if group_name not in self.service_groups:
            return []
        
        service_ids = self.service_groups[group_name]
        return [self.services[sid] for sid in service_ids if sid in self.services]
    
    async def check_service_health(self, service_id: str) -> bool:
        """檢查單個服務健康狀態"""
        service = self.get_service(service_id)
        if not service:
            return False
        
        try:
            # 檢查主要端點
            if service.primary_endpoint:
                health_url = service.primary_endpoint.get_health_check_url()
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        health_url,
                        timeout=aiohttp.ClientTimeout(total=service.primary_endpoint.timeout)
                    ) as response:
                        if response.status == 200:
                            service.health_status = ServiceHealthStatus.HEALTHY
                            service.last_health_check = datetime.now()
                            return True
                        else:
                            service.health_status = ServiceHealthStatus.UNHEALTHY
                            service.last_health_check = datetime.now()
                            return False
            
            # 如果沒有主要端點，檢查所有端點
            for endpoint in service.endpoints:
                health_url = endpoint.get_health_check_url()
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        health_url,
                        timeout=aiohttp.ClientTimeout(total=endpoint.timeout)
                    ) as response:
                        if response.status == 200:
                            service.health_status = ServiceHealthStatus.HEALTHY
                            service.last_health_check = datetime.now()
                            return True
            
            # 所有端點都不健康
            service.health_status = ServiceHealthStatus.UNHEALTHY
            service.last_health_check = datetime.now()
            return False
            
        except Exception as e:
            logger.warning(f"服務健康檢查失敗 {service_id}: {e}")
            service.health_status = ServiceHealthStatus.UNKNOWN
            service.last_health_check = datetime.now()
            return False
    
    async def _health_check_loop(self):
        """健康檢查循環"""
        while self.running:
            try:
                logger.debug("開始服務健康檢查...")
                
                # 並行檢查所有服務
                tasks = []
                for service_id in self.services.keys():
                    task = asyncio.create_task(self.check_service_health(service_id))
                    tasks.append(task)
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                # 更新統計
                self._update_stats()
                self.stats["last_health_check"] = datetime.now().isoformat()
                
                logger.debug("服務健康檢查完成")
                
                # 等待下次檢查
                await asyncio.sleep(30)  # 30秒檢查一次
                
            except Exception as e:
                logger.error(f"健康檢查循環錯誤: {e}")
                await asyncio.sleep(5)
    
    async def _stats_update_loop(self):
        """統計更新循環"""
        while self.running:
            try:
                self._update_stats()
                await asyncio.sleep(60)  # 每分鐘更新一次統計
                
            except Exception as e:
                logger.error(f"統計更新循環錯誤: {e}")
                await asyncio.sleep(10)
    
    def _update_stats(self):
        """更新統計信息"""
        self.stats["total_services"] = len(self.services)
        self.stats["healthy_services"] = len([
            s for s in self.services.values() 
            if s.health_status == ServiceHealthStatus.HEALTHY
        ])
        self.stats["unhealthy_services"] = len([
            s for s in self.services.values() 
            if s.health_status == ServiceHealthStatus.UNHEALTHY
        ])
        self.stats["dynamic_services"] = len([
            s for s in self.services.values() 
            if s.registry_type == ServiceRegistryType.DYNAMIC
        ])
        self.stats["static_services"] = len([
            s for s in self.services.values() 
            if s.registry_type == ServiceRegistryType.STATIC
        ])
    
    def get_registry_status(self) -> Dict[str, Any]:
        """獲取註冊表狀態"""
        return {
            "registry_id": self.registry_id,
            "running": self.running,
            "stats": self.stats,
            "service_groups": {
                group: len(services) for group, services in self.service_groups.items()
            },
            "services": [service.to_dict() for service in self.services.values()]
        }

def create_enhanced_service_registry(registry_id: Optional[str] = None) -> EnhancedServiceRegistry:
    """創建增強服務註冊表實例"""
    return EnhancedServiceRegistry(registry_id)

# 預定義的靜態服務配置
DEFAULT_STATIC_SERVICES = [
    EnhancedServiceInfo(
        service_id="cloud_search_mcp_static",
        name="Cloud Search MCP (Static)",
        description="雲端搜索服務 - 靜態註冊",
        service_type="analysis",
        version="1.0.0",
        registry_type=ServiceRegistryType.STATIC,
        priority=ServicePriority.HIGH,
        endpoints=[
            ServiceEndpoint(
                endpoint_id="cloud_search_primary",
                url="localhost",
                port=8001,
                path="/",
                health_check_path="/health"
            )
        ],
        capabilities=["search", "analysis", "context_enrichment"],
        supported_actions=["search_and_analyze", "health_check", "get_metrics"],
        tags=["search", "analysis", "mcp"]
    ),
    EnhancedServiceInfo(
        service_id="tool_registry_manager_static",
        name="Tool Registry Manager (Static)",
        description="工具註冊管理服務 - 靜態註冊",
        service_type="management",
        version="1.0.0",
        registry_type=ServiceRegistryType.STATIC,
        priority=ServicePriority.CRITICAL,
        endpoints=[
            ServiceEndpoint(
                endpoint_id="tool_registry_primary",
                url="localhost",
                port=8004,
                path="/",
                health_check_path="/health"
            )
        ],
        capabilities=["tool_registration", "discovery", "management"],
        supported_actions=["register_tool", "discover_tools", "get_tool_status"],
        tags=["tools", "registry", "management"]
    )
]

