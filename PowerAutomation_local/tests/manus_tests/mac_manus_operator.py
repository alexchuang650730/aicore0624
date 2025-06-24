#!/usr/bin/env python3
"""
Mac本地版Manus操作腳本
直接在Mac上運行，無需隧道
實現：對話歷史提取、批量下載、任務監控、輸入框操作
"""

import asyncio
import json
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

# 檢查並安裝playwright
try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
except ImportError:
    print("❌ 需要安裝playwright")
    print("請執行: pip3 install playwright && playwright install chromium")
    sys.exit(1)

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

class MacManusOperator:
    """Mac本地Manus操作器"""
    
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
        
        # 選擇器配置 - 針對Manus頁面優化
        self.selectors = {
            # 對話相關選擇器
            'conversation_container': [
                '.conversation-container',
                '.chat-container', 
                '.messages-container',
                '[data-testid="conversation"]',
                '.conversation-view',
                '.chat-view',
                '.main-content',
                '#chat-container'
            ],
            'message_list': [
                '.message-list',
                '.conversation-messages',
                '.chat-messages',
                '[data-testid="messages"]',
                '.messages',
                '.chat-history',
                '.conversation-history'
            ],
            'message_item': [
                '.message',
                '.chat-message',
                '.conversation-message',
                '[data-testid="message"]',
                '.msg',
                '.message-item',
                '.chat-bubble',
                '.message-bubble',
                '[role="listitem"]',
                '.message-row'
            ],
            'message_content': [
                '.message-content',
                '.message-text',
                '.content',
                '.text',
                'p',
                '.message-body',
                '.chat-text',
                '.bubble-content'
            ],
            'message_sender': [
                '.sender',
                '.author',
                '.user',
                '.message-sender',
                '[data-sender]',
                '.message-author',
                '.user-name',
                '.sender-name'
            ],
            'message_timestamp': [
                '.timestamp',
                '.time',
                '.date',
                '.message-time',
                '[data-time]',
                '.message-timestamp',
                '.time-stamp',
                'time'
            ],
            
            # 任務相關選擇器
            'task_container': [
                '.task-container',
                '.tasks-container',
                '.todo-container',
                '[data-testid="tasks"]',
                '.task-list-container',
                '.project-tasks',
                '.task-board'
            ],
            'task_list': [
                '.task-list',
                '.todo-list',
                '.tasks',
                '[data-testid="task-list"]',
                '.task-items',
                '.task-grid'
            ],
            'task_item': [
                '.task-item',
                '.task',
                '.todo-item',
                '[data-testid="task"]',
                '.task-card',
                '.task-row',
                '.project-item'
            ],
            
            # 輸入相關選擇器
            'input_container': [
                '.input-container',
                '.message-input-container',
                '.chat-input-container',
                '[data-testid="input-container"]',
                '.compose-container',
                '.input-area'
            ],
            'input_box': [
                'textarea[placeholder*="輸入"]',
                'textarea[placeholder*="input"]',
                'textarea[placeholder*="message"]',
                'textarea[placeholder*="Type"]',
                'textarea[placeholder*="Enter"]',
                'input[type="text"]',
                '.input-box',
                '.message-input',
                '[data-testid="message-input"]',
                'textarea',
                '.chat-input',
                '.text-input',
                '[contenteditable="true"]',
                '.compose-input'
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
                '[aria-label*="發送"]',
                '.send-icon',
                '[data-action="send"]'
            ]
        }
    
    def _setup_logger(self) -> logging.Logger:
        """設置日誌"""
        logger = logging.getLogger("MacManus")
        logger.setLevel(logging.INFO)
        
        # 清除現有處理器
        logger.handlers.clear()
        
        # 創建logs目錄
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 文件處理器
        log_file = log_dir / f"manus_operations_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
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
                    '--disable-web-security'
                ]
            )
            
            # 創建上下文
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            # 創建頁面
            self.page = await self.context.new_page()
            
            # 導航到Manus頁面
            self.logger.info(f"🌐 導航到Manus頁面: {self.manus_url}")
            await self.page.goto(self.manus_url, wait_until='networkidle', timeout=60000)
            
            # 等待頁面加載
            await self._wait_for_page_ready()
            
            self.logger.info("✅ Playwright初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 初始化Playwright失敗: {e}")
            return False
    
    async def _wait_for_page_ready(self, timeout: int = 60):
        """等待頁面準備就緒"""
        try:
            # 等待基本元素
            await self.page.wait_for_selector('body', timeout=timeout * 1000)
            
            # 檢查是否需要登入
            if await self._check_login_required():
                self.logger.info("🔐 檢測到需要登入，請手動完成登入...")
                print("\n" + "="*50)
                print("🔐 請在瀏覽器中完成登入")
                print("登入完成後按 Enter 繼續...")
                print("="*50)
                input()
                
                # 等待登入完成
                await asyncio.sleep(3)
            
            # 等待內容加載
            await asyncio.sleep(5)
            
            self.logger.info("✅ 頁面準備就緒")
            
        except Exception as e:
            self.logger.error(f"❌ 等待頁面準備失敗: {e}")
    
    async def _check_login_required(self) -> bool:
        """檢查是否需要登入"""
        login_selectors = [
            'input[type="password"]',
            '.login-form',
            '.signin',
            'button:has-text("登入")',
            'button:has-text("Login")',
            'button:has-text("Sign in")',
            '.auth-form',
            '.login-container'
        ]
        
        for selector in login_selectors:
            try:
                element = await self.page.query_selector(selector)
                if element and await element.is_visible():
                    return True
            except:
                continue
        
        return False
    
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
            self.logger.error(f"❌ 提取對話歷史失敗: {e}")
            return []
    
    async def _scroll_to_load_all_content(self):
        """滾動加載所有內容"""
        self.logger.info("📜 滾動加載所有內容...")
        
        # 先滾動到頂部
        await self.page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(2)
        
        last_height = 0
        scroll_attempts = 0
        max_attempts = 50
        
        while scroll_attempts < max_attempts:
            # 滾動到底部
            current_height = await self.page.evaluate("document.body.scrollHeight")
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            # 檢查高度是否變化
            new_height = await self.page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                # 嘗試滾動對話容器
                try:
                    await self.page.evaluate("""
                        const containers = document.querySelectorAll('.conversation-container, .chat-container, .messages-container');
                        containers.forEach(container => {
                            container.scrollTop = container.scrollHeight;
                        });
                    """)
                    await asyncio.sleep(2)
                except:
                    pass
                
                # 如果還是沒變化，退出
                final_height = await self.page.evaluate("document.body.scrollHeight")
                if final_height == last_height:
                    break
            
            last_height = new_height
            scroll_attempts += 1
            
            if scroll_attempts % 10 == 0:
                self.logger.info(f"已滾動 {scroll_attempts} 次...")
        
        self.logger.info(f"✅ 滾動完成，共滾動 {scroll_attempts} 次")
    
    async def _find_all_messages(self) -> List[ConversationMessage]:
        """查找所有消息"""
        messages = []
        
        # 嘗試不同的選擇器查找消息
        for selector_group in ['message_item']:
            message_elements = await self._find_elements(self.selectors[selector_group])
            
            if message_elements:
                self.logger.info(f"使用選擇器組 '{selector_group}' 找到 {len(message_elements)} 個消息元素")
                
                for i, element in enumerate(message_elements):
                    try:
                        message = await self._parse_message_element(element, i)
                        if message and message.content.strip():
                            messages.append(message)
                    except Exception as e:
                        self.logger.debug(f"解析消息 {i} 失敗: {e}")
                
                break  # 找到消息就停止嘗試其他選擇器
        
        # 如果沒找到消息，嘗試通用方法
        if not messages:
            self.logger.info("嘗試通用消息提取方法...")
            messages = await self._extract_messages_generic()
        
        return messages
    
    async def _extract_messages_generic(self) -> List[ConversationMessage]:
        """通用消息提取方法"""
        messages = []
        
        try:
            # 獲取頁面所有文本內容
            page_content = await self.page.content()
            
            # 嘗試查找包含對話的元素
            potential_message_elements = await self.page.query_selector_all('div, p, span')
            
            for i, element in enumerate(potential_message_elements):
                try:
                    text = await element.inner_text()
                    if text and len(text.strip()) > 10:  # 過濾太短的文本
                        # 簡單的消息檢測邏輯
                        if any(keyword in text.lower() for keyword in ['user:', 'assistant:', '用戶:', 'ai:', 'bot:']):
                            message = ConversationMessage(
                                id=f"generic_msg_{i}",
                                content=text.strip(),
                                sender="unknown",
                                timestamp=datetime.now(),
                                message_type="generic",
                                conversation_id="main",
                                metadata={'method': 'generic', 'index': i}
                            )
                            messages.append(message)
                except:
                    continue
            
            self.logger.info(f"通用方法找到 {len(messages)} 條消息")
            
        except Exception as e:
            self.logger.error(f"通用消息提取失敗: {e}")
        
        return messages
    
    async def _parse_message_element(self, element, index: int) -> Optional[ConversationMessage]:
        """解析消息元素"""
        try:
            # 提取內容
            content = await self._extract_text_from_element(element, self.selectors['message_content'])
            if not content:
                content = await element.inner_text()
            
            if not content or not content.strip():
                return None
            
            # 提取發送者
            sender = await self._extract_text_from_element(element, self.selectors['message_sender'])
            if not sender:
                # 從CSS類名或位置判斷
                class_name = await element.get_attribute('class') or ""
                if any(cls in class_name.lower() for cls in ['user', 'human', 'customer']):
                    sender = 'user'
                elif any(cls in class_name.lower() for cls in ['assistant', 'ai', 'bot', 'system']):
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
                content=content.strip(),
                sender=sender,
                timestamp=timestamp,
                message_type=self._determine_message_type(content, sender),
                conversation_id="main",
                attachments=attachments or [],
                metadata={
                    'index': index,
                    'element_class': await element.get_attribute('class'),
                    'extraction_time': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.debug(f"解析消息元素失敗: {e}")
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
            import re
            
            # 處理相對時間
            if "分鐘前" in time_str or "minutes ago" in time_str:
                match = re.search(r'(\d+)', time_str)
                if match:
                    minutes = int(match.group(1))
                    return datetime.now() - timedelta(minutes=minutes)
            
            if "小時前" in time_str or "hours ago" in time_str:
                match = re.search(r'(\d+)', time_str)
                if match:
                    hours = int(match.group(1))
                    return datetime.now() - timedelta(hours=hours)
            
            if "天前" in time_str or "days ago" in time_str:
                match = re.search(r'(\d+)', time_str)
                if match:
                    days = int(match.group(1))
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
    
    async def send_message(self, message: str, wait_for_response: bool = True) -> bool:
        """發送消息到輸入框"""
        self.logger.info(f"📤 發送消息: {message[:50]}...")
        
        try:
            # 查找輸入框
            input_box = await self._find_input_box()
            if not input_box:
                self.logger.error("❌ 找不到輸入框")
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
            await asyncio.sleep(3)
            
            # 如果需要等待回應
            if wait_for_response:
                await self._wait_for_response()
            
            self.logger.info("✅ 消息發送成功")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 發送消息失敗: {e}")
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
            start_time = time.time()
            initial_message_count = len(await self._find_elements(self.selectors['message_item']))
            
            while time.time() - start_time < timeout:
                await asyncio.sleep(3)
                current_message_count = len(await self._find_elements(self.selectors['message_item']))
                
                if current_message_count > initial_message_count:
                    self.logger.info("✅ 檢測到新回應")
                    return
            
            self.logger.warning("⚠️ 等待回應超時")
            
        except Exception as e:
            self.logger.error(f"❌ 等待回應失敗: {e}")
    
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
                
                # 保存為可讀格式
                readable_file = output_path / f"conversations_readable_{timestamp}.txt"
                with open(readable_file, 'w', encoding='utf-8') as f:
                    f.write(f"Manus對話歷史 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    
                    for conv in conversations:
                        f.write(f"[{conv.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {conv.sender}:\n")
                        f.write(f"{conv.content}\n")
                        if conv.attachments:
                            f.write(f"附件: {', '.join(conv.attachments)}\n")
                        f.write("-" * 40 + "\n\n")
                
                self.logger.info(f"📄 可讀格式已保存: {readable_file}")
            
            # 2. 保存頁面截圖
            screenshot_file = output_path / f"screenshot_{timestamp}.png"
            await self.page.screenshot(path=str(screenshot_file), full_page=True)
            self.logger.info(f"📸 頁面截圖已保存: {screenshot_file}")
            
            # 3. 保存頁面HTML
            html_file = output_path / f"page_content_{timestamp}.html"
            html_content = await self.page.content()
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.logger.info(f"📄 頁面HTML已保存: {html_file}")
            
            # 4. 生成統計報告
            stats_file = output_path / f"statistics_{timestamp}.json"
            stats = {
                'extraction_time': datetime.now().isoformat(),
                'total_conversations': len(conversations),
                'conversation_types': {},
                'senders': {},
                'time_range': {
                    'earliest': min([c.timestamp for c in conversations]).isoformat() if conversations else None,
                    'latest': max([c.timestamp for c in conversations]).isoformat() if conversations else None
                }
            }
            
            # 統計消息類型和發送者
            for conv in conversations:
                stats['conversation_types'][conv.message_type] = stats['conversation_types'].get(conv.message_type, 0) + 1
                stats['senders'][conv.sender] = stats['senders'].get(conv.sender, 0) + 1
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            self.logger.info(f"📊 統計報告已保存: {stats_file}")
            
            self.logger.info(f"✅ 批量下載完成，文件保存在: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 批量下載失敗: {e}")
            return False
    
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
            self.logger.error(f"❌ 清理資源失敗: {e}")

# 命令行界面
async def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Mac本地Manus操作工具')
    parser.add_argument('--url', default='https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ', 
                       help='Manus頁面URL')
    parser.add_argument('--headless', action='store_true', help='無頭模式運行')
    parser.add_argument('--action', choices=['conversations', 'send', 'download', 'interactive', 'demo'],
                       default='interactive', help='要執行的操作')
    parser.add_argument('--message', help='要發送的消息 (用於send操作)')
    parser.add_argument('--output', default='manus_data', help='下載輸出目錄')
    
    args = parser.parse_args()
    
    # 創建操作器
    operator = MacManusOperator(args.url)
    
    try:
        print("🚀 啟動Mac本地Manus操作器...")
        print(f"📍 目標URL: {args.url}")
        print(f"🖥️ 無頭模式: {args.headless}")
        
        # 初始化
        success = await operator.initialize(headless=args.headless)
        if not success:
            print("❌ 初始化失敗")
            return 1
        
        print("✅ 初始化成功")
        
        # 執行指定操作
        if args.action == 'conversations':
            print("📜 提取對話歷史...")
            conversations = await operator.extract_conversation_history()
            print(f"✅ 成功提取 {len(conversations)} 條對話")
            
            # 顯示最近5條對話
            if conversations:
                print("\n📋 最近的對話:")
                for conv in conversations[-5:]:
                    print(f"  [{conv.timestamp.strftime('%H:%M')}] {conv.sender}: {conv.content[:50]}...")
        
        elif args.action == 'send':
            if not args.message:
                print("❌ 請使用 --message 指定要發送的消息")
                return 1
            
            print(f"📤 發送消息: {args.message[:30]}...")
            success = await operator.send_message(args.message)
            if success:
                print("✅ 消息發送成功")
            else:
                print("❌ 消息發送失敗")
        
        elif args.action == 'download':
            print(f"📥 批量下載到 {args.output}...")
            success = await operator.batch_download_data(args.output)
            if success:
                print("✅ 批量下載完成")
            else:
                print("❌ 批量下載失敗")
        
        elif args.action == 'demo':
            print("🎬 執行完整演示...")
            
            # 1. 提取對話
            conversations = await operator.extract_conversation_history()
            print(f"📜 提取了 {len(conversations)} 條對話")
            
            # 2. 批量下載
            await operator.batch_download_data(args.output)
            print("📥 完成批量下載")
            
            # 3. 發送測試消息
            test_message = "這是Mac本地腳本發送的測試消息"
            await operator.send_message(test_message)
            print("📤 發送了測試消息")
            
            print("✅ 演示完成")
        
        elif args.action == 'interactive':
            print("🎮 進入交互模式")
            await interactive_mode(operator)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 用戶中斷")
        return 0
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")
        return 1
    finally:
        await operator.cleanup()

async def interactive_mode(operator):
    """交互模式"""
    print("\n" + "="*50)
    print("🎮 Manus交互操作模式")
    print("="*50)
    print("可用命令:")
    print("  1 - 提取對話歷史")
    print("  2 - 發送消息")
    print("  3 - 批量下載數據")
    print("  4 - 執行完整演示")
    print("  5 - 頁面截圖")
    print("  q - 退出")
    print("="*50)
    
    while True:
        try:
            command = input("\n請輸入命令 (1-5, q): ").strip()
            
            if command == 'q':
                print("👋 退出交互模式")
                break
            elif command == '1':
                print("📜 提取對話歷史...")
                conversations = await operator.extract_conversation_history()
                print(f"✅ 成功提取 {len(conversations)} 條對話")
                
                if conversations:
                    print("\n📋 最近的對話:")
                    for conv in conversations[-5:]:
                        print(f"  [{conv.timestamp.strftime('%H:%M')}] {conv.sender}: {conv.content[:80]}...")
                    
                    # 詢問是否保存
                    save = input("\n是否保存對話歷史? (y/n): ").strip().lower()
                    if save == 'y':
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"conversations_{timestamp}.json"
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump([asdict(conv) for conv in conversations], f, 
                                     ensure_ascii=False, indent=2, default=str)
                        print(f"💾 已保存到: {filename}")
            
            elif command == '2':
                message = input("請輸入要發送的消息: ").strip()
                if message:
                    print(f"📤 發送消息: {message[:30]}...")
                    success = await operator.send_message(message)
                    if success:
                        print("✅ 消息發送成功")
                    else:
                        print("❌ 消息發送失敗")
                else:
                    print("❌ 消息不能為空")
            
            elif command == '3':
                output_dir = input("輸入下載目錄 (默認: manus_data): ").strip() or "manus_data"
                print(f"📥 批量下載到 {output_dir}...")
                success = await operator.batch_download_data(output_dir)
                if success:
                    print("✅ 批量下載完成")
                else:
                    print("❌ 批量下載失敗")
            
            elif command == '4':
                print("🎬 執行完整演示...")
                
                # 提取對話
                conversations = await operator.extract_conversation_history()
                print(f"📜 提取了 {len(conversations)} 條對話")
                
                # 批量下載
                await operator.batch_download_data("demo_output")
                print("📥 完成批量下載")
                
                # 發送測試消息
                test_message = f"Mac本地測試消息 - {datetime.now().strftime('%H:%M:%S')}"
                await operator.send_message(test_message)
                print("📤 發送了測試消息")
                
                print("✅ 演示完成")
            
            elif command == '5':
                print("📸 正在截圖...")
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                screenshot_file = f"screenshot_{timestamp}.png"
                await operator.page.screenshot(path=screenshot_file, full_page=True)
                print(f"✅ 截圖已保存: {screenshot_file}")
            
            else:
                print("❌ 無效命令，請輸入 1-5 或 q")
        
        except KeyboardInterrupt:
            print("\n👋 用戶中斷")
            break
        except Exception as e:
            print(f"❌ 執行命令時發生錯誤: {e}")

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))

