#!/usr/bin/env python3
"""
Enhanced AICore 3.0 Fusion CLI - 融合系统命令行工具
提供简单易用的命令行接口来使用融合版AICore系统
"""

import asyncio
import argparse
import json
import sys
from typing import Dict, Any
import time

# 导入融合系统
from enhanced_aicore3_fusion import SimplifiedAIInterface, FusionConfig

class FusionCLI:
    """融合系统CLI工具"""
    
    def __init__(self):
        self.ai = None
        
    async def initialize(self, budget: float = 50.0):
        """初始化AI系统"""
        print("🚀 正在初始化Enhanced AICore 3.0 Fusion...")
        self.ai = SimplifiedAIInterface(budget=budget)
        await self.ai.core.initialize()
        print("✅ 系统初始化完成！")
        
    async def ask_question(self, question: str, budget_limit: float = None):
        """问答功能"""
        print(f"\n❓ 问题: {question}")
        print("🤔 正在思考...")
        
        start_time = time.time()
        answer = await self.ai.ask(question, budget_limit)
        processing_time = time.time() - start_time
        
        print(f"\n💡 回答: {answer}")
        print(f"⏱️  处理时间: {processing_time:.2f}秒")
        
        # 显示成本信息
        budget_status = self.ai.get_budget_status()
        print(f"💰 成本: ${budget_status['current_usage']:.4f} (剩余: ${budget_status['remaining_budget']:.4f})")
        
    async def analyze_content(self, content: str, deep: bool = False):
        """内容分析功能"""
        print(f"\n📊 分析内容: {content[:100]}{'...' if len(content) > 100 else ''}")
        print(f"🔍 分析模式: {'深度分析' if deep else '标准分析'}")
        print("⚡ 正在分析...")
        
        start_time = time.time()
        result = await self.ai.analyze(content, deep=deep)
        processing_time = time.time() - start_time
        
        if result['success']:
            print(f"\n📋 分析结果:")
            print(f"   结果: {result['result']['result']}")
            print(f"   处理方法: {result['result'].get('method', 'unknown')}")
            print(f"   质量评分: {result['result'].get('quality_score', 0):.2f}")
            print(f"   处理时间: {processing_time:.2f}秒")
            print(f"   成本: ${result['cost_used']:.4f}")
            print(f"   处理模式: {result['processing_mode']}")
        else:
            print(f"❌ 分析失败: {result.get('error', '未知错误')}")
    
    async def show_status(self):
        """显示系统状态"""
        print("\n📊 系统状态报告")
        print("=" * 50)
        
        # 预算状态
        budget_status = self.ai.get_budget_status()
        print(f"💰 预算状态:")
        print(f"   总预算: ${budget_status['total_budget']}")
        print(f"   已使用: ${budget_status['current_usage']:.4f}")
        print(f"   剩余预算: ${budget_status['remaining_budget']:.4f}")
        print(f"   使用率: {budget_status['usage_percentage']:.1f}%")
        print(f"   风险级别: {budget_status['risk_level']}")
        
        # 性能摘要
        performance = self.ai.get_performance_summary()
        print(f"\n⚡ 性能摘要:")
        print(f"   总请求数: {performance['total_requests']}")
        print(f"   成功率: {performance['success_rate']:.1f}%")
        print(f"   平均响应时间: {performance['average_response_time']}")
        print(f"   总成本: {performance['total_cost']}")
        print(f"   平均质量: {performance['average_quality']}")
        
        # 系统组件状态
        system_status = self.ai.core.get_system_status()
        print(f"\n🔧 组件状态:")
        for component, status in system_status['components_status'].items():
            status_icon = "✅" if status else "❌"
            print(f"   {component}: {status_icon}")
    
    async def interactive_mode(self):
        """交互模式"""
        print("\n🎯 进入交互模式 (输入 'quit' 退出, 'help' 查看帮助)")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 再见！")
                    break
                elif user_input.lower() in ['help', 'h']:
                    self.show_help()
                elif user_input.lower() in ['status', 's']:
                    await self.show_status()
                elif user_input.lower().startswith('analyze '):
                    content = user_input[8:]  # 移除 'analyze ' 前缀
                    await self.analyze_content(content)
                elif user_input.lower().startswith('deep '):
                    content = user_input[5:]  # 移除 'deep ' 前缀
                    await self.analyze_content(content, deep=True)
                elif user_input:
                    await self.ask_question(user_input)
                else:
                    print("请输入问题或命令")
                    
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
🎯 Enhanced AICore 3.0 Fusion 帮助

基本命令:
  <问题>              - 直接提问
  analyze <内容>      - 标准分析
  deep <内容>         - 深度分析
  status / s          - 显示系统状态
  help / h            - 显示此帮助
  quit / q            - 退出程序

示例:
  > 什么是机器学习？
  > analyze Python在数据科学中的应用
  > deep 分析区块链技术的发展趋势
  > status
        """
        print(help_text)

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Enhanced AICore 3.0 Fusion CLI - 融合版AI系统命令行工具"
    )
    
    parser.add_argument(
        '--budget', '-b',
        type=float,
        default=50.0,
        help='设置预算限制 (默认: $50.0)'
    )
    
    parser.add_argument(
        '--question', '-q',
        type=str,
        help='直接提问'
    )
    
    parser.add_argument(
        '--analyze', '-a',
        type=str,
        help='分析内容'
    )
    
    parser.add_argument(
        '--deep',
        action='store_true',
        help='使用深度分析模式'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='显示系统状态'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='进入交互模式'
    )
    
    args = parser.parse_args()
    
    # 创建CLI实例
    cli = FusionCLI()
    
    try:
        # 初始化系统
        await cli.initialize(budget=args.budget)
        
        # 根据参数执行相应功能
        if args.question:
            await cli.ask_question(args.question)
        elif args.analyze:
            await cli.analyze_content(args.analyze, deep=args.deep)
        elif args.status:
            await cli.show_status()
        elif args.interactive:
            await cli.interactive_mode()
        else:
            # 默认进入交互模式
            print("🎯 欢迎使用Enhanced AICore 3.0 Fusion!")
            print("💡 提示: 使用 --help 查看所有命令选项")
            await cli.interactive_mode()
            
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"❌ 系统错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

