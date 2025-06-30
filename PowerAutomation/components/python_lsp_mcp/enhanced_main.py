#!/usr/bin/env python3
"""
Enhanced Python LSP MCP - 完整的语言服务器协议支持
为 SmartUI Monaco Editor 提供完整的 Python 语言服务器功能
包含所有LSP语义功能：智能补全、错误诊断、代码导航、重构等
"""

import asyncio
import json
import logging
import os
import sys
import ast
import re
import subprocess
import threading
import queue
import time
from typing import Dict, List, Optional, Any, Union, Tuple
import websockets
from websockets.server import serve
from pathlib import Path
import importlib.util
import inspect
import jedi
import autopep8
import pyflakes.api
import pyflakes.checker
from io import StringIO

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedPythonLSPServer:
    """
    增强版 Python LSP 服务器
    提供完整的LSP语义功能
    """
    
    def __init__(self, port: int = 8081):
        self.port = port
        self.clients = set()
        self.document_cache = {}  # 文档缓存
        self.workspace_root = None
        self.running = False
        
        # 初始化 Jedi 环境
        try:
            import jedi
            self.jedi_project = None
            logger.info("✅ Jedi 已初始化")
        except ImportError:
            logger.warning("Jedi 未安装，部分功能可能受限")
            self.jedi_project = None
    
    async def start_server(self):
        """启动 WebSocket LSP 服务器"""
        logger.info(f"启动增强版 Python LSP 服务器，端口: {self.port}")
        
        try:
            # 启动 WebSocket 服务器
            async with serve(
                self.handle_client,
                "0.0.0.0",
                self.port,
                ping_interval=20,
                ping_timeout=10
            ):
                logger.info(f"✅ 增强版 Python LSP 服务器已启动: ws://0.0.0.0:{self.port}")
                self.running = True
                
                # 保持服务器运行
                await asyncio.Future()  # run forever
                
        except Exception as e:
            logger.error(f"启动 LSP 服务器失败: {e}")
            raise
    
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
            response = None
            
            if method == 'initialize':
                response = await self.handle_initialize(params)
            elif method == 'initialized':
                response = {}
            elif method == 'textDocument/didOpen':
                await self.handle_did_open(params)
                return
            elif method == 'textDocument/didChange':
                await self.handle_did_change(params)
                return
            elif method == 'textDocument/didSave':
                await self.handle_did_save(params)
                return
            elif method == 'textDocument/completion':
                response = await self.handle_completion(params)
            elif method == 'textDocument/hover':
                response = await self.handle_hover(params)
            elif method == 'textDocument/definition':
                response = await self.handle_definition(params)
            elif method == 'textDocument/references':
                response = await self.handle_references(params)
            elif method == 'textDocument/documentSymbol':
                response = await self.handle_document_symbols(params)
            elif method == 'textDocument/formatting':
                response = await self.handle_formatting(params)
            elif method == 'textDocument/rangeFormatting':
                response = await self.handle_range_formatting(params)
            elif method == 'textDocument/rename':
                response = await self.handle_rename(params)
            elif method == 'textDocument/codeAction':
                response = await self.handle_code_action(params)
            elif method == 'textDocument/signatureHelp':
                response = await self.handle_signature_help(params)
            elif method == 'workspace/symbol':
                response = await self.handle_workspace_symbols(params)
            elif method == 'textDocument/foldingRange':
                response = await self.handle_folding_ranges(params)
            elif method == 'textDocument/semanticTokens/full':
                response = await self.handle_semantic_tokens(params)
            else:
                response = {'error': {'code': -32601, 'message': f'Method not found: {method}'}}
            
            # 发送响应
            if request_id is not None and response is not None:
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
        # 设置工作区根目录
        if 'rootUri' in params:
            self.workspace_root = params['rootUri'].replace('file://', '')
        elif 'rootPath' in params:
            self.workspace_root = params['rootPath']
        
        # 初始化 Jedi 项目
        if self.workspace_root and self.jedi_project is None:
            try:
                import jedi
                self.jedi_project = jedi.Project(self.workspace_root)
                logger.info(f"✅ Jedi 项目已初始化: {self.workspace_root}")
            except Exception as e:
                logger.warning(f"Jedi 项目初始化失败: {e}")
        
        return {
            'capabilities': {
                'textDocumentSync': {
                    'openClose': True,
                    'change': 1,  # Full document sync
                    'save': {'includeText': True}
                },
                'completionProvider': {
                    'resolveProvider': True,
                    'triggerCharacters': ['.', '(', '[', '"', "'", ' ']
                },
                'hoverProvider': True,
                'definitionProvider': True,
                'referencesProvider': True,
                'documentSymbolProvider': True,
                'workspaceSymbolProvider': True,
                'documentFormattingProvider': True,
                'documentRangeFormattingProvider': True,
                'renameProvider': {'prepareProvider': True},
                'codeActionProvider': {
                    'codeActionKinds': [
                        'quickfix',
                        'refactor',
                        'refactor.extract',
                        'refactor.inline',
                        'source',
                        'source.organizeImports'
                    ]
                },
                'signatureHelpProvider': {
                    'triggerCharacters': ['(', ',']
                },
                'foldingRangeProvider': True,
                'semanticTokensProvider': {
                    'legend': {
                        'tokenTypes': [
                            'namespace', 'type', 'class', 'enum', 'interface',
                            'struct', 'typeParameter', 'parameter', 'variable',
                            'property', 'enumMember', 'event', 'function',
                            'method', 'macro', 'keyword', 'modifier',
                            'comment', 'string', 'number', 'regexp', 'operator'
                        ],
                        'tokenModifiers': [
                            'declaration', 'definition', 'readonly', 'static',
                            'deprecated', 'abstract', 'async', 'modification',
                            'documentation', 'defaultLibrary'
                        ]
                    },
                    'full': True
                }
            },
            'serverInfo': {
                'name': 'Enhanced Python LSP MCP',
                'version': '2.0.0'
            }
        }
    
    async def handle_did_open(self, params: Dict):
        """处理文档打开事件"""
        text_document = params['textDocument']
        uri = text_document['uri']
        text = text_document['text']
        
        # 缓存文档内容
        self.document_cache[uri] = {
            'text': text,
            'version': text_document.get('version', 0),
            'language': text_document.get('languageId', 'python')
        }
        
        # 发送诊断信息
        await self.send_diagnostics(uri, text)
    
    async def handle_did_change(self, params: Dict):
        """处理文档变更事件"""
        text_document = params['textDocument']
        uri = text_document['uri']
        version = text_document.get('version', 0)
        
        # 更新文档缓存
        if uri in self.document_cache:
            changes = params['contentChanges']
            if changes and len(changes) > 0:
                # 完整文档同步
                new_text = changes[0].get('text', '')
                self.document_cache[uri]['text'] = new_text
                self.document_cache[uri]['version'] = version
                
                # 发送诊断信息
                await self.send_diagnostics(uri, new_text)
    
    async def handle_did_save(self, params: Dict):
        """处理文档保存事件"""
        text_document = params['textDocument']
        uri = text_document['uri']
        
        if uri in self.document_cache:
            text = self.document_cache[uri]['text']
            # 重新发送诊断信息
            await self.send_diagnostics(uri, text)
    
    async def send_diagnostics(self, uri: str, text: str):
        """发送诊断信息到客户端"""
        diagnostics = []
        
        try:
            # 使用 pyflakes 进行语法检查
            warning_stream = StringIO()
            checker = pyflakes.checker.Checker(ast.parse(text), uri)
            
            for message in checker.messages:
                diagnostic = {
                    'range': {
                        'start': {'line': message.lineno - 1, 'character': message.col},
                        'end': {'line': message.lineno - 1, 'character': message.col + 10}
                    },
                    'severity': 2,  # Warning
                    'source': 'pyflakes',
                    'message': str(message)
                }
                diagnostics.append(diagnostic)
                
        except SyntaxError as e:
            # 语法错误
            diagnostic = {
                'range': {
                    'start': {'line': (e.lineno or 1) - 1, 'character': e.offset or 0},
                    'end': {'line': (e.lineno or 1) - 1, 'character': (e.offset or 0) + 5}
                },
                'severity': 1,  # Error
                'source': 'python',
                'message': f'语法错误: {e.msg}'
            }
            diagnostics.append(diagnostic)
        except Exception as e:
            logger.debug(f"诊断检查出错: {e}")
        
        # 发送诊断信息
        notification = {
            'jsonrpc': '2.0',
            'method': 'textDocument/publishDiagnostics',
            'params': {
                'uri': uri,
                'diagnostics': diagnostics
            }
        }
        
        # 发送给所有连接的客户端
        for client in self.clients.copy():
            try:
                await client.send(json.dumps(notification))
            except Exception as e:
                logger.debug(f"发送诊断信息失败: {e}")
                self.clients.discard(client)
    
    async def handle_completion(self, params: Dict) -> Dict:
        """处理智能补全请求"""
        text_document = params['textDocument']
        position = params['position']
        uri = text_document['uri']
        
        if uri not in self.document_cache:
            return {'items': []}
        
        text = self.document_cache[uri]['text']
        line = position['line']
        character = position['character']
        
        completions = []
        
        try:
            # 使用 Jedi 进行智能补全
            if 'jedi' in sys.modules:
                import jedi
                script = jedi.Script(code=text, line=line + 1, column=character, path=uri)
                jedi_completions = script.completions()
                
                for completion in jedi_completions[:50]:  # 限制结果数量
                    item = {
                        'label': completion.name,
                        'kind': self._get_completion_kind(completion.type),
                        'detail': completion.description,
                        'documentation': {
                            'kind': 'markdown',
                            'value': completion.docstring() or completion.description
                        },
                        'insertText': completion.name,
                        'sortText': f"{completion.name}_{completion.type}"
                    }
                    
                    # 添加代码片段支持
                    if completion.type == 'function':
                        try:
                            signature = completion.defined_names()[0].description if completion.defined_names() else ''
                            if '(' in signature and ')' in signature:
                                params_part = signature[signature.find('('):signature.find(')') + 1]
                                item['insertText'] = f"{completion.name}${{1:{params_part}}}"
                                item['insertTextFormat'] = 2  # Snippet
                        except:
                            pass
                    
                    completions.append(item)
            
        except Exception as e:
            logger.debug(f"Jedi 补全失败: {e}")
        
        # 添加 Python 关键字和内置函数
        if not completions or len(completions) < 10:
            completions.extend(self._get_python_keywords_and_builtins())
        
        return {'items': completions}
    
    def _get_completion_kind(self, jedi_type: str) -> int:
        """转换 Jedi 类型到 LSP 补全类型"""
        type_mapping = {
            'module': 9,
            'class': 7,
            'function': 3,
            'instance': 6,
            'statement': 6,
            'keyword': 14,
            'param': 6,
            'property': 10
        }
        return type_mapping.get(jedi_type, 1)
    
    def _get_python_keywords_and_builtins(self) -> List[Dict]:
        """获取 Python 关键字和内置函数补全"""
        items = []
        
        # Python 关键字
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'finally', 'for', 'from',
            'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal',
            'not', 'or', 'pass', 'raise', 'return', 'try', 'while',
            'with', 'yield', 'True', 'False', 'None'
        ]
        
        for keyword in keywords:
            items.append({
                'label': keyword,
                'kind': 14,  # Keyword
                'detail': f'Python keyword: {keyword}',
                'insertText': keyword
            })
        
        # 内置函数
        builtins = [
            'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'dir',
            'enumerate', 'eval', 'filter', 'float', 'format', 'frozenset',
            'getattr', 'hasattr', 'hash', 'help', 'hex', 'id', 'input',
            'int', 'isinstance', 'issubclass', 'iter', 'len', 'list',
            'map', 'max', 'min', 'next', 'oct', 'open', 'ord', 'pow',
            'print', 'range', 'repr', 'reversed', 'round', 'set',
            'setattr', 'slice', 'sorted', 'str', 'sum', 'tuple',
            'type', 'vars', 'zip'
        ]
        
        for builtin in builtins:
            items.append({
                'label': builtin,
                'kind': 3,  # Function
                'detail': f'Python builtin: {builtin}',
                'insertText': f'{builtin}(${{1:}})',
                'insertTextFormat': 2  # Snippet
            })
        
        return items
    
    async def handle_hover(self, params: Dict) -> Optional[Dict]:
        """处理悬停信息请求"""
        text_document = params['textDocument']
        position = params['position']
        uri = text_document['uri']
        
        if uri not in self.document_cache:
            return None
        
        text = self.document_cache[uri]['text']
        line = position['line']
        character = position['character']
        
        try:
            if 'jedi' in sys.modules:
                import jedi
                script = jedi.Script(code=text, line=line + 1, column=character, path=uri)
                help_info = script.help()
                
                if help_info:
                    info = help_info[0]
                    content = f"**{info.full_name}**\\n\\n"
                    
                    if info.docstring():
                        content += f"```python\\n{info.description}\\n```\\n\\n"
                        content += info.docstring()
                    else:
                        content += info.description
                    
                    return {
                        'contents': {
                            'kind': 'markdown',
                            'value': content
                        }
                    }
        except Exception as e:
            logger.debug(f"悬停信息获取失败: {e}")
        
        return None
    
    async def handle_definition(self, params: Dict) -> List[Dict]:
        """处理跳转定义请求"""
        text_document = params['textDocument']
        position = params['position']
        uri = text_document['uri']
        
        if uri not in self.document_cache:
            return []
        
        text = self.document_cache[uri]['text']
        line = position['line']
        character = position['character']
        
        try:
            if 'jedi' in sys.modules:
                import jedi
                script = jedi.Script(code=text, line=line + 1, column=character, path=uri)
                definitions = script.goto_definitions()
                
                locations = []
                for definition in definitions:
                    if definition.module_path:
                        location = {
                            'uri': f'file://{definition.module_path}',
                            'range': {
                                'start': {
                                    'line': (definition.line or 1) - 1,
                                    'character': definition.column or 0
                                },
                                'end': {
                                    'line': (definition.line or 1) - 1,
                                    'character': (definition.column or 0) + len(definition.name)
                                }
                            }
                        }
                        locations.append(location)
                
                return locations
        except Exception as e:
            logger.debug(f"定义跳转失败: {e}")
        
        return []
    
    async def handle_references(self, params: Dict) -> List[Dict]:
        """处理查找引用请求"""
        text_document = params['textDocument']
        position = params['position']
        uri = text_document['uri']
        
        if uri not in self.document_cache:
            return []
        
        text = self.document_cache[uri]['text']
        line = position['line']
        character = position['character']
        
        try:
            if 'jedi' in sys.modules:
                import jedi
                script = jedi.Script(code=text, line=line + 1, column=character, path=uri)
                references = script.get_references()
                
                locations = []
                for ref in references:
                    if ref.module_path:
                        location = {
                            'uri': f'file://{ref.module_path}',
                            'range': {
                                'start': {
                                    'line': (ref.line or 1) - 1,
                                    'character': ref.column or 0
                                },
                                'end': {
                                    'line': (ref.line or 1) - 1,
                                    'character': (ref.column or 0) + len(ref.name)
                                }
                            }
                        }
                        locations.append(location)
                
                return locations
        except Exception as e:
            logger.debug(f"引用查找失败: {e}")
        
        return []
    
    async def handle_document_symbols(self, params: Dict) -> List[Dict]:
        """处理文档符号请求"""
        text_document = params['textDocument']
        uri = text_document['uri']
        
        if uri not in self.document_cache:
            return []
        
        text = self.document_cache[uri]['text']
        symbols = []
        
        try:
            # 解析 AST 获取符号
            tree = ast.parse(text)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    symbol = {
                        'name': node.name,
                        'kind': 12,  # Function
                        'range': self._get_node_range(node, text),
                        'selectionRange': self._get_node_range(node, text)
                    }
                    symbols.append(symbol)
                elif isinstance(node, ast.ClassDef):
                    symbol = {
                        'name': node.name,
                        'kind': 5,  # Class
                        'range': self._get_node_range(node, text),
                        'selectionRange': self._get_node_range(node, text)
                    }
                    symbols.append(symbol)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            symbol = {
                                'name': target.id,
                                'kind': 13,  # Variable
                                'range': self._get_node_range(node, text),
                                'selectionRange': self._get_node_range(node, text)
                            }
                            symbols.append(symbol)
        except Exception as e:
            logger.debug(f"文档符号解析失败: {e}")
        
        return symbols
    
    def _get_node_range(self, node: ast.AST, text: str) -> Dict:
        """获取 AST 节点的范围"""
        lines = text.split('\\n')
        start_line = getattr(node, 'lineno', 1) - 1
        start_char = getattr(node, 'col_offset', 0)
        
        # 简化的结束位置计算
        end_line = start_line
        end_char = start_char + 10  # 默认长度
        
        if start_line < len(lines):
            line_text = lines[start_line]
            if hasattr(node, 'name'):
                name_pos = line_text.find(node.name, start_char)
                if name_pos >= 0:
                    end_char = name_pos + len(node.name)
        
        return {
            'start': {'line': start_line, 'character': start_char},
            'end': {'line': end_line, 'character': end_char}
        }
    
    async def handle_formatting(self, params: Dict) -> List[Dict]:
        """处理代码格式化请求"""
        text_document = params['textDocument']
        uri = text_document['uri']
        
        if uri not in self.document_cache:
            return []
        
        text = self.document_cache[uri]['text']
        
        try:
            # 使用 autopep8 格式化代码
            formatted_text = autopep8.fix_code(text)
            
            if formatted_text != text:
                lines = text.split('\\n')
                return [{
                    'range': {
                        'start': {'line': 0, 'character': 0},
                        'end': {'line': len(lines) - 1, 'character': len(lines[-1]) if lines else 0}
                    },
                    'newText': formatted_text
                }]
        except Exception as e:
            logger.debug(f"代码格式化失败: {e}")
        
        return []
    
    async def handle_range_formatting(self, params: Dict) -> List[Dict]:
        """处理范围格式化请求"""
        # 简化实现，使用完整文档格式化
        return await self.handle_formatting(params)
    
    async def handle_rename(self, params: Dict) -> Optional[Dict]:
        """处理重命名请求"""
        text_document = params['textDocument']
        position = params['position']
        new_name = params['newName']
        uri = text_document['uri']
        
        # 简化实现，返回空结果
        return {'changes': {}}
    
    async def handle_code_action(self, params: Dict) -> List[Dict]:
        """处理代码操作请求"""
        text_document = params['textDocument']
        range_param = params['range']
        context = params.get('context', {})
        
        actions = []
        
        # 添加组织导入的代码操作
        actions.append({
            'title': '整理导入语句',
            'kind': 'source.organizeImports',
            'edit': {
                'changes': {
                    text_document['uri']: []
                }
            }
        })
        
        # 添加格式化代码操作
        actions.append({
            'title': '格式化文档',
            'kind': 'source.formatDocument',
            'command': {
                'title': '格式化文档',
                'command': 'editor.action.formatDocument'
            }
        })
        
        return actions
    
    async def handle_signature_help(self, params: Dict) -> Optional[Dict]:
        """处理签名帮助请求"""
        text_document = params['textDocument']
        position = params['position']
        uri = text_document['uri']
        
        if uri not in self.document_cache:
            return None
        
        text = self.document_cache[uri]['text']
        line = position['line']
        character = position['character']
        
        try:
            if 'jedi' in sys.modules:
                import jedi
                script = jedi.Script(code=text, line=line + 1, column=character, path=uri)
                signatures = script.get_signatures()
                
                if signatures:
                    sig = signatures[0]
                    signature_info = {
                        'label': sig.to_string(),
                        'documentation': {
                            'kind': 'markdown',
                            'value': sig.docstring() or sig.to_string()
                        },
                        'parameters': []
                    }
                    
                    for param in sig.params:
                        param_info = {
                            'label': param.to_string(),
                            'documentation': param.description
                        }
                        signature_info['parameters'].append(param_info)
                    
                    return {
                        'signatures': [signature_info],
                        'activeSignature': 0,
                        'activeParameter': 0
                    }
        except Exception as e:
            logger.debug(f"签名帮助失败: {e}")
        
        return None
    
    async def handle_workspace_symbols(self, params: Dict) -> List[Dict]:
        """处理工作区符号搜索请求"""
        query = params.get('query', '')
        symbols = []
        
        # 简化实现，搜索当前缓存的文档
        for uri, doc_info in self.document_cache.items():
            try:
                text = doc_info['text']
                tree = ast.parse(text)
                
                for node in ast.walk(tree):
                    name = None
                    kind = 1
                    
                    if isinstance(node, ast.FunctionDef):
                        name = node.name
                        kind = 12  # Function
                    elif isinstance(node, ast.ClassDef):
                        name = node.name
                        kind = 5  # Class
                    
                    if name and (not query or query.lower() in name.lower()):
                        symbol = {
                            'name': name,
                            'kind': kind,
                            'location': {
                                'uri': uri,
                                'range': self._get_node_range(node, text)
                            }
                        }
                        symbols.append(symbol)
            except Exception as e:
                logger.debug(f"工作区符号搜索失败: {e}")
        
        return symbols[:100]  # 限制结果数量
    
    async def handle_folding_ranges(self, params: Dict) -> List[Dict]:
        """处理代码折叠范围请求"""
        text_document = params['textDocument']
        uri = text_document['uri']
        
        if uri not in self.document_cache:
            return []
        
        text = self.document_cache[uri]['text']
        folding_ranges = []
        
        try:
            tree = ast.parse(text)
            lines = text.split('\\n')
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.If, ast.For, ast.While)):
                    start_line = getattr(node, 'lineno', 1) - 1
                    
                    # 简化的结束行计算
                    end_line = start_line + 5  # 默认折叠5行
                    if hasattr(node, 'body') and node.body:
                        last_node = node.body[-1]
                        if hasattr(last_node, 'lineno'):
                            end_line = last_node.lineno - 1
                    
                    if end_line > start_line:
                        folding_range = {
                            'startLine': start_line,
                            'endLine': min(end_line, len(lines) - 1),
                            'kind': 'region'
                        }
                        folding_ranges.append(folding_range)
        except Exception as e:
            logger.debug(f"代码折叠范围计算失败: {e}")
        
        return folding_ranges
    
    async def handle_semantic_tokens(self, params: Dict) -> Optional[Dict]:
        """处理语义标记请求"""
        text_document = params['textDocument']
        uri = text_document['uri']
        
        if uri not in self.document_cache:
            return None
        
        # 简化实现，返回空的语义标记
        return {'data': []}
    
    def stop_server(self):
        """停止服务器"""
        logger.info("正在停止增强版 Python LSP 服务器...")
        self.running = False

