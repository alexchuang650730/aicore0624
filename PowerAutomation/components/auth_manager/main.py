#!/usr/bin/env python3
"""
认证管理器 - 统一的认证信息管理系统
当认证信息为空时自动触发Human-in-the-Loop (HITL) MCP
"""

import os
import json
import asyncio
import logging
import aiohttp
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class AuthType(Enum):
    """认证类型枚举"""
    MANUS_LOGIN = "manus_login"
    GITHUB_TOKEN = "github_token"
    EC2_PEM_KEY = "ec2_pem_key"
    ANTHROPIC_API_KEY = "anthropic_api_key"
    OPENAI_API_KEY = "openai_api_key"
    REDIS_PASSWORD = "redis_password"
    DATABASE_PASSWORD = "database_password"

@dataclass
class AuthRequest:
    """认证请求数据模型"""
    auth_type: AuthType
    description: str
    required_fields: List[str]
    optional_fields: List[str] = None
    security_level: str = "high"  # low, medium, high
    expires_in: int = 3600  # 秒
    context: Dict[str, Any] = None

@dataclass
class AuthResponse:
    """认证响应数据模型"""
    auth_type: AuthType
    credentials: Dict[str, str]
    timestamp: datetime
    expires_at: datetime
    user_id: str

class AuthManager:
    """统一认证管理器"""
    
    def __init__(self, hitl_mcp_url: str = "http://localhost:8081"):
        self.hitl_mcp_url = hitl_mcp_url
        self.logger = logging.getLogger(__name__)
        self.auth_cache = {}  # 临时认证缓存
        
        # 认证配置
        self.auth_configs = {
            AuthType.MANUS_LOGIN: AuthRequest(
                auth_type=AuthType.MANUS_LOGIN,
                description="Manus平台登录认证",
                required_fields=["email", "password"],
                security_level="high",
                context={"platform": "manus.im", "purpose": "项目数据访问"}
            ),
            AuthType.GITHUB_TOKEN: AuthRequest(
                auth_type=AuthType.GITHUB_TOKEN,
                description="GitHub个人访问令牌",
                required_fields=["token"],
                security_level="high",
                context={"scope": "repo", "purpose": "代码仓库访问"}
            ),
            AuthType.EC2_PEM_KEY: AuthRequest(
                auth_type=AuthType.EC2_PEM_KEY,
                description="Amazon EC2 PEM私钥",
                required_fields=["pem_content", "key_name"],
                optional_fields=["server_ip", "username"],
                security_level="high",
                context={"purpose": "服务器连接"}
            ),
            AuthType.ANTHROPIC_API_KEY: AuthRequest(
                auth_type=AuthType.ANTHROPIC_API_KEY,
                description="Anthropic Claude API密钥",
                required_fields=["api_key"],
                security_level="high",
                context={"service": "Claude AI", "purpose": "AI分析服务"}
            )
        }
    
    async def get_auth(self, auth_type: AuthType, context: Dict = None) -> Optional[Dict[str, str]]:
        """获取认证信息，如果为空则触发HITL"""
        try:
            # 1. 首先检查环境变量
            credentials = self._check_environment_vars(auth_type)
            if credentials and self._validate_credentials(auth_type, credentials):
                self.logger.info(f"从环境变量获取到 {auth_type.value} 认证信息")
                return credentials
            
            # 2. 检查缓存
            cached_auth = self._check_auth_cache(auth_type)
            if cached_auth and not self._is_expired(cached_auth):
                self.logger.info(f"从缓存获取到 {auth_type.value} 认证信息")
                return cached_auth.credentials
            
            # 3. 认证信息为空，触发HITL
            self.logger.warning(f"{auth_type.value} 认证信息为空，触发HITL请求")
            return await self._trigger_hitl_auth_request(auth_type, context)
            
        except Exception as e:
            self.logger.error(f"获取认证信息失败: {e}")
            return None
    
    def _check_environment_vars(self, auth_type: AuthType) -> Optional[Dict[str, str]]:
        """检查环境变量中的认证信息"""
        env_mappings = {
            AuthType.MANUS_LOGIN: {
                "email": "MANUS_LOGIN_EMAIL",
                "password": "MANUS_LOGIN_PASSWORD"
            },
            AuthType.GITHUB_TOKEN: {
                "token": "GITHUB_TOKEN"
            },
            AuthType.EC2_PEM_KEY: {
                "pem_content": "EC2_PEM_CONTENT",
                "key_name": "EC2_KEY_NAME",
                "server_ip": "EC2_SERVER_IP",
                "username": "EC2_USERNAME"
            },
            AuthType.ANTHROPIC_API_KEY: {
                "api_key": "ANTHROPIC_API_KEY"
            }
        }
        
        if auth_type not in env_mappings:
            return None
        
        credentials = {}
        mapping = env_mappings[auth_type]
        
        for field, env_var in mapping.items():
            value = os.getenv(env_var)
            if value:
                credentials[field] = value
        
        # 检查必需字段
        config = self.auth_configs[auth_type]
        for required_field in config.required_fields:
            if required_field not in credentials or not credentials[required_field]:
                return None
        
        return credentials if credentials else None
    
    def _validate_credentials(self, auth_type: AuthType, credentials: Dict[str, str]) -> bool:
        """验证认证信息格式"""
        try:
            if auth_type == AuthType.MANUS_LOGIN:
                email = credentials.get("email", "")
                password = credentials.get("password", "")
                return "@" in email and len(password) >= 6
            
            elif auth_type == AuthType.GITHUB_TOKEN:
                token = credentials.get("token", "")
                return token.startswith("github_pat_") or token.startswith("ghp_")
            
            elif auth_type == AuthType.EC2_PEM_KEY:
                pem_content = credentials.get("pem_content", "")
                return "BEGIN" in pem_content and "PRIVATE KEY" in pem_content
            
            elif auth_type == AuthType.ANTHROPIC_API_KEY:
                api_key = credentials.get("api_key", "")
                return api_key.startswith("sk-ant-")
            
            return True
            
        except Exception as e:
            self.logger.error(f"认证信息验证失败: {e}")
            return False
    
    def _check_auth_cache(self, auth_type: AuthType) -> Optional[AuthResponse]:
        """检查认证缓存"""
        cache_key = f"auth_{auth_type.value}"
        return self.auth_cache.get(cache_key)
    
    def _is_expired(self, auth_response: AuthResponse) -> bool:
        """检查认证是否过期"""
        return datetime.now() > auth_response.expires_at
    
    async def _trigger_hitl_auth_request(self, auth_type: AuthType, context: Dict = None) -> Optional[Dict[str, str]]:
        """触发HITL认证请求"""
        try:
            config = self.auth_configs[auth_type]
            
            # 构建HITL请求
            hitl_request = {
                "type": "auth_request",
                "auth_type": auth_type.value,
                "description": config.description,
                "required_fields": config.required_fields,
                "optional_fields": config.optional_fields or [],
                "security_level": config.security_level,
                "context": {**(config.context or {}), **(context or {})},
                "timestamp": datetime.now().isoformat(),
                "request_id": f"auth_{auth_type.value}_{int(datetime.now().timestamp())}"
            }
            
            # 发送到HITL MCP
            response = await self._send_hitl_request(hitl_request)
            
            if response and response.get("success"):
                credentials = response.get("credentials", {})
                
                # 验证返回的认证信息
                if self._validate_credentials(auth_type, credentials):
                    # 缓存认证信息
                    self._cache_auth_response(auth_type, credentials, config.expires_in)
                    return credentials
                else:
                    self.logger.error(f"HITL返回的认证信息验证失败: {auth_type.value}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"HITL认证请求失败: {e}")
            return None
    
    async def _send_hitl_request(self, request_data: Dict) -> Optional[Dict]:
        """发送请求到HITL MCP"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hitl_mcp_url}/api/auth/request",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=300)  # 5分钟超时
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"HITL请求失败: {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"发送HITL请求异常: {e}")
            return None
    
    def _cache_auth_response(self, auth_type: AuthType, credentials: Dict[str, str], expires_in: int):
        """缓存认证响应"""
        cache_key = f"auth_{auth_type.value}"
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        auth_response = AuthResponse(
            auth_type=auth_type,
            credentials=credentials,
            timestamp=datetime.now(),
            expires_at=expires_at,
            user_id="current_user"  # 可以从上下文获取
        )
        
        self.auth_cache[cache_key] = auth_response
        self.logger.info(f"认证信息已缓存: {auth_type.value}, 过期时间: {expires_at}")
    
    def clear_auth_cache(self, auth_type: AuthType = None):
        """清除认证缓存"""
        if auth_type:
            cache_key = f"auth_{auth_type.value}"
            if cache_key in self.auth_cache:
                del self.auth_cache[cache_key]
                self.logger.info(f"已清除认证缓存: {auth_type.value}")
        else:
            self.auth_cache.clear()
            self.logger.info("已清除所有认证缓存")

# 全局认证管理器实例
auth_manager = AuthManager()

# 便捷函数
async def get_manus_auth(context: Dict = None) -> Optional[Dict[str, str]]:
    """获取Manus认证信息"""
    return await auth_manager.get_auth(AuthType.MANUS_LOGIN, context)

async def get_github_token(context: Dict = None) -> Optional[Dict[str, str]]:
    """获取GitHub Token"""
    return await auth_manager.get_auth(AuthType.GITHUB_TOKEN, context)

async def get_ec2_pem_key(context: Dict = None) -> Optional[Dict[str, str]]:
    """获取EC2 PEM密钥"""
    return await auth_manager.get_auth(AuthType.EC2_PEM_KEY, context)

async def get_anthropic_api_key(context: Dict = None) -> Optional[Dict[str, str]]:
    """获取Anthropic API密钥"""
    return await auth_manager.get_auth(AuthType.ANTHROPIC_API_KEY, context)

if __name__ == "__main__":
    # 测试代码
    async def test_auth_manager():
        # 测试Manus认证
        manus_auth = await get_manus_auth({
            "purpose": "测试Manus连接",
            "project_id": "uxW8QshQ7aEAVOKIxHxoG5"
        })
        print(f"Manus认证结果: {manus_auth}")
        
        # 测试GitHub Token
        github_auth = await get_github_token({
            "purpose": "测试GitHub操作",
            "repository": "alexchuang650730/aicore0624"
        })
        print(f"GitHub认证结果: {github_auth}")
    
    # 运行测试
    asyncio.run(test_auth_manager())

