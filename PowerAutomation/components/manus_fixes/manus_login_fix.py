"""
修复后的Manus登录代码
基于实际观察到的页面结构
"""

async def login_fixed(self) -> bool:
    """修复后的登录到Manus平台方法"""
    try:
        if self.authenticated:
            return True
        
        self.logger.info("🔐 开始登录 Manus 平台")
        
        # 1. 导航到登录页面
        await self.page.goto('https://manus.im/login?type=signIn')
        await self.page.wait_for_load_state('networkidle')
        
        # 2. 点击"Continue with email"按钮
        continue_email_selectors = [
            'button:has-text("Continue with email")',
            'button[class*="Continue with email"]',
            'button:contains("Continue with email")'
        ]
        
        email_button_clicked = False
        for selector in continue_email_selectors:
            try:
                email_button = await self.page.query_selector(selector)
                if email_button:
                    await email_button.click()
                    await self.page.wait_for_timeout(2000)
                    email_button_clicked = True
                    self.logger.info("✅ 已点击Continue with email按钮")
                    break
            except:
                continue
        
        if not email_button_clicked:
            self.logger.error("❌ 无法找到Continue with email按钮")
            return False
        
        # 3. 等待邮箱输入框出现并填写
        email_selectors = [
            'input[placeholder="mail@domain.com"]',
            'input[type="email"]',
            'input[name="email"]',
            'label:has-text("Email") + input',
            'input:near(label:has-text("Email"))'
        ]
        
        email_input = None
        for selector in email_selectors:
            try:
                email_input = await self.page.query_selector(selector)
                if email_input:
                    is_visible = await email_input.is_visible()
                    is_enabled = await email_input.is_enabled()
                    if is_visible and is_enabled:
                        self.logger.info(f"✅ 找到邮箱输入框: {selector}")
                        break
                    else:
                        email_input = None
            except:
                continue
        
        if not email_input:
            self.logger.error("❌ 无法找到邮箱输入框")
            return False
        
        # 4. 填写邮箱
        await email_input.click()
        await email_input.fill('')
        await email_input.type(self.login_email)
        await self.page.wait_for_timeout(1000)
        self.logger.info(f"✅ 已填写邮箱: {self.login_email}")
        
        # 5. 查找并填写密码
        password_selectors = [
            'input[placeholder="Enter password"]',
            'input[type="password"]',
            'input[name="password"]',
            'label:has-text("Password") + input',
            'input:near(label:has-text("Password"))'
        ]
        
        password_input = None
        for selector in password_selectors:
            try:
                password_input = await self.page.query_selector(selector)
                if password_input:
                    is_visible = await password_input.is_visible()
                    is_enabled = await password_input.is_enabled()
                    if is_visible and is_enabled:
                        self.logger.info(f"✅ 找到密码输入框: {selector}")
                        break
                    else:
                        password_input = None
            except:
                continue
        
        if not password_input:
            self.logger.error("❌ 无法找到密码输入框")
            return False
        
        # 6. 填写密码
        await password_input.click()
        await password_input.fill('')
        await password_input.type(self.login_password)
        await self.page.wait_for_timeout(1000)
        self.logger.info("✅ 已填写密码")
        
        # 7. 查找并点击登录按钮
        login_button_selectors = [
            'button:has-text("Sign in")',
            'button[type="submit"]',
            'button:contains("Sign in")',
            'input[type="submit"]'
        ]
        
        login_button = None
        for selector in login_button_selectors:
            try:
                login_button = await self.page.query_selector(selector)
                if login_button:
                    is_visible = await login_button.is_visible()
                    is_enabled = await login_button.is_enabled()
                    if is_visible and is_enabled:
                        self.logger.info(f"✅ 找到登录按钮: {selector}")
                        break
                    else:
                        login_button = None
            except:
                continue
        
        if not login_button:
            self.logger.error("❌ 无法找到登录按钮")
            return False
        
        # 8. 点击登录按钮
        await login_button.click()
        self.logger.info("✅ 已点击登录按钮")
        
        # 9. 等待登录完成
        try:
            # 等待页面跳转或加载
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            # 检查是否登录成功
            current_url = self.page.url
            self.logger.info(f"🔍 当前URL: {current_url}")
            
            # 检查登录成功的标志
            success_indicators = [
                '/app' in current_url,
                '/dashboard' in current_url,
                '/workspace' in current_url
            ]
            
            if any(success_indicators):
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
                # 检查是否有错误消息
                error_selectors = [
                    '.error',
                    '.alert',
                    '[role="alert"]',
                    '.notification'
                ]
                
                error_message = ""
                for selector in error_selectors:
                    try:
                        error_element = await self.page.query_selector(selector)
                        if error_element:
                            error_text = await error_element.text_content()
                            if error_text and error_text.strip():
                                error_message = error_text.strip()
                                break
                    except:
                        continue
                
                if error_message:
                    self.logger.error(f"❌ 登录失败: {error_message}")
                else:
                    self.logger.error("❌ 登录失败 - 未跳转到应用页面")
                
                return False
                
        except Exception as e:
            self.logger.error(f"❌ 等待登录完成时出错: {e}")
            return False
            
    except Exception as e:
        self.logger.error(f"❌ Manus 登录过程失败: {e}")
        return False


async def navigate_to_project_fixed(self, project_id: str = None) -> bool:
    """修复后的导航到指定项目方法"""
    try:
        if not self.authenticated:
            login_success = await self.login_fixed()
            if not login_success:
                return False
        
        # 使用提供的项目ID或默认项目ID
        target_project_id = project_id or self.project_id
        project_url = f"https://manus.im/app/{target_project_id}"
        
        self.logger.info(f"🔗 导航到项目: {project_url}")
        
        # 导航到项目页面
        await self.page.goto(project_url)
        await self.page.wait_for_load_state('networkidle')
        
        # 检查是否成功访问项目
        current_url = self.page.url
        if target_project_id in current_url:
            self.logger.info(f"✅ 成功导航到项目: {target_project_id}")
            return True
        else:
            self.logger.error(f"❌ 导航到项目失败: {current_url}")
            return False
            
    except Exception as e:
        self.logger.error(f"❌ 导航到项目失败: {e}")
        return False


# 修复后的完整登录流程
async def complete_login_flow(manus_connector, target_project_id: str = None):
    """完整的登录和项目访问流程"""
    try:
        # 1. 登录
        login_success = await manus_connector.login_fixed()
        if not login_success:
            return False, "登录失败"
        
        # 2. 导航到项目
        project_success = await manus_connector.navigate_to_project_fixed(target_project_id)
        if not project_success:
            return False, "项目访问失败"
        
        # 3. 验证页面结构
        page_title = await manus_connector.page.title()
        current_url = manus_connector.page.url
        
        return True, {
            'status': 'success',
            'page_title': page_title,
            'current_url': current_url,
            'project_id': target_project_id or manus_connector.project_id
        }
        
    except Exception as e:
        return False, f"完整流程失败: {str(e)}"


# 使用示例
"""
# 在ManusConnector类中替换原有的login方法
async def login(self) -> bool:
    return await self.login_fixed()

async def navigate_to_project(self) -> bool:
    return await self.navigate_to_project_fixed()
"""

