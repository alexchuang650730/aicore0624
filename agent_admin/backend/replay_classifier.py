# -*- coding: utf-8 -*-
"""
Replay Classifier and RL SRT Integrator - Replay分類器和RL SRT整合器

將Manus Replay數據分類並整合到RL SRT學習系統中
實現從replay操作到智能學習的完整數據流

作者: Agentic Agent Team
版本: 1.0.0
日期: 2025-06-22
"""

import os
import sys
import json
import logging
import asyncio
import requests
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import re
from urllib.parse import urlparse, parse_qs
import numpy as np
from collections import defaultdict, Counter

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("replay_classifier")

class ReplayCategory(Enum):
    """Replay分類枚舉"""
    HIGH_QUALITY_SUCCESS = "high_quality_success"
    MODERATE_SUCCESS = "moderate_success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE_CASE = "failure_case"
    OPTIMIZATION_OPPORTUNITY = "optimization_opportunity"

class PatternType(Enum):
    """模式類型枚舉"""
    SUCCESS_PATTERN = "success_pattern"
    FAILURE_PATTERN = "failure_pattern"
    EFFICIENCY_PATTERN = "efficiency_pattern"
    ERROR_RECOVERY_PATTERN = "error_recovery_pattern"
    OPTIMIZATION_PATTERN = "optimization_pattern"

