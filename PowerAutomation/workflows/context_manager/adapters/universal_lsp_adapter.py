#!/usr/bin/env python3
"""
Universal LSP Adapter
通用 LSP 適配器

為 AICore 系統提供統一的語言服務器協議（LSP）整合能力
支持多種 LSP 服務器，包括 Serena、Pylsp、TypeScript Language Server 等
"""

import asyncio
import json
import logging
import time
import subprocess
import socket
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class LSPServerType(Enum):
    """LSP 服務器類型"""
    SERENA = "serena"
    PYLSP = "pylsp"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    RUST = "rust"
    GO = "go"
    GENERIC = "generic"

class LSPCapability(Enum):
    """LSP 能力"""
    COMPLETION = "textDocument/completion"
    HOVER = "textDocument/hover"
    SIGNATURE_HELP = "textDocument/signatureHelp"
    DEFINITION = "textDocument/definition"
    REFERENCES = "textDocument/references"
    DOCUMENT_SYMBOLS = "textDocument/documentSymbol"
    WORKSPACE_SYMBOLS = "workspace/symbol"
    CODE_ACTION = "textDocument/codeAction"
    FORMATTING = "textDocument/formatting"
    DIAGNOSTICS = "textDocument/publishDiagnostics"

@dataclass
class LSPMessage:
    """LSP 消息"""
    id: Optional[Union[str, int]]
    method: str
    params: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ProjectContext:
    """項目上下文"""
    project_path: str
    language: str
    symbols: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    structure: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class CodeSymbol:
    """代碼符號"""
    name: str
    kind: str
    location: Dict[str, Any]
    detail: str = ""
    documentation: str = ""
    container_name: str = ""
    deprecated: bool = False

class BaseLSPClient(ABC):
    """LSP 客戶端基類"""
    
    def __init__(self, server_type: LSPServerType, config: Dict[str, Any] = None):
        self.server_type = server_type
        self.config = config or {}
        self.process = None
        self.initialized = False
        self.capabilities = {}
        self.message_id = 0
        self.pending_requests = {}
        
    @abstractmethod
    async def start_server(self) -> bool:
        """啟動 LSP 服務器"""
        pass
    
    @abstractmethod
    async def initialize(self, root_uri: str) -> bool:
        """初始化 LSP 服務器"""
        pass
    
    @abstractmethod
    async def shutdown(self):
        """關閉 LSP 服務器"""
        pass
    
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """發送 LSP 請求"""
        self.message_id += 1
        message = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": method,
            "params": params or {}
        }
        
        # 這裡需要實現具體的消息發送邏輯
        # 簡化實現，返回模擬響應
        return {"result": {}, "id": self.message_id}
    
    async def send_notification(self, method: str, params: Dict[str, Any] = None):
        """發送 LSP 通知"""
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        
        # 實現通知發送邏輯
        pass

