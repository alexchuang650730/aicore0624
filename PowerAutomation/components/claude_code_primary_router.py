#!/usr/bin/env python3
"""
Claude Code 前置場景識別路由器
移除傳統智慧路由，讓 Claude Code 直接處理和分析所有請求
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

@dataclass
class ScenarioAnalysis:
    """場景分析結果"""
    scenario_type: str  # 場景類型
    complexity_level: str  # 複雜度等級 (low/medium/high/expert)
    content_size: str  # 內容大小 (small/medium/large/massive)
    technical_domains: List[str]  # 技術領域
    recommended_approach: str  # 推薦處理方式
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

class ClaudeCodePrimaryRouter:
    """Claude Code 前置場景識別路由器"""
    
    def __init__(self):
        self.claude_code_endpoint = "http://127.0.0.1:8000/api/claude_code/analyze"
        self.processing_history: List[ProcessingRequest] = []
        
    async def analyze_and_route(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        使用 Claude Code 進行場景分析和路由決策
        
        Args:
            user_input: 用戶輸入
            context: 上下文信息
            
        Returns:
            處理結果和路由決策
        """
        request_id = str(uuid.uuid4())
        request = ProcessingRequest(
            request_id=request_id,
            user_input=user_input,
            context=context or {},
            timestamp=datetime.now()
        )
        
        try:
            # 第一階段：Claude Code 場景分析
            scenario_analysis = await self._claude_code_scenario_analysis(user_input, context)
            request.scenario_analysis = scenario_analysis
            
            # 第二階段：基於分析結果決定處理策略
            processing_result = await self._execute_processing_strategy(request)
            
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
    
    async def _claude_code_scenario_analysis(self, user_input: str, context: Dict[str, Any]) -> ScenarioAnalysis:
        """
        使用 Claude Code 進行深度場景分析
        利用 200K tokens 上下文窗口進行完整分析
        """
        
        analysis_prompt = f"""
        請分析以下用戶請求，提供詳細的場景識別和處理建議：

        用戶輸入：
        {user_input}

        上下文信息：
        {json.dumps(context, ensure_ascii=False, indent=2)}

        請提供以下分析：
        1. 場景類型識別 (代碼分析/需求分析/架構設計/問題診斷/其他)
        2. 複雜度等級評估 (low/medium/high/expert)
        3. 內容大小評估 (small/medium/large/massive)
        4. 涉及的技術領域
        5. 推薦的處理方式
        6. 上下文需求分析
        7. 信心度評分 (0-1)
        8. 詳細的分析推理過程

        請以 JSON 格式回應。
        """
        
        # 模擬 Claude Code API 調用
        # 在實際實施中，這裡會調用真實的 Claude Code API
        analysis_result = await self._mock_claude_code_api(analysis_prompt)
        
        return ScenarioAnalysis(
            scenario_type=analysis_result.get("scenario_type", "general"),
            complexity_level=analysis_result.get("complexity_level", "medium"),
            content_size=analysis_result.get("content_size", "medium"),
            technical_domains=analysis_result.get("technical_domains", []),
            recommended_approach=analysis_result.get("recommended_approach", "claude_code_direct"),
            context_requirements=analysis_result.get("context_requirements", {}),
            confidence_score=analysis_result.get("confidence_score", 0.8),
            analysis_reasoning=analysis_result.get("analysis_reasoning", "基於內容分析的推理")
        )
    
    async def _execute_processing_strategy(self, request: ProcessingRequest) -> Dict[str, Any]:
        """
        基於場景分析結果執行處理策略
        """
        analysis = request.scenario_analysis
        
        if analysis.content_size in ["large", "massive"] or analysis.complexity_level == "expert":
            # 大型內容或專家級複雜度 -> 直接使用 Claude Code
            return await self._claude_code_direct_processing(request)
        
        elif analysis.scenario_type == "code_analysis":
            # 代碼分析場景 -> Claude Code 優先
            return await self._claude_code_direct_processing(request)
        
        elif analysis.recommended_approach == "claude_code_direct":
            # Claude Code 推薦直接處理
            return await self._claude_code_direct_processing(request)
        
        else:
            # 其他場景也使用 Claude Code，但可以考慮輕量級處理
            return await self._claude_code_direct_processing(request)
    
    async def _claude_code_direct_processing(self, request: ProcessingRequest) -> Dict[str, Any]:
        """
        Claude Code 直接處理
        充分利用 200K tokens 上下文窗口
        """
        
        processing_prompt = f"""
        基於以下場景分析，請處理用戶請求：

        場景分析：
        {json.dumps(asdict(request.scenario_analysis), ensure_ascii=False, indent=2)}

        用戶請求：
        {request.user_input}

        上下文：
        {json.dumps(request.context, ensure_ascii=False, indent=2)}

        請提供詳細的分析和解決方案。
        """
        
        # 調用 Claude Code API 進行處理
        result = await self._mock_claude_code_api(processing_prompt)
        
        return {
            "processing_method": "claude_code_direct",
            "result": result,
            "context_used": len(processing_prompt),
            "processing_time": datetime.now().isoformat()
        }
    
    async def _mock_claude_code_api(self, prompt: str) -> Dict[str, Any]:
        """
        模擬 Claude Code API 調用
        在實際實施中會替換為真實的 API 調用
        """
        # 模擬 API 延遲
        await asyncio.sleep(0.1)
        
        # 基於 prompt 內容生成模擬回應
        if "場景識別" in prompt:
            return {
                "scenario_type": "code_analysis",
                "complexity_level": "high",
                "content_size": "large",
                "technical_domains": ["python", "architecture", "api_design"],
                "recommended_approach": "claude_code_direct",
                "context_requirements": {
                    "full_context_needed": True,
                    "technical_depth": "expert"
                },
                "confidence_score": 0.92,
                "analysis_reasoning": "基於內容複雜度和技術深度，建議使用 Claude Code 直接處理以充分利用 200K tokens 上下文窗口"
            }
        else:
            return {
                "analysis": "詳細的技術分析結果",
                "recommendations": ["建議1", "建議2", "建議3"],
                "code_examples": "相關代碼示例",
                "next_steps": "後續步驟建議"
            }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """獲取處理統計信息"""
        if not self.processing_history:
            return {"total_requests": 0}
        
        scenario_types = [req.scenario_analysis.scenario_type for req in self.processing_history if req.scenario_analysis]
        complexity_levels = [req.scenario_analysis.complexity_level for req in self.processing_history if req.scenario_analysis]
        
        return {
            "total_requests": len(self.processing_history),
            "scenario_distribution": {scenario: scenario_types.count(scenario) for scenario in set(scenario_types)},
            "complexity_distribution": {level: complexity_levels.count(level) for level in set(complexity_levels)},
            "average_confidence": sum(req.scenario_analysis.confidence_score for req in self.processing_history if req.scenario_analysis) / len([req for req in self.processing_history if req.scenario_analysis])
        }

# 測試函數
async def test_claude_code_router():
    """測試 Claude Code 前置路由器"""
    router = ClaudeCodePrimaryRouter()
    
    test_cases = [
        {
            "input": "幫我分析這個 Python 項目的架構，包含 50 個文件，總共 10000 行代碼",
            "context": {"project_size": "large", "language": "python"}
        },
        {
            "input": "如何優化 API 響應時間？",
            "context": {"current_response_time": "2s", "target": "500ms"}
        },
        {
            "input": "設計一個微服務架構來處理高併發請求",
            "context": {"expected_qps": 10000, "current_architecture": "monolith"}
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n=== 測試案例 {i+1} ===")
        result = await router.analyze_and_route(test_case["input"], test_case["context"])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print(f"\n=== 處理統計 ===")
    stats = router.get_processing_stats()
    print(json.dumps(stats, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(test_claude_code_router())

