#!/usr/bin/env python3
"""
PowerAutomation API 測試運行器
from pathlib import Path

運行所有生成的 API 測試並生成統一報告
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def run_test_file(test_file_path):
    """運行單個測試文件"""
    print(f"\n🔄 運行測試: {test_file_path.name}")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, str(test_file_path)
        ], capture_output=True, text=True, cwd=test_file_path.parent)
        
        success = result.returncode == 0
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return {
            'test_file': str(test_file_path),
            'success': success,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        print(f"❌ 測試執行失敗: {e}")
        return {
            'test_file': str(test_file_path),
            'success': False,
            'error': str(e)
        }

def main():
    """主函數"""
    print("🚀 PowerAutomation API 測試運行器")
    print("=" * 60)
    
    # 測試文件路徑
    base_dir = Path(__file__).parent
    test_files = [
        base_dir / "developer_tests" / "test_developer_test_flow_mcp.py",
        base_dir / "user_tests" / "test_user_smartinvention_hitl.py",
        base_dir / "admin_tests" / "test_admin_system_monitoring.py"
    ]
    
    # 運行所有測試
    all_results = []
    for test_file in test_files:
        if test_file.exists():
            result = run_test_file(test_file)
            all_results.append(result)
        else:
            print(f"⚠️  測試文件不存在: {test_file}")
    
    # 生成統一報告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = base_dir / "results" / f"api_test_summary_{timestamp}.json"
    
    summary = {
        'test_session': {
            'timestamp': timestamp,
            'total_test_files': len(all_results),
            'successful_files': sum(1 for r in all_results if r['success']),
            'failed_files': sum(1 for r in all_results if not r['success'])
        },
        'test_results': all_results
    }
    
    report_file.parent.mkdir(exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # 打印總結
    print("\n" + "=" * 60)
    print("📊 測試總結:")
    print(f"   總測試文件數: {summary['test_session']['total_test_files']}")
    print(f"   成功文件數: {summary['test_session']['successful_files']}")
    print(f"   失敗文件數: {summary['test_session']['failed_files']}")
    print(f"\n📄 詳細報告已保存到: {report_file}")
    
    # 返回適當的退出碼
    if summary['test_session']['failed_files'] > 0:
        sys.exit(1)
    else:
        print("\n🎉 所有測試都成功完成！")
        sys.exit(0)

if __name__ == "__main__":
    main()
