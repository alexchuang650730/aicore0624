#!/usr/bin/env python3
"""
SmartInvention MCP 與 Claude Code Enhanced Context Manager 集成適配器
保持向後兼容性，同時提供 Claude Code 增強功能
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from claude_code_enhanced_context_manager import (
    ClaudeCodeEnhancedContextManager, 
    ServiceType, 
    ContextScope
)

logger = logging.getLogger(__name__)

class SmartInventionClaudeCodeAdapter:
    """SmartInvention MCP 與 Claude Code 的集成適配器"""
    
    def __init__(self, claude_api_key: Optional[str] = None):
        self.context_manager = ClaudeCodeEnhancedContextManager(
            claude_api_key=claude_api_key
        )
        self.service_mappings = {
            "smart_routing": ServiceType.SMART_ROUTING,
            "code_generation": ServiceType.CODE_GENERATION,
            "code_analysis": ServiceType.CODE_ANALYSIS,
            "test_flow": ServiceType.TEST_FLOW,
            "requirement_analysis": ServiceType.REQUIREMENT_ANALYSIS
        }
    
    async def process_smartinvention_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """處理 SmartInvention MCP 請求"""
        
        try:
            # 解析請求
            request_type = request.get("request_type", "smart_routing")
            content = request.get("content", "")
            session_id = request.get("session_id")
            context_data = request.get("context", {})
            
            # 映射服務類型
            service_type = self.service_mappings.get(request_type, ServiceType.SMART_ROUTING)
            
            # 添加上下文
            context_id = await self.context_manager.add_context(
                content=content,
                service_type=service_type,
                session_id=session_id,
                metadata=context_data
            )
            
            # 獲取增強上下文
            enhanced_context = await self.context_manager.get_context(
                service_type=service_type,
                session_id=session_id,
                include_history=context_data.get("include_history", True),
                include_project_context=context_data.get("include_project_context", True)
            )
            
            # 構建響應 (兼容 SmartInvention MCP 格式)
            response = {
                "request_id": request.get("request_id", context_id),
                "status": "success",
                "service_type": request_type,
                "enhanced_by_claude_code": enhanced_context.get("enhanced_capabilities", False),
                "context_capacity": enhanced_context.get("max_tokens", 8000),
                "response": {
                    "context": enhanced_context,
                    "recommendations": self._generate_recommendations(enhanced_context),
                    "next_actions": self._suggest_next_actions(service_type, enhanced_context)
                },
                "metadata": {
                    "processing_time": 0.1,  # 實際應該測量
                    "token_usage": enhanced_context.get("total_tokens", 0),
                    "claude_code_analysis": enhanced_context.get("claude_analysis"),
                    "capabilities": {
                        "claude_code_available": self.context_manager.is_claude_code_available(),
                        "max_context_tokens": enhanced_context.get("max_tokens", 8000),
                        "enhanced_analysis": enhanced_context.get("enhanced_capabilities", False)
                    }
                }
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing SmartInvention request: {e}")
            return {
                "request_id": request.get("request_id", "unknown"),
                "status": "error",
                "error": str(e),
                "fallback_response": await self._get_fallback_response(request)
            }
    
    def _generate_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """基於上下文生成建議"""
        
        recommendations = []
        
        # 基於 Claude Code 分析生成建議
        claude_analysis = context.get("claude_analysis")
        if claude_analysis:
            recommendations.extend(claude_analysis.get("suggestions", []))
            
            # 基於代碼質量評分的建議
            quality_score = claude_analysis.get("code_quality_score", 0)
            if quality_score < 6:
                recommendations.append("建議重構代碼以提高質量")
            elif quality_score > 8:
                recommendations.append("代碼質量良好，可考慮優化性能")
        
        # 基於服務類型的通用建議
        service_type = context.get("service_type", "")
        if service_type == "code_generation":
            recommendations.append("建議添加單元測試")
            recommendations.append("考慮代碼文檔化")
        elif service_type == "code_analysis":
            recommendations.append("建議進行性能分析")
            recommendations.append("檢查安全性問題")
        
        return recommendations[:5]  # 限制建議數量
    
    def _suggest_next_actions(self, service_type: ServiceType, context: Dict[str, Any]) -> List[str]:
        """建議下一步行動"""
        
        actions = []
        
        if service_type == ServiceType.CODE_GENERATION:
            actions = [
                "運行代碼測試",
                "進行代碼審查",
                "部署到測試環境"
            ]
        elif service_type == ServiceType.CODE_ANALYSIS:
            actions = [
                "修復發現的問題",
                "優化性能瓶頸",
                "更新文檔"
            ]
        elif service_type == ServiceType.REQUIREMENT_ANALYSIS:
            actions = [
                "細化需求規格",
                "創建技術方案",
                "評估實施難度"
            ]
        else:
            actions = [
                "繼續分析",
                "收集更多信息",
                "制定行動計劃"
            ]
        
        return actions
    
    async def _get_fallback_response(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """降級響應"""
        return {
            "message": "使用基礎模式處理請求",
            "service_type": request.get("request_type", "unknown"),
            "enhanced_capabilities": False,
            "context_capacity": 8000
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        stats = self.context_manager.get_stats()
        
        return {
            "system": "SmartInvention + Claude Code Enhanced",
            "status": "operational",
            "capabilities": {
                "claude_code_available": self.context_manager.is_claude_code_available(),
                "max_context_tokens": 200000 if self.context_manager.is_claude_code_available() else 8000,
                "enhanced_analysis": self.context_manager.is_claude_code_available(),
                "service_types": list(self.service_mappings.keys())
            },
            "statistics": stats,
            "version": "1.0.0-claude-enhanced"
        }

# 測試函數
async def test_smartinvention_claude_adapter():
    """測試 SmartInvention Claude Code 適配器"""
    
    adapter = SmartInventionClaudeCodeAdapter()
    
    # 測試請求
    test_request = {
        "request_id": "test-001",
        "request_type": "code_analysis",
        "content": """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
        """,
        "session_id": "test-session",
        "context": {
            "include_history": True,
            "include_project_context": True
        }
    }
    
    # 處理請求
    response = await adapter.process_smartinvention_request(test_request)
    
    print("SmartInvention Claude Code Adapter Test Results:")
    print(f"Status: {response['status']}")
    print(f"Enhanced by Claude Code: {response['enhanced_by_claude_code']}")
    print(f"Context Capacity: {response['context_capacity']}")
    print(f"Recommendations: {response['response']['recommendations']}")
    print(f"Next Actions: {response['response']['next_actions']}")
    
    # 系統狀態
    status = await adapter.get_system_status()
    print(f"\nSystem Status:")
    print(f"Claude Code Available: {status['capabilities']['claude_code_available']}")
    print(f"Max Context Tokens: {status['capabilities']['max_context_tokens']}")
    print(f"Enhanced Analysis: {status['capabilities']['enhanced_analysis']}")

if __name__ == "__main__":
    asyncio.run(test_smartinvention_claude_adapter())

