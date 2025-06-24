"""
PowerAutomation架構配置
PowerAutomation Architecture Configuration
"""

import os
from typing import Dict, List, Any

class PowerAutomationConfig:
    """PowerAutomation配置類"""
    
    # 基本配置
    AGENT_NAME = "PowerAutomation"
    AGENT_VERSION = "3.0.0"
    AGENT_DESCRIPTION = "基於動態專家系統的智能自動化平台"
    
    # Agent Core配置
    AGENT_CORE = {
        'max_concurrent_requests': 50,
        'request_timeout': 300,  # 秒
        'history_limit': 1000,
        'performance_tracking': True,
        'ai_reasoning_enabled': True
    }
    
    # Tool Registry配置
    TOOL_REGISTRY = {
        'auto_discovery': True,
        'discovery_interval': 300,  # 秒
        'health_check_interval': 60,  # 秒
        'discovery_paths': [
            '/opt/aiengine/mcp',
            '/opt/aiengine/tools',
            './tools'
        ],
        'predefined_tools': [
            'general_processor_mcp',
            'test_flow_mcp',
            'system_monitor_adapter_mcp',
            'file_processor_adapter_mcp',
            'recorder_workflow_mcp'
        ]
    }
    
    # Action Executor配置
    ACTION_EXECUTOR = {
        'max_workers': 10,
        'max_concurrent_tasks': 20,
        'default_timeout': 30,  # 秒
        'retry_attempts': 2,
        'execution_modes': ['sequential', 'parallel', 'pipeline'],
        'default_mode': 'parallel'
    }
    
    # MCP服務配置
    MCP_SERVICES = [
        {
            'name': 'operations_workflow_mcp',
            'url': 'http://localhost:8091',
            'port': 8091,
            'health_endpoint': '/health',
            'process_endpoint': '/process',
            'capabilities': ['workflow_analysis', 'process_optimization'],
            'timeout': 30
        },
        {
            'name': 'test_management_workflow_mcp',
            'url': 'http://localhost:8321',
            'port': 8321,
            'health_endpoint': '/health',
            'process_endpoint': '/process',
            'capabilities': ['test_management', 'integration_testing'],
            'timeout': 45
        },
        {
            'name': 'requirements_analysis_mcp',
            'url': 'http://localhost:8090',
            'port': 8090,
            'health_endpoint': '/health',
            'process_endpoint': '/process',
            'capabilities': ['requirement_analysis', 'business_analysis'],
            'timeout': 60
        }
    ]
    
    # HTTP API配置
    HTTP_APIS = [
        {
            'name': 'ai_analysis_engine',
            'url': 'http://localhost:8888',
            'port': 8888,
            'health_endpoint': '/health',
            'api_endpoint': '/api/analyze',
            'capabilities': ['ai_analysis', 'intelligent_processing'],
            'timeout': 45
        },
        {
            'name': 'operations_analysis_engine',
            'url': 'http://localhost:8100',
            'port': 8100,
            'health_endpoint': '/health',
            'api_endpoint': '/api/process',
            'capabilities': ['operations_analysis', 'performance_analysis'],
            'timeout': 30
        }
    ]
    
    # 日誌配置
    LOGGING = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'PowerAutomation.log',
        'max_size': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5,
        'console_output': True
    }
    
    # 性能監控配置
    MONITORING = {
        'enabled': True,
        'metrics_collection': True,
        'performance_tracking': True,
        'health_check_interval': 30,  # 秒
        'metrics_retention_days': 7
    }
    
    # 安全配置
    SECURITY = {
        'enable_auth': False,  # 開發環境關閉
        'api_key_required': False,
        'rate_limiting': {
            'enabled': True,
            'requests_per_minute': 100,
            'burst_limit': 20
        },
        'cors_enabled': True,
        'allowed_origins': ['*']  # 生產環境需要限制
    }
    
    # 緩存配置
    CACHE = {
        'enabled': True,
        'type': 'memory',  # memory, redis, file
        'ttl': 300,  # 秒
        'max_size': 1000,  # 最大緩存項目數
        'cleanup_interval': 60  # 秒
    }
    
    # 錯誤處理配置
    ERROR_HANDLING = {
        'retry_enabled': True,
        'max_retries': 3,
        'retry_delay': 1,  # 秒
        'exponential_backoff': True,
        'circuit_breaker': {
            'enabled': True,
            'failure_threshold': 5,
            'recovery_timeout': 60  # 秒
        }
    }

class DevelopmentConfig(SimplifiedAgentConfig):
    """開發環境配置"""
    
    # 開發環境特定配置
    AGENT_CORE = {
        **SimplifiedAgentConfig.AGENT_CORE,
        'request_timeout': 600,  # 開發環境延長超時
        'performance_tracking': True
    }
    
    LOGGING = {
        **SimplifiedAgentConfig.LOGGING,
        'level': 'DEBUG',
        'console_output': True
    }
    
    TOOL_REGISTRY = {
        **SimplifiedAgentConfig.TOOL_REGISTRY,
        'discovery_interval': 60,  # 開發環境更頻繁的發現
        'health_check_interval': 30
    }

