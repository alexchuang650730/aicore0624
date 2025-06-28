"""
智能Domain分類器 - 基於LLM和Domain Expert的動態領域識別
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import time

logger = logging.getLogger(__name__)

@dataclass
class DomainExpert:
    """領域專家信息"""
    expert_id: str
    name: str
    domain_id: str
    expertise_areas: List[str]
    credentials: List[str]
    contact_info: Dict[str, str]
    prompt_templates: Dict[str, str] = field(default_factory=dict)
    classification_examples: List[Dict] = field(default_factory=list)
    active: bool = True

@dataclass
class DomainClassificationRequest:
    """領域分類請求"""
    request_text: str
    context: Dict = field(default_factory=dict)
    user_preferences: Dict = field(default_factory=dict)
    previous_domains: List[str] = field(default_factory=list)

@dataclass
class DomainClassificationResult:
    """領域分類結果"""
    primary_domain: str
    confidence: float
    secondary_domains: List[Tuple[str, float]] = field(default_factory=list)
    reasoning: str = ""
    expert_insights: Dict[str, str] = field(default_factory=dict)
    llm_analysis: Dict = field(default_factory=dict)

class LLMProvider(ABC):
    """LLM提供者抽象基類"""
    
    @abstractmethod
    async def classify_domain(self, prompt: str, request_text: str) -> Dict:
        """使用LLM進行領域分類"""
        pass
    
    @abstractmethod
    async def analyze_expertise_match(self, expert_prompt: str, request_text: str) -> Dict:
        """分析專家匹配度"""
        pass

class ClaudeProvider(LLMProvider):
    """Claude LLM提供者"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.model = "claude-3-sonnet-20240229"
    
    async def classify_domain(self, prompt: str, request_text: str) -> Dict:
        """使用Claude進行領域分類"""
        try:
            # 模擬Claude API調用
            # 實際實現中需要調用真實的Claude API
            classification_prompt = f"""
{prompt}

請分析以下請求並進行領域分類：
{request_text}

請以JSON格式返回結果，包含：
- primary_domain: 主要領域
- confidence: 信心度(0-1)
- secondary_domains: 次要領域列表
- reasoning: 分類理由
"""
            
            # 這裡應該是真實的API調用
            # response = await claude_api.complete(classification_prompt)
            
            # 模擬響應
            await asyncio.sleep(0.1)  # 模擬API延遲
            
            # 簡單的關鍵詞匹配作為模擬
            if any(word in request_text.lower() for word in ['代碼', 'code', '程式', '技術', 'api']):
                return {
                    "primary_domain": "technology",
                    "confidence": 0.85,
                    "secondary_domains": [("business", 0.3)],
                    "reasoning": "請求包含技術相關關鍵詞，主要涉及技術領域"
                }
            elif any(word in request_text.lower() for word in ['市場', '商業', '業務', 'business']):
                return {
                    "primary_domain": "business", 
                    "confidence": 0.80,
                    "secondary_domains": [("technology", 0.2)],
                    "reasoning": "請求主要涉及商業和市場相關內容"
                }
            elif any(word in request_text.lower() for word in ['設計', '創意', 'design', '品牌']):
                return {
                    "primary_domain": "creative",
                    "confidence": 0.75,
                    "secondary_domains": [("business", 0.4)],
                    "reasoning": "請求涉及設計和創意相關內容"
                }
            else:
                return {
                    "primary_domain": "general",
                    "confidence": 0.60,
                    "secondary_domains": [],
                    "reasoning": "無法明確識別特定領域，歸類為通用領域"
                }
                
        except Exception as e:
            logger.error(f"Claude分類失敗: {e}")
            return {
                "primary_domain": "general",
                "confidence": 0.0,
                "secondary_domains": [],
                "reasoning": f"分類失敗: {str(e)}"
            }
    
    async def analyze_expertise_match(self, expert_prompt: str, request_text: str) -> Dict:
        """分析專家匹配度"""
        try:
            analysis_prompt = f"""
{expert_prompt}

請分析以下請求是否匹配您的專業領域：
{request_text}

請以JSON格式返回：
- match_score: 匹配分數(0-1)
- relevant_expertise: 相關的專業領域
- recommendations: 專業建議
- can_handle: 是否能夠處理此請求
"""
            
            # 模擬專家匹配分析
            await asyncio.sleep(0.1)
            
            return {
                "match_score": 0.8,
                "relevant_expertise": ["軟體架構", "系統設計"],
                "recommendations": ["建議進行詳細的需求分析", "考慮使用微服務架構"],
                "can_handle": True
            }
            
        except Exception as e:
            logger.error(f"專家匹配分析失敗: {e}")
            return {
                "match_score": 0.0,
                "relevant_expertise": [],
                "recommendations": [],
                "can_handle": False
            }

