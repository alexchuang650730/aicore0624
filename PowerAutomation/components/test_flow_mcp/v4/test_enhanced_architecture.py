#!/usr/bin/env python3
"""
增強架構測試腳本
測試數據庫分離、增強對比引擎和上下文管理器
"""

import asyncio
import json
import logging
import os
import sys
import time
import unittest
from datetime import datetime
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "PowerAutomation" / "components" / "mcp" / "shared"))
sys.path.insert(0, str(project_root / "PowerAutomation" / "components" / "mcp" / "workflow" / "test_flow" / "v4"))

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestEnhancedArchitecture(unittest.TestCase):
    """增強架構測試類"""
    
    def setUp(self):
        """測試設置"""
        self.test_user_id = "test_user_123"
        self.test_request_id = "test_req_456"
        self.test_data_dir = project_root / "data" / "test"
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Test setup completed")
    
    def tearDown(self):
        """測試清理"""
        # 清理測試數據
        if self.test_data_dir.exists():
            import shutil
            shutil.rmtree(self.test_data_dir, ignore_errors=True)
        
        logger.info("Test cleanup completed")
    
    def test_plugin_data_access(self):
        """測試插件數據訪問層"""
        logger.info("Testing Plugin Data Access Layer...")
        
        try:
            from plugin_data_access import PluginDataAccess, CodeProject, CodeFile, SyncSession
            
            # 創建測試數據庫
            test_db_path = self.test_data_dir / "test_plugin.db"
            plugin_access = PluginDataAccess(str(test_db_path))
            
            # 測試數據庫初始化
            self.assertTrue(test_db_path.exists(), "Plugin database should be created")
            
            # 測試代碼同步數據保存
            test_code_sync_data = {
                "project_metadata": {
                    "name": "Test Project",
                    "language": "Python",
                    "version": "1.0.0",
                    "git_info": {
                        "branch": "main",
                        "commit_hash": "abc123",
                        "remote_url": "https://github.com/test/repo.git"
                    }
                },
                "project_root": "/test/project",
                "sync_type": "incremental",
                "files": [
                    {
                        "path": "main.py",
                        "content": "print('Hello, World!')",
                        "status": "added",
                        "last_modified": time.time()
                    },
                    {
                        "path": "utils.py",
                        "content": "def helper_function():\n    pass",
                        "status": "modified",
                        "last_modified": time.time()
                    }
                ]
            }
            
            # 異步測試
            async def test_async_operations():
                # 保存代碼同步數據
                sync_session_id = await plugin_access.save_code_sync_data(
                    self.test_user_id, test_code_sync_data
                )
                self.assertIsNotNone(sync_session_id, "Sync session ID should be returned")
                
                # 獲取用戶代碼快照
                code_snapshot = await plugin_access.get_user_code_snapshot(self.test_user_id)
                self.assertIsNotNone(code_snapshot, "Code snapshot should be available")
                self.assertEqual(code_snapshot.file_count, 2, "Should have 2 files")
                
                # 搜索代碼文件
                search_results = await plugin_access.search_code_files(self.test_user_id, "Hello")
                self.assertGreater(len(search_results), 0, "Should find matching files")
                
                # 獲取用戶項目
                projects = await plugin_access.get_user_projects(self.test_user_id)
                self.assertGreater(len(projects), 0, "Should have at least one project")
                
                return True
            
            result = asyncio.run(test_async_operations())
            self.assertTrue(result, "Async operations should complete successfully")
            
            logger.info("✅ Plugin Data Access Layer test passed")
            
        except Exception as e:
            logger.error(f"❌ Plugin Data Access Layer test failed: {e}")
            self.fail(f"Plugin Data Access test failed: {e}")
    
    def test_data_provider(self):
        """測試數據提供者"""
        logger.info("Testing Data Provider...")
        
        try:
            from data_provider import DataProvider, UserContext, ComparisonContext
            from plugin_data_access import PluginDataAccess
            
            # 創建測試數據庫
            test_db_path = self.test_data_dir / "test_provider.db"
            plugin_access = PluginDataAccess(str(test_db_path))
            data_provider = DataProvider(plugin_data_access=plugin_access)
            
            # 異步測試
            async def test_async_operations():
                # 獲取用戶完整上下文
                user_context = await data_provider.get_user_full_context(self.test_user_id)
                self.assertIsNotNone(user_context, "User context should be available")
                self.assertEqual(user_context.user_id, self.test_user_id, "User ID should match")
                
                # 獲取對比數據
                comparison_context = await data_provider.get_comparison_data(
                    self.test_user_id, self.test_request_id
                )
                self.assertIsNotNone(comparison_context, "Comparison context should be available")
                self.assertEqual(comparison_context.user_context.user_id, self.test_user_id, "User ID should match")
                
                # 搜索用戶上下文
                search_results = await data_provider.search_user_context(
                    self.test_user_id, "test query", "all"
                )
                self.assertIsNotNone(search_results, "Search results should be available")
                self.assertIn("results", search_results, "Search results should contain results key")
                
                # 獲取上下文統計
                stats = await data_provider.get_context_statistics(self.test_user_id)
                self.assertIsNotNone(stats, "Context statistics should be available")
                self.assertEqual(stats["user_id"], self.test_user_id, "User ID should match")
                
                return True
            
            result = asyncio.run(test_async_operations())
            self.assertTrue(result, "Async operations should complete successfully")
            
            logger.info("✅ Data Provider test passed")
            
        except Exception as e:
            logger.error(f"❌ Data Provider test failed: {e}")
            self.fail(f"Data Provider test failed: {e}")
    
    def test_enhanced_comparison_engine(self):
        """測試增強對比引擎"""
        logger.info("Testing Enhanced Comparison Engine...")
        
        try:
            from enhanced_comparison_engine import (
                EnhancedComparisonAnalysisEngine, ComparisonRequest, 
                ComparisonType, AnalysisDepth
            )
            from data_provider import DataProvider
            from plugin_data_access import PluginDataAccess
            
            # 創建測試數據庫
            test_db_path = self.test_data_dir / "test_comparison.db"
            plugin_access = PluginDataAccess(str(test_db_path))
            data_provider = DataProvider(plugin_data_access=plugin_access)
            
            # 創建對比引擎
            comparison_engine = EnhancedComparisonAnalysisEngine(data_provider)
            
            # 異步測試
            async def test_async_operations():
                # 測試不同類型的對比分析
                comparison_types = [
                    ComparisonType.CONVERSATION_ANALYSIS,
                    ComparisonType.CODE_QUALITY,
                    ComparisonType.PERFORMANCE_BENCHMARK,
                    ComparisonType.BEST_PRACTICES,
                    ComparisonType.COMPREHENSIVE
                ]
                
                for comp_type in comparison_types:
                    request = ComparisonRequest(
                        user_id=self.test_user_id,
                        request_id=f"{self.test_request_id}_{comp_type.value}",
                        comparison_type=comp_type,
                        analysis_depth=AnalysisDepth.MEDIUM
                    )
                    
                    result = await comparison_engine.analyze_comparison(request)
                    
                    self.assertIsNotNone(result, f"Comparison result should be available for {comp_type.value}")
                    self.assertEqual(result.user_id, self.test_user_id, "User ID should match")
                    self.assertEqual(result.comparison_type, comp_type, "Comparison type should match")
                    self.assertGreaterEqual(result.overall_score, 0.0, "Overall score should be non-negative")
                    self.assertLessEqual(result.overall_score, 1.0, "Overall score should not exceed 1.0")
                    self.assertGreaterEqual(result.confidence_score, 0.0, "Confidence score should be non-negative")
                    self.assertLessEqual(result.confidence_score, 1.0, "Confidence score should not exceed 1.0")
                    
                    logger.info(f"✅ {comp_type.value} analysis completed: "
                              f"score={result.overall_score:.2f}, confidence={result.confidence_score:.2f}")
                
                return True
            
            result = asyncio.run(test_async_operations())
            self.assertTrue(result, "Async operations should complete successfully")
            
            logger.info("✅ Enhanced Comparison Engine test passed")
            
        except Exception as e:
            logger.error(f"❌ Enhanced Comparison Engine test failed: {e}")
            self.fail(f"Enhanced Comparison Engine test failed: {e}")
    
    def test_enhanced_context_manager(self):
        """測試增強上下文管理器"""
        logger.info("Testing Enhanced Context Manager...")
        
        try:
            from context_manager_enhanced import (
                EnhancedContextManager, ContextRequest, ContextType, ContextPriority
            )
            from data_provider import DataProvider
            from plugin_data_access import PluginDataAccess
            
            # 創建測試數據庫
            test_db_path = self.test_data_dir / "test_context.db"
            plugin_access = PluginDataAccess(str(test_db_path))
            data_provider = DataProvider(plugin_data_access=plugin_access)
            
            # 創建上下文管理器
            context_manager = EnhancedContextManager(data_provider)
            
            # 異步測試
            async def test_async_operations():
                # 測試不同類型的上下文請求
                context_types = [
                    ContextType.CONVERSATION,
                    ContextType.CODE,
                    ContextType.MIXED,
                    ContextType.COMPREHENSIVE
                ]
                
                for context_type in context_types:
                    request = ContextRequest(
                        user_id=self.test_user_id,
                        request_id=f"{self.test_request_id}_{context_type.value}",
                        context_type=context_type,
                        priority=ContextPriority.MEDIUM,
                        max_context_length=4000
                    )
                    
                    optimized_context = await context_manager.get_optimized_context(request)
                    
                    self.assertIsNotNone(optimized_context, f"Optimized context should be available for {context_type.value}")
                    self.assertEqual(optimized_context.user_id, self.test_user_id, "User ID should match")
                    self.assertLessEqual(optimized_context.total_tokens, 4000, "Total tokens should not exceed limit")
                    self.assertIsNotNone(optimized_context.context_summary, "Context summary should be available")
                    
                    logger.info(f"✅ {context_type.value} context optimization completed: "
                              f"segments={optimized_context.total_segments}, "
                              f"tokens={optimized_context.total_tokens}, "
                              f"strategy={optimized_context.optimization_strategy}")
                
                # 測試上下文統計
                stats = await context_manager.get_context_statistics(self.test_user_id)
                self.assertIsNotNone(stats, "Context statistics should be available")
                self.assertEqual(stats["user_id"], self.test_user_id, "User ID should match")
                
                # 測試為特定請求優化上下文
                optimized = await context_manager.optimize_context_for_request(
                    self.test_user_id, "請幫我分析這段代碼的性能問題", 2000
                )
                self.assertIsNotNone(optimized, "Request-specific optimization should work")
                self.assertLessEqual(optimized.total_tokens, 2000, "Should respect token limit")
                
                return True
            
            result = asyncio.run(test_async_operations())
            self.assertTrue(result, "Async operations should complete successfully")
            
            logger.info("✅ Enhanced Context Manager test passed")
            
        except Exception as e:
            logger.error(f"❌ Enhanced Context Manager test failed: {e}")
            self.fail(f"Enhanced Context Manager test failed: {e}")
    
    def test_integration(self):
        """測試整體集成"""
        logger.info("Testing Integration...")
        
        try:
            from plugin_data_access import PluginDataAccess
            from data_provider import DataProvider
            from enhanced_comparison_engine import (
                EnhancedComparisonAnalysisEngine, ComparisonRequest, ComparisonType
            )
            from context_manager_enhanced import (
                EnhancedContextManager, ContextRequest, ContextType
            )
            
            # 創建測試數據庫
            test_db_path = self.test_data_dir / "test_integration.db"
            plugin_access = PluginDataAccess(str(test_db_path))
            data_provider = DataProvider(plugin_data_access=plugin_access)
            comparison_engine = EnhancedComparisonAnalysisEngine(data_provider)
            context_manager = EnhancedContextManager(data_provider)
            
            # 異步測試
            async def test_async_operations():
                # 1. 保存測試代碼數據
                test_code_sync_data = {
                    "project_metadata": {
                        "name": "Integration Test Project",
                        "language": "Python",
                        "version": "1.0.0"
                    },
                    "project_root": "/test/integration",
                    "files": [
                        {
                            "path": "app.py",
                            "content": "def main():\n    print('Integration test')\n\nif __name__ == '__main__':\n    main()",
                            "status": "added",
                            "last_modified": time.time()
                        }
                    ]
                }
                
                sync_session_id = await plugin_access.save_code_sync_data(
                    self.test_user_id, test_code_sync_data
                )
                self.assertIsNotNone(sync_session_id, "Should save code sync data")
                
                # 2. 獲取優化上下文
                context_request = ContextRequest(
                    user_id=self.test_user_id,
                    request_id=self.test_request_id,
                    context_type=ContextType.COMPREHENSIVE
                )
                
                optimized_context = await context_manager.get_optimized_context(context_request)
                self.assertIsNotNone(optimized_context, "Should get optimized context")
                
                # 3. 執行對比分析
                comparison_request = ComparisonRequest(
                    user_id=self.test_user_id,
                    request_id=self.test_request_id,
                    comparison_type=ComparisonType.COMPREHENSIVE
                )
                
                comparison_result = await comparison_engine.analyze_comparison(comparison_request)
                self.assertIsNotNone(comparison_result, "Should get comparison result")
                
                # 4. 驗證數據一致性
                self.assertEqual(optimized_context.user_id, comparison_result.user_id, "User IDs should match")
                
                logger.info(f"✅ Integration test completed successfully:")
                logger.info(f"   - Context segments: {optimized_context.total_segments}")
                logger.info(f"   - Context tokens: {optimized_context.total_tokens}")
                logger.info(f"   - Comparison score: {comparison_result.overall_score:.2f}")
                logger.info(f"   - Confidence: {comparison_result.confidence_score:.2f}")
                
                return True
            
            result = asyncio.run(test_async_operations())
            self.assertTrue(result, "Integration test should complete successfully")
            
            logger.info("✅ Integration test passed")
            
        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")
            self.fail(f"Integration test failed: {e}")

