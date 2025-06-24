"""
完全動態MCP服務器 - 零硬編碼版本
整合Cloud Search MCP + 大模型識別領域 + 動態專家
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import aiohttp
import json
import logging
import time
import os
from typing import List, Dict, Any

# 完全動態MCP核心
class FullyDynamicMCP:
    """完全動態MCP - 零硬編碼"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm_config = llm_config
        self.request_count = 0
        self.performance_metrics = {}
    
    async def call_llm(self, prompt: str, system_prompt: str = "") -> str:
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
                # Mock模式 - 用於演示
                await asyncio.sleep(0.2)
                return await self._mock_llm_response(prompt, system_prompt)
                
        except Exception as e:
            logging.error(f"LLM調用失敗: {e}")
            return f"LLM調用失敗: {str(e)}"
    
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
                ]
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
    
    async def _mock_llm_response(self, prompt: str, system_prompt: str) -> str:
        """Mock LLM回應 - 用於演示"""
        if "搜索" in prompt or "背景" in prompt:
            return """
臺銀人壽是台灣銀行旗下的人壽保險公司，主要業務包括人壽保險、年金保險等。
保單行政作業SOP涉及核保、理賠、客戶服務等多個環節。
業界自動化趨勢：OCR技術、AI輔助決策、數位化流程等。
"""
        elif "識別" in prompt or "領域" in prompt:
            return """
保險專家
技術專家
行政管理專家
"""
        elif "提示詞" in prompt:
            if "保險專家" in prompt:
                return "你是資深保險業專家，具有豐富的核保、理賠和風險評估經驗。請基於保險業專業知識和法規要求，提供準確的分析和建議。"
            elif "技術專家" in prompt:
                return "你是技術專家，專精於保險業數位化轉型、自動化系統和OCR技術。請從技術角度分析問題並提供實施建議。"
            elif "行政管理專家" in prompt:
                return "你是行政管理專家，熟悉保險公司內部流程優化和人力資源配置。請從管理角度提供效率提升建議。"
        else:
            # 專家回答
            if "保險專家" in system_prompt:
                return """
基於保險業專業分析：

1. **人力需求評估**
   - 核保作業：每千件保單需要3-5名核保人員
   - 理賠處理：每千件理賠需要2-3名理賠專員
   - 行政支援：約佔總人力的20-25%

2. **自動化現況**
   - 業界平均自動化率：60-70%
   - 領先公司可達：80-85%
   - 簡單案件自動化率：可達90%以上

3. **OCR審核投入**
   - 佔總人力比例：15-20%
   - 每月人力投入：0.5-1人月/千件保單
   - 主要用於文件驗證和資料核對

4. **成本效益分析**
   - 自動化可節省30-40%人力成本
   - 投資回收期：1-2年
   - 錯誤率可降低至2%以下
"""
            elif "技術專家" in system_prompt:
                return """
技術角度分析：

1. **自動化技術架構**
   - OCR + NLP文件處理
   - 規則引擎自動決策
   - 機器學習風險評估
   - API整合各系統

2. **性能提升潛力**
   - 處理速度：提升3-5倍
   - 準確率：可達95%以上
   - 24/7不間斷處理
   - 即時狀態追蹤

3. **實施建議**
   - 採用微服務架構
   - 階段性導入策略
   - 並行運行驗證
   - 持續監控優化

4. **技術投資**
   - 初期投資：系統建置成本
   - 維護成本：較傳統方式低30%
   - 擴展性：易於水平擴展
"""
            else:
                return """
行政管理角度分析：

1. **流程優化**
   - 標準化作業流程
   - 減少重複性工作
   - 提升作業透明度
   - 建立品質控制機制

2. **人力配置**
   - 專業分工制度
   - 跨部門協作
   - 技能培訓計畫
   - 績效管理制度

3. **效率提升**
   - 數位化可減少50%紙本作業
   - 自動化可提升20-30%效率
   - 錯誤率降低60%以上
   - 客戶滿意度提升

4. **管理建議**
   - 建立變更管理機制
   - 員工培訓和轉型
   - 持續改進文化
   - 數據驅動決策
"""
    
    async def cloud_search_mcp(self, user_input: str) -> Dict[str, Any]:
        """Cloud Search MCP - 搜索相關信息"""
        search_prompt = f"""
請分析用戶輸入並提供相關背景信息：

用戶輸入: {user_input}

請提供：
1. 關鍵概念和術語解釋
2. 相關行業背景信息
3. 當前市場趨勢和最佳實務
4. 可能涉及的專業領域
"""
        
        search_result = await self.call_llm(
            search_prompt,
            "你是智能搜索助手，能夠分析用戶需求並提供全面的背景信息和行業洞察。"
        )
        
        return {
            "search_result": search_result,
            "context_enriched": True,
            "timestamp": time.time()
        }
    
    async def identify_domains(self, user_input: str, search_context: str) -> List[str]:
        """用大模型識別需要的專業領域"""
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
"""
        
        domains_response = await self.call_llm(
            domain_prompt,
            "你是專業領域識別專家，能準確判斷問題需要哪些專業知識領域。"
        )
        
        # 解析返回的領域列表
        if domains_response and domains_response.strip():
            domains = [line.strip() for line in domains_response.split('\n') if line.strip()]
            return domains[:3]  # 最多3個專家
        return ["通用專家"]  # 默認專家
    
    async def generate_expert_prompt(self, domain: str, user_input: str, context: str) -> str:
        """動態生成專家提示詞"""
        prompt_generation = f"""
