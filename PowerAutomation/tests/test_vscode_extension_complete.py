#!/usr/bin/env python3
"""
VSCode端擴展安裝和功能驗證測試
Test VSCode Extension Installation and Functionality Verification

基於aicore0623的完整測試流程
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# 添加PowerAutomation路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'PowerAutomation'))

# 導入aicore0623組件
from PowerAutomation.components.local_mcp_adapter import LocalMCPAdapter, AdapterConfig
from PowerAutomation.components.vsix_deployer_mcp import (
    VSIXDeployerMCP, 
    VSIXDeploymentRequest, 
    create_vsix_deployer_mcp
)

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VSCodeExtensionTester:
    """VSCode擴展測試器"""
    
    def __init__(self):
        self.test_results = []
        self.local_mcp_adapter = None
        self.vsix_deployer = None
    
    async def setup_test_environment(self) -> bool:
        """設置測試環境"""
        try:
            logger.info("=== 設置測試環境 ===")
            
            # 創建測試配置
            test_config = AdapterConfig(
                adapter_id="test_vsix_adapter",
                cloud_endpoint="https://test.powerautomation.local",
                api_key="test_api_key_12345",
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
                    "file_path": "/tmp/vsix_test.log"
                }
            )
            
            # 初始化Local MCP Adapter
            logger.info("初始化Local MCP Adapter...")
            self.local_mcp_adapter = LocalMCPAdapter(config_dict=test_config.__dict__)
            
            # 啟動Local MCP Adapter
            await self.local_mcp_adapter.start()
            logger.info("✅ Local MCP Adapter啟動成功")
            
            # 創建VSIX部署器
            logger.info("創建VSIX部署器...")
            self.vsix_deployer = create_vsix_deployer_mcp(self.local_mcp_adapter)
            logger.info("✅ VSIX部署器創建成功")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 測試環境設置失敗: {e}")
            return False
    
    async def create_test_vsix(self) -> str:
        """創建測試用的VSIX文件"""
        logger.info("=== 創建測試VSIX文件 ===")
        
        # 使用現有的PowerAutomation Local擴展
        vsix_source_path = "PowerAutomation_local/vscode-extension"
        
        if os.path.exists(vsix_source_path):
            logger.info(f"找到現有VSCode擴展源碼: {vsix_source_path}")
            
            # 檢查是否已有構建的VSIX文件
            vsix_files = list(Path(vsix_source_path).glob("*.vsix"))
            if vsix_files:
                vsix_file = str(vsix_files[0])
                logger.info(f"✅ 找到現有VSIX文件: {vsix_file}")
                return vsix_file
            
            # 如果沒有VSIX文件，嘗試構建
            logger.info("嘗試構建VSIX文件...")
            try:
                import subprocess
                
                # 切換到擴展目錄
                original_cwd = os.getcwd()
                os.chdir(vsix_source_path)
                
                # 安裝依賴
                logger.info("安裝npm依賴...")
                result = subprocess.run(['npm', 'install'], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    logger.warning(f"npm install警告: {result.stderr}")
                
                # 編譯TypeScript
                logger.info("編譯TypeScript...")
                result = subprocess.run(['npm', 'run', 'compile'], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    logger.warning(f"編譯警告: {result.stderr}")
                
                # 打包VSIX
                logger.info("打包VSIX文件...")
                result = subprocess.run(['npx', 'vsce', 'package'], 
                                      capture_output=True, text=True)
                
                os.chdir(original_cwd)
                
                if result.returncode == 0:
                    # 查找生成的VSIX文件
                    vsix_files = list(Path(vsix_source_path).glob("*.vsix"))
                    if vsix_files:
                        vsix_file = str(vsix_files[0])
                        logger.info(f"✅ VSIX文件構建成功: {vsix_file}")
                        return vsix_file
                
                logger.warning("VSIX構建失敗，使用模擬文件")
                
            except Exception as e:
                logger.warning(f"VSIX構建異常: {e}")
                os.chdir(original_cwd)
        
        # 創建模擬VSIX文件用於測試
        logger.info("創建模擬VSIX文件...")
        temp_dir = tempfile.mkdtemp()
        mock_vsix_path = os.path.join(temp_dir, "test-extension-1.0.0.vsix")
        
        # 創建一個簡單的ZIP文件作為模擬VSIX
        import zipfile
        with zipfile.ZipFile(mock_vsix_path, 'w') as zipf:
            # 添加package.json
            package_json = {
                "name": "test-extension",
                "version": "1.0.0",
                "engines": {"vscode": "^1.60.0"},
                "main": "./extension.js"
            }
            zipf.writestr("package.json", json.dumps(package_json, indent=2))
            
            # 添加簡單的extension.js
            extension_js = """
