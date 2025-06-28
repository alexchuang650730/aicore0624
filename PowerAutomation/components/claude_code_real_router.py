#!/usr/bin/env python3
"""
Claude Code 真實 API 前置場景識別路由器
使用真實的 Claude API 進行動態場景識別和專家引進
"""

import asyncio
import json
import logging
import aiohttp
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# Claude API 配置
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

@dataclass
class ExpertRecommendation:
    """專家推薦"""
    expert_type: str  # 專家類型
    expertise_areas: List[str]  # 專業領域
    confidence: float  # 推薦信心度
    reasoning: str  # 推薦理由
    required_context: Dict[str, Any]  # 所需上下文

@dataclass
class ScenarioAnalysis:
    """場景分析結果"""
    scenario_type: str  # 場景類型
    complexity_level: str  # 複雜度等級
    content_size: str  # 內容大小
    technical_domains: List[str]  # 技術領域
    recommended_experts: List[ExpertRecommendation]  # 推薦專家
    context_requirements: Dict[str, Any]  # 上下文需求
    confidence_score: float  # 信心度分數
    analysis_reasoning: str  # 分析推理過程

@dataclass
class ProcessingRequest:
    """處理請求"""
    request_id: str
    user_input: str
    context: Dict[str, Any]
    timestamp: datetime
    scenario_analysis: Optional[ScenarioAnalysis] = None

