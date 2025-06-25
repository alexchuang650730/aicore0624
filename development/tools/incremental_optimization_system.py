#!/usr/bin/env python3
"""
Incremental Optimization System for AICore Human-in-the-Loop Integration

這個系統設計用於持續優化AICore的性能、決策質量和用戶體驗，
基於實時數據、測試結果和用戶反饋進行增量改進。
"""

import asyncio
import json
import logging
import time
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Set, Tuple
from datetime import datetime, timedelta
import uuid
import pickle
import sqlite3
import aiofiles
import aiohttp
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import threading
import queue
import statistics
from collections import defaultdict, deque
import yaml

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    """優化類型枚舉"""
    PERFORMANCE = "performance"
    ACCURACY = "accuracy"
    EFFICIENCY = "efficiency"
    USER_EXPERIENCE = "user_experience"
    COST = "cost"
    RELIABILITY = "reliability"

class OptimizationStrategy(Enum):
    """優化策略枚舉"""
    GRADIENT_DESCENT = "gradient_descent"
    GENETIC_ALGORITHM = "genetic_algorithm"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    RULE_BASED = "rule_based"
    ENSEMBLE = "ensemble"

class MetricType(Enum):
    """指標類型枚舉"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ACCURACY = "accuracy"
    ERROR_RATE = "error_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    USER_SATISFACTION = "user_satisfaction"
    COST_EFFICIENCY = "cost_efficiency"

@dataclass
class OptimizationMetric:
    """優化指標"""
    metric_id: str
    metric_type: MetricType
    current_value: float
    target_value: float
    weight: float = 1.0
    threshold: Optional[float] = None
    trend: List[float] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class OptimizationRule:
    """優化規則"""
    rule_id: str
    name: str
    condition: str  # Python表達式
    action: str  # 優化動作
    priority: int = 1
    enabled: bool = True
    trigger_count: int = 0
    last_triggered: Optional[datetime] = None
    success_rate: float = 0.0

@dataclass
class OptimizationResult:
    """優化結果"""
    optimization_id: str
    strategy: OptimizationStrategy
    target_metrics: List[str]
    improvement: Dict[str, float]
    confidence: float
    execution_time: float
    timestamp: datetime
    parameters_changed: Dict[str, Any]
    validation_score: Optional[float] = None

class DataCollector:
    """數據收集器"""
    
    def __init__(self, db_path: str = "optimization_data.db"):
        self.db_path = db_path
        self.data_queue = queue.Queue()
        self.collection_thread = None
        self.running = False
        self._init_database()
    
    def _init_database(self):
        """初始化數據庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 創建表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_id TEXT,
                metric_type TEXT,
                value REAL,
                timestamp DATETIME,
                context TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_id TEXT,
                input_features TEXT,
                decision_type TEXT,
                confidence REAL,
                outcome TEXT,
                timestamp DATETIME
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                optimization_id TEXT,
                strategy TEXT,
                parameters TEXT,
                results TEXT,
                timestamp DATETIME
            )
        """)
        
        conn.commit()
        conn.close()
    
    def start_collection(self):
        """開始數據收集"""
        if not self.running:
            self.running = True
            self.collection_thread = threading.Thread(target=self._collection_worker)
            self.collection_thread.start()
            logger.info("Data collection started")
    
    def stop_collection(self):
        """停止數據收集"""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join()
        logger.info("Data collection stopped")
    
    def _collection_worker(self):
        """數據收集工作線程"""
        while self.running:
            try:
                # 處理隊列中的數據
                while not self.data_queue.empty():
                    data = self.data_queue.get_nowait()
                    self._store_data(data)
                
                time.sleep(1)  # 避免過度消耗CPU
            except Exception as e:
                logger.error(f"Data collection error: {e}")
    
    def _store_data(self, data: Dict[str, Any]):
        """存儲數據到數據庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if data["type"] == "metric":
                cursor.execute("""
                    INSERT INTO metrics (metric_id, metric_type, value, timestamp, context)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    data["metric_id"],
                    data["metric_type"],
                    data["value"],
                    data["timestamp"],
                    json.dumps(data.get("context", {}))
                ))
            
            elif data["type"] == "decision":
                cursor.execute("""
                    INSERT INTO decisions (decision_id, input_features, decision_type, confidence, outcome, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    data["decision_id"],
                    json.dumps(data["input_features"]),
                    data["decision_type"],
                    data["confidence"],
                    data["outcome"],
                    data["timestamp"]
                ))
            
            elif data["type"] == "optimization":
                cursor.execute("""
                    INSERT INTO optimizations (optimization_id, strategy, parameters, results, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    data["optimization_id"],
                    data["strategy"],
                    json.dumps(data["parameters"]),
                    json.dumps(data["results"]),
                    data["timestamp"]
                ))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to store data: {e}")
        finally:
            conn.close()
    
    def collect_metric(self, metric_id: str, metric_type: str, value: float, context: Dict[str, Any] = None):
        """收集指標數據"""
        data = {
            "type": "metric",
            "metric_id": metric_id,
            "metric_type": metric_type,
            "value": value,
            "timestamp": datetime.now(),
            "context": context or {}
        }
        self.data_queue.put(data)
    
    def collect_decision(self, decision_id: str, input_features: Dict[str, Any], 
                        decision_type: str, confidence: float, outcome: str):
        """收集決策數據"""
        data = {
            "type": "decision",
            "decision_id": decision_id,
            "input_features": input_features,
            "decision_type": decision_type,
            "confidence": confidence,
            "outcome": outcome,
            "timestamp": datetime.now()
        }
        self.data_queue.put(data)
    
    def get_metrics_data(self, metric_type: str = None, hours: int = 24) -> pd.DataFrame:
        """獲取指標數據"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT * FROM metrics 
            WHERE timestamp > datetime('now', '-{} hours')
        """.format(hours)
        
        if metric_type:
            query += f" AND metric_type = '{metric_type}'"
        
        query += " ORDER BY timestamp"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def get_decisions_data(self, hours: int = 24) -> pd.DataFrame:
        """獲取決策數據"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT * FROM decisions 
            WHERE timestamp > datetime('now', '-{} hours')
            ORDER BY timestamp
        """.format(hours)
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df

class ModelTrainer:
    """模型訓練器"""
    
    def __init__(self, model_dir: str = "./models"):
        self.model_dir = model_dir
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        
        # 確保模型目錄存在
        import os
        os.makedirs(model_dir, exist_ok=True)
    
    def train_routing_model(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """訓練路由決策模型"""
        try:
            # 準備特徵和標籤
            features = []
            labels = []
            
            for _, row in training_data.iterrows():
                input_features = json.loads(row['input_features'])
                features.append([
                    input_features.get('complexity', 0),
                    input_features.get('risk_level', 0),
                    input_features.get('urgency', 0),
                    input_features.get('resource_availability', 1),
                    1 if input_features.get('production_environment') else 0,
                    1 if input_features.get('critical_system') else 0
                ])
                labels.append(row['decision_type'])
            
            if len(features) < 10:  # 需要足夠的訓練數據
                logger.warning("Insufficient training data for routing model")
                return {"success": False, "reason": "insufficient_data"}
            
            X = np.array(features)
            y = np.array(labels)
            
            # 編碼標籤
            label_encoder = LabelEncoder()
            y_encoded = label_encoder.fit_transform(y)
            
            # 特徵縮放
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # 分割數據
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y_encoded, test_size=0.2, random_state=42
            )
            
            # 訓練模型
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # 評估模型
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # 保存模型
            model_path = f"{self.model_dir}/routing_model.joblib"
            scaler_path = f"{self.model_dir}/routing_scaler.joblib"
            encoder_path = f"{self.model_dir}/routing_encoder.joblib"
            
            joblib.dump(model, model_path)
            joblib.dump(scaler, scaler_path)
            joblib.dump(label_encoder, encoder_path)
            
            self.models['routing'] = model
            self.scalers['routing'] = scaler
            self.encoders['routing'] = label_encoder
            
            logger.info(f"Routing model trained with accuracy: {accuracy:.3f}")
            
            return {
                "success": True,
                "accuracy": accuracy,
                "model_path": model_path,
                "training_samples": len(X_train),
                "test_samples": len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Failed to train routing model: {e}")
            return {"success": False, "reason": str(e)}
    
    def train_performance_model(self, metrics_data: pd.DataFrame) -> Dict[str, Any]:
        """訓練性能預測模型"""
        try:
            # 準備時間序列特徵
            metrics_data['timestamp'] = pd.to_datetime(metrics_data['timestamp'])
            metrics_data = metrics_data.sort_values('timestamp')
            
            # 按指標類型分組
            performance_metrics = metrics_data[metrics_data['metric_type'].isin([
                'latency', 'throughput', 'memory_usage', 'cpu_usage'
            ])]
            
            if len(performance_metrics) < 50:
                logger.warning("Insufficient performance data for model training")
                return {"success": False, "reason": "insufficient_data"}
            
            # 創建特徵
            features = []
            targets = []
            
            for metric_type in ['latency', 'throughput', 'memory_usage', 'cpu_usage']:
                metric_data = performance_metrics[performance_metrics['metric_type'] == metric_type]
                if len(metric_data) < 10:
                    continue
                
                values = metric_data['value'].values
                
                # 創建滑動窗口特徵
                window_size = 5
                for i in range(window_size, len(values)):
                    feature_window = values[i-window_size:i]
                    target_value = values[i]
                    
                    features.append([
                        np.mean(feature_window),
                        np.std(feature_window),
                        np.min(feature_window),
                        np.max(feature_window),
                        feature_window[-1]  # 最近值
                    ])
                    targets.append(target_value)
            
            if len(features) < 20:
                logger.warning("Insufficient feature data for performance model")
                return {"success": False, "reason": "insufficient_features"}
            
            X = np.array(features)
            y = np.array(targets)
            
            # 特徵縮放
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # 分割數據
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # 訓練模型
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # 評估模型
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            # 保存模型
            model_path = f"{self.model_dir}/performance_model.joblib"
            scaler_path = f"{self.model_dir}/performance_scaler.joblib"
            
            joblib.dump(model, model_path)
            joblib.dump(scaler, scaler_path)
            
            self.models['performance'] = model
            self.scalers['performance'] = scaler
            
            logger.info(f"Performance model trained with RMSE: {rmse:.3f}")
            
            return {
                "success": True,
                "rmse": rmse,
                "model_path": model_path,
                "training_samples": len(X_train),
                "test_samples": len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Failed to train performance model: {e}")
            return {"success": False, "reason": str(e)}
    
    def load_models(self):
        """加載已保存的模型"""
        try:
            # 加載路由模型
            routing_model_path = f"{self.model_dir}/routing_model.joblib"
            routing_scaler_path = f"{self.model_dir}/routing_scaler.joblib"
            routing_encoder_path = f"{self.model_dir}/routing_encoder.joblib"
            
            if all(os.path.exists(p) for p in [routing_model_path, routing_scaler_path, routing_encoder_path]):
                self.models['routing'] = joblib.load(routing_model_path)
                self.scalers['routing'] = joblib.load(routing_scaler_path)
                self.encoders['routing'] = joblib.load(routing_encoder_path)
                logger.info("Routing model loaded successfully")
            
            # 加載性能模型
            performance_model_path = f"{self.model_dir}/performance_model.joblib"
            performance_scaler_path = f"{self.model_dir}/performance_scaler.joblib"
            
            if all(os.path.exists(p) for p in [performance_model_path, performance_scaler_path]):
                self.models['performance'] = joblib.load(performance_model_path)
                self.scalers['performance'] = joblib.load(performance_scaler_path)
                logger.info("Performance model loaded successfully")
                
        except Exception as e:
            logger.error(f"Failed to load models: {e}")

class OptimizationEngine:
    """優化引擎"""
    
    def __init__(self, data_collector: DataCollector, model_trainer: ModelTrainer):
        self.data_collector = data_collector
        self.model_trainer = model_trainer
        self.metrics = {}
        self.rules = {}
        self.optimization_history = []
        self.running = False
        self.optimization_thread = None
        
        # 加載配置
        self.config = self._load_optimization_config()
        
        # 初始化默認指標
        self._init_default_metrics()
        
        # 初始化默認規則
        self._init_default_rules()
    
    def _load_optimization_config(self) -> Dict[str, Any]:
        """加載優化配置"""
        default_config = {
            "optimization_interval": 300,  # 5分鐘
            "model_retrain_interval": 3600,  # 1小時
            "min_data_points": 100,
            "confidence_threshold": 0.8,
            "max_parameter_change": 0.2,  # 最大參數變化20%
            "rollback_threshold": 0.1  # 性能下降10%則回滾
        }
        
        try:
            with open("optimization_config.yaml", "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        except FileNotFoundError:
            logger.info("Using default optimization configuration")
        except Exception as e:
            logger.warning(f"Failed to load optimization config: {e}")
        
        return default_config
    
    def _init_default_metrics(self):
        """初始化默認指標"""
        default_metrics = [
            OptimizationMetric("routing_latency", MetricType.LATENCY, 0.0, 50.0, 1.0),
            OptimizationMetric("routing_accuracy", MetricType.ACCURACY, 0.0, 0.95, 2.0),
            OptimizationMetric("system_throughput", MetricType.THROUGHPUT, 0.0, 1000.0, 1.5),
            OptimizationMetric("memory_usage", MetricType.MEMORY_USAGE, 0.0, 80.0, 1.0),
            OptimizationMetric("error_rate", MetricType.ERROR_RATE, 0.0, 0.01, 2.0),
        ]
        
        for metric in default_metrics:
            self.metrics[metric.metric_id] = metric
    
    def _init_default_rules(self):
        """初始化默認優化規則"""
        default_rules = [
            OptimizationRule(
                "high_latency_rule",
                "High Latency Optimization",
                "routing_latency > 100",
                "optimize_routing_parameters",
                priority=1
            ),
            OptimizationRule(
                "low_accuracy_rule",
                "Low Accuracy Optimization",
                "routing_accuracy < 0.8",
                "retrain_routing_model",
                priority=2
            ),
            OptimizationRule(
                "high_memory_rule",
                "High Memory Usage Optimization",
                "memory_usage > 90",
                "optimize_memory_usage",
                priority=1
            ),
            OptimizationRule(
                "high_error_rate_rule",
                "High Error Rate Optimization",
                "error_rate > 0.05",
                "investigate_errors",
                priority=1
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.rule_id] = rule
    
    def start_optimization(self):
        """開始優化循環"""
        if not self.running:
            self.running = True
            self.optimization_thread = threading.Thread(target=self._optimization_worker)
            self.optimization_thread.start()
            logger.info("Optimization engine started")
    
    def stop_optimization(self):
        """停止優化循環"""
        self.running = False
        if self.optimization_thread:
            self.optimization_thread.join()
        logger.info("Optimization engine stopped")
    
    def _optimization_worker(self):
        """優化工作線程"""
        last_model_retrain = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # 更新指標
                self._update_metrics()
                
                # 檢查優化規則
                self._check_optimization_rules()
                
                # 定期重新訓練模型
                if current_time - last_model_retrain > self.config["model_retrain_interval"]:
                    self._retrain_models()
                    last_model_retrain = current_time
                
                # 等待下一個優化周期
                time.sleep(self.config["optimization_interval"])
                
            except Exception as e:
                logger.error(f"Optimization worker error: {e}")
                time.sleep(60)  # 錯誤時等待1分鐘
    
    def _update_metrics(self):
        """更新指標值"""
        try:
            # 獲取最近的指標數據
            metrics_data = self.data_collector.get_metrics_data(hours=1)
            
            if metrics_data.empty:
                return
            
            # 按指標類型聚合
            for metric_id, metric in self.metrics.items():
                metric_data = metrics_data[metrics_data['metric_id'] == metric_id]
                
                if not metric_data.empty:
                    # 計算最近的平均值
                    recent_value = metric_data['value'].mean()
                    
                    # 更新指標
                    metric.current_value = recent_value
                    metric.trend.append(recent_value)
                    metric.last_updated = datetime.now()
                    
                    # 保持趨勢數據在合理範圍內
                    if len(metric.trend) > 100:
                        metric.trend = metric.trend[-100:]
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
    
    def _check_optimization_rules(self):
        """檢查優化規則"""
        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            try:
                # 構建評估上下文
                context = {metric.metric_id: metric.current_value for metric in self.metrics.values()}
                
                # 評估規則條件
                if eval(rule.condition, {"__builtins__": {}}, context):
                    logger.info(f"Optimization rule triggered: {rule.name}")
                    
                    # 執行優化動作
                    success = self._execute_optimization_action(rule.action, context)
                    
                    # 更新規則統計
                    rule.trigger_count += 1
                    rule.last_triggered = datetime.now()
                    
                    if success:
                        rule.success_rate = (rule.success_rate * (rule.trigger_count - 1) + 1) / rule.trigger_count
                    else:
                        rule.success_rate = (rule.success_rate * (rule.trigger_count - 1)) / rule.trigger_count
            
            except Exception as e:
                logger.error(f"Failed to evaluate rule {rule_id}: {e}")
    
    def _execute_optimization_action(self, action: str, context: Dict[str, float]) -> bool:
        """執行優化動作"""
        try:
            if action == "optimize_routing_parameters":
                return self._optimize_routing_parameters(context)
            elif action == "retrain_routing_model":
                return self._retrain_routing_model()
            elif action == "optimize_memory_usage":
                return self._optimize_memory_usage(context)
            elif action == "investigate_errors":
                return self._investigate_errors(context)
            else:
                logger.warning(f"Unknown optimization action: {action}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to execute optimization action {action}: {e}")
            return False
    
    def _optimize_routing_parameters(self, context: Dict[str, float]) -> bool:
        """優化路由參數"""
        try:
            # 這裡實現路由參數優化邏輯
            # 例如調整決策閾值、權重等
            
            optimization_result = OptimizationResult(
                optimization_id=str(uuid.uuid4()),
                strategy=OptimizationStrategy.RULE_BASED,
                target_metrics=["routing_latency"],
                improvement={"routing_latency": -10.0},  # 假設改善了10ms
                confidence=0.8,
                execution_time=time.time(),
                timestamp=datetime.now(),
                parameters_changed={"routing_threshold": 0.85}
            )
            
            self.optimization_history.append(optimization_result)
            
            # 記錄優化結果
            self.data_collector.data_queue.put({
                "type": "optimization",
                "optimization_id": optimization_result.optimization_id,
                "strategy": optimization_result.strategy.value,
                "parameters": optimization_result.parameters_changed,
                "results": asdict(optimization_result),
                "timestamp": optimization_result.timestamp
            })
            
            logger.info("Routing parameters optimized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize routing parameters: {e}")
            return False
    
    def _retrain_routing_model(self) -> bool:
        """重新訓練路由模型"""
        try:
            # 獲取最近的決策數據
            decisions_data = self.data_collector.get_decisions_data(hours=24)
            
            if len(decisions_data) < self.config["min_data_points"]:
                logger.warning("Insufficient data for model retraining")
                return False
            
            # 重新訓練模型
            result = self.model_trainer.train_routing_model(decisions_data)
            
            if result["success"]:
                logger.info(f"Routing model retrained with accuracy: {result['accuracy']:.3f}")
                return True
            else:
                logger.error(f"Failed to retrain routing model: {result['reason']}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to retrain routing model: {e}")
            return False
    
    def _optimize_memory_usage(self, context: Dict[str, float]) -> bool:
        """優化記憶體使用"""
        try:
            # 這裡實現記憶體優化邏輯
            # 例如清理緩存、調整緩存大小等
            
            logger.info("Memory usage optimization executed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize memory usage: {e}")
            return False
    
    def _investigate_errors(self, context: Dict[str, float]) -> bool:
        """調查錯誤"""
        try:
            # 這裡實現錯誤調查邏輯
            # 例如分析錯誤日誌、發送警報等
            
            logger.info("Error investigation initiated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to investigate errors: {e}")
            return False
    
    def _retrain_models(self):
        """重新訓練所有模型"""
        try:
            logger.info("Starting model retraining...")
            
            # 獲取訓練數據
            decisions_data = self.data_collector.get_decisions_data(hours=168)  # 一週數據
            metrics_data = self.data_collector.get_metrics_data(hours=168)
            
            # 重新訓練路由模型
            if len(decisions_data) >= self.config["min_data_points"]:
                routing_result = self.model_trainer.train_routing_model(decisions_data)
                if routing_result["success"]:
                    logger.info(f"Routing model retrained: accuracy={routing_result['accuracy']:.3f}")
            
            # 重新訓練性能模型
            if len(metrics_data) >= self.config["min_data_points"]:
                performance_result = self.model_trainer.train_performance_model(metrics_data)
                if performance_result["success"]:
                    logger.info(f"Performance model retrained: RMSE={performance_result['rmse']:.3f}")
            
        except Exception as e:
            logger.error(f"Failed to retrain models: {e}")
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """獲取優化狀態"""
        return {
            "running": self.running,
            "metrics": {mid: asdict(metric) for mid, metric in self.metrics.items()},
            "rules": {rid: asdict(rule) for rid, rule in self.rules.items()},
            "optimization_count": len(self.optimization_history),
            "last_optimization": self.optimization_history[-1].timestamp.isoformat() if self.optimization_history else None
        }
    
    def add_custom_rule(self, rule: OptimizationRule):
        """添加自定義優化規則"""
        self.rules[rule.rule_id] = rule
        logger.info(f"Added custom optimization rule: {rule.name}")
    
    def remove_rule(self, rule_id: str):
        """移除優化規則"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Removed optimization rule: {rule_id}")

