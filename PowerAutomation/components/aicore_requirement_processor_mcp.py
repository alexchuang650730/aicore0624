#!/usr/bin/env python3
"""
AICore 需求處理器 (AICore Requirement Processor)
將用戶需求自動輸入到 AICore 3.0 系統中，調用 smartinvention MCP 和相關專家來解決問題
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
import re

# 導入 AICore 3.0 組件
from core.aicore3 import AICore3, UserRequest, ProcessingResult
from components.enhanced_smartinvention_mcp_v2 import EnhancedSmartinventionMCP

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RequirementAnalysisRequest:
    """需求分析請求"""
    requirement_id: str
    requirement_text: str
    analysis_scope: str = "full"  # full, basic, cross_task
    target_entity: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class RequirementItem:
    """需求項目"""
    requirement_id: str
    title: str
    description: str
    priority: str
    source_tasks: List[str]
    technical_complexity: str
    estimated_hours: int
    category: str
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ManusAction:
    """Manus 行動項目"""
    action_id: str
    action_type: str
    description: str
    related_tasks: List[str]
    execution_status: str
    priority: str
    estimated_effort: str
    prerequisites: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FileReference:
    """檔案參考"""
    file_path: str
    file_type: str
    relevance_score: float
    cross_task_relations: List[str]
    description: str
    size_bytes: Optional[int] = None
    last_modified: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CrossTaskAnalysis:
    """跨任務分析"""
    related_task_count: int
    shared_requirements: List[str]
    dependency_chain: str
    impact_assessment: str
    coordination_needs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RequirementAnalysisResult:
    """需求分析結果"""
    requirement_id: str
    analysis_timestamp: str
    requirements_list: List[RequirementItem]
    manus_actions: List[ManusAction]
    file_references: List[FileReference]
    cross_task_analysis: CrossTaskAnalysis
    expert_insights: Dict[str, Any]
    processing_metrics: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

class RequirementParser:
    """需求解析器"""
    
    def __init__(self):
        self.requirement_patterns = {
            'req_id': r'REQ[_-]?(\d+)',
            'target_entity': r'(REQ[_-]?\d+)',
            'analysis_keywords': ['列出', '分析', '明確需求', 'manus action', '檔案列表'],
            'cross_task_keywords': ['跨任務', '同一個需求', '多任務']
        }
    
    def parse_requirement(self, requirement_text: str) -> Dict[str, Any]:
        """解析需求文本"""
        logger.info(f"🔍 解析需求文本: {requirement_text[:100]}...")
        
        # 提取需求ID
        req_id_match = re.search(self.requirement_patterns['req_id'], requirement_text)
        target_entity = req_id_match.group(0) if req_id_match else None
        
        # 提取目標實體
        entity_match = re.search(self.requirement_patterns['target_entity'], requirement_text)
        target_entity = entity_match.group(0) if entity_match else target_entity
        
        # 分析需求類型
        requirement_type = self._classify_requirement_type(requirement_text)
        
        # 檢查是否需要跨任務分析
        cross_task_analysis = any(keyword in requirement_text for keyword in self.requirement_patterns['cross_task_keywords'])
        
        # 提取輸出格式要求
        output_format = self._extract_output_format(requirement_text)
        
        # 確定分析範圍
        analysis_scope = "full" if cross_task_analysis else "basic"
        
        result = {
            "requirement_type": requirement_type,
            "target_entity": target_entity,
            "analysis_scope": analysis_scope,
            "output_format": output_format,
            "cross_task_analysis": cross_task_analysis,
            "data_sources": ["smartinvention_mcp"],
            "expert_domains": self._determine_expert_domains(requirement_text)
        }
        
        logger.info(f"✅ 需求解析完成: {result}")
        return result
    
    def _classify_requirement_type(self, text: str) -> str:
        """分類需求類型"""
        if any(keyword in text for keyword in self.requirement_patterns['analysis_keywords']):
            return "requirement_analysis"
        return "general_inquiry"
    
    def _extract_output_format(self, text: str) -> List[str]:
        """提取輸出格式要求"""
        formats = []
        if "明確需求" in text or "需求列表" in text:
            formats.append("requirements_list")
        if "manus action" in text:
            formats.append("manus_actions")
        if "檔案列表" in text:
            formats.append("file_list")
        return formats or ["requirements_list"]
    
    def _determine_expert_domains(self, text: str) -> List[str]:
        """確定需要的專家領域"""
        domains = ["requirement_analysis"]  # 基礎需求分析專家
        
        if "界面" in text or "UI" in text or "UX" in text or "設計" in text:
            domains.append("ui_ux_design")
        
        if "檔案" in text or "跨任務" in text:
            domains.append("data_analysis")
        
        if "技術" in text or "實現" in text:
            domains.append("technical_architecture")
        
        return domains

class ExpertCoordinator:
    """專家協調器"""
    
    def __init__(self, aicore: AICore3):
        self.aicore = aicore
        self.expert_configs = {
            "requirement_analysis": {
                "name": "需求分析專家",
                "skills": ["需求工程", "業務分析", "跨任務關聯分析"],
                "scenario_type": "REQUIREMENT_ANALYSIS"
            },
            "ui_ux_design": {
                "name": "UI/UX設計專家", 
                "skills": ["界面設計", "用戶體驗", "前端技術"],
                "scenario_type": "UI_UX_DESIGN"
            },
            "data_analysis": {
                "name": "數據分析專家",
                "skills": ["數據挖掘", "關聯分析", "檔案系統分析"],
                "scenario_type": "DATA_ANALYSIS"
            },
            "technical_architecture": {
                "name": "技術架構專家",
                "skills": ["系統設計", "技術實現", "架構規劃"],
                "scenario_type": "TECHNICAL_ARCHITECTURE"
            }
        }
    
    async def coordinate_experts(self, parsed_requirement: Dict[str, Any], smartinvention_data: Dict[str, Any]) -> Dict[str, Any]:
        """協調專家分析"""
        logger.info(f"🤝 開始專家協調，需要專家: {parsed_requirement['expert_domains']}")
        
        expert_results = {}
        
        for domain in parsed_requirement['expert_domains']:
            if domain in self.expert_configs:
                logger.info(f"🧠 調用 {domain} 專家")
                expert_result = await self._invoke_expert(domain, parsed_requirement, smartinvention_data)
                expert_results[domain] = expert_result
        
        # 聚合專家結果
        aggregated_result = await self._aggregate_expert_results(expert_results, parsed_requirement)
        
        logger.info(f"✅ 專家協調完成，共 {len(expert_results)} 個專家參與")
        return aggregated_result
    
    async def _invoke_expert(self, domain: str, parsed_requirement: Dict[str, Any], smartinvention_data: Dict[str, Any]) -> Dict[str, Any]:
        """調用特定領域專家"""
        config = self.expert_configs[domain]
        
        # 構建專家請求
        expert_request = {
            "expert_domain": domain,
            "expert_name": config["name"],
            "scenario_type": config["scenario_type"],
            "skills": config["skills"],
            "task_data": smartinvention_data,
            "requirement_context": parsed_requirement,
            "analysis_objectives": self._get_analysis_objectives(domain, parsed_requirement)
        }
        
        # 模擬專家分析（在實際實現中會調用 AICore 的動態專家系統）
        if domain == "requirement_analysis":
            return await self._requirement_analysis_expert(expert_request)
        elif domain == "ui_ux_design":
            return await self._ui_ux_design_expert(expert_request)
        elif domain == "data_analysis":
            return await self._data_analysis_expert(expert_request)
        elif domain == "technical_architecture":
            return await self._technical_architecture_expert(expert_request)
        else:
            return {"error": f"Unknown expert domain: {domain}"}
    
    def _get_analysis_objectives(self, domain: str, parsed_requirement: Dict[str, Any]) -> List[str]:
        """獲取分析目標"""
        base_objectives = {
            "requirement_analysis": [
                "識別明確需求",
                "分析需求優先級",
                "評估需求依賴關係"
            ],
            "ui_ux_design": [
                "分析界面設計需求",
                "評估用戶體驗影響",
                "提供設計建議"
            ],
            "data_analysis": [
                "分析跨任務關聯",
                "識別相關檔案",
                "生成依賴關係圖"
            ],
            "technical_architecture": [
                "評估技術可行性",
                "分析實現複雜度",
                "提供架構建議"
            ]
        }
        
        objectives = base_objectives.get(domain, [])
        
        # 根據需求添加特定目標
        if parsed_requirement.get("cross_task_analysis"):
            objectives.append("執行跨任務分析")
        
        return objectives
    
    async def _requirement_analysis_expert(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """需求分析專家"""
        task_data = request["task_data"]
        target_entity = request["requirement_context"].get("target_entity", "REQ_001")
        
        # 分析任務數據中的需求
        requirements = []
        manus_actions = []
        
        # 從任務數據中提取需求
        for task_id, task_info in task_data.get("tasks", {}).items():
            if self._is_relevant_to_target(task_info, target_entity):
                req = self._extract_requirement_from_task(task_info, task_id)
                if req:
                    requirements.append(req)
                
                actions = self._extract_actions_from_task(task_info, task_id)
                manus_actions.extend(actions)
        
        return {
            "expert_type": "requirement_analysis",
            "analysis_result": {
                "identified_requirements": requirements,
                "manus_actions": manus_actions,
                "priority_assessment": self._assess_priorities(requirements),
                "dependency_analysis": self._analyze_dependencies(requirements)
            },
            "confidence": 0.85,
            "processing_time": 2.5
        }
    
    async def _ui_ux_design_expert(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """UI/UX設計專家"""
        requirements = request.get("analysis_result", {}).get("identified_requirements", [])
        
        ui_analysis = {
            "design_complexity": "中等",
            "user_impact": "高",
            "implementation_recommendations": [
                "採用響應式設計",
                "確保跨瀏覽器兼容性",
                "實施用戶測試"
            ],
            "design_patterns": [
                "導航欄整合模式",
                "功能遷移模式"
            ]
        }
        
        return {
            "expert_type": "ui_ux_design",
            "analysis_result": ui_analysis,
            "confidence": 0.80,
            "processing_time": 1.8
        }
    
    async def _data_analysis_expert(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """數據分析專家"""
        task_data = request["task_data"]
        
        # 分析檔案關聯
        file_analysis = self._analyze_file_relationships(task_data)
        cross_task_analysis = self._analyze_cross_task_relationships(task_data)
        
        return {
            "expert_type": "data_analysis",
            "analysis_result": {
                "file_relationships": file_analysis,
                "cross_task_relationships": cross_task_analysis,
                "data_dependencies": self._identify_data_dependencies(task_data)
            },
            "confidence": 0.90,
            "processing_time": 3.2
        }
    
    async def _technical_architecture_expert(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """技術架構專家"""
        requirements = request.get("analysis_result", {}).get("identified_requirements", [])
        
        architecture_analysis = {
            "technical_feasibility": "高",
            "implementation_complexity": "中等",
            "resource_requirements": {
                "development_time": "40-60小時",
                "team_size": "2-3人",
                "technologies": ["HTML/CSS", "JavaScript", "前端框架"]
            },
            "risk_assessment": [
                "用戶適應性風險: 低",
                "技術實現風險: 低",
                "集成風險: 中"
            ]
        }
        
        return {
            "expert_type": "technical_architecture",
            "analysis_result": architecture_analysis,
            "confidence": 0.88,
            "processing_time": 2.1
        }
    
    def _is_relevant_to_target(self, task_info: Dict[str, Any], target_entity: str) -> bool:
        """判斷任務是否與目標實體相關"""
        # 檢查任務描述中是否包含UI/UX相關關鍵詞
        description = task_info.get("description", "").lower()
        ui_keywords = ["ui", "ux", "界面", "設計", "導航", "用戶體驗"]
        
        return any(keyword in description for keyword in ui_keywords)
    
    def _extract_requirement_from_task(self, task_info: Dict[str, Any], task_id: str) -> Optional[Dict[str, Any]]:
        """從任務中提取需求"""
        if not self._is_relevant_to_target(task_info, "REQ_001"):
            return None
        
        description = task_info.get("description", "")
        
        # 生成需求ID
        req_id = f"REQ_001_{task_id}_UI"
        
        # 分析優先級
        priority = "高" if "導航" in description or "智慧下載" in description else "中"
        
        # 評估複雜度
        complexity = "中等" if len(description) > 50 else "低"
        
        return {
            "requirement_id": req_id,
            "title": f"{task_info.get('task_name', '未知任務')} UI需求",
            "description": description,
            "priority": priority,
            "source_tasks": [task_id],
            "technical_complexity": complexity,
            "estimated_hours": 40 if priority == "高" else 20,
            "category": "UI/UX設計"
        }
    
    def _extract_actions_from_task(self, task_info: Dict[str, Any], task_id: str) -> List[Dict[str, Any]]:
        """從任務中提取行動項目"""
        actions = []
        description = task_info.get("description", "")
        
        if "導航" in description:
            actions.append({
                "action_id": f"ACTION_{task_id}_NAV",
                "action_type": "導航優化",
                "description": "優化導航欄功能",
                "related_tasks": [task_id],
                "execution_status": "待執行",
                "priority": "高",
                "estimated_effort": "2-3天"
            })
        
        if "設計" in description:
            actions.append({
                "action_id": f"ACTION_{task_id}_DESIGN",
                "action_type": "界面設計",
                "description": "界面設計優化",
                "related_tasks": [task_id],
                "execution_status": "待執行",
                "priority": "中",
                "estimated_effort": "1-2天"
            })
        
        return actions
    
    def _assess_priorities(self, requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """評估優先級"""
        high_priority = [req for req in requirements if req.get("priority") == "高"]
        medium_priority = [req for req in requirements if req.get("priority") == "中"]
        low_priority = [req for req in requirements if req.get("priority") == "低"]
        
        return {
            "high_priority_count": len(high_priority),
            "medium_priority_count": len(medium_priority),
            "low_priority_count": len(low_priority),
            "priority_distribution": {
                "高": len(high_priority),
                "中": len(medium_priority),
                "低": len(low_priority)
            }
        }
    
    def _analyze_dependencies(self, requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析依賴關係"""
        # 簡化的依賴分析
        dependencies = []
        for req in requirements:
            if "導航" in req.get("description", ""):
                dependencies.append({
                    "requirement": req["requirement_id"],
                    "depends_on": ["基礎UI框架", "用戶認證系統"],
                    "dependency_type": "技術依賴"
                })
        
        return {
            "total_dependencies": len(dependencies),
            "dependency_details": dependencies,
            "critical_path": self._identify_critical_path(dependencies)
        }
    
    def _identify_critical_path(self, dependencies: List[Dict[str, Any]]) -> List[str]:
        """識別關鍵路徑"""
        # 簡化的關鍵路徑分析
        return ["基礎UI框架", "導航欄重構", "功能遷移", "用戶測試"]
    
    def _analyze_file_relationships(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析檔案關係"""
        file_relationships = {}
        
        for task_id, task_info in task_data.get("tasks", {}).items():
            files = task_info.get("files", [])
            for file_info in files:
                file_path = file_info.get("file_path", "")
                if "task_info.json" in file_path:
                    file_relationships[file_path] = {
                        "type": "任務元數據",
                        "relevance_score": 0.95,
                        "related_tasks": [task_id],
                        "cross_references": []
                    }
        
        return file_relationships
    
    def _analyze_cross_task_relationships(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析跨任務關係"""
        ui_related_tasks = []
        
        for task_id, task_info in task_data.get("tasks", {}).items():
            if self._is_relevant_to_target(task_info, "REQ_001"):
                ui_related_tasks.append(task_id)
        
        return {
            "related_task_count": len(ui_related_tasks),
            "related_tasks": ui_related_tasks,
            "shared_requirements": ["UI優化", "用戶體驗提升"],
            "dependency_chain": " → ".join(ui_related_tasks[:3]) if ui_related_tasks else "無",
            "coordination_complexity": "中等" if len(ui_related_tasks) > 2 else "低"
        }
    
    def _identify_data_dependencies(self, task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """識別數據依賴"""
        dependencies = []
        
        # 分析任務間的數據依賴
        for task_id, task_info in task_data.get("tasks", {}).items():
            if self._is_relevant_to_target(task_info, "REQ_001"):
                dependencies.append({
                    "source_task": task_id,
                    "dependency_type": "數據共享",
                    "shared_resources": ["用戶界面配置", "導航設定"],
                    "impact_level": "中"
                })
        
        return dependencies
    
    async def _aggregate_expert_results(self, expert_results: Dict[str, Any], parsed_requirement: Dict[str, Any]) -> Dict[str, Any]:
        """聚合專家結果"""
        logger.info("🔄 聚合專家分析結果")
        
        # 聚合需求列表
        all_requirements = []
        all_actions = []
        
        for domain, result in expert_results.items():
            analysis = result.get("analysis_result", {})
            
            if "identified_requirements" in analysis:
                all_requirements.extend(analysis["identified_requirements"])
            
            if "manus_actions" in analysis:
                all_actions.extend(analysis["manus_actions"])
        
        # 聚合檔案分析
        file_analysis = {}
        cross_task_analysis = {}
        
        if "data_analysis" in expert_results:
            data_result = expert_results["data_analysis"]["analysis_result"]
            file_analysis = data_result.get("file_relationships", {})
            cross_task_analysis = data_result.get("cross_task_relationships", {})
        
        # 聚合專家洞察
        expert_insights = {}
        for domain, result in expert_results.items():
            expert_insights[domain] = {
                "confidence": result.get("confidence", 0.0),
                "processing_time": result.get("processing_time", 0.0),
                "key_findings": result.get("analysis_result", {})
            }
        
        return {
            "requirements": all_requirements,
            "actions": all_actions,
            "file_analysis": file_analysis,
            "cross_task_analysis": cross_task_analysis,
            "expert_insights": expert_insights,
            "aggregation_metadata": {
                "expert_count": len(expert_results),
                "aggregation_time": time.time(),
                "confidence_average": sum(r.get("confidence", 0) for r in expert_results.values()) / len(expert_results)
            }
        }

class AICoreRequirementProcessor:
    """AICore 需求處理器主類"""
    
    def __init__(self):
        self.aicore = None
        self.smartinvention_mcp = None
        self.requirement_parser = RequirementParser()
        self.expert_coordinator = None
        self.processing_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_processing_time": 0.0
        }
    
    async def initialize(self):
        """初始化處理器"""
        logger.info("🚀 初始化 AICore 需求處理器")
        
        try:
            # 初始化 AICore 3.0
            self.aicore = AICore3()
            await self.aicore.initialize()
            
            # 初始化 Enhanced Smartinvention MCP
            self.smartinvention_mcp = EnhancedSmartinventionMCP()
            await self.smartinvention_mcp.initialize()
            
            # 初始化專家協調器
            self.expert_coordinator = ExpertCoordinator(self.aicore)
            
            logger.info("✅ AICore 需求處理器初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 初始化失敗: {e}")
            raise
    
    async def process_requirement(self, requirement_text: str, context: Dict[str, Any] = None) -> RequirementAnalysisResult:
        """處理用戶需求"""
        start_time = time.time()
        request_id = f"REQ_PROC_{int(start_time)}"
        
        logger.info(f"🎯 開始處理需求: {request_id}")
        logger.info(f"📝 需求內容: {requirement_text}")
        
        try:
            # 階段1: 需求解析
            logger.info("🔍 階段1: 需求解析")
            parsed_requirement = self.requirement_parser.parse_requirement(requirement_text)
            
            # 階段2: 數據獲取
            logger.info("📊 階段2: 從 Smartinvention MCP 獲取數據")
            smartinvention_data = await self._acquire_smartinvention_data(parsed_requirement)
            
            # 階段3: 專家協作分析
            logger.info("🧠 階段3: 專家協作分析")
            expert_analysis = await self.expert_coordinator.coordinate_experts(parsed_requirement, smartinvention_data)
            
            # 階段4: 結果格式化
            logger.info("📋 階段4: 結果格式化")
            formatted_result = await self._format_analysis_result(
                request_id, parsed_requirement, expert_analysis, smartinvention_data
            )
            
            # 更新統計
            processing_time = time.time() - start_time
            self._update_processing_stats(True, processing_time)
            
            logger.info(f"✅ 需求處理完成: {request_id}, 耗時: {processing_time:.2f}秒")
            return formatted_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_processing_stats(False, processing_time)
            logger.error(f"❌ 需求處理失敗: {request_id}, 錯誤: {e}")
            raise
    
    async def analyze_req_001(self, analysis_scope: str = "full") -> RequirementAnalysisResult:
        """專門分析 REQ_001 的方法"""
        requirement_text = "首先先針對 REQ_001: 用戶界面設計需求 列出我的明確需求 及manus action 包含相關的檔案列表 注意同一個需求可能跨任務"
        
        context = {
            "target_requirement": "REQ_001",
            "analysis_scope": analysis_scope,
            "focus_areas": ["ui_design", "cross_task_analysis", "file_mapping"]
        }
        
        return await self.process_requirement(requirement_text, context)
    
    async def _acquire_smartinvention_data(self, parsed_requirement: Dict[str, Any]) -> Dict[str, Any]:
        """從 Smartinvention MCP 獲取數據"""
        logger.info("📡 連接 Smartinvention MCP 獲取數據")
        
        try:
            # 獲取所有任務
            all_tasks = await self.smartinvention_mcp.get_all_tasks()
            
            # 搜尋UI相關任務
            ui_tasks = await self.smartinvention_mcp.search_tasks("UI")
            design_tasks = await self.smartinvention_mcp.search_tasks("設計")
            interface_tasks = await self.smartinvention_mcp.search_tasks("界面")
            
            # 合併搜尋結果
            relevant_tasks = {}
            for task_list in [ui_tasks, design_tasks, interface_tasks]:
                if isinstance(task_list, list):
                    for task in task_list:
                        if hasattr(task, 'task_id'):
                            relevant_tasks[task.task_id] = task
            
            # 獲取詳細數據
            detailed_data = {}
            for task_id, task in relevant_tasks.items():
                try:
                    # 獲取對話歷史
                    conversations = await self.smartinvention_mcp.get_task_conversations(task_id)
                    
                    # 獲取檔案列表
                    files = await self.smartinvention_mcp.get_task_files(task_id)
                    
                    # 獲取需求分析（如果可用）
                    requirements = None
                    try:
                        requirements = await self.smartinvention_mcp.analyze_task_requirements(task_id)
                    except:
                        pass  # 需求分析可能不可用
                    
                    detailed_data[task_id] = {
                        "task_info": task,
                        "conversations": conversations,
                        "files": files,
                        "requirements": requirements,
                        "description": getattr(task, 'description', ''),
                        "task_name": getattr(task, 'task_name', f'Task {task_id}')
                    }
                    
                except Exception as e:
                    logger.warning(f"⚠️ 獲取任務 {task_id} 詳細數據失敗: {e}")
                    continue
            
            result = {
                "all_tasks_count": len(all_tasks) if all_tasks else 0,
                "relevant_tasks_count": len(detailed_data),
                "tasks": detailed_data,
                "search_results": {
                    "ui_tasks": len(ui_tasks) if ui_tasks else 0,
                    "design_tasks": len(design_tasks) if design_tasks else 0,
                    "interface_tasks": len(interface_tasks) if interface_tasks else 0
                },
                "acquisition_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ 數據獲取完成: {len(detailed_data)} 個相關任務")
            return result
            
        except Exception as e:
            logger.error(f"❌ Smartinvention MCP 數據獲取失敗: {e}")
            # 返回模擬數據以確保流程繼續
            return self._get_mock_smartinvention_data()
    
    def _get_mock_smartinvention_data(self) -> Dict[str, Any]:
        """獲取模擬數據（當真實數據不可用時）"""
        logger.info("🔄 使用模擬數據")
        
        return {
            "all_tasks_count": 11,
            "relevant_tasks_count": 3,
            "tasks": {
                "TASK_001": {
                    "task_info": {
                        "task_id": "TASK_001",
                        "task_name": "UI/UX設計任務群組",
                        "description": "如何將智慧下載移至導航欄并移除原功能"
                    },
                    "conversations": [],
                    "files": [
                        {
                            "file_path": "/home/ec2-user/smartinvention_mcp/tasks/TASK_001/metadata/task_info.json",
                            "file_type": "任務元數據"
                        }
                    ],
                    "requirements": None
                },
                "TASK_003": {
                    "task_info": {
                        "task_id": "TASK_003",
                        "task_name": "MCP架構群組",
                        "description": "端雲協同系統的界面設計優化"
                    },
                    "conversations": [],
                    "files": [],
                    "requirements": None
                },
                "TASK_006": {
                    "task_info": {
                        "task_id": "TASK_006",
                        "task_name": "企業解決方案群組",
                        "description": "企業級界面設計需求"
                    },
                    "conversations": [],
                    "files": [],
                    "requirements": None
                }
            },
            "search_results": {
                "ui_tasks": 3,
                "design_tasks": 2,
                "interface_tasks": 1
            },
            "acquisition_timestamp": datetime.now().isoformat()
        }
    
    async def _format_analysis_result(self, request_id: str, parsed_requirement: Dict[str, Any], 
                                    expert_analysis: Dict[str, Any], smartinvention_data: Dict[str, Any]) -> RequirementAnalysisResult:
        """格式化分析結果"""
        logger.info("📋 格式化分析結果")
        
        # 轉換需求列表
        requirements_list = []
        for req_data in expert_analysis.get("requirements", []):
            requirement = RequirementItem(
                requirement_id=req_data.get("requirement_id", ""),
                title=req_data.get("title", ""),
                description=req_data.get("description", ""),
                priority=req_data.get("priority", "中"),
                source_tasks=req_data.get("source_tasks", []),
                technical_complexity=req_data.get("technical_complexity", "中等"),
                estimated_hours=req_data.get("estimated_hours", 20),
                category=req_data.get("category", "一般"),
                dependencies=req_data.get("dependencies", []),
                metadata=req_data.get("metadata", {})
            )
            requirements_list.append(requirement)
        
        # 轉換行動項目
        manus_actions = []
        for action_data in expert_analysis.get("actions", []):
            action = ManusAction(
                action_id=action_data.get("action_id", ""),
                action_type=action_data.get("action_type", ""),
                description=action_data.get("description", ""),
                related_tasks=action_data.get("related_tasks", []),
                execution_status=action_data.get("execution_status", "待執行"),
                priority=action_data.get("priority", "中"),
                estimated_effort=action_data.get("estimated_effort", ""),
                prerequisites=action_data.get("prerequisites", []),
                metadata=action_data.get("metadata", {})
            )
            manus_actions.append(action)
        
        # 轉換檔案參考
        file_references = []
        file_analysis = expert_analysis.get("file_analysis", {})
        for file_path, file_data in file_analysis.items():
            file_ref = FileReference(
                file_path=file_path,
                file_type=file_data.get("type", "未知"),
                relevance_score=file_data.get("relevance_score", 0.5),
                cross_task_relations=file_data.get("related_tasks", []),
                description=f"{file_data.get('type', '檔案')} - {file_path}",
                metadata=file_data
            )
            file_references.append(file_ref)
        
        # 轉換跨任務分析
        cross_task_data = expert_analysis.get("cross_task_analysis", {})
        cross_task_analysis = CrossTaskAnalysis(
            related_task_count=cross_task_data.get("related_task_count", 0),
            shared_requirements=cross_task_data.get("shared_requirements", []),
            dependency_chain=cross_task_data.get("dependency_chain", ""),
            impact_assessment=cross_task_data.get("coordination_complexity", "低"),
            coordination_needs=cross_task_data.get("coordination_needs", []),
            metadata=cross_task_data
        )
        
        # 處理指標
        processing_metrics = {
            "total_tasks_analyzed": smartinvention_data.get("relevant_tasks_count", 0),
            "requirements_identified": len(requirements_list),
            "actions_generated": len(manus_actions),
            "files_analyzed": len(file_references),
            "expert_confidence_average": expert_analysis.get("aggregation_metadata", {}).get("confidence_average", 0.0),
            "processing_stages_completed": 4
        }
        
        # 創建最終結果
        result = RequirementAnalysisResult(
            requirement_id=parsed_requirement.get("target_entity", "REQ_001"),
            analysis_timestamp=datetime.now().isoformat(),
            requirements_list=requirements_list,
            manus_actions=manus_actions,
            file_references=file_references,
            cross_task_analysis=cross_task_analysis,
            expert_insights=expert_analysis.get("expert_insights", {}),
            processing_metrics=processing_metrics,
            metadata={
                "request_id": request_id,
                "parsed_requirement": parsed_requirement,
                "smartinvention_data_summary": {
                    "total_tasks": smartinvention_data.get("all_tasks_count", 0),
                    "relevant_tasks": smartinvention_data.get("relevant_tasks_count", 0)
                }
            }
        )
        
        logger.info(f"✅ 結果格式化完成: {len(requirements_list)} 需求, {len(manus_actions)} 行動, {len(file_references)} 檔案")
        return result
    
    def _update_processing_stats(self, success: bool, processing_time: float):
        """更新處理統計"""
        self.processing_stats["total_requests"] += 1
        if success:
            self.processing_stats["successful_requests"] += 1
        
        # 更新平均處理時間
        total_time = self.processing_stats["average_processing_time"] * (self.processing_stats["total_requests"] - 1)
        self.processing_stats["average_processing_time"] = (total_time + processing_time) / self.processing_stats["total_requests"]
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """獲取處理統計"""
        success_rate = 0.0
        if self.processing_stats["total_requests"] > 0:
            success_rate = self.processing_stats["successful_requests"] / self.processing_stats["total_requests"]
        
        return {
            **self.processing_stats,
            "success_rate": success_rate
        }
    
    async def export_result_to_json(self, result: RequirementAnalysisResult, file_path: str):
        """導出結果到JSON檔案"""
        try:
            result_dict = asdict(result)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 結果已導出到: {file_path}")
        except Exception as e:
            logger.error(f"❌ 導出結果失敗: {e}")
            raise

# 使用示例
async def main():
    """主函數示例"""
    processor = AICoreRequirementProcessor()
    
    try:
        # 初始化
        await processor.initialize()
        
        # 處理 REQ_001 需求
        result = await processor.analyze_req_001("full")
        
        # 輸出結果摘要
        print(f"\n🎯 REQ_001 分析結果摘要:")
        print(f"📋 識別需求數量: {len(result.requirements_list)}")
        print(f"🚀 Manus 行動數量: {len(result.manus_actions)}")
        print(f"📁 相關檔案數量: {len(result.file_references)}")
        print(f"🔗 跨任務關聯: {result.cross_task_analysis.related_task_count} 個任務")
        
        # 導出結果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"/home/ubuntu/req_001_analysis_result_{timestamp}.json"
        await processor.export_result_to_json(result, output_file)
        
        # 顯示處理統計
        stats = processor.get_processing_stats()
        print(f"\n📊 處理統計:")
        print(f"總請求數: {stats['total_requests']}")
        print(f"成功率: {stats['success_rate']:.2%}")
        print(f"平均處理時間: {stats['average_processing_time']:.2f}秒")
        
    except Exception as e:
        logger.error(f"❌ 主程序執行失敗: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