class GeminiProvider(LLMProvider):
    """Gemini LLM提供者"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.model = "gemini-pro"
    
    async def classify_domain(self, prompt: str, request_text: str) -> Dict:
        """使用Gemini進行領域分類"""
        try:
            # 模擬Gemini API調用
            await asyncio.sleep(0.1)
            
            # 簡單的模擬實現
            if "技術" in request_text or "代碼" in request_text:
                return {
                    "primary_domain": "technology",
                    "confidence": 0.82,
                    "secondary_domains": [("business", 0.25)],
                    "reasoning": "Gemini識別為技術領域請求"
                }
            else:
                return {
                    "primary_domain": "general",
                    "confidence": 0.65,
                    "secondary_domains": [],
                    "reasoning": "Gemini無法明確分類"
                }
                
        except Exception as e:
            logger.error(f"Gemini分類失敗: {e}")
            return {
                "primary_domain": "general",
                "confidence": 0.0,
                "secondary_domains": [],
                "reasoning": f"分類失敗: {str(e)}"
            }
    
    async def analyze_expertise_match(self, expert_prompt: str, request_text: str) -> Dict:
        """分析專家匹配度"""
        try:
            await asyncio.sleep(0.1)
            return {
                "match_score": 0.75,
                "relevant_expertise": ["業務分析"],
                "recommendations": ["建議進行市場調研"],
                "can_handle": True
            }
        except Exception as e:
            logger.error(f"Gemini專家匹配分析失敗: {e}")
            return {
                "match_score": 0.0,
                "relevant_expertise": [],
                "recommendations": [],
                "can_handle": False
            }

class DomainExpertRegistry:
    """領域專家註冊表"""
    
    def __init__(self):
        self.experts: Dict[str, DomainExpert] = {}
        self.domain_experts: Dict[str, List[str]] = {}  # domain_id -> expert_ids
        self._initialize_default_experts()
    
    def _initialize_default_experts(self):
        """初始化默認專家"""
        # 技術領域專家
        tech_expert = DomainExpert(
            expert_id="tech_expert_001",
            name="Dr. Alex Chen - 軟體架構專家",
            domain_id="technology",
            expertise_areas=[
                "軟體架構設計", "微服務架構", "雲端系統", "API設計",
                "性能優化", "系統安全", "DevOps", "容器化技術"
            ],
            credentials=[
                "Google Cloud Architect認證",
                "AWS Solutions Architect認證", 
                "15年軟體開發經驗",
                "曾任職於Google、Microsoft"
            ],
            contact_info={
                "email": "alex.chen@techexpert.com",
                "linkedin": "linkedin.com/in/alexchen-architect"
            }
        )
        
        # 業務領域專家
        business_expert = DomainExpert(
            expert_id="business_expert_001",
            name="Sarah Wang - 商業策略顧問",
            domain_id="business",
            expertise_areas=[
                "商業模式設計", "市場策略", "競爭分析", "投資評估",
                "風險管理", "業務流程優化", "數位轉型", "創業輔導"
            ],
            credentials=[
                "MBA - Stanford Graduate School of Business",
                "McKinsey & Company 前顧問",
                "10年管理諮詢經驗",
                "成功輔導50+家新創公司"
            ],
            contact_info={
                "email": "sarah.wang@bizstrategy.com",
                "linkedin": "linkedin.com/in/sarahwang-strategy"
            }
        )
        
        # 創意領域專家
        creative_expert = DomainExpert(
            expert_id="creative_expert_001", 
            name="David Kim - 創意總監",
            domain_id="creative",
            expertise_areas=[
                "品牌設計", "用戶體驗設計", "視覺傳達", "創意策略",
                "數位行銷", "內容創作", "設計思維", "創新管理"
            ],
            credentials=[
                "IDEO設計思維認證",
                "Adobe認證設計專家",
                "12年創意產業經驗",
                "Red Dot Design Award得主"
            ],
            contact_info={
                "email": "david.kim@creativelab.com",
                "portfolio": "davidkim.design"
            }
        )
        
        # 註冊專家
        self.register_expert(tech_expert)
        self.register_expert(business_expert)
        self.register_expert(creative_expert)
        
        # 設置專家提示詞模板
        self._setup_expert_prompts()
    
    def _setup_expert_prompts(self):
        """設置專家提示詞模板"""
        
        # 技術專家提示詞
        tech_prompt = """
