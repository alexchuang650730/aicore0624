"""
PowerAutomation Local MCP 異常處理模組

定義所有自定義異常類型

Author: Manus AI
Version: 1.0.0
Date: 2025-06-23
"""


class PowerAutomationError(Exception):
    """PowerAutomation基礎異常類"""
    
    def __init__(self, message: str, error_code: int = None, details: dict = None):
        """
        初始化異常
        
        Args:
            message: 錯誤消息
            error_code: 錯誤碼
            details: 詳細信息
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """轉換為字典格式"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class ConfigurationError(PowerAutomationError):
    """配置錯誤"""
    
    def __init__(self, message: str, config_section: str = None, **kwargs):
        super().__init__(message, error_code=2, **kwargs)
        self.config_section = config_section
        if config_section:
            self.details["config_section"] = config_section


class ServerError(PowerAutomationError):
    """服務器錯誤"""
    
    def __init__(self, message: str, status_code: int = None, **kwargs):
        super().__init__(message, error_code=3, **kwargs)
        self.status_code = status_code
        if status_code:
            self.details["status_code"] = status_code


class ManusError(PowerAutomationError):
    """Manus集成錯誤"""
    
    def __init__(self, message: str, operation: str = None, **kwargs):
        super().__init__(message, error_code=4, **kwargs)
        self.operation = operation
        if operation:
            self.details["operation"] = operation


class AutomationError(PowerAutomationError):
    """自動化測試錯誤"""
    
    def __init__(self, message: str, test_case: str = None, step: str = None, **kwargs):
        super().__init__(message, error_code=5, **kwargs)
        self.test_case = test_case
        self.step = step
        if test_case:
            self.details["test_case"] = test_case
        if step:
            self.details["step"] = step


class ExtensionError(PowerAutomationError):
    """VSCode擴展錯誤"""
    
    def __init__(self, message: str, command: str = None, **kwargs):
        super().__init__(message, error_code=6, **kwargs)
        self.command = command
        if command:
            self.details["command"] = command


class StorageError(PowerAutomationError):
    """存儲錯誤"""
    
    def __init__(self, message: str, path: str = None, operation: str = None, **kwargs):
        super().__init__(message, error_code=7, **kwargs)
        self.path = path
        self.operation = operation
        if path:
            self.details["path"] = path
        if operation:
            self.details["operation"] = operation


class ValidationError(PowerAutomationError):
    """驗證錯誤"""
    
    def __init__(self, message: str, field: str = None, value: str = None, **kwargs):
        super().__init__(message, error_code=8, **kwargs)
        self.field = field
        self.value = value
        if field:
            self.details["field"] = field
        if value:
            self.details["value"] = value


class AuthenticationError(PowerAutomationError):
    """認證錯誤"""
    
    def __init__(self, message: str, username: str = None, **kwargs):
        super().__init__(message, error_code=9, **kwargs)
        self.username = username
        if username:
            self.details["username"] = username


class NetworkError(PowerAutomationError):
    """網絡錯誤"""
    
    def __init__(self, message: str, url: str = None, status_code: int = None, **kwargs):
        super().__init__(message, error_code=10, **kwargs)
        self.url = url
        self.status_code = status_code
        if url:
            self.details["url"] = url
        if status_code:
            self.details["status_code"] = status_code


class TimeoutError(PowerAutomationError):
    """超時錯誤"""
    
    def __init__(self, message: str, timeout: float = None, operation: str = None, **kwargs):
        super().__init__(message, error_code=11, **kwargs)
        self.timeout = timeout
        self.operation = operation
        if timeout:
            self.details["timeout"] = timeout
        if operation:
            self.details["operation"] = operation


# 異常處理裝飾器
def handle_exceptions(default_return=None, log_errors=True):
    """
    異常處理裝飾器
    
    Args:
        default_return: 發生異常時的默認返回值
        log_errors: 是否記錄錯誤日誌
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except PowerAutomationError as e:
                if log_errors and hasattr(args[0], 'logger'):
                    args[0].logger.error(f"{func.__name__} 發生PowerAutomation錯誤: {e}")
                return default_return
            except Exception as e:
                if log_errors and hasattr(args[0], 'logger'):
                    args[0].logger.error(f"{func.__name__} 發生未知錯誤: {e}")
                return default_return
        return wrapper
    return decorator


def async_handle_exceptions(default_return=None, log_errors=True):
    """
    異步異常處理裝飾器
    
    Args:
        default_return: 發生異常時的默認返回值
        log_errors: 是否記錄錯誤日誌
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except PowerAutomationError as e:
                if log_errors and hasattr(args[0], 'logger'):
                    args[0].logger.error(f"{func.__name__} 發生PowerAutomation錯誤: {e}")
                return default_return
            except Exception as e:
                if log_errors and hasattr(args[0], 'logger'):
                    args[0].logger.error(f"{func.__name__} 發生未知錯誤: {e}")
                return default_return
        return wrapper
    return decorator

