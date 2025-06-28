"""
參數化專家MCP - 完全可配置
"""

class ParameterizedMCP:
    def __init__(self, experts):
        self.experts = experts
    
    def identify(self, request):
        """識別需要的專家"""
        return [expert for expert in self.experts.keys() if expert in request]
    
    async def ask_expert(self, expert, request):
        """問專家"""
        prompt = self.experts[expert].format(request=request)
        # 實際調用LLM
        return f"【{expert}專家】基於'{prompt}'的分析結果"
    
    async def process(self, request):
        """處理請求"""
        needed_experts = self.identify(request) or [list(self.experts.keys())[0]]
        answers = [await self.ask_expert(expert, request) for expert in needed_experts]
        return "\n".join(answers)

# 使用示例
import asyncio

async def test():
    # 保險業配置
    insurance_experts = {
        "保險": "你是保險專家，分析: {request}",
        "行政": "你是行政專家，分析: {request}", 
        "核保": "你是核保專家，分析: {request}",
        "理賠": "你是理賠專家，分析: {request}"
    }
    
    mcp = ParameterizedMCP(insurance_experts)
    
    request = "臺銀人壽保單行政作業核保流程分析"
    result = await mcp.process(request)
    print(result)

if __name__ == "__main__":
    asyncio.run(test())

