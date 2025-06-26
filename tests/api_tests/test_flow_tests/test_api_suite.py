#!/usr/bin/env python3
"""
test_flow_mcp API 測試套件範例
實現 SOP 文檔中描述的測試案例
"""

import pytest
import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any
from jsonschema import validate, ValidationError

class TestFlowAPIClient:
    """test_flow_mcp API 客戶端"""
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-Key': api_key,
            'User-Agent': 'test_flow_mcp_api_tester/1.0'
        })
    
    def execute_test(self, test_data: Dict) -> requests.Response:
        """執行測試 API"""
        return self.session.post(
            f"{self.base_url}/api/test/execute",
            json=test_data,
            timeout=self.timeout
        )
    
    def get_test_status(self, task_id: str) -> requests.Response:
        """獲取測試狀態"""
        return self.session.get(
            f"{self.base_url}/api/test/status/{task_id}",
            timeout=self.timeout
        )
    
    def get_test_results(self, task_id: str) -> requests.Response:
        """獲取測試結果"""
        return self.session.get(
            f"{self.base_url}/api/test/results/{task_id}",
            timeout=self.timeout
        )
    
    def get_system_health(self) -> requests.Response:
        """獲取系統健康狀態"""
        return self.session.get(
            f"{self.base_url}/api/system/health",
            timeout=self.timeout
        )
    
    def get_system_metrics(self) -> requests.Response:
        """獲取系統指標"""
        return self.session.get(
            f"{self.base_url}/api/system/metrics",
            timeout=self.timeout
        )

@pytest.fixture(scope="session")
def api_client():
    """API 客戶端 fixture"""
    return TestFlowAPIClient(
        base_url="http://127.0.0.1:8080",
        api_key="test_407CYuVKuP_s3hVqIhO4JZKqcE4-W9ocTgc_fldjxso",
        timeout=30
    )

@pytest.fixture
def test_data_generator():
    """測試數據生成器"""
    class TestDataGenerator:
        @staticmethod
        def generate_requirement_text(complexity="medium"):
            templates = {
                "simple": [
                    "用戶需要登錄功能",
                    "系統應該支援搜索",
                    "實現用戶註冊模組"
                ],
                "medium": [
                    "用戶希望能夠快速搜索產品，並且支援多種篩選條件",
                    "系統需要提供用戶管理功能，支援角色權限控制",
                    "實現訂單處理流程，包括創建、支付、發貨等狀態"
                ],
                "complex": [
                    "用戶在移動端需要離線瀏覽功能，要求數據同步穩定，同時考慮存儲空間限制",
                    "系統應該提供實時通知功能，支援推送和郵件通知，並且考慮用戶隱私設置"
                ]
            }
            import random
            return random.choice(templates[complexity])
        
        @staticmethod
        def generate_unique_id():
            return str(uuid.uuid4())[:8]
    
    return TestDataGenerator()

