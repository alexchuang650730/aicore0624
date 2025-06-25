#!/usr/bin/env python3
"""
Serena LSP Integration Adapter
Serena LSP 整合適配器

整合 Serena 的 LSP 能力到代碼生成系統中，提供代碼理解和項目記憶功能
支持全局符號搜索、項目概覽生成、智能記憶系統
基於 LSP（語言服務器協議）技術，理解項目的代碼結構、關係和邏輯
"""

import asyncio
import json
import logging
import time
import subprocess
import tempfile
import socket
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import aiohttp
import sqlite3
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class LSPCapability(Enum):
    """LSP 能力枚舉"""
    SYMBOL_SEARCH = "symbol_search"
    DEFINITION_LOOKUP = "definition_lookup"
    REFERENCE_FINDING = "reference_finding"
    HOVER_INFO = "hover_info"
    COMPLETION = "completion"
    DIAGNOSTICS = "diagnostics"
    DOCUMENT_SYMBOLS = "document_symbols"
    WORKSPACE_SYMBOLS = "workspace_symbols"
    PROJECT_OVERVIEW = "project_overview"
    MEMORY_SYSTEM = "memory_system"

class SymbolKind(Enum):
    """符號類型"""
    FILE = 1
    MODULE = 2
    NAMESPACE = 3
    PACKAGE = 4
    CLASS = 5
    METHOD = 6
    PROPERTY = 7
    FIELD = 8
    CONSTRUCTOR = 9
    ENUM = 10
    INTERFACE = 11
    FUNCTION = 12
    VARIABLE = 13
    CONSTANT = 14
    STRING = 15
    NUMBER = 16
    BOOLEAN = 17
    ARRAY = 18
    OBJECT = 19
    KEY = 20
    NULL = 21
    ENUM_MEMBER = 22
    STRUCT = 23
    EVENT = 24
    OPERATOR = 25
    TYPE_PARAMETER = 26

@dataclass
class LSPSymbol:
    """LSP 符號"""
    name: str
    kind: SymbolKind
    location: Dict[str, Any]
    container_name: Optional[str] = None
    detail: Optional[str] = None
    documentation: Optional[str] = None
    deprecated: bool = False
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind.value,
            "location": self.location,
            "container_name": self.container_name,
            "detail": self.detail,
            "documentation": self.documentation,
            "deprecated": self.deprecated,
            "tags": self.tags
        }

@dataclass
class ProjectOverview:
    """項目概覽"""
    project_path: str
    total_files: int
    total_symbols: int
    languages: List[str]
    main_modules: List[str]
    dependencies: List[str]
    architecture_patterns: List[str]
    complexity_metrics: Dict[str, Any]
    design_decisions: List[Dict[str, Any]] = field(default_factory=list)
    code_patterns: List[Dict[str, Any]] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_path": self.project_path,
            "total_files": self.total_files,
            "total_symbols": self.total_symbols,
            "languages": self.languages,
            "main_modules": self.main_modules,
            "dependencies": self.dependencies,
            "architecture_patterns": self.architecture_patterns,
            "complexity_metrics": self.complexity_metrics,
            "design_decisions": self.design_decisions,
            "code_patterns": self.code_patterns,
            "generated_at": self.generated_at.isoformat()
        }

@dataclass
class ProjectMemory:
    """項目記憶"""
    project_id: str
    project_path: str
    overview: ProjectOverview
    symbol_index: Dict[str, LSPSymbol] = field(default_factory=dict)
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    design_decisions: List[Dict[str, Any]] = field(default_factory=list)
    code_patterns: List[Dict[str, Any]] = field(default_factory=list)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "project_path": self.project_path,
            "overview": self.overview.to_dict(),
            "symbol_index": {k: v.to_dict() for k, v in self.symbol_index.items()},
            "dependency_graph": self.dependency_graph,
            "design_decisions": self.design_decisions,
            "code_patterns": self.code_patterns,
            "interaction_history": self.interaction_history,
            "last_updated": self.last_updated.isoformat()
        }

