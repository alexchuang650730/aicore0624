"""
PowerAutomation Local MCP Extension Manager

VSCode Extension組件管理器，提供用戶界面和IDE集成功能

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
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.exceptions import ExtensionError, async_handle_exceptions
from shared.utils import ensure_directory, format_duration


class ExtensionManager:
    """VSCode Extension組件管理器"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        初始化Extension Manager
        
        Args:
            config: 擴展配置
            logger: 日誌器
        """
        self.config = config
        self.logger = logger
        
        # 配置參數
        self.auto_start = config.get("auto_start", True)
        self.sidebar_enabled = config.get("sidebar_enabled", True)
        self.notifications_enabled = config.get("notifications_enabled", True)
        self.theme = config.get("theme", "dark")
        self.auto_refresh = config.get("auto_refresh", True)
        self.refresh_interval = config.get("refresh_interval", 30)
        self.max_history_items = config.get("max_history_items", 100)
        
        # 命令配置
        self.commands = config.get("commands", {})
        
        # 狀態信息
        self.status = {
            "initialized": False,
            "running": False,
            "vscode_connected": False,
            "active_sessions": 0,
            "command_count": 0,
            "last_activity": None
        }
        
        # 會話管理
        self.active_sessions = {}
        self.command_history = []
    
    async def initialize(self) -> bool:
        """
        初始化Extension Manager
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.logger.info("正在初始化Extension Manager...")
            
            # 檢查VSCode是否安裝
            if not await self._check_vscode_installation():
                self.logger.warning("VSCode未安裝或不在PATH中")
            
            # 創建擴展目錄
            await self._create_extension_structure()
            
            # 生成擴展文件
            await self._generate_extension_files()
            
            self.status["initialized"] = True
            self.logger.info("Extension Manager初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"Extension Manager初始化失敗: {e}")
            return False
    
    async def start(self) -> bool:
        """
        啟動Extension Manager
        
        Returns:
            bool: 啟動是否成功
        """
        try:
            if not self.status["initialized"]:
                raise ExtensionError("Extension Manager未初始化")
            
            self.logger.info("正在啟動Extension Manager...")
            
            # 安裝VSCode擴展
            if await self._install_extension():
                self.status["vscode_connected"] = True
            
            # 啟動後台任務
            if self.auto_refresh:
                asyncio.create_task(self._background_refresh())
            
            self.status["running"] = True
            self.logger.info("Extension Manager已啟動")
            return True
            
        except Exception as e:
            self.logger.error(f"啟動Extension Manager失敗: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        停止Extension Manager
        
        Returns:
            bool: 停止是否成功
        """
        try:
            self.logger.info("正在停止Extension Manager...")
            
            # 清理活動會話
            self.active_sessions.clear()
            
            self.status["running"] = False
            self.status["vscode_connected"] = False
            self.status["active_sessions"] = 0
            
            self.logger.info("Extension Manager已停止")
            return True
            
        except Exception as e:
            self.logger.error(f"停止Extension Manager失敗: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """
        獲取Extension Manager狀態
        
        Returns:
            Dict[str, Any]: 狀態信息
        """
        try:
            status = self.status.copy()
            
            # 添加會話信息
            status["sessions"] = list(self.active_sessions.keys())
            status["active_sessions"] = len(self.active_sessions)
            
            # 添加配置信息
            status["config"] = {
                "auto_start": self.auto_start,
                "sidebar_enabled": self.sidebar_enabled,
                "notifications_enabled": self.notifications_enabled,
                "theme": self.theme,
                "auto_refresh": self.auto_refresh,
                "refresh_interval": self.refresh_interval
            }
            
            # 添加最近的命令歷史
            status["recent_commands"] = self.command_history[-10:] if self.command_history else []
            
            return status
            
        except Exception as e:
            self.logger.error(f"獲取Extension狀態失敗: {e}")
            return {"error": str(e)}
    
    async def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理擴展請求
        
        Args:
            method: 方法名
            params: 參數
            
        Returns:
            Dict[str, Any]: 響應數據
        """
        try:
            self.status["command_count"] += 1
            self.status["last_activity"] = time.time()
            
            self.logger.debug(f"處理Extension請求: {method}")
            
            # 記錄命令歷史
            command_record = {
                "method": method,
                "params": params,
                "timestamp": time.time()
            }
            self.command_history.append(command_record)
            
            # 限制歷史記錄數量
            if len(self.command_history) > self.max_history_items:
                self.command_history = self.command_history[-self.max_history_items:]
            
            # 路由到相應的方法
            if method == "create_session":
                session_id = params.get("session_id", f"session_{int(time.time())}")
                result = await self.create_session(session_id)
                return {"success": result, "session_id": session_id}
                
            elif method == "close_session":
                session_id = params.get("session_id", "")
                result = await self.close_session(session_id)
                return {"success": result, "message": "會話已關閉"}
                
            elif method == "send_notification":
                message = params.get("message", "")
                level = params.get("level", "info")
                result = await self.send_notification(message, level)
                return {"success": result, "message": "通知已發送"}
                
            elif method == "update_sidebar":
                data = params.get("data", {})
                result = await self.update_sidebar(data)
                return {"success": result, "message": "側邊欄已更新"}
                
            elif method == "execute_command":
                command = params.get("command", "")
                args = params.get("args", [])
                result = await self.execute_command(command, args)
                return {"success": result, "message": "命令執行完成"}
                
            else:
                raise ExtensionError(f"未知的Extension方法: {method}")
            
        except Exception as e:
            self.logger.error(f"處理Extension請求失敗: {e}")
            raise
    
    @async_handle_exceptions(default_return=False)
    async def create_session(self, session_id: str) -> bool:
        """
        創建會話
        
        Args:
            session_id: 會話ID
            
        Returns:
            bool: 創建是否成功
        """
        try:
            self.logger.info(f"創建會話: {session_id}")
            
            session_info = {
                "session_id": session_id,
                "created_at": time.time(),
                "last_activity": time.time(),
                "commands_executed": 0,
                "status": "active"
            }
            
            self.active_sessions[session_id] = session_info
            self.status["active_sessions"] = len(self.active_sessions)
            
            # 發送歡迎通知
            if self.notifications_enabled:
                await self.send_notification(f"PowerAutomation會話 {session_id} 已創建", "info")
            
            return True
            
        except Exception as e:
            self.logger.error(f"創建會話失敗: {e}")
            raise ExtensionError(f"創建會話失敗: {e}", command="create_session")
    
    @async_handle_exceptions(default_return=False)
    async def close_session(self, session_id: str) -> bool:
        """
        關閉會話
        
        Args:
            session_id: 會話ID
            
        Returns:
            bool: 關閉是否成功
        """
        try:
            if session_id not in self.active_sessions:
                self.logger.warning(f"會話不存在: {session_id}")
                return False
            
            self.logger.info(f"關閉會話: {session_id}")
            
            # 更新會話狀態
            session_info = self.active_sessions[session_id]
            session_info["status"] = "closed"
            session_info["closed_at"] = time.time()
            
            # 移除活動會話
            del self.active_sessions[session_id]
            self.status["active_sessions"] = len(self.active_sessions)
            
            # 發送關閉通知
            if self.notifications_enabled:
                duration = session_info.get("closed_at", time.time()) - session_info.get("created_at", time.time())
                await self.send_notification(
                    f"PowerAutomation會話 {session_id} 已關閉 (持續時間: {format_duration(duration)})",
                    "info"
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"關閉會話失敗: {e}")
            raise ExtensionError(f"關閉會話失敗: {e}", command="close_session")
    
    @async_handle_exceptions(default_return=False)
    async def send_notification(self, message: str, level: str = "info") -> bool:
        """
        發送通知
        
        Args:
            message: 通知消息
            level: 通知級別 (info, warning, error)
            
        Returns:
            bool: 發送是否成功
        """
        try:
            if not self.notifications_enabled:
                return True
            
            self.logger.info(f"發送通知 [{level}]: {message}")
            
            # 構建通知數據
            notification = {
                "message": message,
                "level": level,
                "timestamp": time.time(),
                "source": "PowerAutomation"
            }
            
            # 這裡可以實現實際的VSCode通知發送邏輯
            # 例如通過VSCode API或者文件系統通信
            
            return True
            
        except Exception as e:
            self.logger.error(f"發送通知失敗: {e}")
            raise ExtensionError(f"發送通知失敗: {e}", command="send_notification")
    
    @async_handle_exceptions(default_return=False)
    async def update_sidebar(self, data: Dict[str, Any]) -> bool:
        """
        更新側邊欄
        
        Args:
            data: 側邊欄數據
            
        Returns:
            bool: 更新是否成功
        """
        try:
            if not self.sidebar_enabled:
                return True
            
            self.logger.info("更新側邊欄")
            
            # 構建側邊欄數據
            sidebar_data = {
                "status": data.get("status", {}),
                "recent_activities": data.get("recent_activities", []),
                "quick_actions": data.get("quick_actions", []),
                "statistics": data.get("statistics", {}),
                "timestamp": time.time()
            }
            
            # 這裡可以實現實際的側邊欄更新邏輯
            # 例如寫入到VSCode擴展可以讀取的文件
            
            return True
            
        except Exception as e:
            self.logger.error(f"更新側邊欄失敗: {e}")
            raise ExtensionError(f"更新側邊欄失敗: {e}", command="update_sidebar")
    
    @async_handle_exceptions(default_return=False)
    async def execute_command(self, command: str, args: List[str] = None) -> bool:
        """
        執行命令
        
        Args:
            command: 命令名稱
            args: 命令參數
            
        Returns:
            bool: 執行是否成功
        """
        try:
            if args is None:
                args = []
            
            self.logger.info(f"執行命令: {command} {args}")
            
            # 檢查命令是否在配置中
            if command not in self.commands:
                raise ExtensionError(f"未知命令: {command}")
            
            # 這裡可以實現實際的命令執行邏輯
            # 例如調用相應的PowerAutomation功能
            
            return True
            
        except Exception as e:
            self.logger.error(f"執行命令失敗: {e}")
            raise ExtensionError(f"執行命令失敗: {e}", command="execute_command")
    
    async def _check_vscode_installation(self) -> bool:
        """檢查VSCode是否安裝"""
        try:
            result = subprocess.run(["code", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    async def _create_extension_structure(self):
        """創建擴展目錄結構"""
        try:
            extension_dir = os.path.join(os.getcwd(), "vscode-extension")
            ensure_directory(extension_dir)
            
            # 創建子目錄
            subdirs = ["src", "resources", "out", "media"]
            for subdir in subdirs:
                ensure_directory(os.path.join(extension_dir, subdir))
            
        except Exception as e:
            raise ExtensionError(f"創建擴展目錄結構失敗: {e}")
    
    async def _generate_extension_files(self):
        """生成擴展文件"""
        try:
            extension_dir = os.path.join(os.getcwd(), "vscode-extension")
            
            # 生成package.json
            package_json = {
                "name": "powerautomation-local",
                "displayName": "PowerAutomation Local",
                "description": "PowerAutomation Local MCP Extension",
                "version": "1.0.0",
                "engines": {
                    "vscode": "^1.60.0"
                },
                "categories": ["Other"],
                "activationEvents": ["*"],
                "main": "./out/extension.js",
                "contributes": {
                    "commands": [
                        {
                            "command": "powerautomation.login",
                            "title": "Login to Manus",
                            "category": "PowerAutomation"
                        },
                        {
                            "command": "powerautomation.sendMessage",
                            "title": "Send Message",
                            "category": "PowerAutomation"
                        },
                        {
                            "command": "powerautomation.getConversations",
                            "title": "Get Conversations",
                            "category": "PowerAutomation"
                        },
                        {
                            "command": "powerautomation.getTasks",
                            "title": "Get Tasks",
                            "category": "PowerAutomation"
                        },
                        {
                            "command": "powerautomation.runTest",
                            "title": "Run Test",
                            "category": "PowerAutomation"
                        },
                        {
                            "command": "powerautomation.viewStatus",
                            "title": "View Status",
                            "category": "PowerAutomation"
                        }
                    ],
                    "views": {
                        "explorer": [
                            {
                                "id": "powerautomationView",
                                "name": "PowerAutomation",
                                "when": "true"
                            }
                        ]
                    },
                    "configuration": {
                        "title": "PowerAutomation",
                        "properties": {
                            "powerautomation.serverUrl": {
                                "type": "string",
                                "default": "http://localhost:5000",
                                "description": "PowerAutomation Server URL"
                            },
                            "powerautomation.autoStart": {
                                "type": "boolean",
                                "default": True,
                                "description": "Auto start PowerAutomation"
                            }
                        }
                    }
                },
                "scripts": {
                    "vscode:prepublish": "npm run compile",
                    "compile": "tsc -p ./",
                    "watch": "tsc -watch -p ./"
                },
                "devDependencies": {
                    "@types/vscode": "^1.60.0",
                    "@types/node": "14.x",
                    "typescript": "^4.4.4"
                }
            }
            
            with open(os.path.join(extension_dir, "package.json"), 'w') as f:
                json.dump(package_json, f, indent=2)
            
            # 生成TypeScript配置
            tsconfig = {
                "compilerOptions": {
                    "module": "commonjs",
                    "target": "es6",
                    "outDir": "out",
                    "lib": ["es6"],
                    "sourceMap": True,
                    "rootDir": "src",
                    "strict": True
                },
                "exclude": ["node_modules", ".vscode-test"]
            }
            
            with open(os.path.join(extension_dir, "tsconfig.json"), 'w') as f:
                json.dump(tsconfig, f, indent=2)
            
            # 生成主擴展文件
            extension_ts = '''
import * as vscode from 'vscode';
import * as http from 'http';

export function activate(context: vscode.ExtensionContext) {
    console.log('PowerAutomation Extension is now active!');
    
    // 註冊命令
    const commands = [
        vscode.commands.registerCommand('powerautomation.login', () => {
            callPowerAutomationAPI('manus/login', {});
        }),
        vscode.commands.registerCommand('powerautomation.sendMessage', async () => {
            const message = await vscode.window.showInputBox({
                prompt: 'Enter message to send'
            });
            if (message) {
                callPowerAutomationAPI('manus/send_message', { message });
            }
        }),
        vscode.commands.registerCommand('powerautomation.getConversations', () => {
            callPowerAutomationAPI('manus/conversations', {});
        }),
        vscode.commands.registerCommand('powerautomation.getTasks', () => {
            callPowerAutomationAPI('manus/tasks', {});
        }),
        vscode.commands.registerCommand('powerautomation.runTest', async () => {
            const testCase = await vscode.window.showQuickPick([
                'TC001', 'TC002', 'TC003', 'TC004', 'TC005', 'TC006'
            ], {
                placeHolder: 'Select test case to run'
            });
            if (testCase) {
                callPowerAutomationAPI('automation/run_test', { test_case: testCase });
            }
        }),
        vscode.commands.registerCommand('powerautomation.viewStatus', () => {
            callPowerAutomationAPI('status', {});
        })
    ];
    
    commands.forEach(command => context.subscriptions.push(command));
    
    // 創建狀態欄項目
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(gear) PowerAutomation";
    statusBarItem.command = 'powerautomation.viewStatus';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
}

function callPowerAutomationAPI(endpoint: string, data: any) {
    const config = vscode.workspace.getConfiguration('powerautomation');
    const serverUrl = config.get('serverUrl', 'http://localhost:5000');
    
    const postData = JSON.stringify(data);
    const url = new URL(`/api/${endpoint}`, serverUrl);
    
    const options = {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(postData)
        }
    };
    
    const req = http.request(options, (res) => {
        let responseData = '';
        res.on('data', (chunk) => {
            responseData += chunk;
        });
        res.on('end', () => {
            try {
                const result = JSON.parse(responseData);
                vscode.window.showInformationMessage(`PowerAutomation: ${JSON.stringify(result)}`);
            } catch (error) {
                vscode.window.showErrorMessage(`PowerAutomation Error: ${error}`);
            }
        });
    });
    
    req.on('error', (error) => {
        vscode.window.showErrorMessage(`PowerAutomation Request Error: ${error.message}`);
    });
    
    req.write(postData);
    req.end();
}

export function deactivate() {}
'''
            
            with open(os.path.join(extension_dir, "src", "extension.ts"), 'w') as f:
                f.write(extension_ts)
            
        except Exception as e:
            raise ExtensionError(f"生成擴展文件失敗: {e}")
    
    async def _install_extension(self) -> bool:
        """安裝VSCode擴展"""
        try:
            extension_dir = os.path.join(os.getcwd(), "vscode-extension")
            
            # 編譯TypeScript
            result = subprocess.run(["npm", "run", "compile"], 
                                  cwd=extension_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.warning(f"編譯擴展失敗: {result.stderr}")
                return False
            
            # 安裝擴展（開發模式）
            result = subprocess.run(["code", "--install-extension", extension_dir], 
                                  capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"安裝擴展失敗: {e}")
            return False
    
    async def _background_refresh(self):
        """後台刷新任務"""
        try:
            while self.status["running"]:
                # 更新側邊欄數據
                if self.sidebar_enabled:
                    sidebar_data = {
                        "status": self.status,
                        "recent_activities": self.command_history[-5:],
                        "statistics": {
                            "active_sessions": len(self.active_sessions),
                            "total_commands": self.status["command_count"]
                        }
                    }
                    await self.update_sidebar(sidebar_data)
                
                # 等待刷新間隔
                await asyncio.sleep(self.refresh_interval)
                
        except Exception as e:
            self.logger.error(f"後台刷新任務失敗: {e}")

