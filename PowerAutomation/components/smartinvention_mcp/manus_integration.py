"""
PowerAutomation Local MCP Manus Integration

Manus平台集成模組，提供完整的Manus操作功能
包括登錄、消息發送、對話獲取、任務管理等

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
from pathlib import Path
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Browser, Page

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.exceptions import ManusError, async_handle_exceptions
from shared.utils import ensure_directory, safe_json_dumps


class ManusIntegration:
    """Manus平台集成模組"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        初始化Manus Integration
        
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
        
        # 配置參數
        self.base_url = config.get("base_url", "https://manus.im")
        self.app_url = config.get("app_url", "")
        self.login_email = config.get("login_email", "")
        self.login_password = config.get("login_password", "")
        self.login_timeout = config.get("login_timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        self.session_timeout = config.get("session_timeout", 3600)
        
        # 狀態信息
        self.status = {
            "initialized": False,
            "running": False,
            "logged_in": False,
            "last_login_time": None,
            "session_start_time": None,
            "operation_count": 0,
            "error_count": 0
        }
    
    async def initialize(self) -> bool:
        """
        初始化Manus Integration
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.logger.info("正在初始化Manus Integration...")
            
            # 驗證配置
            if not self.app_url or not self.login_email or not self.login_password:
                raise ManusError("Manus配置不完整")
            
            # 初始化Playwright
            self.playwright = await async_playwright().start()
            
            self.status["initialized"] = True
            self.logger.info("Manus Integration初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"Manus Integration初始化失敗: {e}")
            return False
    
    async def start(self) -> bool:
        """
        啟動Manus Integration
        
        Returns:
            bool: 啟動是否成功
        """
        try:
            if not self.status["initialized"]:
                raise ManusError("Manus Integration未初始化")
            
            self.logger.info("正在啟動Manus Integration...")
            
            # 啟動瀏覽器
            await self._start_browser()
            
            # 自動登錄（如果配置了）
            if self.config.get("auto_login", True):
                await self.login()
            
            self.status["running"] = True
            self.logger.info("Manus Integration已啟動")
            return True
            
        except Exception as e:
            self.logger.error(f"啟動Manus Integration失敗: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        停止Manus Integration
        
        Returns:
            bool: 停止是否成功
        """
        try:
            self.logger.info("正在停止Manus Integration...")
            
            # 關閉瀏覽器
            await self._stop_browser()
            
            # 關閉Playwright
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            self.status["running"] = False
            self.status["logged_in"] = False
            self.logged_in = False
            
            self.logger.info("Manus Integration已停止")
            return True
            
        except Exception as e:
            self.logger.error(f"停止Manus Integration失敗: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """
        獲取Manus Integration狀態
        
        Returns:
            Dict[str, Any]: 狀態信息
        """
        try:
            status = self.status.copy()
            
            # 添加會話信息
            if status["session_start_time"]:
                status["session_duration"] = time.time() - status["session_start_time"]
            
            # 添加配置信息
            status["config"] = {
                "base_url": self.base_url,
                "app_url": self.app_url,
                "login_email": self.login_email,
                "auto_login": self.config.get("auto_login", True),
                "keep_alive": self.config.get("keep_alive", True)
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"獲取Manus狀態失敗: {e}")
            return {"error": str(e)}
    
    async def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理Manus請求
        
        Args:
            method: 方法名
            params: 參數
            
        Returns:
            Dict[str, Any]: 響應數據
        """
        try:
            self.status["operation_count"] += 1
            self.logger.debug(f"處理Manus請求: {method}")
            
            # 檢查會話是否有效
            if method != "login" and not await self._is_session_valid():
                await self.login()
            
            # 路由到相應的方法
            if method == "login":
                result = await self.login()
                return {"success": result, "message": "登錄完成"}
                
            elif method == "send_message":
                message = params.get("message", "")
                result = await self.send_message(message)
                return {"success": result, "message": "消息發送完成"}
                
            elif method == "get_conversations":
                conversations = await self.get_conversations()
                return {"conversations": conversations, "count": len(conversations)}
                
            elif method == "get_tasks":
                tasks = await self.get_tasks()
                return {"tasks": tasks, "count": len(tasks)}
                
            elif method == "download_files":
                task_id = params.get("task_id", "")
                files = await self.download_files(task_id)
                return {"files": files, "count": len(files)}
                
            else:
                raise ManusError(f"未知的Manus方法: {method}")
            
        except Exception as e:
            self.status["error_count"] += 1
            self.logger.error(f"處理Manus請求失敗: {e}")
            raise
    
    @async_handle_exceptions(default_return=False)
    async def login(self) -> bool:
        """
        登錄Manus平台
        
        Returns:
            bool: 登錄是否成功
        """
        try:
            self.logger.info("正在登錄Manus平台...")
            
            if not self.page:
                await self._start_browser()
            
            # 導航到應用頁面
            await self.page.goto(self.app_url, timeout=30000)
            await self.page.wait_for_load_state("networkidle")
            
            # 檢查是否已經登錄
            if await self._check_login_status():
                self.logger.info("已經登錄Manus平台")
                self.logged_in = True
                self.status["logged_in"] = True
                self.status["last_login_time"] = time.time()
                self.status["session_start_time"] = time.time()
                return True
            
            # 滾動到頁面底部查找登錄鏈接
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            # 查找並點擊登錄鏈接
            sign_in_link = await self.page.query_selector("text=Already have an account? Sign in")
            if sign_in_link:
                await sign_in_link.click()
                await self.page.wait_for_load_state("networkidle")
            
            # 填入登錄憑證
            await self._fill_login_credentials()
            
            # 提交登錄表單
            await self._submit_login_form()
            
            # 驗證登錄結果
            if await self._verify_login_success():
                self.logged_in = True
                self.status["logged_in"] = True
                self.status["last_login_time"] = time.time()
                self.status["session_start_time"] = time.time()
                self.logger.info("✅ Manus登錄成功")
                return True
            else:
                raise ManusError("登錄驗證失敗")
            
        except Exception as e:
            self.logger.error(f"Manus登錄失敗: {e}")
            raise ManusError(f"登錄失敗: {e}", operation="login")
    
    @async_handle_exceptions(default_return=False)
    async def send_message(self, message: str) -> bool:
        """
        發送消息到Manus
        
        Args:
            message: 要發送的消息
            
        Returns:
            bool: 發送是否成功
        """
        try:
            if not self.logged_in:
                await self.login()
            
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
            return True
            
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
                    
                    task = {
                        "title": title_text.strip(),
                        "status": status_text.strip(),
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
                            "downloaded_at": time.time()
                        }
                        
                        files.append(file_info)
                        
                except Exception as e:
                    self.logger.warning(f"處理文件鏈接失敗: {e}")
                    continue
            
            self.logger.info(f"✅ 找到 {len(files)} 個文件")
            return files
            
        except Exception as e:
            self.logger.error(f"下載文件失敗: {e}")
            raise ManusError(f"下載文件失敗: {e}", operation="download_files")
    
    async def _start_browser(self):
        """啟動瀏覽器"""
        try:
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            self.page = await context.new_page()
            
        except Exception as e:
            raise ManusError(f"啟動瀏覽器失敗: {e}")
    
    async def _stop_browser(self):
        """停止瀏覽器"""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
                
        except Exception as e:
            self.logger.error(f"停止瀏覽器失敗: {e}")
    
    async def _check_login_status(self) -> bool:
        """檢查登錄狀態"""
        try:
            # 檢查是否在登錄頁面
            current_url = self.page.url
            if "login" in current_url.lower():
                return False
            
            # 檢查是否有登錄後的元素
            logged_in_indicators = [
                ".user-menu", ".profile", ".dashboard", ".workspace",
                "text=Dashboard", "text=Profile", "text=Settings"
            ]
            
            for indicator in logged_in_indicators:
                element = await self.page.query_selector(indicator)
                if element:
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def _fill_login_credentials(self):
        """填入登錄憑證"""
        try:
            # 填入郵箱
            email_input = await self.page.query_selector("input[type='email'], input[name='email']")
            if email_input:
                await email_input.fill(self.login_email)
            
            # 填入密碼
            password_input = await self.page.query_selector("input[type='password'], input[name='password']")
            if password_input:
                await password_input.fill(self.login_password)
            
            await asyncio.sleep(1)
            
        except Exception as e:
            raise ManusError(f"填入登錄憑證失敗: {e}")
    
    async def _submit_login_form(self):
        """提交登錄表單"""
        try:
            # 查找並點擊登錄按鈕
            login_buttons = [
                "button[type='submit']",
                "button:has-text('Sign in')",
                "button:has-text('Login')",
                "button:has-text('登錄')",
                ".login-button"
            ]
            
            for selector in login_buttons:
                button = await self.page.query_selector(selector)
                if button:
                    await button.click()
                    break
            
            # 等待頁面響應
            await self.page.wait_for_load_state("networkidle", timeout=30000)
            
        except Exception as e:
            raise ManusError(f"提交登錄表單失敗: {e}")
    
    async def _verify_login_success(self) -> bool:
        """驗證登錄成功"""
        try:
            # 等待頁面加載
            await asyncio.sleep(3)
            
            # 檢查是否跳轉到主頁面
            current_url = self.page.url
            if "login" not in current_url.lower():
                return True
            
            # 檢查是否有錯誤消息
            error_elements = await self.page.query_selector_all(".error, .alert-danger, .login-error")
            if error_elements:
                return False
            
            return await self._check_login_status()
            
        except Exception:
            return False
    
    async def _is_session_valid(self) -> bool:
        """檢查會話是否有效"""
        try:
            if not self.logged_in or not self.page:
                return False
            
            # 檢查會話超時
            if self.status["session_start_time"]:
                session_duration = time.time() - self.status["session_start_time"]
                if session_duration > self.session_timeout:
                    return False
            
            # 檢查頁面狀態
            return await self._check_login_status()
            
        except Exception:
            return False

