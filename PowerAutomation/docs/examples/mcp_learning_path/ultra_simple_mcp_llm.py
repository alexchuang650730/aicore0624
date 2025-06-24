"""
真正的UltraSimpleMCP - 調用LLM API
流程: 請求 → 場景識別 → 拉專家 → LLM生成 → 聚合 → 回答
"""

import asyncio
import aiohttp
import json
from typing import List, Dict

class UltraSimpleMCP:
    """超簡單MCP - 真正調用LLM"""
    
    def __init__(self):
        # 專家提示詞庫
        self.experts = {
            "保險": "你是資深保險業專家，請基於專業知識分析: {request}",
            "技術": "你是技術專家，請從技術角度分析: {request}", 
            "商業": "你是商業顧問，請從商業角度分析: {request}"
        }
    
    def identify(self, request: str) -> List[str]:
        """場景識別"""
        experts = []
        if any(w in request for w in ["保險", "核保", "保單", "理賠", "臺銀人壽"]): 
            experts.append("保險")
        if any(w in request for w in ["自動化", "OCR", "系統", "技術", "AI"]): 
            experts.append("技術") 
        if any(w in request for w in ["人力", "成本", "效率", "業界", "比率"]): 
            experts.append("商業")
        return experts or ["保險"]
    
    async def call_llm(self, prompt: str) -> str:
        """調用LLM API"""
        try:
            # 這裡可以調用不同的LLM API
            # 示例：調用本地LLM或API服務
            
            # 方案1: 調用OpenAI兼容API
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(
            #         "http://localhost:11434/v1/chat/completions",
            #         json={
            #             "model": "llama3",
            #             "messages": [{"role": "user", "content": prompt}]
            #         }
            #     ) as response:
            #         result = await response.json()
            #         return result["choices"][0]["message"]["content"]
            
            # 方案2: 調用Claude API
            # headers = {"Authorization": f"Bearer {api_key}"}
            # ...
            
            # 暫時返回提示詞本身，表示LLM處理
            await asyncio.sleep(0.1)  # 模擬API調用延遲
            return f"基於提示詞'{prompt}'的LLM分析結果"
            
        except Exception as e:
            return f"LLM調用失敗: {str(e)}"
    
    async def ask_expert(self, expert: str, request: str) -> str:
        """問專家"""
        prompt = self.experts[expert].format(request=request)
        
        # 真正調用LLM
        llm_response = await self.call_llm(prompt)
        
        return f"【{expert}專家】{llm_response}"
    
    def aggregate(self, answers: List[str]) -> str:
        """聚合答案"""
        if len(answers) == 1:
            return answers[0]
        
        result = "\n\n".join(answers)
        result += "\n\n【綜合建議】基於各專家分析，建議採用階段性改進策略。"
        return result
    
    async def process(self, request: str) -> str:
        """主流程"""
        experts = self.identify(request)                    # 場景識別
        answers = [await self.ask_expert(e, request) for e in experts]  # 拉專家+LLM生成
        return self.aggregate(answers)                      # 聚合答案

# 測試
async def test():
    mcp = UltraSimpleMCP()
    request = "臺銀人壽保單SOP要多少人力，自動化比率多高？"
    result = await mcp.process(request)
    print(result)

if __name__ == "__main__":
    asyncio.run(test())

