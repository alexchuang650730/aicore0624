# -*- coding: utf-8 -*-
"""
Tool Registry系統 - 工具發現和管理
Tool Registry System - Tool Discovery and Management

統一的工具註冊、發現和管理系統
支持MCP工具的自動發現和智能匹配
"""

import asyncio
import json
import logging
import importlib
import inspect
from typing import Dict, List, Any, Optional, Callable, Type
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import aiohttp

logger = logging.getLogger(__name__)

class ToolType(Enum):
    """工具類型枚舉"""
    MCP_SERVICE = "mcp_service"
    HTTP_API = "http_api"
    PYTHON_MODULE = "python_module"
    SHELL_COMMAND = "shell_command"
    AI_MODEL = "ai_model"

class ToolStatus(Enum):
    """工具狀態枚舉"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    LOADING = "loading"

@dataclass
class ToolCapability:
    """工具能力描述"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

@dataclass
class ToolInfo:
    """工具信息"""
    id: str
    name: str
    type: ToolType
    description: str
    version: str
    capabilities: List[ToolCapability]
    endpoint: str = None  # HTTP API端點或MCP服務地址
    module_path: str = None  # Python模塊路徑
    command: str = None  # Shell命令
    config: Dict[str, Any] = None
    dependencies: List[str] = None
    tags: List[str] = None
    status: ToolStatus = ToolStatus.LOADING
    health_check_url: str = None
    last_health_check: str = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []

