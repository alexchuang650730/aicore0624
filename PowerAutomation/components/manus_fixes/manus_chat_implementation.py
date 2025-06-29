"""
Manus对话框交互的完整实现
展示 _send_message_in_chat 和 _wait_for_ai_response 的具体实现
"""

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
        
        # 🔍 步骤1: 查找对话框输入框
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
        
        # 🔍 步骤2: 如果没找到，尝试通过发送按钮找输入框
        if not chat_input:
            self.logger.warning("⚠️ 未找到对话框输入框，尝试查找发送按钮附近的输入框")
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
        
        # 📝 步骤3: 清空输入框并输入消息
        await chat_input.click()
        await chat_input.fill('')  # 清空现有内容
        await self.page.wait_for_timeout(500)
        await chat_input.type(message)  # 逐字输入消息
        await self.page.wait_for_timeout(1000)
        
        self.logger.info(f"✅ 已在输入框中输入消息 (使用选择器: {used_selector})")
        
        # 🚀 步骤4: 查找并点击发送按钮
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
        
        # 🚀 步骤5: 发送消息
        if send_button:
            await send_button.click()
            self.logger.info("✅ 已点击发送按钮")
        else:
            # 如果没找到发送按钮，尝试按Enter键
            await chat_input.press('Enter')
            self.logger.info("✅ 已按Enter键发送消息")
        
        # ⏱️ 等待消息发送完成
        await self.page.wait_for_timeout(2000)
        
        self.logger.info(f"✅ 消息已成功发送: {message[:50]}...")
        return True
        
    except Exception as e:
        self.logger.error(f"❌ 在对话框中发送消息失败: {e}")
        return False


async def _wait_for_ai_response(self, timeout: int = 30000) -> str:
    """等待Manus AI的回应"""
    try:
        self.logger.info("⏳ 等待Manus AI回应...")
        
        # 记录发送消息前的消息数量
        initial_messages = await self._count_existing_messages()
        
        # 等待新消息出现
        start_time = time.time()
        max_wait_time = timeout / 1000  # 转换为秒
        
        while time.time() - start_time < max_wait_time:
            # 检查是否有新消息
            current_messages = await self._count_existing_messages()
            
            if current_messages > initial_messages:
                # 有新消息，获取最新的AI回应
                latest_response = await self._get_latest_ai_message()
                if latest_response and latest_response.strip():
                    self.logger.info(f"✅ 收到AI回应: {latest_response[:100]}...")
                    return latest_response
            
            # 等待一段时间再检查
            await self.page.wait_for_timeout(1000)
        
        # 超时
        self.logger.warning(f"⚠️ 等待AI回应超时 ({timeout/1000}秒)")
        return ""
        
    except Exception as e:
        self.logger.error(f"❌ 等待AI回应失败: {e}")
        return ""


async def _count_existing_messages(self) -> int:
    """计算当前对话中的消息数量"""
    try:
        message_selectors = [
            '.message',
            '.chat-message', 
            '.conversation-message',
            '[data-testid="message"]',
            '.msg',
            '.dialogue-item'
        ]
        
        for selector in message_selectors:
            try:
                messages = await self.page.query_selector_all(selector)
                if messages:
                    return len(messages)
            except:
                continue
                
        return 0
        
    except Exception as e:
        self.logger.error(f"❌ 计算消息数量失败: {e}")
        return 0


async def _get_latest_ai_message(self) -> str:
    """获取最新的AI回应消息"""
    try:
        # AI回应的可能选择器
        ai_response_selectors = [
            '.message.ai:last-child',
            '.message.assistant:last-child',
            '.chat-message.bot:last-child',
            '.response:last-child',
            '.ai-response:last-child',
            '.message:not(.user):last-child',
            '.message[data-role="assistant"]:last-child',
            '.conversation-message.ai:last-child'
        ]
        
        # 🔍 方法1: 通过AI特定选择器查找
        for selector in ai_response_selectors:
            try:
                response_element = await self.page.query_selector(selector)
                if response_element:
                    response_text = await response_element.text_content()
                    if response_text and response_text.strip():
                        return response_text.strip()
            except:
                continue
        
        # 🔍 方法2: 获取最后一条消息（假设是AI回应）
        general_message_selectors = [
            '.message:last-child',
            '.chat-message:last-child',
            '.conversation-message:last-child'
        ]
        
        for selector in general_message_selectors:
            try:
                response_element = await self.page.query_selector(selector)
                if response_element:
                    response_text = await response_element.text_content()
                    if response_text and response_text.strip():
                        # 简单检查是否是用户消息（通常用户消息较短）
                        if len(response_text.strip()) > 20:  # AI回应通常较长
                            return response_text.strip()
            except:
                continue
        
        # 🔍 方法3: 通过消息内容特征判断
        all_messages = await self.page.query_selector_all('.message, .chat-message')
        if all_messages and len(all_messages) > 0:
            # 获取最后一条消息
            last_message = all_messages[-1]
            message_text = await last_message.text_content()
            if message_text and message_text.strip():
                return message_text.strip()
        
        return ""
        
    except Exception as e:
        self.logger.error(f"❌ 获取最新AI消息失败: {e}")
        return ""


async def get_manus_response(self, query: str) -> str:
    """完整的获取Manus回应流程"""
    try:
        self.logger.info(f"🚀 开始获取Manus回应: {query}")
        
        # 1. 确保在正确的页面
        if not await self.navigate_to_project():
            return "无法访问Manus项目页面"
        
        # 2. 导航到最新任务
        latest_task = await self._get_latest_task()
        if not latest_task:
            return "未找到可用的任务"
            
        await self._navigate_to_task(latest_task)
        
        # 3. 发送消息到对话框
        send_success = await self._send_message_in_chat(query)
        if not send_success:
            return "无法发送消息到对话框"
        
        # 4. 等待并获取AI回应
        ai_response = await self._wait_for_ai_response()
        if not ai_response:
            return "未收到AI回应"
        
        self.logger.info(f"✅ 成功获取Manus回应")
        return ai_response
        
    except Exception as e:
        self.logger.error(f"❌ 获取Manus回应失败: {e}")
        return f"获取回应失败: {str(e)}"


# 使用示例
async def example_usage():
    """使用示例"""
    
    # 发送查询并获取完整回应
    query = "目前的倉的檔案數量是多少"
    
    # 🚀 发送消息
    success = await manus_connector._send_message_in_chat(query)
    if success:
        # ⏳ 等待AI回应
        response = await manus_connector._wait_for_ai_response()
        
        # 📋 直接返回完整回应，不需要解析
        return response  # 例如: "根据项目分析，当前包含12个文件，包括Python脚本、配置文件等..."
    
    return "发送失败"

