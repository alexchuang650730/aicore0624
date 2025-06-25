"""
PowerAutomation Local MCP 共享工具模組

提供通用的工具函數、常量定義和異常處理

Author: Manus AI
Version: 1.0.0
Date: 2025-06-23
"""

import logging
import os
import platform
import psutil
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from logging.handlers import RotatingFileHandler


def setup_logging(
    level: str = "INFO",
    file_enabled: bool = True,
    console_enabled: bool = True,
    max_file_size: str = "10MB",
    backup_count: int = 5,
    log_dir: str = "logs"
) -> logging.Logger:
    """
    設置日誌系統
    
    Args:
        level: 日誌級別
        file_enabled: 是否啟用文件日誌
        console_enabled: 是否啟用控制台日誌
        max_file_size: 最大日誌文件大小
        backup_count: 備份文件數量
        log_dir: 日誌目錄
        
    Returns:
        logging.Logger: 配置好的日誌器
    """
    # 創建日誌器
    logger = logging.getLogger("PowerAutomationMCP")
    logger.setLevel(getattr(logging, level.upper()))
    
    # 清除現有處理器
    logger.handlers.clear()
    
    # 日誌格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # 控制台處理器
    if console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 文件處理器
    if file_enabled:
        # 創建日誌目錄
        os.makedirs(log_dir, exist_ok=True)
        
        # 解析文件大小
        size_bytes = _parse_size(max_file_size)
        
        # 主日誌文件
        log_file = os.path.join(log_dir, "powerautomation_mcp.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=size_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 錯誤日誌文件
        error_log_file = os.path.join(log_dir, "error.log")
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=size_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    
    return logger


def validate_config(config: Dict[str, Any]) -> bool:
    """
    驗證配置文件
    
    Args:
        config: 配置字典
        
    Returns:
        bool: 驗證是否通過
        
    Raises:
        ValueError: 配置驗證失敗
    """
    required_sections = ["server", "manus", "automation", "storage", "extension"]
    
    # 檢查必需的配置段
    for section in required_sections:
        if section not in config:
            raise ValueError(f"缺少必需的配置段: {section}")
    
    # 驗證服務器配置
    server_config = config["server"]
    if "port" not in server_config:
        raise ValueError("server配置中缺少port")
    
    port = server_config["port"]
    if not isinstance(port, int) or port < 1 or port > 65535:
        raise ValueError(f"無效的端口號: {port}")
    
    # 驗證Manus配置
    manus_config = config["manus"]
    required_manus_fields = ["base_url", "app_url", "login_email", "login_password"]
    for field in required_manus_fields:
        if field not in manus_config:
            raise ValueError(f"manus配置中缺少{field}")
    
    # 驗證存儲配置
    storage_config = config["storage"]
    if "base_path" not in storage_config:
        raise ValueError("storage配置中缺少base_path")
    
    # 驗證路徑是否可寫
    base_path = storage_config["base_path"]
    try:
        os.makedirs(base_path, exist_ok=True)
        test_file = os.path.join(base_path, ".test_write")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
    except Exception as e:
        raise ValueError(f"存儲路徑不可寫: {base_path} - {e}")
    
    return True


def get_system_info() -> Dict[str, Any]:
    """
    獲取系統信息
    
    Returns:
        Dict[str, Any]: 系統信息
    """
    try:
        # 基本系統信息
        info = {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "timestamp": time.time()
        }
        
        # CPU信息
        info["cpu"] = {
            "count": psutil.cpu_count(),
            "count_logical": psutil.cpu_count(logical=True),
            "usage_percent": psutil.cpu_percent(interval=1),
            "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }
        
        # 內存信息
        memory = psutil.virtual_memory()
        info["memory"] = {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent,
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2)
        }
        
        # 磁盤信息
        disk = psutil.disk_usage('/')
        info["disk"] = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": (disk.used / disk.total) * 100,
            "total_gb": round(disk.total / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2)
        }
        
        # 網絡信息
        network = psutil.net_io_counters()
        info["network"] = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv
        }
        
        return info
        
    except Exception as e:
        return {"error": str(e), "timestamp": time.time()}


