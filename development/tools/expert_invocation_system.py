#!/usr/bin/env python3
"""
Expert Invocation System for AICore with Human-in-the-Loop Integration

這個系統設計用於智能地調用各種專家系統和人工專家，提供專業的決策支持。
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Set
from datetime import datetime, timedelta
import uuid
import aiohttp
import yaml
from concurrent.futures import ThreadPoolExecutor
import threading

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExpertType(Enum):
    """專家類型枚舉"""
    TECHNICAL = "technical"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    DATA = "data"
    INTEGRATION = "integration"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"

class ExpertLevel(Enum):
    """專家級別枚舉"""
    JUNIOR = 1
    INTERMEDIATE = 2
    SENIOR = 3
    ARCHITECT = 4
    PRINCIPAL = 5

class ConsultationStatus(Enum):
    """諮詢狀態枚舉"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class ExpertAvailability(Enum):
    """專家可用性枚舉"""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ON_CALL = "on_call"

@dataclass
class ExpertProfile:
    """專家檔案"""
    expert_id: str
    name: str
    expert_type: ExpertType
    level: ExpertLevel
    specializations: List[str]
    availability: ExpertAvailability = ExpertAvailability.AVAILABLE
    current_load: int = 0  # 當前處理的案例數
    max_concurrent: int = 3  # 最大並發處理數
    average_response_time: float = 300.0  # 平均響應時間（秒）
    success_rate: float = 0.95  # 成功率
    rating: float = 4.5  # 評分
    contact_info: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_active: datetime = field(default_factory=datetime.now)

@dataclass
class ConsultationRequest:
    """諮詢請求"""
    request_id: str
    workflow_id: str
    expert_type: ExpertType
    required_level: ExpertLevel
    title: str
    description: str
    context: Dict[str, Any]
    priority: int = 3  # 1-5, 5最高
    timeout: int = 1800  # 超時時間（秒）
    required_specializations: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    callback_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    requester_id: Optional[str] = None

@dataclass
class ConsultationResponse:
    """諮詢響應"""
    response_id: str
    request_id: str
    expert_id: str
    status: ConsultationStatus
    recommendation: str
    confidence_score: float
    reasoning: str
    alternative_options: List[Dict[str, Any]] = field(default_factory=list)
    follow_up_required: bool = False
    estimated_implementation_time: Optional[int] = None
    risks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

