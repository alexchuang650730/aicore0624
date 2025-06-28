"""
Manus连接器 - 负责与Manus平台的连接和数据获取
整合自原有的smartinvention_mcp组件
"""

import asyncio
import json
import logging
import os
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import aiofiles
from playwright.async_api import async_playwright, Browser, Page
import re

class ManusConnector:
    """Manus平台连接管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.authenticated = False
        self.session_data = {}
        self.initialized = False
        
        # 从环境变量获取敏感信息
        self.login_email = os.getenv('MANUS_LOGIN_EMAIL', config.get('login_email', ''))
        self.login_password = os.getenv('MANUS_LOGIN_PASSWORD', config.get('login_password', ''))
        self.project_id = os.getenv('MANUS_PROJECT_ID', config.get('project_id', ''))
        
    async def initialize(self):
        """初始化连接器"""
        try:
            self.logger.info("🔗 初始化 Manus 连接器")
            
            # 验证配置
            if not self.login_email or not self.login_password:
                raise ValueError("Manus 登录凭据未配置")
            
            if not self.project_id:
                raise ValueError("Manus 项目ID未配置")
            
            # 启动浏览器
            await self._start_browser()
            
            # 执行登录
            if self.config.get('auto_login', True):
                await self.login()
            
            self.initialized = True
            self.logger.info("✅ Manus 连接器初始化完成")
            
        except Exception as e:
            self.logger.error(f"❌ Manus 连接器初始化失败: {e}")
            raise
    
    async def _start_browser(self):
        """启动浏览器实例"""
        try:
            playwright = await async_playwright().start()
            
            browser_settings = self.config.get('browser_settings', {})
            
            self.browser = await playwright.chromium.launch(
                headless=browser_settings.get('headless', True),
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            context = await self.browser.new_context(
                user_agent=browser_settings.get('user_agent', ''),
                viewport=browser_settings.get('viewport', {'width': 1920, 'height': 1080})
            )
            
            self.page = await context.new_page()
            
            # 设置超时
            self.page.set_default_timeout(browser_settings.get('timeout', 30000))
            
            self.logger.info("🌐 浏览器实例启动成功")
            
        except Exception as e:
            self.logger.error(f"❌ 浏览器启动失败: {e}")
            raise
    
    async def login(self) -> bool:
        """登录到Manus平台"""
        try:
            if self.authenticated:
                return True
            
            self.logger.info("🔐 开始登录 Manus 平台")
            
            # 导航到登录页面
            await self.page.goto(self.config.get('base_url', 'https://manus.im'))
            
            # 等待页面加载
            await self.page.wait_for_load_state('networkidle')
            
            # 查找并填写登录表单
            email_selector = 'input[type="email"], input[name="email"], #email'
            password_selector = 'input[type="password"], input[name="password"], #password'
            login_button_selector = 'button[type="submit"], input[type="submit"], .login-button'
            
            # 填写邮箱
            await self.page.fill(email_selector, self.login_email)
            await asyncio.sleep(0.5)
            
            # 填写密码
            await self.page.fill(password_selector, self.login_password)
            await asyncio.sleep(0.5)
            
            # 点击登录按钮
            await self.page.click(login_button_selector)
            
            # 等待登录完成
            await self.page.wait_for_load_state('networkidle')
            
            # 检查是否登录成功
            current_url = self.page.url
            if '/app' in current_url or '/dashboard' in current_url:
                self.authenticated = True
                self.logger.info("✅ Manus 登录成功")
                
                # 保存会话信息
                self.session_data = {
                    'login_time': datetime.now().isoformat(),
                    'current_url': current_url,
                    'cookies': await self.page.context.cookies()
                }
                
                return True
            else:
                self.logger.error("❌ Manus 登录失败 - 未跳转到应用页面")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Manus 登录过程失败: {e}")
            return False
    
    async def navigate_to_project(self) -> bool:
        """导航到指定项目"""
        try:
            if not self.authenticated:
                await self.login()
            
            project_url = f"{self.config.get('app_url', 'https://manus.im/app')}/{self.project_id}"
            
            self.logger.info(f"📂 导航到项目: {project_url}")
            
            await self.page.goto(project_url)
            await self.page.wait_for_load_state('networkidle')
            
            # 验证是否成功加载项目
            if self.project_id in self.page.url:
                self.logger.info("✅ 成功导航到项目页面")
                return True
            else:
                self.logger.error("❌ 项目页面导航失败")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ 项目导航失败: {e}")
            return False
    
    async def get_project_data(self) -> Dict[str, Any]:
        """获取项目的完整数据"""
        try:
            if not await self.navigate_to_project():
                raise Exception("无法访问项目页面")
            
            self.logger.info("📊 开始获取项目数据")
            
            # 获取项目基本信息
            project_info = await self._extract_project_info()
            
            # 获取任务列表
            tasks = await self._extract_tasks()
            
            # 获取对话列表
            conversations = await self._extract_conversations()
            
            # 获取文件列表
            files = await self._extract_files()
            
            project_data = {
                'project_info': project_info,
                'tasks': tasks,
                'conversations': conversations,
                'files': files,
                'extracted_at': datetime.now().isoformat(),
                'total_items': len(tasks) + len(conversations) + len(files)
            }
            
            self.logger.info(f"✅ 项目数据获取完成 - 总计 {project_data['total_items']} 项")
            
            return project_data
            
        except Exception as e:
            self.logger.error(f"❌ 项目数据获取失败: {e}")
            raise
    
    async def _extract_project_info(self) -> Dict[str, Any]:
        """提取项目基本信息"""
        try:
            # 等待页面元素加载
            await asyncio.sleep(2)
            
            # 提取项目标题
            title_selectors = ['h1', '.project-title', '.page-title', '[data-testid="project-title"]']
            title = ""
            for selector in title_selectors:
                try:
                    title_element = await self.page.query_selector(selector)
                    if title_element:
                        title = await title_element.text_content()
                        if title and title.strip():
                            break
                except:
                    continue
            
            # 提取项目描述
            description_selectors = ['.project-description', '.description', '[data-testid="project-description"]']
            description = ""
            for selector in description_selectors:
                try:
                    desc_element = await self.page.query_selector(selector)
                    if desc_element:
                        description = await desc_element.text_content()
                        if description and description.strip():
                            break
                except:
                    continue
            
            return {
                'id': self.project_id,
                'title': title.strip() if title else f"Project {self.project_id}",
                'description': description.strip() if description else "",
                'url': self.page.url,
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ 项目信息提取失败: {e}")
            return {
                'id': self.project_id,
                'title': f"Project {self.project_id}",
                'description': "",
                'url': self.page.url,
                'extracted_at': datetime.now().isoformat()
            }
    
    async def _extract_tasks(self) -> List[Dict[str, Any]]:
        """提取任务列表"""
        try:
            self.logger.info("📋 提取任务列表")
            
            tasks = []
            
            # 常见的任务选择器
            task_selectors = [
                '.task-item', '.task', '[data-testid="task"]',
                '.todo-item', '.issue', '.card'
            ]
            
            for selector in task_selectors:
                try:
                    task_elements = await self.page.query_selector_all(selector)
                    if task_elements:
                        for i, element in enumerate(task_elements[:self.config.get('data_collection', {}).get('tasks_limit', 100)]):
                            try:
                                # 提取任务信息
                                title_elem = await element.query_selector('h1, h2, h3, h4, .title, .task-title')
                                title = await title_elem.text_content() if title_elem else f"Task {i+1}"
                                
                                desc_elem = await element.query_selector('.description, .content, .task-description')
                                description = await desc_elem.text_content() if desc_elem else ""
                                
                                status_elem = await element.query_selector('.status, .task-status, .state')
                                status = await status_elem.text_content() if status_elem else "unknown"
                                
                                tasks.append({
                                    'id': f"task_{i+1}",
                                    'title': title.strip() if title else "",
                                    'description': description.strip() if description else "",
                                    'status': status.strip() if status else "unknown",
                                    'type': 'task',
                                    'extracted_at': datetime.now().isoformat()
                                })
                                
                            except Exception as e:
                                self.logger.warning(f"⚠️ 任务 {i+1} 提取失败: {e}")
                                continue
                        
                        if tasks:
                            break
                            
                except Exception as e:
                    continue
            
            self.logger.info(f"✅ 提取到 {len(tasks)} 个任务")
            return tasks
            
        except Exception as e:
            self.logger.error(f"❌ 任务提取失败: {e}")
            return []
    
    async def _extract_conversations(self) -> List[Dict[str, Any]]:
        """提取对话列表"""
        try:
            self.logger.info("💬 提取对话列表")
            
            conversations = []
            
            # 常见的对话选择器
            conversation_selectors = [
                '.conversation', '.chat', '.message-thread',
                '.discussion', '.comment-thread', '[data-testid="conversation"]'
            ]
            
            for selector in conversation_selectors:
                try:
                    conv_elements = await self.page.query_selector_all(selector)
                    if conv_elements:
                        for i, element in enumerate(conv_elements[:self.config.get('data_collection', {}).get('conversations_limit', 50)]):
                            try:
                                # 提取对话信息
                                title_elem = await element.query_selector('h1, h2, h3, h4, .title, .conversation-title')
                                title = await title_elem.text_content() if title_elem else f"Conversation {i+1}"
                                
                                # 提取消息内容
                                message_elems = await element.query_selector_all('.message, .chat-message, .comment')
                                messages = []
                                
                                for msg_elem in message_elems[:10]:  # 限制每个对话最多10条消息
                                    try:
                                        content = await msg_elem.text_content()
                                        if content and content.strip():
                                            messages.append({
                                                'content': content.strip(),
                                                'timestamp': datetime.now().isoformat()
                                            })
                                    except:
                                        continue
                                
                                conversations.append({
                                    'id': f"conv_{i+1}",
                                    'title': title.strip() if title else "",
                                    'messages': messages,
                                    'message_count': len(messages),
                                    'type': 'conversation',
                                    'extracted_at': datetime.now().isoformat()
                                })
                                
                            except Exception as e:
                                self.logger.warning(f"⚠️ 对话 {i+1} 提取失败: {e}")
                                continue
                        
                        if conversations:
                            break
                            
                except Exception as e:
                    continue
            
            self.logger.info(f"✅ 提取到 {len(conversations)} 个对话")
            return conversations
            
        except Exception as e:
            self.logger.error(f"❌ 对话提取失败: {e}")
            return []
    
    async def _extract_files(self) -> List[Dict[str, Any]]:
        """提取文件列表"""
        try:
            self.logger.info("📁 提取文件列表")
            
            files = []
            
            # 常见的文件选择器
            file_selectors = [
                '.file-item', '.file', '.attachment',
                '.document', '[data-testid="file"]', 'a[href*="download"]'
            ]
            
            for selector in file_selectors:
                try:
                    file_elements = await self.page.query_selector_all(selector)
                    if file_elements:
                        for i, element in enumerate(file_elements):
                            try:
                                # 提取文件信息
                                name_elem = await element.query_selector('.filename, .file-name, .name')
                                if not name_elem:
                                    name_elem = element
                                
                                name = await name_elem.text_content() if name_elem else f"file_{i+1}"
                                
                                # 尝试获取下载链接
                                href = await element.get_attribute('href')
                                if not href:
                                    link_elem = await element.query_selector('a')
                                    href = await link_elem.get_attribute('href') if link_elem else ""
                                
                                # 提取文件大小
                                size_elem = await element.query_selector('.size, .file-size')
                                size = await size_elem.text_content() if size_elem else ""
                                
                                files.append({
                                    'id': f"file_{i+1}",
                                    'name': name.strip() if name else "",
                                    'url': href if href else "",
                                    'size': size.strip() if size else "",
                                    'type': 'file',
                                    'extracted_at': datetime.now().isoformat()
                                })
                                
                            except Exception as e:
                                self.logger.warning(f"⚠️ 文件 {i+1} 提取失败: {e}")
                                continue
                        
                        if files:
                            break
                            
                except Exception as e:
                    continue
            
            self.logger.info(f"✅ 提取到 {len(files)} 个文件")
            return files
            
        except Exception as e:
            self.logger.error(f"❌ 文件提取失败: {e}")
            return []
    
    async def download_file(self, file_info: Dict[str, Any]) -> Optional[str]:
        """下载指定文件"""
        try:
            if not file_info.get('url'):
                return None
            
            download_path = self.config.get('data_collection', {}).get('download_path', '/tmp/manus_downloads')
            os.makedirs(download_path, exist_ok=True)
            
            file_path = os.path.join(download_path, file_info.get('name', f"file_{datetime.now().timestamp()}"))
            
            # 使用页面下载文件
            async with self.page.expect_download() as download_info:
                await self.page.goto(file_info['url'])
            
            download = await download_info.value
            await download.save_as(file_path)
            
            self.logger.info(f"✅ 文件下载完成: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"❌ 文件下载失败: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            status = {
                'initialized': self.initialized,
                'authenticated': self.authenticated,
                'browser_active': self.browser is not None and self.browser.is_connected(),
                'page_active': self.page is not None,
                'project_id': self.project_id,
                'last_check': datetime.now().isoformat()
            }
            
            if self.authenticated and self.page:
                try:
                    current_url = self.page.url
                    status['current_url'] = current_url
                    status['project_accessible'] = self.project_id in current_url
                except:
                    status['current_url'] = None
                    status['project_accessible'] = False
            
            return status
            
        except Exception as e:
            return {
                'initialized': False,
                'authenticated': False,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.page:
                await self.page.close()
            
            if self.browser:
                await self.browser.close()
            
            self.logger.info("🧹 Manus 连接器资源清理完成")
            
        except Exception as e:
            self.logger.error(f"❌ 资源清理失败: {e}")
    
    def __del__(self):
        """析构函数"""
        if hasattr(self, 'browser') and self.browser:
            try:
                asyncio.create_task(self.cleanup())
            except:
                pass

