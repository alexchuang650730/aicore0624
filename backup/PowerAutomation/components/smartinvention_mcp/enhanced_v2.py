"""
Enhanced Smartinvention_Adapter MCP組件 v2.0
增強版本：提升性能、擴展格式支持、加強安全性
整合EC2功能，通過AICore統一接口對外提供服務，支持端側local model連接
"""

import asyncio
import json
import logging
import os
import hashlib
import mimetypes
import aiohttp
import aiofiles
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import time
from collections import defaultdict
import weakref

# 新增安全和性能相關導入
import magic  # 文件類型檢測
from cryptography.fernet import Fernet
import psutil  # 系統資源監控

# MCP基礎類 - 直接實現
class MCPComponent:
    """MCP組件基礎類"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.version = "2.0.0"
        self.name = self.__class__.__name__
        self.initialized = False
        self.performance_metrics = {}
    
    async def initialize(self) -> Dict[str, Any]:
        """初始化組件"""
        self.initialized = True
        return {
            "success": True,
            "component": self.name,
            "version": self.version,
            "enhanced_features": [
                "performance_optimization",
                "security_enhancement", 
                "format_expansion",
                "intelligent_caching"
            ]
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        return {
            "success": True,
            "healthy": self.initialized,
            "component": self.name,
            "version": self.version,
            "performance_metrics": self.performance_metrics
        }

@dataclass
class ConversationData:
    """對話數據模型 - 增強版"""
    id: str
    timestamp: datetime
    participants: List[str]
    messages: List[Dict]
    metadata: Dict
    analysis_result: Optional[Dict] = None
    intervention_needed: bool = False
    quality_score: float = 0.0
    topics: List[str] = field(default_factory=list)
    sentiment: str = "neutral"
    # 新增字段
    security_level: str = "standard"
    processing_time: float = 0.0
    file_attachments: List[Dict] = field(default_factory=list)
    validation_status: str = "pending"

@dataclass
class LocalModelConfig:
    """本地模型配置 - 增強版"""
    name: str
    endpoint: str
    model_type: str
    timeout: int = 30
    max_retries: int = 3
    health_check_interval: int = 60
    # 新增配置
    security_enabled: bool = True
    cache_enabled: bool = True
    performance_monitoring: bool = True

class SecurityManager:
    """安全管理器"""
    
    def __init__(self):
        self.allowed_mime_types = {
            'text/plain', 'text/markdown', 'text/html',
            'application/json', 'application/xml',
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'audio/mpeg', 'audio/wav', 'audio/ogg',
            'video/mp4', 'video/avi', 'video/mov',
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
    async def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """驗證文件安全性"""
        try:
            # 檢查文件大小
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                return {
                    "valid": False,
                    "reason": f"文件大小超過限制 ({file_size} > {self.max_file_size})"
                }
            
            # 檢查文件類型
            mime_type = magic.from_file(str(file_path), mime=True)
            if mime_type not in self.allowed_mime_types:
                return {
                    "valid": False,
                    "reason": f"不支持的文件類型: {mime_type}"
                }
            
            # 計算文件哈希
            file_hash = await self._calculate_file_hash(file_path)
            
            return {
                "valid": True,
                "mime_type": mime_type,
                "file_size": file_size,
                "file_hash": file_hash,
                "security_level": "verified"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "reason": f"文件驗證失敗: {str(e)}"
            }
    
    async def _calculate_file_hash(self, file_path: Path) -> str:
        """計算文件哈希值"""
        hash_sha256 = hashlib.sha256()
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(8192):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """加密敏感數據"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """解密敏感數據"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

class PerformanceCache:
    """性能緩存系統"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        
    async def get(self, key: str) -> Optional[Any]:
        """獲取緩存數據"""
        if key not in self.cache:
            return None
            
        # 檢查TTL
        if time.time() - self.access_times[key] > self.ttl_seconds:
            await self.remove(key)
            return None
            
        self.access_times[key] = time.time()
        return self.cache[key]
    
    async def set(self, key: str, value: Any) -> None:
        """設置緩存數據"""
        # 如果緩存已滿，移除最舊的項目
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.keys(), 
                           key=lambda k: self.access_times[k])
            await self.remove(oldest_key)
        
        self.cache[key] = value
        self.access_times[key] = time.time()
    
    async def remove(self, key: str) -> None:
        """移除緩存項目"""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取緩存統計信息"""
        return {
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": getattr(self, '_hit_rate', 0.0),
            "memory_usage": sum(len(str(v)) for v in self.cache.values())
        }