您是Dr. Alex Chen，一位資深的軟體架構專家，擁有15年的軟體開發經驗，曾任職於Google和Microsoft。
您的專業領域包括：軟體架構設計、微服務架構、雲端系統、API設計、性能優化、系統安全、DevOps、容器化技術。

作為技術領域的專家，請您：
1. 深入分析技術需求和挑戰
2. 提供基於最佳實踐的解決方案
3. 考慮可擴展性、安全性和性能
4. 推薦合適的技術棧和工具
5. 提供具體的實施建議和注意事項

請以專業、實用的方式回應，並提供具體的技術細節和實施步驟。
"""
        
        # 業務專家提示詞
        business_prompt = """
您是Sarah Wang，一位經驗豐富的商業策略顧問，擁有Stanford MBA學位和McKinsey諮詢背景。
您的專業領域包括：商業模式設計、市場策略、競爭分析、投資評估、風險管理、業務流程優化。

作為業務領域的專家，請您：
1. 從商業價值角度分析問題
2. 提供市場導向的策略建議
3. 評估商業可行性和風險
4. 建議具體的執行計劃和里程碑
5. 考慮ROI和成本效益

請以戰略性、實務性的方式回應，並提供可執行的商業建議。
"""
        
        # 創意專家提示詞
        creative_prompt = """
您是David Kim，一位獲獎的創意總監，擁有12年創意產業經驗和Red Dot Design Award。
您的專業領域包括：品牌設計、用戶體驗設計、視覺傳達、創意策略、數位行銷、內容創作。

作為創意領域的專家，請您：
1. 從用戶體驗和品牌角度思考
2. 提供創新且實用的設計解決方案
3. 考慮視覺美學和功能性的平衡
4. 建議創意執行的具體方法
5. 融合最新的設計趨勢和最佳實踐