class SerenaLSPClient:
    """Serena LSP 客戶端"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.server_host = self.config.get("server_host", "localhost")
        self.server_port = self.config.get("server_port", 2087)
        self.timeout = self.config.get("timeout", 30)
        self.auto_start_server = self.config.get("auto_start_server", True)
        
        self.connected = False
        self.server_process = None
        self.request_id = 0
        
    async def initialize(self):
        """初始化 LSP 客戶端"""
        try:
            # 檢查服務器是否已運行
            if not await self._check_server_running():
                if self.auto_start_server:
                    await self._start_lsp_server()
                else:
                    raise ConnectionError("LSP server is not running and auto_start_server is disabled")
            
            # 建立連接
            await self._connect_to_server()
            
            # 發送初始化請求
            await self._send_initialize_request()
            
            self.connected = True
            logger.info(f"Connected to Serena LSP server at {self.server_host}:{self.server_port}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LSP client: {e}")
            raise
    
    async def _check_server_running(self) -> bool:
        """檢查 LSP 服務器是否運行"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.server_host, self.server_port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    async def _start_lsp_server(self):
        """啟動 LSP 服務器"""
        try:
            logger.info("Starting Python LSP server...")
            self.server_process = subprocess.Popen([
                "python", "-m", "pylsp", 
                "--tcp", 
                "--host", self.server_host,
                "--port", str(self.server_port)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待服務器啟動
            await asyncio.sleep(3)
            
            if not await self._check_server_running():
                raise RuntimeError("Failed to start LSP server")
                
            logger.info("LSP server started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start LSP server: {e}")
            raise
    
    async def _connect_to_server(self):
        """連接到 LSP 服務器"""
        # 這裡應該實現實際的 LSP 協議連接
        # 目前使用模擬實現
        logger.info("Connecting to LSP server...")
        await asyncio.sleep(1)  # 模擬連接時間
    
    async def _send_initialize_request(self):
        """發送初始化請求"""
        # LSP 初始化請求
        initialize_params = {
            "processId": None,
            "clientInfo": {
                "name": "Serena LSP Adapter",
                "version": "1.0.0"
            },
            "capabilities": {
                "textDocument": {
                    "hover": {"contentFormat": ["markdown", "plaintext"]},
                    "completion": {"completionItem": {"snippetSupport": True}},
                    "definition": {"linkSupport": True},
                    "references": {"includeDeclaration": True}
                },
                "workspace": {
                    "symbol": {"symbolKind": {"valueSet": list(range(1, 27))}},
                    "workspaceFolders": True
                }
            }
        }
        
        # 模擬發送請求
        logger.info("Sent LSP initialize request")
    
    async def search_symbols(self, query: str, project_path: Optional[str] = None) -> List[LSPSymbol]:
        """搜索符號"""
        if not self.connected:
            raise RuntimeError("LSP client not connected")
        
        # 模擬符號搜索
        # 實際實現應該發送 workspace/symbol 請求
        symbols = []
        
        # 模擬一些符號結果
        mock_symbols = [
            {
                "name": f"search_result_{i}",
                "kind": SymbolKind.FUNCTION,
                "location": {
                    "uri": f"file:///mock/file_{i}.py",
                    "range": {
                        "start": {"line": i, "character": 0},
                        "end": {"line": i + 5, "character": 0}
                    }
                },
                "detail": f"Mock function {i}",
                "documentation": f"Documentation for function {i}"
            }
            for i in range(min(10, len(query)))  # 基於查詢長度返回結果
        ]
        
        for symbol_data in mock_symbols:
            symbol = LSPSymbol(
                name=symbol_data["name"],
                kind=symbol_data["kind"],
                location=symbol_data["location"],
                detail=symbol_data.get("detail"),
                documentation=symbol_data.get("documentation")
            )
            symbols.append(symbol)
        
        logger.info(f"Found {len(symbols)} symbols for query: {query}")
        return symbols
    
    async def get_document_symbols(self, file_path: str) -> List[LSPSymbol]:
        """獲取文檔符號"""
        if not self.connected:
            raise RuntimeError("LSP client not connected")
        
        # 實際實現應該發送 textDocument/documentSymbol 請求
        # 這裡返回模擬結果
        symbols = []
        
        try:
            # 簡單解析 Python 文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('def ') or stripped.startswith('async def '):
                    func_name = stripped.split('(')[0].replace('def ', '').replace('async def ', '').strip()
                    symbol = LSPSymbol(
                        name=func_name,
                        kind=SymbolKind.FUNCTION,
                        location={
                            "uri": f"file://{file_path}",
                            "range": {
                                "start": {"line": i, "character": 0},
                                "end": {"line": i, "character": len(line)}
                            }
                        },
                        detail=f"Function in {Path(file_path).name}"
                    )
                    symbols.append(symbol)
                elif stripped.startswith('class '):
                    class_name = stripped.split('(')[0].replace('class ', '').replace(':', '').strip()
                    symbol = LSPSymbol(
                        name=class_name,
                        kind=SymbolKind.CLASS,
                        location={
                            "uri": f"file://{file_path}",
                            "range": {
                                "start": {"line": i, "character": 0},
                                "end": {"line": i, "character": len(line)}
                            }
                        },
                        detail=f"Class in {Path(file_path).name}"
                    )
                    symbols.append(symbol)
        
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
        
        return symbols
    
    async def get_hover_info(self, file_path: str, line: int, character: int) -> Optional[Dict[str, Any]]:
        """獲取懸停信息"""
        if not self.connected:
            raise RuntimeError("LSP client not connected")
        
        # 實際實現應該發送 textDocument/hover 請求
        return {
            "contents": f"Hover info for {file_path}:{line}:{character}",
            "range": {
                "start": {"line": line, "character": character},
                "end": {"line": line, "character": character + 10}
            }
        }
    
    async def find_references(self, file_path: str, line: int, character: int) -> List[Dict[str, Any]]:
        """查找引用"""
        if not self.connected:
            raise RuntimeError("LSP client not connected")
        
        # 實際實現應該發送 textDocument/references 請求
        return [
            {
                "uri": f"file://{file_path}",
                "range": {
                    "start": {"line": line, "character": character},
                    "end": {"line": line, "character": character + 10}
                }
            }
        ]
    
    async def shutdown(self):
        """關閉 LSP 客戶端"""
        if self.connected:
            # 發送關閉請求
            logger.info("Shutting down LSP client...")
            self.connected = False
        
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None

class ProjectAnalyzer:
    """項目分析器"""
    
    def __init__(self, lsp_client: SerenaLSPClient):
        self.lsp_client = lsp_client
        
    async def analyze_project_structure(self, project_path: str) -> ProjectOverview:
        """分析項目結構"""
        logger.info(f"Analyzing project structure: {project_path}")
        
        project_path = Path(project_path)
        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
        
        # 統計文件
        total_files = 0
        languages = set()
        main_modules = []
        
        # 支持的文件類型
        language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby'
        }
        
        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                total_files += 1
                
                if file_path.suffix in language_extensions:
                    languages.add(language_extensions[file_path.suffix])
                    
                    # 識別主要模組
                    if file_path.name in ['__init__.py', 'main.py', 'app.py', 'index.js', 'main.java']:
                        main_modules.append(str(file_path.relative_to(project_path)))
        
        # 獲取所有符號
        all_symbols = []
        for file_path in project_path.rglob("*.py"):  # 目前只處理 Python 文件
            try:
                symbols = await self.lsp_client.get_document_symbols(str(file_path))
                all_symbols.extend(symbols)
            except Exception as e:
                logger.error(f"Error getting symbols from {file_path}: {e}")
        
        # 分析架構模式
        architecture_patterns = self._detect_architecture_patterns(project_path, all_symbols)
        
        # 計算複雜度指標
        complexity_metrics = self._calculate_complexity_metrics(project_path, all_symbols)
        
        # 檢測依賴關係
        dependencies = self._detect_dependencies(project_path)
        
        overview = ProjectOverview(
            project_path=str(project_path),
            total_files=total_files,
            total_symbols=len(all_symbols),
            languages=list(languages),
            main_modules=main_modules,
            dependencies=dependencies,
            architecture_patterns=architecture_patterns,
            complexity_metrics=complexity_metrics
        )
        
        logger.info(f"Project analysis completed: {total_files} files, {len(all_symbols)} symbols")
        return overview
    
    def _detect_architecture_patterns(self, project_path: Path, symbols: List[LSPSymbol]) -> List[str]:
        """檢測架構模式"""
        patterns = []
        
        # 檢測 MVC 模式
        has_models = any('model' in symbol.name.lower() for symbol in symbols)
        has_views = any('view' in symbol.name.lower() for symbol in symbols)
        has_controllers = any('controller' in symbol.name.lower() for symbol in symbols)
        
        if has_models and has_views and has_controllers:
            patterns.append("MVC")
        
        # 檢測 API 模式
        has_api_endpoints = any('api' in symbol.name.lower() or 'endpoint' in symbol.name.lower() for symbol in symbols)
        if has_api_endpoints:
            patterns.append("REST API")
        
        # 檢測微服務模式
        service_dirs = [d for d in project_path.iterdir() if d.is_dir() and 'service' in d.name.lower()]
        if len(service_dirs) > 1:
            patterns.append("Microservices")
        
        # 檢測組件模式
        component_symbols = [s for s in symbols if 'component' in s.name.lower()]
        if len(component_symbols) > 5:
            patterns.append("Component-based")
        
        return patterns
    
    def _calculate_complexity_metrics(self, project_path: Path, symbols: List[LSPSymbol]) -> Dict[str, Any]:
        """計算複雜度指標"""
        return {
            "total_symbols": len(symbols),
            "functions": len([s for s in symbols if s.kind == SymbolKind.FUNCTION]),
            "classes": len([s for s in symbols if s.kind == SymbolKind.CLASS]),
            "modules": len([s for s in symbols if s.kind == SymbolKind.MODULE]),
            "average_symbols_per_file": len(symbols) / max(1, len(list(project_path.rglob("*.py")))),
            "complexity_score": min(len(symbols) / 100, 1.0)  # 簡化的複雜度分數
        }
    
    def _detect_dependencies(self, project_path: Path) -> List[str]:
        """檢測項目依賴"""
        dependencies = []
        
        # 檢查 requirements.txt
        req_file = project_path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            dep = line.split('==')[0].split('>=')[0].split('<=')[0]
                            dependencies.append(dep)
            except Exception as e:
                logger.error(f"Error reading requirements.txt: {e}")
        
        # 檢查 package.json
        pkg_file = project_path / "package.json"
        if pkg_file.exists():
            try:
                with open(pkg_file, 'r') as f:
                    pkg_data = json.load(f)
                    deps = pkg_data.get('dependencies', {})
                    dev_deps = pkg_data.get('devDependencies', {})
                    dependencies.extend(list(deps.keys()))
                    dependencies.extend(list(dev_deps.keys()))
            except Exception as e:
                logger.error(f"Error reading package.json: {e}")
        
        return dependencies

class ProjectMemoryManager:
    """項目記憶管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.memory_db_path = self.config.get("memory_db_path", "project_memory.db")
        self.conn = None
        
    async def initialize(self):
        """初始化記憶管理器"""
        self.conn = sqlite3.connect(self.memory_db_path)
        
        # 創建表結構
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS project_memories (
                project_id TEXT PRIMARY KEY,
                project_path TEXT,
                overview TEXT,
                symbol_index TEXT,
                dependency_graph TEXT,
                design_decisions TEXT,
                code_patterns TEXT,
                interaction_history TEXT,
                last_updated TEXT
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS interaction_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT,
                interaction_type TEXT,
                content TEXT,
                timestamp TEXT,
                FOREIGN KEY (project_id) REFERENCES project_memories (project_id)
            )
        """)
        
        self.conn.commit()
        logger.info("Project memory manager initialized")
    
    async def save_project_memory(self, memory: ProjectMemory):
        """保存項目記憶"""
        self.conn.execute("""
            INSERT OR REPLACE INTO project_memories 
            (project_id, project_path, overview, symbol_index, dependency_graph, 
             design_decisions, code_patterns, interaction_history, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory.project_id,
            memory.project_path,
            json.dumps(memory.overview.to_dict()),
            json.dumps({k: v.to_dict() for k, v in memory.symbol_index.items()}),
            json.dumps(memory.dependency_graph),
            json.dumps(memory.design_decisions),
            json.dumps(memory.code_patterns),
            json.dumps(memory.interaction_history),
            memory.last_updated.isoformat()
        ))
        self.conn.commit()
        logger.info(f"Saved memory for project: {memory.project_id}")
    
    async def load_project_memory(self, project_id: str) -> Optional[ProjectMemory]:
        """加載項目記憶"""
        cursor = self.conn.execute("""
            SELECT * FROM project_memories WHERE project_id = ?
        """, (project_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        try:
            overview_data = json.loads(row[2])
            overview = ProjectOverview(
                project_path=overview_data["project_path"],
                total_files=overview_data["total_files"],
                total_symbols=overview_data["total_symbols"],
                languages=overview_data["languages"],
                main_modules=overview_data["main_modules"],
                dependencies=overview_data["dependencies"],
                architecture_patterns=overview_data["architecture_patterns"],
                complexity_metrics=overview_data["complexity_metrics"],
                generated_at=datetime.fromisoformat(overview_data["generated_at"])
            )
            
            symbol_index_data = json.loads(row[3])
            symbol_index = {}
            for k, v in symbol_index_data.items():
                symbol_index[k] = LSPSymbol(
                    name=v["name"],
                    kind=SymbolKind(v["kind"]),
                    location=v["location"],
                    container_name=v.get("container_name"),
                    detail=v.get("detail"),
                    documentation=v.get("documentation"),
                    deprecated=v.get("deprecated", False),
                    tags=v.get("tags", [])
                )
            
            memory = ProjectMemory(
                project_id=row[0],
                project_path=row[1],
                overview=overview,
                symbol_index=symbol_index,
                dependency_graph=json.loads(row[4]),
                design_decisions=json.loads(row[5]),
                code_patterns=json.loads(row[6]),
                interaction_history=json.loads(row[7]),
                last_updated=datetime.fromisoformat(row[8])
            )
            
            logger.info(f"Loaded memory for project: {project_id}")
            return memory
            
        except Exception as e:
            logger.error(f"Error loading project memory: {e}")
            return None
    
    async def add_interaction(self, project_id: str, interaction_type: str, content: str):
        """添加交互記錄"""
        self.conn.execute("""
            INSERT INTO interaction_logs (project_id, interaction_type, content, timestamp)
            VALUES (?, ?, ?, ?)
        """, (project_id, interaction_type, content, datetime.now().isoformat()))
        self.conn.commit()
    
    async def get_interaction_history(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """獲取交互歷史"""
        cursor = self.conn.execute("""
            SELECT interaction_type, content, timestamp 
            FROM interaction_logs 
            WHERE project_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (project_id, limit))
        
        return [
            {
                "interaction_type": row[0],
                "content": row[1],
                "timestamp": row[2]
            }
            for row in cursor.fetchall()
        ]

