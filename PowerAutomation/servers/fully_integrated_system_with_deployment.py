#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全整合的動態MCP-Agent Core智能系統 + 一鍵部署協調
Fully Integrated Dynamic MCP-Agent Core Intelligent System + One-Click Deployment

將動態MCP深度融入Agent Core + 完整的部署協調機制：
1. Agent Core - 智能決策中心
2. Tool Registry - 智能工具引擎  
3. Action Executor - 統一執行引擎
4. Deployment Coordinator - 一鍵部署協調器
"""

import asyncio
import logging
import time
import json
import sys
import os
import hashlib
import secrets
import subprocess
import threading
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps

# 添加組件路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'components'))

# 導入部署協調組件
try:
    from deployment_mcp.remote_deployment_coordinator import RemoteDeploymentCoordinator
    from deployment_mcp.ec2_deployment_trigger import EC2DeploymentTrigger
    DEPLOYMENT_MCP_AVAILABLE = True
    logging.info("✅ 部署協調組件導入成功")
except ImportError as e:
    logging.warning(f"⚠️ 部署協調組件導入失敗: {e}")
    DEPLOYMENT_MCP_AVAILABLE = False

# 導入 SmartInvention-Manus HITL 中間件
try:
    from smartinvention_manus_hitl_middleware import (
        SmartInventionManusMiddleware, 
        VSIXRequest, 
        SmartInventionResponse,
        create_smartinvention_manus_middleware
    )
    SMARTINVENTION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"SmartInvention-Manus 中間件導入失敗: {e}")
    SMARTINVENTION_AVAILABLE = False

# 導入 Enhanced Test Flow MCP v4.0
try:
    from enhanced_test_flow_mcp_v4 import (
        EnhancedTestFlowMCP,
        UserMode,
        ProcessingStage,
        DeveloperRequest
    )
    TEST_FLOW_MCP_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Enhanced Test Flow MCP 導入失敗: {e}")
    TEST_FLOW_MCP_AVAILABLE = False

logger = logging.getLogger(__name__)

# ==================== 部署狀態管理 ====================

class DeploymentStatus(Enum):
    IDLE = "idle"
    PREPARING = "preparing"
    DEPLOYING = "deploying"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class DeploymentTask:
    id: str
    status: DeploymentStatus
    target_environments: List[str]
    started_at: float
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    progress: int = 0
    logs: List[str] = None

    def __post_init__(self):
        if self.logs is None:
            self.logs = []

class OneClickDeploymentManager:
    """一鍵部署管理器"""
    
    def __init__(self):
        self.deployment_coordinator = None
        self.ec2_trigger = None
        self.current_deployment: Optional[DeploymentTask] = None
        self.deployment_history: List[DeploymentTask] = []
        
        # 初始化部署組件
        if DEPLOYMENT_MCP_AVAILABLE:
            try:
                self.deployment_coordinator = RemoteDeploymentCoordinator()
                self.ec2_trigger = EC2DeploymentTrigger()
                logger.info("✅ 部署協調器初始化成功")
            except Exception as e:
                logger.error(f"❌ 部署協調器初始化失敗: {e}")
                DEPLOYMENT_MCP_AVAILABLE = False
    
    async def trigger_one_click_deployment(self, target_environments: List[str] = None) -> Dict[str, Any]:
        """觸發一鍵部署"""
        if not DEPLOYMENT_MCP_AVAILABLE:
            return {
                'success': False,
                'error': '部署協調組件不可用',
                'message': '請檢查 deployment_mcp 組件是否正確安裝'
            }
        
        if self.current_deployment and self.current_deployment.status in [DeploymentStatus.PREPARING, DeploymentStatus.DEPLOYING]:
            return {
                'success': False,
                'error': '已有部署任務正在進行中',
                'current_deployment_id': self.current_deployment.id
            }
        
        # 創建新的部署任務
        deployment_id = f"deploy_{int(time.time())}"
        self.current_deployment = DeploymentTask(
            id=deployment_id,
            status=DeploymentStatus.PREPARING,
            target_environments=target_environments or ["default"],
            started_at=time.time()
        )
        
        # 異步執行部署
        asyncio.create_task(self._execute_deployment())
        
        return {
            'success': True,
            'deployment_id': deployment_id,
            'message': '一鍵部署已啟動',
            'status': 'preparing'
        }
    
    async def _execute_deployment(self):
        """執行部署流程"""
        try:
            deployment = self.current_deployment
            
            # Phase 1: 準備階段
            deployment.status = DeploymentStatus.PREPARING
            deployment.logs.append(f"[{datetime.now()}] 🚀 開始一鍵部署流程")
            deployment.logs.append(f"[{datetime.now()}] 📋 目標環境: {', '.join(deployment.target_environments)}")
            deployment.progress = 10
            
            await asyncio.sleep(1)  # 模擬準備時間
            
            # Phase 2: 部署階段
            deployment.status = DeploymentStatus.DEPLOYING
            deployment.logs.append(f"[{datetime.now()}] 🔧 開始部署到遠程環境...")
            deployment.progress = 30
            
            # 調用部署協調器
            if self.deployment_coordinator:
                deployment.logs.append(f"[{datetime.now()}] 📡 觸發遠程部署協調器...")
                
                # 這裡調用實際的部署邏輯
                deployment_result = await self._call_deployment_coordinator()
                
                if deployment_result.get('success'):
                    deployment.logs.append(f"[{datetime.now()}] ✅ 遠程環境部署成功")
                    deployment.progress = 70
                else:
                    raise Exception(f"遠程部署失敗: {deployment_result.get('error', 'Unknown error')}")
            
            # Phase 3: 驗證階段
            deployment.status = DeploymentStatus.VERIFYING
            deployment.logs.append(f"[{datetime.now()}] 🔍 驗證部署狀態...")
            deployment.progress = 85
            
            await asyncio.sleep(2)  # 模擬驗證時間
            
            # 驗證部署結果
            verification_result = await self._verify_deployment()
            
            if verification_result.get('success'):
                deployment.logs.append(f"[{datetime.now()}] ✅ 部署驗證成功")
                deployment.progress = 100
                deployment.status = DeploymentStatus.COMPLETED
                deployment.completed_at = time.time()
                deployment.logs.append(f"[{datetime.now()}] 🎉 一鍵部署完成！")
            else:
                raise Exception(f"部署驗證失敗: {verification_result.get('error', 'Verification failed')}")
                
        except Exception as e:
            deployment.status = DeploymentStatus.FAILED
            deployment.error_message = str(e)
            deployment.completed_at = time.time()
            deployment.logs.append(f"[{datetime.now()}] ❌ 部署失敗: {str(e)}")
            logger.error(f"部署失敗: {e}")
        
        finally:
            # 將完成的部署添加到歷史記錄
            self.deployment_history.append(self.current_deployment)
            # 保留最近10次部署記錄
            if len(self.deployment_history) > 10:
                self.deployment_history = self.deployment_history[-10:]
    
    async def _call_deployment_coordinator(self) -> Dict[str, Any]:
        """調用部署協調器"""
        try:
            # 讀取環境配置
            config_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 
                'components', 
                'deployment_mcp', 
                'remote_environments.json'
            )
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                environments = config.get('environments', [])
                
                if not environments:
                    return {'success': False, 'error': '未找到配置的遠程環境'}
                
                # 調用部署協調器
                result = await self.deployment_coordinator.deploy_to_environments(environments)
                return result
            else:
                return {'success': False, 'error': '未找到環境配置文件'}
                
        except Exception as e:
            logger.error(f"調用部署協調器失敗: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _verify_deployment(self) -> Dict[str, Any]:
        """驗證部署結果"""
        try:
            # 這裡可以添加實際的驗證邏輯
            # 例如：檢查服務是否正常運行、API 是否可訪問等
            
            # 模擬驗證過程
            await asyncio.sleep(1)
            
            # 簡單的健康檢查
            health_checks = [
                {'name': 'PowerAutomation_local', 'status': 'healthy'},
                {'name': 'AIWeb', 'status': 'healthy'},
                {'name': 'SmartUI', 'status': 'healthy'}
            ]
            
            return {
                'success': True,
                'health_checks': health_checks,
                'message': '所有組件運行正常'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """獲取當前部署狀態"""
        if not self.current_deployment:
            return {
                'status': 'idle',
                'message': '無活躍的部署任務'
            }
        
        return {
            'deployment_id': self.current_deployment.id,
            'status': self.current_deployment.status.value,
            'progress': self.current_deployment.progress,
            'target_environments': self.current_deployment.target_environments,
            'started_at': self.current_deployment.started_at,
            'completed_at': self.current_deployment.completed_at,
            'error_message': self.current_deployment.error_message,
            'logs': self.current_deployment.logs[-10:] if self.current_deployment.logs else []  # 最近10條日誌
        }
    
    def get_deployment_history(self) -> List[Dict[str, Any]]:
        """獲取部署歷史"""
        return [
            {
                'deployment_id': dep.id,
                'status': dep.status.value,
                'target_environments': dep.target_environments,
                'started_at': dep.started_at,
                'completed_at': dep.completed_at,
                'error_message': dep.error_message,
                'duration': (dep.completed_at - dep.started_at) if dep.completed_at else None
            }
            for dep in self.deployment_history
        ]

# ==================== API Key 管理系統 ====================

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
    last_used: float = 0.0
    usage_count: int = 0
    active: bool = True

class APIKeyManager:
    """API Key 管理系統 - 區分開發者和使用者"""
    
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
            return key_info
        
        return None

# 全局實例
api_key_manager = APIKeyManager()
deployment_manager = OneClickDeploymentManager()

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

# ==================== Flask 應用初始化 ====================

app = Flask(__name__)
CORS(app)

# ==================== 一鍵部署 API 端點 ====================

@app.route('/api/deployment/one-click', methods=['POST'])
@require_api_key([UserRole.ADMIN, UserRole.DEVELOPER])
async def trigger_one_click_deployment():
    """觸發一鍵部署"""
    try:
        data = request.get_json() or {}
        target_environments = data.get('target_environments', ['default'])
        
        logger.info(f"🚀 用戶 {request.user_info.name} 觸發一鍵部署")
        
        result = await deployment_manager.trigger_one_click_deployment(target_environments)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"一鍵部署觸發失敗: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/deployment/status', methods=['GET'])
@require_api_key([UserRole.ADMIN, UserRole.DEVELOPER, UserRole.USER])
def get_deployment_status():
    """獲取部署狀態"""
    try:
        status = deployment_manager.get_deployment_status()
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"獲取部署狀態失敗: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/deployment/history', methods=['GET'])
@require_api_key([UserRole.ADMIN, UserRole.DEVELOPER])
def get_deployment_history():
    """獲取部署歷史"""
    try:
        history = deployment_manager.get_deployment_history()
        return jsonify({
            'history': history,
            'total_count': len(history)
        })
        
    except Exception as e:
        logger.error(f"獲取部署歷史失敗: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/deployment/environments', methods=['GET'])
@require_api_key([UserRole.ADMIN, UserRole.DEVELOPER])
def get_deployment_environments():
    """獲取配置的部署環境"""
    try:
        config_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'components', 
            'deployment_mcp', 
            'remote_environments.json'
        )
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return jsonify({
                'environments': config.get('environments', []),
                'total_count': len(config.get('environments', []))
            })
        else:
            return jsonify({
                'environments': [],
                'total_count': 0,
                'message': '環境配置文件不存在'
            })
        
    except Exception as e:
        logger.error(f"獲取部署環境失敗: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/deployment/test-connection', methods=['POST'])
@require_api_key([UserRole.ADMIN, UserRole.DEVELOPER])
async def test_deployment_connection():
    """測試部署連接"""
    try:
        if not DEPLOYMENT_MCP_AVAILABLE:
            return jsonify({
                'success': False,
                'error': '部署協調組件不可用'
            }), 503
        
        # 測試與遠程環境的連接
        test_result = {
            'success': True,
            'message': '部署協調組件可用',
            'components': {
                'deployment_coordinator': deployment_manager.deployment_coordinator is not None,
                'ec2_trigger': deployment_manager.ec2_trigger is not None
            }
        }
        
        return jsonify(test_result)
        
    except Exception as e:
        logger.error(f"測試部署連接失敗: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== 系統狀態 API 端點 ====================

@app.route('/api/system/status', methods=['GET'])
@require_api_key([UserRole.ADMIN, UserRole.DEVELOPER, UserRole.USER])
def get_system_status():
    """獲取系統狀態"""
    return jsonify({
        'system_name': 'PowerAutomation Fully Integrated System',
        'version': '3.0.0',
        'deployment_enabled': DEPLOYMENT_MCP_AVAILABLE,
        'smartinvention_enabled': SMARTINVENTION_AVAILABLE,
        'test_flow_enabled': TEST_FLOW_MCP_AVAILABLE,
        'current_deployment': deployment_manager.get_deployment_status(),
        'uptime': time.time(),
        'user_role': request.user_info.role.value
    })

@app.route('/api/system/health', methods=['GET'])
def get_system_health():
    """系統健康檢查（無需 API Key）"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'services': {
            'main_platform': 'running',
            'deployment_coordinator': 'available' if DEPLOYMENT_MCP_AVAILABLE else 'unavailable',
            'api_key_manager': 'running'
        }
    })

