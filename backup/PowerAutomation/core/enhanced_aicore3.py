"""
增強的 AICore 3.0 - 整合 Smartinvention MCP 到主流程
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# 導入原有組件
from core.aicore3 import AICore3 as OriginalAICore3, UserRequest, ProcessingResult, ExpertResponse

logger = logging.getLogger(__name__)

class EnhancedAICore3(OriginalAICore3):
    """增強的 AICore 3.0 - 整合 Smartinvention MCP 到主流程"""
    
    def __init__(self):
        """初始化增強的 AICore 3.0"""
        super().__init__()
        
        # 新增配置
        self.smartinvention_integration_enabled = True
        self.manus_comparison_enabled = True
        self.incremental_repair_enabled = True
        
        logger.info("🚀 增強的 AICore 3.0 初始化完成 - Smartinvention MCP 整合已啟用")
    
    async def process_request(self, request: UserRequest) -> ProcessingResult:
        """處理用戶請求 - 增強版 5 階段流程 + Smartinvention MCP 整合"""
        start_time = time.time()
        stage_results = {}
        
        logger.info(f"🎯 開始處理請求 (增強版): {request.id}")
        
        try:
            # 階段0: Smartinvention MCP 預處理 (新增)
            if self.smartinvention_integration_enabled:
                stage_results['smartinvention_preprocessing'] = await self._stage0_smartinvention_preprocessing(request)
            
            # 階段1: 整合式搜索和分析
            stage_results['integrated_search'] = await self._stage1_integrated_search_and_analysis(request)
            
            # 階段2: 動態專家生成
            stage_results['dynamic_expert_generation'] = await self._stage2_dynamic_expert_generation(
                request, stage_results['integrated_search']
            )
            
            # 階段3: 專家回答生成 (並行)
            stage_results['expert_response_generation'] = await self._stage3_expert_response_generation(
                request, stage_results['dynamic_expert_generation']['selected_experts']
            )
            
            # 階段4: 智能工具執行
            stage_results['intelligent_tool_execution'] = await self._stage4_intelligent_tool_execution(
                request, stage_results['expert_response_generation']['expert_responses']
            )
            
            # 階段5: 最終結果生成 + Smartinvention MCP 後處理 (增強)
            final_result = await self._stage5_final_result_generation_enhanced(
                request, stage_results, start_time
            )
            
            # 更新統計
            await self._update_execution_stats(final_result, stage_results)
            
            logger.info(f"✅ 請求處理完成 (增強版): {request.id}, 耗時: {final_result.execution_time:.2f}s")
            return final_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ 請求處理失敗: {request.id}, 錯誤: {e}")
            
            return ProcessingResult(
                request_id=request.id,
                success=False,
                stage_results=stage_results,
                expert_analysis=[],
                tool_execution_results=[],
                final_answer=f"處理失敗: {str(e)}",
                confidence=0.0,
                execution_time=execution_time,
                metadata={"error": str(e), "failed_stage": len(stage_results)}
            )
    
    async def _stage0_smartinvention_preprocessing(self, request: UserRequest) -> Dict[str, Any]:
        """階段0: Smartinvention MCP 預處理 - 需求比對和增量修復準備"""
        stage_start = time.time()
        logger.info(f"🔍 階段0: Smartinvention MCP 預處理 - {request.id}")
        
        try:
            # 1. 初始化 Smartinvention Adapter MCP
            if self.smartinvention_adapter is None:
                await self._initialize_smartinvention_adapter()
            
            # 2. 執行需求比對
            manus_comparison_result = None
            if self.manus_comparison_enabled:
                manus_comparison_result = await self._perform_manus_comparison(request)
            
            # 3. 獲取相關任務和檔案
            related_tasks = await self._get_related_tasks(request)
            related_files = await self._get_related_files(request)
            
            # 4. 分析增量修復需求
            incremental_repair_analysis = None
            if self.incremental_repair_enabled:
                incremental_repair_analysis = await self._analyze_incremental_repair_needs(
                    request, manus_comparison_result, related_tasks
                )
            
            # 5. 準備上下文增強
            enhanced_context = await self._prepare_enhanced_context(
                request, manus_comparison_result, related_tasks, related_files
            )
            
            processing_time = time.time() - stage_start
            
            result = {
                "manus_comparison": manus_comparison_result,
                "related_tasks": related_tasks,
                "related_files": related_files,
                "incremental_repair_analysis": incremental_repair_analysis,
                "enhanced_context": enhanced_context,
                "processing_time": processing_time,
                "smartinvention_integration": {
                    "enabled": True,
                    "comparison_performed": manus_comparison_result is not None,
                    "tasks_found": len(related_tasks) if related_tasks else 0,
                    "files_found": len(related_files) if related_files else 0
                }
            }
            
            logger.info(f"✅ Smartinvention MCP 預處理完成: {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Smartinvention MCP 預處理失敗: {e}")
            return {
                "error": str(e),
                "processing_time": time.time() - stage_start,
                "smartinvention_integration": {"enabled": False, "error": str(e)}
            }
    
    async def _perform_manus_comparison(self, request: UserRequest) -> Dict[str, Any]:
        """執行 Manus 需求比對"""
        logger.info(f"🔍 執行 Manus 需求比對: {request.id}")
        
        try:
            # 使用 Manus Adapter MCP 進行需求分析
            if self.manus_adapter:
                comparison_result = await self.manus_adapter.analyze_requirement(
                    requirement_text=request.content,
                    target_entity=request.metadata.get("target_entity", "GENERAL"),
                    context=request.context
                )
                
                logger.info(f"✅ Manus 需求比對完成")
                return {
                    "success": True,
                    "comparison_result": comparison_result,
                    "matched_requirements": comparison_result.get("requirement_items", []),
                    "suggested_actions": comparison_result.get("manus_actions", []),
                    "cross_task_analysis": comparison_result.get("cross_task_analysis", {})
                }
            else:
                logger.warning("⚠️ Manus Adapter MCP 未初始化")
                return {"success": False, "error": "Manus Adapter MCP not initialized"}
                
        except Exception as e:
            logger.error(f"❌ Manus 需求比對失敗: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_related_tasks(self, request: UserRequest) -> List[Dict[str, Any]]:
        """獲取相關任務"""
        logger.info(f"🔍 獲取相關任務: {request.id}")
        
        try:
            if self.smartinvention_adapter:
                # 使用 Smartinvention Adapter 獲取任務數據
                tasks_data = await self.smartinvention_adapter.get_tasks_data()
                
                # 根據請求內容過濾相關任務
                related_tasks = []
                request_keywords = request.content.lower().split()
                
                for task in tasks_data.get("tasks", []):
                    task_content = task.get("content", "").lower()
                    task_title = task.get("title", "").lower()
                    
                    # 簡單的關鍵字匹配
                    relevance_score = 0
                    for keyword in request_keywords:
                        if keyword in task_content or keyword in task_title:
                            relevance_score += 1
                    
                    if relevance_score > 0:
                        task["relevance_score"] = relevance_score
                        related_tasks.append(task)
                
                # 按相關性排序
                related_tasks.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
                
                logger.info(f"✅ 找到 {len(related_tasks)} 個相關任務")
                return related_tasks[:10]  # 限制最多10個相關任務
            
            return []
            
        except Exception as e:
            logger.error(f"❌ 獲取相關任務失敗: {e}")
            return []
    
    async def _get_related_files(self, request: UserRequest) -> List[Dict[str, Any]]:
        """獲取相關檔案"""
        logger.info(f"🔍 獲取相關檔案: {request.id}")
        
        try:
            if self.smartinvention_adapter:
                # 使用 Smartinvention Adapter 獲取檔案數據
                files_data = await self.smartinvention_adapter.get_files_data()
                
                # 根據請求內容過濾相關檔案
                related_files = []
                request_keywords = request.content.lower().split()
                
                for file_info in files_data.get("files", []):
                    file_name = file_info.get("name", "").lower()
                    file_path = file_info.get("path", "").lower()
                    
                    # 關鍵字匹配
                    relevance_score = 0
                    for keyword in request_keywords:
                        if keyword in file_name or keyword in file_path:
                            relevance_score += 1
                    
                    if relevance_score > 0:
                        file_info["relevance_score"] = relevance_score
                        related_files.append(file_info)
                
                # 按相關性排序
                related_files.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
                
                logger.info(f"✅ 找到 {len(related_files)} 個相關檔案")
                return related_files[:20]  # 限制最多20個相關檔案
            
            return []
            
        except Exception as e:
            logger.error(f"❌ 獲取相關檔案失敗: {e}")
            return []
    
    async def _analyze_incremental_repair_needs(self, request: UserRequest, 
                                              manus_comparison: Dict[str, Any],
                                              related_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析增量修復需求"""
        logger.info(f"🔍 分析增量修復需求: {request.id}")
        
        try:
            repair_analysis = {
                "needs_repair": False,
                "repair_type": None,
                "repair_priority": "low",
                "repair_suggestions": [],
                "affected_components": [],
                "estimated_effort": "low"
            }
            
            # 基於 Manus 比對結果分析
            if manus_comparison and manus_comparison.get("success"):
                comparison_result = manus_comparison.get("comparison_result", {})
                
                # 檢查是否有匹配的需求
                matched_requirements = comparison_result.get("requirement_items", [])
                if matched_requirements:
                    repair_analysis["needs_repair"] = True
                    repair_analysis["repair_type"] = "requirement_enhancement"
                    repair_analysis["repair_priority"] = "medium"
                    repair_analysis["repair_suggestions"].extend([
                        f"增強需求: {req.get('description', '')}" for req in matched_requirements[:3]
                    ])
                
                # 檢查建議的行動
                suggested_actions = comparison_result.get("manus_actions", [])
                if suggested_actions:
                    repair_analysis["repair_suggestions"].extend([
                        f"建議行動: {action.get('description', '')}" for action in suggested_actions[:3]
                    ])
                
                # 檢查跨任務分析
                cross_task_analysis = comparison_result.get("cross_task_analysis", {})
                if cross_task_analysis.get("has_dependencies"):
                    repair_analysis["repair_type"] = "cross_task_integration"
                    repair_analysis["repair_priority"] = "high"
                    repair_analysis["affected_components"].extend(
                        cross_task_analysis.get("related_tasks", [])
                    )
            
            # 基於相關任務分析
            if related_tasks:
                high_relevance_tasks = [task for task in related_tasks if task.get("relevance_score", 0) > 2]
                if high_relevance_tasks:
                    repair_analysis["needs_repair"] = True
                    repair_analysis["repair_type"] = "task_integration"
                    repair_analysis["affected_components"].extend([
                        task.get("id", task.get("title", "")) for task in high_relevance_tasks[:5]
                    ])
            
            # 估算修復工作量
            if repair_analysis["needs_repair"]:
                effort_factors = [
                    len(repair_analysis["repair_suggestions"]),
                    len(repair_analysis["affected_components"]),
                    1 if repair_analysis["repair_priority"] == "high" else 0
                ]
                total_effort = sum(effort_factors)
                
                if total_effort > 5:
                    repair_analysis["estimated_effort"] = "high"
                elif total_effort > 2:
                    repair_analysis["estimated_effort"] = "medium"
                else:
                    repair_analysis["estimated_effort"] = "low"
            
            logger.info(f"✅ 增量修復需求分析完成: 需要修復={repair_analysis['needs_repair']}")
            return repair_analysis
            
        except Exception as e:
            logger.error(f"❌ 增量修復需求分析失敗: {e}")
            return {"error": str(e), "needs_repair": False}
    
    async def _prepare_enhanced_context(self, request: UserRequest,
                                      manus_comparison: Dict[str, Any],
                                      related_tasks: List[Dict[str, Any]],
                                      related_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """準備增強的上下文"""
        logger.info(f"🔍 準備增強上下文: {request.id}")
        
        enhanced_context = {
            "original_context": request.context,
            "smartinvention_enhancement": {
                "manus_insights": [],
                "task_context": [],
                "file_context": [],
                "integration_points": []
            }
        }
        
        # 添加 Manus 洞察
        if manus_comparison and manus_comparison.get("success"):
            comparison_result = manus_comparison.get("comparison_result", {})
            enhanced_context["smartinvention_enhancement"]["manus_insights"] = [
                f"需求匹配: {len(comparison_result.get('requirement_items', []))} 個相關需求",
                f"建議行動: {len(comparison_result.get('manus_actions', []))} 個行動項目",
                f"跨任務關聯: {comparison_result.get('cross_task_analysis', {}).get('has_dependencies', False)}"
            ]
        
        # 添加任務上下文
        if related_tasks:
            enhanced_context["smartinvention_enhancement"]["task_context"] = [
                f"任務 {task.get('id', '')}: {task.get('title', '')[:50]}..." 
                for task in related_tasks[:5]
            ]
        
        # 添加檔案上下文
        if related_files:
            enhanced_context["smartinvention_enhancement"]["file_context"] = [
                f"檔案: {file_info.get('name', '')}" 
                for file_info in related_files[:10]
            ]
        
        # 識別整合點
        integration_points = []
        if manus_comparison and related_tasks:
            integration_points.append("Manus 需求與現有任務的整合")
        if related_files:
            integration_points.append("相關檔案的參考和更新")
        
        enhanced_context["smartinvention_enhancement"]["integration_points"] = integration_points
        
        logger.info(f"✅ 增強上下文準備完成")
        return enhanced_context
    
    async def _stage5_final_result_generation_enhanced(self, request: UserRequest, 
                                                     stage_results: Dict[str, Any], 
                                                     start_time: float) -> ProcessingResult:
        """階段5: 最終結果生成 (增強版) + Smartinvention MCP 後處理"""
        stage_start = time.time()
        logger.info(f"🎯 階段5: 最終結果生成 (增強版) - {request.id}")
        
        try:
            # 1. 執行原有的最終結果生成
            original_result = await self._stage5_final_result_generation(request, stage_results, start_time)
            
            # 2. Smartinvention MCP 後處理
            smartinvention_postprocessing = None
            if self.smartinvention_integration_enabled and 'smartinvention_preprocessing' in stage_results:
                smartinvention_postprocessing = await self._smartinvention_postprocessing(
                    request, original_result, stage_results
                )
            
            # 3. 增強最終答案
            enhanced_final_answer = await self._enhance_final_answer(
                original_result.final_answer, 
                stage_results.get('smartinvention_preprocessing', {}),
                smartinvention_postprocessing
            )
            
            # 4. 更新元數據
            enhanced_metadata = original_result.metadata.copy()
            enhanced_metadata.update({
                "smartinvention_integration": True,
                "manus_comparison_performed": stage_results.get('smartinvention_preprocessing', {}).get('manus_comparison') is not None,
                "incremental_repair_analyzed": stage_results.get('smartinvention_preprocessing', {}).get('incremental_repair_analysis') is not None,
                "enhancement_processing_time": time.time() - stage_start
            })
            
            # 5. 創建增強的處理結果
            enhanced_result = ProcessingResult(
                request_id=original_result.request_id,
                success=original_result.success,
                stage_results=stage_results,  # 包含所有階段結果
                expert_analysis=original_result.expert_analysis,
                tool_execution_results=original_result.tool_execution_results,
                final_answer=enhanced_final_answer,
                confidence=original_result.confidence,
                execution_time=time.time() - start_time,
                metadata=enhanced_metadata
            )
            
            logger.info(f"✅ 增強版最終結果生成完成: {time.time() - stage_start:.2f}s")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"❌ 增強版最終結果生成失敗: {e}")
            # 回退到原有結果
            return await self._stage5_final_result_generation(request, stage_results, start_time)
    
    async def _smartinvention_postprocessing(self, request: UserRequest,
                                           original_result: ProcessingResult,
                                           stage_results: Dict[str, Any]) -> Dict[str, Any]:
        """Smartinvention MCP 後處理"""
        logger.info(f"🔍 Smartinvention MCP 後處理: {request.id}")
        
        try:
            postprocessing_result = {
                "incremental_repair_plan": None,
                "manus_action_items": [],
                "integration_recommendations": [],
                "follow_up_tasks": []
            }
            
            # 獲取預處理結果
            preprocessing = stage_results.get('smartinvention_preprocessing', {})
            
            # 生成增量修復計劃
            incremental_repair_analysis = preprocessing.get('incremental_repair_analysis', {})
            if incremental_repair_analysis.get('needs_repair'):
                postprocessing_result["incremental_repair_plan"] = {
                    "repair_type": incremental_repair_analysis.get('repair_type'),
                    "priority": incremental_repair_analysis.get('repair_priority'),
                    "estimated_effort": incremental_repair_analysis.get('estimated_effort'),
                    "repair_steps": incremental_repair_analysis.get('repair_suggestions', []),
                    "affected_components": incremental_repair_analysis.get('affected_components', [])
                }
            
            # 提取 Manus 行動項目
            manus_comparison = preprocessing.get('manus_comparison', {})
            if manus_comparison.get('success'):
                comparison_result = manus_comparison.get('comparison_result', {})
                postprocessing_result["manus_action_items"] = comparison_result.get('manus_actions', [])
            
            # 生成整合建議
            related_tasks = preprocessing.get('related_tasks', [])
            if related_tasks:
                postprocessing_result["integration_recommendations"] = [
                    f"考慮與任務 {task.get('id', '')} 的整合: {task.get('title', '')}"
                    for task in related_tasks[:3]
                ]
            
            # 生成後續任務
            if postprocessing_result["incremental_repair_plan"]:
                postprocessing_result["follow_up_tasks"] = [
                    "執行增量修復計劃",
                    "驗證修復結果",
                    "更新相關文檔"
                ]
            
            logger.info(f"✅ Smartinvention MCP 後處理完成")
            return postprocessing_result
            
        except Exception as e:
            logger.error(f"❌ Smartinvention MCP 後處理失敗: {e}")
            return {"error": str(e)}
    
    async def _enhance_final_answer(self, original_answer: str,
                                  smartinvention_preprocessing: Dict[str, Any],
                                  smartinvention_postprocessing: Dict[str, Any]) -> str:
        """增強最終答案"""
        
        enhanced_sections = [original_answer]
        
        # 添加 Smartinvention 洞察
        if smartinvention_preprocessing.get('manus_comparison', {}).get('success'):
            enhanced_sections.append("\n## 🎯 Manus 需求分析洞察")
            
            comparison_result = smartinvention_preprocessing['manus_comparison']['comparison_result']
            
            # 匹配的需求
            requirement_items = comparison_result.get('requirement_items', [])
            if requirement_items:
                enhanced_sections.append(f"\n### 📋 匹配的需求 ({len(requirement_items)} 項)")
                for i, req in enumerate(requirement_items[:3], 1):
                    enhanced_sections.append(f"{i}. {req.get('description', '')}")
            
            # 建議的行動
            manus_actions = comparison_result.get('manus_actions', [])
            if manus_actions:
                enhanced_sections.append(f"\n### 🚀 建議的 Manus 行動 ({len(manus_actions)} 項)")
                for i, action in enumerate(manus_actions[:3], 1):
                    enhanced_sections.append(f"{i}. {action.get('description', '')}")
        
        # 添加增量修復計劃
        if smartinvention_postprocessing and smartinvention_postprocessing.get('incremental_repair_plan'):
            repair_plan = smartinvention_postprocessing['incremental_repair_plan']
            enhanced_sections.append("\n## 🔧 增量修復計劃")
            enhanced_sections.append(f"**修復類型**: {repair_plan.get('repair_type', '')}")
            enhanced_sections.append(f"**優先級**: {repair_plan.get('priority', '')}")
            enhanced_sections.append(f"**預估工作量**: {repair_plan.get('estimated_effort', '')}")
            
            repair_steps = repair_plan.get('repair_steps', [])
            if repair_steps:
                enhanced_sections.append("\n**修復步驟**:")
                for i, step in enumerate(repair_steps[:3], 1):
                    enhanced_sections.append(f"{i}. {step}")
        
        # 添加整合建議
        if smartinvention_postprocessing and smartinvention_postprocessing.get('integration_recommendations'):
            recommendations = smartinvention_postprocessing['integration_recommendations']
            enhanced_sections.append("\n## 🔗 整合建議")
            for rec in recommendations:
                enhanced_sections.append(f"- {rec}")
        
        return "\n".join(enhanced_sections)
    
    async def _initialize_smartinvention_adapter(self):
        """初始化 Smartinvention Adapter"""
        if self.smartinvention_adapter is None:
            from PowerAutomation.components.mcp.core.smartinvention.main import SmartinventionAdapterMCP
            smartinvention_config = {
                'data_dir': '/tmp/smartinvention_data',
                'sync_interval': 30,
                'max_retries': 3,
                'local_endpoint': 'http://localhost:8000',
                'cloud_endpoint': 'http://18.212.97.173:8000'
            }
            self.smartinvention_adapter = SmartinventionAdapterMCP(smartinvention_config)
            await self.smartinvention_adapter.initialize()
            logger.info("✅ Smartinvention Adapter MCP 初始化完成")

# 工廠函數
def create_enhanced_aicore3() -> EnhancedAICore3:
    """創建增強的 AICore 3.0"""
    return EnhancedAICore3()