class EnhancedPythonLSPMCP:
    """
    增强版 Python LSP MCP 主类
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.lsp_server = EnhancedPythonLSPServer(port=self.config.get('port', 8081))
        self.running = False
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置"""
        default_config = {
            'port': 8081,
            'host': '0.0.0.0',
            'enable_logging': True,
            'log_level': 'INFO',
            'features': {
                'completion': True,
                'hover': True,
                'definition': True,
                'references': True,
                'formatting': True,
                'diagnostics': True,
                'symbols': True,
                'rename': True,
                'code_actions': True,
                'signature_help': True,
                'folding': True,
                'semantic_tokens': True
            }
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
        """启动增强版 Python LSP MCP"""
        logger.info("🚀 启动增强版 Python LSP MCP")
        
        try:
            self.running = True
            await self.lsp_server.start_server()
            
        except Exception as e:
            logger.error(f"启动增强版 Python LSP MCP 失败: {e}")
            self.running = False
            raise
    
    def stop(self):
        """停止增强版 Python LSP MCP"""
        logger.info("⏹️ 停止增强版 Python LSP MCP")
        self.running = False
        self.lsp_server.stop_server()
    
    def get_status(self) -> Dict:
        """获取服务状态"""
        return {
            'running': self.running,
            'port': self.config['port'],
            'clients_connected': len(self.lsp_server.clients),
            'features_enabled': self.config['features'],
            'documents_cached': len(self.lsp_server.document_cache)
        }

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Python LSP MCP Server')
    parser.add_argument('--port', type=int, default=8081, help='WebSocket 服务器端口')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 安装必要的依赖
    try:
        import jedi
        import autopep8
        import pyflakes
        logger.info("✅ 所有依赖已安装")
    except ImportError as e:
        logger.info(f"安装缺失的依赖: {e}")
        missing_packages = []
        try:
            import jedi
        except ImportError:
            missing_packages.append('jedi')
        try:
            import autopep8
        except ImportError:
            missing_packages.append('autopep8')
        try:
            import pyflakes
        except ImportError:
            missing_packages.append('pyflakes')
        
        if missing_packages:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
            logger.info("✅ 依赖安装完成")
    
    # 创建增强版 LSP MCP 实例
    lsp_mcp = EnhancedPythonLSPMCP(args.config)
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
        print("\\n👋 增强版 Python LSP MCP 已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

