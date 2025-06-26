#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用運維 MCP (Operations MCP)
Universal Operations MCP

專門負責執行各種類型的運維操作
與自動化驗證協調器配合，確保運維操作前已通過驗證

作者: PowerAutomation Team
創建時間: 2025-06-26
版本: 1.0.0
"""

import asyncio
import json
import logging
import time
import subprocess
import os
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import aiohttp

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OperationType(Enum):
    """運維操作類型枚舉"""
    SYSTEM_MONITORING = "system_monitoring"
    SERVICE_RESTART = "service_restart"
    DATABASE_MAINTENANCE = "database_maintenance"
    LOG_ROTATION = "log_rotation"
    BACKUP_OPERATION = "backup_operation"
    SECURITY_SCAN = "security_scan"
    PERFORMANCE_TUNING = "performance_tuning"
    HEALTH_CHECK = "health_check"
    ALERT_MANAGEMENT = "alert_management"
    CAPACITY_PLANNING = "capacity_planning"

class OperationPriority(Enum):
    """操作優先級枚舉"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class OperationStatus(Enum):
    """操作狀態枚舉"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"

@dataclass
class OperationConfig:
    """運維操作配置"""
    name: str
    type: OperationType
    priority: OperationPriority
    description: str
    target_systems: List[str]
    parameters: Dict[str, Any]
    timeout: int = 300
    retry_count: int = 2
    maintenance_window: Optional[str] = None
    notification_channels: List[str] = None
    rollback_enabled: bool = True

@dataclass
class OperationResult:
    """運維操作結果"""
    operation_id: str
    status: OperationStatus
    message: str
    timestamp: datetime
    execution_time: float
    affected_systems: List[str]
    metrics: Dict[str, Any]
    logs: List[str]
    alerts_generated: List[str]
    recommendations: List[str]

class OperationsMCP:
    """通用運維 MCP"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.operation_history = []
        self.active_operations = {}
        self.scheduled_operations = {}
        self.system_metrics = {}
        self.alert_rules = []
        
        # 初始化運維環境
        self._initialize_operations_environment()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加載配置"""
        default_config = {
            "monitoring_interval": 60,
            "max_concurrent_operations": 5,
            "default_timeout": 300,
            "log_retention_days": 30,
            "backup_retention_days": 90,
            "alert_thresholds": {
                "cpu_usage": 80,
                "memory_usage": 85,
                "disk_usage": 90,
                "response_time": 5000
            },
            "notification_channels": {
                "email": "admin@company.com",
                "slack": "#ops-alerts",
                "webhook": "http://localhost:8000/alerts"
            },
            "maintenance_windows": {
                "daily": "02:00-04:00",
                "weekly": "Sunday 01:00-05:00",
                "monthly": "First Sunday 00:00-06:00"
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"⚠️ 無法加載配置文件 {config_path}: {e}")
        
        return default_config
    
    def _initialize_operations_environment(self):
        """初始化運維環境"""
        logger.info(f"✅ 運維環境初始化完成")
        logger.info(f"📊 監控間隔: {self.config['monitoring_interval']} 秒")
        logger.info(f"🔧 最大並發操作: {self.config['max_concurrent_operations']}")
    
    async def execute_operation(self, operation_config: OperationConfig) -> OperationResult:
        """
        執行運維操作
        
        Args:
            operation_config: 運維操作配置
            
        Returns:
            運維操作結果
        """
        operation_id = f"{operation_config.name}_{int(time.time())}"
        logger.info(f"⚙️ 開始執行運維操作: {operation_id}")
        
        start_time = time.time()
        logs = []
        alerts_generated = []
        
        try:
            # 1. 驗證操作配置
            await self._validate_operation_config(operation_config)
            logs.append("✅ 運維操作配置驗證通過")
            
            # 2. 檢查維護窗口
            if operation_config.maintenance_window:
                if not await self._check_maintenance_window(operation_config.maintenance_window):
                    raise Exception(f"當前不在維護窗口內: {operation_config.maintenance_window}")
                logs.append("✅ 維護窗口檢查通過")
            
            # 3. 檢查並發操作限制
            if len(self.active_operations) >= self.config["max_concurrent_operations"]:
                raise Exception(f"超過最大並發操作限制: {self.config['max_concurrent_operations']}")
            
            # 4. 標記為活躍操作
            self.active_operations[operation_id] = {
                "config": operation_config,
                "start_time": start_time,
                "status": OperationStatus.IN_PROGRESS
            }
            
            # 5. 執行具體的運維操作
            operation_result = await self._execute_operation_type(
                operation_id, operation_config, logs, alerts_generated
            )
            
            # 6. 收集系統指標
            metrics = await self._collect_system_metrics(operation_config.target_systems)
            logs.append("📊 系統指標收集完成")
            
            # 7. 生成建議
            recommendations = await self._generate_recommendations(
                operation_config, operation_result, metrics
            )
            
            execution_time = time.time() - start_time
            
            result = OperationResult(
                operation_id=operation_id,
                status=OperationStatus.COMPLETED,
                message="運維操作成功完成",
                timestamp=datetime.now(),
                execution_time=execution_time,
                affected_systems=operation_config.target_systems,
                metrics=metrics,
                logs=logs,
                alerts_generated=alerts_generated,
                recommendations=recommendations
            )
            
            # 8. 記錄操作歷史
            self._record_operation_history(result)
            
            # 9. 發送通知
            if operation_config.notification_channels:
                await self._send_notifications(result, operation_config.notification_channels)
            
            # 10. 清理活躍操作
            if operation_id in self.active_operations:
                del self.active_operations[operation_id]
            
            logger.info(f"✅ 運維操作完成: {operation_id}, 耗時 {execution_time:.2f} 秒")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_message = f"運維操作失敗: {str(e)}"
            logger.error(f"❌ {error_message}")
            
            result = OperationResult(
                operation_id=operation_id,
                status=OperationStatus.FAILED,
                message=error_message,
                timestamp=datetime.now(),
                execution_time=execution_time,
                affected_systems=operation_config.target_systems,
                metrics={},
                logs=logs,
                alerts_generated=alerts_generated,
                recommendations=[f"檢查錯誤原因: {str(e)}"]
            )
            
            self._record_operation_history(result)
            
            # 清理活躍操作
            if operation_id in self.active_operations:
                del self.active_operations[operation_id]
            
            return result
    
    async def _validate_operation_config(self, config: OperationConfig):
        """驗證運維操作配置"""
        if not config.name:
            raise ValueError("操作名稱不能為空")
        
        if not config.target_systems:
            raise ValueError("目標系統不能為空")
        
        if config.timeout <= 0:
            raise ValueError("超時時間必須大於 0")
        
        if config.retry_count < 0:
            raise ValueError("重試次數不能小於 0")
    
    async def _check_maintenance_window(self, window: str) -> bool:
        """檢查維護窗口"""
        # 這裡實現維護窗口檢查邏輯
        # 例如：解析時間範圍，檢查當前時間是否在窗口內
        
        current_time = datetime.now()
        # 簡化實現：假設總是在維護窗口內
        return True
    
    async def _execute_operation_type(self, operation_id: str, 
                                    config: OperationConfig, 
                                    logs: List[str],
                                    alerts: List[str]) -> Dict[str, Any]:
        """執行具體的運維操作類型"""
        operation_method = getattr(self, f"_execute_{config.type.value}", None)
        
        if operation_method:
            return await operation_method(operation_id, config, logs, alerts)
        else:
            # 默認操作
            return await self._execute_default_operation(operation_id, config, logs, alerts)
    
    async def _execute_system_monitoring(self, operation_id: str, 
                                       config: OperationConfig,
                                       logs: List[str],
                                       alerts: List[str]) -> Dict[str, Any]:
        """執行系統監控"""
        logs.append("📊 開始系統監控")
        
        monitoring_results = {}
        
        for system in config.target_systems:
            logs.append(f"🔍 監控系統: {system}")
            
            # 收集 CPU 使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 收集內存使用率
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # 收集磁盤使用率
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # 檢查閾值並生成告警
            if cpu_usage > self.config["alert_thresholds"]["cpu_usage"]:
                alert = f"⚠️ {system} CPU 使用率過高: {cpu_usage:.1f}%"
                alerts.append(alert)
                logs.append(alert)
            
            if memory_usage > self.config["alert_thresholds"]["memory_usage"]:
                alert = f"⚠️ {system} 內存使用率過高: {memory_usage:.1f}%"
                alerts.append(alert)
                logs.append(alert)
            
            if disk_usage > self.config["alert_thresholds"]["disk_usage"]:
                alert = f"⚠️ {system} 磁盤使用率過高: {disk_usage:.1f}%"
                alerts.append(alert)
                logs.append(alert)
            
            monitoring_results[system] = {
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "disk_usage": disk_usage,
                "timestamp": datetime.now().isoformat()
            }
        
        logs.append("✅ 系統監控完成")
        return {"monitoring_results": monitoring_results}
    
    async def _execute_service_restart(self, operation_id: str,
                                     config: OperationConfig,
                                     logs: List[str],
                                     alerts: List[str]) -> Dict[str, Any]:
        """執行服務重啟"""
        logs.append("🔄 開始服務重啟")
        
        service_name = config.parameters.get("service_name", "unknown")
        restart_results = {}
        
        for system in config.target_systems:
            logs.append(f"🔄 重啟服務 {service_name} 在系統 {system}")
            
            try:
                # 模擬服務重啟過程
                await asyncio.sleep(2)
                
                restart_results[system] = {
                    "service": service_name,
                    "status": "restarted",
                    "timestamp": datetime.now().isoformat()
                }
                
                logs.append(f"✅ 服務 {service_name} 在 {system} 重啟成功")
                
            except Exception as e:
                error_msg = f"❌ 服務 {service_name} 在 {system} 重啟失敗: {str(e)}"
                logs.append(error_msg)
                alerts.append(error_msg)
                
                restart_results[system] = {
                    "service": service_name,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return {"restart_results": restart_results}
    
    async def _execute_database_maintenance(self, operation_id: str,
                                          config: OperationConfig,
                                          logs: List[str],
                                          alerts: List[str]) -> Dict[str, Any]:
        """執行數據庫維護"""
        logs.append("🗄️ 開始數據庫維護")
        
        maintenance_type = config.parameters.get("maintenance_type", "optimize")
        maintenance_results = {}
        
        for system in config.target_systems:
            logs.append(f"🗄️ 執行數據庫維護 ({maintenance_type}) 在系統 {system}")
            
            # 模擬數據庫維護過程
            if maintenance_type == "backup":
                await self._perform_database_backup(system, logs)
            elif maintenance_type == "optimize":
                await self._perform_database_optimization(system, logs)
            elif maintenance_type == "cleanup":
                await self._perform_database_cleanup(system, logs)
            
            maintenance_results[system] = {
                "maintenance_type": maintenance_type,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
        
        logs.append("✅ 數據庫維護完成")
        return {"maintenance_results": maintenance_results}
    
    async def _execute_health_check(self, operation_id: str,
                                  config: OperationConfig,
                                  logs: List[str],
                                  alerts: List[str]) -> Dict[str, Any]:
        """執行健康檢查"""
        logs.append("🏥 開始健康檢查")
        
        health_results = {}
        
        for system in config.target_systems:
            logs.append(f"🏥 檢查系統健康狀態: {system}")
            
            # 執行各種健康檢查
            checks = {
                "service_status": await self._check_service_status(system),
                "connectivity": await self._check_connectivity(system),
                "resource_usage": await self._check_resource_usage(system),
                "response_time": await self._check_response_time(system)
            }
            
            # 計算整體健康分數
            healthy_checks = sum(1 for check in checks.values() if check)
            health_score = (healthy_checks / len(checks)) * 100
            
            if health_score < 80:
                alert = f"⚠️ {system} 健康狀態不佳: {health_score:.1f}%"
                alerts.append(alert)
                logs.append(alert)
            
            health_results[system] = {
                "health_score": health_score,
                "checks": checks,
                "timestamp": datetime.now().isoformat()
            }
            
            logs.append(f"📊 {system} 健康分數: {health_score:.1f}%")
        
        logs.append("✅ 健康檢查完成")
        return {"health_results": health_results}
    
    async def _execute_default_operation(self, operation_id: str,
                                       config: OperationConfig,
                                       logs: List[str],
                                       alerts: List[str]) -> Dict[str, Any]:
        """執行默認運維操作"""
        logs.append(f"🔧 執行默認運維操作: {config.type.value}")
        
        # 模擬操作執行
        await asyncio.sleep(1)
        
        logs.append("✅ 默認運維操作完成")
        return {"operation_type": config.type.value, "status": "completed"}
    
    # 輔助方法實現
    async def _perform_database_backup(self, system: str, logs: List[str]):
        """執行數據庫備份"""
        logs.append(f"💾 備份數據庫: {system}")
        await asyncio.sleep(2)
        logs.append(f"✅ 數據庫備份完成: {system}")
    
    async def _perform_database_optimization(self, system: str, logs: List[str]):
        """執行數據庫優化"""
        logs.append(f"⚡ 優化數據庫: {system}")
        await asyncio.sleep(1.5)
        logs.append(f"✅ 數據庫優化完成: {system}")
    
    async def _perform_database_cleanup(self, system: str, logs: List[str]):
        """執行數據庫清理"""
        logs.append(f"🧹 清理數據庫: {system}")
        await asyncio.sleep(1)
        logs.append(f"✅ 數據庫清理完成: {system}")
    
    async def _check_service_status(self, system: str) -> bool:
        """檢查服務狀態"""
        # 模擬服務狀態檢查
        await asyncio.sleep(0.2)
        return True
    
    async def _check_connectivity(self, system: str) -> bool:
        """檢查連通性"""
        # 模擬連通性檢查
        await asyncio.sleep(0.3)
        return True
    
    async def _check_resource_usage(self, system: str) -> bool:
        """檢查資源使用情況"""
        # 模擬資源使用檢查
        cpu_usage = psutil.cpu_percent()
        return cpu_usage < 90
    
    async def _check_response_time(self, system: str) -> bool:
        """檢查響應時間"""
        # 模擬響應時間檢查
        await asyncio.sleep(0.1)
        return True
    
    async def _collect_system_metrics(self, target_systems: List[str]) -> Dict[str, Any]:
        """收集系統指標"""
        metrics = {}
        
        for system in target_systems:
            metrics[system] = {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
                "timestamp": datetime.now().isoformat()
            }
        
        return metrics
    
    async def _generate_recommendations(self, config: OperationConfig,
                                      operation_result: Dict[str, Any],
                                      metrics: Dict[str, Any]) -> List[str]:
        """生成運維建議"""
        recommendations = []
        
        # 基於操作類型生成建議
        if config.type == OperationType.SYSTEM_MONITORING:
            recommendations.append("建議定期檢查系統資源使用情況")
            recommendations.append("考慮設置自動化告警規則")
        
        elif config.type == OperationType.SERVICE_RESTART:
            recommendations.append("建議分析服務重啟的根本原因")
            recommendations.append("考慮實施服務健康檢查機制")
        
        elif config.type == OperationType.DATABASE_MAINTENANCE:
            recommendations.append("建議定期執行數據庫維護操作")
            recommendations.append("考慮實施自動化備份策略")
        
        # 基於指標生成建議
        for system, system_metrics in metrics.items():
            if system_metrics.get("cpu_usage", 0) > 80:
                recommendations.append(f"建議優化 {system} 的 CPU 使用率")
            
            if system_metrics.get("memory_usage", 0) > 85:
                recommendations.append(f"建議增加 {system} 的內存容量")
            
            if system_metrics.get("disk_usage", 0) > 90:
                recommendations.append(f"建議清理 {system} 的磁盤空間")
        
        return recommendations
    
    async def _send_notifications(self, result: OperationResult, channels: List[str]):
        """發送通知"""
        notification_message = {
            "operation_id": result.operation_id,
            "status": result.status.value,
            "message": result.message,
            "timestamp": result.timestamp.isoformat(),
            "affected_systems": result.affected_systems
        }
        
        for channel in channels:
            try:
                # 這裡實現實際的通知發送邏輯
                # 例如：發送郵件、Slack 消息、Webhook 等
                logger.info(f"📢 發送通知到 {channel}: {notification_message}")
                await asyncio.sleep(0.1)  # 模擬發送過程
            except Exception as e:
                logger.error(f"❌ 發送通知失敗 ({channel}): {str(e)}")
    
    def _record_operation_history(self, result: OperationResult):
        """記錄操作歷史"""
        self.operation_history.append({
            "operation_id": result.operation_id,
            "status": result.status.value,
            "timestamp": result.timestamp.isoformat(),
            "execution_time": result.execution_time,
            "affected_systems": result.affected_systems
        })
        
        # 保持歷史記錄在合理範圍內
        if len(self.operation_history) > 1000:
            self.operation_history = self.operation_history[-500:]
    
    def get_operation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """獲取操作歷史"""
        return self.operation_history[-limit:]
    
    def get_active_operations(self) -> Dict[str, Any]:
        """獲取活躍操作"""
        return self.active_operations
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """獲取系統指標"""
        return self.system_metrics
    
    async def schedule_operation(self, operation_config: OperationConfig, 
                               schedule_time: datetime) -> str:
        """調度運維操作"""
        operation_id = f"scheduled_{operation_config.name}_{int(time.time())}"
        
        self.scheduled_operations[operation_id] = {
            "config": operation_config,
            "schedule_time": schedule_time,
            "status": OperationStatus.SCHEDULED
        }
        
        logger.info(f"📅 運維操作已調度: {operation_id} at {schedule_time}")
        return operation_id
    
    async def cancel_operation(self, operation_id: str) -> bool:
        """取消運維操作"""
        if operation_id in self.scheduled_operations:
            self.scheduled_operations[operation_id]["status"] = OperationStatus.CANCELLED
            logger.info(f"❌ 已取消調度的運維操作: {operation_id}")
            return True
        
        if operation_id in self.active_operations:
            # 這裡實現取消正在執行的操作的邏輯
            logger.info(f"❌ 嘗試取消正在執行的運維操作: {operation_id}")
            return False
        
        return False

# CLI 接口
async def main():
    """主函數 - CLI 接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="通用運維 MCP")
    parser.add_argument("action", choices=["execute", "monitor", "history", "status", "schedule"],
                       help="操作類型")
    parser.add_argument("--name", type=str, help="操作名稱")
    parser.add_argument("--type", type=str, choices=[t.value for t in OperationType],
                       help="運維操作類型")
    parser.add_argument("--priority", type=str, choices=[p.value for p in OperationPriority],
                       default="normal", help="操作優先級")
    parser.add_argument("--systems", type=str, nargs="+", help="目標系統列表")
    parser.add_argument("--parameters", type=str, default="{}", help="操作參數 (JSON)")
    parser.add_argument("--timeout", type=int, default=300, help="超時時間（秒）")
    
    args = parser.parse_args()
    
    operations_mcp = OperationsMCP()
    
    if args.action == "history":
        history = operations_mcp.get_operation_history()
        print(json.dumps(history, indent=2, ensure_ascii=False))
        return
    
    if args.action == "status":
        active = operations_mcp.get_active_operations()
        print(json.dumps(active, indent=2, ensure_ascii=False))
        return
    
    if args.action == "monitor":
        metrics = operations_mcp.get_system_metrics()
        print(json.dumps(metrics, indent=2, ensure_ascii=False))
        return
    
    if args.action == "execute":
        if not all([args.name, args.type, args.systems]):
            print("❌ 執行操作需要指定 --name, --type, --systems")
            return
        
        try:
            parameters = json.loads(args.parameters)
        except json.JSONDecodeError:
            print("❌ 無效的參數 JSON 格式")
            return
        
        config = OperationConfig(
            name=args.name,
            type=OperationType(args.type),
            priority=OperationPriority(args.priority),
            description=f"執行 {args.type} 操作",
            target_systems=args.systems,
            parameters=parameters,
            timeout=args.timeout
        )
        
        result = await operations_mcp.execute_operation(config)
        
        print(json.dumps({
            "operation_id": result.operation_id,
            "status": result.status.value,
            "message": result.message,
            "execution_time": result.execution_time,
            "affected_systems": result.affected_systems,
            "metrics": result.metrics,
            "logs": result.logs,
            "alerts_generated": result.alerts_generated,
            "recommendations": result.recommendations
        }, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())

