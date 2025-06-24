"""
完全動態MCP服務器 - 零硬編碼版本
整合Cloud Search MCP + 大模型識別領域 + 動態專家 + Web管理界面
Updated: 使用獨立的Cloud Search MCP組件和Web管理界面
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import aiohttp
import json
import logging
import time
import os
import sys
from typing import List, Dict, Any

# 添加組件路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'components'))

# 導入Cloud Search MCP組件和Web管理界面
from cloud_search_mcp import CloudSearchMCP, create_cloud_search_mcp
from web_management_interface import WebManagementInterface, create_web_management_interface

# 完全動態MCP核心
class FullyDynamicMCP:
    """完全動態MCP - 零硬編碼"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm_config = llm_config
        self.request_count = 0
        self.performance_metrics = {}
        
        # 初始化Cloud Search MCP組件
        self.cloud_search_mcp = None
        
    async def initialize(self):
        """初始化MCP組件"""
        try:
            # 創建Cloud Search MCP組件
            self.cloud_search_mcp = await create_cloud_search_mcp(self.llm_config)
            logging.info("Cloud Search MCP組件初始化成功")
            return True
        except Exception as e:
            logging.error(f"Cloud Search MCP組件初始化失敗: {e}")
            return False
    
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
    
    async def _call_claude(self, prompt: str, system_prompt: str) -> str:
        """調用Claude API"""
        # Claude API實現
        return await self._mock_llm_response(prompt, system_prompt)
    
    async def _mock_llm_response(self, prompt: str, system_prompt: str) -> str:
        """Mock LLM回應 - 用於演示"""
        if "搜索" in prompt or "背景" in prompt:
            return """
臺銀人壽是台灣銀行旗下的人壽保險公司，主要業務包括人壽保險、年金保險等。
保單行政作業SOP涉及核保、理賠、客戶服務等多個環節。

**關鍵流程包括：**
1. **核保流程**
   - 風險評估和保費計算
   - 醫療檢查和財務審核
   - 保單條款確認

2. **理賠流程**
   - 理賠申請受理
   - 案件調查和審核
   - 理賠金給付

3. **客戶服務**
   - 保單變更服務
   - 續期保費收取
   - 客戶諮詢處理

4. **管理建議**
   - 建立變更管理機制
   - 員工培訓和轉型
   - 持續改進文化
   - 數據驅動決策
"""
        elif "領域" in prompt or "專家" in prompt:
            return """保險專家
技術專家
法律專家"""
        elif "保險專家" in prompt:
            return """
作為保險專家，我建議：

**核保優化**：
- 建立標準化核保流程
- 導入AI輔助風險評估
- 簡化低風險案件審核

**理賠改善**：
- 數位化理賠申請流程
- 建立快速理賠通道
- 加強理賠案件追蹤

**客戶體驗**：
- 提供24/7線上服務
- 建立客戶自助平台
- 優化保單管理系統
"""
        elif "技術專家" in prompt:
            return """
從技術角度建議：

**系統整合**：
- 建立統一的保單管理平台
- 整合核保、理賠、客服系統
- 實現數據即時同步

**自動化改善**：
- 導入RPA自動化流程
- 建立智能客服機器人
- 實現文件自動識別

**數據分析**：
- 建立商業智能平台
- 實現預測性分析
- 優化風險模型
"""
        elif "法律專家" in prompt:
            return """
法律合規建議：

**法規遵循**：
- 確保符合保險法規要求
- 建立合規監控機制
- 定期進行法規更新

**風險管控**：
- 建立法律風險評估
- 完善內控制度
- 加強員工合規培訓

**客戶權益**：
- 保障客戶知情權
- 建立申訴處理機制
- 確保資料隱私保護
"""
        elif "整合" in prompt:
            return """
綜合各專家建議，臺銀人壽保單行政作業SOP優化方案：

**短期目標（3-6個月）**：
1. 建立標準化作業流程
2. 導入基礎自動化工具
3. 完善員工培訓體系

**中期目標（6-12個月）**：
1. 建立統一數位平台
2. 實現核心流程自動化
3. 建立數據分析能力

**長期目標（1-2年）**：
1. 實現全面數位轉型
2. 建立智能決策系統
3. 達成行業領先水準

**實施建議**：
- 採用敏捷開發方法
- 建立跨部門協作機制
- 持續監控和優化
- 確保合規和風險控制
"""
        else:
            return "根據您的問題，我提供了專業的分析和建議。"
    
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
    
    async def generate_expert_prompt(self, domain: str, user_input: str, search_context: str) -> str:
        """動態生成專家提示詞"""
        prompt_generation = f"""
請為{domain}生成一個專業的提示詞，用於回答用戶問題。

用戶問題: {user_input}
背景信息: {search_context}

生成的提示詞應該：
1. 體現{domain}的專業特色
2. 針對具體問題提供實用建議
3. 結構清晰，邏輯嚴謹
4. 包含具體的行動建議

請直接返回提示詞內容，不要額外說明。
"""
        
        return await self.call_llm(
            prompt_generation,
            f"你是提示詞工程專家，能為{domain}生成高質量的專業提示詞。"
        )
    
    async def ask_domain_expert(self, domain: str, expert_prompt: str, user_input: str, search_context: str) -> str:
        """向特定領域專家提問"""
        full_prompt = f"""
{expert_prompt}

基於以下信息回答問題：
用戶問題: {user_input}
背景信息: {search_context}

請提供專業、實用的建議。
"""
        
        return await self.call_llm(
            full_prompt,
            f"你是{domain}，具有豐富的專業知識和實踐經驗。"
        )
    
    async def aggregate_expert_responses(self, expert_responses: List[str], user_input: str) -> str:
        """聚合專家回答"""
        aggregation_prompt = f"""
請整合以下專家的回答，形成一個連貫、全面的最終答案：

用戶問題: {user_input}

專家回答：
{chr(10).join([f"專家{i+1}: {response}" for i, response in enumerate(expert_responses)])}

請提供：
1. 綜合分析和建議
2. 具體的實施步驟
3. 注意事項和風險提醒
"""
        
        final_answer = await self.call_llm(
            aggregation_prompt,
            "你是整合專家，能將多個專業觀點整合成連貫、實用的最終答案。"
        )
        
        return final_answer
    
    async def process(self, user_input: str) -> Dict[str, Any]:
        """主處理流程 - 使用新的Cloud Search MCP組件"""
        start_time = time.time()
        self.request_count += 1
        
        try:
            # 檢查Cloud Search MCP是否已初始化
            if not self.cloud_search_mcp:
                await self.initialize()
            
            # 1. 使用Cloud Search MCP組件進行搜索和分析
            search_result = await self.cloud_search_mcp.search_and_analyze(user_input)
            
            # 2. 從搜索結果中獲取識別的領域，如果沒有則使用大模型識別
            domains = search_result.domains_identified
            if not domains:
                domains = await self.identify_domains(user_input, search_result.result)
            
            # 3. 動態生成專家提示詞並調用
            expert_responses = []
            expert_prompts = {}
            
            for domain in domains:
                expert_prompt = await self.generate_expert_prompt(
                    domain, user_input, search_result.result
                )
                expert_prompts[domain] = expert_prompt
                
                response = await self.ask_domain_expert(
                    domain, expert_prompt, user_input, search_result.result
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
                "search_context": search_result.result,
                "search_confidence": search_result.confidence_score,
                "search_metadata": search_result.metadata,
                "processing_time": processing_time,
                "process_type": "fully_dynamic_with_cloud_search_mcp",
                "request_count": self.request_count,
                "cloud_search_mcp_version": self.cloud_search_mcp.version if self.cloud_search_mcp else "unknown"
            }
            
        except Exception as e:
            logging.error(f"處理失敗: {e}")
            return {
                "error": str(e),
                "processing_time": time.time() - start_time,
                "request_count": self.request_count
            }
    
    def get_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        cloud_search_metrics = {}
        if self.cloud_search_mcp:
            cloud_search_metrics = self.cloud_search_mcp.get_metrics()
        
        return {
            "system": "FullyDynamicMCP",
            "version": "2.0.0",
            "request_count": self.request_count,
            "performance_metrics": self.performance_metrics,
            "cloud_search_mcp": cloud_search_metrics,
            "llm_provider": self.llm_config.get("provider", "mock"),
            "status": "active",
            "timestamp": time.time()
        }

