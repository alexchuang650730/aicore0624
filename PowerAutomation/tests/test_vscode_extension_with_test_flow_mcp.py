#!/usr/bin/env python3
"""
VSCode Extension Test Scenarios Configuration
使用真實Test Flow MCP v4進行VSCode擴展安裝和驗證系統測試

基於Enhanced Test Flow MCP v4.0的真實測試場景
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

# 添加PowerAutomation路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'PowerAutomation'))

# 導入Enhanced Test Flow MCP v4
try:
    from PowerAutomation.components.enhanced_test_flow_mcp_v4 import (
        EnhancedTestFlowMCP,
        DeveloperRequest,
        UserMode,
        FixStrategy,
        ProcessingStage
    )
except ImportError as e:
    print(f"導入Enhanced Test Flow MCP v4失敗: {e}")
    sys.exit(1)

logger = logging.getLogger(__name__)

class VSCodeExtensionTestScenarios:
    """VSCode擴展測試場景"""
    
    def __init__(self):
        self.test_flow_mcp = None
        self.test_scenarios = []
        self.test_results = []
        
    async def initialize_test_flow_mcp(self):
        """初始化Test Flow MCP"""
        logger.info("🚀 初始化Enhanced Test Flow MCP v4")
        
        # 創建Test Flow MCP實例
        self.test_flow_mcp = EnhancedTestFlowMCP()
        
        logger.info("✅ Enhanced Test Flow MCP v4初始化成功")
        
    def create_test_scenarios(self) -> List[Dict[str, Any]]:
        """創建VSCode擴展測試場景"""
        
        scenarios = [
            {
                "scenario_id": "vscode_installer_basic_test",
                "scenario_name": "VSCode擴展安裝器基本功能測試",
                "description": "測試Enhanced VSCode Installer MCP的基本安裝功能",
                "requirement": """
                測試VSCode擴展安裝器的基本功能：
                1. Mac環境VSCode檢測
                2. 擴展管理器功能
                3. VSIX文件處理
                4. 基本安裝流程
                
                預期結果：所有基本功能正常運行
                """,
                "manus_context": {
                    "project_type": "vscode_extension_installer",
                    "complexity": "medium",
                    "timeline": "immediate",
                    "test_type": "functionality",
                    "target_platform": "Mac"
                },
                "fix_strategy": "intelligent",
                "expected_stages": [
                    ProcessingStage.REQUIREMENT_SYNC,
                    ProcessingStage.COMPARISON_ANALYSIS,
                    ProcessingStage.EVALUATION_REPORT,
                    ProcessingStage.CODE_FIX
                ]
            },
            
            {
                "scenario_id": "vscode_verification_system_test",
                "scenario_name": "VSCode擴展驗證系統測試",
                "description": "測試Complete Extension Verification System的多層驗證功能",
                "requirement": """
                測試VSCode擴展驗證系統的完整功能：
                1. 功能驗證器 - 擴展激活和命令測試
                2. 性能驗證器 - 啟動時間和內存使用
                3. 兼容性驗證器 - VSCode版本和macOS兼容性
                4. 安全驗證器 - 權限檢查和安全評估
                
                預期結果：四個驗證器都能正常工作並生成詳細報告
                """,
                "manus_context": {
                    "project_type": "verification_system",
                    "complexity": "high",
                    "timeline": "immediate",
                    "test_type": "comprehensive",
                    "verification_layers": 4
                },
                "fix_strategy": "conservative",
                "expected_stages": [
                    ProcessingStage.REQUIREMENT_SYNC,
                    ProcessingStage.COMPARISON_ANALYSIS,
                    ProcessingStage.EVALUATION_REPORT,
                    ProcessingStage.CODE_FIX
                ]
            },
            
            {
                "scenario_id": "local_mcp_integration_test",
                "scenario_name": "Local MCP集成測試",
                "description": "測試VSCode擴展系統與Local MCP Adapter的集成",
                "requirement": """
                測試VSCode擴展系統與aicore0623 Local MCP Adapter的集成：
                1. 工具註冊管理器集成
                2. 心跳管理器狀態同步
                3. 智能路由引擎協作
                4. 異步操作協調
                
                預期結果：所有MCP組件無縫集成，狀態同步正常
                """,
                "manus_context": {
                    "project_type": "mcp_integration",
                    "complexity": "high",
                    "timeline": "immediate",
                    "test_type": "integration",
                    "integration_points": ["tool_registry", "heartbeat", "routing"]
                },
                "fix_strategy": "aggressive",
                "expected_stages": [
                    ProcessingStage.REQUIREMENT_SYNC,
                    ProcessingStage.COMPARISON_ANALYSIS,
                    ProcessingStage.EVALUATION_REPORT,
                    ProcessingStage.CODE_FIX
                ]
            },
            
            {
                "scenario_id": "e2e_workflow_test",
                "scenario_name": "端到端工作流測試",
                "description": "測試完整的VSCode擴展安裝到驗證的端到端流程",
                "requirement": """
                測試完整的端到端工作流：
                1. VSIX文件準備和驗證
                2. 擴展安裝流程執行
                3. 多層驗證系統運行
                4. 結果報告生成
                5. 錯誤處理和恢復
                
                預期結果：完整流程順利執行，生成詳細的測試報告
                """,
                "manus_context": {
                    "project_type": "e2e_workflow",
                    "complexity": "very_high",
                    "timeline": "immediate",
                    "test_type": "end_to_end",
                    "workflow_stages": 5
                },
                "fix_strategy": "kilocode_fallback",
                "expected_stages": [
                    ProcessingStage.REQUIREMENT_SYNC,
                    ProcessingStage.COMPARISON_ANALYSIS,
                    ProcessingStage.EVALUATION_REPORT,
                    ProcessingStage.CODE_FIX
                ]
            },
            
            {
                "scenario_id": "performance_stress_test",
                "scenario_name": "性能壓力測試",
                "description": "測試VSCode擴展系統在高負載下的性能表現",
                "requirement": """
                測試VSCode擴展系統的性能極限：
                1. 並發安裝多個擴展
                2. 大型VSIX文件處理
                3. 內存使用監控
                4. 響應時間測量
                5. 系統穩定性評估
                
                預期結果：系統在高負載下保持穩定，性能指標在可接受範圍內
                """,
                "manus_context": {
                    "project_type": "performance_test",
                    "complexity": "high",
                    "timeline": "immediate",
                    "test_type": "stress",
                    "load_level": "high"
                },
                "fix_strategy": "intelligent",
                "expected_stages": [
                    ProcessingStage.REQUIREMENT_SYNC,
                    ProcessingStage.COMPARISON_ANALYSIS,
                    ProcessingStage.EVALUATION_REPORT,
                    ProcessingStage.CODE_FIX
                ]
            }
        ]
        
        self.test_scenarios = scenarios
        return scenarios
    
    async def execute_test_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """執行單個測試場景"""
        logger.info(f"🧪 執行測試場景: {scenario['scenario_name']}")
        
        start_time = time.time()
        
        try:
            # 使用Test Flow MCP處理請求
            result = await self.test_flow_mcp.process_developer_request(
                requirement=scenario["requirement"],
                mode="developer",
                manus_context=scenario["manus_context"],
                fix_strategy=scenario["fix_strategy"]
            )
            
            execution_time = time.time() - start_time
            
            # 分析結果
            test_result = {
                "scenario_id": scenario["scenario_id"],
                "scenario_name": scenario["scenario_name"],
                "success": result.get("success", False),
                "execution_time": execution_time,
                "stages_completed": result.get("stages_completed", []),
                "final_stage": result.get("final_stage"),
                "confidence_score": result.get("confidence_score", 0.0),
                "solution": result.get("solution", ""),
                "recommendations": result.get("recommendations", []),
                "error_message": result.get("error_message"),
                "detailed_result": result
            }
            
            # 驗證預期階段
            expected_stages = scenario.get("expected_stages", [])
            completed_stages_count = result.get("stages_completed", 0)
            
            # 將數字轉換為階段列表
            if isinstance(completed_stages_count, int):
                stage_names = ["requirement_sync", "comparison_analysis", "evaluation_report", "code_fix"]
                completed_stages = stage_names[:completed_stages_count]
            else:
                completed_stages = result.get("stages_completed", [])
            
            test_result["stages_validation"] = {
                "expected": [stage.value for stage in expected_stages],
                "completed": completed_stages,
                "stages_completed_count": completed_stages_count,
                "all_stages_completed": completed_stages_count >= len(expected_stages)
            }
            
            logger.info(f"✅ 測試場景完成: {scenario['scenario_name']} - {'成功' if test_result['success'] else '失敗'}")
            
        except Exception as e:
            execution_time = time.time() - start_time
            test_result = {
                "scenario_id": scenario["scenario_id"],
                "scenario_name": scenario["scenario_name"],
                "success": False,
                "execution_time": execution_time,
                "error_message": str(e),
                "stages_completed": [],
                "final_stage": None,
                "confidence_score": 0.0
            }
            
            logger.error(f"❌ 測試場景失敗: {scenario['scenario_name']} - {e}")
        
        return test_result
    
    async def run_all_test_scenarios(self) -> Dict[str, Any]:
        """運行所有測試場景"""
        logger.info("🎯 開始運行所有VSCode擴展測試場景")
        
        # 創建測試場景
        scenarios = self.create_test_scenarios()
        
        # 執行所有測試場景
        test_results = []
        for scenario in scenarios:
            result = await self.execute_test_scenario(scenario)
            test_results.append(result)
            self.test_results.append(result)
            
            # 短暫延遲避免過載
            await asyncio.sleep(1)
        
        # 生成總體報告
        total_scenarios = len(test_results)
        successful_scenarios = sum(1 for result in test_results if result["success"])
        
        overall_report = {
            "test_suite": "VSCode Extension System Test with Enhanced Test Flow MCP v4",
            "execution_time": datetime.now().isoformat(),
            "total_scenarios": total_scenarios,
            "successful_scenarios": successful_scenarios,
            "failed_scenarios": total_scenarios - successful_scenarios,
            "success_rate": successful_scenarios / total_scenarios if total_scenarios > 0 else 0,
            "test_results": test_results,
            "summary": {
                "overall_success": successful_scenarios == total_scenarios,
                "average_confidence": sum(r.get("confidence_score", 0) for r in test_results) / total_scenarios if total_scenarios > 0 else 0,
                "total_execution_time": sum(r.get("execution_time", 0) for r in test_results)
            }
        }
        
        logger.info(f"📊 測試完成: {successful_scenarios}/{total_scenarios} 成功 ({overall_report['success_rate']:.2%})")
        
        return overall_report
    
    async def cleanup(self):
        """清理資源"""
        if self.test_flow_mcp:
            logger.info("🧹 Test Flow MCP測試完成")

async def main():
    """主函數"""
    print("🚀 開始使用Enhanced Test Flow MCP v4測試VSCode擴展系統")
    print("=" * 80)
    
    test_runner = VSCodeExtensionTestScenarios()
    
    try:
        # 初始化Test Flow MCP
        await test_runner.initialize_test_flow_mcp()
        
        # 運行所有測試場景
        overall_report = await test_runner.run_all_test_scenarios()
        
        # 保存測試報告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"vscode_extension_test_flow_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(overall_report, f, indent=2, ensure_ascii=False, default=str)
        
        # 輸出結果
        print("\n" + "=" * 80)
        print("📊 VSCode擴展系統Test Flow MCP測試報告")
        print("=" * 80)
        print(f"📈 總體結果: {'✅ 成功' if overall_report['summary']['overall_success'] else '❌ 部分失敗'}")
        print(f"📋 測試場景: {overall_report['successful_scenarios']}/{overall_report['total_scenarios']} 成功")
        print(f"📊 成功率: {overall_report['success_rate']:.2%}")
        print(f"🎯 平均信心度: {overall_report['summary']['average_confidence']:.2f}")
        print(f"⏱️  總執行時間: {overall_report['summary']['total_execution_time']:.2f}秒")
        print(f"📄 詳細報告: {report_file}")
        
        # 顯示各場景結果
        print("\n📋 各測試場景結果:")
        for result in overall_report['test_results']:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['scenario_name']}: {result.get('confidence_score', 0):.2f} ({result.get('execution_time', 0):.2f}s)")
            if not result['success'] and result.get('error_message'):
                print(f"   錯誤: {result['error_message']}")
        
        print("=" * 80)
        
        return 0 if overall_report['summary']['overall_success'] else 1
        
    except Exception as e:
        print(f"❌ 測試執行失敗: {e}")
        return 1
    
    finally:
        # 清理資源
        await test_runner.cleanup()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

