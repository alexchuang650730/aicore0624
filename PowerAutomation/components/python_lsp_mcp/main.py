#!/usr/bin/env python3
"""
Python LSP MCP - Language Server Protocol 支持
为 SmartUI Monaco Editor 提供 Python 语言服务器功能
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, List, Optional, Any
import websockets
from websockets.server import serve
import subprocess
import threading
import queue
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PythonLSPServer:
    """
    Python LSP 服务器
    提供代码补全、语法检查、跳转定义等功能
    """
    
    def __init__(self, port: int = 8081):
        self.port = port
        self.clients = set()
        self.lsp_process = None
        self.message_queue = queue.Queue()
        self.running = False
        
    async def start_server(self):
        """启动 WebSocket LSP 服务器"""
        logger.info(f"启动 Python LSP 服务器，端口: {self.port}")
        
        try:
            # 启动 pylsp 进程
            await self._start_pylsp_process()
            
            # 启动 WebSocket 服务器
            async with serve(
                self.handle_client,
                "0.0.0.0",
                self.port,
                ping_interval=20,
                ping_timeout=10
            ):
                logger.info(f"✅ Python LSP 服务器已启动: ws://0.0.0.0:{self.port}")
                self.running = True
                
                # 保持服务器运行
                await asyncio.Future()  # run forever
                
        except Exception as e:
            logger.error(f"启动 LSP 服务器失败: {e}")
            raise
    
    async def _start_pylsp_process(self):
        """启动 Python Language Server 进程"""
        try:
            # 检查 pylsp 是否安装
            result = subprocess.run(['which', 'pylsp'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning("pylsp 未安装，尝试安装...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'python-lsp-server[all]'], check=True)
            
            # 启动 pylsp 进程
            self.lsp_process = subprocess.Popen(
                ['pylsp', '--ws', '--port', str(self.port + 1)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            logger.info("✅ pylsp 进程已启动")
            
        except Exception as e:
            logger.error(f"启动 pylsp 进程失败: {e}")
            # 如果 pylsp 启动失败，使用内置的简化 LSP 功能
            logger.info("使用内置简化 LSP 功能")
    
    async def handle_client(self, websocket, path):
        """处理客户端连接"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"新客户端连接: {client_id}")
        
        self.clients.add(websocket)
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"客户端断开连接: {client_id}")
        except Exception as e:
            logger.error(f"处理客户端消息时出错: {e}")
        finally:
            self.clients.discard(websocket)
    
    async def handle_message(self, websocket, message: str):
        """处理来自客户端的消息"""
        try:
            data = json.loads(message)
            method = data.get('method')
            params = data.get('params', {})
            request_id = data.get('id')
            
            logger.debug(f"收到请求: {method}")
            
            # 路由到相应的处理方法
            if method == 'initialize':
                response = await self.handle_initialize(params)
            elif method == 'textDocument/completion':
                response = await self.handle_completion(params)
            elif method == 'textDocument/hover':
                response = await self.handle_hover(params)
            elif method == 'textDocument/definition':
                response = await self.handle_definition(params)
            elif method == 'textDocument/publishDiagnostics':
                response = await self.handle_diagnostics(params)
            elif method == 'textDocument/formatting':
                response = await self.handle_formatting(params)
            else:
                response = {'error': {'code': -32601, 'message': f'Method not found: {method}'}}
            
            # 发送响应
            if request_id is not None:
                response_message = {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': response
                }
                await websocket.send(json.dumps(response_message))
                
        except json.JSONDecodeError:
            logger.error(f"无效的 JSON 消息: {message}")
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
    
    async def handle_initialize(self, params: Dict) -> Dict:
        """处理初始化请求"""
        return {
            'capabilities': {
                'textDocumentSync': 1,  # Full document sync
                'completionProvider': {
                    'resolveProvider': True,
                    'triggerCharacters': ['.', '(', '[']
                },
                'hoverProvider': True,
                'definitionProvider': True,
                'documentFormattingProvider': True,
                'diagnosticProvider': True
            },
            'serverInfo': {
                'name': 'Python LSP MCP',
                'version': '1.0.0'
            }
        }
    
    async def handle_completion(self, params: Dict) -> Dict:
        """处理代码补全请求"""
        text_document = params.get('textDocument', {})
        position = params.get('position', {})
        
        # 简化的 Python 代码补全
        completions = [
            {
                'label': 'print',
                'kind': 3,  # Function
                'detail': 'print(*values, sep=" ", end="\\n", file=sys.stdout, flush=False)',
                'documentation': 'Print values to stdout',
                'insertText': 'print(${1:value})',
                'insertTextFormat': 2  # Snippet
            },
            {
                'label': 'len',
                'kind': 3,  # Function
                'detail': 'len(obj)',
                'documentation': 'Return the length of an object',
                'insertText': 'len(${1:obj})',
                'insertTextFormat': 2
            },
            {
                'label': 'range',
                'kind': 3,  # Function
                'detail': 'range(stop) or range(start, stop[, step])',
                'documentation': 'Create a range object',
                'insertText': 'range(${1:stop})',
                'insertTextFormat': 2
            },
            {
                'label': 'def',
                'kind': 14,  # Keyword
                'detail': 'def function_name(args):',
                'documentation': 'Define a function',
                'insertText': 'def ${1:function_name}(${2:args}):\\n    ${3:pass}',
                'insertTextFormat': 2
            },
            {
                'label': 'class',
                'kind': 14,  # Keyword
                'detail': 'class ClassName:',
                'documentation': 'Define a class',
                'insertText': 'class ${1:ClassName}:\\n    def __init__(self${2:, args}):\\n        ${3:pass}',
                'insertTextFormat': 2
            },
            {
                'label': 'if',
                'kind': 14,  # Keyword
                'detail': 'if condition:',
                'documentation': 'Conditional statement',
                'insertText': 'if ${1:condition}:\\n    ${2:pass}',
                'insertTextFormat': 2
            },
            {
                'label': 'for',
                'kind': 14,  # Keyword
                'detail': 'for item in iterable:',
                'documentation': 'For loop',
                'insertText': 'for ${1:item} in ${2:iterable}:\\n    ${3:pass}',
                'insertTextFormat': 2
            },
            {
                'label': 'while',
                'kind': 14,  # Keyword
                'detail': 'while condition:',
                'documentation': 'While loop',
                'insertText': 'while ${1:condition}:\\n    ${2:pass}',
                'insertTextFormat': 2
            },
            {
                'label': 'try',
                'kind': 14,  # Keyword
                'detail': 'try-except block',
                'documentation': 'Exception handling',
                'insertText': 'try:\\n    ${1:pass}\\nexcept ${2:Exception} as e:\\n    ${3:pass}',
                'insertTextFormat': 2
            },
            {
                'label': 'import',
                'kind': 9,  # Module
                'detail': 'import module',
                'documentation': 'Import a module',
                'insertText': 'import ${1:module}',
                'insertTextFormat': 2
            },
            {
                'label': 'from',
                'kind': 9,  # Module
                'detail': 'from module import name',
                'documentation': 'Import from a module',
                'insertText': 'from ${1:module} import ${2:name}',
                'insertTextFormat': 2
            }
        ]
        
        return {'items': completions}
    
    async def handle_hover(self, params: Dict) -> Dict:
        """处理悬停信息请求"""
        return {
            'contents': {
                'kind': 'markdown',
                'value': '**Python LSP MCP**\\n\\n提供基础的 Python 语言支持功能'
            }
        }
    
    async def handle_definition(self, params: Dict) -> List[Dict]:
        """处理跳转定义请求"""
        # 简化实现，返回空结果
        return []
    
    async def handle_diagnostics(self, params: Dict) -> Dict:
        """处理诊断信息请求"""
        return {'diagnostics': []}
    
    async def handle_formatting(self, params: Dict) -> List[Dict]:
        """处理代码格式化请求"""
        # 简化实现，返回空的编辑列表
        return []
    
    def stop_server(self):
        """停止服务器"""
        logger.info("正在停止 Python LSP 服务器...")
        self.running = False
        
        if self.lsp_process:
            self.lsp_process.terminate()
            self.lsp_process.wait()
            logger.info("pylsp 进程已停止")

