#!/usr/bin/env python3
"""
Human-in-the-Loop Integration Tool for PowerAutomation
作為獨立工具集成到PowerAutomation，不修改AICore核心

這個工具提供：
1. 智能決策路由 (自動/人工/專家/條件)
2. Human Loop MCP集成
3. 專家系統調用
4. 深度測試框架
5. 增量優化學習

設計原則：
- 不修改AICore核心組件
- 作為獨立工具運行
- 通過API與現有系統集成
- 可插拔的架構設計
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import aiohttp
import sqlite3
from pathlib import Path

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DecisionType(Enum):
    """決策類型枚舉"""
    AUTOMATIC = "automatic"
    HUMAN_REQUIRED = "human_required"
    EXPERT_CONSULTATION = "expert_consultation"
    CONDITIONAL = "conditional"

class ExpertType(Enum):
    """專家類型枚舉"""
    TECHNICAL = "technical"
    API = "api"
    BUSINESS = "business"
    DATA = "data"
    INTEGRATION = "integration"
    SECURITY = "security"
    PERFORMANCE = "performance"

class InteractionType(Enum):
    """交互類型枚舉"""
    APPROVAL = "approval"
    INPUT = "input"
    SELECTION = "selection"
    CONFIRMATION = "confirmation"

@dataclass
class WorkflowContext:
    """工作流上下文"""
    workflow_id: str
    title: str
    description: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    status: str = "pending"
    
class HumanLoopIntegrationTool:
    """Human-in-the-Loop Integration Tool 主類"""
    
    def __init__(self, config_path: str = None):
        """初始化工具"""
        self.config = self._load_config(config_path)
        self.db_path = self.config.get('database_path', 'human_loop_integration.db')
        self.human_loop_mcp_url = self.config.get('human_loop_mcp_url', 'http://localhost:8096')
        self.aicore_api_url = self.config.get('aicore_api_url', 'http://localhost:8080')
        
        # 初始化數據庫
        self._init_database()
        
        # 決策學習模型
        self.decision_model = DecisionLearningModel(self.db_path)
        
        # 專家系統
        self.expert_system = ExpertSystem()
        
        # 測試框架
        self.testing_framework = TestingFramework()
        
        logger.info("Human Loop Integration Tool initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """載入配置"""
        default_config = {
            'database_path': 'human_loop_integration.db',
            'human_loop_mcp_url': 'http://localhost:8096',
            'aicore_api_url': 'http://localhost:8080',
            'decision_thresholds': {
                'complexity_threshold': 0.7,
                'risk_threshold': 0.6,
                'confidence_threshold': 0.8
            },
            'expert_mapping': {
                'deployment': 'technical',
                'api_integration': 'api',
                'business_logic': 'business',
                'data_processing': 'data',
                'system_integration': 'integration',
                'security_review': 'security',
                'performance_optimization': 'performance'
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _init_database(self):
        """初始化數據庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 創建工作流表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                parameters TEXT,
                metadata TEXT,
                status TEXT,
                decision_type TEXT,
                created_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')
        
        # 創建決策歷史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decision_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT,
                decision_type TEXT,
                complexity_score REAL,
                risk_score REAL,
                confidence_score REAL,
                success BOOLEAN,
                execution_time REAL,
                created_at TIMESTAMP,
                FOREIGN KEY (workflow_id) REFERENCES workflows (id)
            )
        ''')
        
        # 創建專家調用記錄表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expert_invocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT,
                expert_type TEXT,
                recommendation TEXT,
                confidence REAL,
                success BOOLEAN,
                created_at TIMESTAMP,
                FOREIGN KEY (workflow_id) REFERENCES workflows (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def process_workflow(self, workflow_context: WorkflowContext) -> Dict[str, Any]:
        """處理工作流的主要入口點"""
        logger.info(f"Processing workflow: {workflow_context.workflow_id}")
        
        try:
            # 1. 分析工作流並做出路由決策
            decision = await self._make_routing_decision(workflow_context)
            
            # 2. 根據決策類型執行相應的處理
            result = await self._execute_decision(workflow_context, decision)
            
            # 3. 記錄結果並學習
            await self._record_and_learn(workflow_context, decision, result)
            
            return {
                'workflow_id': workflow_context.workflow_id,
                'decision_type': decision['type'],
                'result': result,
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing workflow {workflow_context.workflow_id}: {str(e)}")
            return {
                'workflow_id': workflow_context.workflow_id,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _make_routing_decision(self, context: WorkflowContext) -> Dict[str, Any]:
        """智能路由決策"""
        # 計算複雜度分數
        complexity_score = self._calculate_complexity(context)
        
        # 計算風險分數
        risk_score = self._calculate_risk(context)
        
        # 獲取歷史信心度
        confidence_score = await self.decision_model.predict_confidence(context)
        
        # 決策邏輯
        thresholds = self.config['decision_thresholds']
        
        if complexity_score > thresholds['complexity_threshold'] and risk_score > thresholds['risk_threshold']:
            decision_type = DecisionType.HUMAN_REQUIRED
        elif complexity_score > thresholds['complexity_threshold']:
            decision_type = DecisionType.EXPERT_CONSULTATION
        elif confidence_score < thresholds['confidence_threshold']:
            decision_type = DecisionType.CONDITIONAL
        else:
            decision_type = DecisionType.AUTOMATIC
        
        return {
            'type': decision_type,
            'complexity_score': complexity_score,
            'risk_score': risk_score,
            'confidence_score': confidence_score,
            'reasoning': self._generate_decision_reasoning(decision_type, complexity_score, risk_score, confidence_score)
        }
    
    def _calculate_complexity(self, context: WorkflowContext) -> float:
        """計算工作流複雜度"""
        complexity_factors = {
            'parameter_count': len(context.parameters) * 0.1,
            'workflow_type': self._get_workflow_type_complexity(context.metadata.get('workflow_type', 'unknown')),
            'dependencies': len(context.metadata.get('dependencies', [])) * 0.15,
            'environment': self._get_environment_complexity(context.metadata.get('environment', 'development'))
        }
        
        total_complexity = sum(complexity_factors.values())
        return min(total_complexity, 1.0)  # 限制在0-1之間
    
    def _calculate_risk(self, context: WorkflowContext) -> float:
        """計算工作流風險"""
        risk_factors = {
            'environment': self._get_environment_risk(context.metadata.get('environment', 'development')),
            'operation_type': self._get_operation_risk(context.metadata.get('operation_type', 'read')),
            'data_sensitivity': self._get_data_sensitivity_risk(context.metadata.get('data_sensitivity', 'low')),
            'system_impact': self._get_system_impact_risk(context.metadata.get('system_impact', 'low'))
        }
        
        total_risk = sum(risk_factors.values())
        return min(total_risk, 1.0)  # 限制在0-1之間
    
    def _get_workflow_type_complexity(self, workflow_type: str) -> float:
        """獲取工作流類型複雜度"""
        complexity_map = {
            'deployment': 0.8,
            'configuration': 0.6,
            'testing': 0.4,
            'monitoring': 0.3,
            'maintenance': 0.5,
            'unknown': 0.7
        }
        return complexity_map.get(workflow_type, 0.7)
    
    def _get_environment_complexity(self, environment: str) -> float:
        """獲取環境複雜度"""
        complexity_map = {
            'development': 0.2,
            'testing': 0.4,
            'staging': 0.6,
            'production': 0.9
        }
        return complexity_map.get(environment, 0.5)
    
    def _get_environment_risk(self, environment: str) -> float:
        """獲取環境風險"""
        risk_map = {
            'development': 0.1,
            'testing': 0.2,
            'staging': 0.5,
            'production': 0.9
        }
        return risk_map.get(environment, 0.5)
    
    def _get_operation_risk(self, operation_type: str) -> float:
        """獲取操作風險"""
        risk_map = {
            'read': 0.1,
            'write': 0.4,
            'delete': 0.8,
            'deploy': 0.7,
            'configure': 0.6,
            'restart': 0.5
        }
        return risk_map.get(operation_type, 0.5)
    
    def _get_data_sensitivity_risk(self, sensitivity: str) -> float:
        """獲取數據敏感性風險"""
        risk_map = {
            'low': 0.1,
            'medium': 0.4,
            'high': 0.7,
            'critical': 0.9
        }
        return risk_map.get(sensitivity, 0.3)
    
    def _get_system_impact_risk(self, impact: str) -> float:
        """獲取系統影響風險"""
        risk_map = {
            'low': 0.1,
            'medium': 0.4,
            'high': 0.7,
            'critical': 0.9
        }
        return risk_map.get(impact, 0.3)
    
    def _generate_decision_reasoning(self, decision_type: DecisionType, complexity: float, risk: float, confidence: float) -> str:
        """生成決策推理"""
        reasoning_parts = []
        
        if decision_type == DecisionType.HUMAN_REQUIRED:
            reasoning_parts.append(f"高複雜度({complexity:.2f})和高風險({risk:.2f})需要人工介入")
        elif decision_type == DecisionType.EXPERT_CONSULTATION:
            reasoning_parts.append(f"高複雜度({complexity:.2f})需要專家諮詢")
        elif decision_type == DecisionType.CONDITIONAL:
            reasoning_parts.append(f"低信心度({confidence:.2f})需要條件處理")
        else:
            reasoning_parts.append(f"複雜度({complexity:.2f})、風險({risk:.2f})和信心度({confidence:.2f})都在可接受範圍內，可自動處理")
        
        return "; ".join(reasoning_parts)
    
    async def _execute_decision(self, context: WorkflowContext, decision: Dict[str, Any]) -> Dict[str, Any]:
        """執行決策"""
        decision_type = decision['type']
        
        if decision_type == DecisionType.AUTOMATIC:
            return await self._execute_automatic(context)
        elif decision_type == DecisionType.HUMAN_REQUIRED:
            return await self._execute_with_human_loop(context, decision)
        elif decision_type == DecisionType.EXPERT_CONSULTATION:
            return await self._execute_with_expert(context, decision)
        elif decision_type == DecisionType.CONDITIONAL:
            return await self._execute_conditional(context, decision)
        else:
            raise ValueError(f"Unknown decision type: {decision_type}")
    
    async def _execute_automatic(self, context: WorkflowContext) -> Dict[str, Any]:
        """自動執行"""
        logger.info(f"Executing workflow {context.workflow_id} automatically")
        
        # 調用AICore API執行工作流
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.aicore_api_url}/api/workflows/execute",
                    json=asdict(context)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'execution_type': 'automatic',
                            'success': True,
                            'result': result,
                            'message': '自動執行成功'
                        }
                    else:
                        return {
                            'execution_type': 'automatic',
                            'success': False,
                            'error': f"API call failed with status {response.status}",
                            'message': '自動執行失敗'
                        }
        except Exception as e:
            return {
                'execution_type': 'automatic',
                'success': False,
                'error': str(e),
                'message': '自動執行出錯'
            }
    
    async def _execute_with_human_loop(self, context: WorkflowContext, decision: Dict[str, Any]) -> Dict[str, Any]:
        """通過Human Loop MCP執行"""
        logger.info(f"Executing workflow {context.workflow_id} with human loop")
        
        try:
            # 創建Human Loop MCP會話
            session_data = {
                'workflow_id': context.workflow_id,
                'title': context.title,
                'description': context.description,
                'interaction_type': InteractionType.CONFIRMATION.value,
                'options': ['確認執行', '拒絕執行', '修改參數'],
                'context': {
                    'parameters': context.parameters,
                    'decision_reasoning': decision['reasoning'],
                    'complexity_score': decision['complexity_score'],
                    'risk_score': decision['risk_score']
                }
            }
            
            async with aiohttp.ClientSession() as session:
                # 創建會話
                async with session.post(
                    f"{self.human_loop_mcp_url}/api/sessions",
                    json=session_data
                ) as response:
                    if response.status == 200:
                        session_result = await response.json()
                        session_id = session_result['session_id']
                        
                        # 等待人工回應
                        human_response = await self._wait_for_human_response(session_id)
                        
                        if human_response['choice'] == '確認執行':
                            # 執行工作流
                            execution_result = await self._execute_automatic(context)
                            return {
                                'execution_type': 'human_approved',
                                'success': execution_result['success'],
                                'result': execution_result.get('result'),
                                'human_response': human_response,
                                'message': '人工確認後執行'
                            }
                        elif human_response['choice'] == '修改參數':
                            # 更新參數並重新處理
                            if 'updated_parameters' in human_response:
                                context.parameters.update(human_response['updated_parameters'])
                                return await self.process_workflow(context)
                            else:
                                return {
                                    'execution_type': 'human_rejected',
                                    'success': False,
                                    'human_response': human_response,
                                    'message': '人工要求修改參數但未提供新參數'
                                }
                        else:
                            return {
                                'execution_type': 'human_rejected',
                                'success': False,
                                'human_response': human_response,
                                'message': '人工拒絕執行'
                            }
                    else:
                        return {
                            'execution_type': 'human_loop_error',
                            'success': False,
                            'error': f"Failed to create human loop session: {response.status}",
                            'message': 'Human Loop MCP會話創建失敗'
                        }
        except Exception as e:
            return {
                'execution_type': 'human_loop_error',
                'success': False,
                'error': str(e),
                'message': 'Human Loop執行出錯'
            }
    
    async def _wait_for_human_response(self, session_id: str, timeout: int = 300) -> Dict[str, Any]:
        """等待人工回應"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.human_loop_mcp_url}/api/sessions/{session_id}/status"
                    ) as response:
                        if response.status == 200:
                            status_data = await response.json()
                            if status_data['status'] == 'completed':
                                return status_data['response']
                            elif status_data['status'] == 'cancelled':
                                return {'choice': '拒絕執行', 'reason': '會話被取消'}
                        
                        # 等待5秒後重試
                        await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Error checking human response: {str(e)}")
                await asyncio.sleep(5)
        
        # 超時
        return {'choice': '拒絕執行', 'reason': '等待超時'}
    
    async def _execute_with_expert(self, context: WorkflowContext, decision: Dict[str, Any]) -> Dict[str, Any]:
        """通過專家系統執行"""
        logger.info(f"Executing workflow {context.workflow_id} with expert consultation")
        
        # 確定需要的專家類型
        expert_type = self._determine_expert_type(context)
        
        # 調用專家系統
        expert_recommendation = await self.expert_system.get_recommendation(
            expert_type, context, decision
        )
        
        if expert_recommendation['confidence'] > 0.8:
            # 專家建議執行
            execution_result = await self._execute_automatic(context)
            return {
                'execution_type': 'expert_approved',
                'success': execution_result['success'],
                'result': execution_result.get('result'),
                'expert_recommendation': expert_recommendation,
                'message': '專家建議執行'
            }
        else:
            # 專家建議需要人工介入
            return await self._execute_with_human_loop(context, decision)
    
    def _determine_expert_type(self, context: WorkflowContext) -> ExpertType:
        """確定需要的專家類型"""
        workflow_type = context.metadata.get('workflow_type', 'unknown')
        expert_mapping = self.config['expert_mapping']
        
        expert_type_str = expert_mapping.get(workflow_type, 'technical')
        return ExpertType(expert_type_str)
    
    async def _execute_conditional(self, context: WorkflowContext, decision: Dict[str, Any]) -> Dict[str, Any]:
        """條件執行"""
        logger.info(f"Executing workflow {context.workflow_id} conditionally")
        
        # 運行測試框架評估
        test_result = await self.testing_framework.run_pre_execution_tests(context)
        
        if test_result['success_rate'] > 0.8:
            # 測試通過，自動執行
            return await self._execute_automatic(context)
        else:
            # 測試未通過，需要專家或人工介入
            if test_result['success_rate'] > 0.6:
                return await self._execute_with_expert(context, decision)
            else:
                return await self._execute_with_human_loop(context, decision)
    
    async def _record_and_learn(self, context: WorkflowContext, decision: Dict[str, Any], result: Dict[str, Any]):
        """記錄結果並學習"""
        # 記錄到數據庫
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 記錄工作流
        cursor.execute('''
            INSERT OR REPLACE INTO workflows 
            (id, title, description, parameters, metadata, status, decision_type, created_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            context.workflow_id,
            context.title,
            context.description,
            json.dumps(context.parameters),
            json.dumps(context.metadata),
            'completed' if result['success'] else 'failed',
            decision['type'].value,
            context.created_at.isoformat(),
            datetime.now().isoformat()
        ))
        
        # 記錄決策歷史
        cursor.execute('''
            INSERT INTO decision_history 
            (workflow_id, decision_type, complexity_score, risk_score, confidence_score, success, execution_time, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            context.workflow_id,
            decision['type'].value,
            decision['complexity_score'],
            decision['risk_score'],
            decision['confidence_score'],
            result['success'],
            result.get('execution_time', 0),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # 更新學習模型
        await self.decision_model.learn_from_result(context, decision, result)

class DecisionLearningModel:
    """決策學習模型"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    async def predict_confidence(self, context: WorkflowContext) -> float:
        """預測信心度"""
        # 基於歷史數據預測
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查找相似的工作流
        cursor.execute('''
            SELECT success, complexity_score, risk_score 
            FROM decision_history 
            WHERE decision_type = ? 
            ORDER BY created_at DESC 
            LIMIT 10
        ''', ('automatic',))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return 0.5  # 默認信心度
        
        # 計算成功率
        success_rate = sum(1 for r in results if r[0]) / len(results)
        
        # 基於複雜度和風險調整
        avg_complexity = sum(r[1] for r in results) / len(results)
        avg_risk = sum(r[2] for r in results) / len(results)
        
        # 簡單的信心度計算
        confidence = success_rate * (1 - avg_complexity * 0.3) * (1 - avg_risk * 0.3)
        
        return max(0.1, min(0.9, confidence))
    
    async def learn_from_result(self, context: WorkflowContext, decision: Dict[str, Any], result: Dict[str, Any]):
        """從結果中學習"""
        # 這裡可以實現更複雜的機器學習算法
        # 目前只是記錄數據，實際的學習在predict_confidence中進行
        logger.info(f"Learning from workflow {context.workflow_id} result: {result['success']}")

class ExpertSystem:
    """專家系統"""
    
    async def get_recommendation(self, expert_type: ExpertType, context: WorkflowContext, decision: Dict[str, Any]) -> Dict[str, Any]:
        """獲取專家建議"""
        # 模擬專家系統邏輯
        recommendations = {
            ExpertType.TECHNICAL: self._technical_expert_recommendation,
            ExpertType.API: self._api_expert_recommendation,
            ExpertType.BUSINESS: self._business_expert_recommendation,
            ExpertType.DATA: self._data_expert_recommendation,
            ExpertType.INTEGRATION: self._integration_expert_recommendation,
            ExpertType.SECURITY: self._security_expert_recommendation,
            ExpertType.PERFORMANCE: self._performance_expert_recommendation
        }
        
        expert_func = recommendations.get(expert_type, self._default_expert_recommendation)
        return expert_func(context, decision)
    
    def _technical_expert_recommendation(self, context: WorkflowContext, decision: Dict[str, Any]) -> Dict[str, Any]:
        """技術專家建議"""
        # 基於技術複雜度和環境評估
        environment = context.metadata.get('environment', 'development')
        workflow_type = context.metadata.get('workflow_type', 'unknown')
        
        confidence = 0.8
        if environment == 'production' and workflow_type == 'deployment':
            confidence = 0.6  # 生產環境部署需要更謹慎
        
        return {
            'expert_type': 'technical',
            'confidence': confidence,
            'recommendation': 'proceed' if confidence > 0.7 else 'review_required',
            'reasoning': f'基於環境({environment})和工作流類型({workflow_type})的技術評估'
        }
    
    def _api_expert_recommendation(self, context: WorkflowContext, decision: Dict[str, Any]) -> Dict[str, Any]:
        """API專家建議"""
        return {
            'expert_type': 'api',
            'confidence': 0.75,
            'recommendation': 'proceed',
            'reasoning': 'API集成風險評估通過'
        }
    
    def _business_expert_recommendation(self, context: WorkflowContext, decision: Dict[str, Any]) -> Dict[str, Any]:
        """業務專家建議"""
        return {
            'expert_type': 'business',
            'confidence': 0.8,
            'recommendation': 'proceed',
            'reasoning': '業務邏輯評估通過'
        }
    
    def _data_expert_recommendation(self, context: WorkflowContext, decision: Dict[str, Any]) -> Dict[str, Any]:
        """數據專家建議"""
        data_sensitivity = context.metadata.get('data_sensitivity', 'low')
        confidence = 0.9 if data_sensitivity == 'low' else 0.6
        
        return {
            'expert_type': 'data',
            'confidence': confidence,
            'recommendation': 'proceed' if confidence > 0.7 else 'review_required',
            'reasoning': f'基於數據敏感性({data_sensitivity})的評估'
        }
    
    def _integration_expert_recommendation(self, context: WorkflowContext, decision: Dict[str, Any]) -> Dict[str, Any]:
        """集成專家建議"""
        return {
            'expert_type': 'integration',
            'confidence': 0.75,
            'recommendation': 'proceed',
            'reasoning': '系統集成評估通過'
        }
    
    def _security_expert_recommendation(self, context: WorkflowContext, decision: Dict[str, Any]) -> Dict[str, Any]:
        """安全專家建議"""
        environment = context.metadata.get('environment', 'development')
        confidence = 0.9 if environment == 'development' else 0.7
        
        return {
            'expert_type': 'security',
            'confidence': confidence,
            'recommendation': 'proceed' if confidence > 0.7 else 'review_required',
            'reasoning': f'基於環境({environment})的安全評估'
        }
    
    def _performance_expert_recommendation(self, context: WorkflowContext, decision: Dict[str, Any]) -> Dict[str, Any]:
        """性能專家建議"""
        return {
            'expert_type': 'performance',
            'confidence': 0.8,
            'recommendation': 'proceed',
            'reasoning': '性能影響評估通過'
        }
    
    def _default_expert_recommendation(self, context: WorkflowContext, decision: Dict[str, Any]) -> Dict[str, Any]:
        """默認專家建議"""
        return {
            'expert_type': 'general',
            'confidence': 0.6,
            'recommendation': 'review_required',
            'reasoning': '需要進一步評估'
        }

class TestingFramework:
    """測試框架"""
    
    async def run_pre_execution_tests(self, context: WorkflowContext) -> Dict[str, Any]:
        """運行執行前測試"""
        test_results = []
        
        # 運行各種測試
        test_results.append(await self._run_unit_tests(context))
        test_results.append(await self._run_integration_tests(context))
        test_results.append(await self._run_security_tests(context))
        test_results.append(await self._run_performance_tests(context))
        
        # 計算總體成功率
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result['passed'])
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        return {
            'success_rate': success_rate,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'test_results': test_results
        }
    
    async def _run_unit_tests(self, context: WorkflowContext) -> Dict[str, Any]:
        """運行單元測試"""
        # 模擬單元測試
        await asyncio.sleep(0.1)  # 模擬測試時間
        
        return {
            'test_type': 'unit',
            'passed': True,
            'message': '單元測試通過',
            'details': '所有組件功能正常'
        }
    
    async def _run_integration_tests(self, context: WorkflowContext) -> Dict[str, Any]:
        """運行集成測試"""
        # 模擬集成測試
        await asyncio.sleep(0.2)  # 模擬測試時間
        
        return {
            'test_type': 'integration',
            'passed': True,
            'message': '集成測試通過',
            'details': '系統間交互正常'
        }
    
    async def _run_security_tests(self, context: WorkflowContext) -> Dict[str, Any]:
        """運行安全測試"""
        # 模擬安全測試
        await asyncio.sleep(0.1)  # 模擬測試時間
        
        environment = context.metadata.get('environment', 'development')
        passed = environment != 'production' or context.metadata.get('security_reviewed', False)
        
        return {
            'test_type': 'security',
            'passed': passed,
            'message': '安全測試通過' if passed else '安全測試失敗',
            'details': '安全掃描完成' if passed else '需要安全審查'
        }
    
    async def _run_performance_tests(self, context: WorkflowContext) -> Dict[str, Any]:
        """運行性能測試"""
        # 模擬性能測試
        await asyncio.sleep(0.1)  # 模擬測試時間
        
        return {
            'test_type': 'performance',
            'passed': True,
            'message': '性能測試通過',
            'details': '響應時間在可接受範圍內'
        }

# API接口
class HumanLoopIntegrationAPI:
    """Human Loop Integration Tool API"""
    
    def __init__(self, tool: HumanLoopIntegrationTool):
        self.tool = tool
    
    async def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """創建工作流"""
        context = WorkflowContext(
            workflow_id=workflow_data.get('workflow_id', f"wf_{int(time.time())}"),
            title=workflow_data.get('title', ''),
            description=workflow_data.get('description', ''),
            parameters=workflow_data.get('parameters', {}),
            metadata=workflow_data.get('metadata', {}),
            created_at=datetime.now()
        )
        
        return await self.tool.process_workflow(context)
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """獲取工作流狀態"""
        conn = sqlite3.connect(self.tool.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM workflows WHERE id = ?
        ''', (workflow_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'workflow_id': result[0],
                'title': result[1],
                'description': result[2],
                'status': result[5],
                'decision_type': result[6],
                'created_at': result[7],
                'completed_at': result[8]
            }
        else:
            return {'error': 'Workflow not found'}
    
    async def get_decision_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """獲取決策歷史"""
        conn = sqlite3.connect(self.tool.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM decision_history 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': r[0],
                'workflow_id': r[1],
                'decision_type': r[2],
                'complexity_score': r[3],
                'risk_score': r[4],
                'confidence_score': r[5],
                'success': bool(r[6]),
                'execution_time': r[7],
                'created_at': r[8]
            }
            for r in results
        ]

# 主函數
async def main():
    """主函數 - 示例用法"""
    # 初始化工具
    tool = HumanLoopIntegrationTool()
    api = HumanLoopIntegrationAPI(tool)
    
    # 示例工作流
    workflow_data = {
        'workflow_id': 'test_deployment_001',
        'title': 'PowerAutomation VSIX部署',
        'description': '部署PowerAutomation Local MCP 3.0.0到VS Code',
        'parameters': {
            'target': 'vscode',
            'version': '3.0.0',
            'environment': 'production'
        },
        'metadata': {
            'workflow_type': 'deployment',
            'environment': 'production',
            'operation_type': 'deploy',
            'data_sensitivity': 'low',
            'system_impact': 'medium',
            'dependencies': ['vscode', 'python', 'mcp']
        }
    }
    
    # 處理工作流
    result = await api.create_workflow(workflow_data)
    print(f"工作流處理結果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 獲取決策歷史
    history = await api.get_decision_history(5)
    print(f"決策歷史: {json.dumps(history, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    asyncio.run(main())

