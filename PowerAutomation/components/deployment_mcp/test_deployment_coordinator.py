#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署协调机制测试套件
测试 EC2 到本地环境的部署协调功能

作者: PowerAutomation Team
创建时间: 2025-06-29
版本: 1.0.0
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import subprocess

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from remote_deployment_coordinator import (
    RemoteDeploymentCoordinator,
    RemoteEnvironmentConfig,
    RemoteEnvironmentType,
    DeploymentCoordinationStatus
)
from ec2_deployment_trigger import EC2DeploymentTrigger

# 配置测试日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestRemoteEnvironmentConfig(unittest.TestCase):
    """测试远程环境配置"""
    
    def test_config_creation(self):
        """测试配置创建"""
        config = RemoteEnvironmentConfig(
            environment_id="test_env",
            environment_type=RemoteEnvironmentType.MAC_LOCAL,
            connection_method="ssh",
            host="localhost",
            port=22,
            username="testuser",
            ssh_key_path="/path/to/key"
        )
        
        self.assertEqual(config.environment_id, "test_env")
        self.assertEqual(config.environment_type, RemoteEnvironmentType.MAC_LOCAL)
        self.assertEqual(config.connection_method, "ssh")
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 22)
        self.assertEqual(config.init_script_path, "./init_aicore.sh")  # 默认值
        self.assertEqual(config.timeout, 300)  # 默认值

