#!/usr/bin/env python3
"""
ClaudeSDKMCP 测试文件
测试各项功能和性能
"""

import asyncio
import json
import time
import sys
from pathlib import Path
from typing import Dict, Any

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from claude_sdk_mcp_v2 import ClaudeSDKMCP, ExpertProfile, ExpertType, ExpertStatus, ExpertCapability, OperationType
from config import Config

class ClaudeSDKMCPTester:
    """ClaudeSDKMCP 测试类"""
    
    def __init__(self):
        self.config = Config()
        self.claude_sdk = None
        self.test_results = []
    
    async def setup(self):
        """设置测试环境"""
        print("🔧 设置测试环境...")
        self.claude_sdk = ClaudeSDKMCP(api_key=self.config.claude_api.api_key)
        print("✅ ClaudeSDKMCP 初始化完成")
    
    async def test_basic_functionality(self):
        """测试基本功能"""
        print("\n📋 测试基本功能...")
        
        test_cases = [
            {
                "name": "简单代码分析",
                "input": "请分析这段Python代码的问题",
                "context": {
                    "code": "def hello():\n    print('Hello World')",
                    "language": "python"
                }
            },
            {
                "name": "性能优化咨询",
                "input": "如何优化这个算法的性能？",
                "context": {
                    "code": "for i in range(1000000):\n    result = i * i",
                    "language": "python"
                }
            },
            {
                "name": "安全审计请求",
                "input": "请检查这段代码的安全问题",
                "context": {
                    "code": "query = f\"SELECT * FROM users WHERE id = {user_id}\"",
                    "language": "python"
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"  🧪 测试: {test_case['name']}")
            start_time = time.time()
            
            try:
                result = await self.claude_sdk.process_request(
                    test_case["input"],
                    test_case["context"]
                )
                
                processing_time = time.time() - start_time
                
                test_result = {
                    "test_name": test_case["name"],
                    "success": result.success,
                    "processing_time": processing_time,
                    "confidence_score": result.confidence_score,
                    "operations_executed": len(result.operations_executed),
                    "expert_used": result.expert_used
                }
                
                self.test_results.append(test_result)
                
                if result.success:
                    print(f"    ✅ 成功 - 处理时间: {processing_time:.2f}s, 信心度: {result.confidence_score:.2f}")
                    print(f"    📊 执行操作: {len(result.operations_executed)}, 使用专家: {result.expert_used}")
                else:
                    print(f"    ❌ 失败 - {result.error_message}")
                
            except Exception as e:
                print(f"    ❌ 异常 - {e}")
                self.test_results.append({
                    "test_name": test_case["name"],
                    "success": False,
                    "error": str(e)
                })
    
    async def test_expert_system(self):
        """测试专家系统"""
        print("\n👨‍💼 测试专家系统...")
        
        # 测试专家列表
        experts = self.claude_sdk.expert_registry.experts
        print(f"  📊 已注册专家数量: {len(experts)}")
        
        for expert_id, expert in experts.items():
            print(f"    - {expert.name} ({expert_id}): {expert.status.value}")
        
        # 测试动态专家注册
        print("  🔄 测试动态专家注册...")
        
        dynamic_expert = ExpertProfile(
            id="test_expert_001",
            name="测试专家",
            type=ExpertType.DYNAMIC_EXPERT,
            status=ExpertStatus.ACTIVE,
            specialties=["测试", "验证"],
            capabilities=[
                ExpertCapability(
                    name="测试能力",
                    description="专门用于测试的能力",
                    skill_level="expert",
                    domain="testing",
                    keywords=["测试", "验证", "质量"],
                    confidence=0.9,
                    source="manual"
                )
            ],
            context_limit="200K tokens",
            supported_operations=[OperationType.SYNTAX_ANALYSIS],
            confidence_threshold=0.8
        )
        
        success = self.claude_sdk.add_dynamic_expert(dynamic_expert)
        if success:
            print("    ✅ 动态专家注册成功")
        else:
            print("    ❌ 动态专家注册失败")
    
    async def test_operation_handlers(self):
        """测试操作处理器"""
        print("\n⚙️ 测试操作处理器...")
        
        operation_count = len(self.claude_sdk.operation_handlers)
        print(f"  📊 已注册操作处理器数量: {operation_count}")
        
        # 测试几个关键操作处理器
        test_operations = [
            OperationType.SYNTAX_ANALYSIS,
            OperationType.PERFORMANCE_PROFILING,
            OperationType.SECURITY_AUDIT,
            OperationType.API_DESIGN_REVIEW,
            OperationType.DATABASE_DESIGN_REVIEW
        ]
        
        from claude_sdk_mcp_v2 import ProcessingRequest
        from datetime import datetime
        
        test_request = ProcessingRequest(
            request_id="test_001",
            user_input="测试请求",
            context={"test": True},
            timestamp=datetime.now()
        )
        
        for operation in test_operations:
            if operation in self.claude_sdk.operation_handlers:
                try:
                    handler = self.claude_sdk.operation_handlers[operation]
                    result = await handler(test_request)
                    print(f"    ✅ {operation.value}: {result.get('status', 'unknown')}")
                except Exception as e:
                    print(f"    ❌ {operation.value}: {e}")
            else:
                print(f"    ⚠️ {operation.value}: 处理器未找到")
    
    async def test_performance(self):
        """测试性能"""
        print("\n🚀 测试性能...")
        
        # 并发测试
        concurrent_requests = 3
        print(f"  🔄 并发测试 ({concurrent_requests} 个请求)...")
        
        async def single_request(request_id: int):
            start_time = time.time()
            result = await self.claude_sdk.process_request(
                f"测试请求 {request_id}",
                {"test_id": request_id}
            )
            processing_time = time.time() - start_time
            return {
                "request_id": request_id,
                "success": result.success,
                "processing_time": processing_time
            }
        
        start_time = time.time()
        tasks = [single_request(i) for i in range(concurrent_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        successful_requests = sum(1 for r in results if isinstance(r, dict) and r.get("success", False))
        avg_processing_time = sum(r.get("processing_time", 0) for r in results if isinstance(r, dict)) / len(results)
        
        print(f"    📊 总时间: {total_time:.2f}s")
        print(f"    📊 成功请求: {successful_requests}/{concurrent_requests}")
        print(f"    📊 平均处理时间: {avg_processing_time:.2f}s")
        
        # 内存使用测试
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        print(f"    💾 内存使用: {memory_info.rss / 1024 / 1024:.2f} MB")
    
    async def test_error_handling(self):
        """测试错误处理"""
        print("\n🛡️ 测试错误处理...")
        
        error_test_cases = [
            {
                "name": "空输入",
                "input": "",
                "context": {}
            },
            {
                "name": "无效上下文",
                "input": "测试",
                "context": None
            },
            {
                "name": "超大输入",
                "input": "x" * 10000,
                "context": {}
            }
        ]
        
        for test_case in error_test_cases:
            print(f"  🧪 测试: {test_case['name']}")
            try:
                result = await self.claude_sdk.process_request(
                    test_case["input"],
                    test_case["context"]
                )
                
                if result.success:
                    print(f"    ✅ 处理成功")
                else:
                    print(f"    ⚠️ 处理失败但错误处理正常: {result.error_message}")
                
            except Exception as e:
                print(f"    ❌ 未捕获异常: {e}")
    
    async def test_statistics_and_monitoring(self):
        """测试统计和监控"""
        print("\n📈 测试统计和监控...")
        
        stats = self.claude_sdk.get_statistics()
        
        print(f"  📊 版本: {stats['version']}")
        print(f"  📊 总请求数: {stats['total_requests']}")
        print(f"  📊 专家数量: {stats['total_experts']}")
        print(f"  📊 操作处理器数量: {stats['operation_handlers']}")
        
        print("  👨‍💼 专家统计:")
        for expert_id, expert_stats in stats.get('expert_statistics', {}).items():
            print(f"    - {expert_stats['name']}: {expert_stats['total_requests']} 请求, "
                  f"成功率 {expert_stats['success_rate']:.2%}")
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n📋 生成测试报告...")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.get("success", False))
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "test_results": self.test_results,
            "system_info": {
                "version": "2.0.0",
                "features_tested": [
                    "基本功能",
                    "专家系统",
                    "操作处理器",
                    "性能测试",
                    "错误处理",
                    "统计监控"
                ]
            }
        }
        
        # 保存报告
        report_file = Path(__file__).parent / "test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"  📄 测试报告已保存到: {report_file}")
        print(f"  📊 测试成功率: {report['test_summary']['success_rate']:.2%}")
        
        return report
    
    async def cleanup(self):
        """清理资源"""
        if self.claude_sdk:
            await self.claude_sdk.close()

async def main():
    """主测试函数"""
    print("🧪 ClaudeSDKMCP v2.0.0 测试开始")
    print("=" * 50)
    
    tester = ClaudeSDKMCPTester()
    
    try:
        # 设置测试环境
        await tester.setup()
        
        # 运行各项测试
        await tester.test_basic_functionality()
        await tester.test_expert_system()
        await tester.test_operation_handlers()
        await tester.test_performance()
        await tester.test_error_handling()
        await tester.test_statistics_and_monitoring()
        
        # 生成测试报告
        report = tester.generate_test_report()
        
        print("\n" + "=" * 50)
        print("🎉 测试完成!")
        
        if report["test_summary"]["success_rate"] >= 0.8:
            print("✅ 系统运行良好")
        else:
            print("⚠️ 系统存在问题，请检查测试报告")
    
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

