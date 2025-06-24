#!/usr/bin/env python3
"""
簡化的VSCode擴展安裝測試
"""

import asyncio
import json
import os
import sys
import tempfile
import zipfile
from datetime import datetime

# 添加PowerAutomation路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'PowerAutomation'))

async def test_basic_functionality():
    """測試基本功能"""
    print("🚀 開始基本功能測試")
    
    try:
        # 測試導入
        print("📦 測試組件導入...")
        from PowerAutomation.components.enhanced_vscode_installer_mcp import (
            EnhancedMacVSCodeDetector,
            EnhancedMacExtensionManager
        )
        print("✅ 組件導入成功")
        
        # 測試VSCode檢測
        print("🔍 測試VSCode檢測...")
        detector = EnhancedMacVSCodeDetector()
        
        # 在Linux環境下模擬測試
        print("ℹ️ 在Linux環境下運行，跳過Mac特定測試")
        
        # 測試擴展管理器
        print("📁 測試擴展管理器...")
        manager = EnhancedMacExtensionManager()
        print(f"擴展目錄: {manager.extensions_dir}")
        print(f"用戶數據目錄: {manager.user_data_dir}")
        print("✅ 擴展管理器測試成功")
        
        # 創建測試VSIX文件
        print("📦 創建測試VSIX文件...")
        temp_dir = tempfile.mkdtemp()
        vsix_path = os.path.join(temp_dir, "test-extension-1.0.0.vsix")
        
        with zipfile.ZipFile(vsix_path, 'w') as zipf:
            package_json = {
                "name": "test-extension",
                "version": "1.0.0",
                "description": "Test extension",
                "engines": {"vscode": "^1.60.0"}
            }
            zipf.writestr("package.json", json.dumps(package_json, indent=2))
        
        print(f"✅ 測試VSIX文件創建成功: {vsix_path}")
        
        print("🎉 基本功能測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

async def main():
    """主函數"""
    print("=" * 50)
    print("簡化VSCode擴展安裝測試")
    print("=" * 50)
    
    success = await test_basic_functionality()
    
    print("=" * 50)
    print(f"測試結果: {'✅ 成功' if success else '❌ 失敗'}")
    print("=" * 50)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
