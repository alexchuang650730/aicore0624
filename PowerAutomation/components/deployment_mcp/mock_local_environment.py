#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟本地环境
用于测试 EC2 到本地环境的部署协调机制

提供 HTTP API 和 Webhook 接口来模拟本地环境的响应

作者: PowerAutomation Team
创建时间: 2025-06-29
版本: 1.0.0
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from flask import Flask, request, jsonify
import threading

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockLocalEnvironment:
    """模拟本地环境"""
    
    def __init__(self, port: int = 8082):
        self.port = port
        self.app = Flask(__name__)
        self.deployment_history = []
        self.setup_routes()
    
    def setup_routes(self):
        """设置路由"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """健康检查端点"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "environment": "mock_local",
                "services": {
                    "aiweb": "running",
                    "smartui": "running",
                    "powerautomation_local": "running"
                }
            })
        
        @self.app.route('/api/deploy/init', methods=['POST'])
        def deploy_init():
            """部署初始化 API"""
            try:
                data = request.get_json()
                
                # 记录部署请求
                deployment_record = {
                    "timestamp": datetime.now().isoformat(),
                    "action": data.get("action", "unknown"),
                    "script_path": data.get("script_path", "./init_aicore.sh"),
                    "request_data": data
                }
                
                self.deployment_history.append(deployment_record)
                
                # 模拟执行 init_aicore.sh
                script_path = data.get("script_path", "./init_aicore.sh")
                result = self._simulate_script_execution(script_path)
                
                if result["success"]:
                    return jsonify({
                        "status": "success",
                        "message": "本地环境初始化成功",
                        "deployment_id": f"deploy_{int(time.time())}",
                        "script_output": result["output"],
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        "status": "error",
                        "message": "本地环境初始化失败",
                        "error": result["error"],
                        "timestamp": datetime.now().isoformat()
                    }), 500
                    
            except Exception as e:
                logger.error(f"部署 API 错误: {e}")
                return jsonify({
                    "status": "error",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }), 500
        
        @self.app.route('/webhook/deploy', methods=['POST'])
        def webhook_deploy():
            """Webhook 部署端点"""
            try:
                data = request.get_json()
                
                # 记录 webhook 请求
                webhook_record = {
                    "timestamp": datetime.now().isoformat(),
                    "event": data.get("event", "unknown"),
                    "action": data.get("action", "unknown"),
                    "environment_id": data.get("environment_id", "unknown"),
                    "request_data": data
                }
                
                self.deployment_history.append(webhook_record)
                
                # 异步执行部署（模拟）
                threading.Thread(
                    target=self._async_deploy,
                    args=(data,),
                    daemon=True
                ).start()
                
                return jsonify({
                    "received": True,
                    "message": "Webhook 已接收，部署正在后台执行",
                    "timestamp": datetime.now().isoformat()
                }), 202
                
            except Exception as e:
                logger.error(f"Webhook 错误: {e}")
                return jsonify({
                    "received": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """获取环境状态"""
            return jsonify({
                "environment": "mock_local",
                "status": "running",
                "deployment_count": len(self.deployment_history),
                "last_deployment": self.deployment_history[-1] if self.deployment_history else None,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/history', methods=['GET'])
        def get_history():
            """获取部署历史"""
            limit = request.args.get('limit', 10, type=int)
            return jsonify({
                "history": self.deployment_history[-limit:],
                "total_count": len(self.deployment_history),
                "timestamp": datetime.now().isoformat()
            })
    
    def _simulate_script_execution(self, script_path: str) -> Dict[str, Any]:
        """模拟脚本执行"""
        try:
            # 模拟 init_aicore.sh 的执行
            logger.info(f"模拟执行脚本: {script_path}")
            
            # 模拟执行时间
            time.sleep(2)
            
            # 模拟成功的输出
            output = f"""
🚀 AICore 本地环境初始化开始...
✅ 系统要求检查通过
🔧 PowerAutomation_local 初始化完成
🌐 AIWeb & SmartUI 组件初始化完成
🔗 PowerAutomation_local MCP 适配器启动成功
🌐 AIWeb & SmartUI 组件启动成功
📊 本地环境状态验证通过
🎉 AICore 本地环境初始化成功！

服务状态:
• AIWeb 入口: http://localhost:8081 ✅
• SmartUI IDE: http://localhost:3000 ✅
• SmartUI 后端 API: http://localhost:5001 ✅
• PowerAutomation_local MCP: ✅ 运行中

执行时间: {datetime.now().isoformat()}
"""
            
            return {
                "success": True,
                "output": output.strip(),
                "execution_time": 2.0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": 0
            }
    
    def _async_deploy(self, webhook_data: Dict[str, Any]):
        """异步执行部署"""
        try:
            logger.info("开始异步部署...")
            
            # 模拟部署过程
            time.sleep(3)
            
            # 更新部署历史
            result_record = {
                "timestamp": datetime.now().isoformat(),
                "type": "webhook_result",
                "event": webhook_data.get("event"),
                "status": "completed",
                "message": "Webhook 触发的部署已完成"
            }
            
            self.deployment_history.append(result_record)
            logger.info("异步部署完成")
            
        except Exception as e:
            logger.error(f"异步部署失败: {e}")
            
            error_record = {
                "timestamp": datetime.now().isoformat(),
                "type": "webhook_error",
                "event": webhook_data.get("event"),
                "status": "failed",
                "error": str(e)
            }
            
            self.deployment_history.append(error_record)
    
    def run(self, debug: bool = False):
        """运行模拟环境"""
        logger.info(f"🚀 启动模拟本地环境，端口: {self.port}")
        logger.info(f"📡 健康检查: http://localhost:{self.port}/health")
        logger.info(f"🔧 部署 API: http://localhost:{self.port}/api/deploy/init")
        logger.info(f"🪝 Webhook: http://localhost:{self.port}/webhook/deploy")
        
        self.app.run(
            host='0.0.0.0',
            port=self.port,
            debug=debug,
            threaded=True
        )

class MockSSHServer:
    """模拟 SSH 服务器"""
    
    def __init__(self):
        self.command_history = []
    
    def simulate_ssh_command(self, command: str) -> Dict[str, Any]:
        """模拟 SSH 命令执行"""
        try:
            logger.info(f"模拟 SSH 命令: {command}")
            
            # 记录命令历史
            command_record = {
                "timestamp": datetime.now().isoformat(),
                "command": command,
                "type": "ssh_command"
            }
            self.command_history.append(command_record)
            
            # 模拟不同命令的响应
            if "init_aicore.sh" in command:
                # 模拟 init_aicore.sh 执行
                time.sleep(2)
                return {
                    "exit_code": 0,
                    "stdout": "🎉 AICore 本地环境初始化成功！",
                    "stderr": "",
                    "execution_time": 2.0
                }
            elif "test" in command:
                return {
                    "exit_code": 0,
                    "stdout": "SSH connection test successful",
                    "stderr": "",
                    "execution_time": 0.1
                }
            else:
                return {
                    "exit_code": 0,
                    "stdout": f"Command executed: {command}",
                    "stderr": "",
                    "execution_time": 0.5
                }
                
        except Exception as e:
            return {
                "exit_code": 1,
                "stdout": "",
                "stderr": str(e),
                "execution_time": 0
            }

def create_test_init_script():
    """创建测试用的 init_aicore.sh 脚本"""
    script_content = """#!/bin/bash
# 测试用的 init_aicore.sh 脚本

echo "🚀 AICore 本地环境初始化开始..."
sleep 1

echo "✅ 系统要求检查通过"
sleep 0.5

echo "🔧 PowerAutomation_local 初始化完成"
sleep 0.5

echo "🌐 AIWeb & SmartUI 组件初始化完成"
sleep 0.5

echo "🔗 PowerAutomation_local MCP 适配器启动成功"
sleep 0.5

echo "🌐 AIWeb & SmartUI 组件启动成功"
sleep 0.5

echo "📊 本地环境状态验证通过"
sleep 0.5

echo "🎉 AICore 本地环境初始化成功！"
echo ""
echo "服务状态:"
echo "• AIWeb 入口: http://localhost:8081 ✅"
echo "• SmartUI IDE: http://localhost:3000 ✅"
echo "• SmartUI 后端 API: http://localhost:5001 ✅"
echo "• PowerAutomation_local MCP: ✅ 运行中"

exit 0
"""
    
    script_path = Path("./test_init_aicore.sh")
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # 设置执行权限
    os.chmod(script_path, 0o755)
    
    logger.info(f"✅ 创建测试脚本: {script_path}")
    return script_path

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="模拟本地环境用于测试")
    parser.add_argument("--port", type=int, default=8082, help="HTTP 服务端口")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--create-script", action="store_true", help="创建测试脚本")
    
    args = parser.parse_args()
    
    if args.create_script:
        create_test_init_script()
        return
    
    # 创建并运行模拟环境
    mock_env = MockLocalEnvironment(port=args.port)
    
    try:
        mock_env.run(debug=args.debug)
    except KeyboardInterrupt:
        logger.info("🛑 模拟环境已停止")

if __name__ == "__main__":
    main()

