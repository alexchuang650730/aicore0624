#!/usr/bin/env python3
"""
Universal RAG Engine
通用 RAG 引擎

為整個 AICore 系統提供統一的檢索增強生成能力
支持多種數據類型：代碼、文檔、對話、項目知識等
"""

import asyncio
import json
import logging
import time
import hashlib
import sqlite3
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from collections import defaultdict

# 嘗試導入向量數據庫
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available, using fallback vector storage")

# 嘗試導入嵌入模型
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("SentenceTransformers not available, using fallback embeddings")

logger = logging.getLogger(__name__)

class DataType(Enum):
    """數據類型"""
    CODE = "code"
    DOCUMENTATION = "documentation"
    CONVERSATION = "conversation"
    PROJECT_KNOWLEDGE = "project_knowledge"
    GLOBAL_KNOWLEDGE = "global_knowledge"
    ERROR_LOG = "error_log"
    BEST_PRACTICE = "best_practice"
    DESIGN_PATTERN = "design_pattern"

class SearchMode(Enum):
    """搜索模式"""
    SEMANTIC = "semantic"          # 語義搜索
    KEYWORD = "keyword"            # 關鍵詞搜索
    HYBRID = "hybrid"              # 混合搜索
    CONTEXTUAL = "contextual"      # 上下文搜索

@dataclass
class Document:
    """文檔對象"""
    doc_id: str
    content: str
    data_type: DataType
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    relevance_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "content": self.content,
            "data_type": self.data_type.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "access_count": self.access_count,
            "relevance_score": self.relevance_score
        }

@dataclass
class SearchResult:
    """搜索結果"""
    document: Document
    similarity_score: float
    rank: int
    search_metadata: Dict[str, Any] = field(default_factory=dict)

