#!/usr/bin/env python3
"""
Manus Playwright操作腳本
專門實現對話歷史提取、批量下載、任務監控、輸入框操作
"""

import asyncio
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging
from pathlib import Path
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import re

@dataclass
class ConversationMessage:
    """對話消息數據結構"""
    id: str
    content: str
    sender: str  # user, assistant, system
    timestamp: datetime
    message_type: str
    conversation_id: str
    attachments: List[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class TaskItem:
    """任務項目數據結構"""
    task_id: str
    title: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    description: str
    progress: float = 0.0
    assignee: str = ""
    metadata: Dict[str, Any] = None

class ManusPlaywrightOperator:
    """Manus Playwright操作器"""
    
    def __init__(self, manus_url: str = "https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ"):
        self.manus_url = manus_url
        self.logger = self._setup_logger()
        
        # Playwright組件
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # 數據存儲
        self.conversations = []
        self.tasks = []
        self.monitoring_active = False
        
        # 選擇器配置
        self.selectors = {
            # 對話相關選擇器
            'conversation_container': [
                '.conversation-container',
                '.chat-container',
                '.messages-container',
                '[data-testid="conversation"]',
                '.conversation-view',
                '.chat-view'
            ],
            'message_list': [
                '.message-list',
                '.conversation-messages',
                '.chat-messages',
                '[data-testid="messages"]',
                '.messages'
            ],
            'message_item': [
                '.message',
                '.chat-message',
                '.conversation-message',
                '[data-testid="message"]',
                '.msg',
                '.message-item'
            ],
            'message_content': [
                '.message-content',
                '.message-text',
                '.content',
                '.text',
                'p',
                '.message-body'
            ],
            'message_sender': [
                '.sender',
                '.author',
                '.user',
                '.message-sender',
                '[data-sender]',
                '.message-author'
            ],
            'message_timestamp': [
                '.timestamp',
                '.time',
                '.date',
                '.message-time',
                '[data-time]',
                '.message-timestamp'
            ],
            
            # 任務相關選擇器
            'task_container': [
                '.task-container',
                '.tasks-container',
                '.todo-container',
                '[data-testid="tasks"]',
                '.task-list-container'
            ],
            'task_list': [
                '.task-list',
                '.todo-list',
                '.tasks',
                '[data-testid="task-list"]',
                '.task-items'
            ],
            'task_item': [
                '.task-item',
                '.task',
                '.todo-item',
                '[data-testid="task"]',
                '.task-card',
                '.task-row'
            ],
            'task_title': [
                '.task-title',
                '.title',
                'h3',
                'h4',
                '.task-name',
                '.task-text'
            ],
            'task_status': [
                '.status',
                '.task-status',
                '.state',
                '[data-status]',
                '.badge',
                '.task-state'
            ],
            'task_progress': [
                '.progress',
                '.task-progress',
                '.completion',
                '[data-progress]',
                '.progress-bar'
            ],
            
            # 輸入相關選擇器
            'input_container': [
                '.input-container',
                '.message-input-container',
                '.chat-input-container',
                '[data-testid="input-container"]'
            ],
            'input_box': [
                'textarea[placeholder*="輸入"]',
                'textarea[placeholder*="input"]',
                'textarea[placeholder*="message"]',
                'textarea[placeholder*="Type"]',
                'input[type="text"]',
                '.input-box',
                '.message-input',
                '[data-testid="message-input"]',
                'textarea',
                '.chat-input',
                '.text-input'
            ],
            'send_button': [
                'button[type="submit"]',
                '.send-button',
                '.send-btn',
                '[data-testid="send"]',
                'button:has-text("發送")',
                'button:has-text("Send")',
                '.submit-btn',
                '[aria-label*="send"]',
                '[aria-label*="發送"]'
            ],
            
            # 下載和導出相關
            'download_button': [
                '.download',
                '.export',
                'button:has-text("下載")',
                'button:has-text("導出")',
                'button:has-text("Download")',
                'button:has-text("Export")',
                '[data-action="download"]',
                '[data-action="export"]'
            ],
            
            # 滾動和加載相關
            'load_more_button': [
                '.load-more',
                'button:has-text("載入更多")',
                'button:has-text("Load more")',
                '[data-action="load-more"]'
            ],
            'loading_indicator': [
                '.loading',
                '.spinner',
                '.loader',
                '[data-testid="loading"]'
            ]
        }
    
    def _setup_logger(self) -> logging.Logger:
        """設置日誌"""
        logger = logging.getLogger("ManusPlaywright")
        logger.setLevel(logging.INFO)
        
        # 清除現有處理器
        logger.handlers.clear()
        
        # 文件處理器
        log_file = Path("logs") / f"manus_operations_{datetime.now().strftime('%Y%m%d')}.log"
        log_file.parent.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    async def initialize(self, headless: bool = False) -> bool:
        """初始化Playwright"""
        try:
            self.logger.info("🚀 初始化Playwright...")
            
            self.playwright = await async_playwright().start()
            
            # 啟動瀏覽器
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # 創建上下文
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # 創建頁面
            self.page = await self.context.new_page()
            
            # 導航到Manus頁面
            self.logger.info(f"🌐 導航到Manus頁面: {self.manus_url}")
            await self.page.goto(self.manus_url, wait_until='networkidle', timeout=30000)
            
            # 等待頁面加載
            await self._wait_for_page_ready()
            
            self.logger.info("✅ Playwright初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化Playwright失敗: {e}")
            return False
    
    async def _wait_for_page_ready(self, timeout: int = 30):
        """等待頁面準備就緒"""
        try:
            # 等待基本元素
            await self.page.wait_for_selector('body', timeout=timeout * 1000)
            
            # 檢查是否需要登入
            if await self._check_login_required():
                self.logger.info("🔐 檢測到需要登入，請手動完成登入...")
                await self._wait_for_login(timeout)
            
            # 等待內容加載
            await asyncio.sleep(3)
            
            self.logger.info("✅ 頁面準備就緒")
            
        except Exception as e:
            self.logger.error(f"等待頁面準備失敗: {e}")
    
    async def _check_login_required(self) -> bool:
        """檢查是否需要登入"""
        login_selectors = [
            'input[type="password"]',
            '.login-form',
            '.signin',
            'button:has-text("登入")',
            'button:has-text("Login")',
            'button:has-text("Sign in")'
        ]
        
        for selector in login_selectors:
            try:
                element = await self.page.query_selector(selector)
                if element and await element.is_visible():
                    return True
            except:
                continue
        
        return False
    
    async def _wait_for_login(self, timeout: int = 300):
        """等待登入完成"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not await self._check_login_required():
                self.logger.info("✅ 登入完成")
                await asyncio.sleep(3)  # 等待登入後頁面加載
                return
            
            await asyncio.sleep(5)
        
        raise TimeoutError("登入超時")
    
    async def extract_conversation_history(self) -> List[ConversationMessage]:
        """提取對話歷史"""
        self.logger.info("📜 開始提取對話歷史...")
        
        try:
            # 滾動加載所有消息
            await self._scroll_to_load_all_content()
            
            # 查找消息容器
            messages = await self._find_all_messages()
            
            self.logger.info(f"✅ 成功提取 {len(messages)} 條對話記錄")
            self.conversations = messages
            
            return messages
            
        except Exception as e:
            self.logger.error(f"提取對話歷史失敗: {e}")
            return []
    
    async def _scroll_to_load_all_content(self):
        """滾動加載所有內容"""
        self.logger.info("📜 滾動加載所有內容...")
        
        # 先滾動到頂部
        await self.page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(2)
        
        last_height = 0
        scroll_attempts = 0
        max_attempts = 100
        
        while scroll_attempts < max_attempts:
            # 滾動到底部
            current_height = await self.page.evaluate("document.body.scrollHeight")
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            # 檢查是否有"載入更多"按鈕
            load_more_button = await self._find_element(self.selectors['load_more_button'])
            if load_more_button:
                try:
                    await load_more_button.click()
                    await asyncio.sleep(3)
                    self.logger.debug("點擊了載入更多按鈕")
                except:
                    pass
            
            # 檢查是否還在加載
            await self._wait_for_loading_complete()
            
            # 檢查高度是否變化
            new_height = await self.page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            
            last_height = new_height
            scroll_attempts += 1
            
            self.logger.debug(f"滾動第 {scroll_attempts} 次，頁面高度: {new_height}")
        
        self.logger.info(f"✅ 滾動完成，共滾動 {scroll_attempts} 次")
    
    async def _wait_for_loading_complete(self, timeout: int = 10):
        """等待加載完成"""
        try:
            # 等待加載指示器消失
            for selector in self.selectors['loading_indicator']:
                try:
                    await self.page.wait_for_selector(selector, state='hidden', timeout=timeout * 1000)
                except:
                    continue
        except:
            pass
    
    async def _find_all_messages(self) -> List[ConversationMessage]:
        """查找所有消息"""
        messages = []
        
        # 查找消息項目
        message_elements = await self._find_elements(self.selectors['message_item'])
        
        self.logger.info(f"找到 {len(message_elements)} 個消息元素")
        
        for i, element in enumerate(message_elements):
            try:
                message = await self._parse_message_element(element, i)
                if message:
                    messages.append(message)
            except Exception as e:
                self.logger.error(f"解析消息 {i} 失敗: {e}")
        
        return messages
    
    async def _parse_message_element(self, element, index: int) -> Optional[ConversationMessage]:
        """解析消息元素"""
        try:
            # 提取內容
            content = await self._extract_text_from_element(element, self.selectors['message_content'])
            if not content:
                content = await element.inner_text()
            
            # 提取發送者
            sender = await self._extract_text_from_element(element, self.selectors['message_sender'])
            if not sender:
                # 嘗試從CSS類名判斷
                class_name = await element.get_attribute('class') or ""
                if 'user' in class_name.lower():
                    sender = 'user'
                elif 'assistant' in class_name.lower() or 'ai' in class_name.lower():
                    sender = 'assistant'
                else:
                    sender = 'unknown'
            
            # 提取時間戳
            timestamp = await self._extract_timestamp_from_element(element)
            
            # 檢查附件
            attachments = await self._extract_attachments_from_element(element)
            
            # 生成消息ID
            message_id = f"msg_{index}_{int(timestamp.timestamp())}"
            
            return ConversationMessage(
                id=message_id,
                content=content.strip() if content else "",
                sender=sender,
                timestamp=timestamp,
                message_type=self._determine_message_type(content, sender),
                conversation_id="main",
                attachments=attachments,
                metadata={
                    'index': index,
                    'element_html': await element.inner_html()
                }
            )
            
        except Exception as e:
            self.logger.error(f"解析消息元素失敗: {e}")
            return None
    
    async def _extract_text_from_element(self, element, selectors: List[str]) -> Optional[str]:
        """從元素中提取文本"""
        for selector in selectors:
            try:
                sub_element = await element.query_selector(selector)
                if sub_element:
                    text = await sub_element.inner_text()
                    if text and text.strip():
                        return text.strip()
            except:
                continue
        return None
    
    async def _extract_timestamp_from_element(self, element) -> datetime:
        """從元素中提取時間戳"""
        # 嘗試從時間戳選擇器提取
        for selector in self.selectors['message_timestamp']:
            try:
                time_element = await element.query_selector(selector)
                if time_element:
                    # 嘗試從屬性獲取
                    for attr in ['datetime', 'data-time', 'title', 'data-timestamp']:
                        time_str = await time_element.get_attribute(attr)
                        if time_str:
                            parsed_time = self._parse_timestamp(time_str)
                            if parsed_time:
                                return parsed_time
                    
                    # 嘗試從文本獲取
                    text = await time_element.inner_text()
                    if text:
                        parsed_time = self._parse_timestamp(text)
                        if parsed_time:
                            return parsed_time
            except:
                continue
        
        # 如果沒找到，返回當前時間
        return datetime.now()
    
    def _parse_timestamp(self, time_str: str) -> Optional[datetime]:
        """解析時間戳字符串"""
        try:
            # 處理相對時間
            if "分鐘前" in time_str or "minutes ago" in time_str:
                minutes = int(re.search(r'(\d+)', time_str).group(1))
                return datetime.now() - timedelta(minutes=minutes)
            
            if "小時前" in time_str or "hours ago" in time_str:
                hours = int(re.search(r'(\d+)', time_str).group(1))
                return datetime.now() - timedelta(hours=hours)
            
            if "天前" in time_str or "days ago" in time_str:
                days = int(re.search(r'(\d+)', time_str).group(1))
                return datetime.now() - timedelta(days=days)
            
            # 嘗試解析ISO格式
            if 'T' in time_str:
                return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            
            return None
            
        except:
            return None
    
    async def _extract_attachments_from_element(self, element) -> List[str]:
        """從元素中提取附件"""
        attachments = []
        
        try:
            # 查找圖片
            images = await element.query_selector_all('img')
            for img in images:
                src = await img.get_attribute('src')
                if src:
                    attachments.append(f"image:{src}")
            
            # 查找鏈接
            links = await element.query_selector_all('a[href]')
            for link in links:
                href = await link.get_attribute('href')
                if href and href.startswith('http'):
                    attachments.append(f"link:{href}")
            
            # 查找文件
            files = await element.query_selector_all('[data-file], .file, .attachment')
            for file_elem in files:
                file_url = await file_elem.get_attribute('data-file') or await file_elem.get_attribute('href')
                if file_url:
                    attachments.append(f"file:{file_url}")
        
        except Exception as e:
            self.logger.debug(f"提取附件失敗: {e}")
        
        return attachments
    
    def _determine_message_type(self, content: str, sender: str) -> str:
        """判斷消息類型"""
        if not content:
            return 'empty'
        
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['error', 'exception', '錯誤', '異常']):
            return 'error'
        elif any(word in content_lower for word in ['warning', '警告', '注意']):
            return 'warning'
        elif sender == 'system':
            return 'system'
        elif sender == 'user':
            return 'user_message'
        elif sender == 'assistant':
            return 'assistant_response'
        else:
            return 'general'
    
    async def extract_task_list(self) -> List[TaskItem]:
        """提取任務列表"""
        self.logger.info("📋 開始提取任務列表...")
        
        try:
            # 查找任務容器
            task_elements = await self._find_elements(self.selectors['task_item'])
            
            tasks = []
            for i, element in enumerate(task_elements):
                try:
                    task = await self._parse_task_element(element, i)
                    if task:
                        tasks.append(task)
                except Exception as e:
                    self.logger.error(f"解析任務 {i} 失敗: {e}")
            
            self.logger.info(f"✅ 成功提取 {len(tasks)} 個任務")
            self.tasks = tasks
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"提取任務列表失敗: {e}")
            return []
    
    async def _parse_task_element(self, element, index: int) -> Optional[TaskItem]:
        """解析任務元素"""
        try:
            # 提取標題
            title = await self._extract_text_from_element(element, self.selectors['task_title'])
            if not title:
                title = f"任務 {index + 1}"
            
            # 提取狀態
            status = await self._extract_text_from_element(element, self.selectors['task_status'])
            if not status:
                status = "unknown"
            
            # 提取進度
            progress = await self._extract_progress_from_element(element)
            
            # 生成任務ID
            task_id = f"task_{index}_{int(time.time())}"
            
            return TaskItem(
                task_id=task_id,
                title=title,
                status=status.lower(),
                priority="normal",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                description=title,
                progress=progress,
                metadata={
                    'index': index,
                    'element_html': await element.inner_html()
                }
            )
            
        except Exception as e:
            self.logger.error(f"解析任務元素失敗: {e}")
            return None
    
    async def _extract_progress_from_element(self, element) -> float:
        """從元素中提取進度"""
        try:
            for selector in self.selectors['task_progress']:
                progress_element = await element.query_selector(selector)
                if progress_element:
                    # 嘗試從屬性獲取
                    for attr in ['data-progress', 'value', 'aria-valuenow']:
                        progress_str = await progress_element.get_attribute(attr)
                        if progress_str:
                            try:
                                return float(progress_str) / 100.0 if float(progress_str) > 1 else float(progress_str)
                            except:
                                continue
                    
                    # 嘗試從文本獲取
                    text = await progress_element.inner_text()
                    if text and '%' in text:
                        try:
                            progress_num = float(re.search(r'(\d+)', text).group(1))
                            return progress_num / 100.0
                        except:
                            continue
        except:
            pass
        
        return 0.0
    
    async def batch_download_data(self, output_dir: str = "manus_data") -> bool:
        """批量下載數據"""
        self.logger.info("📥 開始批量下載數據...")
        
        try:
            # 創建輸出目錄
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 1. 提取並保存對話歷史
            conversations = await self.extract_conversation_history()
            if conversations:
                conv_file = output_path / f"conversations_{timestamp}.json"
                with open(conv_file, 'w', encoding='utf-8') as f:
                    json.dump([asdict(conv) for conv in conversations], f, 
                             ensure_ascii=False, indent=2, default=str)
                self.logger.info(f"💾 對話歷史已保存: {conv_file}")
            
            # 2. 提取並保存任務列表
            tasks = await self.extract_task_list()
            if tasks:
                tasks_file = output_path / f"tasks_{timestamp}.json"
                with open(tasks_file, 'w', encoding='utf-8') as f:
                    json.dump([asdict(task) for task in tasks], f, 
                             ensure_ascii=False, indent=2, default=str)
                self.logger.info(f"📋 任務列表已保存: {tasks_file}")
            
            # 3. 保存頁面截圖
            screenshot_file = output_path / f"screenshot_{timestamp}.png"
            await self.page.screenshot(path=str(screenshot_file), full_page=True)
            self.logger.info(f"📸 頁面截圖已保存: {screenshot_file}")
            
            # 4. 保存頁面HTML
            html_file = output_path / f"page_content_{timestamp}.html"
            html_content = await self.page.content()
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.logger.info(f"📄 頁面HTML已保存: {html_file}")
            
            # 5. 嘗試觸發下載按鈕
            await self._trigger_download_buttons(output_path)
            
            self.logger.info(f"✅ 批量下載完成，文件保存在: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"批量下載失敗: {e}")
            return False
    
    async def _trigger_download_buttons(self, output_path: Path):
        """觸發下載按鈕"""
        try:
            download_buttons = await self._find_elements(self.selectors['download_button'])
            
            for i, button in enumerate(download_buttons):
                try:
                    if await button.is_visible() and await button.is_enabled():
                        self.logger.info(f"點擊下載按鈕 {i + 1}")
                        
                        # 設置下載處理
                        async with self.page.expect_download() as download_info:
                            await button.click()
                            download = await download_info.value
                            
                            # 保存下載文件
                            download_file = output_path / f"download_{i}_{download.suggested_filename}"
                            await download.save_as(str(download_file))
                            self.logger.info(f"📥 下載文件已保存: {download_file}")
                        
                        await asyncio.sleep(2)
                
                except Exception as e:
                    self.logger.debug(f"下載按鈕 {i + 1} 處理失敗: {e}")
        
        except Exception as e:
            self.logger.debug(f"處理下載按鈕失敗: {e}")
    
    async def monitor_task_changes(self, callback=None, interval: int = 30) -> None:
        """監控任務變化"""
        self.logger.info("👁️ 開始監控任務變化...")
        
        self.monitoring_active = True
        last_task_count = 0
        last_task_states = {}
        
        while self.monitoring_active:
            try:
                # 獲取當前任務
                current_tasks = await self.extract_task_list()
                current_task_count = len(current_tasks)
                
                # 檢查任務數量變化
                if current_task_count != last_task_count:
                    self.logger.info(f"📊 任務數量變化: {last_task_count} -> {current_task_count}")
                    
                    if callback:
                        await callback('task_count_change', {
                            'old_count': last_task_count,
                            'new_count': current_task_count,
                            'tasks': current_tasks
                        })
                    
                    last_task_count = current_task_count
                
                # 檢查任務狀態變化
                current_task_states = {task.task_id: task.status for task in current_tasks}
                
                for task_id, current_status in current_task_states.items():
                    if task_id in last_task_states:
                        old_status = last_task_states[task_id]
                        if old_status != current_status:
                            self.logger.info(f"🔄 任務狀態變化: {task_id} {old_status} -> {current_status}")
                            
                            if callback:
                                await callback('task_status_change', {
                                    'task_id': task_id,
                                    'old_status': old_status,
                                    'new_status': current_status
                                })
                
                last_task_states = current_task_states
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"監控任務變化錯誤: {e}")
                await asyncio.sleep(60)  # 錯誤時等待更長時間
    
    def stop_monitoring(self):
        """停止監控"""
        self.monitoring_active = False
        self.logger.info("🛑 停止任務監控")
    
    async def send_message(self, message: str, wait_for_response: bool = True) -> bool:
        """發送消息到輸入框"""
        self.logger.info(f"📤 發送消息: {message[:50]}...")
        
        try:
            # 查找輸入框
            input_box = await self._find_input_box()
            if not input_box:
                self.logger.error("找不到輸入框")
                return False
            
            # 清空並輸入消息
            await input_box.fill("")
            await asyncio.sleep(0.5)
            await input_box.fill(message)
            await asyncio.sleep(1)
            
            # 查找並點擊發送按鈕
            send_button = await self._find_send_button()
            if send_button:
                await send_button.click()
                self.logger.info("✅ 點擊發送按鈕")
            else:
                # 嘗試按Enter鍵
                await input_box.press('Enter')
                self.logger.info("✅ 按下Enter鍵")
            
            # 等待發送完成
            await asyncio.sleep(2)
            
            # 如果需要等待回應
            if wait_for_response:
                await self._wait_for_response()
            
            self.logger.info("✅ 消息發送成功")
            return True
            
        except Exception as e:
            self.logger.error(f"發送消息失敗: {e}")
            return False
    
    async def _find_input_box(self):
        """查找輸入框"""
        return await self._find_element(self.selectors['input_box'])
    
    async def _find_send_button(self):
        """查找發送按鈕"""
        return await self._find_element(self.selectors['send_button'])
    
    async def _find_element(self, selectors: List[str]):
        """查找元素"""
        for selector in selectors:
            try:
                element = await self.page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    is_enabled = await element.is_enabled()
                    
                    if is_visible and is_enabled:
                        self.logger.debug(f"找到元素: {selector}")
                        return element
            except:
                continue
        
        return None
    
    async def _find_elements(self, selectors: List[str]):
        """查找多個元素"""
        for selector in selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                if elements:
                    self.logger.debug(f"使用選擇器 '{selector}' 找到 {len(elements)} 個元素")
                    return elements
            except:
                continue
        
        return []
    
    async def _wait_for_response(self, timeout: int = 30):
        """等待回應"""
        try:
            # 等待新消息出現
            start_time = time.time()
            initial_message_count = len(await self._find_elements(self.selectors['message_item']))
            
            while time.time() - start_time < timeout:
                await asyncio.sleep(2)
                current_message_count = len(await self._find_elements(self.selectors['message_item']))
                
                if current_message_count > initial_message_count:
                    self.logger.info("✅ 檢測到新回應")
                    return
            
            self.logger.warning("⚠️ 等待回應超時")
            
        except Exception as e:
            self.logger.error(f"等待回應失敗: {e}")
    
    async def auto_reply_with_intelligence(self, trigger_keywords: List[str], response_template: str):
        """智能自動回覆"""
        self.logger.info("🤖 開始智能自動回覆監控...")
        
        last_message_count = 0
        
        while self.monitoring_active:
            try:
                # 獲取最新消息
                messages = await self.extract_conversation_history()
                current_message_count = len(messages)
                
                if current_message_count > last_message_count:
                    # 檢查新消息
                    new_messages = messages[last_message_count:]
                    
                    for message in new_messages:
                        if message.sender == 'user':  # 只處理用戶消息
                            content_lower = message.content.lower()
                            
                            # 檢查是否包含觸發關鍵詞
                            for keyword in trigger_keywords:
                                if keyword.lower() in content_lower:
                                    self.logger.info(f"🎯 檢測到觸發關鍵詞: {keyword}")
                                    
                                    # 生成回覆
                                    reply = response_template.format(
                                        keyword=keyword,
                                        user_message=message.content,
                                        timestamp=datetime.now().strftime('%H:%M')
                                    )
                                    
                                    # 發送回覆
                                    await asyncio.sleep(2)  # 稍等一下再回覆
                                    await self.send_message(reply)
                                    break
                    
                    last_message_count = current_message_count
                
                await asyncio.sleep(10)  # 每10秒檢查一次
                
            except Exception as e:
                self.logger.error(f"智能自動回覆錯誤: {e}")
                await asyncio.sleep(30)
    
    async def cleanup(self):
        """清理資源"""
        try:
            self.monitoring_active = False
            
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            self.logger.info("✅ 資源清理完成")
            
        except Exception as e:
            self.logger.error(f"清理資源失敗: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return {
            'conversations_count': len(self.conversations),
            'tasks_count': len(self.tasks),
            'monitoring_active': self.monitoring_active,
            'manus_url': self.manus_url,
            'last_update': datetime.now().isoformat()
        }

# 使用示例
async def main():
    """主函數示例"""
    operator = ManusPlaywrightOperator()
    
    try:
        # 初始化
        await operator.initialize(headless=False)  # 設置為False以便觀察
        
        print("🔍 1. 提取對話歷史...")
        conversations = await operator.extract_conversation_history()
        print(f"✅ 提取了 {len(conversations)} 條對話")
        
        print("📋 2. 提取任務列表...")
        tasks = await operator.extract_task_list()
        print(f"✅ 提取了 {len(tasks)} 個任務")
        
        print("📥 3. 批量下載數據...")
        await operator.batch_download_data()
        
        print("📤 4. 測試發送消息...")
        await operator.send_message("這是一條測試消息")
        
        print("👁️ 5. 開始監控（運行30秒）...")
        
        async def task_change_callback(event_type, data):
            print(f"📊 任務變化事件: {event_type} - {data}")
        
        # 啟動監控任務
        monitor_task = asyncio.create_task(
            operator.monitor_task_changes(callback=task_change_callback, interval=10)
        )
        
        # 運行30秒後停止
        await asyncio.sleep(30)
        operator.stop_monitoring()
        
        print("✅ 演示完成")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    finally:
        await operator.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

