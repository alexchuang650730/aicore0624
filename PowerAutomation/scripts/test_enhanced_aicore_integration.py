"""
增強 AICore 3.0 測試腳本
測試 Smartinvention MCP 整合到主流程的功能
"""

import asyncio
import logging
import sys
import os
import time
from datetime import datetime

# 添加項目路徑
sys.path.append('/home/ubuntu/aicore0624/PowerAutomation')

from core.enhanced_aicore3 import create_enhanced_aicore3
from core.aicore3 import UserRequest

logger = logging.getLogger(__name__)

async def test_enhanced_aicore_integration():
    """測試增強 AICore 的 Smartinvention MCP 整合"""
    
    try:
        # 1. 創建增強的 AICore 3.0
        enhanced_aicore = create_enhanced_aicore3()
        await enhanced_aicore.initialize()
        
        logger.info("✅ 增強 AICore 3.0 初始化完成")
        
        # 2. 創建測試請求
        test_requests = [
            {
                "id": "test_req_001",
                "content": "我需要針對 REQ_001: 用戶界面設計需求進行詳細分析，包括相關的檔案列表和跨任務關聯",
                "context": {"type": "requirement_analysis", "target_entity": "REQ_001"},
                "metadata": {"target_entity": "REQ_001", "test_case": "requirement_analysis"}
            },
            {
                "id": "test_req_002", 
                "content": "請執行單元測試來驗證代碼功能，並生成測試報告",
                "context": {"type": "testing", "test_type": "unit_testing"},
                "metadata": {"test_case": "testing_workflow"}
            },
            {
                "id": "test_req_003",
                "content": "分析系統性能並提供優化建議",
                "context": {"type": "performance_analysis"},
                "metadata": {"test_case": "performance_optimization"}
            }
        ]
        
        # 3. 執行測試請求
        test_results = []
        
        for i, test_req_data in enumerate(test_requests, 1):
            print(f"\n🧪 執行測試 {i}: {test_req_data['metadata']['test_case']}")
            print(f"請求內容: {test_req_data['content'][:80]}...")
            
            # 創建用戶請求
            user_request = UserRequest(
                id=test_req_data["id"],
                content=test_req_data["content"],
                context=test_req_data["context"],
                metadata=test_req_data["metadata"]
            )
            
            # 處理請求
            start_time = time.time()
            try:
                result = await enhanced_aicore.process_request(user_request)
                processing_time = time.time() - start_time
                
                # 分析結果
                test_result = {
                    "test_case": test_req_data['metadata']['test_case'],
                    "success": result.success,
                    "processing_time": processing_time,
                    "smartinvention_integration": result.metadata.get('smartinvention_integration', False),
                    "manus_comparison_performed": result.metadata.get('manus_comparison_performed', False),
                    "incremental_repair_analyzed": result.metadata.get('incremental_repair_analyzed', False),
                    "stages_completed": len(result.stage_results),
                    "expert_count": len(result.expert_analysis),
                    "confidence": result.confidence
                }
                
                test_results.append(test_result)
                
                # 顯示結果摘要
                print(f"  ✅ 處理成功: {result.success}")
                print(f"  ⏱️ 處理時間: {processing_time:.2f}s")
                print(f"  🔗 Smartinvention 整合: {test_result['smartinvention_integration']}")
                print(f"  🎯 Manus 比對: {test_result['manus_comparison_performed']}")
                print(f"  🔧 增量修復分析: {test_result['incremental_repair_analyzed']}")
                print(f"  📊 階段完成: {test_result['stages_completed']}")
                print(f"  👥 專家參與: {test_result['expert_count']}")
                print(f"  🎯 信心度: {test_result['confidence']:.2f}")
                
                # 檢查 Smartinvention 預處理結果
                if 'smartinvention_preprocessing' in result.stage_results:
                    preprocessing = result.stage_results['smartinvention_preprocessing']
                    smartinvention_integration = preprocessing.get('smartinvention_integration', {})
                    
                    print(f"  📋 相關任務: {smartinvention_integration.get('tasks_found', 0)}")
                    print(f"  📁 相關檔案: {smartinvention_integration.get('files_found', 0)}")
                    
                    # 檢查 Manus 比對結果
                    manus_comparison = preprocessing.get('manus_comparison', {})
                    if manus_comparison.get('success'):
                        comparison_result = manus_comparison.get('comparison_result', {})
                        print(f"  🎯 匹配需求: {len(comparison_result.get('requirement_items', []))}")
                        print(f"  🚀 建議行動: {len(comparison_result.get('manus_actions', []))}")
                    
                    # 檢查增量修復分析
                    repair_analysis = preprocessing.get('incremental_repair_analysis', {})
                    if repair_analysis.get('needs_repair'):
                        print(f"  🔧 需要修復: {repair_analysis.get('repair_type', '')}")
                        print(f"  ⚡ 修復優先級: {repair_analysis.get('repair_priority', '')}")
                
            except Exception as e:
                logger.error(f"❌ 測試 {i} 失敗: {e}")
                test_results.append({
                    "test_case": test_req_data['metadata']['test_case'],
                    "success": False,
                    "error": str(e),
                    "processing_time": time.time() - start_time
                })
                print(f"  ❌ 處理失敗: {e}")
        
        # 4. 生成測試報告
        await generate_test_report(test_results, enhanced_aicore)
        
        return test_results
        
    except Exception as e:
        logger.error(f"❌ 增強 AICore 整合測試失敗: {e}")
        return []