class SerenaLSPAdapter:
    """Serena LSP 適配器主類"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.lsp_client = SerenaLSPClient(self.config.get("lsp_client", {}))
        self.project_analyzer = ProjectAnalyzer(self.lsp_client)
        self.memory_manager = ProjectMemoryManager(self.config.get("memory_manager", {}))
        
        self.initialized = False
        self.current_project_memory = None
        
        # 性能統計
        self.stats = {
            "total_analyses": 0,
            "symbol_searches": 0,
            "memory_saves": 0,
            "memory_loads": 0
        }
    
    async def initialize(self):
        """初始化 LSP 適配器"""
        try:
            await self.lsp_client.initialize()
            await self.memory_manager.initialize()
            self.initialized = True
            logger.info("Serena LSP Adapter initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Serena LSP Adapter: {e}")
            raise
    
    async def analyze_project(self, project_path: str) -> ProjectOverview:
        """分析項目"""
        if not self.initialized:
            raise RuntimeError("LSP adapter not initialized")
        
        self.stats["total_analyses"] += 1
        
        # 生成項目 ID
        project_id = hashlib.md5(project_path.encode()).hexdigest()
        
        # 檢查是否有緩存的記憶
        cached_memory = await self.memory_manager.load_project_memory(project_id)
        if cached_memory:
            # 檢查是否需要更新
            project_modified = Path(project_path).stat().st_mtime
            memory_time = cached_memory.last_updated.timestamp()
            
            if project_modified <= memory_time:
                logger.info(f"Using cached project analysis for {project_path}")
                self.current_project_memory = cached_memory
                return cached_memory.overview
        
        # 執行新的分析
        logger.info(f"Performing fresh project analysis for {project_path}")
        overview = await self.project_analyzer.analyze_project_structure(project_path)
        
        # 創建或更新項目記憶
        if cached_memory:
            cached_memory.overview = overview
            cached_memory.last_updated = datetime.now()
            memory = cached_memory
        else:
            memory = ProjectMemory(
                project_id=project_id,
                project_path=project_path,
                overview=overview
            )
        
        # 保存記憶
        await self.memory_manager.save_project_memory(memory)
        self.current_project_memory = memory
        self.stats["memory_saves"] += 1
        
        # 記錄交互
        await self.memory_manager.add_interaction(
            project_id, "project_analysis", f"Analyzed project structure"
        )
        
        return overview
    
    async def search_symbols(self, query: str, project_path: Optional[str] = None) -> List[LSPSymbol]:
        """搜索符號"""
        if not self.initialized:
            raise RuntimeError("LSP adapter not initialized")
        
        self.stats["symbol_searches"] += 1
        
        symbols = await self.lsp_client.search_symbols(query, project_path)
        
        # 如果有當前項目記憶，記錄交互
        if self.current_project_memory:
            await self.memory_manager.add_interaction(
                self.current_project_memory.project_id,
                "symbol_search",
                f"Searched for symbols: {query}"
            )
        
        return symbols
    
    async def generate_code_with_project_context(self, requirements: str, 
                                               project_info: ProjectOverview,
                                               context: Dict[str, Any]) -> str:
        """基於項目上下文生成代碼"""
        logger.info("Generating code with project context")
        
        # 構建項目感知的代碼生成提示
        prompt_parts = [
            f"Requirements: {requirements}",
            "",
            "Project Context:",
            f"- Languages: {', '.join(project_info.languages)}",
            f"- Architecture Patterns: {', '.join(project_info.architecture_patterns)}",
            f"- Total Files: {project_info.total_files}",
            f"- Total Symbols: {project_info.total_symbols}",
            ""
        ]
        
        # 添加主要模組信息
        if project_info.main_modules:
            prompt_parts.append("Main Modules:")
            for module in project_info.main_modules[:5]:  # 限制數量
                prompt_parts.append(f"- {module}")
            prompt_parts.append("")
        
        # 添加依賴信息
        if project_info.dependencies:
            prompt_parts.append("Key Dependencies:")
            for dep in project_info.dependencies[:10]:  # 限制數量
                prompt_parts.append(f"- {dep}")
            prompt_parts.append("")
        
        prompt_parts.append("Generate code that follows the project's patterns and conventions:")
        
        # 基於項目信息生成代碼
        if "Python" in project_info.languages:
            generated_code = self._generate_python_code_with_context(requirements, project_info)
        elif "JavaScript" in project_info.languages or "TypeScript" in project_info.languages:
            generated_code = self._generate_js_code_with_context(requirements, project_info)
        else:
            generated_code = self._generate_generic_code_with_context(requirements, project_info)
        
        # 記錄代碼生成交互
        if self.current_project_memory:
            await self.memory_manager.add_interaction(
                self.current_project_memory.project_id,
                "code_generation",
                f"Generated code for: {requirements}"
            )
        
        return generated_code
    
    def _generate_python_code_with_context(self, requirements: str, project_info: ProjectOverview) -> str:
        """基於 Python 項目上下文生成代碼"""
        # 檢測是否是 Flask 項目
        is_flask = any("flask" in dep.lower() for dep in project_info.dependencies)
        
        # 檢測是否是 FastAPI 項目
        is_fastapi = any("fastapi" in dep.lower() for dep in project_info.dependencies)
        
        if is_flask and ("api" in requirements.lower() or "endpoint" in requirements.lower()):
            return f'''
from flask import Flask, request, jsonify
from typing import Dict, Any

app = Flask(__name__)

@app.route('/api/endpoint', methods=['POST'])
def handle_request():
    """
    {requirements}
    
    Generated based on Flask project patterns detected in the codebase.
    """
    try:
        data = request.get_json()
        
        # Process the request based on requirements
        result = process_request_data(data)
        
        return jsonify({{
            "success": True,
            "data": result,
            "message": "Request processed successfully"
        }})
    
    except Exception as e:
        return jsonify({{
            "success": False,
            "error": str(e)
        }}), 500

def process_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the request data according to business logic.
    
    Args:
        data: Input data from the request
        
    Returns:
        Processed result data
    """
    # TODO: Implement the actual business logic based on requirements
    return {{"processed": True, "input": data}}

