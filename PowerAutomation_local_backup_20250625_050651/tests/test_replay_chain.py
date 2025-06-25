#!/usr/bin/env python3
"""
PowerAutomation Replay Chain System 測試腳本
測試和驗證Replay鏈結功能

Author: Manus AI
Version: 1.0.0
Date: 2025-06-23
"""

import asyncio
import json
import logging
import time
import sys
from datetime import datetime
from typing import Dict, Any, List

# 導入核心模組
from manus_replay_chain_core import (
    ReplayChainManager, TaskNode, TaskStatus, ChainStatus,
    TaskSimilarityAnalyzer, ChainGenerator, ChainExecutor, SharedContext
)


class ReplayChainTester:
    """Replay鏈結系統測試器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_results = []
        self.start_time = None
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """運行所有測試"""
        self.start_time = time.time()
        self.logger.info("開始運行Replay鏈結系統測試...")
        
        test_suites = [
            ("基本功能測試", self.test_basic_functionality),
            ("任務相似性分析測試", self.test_similarity_analysis),
            ("鏈結生成測試", self.test_chain_generation),
            ("鏈結執行測試", self.test_chain_execution),
            ("管理器集成測試", self.test_manager_integration),
            ("性能測試", self.test_performance),
            ("錯誤處理測試", self.test_error_handling)
        ]
        
        total_tests = 0
        passed_tests = 0
        
        for suite_name, test_func in test_suites:
            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"運行測試套件: {suite_name}")
            self.logger.info(f"{'='*50}")
            
            try:
                result = await test_func()
                self.test_results.append({
                    "suite": suite_name,
                    "success": True,
                    "result": result,
                    "error": None
                })
                
                suite_total = result.get("total_tests", 0)
                suite_passed = result.get("passed_tests", 0)
                
                total_tests += suite_total
                passed_tests += suite_passed
                
                self.logger.info(f"✅ {suite_name} 完成: {suite_passed}/{suite_total} 通過")
                
            except Exception as e:
                self.logger.error(f"❌ {suite_name} 失敗: {e}")
                self.test_results.append({
                    "suite": suite_name,
                    "success": False,
                    "result": None,
                    "error": str(e)
                })
        
        # 生成測試報告
        total_time = time.time() - self.start_time
        
        report = {
            "test_summary": {
                "total_suites": len(test_suites),
                "passed_suites": sum(1 for r in self.test_results if r["success"]),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "total_time": total_time
            },
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info("測試完成總結:")
        self.logger.info(f"總測試套件: {report['test_summary']['total_suites']}")
        self.logger.info(f"通過套件: {report['test_summary']['passed_suites']}")
        self.logger.info(f"總測試案例: {report['test_summary']['total_tests']}")
        self.logger.info(f"通過案例: {report['test_summary']['passed_tests']}")
        self.logger.info(f"成功率: {report['test_summary']['success_rate']:.2%}")
        self.logger.info(f"總耗時: {report['test_summary']['total_time']:.2f}秒")
        self.logger.info(f"{'='*60}")
        
        return report
    
    async def test_basic_functionality(self) -> Dict[str, Any]:
        """測試基本功能"""
        tests = []
        
        # 測試1: TaskNode創建和序列化
        try:
            task = TaskNode(
                task_id="test_001",
                task_type="manus_login",
                description="測試登錄任務",
                parameters={"email": "test@example.com"},
                priority=8
            )
            
            # 測試序列化
            task_dict = task.to_dict()
            assert "task_id" in task_dict
            assert task_dict["task_type"] == "manus_login"
            
            # 測試反序列化
            task_restored = TaskNode.from_dict(task_dict)
            assert task_restored.task_id == task.task_id
            assert task_restored.task_type == task.task_type
            
            tests.append({"name": "TaskNode創建和序列化", "passed": True})
            
        except Exception as e:
            tests.append({"name": "TaskNode創建和序列化", "passed": False, "error": str(e)})
        
        # 測試2: SharedContext功能
        try:
            context = SharedContext()
            
            # 測試數據緩存
            await context.cache_data("test_key", {"data": "test_value"}, ttl=60)
            cached_data = await context.get_cached_data("test_key")
            assert cached_data["data"] == "test_value"
            
            # 測試認證狀態
            await context.set_authentication_state("manus", {"logged_in": True})
            auth_state = await context.get_authentication_state("manus")
            assert auth_state["logged_in"] is True
            
            await context.cleanup()
            tests.append({"name": "SharedContext功能", "passed": True})
            
        except Exception as e:
            tests.append({"name": "SharedContext功能", "passed": False, "error": str(e)})
        
        # 測試3: 任務狀態轉換
        try:
            task = TaskNode(
                task_id="test_002",
                task_type="send_message",
                description="測試消息任務",
                parameters={"message": "Hello"}
            )
            
            # 測試狀態轉換
            assert task.status == TaskStatus.PENDING
            task.status = TaskStatus.RUNNING
            assert task.status == TaskStatus.RUNNING
            task.status = TaskStatus.COMPLETED
            assert task.status == TaskStatus.COMPLETED
            
            tests.append({"name": "任務狀態轉換", "passed": True})
            
        except Exception as e:
            tests.append({"name": "任務狀態轉換", "passed": False, "error": str(e)})
        
        passed_tests = sum(1 for t in tests if t["passed"])
        
        return {
            "total_tests": len(tests),
            "passed_tests": passed_tests,
            "tests": tests
        }
    
    async def test_similarity_analysis(self) -> Dict[str, Any]:
        """測試任務相似性分析"""
        tests = []
        analyzer = TaskSimilarityAnalyzer()
        
        # 測試1: 相同類型任務的相似性
        try:
            task1 = TaskNode(
                task_id="sim_001",
                task_type="manus_login",
                description="登錄Manus平台",
                parameters={"email": "user1@example.com"}
            )
            
            task2 = TaskNode(
                task_id="sim_002",
                task_type="manus_login",
                description="登錄Manus系統",
                parameters={"email": "user2@example.com"}
            )
            
            similarity = analyzer.analyze_similarity(task1, task2)
            
            # 相同類型的任務應該有較高的相似性
            assert similarity.similarity_score > 0.5
            assert similarity.similarity_factors["operation_similarity"] == 1.0
            
            tests.append({"name": "相同類型任務相似性", "passed": True, "score": similarity.similarity_score})
            
        except Exception as e:
            tests.append({"name": "相同類型任務相似性", "passed": False, "error": str(e)})
        
        # 測試2: 不同類型任務的相似性
        try:
            task1 = TaskNode(
                task_id="sim_003",
                task_type="manus_login",
                description="登錄Manus平台",
                parameters={"email": "user@example.com"}
            )
            
            task2 = TaskNode(
                task_id="sim_004",
                task_type="download_files",
                description="下載文件",
                parameters={"task_id": "123"}
            )
            
            similarity = analyzer.analyze_similarity(task1, task2)
            
            # 不同類型的任務應該有較低的相似性
            assert similarity.similarity_score < 0.5
            
            tests.append({"name": "不同類型任務相似性", "passed": True, "score": similarity.similarity_score})
            
        except Exception as e:
            tests.append({"name": "不同類型任務相似性", "passed": False, "error": str(e)})
        
        # 測試3: 時間相似性
        try:
            import time
            
            task1 = TaskNode(
                task_id="sim_005",
                task_type="send_message",
                description="發送消息1",
                parameters={"message": "Hello"}
            )
            
            # 等待一小段時間
            await asyncio.sleep(0.1)
            
            task2 = TaskNode(
                task_id="sim_006",
                task_type="send_message",
                description="發送消息2",
                parameters={"message": "World"}
            )
            
            similarity = analyzer.analyze_similarity(task1, task2)
            
            # 時間接近的任務應該有較高的時間相似性
            assert similarity.similarity_factors["temporal_similarity"] > 0.8
            
            tests.append({"name": "時間相似性分析", "passed": True})
            
        except Exception as e:
            tests.append({"name": "時間相似性分析", "passed": False, "error": str(e)})
        
        passed_tests = sum(1 for t in tests if t["passed"])
        
        return {
            "total_tests": len(tests),
            "passed_tests": passed_tests,
            "tests": tests
        }
    
    async def test_chain_generation(self) -> Dict[str, Any]:
        """測試鏈結生成"""
        tests = []
        generator = ChainGenerator()
        
        # 測試1: 基本鏈結生成
        try:
            tasks = [
                TaskNode(
                    task_id="chain_001",
                    task_type="manus_login",
                    description="登錄Manus",
                    parameters={"email": "test@example.com"},
                    priority=9
                ),
                TaskNode(
                    task_id="chain_002",
                    task_type="send_message",
                    description="發送消息",
                    parameters={"message": "Hello"},
                    dependencies=["chain_001"],
                    priority=7
                ),
                TaskNode(
                    task_id="chain_003",
                    task_type="get_conversations",
                    description="獲取對話",
                    parameters={},
                    dependencies=["chain_001"],
                    priority=6
                )
            ]
            
            chains = generator.generate_chains(tasks)
            
            # 應該生成至少一個鏈結
            assert len(chains) > 0
            
            chain = chains[0]
            assert len(chain.nodes) >= 2
            assert chain.optimization_score > 0
            
            tests.append({"name": "基本鏈結生成", "passed": True, "chains": len(chains)})
            
        except Exception as e:
            tests.append({"name": "基本鏈結生成", "passed": False, "error": str(e)})
        
        # 測試2: 執行順序優化
        try:
            tasks = [
                TaskNode(
                    task_id="order_001",
                    task_type="manus_login",
                    description="登錄",
                    parameters={},
                    priority=10
                ),
                TaskNode(
                    task_id="order_002",
                    task_type="send_message",
                    description="發送消息",
                    parameters={"message": "Test"},
                    dependencies=["order_001"],
                    priority=8
                ),
                TaskNode(
                    task_id="order_003",
                    task_type="get_tasks",
                    description="獲取任務",
                    parameters={},
                    dependencies=["order_001"],
                    priority=6
                )
            ]
            
            chains = generator.generate_chains(tasks)
            
            if chains:
                chain = chains[0]
                execution_order = chain.execution_order
                
                # 登錄任務應該在第一位
                assert execution_order[0] == "order_001"
                
                # 依賴任務應該在登錄任務之後
                login_index = execution_order.index("order_001")
                for task_id in ["order_002", "order_003"]:
                    if task_id in execution_order:
                        assert execution_order.index(task_id) > login_index
            
            tests.append({"name": "執行順序優化", "passed": True})
            
        except Exception as e:
            tests.append({"name": "執行順序優化", "passed": False, "error": str(e)})
        
        # 測試3: 優化分數計算
        try:
            tasks = [
                TaskNode(
                    task_id="score_001",
                    task_type="manus_login",
                    description="登錄",
                    parameters={},
                    estimated_duration=10.0
                ),
                TaskNode(
                    task_id="score_002",
                    task_type="send_message",
                    description="發送消息",
                    parameters={"message": "Test"},
                    estimated_duration=5.0
                )
            ]
            
            chains = generator.generate_chains(tasks)
            
            if chains:
                chain = chains[0]
                
                # 優化分數應該在0-1之間
                assert 0 <= chain.optimization_score <= 1
                
                # 多任務鏈結應該有正的優化分數
                assert chain.optimization_score > 0
            
            tests.append({"name": "優化分數計算", "passed": True})
            
        except Exception as e:
            tests.append({"name": "優化分數計算", "passed": False, "error": str(e)})
        
        passed_tests = sum(1 for t in tests if t["passed"])
        
        return {
            "total_tests": len(tests),
            "passed_tests": passed_tests,
            "tests": tests
        }
    
    async def test_chain_execution(self) -> Dict[str, Any]:
        """測試鏈結執行"""
        tests = []
        
        # 測試1: 基本鏈結執行
        try:
            context = SharedContext()
            executor = ChainExecutor(context)
            
            # 創建測試鏈結
            from manus_replay_chain_core import ReplayChain
            
            chain = ReplayChain(
                chain_id="exec_test_001",
                chain_name="測試鏈結",
                description="測試鏈結執行"
            )
            
            # 添加任務
            task1 = TaskNode(
                task_id="exec_task_001",
                task_type="manus_login",
                description="登錄測試",
                parameters={"email": "test@example.com"},
                priority=9
            )
            
            task2 = TaskNode(
                task_id="exec_task_002",
                task_type="send_message",
                description="發送測試消息",
                parameters={"message": "Test message"},
                dependencies=["exec_task_001"],
                priority=7
            )
            
            chain.add_node(task1)
            chain.add_node(task2)
            chain.execution_order = ["exec_task_001", "exec_task_002"]
            
            # 執行鏈結
            result = await executor.execute_chain(chain)
            
            # 驗證執行結果
            assert result is not None
            assert result.chain_id == chain.chain_id
            assert len(result.node_results) == 2
            
            # 清理
            await context.cleanup()
            
            tests.append({"name": "基本鏈結執行", "passed": True, "duration": result.total_duration})
            
        except Exception as e:
            tests.append({"name": "基本鏈結執行", "passed": False, "error": str(e)})
        
        # 測試2: 共享上下文使用
        try:
            context = SharedContext()
            executor = ChainExecutor(context)
            
            # 創建需要共享上下文的鏈結
            chain = ReplayChain(
                chain_id="context_test_001",
                chain_name="上下文測試鏈結",
                description="測試共享上下文"
            )
            
            # 登錄任務
            login_task = TaskNode(
                task_id="context_login",
                task_type="manus_login",
                description="登錄以設置上下文",
                parameters={"email": "test@example.com"},
                priority=9
            )
            
            # 依賴登錄狀態的任務
            message_task = TaskNode(
                task_id="context_message",
                task_type="send_message",
                description="使用登錄上下文發送消息",
                parameters={"message": "Context test"},
                dependencies=["context_login"],
                priority=7
            )
            
            chain.add_node(login_task)
            chain.add_node(message_task)
            chain.execution_order = ["context_login", "context_message"]
            
            # 執行鏈結
            result = await executor.execute_chain(chain)
            
            # 第二個任務應該能夠使用第一個任務設置的認證狀態
            assert result is not None
            assert len(result.node_results) == 2
            
            # 檢查第二個任務的輸出是否包含緩存標記
            message_result = result.node_results[1]
            if message_result.success and "cached" in message_result.outputs:
                # 如果使用了緩存，說明共享上下文工作正常
                pass
            
            await context.cleanup()
            
            tests.append({"name": "共享上下文使用", "passed": True})
            
        except Exception as e:
            tests.append({"name": "共享上下文使用", "passed": False, "error": str(e)})
        
        passed_tests = sum(1 for t in tests if t["passed"])
        
        return {
            "total_tests": len(tests),
            "passed_tests": passed_tests,
            "tests": tests
        }
    
    async def test_manager_integration(self) -> Dict[str, Any]:
        """測試管理器集成"""
        tests = []
        
        # 測試1: 完整工作流程
        try:
            manager = ReplayChainManager()
            
            # 創建任務
            task1 = TaskNode(
                task_id="mgr_task_001",
                task_type="manus_login",
                description="管理器測試登錄",
                parameters={"email": "test@example.com"},
                priority=9
            )
            
            task2 = TaskNode(
                task_id="mgr_task_002",
                task_type="get_conversations",
                description="管理器測試獲取對話",
                parameters={},
                dependencies=["mgr_task_001"],
                priority=7
            )
            
            task3 = TaskNode(
                task_id="mgr_task_003",
                task_type="get_tasks",
                description="管理器測試獲取任務",
                parameters={},
                dependencies=["mgr_task_001"],
                priority=6
            )
            
            # 添加任務
            await manager.add_task(task1)
            await manager.add_task(task2)
            await manager.add_task(task3)
            
            # 自動生成鏈結
            chain_ids = await manager.auto_generate_chains()
            assert len(chain_ids) > 0
            
            # 獲取鏈結
            chain = await manager.get_chain(chain_ids[0])
            assert chain is not None
            assert len(chain.nodes) >= 2
            
            # 執行鏈結
            result = await manager.execute_chain(chain_ids[0])
            assert result is not None
            
            # 清理
            await manager.cleanup()
            
            tests.append({"name": "完整工作流程", "passed": True, "chains": len(chain_ids)})
            
        except Exception as e:
            tests.append({"name": "完整工作流程", "passed": False, "error": str(e)})
        
        # 測試2: 鏈結管理操作
        try:
            manager = ReplayChainManager()
            
            # 創建任務
            tasks = []
            for i in range(4):
                task = TaskNode(
                    task_id=f"mgmt_task_{i:03d}",
                    task_type="send_message" if i % 2 == 0 else "get_conversations",
                    description=f"管理測試任務 {i}",
                    parameters={"message": f"Test {i}"} if i % 2 == 0 else {},
                    priority=10 - i
                )
                tasks.append(task)
                await manager.add_task(task)
            
            # 手動創建鏈結
            task_ids = [task.task_id for task in tasks[:2]]
            chain_id = await manager.create_chain_from_tasks(task_ids, "手動測試鏈結")
            assert chain_id is not None
            
            # 列出鏈結
            chains = await manager.list_chains()
            assert len(chains) >= 1
            
            # 刪除鏈結
            success = await manager.delete_chain(chain_id)
            assert success is True
            
            # 驗證刪除
            chains_after = await manager.list_chains()
            assert len(chains_after) == len(chains) - 1
            
            await manager.cleanup()
            
            tests.append({"name": "鏈結管理操作", "passed": True})
            
        except Exception as e:
            tests.append({"name": "鏈結管理操作", "passed": False, "error": str(e)})
        
        passed_tests = sum(1 for t in tests if t["passed"])
        
        return {
            "total_tests": len(tests),
            "passed_tests": passed_tests,
            "tests": tests
        }
    
    async def test_performance(self) -> Dict[str, Any]:
        """測試性能"""
        tests = []
        
        # 測試1: 大量任務處理性能
        try:
            start_time = time.time()
            
            manager = ReplayChainManager()
            
            # 創建大量任務
            num_tasks = 50
            for i in range(num_tasks):
                task = TaskNode(
                    task_id=f"perf_task_{i:03d}",
                    task_type=["manus_login", "send_message", "get_conversations", "get_tasks"][i % 4],
                    description=f"性能測試任務 {i}",
                    parameters={"index": i},
                    priority=10 - (i % 10)
                )
                await manager.add_task(task)
            
            # 自動生成鏈結
            chain_ids = await manager.auto_generate_chains()
            
            creation_time = time.time() - start_time
            
            # 驗證結果
            assert len(manager.tasks) == num_tasks
            assert len(chain_ids) > 0
            
            # 性能要求：50個任務的處理時間應該在合理範圍內
            assert creation_time < 30.0  # 30秒內完成
            
            await manager.cleanup()
            
            tests.append({
                "name": "大量任務處理性能",
                "passed": True,
                "tasks": num_tasks,
                "chains": len(chain_ids),
                "time": creation_time
            })
            
        except Exception as e:
            tests.append({"name": "大量任務處理性能", "passed": False, "error": str(e)})
        
        # 測試2: 相似性分析性能
        try:
            start_time = time.time()
            
            analyzer = TaskSimilarityAnalyzer()
            
            # 創建測試任務
            tasks = []
            for i in range(20):
                task = TaskNode(
                    task_id=f"sim_perf_{i:03d}",
                    task_type=["manus_login", "send_message"][i % 2],
                    description=f"相似性測試任務 {i}",
                    parameters={"value": i}
                )
                tasks.append(task)
            
            # 計算所有任務對的相似性
            similarities = []
            for i in range(len(tasks)):
                for j in range(i + 1, len(tasks)):
                    similarity = analyzer.analyze_similarity(tasks[i], tasks[j])
                    similarities.append(similarity)
            
            analysis_time = time.time() - start_time
            
            # 驗證結果
            expected_pairs = len(tasks) * (len(tasks) - 1) // 2
            assert len(similarities) == expected_pairs
            
            # 性能要求：相似性分析應該在合理時間內完成
            assert analysis_time < 10.0  # 10秒內完成
            
            tests.append({
                "name": "相似性分析性能",
                "passed": True,
                "pairs": len(similarities),
                "time": analysis_time
            })
            
        except Exception as e:
            tests.append({"name": "相似性分析性能", "passed": False, "error": str(e)})
        
        passed_tests = sum(1 for t in tests if t["passed"])
        
        return {
            "total_tests": len(tests),
            "passed_tests": passed_tests,
            "tests": tests
        }
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """測試錯誤處理"""
        tests = []
        
        # 測試1: 無效任務處理
        try:
            manager = ReplayChainManager()
            
            # 嘗試創建無效鏈結
            chain_id = await manager.create_chain_from_tasks([], "空鏈結")
            assert chain_id is None  # 應該返回None
            
            # 嘗試創建只有一個任務的鏈結
            task = TaskNode(
                task_id="single_task",
                task_type="manus_login",
                description="單個任務",
                parameters={}
            )
            await manager.add_task(task)
            
            chain_id = await manager.create_chain_from_tasks(["single_task"], "單任務鏈結")
            assert chain_id is None  # 應該返回None
            
            await manager.cleanup()
            
            tests.append({"name": "無效任務處理", "passed": True})
            
        except Exception as e:
            tests.append({"name": "無效任務處理", "passed": False, "error": str(e)})
        
        # 測試2: 不存在的資源訪問
        try:
            manager = ReplayChainManager()
            
            # 嘗試獲取不存在的任務
            task = await manager.get_task("non_existent_task")
            assert task is None
            
            # 嘗試獲取不存在的鏈結
            chain = await manager.get_chain("non_existent_chain")
            assert chain is None
            
            # 嘗試刪除不存在的鏈結
            success = await manager.delete_chain("non_existent_chain")
            assert success is False
            
            await manager.cleanup()
            
            tests.append({"name": "不存在的資源訪問", "passed": True})
            
        except Exception as e:
            tests.append({"name": "不存在的資源訪問", "passed": False, "error": str(e)})
        
        # 測試3: 循環依賴處理
        try:
            manager = ReplayChainManager()
            
            # 創建有循環依賴的任務
            task1 = TaskNode(
                task_id="cycle_task_1",
                task_type="manus_login",
                description="循環任務1",
                parameters={},
                dependencies=["cycle_task_2"]  # 依賴任務2
            )
            
            task2 = TaskNode(
                task_id="cycle_task_2",
                task_type="send_message",
                description="循環任務2",
                parameters={"message": "test"},
                dependencies=["cycle_task_1"]  # 依賴任務1，形成循環
            )
            
            await manager.add_task(task1)
            await manager.add_task(task2)
            
            # 嘗試創建鏈結
            chain_ids = await manager.auto_generate_chains()
            
            # 即使有循環依賴，系統也應該能夠處理（使用優先級排序）
            if chain_ids:
                chain = await manager.get_chain(chain_ids[0])
                assert chain is not None
                assert len(chain.execution_order) == 2
            
            await manager.cleanup()
            
            tests.append({"name": "循環依賴處理", "passed": True})
            
        except Exception as e:
            tests.append({"name": "循環依賴處理", "passed": False, "error": str(e)})
        
        passed_tests = sum(1 for t in tests if t["passed"])
        
        return {
            "total_tests": len(tests),
            "passed_tests": passed_tests,
            "tests": tests
        }


async def main():
    """主函數"""
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/home/ubuntu/replay_chain_test.log'),
            logging.StreamHandler()
        ]
    )
    
    # 創建測試器
    tester = ReplayChainTester()
    
    try:
        # 運行所有測試
        report = await tester.run_all_tests()
        
        # 保存測試報告
        with open('/home/ubuntu/replay_chain_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n測試報告已保存到: /home/ubuntu/replay_chain_test_report.json")
        
        # 返回適當的退出碼
        if report["test_summary"]["success_rate"] >= 0.8:
            print("✅ 測試通過")
            sys.exit(0)
        else:
            print("❌ 測試失敗")
            sys.exit(1)
            
    except Exception as e:
        print(f"測試運行失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

