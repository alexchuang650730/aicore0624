"""
自我進化系統 - 能力比對、短板識別、動態Adapter生成
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import time
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class CapabilityGap:
    """能力短板"""
    gap_id: str
    description: str
    request_examples: List[str]
    current_performance: float  # 0-1
    target_performance: float   # 0-1
    gap_severity: float        # 0-1
    required_expertise: List[str]
    suggested_expert_profile: Dict[str, Any]

@dataclass
class AdapterMCP:
    """動態生成的Adapter MCP"""
    adapter_id: str
    name: str
    target_gap: CapabilityGap
    prompt_template: str
    expert_optimized: bool = False
    performance_score: float = 0.0
    usage_count: int = 0

class CapabilityComparator:
    """能力比對器"""
    
    def __init__(self):
        self.my_capabilities = {
            "coding": 0.85,
            "analysis": 0.80,
            "writing": 0.90,
            "math": 0.75,
            "creative": 0.70,
            "business": 0.65,
            "technical_design": 0.80,
            "data_science": 0.70,
            "ui_ux": 0.60,
            "marketing": 0.55,
            "legal": 0.40,
            "medical": 0.30,
            "finance": 0.50,
            "research": 0.85
        }
    
    async def compare_request_capability(self, request: str, actual_performance: float) -> Dict:
        """比對請求與現有能力"""
        # 分析請求涉及的能力領域
        required_capabilities = await self._analyze_required_capabilities(request)
        
        # 計算能力匹配度
        capability_matches = {}
        overall_match = 0.0
        
        for capability, weight in required_capabilities.items():
            my_level = self.my_capabilities.get(capability, 0.3)  # 默認較低能力
            capability_matches[capability] = {
                "my_level": my_level,
                "weight": weight,
                "contribution": my_level * weight
            }
            overall_match += my_level * weight
        
        # 計算期望vs實際性能差距
        performance_gap = max(0, 0.85 - actual_performance)  # 期望85%以上性能
        
        return {
            "required_capabilities": required_capabilities,
            "capability_matches": capability_matches,
            "overall_match": overall_match,
            "actual_performance": actual_performance,
            "performance_gap": performance_gap,
            "needs_improvement": performance_gap > 0.15
        }
    
    async def _analyze_required_capabilities(self, request: str) -> Dict[str, float]:
        """分析請求需要的能力"""
        capabilities = {}
        request_lower = request.lower()
        
        # 簡單關鍵詞匹配（實際可用LLM分析）
        capability_keywords = {
            "coding": ["代碼", "程式", "code", "programming", "開發", "api"],
            "analysis": ["分析", "analysis", "研究", "調查", "評估"],
            "writing": ["寫作", "文案", "內容", "writing", "content"],
            "math": ["數學", "計算", "math", "算法", "統計"],
            "creative": ["創意", "設計", "creative", "design", "品牌"],
            "business": ["商業", "業務", "business", "市場", "策略"],
            "ui_ux": ["界面", "用戶體驗", "ui", "ux", "交互"],
            "marketing": ["營銷", "推廣", "marketing", "廣告"],
            "legal": ["法律", "合規", "legal", "法規"],
            "medical": ["醫療", "健康", "medical", "診斷"],
            "finance": ["金融", "財務", "finance", "投資", "會計"]
        }
        
        for capability, keywords in capability_keywords.items():
            weight = 0.0
            for keyword in keywords:
                if keyword in request_lower:
                    weight += 0.2
            capabilities[capability] = min(weight, 1.0)
        
        # 歸一化權重
        total_weight = sum(capabilities.values())
        if total_weight > 0:
            capabilities = {k: v/total_weight for k, v in capabilities.items() if v > 0}
        
        return capabilities

class GapIdentifier:
    """短板識別器"""
    
    def __init__(self):
        self.performance_history = {}
        self.gap_threshold = 0.15  # 15%以上差距視為短板
    
    async def identify_gaps(self, comparison_result: Dict, request: str) -> List[CapabilityGap]:
        """識別能力短板"""
        gaps = []
        
        if not comparison_result["needs_improvement"]:
            return gaps
        
        # 分析具體短板
        capability_matches = comparison_result["capability_matches"]
        
        for capability, match_info in capability_matches.items():
            my_level = match_info["my_level"]
            weight = match_info["weight"]
            
            if weight > 0.3 and my_level < 0.7:  # 重要且能力不足
                gap = await self._create_capability_gap(
                    capability, my_level, request, comparison_result
                )
                gaps.append(gap)
        
        return gaps
    
    async def _create_capability_gap(self, capability: str, current_level: float, 
                                   request: str, comparison_result: Dict) -> CapabilityGap:
        """創建能力短板對象"""
        gap_id = f"gap_{capability}_{int(time.time())}"
        
        # 根據能力類型確定專家需求
        expert_profiles = {
            "ui_ux": {
                "title": "UI/UX設計專家",
                "expertise": ["用戶體驗設計", "界面設計", "交互設計", "可用性測試"],
                "background": "設計相關學位，5年以上UX設計經驗"
            },
            "marketing": {
                "title": "數位營銷專家", 
                "expertise": ["數位營銷", "內容營銷", "社交媒體", "SEO/SEM"],
                "background": "營銷相關背景，熟悉數位營銷工具和策略"
            },
            "legal": {
                "title": "法律顧問",
                "expertise": ["商業法", "合規", "知識產權", "合同法"],
                "background": "法律學位，執業律師資格"
            },
            "medical": {
                "title": "醫療專家",
                "expertise": ["臨床醫學", "診斷", "治療方案", "醫療法規"],
                "background": "醫學學位，臨床經驗"
            },
            "finance": {
                "title": "金融分析師",
                "expertise": ["財務分析", "投資評估", "風險管理", "會計"],
                "background": "金融相關學位，CFA或相關認證"
            }
        }
        
        expert_profile = expert_profiles.get(capability, {
            "title": f"{capability}專家",
            "expertise": [capability],
            "background": f"{capability}領域專業背景"
        })
        
        return CapabilityGap(
            gap_id=gap_id,
            description=f"{capability}能力不足，當前水平{current_level:.2f}",
            request_examples=[request],
            current_performance=current_level,
            target_performance=0.85,
            gap_severity=(0.85 - current_level),
            required_expertise=expert_profile["expertise"],
            suggested_expert_profile=expert_profile
        )

class AdapterGenerator:
    """Adapter MCP生成器"""
    
    def __init__(self):
        self.generated_adapters = {}
    
    async def generate_adapter(self, gap: CapabilityGap) -> AdapterMCP:
        """生成新的Adapter MCP"""
        adapter_id = f"adapter_{gap.gap_id}"
        
        # 生成基礎提示詞模板
        base_prompt = await self._generate_base_prompt(gap)
        
        adapter = AdapterMCP(
            adapter_id=adapter_id,
            name=f"{gap.suggested_expert_profile['title']} Adapter",
            target_gap=gap,
            prompt_template=base_prompt
        )
        
        self.generated_adapters[adapter_id] = adapter
        logger.info(f"生成新Adapter: {adapter.name}")
        
        return adapter
    
    async def _generate_base_prompt(self, gap: CapabilityGap) -> str:
        """生成基礎提示詞模板"""
        expertise_areas = ", ".join(gap.required_expertise)
        
        prompt = f"""
