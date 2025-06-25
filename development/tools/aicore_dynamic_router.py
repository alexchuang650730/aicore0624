#!/usr/bin/env python3
"""
AICore Dynamic Routing System with Human-in-the-Loop Integration

這個系統設計用於智能地決定何時需要人工介入，並將請求路由到適當的處理組件。
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
import uuid
import aiohttp
import yaml

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DecisionType(Enum):
    """決策類型枚舉"""
    AUTOMATIC = "automatic"
    HUMAN_REQUIRED = "human_required"
    EXPERT_CONSULTATION = "expert_consultation"
    CONDITIONAL = "conditional"

class Priority(Enum):
    """優先級枚舉"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class InteractionType(Enum):
    """交互類型枚舉"""
    CONFIRMATION = "confirmation"
    CHOICE = "choice"
    INPUT = "input"
    UPLOAD = "upload"
    EXPERT_REVIEW = "expert_review"

@dataclass
class RoutingContext:
    """路由上下文"""
    request_id: str
    workflow_id: str
    operation_type: str
    user_id: Optional[str] = None
    session_data: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.session_data is None:
            self.session_data = {}
        if self.metadata is None:
            self.metadata = {}

@dataclass
class RoutingDecision:
    """路由決策結果"""
    decision_type: DecisionType
    target_component: str
    priority: Priority
    estimated_duration: Optional[int] = None  # 預估處理時間（秒）
    required_expertise: Optional[List[str]] = None
    interaction_config: Optional[Dict[str, Any]] = None
    fallback_strategy: Optional[str] = None
    confidence_score: float = 0.0
    reasoning: str = ""

class RoutingRule(ABC):
    """路由規則抽象基類"""
    
    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority
    
    @abstractmethod
    async def evaluate(self, context: RoutingContext) -> Optional[RoutingDecision]:
        """評估路由規則"""
        pass
    
    @abstractmethod
    def get_confidence(self, context: RoutingContext) -> float:
        """獲取規則置信度"""
        pass

class ComplexityBasedRule(RoutingRule):
    """基於複雜度的路由規則"""
    
    def __init__(self):
        super().__init__("complexity_based", priority=10)
        self.complexity_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8
        }
    
    async def evaluate(self, context: RoutingContext) -> Optional[RoutingDecision]:
        complexity_score = self._calculate_complexity(context)
        
        if complexity_score < self.complexity_thresholds["low"]:
            return RoutingDecision(
                decision_type=DecisionType.AUTOMATIC,
                target_component="auto_processor",
                priority=Priority.LOW,
                confidence_score=0.9,
                reasoning=f"Low complexity score: {complexity_score}"
            )
        elif complexity_score < self.complexity_thresholds["medium"]:
            return RoutingDecision(
                decision_type=DecisionType.CONDITIONAL,
                target_component="conditional_processor",
                priority=Priority.MEDIUM,
                confidence_score=0.7,
                reasoning=f"Medium complexity score: {complexity_score}"
            )
        else:
            return RoutingDecision(
                decision_type=DecisionType.HUMAN_REQUIRED,
                target_component="human_loop_mcp",
                priority=Priority.HIGH,
                interaction_config={
                    "interaction_type": "expert_review",
                    "title": "複雜操作需要人工審核",
                    "message": f"此操作複雜度較高 ({complexity_score:.2f})，需要人工確認",
                    "timeout": 600
                },
                confidence_score=0.8,
                reasoning=f"High complexity score: {complexity_score}"
            )
    
    def _calculate_complexity(self, context: RoutingContext) -> float:
        """計算操作複雜度"""
        complexity = 0.0
        
        # 基於操作類型的複雜度
        operation_complexity = {
            "deployment": 0.7,
            "configuration_change": 0.5,
            "data_migration": 0.8,
            "security_update": 0.9,
            "routine_maintenance": 0.2
        }
        
        complexity += operation_complexity.get(context.operation_type, 0.5)
        
        # 基於元數據的複雜度調整
        if context.metadata:
            if context.metadata.get("production_environment"):
                complexity += 0.2
            if context.metadata.get("critical_system"):
                complexity += 0.3
            if context.metadata.get("multiple_dependencies"):
                complexity += 0.1
        
        return min(complexity, 1.0)
    
    def get_confidence(self, context: RoutingContext) -> float:
        return 0.8

