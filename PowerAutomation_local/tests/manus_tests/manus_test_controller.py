"""
PowerAutomation Manus 測試控制器
集成MCP錄製和Replay分析功能
"""

import asyncio
import json
import logging
import time
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import traceback

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/manus_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ManusCredentials:
    """Manus登錄憑證"""
    email: str = "chuang.hsiaoyen@gmail.com"
    password: str = "silentfleet#1234"

@dataclass
class ManusConfig:
    """Manus配置"""
    url: str = "https://manus.im/app/uuX3KzwzsthCSgqmbQbgOz"
    login_timeout: int = 30000  # 30秒
    page_timeout: int = 60000   # 60秒
    headless: bool = False      # 設為False以便錄屏
    slow_mo: int = 1000        # 操作間隔1秒

@dataclass
class TestStep:
    """測試步驟記錄"""
    step_id: str
    description: str
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    data_extracted: Optional[Dict] = None
    performance_metrics: Optional[Dict] = None

@dataclass
class TestSession:
    """測試會話記錄"""
    session_id: str
    session_name: str
    workflow_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    steps: List[TestStep] = None
    success_rate: float = 0.0
    total_duration: float = 0.0
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []

class MCPRecorder:
    """MCP錄製器"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.recording_dir = f"/home/ubuntu/recordings/{session_id}"
        self.is_recording = False
        self.current_session: Optional[TestSession] = None
        
        # 創建錄製目錄
        os.makedirs(self.recording_dir, exist_ok=True)
        
    def start_recording(self, session_name: str, workflow_type: str) -> TestSession:
        """開始錄製"""
        self.current_session = TestSession(
            session_id=self.session_id,
            session_name=session_name,
            workflow_type=workflow_type,
            start_time=datetime.now()
        )
        self.is_recording = True
        logger.info(f"開始錄製會話: {session_name}")
        return self.current_session
    
    def record_step(self, step: TestStep) -> None:
        """記錄測試步驟"""
        if not self.is_recording or not self.current_session:
            return
            
        self.current_session.steps.append(step)
        logger.info(f"記錄步驟: {step.step_id} - {step.description}")
        
        # 保存步驟數據
        step_file = os.path.join(self.recording_dir, f"step_{step.step_id}.json")
        with open(step_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(step), f, ensure_ascii=False, indent=2, default=str)
    
    def stop_recording(self) -> TestSession:
        """停止錄製"""
        if not self.current_session:
            return None
            
        self.current_session.end_time = datetime.now()
        self.current_session.total_duration = (
            self.current_session.end_time - self.current_session.start_time
        ).total_seconds()
        
        # 計算成功率
        if self.current_session.steps:
            successful_steps = sum(1 for step in self.current_session.steps if step.success)
            self.current_session.success_rate = successful_steps / len(self.current_session.steps)
        
        self.is_recording = False
        
        # 保存完整會話數據
        session_file = os.path.join(self.recording_dir, "session.json")
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.current_session), f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"錄製完成: {self.current_session.session_name}")
        return self.current_session

class ManusTestController:
    """Manus測試控制器"""
    
    def __init__(self, config: Optional[ManusConfig] = None, 
                 credentials: Optional[ManusCredentials] = None):
        """初始化控制器"""
        self.config = config or ManusConfig()
        self.credentials = credentials or ManusCredentials()
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_logged_in = False
        self.recorder: Optional[MCPRecorder] = None
        
    async def start(self, session_id: str = None):
        """啟動瀏覽器和錄製器"""
        try:
            if not session_id:
                session_id = f"manus_test_{int(time.time())}"
                
            # 初始化錄製器
            self.recorder = MCPRecorder(session_id)
            
            # 啟動Playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.headless,
                slow_mo=self.config.slow_mo
            )
            
            # 創建瀏覽器上下文
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # 創建頁面
            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.config.page_timeout)
            
            logger.info("瀏覽器啟動成功")
            return True
            
        except Exception as e:
            logger.error(f"啟動瀏覽器失敗: {e}")
            return False
    
    async def stop(self):
        """停止瀏覽器"""
        try:
            if self.recorder and self.recorder.is_recording:
                self.recorder.stop_recording()
                
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
                
            logger.info("瀏覽器已關閉")
            
        except Exception as e:
            logger.error(f"關閉瀏覽器失敗: {e}")
    
    async def take_screenshot(self, name: str) -> str:
        """截圖"""
        if not self.page:
            return None
            
        screenshot_path = f"/home/ubuntu/screenshots/{name}_{int(time.time())}.png"
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        
        await self.page.screenshot(path=screenshot_path, full_page=True)
        return screenshot_path
    
    async def execute_test_case(self, test_case_name: str, test_function) -> TestSession:
        """執行測試案例"""
        session = self.recorder.start_recording(test_case_name, "manus_automation")
        
        try:
            await test_function()
            logger.info(f"測試案例 {test_case_name} 執行完成")
            
        except Exception as e:
            logger.error(f"測試案例 {test_case_name} 執行失敗: {e}")
            
        finally:
            return self.recorder.stop_recording()

# 測試案例實現
class ManusTestCases:
    """Manus測試案例集合"""
    
    def __init__(self, controller: ManusTestController):
        self.controller = controller
        self.recorder = controller.recorder
        
    async def tc001_login_test(self):
        """TC001: 登錄驗證測試"""
        step = TestStep(
            step_id="TC001_001",
            description="導航到Manus登錄頁面",
            start_time=datetime.now()
        )
        
        try:
            # 導航到Manus頁面
            await self.controller.page.goto(self.controller.config.url)
            await self.controller.page.wait_for_load_state('networkidle')
            
            # 截圖
            screenshot_path = await self.controller.take_screenshot("login_page")
            step.screenshot_path = screenshot_path
            
            step.end_time = datetime.now()
            step.success = True
            
        except Exception as e:
            step.end_time = datetime.now()
            step.success = False
            step.error_message = str(e)
            logger.error(f"登錄測試失敗: {e}")
            
        finally:
            self.recorder.record_step(step)
    
    async def tc002_send_message_test(self):
        """TC002: 信息發送功能測試"""
        test_messages = [
            "🧪 PowerAutomation 測試信息 - 基本文本發送測試",
            "測試特殊字符：@#$%^&*()_+-=[]{}|;':\",./<>?",
            "😀🎉🚀 PowerAutomation 功能測試 ✅📊💡"
        ]
        
        for i, message in enumerate(test_messages):
            step = TestStep(
                step_id=f"TC002_{i+1:03d}",
                description=f"發送測試信息: {message[:30]}...",
                start_time=datetime.now()
            )
            
            try:
                # 查找輸入框
                input_selector = 'textarea, input[type="text"], [contenteditable="true"]'
                await self.controller.page.wait_for_selector(input_selector, timeout=10000)
                
                # 輸入信息
                await self.controller.page.fill(input_selector, message)
                
                # 發送信息（按Enter或點擊發送按鈕）
                await self.controller.page.keyboard.press('Enter')
                
                # 等待信息發送完成
                await self.controller.page.wait_for_timeout(2000)
                
                step.end_time = datetime.now()
                step.success = True
                step.data_extracted = {"message": message, "length": len(message)}
                
            except Exception as e:
                step.end_time = datetime.now()
                step.success = False
                step.error_message = str(e)
                logger.error(f"發送信息失敗: {e}")
                
            finally:
                self.recorder.record_step(step)

if __name__ == "__main__":
    async def main():
        controller = ManusTestController()
        
        try:
            # 啟動測試環境
            await controller.start("manus_comprehensive_test")
            
            # 創建測試案例
            test_cases = ManusTestCases(controller)
            
            # 執行登錄測試
            await controller.execute_test_case("登錄驗證測試", test_cases.tc001_login_test)
            
            # 執行信息發送測試
            await controller.execute_test_case("信息發送測試", test_cases.tc002_send_message_test)
            
        finally:
            await controller.stop()
    
    # 運行測試
    asyncio.run(main())

