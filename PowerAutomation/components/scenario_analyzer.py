"""
Cloud Search場景識別引擎
動態專家發現的核心組件
"""

import asyncio
import logging
import re
import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)

class ScenarioType(Enum):
    """場景類型枚舉"""
    TESTING = "testing"           # 測試場景
    DEPLOYMENT = "deployment"     # 部署場景  
    CODING = "coding"            # 編碼場景
    DEBUGGING = "debugging"      # 調試場景
    ARCHITECTURE = "architecture" # 架構設計場景
    PERFORMANCE = "performance"   # 性能優化場景
    SECURITY = "security"        # 安全場景
    DATA_ANALYSIS = "data_analysis" # 數據分析場景
    INTEGRATION = "integration"   # 集成場景
    MONITORING = "monitoring"     # 監控場景
    DOCUMENTATION = "documentation" # 文檔場景
    RESEARCH = "research"        # 研究場景

class ComplexityLevel(Enum):
    """複雜度等級"""
    LOW = 1      # 簡單場景，基礎專家即可
    MEDIUM = 2   # 中等複雜度，需要1-2個動態專家
    HIGH = 3     # 高複雜度，需要多個專家協作
    CRITICAL = 4 # 關鍵場景，需要頂級專家

@dataclass
class ScenarioContext:
    """場景上下文"""
    keywords: List[str]           # 關鍵詞
    technologies: List[str]       # 涉及技術
    domains: List[str]           # 業務領域
    urgency: str                 # 緊急程度
    scope: str                   # 影響範圍
    constraints: List[str]       # 約束條件

@dataclass
class ExpertRequirement:
    """專家需求"""
    domain: str                  # 專業領域
    scenario_type: ScenarioType  # 場景類型
    skill_level: str            # 技能等級
    specific_skills: List[str]   # 特定技能
    priority: int               # 優先級 (1-10)
    context_keywords: List[str]  # 上下文關鍵詞
    estimated_workload: float   # 預估工作量
    collaboration_needs: List[str] # 協作需求

@dataclass
class Scenario:
    """完整場景描述"""
    id: str
    type: ScenarioType
    complexity: ComplexityLevel
    context: ScenarioContext
    expert_requirements: List[ExpertRequirement]
    confidence: float
    created_at: datetime
    metadata: Dict[str, Any]

