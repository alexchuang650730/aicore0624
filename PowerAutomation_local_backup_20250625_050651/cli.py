#!/usr/bin/env python3
"""
PowerAutomation Local MCP CLI

命令行接口，提供完整的PowerAutomation功能操作
支持交互模式和批處理模式

Author: Manus AI
Version: 1.0.0
Date: 2025-06-23
"""

import asyncio
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from powerautomation_local_mcp import PowerAutomationLocalMCP


class PowerAutomationCLI:
    """PowerAutomation CLI控制器"""
    
    def __init__(self, config_path: str = "config.toml"):
        """
        初始化CLI控制器
        
        Args:
            config_path: 配置文件路徑
        """
        self.config_path = config_path
        self.mcp_adapter = None
        self.interactive_mode = False
    
    async def initialize(self) -> bool:
        """
        初始化MCP適配器
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.mcp_adapter = PowerAutomationLocalMCP(self.config_path)
            return await self.mcp_adapter.initialize()
        except Exception as e:
            print(f"初始化失敗: {e}")
            return False
    
    async def status(self) -> Dict[str, Any]:
        """
        獲取系統狀態
        
        Returns:
            Dict[str, Any]: 系統狀態
        """
        if not self.mcp_adapter:
            return {"error": "MCP適配器未初始化"}
        
        return await self.mcp_adapter.get_status()
    
    async def start_server(self) -> bool:
        """
        啟動Local Server
        
        Returns:
            bool: 啟動是否成功
        """
        if not self.mcp_adapter:
            print("MCP適配器未初始化")
            return False
        
        print("正在啟動Local Server...")
        success = await self.mcp_adapter.start_server()
        
        if success:
            print("✅ Local Server啟動成功")
        else:
            print("❌ Local Server啟動失敗")
        
        return success
    
    async def start_extension(self) -> bool:
        """
        啟動VSCode Extension
        
        Returns:
            bool: 啟動是否成功
        """
        if not self.mcp_adapter:
            print("MCP適配器未初始化")
            return False
        
        print("正在啟動VSCode Extension...")
        success = await self.mcp_adapter.start_extension()
        
        if success:
            print("✅ VSCode Extension啟動成功")
        else:
            print("❌ VSCode Extension啟動失敗")
        
        return success
    
    async def start_all(self) -> bool:
        """
        啟動所有組件
        
        Returns:
            bool: 啟動是否成功
        """
        if not self.mcp_adapter:
            print("MCP適配器未初始化")
            return False
        
        print("正在啟動所有組件...")
        success = await self.mcp_adapter.start_all()
        
        if success:
            print("✅ 所有組件啟動成功")
        else:
            print("❌ 部分組件啟動失敗")
        
        return success
    
    async def stop_all(self) -> bool:
        """
        停止所有組件
        
        Returns:
            bool: 停止是否成功
        """
        if not self.mcp_adapter:
            print("MCP適配器未初始化")
            return False
        
        print("正在停止所有組件...")
        success = await self.mcp_adapter.stop_all()
        
        if success:
            print("✅ 所有組件已停止")
        else:
            print("❌ 停止組件時發生錯誤")
        
        return success
    
    async def manus_login(self) -> bool:
        """
        Manus登錄
        
        Returns:
            bool: 登錄是否成功
        """
        if not self.mcp_adapter:
            print("MCP適配器未初始化")
            return False
        
        print("正在登錄Manus...")
        
        request = {
            "id": f"cli_{int(time.time())}",
            "method": "server.manus_login",
            "params": {},
            "timestamp": time.time()
        }
        
        response = await self.mcp_adapter.handle_request(request)
        
        if response["result"]["status"] == "success":
            print("✅ Manus登錄成功")
            return True
        else:
            print(f"❌ Manus登錄失敗: {response['result']['message']}")
            return False
    
    async def send_message(self, message: str) -> bool:
        """
        發送消息到Manus
        
        Args:
            message: 要發送的消息
            
        Returns:
            bool: 發送是否成功
        """
        if not self.mcp_adapter:
            print("MCP適配器未初始化")
            return False
        
        print(f"正在發送消息: {message}")
        
        request = {
            "id": f"cli_{int(time.time())}",
            "method": "server.send_message",
            "params": {"message": message},
            "timestamp": time.time()
        }
        
        response = await self.mcp_adapter.handle_request(request)
        
        if response["result"]["status"] == "success":
            print("✅ 消息發送成功")
            return True
        else:
            print(f"❌ 消息發送失敗: {response['result']['message']}")
            return False
    
    async def get_conversations(self) -> Optional[Dict[str, Any]]:
        """
        獲取對話歷史
        
        Returns:
            Optional[Dict[str, Any]]: 對話歷史數據
        """
        if not self.mcp_adapter:
            print("MCP適配器未初始化")
            return None
        
        print("正在獲取對話歷史...")
        
        request = {
            "id": f"cli_{int(time.time())}",
            "method": "server.get_conversations",
            "params": {},
            "timestamp": time.time()
        }
        
        response = await self.mcp_adapter.handle_request(request)
        
        if response["result"]["status"] == "success":
            data = response["result"]["data"]
            print(f"✅ 獲取到 {len(data.get('conversations', []))} 條對話記錄")
            return data
        else:
            print(f"❌ 獲取對話歷史失敗: {response['result']['message']}")
            return None
    
    async def get_tasks(self) -> Optional[Dict[str, Any]]:
        """
        獲取任務列表
        
        Returns:
            Optional[Dict[str, Any]]: 任務列表數據
        """
        if not self.mcp_adapter:
            print("MCP適配器未初始化")
            return None
        
        print("正在獲取任務列表...")
        
        request = {
            "id": f"cli_{int(time.time())}",
            "method": "server.get_tasks",
            "params": {},
            "timestamp": time.time()
        }
        
        response = await self.mcp_adapter.handle_request(request)
        
        if response["result"]["status"] == "success":
            data = response["result"]["data"]
            print(f"✅ 獲取到 {len(data.get('tasks', []))} 個任務")
            return data
        else:
            print(f"❌ 獲取任務列表失敗: {response['result']['message']}")
            return None
    
    async def run_test(self, test_case: str) -> bool:
        """
        運行自動化測試
        
        Args:
            test_case: 測試案例名稱
            
        Returns:
            bool: 測試是否成功
        """
        if not self.mcp_adapter:
            print("MCP適配器未初始化")
            return False
        
        print(f"正在運行測試案例: {test_case}")
        
        request = {
            "id": f"cli_{int(time.time())}",
            "method": "server.run_test",
            "params": {"test_case": test_case},
            "timestamp": time.time()
        }
        
        response = await self.mcp_adapter.handle_request(request)
        
        if response["result"]["status"] == "success":
            data = response["result"]["data"]
            print(f"✅ 測試完成 - 成功率: {data.get('success_rate', 'N/A')}%")
            return True
        else:
            print(f"❌ 測試運行失敗: {response['result']['message']}")
            return False
    
    async def interactive_mode(self):
        """交互模式"""
        self.interactive_mode = True
        print("🚀 PowerAutomation Local MCP 交互模式")
        print("輸入 'help' 查看可用命令，輸入 'exit' 退出")
        print("-" * 50)
        
        while self.interactive_mode:
            try:
                command = input("PowerAutomation> ").strip()
                
                if not command:
                    continue
                
                if command.lower() in ['exit', 'quit', 'q']:
                    break
                elif command.lower() == 'help':
                    self._show_help()
                elif command.lower() == 'status':
                    status = await self.status()
                    print(json.dumps(status, indent=2, ensure_ascii=False))
                elif command.lower() == 'start-server':
                    await self.start_server()
                elif command.lower() == 'start-extension':
                    await self.start_extension()
                elif command.lower() == 'start-all':
                    await self.start_all()
                elif command.lower() == 'stop-all':
                    await self.stop_all()
                elif command.lower() == 'login':
                    await self.manus_login()
                elif command.startswith('send '):
                    message = command[5:]
                    await self.send_message(message)
                elif command.lower() == 'conversations':
                    conversations = await self.get_conversations()
                    if conversations:
                        print(json.dumps(conversations, indent=2, ensure_ascii=False))
                elif command.lower() == 'tasks':
                    tasks = await self.get_tasks()
                    if tasks:
                        print(json.dumps(tasks, indent=2, ensure_ascii=False))
                elif command.startswith('test '):
                    test_case = command[5:]
                    await self.run_test(test_case)
                else:
                    print(f"未知命令: {command}")
                    print("輸入 'help' 查看可用命令")
                
            except KeyboardInterrupt:
                print("\n使用 'exit' 命令退出")
            except Exception as e:
                print(f"執行命令時發生錯誤: {e}")
        
        print("退出交互模式")
    
    def _show_help(self):
        """顯示幫助信息"""
        help_text = """
