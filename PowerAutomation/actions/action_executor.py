# -*- coding: utf-8 -*-
"""
Action Executor - 統一執行引擎 (Updated for AICore 2.0)
Action Executor - Unified Execution Engine (Updated for AICore 2.0)

統一的任務執行引擎，支持並行執行、流程編排和結果聚合
支持新的MCP組件和工具命名體系
"""

import asyncio
import json
import logging
import time
import aiohttp
import subprocess
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import importlib

logger = logging.getLogger(__name__)

class ExecutionStatus(Enum):
    """執行狀態枚舉"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class ExecutionMode(Enum):
    """執行模式枚舉"""
    SEQUENTIAL = "sequential"  # 順序執行
    PARALLEL = "parallel"      # 並行執行
    PIPELINE = "pipeline"      # 管道執行

@dataclass
class ExecutionTask:
    """執行任務"""
    id: str
    tool_id: str
    action: str
    parameters: Dict[str, Any]
    timeout: int = 30
    retry_count: int = 0
    max_retries: int = 2
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class ExecutionResult:
    """執行結果"""
    task_id: str
    tool_id: str
    status: ExecutionStatus
    result: Any = None
    error: str = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = str(time.time())

class ActionExecutor:
    """
    統一執行引擎
    
    職責:
    1. 並行執行多個工具
    2. 流程編排和依賴管理
    3. 結果聚合和處理
    4. 錯誤處理和重試
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.tool_registry = None  # 將在初始化時注入
        self.active_executions: Dict[str, ExecutionTask] = {}
        self.execution_history: List[ExecutionResult] = []
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.get('max_workers', 10))
        self.max_concurrent_tasks = self.config.get('max_concurrent_tasks', 20)
        
        logger.info("ActionExecutor initialized")
    
    def set_tool_registry(self, tool_registry):
        """設置工具註冊系統"""
        self.tool_registry = tool_registry
        logger.info("Tool registry injected into ActionExecutor")
    
    async def execute(self, request, tools: List[str], mode: ExecutionMode = ExecutionMode.PARALLEL) -> Dict[str, Any]:
        """
        執行任務的主入口
        
        Args:
            request: Agent請求對象
            tools: 要使用的工具列表
            mode: 執行模式
        
        Returns:
            執行結果字典
        """
        execution_id = f"exec_{request.id}_{int(time.time())}"
        logger.info(f"Starting execution {execution_id} with tools: {tools}")
        
        start_time = time.time()
        
        try:
            # 創建執行任務
            tasks = await self._create_execution_tasks(execution_id, request, tools)
            
            # 根據模式執行任務
            if mode == ExecutionMode.SEQUENTIAL:
                results = await self._execute_sequential(tasks)
            elif mode == ExecutionMode.PARALLEL:
                results = await self._execute_parallel(tasks)
            elif mode == ExecutionMode.PIPELINE:
                results = await self._execute_pipeline(tasks)
            else:
                raise ValueError(f"Unsupported execution mode: {mode}")
            
            # 聚合結果
            aggregated_result = await self._aggregate_results(request, results)
            
            execution_time = time.time() - start_time
            
            return {
                'result': aggregated_result,
                'execution_time': execution_time,
                'tools_used': tools,
                'task_results': results,
                'confidence': self._calculate_confidence(results),
                'details': {
                    'execution_id': execution_id,
                    'mode': mode.value,
                    'task_count': len(tasks)
                }
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Execution {execution_id} failed: {e}")
            
            return {
                'result': None,
                'execution_time': execution_time,
                'tools_used': tools,
                'error': str(e),
                'confidence': 0.0,
                'details': {
                    'execution_id': execution_id,
                    'mode': mode.value,
                    'failed': True
                }
            }
    
    async def _create_execution_tasks(self, execution_id: str, request, tools: List[str]) -> List[ExecutionTask]:
        """創建執行任務"""
        tasks = []
        
        for i, tool_id in enumerate(tools):
            task = ExecutionTask(
                id=f"{execution_id}_task_{i}",
                tool_id=tool_id,
                action="process",
                parameters={
                    'request_content': request.content,
                    'request_type': request.type,
                    'context': request.context,
                    'metadata': request.metadata
                },
                timeout=request.timeout // len(tools) if len(tools) > 1 else request.timeout
            )
            tasks.append(task)
        
        return tasks
    
    async def _execute_sequential(self, tasks: List[ExecutionTask]) -> List[ExecutionResult]:
        """順序執行任務"""
        logger.info(f"Executing {len(tasks)} tasks sequentially")
        results = []
        
        for task in tasks:
            result = await self._execute_single_task(task)
            results.append(result)
            
            # 如果任務失敗且是關鍵任務，停止執行
            if result.status == ExecutionStatus.FAILED:
                logger.warning(f"Task {task.id} failed, continuing with next task")
        
        return results
    
    async def _execute_parallel(self, tasks: List[ExecutionTask]) -> List[ExecutionResult]:
        """並行執行任務"""
        logger.info(f"Executing {len(tasks)} tasks in parallel")
        
        # 限制並發數量
        semaphore = asyncio.Semaphore(min(self.max_concurrent_tasks, len(tasks)))
        
        async def execute_with_semaphore(task):
            async with semaphore:
                return await self._execute_single_task(task)
        
        # 並行執行所有任務
        results = await asyncio.gather(
            *[execute_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )
        
        # 處理異常結果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = ExecutionResult(
                    task_id=tasks[i].id,
                    tool_id=tasks[i].tool_id,
                    status=ExecutionStatus.FAILED,
                    error=str(result)
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_pipeline(self, tasks: List[ExecutionTask]) -> List[ExecutionResult]:
        """管道執行任務（前一個任務的輸出作為下一個任務的輸入）"""
        logger.info(f"Executing {len(tasks)} tasks in pipeline mode")
        results = []
        pipeline_data = None
        
        for task in tasks:
            # 將前一個任務的結果作為當前任務的輸入
            if pipeline_data is not None:
                task.parameters['pipeline_input'] = pipeline_data
            
            result = await self._execute_single_task(task)
            results.append(result)
            
            # 如果任務成功，將結果傳遞給下一個任務
            if result.status == ExecutionStatus.COMPLETED:
                pipeline_data = result.result
            else:
                logger.warning(f"Pipeline task {task.id} failed, breaking pipeline")
                break
        
        return results
    
    async def _execute_single_task(self, task: ExecutionTask) -> ExecutionResult:
        """執行單個任務"""
        logger.info(f"Executing task {task.id} with tool {task.tool_id}")
        
        start_time = time.time()
        self.active_executions[task.id] = task
        
        try:
            # 獲取工具信息
            tool_info = await self.tool_registry.get_tool_info(task.tool_id) if self.tool_registry else None
            
            if not tool_info:
                raise ValueError(f"Tool {task.tool_id} not found in registry")
            
            # 根據工具類型執行
            if tool_info.type.value == "mcp_service":
                result = await self._execute_mcp_tool(tool_info, task)
            elif tool_info.type.value == "http_api":
                result = await self._execute_http_tool(tool_info, task)
            elif tool_info.type.value == "python_module":
                result = await self._execute_python_tool(tool_info, task)
            elif tool_info.type.value == "shell_command":
                result = await self._execute_shell_tool(tool_info, task)
            else:
                result = await self._execute_default_tool(tool_info, task)
            
            execution_time = time.time() - start_time
            
            execution_result = ExecutionResult(
                task_id=task.id,
                tool_id=task.tool_id,
                status=ExecutionStatus.COMPLETED,
                result=result,
                execution_time=execution_time,
                metadata={'tool_type': tool_info.type.value}
            )
            
            logger.info(f"Task {task.id} completed successfully in {execution_time:.2f}s")
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            execution_result = ExecutionResult(
                task_id=task.id,
                tool_id=task.tool_id,
                status=ExecutionStatus.TIMEOUT,
                error="Task execution timeout",
                execution_time=execution_time
            )
            logger.warning(f"Task {task.id} timed out after {execution_time:.2f}s")
            
        except Exception as e:
            execution_time = time.time() - start_time
            execution_result = ExecutionResult(
                task_id=task.id,
                tool_id=task.tool_id,
                status=ExecutionStatus.FAILED,
                error=str(e),
                execution_time=execution_time
            )
            logger.error(f"Task {task.id} failed: {e}")
        
        finally:
            # 清理活動執行
            if task.id in self.active_executions:
                del self.active_executions[task.id]
            
            # 記錄到歷史
            self.execution_history.append(execution_result)
        
        return execution_result
    
    async def _execute_mcp_tool(self, tool_info, task: ExecutionTask) -> Any:
        """執行MCP工具"""
        logger.info(f"Executing MCP tool: {tool_info.name}")
        
        # 構建MCP請求
        mcp_request = {
            'action': task.action,
            'parameters': task.parameters
        }
        
        # 發送HTTP請求到MCP服務
        async with aiohttp.ClientSession() as session:
            url = f"{tool_info.endpoint}/process"
            async with session.post(url, json=mcp_request, timeout=task.timeout) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    raise Exception(f"MCP tool returned status {response.status}")
    
    async def _execute_http_tool(self, tool_info, task: ExecutionTask) -> Any:
        """執行HTTP API工具"""
        logger.info(f"Executing HTTP API tool: {tool_info.name}")
        
        # 構建API請求
        api_request = {
            'data': task.parameters
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"{tool_info.endpoint}/api/process"
            async with session.post(url, json=api_request, timeout=task.timeout) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    raise Exception(f"HTTP API returned status {response.status}")
    
    async def _execute_python_tool(self, tool_info, task: ExecutionTask) -> Any:
        """執行Python模塊工具"""
        logger.info(f"Executing Python tool: {tool_info.name}")
        
        # 模擬Python工具執行
        if tool_info.name == "system_monitor":
            return await self._execute_system_monitor(task.parameters)
        elif tool_info.name == "file_processor":
            return await self._execute_file_processor(task.parameters)
        else:
            return await self._execute_default_python_tool(task.parameters)
    
    async def _execute_shell_tool(self, tool_info, task: ExecutionTask) -> Any:
        """執行Shell命令工具"""
        logger.info(f"Executing shell tool: {tool_info.name}")
        
        # 在線程池中執行shell命令
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.thread_pool,
            self._run_shell_command,
            tool_info.command,
            task.parameters
        )
        return result
    
    def _run_shell_command(self, command: str, parameters: Dict[str, Any]) -> str:
        """運行shell命令"""
        try:
            # 替換命令中的參數
            formatted_command = command.format(**parameters)
            result = subprocess.run(
                formatted_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                raise Exception(f"Shell command failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("Shell command timeout")
    
    async def _execute_default_tool(self, tool_info, task: ExecutionTask) -> Any:
        """執行默認工具"""
        logger.info(f"Executing default tool: {tool_info.name}")
        
        # 默認處理邏輯
        content = task.parameters.get('request_content', '')
        request_type = task.parameters.get('request_type', 'general')
        
        return {
            'processed_content': f"Processed by {tool_info.name}: {content}",
            'tool_type': tool_info.type.value,
            'request_type': request_type,
            'processing_time': time.time()
        }
    
    async def _execute_system_monitor(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行系統監控"""
        try:
            import psutil
            
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'timestamp': time.time()
            }
        except ImportError:
            return {
                'error': 'psutil not available',
                'mock_data': {
                    'cpu_percent': 45.2,
                    'memory_percent': 67.8,
                    'disk_percent': 23.1
                }
            }
    
    async def _execute_file_processor(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行文件處理"""
        content = parameters.get('request_content', '')
        
        return {
            'file_analysis': f"Analyzed content: {len(content)} characters",
            'content_type': 'text',
            'processing_result': 'File processed successfully',
            'timestamp': time.time()
        }
    
    async def _execute_default_python_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行默認Python工具"""
        return {
            'result': 'Default Python tool execution',
            'parameters': parameters,
            'timestamp': time.time()
        }
    
    async def _aggregate_results(self, request, results: List[ExecutionResult]) -> Any:
        """聚合執行結果"""
        logger.info(f"Aggregating {len(results)} execution results")
        
        successful_results = [r for r in results if r.status == ExecutionStatus.COMPLETED]
        failed_results = [r for r in results if r.status == ExecutionStatus.FAILED]
        
        if not successful_results:
            return {
                'error': 'All tools failed to execute',
                'failed_count': len(failed_results),
                'details': [{'tool': r.tool_id, 'error': r.error} for r in failed_results]
            }
        
        # 智能結果聚合
        if len(successful_results) == 1:
            # 單個結果直接返回
            return successful_results[0].result
        else:
            # 多個結果需要聚合
            return self._merge_multiple_results(request, successful_results)
    
    def _merge_multiple_results(self, request, results: List[ExecutionResult]) -> Dict[str, Any]:
        """合併多個執行結果"""
        merged_result = {
            'summary': f"Processed by {len(results)} tools",
            'request_type': request.type,
            'tool_results': {}
        }
        
        for result in results:
            merged_result['tool_results'][result.tool_id] = result.result
        
        # 如果是監控請求，聚合監控數據
        if 'monitor' in request.type.lower():
            merged_result['monitoring_data'] = self._aggregate_monitoring_data(results)
        
        # 如果是分析請求，聚合分析結果
        if 'analysis' in request.type.lower():
            merged_result['analysis_summary'] = self._aggregate_analysis_data(results)
        
        return merged_result
    
    def _aggregate_monitoring_data(self, results: List[ExecutionResult]) -> Dict[str, Any]:
        """聚合監控數據"""
        monitoring_data = {}
        
        for result in results:
            if isinstance(result.result, dict):
                for key, value in result.result.items():
                    if isinstance(value, (int, float)):
                        if key not in monitoring_data:
                            monitoring_data[key] = []
                        monitoring_data[key].append(value)
        
        # 計算平均值
        aggregated = {}
        for key, values in monitoring_data.items():
            aggregated[f"avg_{key}"] = sum(values) / len(values)
            aggregated[f"max_{key}"] = max(values)
            aggregated[f"min_{key}"] = min(values)
        
        return aggregated
    
    def _aggregate_analysis_data(self, results: List[ExecutionResult]) -> Dict[str, Any]:
        """聚合分析數據"""
        analysis_summary = {
            'total_analyses': len(results),
            'successful_analyses': len(results),
            'combined_insights': []
        }
        
        for result in results:
            if isinstance(result.result, dict):
                insight = result.result.get('analysis', result.result.get('result', ''))
                if insight:
                    analysis_summary['combined_insights'].append({
                        'tool': result.tool_id,
                        'insight': insight
                    })
        
        return analysis_summary
    
    def _calculate_confidence(self, results: List[ExecutionResult]) -> float:
        """計算整體置信度"""
        if not results:
            return 0.0
        
        successful_count = len([r for r in results if r.status == ExecutionStatus.COMPLETED])
        total_count = len(results)
        
        base_confidence = successful_count / total_count
        
        # 根據執行時間調整置信度
        avg_execution_time = sum(r.execution_time for r in results) / len(results)
        if avg_execution_time < 5.0:  # 快速執行加分
            base_confidence += 0.1
        elif avg_execution_time > 30.0:  # 執行過慢減分
            base_confidence -= 0.1
        
        return max(0.0, min(1.0, base_confidence))
    
    def get_executor_stats(self) -> Dict[str, Any]:
        """獲取執行器統計信息"""
        total_executions = len(self.execution_history)
        successful_executions = len([r for r in self.execution_history if r.status == ExecutionStatus.COMPLETED])
        
        return {
            'active_tasks': len(self.active_executions),
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'success_rate': successful_executions / total_executions if total_executions > 0 else 0.0,
            'average_execution_time': sum(r.execution_time for r in self.execution_history) / total_executions if total_executions > 0 else 0.0
        }

# 工廠函數
def create_action_executor(config: Dict[str, Any] = None) -> ActionExecutor:
    """創建Action Executor實例"""
    return ActionExecutor(config)

# 示例使用
async def example_usage():
    """示例用法"""
    from core.agent_core import AgentRequest, Priority
    
    # 創建Action Executor
    executor = create_action_executor({
        'max_workers': 5,
        'max_concurrent_tasks': 10
    })
    
    # 模擬請求
    request = AgentRequest(
        id="test_001",
        type="monitoring",
        content="檢查系統狀態",
        priority=Priority.HIGH
    )
    
    # 執行任務
    result = await executor.execute(request, ['system_monitor', 'file_processor'])
    
    print(f"Execution result: {result}")
    print(f"Executor stats: {executor.get_executor_stats()}")

if __name__ == "__main__":
    asyncio.run(example_usage())