請以創新、美學、用戶中心的方式回應，並提供具體的創意指導。
"""
        
        # 更新專家提示詞
        self.experts["tech_expert_001"].prompt_templates["classification"] = tech_prompt
        self.experts["business_expert_001"].prompt_templates["classification"] = business_prompt  
        self.experts["creative_expert_001"].prompt_templates["classification"] = creative_prompt
    
    def register_expert(self, expert: DomainExpert):
        """註冊領域專家"""
        self.experts[expert.expert_id] = expert
        
        if expert.domain_id not in self.domain_experts:
            self.domain_experts[expert.domain_id] = []
        
        self.domain_experts[expert.domain_id].append(expert.expert_id)
        logger.info(f"註冊領域專家: {expert.name} ({expert.domain_id})")
    
    def get_experts_by_domain(self, domain_id: str) -> List[DomainExpert]:
        """獲取指定領域的專家"""
        expert_ids = self.domain_experts.get(domain_id, [])
        return [self.experts[expert_id] for expert_id in expert_ids if self.experts[expert_id].active]
    
    def get_expert(self, expert_id: str) -> Optional[DomainExpert]:
        """獲取指定專家"""
        return self.experts.get(expert_id)
    
    def get_all_experts(self) -> List[DomainExpert]:
        """獲取所有活躍專家"""
        return [expert for expert in self.experts.values() if expert.active]

class IntelligentDomainClassifier:
    """智能領域分類器"""
    
    def __init__(self):
        self.llm_providers: Dict[str, LLMProvider] = {}
        self.expert_registry = DomainExpertRegistry()
        self.classification_cache: Dict[str, DomainClassificationResult] = {}
        self.cache_ttl = 3600  # 1小時緩存
        
        # 初始化LLM提供者
        self._initialize_llm_providers()
    
    def _initialize_llm_providers(self):
        """初始化LLM提供者"""
        self.llm_providers["claude"] = ClaudeProvider()
        self.llm_providers["gemini"] = GeminiProvider()
    
    async def classify_request(self, request: DomainClassificationRequest) -> DomainClassificationResult:
        """智能分類請求"""
        start_time = time.time()
        
        try:
            # 1. 檢查緩存
            cache_key = self._generate_cache_key(request.request_text)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                logger.info(f"使用緩存的分類結果: {cached_result.primary_domain}")
                return cached_result
            
            # 2. 並行使用多個LLM進行分類
            llm_results = await self._classify_with_multiple_llms(request)
            
            # 3. 獲取專家洞察
            expert_insights = await self._get_expert_insights(request, llm_results)
            
            # 4. 綜合分析和決策
            final_result = await self._synthesize_classification(
                request, llm_results, expert_insights
            )
            
            # 5. 緩存結果
            self._cache_result(cache_key, final_result)
            
            processing_time = time.time() - start_time
            logger.info(f"領域分類完成: {final_result.primary_domain} (耗時: {processing_time:.2f}s)")
            
            return final_result
            
        except Exception as e:
            logger.error(f"領域分類失敗: {e}")
            return DomainClassificationResult(
                primary_domain="general",
                confidence=0.0,
                reasoning=f"分類失敗: {str(e)}"
            )
    
    async def _classify_with_multiple_llms(self, request: DomainClassificationRequest) -> Dict[str, Dict]:
        """使用多個LLM進行分類"""
        classification_prompt = self._build_classification_prompt()
        
        tasks = []
        for provider_name, provider in self.llm_providers.items():
            task = self._classify_with_single_llm(
                provider_name, provider, classification_prompt, request.request_text
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        llm_results = {}
        for i, (provider_name, result) in enumerate(zip(self.llm_providers.keys(), results)):
            if isinstance(result, Exception):
                logger.warning(f"LLM {provider_name} 分類失敗: {result}")
                llm_results[provider_name] = {
                    "primary_domain": "general",
                    "confidence": 0.0,
                    "error": str(result)
                }
            else:
                llm_results[provider_name] = result
        
        return llm_results
    
    async def _classify_with_single_llm(self, provider_name: str, provider: LLMProvider, 
                                      prompt: str, request_text: str) -> Dict:
        """使用單個LLM進行分類"""
        try:
            result = await provider.classify_domain(prompt, request_text)
            result["provider"] = provider_name
            return result
        except Exception as e:
            logger.error(f"LLM {provider_name} 分類失敗: {e}")
            raise e
    
    def _build_classification_prompt(self) -> str:
        """構建分類提示詞"""
        available_domains = list(self.expert_registry.domain_experts.keys())
        experts_info = []
        
        for domain_id in available_domains:
            experts = self.expert_registry.get_experts_by_domain(domain_id)
            if experts:
                expert = experts[0]  # 取第一個專家作為代表
                experts_info.append(f"- {domain_id}: {expert.name} - {', '.join(expert.expertise_areas[:3])}")
        
        prompt = f"""
您是一個智能領域分類系統，需要將用戶請求分類到最合適的專業領域。

可用的專業領域和專家：
{chr(10).join(experts_info)}