class TestRemoteDeploymentCoordinator(unittest.TestCase):
    """测试远程部署协调器"""
    
    def setUp(self):
        """设置测试环境"""
        self.coordinator = RemoteDeploymentCoordinator()
        
        # 创建测试配置
        self.test_config = RemoteEnvironmentConfig(
            environment_id="test_mac",
            environment_type=RemoteEnvironmentType.MAC_LOCAL,
            connection_method="ssh",
            host="localhost",
            port=22,
            username="testuser",
            ssh_key_path="/tmp/test_key"
        )
    
    def test_register_environment(self):
        """测试环境注册"""
        self.coordinator.register_remote_environment(self.test_config)
        
        self.assertIn("test_mac", self.coordinator.remote_environments)
        registered_config = self.coordinator.remote_environments["test_mac"]
        self.assertEqual(registered_config.environment_id, "test_mac")
    
    @patch('remote_deployment_coordinator.RemoteDeploymentCoordinator._deploy_ec2_platform')
    @patch('remote_deployment_coordinator.RemoteDeploymentCoordinator._trigger_local_deployment')
    async def test_coordinate_deployment_success(self, mock_trigger_local, mock_deploy_ec2):
        """测试成功的部署协调"""
        # 设置 mock 返回值
        mock_deploy_ec2.return_value = {"success": True, "instance_id": "i-test123"}
        mock_trigger_local.return_value = {"success": True, "output": "Deployment successful"}
        
        # 注册环境
        self.coordinator.register_remote_environment(self.test_config)
        
        # 执行协调部署
        result = await self.coordinator.coordinate_deployment(
            coordination_id="test_deploy_001",
            ec2_deployment_config={"instance_type": "t3.micro"},
            target_environments=["test_mac"]
        )
        
        # 验证结果
        self.assertEqual(result.coordination_id, "test_deploy_001")
        self.assertEqual(result.status, DeploymentCoordinationStatus.COMPLETED)
        self.assertTrue(result.ec2_deployment_result["success"])
        self.assertTrue(result.local_deployment_results["test_mac"]["success"])
        self.assertIsNotNone(result.total_duration)
    
    @patch('remote_deployment_coordinator.RemoteDeploymentCoordinator._deploy_ec2_platform')
    async def test_coordinate_deployment_ec2_failure(self, mock_deploy_ec2):
        """测试 EC2 部署失败的情况"""
        # 设置 EC2 部署失败
        mock_deploy_ec2.return_value = {"success": False, "error": "EC2 deployment failed"}
        
        # 注册环境
        self.coordinator.register_remote_environment(self.test_config)
        
        # 执行协调部署
        result = await self.coordinator.coordinate_deployment(
            coordination_id="test_deploy_002",
            ec2_deployment_config={"instance_type": "t3.micro"},
            target_environments=["test_mac"]
        )
        
        # 验证结果
        self.assertEqual(result.status, DeploymentCoordinationStatus.FAILED)
        self.assertFalse(result.ec2_deployment_result["success"])
        self.assertIn("EC2 deployment failed", result.errors[0])
    
    @patch('paramiko.SSHClient')
    async def test_trigger_via_ssh_success(self, mock_ssh_class):
        """测试通过 SSH 成功触发部署"""
        # 设置 SSH mock
        mock_ssh = Mock()
        mock_ssh_class.return_value = mock_ssh
        
        # 设置命令执行成功
        mock_stdout = Mock()
        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_stdout.read.return_value = b"Deployment successful"
        
        mock_stderr = Mock()
        mock_stderr.read.return_value = b""
        
        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        # 执行测试
        result = await self.coordinator._trigger_via_ssh(self.test_config)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["method"], "ssh")
        self.assertIn("Deployment successful", result["output"])
    
    @patch('paramiko.SSHClient')
    async def test_trigger_via_ssh_failure(self, mock_ssh_class):
        """测试通过 SSH 触发部署失败"""
        # 设置 SSH mock
        mock_ssh = Mock()
        mock_ssh_class.return_value = mock_ssh
        
        # 设置命令执行失败
        mock_stdout = Mock()
        mock_stdout.channel.recv_exit_status.return_value = 1
        mock_stdout.read.return_value = b""
        
        mock_stderr = Mock()
        mock_stderr.read.return_value = b"Command failed"
        
        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        # 执行测试
        result = await self.coordinator._trigger_via_ssh(self.test_config)
        
        # 验证结果
        self.assertFalse(result["success"])
        self.assertEqual(result["method"], "ssh")
        self.assertIn("Command failed", result["error"])
    
    @patch('requests.post')
    async def test_trigger_via_http_success(self, mock_post):
        """测试通过 HTTP API 成功触发部署"""
        # 设置 HTTP mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "message": "Deployment started"}
        mock_post.return_value = mock_response
        
        # 创建 HTTP API 配置
        http_config = RemoteEnvironmentConfig(
            environment_id="test_http",
            environment_type=RemoteEnvironmentType.MAC_LOCAL,
            connection_method="http_api",
            host="localhost",
            port=8080,
            api_token="test_token"
        )
        
        # 执行测试
        result = await self.coordinator._trigger_via_http(http_config)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["method"], "http_api")
        self.assertIn("status", result["response"])
    
    @patch('requests.post')
    async def test_trigger_via_webhook_success(self, mock_post):
        """测试通过 Webhook 成功触发部署"""
        # 设置 Webhook mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"received": true}'
        mock_response.json.return_value = {"received": True}
        mock_post.return_value = mock_response
        
        # 创建 Webhook 配置
        webhook_config = RemoteEnvironmentConfig(
            environment_id="test_webhook",
            environment_type=RemoteEnvironmentType.MAC_LOCAL,
            connection_method="webhook",
            host="localhost",
            port=8080
        )
        
        # 执行测试
        result = await self.coordinator._trigger_via_webhook(webhook_config)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["method"], "webhook")

