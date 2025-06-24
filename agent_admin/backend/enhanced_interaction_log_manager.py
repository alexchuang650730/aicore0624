# -*- coding: utf-8 -*-
"""
Enhanced Interaction Log Manager - 增強版交互日誌管理器

整合原有功能並添加數據處理、模式識別、工作流模板化能力
移除Cloud Edge Data MCP後的統一數據處理中心

作者: Agentic Agent Team
版本: 2.0.0
日期: 2025-06-22
"""

import os
import sys
import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import re

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("enhanced_interaction_log_manager")

class InteractionType(Enum):
    """交互類型枚舉"""
    COMMAND_EXECUTION = "command_execution"
    CODE_EXECUTION = "code_execution"
    FILE_OPERATION = "file_operation"
    BROWSER_NAVIGATION = "browser_navigation"
    API_CALL = "api_call"
    USER_INTERACTION = "user_interaction"
    SYSTEM_DIAGNOSIS = "system_diagnosis"
    ERROR_HANDLING = "error_handling"
    WORKFLOW_EXECUTION = "workflow_execution"

class PatternType(Enum):
    """模式類型枚舉"""
    SUCCESSFUL_WORKFLOW = "successful_workflow"
    ERROR_PATTERN = "error_pattern"
    OPTIMIZATION_OPPORTUNITY = "optimization_opportunity"
    USER_PREFERENCE = "user_preference"
    CONTEXT_TRIGGER = "context_trigger"

@dataclass
class InteractionData:
    """標準化交互數據結構"""
    session_id: str
    timestamp: str
    user_id: str
    interaction_type: InteractionType
    context: Dict[str, Any]
    action_sequence: List[Dict[str, Any]]
    outcomes: Dict[str, Any]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class WorkflowTemplate:
    """工作流模板"""
    id: str
    name: str
    description: str
    context_type: str
    steps: List[Dict[str, Any]]
    conditions: Dict[str, Any]
    expected_outcomes: List[str]
    estimated_time: float
    confidence_score: float
    usage_count: int = 0
    success_rate: float = 0.0