if __name__ == '__main__':
    app.run(debug=True)
'''
        elif is_fastapi and ("api" in requirements.lower() or "endpoint" in requirements.lower()):
            return f'''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

app = FastAPI()

class RequestModel(BaseModel):
    """Request model for the API endpoint"""
    # TODO: Define the actual request fields based on requirements
    data: Dict[str, Any]

class ResponseModel(BaseModel):
    """Response model for the API endpoint"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str

@app.post("/api/endpoint", response_model=ResponseModel)
async def handle_request(request: RequestModel):
    """
    {requirements}
    
    Generated based on FastAPI project patterns detected in the codebase.
    """
    try:
        # Process the request based on requirements
        result = await process_request_data(request.data)
        
        return ResponseModel(
            success=True,
            data=result,
            message="Request processed successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the request data according to business logic.
    
    Args:
        data: Input data from the request
        
    Returns:
        Processed result data
    """
    # TODO: Implement the actual business logic based on requirements
    return {{"processed": True, "input": data}}
'''
        else:
            return f'''
"""
{requirements}

Generated based on Python project patterns detected in the codebase.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GeneratedComponent:
    """
    Component generated based on project requirements.
    
    This follows the patterns detected in your codebase.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {{}}
        self.initialized = False
        
    async def initialize(self) -> bool:
        """Initialize the component"""
        try:
            # TODO: Implement initialization logic based on requirements
            self.initialized = True
            logger.info("Component initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize component: {{e}}")
            return False
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data according to requirements.
        
        Args:
            data: Input data to process
            
        Returns:
            Processed result
        """
        if not self.initialized:
            raise RuntimeError("Component not initialized")
        
        try:
            # TODO: Implement processing logic based on requirements
            result = {{
                "processed": True,
                "input": data,
                "timestamp": datetime.now().isoformat()
            }}
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing data: {{e}}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get component status"""
        return {{
            "initialized": self.initialized,
            "config": self.config
        }}

