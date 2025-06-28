"""
Agent Core - 智能決策中心
完全基於Cloud Search MCP，零硬編碼
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import aiohttp


@dataclass
class DecisionContext:
    """決策上下文"""
    request: str
    domain: Optional[str] = None
    priority: str = "medium"
    budget_limit: Optional[float] = None
    quality_threshold: float = 0.8
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DecisionResult:
    """決策結果"""
    success: bool
    confidence: float
    expert_domains: List[str]
    search_results: List[Dict[str, Any]]
    expert_responses: Dict[str, str]
    final_answer: str
    execution_time: float
    cost_estimate: float
    quality_score: float
    error: Optional[str] = None


class CloudSearchMCPClient:
    """Cloud Search MCP客戶端 - 真正的API調用"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.cloudsearch.mcp"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
    
    async def _get_session(self):
        """獲取HTTP會話"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self.session
    
    async def search(self, query: str, domain: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """真正的搜索API調用"""
        session = await self._get_session()
        
        payload = {
            "query": query,
            "limit": limit,
            "include_metadata": True
        }
        
        if domain:
            payload["domain_filter"] = domain
        
        try:
            async with session.post(f"{self.base_url}/search", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("results", [])
                else:
                    error_text = await response.text()
                    raise Exception(f"Search API failed: {response.status} - {error_text}")
        
        except aiohttp.ClientError as e:
            raise Exception(f"Network error during search: {str(e)}")
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")
    
    async def identify_experts(self, request: str, context: str = "") -> List[str]:
        """識別需要的專家領域"""
        session = await self._get_session()
        
        payload = {
            "task": "identify_experts",
            "request": request,
            "context": context,
            "max_experts": 3
        }
        
        try:
            async with session.post(f"{self.base_url}/analyze", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("expert_domains", [])
                else:
                    error_text = await response.text()
                    raise Exception(f"Expert identification failed: {response.status} - {error_text}")
        
        except aiohttp.ClientError as e:
            raise Exception(f"Network error during expert identification: {str(e)}")
        except Exception as e:
            raise Exception(f"Expert identification failed: {str(e)}")
    
    async def generate_expert_response(self, expert_domain: str, request: str, context: str = "") -> str:
        """生成專家回答"""
        session = await self._get_session()
        
        payload = {
            "task": "expert_response",
            "expert_domain": expert_domain,
            "request": request,
            "context": context,
            "response_format": "professional_analysis"
        }
        
        try:
            async with session.post(f"{self.base_url}/generate", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response", f"{expert_domain}專家分析中...")
                else:
                    error_text = await response.text()
                    raise Exception(f"Expert response generation failed: {response.status} - {error_text}")
        
        except aiohttp.ClientError as e:
            raise Exception(f"Network error during response generation: {str(e)}")
        except Exception as e:
            raise Exception(f"Response generation failed: {str(e)}")
    
    async def aggregate_responses(self, expert_responses: Dict[str, str], request: str) -> str:
        """聚合多專家回答"""
        session = await self._get_session()
        
        payload = {
            "task": "aggregate_responses",
            "expert_responses": expert_responses,
            "original_request": request,
            "format": "comprehensive_summary"
        }
        
        try:
            async with session.post(f"{self.base_url}/aggregate", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("aggregated_response", "專家回答聚合中...")
                else:
                    error_text = await response.text()
                    raise Exception(f"Response aggregation failed: {response.status} - {error_text}")
        
        except aiohttp.ClientError as e:
            raise Exception(f"Network error during aggregation: {str(e)}")
        except Exception as e:
            raise Exception(f"Aggregation failed: {str(e)}")
    
    async def close(self):
        """關閉會話"""
        if self.session:
            await self.session.close()


class IntelligentAgentCore:
    """智能決策中心 - 完全基於Cloud Search MCP"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # 初始化Cloud Search MCP客戶端
        api_key = config.get("cloud_search_api_key")
        if not api_key:
            raise ValueError("Cloud Search MCP API key is required")
        
        self.mcp_client = CloudSearchMCPClient(
            api_key=api_key,
            base_url=config.get("cloud_search_base_url", "https://api.cloudsearch.mcp")
        )
        
        # 統計信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "mcp_calls": 0,
            "average_response_time": 0.0,
            "total_cost": 0.0
        }
    
    async def process_request(self, context: DecisionContext) -> DecisionResult:
        """處理請求 - 核心決策邏輯"""
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        try:
            # 階段1: 搜索背景信息
            search_results = await self._search_background_info(context)
            
            # 階段2: 識別專家領域
            expert_domains = await self._identify_expert_domains(context, search_results)
            
            # 階段3: 生成專家回答
            expert_responses = await self._generate_expert_responses(expert_domains, context, search_results)
            
            # 階段4: 聚合最終回答
            final_answer = await self._aggregate_final_answer(expert_responses, context)
            
            # 階段5: 質量評估
            quality_score = await self._evaluate_quality(final_answer, context)
            
            # 計算成本和執行時間
            execution_time = time.time() - start_time
            cost_estimate = self._calculate_cost(search_results, expert_responses)
            
            # 更新統計
            self.stats["successful_requests"] += 1
            self._update_average_response_time(execution_time)
            self.stats["total_cost"] += cost_estimate
            
            return DecisionResult(
                success=True,
                confidence=min(quality_score, 1.0),
                expert_domains=expert_domains,
                search_results=search_results,
                expert_responses=expert_responses,
                final_answer=final_answer,
                execution_time=execution_time,
                cost_estimate=cost_estimate,
                quality_score=quality_score
            )
        
        except Exception as e:
            self.stats["failed_requests"] += 1
            execution_time = time.time() - start_time
            
            return DecisionResult(
                success=False,
                confidence=0.0,
                expert_domains=[],
                search_results=[],
                expert_responses={},
                final_answer="",
                execution_time=execution_time,
                cost_estimate=0.0,
                quality_score=0.0,
                error=str(e)
            )
    
    async def _search_background_info(self, context: DecisionContext) -> List[Dict[str, Any]]:
        """搜索背景信息"""
        self.stats["mcp_calls"] += 1
        
        try:
            results = await self.mcp_client.search(
                query=context.request,
                domain=context.domain,
                limit=5
            )
            return results
        
        except Exception as e:
            # 如果搜索失敗，返回空結果而不是硬編碼內容
            raise Exception(f"Background search failed: {str(e)}")
    
    async def _identify_expert_domains(self, context: DecisionContext, search_results: List[Dict[str, Any]]) -> List[str]:
        """識別專家領域"""
        self.stats["mcp_calls"] += 1
        
        try:
            # 構建上下文信息
            search_context = ""
            if search_results:
                search_context = " ".join([result.get("content", "") for result in search_results[:3]])
            
            expert_domains = await self.mcp_client.identify_experts(
                request=context.request,
                context=search_context
            )
            
            return expert_domains if expert_domains else ["通用專家"]
        
        except Exception as e:
            raise Exception(f"Expert identification failed: {str(e)}")
    
    async def _generate_expert_responses(self, expert_domains: List[str], context: DecisionContext, search_results: List[Dict[str, Any]]) -> Dict[str, str]:
        """生成專家回答"""
        expert_responses = {}
        
        # 構建上下文信息
        search_context = ""
        if search_results:
            search_context = " ".join([result.get("content", "") for result in search_results])
        
        # 並行生成所有專家回答
        tasks = []
        for expert_domain in expert_domains:
            task = self._generate_single_expert_response(expert_domain, context, search_context)
            tasks.append(task)
        
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, response in enumerate(responses):
                expert_domain = expert_domains[i]
                if isinstance(response, Exception):
                    expert_responses[expert_domain] = f"{expert_domain}分析過程中遇到問題: {str(response)}"
                else:
                    expert_responses[expert_domain] = response
            
            return expert_responses
        
        except Exception as e:
            raise Exception(f"Expert response generation failed: {str(e)}")
    
    async def _generate_single_expert_response(self, expert_domain: str, context: DecisionContext, search_context: str) -> str:
        """生成單個專家回答"""
        self.stats["mcp_calls"] += 1
        
        try:
            response = await self.mcp_client.generate_expert_response(
                expert_domain=expert_domain,
                request=context.request,
                context=search_context
            )
            return response
        
        except Exception as e:
            raise Exception(f"{expert_domain} response generation failed: {str(e)}")
    
    async def _aggregate_final_answer(self, expert_responses: Dict[str, str], context: DecisionContext) -> str:
        """聚合最終回答"""
        self.stats["mcp_calls"] += 1
        
        try:
            if not expert_responses:
                raise Exception("No expert responses to aggregate")
            
            final_answer = await self.mcp_client.aggregate_responses(
                expert_responses=expert_responses,
                request=context.request
            )
            
            return final_answer
        
        except Exception as e:
            raise Exception(f"Response aggregation failed: {str(e)}")
    
    async def _evaluate_quality(self, final_answer: str, context: DecisionContext) -> float:
        """評估回答質量"""
        # 基本質量評估邏輯
        if not final_answer or len(final_answer.strip()) < 50:
            return 0.3
        
        # 檢查是否包含錯誤信息
        if "遇到問題" in final_answer or "失敗" in final_answer:
            return 0.5
        
        # 基於長度和內容豐富度評估
        length_score = min(len(final_answer) / 1000, 1.0)
        
        # 檢查是否包含具體數據或建議
        has_data = any(char.isdigit() for char in final_answer)
        has_recommendations = any(keyword in final_answer for keyword in ["建議", "推薦", "應該", "可以"])
        
        content_score = 0.6
        if has_data:
            content_score += 0.2
        if has_recommendations:
            content_score += 0.2
        
        return min((length_score + content_score) / 2, 1.0)
    
    def _calculate_cost(self, search_results: List[Dict[str, Any]], expert_responses: Dict[str, str]) -> float:
        """計算成本估算"""
        # 基本成本計算
        search_cost = len(search_results) * 0.01  # 每個搜索結果0.01
        response_cost = len(expert_responses) * 0.05  # 每個專家回答0.05
        
        return search_cost + response_cost
    
    def _update_average_response_time(self, execution_time: float):
        """更新平均響應時間"""
        total_requests = self.stats["successful_requests"]
        if total_requests == 1:
            self.stats["average_response_time"] = execution_time
        else:
            current_avg = self.stats["average_response_time"]
            self.stats["average_response_time"] = (current_avg * (total_requests - 1) + execution_time) / total_requests
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        success_rate = 0.0
        if self.stats["total_requests"] > 0:
            success_rate = self.stats["successful_requests"] / self.stats["total_requests"]
        
        return {
            **self.stats,
            "success_rate": success_rate,
            "mcp_integration": True
        }
    
    async def close(self):
        """關閉資源"""
        await self.mcp_client.close()


# 測試代碼
async def test_agent_core():
    """測試Agent Core"""
    config = {
        "cloud_search_api_key": "test_api_key_here",
        "cloud_search_base_url": "https://api.cloudsearch.mcp"
    }
    
    agent_core = IntelligentAgentCore(config)
    
    # 測試請求
    context = DecisionContext(
        request="我要開發一個貪吃蛇遊戲，需要什麼技術棧？",
        domain="game_development",
        priority="medium"
    )
    
    try:
        result = await agent_core.process_request(context)
        print(f"Success: {result.success}")
        print(f"Expert Domains: {result.expert_domains}")
        print(f"Final Answer: {result.final_answer}")
        print(f"Quality Score: {result.quality_score}")
        
    except Exception as e:
        print(f"Test failed: {e}")
    
    finally:
        await agent_core.close()


if __name__ == "__main__":
    asyncio.run(test_agent_core())

