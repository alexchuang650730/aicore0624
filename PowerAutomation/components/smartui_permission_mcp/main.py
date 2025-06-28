#!/usr/bin/env python3
"""
SmartUI 权限管理 MCP
提供基于角色的权限验证和管理功能
"""

import json
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from functools import wraps
import redis
from flask import Flask, request, jsonify, g
from flask_cors import CORS

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PermissionManager:
    """权限管理器"""
    
    # API Key到角色的映射
    API_KEY_ROLES = {
        'admin_qIFdydy7h_cZcop7uGNT73JRhjXQblHgWaRoDJMMz4U': 'admin',
        'dev_WqV-Kud9zmBOv_J_BtvMDJ5ZiPzibZR77o9mv-77Phg': 'developer',
        'user_Bx5z5aQbofp1fS1bNaXF-DTFnV_6X_iu6n7-7VTxi5k': 'user'
    }
    
    # 角色权限配置
    ROLE_PERMISSIONS = {
        'admin': {
            'name': '管理员',
            'description': '完全访问权限',
            'permissions': [
                'code_review', 'code_modify', 'directory_manage', 
                'code_delete', 'user_manage', 'system_config',
                'file_manage_full', 'github_manage', 'chat_unlimited',
                'file_upload', 'file_download', 'file_delete',
                'project_create', 'project_delete', 'audit_view',
                'cache_manage', 'system_monitor'
            ]
        },
        'developer': {
            'name': '开发者',
            'description': '开发功能权限',
            'permissions': [
                'code_view', 'code_edit', 'file_create', 'chat_basic',
                'github_browse', 'plugin_connect', 'file_manage_limited',
                'file_upload', 'file_download', 'project_view',
                'code_analyze', 'debug_access'
            ]
        },
        'user': {
            'name': '用户',
            'description': '基础使用权限',
            'permissions': [
                'text_input', 'file_manage_basic', 'code_view_readonly',
                'chat_basic', 'file_download', 'project_view_readonly'
            ]
        }
    }
    
    def __init__(self):
        """初始化权限管理器"""
        self.redis_client = None
        self.init_redis()
        
    def init_redis(self):
        """初始化Redis连接"""
        try:
            self.redis_client = redis.Redis(
                host='localhost', 
                port=6379, 
                db=1,  # 使用数据库1存储权限数据
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}")
            self.redis_client = None
    
    def get_role_by_api_key(self, api_key: str) -> Optional[str]:
        """根据API Key获取角色"""
        if not api_key:
            return None
            
        # 从缓存中获取
        if self.redis_client:
            try:
                cached_role = self.redis_client.get(f"api_key_role:{api_key}")
                if cached_role:
                    return cached_role
            except Exception as e:
                logger.warning(f"Redis读取失败: {e}")
        
        # 从配置中获取
        role = self.API_KEY_ROLES.get(api_key)
        
        # 缓存结果
        if role and self.redis_client:
            try:
                self.redis_client.setex(f"api_key_role:{api_key}", 3600, role)
            except Exception as e:
                logger.warning(f"Redis写入失败: {e}")
                
        return role
    
    def get_role_permissions(self, role: str) -> List[str]:
        """获取角色权限列表"""
        if role not in self.ROLE_PERMISSIONS:
            return []
        return self.ROLE_PERMISSIONS[role]['permissions']
    
    def check_permission(self, api_key: str, permission: str) -> bool:
        """检查权限"""
        role = self.get_role_by_api_key(api_key)
        if not role:
            return False
            
        permissions = self.get_role_permissions(role)
        return permission in permissions
    
    def check_permissions(self, api_key: str, permissions: List[str], require_all: bool = True) -> bool:
        """检查多个权限"""
        if require_all:
            return all(self.check_permission(api_key, perm) for perm in permissions)
        else:
            return any(self.check_permission(api_key, perm) for perm in permissions)
    
    def get_user_info(self, api_key: str) -> Dict[str, Any]:
        """获取用户信息"""
        role = self.get_role_by_api_key(api_key)
        if not role:
            return {
                'authenticated': False,
                'role': None,
                'permissions': []
            }
        
        role_info = self.ROLE_PERMISSIONS[role]
        return {
            'authenticated': True,
            'role': role,
            'role_name': role_info['name'],
            'role_description': role_info['description'],
            'permissions': role_info['permissions'],
            'api_key_hash': hashlib.sha256(api_key.encode()).hexdigest()[:16]
        }
    
    def log_access(self, api_key: str, action: str, resource: str, result: str, details: Dict = None):
        """记录访问日志"""
        role = self.get_role_by_api_key(api_key)
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'api_key_hash': hashlib.sha256(api_key.encode()).hexdigest()[:16] if api_key else None,
            'role': role,
            'action': action,
            'resource': resource,
            'result': result,
            'details': details or {},
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None
        }
        
        # 记录到日志
        logger.info(f"Access: {json.dumps(log_entry)}")
        
        # 存储到Redis
        if self.redis_client:
            try:
                log_key = f"access_log:{datetime.now().strftime('%Y%m%d')}:{int(time.time())}"
                self.redis_client.setex(log_key, 86400 * 7, json.dumps(log_entry))  # 保存7天
            except Exception as e:
                logger.warning(f"日志存储失败: {e}")
    
    def get_access_logs(self, api_key: str, days: int = 1) -> List[Dict]:
        """获取访问日志（需要audit_view权限）"""
        if not self.check_permission(api_key, 'audit_view'):
            return []
        
        if not self.redis_client:
            return []
        
        logs = []
        try:
            for day_offset in range(days):
                date = (datetime.now() - timedelta(days=day_offset)).strftime('%Y%m%d')
                pattern = f"access_log:{date}:*"
                keys = self.redis_client.keys(pattern)
                
                for key in keys:
                    log_data = self.redis_client.get(key)
                    if log_data:
                        logs.append(json.loads(log_data))
                        
        except Exception as e:
            logger.error(f"获取日志失败: {e}")
        
        return sorted(logs, key=lambda x: x['timestamp'], reverse=True)

