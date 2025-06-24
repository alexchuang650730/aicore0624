"""
動態專家註冊機制
基於Cloud Search結果動態創建和管理專家
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)

class ExpertStatus(Enum):
    """專家狀態"""
    PENDING = "pending"           # 待驗證
    ACTIVE = "active"            # 活躍
    INACTIVE = "inactive"        # 非活躍
    DEPRECATED = "deprecated"    # 已棄用
    FAILED = "failed"           # 驗證失敗

class ExpertType(Enum):
    """專家類型"""
    BASE_EXPERT = "base"         # 基礎專家（固定7種）
    DYNAMIC_EXPERT = "dynamic"   # 動態專家（搜索發現）
    HYBRID_EXPERT = "hybrid"     # 混合專家（基礎+動態）

@dataclass
class ExpertCapability:
    """專家能力定義"""
    name: str                    # 能力名稱
    description: str             # 能力描述
    skill_level: str            # 技能等級 (basic/intermediate/advanced/expert)
    domain: str                 # 專業領域
    keywords: List[str]         # 關鍵詞
    confidence: float           # 能力信心度
    source: str                 # 能力來源 (search/manual/learned)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ExpertProfile:
    """專家檔案"""
    id: str                     # 專家ID
    name: str                   # 專家名稱
    type: ExpertType           # 專家類型
    status: ExpertStatus       # 專家狀態
    capabilities: List[ExpertCapability]  # 能力列表
    specializations: List[str]  # 專業領域
    knowledge_base: Dict[str, Any]  # 知識庫
    performance_metrics: Dict[str, float]  # 性能指標
    usage_history: List[Dict]   # 使用歷史
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExpertRegistrationRequest:
    """專家註冊請求"""
    domain: str                 # 專業領域
    scenario_type: str         # 場景類型
    skill_requirements: List[str]  # 技能要求
    knowledge_sources: List[Dict]  # 知識來源
    priority: int              # 優先級
    context: Dict[str, Any]    # 上下文信息
    requester: str             # 請求者
    expires_at: Optional[datetime] = None

class DynamicExpertRegistry:
    """動態專家註冊中心"""
    
    def __init__(self):
        self.experts: Dict[str, ExpertProfile] = {}
        self.expert_index: Dict[str, Set[str]] = {}  # 領域索引
        self.capability_index: Dict[str, Set[str]] = {}  # 能力索引
        self.performance_tracker = ExpertPerformanceTracker()
        self.knowledge_synthesizer = ExpertKnowledgeSynthesizer()
        self.base_experts_initialized = False
        
        logger.info("✅ 動態專家註冊中心初始化完成")
    
    async def initialize(self):
        """異步初始化基礎專家"""
        if not self.base_experts_initialized:
            await self._initialize_base_experts()
            self.base_experts_initialized = True
    
    async def register_dynamic_expert(self, registration_request: ExpertRegistrationRequest) -> ExpertProfile:
        """註冊動態專家"""
        logger.info(f"🔧 註冊動態專家: {registration_request.domain}")
        
        try:
            # 1. 生成專家ID
            expert_id = self._generate_expert_id(registration_request)
            
            # 2. 檢查是否已存在類似專家
            existing_expert = await self._find_similar_expert(registration_request)
            if existing_expert:
                logger.info(f"發現類似專家，更新現有專家: {existing_expert.id}")
                return await self._update_existing_expert(existing_expert, registration_request)
            
            # 3. 合成專家知識庫
            knowledge_base = await self.knowledge_synthesizer.synthesize_knowledge(
                registration_request.knowledge_sources,
                registration_request.domain
            )
            
            # 4. 生成專家能力
            capabilities = await self._generate_expert_capabilities(
                registration_request, knowledge_base
            )
            
            # 5. 創建專家檔案
            expert_profile = ExpertProfile(
                id=expert_id,
                name=self._generate_expert_name(registration_request),
                type=ExpertType.DYNAMIC_EXPERT,
                status=ExpertStatus.PENDING,
                capabilities=capabilities,
                specializations=[registration_request.domain],
                knowledge_base=knowledge_base,
                performance_metrics=self._initialize_performance_metrics(),
                usage_history=[],
                metadata={
                    "registration_request": asdict(registration_request),
                    "creation_method": "dynamic_search_based",
                    "version": "1.0"
                }
            )
            
            # 6. 驗證專家能力
            validation_result = await self._validate_expert_capabilities(expert_profile)
            if validation_result["valid"]:
                expert_profile.status = ExpertStatus.ACTIVE
                logger.info(f"✅ 專家驗證成功: {expert_id}")
            else:
                expert_profile.status = ExpertStatus.FAILED
                logger.warning(f"❌ 專家驗證失敗: {expert_id}, 原因: {validation_result['reason']}")
            
            # 7. 註冊到系統
            await self._register_expert_to_system(expert_profile)
            
            # 8. 更新索引
            await self._update_expert_indices(expert_profile)
            
            logger.info(f"🎉 動態專家註冊完成: {expert_profile.name} ({expert_id})")
            return expert_profile
            
        except Exception as e:
            logger.error(f"❌ 動態專家註冊失敗: {e}")
            raise
    
    async def find_experts_for_scenario(self, scenario_context: Dict) -> List[ExpertProfile]:
        """為場景尋找合適的專家"""
        logger.info(f"🔍 為場景尋找專家: {scenario_context.get('type', 'unknown')}")
        
        # 1. 解析場景需求
        required_domains = scenario_context.get("domains", [])
        required_skills = scenario_context.get("skills", [])
        complexity_level = scenario_context.get("complexity", "MEDIUM")
        
        # 2. 搜索匹配的專家
        candidate_experts = []
        
        # 基於領域搜索
        for domain in required_domains:
            if domain in self.expert_index:
                for expert_id in self.expert_index[domain]:
                    if expert_id in self.experts:
                        candidate_experts.append(self.experts[expert_id])
        
        # 基於能力搜索
        for skill in required_skills:
            if skill in self.capability_index:
                for expert_id in self.capability_index[skill]:
                    if expert_id in self.experts and self.experts[expert_id] not in candidate_experts:
                        candidate_experts.append(self.experts[expert_id])
        
        # 3. 過濾和排序
        filtered_experts = await self._filter_experts_by_criteria(
            candidate_experts, scenario_context
        )
        
        # 4. 按性能和匹配度排序
        sorted_experts = await self._rank_experts_by_suitability(
            filtered_experts, scenario_context
        )
        
        # 5. 限制專家數量
        max_experts = self._determine_max_experts(complexity_level)
        selected_experts = sorted_experts[:max_experts]
        
        logger.info(f"📋 找到 {len(selected_experts)} 位合適專家")
        return selected_experts
    
    async def update_expert_performance(self, expert_id: str, performance_data: Dict):
        """更新專家性能數據"""
        if expert_id not in self.experts:
            logger.warning(f"專家不存在: {expert_id}")
            return
        
        expert = self.experts[expert_id]
        
        # 更新性能指標
        await self.performance_tracker.update_performance(expert, performance_data)
        
        # 更新使用歷史
        expert.usage_history.append({
            "timestamp": datetime.now(),
            "performance": performance_data,
            "context": performance_data.get("context", {})
        })
        
        # 更新最後使用時間
        expert.last_used = datetime.now()
        
        # 檢查是否需要更新專家狀態
        await self._evaluate_expert_status(expert)
        
        logger.info(f"📊 更新專家性能: {expert_id}")
    
    async def cleanup_inactive_experts(self):
        """清理非活躍專家"""
        logger.info("🧹 開始清理非活躍專家")
        
        current_time = datetime.now()
        inactive_threshold = timedelta(days=30)  # 30天未使用視為非活躍
        
        experts_to_remove = []
        
        for expert_id, expert in self.experts.items():
            # 跳過基礎專家
            if expert.type == ExpertType.BASE_EXPERT:
                continue
            
            # 檢查最後使用時間
            if expert.last_used and (current_time - expert.last_used) > inactive_threshold:
                # 檢查性能指標
                if expert.performance_metrics.get("success_rate", 0) < 0.5:
                    experts_to_remove.append(expert_id)
                    logger.info(f"標記移除非活躍專家: {expert.name} ({expert_id})")
        
        # 移除專家
        for expert_id in experts_to_remove:
            await self._remove_expert(expert_id)
        
        logger.info(f"🧹 清理完成，移除 {len(experts_to_remove)} 位專家")
    
    async def get_expert_statistics(self) -> Dict[str, Any]:
        """獲取專家統計信息"""
        stats = {
            "total_experts": len(self.experts),
            "by_type": {},
            "by_status": {},
            "by_domain": {},
            "performance_summary": {},
            "usage_summary": {}
        }
        
        # 按類型統計
        for expert in self.experts.values():
            expert_type = expert.type.value
            stats["by_type"][expert_type] = stats["by_type"].get(expert_type, 0) + 1
            
            expert_status = expert.status.value
            stats["by_status"][expert_status] = stats["by_status"].get(expert_status, 0) + 1
        
        # 按領域統計
        for domain, expert_ids in self.expert_index.items():
            stats["by_domain"][domain] = len(expert_ids)
        
        # 性能統計
        total_success_rate = sum(e.performance_metrics.get("success_rate", 0) for e in self.experts.values())
        stats["performance_summary"]["average_success_rate"] = total_success_rate / len(self.experts) if self.experts else 0
        
        return stats
    
    # 私有方法
    def _generate_expert_id(self, request: ExpertRegistrationRequest) -> str:
        """生成專家ID"""
        content = f"{request.domain}_{request.scenario_type}_{datetime.now().isoformat()}"
        return f"expert_{hashlib.md5(content.encode()).hexdigest()[:8]}"
    
    def _generate_expert_name(self, request: ExpertRegistrationRequest) -> str:
        """生成專家名稱"""
        domain_name = request.domain.replace("_", " ").title()
        scenario_name = request.scenario_type.replace("_", " ").title()
        return f"{domain_name} {scenario_name} Specialist"
    
    async def _find_similar_expert(self, request: ExpertRegistrationRequest) -> Optional[ExpertProfile]:
        """尋找類似的現有專家"""
        for expert in self.experts.values():
            if (expert.type == ExpertType.DYNAMIC_EXPERT and 
                request.domain in expert.specializations):
                # 檢查技能重疊度
                expert_skills = set()
                for cap in expert.capabilities:
                    expert_skills.update(cap.keywords)
                
                request_skills = set(request.skill_requirements)
                overlap = len(expert_skills.intersection(request_skills))
                
                if overlap / len(request_skills) > 0.7:  # 70%重疊度
                    return expert
        
        return None
    
    async def _update_existing_expert(self, expert: ExpertProfile, request: ExpertRegistrationRequest) -> ExpertProfile:
        """更新現有專家"""
        # 合併新的知識源
        new_knowledge = await self.knowledge_synthesizer.synthesize_knowledge(
            request.knowledge_sources, request.domain
        )
        
        # 更新知識庫
        expert.knowledge_base.update(new_knowledge)
        
        # 添加新能力
        new_capabilities = await self._generate_expert_capabilities(request, new_knowledge)
        expert.capabilities.extend(new_capabilities)
        
        # 更新元數據
        expert.metadata["last_updated"] = datetime.now()
        expert.metadata["update_count"] = expert.metadata.get("update_count", 0) + 1
        
        return expert
    
    async def _generate_expert_capabilities(self, request: ExpertRegistrationRequest, 
                                         knowledge_base: Dict) -> List[ExpertCapability]:
        """生成專家能力"""
        capabilities = []
        
        for skill in request.skill_requirements:
            capability = ExpertCapability(
                name=skill,
                description=f"Expertise in {skill} for {request.domain}",
                skill_level=self._determine_skill_level(skill, knowledge_base),
                domain=request.domain,
                keywords=self._extract_keywords_for_skill(skill, knowledge_base),
                confidence=self._calculate_capability_confidence(skill, knowledge_base),
                source="search_based"
            )
            capabilities.append(capability)
        
        return capabilities
    
    def _determine_skill_level(self, skill: str, knowledge_base: Dict) -> str:
        """確定技能等級"""
        knowledge_depth = len(knowledge_base.get("detailed_info", []))
        
        if knowledge_depth > 10:
            return "expert"
        elif knowledge_depth > 5:
            return "advanced"
        elif knowledge_depth > 2:
            return "intermediate"
        else:
            return "basic"
    
    def _extract_keywords_for_skill(self, skill: str, knowledge_base: Dict) -> List[str]:
        """為技能提取關鍵詞"""
        # 從知識庫中提取相關關鍵詞
        keywords = [skill]
        
        # 從知識庫內容中提取
        for content in knowledge_base.get("content", []):
            if isinstance(content, str) and skill.lower() in content.lower():
                # 簡單的關鍵詞提取
                words = content.lower().split()
                skill_index = words.index(skill.lower()) if skill.lower() in words else -1
                if skill_index >= 0:
                    # 提取周圍的詞作為關鍵詞
                    start = max(0, skill_index - 2)
                    end = min(len(words), skill_index + 3)
                    keywords.extend(words[start:end])
        
        return list(set(keywords))
    
    def _calculate_capability_confidence(self, skill: str, knowledge_base: Dict) -> float:
        """計算能力信心度"""
        # 基於知識庫的豐富程度計算信心度
        content_count = len(knowledge_base.get("content", []))
        detail_count = len(knowledge_base.get("detailed_info", []))
        
        confidence = min(0.95, (content_count * 0.1) + (detail_count * 0.05))
        return max(0.3, confidence)  # 最低30%信心度
    
    def _initialize_performance_metrics(self) -> Dict[str, float]:
        """初始化性能指標"""
        return {
            "success_rate": 0.8,      # 成功率
            "response_time": 1.0,     # 響應時間
            "accuracy": 0.8,          # 準確度
            "user_satisfaction": 0.8,  # 用戶滿意度
            "usage_count": 0          # 使用次數
        }
    
    async def _validate_expert_capabilities(self, expert: ExpertProfile) -> Dict[str, Any]:
        """驗證專家能力"""
        # 簡化的驗證邏輯
        validation_score = 0
        
        # 檢查能力數量
        if len(expert.capabilities) >= 2:
            validation_score += 0.3
        
        # 檢查知識庫豐富度
        if len(expert.knowledge_base.get("content", [])) >= 3:
            validation_score += 0.4
        
        # 檢查專業領域覆蓋
        if len(expert.specializations) >= 1:
            validation_score += 0.3
        
        is_valid = validation_score >= 0.7
        
        return {
            "valid": is_valid,
            "score": validation_score,
            "reason": "Insufficient capabilities" if not is_valid else "Validation passed"
        }
    
    async def _register_expert_to_system(self, expert: ExpertProfile):
        """將專家註冊到系統"""
        self.experts[expert.id] = expert
        logger.info(f"專家已註冊到系統: {expert.id}")
    
    async def _update_expert_indices(self, expert: ExpertProfile):
        """更新專家索引"""
        # 更新領域索引
        for domain in expert.specializations:
            if domain not in self.expert_index:
                self.expert_index[domain] = set()
            self.expert_index[domain].add(expert.id)
        
        # 更新能力索引
        for capability in expert.capabilities:
            cap_name = capability.name
            if cap_name not in self.capability_index:
                self.capability_index[cap_name] = set()
            self.capability_index[cap_name].add(expert.id)
    
    async def _filter_experts_by_criteria(self, experts: List[ExpertProfile], 
                                        scenario_context: Dict) -> List[ExpertProfile]:
        """根據條件過濾專家"""
        filtered = []
        
        for expert in experts:
            # 檢查專家狀態
            if expert.status != ExpertStatus.ACTIVE:
                continue
            
            # 檢查性能指標
            if expert.performance_metrics.get("success_rate", 0) < 0.6:
                continue
            
            filtered.append(expert)
        
        return filtered
    
    async def _rank_experts_by_suitability(self, experts: List[ExpertProfile], 
                                         scenario_context: Dict) -> List[ExpertProfile]:
        """按適合度排序專家"""
        def calculate_suitability_score(expert: ExpertProfile) -> float:
            score = 0
            
            # 性能權重
            score += expert.performance_metrics.get("success_rate", 0) * 0.4
            score += expert.performance_metrics.get("accuracy", 0) * 0.3
            score += expert.performance_metrics.get("user_satisfaction", 0) * 0.2
            
            # 使用頻率權重
            usage_count = expert.performance_metrics.get("usage_count", 0)
            score += min(0.1, usage_count * 0.01)  # 最多加0.1分
            
            return score
        
        return sorted(experts, key=calculate_suitability_score, reverse=True)
    
    def _determine_max_experts(self, complexity_level: str) -> int:
        """確定最大專家數量"""
        mapping = {
            "LOW": 2,
            "MEDIUM": 3,
            "HIGH": 4,
            "CRITICAL": 5
        }
        return mapping.get(complexity_level, 3)
    
    async def _evaluate_expert_status(self, expert: ExpertProfile):
        """評估專家狀態"""
        success_rate = expert.performance_metrics.get("success_rate", 0)
        usage_count = expert.performance_metrics.get("usage_count", 0)
        
        if success_rate < 0.3 and usage_count > 5:
            expert.status = ExpertStatus.DEPRECATED
        elif success_rate > 0.8 and usage_count > 10:
            expert.status = ExpertStatus.ACTIVE
    
    async def _remove_expert(self, expert_id: str):
        """移除專家"""
        if expert_id in self.experts:
            expert = self.experts[expert_id]
            
            # 從索引中移除
            for domain in expert.specializations:
                if domain in self.expert_index:
                    self.expert_index[domain].discard(expert_id)
            
            for capability in expert.capabilities:
                if capability.name in self.capability_index:
                    self.capability_index[capability.name].discard(expert_id)
            
            # 從專家列表中移除
            del self.experts[expert_id]
            
            logger.info(f"專家已移除: {expert_id}")
    
    async def _initialize_base_experts(self):
        """初始化基礎專家"""
        base_experts = [
            ("technical_expert", "Technical Expert", ["programming", "architecture", "development"]),
            ("api_expert", "API Expert", ["api_design", "rest", "integration"]),
            ("business_expert", "Business Expert", ["requirements", "analysis", "strategy"]),
            ("data_expert", "Data Expert", ["data_analysis", "database", "analytics"]),
            ("integration_expert", "Integration Expert", ["system_integration", "middleware"]),
            ("security_expert", "Security Expert", ["security", "authentication", "encryption"]),
            ("performance_expert", "Performance Expert", ["optimization", "scalability", "tuning"])
        ]
        
        for expert_id, name, skills in base_experts:
            capabilities = [
                ExpertCapability(
                    name=skill,
                    description=f"Base expertise in {skill}",
                    skill_level="advanced",
                    domain=expert_id.replace("_expert", ""),
                    keywords=[skill],
                    confidence=0.9,
                    source="base_system"
                ) for skill in skills
            ]
            
            expert = ExpertProfile(
                id=expert_id,
                name=name,
                type=ExpertType.BASE_EXPERT,
                status=ExpertStatus.ACTIVE,
                capabilities=capabilities,
                specializations=[expert_id.replace("_expert", "")],
                knowledge_base={"type": "base_expert", "content": []},
                performance_metrics=self._initialize_performance_metrics(),
                usage_history=[],
                metadata={"base_expert": True}
            )
            
            await self._register_expert_to_system(expert)
            await self._update_expert_indices(expert)

class ExpertPerformanceTracker:
    """專家性能追蹤器"""
    
    async def update_performance(self, expert: ExpertProfile, performance_data: Dict):
        """更新專家性能"""
        metrics = expert.performance_metrics
        
        # 更新成功率
        if "success" in performance_data:
            current_success_rate = metrics.get("success_rate", 0.8)
            new_success = 1.0 if performance_data["success"] else 0.0
            metrics["success_rate"] = (current_success_rate * 0.9) + (new_success * 0.1)
        
        # 更新響應時間
        if "response_time" in performance_data:
            current_time = metrics.get("response_time", 1.0)
            new_time = performance_data["response_time"]
            metrics["response_time"] = (current_time * 0.8) + (new_time * 0.2)
        
        # 更新使用次數
        metrics["usage_count"] = metrics.get("usage_count", 0) + 1
        
        # 更新用戶滿意度
        if "user_rating" in performance_data:
            current_satisfaction = metrics.get("user_satisfaction", 0.8)
            new_rating = performance_data["user_rating"] / 5.0  # 假設5分制
            metrics["user_satisfaction"] = (current_satisfaction * 0.9) + (new_rating * 0.1)

class ExpertKnowledgeSynthesizer:
    """專家知識合成器"""
    
    async def synthesize_knowledge(self, knowledge_sources: List[Dict], domain: str) -> Dict[str, Any]:
        """合成專家知識庫"""
        synthesized = {
            "domain": domain,
            "content": [],
            "detailed_info": [],
            "best_practices": [],
            "examples": [],
            "references": []
        }
        
        for source in knowledge_sources:
            source_type = source.get("type", "unknown")
            content = source.get("content", "")
            
            if source_type == "search_result":
                synthesized["content"].append(content)
                synthesized["references"].append(source.get("url", ""))
            elif source_type == "documentation":
                synthesized["detailed_info"].append(content)
            elif source_type == "example":
                synthesized["examples"].append(content)
            elif source_type == "best_practice":
                synthesized["best_practices"].append(content)
        
        return synthesized

# 工廠函數
def create_dynamic_expert_registry() -> DynamicExpertRegistry:
    """創建動態專家註冊中心"""
    return DynamicExpertRegistry()

