"""
MCP協調器設計模式增強組件
從aicore0620 mcp_coordinator_server.py借鑒協調器設計模式
實現統一的MCP通信接口和服務協調功能
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import aiohttp
import uuid

logger = logging.getLogger(__name__)

class MCPServiceStatus(Enum):
    """MCP服務狀態"""
    UNKNOWN = "unknown"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

class MCPServiceType(Enum):
    """MCP服務類型"""
    ANALYSIS = "analysis"
    GENERATION = "generation"
    MANAGEMENT = "management"
    WORKFLOW = "workflow"
    UTILITY = "utility"

@dataclass
class MCPServiceInfo:
    """MCP服務信息"""
    service_id: str
    name: str
    service_type: MCPServiceType
    description: str
    endpoint: str
    port: int
    status: MCPServiceStatus = MCPServiceStatus.UNKNOWN
    capabilities: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    health_check_url: Optional[str] = None
    last_health_check: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "service_id": self.service_id,
            "name": self.name,
            "service_type": self.service_type.value,
            "description": self.description,
            "endpoint": self.endpoint,
            "port": self.port,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "version": self.version,
            "health_check_url": self.health_check_url,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "metadata": self.metadata
        }

@dataclass
class MCPRequest:
    """MCP請求"""
    request_id: str
    source_service: str
    target_service: str
    action: str
    payload: Dict[str, Any]
    priority: int = 1
    timeout: float = 30.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "request_id": self.request_id,
            "source_service": self.source_service,
            "target_service": self.target_service,
            "action": self.action,
            "payload": self.payload,
            "priority": self.priority,
            "timeout": self.timeout,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class MCPResponse:
    """MCP響應"""
    request_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "request_id": self.request_id,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "processing_time": self.processing_time,
            "timestamp": self.timestamp.isoformat()
        }

class MCPCoordinator:
    """MCP協調器 - 統一MCP通信管理"""
    
    def __init__(self):
        self.services: Dict[str, MCPServiceInfo] = {}
        self.request_queue: asyncio.Queue = asyncio.Queue()
        self.response_callbacks: Dict[str, Callable] = {}
        self.running = False
        self.coordinator_id = f"coordinator_{uuid.uuid4().hex[:8]}"
        
        # 統計信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "active_services": 0,
            "start_time": datetime.now()
        }
        
        logger.info(f"MCP協調器初始化完成 - ID: {self.coordinator_id}")
    
    async def start(self):
        """啟動協調器"""
        if self.running:
            logger.warning("MCP協調器已在運行中")
            return
        
        self.running = True
        logger.info("MCP協調器啟動中...")
        
        # 啟動請求處理任務
        asyncio.create_task(self._process_requests())
        
        # 啟動健康檢查任務
        asyncio.create_task(self._health_check_loop())
        
        logger.info("MCP協調器啟動完成")
    
    async def stop(self):
        """停止協調器"""
        if not self.running:
            return
        
        self.running = False
        logger.info("MCP協調器停止中...")
        
        # 等待所有請求處理完成
        while not self.request_queue.empty():
            await asyncio.sleep(0.1)
        
        logger.info("MCP協調器已停止")
    
    def register_service(self, service_info: MCPServiceInfo):
        """註冊MCP服務"""
        self.services[service_info.service_id] = service_info
        self.stats["active_services"] = len([s for s in self.services.values() if s.status == MCPServiceStatus.RUNNING])
        
        logger.info(f"MCP服務已註冊: {service_info.name} ({service_info.service_id})")
    
    def unregister_service(self, service_id: str):
        """取消註冊MCP服務"""
        if service_id in self.services:
            service_name = self.services[service_id].name
            del self.services[service_id]
            self.stats["active_services"] = len([s for s in self.services.values() if s.status == MCPServiceStatus.RUNNING])
            
            logger.info(f"MCP服務已取消註冊: {service_name} ({service_id})")
    
    def get_service(self, service_id: str) -> Optional[MCPServiceInfo]:
        """獲取服務信息"""
        return self.services.get(service_id)
    
    def list_services(self, service_type: Optional[MCPServiceType] = None, status: Optional[MCPServiceStatus] = None) -> List[MCPServiceInfo]:
        """列出服務"""
        services = list(self.services.values())
        
        if service_type:
            services = [s for s in services if s.service_type == service_type]
        
        if status:
            services = [s for s in services if s.status == status]
        
        return services
    
    async def send_request(self, request: MCPRequest) -> MCPResponse:
        """發送MCP請求"""
        start_time = time.time()
        
        try:
            # 檢查目標服務是否存在
            target_service = self.get_service(request.target_service)
            if not target_service:
                return MCPResponse(
                    request_id=request.request_id,
                    success=False,
                    error=f"目標服務不存在: {request.target_service}",
                    processing_time=time.time() - start_time
                )
            
            # 檢查目標服務狀態
            if target_service.status != MCPServiceStatus.RUNNING:
                return MCPResponse(
                    request_id=request.request_id,
                    success=False,
                    error=f"目標服務不可用: {target_service.status.value}",
                    processing_time=time.time() - start_time
                )
            
            # 發送HTTP請求到目標服務
            response = await self._send_http_request(target_service, request)
            
            self.stats["total_requests"] += 1
            if response.success:
                self.stats["successful_requests"] += 1
            else:
                self.stats["failed_requests"] += 1
            
            return response
            
        except Exception as e:
            self.stats["total_requests"] += 1
            self.stats["failed_requests"] += 1
            
            logger.error(f"發送MCP請求失敗: {e}")
            return MCPResponse(
                request_id=request.request_id,
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    async def _send_http_request(self, service: MCPServiceInfo, request: MCPRequest) -> MCPResponse:
        """發送HTTP請求到目標服務"""
        start_time = time.time()
        
        try:
            url = f"{service.endpoint}/{request.action}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=request.payload,
                    timeout=aiohttp.ClientTimeout(total=request.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return MCPResponse(
                            request_id=request.request_id,
                            success=True,
                            data=data,
                            processing_time=time.time() - start_time
                        )
                    else:
                        error_text = await response.text()
                        return MCPResponse(
                            request_id=request.request_id,
                            success=False,
                            error=f"HTTP {response.status}: {error_text}",
                            processing_time=time.time() - start_time
                        )
                        
        except asyncio.TimeoutError:
            return MCPResponse(
                request_id=request.request_id,
                success=False,
                error="請求超時",
                processing_time=time.time() - start_time
            )
        except Exception as e:
            return MCPResponse(
                request_id=request.request_id,
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    async def _process_requests(self):
        """處理請求隊列"""
        while self.running:
            try:
                # 從隊列中獲取請求
                request = await asyncio.wait_for(self.request_queue.get(), timeout=1.0)
                
                # 處理請求
                response = await self.send_request(request)
                
                # 調用回調函數
                if request.request_id in self.response_callbacks:
                    callback = self.response_callbacks.pop(request.request_id)
                    await callback(response)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"處理請求時發生錯誤: {e}")
    
    async def _health_check_loop(self):
        """健康檢查循環"""
        while self.running:
            try:
                for service in self.services.values():
                    await self._check_service_health(service)
                
                # 每30秒檢查一次
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"健康檢查時發生錯誤: {e}")
                await asyncio.sleep(5)
    
    async def _check_service_health(self, service: MCPServiceInfo):
        """檢查服務健康狀態"""
        if not service.health_check_url:
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    service.health_check_url,
                    timeout=aiohttp.ClientTimeout(total=5.0)
                ) as response:
                    if response.status == 200:
                        service.status = MCPServiceStatus.RUNNING
                    else:
                        service.status = MCPServiceStatus.ERROR
                    
                    service.last_health_check = datetime.now()
                    
        except Exception as e:
            logger.warning(f"服務健康檢查失敗 {service.name}: {e}")
            service.status = MCPServiceStatus.ERROR
            service.last_health_check = datetime.now()
    
    def get_coordinator_status(self) -> Dict[str, Any]:
        """獲取協調器狀態"""
        uptime = datetime.now() - self.stats["start_time"]
        
        return {
            "coordinator_id": self.coordinator_id,
            "running": self.running,
            "uptime": str(uptime),
            "registered_services": len(self.services),
            "active_services": len([s for s in self.services.values() if s.status == MCPServiceStatus.RUNNING]),
            "total_requests": self.stats["total_requests"],
            "successful_requests": self.stats["successful_requests"],
            "failed_requests": self.stats["failed_requests"],
            "success_rate": (self.stats["successful_requests"] / max(self.stats["total_requests"], 1)) * 100,
            "services": [service.to_dict() for service in self.services.values()]
        }

def create_mcp_coordinator() -> MCPCoordinator:
    """創建MCP協調器實例"""
    return MCPCoordinator()

# 預定義的MCP服務配置
DEFAULT_MCP_SERVICES = [
    MCPServiceInfo(
        service_id="cloud_search_mcp",
        name="Cloud Search MCP",
        service_type=MCPServiceType.ANALYSIS,
        description="雲端搜索和分析服務",
        endpoint="http://localhost:8001",
        port=8001,
        capabilities=["search", "analysis", "context_enrichment"],
        health_check_url="http://localhost:8001/health"
    ),
    MCPServiceInfo(
        service_id="enhanced_test_flow_mcp",
        name="Enhanced Test Flow MCP",
        service_type=MCPServiceType.WORKFLOW,
        description="增強測試流程管理",
        endpoint="http://localhost:8002",
        port=8002,
        capabilities=["test_management", "flow_control", "requirement_analysis"],
        health_check_url="http://localhost:8002/health"
    ),
    MCPServiceInfo(
        service_id="smartinvention_mcp",
        name="Smartinvention MCP",
        service_type=MCPServiceType.GENERATION,
        description="智能發明和創新服務",
        endpoint="http://localhost:8003",
        port=8003,
        capabilities=["invention", "innovation", "idea_generation"],
        health_check_url="http://localhost:8003/health"
    ),
    MCPServiceInfo(
        service_id="tool_registry_manager",
        name="Tool Registry Manager",
        service_type=MCPServiceType.MANAGEMENT,
        description="工具註冊和管理服務",
        endpoint="http://localhost:8004",
        port=8004,
        capabilities=["tool_registration", "discovery", "management"],
        health_check_url="http://localhost:8004/health"
    )
]