分類原則：
1. 仔細分析請求的核心內容和意圖
2. 考慮請求涉及的專業知識領域
3. 評估不同領域專家的匹配程度
4. 如果涉及多個領域，識別主要和次要領域
5. 提供分類的詳細理由

請分析請求並返回JSON格式的分類結果，包含：
- primary_domain: 主要領域ID
- confidence: 信心度(0-1)
- secondary_domains: 次要領域列表 [(domain_id, confidence), ...]
- reasoning: 詳細的分類理由
"""
        return prompt
    
    async def _get_expert_insights(self, request: DomainClassificationRequest, 
                                 llm_results: Dict[str, Dict]) -> Dict[str, Dict]:
        """獲取專家洞察"""
        expert_insights = {}
        
        # 基於LLM結果確定候選領域
        candidate_domains = set()
        for result in llm_results.values():
            if "primary_domain" in result:
                candidate_domains.add(result["primary_domain"])
            if "secondary_domains" in result:
                for domain, _ in result["secondary_domains"]:
                    candidate_domains.add(domain)
        
        # 為每個候選領域獲取專家洞察
        for domain_id in candidate_domains:
            if domain_id == "general":
                continue
                
            experts = self.expert_registry.get_experts_by_domain(domain_id)
            if experts:
                expert = experts[0]  # 使用第一個專家
                expert_prompt = expert.prompt_templates.get("classification", "")
                
                if expert_prompt:
                    try:
                        # 使用Claude分析專家匹配度
                        claude_provider = self.llm_providers.get("claude")
                        if claude_provider:
                            insight = await claude_provider.analyze_expertise_match(
                                expert_prompt, request.request_text
                            )
                            expert_insights[domain_id] = {
                                "expert_name": expert.name,
                                "expert_id": expert.expert_id,
                                "insight": insight
                            }
                    except Exception as e:
                        logger.warning(f"獲取專家 {expert.name} 洞察失敗: {e}")
        
        return expert_insights
    
    async def _synthesize_classification(self, request: DomainClassificationRequest,
                                       llm_results: Dict[str, Dict], 
                                       expert_insights: Dict[str, Dict]) -> DomainClassificationResult:
        """綜合分析和決策"""
        
        # 1. 統計LLM投票結果
        domain_votes = {}
        total_confidence = {}
        
        for provider, result in llm_results.items():
            if "primary_domain" in result and result["confidence"] > 0:
                domain = result["primary_domain"]
                confidence = result["confidence"]
                
                if domain not in domain_votes:
                    domain_votes[domain] = 0
                    total_confidence[domain] = 0
                
                domain_votes[domain] += 1
                total_confidence[domain] += confidence
        
        # 2. 計算平均信心度
        avg_confidence = {}
        for domain, votes in domain_votes.items():
            avg_confidence[domain] = total_confidence[domain] / votes
        
        # 3. 結合專家洞察調整分數
        expert_adjusted_confidence = {}
        for domain, confidence in avg_confidence.items():
            adjusted_confidence = confidence
            
            if domain in expert_insights:
                expert_insight = expert_insights[domain]["insight"]
                expert_match_score = expert_insight.get("match_score", 0)
                
                # 專家匹配分數作為置信度調整因子
                adjusted_confidence = confidence * 0.7 + expert_match_score * 0.3
            
            expert_adjusted_confidence[domain] = adjusted_confidence
        
        # 4. 確定最終結果
        if not expert_adjusted_confidence:
            return DomainClassificationResult(
                primary_domain="general",
                confidence=0.5,
                reasoning="無法確定具體領域，歸類為通用領域"
            )
        
        # 選擇信心度最高的領域
        primary_domain = max(expert_adjusted_confidence.keys(), 
                           key=lambda x: expert_adjusted_confidence[x])
        primary_confidence = expert_adjusted_confidence[primary_domain]
        
        # 構建次要領域列表
        secondary_domains = []
        for domain, confidence in expert_adjusted_confidence.items():
            if domain != primary_domain and confidence > 0.3:
                secondary_domains.append((domain, confidence))
        
        secondary_domains.sort(key=lambda x: x[1], reverse=True)
        
        # 構建推理說明
        reasoning_parts = []
        reasoning_parts.append(f"LLM分析結果: {len(llm_results)}個模型參與分析")
        
        for provider, result in llm_results.items():
            if "reasoning" in result:
                reasoning_parts.append(f"{provider}: {result['reasoning']}")
        
        if expert_insights:
            reasoning_parts.append("專家洞察:")
            for domain, insight_data in expert_insights.items():
                expert_name = insight_data["expert_name"]
                match_score = insight_data["insight"].get("match_score", 0)
                reasoning_parts.append(f"- {expert_name} ({domain}): 匹配度 {match_score:.2f}")
        
        reasoning = "\n".join(reasoning_parts)
        
        return DomainClassificationResult(
            primary_domain=primary_domain,
            confidence=primary_confidence,
            secondary_domains=secondary_domains,
            reasoning=reasoning,
            expert_insights={k: v["insight"] for k, v in expert_insights.items()},
            llm_analysis=llm_results
        )
    
    def _generate_cache_key(self, request_text: str) -> str:
        """生成緩存鍵"""
        import hashlib
        return hashlib.md5(request_text.encode('utf-8')).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[DomainClassificationResult]:
        """獲取緩存結果"""
        if cache_key in self.classification_cache:
            cached_item = self.classification_cache[cache_key]
            # 檢查緩存是否過期
            if hasattr(cached_item, 'cached_at'):
                if time.time() - cached_item.cached_at < self.cache_ttl:
                    return cached_item
                else:
                    del self.classification_cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: DomainClassificationResult):
        """緩存結果"""
        result.cached_at = time.time()
        self.classification_cache[cache_key] = result
    
    async def invite_expert(self, expert_info: Dict) -> str:
        """邀請新的領域專家"""
        """
        邀請流程：
        1. 驗證專家資格和專業領域
        2. 創建專家檔案
        3. 設置專業提示詞模板
        4. 添加分類示例
        5. 激活專家參與
        """
        
        expert = DomainExpert(
            expert_id=expert_info["expert_id"],
            name=expert_info["name"],
            domain_id=expert_info["domain_id"],
            expertise_areas=expert_info["expertise_areas"],
            credentials=expert_info["credentials"],
            contact_info=expert_info["contact_info"]
        )
        
        # 註冊專家
        self.expert_registry.register_expert(expert)
        
        # 生成邀請確認
        invitation_message = f"""
