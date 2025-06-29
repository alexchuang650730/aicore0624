#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EC2 部署触发器
在 EC2 主平台部署完成后，自动触发本地环境的 init_aicore.sh

这个脚本应该在 EC2 部署脚本的最后阶段调用，
用于通知和触发所有注册的本地环境进行初始化。

作者: PowerAutomation Team
创建时间: 2025-06-29
版本: 1.0.0
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from remote_deployment_coordinator import (
    RemoteDeploymentCoordinator,
    RemoteEnvironmentConfig,
    RemoteEnvironmentType
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EC2DeploymentTrigger:
    """EC2 部署触发器"""
    
    def __init__(self, config_file: str = "remote_environments.json"):
        self.coordinator = RemoteDeploymentCoordinator()
        self.config_file = config_file
        self.load_environment_configs()
    
    def load_environment_configs(self):
        """加载远程环境配置"""
        config_path = Path(self.config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    configs = json.load(f)
                
                for config_data in configs.get("environments", []):
                    env_config = RemoteEnvironmentConfig(
                        environment_id=config_data["environment_id"],
                        environment_type=RemoteEnvironmentType(config_data["environment_type"]),
                        connection_method=config_data["connection_method"],
                        host=config_data["host"],
                        port=config_data["port"],
                        username=config_data.get("username"),
                        ssh_key_path=config_data.get("ssh_key_path"),
                        api_token=config_data.get("api_token"),
                        init_script_path=config_data.get("init_script_path", "./init_aicore.sh"),
                        health_check_url=config_data.get("health_check_url"),
                        timeout=config_data.get("timeout", 300)
                    )
                    
                    self.coordinator.register_remote_environment(env_config)
                    logger.info(f"✅ 加载环境配置: {env_config.environment_id}")
                
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
                self._create_default_config()
        else:
            logger.warning(f"配置文件不存在: {config_path}")
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置文件"""
        default_config = {
            "environments": [
                {
                    "environment_id": "mac_local_001",
                    "environment_type": "mac_local",
                    "connection_method": "ssh",
                    "host": "192.168.1.100",
                    "port": 22,
                    "username": "alexchuang",
                    "ssh_key_path": "/home/ubuntu/.ssh/id_rsa",
                    "init_script_path": "./init_aicore.sh",
                    "health_check_url": "http://localhost:8081/health",
                    "timeout": 300
                }
            ]
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ 创建默认配置文件: {self.config_file}")
            logger.info("请根据实际环境修改配置文件中的连接信息")
            
        except Exception as e:
            logger.error(f"创建默认配置文件失败: {e}")
    
    async def trigger_local_deployments(self, ec2_deployment_result: dict = None):
        """触发本地环境部署"""
        
        if not ec2_deployment_result:
            ec2_deployment_result = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "ec2_instance_id": os.environ.get("EC2_INSTANCE_ID", "unknown"),
                "public_ip": os.environ.get("EC2_PUBLIC_IP", "unknown")
            }
        
        # 获取所有注册的环境
        target_environments = list(self.coordinator.remote_environments.keys())
        
        if not target_environments:
            logger.warning("⚠️ 没有注册的远程环境，跳过本地部署触发")
            return
        
        logger.info(f"🚀 开始触发 {len(target_environments)} 个本地环境的部署")
        
        # 生成协调ID
        coordination_id = f"ec2_trigger_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 执行协调部署
        result = await self.coordinator.coordinate_deployment(
            coordination_id=coordination_id,
            ec2_deployment_config=ec2_deployment_result,
            target_environments=target_environments
        )
        
        # 输出结果
        self._print_deployment_result(result)
        
        return result
    
    def _print_deployment_result(self, result):
        """打印部署结果"""
        print("\n" + "="*60)
        print("🎯 EC2 到本地环境部署协调结果")
        print("="*60)
        
        print(f"📋 协调ID: {result.coordination_id}")
        print(f"📊 状态: {result.status.value}")
        print(f"⏱️ 总耗时: {result.total_duration:.2f} 秒" if result.total_duration else "⏱️ 进行中...")
        
        print(f"\n☁️ EC2 部署结果:")
        if result.ec2_deployment_result:
            for key, value in result.ec2_deployment_result.items():
                print(f"   {key}: {value}")
        
        print(f"\n💻 本地环境部署结果:")
        for env_id, local_result in result.local_deployment_results.items():
            status = "✅ 成功" if local_result.get("success", False) else "❌ 失败"
            print(f"   {env_id}: {status}")
            if not local_result.get("success", False) and "error" in local_result:
                print(f"      错误: {local_result['error']}")
        
        if result.logs:
            print(f"\n📝 部署日志:")
            for log in result.logs[-10:]:  # 显示最后10条日志
                print(f"   {log}")
        
        if result.errors:
            print(f"\n❌ 错误信息:")
            for error in result.errors:
                print(f"   {error}")
        
        print("="*60)

async def main():
    """主函数 - 可以被 EC2 部署脚本调用"""
    
    print("🚀 EC2 部署触发器启动")
    print("📡 PowerAutomation 主平台部署完成，开始触发本地环境部署...")
    
    # 创建触发器实例
    trigger = EC2DeploymentTrigger()
    
    # 从环境变量或命令行参数获取 EC2 部署结果
    ec2_result = {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "ec2_instance_id": os.environ.get("EC2_INSTANCE_ID", "i-unknown"),
        "public_ip": os.environ.get("EC2_PUBLIC_IP", "unknown"),
        "deployment_version": os.environ.get("DEPLOYMENT_VERSION", "latest"),
        "services": ["powerautomation_main", "mcp_coordinator"],
        "endpoints": [
            f"http://{os.environ.get('EC2_PUBLIC_IP', 'unknown')}:8080/api/health",
            f"http://{os.environ.get('EC2_PUBLIC_IP', 'unknown')}:8080/api/mcp"
        ]
    }
    
    # 触发本地部署
    try:
        result = await trigger.trigger_local_deployments(ec2_result)
        
        # 根据结果设置退出码
        if result.status.value in ["completed"]:
            print("🎉 所有本地环境部署成功完成！")
            sys.exit(0)
        else:
            print("⚠️ 部分本地环境部署失败，请检查日志")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"触发本地部署失败: {e}", exc_info=True)
        print(f"❌ 触发本地部署失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

