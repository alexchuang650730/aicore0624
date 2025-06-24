"""
PowerAutomation Local MCP Adapter - 工具註冊機制
Tool Registration Manager Implementation

負責發現本地工具並向雲端註冊中心註冊
"""

import asyncio
import json
import logging
import aiohttp
import aiofiles
import hashlib
import psutil
import platform
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import importlib.util
import subprocess
import socket

logger = logging.getLogger(__name__)

class ToolStatus(Enum):
    """工具狀態枚舉"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class RegistrationStatus(Enum):
    """註冊狀態枚舉"""
    PENDING = "pending"
    REGISTERED = "registered"
    FAILED = "failed"
    UPDATING = "updating"

@dataclass
class LoadMetrics:
    """負載指標"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    active_requests: int = 0
    queue_length: int = 0
    response_time_avg: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ToolCapability:
    """工具能力描述"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict] = field(default_factory=list)

@dataclass
class LocalToolInfo:
    """本地工具信息"""
    tool_id: str
    name: str
    version: str
    description: str
    tool_type: str  # "python", "binary", "service", "api"
    capabilities: List[ToolCapability]
    endpoint: Optional[str] = None
    executable_path: Optional[str] = None
    config_path: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    status: ToolStatus = ToolStatus.AVAILABLE
    load_metrics: LoadMetrics = field(default_factory=LoadMetrics)
    registration_status: RegistrationStatus = RegistrationStatus.PENDING
    last_heartbeat: Optional[datetime] = None
    registration_time: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RegistrationRequest:
    """註冊請求"""
    adapter_id: str
    tool_info: LocalToolInfo
    system_info: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RegistrationResponse:
    """註冊響應"""
    success: bool
    tool_id: str
    message: str
    assigned_endpoints: List[str] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    next_sync_time: Optional[datetime] = None

class ToolDiscovery:
    """工具發現器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.discovery_paths = config.get('discovery_paths', [])
        self.auto_discovery = config.get('auto_discovery', True)
        self.scan_interval = config.get('scan_interval', 300)  # 5分鐘
        
    async def discover_tools(self) -> List[LocalToolInfo]:
        """發現本地工具"""
        discovered_tools = []
        
        try:
            # 發現Python工具
            python_tools = await self._discover_python_tools()
            discovered_tools.extend(python_tools)
            
            # 發現二進制工具
            binary_tools = await self._discover_binary_tools()
            discovered_tools.extend(binary_tools)
            
            # 發現服務工具
            service_tools = await self._discover_service_tools()
            discovered_tools.extend(service_tools)
            
            # 發現API工具
            api_tools = await self._discover_api_tools()
            discovered_tools.extend(api_tools)
            
            logger.info(f"發現 {len(discovered_tools)} 個本地工具")
            return discovered_tools
            
        except Exception as e:
            logger.error(f"工具發現失敗: {e}")
            return []
    
    async def _discover_python_tools(self) -> List[LocalToolInfo]:
        """發現Python工具"""
        tools = []
        
        for path in self.discovery_paths:
            path_obj = Path(path)
            if not path_obj.exists():
                continue
                
            # 查找Python模塊
            for py_file in path_obj.rglob("*.py"):
                try:
                    tool_info = await self._analyze_python_tool(py_file)
                    if tool_info:
                        tools.append(tool_info)
                except Exception as e:
                    logger.warning(f"分析Python工具失敗 {py_file}: {e}")
        
        return tools
    
    async def _analyze_python_tool(self, py_file: Path) -> Optional[LocalToolInfo]:
        """分析Python工具"""
        try:
            # 讀取文件內容
            async with aiofiles.open(py_file, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # 檢查是否包含工具標識
            if not any(marker in content for marker in ['@tool', 'class Tool', 'def process']):
                return None
            
            # 提取工具信息
            tool_id = f"python_{py_file.stem}_{hashlib.md5(str(py_file).encode()).hexdigest()[:8]}"
            
            # 嘗試動態導入獲取更多信息
            spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 提取工具元數據
                name = getattr(module, '__tool_name__', py_file.stem)
                version = getattr(module, '__version__', '1.0.0')
                description = getattr(module, '__description__', f'Python工具: {py_file.stem}')
                capabilities = getattr(module, '__capabilities__', [])
                
                # 轉換能力格式
                tool_capabilities = []
                for cap in capabilities:
                    if isinstance(cap, dict):
                        tool_capabilities.append(ToolCapability(**cap))
                    else:
                        tool_capabilities.append(ToolCapability(
                            name=str(cap),
                            description=f"能力: {cap}",
                            input_types=["any"],
                            output_types=["any"]
                        ))
                
                return LocalToolInfo(
                    tool_id=tool_id,
                    name=name,
                    version=version,
                    description=description,
                    tool_type="python",
                    capabilities=tool_capabilities,
                    executable_path=str(py_file),
                    dependencies=getattr(module, '__dependencies__', []),
                    metadata={
                        'file_size': py_file.stat().st_size,
                        'last_modified': datetime.fromtimestamp(py_file.stat().st_mtime),
                        'python_version': platform.python_version()
                    }
                )
                
        except Exception as e:
            logger.warning(f"分析Python工具失敗 {py_file}: {e}")
            return None
    
    async def _discover_binary_tools(self) -> List[LocalToolInfo]:
        """發現二進制工具"""
        tools = []
        
        # 常見的工具目錄
        binary_paths = ['/usr/bin', '/usr/local/bin', '/opt/bin']
        binary_paths.extend(self.discovery_paths)
        
        for path in binary_paths:
            path_obj = Path(path)
            if not path_obj.exists():
                continue
                
            # 查找可執行文件
            for binary_file in path_obj.iterdir():
                if binary_file.is_file() and binary_file.stat().st_mode & 0o111:
                    try:
                        tool_info = await self._analyze_binary_tool(binary_file)
                        if tool_info:
                            tools.append(tool_info)
                    except Exception as e:
                        logger.warning(f"分析二進制工具失敗 {binary_file}: {e}")
        
        return tools
    
    async def _analyze_binary_tool(self, binary_file: Path) -> Optional[LocalToolInfo]:
        """分析二進制工具"""
        try:
            # 獲取工具版本信息
            version_info = await self._get_binary_version(binary_file)
            
            tool_id = f"binary_{binary_file.stem}_{hashlib.md5(str(binary_file).encode()).hexdigest()[:8]}"
            
            # 基本能力推斷
            capabilities = [
                ToolCapability(
                    name="command_execution",
                    description=f"執行 {binary_file.name} 命令",
                    input_types=["string", "list"],
                    output_types=["string", "json"]
                )
            ]
            
            return LocalToolInfo(
                tool_id=tool_id,
                name=binary_file.name,
                version=version_info.get('version', '1.0.0'),
                description=f"二進制工具: {binary_file.name}",
                tool_type="binary",
                capabilities=capabilities,
                executable_path=str(binary_file),
                metadata={
                    'file_size': binary_file.stat().st_size,
                    'last_modified': datetime.fromtimestamp(binary_file.stat().st_mtime),
                    'permissions': oct(binary_file.stat().st_mode)[-3:],
                    'version_info': version_info
                }
            )
            
        except Exception as e:
            logger.warning(f"分析二進制工具失敗 {binary_file}: {e}")
            return None
    
    async def _get_binary_version(self, binary_file: Path) -> Dict[str, Any]:
        """獲取二進制工具版本信息"""
        version_info = {}
        
        try:
            # 嘗試常見的版本命令
            version_commands = ['--version', '-v', '--help', '-h']
            
            for cmd in version_commands:
                try:
                    result = subprocess.run(
                        [str(binary_file), cmd],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if result.returncode == 0 and result.stdout:
                        version_info['version_output'] = result.stdout.strip()
                        # 嘗試提取版本號
                        import re
                        version_match = re.search(r'(\d+\.\d+\.\d+)', result.stdout)
                        if version_match:
                            version_info['version'] = version_match.group(1)
                        break
                        
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    continue
                    
        except Exception as e:
            logger.warning(f"獲取版本信息失敗 {binary_file}: {e}")
        
        return version_info
    
    async def _discover_service_tools(self) -> List[LocalToolInfo]:
        """發現服務工具"""
        tools = []
        
        # 檢查常見服務端口
        service_ports = [
            (8000, "HTTP服務"),
            (8080, "HTTP代理服務"),
            (3000, "Node.js服務"),
            (5000, "Flask服務"),
            (9000, "PHP-FPM服務"),
            (11434, "Ollama服務")
        ]
        
        for port, description in service_ports:
            if await self._check_port_open('localhost', port):
                tool_info = await self._analyze_service_tool(port, description)
                if tool_info:
                    tools.append(tool_info)
        
        return tools
    
    async def _check_port_open(self, host: str, port: int) -> bool:
        """檢查端口是否開放"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    async def _analyze_service_tool(self, port: int, description: str) -> Optional[LocalToolInfo]:
        """分析服務工具"""
        try:
            tool_id = f"service_port_{port}"
            endpoint = f"http://localhost:{port}"
            
            # 嘗試獲取服務信息
            service_info = await self._get_service_info(endpoint)
            
            capabilities = [
                ToolCapability(
                    name="http_service",
                    description=f"HTTP服務 - {description}",
                    input_types=["json", "string"],
                    output_types=["json", "string"]
                )
            ]
            
            return LocalToolInfo(
                tool_id=tool_id,
                name=f"Service-{port}",
                version=service_info.get('version', '1.0.0'),
                description=description,
                tool_type="service",
                capabilities=capabilities,
                endpoint=endpoint,
                metadata={
                    'port': port,
                    'service_info': service_info,
                    'protocol': 'http'
                }
            )
            
        except Exception as e:
            logger.warning(f"分析服務工具失敗 port {port}: {e}")
            return None
    
    async def _get_service_info(self, endpoint: str) -> Dict[str, Any]:
        """獲取服務信息"""
        service_info = {}
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                # 嘗試常見的信息端點
                info_endpoints = ['/', '/health', '/status', '/info', '/version']
                
                for info_path in info_endpoints:
                    try:
                        async with session.get(f"{endpoint}{info_path}") as response:
                            if response.status == 200:
                                content_type = response.headers.get('content-type', '')
                                if 'application/json' in content_type:
                                    data = await response.json()
                                    service_info.update(data)
                                else:
                                    text = await response.text()
                                    service_info['response'] = text[:500]  # 限制長度
                                break
                    except Exception:
                        continue
                        
        except Exception as e:
            logger.warning(f"獲取服務信息失敗 {endpoint}: {e}")
        
        return service_info
    
    async def _discover_api_tools(self) -> List[LocalToolInfo]:
        """發現API工具"""
        tools = []
        
        # 檢查配置中的API端點
        api_configs = self.config.get('api_endpoints', [])
        
        for api_config in api_configs:
            try:
                tool_info = await self._analyze_api_tool(api_config)
                if tool_info:
                    tools.append(tool_info)
            except Exception as e:
                logger.warning(f"分析API工具失敗 {api_config}: {e}")
        
        return tools
    
    async def _analyze_api_tool(self, api_config: Dict) -> Optional[LocalToolInfo]:
        """分析API工具"""
        try:
            endpoint = api_config.get('endpoint')
            if not endpoint:
                return None
            
            tool_id = f"api_{hashlib.md5(endpoint.encode()).hexdigest()[:8]}"
            
            # 測試API可用性
            api_info = await self._test_api_endpoint(endpoint, api_config.get('headers', {}))
            
            if not api_info.get('available'):
                return None
            
            capabilities = []
            for cap in api_config.get('capabilities', []):
                capabilities.append(ToolCapability(**cap))
            
            return LocalToolInfo(
                tool_id=tool_id,
                name=api_config.get('name', f"API-{endpoint}"),
                version=api_config.get('version', '1.0.0'),
                description=api_config.get('description', f"API工具: {endpoint}"),
                tool_type="api",
                capabilities=capabilities,
                endpoint=endpoint,
                metadata={
                    'api_info': api_info,
                    'headers': api_config.get('headers', {}),
                    'auth_type': api_config.get('auth_type', 'none')
                }
            )
            
        except Exception as e:
            logger.warning(f"分析API工具失敗: {e}")
            return None
    
    async def _test_api_endpoint(self, endpoint: str, headers: Dict) -> Dict[str, Any]:
        """測試API端點"""
        api_info = {'available': False}
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(endpoint, headers=headers) as response:
                    api_info['available'] = response.status < 500
                    api_info['status_code'] = response.status
                    api_info['response_time'] = response.headers.get('X-Response-Time')
                    
        except Exception as e:
            logger.warning(f"測試API端點失敗 {endpoint}: {e}")
        
        return api_info

class ToolRegistryManager:
    """工具註冊管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.adapter_id = config.get('adapter_id', f"local_adapter_{socket.gethostname()}")
        self.cloud_endpoint = config.get('cloud_endpoint', 'https://powerautomation.cloud')
        self.api_key = config.get('api_key', '')
        self.registration_interval = config.get('registration_interval', 300)  # 5分鐘
        
        # 內部狀態
        self.registered_tools: Dict[str, LocalToolInfo] = {}
        self.discovery = ToolDiscovery(config.get('tool_discovery', {}))
        self.running = False
        self.last_discovery = None
        
        # 統計信息
        self.stats = {
            'total_discovered': 0,
            'total_registered': 0,
            'registration_failures': 0,
            'last_sync_time': None
        }
    
    async def start(self):
        """啟動工具註冊管理器"""
        logger.info("啟動工具註冊管理器...")
        self.running = True
        
        # 初始工具發現和註冊
        await self.discover_and_register_tools()
        
        # 啟動定期同步任務
        asyncio.create_task(self._periodic_sync())
        
        logger.info("工具註冊管理器啟動完成")
    
    async def stop(self):
        """停止工具註冊管理器"""
        logger.info("停止工具註冊管理器...")
        self.running = False
    
    async def discover_and_register_tools(self):
        """發現並註冊工具"""
        try:
            # 發現本地工具
            discovered_tools = await self.discovery.discover_tools()
            self.stats['total_discovered'] = len(discovered_tools)
            
            # 註冊新工具或更新現有工具
            for tool in discovered_tools:
                await self.register_tool(tool)
            
            self.last_discovery = datetime.now()
            logger.info(f"工具發現完成，發現 {len(discovered_tools)} 個工具")
            
        except Exception as e:
            logger.error(f"工具發現和註冊失敗: {e}")
    
    async def register_tool(self, tool: LocalToolInfo) -> bool:
        """註冊單個工具"""
        try:
            # 檢查工具是否已註冊
            if tool.tool_id in self.registered_tools:
                existing_tool = self.registered_tools[tool.tool_id]
                if existing_tool.last_updated >= tool.last_updated:
                    return True  # 無需更新
            
            # 準備註冊請求
            registration_request = RegistrationRequest(
                adapter_id=self.adapter_id,
                tool_info=tool,
                system_info=await self._get_system_info()
            )
            
            # 發送註冊請求到雲端
            response = await self._send_registration_request(registration_request)
            
            if response and response.success:
                tool.registration_status = RegistrationStatus.REGISTERED
                tool.registration_time = datetime.now()
                self.registered_tools[tool.tool_id] = tool
                self.stats['total_registered'] += 1
                
                logger.info(f"工具註冊成功: {tool.name} ({tool.tool_id})")
                return True
            else:
                tool.registration_status = RegistrationStatus.FAILED
                self.stats['registration_failures'] += 1
                logger.error(f"工具註冊失敗: {tool.name} - {response.message if response else 'No response'}")
                return False
                
        except Exception as e:
            logger.error(f"註冊工具失敗 {tool.name}: {e}")
            tool.registration_status = RegistrationStatus.FAILED
            self.stats['registration_failures'] += 1
            return False
    
    async def _send_registration_request(self, request: RegistrationRequest) -> Optional[RegistrationResponse]:
        """發送註冊請求到雲端"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}',
                'X-Adapter-ID': self.adapter_id
            }
            
            data = {
                'adapter_id': request.adapter_id,
                'tool_info': asdict(request.tool_info),
                'system_info': request.system_info,
                'timestamp': request.timestamp.isoformat()
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    f"{self.cloud_endpoint}/api/register/tool",
                    headers=headers,
                    json=data
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return RegistrationResponse(
                            success=result.get('success', False),
                            tool_id=result.get('tool_id', ''),
                            message=result.get('message', ''),
                            assigned_endpoints=result.get('assigned_endpoints', []),
                            configuration=result.get('configuration', {}),
                            next_sync_time=datetime.fromisoformat(result['next_sync_time']) if result.get('next_sync_time') else None
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"註冊請求失敗 {response.status}: {error_text}")
                        return RegistrationResponse(
                            success=False,
                            tool_id=request.tool_info.tool_id,
                            message=f"HTTP {response.status}: {error_text}"
                        )
                        
        except Exception as e:
            logger.error(f"發送註冊請求失敗: {e}")
            return RegistrationResponse(
                success=False,
                tool_id=request.tool_info.tool_id,
                message=f"Network error: {str(e)}"
            )
    
    async def _get_system_info(self) -> Dict[str, Any]:
        """獲取系統信息"""
        try:
            return {
                'hostname': socket.gethostname(),
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_usage': {
                    'total': psutil.disk_usage('/').total,
                    'free': psutil.disk_usage('/').free
                },
                'network_interfaces': [
                    {
                        'name': interface,
                        'addresses': [addr.address for addr in addresses if addr.family == socket.AF_INET]
                    }
                    for interface, addresses in psutil.net_if_addrs().items()
                ],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"獲取系統信息失敗: {e}")
            return {'error': str(e)}
    
    async def update_tool_status(self, tool_id: str, status: ToolStatus, load_metrics: Optional[LoadMetrics] = None):
        """更新工具狀態"""
        if tool_id in self.registered_tools:
            tool = self.registered_tools[tool_id]
            tool.status = status
            tool.last_updated = datetime.now()
            
            if load_metrics:
                tool.load_metrics = load_metrics
            
            # 如果狀態變化顯著，立即同步到雲端
            if status in [ToolStatus.ERROR, ToolStatus.UNAVAILABLE]:
                await self._sync_tool_status(tool)
    
    async def _sync_tool_status(self, tool: LocalToolInfo):
        """同步工具狀態到雲端"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}',
                'X-Adapter-ID': self.adapter_id
            }
            
            data = {
                'tool_id': tool.tool_id,
                'status': tool.status.value,
                'load_metrics': asdict(tool.load_metrics),
                'timestamp': datetime.now().isoformat()
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.put(
                    f"{self.cloud_endpoint}/api/tools/{tool.tool_id}/status",
                    headers=headers,
                    json=data
                ) as response:
                    
                    if response.status == 200:
                        logger.debug(f"工具狀態同步成功: {tool.tool_id}")
                    else:
                        logger.warning(f"工具狀態同步失敗 {tool.tool_id}: {response.status}")
                        
        except Exception as e:
            logger.error(f"同步工具狀態失敗 {tool.tool_id}: {e}")
    
    async def sync_with_cloud(self):
        """與雲端同步"""
        try:
            # 獲取雲端工具狀態
            cloud_tools = await self._get_cloud_tools()
            
            # 比較並更新本地狀態
            for cloud_tool in cloud_tools:
                tool_id = cloud_tool.get('tool_id')
                if tool_id in self.registered_tools:
                    local_tool = self.registered_tools[tool_id]
                    # 更新配置或狀態
                    if cloud_tool.get('configuration'):
                        local_tool.metadata.update(cloud_tool['configuration'])
            
            # 更新統計
            self.stats['last_sync_time'] = datetime.now()
            
            logger.info("與雲端同步完成")
            
        except Exception as e:
            logger.error(f"與雲端同步失敗: {e}")
    
    async def _get_cloud_tools(self) -> List[Dict]:
        """獲取雲端工具列表"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'X-Adapter-ID': self.adapter_id
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                async with session.get(
                    f"{self.cloud_endpoint}/api/sync/tools",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return result.get('tools', [])
                    else:
                        logger.warning(f"獲取雲端工具列表失敗: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"獲取雲端工具列表失敗: {e}")
            return []
    
    async def _periodic_sync(self):
        """定期同步任務"""
        while self.running:
            try:
                await asyncio.sleep(self.registration_interval)
                
                if self.running:
                    # 重新發現工具
                    await self.discover_and_register_tools()
                    
                    # 與雲端同步
                    await self.sync_with_cloud()
                    
            except Exception as e:
                logger.error(f"定期同步任務失敗: {e}")
    
    def get_registered_tools(self) -> List[LocalToolInfo]:
        """獲取已註冊工具列表"""
        return list(self.registered_tools.values())
    
    def get_tool_by_id(self, tool_id: str) -> Optional[LocalToolInfo]:
        """根據ID獲取工具"""
        return self.registered_tools.get(tool_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return {
            **self.stats,
            'registered_tools_count': len(self.registered_tools),
            'tools_by_status': {
                status.value: len([t for t in self.registered_tools.values() if t.status == status])
                for status in ToolStatus
            },
            'tools_by_type': {
                tool_type: len([t for t in self.registered_tools.values() if t.tool_type == tool_type])
                for tool_type in ['python', 'binary', 'service', 'api']
            }
        }

# 創建工具註冊管理器的工廠函數
def create_tool_registry_manager(config: Dict[str, Any]) -> ToolRegistryManager:
    """創建工具註冊管理器實例"""
    return ToolRegistryManager(config)

# 導出主要類和函數
__all__ = [
    'ToolRegistryManager',
    'ToolDiscovery',
    'LocalToolInfo',
    'ToolCapability',
    'LoadMetrics',
    'ToolStatus',
    'RegistrationStatus',
    'create_tool_registry_manager'
]

