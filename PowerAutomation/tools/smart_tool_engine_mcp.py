"""
Smart Tool Engine MCP - 完整版
整合ACI.dev、MCP.so、Zapier三個雲端平台的統一智能工具引擎
支持智能路由、成本優化、性能監控
"""

import json
import logging
import asyncio
import time
import os
import requests
import aiohttp
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import sys
from datetime import datetime
from enum import Enum

# 添加項目路徑
sys.path.append(str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """支持的雲端平台類型"""
    ACI_DEV = "aci_dev"
    MCP_SO = "mcp_so"
    ZAPIER = "zapier"
    LOCAL = "local"

class CostType(Enum):
    """成本類型"""
    FREE = "free"
    FREEMIUM = "freemium"
    PAID = "paid"
    SUBSCRIPTION = "subscription"

class UnifiedToolRegistry:
    """統一工具註冊表"""
    
    def __init__(self):
        self.tools_db = {}
        self.platform_clients = {}
        self.last_sync_time = None
        self.cost_tracker = CostTracker()
        
    def register_tool(self, tool_info: Dict) -> str:
        """註冊工具到統一註冊表"""
        tool_id = f"{tool_info['platform']}:{tool_info['name']}"
        
        unified_tool = {
            # 基礎信息
            "id": tool_id,
            "name": tool_info["name"],
            "description": tool_info["description"],
            "category": tool_info["category"],
            "version": tool_info.get("version", "1.0.0"),
            "tags": tool_info.get("tags", []),
            
            # 平台信息
            "platform": tool_info["platform"],
            "platform_tool_id": tool_info["platform_tool_id"],
            "mcp_endpoint": tool_info["mcp_endpoint"],
            "api_endpoint": tool_info.get("api_endpoint"),
            
            # 功能特性
            "capabilities": tool_info["capabilities"],
            "input_schema": tool_info["input_schema"],
            "output_schema": tool_info["output_schema"],
            "supported_formats": tool_info.get("supported_formats", []),
            
            # 性能指標
            "performance_metrics": {
                "avg_response_time": tool_info.get("avg_response_time", 1000),
                "success_rate": tool_info.get("success_rate", 0.95),
                "throughput": tool_info.get("throughput", 100),
                "reliability_score": tool_info.get("reliability_score", 0.9),
                "uptime": tool_info.get("uptime", 0.99)
            },
            
            # 成本信息
            "cost_model": {
                "type": tool_info.get("cost_type", "free"),
                "cost_per_call": tool_info.get("cost_per_call", 0.0),
                "cost_per_mb": tool_info.get("cost_per_mb", 0.0),
                "monthly_limit": tool_info.get("monthly_limit", -1),
                "daily_limit": tool_info.get("daily_limit", -1),
                "currency": tool_info.get("currency", "USD"),
                "billing_model": tool_info.get("billing_model", "per_call")
            },
            
            # 質量評分
            "quality_scores": {
                "user_rating": tool_info.get("user_rating", 4.0),
                "documentation_quality": tool_info.get("doc_quality", 0.8),
                "community_support": tool_info.get("community_support", 0.7),
                "update_frequency": tool_info.get("update_frequency", 0.8),
                "security_score": tool_info.get("security_score", 0.9)
            },
            
            # 使用統計
            "usage_stats": {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_cost": 0.0,
                "last_used": None,
                "avg_user_satisfaction": 0.0
            },
            
            # 註冊時間
            "registered_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        self.tools_db[tool_id] = unified_tool
        logger.info(f"Registered tool: {tool_id}")
        return tool_id
    
    def search_tools(self, query: str, filters: Dict = None) -> List[Dict]:
        """搜索工具"""
        filters = filters or {}
        matches = []
        query_lower = query.lower()
        
        for tool_id, tool in self.tools_db.items():
            score = 0.0
            
            # 名稱匹配
            if query_lower in tool["name"].lower():
                score += 0.4
            
            # 描述匹配
            if query_lower in tool["description"].lower():
                score += 0.3
            
            # 標籤匹配
            for tag in tool.get("tags", []):
                if query_lower in tag.lower():
                    score += 0.2
            
            # 能力匹配
            for capability in tool["capabilities"]:
                if query_lower in capability.lower():
                    score += 0.3
            
            # 應用過濾器
            if self._apply_filters(tool, filters):
                matches.append({
                    "tool": tool,
                    "relevance_score": score
                })
        
        # 按相關性排序
        matches.sort(key=lambda x: x["relevance_score"], reverse=True)
        return [match["tool"] for match in matches]
    
    def _apply_filters(self, tool: Dict, filters: Dict) -> bool:
        """應用搜索過濾器"""
        # 平台過濾
        if "platforms" in filters:
            if tool["platform"] not in filters["platforms"]:
                return False
        
        # 成本類型過濾
        if "cost_type" in filters:
            if tool["cost_model"]["type"] != filters["cost_type"]:
                return False
        
        # 最大成本過濾
        if "max_cost" in filters:
            if tool["cost_model"]["cost_per_call"] > filters["max_cost"]:
                return False
        
        # 最小評分過濾
        if "min_rating" in filters:
            if tool["quality_scores"]["user_rating"] < filters["min_rating"]:
                return False
        
        # 性能要求過濾
        if "min_success_rate" in filters:
            if tool["performance_metrics"]["success_rate"] < filters["min_success_rate"]:
                return False
        
        return True
    
    def get_tool_by_id(self, tool_id: str) -> Optional[Dict]:
        """根據ID獲取工具"""
        return self.tools_db.get(tool_id)
    
    def update_tool_stats(self, tool_id: str, execution_result: Dict):
        """更新工具使用統計"""
        if tool_id not in self.tools_db:
            return
        
        tool = self.tools_db[tool_id]
        stats = tool["usage_stats"]
        
        stats["total_calls"] += 1
        stats["last_used"] = datetime.now().isoformat()
        
        if execution_result.get("success", False):
            stats["successful_calls"] += 1
        else:
            stats["failed_calls"] += 1
        
        # 更新成本
        cost = execution_result.get("cost", 0.0)
        stats["total_cost"] += cost
        self.cost_tracker.add_cost(tool_id, cost)
        
        # 更新性能指標
        response_time = execution_result.get("response_time", 0)
        if response_time > 0:
            current_avg = tool["performance_metrics"]["avg_response_time"]
            total_calls = stats["total_calls"]
            new_avg = ((current_avg * (total_calls - 1)) + response_time) / total_calls
            tool["performance_metrics"]["avg_response_time"] = new_avg
        
        # 更新成功率
        success_rate = stats["successful_calls"] / stats["total_calls"]
        tool["performance_metrics"]["success_rate"] = success_rate

class CostTracker:
    """成本追蹤器"""
    
    def __init__(self):
        self.daily_costs = {}
        self.monthly_costs = {}
        self.tool_costs = {}
        
    def add_cost(self, tool_id: str, cost: float):
        """添加成本記錄"""
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")
        
        # 日成本
        if today not in self.daily_costs:
            self.daily_costs[today] = 0.0
        self.daily_costs[today] += cost
        
        # 月成本
        if month not in self.monthly_costs:
            self.monthly_costs[month] = 0.0
        self.monthly_costs[month] += cost
        
        # 工具成本
        if tool_id not in self.tool_costs:
            self.tool_costs[tool_id] = 0.0
        self.tool_costs[tool_id] += cost
    
    def get_monthly_cost(self, month: str = None) -> float:
        """獲取月度成本"""
        if month is None:
            month = datetime.now().strftime("%Y-%m")
        return self.monthly_costs.get(month, 0.0)
    
    def check_budget(self, monthly_budget: float) -> Dict:
        """檢查預算狀態"""
        current_month_cost = self.get_monthly_cost()
        remaining = monthly_budget - current_month_cost
        usage_percentage = (current_month_cost / monthly_budget) * 100
        
        return {
            "monthly_budget": monthly_budget,
            "current_cost": current_month_cost,
            "remaining": remaining,
            "usage_percentage": usage_percentage,
            "over_budget": current_month_cost > monthly_budget
        }

class IntelligentRoutingEngine:
    """智能路由引擎"""
    
    def __init__(self, registry: UnifiedToolRegistry):
        self.registry = registry
        self.routing_weights = {
            "performance": 0.3,
            "cost": 0.25,
            "reliability": 0.25,
            "user_rating": 0.2
        }
    
    def select_optimal_tool(self, requirement: str, context: Dict = None) -> Dict:
        """選擇最優工具"""
        context = context or {}
        
        try:
            # 搜索候選工具
            candidates = self.registry.search_tools(requirement, context.get("filters", {}))
            
            if not candidates:
                return {
                    "success": False,
                    "error": "No suitable tools found",
                    "candidates": []
                }
            
            # 評分和排序
            scored_tools = []
            for tool in candidates:
                score = self._calculate_tool_score(tool, context)
                scored_tools.append({
                    "tool": tool,
                    "score": score,
                    "reasoning": self._generate_reasoning(tool, score, context)
                })
            
            # 按分數排序
            scored_tools.sort(key=lambda x: x["score"], reverse=True)
            
            # 檢查預算約束
            budget = context.get("budget", {})
            if budget:
                scored_tools = self._filter_by_budget(scored_tools, budget)
            
            if not scored_tools:
                return {
                    "success": False,
                    "error": "No tools within budget constraints",
                    "candidates": []
                }
            
            best_tool = scored_tools[0]
            
            return {
                "success": True,
                "selected_tool": best_tool["tool"],
                "confidence": best_tool["score"],
                "reasoning": best_tool["reasoning"],
                "alternatives": [t["tool"] for t in scored_tools[1:5]],  # 前5個備選
                "total_candidates": len(candidates)
            }
            
        except Exception as e:
            logger.error(f"Tool selection failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "candidates": []
            }
    
    def _calculate_tool_score(self, tool: Dict, context: Dict) -> float:
        """計算工具評分"""
        scores = {}
        
        # 性能評分
        perf_metrics = tool["performance_metrics"]
        performance_score = (
            (perf_metrics["success_rate"] * 0.4) +
            (min(1.0, 2000 / max(perf_metrics["avg_response_time"], 100)) * 0.3) +
            (perf_metrics["reliability_score"] * 0.3)
        )
        scores["performance"] = performance_score
        
        # 成本評分 (成本越低分數越高)
        cost_per_call = tool["cost_model"]["cost_per_call"]
        if cost_per_call == 0:
            cost_score = 1.0  # 免費工具最高分
        else:
            # 成本評分反比例，最大成本假設為0.1
            cost_score = max(0.0, 1.0 - (cost_per_call / 0.1))
        scores["cost"] = cost_score
        
        # 可靠性評分
        reliability_score = (
            (perf_metrics["uptime"] * 0.4) +
            (perf_metrics["reliability_score"] * 0.3) +
            (tool["quality_scores"]["security_score"] * 0.3)
        )
        scores["reliability"] = reliability_score
        
        # 用戶評分 (歸一化到0-1)
        user_rating = tool["quality_scores"]["user_rating"] / 5.0
        scores["user_rating"] = user_rating
        
        # 加權總分
        total_score = sum(
            scores[metric] * self.routing_weights[metric]
            for metric in scores
        )
        
        # 應用上下文調整
        total_score = self._apply_context_adjustments(total_score, tool, context)
        
        return min(1.0, max(0.0, total_score))
    
    def _apply_context_adjustments(self, base_score: float, tool: Dict, context: Dict) -> float:
        """應用上下文調整"""
        adjusted_score = base_score
        
        # 優先級調整
        priority = context.get("priority", "medium")
        if priority == "high":
            # 高優先級任務偏好高性能工具
            perf_bonus = tool["performance_metrics"]["success_rate"] * 0.1
            adjusted_score += perf_bonus
        elif priority == "low":
            # 低優先級任務偏好低成本工具
            if tool["cost_model"]["type"] == "free":
                adjusted_score += 0.1
        
        # 數據大小調整
        data_size = context.get("data_size", "small")
        if data_size == "large":
            # 大數據偏好高吞吐量工具
            throughput_bonus = min(0.1, tool["performance_metrics"]["throughput"] / 1000)
            adjusted_score += throughput_bonus
        
        # 預算敏感度調整
        budget_priority = context.get("budget_priority", "medium")
        if budget_priority == "high":
            # 高預算敏感度大幅提升免費工具分數
            if tool["cost_model"]["type"] == "free":
                adjusted_score += 0.15
        
        return adjusted_score
    
    def _filter_by_budget(self, scored_tools: List[Dict], budget: Dict) -> List[Dict]:
        """根據預算過濾工具"""
        max_cost = budget.get("max_cost_per_call", float('inf'))
        monthly_budget = budget.get("monthly_budget")
        
        filtered = []
        for item in scored_tools:
            tool = item["tool"]
            cost_per_call = tool["cost_model"]["cost_per_call"]
            
            # 檢查單次調用成本
            if cost_per_call > max_cost:
                continue
            
            # 檢查月度預算
            if monthly_budget:
                current_cost = self.registry.cost_tracker.get_monthly_cost()
                if current_cost + cost_per_call > monthly_budget:
                    continue
            
            filtered.append(item)
        
        return filtered
    
    def _generate_reasoning(self, tool: Dict, score: float, context: Dict) -> str:
        """生成選擇理由"""
        reasons = []
        
        # 性能理由
        success_rate = tool["performance_metrics"]["success_rate"]
        if success_rate > 0.95:
            reasons.append(f"高成功率({success_rate:.1%})")
        
        # 成本理由
        cost_type = tool["cost_model"]["type"]
        if cost_type == "free":
            reasons.append("免費使用")
        elif tool["cost_model"]["cost_per_call"] < 0.01:
            reasons.append("低成本")
        
        # 評分理由
        user_rating = tool["quality_scores"]["user_rating"]
        if user_rating > 4.0:
            reasons.append(f"高用戶評分({user_rating:.1f}/5)")
        
        # 平台理由
        platform = tool["platform"]
        if platform == "local":
            reasons.append("本地工具，無網絡依賴")
        else:
            reasons.append(f"雲端工具({platform})")
        
        reasoning = f"評分: {score:.2f} - " + "、".join(reasons)
        return reasoning

class CloudPlatformIntegration:
    """雲端平台整合"""
    
    def __init__(self):
        self.platform_configs = {
            "aci_dev": {
                "base_url": "https://api.aci.dev",
                "api_key": os.getenv("ACI_DEV_API_KEY"),
                "enabled": bool(os.getenv("ACI_DEV_API_KEY"))
            },
            "mcp_so": {
                "base_url": "https://api.mcp.so",
                "api_key": os.getenv("MCP_SO_API_KEY"),
                "enabled": bool(os.getenv("MCP_SO_API_KEY"))
            },
            "zapier": {
                "base_url": "https://api.zapier.com",
                "api_key": os.getenv("ZAPIER_API_KEY"),
                "enabled": bool(os.getenv("ZAPIER_API_KEY"))
            }
        }
    
    async def discover_tools_from_platform(self, platform: str, query: str = "") -> List[Dict]:
        """從指定平台發現工具"""
        if platform not in self.platform_configs:
            return []
        
        config = self.platform_configs[platform]
        if not config["enabled"]:
            logger.warning(f"Platform {platform} not configured")
            return []
        
        try:
            if platform == "aci_dev":
                return await self._discover_aci_dev_tools(query)
            elif platform == "mcp_so":
                return await self._discover_mcp_so_tools(query)
            elif platform == "zapier":
                return await self._discover_zapier_tools(query)
        except Exception as e:
            logger.error(f"Failed to discover tools from {platform}: {e}")
            return []
    
    async def _discover_aci_dev_tools(self, query: str) -> List[Dict]:
        """發現ACI.dev工具"""
        # 模擬ACI.dev API調用
        mock_tools = [
            {
                "name": "ai_image_enhancer",
                "description": "AI驅動的圖像增強工具",
                "category": "image_processing",
                "platform": "aci_dev",
                "platform_tool_id": "aci_img_enhance_001",
                "mcp_endpoint": "https://api.aci.dev/tools/image-enhancer",
                "capabilities": ["圖像增強", "AI處理", "批量處理"],
                "input_schema": {"type": "object", "properties": {"image_url": {"type": "string"}}},
                "output_schema": {"type": "object", "properties": {"enhanced_url": {"type": "string"}}},
                "cost_type": "freemium",
                "cost_per_call": 0.005,
                "user_rating": 4.5,
                "avg_response_time": 2000
            },
            {
                "name": "smart_text_analyzer",
                "description": "智能文本分析和情感檢測",
                "category": "text_analysis",
                "platform": "aci_dev",
                "platform_tool_id": "aci_text_001",
                "mcp_endpoint": "https://api.aci.dev/tools/text-analyzer",
                "capabilities": ["文本分析", "情感檢測", "關鍵詞提取"],
                "input_schema": {"type": "object", "properties": {"text": {"type": "string"}}},
                "output_schema": {"type": "object", "properties": {"sentiment": {"type": "string"}}},
                "cost_type": "free",
                "cost_per_call": 0.0,
                "user_rating": 4.2,
                "avg_response_time": 800
            }
        ]
        
        # 根據查詢過濾
        if query:
            query_lower = query.lower()
            mock_tools = [
                tool for tool in mock_tools
                if query_lower in tool["name"].lower() or 
                   query_lower in tool["description"].lower() or
                   any(query_lower in cap.lower() for cap in tool["capabilities"])
            ]
        
        return mock_tools
    
    async def _discover_mcp_so_tools(self, query: str) -> List[Dict]:
        """發現MCP.so工具"""
        # 模擬MCP.so API調用
        mock_tools = [
            {
                "name": "data_processor_pro",
                "description": "專業數據處理MCP組件",
                "category": "data_processing",
                "platform": "mcp_so",
                "platform_tool_id": "mcp_data_pro_001",
                "mcp_endpoint": "https://api.mcp.so/components/data-processor",
                "capabilities": ["數據清洗", "格式轉換", "統計分析"],
                "input_schema": {"type": "object", "properties": {"data": {"type": "array"}}},
                "output_schema": {"type": "object", "properties": {"processed_data": {"type": "array"}}},
                "cost_type": "paid",
                "cost_per_call": 0.02,
                "user_rating": 4.7,
                "avg_response_time": 1500
            },
            {
                "name": "workflow_automator",
                "description": "工作流自動化MCP組件",
                "category": "automation",
                "platform": "mcp_so",
                "platform_tool_id": "mcp_workflow_001",
                "mcp_endpoint": "https://api.mcp.so/components/workflow",
                "capabilities": ["工作流設計", "任務調度", "狀態監控"],
                "input_schema": {"type": "object", "properties": {"workflow": {"type": "object"}}},
                "output_schema": {"type": "object", "properties": {"execution_id": {"type": "string"}}},
                "cost_type": "subscription",
                "cost_per_call": 0.01,
                "user_rating": 4.4,
                "avg_response_time": 1200
            }
        ]
        
        # 根據查詢過濾
        if query:
            query_lower = query.lower()
            mock_tools = [
                tool for tool in mock_tools
                if query_lower in tool["name"].lower() or 
                   query_lower in tool["description"].lower() or
                   any(query_lower in cap.lower() for cap in tool["capabilities"])
            ]
        
        return mock_tools
    
    async def _discover_zapier_tools(self, query: str) -> List[Dict]:
        """發現Zapier工具"""
        # 模擬Zapier API調用
        mock_tools = [
            {
                "name": "email_automation",
                "description": "郵件自動化和管理",
                "category": "communication",
                "platform": "zapier",
                "platform_tool_id": "zap_email_001",
                "mcp_endpoint": "https://hooks.zapier.com/email-automation",
                "capabilities": ["郵件發送", "模板管理", "批量處理"],
                "input_schema": {"type": "object", "properties": {"recipients": {"type": "array"}}},
                "output_schema": {"type": "object", "properties": {"sent_count": {"type": "number"}}},
                "cost_type": "freemium",
                "cost_per_call": 0.001,
                "user_rating": 4.3,
                "avg_response_time": 3000
            },
            {
                "name": "crm_integration",
                "description": "CRM系統整合和同步",
                "category": "integration",
                "platform": "zapier",
                "platform_tool_id": "zap_crm_001",
                "mcp_endpoint": "https://hooks.zapier.com/crm-sync",
                "capabilities": ["數據同步", "客戶管理", "報告生成"],
                "input_schema": {"type": "object", "properties": {"customer_data": {"type": "object"}}},
                "output_schema": {"type": "object", "properties": {"sync_status": {"type": "string"}}},
                "cost_type": "paid",
                "cost_per_call": 0.015,
                "user_rating": 4.1,
                "avg_response_time": 2500
            }
        ]
        
        # 根據查詢過濾
        if query:
            query_lower = query.lower()
            mock_tools = [
                tool for tool in mock_tools
                if query_lower in tool["name"].lower() or 
                   query_lower in tool["description"].lower() or
                   any(query_lower in cap.lower() for cap in tool["capabilities"])
            ]
        
        return mock_tools

class SmartToolEngineMCP:
    """Smart Tool Engine MCP主類"""
    
    def __init__(self):
        self.registry = UnifiedToolRegistry()
        self.routing_engine = IntelligentRoutingEngine(self.registry)
        self.cloud_integration = CloudPlatformIntegration()
        self.initialized = False
        
    async def initialize(self):
        """初始化Smart Tool Engine"""
        if self.initialized:
            return
        
        try:
            # 註冊本地示例工具
            await self._register_local_tools()
            
            # 發現雲端工具
            await self._discover_cloud_tools()
            
            self.initialized = True
            logger.info("Smart Tool Engine MCP initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Smart Tool Engine: {e}")
            raise
    
    async def _register_local_tools(self):
        """註冊本地示例工具"""
        local_tools = [
            {
                "name": "local_file_processor",
                "description": "本地文件處理工具",
                "category": "file_processing",
                "platform": "local",
                "platform_tool_id": "local_file_001",
                "mcp_endpoint": "local://file_processor",
                "capabilities": ["文件讀取", "格式轉換", "批量處理"],
                "input_schema": {"type": "object", "properties": {"file_path": {"type": "string"}}},
                "output_schema": {"type": "object", "properties": {"result": {"type": "string"}}},
                "cost_type": "free",
                "cost_per_call": 0.0,
                "user_rating": 4.0,
                "avg_response_time": 500
            },
            {
                "name": "local_data_analyzer",
                "description": "本地數據分析工具",
                "category": "data_analysis",
                "platform": "local",
                "platform_tool_id": "local_data_001",
                "mcp_endpoint": "local://data_analyzer",
                "capabilities": ["數據分析", "統計計算", "可視化"],
                "input_schema": {"type": "object", "properties": {"data": {"type": "array"}}},
                "output_schema": {"type": "object", "properties": {"analysis": {"type": "object"}}},
                "cost_type": "free",
                "cost_per_call": 0.0,
                "user_rating": 4.2,
                "avg_response_time": 800
            }
        ]
        
        for tool in local_tools:
            self.registry.register_tool(tool)
    
    async def _discover_cloud_tools(self):
        """發現雲端工具"""
        platforms = ["aci_dev", "mcp_so", "zapier"]
        
        for platform in platforms:
            try:
                tools = await self.cloud_integration.discover_tools_from_platform(platform)
                for tool in tools:
                    self.registry.register_tool(tool)
                logger.info(f"Discovered {len(tools)} tools from {platform}")
            except Exception as e:
                logger.warning(f"Failed to discover tools from {platform}: {e}")
    
    async def process(self, request: Dict) -> Dict:
        """處理請求"""
        if not self.initialized:
            await self.initialize()
        
        action = request.get("action")
        parameters = request.get("parameters", {})
        
        try:
            if action == "discover_tools":
                return await self._handle_discover_tools(parameters)
            elif action == "select_optimal_tool":
                return await self._handle_select_optimal_tool(parameters)
            elif action == "register_tool":
                return await self._handle_register_tool(parameters)
            elif action == "get_tool_stats":
                return await self._handle_get_tool_stats(parameters)
            elif action == "update_tool_stats":
                return await self._handle_update_tool_stats(parameters)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_discover_tools(self, parameters: Dict) -> Dict:
        """處理工具發現請求"""
        query = parameters.get("query", "")
        filters = parameters.get("filters", {})
        limit = parameters.get("limit", 50)
        
        tools = self.registry.search_tools(query, filters)
        
        # 限制返回數量
        if limit > 0:
            tools = tools[:limit]
        
        return {
            "success": True,
            "tools": tools,
            "total_found": len(tools),
            "query": query,
            "filters": filters
        }
    
    async def _handle_select_optimal_tool(self, parameters: Dict) -> Dict:
        """處理最優工具選擇請求"""
        requirement = parameters.get("requirement", "")
        context = parameters.get("context", {})
        
        result = self.routing_engine.select_optimal_tool(requirement, context)
        return result
    
    async def _handle_register_tool(self, parameters: Dict) -> Dict:
        """處理工具註冊請求"""
        tool_info = parameters.get("tool_info", {})
        
        if not tool_info:
            return {
                "success": False,
                "error": "Missing tool_info parameter"
            }
        
        tool_id = self.registry.register_tool(tool_info)
        
        return {
            "success": True,
            "tool_id": tool_id,
            "message": f"Tool {tool_info.get('name')} registered successfully"
        }
    
    async def _handle_get_tool_stats(self, parameters: Dict) -> Dict:
        """處理工具統計查詢請求"""
        tool_id = parameters.get("tool_id")
        
        if tool_id:
            tool = self.registry.get_tool_by_id(tool_id)
            if tool:
                return {
                    "success": True,
                    "tool_stats": tool["usage_stats"],
                    "performance_metrics": tool["performance_metrics"]
                }
            else:
                return {
                    "success": False,
                    "error": f"Tool {tool_id} not found"
                }
        else:
            # 返回總體統計
            total_tools = len(self.registry.tools_db)
            total_calls = sum(tool["usage_stats"]["total_calls"] for tool in self.registry.tools_db.values())
            total_cost = sum(tool["usage_stats"]["total_cost"] for tool in self.registry.tools_db.values())
            
            return {
                "success": True,
                "overall_stats": {
                    "total_tools": total_tools,
                    "total_calls": total_calls,
                    "total_cost": total_cost,
                    "cost_tracker": {
                        "monthly_cost": self.registry.cost_tracker.get_monthly_cost(),
                        "daily_costs": self.registry.cost_tracker.daily_costs,
                        "tool_costs": self.registry.cost_tracker.tool_costs
                    }
                }
            }
    
    async def _handle_update_tool_stats(self, parameters: Dict) -> Dict:
        """處理工具統計更新請求"""
        tool_id = parameters.get("tool_id")
        execution_result = parameters.get("execution_result", {})
        
        if not tool_id or not execution_result:
            return {
                "success": False,
                "error": "Missing tool_id or execution_result parameter"
            }
        
        self.registry.update_tool_stats(tool_id, execution_result)
        
        return {
            "success": True,
            "message": f"Stats updated for tool {tool_id}"
        }

# 導出主要類
__all__ = [
    'SmartToolEngineMCP',
    'UnifiedToolRegistry', 
    'IntelligentRoutingEngine',
    'CloudPlatformIntegration',
    'CostTracker',
    'PlatformType',
    'CostType'
]

