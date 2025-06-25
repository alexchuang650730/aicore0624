#!/usr/bin/env python3.11
"""
修復版本的測試服務器 - 專門用於測試 test_flow_mcp 集成
"""

import sys
import os
import time
import logging
import secrets
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from functools import wraps
import asyncio

from flask import Flask, request, jsonify

# 添加路徑
sys.path.append('/home/ubuntu/aicore0624/PowerAutomation')
sys.path.append('/home/ubuntu/aicore0624/PowerAutomation/components')

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 用戶角色和數據結構 ====================

class UserRole(Enum):
    DEVELOPER = "developer"
    USER = "user"
    ADMIN = "admin"

@dataclass
class APIKeyInfo:
    key: str
    role: UserRole
    name: str
    created_at: float
    last_used: Optional[float] = None
    usage_count: int = 0
    active: bool = True

@dataclass
class DeveloperRequest:
    request_id: str
    content: str
    context: Dict[str, Any]
    user_mode: str
    timestamp: float

# ==================== API Key 管理器 ====================

class APIKeyManager:
    def __init__(self):
        self.api_keys: Dict[str, APIKeyInfo] = {}
        self._initialize_default_keys()
    
    def _initialize_default_keys(self):
        """初始化默認 API Keys"""
        # 開發者 API Key
        dev_key = "dev_" + secrets.token_urlsafe(32)
        self.api_keys[dev_key] = APIKeyInfo(
            key=dev_key,
            role=UserRole.DEVELOPER,
            name="Default Developer",
            created_at=time.time()
        )
        
        # 使用者 API Key
        user_key = "user_" + secrets.token_urlsafe(32)
        self.api_keys[user_key] = APIKeyInfo(
            key=user_key,
            role=UserRole.USER,
            name="Default User",
            created_at=time.time()
        )
        
        # 管理員 API Key
        admin_key = "admin_" + secrets.token_urlsafe(32)
        self.api_keys[admin_key] = APIKeyInfo(
            key=admin_key,
            role=UserRole.ADMIN,
            name="System Admin",
            created_at=time.time()
        )
        
        logger.info(f"✅ 初始化 API Keys:")
        logger.info(f"   開發者 Key: {dev_key}")
        logger.info(f"   使用者 Key: {user_key}")
        logger.info(f"   管理員 Key: {admin_key}")
    
    def validate_api_key(self, api_key: str) -> Optional[APIKeyInfo]:
        """驗證 API Key 並返回用戶信息"""
        if not api_key:
            return None
        
        key_info = self.api_keys.get(api_key)
        if key_info and key_info.active:
            # 更新使用統計
            key_info.last_used = time.time()
            key_info.usage_count += 1
            logger.info(f"✅ API Key 驗證成功: {key_info.name} ({key_info.role.value})")
            return key_info
        
        logger.warning(f"❌ API Key 驗證失敗: {api_key[:20]}...")
        return None

# ==================== 模擬 test_flow_mcp ====================

class MockTestFlowMCP:
    """模擬的 test_flow_mcp 組件"""
    
    async def process_developer_request(self, developer_request: DeveloperRequest) -> Dict[str, Any]:
        """處理開發者請求"""
        logger.info(f"🔧 test_flow_mcp 處理開發者請求: {developer_request.content}")
        
        # 模擬四階段處理流程
        processing_stages = [
            "需求同步引擎 (Requirement Sync Engine)",
            "比較分析引擎 (Comparison Analysis Engine)", 
            "評估報告生成器 (Evaluation Report Generator)",
            "Code Fix Adapter"
        ]
        
        # 模擬分析結果
        analysis = {
            "requirement_sync": {
                "requirement_id": f"req_{int(time.time())}",
                "sync_status": "completed",
                "manus_integration": True
            },
            "comparison_analysis": {
                "current_system_state": "analyzed",
                "manus_standard_comparison": "completed",
                "differences_identified": 3,
                "improvement_areas": ["code_quality", "test_coverage", "documentation"]
            },
            "evaluation_report": {
                "executive_summary": "系統需求分析完成，發現3個改進領域",
                "detailed_findings": [
                    "代碼質量需要提升",
                    "測試覆蓋率不足", 
                    "文檔需要更新"
                ],
                "priority_recommendations": ["增加單元測試", "重構核心模塊", "更新API文檔"]
            }
        }
        
        # 模擬代碼修復建議
        code_fixes = [
            {
                "file_path": "/path/to/component.py",
                "issue": "缺少錯誤處理",
                "fix_type": "error_handling",
                "suggested_code": "try-except block implementation"
            },
            {
                "file_path": "/path/to/test.py", 
                "issue": "測試覆蓋率不足",
                "fix_type": "test_enhancement",
                "suggested_code": "additional test cases"
            }
        ]
        
        return {
            "request_id": developer_request.request_id,
            "success": True,
            "analysis": analysis,
            "recommendations": [
                "實施建議的代碼修復",
                "增加測試覆蓋率",
                "更新系統文檔",
                "進行代碼審查"
            ],
            "code_fixes": code_fixes,
            "evaluation_report": {
                "overall_score": 7.5,
                "areas_evaluated": ["functionality", "maintainability", "testability"],
                "improvement_potential": "high"
            },
            "processing_stages": processing_stages,
            "execution_time": 2.5,
            "confidence": 0.85
        }