🎉 專家邀請成功！

專家信息：
- 姓名: {expert.name}
- 領域: {expert.domain_id}
- 專業領域: {', '.join(expert.expertise_areas)}
- 資格認證: {', '.join(expert.credentials)}

下一步：
1. 請專家設計專業提示詞模板
2. 提供領域分類示例
3. 參與系統測試和優化

專家現已激活，可以參與領域分類和諮詢服務。
"""
        
        return invitation_message
    
    async def update_expert_prompts(self, expert_id: str, prompt_templates: Dict[str, str]):
        """更新專家提示詞模板"""
        expert = self.expert_registry.get_expert(expert_id)
        if expert:
            expert.prompt_templates.update(prompt_templates)
            logger.info(f"更新專家 {expert.name} 的提示詞模板")
            return True
        return False
    
    async def get_classification_statistics(self) -> Dict:
        """獲取分類統計信息"""
        stats = {
            "total_experts": len(self.expert_registry.get_all_experts()),
            "domains_covered": len(self.expert_registry.domain_experts),
            "llm_providers": len(self.llm_providers),
            "cache_size": len(self.classification_cache),
            "domain_distribution": {}
        }
        
        # 統計各領域專家數量
        for domain_id, expert_ids in self.expert_registry.domain_experts.items():
            active_experts = [eid for eid in expert_ids if self.expert_registry.experts[eid].active]
            stats["domain_distribution"][domain_id] = len(active_experts)
        
        return stats

