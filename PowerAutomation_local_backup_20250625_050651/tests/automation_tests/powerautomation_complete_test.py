#!/usr/bin/env python3
"""
PowerAutomation 完整測試套件
測試所有Manus/TRAE功能和API端點
"""

import requests
import json
import time
from datetime import datetime

class PowerAutomationTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/powerautomation"
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """記錄測試結果"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   📝 {details}")
        if response_data and isinstance(response_data, dict):
            if 'error' in response_data:
                print(f"   ⚠️  錯誤: {response_data['error']}")
        print()
        
    def test_health_check(self):
        """測試健康檢查"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=10)
            success = response.status_code == 200
            data = response.json() if response.status_code == 200 else None
            
            details = f"狀態碼: {response.status_code}"
            if data:
                details += f", 服務狀態: {data.get('status', '未知')}"
                
            self.log_test("健康檢查", success, details, data)
            return success
            
        except Exception as e:
            self.log_test("健康檢查", False, f"請求失敗: {str(e)}")
            return False
    
    def test_system_status(self):
        """測試系統狀態"""
        try:
            response = requests.get(f"{self.api_base}/status", timeout=10)
            success = response.status_code == 200
            data = response.json() if response.status_code == 200 else None
            
            details = f"狀態碼: {response.status_code}"
            if data and data.get('success'):
                status = data.get('status', {})
                details += f", 運行中: {status.get('running', False)}"
                details += f", TRAE連接: {status.get('trae_connected', False)}"
                
            self.log_test("系統狀態檢查", success, details, data)
            return success
            
        except Exception as e:
            self.log_test("系統狀態檢查", False, f"請求失敗: {str(e)}")
            return False
    
    def test_system_start(self):
        """測試系統啟動"""
        try:
            response = requests.post(f"{self.api_base}/start", timeout=10)
            success = response.status_code == 200
            data = response.json() if response.status_code == 200 else None
            
            details = f"狀態碼: {response.status_code}"
            if data and data.get('success'):
                details += ", 系統啟動成功"
                
            self.log_test("系統啟動", success, details, data)
            return success
            
        except Exception as e:
            self.log_test("系統啟動", False, f"請求失敗: {str(e)}")
            return False
    
    def test_trae_status(self):
        """測試TRAE狀態"""
        try:
            response = requests.get(f"{self.api_base}/trae/status", timeout=10)
            success = response.status_code == 200
            data = response.json() if response.status_code == 200 else None
            
            details = f"狀態碼: {response.status_code}"
            if data and data.get('success'):
                trae_status = data.get('trae_status', {})
                details += f", TRAE可用: {trae_status.get('available', False)}"
                
            self.log_test("TRAE狀態檢查", success, details, data)
            return success
            
        except Exception as e:
            self.log_test("TRAE狀態檢查", False, f"請求失敗: {str(e)}")
            return False
    
    def test_trae_send(self):
        """測試TRAE發送消息"""
        try:
            payload = {
                "message": "🧪 PowerAutomation測試消息",
                "repository": "smartinvention"
            }
            
            response = requests.post(
                f"{self.api_base}/trae/send",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            success = response.status_code == 200
            data = response.json() if response.status_code == 200 else None
            
            details = f"狀態碼: {response.status_code}"
            if data and data.get('success'):
                details += ", 消息發送成功"
            elif data and not data.get('success'):
                details += f", 發送失敗: {data.get('error', '未知錯誤')}"
                
            self.log_test("TRAE消息發送", success, details, data)
            return success
            
        except Exception as e:
            self.log_test("TRAE消息發送", False, f"請求失敗: {str(e)}")
            return False
    
    def test_trae_sync(self):
        """測試TRAE數據同步"""
        try:
            payload = {
                "repository": "smartinvention",
                "force": True
            }
            
            response = requests.post(
                f"{self.api_base}/trae/sync",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            success = response.status_code == 200
            data = response.json() if response.status_code == 200 else None
            
            details = f"狀態碼: {response.status_code}"
            if data and data.get('success'):
                details += ", 同步成功"
            elif data and not data.get('success'):
                details += f", 同步失敗: {data.get('error', '未知錯誤')}"
                
            self.log_test("TRAE數據同步", success, details, data)
            return success
            
        except Exception as e:
            self.log_test("TRAE數據同步", False, f"請求失敗: {str(e)}")
            return False
    
    def test_manus_connect(self):
        """測試Manus連接"""
        try:
            response = requests.post(f"{self.api_base}/manus/connect", timeout=10)
            success = response.status_code == 200
            data = response.json() if response.status_code == 200 else None
            
            details = f"狀態碼: {response.status_code}"
            if data and data.get('success'):
                details += ", Manus連接成功"
                
            self.log_test("Manus連接", success, details, data)
            return success
            
        except Exception as e:
            self.log_test("Manus連接", False, f"請求失敗: {str(e)}")
            return False
    
    def test_manus_tasks(self):
        """測試獲取Manus任務列表"""
        try:
            response = requests.get(f"{self.api_base}/manus/tasks", timeout=10)
            success = response.status_code == 200
            data = response.json() if response.status_code == 200 else None
            
            details = f"狀態碼: {response.status_code}"
            if data and data.get('success'):
                tasks = data.get('tasks', [])
                details += f", 任務數量: {len(tasks)}"
                
            self.log_test("Manus任務列表", success, details, data)
            return success
            
        except Exception as e:
            self.log_test("Manus任務列表", False, f"請求失敗: {str(e)}")
            return False
    
    def test_conversation_analysis(self):
        """測試對話分析"""
        try:
            payload = {
                "messages": [
                    {"role": "user", "content": "我需要幫助設置PowerAutomation"},
                    {"role": "assistant", "content": "我可以幫您設置PowerAutomation系統"}
                ],
                "repository": "smartinvention",
                "conversation_id": "test_conv_001"
            }
            
            response = requests.post(
                f"{self.api_base}/analyze",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            success = response.status_code == 200
            data = response.json() if response.status_code == 200 else None
            
            details = f"狀態碼: {response.status_code}"
            if data and data.get('success'):
                analysis = data.get('analysis', {})
                details += f", 消息數: {analysis.get('message_count', 0)}"
                details += f", 需要介入: {analysis.get('intervention_needed', False)}"
                
            self.log_test("對話分析", success, details, data)
            return success
            
        except Exception as e:
            self.log_test("對話分析", False, f"請求失敗: {str(e)}")
            return False
    
    def test_intelligent_intervention(self):
        """測試智能介入"""
        try:
            payload = {
                "type": "suggestion",
                "target": "trae",
                "message": "建議查看PowerAutomation文檔",
                "context": {
                    "repository": "smartinvention",
                    "conversation_id": "test_conv_001"
                }
            }
            
            response = requests.post(
                f"{self.api_base}/intervene",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            success = response.status_code == 200
            data = response.json() if response.status_code == 200 else None
            
            details = f"狀態碼: {response.status_code}"
            if data and data.get('success'):
                intervention = data.get('intervention', {})
                details += f", 介入狀態: {intervention.get('status', '未知')}"
                
            self.log_test("智能介入", success, details, data)
            return success
            
        except Exception as e:
            self.log_test("智能介入", False, f"請求失敗: {str(e)}")
            return False
    
    def test_repositories(self):
        """測試獲取倉庫列表"""
        try:
            response = requests.get(f"{self.api_base}/repositories", timeout=10)
            success = response.status_code == 200
            data = response.json() if response.status_code == 200 else None
            
            details = f"狀態碼: {response.status_code}"
            if data and data.get('success'):
                repos = data.get('repositories', [])
                details += f", 倉庫數量: {len(repos)}"
                
            self.log_test("倉庫列表", success, details, data)
            return success
            
        except Exception as e:
            self.log_test("倉庫列表", False, f"請求失敗: {str(e)}")
            return False
    
    def test_system_test(self):
        """測試系統自檢"""
        try:
            payload = {"type": "full"}
            
            response = requests.post(
                f"{self.api_base}/test",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            success = response.status_code == 200
            data = response.json() if response.status_code == 200 else None
            
            details = f"狀態碼: {response.status_code}"
            if data and data.get('success'):
                test_results = data.get('test_results', {})
                summary = test_results.get('summary', {})
                details += f", 成功率: {summary.get('success_rate', '0%')}"
                details += f", 狀態: {summary.get('status', '未知')}"
                
            self.log_test("系統自檢", success, details, data)
            return success
            
        except Exception as e:
            self.log_test("系統自檢", False, f"請求失敗: {str(e)}")
            return False
    
    def run_all_tests(self):
        """執行所有測試"""
        print("🚀 PowerAutomation 完整測試開始")
        print("=" * 50)
        
        start_time = time.time()
        
        # 基礎測試
        print("📋 基礎功能測試")
        print("-" * 30)
        self.test_health_check()
        self.test_system_status()
        self.test_system_start()
        
        # TRAE測試
        print("🔧 TRAE功能測試")
        print("-" * 30)
        self.test_trae_status()
        self.test_trae_send()
        self.test_trae_sync()
        
        # Manus測試
        print("🌐 Manus功能測試")
        print("-" * 30)
        self.test_manus_connect()
        self.test_manus_tasks()
        
        # 智能功能測試
        print("🧠 智能功能測試")
        print("-" * 30)
        self.test_conversation_analysis()
        self.test_intelligent_intervention()
        
        # 其他功能測試
        print("📊 其他功能測試")
        print("-" * 30)
        self.test_repositories()
        self.test_system_test()
        
        # 測試總結
        end_time = time.time()
        duration = end_time - start_time
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("=" * 50)
        print("📊 測試總結")
        print(f"⏱️  執行時間: {duration:.2f}秒")
        print(f"📈 總測試數: {total_tests}")
        print(f"✅ 通過測試: {passed_tests}")
        print(f"❌ 失敗測試: {total_tests - passed_tests}")
        print(f"📊 成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 測試結果: 優秀")
        elif success_rate >= 60:
            print("👍 測試結果: 良好")
        else:
            print("⚠️  測試結果: 需要改進")
        
        return self.test_results

def main():
    """主函數"""
    import sys
    
    # 檢查命令行參數
    base_url = "http://localhost:5000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"🎯 測試目標: {base_url}")
    print()
    
    # 創建測試器並執行測試
    tester = PowerAutomationTester(base_url)
    results = tester.run_all_tests()
    
    # 保存測試結果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"powerautomation_test_results_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"📄 測試結果已保存到: {results_file}")

if __name__ == "__main__":
    main()

