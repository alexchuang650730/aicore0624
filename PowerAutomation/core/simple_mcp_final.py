"""
極簡MCP協同架構 - 無classifier版本
流程: 場景識別 → 動態專家 → 專家提示詞 → 生成回答 → 聚合答案
總代碼量: ~80行
"""

import asyncio
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class Expert:
    """專家定義"""
    name: str
    prompt: str

class SimpleMCP:
    """極簡MCP協同器"""
    
    def __init__(self):
        # 專家庫 - 可動態擴展
        self.experts = {
            "insurance": Expert(
                name="保險專家",
                prompt="你是保險業專家。請基於保險業專業知識分析: {request}"
            ),
            "tech": Expert(
                name="技術專家", 
                prompt="你是技術專家。請從技術角度分析: {request}"
            ),
            "business": Expert(
                name="商業專家",
                prompt="你是商業顧問。請從商業角度分析: {request}"
            )
        }
    
    def identify_scene(self, request: str) -> List[str]:
        """場景識別 - 簡單關鍵詞匹配"""
        needed_experts = []
        
        # 保險場景
        if any(word in request for word in ["保險", "核保", "理賠", "保單", "臺銀人壽"]):
            needed_experts.append("insurance")
        
        # 技術場景  
        if any(word in request for word in ["自動化", "OCR", "系統", "流程", "AI"]):
            needed_experts.append("tech")
            
        # 商業場景
        if any(word in request for word in ["人力", "成本", "效率", "業界", "比率"]):
            needed_experts.append("business")
        
        # 預設至少一個專家
        return needed_experts if needed_experts else ["insurance"]
    
    async def get_expert_answer(self, expert_id: str, request: str) -> str:
        """獲取專家回答"""
        expert = self.experts[expert_id]
        prompt = expert.prompt.format(request=request)
        
        # 模擬LLM調用 (實際應該調用Claude/Gemini)
        await asyncio.sleep(0.1)
        
        # 模擬專家回答
        if expert_id == "insurance":
            return """
【保險專家分析】
1. 人力需求: 核保作業約需3-5人/千件保單
2. 自動化率: 業界平均60-70%，簡單案件可達80%
3. OCR審核: 約佔15-20%人力，每月0.5-1人月/千件
4. 建議: 導入AI輔助決策，優化OCR準確率
"""
        elif expert_id == "tech":
            return """
【技術專家分析】  
1. 自動化技術: OCR+NLP文件處理，規則引擎決策
2. 性能提升: 處理速度可提升3-5倍，準確率95%+
3. 成本節省: 30-40%成本節省空間
4. 實施建議: 微服務架構，階段性導入
"""
        elif expert_id == "business":
            return """
【商業專家分析】
1. 人力配置: 傳統模式人力密集，自動化可減少30%人力
2. 投資回報: 自動化投資1-2年回本
3. 競爭優勢: 提升處理速度和客戶體驗
4. 風險管控: 保持人工審核關鍵環節
"""
        
        return f"【{expert.name}】: 針對請求的專業分析..."
    
    def aggregate_answers(self, expert_answers: Dict[str, str]) -> str:
        """聚合所有專家答案"""
        if len(expert_answers) == 1:
            return list(expert_answers.values())[0]
        
        # 多專家聚合
        result = "【多專家協同分析】\n\n"
        
        for expert_id, answer in expert_answers.items():
            expert_name = self.experts[expert_id].name
            result += f"## {expert_name}觀點\n{answer}\n\n"
        
        # 綜合結論
        result += """
## 綜合結論
整合各專家觀點，建議:
1. 優先提升OCR技術準確率至95%以上
2. 採用階段性自動化導入策略
3. 保持關鍵環節的人工審核
4. 預期1-2年內實現投資回報
"""
        return result
    
    async def process(self, request: str) -> Dict[str, Any]:
        """主處理流程"""
        # 1. 場景識別
        needed_experts = self.identify_scene(request)
        
        # 2. 動態拉取專家，生成回答
        expert_answers = {}
        for expert_id in needed_experts:
            answer = await self.get_expert_answer(expert_id, request)
            expert_answers[expert_id] = answer
        
        # 3. 聚合答案
        final_answer = self.aggregate_answers(expert_answers)
        
        return {
            "answer": final_answer,
            "experts_used": needed_experts,
            "expert_count": len(needed_experts)
        }

# 測試
async def test_simple_mcp():
    mcp = SimpleMCP()
    
    request = "臺銀人壽保單行政作業SOP大概要花多少人處理表單，自動化比率在業界有多高，表單OCR用人來審核在整個SOP流程所佔的人月大概是多少？"
    
    result = await mcp.process(request)
    
    print(f"使用專家: {result['experts_used']}")
    print(f"專家數量: {result['expert_count']}")
    print("\n" + "="*50)
    print(result['answer'])

if __name__ == "__main__":
    asyncio.run(test_simple_mcp())

