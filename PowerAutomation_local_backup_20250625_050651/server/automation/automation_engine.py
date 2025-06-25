"""
PowerAutomation Local MCP Automation Engine

自動化測試引擎，提供完整的測試執行和管理功能
支持瀏覽器自動化、截圖錄製、結果分析等

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

from shared.exceptions import AutomationError, async_handle_exceptions
from shared.utils import ensure_directory, format_duration


class AutomationEngine:
    """自動化測試引擎"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        初始化Automation Engine
        
        Args:
            config: 自動化配置
            logger: 日誌器
        """
        self.config = config
        self.logger = logger
        self.playwright = None
        self.browser = None
        
        # 配置參數
        self.browser_type = config.get("browser", "chromium")
        self.headless = config.get("headless", False)
        self.screenshot_enabled = config.get("screenshot_enabled", True)
        self.video_recording = config.get("video_recording", True)
        self.test_timeout = config.get("test_timeout", 300)
        
        # 狀態信息
        self.status = {
            "initialized": False,
            "running": False,
            "test_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "last_test_time": None
        }
        
        # 測試結果存儲
        self.test_results = []
    
    async def initialize(self) -> bool:
        """
        初始化Automation Engine
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.logger.info("正在初始化Automation Engine...")
            
            # 初始化Playwright
            self.playwright = await async_playwright().start()
            
            self.status["initialized"] = True
            self.logger.info("Automation Engine初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"Automation Engine初始化失敗: {e}")
            return False
    
    async def start(self) -> bool:
        """
        啟動Automation Engine
        
        Returns:
            bool: 啟動是否成功
        """
        try:
            if not self.status["initialized"]:
                raise AutomationError("Automation Engine未初始化")
            
            self.logger.info("正在啟動Automation Engine...")
            
            # 啟動瀏覽器
            await self._start_browser()
            
            self.status["running"] = True
            self.logger.info("Automation Engine已啟動")
            return True
            
        except Exception as e:
            self.logger.error(f"啟動Automation Engine失敗: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        停止Automation Engine
        
        Returns:
            bool: 停止是否成功
        """
        try:
            self.logger.info("正在停止Automation Engine...")
            
            # 關閉瀏覽器
            await self._stop_browser()
            
            # 關閉Playwright
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            self.status["running"] = False
            self.logger.info("Automation Engine已停止")
            return True
            
        except Exception as e:
            self.logger.error(f"停止Automation Engine失敗: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """
        獲取Automation Engine狀態
        
        Returns:
            Dict[str, Any]: 狀態信息
        """
        try:
            status = self.status.copy()
            
            # 計算成功率
            if status["test_count"] > 0:
                status["success_rate"] = (status["success_count"] / status["test_count"]) * 100
            else:
                status["success_rate"] = 0
            
            # 添加配置信息
            status["config"] = {
                "browser": self.browser_type,
                "headless": self.headless,
                "screenshot_enabled": self.screenshot_enabled,
                "video_recording": self.video_recording,
                "test_timeout": self.test_timeout
            }
            
            # 添加最近的測試結果
            status["recent_results"] = self.test_results[-5:] if self.test_results else []
            
            return status
            
        except Exception as e:
            self.logger.error(f"獲取Automation狀態失敗: {e}")
            return {"error": str(e)}
    
    async def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理自動化請求
        
        Args:
            method: 方法名
            params: 參數
            
        Returns:
            Dict[str, Any]: 響應數據
        """
        try:
            self.logger.debug(f"處理Automation請求: {method}")
            
            # 路由到相應的方法
            if method == "run_test":
                test_case = params.get("test_case", "")
                result = await self.run_test(test_case)
                return result
                
            elif method == "get_test_results":
                return {"results": self.test_results}
                
            elif method == "clear_results":
                self.test_results.clear()
                return {"success": True, "message": "測試結果已清空"}
                
            else:
                raise AutomationError(f"未知的Automation方法: {method}")
            
        except Exception as e:
            self.logger.error(f"處理Automation請求失敗: {e}")
            raise
    
    @async_handle_exceptions(default_return={})
    async def run_test(self, test_case: str) -> Dict[str, Any]:
        """
        運行自動化測試
        
        Args:
            test_case: 測試案例名稱
            
        Returns:
            Dict[str, Any]: 測試結果
        """
        try:
            self.logger.info(f"正在運行測試案例: {test_case}")
            
            start_time = time.time()
            self.status["test_count"] += 1
            self.status["last_test_time"] = start_time
            
            # 創建新的頁面
            page = await self.browser.new_page()
            
            try:
                # 根據測試案例執行相應的測試
                if test_case.upper() == "TC001":
                    result = await self._run_tc001_login_test(page)
                elif test_case.upper() == "TC002":
                    result = await self._run_tc002_message_test(page)
                elif test_case.upper() == "TC003":
                    result = await self._run_tc003_conversation_test(page)
                elif test_case.upper() == "TC004":
                    result = await self._run_tc004_task_test(page)
                elif test_case.upper() == "TC005":
                    result = await self._run_tc005_file_test(page)
                elif test_case.upper() == "TC006":
                    result = await self._run_tc006_integration_test(page)
                else:
                    raise AutomationError(f"未知的測試案例: {test_case}")
                
                # 計算執行時間
                end_time = time.time()
                duration = end_time - start_time
                
                # 更新狀態
                if result.get("success", False):
                    self.status["success_count"] += 1
                else:
                    self.status["failure_count"] += 1
                
                # 構建測試結果
                test_result = {
                    "test_case": test_case,
                    "success": result.get("success", False),
                    "message": result.get("message", ""),
                    "details": result.get("details", {}),
                    "duration": duration,
                    "duration_formatted": format_duration(duration),
                    "timestamp": start_time,
                    "screenshots": result.get("screenshots", []),
                    "video_path": result.get("video_path", "")
                }
                
                # 保存測試結果
                self.test_results.append(test_result)
                
                self.logger.info(f"✅ 測試案例 {test_case} 執行完成 - 成功: {result.get('success', False)}")
                return test_result
                
            finally:
                await page.close()
            
        except Exception as e:
            self.status["failure_count"] += 1
            self.logger.error(f"運行測試案例失敗: {e}")
            raise AutomationError(f"運行測試案例失敗: {e}", test_case=test_case)
    
    async def _run_tc001_login_test(self, page: Page) -> Dict[str, Any]:
        """運行TC001登錄測試"""
        try:
            self.logger.info("執行TC001 - Manus登錄測試")
            
            screenshots = []
            details = {}
            
            # 導航到Manus應用
            app_url = "https://manus.im/app/uuX3KzwzsthCSgqmbQbgOz"
            await page.goto(app_url, timeout=30000)
            
            # 截圖1: 初始頁面
            if self.screenshot_enabled:
                screenshot_path = await self._take_screenshot(page, "tc001_initial")
                screenshots.append(screenshot_path)
            
            # 滾動到底部查找登錄鏈接
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            # 查找並點擊登錄鏈接
            sign_in_link = await page.query_selector("text=Already have an account? Sign in")
            if sign_in_link:
                await sign_in_link.click()
                await page.wait_for_load_state("networkidle")
                details["login_link_found"] = True
            else:
                details["login_link_found"] = False
                return {"success": False, "message": "找不到登錄鏈接", "details": details}
            
            # 截圖2: 登錄頁面
            if self.screenshot_enabled:
                screenshot_path = await self._take_screenshot(page, "tc001_login_page")
                screenshots.append(screenshot_path)
            
            # 填入登錄憑證
            email_input = await page.query_selector("input[type='email']")
            password_input = await page.query_selector("input[type='password']")
            
            if email_input and password_input:
                await email_input.fill("chuang.hsiaoyen@gmail.com")
                await password_input.fill("silentfleet#1234")
                details["credentials_filled"] = True
            else:
                details["credentials_filled"] = False
                return {"success": False, "message": "找不到登錄輸入框", "details": details}
            
            # 截圖3: 填入憑證後
            if self.screenshot_enabled:
                screenshot_path = await self._take_screenshot(page, "tc001_credentials_filled")
                screenshots.append(screenshot_path)
            
            # 提交登錄表單
            login_button = await page.query_selector("button[type='submit']")
            if login_button:
                await login_button.click()
                await page.wait_for_load_state("networkidle", timeout=30000)
                details["login_submitted"] = True
            else:
                details["login_submitted"] = False
                return {"success": False, "message": "找不到登錄按鈕", "details": details}
            
            # 截圖4: 登錄後頁面
            if self.screenshot_enabled:
                screenshot_path = await self._take_screenshot(page, "tc001_after_login")
                screenshots.append(screenshot_path)
            
            # 驗證登錄成功
            current_url = page.url
            if "login" not in current_url.lower():
                details["login_success"] = True
                return {
                    "success": True,
                    "message": "登錄測試成功",
                    "details": details,
                    "screenshots": screenshots
                }
            else:
                details["login_success"] = False
                return {
                    "success": False,
                    "message": "登錄驗證失敗",
                    "details": details,
                    "screenshots": screenshots
                }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"TC001測試執行失敗: {e}",
                "details": details,
                "screenshots": screenshots
            }
    
    async def _run_tc002_message_test(self, page: Page) -> Dict[str, Any]:
        """運行TC002消息發送測試"""
        try:
            self.logger.info("執行TC002 - 消息發送測試")
            
            screenshots = []
            details = {}
            
            # 先執行登錄
            login_result = await self._run_tc001_login_test(page)
            if not login_result.get("success", False):
                return {"success": False, "message": "登錄失敗，無法執行消息測試", "details": details}
            
            # 查找消息輸入框
            message_input = await page.query_selector("textarea, input[type='text']")
            if message_input:
                test_message = "這是一條測試消息，用於驗證消息發送功能"
                await message_input.fill(test_message)
                details["message_input_found"] = True
                details["test_message"] = test_message
            else:
                details["message_input_found"] = False
                return {"success": False, "message": "找不到消息輸入框", "details": details}
            
            # 截圖: 輸入消息後
            if self.screenshot_enabled:
                screenshot_path = await self._take_screenshot(page, "tc002_message_input")
                screenshots.append(screenshot_path)
            
            # 發送消息
            send_button = await page.query_selector("button[type='submit'], button:has-text('Send')")
            if send_button:
                await send_button.click()
                details["message_sent"] = True
            else:
                await message_input.press("Enter")
                details["message_sent"] = True
            
            # 等待消息發送完成
            await asyncio.sleep(3)
            
            # 截圖: 消息發送後
            if self.screenshot_enabled:
                screenshot_path = await self._take_screenshot(page, "tc002_message_sent")
                screenshots.append(screenshot_path)
            
            return {
                "success": True,
                "message": "消息發送測試成功",
                "details": details,
                "screenshots": screenshots
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"TC002測試執行失敗: {e}",
                "details": details,
                "screenshots": screenshots
            }
    
    async def _run_tc003_conversation_test(self, page: Page) -> Dict[str, Any]:
        """運行TC003對話獲取測試"""
        try:
            self.logger.info("執行TC003 - 對話獲取測試")
            
            screenshots = []
            details = {}
            
            # 先執行登錄
            login_result = await self._run_tc001_login_test(page)
            if not login_result.get("success", False):
                return {"success": False, "message": "登錄失敗，無法執行對話測試", "details": details}
            
            # 查找對話元素
            conversation_elements = await page.query_selector_all(".conversation, .message, .chat-item")
            details["conversation_count"] = len(conversation_elements)
            
            # 截圖: 對話頁面
            if self.screenshot_enabled:
                screenshot_path = await self._take_screenshot(page, "tc003_conversations")
                screenshots.append(screenshot_path)
            
            # 提取對話內容
            conversations = []
            for element in conversation_elements[:5]:  # 只提取前5條
                try:
                    text = await element.text_content()
                    if text and text.strip():
                        conversations.append(text.strip())
                except:
                    continue
            
            details["extracted_conversations"] = conversations
            details["extraction_success"] = len(conversations) > 0
            
            return {
                "success": len(conversations) > 0,
                "message": f"對話獲取測試完成，提取到{len(conversations)}條對話",
                "details": details,
                "screenshots": screenshots
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"TC003測試執行失敗: {e}",
                "details": details,
                "screenshots": screenshots
            }
    
    async def _run_tc004_task_test(self, page: Page) -> Dict[str, Any]:
        """運行TC004任務獲取測試"""
        try:
            self.logger.info("執行TC004 - 任務獲取測試")
            
            screenshots = []
            details = {}
            
            # 先執行登錄
            login_result = await self._run_tc001_login_test(page)
            if not login_result.get("success", False):
                return {"success": False, "message": "登錄失敗，無法執行任務測試", "details": details}
            
            # 查找任務元素
            task_elements = await page.query_selector_all(".task, .task-item, .project")
            details["task_count"] = len(task_elements)
            
            # 截圖: 任務頁面
            if self.screenshot_enabled:
                screenshot_path = await self._take_screenshot(page, "tc004_tasks")
                screenshots.append(screenshot_path)
            
            # 提取任務信息
            tasks = []
            for element in task_elements[:5]:  # 只提取前5個
                try:
                    text = await element.text_content()
                    if text and text.strip():
                        tasks.append(text.strip())
                except:
                    continue
            
            details["extracted_tasks"] = tasks
            details["extraction_success"] = len(tasks) > 0
            
            return {
                "success": len(tasks) > 0,
                "message": f"任務獲取測試完成，提取到{len(tasks)}個任務",
                "details": details,
                "screenshots": screenshots
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"TC004測試執行失敗: {e}",
                "details": details,
                "screenshots": screenshots
            }
    
    async def _run_tc005_file_test(self, page: Page) -> Dict[str, Any]:
        """運行TC005文件下載測試"""
        try:
            self.logger.info("執行TC005 - 文件下載測試")
            
            screenshots = []
            details = {}
            
            # 先執行登錄
            login_result = await self._run_tc001_login_test(page)
            if not login_result.get("success", False):
                return {"success": False, "message": "登錄失敗，無法執行文件測試", "details": details}
            
            # 查找文件鏈接
            file_links = await page.query_selector_all("a[href*='download'], a[href*='file'], .file-link")
            details["file_link_count"] = len(file_links)
            
            # 截圖: 文件頁面
            if self.screenshot_enabled:
                screenshot_path = await self._take_screenshot(page, "tc005_files")
                screenshots.append(screenshot_path)
            
            # 提取文件信息
            files = []
            for link in file_links[:5]:  # 只處理前5個
                try:
                    href = await link.get_attribute("href")
                    text = await link.text_content()
                    if href and text:
                        files.append({"name": text.strip(), "url": href})
                except:
                    continue
            
            details["extracted_files"] = files
            details["extraction_success"] = len(files) > 0
            
            return {
                "success": len(files) > 0,
                "message": f"文件下載測試完成，找到{len(files)}個文件",
                "details": details,
                "screenshots": screenshots
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"TC005測試執行失敗: {e}",
                "details": details,
                "screenshots": screenshots
            }
    
    async def _run_tc006_integration_test(self, page: Page) -> Dict[str, Any]:
        """運行TC006集成測試"""
        try:
            self.logger.info("執行TC006 - 集成測試")
            
            screenshots = []
            details = {}
            
            # 執行所有測試案例
            test_results = []
            
            # TC001 - 登錄測試
            tc001_result = await self._run_tc001_login_test(page)
            test_results.append({"test": "TC001", "success": tc001_result.get("success", False)})
            
            if tc001_result.get("success", False):
                # TC002 - 消息測試
                tc002_result = await self._run_tc002_message_test(page)
                test_results.append({"test": "TC002", "success": tc002_result.get("success", False)})
                
                # TC003 - 對話測試
                tc003_result = await self._run_tc003_conversation_test(page)
                test_results.append({"test": "TC003", "success": tc003_result.get("success", False)})
                
                # TC004 - 任務測試
                tc004_result = await self._run_tc004_task_test(page)
                test_results.append({"test": "TC004", "success": tc004_result.get("success", False)})
                
                # TC005 - 文件測試
                tc005_result = await self._run_tc005_file_test(page)
                test_results.append({"test": "TC005", "success": tc005_result.get("success", False)})
            
            # 計算成功率
            total_tests = len(test_results)
            successful_tests = sum(1 for result in test_results if result["success"])
            success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
            
            details["test_results"] = test_results
            details["total_tests"] = total_tests
            details["successful_tests"] = successful_tests
            details["success_rate"] = success_rate
            
            # 截圖: 集成測試完成
            if self.screenshot_enabled:
                screenshot_path = await self._take_screenshot(page, "tc006_integration_complete")
                screenshots.append(screenshot_path)
            
            return {
                "success": success_rate >= 80,  # 80%以上成功率視為成功
                "message": f"集成測試完成，成功率: {success_rate:.1f}%",
                "details": details,
                "screenshots": screenshots
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"TC006測試執行失敗: {e}",
                "details": details,
                "screenshots": screenshots
            }
    
    async def _start_browser(self):
        """啟動瀏覽器"""
        try:
            browser_type = getattr(self.playwright, self.browser_type)
            self.browser = await browser_type.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
        except Exception as e:
            raise AutomationError(f"啟動瀏覽器失敗: {e}")
    
    async def _stop_browser(self):
        """停止瀏覽器"""
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
                
        except Exception as e:
            self.logger.error(f"停止瀏覽器失敗: {e}")
    
    async def _take_screenshot(self, page: Page, name: str) -> str:
        """截圖"""
        try:
            if not self.screenshot_enabled:
                return ""
            
            # 創建截圖目錄
            screenshot_dir = "screenshots"
            ensure_directory(screenshot_dir)
            
            # 生成截圖文件名
            timestamp = int(time.time())
            filename = f"{name}_{timestamp}.png"
            filepath = os.path.join(screenshot_dir, filename)
            
            # 截圖
            await page.screenshot(path=filepath, full_page=True)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"截圖失敗: {e}")
            return ""