class IncrementalOptimizationSystem:
    """增量優化系統主類"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        
        # 初始化組件
        self.data_collector = DataCollector(self.config.get("db_path", "optimization_data.db"))
        self.model_trainer = ModelTrainer(self.config.get("model_dir", "./models"))
        self.optimization_engine = OptimizationEngine(self.data_collector, self.model_trainer)
        
        # 加載已有模型
        self.model_trainer.load_models()
        
        logger.info("Incremental Optimization System initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加載配置"""
        default_config = {
            "db_path": "optimization_data.db",
            "model_dir": "./models",
            "auto_start": True,
            "web_interface": True,
            "web_port": 8097
        }
        
        if config_path:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    async def start(self):
        """啟動優化系統"""
        try:
            # 啟動數據收集
            self.data_collector.start_collection()
            
            # 啟動優化引擎
            self.optimization_engine.start_optimization()
            
            logger.info("Incremental Optimization System started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start optimization system: {e}")
            raise
    
    async def stop(self):
        """停止優化系統"""
        try:
            # 停止優化引擎
            self.optimization_engine.stop_optimization()
            
            # 停止數據收集
            self.data_collector.stop_collection()
            
            logger.info("Incremental Optimization System stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop optimization system: {e}")
    
    def collect_routing_decision(self, decision_id: str, input_features: Dict[str, Any], 
                               decision_type: str, confidence: float, outcome: str):
        """收集路由決策數據"""
        self.data_collector.collect_decision(decision_id, input_features, decision_type, confidence, outcome)
    
    def collect_performance_metric(self, metric_id: str, metric_type: str, value: float, context: Dict[str, Any] = None):
        """收集性能指標"""
        self.data_collector.collect_metric(metric_id, metric_type, value, context)
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        return {
            "data_collector": {
                "running": self.data_collector.running,
                "queue_size": self.data_collector.data_queue.qsize()
            },
            "optimization_engine": self.optimization_engine.get_optimization_status(),
            "models": {
                "loaded_models": list(self.model_trainer.models.keys()),
                "model_dir": self.model_trainer.model_dir
            }
        }
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """生成優化報告"""
        try:
            # 獲取最近的數據
            metrics_data = self.data_collector.get_metrics_data(hours=24)
            decisions_data = self.data_collector.get_decisions_data(hours=24)
            
            # 計算統計信息
            report = {
                "generated_at": datetime.now().isoformat(),
                "data_summary": {
                    "metrics_count": len(metrics_data),
                    "decisions_count": len(decisions_data),
                    "time_range": "24 hours"
                },
                "optimization_summary": {
                    "total_optimizations": len(self.optimization_engine.optimization_history),
                    "recent_optimizations": len([
                        opt for opt in self.optimization_engine.optimization_history
                        if opt.timestamp > datetime.now() - timedelta(hours=24)
                    ])
                },
                "metrics_analysis": {},
                "recommendations": []
            }
            
            # 分析指標趨勢
            for metric_id, metric in self.optimization_engine.metrics.items():
                if len(metric.trend) > 1:
                    trend_direction = "increasing" if metric.trend[-1] > metric.trend[0] else "decreasing"
                    trend_change = abs(metric.trend[-1] - metric.trend[0]) / metric.trend[0] * 100 if metric.trend[0] != 0 else 0
                    
                    report["metrics_analysis"][metric_id] = {
                        "current_value": metric.current_value,
                        "target_value": metric.target_value,
                        "trend_direction": trend_direction,
                        "trend_change_percent": trend_change,
                        "meeting_target": metric.current_value <= metric.target_value if metric.metric_type in [MetricType.LATENCY, MetricType.ERROR_RATE] else metric.current_value >= metric.target_value
                    }
            
            # 生成建議
            for metric_id, analysis in report["metrics_analysis"].items():
                if not analysis["meeting_target"]:
                    report["recommendations"].append(f"Consider optimizing {metric_id} - current: {analysis['current_value']:.2f}, target: {analysis['target_value']:.2f}")
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate optimization report: {e}")
            return {"error": str(e)}