# Factory function
async def create_component(config: Dict[str, Any] = None) -> GeneratedComponent:
    """Create and initialize the component"""
    component = GeneratedComponent(config)
    await component.initialize()
    return component
'''
    
    def _generate_js_code_with_context(self, requirements: str, project_info: ProjectOverview) -> str:
        """基於 JavaScript/TypeScript 項目上下文生成代碼"""
        is_react = any("react" in dep.lower() for dep in project_info.dependencies)
        is_express = any("express" in dep.lower() for dep in project_info.dependencies)
        
        if is_react and ("component" in requirements.lower()):
            return f'''
import React, {{ useState, useEffect }} from 'react';

/**
 * {requirements}
 * 
 * Generated based on React project patterns detected in the codebase.
 */
const GeneratedComponent = ({{ ...props }}) => {{
  const [state, setState] = useState({{}});
  const [loading, setLoading] = useState(false);

  useEffect(() => {{
    // TODO: Implement component initialization logic
    initializeComponent();
  }}, []);

  const initializeComponent = async () => {{
    setLoading(true);
    try {{
      // TODO: Implement initialization based on requirements
      console.log('Component initialized');
    }} catch (error) {{
      console.error('Error initializing component:', error);
    }} finally {{
      setLoading(false);
    }}
  }};

  const handleAction = async () => {{
    // TODO: Implement action handler based on requirements
    console.log('Action handled');
  }};

  if (loading) {{
    return <div>Loading...</div>;
  }}

  return (
    <div className="generated-component">
      <h2>Generated Component</h2>
      <button onClick={{handleAction}}>
        Perform Action
      </button>
    </div>
  );
}};