class LearningValueLevel(Enum):
    """學習價值等級枚舉"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"

@dataclass
class ReplayOperation:
    """Replay操作"""
    timestamp: str
    action_type: str
    target: str
    value: Optional[str] = None
    success: bool = True
    duration: float = 0.0
    context: Dict[str, Any] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class ReplayClassification:
    """Replay分類結果"""
    primary_category: ReplayCategory
    success_rate: float
    efficiency_score: float
    learning_value: LearningValueLevel
    total_operations: int
    successful_operations: int
    identified_patterns: List[PatternType]
    quality_metrics: Dict[str, float]

@dataclass
class LearningPattern:
    """學習模式"""
    pattern_type: PatternType
    pattern_description: str
    operations_involved: List[int]
    confidence_score: float
    learning_value: float
    recommendations: List[str]

class ReplayDataParser:
    """Replay數據解析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ReplayDataParser")
    
    def parse_manus_replay(self, replay_url: str) -> Dict[str, Any]:
        """解析Manus replay數據"""
        try:
            self.logger.info(f"開始解析Manus replay: {replay_url}")
            
            # 提取replay ID
            replay_id = self._extract_replay_id(replay_url)
            
            # 模擬從Manus API獲取replay數據
            # 實際實現中需要調用Manus API
            replay_data = self._fetch_replay_data(replay_id)
            
            # 解析操作序列
            operations = self._parse_operations(replay_data)
            
            # 提取上下文信息
            context = self._extract_context(replay_data)
            
            # 分析操作模式
            patterns = self._analyze_operation_patterns(operations)
            
            result = {
                'replay_id': replay_id,
                'replay_url': replay_url,
                'operations': operations,
                'context': context,
                'patterns': patterns,
                'metadata': self._extract_metadata(replay_data),
                'parsed_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"Replay解析完成: {len(operations)} 個操作")
            return result
            
        except Exception as e:
            self.logger.error(f"解析Manus replay失敗: {e}")
            return {}
    
    def _extract_replay_id(self, replay_url: str) -> str:
        """從URL提取replay ID"""
        try:
            # 解析URL: https://manus.im/share/4Zn26HUNIGO0Ot0bTpUDGI?replay=1
            parsed_url = urlparse(replay_url)
            path_parts = parsed_url.path.split('/')
            
            if len(path_parts) >= 3 and path_parts[1] == 'share':
                return path_parts[2]
            
            return hashlib.md5(replay_url.encode()).hexdigest()[:16]
            
        except Exception as e:
            self.logger.error(f"提取replay ID失敗: {e}")
            return "unknown_replay"
    
    def _fetch_replay_data(self, replay_id: str) -> Dict[str, Any]:
        """獲取replay數據"""
        # 這裡應該調用實際的Manus API
        # 目前返回模擬數據
        
        sample_replay_data = {
            'id': replay_id,
            'title': 'Form Filling Demo',
            'description': 'Automated form filling workflow',
            'duration': 45.5,
            'created_at': '2025-06-22T10:30:00Z',
            'steps': [
                {
                    'timestamp': '2025-06-22T10:30:00Z',
                    'action': 'navigate',
                    'target': 'https://example.com/form',
                    'success': True,
                    'duration': 2.1,
                    'screenshot': 'step_001.png'
                },
                {
                    'timestamp': '2025-06-22T10:30:02Z',
                    'action': 'click',
                    'target': 'input[name="email"]',
                    'success': True,
                    'duration': 0.5,
                    'screenshot': 'step_002.png'
                },
                {
                    'timestamp': '2025-06-22T10:30:03Z',
                    'action': 'type',
                    'target': 'input[name="email"]',
                    'value': 'user@example.com',
                    'success': True,
                    'duration': 1.2,
                    'screenshot': 'step_003.png'
                },
                {
                    'timestamp': '2025-06-22T10:30:04Z',
                    'action': 'click',
                    'target': 'input[name="password"]',
                    'success': True,
                    'duration': 0.3,
                    'screenshot': 'step_004.png'
                },
                {
                    'timestamp': '2025-06-22T10:30:05Z',
                    'action': 'type',
                    'target': 'input[name="password"]',
                    'value': '********',
                    'success': True,
                    'duration': 0.8,
                    'screenshot': 'step_005.png'
                },
                {
                    'timestamp': '2025-06-22T10:30:06Z',
                    'action': 'click',
                    'target': 'button[type="submit"]',
                    'success': True,
                    'duration': 0.4,
                    'screenshot': 'step_006.png'
                },
                {
                    'timestamp': '2025-06-22T10:30:08Z',
                    'action': 'wait',
                    'target': '.success-message',
                    'success': True,
                    'duration': 1.5,
                    'screenshot': 'step_007.png'
                }
            ],
            'metadata': {
                'browser': 'chrome',
                'viewport': {'width': 1920, 'height': 1080},
                'user_agent': 'Mozilla/5.0...',
                'final_url': 'https://example.com/dashboard'
            }
        }
        
        return sample_replay_data
    
    def _parse_operations(self, replay_data: Dict[str, Any]) -> List[ReplayOperation]:
        """解析操作序列"""
        operations = []
        
        for step in replay_data.get('steps', []):
            operation = ReplayOperation(
                timestamp=step.get('timestamp', ''),
                action_type=step.get('action', 'unknown'),
                target=step.get('target', ''),
                value=step.get('value'),
                success=step.get('success', True),
                duration=step.get('duration', 0.0),
                context={
                    'screenshot': step.get('screenshot'),
                    'step_index': len(operations),
                    'page_context': replay_data.get('metadata', {})
                },
                error_message=step.get('error')
            )
            operations.append(operation)
        
        return operations
    
    def _extract_context(self, replay_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取上下文信息"""
        metadata = replay_data.get('metadata', {})
        
        context = {
            'replay_title': replay_data.get('title', 'Unknown'),
            'replay_description': replay_data.get('description', ''),
            'total_duration': replay_data.get('duration', 0.0),
            'browser_info': {
                'browser': metadata.get('browser', 'unknown'),
                'viewport': metadata.get('viewport', {}),
                'user_agent': metadata.get('user_agent', '')
            },
            'navigation_info': {
                'start_url': self._extract_start_url(replay_data),
                'final_url': metadata.get('final_url', ''),
                'domain': self._extract_domain(replay_data)
            },
            'task_indicators': self._identify_task_indicators(replay_data)
        }
        
        return context
    
    def _analyze_operation_patterns(self, operations: List[ReplayOperation]) -> Dict[str, Any]:
        """分析操作模式"""
        patterns = {
            'action_sequence': [op.action_type for op in operations],
            'timing_analysis': self._analyze_timing(operations),
            'success_pattern': self._analyze_success_pattern(operations),
            'target_analysis': self._analyze_targets(operations),
            'value_patterns': self._analyze_value_patterns(operations)
        }
        
        return patterns
    
    def _analyze_timing(self, operations: List[ReplayOperation]) -> Dict[str, Any]:
        """分析時間模式"""
        durations = [op.duration for op in operations]
        
        return {
            'total_duration': sum(durations),
            'average_duration': np.mean(durations) if durations else 0,
            'max_duration': max(durations) if durations else 0,
            'min_duration': min(durations) if durations else 0,
            'duration_variance': np.var(durations) if durations else 0,
            'slow_operations': [i for i, d in enumerate(durations) if d > 2.0]
        }
    
    def _analyze_success_pattern(self, operations: List[ReplayOperation]) -> Dict[str, Any]:
        """分析成功模式"""
        total_ops = len(operations)
        successful_ops = sum(1 for op in operations if op.success)
        
        return {
            'total_operations': total_ops,
            'successful_operations': successful_ops,
            'success_rate': successful_ops / total_ops if total_ops > 0 else 0,
            'failed_operations': [i for i, op in enumerate(operations) if not op.success],
            'consecutive_successes': self._find_consecutive_successes(operations)
        }
    
    def _analyze_targets(self, operations: List[ReplayOperation]) -> Dict[str, Any]:
        """分析目標元素"""
        targets = [op.target for op in operations if op.target]
        target_types = self._classify_targets(targets)
        
        return {
            'unique_targets': len(set(targets)),
            'target_types': target_types,
            'most_common_targets': Counter(targets).most_common(5),
            'selector_complexity': self._assess_selector_complexity(targets)
        }
    
    def _analyze_value_patterns(self, operations: List[ReplayOperation]) -> Dict[str, Any]:
        """分析輸入值模式"""
        values = [op.value for op in operations if op.value]
        
        return {
            'total_inputs': len(values),
            'input_types': self._classify_input_types(values),
            'average_input_length': np.mean([len(v) for v in values]) if values else 0,
            'sensitive_data_indicators': self._detect_sensitive_data(values)
        }

class IntelligentReplayClassifier:
    """智能Replay分類器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.IntelligentReplayClassifier")
        
        # 分類規則配置
        self.classification_thresholds = {
            'high_quality_success': {'success_rate': 0.9, 'efficiency_score': 0.8},
            'moderate_success': {'success_rate': 0.8, 'efficiency_score': 0.6},
            'partial_success': {'success_rate': 0.5, 'efficiency_score': 0.4}
        }
        
        # 模式識別規則
        self.pattern_rules = {
            'efficiency_indicators': ['fast_execution', 'minimal_steps', 'direct_path'],
            'quality_indicators': ['stable_selectors', 'proper_waits', 'error_handling'],
            'optimization_indicators': ['redundant_steps', 'slow_operations', 'unnecessary_waits']
        }
    
    def classify_and_learn(self, replay_data: Dict[str, Any]) -> Dict[str, Any]:
        """分類並學習replay數據"""
        try:
            self.logger.info(f"開始分類replay: {replay_data.get('replay_id', 'unknown')}")
            
            # 1. 基礎分類
            basic_classification = self._perform_basic_classification(replay_data)
            
            # 2. 模式識別
            identified_patterns = self._identify_learning_patterns(replay_data)
            
            # 3. 學習價值評估
            learning_value = self._assess_learning_value(replay_data, identified_patterns)
            
            # 4. 質量指標計算
            quality_metrics = self._calculate_quality_metrics(replay_data)
            
            # 5. 生成學習樣本
            learning_samples = self._generate_learning_samples(
                replay_data, 
                basic_classification, 
                identified_patterns
            )
            
            # 6. 生成改進建議
            recommendations = self._generate_recommendations(
                basic_classification,
                identified_patterns,
                quality_metrics
            )
            
            result = {
                'classification': basic_classification,
                'patterns': identified_patterns,
                'learning_value': learning_value,
                'quality_metrics': quality_metrics,
                'learning_samples': learning_samples,
                'recommendations': recommendations,
                'classified_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"分類完成: {basic_classification.primary_category.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"分類replay失敗: {e}")
            return {}
    
    def _perform_basic_classification(self, replay_data: Dict[str, Any]) -> ReplayClassification:
        """執行基礎分類"""
        operations = replay_data.get('operations', [])
        patterns = replay_data.get('patterns', {})
        
        # 計算基礎指標
        total_ops = len(operations)
        successful_ops = sum(1 for op in operations if op.success)
        success_rate = successful_ops / total_ops if total_ops > 0 else 0
        
        # 計算效率分數
        timing_analysis = patterns.get('timing_analysis', {})
        avg_duration = timing_analysis.get('average_duration', 0)
        efficiency_score = self._calculate_efficiency_score(avg_duration, total_ops)
        
        # 確定主要分類
        primary_category = self._determine_primary_category(success_rate, efficiency_score)
        
        # 評估學習價值
        learning_value = self._determine_learning_value(success_rate, efficiency_score, total_ops)
        
        # 識別模式類型
        identified_patterns = self._identify_pattern_types(replay_data)
        
        # 計算質量指標
        quality_metrics = self._calculate_basic_quality_metrics(replay_data)
        
        classification = ReplayClassification(
            primary_category=primary_category,
            success_rate=success_rate,
            efficiency_score=efficiency_score,
            learning_value=learning_value,
            total_operations=total_ops,
            successful_operations=successful_ops,
            identified_patterns=identified_patterns,
            quality_metrics=quality_metrics
        )
        
        return classification
    
    def _calculate_efficiency_score(self, avg_duration: float, total_ops: int) -> float:
        """計算效率分數"""
        # 基於平均執行時間和操作數量計算效率
        if avg_duration <= 1.0:
            time_score = 1.0
        elif avg_duration <= 2.0:
            time_score = 0.8
        elif avg_duration <= 3.0:
            time_score = 0.6
        else:
            time_score = 0.4
        
        # 基於操作數量調整（更少的操作通常更高效）
        if total_ops <= 5:
            ops_score = 1.0
        elif total_ops <= 10:
            ops_score = 0.8
        elif total_ops <= 20:
            ops_score = 0.6
        else:
            ops_score = 0.4
        
        return (time_score + ops_score) / 2
    
    def _determine_primary_category(self, success_rate: float, efficiency_score: float) -> ReplayCategory:
        """確定主要分類"""
        thresholds = self.classification_thresholds
        
        if (success_rate >= thresholds['high_quality_success']['success_rate'] and 
            efficiency_score >= thresholds['high_quality_success']['efficiency_score']):
            return ReplayCategory.HIGH_QUALITY_SUCCESS
        elif (success_rate >= thresholds['moderate_success']['success_rate'] and 
              efficiency_score >= thresholds['moderate_success']['efficiency_score']):
            return ReplayCategory.MODERATE_SUCCESS
        elif (success_rate >= thresholds['partial_success']['success_rate'] and 
              efficiency_score >= thresholds['partial_success']['efficiency_score']):
            return ReplayCategory.PARTIAL_SUCCESS
        else:
            return ReplayCategory.FAILURE_CASE
    
    def _determine_learning_value(self, success_rate: float, efficiency_score: float, total_ops: int) -> LearningValueLevel:
        """確定學習價值等級"""
        # 綜合考慮成功率、效率和操作數量
        value_score = (success_rate * 0.4 + efficiency_score * 0.4 + min(total_ops / 10, 1.0) * 0.2)
        
        if value_score >= 0.8:
            return LearningValueLevel.HIGH
        elif value_score >= 0.6:
            return LearningValueLevel.MEDIUM
        elif value_score >= 0.4:
            return LearningValueLevel.LOW
        else:
            return LearningValueLevel.MINIMAL
    
    def _identify_pattern_types(self, replay_data: Dict[str, Any]) -> List[PatternType]:
        """識別模式類型"""
        patterns = []
        operations = replay_data.get('operations', [])
        
        # 檢查成功模式
        success_rate = sum(1 for op in operations if op.success) / len(operations) if operations else 0
        if success_rate >= 0.8:
            patterns.append(PatternType.SUCCESS_PATTERN)
        
        # 檢查失敗模式
        if success_rate < 0.6:
            patterns.append(PatternType.FAILURE_PATTERN)
        
        # 檢查效率模式
        timing_analysis = replay_data.get('patterns', {}).get('timing_analysis', {})
        avg_duration = timing_analysis.get('average_duration', 0)
        if avg_duration <= 1.5:
            patterns.append(PatternType.EFFICIENCY_PATTERN)
        
        # 檢查錯誤恢復模式
        failed_ops = [op for op in operations if not op.success]
        if failed_ops and success_rate >= 0.7:  # 有失敗但整體成功率還不錯
            patterns.append(PatternType.ERROR_RECOVERY_PATTERN)
        
        # 檢查優化模式
        slow_operations = timing_analysis.get('slow_operations', [])
        if slow_operations:
            patterns.append(PatternType.OPTIMIZATION_PATTERN)
        
        return patterns
    
    def _identify_learning_patterns(self, replay_data: Dict[str, Any]) -> List[LearningPattern]:
        """識別學習模式"""
        learning_patterns = []
        operations = replay_data.get('operations', [])
        
        # 識別高效操作序列
        efficient_sequences = self._find_efficient_sequences(operations)
        for seq in efficient_sequences:
            pattern = LearningPattern(
                pattern_type=PatternType.EFFICIENCY_PATTERN,
                pattern_description=f"高效操作序列: {' → '.join([operations[i].action_type for i in seq])}",
                operations_involved=seq,
                confidence_score=0.8,
                learning_value=0.9,
                recommendations=["保持這種高效的操作順序", "可以作為最佳實踐模板"]
            )
            learning_patterns.append(pattern)
        
        # 識別錯誤模式
        error_patterns = self._find_error_patterns(operations)
        for error_pattern in error_patterns:
            pattern = LearningPattern(
                pattern_type=PatternType.FAILURE_PATTERN,
                pattern_description=f"錯誤模式: {error_pattern['description']}",
                operations_involved=error_pattern['operations'],
                confidence_score=0.7,
                learning_value=0.8,
                recommendations=error_pattern['recommendations']
            )
            learning_patterns.append(pattern)
        
        # 識別優化機會
        optimization_opportunities = self._find_optimization_opportunities(operations)
        for opp in optimization_opportunities:
            pattern = LearningPattern(
                pattern_type=PatternType.OPTIMIZATION_PATTERN,
                pattern_description=f"優化機會: {opp['description']}",
                operations_involved=opp['operations'],
                confidence_score=0.6,
                learning_value=0.7,
                recommendations=opp['recommendations']
            )
            learning_patterns.append(pattern)
        
        return learning_patterns
    
    def _generate_learning_samples(self, replay_data: Dict[str, Any], 
                                 classification: ReplayClassification,
                                 patterns: List[LearningPattern]) -> List[Dict[str, Any]]:
        """生成學習樣本"""
        learning_samples = []
        
        # 根據分類生成不同類型的學習樣本
        if classification.primary_category == ReplayCategory.HIGH_QUALITY_SUCCESS:
            sample = self._create_positive_learning_sample(replay_data, classification, patterns)
            learning_samples.append(sample)
        
        elif classification.primary_category == ReplayCategory.FAILURE_CASE:
            sample = self._create_negative_learning_sample(replay_data, classification, patterns)
            learning_samples.append(sample)
        
        # 為每個識別的模式生成專門的學習樣本
        for pattern in patterns:
            if pattern.learning_value >= 0.7:
                sample = self._create_pattern_learning_sample(replay_data, pattern)
                learning_samples.append(sample)
        
        return learning_samples
    
    def _create_positive_learning_sample(self, replay_data: Dict[str, Any],
                                       classification: ReplayClassification,
                                       patterns: List[LearningPattern]) -> Dict[str, Any]:
        """創建正面學習樣本"""
        return {
            'type': 'positive_example',
            'category': classification.primary_category.value,
            'learning_focus': 'success_pattern_reinforcement',
            'key_insights': [
                f"高成功率操作序列 ({classification.success_rate:.1%})",
                f"高效執行模式 (效率分數: {classification.efficiency_score:.2f})",
                "可作為最佳實踐模板"
            ],
            'recommended_actions': [
                "將此操作序列加入成功模式庫",
                "在相似場景中優先推薦此模式",
                "分析成功因素並應用到其他場景"
            ],
            'confidence_level': 'high',
            'learning_weight': 1.0
        }
    
    def _create_negative_learning_sample(self, replay_data: Dict[str, Any],
                                       classification: ReplayClassification,
                                       patterns: List[LearningPattern]) -> Dict[str, Any]:
        """創建負面學習樣本"""
        return {
            'type': 'negative_example',
            'category': classification.primary_category.value,
            'learning_focus': 'failure_pattern_avoidance',
            'key_insights': [
                f"低成功率警示 ({classification.success_rate:.1%})",
                f"效率問題識別 (效率分數: {classification.efficiency_score:.2f})",
                "需要避免的操作模式"
            ],
            'recommended_actions': [
                "將此模式加入失敗模式庫",
                "在推薦時避免類似操作序列",
                "分析失敗原因並提供替代方案"
            ],
            'confidence_level': 'medium',
            'learning_weight': 0.8
        }

class ReplayRLSRTIntegrator:
    """Replay RL SRT整合器"""
    
    def __init__(self, rl_srt_adapter):
        self.rl_srt_adapter = rl_srt_adapter
        self.replay_classifier = IntelligentReplayClassifier()
        self.replay_parser = ReplayDataParser()
        self.logger = logging.getLogger(f"{__name__}.ReplayRLSRTIntegrator")
    
    def process_replay_for_learning(self, replay_input: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """處理replay數據用於RL SRT學習"""
        try:
            self.logger.info("開始處理replay數據進行學習")
            
            # 1. 解析replay數據
            if isinstance(replay_input, str):
                replay_data = self.replay_parser.parse_manus_replay(replay_input)
            else:
                replay_data = replay_input
            
            if not replay_data:
                raise ValueError("無法解析replay數據")
            
            # 2. 分類和模式識別
            classification_result = self.replay_classifier.classify_and_learn(replay_data)
            
            # 3. 轉換為RL SRT訓練格式
            training_data_list = self._convert_to_rl_training_format(
                replay_data, 
                classification_result
            )
            
            # 4. 批量學習
            learning_results = []
            for training_data in training_data_list:
                try:
                    result = self.rl_srt_adapter.process_training_data(training_data)
                    learning_results.append(result)
                except Exception as e:
                    self.logger.error(f"RL SRT學習失敗: {e}")
                    learning_results.append({'error': str(e)})
            
            # 5. 生成學習報告
            learning_report = self._generate_learning_report(
                replay_data, 
                classification_result, 
                learning_results
            )
            
            self.logger.info("Replay學習處理完成")
            return learning_report
            
        except Exception as e:
            self.logger.error(f"處理replay學習失敗: {e}")
            return {'error': str(e)}
    
    def _convert_to_rl_training_format(self, replay_data: Dict[str, Any], 
                                     classification_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """轉換為RL SRT訓練格式"""
        training_data_list = []
        
        try:
            operations = replay_data.get('operations', [])
            classification = classification_result.get('classification', {})
            
            # 為每個學習樣本生成訓練數據
            for learning_sample in classification_result.get('learning_samples', []):
                
                # 構建上下文狀態
                context_state = {
                    'task_type': self._infer_task_type(replay_data),
                    'environment_type': 'web_browser',
                    'available_tools': len(set(op.action_type for op in operations)),
                    'user_intent_clarity': self._map_learning_value_to_clarity(
                        classification.get('learning_value', 'medium')
                    ),
                    'initial_complexity': self._assess_complexity(replay_data)
                }
                
                # 構建動作序列
                action_sequence = []
                for i, operation in enumerate(operations):
                    action = {
                        'step_id': i,
                        'action_type': operation.action_type,
                        'parameters': {
                            'target': operation.target,
                            'value': operation.value,
                            'duration': operation.duration
                        },
                        'execution_time': operation.duration,
                        'success': operation.success,
                        'immediate_reward': 1.0 if operation.success else 0.0,
                        'metadata': operation.context
                    }
                    action_sequence.append(action)
                
                # 計算獎勵信號
                reward_signals = self._calculate_replay_rewards(
                    classification,
                    classification_result.get('patterns', []),
                    learning_sample
                )
                
                # 構建訓練數據
                training_data = {
                    'session_id': f"replay_{replay_data.get('replay_id', 'unknown')}_{len(training_data_list)}",
                    'data_source': 'manus_replay',
                    'context_state': context_state,
                    'action_sequence': action_sequence,
                    'reward_signals': reward_signals,
                    'metadata': {
                        'replay_id': replay_data.get('replay_id'),
                        'replay_url': replay_data.get('replay_url'),
                        'classification': classification,
                        'learning_sample': learning_sample,
                        'patterns': classification_result.get('patterns', [])
                    },
                    'generated_at': datetime.now().isoformat()
                }
                
                training_data_list.append(training_data)
            
            return training_data_list
            
        except Exception as e:
            self.logger.error(f"轉換RL訓練格式失敗: {e}")
            return []
    
    def _calculate_replay_rewards(self, classification: Dict[str, Any],
                                patterns: List[Dict[str, Any]],
                                learning_sample: Dict[str, Any]) -> Dict[str, float]:
        """基於replay分類計算獎勵信號"""
        
        # 基礎獎勵
        completion_reward = classification.get('success_rate', 0.0)
        efficiency_reward = classification.get('efficiency_score', 0.5)
        
        # 學習樣本類型調整
        sample_type = learning_sample.get('type', 'general')
        if sample_type == 'positive_example':
            learning_bonus = 0.3
        elif sample_type == 'negative_example':
            learning_bonus = -0.2
        else:
            learning_bonus = 0.0
        
        # 模式質量獎勵
        pattern_quality = 0.5
        high_value_patterns = [p for p in patterns if p.get('learning_value', 0) >= 0.7]
        if high_value_patterns:
            pattern_quality += len(high_value_patterns) * 0.1
        
        # 學習價值獎勵
        learning_value_map = {
            'high': 1.0,
            'medium': 0.7,
            'low': 0.4,
            'minimal': 0.1
        }
        learning_value_reward = learning_value_map.get(
            classification.get('learning_value', 'medium'), 0.5
        )
        
        # 時間獎勵（基於效率）
        time_reward = efficiency_reward
        
        # 錯誤懲罰
        error_penalty = max(0, (1.0 - completion_reward) * 0.3)
        
        # 總獎勵計算
        total_reward = (
            completion_reward * 0.3 +
            efficiency_reward * 0.25 +
            learning_value_reward * 0.25 +
            pattern_quality * 0.1 +
            time_reward * 0.1 +
            learning_bonus -
            error_penalty
        )
        
        return {
            'completion_reward': completion_reward,
            'efficiency_reward': efficiency_reward,
            'satisfaction_reward': learning_value_reward,
            'time_reward': time_reward,
            'error_penalty': error_penalty,
            'learning_bonus': learning_bonus,
            'total_reward': max(total_reward, 0.0)
        }
    
    def _generate_learning_report(self, replay_data: Dict[str, Any],
                                classification_result: Dict[str, Any],
                                learning_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成學習報告"""
        
        classification = classification_result.get('classification', {})
        patterns = classification_result.get('patterns', [])
        
        # 統計學習結果
        successful_learning = [r for r in learning_results if 'error' not in r]
        failed_learning = [r for r in learning_results if 'error' in r]
        
        # 提取學習洞察
        learning_insights = []
        for result in successful_learning:
            insights = result.get('learned_patterns', {}).get('insights', {})
            if insights:
                learning_insights.append(insights)
        
        report = {
            'replay_info': {
                'replay_id': replay_data.get('replay_id'),
                'replay_url': replay_data.get('replay_url'),
                'total_operations': len(replay_data.get('operations', [])),
                'replay_duration': replay_data.get('context', {}).get('total_duration', 0)
            },
            'classification_summary': {
                'primary_category': classification.get('primary_category', 'unknown'),
                'success_rate': classification.get('success_rate', 0),
                'efficiency_score': classification.get('efficiency_score', 0),
                'learning_value': classification.get('learning_value', 'unknown'),
                'identified_patterns': [p.get('pattern_type', 'unknown') for p in patterns]
            },
            'learning_results': {
                'total_samples_processed': len(learning_results),
                'successful_learning_sessions': len(successful_learning),
                'failed_learning_sessions': len(failed_learning),
                'learning_insights': learning_insights,
                'generated_strategies': len([r for r in successful_learning if r.get('optimized_strategies')])
            },
            'recommendations': classification_result.get('recommendations', []),
            'next_steps': self._generate_next_steps(classification_result, learning_results),
            'generated_at': datetime.now().isoformat()
        }
        
        return report
    
    def _infer_task_type(self, replay_data: Dict[str, Any]) -> str:
        """推斷任務類型"""
        operations = replay_data.get('operations', [])
        action_types = [op.action_type for op in operations]
        
        # 基於動作類型推斷任務
        if 'type' in action_types and 'click' in action_types:
            return 'form_filling'
        elif 'navigate' in action_types and len(set(action_types)) <= 3:
            return 'navigation'
        elif 'wait' in action_types and 'click' in action_types:
            return 'automation'
        else:
            return 'general_interaction'
    
    def _assess_complexity(self, replay_data: Dict[str, Any]) -> str:
        """評估複雜度"""
        operations = replay_data.get('operations', [])
        unique_actions = len(set(op.action_type for op in operations))
        total_operations = len(operations)
        
        if total_operations <= 5 and unique_actions <= 3:
            return 'simple'
        elif total_operations <= 15 and unique_actions <= 6:
            return 'medium'
        else:
            return 'complex'
    
    def _map_learning_value_to_clarity(self, learning_value: str) -> float:
        """將學習價值映射為意圖清晰度"""
        mapping = {
            'high': 0.9,
            'medium': 0.7,
            'low': 0.5,
            'minimal': 0.3
        }
        return mapping.get(learning_value, 0.5)
    
    def _generate_next_steps(self, classification_result: Dict[str, Any],
                           learning_results: List[Dict[str, Any]]) -> List[str]:
        """生成下一步建議"""
        next_steps = []
        
        classification = classification_result.get('classification', {})
        category = classification.get('primary_category', 'unknown')
        
        if category == 'high_quality_success':
            next_steps.extend([
                "將此replay模式加入最佳實踐庫",
                "在相似場景中優先推薦此操作序列",
                "分析成功因素並應用到其他任務"
            ])
        elif category == 'failure_case':
            next_steps.extend([
                "分析失敗原因並記錄到錯誤模式庫",
                "開發針對此類問題的預防策略",
                "尋找替代的成功操作序列"
            ])
        
        # 基於學習結果添加建議
        successful_learning = [r for r in learning_results if 'error' not in r]
        if successful_learning:
            next_steps.append("監控新學習策略的實際應用效果")
        
        if not next_steps:
            next_steps.append("繼續收集更多replay數據以改進學習效果")
        
        return next_steps

# 導出主要類
__all__ = [
    'ReplayDataParser',
    'IntelligentReplayClassifier', 
    'ReplayRLSRTIntegrator',
    'ReplayOperation',
    'ReplayClassification',
    'LearningPattern',
    'ReplayCategory',
    'PatternType',
    'LearningValueLevel'
]

if __name__ == "__main__":
    # 測試Replay分類和RL SRT整合
    async def test_replay_integration():
        # 模擬RL SRT適配器
        class MockRLSRTAdapter:
            def process_training_data(self, training_data):
                return {
                    'session_id': training_data.get('session_id'),
                    'learned_patterns': {'insights': {'test': 'success'}},
                    'optimized_strategies': {'pattern_key': 'test_pattern'}
                }
        
        # 創建整合器
        mock_adapter = MockRLSRTAdapter()
        integrator = ReplayRLSRTIntegrator(mock_adapter)
        
        # 測試replay URL處理
        test_replay_url = "https://manus.im/share/4Zn26HUNIGO0Ot0bTpUDGI?replay=1"
        
        print("開始測試Replay整合...")
        learning_report = integrator.process_replay_for_learning(test_replay_url)
        
        print("\n學習報告:")
        print(f"Replay ID: {learning_report.get('replay_info', {}).get('replay_id')}")
        print(f"分類結果: {learning_report.get('classification_summary', {}).get('primary_category')}")
        print(f"成功率: {learning_report.get('classification_summary', {}).get('success_rate', 0):.1%}")
        print(f"學習會話數: {learning_report.get('learning_results', {}).get('total_samples_processed', 0)}")
        print(f"成功學習數: {learning_report.get('learning_results', {}).get('successful_learning_sessions', 0)}")
        
        recommendations = learning_report.get('recommendations', [])
        if recommendations:
            print(f"\n改進建議:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"{i}. {rec}")
        
        next_steps = learning_report.get('next_steps', [])
        if next_steps:
            print(f"\n下一步行動:")
            for i, step in enumerate(next_steps[:3], 1):
                print(f"{i}. {step}")
    
    # 運行測試
    asyncio.run(test_replay_integration())