class ToolRegistry:
    """
    工具註冊系統
    
    職責:
    1. 自動發現可用工具
    2. 工具註冊和管理
    3. 能力標記和匹配
    4. 健康檢查和狀態管理
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.tools: Dict[str, ToolInfo] = {}
        self.capability_index: Dict[str, List[str]] = {}  # 能力 -> 工具ID列表
        self.tag_index: Dict[str, List[str]] = {}  # 標籤 -> 工具ID列表
        self.discovery_paths = self.config.get('discovery_paths', [])
        self.auto_discovery = self.config.get('auto_discovery', True)
        
        logger.info("ToolRegistry initialized")
    
    async def initialize(self):
        """初始化工具註冊系統"""
        logger.info("Initializing ToolRegistry...")
        
        if self.auto_discovery:
            await self.discover_tools()
        
        # 加載預配置的工具
        await self.load_predefined_tools()
        
        # 執行初始健康檢查
        await self.health_check_all()
        
        logger.info(f"ToolRegistry initialized with {len(self.tools)} tools")
    
    async def discover_tools(self):
        """自動發現工具"""
        logger.info("Starting tool discovery...")
        
        # 發現MCP服務
        await self._discover_mcp_services()
        
        # 發現HTTP API
        await self._discover_http_apis()
        
        # 發現Python模塊
        await self._discover_python_modules()
        
        logger.info(f"Tool discovery completed, found {len(self.tools)} tools")
    
    async def _discover_mcp_services(self):
        """發現MCP服務"""
        logger.info("Discovering MCP services...")
        
        # 預定義的MCP服務端點
        mcp_endpoints = [
            {"name": "operations_workflow_mcp", "url": "http://localhost:8091", "port": 8091},
            {"name": "test_management_workflow_mcp", "url": "http://localhost:8321", "port": 8321},
            {"name": "requirements_analysis_mcp", "url": "http://localhost:8090", "port": 8090},
            {"name": "test_flow_mcp", "url": "http://localhost:8095", "port": 8095},
        ]
        
        for endpoint in mcp_endpoints:
            try:
                # 嘗試連接MCP服務
                health_url = f"{endpoint['url']}/health"
                async with aiohttp.ClientSession() as session:
                    async with session.get(health_url, timeout=5) as response:
                        if response.status == 200:
                            service_info = await response.json()
                            await self._register_mcp_service(endpoint, service_info)
            except Exception as e:
                logger.warning(f"Failed to discover MCP service {endpoint['name']}: {e}")
    
    async def _register_mcp_service(self, endpoint: Dict, service_info: Dict):
        """註冊MCP服務"""
        tool_id = f"mcp_{endpoint['name']}"
        
            # 處理capabilities - 支持多種格式
        capabilities = []
        cap_data = service_info.get('capabilities', {})
        
        if isinstance(cap_data, list):
            # 處理列表格式 (Test Flow MCP格式)
            for cap_name in cap_data:
                capability = ToolCapability(
                    name=cap_name,
                    description=f"Capability: {cap_name}",
                    input_types=['json', 'text'],
                    output_types=['json', 'text'],
                    parameters={}
                )
                capabilities.append(capability)
        elif isinstance(cap_data, dict):
            # 處理字典格式 (標準格式或嵌套格式)
            for cap_name, cap_info in cap_data.items():
                if isinstance(cap_info, dict):
                    # 標準字典格式
                    capability = ToolCapability(
                        name=cap_name,
                        description=cap_info.get('description', f'Capability: {cap_name}'),
                        input_types=cap_info.get('input_types', ['json']),
                        output_types=cap_info.get('output_types', ['json']),
                        parameters=cap_info.get('parameters', {})
                    )
                else:
                    # 簡單值格式
                    capability = ToolCapability(
                        name=cap_name,
                        description=f"Capability: {cap_name}",
                        input_types=['json'],
                        output_types=['json'],
                        parameters={}
                    )
                capabilities.append(capability)      
        tool_info = ToolInfo(
            id=tool_id,
            name=endpoint['name'],
            type=ToolType.MCP_SERVICE,
            description=service_info.get('description', f"MCP service: {endpoint['name']}"),
            version=service_info.get('version', '1.0.0'),
            capabilities=capabilities,
            endpoint=endpoint['url'],
            health_check_url=f"{endpoint['url']}/health",
            status=ToolStatus.AVAILABLE,
            tags=['mcp', 'service', 'workflow']
        )
        
        await self.register_tool(tool_info)
        logger.info(f"Registered MCP service: {tool_id}")
    
    async def _discover_http_apis(self):
        """發現HTTP API"""
        logger.info("Discovering HTTP APIs...")
        
        # 預定義的API端點
        api_endpoints = [
            {"name": "ai_analysis_engine", "url": "http://localhost:8888", "type": "ai_engine"},
            {"name": "operations_analysis_engine", "url": "http://localhost:8100", "type": "analysis"},
        ]
        
        for endpoint in api_endpoints:
            try:
                health_url = f"{endpoint['url']}/health"
                async with aiohttp.ClientSession() as session:
                    async with session.get(health_url, timeout=5) as response:
                        if response.status == 200:
                            api_info = await response.json()
                            await self._register_http_api(endpoint, api_info)
            except Exception as e:
                logger.warning(f"Failed to discover HTTP API {endpoint['name']}: {e}")
    
    async def _register_http_api(self, endpoint: Dict, api_info: Dict):
        """註冊HTTP API"""
        tool_id = f"api_{endpoint['name']}"
        
        capabilities = [
            ToolCapability(
                name="http_request",
                description="HTTP API request capability",
                input_types=['json', 'text'],
                output_types=['json', 'text']
            )
        ]
        
        tool_info = ToolInfo(
            id=tool_id,
            name=endpoint['name'],
            type=ToolType.HTTP_API,
            description=api_info.get('description', f"HTTP API: {endpoint['name']}"),
            version=api_info.get('version', '1.0.0'),
            capabilities=capabilities,
            endpoint=endpoint['url'],
            health_check_url=f"{endpoint['url']}/health",
            status=ToolStatus.AVAILABLE,
            tags=['api', 'http', endpoint.get('type', 'general')]
        )
        
        await self.register_tool(tool_info)
        logger.info(f"Registered HTTP API: {tool_id}")
    
    async def _discover_python_modules(self):
        """發現Python模塊"""
        logger.info("Discovering Python modules...")
        
        # 預定義的Python工具模塊
        python_tools = [
            {
                "name": "system_monitor",
                "module": "psutil",
                "description": "System monitoring and resource analysis",
                "capabilities": ["cpu_monitoring", "memory_monitoring", "disk_monitoring"]
            },
            {
                "name": "file_processor",
                "module": "builtins",
                "description": "File processing and manipulation",
                "capabilities": ["file_read", "file_write", "file_analysis"]
            }
        ]
        
        for tool_config in python_tools:
            try:
                await self._register_python_module(tool_config)
            except Exception as e:
                logger.warning(f"Failed to register Python module {tool_config['name']}: {e}")
    
    async def _register_python_module(self, tool_config: Dict):
        """註冊Python模塊"""
        tool_id = f"py_{tool_config['name']}"
        
        capabilities = []
        for cap_name in tool_config.get('capabilities', []):
            capability = ToolCapability(
                name=cap_name,
                description=f"Python capability: {cap_name}",
                input_types=['python_object', 'text'],
                output_types=['python_object', 'text']
            )
            capabilities.append(capability)
        
        tool_info = ToolInfo(
            id=tool_id,
            name=tool_config['name'],
            type=ToolType.PYTHON_MODULE,
            description=tool_config['description'],
            version="1.0.0",
            capabilities=capabilities,
            module_path=tool_config['module'],
            status=ToolStatus.AVAILABLE,
            tags=['python', 'module', 'local']
        )
        
        await self.register_tool(tool_info)
        logger.info(f"Registered Python module: {tool_id}")
    
    async def load_predefined_tools(self):
        """加載預定義工具"""
        logger.info("Loading predefined tools...")
        
        # 新的工具配置 - 移除舊的default_processor和general_processor
        # 添加新的General_Processor MCP和重命名的工具
        default_tools = [
            {
                "id": "general_processor_mcp",
                "name": "General_Processor MCP",
                "type": "mcp_component",
                "description": "統一的通用處理器MCP組件，整合多種處理能力",
                "capabilities": [
                    {
                        "name": "general_processing",
                        "description": "通用處理能力，支持多種數據格式",
                        "input_types": ["text", "json", "auto"],
                        "output_types": ["text", "json"]
                    },
                    {
                        "name": "text_processing", 
                        "description": "專業文本處理和分析能力",
                        "input_types": ["text"],
                        "output_types": ["text", "json"]
                    },
                    {
                        "name": "json_processing",
                        "description": "JSON數據處理和轉換能力", 
                        "input_types": ["json"],
                        "output_types": ["json", "text"]
                    },
                    {
                        "name": "fallback_processing",
                        "description": "系統回退處理能力，確保穩定性",
                        "input_types": ["any"],
                        "output_types": ["text", "json"]
                    },
                    {
                        "name": "auto_processing",
                        "description": "智能自動處理能力，自動選擇最佳模式",
                        "input_types": ["any"],
                        "output_types": ["text", "json"]
                    },
                    {
                        "name": "expert_insight_processing",
                        "description": "專家洞察處理能力，整合多專家分析",
                        "input_types": ["dict_with_expert_insights"],
                        "output_types": ["json"]
                    }
                ]
            },
            {
                "id": "recorder_workflow_mcp",
                "name": "Recorder_Workflow MCP",
                "type": "mcp_component",
                "description": "工作流錄製和管理的MCP組件，支持智能學習和模式分析",
                "module_path": "components.recorder_workflow_mcp",
                "class_name": "RecorderWorkflowMCP",
                "capabilities": [
                    {
                        "name": "workflow_recording",
                        "description": "錄製用戶工作流操作",
                        "input_types": ["json"],
                        "output_types": ["json"],
                        "parameters": {
                            "session_name": "string",
                            "workflow_type": "string",
                            "description": "string"
                        }
                    },
                    {
                        "name": "session_management",
                        "description": "管理錄製會話生命週期",
                        "input_types": ["json"],
                        "output_types": ["json"],
                        "parameters": {
                            "session_id": "string",
                            "action": "string"
                        }
                    },
                    {
                        "name": "data_processing",
                        "description": "處理和分析錄製數據",
                        "input_types": ["json"],
                        "output_types": ["json"],
                        "parameters": {
                            "session_id": "string",
                            "analysis_type": "string"
                        }
                    },
                    {
                        "name": "pattern_analysis",
                        "description": "分析工作流模式和優化建議",
                        "input_types": ["json"],
                        "output_types": ["json"],
                        "parameters": {
                            "workflow_data": "object",
                            "analysis_depth": "string"
                        }
                    },
                    {
                        "name": "workflow_export",
                        "description": "導出工作流數據為不同格式",
                        "input_types": ["json"],
                        "output_types": ["json", "csv", "yaml"],
                        "parameters": {
                            "session_id": "string",
                            "format": "string"
                        }
                    }
                ]
            },
            {
                "id": "test_flow_mcp",
                "name": "Test_Flow MCP",
                "type": "mcp_component", 
                "description": "測試流程MCP組件，提供API測試和UI測試能力",
                "capabilities": [
                    {
                        "name": "api_testing",
                        "description": "API接口測試能力",
                        "input_types": ["json"],
                        "output_types": ["json"]
                    },
                    {
                        "name": "test_case_generation",
                        "description": "測試用例生成能力",
                        "input_types": ["text", "json"],
                        "output_types": ["json"]
                    },
                    {
                        "name": "integration_testing",
                        "description": "集成測試能力",
                        "input_types": ["json"],
                        "output_types": ["json"]
                    },
                    {
                        "name": "ui_testing",
                        "description": "UI測試能力",
                        "input_types": ["json"],
                        "output_types": ["json"]
                    }
                ]
            },
            {
                "id": "system_monitor_adapter_mcp",
                "name": "SystemMonitor_Adapter MCP",
                "type": "mcp_component",
                "description": "系統監控適配器MCP組件，提供系統資源監控能力",
                "capabilities": [
                    {
                        "name": "cpu_monitoring",
                        "description": "CPU使用率監控",
                        "input_types": ["text"],
                        "output_types": ["json"]
                    },
                    {
                        "name": "memory_monitoring", 
                        "description": "內存使用監控",
                        "input_types": ["text"],
                        "output_types": ["json"]
                    },
                    {
                        "name": "disk_monitoring",
                        "description": "磁盤使用監控",
                        "input_types": ["text"],
                        "output_types": ["json"]
                    },
                    {
                        "name": "system_health_check",
                        "description": "系統健康檢查",
                        "input_types": ["text"],
                        "output_types": ["json"]
                    }
                ]
            },
            {
                "id": "file_processor_adapter_mcp",
                "name": "FileProcessor_Adapter MCP", 
                "type": "mcp_component",
                "description": "文件處理適配器MCP組件，提供文件操作和分析能力",
                "capabilities": [
                    {
                        "name": "file_read",
                        "description": "文件讀取能力",
                        "input_types": ["text"],
                        "output_types": ["text", "json"]
                    },
                    {
                        "name": "file_write",
                        "description": "文件寫入能力", 
                        "input_types": ["text", "json"],
                        "output_types": ["text"]
                    },
                    {
                        "name": "file_analysis",
                        "description": "文件分析能力",
                        "input_types": ["text"],
                        "output_types": ["json"]
                    },
                    {
                        "name": "batch_file_processing",
                        "description": "批量文件處理能力",
                        "input_types": ["json"],
                        "output_types": ["json"]
                    }
                ]
            },
            {
                "id": "recorder_workflow_mcp",
                "name": "Recorder_Workflow MCP",
                "type": "mcp_component",
                "description": "工作流錄製和管理的MCP組件，提供工作流錄製、會話管理和數據處理能力",
                "capabilities": [
                    {
                        "name": "workflow_recording",
                        "description": "工作流錄製能力，支持多種工作流類型",
                        "input_types": ["json"],
                        "output_types": ["json"]
                    },
                    {
                        "name": "session_management",
                        "description": "錄製會話管理能力",
                        "input_types": ["json"],
                        "output_types": ["json"]
                    },
                    {
                        "name": "data_processing",
                        "description": "工作流數據處理和分析能力",
                        "input_types": ["json"],
                        "output_types": ["json"]
                    },
                    {
                        "name": "step_tracking",
                        "description": "工作流步驟追蹤能力",
                        "input_types": ["json"],
                        "output_types": ["json"]
                    },
                    {
                        "name": "result_export",
                        "description": "錄製結果導出能力，支持多種格式",
                        "input_types": ["json"],
                        "output_types": ["json", "csv"]
                    }
                ]
            },
            {
                "id": "local_mcp_adapter",
                "name": "Local MCP Adapter",
                "type": "mcp_component",
                "description": "端側MCP適配器，提供工具註冊、心跳管理和智慧路由功能",
                "module_path": "components.local_mcp_adapter",
                "class_name": "LocalMCPAdapter",
                "capabilities": [
                    {
                        "name": "tool_registration",
                        "description": "向中央註冊中心註冊本地工具",
                        "input_types": ["json"],
                        "output_types": ["json"],
                        "parameters": {
                            "tool_info": "dict",
                            "capabilities": "list",
                            "endpoint": "string"
                        }
                    },
                    {
                        "name": "heartbeat_management",
                        "description": "維持與雲端的連接狀態",
                        "input_types": ["json"],
                        "output_types": ["json"],
                        "parameters": {
                            "interval": "int",
                            "timeout": "int"
                        }
                    },
                    {
                        "name": "smart_routing",
                        "description": "根據負載和可用性進行智能路由",
                        "input_types": ["json"],
                        "output_types": ["json"],
                        "parameters": {
                            "capability": "string",
                            "priority": "string",
                            "timeout": "float"
                        }
                    },
                    {
                        "name": "load_monitoring",
                        "description": "監控系統負載和性能指標",
                        "input_types": ["json"],
                        "output_types": ["json"],
                        "parameters": {
                            "metrics_type": "string"
                        }
                    }
                ]
            },
            {
                "id": "smartinvention_adapter_mcp",
                "name": "Smartinvention_Adapter MCP",
                "type": "mcp_component",
                "description": "智能發明適配器MCP組件，整合EC2功能，支持端側local model連接和對話智能分析",
                "module_path": "components.smartinvention_adapter_mcp",
                "class_name": "SmartinventionAdapterMCP",
                "capabilities": [
                    {
                        "name": "conversation_processing",
                        "description": "智能對話處理和分析",
                        "input_types": ["json", "list"],
                        "output_types": ["json"],
                        "parameters": {
                            "conversations": "array",
                            "metadata": "object",
                            "analysis_type": "string"
                        }
                    },
                    {
                        "name": "local_model_management",
                        "description": "本地模型連接和管理",
                        "input_types": ["json"],
                        "output_types": ["json"],
                        "parameters": {
                            "model_name": "string",
                            "endpoint": "string",
                            "model_type": "string",
                            "config": "object"
                        }
                    },
                    {
                        "name": "data_synchronization",
                        "description": "數據同步管理",
                        "input_types": ["json"],
                        "output_types": ["json"],
                        "parameters": {
                            "sync_direction": "string",
                            "data_type": "string"
                        }
                    },
                    {
                        "name": "system_management",
                        "description": "系統管理和監控",
                        "input_types": ["json"],
                        "output_types": ["json"],
                        "parameters": {
                            "include_details": "boolean"
                        }
                    }
                ]
            }
        ]
        
        for tool_config in default_tools:
            capabilities = []
            for cap_config in tool_config.get('capabilities', []):
                capability = ToolCapability(
                    name=cap_config['name'],
                    description=cap_config['description'],
                    input_types=cap_config['input_types'],
                    output_types=cap_config['output_types']
                )
                capabilities.append(capability)
            
            # 根據工具類型設置正確的ToolType和標籤
            tool_type = tool_config.get('type', 'python_module')
            if tool_type == 'mcp_component':
                tool_type_enum = ToolType.MCP_SERVICE
                tags = ['mcp', 'component', 'integrated']
                version = "2.0.0"
            else:
                tool_type_enum = ToolType.PYTHON_MODULE
                tags = ['default', 'fallback']
                version = "1.0.0"
            
            tool_info = ToolInfo(
                id=tool_config['id'],
                name=tool_config['name'],
                type=tool_type_enum,
                description=tool_config['description'],
                version=version,
                capabilities=capabilities,
                status=ToolStatus.AVAILABLE,
                tags=tags
            )
            
            await self.register_tool(tool_info)
    
    async def register_tool(self, tool_info: ToolInfo):
        """註冊工具"""
        self.tools[tool_info.id] = tool_info
        
        # 更新能力索引
        for capability in tool_info.capabilities:
            if capability.name not in self.capability_index:
                self.capability_index[capability.name] = []
            self.capability_index[capability.name].append(tool_info.id)
        
        # 更新標籤索引
        for tag in tool_info.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            self.tag_index[tag].append(tool_info.id)
        
        logger.info(f"Tool registered: {tool_info.id}")
    
    async def get_available_tools(self) -> List[str]:
        """獲取可用工具列表"""
        available_tools = []
        for tool_id, tool_info in self.tools.items():
            if tool_info.status == ToolStatus.AVAILABLE:
                available_tools.append(tool_id)
        return available_tools
    
    async def get_tool_info(self, tool_id: str) -> Optional[ToolInfo]:
        """獲取工具信息"""
        return self.tools.get(tool_id)
    
    async def find_tools_by_capability(self, capability: str) -> List[str]:
        """根據能力查找工具"""
        return self.capability_index.get(capability, [])
    
    async def find_tools_by_tag(self, tag: str) -> List[str]:
        """根據標籤查找工具"""
        return self.tag_index.get(tag, [])
    
    async def find_tools_by_type(self, tool_type: ToolType) -> List[str]:
        """根據類型查找工具"""
        matching_tools = []
        for tool_id, tool_info in self.tools.items():
            if tool_info.type == tool_type:
                matching_tools.append(tool_id)
        return matching_tools
    
    async def health_check_all(self):
        """檢查所有工具健康狀態"""
        logger.info("Performing health check on all tools...")
        
        for tool_id, tool_info in self.tools.items():
            try:
                await self.health_check_tool(tool_id)
            except Exception as e:
                logger.warning(f"Health check failed for tool {tool_id}: {e}")
    
    async def health_check_tool(self, tool_id: str) -> bool:
        """檢查單個工具健康狀態"""
        tool_info = self.tools.get(tool_id)
        if not tool_info:
            return False
        
        try:
            if tool_info.health_check_url:
                async with aiohttp.ClientSession() as session:
                    async with session.get(tool_info.health_check_url, timeout=5) as response:
                        if response.status == 200:
                            tool_info.status = ToolStatus.AVAILABLE
                            tool_info.last_health_check = str(asyncio.get_event_loop().time())
                            return True
                        else:
                            tool_info.status = ToolStatus.UNAVAILABLE
                            return False
            else:
                # 對於沒有健康檢查URL的工具，假設可用
                tool_info.status = ToolStatus.AVAILABLE
                return True
                
        except Exception as e:
            tool_info.status = ToolStatus.ERROR
            logger.warning(f"Health check failed for {tool_id}: {e}")
            return False
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """獲取註冊系統統計信息"""
        total_tools = len(self.tools)
        available_tools = len([t for t in self.tools.values() if t.status == ToolStatus.AVAILABLE])
        
        type_distribution = {}
        for tool_info in self.tools.values():
            tool_type = tool_info.type.value
            type_distribution[tool_type] = type_distribution.get(tool_type, 0) + 1
        
        return {
            'total_tools': total_tools,
            'available_tools': available_tools,
            'unavailable_tools': total_tools - available_tools,
            'type_distribution': type_distribution,
            'total_capabilities': len(self.capability_index),
            'total_tags': len(self.tag_index)
        }
    
    def export_registry(self) -> Dict[str, Any]:
        """導出註冊信息"""
        return {
            'tools': {tool_id: asdict(tool_info) for tool_id, tool_info in self.tools.items()},
            'capability_index': self.capability_index,
            'tag_index': self.tag_index,
            'stats': self.get_registry_stats()
        }

# 工廠函數
def create_tool_registry(config: Dict[str, Any] = None) -> ToolRegistry:
    """創建Tool Registry實例"""
    return ToolRegistry(config)

# 示例使用
async def example_usage():
    """示例用法"""
    # 創建Tool Registry
    registry = create_tool_registry({
        'auto_discovery': True,
        'discovery_paths': ['/opt/tools']
    })
    
    # 初始化
    await registry.initialize()
    
    # 獲取可用工具
    available_tools = await registry.get_available_tools()
    print(f"Available tools: {available_tools}")
    
    # 根據能力查找工具
    monitoring_tools = await registry.find_tools_by_capability('monitoring')
    print(f"Monitoring tools: {monitoring_tools}")
    
    # 獲取統計信息
    stats = registry.get_registry_stats()
    print(f"Registry stats: {stats}")

if __name__ == "__main__":
    asyncio.run(example_usage())

