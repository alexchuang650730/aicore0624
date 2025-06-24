"""
AICore 3.0 端點映射配置
整合Smartinvention Adapter MCP的API端點
"""

# Smartinvention Adapter端點映射 - 接手原EC2 API端口
SMARTINVENTION_ENDPOINTS = {
    # 原EC2 API端點 -> AICore統一處理
    "/api/sync/conversations": "smartinvention_adapter.process_conversation_sync",
    "/api/conversations/latest": "smartinvention_adapter.get_latest_conversations", 
    "/api/interventions/needed": "smartinvention_adapter.get_interventions_needed",
    "/api/health": "smartinvention_adapter.health_check",
    "/api/statistics": "smartinvention_adapter.get_statistics",
    
    # 新增本地模型端點
    "/api/local-models/connect": "smartinvention_adapter.connect_local_model",
    "/api/local-models/query": "smartinvention_adapter.query_local_model",
    "/api/local-models/status": "smartinvention_adapter.get_model_status",
    
    # 數據同步端點
    "/api/sync/start": "smartinvention_adapter.start_sync",
    "/api/sync/status": "smartinvention_adapter.get_sync_status"
}

# AICore 3.0 核心端點
AICORE_ENDPOINTS = {
    # 核心處理端點
    "/api/aicore/process": "aicore.process_request",
    "/api/aicore/status": "aicore.get_status",
    "/api/aicore/experts": "aicore.get_experts",
    "/api/aicore/tools": "aicore.get_tools",
    
    # 專家管理端點
    "/api/experts/register": "aicore.register_expert",
    "/api/experts/list": "aicore.list_experts",
    "/api/experts/query": "aicore.query_experts",
    
    # 工具管理端點
    "/api/tools/register": "aicore.register_tool",
    "/api/tools/list": "aicore.list_tools",
    "/api/tools/execute": "aicore.execute_tool"
}

# 統一端點映射
UNIFIED_ENDPOINTS = {
    **SMARTINVENTION_ENDPOINTS,
    **AICORE_ENDPOINTS
}

def get_endpoint_handler(endpoint: str) -> str:
    """獲取端點處理器"""
    return UNIFIED_ENDPOINTS.get(endpoint)

def is_smartinvention_endpoint(endpoint: str) -> bool:
    """檢查是否為Smartinvention端點"""
    return endpoint in SMARTINVENTION_ENDPOINTS

def is_aicore_endpoint(endpoint: str) -> bool:
    """檢查是否為AICore端點"""
    return endpoint in AICORE_ENDPOINTS

def get_all_endpoints() -> dict:
    """獲取所有端點映射"""
    return UNIFIED_ENDPOINTS.copy()

def get_smartinvention_endpoints() -> dict:
    """獲取Smartinvention端點映射"""
    return SMARTINVENTION_ENDPOINTS.copy()

def get_aicore_endpoints() -> dict:
    """獲取AICore端點映射"""
    return AICORE_ENDPOINTS.copy()