您是一位專業的{gap.suggested_expert_profile['title']}，專精於{expertise_areas}。

專業背景：
{gap.suggested_expert_profile['background']}

核心能力：
{chr(10).join(f"- {skill}" for skill in gap.required_expertise)}

當處理相關請求時，請：
1. 運用您的專業知識深入分析問題
2. 提供基於最佳實踐的解決方案
3. 考慮實際應用中的挑戰和限制
4. 給出具體、可執行的建議
5. 必要時提供相關資源和參考

請以專業、實用的方式回應，確保建議的可行性和有效性。

[注意：此為基礎模板，需要專家進一步優化]
"""
        return prompt

class ExpertInviter:
    """專家邀請系統"""
    
    def __init__(self):
        self.expert_database = {}
        self.invitation_history = {}
    
    async def find_and_invite_expert(self, gap: CapabilityGap) -> Dict:
        """根據短板尋找並邀請專家"""
        # 搜索合適的專家
        suitable_experts = await self._search_experts(gap)
        
        if not suitable_experts:
            # 生成專家邀請需求
            invitation_request = await self._generate_invitation_request(gap)
            return {
                "status": "invitation_needed",
                "invitation_request": invitation_request,
                "gap_info": gap
            }
        
        # 邀請最合適的專家
        best_expert = suitable_experts[0]
        invitation_result = await self._send_invitation(best_expert, gap)
        
        return {
            "status": "expert_invited",
            "expert": best_expert,
            "invitation_result": invitation_result
        }
    
    async def _search_experts(self, gap: CapabilityGap) -> List[Dict]:
        """搜索合適的專家"""
        # 這裡可以連接專家數據庫或平台
        # 暫時返回空列表，表示需要邀請新專家
        return []
    
    async def _generate_invitation_request(self, gap: CapabilityGap) -> Dict:
        """生成專家邀請需求"""
        return {
            "title": f"邀請{gap.suggested_expert_profile['title']}",
            "description": f"我們需要{gap.suggested_expert_profile['title']}來幫助優化{gap.description}",
            "required_expertise": gap.required_expertise,
            "background_requirements": gap.suggested_expert_profile['background'],
            "tasks": [
                "優化AI提示詞模板",
                "提供專業知識指導", 
                "驗證解決方案的專業性",
                "持續改進系統性能"
            ],
            "gap_severity": gap.gap_severity,
            "expected_improvement": f"從{gap.current_performance:.2f}提升到{gap.target_performance:.2f}"
        }
    
    async def _send_invitation(self, expert: Dict, gap: CapabilityGap) -> Dict:
        """發送專家邀請"""
        invitation_id = f"inv_{gap.gap_id}_{int(time.time())}"
        
        invitation = {
            "invitation_id": invitation_id,
            "expert_id": expert.get("expert_id"),
            "gap_id": gap.gap_id,
            "sent_at": time.time(),
            "status": "pending"
        }
        
        self.invitation_history[invitation_id] = invitation
        
        return invitation

class PromptOptimizer:
    """提示詞優化器"""
    
    def __init__(self):
        self.optimization_history = {}
    
    async def optimize_with_expert(self, adapter: AdapterMCP, expert_feedback: Dict) -> AdapterMCP:
        """使用專家反饋優化提示詞"""
        
        # 應用專家優化
        optimized_prompt = await self._apply_expert_optimization(
            adapter.prompt_template, expert_feedback
        )
        
        # 更新Adapter
        adapter.prompt_template = optimized_prompt
        adapter.expert_optimized = True
        
        # 記錄優化歷史
        optimization_record = {
            "adapter_id": adapter.adapter_id,
            "original_prompt": adapter.prompt_template,
            "optimized_prompt": optimized_prompt,
            "expert_feedback": expert_feedback,
            "optimized_at": time.time()
        }
        
        self.optimization_history[adapter.adapter_id] = optimization_record
        
        logger.info(f"專家優化完成: {adapter.name}")
        return adapter
    
    async def _apply_expert_optimization(self, base_prompt: str, expert_feedback: Dict) -> str:
        """應用專家優化建議"""
        
        # 提取專家建議
        expert_additions = expert_feedback.get("prompt_additions", [])
        expert_modifications = expert_feedback.get("prompt_modifications", {})
        expert_examples = expert_feedback.get("examples", [])
        
        # 構建優化後的提示詞
        optimized_sections = []
        
        # 基礎部分
        optimized_sections.append(base_prompt)
        
        # 專家補充
        if expert_additions:
            optimized_sections.append("\n## 專家補充指導：")
            for addition in expert_additions:
                optimized_sections.append(f"- {addition}")
        
        # 專業示例
        if expert_examples:
            optimized_sections.append("\n## 專業示例：")
            for i, example in enumerate(expert_examples, 1):
                optimized_sections.append(f"{i}. {example}")
        
        # 專家修正
        if expert_modifications:
            optimized_sections.append("\n## 專家修正要點：")
            for key, value in expert_modifications.items():
                optimized_sections.append(f"- {key}: {value}")
        
        return "\n".join(optimized_sections)

class SelfEvolutionSystem:
    """自我進化系統主控制器"""
    
    def __init__(self):
        self.capability_comparator = CapabilityComparator()
        self.gap_identifier = GapIdentifier()
        self.adapter_generator = AdapterGenerator()
        self.expert_inviter = ExpertInviter()
        self.prompt_optimizer = PromptOptimizer()
        
        self.evolution_history = []
    
    async def process_request_with_evolution(self, request: str, actual_performance: float) -> Dict:
        """處理請求並進行自我進化"""
        
        # 1. 能力比對
        comparison = await self.capability_comparator.compare_request_capability(
            request, actual_performance
        )
        
        # 2. 識別短板
        gaps = await self.gap_identifier.identify_gaps(comparison, request)
        
        evolution_result = {
            "request": request,
            "comparison": comparison,
            "gaps_identified": len(gaps),
            "gaps": [],
            "adapters_generated": [],
            "expert_invitations": []
        }
        
        # 3. 處理每個短板
        for gap in gaps:
            gap_result = await self._process_single_gap(gap)
            evolution_result["gaps"].append(gap_result)
        
        # 4. 記錄進化歷史
        self.evolution_history.append({
            "timestamp": time.time(),
            "result": evolution_result
        })
        
        return evolution_result
    
    async def _process_single_gap(self, gap: CapabilityGap) -> Dict:
        """處理單個能力短板"""
        
        # 生成Adapter MCP
        adapter = await self.adapter_generator.generate_adapter(gap)
        
        # 邀請專家
        expert_invitation = await self.expert_inviter.find_and_invite_expert(gap)
        
        return {
            "gap": gap,
            "adapter": adapter,
            "expert_invitation": expert_invitation
        }
    
    async def apply_expert_feedback(self, adapter_id: str, expert_feedback: Dict) -> bool:
        """應用專家反饋"""
        adapter = self.adapter_generator.generated_adapters.get(adapter_id)
        if not adapter:
            return False
        
        # 優化提示詞
        optimized_adapter = await self.prompt_optimizer.optimize_with_expert(
            adapter, expert_feedback
        )
        
        logger.info(f"專家反饋已應用到 {optimized_adapter.name}")
        return True
    
    async def get_evolution_status(self) -> Dict:
        """獲取進化狀態"""
        return {
            "total_gaps_identified": len(self.gap_identifier.performance_history),
            "adapters_generated": len(self.adapter_generator.generated_adapters),
            "expert_invitations": len(self.expert_inviter.invitation_history),
            "optimizations_applied": len(self.prompt_optimizer.optimization_history),
            "evolution_cycles": len(self.evolution_history)
        }

# 使用示例
async def demo_self_evolution():
    """演示自我進化系統"""
    
    system = SelfEvolutionSystem()
    
    # 模擬一個UI設計請求的處理結果
    request = "請幫我設計一個電商網站的用戶界面，需要考慮用戶體驗和轉化率優化"
    actual_performance = 0.6  # 假設實際處理效果只有60%
    
    # 觸發自我進化
    evolution_result = await system.process_request_with_evolution(request, actual_performance)
    
    print("🔄 自我進化結果:")
    print(f"識別到 {evolution_result['gaps_identified']} 個能力短板")
    
    for gap_result in evolution_result['gaps']:
        gap = gap_result['gap']
        adapter = gap_result['adapter']
        invitation = gap_result['expert_invitation']
        
        print(f"\n📊 短板: {gap.description}")
        print(f"🤖 生成Adapter: {adapter.name}")
        print(f"👨‍💼 專家邀請: {invitation['status']}")
        
        if invitation['status'] == 'invitation_needed':
            req = invitation['invitation_request']
            print(f"   需要邀請: {req['title']}")
            print(f"   任務: {', '.join(req['tasks'])}")
    
    # 模擬專家反饋
    if evolution_result['gaps']:
        adapter_id = evolution_result['gaps'][0]['adapter'].adapter_id
        expert_feedback = {
            "prompt_additions": [
                "考慮移動端優先的響應式設計",
                "注重無障礙設計原則",
                "應用心理學原理提升用戶體驗"
            ],
            "examples": [
                "使用F型掃描模式設計頁面布局",
                "應用色彩心理學選擇主色調"
            ],
            "prompt_modifications": {
                "用戶研究": "必須先進行用戶畫像分析",
                "A/B測試": "建議對關鍵頁面進行A/B測試"
            }
        }
        
        success = await system.apply_expert_feedback(adapter_id, expert_feedback)
        if success:
            print(f"\n✅ 專家反饋已應用到 {adapter_id}")
    
    # 顯示系統狀態
    status = await system.get_evolution_status()
    print(f"\n📈 系統進化狀態:")
    print(f"   總短板數: {status['total_gaps_identified']}")
    print(f"   生成適配器: {status['adapters_generated']}")
    print(f"   專家邀請: {status['expert_invitations']}")
    print(f"   優化次數: {status['optimizations_applied']}")

if __name__ == "__main__":
    asyncio.run(demo_self_evolution())

