# -*- coding: utf-8 -*-
"""
Simplified RL SRT MCP Adapter - 簡化的強化學習自我獎勵訓練適配器

專注於實用的模式學習和策略優化，而非複雜的強化學習算法
與Enhanced Interaction Log Manager協同工作

作者: Agentic Agent Team
版本: 2.0.0 (簡化版)
日期: 2025-06-22
"""

import os
import sys
import json
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
from collections import defaultdict, deque

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simplified_rl_srt_adapter")

class StrategyType(Enum):
    """策略類型枚舉"""
    PATTERN_MATCHING = "pattern_matching"
    OPTIMIZATION = "optimization"
    ERROR_RECOVERY = "error_recovery"
    ADAPTIVE = "adaptive"

class LearningMode(Enum):
    """學習模式枚舉"""
    PATTERN_RECOGNITION = "pattern_recognition"
    STRATEGY_OPTIMIZATION = "strategy_optimization"
    FEEDBACK_LEARNING = "feedback_learning"
    CONTINUOUS_IMPROVEMENT = "continuous_improvement"

@dataclass
class ContextState:
    """上下文狀態"""
    task_type: str
    environment_type: str
    available_tools: int
    user_intent_clarity: float
    complexity: str
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class ActionRecommendation:
    """動作推薦"""
    recommended_action: Dict[str, Any]
    confidence_score: float
    reasoning: str
    alternative_actions: List[Dict[str, Any]]
    expected_outcome: Dict[str, Any]
    strategy_type: StrategyType
    learning_feedback: Dict[str, Any] = None