class Expert(ABC):
    """專家抽象基類"""
    
    def __init__(self, profile: ExpertProfile):
        self.profile = profile
        self.active_consultations: Set[str] = set()
        self.consultation_history: List[str] = []
    
    @abstractmethod
    async def handle_consultation(self, request: ConsultationRequest) -> ConsultationResponse:
        """處理諮詢請求"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """檢查是否可用"""
        pass
    
    async def update_availability(self, availability: ExpertAvailability):
        """更新可用性狀態"""
        self.profile.availability = availability
        self.profile.last_active = datetime.now()
    
    def get_current_load(self) -> float:
        """獲取當前負載率"""
        return len(self.active_consultations) / self.profile.max_concurrent

class AIExpert(Expert):
    """AI專家系統"""
    
    def __init__(self, profile: ExpertProfile, ai_model_config: Dict[str, Any]):
        super().__init__(profile)
        self.ai_model_config = ai_model_config
        self.knowledge_base = {}
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """加載知識庫"""
        # 這裡可以加載預訓練的知識庫
        self.knowledge_base = {
            "best_practices": {},
            "common_issues": {},
            "solution_patterns": {},
            "risk_assessments": {}
        }
    
    async def handle_consultation(self, request: ConsultationRequest) -> ConsultationResponse:
        """處理諮詢請求"""
        self.active_consultations.add(request.request_id)
        
        try:
            # 分析請求
            analysis = await self._analyze_request(request)
            
            # 生成建議
            recommendation = await self._generate_recommendation(request, analysis)
            
            # 評估置信度
            confidence = await self._calculate_confidence(request, recommendation)
            
            response = ConsultationResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                expert_id=self.profile.expert_id,
                status=ConsultationStatus.COMPLETED,
                recommendation=recommendation["solution"],
                confidence_score=confidence,
                reasoning=recommendation["reasoning"],
                alternative_options=recommendation.get("alternatives", []),
                risks=recommendation.get("risks", []),
                dependencies=recommendation.get("dependencies", [])
            )
            
            return response
            
        finally:
            self.active_consultations.discard(request.request_id)
            self.consultation_history.append(request.request_id)
    
    async def _analyze_request(self, request: ConsultationRequest) -> Dict[str, Any]:
        """分析請求"""
        # 模擬AI分析過程
        await asyncio.sleep(0.1)  # 模擬處理時間
        
        return {
            "complexity": self._assess_complexity(request),
            "risk_level": self._assess_risk(request),
            "required_expertise": self._identify_required_expertise(request),
            "similar_cases": self._find_similar_cases(request)
        }
    
    async def _generate_recommendation(self, request: ConsultationRequest, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成建議"""
        # 模擬AI推理過程
        await asyncio.sleep(0.2)
        
        if request.expert_type == ExpertType.DEPLOYMENT:
            return {
                "solution": "建議使用藍綠部署策略，先在測試環境驗證，然後逐步切換流量",
                "reasoning": "基於當前系統架構和風險評估，藍綠部署可以最小化停機時間和風險",
                "alternatives": [
                    {"name": "滾動更新", "pros": ["零停機"], "cons": ["回滾複雜"]},
                    {"name": "金絲雀發布", "pros": ["風險可控"], "cons": ["部署時間長"]}
                ],
                "risks": ["數據庫遷移風險", "配置不一致風險"],
                "dependencies": ["數據庫備份", "監控系統", "回滾腳本"]
            }
        elif request.expert_type == ExpertType.SECURITY:
            return {
                "solution": "建議實施多層安全防護，包括網路隔離、身份驗證和數據加密",
                "reasoning": "基於威脅模型分析，多層防護可以有效降低安全風險",
                "alternatives": [
                    {"name": "零信任架構", "pros": ["最高安全性"], "cons": ["實施複雜"]},
                    {"name": "傳統防火牆", "pros": ["簡單易用"], "cons": ["防護有限"]}
                ],
                "risks": ["配置錯誤風險", "性能影響"],
                "dependencies": ["PKI基礎設施", "身份管理系統"]
            }
        else:
            return {
                "solution": f"針對{request.expert_type.value}領域的專業建議",
                "reasoning": "基於最佳實踐和經驗分析",
                "alternatives": [],
                "risks": [],
                "dependencies": []
            }
    
    async def _calculate_confidence(self, request: ConsultationRequest, recommendation: Dict[str, Any]) -> float:
        """計算置信度"""
        base_confidence = 0.8
        
        # 基於專家專業領域匹配度調整
        if request.expert_type in [ExpertType.TECHNICAL, ExpertType.DEPLOYMENT]:
            base_confidence += 0.1
        
        # 基於請求複雜度調整
        complexity = self._assess_complexity(request)
        if complexity < 0.5:
            base_confidence += 0.1
        elif complexity > 0.8:
            base_confidence -= 0.2
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _assess_complexity(self, request: ConsultationRequest) -> float:
        """評估複雜度"""
        complexity = 0.5  # 基礎複雜度
        
        # 基於描述長度
        if len(request.description) > 500:
            complexity += 0.2
        
        # 基於上下文複雜度
        if len(request.context) > 5:
            complexity += 0.1
        
        # 基於所需專業技能數量
        if len(request.required_specializations) > 3:
            complexity += 0.2
        
        return min(complexity, 1.0)
    
    def _assess_risk(self, request: ConsultationRequest) -> float:
        """評估風險"""
        risk = 0.3  # 基礎風險
        
        # 基於優先級
        if request.priority >= 4:
            risk += 0.3
        
        # 基於上下文中的風險指標
        risk_keywords = ["production", "critical", "database", "security"]
        for keyword in risk_keywords:
            if keyword in request.description.lower():
                risk += 0.1
        
        return min(risk, 1.0)
    
    def _identify_required_expertise(self, request: ConsultationRequest) -> List[str]:
        """識別所需專業技能"""
        expertise = [request.expert_type.value]
        
        # 基於描述內容識別額外技能
        skill_keywords = {
            "kubernetes": "container_orchestration",
            "docker": "containerization",
            "aws": "cloud_aws",
            "database": "database_management",
            "security": "cybersecurity"
        }
        
        for keyword, skill in skill_keywords.items():
            if keyword in request.description.lower():
                expertise.append(skill)
        
        return list(set(expertise))
    
    def _find_similar_cases(self, request: ConsultationRequest) -> List[str]:
        """查找相似案例"""
        # 模擬查找相似案例
        return [f"case_{i}" for i in range(3)]
    
    async def is_available(self) -> bool:
        """檢查是否可用"""
        return (self.profile.availability == ExpertAvailability.AVAILABLE and 
                len(self.active_consultations) < self.profile.max_concurrent)

