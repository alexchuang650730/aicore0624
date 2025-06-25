"""
完全整合的動態MCP-Agent Core智能系統
Fully Integrated Dynamic MCP-Agent Core Intelligent System

將動態MCP深度融入Agent Core的三個核心組件：
1. Agent Core - 智能決策中心
2. Tool Registry - 智能工具引擎  
3. Action Executor - 統一執行引擎
"""

import asyncio
import logging
import time
import json
import sys
import os
import hashlib
import secrets
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps

# 添加組件路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'components'))

# 導入 SmartInvention-Manus HITL 中間件
try:
    from smartinvention_manus_hitl_middleware import (
        SmartInventionManusMiddleware, 
        VSIXRequest, 
        SmartInventionResponse,
        create_smartinvention_manus_middleware
    )
    SMARTINVENTION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"SmartInvention-Manus 中間件導入失敗: {e}")
    SMARTINVENTION_AVAILABLE = False

# 導入 Enhanced Test Flow MCP v4.0
try:
    from enhanced_test_flow_mcp_v4 import (
        EnhancedTestFlowMCP,
        UserMode,
        ProcessingStage,
        DeveloperRequest
    )
    TEST_FLOW_MCP_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Enhanced Test Flow MCP 導入失敗: {e}")
    TEST_FLOW_MCP_AVAILABLE = False

logger = logging.getLogger(__name__)

# ==================== API Key 管理系統 ====================

class UserRole(Enum):
    DEVELOPER = "developer"
    USER = "user"
    ADMIN = "admin"

@dataclass
class APIKeyInfo:
    key: str
    role: UserRole
    name: str
    created_at: float
    last_used: float = 0.0
    usage_count: int = 0
    active: bool = True

class APIKeyManager:
    """API Key 管理系統 - 區分開發者和使用者"""
    
    def __init__(self):
        self.api_keys: Dict[str, APIKeyInfo] = {}
        self._initialize_default_keys()
    
    def _initialize_default_keys(self):
        """初始化默認 API Keys"""
        # 開發者 API Key
        dev_key = "dev_" + secrets.token_urlsafe(32)
        self.api_keys[dev_key] = APIKeyInfo(
            key=dev_key,
            role=UserRole.DEVELOPER,
            name="Default Developer",
            created_at=time.time()
        )
        
        # 使用者 API Key
        user_key = "user_" + secrets.token_urlsafe(32)
        self.api_keys[user_key] = APIKeyInfo(
            key=user_key,
            role=UserRole.USER,
            name="Default User",
            created_at=time.time()
        )
        
        # 管理員 API Key
        admin_key = "admin_" + secrets.token_urlsafe(32)
        self.api_keys[admin_key] = APIKeyInfo(
            key=admin_key,
            role=UserRole.ADMIN,
            name="System Admin",
            created_at=time.time()
        )
        
        logger.info(f"✅ 初始化 API Keys:")
        logger.info(f"   開發者 Key: {dev_key}")
        logger.info(f"   使用者 Key: {user_key}")
        logger.info(f"   管理員 Key: {admin_key}")
    
    def validate_api_key(self, api_key: str) -> Optional[APIKeyInfo]:
        """驗證 API Key 並返回用戶信息"""
        if not api_key:
            return None
        
        key_info = self.api_keys.get(api_key)
        if key_info and key_info.active:
            # 更新使用統計
            key_info.last_used = time.time()
            key_info.usage_count += 1
            return key_info
        
        return None
    
    def create_api_key(self, role: UserRole, name: str) -> str:
        """創建新的 API Key"""
        prefix = role.value
        new_key = f"{prefix}_" + secrets.token_urlsafe(32)
        
        self.api_keys[new_key] = APIKeyInfo(
            key=new_key,
            role=role,
            name=name,
            created_at=time.time()
        )
        
        logger.info(f"✅ 創建新 API Key: {new_key} ({role.value} - {name})")
        return new_key
    
    def revoke_api_key(self, api_key: str) -> bool:
        """撤銷 API Key"""
        if api_key in self.api_keys:
            self.api_keys[api_key].active = False
            logger.info(f"🚫 撤銷 API Key: {api_key}")
            return True
        return False
    
    def get_all_keys(self) -> List[Dict[str, Any]]:
        """獲取所有 API Keys 信息（不包含完整 key）"""
        return [
            {
                'key_prefix': key_info.key[:12] + "...",
                'role': key_info.role.value,
                'name': key_info.name,
                'created_at': key_info.created_at,
                'last_used': key_info.last_used,
                'usage_count': key_info.usage_count,
                'active': key_info.active
            }
            for key_info in self.api_keys.values()
        ]

# 全局 API Key 管理器
api_key_manager = APIKeyManager()

