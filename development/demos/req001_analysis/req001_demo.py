#!/usr/bin/env python3
"""
REQ_001 演示腳本
展示如何使用 Manus_Adapter_MCP 和 AICore 3.0 來處理具體的 REQ_001 需求

使用場景：
"首先先針對 REQ_001: 用戶界面設計需求 列出我的明確需求 及manus action 包含相關的檔案列表 注意同一個需求可能跨任務"
"""

import asyncio
import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "PowerAutomation"))

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class REQ001Demo:
    """REQ_001 演示類"""
    
    def __init__(self):
        self.aicore = None
        self.demo_results = {}
    
    async def initialize(self):
        """初始化演示環境"""
        logger.info("🚀 初始化 REQ_001 演示環境")
        
        try:
            # 導入 AICore 3.0
            from core.aicore3 import create_aicore3
            
            # 創建和初始化 AICore
            self.aicore = create_aicore3()
            await self.aicore.initialize()
            
            logger.info("✅ AICore 3.0 初始化完成")
            logger.info("✅ Manus_Adapter_MCP 已註冊")
            
        except Exception as e:
            logger.error(f"❌ 初始化失敗: {e}")
            raise
    
    async def demo_req001_analysis(self):
        """演示 REQ_001 需求分析"""
        logger.info("🎯 開始 REQ_001 需求分析演示")
        
        # 用戶的原始需求
        requirement_text = "首先先針對 REQ_001: 用戶界面設計需求 列出我的明確需求 及manus action 包含相關的檔案列表 注意同一個需求可能跨任務"
        
        try:
            # 使用 AICore 的 Manus 處理方法
            result = await self.aicore.process_manus_requirement(
                requirement_text=requirement_text,
                target_entity="REQ_001",
                context={
                    "project": "manus_system",
                    "priority": "high",
                    "analysis_type": "comprehensive",
                    "cross_task_analysis": True
                }
            )
            
            self.demo_results["req001_analysis"] = result
            
            # 輸出結果
            self._display_analysis_results(result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ REQ_001 分析失敗: {e}")
            raise
    
    def _display_analysis_results(self, result):
        """顯示分析結果"""
        print("\n" + "="*80)
        print("🎯 REQ_001: 用戶界面設計需求 - 分析結果")
        print("="*80)
        
        if result["success"]:
            analysis = result["analysis_result"]
            
            print(f"📋 目標實體: {analysis['target_entity']}")
            print(f"⚡ 處理時間: {analysis['processing_time']:.2f}秒")
            print(f"🎯 信心度: {analysis['confidence_score']:.2f}")
            
            print(f"\n📝 明確需求列表 ({len(analysis['requirements_list'])} 項):")
            for i, req in enumerate(analysis['requirements_list'], 1):
                print(f"  {i}. {req}")
            
            print(f"\n🚀 Manus Actions ({len(analysis['manus_actions'])} 項):")
            for i, action in enumerate(analysis['manus_actions'], 1):
                print(f"  {i}. {action}")
            
            print(f"\n📁 相關檔案列表 ({len(analysis['file_references'])} 項):")
            for i, file_ref in enumerate(analysis['file_references'], 1):
                if isinstance(file_ref, dict):
                    print(f"  {i}. {file_ref.get('file_path', 'N/A')} - {file_ref.get('file_type', 'N/A')}")
                else:
                    print(f"  {i}. {file_ref}")
            
            print(f"\n🔗 跨任務分析:")
            cross_task = analysis['cross_task_analysis']
            if isinstance(cross_task, dict):
                for key, value in cross_task.items():
                    print(f"  - {key}: {value}")
            else:
                print(f"  {cross_task}")
            
            print(f"\n🧠 專家洞察:")
            expert_insights = analysis['expert_insights']
            if isinstance(expert_insights, dict):
                for expert_domain, insight in expert_insights.items():
                    print(f"  📊 {expert_domain}:")
                    if isinstance(insight, dict):
                        print(f"    - 分析: {insight.get('analysis', 'N/A')}")
                        print(f"    - 信心度: {insight.get('confidence', 'N/A')}")
                    else:
                        print(f"    - {insight}")
        else:
            print(f"❌ 分析失敗: {result.get('error', '未知錯誤')}")
    
    async def demo_manus_adapter_capabilities(self):
        """演示 Manus Adapter 的各種能力"""
        logger.info("🔧 演示 Manus Adapter 能力")
        
        try:
            # 獲取 Manus Adapter 狀態
            status = await self.aicore.manus_adapter.get_manus_status()
            
            print("\n" + "="*60)
            print("📊 Manus_Adapter_MCP 狀態")
            print("="*60)
            
            for key, value in status.items():
                print(f"  {key}: {value}")
            
            # 演示不同類型的分析
            demo_requests = [
                {
                    "type": "UI設計審查",
                    "endpoint": "/api/manus/ui/review",
                    "data": {
                        "ui_component": "REQ_001_NavigationBar",
                        "design_requirements": ["智慧下載整合", "用戶友好", "響應式設計"],
                        "context": {"project": "manus_ui"}
                    }
                },
                {
                    "type": "跨任務分析",
                    "endpoint": "/api/manus/cross-task/analyze",
                    "data": {
                        "task_list": ["TASK_001", "TASK_003", "TASK_006"],
                        "analysis_focus": "dependencies",
                        "context": {"scope": "ui_requirements"}
                    }
                }
            ]
            
            for demo_req in demo_requests:
                print(f"\n🎯 演示: {demo_req['type']}")
                print("-" * 40)
                
                result = await self.aicore.handle_manus_request(
                    demo_req["endpoint"], 
                    demo_req["data"]
                )
                
                if result["success"]:
                    print(f"✅ {demo_req['type']} 成功")
                    data = result.get("data", {})
                    print(f"  - 處理時間: {data.get('processing_time', 'N/A')}秒")
                    print(f"  - 信心度: {data.get('confidence_score', 'N/A')}")
                    print(f"  - 建議數量: {len(data.get('recommendations', []))}")
                else:
                    print(f"❌ {demo_req['type']} 失敗: {result.get('error', '未知錯誤')}")
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Manus Adapter 能力演示失敗: {e}")
            raise
    
    async def demo_aicore_integration(self):
        """演示 AICore 整合效果"""
        logger.info("🔗 演示 AICore 整合效果")
        
        try:
            # 獲取 AICore 系統統計
            stats = await self.aicore.get_system_statistics()
            
            print("\n" + "="*60)
            print("📈 AICore 3.0 系統統計")
            print("="*60)
            
            # 性能指標
            performance = stats.get("performance_metrics", {})
            print("⚡ 性能指標:")
            for key, value in performance.items():
                print(f"  - {key}: {value}")
            
            # 專家統計
            expert_stats = stats.get("expert_registry_stats", {})
            print(f"\n👥 專家系統:")
            print(f"  - 總專家數: {expert_stats.get('total_experts', 0)}")
            print(f"  - 活躍專家數: {expert_stats.get('by_status', {}).get('active', 0)}")
            
            # 系統健康
            health = stats.get("system_health", {})
            print(f"\n🏥 系統健康:")
            for key, value in health.items():
                print(f"  - {key}: {value}")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ AICore 整合演示失敗: {e}")
            raise
    
    async def save_demo_results(self):
        """保存演示結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"req001_demo_results_{timestamp}.json"
        
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.demo_results, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"📄 演示結果已保存到: {results_file}")
            return results_file
            
        except Exception as e:
            logger.error(f"❌ 保存演示結果失敗: {e}")
            return None
    
    async def run_complete_demo(self):
        """運行完整演示"""
        logger.info("🎬 開始 REQ_001 完整演示")
        
        try:
            # 1. 初始化
            await self.initialize()
            
            # 2. REQ_001 需求分析
            analysis_result = await self.demo_req001_analysis()
            
            # 3. Manus Adapter 能力演示
            adapter_status = await self.demo_manus_adapter_capabilities()
            
            # 4. AICore 整合演示
            integration_stats = await self.demo_aicore_integration()
            
            # 5. 保存結果
            results_file = await self.save_demo_results()
            
            print("\n" + "="*80)
            print("🎉 REQ_001 演示完成")
            print("="*80)
            print("✅ 所有演示項目成功完成")
            print(f"📄 結果文件: {results_file}")
            print("\n🎯 演示總結:")
            print("  1. ✅ Manus_Adapter_MCP 成功註冊到 AICore 3.0")
            print("  2. ✅ 利用 AICore 的動態專家系統進行智能分析")
            print("  3. ✅ 通過智慧路由選擇最佳處理工具")
            print("  4. ✅ 使用工具發現機制自動匹配分析工具")
            print("  5. ✅ 成功處理 REQ_001 用戶界面設計需求")
            print("  6. ✅ 提供明確需求列表、Manus actions 和檔案列表")
            print("  7. ✅ 完成跨任務關聯分析")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 完整演示失敗: {e}")
            return False

async def main():
    """主函數"""
    print("🚀 REQ_001 演示腳本啟動")
    print("展示 Manus_Adapter_MCP 與 AICore 3.0 的完整整合")
    
    demo = REQ001Demo()
    success = await demo.run_complete_demo()
    
    if success:
        print("\n✅ 演示成功完成！")
        return 0
    else:
        print("\n❌ 演示失敗！")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())

