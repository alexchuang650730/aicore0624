#!/usr/bin/env python3
"""
环境检查器脚本
检查AICore运行环境的完整性和依赖
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path
import json

class EnvironmentChecker:
    """环境检查器"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.deployment_dir = self.script_dir.parent
        self.powerautomation_dir = self.deployment_dir.parent / "PowerAutomation"
        self.check_results = []
        
    def check_python_version(self):
        """检查Python版本"""
        print("🐍 检查Python版本...")
        
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major >= 3 and version.minor >= 8:
            status = "✅"
            message = f"Python版本 {version_str} 符合要求 (>= 3.8)"
            success = True
        else:
            status = "❌"
            message = f"Python版本 {version_str} 不符合要求 (需要 >= 3.8)"
            success = False
        
        print(f"   {status} {message}")
        
        self.check_results.append({
            'category': 'python',
            'item': 'version',
            'status': success,
            'message': message,
            'details': {
                'version': version_str,
                'required': '>= 3.8'
            }
        })
        
        return success
    
    def check_required_packages(self):
        """检查必需的Python包"""
        print("\n📦 检查必需的Python包...")
        
        required_packages = [
            'asyncio',
            'toml',
            'pathlib',
            'json',
            'datetime',
            'subprocess',
            'argparse'
        ]
        
        optional_packages = [
            'aiohttp',
            'numpy',
            'requests'
        ]
        
        all_success = True
        
        # 检查必需包
        for package in required_packages:
            try:
                importlib.import_module(package)
                print(f"   ✅ {package} - 已安装")
                self.check_results.append({
                    'category': 'packages',
                    'item': package,
                    'status': True,
                    'message': f"{package} 已安装",
                    'required': True
                })
            except ImportError:
                print(f"   ❌ {package} - 未安装 (必需)")
                all_success = False
                self.check_results.append({
                    'category': 'packages',
                    'item': package,
                    'status': False,
                    'message': f"{package} 未安装",
                    'required': True
                })
        
        # 检查可选包
        for package in optional_packages:
            try:
                importlib.import_module(package)
                print(f"   ✅ {package} - 已安装 (可选)")
                self.check_results.append({
                    'category': 'packages',
                    'item': package,
                    'status': True,
                    'message': f"{package} 已安装",
                    'required': False
                })
            except ImportError:
                print(f"   ⚠️ {package} - 未安装 (可选)")
                self.check_results.append({
                    'category': 'packages',
                    'item': package,
                    'status': False,
                    'message': f"{package} 未安装",
                    'required': False
                })
        
        return all_success
    
    def check_powerautomation_structure(self):
        """检查PowerAutomation目录结构"""
        print("\n🏗️ 检查PowerAutomation目录结构...")
        
        required_dirs = [
            'components',
            'core',
            'config',
            'tools'
        ]
        
        required_files = [
            'core/aicore3.py',
            'components/code_generation_mcp.py',
            'components/enhanced_test_flow_mcp_v4.py'
        ]
        
        all_success = True
        
        # 检查PowerAutomation目录是否存在
        if not self.powerautomation_dir.exists():
            print(f"   ❌ PowerAutomation目录不存在: {self.powerautomation_dir}")
            self.check_results.append({
                'category': 'structure',
                'item': 'powerautomation_dir',
                'status': False,
                'message': 'PowerAutomation目录不存在'
            })
            return False
        
        print(f"   ✅ PowerAutomation目录存在: {self.powerautomation_dir}")
        
        # 检查必需目录
        for dir_name in required_dirs:
            dir_path = self.powerautomation_dir / dir_name
            if dir_path.exists():
                print(f"   ✅ {dir_name}/ - 目录存在")
                self.check_results.append({
                    'category': 'structure',
                    'item': f'dir_{dir_name}',
                    'status': True,
                    'message': f"{dir_name} 目录存在"
                })
            else:
                print(f"   ❌ {dir_name}/ - 目录不存在")
                all_success = False
                self.check_results.append({
                    'category': 'structure',
                    'item': f'dir_{dir_name}',
                    'status': False,
                    'message': f"{dir_name} 目录不存在"
                })
        
        # 检查必需文件
        for file_path in required_files:
            full_path = self.powerautomation_dir / file_path
            if full_path.exists():
                print(f"   ✅ {file_path} - 文件存在")
                self.check_results.append({
                    'category': 'structure',
                    'item': f'file_{file_path.replace("/", "_")}',
                    'status': True,
                    'message': f"{file_path} 文件存在"
                })
            else:
                print(f"   ❌ {file_path} - 文件不存在")
                all_success = False
                self.check_results.append({
                    'category': 'structure',
                    'item': f'file_{file_path.replace("/", "_")}',
                    'status': False,
                    'message': f"{file_path} 文件不存在"
                })
        
        return all_success
    
    def check_deployment_structure(self):
        """检查deployment目录结构"""
        print("\n📁 检查deployment目录结构...")
        
        required_dirs = [
            'demos',
            'scripts',
            'config',
            'templates'
        ]
        
        demo_dirs = [
            'demos/demo1_snake_game',
            'demos/demo2_code_generation',
            'demos/demo3_mcp_showcase'
        ]
        
        all_success = True
        
        # 检查deployment目录
        if not self.deployment_dir.exists():
            print(f"   ❌ deployment目录不存在: {self.deployment_dir}")
            return False
        
        print(f"   ✅ deployment目录存在: {self.deployment_dir}")
        
        # 检查必需目录
        for dir_name in required_dirs:
            dir_path = self.deployment_dir / dir_name
            if dir_path.exists():
                print(f"   ✅ {dir_name}/ - 目录存在")
                self.check_results.append({
                    'category': 'deployment',
                    'item': f'dir_{dir_name}',
                    'status': True,
                    'message': f"{dir_name} 目录存在"
                })
            else:
                print(f"   ❌ {dir_name}/ - 目录不存在")
                all_success = False
                self.check_results.append({
                    'category': 'deployment',
                    'item': f'dir_{dir_name}',
                    'status': False,
                    'message': f"{dir_name} 目录不存在"
                })
        
        # 检查演示目录
        for demo_dir in demo_dirs:
            dir_path = self.deployment_dir / demo_dir
            if dir_path.exists():
                print(f"   ✅ {demo_dir}/ - 演示目录存在")
                
                # 检查演示文件
                demo_files = list(dir_path.glob("*_demo.py"))
                config_files = list(dir_path.glob("demo_config.toml"))
                readme_files = list(dir_path.glob("README.md"))
                
                if demo_files:
                    print(f"      ✅ 演示脚本: {demo_files[0].name}")
                else:
                    print(f"      ❌ 缺少演示脚本")
                    all_success = False
                
                if config_files:
                    print(f"      ✅ 配置文件: {config_files[0].name}")
                else:
                    print(f"      ❌ 缺少配置文件")
                    all_success = False
                
                if readme_files:
                    print(f"      ✅ 说明文档: {readme_files[0].name}")
                else:
                    print(f"      ⚠️ 缺少说明文档")
                
                self.check_results.append({
                    'category': 'deployment',
                    'item': f'demo_{demo_dir.replace("/", "_")}',
                    'status': bool(demo_files and config_files),
                    'message': f"{demo_dir} 演示完整性检查"
                })
                
            else:
                print(f"   ❌ {demo_dir}/ - 演示目录不存在")
                all_success = False
                self.check_results.append({
                    'category': 'deployment',
                    'item': f'demo_{demo_dir.replace("/", "_")}',
                    'status': False,
                    'message': f"{demo_dir} 演示目录不存在"
                })
        
        return all_success
    
    def check_permissions(self):
        """检查文件权限"""
        print("\n🔐 检查文件权限...")
        
        # 检查脚本执行权限
        script_files = [
            self.script_dir / "demo_runner.py",
            self.script_dir / "environment_checker.py"
        ]
        
        all_success = True
        
        for script_file in script_files:
            if script_file.exists():
                if os.access(script_file, os.R_OK):
                    print(f"   ✅ {script_file.name} - 可读")
                else:
                    print(f"   ❌ {script_file.name} - 不可读")
                    all_success = False
                
                if os.access(script_file, os.X_OK):
                    print(f"   ✅ {script_file.name} - 可执行")
                else:
                    print(f"   ⚠️ {script_file.name} - 不可执行 (可能需要chmod +x)")
                
                self.check_results.append({
                    'category': 'permissions',
                    'item': script_file.name,
                    'status': os.access(script_file, os.R_OK),
                    'message': f"{script_file.name} 权限检查"
                })
        
        return all_success
    
    def run_all_checks(self):
        """运行所有检查"""
        print("🔍 AICore环境检查器")
        print("=" * 50)
        
        checks = [
            ("Python版本", self.check_python_version),
            ("Python包", self.check_required_packages),
            ("PowerAutomation结构", self.check_powerautomation_structure),
            ("Deployment结构", self.check_deployment_structure),
            ("文件权限", self.check_permissions)
        ]
        
        results = {}
        
        for check_name, check_func in checks:
            try:
                results[check_name] = check_func()
            except Exception as e:
                print(f"\n❌ {check_name} 检查时发生错误: {str(e)}")
                results[check_name] = False
        
        # 生成总结
        self.generate_summary(results)
        
        return results
    
    def generate_summary(self, results):
        """生成检查总结"""
        print("\n" + "=" * 50)
        print("📊 环境检查总结")
        print("=" * 50)
        
        total_checks = len(results)
        passed_checks = len([r for r in results.values() if r])
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        print(f"总检查项: {total_checks}")
        print(f"通过检查: {passed_checks}")
        print(f"失败检查: {total_checks - passed_checks}")
        print(f"通过率: {success_rate:.1f}%")
        print()
        
        print("详细结果:")
        for check_name, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {check_name}")
        
        # 保存检查结果
        self.save_results(results, success_rate)
        
        # 提供建议
        if success_rate < 100:
            print("\n💡 修复建议:")
            self.provide_suggestions()
        else:
            print("\n🎉 环境检查全部通过！AICore已准备就绪。")
    
    def provide_suggestions(self):
        """提供修复建议"""
        failed_checks = [r for r in self.check_results if not r['status']]
        
        suggestions = []
        
        for check in failed_checks:
            if check['category'] == 'python':
                suggestions.append("升级Python到3.8或更高版本")
            elif check['category'] == 'packages':
                if check.get('required'):
                    suggestions.append(f"安装必需包: pip install {check['item']}")
                else:
                    suggestions.append(f"安装可选包: pip install {check['item']}")
            elif check['category'] == 'structure':
                suggestions.append(f"检查并创建缺失的目录或文件: {check['item']}")
            elif check['category'] == 'deployment':
                suggestions.append(f"检查deployment目录结构: {check['item']}")
            elif check['category'] == 'permissions':
                suggestions.append(f"修复文件权限: chmod +x {check['item']}")
        
        # 去重并显示建议
        unique_suggestions = list(set(suggestions))
        for i, suggestion in enumerate(unique_suggestions, 1):
            print(f"  {i}. {suggestion}")
    
    def save_results(self, results, success_rate):
        """保存检查结果"""
        report = {
            'timestamp': str(Path(__file__).stat().st_mtime),
            'summary': {
                'total_checks': len(results),
                'passed_checks': len([r for r in results.values() if r]),
                'success_rate': success_rate
            },
            'results': results,
            'detailed_results': self.check_results
        }
        
        results_dir = self.deployment_dir / "results"
        results_dir.mkdir(exist_ok=True)
        
        result_file = results_dir / "environment_check.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 检查结果已保存: {result_file}")

def main():
    """主函数"""
    checker = EnvironmentChecker()
    results = checker.run_all_checks()
    
    # 返回适当的退出码
    if all(results.values()):
        sys.exit(0)  # 所有检查通过
    else:
        sys.exit(1)  # 有检查失败

if __name__ == "__main__":
    main()