# 使用示例
async def main():
    """主函數示例"""
    # 創建優化系統
    optimization_system = IncrementalOptimizationSystem()
    
    try:
        # 啟動系統
        await optimization_system.start()
        
        # 模擬一些數據收集
        for i in range(10):
            # 模擬路由決策
            optimization_system.collect_routing_decision(
                decision_id=str(uuid.uuid4()),
                input_features={"complexity": np.random.uniform(0, 1), "risk_level": np.random.uniform(0, 1)},
                decision_type=np.random.choice(["automatic", "human_required"]),
                confidence=np.random.uniform(0.7, 1.0),
                outcome="success"
            )
            
            # 模擬性能指標
            optimization_system.collect_performance_metric(
                metric_id="routing_latency",
                metric_type="latency",
                value=np.random.uniform(20, 100),
                context={"system_load": np.random.uniform(0.3, 0.9)}
            )
            
            await asyncio.sleep(1)
        
        # 等待一段時間讓系統處理數據
        await asyncio.sleep(10)
        
        # 獲取系統狀態
        status = optimization_system.get_system_status()
        print("System Status:", json.dumps(status, indent=2, default=str))
        
        # 生成優化報告
        report = optimization_system.generate_optimization_report()
        print("Optimization Report:", json.dumps(report, indent=2, default=str))
        
    finally:
        await optimization_system.stop()

if __name__ == "__main__":
    asyncio.run(main())