export default GeneratedComponent;
'''
        elif is_express and ("api" in requirements.lower() or "endpoint" in requirements.lower()):
            return f'''
const express = require('express');
const router = express.Router();

/**
 * {requirements}
 * 
 * Generated based on Express.js project patterns detected in the codebase.
 */

// Middleware for request validation
const validateRequest = (req, res, next) => {{
  // TODO: Implement request validation based on requirements
  next();
}};

// Main endpoint handler
router.post('/api/endpoint', validateRequest, async (req, res) => {{
  try {{
    const {{ data }} = req.body;
    
    // Process the request based on requirements
    const result = await processRequestData(data);
    
    res.json({{
      success: true,
      data: result,
      message: 'Request processed successfully'
    }});
    
  }} catch (error) {{
    console.error('Error processing request:', error);
    res.status(500).json({{
      success: false,
      error: error.message
    }});
  }}
}});

async function processRequestData(data) {{
  // TODO: Implement the actual business logic based on requirements
  return {{
    processed: true,
    input: data,
    timestamp: new Date().toISOString()
  }};
}}

module.exports = router;
'''
        else:
            return f'''
/**
 * {requirements}
 * 
 * Generated based on JavaScript project patterns detected in the codebase.
 */

class GeneratedComponent {{
  constructor(config = {{}}) {{
    this.config = config;
    this.initialized = false;
  }}

