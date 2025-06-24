#!/usr/bin/env python3
"""
簡化的Enhanced VSCode Installer MCP註冊狀態檢查
"""

import sys
import os

# 添加PowerAutomation路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'PowerAutomation'))

def check_registration():
    print("🔍 Enhanced VSCode Installer MCP 註冊狀態檢查")
    print("=" * 60)
    
    try:
        # 1. 檢查文件存在
        print("📁 檢查組件文件...")
        files = [
            "PowerAutomation/components/enhanced_vscode_installer_mcp.py",
            "PowerAutomation/components/tool_registry_manager.py",
            "PowerAutomation/components/local_mcp_adapter.py"
        ]
        
        for file_path in files:
            exists = os.path.exists(file_path)
            print(f"  {'✅' if exists else '❌'} {file_path}: {'存在' if exists else '不存在'}")
        
        # 2. 檢查導入
        print("\n📦 檢查組件導入...")
        from PowerAutomation.components.enhanced_vscode_installer_mcp import (
            EnhancedLocalMCPVSCodeInstaller
        )
        print("  ✅ Enhanced VSCode Installer MCP導入成功")
        
        from PowerAutomation.components.tool_registry_manager import (
            ToolRegistryManager
        )
        print("  ✅ 工具註冊管理器導入成功")
        
        # 3. 檢查註冊方法
        print("\n🔧 檢查註冊方法...")
        has_register_method = hasattr(EnhancedLocalMCPVSCodeInstaller, '_register_installer_tools')
        print(f"  {'✅' if has_register_method else '❌'} Enhanced VSCode Installer有註冊方法: {has_register_method}")
        
        has_registry_method = hasattr(ToolRegistryManager, 'register_tool')
        print(f"  {'✅' if has_registry_method else '❌'} 工具註冊管理器有註冊方法: {has_registry_method}")
        
        # 4. 檢查工具ID
        print("\n🆔 檢查工具ID配置...")
        # 讀取enhanced_vscode_installer_mcp.py文件內容
        with open("PowerAutomation/components/enhanced_vscode_installer_mcp.py", 'r') as f:
            content = f.read()
            
        has_tool_id = 'tool_id="enhanced_vscode_installer"' in content
        print(f"  {'✅' if has_tool_id else '❌'} 工具ID配置正確: {has_tool_id}")
        
        # 總結
        print("\n" + "=" * 60)
        all_checks = [True, True, has_register_method, has_registry_method, has_tool_id]
        success_count = sum(all_checks)
        
        if success_count == len(all_checks):
            print("✅ Enhanced VSCode Installer MCP 組件已準備就緒")
            print("📋 所有必要的註冊機制都已實現")
            print("🔧 需要通過Local MCP Adapter啟動來完成實際註冊")
        else:
            print(f"⚠️ Enhanced VSCode Installer MCP 部分就緒 ({success_count}/{len(all_checks)})")
        
        print("=" * 60)
        
        return success_count == len(all_checks)
        
    except Exception as e:
        print(f"❌ 檢查過程中發生錯誤: {e}")
        return False

if __name__ == "__main__":
    success = check_registration()
    sys.exit(0 if success else 1)
