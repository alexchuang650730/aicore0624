# -*- coding: utf-8 -*-
"""
远程部署协调器 (Remote Deployment Coordinator)
负责协调 EC2 主平台到本地环境的部署

支持多种连接方式：
- SSH 远程执行
- HTTP API 调用
- Webhook 通知

作者: PowerAutomation Team
版本: 2.0.0 (支持真正的一键部署)
"""

import asyncio
import json
import logging
import subprocess
import time
import aiohttp
import paramiko
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ConnectionMethod(Enum):
    SSH = "ssh"
    HTTP_API = "http_api"
    WEBHOOK = "webhook"

class EnvironmentType(Enum):
    MAC_LOCAL = "mac_local"
    WINDOWS_LOCAL = "windows_local"
    LINUX_LOCAL = "linux_local"
    DOCKER = "docker"

@dataclass
class RemoteEnvironment:
    environment_id: str
    environment_type: EnvironmentType
    connection_method: ConnectionMethod
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    ssh_key_path: Optional[str] = None
    api_endpoint: Optional[str] = None
    webhook_url: Optional[str] = None
    init_script_path: str = "./init_aicore.sh"
    working_directory: str = "."
    timeout: int = 300
    health_check_url: Optional[str] = None

class RemoteDeploymentCoordinator:
    """远程部署协调器"""
    
    def __init__(self):
        self.deployment_results = {}
        self.active_connections = {}
    
    async def deploy_to_environments(self, environments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """部署到多个环境"""
        try:
            logger.info(f"🚀 开始部署到 {len(environments)} 个环境")
            
            # 转换配置为环境对象
            env_objects = []
            for env_config in environments:
                try:
                    env = RemoteEnvironment(
                        environment_id=env_config.get('environment_id', 'unknown'),
                        environment_type=EnvironmentType(env_config.get('environment_type', 'mac_local')),
                        connection_method=ConnectionMethod(env_config.get('connection_method', 'ssh')),
                        host=env_config.get('host', 'localhost'),
                        port=env_config.get('port', 22),
                        username=env_config.get('username'),
                        password=env_config.get('password'),
                        ssh_key_path=env_config.get('ssh_key_path'),
                        api_endpoint=env_config.get('api_endpoint'),
                        webhook_url=env_config.get('webhook_url'),
                        init_script_path=env_config.get('init_script_path', './init_aicore.sh'),
                        working_directory=env_config.get('working_directory', '.'),
                        timeout=env_config.get('timeout', 300),
                        health_check_url=env_config.get('health_check_url')
                    )
                    env_objects.append(env)
                except Exception as e:
                    logger.error(f"❌ 环境配置解析失败 {env_config.get('environment_id', 'unknown')}: {e}")
                    continue
            
            if not env_objects:
                return {
                    'success': False,
                    'error': '没有有效的环境配置',
                    'results': {}
                }
            
            # 并行部署到所有环境
            deployment_tasks = [
                self._deploy_to_single_environment(env) 
                for env in env_objects
            ]
            
            results = await asyncio.gather(*deployment_tasks, return_exceptions=True)
            
            # 整理结果
            deployment_results = {}
            success_count = 0
            
            for i, result in enumerate(results):
                env_id = env_objects[i].environment_id
                
                if isinstance(result, Exception):
                    deployment_results[env_id] = {
                        'success': False,
                        'error': str(result),
                        'environment_type': env_objects[i].environment_type.value
                    }
                else:
                    deployment_results[env_id] = result
                    if result.get('success'):
                        success_count += 1
            
            overall_success = success_count > 0
            
            logger.info(f"📊 部署完成: {success_count}/{len(env_objects)} 个环境成功")
            
            return {
                'success': overall_success,
                'total_environments': len(env_objects),
                'successful_deployments': success_count,
                'failed_deployments': len(env_objects) - success_count,
                'results': deployment_results,
                'message': f'部署完成，{success_count}/{len(env_objects)} 个环境成功'
            }
            
        except Exception as e:
            logger.error(f"❌ 部署协调失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': {}
            }
    
    async def _deploy_to_single_environment(self, env: RemoteEnvironment) -> Dict[str, Any]:
        """部署到单个环境"""
        start_time = time.time()
        
        try:
            logger.info(f"🔧 开始部署到环境: {env.environment_id} ({env.environment_type.value})")
            
            # 根据连接方式选择部署方法
            if env.connection_method == ConnectionMethod.SSH:
                result = await self._deploy_via_ssh(env)
            elif env.connection_method == ConnectionMethod.HTTP_API:
                result = await self._deploy_via_http_api(env)
            elif env.connection_method == ConnectionMethod.WEBHOOK:
                result = await self._deploy_via_webhook(env)
            else:
                raise ValueError(f"不支持的连接方式: {env.connection_method}")
            
            # 添加执行时间
            result['execution_time'] = time.time() - start_time
            result['environment_id'] = env.environment_id
            result['environment_type'] = env.environment_type.value
            
            # 如果部署成功，进行健康检查
            if result.get('success') and env.health_check_url:
                health_result = await self._perform_health_check(env)
                result['health_check'] = health_result
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 环境 {env.environment_id} 部署失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'environment_id': env.environment_id,
                'environment_type': env.environment_type.value,
                'execution_time': time.time() - start_time
            }
    
    async def _deploy_via_ssh(self, env: RemoteEnvironment) -> Dict[str, Any]:
        """通过 SSH 部署"""
        try:
            logger.info(f"🔐 通过 SSH 连接到 {env.host}:{env.port}")
            
            # 创建 SSH 客户端
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 连接参数
            connect_kwargs = {
                'hostname': env.host,
                'port': env.port,
                'username': env.username,
                'timeout': 30
            }
            
            # 使用密钥或密码认证
            if env.ssh_key_path:
                connect_kwargs['key_filename'] = env.ssh_key_path
            elif env.password:
                connect_kwargs['password'] = env.password
            else:
                raise ValueError("需要提供 SSH 密钥或密码")
            
            # 建立连接
            ssh_client.connect(**connect_kwargs)
            
            # 构建执行命令
            commands = []
            
            # 切换到工作目录
            if env.working_directory != ".":
                commands.append(f"cd {env.working_directory}")
            
            # 检查脚本是否存在
            commands.append(f"if [ ! -f {env.init_script_path} ]; then echo 'ERROR: Script not found: {env.init_script_path}'; exit 1; fi")
            
            # 设置执行权限
            commands.append(f"chmod +x {env.init_script_path}")
            
            # 执行初始化脚本
            commands.append(f"{env.init_script_path}")
            
            # 组合命令
            full_command = " && ".join(commands)
            
            logger.info(f"📜 执行命令: {full_command}")
            
            # 执行命令
            stdin, stdout, stderr = ssh_client.exec_command(full_command, timeout=env.timeout)
            
            # 读取输出
            stdout_output = stdout.read().decode('utf-8')
            stderr_output = stderr.read().decode('utf-8')
            exit_code = stdout.channel.recv_exit_status()
            
            # 关闭连接
            ssh_client.close()
            
            success = exit_code == 0
            
            if success:
                logger.info(f"✅ SSH 部署成功: {env.environment_id}")
            else:
                logger.error(f"❌ SSH 部署失败: {env.environment_id}, 退出码: {exit_code}")
            
            return {
                'success': success,
                'exit_code': exit_code,
                'stdout': stdout_output,
                'stderr': stderr_output,
                'command': full_command,
                'connection_method': 'ssh'
            }
            
        except Exception as e:
            logger.error(f"❌ SSH 部署异常: {e}")
            return {
                'success': False,
                'error': str(e),
                'connection_method': 'ssh'
            }
    
    async def _deploy_via_http_api(self, env: RemoteEnvironment) -> Dict[str, Any]:
        """通过 HTTP API 部署"""
        try:
            if not env.api_endpoint:
                raise ValueError("HTTP API 部署需要提供 api_endpoint")
            
            logger.info(f"🌐 通过 HTTP API 部署: {env.api_endpoint}")
            
            # 准备请求数据
            payload = {
                'action': 'deploy',
                'script_path': env.init_script_path,
                'working_directory': env.working_directory,
                'environment_id': env.environment_id,
                'timeout': env.timeout
            }
            
            # 发送 HTTP 请求
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    env.api_endpoint,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=env.timeout)
                ) as response:
                    
                    response_data = await response.json()
                    success = response.status == 200 and response_data.get('success', False)
                    
                    if success:
                        logger.info(f"✅ HTTP API 部署成功: {env.environment_id}")
                    else:
                        logger.error(f"❌ HTTP API 部署失败: {env.environment_id}")
                    
                    return {
                        'success': success,
                        'status_code': response.status,
                        'response': response_data,
                        'connection_method': 'http_api'
                    }
            
        except Exception as e:
            logger.error(f"❌ HTTP API 部署异常: {e}")
            return {
                'success': False,
                'error': str(e),
                'connection_method': 'http_api'
            }
    
    async def _deploy_via_webhook(self, env: RemoteEnvironment) -> Dict[str, Any]:
        """通过 Webhook 部署"""
        try:
            if not env.webhook_url:
                raise ValueError("Webhook 部署需要提供 webhook_url")
            
            logger.info(f"🔗 通过 Webhook 部署: {env.webhook_url}")
            
            # 准备 Webhook 数据
            payload = {
                'event': 'deployment_trigger',
                'environment_id': env.environment_id,
                'script_path': env.init_script_path,
                'working_directory': env.working_directory,
                'timestamp': time.time()
            }
            
            # 发送 Webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    env.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    success = response.status in [200, 202]
                    response_text = await response.text()
                    
                    if success:
                        logger.info(f"✅ Webhook 发送成功: {env.environment_id}")
                    else:
                        logger.error(f"❌ Webhook 发送失败: {env.environment_id}")
                    
                    return {
                        'success': success,
                        'status_code': response.status,
                        'response': response_text,
                        'connection_method': 'webhook',
                        'note': 'Webhook 已发送，实际部署状态需要通过其他方式验证'
                    }
            
        except Exception as e:
            logger.error(f"❌ Webhook 部署异常: {e}")
            return {
                'success': False,
                'error': str(e),
                'connection_method': 'webhook'
            }
    
    async def _perform_health_check(self, env: RemoteEnvironment) -> Dict[str, Any]:
        """执行健康检查"""
        try:
            logger.info(f"🔍 执行健康检查: {env.health_check_url}")
            
            # 等待服务启动
            await asyncio.sleep(5)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    env.health_check_url,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    success = response.status == 200
                    response_data = await response.text()
                    
                    return {
                        'success': success,
                        'status_code': response.status,
                        'response': response_data[:500],  # 限制响应长度
                        'url': env.health_check_url
                    }
            
        except Exception as e:
            logger.error(f"❌ 健康检查失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': env.health_check_url
            }
    
    async def get_environment_status(self, environment_id: str) -> Dict[str, Any]:
        """获取环境状态"""
        # 这里可以实现环境状态查询逻辑
        return {
            'environment_id': environment_id,
            'status': 'unknown',
            'message': '状态查询功能待实现'
        }

# 用于测试的主函数
async def main():
    """测试函数"""
    coordinator = RemoteDeploymentCoordinator()
    
    # 测试环境配置
    test_environments = [
        {
            'environment_id': 'test_local',
            'environment_type': 'mac_local',
            'connection_method': 'ssh',
            'host': 'localhost',
            'port': 22,
            'username': 'testuser',
            'ssh_key_path': '~/.ssh/id_rsa',
            'init_script_path': './init_aicore.sh',
            'working_directory': '.',
            'timeout': 300
        }
    ]
    
    result = await coordinator.deploy_to_environments(test_environments)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

