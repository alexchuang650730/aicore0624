#!/usr/bin/env python3
"""
PowerAutomation Local MCP 簡化測試

快速驗證MCP適配器的基本功能

Author: Manus AI
Version: 1.0.0
Date: 2025-06-23
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from shared.utils import setup_logging


async def test_basic_functionality():
    """測試基本功能"""
    logger = setup_logging("INFO", console_enabled=True, file_enabled=False)
    
    print("🚀 開始PowerAutomation MCP基本功能測試...")
    print("="*60)
    
    test_results = []
    
    # 測試1: 配置文件加載
    print("📋 測試1: 配置文件加載")
    try:
        import toml
        with open("config.toml", 'r', encoding='utf-8') as f:
            config = toml.load(f)
        
        required_sections = ["server", "manus", "automation", "storage", "extension"]
        missing_sections = [section for section in required_sections if section not in config]
        
        if not missing_sections:
            print("✅ 配置文件加載成功")
            test_results.append({"test": "config_load", "success": True})
        else:
            print(f"❌ 配置文件缺少段落: {missing_sections}")
            test_results.append({"test": "config_load", "success": False})
            
    except Exception as e:
        print(f"❌ 配置文件加載失敗: {e}")
        test_results.append({"test": "config_load", "success": False})
    
    # 測試2: 模組導入
    print("\n📦 測試2: 模組導入")
    try:
        from powerautomation_local_mcp import PowerAutomationLocalMCP
        from shared.utils import get_system_info
        from shared.exceptions import PowerAutomationError
        
        print("✅ 核心模組導入成功")
        test_results.append({"test": "module_import", "success": True})
        
    except Exception as e:
        print(f"❌ 模組導入失敗: {e}")
        test_results.append({"test": "module_import", "success": False})
        return test_results
    
    # 測試3: MCP適配器創建
    print("\n🔧 測試3: MCP適配器創建")
    try:
        mcp_adapter = PowerAutomationLocalMCP("config.toml")
        print("✅ MCP適配器創建成功")
        test_results.append({"test": "mcp_creation", "success": True})
        
    except Exception as e:
        print(f"❌ MCP適配器創建失敗: {e}")
        test_results.append({"test": "mcp_creation", "success": False})
        return test_results
    
    # 測試4: 系統信息獲取
    print("\n💻 測試4: 系統信息獲取")
    try:
        system_info = get_system_info()
        
        required_keys = ["platform", "cpu", "memory", "disk"]
        missing_keys = [key for key in required_keys if key not in system_info]
        
        if not missing_keys:
            print("✅ 系統信息獲取成功")
            print(f"   - 平台: {system_info.get('platform', 'Unknown')}")
            print(f"   - CPU核心: {system_info.get('cpu', {}).get('count', 'Unknown')}")
            print(f"   - 內存: {system_info.get('memory', {}).get('total_gb', 'Unknown')} GB")
            test_results.append({"test": "system_info", "success": True})
        else:
            print(f"❌ 系統信息缺少字段: {missing_keys}")
            test_results.append({"test": "system_info", "success": False})
            
    except Exception as e:
        print(f"❌ 系統信息獲取失敗: {e}")
        test_results.append({"test": "system_info", "success": False})
    
    # 測試5: 目錄結構檢查
    print("\n📁 測試5: 目錄結構檢查")
    try:
        required_dirs = [
            "server", "extension", "shared", "tests", "docs",
            "server/integrations", "server/automation", "server/storage",
            "extension/ui", "extension/commands", "extension/settings"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                missing_dirs.append(dir_path)
        
        if not missing_dirs:
            print("✅ 目錄結構完整")
            test_results.append({"test": "directory_structure", "success": True})
        else:
            print(f"❌ 缺少目錄: {missing_dirs}")
            test_results.append({"test": "directory_structure", "success": False})
            
    except Exception as e:
        print(f"❌ 目錄結構檢查失敗: {e}")
        test_results.append({"test": "directory_structure", "success": False})
    
    # 測試6: 核心文件檢查
    print("\n📄 測試6: 核心文件檢查")
    try:
        required_files = [
            "powerautomation_local_mcp.py",
            "config.toml",
            "cli.py",
            "__init__.py",
            "shared/utils.py",
            "shared/exceptions.py",
            "server/server_manager.py",
            "server/integrations/manus_integration.py",
            "server/automation/automation_engine.py",
            "server/storage/data_storage.py",
            "extension/extension_manager.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if not missing_files:
            print("✅ 核心文件完整")
            test_results.append({"test": "core_files", "success": True})
        else:
            print(f"❌ 缺少文件: {missing_files}")
            test_results.append({"test": "core_files", "success": False})
            
    except Exception as e:
        print(f"❌ 核心文件檢查失敗: {e}")
        test_results.append({"test": "core_files", "success": False})
    
    # 測試7: 依賴包檢查
    print("\n📦 測試7: 依賴包檢查")
    try:
        required_packages = [
            "toml", "aiohttp", "flask", "flask_cors", 
            "playwright", "psutil", "json", "logging"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if not missing_packages:
            print("✅ 依賴包完整")
            test_results.append({"test": "dependencies", "success": True})
        else:
            print(f"❌ 缺少依賴包: {missing_packages}")
            test_results.append({"test": "dependencies", "success": False})
            
    except Exception as e:
        print(f"❌ 依賴包檢查失敗: {e}")
        test_results.append({"test": "dependencies", "success": False})
    
    # 生成測試報告
    print("\n" + "="*60)
    print("📊 測試結果摘要")
    print("="*60)
    
    total_tests = len(test_results)
    successful_tests = sum(1 for result in test_results if result["success"])
    failed_tests = total_tests - successful_tests
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"總測試數: {total_tests}")
    print(f"成功測試: {successful_tests}")
    print(f"失敗測試: {failed_tests}")
    print(f"成功率: {success_rate:.1f}%")
    print("-" * 60)
    
    for result in test_results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {result['test']}")
    
    print("="*60)
    
    # 保存測試報告
    report = {
        "test_summary": {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate
        },
        "test_details": test_results,
        "timestamp": time.time()
    }
    
    with open("basic_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"測試報告已保存到: basic_test_report.json")
    
    if success_rate >= 80:
        print("\n🎉 基本功能測試通過！")
        return True
    else:
        print("\n⚠️ 基本功能測試失敗，請檢查錯誤信息")
        return False


async def main():
    """主函數"""
    try:
        success = await test_basic_functionality()
        return 0 if success else 1
    except Exception as e:
        print(f"測試執行失敗: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

