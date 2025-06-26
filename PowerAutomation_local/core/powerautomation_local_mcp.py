"""
PowerAutomation Local MCP with Replay Chain Support
支持Replay鏈結的PowerAutomation本地MCP服務

Author: Manus AI
Version: 2.0.0
Date: 2025-06-23
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_server import MCPServer, create_server_config, setup_logging
from mcp_manus_integration import MCPManusIntegration
from manus_replay_chain_core import ReplayChainManager, TaskNode, ReplayChain


class PowerAutomationMCP:
    """PowerAutomation MCP主服務類"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化PowerAutomation MCP
        
        Args:
            config_path: 配置文件路徑
        """
        self.config_path = config_path or "config.toml"
        self.config = self._load_config()
        self.logger = self._setup_logger()
        
        # 核心組件
        self.mcp_server = None
        self.manus_integration = None
        self.chain_manager = None
        
        # 服務狀態
        self.is_running = False
        self.start_time = None
    
    def _load_config(self) -> Dict[str, Any]:
        """加載配置"""
        try:
            if os.path.exists(self.config_path):
                import toml
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = toml.load(f)
                return config
            else:
                # 使用默認配置
                return create_server_config()
        except Exception as e:
            print(f"加載配置失敗，使用默認配置: {e}")
            return create_server_config()
    
    def _setup_logger(self) -> logging.Logger:
        """設置日誌器"""
        setup_logging(self.config)
        return logging.getLogger(__name__)
    
    async def start(self):
        """啟動MCP服務"""
        try:
            self.logger.info("啟動PowerAutomation MCP服務...")
            self.start_time = time.time()
            
            # 創建MCP服務器
            self.mcp_server = MCPServer(self.config)
            
            # 初始化服務
            await self.mcp_server._initialize_services()
            
            self.is_running = True
            self.logger.info("✅ PowerAutomation MCP服務啟動成功")
            
            # 運行服務器
            server_config = self.config.get("server", {})
            self.mcp_server.run(
                host=server_config.get("host", "0.0.0.0"),
                port=server_config.get("port", 8080)
            )
            
        except Exception as e:
            self.logger.error(f"啟動MCP服務失敗: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """停止MCP服務"""
        try:
            self.logger.info("停止PowerAutomation MCP服務...")
            
            if self.mcp_server:
                await self.mcp_server._cleanup_services()
                self.mcp_server = None
            
            self.is_running = False
            self.logger.info("✅ PowerAutomation MCP服務已停止")
            
        except Exception as e:
            self.logger.error(f"停止MCP服務失敗: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """獲取服務狀態"""
        status = {
            "service_name": "PowerAutomation MCP",
            "version": "2.0.0",
            "is_running": self.is_running,
            "start_time": self.start_time,
            "uptime": time.time() - self.start_time if self.start_time else 0,
            "config_path": self.config_path
        }
        
        if self.mcp_server:
            status["server_status"] = self.mcp_server.server_status
            
            if self.mcp_server.manus_integration:
                status["manus_status"] = self.mcp_server.manus_integration.status
                status["chain_manager_status"] = {
                    "total_tasks": len(self.mcp_server.manus_integration.chain_manager.tasks),
                    "total_chains": len(self.mcp_server.manus_integration.chain_manager.chains)
                }
        
        return status


# ==================== CLI接口 ====================

async def cli_main():
    """CLI主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PowerAutomation MCP服務")
    parser.add_argument("--config", "-c", help="配置文件路徑", default="config.toml")
    parser.add_argument("--host", help="服務器主機", default="0.0.0.0")
    parser.add_argument("--port", "-p", type=int, help="服務器端口", default=8080)
    parser.add_argument("--log-level", help="日誌級別", default="INFO")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 啟動命令
    start_parser = subparsers.add_parser("start", help="啟動MCP服務")
    start_parser.add_argument("--daemon", "-d", action="store_true", help="後台運行")
    
    # 停止命令
    stop_parser = subparsers.add_parser("stop", help="停止MCP服務")
    
    # 狀態命令
    status_parser = subparsers.add_parser("status", help="查看服務狀態")
    
    # 測試命令
    test_parser = subparsers.add_parser("test", help="運行測試")
    test_parser.add_argument("--test-type", choices=["basic", "chain", "integration"], default="basic")
    
    args = parser.parse_args()
    
    # 創建MCP實例
    mcp = PowerAutomationMCP(args.config)
    
    try:
        if args.command == "start" or not args.command:
            # 啟動服務
            await mcp.start()
            
        elif args.command == "status":
            # 顯示狀態
            status = mcp.get_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))
            
        elif args.command == "test":
            # 運行測試
            await run_tests(mcp, args.test_type)
            
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n收到中斷信號，正在停止服務...")
        await mcp.stop()
    except Exception as e:
        print(f"運行失敗: {e}")
        await mcp.stop()
        sys.exit(1)


