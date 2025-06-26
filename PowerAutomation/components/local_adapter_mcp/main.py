"""
PowerAutomation Local MCP Adapter - 主組件
Local MCP Adapter Main Component

整合工具註冊、心跳管理和智慧路由功能的端側適配器
"""

import asyncio
import json
import logging
import socket
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import yaml

# 導入核心組件
from .tool_registry_manager import (
    ToolRegistryManager, 
    LocalToolInfo, 
    ToolStatus,
    create_tool_registry_manager
)
from .heartbeat_manager import (
    HeartbeatManager,
    ConnectionStatus,
    HeartbeatStatus,
    create_heartbeat_manager
)
from .smart_routing_engine import (
    SmartRoutingEngine,
    ToolEndpoint,
    RoutingRequest,
    RoutingDecision,
    LoadMetrics,
    ToolHealth,
    create_smart_routing_engine
)

logger = logging.getLogger(__name__)

@dataclass
class AdapterConfig:
    """適配器配置"""
    adapter_id: str
    cloud_endpoint: str
    api_key: str
    
    # 工具註冊配置
    tool_discovery: Dict[str, Any]
    
    # 心跳配置
    heartbeat: Dict[str, Any]
    
    # 路由配置
    routing: Dict[str, Any]
    
    # 安全配置
    security: Dict[str, Any]
    
    # 日誌配置
    logging: Dict[str, Any]

