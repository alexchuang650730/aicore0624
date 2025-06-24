"""
Enhanced Test Flow MCP v5.1 - 深化Manus整合版本 (完整版)
優化manus處理邏輯，增強上下文處理能力，提升同步效率
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import time
import hashlib

# 新增manus專用導入
from collections import defaultdict, deque

class ProcessingMode(Enum):
    """處理模式枚舉"""
    DEVELOPER = "developer"
    ANALYST = "analyst"
    AUTOMATED = "automated"
    MANUS_SYNC = "manus_sync"  # 新增manus同步模式

class FixStrategy(Enum):
    """修復策略枚舉"""
    INTELLIGENT = "intelligent"
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    MANUS_GUIDED = "manus_guided"  # 新增manus引導策略

class SyncStatus(Enum):
    """同步狀態枚舉"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

@dataclass
class EnhancedManusContext:
    """增強版Manus上下文數據結構"""
    # 基礎信息
    session_id: str
    timestamp: datetime
    user_id: Optional[str] = None
    
    # 對話上下文
    conversation_history: List[Dict] = field(default_factory=list)
    current_topic: Optional[str] = None
    topic_evolution: List[str] = field(default_factory=list)
    
    # 需求上下文
    requirements: List[Dict] = field(default_factory=list)
    requirement_priority: Dict[str, float] = field(default_factory=dict)
    requirement_dependencies: Dict[str, List[str]] = field(default_factory=dict)
    
    # 技術上下文
    technical_stack: List[str] = field(default_factory=list)
    complexity_indicators: Dict[str, float] = field(default_factory=dict)
    performance_constraints: Dict[str, Any] = field(default_factory=dict)
    
    # 業務上下文
    business_objectives: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    timeline_constraints: Optional[Dict[str, Any]] = None
    
    # 質量上下文
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    testing_requirements: List[str] = field(default_factory=list)
    compliance_requirements: List[str] = field(default_factory=list)
    
    # 元數據
    context_version: str = "2.0"
    validation_status: str = "pending"
    confidence_score: float = 0.0
    last_updated: Optional[datetime] = None

@dataclass
class SyncResult:
    """同步結果數據結構"""
    sync_id: str
    status: SyncStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # 同步統計
    total_records: int = 0
    processed_records: int = 0
    successful_records: int = 0
    failed_records: int = 0
    
    # 數據質量
    data_quality_score: float = 0.0
    validation_errors: List[str] = field(default_factory=list)
    data_inconsistencies: List[str] = field(default_factory=list)
    
    # 性能指標
    processing_time: float = 0.0
    throughput: float = 0.0  # records per second
    memory_usage: float = 0.0
    
    # 結果數據
    synchronized_data: Dict[str, Any] = field(default_factory=dict)
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

