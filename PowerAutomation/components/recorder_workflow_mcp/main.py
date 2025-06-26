"""
Recorder_Workflow MCP 組件
工作流錄製和管理的MCP組件

基於原有Workflow Recorder核心功能，提供：
- 工作流錄製會話管理
- 錄製數據處理和分析
- 工作流步驟追蹤
- 錄製結果導出
- 智能工作流學習

作者: PowerAutomation Team
版本: 2.0.0
日期: 2025-06-23
"""

import json
import logging
import asyncio
import time
import os
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import tempfile
import subprocess

logger = logging.getLogger(__name__)

class RecordingStatus(Enum):
    """錄製狀態枚舉"""
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowType(Enum):
    """工作流類型枚舉"""
    FORM_FILLING = "form_filling"
    DATA_EXTRACTION = "data_extraction"
    NAVIGATION = "navigation"
    AUTOMATION = "automation"
    TESTING = "testing"
    GENERAL = "general"
    DEPLOYMENT = "deployment"
    CODING = "coding"

@dataclass
class RecordingSession:
    """錄製會話數據結構"""
    session_id: str
    session_name: str
    start_time: str
    end_time: Optional[str] = None
    status: RecordingStatus = RecordingStatus.IDLE
    workflow_type: WorkflowType = WorkflowType.AUTOMATION
    description: str = ""
    recorded_steps: int = 0
    workflow_file: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class WorkflowStep:
    """工作流步驟數據結構"""
    step_id: int
    action_type: str
    selector: str
    value: Optional[str] = None
    wait_time: float = 0.0
    screenshot: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class WorkflowDataProcessor:
    """工作流數據處理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.WorkflowDataProcessor")
    
    async def process_recording_data(self, session: RecordingSession, raw_data: Dict) -> Dict[str, Any]:
        """處理錄製數據"""
        try:
            processed_data = {
                "session_info": asdict(session),
                "workflow_steps": [],
                "statistics": {
                    "total_steps": 0,
                    "successful_steps": 0,
                    "failed_steps": 0,
                    "total_duration": 0.0,
                    "average_step_time": 0.0,
                    "complexity_score": 0.0,
                    "action_types": {}
                },
                "patterns": {
                    "common_selectors": [],
                    "frequent_actions": [],
                    "error_patterns": []
                },
                "metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "processor_version": "2.0.0"
                }
            }
            
            # 處理步驟數據
            steps = raw_data.get("steps", [])
            action_counts = {}
            
            for i, step_data in enumerate(steps):
                step = WorkflowStep(
                    step_id=i + 1,
                    action_type=step_data.get("action", "unknown"),
                    selector=step_data.get("selector", ""),
                    value=step_data.get("value"),
                    wait_time=step_data.get("wait_time", 0.0),
                    success=step_data.get("success", True),
                    execution_time=step_data.get("execution_time", 0.0),
                    metadata={
                        "url": step_data.get("url"),
                        "element_text": step_data.get("element_text"),
                        "coordinates": step_data.get("coordinates"),
                        "timestamp": step_data.get("timestamp")
                    }
                )
                processed_data["workflow_steps"].append(asdict(step))
                
                # 統計動作類型
                action_type = step.action_type
                action_counts[action_type] = action_counts.get(action_type, 0) + 1
            
            # 計算統計信息
            stats = processed_data["statistics"]
            stats["total_steps"] = len(steps)
            stats["successful_steps"] = sum(1 for s in steps if s.get("success", True))
            stats["failed_steps"] = stats["total_steps"] - stats["successful_steps"]
            stats["total_duration"] = sum(s.get("execution_time", 0.0) for s in steps)
            stats["average_step_time"] = stats["total_duration"] / max(stats["total_steps"], 1)
            stats["action_types"] = action_counts
            stats["complexity_score"] = self._calculate_complexity_score(processed_data["workflow_steps"])
            
            # 分析模式
            processed_data["patterns"] = self._analyze_patterns(processed_data["workflow_steps"])
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"處理錄製數據失敗: {e}")
            raise
    
    def _calculate_complexity_score(self, steps: List[Dict]) -> float:
        """計算工作流複雜度分數"""
        try:
            if not steps:
                return 0.0
            
            # 基於多個因素計算複雜度
            step_count_factor = min(len(steps) / 20.0, 1.0)  # 步驟數量
            unique_actions = len(set(step.get("action_type", "") for step in steps))
            action_variety_factor = min(unique_actions / 10.0, 1.0)  # 動作多樣性
            
            # 錯誤率因素
            failed_steps = sum(1 for step in steps if not step.get("success", True))
            error_factor = failed_steps / len(steps) if steps else 0
            
            complexity_score = (
                step_count_factor * 0.4 +
                action_variety_factor * 0.4 +
                error_factor * 0.2
            )
            
            return min(complexity_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"計算複雜度分數失敗: {e}")
            return 0.5
    
    def _analyze_patterns(self, steps: List[Dict]) -> Dict[str, List]:
        """分析工作流模式"""
        try:
            patterns = {
                "common_selectors": [],
                "frequent_actions": [],
                "error_patterns": []
            }
            
            if not steps:
                return patterns
            
            # 分析常用選擇器
            selectors = [step.get("selector", "") for step in steps if step.get("selector")]
            selector_counts = {}
            for selector in selectors:
                selector_counts[selector] = selector_counts.get(selector, 0) + 1
            
            patterns["common_selectors"] = sorted(
                selector_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            # 分析頻繁動作
            actions = [step.get("action_type", "") for step in steps]
            action_counts = {}
            for action in actions:
                action_counts[action] = action_counts.get(action, 0) + 1
            
            patterns["frequent_actions"] = sorted(
                action_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            # 分析錯誤模式
            error_steps = [step for step in steps if not step.get("success", True)]
            patterns["error_patterns"] = [
                {
                    "step_id": step.get("step_id"),
                    "action_type": step.get("action_type"),
                    "error_message": step.get("error_message", "Unknown error")
                }
                for step in error_steps[:5]
            ]
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"分析模式失敗: {e}")
            return {"common_selectors": [], "frequent_actions": [], "error_patterns": []}

class RecorderWorkflowMCP:
    """Recorder_Workflow MCP 組件"""
    
    def __init__(self, recordings_dir: str = "./recordings"):
        self.recordings_dir = Path(recordings_dir)
        self.recordings_dir.mkdir(exist_ok=True)
        
        self.current_session: Optional[RecordingSession] = None
        self.sessions_history: List[RecordingSession] = []
        self.data_processor = WorkflowDataProcessor()
        
        # 組件信息
        self.component_info = {
            "name": "Recorder_Workflow MCP",
            "version": "2.0.0",
            "description": "工作流錄製和管理的MCP組件，支持智能學習和模式分析",
            "tool_type": "MCP Component",
            "capabilities": {
                "workflow_recording": {
                    "description": "錄製用戶工作流操作",
                    "input_types": ["json"],
                    "output_types": ["json"],
                    "parameters": {
                        "session_name": "string",
                        "workflow_type": "string",
                        "description": "string"
                    }
                },
                "session_management": {
                    "description": "管理錄製會話生命週期",
                    "input_types": ["json"],
                    "output_types": ["json"],
                    "parameters": {
                        "session_id": "string",
                        "action": "string"
                    }
                },
                "data_processing": {
                    "description": "處理和分析錄製數據",
                    "input_types": ["json"],
                    "output_types": ["json"],
                    "parameters": {
                        "session_id": "string",
                        "analysis_type": "string"
                    }
                },
                "pattern_analysis": {
                    "description": "分析工作流模式和優化建議",
                    "input_types": ["json"],
                    "output_types": ["json"],
                    "parameters": {
                        "workflow_data": "object",
                        "analysis_depth": "string"
                    }
                },
                "workflow_export": {
                    "description": "導出工作流數據為不同格式",
                    "input_types": ["json"],
                    "output_types": ["json", "csv", "yaml"],
                    "parameters": {
                        "session_id": "string",
                        "format": "string"
                    }
                }
            },
            "supported_types": [wt.value for wt in WorkflowType],
            "tool_discovery": {
                "registry_compatible": True,
                "mcp_version": "2.0",
                "discovery_metadata": {
                    "tags": ["mcp", "component", "workflow", "recording", "automation"],
                    "category": "workflow_tools",
                    "priority": "high"
                }
            }
        }
        
        self.logger = logging.getLogger(f"{__name__}.RecorderWorkflowMCP")
        self.logger.info("🎬 Recorder_Workflow MCP 組件初始化完成")
    
    @staticmethod
    def get_capabilities() -> Dict[str, Any]:
        """返回組件能力描述，供Tool Registry發現"""
        return {
            "name": "recorder_workflow_mcp",
            "description": "工作流錄製和管理的MCP組件，支持智能學習和模式分析",
            "tool_type": "MCP Component",
            "capabilities": {
                "workflow_recording": {
                    "description": "錄製用戶工作流操作",
                    "input_types": ["json"],
                    "output_types": ["json"],
                    "parameters": {
                        "session_name": "string",
                        "workflow_type": "string",
                        "description": "string"
                    }
                },
                "session_management": {
                    "description": "管理錄製會話生命週期",
                    "input_types": ["json"],
                    "output_types": ["json"],
                    "parameters": {
                        "session_id": "string",
                        "action": "string"
                    }
                },
                "data_processing": {
                    "description": "處理和分析錄製數據",
                    "input_types": ["json"],
                    "output_types": ["json"],
                    "parameters": {
                        "session_id": "string",
                        "analysis_type": "string"
                    }
                },
                "pattern_analysis": {
                    "description": "分析工作流模式和優化建議",
                    "input_types": ["json"],
                    "output_types": ["json"],
                    "parameters": {
                        "workflow_data": "object",
                        "analysis_depth": "string"
                    }
                },
                "workflow_export": {
                    "description": "導出工作流數據為不同格式",
                    "input_types": ["json"],
                    "output_types": ["json", "csv", "yaml"],
                    "parameters": {
                        "session_id": "string",
                        "format": "string"
                    }
                }
            },
            "tool_discovery": {
                "registry_compatible": True,
                "mcp_version": "2.0",
                "discovery_metadata": {
                    "tags": ["mcp", "component", "workflow", "recording", "automation"],
                    "category": "workflow_tools",
                    "priority": "high"
                }
            }
        }
    
    async def start_recording(self, session_name: str, 
                            workflow_type: str = "automation",
                            description: str = "") -> Dict[str, Any]:
        """開始錄製工作流"""
        try:
            if self.current_session and self.current_session.status == RecordingStatus.RECORDING:
                return {
                    "success": False,
                    "error": "已有錄製會話正在進行中",
                    "current_session": asdict(self.current_session)
                }
            
            # 創建新的錄製會話
            session_id = f"workflow_{uuid.uuid4().hex[:8]}"
            session = RecordingSession(
                session_id=session_id,
                session_name=session_name,
                start_time=datetime.now().isoformat(),
                status=RecordingStatus.RECORDING,
                workflow_type=WorkflowType(workflow_type),
                description=description
            )
            
            # 創建會話目錄
            session_dir = self.recordings_dir / session_id
            session_dir.mkdir(exist_ok=True)
            
            self.current_session = session
            self.logger.info(f"🎬 開始錄製會話: {session_name} ({session_id})")
            
            return {
                "success": True,
                "session": asdict(session),
                "message": f"錄製會話 '{session_name}' 已開始"
            }
            
        except Exception as e:
            self.logger.error(f"❌ 開始錄製失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_recording(self) -> Dict[str, Any]:
        """停止錄製並處理結果"""
        try:
            if not self.current_session or self.current_session.status != RecordingStatus.RECORDING:
                return {
                    "success": False,
                    "error": "沒有正在進行的錄製會話"
                }
            
            # 更新會話狀態
            self.current_session.status = RecordingStatus.PROCESSING
            self.current_session.end_time = datetime.now().isoformat()
            
            # 模擬處理錄製結果（實際實現中會處理真實的錄製數據）
            mock_recording_data = {
                "steps": [
                    {
                        "action": "click",
                        "selector": "#submit-button",
                        "success": True,
                        "execution_time": 0.5,
                        "url": "https://example.com/form",
                        "element_text": "Submit"
                    },
                    {
                        "action": "input",
                        "selector": "#username",
                        "value": "test_user",
                        "success": True,
                        "execution_time": 0.3,
                        "url": "https://example.com/form"
                    },
                    {
                        "action": "navigate",
                        "selector": "",
                        "value": "https://example.com/dashboard",
                        "success": True,
                        "execution_time": 1.2
                    }
                ]
            }
            
            # 處理錄製數據
            processed_data = await self.data_processor.process_recording_data(
                self.current_session, mock_recording_data
            )
            
            # 保存處理結果
            result_file = self.recordings_dir / self.current_session.session_id / "workflow_data.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
            
            # 更新會話信息
            self.current_session.status = RecordingStatus.COMPLETED
            self.current_session.recorded_steps = len(mock_recording_data.get('steps', []))
            self.current_session.workflow_file = str(result_file)
            
            # 保存到歷史
            completed_session = self.current_session
            self.sessions_history.append(completed_session)
            self.current_session = None
            
            self.logger.info(f"✅ 錄製會話完成: {completed_session.session_name}")
            
            return {
                "success": True,
                "session": asdict(completed_session),
                "processed_data": processed_data,
                "message": f"錄製會話 '{completed_session.session_name}' 已完成"
            }
            
        except Exception as e:
            self.logger.error(f"❌ 停止錄製失敗: {e}")
            if self.current_session:
                self.current_session.status = RecordingStatus.FAILED
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_recording_status(self) -> Dict[str, Any]:
        """獲取錄製狀態"""
        try:
            status_info = {
                "is_recording": self.current_session is not None and 
                              self.current_session.status == RecordingStatus.RECORDING,
                "current_session": asdict(self.current_session) if self.current_session else None,
                "total_sessions": len(self.sessions_history),
                "recent_sessions": [asdict(s) for s in self.sessions_history[-5:]],
                "component_info": self.component_info
            }
            
            return {
                "success": True,
                "data": status_info
            }
            
        except Exception as e:
            self.logger.error(f"❌ 獲取錄製狀態失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_workflow_patterns(self, workflow_data: Dict, analysis_depth: str = "basic") -> Dict[str, Any]:
        """分析工作流模式"""
        try:
            steps = workflow_data.get("workflow_steps", [])
            if not steps:
                return {
                    "success": False,
                    "error": "沒有工作流步驟數據"
                }
            
            analysis_result = {
                "analysis_type": analysis_depth,
                "timestamp": datetime.now().isoformat(),
                "patterns": self.data_processor._analyze_patterns(steps),
                "recommendations": [],
                "optimization_suggestions": []
            }
            
            # 基於分析深度提供不同級別的建議
            if analysis_depth == "advanced":
                analysis_result["recommendations"] = self._generate_advanced_recommendations(steps)
                analysis_result["optimization_suggestions"] = self._generate_optimization_suggestions(steps)
            else:
                analysis_result["recommendations"] = self._generate_basic_recommendations(steps)
            
            return {
                "success": True,
                "analysis": analysis_result
            }
            
        except Exception as e:
            self.logger.error(f"❌ 分析工作流模式失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_basic_recommendations(self, steps: List[Dict]) -> List[str]:
        """生成基本建議"""
        recommendations = []
        
        # 檢查錯誤率
        failed_steps = sum(1 for step in steps if not step.get("success", True))
        if failed_steps > 0:
            error_rate = failed_steps / len(steps)
            if error_rate > 0.1:
                recommendations.append(f"工作流錯誤率較高 ({error_rate:.1%})，建議檢查失敗步驟")
        
        # 檢查執行時間
        total_time = sum(step.get("execution_time", 0) for step in steps)
        if total_time > 30:
            recommendations.append("工作流執行時間較長，考慮優化步驟順序")
        
        # 檢查重複動作
        actions = [step.get("action_type") for step in steps]
        if len(set(actions)) < len(actions) * 0.5:
            recommendations.append("檢測到重複動作，可能存在優化空間")
        
        return recommendations
    
    def _generate_advanced_recommendations(self, steps: List[Dict]) -> List[str]:
        """生成高級建議"""
        recommendations = self._generate_basic_recommendations(steps)
        
        # 高級分析
        selectors = [step.get("selector") for step in steps if step.get("selector")]
        if len(set(selectors)) < len(selectors) * 0.3:
            recommendations.append("檢測到大量重複選擇器，建議使用循環或批量操作")
        
        # 分析等待時間
        wait_times = [step.get("wait_time", 0) for step in steps]
        avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0
        if avg_wait > 2:
            recommendations.append("平均等待時間較長，建議優化頁面加載或使用智能等待")
        
        return recommendations
    
    def _generate_optimization_suggestions(self, steps: List[Dict]) -> List[Dict]:
        """生成優化建議"""
        suggestions = []
        
        # 建議並行化
        navigation_steps = [step for step in steps if step.get("action_type") == "navigate"]
        if len(navigation_steps) > 2:
            suggestions.append({
                "type": "parallelization",
                "description": "多個導航步驟可以考慮並行處理",
                "impact": "medium"
            })
        
        # 建議緩存
        repeated_selectors = {}
        for step in steps:
            selector = step.get("selector", "")
            if selector:
                repeated_selectors[selector] = repeated_selectors.get(selector, 0) + 1
        
        high_frequency_selectors = [s for s, count in repeated_selectors.items() if count > 3]
        if high_frequency_selectors:
            suggestions.append({
                "type": "caching",
                "description": f"高頻選擇器 {high_frequency_selectors[:3]} 建議使用元素緩存",
                "impact": "high"
            })
        
        return suggestions
    
    async def list_sessions(self, limit: int = 10) -> Dict[str, Any]:
        """列出錄製會話"""
        try:
            sessions = self.sessions_history[-limit:] if limit > 0 else self.sessions_history
            
            return {
                "success": True,
                "sessions": [asdict(s) for s in sessions],
                "total_count": len(self.sessions_history)
            }
            
        except Exception as e:
            self.logger.error(f"❌ 列出會話失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """獲取會話數據"""
        try:
            # 查找會話
            session = None
            for s in self.sessions_history:
                if s.session_id == session_id:
                    session = s
                    break
            
            if not session:
                return {
                    "success": False,
                    "error": f"會話 {session_id} 不存在"
                }
            
            # 讀取會話數據文件
            data_file = self.recordings_dir / session_id / "workflow_data.json"
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
            else:
                workflow_data = None
            
            return {
                "success": True,
                "session": asdict(session),
                "workflow_data": workflow_data
            }
            
        except Exception as e:
            self.logger.error(f"❌ 獲取會話數據失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def export_workflow(self, session_id: str, format: str = "json") -> Dict[str, Any]:
        """導出工作流數據"""
        try:
            session_data = await self.get_session_data(session_id)
            if not session_data["success"]:
                return session_data
            
            workflow_data = session_data["workflow_data"]
            if not workflow_data:
                return {
                    "success": False,
                    "error": "會話數據不存在"
                }
            
            # 根據格式導出
            if format == "json":
                export_data = workflow_data
            elif format == "csv":
                # 簡化的CSV導出
                steps = workflow_data.get("workflow_steps", [])
                csv_data = "step_id,action_type,selector,value,success,execution_time\n"
                for step in steps:
                    csv_data += f"{step['step_id']},{step['action_type']},{step['selector']},{step.get('value', '')},{step['success']},{step['execution_time']}\n"
                export_data = csv_data
            elif format == "yaml":
                import yaml
                export_data = yaml.dump(workflow_data, default_flow_style=False, allow_unicode=True)
            else:
                return {
                    "success": False,
                    "error": f"不支持的導出格式: {format}"
                }
            
            return {
                "success": True,
                "format": format,
                "data": export_data,
                "session_id": session_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ 導出工作流失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_component_info(self) -> Dict[str, Any]:
        """獲取組件信息"""
        return self.component_info

def create_recorder_workflow_mcp(recordings_dir: str = "./recordings") -> RecorderWorkflowMCP:
    """創建Recorder_Workflow MCP組件實例"""
    return RecorderWorkflowMCP(recordings_dir)

# 導出主要類和函數
__all__ = [
    "RecorderWorkflowMCP",
    "RecordingSession", 
    "WorkflowStep",
    "RecordingStatus",
    "WorkflowType",
    "create_recorder_workflow_mcp"
]