可用命令:
  help                    - 顯示此幫助信息
  status                  - 查看系統狀態
  start-server           - 啟動Local Server
  start-extension        - 啟動VSCode Extension
  start-all              - 啟動所有組件
  stop-all               - 停止所有組件
  login                  - 登錄Manus
  send <message>         - 發送消息到Manus
  conversations          - 獲取對話歷史
  tasks                  - 獲取任務列表
  test <test_case>       - 運行自動化測試
  exit/quit/q            - 退出交互模式

示例:
  send 你好，請幫我分析這個文檔
  test TC001
        """
        print(help_text)
    
    async def cleanup(self):
        """清理資源"""
        if self.mcp_adapter:
            await self.mcp_adapter.shutdown()


async def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="PowerAutomation Local MCP CLI")
    parser.add_argument("--config", "-c", default="config.toml", help="配置文件路徑")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 狀態命令
    subparsers.add_parser("status", help="查看系統狀態")
    
    # 啟動命令
    subparsers.add_parser("start-server", help="啟動Local Server")
    subparsers.add_parser("start-extension", help="啟動VSCode Extension")
    subparsers.add_parser("start-all", help="啟動所有組件")
    
    # 停止命令
    subparsers.add_parser("stop-all", help="停止所有組件")
    
    # Manus命令
    subparsers.add_parser("login", help="登錄Manus")
    
    send_parser = subparsers.add_parser("send", help="發送消息")
    send_parser.add_argument("message", help="要發送的消息")
    
    subparsers.add_parser("conversations", help="獲取對話歷史")
    subparsers.add_parser("tasks", help="獲取任務列表")
    
    # 測試命令
    test_parser = subparsers.add_parser("test", help="運行自動化測試")
    test_parser.add_argument("test_case", help="測試案例名稱")
    
    # 交互模式
    subparsers.add_parser("interactive", help="進入交互模式")
    
    args = parser.parse_args()
    
    # 創建CLI實例
    cli = PowerAutomationCLI(args.config)
    
    try:
        # 初始化
        if not await cli.initialize():
            print("CLI初始化失敗")
            return 1
        
        # 執行命令
        if args.command == "status":
            status = await cli.status()
            print(json.dumps(status, indent=2, ensure_ascii=False))
            
        elif args.command == "start-server":
            await cli.start_server()
            
        elif args.command == "start-extension":
            await cli.start_extension()
            
        elif args.command == "start-all":
            await cli.start_all()
            
        elif args.command == "stop-all":
            await cli.stop_all()
            
        elif args.command == "login":
            await cli.manus_login()
            
        elif args.command == "send":
            await cli.send_message(args.message)
            
        elif args.command == "conversations":
            conversations = await cli.get_conversations()
            if conversations:
                print(json.dumps(conversations, indent=2, ensure_ascii=False))
                
        elif args.command == "tasks":
            tasks = await cli.get_tasks()
            if tasks:
                print(json.dumps(tasks, indent=2, ensure_ascii=False))
                
        elif args.command == "test":
            await cli.run_test(args.test_case)
            
        elif args.command == "interactive":
            await cli.interactive_mode()
            
        else:
            # 默認進入交互模式
            await cli.interactive_mode()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n操作被用戶中斷")
        return 1
    except Exception as e:
        print(f"執行過程中發生錯誤: {e}")
        return 1
    finally:
        await cli.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