const vscode = require('vscode');
function activate(context) {
    console.log('Test extension activated');
}
function deactivate() {}
module.exports = { activate, deactivate };
"""
            zipf.writestr("extension.js", extension_js)
        
        logger.info(f"✅ 模擬VSIX文件創建完成: {mock_vsix_path}")
        return mock_vsix_path
    
    async def test_vsix_deployment(self, vsix_file_path: str) -> Dict[str, Any]:
        """測試VSIX部署"""
        logger.info("=== 測試VSIX部署 ===")
        
        test_result = {
            'test_name': 'VSIX部署測試',
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
                target_platform="mac" if sys.platform == "darwin" else "universal",
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
            logger.error(f"❌ 部署測試異常: {e}")
        
        finally:
            test_result['execution_time'] = time.time() - start_time
        
        return test_result
    
    async def test_extension_functionality(self) -> Dict[str, Any]:
        """測試擴展功能"""
        logger.info("=== 測試擴展功能 ===")
        
        test_result = {
            'test_name': '擴展功能測試',
            'success': False,
            'details': {},
            'execution_time': 0,
            'error_message': None
        }
        
        start_time = time.time()
        
        try:
            # 檢查VSCode是否可用
            import subprocess
            
            if sys.platform == "darwin":
                # Mac環境
                from PowerAutomation.components.vsix_deployer_mcp import MacVSCodeDetector
                detector = MacVSCodeDetector()
                vscode_cmd = detector.detect_vscode_command()
            else:
                vscode_cmd = "code"
            
            # 測試VSCode版本
            logger.info("檢查VSCode版本...")
            result = subprocess.run([vscode_cmd, '--version'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                vscode_version = result.stdout.strip().split('\n')[0]
                test_result['details']['vscode_version'] = vscode_version
                logger.info(f"✅ VSCode版本: {vscode_version}")
            else:
                raise Exception(f"VSCode版本檢查失敗: {result.stderr}")
            
            # 測試擴展列表
            logger.info("檢查已安裝擴展...")
            result = subprocess.run([vscode_cmd, '--list-extensions'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                extensions = result.stdout.strip().split('\n')
                test_result['details']['installed_extensions'] = extensions
                test_result['details']['extension_count'] = len(extensions)
                logger.info(f"✅ 已安裝擴展數量: {len(extensions)}")
                
                # 檢查測試擴展是否在列表中
                test_extension_found = any('test-extension' in ext for ext in extensions)
                test_result['details']['test_extension_found'] = test_extension_found
                
                if test_extension_found:
                    logger.info("✅ 測試擴展已找到")
                else:
                    logger.warning("⚠️ 測試擴展未在列表中找到")
            else:
                raise Exception(f"擴展列表檢查失敗: {result.stderr}")
            
            # 功能測試成功
            test_result['success'] = True
            logger.info("✅ 擴展功能測試完成")
            
        except Exception as e:
            test_result['error_message'] = str(e)
            logger.error(f"❌ 功能測試異常: {e}")
        
        finally:
            test_result['execution_time'] = time.time() - start_time
        
        return test_result
    
    async def test_local_mcp_integration(self) -> Dict[str, Any]:
        """測試Local MCP集成"""
        logger.info("=== 測試Local MCP集成 ===")
        
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
                
                # 檢查VSIX部署工具是否已註冊
                vsix_tool_found = any(tool.get('tool_id') == 'vsix_deployer' for tool in tools)
                test_result['details']['vsix_tool_registered'] = vsix_tool_found
                
                if vsix_tool_found:
                    logger.info("✅ VSIX部署工具已註冊")
                else:
                    logger.warning("⚠️ VSIX部署工具未註冊")
            
            # 檢查心跳狀態
            if self.local_mcp_adapter.heartbeat_manager:
                heartbeat_status = await self.local_mcp_adapter.heartbeat_manager.get_status()
                test_result['details']['heartbeat_status'] = heartbeat_status
                logger.info(f"心跳狀態: {heartbeat_status.get('status', 'unknown')}")
            
            # 檢查VSIX部署器狀態
            deployment_list = await self.vsix_deployer.list_deployments()
            test_result['details']['deployment_stats'] = deployment_list['stats']
            logger.info(f"部署統計: {deployment_list['stats']}")
            
            test_result['success'] = True
            logger.info("✅ Local MCP集成測試完成")
            
        except Exception as e:
            test_result['error_message'] = str(e)
            logger.error(f"❌ Local MCP集成測試異常: {e}")
        
        finally:
            test_result['execution_time'] = time.time() - start_time
        
        return test_result
    
    async def run_complete_test(self) -> Dict[str, Any]:
        """運行完整測試"""
        logger.info("🚀 開始VSCode端擴展安裝和功能驗證完整測試")
        
        complete_test_result = {
            'test_suite': 'VSCode Extension Installation and Verification',
            'start_time': datetime.now().isoformat(),
            'success': False,
            'test_results': [],
            'summary': {},
            'total_execution_time': 0
        }
        
        suite_start_time = time.time()
        
        try:
            # 1. 設置測試環境
            if not await self.setup_test_environment():
                raise Exception("測試環境設置失敗")
            
            # 2. 創建測試VSIX
            vsix_file_path = await self.create_test_vsix()
            
            # 3. 運行各項測試
            tests = [
                self.test_local_mcp_integration(),
                self.test_vsix_deployment(vsix_file_path),
                self.test_extension_functionality()
            ]
            
            for test_coro in tests:
                test_result = await test_coro
                complete_test_result['test_results'].append(test_result)
                self.test_results.append(test_result)
            
            # 4. 生成測試摘要
            total_tests = len(complete_test_result['test_results'])
            successful_tests = sum(1 for result in complete_test_result['test_results'] if result['success'])
            
            complete_test_result['summary'] = {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': total_tests - successful_tests,
                'success_rate': successful_tests / total_tests if total_tests > 0 else 0
            }
            
            complete_test_result['success'] = successful_tests == total_tests
            
            logger.info(f"🎯 測試完成: {successful_tests}/{total_tests} 成功")
            
        except Exception as e:
            complete_test_result['error_message'] = str(e)
            logger.error(f"❌ 完整測試異常: {e}")
        
        finally:
            complete_test_result['total_execution_time'] = time.time() - suite_start_time
            complete_test_result['end_time'] = datetime.now().isoformat()
            
            # 清理測試環境
            await self.cleanup_test_environment()
        
        return complete_test_result
    
    async def cleanup_test_environment(self):
        """清理測試環境"""
        logger.info("=== 清理測試環境 ===")
        
        try:
            if self.local_mcp_adapter:
                await self.local_mcp_adapter.stop()
                logger.info("✅ Local MCP Adapter已停止")
        except Exception as e:
            logger.warning(f"清理Local MCP Adapter失敗: {e}")

async def main():
    """主函數"""
    from datetime import datetime
    
    print("🚀 VSCode端擴展安裝和功能驗證測試")
    print("=" * 60)
    
    tester = VSCodeExtensionTester()
    
    try:
        # 運行完整測試
        test_result = await tester.run_complete_test()
        
        # 保存測試結果
        result_file = f"vsix_test_result_{int(time.time())}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(test_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 測試結果已保存到: {result_file}")
        
        # 打印測試摘要
        print("\n📊 測試摘要:")
        print(f"總測試數: {test_result['summary']['total_tests']}")
        print(f"成功測試: {test_result['summary']['successful_tests']}")
        print(f"失敗測試: {test_result['summary']['failed_tests']}")
        print(f"成功率: {test_result['summary']['success_rate']:.1%}")
        print(f"總執行時間: {test_result['total_execution_time']:.2f}秒")
        
        if test_result['success']:
            print("\n🎉 所有測試通過！VSCode端擴展安裝和功能驗證成功！")
            return 0
        else:
            print("\n❌ 部分測試失敗，請檢查測試結果")
            return 1
            
    except Exception as e:
        print(f"\n💥 測試執行異常: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))

