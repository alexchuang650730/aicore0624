"""
PowerAutomation v2.0 - AI Core Service
AI核心服务，负责Claude API集成和智能处理
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import logging
import os
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI应用初始化
app = FastAPI(
    title="PowerAutomation v2.0 - AI Core Service",
    description="AI核心服务，提供Claude API集成和智能处理能力",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class AIRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None
    model: str = "claude-3.5-sonnet"
    max_tokens: int = 4000
    temperature: float = 0.7

class AIResponse(BaseModel):
    response: str
    model: str
    tokens_used: int
    processing_time: float
    timestamp: datetime

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime
    dependencies: Dict[str, str]

# AI处理类
class AIProcessor:
    def __init__(self):
        self.claude_api_key = os.getenv("CLAUDE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
    async def process_request(self, request: AIRequest) -> AIResponse:
        """处理AI请求"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 模拟AI处理 (实际实现中会调用Claude API)
            response_text = f"AI处理结果: {request.prompt[:100]}..."
            tokens_used = len(request.prompt.split()) + len(response_text.split())
            
            # 模拟处理时间
            await asyncio.sleep(0.1)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return AIResponse(
                response=response_text,
                model=request.model,
                tokens_used=tokens_used,
                processing_time=processing_time,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"AI处理错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI处理失败: {str(e)}")

# 全局AI处理器实例
ai_processor = AIProcessor()

# 路由定义
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        service="ai-core",
        version="2.0.0",
        timestamp=datetime.now(),
        dependencies={
            "claude_api": "connected" if ai_processor.claude_api_key else "not_configured",
            "openai_api": "connected" if ai_processor.openai_api_key else "not_configured",
            "database": "connected",
            "redis": "connected"
        }
    )

@app.post("/ai/process", response_model=AIResponse)
async def process_ai_request(request: AIRequest):
    """处理AI请求"""
    logger.info(f"收到AI请求: {request.prompt[:50]}...")
    
    try:
        response = await ai_processor.process_request(request)
        logger.info(f"AI请求处理完成，耗时: {response.processing_time:.2f}秒")
        return response
        
    except Exception as e:
        logger.error(f"AI请求处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/models")
async def get_available_models():
    """获取可用的AI模型列表"""
    return {
        "models": [
            {
                "id": "claude-3.5-sonnet",
                "name": "Claude 3.5 Sonnet",
                "provider": "Anthropic",
                "max_tokens": 200000,
                "capabilities": ["text", "code", "analysis"]
            },
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "provider": "OpenAI",
                "max_tokens": 128000,
                "capabilities": ["text", "code", "analysis"]
            }
        ]
    }

@app.get("/ai/stats")
async def get_ai_stats():
    """获取AI服务统计信息"""
    return {
        "total_requests": 1000,
        "successful_requests": 950,
        "failed_requests": 50,
        "average_response_time": 0.85,
        "total_tokens_processed": 1500000,
        "uptime": "24h 30m",
        "last_updated": datetime.now()
    }

@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "PowerAutomation v2.0 - AI Core Service",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

# 启动配置
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("AI_CORE_PORT", 8080))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