class EnhancedManusSync:
    """增強版Manus同步引擎"""
    
    def __init__(self):
        self.sync_history = deque(maxlen=1000)
        self.active_syncs = {}
        
    async def sync_with_manus_enhanced(self, context: EnhancedManusContext,
                                     sync_options: Dict[str, Any] = None) -> SyncResult:
        """增強版manus同步"""
        sync_id = self._generate_sync_id()
        start_time = datetime.now()
        
        sync_result = SyncResult(
            sync_id=sync_id,
            status=SyncStatus.IN_PROGRESS,
            start_time=start_time
        )
        
        try:
            # 記錄活動同步
            self.active_syncs[sync_id] = sync_result
            
            # 1. 數據預處理
            processed_data = await self._preprocess_manus_data(context)
            sync_result.total_records = len(processed_data.get('records', []))
            
            # 2. 增量同步處理
            sync_data = await self._perform_incremental_sync(processed_data, sync_options)
            sync_result.synchronized_data = sync_data
            sync_result.processed_records = len(sync_data.get('synced_records', []))
            
            # 3. 質量評估
            quality_score = await self._assess_data_quality(sync_data)
            sync_result.data_quality_score = quality_score
            
            # 4. 生成建議
            recommendations = await self._generate_sync_recommendations(context, sync_data)
            sync_result.recommendations = recommendations
            
            # 完成同步
            sync_result.status = SyncStatus.COMPLETED
            sync_result.end_time = datetime.now()
            sync_result.processing_time = (sync_result.end_time - start_time).total_seconds()
            sync_result.successful_records = sync_result.processed_records
            
            # 計算吞吐量
            if sync_result.processing_time > 0:
                sync_result.throughput = sync_result.processed_records / sync_result.processing_time
            
        except Exception as e:
            sync_result.status = SyncStatus.FAILED
            sync_result.validation_errors.append(f"同步失敗: {str(e)}")
            sync_result.end_time = datetime.now()
            sync_result.processing_time = (sync_result.end_time - start_time).total_seconds()
        
        finally:
            # 清理活動同步記錄
            self.active_syncs.pop(sync_id, None)
            # 添加到歷史記錄
            self.sync_history.append(sync_result)
        
        return sync_result
    
    async def _preprocess_manus_data(self, context: EnhancedManusContext) -> Dict[str, Any]:
        """預處理manus數據"""
        processed_data = {
            "records": [],
            "metadata": {
                "preprocessing_time": datetime.now().isoformat(),
                "context_version": context.context_version
            }
        }
        
        # 處理對話歷史
        for conv in context.conversation_history:
            processed_record = {
                "type": "conversation",
                "data": conv,
                "processed_at": datetime.now().isoformat(),
                "quality_score": await self._calculate_record_quality(conv)
            }
            processed_data["records"].append(processed_record)
        
        # 處理需求數據
        for req in context.requirements:
            processed_record = {
                "type": "requirement",
                "data": req,
                "processed_at": datetime.now().isoformat(),
                "priority": context.requirement_priority.get(req.get('id', ''), 0.5)
            }
            processed_data["records"].append(processed_record)
        
        return processed_data
    
    async def _perform_incremental_sync(self, processed_data: Dict[str, Any],
                                      sync_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """執行增量同步"""
        sync_options = sync_options or {}
        
        sync_data = {
            "synced_records": [],
            "skipped_records": [],
            "updated_records": [],
            "sync_metadata": {
                "sync_type": "incremental",
                "sync_time": datetime.now().isoformat(),
                "options": sync_options
            }
        }
        
        # 模擬增量同步邏輯
        for record in processed_data.get("records", []):
            sync_data["synced_records"].append(record)
        
        return sync_data
    
    async def _assess_data_quality(self, sync_data: Dict[str, Any]) -> float:
        """評估數據質量"""
        synced_records = sync_data.get("synced_records", [])
        if not synced_records:
            return 0.0
        
        quality_scores = []
        for record in synced_records:
            quality_score = record.get("quality_score", 0.5)
            quality_scores.append(quality_score)
        
        return sum(quality_scores) / len(quality_scores)
    
    async def _calculate_record_quality(self, record: Dict[str, Any]) -> float:
        """計算記錄質量分數"""
        quality_score = 0.0
        
        # 基於數據完整性
        if record.get("id"):
            quality_score += 0.2
        if record.get("timestamp"):
            quality_score += 0.2
        if record.get("content") or record.get("messages"):
            quality_score += 0.3
        if record.get("metadata"):
            quality_score += 0.3
        
        return quality_score
    
    async def _generate_sync_recommendations(self, context: EnhancedManusContext, 
                                           sync_data: Dict[str, Any]) -> List[str]:
        """生成同步建議"""
        recommendations = []
        
        synced_count = len(sync_data.get("synced_records", []))
        
        if synced_count > 50:
            recommendations.append("數據量較大，建議考慮分批處理")
        
        if len(context.requirements) > 10:
            recommendations.append("需求數量較多，建議進行優先級排序")
        
        if len(context.technical_stack) > 5:
            recommendations.append("技術棧複雜，建議進行架構評估")
        
        return recommendations
    
    def _generate_sync_id(self) -> str:
        """生成同步ID"""
        return f"sync_{int(time.time())}_{hash(str(datetime.now())) % 10000}"

class EnhancedTestFlowMCPv51:
    """增強版Test Flow MCP v5.1 - 深化Manus整合"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.version = "5.1"
        self.manus_sync = EnhancedManusSync()
        self.logger = logging.getLogger(__name__)
        self.performance_metrics = {}
        
    async def process_with_enhanced_manus(self, requirement: str,
                                        manus_context: EnhancedManusContext,
                                        processing_mode: ProcessingMode = ProcessingMode.MANUS_SYNC,
                                        fix_strategy: FixStrategy = FixStrategy.MANUS_GUIDED) -> Dict[str, Any]:
        """使用增強manus整合處理需求"""
        start_time = time.time()
        
        try:
            self.logger.info(f"開始增強manus處理: {requirement[:50]}...")
            
            # 1. 同步manus數據
            sync_result = await self.manus_sync.sync_with_manus_enhanced(manus_context)
            
            # 2. 基於同步結果進行需求處理
            processing_result = await self._process_requirement_with_context(
                requirement, manus_context, sync_result
            )
            
            # 3. 生成增強報告
            enhanced_report = await self._generate_enhanced_report(
                requirement, manus_context, sync_result, processing_result
            )
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "requirement": requirement,
                "processing_mode": processing_mode.value,
                "fix_strategy": fix_strategy.value,
                "sync_result": sync_result.__dict__,
                "processing_result": processing_result,
                "enhanced_report": enhanced_report,
                "processing_time": processing_time,
                "performance_metrics": {
                    "sync_throughput": sync_result.throughput,
                    "data_quality": sync_result.data_quality_score,
                    "total_processing_time": processing_time
                }
            }
            
        except Exception as e:
            self.logger.error(f"增強manus處理失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "requirement": requirement,
                "processing_time": time.time() - start_time
            }
    
    async def _process_requirement_with_context(self, requirement: str,
                                              context: EnhancedManusContext,
                                              sync_result: SyncResult) -> Dict[str, Any]:
        """基於上下文處理需求"""
        processing_result = {
            "requirement_analysis": {},
            "context_integration": {},
            "solution_recommendations": [],
            "implementation_plan": {}
        }
        
        # 需求分析
        processing_result["requirement_analysis"] = {
            "complexity_score": await self._analyze_requirement_complexity(requirement),
            "technical_feasibility": await self._assess_technical_feasibility(requirement, context),
            "business_value": await self._assess_business_value(requirement, context),
            "risk_assessment": await self._assess_implementation_risk(requirement, context)
        }
        
        # 上下文整合
        processing_result["context_integration"] = {
            "related_requirements": await self._find_related_requirements(requirement, context),
            "technical_constraints": context.performance_constraints,
            "business_alignment": await self._assess_business_alignment(requirement, context),
            "stakeholder_impact": await self._assess_stakeholder_impact(requirement, context)
        }
        
        # 解決方案建議
        processing_result["solution_recommendations"] = await self._generate_solution_recommendations(
            requirement, context, sync_result
        )
        
        # 實施計劃
        processing_result["implementation_plan"] = await self._create_implementation_plan(
            requirement, context, processing_result
        )
        
        return processing_result
    
    async def _analyze_requirement_complexity(self, requirement: str) -> float:
        """分析需求複雜度"""
        complexity_keywords = ['optimize', 'enhance', 'integrate', 'complex', 'multiple', 'advanced']
        keyword_count = sum(1 for keyword in complexity_keywords if keyword in requirement.lower())
        length_factor = min(len(requirement) / 200, 1.0)
        return min((keyword_count * 0.2) + length_factor, 1.0)
    
    async def _assess_technical_feasibility(self, requirement: str, context: EnhancedManusContext) -> float:
        """評估技術可行性"""
        tech_stack_size = len(context.technical_stack)
        if tech_stack_size == 0:
            return 0.5  # 中等可行性
        
        # 基於技術棧的多樣性評估可行性
        return min(tech_stack_size * 0.1 + 0.5, 1.0)
    
    async def _assess_business_value(self, requirement: str, context: EnhancedManusContext) -> float:
        """評估業務價值"""
        value_keywords = ['performance', 'efficiency', 'user experience', 'cost', 'revenue']
        keyword_count = sum(1 for keyword in value_keywords if keyword in requirement.lower())
        business_objectives_count = len(context.business_objectives)
        
        return min((keyword_count * 0.2) + (business_objectives_count * 0.1), 1.0)
    
    async def _assess_implementation_risk(self, requirement: str, context: EnhancedManusContext) -> float:
        """評估實施風險"""
        risk_keywords = ['complex', 'integration', 'migration', 'legacy', 'critical']
        keyword_count = sum(1 for keyword in risk_keywords if keyword in requirement.lower())
        
        # 風險與複雜度成正比
        complexity = await self._analyze_requirement_complexity(requirement)
        return min((keyword_count * 0.15) + (complexity * 0.5), 1.0)
    
    async def _find_related_requirements(self, requirement: str, context: EnhancedManusContext) -> List[str]:
        """查找相關需求"""
        related = []
        req_words = set(requirement.lower().split())
        
        for req in context.requirements:
            req_desc = req.get('description', '').lower()
            req_words_set = set(req_desc.split())
            
            # 計算詞彙重疊度
            overlap = len(req_words.intersection(req_words_set))
            if overlap > 2:  # 如果有超過2個共同詞彙
                related.append(req.get('id', 'unknown'))
        
        return related
    
    async def _assess_business_alignment(self, requirement: str, context: EnhancedManusContext) -> float:
        """評估業務對齊度"""
        if not context.business_objectives:
            return 0.5
        
        alignment_score = 0.0
        req_words = set(requirement.lower().split())
        
        for objective in context.business_objectives:
            obj_words = set(objective.lower().split())
            overlap = len(req_words.intersection(obj_words))
            if overlap > 0:
                alignment_score += overlap * 0.1
        
        return min(alignment_score, 1.0)
    
    async def _assess_stakeholder_impact(self, requirement: str, context: EnhancedManusContext) -> Dict[str, float]:
        """評估利益相關者影響"""
        impact = {}
        
        for stakeholder in context.stakeholders:
            # 簡化的影響評估
            if 'user' in stakeholder.lower():
                impact[stakeholder] = 0.8  # 用戶相關需求通常影響較大
            elif 'developer' in stakeholder.lower():
                impact[stakeholder] = 0.6
            else:
                impact[stakeholder] = 0.4
        
        return impact
    
    async def _generate_solution_recommendations(self, requirement: str, 
                                               context: EnhancedManusContext,
                                               sync_result: SyncResult) -> List[str]:
        """生成解決方案建議"""
        recommendations = []
        
        # 基於需求內容生成建議
        if 'performance' in requirement.lower():
            recommendations.append("建議進行性能基準測試和瓶頸分析")
            recommendations.append("考慮實施緩存機制和異步處理")
        
        if 'optimize' in requirement.lower():
            recommendations.append("建議採用漸進式優化策略")
            recommendations.append("實施性能監控和指標收集")
        
        # 基於上下文生成建議
        if len(context.technical_stack) > 3:
            recommendations.append("技術棧較複雜，建議進行架構評估")
        
        if sync_result.data_quality_score < 0.7:
            recommendations.append("數據質量需要改善，建議加強數據驗證")
        
        return recommendations
    
    async def _create_implementation_plan(self, requirement: str,
                                        context: EnhancedManusContext,
                                        processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """創建實施計劃"""
        complexity = processing_result.get("requirement_analysis", {}).get("complexity_score", 0.5)
        
        # 基於複雜度估算工期
        if complexity < 0.3:
            duration = "1-2週"
            phases = ["需求分析", "實施", "測試"]
        elif complexity < 0.7:
            duration = "3-4週"
            phases = ["需求分析", "設計", "實施", "測試", "部署"]
        else:
            duration = "5-8週"
            phases = ["需求分析", "架構設計", "分階段實施", "集成測試", "性能測試", "部署"]
        
        return {
            "estimated_duration": duration,
            "phases": phases,
            "resource_requirements": f"{len(context.technical_stack)}個技術領域專家",
            "milestones": [f"階段{i+1}完成" for i in range(len(phases))],
            "risk_mitigation": ["定期進度檢查", "技術風險評估", "質量保證流程"]
        }
    
    async def _generate_enhanced_report(self, requirement: str,
                                      context: EnhancedManusContext,
                                      sync_result: SyncResult,
                                      processing_result: Dict[str, Any]) -> str:
        """生成增強報告"""
        report_sections = []
        
        # 報告標題
        report_sections.append("# Enhanced Test Flow MCP v5.1 - Manus整合報告")
        report_sections.append(f"**生成時間**: {datetime.now().isoformat()}")
        report_sections.append(f"**需求**: {requirement}")
        report_sections.append("")
        
        # 同步結果摘要
        report_sections.append("## Manus同步結果")
        report_sections.append(f"- **同步狀態**: {sync_result.status.value}")
        report_sections.append(f"- **處理記錄數**: {sync_result.processed_records}")
        report_sections.append(f"- **數據質量分數**: {sync_result.data_quality_score:.2f}")
        report_sections.append(f"- **處理時間**: {sync_result.processing_time:.2f}秒")
        report_sections.append(f"- **吞吐量**: {sync_result.throughput:.2f} records/sec")
        report_sections.append("")
        
        # 需求分析結果
        req_analysis = processing_result.get("requirement_analysis", {})
        report_sections.append("## 需求分析結果")
        report_sections.append(f"- **複雜度分數**: {req_analysis.get('complexity_score', 0):.2f}")
        report_sections.append(f"- **技術可行性**: {req_analysis.get('technical_feasibility', 0):.2f}")
        report_sections.append(f"- **業務價值**: {req_analysis.get('business_value', 0):.2f}")
        report_sections.append(f"- **風險評估**: {req_analysis.get('risk_assessment', 0):.2f}")
        report_sections.append("")
        
        # 建議列表
        recommendations = sync_result.recommendations
        if recommendations:
            report_sections.append("## 智能建議")
            for i, rec in enumerate(recommendations, 1):
                report_sections.append(f"{i}. {rec}")
            report_sections.append("")
        
        # 實施計劃
        impl_plan = processing_result.get("implementation_plan", {})
        if impl_plan:
            report_sections.append("## 實施計劃")
            report_sections.append(f"- **預估工期**: {impl_plan.get('estimated_duration', 'TBD')}")
            report_sections.append(f"- **資源需求**: {impl_plan.get('resource_requirements', 'TBD')}")
            report_sections.append(f"- **關鍵里程碑**: {len(impl_plan.get('milestones', []))}個")
            report_sections.append("")
        
        return "\n".join(report_sections)

# 測試函數
async def test_enhanced_test_flow_mcp_v51():
    """測試增強版Test Flow MCP v5.1"""
    print("🚀 測試增強版Test Flow MCP v5.1...")
    
    # 創建測試上下文
    test_context = EnhancedManusContext(
        session_id="test_session_001",
        timestamp=datetime.now(),
        user_id="test_user",
        conversation_history=[
            {
                "id": "conv_001",
                "messages": [
                    {"role": "user", "content": "我需要優化MCP組件的性能"},
                    {"role": "assistant", "content": "我可以幫您分析性能瓶頸"}
                ],
                "timestamp": datetime.now().isoformat()
            }
        ],
        requirements=[
            {
                "id": "req_001",
                "description": "優化MCP組件性能，提升處理速度",
                "priority": "high"
            }
        ],
        technical_stack=["Python", "AsyncIO", "MCP"],
        business_objectives=["提升系統性能", "改善用戶體驗"],
        stakeholders=["用戶", "開發團隊", "產品經理"]
    )
    
    # 創建MCP實例
    mcp = EnhancedTestFlowMCPv51()
    
    # 測試處理
    result = await mcp.process_with_enhanced_manus(
        requirement="優化MCP組件性能，支持更高並發處理",
        manus_context=test_context,
        processing_mode=ProcessingMode.MANUS_SYNC,
        fix_strategy=FixStrategy.MANUS_GUIDED
    )
    
    print("✅ 增強版Test Flow MCP v5.1測試完成:")
    print(f"   - 處理成功: {result['success']}")
    
    if result['success']:
        print(f"   - 同步記錄數: {result['sync_result']['processed_records']}")
        print(f"   - 數據質量: {result['sync_result']['data_quality_score']:.2f}")
        print(f"   - 處理時間: {result['processing_time']:.2f}秒")
        print(f"   - 建議數量: {len(result['sync_result']['recommendations'])}")
        print(f"   - 複雜度分數: {result['processing_result']['requirement_analysis']['complexity_score']:.2f}")
    else:
        print(f"   - 錯誤信息: {result.get('error', '未知錯誤')}")
        print(f"   - 處理時間: {result.get('processing_time', 0):.2f}秒")

if __name__ == "__main__":
    asyncio.run(test_enhanced_test_flow_mcp_v51())

