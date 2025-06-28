#!/usr/bin/env python3
"""
ClaudeSDKMCP 快速启动脚本
演示基本功能和使用方法
"""

import asyncio
import json
import os
from claude_sdk_mcp_v2 import ClaudeSDKMCP

async def demo_basic_usage():
    """演示基本使用方法"""
    print("🚀 ClaudeSDKMCP v2.0.0 快速启动演示")
    print("=" * 50)
    
    # 初始化 ClaudeSDKMCP
    print("🔧 初始化 ClaudeSDKMCP...")
    claude_sdk = ClaudeSDKMCP()
    
    try:
        # 演示代码分析
        print("\n📋 演示代码分析功能...")
        
        sample_code = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# 性能问题：递归实现效率低
result = calculate_fibonacci(30)
print(result)
        """
        
        result = await claude_sdk.process_request(
            "请分析这段Python代码的性能问题并提供优化建议",
            {
                "code": sample_code,
                "language": "python",
                "context": "算法优化"
            }
        )
        
        print(f"✅ 分析完成!")
        print(f"📊 使用专家: {result.expert_used}")
        print(f"📊 执行操作数: {len(result.operations_executed)}")
        print(f"📊 信心度: {result.confidence_score:.2f}")
        print(f"📊 处理时间: {result.processing_time:.2f}s")
        
        if result.recommendations:
            print("\n💡 建议:")
            for i, rec in enumerate(result.recommendations[:3], 1):
                print(f"  {i}. {rec}")
        
        # 演示专家推荐
        print("\n👨‍💼 演示专家推荐功能...")
        
        from claude_sdk_mcp_v2 import ScenarioAnalysis, ScenarioType, ComplexityLevel, ContentSize
        
        scenario = ScenarioAnalysis(
            scenario_type=ScenarioType.PERFORMANCE_OPTIMIZATION,
            complexity_level=ComplexityLevel.HIGH,
            content_size=ContentSize.MEDIUM,
            technical_domains=["python", "algorithms"],
            recommended_experts=[],
            recommended_operations=[],
            context_requirements={},
            confidence_score=0.9,
            analysis_reasoning="性能优化场景",
            estimated_tokens=2000
        )
        
        expert_recommendations = claude_sdk.get_expert_recommendations_for_scenario(scenario)
        
        print(f"📊 推荐专家数量: {len(expert_recommendations)}")
        for rec in expert_recommendations:
            print(f"  - {rec.expert_type.value}: 匹配度 {rec.match_score:.2f}")
        
        # 显示系统统计
        print("\n📈 系统统计信息...")
        stats = claude_sdk.get_statistics()
        
        print(f"📊 版本: {stats['version']}")
        print(f"📊 总请求数: {stats['total_requests']}")
        print(f"📊 专家数量: {stats['total_experts']}")
        print(f"📊 操作处理器数量: {stats['operation_handlers']}")
        
        print("\n🎯 核心特点:")
        for feature in stats['features']:
            print(f"  ✅ {feature}")
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
    
    finally:
        await claude_sdk.close()
    
    print("\n" + "=" * 50)
    print("🎉 演示完成!")
    print("\n📚 更多使用方法:")
    print("  - 查看 README.md 了解详细文档")
    print("  - 运行 python cli.py --help 查看CLI选项")
    print("  - 运行 python cli.py interactive 进入交互模式")
    print("  - 运行 python test_claude_sdk_mcp.py 执行完整测试")

def show_configuration_guide():
    """显示配置指南"""
    print("\n🔧 配置指南:")
    print("1. 设置 Claude API 密钥:")
    print("   export CLAUDE_API_KEY='your-api-key-here'")
    print("\n2. 可选配置:")
    print("   export LOG_LEVEL='INFO'")
    print("   export ENABLE_DYNAMIC_EXPERTS='true'")
    print("   export MAX_EXPERTS='20'")
    print("   export CONFIDENCE_THRESHOLD='0.8'")
    print("\n3. 安装依赖:")
    print("   pip install -r requirements.txt")

def show_usage_examples():
    """显示使用示例"""
    print("\n📖 使用示例:")
    print("\n1. CLI 使用:")
    print("   # 分析文件")
    print("   python cli.py analyze --file code.py")
    print("   # 分析代码片段")
    print("   python cli.py analyze --code 'def hello(): pass'")
    print("   # 获取专家推荐")
    print("   python cli.py experts recommend --scenario performance_optimization")
    print("   # 交互模式")
    print("   python cli.py interactive")
    
    print("\n2. Python API 使用:")
    print("""
import asyncio
from claude_sdk_mcp_v2 import ClaudeSDKMCP

async def main():
    claude_sdk = ClaudeSDKMCP(api_key="your-api-key")
    result = await claude_sdk.process_request(
        "分析这段代码",
        {"code": "def hello(): pass", "language": "python"}
    )
    print(f"结果: {result.success}")
    await claude_sdk.close()

asyncio.run(main())
    """)

async def main():
    """主函数"""
    print("🌟 欢迎使用 ClaudeSDKMCP v2.0.0!")
    
    # 检查是否设置了API密钥
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key or api_key == "your-claude-api-key-here":
        print("\n⚠️ 注意: 未检测到有效的 Claude API 密钥")
        print("系统将使用默认模式运行（功能受限）")
        show_configuration_guide()
    
    print("\n选择操作:")
    print("1. 运行基本功能演示")
    print("2. 显示配置指南")
    print("3. 显示使用示例")
    print("4. 退出")
    
    try:
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == "1":
            await demo_basic_usage()
        elif choice == "2":
            show_configuration_guide()
        elif choice == "3":
            show_usage_examples()
        elif choice == "4":
            print("👋 再见!")
        else:
            print("❌ 无效选择")
    
    except KeyboardInterrupt:
        print("\n👋 再见!")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())

