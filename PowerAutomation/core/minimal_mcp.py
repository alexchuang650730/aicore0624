"""
極簡MCP - 20行版本
"""

async def mcp(request):
    """MCP核心"""
    # 識別專家
    experts = []
    if "保險" in request: experts.append("保險專家")
    if "技術" in request: experts.append("技術專家")
    if not experts: experts = ["保險專家"]
    
    # 生成回答
    answers = []
    for expert in experts:
        if expert == "保險專家":
            answers.append("核保需3-5人/千件，自動化率60-70%，OCR審核0.5-1人月/千件")
        elif expert == "技術專家":
            answers.append("OCR+AI可提升3-5倍效率，準確率95%+")
    
    return "\n".join(answers)

# 測試
import asyncio
result = asyncio.run(mcp("臺銀人壽保單SOP要多少人力，自動化比率多高？"))
print(result)

