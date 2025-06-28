#!/usr/bin/env python3
"""
AICore 3.1 - Enhanced Dynamic Expert System
增强版动态专家系统，优化性能监控和错误处理
"""

import asyncio
import time
import logging
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import hashlib
import traceback

# 导入组件
from components.general_processor_mcp import GeneralProcessorMCP, create_general_processor_mcp
from components.dynamic_expert_registry import (
    DynamicExpertRegistry, create_dynamic_expert_registry,
    ExpertRegistrationRequest, ExpertProfile, ExpertStatus, ExpertType as DynamicExpertType
)
from components.expert_recommendation_aggregator import (
    ExpertRecommendationAggregator, create_expert_recommendation_aggregator,
    AggregationStrategy, AggregatedRecommendation, AggregationResult
)
from components.dynamic_mcp_generator import (
    DynamicMCPGenerator, create_dynamic_mcp_generator,
    MCPToolType, MCPToolSpec, DynamicMCPRequest
)
from tools.tool_registry import ToolRegistry
from actions.action_executor import ActionExecutor

# 增强版导入
try:
    from components.enhanced_test_flow_mcp_v52 import TestFlowMCPv52
except ImportError:
    TestFlowMCPv52 = None

logger = logging.getLogger(__name__)

class ProcessingStage(Enum):
    """处理阶段 - 6阶段完整流程"""
    INTEGRATED_SEARCH_ANALYSIS = "integrated_search_analysis"      # 整合式搜索和分析
    DYNAMIC_EXPERT_GENERATION = "dynamic_expert_generation"        # 动态专家生成
    EXPERT_RESPONSE_GENERATION = "expert_response_generation"      # 专家回答生成
    EXPERT_RECOMMENDATION_AGGREGATION = "expert_recommendation_aggregation"  # 专家建议聚合
    DYNAMIC_TOOL_GENERATION = "dynamic_tool_generation"           # 动态工具生成和执行
    FINAL_RESULT_GENERATION = "final_result_generation"           # 最终结果生成