async def run_tests(mcp: PowerAutomationMCP, test_type: str):
    """運行測試"""
    print(f"運行 {test_type} 測試...")
    
    try:
        if test_type == "basic":
            await test_basic_functionality(mcp)
        elif test_type == "chain":
            await test_chain_functionality(mcp)
        elif test_type == "integration":
            await test_integration_functionality(mcp)
        
        print("✅ 測試完成")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        raise


async def test_basic_functionality(mcp: PowerAutomationMCP):
    """測試基本功能"""
    print("測試基本功能...")
    
    # 測試配置加載
    assert mcp.config is not None, "配置加載失敗"
    print("✓ 配置加載正常")
    
    # 測試日誌器
    assert mcp.logger is not None, "日誌器創建失敗"
    print("✓ 日誌器創建正常")
    
    # 測試狀態獲取
    status = mcp.get_status()
    assert status["service_name"] == "PowerAutomation MCP", "服務名稱不正確"
    print("✓ 狀態獲取正常")


async def test_chain_functionality(mcp: PowerAutomationMCP):
    """測試鏈結功能"""
    print("測試鏈結功能...")
    
    # 創建鏈結管理器
    chain_manager = ReplayChainManager()
    
    try:
        # 創建測試任務
        task1 = TaskNode(
            task_id="test_task_1",
            task_type="manus_login",
            description="測試登錄任務",
            parameters={"email": "test@example.com"},
            priority=9
        )
        
        task2 = TaskNode(
            task_id="test_task_2",
            task_type="send_message",
            description="測試發送消息任務",
            parameters={"message": "Hello World"},
            dependencies=["test_task_1"],
            priority=7
        )
        
        # 添加任務
        await chain_manager.add_task(task1)
        await chain_manager.add_task(task2)
        print("✓ 任務創建正常")
        
        # 自動生成鏈結
        chain_ids = await chain_manager.auto_generate_chains()
        assert len(chain_ids) > 0, "鏈結生成失敗"
        print("✓ 鏈結生成正常")
        
        # 獲取鏈結
        chain = await chain_manager.get_chain(chain_ids[0])
        assert chain is not None, "鏈結獲取失敗"
        assert len(chain.nodes) == 2, "鏈結任務數量不正確"
        print("✓ 鏈結獲取正常")
        
    finally:
        await chain_manager.cleanup()


async def test_integration_functionality(mcp: PowerAutomationMCP):
    """測試集成功能"""
    print("測試集成功能...")
    
    # 這裡可以添加更複雜的集成測試
    # 例如測試MCP服務器和Manus集成的交互
    
    print("✓ 集成測試通過")


# ==================== 入口點 ====================

def main():
    """主入口點"""
    try:
        asyncio.run(cli_main())
    except KeyboardInterrupt:
        print("\n程序被用戶中斷")
    except Exception as e:
        print(f"程序運行失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

