"""
最簡MCP - 去掉所有複雜組件
流程: 請求 → 場景識別 → 拉專家 → 生成 → 聚合 → 回答
總代碼量: ~50行
"""

import asyncio
from typing import List, Dict

class UltraSimpleMCP:
    """超簡單MCP"""
    
    def __init__(self):
        # 專家提示詞庫
        self.experts = {
            "保險": "你是保險專家，分析: {request}",
            "技術": "你是技術專家，分析: {request}", 
            "商業": "你是商業專家，分析: {request}"
        }
    
    def identify(self, request: str) -> List[str]:
        """場景識別"""
        experts = []
        if any(w in request for w in ["保險", "核保", "保單"]): experts.append("保險")
        if any(w in request for w in ["自動化", "OCR", "系統"]): experts.append("技術") 
        if any(w in request for w in ["人力", "成本", "效率"]): experts.append("商業")
        return experts or ["保險"]
    
    async def ask_expert(self, expert: str, request: str) -> str:
        """問專家"""
        prompt = self.experts[expert].format(request=request)
        # 實際應該調用LLM API
        await asyncio.sleep(0.1)
        
        # 模擬回答
        answers = {
            "保險": "核保需3-5人/千件，自動化率60-70%，OCR審核0.5-1人月/千件",
            "技術": "OCR+AI可提升3-5倍效率，準確率95%+，成本節省30-40%", 
            "商業": "自動化可減少30%人力，1-2年回本，提升競爭優勢"
        }
        return f"【{expert}專家】{answers.get(expert, '專業分析...')}"
    
    def aggregate(self, answers: List[str]) -> str:
        """聚合答案"""
        if len(answers) == 1:
            return answers[0]
        return "\n\n".join(answers) + "\n\n【綜合建議】優化OCR技術，階段性自動化導入"
    
    async def process(self, request: str) -> str:
        """主流程"""
        experts = self.identify(request)                    # 場景識別
        answers = [await self.ask_expert(e, request) for e in experts]  # 拉專家
        return self.aggregate(answers)                      # 聚合答案

# 測試
async def test():
    mcp = UltraSimpleMCP()
    request = "臺銀人壽保單SOP要多少人力，自動化比率多高，OCR審核佔多少人月？"
    result = await mcp.process(request)
    print(result)

if __name__ == "__main__":
    asyncio.run(test())

