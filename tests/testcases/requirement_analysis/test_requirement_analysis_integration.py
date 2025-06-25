#!/usr/bin/env python3.11
"""
需求分析集成測試
測試 test_flow_mcp 的「需求分析」工作流
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List

# 測試配置
SERVER_URL = "http://127.0.0.1:8080"
DEVELOPER_API_KEY = "dev_407CYuVKuP_s3hVqIhO4JZKqcE4-W9ocTgc_fldjxso"

class RequirementAnalysisIntegrationTest:
    """需求分析集成測試類"""
    
    def __init__(self):
        self.test_results = []
        self.test_start_time = datetime.now()
        
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
    
    def test_server_connectivity(self) -> bool:
        """測試服務器連接性"""
        try:
            response = requests.get(f"{SERVER_URL}/api/status", timeout=10)
            success = response.status_code == 200
            
            details = {
                'status_code': response.status_code,
                'response': response.json() if success else response.text
            }
            
            self.log_test_result("服務器連接性測試", success, details)
            return success
            
        except Exception as e:
            self.log_test_result("服務器連接性測試", False, {'error': str(e)})
            return False
    
    def test_api_key_authentication(self) -> bool:
        """測試 API Key 認證"""
        try:
            # 測試無 API Key 的請求
            response = requests.post(f"{SERVER_URL}/api/process", 
                                   json={"request": "測試", "context": {}}, 
                                   timeout=10)
            
            no_key_success = response.status_code == 401
            
            # 測試有效 API Key 的請求
            headers = {"X-API-Key": DEVELOPER_API_KEY}
            response = requests.post(f"{SERVER_URL}/api/process",
                                   json={"request": "測試認證", "context": {}},
                                   headers=headers,
                                   timeout=10)
            
            with_key_success = response.status_code == 200
            
            success = no_key_success and with_key_success
            
            details = {
                'no_key_status': response.status_code if not no_key_success else 401,
                'with_key_status': response.status_code,
                'with_key_response': response.json() if with_key_success else response.text
            }
            
            self.log_test_result("API Key 認證測試", success, details)
            return success
            
        except Exception as e:
            self.log_test_result("API Key 認證測試", False, {'error': str(e)})
            return False
    
    def test_requirement_analysis_workflow(self) -> bool:
        """測試需求分析工作流"""
        try:
            headers = {"X-API-Key": DEVELOPER_API_KEY, "Content-Type": "application/json"}
            
            # 構建需求分析測試請求
            test_request = {
                "request": "我想要多了解本系統的架構和功能",
                "context": {
                    "source": "vscode_vsix",
                    "user_role": "developer",
                    "workflow_type": "requirement_analysis",
                    "test_scenario": "system_architecture_inquiry"
                }
            }
            
            print(f"🔄 發送需求分析請求...")
            response = requests.post(f"{SERVER_URL}/api/process",
                                   json=test_request,
                                   headers=headers,
                                   timeout=30)
            
            success = response.status_code == 200
            
            if success:
                response_data = response.json()
                
                # 檢查響應結構
                required_fields = ['success', 'user_role', 'message']
                has_required_fields = all(field in response_data for field in required_fields)
                
                # 檢查是否識別為開發者角色
                is_developer_role = response_data.get('user_role') == 'developer'
                
                # 檢查是否有處理結果
                has_processing_result = 'message' in response_data and len(response_data['message']) > 0
                
                success = success and has_required_fields and is_developer_role and has_processing_result
                
                details = {
                    'status_code': response.status_code,
                    'response_data': response_data,
                    'has_required_fields': has_required_fields,
                    'is_developer_role': is_developer_role,
                    'has_processing_result': has_processing_result,
                    'response_length': len(str(response_data))
                }
            else:
                details = {
                    'status_code': response.status_code,
                    'error_response': response.text
                }
            
            self.log_test_result("需求分析工作流測試", success, details)
            return success
            
        except Exception as e:
            self.log_test_result("需求分析工作流測試", False, {'error': str(e)})
            return False
    
    def test_test_flow_mcp_integration(self) -> bool:
        """測試 test_flow_mcp 集成"""
        try:
            headers = {"X-API-Key": DEVELOPER_API_KEY, "Content-Type": "application/json"}
            
            # 構建 test_flow_mcp 測試請求
            test_request = {
                "request": "請分析當前系統的測試覆蓋率並提供改進建議",
                "context": {
                    "source": "vscode_vsix",
                    "user_role": "developer",
                    "workflow_type": "test_flow_analysis",
                    "target_component": "test_flow_mcp",
                    "analysis_type": "coverage_analysis"
                }
            }
            
            print(f"🔄 發送 test_flow_mcp 集成測試請求...")
            response = requests.post(f"{SERVER_URL}/api/process",
                                   json=test_request,
                                   headers=headers,
                                   timeout=45)
            
            success = response.status_code == 200
            
            if success:
                response_data = response.json()
                
                # 檢查是否觸發了開發者模式
                is_developer_mode = response_data.get('user_role') == 'developer'
                
                # 檢查響應是否包含測試相關內容
                response_text = str(response_data).lower()
                has_test_content = any(keyword in response_text for keyword in 
                                     ['test', 'coverage', 'analysis', 'mcp', 'flow'])
                
                success = success and is_developer_mode and has_test_content
                
                details = {
                    'status_code': response.status_code,
                    'response_data': response_data,
                    'is_developer_mode': is_developer_mode,
                    'has_test_content': has_test_content,
                    'response_keywords': [kw for kw in ['test', 'coverage', 'analysis', 'mcp', 'flow'] 
                                        if kw in response_text]
                }
            else:
                details = {
                    'status_code': response.status_code,
                    'error_response': response.text
                }
            
            self.log_test_result("test_flow_mcp 集成測試", success, details)
            return success
            
        except Exception as e:
            self.log_test_result("test_flow_mcp 集成測試", False, {'error': str(e)})
            return False
    
    def test_developer_vs_user_role_differentiation(self) -> bool:
        """測試開發者與使用者角色區分"""
        try:
            # 測試開發者角色
            dev_headers = {"X-API-Key": DEVELOPER_API_KEY, "Content-Type": "application/json"}
            dev_request = {
                "request": "開發者測試請求",
                "context": {"source": "vscode_vsix"}
            }
            
            dev_response = requests.post(f"{SERVER_URL}/api/process",
                                       json=dev_request,
                                       headers=dev_headers,
                                       timeout=20)
            
            dev_success = dev_response.status_code == 200
            dev_data = dev_response.json() if dev_success else {}
            
            # 檢查開發者角色識別
            is_dev_role = dev_data.get('user_role') == 'developer'
            
            success = dev_success and is_dev_role
            
            details = {
                'developer_test': {
                    'status_code': dev_response.status_code,
                    'identified_role': dev_data.get('user_role'),
                    'is_correct_role': is_dev_role
                }
            }
            
            self.log_test_result("開發者與使用者角色區分測試", success, details)
            return success
            
        except Exception as e:
            self.log_test_result("開發者與使用者角色區分測試", False, {'error': str(e)})
            return False
    
    def save_test_results(self):
        """保存測試結果到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"requirement_analysis_test_results_{timestamp}.json"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        test_summary = {
            'test_session': {
                'start_time': self.test_start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'total_tests': len(self.test_results),
                'passed_tests': sum(1 for r in self.test_results if r['success']),
                'failed_tests': sum(1 for r in self.test_results if not r['success'])
            },
            'test_results': self.test_results,
            'server_config': {
                'server_url': SERVER_URL,
                'api_key_used': DEVELOPER_API_KEY[:12] + "..."
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(test_summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 測試結果已保存到: {filepath}")
        return filepath
    
    def run_all_tests(self):
        """運行所有測試"""
        print("🚀 開始需求分析集成測試...")
        print(f"📡 服務器地址: {SERVER_URL}")
        print(f"🔑 使用開發者 API Key: {DEVELOPER_API_KEY[:12]}...")
        print("=" * 60)
        
        # 運行測試序列
        tests = [
            self.test_server_connectivity,
            self.test_api_key_authentication,
            self.test_requirement_analysis_workflow,
            self.test_test_flow_mcp_integration,
            self.test_developer_vs_user_role_differentiation
        ]
        
        for test_func in tests:
            try:
                test_func()
                time.sleep(1)  # 測試間隔
            except Exception as e:
                print(f"❌ 測試執行異常: {e}")
        
        # 生成測試報告
        print("\n" + "=" * 60)
        print("📊 測試結果總結:")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"   總測試數: {total_tests}")
        print(f"   通過測試: {passed_tests}")
        print(f"   失敗測試: {failed_tests}")
        print(f"   成功率: {(passed_tests/total_tests*100):.1f}%")
        
        # 保存結果
        result_file = self.save_test_results()
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = RequirementAnalysisIntegrationTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 所有測試通過！")
        exit(0)
    else:
        print("\n⚠️  部分測試失敗，請檢查測試結果。")
        exit(1)

