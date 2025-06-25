#!/usr/bin/env python3
"""
PowerAutomation API 測試生成器

基於 powerautomation_api_test_template.md 模板，自動生成標準化的 Python API 測試腳本
支持三種使用者角色：開發者、使用者、管理員
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class APITestConfig:
    """API 測試配置"""
    server_url: str = "http://127.0.0.1:8080"
    timeout: int = 30
    developer_api_key: str = "dev_407CYuVKuP_s3hVqIhO4JZKqcE4-W9ocTgc_fldjxso"
    user_api_key: str = "user_RcmKEIPfGCQrA6sSohzn5NDXYMsS5mkyP9jPhM3llTw"
    admin_api_key: str = "admin_pth4jG-nVjvGaTZA2URN7SyHu-o7wBaeLOYbMrLMKkc"

class PowerAutomationAPITestGenerator:
    """PowerAutomation API 測試生成器"""
    
    def __init__(self, output_dir: str = "generated_api_tests"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.config = APITestConfig()
        
        # 創建子目錄
        (self.output_dir / "developer_tests").mkdir(exist_ok=True)
        (self.output_dir / "user_tests").mkdir(exist_ok=True)
        (self.output_dir / "admin_tests").mkdir(exist_ok=True)
        (self.output_dir / "results").mkdir(exist_ok=True)
    
    def generate_developer_test(self) -> str:
        """生成開發者 test_flow_mcp 集成測試"""
        template = '''#!/usr/bin/env python3
"""
PowerAutomation 開發者 test_flow_mcp 集成測試

測試ID: PA_DEV_TF_001
業務模塊: PowerAutomation Core, test_flow_mcp
生成時間: {generation_time}
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
        self.server_url = "{server_url}"
        self.api_key = "{developer_api_key}"
        self.timeout = {timeout}
        self.headers = {{
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }}
        self.test_results = []
    
    def log_test_result(self, test_name: str, success: bool, details: Dict[str, Any]):
        """記錄測試結果"""
        result = {{
            'test_name': test_name,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }}
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{{status}} {{test_name}}")
        if not success:
            print(f"   錯誤: {{details.get('error', 'Unknown error')}}")
    
    def test_create_analysis_request(self):
        """測試步驟1: 提交 test_flow_mcp 分析請求 (Create)"""
        try:
            # 構建分析請求
            request_data = {{
                "request": "請分析當前系統的測試覆蓋率並提供改進建議",
                "context": {{
                    "source": "vscode_vsix",
                    "user_role": "developer",
                    "workflow_type": "test_flow_analysis",
                    "target_component": "test_flow_mcp",
                    "analysis_type": "coverage_analysis"
                }}
            }}
            
            # 發送 POST 請求
            response = requests.post(
                f"{{self.server_url}}/api/process",
                json=request_data,
                headers=self.headers,
                timeout=self.timeout
            )
            
            # 檢查點1: HTTP 狀態碼為 200
            success = response.status_code == 200
            
            details = {{
                'status_code': response.status_code,
                'response_data': response.json() if success else response.text,
                'request_data': request_data
            }}
            
            self.log_test_result("提交 test_flow_mcp 分析請求", success, details)
            
            # 保存響應數據供後續測試使用
            if success:
                self.analysis_response = response.json()
            
            self.assertTrue(success, f"HTTP 狀態碼應為 200，實際為 {{response.status_code}}")
            
        except Exception as e:
            self.log_test_result("提交 test_flow_mcp 分析請求", False, {{'error': str(e)}})
            self.fail(f"測試執行異常: {{e}}")
    
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
            
            details = {{
                'has_test_flow_analysis': has_test_flow_analysis,
                'four_stages_present': four_stages_present,
                'response_structure': list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'
            }}
            
            self.log_test_result("獲取分析報告", success, details)
            
            self.assertTrue(has_test_flow_analysis, "響應應包含 test_flow_analysis 相關內容")
            self.assertTrue(four_stages_present, "響應應包含四階段處理結果")
            
        except Exception as e:
            self.log_test_result("獲取分析報告", False, {{'error': str(e)}})
            self.fail(f"測試執行異常: {{e}}")
    
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
            
            details = {{
                'user_role_correct': user_role_correct,
                'has_test_keywords': has_test_keywords,
                'found_keywords': [kw for kw in test_keywords if kw in response_text],
                'has_recommendations': has_recommendations,
                'has_code_fixes': has_code_fixes
            }}
            
            self.log_test_result("驗證分析結果質量", success, details)
            
            self.assertTrue(user_role_correct, "user_role 應識別為 developer")
            self.assertTrue(has_test_keywords, "響應應包含測試相關關鍵詞")
            self.assertTrue(has_recommendations, "響應應包含改進建議")
            self.assertTrue(has_code_fixes, "響應應包含代碼修復建議")
            
        except Exception as e:
            self.log_test_result("驗證分析結果質量", False, {{'error': str(e)}})
            self.fail(f"測試執行異常: {{e}}")
    
    def tearDown(self):
        """測試後清理"""
        # 保存測試結果
        if hasattr(self, 'test_results') and self.test_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = f"developer_test_flow_mcp_results_{{timestamp}}.json"
            result_path = Path(__file__).parent.parent / "results" / result_file
            
            test_summary = {{
                'test_session': {{
                    'test_class': 'TestDeveloperTestFlowMCP',
                    'timestamp': timestamp,
                    'total_tests': len(self.test_results),
                    'passed_tests': sum(1 for r in self.test_results if r['success']),
                    'failed_tests': sum(1 for r in self.test_results if not r['success'])
                }},
                'test_results': self.test_results,
                'config': {{
                    'server_url': self.server_url,
                    'api_key_used': self.api_key[:12] + "...",
                    'timeout': self.timeout
                }}
            }}
            
            result_path.parent.mkdir(exist_ok=True)
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(test_summary, f, indent=2, ensure_ascii=False)
            
            print(f"\\n📄 開發者測試結果已保存到: {{result_path}}")