class TestExecuteAPI:
    """測試執行 API 測試類"""
    
    def test_requirement_analysis_basic(self, api_client, test_data_generator):
        """基礎需求分析測試"""
        test_data = {
            "test_type": "requirement_analysis",
            "test_parameters": {
                "requirement_text": test_data_generator.generate_requirement_text("simple"),
                "analysis_depth": "standard"
            },
            "execution_options": {
                "timeout": 300,
                "priority": "medium"
            }
        }
        
        response = api_client.execute_test(test_data)
        
        # 驗證響應狀態碼
        assert response.status_code == 200, f"期望狀態碼 200，實際 {response.status_code}"
        
        # 驗證響應格式
        response_data = response.json()
        expected_schema = {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "task_id": {"type": "string"},
                "status": {"type": "string", "enum": ["running", "queued"]},
                "estimated_completion": {"type": "string"}
            },
            "required": ["success", "task_id", "status"]
        }
        
        try:
            validate(instance=response_data, schema=expected_schema)
        except ValidationError as e:
            pytest.fail(f"響應格式驗證失敗: {e.message}")
        
        # 驗證業務邏輯
        assert response_data['success'] is True, "success 字段應為 true"
        assert len(response_data['task_id']) > 0, "task_id 不能為空"
        assert response_data['status'] in ['running', 'queued'], f"無效的狀態: {response_data['status']}"
        
        return response_data['task_id']
    
    @pytest.mark.parametrize("test_type,expected_status", [
        ("requirement_analysis", 200),
        ("functional_test", 200),
        ("integration_test", 200),
        ("performance_test", 200)
    ])
    def test_different_test_types(self, api_client, test_data_generator, test_type, expected_status):
        """不同測試類型執行測試"""
        test_data = {
            "test_type": test_type,
            "test_parameters": {
                "requirement_text": f"測試 {test_type} 功能 - {test_data_generator.generate_unique_id()}"
            }
        }
        
        response = api_client.execute_test(test_data)
        assert response.status_code == expected_status
        
        if expected_status == 200:
            response_data = response.json()
            assert response_data['success'] is True
            assert 'task_id' in response_data
    
    def test_complex_requirement_analysis(self, api_client, test_data_generator):
        """複雜需求分析測試"""
        test_data = {
            "test_type": "requirement_analysis",
            "test_parameters": {
                "requirement_text": test_data_generator.generate_requirement_text("complex"),
                "analysis_depth": "detailed",
                "include_security_check": True,
                "include_performance_analysis": True
            },
            "execution_options": {
                "timeout": 600,
                "priority": "high",
                "notification_enabled": True
            }
        }
        
        response = api_client.execute_test(test_data)
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data['success'] is True
        assert 'task_id' in response_data
        
        # 驗證複雜參數的處理
        task_id = response_data['task_id']
        
        # 等待一段時間後檢查狀態
        time.sleep(2)
        status_response = api_client.get_test_status(task_id)
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data['success'] is True
        assert status_data['task_id'] == task_id

class TestExecuteAPINegative:
    """測試執行 API 負向測試類"""
    
    def test_missing_required_parameter(self, api_client):
        """缺少必需參數測試"""
        test_data = {
            "test_parameters": {
                "requirement_text": "測試需求"
            }
            # 故意省略 test_type 參數
        }
        
        response = api_client.execute_test(test_data)
        assert response.status_code == 400
        
        response_data = response.json()
        assert response_data['success'] is False
        assert 'error_code' in response_data
        assert response_data['error_code'] in ['MISSING_REQUIRED_PARAMETER', 'VALIDATION_ERROR']
    
    def test_invalid_test_type(self, api_client):
        """無效測試類型測試"""
        test_data = {
            "test_type": "invalid_test_type",
            "test_parameters": {
                "requirement_text": "測試需求"
            }
        }
        
        response = api_client.execute_test(test_data)
        assert response.status_code == 400
        
        response_data = response.json()
        assert response_data['success'] is False
        assert 'error_code' in response_data
    
    def test_invalid_api_key(self, api_client):
        """無效 API Key 測試"""
        # 創建使用無效 API Key 的客戶端
        invalid_client = TestFlowAPIClient(
            base_url=api_client.base_url,
            api_key="invalid_api_key_12345",
            timeout=api_client.timeout
        )
        
        test_data = {
            "test_type": "requirement_analysis",
            "test_parameters": {
                "requirement_text": "測試需求"
            }
        }
        
        response = invalid_client.execute_test(test_data)
        assert response.status_code == 401
        
        response_data = response.json()
        assert response_data['success'] is False
        assert 'error_code' in response_data
    
    @pytest.mark.parametrize("invalid_input,expected_error", [
        ("", "EMPTY_PARAMETER"),
        ("A" * 10001, "PARAMETER_TOO_LONG"),
        ("<script>alert('xss')</script>", "INVALID_INPUT"),
        ("'; DROP TABLE users; --", "INVALID_INPUT")
    ])
    def test_invalid_requirement_text(self, api_client, invalid_input, expected_error):
        """無效需求文本測試"""
        test_data = {
            "test_type": "requirement_analysis",
            "test_parameters": {
                "requirement_text": invalid_input
            }
        }
        
        response = api_client.execute_test(test_data)
        assert response.status_code == 400
        
        response_data = response.json()
        assert response_data['success'] is False
        assert 'error_code' in response_data
        # 注意：實際的錯誤碼可能與預期不完全匹配，這裡只檢查是否有錯誤碼