class PythonLSPMCP:
    """
    Python LSP MCP 主类
    集成到 PowerAutomation 系统中
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.lsp_server = PythonLSPServer(port=self.config.get('port', 8081))
        self.running = False
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置"""
        default_config = {
            'port': 8081,
            'host': '0.0.0.0',
            'enable_logging': True,
            'log_level': 'INFO'
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")
        
        return default_config
    
    async def start(self):
        """启动 Python LSP MCP"""
        logger.info("🚀 启动 Python LSP MCP")
        
        try:
            self.running = True
            await self.lsp_server.start_server()
            
        except Exception as e:
            logger.error(f"启动 Python LSP MCP 失败: {e}")
            self.running = False
            raise
    
    def stop(self):
        """停止 Python LSP MCP"""
        logger.info("⏹️ 停止 Python LSP MCP")
        self.running = False
        self.lsp_server.stop_server()
    
    def get_status(self) -> Dict:
        """获取服务状态"""
        return {
            'running': self.running,
            'port': self.config['port'],
            'clients_connected': len(self.lsp_server.clients),
            'lsp_process_running': self.lsp_server.lsp_process is not None and self.lsp_server.lsp_process.poll() is None
        }

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Python LSP MCP Server')
    parser.add_argument('--port', type=int, default=8081, help='WebSocket 服务器端口')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 创建 LSP MCP 实例
    lsp_mcp = PythonLSPMCP(args.config)
    lsp_mcp.config['port'] = args.port
    
    try:
        # 启动服务
        await lsp_mcp.start()
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止服务...")
        lsp_mcp.stop()
    except Exception as e:
        logger.error(f"服务运行时出错: {e}")
        lsp_mcp.stop()
        raise

if __name__ == "__main__":
    # 运行主函数
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n👋 Python LSP MCP 已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