class PerformanceLevel(Enum):
    """性能等级"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    CRITICAL = "critical"

@dataclass
class PerformanceMetrics:
    """性能指标数据结构"""
    execution_time: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    success_rate: float = 100.0
    error_count: int = 0
    warning_count: int = 0
    stage_timings: Dict[str, float] = None
    
    def __post_init__(self):
        if self.stage_timings is None:
            self.stage_timings = {}
    
    def get_performance_level(self) -> PerformanceLevel:
        """获取性能等级"""
        if self.execution_time < 1.0 and self.success_rate >= 95:
            return PerformanceLevel.EXCELLENT
        elif self.execution_time < 3.0 and self.success_rate >= 90:
            return PerformanceLevel.GOOD
        elif self.execution_time < 5.0 and self.success_rate >= 80:
            return PerformanceLevel.AVERAGE
        elif self.execution_time < 10.0 and self.success_rate >= 70:
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL

@dataclass
class UserRequest:
    """用户请求数据结构"""
    id: str
    content: str
    context: Dict[str, Any]
    priority: str = "normal"
    metadata: Dict[str, Any] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class ExpertResponse:
    """专家响应数据结构"""
    expert_id: str
    expert_name: str
    expert_type: str
    analysis: str
    recommendations: List[str]
    tool_suggestions: List[Dict[str, Any]]
    confidence: float
    processing_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ProcessingResult:
    """处理结果数据结构"""
    request_id: str
    success: bool
    stage_results: Dict[str, Any]
    expert_analysis: List[ExpertResponse]
    tool_execution_results: List[Dict[str, Any]]
    final_answer: str
    confidence: float
    execution_time: float
    metadata: Dict[str, Any]
    performance_metrics: PerformanceMetrics = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.performance_metrics is None:
            self.performance_metrics = PerformanceMetrics()

class EnhancedErrorHandler:
    """增强版错误处理器"""
    
    def __init__(self):
        self.error_history = []
        self.error_patterns = {}
        
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理错误"""
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'traceback': traceback.format_exc()
        }
        
        self.error_history.append(error_info)
        
        # 分析错误模式
        error_pattern = self._analyze_error_pattern(error_info)
        
        # 生成恢复建议
        recovery_suggestions = self._generate_recovery_suggestions(error_pattern)
        
        return {
            'error_info': error_info,
            'error_pattern': error_pattern,
            'recovery_suggestions': recovery_suggestions,
            'should_retry': self._should_retry(error_pattern),
            'retry_delay': self._get_retry_delay(error_pattern)
        }
    
    def _analyze_error_pattern(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析错误模式"""
        error_type = error_info['error_type']
        
        if error_type not in self.error_patterns:
            self.error_patterns[error_type] = {
                'count': 0,
                'first_occurrence': error_info['timestamp'],
                'last_occurrence': error_info['timestamp'],
                'contexts': []
            }
        
        pattern = self.error_patterns[error_type]
        pattern['count'] += 1
        pattern['last_occurrence'] = error_info['timestamp']
        pattern['contexts'].append(error_info['context'])
        
        return {
            'error_type': error_type,
            'frequency': pattern['count'],
            'is_recurring': pattern['count'] > 1,
            'time_span': pattern['last_occurrence']
        }
    
    def _generate_recovery_suggestions(self, error_pattern: Dict[str, Any]) -> List[str]:
        """生成恢复建议"""
        suggestions = []
        error_type = error_pattern['error_type']
        
        if error_type == 'ModuleNotFoundError':
            suggestions.extend([
                "检查模块导入路径是否正确",
                "确认所需的依赖包已安装",
                "验证Python路径配置"
            ])
        elif error_type == 'ConnectionError':
            suggestions.extend([
                "检查网络连接状态",
                "验证服务端点可用性",
                "考虑增加重试机制"
            ])
        elif error_type == 'TimeoutError':
            suggestions.extend([
                "增加超时时间限制",
                "优化处理逻辑性能",
                "考虑异步处理方案"
            ])
        else:
            suggestions.append("查看详细错误信息和堆栈跟踪")
        
        return suggestions
    
    def _should_retry(self, error_pattern: Dict[str, Any]) -> bool:
        """判断是否应该重试"""
        error_type = error_pattern['error_type']
        frequency = error_pattern['frequency']
        
        # 网络相关错误可以重试，但不超过3次
        if error_type in ['ConnectionError', 'TimeoutError'] and frequency <= 3:
            return True
        
        # 其他错误类型一般不重试
        return False
    
    def _get_retry_delay(self, error_pattern: Dict[str, Any]) -> float:
        """获取重试延迟时间"""
        frequency = error_pattern['frequency']
        # 指数退避策略
        return min(2 ** frequency, 30.0)

class IntegratedCloudSearch:
    """整合式Cloud Search引擎"""
    
    def __init__(self):
        self.mock_mode = True  # 开发阶段使用模拟模式
        self.performance_tracker = {}
    
    async def integrated_search(self, params: Dict) -> Dict:
        """执行整合式搜索"""
        start_time = time.time()
        
        try:
            # 模拟搜索过程
            await asyncio.sleep(0.1)  # 模拟网络延迟
            
            search_results = {
                'query': params.get('query', ''),
                'results': [
                    {
                        'title': f"搜索结果 {i+1}",
                        'content': f"这是关于 '{params.get('query', '')}' 的搜索结果内容 {i+1}",
                        'relevance': 0.9 - i * 0.1,
                        'source': f"source_{i+1}.com"
                    }
                    for i in range(3)
                ],
                'total_results': 3,
                'search_time': time.time() - start_time
            }
            
            # 记录性能指标
            self.performance_tracker['last_search_time'] = time.time() - start_time
            
            return search_results
            
        except Exception as e:
            logger.error(f"搜索过程中发生错误: {str(e)}")
            return {
                'query': params.get('query', ''),
                'results': [],
                'total_results': 0,
                'error': str(e),
                'search_time': time.time() - start_time
            }

class AICore31:
    """AICore 3.1 - 增强版动态专家系统"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.version = "3.1"
        
        # 初始化日志
        self.logger = self._setup_logging()
        
        # 初始化组件
        self.general_processor = create_general_processor_mcp()
        self.expert_registry = create_dynamic_expert_registry()
        self.recommendation_aggregator = create_expert_recommendation_aggregator()
        self.mcp_generator = create_dynamic_mcp_generator()
        self.tool_registry = ToolRegistry()
        self.action_executor = ActionExecutor()
        
        # 增强版组件
        self.cloud_search = IntegratedCloudSearch()
        self.error_handler = EnhancedErrorHandler()
        self.test_flow_mcp = TestFlowMCPv52() if TestFlowMCPv52 else None
        
        # 性能监控
        self.performance_history = []
        self.processing_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_processing_time': 0.0
        }
        
        self.logger.info(f"AICore {self.version} 初始化完成")
    
    def _setup_logging(self):
        """设置日志"""
        logger = logging.getLogger(f"AICore_{self.version}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def process_request(self, request: UserRequest) -> ProcessingResult:
        """处理用户请求 - 主要入口点"""
        start_time = time.time()
        request_id = request.id
        
        self.logger.info(f"开始处理请求: {request_id}")
        
        # 初始化结果结构
        result = ProcessingResult(
            request_id=request_id,
            success=False,
            stage_results={},
            expert_analysis=[],
            tool_execution_results=[],
            final_answer="",
            confidence=0.0,
            execution_time=0.0,
            metadata={}
        )
        
        try:
            # 阶段1: 整合式搜索和分析
            stage1_result = await self._stage1_integrated_search_analysis(request)
            result.stage_results[ProcessingStage.INTEGRATED_SEARCH_ANALYSIS.value] = stage1_result
            
            # 阶段2: 动态专家生成
            stage2_result = await self._stage2_dynamic_expert_generation(request, stage1_result)
            result.stage_results[ProcessingStage.DYNAMIC_EXPERT_GENERATION.value] = stage2_result
            
            # 阶段3: 专家回答生成
            stage3_result = await self._stage3_expert_response_generation(request, stage2_result)
            result.stage_results[ProcessingStage.EXPERT_RESPONSE_GENERATION.value] = stage3_result
            result.expert_analysis = stage3_result.get('expert_responses', [])
            
            # 阶段4: 专家建议聚合
            stage4_result = await self._stage4_expert_recommendation_aggregation(stage3_result)
            result.stage_results[ProcessingStage.EXPERT_RECOMMENDATION_AGGREGATION.value] = stage4_result
            
            # 阶段5: 动态工具生成和执行
            stage5_result = await self._stage5_dynamic_tool_generation(stage4_result)
            result.stage_results[ProcessingStage.DYNAMIC_TOOL_GENERATION.value] = stage5_result
            result.tool_execution_results = stage5_result.get('tool_results', [])
            
            # 阶段6: 最终结果生成
            stage6_result = await self._stage6_final_result_generation(result.stage_results)
            result.stage_results[ProcessingStage.FINAL_RESULT_GENERATION.value] = stage6_result
            
            # 设置最终结果
            result.final_answer = stage6_result.get('final_answer', '')
            result.confidence = stage6_result.get('confidence', 0.0)
            result.success = True
            
        except Exception as e:
            self.logger.error(f"处理请求时发生错误: {str(e)}")
            
            # 使用增强版错误处理
            error_analysis = self.error_handler.handle_error(e, {
                'request_id': request_id,
                'stage': 'processing',
                'request_content': request.content
            })
            
            result.metadata['error_analysis'] = error_analysis
            result.final_answer = f"处理过程中发生错误: {str(e)}"
            result.success = False
        
        # 计算执行时间和性能指标
        execution_time = time.time() - start_time
        result.execution_time = execution_time
        
        # 更新性能指标
        performance_metrics = PerformanceMetrics(
            execution_time=execution_time,
            success_rate=100.0 if result.success else 0.0,
            error_count=0 if result.success else 1
        )
        result.performance_metrics = performance_metrics
        
        # 更新统计信息
        self._update_processing_stats(result)
        
        self.logger.info(f"请求处理完成: {request_id}, 成功: {result.success}, 耗时: {execution_time:.2f}s")
        
        return result
    
    async def _stage1_integrated_search_analysis(self, request: UserRequest) -> Dict[str, Any]:
        """阶段1: 整合式搜索和分析"""
        start_time = time.time()
        
        try:
            # 执行搜索
            search_params = {
                'query': request.content,
                'context': request.context,
                'priority': request.priority
            }
            
            search_results = await self.cloud_search.integrated_search(search_params)
            
            # 分析搜索结果
            analysis = {
                'search_quality': self._evaluate_search_quality(search_results),
                'key_topics': self._extract_key_topics(search_results),
                'complexity_level': self._assess_complexity(request.content),
                'recommended_experts': self._suggest_expert_types(search_results)
            }
            
            return {
                'search_results': search_results,
                'analysis': analysis,
                'processing_time': time.time() - start_time,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"阶段1处理错误: {str(e)}")
            return {
                'search_results': {},
                'analysis': {},
                'processing_time': time.time() - start_time,
                'success': False,
                'error': str(e)
            }
    
    async def _stage2_dynamic_expert_generation(self, request: UserRequest, stage1_result: Dict) -> Dict[str, Any]:
        """阶段2: 动态专家生成"""
        start_time = time.time()
        
        try:
            analysis = stage1_result.get('analysis', {})
            recommended_experts = analysis.get('recommended_experts', ['general'])
            
            generated_experts = []
            for expert_type in recommended_experts:
                expert_profile = await self._generate_expert_profile(expert_type, request, stage1_result)
                generated_experts.append(expert_profile)
            
            return {
                'generated_experts': generated_experts,
                'expert_count': len(generated_experts),
                'processing_time': time.time() - start_time,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"阶段2处理错误: {str(e)}")
            return {
                'generated_experts': [],
                'expert_count': 0,
                'processing_time': time.time() - start_time,
                'success': False,
                'error': str(e)
            }
    
    async def _stage3_expert_response_generation(self, request: UserRequest, stage2_result: Dict) -> Dict[str, Any]:
        """阶段3: 专家回答生成"""
        start_time = time.time()
        
        try:
            experts = stage2_result.get('generated_experts', [])
            expert_responses = []
            
            for expert in experts:
                response = await self._generate_expert_response(expert, request)
                expert_responses.append(response)
            
            return {
                'expert_responses': expert_responses,
                'response_count': len(expert_responses),
                'processing_time': time.time() - start_time,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"阶段3处理错误: {str(e)}")
            return {
                'expert_responses': [],
                'response_count': 0,
                'processing_time': time.time() - start_time,
                'success': False,
                'error': str(e)
            }
    
    async def _stage4_expert_recommendation_aggregation(self, stage3_result: Dict) -> Dict[str, Any]:
        """阶段4: 专家建议聚合"""
        start_time = time.time()
        
        try:
            expert_responses = stage3_result.get('expert_responses', [])
            
            # 聚合专家建议
            aggregated_recommendations = []
            confidence_scores = []
            
            for response in expert_responses:
                aggregated_recommendations.extend(response.recommendations)
                confidence_scores.append(response.confidence)
            
            # 计算整体置信度
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            # 去重和排序建议
            unique_recommendations = list(set(aggregated_recommendations))
            
            return {
                'aggregated_recommendations': unique_recommendations,
                'overall_confidence': overall_confidence,
                'expert_count': len(expert_responses),
                'processing_time': time.time() - start_time,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"阶段4处理错误: {str(e)}")
            return {
                'aggregated_recommendations': [],
                'overall_confidence': 0.0,
                'expert_count': 0,
                'processing_time': time.time() - start_time,
                'success': False,
                'error': str(e)
            }
    
    async def _stage5_dynamic_tool_generation(self, stage4_result: Dict) -> Dict[str, Any]:
        """阶段5: 动态工具生成和执行"""
        start_time = time.time()
        
        try:
            recommendations = stage4_result.get('aggregated_recommendations', [])
            
            # 基于建议生成工具
            tool_results = []
            for i, recommendation in enumerate(recommendations[:3]):  # 限制工具数量
                tool_result = await self._execute_recommendation_tool(recommendation, i)
                tool_results.append(tool_result)
            
            return {
                'tool_results': tool_results,
                'tool_count': len(tool_results),
                'processing_time': time.time() - start_time,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"阶段5处理错误: {str(e)}")
            return {
                'tool_results': [],
                'tool_count': 0,
                'processing_time': time.time() - start_time,
                'success': False,
                'error': str(e)
            }
    
    async def _stage6_final_result_generation(self, stage_results: Dict) -> Dict[str, Any]:
        """阶段6: 最终结果生成"""
        start_time = time.time()
        
        try:
            # 整合所有阶段的结果
            search_analysis = stage_results.get(ProcessingStage.INTEGRATED_SEARCH_ANALYSIS.value, {})
            expert_responses = stage_results.get(ProcessingStage.EXPERT_RESPONSE_GENERATION.value, {})
            aggregated_recommendations = stage_results.get(ProcessingStage.EXPERT_RECOMMENDATION_AGGREGATION.value, {})
            tool_results = stage_results.get(ProcessingStage.DYNAMIC_TOOL_GENERATION.value, {})
            
            # 生成最终答案
            final_answer = self._synthesize_final_answer(
                search_analysis, expert_responses, aggregated_recommendations, tool_results
            )
            
            # 计算整体置信度
            confidence = aggregated_recommendations.get('overall_confidence', 0.0)
            
            return {
                'final_answer': final_answer,
                'confidence': confidence,
                'processing_time': time.time() - start_time,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"阶段6处理错误: {str(e)}")
            return {
                'final_answer': f"生成最终结果时发生错误: {str(e)}",
                'confidence': 0.0,
                'processing_time': time.time() - start_time,
                'success': False,
                'error': str(e)
            }
    
    def _evaluate_search_quality(self, search_results: Dict) -> float:
        """评估搜索质量"""
        results = search_results.get('results', [])
        if not results:
            return 0.0
        
        # 基于结果数量和相关性评分
        relevance_scores = [r.get('relevance', 0.0) for r in results]
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        
        # 结果数量因子
        count_factor = min(len(results) / 5.0, 1.0)
        
        return avg_relevance * count_factor
    
    def _extract_key_topics(self, search_results: Dict) -> List[str]:
        """提取关键主题"""
        # 简化实现，实际应该使用NLP技术
        query = search_results.get('query', '')
        topics = []
        
        # 基于查询内容提取关键词
        keywords = query.lower().split()
        for keyword in keywords:
            if len(keyword) > 2:  # 过滤短词
                topics.append(keyword)
        
        return topics[:5]  # 返回前5个主题
    
    def _assess_complexity(self, content: str) -> str:
        """评估复杂度"""
        word_count = len(content.split())
        
        if word_count < 10:
            return "simple"
        elif word_count < 50:
            return "medium"
        else:
            return "complex"
    
    def _suggest_expert_types(self, search_results: Dict) -> List[str]:
        """建议专家类型"""
        query = search_results.get('query', '').lower()
        expert_types = []
        
        # 基于关键词匹配专家类型
        if any(keyword in query for keyword in ['code', 'programming', 'development']):
            expert_types.append('code_expert')
        if any(keyword in query for keyword in ['design', 'ui', 'ux']):
            expert_types.append('design_expert')
        if any(keyword in query for keyword in ['data', 'analysis', 'statistics']):
            expert_types.append('data_expert')
        
        # 默认添加通用专家
        if not expert_types:
            expert_types.append('general_expert')
        
        return expert_types
    
    async def _generate_expert_profile(self, expert_type: str, request: UserRequest, stage1_result: Dict) -> Dict[str, Any]:
        """生成专家档案"""
        expert_id = hashlib.md5(f"{expert_type}_{request.id}".encode()).hexdigest()[:8]
        
        return {
            'expert_id': expert_id,
            'expert_type': expert_type,
            'expert_name': f"{expert_type.replace('_', ' ').title()} Expert",
            'specialization': self._get_expert_specialization(expert_type),
            'confidence_level': 0.8,
            'created_at': datetime.now().isoformat()
        }
    
    def _get_expert_specialization(self, expert_type: str) -> List[str]:
        """获取专家专业领域"""
        specializations = {
            'code_expert': ['软件开发', '代码审查', '架构设计', '性能优化'],
            'design_expert': ['用户界面设计', '用户体验', '视觉设计', '交互设计'],
            'data_expert': ['数据分析', '统计建模', '机器学习', '数据可视化'],
            'general_expert': ['问题分析', '解决方案设计', '项目管理', '咨询建议']
        }
        
        return specializations.get(expert_type, ['通用咨询'])
    
    async def _generate_expert_response(self, expert: Dict, request: UserRequest) -> ExpertResponse:
        """生成专家回应"""
        expert_type = expert['expert_type']
        
        # 模拟专家分析过程
        await asyncio.sleep(0.1)  # 模拟思考时间
        
        analysis = f"作为{expert['expert_name']}，我分析了您的请求：{request.content[:100]}..."
        
        recommendations = [
            f"建议1：基于{expert_type}的角度，建议采用最佳实践方法",
            f"建议2：考虑{expert['specialization'][0]}的相关因素",
            f"建议3：建议进一步深入{expert['specialization'][1] if len(expert['specialization']) > 1 else '相关领域'}的研究"
        ]
        
        tool_suggestions = [
            {
                'tool_name': f"{expert_type}_analyzer",
                'tool_description': f"用于{expert_type}分析的专用工具",
                'parameters': {'input': request.content}
            }
        ]
        
        return ExpertResponse(
            expert_id=expert['expert_id'],
            expert_name=expert['expert_name'],
            expert_type=expert_type,
            analysis=analysis,
            recommendations=recommendations,
            tool_suggestions=tool_suggestions,
            confidence=0.85,
            processing_time=0.1
        )
    
    async def _execute_recommendation_tool(self, recommendation: str, tool_index: int) -> Dict[str, Any]:
        """执行建议工具"""
        # 模拟工具执行
        await asyncio.sleep(0.05)
        
        return {
            'tool_id': f"tool_{tool_index}",
            'tool_name': f"recommendation_processor_{tool_index}",
            'input': recommendation,
            'output': f"已处理建议：{recommendation[:50]}...",
            'success': True,
            'execution_time': 0.05
        }
    
    def _synthesize_final_answer(self, search_analysis: Dict, expert_responses: Dict, 
                                aggregated_recommendations: Dict, tool_results: Dict) -> str:
        """综合生成最终答案"""
        
        # 获取各阶段的关键信息
        search_quality = search_analysis.get('analysis', {}).get('search_quality', 0.0)
        expert_count = expert_responses.get('response_count', 0)
        recommendations = aggregated_recommendations.get('aggregated_recommendations', [])
        tool_count = tool_results.get('tool_count', 0)
        
        # 构建最终答案
        answer_parts = []
        
        answer_parts.append("基于AICore 3.1的综合分析，我为您提供以下解答：")
        
        if search_quality > 0.7:
            answer_parts.append(f"✅ 通过高质量搜索分析（质量评分：{search_quality:.2f}），我们获得了相关信息。")
        
        if expert_count > 0:
            answer_parts.append(f"🧠 {expert_count}位专业专家参与了分析，提供了多角度的见解。")
        
        if recommendations:
            answer_parts.append("📋 主要建议包括：")
            for i, rec in enumerate(recommendations[:3], 1):
                answer_parts.append(f"   {i}. {rec}")
        
        if tool_count > 0:
            answer_parts.append(f"🔧 执行了{tool_count}个专业工具进行深度分析。")
        
        answer_parts.append("💡 这个解答结合了搜索分析、专家知识和工具执行的结果，为您提供全面的解决方案。")
        
        return "\n".join(answer_parts)
    
    def _update_processing_stats(self, result: ProcessingResult):
        """更新处理统计信息"""
        self.processing_stats['total_requests'] += 1
        
        if result.success:
            self.processing_stats['successful_requests'] += 1
        else:
            self.processing_stats['failed_requests'] += 1
        
        # 更新平均处理时间
        total_time = (self.processing_stats['average_processing_time'] * 
                     (self.processing_stats['total_requests'] - 1) + result.execution_time)
        self.processing_stats['average_processing_time'] = total_time / self.processing_stats['total_requests']
        
        # 记录性能历史
        self.performance_history.append({
            'timestamp': result.timestamp,
            'execution_time': result.execution_time,
            'success': result.success,
            'performance_level': result.performance_metrics.get_performance_level().value
        })
        
        # 保持历史记录在合理范围内
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'version': self.version,
            'processing_stats': self.processing_stats.copy(),
            'performance_history_count': len(self.performance_history),
            'error_patterns': len(self.error_handler.error_patterns),
            'components_status': {
                'general_processor': bool(self.general_processor),
                'expert_registry': bool(self.expert_registry),
                'recommendation_aggregator': bool(self.recommendation_aggregator),
                'mcp_generator': bool(self.mcp_generator),
                'test_flow_mcp': bool(self.test_flow_mcp),
                'cloud_search': bool(self.cloud_search),
                'error_handler': bool(self.error_handler)
            },
            'timestamp': datetime.now().isoformat()
        }

