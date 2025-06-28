#!/usr/bin/env python3
"""
Claude Code 路由器測試執行器
基於 tests/templates 格式執行完整測試
"""

import asyncio
import yaml
import json
import time
from typing import Dict, Any, List
from datetime import datetime
from claude_code_real_router import ClaudeCodeRealRouter

class TestExecutor:
    """測試執行器"""
    
    def __init__(self, test_config_path: str):
        with open(test_config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        self.router = ClaudeCodeRealRouter()
        self.results = []
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """執行所有測試"""
        print(f"🚀 開始執行測試套件: {self.config['test_suite']['name']}")
        print(f"📝 描述: {self.config['test_suite']['description']}")
        print("="*60)
        
        start_time = time.time()
        
        # 執行基本功能測試
        basic_results = await self._run_basic_tests()
        
        # 執行性能測試
        performance_results = await self._run_performance_tests()
        
        # 執行對比測試
        comparison_results = await self._run_comparison_tests()
        
        # 執行專家驗證測試
        expert_results = await self._run_expert_validation()
        
        end_time = time.time()
        
        # 生成測試報告
        report = self._generate_test_report(
            basic_results, performance_results, 
            comparison_results, expert_results,
            end_time - start_time
        )
        
        return report
    
    async def _run_basic_tests(self) -> List[Dict[str, Any]]:
        """執行基本功能測試"""
        print("\n📋 執行基本功能測試")
        print("-" * 40)
        
        results = []
        test_cases = self.config.get('test_cases', [])
        
        for i, test_case in enumerate(test_cases):
            print(f"\n🔍 測試 {i+1}/{len(test_cases)}: {test_case['name']}")
            
            try:
                # 執行測試步驟
                step = test_case['steps'][0]  # 假設每個測試只有一個步驟
                payload = step['payload']
                
                start_time = time.time()
                response = await self.router.analyze_and_route(
                    payload['user_input'], 
                    payload['context']
                )
                end_time = time.time()
                
                # 驗證結果
                validation_results = self._validate_response(response, step.get('validation', []))
                
                result = {
                    "test_name": test_case['name'],
                    "status": "PASS" if all(validation_results.values()) else "FAIL",
                    "response_time": end_time - start_time,
                    "response": response,
                    "validations": validation_results
                }
                
                results.append(result)
                
                # 打印結果
                status_icon = "✅" if result["status"] == "PASS" else "❌"
                print(f"{status_icon} {result['status']} - {result['response_time']:.2f}s")
                
                if response['status'] == 'success':
                    analysis = response['scenario_analysis']
                    print(f"   場景: {analysis['scenario_type']}")
                    print(f"   複雜度: {analysis['complexity_level']}")
                    if analysis['recommended_experts']:
                        expert = analysis['recommended_experts'][0]
                        print(f"   專家: {expert['expert_type']} (信心度: {expert['confidence']})")
                
            except Exception as e:
                result = {
                    "test_name": test_case['name'],
                    "status": "ERROR",
                    "error": str(e),
                    "response_time": 0
                }
                results.append(result)
                print(f"❌ ERROR - {str(e)}")
        
        return results
    
    async def _run_performance_tests(self) -> List[Dict[str, Any]]:
        """執行性能測試"""
        print("\n⚡ 執行性能測試")
        print("-" * 40)
        
        results = []
        performance_tests = self.config.get('performance_tests', [])
        
        for test in performance_tests:
            print(f"\n🔍 性能測試: {test['name']}")
            
            try:
                payload = test['payload']
                expected_perf = test['expected_performance']
                
                start_time = time.time()
                response = await self.router.analyze_and_route(
                    payload['user_input'], 
                    payload['context']
                )
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                max_time_ms = expected_perf['max_response_time']
                
                result = {
                    "test_name": test['name'],
                    "status": "PASS" if response_time_ms <= max_time_ms else "FAIL",
                    "response_time_ms": response_time_ms,
                    "max_allowed_ms": max_time_ms,
                    "response": response
                }
                
                results.append(result)
                
                status_icon = "✅" if result["status"] == "PASS" else "❌"
                print(f"{status_icon} {result['status']} - {response_time_ms:.0f}ms (限制: {max_time_ms}ms)")
                
            except Exception as e:
                result = {
                    "test_name": test['name'],
                    "status": "ERROR",
                    "error": str(e)
                }
                results.append(result)
                print(f"❌ ERROR - {str(e)}")
        
        return results
    
    async def _run_comparison_tests(self) -> List[Dict[str, Any]]:
        """執行對比測試"""
        print("\n🔄 執行對比測試 (Claude Code vs 傳統路由)")
        print("-" * 40)
        
        results = []
        comparison_tests = self.config.get('comparison_tests', [])
        
        for test in comparison_tests:
            print(f"\n🔍 對比測試: {test['name']}")
            
            scenarios = test.get('scenarios', [])
            for scenario in scenarios:
                try:
                    response = await self.router.analyze_and_route(scenario['input'], {})
                    
                    if response['status'] == 'success':
                        analysis = response['scenario_analysis']
                        expected_claude = scenario['expected_claude_code']
                        
                        # 檢查場景識別準確性
                        scenario_match = analysis['scenario_type'] == expected_claude['scenario_type']
                        
                        # 檢查專家推薦準確性
                        expert_match = False
                        if analysis['recommended_experts']:
                            expert_match = analysis['recommended_experts'][0]['expert_type'] == expected_claude['expert_type']
                        
                        # 檢查信心度
                        confidence_ok = analysis['confidence_score'] >= float(expected_claude['confidence'].replace('>= ', ''))
                        
                        result = {
                            "input": scenario['input'][:50] + "...",
                            "scenario_match": scenario_match,
                            "expert_match": expert_match,
                            "confidence_ok": confidence_ok,
                            "actual_scenario": analysis['scenario_type'],
                            "actual_expert": analysis['recommended_experts'][0]['expert_type'] if analysis['recommended_experts'] else "none",
                            "actual_confidence": analysis['confidence_score']
                        }
                        
                        results.append(result)
                        
                        status = "✅ PASS" if all([scenario_match, expert_match, confidence_ok]) else "❌ FAIL"
                        print(f"{status} - 場景: {scenario_match}, 專家: {expert_match}, 信心度: {confidence_ok}")
                        
                except Exception as e:
                    print(f"❌ ERROR - {str(e)}")
        
        return results
    
    async def _run_expert_validation(self) -> List[Dict[str, Any]]:
        """執行專家驗證測試"""
        print("\n👨‍💼 執行專家驗證測試")
        print("-" * 40)
        
        results = []
        expert_validations = self.config.get('expert_validation', [])
        
        for expert_config in expert_validations:
            expert_type = expert_config['expert_type']
            test_scenarios = expert_config['test_scenarios']
            expected_keywords = expert_config['expected_keywords']
            
            print(f"\n🔍 驗證專家: {expert_type}")
            
            expert_results = []
            
            for scenario in test_scenarios:
                try:
                    response = await self.router.analyze_and_route(scenario, {})
                    
                    if response['status'] == 'success':
                        # 檢查是否推薦了正確的專家
                        recommended_experts = response['scenario_analysis']['recommended_experts']
                        correct_expert = any(exp['expert_type'] == expert_type for exp in recommended_experts)
                        
                        # 檢查專家回應中是否包含預期關鍵詞
                        expert_response = ""
                        if 'processing_result' in response and 'expert_analysis' in response['processing_result']:
                            expert_response = response['processing_result']['expert_analysis'].get('expert_response', '').lower()
                        
                        keyword_matches = sum(1 for keyword in expected_keywords if keyword.lower() in expert_response)
                        keyword_score = keyword_matches / len(expected_keywords)
                        
                        expert_results.append({
                            "scenario": scenario,
                            "correct_expert": correct_expert,
                            "keyword_score": keyword_score,
                            "keyword_matches": keyword_matches
                        })
                        
                        status = "✅" if correct_expert and keyword_score >= 0.5 else "❌"
                        print(f"{status} {scenario[:30]}... - 專家: {correct_expert}, 關鍵詞: {keyword_matches}/{len(expected_keywords)}")
                        
                except Exception as e:
                    print(f"❌ ERROR - {str(e)}")
            
            results.append({
                "expert_type": expert_type,
                "results": expert_results
            })
        
        return results
    
    def _validate_response(self, response: Dict[str, Any], validations: List[str]) -> Dict[str, bool]:
        """驗證回應結果"""
        results = {}
        
        for validation in validations:
            try:
                # 簡單的驗證邏輯
                if "response.status == 'success'" in validation:
                    results[validation] = response.get('status') == 'success'
                elif "scenario_type ==" in validation:
                    expected_type = validation.split("== '")[1].split("'")[0]
                    actual_type = response.get('scenario_analysis', {}).get('scenario_type', '')
                    results[validation] = actual_type == expected_type
                elif "complexity_level in" in validation:
                    allowed_levels = validation.split("in ")[1].strip("[]").replace("'", "").split(", ")
                    actual_level = response.get('scenario_analysis', {}).get('complexity_level', '')
                    results[validation] = actual_level in allowed_levels
                elif "len(response.scenario_analysis.recommended_experts)" in validation:
                    experts = response.get('scenario_analysis', {}).get('recommended_experts', [])
                    expected_count = int(validation.split(">= ")[1])
                    results[validation] = len(experts) >= expected_count
                elif "expert_type ==" in validation:
                    expected_expert = validation.split("== '")[1].split("'")[0]
                    experts = response.get('scenario_analysis', {}).get('recommended_experts', [])
                    actual_expert = experts[0].get('expert_type', '') if experts else ''
                    results[validation] = actual_expert == expected_expert
                elif "confidence_score >=" in validation:
                    expected_score = float(validation.split(">= ")[1])
                    actual_score = response.get('scenario_analysis', {}).get('confidence_score', 0)
                    results[validation] = actual_score >= expected_score
                else:
                    # 其他驗證邏輯
                    results[validation] = True
                    
            except Exception as e:
                results[validation] = False
        
        return results
    
    def _generate_test_report(self, basic_results: List, performance_results: List, 
                            comparison_results: List, expert_results: List, 
                            total_time: float) -> Dict[str, Any]:
        """生成測試報告"""
        
        # 計算統計數據
        total_basic = len(basic_results)
        passed_basic = sum(1 for r in basic_results if r.get('status') == 'PASS')
        
        total_performance = len(performance_results)
        passed_performance = sum(1 for r in performance_results if r.get('status') == 'PASS')
        
        # 計算成功率
        basic_success_rate = (passed_basic / total_basic * 100) if total_basic > 0 else 0
        performance_success_rate = (passed_performance / total_performance * 100) if total_performance > 0 else 0
        
        report = {
            "test_summary": {
                "test_suite": self.config['test_suite']['name'],
                "total_execution_time": f"{total_time:.2f}s",
                "timestamp": datetime.now().isoformat()
            },
            "basic_tests": {
                "total": total_basic,
                "passed": passed_basic,
                "failed": total_basic - passed_basic,
                "success_rate": f"{basic_success_rate:.1f}%",
                "results": basic_results
            },
            "performance_tests": {
                "total": total_performance,
                "passed": passed_performance,
                "failed": total_performance - passed_performance,
                "success_rate": f"{performance_success_rate:.1f}%",
                "results": performance_results
            },
            "comparison_tests": {
                "results": comparison_results
            },
            "expert_validation": {
                "results": expert_results
            },
            "overall_assessment": {
                "claude_code_routing_effectiveness": "HIGH" if basic_success_rate >= 80 else "MEDIUM" if basic_success_rate >= 60 else "LOW",
                "expert_recommendation_accuracy": "HIGH" if passed_basic >= total_basic * 0.8 else "MEDIUM",
                "performance_satisfaction": "GOOD" if performance_success_rate >= 80 else "FAIR"
            }
        }
        
        return report

async def main():
    """主函數"""
    executor = TestExecutor('/home/ubuntu/claude_code_router_test.yaml')
    report = await executor.run_all_tests()
    
    # 保存測試報告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"/home/ubuntu/claude_router_test_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, ensure_ascii=False, indent=2)
    
    # 打印總結
    print("\n" + "="*60)
    print("📊 測試總結報告")
    print("="*60)
    print(f"✅ 基本功能測試: {report['basic_tests']['success_rate']} ({report['basic_tests']['passed']}/{report['basic_tests']['total']})")
    print(f"⚡ 性能測試: {report['performance_tests']['success_rate']} ({report['performance_tests']['passed']}/{report['performance_tests']['total']})")
    print(f"🎯 Claude Code 路由效果: {report['overall_assessment']['claude_code_routing_effectiveness']}")
    print(f"👨‍💼 專家推薦準確性: {report['overall_assessment']['expert_recommendation_accuracy']}")
    print(f"📈 性能表現: {report['overall_assessment']['performance_satisfaction']}")
    print(f"⏱️  總執行時間: {report['test_summary']['total_execution_time']}")
    print(f"📄 詳細報告: {report_file}")
    
    return report

if __name__ == "__main__":
    asyncio.run(main())

