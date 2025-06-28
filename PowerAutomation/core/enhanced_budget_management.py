#!/usr/bin/env python3
"""
Enhanced Budget Management System - 增强版预算管理系统
整合PowerAutomation-v2的智能成本控制优势到Core系统

核心功能:
- 智能预算管理和分配
- 实时成本监控和预警
- 成本预测和优化建议
- 多维度成本分析
- 自动成本优化策略
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)

class CostType(Enum):
    """成本类型"""
    API_CALL = "api_call"
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    TOOL_USAGE = "tool_usage"
    EXPERT_CONSULTATION = "expert_consultation"

class BudgetPeriod(Enum):
    """预算周期"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class AlertLevel(Enum):
    """预警级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class CostItem:
    """成本项目"""
    id: str
    type: CostType
    amount: float
    description: str
    timestamp: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class BudgetConfig:
    """预算配置"""
    total_budget: float
    period: BudgetPeriod
    cost_limits: Dict[CostType, float]
    alert_thresholds: Dict[AlertLevel, float]
    auto_optimization: bool = True
    
@dataclass
class CostPrediction:
    """成本预测"""
    predicted_cost: float
    confidence: float
    factors: List[str]
    optimization_suggestions: List[str]
    risk_assessment: str

@dataclass
class BudgetAlert:
    """预算预警"""
    level: AlertLevel
    message: str
    current_usage: float
    budget_limit: float
    usage_percentage: float
    recommendations: List[str]
    timestamp: float

class CostPredictor:
    """成本预测器"""
    
    def __init__(self):
        self.historical_data = []
        self.prediction_models = {}
        
    async def predict_cost(self, task_description: str, context: Dict[str, Any]) -> CostPrediction:
        """预测任务成本"""
        # 分析任务复杂度
        complexity_score = self._analyze_complexity(task_description, context)
        
        # 预测各类成本
        api_cost = self._predict_api_cost(complexity_score, context)
        compute_cost = self._predict_compute_cost(complexity_score, context)
        tool_cost = self._predict_tool_cost(task_description, context)
        
        total_predicted_cost = api_cost + compute_cost + tool_cost
        
        # 生成优化建议
        optimization_suggestions = self._generate_optimization_suggestions(
            task_description, total_predicted_cost, context
        )
        
        return CostPrediction(
            predicted_cost=total_predicted_cost,
            confidence=0.85,  # 基于历史准确率
            factors=[
                f"API调用成本: ${api_cost:.4f}",
                f"计算成本: ${compute_cost:.4f}",
                f"工具使用成本: ${tool_cost:.4f}"
            ],
            optimization_suggestions=optimization_suggestions,
            risk_assessment=self._assess_cost_risk(total_predicted_cost)
        )
    
    def _analyze_complexity(self, task_description: str, context: Dict[str, Any]) -> float:
        """分析任务复杂度"""
        complexity_factors = {
            'length': len(task_description) / 1000,
            'context_size': len(str(context)) / 1000,
            'keywords': self._count_complex_keywords(task_description),
            'data_processing': 1.0 if 'data' in task_description.lower() else 0.0
        }
        
        return sum(complexity_factors.values()) / len(complexity_factors)
    
    def _predict_api_cost(self, complexity_score: float, context: Dict[str, Any]) -> float:
        """预测API调用成本"""
        base_cost = 0.002  # 基础API调用成本
        complexity_multiplier = 1 + complexity_score
        context_multiplier = 1 + (len(str(context)) / 10000)
        
        return base_cost * complexity_multiplier * context_multiplier
    
    def _predict_compute_cost(self, complexity_score: float, context: Dict[str, Any]) -> float:
        """预测计算成本"""
        base_compute_cost = 0.001
        return base_compute_cost * (1 + complexity_score)
    
    def _predict_tool_cost(self, task_description: str, context: Dict[str, Any]) -> float:
        """预测工具使用成本"""
        tool_keywords = ['search', 'analysis', 'generation', 'processing']
        tool_usage_count = sum(1 for keyword in tool_keywords if keyword in task_description.lower())
        
        return tool_usage_count * 0.0005  # 每个工具使用0.0005美元
    
    def _count_complex_keywords(self, text: str) -> int:
        """计算复杂关键词数量"""
        complex_keywords = [
            'analysis', 'optimization', 'generation', 'processing',
            'complex', 'detailed', 'comprehensive', 'advanced'
        ]
        return sum(1 for keyword in complex_keywords if keyword in text.lower())
    
    def _generate_optimization_suggestions(self, task_description: str, predicted_cost: float, context: Dict[str, Any]) -> List[str]:
        """生成成本优化建议"""
        suggestions = []
        
        if predicted_cost > 0.01:
            suggestions.append("考虑将复杂任务分解为多个简单子任务")
            
        if len(str(context)) > 5000:
            suggestions.append("优化上下文信息，移除不必要的数据")
            
        if 'detailed' in task_description.lower():
            suggestions.append("评估是否需要详细分析，考虑使用摘要模式")
            
        return suggestions
    
    def _assess_cost_risk(self, predicted_cost: float) -> str:
        """评估成本风险"""
        if predicted_cost < 0.005:
            return "低风险 - 成本在预期范围内"
        elif predicted_cost < 0.02:
            return "中等风险 - 建议监控成本使用"
        else:
            return "高风险 - 强烈建议优化任务或增加预算"

class BudgetManager:
    """预算管理器"""
    
    def __init__(self, config: BudgetConfig):
        self.config = config
        self.current_usage = 0.0
        self.cost_history = []
        self.alerts = []
        self.cost_predictor = CostPredictor()
        
        # 成本追踪
        self.cost_by_type = {cost_type: 0.0 for cost_type in CostType}
        self.daily_usage = {}
        
        logger.info(f"预算管理器初始化完成 - 总预算: ${config.total_budget}")
    
    async def evaluate_task_cost(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """评估任务成本"""
        if context is None:
            context = {}
            
        # 预测成本
        prediction = await self.cost_predictor.predict_cost(task_description, context)
        
        # 检查预算约束
        budget_check = self._check_budget_constraints(prediction.predicted_cost)
        
        # 生成建议
        recommendations = self._generate_task_recommendations(prediction, budget_check)
        
        return {
            'prediction': asdict(prediction),
            'budget_check': budget_check,
            'recommendations': recommendations,
            'approval_required': prediction.predicted_cost > self.config.total_budget * 0.1
        }
    
    def _check_budget_constraints(self, predicted_cost: float) -> Dict[str, Any]:
        """检查预算约束"""
        remaining_budget = self.config.total_budget - self.current_usage
        usage_after_task = self.current_usage + predicted_cost
        usage_percentage = (usage_after_task / self.config.total_budget) * 100
        
        return {
            'remaining_budget': remaining_budget,
            'predicted_usage_after': usage_after_task,
            'usage_percentage': usage_percentage,
            'within_budget': predicted_cost <= remaining_budget,
            'risk_level': self._calculate_risk_level(usage_percentage)
        }
    
    def _calculate_risk_level(self, usage_percentage: float) -> str:
        """计算风险级别"""
        if usage_percentage < 50:
            return "low"
        elif usage_percentage < 75:
            return "medium"
        elif usage_percentage < 90:
            return "high"
        else:
            return "critical"
    
    def _generate_task_recommendations(self, prediction: CostPrediction, budget_check: Dict[str, Any]) -> List[str]:
        """生成任务建议"""
        recommendations = []
        
        if not budget_check['within_budget']:
            recommendations.append("⚠️ 预测成本超出剩余预算，建议优化任务或增加预算")
            
        if budget_check['risk_level'] == 'high':
            recommendations.append("📊 预算使用率较高，建议谨慎执行")
            
        recommendations.extend(prediction.optimization_suggestions)
        
        return recommendations
    
    async def record_cost(self, cost_item: CostItem) -> None:
        """记录成本"""
        self.current_usage += cost_item.amount
        self.cost_history.append(cost_item)
        self.cost_by_type[cost_item.type] += cost_item.amount
        
        # 记录每日使用情况
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.daily_usage:
            self.daily_usage[today] = 0.0
        self.daily_usage[today] += cost_item.amount
        
        # 检查预警
        await self._check_alerts()
        
        logger.info(f"记录成本: {cost_item.type.value} ${cost_item.amount:.4f}")
    
    async def _check_alerts(self) -> None:
        """检查预警条件"""
        usage_percentage = (self.current_usage / self.config.total_budget) * 100
        
        for alert_level, threshold in self.config.alert_thresholds.items():
            if usage_percentage >= threshold:
                alert = BudgetAlert(
                    level=alert_level,
                    message=f"预算使用率达到 {usage_percentage:.1f}%",
                    current_usage=self.current_usage,
                    budget_limit=self.config.total_budget,
                    usage_percentage=usage_percentage,
                    recommendations=self._generate_alert_recommendations(alert_level),
                    timestamp=time.time()
                )
                
                self.alerts.append(alert)
                logger.warning(f"预算预警: {alert.message}")
    
    def _generate_alert_recommendations(self, alert_level: AlertLevel) -> List[str]:
        """生成预警建议"""
        recommendations = []
        
        if alert_level == AlertLevel.WARNING:
            recommendations.extend([
                "监控后续任务的成本使用",
                "考虑优化高成本操作",
                "评估是否需要调整预算"
            ])
        elif alert_level == AlertLevel.CRITICAL:
            recommendations.extend([
                "立即暂停非必要的高成本操作",
                "审查当前任务的必要性",
                "考虑增加预算或延期部分任务"
            ])
        elif alert_level == AlertLevel.EMERGENCY:
            recommendations.extend([
                "停止所有非紧急任务",
                "立即联系管理员增加预算",
                "启动成本应急处理流程"
            ])
            
        return recommendations
    
    def get_budget_status(self) -> Dict[str, Any]:
        """获取预算状态"""
        usage_percentage = (self.current_usage / self.config.total_budget) * 100
        
        return {
            'total_budget': self.config.total_budget,
            'current_usage': self.current_usage,
            'remaining_budget': self.config.total_budget - self.current_usage,
            'usage_percentage': usage_percentage,
            'cost_by_type': dict(self.cost_by_type),
            'daily_usage': dict(self.daily_usage),
            'active_alerts': len([a for a in self.alerts if a.timestamp > time.time() - 3600]),
            'risk_level': self._calculate_risk_level(usage_percentage)
        }
    
    async def optimize_costs(self) -> Dict[str, Any]:
        """自动成本优化"""
        if not self.config.auto_optimization:
            return {'optimization_enabled': False}
            
        optimization_actions = []
        savings_estimate = 0.0
        
        # 分析成本模式
        cost_analysis = self._analyze_cost_patterns()
        
        # 生成优化建议
        if cost_analysis['high_cost_types']:
            optimization_actions.append("优化高成本操作类型")
            savings_estimate += cost_analysis['potential_savings']
            
        return {
            'optimization_enabled': True,
            'actions_taken': optimization_actions,
            'estimated_savings': savings_estimate,
            'cost_analysis': cost_analysis
        }
    
    def _analyze_cost_patterns(self) -> Dict[str, Any]:
        """分析成本模式"""
        if not self.cost_history:
            return {'high_cost_types': [], 'potential_savings': 0.0}
            
        # 找出高成本类型
        high_cost_types = [
            cost_type for cost_type, amount in self.cost_by_type.items()
            if amount > self.config.total_budget * 0.2
        ]
        
        potential_savings = sum(
            self.cost_by_type[cost_type] * 0.1  # 假设可以节省10%
            for cost_type in high_cost_types
        )
        
        return {
            'high_cost_types': [ct.value for ct in high_cost_types],
            'potential_savings': potential_savings,
            'total_transactions': len(self.cost_history),
            'average_transaction_cost': self.current_usage / len(self.cost_history) if self.cost_history else 0
        }

class CostOptimizer:
    """成本优化器"""
    
    def __init__(self, budget_manager: BudgetManager):
        self.budget_manager = budget_manager
        self.optimization_strategies = {
            'task_decomposition': self._optimize_task_decomposition,
            'caching': self._optimize_caching,
            'batch_processing': self._optimize_batch_processing,
            'resource_pooling': self._optimize_resource_pooling
        }
    
    async def optimize_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """优化任务以降低成本"""
        original_prediction = await self.budget_manager.cost_predictor.predict_cost(task_description, context)
        
        optimization_results = {}
        best_strategy = None
        max_savings = 0.0
        
        for strategy_name, strategy_func in self.optimization_strategies.items():
            try:
                result = await strategy_func(task_description, context, original_prediction)
                optimization_results[strategy_name] = result
                
                if result['savings'] > max_savings:
                    max_savings = result['savings']
                    best_strategy = strategy_name
                    
            except Exception as e:
                logger.error(f"优化策略 {strategy_name} 执行失败: {e}")
                optimization_results[strategy_name] = {'error': str(e)}
        
        return {
            'original_cost': original_prediction.predicted_cost,
            'optimization_results': optimization_results,
            'best_strategy': best_strategy,
            'max_savings': max_savings,
            'optimized_cost': original_prediction.predicted_cost - max_savings
        }
    
    async def _optimize_task_decomposition(self, task_description: str, context: Dict[str, Any], original_prediction: CostPrediction) -> Dict[str, Any]:
        """任务分解优化"""
        # 简化实现：假设分解可以节省20%成本
        savings = original_prediction.predicted_cost * 0.2
        
        return {
            'strategy': 'task_decomposition',
            'savings': savings,
            'description': '将复杂任务分解为多个简单子任务',
            'implementation': [
                '识别任务中的独立组件',
                '按优先级排序子任务',
                '并行处理可并行的子任务'
            ]
        }
    
    async def _optimize_caching(self, task_description: str, context: Dict[str, Any], original_prediction: CostPrediction) -> Dict[str, Any]:
        """缓存优化"""
        # 检查是否有可缓存的内容
        cacheable_keywords = ['analysis', 'search', 'lookup', 'query']
        has_cacheable_content = any(keyword in task_description.lower() for keyword in cacheable_keywords)
        
        savings = original_prediction.predicted_cost * 0.15 if has_cacheable_content else 0.0
        
        return {
            'strategy': 'caching',
            'savings': savings,
            'description': '利用缓存减少重复计算',
            'applicable': has_cacheable_content
        }
    
    async def _optimize_batch_processing(self, task_description: str, context: Dict[str, Any], original_prediction: CostPrediction) -> Dict[str, Any]:
        """批处理优化"""
        # 检查是否适合批处理
        batch_keywords = ['multiple', 'batch', 'list', 'several']
        suitable_for_batch = any(keyword in task_description.lower() for keyword in batch_keywords)
        
        savings = original_prediction.predicted_cost * 0.25 if suitable_for_batch else 0.0
        
        return {
            'strategy': 'batch_processing',
            'savings': savings,
            'description': '批量处理相似任务以降低单位成本',
            'applicable': suitable_for_batch
        }
    
    async def _optimize_resource_pooling(self, task_description: str, context: Dict[str, Any], original_prediction: CostPrediction) -> Dict[str, Any]:
        """资源池化优化"""
        # 简化实现：假设资源池化可以节省10%成本
        savings = original_prediction.predicted_cost * 0.1
        
        return {
            'strategy': 'resource_pooling',
            'savings': savings,
            'description': '共享和重用计算资源',
            'implementation': [
                '复用已初始化的模型和工具',
                '共享中间计算结果',
                '优化资源分配策略'
            ]
        }

# 使用示例和测试
async def demo_budget_management():
    """演示预算管理功能"""
    
    # 配置预算
    budget_config = BudgetConfig(
        total_budget=10.0,  # 10美元预算
        period=BudgetPeriod.MONTHLY,
        cost_limits={
            CostType.API_CALL: 5.0,
            CostType.COMPUTE: 3.0,
            CostType.TOOL_USAGE: 2.0
        },
        alert_thresholds={
            AlertLevel.WARNING: 50.0,
            AlertLevel.CRITICAL: 80.0,
            AlertLevel.EMERGENCY: 95.0
        }
    )
    
    # 创建预算管理器
    budget_manager = BudgetManager(budget_config)
    cost_optimizer = CostOptimizer(budget_manager)
    
    # 测试任务成本评估
    test_task = "分析大型数据集并生成详细报告，包括数据可视化和深度洞察"
    
    print("=== 成本评估演示 ===")
    cost_evaluation = await budget_manager.evaluate_task_cost(test_task)
    print(f"任务: {test_task}")
    print(f"预测成本: ${cost_evaluation['prediction']['predicted_cost']:.4f}")
    print(f"优化建议: {cost_evaluation['recommendations']}")
    
    # 测试成本优化
    print("\n=== 成本优化演示 ===")
    optimization_result = await cost_optimizer.optimize_task(test_task, {})
    print(f"原始成本: ${optimization_result['original_cost']:.4f}")
    print(f"最佳策略: {optimization_result['best_strategy']}")
    print(f"最大节省: ${optimization_result['max_savings']:.4f}")
    print(f"优化后成本: ${optimization_result['optimized_cost']:.4f}")
    
    # 模拟成本记录
    print("\n=== 成本记录演示 ===")
    cost_item = CostItem(
        id=str(uuid.uuid4()),
        type=CostType.API_CALL,
        amount=0.05,
        description="Claude API调用",
        timestamp=time.time()
    )
    
    await budget_manager.record_cost(cost_item)
    
    # 查看预算状态
    budget_status = budget_manager.get_budget_status()
    print(f"当前预算状态:")
    print(f"- 总预算: ${budget_status['total_budget']}")
    print(f"- 已使用: ${budget_status['current_usage']:.4f}")
    print(f"- 剩余: ${budget_status['remaining_budget']:.4f}")
    print(f"- 使用率: {budget_status['usage_percentage']:.1f}%")

if __name__ == "__main__":
    asyncio.run(demo_budget_management())

