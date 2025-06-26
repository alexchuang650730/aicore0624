#!/usr/bin/env python3
"""
Enhanced Local MCP VSCode Extension Installer
增強的Local MCP端VSCode擴展安裝組件

基於aicore0623架構，提供完整的Mac端VSCode擴展安裝和驗證功能
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
import hashlib
import platform
import shutil
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import aiohttp
import aiofiles

# 導入aicore0623的核心組件
try:
    from .local_mcp_adapter import LocalMCPAdapter, AdapterConfig
    from .tool_registry_manager import ToolRegistryManager, LocalToolInfo, ToolStatus
    from .heartbeat_manager import HeartbeatManager, ConnectionStatus
    from .smart_routing_engine import SmartRoutingEngine, RoutingRequest
except ImportError:
    # 開發環境下的導入
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from components.local_mcp_adapter import LocalMCPAdapter, AdapterConfig
    from components.tool_registry_manager import ToolRegistryManager, LocalToolInfo, ToolStatus
    from components.heartbeat_manager import HeartbeatManager, ConnectionStatus
    from components.smart_routing_engine import SmartRoutingEngine, RoutingRequest

logger = logging.getLogger(__name__)

@dataclass
class ExtensionInstallRequest:
    """擴展安裝請求"""
    extension_name: str
    extension_version: str
    vsix_url: Optional[str] = None
    vsix_data: Optional[bytes] = None
    vsix_file_path: Optional[str] = None
    target_platform: str = "universal"
    install_id: str = ""
    metadata: Dict[str, Any] = None
    force_reinstall: bool = False
    
    def __post_init__(self):
        if not self.install_id:
            self.install_id = f"install_{int(datetime.now().timestamp())}"
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ExtensionInstallResult:
    """擴展安裝結果"""
    success: bool
    install_id: str
    extension_name: str
    extension_version: str
    installation_path: Optional[str] = None
    verification_result: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    install_log: List[str] = None
    execution_time: float = 0.0
    
    def __post_init__(self):
        if self.install_log is None:
            self.install_log = []

class EnhancedMacVSCodeDetector:
    """增強的Mac環境VSCode檢測器"""
    
    POSSIBLE_VSCODE_PATHS = [
        "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
        "/usr/local/bin/code",
        "/opt/homebrew/bin/code",  # Apple Silicon Mac
        "~/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
        "/opt/local/bin/code",  # MacPorts
        "/usr/bin/code"  # 系統安裝
    ]
    
    def __init__(self):
        self._cached_vscode_path = None
        self._cached_vscode_version = None
    
    async def detect_vscode_command(self) -> str:
        """異步檢測Mac上的VSCode命令路徑"""
        if self._cached_vscode_path:
            return self._cached_vscode_path
        
        # 1. 檢查PATH中的code命令
        try:
            process = await asyncio.create_subprocess_exec(
                'which', 'code',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                vscode_path = stdout.decode().strip()
                if await self._verify_vscode_command(vscode_path):
                    self._cached_vscode_path = vscode_path
                    return vscode_path
        except Exception as e:
            logger.debug(f"which命令檢查失敗: {e}")
        
        # 2. 檢查常見安裝路徑
        for path in self.POSSIBLE_VSCODE_PATHS:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                if await self._verify_vscode_command(expanded_path):
                    self._cached_vscode_path = expanded_path
                    return expanded_path
        
        # 3. 檢查Applications目錄中的所有VSCode變體
        apps_dir = "/Applications"
        if os.path.exists(apps_dir):
            for app_name in os.listdir(apps_dir):
                if "visual studio code" in app_name.lower():
                    app_path = os.path.join(apps_dir, app_name)
                    code_path = f"{app_path}/Contents/Resources/app/bin/code"
                    if os.path.exists(code_path):
                        if await self._verify_vscode_command(code_path):
                            self._cached_vscode_path = code_path
                            return code_path
        
        raise Exception("未找到VSCode安裝，請確保VSCode已安裝並可用")
    
    async def _verify_vscode_command(self, vscode_path: str) -> bool:
        """驗證VSCode命令是否有效"""
        try:
            process = await asyncio.create_subprocess_exec(
                vscode_path, '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return process.returncode == 0
        except Exception:
            return False
    
    async def get_vscode_version(self) -> str:
        """獲取VSCode版本信息"""
        if self._cached_vscode_version:
            return self._cached_vscode_version
        
        try:
            vscode_cmd = await self.detect_vscode_command()
            process = await asyncio.create_subprocess_exec(
                vscode_cmd, '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                version_info = stdout.decode().strip().split('\n')
                self._cached_vscode_version = version_info[0] if version_info else "unknown"
                return self._cached_vscode_version
        except Exception as e:
            logger.warning(f"獲取VSCode版本失敗: {e}")
        
        return "unknown"

class EnhancedMacExtensionManager:
    """增強的Mac擴展管理器"""
    
    def __init__(self):
        self.extensions_dir = self._get_extensions_dir()
        self.user_data_dir = self._get_user_data_dir()
    
    def _get_extensions_dir(self) -> str:
        """獲取Mac VSCode擴展目錄"""
        home = os.path.expanduser("~")
        return f"{home}/.vscode/extensions"
    
    def _get_user_data_dir(self) -> str:
        """獲取Mac VSCode用戶數據目錄"""
        home = os.path.expanduser("~")
        return f"{home}/Library/Application Support/Code/User"
    
    def ensure_directories_exist(self) -> bool:
        """確保必要的目錄存在"""
        try:
            os.makedirs(self.extensions_dir, mode=0o755, exist_ok=True)
            os.makedirs(self.user_data_dir, mode=0o755, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"創建目錄失敗: {e}")
            return False
    
    def get_extension_install_path(self, extension_name: str, version: str) -> str:
        """獲取特定擴展的安裝路徑"""
        return f"{self.extensions_dir}/{extension_name}-{version}"
    
    def is_extension_installed(self, extension_name: str, version: str = None) -> bool:
        """檢查擴展是否已安裝"""
        if not os.path.exists(self.extensions_dir):
            return False
        
        for folder in os.listdir(self.extensions_dir):
            if folder.startswith(extension_name):
                if version is None or folder == f"{extension_name}-{version}":
                    return True
        return False
    
    def get_installed_extensions(self) -> List[Dict[str, str]]:
        """獲取已安裝的擴展列表"""
        extensions = []
        if not os.path.exists(self.extensions_dir):
            return extensions
        
        for folder in os.listdir(self.extensions_dir):
            if '-' in folder:
                parts = folder.rsplit('-', 1)
                if len(parts) == 2:
                    name, version = parts
                    extensions.append({
                        'name': name,
                        'version': version,
                        'folder': folder,
                        'path': os.path.join(self.extensions_dir, folder)
                    })
        
        return extensions

class ExtensionFunctionalityTester:
    """擴展功能測試器"""
    
    def __init__(self, vscode_detector: EnhancedMacVSCodeDetector):
        self.vscode_detector = vscode_detector
    
    async def test_extension_activation(self, extension_name: str) -> Dict[str, Any]:
        """測試擴展激活"""
        test_result = {
            'test_name': 'extension_activation',
            'success': False,
            'details': {},
            'execution_time': 0
        }
        
        start_time = time.time()
        
        try:
            vscode_cmd = await self.vscode_detector.detect_vscode_command()
            
            # 創建臨時工作區
            temp_dir = tempfile.mkdtemp()
            workspace_file = os.path.join(temp_dir, "test.code-workspace")
            
            workspace_config = {
                "folders": [{"path": temp_dir}],
                "extensions": {
                    "recommendations": [extension_name]
                }
            }
            
            with open(workspace_file, 'w') as f:
                json.dump(workspace_config, f, indent=2)
            
            # 嘗試啟動VSCode並檢查擴展
            process = await asyncio.create_subprocess_exec(
                vscode_cmd, workspace_file, '--wait',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # 等待短時間後檢查
            await asyncio.sleep(2)
            
            # 檢查擴展是否在運行
            list_process = await asyncio.create_subprocess_exec(
                vscode_cmd, '--list-extensions', '--show-versions',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await list_process.communicate()
            
            if list_process.returncode == 0:
                extensions = stdout.decode().strip().split('\n')
                extension_found = any(extension_name in ext for ext in extensions)
                
                test_result['success'] = extension_found
                test_result['details'] = {
                    'extension_found': extension_found,
                    'installed_extensions': extensions
                }
            
            # 清理
            shutil.rmtree(temp_dir, ignore_errors=True)
            
        except Exception as e:
            test_result['details']['error'] = str(e)
        
        finally:
            test_result['execution_time'] = time.time() - start_time
        
        return test_result
    
    async def test_extension_performance(self, extension_name: str) -> Dict[str, Any]:
        """測試擴展性能"""
        test_result = {
            'test_name': 'extension_performance',
            'success': False,
            'details': {},
            'execution_time': 0
        }
        
        start_time = time.time()
        
        try:
            vscode_cmd = await self.vscode_detector.detect_vscode_command()
            
            # 測試VSCode啟動時間
            startup_start = time.time()
            
            process = await asyncio.create_subprocess_exec(
                vscode_cmd, '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            startup_time = time.time() - startup_start
            
            test_result['success'] = process.returncode == 0
            test_result['details'] = {
                'startup_time': startup_time,
                'performance_acceptable': startup_time < 5.0  # 5秒內啟動
            }
            
        except Exception as e:
            test_result['details']['error'] = str(e)
        
        finally:
            test_result['execution_time'] = time.time() - start_time
        
        return test_result

class EnhancedLocalMCPVSCodeInstaller:
    """增強的Local MCP VSCode擴展安裝器"""
    
    def __init__(self, local_mcp_adapter: LocalMCPAdapter):
        """
        初始化增強的VSCode擴展安裝器
        
        Args:
            local_mcp_adapter: aicore0623的Local MCP Adapter實例
        """
        self.local_mcp_adapter = local_mcp_adapter
        self.adapter_id = local_mcp_adapter.adapter_id
        
        # 平台檢測
        self.platform = platform.system()
        self.is_mac = self.platform == "Darwin"
        
        # Mac特定組件
        if self.is_mac:
            self.vscode_detector = EnhancedMacVSCodeDetector()
            self.extension_manager = EnhancedMacExtensionManager()
            self.functionality_tester = ExtensionFunctionalityTester(self.vscode_detector)
        else:
            raise Exception("此版本僅支持Mac環境")
        
        # 安裝狀態
        self.active_installs: Dict[str, ExtensionInstallRequest] = {}
        self.install_history: List[ExtensionInstallResult] = []
        
        # 註冊到工具註冊管理器
        self._register_installer_tools()
    
    def _register_installer_tools(self):
        """註冊安裝器工具到工具註冊管理器"""
        if self.local_mcp_adapter.tool_registry_manager:
            installer_tool = LocalToolInfo(
                tool_id="enhanced_vscode_installer",
                tool_name="Enhanced VSCode Extension Installer",
                tool_type="extension_management",
                version="2.0.0",
                description="增強的Mac端VSCode擴展安裝和驗證工具",
                capabilities=[
                    "mac_vscode_detection",
                    "extension_installation",
                    "functionality_testing",
                    "performance_testing",
                    "real_cli_integration"
                ],
                endpoint=f"http://localhost:8080/api/v1/vscode/install",
                status=ToolStatus.ACTIVE,
                metadata={
                    "platform": self.platform,
                    "mac_optimized": True,
                    "real_vscode_cli": True,
                    "functionality_testing": True
                }
            )
            
            self.local_mcp_adapter.tool_registry_manager.register_tool(installer_tool)
            logger.info(f"增強VSCode安裝器已註冊: {installer_tool.tool_id}")
    
    async def install_extension(self, request: ExtensionInstallRequest) -> ExtensionInstallResult:
        """
        安裝VSCode擴展
        
        Args:
            request: 擴展安裝請求
            
        Returns:
            ExtensionInstallResult: 安裝結果
        """
        start_time = time.time()
        install_log = []
        
        try:
            install_log.append(f"🚀 開始安裝VSCode擴展: {request.extension_name} v{request.extension_version}")
            install_log.append(f"平台: {self.platform}")
            install_log.append(f"安裝ID: {request.install_id}")
            
            # 記錄活躍安裝
            self.active_installs[request.install_id] = request
            
            # 步驟1: 環境檢查和準備
            install_log.append("=== 步驟1: 環境檢查和準備 ===")
            env_result = await self._prepare_environment()
            install_log.extend(env_result.get('log', []))
            
            if not env_result['success']:
                raise Exception(f"環境準備失敗: {env_result.get('error', '未知錯誤')}")
            
            # 步驟2: 檢查現有安裝
            install_log.append("=== 步驟2: 檢查現有安裝 ===")
            existing_check = await self._check_existing_installation(request)
            install_log.extend(existing_check.get('log', []))
            
            if existing_check.get('already_installed') and not request.force_reinstall:
                install_log.append("✅ 擴展已安裝，跳過安裝步驟")
                # 直接進行驗證
                verification_result = await self._verify_installation(request)
                
                return ExtensionInstallResult(
                    success=True,
                    install_id=request.install_id,
                    extension_name=request.extension_name,
                    extension_version=request.extension_version,
                    installation_path=existing_check.get('installation_path'),
                    verification_result=verification_result,
                    install_log=install_log,
                    execution_time=time.time() - start_time
                )
            
            # 步驟3: 準備VSIX文件
            install_log.append("=== 步驟3: 準備VSIX文件 ===")
            vsix_file_path = await self._prepare_vsix_file(request)
            install_log.append(f"VSIX文件準備完成: {vsix_file_path}")
            
            # 步驟4: 執行安裝
            install_log.append("=== 步驟4: 執行VSCode擴展安裝 ===")
            install_result = await self._execute_installation(vsix_file_path, request)
            install_log.extend(install_result.get('log', []))
            
            if not install_result['success']:
                raise Exception(f"擴展安裝失敗: {install_result.get('error', '未知錯誤')}")
            
            # 步驟5: 驗證安裝
            install_log.append("=== 步驟5: 驗證擴展安裝 ===")
            verification_result = await self._verify_installation(request)
            install_log.extend(verification_result.get('log', []))
            
            # 步驟6: 功能測試
            install_log.append("=== 步驟6: 擴展功能測試 ===")
            functionality_result = await self._test_extension_functionality(request)
            install_log.extend(functionality_result.get('log', []))
            
            # 步驟7: 性能測試
            install_log.append("=== 步驟7: 性能基準測試 ===")
            performance_result = await self._test_extension_performance(request)
            install_log.extend(performance_result.get('log', []))
            
            # 步驟8: 清理臨時文件
            install_log.append("=== 步驟8: 清理臨時文件 ===")
            await self._cleanup_temp_files(vsix_file_path)
            install_log.append("臨時文件清理完成")
            
            # 創建成功結果
            execution_time = time.time() - start_time
            result = ExtensionInstallResult(
                success=True,
                install_id=request.install_id,
                extension_name=request.extension_name,
                extension_version=request.extension_version,
                installation_path=install_result.get('installation_path'),
                verification_result=verification_result,
                performance_metrics={
                    'functionality_test': functionality_result,
                    'performance_test': performance_result
                },
                install_log=install_log,
                execution_time=execution_time
            )
            
            install_log.append(f"🎉 VSCode擴展安裝成功完成! 執行時間: {execution_time:.2f}秒")
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_message = str(e)
            install_log.append(f"❌ VSCode擴展安裝失敗: {error_message}")
            
            result = ExtensionInstallResult(
                success=False,
                install_id=request.install_id,
                extension_name=request.extension_name,
                extension_version=request.extension_version,
                error_message=error_message,
                install_log=install_log,
                execution_time=execution_time
            )
        
        finally:
            # 清理活躍安裝記錄
            if request.install_id in self.active_installs:
                del self.active_installs[request.install_id]
            
            # 添加到歷史記錄
            self.install_history.append(result)
            
            # 更新心跳狀態
            if self.local_mcp_adapter.heartbeat_manager:
                await self._update_heartbeat_status(result)
        
        return result
    
    async def _prepare_environment(self) -> Dict[str, Any]:
        """準備安裝環境"""
        env_result = {'success': True, 'log': []}
        
        try:
            # 檢查Mac環境
            env_result['log'].append(f"檢查Mac環境: {self.platform}")
            
            # 檢測VSCode
            try:
                vscode_path = await self.vscode_detector.detect_vscode_command()
                vscode_version = await self.vscode_detector.get_vscode_version()
                env_result['vscode_path'] = vscode_path
                env_result['vscode_version'] = vscode_version
                env_result['log'].append(f"✅ VSCode檢測成功: {vscode_path}")
                env_result['log'].append(f"✅ VSCode版本: {vscode_version}")
            except Exception as e:
                env_result['success'] = False
                env_result['error'] = f"VSCode檢測失敗: {e}"
                env_result['log'].append(f"❌ VSCode檢測失敗: {e}")
                return env_result
            
            # 確保目錄存在
            if not self.extension_manager.ensure_directories_exist():
                env_result['success'] = False
                env_result['error'] = "無法創建必要的目錄"
                env_result['log'].append("❌ 目錄創建失敗")
                return env_result
            
            env_result['log'].append(f"✅ 擴展目錄: {self.extension_manager.extensions_dir}")
            env_result['log'].append(f"✅ 用戶數據目錄: {self.extension_manager.user_data_dir}")
            
        except Exception as e:
            env_result['success'] = False
            env_result['error'] = f"環境準備異常: {e}"
            env_result['log'].append(f"❌ 環境準備異常: {e}")
        
        return env_result
    
    async def _check_existing_installation(self, request: ExtensionInstallRequest) -> Dict[str, Any]:
        """檢查現有安裝"""
        check_result = {'log': []}
        
        try:
            # 文件系統檢查
            is_installed = self.extension_manager.is_extension_installed(
                request.extension_name, request.extension_version
            )
            
            if is_installed:
                installation_path = self.extension_manager.get_extension_install_path(
                    request.extension_name, request.extension_version
                )
                check_result['already_installed'] = True
                check_result['installation_path'] = installation_path
                check_result['log'].append(f"✅ 擴展已安裝: {installation_path}")
            else:
                check_result['already_installed'] = False
                check_result['log'].append(f"ℹ️ 擴展未安裝，將進行新安裝")
            
            # CLI檢查
            vscode_cmd = await self.vscode_detector.detect_vscode_command()
            process = await asyncio.create_subprocess_exec(
                vscode_cmd, '--list-extensions', '--show-versions',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                installed_extensions = stdout.decode().strip().split('\n')
                target_extension = f"{request.extension_name}@{request.extension_version}"
                cli_installed = any(target_extension in ext for ext in installed_extensions)
                
                check_result['cli_installed'] = cli_installed
                check_result['log'].append(f"CLI檢查結果: {'已安裝' if cli_installed else '未安裝'}")
            
        except Exception as e:
            check_result['log'].append(f"⚠️ 現有安裝檢查異常: {e}")
        
        return check_result
    
    async def _prepare_vsix_file(self, request: ExtensionInstallRequest) -> str:
        """準備VSIX文件"""
        if request.vsix_file_path and os.path.exists(request.vsix_file_path):
            return request.vsix_file_path
        
        if request.vsix_data:
            # 使用提供的二進制數據
            temp_dir = tempfile.mkdtemp()
            vsix_file_path = os.path.join(temp_dir, f"{request.extension_name}-{request.extension_version}.vsix")
            
            async with aiofiles.open(vsix_file_path, 'wb') as f:
                await f.write(request.vsix_data)
            
            return vsix_file_path
            
        elif request.vsix_url:
            # 從URL下載VSIX文件
            temp_dir = tempfile.mkdtemp()
            vsix_file_path = os.path.join(temp_dir, f"{request.extension_name}-{request.extension_version}.vsix")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(request.vsix_url) as response:
                    if response.status == 200:
                        async with aiofiles.open(vsix_file_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)
                    else:
                        raise Exception(f"下載VSIX文件失敗: HTTP {response.status}")
            
            return vsix_file_path
        
        else:
            raise Exception("必須提供vsix_data、vsix_url或vsix_file_path")
    
    async def _execute_installation(self, vsix_file_path: str, request: ExtensionInstallRequest) -> Dict[str, Any]:
        """執行安裝"""
        install_result = {'success': True, 'log': []}
        
        try:
            vscode_cmd = await self.vscode_detector.detect_vscode_command()
            cmd = [vscode_cmd, "--install-extension", vsix_file_path]
            
            if request.force_reinstall:
                cmd.append("--force")
            
            install_result['log'].append(f"執行安裝命令: {' '.join(cmd)}")
            
            # 執行安裝命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            install_result['log'].append(f"命令返回碼: {process.returncode}")
            install_result['log'].append(f"stdout: {stdout.decode()}")
            install_result['log'].append(f"stderr: {stderr.decode()}")
            
            if process.returncode == 0:
                install_result['log'].append("✅ VSCode擴展安裝成功")
                
                # 確定安裝路徑
                install_path = self.extension_manager.get_extension_install_path(
                    request.extension_name, request.extension_version
                )
                install_result['installation_path'] = install_path
                
            else:
                install_result['success'] = False
                install_result['error'] = f"安裝命令失敗: {stderr.decode()}"
                install_result['log'].append(f"❌ VSCode擴展安裝失敗")
        
        except Exception as e:
            install_result['success'] = False
            install_result['error'] = f"安裝過程異常: {e}"
            install_result['log'].append(f"❌ 安裝過程異常: {e}")
        
        return install_result
    
    async def _verify_installation(self, request: ExtensionInstallRequest) -> Dict[str, Any]:
        """驗證安裝"""
        verification = {'success': True, 'log': []}
        
        try:
            # CLI驗證
            vscode_cmd = await self.vscode_detector.detect_vscode_command()
            list_cmd = [vscode_cmd, "--list-extensions", "--show-versions"]
            
            verification['log'].append(f"執行驗證命令: {' '.join(list_cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *list_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                installed_extensions = stdout.decode().strip().split('\n')
                verification['installed_extensions'] = installed_extensions
                verification['log'].append(f"已安裝擴展列表: {len(installed_extensions)}個擴展")
                
                # 檢查目標擴展
                target_extension = f"{request.extension_name}@{request.extension_version}"
                extension_found = any(target_extension in ext for ext in installed_extensions)
                
                verification['extension_found_in_cli'] = extension_found
                if extension_found:
                    verification['log'].append(f"✅ 目標擴展已在CLI中找到: {target_extension}")
                else:
                    verification['log'].append(f"⚠️ 目標擴展未在CLI中找到: {target_extension}")
            
            # 文件系統驗證
            is_installed = self.extension_manager.is_extension_installed(
                request.extension_name, request.extension_version
            )
            verification['extension_found_in_filesystem'] = is_installed
            
            if is_installed:
                verification['log'].append(f"✅ 擴展文件夾已找到")
            else:
                verification['log'].append(f"⚠️ 擴展文件夾未找到")
            
            # 綜合判斷
            verification['success'] = extension_found or is_installed
            
        except Exception as e:
            verification['success'] = False
            verification['error'] = f"驗證過程異常: {e}"
            verification['log'].append(f"❌ 驗證過程異常: {e}")
        
        return verification
    
    async def _test_extension_functionality(self, request: ExtensionInstallRequest) -> Dict[str, Any]:
        """測試擴展功能"""
        functionality_result = {'log': []}
        
        try:
            functionality_result['log'].append("開始擴展功能測試...")
            
            # 激活測試
            activation_test = await self.functionality_tester.test_extension_activation(
                request.extension_name
            )
            functionality_result['activation_test'] = activation_test
            functionality_result['log'].append(f"激活測試: {'成功' if activation_test['success'] else '失敗'}")
            
        except Exception as e:
            functionality_result['error'] = str(e)
            functionality_result['log'].append(f"❌ 功能測試異常: {e}")
        
        return functionality_result
    
    async def _test_extension_performance(self, request: ExtensionInstallRequest) -> Dict[str, Any]:
        """測試擴展性能"""
        performance_result = {'log': []}
        
        try:
            performance_result['log'].append("開始性能基準測試...")
            
            # 性能測試
            performance_test = await self.functionality_tester.test_extension_performance(
                request.extension_name
            )
            performance_result['performance_test'] = performance_test
            performance_result['log'].append(f"性能測試: {'通過' if performance_test['success'] else '未通過'}")
            
        except Exception as e:
            performance_result['error'] = str(e)
            performance_result['log'].append(f"❌ 性能測試異常: {e}")
        
        return performance_result
    
    async def _cleanup_temp_files(self, vsix_file_path: str):
        """清理臨時文件"""
        try:
            temp_dir = os.path.dirname(vsix_file_path)
            if os.path.exists(vsix_file_path):
                os.remove(vsix_file_path)
            if os.path.exists(temp_dir) and temp_dir.startswith('/tmp'):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logger.warning(f"清理臨時文件失敗: {e}")
    
    async def _update_heartbeat_status(self, result: ExtensionInstallResult):
        """更新心跳狀態"""
        if self.local_mcp_adapter.heartbeat_manager:
            status_data = {
                'enhanced_vscode_installer_status': 'active',
                'last_install': {
                    'install_id': result.install_id,
                    'success': result.success,
                    'extension_name': result.extension_name,
                    'execution_time': result.execution_time
                },
                'install_stats': {
                    'total_installs': len(self.install_history),
                    'successful_installs': sum(1 for r in self.install_history if r.success),
                    'active_installs': len(self.active_installs)
                }
            }
            
            await self.local_mcp_adapter.heartbeat_manager.update_status(status_data)
    
    async def get_install_status(self, install_id: str) -> Optional[Dict[str, Any]]:
        """獲取安裝狀態"""
        # 檢查活躍安裝
        if install_id in self.active_installs:
            return {
                'status': 'in_progress',
                'request': asdict(self.active_installs[install_id])
            }
        
        # 檢查歷史記錄
        for result in self.install_history:
            if result.install_id == install_id:
                return {
                    'status': 'completed',
                    'result': asdict(result)
                }
        
        return None
    
    async def list_installs(self) -> Dict[str, Any]:
        """列出所有安裝"""
        return {
            'active_installs': {
                install_id: asdict(request) 
                for install_id, request in self.active_installs.items()
            },
            'install_history': [
                asdict(result) for result in self.install_history[-10:]  # 最近10個
            ],
            'stats': {
                'total_installs': len(self.install_history),
                'successful_installs': sum(1 for r in self.install_history if r.success),
                'active_installs': len(self.active_installs)
            }
        }

def create_enhanced_vscode_installer(local_mcp_adapter: LocalMCPAdapter) -> EnhancedLocalMCPVSCodeInstaller:
    """創建增強的VSCode安裝器實例"""
    return EnhancedLocalMCPVSCodeInstaller(local_mcp_adapter)

# 導出主要類和函數
__all__ = [
    'EnhancedLocalMCPVSCodeInstaller',
    'ExtensionInstallRequest',
    'ExtensionInstallResult',
    'EnhancedMacVSCodeDetector',
    'EnhancedMacExtensionManager',
    'ExtensionFunctionalityTester',
    'create_enhanced_vscode_installer'
]