class HumanExpert(Expert):
    """人工專家"""
    
    def __init__(self, profile: ExpertProfile, human_loop_client):
        super().__init__(profile)
        self.human_loop_client = human_loop_client
        self.pending_sessions: Dict[str, str] = {}  # request_id -> session_id
    
    async def handle_consultation(self, request: ConsultationRequest) -> ConsultationResponse:
        """處理諮詢請求"""
        self.active_consultations.add(request.request_id)
        
        try:
            # 創建人工交互會話
            session_id = await self._create_consultation_session(request)
            self.pending_sessions[request.request_id] = session_id
            
            # 等待人工響應
            response = await self._wait_for_human_response(request, session_id)
            
            return response
            
        finally:
            self.active_consultations.discard(request.request_id)
            self.pending_sessions.pop(request.request_id, None)
            self.consultation_history.append(request.request_id)
    
    async def _create_consultation_session(self, request: ConsultationRequest) -> str:
        """創建諮詢會話"""
        session_data = {
            "interaction_data": {
                "interaction_type": "expert_review",
                "title": f"專家諮詢: {request.title}",
                "message": request.description,
                "context": request.context,
                "expert_type": request.expert_type.value,
                "required_level": request.required_level.value,
                "priority": request.priority,
                "attachments": request.attachments,
                "timeout": request.timeout,
                "fields": [
                    {
                        "name": "recommendation",
                        "type": "textarea",
                        "label": "建議方案",
                        "required": True,
                        "placeholder": "請提供詳細的建議方案..."
                    },
                    {
                        "name": "confidence",
                        "type": "range",
                        "label": "置信度",
                        "min": 0,
                        "max": 100,
                        "default": 80
                    },
                    {
                        "name": "reasoning",
                        "type": "textarea",
                        "label": "推理過程",
                        "required": True,
                        "placeholder": "請說明推理過程和依據..."
                    },
                    {
                        "name": "risks",
                        "type": "text",
                        "label": "風險評估",
                        "placeholder": "請列出主要風險點（用逗號分隔）"
                    },
                    {
                        "name": "alternatives",
                        "type": "textarea",
                        "label": "替代方案",
                        "placeholder": "如有替代方案，請詳細說明..."
                    },
                    {
                        "name": "follow_up",
                        "type": "checkbox",
                        "label": "需要後續跟進",
                        "default": False
                    }
                ]
            },
            "workflow_id": request.workflow_id,
            "expert_id": self.profile.expert_id,
            "callback_url": request.callback_url
        }
        
        return await self.human_loop_client.create_session(session_data)
    
    async def _wait_for_human_response(self, request: ConsultationRequest, session_id: str) -> ConsultationResponse:
        """等待人工響應"""
        start_time = time.time()
        timeout = request.timeout
        
        while time.time() - start_time < timeout:
            try:
                session_status = await self.human_loop_client.get_session_status(session_id)
                
                if session_status["session"]["status"] == "completed":
                    # 解析人工響應
                    user_response = session_status["session"].get("response", {})
                    
                    return ConsultationResponse(
                        response_id=str(uuid.uuid4()),
                        request_id=request.request_id,
                        expert_id=self.profile.expert_id,
                        status=ConsultationStatus.COMPLETED,
                        recommendation=user_response.get("recommendation", ""),
                        confidence_score=float(user_response.get("confidence", 80)) / 100.0,
                        reasoning=user_response.get("reasoning", ""),
                        risks=user_response.get("risks", "").split(",") if user_response.get("risks") else [],
                        follow_up_required=user_response.get("follow_up", False),
                        alternative_options=self._parse_alternatives(user_response.get("alternatives", "")),
                        completed_at=datetime.now()
                    )
                
                elif session_status["session"]["status"] == "cancelled":
                    return ConsultationResponse(
                        response_id=str(uuid.uuid4()),
                        request_id=request.request_id,
                        expert_id=self.profile.expert_id,
                        status=ConsultationStatus.CANCELLED,
                        recommendation="諮詢已取消",
                        confidence_score=0.0,
                        reasoning="用戶取消了諮詢請求"
                    )
                
                # 等待一段時間後再檢查
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error checking session status: {e}")
                await asyncio.sleep(10)
        
        # 超時處理
        await self.human_loop_client.cancel_session(session_id, "Consultation timeout")
        
        return ConsultationResponse(
            response_id=str(uuid.uuid4()),
            request_id=request.request_id,
            expert_id=self.profile.expert_id,
            status=ConsultationStatus.TIMEOUT,
            recommendation="諮詢超時",
            confidence_score=0.0,
            reasoning="專家響應超時"
        )
    
    def _parse_alternatives(self, alternatives_text: str) -> List[Dict[str, Any]]:
        """解析替代方案文本"""
        if not alternatives_text.strip():
            return []
        
        # 簡單解析，實際可以更複雜
        alternatives = []
        for line in alternatives_text.split('\n'):
            if line.strip():
                alternatives.append({
                    "description": line.strip(),
                    "pros": [],
                    "cons": []
                })
        
        return alternatives
    
    async def is_available(self) -> bool:
        """檢查是否可用"""
        return (self.profile.availability in [ExpertAvailability.AVAILABLE, ExpertAvailability.ON_CALL] and 
                len(self.active_consultations) < self.profile.max_concurrent)

