#!/usr/bin/env python3
"""
ClaudeSDKMCP CLI 接口
提供命令行界面来使用 ClaudeSDKMCP
"""

import asyncio
import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import asdict

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from claude_sdk_mcp_v2 import ClaudeSDKMCP, ScenarioType, ComplexityLevel, ContentSize
from config import Config, OPERATION_CATEGORIES, EXPERT_SPECIALTIES, SCENARIO_CONFIGS

class ClaudeSDKMCPCLI:
    """ClaudeSDKMCP CLI 类"""
    
    def __init__(self):
        self.config = Config()
        self.claude_sdk = None
    
    async def initialize(self):
        """初始化 ClaudeSDKMCP"""
        self.claude_sdk = ClaudeSDKMCP(api_key=self.config.claude_api.api_key)
        print("ClaudeSDKMCP v2.0.0 已初始化")
    
    async def analyze_code(self, code: str, language: str = "python", context: str = "") -> Dict[str, Any]:
        """分析代码"""
        if not self.claude_sdk:
            await self.initialize()
        
        request_context = {
            "code": code,
            "language": language,
            "context": context
        }
        
        result = await self.claude_sdk.process_request(
            f"请分析这段{language}代码",
            request_context
        )
        
        return asdict(result)
    
    async def analyze_file(self, file_path: str, context: str = "") -> Dict[str, Any]:
        """分析文件"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 根据文件扩展名确定语言
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby'
        }
        language = language_map.get(ext, 'unknown')
        
        return await self.analyze_code(code, language, context)
    
    async def get_expert_recommendation(self, scenario: str, domains: list = None) -> Dict[str, Any]:
        """获取专家推荐"""
        if not self.claude_sdk:
            await self.initialize()
        
        # 创建场景分析
        from claude_sdk_mcp_v2 import ScenarioAnalysis
        
        scenario_analysis = ScenarioAnalysis(
            scenario_type=ScenarioType(scenario),
            complexity_level=ComplexityLevel.MEDIUM,
            content_size=ContentSize.MEDIUM,
            technical_domains=domains or ["general"],
            recommended_experts=[],
            recommended_operations=[],
            context_requirements={},
            confidence_score=0.8,
            analysis_reasoning="CLI请求",
            estimated_tokens=1000
        )
        
        recommendations = self.claude_sdk.get_expert_recommendations_for_scenario(scenario_analysis)
        
        return {
            "scenario": scenario,
            "recommendations": [asdict(rec) for rec in recommendations]
        }
    
    async def list_experts(self) -> Dict[str, Any]:
        """列出所有专家"""
        if not self.claude_sdk:
            await self.initialize()
        
        experts = {}
        for expert_id, expert in self.claude_sdk.expert_registry.experts.items():
            experts[expert_id] = {
                "name": expert.name,
                "type": expert.type.value,
                "status": expert.status.value,
                "specialties": expert.specialties,
                "total_requests": expert.total_requests,
                "success_rate": expert.success_rate
            }
        
        return {"experts": experts}
    
    async def list_operations(self, category: str = None) -> Dict[str, Any]:
        """列出操作"""
        if category and category in OPERATION_CATEGORIES:
            return {
                "category": category,
                "operations": OPERATION_CATEGORIES[category]
            }
        else:
            return {"categories": OPERATION_CATEGORIES}
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.claude_sdk:
            await self.initialize()
        
        return self.claude_sdk.get_statistics()
    
    async def interactive_mode(self):
        """交互模式"""
        if not self.claude_sdk:
            await self.initialize()
        
        print("\n=== ClaudeSDKMCP 交互模式 ===")
        print("输入 'help' 查看帮助，输入 'quit' 退出")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    self._print_interactive_help()
                elif user_input.lower() == 'stats':
                    stats = await self.get_statistics()
                    print(json.dumps(stats, ensure_ascii=False, indent=2, default=str))
                elif user_input.lower() == 'experts':
                    experts = await self.list_experts()
                    print(json.dumps(experts, ensure_ascii=False, indent=2, default=str))
                elif user_input.lower() == 'operations':
                    operations = await self.list_operations()
                    print(json.dumps(operations, ensure_ascii=False, indent=2))
                elif user_input.startswith('analyze:'):
                    code = user_input[8:].strip()
                    if code:
                        result = await self.analyze_code(code)
                        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
                    else:
                        print("请提供要分析的代码")
                elif user_input.startswith('file:'):
                    file_path = user_input[5:].strip()
                    if file_path:
                        try:
                            result = await self.analyze_file(file_path)
                            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
                        except Exception as e:
                            print(f"分析文件失败: {e}")
                    else:
                        print("请提供文件路径")
                elif user_input:
                    # 直接处理用户输入
                    result = await self.claude_sdk.process_request(user_input)
                    print(json.dumps(asdict(result), ensure_ascii=False, indent=2, default=str))
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"错误: {e}")
        
        print("\n再见!")
    
    def _print_interactive_help(self):
        """打印交互模式帮助"""
        help_text = """