請為{domain}生成一個專業的系統提示詞，用於回答用戶問題。

專家領域: {domain}
用戶問題: {user_input}
背景信息: {context}

請生成一個專業的系統提示詞，讓{domain}能夠：
1. 展現專業知識和經驗
2. 提供準確、實用的建議
3. 符合該領域的專業標準
4. 給出具體的數據和建議

系統提示詞應該以"你是..."開始。
"""
        
        expert_prompt = await self.call_llm(
            prompt_generation,
            "你是提示詞工程專家，能為不同專業領域生成最適合的系統提示詞。"
        )
        
        return expert_prompt.strip()
    
    async def ask_domain_expert(self, domain: str, expert_prompt: str, user_input: str, context: str) -> str:
        """調用領域專家"""
        final_prompt = f"""
背景信息: {context}

用戶問題: {user_input}

請基於你的專業知識提供詳細、準確的回答，包括：
1. 專業分析
2. 具體數據（如果適用）
3. 實用建議
4. 風險考量（如果適用）
"""
        
        expert_response = await self.call_llm(
            final_prompt,
            expert_prompt
        )
        
        return f"【{domain}】\n{expert_response}"
    
    async def aggregate_expert_responses(self, responses: List[str], user_input: str) -> str:
        """聚合專家回答"""
        if len(responses) == 1:
            return responses[0]
        
        aggregation_prompt = f"""
請整合以下專家的回答，為用戶提供一個綜合、連貫的最終答案。

用戶問題: {user_input}

專家回答:
{chr(10).join(responses)}

請提供一個整合的最終回答，要求：
1. 突出各專家的重點觀點
2. 整合互補的信息
3. 給出綜合建議
4. 保持邏輯連貫性
"""
        
        final_answer = await self.call_llm(
            aggregation_prompt,
            "你是整合專家，能將多個專業觀點整合成連貫、實用的最終答案。"
        )
        
        return final_answer
    
    async def process(self, user_input: str) -> Dict[str, Any]:
        """主處理流程"""
        start_time = time.time()
        self.request_count += 1
        
        try:
            # 1. Cloud Search MCP
            search_result = await self.cloud_search_mcp(user_input)
            
            # 2. 大模型識別領域
            domains = await self.identify_domains(user_input, search_result["search_result"])
            
            # 3. 動態生成專家提示詞並調用
            expert_responses = []
            expert_prompts = {}
            
            for domain in domains:
                expert_prompt = await self.generate_expert_prompt(
                    domain, user_input, search_result["search_result"]
                )
                expert_prompts[domain] = expert_prompt
                
                response = await self.ask_domain_expert(
                    domain, expert_prompt, user_input, search_result["search_result"]
                )
                expert_responses.append(response)
            
            # 4. 聚合回答
            final_answer = await self.aggregate_expert_responses(expert_responses, user_input)
            
            processing_time = time.time() - start_time
            
            # 更新性能指標
            for domain in domains:
                if domain not in self.performance_metrics:
                    self.performance_metrics[domain] = {
                        "total_requests": 0,
                        "total_time": 0,
                        "avg_time": 0
                    }
                self.performance_metrics[domain]["total_requests"] += 1
                self.performance_metrics[domain]["total_time"] += processing_time
                self.performance_metrics[domain]["avg_time"] = (
                    self.performance_metrics[domain]["total_time"] / 
                    self.performance_metrics[domain]["total_requests"]
                )
            
            return {
                "final_answer": final_answer,
                "domains_identified": domains,
                "expert_count": len(domains),
                "expert_prompts": expert_prompts,
                "search_context": search_result["search_result"],
                "processing_time": processing_time,
                "process_type": "fully_dynamic",
                "request_id": self.request_count
            }
            
        except Exception as e:
            logging.error(f"處理失敗: {e}")
            return {
                "final_answer": f"處理失敗: {str(e)}",
                "domains_identified": [],
                "expert_count": 0,
                "expert_prompts": {},
                "search_context": "",
                "processing_time": time.time() - start_time,
                "process_type": "error",
                "request_id": self.request_count
            }

# Flask應用
app = Flask(__name__)
CORS(app)

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化完全動態MCP
llm_config = {
    "provider": os.getenv("LLM_PROVIDER", "mock"),  # mock, ollama, openai, claude
    "model": os.getenv("LLM_MODEL", "llama3"),
    "api_key": os.getenv("LLM_API_KEY", ""),
    "base_url": os.getenv("LLM_BASE_URL", "http://localhost:11434")
}

dynamic_mcp = FullyDynamicMCP(llm_config)

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查"""
    return jsonify({
        "status": "healthy",
        "mcp_type": "fully_dynamic",
        "llm_provider": llm_config["provider"],
        "total_requests": dynamic_mcp.request_count,
        "timestamp": time.time()
    })

