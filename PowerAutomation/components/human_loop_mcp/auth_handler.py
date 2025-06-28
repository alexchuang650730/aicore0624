#!/usr/bin/env python3
"""
HITL认证处理器 - 处理来自认证管理器的认证请求
通过SmartUI向用户请求认证信息
"""

import asyncio
import json
import logging
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

class HITLAuthHandler:
    """HITL认证处理器"""
    
    def __init__(self, smartui_url: str = "http://18.212.49.136"):
        self.smartui_url = smartui_url
        self.logger = logging.getLogger(__name__)
        self.pending_requests = {}  # 待处理的认证请求
        
        # 初始化Flask应用
        self.app = Flask(__name__)
        CORS(self.app)
        self._setup_routes()
    
    def _setup_routes(self):
        """设置API路由"""
        
        @self.app.route('/api/auth/request', methods=['POST'])
        def handle_auth_request_route():
            """处理认证请求的路由"""
            try:
                request_data = request.get_json()
                
                # 异步处理认证请求
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.handle_auth_request(request_data))
                loop.close()
                
                return jsonify(result)
                
            except Exception as e:
                self.logger.error(f"处理认证请求路由失败: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/auth/submit', methods=['POST'])
        def submit_auth_response_route():
            """提交认证响应的路由"""
            try:
                data = request.get_json()
                request_id = data.get('request_id')
                credentials = data.get('credentials', {})
                
                # 异步处理认证响应
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.submit_auth_response(request_id, credentials))
                loop.close()
                
                return jsonify(result)
                
            except Exception as e:
                self.logger.error(f"提交认证响应路由失败: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/auth/cancel', methods=['POST'])
        def cancel_auth_request_route():
            """取消认证请求的路由"""
            try:
                data = request.get_json()
                request_id = data.get('request_id')
                
                # 异步处理取消请求
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.cancel_auth_request(request_id))
                loop.close()
                
                return jsonify(result)
                
            except Exception as e:
                self.logger.error(f"取消认证请求路由失败: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """健康检查"""
            return jsonify({
                "status": "healthy",
                "service": "HITL Auth Handler",
                "timestamp": datetime.now().isoformat(),
                "pending_requests": len(self.pending_requests)
            })
    
    async def handle_auth_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理认证请求"""
        try:
            request_id = request_data.get("request_id")
            auth_type = request_data.get("auth_type")
            
            self.logger.info(f"收到认证请求: {auth_type} (ID: {request_id})")
            
            # 存储待处理请求
            self.pending_requests[request_id] = {
                "request_data": request_data,
                "timestamp": datetime.now(),
                "status": "pending"
            }
            
            # 发送到SmartUI
            ui_response = await self._send_to_smartui(request_data)
            
            if ui_response.get("success"):
                # 等待用户输入
                credentials = await self._wait_for_user_input(request_id)
                
                if credentials:
                    return {
                        "success": True,
                        "credentials": credentials,
                        "request_id": request_id,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": "用户取消或超时",
                        "request_id": request_id
                    }
            else:
                return {
                    "success": False,
                    "error": "无法发送到SmartUI",
                    "request_id": request_id
                }
                
        except Exception as e:
            self.logger.error(f"处理认证请求失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "request_id": request_data.get("request_id")
            }
    
    async def _send_to_smartui(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """发送认证请求到SmartUI"""
        try:
            # 构建SmartUI认证界面数据
            ui_request = {
                "type": "auth_modal",
                "auth_type": request_data["auth_type"],
                "title": f"需要{request_data['description']}",
                "description": self._generate_auth_description(request_data),
                "fields": self._generate_auth_fields(request_data),
                "security_level": request_data.get("security_level", "high"),
                "context": request_data.get("context", {}),
                "request_id": request_data["request_id"]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.smartui_url}/api/auth/modal",
                    json=ui_request
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
                        
        except Exception as e:
            self.logger.error(f"发送到SmartUI失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_auth_description(self, request_data: Dict[str, Any]) -> str:
        """生成认证描述"""
        auth_type = request_data["auth_type"]
        context = request_data.get("context", {})
        
        descriptions = {
            "manus_login": f"需要Manus平台登录信息以访问项目 {context.get('platform', 'manus.im')}",
            "github_token": f"需要GitHub个人访问令牌以进行 {context.get('purpose', '代码仓库操作')}",
            "ec2_pem_key": f"需要EC2 PEM私钥以连接服务器进行 {context.get('purpose', '远程操作')}",
            "anthropic_api_key": f"需要Anthropic API密钥以使用 {context.get('service', 'Claude AI服务')}"
        }
        
        return descriptions.get(auth_type, f"需要 {request_data['description']}")
    
    def _generate_auth_fields(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成认证字段配置"""
        auth_type = request_data["auth_type"]
        required_fields = request_data["required_fields"]
        optional_fields = request_data.get("optional_fields", [])
        
        field_configs = {
            "email": {
                "type": "email",
                "label": "邮箱地址",
                "placeholder": "请输入邮箱地址",
                "validation": "email"
            },
            "password": {
                "type": "password",
                "label": "密码",
                "placeholder": "请输入密码",
                "validation": "required"
            },
            "token": {
                "type": "password",
                "label": "访问令牌",
                "placeholder": "github_pat_...",
                "validation": "required"
            },
            "pem_content": {
                "type": "textarea",
                "label": "PEM私钥内容",
                "placeholder": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----",
                "validation": "required"
            },
            "key_name": {
                "type": "text",
                "label": "密钥名称",
                "placeholder": "例如: my-ec2-key",
                "validation": "required"
            },
            "server_ip": {
                "type": "text",
                "label": "服务器IP",
                "placeholder": "例如: 18.212.49.136",
                "validation": "ip"
            },
            "username": {
                "type": "text",
                "label": "用户名",
                "placeholder": "例如: ec2-user",
                "validation": "optional"
            },
            "api_key": {
                "type": "password",
                "label": "API密钥",
                "placeholder": "sk-ant-...",
                "validation": "required"
            }
        }
        
        fields = []
        
        # 添加必需字段
        for field in required_fields:
            if field in field_configs:
                config = field_configs[field].copy()
                config["name"] = field
                config["required"] = True
                fields.append(config)
        
        # 添加可选字段
        for field in optional_fields:
            if field in field_configs:
                config = field_configs[field].copy()
                config["name"] = field
                config["required"] = False
                fields.append(config)
        
        return fields
    
    async def _wait_for_user_input(self, request_id: str, timeout: int = 300) -> Optional[Dict[str, str]]:
        """等待用户输入"""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            if request_id in self.pending_requests:
                request_info = self.pending_requests[request_id]
                
                if request_info["status"] == "completed":
                    credentials = request_info.get("credentials")
                    del self.pending_requests[request_id]
                    return credentials
                elif request_info["status"] == "cancelled":
                    del self.pending_requests[request_id]
                    return None
            
            await asyncio.sleep(1)
        
        # 超时
        if request_id in self.pending_requests:
            del self.pending_requests[request_id]
        
        return None
    
    async def submit_auth_response(self, request_id: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """提交认证响应"""
        try:
            if request_id in self.pending_requests:
                self.pending_requests[request_id]["status"] = "completed"
                self.pending_requests[request_id]["credentials"] = credentials
                
                return {
                    "success": True,
                    "message": "认证信息已提交",
                    "request_id": request_id
                }
            else:
                return {
                    "success": False,
                    "error": "未找到对应的认证请求",
                    "request_id": request_id
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "request_id": request_id
            }
    
    async def cancel_auth_request(self, request_id: str) -> Dict[str, Any]:
        """取消认证请求"""
        try:
            if request_id in self.pending_requests:
                self.pending_requests[request_id]["status"] = "cancelled"
                
                return {
                    "success": True,
                    "message": "认证请求已取消",
                    "request_id": request_id
                }
            else:
                return {
                    "success": False,
                    "error": "未找到对应的认证请求",
                    "request_id": request_id
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "request_id": request_id
            }
    
    def run(self, host: str = "0.0.0.0", port: int = 8081, debug: bool = False):
        """运行HITL认证处理器服务"""
        self.logger.info(f"启动HITL认证处理器服务: {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建并运行HITL认证处理器
    handler = HITLAuthHandler()
    handler.run(port=8081, debug=True)