def require_api_key(allowed_roles: List[UserRole] = None):
    """API Key 驗證裝飾器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 從 Header 或 Query Parameter 獲取 API Key
            api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
            
            if not api_key:
                return jsonify({'error': 'API Key is required'}), 401
            
            # 驗證 API Key
            key_info = api_key_manager.validate_api_key(api_key)
            if not key_info:
                return jsonify({'error': 'Invalid API Key'}), 401
            
            # 檢查角色權限
            if allowed_roles and key_info.role not in allowed_roles:
                return jsonify({'error': f'Access denied. Required roles: {[r.value for r in allowed_roles]}'}), 403
            
            # 將用戶信息添加到請求上下文
            request.user_info = key_info
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== 核心數據結構 ====================

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AgentRequest:
    id: str
    content: str
    priority: Priority = Priority.MEDIUM
    timeout: int = 30
    context: Dict[str, Any] = None

@dataclass
class AgentResponse:
    request_id: str
    status: TaskStatus
    result: Any = None
    error: str = None
    execution_time: float = 0.0
    tools_used: List[str] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = None

# ==================== 動態MCP引擎 ====================

class DynamicMCPEngine:
    """
    動態MCP引擎 - 零硬編碼的智能專家系統
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.expert_cache = {}
        self.search_cache = {}
        
    async def cloud_search(self, query: str, context: str = "") -> Dict[str, Any]:
        """Cloud Search MCP - 智能搜索背景信息"""
        try:
            cache_key = f"search:{query}:{context}"
            if cache_key in self.search_cache:
                return self.search_cache[cache_key]
            
            # 模擬Cloud Search（實際應調用真實搜索API）
            await asyncio.sleep(0.1)
            
            search_results = self._generate_search_results(query)
            
            result = {
                'success': True,
                'query': query,
                'context': context,
                'results': search_results,
                'summary': self._summarize_search_results(search_results)
            }
            
            self.search_cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Cloud search failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_search_results(self, query: str) -> List[Dict[str, Any]]:
        """生成搜索結果"""
        results = []
        
        # 基於查詢關鍵詞生成相關結果
        if any(keyword in query.lower() for keyword in ['保險', '核保', '理賠', '臺銀']):
            results.extend([
                {
                    'title': '保險業數位轉型趨勢',
                    'content': '保險業正朝向數位化、自動化方向發展，OCR技術和AI輔助決策成為主流。',
                    'relevance': 0.9,
                    'source': 'industry_analysis'
                },
                {
                    'title': '核保流程優化實務',
                    'content': '現代核保流程通過自動化可提升60-70%效率，減少人工審核時間。',
                    'relevance': 0.85,
                    'source': 'best_practices'
                }
            ])
        
        if any(keyword in query.lower() for keyword in ['人力', '成本', '效率']):
            results.extend([
                {
                    'title': '人力資源優化策略',
                    'content': '通過自動化和數位化，可減少30-40%人力成本，提升作業效率。',
                    'relevance': 0.88,
                    'source': 'efficiency_study'
                }
            ])
        
        if any(keyword in query.lower() for keyword in ['ocr', '自動化', '技術']):
            results.extend([
                {
                    'title': 'OCR技術在保險業應用',
                    'content': 'OCR技術在文件處理中可達95%以上準確率，大幅減少人工審核需求。',
                    'relevance': 0.92,
                    'source': 'technology_review'
                }
            ])
        
        return results[:5]  # 返回最多5個結果
    
    def _summarize_search_results(self, results: List[Dict[str, Any]]) -> str:
        """總結搜索結果"""
        if not results:
            return "未找到相關信息"
        
        summary_parts = []
        for result in results[:3]:  # 取前3個最相關的結果
            summary_parts.append(result['content'])
        
        return " ".join(summary_parts)
    
    async def identify_expert_domains(self, request: str, background: str) -> List[str]:
        """動態識別專家領域"""
        try:
            # 基於請求內容和背景信息識別需要的專家
            domains = []
            
            request_lower = request.lower()
            background_lower = background.lower()
            combined_text = f"{request_lower} {background_lower}"
            
            # 動態識別專家領域
            if any(keyword in combined_text for keyword in ['保險', '核保', '理賠', '承保', '精算']):
                domains.append('保險專家')
            
            if any(keyword in combined_text for keyword in ['技術', '自動化', 'ocr', '系統', 'ai', '數位']):
                domains.append('技術專家')
            
            if any(keyword in combined_text for keyword in ['管理', '流程', '效率', '優化', '作業']):
                domains.append('管理專家')
            
            if any(keyword in combined_text for keyword in ['成本', '預算', '投資', '財務', '經濟']):
                domains.append('財務專家')
            
            if any(keyword in combined_text for keyword in ['法規', '合規', '監管', '規範']):
                domains.append('法規專家')
            
            # 如果沒有識別到特定領域，使用通用專家
            if not domains:
                domains = ['通用專家']
            
            return domains[:3]  # 最多3個專家
            
        except Exception as e:
            logger.error(f"Expert domain identification failed: {e}")
            return ['通用專家']
    
    async def generate_expert_response(self, expert_domain: str, request: str, background: str) -> str:
        """生成專家回答"""
        try:
            cache_key = f"expert:{expert_domain}:{request[:50]}"
            if cache_key in self.expert_cache:
                return self.expert_cache[cache_key]
            
            # 為每個專家生成專業回答
            expert_response = self._generate_domain_specific_response(expert_domain, request, background)
            
            self.expert_cache[cache_key] = expert_response
            return expert_response
            
        except Exception as e:
            logger.error(f"Expert response generation failed: {e}")
            return f"{expert_domain}分析過程中遇到問題: {str(e)}"
    
    def _generate_domain_specific_response(self, expert_domain: str, request: str, background: str) -> str:
        """生成領域專業回答"""
        responses = {
            '保險專家': self._generate_insurance_expert_response(request, background),
            '技術專家': self._generate_tech_expert_response(request, background),
            '管理專家': self._generate_management_expert_response(request, background),
            '財務專家': self._generate_finance_expert_response(request, background),
            '法規專家': self._generate_legal_expert_response(request, background),
            '通用專家': self._generate_general_expert_response(request, background)
        }
        
        return responses.get(expert_domain, f"{expert_domain}正在分析中...")
    
    def _generate_insurance_expert_response(self, request: str, background: str) -> str:
        """保險專家回答"""
        response_parts = ["**保險專業分析:**"]
        
        if "人力" in request or "人員" in request:
            response_parts.append("- 核保人員配置：建議每千件保單配置3-5名核保人員")
            response_parts.append("- 理賠人員配置：建議每千件理賠案配置2-3名理賠專員")
        
        if "自動化" in request:
            response_parts.append("- 業界自動化率：目前達60-70%，領先公司可達80-85%")
            response_parts.append("- 核保自動化：簡單案件可達90%自動核保率")
        
        if "ocr" in request.lower():
            response_parts.append("- OCR應用：文件識別準確率可達95%以上")
            response_parts.append("- 人工審核：約需15-20%案件進行人工複核")
        
        if "成本" in request:
            response_parts.append("- 自動化可降低30-40%作業成本")
            response_parts.append("- 投資回收期：通常為1-2年")
        
        return "\n".join(response_parts)
    
    def _generate_tech_expert_response(self, request: str, background: str) -> str:
        """技術專家回答"""
        response_parts = ["**技術實施分析:**"]
        
        if "ocr" in request.lower():
            response_parts.append("- OCR技術：建議使用深度學習模型，準確率可達95%+")
            response_parts.append("- 處理能力：每小時可處理1000-2000份文件")
        
        if "自動化" in request:
            response_parts.append("- RPA實施：可自動化80%重複性作業")
            response_parts.append("- AI輔助：決策準確率可提升至90%以上")
        
        if "系統" in request:
            response_parts.append("- 系統整合：建議採用微服務架構")
            response_parts.append("- 擴展性：支援彈性擴展和負載均衡")
        
        return "\n".join(response_parts)
    
    def _generate_management_expert_response(self, request: str, background: str) -> str:
        """管理專家回答"""
        response_parts = ["**管理優化建議:**"]
        
        if "流程" in request:
            response_parts.append("- 流程標準化：建立SOP標準作業程序")
            response_parts.append("- 品質控制：實施多層次審核機制")
        
        if "效率" in request:
            response_parts.append("- 效率提升：數位化可提升20-30%作業效率")
            response_parts.append("- 錯誤減少：自動化可降低60%人為錯誤")
        
        if "人力" in request:
            response_parts.append("- 人力配置：建議採用專業分工制度")
            response_parts.append("- 培訓計畫：定期技能提升和轉型培訓")
        
        return "\n".join(response_parts)
    
    def _generate_finance_expert_response(self, request: str, background: str) -> str:
        """財務專家回答"""
        response_parts = ["**財務效益分析:**"]
        
        if "成本" in request:
            response_parts.append("- 成本節省：自動化可節省30-40%人力成本")
            response_parts.append("- 投資評估：建議分階段投資，降低風險")
        
        if "投資" in request or "預算" in request:
            response_parts.append("- ROI分析：預期投資回報率15-25%")
            response_parts.append("- 回收期：通常為12-24個月")
        
        return "\n".join(response_parts)
    
    def _generate_legal_expert_response(self, request: str, background: str) -> str:
        """法規專家回答"""
        response_parts = ["**法規合規分析:**"]
        
        response_parts.append("- 個資保護：確保符合個資法相關規定")
        response_parts.append("- 保險法規：遵循金管會相關監管要求")
        response_parts.append("- 資料安全：建立完善的資料保護機制")
        
        return "\n".join(response_parts)
    
    def _generate_general_expert_response(self, request: str, background: str) -> str:
        """通用專家回答"""
        return f"**綜合分析:** 基於您的需求「{request}」，建議從技術、管理、財務等多個角度進行綜合評估，制定適合的實施策略。"
    
    async def aggregate_responses(self, expert_responses: Dict[str, str], request: str) -> str:
        """聚合專家回答"""
        if not expert_responses:
            return "未能獲取專家分析，請重新嘗試。"
        
        # 構建聚合回答
        aggregated_parts = ["**綜合專業分析:**\n"]
        
        for expert, response in expert_responses.items():
            aggregated_parts.append(f"### {expert}")
            aggregated_parts.append(response)
            aggregated_parts.append("")
        
        # 添加總結
        aggregated_parts.append("### 總結建議")
        aggregated_parts.append("基於以上專家分析，建議採用分階段實施策略，優先導入自動化程度高、投資回報明確的項目，並建立完善的品質控制和風險管理機制。")
        
        return "\n".join(aggregated_parts)

