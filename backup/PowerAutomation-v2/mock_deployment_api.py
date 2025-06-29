"""
Mock Deployment API Server for Testing VSIX Auto Deployer
用於測試 VSIX 自動部署器的模擬部署 API 服務器

Author: Manus AI
Version: 1.0.0
Date: 2025-06-24
"""

import asyncio
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn


class VSIXDeployRequest(BaseModel):
    """VSIX 部署請求模型"""
    vsix_path: str
    target_environment: str = "development"


class VSIXDeployResponse(BaseModel):
    """VSIX 部署響應模型"""
    success: bool
    message: str
    deployment_id: str
    vsix_file: str
    target_environment: str
    status: str


# 創建 FastAPI 應用
app = FastAPI(
    title="Mock VSIX Deployment API",
    description="模擬 VSIX 部署 API 服務器",
    version="1.0.0"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "service": "Mock VSIX Deployment API",
        "version": "1.0.0"
    }


@app.post("/api/mcp/deploy_vsix", response_model=VSIXDeployResponse)
async def deploy_vsix(request: VSIXDeployRequest):
    """
    模擬 VSIX 部署端點
    
    Args:
        request: VSIX 部署請求
        
    Returns:
        部署響應
    """
    logger.info(f"收到 VSIX 部署請求: {request.vsix_path}")
    
    try:
        # 模擬部署邏輯
        import os
        import time
        
        # 檢查檔案是否存在
        if not os.path.exists(request.vsix_path):
            raise HTTPException(
                status_code=404,
                detail=f"VSIX 檔案不存在: {request.vsix_path}"
            )
        
        # 模擬部署時間
        await asyncio.sleep(1)
        
        # 生成部署 ID
        deployment_id = f"deploy_{int(time.time())}"
        
        # 提取檔案名
        vsix_file = os.path.basename(request.vsix_path)
        
        # 模擬成功部署
        response = VSIXDeployResponse(
            success=True,
            message=f"VSIX 檔案 {vsix_file} 已成功部署到 {request.target_environment} 環境",
            deployment_id=deployment_id,
            vsix_file=vsix_file,
            target_environment=request.target_environment,
            status="completed"
        )
        
        logger.info(f"VSIX 部署成功: {vsix_file} -> {request.target_environment}")
        return response
        
    except Exception as e:
        logger.error(f"VSIX 部署失敗: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"部署失敗: {str(e)}"
        )


@app.get("/api/mcp/deployment_status/{deployment_id}")
async def get_deployment_status(deployment_id: str):
    """
    獲取部署狀態
    
    Args:
        deployment_id: 部署 ID
        
    Returns:
        部署狀態
    """
    return {
        "deployment_id": deployment_id,
        "status": "completed",
        "progress": 100,
        "message": "部署已完成"
    }


@app.get("/api/mcp/deployments")
async def list_deployments():
    """
    列出所有部署
    
    Returns:
        部署列表
    """
    return {
        "deployments": [],
        "total": 0
    }


def start_mock_server(host: str = "0.0.0.0", port: int = 8394):
    """
    啟動模擬服務器
    
    Args:
        host: 主機地址
        port: 端口號
    """
    logger.info(f"啟動模擬 VSIX 部署 API 服務器: http://{host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    start_mock_server()