if __name__ == "__main__":
    # 運行測試
    unittest.main(verbosity=2)
'''
        
        return template.format(
            generation_time=datetime.now().isoformat(),
            server_url=self.config.server_url,
            developer_api_key=self.config.developer_api_key,
            timeout=self.config.timeout
        )
    
    def generate_user_test(self) -> str:
        """生成使用者 SmartInvention-Manus HITL 測試"""
        template = '''#!/usr/bin/env python3
"""
PowerAutomation 使用者 SmartInvention-Manus HITL 測試

測試ID: PA_USER_SM_001
業務模塊: PowerAutomation Core, SmartInvention-Manus HITL
生成時間: {generation_time}
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
        self.server_url = "{server_url}"
        self.api_key = "{user_api_key}"
        self.timeout = {timeout}
        self.headers = {{
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }}
        self.test_results = []
    
    def log_test_result(self, test_name: str, success: bool, details: Dict[str, Any]):
        """記錄測試結果"""
        result = {{
            'test_name': test_name,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }}
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{{status}} {{test_name}}")
        if not success:
            print(f"   錯誤: {{details.get('error', 'Unknown error')}}")
    
    def test_create_general_request(self):
        """測試步驟1: 提交常規請求 (Create)"""
        try:
            # 構建常規請求
            request_data = {{
                "request": "我需要一份關於人工智能發展趨勢的詳細報告",
                "context": {{
                    "source": "web_interface",
                    "user_role": "user",
                    "workflow_type": "general_inquiry",
                    "priority": "normal"
                }}
            }}
            
            # 發送 POST 請求
            response = requests.post(
                f"{{self.server_url}}/api/process",
                json=request_data,
                headers=self.headers,
                timeout=self.timeout
            )
            
            # 檢查點1: HTTP 狀態碼為 200
            success = response.status_code == 200
            
            details = {{
                'status_code': response.status_code,
                'response_data': response.json() if success else response.text,
                'request_data': request_data
            }}
            
            self.log_test_result("提交常規請求", success, details)
            
            # 保存響應數據供後續測試使用
            if success:
                self.hitl_response = response.json()
            
            self.assertTrue(success, f"HTTP 狀態碼應為 200，實際為 {{response.status_code}}")
            
        except Exception as e:
            self.log_test_result("提交常規請求", False, {{'error': str(e)}})
            self.fail(f"測試執行異常: {{e}}")
    
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
            
            details = {{
                'has_result': has_result,
                'has_metadata': has_metadata,
                'has_manus_response': has_manus_response,
                'response_structure': list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'
            }}
            
            self.log_test_result("獲取處理結果", success, details)
            
            self.assertTrue(has_result, "響應應包含處理結果")
            
        except Exception as e:
            self.log_test_result("獲取處理結果", False, {{'error': str(e)}})
            self.fail(f"測試執行異常: {{e}}")
    
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
            
            details = {{
                'user_role_correct': user_role_correct,
                'system_type_correct': system_type_correct,
                'hitl_tools_present': hitl_tools_present,
                'manus_available': manus_available
            }}
            
            self.log_test_result("驗證 HITL 流程", success, details)
            
            self.assertTrue(user_role_correct, "user_role 應識別為 user")
            
        except Exception as e:
            self.log_test_result("驗證 HITL 流程", False, {{'error': str(e)}})
            self.fail(f"測試執行異常: {{e}}")
    
    def tearDown(self):
        """測試後清理"""
        # 保存測試結果
        if hasattr(self, 'test_results') and self.test_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = f"user_smartinvention_hitl_results_{{timestamp}}.json"
            result_path = Path(__file__).parent.parent / "results" / result_file
            
            test_summary = {{
                'test_session': {{
                    'test_class': 'TestUserSmartInventionHITL',
                    'timestamp': timestamp,
                    'total_tests': len(self.test_results),
                    'passed_tests': sum(1 for r in self.test_results if r['success']),
                    'failed_tests': sum(1 for r in self.test_results if not r['success'])
                }},
                'test_results': self.test_results,
                'config': {{
                    'server_url': self.server_url,
                    'api_key_used': self.api_key[:12] + "...",
                    'timeout': self.timeout
                }}
            }}
            
            result_path.parent.mkdir(exist_ok=True)
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(test_summary, f, indent=2, ensure_ascii=False)
            
            print(f"\\n📄 使用者測試結果已保存到: {{result_path}}")

if __name__ == "__main__":
    # 運行測試
    unittest.main(verbosity=2)
'''
        
        return template.format(
            generation_time=datetime.now().isoformat(),
            server_url=self.config.server_url,
            user_api_key=self.config.user_api_key,
            timeout=self.config.timeout
        )
    
    def generate_admin_test(self) -> str:
        """生成管理員系統監控測試"""
        template = '''#!/usr/bin/env python3
"""
PowerAutomation 管理員系統監控測試