class ExpertInvocationSystem:
    """專家調用系統"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.experts: Dict[str, Expert] = {}
        self.expert_registry: Dict[ExpertType, List[str]] = {}
        self.active_consultations: Dict[str, ConsultationRequest] = {}
        self.consultation_history: List[ConsultationResponse] = []
        self.config = self._load_config(config_path)
        self.human_loop_client = None
        self._initialize_system()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加載配置"""
        default_config = {
            "human_loop_mcp": {
                "url": "http://localhost:8096",
                "timeout": 30
            },
            "expert_selection": {
                "prefer_ai": True,
                "escalation_threshold": 0.7,
                "load_balancing": True
            },
            "consultation": {
                "default_timeout": 1800,
                "max_retries": 2,
                "auto_escalate": True
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def _initialize_system(self):
        """初始化系統"""
        # 初始化Human Loop MCP客戶端
        from aicore_dynamic_router import HumanLoopMCPClient
        self.human_loop_client = HumanLoopMCPClient(
            base_url=self.config["human_loop_mcp"]["url"],
            timeout=self.config["human_loop_mcp"]["timeout"]
        )
        
        # 註冊默認專家
        self._register_default_experts()
    
    def _register_default_experts(self):
        """註冊默認專家"""
        # AI專家
        ai_experts = [
            (ExpertType.TECHNICAL, "AI技術專家", ["python", "javascript", "system_design"]),
            (ExpertType.DEPLOYMENT, "AI部署專家", ["kubernetes", "docker", "ci_cd"]),
            (ExpertType.SECURITY, "AI安全專家", ["cybersecurity", "encryption", "compliance"]),
            (ExpertType.PERFORMANCE, "AI性能專家", ["optimization", "monitoring", "scaling"]),
            (ExpertType.DATA, "AI數據專家", ["database", "analytics", "etl"])
        ]
        
        for expert_type, name, specializations in ai_experts:
            profile = ExpertProfile(
                expert_id=f"ai_{expert_type.value}_{uuid.uuid4().hex[:8]}",
                name=name,
                expert_type=expert_type,
                level=ExpertLevel.SENIOR,
                specializations=specializations,
                max_concurrent=10,
                average_response_time=30.0,
                success_rate=0.9
            )
            
            ai_expert = AIExpert(profile, {"model": "gpt-4", "temperature": 0.3})
            self.register_expert(ai_expert)
        
        # 人工專家（示例）
        human_experts = [
            (ExpertType.TECHNICAL, "資深技術架構師", ExpertLevel.ARCHITECT, ["microservices", "distributed_systems"]),
            (ExpertType.SECURITY, "安全專家", ExpertLevel.PRINCIPAL, ["penetration_testing", "security_audit"]),
            (ExpertType.BUSINESS, "業務分析師", ExpertLevel.SENIOR, ["requirements_analysis", "process_optimization"])
        ]
        
        for expert_type, name, level, specializations in human_experts:
            profile = ExpertProfile(
                expert_id=f"human_{expert_type.value}_{uuid.uuid4().hex[:8]}",
                name=name,
                expert_type=expert_type,
                level=level,
                specializations=specializations,
                max_concurrent=3,
                average_response_time=1200.0,
                success_rate=0.95,
                contact_info={"email": f"{name.lower().replace(' ', '.')}@company.com"}
            )
            
            human_expert = HumanExpert(profile, self.human_loop_client)
            self.register_expert(human_expert)
    
    def register_expert(self, expert: Expert):
        """註冊專家"""
        self.experts[expert.profile.expert_id] = expert
        
        expert_type = expert.profile.expert_type
        if expert_type not in self.expert_registry:
            self.expert_registry[expert_type] = []
        
        self.expert_registry[expert_type].append(expert.profile.expert_id)
        
        logger.info(f"Registered expert: {expert.profile.name} ({expert.profile.expert_type.value})")
    
    async def request_consultation(self, request: ConsultationRequest) -> str:
        """請求專家諮詢"""
        logger.info(f"Received consultation request: {request.request_id}")
        
        # 選擇最適合的專家
        expert = await self._select_expert(request)
        
        if not expert:
            raise Exception(f"No available expert found for {request.expert_type.value}")
        
        # 記錄活躍諮詢
        self.active_consultations[request.request_id] = request
        
        # 異步處理諮詢
        asyncio.create_task(self._handle_consultation_async(expert, request))
        
        return request.request_id
    
    async def _select_expert(self, request: ConsultationRequest) -> Optional[Expert]:
        """選擇專家"""
        candidates = self.expert_registry.get(request.expert_type, [])
        
        if not candidates:
            return None
        
        # 過濾可用專家
        available_experts = []
        for expert_id in candidates:
            expert = self.experts[expert_id]
            if (await expert.is_available() and 
                expert.profile.level.value >= request.required_level.value):
                available_experts.append(expert)
        
        if not available_experts:
            return None
        
        # 選擇策略
        if self.config["expert_selection"]["prefer_ai"]:
            # 優先選擇AI專家
            ai_experts = [e for e in available_experts if isinstance(e, AIExpert)]
            if ai_experts:
                return self._select_best_expert(ai_experts, request)
        
        # 選擇最佳專家
        return self._select_best_expert(available_experts, request)
    
    def _select_best_expert(self, experts: List[Expert], request: ConsultationRequest) -> Expert:
        """選擇最佳專家"""
        # 計算專家匹配分數
        scored_experts = []
        
        for expert in experts:
            score = self._calculate_expert_score(expert, request)
            scored_experts.append((expert, score))
        
        # 按分數排序
        scored_experts.sort(key=lambda x: x[1], reverse=True)
        
        return scored_experts[0][0]
    
    def _calculate_expert_score(self, expert: Expert, request: ConsultationRequest) -> float:
        """計算專家匹配分數"""
        score = 0.0
        
        # 專業技能匹配
        matching_skills = set(expert.profile.specializations) & set(request.required_specializations)
        skill_score = len(matching_skills) / max(len(request.required_specializations), 1)
        score += skill_score * 0.4
        
        # 專家級別
        level_score = expert.profile.level.value / 5.0
        score += level_score * 0.2
        
        # 成功率
        score += expert.profile.success_rate * 0.2
        
        # 當前負載（負載越低分數越高）
        load_score = 1.0 - expert.get_current_load()
        score += load_score * 0.1
        
        # 響應時間（響應越快分數越高）
        time_score = 1.0 - min(expert.profile.average_response_time / 3600.0, 1.0)
        score += time_score * 0.1
        
        return score
    
    async def _handle_consultation_async(self, expert: Expert, request: ConsultationRequest):
        """異步處理諮詢"""
        try:
            response = await expert.handle_consultation(request)
            
            # 記錄響應
            self.consultation_history.append(response)
            
            # 發送回調（如果有）
            if request.callback_url:
                await self._send_callback(request.callback_url, response)
            
            logger.info(f"Consultation completed: {request.request_id}")
            
        except Exception as e:
            logger.error(f"Error handling consultation {request.request_id}: {e}")
            
            # 創建錯誤響應
            error_response = ConsultationResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                expert_id=expert.profile.expert_id,
                status=ConsultationStatus.CANCELLED,
                recommendation="諮詢處理失敗",
                confidence_score=0.0,
                reasoning=f"系統錯誤: {str(e)}"
            )
            
            self.consultation_history.append(error_response)
            
            if request.callback_url:
                await self._send_callback(request.callback_url, error_response)
        
        finally:
            # 清理活躍諮詢
            self.active_consultations.pop(request.request_id, None)
    
    async def _send_callback(self, callback_url: str, response: ConsultationResponse):
        """發送回調"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    callback_url,
                    json=asdict(response),
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        logger.info(f"Callback sent successfully to {callback_url}")
                    else:
                        logger.warning(f"Callback failed with status {resp.status}")
        except Exception as e:
            logger.error(f"Error sending callback to {callback_url}: {e}")
    
    async def get_consultation_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """獲取諮詢狀態"""
        # 檢查活躍諮詢
        if request_id in self.active_consultations:
            return {
                "status": "in_progress",
                "request": asdict(self.active_consultations[request_id])
            }
        
        # 檢查歷史記錄
        for response in self.consultation_history:
            if response.request_id == request_id:
                return {
                    "status": "completed",
                    "response": asdict(response)
                }
        
        return None
    
    async def get_expert_statistics(self) -> Dict[str, Any]:
        """獲取專家統計信息"""
        stats = {
            "total_experts": len(self.experts),
            "expert_types": {},
            "active_consultations": len(self.active_consultations),
            "completed_consultations": len(self.consultation_history),
            "average_response_time": 0.0,
            "success_rate": 0.0
        }
        
        # 按類型統計專家
        for expert in self.experts.values():
            expert_type = expert.profile.expert_type.value
            if expert_type not in stats["expert_types"]:
                stats["expert_types"][expert_type] = {
                    "count": 0,
                    "available": 0,
                    "ai_experts": 0,
                    "human_experts": 0
                }
            
            stats["expert_types"][expert_type]["count"] += 1
            
            if await expert.is_available():
                stats["expert_types"][expert_type]["available"] += 1
            
            if isinstance(expert, AIExpert):
                stats["expert_types"][expert_type]["ai_experts"] += 1
            else:
                stats["expert_types"][expert_type]["human_experts"] += 1
        
        # 計算平均響應時間和成功率
        if self.consultation_history:
            total_time = sum(r.completed_at.timestamp() - r.created_at.timestamp() 
                           for r in self.consultation_history if r.completed_at)
            stats["average_response_time"] = total_time / len(self.consultation_history)
            
            successful = sum(1 for r in self.consultation_history 
                           if r.status == ConsultationStatus.COMPLETED)
            stats["success_rate"] = successful / len(self.consultation_history)
        
        return stats

# 使用示例
async def example_usage():
    """使用示例"""
    # 創建專家調用系統
    expert_system = ExpertInvocationSystem()
    
    # 創建諮詢請求
    request = ConsultationRequest(
        request_id=str(uuid.uuid4()),
        workflow_id="deployment-workflow-123",
        expert_type=ExpertType.DEPLOYMENT,
        required_level=ExpertLevel.SENIOR,
        title="生產環境部署策略諮詢",
        description="需要為新版本應用選擇最佳的部署策略，考慮到系統的高可用性要求和零停機時間目標。",
        context={
            "application": "web-service",
            "environment": "production",
            "current_architecture": "microservices",
            "traffic": "high",
            "database": "postgresql"
        },
        priority=4,
        required_specializations=["kubernetes", "ci_cd", "monitoring"],
        callback_url="http://localhost:8080/consultation/callback"
    )
    
    # 請求諮詢
    consultation_id = await expert_system.request_consultation(request)
    print(f"Consultation requested: {consultation_id}")
    
    # 等待一段時間
    await asyncio.sleep(2)
    
    # 檢查狀態
    status = await expert_system.get_consultation_status(consultation_id)
    print(f"Consultation status: {json.dumps(status, indent=2, default=str)}")
    
    # 獲取統計信息
    stats = await expert_system.get_expert_statistics()
    print(f"Expert statistics: {json.dumps(stats, indent=2, default=str)}")

if __name__ == "__main__":
    asyncio.run(example_usage())