class DataStandardizer:
    """數據標準化處理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DataStandardizer")
    
    def standardize_replay(self, replay_data: Dict[str, Any]) -> InteractionData:
        """標準化Replay數據"""
        try:
            # 提取基本信息
            session_id = replay_data.get('session_id', self._generate_session_id())
            timestamp = replay_data.get('timestamp', datetime.now().isoformat())
            user_id = replay_data.get('user_id', 'replay_user')
            
            # 提取上下文
            context = self._extract_context(replay_data)
            
            # 提取動作序列
            action_sequence = self._extract_action_sequence(replay_data)
            
            # 提取結果
            outcomes = self._extract_outcomes(replay_data)
            
            # 確定交互類型
            interaction_type = self._determine_interaction_type(action_sequence)
            
            # 提取元數據
            metadata = self._extract_metadata(replay_data)
            
            return InteractionData(
                session_id=session_id,
                timestamp=timestamp,
                user_id=user_id,
                interaction_type=interaction_type,
                context=context,
                action_sequence=action_sequence,
                outcomes=outcomes,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"數據標準化失敗: {e}")
            raise
    
    def _generate_session_id(self) -> str:
        """生成會話ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:16]
    
    def _extract_context(self, replay_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取上下文信息"""
        return {
            'task_description': replay_data.get('description', ''),
            'initial_state': replay_data.get('initial_state', {}),
            'environment': replay_data.get('environment', {}),
            'user_intent': replay_data.get('user_intent', ''),
            'available_tools': replay_data.get('available_tools', [])
        }
    
    def _extract_action_sequence(self, replay_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取動作序列"""
        actions = []
        
        for step in replay_data.get('steps', []):
            action = {
                'type': step.get('action', 'unknown'),
                'parameters': step.get('parameters', {}),
                'timestamp': step.get('timestamp'),
                'result': step.get('result', {}),
                'success': step.get('success', True),
                'execution_time': step.get('execution_time', 0),
                'error_message': step.get('error_message', '')
            }
            actions.append(action)
        
        return actions
    
    def _extract_outcomes(self, replay_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取執行結果"""
        return {
            'overall_success': replay_data.get('success', True),
            'completion_time': replay_data.get('completion_time', 0),
            'final_state': replay_data.get('final_state', {}),
            'user_satisfaction': replay_data.get('user_satisfaction', 0.8),
            'errors_encountered': replay_data.get('errors', []),
            'resources_used': replay_data.get('resources_used', {})
        }
    
    def _determine_interaction_type(self, action_sequence: List[Dict[str, Any]]) -> InteractionType:
        """根據動作序列確定交互類型"""
        if not action_sequence:
            return InteractionType.USER_INTERACTION
        
        # 分析主要動作類型
        action_types = [action.get('type', '') for action in action_sequence]
        
        if any('command' in action_type.lower() for action_type in action_types):
            return InteractionType.COMMAND_EXECUTION
        elif any('code' in action_type.lower() for action_type in action_types):
            return InteractionType.CODE_EXECUTION
        elif any('file' in action_type.lower() for action_type in action_types):
            return InteractionType.FILE_OPERATION
        elif any('browser' in action_type.lower() for action_type in action_types):
            return InteractionType.BROWSER_NAVIGATION
        elif any('api' in action_type.lower() for action_type in action_types):
            return InteractionType.API_CALL
        else:
            return InteractionType.WORKFLOW_EXECUTION
    
    def _extract_metadata(self, replay_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取元數據"""
        return {
            'source': 'replay_data',
            'version': replay_data.get('version', '1.0'),
            'tags': replay_data.get('tags', []),
            'priority': replay_data.get('priority', 'normal'),
            'complexity': self._assess_complexity(replay_data)
        }
    
    def _assess_complexity(self, replay_data: Dict[str, Any]) -> str:
        """評估任務複雜度"""
        step_count = len(replay_data.get('steps', []))
        
        if step_count <= 3:
            return 'simple'
        elif step_count <= 10:
            return 'medium'
        else:
            return 'complex'

class FeatureExtractor:
    """特徵提取器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.FeatureExtractor")
    
    def extract_features(self, interaction_data: InteractionData) -> Dict[str, Any]:
        """提取交互特徵"""
        try:
            features = {
                'basic_features': self._extract_basic_features(interaction_data),
                'sequence_features': self._extract_sequence_features(interaction_data),
                'context_features': self._extract_context_features(interaction_data),
                'outcome_features': self._extract_outcome_features(interaction_data),
                'temporal_features': self._extract_temporal_features(interaction_data)
            }
            
            return features
            
        except Exception as e:
            self.logger.error(f"特徵提取失敗: {e}")
            return {}
    
    def _extract_basic_features(self, interaction_data: InteractionData) -> Dict[str, Any]:
        """提取基本特徵"""
        return {
            'interaction_type': interaction_data.interaction_type.value,
            'action_count': len(interaction_data.action_sequence),
            'success_rate': self._calculate_action_success_rate(interaction_data.action_sequence),
            'complexity': interaction_data.metadata.get('complexity', 'medium'),
            'user_id': interaction_data.user_id
        }
    
    def _extract_sequence_features(self, interaction_data: InteractionData) -> Dict[str, Any]:
        """提取序列特徵"""
        action_sequence = interaction_data.action_sequence
        
        return {
            'action_types': [action.get('type') for action in action_sequence],
            'action_pattern': self._extract_action_pattern(action_sequence),
            'error_positions': self._find_error_positions(action_sequence),
            'retry_patterns': self._identify_retry_patterns(action_sequence),
            'branching_points': self._find_branching_points(action_sequence)
        }
    
    def _extract_context_features(self, interaction_data: InteractionData) -> Dict[str, Any]:
        """提取上下文特徵"""
        context = interaction_data.context
        
        return {
            'task_type': self._classify_task_type(context),
            'environment_type': context.get('environment', {}).get('type', 'unknown'),
            'available_tools': len(context.get('available_tools', [])),
            'initial_state_complexity': self._assess_state_complexity(context.get('initial_state', {})),
            'user_intent_clarity': self._assess_intent_clarity(context.get('user_intent', ''))
        }
    
    def _extract_outcome_features(self, interaction_data: InteractionData) -> Dict[str, Any]:
        """提取結果特徵"""
        outcomes = interaction_data.outcomes
        
        return {
            'overall_success': outcomes.get('overall_success', False),
            'completion_time': outcomes.get('completion_time', 0),
            'error_count': len(outcomes.get('errors_encountered', [])),
            'user_satisfaction': outcomes.get('user_satisfaction', 0.5),
            'resource_efficiency': self._calculate_resource_efficiency(outcomes.get('resources_used', {}))
        }
    
    def _extract_temporal_features(self, interaction_data: InteractionData) -> Dict[str, Any]:
        """提取時間特徵"""
        action_sequence = interaction_data.action_sequence
        
        execution_times = [action.get('execution_time', 0) for action in action_sequence]
        
        return {
            'total_time': sum(execution_times),
            'average_action_time': sum(execution_times) / len(execution_times) if execution_times else 0,
            'time_variance': self._calculate_time_variance(execution_times),
            'peak_time': max(execution_times) if execution_times else 0,
            'time_distribution': self._analyze_time_distribution(execution_times)
        }
    
    def _calculate_action_success_rate(self, action_sequence: List[Dict[str, Any]]) -> float:
        """計算動作成功率"""
        if not action_sequence:
            return 0.0
        
        successful_actions = sum(1 for action in action_sequence if action.get('success', True))
        return successful_actions / len(action_sequence)
    
    def _extract_action_pattern(self, action_sequence: List[Dict[str, Any]]) -> str:
        """提取動作模式"""
        action_types = [action.get('type', 'unknown') for action in action_sequence]
        return ' -> '.join(action_types)
    
    def _find_error_positions(self, action_sequence: List[Dict[str, Any]]) -> List[int]:
        """找到錯誤位置"""
        error_positions = []
        for i, action in enumerate(action_sequence):
            if not action.get('success', True):
                error_positions.append(i)
        return error_positions
    
    def _identify_retry_patterns(self, action_sequence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """識別重試模式"""
        retry_patterns = []
        
        for i in range(len(action_sequence) - 1):
            current_action = action_sequence[i]
            next_action = action_sequence[i + 1]
            
            if (current_action.get('type') == next_action.get('type') and
                not current_action.get('success', True)):
                retry_patterns.append({
                    'position': i,
                    'action_type': current_action.get('type'),
                    'retry_count': 1
                })
        
        return retry_patterns
    
    def _find_branching_points(self, action_sequence: List[Dict[str, Any]]) -> List[int]:
        """找到分支點"""
        # 簡化實現：找到錯誤後的恢復點
        branching_points = []
        
        for i, action in enumerate(action_sequence):
            if not action.get('success', True) and i < len(action_sequence) - 1:
                branching_points.append(i + 1)
        
        return branching_points
    
    def _classify_task_type(self, context: Dict[str, Any]) -> str:
        """分類任務類型"""
        task_description = context.get('task_description', '').lower()
        
        if 'debug' in task_description or 'fix' in task_description:
            return 'debugging'
        elif 'deploy' in task_description or 'install' in task_description:
            return 'deployment'
        elif 'test' in task_description or 'verify' in task_description:
            return 'testing'
        elif 'create' in task_description or 'build' in task_description:
            return 'development'
        else:
            return 'general'
    
    def _assess_state_complexity(self, initial_state: Dict[str, Any]) -> str:
        """評估狀態複雜度"""
        state_size = len(str(initial_state))
        
        if state_size < 100:
            return 'simple'
        elif state_size < 500:
            return 'medium'
        else:
            return 'complex'
    
    def _assess_intent_clarity(self, user_intent: str) -> float:
        """評估意圖清晰度"""
        if not user_intent:
            return 0.0
        
        # 簡化實現：基於長度和關鍵詞
        clarity_score = min(len(user_intent) / 100, 1.0)
        
        # 檢查是否包含明確的動作詞
        action_words = ['create', 'fix', 'deploy', 'test', 'check', 'install', 'update']
        if any(word in user_intent.lower() for word in action_words):
            clarity_score += 0.2
        
        return min(clarity_score, 1.0)
    
    def _calculate_resource_efficiency(self, resources_used: Dict[str, Any]) -> float:
        """計算資源效率"""
        # 簡化實現：基於資源使用情況
        if not resources_used:
            return 0.8  # 默認效率
        
        cpu_usage = resources_used.get('cpu', 0.5)
        memory_usage = resources_used.get('memory', 0.5)
        
        # 效率 = 1 - 平均資源使用率
        efficiency = 1.0 - (cpu_usage + memory_usage) / 2
        return max(0.0, min(1.0, efficiency))
    
    def _calculate_time_variance(self, execution_times: List[float]) -> float:
        """計算時間方差"""
        if len(execution_times) < 2:
            return 0.0
        
        mean_time = sum(execution_times) / len(execution_times)
        variance = sum((t - mean_time) ** 2 for t in execution_times) / len(execution_times)
        return variance
    
    def _analyze_time_distribution(self, execution_times: List[float]) -> Dict[str, float]:
        """分析時間分布"""
        if not execution_times:
            return {}
        
        sorted_times = sorted(execution_times)
        n = len(sorted_times)
        
        return {
            'min': sorted_times[0],
            'q1': sorted_times[n // 4] if n > 4 else sorted_times[0],
            'median': sorted_times[n // 2],
            'q3': sorted_times[3 * n // 4] if n > 4 else sorted_times[-1],
            'max': sorted_times[-1]
        }

class PatternAnalyzer:
    """模式分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.PatternAnalyzer")
        self.patterns_db = {}
    
    def analyze_patterns(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """分析操作模式"""
        try:
            patterns = {
                'successful_workflows': self._identify_successful_workflows(features),
                'error_patterns': self._identify_error_patterns(features),
                'optimization_opportunities': self._find_optimizations(features),
                'user_preferences': self._extract_user_preferences(features),
                'context_triggers': self._identify_context_triggers(features)
            }
            
            # 更新模式數據庫
            self._update_patterns_db(patterns)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"模式分析失敗: {e}")
            return {}
    
    def _identify_successful_workflows(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """識別成功的工作流模式"""
        successful_patterns = []
        
        outcome_features = features.get('outcome_features', {})
        if outcome_features.get('overall_success', False):
            pattern = {
                'pattern_type': PatternType.SUCCESSFUL_WORKFLOW.value,
                'context_type': features.get('context_features', {}).get('task_type', 'unknown'),
                'action_pattern': features.get('sequence_features', {}).get('action_pattern', ''),
                'success_indicators': {
                    'completion_time': outcome_features.get('completion_time', 0),
                    'user_satisfaction': outcome_features.get('user_satisfaction', 0),
                    'resource_efficiency': outcome_features.get('resource_efficiency', 0),
                    'error_count': outcome_features.get('error_count', 0)
                },
                'confidence_score': self._calculate_pattern_confidence(features),
                'reusability_score': self._assess_reusability(features)
            }
            successful_patterns.append(pattern)
        
        return successful_patterns
    
    def _identify_error_patterns(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """識別錯誤模式"""
        error_patterns = []
        
        sequence_features = features.get('sequence_features', {})
        error_positions = sequence_features.get('error_positions', [])
        
        if error_positions:
            pattern = {
                'pattern_type': PatternType.ERROR_PATTERN.value,
                'error_positions': error_positions,
                'error_types': self._classify_error_types(features),
                'recovery_strategies': self._identify_recovery_strategies(features),
                'prevention_measures': self._suggest_prevention_measures(features),
                'impact_assessment': self._assess_error_impact(features)
            }
            error_patterns.append(pattern)
        
        return error_patterns
    
    def _find_optimizations(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """找到優化機會"""
        optimizations = []
        
        temporal_features = features.get('temporal_features', {})
        outcome_features = features.get('outcome_features', {})
        
        # 時間優化機會
        if temporal_features.get('time_variance', 0) > 10:
            optimizations.append({
                'type': 'time_optimization',
                'description': '執行時間不穩定，可以優化',
                'potential_improvement': '減少20-30%執行時間',
                'suggested_actions': ['並行化操作', '緩存中間結果', '優化算法']
            })
        
        # 資源優化機會
        if outcome_features.get('resource_efficiency', 1.0) < 0.7:
            optimizations.append({
                'type': 'resource_optimization',
                'description': '資源使用效率較低',
                'potential_improvement': '提升30-40%資源效率',
                'suggested_actions': ['優化內存使用', '減少CPU密集操作', '使用更高效的算法']
            })
        
        return optimizations
    
    def _extract_user_preferences(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """提取用戶偏好"""
        basic_features = features.get('basic_features', {})
        context_features = features.get('context_features', {})
        
        return {
            'preferred_interaction_types': [basic_features.get('interaction_type', 'unknown')],
            'preferred_tools': context_features.get('available_tools', 0),
            'complexity_tolerance': basic_features.get('complexity', 'medium'),
            'error_tolerance': 1.0 - basic_features.get('success_rate', 1.0),
            'time_preference': self._infer_time_preference(features)
        }
    
    def _identify_context_triggers(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """識別上下文觸發器"""
        context_features = features.get('context_features', {})
        
        triggers = []
        
        # 任務類型觸發器
        task_type = context_features.get('task_type', 'unknown')
        if task_type != 'unknown':
            triggers.append({
                'trigger_type': 'task_type',
                'trigger_value': task_type,
                'recommended_approach': self._get_recommended_approach(task_type),
                'success_probability': self._estimate_success_probability(features)
            })
        
        return triggers
    
    def _calculate_pattern_confidence(self, features: Dict[str, Any]) -> float:
        """計算模式置信度"""
        outcome_features = features.get('outcome_features', {})
        
        success_score = 1.0 if outcome_features.get('overall_success', False) else 0.0
        satisfaction_score = outcome_features.get('user_satisfaction', 0.5)
        efficiency_score = outcome_features.get('resource_efficiency', 0.5)
        
        confidence = (success_score + satisfaction_score + efficiency_score) / 3
        return confidence
    
    def _assess_reusability(self, features: Dict[str, Any]) -> float:
        """評估可重用性"""
        basic_features = features.get('basic_features', {})
        context_features = features.get('context_features', {})
        
        # 基於複雜度和通用性評估
        complexity = basic_features.get('complexity', 'medium')
        task_type = context_features.get('task_type', 'unknown')
        
        complexity_score = {'simple': 0.9, 'medium': 0.7, 'complex': 0.4}.get(complexity, 0.5)
        generality_score = {'general': 0.9, 'development': 0.7, 'debugging': 0.6, 'testing': 0.8, 'deployment': 0.5}.get(task_type, 0.5)
        
        return (complexity_score + generality_score) / 2
    
    def _classify_error_types(self, features: Dict[str, Any]) -> List[str]:
        """分類錯誤類型"""
        # 簡化實現
        sequence_features = features.get('sequence_features', {})
        retry_patterns = sequence_features.get('retry_patterns', [])
        
        error_types = []
        if retry_patterns:
            error_types.append('transient_error')
        
        outcome_features = features.get('outcome_features', {})
        if outcome_features.get('error_count', 0) > 0:
            error_types.append('execution_error')
        
        return error_types or ['unknown_error']
    
    def _identify_recovery_strategies(self, features: Dict[str, Any]) -> List[str]:
        """識別恢復策略"""
        sequence_features = features.get('sequence_features', {})
        retry_patterns = sequence_features.get('retry_patterns', [])
        
        strategies = []
        if retry_patterns:
            strategies.append('retry_with_backoff')
        
        branching_points = sequence_features.get('branching_points', [])
        if branching_points:
            strategies.append('alternative_approach')
        
        return strategies or ['manual_intervention']
    
    def _suggest_prevention_measures(self, features: Dict[str, Any]) -> List[str]:
        """建議預防措施"""
        return [
            'input_validation',
            'precondition_check',
            'resource_availability_check',
            'error_handling_improvement'
        ]
    
    def _assess_error_impact(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """評估錯誤影響"""
        outcome_features = features.get('outcome_features', {})
        temporal_features = features.get('temporal_features', {})
        
        return {
            'time_impact': temporal_features.get('total_time', 0),
            'success_impact': 1.0 - outcome_features.get('overall_success', 0),
            'user_impact': 1.0 - outcome_features.get('user_satisfaction', 0.5),
            'resource_impact': 1.0 - outcome_features.get('resource_efficiency', 0.5)
        }
    
    def _infer_time_preference(self, features: Dict[str, Any]) -> str:
        """推斷時間偏好"""
        temporal_features = features.get('temporal_features', {})
        total_time = temporal_features.get('total_time', 0)
        
        if total_time < 30:
            return 'fast'
        elif total_time < 120:
            return 'moderate'
        else:
            return 'thorough'
    
    def _get_recommended_approach(self, task_type: str) -> str:
        """獲取推薦方法"""
        approaches = {
            'debugging': 'systematic_diagnosis',
            'deployment': 'staged_rollout',
            'testing': 'comprehensive_validation',
            'development': 'iterative_development',
            'general': 'adaptive_approach'
        }
        return approaches.get(task_type, 'default_approach')
    
    def _estimate_success_probability(self, features: Dict[str, Any]) -> float:
        """估計成功概率"""
        basic_features = features.get('basic_features', {})
        context_features = features.get('context_features', {})
        
        success_rate = basic_features.get('success_rate', 0.5)
        intent_clarity = context_features.get('user_intent_clarity', 0.5)
        
        return (success_rate + intent_clarity) / 2
    
    def _update_patterns_db(self, patterns: Dict[str, Any]):
        """更新模式數據庫"""
        timestamp = datetime.now().isoformat()
        
        for pattern_type, pattern_list in patterns.items():
            if pattern_type not in self.patterns_db:
                self.patterns_db[pattern_type] = []
            
            for pattern in pattern_list:
                pattern['discovered_at'] = timestamp
                self.patterns_db[pattern_type].append(pattern)

class WorkflowTemplateManager:
    """工作流模板管理器"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        self.templates = {}
        self.logger = logging.getLogger(f"{__name__}.WorkflowTemplateManager")
        
        # 加載現有模板
        self._load_existing_templates()
    
    def generate_templates(self, patterns: Dict[str, Any]) -> Dict[str, List[WorkflowTemplate]]:
        """基於模式生成工作流模板"""
        templates = {}
        
        try:
            # 從成功工作流生成模板
            if 'successful_workflows' in patterns:
                templates['workflow_templates'] = self._create_workflow_templates(
                    patterns['successful_workflows']
                )
            
            # 從錯誤模式生成恢復模板
            if 'error_patterns' in patterns:
                templates['recovery_templates'] = self._create_recovery_templates(
                    patterns['error_patterns']
                )
            
            # 從優化機會生成優化模板
            if 'optimization_opportunities' in patterns:
                templates['optimization_templates'] = self._create_optimization_templates(
                    patterns['optimization_opportunities']
                )
            
            # 保存模板
            self._save_templates(templates)
            
            return templates
            
        except Exception as e:
            self.logger.error(f"模板生成失敗: {e}")
            return {}
    
    def _create_workflow_templates(self, successful_patterns: List[Dict[str, Any]]) -> List[WorkflowTemplate]:
        """創建工作流模板"""
        templates = []
        
        for pattern in successful_patterns:
            template_id = self._generate_template_id(pattern)
            
            template = WorkflowTemplate(
                id=template_id,
                name=f"{pattern.get('context_type', 'Unknown')} Workflow",
                description=self._generate_description(pattern),
                context_type=pattern.get('context_type', 'unknown'),
                steps=self._extract_template_steps(pattern),
                conditions=self._extract_conditions(pattern),
                expected_outcomes=self._extract_expected_outcomes(pattern),
                estimated_time=pattern.get('success_indicators', {}).get('completion_time', 0),
                confidence_score=pattern.get('confidence_score', 0.5)
            )
            
            templates.append(template)
            self.templates[template_id] = template
        
        return templates
    
    def _create_recovery_templates(self, error_patterns: List[Dict[str, Any]]) -> List[WorkflowTemplate]:
        """創建錯誤恢復模板"""
        templates = []
        
        for pattern in error_patterns:
            template_id = f"recovery_{self._generate_template_id(pattern)}"
            
            template = WorkflowTemplate(
                id=template_id,
                name="Error Recovery Workflow",
                description=f"Recovery strategy for {pattern.get('error_types', ['unknown'])}",
                context_type="error_recovery",
                steps=self._create_recovery_steps(pattern),
                conditions=self._extract_error_conditions(pattern),
                expected_outcomes=["error_resolved", "system_stable"],
                estimated_time=30.0,  # 估計恢復時間
                confidence_score=0.7
            )
            
            templates.append(template)
            self.templates[template_id] = template
        
        return templates
    
    def _create_optimization_templates(self, optimization_opportunities: List[Dict[str, Any]]) -> List[WorkflowTemplate]:
        """創建優化模板"""
        templates = []
        
        for opportunity in optimization_opportunities:
            template_id = f"optimization_{opportunity.get('type', 'unknown')}"
            
            template = WorkflowTemplate(
                id=template_id,
                name=f"{opportunity.get('type', 'Unknown')} Optimization",
                description=opportunity.get('description', ''),
                context_type="optimization",
                steps=self._create_optimization_steps(opportunity),
                conditions={'optimization_needed': True},
                expected_outcomes=[opportunity.get('potential_improvement', 'improved_performance')],
                estimated_time=60.0,  # 估計優化時間
                confidence_score=0.8
            )
            
            templates.append(template)
            self.templates[template_id] = template
        
        return templates
    
    def _generate_template_id(self, pattern: Dict[str, Any]) -> str:
        """生成模板ID"""
        context_type = pattern.get('context_type', 'unknown')
        action_pattern = pattern.get('action_pattern', '')
        
        content = f"{context_type}_{action_pattern}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _generate_description(self, pattern: Dict[str, Any]) -> str:
        """生成模板描述"""
        context_type = pattern.get('context_type', 'unknown')
        confidence = pattern.get('confidence_score', 0.5)
        
        return f"Workflow template for {context_type} tasks with {confidence:.1%} confidence"
    
    def _extract_template_steps(self, pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取模板步驟"""
        action_pattern = pattern.get('action_pattern', '')
        action_types = action_pattern.split(' -> ') if action_pattern else []
        
        steps = []
        for i, action_type in enumerate(action_types):
            step = {
                'step_id': i + 1,
                'action_type': action_type,
                'description': f"Execute {action_type}",
                'required_parameters': [],
                'expected_result': 'success',
                'error_handling': 'retry_once'
            }
            steps.append(step)
        
        return steps
    
    def _extract_conditions(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """提取執行條件"""
        return {
            'context_type': pattern.get('context_type'),
            'min_confidence': 0.6,
            'required_tools': [],
            'preconditions': []
        }
    
    def _extract_expected_outcomes(self, pattern: Dict[str, Any]) -> List[str]:
        """提取預期結果"""
        success_indicators = pattern.get('success_indicators', {})
        
        outcomes = ['task_completed']
        
        if success_indicators.get('user_satisfaction', 0) > 0.8:
            outcomes.append('high_user_satisfaction')
        
        if success_indicators.get('resource_efficiency', 0) > 0.7:
            outcomes.append('efficient_resource_usage')
        
        return outcomes
    
    def _create_recovery_steps(self, error_pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """創建恢復步驟"""
        recovery_strategies = error_pattern.get('recovery_strategies', [])
        
        steps = []
        for i, strategy in enumerate(recovery_strategies):
            step = {
                'step_id': i + 1,
                'action_type': 'recovery_action',
                'strategy': strategy,
                'description': f"Apply {strategy} recovery strategy",
                'required_parameters': [],
                'expected_result': 'error_resolved'
            }
            steps.append(step)
        
        return steps
    
    def _extract_error_conditions(self, error_pattern: Dict[str, Any]) -> Dict[str, Any]:
        """提取錯誤條件"""
        return {
            'error_types': error_pattern.get('error_types', []),
            'error_positions': error_pattern.get('error_positions', []),
            'trigger_conditions': ['error_detected']
        }
    
    def _create_optimization_steps(self, opportunity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """創建優化步驟"""
        suggested_actions = opportunity.get('suggested_actions', [])
        
        steps = []
        for i, action in enumerate(suggested_actions):
            step = {
                'step_id': i + 1,
                'action_type': 'optimization_action',
                'optimization': action,
                'description': f"Apply {action} optimization",
                'required_parameters': [],
                'expected_result': 'performance_improved'
            }
            steps.append(step)
        
        return steps
    
    def _save_templates(self, templates: Dict[str, List[WorkflowTemplate]]):
        """保存模板到文件"""
        try:
            for template_type, template_list in templates.items():
                file_path = self.templates_dir / f"{template_type}.json"
                
                template_data = []
                for template in template_list:
                    template_data.append(asdict(template))
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, ensure_ascii=False, indent=2)
                
                self.logger.info(f"保存了 {len(template_list)} 個 {template_type}")
                
        except Exception as e:
            self.logger.error(f"模板保存失敗: {e}")
    
    def _load_existing_templates(self):
        """加載現有模板"""
        try:
            for template_file in self.templates_dir.glob("*.json"):
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                for template_dict in template_data:
                    template = WorkflowTemplate(**template_dict)
                    self.templates[template.id] = template
                
                self.logger.info(f"加載了 {len(template_data)} 個模板從 {template_file.name}")
                
        except Exception as e:
            self.logger.error(f"模板加載失敗: {e}")
    
    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """獲取指定模板"""
        return self.templates.get(template_id)
    
    def find_matching_templates(self, context: Dict[str, Any]) -> List[WorkflowTemplate]:
        """找到匹配的模板"""
        matching_templates = []
        
        context_type = context.get('task_type', 'unknown')
        
        for template in self.templates.values():
            if template.context_type == context_type:
                matching_templates.append(template)
        
        # 按置信度排序
        matching_templates.sort(key=lambda t: t.confidence_score, reverse=True)
        
        return matching_templates

class EnhancedInteractionLogManager:
    """增強版交互日誌管理器"""
    
    def __init__(self, data_dir: str = "enhanced_interaction_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 初始化組件
        self.data_standardizer = DataStandardizer()
        self.feature_extractor = FeatureExtractor()
        self.pattern_analyzer = PatternAnalyzer()
        self.workflow_templates = WorkflowTemplateManager(str(self.data_dir / "templates"))
        
        # 統計信息
        self.statistics = {
            'total_interactions': 0,
            'successful_interactions': 0,
            'patterns_discovered': 0,
            'templates_generated': 0
        }
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Enhanced Interaction Log Manager 初始化完成")
    
    def process_replay_data(self, replay_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理Replay數據的主入口"""
        try:
            self.logger.info("開始處理Replay數據")
            
            # 1. 數據標準化
            standardized_data = self.data_standardizer.standardize_replay(replay_data)
            self.logger.info(f"數據標準化完成: {standardized_data.session_id}")
            
            # 2. 特徵提取
            features = self.feature_extractor.extract_features(standardized_data)
            self.logger.info("特徵提取完成")
            
            # 3. 模式分析
            patterns = self.pattern_analyzer.analyze_patterns(features)
            self.logger.info(f"模式分析完成，發現 {len(patterns)} 種模式")
            
            # 4. 生成工作流模板
            templates = self.workflow_templates.generate_templates(patterns)
            self.logger.info(f"工作流模板生成完成，創建 {sum(len(t) for t in templates.values())} 個模板")
            
            # 5. 為RL SRT準備訓練數據
            training_data = self._prepare_rl_training_data(patterns, standardized_data, features)
            self.logger.info("RL訓練數據準備完成")
            
            # 6. 更新統計信息
            self._update_statistics(standardized_data, patterns, templates)
            
            # 7. 保存處理結果
            self._save_processing_results(standardized_data, features, patterns, templates)
            
            result = {
                'session_id': standardized_data.session_id,
                'standardized_data': asdict(standardized_data),
                'features': features,
                'patterns': patterns,
                'templates': {k: [asdict(t) for t in v] for k, v in templates.items()},
                'training_data': training_data,
                'statistics': self.statistics.copy()
            }
            
            self.logger.info("Replay數據處理完成")
            return result
            
        except Exception as e:
            self.logger.error(f"Replay數據處理失敗: {e}")
            return {'error': str(e)}
    
    def _prepare_rl_training_data(self, patterns: Dict[str, Any], 
                                 interaction_data: InteractionData,
                                 features: Dict[str, Any]) -> Dict[str, Any]:
        """為RL SRT準備訓練數據"""
        training_data = {
            'session_id': interaction_data.session_id,
            'context_state': self._extract_context_state(interaction_data, features),
            'action_sequence': self._extract_action_sequence_for_rl(interaction_data),
            'reward_signals': self._calculate_reward_signals(patterns, features),
            'state_transitions': self._extract_state_transitions(interaction_data),
            'learning_metadata': {
                'interaction_type': interaction_data.interaction_type.value,
                'complexity': features.get('basic_features', {}).get('complexity', 'medium'),
                'success_rate': features.get('basic_features', {}).get('success_rate', 0.5),
                'confidence_score': patterns.get('successful_workflows', [{}])[0].get('confidence_score', 0.5) if patterns.get('successful_workflows') else 0.5
            }
        }
        
        return training_data
    
    def _extract_context_state(self, interaction_data: InteractionData, features: Dict[str, Any]) -> Dict[str, Any]:
        """提取上下文狀態"""
        return {
            'task_type': features.get('context_features', {}).get('task_type', 'unknown'),
            'environment_type': features.get('context_features', {}).get('environment_type', 'unknown'),
            'available_tools': features.get('context_features', {}).get('available_tools', 0),
            'user_intent_clarity': features.get('context_features', {}).get('user_intent_clarity', 0.5),
            'initial_complexity': features.get('context_features', {}).get('initial_state_complexity', 'medium')
        }
    
    def _extract_action_sequence_for_rl(self, interaction_data: InteractionData) -> List[Dict[str, Any]]:
        """為RL提取動作序列"""
        rl_actions = []
        
        for i, action in enumerate(interaction_data.action_sequence):
            rl_action = {
                'step_id': i,
                'action_type': action.get('type', 'unknown'),
                'parameters': action.get('parameters', {}),
                'execution_time': action.get('execution_time', 0),
                'success': action.get('success', True),
                'immediate_reward': 1.0 if action.get('success', True) else -0.5
            }
            rl_actions.append(rl_action)
        
        return rl_actions
    
    def _calculate_reward_signals(self, patterns: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, float]:
        """計算獎勵信號"""
        outcome_features = features.get('outcome_features', {})
        
        rewards = {
            'completion_reward': 1.0 if outcome_features.get('overall_success', False) else 0.0,
            'efficiency_reward': outcome_features.get('resource_efficiency', 0.5),
            'satisfaction_reward': outcome_features.get('user_satisfaction', 0.5),
            'time_reward': max(0.0, 1.0 - outcome_features.get('completion_time', 60) / 300),  # 5分鐘為基準
            'error_penalty': -0.1 * outcome_features.get('error_count', 0)
        }
        
        # 計算總獎勵
        rewards['total_reward'] = sum(rewards.values())
        
        return rewards
    
    def _extract_state_transitions(self, interaction_data: InteractionData) -> List[Dict[str, Any]]:
        """提取狀態轉換"""
        transitions = []
        
        for i in range(len(interaction_data.action_sequence) - 1):
            current_action = interaction_data.action_sequence[i]
            next_action = interaction_data.action_sequence[i + 1]
            
            transition = {
                'from_state': {
                    'action_type': current_action.get('type'),
                    'success': current_action.get('success', True)
                },
                'action': current_action.get('type'),
                'to_state': {
                    'action_type': next_action.get('type'),
                    'context': 'transition'
                },
                'reward': 1.0 if current_action.get('success', True) else -0.5
            }
            transitions.append(transition)
        
        return transitions
    
    def _update_statistics(self, interaction_data: InteractionData, 
                          patterns: Dict[str, Any], 
                          templates: Dict[str, List[WorkflowTemplate]]):
        """更新統計信息"""
        self.statistics['total_interactions'] += 1
        
        if interaction_data.outcomes.get('overall_success', False):
            self.statistics['successful_interactions'] += 1
        
        self.statistics['patterns_discovered'] += sum(len(pattern_list) for pattern_list in patterns.values())
        self.statistics['templates_generated'] += sum(len(template_list) for template_list in templates.values())
    
    def _save_processing_results(self, interaction_data: InteractionData,
                               features: Dict[str, Any],
                               patterns: Dict[str, Any],
                               templates: Dict[str, List[WorkflowTemplate]]):
        """保存處理結果"""
        try:
            # 創建保存目錄
            session_dir = self.data_dir / "sessions" / interaction_data.session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存標準化數據
            with open(session_dir / "interaction_data.json", 'w', encoding='utf-8') as f:
                json.dump(asdict(interaction_data), f, ensure_ascii=False, indent=2, default=str)
            
            # 保存特徵
            with open(session_dir / "features.json", 'w', encoding='utf-8') as f:
                json.dump(features, f, ensure_ascii=False, indent=2)
            
            # 保存模式
            with open(session_dir / "patterns.json", 'w', encoding='utf-8') as f:
                json.dump(patterns, f, ensure_ascii=False, indent=2)
            
            # 保存統計信息
            with open(self.data_dir / "statistics.json", 'w', encoding='utf-8') as f:
                json.dump(self.statistics, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"處理結果已保存到 {session_dir}")
            
        except Exception as e:
            self.logger.error(f"保存處理結果失敗: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return self.statistics.copy()
    
    def find_similar_interactions(self, context: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """找到相似的交互"""
        # 簡化實現：基於任務類型匹配
        similar_interactions = []
        
        target_task_type = context.get('task_type', 'unknown')
        
        # 搜索會話目錄
        sessions_dir = self.data_dir / "sessions"
        if sessions_dir.exists():
            for session_dir in sessions_dir.iterdir():
                if session_dir.is_dir():
                    interaction_file = session_dir / "interaction_data.json"
                    if interaction_file.exists():
                        try:
                            with open(interaction_file, 'r', encoding='utf-8') as f:
                                interaction_data = json.load(f)
                            
                            # 檢查任務類型匹配
                            if interaction_data.get('context', {}).get('task_type') == target_task_type:
                                similar_interactions.append({
                                    'session_id': interaction_data.get('session_id'),
                                    'interaction_data': interaction_data,
                                    'similarity_score': 0.8  # 簡化的相似度分數
                                })
                                
                                if len(similar_interactions) >= limit:
                                    break
                                    
                        except Exception as e:
                            self.logger.error(f"讀取交互數據失敗 {interaction_file}: {e}")
        
        return similar_interactions
    
    def get_workflow_recommendations(self, context: Dict[str, Any]) -> List[WorkflowTemplate]:
        """獲取工作流推薦"""
        return self.workflow_templates.find_matching_templates(context)

# 導出主要類
__all__ = [
    'EnhancedInteractionLogManager',
    'InteractionData',
    'WorkflowTemplate',
    'InteractionType',
    'PatternType'
]

if __name__ == "__main__":
    # 測試Enhanced Interaction Log Manager
    manager = EnhancedInteractionLogManager()
    
    # 測試數據
    test_replay_data = {
        'session_id': 'test_session_001',
        'description': 'SmartUI診斷和修復',
        'steps': [
            {
                'action': 'execute_command',
                'parameters': {'command': 'ps aux | grep smartui'},
                'result': {'output': 'smartui process found'},
                'success': True,
                'execution_time': 2.5
            },
            {
                'action': 'check_port',
                'parameters': {'port': 8000},
                'result': {'status': 'listening'},
                'success': True,
                'execution_time': 1.2
            },
            {
                'action': 'access_interface',
                'parameters': {'url': 'http://localhost:8000'},
                'result': {'status_code': 200},
                'success': True,
                'execution_time': 3.1
            }
        ],
        'success': True,
        'completion_time': 6.8,
        'user_satisfaction': 0.9
    }
    
    # 處理測試數據
    result = manager.process_replay_data(test_replay_data)
    
    print("處理結果:")
    print(f"會話ID: {result.get('session_id')}")
    print(f"發現模式: {len(result.get('patterns', {}))}")
    print(f"生成模板: {sum(len(templates) for templates in result.get('templates', {}).values())}")
    print(f"統計信息: {result.get('statistics')}")

