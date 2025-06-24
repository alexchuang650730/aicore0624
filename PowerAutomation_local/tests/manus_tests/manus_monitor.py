"""
Manus對話監控模組
實現實時監控Manus平台的對話狀態和內容
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

@dataclass
class ManusConversation:
    """Manus對話數據結構"""
    conversation_id: str
    user_id: str
    title: str
    status: str  # active, waiting, stuck, resolved, abandoned
    last_message: str
    last_message_time: datetime
    message_count: int
    recent_messages: List[Dict[str, Any]]
    metadata: Dict[str, Any] = None

class ManusMonitor:
    """Manus平台監控器"""
    
    def __init__(self, config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.driver = None
        self.is_monitoring = False
        self.conversations = {}
        self.session = None
        
        # 監控統計
        self.stats = {
            'total_conversations': 0,
            'active_conversations': 0,
            'messages_processed': 0,
            'last_update': None
        }
    
    async def start_monitoring(self):
        """開始監控"""
        if self.is_monitoring:
            self.logger.warning("Manus監控已經在運行中")
            return
        
        self.is_monitoring = True
        self.logger.info("🔍 開始Manus對話監控...")
        
        try:
            # 初始化瀏覽器
            await self._init_browser()
            
            # 登入Manus（如果需要）
            await self._login_if_needed()
            
            # 開始監控循環
            while self.is_monitoring:
                await self._monitor_conversations()
                await asyncio.sleep(self.config.manus_check_interval)
                
        except Exception as e:
            self.logger.error(f"Manus監控錯誤: {e}")
        finally:
            await self._cleanup()
    
    def stop_monitoring(self):
        """停止監控"""
        self.is_monitoring = False
        self.logger.info("🛑 停止Manus監控...")
    
    async def _init_browser(self):
        """初始化瀏覽器"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 無頭模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            
            self.logger.info("✅ 瀏覽器初始化完成")
            
        except Exception as e:
            self.logger.error(f"瀏覽器初始化失敗: {e}")
            raise
    
    async def _login_if_needed(self):
        """如果需要則登入Manus"""
        try:
            self.driver.get(self.config.manus_base_url)
            await asyncio.sleep(2)
            
            # 檢查是否需要登入
            if "login" in self.driver.current_url.lower() or self._is_login_page():
                self.logger.info("🔐 檢測到需要登入，請手動完成登入...")
                # 這裡可以實現自動登入邏輯，或者等待手動登入
                await self._wait_for_login()
            
            self.logger.info("✅ Manus登入狀態確認")
            
        except Exception as e:
            self.logger.error(f"Manus登入檢查失敗: {e}")
    
    def _is_login_page(self) -> bool:
        """檢查是否為登入頁面"""
        try:
            # 尋找登入相關元素
            login_indicators = [
                "input[type='password']",
                "button[type='submit']",
                ".login-form",
                "#login",
                ".signin"
            ]
            
            for indicator in login_indicators:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, indicator)
                    return True
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception:
            return False
    
    async def _wait_for_login(self, timeout: int = 300):
        """等待登入完成"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self._is_login_page():
                self.logger.info("✅ 登入完成")
                return
            
            await asyncio.sleep(5)
        
        raise TimeoutException("登入超時")
    
    async def _monitor_conversations(self):
        """監控對話"""
        try:
            # 獲取對話列表
            conversations = await self._get_conversation_list()
            
            # 更新對話狀態
            for conv in conversations:
                await self._update_conversation(conv)
            
            # 更新統計
            self._update_stats(conversations)
            
            self.logger.debug(f"監控完成，發現 {len(conversations)} 個對話")
            
        except Exception as e:
            self.logger.error(f"監控對話時發生錯誤: {e}")
    
    async def _get_conversation_list(self) -> List[ManusConversation]:
        """獲取對話列表"""
        conversations = []
        
        try:
            # 導航到對話列表頁面
            await self._navigate_to_conversations()
            
            # 滾動加載所有對話
            await self._scroll_to_load_all()
            
            # 解析對話元素
            conversation_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".conversation-item, .chat-item, .task-item, [data-conversation-id]"
            )
            
            for element in conversation_elements:
                conv = await self._parse_conversation_element(element)
                if conv:
                    conversations.append(conv)
            
            self.logger.debug(f"解析到 {len(conversations)} 個對話")
            
        except Exception as e:
            self.logger.error(f"獲取對話列表失敗: {e}")
        
        return conversations
    
    async def _navigate_to_conversations(self):
        """導航到對話列表"""
        try:
            # 嘗試多種可能的對話列表URL
            possible_urls = [
                f"{self.config.manus_base_url}/conversations",
                f"{self.config.manus_base_url}/chats",
                f"{self.config.manus_base_url}/tasks",
                f"{self.config.manus_base_url}/dashboard"
            ]
            
            for url in possible_urls:
                try:
                    self.driver.get(url)
                    await asyncio.sleep(2)
                    
                    # 檢查是否成功加載對話列表
                    if self._has_conversation_list():
                        self.logger.debug(f"成功導航到對話列表: {url}")
                        return
                        
                except Exception:
                    continue
            
            # 如果都失敗，嘗試尋找對話列表鏈接
            await self._find_conversation_link()
            
        except Exception as e:
            self.logger.error(f"導航到對話列表失敗: {e}")
    
    def _has_conversation_list(self) -> bool:
        """檢查是否有對話列表"""
        try:
            list_indicators = [
                ".conversation-list",
                ".chat-list", 
                ".task-list",
                "[data-conversation-id]",
                ".conversation-item"
            ]
            
            for indicator in list_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements:
                        return True
                except:
                    continue
            
            return False
            
        except Exception:
            return False
    
    async def _find_conversation_link(self):
        """尋找對話列表鏈接"""
        try:
            link_texts = [
                "對話", "conversations", "chats", "tasks", 
                "消息", "messages", "聊天", "任務"
            ]
            
            for text in link_texts:
                try:
                    link = self.driver.find_element(
                        By.XPATH, 
                        f"//a[contains(text(), '{text}') or contains(@href, '{text}')]"
                    )
                    link.click()
                    await asyncio.sleep(2)
                    
                    if self._has_conversation_list():
                        self.logger.debug(f"通過鏈接找到對話列表: {text}")
                        return
                        
                except:
                    continue
            
            self.logger.warning("無法找到對話列表")
            
        except Exception as e:
            self.logger.error(f"尋找對話列表鏈接失敗: {e}")
    
    async def _scroll_to_load_all(self):
        """滾動加載所有對話"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # 滾動到底部
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
                
                # 檢查是否有新內容加載
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                    
                last_height = new_height
            
            # 滾動回頂部
            self.driver.execute_script("window.scrollTo(0, 0);")
            await asyncio.sleep(1)
            
        except Exception as e:
            self.logger.error(f"滾動加載失敗: {e}")
    
    async def _parse_conversation_element(self, element) -> Optional[ManusConversation]:
        """解析對話元素"""
        try:
            # 提取對話ID
            conv_id = self._extract_conversation_id(element)
            if not conv_id:
                return None
            
            # 提取基本信息
            title = self._extract_text(element, [
                ".conversation-title", ".chat-title", ".task-title", 
                ".title", "h3", "h4", ".subject"
            ]) or f"對話 {conv_id}"
            
            # 提取最後消息
            last_message = self._extract_text(element, [
                ".last-message", ".latest-message", ".preview", 
                ".content-preview", ".message-preview"
            ]) or ""
            
            # 提取時間
            last_message_time = self._extract_time(element) or datetime.now()
            
            # 提取狀態
            status = self._extract_status(element)
            
            # 提取用戶ID
            user_id = self._extract_user_id(element) or "unknown"
            
            # 獲取詳細消息（如果可能）
            recent_messages = await self._get_recent_messages(conv_id)
            
            return ManusConversation(
                conversation_id=conv_id,
                user_id=user_id,
                title=title,
                status=status,
                last_message=last_message,
                last_message_time=last_message_time,
                message_count=len(recent_messages),
                recent_messages=recent_messages,
                metadata={
                    'element_html': element.get_attribute('outerHTML')[:500],
                    'discovered_at': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"解析對話元素失敗: {e}")
            return None
    
    def _extract_conversation_id(self, element) -> Optional[str]:
        """提取對話ID"""
        try:
            # 嘗試從屬性中獲取
            for attr in ['data-conversation-id', 'data-chat-id', 'data-task-id', 'id']:
                conv_id = element.get_attribute(attr)
                if conv_id:
                    return conv_id
            
            # 嘗試從URL中獲取
            links = element.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute('href')
                if href:
                    # 從URL中提取ID
                    match = re.search(r'/(?:conversation|chat|task)/([^/?]+)', href)
                    if match:
                        return match.group(1)
            
            # 生成臨時ID
            return f"temp_{hash(element.get_attribute('outerHTML')) % 10000}"
            
        except Exception:
            return None
    
    def _extract_text(self, element, selectors: List[str]) -> Optional[str]:
        """提取文本內容"""
        try:
            for selector in selectors:
                try:
                    sub_element = element.find_element(By.CSS_SELECTOR, selector)
                    text = sub_element.text.strip()
                    if text:
                        return text
                except:
                    continue
            
            # 如果都沒找到，返回元素的文本
            return element.text.strip()[:200] if element.text else None
            
        except Exception:
            return None
    
    def _extract_time(self, element) -> Optional[datetime]:
        """提取時間"""
        try:
            time_selectors = [
                ".timestamp", ".time", ".date", ".last-updated",
                "[data-time]", "[datetime]", ".ago"
            ]
            
            for selector in time_selectors:
                try:
                    time_element = element.find_element(By.CSS_SELECTOR, selector)
                    
                    # 嘗試從屬性獲取
                    for attr in ['datetime', 'data-time', 'title']:
                        time_str = time_element.get_attribute(attr)
                        if time_str:
                            return self._parse_time_string(time_str)
                    
                    # 嘗試從文本獲取
                    time_text = time_element.text.strip()
                    if time_text:
                        return self._parse_time_string(time_text)
                        
                except:
                    continue
            
            return None
            
        except Exception:
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
            
            # 其他格式...
            return None
            
        except Exception:
            return None
    
    def _extract_status(self, element) -> str:
        """提取對話狀態"""
        try:
            # 檢查狀態指示器
            status_indicators = {
                'active': ['.active', '.online', '.responding'],
                'waiting': ['.waiting', '.pending', '.queue'],
                'stuck': ['.stuck', '.blocked', '.error'],
                'resolved': ['.resolved', '.completed', '.done'],
                'abandoned': ['.abandoned', '.closed', '.inactive']
            }
            
            for status, selectors in status_indicators.items():
                for selector in selectors:
                    try:
                        if element.find_elements(By.CSS_SELECTOR, selector):
                            return status
                    except:
                        continue
            
            # 根據最後活動時間判斷
            last_time = self._extract_time(element)
            if last_time:
                time_diff = (datetime.now() - last_time).total_seconds()
                if time_diff < 300:  # 5分鐘內
                    return 'active'
                elif time_diff < 3600:  # 1小時內
                    return 'waiting'
                else:
                    return 'stuck'
            
            return 'unknown'
            
        except Exception:
            return 'unknown'
    
    def _extract_user_id(self, element) -> Optional[str]:
        """提取用戶ID"""
        try:
            # 嘗試從屬性獲取
            for attr in ['data-user-id', 'data-user', 'data-customer-id']:
                user_id = element.get_attribute(attr)
                if user_id:
                    return user_id
            
            # 嘗試從用戶名元素獲取
            user_selectors = ['.username', '.user-name', '.customer-name', '.user']
            for selector in user_selectors:
                try:
                    user_element = element.find_element(By.CSS_SELECTOR, selector)
                    return user_element.text.strip()
                except:
                    continue
            
            return None
            
        except Exception:
            return None
    
    async def _get_recent_messages(self, conv_id: str) -> List[Dict[str, Any]]:
        """獲取最近的消息（簡化版本）"""
        try:
            # 這裡可以實現點擊進入對話詳情獲取消息的邏輯
            # 為了簡化，暫時返回空列表
            return []
            
        except Exception as e:
            self.logger.error(f"獲取對話 {conv_id} 的消息失敗: {e}")
            return []
    
    async def _update_conversation(self, conv: ManusConversation):
        """更新對話狀態"""
        try:
            old_conv = self.conversations.get(conv.conversation_id)
            
            # 檢查是否有變化
            if old_conv:
                if (old_conv.last_message != conv.last_message or 
                    old_conv.status != conv.status):
                    self.logger.info(f"對話 {conv.conversation_id} 狀態更新: {old_conv.status} -> {conv.status}")
            
            # 更新對話
            self.conversations[conv.conversation_id] = conv
            
        except Exception as e:
            self.logger.error(f"更新對話狀態失敗: {e}")
    
    def _update_stats(self, conversations: List[ManusConversation]):
        """更新統計信息"""
        self.stats['total_conversations'] = len(conversations)
        self.stats['active_conversations'] = len([c for c in conversations if c.status == 'active'])
        self.stats['last_update'] = datetime.now()
    
    async def _cleanup(self):
        """清理資源"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
            
            if self.session:
                await self.session.close()
                self.session = None
                
        except Exception as e:
            self.logger.error(f"清理資源失敗: {e}")
    
    def get_conversations(self) -> Dict[str, ManusConversation]:
        """獲取所有對話"""
        return self.conversations.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取監控統計"""
        return self.stats.copy()

