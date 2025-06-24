"""
Manus智能操作腳本
實現對話歷史提取、批量下載、任務列表監控、輸入框操作
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import re
import os
from pathlib import Path

@dataclass
class ManusMessage:
    """Manus消息數據結構"""
    id: str
    content: str
    sender: str  # user, assistant, system
    timestamp: datetime
    message_type: str
    conversation_id: str
    metadata: Dict[str, Any] = None

@dataclass
class ManusTask:
    """Manus任務數據結構"""
    task_id: str
    title: str
    status: str  # pending, active, completed, failed
    priority: str
    created_at: datetime
    updated_at: datetime
    description: str
    metadata: Dict[str, Any] = None

class ManusOperator:
    """Manus操作器 - 在Mac本機運行"""
    
    def __init__(self, config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.browser = None
        self.context = None
        self.page = None
        self.is_running = False
        
        # 數據存儲
        self.conversations = {}
        self.tasks = {}
        self.message_history = []
        
        # 頁面元素選擇器
        self.selectors = {
            # 對話相關
            'conversation_list': [
                '.conversation-list',
                '.chat-list', 
                '.message-list',
                '[data-testid="conversation-list"]',
                '.conversations'
            ],
            'message_container': [
                '.message',
                '.chat-message',
                '.conversation-message',
                '[data-testid="message"]',
                '.msg'
            ],
            'message_content': [
                '.message-content',
                '.message-text',
                '.content',
                '.text',
                'p'
            ],
            'message_sender': [
                '.sender',
                '.author',
                '.user',
                '.message-sender',
                '[data-sender]'
            ],
            'message_time': [
                '.timestamp',
                '.time',
                '.date',
                '.message-time',
                '[data-time]'
            ],
            
            # 任務相關
            'task_list': [
                '.task-list',
                '.todo-list',
                '.tasks',
                '[data-testid="task-list"]',
                '.task-container'
            ],
            'task_item': [
                '.task-item',
                '.task',
                '.todo-item',
                '[data-testid="task"]',
                '.task-card'
            ],
            'task_title': [
                '.task-title',
                '.title',
                'h3',
                'h4',
                '.task-name'
            ],
            'task_status': [
                '.status',
                '.task-status',
                '.state',
                '[data-status]',
                '.badge'
            ],
            
            # 輸入相關
            'input_box': [
                'textarea[placeholder*="輸入"]',
                'textarea[placeholder*="input"]',
                'textarea[placeholder*="message"]',
                'input[type="text"]',
                '.input-box',
                '.message-input',
                '[data-testid="message-input"]',
                'textarea',
                '.chat-input'
            ],
            'send_button': [
                'button[type="submit"]',
                '.send-button',
                '.send-btn',
                '[data-testid="send"]',
                'button:has-text("發送")',
                'button:has-text("Send")',
                '.submit-btn'
            ],
            
            # 下載相關
            'download_button': [
                '.download',
                '.export',
                'button:has-text("下載")',
                'button:has-text("導出")',
                'button:has-text("Download")',
                '[data-action="download"]'
            ]
        }
    
    async def start(self):
        """啟動Manus操作器"""
        if self.is_running:
            self.logger.warning("Manus操作器已經在運行中")
            return
        
        self.is_running = True
        self.logger.info("🚀 啟動Manus操作器...")
        
        try:
            # 啟動瀏覽器
            await self._init_browser()
            
            # 導航到Manus頁面
            await self._navigate_to_manus()
            
            # 等待頁面加載
            await self._wait_for_page_load()
            
            self.logger.info("✅ Manus操作器啟動完成")
            
        except Exception as e:
            self.logger.error(f"啟動Manus操作器失敗: {e}")
            raise
    
    async def stop(self):
        """停止操作器"""
        self.is_running = False
        await self._cleanup()
        self.logger.info("🛑 Manus操作器已停止")
    
    async def _init_browser(self):
        """初始化瀏覽器"""
        playwright = await async_playwright().start()
        
        # 啟動瀏覽器（非無頭模式，因為可能需要登入）
        self.browser = await playwright.chromium.launch(
            headless=False,  # 顯示瀏覽器以便登入
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # 創建上下文
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        # 創建頁面
        self.page = await self.context.new_page()
        
        self.logger.info("✅ 瀏覽器初始化完成")
    
    async def _navigate_to_manus(self):
        """導航到Manus頁面"""
        manus_url = "https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ"
        
        self.logger.info(f"🌐 導航到Manus頁面: {manus_url}")
        await self.page.goto(manus_url, wait_until='networkidle')
        
        # 等待一下讓頁面完全加載
        await asyncio.sleep(3)
    
    async def _wait_for_page_load(self):
        """等待頁面加載完成"""
        try:
            # 等待主要元素出現
            await self.page.wait_for_selector('body', timeout=10000)
            
            # 檢查是否需要登入
            if await self._check_login_required():
                self.logger.info("🔐 檢測到需要登入，請手動完成登入...")
                await self._wait_for_login()
            
            self.logger.info("✅ 頁面加載完成")
            
        except Exception as e:
            self.logger.error(f"等待頁面加載失敗: {e}")
    
    async def _check_login_required(self) -> bool:
        """檢查是否需要登入"""
        login_indicators = [
            'input[type="password"]',
            '.login-form',
            '.signin',
            'button:has-text("登入")',
            'button:has-text("Login")'
        ]
        
        for indicator in login_indicators:
            try:
                element = await self.page.query_selector(indicator)
                if element:
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
                return
            
            await asyncio.sleep(5)
        
        raise TimeoutError("登入超時")
    
    async def get_conversation_history(self) -> List[ManusMessage]:
        """獲取對話歷史"""
        self.logger.info("📜 開始獲取對話歷史...")
        
        messages = []
        
        try:
            # 滾動加載所有消息
            await self._scroll_to_load_all_messages()
            
            # 查找消息容器
            message_containers = await self._find_elements(self.selectors['message_container'])
            
            self.logger.info(f"找到 {len(message_containers)} 個消息容器")
            
            for i, container in enumerate(message_containers):
                try:
                    message = await self._parse_message(container, i)
                    if message:
                        messages.append(message)
                except Exception as e:
                    self.logger.error(f"解析消息 {i} 失敗: {e}")
            
            self.logger.info(f"✅ 成功獲取 {len(messages)} 條對話歷史")
            self.message_history = messages
            
        except Exception as e:
            self.logger.error(f"獲取對話歷史失敗: {e}")
        
        return messages
    
    async def _scroll_to_load_all_messages(self):
        """滾動加載所有消息"""
        self.logger.info("📜 滾動加載所有消息...")
        
        # 先滾動到頂部
        await self.page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        
        last_height = await self.page.evaluate("document.body.scrollHeight")
        scroll_attempts = 0
        max_attempts = 50
        
        while scroll_attempts < max_attempts:
            # 滾動到底部
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            # 檢查是否有新內容
            new_height = await self.page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            
            last_height = new_height
            scroll_attempts += 1
            
            self.logger.debug(f"滾動第 {scroll_attempts} 次，頁面高度: {new_height}")
        
        # 滾動回頂部
        await self.page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        
        self.logger.info(f"✅ 滾動完成，共滾動 {scroll_attempts} 次")
    
    async def _find_elements(self, selectors: List[str]):
        """查找元素"""
        for selector in selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                if elements:
                    self.logger.debug(f"使用選擇器 '{selector}' 找到 {len(elements)} 個元素")
                    return elements
            except Exception as e:
                self.logger.debug(f"選擇器 '{selector}' 失敗: {e}")
                continue
        
        self.logger.warning(f"所有選擇器都失敗: {selectors}")
        return []
    
    async def _parse_message(self, container, index: int) -> Optional[ManusMessage]:
        """解析單個消息"""
        try:
            # 提取內容
            content = await self._extract_text_from_element(
                container, self.selectors['message_content']
            )
            
            # 提取發送者
            sender = await self._extract_text_from_element(
                container, self.selectors['message_sender']
            ) or "unknown"
            
            # 提取時間
            timestamp = await self._extract_time_from_element(
                container, self.selectors['message_time']
            ) or datetime.now()
            
            # 生成消息ID
            message_id = f"msg_{index}_{int(timestamp.timestamp())}"
            
            # 判斷消息類型
            message_type = self._determine_message_type(container, content, sender)
            
            return ManusMessage(
                id=message_id,
                content=content or "",
                sender=sender,
                timestamp=timestamp,
                message_type=message_type,
                conversation_id="main",
                metadata={
                    'index': index,
                    'html': await container.inner_html() if container else ""
                }
            )
            
        except Exception as e:
            self.logger.error(f"解析消息失敗: {e}")
            return None
    
    async def _extract_text_from_element(self, container, selectors: List[str]) -> Optional[str]:
        """從元素中提取文本"""
        for selector in selectors:
            try:
                element = await container.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    if text and text.strip():
                        return text.strip()
            except:
                continue
        
        # 如果都沒找到，返回容器的文本
        try:
            return await container.inner_text()
        except:
            return None
    
    async def _extract_time_from_element(self, container, selectors: List[str]) -> Optional[datetime]:
        """從元素中提取時間"""
        for selector in selectors:
            try:
                element = await container.query_selector(selector)
                if element:
                    # 嘗試從屬性獲取
                    for attr in ['datetime', 'data-time', 'title']:
                        time_str = await element.get_attribute(attr)
                        if time_str:
                            parsed_time = self._parse_time_string(time_str)
                            if parsed_time:
                                return parsed_time
                    
                    # 嘗試從文本獲取
                    text = await element.inner_text()
                    if text:
                        parsed_time = self._parse_time_string(text)
                        if parsed_time:
                            return parsed_time
            except:
                continue
        
        return None
    
    def _parse_time_string(self, time_str: str) -> Optional[datetime]:
        """解析時間字符串"""
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
            
        except Exception:
            return None
    
    def _determine_message_type(self, container, content: str, sender: str) -> str:
        """判斷消息類型"""
        try:
            # 檢查CSS類名
            class_name = container.get_attribute('class') or ""
            
            if 'user' in class_name.lower() or 'human' in class_name.lower():
                return 'user'
            elif 'assistant' in class_name.lower() or 'ai' in class_name.lower() or 'bot' in class_name.lower():
                return 'assistant'
            elif 'system' in class_name.lower():
                return 'system'
            
            # 根據發送者判斷
            if sender and sender.lower() in ['user', 'human', '用戶']:
                return 'user'
            elif sender and sender.lower() in ['assistant', 'ai', 'bot', '助手']:
                return 'assistant'
            
            return 'unknown'
            
        except:
            return 'unknown'
    
    async def get_task_list(self) -> List[ManusTask]:
        """獲取任務列表"""
        self.logger.info("📋 開始獲取任務列表...")
        
        tasks = []
        
        try:
            # 查找任務容器
            task_containers = await self._find_elements(self.selectors['task_item'])
            
            self.logger.info(f"找到 {len(task_containers)} 個任務")
            
            for i, container in enumerate(task_containers):
                try:
                    task = await self._parse_task(container, i)
                    if task:
                        tasks.append(task)
                except Exception as e:
                    self.logger.error(f"解析任務 {i} 失敗: {e}")
            
            self.logger.info(f"✅ 成功獲取 {len(tasks)} 個任務")
            
        except Exception as e:
            self.logger.error(f"獲取任務列表失敗: {e}")
        
        return tasks
    
    async def _parse_task(self, container, index: int) -> Optional[ManusTask]:
        """解析單個任務"""
        try:
            # 提取標題
            title = await self._extract_text_from_element(
                container, self.selectors['task_title']
            ) or f"任務 {index}"
            
            # 提取狀態
            status = await self._extract_text_from_element(
                container, self.selectors['task_status']
            ) or "unknown"
            
            # 生成任務ID
            task_id = f"task_{index}_{int(time.time())}"
            
            return ManusTask(
                task_id=task_id,
                title=title,
                status=status.lower(),
                priority="normal",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                description=title,
                metadata={
                    'index': index,
                    'html': await container.inner_html()
                }
            )
            
        except Exception as e:
            self.logger.error(f"解析任務失敗: {e}")
            return None
    
    async def send_message(self, message: str) -> bool:
        """發送消息"""
        self.logger.info(f"📤 發送消息: {message[:50]}...")
        
        try:
            # 查找輸入框
            input_box = await self._find_input_box()
            if not input_box:
                self.logger.error("找不到輸入框")
                return False
            
            # 清空輸入框
            await input_box.fill("")
            await asyncio.sleep(0.5)
            
            # 輸入消息
            await input_box.fill(message)
            await asyncio.sleep(1)
            
            # 查找發送按鈕
            send_button = await self._find_send_button()
            if send_button:
                await send_button.click()
            else:
                # 嘗試按Enter鍵
                await input_box.press('Enter')
            
            await asyncio.sleep(2)
            
            self.logger.info("✅ 消息發送成功")
            return True
            
        except Exception as e:
            self.logger.error(f"發送消息失敗: {e}")
            return False
    
    async def _find_input_box(self):
        """查找輸入框"""
        for selector in self.selectors['input_box']:
            try:
                element = await self.page.query_selector(selector)
                if element:
                    # 檢查元素是否可見和可編輯
                    is_visible = await element.is_visible()
                    is_enabled = await element.is_enabled()
                    
                    if is_visible and is_enabled:
                        self.logger.debug(f"找到輸入框: {selector}")
                        return element
            except:
                continue
        
        return None
    
    async def _find_send_button(self):
        """查找發送按鈕"""
        for selector in self.selectors['send_button']:
            try:
                element = await self.page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    is_enabled = await element.is_enabled()
                    
                    if is_visible and is_enabled:
                        self.logger.debug(f"找到發送按鈕: {selector}")
                        return element
            except:
                continue
        
        return None
    
    async def batch_download_conversations(self, output_dir: str = "manus_data") -> bool:
        """批量下載對話"""
        self.logger.info("📥 開始批量下載對話...")
        
        try:
            # 創建輸出目錄
            os.makedirs(output_dir, exist_ok=True)
            
            # 獲取對話歷史
            messages = await self.get_conversation_history()
            
            # 保存為JSON
            conversations_file = os.path.join(output_dir, f"conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            with open(conversations_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(msg) for msg in messages], f, ensure_ascii=False, indent=2, default=str)
            
            # 獲取任務列表
            tasks = await self.get_task_list()
            
            # 保存任務
            tasks_file = os.path.join(output_dir, f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(task) for task in tasks], f, ensure_ascii=False, indent=2, default=str)
            
            # 保存頁面截圖
            screenshot_file = os.path.join(output_dir, f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            await self.page.screenshot(path=screenshot_file, full_page=True)
            
            self.logger.info(f"✅ 批量下載完成，文件保存在: {output_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"批量下載失敗: {e}")
            return False
    
    async def monitor_changes(self, callback=None):
        """監控頁面變化"""
        self.logger.info("👁️ 開始監控頁面變化...")
        
        last_message_count = 0
        last_task_count = 0
        
        while self.is_running:
            try:
                # 檢查新消息
                current_messages = await self.get_conversation_history()
                if len(current_messages) > last_message_count:
                    new_messages = current_messages[last_message_count:]
                    self.logger.info(f"🆕 檢測到 {len(new_messages)} 條新消息")
                    
                    if callback:
                        await callback('new_messages', new_messages)
                    
                    last_message_count = len(current_messages)
                
                # 檢查任務變化
                current_tasks = await self.get_task_list()
                if len(current_tasks) != last_task_count:
                    self.logger.info(f"📋 任務數量變化: {last_task_count} -> {len(current_tasks)}")
                    
                    if callback:
                        await callback('task_change', current_tasks)
                    
                    last_task_count = len(current_tasks)
                
                await asyncio.sleep(10)  # 每10秒檢查一次
                
            except Exception as e:
                self.logger.error(f"監控過程中發生錯誤: {e}")
                await asyncio.sleep(30)
    
    async def _cleanup(self):
        """清理資源"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
        except Exception as e:
            self.logger.error(f"清理資源失敗: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return {
            'is_running': self.is_running,
            'total_messages': len(self.message_history),
            'total_tasks': len(self.tasks),
            'last_update': datetime.now().isoformat()
        }

