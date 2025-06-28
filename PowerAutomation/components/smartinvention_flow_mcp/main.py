#!/usr/bin/env python3
"""
SmartInvention Flow MCP - 统一智能分析服务
整合Manus数据获取、Claude Code分析、质量评分的完整流程

Version: 1.0.0
Author: AICore Team
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
from aiohttp import web
import aiofiles

# 添加项目路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent))

# 导入核心模块
from core.manus_connector import ManusConnector
from core.task_manager import TaskManager
from core.data_collector import DataCollector
from ai.claude_adapter import ClaudeAdapter
from ai.requirement_analyzer import RequirementAnalyzer
from ai.quality_scorer import QualityScorer
from ai.suggestion_generator import SuggestionGenerator
from flow.request_router import RequestRouter
from flow.pipeline_manager import PipelineManager
from flow.response_formatter import ResponseFormatter
from api.smartui_interface import SmartUIInterface
from api.health_checker import HealthChecker
from api.config_manager import ConfigManager
from utils.logger import setup_logger
from utils.cache import CacheManager
from utils.helpers import load_config, validate_request

class SmartInventionFlowMCP:
    """SmartInvention Flow MCP 主服务类"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or str(current_dir / "config")
        self.config = {}
        self.components = {}
        self.app = None
        self.logger = None
        self.initialized = False
        
    async def initialize(self):
        """初始化MCP服务"""
        try:
            # 设置日志
            self.logger = setup_logger("SmartInventionFlowMCP")
            self.logger.info("🚀 启动 SmartInvention Flow MCP v1.0.0")
            
            # 加载配置
            await self._load_configurations()
            
            # 初始化组件
            await self._initialize_components()
            
            # 设置Web应用
            await self._setup_web_app()
            
            self.initialized = True
            self.logger.info("✅ SmartInvention Flow MCP 初始化完成")
            
        except Exception as e:
            self.logger.error(f"❌ 初始化失败: {e}")
            raise
    
    async def _load_configurations(self):
        """加载所有配置文件"""
        config_files = [
            "manus_config.json",
            "claude_config.json", 
            "flow_config.json"
        ]
        
        for config_file in config_files:
            config_path = Path(self.config_dir) / config_file
            if config_path.exists():
                async with aiofiles.open(config_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    config_data = json.loads(content)
                    self.config.update(config_data)
                    self.logger.info(f"📄 已加载配置: {config_file}")
            else:
                self.logger.warning(f"⚠️ 配置文件不存在: {config_file}")
    
    async def _initialize_components(self):
        """初始化所有组件"""
        try:
            # 核心组件
            self.components['manus_connector'] = ManusConnector(self.config.get('manus', {}))
            self.components['task_manager'] = TaskManager(self.config.get('manus', {}))
            self.components['data_collector'] = DataCollector(self.config.get('manus', {}))
            
            # AI组件
            self.components['claude_adapter'] = ClaudeAdapter(self.config.get('claude_code', {}))
            self.components['requirement_analyzer'] = RequirementAnalyzer(self.config.get('claude_code', {}))
            self.components['quality_scorer'] = QualityScorer(self.config.get('comparison_engine', {}))
            self.components['suggestion_generator'] = SuggestionGenerator(self.config.get('claude_code', {}))
            
            # 流程控制组件
            self.components['request_router'] = RequestRouter(self.config.get('flow_config', {}))
            self.components['pipeline_manager'] = PipelineManager(self.config.get('flow_config', {}))
            self.components['response_formatter'] = ResponseFormatter(self.config.get('flow_config', {}))
            
            # API组件
            self.components['smartui_interface'] = SmartUIInterface(self.config.get('flow_config', {}))
            self.components['health_checker'] = HealthChecker(self.config.get('flow_config', {}))
            self.components['config_manager'] = ConfigManager(self.config)
            
            # 工具组件
            self.components['cache_manager'] = CacheManager(self.config.get('flow_control', {}))
            
            # 初始化所有组件
            for name, component in self.components.items():
                if hasattr(component, 'initialize'):
                    await component.initialize()
                    self.logger.info(f"✅ 组件初始化完成: {name}")
                    
        except Exception as e:
            self.logger.error(f"❌ 组件初始化失败: {e}")
            raise
    
    async def _setup_web_app(self):
        """设置Web应用和路由"""
        self.app = web.Application()
        
        # 设置路由
        base_path = self.config.get('flow_config', {}).get('api_endpoints', {}).get('base_path', '/api/smartinvention')
        
        # 主要API端点
        self.app.router.add_post(f"{base_path}/analyze", self.handle_analyze)
        self.app.router.add_get(f"{base_path}/health", self.handle_health)
        self.app.router.add_get(f"{base_path}/status", self.handle_status)
        self.app.router.add_get(f"{base_path}/config", self.handle_get_config)
        self.app.router.add_post(f"{base_path}/config", self.handle_set_config)
        self.app.router.add_get(f"{base_path}/tasks", self.handle_get_tasks)
        self.app.router.add_get(f"{base_path}/conversations", self.handle_get_conversations)
        self.app.router.add_get(f"{base_path}/files", self.handle_get_files)
        
        # CORS支持
        self.app.middlewares.append(self._cors_middleware)
        
        self.logger.info(f"🌐 Web应用设置完成，基础路径: {base_path}")
    
    async def _cors_middleware(self, request, handler):
        """CORS中间件"""
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    async def handle_analyze(self, request):
        """处理分析请求 - 主要API端点"""
        try:
            # 解析请求
            data = await request.json()
            
            # 验证请求
            if not validate_request(data):
                return web.json_response({
                    'error': '请求格式无效',
                    'code': 'INVALID_REQUEST'
                }, status=400)
            
            # 路由请求
            router = self.components['request_router']
            route_info = await router.route_request(data)
            
            # 执行分析管道
            pipeline = self.components['pipeline_manager']
            result = await pipeline.execute_pipeline(data, route_info)
            
            # 格式化响应
            formatter = self.components['response_formatter']
            formatted_result = await formatter.format_response(result)
            
            return web.json_response(formatted_result)
            
        except Exception as e:
            self.logger.error(f"❌ 分析请求处理失败: {e}")
            return web.json_response({
                'error': f'处理失败: {str(e)}',
                'code': 'PROCESSING_ERROR'
            }, status=500)
    
    async def handle_health(self, request):
        """健康检查端点"""
        try:
            health_checker = self.components['health_checker']
            health_status = await health_checker.check_health()
            return web.json_response(health_status)
        except Exception as e:
            return web.json_response({
                'status': 'unhealthy',
                'error': str(e)
            }, status=500)
    
    async def handle_status(self, request):
        """系统状态端点"""
        try:
            status = {
                'service': 'SmartInvention Flow MCP',
                'version': '1.0.0',
                'initialized': self.initialized,
                'components': {
                    name: 'active' if hasattr(comp, 'initialized') and comp.initialized else 'inactive'
                    for name, comp in self.components.items()
                },
                'timestamp': datetime.now().isoformat()
            }
            return web.json_response(status)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_get_config(self, request):
        """获取配置端点"""
        try:
            config_manager = self.components['config_manager']
            config = await config_manager.get_config()
            return web.json_response(config)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_set_config(self, request):
        """设置配置端点"""
        try:
            data = await request.json()
            config_manager = self.components['config_manager']
            result = await config_manager.set_config(data)
            return web.json_response(result)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_get_tasks(self, request):
        """获取任务列表端点"""
        try:
            task_manager = self.components['task_manager']
            tasks = await task_manager.get_tasks()
            return web.json_response({'tasks': tasks})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_get_conversations(self, request):
        """获取对话列表端点"""
        try:
            data_collector = self.components['data_collector']
            conversations = await data_collector.get_conversations()
            return web.json_response({'conversations': conversations})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_get_files(self, request):
        """获取文件列表端点"""
        try:
            data_collector = self.components['data_collector']
            files = await data_collector.get_files()
            return web.json_response({'files': files})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def start_server(self):
        """启动服务器"""
        if not self.initialized:
            await self.initialize()
        
        host = self.config.get('flow_config', {}).get('host', '18.212.49.136')
        port = self.config.get('flow_config', {}).get('port', 8080)
        
        self.logger.info(f"🚀 启动服务器: http://{host}:{port}")
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        self.logger.info(f"✅ SmartInvention Flow MCP 服务已启动")
        self.logger.info(f"📡 API基础路径: http://{host}:{port}/api/smartinvention")
        
        return runner

async def main():
    """主函数"""
    try:
        # 创建MCP实例
        mcp = SmartInventionFlowMCP()
        
        # 启动服务器
        runner = await mcp.start_server()
        
        # 保持运行
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            mcp.logger.info("🛑 收到停止信号，正在关闭服务...")
        finally:
            await runner.cleanup()
            mcp.logger.info("✅ 服务已关闭")
            
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