@dataclass
class LearningExperience:
    """學習經驗"""
    session_id: str
    context_state: ContextState
    action_taken: Dict[str, Any]
    outcome: Dict[str, Any]
    reward_score: float
    lessons_learned: List[str]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class PatternMatcher:
    """模式匹配器"""
    
    def __init__(self):
        self.patterns_db = defaultdict(list)
        self.similarity_threshold = 0.7
        self.logger = logging.getLogger(f"{__name__}.PatternMatcher")
    
    def learn_patterns(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """學習模式"""
        try:
            session_id = training_data.get('session_id', 'unknown')
            context_state = training_data.get('context_state', {})
            action_sequence = training_data.get('action_sequence', [])
            reward_signals = training_data.get('reward_signals', {})
            
            # 提取模式
            pattern = self._extract_pattern(context_state, action_sequence, reward_signals)
            
            # 存儲模式
            pattern_key = self._generate_pattern_key(context_state)
            self.patterns_db[pattern_key].append(pattern)
            
            # 分析模式洞察
            insights = self._analyze_pattern_insights(pattern_key)
            
            self.logger.info(f"學習模式完成: {session_id}, 模式鍵: {pattern_key}")
            
            return {
                'pattern_key': pattern_key,
                'pattern': pattern,
                'insights': insights,
                'total_patterns': len(self.patterns_db[pattern_key])
            }
            
        except Exception as e:
            self.logger.error(f"模式學習失敗: {e}")
            return {}
    
    def find_similar_contexts(self, current_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """找到相似上下文"""
        try:
            current_pattern_key = self._generate_pattern_key(current_context)
            similar_contexts = []
            
            # 精確匹配
            if current_pattern_key in self.patterns_db:
                for pattern in self.patterns_db[current_pattern_key]:
                    similar_contexts.append({
                        'context': pattern['context_state'],
                        'similarity_score': 1.0,
                        'match_type': 'exact',
                        'pattern': pattern
                    })
            
            # 模糊匹配
            for pattern_key, patterns in self.patterns_db.items():
                if pattern_key != current_pattern_key:
                    similarity = self._calculate_context_similarity(current_context, pattern_key)
                    if similarity >= self.similarity_threshold:
                        for pattern in patterns:
                            similar_contexts.append({
                                'context': pattern['context_state'],
                                'similarity_score': similarity,
                                'match_type': 'fuzzy',
                                'pattern': pattern
                            })
            
            # 按相似度排序
            similar_contexts.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return similar_contexts[:10]  # 返回前10個最相似的
            
        except Exception as e:
            self.logger.error(f"相似上下文查找失敗: {e}")
            return []
    
    def _extract_pattern(self, context_state: Dict[str, Any], 
                        action_sequence: List[Dict[str, Any]], 
                        reward_signals: Dict[str, float]) -> Dict[str, Any]:
        """提取模式"""
        return {
            'context_state': context_state,
            'action_sequence': action_sequence,
            'reward_signals': reward_signals,
            'success_rate': self._calculate_success_rate(action_sequence),
            'efficiency_score': reward_signals.get('efficiency_reward', 0.5),
            'total_reward': reward_signals.get('total_reward', 0.0),
            'action_pattern': ' -> '.join([action.get('action_type', 'unknown') for action in action_sequence]),
            'extracted_at': datetime.now().isoformat()
        }
    
    def _generate_pattern_key(self, context_state: Dict[str, Any]) -> str:
        """生成模式鍵"""
        task_type = context_state.get('task_type', 'unknown')
        complexity = context_state.get('complexity', 'medium')
        environment = context_state.get('environment_type', 'unknown')
        
        return f"{task_type}_{complexity}_{environment}"
    
    def _analyze_pattern_insights(self, pattern_key: str) -> Dict[str, Any]:
        """分析模式洞察"""
        patterns = self.patterns_db.get(pattern_key, [])
        
        if not patterns:
            return {}
        
        # 計算統計信息
        success_rates = [p['success_rate'] for p in patterns]
        efficiency_scores = [p['efficiency_score'] for p in patterns]
        total_rewards = [p['total_reward'] for p in patterns]
        
        insights = {
            'pattern_count': len(patterns),
            'average_success_rate': np.mean(success_rates),
            'average_efficiency': np.mean(efficiency_scores),
            'average_reward': np.mean(total_rewards),
            'best_pattern': max(patterns, key=lambda p: p['total_reward']),
            'most_common_actions': self._find_most_common_actions(patterns),
            'improvement_trend': self._calculate_improvement_trend(patterns)
        }
        
        return insights
    
    def _calculate_context_similarity(self, context1: Dict[str, Any], pattern_key: str) -> float:
        """計算上下文相似度"""
        # 簡化實現：基於任務類型和複雜度
        context1_key = self._generate_pattern_key(context1)
        
        # 分解模式鍵
        parts1 = context1_key.split('_')
        parts2 = pattern_key.split('_')
        
        if len(parts1) != 3 or len(parts2) != 3:
            return 0.0
        
        # 計算各部分相似度
        task_similarity = 1.0 if parts1[0] == parts2[0] else 0.0
        complexity_similarity = 1.0 if parts1[1] == parts2[1] else 0.5
        environment_similarity = 1.0 if parts1[2] == parts2[2] else 0.3
        
        # 加權平均
        similarity = (task_similarity * 0.5 + complexity_similarity * 0.3 + environment_similarity * 0.2)
        
        return similarity
    
    def _calculate_success_rate(self, action_sequence: List[Dict[str, Any]]) -> float:
        """計算成功率"""
        if not action_sequence:
            return 0.0
        
        successful_actions = sum(1 for action in action_sequence if action.get('success', True))
        return successful_actions / len(action_sequence)
    
    def _find_most_common_actions(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """找到最常見的動作"""
        action_counts = defaultdict(int)
        
        for pattern in patterns:
            for action in pattern['action_sequence']:
                action_type = action.get('action_type', 'unknown')
                action_counts[action_type] += 1
        
        # 按頻率排序
        sorted_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [action for action, count in sorted_actions[:5]]
    
    def _calculate_improvement_trend(self, patterns: List[Dict[str, Any]]) -> str:
        """計算改進趨勢"""
        if len(patterns) < 2:
            return 'insufficient_data'
        
        # 按時間排序
        sorted_patterns = sorted(patterns, key=lambda p: p['extracted_at'])
        
        # 計算最近和早期的平均獎勵
        half_point = len(sorted_patterns) // 2
        early_avg = np.mean([p['total_reward'] for p in sorted_patterns[:half_point]])
        recent_avg = np.mean([p['total_reward'] for p in sorted_patterns[half_point:]])
        
        if recent_avg > early_avg * 1.1:
            return 'improving'
        elif recent_avg < early_avg * 0.9:
            return 'declining'
        else:
            return 'stable'

class StrategyOptimizer:
    """策略優化器"""
    
    def __init__(self):
        self.strategies_db = defaultdict(list)
        self.optimization_history = deque(maxlen=1000)
        self.logger = logging.getLogger(f"{__name__}.StrategyOptimizer")
    
    def optimize(self, pattern_insights: Dict[str, Any]) -> Dict[str, Any]:
        """優化策略"""
        try:
            pattern_key = pattern_insights.get('pattern_key', 'unknown')
            insights = pattern_insights.get('insights', {})
            
            # 生成優化策略
            optimized_strategy = self._generate_optimized_strategy(pattern_key, insights)
            
            # 存儲策略
            self.strategies_db[pattern_key].append(optimized_strategy)
            
            # 記錄優化歷史
            self.optimization_history.append({
                'pattern_key': pattern_key,
                'strategy': optimized_strategy,
                'timestamp': datetime.now().isoformat()
            })
            
            self.logger.info(f"策略優化完成: {pattern_key}")
            
            return optimized_strategy
            
        except Exception as e:
            self.logger.error(f"策略優化失敗: {e}")
            return {}
    
    def get_best_strategy(self, similar_contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """獲取最佳策略"""
        try:
            if not similar_contexts:
                return self._get_default_strategy()
            
            # 選擇最相似的上下文
            best_context = similar_contexts[0]
            pattern = best_context.get('pattern', {})
            
            # 生成推薦策略
            strategy = {
                'action': self._recommend_action(pattern),
                'confidence': best_context.get('similarity_score', 0.5),
                'reasoning': self._generate_reasoning(pattern, best_context),
                'alternatives': self._generate_alternatives(pattern),
                'expected_outcome': self._predict_outcome(pattern),
                'strategy_type': self._determine_strategy_type(pattern)
            }
            
            return strategy
            
        except Exception as e:
            self.logger.error(f"獲取最佳策略失敗: {e}")
            return self._get_default_strategy()
    
    def _generate_optimized_strategy(self, pattern_key: str, insights: Dict[str, Any]) -> Dict[str, Any]:
        """生成優化策略"""
        best_pattern = insights.get('best_pattern', {})
        most_common_actions = insights.get('most_common_actions', [])
        average_success_rate = insights.get('average_success_rate', 0.5)
        
        strategy = {
            'pattern_key': pattern_key,
            'recommended_actions': most_common_actions,
            'success_probability': average_success_rate,
            'optimization_suggestions': self._generate_optimization_suggestions(insights),
            'risk_assessment': self._assess_risks(insights),
            'performance_metrics': {
                'expected_success_rate': average_success_rate,
                'expected_efficiency': insights.get('average_efficiency', 0.5),
                'expected_reward': insights.get('average_reward', 0.0)
            },
            'created_at': datetime.now().isoformat()
        }
        
        return strategy
    
    def _recommend_action(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """推薦動作"""
        action_sequence = pattern.get('action_sequence', [])
        
        if not action_sequence:
            return {'type': 'default_action', 'parameters': {}}
        
        # 選擇第一個成功的動作作為推薦
        for action in action_sequence:
            if action.get('success', True):
                return {
                    'type': action.get('action_type', 'unknown'),
                    'parameters': action.get('parameters', {}),
                    'expected_execution_time': action.get('execution_time', 0)
                }
        
        # 如果沒有成功的動作，返回第一個動作
        return {
            'type': action_sequence[0].get('action_type', 'unknown'),
            'parameters': action_sequence[0].get('parameters', {}),
            'expected_execution_time': action_sequence[0].get('execution_time', 0)
        }
    
    def _generate_reasoning(self, pattern: Dict[str, Any], context: Dict[str, Any]) -> str:
        """生成推理說明"""
        similarity_score = context.get('similarity_score', 0.5)
        success_rate = pattern.get('success_rate', 0.5)
        
        reasoning = f"基於相似度 {similarity_score:.1%} 的歷史模式，該策略的成功率為 {success_rate:.1%}。"
        
        if similarity_score > 0.9:
            reasoning += " 這是一個高度匹配的場景。"
        elif similarity_score > 0.7:
            reasoning += " 這是一個較為相似的場景。"
        else:
            reasoning += " 這是一個部分相似的場景，建議謹慎執行。"
        
        return reasoning
    
    def _generate_alternatives(self, pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成替代方案"""
        action_sequence = pattern.get('action_sequence', [])
        alternatives = []
        
        # 生成基於動作序列的替代方案
        for i, action in enumerate(action_sequence[1:3]):  # 取第2和第3個動作作為替代
            alternative = {
                'type': action.get('action_type', 'unknown'),
                'parameters': action.get('parameters', {}),
                'confidence': 0.7 - i * 0.1,  # 遞減置信度
                'reason': f"替代方案 {i+1}：基於歷史序列的第 {i+2} 個動作"
            }
            alternatives.append(alternative)
        
        return alternatives
    
    def _predict_outcome(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """預測結果"""
        return {
            'success_probability': pattern.get('success_rate', 0.5),
            'expected_efficiency': pattern.get('efficiency_score', 0.5),
            'expected_reward': pattern.get('total_reward', 0.0),
            'estimated_time': sum(action.get('execution_time', 0) for action in pattern.get('action_sequence', [])),
            'risk_level': 'low' if pattern.get('success_rate', 0.5) > 0.8 else 'medium'
        }
    
    def _determine_strategy_type(self, pattern: Dict[str, Any]) -> StrategyType:
        """確定策略類型"""
        success_rate = pattern.get('success_rate', 0.5)
        efficiency_score = pattern.get('efficiency_score', 0.5)
        
        if success_rate > 0.9 and efficiency_score > 0.8:
            return StrategyType.OPTIMIZATION
        elif success_rate < 0.5:
            return StrategyType.ERROR_RECOVERY
        elif success_rate > 0.7:
            return StrategyType.PATTERN_MATCHING
        else:
            return StrategyType.ADAPTIVE
    
    def _generate_optimization_suggestions(self, insights: Dict[str, Any]) -> List[str]:
        """生成優化建議"""
        suggestions = []
        
        avg_success_rate = insights.get('average_success_rate', 0.5)
        avg_efficiency = insights.get('average_efficiency', 0.5)
        improvement_trend = insights.get('improvement_trend', 'stable')
        
        if avg_success_rate < 0.8:
            suggestions.append("提高動作成功率：增加錯誤處理和重試機制")
        
        if avg_efficiency < 0.7:
            suggestions.append("提高執行效率：優化資源使用和並行處理")
        
        if improvement_trend == 'declining':
            suggestions.append("性能下降趨勢：需要重新評估策略有效性")
        
        if not suggestions:
            suggestions.append("當前策略表現良好，繼續監控和微調")
        
        return suggestions
    
    def _assess_risks(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """評估風險"""
        avg_success_rate = insights.get('average_success_rate', 0.5)
        pattern_count = insights.get('pattern_count', 0)
        improvement_trend = insights.get('improvement_trend', 'stable')
        
        risk_level = 'low'
        risk_factors = []
        
        if avg_success_rate < 0.6:
            risk_level = 'high'
            risk_factors.append('低成功率')
        
        if pattern_count < 3:
            risk_level = 'medium' if risk_level == 'low' else 'high'
            risk_factors.append('樣本數量不足')
        
        if improvement_trend == 'declining':
            risk_level = 'high'
            risk_factors.append('性能下降趨勢')
        
        return {
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'mitigation_strategies': self._generate_mitigation_strategies(risk_factors)
        }
    
    def _generate_mitigation_strategies(self, risk_factors: List[str]) -> List[str]:
        """生成風險緩解策略"""
        strategies = []
        
        for factor in risk_factors:
            if '低成功率' in factor:
                strategies.append('增加測試和驗證步驟')
            elif '樣本數量不足' in factor:
                strategies.append('收集更多訓練數據')
            elif '性能下降' in factor:
                strategies.append('重新評估和調整策略')
        
        return strategies
    
    def _get_default_strategy(self) -> Dict[str, Any]:
        """獲取默認策略"""
        return {
            'action': {'type': 'default_action', 'parameters': {}},
            'confidence': 0.5,
            'reasoning': '沒有找到匹配的歷史模式，使用默認策略',
            'alternatives': [],
            'expected_outcome': {
                'success_probability': 0.5,
                'expected_efficiency': 0.5,
                'risk_level': 'medium'
            },
            'strategy_type': StrategyType.ADAPTIVE
        }

class FeedbackProcessor:
    """反饋處理器"""
    
    def __init__(self):
        self.feedback_history = deque(maxlen=1000)
        self.learning_metrics = defaultdict(list)
        self.logger = logging.getLogger(f"{__name__}.FeedbackProcessor")
    
    def process_feedback(self, action_result: Dict[str, Any], 
                        expected_outcome: Dict[str, Any]) -> Dict[str, Any]:
        """處理執行反饋"""
        try:
            # 計算實際vs預期的差異
            feedback_analysis = self._analyze_feedback(action_result, expected_outcome)
            
            # 生成學習信號
            learning_signals = self._generate_learning_signals(feedback_analysis)
            
            # 更新學習指標
            self._update_learning_metrics(feedback_analysis, learning_signals)
            
            # 記錄反饋歷史
            feedback_record = {
                'action_result': action_result,
                'expected_outcome': expected_outcome,
                'feedback_analysis': feedback_analysis,
                'learning_signals': learning_signals,
                'timestamp': datetime.now().isoformat()
            }
            self.feedback_history.append(feedback_record)
            
            self.logger.info("反饋處理完成")
            
            return {
                'feedback_analysis': feedback_analysis,
                'learning_signals': learning_signals,
                'improvement_suggestions': self._generate_improvement_suggestions(feedback_analysis)
            }
            
        except Exception as e:
            self.logger.error(f"反饋處理失敗: {e}")
            return {}
    
    def _analyze_feedback(self, action_result: Dict[str, Any], 
                         expected_outcome: Dict[str, Any]) -> Dict[str, Any]:
        """分析反饋"""
        actual_success = action_result.get('success', False)
        expected_success = expected_outcome.get('success_probability', 0.5) > 0.5
        
        actual_time = action_result.get('execution_time', 0)
        expected_time = expected_outcome.get('estimated_time', 0)
        
        analysis = {
            'success_match': actual_success == expected_success,
            'success_accuracy': 1.0 if actual_success == expected_success else 0.0,
            'time_accuracy': self._calculate_time_accuracy(actual_time, expected_time),
            'overall_accuracy': 0.0,
            'prediction_errors': [],
            'positive_surprises': [],
            'negative_surprises': []
        }
        
        # 計算總體準確度
        analysis['overall_accuracy'] = (analysis['success_accuracy'] + analysis['time_accuracy']) / 2
        
        # 識別預測錯誤
        if not analysis['success_match']:
            if actual_success and not expected_success:
                analysis['positive_surprises'].append('unexpected_success')
            elif not actual_success and expected_success:
                analysis['negative_surprises'].append('unexpected_failure')
        
        if analysis['time_accuracy'] < 0.7:
            if actual_time > expected_time * 1.5:
                analysis['negative_surprises'].append('longer_than_expected')
            elif actual_time < expected_time * 0.5:
                analysis['positive_surprises'].append('faster_than_expected')
        
        return analysis
    
    def _calculate_time_accuracy(self, actual_time: float, expected_time: float) -> float:
        """計算時間準確度"""
        if expected_time == 0:
            return 1.0 if actual_time == 0 else 0.5
        
        ratio = actual_time / expected_time
        
        # 在0.5-2.0倍範圍內認為是合理的
        if 0.5 <= ratio <= 2.0:
            return 1.0 - abs(ratio - 1.0) / 1.0  # 越接近1.0越好
        else:
            return max(0.0, 1.0 - abs(ratio - 1.0) / 2.0)  # 超出範圍的懲罰
    
    def _generate_learning_signals(self, feedback_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成學習信號"""
        signals = {
            'prediction_quality': feedback_analysis['overall_accuracy'],
            'success_prediction_quality': feedback_analysis['success_accuracy'],
            'time_prediction_quality': feedback_analysis['time_accuracy'],
            'learning_opportunities': [],
            'reinforcement_signals': {}
        }
        
        # 識別學習機會
        if feedback_analysis['positive_surprises']:
            signals['learning_opportunities'].extend([
                f"學習正面意外: {surprise}" for surprise in feedback_analysis['positive_surprises']
            ])
        
        if feedback_analysis['negative_surprises']:
            signals['learning_opportunities'].extend([
                f"改進負面意外: {surprise}" for surprise in feedback_analysis['negative_surprises']
            ])
        
        # 生成強化信號
        if feedback_analysis['overall_accuracy'] > 0.8:
            signals['reinforcement_signals']['strategy_effectiveness'] = 'high'
        elif feedback_analysis['overall_accuracy'] > 0.6:
            signals['reinforcement_signals']['strategy_effectiveness'] = 'medium'
        else:
            signals['reinforcement_signals']['strategy_effectiveness'] = 'low'
        
        return signals
    
    def _update_learning_metrics(self, feedback_analysis: Dict[str, Any], 
                               learning_signals: Dict[str, Any]):
        """更新學習指標"""
        timestamp = datetime.now().isoformat()
        
        # 記錄準確度指標
        self.learning_metrics['overall_accuracy'].append({
            'value': feedback_analysis['overall_accuracy'],
            'timestamp': timestamp
        })
        
        self.learning_metrics['success_accuracy'].append({
            'value': feedback_analysis['success_accuracy'],
            'timestamp': timestamp
        })
        
        self.learning_metrics['time_accuracy'].append({
            'value': feedback_analysis['time_accuracy'],
            'timestamp': timestamp
        })
        
        # 記錄學習信號
        self.learning_metrics['prediction_quality'].append({
            'value': learning_signals['prediction_quality'],
            'timestamp': timestamp
        })
    
    def _generate_improvement_suggestions(self, feedback_analysis: Dict[str, Any]) -> List[str]:
        """生成改進建議"""
        suggestions = []
        
        if feedback_analysis['success_accuracy'] < 0.7:
            suggestions.append("改進成功率預測：收集更多成功/失敗案例")
        
        if feedback_analysis['time_accuracy'] < 0.7:
            suggestions.append("改進時間預測：優化執行時間估算模型")
        
        if feedback_analysis['negative_surprises']:
            suggestions.append("分析負面意外：識別預測盲點並改進模型")
        
        if feedback_analysis['positive_surprises']:
            suggestions.append("利用正面意外：將意外成功因素納入模型")
        
        return suggestions
    
    def get_learning_metrics_summary(self) -> Dict[str, Any]:
        """獲取學習指標摘要"""
        summary = {}
        
        for metric_name, metric_data in self.learning_metrics.items():
            if metric_data:
                values = [item['value'] for item in metric_data]
                summary[metric_name] = {
                    'current': values[-1],
                    'average': np.mean(values),
                    'trend': 'improving' if len(values) > 1 and values[-1] > values[0] else 'stable',
                    'sample_count': len(values)
                }
        
        return summary

class KnowledgeBase:
    """知識庫"""
    
    def __init__(self, knowledge_dir: str = "rl_knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.knowledge_dir.mkdir(exist_ok=True)
        
        self.experiences = []
        self.strategies = {}
        self.patterns = {}
        self.metrics = {}
        
        self.logger = logging.getLogger(f"{__name__}.KnowledgeBase")
        
        # 加載現有知識
        self._load_knowledge()
    
    def update(self, optimized_strategies: Dict[str, Any]):
        """更新知識庫"""
        try:
            strategy_id = optimized_strategies.get('pattern_key', 'unknown')
            
            # 更新策略
            self.strategies[strategy_id] = optimized_strategies
            
            # 保存知識
            self._save_knowledge()
            
            self.logger.info(f"知識庫更新完成: {strategy_id}")
            
        except Exception as e:
            self.logger.error(f"知識庫更新失敗: {e}")
    
    def add_experience(self, experience: LearningExperience):
        """添加學習經驗"""
        self.experiences.append(experience)
        
        # 限制經驗數量
        if len(self.experiences) > 1000:
            self.experiences = self.experiences[-1000:]
    
    def get_recent_updates(self) -> Dict[str, Any]:
        """獲取最近更新"""
        recent_strategies = {}
        recent_experiences = []
        
        # 獲取最近的策略
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for strategy_id, strategy in self.strategies.items():
            created_at = strategy.get('created_at', '')
            if created_at and datetime.fromisoformat(created_at) > cutoff_time:
                recent_strategies[strategy_id] = strategy
        
        # 獲取最近的經驗
        for experience in self.experiences[-10:]:  # 最近10個經驗
            recent_experiences.append(asdict(experience))
        
        return {
            'recent_strategies': recent_strategies,
            'recent_experiences': recent_experiences,
            'total_strategies': len(self.strategies),
            'total_experiences': len(self.experiences)
        }
    
    def _save_knowledge(self):
        """保存知識到文件"""
        try:
            # 保存策略
            strategies_file = self.knowledge_dir / "strategies.json"
            with open(strategies_file, 'w', encoding='utf-8') as f:
                json.dump(self.strategies, f, ensure_ascii=False, indent=2)
            
            # 保存經驗
            experiences_file = self.knowledge_dir / "experiences.pkl"
            with open(experiences_file, 'wb') as f:
                pickle.dump(self.experiences, f)
            
            # 保存模式
            patterns_file = self.knowledge_dir / "patterns.json"
            with open(patterns_file, 'w', encoding='utf-8') as f:
                json.dump(self.patterns, f, ensure_ascii=False, indent=2)
            
            self.logger.info("知識保存完成")
            
        except Exception as e:
            self.logger.error(f"知識保存失敗: {e}")
    
    def _load_knowledge(self):
        """從文件加載知識"""
        try:
            # 加載策略
            strategies_file = self.knowledge_dir / "strategies.json"
            if strategies_file.exists():
                with open(strategies_file, 'r', encoding='utf-8') as f:
                    self.strategies = json.load(f)
            
            # 加載經驗
            experiences_file = self.knowledge_dir / "experiences.pkl"
            if experiences_file.exists():
                with open(experiences_file, 'rb') as f:
                    self.experiences = pickle.load(f)
            
            # 加載模式
            patterns_file = self.knowledge_dir / "patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    self.patterns = json.load(f)
            
            self.logger.info(f"知識加載完成: {len(self.strategies)} 策略, {len(self.experiences)} 經驗")
            
        except Exception as e:
            self.logger.error(f"知識加載失敗: {e}")

class SimplifiedRLSRTAdapter:
    """簡化的RL SRT適配器"""
    
    def __init__(self, knowledge_dir: str = "rl_srt_knowledge"):
        self.pattern_matcher = PatternMatcher()
        self.strategy_optimizer = StrategyOptimizer()
        self.feedback_processor = FeedbackProcessor()
        self.knowledge_base = KnowledgeBase(knowledge_dir)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Simplified RL SRT Adapter 初始化完成")
    
    def process_training_data(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理來自Enhanced Interaction Log Manager的訓練數據"""
        try:
            self.logger.info(f"開始處理訓練數據: {training_data.get('session_id', 'unknown')}")
            
            # 1. 模式匹配學習
            pattern_insights = self.pattern_matcher.learn_patterns(training_data)
            self.logger.info("模式匹配學習完成")
            
            # 2. 策略優化
            optimized_strategies = self.strategy_optimizer.optimize(pattern_insights)
            self.logger.info("策略優化完成")
            
            # 3. 更新知識庫
            self.knowledge_base.update(optimized_strategies)
            self.logger.info("知識庫更新完成")
            
            # 4. 創建學習經驗
            experience = self._create_learning_experience(training_data, pattern_insights, optimized_strategies)
            self.knowledge_base.add_experience(experience)
            
            result = {
                'session_id': training_data.get('session_id'),
                'learned_patterns': pattern_insights,
                'optimized_strategies': optimized_strategies,
                'knowledge_updates': self.knowledge_base.get_recent_updates(),
                'learning_metrics': self.feedback_processor.get_learning_metrics_summary()
            }
            
            self.logger.info("訓練數據處理完成")
            return result
            
        except Exception as e:
            self.logger.error(f"訓練數據處理失敗: {e}")
            return {'error': str(e)}
    
    def recommend_action(self, current_context: Dict[str, Any]) -> ActionRecommendation:
        """基於學習的模式推薦動作"""
        try:
            self.logger.info("開始生成動作推薦")
            
            # 1. 匹配相似上下文
            similar_contexts = self.pattern_matcher.find_similar_contexts(current_context)
            self.logger.info(f"找到 {len(similar_contexts)} 個相似上下文")
            
            # 2. 獲取最佳策略
            best_strategy = self.strategy_optimizer.get_best_strategy(similar_contexts)
            self.logger.info("最佳策略獲取完成")
            
            # 3. 生成推薦
            recommendation = ActionRecommendation(
                recommended_action=best_strategy.get('action', {}),
                confidence_score=best_strategy.get('confidence', 0.5),
                reasoning=best_strategy.get('reasoning', ''),
                alternative_actions=best_strategy.get('alternatives', []),
                expected_outcome=best_strategy.get('expected_outcome', {}),
                strategy_type=best_strategy.get('strategy_type', StrategyType.ADAPTIVE),
                learning_feedback={
                    'similar_contexts_count': len(similar_contexts),
                    'best_match_similarity': similar_contexts[0].get('similarity_score', 0.0) if similar_contexts else 0.0,
                    'strategy_confidence': best_strategy.get('confidence', 0.5)
                }
            )
            
            self.logger.info(f"動作推薦生成完成，置信度: {recommendation.confidence_score:.2f}")
            return recommendation
            
        except Exception as e:
            self.logger.error(f"動作推薦生成失敗: {e}")
            return self._get_default_recommendation()
    
    def process_action_feedback(self, action_result: Dict[str, Any], 
                              expected_outcome: Dict[str, Any]) -> Dict[str, Any]:
        """處理動作執行反饋"""
        try:
            self.logger.info("開始處理動作反饋")
            
            # 處理反饋
            feedback_result = self.feedback_processor.process_feedback(action_result, expected_outcome)
            
            self.logger.info("動作反饋處理完成")
            return feedback_result
            
        except Exception as e:
            self.logger.error(f"動作反饋處理失敗: {e}")
            return {'error': str(e)}
    
    def _create_learning_experience(self, training_data: Dict[str, Any],
                                  pattern_insights: Dict[str, Any],
                                  optimized_strategies: Dict[str, Any]) -> LearningExperience:
        """創建學習經驗"""
        context_state_data = training_data.get('context_state', {})
        context_state = ContextState(
            task_type=context_state_data.get('task_type', 'unknown'),
            environment_type=context_state_data.get('environment_type', 'unknown'),
            available_tools=context_state_data.get('available_tools', 0),
            user_intent_clarity=context_state_data.get('user_intent_clarity', 0.5),
            complexity=context_state_data.get('initial_complexity', 'medium')
        )
        
        # 提取主要動作
        action_sequence = training_data.get('action_sequence', [])
        main_action = action_sequence[0] if action_sequence else {'action_type': 'unknown'}
        
        # 計算結果
        reward_signals = training_data.get('reward_signals', {})
        outcome = {
            'success': reward_signals.get('completion_reward', 0) > 0,
            'efficiency': reward_signals.get('efficiency_reward', 0.5),
            'satisfaction': reward_signals.get('satisfaction_reward', 0.5),
            'total_reward': reward_signals.get('total_reward', 0.0)
        }
        
        # 提取經驗教訓
        lessons_learned = []
        insights = pattern_insights.get('insights', {})
        if insights.get('improvement_trend') == 'improving':
            lessons_learned.append("策略效果正在改善")
        if insights.get('average_success_rate', 0) > 0.8:
            lessons_learned.append("高成功率策略")
        
        experience = LearningExperience(
            session_id=training_data.get('session_id', 'unknown'),
            context_state=context_state,
            action_taken=main_action,
            outcome=outcome,
            reward_score=reward_signals.get('total_reward', 0.0),
            lessons_learned=lessons_learned
        )
        
        return experience
    
    def _get_default_recommendation(self) -> ActionRecommendation:
        """獲取默認推薦"""
        return ActionRecommendation(
            recommended_action={'type': 'default_action', 'parameters': {}},
            confidence_score=0.5,
            reasoning='沒有找到匹配的歷史模式，使用默認推薦',
            alternative_actions=[],
            expected_outcome={'success_probability': 0.5, 'risk_level': 'medium'},
            strategy_type=StrategyType.ADAPTIVE,
            learning_feedback={'note': 'default_recommendation'}
        )
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """獲取學習統計信息"""
        return {
            'knowledge_base_stats': self.knowledge_base.get_recent_updates(),
            'learning_metrics': self.feedback_processor.get_learning_metrics_summary(),
            'pattern_database_size': len(self.pattern_matcher.patterns_db),
            'strategy_database_size': len(self.strategy_optimizer.strategies_db),
            'feedback_history_size': len(self.feedback_processor.feedback_history)
        }

# 導出主要類
__all__ = [
    'SimplifiedRLSRTAdapter',
    'ActionRecommendation',
    'LearningExperience',
    'ContextState',
    'StrategyType',
    'LearningMode'
]

if __name__ == "__main__":
    # 測試Simplified RL SRT Adapter
    adapter = SimplifiedRLSRTAdapter()
    
    # 測試訓練數據
    test_training_data = {
        'session_id': 'test_rl_session_001',
        'context_state': {
            'task_type': 'debugging',
            'environment_type': 'development',
            'available_tools': 5,
            'user_intent_clarity': 0.8,
            'initial_complexity': 'medium'
        },
        'action_sequence': [
            {
                'step_id': 0,
                'action_type': 'execute_command',
                'parameters': {'command': 'ps aux | grep smartui'},
                'execution_time': 2.5,
                'success': True,
                'immediate_reward': 1.0
            },
            {
                'step_id': 1,
                'action_type': 'check_port',
                'parameters': {'port': 8000},
                'execution_time': 1.2,
                'success': True,
                'immediate_reward': 1.0
            }
        ],
        'reward_signals': {
            'completion_reward': 1.0,
            'efficiency_reward': 0.8,
            'satisfaction_reward': 0.9,
            'time_reward': 0.7,
            'error_penalty': 0.0,
            'total_reward': 4.4
        }
    }
    
    # 處理訓練數據
    training_result = adapter.process_training_data(test_training_data)
    print("訓練結果:")
    print(f"會話ID: {training_result.get('session_id')}")
    print(f"學習模式: {len(training_result.get('learned_patterns', {}))}")
    print(f"優化策略: {training_result.get('optimized_strategies', {}).get('pattern_key', 'unknown')}")
    
    # 測試推薦
    test_context = {
        'task_type': 'debugging',
        'environment_type': 'development',
        'available_tools': 5,
        'user_intent_clarity': 0.8,
        'complexity': 'medium'
    }
    
    recommendation = adapter.recommend_action(test_context)
    print(f"\n推薦結果:")
    print(f"推薦動作: {recommendation.recommended_action}")
    print(f"置信度: {recommendation.confidence_score:.2f}")
    print(f"推理: {recommendation.reasoning}")
    
    # 獲取學習統計
    stats = adapter.get_learning_statistics()
    print(f"\n學習統計:")
    print(f"知識庫策略數: {stats.get('strategy_database_size', 0)}")
    print(f"模式數據庫大小: {stats.get('pattern_database_size', 0)}")
    print(f"反饋歷史大小: {stats.get('feedback_history_size', 0)}")