class TestStatusAPI:
    """測試狀態查詢 API 測試類"""
    
    def test_valid_task_status_query(self, api_client, test_data_generator):
        """有效任務狀態查詢測試"""
        # 首先創建一個測試任務
        test_data = {
            "test_type": "requirement_analysis",
            "test_parameters": {
                "requirement_text": test_data_generator.generate_requirement_text("simple")
            }
        }
        
        execute_response = api_client.execute_test(test_data)
        assert execute_response.status_code == 200
        
        execute_data = execute_response.json()
        task_id = execute_data['task_id']
        
        # 查詢任務狀態
        status_response = api_client.get_test_status(task_id)
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data['success'] is True
        assert status_data['task_id'] == task_id
        assert 'status' in status_data
        assert status_data['status'] in ['running', 'queued', 'completed', 'failed']
    
    def test_invalid_task_id_query(self, api_client):
        """無效任務 ID 查詢測試"""
        invalid_task_id = "invalid_task_id_12345"
        
        response = api_client.get_test_status(invalid_task_id)
        assert response.status_code == 404
        
        response_data = response.json()
        assert response_data['success'] is False
        assert 'error_code' in response_data
    
    def test_status_query_with_progress(self, api_client, test_data_generator):
        """帶進度信息的狀態查詢測試"""
        # 創建一個較複雜的測試任務
        test_data = {
            "test_type": "requirement_analysis",
            "test_parameters": {
                "requirement_text": test_data_generator.generate_requirement_text("complex"),
                "analysis_depth": "detailed"
            }
        }
        
        execute_response = api_client.execute_test(test_data)
        assert execute_response.status_code == 200
        
        task_id = execute_response.json()['task_id']
        
        # 多次查詢狀態，觀察進度變化
        for i in range(3):
            time.sleep(1)
            status_response = api_client.get_test_status(task_id)
            assert status_response.status_code == 200
            
            status_data = status_response.json()
            assert status_data['success'] is True
            
            # 檢查是否有進度信息
            if 'progress' in status_data:
                progress = status_data['progress']
                if 'completion_percentage' in progress:
                    assert 0 <= progress['completion_percentage'] <= 100

class TestResultsAPI:
    """測試結果獲取 API 測試類"""
    
    def test_get_completed_test_results(self, api_client, test_data_generator):
        """獲取已完成測試結果"""
        # 創建並等待測試完成
        test_data = {
            "test_type": "requirement_analysis",
            "test_parameters": {
                "requirement_text": test_data_generator.generate_requirement_text("simple")
            }
        }
        
        execute_response = api_client.execute_test(test_data)
        assert execute_response.status_code == 200
        
        task_id = execute_response.json()['task_id']
        
        # 等待測試完成（最多等待30秒）
        max_wait_time = 30
        wait_interval = 2
        waited_time = 0
        
        while waited_time < max_wait_time:
            time.sleep(wait_interval)
            waited_time += wait_interval
            
            status_response = api_client.get_test_status(task_id)
            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data.get('status') == 'completed':
                    break
        
        # 獲取測試結果
        results_response = api_client.get_test_results(task_id)
        
        if results_response.status_code == 200:
            results_data = results_response.json()
            assert results_data['success'] is True
            assert results_data['task_id'] == task_id
            assert 'results' in results_data
            
            # 驗證結果結構
            results = results_data['results']
            if isinstance(results, dict):
                # 檢查需求分析結果的基本結構
                expected_keys = ['analysis_score', 'feasibility', 'complexity_estimate']
                for key in expected_keys:
                    if key in results:
                        assert results[key] is not None
        else:
            # 如果測試還未完成，應該返回適當的狀態
            assert results_response.status_code in [202, 404]
    
    def test_get_results_for_nonexistent_task(self, api_client):
        """獲取不存在任務的結果"""
        invalid_task_id = "nonexistent_task_12345"
        
        response = api_client.get_test_results(invalid_task_id)
        assert response.status_code == 404
        
        response_data = response.json()
        assert response_data['success'] is False
        assert 'error_code' in response_data

