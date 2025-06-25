#!/usr/bin/env python3
"""
Deep Testing Framework for AICore Human-in-the-Loop Integration

這個框架設計用於對AICore系統進行全面的深度測試，包括功能測試、性能測試、
集成測試和端到端測試。
"""

import asyncio
import json
import logging
import time
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Set, Tuple
from datetime import datetime, timedelta
import uuid
import aiohttp
import yaml
import pytest
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import psutil
import threading
import subprocess
import sys
import os

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestType(Enum):
    """測試類型枚舉"""
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    STRESS = "stress"
    END_TO_END = "end_to_end"
    SECURITY = "security"
    COMPATIBILITY = "compatibility"

class TestStatus(Enum):
    """測試狀態枚舉"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

class TestPriority(Enum):
    """測試優先級枚舉"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class TestMetrics:
    """測試指標"""
    execution_time: float = 0.0
    memory_usage: float = 0.0  # MB
    cpu_usage: float = 0.0  # %
    network_requests: int = 0
    database_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    error_count: int = 0
    success_rate: float = 0.0
    throughput: float = 0.0  # requests/second
    latency_p50: float = 0.0  # ms
    latency_p95: float = 0.0  # ms
    latency_p99: float = 0.0  # ms

@dataclass
class TestResult:
    """測試結果"""
    test_id: str
    test_name: str
    test_type: TestType
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    message: str = ""
    error_details: Optional[str] = None
    metrics: TestMetrics = field(default_factory=TestMetrics)
    assertions: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)  # 測試產物路徑
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestSuite:
    """測試套件"""
    suite_id: str
    name: str
    description: str
    test_cases: List[str] = field(default_factory=list)
    setup_hooks: List[Callable] = field(default_factory=list)
    teardown_hooks: List[Callable] = field(default_factory=list)
    parallel: bool = False
    timeout: int = 3600  # 秒
    retry_count: int = 0
    tags: List[str] = field(default_factory=list)

