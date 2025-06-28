#!/usr/bin/env python3
"""
Human Loop MCP 集成適配器
極簡版本 - 只專注於與 Human Loop MCP 服務的集成

設計原則：
1. 不重複實現 AICore 已有的智能路由、專家系統、測試框架功能
2. 只提供與 Human Loop MCP 服務的集成接口
3. 利用 AICore 現有的決策和優化能力
4. 作為輕量級適配器集成到現有組件中
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InteractionType(Enum):
    """交互類型"""
    CONFIRMATION = "confirmation"
    SELECTION = "selection"
    INPUT = "input"
    FILE_UPLOAD = "file_upload"

class HumanLoopMCPClient:
    """Human Loop MCP 客戶端 - 極簡版本"""
    
    def __init__(self, mcp_url: str = "http://localhost:8096"):
        """
        初始化 Human Loop MCP 客戶端
        
        Args:
            mcp_url: Human Loop MCP 服務的 URL
        """
        self.mcp_url = mcp_url
        self.session_timeout = 300  # 5分鐘超時
        
    async def create_interaction_session(self, 
                                       interaction_data: Dict[str, Any],
                                       workflow_id: str = None,
                                       callback_url: str = None) -> Dict[str, Any]:
        """
        創建人機交互會話
        
        Args:
            interaction_data: 交互數據
            workflow_id: 工作流ID
            callback_url: 回調URL
            
        Returns:
            會話創建結果
        """
        try:
            session_data = {
                "interaction_data": interaction_data,
                "workflow_id": workflow_id or f"workflow_{int(datetime.now().timestamp())}",
                "callback_url": callback_url
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.mcp_url}/api/sessions",
                    json=session_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"成功創建交互會話: {result.get('session_id')}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"創建會話失敗: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            logger.error(f"創建交互會話時發生錯誤: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def wait_for_user_response(self, session_id: str, timeout: int = None) -> Dict[str, Any]:
        """
        等待用戶響應
        
        Args:
            session_id: 會話ID
            timeout: 超時時間（秒）
            
        Returns:
            用戶響應結果
        """
        timeout = timeout or self.session_timeout
        start_time = datetime.now()
        
        try:
            while True:
                # 檢查會話狀態
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.mcp_url}/api/sessions/{session_id}",
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            session_data = await response.json()
                            session_info = session_data.get("session", {})
                            status = session_info.get("status")
                            
                            if status == "completed":
                                logger.info(f"用戶已響應會話: {session_id}")
                                return {
                                    "success": True,
                                    "status": "completed",
                                    "response": session_info.get("response"),
                                    "session": session_info
                                }
                            elif status == "cancelled":
                                logger.info(f"會話已取消: {session_id}")
                                return {
                                    "success": False,
                                    "status": "cancelled",
                                    "reason": session_info.get("cancellation_reason", "用戶取消")
                                }
                            elif status == "timeout":
                                logger.info(f"會話已超時: {session_id}")
                                return {
                                    "success": False,
                                    "status": "timeout",
                                    "reason": "會話超時"
                                }
                        else:
                            logger.error(f"獲取會話狀態失敗: {response.status}")
                
                # 檢查是否超時
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed >= timeout:
                    logger.warning(f"等待用戶響應超時: {session_id}")
                    return {
                        "success": False,
                        "status": "timeout",
                        "reason": f"等待超時 ({timeout}秒)"
                    }
                
                # 等待5秒後重試
                await asyncio.sleep(5)
                
        except Exception as e:
            logger.error(f"等待用戶響應時發生錯誤: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_session(self, session_id: str, reason: str = "系統取消") -> Dict[str, Any]:
        """
        取消交互會話
        
        Args:
            session_id: 會話ID
            reason: 取消原因
            
        Returns:
            取消結果
        """
        try:
            cancel_data = {"reason": reason}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.mcp_url}/api/sessions/{session_id}/cancel",
                    json=cancel_data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"成功取消會話: {session_id}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"取消會話失敗: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            logger.error(f"取消會話時發生錯誤: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_service_health(self) -> bool:
        """
        檢查 Human Loop MCP 服務健康狀態
        
        Returns:
            服務是否健康
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.mcp_url}/api/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        logger.info(f"Human Loop MCP 服務健康: {health_data.get('status')}")
                        return True
                    else:
                        logger.warning(f"Human Loop MCP 服務異常: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"檢查服務健康狀態失敗: {str(e)}")
            return False

class HumanLoopIntegrationMixin:
    """
    Human Loop 集成 Mixin
    可以被現有的 PowerAutomation 組件繼承使用
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.human_loop_client = None
        self._init_human_loop_client()
    
    def _init_human_loop_client(self):
        """初始化 Human Loop 客戶端"""
        # 從環境變量或配置中獲取 MCP URL
        import os
        mcp_url = os.getenv('HUMAN_LOOP_MCP_URL', 'http://localhost:8096')
        self.human_loop_client = HumanLoopMCPClient(mcp_url)
    
    async def request_human_confirmation(self, 
                                       title: str,
                                       message: str,
                                       options: List[Dict[str, str]] = None,
                                       timeout: int = 300) -> Dict[str, Any]:
        """
        請求人工確認
        
        Args:
            title: 確認標題
            message: 確認消息
            options: 選項列表
            timeout: 超時時間
            
        Returns:
            用戶響應結果
        """
        if not options:
            options = [
                {"value": "confirm", "label": "確認"},
                {"value": "cancel", "label": "取消"}
            ]
        
        interaction_data = {
            "interaction_type": InteractionType.CONFIRMATION.value,
            "title": title,
            "message": message,
            "options": options,
            "timeout": timeout
        }
        
        # 創建會話
        session_result = await self.human_loop_client.create_interaction_session(
            interaction_data=interaction_data,
            workflow_id=getattr(self, 'workflow_id', None)
        )
        
        if not session_result.get("success"):
            return session_result
        
        session_id = session_result.get("session_id")
        
        # 等待用戶響應
        response_result = await self.human_loop_client.wait_for_user_response(
            session_id, timeout
        )
        
        return response_result
    
    async def request_human_selection(self,
                                    title: str,
                                    message: str,
                                    options: List[Dict[str, str]],
                                    multiple: bool = False,
                                    timeout: int = 300) -> Dict[str, Any]:
        """
        請求人工選擇
        
        Args:
            title: 選擇標題
            message: 選擇消息
            options: 選項列表
            multiple: 是否多選
            timeout: 超時時間
            
        Returns:
            用戶響應結果
        """
        interaction_data = {
            "interaction_type": InteractionType.SELECTION.value,
            "title": title,
            "message": message,
            "options": options,
            "multiple": multiple,
            "timeout": timeout
        }
        
        # 創建會話
        session_result = await self.human_loop_client.create_interaction_session(
            interaction_data=interaction_data,
            workflow_id=getattr(self, 'workflow_id', None)
        )
        
        if not session_result.get("success"):
            return session_result
        
        session_id = session_result.get("session_id")
        
        # 等待用戶響應
        response_result = await self.human_loop_client.wait_for_user_response(
            session_id, timeout
        )
        
        return response_result
    
    async def request_human_input(self,
                                title: str,
                                message: str,
                                fields: List[Dict[str, Any]],
                                timeout: int = 300) -> Dict[str, Any]:
        """
        請求人工輸入
        
        Args:
            title: 輸入標題
            message: 輸入消息
            fields: 輸入字段列表
            timeout: 超時時間
            
        Returns:
            用戶響應結果
        """
        interaction_data = {
            "interaction_type": InteractionType.INPUT.value,
            "title": title,
            "message": message,
            "fields": fields,
            "timeout": timeout
        }
        
        # 創建會話
        session_result = await self.human_loop_client.create_interaction_session(
            interaction_data=interaction_data,
            workflow_id=getattr(self, 'workflow_id', None)
        )
        
        if not session_result.get("success"):
            return session_result
        
        session_id = session_result.get("session_id")
        
        # 等待用戶響應
        response_result = await self.human_loop_client.wait_for_user_response(
            session_id, timeout
        )
        
        return response_result

# 便利函數
async def create_human_loop_client(mcp_url: str = "http://localhost:8096") -> HumanLoopMCPClient:
    """
    創建 Human Loop MCP 客戶端
    
    Args:
        mcp_url: MCP 服務 URL
        
    Returns:
        客戶端實例
    """
    client = HumanLoopMCPClient(mcp_url)
    
    # 檢查服務健康狀態
    if await client.check_service_health():
        logger.info("Human Loop MCP 服務連接成功")
        return client
    else:
        logger.warning("Human Loop MCP 服務連接失敗，但仍返回客戶端實例")
        return client

async def quick_confirmation(title: str, 
                           message: str, 
                           mcp_url: str = "http://localhost:8096",
                           timeout: int = 300) -> bool:
    """
    快速確認函數
    
    Args:
        title: 確認標題
        message: 確認消息
        mcp_url: MCP 服務 URL
        timeout: 超時時間
        
    Returns:
        用戶是否確認
    """
    client = await create_human_loop_client(mcp_url)
    
    interaction_data = {
        "interaction_type": InteractionType.CONFIRMATION.value,
        "title": title,
        "message": message,
        "options": [
            {"value": "confirm", "label": "確認"},
            {"value": "cancel", "label": "取消"}
        ],
        "timeout": timeout
    }
    
    # 創建會話
    session_result = await client.create_interaction_session(interaction_data)
    
    if not session_result.get("success"):
        logger.error(f"創建確認會話失敗: {session_result.get('error')}")
        return False
    
    session_id = session_result.get("session_id")
    
    # 等待用戶響應
    response_result = await client.wait_for_user_response(session_id, timeout)
    
    if response_result.get("success") and response_result.get("status") == "completed":
        user_choice = response_result.get("response", {}).get("choice")
        return user_choice == "confirm"
    else:
        logger.warning(f"用戶確認失敗或超時: {response_result}")
        return False

# 示例使用
async def example_usage():
    """示例用法"""
    
    # 方式1: 使用客戶端
    client = await create_human_loop_client()
    
    # 創建確認交互
    interaction_data = {
        "interaction_type": "confirmation",
        "title": "部署確認",
        "message": "確定要部署 PowerAutomation VSIX 到生產環境嗎？",
        "options": [
            {"value": "confirm", "label": "確認部署"},
            {"value": "cancel", "label": "取消部署"}
        ]
    }
    
    session_result = await client.create_interaction_session(interaction_data)
    if session_result.get("success"):
        session_id = session_result.get("session_id")
        response = await client.wait_for_user_response(session_id)
        print(f"用戶響應: {response}")
    
    # 方式2: 使用快速確認
    confirmed = await quick_confirmation(
        title="快速確認",
        message="是否繼續執行操作？"
    )
    print(f"用戶確認: {confirmed}")

if __name__ == "__main__":
    asyncio.run(example_usage())