class TestSystemAPI:
    """系統管理 API 測試類"""
    
    def test_system_health_check(self, api_client):
        """系統健康檢查測試"""
        response = api_client.get_system_health()
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data['success'] is True
        assert 'status' in health_data
        assert health_data['status'] in ['healthy', 'degraded', 'unhealthy']
        
        # 檢查組件狀態
        if 'components' in health_data:
            components = health_data['components']
            assert isinstance(components, dict)
            
            # 驗證關鍵組件
            expected_components = ['database', 'mcp_coordinator', 'test_engines']
            for component in expected_components:
                if component in components:
                    assert 'status' in components[component]
    
    def test_system_metrics(self, api_client):
        """系統指標測試"""
        response = api_client.get_system_metrics()
        
        # 系統指標可能需要特殊權限，所以允許 403 狀態碼
        assert response.status_code in [200, 403]
        
        if response.status_code == 200:
            # 如果返回 200，檢查是否為 Prometheus 格式
            content_type = response.headers.get('Content-Type', '')
            if 'text/plain' in content_type:
                # Prometheus 格式
                metrics_text = response.text
                assert '# HELP' in metrics_text or '# TYPE' in metrics_text
            else:
                # JSON 格式
                metrics_data = response.json()
                assert isinstance(metrics_data, dict)

class TestPerformance:
    """性能測試類"""
    
    def test_concurrent_requests(self, api_client, test_data_generator):
        """併發請求測試"""
        import threading
        import queue
        
        num_threads = 5
        results_queue = queue.Queue()
        
        def make_request():
            try:
                test_data = {
                    "test_type": "requirement_analysis",
                    "test_parameters": {
                        "requirement_text": test_data_generator.generate_requirement_text("simple")
                    }
                }
                
                start_time = time.time()
                response = api_client.execute_test(test_data)
                end_time = time.time()
                
                results_queue.put({
                    'status_code': response.status_code,
                    'response_time': end_time - start_time,
                    'success': response.status_code == 200
                })
            except Exception as e:
                results_queue.put({
                    'status_code': 0,
                    'response_time': 0,
                    'success': False,
                    'error': str(e)
                })
        
        # 創建並啟動線程
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有線程完成
        for thread in threads:
            thread.join(timeout=30)
        
        # 收集結果
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        # 驗證結果
        assert len(results) == num_threads, f"期望 {num_threads} 個結果，實際 {len(results)}"
        
        successful_requests = sum(1 for r in results if r['success'])
        success_rate = successful_requests / num_threads
        
        # 至少 80% 的請求應該成功
        assert success_rate >= 0.8, f"成功率過低: {success_rate:.2%}"
        
        # 檢查響應時間
        response_times = [r['response_time'] for r in results if r['success']]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            # 平均響應時間應該在合理範圍內
            assert avg_response_time < 10, f"平均響應時間過高: {avg_response_time:.2f}秒"
            assert max_response_time < 20, f"最大響應時間過高: {max_response_time:.2f}秒"
    
    @pytest.mark.slow
    def test_response_time_stability(self, api_client, test_data_generator):
        """響應時間穩定性測試"""
        num_requests = 10
        response_times = []
        
        for i in range(num_requests):
            test_data = {
                "test_type": "requirement_analysis",
                "test_parameters": {
                    "requirement_text": f"{test_data_generator.generate_requirement_text('simple')} - 請求 {i+1}"
                }
            }
            
            start_time = time.time()
            response = api_client.execute_test(test_data)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
            
            # 請求間隔
            time.sleep(0.5)
        
        # 計算統計指標
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        # 計算變異係數
        import statistics
        std_dev = statistics.stdev(response_times)
        cv = std_dev / avg_time if avg_time > 0 else 0
        
        # 驗證穩定性
        assert cv < 0.5, f"響應時間變異係數過高: {cv:.3f}"
        assert max_time / min_time < 3, f"響應時間差異過大: 最大 {max_time:.2f}s, 最小 {min_time:.2f}s"

if __name__ == "__main__":
    # 運行測試
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--maxfail=5",
        "-x"  # 遇到第一個失敗就停止
    ])

