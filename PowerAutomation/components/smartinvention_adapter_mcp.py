"""
Smartinvention_Adapter MCP組件
整合EC2功能，通過AICore統一接口對外提供服務，支持端側local model連接
"""

import asyncio
import json
import logging
import os
import aiohttp
import aiofiles
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

# MCP基礎類 - 直接實現
class MCPComponent:
    """MCP組件基礎類"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.version = "2.0.0"
        self.name = self.__class__.__name__
        self.initialized = False
    
    async def initialize(self) -> Dict[str, Any]:
        """初始化組件"""
        self.initialized = True
        return {
            "success": True,
            "component": self.name,
            "version": self.version
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        return {
            "success": True,
            "healthy": self.initialized,
            "component": self.name,
            "version": self.version
        }

@dataclass
class ConversationData:
    """對話數據模型"""
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

@dataclass
class LocalModelConfig:
    """本地模型配置"""
    name: str
    endpoint: str
    model_type: str
    timeout: int = 30
    max_retries: int = 3
    health_check_interval: int = 60

class ConversationStorage:
    """對話數據存儲 - 整合原EC2存儲邏輯"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.logs_dir = self.data_dir / "logs"
        
        # 確保目錄存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
    
    async def save_conversations(self, conversations: List[Dict], metadata: Dict) -> str:
        """保存對話數據"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversations_{timestamp}.json"
            filepath = self.data_dir / filename
            
            # 準備保存數據
            save_data = {
                "metadata": metadata,
                "conversations": conversations,
                "total_count": len(conversations),
                "save_time": datetime.now().isoformat(),
                "file_version": "1.0"
            }
            
            # 保存到文件
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(save_data, indent=2, ensure_ascii=False))
            
            self.logger.info(f"保存 {len(conversations)} 條對話到 {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"保存對話失敗: {e}")
            raise
    
    async def save_intervention_analysis(self, analyses: List[Dict]) -> str:
        """保存介入分析結果"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"intervention_analysis_{timestamp}.json"
            filepath = self.data_dir / filename
            
            save_data = {
                "analyses": analyses,
                "total_count": len(analyses),
                "analysis_time": datetime.now().isoformat(),
                "file_version": "1.0"
            }
            
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(save_data, indent=2, ensure_ascii=False))
            
            self.logger.info(f"保存 {len(analyses)} 條分析結果到 {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"保存分析結果失敗: {e}")
            raise
    
    async def get_latest_conversations(self, limit: int = 10) -> List[Dict]:
        """獲取最新對話"""
        try:
            conversation_files = list(self.data_dir.glob("conversations_*.json"))
            conversation_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            conversations = []
            for file_path in conversation_files[:5]:  # 最多檢查5個文件
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
                    conversations.extend(data.get('conversations', []))
                
                if len(conversations) >= limit:
                    break
            
            return conversations[:limit]
            
        except Exception as e:
            self.logger.error(f"獲取最新對話失敗: {e}")
            return []
    
    async def get_interventions_needed(self) -> List[Dict]:
        """獲取需要介入的對話"""
        try:
            analysis_files = list(self.data_dir.glob("intervention_analysis_*.json"))
            analysis_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            interventions = []
            for file_path in analysis_files[:3]:  # 最多檢查3個文件
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
                    
                    # 篩選需要介入的分析結果
                    for analysis in data.get('analyses', []):
                        if analysis.get('intervention_needed', False):
                            interventions.append(analysis)
            
            return interventions
            
        except Exception as e:
            self.logger.error(f"獲取介入需求失敗: {e}")
            return []

class ConversationProcessor:
    """對話處理器 - 整合原EC2對話分析功能"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.storage = ConversationStorage(config.get('data_dir', '/tmp/smartinvention_data'))
        self.logger = logging.getLogger(__name__)
        
        # 分析配置
        self.analysis_config = config.get('analysis', {
            'enable_sentiment': True,
            'enable_intent': True,
            'enable_quality': True,
            'enable_topics': True,
            'intervention_threshold': 0.7
        })
    
    async def process_conversation_sync(self, conversations: List[Dict], metadata: Dict) -> Dict:
        """
        處理對話同步請求 (原 POST /api/sync/conversations)
        """
        try:
            self.logger.info(f"處理對話同步請求: {len(conversations)} 條對話")
            
            # 保存對話數據
            filename = await self.storage.save_conversations(conversations, metadata)
            
            # 智能分析
            analysis_results = []
            for conv in conversations:
                analysis = await self.analyze_conversation(conv)
                analysis_results.append(analysis)
            
            # 保存分析結果
            analysis_filename = await self.storage.save_intervention_analysis(analysis_results)
            
            # 統計介入需求
            intervention_count = sum(1 for a in analysis_results if a.get('intervention_needed', False))
            
            return {
                "success": True,
                "conversations_saved": len(conversations),
                "filename": filename,
                "analysis_filename": analysis_filename,
                "analysis_results": analysis_results,
                "intervention_needed_count": intervention_count,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"對話同步處理失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_latest_conversations(self, limit: int = 10) -> Dict:
        """
        獲取最新對話 (原 GET /api/conversations/latest)
        """
        try:
            conversations = await self.storage.get_latest_conversations(limit)
            
            return {
                "success": True,
                "conversations": conversations,
                "count": len(conversations),
                "limit": limit,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"獲取最新對話失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_interventions_needed(self) -> Dict:
        """
        獲取需要介入的對話 (原 GET /api/interventions/needed)
        """
        try:
            interventions = await self.storage.get_interventions_needed()
            
            # 按優先級排序
            interventions.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
            
            return {
                "success": True,
                "interventions": interventions,
                "count": len(interventions),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"獲取介入需求失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def analyze_conversation(self, conversation: Dict) -> Dict:
        """智能對話分析"""
        try:
            analysis = {
                "conversation_id": conversation.get("id", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "analysis_version": "1.0"
            }
            
            # 情感分析
            if self.analysis_config.get('enable_sentiment', True):
                analysis["sentiment"] = await self._analyze_sentiment(conversation)
            
            # 意圖分析
            if self.analysis_config.get('enable_intent', True):
                analysis["intent"] = await self._analyze_intent(conversation)
            
            # 質量評分
            if self.analysis_config.get('enable_quality', True):
                analysis["quality_score"] = await self._calculate_quality_score(conversation)
            
            # 主題提取
            if self.analysis_config.get('enable_topics', True):
                analysis["topics"] = await self._extract_topics(conversation)
            
            # 介入檢測
            analysis["intervention_needed"] = await self._check_intervention_needed(conversation, analysis)
            analysis["priority_score"] = await self._calculate_priority_score(conversation, analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"對話分析失敗: {e}")
            return {
                "conversation_id": conversation.get("id", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "intervention_needed": True,  # 分析失敗時標記為需要介入
                "priority_score": 0.5
            }
    
    async def _analyze_sentiment(self, conversation: Dict) -> Dict:
        """情感分析"""
        # 簡化的情感分析邏輯
        messages = conversation.get('messages', [])
        if not messages:
            return {"overall": "neutral", "confidence": 0.0}
        
        # 基於關鍵詞的簡單情感分析
        positive_keywords = ['好', '棒', '讚', '滿意', '開心', '謝謝']
        negative_keywords = ['不好', '差', '糟', '不滿', '生氣', '問題']
        
        positive_count = 0
        negative_count = 0
        total_words = 0
        
        for msg in messages:
            content = msg.get('content', '')
            total_words += len(content)
            
            for keyword in positive_keywords:
                positive_count += content.count(keyword)
            
            for keyword in negative_keywords:
                negative_count += content.count(keyword)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(positive_count / max(total_words, 1), 1.0)
        elif negative_count > positive_count:
            sentiment = "negative" 
            confidence = min(negative_count / max(total_words, 1), 1.0)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "overall": sentiment,
            "confidence": confidence,
            "positive_signals": positive_count,
            "negative_signals": negative_count
        }
    
    async def _analyze_intent(self, conversation: Dict) -> Dict:
        """意圖分析"""
        messages = conversation.get('messages', [])
        if not messages:
            return {"primary_intent": "unknown", "confidence": 0.0}
        
        # 基於關鍵詞的意圖識別
        intent_keywords = {
            "question": ["什麼", "如何", "怎麼", "為什麼", "?", "？"],
            "complaint": ["投訴", "抱怨", "不滿", "問題", "錯誤"],
            "request": ["請", "希望", "需要", "想要", "申請"],
            "praise": ["讚", "好", "棒", "滿意", "謝謝"]
        }
        
        intent_scores = {intent: 0 for intent in intent_keywords.keys()}
        
        for msg in messages:
            content = msg.get('content', '')
            for intent, keywords in intent_keywords.items():
                for keyword in keywords:
                    intent_scores[intent] += content.count(keyword)
        
        # 找出最高分的意圖
        primary_intent = max(intent_scores, key=intent_scores.get)
        max_score = intent_scores[primary_intent]
        total_score = sum(intent_scores.values())
        
        confidence = max_score / max(total_score, 1) if total_score > 0 else 0.0
        
        return {
            "primary_intent": primary_intent,
            "confidence": confidence,
            "all_intents": intent_scores
        }
    
    async def _calculate_quality_score(self, conversation: Dict) -> float:
        """計算對話質量評分"""
        messages = conversation.get('messages', [])
        if not messages:
            return 0.0
        
        score = 0.5  # 基礎分數
        
        # 對話長度評分
        if len(messages) >= 3:
            score += 0.2
        
        # 回應時間評分 (如果有時間戳)
        timestamps = [msg.get('timestamp') for msg in messages if msg.get('timestamp')]
        if len(timestamps) >= 2:
            # 簡化的回應時間評分
            score += 0.1
        
        # 內容豐富度評分
        total_length = sum(len(msg.get('content', '')) for msg in messages)
        if total_length > 100:
            score += 0.2
        
        return min(score, 1.0)
    
    async def _extract_topics(self, conversation: Dict) -> List[str]:
        """提取對話主題"""
        messages = conversation.get('messages', [])
        if not messages:
            return []
        
        # 簡化的主題提取
        topic_keywords = {
            "技術支持": ["技術", "支持", "幫助", "問題", "錯誤"],
            "產品諮詢": ["產品", "功能", "價格", "購買"],
            "服務投訴": ["投訴", "不滿", "服務", "態度"],
            "一般諮詢": ["諮詢", "了解", "資訊", "信息"]
        }
        
        content = " ".join(msg.get('content', '') for msg in messages)
        detected_topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics if detected_topics else ["一般對話"]
    
    async def _check_intervention_needed(self, conversation: Dict, analysis: Dict) -> bool:
        """檢測是否需要介入"""
        # 基於多個因素判斷是否需要介入
        intervention_factors = []
        
        # 情感因素
        sentiment = analysis.get('sentiment', {})
        if sentiment.get('overall') == 'negative' and sentiment.get('confidence', 0) > 0.7:
            intervention_factors.append("negative_sentiment")
        
        # 意圖因素
        intent = analysis.get('intent', {})
        if intent.get('primary_intent') == 'complaint' and intent.get('confidence', 0) > 0.6:
            intervention_factors.append("complaint_intent")
        
        # 質量因素
        quality_score = analysis.get('quality_score', 0.5)
        if quality_score < 0.3:
            intervention_factors.append("low_quality")
        
        # 關鍵詞檢測
        messages = conversation.get('messages', [])
        content = " ".join(msg.get('content', '') for msg in messages)
        urgent_keywords = ["緊急", "立即", "馬上", "重要", "嚴重"]
        if any(keyword in content for keyword in urgent_keywords):
            intervention_factors.append("urgent_keywords")
        
        # 如果有任何介入因素，則需要介入
        return len(intervention_factors) > 0
    
    async def _calculate_priority_score(self, conversation: Dict, analysis: Dict) -> float:
        """計算優先級評分"""
        score = 0.0
        
        # 情感權重
        sentiment = analysis.get('sentiment', {})
        if sentiment.get('overall') == 'negative':
            score += sentiment.get('confidence', 0) * 0.4
        
        # 意圖權重
        intent = analysis.get('intent', {})
        if intent.get('primary_intent') == 'complaint':
            score += intent.get('confidence', 0) * 0.3
        
        # 質量權重
        quality_score = analysis.get('quality_score', 0.5)
        if quality_score < 0.5:
            score += (0.5 - quality_score) * 0.3
        
        return min(score, 1.0)

class LocalModelConnector:
    """本地模型連接器 - 連接端側local model"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.models = {}  # 存儲模型連接
        self.logger = logging.getLogger(__name__)
        
        # 連接配置
        self.connection_config = {
            "timeout": config.get('model_timeout', 30),
            "max_retries": config.get('model_max_retries', 3),
            "health_check_interval": config.get('health_check_interval', 60)
        }
    
    async def connect_to_local_model(self, model_name: str, endpoint: str, model_type: str = "general", config: Dict = None) -> Dict:
        """連接到端側本地模型"""
        try:
            self.logger.info(f"連接本地模型: {model_name} at {endpoint}")
            
            # 創建模型配置
            model_config = LocalModelConfig(
                name=model_name,
                endpoint=endpoint,
                model_type=model_type,
                timeout=config.get('timeout', self.connection_config['timeout']) if config else self.connection_config['timeout'],
                max_retries=config.get('max_retries', self.connection_config['max_retries']) if config else self.connection_config['max_retries']
            )
            
            # 測試連接
            health_check = await self._test_model_connection(model_config)
            
            if health_check["healthy"]:
                self.models[model_name] = model_config
                self.logger.info(f"成功連接模型: {model_name}")
                
                return {
                    "success": True,
                    "model_name": model_name,
                    "endpoint": endpoint,
                    "model_type": model_type,
                    "status": "connected",
                    "health": health_check,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise Exception(f"模型健康檢查失敗: {health_check.get('error')}")
                
        except Exception as e:
            self.logger.error(f"連接模型失敗 {model_name}: {e}")
            return {
                "success": False,
                "model_name": model_name,
                "endpoint": endpoint,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def query_local_model(self, model_name: str, query: Dict, parameters: Dict = None) -> Dict:
        """查詢本地模型"""
        try:
            if model_name not in self.models:
                raise ValueError(f"模型 {model_name} 未連接")
            
            model_config = self.models[model_name]
            
            # 準備查詢數據
            query_data = {
                "query": query,
                "parameters": parameters or {},
                "timestamp": datetime.now().isoformat()
            }
            
            # 發送查詢
            result = await self._send_model_query(model_config, query_data)
            
            return {
                "success": True,
                "model_name": model_name,
                "query": query,
                "parameters": parameters,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"查詢模型失敗 {model_name}: {e}")
            return {
                "success": False,
                "model_name": model_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_model_status(self) -> Dict:
        """獲取所有模型狀態"""
        model_status = {}
        
        for model_name, model_config in self.models.items():
            try:
                health = await self._test_model_connection(model_config)
                model_status[model_name] = {
                    "status": "healthy" if health["healthy"] else "unhealthy",
                    "endpoint": model_config.endpoint,
                    "model_type": model_config.model_type,
                    "last_check": datetime.now().isoformat(),
                    "health_details": health
                }
            except Exception as e:
                model_status[model_name] = {
                    "status": "error",
                    "endpoint": model_config.endpoint,
                    "model_type": model_config.model_type,
                    "error": str(e),
                    "last_check": datetime.now().isoformat()
                }
        
        return {
            "success": True,
            "models": model_status,
            "total_models": len(model_status),
            "healthy_models": sum(1 for status in model_status.values() if status.get("status") == "healthy"),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _test_model_connection(self, model_config: LocalModelConfig) -> Dict:
        """測試模型連接"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=model_config.timeout)) as session:
                # 發送健康檢查請求
                health_url = f"{model_config.endpoint}/health"
                async with session.get(health_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "healthy": True,
                            "response_time": response.headers.get('X-Response-Time', 'unknown'),
                            "model_info": data
                        }
                    else:
                        return {
                            "healthy": False,
                            "error": f"HTTP {response.status}",
                            "response": await response.text()
                        }
                        
        except asyncio.TimeoutError:
            return {
                "healthy": False,
                "error": "連接超時"
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def _send_model_query(self, model_config: LocalModelConfig, query_data: Dict) -> Dict:
        """發送模型查詢"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=model_config.timeout)) as session:
                query_url = f"{model_config.endpoint}/query"
                async with session.post(query_url, json=query_data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"查詢失敗: HTTP {response.status} - {await response.text()}")
                        
        except Exception as e:
            raise Exception(f"發送查詢失敗: {e}")

class DataSyncManager:
    """數據同步管理器 - 整合原EC2同步功能"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 同步配置
        self.sync_config = {
            "sync_interval": config.get('sync_interval', 30),
            "max_retries": config.get('max_retries', 3),
            "endpoints": {
                "local": config.get('local_endpoint', 'http://localhost:8000'),
                "cloud": config.get('cloud_endpoint', 'http://18.212.97.173:8000')
            }
        }
        
        self.sync_running = False
        self.sync_task = None
    
    async def start_real_time_sync(self) -> Dict:
        """啟動實時同步"""
        try:
            if self.sync_running:
                return {
                    "success": True,
                    "message": "同步已在運行",
                    "sync_interval": self.sync_config["sync_interval"]
                }
            
            self.sync_running = True
            self.sync_task = asyncio.create_task(self._real_time_sync_loop())
            
            self.logger.info("啟動實時數據同步")
            return {
                "success": True,
                "message": "實時同步已啟動",
                "sync_interval": self.sync_config["sync_interval"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"啟動同步失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def stop_real_time_sync(self) -> Dict:
        """停止實時同步"""
        try:
            if not self.sync_running:
                return {
                    "success": True,
                    "message": "同步未在運行"
                }
            
            self.sync_running = False
            if self.sync_task:
                self.sync_task.cancel()
                try:
                    await self.sync_task
                except asyncio.CancelledError:
                    pass
            
            self.logger.info("停止實時數據同步")
            return {
                "success": True,
                "message": "實時同步已停止",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"停止同步失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_sync_status(self) -> Dict:
        """獲取同步狀態"""
        return {
            "success": True,
            "sync_running": self.sync_running,
            "sync_interval": self.sync_config["sync_interval"],
            "endpoints": self.sync_config["endpoints"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _real_time_sync_loop(self):
        """實時同步循環"""
        while self.sync_running:
            try:
                # 執行同步操作
                await self._perform_sync()
                
                # 等待下一次同步
                await asyncio.sleep(self.sync_config["sync_interval"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"同步循環錯誤: {e}")
                await asyncio.sleep(5)  # 錯誤後短暫等待
    
    async def _perform_sync(self):
        """執行同步操作"""
        # 這裡實現具體的同步邏輯
        # 可以根據需要同步對話數據、分析結果等
        self.logger.debug("執行數據同步...")

class SmartinventionAdapterMCP(MCPComponent):
    """
    Smartinvention適配器MCP組件
    整合EC2功能，通過AICore統一接口對外提供服務
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 初始化子組件
        self.conversation_processor = ConversationProcessor(config)
        self.local_model_connector = LocalModelConnector(config)
        self.data_sync_manager = DataSyncManager(config)
        
        # AICore接口配置 - 接手原EC2端口
        self.aicore_endpoints = {
            "conversation_sync": "/api/sync/conversations",
            "conversation_latest": "/api/conversations/latest", 
            "interventions_needed": "/api/interventions/needed",
            "health_check": "/api/health",
            "statistics": "/api/statistics",
            "local_model_connect": "/api/local-models/connect",
            "local_model_query": "/api/local-models/query",
            "local_model_status": "/api/local-models/status",
            "sync_start": "/api/sync/start",
            "sync_status": "/api/sync/status"
        }
    
    async def initialize(self) -> Dict:
        """初始化MCP組件"""
        try:
            self.logger.info("初始化Smartinvention Adapter MCP")
            
            # 啟動數據同步
            sync_result = await self.data_sync_manager.start_real_time_sync()
            
            return {
                "success": True,
                "component": self.name,
                "version": self.version,
                "endpoints": list(self.aicore_endpoints.values()),
                "sync_started": sync_result.get("success", False),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"初始化失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def health_check(self) -> Dict:
        """健康檢查 (原 GET /api/health)"""
        try:
            # 檢查各子組件狀態
            model_status = await self.local_model_connector.get_model_status()
            sync_status = await self.data_sync_manager.get_sync_status()
            
            healthy = (
                model_status.get("success", False) and
                sync_status.get("success", False)
            )
            
            return {
                "success": True,
                "healthy": healthy,
                "components": {
                    "conversation_processor": True,  # 總是健康
                    "local_model_connector": model_status.get("success", False),
                    "data_sync_manager": sync_status.get("success", False)
                },
                "model_status": model_status,
                "sync_status": sync_status,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"健康檢查失敗: {e}")
            return {
                "success": False,
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_statistics(self) -> Dict:
        """獲取統計信息 (原 GET /api/statistics)"""
        try:
            # 收集各種統計信息
            model_status = await self.local_model_connector.get_model_status()
            sync_status = await self.data_sync_manager.get_sync_status()
            
            # 簡化的統計信息
            stats = {
                "total_models": model_status.get("total_models", 0),
                "healthy_models": model_status.get("healthy_models", 0),
                "sync_running": sync_status.get("sync_running", False),
                "sync_interval": sync_status.get("sync_interval", 0),
                "uptime": "unknown",  # 可以添加運行時間統計
                "last_sync": "unknown"  # 可以添加最後同步時間
            }
            
            return {
                "success": True,
                "statistics": stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"獲取統計失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # 對話處理方法
    async def process_conversation_sync(self, request_data: Dict) -> Dict:
        """處理對話同步"""
        conversations = request_data.get("conversations", [])
        metadata = request_data.get("metadata", {})
        return await self.conversation_processor.process_conversation_sync(conversations, metadata)
    
    async def get_latest_conversations(self, request_data: Dict) -> Dict:
        """獲取最新對話"""
        limit = request_data.get("limit", 10)
        return await self.conversation_processor.get_latest_conversations(limit)
    
    async def get_interventions_needed(self, request_data: Dict) -> Dict:
        """獲取需要介入的對話"""
        return await self.conversation_processor.get_interventions_needed()
    
    # 本地模型方法
    async def connect_local_model(self, request_data: Dict) -> Dict:
        """連接本地模型"""
        model_name = request_data.get("model_name")
        endpoint = request_data.get("endpoint")
        model_type = request_data.get("model_type", "general")
        config = request_data.get("config", {})
        
        return await self.local_model_connector.connect_to_local_model(
            model_name, endpoint, model_type, config
        )
    
    async def query_local_model(self, request_data: Dict) -> Dict:
        """查詢本地模型"""
        model_name = request_data.get("model_name")
        query = request_data.get("query")
        parameters = request_data.get("parameters", {})
        
        return await self.local_model_connector.query_local_model(
            model_name, query, parameters
        )
    
    async def get_model_status(self, request_data: Dict) -> Dict:
        """獲取模型狀態"""
        return await self.local_model_connector.get_model_status()
    
    # 同步管理方法
    async def start_sync(self, request_data: Dict) -> Dict:
        """啟動同步"""
        return await self.data_sync_manager.start_real_time_sync()
    
    async def get_sync_status(self, request_data: Dict) -> Dict:
        """獲取同步狀態"""
        return await self.data_sync_manager.get_sync_status()
    
    # MCP接口實現
    def get_capabilities(self) -> Dict:
        """獲取MCP能力"""
        return {
            "conversation_processing": {
                "description": "智能對話處理和分析",
                "methods": [
                    "process_conversation_sync",
                    "get_latest_conversations",
                    "get_interventions_needed",
                    "analyze_conversation"
                ]
            },
            "local_model_management": {
                "description": "本地模型連接和管理",
                "methods": [
                    "connect_local_model",
                    "query_local_model",
                    "get_model_status"
                ]
            },
            "data_synchronization": {
                "description": "數據同步管理",
                "methods": [
                    "start_sync",
                    "stop_sync",
                    "get_sync_status"
                ]
            },
            "system_management": {
                "description": "系統管理和監控",
                "methods": [
                    "health_check",
                    "get_statistics"
                ]
            }
        }
    
    def get_tools(self) -> List[Dict]:
        """獲取MCP工具"""
        return [
            {
                "name": "sync_conversations",
                "description": "同步對話數據，支持端側到雲端的雙向同步",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "conversations": {"type": "array"},
                        "metadata": {"type": "object"},
                        "sync_direction": {"type": "string", "enum": ["to_cloud", "from_cloud", "bidirectional"]}
                    },
                    "required": ["conversations"]
                }
            },
            {
                "name": "connect_local_model", 
                "description": "連接端側本地模型",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "model_name": {"type": "string"},
                        "endpoint": {"type": "string"},
                        "model_type": {"type": "string"},
                        "config": {"type": "object"}
                    },
                    "required": ["model_name", "endpoint"]
                }
            },
            {
                "name": "analyze_conversation",
                "description": "智能分析對話內容，提取情感、意圖、質量等信息",
                "input_schema": {
                    "type": "object", 
                    "properties": {
                        "conversation": {"type": "object"},
                        "analysis_type": {"type": "string", "enum": ["full", "sentiment", "intent", "quality"]},
                        "use_local_model": {"type": "boolean"}
                    },
                    "required": ["conversation"]
                }
            },
            {
                "name": "query_local_model",
                "description": "查詢端側本地模型",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "model_name": {"type": "string"},
                        "query": {"type": "object"},
                        "parameters": {"type": "object"}
                    },
                    "required": ["model_name", "query"]
                }
            },
            {
                "name": "get_system_status",
                "description": "獲取系統整體狀態",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "include_details": {"type": "boolean"}
                    }
                }
            }
        ]

# 導出主要類
__all__ = [
    "SmartinventionAdapterMCP",
    "ConversationProcessor", 
    "LocalModelConnector",
    "DataSyncManager",
    "ConversationStorage"
]