class EmbeddingEngine:
    """嵌入引擎"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.model_name = self.config.get("model_name", "all-MiniLM-L6-v2")
        self.model = None
        self.embedding_dim = 384  # 默認維度
        self.initialized = False
        
    async def initialize(self):
        """初始化嵌入模型"""
        try:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.model = SentenceTransformer(self.model_name)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                logger.info(f"Initialized SentenceTransformer model: {self.model_name}")
            else:
                logger.warning("Using fallback embedding engine")
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding engine: {e}")
            self.initialized = True  # 允許使用回退模式
    
    async def encode(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """編碼文本為向量"""
        if not self.initialized:
            await self.initialize()
        
        if isinstance(texts, str):
            texts = [texts]
        
        try:
            if self.model:
                embeddings = self.model.encode(texts)
                return embeddings.tolist() if len(texts) > 1 else embeddings[0].tolist()
            else:
                # 回退到簡單的哈希嵌入
                return [self._hash_embedding(text) for text in texts]
                
        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            return [self._hash_embedding(text) for text in texts]
    
    def _hash_embedding(self, text: str) -> List[float]:
        """基於哈希的簡單嵌入"""
        # 創建確定性的偽隨機向量
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # 轉換為浮點數向量
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            chunk = hash_bytes[i:i+4]
            if len(chunk) == 4:
                value = int.from_bytes(chunk, byteorder='big') / (2**32)
                embedding.append(value)
        
        # 填充到目標維度
        while len(embedding) < self.embedding_dim:
            embedding.extend(embedding[:min(len(embedding), self.embedding_dim - len(embedding))])
        
        return embedding[:self.embedding_dim]

class VectorStore:
    """向量存儲"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.storage_path = self.config.get("storage_path", "./vector_store")
        self.collection_name = self.config.get("collection_name", "universal_rag")
        
        self.chroma_client = None
        self.collection = None
        self.fallback_storage = {}  # 回退存儲
        self.initialized = False
        
    async def initialize(self):
        """初始化向量存儲"""
        try:
            if CHROMADB_AVAILABLE:
                # 初始化 ChromaDB
                self.chroma_client = chromadb.PersistentClient(
                    path=self.storage_path,
                    settings=Settings(anonymized_telemetry=False)
                )
                
                self.collection = self.chroma_client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"description": "Universal RAG collection for AICore"}
                )
                
                logger.info(f"Initialized ChromaDB collection: {self.collection_name}")
            else:
                logger.warning("Using fallback vector storage")
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            self.initialized = True  # 允許使用回退模式
    
    async def add_documents(self, documents: List[Document]):
        """添加文檔"""
        if not self.initialized:
            await self.initialize()
        
        try:
            if self.collection:
                # 使用 ChromaDB
                ids = [doc.doc_id for doc in documents]
                embeddings = [doc.embedding for doc in documents if doc.embedding]
                metadatas = [doc.to_dict() for doc in documents]
                documents_text = [doc.content for doc in documents]
                
                if embeddings and len(embeddings) == len(documents):
                    self.collection.add(
                        ids=ids,
                        embeddings=embeddings,
                        metadatas=metadatas,
                        documents=documents_text
                    )
                else:
                    # 讓 ChromaDB 自動生成嵌入
                    self.collection.add(
                        ids=ids,
                        metadatas=metadatas,
                        documents=documents_text
                    )
            else:
                # 使用回退存儲
                for doc in documents:
                    self.fallback_storage[doc.doc_id] = doc
            
            logger.info(f"Added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            # 回退到內存存儲
            for doc in documents:
                self.fallback_storage[doc.doc_id] = doc
    
    async def search(self, query_embedding: List[float], limit: int = 10, 
                    filters: Dict[str, Any] = None) -> List[Tuple[str, float]]:
        """搜索相似文檔"""
        try:
            if self.collection:
                # 使用 ChromaDB 搜索
                where_clause = {}
                if filters:
                    for key, value in filters.items():
                        where_clause[key] = value
                
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit,
                    where=where_clause if where_clause else None
                )
                
                # 解析結果
                search_results = []
                if results['ids'] and results['distances']:
                    for doc_id, distance in zip(results['ids'][0], results['distances'][0]):
                        similarity = 1.0 - distance  # 轉換距離為相似度
                        search_results.append((doc_id, similarity))
                
                return search_results
            else:
                # 使用回退搜索
                return await self._fallback_search(query_embedding, limit, filters)
                
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return await self._fallback_search(query_embedding, limit, filters)
    
    async def _fallback_search(self, query_embedding: List[float], limit: int, 
                              filters: Dict[str, Any] = None) -> List[Tuple[str, float]]:
        """回退搜索實現"""
        results = []
        
        for doc_id, doc in self.fallback_storage.items():
            # 應用過濾器
            if filters:
                match = True
                for key, value in filters.items():
                    if key == "data_type" and doc.data_type.value != value:
                        match = False
                        break
                    elif key in doc.metadata and doc.metadata[key] != value:
                        match = False
                        break
                
                if not match:
                    continue
            
            # 計算相似度（簡化實現）
            if doc.embedding:
                similarity = self._cosine_similarity(query_embedding, doc.embedding)
            else:
                similarity = 0.5  # 默認相似度
            
            results.append((doc_id, similarity))
        
        # 排序並返回前 N 個結果
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """計算餘弦相似度"""
        try:
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(a * a for a in vec2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
        except:
            return 0.0
    
    async def get_document(self, doc_id: str) -> Optional[Document]:
        """獲取文檔"""
        try:
            if self.collection:
                results = self.collection.get(ids=[doc_id])
                if results['ids']:
                    metadata = results['metadatas'][0]
                    content = results['documents'][0]
                    
                    # 重建 Document 對象
                    doc = Document(
                        doc_id=doc_id,
                        content=content,
                        data_type=DataType(metadata.get('data_type', 'documentation')),
                        metadata=metadata.get('metadata', {}),
                        created_at=datetime.fromisoformat(metadata.get('created_at', datetime.now().isoformat())),
                        updated_at=datetime.fromisoformat(metadata.get('updated_at', datetime.now().isoformat())),
                        access_count=metadata.get('access_count', 0),
                        relevance_score=metadata.get('relevance_score', 0.0)
                    )
                    return doc
            else:
                return self.fallback_storage.get(doc_id)
                
        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {e}")
            return self.fallback_storage.get(doc_id)
        
        return None
    
    async def delete_document(self, doc_id: str) -> bool:
        """刪除文檔"""
        try:
            if self.collection:
                self.collection.delete(ids=[doc_id])
            
            if doc_id in self.fallback_storage:
                del self.fallback_storage[doc_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
    
    async def update_document(self, document: Document):
        """更新文檔"""
        await self.delete_document(document.doc_id)
        await self.add_documents([document])

class UniversalRAGEngine:
    """通用 RAG 引擎"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = "Universal RAG Engine"
        self.version = "1.0.0"
        
        # 初始化子組件
        self.embedding_engine = EmbeddingEngine(self.config.get("embedding", {}))
        self.vector_store = VectorStore(self.config.get("vector_store", {}))
        
        # 配置參數
        self.max_chunk_size = self.config.get("max_chunk_size", 2000)
        self.chunk_overlap = self.config.get("chunk_overlap", 200)
        self.default_search_limit = self.config.get("default_search_limit", 10)
        self.similarity_threshold = self.config.get("similarity_threshold", 0.3)
        
        # 狀態管理
        self.initialized = False
        self.status = "initializing"
        
        # 性能統計
        self.stats = {
            "total_documents": 0,
            "total_searches": 0,
            "successful_searches": 0,
            "average_search_time": 0.0,
            "data_type_distribution": {dt.value: 0 for dt in DataType}
        }
        
        logger.info(f"Initializing {self.name} v{self.version}")
    
    async def initialize(self):
        """初始化 RAG 引擎"""
        try:
            logger.info("Initializing Universal RAG Engine components...")
            
            # 初始化嵌入引擎
            await self.embedding_engine.initialize()
            logger.info("✅ Embedding Engine initialized")
            
            # 初始化向量存儲
            await self.vector_store.initialize()
            logger.info("✅ Vector Store initialized")
            
            self.initialized = True
            self.status = "ready"
            logger.info(f"🎉 {self.name} initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.name}: {e}")
            self.status = "error"
            return False
    
    async def add_document(self, content: str, data_type: DataType, 
                          metadata: Dict[str, Any] = None) -> str:
        """添加單個文檔"""
        doc_id = f"{data_type.value}_{hashlib.md5(content.encode()).hexdigest()[:12]}"
        
        # 生成嵌入
        embedding = await self.embedding_engine.encode(content)
        
        # 創建文檔對象
        document = Document(
            doc_id=doc_id,
            content=content,
            data_type=data_type,
            metadata=metadata or {},
            embedding=embedding
        )
        
        # 添加到向量存儲
        await self.vector_store.add_documents([document])
        
        # 更新統計
        self.stats["total_documents"] += 1
        self.stats["data_type_distribution"][data_type.value] += 1
        
        logger.debug(f"Added document {doc_id} of type {data_type.value}")
        return doc_id
    
    async def add_documents_batch(self, documents_data: List[Tuple[str, DataType, Dict[str, Any]]]) -> List[str]:
        """批量添加文檔"""
        documents = []
        doc_ids = []
        
        # 準備文檔內容
        contents = [content for content, _, _ in documents_data]
        
        # 批量生成嵌入
        embeddings = await self.embedding_engine.encode(contents)
        if not isinstance(embeddings[0], list):
            embeddings = [embeddings]
        
        # 創建文檔對象
        for i, (content, data_type, metadata) in enumerate(documents_data):
            doc_id = f"{data_type.value}_{hashlib.md5(content.encode()).hexdigest()[:12]}"
            
            document = Document(
                doc_id=doc_id,
                content=content,
                data_type=data_type,
                metadata=metadata or {},
                embedding=embeddings[i] if i < len(embeddings) else None
            )
            
            documents.append(document)
            doc_ids.append(doc_id)
        
        # 批量添加到向量存儲
        await self.vector_store.add_documents(documents)
        
        # 更新統計
        self.stats["total_documents"] += len(documents)
        for _, data_type, _ in documents_data:
            self.stats["data_type_distribution"][data_type.value] += 1
        
        logger.info(f"Added {len(documents)} documents in batch")
        return doc_ids
    
    async def search(self, query: str, data_types: List[DataType] = None, 
                    limit: int = None, mode: SearchMode = SearchMode.SEMANTIC,
                    filters: Dict[str, Any] = None) -> List[SearchResult]:
        """搜索文檔"""
        if not self.initialized:
            raise RuntimeError("RAG Engine not initialized")
        
        start_time = time.time()
        self.stats["total_searches"] += 1
        
        try:
            limit = limit or self.default_search_limit
            
            # 生成查詢嵌入
            query_embedding = await self.embedding_engine.encode(query)
            
            # 準備過濾器
            search_filters = filters or {}
            if data_types:
                # 如果指定了數據類型，需要分別搜索每種類型
                all_results = []
                for data_type in data_types:
                    type_filters = {**search_filters, "data_type": data_type.value}
                    type_results = await self.vector_store.search(
                        query_embedding, limit, type_filters
                    )
                    all_results.extend(type_results)
                
                # 合併並重新排序
                all_results.sort(key=lambda x: x[1], reverse=True)
                search_results = all_results[:limit]
            else:
                search_results = await self.vector_store.search(
                    query_embedding, limit, search_filters
                )
            
            # 構建結果對象
            results = []
            for rank, (doc_id, similarity) in enumerate(search_results):
                if similarity >= self.similarity_threshold:
                    document = await self.vector_store.get_document(doc_id)
                    if document:
                        # 更新訪問計數
                        document.access_count += 1
                        document.relevance_score = similarity
                        await self.vector_store.update_document(document)
                        
                        result = SearchResult(
                            document=document,
                            similarity_score=similarity,
                            rank=rank + 1,
                            search_metadata={
                                "query": query,
                                "search_mode": mode.value,
                                "search_time": time.time() - start_time
                            }
                        )
                        results.append(result)
            
            # 更新統計
            self.stats["successful_searches"] += 1
            search_time = time.time() - start_time
            self.stats["average_search_time"] = (
                (self.stats["average_search_time"] * (self.stats["successful_searches"] - 1) + search_time)
                / self.stats["successful_searches"]
            )
            
            logger.info(f"Search completed: found {len(results)} results in {search_time:.2f}s")
            return results
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
    
    async def search_code_knowledge(self, query: str, limit: int = 5) -> List[SearchResult]:
        """搜索代碼相關知識"""
        return await self.search(
            query=query,
            data_types=[DataType.CODE, DataType.BEST_PRACTICE, DataType.DESIGN_PATTERN],
            limit=limit,
            mode=SearchMode.SEMANTIC
        )
    
    async def search_project_experience(self, query: str, limit: int = 3) -> List[SearchResult]:
        """搜索項目經驗"""
        return await self.search(
            query=query,
            data_types=[DataType.PROJECT_KNOWLEDGE, DataType.DOCUMENTATION],
            limit=limit,
            mode=SearchMode.CONTEXTUAL
        )
    
    async def search_test_knowledge(self, query: str, limit: int = 5) -> List[SearchResult]:
        """搜索測試相關知識"""
        return await self.search(
            query=query,
            data_types=[DataType.CODE, DataType.BEST_PRACTICE],
            limit=limit,
            filters={"category": "testing"}
        )
    
    async def get_global_knowledge(self, query: str, limit: int = 3) -> List[SearchResult]:
        """獲取全局知識"""
        return await self.search(
            query=query,
            data_types=[DataType.GLOBAL_KNOWLEDGE, DataType.BEST_PRACTICE],
            limit=limit,
            mode=SearchMode.HYBRID
        )
    
    async def add_code_snippet(self, code: str, language: str, description: str = "",
                             project_path: str = None) -> str:
        """添加代碼片段"""
        metadata = {
            "language": language,
            "description": description,
            "category": "code_snippet"
        }
        
        if project_path:
            metadata["project_path"] = project_path
        
        return await self.add_document(code, DataType.CODE, metadata)
    
    async def add_documentation(self, content: str, doc_type: str = "general",
                               source: str = None) -> str:
        """添加文檔"""
        metadata = {
            "doc_type": doc_type,
            "category": "documentation"
        }
        
        if source:
            metadata["source"] = source
        
        return await self.add_document(content, DataType.DOCUMENTATION, metadata)
    
    async def add_conversation_context(self, conversation: str, session_id: str,
                                     participants: List[str] = None) -> str:
        """添加對話上下文"""
        metadata = {
            "session_id": session_id,
            "participants": participants or [],
            "category": "conversation"
        }
        
        return await self.add_document(conversation, DataType.CONVERSATION, metadata)
    
    async def add_project_knowledge(self, knowledge: str, project_name: str,
                                   knowledge_type: str = "general") -> str:
        """添加項目知識"""
        metadata = {
            "project_name": project_name,
            "knowledge_type": knowledge_type,
            "category": "project"
        }
        
        return await self.add_document(knowledge, DataType.PROJECT_KNOWLEDGE, metadata)
    
    async def cleanup_old_documents(self, max_age_days: int = 30, 
                                   min_access_count: int = 1) -> int:
        """清理舊文檔"""
        # 這裡需要實現清理邏輯
        # 由於向量存儲的限制，這是一個簡化實現
        logger.info(f"Cleanup requested for documents older than {max_age_days} days")
        return 0  # 返回清理的文檔數量
    
    def get_status(self) -> Dict[str, Any]:
        """獲取引擎狀態"""
        return {
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "initialized": self.initialized,
            "stats": self.stats,
            "config": {
                "max_chunk_size": self.max_chunk_size,
                "similarity_threshold": self.similarity_threshold,
                "embedding_model": self.embedding_engine.model_name
            },
            "components": {
                "embedding_engine": {
                    "initialized": self.embedding_engine.initialized,
                    "model_available": self.embedding_engine.model is not None,
                    "embedding_dim": self.embedding_engine.embedding_dim
                },
                "vector_store": {
                    "initialized": self.vector_store.initialized,
                    "chromadb_available": CHROMADB_AVAILABLE,
                    "fallback_docs": len(self.vector_store.fallback_storage)
                }
            }
        }
    
    async def shutdown(self):
        """關閉引擎"""
        logger.info("Shutting down Universal RAG Engine...")
        
        # 清理資源
        if hasattr(self.embedding_engine, 'model') and self.embedding_engine.model:
            del self.embedding_engine.model
        
        if self.vector_store.chroma_client:
            # ChromaDB 會自動持久化
            pass
        
        self.status = "shutdown"
        logger.info("Universal RAG Engine shut down")

# 工廠函數
async def create_universal_rag_engine(config: Dict[str, Any] = None) -> UniversalRAGEngine:
    """創建並初始化通用 RAG 引擎"""
    engine = UniversalRAGEngine(config)
    await engine.initialize()
    return engine

if __name__ == "__main__":
    # 測試代碼
    async def test_rag_engine():
        config = {
            "embedding": {"model_name": "all-MiniLM-L6-v2"},
            "vector_store": {"storage_path": "./test_vector_store"},
            "max_chunk_size": 1000,
            "similarity_threshold": 0.3
        }
        
        engine = await create_universal_rag_engine(config)
        
        # 添加測試文檔
        await engine.add_code_snippet(
            "def hello_world():\n    print('Hello, World!')",
            "python",
            "Simple hello world function"
        )
        
        await engine.add_documentation(
            "This is a comprehensive guide to Python programming.",
            "tutorial",
            "python_guide"
        )
        
        # 搜索測試
        results = await engine.search("python function", limit=5)
        print(f"Found {len(results)} results")
        
        for result in results:
            print(f"- {result.document.data_type.value}: {result.similarity_score:.3f}")
            print(f"  {result.document.content[:100]}...")
        
        # 獲取狀態
        status = engine.get_status()
        print(f"Engine status: {status['status']}")
        print(f"Total documents: {status['stats']['total_documents']}")
        
        # 關閉引擎
        await engine.shutdown()
    
    asyncio.run(test_rag_engine())

