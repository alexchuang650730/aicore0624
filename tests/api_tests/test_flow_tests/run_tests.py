#!/usr/bin/env python3
"""
test_flow_mcp API 測試執行腳本
提供多種測試執行模式和報告生成功能
"""

import os
import sys
import json
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class TestRunner:
    """測試執行器"""
    
    def __init__(self, config_file: str = "test_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.results_dir = Path("test_results")
        self.results_dir.mkdir(exist_ok=True)
    
    def load_config(self) -> Dict:
        """載入配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件 {self.config_file} 不存在")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"配置文件格式錯誤: {e}")
            sys.exit(1)
    
    def run_smoke_tests(self) -> bool:
        """執行冒煙測試"""
        print("🔥 執行冒煙測試...")
        
        cmd = [
            "python", "-m", "pytest",
            "test_api_suite.py::TestExecuteAPI::test_requirement_analysis_basic",
            "test_api_suite.py::TestSystemAPI::test_system_health_check",
            "-v", "--tb=short",
            f"--junitxml={self.results_dir}/smoke_test_results.xml"
        ]
        
        return self._run_pytest_command(cmd, "smoke_test")
    
    def run_regression_tests(self) -> bool:
        """執行回歸測試"""
        print("🔄 執行回歸測試...")
        
        cmd = [
            "python", "-m", "pytest",
            "test_api_suite.py",
            "-m", "not slow and not performance",
            "-v", "--tb=short",
            f"--junitxml={self.results_dir}/regression_test_results.xml"
        ]
        
        return self._run_pytest_command(cmd, "regression_test")
    
    def run_performance_tests(self) -> bool:
        """執行性能測試"""
        print("⚡ 執行性能測試...")
        
        cmd = [
            "python", "-m", "pytest",
            "test_api_suite.py::TestPerformance",
            "-v", "--tb=short",
            f"--junitxml={self.results_dir}/performance_test_results.xml"
        ]
        
        return self._run_pytest_command(cmd, "performance_test")
    
    def run_security_tests(self) -> bool:
        """執行安全測試"""
        print("🔒 執行安全測試...")
        
        cmd = [
            "python", "-m", "pytest",
            "test_api_suite.py::TestExecuteAPINegative",
            "-v", "--tb=short",
            f"--junitxml={self.results_dir}/security_test_results.xml"
        ]
        
        return self._run_pytest_command(cmd, "security_test")
    
    def run_full_test_suite(self) -> bool:
        """執行完整測試套件"""
        print("🎯 執行完整測試套件...")
        
        cmd = [
            "python", "-m", "pytest",
            "test_api_suite.py",
            "-v", "--tb=short",
            f"--junitxml={self.results_dir}/full_test_results.xml",
            f"--html={self.results_dir}/full_test_report.html",
            "--self-contained-html"
        ]
        
        return self._run_pytest_command(cmd, "full_test")
    
    def run_parallel_tests(self, num_workers: int = 4) -> bool:
        """執行並行測試"""
        print(f"🚀 執行並行測試 (工作進程數: {num_workers})...")
        
        cmd = [
            "python", "-m", "pytest",
            "test_api_suite.py",
            "-m", "parallel",
            f"-n", str(num_workers),
            "-v", "--tb=short",
            f"--junitxml={self.results_dir}/parallel_test_results.xml"
        ]
        
        return self._run_pytest_command(cmd, "parallel_test")
    
    def _run_pytest_command(self, cmd: List[str], test_type: str) -> bool:
        """執行 pytest 命令"""
        start_time = time.time()
        
        try:
            # 設置環境變量
            env = os.environ.copy()
            env['PYTHONPATH'] = os.getcwd()
            
            # 執行測試
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=1800  # 30分鐘超時
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 保存執行日誌
            log_file = self.results_dir / f"{test_type}_execution.log"
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"測試類型: {test_type}\n")
                f.write(f"執行時間: {datetime.now().isoformat()}\n")
                f.write(f"持續時間: {duration:.2f} 秒\n")
                f.write(f"返回碼: {result.returncode}\n")
                f.write(f"命令: {' '.join(cmd)}\n\n")
                f.write("=== STDOUT ===\n")
                f.write(result.stdout)
                f.write("\n=== STDERR ===\n")
                f.write(result.stderr)
            
            # 輸出結果摘要
            if result.returncode == 0:
                print(f"✅ {test_type} 測試通過 (耗時: {duration:.2f}秒)")
                return True
            else:
                print(f"❌ {test_type} 測試失敗 (耗時: {duration:.2f}秒)")
                print(f"錯誤信息: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_type} 測試超時")
            return False
        except Exception as e:
            print(f"💥 {test_type} 測試執行異常: {e}")
            return False
    
    def generate_summary_report(self, test_results: Dict[str, bool]):
        """生成測試摘要報告"""
        print("\n📊 生成測試摘要報告...")
        
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        summary = {
            "execution_time": datetime.now().isoformat(),
            "total_test_suites": total_tests,
            "passed_test_suites": passed_tests,
            "failed_test_suites": failed_tests,
            "pass_rate": pass_rate,
            "test_results": test_results,
            "environment": {
                "base_url": self.config["api_config"]["base_url"],
                "python_version": sys.version,
                "working_directory": os.getcwd()
            }
        }
        
        # 保存 JSON 報告
        summary_file = self.results_dir / "test_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # 生成 Markdown 報告
        self._generate_markdown_report(summary)
        
        # 輸出控制台摘要
        print("\n" + "="*60)
        print("📋 測試執行摘要")
        print("="*60)
        print(f"總測試套件數: {total_tests}")
        print(f"通過套件數: {passed_tests}")
        print(f"失敗套件數: {failed_tests}")
        print(f"通過率: {pass_rate:.1f}%")
        print("\n詳細結果:")
        for test_name, result in test_results.items():
            status = "✅ 通過" if result else "❌ 失敗"
            print(f"  {test_name}: {status}")
        print("="*60)
        
        return summary
    
    def _generate_markdown_report(self, summary: Dict):
        """生成 Markdown 格式報告"""
        report_file = self.results_dir / "test_summary.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# test_flow_mcp API 測試摘要報告\n\n")
            f.write(f"**執行時間**: {summary['execution_time']}\n")
            f.write(f"**測試環境**: {summary['environment']['base_url']}\n\n")
            
            f.write("## 測試結果概覽\n\n")
            f.write(f"- **總測試套件數**: {summary['total_test_suites']}\n")
            f.write(f"- **通過套件數**: {summary['passed_test_suites']}\n")
            f.write(f"- **失敗套件數**: {summary['failed_test_suites']}\n")
            f.write(f"- **通過率**: {summary['pass_rate']:.1f}%\n\n")
            
            f.write("## 詳細結果\n\n")
            f.write("| 測試套件 | 狀態 |\n")
            f.write("|---------|------|\n")
            
            for test_name, result in summary['test_results'].items():
                status = "✅ 通過" if result else "❌ 失敗"
                f.write(f"| {test_name} | {status} |\n")
            
            f.write("\n## 測試文件位置\n\n")
            f.write("測試結果文件保存在 `test_results/` 目錄下：\n\n")
            f.write("- `test_summary.json` - JSON 格式摘要\n")
            f.write("- `*_test_results.xml` - JUnit XML 格式結果\n")
            f.write("- `*_execution.log` - 執行日誌\n")
            f.write("- `full_test_report.html` - HTML 格式詳細報告\n")
    
    def check_environment(self) -> bool:
        """檢查測試環境"""
        print("🔍 檢查測試環境...")
        
        # 檢查必要的 Python 包
        required_packages = ['pytest', 'requests', 'jsonschema']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ 缺少必要的 Python 包: {', '.join(missing_packages)}")
            print("請運行: pip install pytest requests jsonschema")
            return False
        
        # 檢查 API 服務可用性
        try:
            import requests
            base_url = self.config["api_config"]["base_url"]
            api_key = self.config["api_config"]["api_key"]
            
            response = requests.get(
                f"{base_url}/api/system/health",
                headers={'X-API-Key': api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ API 服務可用")
                return True
            else:
                print(f"❌ API 服務不可用 (狀態碼: {response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ 無法連接到 API 服務: {e}")
            return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="test_flow_mcp API 測試執行器")
    parser.add_argument("--config", default="test_config.json", help="配置文件路徑")
    parser.add_argument("--smoke", action="store_true", help="執行冒煙測試")
    parser.add_argument("--regression", action="store_true", help="執行回歸測試")
    parser.add_argument("--performance", action="store_true", help="執行性能測試")
    parser.add_argument("--security", action="store_true", help="執行安全測試")
    parser.add_argument("--full", action="store_true", help="執行完整測試套件")
    parser.add_argument("--parallel", type=int, metavar="N", help="執行並行測試 (指定工作進程數)")
    parser.add_argument("--check-env", action="store_true", help="檢查測試環境")
    parser.add_argument("--all", action="store_true", help="執行所有測試類型")
    
    args = parser.parse_args()
    
    # 創建測試執行器
    runner = TestRunner(args.config)
    
    # 檢查環境
    if args.check_env or not any([args.smoke, args.regression, args.performance, 
                                  args.security, args.full, args.parallel, args.all]):
        if not runner.check_environment():
            sys.exit(1)
        if args.check_env:
            return
    
    # 執行測試
    test_results = {}
    
    if args.all:
        # 執行所有測試類型
        test_results["smoke"] = runner.run_smoke_tests()
        test_results["regression"] = runner.run_regression_tests()
        test_results["security"] = runner.run_security_tests()
        test_results["performance"] = runner.run_performance_tests()
        test_results["full"] = runner.run_full_test_suite()
    else:
        # 執行指定的測試類型
        if args.smoke:
            test_results["smoke"] = runner.run_smoke_tests()
        
        if args.regression:
            test_results["regression"] = runner.run_regression_tests()
        
        if args.performance:
            test_results["performance"] = runner.run_performance_tests()
        
        if args.security:
            test_results["security"] = runner.run_security_tests()
        
        if args.full:
            test_results["full"] = runner.run_full_test_suite()
        
        if args.parallel:
            test_results["parallel"] = runner.run_parallel_tests(args.parallel)
    
    # 如果沒有指定任何測試類型，執行冒煙測試
    if not test_results:
        test_results["smoke"] = runner.run_smoke_tests()
    
    # 生成摘要報告
    summary = runner.generate_summary_report(test_results)
    
    # 根據測試結果設置退出碼
    if all(test_results.values()):
        print("\n🎉 所有測試都通過了！")
        sys.exit(0)
    else:
        print("\n💥 有測試失敗，請檢查詳細日誌")
        sys.exit(1)

if __name__ == "__main__":
    main()

