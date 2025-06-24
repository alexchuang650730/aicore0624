"""
PowerAutomation 3.0 配置文件 - Enhanced Tool Registry版
支持Smart Tool Engine、雲端平台整合、智能路由引擎
"""

import os
from typing import Dict, Any, List
from enum import Enum

class EnvironmentType(Enum):
    """環境類型"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class PowerAutomationConfig:
    """PowerAutomation 3.0 配置類"""
    
    def __init__(self, environment: str = "development"):
        self.environment = EnvironmentType(environment)
        self.config = self._build_config()
    
    def _build_config(self) -> Dict[str, Any]:
        """構建配置"""
        base_config = {
            # 基礎配置
            "environment": self.environment.value,
            "debug": self.environment in [EnvironmentType.DEVELOPMENT, EnvironmentType.TESTING],
            "log_level": "DEBUG" if self.environment == EnvironmentType.DEVELOPMENT else "INFO",
            
            # AICore 3.0 配置
            "aicore": {
                "version": "3.0.0",
                "enable_dynamic_experts": True,
                "enable_expert_aggregation": True,
                "max_concurrent_experts": 5,
                "expert_timeout": 30,
                "enable_scenario_analysis": True,
                "enable_intelligent_routing": True
            },
            
            # Enhanced Tool Registry 配置
            "enhanced_tool_registry": {
                "enable_enhanced_features": True,
                "smart_engine": {
                    # 基礎設置
                    "enable_cloud_tools": True,
                    "enable_intelligent_routing": True,
                    "enable_cost_optimization": True,
                    "enable_performance_monitoring": True,
                    "max_cloud_tools": 100,
                    "default_timeout": 30,
                    "cache_ttl": 300,  # 5分鐘緩存
                    
                    # 成本預算配置
                    "cost_budget": {
                        "max_cost_per_call": 0.01,
                        "monthly_budget": 100.0,
                        "currency": "USD",
                        "enable_budget_alerts": True,
                        "budget_alert_threshold": 0.8,  # 80%預算使用時警告
                        "prefer_free_tools": True
                    },
                    
                    # 性能要求配置
                    "performance_requirements": {
                        "min_success_rate": 0.90,
                        "max_response_time": 5000,  # 毫秒
                        "min_throughput": 10,  # 請求/分鐘
                        "min_uptime": 0.95,
                        "enable_performance_monitoring": True
                    },
                    
                    # 智能路由配置
                    "intelligent_routing": {
                        "enable_multi_dimensional_scoring": True,
                        "scoring_weights": {
                            "performance": 0.3,
                            "cost": 0.25,
                            "reliability": 0.25,
                            "user_rating": 0.2
                        },
                        "enable_context_optimization": True,
                        "enable_fallback_routing": True
                    },
                    
                    # 雲端平台配置
                    "cloud_platforms": {
                        "aci_dev": {
                            "enabled": bool(os.getenv('ACI_DEV_API_KEY')),
                            "api_key": os.getenv('ACI_DEV_API_KEY'),
                            "base_url": "https://api.aci.dev",
                            "priority": 1,
                            "timeout": 10,
                            "max_retries": 3,
                            "rate_limit": {
                                "requests_per_minute": 60,
                                "requests_per_hour": 1000
                            }
                        },
                        "mcp_so": {
                            "enabled": bool(os.getenv('MCP_SO_API_KEY')),
                            "api_key": os.getenv('MCP_SO_API_KEY'),
                            "base_url": "https://api.mcp.so",
                            "priority": 2,
                            "timeout": 15,
                            "max_retries": 3,
                            "rate_limit": {
                                "requests_per_minute": 100,
                                "requests_per_hour": 2000
                            }
                        },
                        "zapier": {
                            "enabled": bool(os.getenv('ZAPIER_API_KEY')),
                            "api_key": os.getenv('ZAPIER_API_KEY'),
                            "base_url": "https://api.zapier.com",
                            "priority": 3,
                            "timeout": 20,
                            "max_retries": 2,
                            "rate_limit": {
                                "requests_per_minute": 30,
                                "requests_per_hour": 500
                            }
                        }
                    }
                }
            },
            
            # 工具註冊表配置
            "tool_registry": {
                "enable_auto_discovery": True,
                "discovery_interval": 3600,  # 1小時
                "health_check_interval": 300,  # 5分鐘
                "max_tools": 1000,
                "enable_tool_versioning": True,
                "enable_tool_metrics": True
            },
            
            # MCP組件配置
            "mcp_components": {
                "general_processor": {
                    "enabled": True,
                    "endpoint": "http://localhost:8090",
                    "timeout": 30,
                    "max_retries": 3
                },
                "recorder_workflow": {
                    "enabled": True,
                    "endpoint": "http://localhost:8091",
                    "timeout": 60,
                    "max_retries": 2
                },
                "test_flow": {
                    "enabled": True,
                    "endpoint": "http://localhost:8092",
                    "timeout": 45,
                    "max_retries": 3
                },
                "dynamic_expert_registry": {
                    "enabled": True,
                    "max_experts": 10,
                    "expert_timeout": 30
                }
            },
            
            # 動作執行器配置
            "action_executor": {
                "max_workers": 10,
                "max_concurrent_tasks": 20,
                "default_timeout": 30,
                "enable_parallel_execution": True,
                "enable_pipeline_execution": True,
                "enable_result_caching": True,
                "cache_ttl": 600  # 10分鐘
            },
            
            # 日誌配置
            "logging": {
                "level": "DEBUG" if self.environment == EnvironmentType.DEVELOPMENT else "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_logging": True,
                "log_file": f"powerautomation_{self.environment.value}.log",
                "max_file_size": "10MB",
                "backup_count": 5,
                "enable_structured_logging": True
            },
            
            # 安全配置
            "security": {
                "enable_api_key_validation": True,
                "enable_rate_limiting": True,
                "enable_request_validation": True,
                "max_request_size": "10MB",
                "allowed_origins": ["*"] if self.environment == EnvironmentType.DEVELOPMENT else [],
                "enable_cors": True
            },
            
            # 監控配置
            "monitoring": {
                "enable_metrics": True,
                "enable_health_checks": True,
                "health_check_interval": 60,
                "enable_performance_tracking": True,
                "enable_cost_tracking": True,
                "metrics_retention_days": 30
            }
        }
        
        # 環境特定配置
        if self.environment == EnvironmentType.DEVELOPMENT:
            base_config.update(self._get_development_config())
        elif self.environment == EnvironmentType.TESTING:
            base_config.update(self._get_testing_config())
        elif self.environment == EnvironmentType.STAGING:
            base_config.update(self._get_staging_config())
        elif self.environment == EnvironmentType.PRODUCTION:
            base_config.update(self._get_production_config())
        
        return base_config
    
    def _get_development_config(self) -> Dict[str, Any]:
        """開發環境配置"""
        return {
            "enhanced_tool_registry": {
                "smart_engine": {
                    "cost_budget": {
                        "monthly_budget": 10.0,  # 開發環境低預算
                        "max_cost_per_call": 0.005
                    },
                    "cloud_platforms": {
                        # 開發環境可能只啟用部分平台
                        "aci_dev": {"enabled": True},
                        "mcp_so": {"enabled": False},  # 開發時可能不需要
                        "zapier": {"enabled": False}
                    }
                }
            },
            "logging": {
                "level": "DEBUG",
                "enable_console_logging": True
            }
        }
    
    def _get_testing_config(self) -> Dict[str, Any]:
        """測試環境配置"""
        return {
            "enhanced_tool_registry": {
                "smart_engine": {
                    "enable_cloud_tools": False,  # 測試環境使用模擬工具
                    "cost_budget": {
                        "monthly_budget": 5.0,  # 測試環境極低預算
                        "max_cost_per_call": 0.001
                    }
                }
            },
            "mcp_components": {
                # 測試環境可能使用模擬端點
                "general_processor": {"endpoint": "http://localhost:18090"},
                "recorder_workflow": {"endpoint": "http://localhost:18091"},
                "test_flow": {"endpoint": "http://localhost:18092"}
            }
        }
    
    def _get_staging_config(self) -> Dict[str, Any]:
        """預發布環境配置"""
        return {
            "enhanced_tool_registry": {
                "smart_engine": {
                    "cost_budget": {
                        "monthly_budget": 50.0,  # 預發布環境中等預算
                        "max_cost_per_call": 0.008
                    }
                }
            },
            "logging": {
                "level": "INFO"
            }
        }
    
    def _get_production_config(self) -> Dict[str, Any]:
        """生產環境配置"""
        return {
            "enhanced_tool_registry": {
                "smart_engine": {
                    "cost_budget": {
                        "monthly_budget": 200.0,  # 生產環境高預算
                        "max_cost_per_call": 0.02,
                        "enable_budget_alerts": True
                    },
                    "performance_requirements": {
                        "min_success_rate": 0.95,  # 生產環境高要求
                        "max_response_time": 3000,
                        "min_uptime": 0.99
                    }
                }
            },
            "security": {
                "enable_api_key_validation": True,
                "enable_rate_limiting": True,
                "allowed_origins": []  # 生產環境嚴格CORS
            },
            "logging": {
                "level": "WARNING",  # 生產環境減少日誌
                "enable_console_logging": False
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """獲取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """設置配置值"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_smart_engine_config(self) -> Dict[str, Any]:
        """獲取Smart Engine配置"""
        return self.get('enhanced_tool_registry.smart_engine', {})
    
    def get_cloud_platform_config(self, platform: str) -> Dict[str, Any]:
        """獲取雲端平台配置"""
        return self.get(f'enhanced_tool_registry.smart_engine.cloud_platforms.{platform}', {})
    
    def is_cloud_platform_enabled(self, platform: str) -> bool:
        """檢查雲端平台是否啟用"""
        return self.get_cloud_platform_config(platform).get('enabled', False)
    
    def get_cost_budget(self) -> Dict[str, Any]:
        """獲取成本預算配置"""
        return self.get('enhanced_tool_registry.smart_engine.cost_budget', {})
    
    def get_performance_requirements(self) -> Dict[str, Any]:
        """獲取性能要求配置"""
        return self.get('enhanced_tool_registry.smart_engine.performance_requirements', {})

def create_config(environment: str = None) -> PowerAutomationConfig:
    """創建配置實例"""
    if environment is None:
        environment = os.getenv('POWERAUTOMATION_ENV', 'development')
    
    return PowerAutomationConfig(environment)

def create_enhanced_config(environment: str = None) -> Dict[str, Any]:
    """創建增強配置字典（向後兼容）"""
    config = create_config(environment)
    return config.config

# 預定義配置實例
development_config = create_config('development')
testing_config = create_config('testing')
staging_config = create_config('staging')
production_config = create_config('production')

# 導出
__all__ = [
    'PowerAutomationConfig',
    'EnvironmentType',
    'create_config',
    'create_enhanced_config',
    'development_config',
    'testing_config', 
    'staging_config',
    'production_config'
]