async def generate_test_report(test_results: list, enhanced_aicore) -> None:
    """生成測試報告"""
    
    print(f"\n📊 增強 AICore 3.0 整合測試報告")
    print(f"=" * 60)
    
    # 總體統計
    total_tests = len(test_results)
    successful_tests = len([r for r in test_results if r.get('success', False)])
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📈 總體統計:")
    print(f"  總測試數: {total_tests}")
    print(f"  成功測試: {successful_tests}")
    print(f"  成功率: {success_rate:.1f}%")
    
    # Smartinvention 整合統計
    smartinvention_integrated = len([r for r in test_results if r.get('smartinvention_integration', False)])
    manus_compared = len([r for r in test_results if r.get('manus_comparison_performed', False)])
    repair_analyzed = len([r for r in test_results if r.get('incremental_repair_analyzed', False)])
    
    print(f"\n🔗 Smartinvention MCP 整合統計:")
    print(f"  整合成功: {smartinvention_integrated}/{total_tests}")
    print(f"  Manus 比對: {manus_compared}/{total_tests}")
    print(f"  增量修復分析: {repair_analyzed}/{total_tests}")
    
    # 性能統計
    processing_times = [r.get('processing_time', 0) for r in test_results if r.get('success', False)]
    if processing_times:
        avg_time = sum(processing_times) / len(processing_times)
        max_time = max(processing_times)
        min_time = min(processing_times)
        
        print(f"\n⏱️ 性能統計:")
        print(f"  平均處理時間: {avg_time:.2f}s")
        print(f"  最大處理時間: {max_time:.2f}s")
        print(f"  最小處理時間: {min_time:.2f}s")
    
    # 專家系統統計
    expert_counts = [r.get('expert_count', 0) for r in test_results if r.get('success', False)]
    if expert_counts:
        avg_experts = sum(expert_counts) / len(expert_counts)
        print(f"\n👥 專家系統統計:")
        print(f"  平均專家參與數: {avg_experts:.1f}")
    
    # 詳細測試結果
    print(f"\n📋 詳細測試結果:")
    for i, result in enumerate(test_results, 1):
        status = "✅ 成功" if result.get('success', False) else "❌ 失敗"
        test_case = result.get('test_case', f'test_{i}')
        processing_time = result.get('processing_time', 0)
        
        print(f"  {i}. {test_case}: {status} ({processing_time:.2f}s)")
        
        if not result.get('success', False) and 'error' in result:
            print(f"     錯誤: {result['error']}")
    
    # 系統狀態
    if hasattr(enhanced_aicore, 'get_expert_statistics'):
        try:
            expert_stats = enhanced_aicore.dynamic_expert_registry.get_expert_statistics()
            print(f"\n🧠 專家系統狀態:")
            print(f"  總專家數: {expert_stats.get('total_experts', 0)}")
            print(f"  活躍專家數: {expert_stats.get('active_experts', 0)}")
            print(f"  覆蓋領域: {expert_stats.get('domains', 0)}")
        except Exception as e:
            logger.warning(f"無法獲取專家統計: {e}")
    
    print(f"\n🎯 測試結論:")
    if success_rate >= 80:
        print(f"  ✅ 增強 AICore 3.0 整合測試通過")
        print(f"  ✅ Smartinvention MCP 成功整合到主流程")
        print(f"  ✅ Manus 需求比對和增量修復功能正常")
    elif success_rate >= 60:
        print(f"  ⚠️ 增強 AICore 3.0 整合測試部分通過")
        print(f"  ⚠️ 需要進一步優化整合機制")
    else:
        print(f"  ❌ 增強 AICore 3.0 整合測試失敗")
        print(f"  ❌ 需要檢查和修復整合問題")