# 全局权限管理器实例
permission_manager = PermissionManager()

def require_permission(permission: str):
    """权限装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取API Key
            api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not api_key:
                api_key = request.json.get('api_key') if request.json else None
            
            # 检查权限
            if not permission_manager.check_permission(api_key, permission):
                permission_manager.log_access(
                    api_key, 
                    f.__name__, 
                    request.path, 
                    'permission_denied',
                    {'required_permission': permission}
                )
                return jsonify({
                    'error': '权限不足',
                    'required_permission': permission,
                    'code': 'PERMISSION_DENIED'
                }), 403
            
            # 将用户信息添加到请求上下文
            g.user_info = permission_manager.get_user_info(api_key)
            g.api_key = api_key
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_permissions(permissions: List[str], require_all: bool = True):
    """多权限装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取API Key
            api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not api_key:
                api_key = request.json.get('api_key') if request.json else None
            
            # 检查权限
            if not permission_manager.check_permissions(api_key, permissions, require_all):
                permission_manager.log_access(
                    api_key, 
                    f.__name__, 
                    request.path, 
                    'permission_denied',
                    {'required_permissions': permissions, 'require_all': require_all}
                )
                return jsonify({
                    'error': '权限不足',
                    'required_permissions': permissions,
                    'require_all': require_all,
                    'code': 'PERMISSION_DENIED'
                }), 403
            
            # 将用户信息添加到请求上下文
            g.user_info = permission_manager.get_user_info(api_key)
            g.api_key = api_key
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

@app.route('/api/auth/verify', methods=['POST'])
def verify_api_key():
    """验证API Key"""
    data = request.get_json()
    api_key = data.get('api_key') if data else None
    
    if not api_key:
        api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    user_info = permission_manager.get_user_info(api_key)
    
    permission_manager.log_access(
        api_key, 
        'verify_api_key', 
        '/api/auth/verify', 
        'success' if user_info['authenticated'] else 'failed'
    )
    
    return jsonify(user_info)