def create_directory_structure(base_path: str, paths_config: Dict[str, str]) -> bool:
    """
    創建目錄結構
    
    Args:
        base_path: 基礎路徑
        paths_config: 路徑配置
        
    Returns:
        bool: 創建是否成功
    """
    try:
        # 創建基礎目錄
        os.makedirs(base_path, exist_ok=True)
        
        # 創建子目錄
        for name, path in paths_config.items():
            full_path = os.path.join(base_path, path)
            os.makedirs(full_path, exist_ok=True)
        
        return True
        
    except Exception as e:
        print(f"創建目錄結構失敗: {e}")
        return False


def calculate_file_hash(file_path: str, algorithm: str = "md5") -> Optional[str]:
    """
    計算文件哈希值
    
    Args:
        file_path: 文件路徑
        algorithm: 哈希算法
        
    Returns:
        Optional[str]: 哈希值
    """
    try:
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
        
    except Exception:
        return None


def format_bytes(bytes_value: int) -> str:
    """
    格式化字節數
    
    Args:
        bytes_value: 字節數
        
    Returns:
        str: 格式化後的字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    格式化時間長度
    
    Args:
        seconds: 秒數
        
    Returns:
        str: 格式化後的時間字符串
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分鐘"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}小時"
    else:
        days = seconds / 86400
        return f"{days:.1f}天"


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    安全的JSON解析
    
    Args:
        json_str: JSON字符串
        default: 默認值
        
    Returns:
        Any: 解析結果或默認值
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    安全的JSON序列化
    
    Args:
        obj: 要序列化的對象
        default: 默認值
        
    Returns:
        str: JSON字符串
    """
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return default


def ensure_directory(path: str) -> bool:
    """
    確保目錄存在
    
    Args:
        path: 目錄路徑
        
    Returns:
        bool: 是否成功
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False


def is_port_available(port: int, host: str = "localhost") -> bool:
    """
    檢查端口是否可用
    
    Args:
        port: 端口號
        host: 主機地址
        
    Returns:
        bool: 端口是否可用
    """
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0
    except Exception:
        return False


def _parse_size(size_str: str) -> int:
    """
    解析大小字符串為字節數
    
    Args:
        size_str: 大小字符串 (如 "10MB")
        
    Returns:
        int: 字節數
    """
    size_str = size_str.upper().strip()
    
    if size_str.endswith('B'):
        size_str = size_str[:-1]
    
    multipliers = {
        'K': 1024,
        'M': 1024 ** 2,
        'G': 1024 ** 3,
        'T': 1024 ** 4
    }
    
    for suffix, multiplier in multipliers.items():
        if size_str.endswith(suffix):
            number = float(size_str[:-1])
            return int(number * multiplier)
    
    return int(float(size_str))


# 常量定義
class Constants:
    """常量定義"""
    
    # 版本信息
    VERSION = "1.0.0"
    
    # 默認配置
    DEFAULT_CONFIG = {
        "server": {
            "host": "0.0.0.0",
            "port": 5000,
            "debug": False
        },
        "logging": {
            "level": "INFO",
            "file_enabled": True,
            "console_enabled": True
        }
    }
    
    # API端點
    API_ENDPOINTS = {
        "status": "/api/status",
        "manus_login": "/api/manus/login",
        "send_message": "/api/manus/send_message",
        "get_conversations": "/api/manus/get_conversations",
        "get_tasks": "/api/manus/get_tasks",
        "run_test": "/api/automation/run_test"
    }
    
    # 錯誤碼
    ERROR_CODES = {
        "SUCCESS": 0,
        "GENERAL_ERROR": 1,
        "CONFIG_ERROR": 2,
        "SERVER_ERROR": 3,
        "MANUS_ERROR": 4,
        "AUTOMATION_ERROR": 5
    }
    
    # 狀態碼
    STATUS_CODES = {
        "INITIALIZED": "initialized",
        "RUNNING": "running",
        "STOPPED": "stopped",
        "ERROR": "error"
    }