class TestEC2DeploymentTrigger(unittest.TestCase):
    """测试 EC2 部署触发器"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时配置文件
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        test_config = {
            "environments": [
                {
                    "environment_id": "test_env_001",
                    "environment_type": "mac_local",
                    "connection_method": "ssh",
                    "host": "localhost",
                    "port": 22,
                    "username": "testuser",
                    "ssh_key_path": "/tmp/test_key",
                    "init_script_path": "./init_aicore.sh",
                    "timeout": 300
                }
            ]
        }
        
        json.dump(test_config, self.temp_config)
        self.temp_config.close()
        
        self.trigger = EC2DeploymentTrigger(self.temp_config.name)
    
    def tearDown(self):
        """清理测试环境"""
        os.unlink(self.temp_config.name)
    
    def test_load_environment_configs(self):
        """测试环境配置加载"""
        # 验证配置已加载
        self.assertIn("test_env_001", self.trigger.coordinator.remote_environments)
        
        config = self.trigger.coordinator.remote_environments["test_env_001"]
        self.assertEqual(config.environment_id, "test_env_001")
        self.assertEqual(config.host, "localhost")
    
    @patch('ec2_deployment_trigger.RemoteDeploymentCoordinator.coordinate_deployment')
    async def test_trigger_local_deployments(self, mock_coordinate):
        """测试触发本地部署"""
        # 设置 mock 返回值
        mock_result = Mock()
        mock_result.status = DeploymentCoordinationStatus.COMPLETED
        mock_result.coordination_id = "test_coordination"
        mock_result.total_duration = 30.5
        mock_result.ec2_deployment_result = {"success": True}
        mock_result.local_deployment_results = {"test_env_001": {"success": True}}
        mock_result.logs = ["Test log"]
        mock_result.errors = []
        
        mock_coordinate.return_value = mock_result
        
        # 执行测试
        result = await self.trigger.trigger_local_deployments()
        
        # 验证结果
        self.assertEqual(result.status, DeploymentCoordinationStatus.COMPLETED)
        mock_coordinate.assert_called_once()

class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """设置集成测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, "test_config.json")
        
        # 创建测试配置
        test_config = {
            "environments": [
                {
                    "environment_id": "integration_test",
                    "environment_type": "mac_local",
                    "connection_method": "ssh",
                    "host": "localhost",
                    "port": 22,
                    "username": "testuser",
                    "ssh_key_path": "/tmp/test_key",
                    "init_script_path": "./test_init.sh",
                    "timeout": 60
                }
            ]
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
        
        # 创建测试脚本
        self.test_script = os.path.join(self.test_dir, "test_init.sh")
        with open(self.test_script, 'w') as f:
            f.write("""#!/bin/bash
echo "Test deployment script executed"
echo "Environment: $1"
echo "Timestamp: $(date)"
exit 0
""")
        os.chmod(self.test_script, 0o755)
    
    def tearDown(self):
        """清理集成测试环境"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_config_file_creation(self):
        """测试配置文件创建"""
        # 删除配置文件
        os.unlink(self.config_file)
        
        # 创建触发器（应该创建默认配置）
        trigger = EC2DeploymentTrigger(self.config_file)
        
        # 验证配置文件已创建
        self.assertTrue(os.path.exists(self.config_file))
        
        # 验证配置内容
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        self.assertIn("environments", config)
        self.assertGreater(len(config["environments"]), 0)

class TestEndToEnd(unittest.TestCase):
    """端到端测试"""
    
    @patch.dict(os.environ, {
        'EC2_INSTANCE_ID': 'i-test123456',
        'EC2_PUBLIC_IP': '54.123.45.67',
        'DEPLOYMENT_VERSION': 'v1.0.0-test'
    })
    @patch('subprocess.run')
    def test_full_deployment_simulation(self, mock_subprocess):
        """测试完整的部署模拟"""
        # 模拟成功的脚本执行
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Deployment successful"
        mock_subprocess.return_value.stderr = ""
        
        # 创建临时配置
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_config = {
                "environments": [
                    {
                        "environment_id": "e2e_test",
                        "environment_type": "mac_local",
                        "connection_method": "ssh",
                        "host": "localhost",
                        "port": 22,
                        "username": "testuser",
                        "ssh_key_path": "/tmp/test_key",
                        "init_script_path": "./init_aicore.sh",
                        "timeout": 300
                    }
                ]
            }
            json.dump(test_config, f)
            config_file = f.name
        
        try:
            # 验证环境变量
            self.assertEqual(os.environ['EC2_INSTANCE_ID'], 'i-test123456')
            self.assertEqual(os.environ['EC2_PUBLIC_IP'], '54.123.45.67')
            
            # 创建触发器
            trigger = EC2DeploymentTrigger(config_file)
            
            # 验证配置加载
            self.assertIn("e2e_test", trigger.coordinator.remote_environments)
            
            logger.info("✅ 端到端测试模拟完成")
            
        finally:
            os.unlink(config_file)

class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.test_results = {}
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始运行部署协调机制测试套件")
        print("=" * 60)
        
        test_classes = [
            TestRemoteEnvironmentConfig,
            TestRemoteDeploymentCoordinator,
            TestEC2DeploymentTrigger,
            TestIntegration,
            TestEndToEnd
        ]
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for test_class in test_classes:
            print(f"\n📋 运行测试类: {test_class.__name__}")
            print("-" * 40)
            
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            
            class_total = result.testsRun
            class_failures = len(result.failures)
            class_errors = len(result.errors)
            class_passed = class_total - class_failures - class_errors
            
            total_tests += class_total
            passed_tests += class_passed
            failed_tests += class_failures + class_errors
            
            self.test_results[test_class.__name__] = {
                "total": class_total,
                "passed": class_passed,
                "failed": class_failures + class_errors,
                "failures": result.failures,
                "errors": result.errors
            }
            
            if class_failures + class_errors == 0:
                print(f"✅ {test_class.__name__}: 全部通过 ({class_passed}/{class_total})")
            else:
                print(f"❌ {test_class.__name__}: {class_passed}/{class_total} 通过")
        
        # 输出总结
        print("\n" + "=" * 60)
        print("📊 测试结果总结")
        print("=" * 60)
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        if failed_tests == 0:
            print("\n🎉 所有测试通过！部署协调机制工作正常。")
            return True
        else:
            print(f"\n⚠️ 有 {failed_tests} 个测试失败，需要修复。")
            self._print_failure_details()
            return False
    
    def _print_failure_details(self):
        """打印失败详情"""
        print("\n❌ 失败详情:")
        for class_name, results in self.test_results.items():
            if results["failed"] > 0:
                print(f"\n{class_name}:")
                for failure in results["failures"]:
                    print(f"  - {failure[0]}: {failure[1]}")
                for error in results["errors"]:
                    print(f"  - {error[0]}: {error[1]}")

async def run_async_tests():
    """运行异步测试"""
    print("🔄 运行异步测试...")
    
    try:
        # 测试协调部署
        coordinator = RemoteDeploymentCoordinator()
        
        # 注册测试环境
        test_config = RemoteEnvironmentConfig(
            environment_id="async_test",
            environment_type=RemoteEnvironmentType.MAC_LOCAL,
            connection_method="ssh",
            host="localhost",
            port=22,
            username="testuser",
            ssh_key_path="/tmp/test_key"
        )
        coordinator.register_remote_environment(test_config)
        
        # 测试 EC2 部署
        with patch.object(coordinator, '_deploy_ec2_platform') as mock_ec2, \
             patch.object(coordinator, '_trigger_local_deployment') as mock_local:
            
            mock_ec2.return_value = {"success": True, "instance_id": "i-test123"}
            mock_local.return_value = {"success": True, "output": "Success"}
            
            result = await coordinator.coordinate_deployment(
                coordination_id="async_test_001",
                ec2_deployment_config={"instance_type": "t3.micro"},
                target_environments=["async_test"]
            )
            
            assert result.status == DeploymentCoordinationStatus.COMPLETED
            print("✅ 异步协调部署测试通过")
        
        # 测试 SSH 触发
        with patch('paramiko.SSHClient') as mock_ssh_class:
            mock_ssh = Mock()
            mock_ssh_class.return_value = mock_ssh
            
            mock_stdout = Mock()
            mock_stdout.channel.recv_exit_status.return_value = 0
            mock_stdout.read.return_value = b"Success"
            
            mock_stderr = Mock()
            mock_stderr.read.return_value = b""
            
            mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)
            
            result = await coordinator._trigger_via_ssh(test_config)
            assert result["success"] == True
            print("✅ SSH 触发测试通过")
        
        # 测试 HTTP API 触发
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success"}
            mock_post.return_value = mock_response
            
            http_config = RemoteEnvironmentConfig(
                environment_id="async_http_test",
                environment_type=RemoteEnvironmentType.MAC_LOCAL,
                connection_method="http_api",
                host="localhost",
                port=8080,
                api_token="test_token"
            )
            
            result = await coordinator._trigger_via_http(http_config)
            assert result["success"] == True
            print("✅ HTTP API 触发测试通过")
        
        print("🎉 所有异步测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 异步测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 PowerAutomation 部署协调机制测试套件")
    print("测试 EC2 到本地环境的部署协调功能")
    print("=" * 60)
    
    # 运行同步测试
    runner = TestRunner()
    sync_success = runner.run_all_tests()
    
    # 运行异步测试
    async_success = asyncio.run(run_async_tests())
    
    # 总结
    if sync_success and async_success:
        print("\n🎉 所有测试通过！部署协调机制已准备就绪。")
        print("✅ 可以安全地上传到 GitHub。")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请修复后再上传。")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

