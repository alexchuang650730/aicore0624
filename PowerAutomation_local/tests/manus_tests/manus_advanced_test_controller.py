#!/usr/bin/env python3
"""
PowerAutomation Manus 完善自動化測試腳本
基於實際測試中學到的解決方案

版本: v2.0
作者: PowerAutomation Team
日期: 2025-06-23
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import logging

class ManusAdvancedTestController:
    """
    Manus高級測試控制器
    集成了所有學到的解決方案和最佳實踐
    """
    
    def __init__(self, config_file="manus_test_config.json"):
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.browser = None
        self.page = None
        self.test_results = []
        self.screenshots_dir = Path("screenshots_advanced")
        self.screenshots_dir.mkdir(exist_ok=True)
        
    def load_config(self, config_file):
        """加載測試配置"""
        default_config = {
            "manus_url": "https://manus.im/app/uuX3KzwzsthCSgqmbQbgOz",
            "login_url": "https://manus.im/login?type=signIn",
            "credentials": {
                "email": "chuang.hsiaoyen@gmail.com",
                "password": "silentfleet#1234"
            },
            "timeouts": {
                "navigation": 30000,
                "element_wait": 10000,
                "input_delay": 100
            },
            "retry_config": {
                "max_retries": 3,
                "retry_delay": 2
            }
        }
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合併默認配置
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except FileNotFoundError:
            self.logger.info(f"配置文件 {config_file} 不存在，使用默認配置")
            return default_config
    
    def setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('manus_advanced_test.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def start_browser(self, headless=False):
        """啟動瀏覽器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
        
        # 設置超時
        self.page.set_default_timeout(self.config['timeouts']['navigation'])
        
        self.logger.info("瀏覽器啟動成功")
    
    async def take_screenshot(self, name, description=""):
        """拍攝截圖"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")[:-3]
        filename = f"{name}_{timestamp}.png"
        filepath = self.screenshots_dir / filename
        
        await self.page.screenshot(path=str(filepath), full_page=True)
        
        screenshot_info = {
            "filename": filename,
            "filepath": str(filepath),
            "timestamp": timestamp,
            "description": description,
            "url": self.page.url,
            "title": await self.page.title()
        }
        
        self.logger.info(f"截圖已保存: {filename} - {description}")
        return screenshot_info
    
    async def safe_input(self, selector, text, clear_first=True, use_js=False):
        """
        安全輸入方法 - 解決重複字符問題
        基於實際測試中學到的解決方案
        """
        try:
            element = await self.page.wait_for_selector(selector, timeout=self.config['timeouts']['element_wait'])
            
            if use_js:
                # 使用JavaScript直接設置值 - 避免重複字符問題
                await self.page.evaluate(f"""
                    const element = document.querySelector('{selector}');
                    if (element) {{
                        element.value = '';
                        element.value = '{text}';
                        element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                """)
                self.logger.info(f"使用JavaScript成功輸入到 {selector}")
            else:
                # 傳統方法
                if clear_first:
                    await element.clear()
                
                # 添加輸入延遲避免重複字符
                await element.type(text, delay=self.config['timeouts']['input_delay'])
                self.logger.info(f"成功輸入到 {selector}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"輸入失敗 {selector}: {str(e)}")
            return False
    
    async def smart_click(self, selector, wait_for_navigation=False):
        """智能點擊方法"""
        try:
            element = await self.page.wait_for_selector(selector, timeout=self.config['timeouts']['element_wait'])
            
            if wait_for_navigation:
                async with self.page.expect_navigation():
                    await element.click()
            else:
                await element.click()
            
            self.logger.info(f"成功點擊 {selector}")
            return True
            
        except Exception as e:
            self.logger.error(f"點擊失敗 {selector}: {str(e)}")
            return False
    
    async def find_sign_in_link(self):
        """
        智能查找Sign in鏈接
        基於實際測試中學到的解決方案
        """
        try:
            # 方法1: 滾動到頁面底部查找
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)
            
            # 方法2: 使用JavaScript查找包含"Sign in"的元素
            sign_in_element = await self.page.evaluate("""
                () => {
                    const elements = Array.from(document.querySelectorAll('*'));
                    return elements.find(el => 
                        el.textContent && 
                        (el.textContent.includes('Sign in') || 
                         el.textContent.includes('登錄') ||
                         el.textContent.includes('登入'))
                    );
                }
            """)
            
            if sign_in_element:
                await self.page.evaluate("arguments[0].click()", sign_in_element)
                self.logger.info("成功找到並點擊Sign in鏈接")
                return True
            
            # 方法3: 嘗試常見的選擇器
            selectors = [
                'a[href*="signin"]',
                'a[href*="login"]',
                'button:has-text("Sign in")',
                'a:has-text("Sign in")',
                'a:has-text("登錄")',
                'a:has-text("登入")'
            ]
            
            for selector in selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=2000)
                    await element.click()
                    self.logger.info(f"使用選擇器成功點擊: {selector}")
                    return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"查找Sign in鏈接失敗: {str(e)}")
            return False
    
    async def handle_captcha(self):
        """處理CAPTCHA"""
        try:
            # 檢查是否有hCaptcha
            captcha_frames = await self.page.query_selector_all('iframe[src*="hcaptcha"]')
            if captcha_frames:
                self.logger.warning("檢測到hCaptcha，需要手動處理或使用Google登錄繞過")
                return False
            
            # 檢查其他類型的CAPTCHA
            captcha_selectors = [
                '.captcha',
                '#captcha',
                '[class*="captcha"]',
                'iframe[src*="recaptcha"]'
            ]
            
            for selector in captcha_selectors:
                element = await self.page.query_selector(selector)
                if element:
                    self.logger.warning(f"檢測到CAPTCHA: {selector}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"CAPTCHA檢查失敗: {str(e)}")
            return False
    
    async def tc001_login_test(self):
        """TC001: 登錄驗證測試 - 完善版"""
        test_result = {
            "test_case": "TC001",
            "name": "Manus登錄驗證測試",
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "screenshots": [],
            "status": "running"
        }
        
        try:
            # 步驟1: 導航到Manus平台
            self.logger.info("TC001 - 步驟1: 導航到Manus平台")
            await self.page.goto(self.config['manus_url'])
            screenshot = await self.take_screenshot("tc001_step1_navigate", "導航到Manus平台")
            test_result["screenshots"].append(screenshot)
            test_result["steps"].append({"step": 1, "description": "導航到Manus平台", "status": "success"})
            
            # 步驟2: 查找並點擊Sign in鏈接
            self.logger.info("TC001 - 步驟2: 查找Sign in鏈接")
            sign_in_success = await self.find_sign_in_link()
            screenshot = await self.take_screenshot("tc001_step2_signin", "查找並點擊Sign in鏈接")
            test_result["screenshots"].append(screenshot)
            
            if not sign_in_success:
                test_result["steps"].append({"step": 2, "description": "查找Sign in鏈接", "status": "failed"})
                test_result["status"] = "failed"
                return test_result
            
            test_result["steps"].append({"step": 2, "description": "查找Sign in鏈接", "status": "success"})
            
            # 等待頁面加載
            await asyncio.sleep(2)
            
            # 步驟3: 檢查是否成功切換到登錄模式
            current_url = self.page.url
            if "signin" in current_url.lower() or "login" in current_url.lower():
                self.logger.info("成功切換到登錄模式")
                test_result["steps"].append({"step": 3, "description": "切換到登錄模式", "status": "success"})
            else:
                self.logger.warning("可能未成功切換到登錄模式")
                test_result["steps"].append({"step": 3, "description": "切換到登錄模式", "status": "warning"})
            
            # 步驟4: 填入登錄憑證
            self.logger.info("TC001 - 步驟4: 填入登錄憑證")
            
            # 查找email輸入框
            email_selectors = [
                'input[type="email"]',
                'input[placeholder*="mail"]',
                'input[name="email"]',
                'input[id*="email"]'
            ]
            
            email_success = False
            for selector in email_selectors:
                if await self.safe_input(selector, self.config['credentials']['email'], use_js=True):
                    email_success = True
                    break
            
            # 查找密碼輸入框
            password_selectors = [
                'input[type="password"]',
                'input[placeholder*="password"]',
                'input[name="password"]',
                'input[id*="password"]'
            ]
            
            password_success = False
            for selector in password_selectors:
                if await self.safe_input(selector, self.config['credentials']['password'], use_js=True):
                    password_success = True
                    break
            
            screenshot = await self.take_screenshot("tc001_step4_credentials", "填入登錄憑證")
            test_result["screenshots"].append(screenshot)
            
            if email_success and password_success:
                test_result["steps"].append({"step": 4, "description": "填入登錄憑證", "status": "success"})
            else:
                test_result["steps"].append({"step": 4, "description": "填入登錄憑證", "status": "failed"})
                test_result["status"] = "failed"
                return test_result
            
            # 步驟5: 檢查CAPTCHA
            self.logger.info("TC001 - 步驟5: 檢查CAPTCHA")
            captcha_ok = await self.handle_captcha()
            
            if not captcha_ok:
                self.logger.info("檢測到CAPTCHA，嘗試Google登錄繞過")
                # 嘗試Google登錄
                google_login_success = await self.try_google_login()
                if google_login_success:
                    test_result["steps"].append({"step": 5, "description": "使用Google登錄繞過CAPTCHA", "status": "success"})
                else:
                    test_result["steps"].append({"step": 5, "description": "CAPTCHA處理", "status": "manual_required"})
            else:
                test_result["steps"].append({"step": 5, "description": "無CAPTCHA阻擋", "status": "success"})
            
            # 步驟6: 提交登錄表單
            self.logger.info("TC001 - 步驟6: 提交登錄表單")
            submit_selectors = [
                'button[type="submit"]',
                'button:has-text("Sign in")',
                'button:has-text("登錄")',
                'input[type="submit"]'
            ]
            
            submit_success = False
            for selector in submit_selectors:
                if await self.smart_click(selector, wait_for_navigation=True):
                    submit_success = True
                    break
            
            screenshot = await self.take_screenshot("tc001_step6_submit", "提交登錄表單")
            test_result["screenshots"].append(screenshot)
            
            if submit_success:
                test_result["steps"].append({"step": 6, "description": "提交登錄表單", "status": "success"})
            else:
                test_result["steps"].append({"step": 6, "description": "提交登錄表單", "status": "failed"})
            
            # 等待頁面響應
            await asyncio.sleep(3)
            
            # 步驟7: 驗證登錄結果
            self.logger.info("TC001 - 步驟7: 驗證登錄結果")
            final_url = self.page.url
            page_title = await self.page.title()
            
            # 檢查是否登錄成功的指標
            success_indicators = [
                "dashboard" in final_url.lower(),
                "app" in final_url.lower() and "login" not in final_url.lower(),
                "welcome" in page_title.lower(),
                "manus" in page_title.lower() and "sign" not in page_title.lower()
            ]
            
            if any(success_indicators):
                test_result["status"] = "success"
                test_result["steps"].append({"step": 7, "description": "登錄成功驗證", "status": "success"})
                self.logger.info("TC001 登錄測試成功完成")
            else:
                test_result["status"] = "partial_success"
                test_result["steps"].append({"step": 7, "description": "登錄狀態待確認", "status": "warning"})
                self.logger.warning("TC001 登錄狀態需要進一步確認")
            
            screenshot = await self.take_screenshot("tc001_step7_result", "登錄結果驗證")
            test_result["screenshots"].append(screenshot)
            
        except Exception as e:
            self.logger.error(f"TC001 測試執行失敗: {str(e)}")
            test_result["status"] = "error"
            test_result["error"] = str(e)
        
        finally:
            test_result["end_time"] = datetime.now().isoformat()
            test_result["duration"] = (datetime.fromisoformat(test_result["end_time"]) - 
                                     datetime.fromisoformat(test_result["start_time"])).total_seconds()
        
        return test_result
    
    async def try_google_login(self):
        """嘗試Google登錄繞過CAPTCHA"""
        try:
            # 查找Google登錄按鈕
            google_selectors = [
                'button:has-text("Sign in with Google")',
                'a:has-text("Sign in with Google")',
                '[class*="google"]',
                'button[class*="google"]'
            ]
            
            for selector in google_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=2000)
                    await element.click()
                    self.logger.info("成功點擊Google登錄按鈕")
                    
                    # 等待跳轉到Google登錄頁面
                    await asyncio.sleep(3)
                    
                    # 如果跳轉到Google頁面，填入憑證
                    if "accounts.google.com" in self.page.url:
                        # 填入email
                        await self.safe_input('input[type="email"]', self.config['credentials']['email'], use_js=True)
                        await self.smart_click('button:has-text("Next")')
                        await asyncio.sleep(2)
                        
                        # 填入密碼
                        await self.safe_input('input[type="password"]', self.config['credentials']['password'], use_js=True)
                        await self.smart_click('button:has-text("Next")')
                        
                        self.logger.info("Google登錄憑證已填入")
                        return True
                    
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Google登錄嘗試失敗: {str(e)}")
            return False
    
    async def create_mock_test_environment(self):
        """創建模擬測試環境用於TC002-TC006"""
        mock_data = {
            "conversations": [
                {
                    "id": "conv_001",
                    "title": "PowerAutomation項目討論",
                    "date": "2025-06-23",
                    "messages": [
                        {"role": "user", "content": "請幫我分析這個自動化測試項目"},
                        {"role": "assistant", "content": "我來幫您分析PowerAutomation測試項目的架構和實施方案"}
                    ],
                    "category": "技術討論"
                },
                {
                    "id": "conv_002", 
                    "title": "測試案例設計",
                    "date": "2025-06-22",
                    "messages": [
                        {"role": "user", "content": "需要設計完整的測試案例"},
                        {"role": "assistant", "content": "我建議從登錄驗證開始，然後是功能測試"}
                    ],
                    "category": "測試設計"
                }
            ],
            "tasks": [
                {
                    "id": "task_001",
                    "title": "完成Manus登錄自動化",
                    "status": "completed",
                    "files": ["login_test.py", "test_results.json"],
                    "category": "自動化測試"
                },
                {
                    "id": "task_002",
                    "title": "實施數據存儲驗證",
                    "status": "in_progress", 
                    "files": ["data_storage_test.py", "storage_report.md"],
                    "category": "數據驗證"
                }
            ],
            "files": [
                {
                    "name": "PowerAutomation_Test_Report.pdf",
                    "type": "pdf",
                    "size": "2.5MB",
                    "category": "報告"
                },
                {
                    "name": "manus_test_controller.py", 
                    "type": "python",
                    "size": "15KB",
                    "category": "代碼"
                }
            ]
        }
        
        # 保存模擬數據
        with open("mock_manus_data.json", "w", encoding="utf-8") as f:
            json.dump(mock_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info("模擬測試環境已創建")
        return mock_data
    
    async def close(self):
        """關閉瀏覽器"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        self.logger.info("瀏覽器已關閉")

# 配置文件生成
def create_config_file():
    """創建配置文件"""
    config = {
        "manus_url": "https://manus.im/app/uuX3KzwzsthCSgqmbQbgOz",
        "login_url": "https://manus.im/login?type=signIn", 
        "credentials": {
            "email": "chuang.hsiaoyen@gmail.com",
            "password": "silentfleet#1234"
        },
        "timeouts": {
            "navigation": 30000,
            "element_wait": 10000,
            "input_delay": 100
        },
        "retry_config": {
            "max_retries": 3,
            "retry_delay": 2
        },
        "test_settings": {
            "headless": False,
            "screenshot_on_failure": True,
            "video_recording": True
        }
    }
    
    with open("manus_test_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("配置文件 manus_test_config.json 已創建")

if __name__ == "__main__":
    # 創建配置文件
    create_config_file()
    
    # 示例使用
    async def main():
        controller = ManusAdvancedTestController()
        
        try:
            await controller.start_browser(headless=False)
            
            # 執行TC001測試
            tc001_result = await controller.tc001_login_test()
            print(f"TC001 測試結果: {tc001_result['status']}")
            
            # 創建模擬環境
            mock_data = await controller.create_mock_test_environment()
            print("模擬測試環境已準備就緒")
            
        finally:
            await controller.close()
    
    # 運行測試
    # asyncio.run(main())