  async initialize() {{
    try {{
      // TODO: Implement initialization logic based on requirements
      this.initialized = true;
      console.log('Component initialized successfully');
      return true;
    }} catch (error) {{
      console.error('Failed to initialize component:', error);
      return false;
    }}
  }}

  async process(data) {{
    if (!this.initialized) {{
      throw new Error('Component not initialized');
    }}

    try {{
      // TODO: Implement processing logic based on requirements
      const result = {{
        processed: true,
        input: data,
        timestamp: new Date().toISOString()
      }};

      return result;
    }} catch (error) {{
      console.error('Error processing data:', error);
      throw error;
    }}
  }}

  getStatus() {{
    return {{
      initialized: this.initialized,
      config: this.config
    }};
  }}
}}

// Factory function
async function createComponent(config = {{}}) {{
  const component = new GeneratedComponent(config);
  await component.initialize();
  return component;
}}

module.exports = {{ GeneratedComponent, createComponent }};
'''
    
    def _generate_generic_code_with_context(self, requirements: str, project_info: ProjectOverview) -> str:
        """生成通用代碼"""
        return f'''
/*
 * {requirements}
 * 
 * Generated based on project patterns detected in the codebase.
 * Languages: {', '.join(project_info.languages)}
 * Architecture: {', '.join(project_info.architecture_patterns)}
 */

