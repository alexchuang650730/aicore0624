#!/usr/bin/env python3
"""
Code-Specific RAG Engine
代碼專用 RAG 引擎

專門為代碼理解、檢索和生成優化的 RAG 系統
支持代碼語義分析、項目感知檢索和智能代碼生成
"""

import asyncio
import json
import logging
import time
import hashlib
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import sqlite3
from concurrent.futures import ThreadPoolExecutor

# 向量數據庫導入
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logging.warning("ChromaDB not available, using fallback storage")

# 嵌入模型導入
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("SentenceTransformers not available, using mock embeddings")

logger = logging.getLogger(__name__)

class CodeContentType(Enum):
    """代碼內容類型"""
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"
    COMMENT = "comment"
    DOCSTRING = "docstring"
    TEST = "test"
    CONFIG = "config"
    API_ENDPOINT = "api_endpoint"
    DATABASE_MODEL = "database_model"

class CodeLanguage(Enum):
    """支持的編程語言"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"

@dataclass
class CodeChunk:
    """代碼分塊"""
    chunk_id: str
    content: str
    content_type: CodeContentType
    language: CodeLanguage
    source_file: str
    start_line: int
    end_line: int
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    symbols: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    complexity_score: float = 0.0
    quality_score: float = 0.0
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "content_type": self.content_type.value,
            "language": self.language.value,
            "source_file": self.source_file,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "function_name": self.function_name,
            "class_name": self.class_name,
            "symbols": self.symbols,
            "dependencies": self.dependencies,
            "complexity_score": self.complexity_score,
            "quality_score": self.quality_score,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class CodeRetrievalQuery:
    """代碼檢索查詢"""
    query_text: str
    language: Optional[CodeLanguage] = None
    content_types: List[CodeContentType] = field(default_factory=list)
    project_path: Optional[str] = None
    max_results: int = 10
    similarity_threshold: float = 0.7
    include_context: bool = True
    complexity_preference: Optional[str] = None  # "simple", "complex", None
    
@dataclass
class CodeRetrievalResult:
    """代碼檢索結果"""
    chunk: CodeChunk
    similarity_score: float
    relevance_score: float
    context_score: float
    final_score: float
    retrieval_reason: str

class CodeDocumentChunker:
    """代碼文檔分塊器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_chunk_size = self.config.get("max_chunk_size", 1000)
        self.overlap_size = self.config.get("overlap_size", 200)
        self.min_chunk_size = self.config.get("min_chunk_size", 100)
        
    async def chunk_code_file(self, file_path: str, content: str, language: CodeLanguage) -> List[CodeChunk]:
        """對代碼文件進行智能分塊"""
        chunks = []
        
        try:
            if language == CodeLanguage.PYTHON:
                chunks = await self._chunk_python_code(file_path, content)
            elif language in [CodeLanguage.JAVASCRIPT, CodeLanguage.TYPESCRIPT]:
                chunks = await self._chunk_js_ts_code(file_path, content, language)
            elif language == CodeLanguage.JAVA:
                chunks = await self._chunk_java_code(file_path, content)
            else:
                # 回退到基於行的分塊
                chunks = await self._chunk_by_lines(file_path, content, language)
                
        except Exception as e:
            logger.error(f"Error chunking file {file_path}: {e}")
            chunks = await self._chunk_by_lines(file_path, content, language)
            
        return chunks
    
    async def _chunk_python_code(self, file_path: str, content: str) -> List[CodeChunk]:
        """Python 代碼分塊"""
        chunks = []
        lines = content.split('\n')
        
        current_chunk = []
        current_start = 0
        current_type = CodeContentType.FUNCTION
        current_function = None
        current_class = None
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 檢測類定義
            if line.startswith('class '):
                if current_chunk:
                    chunk = self._create_code_chunk(
                        file_path, current_chunk, current_start, i-1, 
                        CodeLanguage.PYTHON, current_type, current_function, current_class
                    )
                    chunks.append(chunk)
                
                # 開始新的類分塊
                current_chunk = [lines[i]]
                current_start = i
                current_type = CodeContentType.CLASS
                current_class = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                current_function = None
                
            # 檢測函數定義
            elif line.startswith('def ') or line.startswith('async def '):
                if current_chunk and len('\n'.join(current_chunk)) > self.min_chunk_size:
                    chunk = self._create_code_chunk(
                        file_path, current_chunk, current_start, i-1,
                        CodeLanguage.PYTHON, current_type, current_function, current_class
                    )
                    chunks.append(chunk)
                
                # 開始新的函數分塊
                current_chunk = [lines[i]]
                current_start = i
                current_type = CodeContentType.FUNCTION
                func_line = line.replace('async def ', 'def ')
                current_function = func_line.split('def ')[1].split('(')[0].strip()
                
            else:
                current_chunk.append(lines[i])
                
                # 檢查分塊大小
                if len('\n'.join(current_chunk)) > self.max_chunk_size:
                    chunk = self._create_code_chunk(
                        file_path, current_chunk, current_start, i,
                        CodeLanguage.PYTHON, current_type, current_function, current_class
                    )
                    chunks.append(chunk)
                    
                    # 開始新分塊，保留重疊
                    overlap_lines = current_chunk[-self.overlap_size//50:] if len(current_chunk) > self.overlap_size//50 else current_chunk
                    current_chunk = overlap_lines
                    current_start = i - len(overlap_lines) + 1
            
            i += 1
        
        # 處理最後一個分塊
        if current_chunk:
            chunk = self._create_code_chunk(
                file_path, current_chunk, current_start, len(lines)-1,
                CodeLanguage.PYTHON, current_type, current_function, current_class
            )
            chunks.append(chunk)
        
        return chunks
    
    async def _chunk_js_ts_code(self, file_path: str, content: str, language: CodeLanguage) -> List[CodeChunk]:
        """JavaScript/TypeScript 代碼分塊"""
        # 簡化實現，實際應該使用 AST 解析
        return await self._chunk_by_lines(file_path, content, language)
    
    async def _chunk_java_code(self, file_path: str, content: str) -> List[CodeChunk]:
        """Java 代碼分塊"""
        # 簡化實現，實際應該使用 AST 解析
        return await self._chunk_by_lines(file_path, content, CodeLanguage.JAVA)
    
    async def _chunk_by_lines(self, file_path: str, content: str, language: CodeLanguage) -> List[CodeChunk]:
        """基於行數的回退分塊方法"""
        chunks = []
        lines = content.split('\n')
        lines_per_chunk = self.max_chunk_size // 50
        overlap_lines = self.overlap_size // 50
        
        for i in range(0, len(lines), lines_per_chunk - overlap_lines):
            end_idx = min(i + lines_per_chunk, len(lines))
            chunk_lines = lines[i:end_idx]
            chunk_content = '\n'.join(chunk_lines)
            
            if len(chunk_content.strip()) > self.min_chunk_size:
                chunk = CodeChunk(
                    chunk_id=self._generate_chunk_id(file_path, i, end_idx-1),
                    content=chunk_content,
                    content_type=CodeContentType.FUNCTION,  # 默認類型
                    language=language,
                    source_file=file_path,
                    start_line=i,
                    end_line=end_idx-1,
                    symbols=self._extract_symbols(chunk_content, language)
                )
                chunks.append(chunk)
        
        return chunks
    
    def _create_code_chunk(self, file_path: str, lines: List[str], start_line: int, end_line: int,
                          language: CodeLanguage, content_type: CodeContentType,
                          function_name: Optional[str], class_name: Optional[str]) -> CodeChunk:
        """創建代碼分塊"""
        content = '\n'.join(lines)
        
        return CodeChunk(
            chunk_id=self._generate_chunk_id(file_path, start_line, end_line),
            content=content,
            content_type=content_type,
            language=language,
            source_file=file_path,
            start_line=start_line,
            end_line=end_line,
            function_name=function_name,
            class_name=class_name,
            symbols=self._extract_symbols(content, language),
            complexity_score=self._calculate_complexity(content, language),
            quality_score=self._calculate_quality(content, language)
        )
    
    def _extract_symbols(self, content: str, language: CodeLanguage) -> List[str]:
        """提取代碼符號"""
        symbols = []
        lines = content.split('\n')
        
        for line in lines:
            stripped = line.strip()
            if language == CodeLanguage.PYTHON:
                if stripped.startswith(('def ', 'class ', 'async def ')):
                    if 'def ' in stripped:
                        parts = stripped.split('(')[0].split()
                        if len(parts) >= 2:
                            symbols.append(parts[-1])
                    elif 'class ' in stripped:
                        parts = stripped.split('(')[0].split()
                        if len(parts) >= 2:
                            symbols.append(parts[1])
        
        return symbols
    
    def _calculate_complexity(self, content: str, language: CodeLanguage) -> float:
        """計算代碼複雜度"""
        # 簡化的複雜度計算
        complexity_indicators = ['if ', 'for ', 'while ', 'try:', 'except:', 'elif ', 'else:']
        score = sum(content.count(indicator) for indicator in complexity_indicators)
        return min(score / 10.0, 1.0)  # 歸一化到 0-1
    
    def _calculate_quality(self, content: str, language: CodeLanguage) -> float:
        """計算代碼質量分數"""
        # 簡化的質量評估
        quality_score = 0.5  # 基礎分數
        
        # 有文檔字符串加分
        if '"""' in content or "'''" in content:
            quality_score += 0.2
        
        # 有類型提示加分
        if '->' in content or ':' in content:
            quality_score += 0.1
        
        # 有異常處理加分
        if 'try:' in content and 'except' in content:
            quality_score += 0.1
        
        # 代碼行數適中加分
        lines = content.split('\n')
        if 10 <= len(lines) <= 50:
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    def _generate_chunk_id(self, file_path: str, start_line: int, end_line: int) -> str:
        """生成分塊ID"""
        content = f"{file_path}:{start_line}-{end_line}"
        return hashlib.md5(content.encode()).hexdigest()

class CodeEmbeddingEngine:
    """代碼嵌入引擎"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.model_name = self.config.get("model_name", "all-MiniLM-L6-v2")
        self.model = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def initialize(self):
        """初始化嵌入模型"""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"Code embedding model {self.model_name} loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                self.model = None
        else:
            logger.warning("Using mock embeddings")
    
    async def embed_code_chunk(self, chunk: CodeChunk) -> List[float]:
        """為代碼分塊生成嵌入向量"""
        if self.model:
            # 構建用於嵌入的文本
            embed_text = self._prepare_text_for_embedding(chunk)
            
            # 在線程池中執行嵌入
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                self.executor, self.model.encode, embed_text
            )
            return embedding.tolist()
        else:
            # 模擬嵌入向量
            return [0.1] * 384  # MiniLM 的向量維度
    
    def _prepare_text_for_embedding(self, chunk: CodeChunk) -> str:
        """準備用於嵌入的文本"""
        parts = []
        
        # 添加內容類型信息
        parts.append(f"Type: {chunk.content_type.value}")
        
        # 添加語言信息
        parts.append(f"Language: {chunk.language.value}")
        
        # 添加函數/類名
        if chunk.function_name:
            parts.append(f"Function: {chunk.function_name}")
        if chunk.class_name:
            parts.append(f"Class: {chunk.class_name}")
        
        # 添加符號信息
        if chunk.symbols:
            parts.append(f"Symbols: {', '.join(chunk.symbols)}")
        
        # 添加代碼內容（清理後）
        cleaned_content = self._clean_code_for_embedding(chunk.content)
        parts.append(f"Code: {cleaned_content}")
        
        return " | ".join(parts)
    
    def _clean_code_for_embedding(self, content: str) -> str:
        """清理代碼用於嵌入"""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped = line.strip()
            # 跳過空行和純注釋行
            if stripped and not stripped.startswith('#'):
                cleaned_lines.append(stripped)
        
        return ' '.join(cleaned_lines)

class CodeVectorStore:
    """代碼向量存儲"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.collection_name = self.config.get("collection_name", "code_chunks")
        self.persist_directory = self.config.get("persist_directory", "./data/code_chroma_db")
        
        self.client = None
        self.collection = None
        self.conn = None  # SQLite 回退
        
    async def initialize(self):
        """初始化向量存儲"""
        if CHROMA_AVAILABLE:
            try:
                self.client = chromadb.PersistentClient(path=self.persist_directory)
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"description": "Code chunks for RAG"}
                )
                logger.info(f"ChromaDB collection '{self.collection_name}' initialized")
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB: {e}")
                await self._init_sqlite_fallback()
        else:
            await self._init_sqlite_fallback()
    
    async def _init_sqlite_fallback(self):
        """初始化 SQLite 回退存儲"""
        self.conn = sqlite3.connect("code_chunks.db")
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS code_chunks (
                chunk_id TEXT PRIMARY KEY,
                content TEXT,
                content_type TEXT,
                language TEXT,
                source_file TEXT,
                start_line INTEGER,
                end_line INTEGER,
                function_name TEXT,
                class_name TEXT,
                symbols TEXT,
                complexity_score REAL,
                quality_score REAL,
                embedding TEXT,
                metadata TEXT,
                created_at TEXT
            )
        """)
        self.conn.commit()
        logger.info("SQLite fallback storage initialized")
    
    async def store_chunk(self, chunk: CodeChunk, embedding: List[float]):
        """存儲代碼分塊"""
        if self.collection:
            # ChromaDB 存儲
            self.collection.add(
                documents=[chunk.content],
                embeddings=[embedding],
                metadatas=[{
                    "chunk_id": chunk.chunk_id,
                    "content_type": chunk.content_type.value,
                    "language": chunk.language.value,
                    "source_file": chunk.source_file,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "function_name": chunk.function_name or "",
                    "class_name": chunk.class_name or "",
                    "symbols": json.dumps(chunk.symbols),
                    "complexity_score": chunk.complexity_score,
                    "quality_score": chunk.quality_score,
                    "metadata": json.dumps(chunk.metadata)
                }],
                ids=[chunk.chunk_id]
            )
        else:
            # SQLite 回退存儲
            self.conn.execute("""
                INSERT OR REPLACE INTO code_chunks 
                (chunk_id, content, content_type, language, source_file, start_line, end_line,
                 function_name, class_name, symbols, complexity_score, quality_score, 
                 embedding, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chunk.chunk_id, chunk.content, chunk.content_type.value, chunk.language.value,
                chunk.source_file, chunk.start_line, chunk.end_line,
                chunk.function_name, chunk.class_name, json.dumps(chunk.symbols),
                chunk.complexity_score, chunk.quality_score,
                json.dumps(embedding), json.dumps(chunk.metadata),
                chunk.created_at.isoformat()
            ))
            self.conn.commit()
    
    async def search_similar_chunks(self, query_embedding: List[float], 
                                  filters: Dict[str, Any] = None,
                                  n_results: int = 10) -> List[Tuple[CodeChunk, float]]:
        """搜索相似的代碼分塊"""
        if self.collection:
            # ChromaDB 搜索
            where_clause = {}
            if filters:
                if "language" in filters:
                    where_clause["language"] = filters["language"]
                if "content_type" in filters:
                    where_clause["content_type"] = filters["content_type"]
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause if where_clause else None
            )
            
            chunks_with_scores = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            )):
                chunk = CodeChunk(
                    chunk_id=metadata['chunk_id'],
                    content=doc,
                    content_type=CodeContentType(metadata['content_type']),
                    language=CodeLanguage(metadata['language']),
                    source_file=metadata['source_file'],
                    start_line=metadata['start_line'],
                    end_line=metadata['end_line'],
                    function_name=metadata.get('function_name') or None,
                    class_name=metadata.get('class_name') or None,
                    symbols=json.loads(metadata.get('symbols', '[]')),
                    complexity_score=metadata.get('complexity_score', 0.0),
                    quality_score=metadata.get('quality_score', 0.0),
                    metadata=json.loads(metadata.get('metadata', '{}'))
                )
                similarity = 1 - distance
                chunks_with_scores.append((chunk, similarity))
            
            return chunks_with_scores
        else:
            # SQLite 回退搜索
            query = "SELECT * FROM code_chunks"
            params = []
            
            if filters:
                conditions = []
                if "language" in filters:
                    conditions.append("language = ?")
                    params.append(filters["language"])
                if "content_type" in filters:
                    conditions.append("content_type = ?")
                    params.append(filters["content_type"])
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            
            query += f" LIMIT {n_results}"
            
            cursor = self.conn.execute(query, params)
            chunks_with_scores = []
            
            for row in cursor.fetchall():
                chunk = CodeChunk(
                    chunk_id=row[0],
                    content=row[1],
                    content_type=CodeContentType(row[2]),
                    language=CodeLanguage(row[3]),
                    source_file=row[4],
                    start_line=row[5],
                    end_line=row[6],
                    function_name=row[7] or None,
                    class_name=row[8] or None,
                    symbols=json.loads(row[9]) if row[9] else [],
                    complexity_score=row[10] or 0.0,
                    quality_score=row[11] or 0.0,
                    metadata=json.loads(row[13]) if row[13] else {}
                )
                # 模擬相似度分數
                similarity = 0.8
                chunks_with_scores.append((chunk, similarity))
            
            return chunks_with_scores