class ScenarioAnalyzer:
    """場景分析引擎"""
    
    def __init__(self):
        self.scenario_patterns = self._load_scenario_patterns()
        self.technology_mapping = self._load_technology_mapping()
        self.expert_templates = self._load_expert_templates()
    
    async def analyze_scenario(self, request, background_info: Dict) -> Scenario:
        """分析用戶請求場景"""
        logger.info("🔍 開始場景分析...")
        
        # 1. 文本預處理
        processed_text = self._preprocess_text(request.content)
        
        # 2. 場景類型識別
        scenario_type = await self._identify_scenario_type(processed_text, request.context)
        
        # 3. 複雜度評估
        complexity = await self._assess_complexity(processed_text, scenario_type, background_info)
        
        # 4. 上下文提取
        context = await self._extract_context(processed_text, request.context, background_info)
        
        # 5. 專家需求生成
        expert_requirements = await self._generate_expert_requirements(
            scenario_type, complexity, context, processed_text
        )
        
        # 6. 信心度計算
        confidence = await self._calculate_confidence(scenario_type, context, expert_requirements)
        
        scenario = Scenario(
            id=f"scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=scenario_type,
            complexity=complexity,
            context=context,
            expert_requirements=expert_requirements,
            confidence=confidence,
            created_at=datetime.now(),
            metadata={
                "original_request": request.content,
                "background_info": background_info,
                "processing_time": 0.0
            }
        )
        
        logger.info(f"✅ 場景分析完成: {scenario_type.value}, 複雜度: {complexity.value}")
        return scenario
    
    async def _identify_scenario_type(self, text: str, context: Dict) -> ScenarioType:
        """識別場景類型"""
        
        # 場景關鍵詞映射
        scenario_keywords = {
            ScenarioType.TESTING: [
                "test", "testing", "unit test", "integration test", "e2e test",
                "測試", "單元測試", "集成測試", "端到端測試", "自動化測試",
                "pytest", "jest", "selenium", "cypress", "test case",
                "bug", "defect", "quality assurance", "qa"
            ],
            ScenarioType.DEPLOYMENT: [
                "deploy", "deployment", "release", "production", "staging",
                "部署", "發布", "上線", "生產環境", "預發布",
                "docker", "kubernetes", "ci/cd", "pipeline", "devops",
                "aws", "azure", "gcp", "server", "infrastructure"
            ],
            ScenarioType.CODING: [
                "code", "coding", "programming", "development", "implement",
                "編碼", "開發", "實現", "程式", "代碼",
                "python", "javascript", "java", "c++", "react", "vue",
                "algorithm", "data structure", "function", "class", "api"
            ],
            ScenarioType.DEBUGGING: [
                "debug", "debugging", "error", "exception", "bug fix",
                "調試", "除錯", "錯誤", "異常", "修復",
                "stack trace", "log", "troubleshoot", "issue", "problem"
            ],
            ScenarioType.ARCHITECTURE: [
                "architecture", "design", "system design", "microservice",
                "架構", "設計", "系統設計", "微服務",
                "scalability", "pattern", "framework", "structure"
            ],
            ScenarioType.PERFORMANCE: [
                "performance", "optimization", "speed", "latency", "throughput",
                "性能", "優化", "速度", "延遲", "吞吐量",
                "benchmark", "profiling", "memory", "cpu", "cache"
            ],
            ScenarioType.SECURITY: [
                "security", "authentication", "authorization", "encryption",
                "安全", "認證", "授權", "加密",
                "vulnerability", "penetration", "firewall", "ssl", "https"
            ],
            ScenarioType.DATA_ANALYSIS: [
                "data", "analysis", "analytics", "visualization", "report",
                "數據", "分析", "可視化", "報告",
                "pandas", "numpy", "matplotlib", "sql", "database"
            ],
            ScenarioType.INTEGRATION: [
                "integration", "api", "webhook", "connector", "sync",
                "集成", "整合", "接口", "同步",
                "rest", "graphql", "soap", "middleware", "etl"
            ],
            ScenarioType.MONITORING: [
                "monitoring", "observability", "logging", "metrics", "alerting",
                "監控", "可觀測性", "日誌", "指標", "告警",
                "prometheus", "grafana", "elk", "datadog", "newrelic"
            ]
        }
        
        # 計算每種場景的匹配分數
        scenario_scores = {}
        text_lower = text.lower()
        
        for scenario_type, keywords in scenario_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    # 根據關鍵詞重要性給予不同權重
                    if len(keyword) > 8:  # 長關鍵詞權重更高
                        score += 3
                    elif len(keyword) > 4:
                        score += 2
                    else:
                        score += 1
            
            scenario_scores[scenario_type] = score
        
        # 選擇得分最高的場景類型
        if scenario_scores:
            best_scenario = max(scenario_scores, key=scenario_scores.get)
            if scenario_scores[best_scenario] > 0:
                return best_scenario
        
        # 默認返回編碼場景
        return ScenarioType.CODING
    
    async def _assess_complexity(self, text: str, scenario_type: ScenarioType, background_info: Dict) -> ComplexityLevel:
        """評估場景複雜度"""
        
        complexity_indicators = {
            "high": ["enterprise", "large scale", "distributed", "microservice", "complex", "advanced"],
            "medium": ["integration", "multiple", "several", "various", "moderate"],
            "low": ["simple", "basic", "single", "straightforward", "easy"]
        }
        
        score = 0
        text_lower = text.lower()
        
        # 基於關鍵詞評分
        for level, indicators in complexity_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    if level == "high":
                        score += 3
                    elif level == "medium":
                        score += 2
                    else:
                        score -= 1
        
        # 基於文本長度
        if len(text) > 500:
            score += 2
        elif len(text) > 200:
            score += 1
        
        # 基於場景類型
        scenario_complexity_base = {
            ScenarioType.ARCHITECTURE: 3,
            ScenarioType.INTEGRATION: 2,
            ScenarioType.DEPLOYMENT: 2,
            ScenarioType.SECURITY: 2,
            ScenarioType.PERFORMANCE: 2,
            ScenarioType.TESTING: 1,
            ScenarioType.CODING: 1,
            ScenarioType.DEBUGGING: 1
        }
        
        score += scenario_complexity_base.get(scenario_type, 1)
        
        # 轉換為複雜度等級
        if score >= 8:
            return ComplexityLevel.CRITICAL
        elif score >= 5:
            return ComplexityLevel.HIGH
        elif score >= 3:
            return ComplexityLevel.MEDIUM
        else:
            return ComplexityLevel.LOW
    
    async def _extract_context(self, text: str, request_context: Dict, background_info: Dict) -> ScenarioContext:
        """提取場景上下文"""
        
        # 技術關鍵詞提取
        tech_patterns = {
            "languages": r"\b(python|javascript|java|c\+\+|c#|go|rust|typescript|php|ruby)\b",
            "frameworks": r"\b(react|vue|angular|django|flask|spring|express|laravel)\b",
            "databases": r"\b(mysql|postgresql|mongodb|redis|elasticsearch|sqlite)\b",
            "cloud": r"\b(aws|azure|gcp|docker|kubernetes|terraform)\b",
            "tools": r"\b(git|jenkins|gitlab|github|jira|confluence)\b"
        }
        
        technologies = []
        for category, pattern in tech_patterns.items():
            matches = re.findall(pattern, text.lower())
            technologies.extend(matches)
        
        # 關鍵詞提取
        keywords = self._extract_keywords(text)
        
        # 領域識別
        domains = self._identify_domains(text, technologies)
        
        return ScenarioContext(
            keywords=keywords,
            technologies=list(set(technologies)),
            domains=domains,
            urgency=self._assess_urgency(text),
            scope=self._assess_scope(text),
            constraints=self._extract_constraints(text)
        )
    
    async def _generate_expert_requirements(self, scenario_type: ScenarioType, complexity: ComplexityLevel, 
                                          context: ScenarioContext, text: str) -> List[ExpertRequirement]:
        """生成專家需求"""
        
        requirements = []
        
        # 基於場景類型的專家模板
        expert_templates = {
            ScenarioType.TESTING: [
                {
                    "domain": "test_automation",
                    "skills": ["pytest", "selenium", "cypress", "test_strategy"],
                    "priority": 9
                },
                {
                    "domain": "qa_engineering", 
                    "skills": ["quality_assurance", "test_planning", "bug_tracking"],
                    "priority": 8
                }
            ],
            ScenarioType.DEPLOYMENT: [
                {
                    "domain": "devops_engineering",
                    "skills": ["ci_cd", "docker", "kubernetes", "infrastructure"],
                    "priority": 10
                },
                {
                    "domain": "cloud_architecture",
                    "skills": ["aws", "azure", "gcp", "terraform", "monitoring"],
                    "priority": 8
                },
                {
                    "domain": "release_management",
                    "skills": ["deployment_strategy", "rollback", "blue_green"],
                    "priority": 7
                }
            ],
            ScenarioType.CODING: [
                {
                    "domain": "software_engineering",
                    "skills": ["clean_code", "design_patterns", "algorithms"],
                    "priority": 9
                },
                {
                    "domain": "language_specialist",
                    "skills": context.technologies,  # 動態基於檢測到的技術
                    "priority": 8
                }
            ],
            ScenarioType.DEBUGGING: [
                {
                    "domain": "debugging_specialist",
                    "skills": ["troubleshooting", "log_analysis", "profiling"],
                    "priority": 10
                },
                {
                    "domain": "system_analysis",
                    "skills": ["root_cause_analysis", "monitoring", "diagnostics"],
                    "priority": 8
                }
            ],
            ScenarioType.ARCHITECTURE: [
                {
                    "domain": "solution_architect",
                    "skills": ["system_design", "scalability", "patterns"],
                    "priority": 10
                },
                {
                    "domain": "enterprise_architect",
                    "skills": ["microservices", "distributed_systems", "governance"],
                    "priority": 9
                }
            ],
            ScenarioType.PERFORMANCE: [
                {
                    "domain": "performance_engineer",
                    "skills": ["optimization", "profiling", "benchmarking"],
                    "priority": 10
                },
                {
                    "domain": "scalability_expert",
                    "skills": ["load_testing", "capacity_planning", "caching"],
                    "priority": 8
                }
            ],
            ScenarioType.SECURITY: [
                {
                    "domain": "security_engineer",
                    "skills": ["penetration_testing", "vulnerability_assessment"],
                    "priority": 10
                },
                {
                    "domain": "compliance_specialist",
                    "skills": ["gdpr", "sox", "security_audit"],
                    "priority": 7
                }
            ],
            ScenarioType.DATA_ANALYSIS: [
                {
                    "domain": "data_scientist",
                    "skills": ["pandas", "numpy", "machine_learning"],
                    "priority": 9
                },
                {
                    "domain": "data_engineer",
                    "skills": ["etl", "data_pipeline", "big_data"],
                    "priority": 8
                }
            ],
            ScenarioType.INTEGRATION: [
                {
                    "domain": "integration_specialist",
                    "skills": ["api_design", "webhooks", "message_queues"],
                    "priority": 9
                },
                {
                    "domain": "middleware_expert",
                    "skills": ["esb", "api_gateway", "service_mesh"],
                    "priority": 7
                }
            ],
            ScenarioType.MONITORING: [
                {
                    "domain": "observability_engineer",
                    "skills": ["prometheus", "grafana", "elk_stack"],
                    "priority": 9
                },
                {
                    "domain": "sre_specialist",
                    "skills": ["incident_response", "alerting", "sla_management"],
                    "priority": 8
                }
            ]
        }
        
        # 獲取場景對應的專家模板
        templates = expert_templates.get(scenario_type, [])
        
        for template in templates:
            # 根據複雜度調整技能等級
            skill_level = self._determine_skill_level(complexity, template["priority"])
            
            # 計算工作量
            workload = self._estimate_workload(complexity, len(template["skills"]))
            
            requirement = ExpertRequirement(
                domain=template["domain"],
                scenario_type=scenario_type,
                skill_level=skill_level,
                specific_skills=template["skills"],
                priority=template["priority"],
                context_keywords=context.keywords,
                estimated_workload=workload,
                collaboration_needs=self._identify_collaboration_needs(template["domain"], templates)
            )
            
            requirements.append(requirement)
        
        # 根據複雜度限制專家數量
        max_experts = {
            ComplexityLevel.LOW: 2,
            ComplexityLevel.MEDIUM: 3,
            ComplexityLevel.HIGH: 4,
            ComplexityLevel.CRITICAL: 5
        }
        
        # 按優先級排序並限制數量
        requirements.sort(key=lambda x: x.priority, reverse=True)
        return requirements[:max_experts[complexity]]
    
    def _determine_skill_level(self, complexity: ComplexityLevel, priority: int) -> str:
        """確定技能等級"""
        if complexity == ComplexityLevel.CRITICAL or priority >= 9:
            return "expert"
        elif complexity == ComplexityLevel.HIGH or priority >= 7:
            return "advanced"
        elif complexity == ComplexityLevel.MEDIUM or priority >= 5:
            return "intermediate"
        else:
            return "basic"
    
    def _estimate_workload(self, complexity: ComplexityLevel, skill_count: int) -> float:
        """估算工作量"""
        base_workload = {
            ComplexityLevel.LOW: 1.0,
            ComplexityLevel.MEDIUM: 2.0,
            ComplexityLevel.HIGH: 4.0,
            ComplexityLevel.CRITICAL: 8.0
        }
        
        return base_workload[complexity] * (1 + skill_count * 0.2)
    
    def _identify_collaboration_needs(self, domain: str, all_templates: List[Dict]) -> List[str]:
        """識別協作需求"""
        collaboration_map = {
            "devops_engineering": ["security_engineer", "performance_engineer"],
            "test_automation": ["software_engineering", "qa_engineering"],
            "solution_architect": ["security_engineer", "performance_engineer"],
            "data_scientist": ["data_engineer", "software_engineering"]
        }
        
        return collaboration_map.get(domain, [])
    
    def _preprocess_text(self, text: str) -> str:
        """文本預處理"""
        # 移除特殊字符，保留中英文和數字
        cleaned = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
        return cleaned.strip()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取關鍵詞"""
        # 簡單的關鍵詞提取，實際可以使用更複雜的NLP技術
        words = text.lower().split()
        # 過濾停用詞和短詞
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return list(set(keywords))
    
    def _identify_domains(self, text: str, technologies: List[str]) -> List[str]:
        """識別業務領域"""
        domain_keywords = {
            "web_development": ["web", "frontend", "backend", "html", "css"],
            "mobile_development": ["mobile", "ios", "android", "react native", "flutter"],
            "data_science": ["data", "analytics", "machine learning", "ai"],
            "devops": ["deployment", "infrastructure", "ci/cd", "docker"],
            "security": ["security", "authentication", "encryption", "vulnerability"]
        }
        
        domains = []
        text_lower = text.lower()
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                domains.append(domain)
        
        return domains
    
    def _assess_urgency(self, text: str) -> str:
        """評估緊急程度"""
        urgent_keywords = ["urgent", "asap", "critical", "emergency", "immediately"]
        high_keywords = ["important", "priority", "soon", "quickly"]
        
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in urgent_keywords):
            return "urgent"
        elif any(keyword in text_lower for keyword in high_keywords):
            return "high"
        else:
            return "normal"
    
    def _assess_scope(self, text: str) -> str:
        """評估影響範圍"""
        enterprise_keywords = ["enterprise", "organization", "company-wide", "global"]
        team_keywords = ["team", "department", "group", "project"]
        
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in enterprise_keywords):
            return "enterprise"
        elif any(keyword in text_lower for keyword in team_keywords):
            return "team"
        else:
            return "individual"
    
    def _extract_constraints(self, text: str) -> List[str]:
        """提取約束條件"""
        constraint_patterns = [
            r"budget.*?(\$[\d,]+|\d+.*?dollar)",
            r"deadline.*?(\d+.*?day|\d+.*?week|\d+.*?month)",
            r"resource.*?(\d+.*?people|\d+.*?developer)",
            r"technology.*?(must use|required|mandatory)"
        ]
        
        constraints = []
        for pattern in constraint_patterns:
            matches = re.findall(pattern, text.lower())
            constraints.extend(matches)
        
        return constraints
    
    async def _calculate_confidence(self, scenario_type: ScenarioType, context: ScenarioContext, 
                                  requirements: List[ExpertRequirement]) -> float:
        """計算識別信心度"""
        confidence = 0.5  # 基礎信心度
        
        # 基於關鍵詞匹配度
        if len(context.keywords) > 5:
            confidence += 0.2
        
        # 基於技術識別
        if len(context.technologies) > 0:
            confidence += 0.2
        
        # 基於專家需求明確度
        if len(requirements) > 0:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _load_scenario_patterns(self) -> Dict:
        """加載場景模式"""
        # 實際實現中可以從配置文件或數據庫加載
        return {}
    
    def _load_technology_mapping(self) -> Dict:
        """加載技術映射"""
        return {}
    
    def _load_expert_templates(self) -> Dict:
        """加載專家模板"""
        return {}

# 創建場景分析器實例的工廠函數
def create_scenario_analyzer() -> ScenarioAnalyzer:
    """創建場景分析器實例"""
    return ScenarioAnalyzer()