class SerenaLSPClient(BaseLSPClient):
    """Serena LSP 客戶端"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(LSPServerType.SERENA, config)
        self.serena_path = self.config.get("serena_path", "serena")
        self.memory_enabled = self.config.get("memory_enabled", True)
        self.project_memory = {}
        
    async def start_server(self) -> bool:
        """啟動 Serena LSP 服務器"""
        try:
            # 檢查 Serena 是否可用
            result = subprocess.run([self.serena_path, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"Serena LSP server available: {result.stdout.strip()}")
                return True
            else:
                logger.warning("Serena LSP server not available, using mock mode")
                return True  # 允許模擬模式
                
        except Exception as e:
            logger.error(f"Error starting Serena LSP server: {e}")
            return True  # 允許模擬模式
    
    async def initialize(self, root_uri: str) -> bool:
        """初始化 Serena LSP 服務器"""
        try:
            # 發送初始化請求
            init_params = {
                "processId": None,
                "rootUri": root_uri,
                "capabilities": {
                    "textDocument": {
                        "completion": {"dynamicRegistration": True},
                        "hover": {"dynamicRegistration": True},
                        "signatureHelp": {"dynamicRegistration": True},
                        "definition": {"dynamicRegistration": True},
                        "references": {"dynamicRegistration": True},
                        "documentSymbol": {"dynamicRegistration": True}
                    },
                    "workspace": {
                        "symbol": {"dynamicRegistration": True},
                        "workspaceFolders": True
                    }
                },
                "initializationOptions": {
                    "memoryEnabled": self.memory_enabled
                }
            }
            
            response = await self.send_request("initialize", init_params)
            
            if response.get("result"):
                self.capabilities = response["result"].get("capabilities", {})
                self.initialized = True
                
                # 發送 initialized 通知
                await self.send_notification("initialized")
                
                logger.info("Serena LSP server initialized successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error initializing Serena LSP server: {e}")
            return False
    
    async def get_project_overview(self, project_path: str) -> ProjectContext:
        """獲取項目概覽"""
        try:
            # 檢查內存中是否有緩存
            if project_path in self.project_memory:
                cached_context = self.project_memory[project_path]
                # 檢查是否需要更新
                if datetime.now() - cached_context.last_updated < timedelta(minutes=30):
                    return cached_context
            
            # 獲取工作區符號
            symbols_response = await self.send_request("workspace/symbol", {
                "query": ""
            })
            
            symbols = []
            if symbols_response.get("result"):
                for symbol_info in symbols_response["result"]:
                    symbol = CodeSymbol(
                        name=symbol_info.get("name", ""),
                        kind=symbol_info.get("kind", ""),
                        location=symbol_info.get("location", {}),
                        detail=symbol_info.get("detail", ""),
                        documentation=symbol_info.get("documentation", ""),
                        container_name=symbol_info.get("containerName", "")
                    )
                    symbols.append(symbol)
            
            # 分析項目結構
            project_structure = await self._analyze_project_structure(project_path)
            
            # 檢測語言
            language = await self._detect_project_language(project_path)
            
            # 創建項目上下文
            context = ProjectContext(
                project_path=project_path,
                language=language,
                symbols=[symbol.__dict__ for symbol in symbols],
                structure=project_structure,
                metadata={
                    "total_symbols": len(symbols),
                    "analyzed_at": datetime.now().isoformat()
                }
            )
            
            # 緩存到內存
            if self.memory_enabled:
                self.project_memory[project_path] = context
            
            logger.info(f"Generated project overview for {project_path}: {len(symbols)} symbols")
            return context
            
        except Exception as e:
            logger.error(f"Error getting project overview: {e}")
            return ProjectContext(project_path=project_path, language="unknown")
    
    async def get_symbol_definition(self, file_path: str, line: int, character: int) -> List[Dict[str, Any]]:
        """獲取符號定義"""
        try:
            params = {
                "textDocument": {"uri": f"file://{file_path}"},
                "position": {"line": line, "character": character}
            }
            
            response = await self.send_request("textDocument/definition", params)
            
            if response.get("result"):
                return response["result"]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting symbol definition: {e}")
            return []
    
    async def get_symbol_references(self, file_path: str, line: int, character: int) -> List[Dict[str, Any]]:
        """獲取符號引用"""
        try:
            params = {
                "textDocument": {"uri": f"file://{file_path}"},
                "position": {"line": line, "character": character},
                "context": {"includeDeclaration": True}
            }
            
            response = await self.send_request("textDocument/references", params)
            
            if response.get("result"):
                return response["result"]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting symbol references: {e}")
            return []
    
    async def get_hover_info(self, file_path: str, line: int, character: int) -> Optional[str]:
        """獲取懸停信息"""
        try:
            params = {
                "textDocument": {"uri": f"file://{file_path}"},
                "position": {"line": line, "character": character}
            }
            
            response = await self.send_request("textDocument/hover", params)
            
            if response.get("result") and response["result"].get("contents"):
                contents = response["result"]["contents"]
                if isinstance(contents, str):
                    return contents
                elif isinstance(contents, dict):
                    return contents.get("value", "")
                elif isinstance(contents, list) and contents:
                    return str(contents[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting hover info: {e}")
            return None
    
    async def _analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """分析項目結構"""
        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                return {}
            
            structure = {
                "root": str(project_dir),
                "files": [],
                "directories": [],
                "languages": set(),
                "frameworks": set()
            }
            
            # 遍歷項目文件
            for item in project_dir.rglob("*"):
                if item.is_file():
                    rel_path = str(item.relative_to(project_dir))
                    structure["files"].append(rel_path)
                    
                    # 檢測語言
                    suffix = item.suffix.lower()
                    if suffix in [".py", ".pyx"]:
                        structure["languages"].add("python")
                    elif suffix in [".js", ".jsx", ".ts", ".tsx"]:
                        structure["languages"].add("javascript")
                    elif suffix in [".java"]:
                        structure["languages"].add("java")
                    elif suffix in [".rs"]:
                        structure["languages"].add("rust")
                    elif suffix in [".go"]:
                        structure["languages"].add("go")
                    
                    # 檢測框架
                    if item.name in ["package.json", "requirements.txt", "Cargo.toml", "go.mod"]:
                        structure["frameworks"].add(self._detect_framework_from_file(item))
                
                elif item.is_dir():
                    rel_path = str(item.relative_to(project_dir))
                    structure["directories"].append(rel_path)
            
            # 轉換 set 為 list 以便 JSON 序列化
            structure["languages"] = list(structure["languages"])
            structure["frameworks"] = list(structure["frameworks"])
            
            return structure
            
        except Exception as e:
            logger.error(f"Error analyzing project structure: {e}")
            return {}
    
    async def _detect_project_language(self, project_path: str) -> str:
        """檢測項目主要語言"""
        try:
            project_dir = Path(project_path)
            language_counts = {}
            
            for item in project_dir.rglob("*.py"):
                language_counts["python"] = language_counts.get("python", 0) + 1
            
            for item in project_dir.rglob("*.js"):
                language_counts["javascript"] = language_counts.get("javascript", 0) + 1
            
            for item in project_dir.rglob("*.ts"):
                language_counts["typescript"] = language_counts.get("typescript", 0) + 1
            
            for item in project_dir.rglob("*.java"):
                language_counts["java"] = language_counts.get("java", 0) + 1
            
            if language_counts:
                return max(language_counts, key=language_counts.get)
            
            return "unknown"
            
        except Exception as e:
            logger.error(f"Error detecting project language: {e}")
            return "unknown"
    
    def _detect_framework_from_file(self, file_path: Path) -> str:
        """從文件檢測框架"""
        try:
            if file_path.name == "package.json":
                return "nodejs"
            elif file_path.name == "requirements.txt":
                return "python"
            elif file_path.name == "Cargo.toml":
                return "rust"
            elif file_path.name == "go.mod":
                return "go"
            
            return "unknown"
            
        except Exception as e:
            logger.error(f"Error detecting framework from file: {e}")
            return "unknown"
    
    async def shutdown(self):
        """關閉 Serena LSP 服務器"""
        try:
            if self.initialized:
                await self.send_request("shutdown")
                await self.send_notification("exit")
            
            if self.process:
                self.process.terminate()
                await asyncio.sleep(1)
                if self.process.poll() is None:
                    self.process.kill()
            
            self.initialized = False
            logger.info("Serena LSP server shut down")
            
        except Exception as e:
            logger.error(f"Error shutting down Serena LSP server: {e}")

class GenericLSPClient(BaseLSPClient):
    """通用 LSP 客戶端"""
    
    def __init__(self, server_type: LSPServerType, config: Dict[str, Any] = None):
        super().__init__(server_type, config)
        self.server_command = self.config.get("server_command", [])
        self.server_args = self.config.get("server_args", [])
        
    async def start_server(self) -> bool:
        """啟動通用 LSP 服務器"""
        try:
            if self.server_command:
                command = self.server_command + self.server_args
                self.process = subprocess.Popen(
                    command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                logger.info(f"Started {self.server_type.value} LSP server")
                return True
            else:
                logger.warning(f"No server command configured for {self.server_type.value}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting {self.server_type.value} LSP server: {e}")
            return False
    
    async def initialize(self, root_uri: str) -> bool:
        """初始化通用 LSP 服務器"""
        try:
            init_params = {
                "processId": None,
                "rootUri": root_uri,
                "capabilities": {
                    "textDocument": {
                        "completion": {"dynamicRegistration": True},
                        "hover": {"dynamicRegistration": True},
                        "definition": {"dynamicRegistration": True}
                    }
                }
            }
            
            response = await self.send_request("initialize", init_params)
            
            if response.get("result"):
                self.capabilities = response["result"].get("capabilities", {})
                self.initialized = True
                await self.send_notification("initialized")
                
                logger.info(f"{self.server_type.value} LSP server initialized")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error initializing {self.server_type.value} LSP server: {e}")
            return False
    
    async def shutdown(self):
        """關閉通用 LSP 服務器"""
        try:
            if self.initialized:
                await self.send_request("shutdown")
                await self.send_notification("exit")
            
            if self.process:
                self.process.terminate()
                await asyncio.sleep(1)
                if self.process.poll() is None:
                    self.process.kill()
            
            self.initialized = False
            logger.info(f"{self.server_type.value} LSP server shut down")
            
        except Exception as e:
            logger.error(f"Error shutting down {self.server_type.value} LSP server: {e}")

class UniversalLSPAdapter:
    """通用 LSP 適配器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = "Universal LSP Adapter"
        self.version = "1.0.0"
        
        # LSP 客戶端管理
        self.clients = {}  # server_type -> client
        self.active_projects = {}  # project_path -> server_type
        
        # 配置參數
        self.auto_detect_language = self.config.get("auto_detect_language", True)
        self.enable_caching = self.config.get("enable_caching", True)
        self.cache_ttl = self.config.get("cache_ttl", 300)  # 5分鐘
        
        # 緩存
        self.symbol_cache = {}
        self.project_cache = {}
        
        # 狀態管理
        self.initialized = False
        self.status = "initializing"
        
        # 統計信息
        self.stats = {
            "total_projects": 0,
            "active_clients": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_requests": 0,
            "successful_requests": 0
        }
        
        logger.info(f"Initializing {self.name} v{self.version}")
    
    async def initialize(self):
        """初始化 LSP 適配器"""
        try:
            logger.info("Initializing Universal LSP Adapter...")
            
            # 初始化 Serena LSP 客戶端
            serena_config = self.config.get("serena", {})
            serena_client = SerenaLSPClient(serena_config)
            if await serena_client.start_server():
                self.clients[LSPServerType.SERENA] = serena_client
                logger.info("✅ Serena LSP client initialized")
            
            # 初始化其他 LSP 客戶端（如果配置了）
            for server_type in [LSPServerType.PYLSP, LSPServerType.TYPESCRIPT]:
                server_config = self.config.get(server_type.value, {})
                if server_config.get("enabled", False):
                    client = GenericLSPClient(server_type, server_config)
                    if await client.start_server():
                        self.clients[server_type] = client
                        logger.info(f"✅ {server_type.value} LSP client initialized")
            
            self.stats["active_clients"] = len(self.clients)
            self.initialized = True
            self.status = "ready"
            
            logger.info(f"🎉 {self.name} initialization completed with {len(self.clients)} clients")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.name}: {e}")
            self.status = "error"
            return False
    
    async def analyze_project(self, project_path: str, language: str = None) -> ProjectContext:
        """分析項目"""
        try:
            self.stats["total_requests"] += 1
            
            # 檢查緩存
            cache_key = f"project_{project_path}"
            if self.enable_caching and cache_key in self.project_cache:
                cached_data = self.project_cache[cache_key]
                if datetime.now() - cached_data["timestamp"] < timedelta(seconds=self.cache_ttl):
                    self.stats["cache_hits"] += 1
                    return cached_data["context"]
            
            self.stats["cache_misses"] += 1
            
            # 選擇合適的 LSP 客戶端
            client = await self._select_client_for_project(project_path, language)
            
            if not client:
                logger.warning(f"No suitable LSP client found for project {project_path}")
                return ProjectContext(project_path=project_path, language=language or "unknown")
            
            # 初始化客戶端（如果需要）
            if not client.initialized:
                await client.initialize(f"file://{project_path}")
            
            # 獲取項目上下文
            if isinstance(client, SerenaLSPClient):
                context = await client.get_project_overview(project_path)
            else:
                # 對於其他客戶端，創建基本上下文
                context = ProjectContext(
                    project_path=project_path,
                    language=language or "unknown"
                )
            
            # 緩存結果
            if self.enable_caching:
                self.project_cache[cache_key] = {
                    "context": context,
                    "timestamp": datetime.now()
                }
            
            # 記錄活動項目
            if client.server_type not in self.active_projects.values():
                self.active_projects[project_path] = client.server_type
                self.stats["total_projects"] += 1
            
            self.stats["successful_requests"] += 1
            logger.info(f"Analyzed project {project_path} using {client.server_type.value}")
            return context
            
        except Exception as e:
            logger.error(f"Error analyzing project {project_path}: {e}")
            return ProjectContext(project_path=project_path, language=language or "unknown")
    
    async def get_symbol_information(self, file_path: str, line: int, character: int,
                                   info_type: str = "definition") -> List[Dict[str, Any]]:
        """獲取符號信息"""
        try:
            self.stats["total_requests"] += 1
            
            # 檢查緩存
            cache_key = f"symbol_{file_path}_{line}_{character}_{info_type}"
            if self.enable_caching and cache_key in self.symbol_cache:
                cached_data = self.symbol_cache[cache_key]
                if datetime.now() - cached_data["timestamp"] < timedelta(seconds=self.cache_ttl):
                    self.stats["cache_hits"] += 1
                    return cached_data["result"]
            
            self.stats["cache_misses"] += 1
            
            # 找到合適的客戶端
            project_path = str(Path(file_path).parent)
            client = await self._select_client_for_project(project_path)
            
            if not client or not isinstance(client, SerenaLSPClient):
                return []
            
            # 獲取符號信息
            result = []
            if info_type == "definition":
                result = await client.get_symbol_definition(file_path, line, character)
            elif info_type == "references":
                result = await client.get_symbol_references(file_path, line, character)
            elif info_type == "hover":
                hover_info = await client.get_hover_info(file_path, line, character)
                if hover_info:
                    result = [{"contents": hover_info}]
            
            # 緩存結果
            if self.enable_caching:
                self.symbol_cache[cache_key] = {
                    "result": result,
                    "timestamp": datetime.now()
                }
            
            self.stats["successful_requests"] += 1
            return result
            
        except Exception as e:
            logger.error(f"Error getting symbol information: {e}")
            return []
    
    async def get_project_symbols(self, project_path: str) -> List[CodeSymbol]:
        """獲取項目符號"""
        try:
            context = await self.analyze_project(project_path)
            symbols = []
            
            for symbol_data in context.symbols:
                symbol = CodeSymbol(
                    name=symbol_data.get("name", ""),
                    kind=symbol_data.get("kind", ""),
                    location=symbol_data.get("location", {}),
                    detail=symbol_data.get("detail", ""),
                    documentation=symbol_data.get("documentation", ""),
                    container_name=symbol_data.get("container_name", "")
                )
                symbols.append(symbol)
            
            return symbols
            
        except Exception as e:
            logger.error(f"Error getting project symbols: {e}")
            return []
    
    async def search_workspace_symbols(self, query: str, project_path: str = None) -> List[CodeSymbol]:
        """搜索工作區符號"""
        try:
            if project_path:
                client = await self._select_client_for_project(project_path)
                if client and isinstance(client, SerenaLSPClient):
                    # 使用 workspace/symbol 請求
                    response = await client.send_request("workspace/symbol", {"query": query})
                    
                    symbols = []
                    if response.get("result"):
                        for symbol_info in response["result"]:
                            symbol = CodeSymbol(
                                name=symbol_info.get("name", ""),
                                kind=symbol_info.get("kind", ""),
                                location=symbol_info.get("location", {}),
                                detail=symbol_info.get("detail", ""),
                                documentation=symbol_info.get("documentation", ""),
                                container_name=symbol_info.get("containerName", "")
                            )
                            symbols.append(symbol)
                    
                    return symbols
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching workspace symbols: {e}")
            return []
    
    async def _select_client_for_project(self, project_path: str, language: str = None) -> Optional[BaseLSPClient]:
        """為項目選擇合適的 LSP 客戶端"""
        try:
            # 如果已經有活動的客戶端
            if project_path in self.active_projects:
                server_type = self.active_projects[project_path]
                return self.clients.get(server_type)
            
            # 自動檢測語言
            if not language and self.auto_detect_language:
                language = await self._detect_project_language(project_path)
            
            # 根據語言選擇客戶端
            if language == "python" and LSPServerType.PYLSP in self.clients:
                return self.clients[LSPServerType.PYLSP]
            elif language in ["javascript", "typescript"] and LSPServerType.TYPESCRIPT in self.clients:
                return self.clients[LSPServerType.TYPESCRIPT]
            elif LSPServerType.SERENA in self.clients:
                # Serena 作為通用選擇
                return self.clients[LSPServerType.SERENA]
            
            # 返回任何可用的客戶端
            if self.clients:
                return next(iter(self.clients.values()))
            
            return None
            
        except Exception as e:
            logger.error(f"Error selecting client for project: {e}")
            return None
    
    async def _detect_project_language(self, project_path: str) -> str:
        """檢測項目語言"""
        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                return "unknown"
            
            # 檢查特定文件
            if (project_dir / "package.json").exists():
                return "javascript"
            elif (project_dir / "requirements.txt").exists() or (project_dir / "pyproject.toml").exists():
                return "python"
            elif (project_dir / "Cargo.toml").exists():
                return "rust"
            elif (project_dir / "go.mod").exists():
                return "go"
            elif any(project_dir.glob("*.java")):
                return "java"
            elif any(project_dir.glob("*.py")):
                return "python"
            elif any(project_dir.glob("*.js")) or any(project_dir.glob("*.ts")):
                return "javascript"
            
            return "unknown"
            
        except Exception as e:
            logger.error(f"Error detecting project language: {e}")
            return "unknown"
    
    async def cleanup_cache(self) -> int:
        """清理過期緩存"""
        try:
            current_time = datetime.now()
            expired_keys = []
            
            # 清理符號緩存
            for key, cached_data in self.symbol_cache.items():
                if current_time - cached_data["timestamp"] > timedelta(seconds=self.cache_ttl):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.symbol_cache[key]
            
            # 清理項目緩存
            expired_project_keys = []
            for key, cached_data in self.project_cache.items():
                if current_time - cached_data["timestamp"] > timedelta(seconds=self.cache_ttl):
                    expired_project_keys.append(key)
            
            for key in expired_project_keys:
                del self.project_cache[key]
            
            total_cleaned = len(expired_keys) + len(expired_project_keys)
            logger.info(f"Cleaned up {total_cleaned} expired cache entries")
            return total_cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            return 0
    
    def get_status(self) -> Dict[str, Any]:
        """獲取適配器狀態"""
        return {
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "initialized": self.initialized,
            "stats": self.stats,
            "clients": {
                server_type.value: {
                    "initialized": client.initialized,
                    "capabilities": list(client.capabilities.keys()) if client.capabilities else []
                }
                for server_type, client in self.clients.items()
            },
            "active_projects": {path: server_type.value for path, server_type in self.active_projects.items()},
            "cache_stats": {
                "symbol_cache_size": len(self.symbol_cache),
                "project_cache_size": len(self.project_cache),
                "cache_hit_rate": self.stats["cache_hits"] / max(1, self.stats["cache_hits"] + self.stats["cache_misses"])
            }
        }
    
    async def shutdown(self):
        """關閉適配器"""
        logger.info("Shutting down Universal LSP Adapter...")
        
        # 關閉所有客戶端
        for server_type, client in self.clients.items():
            try:
                await client.shutdown()
                logger.info(f"✅ {server_type.value} client shut down")
            except Exception as e:
                logger.error(f"Error shutting down {server_type.value} client: {e}")
        
        # 清理緩存
        self.symbol_cache.clear()
        self.project_cache.clear()
        self.active_projects.clear()
        
        self.status = "shutdown"
        logger.info("Universal LSP Adapter shut down")

