#!/usr/bin/env python3
"""
Demo1: 贪吃蛇游戏生成演示
展示AICore代码生成能力的完整流程演示
"""

import sys
import os
import asyncio
import sys
from pathlib import Path

# 添加PowerAutomation到Python路径
powerautomation_dir = Path(__file__).parent.parent.parent / "PowerAutomation"
sys.path.insert(0, str(powerautomation_dir))

from components.code_generation_mcp import CodeGenerationMcprom core.aicore3 import AICore3

class SnakeGameDemo:
    """贪吃蛇游戏演示类"""
    
    def __init__(self, config_path: str = None):
        """初始化演示"""
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), 'demo_config.toml')
        self.config = self._load_config()
        self.demo_name = self.config['demo_settings']['name']
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _load_config(self) -> dict:
        """加载演示配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return toml.load(f)
        except FileNotFoundError:
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """获取默认配置"""
        return {
            'demo_settings': {
                'name': 'Snake Game Generation Demo',
                'description': '完整的贪吃蛇游戏生成演示',
                'target_audience': '客户演示、技术展示'
            },
            'generation_config': {
                'game_type': 'snake',
                'language': 'python',
                'framework': 'pygame',
                'complexity_level': 'intermediate'
            },
            'display_config': {
                'show_generation_process': True,
                'show_code_analysis': True,
                'show_performance_metrics': True
            }
        }
    
    async def run_demo(self):
        """运行完整演示"""
        print(f"🎮 {self.demo_name}")
        print("=" * 60)
        print(f"📋 描述: {self.config['demo_settings']['description']}")
        print(f"🎯 目标: {self.config['demo_settings']['target_audience']}")
        print()
        
        try:
            # 第一步: 初始化AICore
            print("🚀 第一步: 初始化AICore系统")
            aicore = AICore3()
            await aicore.initialize()
            print("✅ AICore系统初始化完成")
            print()
            
            # 第二步: 配置代码生成参数
            print("⚙️ 第二步: 配置代码生成参数")
            generation_config = self.config['generation_config']
            print(f"   游戏类型: {generation_config['game_type']}")
            print(f"   编程语言: {generation_config['language']}")
            print(f"   框架: {generation_config['framework']}")
            print(f"   复杂度: {generation_config['complexity_level']}")
            print()
            
            # 第三步: 生成贪吃蛇游戏
            print("🎯 第三步: 生成贪吃蛇游戏代码")
            task_request = {
                "task_type": "code_generation",
                "requirements": {
                    "project_type": "game",
                    "game_type": generation_config['game_type'],
                    "language": generation_config['language'],
                    "framework": generation_config['framework'],
                    "features": [
                        "游戏窗口和界面",
                        "蛇的移动控制",
                        "食物生成和碰撞检测",
                        "分数系统",
                        "游戏结束检测",
                        "重新开始功能"
                    ],
                    "complexity": generation_config['complexity_level']
                },
                "quality_requirements": {
                    "code_quality": "high",
                    "documentation": "comprehensive",
                    "testing": "basic"
                }
            }
            
            # 使用AICore处理任务
            result = await aicore.process_task(task_request)
            
            if result.get('success'):
                print("✅ 贪吃蛇游戏生成成功!")
                
                # 保存生成的代码
                game_code = result.get('generated_code', '')
                output_file = os.path.join(self.output_dir, 'snake_game.py')
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(game_code)
                print(f"📁 游戏代码已保存到: {output_file}")
                
                # 显示代码分析
                if self.config['display_config']['show_code_analysis']:
                    print("\n📊 代码质量分析:")
                    analysis = result.get('quality_analysis', {})
                    print(f"   代码行数: {analysis.get('lines_of_code', 'N/A')}")
                    print(f"   质量分数: {analysis.get('quality_score', 'N/A')}/10")
                    print(f"   复杂度: {analysis.get('complexity', 'N/A')}")
                    print(f"   可维护性: {analysis.get('maintainability', 'N/A')}")
                
                # 显示性能指标
                if self.config['display_config']['show_performance_metrics']:
                    print("\n⚡ 性能指标:")
                    metrics = result.get('performance_metrics', {})
                    print(f"   生成时间: {metrics.get('generation_time', 'N/A')}秒")
                    print(f"   处理速度: {metrics.get('processing_speed', 'N/A')} 行/秒")
                    print(f"   内存使用: {metrics.get('memory_usage', 'N/A')} MB")
                
                print("\n🎉 演示完成!")
                print(f"🎮 您可以运行生成的游戏: python {output_file}")
                
            else:
                print("❌ 游戏生成失败")
                error_msg = result.get('error', '未知错误')
                print(f"错误信息: {error_msg}")
                
        except Exception as e:
            print(f"❌ 演示过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def generate_demo_report(self):
        """生成演示报告"""
        report_path = os.path.join(self.output_dir, 'demo_report.md')
        
        report_content = f"""# {self.demo_name} - 演示报告

## 演示概述
- **演示名称**: {self.config['demo_settings']['name']}
- **描述**: {self.config['demo_settings']['description']}
- **目标受众**: {self.config['demo_settings']['target_audience']}

## 生成配置
- **游戏类型**: {self.config['generation_config']['game_type']}
- **编程语言**: {self.config['generation_config']['language']}
- **框架**: {self.config['generation_config']['framework']}
- **复杂度**: {self.config['generation_config']['complexity_level']}

## 演示流程
1. 初始化AICore系统
2. 配置代码生成参数
3. 生成贪吃蛇游戏代码
4. 分析代码质量和性能
5. 保存结果和报告

## 输出文件
- `snake_game.py` - 生成的贪吃蛇游戏
- `demo_report.md` - 本演示报告

## 使用说明
```bash
# 运行演示
python snake_game_demo.py

# 运行生成的游戏
python output/snake_game.py
```

## 技术特点
- 完整的游戏功能实现
- 高质量代码生成
- 实时性能监控
- 详细的质量分析

---
*演示由AICore系统自动生成*
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 演示报告已生成: {report_path}")

async def main():
    """主函数"""
    demo = SnakeGameDemo()
    await demo.run_demo()
    demo.generate_demo_report()

if __name__ == "__main__":
    asyncio.run(main())