class ClaudeCodeRealRouter:
    """Claude Code 真實 API 路由器"""
    
    def __init__(self):
        self.api_key = os.getenv("CLAUDE_API_KEY", "your-claude-api-key-here")
        self.processing_history: List[ProcessingRequest] = []
        self.expert_registry = {
            "code_architect": {
                "name": "代碼架構專家",
                "specialties": ["系統設計", "架構模式", "代碼重構"],
                "context_limit": "200K tokens"
            },
            "performance_optimizer": {
                "name": "性能優化專家", 
                "specialties": ["性能調優", "算法優化", "系統監控"],
                "context_limit": "200K tokens"
            },
            "api_designer": {
                "name": "API 設計專家",
                "specialties": ["RESTful API", "GraphQL", "微服務"],
                "context_limit": "200K tokens"
            },
            "security_analyst": {
                "name": "安全分析專家",
                "specialties": ["代碼審計", "漏洞分析", "安全架構"],
                "context_limit": "200K tokens"
            },
            "database_expert": {
                "name": "數據庫專家",
                "specialties": ["數據庫設計", "查詢優化", "數據遷移"],
                "context_limit": "200K tokens"
            }
        }
        
    async def analyze_and_route(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        使用真實 Claude API 進行場景分析和專家推薦
        """
        request_id = str(uuid.uuid4())
        request = ProcessingRequest(
            request_id=request_id,
            user_input=user_input,
            context=context or {},
            timestamp=datetime.now()
        )
        
        try:
            # 使用真實 Claude API 進行場景分析
            scenario_analysis = await self._real_claude_scenario_analysis(user_input, context)
            request.scenario_analysis = scenario_analysis
            
            # 基於分析結果執行專家匹配和處理
            processing_result = await self._execute_expert_processing(request)
            
            # 記錄處理歷史
            self.processing_history.append(request)
            
            return {
                "request_id": request_id,
                "scenario_analysis": asdict(scenario_analysis),
                "processing_result": processing_result,
                "timestamp": request.timestamp.isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"處理請求失敗: {e}")
            return {
                "request_id": request_id,
                "error": str(e),
                "timestamp": request.timestamp.isoformat(),
                "status": "error"
            }
    
    async def _real_claude_scenario_analysis(self, user_input: str, context: Dict[str, Any]) -> ScenarioAnalysis:
        """
        使用真實 Claude API 進行深度場景分析和專家推薦
        """
        
        analysis_prompt = f"""你是一個智能場景識別和專家推薦系統。請分析以下用戶請求，並推薦最適合的專家來處理。

用戶輸入：
{user_input}

上下文信息：
{json.dumps(context, ensure_ascii=False, indent=2)}

可用專家類型：
{json.dumps(self.expert_registry, ensure_ascii=False, indent=2)}

請提供詳細分析，包括：
1. 場景類型識別（從以下選擇：code_analysis, architecture_design, performance_optimization, api_design, security_audit, database_design, general_consulting）
2. 複雜度等級（low/medium/high/expert）
3. 內容大小評估（small/medium/large/massive）
4. 涉及的技術領域列表
5. 推薦的專家（從可用專家中選擇1-3個最適合的）
6. 每個推薦專家的詳細信息：
   - expert_type: 專家類型
   - expertise_areas: 專業領域列表
   - confidence: 推薦信心度（0-1）
   - reasoning: 推薦理由
   - required_context: 所需上下文信息
7. 上下文需求分析
8. 整體信心度評分（0-1）
9. 詳細的分析推理過程

請以以下 JSON 格式回應：
{{
  "scenario_type": "場景類型",
  "complexity_level": "複雜度等級",
  "content_size": "內容大小",
  "technical_domains": ["技術領域1", "技術領域2"],
  "recommended_experts": [
    {{
      "expert_type": "專家類型",
      "expertise_areas": ["專業領域1", "專業領域2"],
      "confidence": 0.95,
      "reasoning": "推薦理由",
      "required_context": {{"key": "value"}}
    }}
  ],
  "context_requirements": {{"key": "value"}},
  "confidence_score": 0.9,
  "analysis_reasoning": "詳細分析推理"
}}"""

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": CLAUDE_API_KEY,
                    "anthropic-version": "2023-06-01"
                }
                
                payload = {
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 2000,
                    "messages": [
                        {
                            "role": "user",
                            "content": analysis_prompt
                        }
                    ]
                }
                
                async with session.post(CLAUDE_API_URL, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["content"][0]["text"]
                        
                        # 解析 JSON 回應
                        try:
                            analysis_data = json.loads(content)
                        except json.JSONDecodeError:
                            # 如果 JSON 解析失敗，嘗試提取 JSON 部分
                            import re
                            json_match = re.search(r'\{.*\}', content, re.DOTALL)
                            if json_match:
                                analysis_data = json.loads(json_match.group())
                            else:
                                raise ValueError("無法解析 Claude API 回應")
                        
                        # 轉換為 ExpertRecommendation 對象
                        expert_recommendations = []
                        for expert_data in analysis_data.get("recommended_experts", []):
                            expert_recommendations.append(ExpertRecommendation(
                                expert_type=expert_data.get("expert_type", "general"),
                                expertise_areas=expert_data.get("expertise_areas", []),
                                confidence=expert_data.get("confidence", 0.5),
                                reasoning=expert_data.get("reasoning", ""),
                                required_context=expert_data.get("required_context", {})
                            ))
                        
                        return ScenarioAnalysis(
                            scenario_type=analysis_data.get("scenario_type", "general"),
                            complexity_level=analysis_data.get("complexity_level", "medium"),
                            content_size=analysis_data.get("content_size", "medium"),
                            technical_domains=analysis_data.get("technical_domains", []),
                            recommended_experts=expert_recommendations,
                            context_requirements=analysis_data.get("context_requirements", {}),
                            confidence_score=analysis_data.get("confidence_score", 0.8),
                            analysis_reasoning=analysis_data.get("analysis_reasoning", "基於 Claude API 的分析")
                        )
                    else:
                        error_text = await response.text()
                        raise Exception(f"Claude API 調用失敗: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Claude API 調用錯誤: {e}")
            # 回退到基本分析
            return ScenarioAnalysis(
                scenario_type="general",
                complexity_level="medium",
                content_size="medium",
                technical_domains=["general"],
                recommended_experts=[ExpertRecommendation(
                    expert_type="code_architect",
                    expertise_areas=["general"],
                    confidence=0.5,
                    reasoning="API 調用失敗，使用默認專家",
                    required_context={}
                )],
                context_requirements={},
                confidence_score=0.5,
                analysis_reasoning=f"API 調用失敗: {str(e)}"
            )
    
    async def _execute_expert_processing(self, request: ProcessingRequest) -> Dict[str, Any]:
        """
        基於專家推薦執行處理
        """
        analysis = request.scenario_analysis
        
        if not analysis.recommended_experts:
            return {"error": "沒有推薦的專家"}
        
        # 選擇信心度最高的專家
        best_expert = max(analysis.recommended_experts, key=lambda x: x.confidence)
        
        # 使用選定專家進行處理
        expert_result = await self._expert_processing(request, best_expert)
        
        return {
            "selected_expert": asdict(best_expert),
            "expert_analysis": expert_result,
            "processing_method": "expert_based",
            "context_utilization": "200K tokens available"
        }
    
    async def _expert_processing(self, request: ProcessingRequest, expert: ExpertRecommendation) -> Dict[str, Any]:
        """
        專家級處理
        """
        expert_info = self.expert_registry.get(expert.expert_type, {})
        
        expert_prompt = f"""你是一位{expert_info.get('name', '專業')}專家，專精於{', '.join(expert.expertise_areas)}。

用戶請求：
{request.user_input}

上下文信息：
{json.dumps(request.context, ensure_ascii=False, indent=2)}

場景分析：
{json.dumps(asdict(request.scenario_analysis), ensure_ascii=False, indent=2)}

請以專家的角度提供詳細的分析和建議，包括：
1. 專業分析
2. 具體建議
3. 實施步驟
4. 潛在風險和注意事項
5. 相關最佳實踐

請提供詳細且實用的專業建議。"""

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": CLAUDE_API_KEY,
                    "anthropic-version": "2023-06-01"
                }
                
                payload = {
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 4000,
                    "messages": [
                        {
                            "role": "user",
                            "content": expert_prompt
                        }
                    ]
                }
                
                async with session.post(CLAUDE_API_URL, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["content"][0]["text"]
                        
                        return {
                            "expert_response": content,
                            "expert_type": expert.expert_type,
                            "confidence": expert.confidence,
                            "tokens_used": result.get("usage", {}).get("output_tokens", 0)
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"專家處理失敗: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"專家處理錯誤: {str(e)}"}
    
    def get_expert_stats(self) -> Dict[str, Any]:
        """獲取專家使用統計"""
        if not self.processing_history:
            return {"total_requests": 0}
        
        expert_usage = {}
        for request in self.processing_history:
            if request.scenario_analysis and request.scenario_analysis.recommended_experts:
                for expert in request.scenario_analysis.recommended_experts:
                    expert_usage[expert.expert_type] = expert_usage.get(expert.expert_type, 0) + 1
        
        return {
            "total_requests": len(self.processing_history),
            "expert_usage": expert_usage,
            "available_experts": list(self.expert_registry.keys())
        }

# 測試函數
async def test_real_claude_router():
    """測試真實 Claude API 路由器"""
    router = ClaudeCodeRealRouter()
    
    test_cases = [
        {
            "input": "我的 Python API 響應時間太慢，平均 3 秒才能返回結果，需要優化到 500ms 以內",
            "context": {"current_response_time": "3s", "target": "500ms", "language": "python", "framework": "flask"}
        },
        {
            "input": "幫我設計一個電商系統的數據庫架構，需要支持用戶、商品、訂單、支付等功能",
            "context": {"system_type": "ecommerce", "expected_users": 100000, "requirements": ["scalability", "consistency"]}
        },
        {
            "input": "這段代碼有安全漏洞嗎？\n\ndef login(username, password):\n    query = f\"SELECT * FROM users WHERE username='{username}' AND password='{password}'\"\n    return db.execute(query)",
            "context": {"code_type": "authentication", "language": "python", "concern": "security"}
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n{'='*50}")
        print(f"測試案例 {i+1}: {test_case['input'][:50]}...")
        print(f"{'='*50}")
        
        result = await router.analyze_and_route(test_case["input"], test_case["context"])
        
        if result["status"] == "success":
            print(f"✅ 場景識別: {result['scenario_analysis']['scenario_type']}")
            print(f"✅ 複雜度: {result['scenario_analysis']['complexity_level']}")
            print(f"✅ 技術領域: {', '.join(result['scenario_analysis']['technical_domains'])}")
            print(f"✅ 推薦專家數量: {len(result['scenario_analysis']['recommended_experts'])}")
            
            if result['scenario_analysis']['recommended_experts']:
                best_expert = result['scenario_analysis']['recommended_experts'][0]
                print(f"✅ 最佳專家: {best_expert['expert_type']} (信心度: {best_expert['confidence']})")
                print(f"✅ 推薦理由: {best_expert['reasoning']}")
            
            if 'expert_analysis' in result['processing_result']:
                expert_response = result['processing_result']['expert_analysis'].get('expert_response', '')
                print(f"✅ 專家回應預覽: {expert_response[:200]}...")
        else:
            print(f"❌ 處理失敗: {result['error']}")
    
    print(f"\n{'='*50}")
    print("專家使用統計")
    print(f"{'='*50}")
    stats = router.get_expert_stats()
    print(json.dumps(stats, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(test_real_claude_router())