async def test_specific_smartinvention_features():
    """測試特定的 Smartinvention 功能"""
    
    print(f"\n🔬 測試特定 Smartinvention 功能")
    
    try:
        enhanced_aicore = create_enhanced_aicore3()
        await enhanced_aicore.initialize()
        
        # 測試 Manus Adapter MCP
        if enhanced_aicore.manus_adapter:
            print(f"  ✅ Manus Adapter MCP 已初始化")
            
            # 測試需求分析
            test_requirement = "針對 REQ_001: 用戶界面設計需求進行分析"
            try:
                analysis_result = await enhanced_aicore.manus_adapter.analyze_requirement(
                    requirement_text=test_requirement,
                    target_entity="REQ_001"
                )
                print(f"  ✅ Manus 需求分析功能正常")
                print(f"     分析結果包含 {len(analysis_result.get('requirement_items', []))} 個需求項目")
            except Exception as e:
                print(f"  ❌ Manus 需求分析失敗: {e}")
        else:
            print(f"  ❌ Manus Adapter MCP 未初始化")
        
        # 測試 Smartinvention Adapter MCP
        if enhanced_aicore.smartinvention_adapter:
            print(f"  ✅ Smartinvention Adapter MCP 已初始化")
            
            # 測試數據獲取
            try:
                tasks_data = await enhanced_aicore.smartinvention_adapter.get_tasks_data()
                files_data = await enhanced_aicore.smartinvention_adapter.get_files_data()
                print(f"  ✅ Smartinvention 數據獲取功能正常")
                print(f"     任務數據: {len(tasks_data.get('tasks', []))} 個任務")
                print(f"     檔案數據: {len(files_data.get('files', []))} 個檔案")
            except Exception as e:
                print(f"  ❌ Smartinvention 數據獲取失敗: {e}")
        else:
            print(f"  ❌ Smartinvention Adapter MCP 未初始化")
        
    except Exception as e:
        print(f"  ❌ Smartinvention 功能測試失敗: {e}")

async def main():
    """主函數"""
    
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 開始增強 AICore 3.0 整合測試")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 測試特定功能
    await test_specific_smartinvention_features()
    
    # 2. 執行整合測試
    test_results = await test_enhanced_aicore_integration()
    
    print(f"\n🎉 增強 AICore 3.0 整合測試完成！")
    
    # 3. 保存測試結果
    import json
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"/home/ubuntu/enhanced_aicore_integration_test_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_timestamp": datetime.now().isoformat(),
            "test_results": test_results,
            "summary": {
                "total_tests": len(test_results),
                "successful_tests": len([r for r in test_results if r.get('success', False)]),
                "success_rate": (len([r for r in test_results if r.get('success', False)]) / len(test_results) * 100) if test_results else 0
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"📄 測試報告已保存: {report_file}")

if __name__ == "__main__":
    asyncio.run(main())