# ==================== Flask 應用 ====================

app = Flask(__name__)
api_key_manager = APIKeyManager()
test_flow_mcp = MockTestFlowMCP()

def require_api_key(allowed_roles: List[UserRole] = None):
    """API Key 驗證裝飾器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 從 Header 或 Query Parameter 獲取 API Key
            api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
            
            if not api_key:
                return jsonify({'error': 'API Key is required'}), 401
            
            # 驗證 API Key
            key_info = api_key_manager.validate_api_key(api_key)
            if not key_info:
                return jsonify({'error': 'Invalid API Key'}), 401
            
            # 檢查角色權限
            if allowed_roles and key_info.role not in allowed_roles:
                return jsonify({'error': f'Access denied. Required roles: {[r.value for r in allowed_roles]}'}), 403
            
            # 將用戶信息添加到請求上下文
            request.user_info = key_info
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/api/status', methods=['GET'])
def get_status():
    """獲取系統狀態"""
    return jsonify({
        'system_type': 'test_flow_mcp_integration_server',
        'test_flow_mcp_enabled': True,
        'api_keys_count': len(api_key_manager.api_keys),
        'uptime_seconds': time.time() - start_time,
        'features': [
            'test_flow_mcp_integration',
            'api_key_authentication',
            'developer_mode_support',
            'requirement_analysis'
        ]
    })

@app.route('/api/process', methods=['POST'])
@require_api_key([UserRole.DEVELOPER, UserRole.USER, UserRole.ADMIN])
def process_request():
    """處理用戶請求"""
    try:
        data = request.get_json()
        user_request = data.get('request', '')
        context = data.get('context', {})
        
        user_info = request.user_info
        logger.info(f"🎯 處理請求 ({user_info.role.value}): {user_request[:100]}...")
        
        if user_info.role == UserRole.DEVELOPER:
            # 開發者角色 - 使用 test_flow_mcp
            developer_request = DeveloperRequest(
                request_id=f"dev_{int(time.time())}",
                content=user_request,
                context=context,
                user_mode="developer",
                timestamp=time.time()
            )
            
            # 使用 asyncio 運行異步方法
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                test_flow_response = loop.run_until_complete(
                    test_flow_mcp.process_developer_request(developer_request)
                )
            finally:
                loop.close()
            
            return jsonify({
                'request_id': test_flow_response.get('request_id'),
                'success': test_flow_response.get('success', True),
                'result': {
                    'test_flow_analysis': test_flow_response.get('analysis', {}),
                    'recommendations': test_flow_response.get('recommendations', []),
                    'code_fixes': test_flow_response.get('code_fixes', []),
                    'evaluation_report': test_flow_response.get('evaluation_report', {}),
                    'processing_stages': test_flow_response.get('processing_stages', [])
                },
                'execution_time': test_flow_response.get('execution_time', 0.0),
                'tools_used': ['test_flow_mcp', 'requirement_sync', 'comparison_analysis', 'code_fix_adapter'],
                'confidence': test_flow_response.get('confidence', 0.8),
                'metadata': {
                    'system_type': 'test_flow_mcp_integrated',
                    'user_role': 'developer',
                    'processing_mode': 'developer_mode',
                    'test_flow_enabled': True,
                    'stages_completed': len(test_flow_response.get('processing_stages', [])),
                    'fixes_generated': len(test_flow_response.get('code_fixes', []))
                }
            })
        else:
            # 使用者角色 - 模擬 SmartInvention 流程
            return jsonify({
                'request_id': f"user_{int(time.time())}",
                'success': True,
                'result': {
                    'primary_response': {
                        'type': 'smartinvention_response',
                        'content': f'SmartInvention 處理結果: {user_request}'
                    },
                    'smartinvention_analysis': {
                        'conversation_history': None,
                        'incremental_comparison': None,
                        'hitl_review': None,
                        'final_recommendations': ['建議1', '建議2']
                    }
                },
                'execution_time': 1.0,
                'tools_used': ['smartinvention_mcp'],
                'confidence': 0.7,
                'metadata': {
                    'system_type': 'smartinvention_integrated',
                    'user_role': 'user',
                    'hitl_enabled': True
                }
            })
            
    except Exception as e:
        logger.error(f"❌ 請求處理失敗: {e}")
        return jsonify({
            'success': False,
            'error': f"請求處理失敗: {str(e)}"
        }), 500

@app.route('/api/keys', methods=['GET'])
@require_api_key([UserRole.ADMIN])
def get_api_keys():
    """獲取所有 API Keys（僅管理員）"""
    return jsonify({
        'api_keys': [
            {
                'key': key,
                'role': info.role.value,
                'name': info.name,
                'created_at': info.created_at,
                'usage_count': info.usage_count,
                'active': info.active
            }
            for key, info in api_key_manager.api_keys.items()
        ],
        'total_count': len(api_key_manager.api_keys)
    })

if __name__ == '__main__':
    start_time = time.time()
    logger.info("🚀 啟動 test_flow_mcp 集成測試服務器...")
    logger.info("📡 服務器將運行在 http://127.0.0.1:8080")
    
    app.run(host='0.0.0.0', port=8080, debug=False)

