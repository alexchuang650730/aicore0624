"""
PowerAutomation Local MCP 共享模組

提供通用的工具函數、常量定義和異常處理

Author: Manus AI
Version: 1.0.0
Date: 2025-06-23
"""

from .utils import (
    setup_logging,
    validate_config,
    get_system_info,
    create_directory_structure,
    calculate_file_hash,
    format_bytes,
    format_duration,
    safe_json_loads,
    safe_json_dumps,
    ensure_directory,
    is_port_available,
    Constants
)

from .exceptions import (
    PowerAutomationError,
    ConfigurationError,
    ServerError,
    ManusError,
    AutomationError,
    ExtensionError,
    StorageError,
    ValidationError,
    AuthenticationError,
    NetworkError,
    TimeoutError,
    handle_exceptions,
    async_handle_exceptions
)

__all__ = [
    # 工具函數
    "setup_logging",
    "validate_config", 
    "get_system_info",
    "create_directory_structure",
    "calculate_file_hash",
    "format_bytes",
    "format_duration",
    "safe_json_loads",
    "safe_json_dumps",
    "ensure_directory",
    "is_port_available",
    "Constants",
    
    # 異常類
    "PowerAutomationError",
    "ConfigurationError",
    "ServerError",
    "ManusError",
    "AutomationError",
    "ExtensionError",
    "StorageError",
    "ValidationError",
    "AuthenticationError",
    "NetworkError",
    "TimeoutError",
    "handle_exceptions",
    "async_handle_exceptions"
]

