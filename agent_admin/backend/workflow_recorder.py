# -*- coding: utf-8 -*-
"""
Workflow Recorder - 工作流錄製器

整合browser-use/workflow-use工具，提供工作流錄製、解析和管理功能
與Enhanced Interaction Log Manager和Simplified RL SRT Adapter協同工作

作者: Agentic Agent Team
版本: 1.0.0
日期: 2025-06-22
"""

import os
import sys
import json
import logging
import asyncio
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import tempfile
import shutil
import uuid

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("workflow_recorder")

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

@dataclass
class RecordingSession:
    """錄製會話"""
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
    """工作流步驟"""
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

class WorkflowRecorder:
    """工作流錄製器"""
    
    def __init__(self, workflow_use_path: str = "./workflow-use", 
                 recordings_dir: str = "./recordings"):
        self.workflow_use_path = Path(workflow_use_path)
        self.recordings_dir = Path(recordings_dir)
        self.recordings_dir.mkdir(exist_ok=True)
        
        self.current_session: Optional[RecordingSession] = None
        self.recording_process: Optional[subprocess.Popen] = None
        self.sessions_history: List[RecordingSession] = []
        
        self.logger = logging.getLogger(f"{__name__}.WorkflowRecorder")
        
        # 檢查workflow-use環境
        self._check_environment()
    
    def _check_environment(self):
        """檢查workflow-use環境"""
        try:
            if not self.workflow_use_path.exists():
                self.logger.warning(f"Workflow-use路徑不存在: {self.workflow_use_path}")
                return False
            
            # 檢查必要文件
            required_files = ["workflows/cli.py", "extension"]
            for file_path in required_files:
                if not (self.workflow_use_path / file_path).exists():
                    self.logger.warning(f"缺少必要文件: {file_path}")
                    return False
            
            self.logger.info("Workflow-use環境檢查通過")
            return True
            
        except Exception as e:
            self.logger.error(f"環境檢查失敗: {e}")
            return False
    
    async def start_recording(self, session_name: str, 
                            workflow_type: WorkflowType = WorkflowType.AUTOMATION,
                            description: str = "") -> RecordingSession:
        """開始錄製工作流"""
        try:
            if self.current_session and self.current_session.status == RecordingStatus.RECORDING:
                raise ValueError("已有錄製會話正在進行中")
            
            # 創建新的錄製會話
            session_id = f"workflow_{uuid.uuid4().hex[:8]}"
            session = RecordingSession(
                session_id=session_id,
                session_name=session_name,
                start_time=datetime.now().isoformat(),
                status=RecordingStatus.RECORDING,
                workflow_type=workflow_type,
                description=description
            )
            
            # 創建會話目錄
            session_dir = self.recordings_dir / session_id
            session_dir.mkdir(exist_ok=True)
            
            # 啟動workflow-use錄製
            await self._start_workflow_use_recording(session)
            
            self.current_session = session
            self.logger.info(f"開始錄製會話: {session_name} ({session_id})")
            
            return session
            
        except Exception as e:
            self.logger.error(f"開始錄製失敗: {e}")
            raise
    
    async def stop_recording(self) -> Optional[RecordingSession]:
        """停止錄製並處理結果"""
        try:
            if not self.current_session or self.current_session.status != RecordingStatus.RECORDING:
                self.logger.warning("沒有正在進行的錄製會話")
                return None
            
            # 停止錄製進程
            await self._stop_workflow_use_recording()
            
            # 更新會話狀態
            self.current_session.status = RecordingStatus.PROCESSING
            self.current_session.end_time = datetime.now().isoformat()
            
            # 處理錄製結果
            workflow_data = await self._process_recording_result()
            
            if workflow_data:
                self.current_session.status = RecordingStatus.COMPLETED
                self.current_session.recorded_steps = len(workflow_data.get('steps', []))
                self.current_session.workflow_file = workflow_data.get('file_path')
            else:
                self.current_session.status = RecordingStatus.FAILED
            
            # 保存會話到歷史
            self.sessions_history.append(self.current_session)
            completed_session = self.current_session
            self.current_session = None
            
            self.logger.info(f"錄製會話完成: {completed_session.session_name}")
            return completed_session
            
        except Exception as e:
            self.logger.error(f"停止錄製失敗: {e}")
            if self.current_session:
                self.current_session.status = RecordingStatus.FAILED
            raise
    
    async def _start_workflow_use_recording(self, session: RecordingSession):
        """啟動workflow-use錄製進程"""
        try:
            # 切換到workflow-use目錄
            workflows_dir = self.workflow_use_path / "workflows"
            
            # 構建錄製命令
            cmd = [
                "python", "cli.py", "create-workflow",
                "--output", f"../recordings/{session.session_id}/workflow.json",
                "--name", session.session_name,
                "--description", session.description
            ]
            
            # 啟動錄製進程
            self.recording_process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=workflows_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self.logger.info(f"Workflow-use錄製進程已啟動: PID {self.recording_process.pid}")
            
        except Exception as e:
            self.logger.error(f"啟動workflow-use錄製失敗: {e}")
            raise
    
    async def _stop_workflow_use_recording(self):
        """停止workflow-use錄製進程"""
        try:
            if self.recording_process:
                # 發送終止信號
                self.recording_process.terminate()
                
                # 等待進程結束
                try:
                    await asyncio.wait_for(self.recording_process.wait(), timeout=10.0)
                except asyncio.TimeoutError:
                    # 強制殺死進程
                    self.recording_process.kill()
                    await self.recording_process.wait()
                
                self.logger.info("Workflow-use錄製進程已停止")
                self.recording_process = None
            
        except Exception as e:
            self.logger.error(f"停止workflow-use錄製失敗: {e}")
            raise
    
    async def _process_recording_result(self) -> Optional[Dict[str, Any]]:
        """處理錄製結果"""
        try:
            if not self.current_session:
                return None
            
            session_dir = self.recordings_dir / self.current_session.session_id
            workflow_file = session_dir / "workflow.json"
            
            if not workflow_file.exists():
                self.logger.error(f"工作流文件不存在: {workflow_file}")
                return None
            
            # 讀取工作流文件
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            
            # 解析工作流數據
            parsed_data = self.parse_workflow_json(workflow_data)
            
            # 保存解析結果
            parsed_file = session_dir / "parsed_workflow.json"
            with open(parsed_file, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, ensure_ascii=False, indent=2)
            
            # 生成會話摘要
            summary = self._generate_session_summary(parsed_data)
            summary_file = session_dir / "session_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            return {
                'file_path': str(workflow_file),
                'parsed_data': parsed_data,
                'summary': summary,
                'steps': parsed_data.get('steps', [])
            }
            
        except Exception as e:
            self.logger.error(f"處理錄製結果失敗: {e}")
            return None
    
    def parse_workflow_json(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析工作流JSON數據"""
        try:
            parsed_data = {
                'workflow_id': workflow_data.get('id', 'unknown'),
                'name': workflow_data.get('name', 'Unnamed Workflow'),
                'description': workflow_data.get('description', ''),
                'version': workflow_data.get('version', '1.0'),
                'created_at': workflow_data.get('created_at', datetime.now().isoformat()),
                'steps': [],
                'variables': workflow_data.get('variables', {}),
                'metadata': workflow_data.get('metadata', {}),
                'statistics': {
                    'total_steps': 0,
                    'action_types': {},
                    'estimated_duration': 0.0,
                    'complexity_score': 0.0
                }
            }
            
            # 解析步驟
            steps_data = workflow_data.get('steps', [])
            for i, step_data in enumerate(steps_data):
                step = self._parse_workflow_step(i, step_data)
                parsed_data['steps'].append(step)
            
            # 計算統計信息
            parsed_data['statistics'] = self._calculate_workflow_statistics(parsed_data['steps'])
            
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"解析工作流JSON失敗: {e}")
            return {}
    
    def _parse_workflow_step(self, step_index: int, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析工作流步驟"""
        try:
            step = {
                'step_id': step_index,
                'action_type': step_data.get('action', 'unknown'),
                'selector': step_data.get('selector', ''),
                'value': step_data.get('value'),
                'wait_time': step_data.get('wait', 0.0),
                'screenshot': step_data.get('screenshot'),
                'success': step_data.get('success', True),
                'error_message': step_data.get('error'),
                'execution_time': step_data.get('duration', 0.0),
                'metadata': {
                    'url': step_data.get('url'),
                    'element_text': step_data.get('element_text'),
                    'coordinates': step_data.get('coordinates'),
                    'timestamp': step_data.get('timestamp'),
                    'browser_info': step_data.get('browser_info', {})
                }
            }
            
            return step
            
        except Exception as e:
            self.logger.error(f"解析工作流步驟失敗: {e}")
            return {}
    
    def _calculate_workflow_statistics(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """計算工作流統計信息"""
        try:
            statistics = {
                'total_steps': len(steps),
                'action_types': {},
                'estimated_duration': 0.0,
                'complexity_score': 0.0,
                'success_rate': 0.0,
                'unique_selectors': set(),
                'urls_visited': set()
            }
            
            successful_steps = 0
            
            for step in steps:
                # 統計動作類型
                action_type = step.get('action_type', 'unknown')
                statistics['action_types'][action_type] = statistics['action_types'].get(action_type, 0) + 1
                
                # 累計執行時間
                statistics['estimated_duration'] += step.get('execution_time', 0.0)
                
                # 統計成功率
                if step.get('success', True):
                    successful_steps += 1
                
                # 收集選擇器和URL
                selector = step.get('selector', '')
                if selector:
                    statistics['unique_selectors'].add(selector)
                
                url = step.get('metadata', {}).get('url', '')
                if url:
                    statistics['urls_visited'].add(url)
            
            # 計算成功率
            if len(steps) > 0:
                statistics['success_rate'] = successful_steps / len(steps)
            
            # 計算複雜度分數
            statistics['complexity_score'] = self._calculate_complexity_score(statistics)
            
            # 轉換集合為列表（JSON序列化）
            statistics['unique_selectors'] = list(statistics['unique_selectors'])
            statistics['urls_visited'] = list(statistics['urls_visited'])
            
            return statistics
            
        except Exception as e:
            self.logger.error(f"計算工作流統計失敗: {e}")
            return {}
    
    def _calculate_complexity_score(self, statistics: Dict[str, Any]) -> float:
        """計算複雜度分數"""
        try:
            # 基於多個因素計算複雜度
            step_count_factor = min(statistics['total_steps'] / 10.0, 1.0)  # 步驟數量
            action_variety_factor = len(statistics['action_types']) / 10.0  # 動作類型多樣性
            selector_variety_factor = len(statistics['unique_selectors']) / 20.0  # 選擇器多樣性
            url_variety_factor = len(statistics['urls_visited']) / 5.0  # URL多樣性
            
            complexity_score = (
                step_count_factor * 0.3 +
                action_variety_factor * 0.3 +
                selector_variety_factor * 0.2 +
                url_variety_factor * 0.2
            )
            
            return min(complexity_score, 1.0)  # 限制在0-1範圍內
            
        except Exception as e:
            self.logger.error(f"計算複雜度分數失敗: {e}")
            return 0.5
    
    def _generate_session_summary(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成會話摘要"""
        try:
            statistics = parsed_data.get('statistics', {})
            
            summary = {
                'session_id': self.current_session.session_id if self.current_session else 'unknown',
                'workflow_name': parsed_data.get('name', 'Unknown'),
                'recording_summary': {
                    'total_steps': statistics.get('total_steps', 0),
                    'estimated_duration': statistics.get('estimated_duration', 0.0),
                    'complexity_score': statistics.get('complexity_score', 0.0),
                    'success_rate': statistics.get('success_rate', 0.0),
                    'action_distribution': statistics.get('action_types', {}),
                    'unique_elements': len(statistics.get('unique_selectors', [])),
                    'pages_visited': len(statistics.get('urls_visited', []))
                },
                'quality_assessment': self._assess_recording_quality(statistics),
                'recommendations': self._generate_recommendations(statistics),
                'generated_at': datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"生成會話摘要失敗: {e}")
            return {}
    
    def _assess_recording_quality(self, statistics: Dict[str, Any]) -> Dict[str, Any]:
        """評估錄製質量"""
        try:
            quality = {
                'overall_score': 0.0,
                'factors': {
                    'completeness': 0.0,
                    'reliability': 0.0,
                    'efficiency': 0.0,
                    'maintainability': 0.0
                },
                'issues': [],
                'strengths': []
            }
            
            # 完整性評估
            step_count = statistics.get('total_steps', 0)
            if step_count >= 5:
                quality['factors']['completeness'] = min(step_count / 20.0, 1.0)
                quality['strengths'].append('工作流步驟充足')
            else:
                quality['factors']['completeness'] = step_count / 5.0
                quality['issues'].append('工作流步驟較少，可能不完整')
            
            # 可靠性評估
            success_rate = statistics.get('success_rate', 0.0)
            quality['factors']['reliability'] = success_rate
            if success_rate >= 0.9:
                quality['strengths'].append('執行成功率高')
            elif success_rate < 0.7:
                quality['issues'].append('執行成功率較低，需要優化')
            
            # 效率評估
            avg_step_time = statistics.get('estimated_duration', 0.0) / max(step_count, 1)
            if avg_step_time <= 2.0:
                quality['factors']['efficiency'] = 1.0
                quality['strengths'].append('執行效率高')
            elif avg_step_time <= 5.0:
                quality['factors']['efficiency'] = 0.7
            else:
                quality['factors']['efficiency'] = 0.4
                quality['issues'].append('執行時間較長，需要優化')
            
            # 可維護性評估
            complexity_score = statistics.get('complexity_score', 0.0)
            if complexity_score <= 0.5:
                quality['factors']['maintainability'] = 1.0 - complexity_score
                quality['strengths'].append('工作流結構簡潔')
            else:
                quality['factors']['maintainability'] = 1.0 - complexity_score
                quality['issues'].append('工作流較為複雜，維護難度較高')
            
            # 計算總體分數
            quality['overall_score'] = sum(quality['factors'].values()) / len(quality['factors'])
            
            return quality
            
        except Exception as e:
            self.logger.error(f"評估錄製質量失敗: {e}")
            return {}
    
    def _generate_recommendations(self, statistics: Dict[str, Any]) -> List[str]:
        """生成改進建議"""
        try:
            recommendations = []
            
            # 基於統計信息生成建議
            success_rate = statistics.get('success_rate', 0.0)
            if success_rate < 0.8:
                recommendations.append("建議優化選擇器，提高元素定位的可靠性")
            
            complexity_score = statistics.get('complexity_score', 0.0)
            if complexity_score > 0.7:
                recommendations.append("考慮將複雜工作流拆分為多個簡單的子工作流")
            
            step_count = statistics.get('total_steps', 0)
            if step_count > 30:
                recommendations.append("工作流步驟較多，建議添加檢查點和錯誤處理")
            
            action_types = statistics.get('action_types', {})
            if 'wait' in action_types and action_types['wait'] > step_count * 0.3:
                recommendations.append("等待步驟較多，考慮優化頁面加載時間")
            
            if len(statistics.get('urls_visited', [])) > 5:
                recommendations.append("涉及多個頁面，建議添加頁面驗證步驟")
            
            if not recommendations:
                recommendations.append("工作流質量良好，可以直接使用")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"生成改進建議失敗: {e}")
            return []
    
    def get_recording_status(self) -> Dict[str, Any]:
        """獲取錄製狀態"""
        try:
            status = {
                'is_recording': self.current_session is not None and 
                              self.current_session.status == RecordingStatus.RECORDING,
                'current_session': asdict(self.current_session) if self.current_session else None,
                'total_sessions': len(self.sessions_history),
                'recent_sessions': [asdict(session) for session in self.sessions_history[-5:]],
                'environment_ready': self._check_environment()
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"獲取錄製狀態失敗: {e}")
            return {}
    
    def get_session_by_id(self, session_id: str) -> Optional[RecordingSession]:
        """根據ID獲取會話"""
        for session in self.sessions_history:
            if session.session_id == session_id:
                return session
        return None
    
    def load_workflow_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """加載工作流文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            
            return self.parse_workflow_json(workflow_data)
            
        except Exception as e:
            self.logger.error(f"加載工作流文件失敗: {e}")
            return None
    
    def export_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """導出會話數據"""
        try:
            session = self.get_session_by_id(session_id)
            if not session:
                return None
            
            session_dir = self.recordings_dir / session_id
            
            # 讀取相關文件
            export_data = {
                'session': asdict(session),
                'workflow_data': None,
                'parsed_data': None,
                'summary': None
            }
            
            # 讀取工作流文件
            workflow_file = session_dir / "workflow.json"
            if workflow_file.exists():
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    export_data['workflow_data'] = json.load(f)
            
            # 讀取解析數據
            parsed_file = session_dir / "parsed_workflow.json"
            if parsed_file.exists():
                with open(parsed_file, 'r', encoding='utf-8') as f:
                    export_data['parsed_data'] = json.load(f)
            
            # 讀取摘要
            summary_file = session_dir / "session_summary.json"
            if summary_file.exists():
                with open(summary_file, 'r', encoding='utf-8') as f:
                    export_data['summary'] = json.load(f)
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"導出會話數據失敗: {e}")
            return None

class WorkflowDataProcessor:
    """工作流數據處理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.WorkflowDataProcessor")
    
    def process_workflow_to_training_data(self, workflow_data: Dict[str, Any], 
                                        session_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """將工作流轉換為訓練數據格式"""
        try:
            if session_metadata is None:
                session_metadata = {}
            
            # 提取基本信息
            session_id = session_metadata.get('session_id', workflow_data.get('workflow_id', 'unknown'))
            
            # 構建上下文狀態
            context_state = self._extract_context_state(workflow_data, session_metadata)
            
            # 提取動作序列
            action_sequence = self._extract_action_sequence(workflow_data)
            
            # 計算獎勵信號
            reward_signals = self._calculate_reward_signals(workflow_data, action_sequence)
            
            # 構建訓練數據
            training_data = {
                'session_id': session_id,
                'data_source': 'workflow_recorder',
                'context_state': context_state,
                'action_sequence': action_sequence,
                'reward_signals': reward_signals,
                'metadata': {
                    'workflow_name': workflow_data.get('name', 'Unknown'),
                    'workflow_version': workflow_data.get('version', '1.0'),
                    'recording_timestamp': workflow_data.get('created_at'),
                    'complexity_score': workflow_data.get('statistics', {}).get('complexity_score', 0.0),
                    'total_steps': len(action_sequence),
                    'estimated_duration': workflow_data.get('statistics', {}).get('estimated_duration', 0.0)
                },
                'generated_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"工作流轉換為訓練數據完成: {session_id}")
            return training_data
            
        except Exception as e:
            self.logger.error(f"工作流轉訓練數據失敗: {e}")
            return {}
    
    def _extract_context_state(self, workflow_data: Dict[str, Any], 
                             session_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """提取上下文狀態"""
        try:
            statistics = workflow_data.get('statistics', {})
            
            # 確定任務類型
            task_type = self._determine_task_type(workflow_data)
            
            # 確定複雜度
            complexity_score = statistics.get('complexity_score', 0.0)
            if complexity_score <= 0.3:
                complexity = 'simple'
            elif complexity_score <= 0.7:
                complexity = 'medium'
            else:
                complexity = 'complex'
            
            context_state = {
                'task_type': task_type,
                'environment_type': 'web_browser',
                'available_tools': len(statistics.get('action_types', {})),
                'user_intent_clarity': self._assess_intent_clarity(workflow_data),
                'initial_complexity': complexity,
                'workflow_metadata': {
                    'total_steps': statistics.get('total_steps', 0),
                    'unique_selectors': len(statistics.get('unique_selectors', [])),
                    'pages_visited': len(statistics.get('urls_visited', [])),
                    'action_distribution': statistics.get('action_types', {})
                }
            }
            
            return context_state
            
        except Exception as e:
            self.logger.error(f"提取上下文狀態失敗: {e}")
            return {}
    
    def _determine_task_type(self, workflow_data: Dict[str, Any]) -> str:
        """確定任務類型"""
        try:
            action_types = workflow_data.get('statistics', {}).get('action_types', {})
            
            # 基於動作類型分布判斷任務類型
            if 'fill' in action_types or 'input' in action_types:
                return 'form_filling'
            elif 'extract' in action_types or 'scrape' in action_types:
                return 'data_extraction'
            elif 'click' in action_types and 'navigate' in action_types:
                return 'navigation'
            elif 'test' in action_types or 'verify' in action_types:
                return 'testing'
            else:
                return 'automation'
                
        except Exception as e:
            self.logger.error(f"確定任務類型失敗: {e}")
            return 'automation'
    
    def _assess_intent_clarity(self, workflow_data: Dict[str, Any]) -> float:
        """評估意圖清晰度"""
        try:
            # 基於工作流的結構化程度評估意圖清晰度
            steps = workflow_data.get('steps', [])
            if not steps:
                return 0.5
            
            # 檢查步驟的一致性和邏輯性
            consistent_actions = 0
            total_actions = len(steps)
            
            for step in steps:
                if step.get('success', True) and step.get('selector'):
                    consistent_actions += 1
            
            clarity_score = consistent_actions / total_actions if total_actions > 0 else 0.5
            
            # 基於描述和命名的清晰度調整
            name = workflow_data.get('name', '')
            description = workflow_data.get('description', '')
            
            if name and name != 'Unnamed Workflow':
                clarity_score += 0.1
            
            if description and len(description) > 10:
                clarity_score += 0.1
            
            return min(clarity_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"評估意圖清晰度失敗: {e}")
            return 0.5
    
    def _extract_action_sequence(self, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取動作序列"""
        try:
            steps = workflow_data.get('steps', [])
            action_sequence = []
            
            for step in steps:
                action = {
                    'step_id': step.get('step_id', 0),
                    'action_type': step.get('action_type', 'unknown'),
                    'parameters': {
                        'selector': step.get('selector', ''),
                        'value': step.get('value'),
                        'wait_time': step.get('wait_time', 0.0)
                    },
                    'execution_time': step.get('execution_time', 0.0),
                    'success': step.get('success', True),
                    'immediate_reward': 1.0 if step.get('success', True) else 0.0,
                    'metadata': step.get('metadata', {})
                }
                
                action_sequence.append(action)
            
            return action_sequence
            
        except Exception as e:
            self.logger.error(f"提取動作序列失敗: {e}")
            return []
    
    def _calculate_reward_signals(self, workflow_data: Dict[str, Any], 
                                action_sequence: List[Dict[str, Any]]) -> Dict[str, float]:
        """計算獎勵信號"""
        try:
            statistics = workflow_data.get('statistics', {})
            
            # 完成獎勵
            success_rate = statistics.get('success_rate', 0.0)
            completion_reward = success_rate
            
            # 效率獎勵
            total_time = statistics.get('estimated_duration', 0.0)
            step_count = len(action_sequence)
            avg_step_time = total_time / max(step_count, 1)
            
            # 效率評分：步驟時間越短越好
            if avg_step_time <= 1.0:
                efficiency_reward = 1.0
            elif avg_step_time <= 3.0:
                efficiency_reward = 0.8
            elif avg_step_time <= 5.0:
                efficiency_reward = 0.6
            else:
                efficiency_reward = 0.4
            
            # 滿意度獎勵（基於工作流質量）
            complexity_score = statistics.get('complexity_score', 0.0)
            satisfaction_reward = 1.0 - complexity_score * 0.3  # 複雜度適中更好
            
            # 時間獎勵（基於執行速度）
            if total_time <= 30.0:
                time_reward = 1.0
            elif total_time <= 60.0:
                time_reward = 0.8
            elif total_time <= 120.0:
                time_reward = 0.6
            else:
                time_reward = 0.4
            
            # 錯誤懲罰
            failed_steps = sum(1 for action in action_sequence if not action.get('success', True))
            error_penalty = failed_steps * 0.1
            
            # 計算總獎勵
            total_reward = (
                completion_reward * 0.4 +
                efficiency_reward * 0.3 +
                satisfaction_reward * 0.2 +
                time_reward * 0.1 -
                error_penalty
            )
            
            reward_signals = {
                'completion_reward': completion_reward,
                'efficiency_reward': efficiency_reward,
                'satisfaction_reward': satisfaction_reward,
                'time_reward': time_reward,
                'error_penalty': error_penalty,
                'total_reward': max(total_reward, 0.0)  # 確保非負
            }
            
            return reward_signals
            
        except Exception as e:
            self.logger.error(f"計算獎勵信號失敗: {e}")
            return {}

# 導出主要類
__all__ = [
    'WorkflowRecorder',
    'WorkflowDataProcessor',
    'RecordingSession',
    'WorkflowStep',
    'RecordingStatus',
    'WorkflowType'
]

if __name__ == "__main__":
    # 測試工作流錄製器
    async def test_workflow_recorder():
        recorder = WorkflowRecorder()
        processor = WorkflowDataProcessor()
        
        # 測試錄製狀態
        status = recorder.get_recording_status()
        print("錄製狀態:")
        print(f"環境就緒: {status.get('environment_ready')}")
        print(f"正在錄製: {status.get('is_recording')}")
        print(f"歷史會話數: {status.get('total_sessions')}")
        
        # 模擬工作流數據
        test_workflow_data = {
            'workflow_id': 'test_workflow_001',
            'name': 'Test Form Filling',
            'description': 'Test workflow for form filling automation',
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'steps': [
                {
                    'step_id': 0,
                    'action_type': 'navigate',
                    'selector': '',
                    'value': 'https://example.com/form',
                    'wait_time': 2.0,
                    'success': True,
                    'execution_time': 1.5,
                    'metadata': {'url': 'https://example.com/form'}
                },
                {
                    'step_id': 1,
                    'action_type': 'fill',
                    'selector': '#name',
                    'value': 'John Doe',
                    'wait_time': 0.5,
                    'success': True,
                    'execution_time': 0.8,
                    'metadata': {'element_text': 'Name field'}
                },
                {
                    'step_id': 2,
                    'action_type': 'click',
                    'selector': '#submit',
                    'value': None,
                    'wait_time': 1.0,
                    'success': True,
                    'execution_time': 0.3,
                    'metadata': {'element_text': 'Submit button'}
                }
            ],
            'variables': {'user_name': 'John Doe'},
            'metadata': {'browser': 'chrome', 'version': '1.0'}
        }
        
        # 解析工作流
        parsed_data = recorder.parse_workflow_json(test_workflow_data)
        print(f"\n解析結果:")
        print(f"工作流名稱: {parsed_data.get('name')}")
        print(f"總步驟數: {parsed_data.get('statistics', {}).get('total_steps')}")
        print(f"複雜度分數: {parsed_data.get('statistics', {}).get('complexity_score'):.2f}")
        print(f"成功率: {parsed_data.get('statistics', {}).get('success_rate'):.2f}")
        
        # 轉換為訓練數據
        training_data = processor.process_workflow_to_training_data(parsed_data)
        print(f"\n訓練數據:")
        print(f"會話ID: {training_data.get('session_id')}")
        print(f"任務類型: {training_data.get('context_state', {}).get('task_type')}")
        print(f"動作序列長度: {len(training_data.get('action_sequence', []))}")
        print(f"總獎勵: {training_data.get('reward_signals', {}).get('total_reward', 0):.2f}")
    
    # 運行測試
    asyncio.run(test_workflow_recorder())

