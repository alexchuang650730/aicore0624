#!/usr/bin/env python3
"""
Demo2: 多场景代码生成演示
展示AICore在不同场景下的代码生成能力
"""

import sys
import os
import asyncio
import toml
from pathlib import Path
from datetime import datetime

# 添加PowerAutomation到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
powerautomation_dir = project_root / "PowerAutomation"
sys.path.insert(0, str(powerautomation_dir))
sys.path.insert(0, str(project_root))

from components.code_generation_mcp import CodeGenerationMcp
from core.aicore3 import AICore3

class CodeGenerationDemo:
    """多场景代码生成演示类"""
    
    def __init__(self, config_path: str = None):
        """初始化演示"""
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), 'demo_config.toml')
        self.config = self._load_config()
        self.demo_name = self.config['demo_settings']['name']
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(self.output_dir, exist_ok=True)
        self.results = []
        
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
                'name': 'Multi-Scenario Code Generation Demo',
                'description': '多场景代码生成能力展示'
            },
            'scenarios': {
                'api_generation': True,
                'frontend_components': True,
                'backend_services': True,
                'database_schemas': True
            },
            'languages': {
                'python': True,
                'javascript': True,
                'typescript': True,
                'java': False
            }
        }
    
    async def run_demo(self):
        """运行完整演示"""
        print(f"🚀 {self.demo_name}")
        print("=" * 60)
        print(f"📋 描述: {self.config['demo_settings']['description']}")
        print()
        
        try:
            # 初始化AICore
            print("🔧 初始化AICore系统...")
            aicore = AICore3()
            await aicore.initialize()
            print("✅ AICore系统初始化完成")
            print()
            
            # 运行各个场景演示
            scenarios = self.config['scenarios']
            
            if scenarios.get('api_generation'):
                await self._demo_api_generation(aicore)
            
            if scenarios.get('frontend_components'):
                await self._demo_frontend_components(aicore)
            
            if scenarios.get('backend_services'):
                await self._demo_backend_services(aicore)
            
            if scenarios.get('database_schemas'):
                await self._demo_database_schemas(aicore)
            
            # 生成总结报告
            self._generate_summary_report()
            
            print("\n🎉 所有演示场景完成!")
            print(f"📁 结果已保存到: {self.output_dir}")
            
        except Exception as e:
            print(f"❌ 演示过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
    
    async def _demo_api_generation(self, aicore):
        """API生成演示"""
        print("🌐 场景1: API接口生成")
        print("-" * 40)
        
        task_request = {
            "task_type": "code_generation",
            "requirements": {
                "project_type": "api",
                "api_type": "rest",
                "language": "python",
                "framework": "fastapi",
                "endpoints": [
                    {"method": "GET", "path": "/users", "description": "获取用户列表"},
                    {"method": "POST", "path": "/users", "description": "创建新用户"},
                    {"method": "GET", "path": "/users/{id}", "description": "获取用户详情"},
                    {"method": "PUT", "path": "/users/{id}", "description": "更新用户信息"},
                    {"method": "DELETE", "path": "/users/{id}", "description": "删除用户"}
                ],
                "features": ["数据验证", "错误处理", "API文档", "认证授权"]
            }
        }
        
        result = await aicore.process_task(task_request)
        
        if result.get('success'):
            print("✅ API代码生成成功!")
            
            # 保存生成的代码
            api_code = result.get('generated_code', '')
            output_file = os.path.join(self.output_dir, 'user_api.py')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(api_code)
            
            print(f"📁 API代码已保存: {output_file}")
            
            # 记录结果
            self.results.append({
                'scenario': 'API生成',
                'language': 'Python',
                'framework': 'FastAPI',
                'success': True,
                'output_file': output_file,
                'quality_score': result.get('quality_analysis', {}).get('quality_score', 'N/A'),
                'generation_time': result.get('performance_metrics', {}).get('generation_time', 'N/A')
            })
            
        else:
            print("❌ API生成失败")
            self.results.append({
                'scenario': 'API生成',
                'success': False,
                'error': result.get('error', '未知错误')
            })
        
        print()
    
    async def _demo_frontend_components(self, aicore):
        """前端组件生成演示"""
        print("🎨 场景2: 前端组件生成")
        print("-" * 40)
        
        task_request = {
            "task_type": "code_generation",
            "requirements": {
                "project_type": "frontend",
                "component_type": "react",
                "language": "typescript",
                "components": [
                    {
                        "name": "UserCard",
                        "type": "display",
                        "props": ["user", "onEdit", "onDelete"],
                        "features": ["头像显示", "信息展示", "操作按钮"]
                    },
                    {
                        "name": "UserForm",
                        "type": "form",
                        "props": ["initialData", "onSubmit", "onCancel"],
                        "features": ["表单验证", "错误提示", "提交处理"]
                    }
                ],
                "styling": "tailwindcss",
                "features": ["响应式设计", "无障碍支持", "TypeScript类型"]
            }
        }
        
        result = await aicore.process_task(task_request)
        
        if result.get('success'):
            print("✅ 前端组件生成成功!")
            
            # 保存生成的代码
            component_code = result.get('generated_code', '')
            output_file = os.path.join(self.output_dir, 'user_components.tsx')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(component_code)
            
            print(f"📁 组件代码已保存: {output_file}")
            
            # 记录结果
            self.results.append({
                'scenario': '前端组件',
                'language': 'TypeScript',
                'framework': 'React',
                'success': True,
                'output_file': output_file,
                'quality_score': result.get('quality_analysis', {}).get('quality_score', 'N/A'),
                'generation_time': result.get('performance_metrics', {}).get('generation_time', 'N/A')
            })
            
        else:
            print("❌ 前端组件生成失败")
            self.results.append({
                'scenario': '前端组件',
                'success': False,
                'error': result.get('error', '未知错误')
            })
        
        print()
    
    async def _demo_backend_services(self, aicore):
        """后端服务生成演示"""
        print("⚙️ 场景3: 后端服务生成")
        print("-" * 40)
        
        task_request = {
            "task_type": "code_generation",
            "requirements": {
                "project_type": "backend",
                "service_type": "microservice",
                "language": "python",
                "framework": "flask",
                "services": [
                    {
                        "name": "UserService",
                        "description": "用户管理服务",
                        "methods": ["create_user", "get_user", "update_user", "delete_user"]
                    },
                    {
                        "name": "AuthService", 
                        "description": "认证授权服务",
                        "methods": ["login", "logout", "verify_token", "refresh_token"]
                    }
                ],
                "database": "postgresql",
                "features": ["数据库连接", "错误处理", "日志记录", "配置管理"]
            }
        }
        
        result = await aicore.process_task(task_request)
        
        if result.get('success'):
            print("✅ 后端服务生成成功!")
            
            # 保存生成的代码
            service_code = result.get('generated_code', '')
            output_file = os.path.join(self.output_dir, 'user_service.py')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(service_code)
            
            print(f"📁 服务代码已保存: {output_file}")
            
            # 记录结果
            self.results.append({
                'scenario': '后端服务',
                'language': 'Python',
                'framework': 'Flask',
                'success': True,
                'output_file': output_file,
                'quality_score': result.get('quality_analysis', {}).get('quality_score', 'N/A'),
                'generation_time': result.get('performance_metrics', {}).get('generation_time', 'N/A')
            })
            
        else:
            print("❌ 后端服务生成失败")
            self.results.append({
                'scenario': '后端服务',
                'success': False,
                'error': result.get('error', '未知错误')
            })
        
        print()
    
    async def _demo_database_schemas(self, aicore):
        """数据库模式生成演示"""
        print("🗄️ 场景4: 数据库模式生成")
        print("-" * 40)
        
        task_request = {
            "task_type": "code_generation",
            "requirements": {
                "project_type": "database",
                "database_type": "postgresql",
                "schema_name": "user_management",
                "tables": [
                    {
                        "name": "users",
                        "columns": [
                            {"name": "id", "type": "SERIAL", "constraints": ["PRIMARY KEY"]},
                            {"name": "username", "type": "VARCHAR(50)", "constraints": ["UNIQUE", "NOT NULL"]},
                            {"name": "email", "type": "VARCHAR(100)", "constraints": ["UNIQUE", "NOT NULL"]},
                            {"name": "password_hash", "type": "VARCHAR(255)", "constraints": ["NOT NULL"]},
                            {"name": "created_at", "type": "TIMESTAMP", "constraints": ["DEFAULT CURRENT_TIMESTAMP"]},
                            {"name": "updated_at", "type": "TIMESTAMP", "constraints": ["DEFAULT CURRENT_TIMESTAMP"]}
                        ]
                    },
                    {
                        "name": "user_profiles",
                        "columns": [
                            {"name": "id", "type": "SERIAL", "constraints": ["PRIMARY KEY"]},
                            {"name": "user_id", "type": "INTEGER", "constraints": ["REFERENCES users(id)"]},
                            {"name": "first_name", "type": "VARCHAR(50)"},
                            {"name": "last_name", "type": "VARCHAR(50)"},
                            {"name": "avatar_url", "type": "TEXT"},
                            {"name": "bio", "type": "TEXT"}
                        ]
                    }
                ],
                "features": ["索引优化", "外键约束", "触发器", "视图"]
            }
        }
        
        result = await aicore.process_task(task_request)
        
        if result.get('success'):
            print("✅ 数据库模式生成成功!")
            
            # 保存生成的代码
            schema_code = result.get('generated_code', '')
            output_file = os.path.join(self.output_dir, 'database_schema.sql')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(schema_code)
            
            print(f"📁 数据库模式已保存: {output_file}")
            
            # 记录结果
            self.results.append({
                'scenario': '数据库模式',
                'language': 'SQL',
                'framework': 'PostgreSQL',
                'success': True,
                'output_file': output_file,
                'quality_score': result.get('quality_analysis', {}).get('quality_score', 'N/A'),
                'generation_time': result.get('performance_metrics', {}).get('generation_time', 'N/A')
            })
            
        else:
            print("❌ 数据库模式生成失败")
            self.results.append({
                'scenario': '数据库模式',
                'success': False,
                'error': result.get('error', '未知错误')
            })
        
        print()
    
    def _generate_summary_report(self):
        """生成总结报告"""
        report_path = os.path.join(self.output_dir, 'demo_summary_report.md')
        
        # 计算统计信息
        total_scenarios = len(self.results)
        successful_scenarios = len([r for r in self.results if r.get('success')])
        success_rate = (successful_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0
        
        # 生成报告内容
        report_content = f"""# {self.demo_name} - 总结报告

## 演示概述
- **演示时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **总场景数**: {total_scenarios}
- **成功场景数**: {successful_scenarios}
- **成功率**: {success_rate:.1f}%

## 场景结果详情

"""
        
        for i, result in enumerate(self.results, 1):
            status = "✅ 成功" if result.get('success') else "❌ 失败"
            report_content += f"""### 场景{i}: {result['scenario']}
- **状态**: {status}
- **语言**: {result.get('language', 'N/A')}
- **框架**: {result.get('framework', 'N/A')}
"""
            
            if result.get('success'):
                report_content += f"""- **输出文件**: {result.get('output_file', 'N/A')}
- **质量分数**: {result.get('quality_score', 'N/A')}
- **生成时间**: {result.get('generation_time', 'N/A')}秒
"""
            else:
                report_content += f"- **错误信息**: {result.get('error', 'N/A')}\n"
            
            report_content += "\n"
        
        report_content += f"""## 技术栈覆盖

### 编程语言
- Python ✅
- TypeScript ✅
- SQL ✅

### 框架和技术
- FastAPI (Python Web框架)
- React (前端框架)
- Flask (Python微服务框架)
- PostgreSQL (数据库)
- TailwindCSS (样式框架)

## 生成的文件

"""
        
        for result in self.results:
            if result.get('success') and result.get('output_file'):
                filename = os.path.basename(result['output_file'])
                report_content += f"- `{filename}` - {result['scenario']}\n"
        
        report_content += f"""
## 演示价值

### 技术展示
- 多语言代码生成能力
- 不同项目类型支持
- 完整的开发栈覆盖
- 高质量代码输出

### 实用价值
- 快速原型开发
- 标准化代码模板
- 最佳实践示例
- 开发效率提升

## 使用建议

1. **API开发**: 使用生成的FastAPI代码作为起点
2. **前端开发**: 参考React组件的最佳实践
3. **后端服务**: 基于Flask服务模板扩展功能
4. **数据库设计**: 使用生成的SQL模式作为基础

---
*报告由AICore系统自动生成*
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 总结报告已生成: {report_path}")

async def main():
    """主函数"""
    demo = CodeGenerationDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())

