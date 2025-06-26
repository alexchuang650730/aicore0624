"""
PowerAutomation VSIX Deployer - 基於aicore0623
VSIX Extension Deployment Component for PowerAutomation

整合到aicore0623架構的VSCode擴展部署系統
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
import hashlib
import platform
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import aiohttp
import aiofiles

# 導入aicore0623的核心組件
from .local_mcp_adapter import LocalMCPAdapter, AdapterConfig
from .tool_registry_manager import ToolRegistryManager, LocalToolInfo, ToolStatus
from .heartbeat_manager import HeartbeatManager, ConnectionStatus
from .smart_routing_engine import SmartRoutingEngine, RoutingRequest

logger = logging.getLogger(__name__)

@dataclass
class VSIXDeploymentRequest:
    """VSIX部署請求"""
    extension_name: str
    extension_version: str
    vsix_url: Optional[str] = None
    vsix_data: Optional[bytes] = None
    target_platform: str = "universal"
    deployment_id: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.deployment_id:
            self.deployment_id = f"deploy_{int(datetime.now().timestamp())}"
        if self.metadata is None:
            self.metadata = {}

@dataclass
class VSIXDeploymentResult:
    """VSIX部署結果"""
    success: bool
    deployment_id: str
    extension_name: str
    extension_version: str
    installation_path: Optional[str] = None
    verification_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    deployment_log: List[str] = None
    execution_time: float = 0.0
    
    def __post_init__(self):
        if self.deployment_log is None:
            self.deployment_log = []

class MacVSCodeDetector:
    """Mac環境下的VSCode檢測器"""
    
    POSSIBLE_VSCODE_PATHS = [
        "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
        "/usr/local/bin/code",
        "/opt/homebrew/bin/code",
        "~/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
    ]
    
    def detect_vscode_command(self) -> str:
        """檢測Mac上的VSCode命令路徑"""
        # 1. 檢查PATH中的code命令
        try:
            result = subprocess.run(['which', 'code'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        # 2. 檢查常見安裝路徑
        for path in self.POSSIBLE_VSCODE_PATHS:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                return expanded_path
        
        # 3. 檢查Applications目錄
        app_path = "/Applications/Visual Studio Code.app"
        if os.path.exists(app_path):
            return f"{app_path}/Contents/Resources/app/bin/code"
        
        raise Exception("未找到VSCode安裝，請確保VSCode已安裝並添加到PATH")

class MacExtensionPaths:
    """Mac環境下的擴展路徑管理"""
    
    @staticmethod
    def get_extensions_dir() -> str:
        """獲取Mac VSCode擴展目錄"""
        home = os.path.expanduser("~")
        return f"{home}/.vscode/extensions"
    
    @staticmethod
    def get_user_data_dir() -> str:
        """獲取Mac VSCode用戶數據目錄"""
        home = os.path.expanduser("~")
        return f"{home}/Library/Application Support/Code/User"
    
    @staticmethod
    def get_extension_install_path(extension_name: str, version: str) -> str:
        """獲取特定擴展的安裝路徑"""
        extensions_dir = MacExtensionPaths.get_extensions_dir()
        return f"{extensions_dir}/{extension_name}-{version}"

class VSIXDeployerMCP:
    """PowerAutomation VSIX部署器 - 整合到aicore0623架構"""
    
    def __init__(self, local_mcp_adapter: LocalMCPAdapter):
        """
        初始化VSIX部署器
        
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
            self.vscode_detector = MacVSCodeDetector()
            self.extension_paths = MacExtensionPaths()
        
        # 部署狀態
        self.active_deployments: Dict[str, VSIXDeploymentRequest] = {}
        self.deployment_history: List[VSIXDeploymentResult] = []
        
        # 註冊到工具註冊管理器
        self._register_vsix_tools()
    
    def _register_vsix_tools(self):
        """註冊VSIX相關工具到工具註冊管理器"""
        if self.local_mcp_adapter.tool_registry_manager:
            # 註冊VSIX部署工具
            vsix_tool = LocalToolInfo(
                tool_id="vsix_deployer",
                tool_name="VSIX Extension Deployer",
                tool_type="extension_management",
                version="1.0.0",
                description="VSCode擴展VSIX文件部署和驗證工具",
                capabilities=[
                    "vsix_deployment",
                    "extension_installation", 
                    "mac_vscode_integration",
                    "extension_verification"
                ],
                endpoint=f"http://localhost:8080/api/v1/vsix",
                status=ToolStatus.ACTIVE,
                metadata={
                    "platform": self.platform,
                    "supports_mac": self.is_mac,
                    "vscode_integration": True
                }
            )
            
            self.local_mcp_adapter.tool_registry_manager.register_tool(vsix_tool)
            logger.info(f"VSIX部署工具已註冊到工具註冊管理器: {vsix_tool.tool_id}")
    
    async def deploy_vsix(self, request: VSIXDeploymentRequest) -> VSIXDeploymentResult:
        """
        部署VSIX擴展
        
        Args:
            request: VSIX部署請求
            
        Returns:
            VSIXDeploymentResult: 部署結果
        """
        start_time = time.time()
        deployment_log = []
        
        try:
            deployment_log.append(f"開始VSIX部署: {request.extension_name} v{request.extension_version}")
            deployment_log.append(f"目標平台: {self.platform}")
            deployment_log.append(f"部署ID: {request.deployment_id}")
            
            # 記錄活躍部署
            self.active_deployments[request.deployment_id] = request
            
            # 步驟1: 環境檢查
            deployment_log.append("=== 步驟1: 環境檢查 ===")
            env_check = await self._check_environment()
            deployment_log.extend(env_check.get('log', []))
            
            if not env_check['success']:
                raise Exception(f"環境檢查失敗: {env_check.get('error', '未知錯誤')}")
            
            # 步驟2: 獲取VSIX文件
            deployment_log.append("=== 步驟2: 獲取VSIX文件 ===")
            vsix_file_path = await self._prepare_vsix_file(request)
            deployment_log.append(f"VSIX文件準備完成: {vsix_file_path}")
            
            # 步驟3: 安裝擴展
            deployment_log.append("=== 步驟3: 安裝VSCode擴展 ===")
            install_result = await self._install_extension(vsix_file_path, request)
            deployment_log.extend(install_result.get('log', []))
            
            if not install_result['success']:
                raise Exception(f"擴展安裝失敗: {install_result.get('error', '未知錯誤')}")
            
            # 步驟4: 驗證安裝
            deployment_log.append("=== 步驟4: 驗證擴展安裝 ===")
            verification_result = await self._verify_installation(request)
            deployment_log.extend(verification_result.get('log', []))
            
            # 步驟5: 清理臨時文件
            deployment_log.append("=== 步驟5: 清理臨時文件 ===")
            await self._cleanup_temp_files(vsix_file_path)
            deployment_log.append("臨時文件清理完成")
            
            # 創建成功結果
            execution_time = time.time() - start_time
            result = VSIXDeploymentResult(
                success=True,
                deployment_id=request.deployment_id,
                extension_name=request.extension_name,
                extension_version=request.extension_version,
                installation_path=install_result.get('installation_path'),
                verification_result=verification_result,
                deployment_log=deployment_log,
                execution_time=execution_time
            )
            
            deployment_log.append(f"🎉 VSIX部署成功完成! 執行時間: {execution_time:.2f}秒")
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_message = str(e)
            deployment_log.append(f"❌ VSIX部署失敗: {error_message}")
            
            result = VSIXDeploymentResult(
                success=False,
                deployment_id=request.deployment_id,
                extension_name=request.extension_name,
                extension_version=request.extension_version,
                error_message=error_message,
                deployment_log=deployment_log,
                execution_time=execution_time
            )
        
        finally:
            # 清理活躍部署記錄
            if request.deployment_id in self.active_deployments:
                del self.active_deployments[request.deployment_id]
            
            # 添加到歷史記錄
            self.deployment_history.append(result)
            
            # 更新心跳狀態
            if self.local_mcp_adapter.heartbeat_manager:
                await self._update_heartbeat_status(result)
        
        return result
    
    async def _check_environment(self) -> Dict[str, Any]:
        """檢查部署環境"""
        check_result = {'success': True, 'log': []}
        
        try:
            # 檢查操作系統
            check_result['log'].append(f"操作系統: {self.platform}")
            
            if self.is_mac:
                # Mac特定檢查
                check_result['log'].append("執行Mac環境檢查...")
                
                # 檢查VSCode安裝
                try:
                    vscode_path = self.vscode_detector.detect_vscode_command()
                    check_result['vscode_path'] = vscode_path
                    check_result['log'].append(f"✅ VSCode檢測成功: {vscode_path}")
                except Exception as e:
                    check_result['success'] = False
                    check_result['error'] = f"VSCode檢測失敗: {e}"
                    check_result['log'].append(f"❌ VSCode檢測失敗: {e}")
                    return check_result
                
                # 檢查擴展目錄
                extensions_dir = self.extension_paths.get_extensions_dir()
                if os.path.exists(extensions_dir):
                    check_result['log'].append(f"✅ 擴展目錄存在: {extensions_dir}")
                else:
                    check_result['log'].append(f"⚠️ 擴展目錄不存在，將創建: {extensions_dir}")
                    try:
                        os.makedirs(extensions_dir, mode=0o755, exist_ok=True)
                        check_result['log'].append(f"✅ 擴展目錄創建成功")
                    except Exception as e:
                        check_result['success'] = False
                        check_result['error'] = f"無法創建擴展目錄: {e}"
                        check_result['log'].append(f"❌ 擴展目錄創建失敗: {e}")
                        return check_result
            
            else:
                check_result['log'].append("⚠️ 非Mac環境，使用通用檢查")
                # 通用環境檢查
                try:
                    result = subprocess.run(['code', '--version'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        check_result['log'].append(f"✅ VSCode檢測成功")
                    else:
                        check_result['success'] = False
                        check_result['error'] = "VSCode命令不可用"
                        check_result['log'].append(f"❌ VSCode命令不可用")
                except Exception as e:
                    check_result['success'] = False
                    check_result['error'] = f"VSCode檢測失敗: {e}"
                    check_result['log'].append(f"❌ VSCode檢測失敗: {e}")
            
        except Exception as e:
            check_result['success'] = False
            check_result['error'] = f"環境檢查異常: {e}"
            check_result['log'].append(f"❌ 環境檢查異常: {e}")
        
        return check_result
    
    async def _prepare_vsix_file(self, request: VSIXDeploymentRequest) -> str:
        """準備VSIX文件"""
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
            raise Exception("必須提供vsix_data或vsix_url")
    
    async def _install_extension(self, vsix_file_path: str, request: VSIXDeploymentRequest) -> Dict[str, Any]:
        """安裝VSCode擴展"""
        install_result = {'success': True, 'log': []}
        
        try:
            if self.is_mac:
                # Mac特定安裝
                vscode_cmd = self.vscode_detector.detect_vscode_command()
                cmd = [vscode_cmd, "--install-extension", vsix_file_path]
            else:
                # 通用安裝
                cmd = ["code", "--install-extension", vsix_file_path]
            
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
                if self.is_mac:
                    install_path = self.extension_paths.get_extension_install_path(
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
    
    async def _verify_installation(self, request: VSIXDeploymentRequest) -> Dict[str, Any]:
        """驗證擴展安裝"""
        verification = {'success': True, 'log': []}
        
        try:
            # 檢查擴展是否出現在已安裝列表中
            if self.is_mac:
                vscode_cmd = self.vscode_detector.detect_vscode_command()
                list_cmd = [vscode_cmd, "--list-extensions", "--show-versions"]
            else:
                list_cmd = ["code", "--list-extensions", "--show-versions"]
            
            verification['log'].append(f"執行列表命令: {' '.join(list_cmd)}")
            
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
                
                # 檢查目標擴展是否在列表中
                target_extension = f"{request.extension_name}@{request.extension_version}"
                extension_found = any(target_extension in ext for ext in installed_extensions)
                
                if extension_found:
                    verification['log'].append(f"✅ 目標擴展已找到: {target_extension}")
                else:
                    verification['log'].append(f"⚠️ 目標擴展未在列表中找到: {target_extension}")
                    verification['extension_listed'] = False
            else:
                verification['log'].append(f"❌ 列表命令失敗: {stderr.decode()}")
                verification['list_command_failed'] = True
            
            # Mac特定的文件系統檢查
            if self.is_mac:
                extensions_dir = self.extension_paths.get_extensions_dir()
                if os.path.exists(extensions_dir):
                    extension_folders = os.listdir(extensions_dir)
                    verification['extension_folders'] = extension_folders
                    verification['log'].append(f"擴展目錄內容: {len(extension_folders)}個文件夾")
                    
                    # 檢查特定擴展文件夾
                    target_folder = f"{request.extension_name}-{request.extension_version}"
                    if target_folder in extension_folders:
                        verification['log'].append(f"✅ 擴展文件夾已找到: {target_folder}")
                    else:
                        verification['log'].append(f"⚠️ 擴展文件夾未找到: {target_folder}")
        
        except Exception as e:
            verification['success'] = False
            verification['error'] = f"驗證過程異常: {e}"
            verification['log'].append(f"❌ 驗證過程異常: {e}")
        
        return verification
    
    async def _cleanup_temp_files(self, vsix_file_path: str):
        """清理臨時文件"""
        try:
            temp_dir = os.path.dirname(vsix_file_path)
            if os.path.exists(vsix_file_path):
                os.remove(vsix_file_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except Exception as e:
            logger.warning(f"清理臨時文件失敗: {e}")
    
    async def _update_heartbeat_status(self, result: VSIXDeploymentResult):
        """更新心跳狀態"""
        if self.local_mcp_adapter.heartbeat_manager:
            status_data = {
                'vsix_deployer_status': 'active',
                'last_deployment': {
                    'deployment_id': result.deployment_id,
                    'success': result.success,
                    'extension_name': result.extension_name,
                    'execution_time': result.execution_time
                },
                'deployment_stats': {
                    'total_deployments': len(self.deployment_history),
                    'successful_deployments': sum(1 for r in self.deployment_history if r.success),
                    'active_deployments': len(self.active_deployments)
                }
            }
            
            await self.local_mcp_adapter.heartbeat_manager.update_status(status_data)
    
    async def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """獲取部署狀態"""
        # 檢查活躍部署
        if deployment_id in self.active_deployments:
            return {
                'status': 'in_progress',
                'request': asdict(self.active_deployments[deployment_id])
            }
        
        # 檢查歷史記錄
        for result in self.deployment_history:
            if result.deployment_id == deployment_id:
                return {
                    'status': 'completed',
                    'result': asdict(result)
                }
        
        return None
    
    async def list_deployments(self) -> Dict[str, Any]:
        """列出所有部署"""
        return {
            'active_deployments': {
                deployment_id: asdict(request) 
                for deployment_id, request in self.active_deployments.items()
            },
            'deployment_history': [
                asdict(result) for result in self.deployment_history[-10:]  # 最近10個
            ],
            'stats': {
                'total_deployments': len(self.deployment_history),
                'successful_deployments': sum(1 for r in self.deployment_history if r.success),
                'active_deployments': len(self.active_deployments)
            }
        }

def create_vsix_deployer_mcp(local_mcp_adapter: LocalMCPAdapter) -> VSIXDeployerMCP:
    """創建VSIX部署器實例"""
    return VSIXDeployerMCP(local_mcp_adapter)

# 導出主要類和函數
__all__ = [
    'VSIXDeployerMCP',
    'VSIXDeploymentRequest', 
    'VSIXDeploymentResult',
    'MacVSCodeDetector',
    'MacExtensionPaths',
    'create_vsix_deployer_mcp'
]

