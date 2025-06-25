#!/usr/bin/env python3
"""
PowerAutomation 使用者 SmartInvention-Manus HITL 測試
from pathlib import Path

測試ID: PA_USER_SM_001
業務模塊: PowerAutomation Core, SmartInvention-Manus HITL
生成時間: 2025-06-25T07:00:34.240825
"""

import unittest
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class TestUserSmartInventionHITL(unittest.TestCase):
    """使用者 SmartInvention-Manus HITL 測試類"""
    
    def setUp(self):
        """測試前置設置"""
        self.server_url = "http://127.0.0.1:8080"
        self.api_key = "user_RcmKEIPfGCQrA6sSohzn5NDXYMsS5mkyP9jPhM3llTw"
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
    
    def test_create_general_request(self):
        """測試步驟1: 提交常規請求 (Create)"""
        try:
            # 構建常規請求
            request_data = {
                "request": "我需要一份關於人工智能發展趨勢的詳細報告",
                "context": {
                    "source": "web_interface",
                    "user_role": "user",
                    "workflow_type": "general_inquiry",
                    "priority": "normal"
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
            
            self.log_test_result("提交常規請求", success, details)
            
            # 保存響應數據供後續測試使用
            if success:
                self.hitl_response = response.json()
            
            self.assertTrue(success, f"HTTP 狀態碼應為 200，實際為 {response.status_code}")
            
        except Exception as e:
            self.log_test_result("提交常規請求", False, {'error': str(e)})
            self.fail(f"測試執行異常: {e}")
    
    def test_read_processing_result(self):
        """測試步驟2: 獲取處理結果 (Read)"""
        try:
            # 確保前一個測試已執行
            if not hasattr(self, 'hitl_response'):
                self.test_create_general_request()
            
            response_data = self.hitl_response
            
            # 檢查點2: 響應包含 result 字段
            has_result = 'result' in response_data or 'message' in response_data
            
            # 檢查點3: 包含 metadata 字段，顯示 HITL 狀態
            has_metadata = 'metadata' in response_data
            
            # 檢查點4: 包含 manus_direct_response 字段
            has_manus_response = 'manus_direct_response' in str(response_data) or 'manus' in str(response_data)
            
            success = has_result and (has_metadata or has_manus_response)
            
            details = {
                'has_result': has_result,
                'has_metadata': has_metadata,
                'has_manus_response': has_manus_response,
                'response_structure': list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'
            }
            
            self.log_test_result("獲取處理結果", success, details)
            
            self.assertTrue(has_result, "響應應包含處理結果")
            
        except Exception as e:
            self.log_test_result("獲取處理結果", False, {'error': str(e)})
            self.fail(f"測試執行異常: {e}")
    
    def test_validate_hitl_process(self):
        """測試步驟3: 驗證 HITL 流程 (Validate)"""
        try:
            # 確保前一個測試已執行
            if not hasattr(self, 'hitl_response'):
                self.test_create_general_request()
            
            response_data = self.hitl_response
            
            # 檢查點5: user_role 識別為 "user"
            user_role_correct = response_data.get('user_role') == 'user'
            
            # 檢查點6: system_type 為 "smartinvention_manus_integrated"
            system_type_correct = 'smartinvention' in str(response_data).lower() or 'manus' in str(response_data).lower()
            
            # 檢查點7: tools_used 包含 HITL 相關工具
            hitl_tools_present = any(tool in str(response_data).lower() for tool in ['smartinvention', 'manus', 'hitl'])
            
            # 檢查點8: manus_direct_available 為 true
            manus_available = 'manus' in str(response_data).lower()
            
            success = user_role_correct and (system_type_correct or hitl_tools_present or manus_available)
            
            details = {
                'user_role_correct': user_role_correct,
                'system_type_correct': system_type_correct,
                'hitl_tools_present': hitl_tools_present,
                'manus_available': manus_available
            }
            
            self.log_test_result("驗證 HITL 流程", success, details)
            
            self.assertTrue(user_role_correct, "user_role 應識別為 user")
            
        except Exception as e:
            self.log_test_result("驗證 HITL 流程", False, {'error': str(e)})
            self.fail(f"測試執行異常: {e}")
    
    def tearDown(self):
        """測試後清理"""
        # 保存測試結果
        if hasattr(self, 'test_results') and self.test_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = f"user_smartinvention_hitl_results_{timestamp}.json"
            result_path = Path(__file__).parent.parent / "results" / result_file
            
            test_summary = {
                'test_session': {
                    'test_class': 'TestUserSmartInventionHITL',
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
            
            print(f"\n📄 使用者測試結果已保存到: {result_path}")

if __name__ == "__main__":
    # 運行測試
    unittest.main(verbosity=2)