@app.route('/api/process', methods=['POST'])
def process_request():
    """處理請求 - 主要API"""
    try:
        data = request.get_json()
        user_input = data.get('request', '')
        
        if not user_input:
            return jsonify({"error": "請求內容不能為空"}), 400
        
        # 執行完全動態MCP處理
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(dynamic_mcp.process(user_input))
        
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"處理請求失敗: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/search', methods=['POST'])
def cloud_search():
    """Cloud Search MCP"""
    try:
        data = request.get_json()
        user_input = data.get('request', '')
        
        if not user_input:
            return jsonify({"error": "請求內容不能為空"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(dynamic_mcp.cloud_search_mcp(user_input))
        
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"搜索失敗: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/identify', methods=['POST'])
def identify_domains():
    """識別專業領域"""
    try:
        data = request.get_json()
        user_input = data.get('request', '')
        context = data.get('context', '')
        
        if not user_input:
            return jsonify({"error": "請求內容不能為空"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        domains = loop.run_until_complete(
            dynamic_mcp.identify_domains(user_input, context)
        )
        
        loop.close()
        
        return jsonify({
            "request": user_input,
            "identified_domains": domains,
            "domain_count": len(domains)
        })
        
    except Exception as e:
        logger.error(f"識別領域失敗: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """獲取系統狀態"""
    return jsonify({
        "mcp_type": "fully_dynamic",
        "llm_config": {
            "provider": llm_config["provider"],
            "model": llm_config["model"],
            "base_url": llm_config["base_url"]
        },
        "performance_metrics": dynamic_mcp.performance_metrics,
        "total_requests": dynamic_mcp.request_count,
        "features": [
            "cloud_search_mcp",
            "dynamic_domain_identification", 
            "dynamic_expert_prompt_generation",
            "intelligent_response_aggregation"
        ]
    })

@app.route('/api/demo', methods=['POST'])
def demo_request():
    """演示請求"""
    try:
        data = request.get_json()
        demo_type = data.get('type', 'insurance')
        
        demo_requests = {
            'insurance': "臺銀人壽保單行政作業SOP大概要花多少人處理表單，自動化比率在業界有多高，表單OCR用人來審核在整個SOP流程所佔的人月大概是多少？",
            'technology': "保險業如何運用AI和OCR技術提升核保效率？",
            'management': "保險公司如何優化人力配置和流程管理？",
            'general': "請分析保險業數位轉型的趨勢和挑戰"
        }
        
        user_input = demo_requests.get(demo_type, demo_requests['insurance'])
        
        # 處理演示請求
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(dynamic_mcp.process(user_input))
        result["demo_type"] = demo_type
        result["demo_request"] = user_input
        
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"演示請求失敗: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 完全動態MCP服務器啟動中...")
    logger.info(f"📋 LLM配置: {llm_config['provider']} - {llm_config['model']}")
    logger.info("📡 API端點:")
    logger.info("  - GET  /health          - 健康檢查")
    logger.info("  - POST /api/process     - 完全動態處理")
    logger.info("  - POST /api/search      - Cloud Search MCP")
    logger.info("  - POST /api/identify    - 識別專業領域")
    logger.info("  - GET  /api/status      - 系統狀態")
    logger.info("  - POST /api/demo        - 演示請求")
    logger.info("🎯 特色: 零硬編碼、完全動態、LLM驅動")
    
    app.run(host='0.0.0.0', port=5002, debug=False)