class RiskBasedRule(RoutingRule):
    """基於風險的路由規則"""
    
    def __init__(self):
        super().__init__("risk_based", priority=20)
        self.risk_factors = {
            "production_deployment": 0.8,
            "database_changes": 0.7,
            "security_modifications": 0.9,
            "user_data_access": 0.6,
            "system_configuration": 0.5
        }
    
    async def evaluate(self, context: RoutingContext) -> Optional[RoutingDecision]:
        risk_score = self._calculate_risk(context)
        
        if risk_score > 0.7:
            return RoutingDecision(
                decision_type=DecisionType.HUMAN_REQUIRED,
                target_component="human_loop_mcp",
                priority=Priority.CRITICAL,
                interaction_config={
                    "interaction_type": "confirmation",
                    "title": "高風險操作確認",
                    "message": f"此操作風險較高 ({risk_score:.2f})，請仔細確認",
                    "options": [
                        {"value": "proceed", "label": "繼續執行"},
                        {"value": "review", "label": "需要專家審核"},
                        {"value": "cancel", "label": "取消操作"}
                    ],
                    "timeout": 300
                },
                confidence_score=0.9,
                reasoning=f"High risk score: {risk_score}"
            )
        
        return None
    
    def _calculate_risk(self, context: RoutingContext) -> float:
        """計算操作風險"""
        risk = 0.0
        
        # 檢查各種風險因素
        for factor, weight in self.risk_factors.items():
            if context.metadata and context.metadata.get(factor):
                risk += weight
        
        # 基於操作類型的風險
        if "delete" in context.operation_type.lower():
            risk += 0.5
        if "production" in str(context.metadata):
            risk += 0.3
        
        return min(risk, 1.0)
    
    def get_confidence(self, context: RoutingContext) -> float:
        return 0.9

class UserExperienceRule(RoutingRule):
    """基於用戶體驗的路由規則"""
    
    def __init__(self):
        super().__init__("user_experience", priority=5)
        self.user_preferences = {}  # 可以從數據庫加載用戶偏好
    
    async def evaluate(self, context: RoutingContext) -> Optional[RoutingDecision]:
        if not context.user_id:
            return None
        
        user_pref = self.user_preferences.get(context.user_id, {})
        
        # 如果用戶偏好自動化
        if user_pref.get("automation_preference") == "high":
            return RoutingDecision(
                decision_type=DecisionType.AUTOMATIC,
                target_component="auto_processor",
                priority=Priority.MEDIUM,
                confidence_score=0.6,
                reasoning="User prefers high automation"
            )
        
        # 如果用戶偏好人工控制
        if user_pref.get("automation_preference") == "low":
            return RoutingDecision(
                decision_type=DecisionType.HUMAN_REQUIRED,
                target_component="human_loop_mcp",
                priority=Priority.MEDIUM,
                interaction_config={
                    "interaction_type": "confirmation",
                    "title": "操作確認",
                    "message": "根據您的偏好設置，需要您確認此操作",
                    "timeout": 180
                },
                confidence_score=0.7,
                reasoning="User prefers manual control"
            )
        
        return None
    
    def get_confidence(self, context: RoutingContext) -> float:
        return 0.6 if context.user_id else 0.0