class LocalMCPAdapter:
    """PowerAutomation Local MCP Adapter"""
    
    def __init__(self, config_path: Optional[str] = None, config_dict: Optional[Dict] = None):
        """
        初始化Local MCP Adapter
        
        Args:
            config_path: 配置文件路徑
            config_dict: 配置字典（優先於config_path）
        """
        # 加載配置
        self.config = self._load_config(config_path, config_dict)
        
        # 適配器信息
        self.adapter_id = self.config.adapter_id
        self.start_time = datetime.now()
        self.running = False
        
        # 核心組件
        self.tool_registry_manager: Optional[ToolRegistryManager] = None
        self.heartbeat_manager: Optional[HeartbeatManager] = None
        self.smart_routing_engine: Optional[SmartRoutingEngine] = None
        
        # 狀態管理
        self.status = {
            'adapter_status': 'stopped',
            'tool_registry_status': 'stopped',
            'heartbeat_status': 'stopped',
            'routing_status': 'stopped',
            'last_updated': datetime.now()
        }
        
        # 統計信息
        self.stats = {
            'uptime': 0.0,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'registered_tools': 0,
            'active_connections': 0
        }
        
        # 回調函數
        self.status_callbacks: List[Callable] = []
        self.request_callbacks: List[Callable] = []
        
        logger.info(f"Local MCP Adapter 初始化完成 - ID: {self.adapter_id}")
    
    def _load_config(self, config_path: Optional[str], config_dict: Optional[Dict]) -> AdapterConfig:
        """加載配置"""
        if config_dict:
            config_data = config_dict
        elif config_path:
            config_file = Path(config_path)
            if not config_file.exists():
                raise FileNotFoundError(f"配置文件不存在: {config_path}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
        else:
            # 使用默認配置
            config_data = self._get_default_config()
        
        # 驗證和補充配置
        config_data = self._validate_and_complete_config(config_data)
        
        return AdapterConfig(**config_data)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        hostname = socket.gethostname()
        
        return {
            'adapter_id': f"local_adapter_{hostname}_{int(time.time())}",
            'cloud_endpoint': 'https://powerautomation.cloud',
            'api_key': '',
            'tool_discovery': {
                'discovery_paths': ['./tools', '/usr/local/tools'],
                'auto_discovery': True,
                'scan_interval': 300,
                'api_endpoints': []
            },
            'heartbeat': {
                'heartbeat_interval': 30,
                'timeout': 10,
                'retry_count': 3,
                'retry_delay': 5,
                'max_retry_delay': 300,
                'use_ssl': True,
                'verify_ssl': True
            },
            'routing': {
                'default_strategy': 'intelligent',
                'load_threshold': 0.8,
                'latency_threshold': 1000,
                'error_rate_threshold': 0.1,
                'failover_enabled': True,
                'circuit_breaker_threshold': 5,
                'circuit_breaker_timeout': 60
            },
            'security': {
                'tls_enabled': True,
                'cert_path': './certs',
                'auth_required': True
            },
            'logging': {
                'level': 'INFO',
                'file': './logs/adapter.log',
                'max_size': '10MB',
                'backup_count': 5
            }
        }
    
    def _validate_and_complete_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """驗證和補充配置"""
        default_config = self._get_default_config()
        
        # 遞歸合併配置
        def merge_config(default: Dict, user: Dict) -> Dict:
            result = default.copy()
            for key, value in user.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_config(result[key], value)
                else:
                    result[key] = value
            return result
        
        return merge_config(default_config, config_data)
    
    async def start(self):
        """啟動適配器"""
        if self.running:
            logger.warning("適配器已經在運行")
            return
        
        logger.info("啟動 PowerAutomation Local MCP Adapter...")
        
        try:
            # 更新狀態
            self.running = True
            self.status['adapter_status'] = 'starting'
            await self._notify_status_change()
            
            # 初始化核心組件
            await self._initialize_components()
            
            # 啟動組件
            await self._start_components()
            
            # 設置組件間的關聯
            await self._setup_component_relationships()
            
            # 更新狀態
            self.status['adapter_status'] = 'running'
            await self._notify_status_change()
            
            logger.info("Local MCP Adapter 啟動完成")
            
        except Exception as e:
            logger.error(f"啟動適配器失敗: {e}")
            self.status['adapter_status'] = 'error'
            await self._notify_status_change()
            raise
    
    async def stop(self):
        """停止適配器"""
        if not self.running:
            logger.warning("適配器未在運行")
            return
        
        logger.info("停止 PowerAutomation Local MCP Adapter...")
        
        try:
            # 更新狀態
            self.running = False
            self.status['adapter_status'] = 'stopping'
            await self._notify_status_change()
            
            # 停止組件
            await self._stop_components()
            
            # 更新狀態
            self.status['adapter_status'] = 'stopped'
            await self._notify_status_change()
            
            logger.info("Local MCP Adapter 已停止")
            
        except Exception as e:
            logger.error(f"停止適配器失敗: {e}")
            self.status['adapter_status'] = 'error'
            await self._notify_status_change()
    
    async def _initialize_components(self):
        """初始化核心組件"""
        logger.info("初始化核心組件...")
        
        # 初始化工具註冊管理器
        self.tool_registry_manager = create_tool_registry_manager({
            **self.config.tool_discovery,
            'adapter_id': self.adapter_id,
            'cloud_endpoint': self.config.cloud_endpoint,
            'api_key': self.config.api_key
        })
        
        # 初始化心跳管理器
        self.heartbeat_manager = create_heartbeat_manager({
            **self.config.heartbeat,
            'cloud_endpoint': self.config.cloud_endpoint,
            'api_key': self.config.api_key
        }, self.adapter_id)
        
        # 初始化智慧路由引擎
        self.smart_routing_engine = create_smart_routing_engine(
            self.config.routing
        )
        
        logger.info("核心組件初始化完成")
    
    async def _start_components(self):
        """啟動組件"""
        logger.info("啟動核心組件...")
        
        # 啟動工具註冊管理器
        if self.tool_registry_manager:
            await self.tool_registry_manager.start()
            self.status['tool_registry_status'] = 'running'
        
        # 啟動心跳管理器
        if self.heartbeat_manager:
            await self.heartbeat_manager.start()
            self.status['heartbeat_status'] = 'running'
        
        # 智慧路由引擎無需啟動（無狀態）
        self.status['routing_status'] = 'running'
        
        logger.info("核心組件啟動完成")
    
    async def _stop_components(self):
        """停止組件"""
        logger.info("停止核心組件...")
        
        # 停止心跳管理器
        if self.heartbeat_manager:
            await self.heartbeat_manager.stop()
            self.status['heartbeat_status'] = 'stopped'
        
        # 停止工具註冊管理器
        if self.tool_registry_manager:
            await self.tool_registry_manager.stop()
            self.status['tool_registry_status'] = 'stopped'
        
        # 智慧路由引擎無需停止
        self.status['routing_status'] = 'stopped'
        
        logger.info("核心組件已停止")
    
    async def _setup_component_relationships(self):
        """設置組件間的關聯"""
        logger.info("設置組件關聯...")
        
        # 心跳管理器引用工具註冊管理器
        if self.heartbeat_manager and self.tool_registry_manager:
            self.heartbeat_manager.set_tool_registry_manager(self.tool_registry_manager)
        
        # 設置回調函數
        if self.heartbeat_manager:
            self.heartbeat_manager.add_status_callback(self._on_connection_status_change)
            self.heartbeat_manager.add_command_callback(self._on_server_command)
        
        if self.smart_routing_engine:
            self.smart_routing_engine.add_route_callback(self._on_route_decision)
        
        # 同步工具端點到路由引擎
        await self._sync_tools_to_routing_engine()
        
        logger.info("組件關聯設置完成")
    
    async def _sync_tools_to_routing_engine(self):
        """同步工具到路由引擎"""
        if not self.tool_registry_manager or not self.smart_routing_engine:
            return
        
        # 獲取已註冊的工具
        registered_tools = self.tool_registry_manager.get_registered_tools()
        
        for tool in registered_tools:
            # 創建工具端點
            endpoint = ToolEndpoint(
                tool_id=tool.tool_id,
                endpoint_url=tool.endpoint or f"local://{tool.tool_id}",
                weight=1.0,
                max_connections=100,
                current_connections=0,
                health=self._convert_tool_status_to_health(tool.status),
                load_metrics=self._convert_load_metrics(tool.load_metrics),
                capabilities=[cap.name for cap in tool.capabilities],
                metadata=tool.metadata
            )
            
            # 註冊到路由引擎
            self.smart_routing_engine.register_tool_endpoint(tool.tool_id, endpoint)
        
        logger.info(f"同步 {len(registered_tools)} 個工具到路由引擎")
    
    def _convert_tool_status_to_health(self, status: ToolStatus) -> ToolHealth:
        """轉換工具狀態到健康狀態"""
        mapping = {
            ToolStatus.AVAILABLE: ToolHealth.HEALTHY,
            ToolStatus.BUSY: ToolHealth.WARNING,
            ToolStatus.ERROR: ToolHealth.CRITICAL,
            ToolStatus.UNAVAILABLE: ToolHealth.UNAVAILABLE,
            ToolStatus.MAINTENANCE: ToolHealth.WARNING
        }
        return mapping.get(status, ToolHealth.UNAVAILABLE)
    
    def _convert_load_metrics(self, tool_metrics) -> LoadMetrics:
        """轉換負載指標"""
        return LoadMetrics(
            cpu_usage=tool_metrics.cpu_usage,
            memory_usage=tool_metrics.memory_usage,
            active_requests=tool_metrics.active_requests,
            queue_length=tool_metrics.queue_length,
            response_time_avg=tool_metrics.response_time_avg,
            response_time_p95=0.0,  # 需要計算
            error_rate=0.0,  # 需要計算
            throughput=0.0,  # 需要計算
            last_updated=tool_metrics.last_updated
        )
    
    async def _on_connection_status_change(self, old_status: ConnectionStatus, new_status: ConnectionStatus):
        """處理連接狀態變化"""
        logger.info(f"連接狀態變化: {old_status.value} -> {new_status.value}")
        
        # 更新適配器狀態
        if new_status == ConnectionStatus.CONNECTED:
            self.status['heartbeat_status'] = 'connected'
        elif new_status == ConnectionStatus.DISCONNECTED:
            self.status['heartbeat_status'] = 'disconnected'
        elif new_status == ConnectionStatus.ERROR:
            self.status['heartbeat_status'] = 'error'
        
        await self._notify_status_change()
    
    async def _on_server_command(self, command_type: str, command_data: Dict[str, Any]):
        """處理服務器命令"""
        logger.info(f"收到服務器命令: {command_type}")
        
        try:
            if command_type == 'refresh_tools':
                await self._handle_refresh_tools_command(command_data)
            elif command_type == 'update_routing':
                await self._handle_update_routing_command(command_data)
            elif command_type == 'health_check':
                await self._handle_health_check_command(command_data)
            
        except Exception as e:
            logger.error(f"處理服務器命令失敗 {command_type}: {e}")
    
    async def _handle_refresh_tools_command(self, command_data: Dict[str, Any]):
        """處理刷新工具命令"""
        if self.tool_registry_manager:
            await self.tool_registry_manager.discover_and_register_tools()
            await self._sync_tools_to_routing_engine()
    
    async def _handle_update_routing_command(self, command_data: Dict[str, Any]):
        """處理更新路由命令"""
        # 可以根據命令數據更新路由配置
        logger.info("處理路由更新命令")
    
    async def _handle_health_check_command(self, command_data: Dict[str, Any]):
        """處理健康檢查命令"""
        # 執行全面健康檢查
        health_status = await self.get_health_status()
        logger.info(f"健康檢查結果: {health_status}")
    
    async def _on_route_decision(self, request: RoutingRequest, decision: RoutingDecision):
        """處理路由決策"""
        logger.debug(f"路由決策: {request.request_id} -> {decision.target_tool}")
        
        # 更新統計
        self.stats['total_requests'] += 1
        
        # 通知回調
        for callback in self.request_callbacks:
            try:
                await callback(request, decision)
            except Exception as e:
                logger.error(f"請求回調執行失敗: {e}")
    
    async def _notify_status_change(self):
        """通知狀態變化"""
        self.status['last_updated'] = datetime.now()
        
        for callback in self.status_callbacks:
            try:
                await callback(self.status.copy())
            except Exception as e:
                logger.error(f"狀態回調執行失敗: {e}")
    
    # 公共API方法
    
    def add_status_callback(self, callback: Callable):
        """添加狀態變化回調"""
        self.status_callbacks.append(callback)
    
    def add_request_callback(self, callback: Callable):
        """添加請求回調"""
        self.request_callbacks.append(callback)
    
    async def route_request(self, capability: str, priority: str = 'normal', 
                          timeout: float = 30.0, metadata: Dict[str, Any] = None) -> RoutingDecision:
        """路由請求"""
        if not self.smart_routing_engine:
            raise Exception("智慧路由引擎未初始化")
        
        # 創建路由請求
        request = RoutingRequest(
            request_id=f"req_{int(time.time() * 1000)}_{id(self)}",
            capability_required=capability,
            priority=getattr(RequestPriority, priority.upper(), RequestPriority.NORMAL),
            timeout=timeout,
            metadata=metadata or {}
        )
        
        # 執行路由
        decision = await self.smart_routing_engine.route_request(request)
        
        # 更新統計
        self.stats['successful_requests'] += 1
        
        return decision
    
    async def get_registered_tools(self) -> List[LocalToolInfo]:
        """獲取已註冊工具"""
        if not self.tool_registry_manager:
            return []
        
        return self.tool_registry_manager.get_registered_tools()
    
    async def get_tool_by_id(self, tool_id: str) -> Optional[LocalToolInfo]:
        """根據ID獲取工具"""
        if not self.tool_registry_manager:
            return None
        
        return self.tool_registry_manager.get_tool_by_id(tool_id)
    
    async def update_tool_status(self, tool_id: str, status: ToolStatus, 
                               load_metrics: Optional[LoadMetrics] = None):
        """更新工具狀態"""
        if self.tool_registry_manager:
            await self.tool_registry_manager.update_tool_status(tool_id, status, load_metrics)
        
        # 同步到路由引擎
        if self.smart_routing_engine and load_metrics:
            tool = await self.get_tool_by_id(tool_id)
            if tool and tool.endpoint:
                await self.smart_routing_engine.update_tool_metrics(
                    tool_id, tool.endpoint, load_metrics
                )
    
    async def get_health_status(self) -> Dict[str, Any]:
        """獲取健康狀態"""
        health = {
            'adapter_id': self.adapter_id,
            'status': self.status['adapter_status'],
            'uptime': (datetime.now() - self.start_time).total_seconds(),
            'components': {
                'tool_registry': self.status['tool_registry_status'],
                'heartbeat': self.status['heartbeat_status'],
                'routing': self.status['routing_status']
            }
        }
        
        # 添加組件詳細狀態
        if self.heartbeat_manager:
            health['heartbeat_details'] = {
                'connection_status': self.heartbeat_manager.get_connection_status().value,
                'heartbeat_status': self.heartbeat_manager.get_heartbeat_status().value,
                'statistics': self.heartbeat_manager.get_statistics()
            }
        
        if self.tool_registry_manager:
            health['tool_registry_details'] = {
                'statistics': self.tool_registry_manager.get_statistics()
            }
        
        if self.smart_routing_engine:
            health['routing_details'] = {
                'statistics': self.smart_routing_engine.get_routing_statistics(),
                'endpoints_status': self.smart_routing_engine.get_tool_endpoints_status()
            }
        
        return health
    
    async def get_statistics(self) -> Dict[str, Any]:
        """獲取統計信息"""
        # 更新運行時間
        self.stats['uptime'] = (datetime.now() - self.start_time).total_seconds()
        
        # 更新工具數量
        if self.tool_registry_manager:
            self.stats['registered_tools'] = len(self.tool_registry_manager.registered_tools)
        
        return self.stats.copy()
    
    def get_config(self) -> AdapterConfig:
        """獲取配置"""
        return self.config
    
    def get_adapter_info(self) -> Dict[str, Any]:
        """獲取適配器信息"""
        return {
            'adapter_id': self.adapter_id,
            'version': '1.0.0',
            'start_time': self.start_time.isoformat(),
            'hostname': socket.gethostname(),
            'status': self.status.copy(),
            'config': {
                'cloud_endpoint': self.config.cloud_endpoint,
                'tool_discovery_paths': self.config.tool_discovery.get('discovery_paths', []),
                'heartbeat_interval': self.config.heartbeat.get('heartbeat_interval', 30),
                'routing_strategy': self.config.routing.get('default_strategy', 'intelligent')
            }
        }

# 創建適配器的工廠函數
def create_local_mcp_adapter(config_path: Optional[str] = None, 
                           config_dict: Optional[Dict] = None) -> LocalMCPAdapter:
    """創建Local MCP Adapter實例"""
    return LocalMCPAdapter(config_path, config_dict)

# 導出主要類和函數
__all__ = [
    'LocalMCPAdapter',
    'AdapterConfig',
    'create_local_mcp_adapter'
]



# ===== Integrated Heartbeat Manager =====
import certifi

logger = logging.getLogger(__name__)

class ConnectionStatus(Enum):
    """連接狀態枚舉"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class HeartbeatStatus(Enum):
    """心跳狀態枚舉"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILED = "failed"

@dataclass
class SystemMetrics:
    """系統指標"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    load_average: List[float]
    uptime: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AdapterStatus:
    """適配器狀態"""
    adapter_id: str
    status: ConnectionStatus
    last_heartbeat: datetime
    uptime: float
    tool_count: int
    active_connections: int
    error_count: int = 0
    warning_count: int = 0

@dataclass
class HeartbeatData:
    """心跳數據"""
    adapter_id: str
    timestamp: datetime
    sequence_number: int
    status: AdapterStatus
    system_metrics: SystemMetrics
    tool_status: Dict[str, Any]
    configuration_version: str
    capabilities: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HeartbeatResponse:
    """心跳響應"""
    success: bool
    server_timestamp: datetime
    next_heartbeat_interval: int
    commands: List[Dict[str, Any]] = field(default_factory=list)
    configuration_updates: Dict[str, Any] = field(default_factory=dict)
    message: str = ""

@dataclass
class ConnectionConfig:
    """連接配置"""
    cloud_endpoint: str
    api_key: str
    heartbeat_interval: int = 30  # 秒
    timeout: int = 10  # 秒
    retry_count: int = 3
    retry_delay: int = 5  # 秒
    max_retry_delay: int = 300  # 秒
    use_ssl: bool = True
    verify_ssl: bool = True
    compression: bool = True

class HeartbeatManager:
    """心跳管理器"""
    
    def __init__(self, config: ConnectionConfig, adapter_id: str):
        self.config = config
        self.adapter_id = adapter_id
        
        # 連接狀態
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.last_heartbeat_time = None
        self.last_successful_heartbeat = None
        self.sequence_number = 0
        self.start_time = time.time()
        
        # 統計信息
        self.stats = {
            'total_heartbeats': 0,
            'successful_heartbeats': 0,
            'failed_heartbeats': 0,
            'connection_errors': 0,
            'reconnection_count': 0,
            'average_response_time': 0.0,
            'last_error': None
        }
        
        # 回調函數
        self.status_callbacks: List[Callable] = []
        self.command_callbacks: List[Callable] = []
        
        # 內部狀態
        self.running = False
        self.heartbeat_task = None
        self.session = None
        self.retry_delay = self.config.retry_delay
        
        # 工具狀態引用
        self.tool_registry_manager = None
        
    def set_tool_registry_manager(self, tool_registry_manager):
        """設置工具註冊管理器引用"""
        self.tool_registry_manager = tool_registry_manager
    
    def add_status_callback(self, callback: Callable):
        """添加狀態變化回調"""
        self.status_callbacks.append(callback)
    
    def add_command_callback(self, callback: Callable):
        """添加命令處理回調"""
        self.command_callbacks.append(callback)
    
    async def start(self):
        """啟動心跳管理器"""
        logger.info("啟動心跳管理器...")
        self.running = True
        
        # 創建HTTP會話
        await self._create_session()
        
        # 啟動心跳任務
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        logger.info("心跳管理器啟動完成")
    
    async def stop(self):
        """停止心跳管理器"""
        logger.info("停止心跳管理器...")
        self.running = False
        
        # 取消心跳任務
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # 關閉HTTP會話
        await self._close_session()
        
        # 更新狀態
        await self._update_connection_status(ConnectionStatus.DISCONNECTED)
        
        logger.info("心跳管理器已停止")
    
    async def _create_session(self):
        """創建HTTP會話"""
        try:
            # SSL配置
            ssl_context = None
            if self.config.use_ssl:
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                if not self.config.verify_ssl:
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
            
            # 連接器配置
            connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                limit=10,
                limit_per_host=5,
                keepalive_timeout=60,
                enable_cleanup_closed=True
            )
            
            # 超時配置
            timeout = aiohttp.ClientTimeout(
                total=self.config.timeout,
                connect=self.config.timeout // 2
            )
            
            # 創建會話
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': f'PowerAutomation-LocalAdapter/{self.adapter_id}',
                    'Authorization': f'Bearer {self.config.api_key}',
                    'X-Adapter-ID': self.adapter_id
                }
            )
            
            logger.debug("HTTP會話創建成功")
            
        except Exception as e:
            logger.error(f"創建HTTP會話失敗: {e}")
            raise
    
    async def _close_session(self):
        """關閉HTTP會話"""
        if self.session:
            try:
                await self.session.close()
                self.session = None
                logger.debug("HTTP會話已關閉")
            except Exception as e:
                logger.error(f"關閉HTTP會話失敗: {e}")
    
    async def _heartbeat_loop(self):
        """心跳循環"""
        while self.running:
            try:
                # 發送心跳
                success = await self._send_heartbeat()
                
                if success:
                    # 重置重試延遲
                    self.retry_delay = self.config.retry_delay
                    
                    # 等待下次心跳
                    await asyncio.sleep(self.config.heartbeat_interval)
                else:
                    # 心跳失敗，進入重連模式
                    await self._handle_heartbeat_failure()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"心跳循環異常: {e}")
                await self._handle_heartbeat_failure()
    
    async def _send_heartbeat(self) -> bool:
        """發送心跳"""
        try:
            start_time = time.time()
            
            # 準備心跳數據
            heartbeat_data = await self._prepare_heartbeat_data()
            
            # 更新連接狀態
            if self.connection_status == ConnectionStatus.DISCONNECTED:
                await self._update_connection_status(ConnectionStatus.CONNECTING)
            
            # 發送心跳請求
            response = await self._send_heartbeat_request(heartbeat_data)
            
            if response and response.success:
                # 心跳成功
                response_time = time.time() - start_time
                await self._handle_heartbeat_success(response, response_time)
                return True
            else:
                # 心跳失敗
                await self._handle_heartbeat_error(response)
                return False
                
        except Exception as e:
            logger.error(f"發送心跳失敗: {e}")
            await self._handle_heartbeat_error(None, str(e))
            return False
    
    async def _prepare_heartbeat_data(self) -> HeartbeatData:
        """準備心跳數據"""
        # 獲取系統指標
        system_metrics = await self._collect_system_metrics()
        
        # 獲取適配器狀態
        adapter_status = AdapterStatus(
            adapter_id=self.adapter_id,
            status=self.connection_status,
            last_heartbeat=self.last_heartbeat_time or datetime.now(),
            uptime=time.time() - self.start_time,
            tool_count=len(self.tool_registry_manager.registered_tools) if self.tool_registry_manager else 0,
            active_connections=1,  # 當前只有一個連接
            error_count=self.stats['connection_errors'],
            warning_count=0
        )
        
        # 獲取工具狀態
        tool_status = {}
        if self.tool_registry_manager:
            for tool_id, tool in self.tool_registry_manager.registered_tools.items():
                tool_status[tool_id] = {
                    'status': tool.status.value,
                    'load_metrics': asdict(tool.load_metrics),
                    'last_updated': tool.last_updated.isoformat()
                }
        
        # 增加序列號
        self.sequence_number += 1
        
        return HeartbeatData(
            adapter_id=self.adapter_id,
            timestamp=datetime.now(),
            sequence_number=self.sequence_number,
            status=adapter_status,
            system_metrics=system_metrics,
            tool_status=tool_status,
            configuration_version="1.0.0",
            capabilities=[
                "tool_registration",
                "smart_routing",
                "load_balancing",
                "health_monitoring"
            ],
            metadata={
                'hostname': socket.gethostname(),
                'python_version': f"{psutil.PYTHON_VERSION}",
                'adapter_version': "1.0.0"
            }
        )
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """收集系統指標"""
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 內存使用率
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # 磁盤使用率
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # 網絡IO
            network_io = psutil.net_io_counters()
            network_data = {
                'bytes_sent': network_io.bytes_sent,
                'bytes_recv': network_io.bytes_recv,
                'packets_sent': network_io.packets_sent,
                'packets_recv': network_io.packets_recv
            }
            
            # 負載平均值
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0.0, 0.0, 0.0]
            
            # 系統運行時間
            uptime = time.time() - psutil.boot_time()
            
            return SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_data,
                load_average=list(load_avg),
                uptime=uptime
            )
            
        except Exception as e:
            logger.error(f"收集系統指標失敗: {e}")
            return SystemMetrics(
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={},
                load_average=[0.0, 0.0, 0.0],
                uptime=0.0
            )
    
    async def _send_heartbeat_request(self, heartbeat_data: HeartbeatData) -> Optional[HeartbeatResponse]:
        """發送心跳請求"""
        try:
            if not self.session:
                await self._create_session()
            
            # 準備請求數據
            data = asdict(heartbeat_data)
            
            # 轉換datetime為ISO格式
            data['timestamp'] = heartbeat_data.timestamp.isoformat()
            data['status']['last_heartbeat'] = heartbeat_data.status.last_heartbeat.isoformat()
            data['system_metrics']['timestamp'] = heartbeat_data.system_metrics.timestamp.isoformat()
            
            # 發送請求
            async with self.session.post(
                f"{self.config.cloud_endpoint}/api/heartbeat",
                json=data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return HeartbeatResponse(
                        success=result.get('success', False),
                        server_timestamp=datetime.fromisoformat(result.get('server_timestamp', datetime.now().isoformat())),
                        next_heartbeat_interval=result.get('next_heartbeat_interval', self.config.heartbeat_interval),
                        commands=result.get('commands', []),
                        configuration_updates=result.get('configuration_updates', {}),
                        message=result.get('message', '')
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"心跳請求失敗 {response.status}: {error_text}")
                    return HeartbeatResponse(
                        success=False,
                        server_timestamp=datetime.now(),
                        next_heartbeat_interval=self.config.heartbeat_interval,
                        message=f"HTTP {response.status}: {error_text}"
                    )
                    
        except Exception as e:
            logger.error(f"發送心跳請求異常: {e}")
            return None
    
    async def _handle_heartbeat_success(self, response: HeartbeatResponse, response_time: float):
        """處理心跳成功"""
        # 更新統計
        self.stats['total_heartbeats'] += 1
        self.stats['successful_heartbeats'] += 1
        
        # 更新平均響應時間
        total_successful = self.stats['successful_heartbeats']
        current_avg = self.stats['average_response_time']
        self.stats['average_response_time'] = (current_avg * (total_successful - 1) + response_time) / total_successful
        
        # 更新時間戳
        self.last_heartbeat_time = datetime.now()
        self.last_successful_heartbeat = self.last_heartbeat_time
        
        # 更新連接狀態
        await self._update_connection_status(ConnectionStatus.CONNECTED)
        
        # 處理服務器命令
        if response.commands:
            await self._process_server_commands(response.commands)
        
        # 處理配置更新
        if response.configuration_updates:
            await self._process_configuration_updates(response.configuration_updates)
        
        # 更新心跳間隔
        if response.next_heartbeat_interval != self.config.heartbeat_interval:
            logger.info(f"更新心跳間隔: {self.config.heartbeat_interval} -> {response.next_heartbeat_interval}")
            self.config.heartbeat_interval = response.next_heartbeat_interval
        
        logger.debug(f"心跳成功 - 響應時間: {response_time:.3f}s")
    
    async def _handle_heartbeat_error(self, response: Optional[HeartbeatResponse], error_msg: str = ""):
        """處理心跳錯誤"""
        # 更新統計
        self.stats['total_heartbeats'] += 1
        self.stats['failed_heartbeats'] += 1
        self.stats['connection_errors'] += 1
        self.stats['last_error'] = error_msg or (response.message if response else "Unknown error")
        
        # 更新時間戳
        self.last_heartbeat_time = datetime.now()
        
        logger.warning(f"心跳失敗: {self.stats['last_error']}")
    
    async def _handle_heartbeat_failure(self):
        """處理心跳失敗"""
        # 更新連接狀態
        await self._update_connection_status(ConnectionStatus.RECONNECTING)
        
        # 重試邏輯
        retry_count = 0
        while retry_count < self.config.retry_count and self.running:
            retry_count += 1
            
            logger.info(f"嘗試重連 ({retry_count}/{self.config.retry_count})...")
            
            # 等待重試延遲
            await asyncio.sleep(self.retry_delay)
            
            # 嘗試重新連接
            try:
                # 重新創建會話
                await self._close_session()
                await self._create_session()
                
                # 嘗試發送心跳
                if await self._send_heartbeat():
                    logger.info("重連成功")
                    self.stats['reconnection_count'] += 1
                    return
                    
            except Exception as e:
                logger.error(f"重連嘗試失敗: {e}")
            
            # 增加重試延遲（指數退避）
            self.retry_delay = min(self.retry_delay * 2, self.config.max_retry_delay)
        
        # 所有重試都失敗
        logger.error("重連失敗，進入錯誤狀態")
        await self._update_connection_status(ConnectionStatus.ERROR)
        
        # 等待一段時間後重新開始心跳循環
        await asyncio.sleep(self.config.max_retry_delay)
    
    async def _update_connection_status(self, new_status: ConnectionStatus):
        """更新連接狀態"""
        if self.connection_status != new_status:
            old_status = self.connection_status
            self.connection_status = new_status
            
            logger.info(f"連接狀態變化: {old_status.value} -> {new_status.value}")
            
            # 通知狀態變化回調
            for callback in self.status_callbacks:
                try:
                    await callback(old_status, new_status)
                except Exception as e:
                    logger.error(f"狀態回調執行失敗: {e}")
    
    async def _process_server_commands(self, commands: List[Dict[str, Any]]):
        """處理服務器命令"""
        for command in commands:
            try:
                command_type = command.get('type')
                command_data = command.get('data', {})
                
                logger.info(f"處理服務器命令: {command_type}")
                
                # 內建命令處理
                if command_type == 'update_config':
                    await self._handle_config_update(command_data)
                elif command_type == 'restart_heartbeat':
                    await self._handle_restart_heartbeat(command_data)
                elif command_type == 'sync_tools':
                    await self._handle_sync_tools(command_data)
                
                # 通知命令回調
                for callback in self.command_callbacks:
                    try:
                        await callback(command_type, command_data)
                    except Exception as e:
                        logger.error(f"命令回調執行失敗: {e}")
                        
            except Exception as e:
                logger.error(f"處理服務器命令失敗: {e}")
    
    async def _handle_config_update(self, config_data: Dict[str, Any]):
        """處理配置更新命令"""
        try:
            if 'heartbeat_interval' in config_data:
                self.config.heartbeat_interval = config_data['heartbeat_interval']
                logger.info(f"更新心跳間隔: {self.config.heartbeat_interval}")
            
            if 'timeout' in config_data:
                self.config.timeout = config_data['timeout']
                logger.info(f"更新超時時間: {self.config.timeout}")
                
        except Exception as e:
            logger.error(f"處理配置更新失敗: {e}")
    
    async def _handle_restart_heartbeat(self, command_data: Dict[str, Any]):
        """處理重啟心跳命令"""
        try:
            logger.info("收到重啟心跳命令")
            # 重置統計
            self.sequence_number = 0
            # 可以在這裡添加其他重啟邏輯
        except Exception as e:
            logger.error(f"處理重啟心跳命令失敗: {e}")
    
    async def _handle_sync_tools(self, command_data: Dict[str, Any]):
        """處理同步工具命令"""
        try:
            if self.tool_registry_manager:
                logger.info("收到同步工具命令")
                await self.tool_registry_manager.sync_with_cloud()
        except Exception as e:
            logger.error(f"處理同步工具命令失敗: {e}")
    
    async def _process_configuration_updates(self, config_updates: Dict[str, Any]):
        """處理配置更新"""
        try:
            logger.info(f"處理配置更新: {list(config_updates.keys())}")
            
            # 這裡可以根據需要處理各種配置更新
            # 例如：工具配置、路由配置等
            
        except Exception as e:
            logger.error(f"處理配置更新失敗: {e}")
    
    def get_connection_status(self) -> ConnectionStatus:
        """獲取連接狀態"""
        return self.connection_status
    
    def get_heartbeat_status(self) -> HeartbeatStatus:
        """獲取心跳狀態"""
        if self.connection_status == ConnectionStatus.CONNECTED:
            if self.last_successful_heartbeat:
                time_since_last = datetime.now() - self.last_successful_heartbeat
                if time_since_last.total_seconds() < self.config.heartbeat_interval * 2:
                    return HeartbeatStatus.HEALTHY
                elif time_since_last.total_seconds() < self.config.heartbeat_interval * 5:
                    return HeartbeatStatus.WARNING
                else:
                    return HeartbeatStatus.CRITICAL
            else:
                return HeartbeatStatus.WARNING
        else:
            return HeartbeatStatus.FAILED
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計信息"""
        uptime = time.time() - self.start_time
        success_rate = (self.stats['successful_heartbeats'] / max(self.stats['total_heartbeats'], 1)) * 100
        
        return {
            **self.stats,
            'connection_status': self.connection_status.value,
            'heartbeat_status': self.get_heartbeat_status().value,
            'uptime': uptime,
            'success_rate': success_rate,
            'last_heartbeat_time': self.last_heartbeat_time.isoformat() if self.last_heartbeat_time else None,
            'last_successful_heartbeat': self.last_successful_heartbeat.isoformat() if self.last_successful_heartbeat else None,
            'current_retry_delay': self.retry_delay,
            'sequence_number': self.sequence_number
        }

# 創建心跳管理器的工廠函數
def create_heartbeat_manager(config: Dict[str, Any], adapter_id: str) -> HeartbeatManager:
    """創建心跳管理器實例"""
    connection_config = ConnectionConfig(
        cloud_endpoint=config.get('cloud_endpoint', 'https://powerautomation.cloud'),
        api_key=config.get('api_key', ''),
        heartbeat_interval=config.get('heartbeat_interval', 30),
        timeout=config.get('timeout', 10),
        retry_count=config.get('retry_count', 3),
        retry_delay=config.get('retry_delay', 5),
        max_retry_delay=config.get('max_retry_delay', 300),
        use_ssl=config.get('use_ssl', True),
        verify_ssl=config.get('verify_ssl', True),
        compression=config.get('compression', True)
    )
    
    return HeartbeatManager(connection_config, adapter_id)

# 導出主要類和函數
__all__ = [
    'HeartbeatManager',
    'ConnectionConfig',
    'HeartbeatData',
    'HeartbeatResponse',
    'SystemMetrics',
    'AdapterStatus',
    'ConnectionStatus',
    'HeartbeatStatus',
    'create_heartbeat_manager'
]