@app.route('/api/auth/permissions', methods=['GET'])
def get_permissions():
    """获取当前用户权限"""
    api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_info = permission_manager.get_user_info(api_key)
    
    return jsonify({
        'permissions': user_info.get('permissions', []),
        'role': user_info.get('role'),
        'role_name': user_info.get('role_name')
    })

@app.route('/api/auth/check', methods=['POST'])
def check_permission():
    """检查特定权限"""
    data = request.get_json()
    api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
    permission = data.get('permission')
    
    if not permission:
        return jsonify({'error': '缺少权限参数'}), 400
    
    has_permission = permission_manager.check_permission(api_key, permission)
    
    return jsonify({
        'has_permission': has_permission,
        'permission': permission
    })

@app.route('/api/files/upload', methods=['POST'])
@require_permission('file_upload')
def upload_file():
    """文件上传接口"""
    # 模拟文件上传逻辑
    files = request.files.getlist('files')
    
    permission_manager.log_access(
        g.api_key, 
        'upload_file', 
        '/api/files/upload', 
        'success',
        {'file_count': len(files)}
    )
    
    return jsonify({
        'message': f'成功上传 {len(files)} 个文件',
        'files': [f.filename for f in files]
    })

@app.route('/api/files/delete', methods=['DELETE'])
@require_permission('file_delete')
def delete_file():
    """文件删除接口"""
    data = request.get_json()
    file_path = data.get('file_path')
    
    permission_manager.log_access(
        g.api_key, 
        'delete_file', 
        '/api/files/delete', 
        'success',
        {'file_path': file_path}
    )
    
    return jsonify({
        'message': f'文件 {file_path} 删除成功'
    })

@app.route('/api/code/analyze', methods=['POST'])
@require_permissions(['code_view', 'code_analyze'], require_all=False)
def analyze_code():
    """代码分析接口"""
    data = request.get_json()
    code_content = data.get('code_content', '')
    
    # 模拟代码分析
    analysis_result = {
        'summary': '代码分析完成',
        'quality_score': 8.5,
        'suggestions': [
            '建议添加错误处理',
            '可以优化变量命名',
            '建议添加注释'
        ],
        'complexity': 'medium',
        'lines_of_code': len(code_content.split('\n'))
    }
    
    permission_manager.log_access(
        g.api_key, 
        'analyze_code', 
        '/api/code/analyze', 
        'success',
        {'code_length': len(code_content)}
    )
    
    return jsonify(analysis_result)

@app.route('/api/admin/logs', methods=['GET'])
@require_permission('audit_view')
def get_logs():
    """获取访问日志"""
    days = request.args.get('days', 1, type=int)
    logs = permission_manager.get_access_logs(g.api_key, days)
    
    return jsonify({
        'logs': logs,
        'total': len(logs)
    })

@app.route('/api/admin/users', methods=['GET'])
@require_permission('user_manage')
def get_users():
    """获取用户列表"""
    users = []
    for api_key, role in permission_manager.API_KEY_ROLES.items():
        role_info = permission_manager.ROLE_PERMISSIONS[role]
        users.append({
            'api_key_hash': hashlib.sha256(api_key.encode()).hexdigest()[:16],
            'role': role,
            'role_name': role_info['name'],
            'permissions_count': len(role_info['permissions'])
        })
    
    return jsonify({'users': users})

@app.route('/api/system/status', methods=['GET'])
@require_permission('system_monitor')
def system_status():
    """系统状态"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'redis_connected': permission_manager.redis_client is not None,
        'active_roles': list(permission_manager.ROLE_PERMISSIONS.keys())
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': 'smartui-permission-mcp',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("启动 SmartUI 权限管理 MCP")
    app.run(host='0.0.0.0', port=8081, debug=False)