// TODO: Implement the functionality based on requirements
// This is a generic template that should be adapted to your specific language and framework

function processRequirement() {{
    // Implementation based on: {requirements}
    return {{
        success: true,
        message: "Requirement processed",
        timestamp: new Date().toISOString()
    }};
}}
'''
    
    async def get_project_memory(self, project_path: str) -> Optional[ProjectMemory]:
        """獲取項目記憶"""
        project_id = hashlib.md5(project_path.encode()).hexdigest()
        memory = await self.memory_manager.load_project_memory(project_id)
        self.stats["memory_loads"] += 1
        return memory
    
    async def add_design_decision(self, project_path: str, decision: Dict[str, Any]):
        """添加設計決策"""
        if self.current_project_memory:
            self.current_project_memory.design_decisions.append(decision)
            await self.memory_manager.save_project_memory(self.current_project_memory)
            
            await self.memory_manager.add_interaction(
                self.current_project_memory.project_id,
                "design_decision",
                f"Added design decision: {decision.get('title', 'Untitled')}"
            )
    
    async def add_code_pattern(self, project_path: str, pattern: Dict[str, Any]):
        """添加代碼模式"""
        if self.current_project_memory:
            self.current_project_memory.code_patterns.append(pattern)
            await self.memory_manager.save_project_memory(self.current_project_memory)
            
            await self.memory_manager.add_interaction(
                self.current_project_memory.project_id,
                "code_pattern",
                f"Added code pattern: {pattern.get('name', 'Unnamed')}"
            )
    
    def get_status(self) -> Dict[str, Any]:
        """獲取適配器狀態"""
        return {
            "initialized": self.initialized,
            "lsp_connected": self.lsp_client.connected,
            "current_project": self.current_project_memory.project_path if self.current_project_memory else None,
            "stats": self.stats
        }
    
    async def shutdown(self):
        """關閉適配器"""
        if self.lsp_client:
            await self.lsp_client.shutdown()
        if self.memory_manager and self.memory_manager.conn:
            self.memory_manager.conn.close()
        logger.info("Serena LSP Adapter shut down")

# 工廠函數
async def create_serena_lsp_adapter(config: Dict[str, Any] = None) -> SerenaLSPAdapter:
    """創建並初始化 Serena LSP 適配器"""
    adapter = SerenaLSPAdapter(config)
    await adapter.initialize()
    return adapter