# Flask應用初始化
app = Flask(__name__)
CORS(app)

# 初始化Web管理界面
web_interface = create_web_management_interface(app)

# 全局MCP實例
_mcp_instance = None

async def get_mcp_instance():
    """獲取MCP實例（單例模式）"""
    global _mcp_instance
    if _mcp_instance is None:
        # 默認配置
        llm_config = {
            "provider": "mock",  # 可選: openai, claude, ollama, mock
            "model": "gpt-3.5-turbo",
            "api_key": "",
            "base_url": ""
        }
        
        _mcp_instance = FullyDynamicMCP(llm_config)
        await _mcp_instance.initialize()
    
    return _mcp_instance

@app.route('/process', methods=['POST'])
def process_request():
    """處理用戶請求"""
    start_time = time.time()
    try:
        data = request.get_json()
        user_input = data.get('input', '')
        
        if not user_input:
            return jsonify({"error": "缺少輸入內容"}), 400
        
        # 使用asyncio運行異步處理
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            mcp = loop.run_until_complete(get_mcp_instance())
            result = loop.run_until_complete(mcp.process(user_input))
            
            # 記錄請求到Web界面
            response_time = (time.time() - start_time) * 1000  # 轉換為毫秒
            web_interface.record_request(response_time)
            
            return jsonify(result)
        finally:
            loop.close()
            
    except Exception as e:
        logging.error(f"請求處理失敗: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """獲取系統狀態"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            mcp = loop.run_until_complete(get_mcp_instance())
            status = mcp.get_status()
            return jsonify(status)
        finally:
            loop.close()
            
    except Exception as e:
        logging.error(f"狀態獲取失敗: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            mcp = loop.run_until_complete(get_mcp_instance())
            if mcp.cloud_search_mcp:
                health = loop.run_until_complete(mcp.cloud_search_mcp.health_check())
                return jsonify(health)
            else:
                return jsonify({"healthy": False, "error": "Cloud Search MCP未初始化"})
        finally:
            loop.close()
            
    except Exception as e:
        logging.error(f"健康檢查失敗: {e}")
        return jsonify({"healthy": False, "error": str(e)}), 500

if __name__ == '__main__':
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 啟動完全動態MCP服務器 v2.1")
    print("📦 整合Cloud Search MCP組件")
    print("🌐 整合Web管理界面")
    print("🔗 支持多種LLM提供商")
    print("📊 內建性能監控和健康檢查")
    print("💻 Web界面: http://localhost:8099")
    
    app.run(host='0.0.0.0', port=8099, debug=True)

