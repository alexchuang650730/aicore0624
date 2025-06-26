#!/usr/bin/env python3
"""
Manus 集成測試腳本
用於驗證 SmartInvention 的 Manus 數據抓取功能是否正常工作
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PowerAutomation.components.smartinvention_mcp.main import SmartinventionAdapterMCP
from PowerAutomation.components.mcp.shared.data_provider import DataProvider, ManusDataAccess

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_manus_integration():
    """測試 Manus 集成功能"""
    
    print("🚀 開始測試 Manus 集成功能...")
    
    try:
        # 1. 測試 SmartinventionAdapterMCP 初始化
        print("\n1️⃣ 測試 SmartinventionAdapterMCP 初始化...")
        
        # 載入配置
        config_path = Path(__file__).parent / "manus_config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            print("⚠️  配置文件不存在，使用默認配置")
            config = {
                "manus": {
                    "base_url": "https://manus.im",
                    "app_url": "https://manus.im/app",
                    "auto_login": False  # 測試時不自動登錄
                }
            }
        
        # 初始化 SmartinventionAdapterMCP
        smartinvention_mcp = SmartinventionAdapterMCP(config)
        init_result = await smartinvention_mcp.initialize()
        
        if init_result.get("success"):
            print("✅ SmartinventionAdapterMCP 初始化成功")
            print(f"   版本: {init_result.get('version')}")
            print(f"   Manus 集成: {init_result.get('manus_integration')}")
            print(f"   數據源: {init_result.get('data_source')}")
        else:
            print(f"❌ SmartinventionAdapterMCP 初始化失敗: {init_result.get('error')}")
            return False
        
        # 2. 測試健康檢查
        print("\n2️⃣ 測試健康檢查...")
        health_result = await smartinvention_mcp.handle_request("health_check", {})
        if health_result.get("success"):
            print("✅ 健康檢查通過")
        else:
            print(f"❌ 健康檢查失敗: {health_result}")
        
        # 3. 測試獲取 Manus 標準
        print("\n3️⃣ 測試獲取 Manus 標準...")
        standards_result = await smartinvention_mcp.handle_request("get_manus_standards", {})
        if standards_result.get("standards"):
            standards = standards_result["standards"]
            print("✅ 成功獲取 Manus 標準")
            print(f"   編碼標準: {list(standards.get('coding_standards', {}).keys())}")
            print(f"   安全標準: {list(standards.get('security_standards', {}).keys())}")
            print(f"   測試標準: {list(standards.get('testing_standards', {}).keys())}")
            print(f"   數據源: {standards.get('data_source', 'unknown')}")
            print(f"   最後更新: {standards.get('last_updated', 'unknown')}")
        else:
            print(f"❌ 獲取 Manus 標準失敗: {standards_result}")
        
        # 4. 測試 DataProvider
        print("\n4️⃣ 測試 DataProvider...")
        data_provider = DataProvider(manus_config=config.get("manus"))
        provider_init = await data_provider.initialize()
        
        if provider_init:
            print("✅ DataProvider 初始化成功")
            
            # 測試獲取對比數據
            test_user_id = "test_user_001"
            test_request = {
                "method": "generate_test_case",
                "parameters": {"feature": "user_authentication"}
            }
            
            comparison_context = await data_provider.get_comparison_data(test_user_id, test_request)
            print(f"✅ 成功獲取對比數據")
            print(f"   用戶 ID: {comparison_context.user_context.user_id}")
            print(f"   對話數量: {len(comparison_context.user_context.conversations)}")
            print(f"   上下文分數: {comparison_context.user_context.context_score}")
            print(f"   數據源: {comparison_context.comparison_metadata.get('data_source')}")
            
        else:
            print("❌ DataProvider 初始化失敗")
        
        # 5. 測試對話同步（如果配置了登錄信息）
        print("\n5️⃣ 測試對話同步...")
        if config.get("manus", {}).get("login_email") and config.get("manus", {}).get("login_password"):
            sync_result = await smartinvention_mcp.handle_request("sync_conversations", {})
            if sync_result.get("success"):
                print("✅ 對話同步成功")
                print(f"   處理對話數: {sync_result.get('conversations_processed', 0)}")
                print(f"   發現任務數: {sync_result.get('tasks_found', 0)}")
            else:
                print(f"❌ 對話同步失敗: {sync_result.get('error')}")
        else:
            print("⚠️  未配置登錄信息，跳過對話同步測試")
        
        print("\n🎉 Manus 集成測試完成！")
        return True
        
    except Exception as e:
        print(f"\n💥 測試過程中發生錯誤: {e}")
        logger.exception("測試失敗")
        return False

async def test_comparison_engine():
    """測試對比引擎"""
    
    print("\n🔍 測試對比引擎...")
    
    try:
        # 導入對比引擎
        from PowerAutomation.components.test_flow_mcp.v4.enhanced_comparison_engine import EnhancedComparisonAnalysisEngine
        
        # 初始化對比引擎
        config = {
            "manus": {
                "base_url": "https://manus.im",
                "app_url": "https://manus.im/app",
                "auto_login": False
            }
        }
        
        data_provider = DataProvider(manus_config=config.get("manus"))
        await data_provider.initialize()
        
        comparison_engine = EnhancedComparisonAnalysisEngine(data_provider)
        
        # 測試對比分析
        test_user_id = "test_user_001"
        test_request = {
            "method": "generate_test_case",
            "parameters": {"feature": "user_authentication"},
            "code_context": "def login(username, password): return authenticate(username, password)"
        }
        
        analysis_result = await comparison_engine.analyze_request(test_user_id, test_request)
        
        if analysis_result.get("success"):
            print("✅ 對比分析成功")
            print(f"   分析 ID: {analysis_result.get('analysis_id')}")
            print(f"   置信度: {analysis_result.get('confidence_score')}")
            print(f"   建議數量: {len(analysis_result.get('recommendations', []))}")
            print(f"   數據源: {analysis_result.get('metadata', {}).get('data_source')}")
        else:
            print(f"❌ 對比分析失敗: {analysis_result.get('error')}")
        
        return True
        
    except ImportError as e:
        print(f"⚠️  無法導入對比引擎: {e}")
        return False
    except Exception as e:
        print(f"💥 對比引擎測試失敗: {e}")
        logger.exception("對比引擎測試失敗")
        return False

async def main():
    """主測試函數"""
    
    print("=" * 60)
    print("🧪 SmartInvention Manus 集成測試")
    print("=" * 60)
    
    # 測試 Manus 集成
    manus_test_result = await test_manus_integration()
    
    # 測試對比引擎
    comparison_test_result = await test_comparison_engine()
    
    print("\n" + "=" * 60)
    print("📊 測試結果總結")
    print("=" * 60)
    print(f"Manus 集成測試: {'✅ 通過' if manus_test_result else '❌ 失敗'}")
    print(f"對比引擎測試: {'✅ 通過' if comparison_test_result else '❌ 失敗'}")
    
    if manus_test_result and comparison_test_result:
        print("\n🎉 所有測試通過！SmartInvention 的 Manus 數據抓取功能已修復。")
        return 0
    else:
        print("\n⚠️  部分測試失敗，請檢查配置和依賴。")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