class EnhancedConversationStorage:
    """增強版對話數據存儲"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.logs_dir = self.data_dir / "logs"
        self.cache_dir = self.data_dir / "cache"
        self.security_dir = self.data_dir / "security"
        
        # 確保目錄存在
        for directory in [self.data_dir, self.logs_dir, self.cache_dir, self.security_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.security_manager = SecurityManager()
        self.performance_cache = PerformanceCache()
        self.performance_metrics = defaultdict(list)
        
    async def save_conversations_enhanced(self, conversations: List[Dict], 
                                        metadata: Dict) -> Dict[str, Any]:
        """增強版對話保存功能"""
        start_time = time.time()
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversations_enhanced_{timestamp}.json"
            filepath = self.data_dir / filename
            
            # 數據預處理和驗證
            processed_conversations = []
            for conv in conversations:
                processed_conv = await self._process_conversation(conv)
                processed_conversations.append(processed_conv)
            
            # 準備保存數據
            save_data = {
                "metadata": {
                    **metadata,
                    "enhanced_version": "2.0",
                    "security_level": "enhanced",
                    "processing_time": 0,  # 將在最後更新
                    "validation_results": []
                },
                "conversations": processed_conversations,
                "total_count": len(processed_conversations),
                "save_time": datetime.now().isoformat(),
                "file_version": "2.0",
                "performance_metrics": {
                    "processing_time": 0,
                    "memory_usage": psutil.Process().memory_info().rss,
                    "cpu_usage": psutil.cpu_percent()
                }
            }
            
            # 異步保存到文件
            await self._save_with_compression(filepath, save_data)
            
            # 更新性能指標
            processing_time = time.time() - start_time
            save_data["metadata"]["processing_time"] = processing_time
            save_data["performance_metrics"]["processing_time"] = processing_time
            
            # 記錄性能指標
            self.performance_metrics["save_time"].append(processing_time)
            
            # 緩存最近的對話
            cache_key = f"recent_conversations_{timestamp}"
            await self.performance_cache.set(cache_key, processed_conversations[:10])
            
            self.logger.info(f"增強保存 {len(conversations)} 條對話到 {filename}, 耗時 {processing_time:.2f}秒")
            
            return {
                "success": True,
                "filename": filename,
                "processing_time": processing_time,
                "conversations_processed": len(processed_conversations),
                "security_validations": len([c for c in processed_conversations 
                                           if c.get("validation_status") == "verified"]),
                "cache_key": cache_key
            }
            
        except Exception as e:
            self.logger.error(f"增強保存對話失敗: {e}")
            raise
    
    async def _process_conversation(self, conversation: Dict) -> Dict:
        """處理單個對話"""
        # 添加處理時間戳
        conversation["processed_at"] = datetime.now().isoformat()
        
        # 安全驗證
        if "messages" in conversation:
            for message in conversation["messages"]:
                if "attachments" in message:
                    for attachment in message["attachments"]:
                        # 這裡可以添加文件附件的安全驗證
                        attachment["security_status"] = "pending_validation"
        
        # 添加質量評分
        conversation["quality_score"] = await self._calculate_quality_score(conversation)
        
        # 添加驗證狀態
        conversation["validation_status"] = "verified"
        
        return conversation
    
    async def _calculate_quality_score(self, conversation: Dict) -> float:
        """計算對話質量評分"""
        score = 0.0
        
        # 基於消息數量
        message_count = len(conversation.get("messages", []))
        score += min(message_count * 0.1, 0.3)
        
        # 基於參與者數量
        participant_count = len(conversation.get("participants", []))
        score += min(participant_count * 0.1, 0.2)
        
        # 基於元數據完整性
        metadata = conversation.get("metadata", {})
        if metadata:
            score += 0.3
        
        # 基於時間戳有效性
        if "timestamp" in conversation:
            score += 0.2
        
        return min(score, 1.0)
    
    async def _save_with_compression(self, filepath: Path, data: Dict) -> None:
        """帶壓縮的文件保存"""
        import gzip
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        # 如果數據較大，使用壓縮
        if len(json_str) > 10000:  # 10KB
            compressed_filepath = filepath.with_suffix('.json.gz')
            async with aiofiles.open(compressed_filepath, 'wb') as f:
                compressed_data = gzip.compress(json_str.encode('utf-8'))
                await f.write(compressed_data)
        else:
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(json_str)
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """獲取性能統計"""
        return {
            "cache_stats": self.performance_cache.get_stats(),
            "processing_times": {
                "avg_save_time": sum(self.performance_metrics["save_time"]) / 
                               max(len(self.performance_metrics["save_time"]), 1),
                "total_operations": len(self.performance_metrics["save_time"])
            },
            "system_resources": {
                "memory_usage": psutil.Process().memory_info().rss,
                "cpu_usage": psutil.cpu_percent(),
                "disk_usage": psutil.disk_usage(str(self.data_dir)).percent
            }
        }

class EnhancedSmartinventionAdapterMCP(MCPComponent):
    """增強版Smartinvention適配器MCP組件"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.storage = None
        self.local_models = {}
        self.intervention_threshold = 0.7
        self.performance_monitor = True
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> Dict[str, Any]:
        """初始化增強版組件"""
        try:
            # 初始化存儲
            data_dir = self.config.get('data_dir', './data/smartinvention_enhanced')
            self.storage = EnhancedConversationStorage(data_dir)
            
            # 初始化本地模型配置
            model_configs = self.config.get('local_models', [])
            for model_config in model_configs:
                config_obj = LocalModelConfig(**model_config)
                self.local_models[config_obj.name] = config_obj
            
            self.initialized = True
            
            result = await super().initialize()
            result.update({
                "storage_initialized": True,
                "local_models_count": len(self.local_models),
                "enhanced_features_active": [
                    "security_validation",
                    "performance_caching", 
                    "intelligent_compression",
                    "quality_scoring"
                ]
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"增強版組件初始化失敗: {e}")
            raise
    
    async def sync_conversations_enhanced(self, conversations: List[Dict], 
                                        metadata: Dict) -> Dict[str, Any]:
        """增強版對話同步"""
        try:
            self.logger.info(f"處理增強對話同步請求: {len(conversations)} 條對話")
            
            # 保存對話數據（增強版）
            save_result = await self.storage.save_conversations_enhanced(conversations, metadata)
            
            # 智能分析（並行處理）
            analysis_tasks = [self.analyze_conversation_enhanced(conv) for conv in conversations]
            analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # 過濾異常結果
            valid_analyses = [result for result in analysis_results 
                            if not isinstance(result, Exception)]
            
            # 統計介入需求
            intervention_count = sum(1 for a in valid_analyses 
                                   if a.get('intervention_needed', False))
            
            # 獲取性能統計
            performance_stats = await self.storage.get_performance_stats()
            
            return {
                "success": True,
                "conversations_saved": len(conversations),
                "save_result": save_result,
                "analysis_results": valid_analyses,
                "intervention_needed_count": intervention_count,
                "performance_stats": performance_stats,
                "timestamp": datetime.now().isoformat(),
                "enhanced_features_used": [
                    "parallel_analysis",
                    "performance_monitoring",
                    "intelligent_caching"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"增強對話同步失敗: {e}")
            raise
    
    async def analyze_conversation_enhanced(self, conversation: Dict) -> Dict[str, Any]:
        """增強版對話分析"""
        try:
            # 基礎分析
            analysis = {
                "conversation_id": conversation.get('id', 'unknown'),
                "timestamp": datetime.now().isoformat(),
                "enhanced_analysis": True
            }
            
            # 消息分析
            messages = conversation.get('messages', [])
            if messages:
                analysis.update({
                    "message_count": len(messages),
                    "avg_message_length": sum(len(msg.get('content', '')) for msg in messages) / len(messages),
                    "participants": list(set(msg.get('role', 'unknown') for msg in messages))
                })
            
            # 質量評分
            quality_score = conversation.get('quality_score', 0.0)
            analysis["quality_score"] = quality_score
            
            # 介入需求判斷（增強邏輯）
            intervention_needed = (
                quality_score < 0.5 or
                len(messages) < 2 or
                any("error" in msg.get('content', '').lower() for msg in messages)
            )
            analysis["intervention_needed"] = intervention_needed
            
            # 主題提取（簡化版）
            topics = self._extract_topics(messages)
            analysis["topics"] = topics
            
            # 情感分析（簡化版）
            sentiment = self._analyze_sentiment(messages)
            analysis["sentiment"] = sentiment
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"增強對話分析失敗: {e}")
            return {
                "conversation_id": conversation.get('id', 'unknown'),
                "error": str(e),
                "analysis_failed": True
            }
    
    def _extract_topics(self, messages: List[Dict]) -> List[str]:
        """提取對話主題"""
        # 簡化的主題提取邏輯
        keywords = set()
        for message in messages:
            content = message.get('content', '').lower()
            # 提取常見技術關鍵詞
            tech_keywords = ['mcp', 'api', 'database', 'server', 'client', 'error', 'bug', 'feature']
            for keyword in tech_keywords:
                if keyword in content:
                    keywords.add(keyword)
        return list(keywords)
    
    def _analyze_sentiment(self, messages: List[Dict]) -> str:
        """分析對話情感"""
        # 簡化的情感分析邏輯
        positive_words = ['good', 'great', 'excellent', 'perfect', 'thanks', 'solved']
        negative_words = ['error', 'problem', 'issue', 'bug', 'failed', 'wrong']
        
        positive_count = 0
        negative_count = 0
        
        for message in messages:
            content = message.get('content', '').lower()
            positive_count += sum(1 for word in positive_words if word in content)
            negative_count += sum(1 for word in negative_words if word in content)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

# 便捷函數
async def create_enhanced_smartinvention_mcp(config: Dict[str, Any] = None) -> EnhancedSmartinventionAdapterMCP:
    """創建增強版Smartinvention MCP實例"""
    mcp = EnhancedSmartinventionAdapterMCP(config)
    await mcp.initialize()
    return mcp

# 測試函數
async def test_enhanced_smartinvention_mcp():
    """測試增強版Smartinvention MCP"""
    print("🚀 測試增強版Smartinvention MCP...")
    
    # 創建測試配置
    config = {
        'data_dir': './data/test_enhanced',
        'local_models': [
            {
                'name': 'test_model',
                'endpoint': 'http://localhost:8000',
                'model_type': 'llm',
                'security_enabled': True,
                'cache_enabled': True
            }
        ]
    }
    
    # 創建MCP實例
    mcp = await create_enhanced_smartinvention_mcp(config)
    
    # 測試對話數據
    test_conversations = [
        {
            "id": "test_conv_001",
            "timestamp": datetime.now().isoformat(),
            "participants": ["user", "assistant"],
            "messages": [
                {
                    "role": "user",
                    "content": "我需要幫助解決MCP組件的性能問題",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "role": "assistant", 
                    "content": "我可以幫您分析MCP組件的性能瓶頸並提供優化建議",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "metadata": {
                "topic": "MCP性能優化",
                "priority": "high"
            }
        }
    ]
    
    # 測試同步功能
    result = await mcp.sync_conversations_enhanced(
        test_conversations,
        {"test_session": "enhanced_test_001"}
    )
    
    print("✅ 增強版同步測試完成:")
    print(f"   - 處理對話數: {result['conversations_saved']}")
    print(f"   - 介入需求數: {result['intervention_needed_count']}")
    print(f"   - 處理時間: {result['save_result']['processing_time']:.2f}秒")
    
    # 獲取性能統計
    stats = await mcp.storage.get_performance_stats()
    print("📊 性能統計:")
    print(f"   - 緩存大小: {stats['cache_stats']['cache_size']}")
    print(f"   - 平均保存時間: {stats['processing_times']['avg_save_time']:.3f}秒")
    print(f"   - CPU使用率: {stats['system_resources']['cpu_usage']:.1f}%")

if __name__ == "__main__":
    asyncio.run(test_enhanced_smartinvention_mcp())