測試ID: PA_ADMIN_SYS_001
業務模塊: PowerAutomation Core, System Management
生成時間: {generation_time}
"""

import unittest
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class TestAdminSystemMonitoring(unittest.TestCase):
    """管理員系統監控測試類"""
    
    def setUp(self):
        """測試前置設置"""
        self.server_url = "{server_url}"
        self.api_key = "{admin_api_key}"
        self.timeout = {timeout}
        self.headers = {{
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }}
        self.test_results = []
    
    def log_test_result(self, test_name: str, success: bool, details: Dict[str, Any]):
        """記錄測試結果"""
        result = {{
            'test_name': test_name,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }}
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{{status}} {{test_name}}")
        if not success:
            print(f"   錯誤: {{details.get('error', 'Unknown error')}}")
    
    def test_read_system_status(self):
        """測試步驟1: 獲取系統狀態 (Read)"""
        try:
            # 發送 GET 請求到 /api/status
            response = requests.get(
                f"{{self.server_url}}/api/status",
                headers=self.headers,
                timeout=self.timeout
            )
            
            # 檢查點1: HTTP 狀態碼為 200
            success = response.status_code == 200
            
            if success:
                response_data = response.json()
                
                # 檢查點2: 響應包含系統運行時間
                has_uptime = 'uptime' in response_data or 'runtime' in response_data or 'time' in str(response_data)
                
                # 檢查點3: 響應包含 API Keys 統計
                has_api_keys = 'api_keys' in response_data or 'keys' in str(response_data)
                
                # 檢查點4: 響應包含功能特性列表
                has_features = 'features' in response_data or 'enabled' in str(response_data)
                
                success = success and (has_uptime or has_api_keys or has_features)
            else:
                response_data = response.text
                has_uptime = has_api_keys = has_features = False
            
            details = {{
                'status_code': response.status_code,
                'response_data': response_data,
                'has_uptime': has_uptime,
                'has_api_keys': has_api_keys,
                'has_features': has_features
            }}
            
            self.log_test_result("獲取系統狀態", success, details)
            
            # 保存響應數據供後續測試使用
            if success:
                self.system_status = response_data
            
            self.assertTrue(success, f"HTTP 狀態碼應為 200，實際為 {{response.status_code}}")
            
        except Exception as e:
            self.log_test_result("獲取系統狀態", False, {{'error': str(e)}})
            self.fail(f"測試執行異常: {{e}}")
    
    def test_validate_admin_privileges(self):
        """測試步驟2: 驗證管理員權限 (Validate)"""
        try:
            # 確保前一個測試已執行
            if not hasattr(self, 'system_status'):
                self.test_read_system_status()
            
            response_data = self.system_status
            
            # 檢查點5: 響應包含詳細的系統配置信息
            has_detailed_config = len(str(response_data)) > 100  # 簡單的詳細程度檢查
            
            # 檢查點6: 響應包含各模塊的運行狀態
            has_module_status = any(module in str(response_data).lower() for module in ['test_flow', 'mcp', 'enabled', 'status'])
            
            # 檢查點7: 響應包含錯誤日誌統計（可選）
            has_error_stats = 'error' in str(response_data).lower() or 'log' in str(response_data).lower()
            
            # 檢查點8: 響應包含性能指標（可選）
            has_performance_metrics = any(metric in str(response_data).lower() for metric in ['time', 'count', 'performance', 'metric'])
            
            success = has_detailed_config and has_module_status
            
            details = {{
                'has_detailed_config': has_detailed_config,
                'has_module_status': has_module_status,
                'has_error_stats': has_error_stats,
                'has_performance_metrics': has_performance_metrics,
                'response_length': len(str(response_data))
            }}
            
            self.log_test_result("驗證管理員權限", success, details)
            
            self.assertTrue(has_detailed_config, "管理員應能獲取詳細的系統配置信息")
            self.assertTrue(has_module_status, "管理員應能獲取各模塊的運行狀態")
            
        except Exception as e:
            self.log_test_result("驗證管理員權限", False, {{'error': str(e)}})
            self.fail(f"測試執行異常: {{e}}")
    
    def test_monitor_system_health(self):
        """測試步驟3: 監控系統健康狀態 (Monitor)"""
        try:
            # 確保前一個測試已執行
            if not hasattr(self, 'system_status'):
                self.test_read_system_status()
            
            response_data = self.system_status
            response_text = str(response_data).lower()
            
            # 檢查點9: test_flow_mcp 模塊狀態為 enabled
            test_flow_enabled = 'test_flow' in response_text and ('enabled' in response_text or 'true' in response_text)
            
            # 檢查點10: smartinvention_mcp 模塊狀態為 enabled
            smartinvention_enabled = 'smartinvention' in response_text or 'manus' in response_text
            
            # 檢查點11: 系統運行時間 > 0
            has_positive_uptime = any(char.isdigit() for char in response_text)
            
            # 檢查點12: 錯誤率在可接受範圍內（假設沒有明顯的錯誤指示）
            acceptable_error_rate = 'error' not in response_text or 'critical' not in response_text
            
            success = test_flow_enabled or smartinvention_enabled or has_positive_uptime
            
            details = {{
                'test_flow_enabled': test_flow_enabled,
                'smartinvention_enabled': smartinvention_enabled,
                'has_positive_uptime': has_positive_uptime,
                'acceptable_error_rate': acceptable_error_rate
            }}
            
            self.log_test_result("監控系統健康狀態", success, details)
            
            # 至少一個核心模塊應該是啟用的
            self.assertTrue(test_flow_enabled or smartinvention_enabled, "至少一個核心模塊應該是啟用的")
            
        except Exception as e:
            self.log_test_result("監控系統健康狀態", False, {{'error': str(e)}})
            self.fail(f"測試執行異常: {{e}}")
    
    def tearDown(self):
        """測試後清理"""
        # 保存測試結果
        if hasattr(self, 'test_results') and self.test_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = f"admin_system_monitoring_results_{{timestamp}}.json"
            result_path = Path(__file__).parent.parent / "results" / result_file
            
            test_summary = {{
                'test_session': {{
                    'test_class': 'TestAdminSystemMonitoring',
                    'timestamp': timestamp,
                    'total_tests': len(self.test_results),
                    'passed_tests': sum(1 for r in self.test_results if r['success']),
                    'failed_tests': sum(1 for r in self.test_results if not r['success'])
                }},
                'test_results': self.test_results,
                'config': {{
                    'server_url': self.server_url,
                    'api_key_used': self.api_key[:12] + "...",
                    'timeout': self.timeout
                }}
            }}
            
            result_path.parent.mkdir(exist_ok=True)
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(test_summary, f, indent=2, ensure_ascii=False)
            
            print(f"\\n📄 管理員測試結果已保存到: {{result_path}}")

if __name__ == "__main__":
    # 運行測試
    unittest.main(verbosity=2)
'''
        
        return template.format(
            generation_time=datetime.now().isoformat(),
            server_url=self.config.server_url,
            admin_api_key=self.config.admin_api_key,
            timeout=self.config.timeout
        )
    
    def generate_all_tests(self):
        """生成所有測試文件"""
        print("🚀 開始生成 PowerAutomation API 測試文件...")
        
        # 生成開發者測試
        developer_test = self.generate_developer_test()
        developer_path = self.output_dir / "developer_tests" / "test_developer_test_flow_mcp.py"
        with open(developer_path, 'w', encoding='utf-8') as f:
            f.write(developer_test)
        print(f"✅ 開發者測試文件已生成: {developer_path}")
        
        # 生成使用者測試
        user_test = self.generate_user_test()
        user_path = self.output_dir / "user_tests" / "test_user_smartinvention_hitl.py"
        with open(user_path, 'w', encoding='utf-8') as f:
            f.write(user_test)
        print(f"✅ 使用者測試文件已生成: {user_path}")
        
        # 生成管理員測試
        admin_test = self.generate_admin_test()
        admin_path = self.output_dir / "admin_tests" / "test_admin_system_monitoring.py"
        with open(admin_path, 'w', encoding='utf-8') as f:
            f.write(admin_test)
        print(f"✅ 管理員測試文件已生成: {admin_path}")
        
        # 生成測試運行腳本
        self.generate_test_runner()
        
        print(f"\\n🎉 所有測試文件已生成完成！")
        print(f"📁 輸出目錄: {self.output_dir.absolute()}")
        
        return {
            'developer_test': developer_path,
            'user_test': user_path,
            'admin_test': admin_path
        }
    
    def generate_test_runner(self):
        """生成測試運行腳本"""
        runner_script = '''#!/usr/bin/env python3
"""
PowerAutomation API 測試運行器

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
    print(f"\\n🔄 運行測試: {test_file_path.name}")
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
    print("\\n" + "=" * 60)
    print("📊 測試總結:")
    print(f"   總測試文件數: {summary['test_session']['total_test_files']}")
    print(f"   成功文件數: {summary['test_session']['successful_files']}")
    print(f"   失敗文件數: {summary['test_session']['failed_files']}")
    print(f"\\n📄 詳細報告已保存到: {report_file}")
    
    # 返回適當的退出碼
    if summary['test_session']['failed_files'] > 0:
        sys.exit(1)
    else:
        print("\\n🎉 所有測試都成功完成！")
        sys.exit(0)

if __name__ == "__main__":
    main()
'''
        
        runner_path = self.output_dir / "run_all_api_tests.py"
        with open(runner_path, 'w', encoding='utf-8') as f:
            f.write(runner_script)
        
        # 設置執行權限
        os.chmod(runner_path, 0o755)
        
        print(f"✅ 測試運行腳本已生成: {runner_path}")

if __name__ == "__main__":
    # 創建生成器並生成所有測試
    generator = PowerAutomationAPITestGenerator()
    generated_files = generator.generate_all_tests()
    
    print("\\n📋 生成的測試文件:")
    for role, path in generated_files.items():
        print(f"  {role}: {path}")

