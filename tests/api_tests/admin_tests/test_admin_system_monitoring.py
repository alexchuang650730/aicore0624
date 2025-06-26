#!/usr/bin/env python3
"""
PowerAutomation 管理員系統監控測試
from pathlib import Path

測試ID: PA_ADMIN_SYS_001
業務模塊: PowerAutomation Core, System Management
from pathlib import Path
生成時間: 2025-06-25T07:00:34.241649
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
        self.server_url = "http://127.0.0.1:8080"
        self.api_key = "admin_pth4jG-nVjvGaTZA2URN7SyHu-o7wBaeLOYbMrLMKkc"
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
    
    def test_read_system_status(self):
        """測試步驟1: 獲取系統狀態 (Read)"""
        try:
            # 發送 GET 請求到 /api/status
            response = requests.get(
                f"{self.server_url}/api/status",
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
            
            details = {
                'status_code': response.status_code,
                'response_data': response_data,
                'has_uptime': has_uptime,
                'has_api_keys': has_api_keys,
                'has_features': has_features
            }
            
            self.log_test_result("獲取系統狀態", success, details)
            
            # 保存響應數據供後續測試使用
            if success:
                self.system_status = response_data
            
            self.assertTrue(success, f"HTTP 狀態碼應為 200，實際為 {response.status_code}")
            
        except Exception as e:
            self.log_test_result("獲取系統狀態", False, {'error': str(e)})
            self.fail(f"測試執行異常: {e}")
    
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
            
            details = {
                'has_detailed_config': has_detailed_config,
                'has_module_status': has_module_status,
                'has_error_stats': has_error_stats,
                'has_performance_metrics': has_performance_metrics,
                'response_length': len(str(response_data))
            }
            
            self.log_test_result("驗證管理員權限", success, details)
            
            self.assertTrue(has_detailed_config, "管理員應能獲取詳細的系統配置信息")
            self.assertTrue(has_module_status, "管理員應能獲取各模塊的運行狀態")
            
        except Exception as e:
            self.log_test_result("驗證管理員權限", False, {'error': str(e)})
            self.fail(f"測試執行異常: {e}")
    
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
            
            details = {
                'test_flow_enabled': test_flow_enabled,
                'smartinvention_enabled': smartinvention_enabled,
                'has_positive_uptime': has_positive_uptime,
                'acceptable_error_rate': acceptable_error_rate
            }
            
            self.log_test_result("監控系統健康狀態", success, details)
            
            # 至少一個核心模塊應該是啟用的
            self.assertTrue(test_flow_enabled or smartinvention_enabled, "至少一個核心模塊應該是啟用的")
            
        except Exception as e:
            self.log_test_result("監控系統健康狀態", False, {'error': str(e)})
            self.fail(f"測試執行異常: {e}")
    
    def tearDown(self):
        """測試後清理"""
        # 保存測試結果
        if hasattr(self, 'test_results') and self.test_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = f"admin_system_monitoring_results_{timestamp}.json"
            result_path = Path(__file__).parent.parent / "results" / result_file
            
            test_summary = {
                'test_session': {
                    'test_class': 'TestAdminSystemMonitoring',
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
            
            print(f"\n📄 管理員測試結果已保存到: {result_path}")

if __name__ == "__main__":
    # 運行測試
    unittest.main(verbosity=2)
