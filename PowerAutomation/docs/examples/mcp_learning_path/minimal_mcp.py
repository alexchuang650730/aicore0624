"""
MCP学习路径 - 第一步：概念入门
=================================

文件：minimal_mcp.py
目标：理解MCP的最基本概念
代码量：~20行
学习时间：5分钟

这是一个极简的MCP实现，用于演示MCP的核心概念：
1. 专家识别 - 根据请求内容识别需要哪些专家
2. 专家调用 - 调用相应的专家获取答案  
3. 答案生成 - 生成最终回答

注意：这是教学示例，不适用于生产环境。
请参考 PowerAutomation/core/aicore3.py 了解完整实现。

学习要点：
- MCP = Model-Centric Processing（以模型为中心的处理）
- 专家系统：不同领域的专业知识模块
- 简单的关键词匹配进行专家识别
- 硬编码的专家回答（实际应该调用LLM）
"""

import asyncio

async def mcp(request):
    """
    MCP核心函数 - 极简版本
    
    参数:
        request (str): 用户请求文本
    
    返回:
        str: 专家回答的聚合结果
    
    处理流程:
        1. 专家识别 - 通过关键词匹配
        2. 专家调用 - 获取专家回答
        3. 答案聚合 - 合并多个专家的回答
    """
    
    # 第一步：专家识别
    # 通过简单的关键词匹配来识别需要哪些专家
    experts = []
    
    if "保險" in request or "核保" in request or "保單" in request:
        experts.append("保險專家")
    
    if "技術" in request or "自動化" in request or "OCR" in request or "AI" in request:
        experts.append("技術專家")
    
    # 如果没有匹配到任何专家，默认使用保险专家
    if not experts:
        experts = ["保險專家"]
    
    print(f"🔍 识别到需要的专家: {experts}")
    
    # 第二步：专家调用和答案生成
    # 在真实系统中，这里应该调用LLM API
    answers = []
    
    for expert in experts:
        if expert == "保險專家":
            # 模拟保险专家的回答
            answer = "【保險專家】核保需3-5人/千件，自動化率60-70%，OCR審核0.5-1人月/千件"
            answers.append(answer)
            print(f"💼 {expert}: 已生成专业分析")
            
        elif expert == "技術專家":
            # 模拟技术专家的回答
            answer = "【技術專家】OCR+AI可提升3-5倍效率，準確率95%+"
            answers.append(answer)
            print(f"🔧 {expert}: 已生成技术分析")
    
    # 第三步：答案聚合
    # 简单地将所有专家的回答用换行符连接
    final_answer = "\n".join(answers)
    
    print(f"✅ 聚合完成，共 {len(answers)} 个专家回答")
    
    return final_answer

# 学习练习区域
# ===============

def learning_exercise_1():
    """
    练习1：理解专家识别机制
    尝试修改关键词，观察专家识别的变化
    """
    test_requests = [
        "保險業務流程分析",           # 应该识别：保险专家
        "OCR技術自動化方案",         # 应该识别：技术专家  
        "保單處理自動化技術方案",     # 应该识别：保险专家 + 技术专家
        "人力資源管理",              # 应该识别：保险专家（默认）
    ]
    
    print("=== 练习1：专家识别测试 ===")
    for i, request in enumerate(test_requests, 1):
        print(f"\n测试 {i}: {request}")
        # 这里可以添加测试代码
        
def learning_exercise_2():
    """
    练习2：扩展专家类型
    尝试添加新的专家类型，如"商业专家"、"法律专家"
    """
    print("=== 练习2：扩展专家类型 ===")
    print("提示：在mcp函数中添加新的专家识别逻辑")
    print("例如：if '商業' in request: experts.append('商業專家')")

def learning_exercise_3():
    """
    练习3：改进答案质量
    尝试让专家回答更加详细和专业
    """
    print("=== 练习3：改进答案质量 ===")
    print("提示：修改专家回答的内容，使其更加详细和专业")

# 主测试函数
async def main():
    """主测试函数 - 演示MCP的基本工作流程"""
    
    print("🚀 MCP学习路径 - 第一步：概念入门")
    print("=" * 50)
    
    # 测试用例
    test_request = "臺銀人壽保單SOP要多少人力，自動化比率多高？"
    
    print(f"📝 用户请求: {test_request}")
    print("\n🔄 MCP处理过程:")
    
    # 调用MCP处理
    result = await mcp(test_request)
    
    print(f"\n📋 最终回答:")
    print("-" * 30)
    print(result)
    print("-" * 30)
    
    print(f"\n🎯 学习总结:")
    print("1. MCP通过专家识别确定需要哪些专业知识")
    print("2. 每个专家提供特定领域的专业回答")
    print("3. 最终将多个专家的回答聚合成完整答案")
    print("\n📚 下一步：学习 ultra_simple_mcp.py 了解架构设计")

# 如果直接运行此文件
if __name__ == "__main__":
    # 运行主测试
    asyncio.run(main())
    
    # 可以取消注释下面的行来运行练习
    # learning_exercise_1()
    # learning_exercise_2() 
    # learning_exercise_3()

"""
学习检查清单：
□ 理解了MCP的基本概念
□ 知道什么是专家系统
□ 了解专家识别的工作原理
□ 明白答案聚合的基本方法
□ 认识到这是简化版本，生产环境需要更复杂的实现

完成后请继续学习：ultra_simple_mcp.py
"""