def run_performance_test():
    """運行性能測試"""
    logger.info("Running performance tests...")
    
    try:
        from plugin_data_access import PluginDataAccess
        from data_provider import DataProvider
        from enhanced_comparison_engine import EnhancedComparisonAnalysisEngine, ComparisonRequest, ComparisonType
        
        # 創建大量測試數據
        test_data_dir = Path(__file__).parent.parent / "data" / "perf_test"
        test_data_dir.mkdir(parents=True, exist_ok=True)
        
        test_db_path = test_data_dir / "perf_test.db"
        plugin_access = PluginDataAccess(str(test_db_path))
        data_provider = DataProvider(plugin_data_access=plugin_access)
        comparison_engine = EnhancedComparisonAnalysisEngine(data_provider)
        
        async def performance_test():
            # 創建大量代碼文件
            large_code_sync_data = {
                "project_metadata": {
                    "name": "Performance Test Project",
                    "language": "Python",
                    "version": "1.0.0"
                },
                "project_root": "/test/performance",
                "files": []
            }
            
            # 生成100個文件
            for i in range(100):
                large_code_sync_data["files"].append({
                    "path": f"module_{i}.py",
                    "content": f"# Module {i}\n" + "def function_{}():\n    pass\n" * 10,
                    "status": "added",
                    "last_modified": time.time()
                })
            
            # 測試保存性能
            start_time = time.time()
            sync_session_id = await plugin_access.save_code_sync_data("perf_user", large_code_sync_data)
            save_time = time.time() - start_time
            
            # 測試查詢性能
            start_time = time.time()
            code_snapshot = await plugin_access.get_user_code_snapshot("perf_user")
            query_time = time.time() - start_time
            
            # 測試對比分析性能
            start_time = time.time()
            comparison_request = ComparisonRequest(
                user_id="perf_user",
                request_id="perf_req",
                comparison_type=ComparisonType.COMPREHENSIVE
            )
            comparison_result = await comparison_engine.analyze_comparison(comparison_request)
            analysis_time = time.time() - start_time
            
            logger.info(f"Performance test results:")
            logger.info(f"  - Save 100 files: {save_time:.2f}s")
            logger.info(f"  - Query snapshot: {query_time:.2f}s")
            logger.info(f"  - Comparison analysis: {analysis_time:.2f}s")
            logger.info(f"  - Total files processed: {code_snapshot.file_count if code_snapshot else 0}")
            
            # 清理
            import shutil
            shutil.rmtree(test_data_dir, ignore_errors=True)
            
            return True
        
        result = asyncio.run(performance_test())
        logger.info("✅ Performance test completed")
        return result
        
    except Exception as e:
        logger.error(f"❌ Performance test failed: {e}")
        return False

def main():
    """主測試函數"""
    logger.info("🚀 Starting Enhanced Architecture Tests")
    
    # 運行單元測試
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestEnhancedArchitecture)
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(test_suite)
    
    # 運行性能測試
    perf_result = run_performance_test()
    
    # 總結結果
    if test_result.wasSuccessful() and perf_result:
        logger.info("✅ All tests passed successfully!")
        return 0
    else:
        logger.error("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())