class ProductionConfig(SimplifiedAgentConfig):
    """生產環境配置"""
    
    # 生產環境特定配置
    AGENT_CORE = {
        **SimplifiedAgentConfig.AGENT_CORE,
        'max_concurrent_requests': 100,
        'request_timeout': 180,  # 生產環境縮短超時
        'performance_tracking': True
    }
    
    LOGGING = {
        **SimplifiedAgentConfig.LOGGING,
        'level': 'INFO',
        'console_output': False
    }
    
    SECURITY = {
        **SimplifiedAgentConfig.SECURITY,
        'enable_auth': True,
        'api_key_required': True,
        'allowed_origins': [
            'https://yourdomain.com',
            'https://api.yourdomain.com'
        ]
    }
    
    ACTION_EXECUTOR = {
        **SimplifiedAgentConfig.ACTION_EXECUTOR,
        'max_workers': 20,
        'max_concurrent_tasks': 50
    }

class TestingConfig(SimplifiedAgentConfig):
    """測試環境配置"""
    
    # 測試環境特定配置
    AGENT_CORE = {
        **SimplifiedAgentConfig.AGENT_CORE,
        'request_timeout': 30,  # 測試環境快速超時
        'history_limit': 100
    }
    
    LOGGING = {
        **SimplifiedAgentConfig.LOGGING,
        'level': 'DEBUG',
        'file': 'test_PowerAutomation.log'
    }
    
    CACHE = {
        **SimplifiedAgentConfig.CACHE,
        'enabled': False  # 測試環境禁用緩存
    }

# 配置字典
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(env: str = None) -> SimplifiedAgentConfig:
    """
    獲取配置
    
    Args:
        env: 環境名稱 (development, production, testing)
    
    Returns:
        配置類實例
    """
    if env is None:
        env = os.environ.get('AGENT_ENV', 'default')
    
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()

# 環境變量覆蓋
def apply_env_overrides(config: SimplifiedAgentConfig) -> SimplifiedAgentConfig:
    """
    應用環境變量覆蓋
    
    支持的環境變量:
    - AGENT_NAME: Agent名稱
    - AGENT_LOG_LEVEL: 日誌級別
    - AGENT_MAX_WORKERS: 最大工作線程數
    - AGENT_TIMEOUT: 默認超時時間
    """
    
    # Agent名稱覆蓋
    if os.environ.get('AGENT_NAME'):
        config.AGENT_NAME = os.environ.get('AGENT_NAME')
    
    # 日誌級別覆蓋
    if os.environ.get('AGENT_LOG_LEVEL'):
        config.LOGGING['level'] = os.environ.get('AGENT_LOG_LEVEL')
    
    # 最大工作線程數覆蓋
    if os.environ.get('AGENT_MAX_WORKERS'):
        config.ACTION_EXECUTOR['max_workers'] = int(os.environ.get('AGENT_MAX_WORKERS'))
    
    # 超時時間覆蓋
    if os.environ.get('AGENT_TIMEOUT'):
        config.AGENT_CORE['request_timeout'] = int(os.environ.get('AGENT_TIMEOUT'))
    
    return config

# 配置驗證
def validate_config(config: SimplifiedAgentConfig) -> bool:
    """
    驗證配置有效性
    
    Args:
        config: 配置實例
    
    Returns:
        配置是否有效
    """
    try:
        # 檢查必要的配置項
        assert config.AGENT_NAME, "Agent name is required"
        assert config.AGENT_VERSION, "Agent version is required"
        assert config.AGENT_CORE['max_concurrent_requests'] > 0, "Max concurrent requests must be positive"
        assert config.ACTION_EXECUTOR['max_workers'] > 0, "Max workers must be positive"
        
        # 檢查MCP服務配置
        for service in config.MCP_SERVICES:
            assert service['name'], "MCP service name is required"
            assert service['url'], "MCP service URL is required"
            assert service['port'] > 0, "MCP service port must be positive"
        
        # 檢查HTTP API配置
        for api in config.HTTP_APIS:
            assert api['name'], "HTTP API name is required"
            assert api['url'], "HTTP API URL is required"
            assert api['port'] > 0, "HTTP API port must be positive"
        
        return True
        
    except AssertionError as e:
        print(f"Configuration validation failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during configuration validation: {e}")
        return False

# 配置導出
def export_config(config: SimplifiedAgentConfig, format: str = 'dict') -> Any:
    """
    導出配置
    
    Args:
        config: 配置實例
        format: 導出格式 (dict, json, yaml)
    
    Returns:
        導出的配置數據
    """
    config_dict = {}
    
    # 獲取所有大寫的類屬性
    for attr_name in dir(config):
        if attr_name.isupper() and not attr_name.startswith('_'):
            config_dict[attr_name] = getattr(config, attr_name)
    
    if format == 'dict':
        return config_dict
    elif format == 'json':
        import json
        return json.dumps(config_dict, indent=2, ensure_ascii=False)
    elif format == 'yaml':
        try:
            import yaml
            return yaml.dump(config_dict, default_flow_style=False, allow_unicode=True)
        except ImportError:
            print("PyYAML not installed, falling back to JSON format")
            import json
            return json.dumps(config_dict, indent=2, ensure_ascii=False)
    else:
        raise ValueError(f"Unsupported export format: {format}")

# 示例使用
if __name__ == "__main__":
    # 獲取開發環境配置
    dev_config = get_config('development')
    
    # 應用環境變量覆蓋
    dev_config = apply_env_overrides(dev_config)
    
    # 驗證配置
    if validate_config(dev_config):
        print("Configuration is valid")
        
        # 導出配置
        config_json = export_config(dev_config, 'json')
        print("Configuration exported successfully")
    else:
        print("Configuration validation failed")

