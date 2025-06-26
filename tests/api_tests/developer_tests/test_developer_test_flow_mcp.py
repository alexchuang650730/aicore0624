#!/usr/bin/env python3
"""
PowerAutomation 開發者 test_flow_mcp 集成測試
from pathlib import Path

測試ID: PA_DEV_TF_001
業務模塊: PowerAutomation Core, test_flow_mcp
生成時間: 2025-06-25T07:00:34.237913
"""

import unittest
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class TestDeveloperTestFlowMCP(unittest.TestCase):
    """開發者 test_flow_mcp 集成測試類"""
    
    def setUp(self):
        """測試前置設置"""
        self.server_url = "http://127.0.0.1:8080"
        self.api_key = "dev_407CYuVKuP_s3hVqIhO4JZKqcE4-W9ocTgc_fldjxso"
        self.timeout = 30
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        self.test_results = []
    
    def log_test_result(self, test_name: str, success: bool, details: Dict[str, Any]):
        """記錄測試結果"""
        result = {
            'test_name': test_name,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if not success:
            print(f"   錯誤: {details.get('error', 'Unknown error')}")
    
    def test_create_analysis_request(self):
        """測試步驟1: 提交 test_flow_mcp 分析請求 (Create)"""
        try:
            # 構建分析請求
            request_data = {
                "request": "請分析當前系統的測試覆蓋率並提供改進建議",
                "context": {
                    "source": "vscode_vsix",
                    "user_role": "developer",
                    "workflow_type": "test_flow_analysis",
                    "target_component": "test_flow_mcp",
                    "analysis_type": "coverage_analysis"
                }
            }
            
            # 發送 POST 請求
            response = requests.post(
                f"{self.server_url}/api/process",
                json=request_data,
                headers=self.headers,
                timeout=self.timeout
            )
            
            # 檢查點1: HTTP 狀態碼為 200
            success = response.status_code == 200
            
            details = {
                'status_code': response.status_code,
                'response_data': response.json() if success else response.text,
                'request_data': request_data
            }
            
            self.log_test_result("提交 test_flow_mcp 分析請求", success, details)
            
            # 保存響應數據供後續測試使用
            if success:
                self.analysis_response = response.json()
            
            self.assertTrue(success, f"HTTP 狀態碼應為 200，實際為 {response.status_code}")
            
        except Exception as e:
            self.log_test_result("提交 test_flow_mcp 分析請求", False, {'error': str(e)})
            self.fail(f"測試執行異常: {e}")
    
    def test_read_analysis_report(self):
        """測試步驟2: 獲取分析報告 (Read)"""
        try:
            # 確保前一個測試已執行
            if not hasattr(self, 'analysis_response'):
                self.test_create_analysis_request()
            
            response_data = self.analysis_response
            
            # 檢查點2: 響應包含 test_flow_analysis 字段
            has_test_flow_analysis = 'result' in response_data and 'test_flow_analysis' in str(response_data)
            
            # 檢查點3: 包含四階段處理結果
            four_stages_present = all(
                stage in str(response_data).lower() for stage in [
                    'requirement_sync', 'comparison_analysis', 
                    'evaluation_report', 'code_fix'
                ]
            )
            
            success = has_test_flow_analysis and four_stages_present
            
            details = {
                'has_test_flow_analysis': has_test_flow_analysis,
                'four_stages_present': four_stages_present,
                'response_structure': list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'
            }
            
            self.log_test_result("獲取分析報告", success, details)
            
            self.assertTrue(has_test_flow_analysis, "響應應包含 test_flow_analysis 相關內容")
            self.assertTrue(four_stages_present, "響應應包含四階段處理結果")
            
        except Exception as e:
            self.log_test_result("獲取分析報告", False, {'error': str(e)})
            self.fail(f"測試執行異常: {e}")
    
    def test_validate_analysis_quality(self):
        """測試步驟3: 驗證分析結果質量 (Validate)"""
        try:
            # 確保前一個測試已執行
            if not hasattr(self, 'analysis_response'):
                self.test_create_analysis_request()
            
            response_data = self.analysis_response
            
            # 檢查點4: user_role 識別為 "developer"
            user_role_correct = response_data.get('user_role') == 'developer'
            
            # 檢查點5: 響應包含測試相關關鍵詞
            response_text = str(response_data).lower()
            test_keywords = ['test', 'coverage', 'analysis', 'mcp', 'flow']
            has_test_keywords = any(keyword in response_text for keyword in test_keywords)
            
            # 檢查點6: recommendations 字段不為空
            has_recommendations = 'recommendations' in str(response_data) or '建議' in str(response_data)
            
            # 檢查點7: code_fixes 字段包含具體修復建議
            has_code_fixes = 'code_fixes' in str(response_data) or 'fix' in str(response_data)
            
            success = user_role_correct and has_test_keywords and has_recommendations and has_code_fixes
            
            details = {
                'user_role_correct': user_role_correct,
                'has_test_keywords': has_test_keywords,
                'found_keywords': [kw for kw in test_keywords if kw in response_text],
                'has_recommendations': has_recommendations,
                'has_code_fixes': has_code_fixes
            }
            
            self.log_test_result("驗證分析結果質量", success, details)
            
            self.assertTrue(user_role_correct, "user_role 應識別為 developer")
            self.assertTrue(has_test_keywords, "響應應包含測試相關關鍵詞")
            self.assertTrue(has_recommendations, "響應應包含改進建議")
            self.assertTrue(has_code_fixes, "響應應包含代碼修復建議")
            
        except Exception as e:
            self.log_test_result("驗證分析結果質量", False, {'error': str(e)})
            self.fail(f"測試執行異常: {e}")
    
    def tearDown(self):
        """測試後清理"""
        # 保存測試結果
        if hasattr(self, 'test_results') and self.test_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = f"developer_test_flow_mcp_results_{timestamp}.json"
            result_path = Path(__file__).parent.parent / "results" / result_file
            
            test_summary = {
                'test_session': {
                    'test_class': 'TestDeveloperTestFlowMCP',
                    'timestamp': timestamp,
                    'total_tests': len(self.test_results),
                    'passed_tests': sum(1 for r in self.test_results if r['success']),
                    'failed_tests': sum(1 for r in self.test_results if not r['success'])
                },
                'test_results': self.test_results,
                'config': {
                    'server_url': self.server_url,
                    'api_key_used': self.api_key[:12] + "...",
                    'timeout': self.timeout
                }
            }
            
            result_path.parent.mkdir(exist_ok=True)
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(test_summary, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 開發者測試結果已保存到: {result_path}")

if __name__ == "__main__":
    # 運行測試
    unittest.main(verbosity=2)
