#!/usr/bin/env python3
"""
演示运行器脚本
用于批量运行和管理AICore演示
"""

import os
import sys
import asyncio
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
import json

class DemoRunner:
    """演示运行器"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.deployment_dir = self.script_dir.parent
        self.demos_dir = self.deployment_dir / "demos"
        self.results_dir = self.deployment_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        
    def list_demos(self):
        """列出所有可用的演示"""
        demos = []
        if self.demos_dir.exists():
            for demo_dir in self.demos_dir.iterdir():
                if demo_dir.is_dir() and demo_dir.name.startswith('demo'):
                    demo_script = None
                    for py_file in demo_dir.glob("*.py"):
                        if py_file.name.endswith("_demo.py"):
                            demo_script = py_file
                            break
                    
                    if demo_script:
                        demos.append({
                            'name': demo_dir.name,
                            'path': demo_dir,
                            'script': demo_script,
                            'description': self._get_demo_description(demo_dir)
                        })
        return demos
    
    def _get_demo_description(self, demo_dir):
        """获取演示描述"""
        readme_file = demo_dir / "README.md"
        if readme_file.exists():
            try:
                with open(readme_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith('## 📋 演示概述'):
                            # 找到下一行的描述
                            idx = lines.index(line)
                            if idx + 2 < len(lines):
                                return lines[idx + 2].strip()
            except:
                pass
        return "AICore演示"
    
    async def run_demo(self, demo_name, verbose=False):
        """运行指定的演示"""
        demos = self.list_demos()
        demo = next((d for d in demos if d['name'] == demo_name), None)
        
        if not demo:
            print(f"❌ 演示 '{demo_name}' 不存在")
            return False
        
        print(f"🚀 运行演示: {demo['name']}")
        print(f"📋 描述: {demo['description']}")
        print(f"📁 路径: {demo['path']}")
        print()
        
        # 记录开始时间
        start_time = datetime.now()
        
        try:
            # 切换到演示目录
            original_cwd = os.getcwd()
            os.chdir(demo['path'])
            
            # 运行演示脚本
            cmd = [sys.executable, demo['script'].name]
            
            if verbose:
                print(f"🔧 执行命令: {' '.join(cmd)}")
                print()
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            stdout, stderr = process.communicate()
            
            # 恢复原始工作目录
            os.chdir(original_cwd)
            
            # 记录结束时间
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 判断执行结果
            success = process.returncode == 0
            
            if success:
                print("✅ 演示执行成功!")
            else:
                print("❌ 演示执行失败!")
            
            print(f"⏱️ 执行时间: {duration:.2f}秒")
            
            if verbose or not success:
                if stdout:
                    print("\n📤 标准输出:")
                    print(stdout)
                if stderr:
                    print("\n📤 错误输出:")
                    print(stderr)
            
            # 保存执行结果
            result = {
                'demo_name': demo_name,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration': duration,
                'success': success,
                'return_code': process.returncode,
                'stdout': stdout,
                'stderr': stderr
            }
            
            result_file = self.results_dir / f"{demo_name}_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"📄 结果已保存: {result_file}")
            
            return success
            
        except Exception as e:
            print(f"❌ 运行演示时发生异常: {str(e)}")
            return False
    
    async def run_all_demos(self, verbose=False):
        """运行所有演示"""
        demos = self.list_demos()
        
        if not demos:
            print("❌ 没有找到可用的演示")
            return
        
        print(f"🎯 发现 {len(demos)} 个演示，开始批量运行...")
        print()
        
        results = []
        
        for i, demo in enumerate(demos, 1):
            print(f"[{i}/{len(demos)}] 运行演示: {demo['name']}")
            success = await self.run_demo(demo['name'], verbose)
            results.append({
                'name': demo['name'],
                'success': success
            })
            print()
        
        # 生成总结报告
        self._generate_batch_report(results)
    
    def _generate_batch_report(self, results):
        """生成批量运行报告"""
        total_demos = len(results)
        successful_demos = len([r for r in results if r['success']])
        success_rate = (successful_demos / total_demos * 100) if total_demos > 0 else 0
        
        print("📊 批量运行总结:")
        print(f"   总演示数: {total_demos}")
        print(f"   成功数: {successful_demos}")
        print(f"   失败数: {total_demos - successful_demos}")
        print(f"   成功率: {success_rate:.1f}%")
        print()
        
        print("📋 详细结果:")
        for result in results:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['name']}")
        
        # 保存批量报告
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_demos': total_demos,
            'successful_demos': successful_demos,
            'success_rate': success_rate,
            'results': results
        }
        
        report_file = self.results_dir / f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 批量报告已保存: {report_file}")
    
    def clean_results(self, days=7):
        """清理旧的结果文件"""
        if not self.results_dir.exists():
            return
        
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        cleaned_count = 0
        
        for result_file in self.results_dir.glob("*.json"):
            if result_file.stat().st_mtime < cutoff_time:
                result_file.unlink()
                cleaned_count += 1
        
        print(f"🧹 已清理 {cleaned_count} 个超过 {days} 天的结果文件")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AICore演示运行器")
    parser.add_argument('action', choices=['list', 'run', 'run-all', 'clean'], 
                       help='要执行的操作')
    parser.add_argument('--demo', '-d', help='要运行的演示名称 (用于run操作)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='显示详细输出')
    parser.add_argument('--days', type=int, default=7, 
                       help='清理多少天前的结果文件 (用于clean操作)')
    
    args = parser.parse_args()
    
    runner = DemoRunner()
    
    if args.action == 'list':
        demos = runner.list_demos()
        if demos:
            print("📋 可用的演示:")
            for demo in demos:
                print(f"   🎯 {demo['name']}: {demo['description']}")
        else:
            print("❌ 没有找到可用的演示")
    
    elif args.action == 'run':
        if not args.demo:
            print("❌ 请指定要运行的演示名称 (--demo)")
            return
        
        asyncio.run(runner.run_demo(args.demo, args.verbose))
    
    elif args.action == 'run-all':
        asyncio.run(runner.run_all_demos(args.verbose))
    
    elif args.action == 'clean':
        runner.clean_results(args.days)

if __name__ == "__main__":
    main()