class AICoreDynamicRouter:
    """AICore動態路由器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.rules: List[RoutingRule] = []
        self.human_loop_client = None
        self.expert_system = None
        self.config = self._load_config(config_path)
        self._initialize_components()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加載配置"""
        default_config = {
            "human_loop_mcp": {
                "url": "http://localhost:8096",
                "timeout": 30
            },
            "routing": {
                "default_timeout": 300,
                "max_retries": 3,
                "fallback_to_human": True
            },
            "logging": {
                "level": "INFO",
                "file": "aicore_router.log"
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
    
    def _initialize_components(self):
        """初始化組件"""
        # 添加默認路由規則
        self.add_rule(RiskBasedRule())
        self.add_rule(ComplexityBasedRule())
        self.add_rule(UserExperienceRule())
        
        # 初始化Human Loop MCP客戶端
        self.human_loop_client = HumanLoopMCPClient(
            base_url=self.config["human_loop_mcp"]["url"],
            timeout=self.config["human_loop_mcp"]["timeout"]
        )
    
    def add_rule(self, rule: RoutingRule):
        """添加路由規則"""
        self.rules.append(rule)
        # 按優先級排序
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    async def route_request(self, context: RoutingContext) -> RoutingDecision:
        """路由請求"""
        logger.info(f"Routing request {context.request_id} for operation {context.operation_type}")
        
        # 評估所有規則
        decisions = []
        for rule in self.rules:
            try:
                decision = await rule.evaluate(context)
                if decision:
                    decision.confidence_score *= rule.get_confidence(context)
                    decisions.append((rule, decision))
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")
        
        # 選擇最佳決策
        if not decisions:
            return self._get_default_decision(context)
        
        # 按置信度和優先級排序
        decisions.sort(key=lambda x: (x[1].confidence_score, x[0].priority), reverse=True)
        best_rule, best_decision = decisions[0]
        
        logger.info(f"Selected decision from rule {best_rule.name}: {best_decision.decision_type}")
        
        # 如果需要人工介入，創建會話
        if best_decision.decision_type == DecisionType.HUMAN_REQUIRED:
            session_id = await self._create_human_session(context, best_decision)
            best_decision.metadata = {"session_id": session_id}
        
        return best_decision
    
    def _get_default_decision(self, context: RoutingContext) -> RoutingDecision:
        """獲取默認決策"""
        return RoutingDecision(
            decision_type=DecisionType.HUMAN_REQUIRED if self.config["routing"]["fallback_to_human"] else DecisionType.AUTOMATIC,
            target_component="human_loop_mcp" if self.config["routing"]["fallback_to_human"] else "auto_processor",
            priority=Priority.MEDIUM,
            confidence_score=0.5,
            reasoning="No specific rule matched, using default strategy"
        )
    
    async def _create_human_session(self, context: RoutingContext, decision: RoutingDecision) -> str:
        """創建人工交互會話"""
        if not decision.interaction_config:
            decision.interaction_config = {
                "interaction_type": "confirmation",
                "title": "操作確認",
                "message": "需要您確認此操作",
                "timeout": self.config["routing"]["default_timeout"]
            }
        
        session_data = {
            "interaction_data": decision.interaction_config,
            "workflow_id": context.workflow_id,
            "callback_url": f"http://localhost:8080/callback/{context.request_id}"
        }
        
        try:
            session_id = await self.human_loop_client.create_session(session_data)
            logger.info(f"Created human interaction session: {session_id}")
            return session_id
        except Exception as e:
            logger.error(f"Failed to create human session: {e}")
            raise
    
    async def get_routing_statistics(self) -> Dict[str, Any]:
        """獲取路由統計信息"""
        # 這裡可以實現統計邏輯
        return {
            "total_requests": 0,
            "automatic_decisions": 0,
            "human_interventions": 0,
            "expert_consultations": 0,
            "average_response_time": 0.0
        }

class HumanLoopMCPClient:
    """Human Loop MCP客戶端"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_session(self, session_data: Dict[str, Any]) -> str:
        """創建交互會話"""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        
        async with self.session.post(f"{self.base_url}/api/sessions", json=session_data) as response:
            if response.status == 200:
                result = await response.json()
                return result["session_id"]
            else:
                raise Exception(f"Failed to create session: {response.status}")
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """獲取會話狀態"""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        
        async with self.session.get(f"{self.base_url}/api/sessions/{session_id}") as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to get session status: {response.status}")
    
    async def cancel_session(self, session_id: str, reason: str = "Cancelled by system") -> bool:
        """取消會話"""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        
        async with self.session.post(
            f"{self.base_url}/api/sessions/{session_id}/cancel",
            json={"reason": reason}
        ) as response:
            return response.status == 200

# 使用示例
async def example_usage():
    """使用示例"""
    # 創建路由器
    router = AICoreDynamicRouter()
    
    # 創建路由上下文
    context = RoutingContext(
        request_id=str(uuid.uuid4()),
        workflow_id="deployment-workflow-123",
        operation_type="deployment",
        user_id="user-123",
        metadata={
            "production_environment": True,
            "critical_system": True,
            "target": "production-server"
        }
    )
    
    # 執行路由決策
    decision = await router.route_request(context)
    
    print(f"Routing Decision:")
    print(f"  Type: {decision.decision_type}")
    print(f"  Target: {decision.target_component}")
    print(f"  Priority: {decision.priority}")
    print(f"  Confidence: {decision.confidence_score}")
    print(f"  Reasoning: {decision.reasoning}")
    
    if decision.interaction_config:
        print(f"  Interaction Config: {json.dumps(decision.interaction_config, indent=2)}")

if __name__ == "__main__":
    asyncio.run(example_usage())