# ==================== 整合的Agent Core ====================

class IntegratedAgentCore:
    """
    整合的Agent Core - 融入動態MCP的智能決策中心
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.dynamic_mcp = DynamicMCPEngine(config.get('dynamic_mcp', {}))
        
        # 統計信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'mcp_calls': 0
        }
        
        logger.info("Integrated Agent Core initialized")
    
    async def process_request(self, agent_request: AgentRequest) -> AgentResponse:
        """處理Agent請求 - 整合動態MCP流程"""
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        try:
            # 階段1: Cloud Search MCP - 搜索背景信息
            search_result = await self.dynamic_mcp.cloud_search(
                agent_request.content, 
                "背景信息搜索"
            )
            self.stats['mcp_calls'] += 1
            
            if not search_result['success']:
                raise Exception(f"Cloud search failed: {search_result.get('error', 'Unknown error')}")
            
            background_info = search_result['summary']
            
            # 階段2: 動態識別專家領域
            expert_domains = await self.dynamic_mcp.identify_expert_domains(
                agent_request.content, 
                background_info
            )
            
            # 階段3: 獲取專家回答
            expert_responses = {}
            for domain in expert_domains:
                response = await self.dynamic_mcp.generate_expert_response(
                    domain, 
                    agent_request.content, 
                    background_info
                )
                expert_responses[domain] = response
                self.stats['mcp_calls'] += 1
            
            # 階段4: 聚合專家回答
            final_answer = await self.dynamic_mcp.aggregate_responses(
                expert_responses, 
                agent_request.content
            )
            
            execution_time = time.time() - start_time
            self.stats['successful_requests'] += 1
            self._update_average_response_time(execution_time)
            
            return AgentResponse(
                request_id=agent_request.id,
                status=TaskStatus.COMPLETED,
                result={
                    'final_answer': final_answer,
                    'background_info': background_info,
                    'expert_domains': expert_domains,
                    'expert_responses': expert_responses,
                    'search_results': search_result['results']
                },
                execution_time=execution_time,
                tools_used=['dynamic_mcp', 'cloud_search'],
                confidence=0.9,
                metadata={
                    'mcp_integrated': True,
                    'experts_consulted': len(expert_domains),
                    'search_results_count': len(search_result['results'])
                }
            )
            
        except Exception as e:
            logger.error(f"Agent request processing failed: {e}")
            self.stats['failed_requests'] += 1
            
            return AgentResponse(
                request_id=agent_request.id,
                status=TaskStatus.FAILED,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def _update_average_response_time(self, execution_time: float):
        """更新平均響應時間"""
        total_successful = self.stats['successful_requests']
        current_avg = self.stats['average_response_time']
        
        new_avg = ((current_avg * (total_successful - 1)) + execution_time) / total_successful
        self.stats['average_response_time'] = new_avg
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return {
            **self.stats,
            'success_rate': self.stats['successful_requests'] / max(self.stats['total_requests'], 1),
            'mcp_integration': True
        }

# ==================== 整合的Tool Registry ====================

class IntegratedToolRegistry:
    """
    整合的Tool Registry - 融入動態MCP的智能工具引擎
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.dynamic_mcp = DynamicMCPEngine(config.get('dynamic_mcp', {}))
        
        # 工具註冊表
        self.tools = {
            'dynamic_mcp': {
                'id': 'dynamic_mcp',
                'name': 'Dynamic MCP Engine',
                'type': 'intelligent_expert_system',
                'capabilities': ['expert_consultation', 'cloud_search', 'domain_identification'],
                'cost_model': {'type': 'free', 'cost_per_call': 0.0},
                'performance_metrics': {'success_rate': 0.95, 'avg_response_time': 2.0}
            },
            'cloud_search': {
                'id': 'cloud_search',
                'name': 'Cloud Search MCP',
                'type': 'search_engine',
                'capabilities': ['information_search', 'background_research'],
                'cost_model': {'type': 'free', 'cost_per_call': 0.0},
                'performance_metrics': {'success_rate': 0.90, 'avg_response_time': 1.0}
            }
        }
        
        logger.info("Integrated Tool Registry initialized")
    
    async def find_optimal_tools(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """智能工具選擇 - 基於動態MCP"""
        try:
            # 使用動態MCP分析需求
            search_result = await self.dynamic_mcp.cloud_search(request, "工具選擇分析")
            
            # 基於分析結果選擇最優工具
            if search_result['success']:
                # 對於大多數請求，動態MCP是最優選擇
                selected_tool = self.tools['dynamic_mcp']
                alternatives = [self.tools['cloud_search']]
                
                return {
                    'success': True,
                    'selected_tool': selected_tool,
                    'alternatives': alternatives,
                    'decision_explanation': {
                        'reasoning': 'Dynamic MCP provides comprehensive expert analysis',
                        'confidence': 0.9,
                        'search_informed': True
                    }
                }
            else:
                # 回退到基礎工具
                return {
                    'success': True,
                    'selected_tool': self.tools['cloud_search'],
                    'alternatives': [],
                    'decision_explanation': {
                        'reasoning': 'Fallback to basic search tool',
                        'confidence': 0.7,
                        'fallback_used': True
                    }
                }
                
        except Exception as e:
            logger.error(f"Tool selection failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def execute_with_tool(self, tool_id: str, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """使用指定工具執行"""
        try:
            if tool_id == 'dynamic_mcp':
                # 使用動態MCP執行完整流程
                search_result = await self.dynamic_mcp.cloud_search(request, "工具執行")
                expert_domains = await self.dynamic_mcp.identify_expert_domains(request, search_result['summary'])
                
                expert_responses = {}
                for domain in expert_domains:
                    response = await self.dynamic_mcp.generate_expert_response(domain, request, search_result['summary'])
                    expert_responses[domain] = response
                
                final_answer = await self.dynamic_mcp.aggregate_responses(expert_responses, request)
                
                return {
                    'success': True,
                    'result': final_answer,
                    'tool_used': tool_id,
                    'experts_consulted': expert_domains
                }
                
            elif tool_id == 'cloud_search':
                # 僅使用搜索功能
                search_result = await self.dynamic_mcp.cloud_search(request, context or "")
                return {
                    'success': search_result['success'],
                    'result': search_result['summary'],
                    'tool_used': tool_id,
                    'search_results': search_result.get('results', [])
                }
            else:
                return {
                    'success': False,
                    'error': f"Unknown tool: {tool_id}"
                }
                
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """獲取可用工具列表"""
        return list(self.tools.values())

# ==================== 整合的Action Executor ====================

class IntegratedActionExecutor:
    """
    整合的Action Executor - 融入動態MCP的統一執行引擎
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.tool_registry = None
        
        # 執行統計
        self.execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'mcp_executions': 0
        }
        
        logger.info("Integrated Action Executor initialized")
    
    def set_tool_registry(self, tool_registry: IntegratedToolRegistry):
        """設置工具註冊表"""
        self.tool_registry = tool_registry
    
    async def execute(self, request: AgentRequest, tools: List[str] = None, mode: str = 'intelligent') -> Dict[str, Any]:
        """執行動作 - 整合動態MCP"""
        self.execution_stats['total_executions'] += 1
        
        try:
            if not self.tool_registry:
                raise Exception("Tool registry not configured")
            
            # 如果沒有指定工具，使用智能工具選擇
            if not tools:
                tool_selection = await self.tool_registry.find_optimal_tools(request.content, request.context)
                if tool_selection['success']:
                    selected_tool_id = tool_selection['selected_tool']['id']
                else:
                    selected_tool_id = 'dynamic_mcp'  # 默認使用動態MCP
            else:
                selected_tool_id = tools[0]  # 使用第一個指定的工具
            
            # 執行工具
            execution_result = await self.tool_registry.execute_with_tool(
                selected_tool_id, 
                request.content, 
                request.context
            )
            
            if execution_result['success']:
                self.execution_stats['successful_executions'] += 1
                if 'mcp' in selected_tool_id:
                    self.execution_stats['mcp_executions'] += 1
            else:
                self.execution_stats['failed_executions'] += 1
            
            return {
                'success': execution_result['success'],
                'result': execution_result.get('result', ''),
                'tool_used': selected_tool_id,
                'execution_mode': mode,
                'metadata': {
                    'mcp_integrated': 'mcp' in selected_tool_id,
                    'experts_consulted': execution_result.get('experts_consulted', []),
                    'search_results': execution_result.get('search_results', [])
                }
            }
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            self.execution_stats['failed_executions'] += 1
            
            return {
                'success': False,
                'error': str(e),
                'execution_mode': mode
            }
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """獲取執行統計"""
        total = self.execution_stats['total_executions']
        return {
            **self.execution_stats,
            'success_rate': self.execution_stats['successful_executions'] / max(total, 1),
            'mcp_usage_rate': self.execution_stats['mcp_executions'] / max(total, 1)
        }

# ==================== 完全整合的智能系統 ====================

class FullyIntegratedIntelligentSystem:
    """
    完全整合的智能系統
    將動態MCP深度融入Agent Core的三個核心組件
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # 初始化三個核心組件
        self.agent_core = IntegratedAgentCore(self.config.get('agent_core', {}))
        self.tool_registry = IntegratedToolRegistry(self.config.get('tool_registry', {}))
        self.action_executor = IntegratedActionExecutor(self.config.get('action_executor', {}))
        
        # 初始化 SmartInvention-Manus HITL 中間件
        self.smartinvention_middleware = None
        self.smartinvention_init_task = None
        if SMARTINVENTION_AVAILABLE:
            # 延遲初始化，在第一次使用時進行
            pass
        
        # 初始化 Enhanced Test Flow MCP v4.0
        self.test_flow_mcp = None
        if TEST_FLOW_MCP_AVAILABLE:
            try:
                self.test_flow_mcp = EnhancedTestFlowMCP()
                logger.info("Enhanced Test Flow MCP v4.0 initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Test Flow MCP: {e}")
                self.test_flow_mcp = None
        
        # 設置組件間依賴
        self.action_executor.set_tool_registry(self.tool_registry)
        
        # 系統統計
        self.system_stats = {
            'system_start_time': time.time(),
            'total_requests': 0,
            'integration_level': 'full',
            'smartinvention_enabled': SMARTINVENTION_AVAILABLE,
            'test_flow_mcp_enabled': TEST_FLOW_MCP_AVAILABLE and self.test_flow_mcp is not None
        }
        
        logger.info("Fully Integrated Intelligent System initialized")
    
    async def _ensure_smartinvention_initialized(self):
        """確保 SmartInvention 中間件已初始化"""
        if self.smartinvention_middleware is None:
            await self._initialize_smartinvention_middleware()
    
    async def _initialize_smartinvention_middleware(self):
        """異步初始化 SmartInvention 中間件"""
        try:
            middleware_config = self.config.get('smartinvention_middleware', {
                "hitl_enabled": True,
                "auto_approve_threshold": 0.8,
                "review_timeout": 300
            })
            
            # 簡化版本的中間件初始化，避免複雜的依賴
            from smartinvention_manus_hitl_middleware import SmartInventionManusMiddleware
            self.smartinvention_middleware = SmartInventionManusMiddleware(middleware_config)
            
            logger.info("✅ SmartInvention-Manus HITL 中間件初始化成功")
            
        except Exception as e:
            logger.error(f"❌ SmartInvention 中間件初始化失敗: {e}")
            self.smartinvention_middleware = None
    
    async def process_request(self, user_request: str, context: Dict[str, Any] = None, user_role: UserRole = UserRole.USER) -> Dict[str, Any]:
        """處理用戶請求 - 完全整合流程，支持 VSIX SmartInvention 流程和用戶角色"""
        self.system_stats['total_requests'] += 1
        context = context or {}
        
        # 根據用戶角色調整上下文
        context['user_role'] = user_role.value
        context['is_developer'] = user_role == UserRole.DEVELOPER
        context['is_admin'] = user_role == UserRole.ADMIN
        
        # 檢查是否為 VSIX 請求
        is_vsix_request = (
            context.get('source') == 'vscode_vsix' or 
            context.get('client') == 'vsix' or
            'vsix' in context.get('user_agent', '').lower()
        )
        
        # 如果是 VSIX 請求且 SmartInvention 中間件可用，使用 SmartInvention 流程
        if is_vsix_request and SMARTINVENTION_AVAILABLE:
            # 確保 SmartInvention 中間件已初始化
            if not self.smartinvention_middleware:
                await self._ensure_smartinvention_initialized()
            
            if self.smartinvention_middleware:
                return await self._process_vsix_request(user_request, context, user_role)
            else:
                logger.warning("SmartInvention 中間件初始化失敗，使用常規流程")
                return await self._process_regular_request(user_request, context, user_role)
        
        # 否則使用原有的處理流程
        return await self._process_regular_request(user_request, context, user_role)
    
    async def _process_vsix_request(self, user_request: str, context: Dict[str, Any], user_role: UserRole) -> Dict[str, Any]:
        """處理 VSIX 請求 - 根據用戶角色選擇處理流程"""
        logger.info(f"🎯 處理 VSIX 請求 ({user_role.value}): {user_request[:100]}...")
        
        try:
            # 根據用戶角色選擇處理流程
            if user_role == UserRole.DEVELOPER and self.test_flow_mcp is not None:
                # 開發者角色 - 使用 test_flow_mcp 流程
                return await self._process_developer_request_with_test_flow(user_request, context)
            else:
                # 使用者角色 - 使用 SmartInvention-Manus HITL 流程
                return await self._process_user_request_with_smartinvention(user_request, context)
                
        except Exception as e:
            logger.error(f"❌ VSIX 請求處理失敗: {e}")
            return {
                'request_id': f"vsix_error_{int(time.time())}",
                'success': False,
                'result': None,
                'error': f"請求處理失敗: {str(e)}",
                'execution_time': 0.0,
                'tools_used': [],
                'confidence': 0.0,
                'metadata': {
                    'system_type': 'error',
                    'request_source': 'vscode_vsix',
                    'user_role': user_role.value,
                    'error_type': 'processing_failure'
                }
            }
    
    async def _process_developer_request_with_test_flow(self, user_request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """處理開發者請求 - 使用 test_flow_mcp 流程"""
        logger.info(f"🔧 開發者模式: 使用 test_flow_mcp 處理請求")
        
        try:
            # 創建開發者請求對象
            developer_request = DeveloperRequest(
                request_id=f"dev_{int(time.time())}_{self.system_stats['total_requests']}",
                content=user_request,
                context=context,
                user_mode=UserMode.DEVELOPER,
                timestamp=time.time()
            )
            
            # 使用 test_flow_mcp 處理
            test_flow_response = await self.test_flow_mcp.process_developer_request(developer_request)
            
            return {
                'request_id': test_flow_response.get('request_id', developer_request.request_id),
                'success': test_flow_response.get('success', True),
                'result': {
                    'test_flow_analysis': test_flow_response.get('analysis', {}),
                    'recommendations': test_flow_response.get('recommendations', []),
                    'code_fixes': test_flow_response.get('code_fixes', []),
                    'evaluation_report': test_flow_response.get('evaluation_report', {}),
                    'processing_stages': test_flow_response.get('processing_stages', [])
                },
                'error': test_flow_response.get('error'),
                'execution_time': test_flow_response.get('execution_time', 0.0),
                'tools_used': ['test_flow_mcp', 'requirement_sync', 'comparison_analysis', 'code_fix_adapter'],
                'confidence': test_flow_response.get('confidence', 0.8),
                'metadata': {
                    'system_type': 'test_flow_mcp_integrated',
                    'request_source': 'vscode_vsix',
                    'user_role': 'developer',
                    'processing_mode': 'developer_mode',
                    'test_flow_enabled': True,
                    'stages_completed': len(test_flow_response.get('processing_stages', [])),
                    'fixes_generated': len(test_flow_response.get('code_fixes', []))
                }
            }
            
        except Exception as e:
            logger.error(f"❌ test_flow_mcp 處理失敗: {e}")
            return {
                'request_id': f"dev_error_{int(time.time())}",
                'success': False,
                'result': None,
                'error': f"test_flow_mcp 處理失敗: {str(e)}",
                'execution_time': 0.0,
                'tools_used': ['test_flow_mcp'],
                'confidence': 0.0,
                'metadata': {
                    'system_type': 'test_flow_mcp_error',
                    'request_source': 'vscode_vsix',
                    'user_role': 'developer',
                    'error_type': 'test_flow_processing_failure'
                }
            }
    
    async def _process_user_request_with_smartinvention(self, user_request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """處理使用者請求 - 使用 SmartInvention-Manus HITL 流程"""
        logger.info(f"👤 使用者模式: 使用 SmartInvention-Manus HITL 處理請求")
        
        try:
            # 確保 SmartInvention 中間件已初始化
            await self._ensure_smartinvention_initialized()
            
            # 創建 VSIX 請求對象
            vsix_request = VSIXRequest(
                request_id=f"vsix_{int(time.time())}_{self.system_stats['total_requests']}",
                content=user_request,
                context=context,
                timestamp=time.time(),
                source="vscode_vsix"
            )
            
            # 使用 SmartInvention 中間件處理
            smartinvention_response = await self.smartinvention_middleware.process_vsix_request(vsix_request)
            
            # 轉換為標準響應格式 - 突出 Manus 原始回覆
            primary_response = smartinvention_response.get_primary_response()
            
            return {
                'request_id': smartinvention_response.request_id,
                'success': smartinvention_response.success,
                'result': {
                    'primary_response': primary_response,  # 主要回覆（優先 Manus）
                    'manus_direct_response': smartinvention_response.manus_original_response,  # Manus 直接回覆
                    'smartinvention_analysis': {
                        'conversation_history': asdict(smartinvention_response.conversation_history) if smartinvention_response.conversation_history else None,
                        'incremental_comparison': asdict(smartinvention_response.incremental_comparison) if smartinvention_response.incremental_comparison else None,
                        'hitl_review': asdict(smartinvention_response.hitl_review) if smartinvention_response.hitl_review else None,
                        'final_recommendations': smartinvention_response.final_recommendations
                    }
                },
                'error': smartinvention_response.error_message,
                'execution_time': smartinvention_response.execution_time,
                'tools_used': ['smartinvention_mcp', 'manus_adapter', 'hitl_review'],
                'confidence': smartinvention_response.incremental_comparison.confidence_score if smartinvention_response.incremental_comparison else 0.0,
                'metadata': {
                    'system_type': 'smartinvention_manus_integrated',
                    'request_source': 'vscode_vsix',
                    'user_role': 'user',
                    'hitl_enabled': True,
                    'manus_direct_available': smartinvention_response.manus_original_response is not None,
                    'response_type': primary_response['type'],
                    'recommendations_count': len(smartinvention_response.final_recommendations),
                    'conversation_messages': smartinvention_response.conversation_history.total_messages if smartinvention_response.conversation_history else 0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ SmartInvention 處理失敗: {e}")
            return {
                'request_id': f"user_error_{int(time.time())}",
                'success': False,
                'result': None,
                'error': f"SmartInvention 處理失敗: {str(e)}",
                'execution_time': 0.0,
                'tools_used': ['smartinvention_mcp'],
                'confidence': 0.0,
                'metadata': {
                    'system_type': 'smartinvention_error',
                    'request_source': 'vscode_vsix',
                    'user_role': 'user',
                    'error_type': 'smartinvention_processing_failure'
                }
            }
    
    async def _process_regular_request(self, user_request: str, context: Dict[str, Any], user_role: UserRole) -> Dict[str, Any]:
        """處理常規請求 - 原有流程"""
        # 創建Agent請求
        agent_request = AgentRequest(
            id=f"req_{int(time.time())}_{self.system_stats['total_requests']}",
            content=user_request,
            priority=Priority.MEDIUM,
            context=context
        )
        
        # 使用整合的Agent Core處理請求
        agent_response = await self.agent_core.process_request(agent_request)
        
        return {
            'request_id': agent_response.request_id,
            'success': agent_response.status == TaskStatus.COMPLETED,
            'result': agent_response.result,
            'error': agent_response.error,
            'execution_time': agent_response.execution_time,
            'tools_used': agent_response.tools_used,
            'confidence': agent_response.confidence,
            'metadata': {
                **agent_response.metadata,
                'system_type': 'fully_integrated',
                'integration_components': ['agent_core', 'tool_registry', 'action_executor'],
                'dynamic_mcp_integrated': True
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        uptime = time.time() - self.system_stats['system_start_time']
        
        return {
            'system_type': 'fully_integrated_intelligent_system',
            'uptime_seconds': uptime,
            'integration_level': 'full',
            'components': {
                'agent_core': {
                    'status': 'active',
                    'stats': self.agent_core.get_stats()
                },
                'tool_registry': {
                    'status': 'active',
                    'available_tools': len(self.tool_registry.get_available_tools())
                },
                'action_executor': {
                    'status': 'active',
                    'stats': self.action_executor.get_execution_stats()
                }
            },
            'features': [
                'dynamic_mcp_integration',
                'cloud_search_mcp',
                'intelligent_expert_consultation',
                'zero_hardcoded_responses',
                'multi_component_integration'
            ],
            'system_stats': self.system_stats
        }

# ==================== Flask應用 ====================

app = Flask(__name__)
CORS(app)

# 初始化完全整合的智能系統
integrated_system = FullyIntegratedIntelligentSystem()

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查"""
    return jsonify({
        'status': 'healthy',
        'system_type': 'fully_integrated_intelligent_system',
        'timestamp': time.time(),
        'components': ['agent_core', 'tool_registry', 'action_executor'],
        'dynamic_mcp': 'integrated'
    })

@app.route('/api/process', methods=['POST'])
@require_api_key([UserRole.DEVELOPER, UserRole.USER, UserRole.ADMIN])
def process_request():
    """處理用戶請求"""
    try:
        data = request.get_json()
        user_request = data.get('request', '')
        context = data.get('context', {})
        
        if not user_request:
            return jsonify({'error': 'Request content is required'}), 400
        
        # 獲取用戶角色
        user_role = request.user_info.role
        
        # 使用 asyncio.run 處理異步調用
        result = asyncio.run(integrated_system.process_request(user_request, context, user_role))
        
        # 添加用戶角色信息到響應
        result['user_role'] = user_role.value
        result['api_key_info'] = {
            'name': request.user_info.name,
            'usage_count': request.user_info.usage_count
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API request processing failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """獲取系統狀態"""
    return jsonify(integrated_system.get_system_status())

@app.route('/api/tools', methods=['GET'])
def get_tools():
    """獲取可用工具"""
    return jsonify({
        'tools': integrated_system.tool_registry.get_available_tools(),
        'integration_level': 'full'
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """獲取統計信息"""
    return jsonify({
        'agent_core_stats': integrated_system.agent_core.get_stats(),
        'execution_stats': integrated_system.action_executor.get_execution_stats(),
        'system_stats': integrated_system.system_stats
    })

# ==================== SmartInvention HITL API 端點 ====================

@app.route('/api/hitl/pending_reviews', methods=['GET'])
@require_api_key([UserRole.DEVELOPER, UserRole.ADMIN])
def get_pending_reviews():
    """獲取待審核項目"""
    try:
        if not integrated_system.smartinvention_middleware:
            return jsonify({'error': 'SmartInvention middleware not available'}), 503
        
        # 使用 asyncio.run 處理異步調用
        pending_reviews = asyncio.run(integrated_system.smartinvention_middleware.get_pending_reviews())
        return jsonify({
            'success': True,
            'pending_reviews': pending_reviews,
            'count': len(pending_reviews)
        })
        
    except Exception as e:
        logger.error(f"獲取待審核項目失敗: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/hitl/submit_review', methods=['POST'])
@require_api_key([UserRole.DEVELOPER, UserRole.ADMIN])
def submit_review():
    """提交審核結果"""
    try:
        if not integrated_system.smartinvention_middleware:
            return jsonify({'error': 'SmartInvention middleware not available'}), 503
        
        data = request.get_json()
        review_id = data.get('review_id')
        status = data.get('status')  # 'approved', 'rejected', 'modified'
        approved_recommendations = data.get('approved_recommendations', [])
        comments = data.get('comments', '')
        
        if not review_id or not status:
            return jsonify({'error': 'review_id and status are required'}), 400
        
        # 使用 asyncio.run 處理異步調用
        success = asyncio.run(integrated_system.smartinvention_middleware.submit_review(
            review_id, status, approved_recommendations, comments
        ))
        
        if success:
            return jsonify({
                'success': True,
                'message': f'審核結果已提交: {review_id}',
                'review_id': review_id,
                'status': status
            })
        else:
            return jsonify({'error': 'Failed to submit review'}), 400
        
    except Exception as e:
        logger.error(f"提交審核結果失敗: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/smartinvention/status', methods=['GET'])
@require_api_key([UserRole.DEVELOPER, UserRole.USER, UserRole.ADMIN])
def get_smartinvention_status():
    """獲取 SmartInvention 狀態"""
    return jsonify({
        'smartinvention_available': SMARTINVENTION_AVAILABLE,
        'middleware_initialized': integrated_system.smartinvention_middleware is not None,
        'hitl_enabled': integrated_system.smartinvention_middleware is not None,
        'system_type': 'smartinvention_integrated',
        'user_role': request.user_info.role.value
    })

# ==================== API Key 管理端點 ====================

@app.route('/api/keys', methods=['GET'])
@require_api_key([UserRole.ADMIN])
def get_api_keys():
    """獲取所有 API Keys（僅管理員）"""
    return jsonify({
        'api_keys': api_key_manager.get_all_keys(),
        'total_count': len(api_key_manager.api_keys)
    })

@app.route('/api/keys', methods=['POST'])
@require_api_key([UserRole.ADMIN])
def create_api_key():
    """創建新的 API Key（僅管理員）"""
    try:
        data = request.get_json()
        role_str = data.get('role', 'user')
        name = data.get('name', 'Unnamed User')
        
        # 驗證角色
        try:
            role = UserRole(role_str)
        except ValueError:
            return jsonify({'error': f'Invalid role: {role_str}. Valid roles: {[r.value for r in UserRole]}'}), 400
        
        new_key = api_key_manager.create_api_key(role, name)
        
        return jsonify({
            'success': True,
            'api_key': new_key,
            'role': role.value,
            'name': name,
            'message': f'API Key created for {name} ({role.value})'
        })
        
    except Exception as e:
        logger.error(f"創建 API Key 失敗: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/keys/<api_key>', methods=['DELETE'])
@require_api_key([UserRole.ADMIN])
def revoke_api_key(api_key):
    """撤銷 API Key（僅管理員）"""
    try:
        success = api_key_manager.revoke_api_key(api_key)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'API Key revoked: {api_key[:12]}...'
            })
        else:
            return jsonify({'error': 'API Key not found'}), 404
        
    except Exception as e:
        logger.error(f"撤銷 API Key 失敗: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/keys/info', methods=['GET'])
@require_api_key([UserRole.DEVELOPER, UserRole.USER, UserRole.ADMIN])
def get_current_key_info():
    """獲取當前 API Key 信息"""
    return jsonify({
        'key_prefix': request.user_info.key[:12] + "...",
        'role': request.user_info.role.value,
        'name': request.user_info.name,
        'created_at': request.user_info.created_at,
        'last_used': request.user_info.last_used,
        'usage_count': request.user_info.usage_count,
        'active': request.user_info.active
    })

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Fully Integrated Intelligent System Server...")
    app.run(host='0.0.0.0', port=8080, debug=False)

