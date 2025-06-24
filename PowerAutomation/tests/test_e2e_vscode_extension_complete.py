#!/usr/bin/env python3
"""
End-to-End VSCode Extension Installation and Verification Test
端到端VSCode擴展安裝和驗證測試

基於aicore0623架構的完整測試流程
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# 添加PowerAutomation路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'PowerAutomation'))

# 導入aicore0623組件
try:
    from PowerAutomation.components.local_mcp_adapter import LocalMCPAdapter, AdapterConfig
    from PowerAutomation.components.enhanced_vscode_installer_mcp import (
        EnhancedLocalMCPVSCodeInstaller,
        ExtensionInstallRequest,
        create_enhanced_vscode_installer
    )
    from PowerAutomation.components.complete_extension_verification_system import (
        CompleteExtensionVerificationSystem,
        create_complete_verification_system
    )
    from PowerAutomation.components.vsix_deployer_mcp import (
        VSIXDeployerMCP,
        VSIXDeploymentRequest,
        create_vsix_deployer_mcp
    )
except ImportError as e:
    print(f"導入錯誤: {e}")
    print("請確保在aicore0623目錄下運行此腳本")
    sys.exit(1)

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EndToEndVSCodeExtensionTester:
    """端到端VSCode擴展測試器"""
    
    def __init__(self):
        self.test_results = []
        self.local_mcp_adapter = None
        self.enhanced_installer = None
        self.verification_system = None
        self.vsix_deployer = None
        self.test_start_time = None
        
    async def setup_test_environment(self) -> bool:
        """設置測試環境"""
        try:
            logger.info("🚀 設置端到端測試環境")
            
            # 創建測試配置
            test_config = AdapterConfig(
                adapter_id="e2e_test_adapter",
                cloud_endpoint="https://test.powerautomation.local",
                api_key="test_api_key_e2e_12345",
                tool_discovery={
                    "auto_discovery": True,
                    "discovery_interval": 30,
                    "discovery_timeout": 10
                },
                heartbeat={
                    "interval": 30,
                    "timeout": 10,
                    "retry_count": 3
                },
                routing={
                    "load_balancing": "round_robin",
                    "health_check_interval": 60,
                    "circuit_breaker": True
                },
                security={
                    "api_key_required": True,
                    "rate_limiting": True,
                    "max_requests_per_minute": 100
                },
                logging={
                    "level": "INFO",
                    "file_path": "/tmp/e2e_test.log"
                }
            )
            
            # 初始化Local MCP Adapter
            logger.info("初始化Local MCP Adapter...")
            self.local_mcp_adapter = LocalMCPAdapter(config_dict=test_config.__dict__)
            
            # 啟動Local MCP Adapter
            await self.local_mcp_adapter.start()
            logger.info("✅ Local MCP Adapter啟動成功")
            
            # 創建增強的VSCode安裝器
            logger.info("創建增強的VSCode安裝器...")
            self.enhanced_installer = create_enhanced_vscode_installer(self.local_mcp_adapter)
            logger.info("✅ 增強VSCode安裝器創建成功")
            
            # 創建完整的驗證系統
            logger.info("創建完整的驗證系統...")
            self.verification_system = create_complete_verification_system(self.local_mcp_adapter)
            logger.info("✅ 完整驗證系統創建成功")
            
            # 創建VSIX部署器
            logger.info("創建VSIX部署器...")
            self.vsix_deployer = create_vsix_deployer_mcp(self.local_mcp_adapter)
            logger.info("✅ VSIX部署器創建成功")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 測試環境設置失敗: {e}")
            return False
    
    async def create_test_vsix_file(self) -> str:
        """創建測試用的VSIX文件"""
        logger.info("📦 創建測試VSIX文件")
        
        # 檢查是否有現有的VSIX文件
        vsix_source_paths = [
            "PowerAutomation_local/vscode-extension",
            "../PowerAutomation_local/vscode-extension",
            "../../PowerAutomation_local/vscode-extension"
        ]
        
        for vsix_source_path in vsix_source_paths:
            if os.path.exists(vsix_source_path):
                logger.info(f"找到VSCode擴展源碼: {vsix_source_path}")
                
                # 檢查是否已有構建的VSIX文件
                vsix_files = list(Path(vsix_source_path).glob("*.vsix"))
                if vsix_files:
                    vsix_file = str(vsix_files[0])
                    logger.info(f"✅ 找到現有VSIX文件: {vsix_file}")
                    return vsix_file
        
        # 創建模擬VSIX文件用於測試
        logger.info("創建模擬VSIX文件...")
        temp_dir = tempfile.mkdtemp()
        mock_vsix_path = os.path.join(temp_dir, "test-extension-1.0.0.vsix")
        
        # 創建一個簡單的ZIP文件作為模擬VSIX
        with zipfile.ZipFile(mock_vsix_path, 'w') as zipf:
            # 添加package.json
            package_json = {
                "name": "test-extension",
                "displayName": "Test Extension",
                "version": "1.0.0",
                "description": "A test extension for e2e testing",
                "engines": {"vscode": "^1.60.0"},
                "categories": ["Other"],
                "main": "./extension.js",
                "contributes": {
                    "commands": [{
                        "command": "test-extension.helloWorld",
                        "title": "Hello World"
                    }]
                },
                "scripts": {
                    "vscode:prepublish": "npm run compile",
                    "compile": "tsc -p ./"
                },
                "devDependencies": {
                    "@types/vscode": "^1.60.0"
                }
            }
            zipf.writestr("package.json", json.dumps(package_json, indent=2))
            
            # 添加簡單的extension.js
            extension_js = """
