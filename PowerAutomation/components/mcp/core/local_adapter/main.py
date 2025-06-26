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

