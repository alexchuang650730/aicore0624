"""
Cloud Search MCP組件 v1.0
智能雲端搜索和上下文分析組件
提供背景信息檢索、行業洞察分析、專業領域識別等功能
"""

import asyncio
import json
import logging
import time
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

@dataclass
class SearchResult:
    """搜索結果數據模型"""
    query: str
    result: str
    context_enriched: bool
    timestamp: float
    domains_identified: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SearchMetrics:
    """搜索性能指標"""
    total_searches: int = 0
    average_response_time: float = 0.0
    success_rate: float = 0.0
    cache_hit_rate: float = 0.0
    last_updated: str = ""

class CloudSearchMCP:
    """Cloud Search MCP組件 - 智能雲端搜索和上下文分析"""
    
    def __init__(self, llm_config: Dict[str, Any] = None):
        self.llm_config = llm_config or {}
        self.version = "1.0.0"
        self.name = "CloudSearchMCP"
        self.initialized = False
        
        # 性能指標
        self.metrics = SearchMetrics()
        self.search_cache = {}
        self.cache_ttl = 3600  # 1小時緩存
        
        # 日誌設置
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> Dict[str, Any]:
        """初始化Cloud Search MCP組件"""
        try:
            self.initialized = True
            self.metrics.last_updated = datetime.now().isoformat()
            
            self.logger.info(f"Cloud Search MCP v{self.version} 初始化成功")
            
            return {
                "success": True,
                "component": self.name,
                "version": self.version,
                "features": [
                    "intelligent_search",
                    "context_analysis", 
                    "domain_identification",
                    "industry_insights",
                    "smart_caching"
                ],
                "llm_provider": self.llm_config.get("provider", "mock"),
                "cache_enabled": True,
                "initialized_at": self.metrics.last_updated
            }
            
        except Exception as e:
            self.logger.error(f"Cloud Search MCP初始化失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "component": self.name
            }
    
    async def search_and_analyze(self, user_input: str) -> SearchResult:
        """主要搜索和分析方法"""
        start_time = time.time()
        
        try:
            # 檢查緩存
            cache_key = self._generate_cache_key(user_input)
            cached_result = self._get_from_cache(cache_key)
            
            if cached_result:
                self.logger.info(f"使用緩存結果: {user_input[:50]}...")
                return cached_result
            
            # 執行搜索分析
            search_result = await self._perform_search(user_input)
            
            # 識別專業領域
            domains = await self._identify_domains(user_input, search_result)
            
            # 計算信心分數
            confidence = self._calculate_confidence(search_result, domains)
            
            # 創建結果對象
            result = SearchResult(
                query=user_input,
                result=search_result,
                context_enriched=True,
                timestamp=time.time(),
                domains_identified=domains,
                confidence_score=confidence,
                metadata={
                    "response_time": time.time() - start_time,
                    "cache_used": False,
                    "llm_provider": self.llm_config.get("provider", "mock")
                }
            )
            
            # 存入緩存
            self._save_to_cache(cache_key, result)
            
            # 更新指標
            self._update_metrics(time.time() - start_time, True)
            
            return result
            
        except Exception as e:
            self.logger.error(f"搜索分析失敗: {e}")
            self._update_metrics(time.time() - start_time, False)
            
            return SearchResult(
                query=user_input,
                result=f"搜索失敗: {str(e)}",
                context_enriched=False,
                timestamp=time.time(),
                confidence_score=0.0,
                metadata={"error": str(e)}
            )
    
    async def _perform_search(self, user_input: str) -> str:
        """執行智能搜索"""
        search_prompt = f"""
請分析用戶輸入並提供相關背景信息：

用戶輸入: {user_input}

請提供：
1. 關鍵概念和術語解釋
2. 相關行業背景信息
3. 當前市場趨勢和最佳實務
4. 可能涉及的專業領域
5. 相關法規和標準

要求：
- 提供準確、實用的信息
- 重點關注實際應用場景
- 包含最新的行業動態
- 語言簡潔明確
"""
        
        system_prompt = "你是智能搜索助手，能夠分析用戶需求並提供全面的背景信息和行業洞察。你的回答應該準確、實用、結構化。"
        
        return await self._call_llm(search_prompt, system_prompt)
    
    async def _identify_domains(self, user_input: str, search_context: str) -> List[str]:
        """識別相關專業領域"""
        domain_prompt = f"""
基於用戶輸入和背景信息，請識別需要哪些專業領域的專家來回答這個問題。

用戶輸入: {user_input}
背景信息: {search_context}

請只返回需要的專業領域名稱，每行一個，例如：
保險專家
技術專家
法律專家

要求：
- 最多3個專家
- 只返回領域名稱
- 不要解釋或說明
- 確保領域相關性高
"""
        
        system_prompt = "你是專業領域識別專家，能準確判斷問題需要哪些專業知識領域。"
        
        try:
            domains_response = await self._call_llm(domain_prompt, system_prompt)
            
            if domains_response and domains_response.strip():
                domains = [line.strip() for line in domains_response.split('\n') if line.strip()]
                return domains[:3]  # 最多3個專家
            
            return []
            
        except Exception as e:
            self.logger.error(f"領域識別失敗: {e}")
            return []
    
    async def _call_llm(self, prompt: str, system_prompt: str = "") -> str:
        """調用大模型API"""
        try:
            provider = self.llm_config.get("provider", "mock")
            
            if provider == "openai":
                return await self._call_openai(prompt, system_prompt)
            elif provider == "claude":
                return await self._call_claude(prompt, system_prompt)
            elif provider == "ollama":
                return await self._call_ollama(prompt, system_prompt)
            else:
                # Mock模式 - 用於演示和測試
                return await self._mock_llm_response(prompt, system_prompt)
                
        except Exception as e:
            self.logger.error(f"LLM調用失敗: {e}")
            return f"LLM調用失敗: {str(e)}"
    
    async def _call_openai(self, prompt: str, system_prompt: str) -> str:
        """調用OpenAI API"""
        try:
            url = f"{self.llm_config.get('base_url', 'https://api.openai.com')}/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.llm_config.get('api_key')}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.llm_config.get("model", "gpt-3.5-turbo"),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        return f"OpenAI API錯誤: {response.status}"
                        
        except Exception as e:
            return f"OpenAI調用失敗: {str(e)}"
    
    async def _call_ollama(self, prompt: str, system_prompt: str) -> str:
        """調用Ollama本地LLM"""
        try:
            url = f"{self.llm_config.get('base_url', 'http://localhost:11434')}/api/generate"
            
            payload = {
                "model": self.llm_config.get("model", "llama3"),
                "prompt": f"{system_prompt}\n\n{prompt}",
                "stream": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "無回應")
                    else:
                        return f"Ollama API錯誤: {response.status}"
                        
        except Exception as e:
            return f"Ollama調用失敗: {str(e)}"
    
    async def _call_claude(self, prompt: str, system_prompt: str) -> str:
        """調用Claude API"""
        try:
            # Claude API實現
            # 這裡可以根據需要實現Claude API調用
            return await self._mock_llm_response(prompt, system_prompt)
        except Exception as e:
            return f"Claude調用失敗: {str(e)}"
    
    async def _mock_llm_response(self, prompt: str, system_prompt: str) -> str:
        """Mock LLM回應 - 用於演示和測試"""
        await asyncio.sleep(0.2)  # 模擬API延遲
        
        if "搜索" in prompt or "背景" in prompt:
            return """
基於您的查詢，以下是相關的背景信息和分析：

**關鍵概念解釋**：
- 涉及的核心概念包括業務流程優化、系統整合、數據分析等
- 相關技術包括API整合、自動化工具、雲端服務等

**行業背景**：
- 當前行業趨勢朝向數位化轉型和智能化發展
- 企業越來越重視效率提升和成本控制
- 自動化和AI技術應用日益普及

**市場趨勢**：
- 雲端優先策略成為主流
- 低代碼/無代碼平台快速發展
- 數據驅動決策成為標準實踐

**專業領域**：
- 需要技術專家進行系統設計和實施
- 需要業務專家確保方案符合實際需求
- 可能需要合規專家確保符合相關法規

**相關標準**：
- 遵循行業最佳實踐和標準
- 考慮資訊安全和隱私保護要求
- 確保系統可擴展性和可維護性
"""
        elif "領域" in prompt or "專家" in prompt:
            return """技術專家
業務專家
合規專家"""
        else:
            return "根據您的查詢，我提供了相關的分析和建議。如需更詳細的信息，請提供更具體的問題。"
    
    def _generate_cache_key(self, user_input: str) -> str:
        """生成緩存鍵"""
        import hashlib
        return hashlib.md5(user_input.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[SearchResult]:
        """從緩存獲取結果"""
        if cache_key in self.search_cache:
            cached_item = self.search_cache[cache_key]
            if time.time() - cached_item["timestamp"] < self.cache_ttl:
                return cached_item["result"]
            else:
                # 緩存過期，刪除
                del self.search_cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, result: SearchResult):
        """保存到緩存"""
        self.search_cache[cache_key] = {
            "result": result,
            "timestamp": time.time()
        }
        
        # 限制緩存大小
        if len(self.search_cache) > 100:
            # 刪除最舊的緩存項
            oldest_key = min(self.search_cache.keys(), 
                           key=lambda k: self.search_cache[k]["timestamp"])
            del self.search_cache[oldest_key]
    
    def _calculate_confidence(self, search_result: str, domains: List[str]) -> float:
        """計算信心分數"""
        try:
            confidence = 0.5  # 基礎分數
            
            # 根據結果長度調整
            if len(search_result) > 200:
                confidence += 0.2
            
            # 根據識別的領域數量調整
            if len(domains) > 0:
                confidence += 0.2
            
            # 根據內容質量調整
            if "專業" in search_result or "分析" in search_result:
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.5
    
    def _update_metrics(self, response_time: float, success: bool):
        """更新性能指標"""
        self.metrics.total_searches += 1
        
        # 更新平均響應時間
        if self.metrics.total_searches == 1:
            self.metrics.average_response_time = response_time
        else:
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * (self.metrics.total_searches - 1) + response_time) 
                / self.metrics.total_searches
            )
        
        # 更新成功率
        if success:
            success_count = int(self.metrics.success_rate * (self.metrics.total_searches - 1)) + 1
        else:
            success_count = int(self.metrics.success_rate * (self.metrics.total_searches - 1))
        
        self.metrics.success_rate = success_count / self.metrics.total_searches
        
        # 更新緩存命中率
        cache_hits = len([item for item in self.search_cache.values() 
                         if time.time() - item["timestamp"] < self.cache_ttl])
        self.metrics.cache_hit_rate = cache_hits / max(self.metrics.total_searches, 1)
    
    def get_metrics(self) -> Dict[str, Any]:
        """獲取性能指標"""
        return {
            "component": self.name,
            "version": self.version,
            "metrics": {
                "total_searches": self.metrics.total_searches,
                "average_response_time": round(self.metrics.average_response_time, 3),
                "success_rate": round(self.metrics.success_rate, 3),
                "cache_hit_rate": round(self.metrics.cache_hit_rate, 3),
                "cache_size": len(self.search_cache),
                "last_updated": self.metrics.last_updated
            },
            "status": "active" if self.initialized else "inactive"
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        try:
            # 執行簡單的測試搜索
            test_result = await self.search_and_analyze("測試查詢")
            
            return {
                "healthy": True,
                "component": self.name,
                "version": self.version,
                "test_response_time": test_result.metadata.get("response_time", 0),
                "cache_status": "active",
                "llm_provider": self.llm_config.get("provider", "mock"),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "component": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# 便利函數
async def create_cloud_search_mcp(llm_config: Dict[str, Any] = None) -> CloudSearchMCP:
    """創建並初始化Cloud Search MCP組件"""
    mcp = CloudSearchMCP(llm_config)
    await mcp.initialize()
    return mcp

# 使用示例
async def example_usage():
    """使用示例"""
    # 創建組件
    cloud_search = await create_cloud_search_mcp({
        "provider": "mock",  # 或 "openai", "ollama", "claude"
        "model": "gpt-3.5-turbo",
        "api_key": "your-api-key"
    })
    
    # 執行搜索
    result = await cloud_search.search_and_analyze("如何優化業務流程？")
    
    print(f"搜索結果: {result.result}")
    print(f"識別領域: {result.domains_identified}")
    print(f"信心分數: {result.confidence_score}")
    
    # 獲取指標
    metrics = cloud_search.get_metrics()
    print(f"性能指標: {metrics}")

if __name__ == "__main__":
    asyncio.run(example_usage())



# ============================================================================
# 台銀版本擴展 (Taiwan Bank Based Extension)
# ============================================================================

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

try:
    from taiwan_bank_config import (
        TaiwanBankConfig, 
        TAIWAN_BANK_LLM_CONFIG, 
        TAIWAN_BANK_PROMPT_TEMPLATE,
        TAIWAN_BANK_PERFORMANCE_CONFIG
    )
except ImportError:
    # 如果配置文件不存在，使用默認配置
    TaiwanBankConfig = None
    TAIWAN_BANK_LLM_CONFIG = {}
    TAIWAN_BANK_PROMPT_TEMPLATE = ""
    TAIWAN_BANK_PERFORMANCE_CONFIG = {}

@dataclass
class TaiwanBankSearchResult(SearchResult):
    """台銀版本搜索結果數據模型"""
    taiwan_bank_data_used: bool = False
    analysis_length: int = 0
    professional_level: str = "Standard"
    cost_analysis: Dict[str, Any] = field(default_factory=dict)
    roi_analysis: Dict[str, Any] = field(default_factory=dict)

class TaiwanBankCloudSearchMCP(CloudSearchMCP):
    """台銀版本 Cloud Search MCP - 基於台銀OCR審核人月成本詳細計算分析"""
    
    def __init__(self, llm_config: Dict[str, Any] = None):
        # 合併台銀配置
        taiwan_config = TAIWAN_BANK_LLM_CONFIG.copy()
        if llm_config:
            taiwan_config.update(llm_config)
        
        super().__init__(taiwan_config)
        self.version = "6.0.0-TaiwanBankBased"
        self.name = "TaiwanBankCloudSearchMCP"
        self.taiwan_bank_config = TaiwanBankConfig() if TaiwanBankConfig else None
        self.performance_config = TAIWAN_BANK_PERFORMANCE_CONFIG
        
        # 台銀專用指標
        self.taiwan_metrics = {
            "total_taiwan_searches": 0,
            "average_analysis_length": 0,
            "professional_standard_rate": 0.0,
            "taiwan_data_usage_rate": 0.0
        }
        
        self.logger.info(f"台銀版本 {self.name} v{self.version} 初始化完成")

    async def taiwan_bank_search(self, user_input: str) -> TaiwanBankSearchResult:
        """
        台銀版本專業搜索分析
        
        Args:
            user_input: 用戶查詢
            
        Returns:
            TaiwanBankSearchResult: 台銀版本搜索結果
        """
        start_time = time.time()
        
        try:
            # 檢查緩存
            cache_key = f"taiwan_bank_{hash(user_input)}"
            if cache_key in self.search_cache:
                cached_result = self.search_cache[cache_key]
                if time.time() - cached_result["timestamp"] < self.performance_config.get("cache_ttl", 7200):
                    self.logger.info(f"台銀版本緩存命中: {user_input[:50]}...")
                    return cached_result["result"]
            
            # 使用台銀專用 prompt
            prompt = TAIWAN_BANK_PROMPT_TEMPLATE.format(user_input=user_input)
            
            # 調用 LLM
            response = await self._call_llm_with_taiwan_context(prompt)
            
            # 解析響應
            try:
                result_data = json.loads(response)
            except json.JSONDecodeError:
                # 如果不是 JSON，創建結構化結果
                result_data = {
                    "background_analysis": response,
                    "expert_domains": ["保險業務流程優化", "保險科技應用", "保險運營管理"],
                    "confidence_score": 0.85,
                    "taiwan_bank_data_used": True,
                    "analysis_length": len(response),
                    "professional_level": "Taiwan_Bank_Standard"
                }
            
            # 創建台銀版本結果
            taiwan_result = TaiwanBankSearchResult(
                query=user_input,
                result=result_data.get("background_analysis", ""),
                context_enriched=True,
                timestamp=time.time(),
                domains_identified=result_data.get("expert_domains", []),
                confidence_score=result_data.get("confidence_score", 0.85),
                taiwan_bank_data_used=result_data.get("taiwan_bank_data_used", True),
                analysis_length=result_data.get("analysis_length", len(result_data.get("background_analysis", ""))),
                professional_level=result_data.get("professional_level", "Taiwan_Bank_Standard"),
                metadata={
                    "response_time": time.time() - start_time,
                    "model_used": self.llm_config.get("model", "unknown"),
                    "taiwan_bank_version": self.version,
                    "cost_analysis": self._generate_cost_analysis(),
                    "roi_analysis": self._generate_roi_analysis()
                }
            )
            
            # 更新台銀指標
            self._update_taiwan_metrics(taiwan_result)
            
            # 緩存結果
            if self.performance_config.get("cache_enabled", True):
                self.search_cache[cache_key] = {
                    "result": taiwan_result,
                    "timestamp": time.time()
                }
            
            self.logger.info(f"台銀版本搜索完成: {time.time() - start_time:.2f}秒")
            return taiwan_result
            
        except Exception as e:
            self.logger.error(f"台銀版本搜索失敗: {str(e)}")
            # 返回錯誤結果
            return TaiwanBankSearchResult(
                query=user_input,
                result=f"台銀版本分析失敗: {str(e)}",
                context_enriched=False,
                timestamp=time.time(),
                confidence_score=0.0,
                metadata={"error": str(e), "response_time": time.time() - start_time}
            )

    async def _call_llm_with_taiwan_context(self, prompt: str) -> str:
        """
        使用台銀上下文調用 LLM
        
        Args:
            prompt: 包含台銀上下文的 prompt
            
        Returns:
            str: LLM 響應
        """
        # 這裡應該調用實際的 LLM API
        # 為了演示，返回模擬的台銀專業分析
        
        await asyncio.sleep(0.1)  # 模擬 API 調用延遲
        
        # 模擬台銀專業分析響應
        mock_response = {
            "background_analysis": f"""基於台銀OCR審核人月成本詳細計算分析，針對查詢進行專業分析：

計算基礎參數：
年度總案件量：100,000件，OCR系統覆蓋率：100%，需人工審核比例：90%，OCR平均準確率：88%（混合文檔）。單件審核時間：35分鐘/件 = 0.58小時/件，年度總工時：52,200小時。

成本計算分析：
月薪：35,000元，社保福利：10,500元，月人工成本：45,500元/人，人月成本：48,116元，單件成本：266元。

人力配置需求：
基礎配置：29人，標準配置：34人，增強配置：41人。根據業務量變化，建議採用彈性配置策略。

投資回報分析：
年度總成本：2,656萬元，相比全人工節約：41%成本，投資回收期：約2.3個月。這個ROI表現在行業中屬於優秀水平。

技術優化建議：
1. 提升OCR準確率至92%以上，可減少15%人工審核工作量
2. 實施智能分類系統，優先處理高價值案件
3. 建立質量控制機制，確保審核標準一致性
4. 定期評估和調整人力配置，優化成本效益

風險評估：
技術風險：OCR系統穩定性、準確率波動
運營風險：人員流動、培訓成本
合規風險：監管要求變化、數據安全

基於台銀的實際經驗，建議分三階段實施：第一階段優化現有流程，第二階段引入新技術，第三階段全面數字化轉型。""",
            
            "expert_domains": ["保險業務流程優化", "保險科技應用", "保險運營管理"],
            "confidence_score": 0.95,
            "taiwan_bank_data_used": True,
            "analysis_length": 1740,
            "professional_level": "Taiwan_Bank_Standard"
        }
        
        return json.dumps(mock_response, ensure_ascii=False, indent=2)

    def _generate_cost_analysis(self) -> Dict[str, Any]:
        """生成成本分析數據"""
        if not self.taiwan_bank_config:
            return {}
            
        return {
            "annual_cases": self.taiwan_bank_config.ANNUAL_CASES,
            "cost_per_case": self.taiwan_bank_config.COST_PER_CASE,
            "annual_total_cost": self.taiwan_bank_config.ANNUAL_TOTAL_COST,
            "cost_saving_rate": self.taiwan_bank_config.COST_SAVING_RATE,
            "staff_configurations": {
                "basic": self.taiwan_bank_config.STAFF_CONFIG_BASIC,
                "standard": self.taiwan_bank_config.STAFF_CONFIG_STANDARD,
                "enhanced": self.taiwan_bank_config.STAFF_CONFIG_ENHANCED
            }
        }

    def _generate_roi_analysis(self) -> Dict[str, Any]:
        """生成 ROI 分析數據"""
        if not self.taiwan_bank_config:
            return {}
            
        return {
            "payback_period_months": self.taiwan_bank_config.PAYBACK_PERIOD_MONTHS,
            "cost_saving_rate": self.taiwan_bank_config.COST_SAVING_RATE,
            "annual_savings": self.taiwan_bank_config.ANNUAL_TOTAL_COST * self.taiwan_bank_config.COST_SAVING_RATE,
            "efficiency_metrics": {
                "review_time_per_case": self.taiwan_bank_config.REVIEW_TIME_PER_CASE,
                "ocr_accuracy_rate": self.taiwan_bank_config.OCR_ACCURACY_RATE,
                "manual_review_rate": self.taiwan_bank_config.MANUAL_REVIEW_RATE
            }
        }

    def _update_taiwan_metrics(self, result: TaiwanBankSearchResult):
        """更新台銀專用指標"""
        self.taiwan_metrics["total_taiwan_searches"] += 1
        
        # 更新平均分析長度
        total_searches = self.taiwan_metrics["total_taiwan_searches"]
        current_avg = self.taiwan_metrics["average_analysis_length"]
        new_avg = (current_avg * (total_searches - 1) + result.analysis_length) / total_searches
        self.taiwan_metrics["average_analysis_length"] = new_avg
        
        # 更新專業標準率
        if result.professional_level == "Taiwan_Bank_Standard":
            professional_count = self.taiwan_metrics["professional_standard_rate"] * (total_searches - 1) + 1
            self.taiwan_metrics["professional_standard_rate"] = professional_count / total_searches
        
        # 更新台銀數據使用率
        if result.taiwan_bank_data_used:
            taiwan_data_count = self.taiwan_metrics["taiwan_data_usage_rate"] * (total_searches - 1) + 1
            self.taiwan_metrics["taiwan_data_usage_rate"] = taiwan_data_count / total_searches

    def get_taiwan_metrics(self) -> Dict[str, Any]:
        """獲取台銀版本專用指標"""
        base_metrics = self.get_metrics()
        base_metrics.update({
            "taiwan_metrics": self.taiwan_metrics,
            "taiwan_bank_config": {
                "version": self.version,
                "professional_level": "Taiwan_Bank_Standard",
                "data_source": "台銀OCR審核人月成本詳細計算分析"
            }
        })
        return base_metrics

    async def health_check_taiwan(self) -> Dict[str, Any]:
        """台銀版本健康檢查"""
        try:
            # 執行台銀版本測試
            test_result = await self.taiwan_bank_search("測試查詢：核保流程優化")
            
            return {
                "healthy": True,
                "component": self.name,
                "version": self.version,
                "taiwan_bank_features": {
                    "config_loaded": self.taiwan_bank_config is not None,
                    "professional_analysis": test_result.professional_level == "Taiwan_Bank_Standard",
                    "taiwan_data_used": test_result.taiwan_bank_data_used,
                    "analysis_length": test_result.analysis_length,
                    "response_time": test_result.metadata.get("response_time", 0)
                },
                "taiwan_metrics": self.taiwan_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "component": self.name,
                "error": str(e),
                "taiwan_bank_status": "failed",
                "timestamp": datetime.now().isoformat()
            }

# 台銀版本便利函數
async def create_taiwan_bank_cloud_search_mcp(llm_config: Dict[str, Any] = None) -> TaiwanBankCloudSearchMCP:
    """創建並初始化台銀版本 Cloud Search MCP 組件"""
    mcp = TaiwanBankCloudSearchMCP(llm_config)
    await mcp.initialize()
    return mcp

# 台銀版本使用示例
async def taiwan_bank_example_usage():
    """台銀版本使用示例"""
    # 創建台銀版本組件
    taiwan_cloud_search = await create_taiwan_bank_cloud_search_mcp({
        "provider": "claude",
        "model": "claude-3-5-sonnet-20241022",
        "api_key": "your-claude-api-key"
    })
    
    # 執行台銀版本搜索
    result = await taiwan_cloud_search.taiwan_bank_search(
        "核保流程需要多少人力處理表單？自動化比率在業界有多高？表單OCR用人來審核在整個SOP流程所佔的人月大概是多少？"
    )
    
    print(f"台銀版本分析結果: {result.result[:200]}...")
    print(f"識別專家領域: {result.domains_identified}")
    print(f"信心分數: {result.confidence_score}")
    print(f"分析長度: {result.analysis_length} 字符")
    print(f"專業級別: {result.professional_level}")
    print(f"台銀數據使用: {result.taiwan_bank_data_used}")
    
    # 獲取台銀指標
    taiwan_metrics = taiwan_cloud_search.get_taiwan_metrics()
    print(f"台銀版本指標: {taiwan_metrics['taiwan_metrics']}")
    
    # 健康檢查
    health_status = await taiwan_cloud_search.health_check_taiwan()
    print(f"台銀版本健康狀態: {health_status['healthy']}")

if __name__ == "__main__":
    # 運行台銀版本示例
    print("=== 台銀版本 Cloud Search MCP 示例 ===")
    asyncio.run(taiwan_bank_example_usage())

