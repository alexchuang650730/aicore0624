#!/usr/bin/env python3
"""
AICore Human-in-the-Loop Integration System

這是一個完整的AICore系統，整合了動態路由、專家調用、深度測試和增量優化，
實現智能化的人機協作流程。
"""

import asyncio
import json
import logging
import time
import yaml
import aiohttp
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Set, Tuple
from datetime import datetime, timedelta
import uuid
import threading
import signal
import sys
import os
from pathlib import Path

# 導入自定義模組
try:
    from aicore_dynamic_router import AICoreDynamicRouter, RoutingContext, DecisionType
    from expert_invocation_system import ExpertInvocationSystem, ConsultationRequest, ExpertType
    from deep_testing_framework import DeepTestingFramework, TestType, TestStatus
    from incremental_optimization_system import IncrementalOptimizationSystem
except ImportError as e:
    logging.error(f"Failed to import required modules: {e}")
    sys.exit(1)

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aicore_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemStatus(Enum):
    """系統狀態枚舉"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

class WorkflowType(Enum):
    """工作流類型枚舉"""
    DEPLOYMENT = "deployment"
    CONFIGURATION = "configuration"
    MAINTENANCE = "maintenance"
    MONITORING = "monitoring"
    TESTING = "testing"
    OPTIMIZATION = "optimization"

@dataclass
class WorkflowRequest:
    """工作流請求"""
    request_id: str
    workflow_type: WorkflowType
    title: str
    description: str
    parameters: Dict[str, Any]
    priority: int = 1
    timeout: int = 3600  # 默認1小時超時
    callback_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class WorkflowResult:
    """工作流結果"""
    request_id: str
    status: str
    result: Dict[str, Any]
    execution_time: float
    human_interventions: List[Dict[str, Any]] = field(default_factory=list)
    expert_consultations: List[Dict[str, Any]] = field(default_factory=list)
    optimization_applied: List[Dict[str, Any]] = field(default_factory=list)
    completed_at: datetime = field(default_factory=datetime.now)

class HumanLoopMCPClient:
    """Human Loop MCP客戶端"""
    
    def __init__(self, base_url: str = "http://localhost:8096"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_session(self, session_data: Dict[str, Any]) -> str:
        """創建人工介入會話"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/sessions",
                json=session_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 201:
                    result = await response.json()
                    return result.get("session_id")
                else:
                    raise Exception(f"Failed to create session: {response.status}")
        except Exception as e:
            logger.error(f"Failed to create MCP session: {e}")
            raise
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """獲取會話狀態"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/sessions/{session_id}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to get session status: {response.status}")
        except Exception as e:
            logger.error(f"Failed to get session status: {e}")
            raise
    
    async def wait_for_response(self, session_id: str, timeout: int = 300) -> Dict[str, Any]:
        """等待人工回應"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                status = await self.get_session_status(session_id)
                
                if status.get("status") == "completed":
                    return status.get("response", {})
                elif status.get("status") == "cancelled":
                    raise Exception("Session was cancelled")
                elif status.get("status") == "expired":
                    raise Exception("Session expired")
                
                await asyncio.sleep(2)  # 每2秒檢查一次
                
            except Exception as e:
                logger.error(f"Error waiting for response: {e}")
                break
        
        raise TimeoutError(f"Timeout waiting for human response after {timeout} seconds")
    
    async def cancel_session(self, session_id: str, reason: str = "") -> bool:
        """取消會話"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.delete(
                f"{self.base_url}/api/sessions/{session_id}",
                json={"reason": reason},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Failed to cancel session: {e}")
            return False

class AICoreMasterController:
    """AICore主控制器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.status = SystemStatus.INITIALIZING
        self.start_time = None
        
        # 初始化組件
        self.router = None
        self.expert_system = None
        self.testing_framework = None
        self.optimization_system = None
        self.mcp_client = None
        
        # 工作流管理
        self.active_workflows = {}
        self.workflow_history = []
        
        # 統計信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "human_interventions": 0,
            "expert_consultations": 0,
            "optimizations_applied": 0
        }
        
        # 事件處理
        self.event_handlers = {}
        
        logger.info("AICore Master Controller initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加載配置"""
        default_config = {
            "system": {
                "name": "AICore Human-in-the-Loop System",
                "version": "1.0.0",
                "environment": "development"
            },
            "components": {
                "router": {"enabled": True},
                "expert_system": {"enabled": True},
                "testing_framework": {"enabled": True},
                "optimization_system": {"enabled": True},
                "human_loop_mcp": {"enabled": True, "url": "http://localhost:8096"}
            },
            "workflows": {
                "default_timeout": 3600,
                "max_concurrent": 10,
                "retry_count": 3
            },
            "monitoring": {
                "health_check_interval": 60,
                "metrics_collection_interval": 30,
                "log_level": "INFO"
            },
            "security": {
                "api_key_required": False,
                "rate_limiting": True,
                "max_requests_per_minute": 100
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    self._deep_update(default_config, user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """深度更新字典"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    async def initialize(self):
        """初始化系統"""
        try:
            logger.info("Initializing AICore system components...")
            
            # 初始化動態路由器
            if self.config["components"]["router"]["enabled"]:
                self.router = AICoreDynamicRouter()
                logger.info("Dynamic router initialized")
            
            # 初始化專家系統
            if self.config["components"]["expert_system"]["enabled"]:
                self.expert_system = ExpertInvocationSystem()
                logger.info("Expert system initialized")
            
            # 初始化測試框架
            if self.config["components"]["testing_framework"]["enabled"]:
                self.testing_framework = DeepTestingFramework()
                logger.info("Testing framework initialized")
            
            # 初始化優化系統
            if self.config["components"]["optimization_system"]["enabled"]:
                self.optimization_system = IncrementalOptimizationSystem()
                await self.optimization_system.start()
                logger.info("Optimization system initialized")
            
            # 初始化Human Loop MCP客戶端
            if self.config["components"]["human_loop_mcp"]["enabled"]:
                mcp_url = self.config["components"]["human_loop_mcp"]["url"]
                self.mcp_client = HumanLoopMCPClient(mcp_url)
                logger.info(f"Human Loop MCP client initialized: {mcp_url}")
            
            self.status = SystemStatus.RUNNING
            self.start_time = datetime.now()
            
            logger.info("AICore system initialization completed successfully")
            
        except Exception as e:
            self.status = SystemStatus.ERROR
            logger.error(f"Failed to initialize AICore system: {e}")
            raise
    
    async def shutdown(self):
        """關閉系統"""
        try:
            logger.info("Shutting down AICore system...")
            self.status = SystemStatus.STOPPING
            
            # 停止優化系統
            if self.optimization_system:
                await self.optimization_system.stop()
            
            # 關閉MCP客戶端
            if self.mcp_client and hasattr(self.mcp_client, 'session') and self.mcp_client.session:
                await self.mcp_client.session.close()
            
            # 取消所有活動工作流
            for workflow_id in list(self.active_workflows.keys()):
                await self._cancel_workflow(workflow_id, "System shutdown")
            
            self.status = SystemStatus.STOPPED
            logger.info("AICore system shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during system shutdown: {e}")
            self.status = SystemStatus.ERROR
    
    async def process_workflow(self, request: WorkflowRequest) -> WorkflowResult:
        """處理工作流請求"""
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        logger.info(f"Processing workflow request: {request.request_id}")
        
        try:
            # 添加到活動工作流
            self.active_workflows[request.request_id] = request
            
            # 創建路由上下文
            routing_context = RoutingContext(
                request_id=request.request_id,
                workflow_id=request.request_id,
                operation_type=request.workflow_type.value,
                metadata=request.metadata
            )
            
            # 動態路由決策
            routing_decision = await self.router.route_request(routing_context)
            
            # 記錄路由決策
            if self.optimization_system:
                self.optimization_system.collect_routing_decision(
                    decision_id=request.request_id,
                    input_features=request.metadata,
                    decision_type=routing_decision.decision_type.value,
                    confidence=routing_decision.confidence,
                    outcome="pending"
                )
            
            result = WorkflowResult(
                request_id=request.request_id,
                status="processing",
                result={},
                execution_time=0.0
            )
            
            # 根據路由決策執行相應流程
            if routing_decision.decision_type == DecisionType.AUTOMATIC:
                # 自動處理
                result = await self._process_automatic_workflow(request, routing_decision)
                
            elif routing_decision.decision_type == DecisionType.HUMAN_REQUIRED:
                # 需要人工介入
                result = await self._process_human_workflow(request, routing_decision)
                
            elif routing_decision.decision_type == DecisionType.EXPERT_CONSULTATION:
                # 需要專家諮詢
                result = await self._process_expert_workflow(request, routing_decision)
                
            elif routing_decision.decision_type == DecisionType.CONDITIONAL:
                # 條件性處理
                result = await self._process_conditional_workflow(request, routing_decision)
            
            # 計算執行時間
            result.execution_time = time.time() - start_time
            result.completed_at = datetime.now()
            
            # 更新統計
            if result.status == "completed":
                self.stats["successful_requests"] += 1
            else:
                self.stats["failed_requests"] += 1
            
            # 記錄優化數據
            if self.optimization_system:
                self.optimization_system.collect_routing_decision(
                    decision_id=request.request_id,
                    input_features=request.metadata,
                    decision_type=routing_decision.decision_type.value,
                    confidence=routing_decision.confidence,
                    outcome=result.status
                )
                
                # 收集性能指標
                self.optimization_system.collect_performance_metric(
                    metric_id="workflow_execution_time",
                    metric_type="latency",
                    value=result.execution_time * 1000,  # 轉換為毫秒
                    context={"workflow_type": request.workflow_type.value}
                )
            
            # 移除活動工作流
            if request.request_id in self.active_workflows:
                del self.active_workflows[request.request_id]
            
            # 添加到歷史記錄
            self.workflow_history.append(result)
            
            logger.info(f"Workflow {request.request_id} completed with status: {result.status}")
            return result
            
        except Exception as e:
            # 錯誤處理
            self.stats["failed_requests"] += 1
            
            error_result = WorkflowResult(
                request_id=request.request_id,
                status="error",
                result={"error": str(e)},
                execution_time=time.time() - start_time
            )
            
            # 移除活動工作流
            if request.request_id in self.active_workflows:
                del self.active_workflows[request.request_id]
            
            self.workflow_history.append(error_result)
            
            logger.error(f"Workflow {request.request_id} failed: {e}")
            return error_result
    
    async def _process_automatic_workflow(self, request: WorkflowRequest, routing_decision) -> WorkflowResult:
        """處理自動工作流"""
        logger.info(f"Processing automatic workflow: {request.request_id}")
        
        # 模擬自動處理邏輯
        await asyncio.sleep(1)  # 模擬處理時間
        
        return WorkflowResult(
            request_id=request.request_id,
            status="completed",
            result={
                "processing_type": "automatic",
                "routing_confidence": routing_decision.confidence,
                "message": "Workflow completed automatically"
            },
            execution_time=0.0
        )
    
    async def _process_human_workflow(self, request: WorkflowRequest, routing_decision) -> WorkflowResult:
        """處理需要人工介入的工作流"""
        logger.info(f"Processing human intervention workflow: {request.request_id}")
        
        if not self.mcp_client:
            raise Exception("Human Loop MCP client not available")
        
        # 創建人工介入會話
        session_data = {
            "interaction_data": {
                "interaction_type": "approval",
                "title": request.title,
                "message": request.description,
                "workflow_type": request.workflow_type.value,
                "parameters": request.parameters,
                "timeout": request.timeout
            },
            "workflow_id": request.request_id,
            "callback_url": request.callback_url
        }
        
        try:
            async with self.mcp_client as client:
                session_id = await client.create_session(session_data)
                
                # 等待人工回應
                human_response = await client.wait_for_response(session_id, request.timeout)
                
                self.stats["human_interventions"] += 1
                
                return WorkflowResult(
                    request_id=request.request_id,
                    status="completed",
                    result={
                        "processing_type": "human_intervention",
                        "human_response": human_response,
                        "session_id": session_id
                    },
                    execution_time=0.0,
                    human_interventions=[{
                        "session_id": session_id,
                        "response": human_response,
                        "timestamp": datetime.now().isoformat()
                    }]
                )
                
        except Exception as e:
            logger.error(f"Human intervention failed: {e}")
            return WorkflowResult(
                request_id=request.request_id,
                status="failed",
                result={"error": f"Human intervention failed: {str(e)}"},
                execution_time=0.0
            )
    
    async def _process_expert_workflow(self, request: WorkflowRequest, routing_decision) -> WorkflowResult:
        """處理需要專家諮詢的工作流"""
        logger.info(f"Processing expert consultation workflow: {request.request_id}")
        
        if not self.expert_system:
            raise Exception("Expert system not available")
        
        # 創建專家諮詢請求
        consultation_request = ConsultationRequest(
            request_id=request.request_id,
            workflow_id=request.request_id,
            expert_type=ExpertType.TECHNICAL,  # 根據工作流類型選擇專家類型
            title=request.title,
            description=request.description,
            context=request.parameters,
            timeout=min(request.timeout, 1800)  # 最多30分鐘
        )
        
        try:
            consultation_id = await self.expert_system.request_consultation(consultation_request)
            
            # 等待專家回應（這裡簡化處理）
            await asyncio.sleep(2)  # 模擬專家處理時間
            
            expert_response = {
                "recommendation": "Proceed with caution",
                "confidence": 0.85,
                "reasoning": "Based on the provided context, the operation appears safe to proceed."
            }
            
            self.stats["expert_consultations"] += 1
            
            return WorkflowResult(
                request_id=request.request_id,
                status="completed",
                result={
                    "processing_type": "expert_consultation",
                    "expert_response": expert_response,
                    "consultation_id": consultation_id
                },
                execution_time=0.0,
                expert_consultations=[{
                    "consultation_id": consultation_id,
                    "response": expert_response,
                    "timestamp": datetime.now().isoformat()
                }]
            )
            
        except Exception as e:
            logger.error(f"Expert consultation failed: {e}")
            return WorkflowResult(
                request_id=request.request_id,
                status="failed",
                result={"error": f"Expert consultation failed: {str(e)}"},
                execution_time=0.0
            )
    
    async def _process_conditional_workflow(self, request: WorkflowRequest, routing_decision) -> WorkflowResult:
        """處理條件性工作流"""
        logger.info(f"Processing conditional workflow: {request.request_id}")
        
        # 根據條件決定處理方式
        if routing_decision.confidence > 0.8:
            # 高信心度，自動處理
            return await self._process_automatic_workflow(request, routing_decision)
        else:
            # 低信心度，需要人工確認
            return await self._process_human_workflow(request, routing_decision)
    
    async def _cancel_workflow(self, workflow_id: str, reason: str = ""):
        """取消工作流"""
        if workflow_id in self.active_workflows:
            logger.info(f"Cancelling workflow: {workflow_id}")
            del self.active_workflows[workflow_id]
            
            # 如果有相關的MCP會話，也要取消
            if self.mcp_client:
                try:
                    async with self.mcp_client as client:
                        await client.cancel_session(workflow_id, reason)
                except:
                    pass  # 忽略取消錯誤
    
    async def run_system_tests(self) -> Dict[str, Any]:
        """運行系統測試"""
        if not self.testing_framework:
            return {"error": "Testing framework not available"}
        
        logger.info("Running system tests...")
        
        try:
            # 運行所有測試套件
            test_results = await self.testing_framework.run_all_tests()
            
            # 生成測試報告
            report = self.testing_framework.generate_report("json")
            
            logger.info("System tests completed")
            return {
                "status": "completed",
                "results": test_results,
                "report": json.loads(report)
            }
            
        except Exception as e:
            logger.error(f"System tests failed: {e}")
            return {"error": str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        status = {
            "system": {
                "status": self.status.value,
                "uptime_seconds": uptime,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "version": self.config["system"]["version"]
            },
            "components": {
                "router": {"enabled": self.router is not None},
                "expert_system": {"enabled": self.expert_system is not None},
                "testing_framework": {"enabled": self.testing_framework is not None},
                "optimization_system": {"enabled": self.optimization_system is not None},
                "human_loop_mcp": {"enabled": self.mcp_client is not None}
            },
            "workflows": {
                "active_count": len(self.active_workflows),
                "total_processed": len(self.workflow_history),
                "active_workflows": list(self.active_workflows.keys())
            },
            "statistics": self.stats.copy()
        }
        
        # 添加優化系統狀態
        if self.optimization_system:
            try:
                opt_status = self.optimization_system.get_system_status()
                status["optimization"] = opt_status
            except:
                status["optimization"] = {"error": "Failed to get optimization status"}
        
        return status
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """獲取工作流狀態"""
        # 檢查活動工作流
        if workflow_id in self.active_workflows:
            request = self.active_workflows[workflow_id]
            return {
                "status": "active",
                "request": asdict(request),
                "started_at": request.created_at.isoformat()
            }
        
        # 檢查歷史記錄
        for result in self.workflow_history:
            if result.request_id == workflow_id:
                return {
                    "status": "completed",
                    "result": asdict(result)
                }
        
        return None
    
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # 檢查各組件健康狀態
        try:
            # 檢查路由器
            if self.router:
                health["components"]["router"] = {"status": "healthy"}
            
            # 檢查專家系統
            if self.expert_system:
                health["components"]["expert_system"] = {"status": "healthy"}
            
            # 檢查測試框架
            if self.testing_framework:
                health["components"]["testing_framework"] = {"status": "healthy"}
            
            # 檢查優化系統
            if self.optimization_system:
                health["components"]["optimization_system"] = {"status": "healthy"}
            
            # 檢查MCP連接
            if self.mcp_client:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"{self.config['components']['human_loop_mcp']['url']}/api/health",
                            timeout=aiohttp.ClientTimeout(total=5)
                        ) as response:
                            if response.status == 200:
                                health["components"]["human_loop_mcp"] = {"status": "healthy"}
                            else:
                                health["components"]["human_loop_mcp"] = {"status": "unhealthy", "reason": f"HTTP {response.status}"}
                except Exception as e:
                    health["components"]["human_loop_mcp"] = {"status": "unhealthy", "reason": str(e)}
            
            # 檢查是否有不健康的組件
            unhealthy_components = [
                name for name, status in health["components"].items()
                if status.get("status") != "healthy"
            ]
            
            if unhealthy_components:
                health["status"] = "degraded"
                health["unhealthy_components"] = unhealthy_components
            
        except Exception as e:
            health["status"] = "unhealthy"
            health["error"] = str(e)
        
        return health

# Web API服務器（可選）
class AICoreMasterAPI:
    """AICore主控制器Web API"""
    
    def __init__(self, controller: AICoreMasterController, port: int = 8098):
        self.controller = controller
        self.port = port
        self.app = None
    
    async def start_server(self):
        """啟動Web服務器"""
        try:
            from aiohttp import web, web_request
            
            app = web.Application()
            
            # 添加路由
            app.router.add_get('/api/health', self.health_check)
            app.router.add_get('/api/status', self.get_status)
            app.router.add_post('/api/workflows', self.create_workflow)
            app.router.add_get('/api/workflows/{workflow_id}', self.get_workflow)
            app.router.add_post('/api/tests/run', self.run_tests)
            
            # 啟動服務器
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, 'localhost', self.port)
            await site.start()
            
            logger.info(f"AICore API server started on port {self.port}")
            
        except ImportError:
            logger.warning("aiohttp not available, skipping web API server")
        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
    
    async def health_check(self, request):
        """健康檢查端點"""
        from aiohttp import web
        health = await self.controller.health_check()
        return web.json_response(health)
    
    async def get_status(self, request):
        """獲取系統狀態端點"""
        from aiohttp import web
        status = self.controller.get_system_status()
        return web.json_response(status)
    
    async def create_workflow(self, request):
        """創建工作流端點"""
        from aiohttp import web
        try:
            data = await request.json()
            
            workflow_request = WorkflowRequest(
                request_id=str(uuid.uuid4()),
                workflow_type=WorkflowType(data.get("workflow_type", "deployment")),
                title=data.get("title", ""),
                description=data.get("description", ""),
                parameters=data.get("parameters", {}),
                priority=data.get("priority", 1),
                timeout=data.get("timeout", 3600),
                callback_url=data.get("callback_url"),
                metadata=data.get("metadata", {})
            )
            
            result = await self.controller.process_workflow(workflow_request)
            return web.json_response(asdict(result))
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)
    
    async def get_workflow(self, request):
        """獲取工作流狀態端點"""
        from aiohttp import web
        workflow_id = request.match_info['workflow_id']
        status = self.controller.get_workflow_status(workflow_id)
        
        if status:
            return web.json_response(status)
        else:
            return web.json_response({"error": "Workflow not found"}, status=404)
    
    async def run_tests(self, request):
        """運行測試端點"""
        from aiohttp import web
        try:
            results = await self.controller.run_system_tests()
            return web.json_response(results)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

# 主函數
async def main():
    """主函數"""
    # 設置信號處理
    controller = None
    api_server = None
    
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        if controller:
            asyncio.create_task(controller.shutdown())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 創建主控制器
        controller = AICoreMasterController("aicore_config.yaml")
        
        # 初始化系統
        await controller.initialize()
        
        # 啟動API服務器（可選）
        if controller.config.get("api", {}).get("enabled", True):
            api_server = AICoreMasterAPI(controller, controller.config.get("api", {}).get("port", 8098))
            await api_server.start_server()
        
        logger.info("AICore Human-in-the-Loop Integration System is running")
        
        # 運行系統測試（可選）
        if controller.config.get("startup", {}).get("run_tests", False):
            test_results = await controller.run_system_tests()
            logger.info(f"Startup tests completed: {test_results.get('status', 'unknown')}")
        
        # 示例工作流處理
        sample_request = WorkflowRequest(
            request_id=str(uuid.uuid4()),
            workflow_type=WorkflowType.DEPLOYMENT,
            title="Sample Deployment",
            description="This is a sample deployment workflow",
            parameters={"environment": "staging", "version": "1.0.0"},
            metadata={"complexity": "medium", "risk_level": "low"}
        )
        
        logger.info("Processing sample workflow...")
        result = await controller.process_workflow(sample_request)
        logger.info(f"Sample workflow result: {result.status}")
        
        # 保持系統運行
        while controller.status == SystemStatus.RUNNING:
            await asyncio.sleep(60)  # 每分鐘檢查一次
            
            # 定期健康檢查
            health = await controller.health_check()
            if health["status"] != "healthy":
                logger.warning(f"System health check failed: {health}")
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"System error: {e}")
    finally:
        if controller:
            await controller.shutdown()

if __name__ == "__main__":
    # 創建配置文件示例
    config_example = {
        "system": {
            "name": "AICore Human-in-the-Loop System",
            "version": "1.0.0",
            "environment": "production"
        },
        "components": {
            "router": {"enabled": True},
            "expert_system": {"enabled": True},
            "testing_framework": {"enabled": True},
            "optimization_system": {"enabled": True},
            "human_loop_mcp": {"enabled": True, "url": "http://localhost:8096"}
        },
        "api": {
            "enabled": True,
            "port": 8098
        },
        "startup": {
            "run_tests": True
        }
    }
    
    # 如果配置文件不存在，創建示例配置
    if not os.path.exists("aicore_config.yaml"):
        with open("aicore_config.yaml", "w", encoding="utf-8") as f:
            yaml.dump(config_example, f, default_flow_style=False, allow_unicode=True)
        logger.info("Created example configuration file: aicore_config.yaml")
    
    # 運行主程序
    asyncio.run(main())

