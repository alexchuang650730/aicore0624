#!/usr/bin/env python3
"""
SmartInvention API 測試執行腳本
仿照 test_flow_api_examples 的結構，提供多種測試模式和報告生成功能

使用方式:
    python run_tests.py --smoke                    # 冒煙測試
    python run_tests.py --regression               # 回歸測試
    python run_tests.py --performance              # 性能測試
    python run_tests.py --integration              # 集成測試
    python run_tests.py --full                     # 完整測試
    python run_tests.py --check-env                # 環境檢查
"""

import asyncio
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# 導入測試套件
from test_api_suite import SmartInventionAPITestSuite, TestResult

class SmartInventionTestRunner:
    """SmartInvention 測試執行器"""
    
    def __init__(self, config_file: str = "test_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self.test_suite = SmartInventionAPITestSuite(self.config)
        self.results_dir = Path("test_results")
        self.results_dir.mkdir(exist_ok=True)
    
    def _load_config(self) -> Dict:
        """載入測試配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 配置文件 {self.config_file} 不存在")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式錯誤: {e}")
            sys.exit(1)
    
    async def check_environment(self) -> bool:
        """檢查測試環境"""
        print("🔍 檢查測試環境...")
        
        # 檢查 API 服務是否可用
        try:
            import aiohttp
            base_url = self.config["api_config"]["base_url"]
            health_endpoint = self.config["endpoints"]["health_check"]
            
            async with aiohttp.ClientSession() as session:
                url = f"{base_url}{health_endpoint}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        print(f"✅ API 服務可用: {url}")
                        return True
                    else:
                        print(f"❌ API 服務不可用: {url} (HTTP {response.status})")
                        return False
        except Exception as e:
            print(f"❌ 無法連接到 API 服務: {e}")
            return False
    
    async def run_smoke_tests(self) -> List[TestResult]:
        """運行冒煙測試"""
        print("🚀 運行冒煙測試...")
        
        # 只運行基礎功能測試
        results = []
        
        await self.test_suite.test_health_check()
        await self.test_suite.test_get_latest_conversations()
        await self.test_suite.test_search_conversations()
        
        return self.test_suite.test_results
    
    async def run_regression_tests(self) -> List[TestResult]:
        """運行回歸測試"""
        print("🔄 運行回歸測試...")
        
        # 運行核心功能測試
        results = []
        
        await self.test_suite.test_health_check()
        await self.test_suite.test_get_latest_conversations()
        await self.test_suite.test_search_conversations()
        await self.test_suite.test_interventions_needed()
        await self.test_suite.test_smartinvention_process()
        await self.test_suite.test_conversation_analysis()
        await self.test_suite.test_incremental_comparison()
        
        return self.test_suite.test_results
    
    async def run_performance_tests(self) -> List[TestResult]:
        """運行性能測試"""
        print("⚡ 運行性能測試...")
        
        # 運行性能相關測試
        await self.test_suite.test_concurrent_requests()
        await self.test_suite.test_large_conversation_handling()
        
        return self.test_suite.test_results
    
    async def run_integration_tests(self) -> List[TestResult]:
        """運行集成測試"""
        print("🔗 運行集成測試...")
        
        # 運行集成測試
        await self.test_suite.test_manus_comparison_workflow()
        await self.test_suite.test_hitl_middleware()
        
        return self.test_suite.test_results
    
    async def run_full_tests(self) -> List[TestResult]:
        """運行完整測試套件"""
        print("🎯 運行完整測試套件...")
        
        # 運行所有測試
        return await self.test_suite.run_all_tests()
    
    def generate_html_report(self, report: Dict, output_file: str):
        """生成 HTML 格式報告"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartInvention API 測試報告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric {{ background-color: #e8f4fd; padding: 15px; border-radius: 5px; text-align: center; }}
        .metric h3 {{ margin: 0; color: #2c5aa0; }}
        .metric p {{ margin: 5px 0; font-size: 24px; font-weight: bold; }}
        .test-results {{ margin: 20px 0; }}
        .test-item {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .success {{ border-left: 5px solid #28a745; }}
        .failure {{ border-left: 5px solid #dc3545; }}
        .details {{ background-color: #f8f9fa; padding: 10px; margin-top: 10px; border-radius: 3px; }}
        pre {{ background-color: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SmartInvention API 測試報告</h1>
        <p>生成時間: {report['timestamp']}</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <h3>總測試數</h3>
            <p>{report['summary']['total_tests']}</p>
        </div>
        <div class="metric">
            <h3>成功測試</h3>
            <p style="color: #28a745;">{report['summary']['successful_tests']}</p>
        </div>
        <div class="metric">
            <h3>失敗測試</h3>
            <p style="color: #dc3545;">{report['summary']['failed_tests']}</p>
        </div>
        <div class="metric">
            <h3>成功率</h3>
            <p>{report['summary']['success_rate']:.1%}</p>
        </div>
        <div class="metric">
            <h3>總執行時間</h3>
            <p>{report['summary']['total_execution_time']:.2f}s</p>
        </div>
    </div>
    
    <div class="test-results">
        <h2>測試結果詳情</h2>
"""
        
        for result in report['test_results']:
            status_class = "success" if result['success'] else "failure"
            status_text = "✅ 成功" if result['success'] else "❌ 失敗"
            
            html_content += f"""
        <div class="test-item {status_class}">
            <h3>{result['test_name']} - {status_text}</h3>
            <p><strong>執行時間:</strong> {result['execution_time']:.2f}s</p>
            <p><strong>時間戳:</strong> {result['timestamp']}</p>
"""
            
            if result['error_message']:
                html_content += f"""
            <div class="details">
                <strong>錯誤信息:</strong>
                <pre>{result['error_message']}</pre>
            </div>
"""
            
            if result['response_data']:
                html_content += f"""
            <div class="details">
                <strong>響應數據:</strong>
                <pre>{json.dumps(result['response_data'], indent=2, ensure_ascii=False)}</pre>
            </div>
"""
            
            html_content += "        </div>\n"
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def generate_markdown_report(self, report: Dict, output_file: str):
        """生成 Markdown 格式報告"""
        md_content = f"""# SmartInvention API 測試報告

**生成時間:** {report['timestamp']}

## 📊 測試摘要

| 指標 | 數值 |
|------|------|
| 總測試數 | {report['summary']['total_tests']} |
| 成功測試 | {report['summary']['successful_tests']} |
| 失敗測試 | {report['summary']['failed_tests']} |
| 成功率 | {report['summary']['success_rate']:.1%} |
| 總執行時間 | {report['summary']['total_execution_time']:.2f}s |
| 平均執行時間 | {report['summary']['average_execution_time']:.2f}s |

## 📋 測試結果詳情

"""
        
        for result in report['test_results']:
            status_emoji = "✅" if result['success'] else "❌"
            md_content += f"""### {status_emoji} {result['test_name']}

- **狀態:** {'成功' if result['success'] else '失敗'}
- **執行時間:** {result['execution_time']:.2f}s
- **時間戳:** {result['timestamp']}

"""
            
            if result['error_message']:
                md_content += f"""**錯誤信息:**
```
{result['error_message']}
```

"""
            
            if result['response_data']:
                md_content += f"""**響應數據:**
```json
{json.dumps(result['response_data'], indent=2, ensure_ascii=False)}
```

"""
            
            md_content += "---\n\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def save_reports(self, report: Dict, test_type: str):
        """保存測試報告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"smartinvention_{test_type}_test_{timestamp}"
        
        # JSON 報告
        json_file = self.results_dir / f"{base_filename}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"📄 JSON 報告已保存: {json_file}")
        
        # HTML 報告
        html_file = self.results_dir / f"{base_filename}.html"
        self.generate_html_report(report, html_file)
        print(f"🌐 HTML 報告已保存: {html_file}")
        
        # Markdown 報告
        md_file = self.results_dir / f"{base_filename}.md"
        self.generate_markdown_report(report, md_file)
        print(f"📝 Markdown 報告已保存: {md_file}")

async def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="SmartInvention API 測試執行器")
    parser.add_argument("--smoke", action="store_true", help="運行冒煙測試")
    parser.add_argument("--regression", action="store_true", help="運行回歸測試")
    parser.add_argument("--performance", action="store_true", help="運行性能測試")
    parser.add_argument("--integration", action="store_true", help="運行集成測試")
    parser.add_argument("--full", action="store_true", help="運行完整測試套件")
    parser.add_argument("--check-env", action="store_true", help="檢查測試環境")
    parser.add_argument("--config", default="test_config.json", help="測試配置文件")
    
    args = parser.parse_args()
    
    # 創建測試執行器
    runner = SmartInventionTestRunner(args.config)
    
    # 檢查環境
    if args.check_env:
        env_ok = await runner.check_environment()
        if env_ok:
            print("✅ 環境檢查通過")
            sys.exit(0)
        else:
            print("❌ 環境檢查失敗")
            sys.exit(1)
    
    # 確定測試類型
    if args.smoke:
        test_type = "smoke"
        results = await runner.run_smoke_tests()
    elif args.regression:
        test_type = "regression"
        results = await runner.run_regression_tests()
    elif args.performance:
        test_type = "performance"
        results = await runner.run_performance_tests()
    elif args.integration:
        test_type = "integration"
        results = await runner.run_integration_tests()
    elif args.full:
        test_type = "full"
        results = await runner.run_full_tests()
    else:
        print("請指定測試類型: --smoke, --regression, --performance, --integration, 或 --full")
        sys.exit(1)
    
    # 生成報告
    report = runner.test_suite.generate_test_report()
    
    # 輸出摘要
    print(f"\n📊 {test_type.upper()} 測試摘要")
    print("=" * 50)
    print(f"總測試數: {report['summary']['total_tests']}")
    print(f"成功測試: {report['summary']['successful_tests']}")
    print(f"失敗測試: {report['summary']['failed_tests']}")
    print(f"成功率: {report['summary']['success_rate']:.1%}")
    print(f"總執行時間: {report['summary']['total_execution_time']:.2f}s")
    
    # 保存報告
    runner.save_reports(report, test_type)
    
    # 根據測試結果設置退出碼
    if report['summary']['failed_tests'] > 0:
        print(f"\n❌ 測試失敗: {report['summary']['failed_tests']} 個測試未通過")
        sys.exit(1)
    else:
        print(f"\n✅ 所有測試通過!")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())

