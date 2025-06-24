#!/usr/bin/env python3
"""
Enhanced VSCode Installer MCP 註冊狀態檢查腳本
檢查Enhanced VSCode Installer MCP是否已正確註冊在系統中
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# 添加PowerAutomation路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'PowerAutomation'))

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MCPRegistrationChecker:
    """MCP註冊狀態檢查器"""
    
    def __init__(self):
        self.check_results = {}
        
    async def check_enhanced_vscode_installer_registration(self) -> Dict[str, Any]:
        """檢查Enhanced VSCode Installer MCP的註冊狀態"""
        
        print("🔍 檢查Enhanced VSCode Installer MCP註冊狀態")
        print("=" * 60)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "component_name": "Enhanced VSCode Installer MCP",
            "checks": {}
        }
        
        # 1. 檢查文件存在性
        print("📁 檢查組件文件...")
        file_check = self._check_component_files()
        results["checks"]["file_existence"] = file_check
        
        # 2. 檢查導入能力
        print("📦 檢查組件導入...")
        import_check = await self._check_component_import()
        results["checks"]["import_capability"] = import_check
        
        # 3. 檢查工具註冊管理器集成
        print("🔧 檢查工具註冊管理器集成...")
        registry_check = await self._check_tool_registry_integration()
        results["checks"]["tool_registry_integration"] = registry_check
        
        # 4. 檢查Local MCP Adapter集成
        print("🔗 檢查Local MCP Adapter集成...")
        adapter_check = await self._check_local_mcp_adapter_integration()
        results["checks"]["local_mcp_adapter_integration"] = adapter_check
        
        # 5. 檢查工具註冊狀態
        print("📋 檢查工具註冊狀態...")
        registration_check = await self._check_tool_registration_status()
        results["checks"]["tool_registration_status"] = registration_check
        
        # 6. 生成總體評估
        overall_status = self._generate_overall_assessment(results["checks"])
        results["overall_status"] = overall_status
        
        return results
    
    def _check_component_files(self) -> Dict[str, Any]:
        """檢查組件文件存在性"""
        
        required_files = [
            "PowerAutomation/components/enhanced_vscode_installer_mcp.py",
            "PowerAutomation/components/tool_registry_manager.py",
            "PowerAutomation/components/local_mcp_adapter.py"
        ]
        
        file_status = {}
        all_files_exist = True
        
        for file_path in required_files:
            exists = os.path.exists(file_path)
            file_status[file_path] = {
                "exists": exists,
                "size": os.path.getsize(file_path) if exists else 0
            }
            if not exists:
                all_files_exist = False
            
            status_icon = "✅" if exists else "❌"
            print(f"  {status_icon} {file_path}: {'存在' if exists else '不存在'}")
        
        return {
            "success": all_files_exist,
            "files": file_status,
            "message": "所有必需文件存在" if all_files_exist else "缺少必需文件"
        }
    
    async def _check_component_import(self) -> Dict[str, Any]:
        """檢查組件導入能力"""
        
        try:
            # 嘗試導入Enhanced VSCode Installer MCP
            from PowerAutomation.components.enhanced_vscode_installer_mcp import (
                EnhancedMacVSCodeDetector,
                EnhancedMacExtensionManager,
                ExtensionFunctionalityTester,
                EnhancedLocalMCPVSCodeInstaller
            )
            
            print("  ✅ Enhanced VSCode Installer MCP組件導入成功")
            
            # 嘗試導入工具註冊管理器
            from PowerAutomation.components.tool_registry_manager import (
                ToolRegistryManager,
                LocalToolInfo,
                ToolStatus
            )
            
            print("  ✅ 工具註冊管理器導入成功")
            
            return {
                "success": True,
                "imported_components": [
                    "EnhancedMacVSCodeDetector",
                    "EnhancedMacExtensionManager", 
                    "ExtensionFunctionalityTester",
                    "EnhancedLocalMCPVSCodeInstaller",
                    "ToolRegistryManager",
                    "LocalToolInfo",
                    "ToolStatus"
                ],
                "message": "所有組件導入成功"
            }
            
        except ImportError as e:
            print(f"  ❌ 組件導入失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "組件導入失敗"
            }
    
    async def _check_tool_registry_integration(self) -> Dict[str, Any]:
        """檢查工具註冊管理器集成"""
        
        try:
            from PowerAutomation.components.enhanced_vscode_installer_mcp import EnhancedLocalMCPVSCodeInstaller
            from PowerAutomation.components.tool_registry_manager import ToolRegistryManager
            
            # 檢查Enhanced VSCode Installer MCP是否有註冊方法
            installer_class = EnhancedLocalMCPVSCodeInstaller
            has_register_method = hasattr(installer_class, '_register_installer_tools')
            
            print(f"  {'✅' if has_register_method else '❌'} Enhanced VSCode Installer MCP有註冊方法: {has_register_method}")
            
            # 檢查工具註冊管理器的註冊方法
            registry_class = ToolRegistryManager
            has_registry_method = hasattr(registry_class, 'register_tool')
            
            print(f"  {'✅' if has_registry_method else '❌'} 工具註冊管理器有註冊方法: {has_registry_method}")
            
            return {
                "success": has_register_method and has_registry_method,
                "installer_has_register_method": has_register_method,
                "registry_has_register_method": has_registry_method,
                "message": "工具註冊集成正常" if (has_register_method and has_registry_method) else "工具註冊集成有問題"
            }
            
        except Exception as e:
            print(f"  ❌ 工具註冊集成檢查失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "工具註冊集成檢查失敗"
            }
    
    async def _check_local_mcp_adapter_integration(self) -> Dict[str, Any]:
        """檢查Local MCP Adapter集成"""
        
        try:
            from PowerAutomation.components.local_mcp_adapter import LocalMCPAdapter
            
            # 檢查Local MCP Adapter是否有工具註冊管理器
            adapter_class = LocalMCPAdapter
            has_tool_registry = hasattr(adapter_class, 'tool_registry_manager')
            
            print(f"  {'✅' if has_tool_registry else '❌'} Local MCP Adapter有工具註冊管理器屬性: {has_tool_registry}")
            
            # 檢查是否有啟動工具註冊管理器的方法
            has_start_registry = any('tool_registry' in method for method in dir(adapter_class) if 'start' in method.lower())
            
            print(f"  {'✅' if has_start_registry else '❌'} Local MCP Adapter有啟動工具註冊的方法: {has_start_registry}")
            
            return {
                "success": has_tool_registry,
                "has_tool_registry_attribute": has_tool_registry,
                "has_start_registry_method": has_start_registry,
                "message": "Local MCP Adapter集成正常" if has_tool_registry else "Local MCP Adapter集成有問題"
            }
            
        except Exception as e:
            print(f"  ❌ Local MCP Adapter集成檢查失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Local MCP Adapter集成檢查失敗"
            }
    
    async def _check_tool_registration_status(self) -> Dict[str, Any]:
        """檢查工具註冊狀態"""
        
        try:
            # 嘗試創建Local MCP Adapter實例並檢查註冊狀態
            from PowerAutomation.components.local_mcp_adapter import LocalMCPAdapter
            from PowerAutomation.components.enhanced_vscode_installer_mcp import create_enhanced_vscode_installer
            
            print("  🚀 嘗試創建Local MCP Adapter實例...")
            
            # 創建Local MCP Adapter (使用正確的參數)
            adapter = LocalMCPAdapter()
            
            # 檢查工具註冊管理器是否已初始化
            has_registry_manager = adapter.tool_registry_manager is not None
            print(f"  {'✅' if has_registry_manager else '❌'} 工具註冊管理器已初始化: {has_registry_manager}")
            
            if not has_registry_manager:
                # 嘗試啟動核心組件來初始化工具註冊管理器
                print("  🔄 嘗試啟動Local MCP Adapter...")
                await adapter.start()
                has_registry_manager = adapter.tool_registry_manager is not None
                print(f"  {'✅' if has_registry_manager else '❌'} 啟動後工具註冊管理器狀態: {has_registry_manager}")
            
            if has_registry_manager:
                # 檢查已註冊的工具
                registered_tools = adapter.tool_registry_manager.get_registered_tools()
                enhanced_vscode_registered = any(
                    tool.tool_id == "enhanced_vscode_installer" 
                    for tool in registered_tools
                )
                
                print(f"  {'✅' if enhanced_vscode_registered else '❌'} Enhanced VSCode Installer已註冊: {enhanced_vscode_registered}")
                print(f"  📊 已註冊工具數量: {len(registered_tools)}")
                
                # 列出已註冊的工具
                for tool in registered_tools:
                    print(f"    - {tool.tool_id}: {tool.tool_name}")
                
                return {
                    "success": enhanced_vscode_registered,
                    "registry_manager_initialized": has_registry_manager,
                    "enhanced_vscode_registered": enhanced_vscode_registered,
                    "total_registered_tools": len(registered_tools),
                    "registered_tools": [
                        {
                            "tool_id": tool.tool_id,
                            "tool_name": tool.tool_name,
                            "status": tool.status.value if hasattr(tool.status, 'value') else str(tool.status)
                        }
                        for tool in registered_tools
                    ],
                    "message": "Enhanced VSCode Installer已註冊" if enhanced_vscode_registered else "Enhanced VSCode Installer未註冊"
                }
            else:
                return {
                    "success": False,
                    "registry_manager_initialized": False,
                    "message": "工具註冊管理器未初始化"
                }
                
        except Exception as e:
            print(f"  ❌ 工具註冊狀態檢查失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "工具註冊狀態檢查失敗"
            }
    
    def _generate_overall_assessment(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """生成總體評估"""
        
        # 計算成功的檢查項目
        successful_checks = sum(1 for check in checks.values() if check.get("success", False))
        total_checks = len(checks)
        success_rate = successful_checks / total_checks if total_checks > 0 else 0
        
        # 判斷總體狀態
        if success_rate == 1.0:
            status = "fully_registered"
            message = "Enhanced VSCode Installer MCP已完全註冊並集成"
            icon = "✅"
        elif success_rate >= 0.8:
            status = "mostly_registered"
            message = "Enhanced VSCode Installer MCP大部分功能已註冊，有少量問題"
            icon = "⚠️"
        elif success_rate >= 0.5:
            status = "partially_registered"
            message = "Enhanced VSCode Installer MCP部分註冊，需要修復"
            icon = "🔧"
        else:
            status = "not_registered"
            message = "Enhanced VSCode Installer MCP未正確註冊，需要完整設置"
            icon = "❌"
        
        print("\n" + "=" * 60)
        print(f"{icon} 總體評估: {message}")
        print(f"📊 成功率: {successful_checks}/{total_checks} ({success_rate:.1%})")
        print("=" * 60)
        
        return {
            "status": status,
            "success_rate": success_rate,
            "successful_checks": successful_checks,
            "total_checks": total_checks,
            "message": message,
            "icon": icon
        }

async def main():
    """主函數"""
    print("🔍 Enhanced VSCode Installer MCP 註冊狀態檢查")
    print("=" * 60)
    
    checker = MCPRegistrationChecker()
    
    try:
        # 執行檢查
        results = await checker.check_enhanced_vscode_installer_registration()
        
        # 保存檢查結果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"enhanced_vscode_installer_mcp_registration_check_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 詳細檢查報告已保存: {report_file}")
        
        # 返回狀態碼
        overall_status = results["overall_status"]["status"]
        if overall_status == "fully_registered":
            return 0
        elif overall_status in ["mostly_registered", "partially_registered"]:
            return 1
        else:
            return 2
            
    except Exception as e:
        print(f"❌ 檢查過程中發生錯誤: {e}")
        return 3

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