class TestCase(ABC):
    """測試用例抽象基類"""
    
    def __init__(self, test_id: str, name: str, test_type: TestType, priority: TestPriority = TestPriority.MEDIUM):
        self.test_id = test_id
        self.name = name
        self.test_type = test_type
        self.priority = priority
        self.timeout = 300  # 默認5分鐘超時
        self.retry_count = 0
        self.tags = []
        self.dependencies = []
        self.setup_data = {}
        self.cleanup_data = {}
    
    @abstractmethod
    async def setup(self) -> bool:
        """測試前置設置"""
        pass
    
    @abstractmethod
    async def execute(self) -> TestResult:
        """執行測試"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> bool:
        """測試後清理"""
        pass
    
    async def run(self) -> TestResult:
        """運行測試用例"""
        start_time = datetime.now()
        result = TestResult(
            test_id=self.test_id,
            test_name=self.name,
            test_type=self.test_type,
            status=TestStatus.PENDING,
            start_time=start_time
        )
        
        try:
            # 前置設置
            if not await self.setup():
                result.status = TestStatus.ERROR
                result.message = "Setup failed"
                return result
            
            # 執行測試
            result = await self.execute()
            result.start_time = start_time
            
        except asyncio.TimeoutError:
            result.status = TestStatus.ERROR
            result.message = "Test timeout"
        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = f"Test execution failed: {str(e)}"
            result.error_details = traceback.format_exc()
        finally:
            # 清理
            try:
                await self.cleanup()
            except Exception as e:
                logger.warning(f"Cleanup failed for test {self.test_id}: {e}")
            
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()
        
        return result

class DynamicRoutingTestCase(TestCase):
    """動態路由測試用例"""
    
    def __init__(self):
        super().__init__(
            test_id="dynamic_routing_001",
            name="Dynamic Routing Functionality Test",
            test_type=TestType.INTEGRATION,
            priority=TestPriority.HIGH
        )
        self.router = None
    
    async def setup(self) -> bool:
        """設置測試環境"""
        try:
            from aicore_dynamic_router import AICoreDynamicRouter, RoutingContext
            self.router = AICoreDynamicRouter()
            return True
        except Exception as e:
            logger.error(f"Failed to setup dynamic router: {e}")
            return False
    
    async def execute(self) -> TestResult:
        """執行動態路由測試"""
        result = TestResult(
            test_id=self.test_id,
            test_name=self.name,
            test_type=self.test_type,
            status=TestStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            from aicore_dynamic_router import RoutingContext, DecisionType
            
            # 測試場景1: 低複雜度操作
            context1 = RoutingContext(
                request_id=str(uuid.uuid4()),
                workflow_id="test-workflow-1",
                operation_type="routine_maintenance",
                metadata={"complexity": "low"}
            )
            
            decision1 = await self.router.route_request(context1)
            
            # 驗證決策
            assert decision1.decision_type == DecisionType.AUTOMATIC, "Low complexity should route to automatic"
            result.assertions.append({
                "name": "low_complexity_routing",
                "expected": "automatic",
                "actual": decision1.decision_type.value,
                "passed": decision1.decision_type == DecisionType.AUTOMATIC
            })
            
            # 測試場景2: 高風險操作
            context2 = RoutingContext(
                request_id=str(uuid.uuid4()),
                workflow_id="test-workflow-2",
                operation_type="deployment",
                metadata={
                    "production_environment": True,
                    "critical_system": True,
                    "database_changes": True
                }
            )
            
            decision2 = await self.router.route_request(context2)
            
            # 驗證決策
            assert decision2.decision_type == DecisionType.HUMAN_REQUIRED, "High risk should require human intervention"
            result.assertions.append({
                "name": "high_risk_routing",
                "expected": "human_required",
                "actual": decision2.decision_type.value,
                "passed": decision2.decision_type == DecisionType.HUMAN_REQUIRED
            })
            
            # 測試場景3: 中等複雜度操作
            context3 = RoutingContext(
                request_id=str(uuid.uuid4()),
                workflow_id="test-workflow-3",
                operation_type="configuration_change",
                metadata={"complexity": "medium"}
            )
            
            decision3 = await self.router.route_request(context3)
            
            # 驗證決策
            result.assertions.append({
                "name": "medium_complexity_routing",
                "expected": "conditional_or_human",
                "actual": decision3.decision_type.value,
                "passed": decision3.decision_type in [DecisionType.CONDITIONAL, DecisionType.HUMAN_REQUIRED]
            })
            
            # 計算成功率
            passed_assertions = sum(1 for a in result.assertions if a["passed"])
            result.metrics.success_rate = passed_assertions / len(result.assertions)
            
            if result.metrics.success_rate == 1.0:
                result.status = TestStatus.PASSED
                result.message = "All routing scenarios passed"
            else:
                result.status = TestStatus.FAILED
                result.message = f"Some routing scenarios failed. Success rate: {result.metrics.success_rate:.2%}"
            
        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = f"Test execution error: {str(e)}"
            result.error_details = traceback.format_exc()
        
        return result
    
    async def cleanup(self) -> bool:
        """清理測試環境"""
        self.router = None
        return True

class ExpertInvocationTestCase(TestCase):
    """專家調用測試用例"""
    
    def __init__(self):
        super().__init__(
            test_id="expert_invocation_001",
            name="Expert Invocation System Test",
            test_type=TestType.INTEGRATION,
            priority=TestPriority.HIGH
        )
        self.expert_system = None
    
    async def setup(self) -> bool:
        """設置測試環境"""
        try:
            from expert_invocation_system import ExpertInvocationSystem
            self.expert_system = ExpertInvocationSystem()
            return True
        except Exception as e:
            logger.error(f"Failed to setup expert system: {e}")
            return False
    
    async def execute(self) -> TestResult:
        """執行專家調用測試"""
        result = TestResult(
            test_id=self.test_id,
            test_name=self.name,
            test_type=self.test_type,
            status=TestStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            from expert_invocation_system import ConsultationRequest, ExpertType, ExpertLevel
            
            # 測試場景1: AI專家諮詢
            request1 = ConsultationRequest(
                request_id=str(uuid.uuid4()),
                workflow_id="test-workflow-expert-1",
                expert_type=ExpertType.TECHNICAL,
                required_level=ExpertLevel.SENIOR,
                title="技術架構諮詢",
                description="需要技術架構建議",
                context={"system": "microservices"},
                timeout=60  # 短超時用於測試
            )
            
            consultation_id1 = await self.expert_system.request_consultation(request1)
            assert consultation_id1 == request1.request_id, "Consultation ID should match request ID"
            
            result.assertions.append({
                "name": "ai_expert_consultation_request",
                "expected": request1.request_id,
                "actual": consultation_id1,
                "passed": consultation_id1 == request1.request_id
            })
            
            # 等待處理完成
            await asyncio.sleep(2)
            
            # 檢查諮詢狀態
            status1 = await self.expert_system.get_consultation_status(consultation_id1)
            assert status1 is not None, "Consultation status should be available"
            
            result.assertions.append({
                "name": "consultation_status_available",
                "expected": "not_none",
                "actual": "available" if status1 else "none",
                "passed": status1 is not None
            })
            
            # 測試場景2: 專家統計信息
            stats = await self.expert_system.get_expert_statistics()
            assert "total_experts" in stats, "Statistics should include total experts"
            assert stats["total_experts"] > 0, "Should have registered experts"
            
            result.assertions.append({
                "name": "expert_statistics",
                "expected": "> 0",
                "actual": stats["total_experts"],
                "passed": stats["total_experts"] > 0
            })
            
            # 計算成功率
            passed_assertions = sum(1 for a in result.assertions if a["passed"])
            result.metrics.success_rate = passed_assertions / len(result.assertions)
            
            if result.metrics.success_rate == 1.0:
                result.status = TestStatus.PASSED
                result.message = "All expert invocation scenarios passed"
            else:
                result.status = TestStatus.FAILED
                result.message = f"Some expert invocation scenarios failed. Success rate: {result.metrics.success_rate:.2%}"
            
        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = f"Test execution error: {str(e)}"
            result.error_details = traceback.format_exc()
        
        return result
    
    async def cleanup(self) -> bool:
        """清理測試環境"""
        self.expert_system = None
        return True

class HumanLoopMCPTestCase(TestCase):
    """Human Loop MCP測試用例"""
    
    def __init__(self):
        super().__init__(
            test_id="human_loop_mcp_001",
            name="Human Loop MCP Integration Test",
            test_type=TestType.INTEGRATION,
            priority=TestPriority.CRITICAL
        )
        self.mcp_client = None
        self.test_sessions = []
    
    async def setup(self) -> bool:
        """設置測試環境"""
        try:
            from aicore_dynamic_router import HumanLoopMCPClient
            self.mcp_client = HumanLoopMCPClient("http://localhost:8096")
            return True
        except Exception as e:
            logger.error(f"Failed to setup Human Loop MCP client: {e}")
            return False
    
    async def execute(self) -> TestResult:
        """執行Human Loop MCP測試"""
        result = TestResult(
            test_id=self.test_id,
            test_name=self.name,
            test_type=self.test_type,
            status=TestStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # 測試場景1: 健康檢查
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:8096/api/health", timeout=aiohttp.ClientTimeout(total=10)) as response:
                        health_check_passed = response.status == 200
            except:
                health_check_passed = False
            
            result.assertions.append({
                "name": "health_check",
                "expected": "200",
                "actual": "200" if health_check_passed else "failed",
                "passed": health_check_passed
            })
            
            if health_check_passed:
                # 測試場景2: 創建會話
                session_data = {
                    "interaction_data": {
                        "interaction_type": "confirmation",
                        "title": "測試確認",
                        "message": "這是一個測試會話",
                        "timeout": 60
                    },
                    "workflow_id": "test-workflow-mcp",
                    "callback_url": "http://localhost:8080/test/callback"
                }
                
                try:
                    session_id = await self.mcp_client.create_session(session_data)
                    self.test_sessions.append(session_id)
                    session_created = True
                except:
                    session_created = False
                
                result.assertions.append({
                    "name": "session_creation",
                    "expected": "success",
                    "actual": "success" if session_created else "failed",
                    "passed": session_created
                })
                
                if session_created:
                    # 測試場景3: 獲取會話狀態
                    try:
                        session_status = await self.mcp_client.get_session_status(session_id)
                        status_retrieved = session_status is not None
                    except:
                        status_retrieved = False
                    
                    result.assertions.append({
                        "name": "session_status_retrieval",
                        "expected": "success",
                        "actual": "success" if status_retrieved else "failed",
                        "passed": status_retrieved
                    })
                    
                    # 測試場景4: 取消會話
                    try:
                        cancel_success = await self.mcp_client.cancel_session(session_id, "Test cleanup")
                    except:
                        cancel_success = False
                    
                    result.assertions.append({
                        "name": "session_cancellation",
                        "expected": "success",
                        "actual": "success" if cancel_success else "failed",
                        "passed": cancel_success
                    })
            
            # 計算成功率
            passed_assertions = sum(1 for a in result.assertions if a["passed"])
            result.metrics.success_rate = passed_assertions / len(result.assertions) if result.assertions else 0.0
            
            if result.metrics.success_rate >= 0.75:  # 75%通過率視為成功
                result.status = TestStatus.PASSED
                result.message = f"Human Loop MCP integration test passed. Success rate: {result.metrics.success_rate:.2%}"
            else:
                result.status = TestStatus.FAILED
                result.message = f"Human Loop MCP integration test failed. Success rate: {result.metrics.success_rate:.2%}"
            
        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = f"Test execution error: {str(e)}"
            result.error_details = traceback.format_exc()
        
        return result
    
    async def cleanup(self) -> bool:
        """清理測試環境"""
        # 清理測試會話
        for session_id in self.test_sessions:
            try:
                await self.mcp_client.cancel_session(session_id, "Test cleanup")
            except:
                pass
        
        self.test_sessions.clear()
        
        if self.mcp_client and hasattr(self.mcp_client, 'session') and self.mcp_client.session:
            await self.mcp_client.session.close()
        
        return True

class PerformanceTestCase(TestCase):
    """性能測試用例"""
    
    def __init__(self):
        super().__init__(
            test_id="performance_001",
            name="System Performance Test",
            test_type=TestType.PERFORMANCE,
            priority=TestPriority.HIGH
        )
        self.router = None
        self.expert_system = None
    
    async def setup(self) -> bool:
        """設置測試環境"""
        try:
            from aicore_dynamic_router import AICoreDynamicRouter
            from expert_invocation_system import ExpertInvocationSystem
            
            self.router = AICoreDynamicRouter()
            self.expert_system = ExpertInvocationSystem()
            return True
        except Exception as e:
            logger.error(f"Failed to setup performance test: {e}")
            return False
    
    async def execute(self) -> TestResult:
        """執行性能測試"""
        result = TestResult(
            test_id=self.test_id,
            test_name=self.name,
            test_type=self.test_type,
            status=TestStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            from aicore_dynamic_router import RoutingContext
            
            # 性能測試參數
            num_requests = 100
            concurrent_requests = 10
            
            # 測試路由性能
            routing_times = []
            
            async def test_routing():
                context = RoutingContext(
                    request_id=str(uuid.uuid4()),
                    workflow_id="perf-test",
                    operation_type="deployment",
                    metadata={"test": True}
                )
                
                start = time.time()
                await self.router.route_request(context)
                end = time.time()
                
                return end - start
            
            # 並發路由測試
            tasks = [test_routing() for _ in range(num_requests)]
            routing_times = await asyncio.gather(*tasks)
            
            # 計算性能指標
            result.metrics.latency_p50 = statistics.median(routing_times) * 1000  # ms
            result.metrics.latency_p95 = statistics.quantiles(routing_times, n=20)[18] * 1000  # ms
            result.metrics.latency_p99 = statistics.quantiles(routing_times, n=100)[98] * 1000  # ms
            result.metrics.throughput = num_requests / sum(routing_times)
            
            # 性能斷言
            avg_latency = statistics.mean(routing_times) * 1000
            
            result.assertions.append({
                "name": "average_latency",
                "expected": "< 100ms",
                "actual": f"{avg_latency:.2f}ms",
                "passed": avg_latency < 100
            })
            
            result.assertions.append({
                "name": "p95_latency",
                "expected": "< 200ms",
                "actual": f"{result.metrics.latency_p95:.2f}ms",
                "passed": result.metrics.latency_p95 < 200
            })
            
            result.assertions.append({
                "name": "throughput",
                "expected": "> 50 req/s",
                "actual": f"{result.metrics.throughput:.2f} req/s",
                "passed": result.metrics.throughput > 50
            })
            
            # 記憶體使用測試
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            result.metrics.memory_usage = memory_usage
            
            result.assertions.append({
                "name": "memory_usage",
                "expected": "< 500MB",
                "actual": f"{memory_usage:.2f}MB",
                "passed": memory_usage < 500
            })
            
            # 計算成功率
            passed_assertions = sum(1 for a in result.assertions if a["passed"])
            result.metrics.success_rate = passed_assertions / len(result.assertions)
            
            if result.metrics.success_rate >= 0.8:
                result.status = TestStatus.PASSED
                result.message = f"Performance test passed. Success rate: {result.metrics.success_rate:.2%}"
            else:
                result.status = TestStatus.FAILED
                result.message = f"Performance test failed. Success rate: {result.metrics.success_rate:.2%}"
            
        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = f"Test execution error: {str(e)}"
            result.error_details = traceback.format_exc()
        
        return result
    
    async def cleanup(self) -> bool:
        """清理測試環境"""
        self.router = None
        self.expert_system = None
        return True

class DeepTestingFramework:
    """深度測試框架"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.test_cases: Dict[str, TestCase] = {}
        self.test_suites: Dict[str, TestSuite] = {}
        self.test_results: List[TestResult] = []
        self.config = self._load_config(config_path)
        self.executor = ThreadPoolExecutor(max_workers=self.config.get("max_workers", 4))
        self._register_default_tests()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加載配置"""
        default_config = {
            "max_workers": 4,
            "default_timeout": 300,
            "retry_count": 1,
            "parallel_execution": True,
            "report_format": "json",
            "artifacts_dir": "./test_artifacts",
            "log_level": "INFO"
        }
        
        if config_path:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def _register_default_tests(self):
        """註冊默認測試用例"""
        # 註冊核心測試用例
        self.register_test_case(DynamicRoutingTestCase())
        self.register_test_case(ExpertInvocationTestCase())
        self.register_test_case(HumanLoopMCPTestCase())
        self.register_test_case(PerformanceTestCase())
        
        # 創建測試套件
        integration_suite = TestSuite(
            suite_id="integration_suite",
            name="Integration Test Suite",
            description="Tests for system integration",
            test_cases=["dynamic_routing_001", "expert_invocation_001", "human_loop_mcp_001"],
            parallel=True
        )
        
        performance_suite = TestSuite(
            suite_id="performance_suite",
            name="Performance Test Suite",
            description="Tests for system performance",
            test_cases=["performance_001"],
            parallel=False
        )
        
        self.register_test_suite(integration_suite)
        self.register_test_suite(performance_suite)
    
    def register_test_case(self, test_case: TestCase):
        """註冊測試用例"""
        self.test_cases[test_case.test_id] = test_case
        logger.info(f"Registered test case: {test_case.name}")
    
    def register_test_suite(self, test_suite: TestSuite):
        """註冊測試套件"""
        self.test_suites[test_suite.suite_id] = test_suite
        logger.info(f"Registered test suite: {test_suite.name}")
    
    async def run_test_case(self, test_id: str) -> TestResult:
        """運行單個測試用例"""
        if test_id not in self.test_cases:
            raise ValueError(f"Test case {test_id} not found")
        
        test_case = self.test_cases[test_id]
        logger.info(f"Running test case: {test_case.name}")
        
        result = await test_case.run()
        self.test_results.append(result)
        
        logger.info(f"Test case {test_case.name} completed with status: {result.status.value}")
        return result
    
    async def run_test_suite(self, suite_id: str) -> List[TestResult]:
        """運行測試套件"""
        if suite_id not in self.test_suites:
            raise ValueError(f"Test suite {suite_id} not found")
        
        suite = self.test_suites[suite_id]
        logger.info(f"Running test suite: {suite.name}")
        
        # 執行前置鉤子
        for hook in suite.setup_hooks:
            try:
                await hook()
            except Exception as e:
                logger.error(f"Setup hook failed: {e}")
        
        results = []
        
        try:
            if suite.parallel:
                # 並行執行
                tasks = [self.run_test_case(test_id) for test_id in suite.test_cases]
                results = await asyncio.gather(*tasks, return_exceptions=True)
            else:
                # 順序執行
                for test_id in suite.test_cases:
                    result = await self.run_test_case(test_id)
                    results.append(result)
        
        finally:
            # 執行後置鉤子
            for hook in suite.teardown_hooks:
                try:
                    await hook()
                except Exception as e:
                    logger.error(f"Teardown hook failed: {e}")
        
        logger.info(f"Test suite {suite.name} completed")
        return results
    
    async def run_all_tests(self) -> Dict[str, List[TestResult]]:
        """運行所有測試"""
        logger.info("Running all test suites")
        
        all_results = {}
        
        for suite_id in self.test_suites:
            try:
                results = await self.run_test_suite(suite_id)
                all_results[suite_id] = results
            except Exception as e:
                logger.error(f"Failed to run test suite {suite_id}: {e}")
                all_results[suite_id] = []
        
        return all_results
    
    def generate_report(self, format_type: str = "json") -> str:
        """生成測試報告"""
        if not self.test_results:
            return "No test results available"
        
        # 計算統計信息
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.status == TestStatus.PASSED)
        failed_tests = sum(1 for r in self.test_results if r.status == TestStatus.FAILED)
        error_tests = sum(1 for r in self.test_results if r.status == TestStatus.ERROR)
        
        total_duration = sum(r.duration for r in self.test_results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        report_data = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "success_rate": success_rate,
                "total_duration": total_duration,
                "average_duration": avg_duration,
                "generated_at": datetime.now().isoformat()
            },
            "test_results": [asdict(result) for result in self.test_results],
            "performance_metrics": self._aggregate_performance_metrics()
        }
        
        if format_type == "json":
            return json.dumps(report_data, indent=2, default=str)
        elif format_type == "html":
            return self._generate_html_report(report_data)
        else:
            return str(report_data)
    
    def _aggregate_performance_metrics(self) -> Dict[str, Any]:
        """聚合性能指標"""
        performance_results = [r for r in self.test_results if r.test_type == TestType.PERFORMANCE]
        
        if not performance_results:
            return {}
        
        metrics = {
            "average_latency_p50": statistics.mean([r.metrics.latency_p50 for r in performance_results]),
            "average_latency_p95": statistics.mean([r.metrics.latency_p95 for r in performance_results]),
            "average_latency_p99": statistics.mean([r.metrics.latency_p99 for r in performance_results]),
            "average_throughput": statistics.mean([r.metrics.throughput for r in performance_results]),
            "average_memory_usage": statistics.mean([r.metrics.memory_usage for r in performance_results])
        }
        
        return metrics
    
    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """生成HTML報告"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AICore Deep Testing Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .summary { background: #f5f5f5; padding: 15px; border-radius: 5px; }
                .test-result { margin: 10px 0; padding: 10px; border: 1px solid #ddd; }
                .passed { background: #d4edda; }
                .failed { background: #f8d7da; }
                .error { background: #fff3cd; }
                table { width: 100%; border-collapse: collapse; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>AICore Deep Testing Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Tests: {total_tests}</p>
                <p>Passed: {passed}</p>
                <p>Failed: {failed}</p>
                <p>Errors: {errors}</p>
                <p>Success Rate: {success_rate:.2%}</p>
                <p>Total Duration: {total_duration:.2f}s</p>
            </div>
            <h2>Test Results</h2>
            {test_results_html}
        </body>
        </html>
        """.format(
            total_tests=report_data["summary"]["total_tests"],
            passed=report_data["summary"]["passed"],
            failed=report_data["summary"]["failed"],
            errors=report_data["summary"]["errors"],
            success_rate=report_data["summary"]["success_rate"],
            total_duration=report_data["summary"]["total_duration"],
            test_results_html=self._format_test_results_html(report_data["test_results"])
        )
        
        return html_template
    
    def _format_test_results_html(self, test_results: List[Dict[str, Any]]) -> str:
        """格式化測試結果為HTML"""
        html = ""
        for result in test_results:
            status_class = result["status"].lower()
            html += f"""
            <div class="test-result {status_class}">
                <h3>{result["test_name"]}</h3>
                <p>Status: {result["status"]}</p>
                <p>Duration: {result["duration"]:.2f}s</p>
                <p>Message: {result["message"]}</p>
            </div>
            """
        return html
    
    async def cleanup(self):
        """清理資源"""
        self.executor.shutdown(wait=True)

# 使用示例
async def main():
    """主函數示例"""
    # 創建測試框架
    framework = DeepTestingFramework()
    
    try:
        # 運行所有測試
        logger.info("Starting deep testing framework...")
        results = await framework.run_all_tests()
        
        # 生成報告
        report = framework.generate_report("json")
        
        # 保存報告
        with open("test_report.json", "w", encoding="utf-8") as f:
            f.write(report)
        
        logger.info("Testing completed. Report saved to test_report.json")
        
        # 打印摘要
        total_tests = len(framework.test_results)
        passed_tests = sum(1 for r in framework.test_results if r.status == TestStatus.PASSED)
        
        print(f"\n=== Test Summary ===")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Success Rate: {passed_tests/total_tests:.2%}" if total_tests > 0 else "No tests run")
        
    finally:
        await framework.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

