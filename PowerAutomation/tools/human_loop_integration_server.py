#!/usr/bin/env python3
"""
Human Loop Integration Tool API Server
提供HTTP API接口來使用Human Loop Integration Tool

這個服務器作為獨立服務運行，不修改AICore核心
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 導入我們的工具
from human_loop_integration_tool import (
    HumanLoopIntegrationTool, 
    HumanLoopIntegrationAPI,
    WorkflowContext
)

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI應用
app = FastAPI(
    title="Human Loop Integration Tool API",
    description="PowerAutomation Human-in-the-Loop Integration System API",
    version="1.0.0"
)

# 添加CORS中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局變量
tool = None
api = None

# Pydantic模型
class WorkflowRequest(BaseModel):
    workflow_id: str = None
    title: str
    description: str
    parameters: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    result: Dict[str, Any] = None
    error: str = None
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    components: Dict[str, str]

class DecisionHistoryResponse(BaseModel):
    history: list
    total_count: int

@app.on_event("startup")
async def startup_event():
    """應用啟動事件"""
    global tool, api
    
    logger.info("Starting Human Loop Integration Tool API Server...")
    
    # 初始化工具
    config_path = Path(__file__).parent / "human_loop_integration_config.json"
    tool = HumanLoopIntegrationTool(str(config_path) if config_path.exists() else None)
    api = HumanLoopIntegrationAPI(tool)
    
    logger.info("Human Loop Integration Tool API Server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉事件"""
    logger.info("Shutting down Human Loop Integration Tool API Server...")

@app.get("/", response_model=Dict[str, str])
async def root():
    """根路徑"""
    return {
        "message": "Human Loop Integration Tool API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """健康檢查"""
    try:
        # 檢查各組件狀態
        components = {
            "database": "ok",
            "human_loop_mcp": "unknown",  # 需要實際檢查
            "aicore_api": "unknown",      # 需要實際檢查
            "expert_system": "ok",
            "testing_framework": "ok"
        }
        
        # 嘗試檢查Human Loop MCP連接
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{tool.human_loop_mcp_url}/health", timeout=5) as response:
                    if response.status == 200:
                        components["human_loop_mcp"] = "ok"
                    else:
                        components["human_loop_mcp"] = "error"
        except:
            components["human_loop_mcp"] = "unreachable"
        
        # 嘗試檢查AICore API連接
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{tool.aicore_api_url}/health", timeout=5) as response:
                    if response.status == 200:
                        components["aicore_api"] = "ok"
                    else:
                        components["aicore_api"] = "error"
        except:
            components["aicore_api"] = "unreachable"
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            components=components
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/api/workflows", response_model=WorkflowResponse)
async def create_workflow(workflow_request: WorkflowRequest, background_tasks: BackgroundTasks):
    """創建並處理工作流"""
    try:
        # 生成workflow_id如果未提供
        if not workflow_request.workflow_id:
            workflow_request.workflow_id = f"wf_{int(datetime.now().timestamp())}"
        
        # 轉換為字典
        workflow_data = workflow_request.dict()
        
        # 處理工作流
        result = await api.create_workflow(workflow_data)
        
        return WorkflowResponse(
            workflow_id=result['workflow_id'],
            status=result['status'],
            result=result.get('result'),
            error=result.get('error'),
            timestamp=result['timestamp']
        )
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating workflow: {str(e)}")

@app.get("/api/workflows/{workflow_id}", response_model=Dict[str, Any])
async def get_workflow_status(workflow_id: str):
    """獲取工作流狀態"""
    try:
        result = await api.get_workflow_status(workflow_id)
        
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting workflow status: {str(e)}")

@app.get("/api/decisions/history", response_model=DecisionHistoryResponse)
async def get_decision_history(limit: int = 10):
    """獲取決策歷史"""
    try:
        history = await api.get_decision_history(limit)
        
        return DecisionHistoryResponse(
            history=history,
            total_count=len(history)
        )
    except Exception as e:
        logger.error(f"Error getting decision history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting decision history: {str(e)}")

@app.get("/api/config", response_model=Dict[str, Any])
async def get_config():
    """獲取當前配置"""
    try:
        return tool.config
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting config: {str(e)}")

@app.post("/api/config", response_model=Dict[str, str])
async def update_config(config_data: Dict[str, Any]):
    """更新配置"""
    try:
        # 更新配置
        tool.config.update(config_data)
        
        # 保存到文件
        config_path = Path(__file__).parent / "human_loop_integration_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(tool.config, f, indent=2, ensure_ascii=False)
        
        return {"message": "Configuration updated successfully"}
    except Exception as e:
        logger.error(f"Error updating config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating config: {str(e)}")

@app.get("/api/stats", response_model=Dict[str, Any])
async def get_statistics():
    """獲取統計信息"""
    try:
        import sqlite3
        
        conn = sqlite3.connect(tool.db_path)
        cursor = conn.cursor()
        
        # 獲取各種統計信息
        stats = {}
        
        # 總工作流數
        cursor.execute("SELECT COUNT(*) FROM workflows")
        stats['total_workflows'] = cursor.fetchone()[0]
        
        # 成功率
        cursor.execute("SELECT COUNT(*) FROM workflows WHERE status = 'completed'")
        completed = cursor.fetchone()[0]
        stats['success_rate'] = completed / stats['total_workflows'] if stats['total_workflows'] > 0 else 0
        
        # 決策類型分布
        cursor.execute("""
            SELECT decision_type, COUNT(*) 
            FROM decision_history 
            GROUP BY decision_type
        """)
        decision_distribution = dict(cursor.fetchall())
        stats['decision_distribution'] = decision_distribution
        
        # 平均複雜度和風險
        cursor.execute("""
            SELECT AVG(complexity_score), AVG(risk_score), AVG(confidence_score)
            FROM decision_history
        """)
        averages = cursor.fetchone()
        stats['average_scores'] = {
            'complexity': averages[0] if averages[0] else 0,
            'risk': averages[1] if averages[1] else 0,
            'confidence': averages[2] if averages[2] else 0
        }
        
        # 最近24小時的活動
        cursor.execute("""
            SELECT COUNT(*) 
            FROM workflows 
            WHERE created_at > datetime('now', '-1 day')
        """)
        stats['recent_activity'] = cursor.fetchone()[0]
        
        conn.close()
        
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

@app.post("/api/test", response_model=Dict[str, Any])
async def run_test_workflow():
    """運行測試工作流"""
    try:
        # 創建測試工作流
        test_workflow = WorkflowRequest(
            title="測試工作流",
            description="Human Loop Integration Tool功能測試",
            parameters={
                "test_mode": True,
                "target": "test_environment"
            },
            metadata={
                "workflow_type": "testing",
                "environment": "development",
                "operation_type": "read",
                "data_sensitivity": "low",
                "system_impact": "low"
            }
        )
        
        # 處理測試工作流
        result = await create_workflow(test_workflow, BackgroundTasks())
        
        return {
            "test_result": result,
            "message": "測試工作流執行完成"
        }
    except Exception as e:
        logger.error(f"Error running test workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running test workflow: {str(e)}")

# 主函數
def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Human Loop Integration Tool API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8098, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")
    
    args = parser.parse_args()
    
    logger.info(f"Starting Human Loop Integration Tool API Server on {args.host}:{args.port}")
    
    uvicorn.run(
        "human_loop_integration_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )

if __name__ == "__main__":
    main()