const vscode = require('vscode');

function activate(context) {
    console.log('Test extension is now active!');
    
    let disposable = vscode.commands.registerCommand('test-extension.helloWorld', function () {
        vscode.window.showInformationMessage('Hello World from Test Extension!');
    });
    
    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
"""
            zipf.writestr("extension.js", extension_js)
            
            # 添加README.md
            readme_md = """# Test Extension

This is a test extension for end-to-end testing of the VSCode extension installation and verification system.

## Features

- Hello World command
- Basic extension structure
- Compatible with VSCode 1.60.0+

## Usage

1. Install the extension
2. Open Command Palette (Cmd+Shift+P)
3. Run "Hello World" command
"""
            zipf.writestr("README.md", readme_md)
        
        logger.info(f"✅ 模擬VSIX文件創建完成: {mock_vsix_path}")
        return mock_vsix_path
    
    async def test_enhanced_installer(self, vsix_file_path: str) -> Dict[str, Any]:
        """測試增強的安裝器"""
        logger.info("🔧 測試增強的VSCode安裝器")
        
        test_result = {
            'test_name': '增強VSCode安裝器測試',
            'success': False,
            'details': {},
            'execution_time': 0,
            'error_message': None
        }
        
        start_time = time.time()
        
        try:
            # 讀取VSIX文件
            with open(vsix_file_path, 'rb') as f:
                vsix_data = f.read()
            
            # 創建安裝請求
            install_request = ExtensionInstallRequest(
                extension_name="test-extension",
                extension_version="1.0.0",
                vsix_data=vsix_data,
                target_platform="mac",
                force_reinstall=True,  # 強制重新安裝以確保測試
                metadata={
                    'test_mode': True,
                    'source_file': vsix_file_path
                }
            )
            
            logger.info(f"開始安裝: {install_request.extension_name} v{install_request.extension_version}")
            
            # 執行安裝
            install_result = await self.enhanced_installer.install_extension(install_request)
            
            test_result['details'] = {
                'install_id': install_result.install_id,
                'success': install_result.success,
                'installation_path': install_result.installation_path,
                'verification_result': install_result.verification_result,
                'performance_metrics': install_result.performance_metrics,
                'install_log': install_result.install_log,
                'error_message': install_result.error_message
            }
            
            test_result['success'] = install_result.success
            if not install_result.success:
                test_result['error_message'] = install_result.error_message
            
            logger.info(f"安裝結果: {'成功' if install_result.success else '失敗'}")
            
        except Exception as e:
            test_result['error_message'] = str(e)
            logger.error(f"❌ 增強安裝器測試異常: {e}")
        
        finally:
            test_result['execution_time'] = time.time() - start_time
        
        return test_result
    
    async def test_verification_system(self) -> Dict[str, Any]:
        """測試驗證系統"""
        logger.info("🔍 測試完整驗證系統")
        
        test_result = {
            'test_name': '完整驗證系統測試',
            'success': False,
            'details': {},
            'execution_time': 0,
            'error_message': None
        }
        
        start_time = time.time()
        
        try:
            # 運行完整驗證
            verification_report = await self.verification_system.run_complete_verification(
                "test-extension", "1.0.0"
            )
            
            test_result['details'] = {
                'verification_id': verification_report.verification_id,
                'overall_success': verification_report.overall_success,
                'total_tests': len(verification_report.test_results),
                'successful_tests': sum(1 for r in verification_report.test_results if r.success),
                'performance_metrics': verification_report.performance_metrics,
                'compatibility_info': verification_report.compatibility_info,
                'security_assessment': verification_report.security_assessment,
                'recommendations': verification_report.recommendations
            }
            
            test_result['success'] = verification_report.overall_success
            
            logger.info(f"驗證結果: {'成功' if verification_report.overall_success else '部分失敗'}")
            logger.info(f"測試通過率: {test_result['details']['successful_tests']}/{test_result['details']['total_tests']}")
            
        except Exception as e:
            test_result['error_message'] = str(e)
            logger.error(f"❌ 驗證系統測試異常: {e}")
        
        finally:
            test_result['execution_time'] = time.time() - start_time
        
        return test_result
    
    async def test_vsix_deployer(self, vsix_file_path: str) -> Dict[str, Any]:
        """測試VSIX部署器"""
        logger.info("🚀 測試VSIX部署器")
        
        test_result = {
            'test_name': 'VSIX部署器測試',
            'success': False,
            'details': {},
            'execution_time': 0,
            'error_message': None
        }
        
        start_time = time.time()
        
        try:
            # 讀取VSIX文件
            with open(vsix_file_path, 'rb') as f:
                vsix_data = f.read()
            
            # 創建部署請求
            deployment_request = VSIXDeploymentRequest(
                extension_name="test-extension",
                extension_version="1.0.0",
                vsix_data=vsix_data,
                target_platform="mac",
                metadata={
                    'test_deployment': True,
                    'source_file': vsix_file_path
                }
            )
            
            logger.info(f"開始部署: {deployment_request.extension_name} v{deployment_request.extension_version}")
            
            # 執行部署
            deployment_result = await self.vsix_deployer.deploy_vsix(deployment_request)
            
            test_result['details'] = {
                'deployment_id': deployment_result.deployment_id,
                'success': deployment_result.success,
                'installation_path': deployment_result.installation_path,
                'verification_result': deployment_result.verification_result,
                'deployment_log': deployment_result.deployment_log,
                'error_message': deployment_result.error_message
            }
            
            test_result['success'] = deployment_result.success
            if not deployment_result.success:
                test_result['error_message'] = deployment_result.error_message
            
            logger.info(f"部署結果: {'成功' if deployment_result.success else '失敗'}")
            
        except Exception as e:
            test_result['error_message'] = str(e)
            logger.error(f"❌ VSIX部署器測試異常: {e}")
        
        finally:
            test_result['execution_time'] = time.time() - start_time
        
        return test_result
    
    async def test_local_mcp_integration(self) -> Dict[str, Any]:
        """測試Local MCP集成"""
        logger.info("🔗 測試Local MCP集成")
        
        test_result = {
            'test_name': 'Local MCP集成測試',
            'success': False,
            'details': {},
            'execution_time': 0,
            'error_message': None
        }
        
        start_time = time.time()
        
        try:
            # 檢查Local MCP Adapter狀態
            adapter_status = await self.local_mcp_adapter.get_status()
            test_result['details']['adapter_status'] = adapter_status
            logger.info(f"Adapter狀態: {adapter_status.get('adapter_status', 'unknown')}")
            
            # 檢查工具註冊
            if self.local_mcp_adapter.tool_registry_manager:
                tools = await self.local_mcp_adapter.tool_registry_manager.list_tools()
                test_result['details']['registered_tools'] = tools
                logger.info(f"已註冊工具數量: {len(tools)}")
                
                # 檢查各個組件的工具是否已註冊
                tool_ids = [tool.get('tool_id') for tool in tools]
                test_result['details']['tool_registration'] = {
                    'enhanced_vscode_installer': 'enhanced_vscode_installer' in tool_ids,
                    'vsix_deployer': 'vsix_deployer' in tool_ids
                }
            
            # 檢查心跳狀態
            if self.local_mcp_adapter.heartbeat_manager:
                heartbeat_status = await self.local_mcp_adapter.heartbeat_manager.get_status()
                test_result['details']['heartbeat_status'] = heartbeat_status
                logger.info(f"心跳狀態: {heartbeat_status.get('status', 'unknown')}")
            
            # 檢查安裝器狀態
            install_stats = await self.enhanced_installer.list_installs()
            test_result['details']['installer_stats'] = install_stats['stats']
            logger.info(f"安裝器統計: {install_stats['stats']}")
            
            # 檢查部署器狀態
            deployment_stats = await self.vsix_deployer.list_deployments()
            test_result['details']['deployer_stats'] = deployment_stats['stats']
            logger.info(f"部署器統計: {deployment_stats['stats']}")
            
            # 檢查驗證系統歷史
            verification_history = await self.verification_system.list_verification_history()
            test_result['details']['verification_history'] = verification_history
            logger.info(f"驗證歷史: {len(verification_history)}個記錄")
            
            test_result['success'] = True
            logger.info("✅ Local MCP集成測試完成")
            
        except Exception as e:
            test_result['error_message'] = str(e)
            logger.error(f"❌ Local MCP集成測試異常: {e}")
        
        finally:
            test_result['execution_time'] = time.time() - start_time
        
        return test_result
    
    async def run_complete_e2e_test(self) -> Dict[str, Any]:
        """運行完整的端到端測試"""
        logger.info("🎯 開始端到端VSCode擴展安裝和驗證測試")
        
        self.test_start_time = time.time()
        
        complete_test_result = {
            'test_suite': 'End-to-End VSCode Extension Installation and Verification',
            'start_time': datetime.now().isoformat(),
            'success': False,
            'test_results': [],
            'summary': {},
            'total_execution_time': 0,
            'environment_info': {
                'platform': sys.platform,
                'python_version': sys.version,
                'working_directory': os.getcwd()
            }
        }
        
        try:
            # 1. 設置測試環境
            logger.info("=== 階段1: 設置測試環境 ===")
            if not await self.setup_test_environment():
                raise Exception("測試環境設置失敗")
            
            # 2. 創建測試VSIX
            logger.info("=== 階段2: 創建測試VSIX ===")
            vsix_file_path = await self.create_test_vsix_file()
            
            # 3. 運行各項測試
            logger.info("=== 階段3: 執行測試套件 ===")
            tests = [
                self.test_local_mcp_integration(),
                self.test_enhanced_installer(vsix_file_path),
                self.test_verification_system(),
                self.test_vsix_deployer(vsix_file_path)
            ]
            
            for test_coro in tests:
                test_result = await test_coro
                complete_test_result['test_results'].append(test_result)
                self.test_results.append(test_result)
            
            # 4. 生成測試摘要
            logger.info("=== 階段4: 生成測試摘要 ===")
            total_tests = len(complete_test_result['test_results'])
            successful_tests = sum(1 for result in complete_test_result['test_results'] if result['success'])
            
            complete_test_result['summary'] = {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': total_tests - successful_tests,
                'success_rate': successful_tests / total_tests if total_tests > 0 else 0,
                'test_details': [
                    {
                        'test_name': result['test_name'],
                        'success': result['success'],
                        'execution_time': result['execution_time'],
                        'error_message': result.get('error_message')
                    }
                    for result in complete_test_result['test_results']
                ]
            }
            
            complete_test_result['success'] = successful_tests == total_tests
            
            # 5. 輸出測試結果
            logger.info("=== 階段5: 測試結果 ===")
            logger.info(f"🎯 測試完成: {successful_tests}/{total_tests} 成功")
            logger.info(f"📊 成功率: {complete_test_result['summary']['success_rate']:.2%}")
            
            for result in complete_test_result['test_results']:
                status = "✅" if result['success'] else "❌"
                logger.info(f"{status} {result['test_name']}: {result['execution_time']:.2f}秒")
                if not result['success'] and result.get('error_message'):
                    logger.error(f"   錯誤: {result['error_message']}")
            
        except Exception as e:
            complete_test_result['error_message'] = str(e)
            logger.error(f"❌ 端到端測試異常: {e}")
        
        finally:
            complete_test_result['total_execution_time'] = time.time() - self.test_start_time
            complete_test_result['end_time'] = datetime.now().isoformat()
            
            # 清理資源
            if self.local_mcp_adapter:
                try:
                    await self.local_mcp_adapter.stop()
                    logger.info("✅ Local MCP Adapter已停止")
                except Exception as e:
                    logger.warning(f"停止Local MCP Adapter時出現警告: {e}")
        
        return complete_test_result
    
    def save_test_report(self, test_result: Dict[str, Any], output_file: str = None):
        """保存測試報告"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"e2e_test_report_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(test_result, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"📄 測試報告已保存: {output_file}")
            
        except Exception as e:
            logger.error(f"❌ 保存測試報告失敗: {e}")

async def main():
    """主函數"""
    print("🚀 啟動端到端VSCode擴展安裝和驗證測試")
    print("=" * 60)
    
    tester = EndToEndVSCodeExtensionTester()
    
    try:
        # 運行完整測試
        test_result = await tester.run_complete_e2e_test()
        
        # 保存測試報告
        tester.save_test_report(test_result)
        
        # 輸出最終結果
        print("\n" + "=" * 60)
        print("🎯 端到端測試完成")
        print(f"📊 總體結果: {'✅ 成功' if test_result['success'] else '❌ 失敗'}")
        print(f"⏱️  總執行時間: {test_result['total_execution_time']:.2f}秒")
        print(f"📈 成功率: {test_result['summary']['success_rate']:.2%}")
        print("=" * 60)
        
        # 返回適當的退出碼
        return 0 if test_result['success'] else 1
        
    except Exception as e:
        print(f"❌ 測試執行失敗: {e}")
        return 1

if __name__ == "__main__":
    # 運行測試
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

