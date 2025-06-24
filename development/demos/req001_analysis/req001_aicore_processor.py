#!/usr/bin/env python3
"""
REQ_001 AICore 處理器
專門處理 REQ_001: 用戶界面設計需求的 AICore 處理器
基於 AICore 需求處理器框架，針對用戶的具體需求進行優化
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# 導入 AICore 需求處理器
from components.aicore_requirement_processor_mcp import AICoreRequirementProcessor

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class REQ001AICoreProcessor:
    """REQ_001 專用 AICore 處理器"""
    
    def __init__(self):
        self.base_processor = AICoreRequirementProcessor()
        self.req_001_context = {
            "target_requirement": "REQ_001",
            "requirement_title": "用戶界面設計需求",
            "focus_areas": [
                "智慧下載功能導航欄整合",
                "UI/UX設計優化",
                "跨任務需求分析",
                "檔案關聯分析"
            ],
            "expected_outputs": [
                "明確需求列表",
                "Manus action 清單",
                "相關檔案列表",
                "跨任務關聯分析"
            ]
        }
    
    async def initialize(self):
        """初始化處理器"""
        logger.info("🚀 初始化 REQ_001 AICore 處理器")
        await self.base_processor.initialize()
        logger.info("✅ REQ_001 AICore 處理器初始化完成")
    
    async def process_user_requirement(self) -> Dict[str, Any]:
        """處理用戶的具體需求"""
        logger.info("🎯 開始處理用戶需求: REQ_001 分析")
        
        # 用戶的原始需求
        user_requirement = "首先先針對 REQ_001: 用戶界面設計需求 列出我的明確需求 及manus action 包含相關的檔案列表 注意同一個需求可能跨任務"
        
        try:
            # 使用 AICore 需求處理器處理
            result = await self.base_processor.process_requirement(
                user_requirement, 
                self.req_001_context
            )
            
            # 格式化為用戶友好的輸出
            formatted_result = await self._format_user_friendly_output(result)
            
            # 保存結果
            await self._save_processing_result(formatted_result)
            
            logger.info("✅ REQ_001 需求處理完成")
            return formatted_result
            
        except Exception as e:
            logger.error(f"❌ REQ_001 需求處理失敗: {e}")
            raise
    
    async def _format_user_friendly_output(self, result) -> Dict[str, Any]:
        """格式化為用戶友好的輸出"""
        logger.info("📋 格式化用戶友好輸出")
        
        # 提取明確需求列表
        requirements_list = []
        for req in result.requirements_list:
            requirements_list.append({
                "需求ID": req.requirement_id,
                "需求標題": req.title,
                "需求描述": req.description,
                "優先級": req.priority,
                "來源任務": req.source_tasks,
                "技術複雜度": req.technical_complexity,
                "預估工時": f"{req.estimated_hours}小時",
                "需求類別": req.category
            })
        
        # 提取 Manus Actions
        manus_actions = []
        for action in result.manus_actions:
            manus_actions.append({
                "行動ID": action.action_id,
                "行動類型": action.action_type,
                "描述": action.description,
                "相關任務": action.related_tasks,
                "執行狀態": action.execution_status,
                "優先級": action.priority,
                "預估工作量": action.estimated_effort
            })
        
        # 提取檔案列表
        file_list = []
        for file_ref in result.file_references:
            file_list.append({
                "檔案路徑": file_ref.file_path,
                "檔案類型": file_ref.file_type,
                "相關性評分": f"{file_ref.relevance_score:.2f}",
                "跨任務關聯": file_ref.cross_task_relations,
                "描述": file_ref.description
            })
        
        # 跨任務分析
        cross_task_analysis = {
            "關聯任務數量": result.cross_task_analysis.related_task_count,
            "共享需求": result.cross_task_analysis.shared_requirements,
            "依賴關係鏈": result.cross_task_analysis.dependency_chain,
            "影響評估": result.cross_task_analysis.impact_assessment,
            "協調需求": result.cross_task_analysis.coordination_needs
        }
        
        # 處理統計
        processing_stats = {
            "分析任務總數": result.processing_metrics.get("total_tasks_analyzed", 0),
            "識別需求數量": result.processing_metrics.get("requirements_identified", 0),
            "生成行動數量": result.processing_metrics.get("actions_generated", 0),
            "分析檔案數量": result.processing_metrics.get("files_analyzed", 0),
            "專家信心平均值": f"{result.processing_metrics.get('expert_confidence_average', 0.0):.2f}"
        }
        
        return {
            "REQ_001_分析結果": {
                "分析時間": result.analysis_timestamp,
                "明確需求列表": requirements_list,
                "Manus_Actions": manus_actions,
                "相關檔案列表": file_list,
                "跨任務分析": cross_task_analysis,
                "處理統計": processing_stats,
                "專家洞察": result.expert_insights
            },
            "元數據": {
                "需求ID": result.requirement_id,
                "處理器版本": "REQ_001_AICore_Processor_v1.0",
                "AICore版本": "3.0",
                "處理狀態": "成功"
            }
        }
    
    async def _save_processing_result(self, result: Dict[str, Any]):
        """保存處理結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存 JSON 格式結果
        json_file = f"/home/ubuntu/req001_aicore_processing_result_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 生成 Markdown 報告
        md_file = f"/home/ubuntu/req001_aicore_processing_report_{timestamp}.md"
        await self._generate_markdown_report(result, md_file)
        
        logger.info(f"✅ 處理結果已保存:")
        logger.info(f"📄 JSON 格式: {json_file}")
        logger.info(f"📝 Markdown 報告: {md_file}")
    
    async def _generate_markdown_report(self, result: Dict[str, Any], file_path: str):
        """生成 Markdown 報告"""
        analysis_result = result["REQ_001_分析結果"]
        metadata = result["元數據"]
        
        markdown_content = f"""# REQ_001: 用戶界面設計需求 - AICore 分析報告

## 📊 分析概覽

**分析時間**: {analysis_result["分析時間"]}  
**需求ID**: {metadata["需求ID"]}  
**處理器版本**: {metadata["處理器版本"]}  
**處理狀態**: {metadata["處理狀態"]}

## 🎯 明確需求列表

"""
        
        # 添加需求列表
        for i, req in enumerate(analysis_result["明確需求列表"], 1):
            markdown_content += f"""### 需求 {i}: {req["需求標題"]}

- **需求ID**: {req["需求ID"]}
- **描述**: {req["需求描述"]}
- **優先級**: {req["優先級"]}
- **來源任務**: {', '.join(req["來源任務"])}
- **技術複雜度**: {req["技術複雜度"]}
- **預估工時**: {req["預估工時"]}
- **需求類別**: {req["需求類別"]}

"""
        
        # 添加 Manus Actions
        markdown_content += "## 🚀 Manus Actions\n\n"
        for i, action in enumerate(analysis_result["Manus_Actions"], 1):
            markdown_content += f"""### Action {i}: {action["行動類型"]}

- **行動ID**: {action["行動ID"]}
- **描述**: {action["描述"]}
- **相關任務**: {', '.join(action["相關任務"])}
- **執行狀態**: {action["執行狀態"]}
- **優先級**: {action["優先級"]}
- **預估工作量**: {action["預估工作量"]}

"""
        
        # 添加檔案列表
        markdown_content += "## 📁 相關檔案列表\n\n"
        for i, file_info in enumerate(analysis_result["相關檔案列表"], 1):
            markdown_content += f"""### 檔案 {i}

- **檔案路徑**: `{file_info["檔案路徑"]}`
- **檔案類型**: {file_info["檔案類型"]}
- **相關性評分**: {file_info["相關性評分"]}
- **跨任務關聯**: {', '.join(file_info["跨任務關聯"])}
- **描述**: {file_info["描述"]}

"""
        
        # 添加跨任務分析
        cross_task = analysis_result["跨任務分析"]
        markdown_content += f"""## 🔗 跨任務分析

- **關聯任務數量**: {cross_task["關聯任務數量"]}
- **共享需求**: {', '.join(cross_task["共享需求"])}
- **依賴關係鏈**: {cross_task["依賴關係鏈"]}
- **影響評估**: {cross_task["影響評估"]}
- **協調需求**: {', '.join(cross_task["協調需求"]) if cross_task["協調需求"] else '無'}

"""
        
        # 添加處理統計
        stats = analysis_result["處理統計"]
        markdown_content += f"""## 📈 處理統計

- **分析任務總數**: {stats["分析任務總數"]}
- **識別需求數量**: {stats["識別需求數量"]}
- **生成行動數量**: {stats["生成行動數量"]}
- **分析檔案數量**: {stats["分析檔案數量"]}
- **專家信心平均值**: {stats["專家信心平均值"]}

## 🧠 專家洞察

"""
        
        # 添加專家洞察
        for expert_domain, insights in analysis_result["專家洞察"].items():
            markdown_content += f"""### {expert_domain}

- **信心度**: {insights.get('confidence', 'N/A')}
- **處理時間**: {insights.get('processing_time', 'N/A')}秒

"""
        
        markdown_content += """## 📝 結論

本次 REQ_001 分析通過 AICore 3.0 動態專家系統，成功識別了用戶界面設計需求的明確需求、相關行動項目和檔案關聯。分析結果為後續的實施提供了清晰的指導方向。

## 🔄 下一步建議

1. **優先執行高優先級需求**：專注於智慧下載導航欄整合等核心需求
2. **協調跨任務依賴**：確保相關任務間的協調和同步
3. **實施監控機制**：建立進度追蹤和質量監控
4. **持續優化**：基於實施反饋持續改進需求和實施方案

---

*本報告由 AICore 3.0 動態專家系統自動生成*
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    
    async def get_processing_summary(self) -> Dict[str, Any]:
        """獲取處理摘要"""
        stats = self.base_processor.get_processing_stats()
        
        return {
            "處理器狀態": "就緒",
            "支持的需求": ["REQ_001"],
            "處理統計": stats,
            "功能特性": [
                "智能需求解析",
                "動態專家協調",
                "跨任務關聯分析",
                "自動化報告生成"
            ]
        }

async def main():
    """主函數 - 處理用戶的 REQ_001 需求"""
    logger.info("🚀 啟動 REQ_001 AICore 處理器")
    
    try:
        # 創建處理器
        processor = REQ001AICoreProcessor()
        
        # 初始化
        await processor.initialize()
        
        # 處理用戶需求
        result = await processor.process_user_requirement()
        
        # 輸出摘要
        print("\n" + "="*60)
        print("🎯 REQ_001: 用戶界面設計需求 - 處理完成")
        print("="*60)
        
        analysis_result = result["REQ_001_分析結果"]
        
        print(f"📋 識別需求數量: {len(analysis_result['明確需求列表'])}")
        print(f"🚀 Manus 行動數量: {len(analysis_result['Manus_Actions'])}")
        print(f"📁 相關檔案數量: {len(analysis_result['相關檔案列表'])}")
        print(f"🔗 跨任務關聯: {analysis_result['跨任務分析']['關聯任務數量']} 個任務")
        
        print("\n📊 明確需求列表:")
        for i, req in enumerate(analysis_result["明確需求列表"], 1):
            print(f"  {i}. {req['需求標題']} (優先級: {req['優先級']})")
        
        print("\n🚀 Manus Actions:")
        for i, action in enumerate(analysis_result["Manus_Actions"], 1):
            print(f"  {i}. {action['行動類型']}: {action['描述']}")
        
        print("\n📁 相關檔案:")
        for i, file_info in enumerate(analysis_result["相關檔案列表"], 1):
            print(f"  {i}. {file_info['檔案類型']}: {file_info['檔案路徑']}")
        
        print(f"\n🔗 跨任務分析:")
        cross_task = analysis_result["跨任務分析"]
        print(f"  - 關聯任務: {cross_task['關聯任務數量']} 個")
        print(f"  - 共享需求: {', '.join(cross_task['共享需求'])}")
        print(f"  - 依賴鏈: {cross_task['依賴關係鏈']}")
        
        print("\n✅ 處理完成！詳細報告已保存到檔案。")
        
        # 獲取處理摘要
        summary = await processor.get_processing_summary()
        print(f"\n📈 處理器統計:")
        print(f"  - 成功率: {summary['處理統計'].get('success_rate', 0):.1%}")
        print(f"  - 平均處理時間: {summary['處理統計'].get('average_processing_time', 0):.2f}秒")
        
    except Exception as e:
        logger.error(f"❌ REQ_001 處理失敗: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