class CodeRAGEngine:
    """代碼專用 RAG 引擎"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.chunker = CodeDocumentChunker(self.config.get("chunker", {}))
        self.embedding_engine = CodeEmbeddingEngine(self.config.get("embedding", {}))
        self.vector_store = CodeVectorStore(self.config.get("vector_store", {}))
        
        # 緩存配置
        self.cache_ttl = self.config.get("cache_ttl", 3600)
        self.query_cache = {}
        
        # 性能統計
        self.stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "indexed_chunks": 0,
            "average_response_time": 0.0
        }
        
        self.initialized = False
    
    async def initialize(self):
        """初始化 RAG 引擎"""
        try:
            await self.embedding_engine.initialize()
            await self.vector_store.initialize()
            self.initialized = True
            logger.info("Code RAG Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Code RAG Engine: {e}")
            raise
    
    async def index_project(self, project_path: str, language_filter: List[CodeLanguage] = None):
        """索引項目代碼"""
        logger.info(f"Indexing project: {project_path}")
        
        project_path = Path(project_path)
        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
        
        # 支持的文件擴展名
        extensions = {
            ".py": CodeLanguage.PYTHON,
            ".js": CodeLanguage.JAVASCRIPT,
            ".ts": CodeLanguage.TYPESCRIPT,
            ".java": CodeLanguage.JAVA,
            ".cpp": CodeLanguage.CPP,
            ".cs": CodeLanguage.CSHARP,
            ".go": CodeLanguage.GO,
            ".rs": CodeLanguage.RUST,
            ".php": CodeLanguage.PHP,
            ".rb": CodeLanguage.RUBY
        }
        
        indexed_count = 0
        
        for file_path in project_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in extensions:
                language = extensions[file_path.suffix]
                
                # 語言過濾
                if language_filter and language not in language_filter:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 分塊
                    chunks = await self.chunker.chunk_code_file(
                        str(file_path), content, language
                    )
                    
                    # 為每個分塊生成嵌入並存儲
                    for chunk in chunks:
                        embedding = await self.embedding_engine.embed_code_chunk(chunk)
                        await self.vector_store.store_chunk(chunk, embedding)
                        indexed_count += 1
                    
                    if indexed_count % 100 == 0:
                        logger.info(f"Indexed {indexed_count} code chunks...")
                        
                except Exception as e:
                    logger.error(f"Error indexing file {file_path}: {e}")
                    continue
        
        self.stats["indexed_chunks"] = indexed_count
        logger.info(f"Project indexing completed. Total chunks: {indexed_count}")
    
    async def retrieve_similar_code(self, query: str, language: Optional[str] = None, 
                                  project_path: Optional[str] = None,
                                  max_results: int = 10) -> List[CodeRetrievalResult]:
        """檢索相似代碼"""
        start_time = time.time()
        self.stats["total_queries"] += 1
        
        # 檢查緩存
        cache_key = f"{query}:{language}:{project_path}:{max_results}"
        if cache_key in self.query_cache:
            cache_entry = self.query_cache[cache_key]
            if datetime.now() - cache_entry["timestamp"] < timedelta(seconds=self.cache_ttl):
                self.stats["cache_hits"] += 1
                return cache_entry["results"]
        
        # 構建查詢
        query_chunk = CodeChunk(
            chunk_id="query",
            content=query,
            content_type=CodeContentType.FUNCTION,
            language=CodeLanguage(language) if language else CodeLanguage.PYTHON,
            source_file="query",
            start_line=0,
            end_line=0
        )
        
        # 生成查詢嵌入
        query_embedding = await self.embedding_engine.embed_code_chunk(query_chunk)
        
        # 構建過濾條件
        filters = {}
        if language:
            filters["language"] = language
        
        # 搜索相似分塊
        similar_chunks = await self.vector_store.search_similar_chunks(
            query_embedding, filters, max_results
        )
        
        # 構建檢索結果
        results = []
        for chunk, similarity in similar_chunks:
            # 計算相關性分數
            relevance_score = self._calculate_relevance_score(query, chunk)
            
            # 計算上下文分數
            context_score = self._calculate_context_score(chunk, project_path)
            
            # 計算最終分數
            final_score = (similarity * 0.4 + relevance_score * 0.4 + context_score * 0.2)
            
            result = CodeRetrievalResult(
                chunk=chunk,
                similarity_score=similarity,
                relevance_score=relevance_score,
                context_score=context_score,
                final_score=final_score,
                retrieval_reason=f"Similarity: {similarity:.2f}, Relevance: {relevance_score:.2f}"
            )
            results.append(result)
        
        # 按最終分數排序
        results.sort(key=lambda x: x.final_score, reverse=True)
        
        # 緩存結果
        self.query_cache[cache_key] = {
            "results": results,
            "timestamp": datetime.now()
        }
        
        # 更新統計
        response_time = time.time() - start_time
        self.stats["average_response_time"] = (
            (self.stats["average_response_time"] * (self.stats["total_queries"] - 1) + response_time) 
            / self.stats["total_queries"]
        )
        
        logger.info(f"Retrieved {len(results)} similar code chunks in {response_time:.2f}s")
        return results
    
    async def generate_code_with_context(self, requirements: str, similar_code: List[CodeRetrievalResult],
                                       context: Dict[str, Any]) -> str:
        """基於上下文生成代碼"""
        # 構建生成提示
        prompt_parts = [
            f"Requirements: {requirements}",
            "",
            "Similar code examples:"
        ]
        
        for i, result in enumerate(similar_code[:3]):  # 使用前3個最相似的例子
            prompt_parts.append(f"Example {i+1} (Score: {result.final_score:.2f}):")
            prompt_parts.append(f"```{result.chunk.language.value}")
            prompt_parts.append(result.chunk.content)
            prompt_parts.append("```")
            prompt_parts.append("")
        
        prompt_parts.append("Generate code based on the requirements and examples above:")
        
        # 這裡應該調用實際的代碼生成模型
        # 目前返回一個基於模板的簡單實現
        generated_code = self._generate_template_code(requirements, similar_code)
        
        return generated_code
    
    def _calculate_relevance_score(self, query: str, chunk: CodeChunk) -> float:
        """計算相關性分數"""
        query_words = set(query.lower().split())
        chunk_words = set(chunk.content.lower().split())
        
        if not query_words:
            return 0.0
        
        intersection = query_words.intersection(chunk_words)
        return len(intersection) / len(query_words)
    
    def _calculate_context_score(self, chunk: CodeChunk, project_path: Optional[str]) -> float:
        """計算上下文分數"""
        score = 0.5  # 基礎分數
        
        # 如果在同一項目中，加分
        if project_path and project_path in chunk.source_file:
            score += 0.3
        
        # 高質量代碼加分
        score += chunk.quality_score * 0.2
        
        return min(score, 1.0)
    
    def _generate_template_code(self, requirements: str, similar_code: List[CodeRetrievalResult]) -> str:
        """基於模板生成代碼"""
        # 簡化的模板生成邏輯
        if "api" in requirements.lower() or "endpoint" in requirements.lower():
            return f'''
def handle_request():
    """
    {requirements}
    """
    try:
        # TODO: Implement the logic based on requirements
        result = process_request()
        return {{"success": True, "data": result}}
    except Exception as e:
        return {{"success": False, "error": str(e)}}

def process_request():
    """Process the actual request logic"""
    # TODO: Implement based on similar code patterns
    return {{"message": "Request processed successfully"}}
'''
        else:
            return f'''
def generated_function():
    """
    {requirements}
    """
    # TODO: Implement based on requirements
    pass
'''
    
    def get_status(self) -> Dict[str, Any]:
        """獲取 RAG 引擎狀態"""
        return {
            "initialized": self.initialized,
            "stats": self.stats,
            "cache_size": len(self.query_cache),
            "components": {
                "chunker": "ready",
                "embedding_engine": "ready" if self.embedding_engine.model else "fallback",
                "vector_store": "chromadb" if self.vector_store.collection else "sqlite"
            }
        }

# 工廠函數
async def create_code_rag_engine(config: Dict[str, Any] = None) -> CodeRAGEngine:
    """創建並初始化代碼 RAG 引擎"""
    engine = CodeRAGEngine(config)
    await engine.initialize()
    return engine

