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
    
    def check_repository_exists(self, repo_name: str) -> bool:
        """检查Manus项目中是否存在指定仓库"""
        try:
            self.logger.info(f"🔍 检查仓库是否存在: {repo_name}")
            
            # 方法1: 通过项目文件列表检查
            project_data = self.get_project_data()
            if project_data and 'files' in project_data:
                for file_info in project_data['files']:
                    file_path = file_info.get('path', '')
                    if repo_name in file_path or repo_name.split('/')[-1] in file_path:
                        self.logger.info(f"✅ 在项目文件中找到仓库: {file_path}")
                        return True
            
            # 方法2: 通过对话历史检查git相关操作
            conversations = self._extract_conversations()
            for conv in conversations:
                content = conv.get('content', '')
                if 'git clone' in content and repo_name in content:
                    self.logger.info(f"✅ 在对话历史中找到git clone记录")
                    return True
                if 'git pull' in content and repo_name in content:
                    self.logger.info(f"✅ 在对话历史中找到git pull记录")
                    return True
            
            # 方法3: 检查是否有相关的仓库目录结构
            if project_data and 'files' in project_data:
                repo_indicators = ['.git', 'README.md', 'package.json', 'requirements.txt']
                for file_info in project_data['files']:
                    file_path = file_info.get('path', '')
                    for indicator in repo_indicators:
                        if indicator in file_path and repo_name.split('/')[-1] in file_path:
                            self.logger.info(f"✅ 找到仓库指示文件: {file_path}")
                            return True
            
            self.logger.info(f"❌ 未找到仓库: {repo_name}")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ 检查仓库存在性失败: {e}")
            return False  # 默认假设不存在，触发clone
    
    def get_repository_status(self, repo_name: str) -> dict:
        """获取仓库状态信息"""
        try:
            exists = self.check_repository_exists(repo_name)
            
            status = {
                'repository_name': repo_name,
                'exists_in_manus': exists,
                'recommended_action': 'git_pull' if exists else 'git_clone',
                'check_time': datetime.now().isoformat()
            }
            
            if exists:
                # 如果仓库存在，尝试获取更多信息
                project_data = self.get_project_data()
                if project_data and 'files' in project_data:
                    repo_files = [f for f in project_data['files'] 
                                if repo_name.split('/')[-1] in f.get('path', '')]
                    status['file_count_in_manus'] = len(repo_files)
                    status['last_modified'] = max([f.get('modified', '') for f in repo_files], default='')
            
            return status
            
        except Exception as e:
            self.logger.error(f"❌ 获取仓库状态失败: {e}")
            return {
                'repository_name': repo_name,
                'exists_in_manus': False,
                'recommended_action': 'git_clone',
                'error': str(e),
                'check_time': datetime.now().isoformat()
            }

    async def send_message_to_latest_task(self, message: str) -> dict:
        """
        真实发送消息到Manus平台的最新任务
        通过任务列表找到最新任务，在右边栏位对话框发送query
        """
        try:
            self.logger.info(f"🚀 开始真实发送消息到Manus: {message[:50]}...")
            
            # 1. 确保已登录并在项目页面
            if not await self.navigate_to_project():
                return {
                    'success': False,
                    'error': '无法导航到项目页面',
                    'message': message
                }
            
            # 2. 获取最新任务
            latest_task = await self._get_latest_task()
            if not latest_task:
                return {
                    'success': False,
                    'error': '未找到可用的任务',
                    'message': message
                }
            
            self.logger.info(f"📋 找到最新任务: {latest_task.get('title', 'Unknown')}")
            
            # 3. 导航到任务页面
            task_success = await self._navigate_to_task(latest_task)
            if not task_success:
                return {
                    'success': False,
                    'error': '无法导航到任务页面',
                    'task': latest_task,
                    'message': message
                }
            
            # 4. 在右边栏位对话框发送消息
            send_success = await self._send_message_in_chat(message)
            if not send_success:
                return {
                    'success': False,
                    'error': '无法在对话框中发送消息',
                    'task': latest_task,
                    'message': message
                }
            
            self.logger.info(f"✅ 消息已成功发送到Manus任务: {latest_task.get('title', 'Unknown')}")
            
            return {
                'success': True,
                'task': latest_task,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'status': '消息已发送到Manus平台'
            }
            
        except Exception as e:
            self.logger.error(f"❌ 发送消息到Manus失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': message
            }
    
    async def _get_latest_task(self) -> dict:
        """获取最新的任务"""
        try:
            # 等待任务列表加载
            await self.page.wait_for_timeout(2000)
            
            # 查找任务列表容器
            task_selectors = [
                '.task-list .task-item:first-child',
                '[data-testid="task-item"]:first-child',
                '.task-container .task:first-child',
                '.tasks .task:first-child',
                'li[class*="task"]:first-child',
                '.list-item:first-child'
            ]
            
            latest_task_element = None
            for selector in task_selectors:
                try:
                    latest_task_element = await self.page.query_selector(selector)
                    if latest_task_element:
                        self.logger.info(f"✅ 使用选择器找到任务: {selector}")
                        break
                except:
                    continue
            
            if not latest_task_element:
                self.logger.warning("⚠️ 未找到任务元素，尝试通过文本查找")
                # 尝试通过文本内容查找
                all_elements = await self.page.query_selector_all('*')
                for element in all_elements[:50]:  # 限制检查前50个元素
                    try:
                        text = await element.text_content()
                        if text and any(keyword in text.lower() for keyword in ['task', '任务', 'project', '项目']):
                            latest_task_element = element
                            break
                    except:
                        continue
            
            if latest_task_element:
                # 提取任务信息
                task_title = await latest_task_element.text_content() or "Unknown Task"
                task_href = await latest_task_element.get_attribute('href')
                
                return {
                    'title': task_title.strip(),
                    'element': latest_task_element,
                    'href': task_href,
                    'found_method': 'element_search'
                }
            
            # 如果还是没找到，返回默认任务信息
            self.logger.warning("⚠️ 未找到具体任务，使用当前页面作为任务")
            return {
                'title': 'Current Page Task',
                'element': None,
                'href': None,
                'found_method': 'current_page'
            }
            
        except Exception as e:
            self.logger.error(f"❌ 获取最新任务失败: {e}")
            return None
    
    async def _navigate_to_task(self, task: dict) -> bool:
        """导航到指定任务页面"""
        try:
            if task.get('element') and task.get('href'):
                # 如果有链接，点击导航
                await task['element'].click()
                await self.page.wait_for_timeout(3000)
                self.logger.info(f"✅ 已导航到任务: {task['title']}")
                return True
            elif task.get('element'):
                # 如果有元素但没有链接，尝试点击
                await task['element'].click()
                await self.page.wait_for_timeout(3000)
                self.logger.info(f"✅ 已点击任务元素: {task['title']}")
                return True
            else:
                # 如果是当前页面，直接返回成功
                self.logger.info("✅ 使用当前页面作为任务页面")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ 导航到任务失败: {e}")
            return False
    
    async def _send_message_in_chat(self, message: str) -> bool:
        """在右边栏位对话框中发送消息"""
        try:
            # 等待页面加载
            await self.page.wait_for_timeout(2000)
            
            # 查找对话框输入框的多种可能选择器
            chat_input_selectors = [
                'textarea[placeholder*="输入"]',
                'textarea[placeholder*="消息"]',
                'textarea[placeholder*="message"]',
                'input[placeholder*="输入"]',
                'input[placeholder*="消息"]',
                'input[placeholder*="message"]',
                '.chat-input textarea',
                '.message-input textarea',
                '.input-box textarea',
                '[data-testid="chat-input"]',
                '[data-testid="message-input"]',
                '.chat-container textarea',
                '.conversation textarea',
                'div[contenteditable="true"]',
                '.editable-div',
                '#chat-input',
                '#message-input'
            ]
            
            chat_input = None
            used_selector = None
            
            for selector in chat_input_selectors:
                try:
                    chat_input = await self.page.query_selector(selector)
                    if chat_input:
                        # 检查元素是否可见和可用
                        is_visible = await chat_input.is_visible()
                        is_enabled = await chat_input.is_enabled()
                        if is_visible and is_enabled:
                            used_selector = selector
                            self.logger.info(f"✅ 找到对话框输入框: {selector}")
                            break
                        else:
                            chat_input = None
                except:
                    continue
            
            if not chat_input:
                self.logger.warning("⚠️ 未找到对话框输入框，尝试查找发送按钮附近的输入框")
                # 尝试通过发送按钮找到输入框
                send_buttons = await self.page.query_selector_all('button')
                for button in send_buttons:
                    try:
                        button_text = await button.text_content()
                        if button_text and any(keyword in button_text.lower() for keyword in ['send', '发送', 'submit', '提交']):
                            # 在发送按钮附近查找输入框
                            parent = await button.query_selector('xpath=..')
                            if parent:
                                nearby_input = await parent.query_selector('textarea, input[type="text"], div[contenteditable="true"]')
                                if nearby_input:
                                    chat_input = nearby_input
                                    used_selector = "near_send_button"
                                    break
                    except:
                        continue
            
            if not chat_input:
                self.logger.error("❌ 无法找到对话框输入框")
                return False
            
            # 清空输入框并输入消息
            await chat_input.click()
            await chat_input.fill('')
            await self.page.wait_for_timeout(500)
            await chat_input.type(message)
            await self.page.wait_for_timeout(1000)
            
            self.logger.info(f"✅ 已在输入框中输入消息 (使用选择器: {used_selector})")
            
            # 查找并点击发送按钮
            send_button_selectors = [
                'button[type="submit"]',
                'button:has-text("发送")',
                'button:has-text("Send")',
                'button:has-text("提交")',
                'button:has-text("Submit")',
                '.send-button',
                '.submit-button',
                '[data-testid="send-button"]',
                '[data-testid="submit-button"]',
                'button[aria-label*="发送"]',
                'button[aria-label*="send"]'
            ]
            
            send_button = None
            for selector in send_button_selectors:
                try:
                    send_button = await self.page.query_selector(selector)
                    if send_button:
                        is_visible = await send_button.is_visible()
                        is_enabled = await send_button.is_enabled()
                        if is_visible and is_enabled:
                            self.logger.info(f"✅ 找到发送按钮: {selector}")
                            break
                        else:
                            send_button = None
                except:
                    continue
            
            if send_button:
                await send_button.click()
                self.logger.info("✅ 已点击发送按钮")
            else:
                # 如果没找到发送按钮，尝试按Enter键
                await chat_input.press('Enter')
                self.logger.info("✅ 已按Enter键发送消息")
            
            # 等待消息发送完成
            await self.page.wait_for_timeout(2000)
            
            self.logger.info(f"✅ 消息已成功发送: {message[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 在对话框中发送消息失败: {e}")
            return False

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

