"""
PowerAutomation Local MCP Server Manager

管理Local Server組件的生命週期和功能
提供Flask API服務和Manus集成功能

Author: Manus AI
Version: 1.0.0
Date: 2025-06-23
"""

import asyncio
import json
import logging
import os
import sys
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.exceptions import ServerError, ManusError, async_handle_exceptions
from shared.utils import ensure_directory, format_bytes, format_duration
from .integrations.manus_integration import ManusIntegration
from .automation.automation_engine import AutomationEngine
from .storage.data_storage import DataStorage


class ServerManager:
    """Local Server組件管理器"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        初始化Server Manager
        
        Args:
            config: 服務器配置
            logger: 日誌器
        """
        self.config = config
        self.logger = logger
        self.app = None
        self.server_thread = None
        self.running = False
        
        # 組件實例
        self.manus_integration = None
        self.automation_engine = None
        self.data_storage = None
        
        # 狀態信息
        self.status = {
            "initialized": False,
            "running": False,
            "start_time": None,
            "request_count": 0,
            "error_count": 0,
            "last_request_time": None
        }
    
    async def initialize(self) -> bool:
        """
        初始化Server Manager
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.logger.info("正在初始化Server Manager...")
            
            # 創建Flask應用
            self._create_flask_app()
            
            # 初始化組件
            await self._initialize_components()
            
            # 註冊路由
            self._register_routes()
            
            self.status["initialized"] = True
            self.logger.info("Server Manager初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"Server Manager初始化失敗: {e}")
            return False
    
    async def start(self) -> bool:
        """
        啟動Local Server
        
        Returns:
            bool: 啟動是否成功
        """
        try:
            if self.running:
                self.logger.warning("Server已經在運行中")
                return True
            
            self.logger.info("正在啟動Local Server...")
            
            # 檢查端口可用性
            host = self.config.get("host", "0.0.0.0")
            port = self.config.get("port", 5000)
            
            if not self._is_port_available(port):
                raise ServerError(f"端口 {port} 已被占用")
            
            # 啟動Flask服務器
            self._start_flask_server()
            
            # 啟動組件
            await self._start_components()
            
            self.running = True
            self.status["running"] = True
            self.status["start_time"] = time.time()
            
            self.logger.info(f"Local Server已啟動 - {host}:{port}")
            return True
            
        except Exception as e:
            self.logger.error(f"啟動Local Server失敗: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        停止Local Server
        
        Returns:
            bool: 停止是否成功
        """
        try:
            if not self.running:
                self.logger.warning("Server未在運行")
                return True
            
            self.logger.info("正在停止Local Server...")
            
            # 停止組件
            await self._stop_components()
            
            # 停止Flask服務器
            self._stop_flask_server()
            
            self.running = False
            self.status["running"] = False
            
            self.logger.info("Local Server已停止")
            return True
            
        except Exception as e:
            self.logger.error(f"停止Local Server失敗: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """
        獲取服務器狀態
        
        Returns:
            Dict[str, Any]: 服務器狀態
        """
        try:
            status = self.status.copy()
            
            # 添加運行時間
            if status["start_time"]:
                status["uptime"] = time.time() - status["start_time"]
                status["uptime_formatted"] = format_duration(status["uptime"])
            
            # 添加組件狀態
            if self.manus_integration:
                status["manus"] = await self.manus_integration.get_status()
            
            if self.automation_engine:
                status["automation"] = await self.automation_engine.get_status()
            
            if self.data_storage:
                status["storage"] = await self.data_storage.get_status()
            
            # 添加配置信息
            status["config"] = {
                "host": self.config.get("host", "0.0.0.0"),
                "port": self.config.get("port", 5000),
                "debug": self.config.get("debug", False),
                "cors_enabled": self.config.get("cors_enabled", True)
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"獲取服務器狀態失敗: {e}")
            return {"error": str(e)}
    
    async def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理API請求
        
        Args:
            method: 方法名
            params: 參數
            
        Returns:
            Dict[str, Any]: 響應數據
        """
        try:
            self.status["request_count"] += 1
            self.status["last_request_time"] = time.time()
            
            self.logger.debug(f"處理Server請求: {method}")
            
            # 路由到相應的處理器
            if method.startswith("manus_"):
                if not self.manus_integration:
                    raise ServerError("Manus Integration未初始化")
                return await self.manus_integration.handle_request(method[6:], params)
                
            elif method.startswith("automation_"):
                if not self.automation_engine:
                    raise ServerError("Automation Engine未初始化")
                return await self.automation_engine.handle_request(method[11:], params)
                
            elif method.startswith("storage_"):
                if not self.data_storage:
                    raise ServerError("Data Storage未初始化")
                return await self.data_storage.handle_request(method[8:], params)
                
            elif method == "get_status":
                return await self.get_status()
                
            else:
                raise ServerError(f"未知的Server方法: {method}")
            
        except Exception as e:
            self.status["error_count"] += 1
            self.logger.error(f"處理Server請求失敗: {e}")
            raise
    
    def _create_flask_app(self):
        """創建Flask應用"""
        self.app = Flask(__name__)
        
        # 配置CORS
        if self.config.get("cors_enabled", True):
            CORS(self.app, origins="*")
        
        # 配置Flask
        self.app.config['JSON_AS_ASCII'] = False
        self.app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    async def _initialize_components(self):
        """初始化組件"""
        try:
            # 初始化Manus Integration
            self.manus_integration = ManusIntegration(
                config=self.config.get("manus", {}),
                logger=self.logger
            )
            await self.manus_integration.initialize()
            
            # 初始化Automation Engine
            self.automation_engine = AutomationEngine(
                config=self.config.get("automation", {}),
                logger=self.logger
            )
            await self.automation_engine.initialize()
            
            # 初始化Data Storage
            self.data_storage = DataStorage(
                config=self.config.get("storage", {}),
                logger=self.logger
            )
            await self.data_storage.initialize()
            
        except Exception as e:
            raise ServerError(f"初始化組件失敗: {e}")
    
    def _register_routes(self):
        """註冊Flask路由"""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """獲取狀態"""
            try:
                # 由於Flask路由是同步的，我們需要在新的事件循環中運行異步方法
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                status = loop.run_until_complete(self.get_status())
                loop.close()
                
                return jsonify(status)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/manus/login', methods=['POST'])
        def manus_login():
            """Manus登錄"""
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.manus_integration.handle_request("login", {})
                )
                loop.close()
                
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/manus/send_message', methods=['POST'])
        def send_message():
            """發送消息"""
            try:
                data = request.get_json()
                message = data.get("message", "")
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.manus_integration.handle_request("send_message", {"message": message})
                )
                loop.close()
                
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/manus/conversations', methods=['GET'])
        def get_conversations():
            """獲取對話歷史"""
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.manus_integration.handle_request("get_conversations", {})
                )
                loop.close()
                
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/manus/tasks', methods=['GET'])
        def get_tasks():
            """獲取任務列表"""
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.manus_integration.handle_request("get_tasks", {})
                )
                loop.close()
                
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/automation/run_test', methods=['POST'])
        def run_test():
            """運行自動化測試"""
            try:
                data = request.get_json()
                test_case = data.get("test_case", "")
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.automation_engine.handle_request("run_test", {"test_case": test_case})
                )
                loop.close()
                
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/storage/search', methods=['POST'])
        def search_data():
            """搜索數據"""
            try:
                data = request.get_json()
                query = data.get("query", "")
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.data_storage.handle_request("search", {"query": query})
                )
                loop.close()
                
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        # 健康檢查端點
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """健康檢查"""
            return jsonify({
                "status": "healthy",
                "timestamp": time.time(),
                "uptime": time.time() - self.status.get("start_time", time.time())
            })
    
    def _start_flask_server(self):
        """啟動Flask服務器"""
        def run_server():
            host = self.config.get("host", "0.0.0.0")
            port = self.config.get("port", 5000)
            debug = self.config.get("debug", False)
            
            self.app.run(
                host=host,
                port=port,
                debug=debug,
                threaded=True,
                use_reloader=False
            )
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # 等待服務器啟動
        time.sleep(2)
    
    def _stop_flask_server(self):
        """停止Flask服務器"""
        # Flask服務器會在主線程結束時自動停止
        if self.server_thread and self.server_thread.is_alive():
            # 發送停止信號
            try:
                host = self.config.get("host", "localhost")
                port = self.config.get("port", 5000)
                requests.get(f"http://{host}:{port}/shutdown", timeout=1)
            except:
                pass
    
    async def _start_components(self):
        """啟動組件"""
        try:
            if self.manus_integration:
                await self.manus_integration.start()
            
            if self.automation_engine:
                await self.automation_engine.start()
            
            if self.data_storage:
                await self.data_storage.start()
                
        except Exception as e:
            raise ServerError(f"啟動組件失敗: {e}")
    
    async def _stop_components(self):
        """停止組件"""
        try:
            if self.manus_integration:
                await self.manus_integration.stop()
            
            if self.automation_engine:
                await self.automation_engine.stop()
            
            if self.data_storage:
                await self.data_storage.stop()
                
        except Exception as e:
            self.logger.error(f"停止組件時發生錯誤: {e}")
    
    def _is_port_available(self, port: int) -> bool:
        """檢查端口是否可用"""
        import socket
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(("localhost", port))
                return result != 0
        except Exception:
            return False

