"""
PowerAutomation Local MCP Manus Integration with Replay Chain Support
整合Replay鏈結功能的Manus平台集成模組

Author: Manus AI
Version: 2.0.0
Date: 2025-06-23
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Browser, Page

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.exceptions import ManusError, async_handle_exceptions
from shared.utils import ensure_directory, safe_json_dumps
from manus_replay_chain_core import (
    ReplayChainManager, TaskNode, TaskStatus, ChainStatus,
    ChainExecutionResult, TaskExecutionResult
)


class MCPManusIntegration:
    """MCP架構下的Manus平台集成模組，支持Replay鏈結功能"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        初始化MCP Manus Integration
        
        Args:
            config: Manus配置
            logger: 日誌器
        """
        self.config = config
        self.logger = logger
        self.playwright = None
        self.browser = None
        self.page = None
        self.logged_in = False
        
        # Replay鏈結管理器
        self.chain_manager = ReplayChainManager()
        
        # 配置參數
        self.base_url = config.get("base_url", "https://manus.im")
        self.app_url = config.get("app_url", "")
        self.login_email = config.get("login_email", "")
        self.login_password = config.get("login_password", "")
        self.auto_login = config.get("auto_login", True)
        self.keep_alive = config.get("keep_alive", True)
        self.headless = config.get("headless", False)
        self.slow_mo = config.get("slow_mo", 1000)
        
        # 狀態追蹤
        self.status = {
            "connected": False,
            "logged_in": False,
            "session_start_time": None,
            "last_activity_time": None,
            "operation_count": 0,
            "error_count": 0,
            "chain_count": 0,
            "active_executions": 0
        }
        
        # MCP消息處理器映射
        self.mcp_handlers = {
            # 基本操作
            "login": self._handle_login,
            "logout": self._handle_logout,
            "send_message": self._handle_send_message,
            "get_conversations": self._handle_get_conversations,
            "get_tasks": self._handle_get_tasks,
            "download_files": self._handle_download_files,
            
            # Replay鏈結操作
            "create_task": self._handle_create_task,
            "create_chain": self._handle_create_chain,
            "execute_chain": self._handle_execute_chain,
            "get_chain_status": self._handle_get_chain_status,
            "list_chains": self._handle_list_chains,
            "delete_chain": self._handle_delete_chain,
            "auto_generate_chains": self._handle_auto_generate_chains,
            
            # 監控和管理
            "get_execution_progress": self._handle_get_execution_progress,
            "cancel_execution": self._handle_cancel_execution,
            "get_system_status": self._handle_get_system_status
        }
    
    async def initialize(self) -> bool:
        """
        初始化MCP Manus Integration
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.logger.info("初始化MCP Manus Integration...")
            
            # 啟動Playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo
            )
            
            # 創建頁面
            self.page = await self.browser.new_page()
            
            # 設置頁面配置
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            await self.page.set_extra_http_headers({
                "User-Agent": "PowerAutomation/2.0.0 MCP Client"
            })
            
            self.status["connected"] = True
            self.status["session_start_time"] = time.time()
            
            # 自動登錄
            if self.auto_login and self.login_email and self.login_password:
                await self.login()
            
            self.logger.info("✅ MCP Manus Integration初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化MCP Manus Integration失敗: {e}")
            return False
    
    async def cleanup(self):
        """清理資源"""
        try:
            # 清理鏈結管理器
            await self.chain_manager.cleanup()
            
            # 關閉瀏覽器
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            self.status["connected"] = False
            self.status["logged_in"] = False
            
            self.logger.info("✅ MCP Manus Integration已清理")
            
        except Exception as e:
            self.logger.error(f"清理資源失敗: {e}")
    
    async def handle_mcp_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理MCP請求
        
        Args:
            method: 方法名
            params: 參數
            
        Returns:
            Dict[str, Any]: 響應數據
        """
        try:
            self.status["operation_count"] += 1
            self.status["last_activity_time"] = time.time()
            
            self.logger.debug(f"處理MCP請求: {method}")
            
            # 檢查方法是否支持
            if method not in self.mcp_handlers:
                raise ManusError(f"不支持的方法: {method}")
            
            # 調用相應的處理器
            handler = self.mcp_handlers[method]
            result = await handler(params)
            
            # 包裝響應
            response = {
                "success": True,
                "method": method,
                "result": result,
                "timestamp": time.time(),
                "execution_time": time.time() - self.status["last_activity_time"]
            }
            
            return response
            
        except Exception as e:
            self.status["error_count"] += 1
            self.logger.error(f"處理MCP請求失敗: {method}, 錯誤: {e}")
            
            return {
                "success": False,
                "method": method,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": time.time()
            }
    
    # ==================== 基本操作處理器 ====================
    
    async def _handle_login(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理登錄請求"""
        email = params.get("email", self.login_email)
        password = params.get("password", self.login_password)
        
        if not email or not password:
            raise ManusError("缺少登錄憑證")
        
        result = await self.login(email, password)
        return result
    
    async def _handle_logout(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理登出請求"""
        result = await self.logout()
        return result
    
    async def _handle_send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理發送消息請求"""
        message = params.get("message", "")
        if not message:
            raise ManusError("消息內容不能為空")
        
        result = await self.send_message(message)
        return result
    
    async def _handle_get_conversations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理獲取對話請求"""
        conversations = await self.get_conversations()
        return {"conversations": conversations, "count": len(conversations)}
    
    async def _handle_get_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理獲取任務請求"""
        tasks = await self.get_tasks()
        return {"tasks": tasks, "count": len(tasks)}
    
    async def _handle_download_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理下載文件請求"""
        task_id = params.get("task_id", "")
        files = await self.download_files(task_id)
        return {"files": files, "count": len(files)}
    
    # ==================== Replay鏈結操作處理器 ====================
    
    async def _handle_create_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理創建任務請求"""
        try:
            # 提取任務參數
            task_type = params.get("task_type", "")
            description = params.get("description", "")
            task_params = params.get("parameters", {})
            priority = params.get("priority", 5)
            dependencies = params.get("dependencies", [])
            
            if not task_type:
                raise ManusError("任務類型不能為空")
            
            # 創建任務節點
            task_node = TaskNode(
                task_id=f"task_{int(time.time() * 1000)}_{len(self.chain_manager.tasks)}",
                task_type=task_type,
                description=description,
                parameters=task_params,
                priority=priority,
                dependencies=dependencies
            )
            
            # 添加到管理器
            task_id = await self.chain_manager.add_task(task_node)
            
            return {
                "task_id": task_id,
                "task_type": task_type,
                "description": description,
                "status": "created"
            }
            
        except Exception as e:
            raise ManusError(f"創建任務失敗: {e}")
    
    async def _handle_create_chain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理創建鏈結請求"""
        try:
            task_ids = params.get("task_ids", [])
            chain_name = params.get("chain_name")
            
            if len(task_ids) < 2:
                raise ManusError("至少需要2個任務才能創建鏈結")
            
            # 創建鏈結
            chain_id = await self.chain_manager.create_chain_from_tasks(task_ids, chain_name)
            
            if not chain_id:
                raise ManusError("創建鏈結失敗")
            
            self.status["chain_count"] += 1
            
            # 獲取鏈結詳情
            chain = await self.chain_manager.get_chain(chain_id)
            
            return {
                "chain_id": chain_id,
                "chain_name": chain.chain_name,
                "description": chain.description,
                "task_count": len(chain.nodes),
                "estimated_duration": chain.total_estimated_duration,
                "optimization_score": chain.optimization_score,
                "status": chain.status.value
            }
            
        except Exception as e:
            raise ManusError(f"創建鏈結失敗: {e}")
    
    async def _handle_execute_chain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理執行鏈結請求"""
        try:
            chain_id = params.get("chain_id", "")
            if not chain_id:
                raise ManusError("鏈結ID不能為空")
            
            # 檢查鏈結是否存在
            chain = await self.chain_manager.get_chain(chain_id)
            if not chain:
                raise ManusError(f"鏈結不存在: {chain_id}")
            
            self.status["active_executions"] += 1
            
            try:
                # 執行鏈結
                result = await self.chain_manager.execute_chain(chain_id)
                
                if result:
                    return {
                        "execution_id": result.execution_id,
                        "chain_id": result.chain_id,
                        "success": result.success,
                        "total_duration": result.total_duration,
                        "completed_tasks": len(result.node_results),
                        "successful_tasks": sum(1 for r in result.node_results if r.success),
                        "error_message": result.error_message,
                        "artifacts": result.artifacts
                    }
                else:
                    raise ManusError("執行鏈結失敗")
                    
            finally:
                self.status["active_executions"] -= 1
            
        except Exception as e:
            self.status["active_executions"] = max(0, self.status["active_executions"] - 1)
            raise ManusError(f"執行鏈結失敗: {e}")
    
    async def _handle_get_chain_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理獲取鏈結狀態請求"""
        try:
            chain_id = params.get("chain_id", "")
            if not chain_id:
                raise ManusError("鏈結ID不能為空")
            
            chain = await self.chain_manager.get_chain(chain_id)
            if not chain:
                raise ManusError(f"鏈結不存在: {chain_id}")
            
            # 獲取任務狀態統計
            task_status_counts = {}
            for node in chain.nodes:
                status = node.status.value
                task_status_counts[status] = task_status_counts.get(status, 0) + 1
            
            return {
                "chain_id": chain.chain_id,
                "chain_name": chain.chain_name,
                "status": chain.status.value,
                "task_count": len(chain.nodes),
                "task_status_counts": task_status_counts,
                "execution_count": chain.execution_count,
                "success_rate": chain.success_rate,
                "last_executed": chain.last_executed.isoformat() if chain.last_executed else None,
                "estimated_duration": chain.total_estimated_duration,
                "optimization_score": chain.optimization_score
            }
            
        except Exception as e:
            raise ManusError(f"獲取鏈結狀態失敗: {e}")
    
    async def _handle_list_chains(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理列出鏈結請求"""
        try:
            chains = await self.chain_manager.list_chains()
            
            chain_list = []
            for chain in chains:
                chain_info = {
                    "chain_id": chain.chain_id,
                    "chain_name": chain.chain_name,
                    "description": chain.description,
                    "status": chain.status.value,
                    "task_count": len(chain.nodes),
                    "execution_count": chain.execution_count,
                    "success_rate": chain.success_rate,
                    "optimization_score": chain.optimization_score,
                    "created_at": chain.created_at.isoformat(),
                    "last_executed": chain.last_executed.isoformat() if chain.last_executed else None
                }
                chain_list.append(chain_info)
            
            return {
                "chains": chain_list,
                "count": len(chain_list)
            }
            
        except Exception as e:
            raise ManusError(f"列出鏈結失敗: {e}")
    
    async def _handle_delete_chain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理刪除鏈結請求"""
        try:
            chain_id = params.get("chain_id", "")
            if not chain_id:
                raise ManusError("鏈結ID不能為空")
            
            success = await self.chain_manager.delete_chain(chain_id)
            
            if success:
                self.status["chain_count"] = max(0, self.status["chain_count"] - 1)
                return {"chain_id": chain_id, "deleted": True}
            else:
                raise ManusError(f"鏈結不存在: {chain_id}")
                
        except Exception as e:
            raise ManusError(f"刪除鏈結失敗: {e}")
    
    async def _handle_auto_generate_chains(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理自動生成鏈結請求"""
        try:
            # 自動生成鏈結
            chain_ids = await self.chain_manager.auto_generate_chains()
            
            self.status["chain_count"] += len(chain_ids)
            
            # 獲取生成的鏈結詳情
            chains_info = []
            for chain_id in chain_ids:
                chain = await self.chain_manager.get_chain(chain_id)
                if chain:
                    chains_info.append({
                        "chain_id": chain.chain_id,
                        "chain_name": chain.chain_name,
                        "description": chain.description,
                        "task_count": len(chain.nodes),
                        "optimization_score": chain.optimization_score
                    })
            
            return {
                "generated_chains": chains_info,
                "count": len(chains_info)
            }
            
        except Exception as e:
            raise ManusError(f"自動生成鏈結失敗: {e}")
    
    # ==================== 監控和管理處理器 ====================
    
    async def _handle_get_execution_progress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理獲取執行進度請求"""
        try:
            execution_id = params.get("execution_id", "")
            if not execution_id:
                raise ManusError("執行ID不能為空")
            
            status = await self.chain_manager.executor.get_execution_status(execution_id)
            
            if status:
                return status
            else:
                raise ManusError(f"執行不存在: {execution_id}")
                
        except Exception as e:
            raise ManusError(f"獲取執行進度失敗: {e}")
    
    async def _handle_cancel_execution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理取消執行請求"""
        try:
            execution_id = params.get("execution_id", "")
            if not execution_id:
                raise ManusError("執行ID不能為空")
            
            success = await self.chain_manager.executor.cancel_execution(execution_id)
            
            if success:
                self.status["active_executions"] = max(0, self.status["active_executions"] - 1)
                return {"execution_id": execution_id, "cancelled": True}
            else:
                raise ManusError(f"執行不存在或無法取消: {execution_id}")
                
        except Exception as e:
            raise ManusError(f"取消執行失敗: {e}")
    
    async def _handle_get_system_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理獲取系統狀態請求"""
        try:
            # 獲取基本狀態
            status = self.status.copy()
            
            # 添加會話信息
            if status["session_start_time"]:
                status["session_duration"] = time.time() - status["session_start_time"]
            
            # 添加鏈結管理器狀態
            status["total_tasks"] = len(self.chain_manager.tasks)
            status["total_chains"] = len(self.chain_manager.chains)
            
            # 添加任務狀態統計
            task_status_counts = {}
            for task in self.chain_manager.tasks.values():
                task_status = task.status.value
                task_status_counts[task_status] = task_status_counts.get(task_status, 0) + 1
            status["task_status_counts"] = task_status_counts
            
            # 添加鏈結狀態統計
            chain_status_counts = {}
            for chain in self.chain_manager.chains.values():
                chain_status = chain.status.value
                chain_status_counts[chain_status] = chain_status_counts.get(chain_status, 0) + 1
            status["chain_status_counts"] = chain_status_counts
            
            # 添加配置信息
            status["config"] = {
                "base_url": self.base_url,
                "app_url": self.app_url,
                "login_email": self.login_email,
                "auto_login": self.auto_login,
                "keep_alive": self.keep_alive,
                "headless": self.headless
            }
            
            return status
            
        except Exception as e:
            raise ManusError(f"獲取系統狀態失敗: {e}")
    
    # ==================== 原有的Manus操作方法 ====================
    
    @async_handle_exceptions(default_return={})
    async def login(self, email: str = None, password: str = None) -> Dict[str, Any]:
        """
        登錄Manus平台
        
        Args:
            email: 登錄郵箱
            password: 登錄密碼
            
        Returns:
            Dict[str, Any]: 登錄結果
        """
        try:
            if not self.page:
                raise ManusError("瀏覽器未初始化")
            
            email = email or self.login_email
            password = password or self.login_password
            
            if not email or not password:
                raise ManusError("缺少登錄憑證")
            
            self.logger.info(f"正在登錄Manus平台: {email}")
            
            # 導航到登錄頁面
            login_url = f"{self.base_url}/login" if not self.app_url else self.app_url
            await self.page.goto(login_url, wait_until="networkidle")
            
            # 查找並填寫郵箱
            email_input = await self.page.query_selector("input[type='email'], input[name='email']")
            if email_input:
                await email_input.fill(email)
            else:
                raise ManusError("找不到郵箱輸入框")
            
            # 查找並填寫密碼
            password_input = await self.page.query_selector("input[type='password'], input[name='password']")
            if password_input:
                await password_input.fill(password)
            else:
                raise ManusError("找不到密碼輸入框")
            
            # 查找並點擊登錄按鈕
            login_button = await self.page.query_selector("button[type='submit'], button:has-text('Login'), button:has-text('登錄')")
            if login_button:
                await login_button.click()
            else:
                # 嘗試按Enter鍵登錄
                await password_input.press("Enter")
            
            # 等待登錄完成
            await asyncio.sleep(3)
            
            # 檢查是否登錄成功
            current_url = self.page.url
            if "login" not in current_url.lower():
                self.logged_in = True
                self.status["logged_in"] = True
                self.logger.info("✅ 登錄成功")
                
                return {
                    "success": True,
                    "message": "登錄成功",
                    "email": email,
                    "current_url": current_url
                }
            else:
                raise ManusError("登錄失敗，請檢查憑證")
            
        except Exception as e:
            self.logger.error(f"登錄失敗: {e}")
            raise ManusError(f"登錄失敗: {e}", operation="login")
    
    @async_handle_exceptions(default_return={})
    async def logout(self) -> Dict[str, Any]:
        """
        登出Manus平台
        
        Returns:
            Dict[str, Any]: 登出結果
        """
        try:
            if not self.logged_in:
                return {"success": True, "message": "已經登出"}
            
            self.logger.info("正在登出Manus平台...")
            
            # 查找並點擊登出按鈕
            logout_button = await self.page.query_selector("button:has-text('Logout'), button:has-text('登出'), a:has-text('Logout')")
            if logout_button:
                await logout_button.click()
                await asyncio.sleep(2)
            
            self.logged_in = False
            self.status["logged_in"] = False
            
            self.logger.info("✅ 登出成功")
            return {"success": True, "message": "登出成功"}
            
        except Exception as e:
            self.logger.error(f"登出失敗: {e}")
            raise ManusError(f"登出失敗: {e}", operation="logout")
    
    @async_handle_exceptions(default_return={})
    async def send_message(self, message: str) -> Dict[str, Any]:
        """
        發送消息
        
        Args:
            message: 消息內容
            
        Returns:
            Dict[str, Any]: 發送結果
        """
        try:
            if not self.logged_in:
                await self.login()
            
            if not message.strip():
                raise ManusError("消息內容不能為空")
            
            self.logger.info(f"正在發送消息: {message[:50]}...")
            
            # 查找消息輸入框
            message_input = await self.page.query_selector("textarea, input[type='text']")
            if not message_input:
                raise ManusError("找不到消息輸入框")
            
            # 清空並輸入消息
            await message_input.fill("")
            await message_input.type(message)
            
            # 查找並點擊發送按鈕
            send_button = await self.page.query_selector("button[type='submit'], button:has-text('Send'), button:has-text('發送')")
            if send_button:
                await send_button.click()
            else:
                # 嘗試按Enter鍵發送
                await message_input.press("Enter")
            
            # 等待消息發送完成
            await asyncio.sleep(2)
            
            self.logger.info("✅ 消息發送成功")
            return {
                "success": True,
                "message": "消息發送成功",
                "content": message,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"發送消息失敗: {e}")
            raise ManusError(f"發送消息失敗: {e}", operation="send_message")
    
    @async_handle_exceptions(default_return=[])
    async def get_conversations(self) -> List[Dict[str, Any]]:
        """
        獲取對話歷史
        
        Returns:
            List[Dict[str, Any]]: 對話列表
        """
        try:
            if not self.logged_in:
                await self.login()
            
            self.logger.info("正在獲取對話歷史...")
            
            conversations = []
            
            # 查找對話元素
            conversation_elements = await self.page.query_selector_all(".conversation, .message, .chat-item")
            
            for element in conversation_elements:
                try:
                    # 提取對話信息
                    text = await element.text_content()
                    timestamp = await element.get_attribute("data-timestamp") or str(time.time())
                    
                    conversation = {
                        "text": text.strip(),
                        "timestamp": timestamp,
                        "extracted_at": time.time()
                    }
                    
                    conversations.append(conversation)
                    
                except Exception as e:
                    self.logger.warning(f"提取對話元素失敗: {e}")
                    continue
            
            self.logger.info(f"✅ 獲取到 {len(conversations)} 條對話記錄")
            return conversations
            
        except Exception as e:
            self.logger.error(f"獲取對話歷史失敗: {e}")
            raise ManusError(f"獲取對話歷史失敗: {e}", operation="get_conversations")
    
    @async_handle_exceptions(default_return=[])
    async def get_tasks(self) -> List[Dict[str, Any]]:
        """
        獲取任務列表
        
        Returns:
            List[Dict[str, Any]]: 任務列表
        """
        try:
            if not self.logged_in:
                await self.login()
            
            self.logger.info("正在獲取任務列表...")
            
            tasks = []
            
            # 查找任務元素
            task_elements = await self.page.query_selector_all(".task, .task-item, .project")
            
            for element in task_elements:
                try:
                    # 提取任務信息
                    title = await element.query_selector(".title, .task-title, h3, h4")
                    title_text = await title.text_content() if title else "未知任務"
                    
                    status = await element.query_selector(".status, .task-status")
                    status_text = await status.text_content() if status else "未知狀態"
                    
                    # 嘗試提取更多信息
                    description = await element.query_selector(".description, .task-description")
                    description_text = await description.text_content() if description else ""
                    
                    priority = await element.query_selector(".priority, .task-priority")
                    priority_text = await priority.text_content() if priority else "normal"
                    
                    task = {
                        "title": title_text.strip(),
                        "status": status_text.strip(),
                        "description": description_text.strip(),
                        "priority": priority_text.strip(),
                        "extracted_at": time.time()
                    }
                    
                    tasks.append(task)
                    
                except Exception as e:
                    self.logger.warning(f"提取任務元素失敗: {e}")
                    continue
            
            self.logger.info(f"✅ 獲取到 {len(tasks)} 個任務")
            return tasks
            
        except Exception as e:
            self.logger.error(f"獲取任務列表失敗: {e}")
            raise ManusError(f"獲取任務列表失敗: {e}", operation="get_tasks")
    
    @async_handle_exceptions(default_return=[])
    async def download_files(self, task_id: str = "") -> List[Dict[str, Any]]:
        """
        下載任務文件
        
        Args:
            task_id: 任務ID
            
        Returns:
            List[Dict[str, Any]]: 下載的文件列表
        """
        try:
            if not self.logged_in:
                await self.login()
            
            self.logger.info(f"正在下載任務文件: {task_id}")
            
            files = []
            
            # 查找文件鏈接
            file_links = await self.page.query_selector_all("a[href*='download'], a[href*='file'], .file-link")
            
            for link in file_links:
                try:
                    href = await link.get_attribute("href")
                    text = await link.text_content()
                    
                    if href and text:
                        file_info = {
                            "name": text.strip(),
                            "url": href,
                            "task_id": task_id,
                            "extracted_at": time.time()
                        }
                        files.append(file_info)
                        
                except Exception as e:
                    self.logger.warning(f"提取文件鏈接失敗: {e}")
                    continue
            
            self.logger.info(f"✅ 找到 {len(files)} 個文件")
            return files
            
        except Exception as e:
            self.logger.error(f"下載文件失敗: {e}")
            raise ManusError(f"下載文件失敗: {e}", operation="download_files")
    
    async def _is_session_valid(self) -> bool:
        """檢查會話是否有效"""
        try:
            if not self.page:
                return False
            
            # 檢查當前頁面是否需要登錄
            current_url = self.page.url
            if "login" in current_url.lower():
                return False
            
            # 檢查是否有登錄狀態指示器
            login_indicator = await self.page.query_selector(".user-info, .profile, .avatar")
            return login_indicator is not None
            
        except Exception:
            return False


# 使用示例和測試
async def test_mcp_manus_integration():
    """測試MCP Manus Integration"""
    # 配置
    config = {
        "base_url": "https://manus.im",
        "app_url": "https://manus.im/app/uuX3KzwzsthCSgqmbQbgOz",
        "login_email": "test@example.com",
        "login_password": "password123",
        "auto_login": True,
        "headless": False,
        "slow_mo": 1000
    }
    
    # 創建日誌器
    logger = logging.getLogger("test_mcp_manus")
    logger.setLevel(logging.INFO)
    
    # 創建集成實例
    integration = MCPManusIntegration(config, logger)
    
    try:
        # 初始化
        await integration.initialize()
        
        # 測試創建任務
        print("=== 測試創建任務 ===")
        task1_result = await integration.handle_mcp_request("create_task", {
            "task_type": "manus_login",
            "description": "登錄Manus平台",
            "parameters": {"email": "test@example.com", "password": "password123"},
            "priority": 9
        })
        print(f"任務1創建結果: {task1_result}")
        
        task2_result = await integration.handle_mcp_request("create_task", {
            "task_type": "send_message",
            "description": "發送測試消息",
            "parameters": {"message": "Hello, this is a test message"},
            "priority": 7,
            "dependencies": [task1_result["result"]["task_id"]]
        })
        print(f"任務2創建結果: {task2_result}")
        
        task3_result = await integration.handle_mcp_request("create_task", {
            "task_type": "get_conversations",
            "description": "獲取對話列表",
            "parameters": {},
            "priority": 6,
            "dependencies": [task1_result["result"]["task_id"]]
        })
        print(f"任務3創建結果: {task3_result}")
        
        # 測試自動生成鏈結
        print("\n=== 測試自動生成鏈結 ===")
        auto_chain_result = await integration.handle_mcp_request("auto_generate_chains", {})
        print(f"自動生成鏈結結果: {auto_chain_result}")
        
        # 測試列出鏈結
        print("\n=== 測試列出鏈結 ===")
        list_chains_result = await integration.handle_mcp_request("list_chains", {})
        print(f"鏈結列表: {list_chains_result}")
        
        # 測試執行鏈結
        if auto_chain_result["success"] and auto_chain_result["result"]["generated_chains"]:
            chain_id = auto_chain_result["result"]["generated_chains"][0]["chain_id"]
            
            print(f"\n=== 測試執行鏈結: {chain_id} ===")
            execute_result = await integration.handle_mcp_request("execute_chain", {
                "chain_id": chain_id
            })
            print(f"執行結果: {execute_result}")
        
        # 測試獲取系統狀態
        print("\n=== 測試獲取系統狀態 ===")
        status_result = await integration.handle_mcp_request("get_system_status", {})
        print(f"系統狀態: {status_result}")
        
    finally:
        # 清理
        await integration.cleanup()


if __name__ == "__main__":
    # 配置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 運行測試
    asyncio.run(test_mcp_manus_integration())

