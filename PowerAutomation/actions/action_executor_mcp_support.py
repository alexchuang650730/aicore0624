    async def _get_tool_executor_mapping(self) -> Dict[str, Callable]:
        """獲取工具執行器映射 - 支持新的MCP組件命名"""
        return {
            # 新的MCP組件
            'general_processor_mcp': self._execute_general_processor_mcp,
            'test_flow_mcp': self._execute_test_flow_mcp,
            'system_monitor_adapter_mcp': self._execute_system_monitor_adapter_mcp,
            'file_processor_adapter_mcp': self._execute_file_processor_adapter_mcp,
            
            # 向後兼容的舊工具名稱
            'default_processor': self._execute_general_processor_mcp,  # 映射到新的General_Processor MCP
            'general_processor': self._execute_general_processor_mcp,  # 映射到新的General_Processor MCP
            'mcp_test_flow_mcp': self._execute_test_flow_mcp,
            'py_system_monitor': self._execute_system_monitor_adapter_mcp,
            'py_file_processor': self._execute_file_processor_adapter_mcp,
            
            # 通用執行器
            'system_monitor': self._execute_system_monitor,
            'file_processor': self._execute_file_processor
        }
    
    async def _execute_general_processor_mcp(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行General_Processor MCP"""
        logger.info("🔄 執行 General_Processor MCP")
        
        try:
            # 導入General_Processor MCP
            from ..components.general_processor_mcp import create_general_processor_mcp
            
            processor = create_general_processor_mcp()
            
            # 準備處理數據
            content = parameters.get('request_content', '')
            context = parameters.get('context', {})
            mode = parameters.get('mode', 'auto')
            
            processing_data = {
                'content': content,
                'context': context,
                'metadata': parameters.get('metadata', {})
            }
            
            # 執行處理
            result = await processor.process(processing_data, mode)
            
            return {
                'success': result.success,
                'output': result.data,
                'mode_used': result.mode_used,
                'execution_time': result.execution_time,
                'metadata': result.metadata,
                'component': 'General_Processor MCP'
            }
            
        except Exception as e:
            logger.error(f"General_Processor MCP執行失敗: {e}")
            return {
                'success': False,
                'error': str(e),
                'component': 'General_Processor MCP',
                'fallback_used': True
            }
    
    async def _execute_test_flow_mcp(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行Test_Flow MCP"""
        logger.info("🧪 執行 Test_Flow MCP")
        
        # 模擬測試流程執行
        test_type = parameters.get('test_type', 'api_test')
        target = parameters.get('target', 'unknown')
        
        await asyncio.sleep(0.5)  # 模擬測試執行時間
        
        return {
            'success': True,
            'test_results': {
                'test_type': test_type,
                'target': target,
                'status': 'passed',
                'test_cases_run': 5,
                'test_cases_passed': 4,
                'test_cases_failed': 1,
                'coverage': '85%'
            },
            'execution_time': 0.5,
            'component': 'Test_Flow MCP'
        }
    
    async def _execute_system_monitor_adapter_mcp(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行SystemMonitor_Adapter MCP"""
        logger.info("📊 執行 SystemMonitor_Adapter MCP")
        
        try:
            import psutil
            
            # 獲取系統資源信息
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'success': True,
                'system_metrics': {
                    'cpu': {
                        'usage_percent': cpu_percent,
                        'core_count': psutil.cpu_count()
                    },
                    'memory': {
                        'usage_percent': memory.percent,
                        'total_gb': round(memory.total / (1024**3), 2),
                        'available_gb': round(memory.available / (1024**3), 2)
                    },
                    'disk': {
                        'usage_percent': round(disk.used / disk.total * 100, 2),
                        'total_gb': round(disk.total / (1024**3), 2),
                        'free_gb': round(disk.free / (1024**3), 2)
                    }
                },
                'timestamp': time.time(),
                'component': 'SystemMonitor_Adapter MCP'
            }
            
        except ImportError:
            # 如果psutil不可用，返回模擬數據
            return {
                'success': True,
                'system_metrics': {
                    'cpu': {'usage_percent': 45.2, 'core_count': 4},
                    'memory': {'usage_percent': 67.8, 'total_gb': 16.0, 'available_gb': 5.2},
                    'disk': {'usage_percent': 23.1, 'total_gb': 500.0, 'free_gb': 384.5}
                },
                'timestamp': time.time(),
                'component': 'SystemMonitor_Adapter MCP',
                'note': 'Using simulated data (psutil not available)'
            }
    
    async def _execute_file_processor_adapter_mcp(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行FileProcessor_Adapter MCP"""
        logger.info("📁 執行 FileProcessor_Adapter MCP")
        
        operation = parameters.get('operation', 'analyze')
        file_path = parameters.get('file_path', '')
        content = parameters.get('content', '')
        
        if operation == 'analyze':
            # 文件分析
            if file_path:
                try:
                    import os
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        file_ext = os.path.splitext(file_path)[1]
                        
                        return {
                            'success': True,
                            'analysis_result': {
                                'file_path': file_path,
                                'file_size_bytes': file_size,
                                'file_extension': file_ext,
                                'file_type': self._detect_file_type(file_ext),
                                'readable': True
                            },
                            'component': 'FileProcessor_Adapter MCP'
                        }
                    else:
                        return {
                            'success': False,
                            'error': f'File not found: {file_path}',
                            'component': 'FileProcessor_Adapter MCP'
                        }
                except Exception as e:
                    return {
                        'success': False,
                        'error': str(e),
                        'component': 'FileProcessor_Adapter MCP'
                    }
            else:
                # 分析內容
                return {
                    'success': True,
                    'analysis_result': {
                        'content_length': len(content),
                        'content_type': 'text',
                        'word_count': len(content.split()) if content else 0,
                        'line_count': len(content.split('\n')) if content else 0
                    },
                    'component': 'FileProcessor_Adapter MCP'
                }
        
        elif operation == 'process':
            # 文件處理
            processed_content = f"Processed: {content[:100]}..." if len(content) > 100 else f"Processed: {content}"
            
            return {
                'success': True,
                'processed_content': processed_content,
                'processing_stats': {
                    'original_length': len(content),
                    'processed_length': len(processed_content),
                    'processing_time': 0.1
                },
                'component': 'FileProcessor_Adapter MCP'
            }
        
        else:
            return {
                'success': False,
                'error': f'Unknown operation: {operation}',
                'component': 'FileProcessor_Adapter MCP'
            }
    
    def _detect_file_type(self, file_extension: str) -> str:
        """檢測文件類型"""
        ext_mapping = {
            '.txt': 'text',
            '.md': 'markdown',
            '.json': 'json',
            '.py': 'python',
            '.js': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.xml': 'xml',
            '.csv': 'csv',
            '.log': 'log'
        }
        return ext_mapping.get(file_extension.lower(), 'unknown')

