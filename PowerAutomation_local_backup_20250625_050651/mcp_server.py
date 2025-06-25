"""
PowerAutomation MCP Server with Replay Chain Support
支持Replay鏈結的MCP服務器端點處理器

Author: Manus AI
Version: 2.0.0
Date: 2025-06-23
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import asdict
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from mcp_manus_integration import MCPManusIntegration
from manus_replay_chain_core import TaskNode, ReplayChain, ChainStatus, TaskStatus


# ==================== Pydantic模型定義 ====================

class MCPRequest(BaseModel):
    """MCP請求模型"""
    method: str = Field(..., description="方法名")
    params: Dict[str, Any] = Field(default_factory=dict, description="參數")
    request_id: Optional[str] = Field(default=None, description="請求ID")
    timestamp: Optional[float] = Field(default_factory=time.time, description="時間戳")


class MCPResponse(BaseModel):
    """MCP響應模型"""
    success: bool = Field(..., description="是否成功")
    method: str = Field(..., description="方法名")
    result: Optional[Dict[str, Any]] = Field(default=None, description="結果數據")
    error: Optional[str] = Field(default=None, description="錯誤信息")
    error_type: Optional[str] = Field(default=None, description="錯誤類型")
    request_id: Optional[str] = Field(default=None, description="請求ID")
    timestamp: float = Field(default_factory=time.time, description="時間戳")
    execution_time: Optional[float] = Field(default=None, description="執行時間")


class TaskCreateRequest(BaseModel):
    """創建任務請求模型"""
    task_type: str = Field(..., description="任務類型")
    description: str = Field(..., description="任務描述")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="任務參數")
    priority: int = Field(default=5, ge=1, le=10, description="優先級(1-10)")
    dependencies: List[str] = Field(default_factory=list, description="依賴任務ID列表")


class ChainCreateRequest(BaseModel):
    """創建鏈結請求模型"""
    task_ids: List[str] = Field(..., min_items=2, description="任務ID列表")
    chain_name: Optional[str] = Field(default=None, description="鏈結名稱")
    description: Optional[str] = Field(default=None, description="鏈結描述")


class ChainExecuteRequest(BaseModel):
    """執行鏈結請求模型"""
    chain_id: str = Field(..., description="鏈結ID")
    execution_mode: str = Field(default="sequential", description="執行模式")
    monitoring: Dict[str, bool] = Field(default_factory=dict, description="監控選項")


class HealthCheckResponse(BaseModel):
    """健康檢查響應模型"""
    status: str = Field(..., description="服務狀態")
    timestamp: float = Field(..., description="時間戳")
    version: str = Field(..., description="版本號")
    services: Dict[str, str] = Field(..., description="服務狀態")
    metrics: Dict[str, Any] = Field(..., description="性能指標")


# ==================== MCP服務器類 ====================

class MCPServer:
    """MCP服務器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化MCP服務器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 創建FastAPI應用
        self.app = FastAPI(
            title="PowerAutomation MCP Server",
            description="支持Replay鏈結的MCP服務器",
            version="2.0.0"
        )
        
        # 配置CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Manus集成實例
        self.manus_integration = None
        
        # 服務器狀態
        self.server_status = {
            "started_at": time.time(),
            "request_count": 0,
            "error_count": 0,
            "active_connections": 0,
            "active_executions": 0
        }
        
        # 註冊路由
        self._register_routes()
    
    def _register_routes(self):
        """註冊API路由"""
        
        @self.app.on_event("startup")
        async def startup_event():
            """服務器啟動事件"""
            await self._initialize_services()
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """服務器關閉事件"""
            await self._cleanup_services()
        
        # ==================== 健康檢查端點 ====================
        
        @self.app.get("/v3/health", response_model=HealthCheckResponse)
        async def health_check():
            """健康檢查"""
            return HealthCheckResponse(
                status="healthy",
                timestamp=time.time(),
                version="2.0.0",
                services={
                    "mcp_server": "healthy",
                    "manus_integration": "healthy" if self.manus_integration else "unavailable",
                    "replay_chain_manager": "healthy"
                },
                metrics={
                    "uptime": time.time() - self.server_status["started_at"],
                    "request_count": self.server_status["request_count"],
                    "error_count": self.server_status["error_count"],
                    "active_connections": self.server_status["active_connections"],
                    "active_executions": self.server_status["active_executions"]
                }
            )
        
        # ==================== 連接管理端點 ====================
        
        @self.app.post("/v3/connect", response_model=MCPResponse)
        async def connect_client(request: MCPRequest):
            """建立客戶端連接"""
            try:
                self.server_status["request_count"] += 1
                self.server_status["active_connections"] += 1
                
                client_id = request.params.get("client_id", f"client_{uuid.uuid4().hex[:8]}")
                version = request.params.get("version", "unknown")
                capabilities = request.params.get("capabilities", [])
                
                # 初始化Manus集成（如果尚未初始化）
                if not self.manus_integration:
                    await self._initialize_manus_integration()
                
                result = {
                    "status": "connected",
                    "session_id": f"sess_{uuid.uuid4().hex[:8]}",
                    "client_id": client_id,
                    "server_capabilities": [
                        "task_management",
                        "chain_execution",
                        "manus_automation",
                        "real_time_monitoring",
                        "smart_routing"
                    ],
                    "supported_methods": list(self.manus_integration.mcp_handlers.keys()) if self.manus_integration else [],
                    "heartbeat_interval": 30,
                    "max_message_size": 1048576
                }
                
                return MCPResponse(
                    success=True,
                    method="connect",
                    result=result,
                    request_id=request.request_id
                )
                
            except Exception as e:
                self.server_status["error_count"] += 1
                self.logger.error(f"連接失敗: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/v3/disconnect", response_model=MCPResponse)
        async def disconnect_client(request: MCPRequest):
            """斷開客戶端連接"""
            try:
                self.server_status["active_connections"] = max(0, self.server_status["active_connections"] - 1)
                
                return MCPResponse(
                    success=True,
                    method="disconnect",
                    result={"status": "disconnected"},
                    request_id=request.request_id
                )
                
            except Exception as e:
                self.logger.error(f"斷開連接失敗: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # ==================== 通用MCP請求處理端點 ====================
        
        @self.app.post("/v3/request", response_model=MCPResponse)
        async def handle_mcp_request(request: MCPRequest):
            """處理通用MCP請求"""
            start_time = time.time()
            
            try:
                self.server_status["request_count"] += 1
                
                if not self.manus_integration:
                    raise HTTPException(status_code=503, detail="Manus集成服務不可用")
                
                # 處理請求
                result = await self.manus_integration.handle_mcp_request(request.method, request.params)
                
                # 計算執行時間
                execution_time = time.time() - start_time
                
                return MCPResponse(
                    success=result.get("success", False),
                    method=request.method,
                    result=result.get("result"),
                    error=result.get("error"),
                    error_type=result.get("error_type"),
                    request_id=request.request_id,
                    execution_time=execution_time
                )
                
            except Exception as e:
                self.server_status["error_count"] += 1
                execution_time = time.time() - start_time
                self.logger.error(f"處理MCP請求失敗: {request.method}, 錯誤: {e}")
                
                return MCPResponse(
                    success=False,
                    method=request.method,
                    error=str(e),
                    error_type=type(e).__name__,
                    request_id=request.request_id,
                    execution_time=execution_time
                )
        
        # ==================== 任務管理端點 ====================
        
        @self.app.post("/v3/tasks/create", response_model=MCPResponse)
        async def create_task(task_request: TaskCreateRequest):
            """創建任務"""
            try:
                if not self.manus_integration:
                    raise HTTPException(status_code=503, detail="Manus集成服務不可用")
                
                params = {
                    "task_type": task_request.task_type,
                    "description": task_request.description,
                    "parameters": task_request.parameters,
                    "priority": task_request.priority,
                    "dependencies": task_request.dependencies
                }
                
                result = await self.manus_integration.handle_mcp_request("create_task", params)
                
                return MCPResponse(
                    success=result.get("success", False),
                    method="create_task",
                    result=result.get("result"),
                    error=result.get("error")
                )
                
            except Exception as e:
                self.logger.error(f"創建任務失敗: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/v3/tasks/list", response_model=MCPResponse)
        async def list_tasks():
            """列出所有任務"""
            try:
                if not self.manus_integration:
                    raise HTTPException(status_code=503, detail="Manus集成服務不可用")
                
                tasks = await self.manus_integration.chain_manager.list_tasks()
                task_list = [task.to_dict() for task in tasks]
                
                return MCPResponse(
                    success=True,
                    method="list_tasks",
                    result={"tasks": task_list, "count": len(task_list)}
                )
                
            except Exception as e:
                self.logger.error(f"列出任務失敗: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/v3/tasks/{task_id}", response_model=MCPResponse)
        async def get_task(task_id: str):
            """獲取特定任務"""
            try:
                if not self.manus_integration:
                    raise HTTPException(status_code=503, detail="Manus集成服務不可用")
                
                task = await self.manus_integration.chain_manager.get_task(task_id)
                
                if task:
                    return MCPResponse(
                        success=True,
                        method="get_task",
                        result=task.to_dict()
                    )
                else:
                    raise HTTPException(status_code=404, detail=f"任務不存在: {task_id}")
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"獲取任務失敗: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # ==================== 鏈結管理端點 ====================
        
        @self.app.post("/v3/chains/create", response_model=MCPResponse)
        async def create_chain(chain_request: ChainCreateRequest):
            """創建鏈結"""
            try:
                if not self.manus_integration:
                    raise HTTPException(status_code=503, detail="Manus集成服務不可用")
                
                params = {
                    "task_ids": chain_request.task_ids,
                    "chain_name": chain_request.chain_name
                }
                
                result = await self.manus_integration.handle_mcp_request("create_chain", params)
                
                return MCPResponse(
                    success=result.get("success", False),
                    method="create_chain",
                    result=result.get("result"),
                    error=result.get("error")
                )
                
            except Exception as e:
                self.logger.error(f"創建鏈結失敗: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/v3/chains/{chain_id}/execute", response_model=MCPResponse)
        async def execute_chain(chain_id: str, background_tasks: BackgroundTasks):
            """執行鏈結"""
            try:
                if not self.manus_integration:
                    raise HTTPException(status_code=503, detail="Manus集成服務不可用")
                
                # 在後台執行鏈結
                background_tasks.add_task(self._execute_chain_background, chain_id)
                
                return MCPResponse(
                    success=True,
                    method="execute_chain",
                    result={
                        "chain_id": chain_id,
                        "status": "execution_started",
                        "message": "鏈結執行已在後台開始"
                    }
                )
                
            except Exception as e:
                self.logger.error(f"執行鏈結失敗: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/v3/chains/{chain_id}/status", response_model=MCPResponse)
        async def get_chain_status(chain_id: str):
            """獲取鏈結狀態"""
            try:
                if not self.manus_integration:
                    raise HTTPException(status_code=503, detail="Manus集成服務不可用")
                
                result = await self.manus_integration.handle_mcp_request("get_chain_status", {"chain_id": chain_id})
                
                return MCPResponse(
                    success=result.get("success", False),
                    method="get_chain_status",
                    result=result.get("result"),
                    error=result.get("error")
                )
                
            except Exception as e:
                self.logger.error(f"獲取鏈結狀態失敗: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/v3/chains/list", response_model=MCPResponse)
        async def list_chains():
            """列出所有鏈結"""
            try:
                if not self.manus_integration:
                    raise HTTPException(status_code=503, detail="Manus集成服務不可用")
                
                result = await self.manus_integration.handle_mcp_request("list_chains", {})
                
                return MCPResponse(
                    success=result.get("success", False),
                    method="list_chains",
                    result=result.get("result"),
                    error=result.get("error")
                )
                
            except Exception as e:
                self.logger.error(f"列出鏈結失敗: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/v3/chains/{chain_id}", response_model=MCPResponse)
        async def delete_chain(chain_id: str):
            """刪除鏈結"""
            try:
                if not self.manus_integration:
                    raise HTTPException(status_code=503, detail="Manus集成服務不可用")
                
                result = await self.manus_integration.handle_mcp_request("delete_chain", {"chain_id": chain_id})
                
                return MCPResponse(
                    success=result.get("success", False),
                    method="delete_chain",
                    result=result.get("result"),
                    error=result.get("error")
                )
                
            except Exception as e:
                self.logger.error(f"刪除鏈結失敗: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/v3/chains/auto-generate", response_model=MCPResponse)
        async def auto_generate_chains():
            """自動生成鏈結"""
            try:
                if not self.manus_integration:
                    raise HTTPException(status_code=503, detail="Manus集成服務不可用")
                
                result = await self.manus_integration.handle_mcp_request("auto_generate_chains", {})
                
                return MCPResponse(
                    success=result.get("success", False),
                    method="auto_generate_chains",
                    result=result.get("result"),
                    error=result.get("error")
                )
                
            except Exception as e:
                self.logger.error(f"自動生成鏈結失敗: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # ==================== 執行監控端點 ====================
        
        @self.app.get("/v3/executions/{execution_id}/progress", response_model=MCPResponse)
        async def get_execution_progress(execution_id: str):
            """獲取執行進度"""
            try:
                if not self.manus_integration:
                    raise HTTPException(status_code=503, detail="Manus集成服務不可用")
                
                result = await self.manus_integration.handle_mcp_request("get_execution_progress", {"execution_id": execution_id})
                
                return MCPResponse(
                    success=result.get("success", False),
                    method="get_execution_progress",
                    result=result.get("result"),
                    error=result.get("error")
                )
                
            except Exception as e:
                self.logger.error(f"獲取執行進度失敗: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/v3/executions/{execution_id}/cancel", response_model=MCPResponse)
        async def cancel_execution(execution_id: str):
            """取消執行"""
            try:
                if not self.manus_integration:
                    raise HTTPException(status_code=503, detail="Manus集成服務不可用")
                
                result = await self.manus_integration.handle_mcp_request("cancel_execution", {"execution_id": execution_id})
                
                return MCPResponse(
                    success=result.get("success", False),
                    method="cancel_execution",
                    result=result.get("result"),
                    error=result.get("error")
                )
                
            except Exception as e:
                self.logger.error(f"取消執行失敗: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # ==================== 系統狀態端點 ====================
        
        @self.app.get("/v3/system/status", response_model=MCPResponse)
        async def get_system_status():
            """獲取系統狀態"""
            try:
                if not self.manus_integration:
                    raise HTTPException(status_code=503, detail="Manus集成服務不可用")
                
                result = await self.manus_integration.handle_mcp_request("get_system_status", {})
                
                # 添加服務器狀態
                if result.get("success"):
                    result["result"]["server_status"] = self.server_status.copy()
                    result["result"]["server_status"]["uptime"] = time.time() - self.server_status["started_at"]
                
                return MCPResponse(
                    success=result.get("success", False),
                    method="get_system_status",
                    result=result.get("result"),
                    error=result.get("error")
                )
                
            except Exception as e:
                self.logger.error(f"獲取系統狀態失敗: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _initialize_services(self):
        """初始化服務"""
        try:
            self.logger.info("初始化MCP服務器服務...")
            
            # 初始化Manus集成
            await self._initialize_manus_integration()
            
            self.logger.info("✅ MCP服務器服務初始化完成")
            
        except Exception as e:
            self.logger.error(f"初始化服務失敗: {e}")
            raise
    
    async def _initialize_manus_integration(self):
        """初始化Manus集成"""
        try:
            if self.manus_integration:
                return
            
            # 從配置創建Manus集成
            manus_config = self.config.get("manus", {})
            
            # 創建日誌器
            manus_logger = logging.getLogger("mcp_manus_integration")
            
            # 創建集成實例
            self.manus_integration = MCPManusIntegration(manus_config, manus_logger)
            
            # 初始化
            success = await self.manus_integration.initialize()
            
            if not success:
                raise Exception("Manus集成初始化失敗")
            
            self.logger.info("✅ Manus集成初始化成功")
            
        except Exception as e:
            self.logger.error(f"初始化Manus集成失敗: {e}")
            self.manus_integration = None
            raise
    
    async def _cleanup_services(self):
        """清理服務"""
        try:
            self.logger.info("清理MCP服務器服務...")
            
            if self.manus_integration:
                await self.manus_integration.cleanup()
                self.manus_integration = None
            
            self.logger.info("✅ MCP服務器服務清理完成")
            
        except Exception as e:
            self.logger.error(f"清理服務失敗: {e}")
    
    async def _execute_chain_background(self, chain_id: str):
        """在後台執行鏈結"""
        try:
            self.server_status["active_executions"] += 1
            
            result = await self.manus_integration.handle_mcp_request("execute_chain", {"chain_id": chain_id})
            
            if result.get("success"):
                self.logger.info(f"鏈結執行完成: {chain_id}")
            else:
                self.logger.error(f"鏈結執行失敗: {chain_id}, 錯誤: {result.get('error')}")
            
        except Exception as e:
            self.logger.error(f"後台執行鏈結失敗: {chain_id}, 錯誤: {e}")
        
        finally:
            self.server_status["active_executions"] = max(0, self.server_status["active_executions"] - 1)
    
    def run(self, host: str = "0.0.0.0", port: int = 8080, **kwargs):
        """運行服務器"""
        self.logger.info(f"啟動MCP服務器: {host}:{port}")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info",
            **kwargs
        )


# ==================== 配置和啟動 ====================

def create_server_config() -> Dict[str, Any]:
    """創建服務器配置"""
    return {
        "server": {
            "host": "0.0.0.0",
            "port": 8080,
            "workers": 1,
            "log_level": "info"
        },
        "manus": {
            "base_url": "https://manus.im",
            "app_url": "https://manus.im/app/uuX3KzwzsthCSgqmbQbgOz",
            "login_email": "chuang.hsiaoyen@gmail.com",
            "login_password": "silentfleet#1234",
            "auto_login": True,
            "keep_alive": True,
            "headless": False,
            "slow_mo": 1000
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }


def setup_logging(config: Dict[str, Any]):
    """設置日誌"""
    logging_config = config.get("logging", {})
    
    logging.basicConfig(
        level=getattr(logging, logging_config.get("level", "INFO")),
        format=logging_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
        handlers=[
            logging.FileHandler("/home/ubuntu/mcp_server.log"),
            logging.StreamHandler()
        ]
    )


async def main():
    """主函數"""
    # 創建配置
    config = create_server_config()
    
    # 設置日誌
    setup_logging(config)
    
    # 創建服務器
    server = MCPServer(config)
    
    # 運行服務器
    server_config = config.get("server", {})
    server.run(
        host=server_config.get("host", "0.0.0.0"),
        port=server_config.get("port", 8080),
        workers=server_config.get("workers", 1),
        log_level=server_config.get("log_level", "info")
    )


if __name__ == "__main__":
    asyncio.run(main())