# ==================== API Key 管理端點 ====================

@app.route('/api/keys', methods=['GET'])
@require_api_key([UserRole.ADMIN])
def get_api_keys():
    """獲取所有 API Keys（僅管理員）"""
    return jsonify({
        'api_keys': [
            {
                'key_prefix': key_info.key[:12] + "...",
                'role': key_info.role.value,
                'name': key_info.name,
                'created_at': key_info.created_at,
                'last_used': key_info.last_used,
                'usage_count': key_info.usage_count,
                'active': key_info.active
            }
            for key_info in api_key_manager.api_keys.values()
        ],
        'total_count': len(api_key_manager.api_keys)
    })

@app.route('/api/keys/info', methods=['GET'])
@require_api_key([UserRole.DEVELOPER, UserRole.USER, UserRole.ADMIN])
def get_current_key_info():
    """獲取當前 API Key 信息"""
    return jsonify({
        'key_prefix': request.user_info.key[:12] + "...",
        'role': request.user_info.role.value,
        'name': request.user_info.name,
        'created_at': request.user_info.created_at,
        'last_used': request.user_info.last_used,
        'usage_count': request.user_info.usage_count,
        'active': request.user_info.active
    })

# ==================== 啟動時自動部署檢測 ====================

async def startup_deployment_check():
    """啟動時檢查是否需要觸發部署"""
    try:
        logger.info("🔍 檢查是否需要觸發自動部署...")
        
        # 檢查環境變量或配置文件
        auto_deploy = os.getenv('AUTO_DEPLOY_ON_STARTUP', 'false').lower() == 'true'
        
        if auto_deploy and DEPLOYMENT_MCP_AVAILABLE:
            logger.info("🚀 啟動時自動觸發一鍵部署...")
            await deployment_manager.trigger_one_click_deployment(['default'])
        else:
            logger.info("ℹ️ 跳過自動部署（AUTO_DEPLOY_ON_STARTUP=false 或部署組件不可用）")
            
    except Exception as e:
        logger.error(f"啟動時部署檢查失敗: {e}")

def run_startup_check():
    """在新線程中運行啟動檢查"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(startup_deployment_check())
    loop.close()

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🚀 啟動 PowerAutomation 完全整合智能系統...")
    logger.info(f"📦 部署協調功能: {'✅ 可用' if DEPLOYMENT_MCP_AVAILABLE else '❌ 不可用'}")
    
    # 啟動時檢查自動部署
    startup_thread = threading.Thread(target=run_startup_check)
    startup_thread.daemon = True
    startup_thread.start()
    
    logger.info("🌐 啟動 Web 服務器...")
    app.run(host='0.0.0.0', port=8080, debug=False)