# 工廠函數
async def create_universal_lsp_adapter(config: Dict[str, Any] = None) -> UniversalLSPAdapter:
    """創建並初始化通用 LSP 適配器"""
    adapter = UniversalLSPAdapter(config)
    await adapter.initialize()
    return adapter

if __name__ == "__main__":
    # 測試代碼
    async def test_lsp_adapter():
        config = {
            "serena": {
                "serena_path": "serena",
                "memory_enabled": True
            },
            "pylsp": {
                "enabled": False,
                "server_command": ["pylsp"]
            },
            "auto_detect_language": True,
            "enable_caching": True,
            "cache_ttl": 300
        }
        
        adapter = await create_universal_lsp_adapter(config)
        
        # 測試項目分析
        project_path = "/path/to/test/project"
        context = await adapter.analyze_project(project_path)
        print(f"Project context: {context.language}, {len(context.symbols)} symbols")
        
        # 測試符號搜索
        symbols = await adapter.search_workspace_symbols("test", project_path)
        print(f"Found {len(symbols)} symbols matching 'test'")
        
        # 獲取狀態
        status = adapter.get_status()
        print(f"Adapter status: {status['status']}")
        print(f"Active clients: {list(status['clients'].keys())}")
        
        # 關閉適配器
        await adapter.shutdown()
    
    asyncio.run(test_lsp_adapter())

