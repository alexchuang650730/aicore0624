#!/usr/bin/env python3
"""
KiloCode集成测试脚本
测试Code Generation MCP与KiloCode的集成功能
"""

import asyncio
import json
import sys
import os

# 添加PowerAutomation路径
sys.path.append('/home/ubuntu/aicore0624/PowerAutomation')

from components.code_generation_mcp import CodeGenerationMcp

async def test_kilocode_integration():
    """测试KiloCode集成功能"""
    
    print("🚀 开始测试KiloCode集成...")
    
    # 配置KiloCode集成
    config = {
        "kilocode": {
            "enabled": True,
            "kilocode_url": "http://localhost:8080",
            "kilocode_api_key": "sk-ant-api03-[YOUR_API_KEY_HERE]",
            "timeout": 30
        },
        "use_kilocode_fallback": True,
        "quality_threshold": 0.7
    }
    
    # 初始化Code Generation MCP
    mcp = CodeGenerationMcp(config)
    await mcp.initialize()
    
    print(f"✅ MCP初始化完成: {mcp.name} v{mcp.version}")
    print(f"📊 KiloCode集成状态: {'启用' if mcp.kilocode.enabled else '禁用'}")
    print(f"🎯 质量阈值: {mcp.quality_threshold}")
    
    # 测试用例1：基本代码生成
    print("\n📝 测试用例1: 基本API代码生成")
    test_data_1 = {
        "code_type": "api",
        "language": "python",
        "framework": "flask",
        "requirements": "创建一个用户管理API，包含增删改查功能",
        "specifications": {
            "endpoint": "users",
            "method": "POST",
            "function_name": "create_user",
            "description": "创建新用户"
        }
    }
    
    result_1 = await mcp._generate_code(test_data_1)
    print(f"状态: {result_1.get('status')}")
    print(f"生成方法: {result_1.get('code_info', {}).get('generation_method', 'unknown')}")
    print(f"质量分数: {result_1.get('code_info', {}).get('quality_score', 0):.2f}")
    
    if result_1.get('status') == 'success':
        print("✅ 测试用例1通过")
        print(f"生成的代码长度: {len(result_1.get('generated_code', ''))} 字符")
    else:
        print(f"❌ 测试用例1失败: {result_1.get('error')}")
    
    # 测试用例2：强制使用KiloCode（通过设置高质量阈值）
    print("\n📝 测试用例2: 强制使用KiloCode（高质量阈值）")
    mcp.quality_threshold = 0.95  # 设置很高的阈值，强制使用KiloCode
    
    test_data_2 = {
        "code_type": "api",
        "language": "python",
        "framework": "fastapi",
        "requirements": "创建一个高性能的数据分析API，支持实时数据处理",
        "specifications": {
            "endpoint": "analytics",
            "method": "POST",
            "function_name": "analyze_data",
            "description": "实时数据分析"
        }
    }
    
    result_2 = await mcp._generate_code(test_data_2)
    print(f"状态: {result_2.get('status')}")
    print(f"生成方法: {result_2.get('code_info', {}).get('generation_method', 'unknown')}")
    print(f"质量分数: {result_2.get('code_info', {}).get('quality_score', 0):.2f}")
    
    if result_2.get('status') == 'success':
        print("✅ 测试用例2通过")
        generation_method = result_2.get('code_info', {}).get('generation_method', 'unknown')
        if 'kilocode' in generation_method:
            print("🎯 成功触发KiloCode生成")
        else:
            print("⚠️  未触发KiloCode生成")
    else:
        print(f"❌ 测试用例2失败: {result_2.get('error')}")
    
    # 测试用例3：KiloCode禁用情况
    print("\n📝 测试用例3: KiloCode禁用情况")
    mcp.kilocode.enabled = False
    mcp.quality_threshold = 0.7  # 恢复正常阈值
    
    result_3 = await mcp._generate_code(test_data_1)
    print(f"状态: {result_3.get('status')}")
    print(f"生成方法: {result_3.get('code_info', {}).get('generation_method', 'unknown')}")
    
    if result_3.get('status') == 'success':
        generation_method = result_3.get('code_info', {}).get('generation_method', 'unknown')
        if 'kilocode' not in generation_method:
            print("✅ 测试用例3通过 - KiloCode正确禁用")
        else:
            print("❌ 测试用例3失败 - KiloCode未正确禁用")
    else:
        print(f"❌ 测试用例3失败: {result_3.get('error')}")
    
    # 性能统计
    print("\n📊 性能统计:")
    stats = mcp.performance_stats
    print(f"总生成次数: {stats['total_generations']}")
    print(f"成功生成次数: {stats['successful_generations']}")
    print(f"模板使用次数: {stats['template_usage']}")
    print(f"KiloCode使用次数: {stats['kilocode_usage']}")
    
    print("\n🎉 KiloCode集成测试完成!")

async def test_kilocode_direct():
    """直接测试KiloCode集成类"""
    print("\n🔧 直接测试KiloCode集成类...")
    
    from components.code_generation_mcp import KiloCodeIntegration
    
    kilocode = KiloCodeIntegration({
        "enabled": True,
        "kilocode_url": "http://localhost:8080",
        "timeout": 30
    })
    
    result = await kilocode.generate_code(
        "创建一个简单的Hello World API",
        "python",
        "api",
        "flask"
    )
    
    print(f"KiloCode直接调用结果: {result.get('success')}")
    if result.get('success'):
        print(f"生成代码长度: {len(result.get('generated_code', ''))} 字符")
        print(f"质量分数: {result.get('quality_score', 0):.2f}")
        print("✅ KiloCode集成类测试通过")
    else:
        print(f"❌ KiloCode集成类测试失败: {result.get('error')}")

if __name__ == "__main__":
    print("🧪 KiloCode集成测试套件")
    print("=" * 50)
    
    try:
        # 运行主要测试
        asyncio.run(test_kilocode_integration())
        
        # 运行直接测试
        asyncio.run(test_kilocode_direct())
        
        print("\n✅ 所有测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

