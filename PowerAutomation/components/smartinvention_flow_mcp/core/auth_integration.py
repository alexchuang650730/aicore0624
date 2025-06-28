#!/usr/bin/env python3
"""
认证集成模块 - 将认证管理器集成到SmartInvention Flow MCP中
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from ..auth_manager.main import auth_manager, AuthType

class AuthIntegration:
    """认证集成器 - 为SmartInvention Flow MCP提供统一认证"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.auth_manager = auth_manager
    
    async def get_manus_credentials(self, context: Dict = None) -> Optional[Dict[str, str]]:
        """获取Manus认证信息"""
        try:
            default_context = {
                "purpose": "访问Manus项目数据",
                "project_id": "uxW8QshQ7aEAVOKIxHxoG5",
                "platform": "manus.im"
            }
            
            if context:
                default_context.update(context)
            
            credentials = await self.auth_manager.get_auth(AuthType.MANUS_LOGIN, default_context)
            
            if credentials:
                self.logger.info("成功获取Manus认证信息")
                return credentials
            else:
                self.logger.warning("未能获取Manus认证信息")
                return None
                
        except Exception as e:
            self.logger.error(f"获取Manus认证信息失败: {e}")
            return None
    
    async def get_github_credentials(self, context: Dict = None) -> Optional[Dict[str, str]]:
        """获取GitHub认证信息"""
        try:
            default_context = {
                "purpose": "GitHub仓库操作",
                "repository": "alexchuang650730/aicore0624",
                "scope": "repo"
            }
            
            if context:
                default_context.update(context)
            
            credentials = await self.auth_manager.get_auth(AuthType.GITHUB_TOKEN, default_context)
            
            if credentials:
                self.logger.info("成功获取GitHub认证信息")
                return credentials
            else:
                self.logger.warning("未能获取GitHub认证信息")
                return None
                
        except Exception as e:
            self.logger.error(f"获取GitHub认证信息失败: {e}")
            return None
    
    async def get_ec2_credentials(self, context: Dict = None) -> Optional[Dict[str, str]]:
        """获取EC2认证信息"""
        try:
            default_context = {
                "purpose": "EC2服务器连接",
                "server_ip": "18.212.49.136",
                "username": "ec2-user"
            }
            
            if context:
                default_context.update(context)
            
            credentials = await self.auth_manager.get_auth(AuthType.EC2_PEM_KEY, default_context)
            
            if credentials:
                self.logger.info("成功获取EC2认证信息")
                return credentials
            else:
                self.logger.warning("未能获取EC2认证信息")
                return None
                
        except Exception as e:
            self.logger.error(f"获取EC2认证信息失败: {e}")
            return None
    
    async def get_anthropic_credentials(self, context: Dict = None) -> Optional[Dict[str, str]]:
        """获取Anthropic API认证信息"""
        try:
            default_context = {
                "purpose": "Claude AI服务",
                "service": "Anthropic Claude",
                "model": "claude-3-sonnet"
            }
            
            if context:
                default_context.update(context)
            
            credentials = await self.auth_manager.get_auth(AuthType.ANTHROPIC_API_KEY, default_context)
            
            if credentials:
                self.logger.info("成功获取Anthropic认证信息")
                return credentials
            else:
                self.logger.warning("未能获取Anthropic认证信息")
                return None
                
        except Exception as e:
            self.logger.error(f"获取Anthropic认证信息失败: {e}")
            return None
    
    async def validate_all_credentials(self) -> Dict[str, bool]:
        """验证所有必需的认证信息"""
        validation_results = {}
        
        # 验证Manus认证
        manus_creds = await self.get_manus_credentials()
        validation_results['manus'] = manus_creds is not None
        
        # 验证GitHub认证
        github_creds = await self.get_github_credentials()
        validation_results['github'] = github_creds is not None
        
        # 验证EC2认证
        ec2_creds = await self.get_ec2_credentials()
        validation_results['ec2'] = ec2_creds is not None
        
        # 验证Anthropic认证
        anthropic_creds = await self.get_anthropic_credentials()
        validation_results['anthropic'] = anthropic_creds is not None
        
        self.logger.info(f"认证验证结果: {validation_results}")
        return validation_results
    
    def clear_credentials(self, auth_type: str = None):
        """清除认证缓存"""
        if auth_type:
            auth_type_enum = getattr(AuthType, auth_type.upper(), None)
            if auth_type_enum:
                self.auth_manager.clear_auth_cache(auth_type_enum)
                self.logger.info(f"已清除 {auth_type} 认证缓存")
        else:
            self.auth_manager.clear_auth_cache()
            self.logger.info("已清除所有认证缓存")

# 全局认证集成实例
auth_integration = AuthIntegration()

# 便捷函数
async def ensure_manus_auth(context: Dict = None) -> Optional[Dict[str, str]]:
    """确保Manus认证可用"""
    return await auth_integration.get_manus_credentials(context)

async def ensure_github_auth(context: Dict = None) -> Optional[Dict[str, str]]:
    """确保GitHub认证可用"""
    return await auth_integration.get_github_credentials(context)

async def ensure_ec2_auth(context: Dict = None) -> Optional[Dict[str, str]]:
    """确保EC2认证可用"""
    return await auth_integration.get_ec2_credentials(context)

async def ensure_anthropic_auth(context: Dict = None) -> Optional[Dict[str, str]]:
    """确保Anthropic认证可用"""
    return await auth_integration.get_anthropic_credentials(context)

if __name__ == "__main__":
    # 测试认证集成
    async def test_auth_integration():
        print("测试认证集成...")
        
        # 测试所有认证
        results = await auth_integration.validate_all_credentials()
        
        for service, available in results.items():
            status = "✅ 可用" if available else "❌ 不可用"
            print(f"{service}: {status}")
    
    # 运行测试
    asyncio.run(test_auth_integration())