# 工厂函数
def create_aicore31(config: Optional[Dict] = None) -> AICore31:
    """创建AICore 3.1实例"""
    return AICore31(config)

# 向后兼容性
AICore3 = AICore31
create_aicore3 = create_aicore31

# 主函数用于测试
async def main():
    """主函数"""
    print("AICore 3.1 - Enhanced Dynamic Expert System")
    print("=" * 50)
    
    # 创建AICore实例
    aicore = create_aicore31()
    
    # 创建测试请求
    test_request = UserRequest(
        id="test_001",
        content="如何设计一个高性能的Web应用程序？",
        context={
            'domain': 'web_development',
            'complexity': 'high',
            'requirements': ['performance', 'scalability', 'security']
        }
    )
    
    print(f"处理测试请求: {test_request.content}")
    print("-" * 50)
    
    # 处理请求
    result = await aicore.process_request(test_request)
    
    # 显示结果
    print(f"处理结果:")
    print(f"  成功: {result.success}")
    print(f"  执行时间: {result.execution_time:.2f}秒")
    print(f"  置信度: {result.confidence:.2f}")
    print(f"  性能等级: {result.performance_metrics.get_performance_level().value}")
    print(f"  专家分析数量: {len(result.expert_analysis)}")
    print(f"  工具执行数量: {len(result.tool_execution_results)}")
    
    print(f"\n最终答案:")
    print(result.final_answer)
    
    # 显示系统状态
    print(f"\n系统状态:")
    status = aicore.get_system_status()
    for key, value in status.items():
        if key != 'components_status':
            print(f"  {key}: {value}")
    
    print(f"\n组件状态:")
    for component, status in status['components_status'].items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {component}")

if __name__ == "__main__":
    asyncio.run(main())

