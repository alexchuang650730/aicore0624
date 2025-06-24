#!/usr/bin/env python3
"""
Enhanced VSCode Installer MCP 註冊配置腳本
確保Enhanced VSCode Installer MCP正確註冊到系統中
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any

# 添加PowerAutomation路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'PowerAutomation'))

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class EnhancedVSCodeInstallerMCPRegistrar:
    """Enhanced VSCode Installer MCP註冊器"""
    
    def __init__(self):
        self.registration_results = {}
        
    async def register_enhanced_vscode_installer_mcp(self) -> Dict[str, Any]:
        """註冊Enhanced VSCode Installer MCP到系統"""
        
        print("🚀 開始註冊Enhanced VSCode Installer MCP")
        print("=" * 60)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "component_name": "Enhanced VSCode Installer MCP",
            "registration_steps": {}
        }
        
        try:
            # 步驟1: 導入必要組件
            print("📦 步驟1: 導入必要組件...")
            import_result = await self._import_components()
            results["registration_steps"]["import_components"] = import_result
            
            if not import_result["success"]:
                return self._generate_failure_result(results, "組件導入失敗")
            
            # 步驟2: 創建Local MCP Adapter實例
            print("🔧 步驟2: 創建Local MCP Adapter實例...")
            adapter_result = await self._create_adapter_instance()
            results["registration_steps"]["create_adapter"] = adapter_result
            
            if not adapter_result["success"]:
                return self._generate_failure_result(results, "Local MCP Adapter創建失敗")
            
            # 步驟3: 創建Enhanced VSCode Installer實例
            print("🛠️ 步驟3: 創建Enhanced VSCode Installer實例...")
            installer_result = await self._create_installer_instance(adapter_result["adapter"])
            results["registration_steps"]["create_installer"] = installer_result
            
            if not installer_result["success"]:
                return self._generate_failure_result(results, "Enhanced VSCode Installer創建失敗")
            
            # 步驟4: 驗證註冊狀態
            print("✅ 步驟4: 驗證註冊狀態...")
            verification_result = await self._verify_registration(adapter_result["adapter"])
            results["registration_steps"]["verify_registration"] = verification_result
            
            # 步驟5: 生成註冊配置文件
            print("📄 步驟5: 生成註冊配置文件...")
            config_result = await self._generate_registration_config(
                adapter_result["adapter"], 
                installer_result["installer"]
            )
            results["registration_steps"]["generate_config"] = config_result
            
            # 生成總體結果
            overall_success = all(
                step.get("success", False) 
                for step in results["registration_steps"].values()
            )
            
            results["overall_result"] = {
                "success": overall_success,
                "message": "Enhanced VSCode Installer MCP註冊成功" if overall_success else "Enhanced VSCode Installer MCP註冊部分成功",
                "registered_tool_id": "enhanced_vscode_installer",
                "registration_complete": overall_success
            }
            
            return results
            
        except Exception as e:
            logger.error(f"註冊過程中發生錯誤: {e}")
            return self._generate_failure_result(results, f"註冊過程異常: {str(e)}")
    
    async def _import_components(self) -> Dict[str, Any]:
        """導入必要組件"""
        
        try:
            from PowerAutomation.components.local_mcp_adapter import LocalMCPAdapter
            from PowerAutomation.components.enhanced_vscode_installer_mcp import (
                EnhancedLocalMCPVSCodeInstaller,
                create_enhanced_vscode_installer
            )
            from PowerAutomation.components.tool_registry_manager import (
                ToolRegistryManager,
                LocalToolInfo,
                ToolStatus
            )
            
            print("  ✅ 所有必要組件導入成功")
            
            return {
                "success": True,
                "imported_modules": [
                    "LocalMCPAdapter",
                    "EnhancedLocalMCPVSCodeInstaller", 
                    "create_enhanced_vscode_installer",
                    "ToolRegistryManager",
                    "LocalToolInfo",
                    "ToolStatus"
                ],
                "message": "組件導入成功"
            }
            
        except ImportError as e:
            print(f"  ❌ 組件導入失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "組件導入失敗"
            }
    
    async def _create_adapter_instance(self) -> Dict[str, Any]:
        """創建Local MCP Adapter實例"""
        
        try:
            from PowerAutomation.components.local_mcp_adapter import LocalMCPAdapter
            
            # 創建Local MCP Adapter實例
            adapter = LocalMCPAdapter()
            
            print(f"  ✅ Local MCP Adapter創建成功 - ID: {adapter.adapter_id}")
            
            return {
                "success": True,
                "adapter": adapter,
                "adapter_id": adapter.adapter_id,
                "message": "Local MCP Adapter創建成功"
            }
            
        except Exception as e:
            print(f"  ❌ Local MCP Adapter創建失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Local MCP Adapter創建失敗"
            }
    
    async def _create_installer_instance(self, adapter) -> Dict[str, Any]:
        """創建Enhanced VSCode Installer實例"""
        
        try:
            from PowerAutomation.components.enhanced_vscode_installer_mcp import (
                EnhancedLocalMCPVSCodeInstaller
            )
            
            # 創建Enhanced VSCode Installer實例
            installer = EnhancedLocalMCPVSCodeInstaller(adapter)
            
            print("  ✅ Enhanced VSCode Installer創建成功")
            print(f"  📋 工具ID: enhanced_vscode_installer")
            print(f"  🔧 版本: 2.0.0")
            
            return {
                "success": True,
                "installer": installer,
                "tool_id": "enhanced_vscode_installer",
                "version": "2.0.0",
                "message": "Enhanced VSCode Installer創建成功"
            }
            
        except Exception as e:
            print(f"  ❌ Enhanced VSCode Installer創建失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Enhanced VSCode Installer創建失敗"
            }
    
    async def _verify_registration(self, adapter) -> Dict[str, Any]:
        """驗證註冊狀態"""
        
        try:
            # 檢查工具註冊管理器
            has_registry = adapter.tool_registry_manager is not None
            print(f"  {'✅' if has_registry else '❌'} 工具註冊管理器: {'已初始化' if has_registry else '未初始化'}")
            
            if has_registry:
                # 檢查已註冊的工具
                registered_tools = adapter.tool_registry_manager.get_registered_tools()
                enhanced_vscode_registered = any(
                    tool.tool_id == "enhanced_vscode_installer" 
                    for tool in registered_tools
                )
                
                print(f"  {'✅' if enhanced_vscode_registered else '❌'} Enhanced VSCode Installer: {'已註冊' if enhanced_vscode_registered else '未註冊'}")
                print(f"  📊 已註冊工具總數: {len(registered_tools)}")
                
                # 列出所有已註冊的工具
                if registered_tools:
                    print("  📋 已註冊工具列表:")
                    for tool in registered_tools:
                        print(f"    - {tool.tool_id}: {tool.tool_name}")
                
                return {
                    "success": enhanced_vscode_registered,
                    "registry_manager_available": has_registry,
                    "enhanced_vscode_registered": enhanced_vscode_registered,
                    "total_registered_tools": len(registered_tools),
                    "registered_tools": [
                        {
                            "tool_id": tool.tool_id,
                            "tool_name": tool.tool_name,
                            "status": str(tool.status)
                        }
                        for tool in registered_tools
                    ],
                    "message": "Enhanced VSCode Installer已註冊" if enhanced_vscode_registered else "Enhanced VSCode Installer未註冊"
                }
            else:
                return {
                    "success": False,
                    "registry_manager_available": False,
                    "message": "工具註冊管理器未初始化"
                }
                
        except Exception as e:
            print(f"  ❌ 註冊狀態驗證失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "註冊狀態驗證失敗"
            }
    
    async def _generate_registration_config(self, adapter, installer) -> Dict[str, Any]:
        """生成註冊配置文件"""
        
        try:
            # 生成配置信息
            config = {
                "enhanced_vscode_installer_mcp": {
                    "tool_id": "enhanced_vscode_installer",
                    "tool_name": "Enhanced VSCode Extension Installer",
                    "version": "2.0.0",
                    "description": "增強的Mac端VSCode擴展安裝和驗證工具",
                    "capabilities": [
                        "mac_vscode_detection",
                        "extension_installation", 
                        "functionality_testing",
                        "performance_testing",
                        "real_cli_integration"
                    ],
                    "endpoint": "http://localhost:8080/api/v1/vscode/install",
                    "platform": "Mac",
                    "registration_status": "ready",
                    "registration_timestamp": datetime.now().isoformat()
                },
                "local_mcp_adapter": {
                    "adapter_id": adapter.adapter_id,
                    "status": "initialized",
                    "tool_registry_manager": adapter.tool_registry_manager is not None,
                    "heartbeat_manager": adapter.heartbeat_manager is not None,
                    "smart_routing_engine": adapter.smart_routing_engine is not None
                },
                "registration_instructions": {
                    "manual_registration": "通過Local MCP Adapter啟動來完成實際註冊",
                    "startup_command": "await adapter.start()",
                    "verification_command": "adapter.tool_registry_manager.get_registered_tools()",
                    "notes": [
                        "Enhanced VSCode Installer MCP組件已準備就緒",
                        "所有必要的註冊機制都已實現",
                        "需要通過Local MCP Adapter啟動來完成實際註冊"
                    ]
                }
            }
            
            # 保存配置文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            config_file = f"enhanced_vscode_installer_mcp_registration_config_{timestamp}.json"
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"  ✅ 註冊配置文件已生成: {config_file}")
            
            return {
                "success": True,
                "config_file": config_file,
                "config": config,
                "message": "註冊配置文件生成成功"
            }
            
        except Exception as e:
            print(f"  ❌ 註冊配置文件生成失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "註冊配置文件生成失敗"
            }
    
    def _generate_failure_result(self, results: Dict[str, Any], error_message: str) -> Dict[str, Any]:
        """生成失敗結果"""
        
        results["overall_result"] = {
            "success": False,
            "message": error_message,
            "registration_complete": False
        }
        
        return results

async def main():
    """主函數"""
    print("🚀 Enhanced VSCode Installer MCP 註冊配置")
    print("=" * 60)
    
    registrar = EnhancedVSCodeInstallerMCPRegistrar()
    
    try:
        # 執行註冊
        results = await registrar.register_enhanced_vscode_installer_mcp()
        
        # 保存註冊結果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"enhanced_vscode_installer_mcp_registration_result_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        # 輸出結果
        print("\n" + "=" * 60)
        print("📊 Enhanced VSCode Installer MCP 註冊結果")
        print("=" * 60)
        
        overall_result = results.get("overall_result", {})
        success = overall_result.get("success", False)
        
        print(f"📈 總體結果: {'✅ 成功' if success else '❌ 失敗'}")
        print(f"📋 註冊狀態: {overall_result.get('message', '未知')}")
        print(f"🆔 工具ID: {overall_result.get('registered_tool_id', 'N/A')}")
        print(f"📄 詳細報告: {report_file}")
        
        # 顯示各步驟結果
        print("\n📋 註冊步驟結果:")
        for step_name, step_result in results.get("registration_steps", {}).items():
            status = "✅" if step_result.get("success", False) else "❌"
            print(f"{status} {step_name}: {step_result.get('message', '未知')}")
        
        print("=" * 60)
        
        if success:
            print("🎉 Enhanced VSCode Installer MCP 註冊配置完成！")
            print("💡 提示: 通過Local MCP Adapter啟動來完成實際註冊")
        else:
            print("⚠️ Enhanced VSCode Installer MCP 註冊配置需要進一步處理")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ 註冊配置過程中發生錯誤: {e}")
        return 2

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

