#!/usr/bin/env python3
"""
SmartInvention Manus Mode CLI
命令行接口，用于管理和操作SmartInvention Manus模式MCP

Usage:
    python cli.py --help
    python cli.py status
    python cli.py tasks --limit 5
    python cli.py checkin-summary
    python cli.py agent-summary
    python cli.py save-history
    python cli.py start-server --port 5003
"""

import argparse
import asyncio
import json
import sys
import logging
from datetime import datetime
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from smartinvention_mcp_enhanced import SmartinventionManusModeMCP
from smartui_manus_integration import app, mcp_instance

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ManusModeCLI:
    """SmartInvention Manus模式命令行接口"""
    
    def __init__(self):
        self.mcp_config = {
            "manus": {
                "base_url": "https://manus.im",
                "app_url": "https://manus.im/app/oXk20YJhBI530ArzGBJEJC",
                "auto_login": True
            }
        }
        self.mcp = SmartinventionManusModeMCP(self.mcp_config)
    
    async def initialize(self):
        """初始化MCP实例"""
        try:
            result = await self.mcp.initialize()
            if result.get("success"):
                logger.info("MCP初始化成功")
                return True
            else:
                logger.error(f"MCP初始化失败: {result.get('error')}")
                return False
        except Exception as e:
            logger.error(f"MCP初始化异常: {e}")
            return False
    
    async def get_status(self):
        """获取系统状态"""
        try:
            print("🔍 获取SmartInvention Manus模式状态...")
            
            # 获取任务状态
            tasks_result = await self.mcp.handle_request("get_latest_tasks_with_checkin", {"limit": 3})
            
            # 获取checkin汇总
            checkin_result = await self.mcp.handle_request("get_checkin_summary", {})
            
            # 获取Agent汇总
            agent_result = await self.mcp.handle_request("get_agent_summary", {})
            
            # 显示状态信息
            print("\n" + "="*60)
            print("📊 SmartInvention Manus模式状态报告")
            print("="*60)
            
            # 任务状态
            if tasks_result.get("success"):
                tasks = tasks_result.get("tasks", [])
                print(f"\n📋 任务状态:")
                print(f"   最新任务数量: {len(tasks)}")
                for i, task in enumerate(tasks[:3], 1):
                    title = task.get("title", "未知任务")[:30]
                    files_count = task.get("checkin_summary", {}).get("total_files", 0)
                    print(f"   {i}. {title} ({files_count}个文件)")
            
            # Checkin状态
            if checkin_result.get("success"):
                summary = checkin_result.get("summary", {})
                print(f"\n📁 文件Checkin状态:")
                print(f"   总文件数: {summary.get('total_files', 0)}")
                status_dist = summary.get("status_distribution", {})
                for status, count in status_dist.items():
                    print(f"   {status}: {count}个")
            
            # Agent状态
            if agent_result.get("success"):
                summary = agent_result.get("summary", {})
                print(f"\n🤖 Agent状态:")
                print(f"   总Agent数: {summary.get('total_agents', 0)}")
                task_dist = summary.get("task_distribution", {})
                for task_id, count in task_dist.items():
                    print(f"   任务{task_id}: {count}个Agent")
            
            print(f"\n⏰ 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            print(f"❌ 获取状态失败: {e}")
    
    async def get_tasks(self, limit=5):
        """获取最新任务"""
        try:
            print(f"📋 获取最新{limit}个任务...")
            
            result = await self.mcp.handle_request("get_latest_tasks_with_checkin", {"limit": limit})
            
            if not result.get("success"):
                print(f"❌ 获取任务失败: {result.get('error')}")
                return
            
            tasks = result.get("tasks", [])
            
            print(f"\n找到{len(tasks)}个任务:")
            print("-" * 80)
            
            for i, task in enumerate(tasks, 1):
                title = task.get("title", "未知任务")
                status = task.get("status", "未知")
                checkin_summary = task.get("checkin_summary", {})
                
                print(f"{i}. 任务: {title}")
                print(f"   状态: {status}")
                print(f"   文件: {checkin_summary.get('total_files', 0)}个")
                print(f"   已签入: {checkin_summary.get('checked_in', 0)}个")
                print(f"   待处理: {checkin_summary.get('pending', 0)}个")
                print(f"   已修改: {checkin_summary.get('modified', 0)}个")
                print("-" * 80)
            
        except Exception as e:
            logger.error(f"获取任务失败: {e}")
            print(f"❌ 获取任务失败: {e}")
    
    async def get_checkin_summary(self):
        """获取checkin状态汇总"""
        try:
            print("📁 获取文件Checkin状态汇总...")
            
            result = await self.mcp.handle_request("get_checkin_summary", {})
            
            if not result.get("success"):
                print(f"❌ 获取checkin汇总失败: {result.get('error')}")
                return
            
            summary = result.get("summary", {})
            
            print("\n📊 文件Checkin状态汇总:")
            print("-" * 50)
            print(f"总文件数: {summary.get('total_files', 0)}")
            print(f"待处理更改: {summary.get('pending_changes_count', 0)}")
            print(f"最后更新: {summary.get('last_updated', 'N/A')}")
            
            print("\n状态分布:")
            status_dist = summary.get("status_distribution", {})
            for status, count in status_dist.items():
                percentage = (count / summary.get('total_files', 1)) * 100
                print(f"  {status}: {count}个 ({percentage:.1f}%)")
            
            print("\n任务分解:")
            task_breakdown = summary.get("task_breakdown", {})
            for task_id, stats in task_breakdown.items():
                print(f"  任务{task_id}: {stats.get('files', 0)}个文件")
                print(f"    - 已签入: {stats.get('checked_in', 0)}个")
                print(f"    - 待处理: {stats.get('pending', 0)}个")
            
        except Exception as e:
            logger.error(f"获取checkin汇总失败: {e}")
            print(f"❌ 获取checkin汇总失败: {e}")
    
    async def get_agent_summary(self):
        """获取Agent状态汇总"""
        try:
            print("🤖 获取Agent状态汇总...")
            
            result = await self.mcp.handle_request("get_agent_summary", {})
            
            if not result.get("success"):
                print(f"❌ 获取Agent汇总失败: {result.get('error')}")
                return
            
            summary = result.get("summary", {})
            
            print("\n🤖 Agent状态汇总:")
            print("-" * 50)
            print(f"总Agent数: {summary.get('total_agents', 0)}")
            print(f"最后更新: {summary.get('last_updated', 'N/A')}")
            
            print("\nAgent列表:")
            agents = summary.get("agents", [])
            for agent in agents:
                print(f"  ID: {agent.get('agent_id')}")
                print(f"  名称: {agent.get('agent_name')}")
                print(f"  类型: {agent.get('agent_type')}")
                print(f"  任务: {agent.get('task_id')}")
                print(f"  目录: {agent.get('directory')}")
                print(f"  创建时间: {agent.get('created_at')}")
                print("-" * 30)
            
            print("\n任务分布:")
            task_dist = summary.get("task_distribution", {})
            for task_id, count in task_dist.items():
                print(f"  任务{task_id}: {count}个Agent")
            
        except Exception as e:
            logger.error(f"获取Agent汇总失败: {e}")
            print(f"❌ 获取Agent汇总失败: {e}")
    
    async def save_history(self):
        """保存完整历史记录"""
        try:
            print("💾 保存任务完整历史记录...")
            
            result = await self.mcp.handle_request("save_tasks_complete_history", {})
            
            if not result.get("success"):
                print(f"❌ 保存历史失败: {result.get('error')}")
                return
            
            saved_tasks = result.get("saved_tasks", [])
            
            print(f"\n✅ 成功保存{len(saved_tasks)}个任务的完整历史:")
            print("-" * 60)
            
            for task_summary in saved_tasks:
                task_id = task_summary.get("task_id")
                conversations = task_summary.get("total_conversations", 0)
                modifications = task_summary.get("total_modifications", 0)
                agents = task_summary.get("agents_count", 0)
                
                print(f"任务: {task_id}")
                print(f"  对话记录: {conversations}条")
                print(f"  修改记录: {modifications}条")
                print(f"  参与Agent: {agents}个")
                print(f"  保存时间: {task_summary.get('saved_at')}")
                print("-" * 30)
            
            print(f"\n📁 数据保存位置: /tmp/smartinvention_agents/")
            
        except Exception as e:
            logger.error(f"保存历史失败: {e}")
            print(f"❌ 保存历史失败: {e}")
    
    def start_server(self, port=5003):
        """启动HTTP服务器"""
        try:
            print(f"🚀 启动SmartUI Manus Integration服务器...")
            print(f"   端口: {port}")
            print(f"   健康检查: http://localhost:{port}/health")
            print(f"   API文档: http://localhost:{port}/api/")
            print("\n按 Ctrl+C 停止服务器")
            
            app.run(host='0.0.0.0', port=port, debug=False)
            
        except KeyboardInterrupt:
            print("\n👋 服务器已停止")
        except Exception as e:
            logger.error(f"启动服务器失败: {e}")
            print(f"❌ 启动服务器失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="SmartInvention Manus Mode CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python cli.py status                    # 获取系统状态
  python cli.py tasks --limit 10          # 获取最新10个任务
  python cli.py checkin-summary           # 获取checkin状态汇总
  python cli.py agent-summary             # 获取Agent状态汇总
  python cli.py save-history              # 保存完整历史记录
  python cli.py start-server --port 5003  # 启动HTTP服务器
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # status命令
    subparsers.add_parser('status', help='获取系统状态')
    
    # tasks命令
    tasks_parser = subparsers.add_parser('tasks', help='获取最新任务')
    tasks_parser.add_argument('--limit', type=int, default=5, help='任务数量限制 (默认: 5)')
    
    # checkin-summary命令
    subparsers.add_parser('checkin-summary', help='获取checkin状态汇总')
    
    # agent-summary命令
    subparsers.add_parser('agent-summary', help='获取Agent状态汇总')
    
    # save-history命令
    subparsers.add_parser('save-history', help='保存完整历史记录')
    
    # start-server命令
    server_parser = subparsers.add_parser('start-server', help='启动HTTP服务器')
    server_parser.add_argument('--port', type=int, default=5003, help='服务器端口 (默认: 5003)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = ManusModeCLI()
    
    # 对于start-server命令，不需要异步初始化
    if args.command == 'start-server':
        cli.start_server(args.port)
        return
    
    # 其他命令需要异步处理
    async def run_command():
        # 初始化MCP
        if not await cli.initialize():
            print("❌ MCP初始化失败，无法继续")
            return
        
        # 执行相应命令
        if args.command == 'status':
            await cli.get_status()
        elif args.command == 'tasks':
            await cli.get_tasks(args.limit)
        elif args.command == 'checkin-summary':
            await cli.get_checkin_summary()
        elif args.command == 'agent-summary':
            await cli.get_agent_summary()
        elif args.command == 'save-history':
            await cli.save_history()
    
    # 运行异步命令
    try:
        asyncio.run(run_command())
    except KeyboardInterrupt:
        print("\n👋 操作已取消")
    except Exception as e:
        logger.error(f"命令执行失败: {e}")
        print(f"❌ 命令执行失败: {e}")

if __name__ == "__main__":
    main()

