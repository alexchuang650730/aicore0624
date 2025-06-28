#!/usr/bin/env python3
"""
ClaudeSDKMCP 配置文件
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

@dataclass
class ClaudeAPIConfig:
    """Claude API 配置"""
    api_key: str = ""
    api_url: str = "https://api.anthropic.com/v1/messages"
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 200000
    timeout: int = 60

@dataclass
class ExpertConfig:
    """专家配置"""
    enable_dynamic_experts: bool = True
    max_experts: int = 20
    expert_timeout: int = 300
    confidence_threshold: float = 0.8
    performance_tracking: bool = True

@dataclass
class ProcessingConfig:
    """处理配置"""
    max_concurrent_operations: int = 5
    operation_timeout: int = 120
    enable_caching: bool = True
    cache_ttl: int = 3600
    max_history_size: int = 1000

@dataclass
class SystemConfig:
    """系统配置"""
    log_level: LogLevel = LogLevel.INFO
    log_file: str = "claude_sdk_mcp.log"
    enable_metrics: bool = True
    metrics_port: int = 8080
    debug_mode: bool = False

class Config:
    """主配置类"""
    
    def __init__(self):
        self.claude_api = ClaudeAPIConfig()
        self.expert = ExpertConfig()
        self.processing = ProcessingConfig()
        self.system = SystemConfig()
        
        # 从环境变量加载配置
        self._load_from_env()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        # Claude API 配置
        self.claude_api.api_key = os.getenv("CLAUDE_API_KEY", self.claude_api.api_key)
        self.claude_api.api_url = os.getenv("CLAUDE_API_URL", self.claude_api.api_url)
        self.claude_api.model = os.getenv("CLAUDE_MODEL", self.claude_api.model)
        
        # 专家配置
        self.expert.enable_dynamic_experts = os.getenv("ENABLE_DYNAMIC_EXPERTS", "true").lower() == "true"
        self.expert.max_experts = int(os.getenv("MAX_EXPERTS", str(self.expert.max_experts)))
        self.expert.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", str(self.expert.confidence_threshold)))
        
        # 处理配置
        self.processing.max_concurrent_operations = int(os.getenv("MAX_CONCURRENT_OPERATIONS", str(self.processing.max_concurrent_operations)))
        self.processing.enable_caching = os.getenv("ENABLE_CACHING", "true").lower() == "true"
        
        # 系统配置
        log_level_str = os.getenv("LOG_LEVEL", self.system.log_level.value)
        try:
            self.system.log_level = LogLevel(log_level_str)
        except ValueError:
            self.system.log_level = LogLevel.INFO
        
        self.system.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "claude_api": {
                "api_key": "***" if self.claude_api.api_key else "",
                "api_url": self.claude_api.api_url,
                "model": self.claude_api.model,
                "max_tokens": self.claude_api.max_tokens,
                "timeout": self.claude_api.timeout
            },
            "expert": {
                "enable_dynamic_experts": self.expert.enable_dynamic_experts,
                "max_experts": self.expert.max_experts,
                "expert_timeout": self.expert.expert_timeout,
                "confidence_threshold": self.expert.confidence_threshold,
                "performance_tracking": self.expert.performance_tracking
            },
            "processing": {
                "max_concurrent_operations": self.processing.max_concurrent_operations,
                "operation_timeout": self.processing.operation_timeout,
                "enable_caching": self.processing.enable_caching,
                "cache_ttl": self.processing.cache_ttl,
                "max_history_size": self.processing.max_history_size
            },
            "system": {
                "log_level": self.system.log_level.value,
                "log_file": self.system.log_file,
                "enable_metrics": self.system.enable_metrics,
                "metrics_port": self.system.metrics_port,
                "debug_mode": self.system.debug_mode
            }
        }

# 默认配置实例
default_config = Config()

# 操作类型映射
OPERATION_CATEGORIES = {
    "code_analysis": [
        "syntax_analysis",
        "semantic_analysis", 
        "complexity_analysis",
        "dependency_analysis",
        "pattern_detection",
        "code_smell_detection",
        "duplication_detection",
        "maintainability_analysis"
    ],
    "architecture": [
        "architecture_review",
        "design_pattern_analysis",
        "modularity_analysis",
        "coupling_analysis",
        "cohesion_analysis",
        "scalability_analysis",
        "extensibility_analysis",
        "architecture_recommendation"
    ],
    "performance": [
        "performance_profiling",
        "bottleneck_identification",
        "algorithm_optimization",
        "memory_optimization",
        "cpu_optimization",
        "io_optimization",
        "caching_strategy",
        "performance_monitoring"
    ],
    "api_design": [
        "api_design_review",
        "rest_api_analysis",
        "graphql_analysis",
        "api_documentation",
        "api_versioning",
        "api_security_review"
    ],
    "security": [
        "vulnerability_scan",
        "security_audit",
        "authentication_review",
        "authorization_review",
        "data_protection_review"
    ],
    "database": [
        "database_design_review",
        "query_optimization",
        "data_migration_analysis"
    ]
}

# 专家类型映射
EXPERT_SPECIALTIES = {
    "code_architect": {
        "name": "代码架构专家",
        "description": "专注于系统设计、架构模式和代码重构",
        "primary_operations": OPERATION_CATEGORIES["architecture"],
        "secondary_operations": OPERATION_CATEGORIES["code_analysis"]
    },
    "performance_optimizer": {
        "name": "性能优化专家", 
        "description": "专注于性能调优、算法优化和系统监控",
        "primary_operations": OPERATION_CATEGORIES["performance"],
        "secondary_operations": []
    },
    "api_designer": {
        "name": "API设计专家",
        "description": "专注于RESTful API、GraphQL和微服务设计",
        "primary_operations": OPERATION_CATEGORIES["api_design"],
        "secondary_operations": []
    },
    "security_analyst": {
        "name": "安全分析专家",
        "description": "专注于代码审计、漏洞分析和安全架构",
        "primary_operations": OPERATION_CATEGORIES["security"],
        "secondary_operations": []
    },
    "database_expert": {
        "name": "数据库专家",
        "description": "专注于数据库设计、查询优化和数据迁移",
        "primary_operations": OPERATION_CATEGORIES["database"],
        "secondary_operations": []
    }
}

# 场景类型配置
SCENARIO_CONFIGS = {
    "code_analysis": {
        "default_complexity": "medium",
        "recommended_experts": ["code_architect", "performance_optimizer"],
        "default_operations": OPERATION_CATEGORIES["code_analysis"][:3]
    },
    "architecture_design": {
        "default_complexity": "high",
        "recommended_experts": ["code_architect"],
        "default_operations": OPERATION_CATEGORIES["architecture"][:3]
    },
    "performance_optimization": {
        "default_complexity": "high",
        "recommended_experts": ["performance_optimizer"],
        "default_operations": OPERATION_CATEGORIES["performance"][:3]
    },
    "api_design": {
        "default_complexity": "medium",
        "recommended_experts": ["api_designer"],
        "default_operations": OPERATION_CATEGORIES["api_design"][:3]
    },
    "security_audit": {
        "default_complexity": "high",
        "recommended_experts": ["security_analyst"],
        "default_operations": OPERATION_CATEGORIES["security"][:3]
    },
    "database_design": {
        "default_complexity": "medium",
        "recommended_experts": ["database_expert"],
        "default_operations": OPERATION_CATEGORIES["database"][:3]
    }
}