可用命令:
  help                    - 显示此帮助信息
  stats                   - 显示系统统计信息
  experts                 - 列出所有专家
  operations              - 列出所有操作类型
  analyze: <code>         - 分析代码片段
  file: <path>           - 分析文件
  quit/exit/q            - 退出程序
  
或者直接输入问题，系统会自动分析并推荐专家处理。

示例:
  analyze: def hello(): print("world")
  file: /path/to/code.py
  请帮我优化这个算法的性能
        """
        print(help_text)
    
    async def cleanup(self):
        """清理资源"""
        if self.claude_sdk:
            await self.claude_sdk.close()

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="ClaudeSDKMCP CLI - 智能代码分析和专家咨询系统")
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析代码')
    analyze_group = analyze_parser.add_mutually_exclusive_group(required=True)
    analyze_group.add_argument('--code', type=str, help='要分析的代码')
    analyze_group.add_argument('--file', type=str, help='要分析的文件路径')
    analyze_parser.add_argument('--language', type=str, default='python', help='编程语言')
    analyze_parser.add_argument('--context', type=str, default='', help='上下文信息')
    
    # experts 命令
    experts_parser = subparsers.add_parser('experts', help='专家管理')
    experts_subparsers = experts_parser.add_subparsers(dest='experts_action')
    experts_subparsers.add_parser('list', help='列出所有专家')
    
    recommend_parser = experts_subparsers.add_parser('recommend', help='获取专家推荐')
    recommend_parser.add_argument('--scenario', type=str, required=True, 
                                choices=['code_analysis', 'architecture_design', 'performance_optimization', 
                                       'api_design', 'security_audit', 'database_design'],
                                help='场景类型')
    recommend_parser.add_argument('--domains', nargs='+', help='技术领域')
    
    # operations 命令
    operations_parser = subparsers.add_parser('operations', help='列出操作')
    operations_parser.add_argument('--category', type=str, 
                                 choices=['code_analysis', 'architecture', 'performance', 
                                        'api_design', 'security', 'database'],
                                 help='操作类别')
    
    # stats 命令
    subparsers.add_parser('stats', help='显示统计信息')
    
    # interactive 命令
    subparsers.add_parser('interactive', help='进入交互模式')
    
    # config 命令
    config_parser = subparsers.add_parser('config', help='配置管理')
    config_parser.add_argument('--show', action='store_true', help='显示当前配置')
    
    args = parser.parse_args()
    
    cli = ClaudeSDKMCPCLI()
    
    try:
        if args.command == 'analyze':
            if args.code:
                result = await cli.analyze_code(args.code, args.language, args.context)
            elif args.file:
                result = await cli.analyze_file(args.file, args.context)
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        
        elif args.command == 'experts':
            if args.experts_action == 'list':
                result = await cli.list_experts()
                print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
            elif args.experts_action == 'recommend':
                result = await cli.get_expert_recommendation(args.scenario, args.domains)
                print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        
        elif args.command == 'operations':
            result = await cli.list_operations(args.category)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif args.command == 'stats':
            result = await cli.get_statistics()
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        
        elif args.command == 'interactive':
            await cli.interactive_mode()
        
        elif args.command == 'config':
            if args.show:
                config_dict = cli.config.to_dict()
                print(json.dumps(config_dict, ensure_ascii=False, indent=2))
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    
    finally:
        await cli.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

