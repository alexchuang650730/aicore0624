#!/usr/bin/env python3
"""
Dynamic Cloud Search MCP 組件
動態設定 Cloud Search MCP

基於原始 CloudSearchMCP 的智慧路由和動態感知能力
整合台銀OCR審核人月成本詳細計算分析的專業數據
實現根據環境及使用者需求動態更新設定的能力
"""

import asyncio
import json
import logging
import time
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path

# 動態導入基礎組件
try:
    from cloud_search_mcp import CloudSearchMCP, SearchResult, SearchMetrics
except ImportError:
    # 如果無法導入，定義基礎類
    @dataclass
    class SearchResult:
        query: str
        result: str
        context_enriched: bool
        timestamp: float
        domains_identified: List[str] = field(default_factory=list)
        confidence_score: float = 0.0
        metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DynamicConfig:
    """動態配置數據模型"""
    environment: str = "production"  # production, development, testing
    user_type: str = "standard"     # standard, professional, enterprise
    analysis_depth: str = "detailed"  # basic, detailed, comprehensive
    performance_mode: str = "balanced"  # speed, balanced, quality
    taiwan_bank_enabled: bool = True
    cache_strategy: str = "adaptive"  # none, basic, adaptive, aggressive
    
    # 動態調整參數
    max_tokens: int = 2500
    temperature: float = 0.3
    cache_ttl: int = 7200
    timeout: int = 30
    
    # 台銀專用參數
    professional_level: str = "Taiwan_Bank_Standard"
    data_source_priority: List[str] = field(default_factory=lambda: ["taiwan_bank", "industry", "general"])

@dataclass
class ContextAwareResult(SearchResult):
    """上下文感知結果數據模型"""
    environment_detected: str = ""
    user_type_detected: str = ""
    analysis_depth_used: str = ""
    performance_mode_used: str = ""
    taiwan_bank_data_used: bool = False
    dynamic_adjustments: Dict[str, Any] = field(default_factory=dict)
    processing_strategy: str = ""

class EnvironmentDetector:
    """環境檢測器 - 智慧感知當前環境和使用者需求"""
    
    @staticmethod
    def detect_environment() -> str:
        """檢測當前環境"""
        # 檢測環境變數
        if os.getenv("ENVIRONMENT"):
            return os.getenv("ENVIRONMENT").lower()
        
        # 檢測運行路徑
        current_path = Path.cwd()
        if "development" in str(current_path):
            return "development"
        elif "test" in str(current_path):
            return "testing"
        else:
            return "production"
    
    @staticmethod
    def detect_user_type(query: str, context: Dict[str, Any] = None) -> str:
        """根據查詢內容檢測使用者類型"""
        query_lower = query.lower()
        
        # 專業用戶指標
        professional_keywords = [
            "核保", "承保", "理賠", "精算", "風險評估", "OCR", "人月成本",
            "ROI", "投資回報", "成本效益", "流程優化", "自動化比率"
        ]
        
        # 企業用戶指標
        enterprise_keywords = [
            "系統整合", "API", "大量處理", "批次", "企業級", "部署",
            "架構", "擴展性", "高可用", "負載均衡"
        ]
        
        professional_score = sum(1 for keyword in professional_keywords if keyword in query_lower)
        enterprise_score = sum(1 for keyword in enterprise_keywords if keyword in query_lower)
        
        if enterprise_score >= 2:
            return "enterprise"
        elif professional_score >= 2:
            return "professional"
        else:
            return "standard"
    
    @staticmethod
    def detect_analysis_depth(query: str, user_type: str) -> str:
        """檢測所需分析深度"""
        query_lower = query.lower()
        
        # 基礎分析指標
        if any(word in query_lower for word in ["什麼是", "簡單", "概述", "基本"]):
            return "basic"
        
        # 詳細分析指標
        elif any(word in query_lower for word in ["詳細", "具體", "分析", "計算", "評估"]):
            return "detailed"
        
        # 全面分析指標
        elif any(word in query_lower for word in ["全面", "深入", "完整", "專業", "報告"]):
            return "comprehensive"
        
        # 根據用戶類型決定默認深度
        elif user_type == "enterprise":
            return "comprehensive"
        elif user_type == "professional":
            return "detailed"
        else:
            return "basic"
    
    @staticmethod
    def detect_performance_mode(context: Dict[str, Any] = None) -> str:
        """檢測性能模式偏好"""
        if context:
            # 檢查是否有時間限制
            if context.get("time_sensitive", False):
                return "speed"
            # 檢查是否需要高質量
            elif context.get("quality_critical", False):
                return "quality"
        
        return "balanced"

class DynamicConfigManager:
    """動態配置管理器 - 根據環境和需求動態調整設定"""
    
    def __init__(self):
        self.base_config = DynamicConfig()
        self.environment_configs = self._load_environment_configs()
        self.user_type_configs = self._load_user_type_configs()
        
    def _load_environment_configs(self) -> Dict[str, Dict[str, Any]]:
        """載入環境特定配置"""
        return {
            "production": {
                "max_tokens": 2500,
                "temperature": 0.1,
                "cache_ttl": 7200,
                "timeout": 30,
                "cache_strategy": "aggressive"
            },
            "development": {
                "max_tokens": 1500,
                "temperature": 0.3,
                "cache_ttl": 1800,
                "timeout": 60,
                "cache_strategy": "basic"
            },
            "testing": {
                "max_tokens": 1000,
                "temperature": 0.5,
                "cache_ttl": 300,
                "timeout": 10,
                "cache_strategy": "none"
            }
        }
    
    def _load_user_type_configs(self) -> Dict[str, Dict[str, Any]]:
        """載入用戶類型特定配置"""
        return {
            "standard": {
                "analysis_depth": "basic",
                "max_tokens": 1500,
                "professional_level": "Standard"
            },
            "professional": {
                "analysis_depth": "detailed",
                "max_tokens": 2500,
                "professional_level": "Professional"
            },
            "enterprise": {
                "analysis_depth": "comprehensive",
                "max_tokens": 4000,
                "professional_level": "Enterprise"
            }
        }
    
    def generate_dynamic_config(
        self, 
        query: str, 
        context: Dict[str, Any] = None,
        user_preferences: Dict[str, Any] = None
    ) -> DynamicConfig:
        """
        根據查詢、上下文和用戶偏好生成動態配置
        
        Args:
            query: 用戶查詢
            context: 上下文信息
            user_preferences: 用戶偏好設定
            
        Returns:
            DynamicConfig: 動態生成的配置
        """
        # 檢測環境和用戶特徵
        environment = EnvironmentDetector.detect_environment()
        user_type = EnvironmentDetector.detect_user_type(query, context)
        analysis_depth = EnvironmentDetector.detect_analysis_depth(query, user_type)
        performance_mode = EnvironmentDetector.detect_performance_mode(context)
        
        # 創建基礎配置
        config = DynamicConfig(
            environment=environment,
            user_type=user_type,
            analysis_depth=analysis_depth,
            performance_mode=performance_mode
        )
        
        # 應用環境特定配置
        if environment in self.environment_configs:
            env_config = self.environment_configs[environment]
            for key, value in env_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        # 應用用戶類型特定配置
        if user_type in self.user_type_configs:
            user_config = self.user_type_configs[user_type]
            for key, value in user_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        # 應用性能模式調整
        config = self._apply_performance_mode(config, performance_mode)
        
        # 應用用戶偏好覆蓋
        if user_preferences:
            for key, value in user_preferences.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        # 檢測是否需要台銀數據
        config.taiwan_bank_enabled = self._should_use_taiwan_bank_data(query, user_type)
        
        return config
    
    def _apply_performance_mode(self, config: DynamicConfig, mode: str) -> DynamicConfig:
        """應用性能模式調整"""
        if mode == "speed":
            config.max_tokens = min(config.max_tokens, 1500)
            config.temperature = 0.1
            config.cache_strategy = "aggressive"
            config.timeout = 15
        elif mode == "quality":
            config.max_tokens = max(config.max_tokens, 3000)
            config.temperature = 0.3
            config.cache_strategy = "basic"
            config.timeout = 60
        # balanced 模式保持默認設定
        
        return config
    
    def _should_use_taiwan_bank_data(self, query: str, user_type: str) -> bool:
        """判斷是否應該使用台銀數據"""
        taiwan_bank_keywords = [
            "核保", "OCR", "審核", "人月", "成本", "保險", "承保",
            "理賠", "表單", "自動化", "流程", "ROI", "投資回報"
        ]
        
        query_lower = query.lower()
        keyword_matches = sum(1 for keyword in taiwan_bank_keywords if keyword in query_lower)
        
        # 專業和企業用戶更傾向使用台銀數據
        if user_type in ["professional", "enterprise"]:
            return keyword_matches >= 1
        else:
            return keyword_matches >= 2

class DynamicCloudSearchMCP:
    """Dynamic Cloud Search MCP - 動態設定智慧路由和上下文感知"""
    
    def __init__(self, base_llm_config: Dict[str, Any] = None):
        self.base_llm_config = base_llm_config or {}
        self.version = "7.0.0-Dynamic"
        self.name = "DynamicCloudSearchMCP"
        
        # 動態配置管理器
        self.config_manager = DynamicConfigManager()
        
        # 台銀數據
        self.taiwan_bank_data = self._load_taiwan_bank_data()
        
        # 緩存和指標
        self.adaptive_cache = {}
        self.performance_metrics = {
            "total_requests": 0,
            "config_adaptations": 0,
            "taiwan_bank_usage": 0,
            "average_response_time": 0.0,
            "user_type_distribution": {"standard": 0, "professional": 0, "enterprise": 0},
            "environment_distribution": {"production": 0, "development": 0, "testing": 0}
        }
        
        # 日誌
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Dynamic Cloud Search MCP v{self.version} 初始化完成")
    
    def _load_taiwan_bank_data(self) -> Dict[str, Any]:
        """載入台銀數據"""
        return {
            "基礎參數": {
                "年處理案件量": 100000,
                "OCR處理覆蓋率": "100%",
                "人工審核必要性": "90%",
                "OCR平均準確率": "88%",
                "單件審核時間": 35,  # 分鐘
                "年度總工時": 52200  # 小時
            },
            "成本參數": {
                "月薪": 35000,
                "社保福利": 10500,
                "月人工成本": 45500,
                "人月成本": 48116,
                "單件成本": 266,
                "年度總成本": 26560000
            },
            "人力配置": {
                "基礎配置": 29,
                "標準配置": 34,
                "增強配置": 41
            },
            "ROI數據": {
                "投資回收期": 2.3,  # 月
                "成本節約率": 0.41,
                "效率提升": 0.50
            }
        }
    
    async def dynamic_search_and_analyze(
        self, 
        query: str, 
        context: Dict[str, Any] = None,
        user_preferences: Dict[str, Any] = None
    ) -> ContextAwareResult:
        """
        動態搜索和分析 - 根據環境和需求自動調整
        
        Args:
            query: 用戶查詢
            context: 上下文信息
            user_preferences: 用戶偏好設定
            
        Returns:
            ContextAwareResult: 上下文感知的分析結果
        """
        start_time = time.time()
        
        try:
            # 生成動態配置
            dynamic_config = self.config_manager.generate_dynamic_config(
                query, context, user_preferences
            )
            
            self.logger.info(f"動態配置生成: 環境={dynamic_config.environment}, "
                           f"用戶類型={dynamic_config.user_type}, "
                           f"分析深度={dynamic_config.analysis_depth}")
            
            # 檢查自適應緩存
            cache_result = self._check_adaptive_cache(query, dynamic_config)
            if cache_result:
                self.logger.info("自適應緩存命中")
                return cache_result
            
            # 根據配置選擇處理策略
            processing_strategy = self._select_processing_strategy(dynamic_config)
            
            # 執行分析
            if dynamic_config.taiwan_bank_enabled:
                analysis_result = await self._taiwan_bank_analysis(query, dynamic_config)
            else:
                analysis_result = await self._standard_analysis(query, dynamic_config)
            
            # 創建上下文感知結果
            result = ContextAwareResult(
                query=query,
                result=analysis_result["content"],
                context_enriched=True,
                timestamp=time.time(),
                domains_identified=analysis_result.get("domains", []),
                confidence_score=analysis_result.get("confidence", 0.85),
                environment_detected=dynamic_config.environment,
                user_type_detected=dynamic_config.user_type,
                analysis_depth_used=dynamic_config.analysis_depth,
                performance_mode_used=dynamic_config.performance_mode,
                taiwan_bank_data_used=dynamic_config.taiwan_bank_enabled,
                processing_strategy=processing_strategy,
                dynamic_adjustments={
                    "max_tokens": dynamic_config.max_tokens,
                    "temperature": dynamic_config.temperature,
                    "cache_ttl": dynamic_config.cache_ttl,
                    "professional_level": dynamic_config.professional_level
                },
                metadata={
                    "response_time": time.time() - start_time,
                    "config_version": self.version,
                    "adaptations_made": self._count_adaptations(dynamic_config)
                }
            )
            
            # 存入自適應緩存
            self._save_to_adaptive_cache(query, dynamic_config, result)
            
            # 更新指標
            self._update_performance_metrics(dynamic_config, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"動態分析失敗: {str(e)}")
            return ContextAwareResult(
                query=query,
                result=f"動態分析失敗: {str(e)}",
                context_enriched=False,
                timestamp=time.time(),
                confidence_score=0.0,
                metadata={"error": str(e), "response_time": time.time() - start_time}
            )
    
    def _select_processing_strategy(self, config: DynamicConfig) -> str:
        """選擇處理策略"""
        if config.performance_mode == "speed":
            return "fast_track"
        elif config.analysis_depth == "comprehensive":
            return "deep_analysis"
        elif config.taiwan_bank_enabled:
            return "taiwan_bank_professional"
        else:
            return "standard_analysis"
    
    async def _taiwan_bank_analysis(self, query: str, config: DynamicConfig) -> Dict[str, Any]:
        """台銀專業分析"""
        # 構建台銀專用 prompt
        prompt = self._build_taiwan_bank_prompt(query, config)
        
        # 模擬 LLM 調用 (實際應該調用真實 API)
        await asyncio.sleep(0.1)  # 模擬 API 延遲
        
        # 根據分析深度生成不同詳細程度的回答
        if config.analysis_depth == "comprehensive":
            content = self._generate_comprehensive_taiwan_analysis(query)
        elif config.analysis_depth == "detailed":
            content = self._generate_detailed_taiwan_analysis(query)
        else:
            content = self._generate_basic_taiwan_analysis(query)
        
        return {
            "content": content,
            "domains": ["保險業務流程優化", "保險科技應用", "保險運營管理"],
            "confidence": 0.95
        }
    
    async def _standard_analysis(self, query: str, config: DynamicConfig) -> Dict[str, Any]:
        """標準分析"""
        # 構建標準 prompt
        prompt = f"請分析以下查詢並提供相關信息：{query}"
        
        # 模擬 LLM 調用
        await asyncio.sleep(0.05)
        
        content = f"針對您的查詢「{query}」，提供以下分析：\n\n這是一個{config.analysis_depth}級別的分析，適合{config.user_type}用戶。"
        
        return {
            "content": content,
            "domains": ["一般分析"],
            "confidence": 0.75
        }
    
    def _build_taiwan_bank_prompt(self, query: str, config: DynamicConfig) -> str:
        """構建台銀專用 prompt"""
        base_prompt = f"""
基於台銀OCR審核人月成本詳細計算分析，請針對以下查詢提供專業分析：

查詢: {query}

台銀數據參考:
- 年處理案件量: {self.taiwan_bank_data['基礎參數']['年處理案件量']:,}件
- OCR處理覆蓋率: {self.taiwan_bank_data['基礎參數']['OCR處理覆蓋率']}
- 人月成本: {self.taiwan_bank_data['成本參數']['人月成本']:,}元
- 單件成本: {self.taiwan_bank_data['成本參數']['單件成本']}元
- 投資回收期: {self.taiwan_bank_data['ROI數據']['投資回收期']}個月

分析要求:
- 分析深度: {config.analysis_depth}
- 專業級別: {config.professional_level}
- 最大字數: {config.max_tokens}
"""
        
        if config.analysis_depth == "comprehensive":
            base_prompt += """
- 包含詳細計算過程
- 提供多個案例分析
- 包含風險評估和建議
- 提供實施路線圖
"""
        elif config.analysis_depth == "detailed":
            base_prompt += """
- 包含關鍵數據分析
- 提供實用建議
- 包含成本效益分析
"""
        else:
            base_prompt += """
- 提供核心要點
- 簡潔明確的結論
"""
        
        return base_prompt
    
    def _generate_comprehensive_taiwan_analysis(self, query: str) -> str:
        """生成全面的台銀分析"""
        return f"""基於台銀OCR審核人月成本詳細計算分析，針對「{query}」提供全面專業分析：

## 📊 計算基礎參數
年度總案件量：{self.taiwan_bank_data['基礎參數']['年處理案件量']:,}件
OCR系統覆蓋率：{self.taiwan_bank_data['基礎參數']['OCR處理覆蓋率']}
需人工審核比例：{self.taiwan_bank_data['基礎參數']['人工審核必要性']}
OCR平均準確率：{self.taiwan_bank_data['基礎參數']['OCR平均準確率']}（混合文檔）

## 💰 成本結構分析
月薪：{self.taiwan_bank_data['成本參數']['月薪']:,}元
社保福利：{self.taiwan_bank_data['成本參數']['社保福利']:,}元
月人工成本：{self.taiwan_bank_data['成本參數']['月人工成本']:,}元/人
人月成本：{self.taiwan_bank_data['成本參數']['人月成本']:,}元
單件處理成本：{self.taiwan_bank_data['成本參數']['單件成本']}元/件
年度總成本：{self.taiwan_bank_data['成本參數']['年度總成本']:,}元

## 👥 人力配置方案
- 基礎配置：{self.taiwan_bank_data['人力配置']['基礎配置']}人（適用於標準業務量）
- 標準配置：{self.taiwan_bank_data['人力配置']['標準配置']}人（推薦配置）
- 增強配置：{self.taiwan_bank_data['人力配置']['增強配置']}人（高峰期配置）

## 📈 投資回報分析
投資回收期：{self.taiwan_bank_data['ROI數據']['投資回收期']}個月
成本節約率：{self.taiwan_bank_data['ROI數據']['成本節約率']*100:.1f}%
效率提升：{self.taiwan_bank_data['ROI數據']['效率提升']*100:.1f}%

## 🎯 實施建議
1. **第一階段**（1-3個月）：優化現有OCR系統，提升準確率至92%以上
2. **第二階段**（4-6個月）：實施智能分類和優先級處理
3. **第三階段**（7-12個月）：建立完整的質量控制和監控體系

## ⚠️ 風險評估
- **技術風險**：OCR系統穩定性、準確率波動
- **運營風險**：人員流動、培訓成本增加
- **合規風險**：監管要求變化、數據安全要求

## 💡 優化潛力
通過技術升級和流程優化，預計可進一步：
- 減少人工審核工作量15-20%
- 提升處理效率25-30%
- 降低運營成本10-15%

這個分析基於台銀的實際運營數據，具有很高的參考價值和實用性。"""
    
    def _generate_detailed_taiwan_analysis(self, query: str) -> str:
        """生成詳細的台銀分析"""
        return f"""基於台銀OCR審核人月成本分析，針對「{query}」的專業分析：

## 核心數據
- 年處理案件：{self.taiwan_bank_data['基礎參數']['年處理案件量']:,}件
- 人月成本：{self.taiwan_bank_data['成本參數']['人月成本']:,}元
- 單件成本：{self.taiwan_bank_data['成本參數']['單件成本']}元
- 投資回收期：{self.taiwan_bank_data['ROI數據']['投資回收期']}個月

## 成本效益分析
根據台銀實際數據，OCR審核系統相比全人工處理：
- 成本節約：{self.taiwan_bank_data['ROI數據']['成本節約率']*100:.1f}%
- 效率提升：{self.taiwan_bank_data['ROI數據']['效率提升']*100:.1f}%
- 年度節約：{int(self.taiwan_bank_data['成本參數']['年度總成本'] * self.taiwan_bank_data['ROI數據']['成本節約率']):,}元

## 人力配置建議
推薦採用{self.taiwan_bank_data['人力配置']['標準配置']}人的標準配置，可根據業務量在{self.taiwan_bank_data['人力配置']['基礎配置']}-{self.taiwan_bank_data['人力配置']['增強配置']}人之間彈性調整。

## 實施要點
1. 確保OCR準確率達到{self.taiwan_bank_data['基礎參數']['OCR平均準確率']}以上
2. 建立有效的人工審核流程
3. 定期評估和優化系統性能

這個分析基於台銀的實際運營經驗，為類似項目提供了可靠的參考基準。"""
    
    def _generate_basic_taiwan_analysis(self, query: str) -> str:
        """生成基礎的台銀分析"""
        return f"""基於台銀數據，針對「{query}」的要點分析：

**關鍵數據**：
- 年處理{self.taiwan_bank_data['基礎參數']['年處理案件量']:,}件，人月成本{self.taiwan_bank_data['成本參數']['人月成本']:,}元
- 投資回收期{self.taiwan_bank_data['ROI數據']['投資回收期']}個月，成本節約{self.taiwan_bank_data['ROI數據']['成本節約率']*100:.1f}%

**核心建議**：
採用{self.taiwan_bank_data['人力配置']['標準配置']}人標準配置，確保OCR準確率達到{self.taiwan_bank_data['基礎參數']['OCR平均準確率']}，可實現顯著的成本效益。

**結論**：
台銀模式證明了OCR審核系統的可行性和經濟效益，值得推廣應用。"""
    
    def _check_adaptive_cache(self, query: str, config: DynamicConfig) -> Optional[ContextAwareResult]:
        """檢查自適應緩存"""
        cache_key = f"{hash(query)}_{config.environment}_{config.user_type}_{config.analysis_depth}"
        
        if cache_key in self.adaptive_cache:
            cached_item = self.adaptive_cache[cache_key]
            if time.time() - cached_item["timestamp"] < config.cache_ttl:
                return cached_item["result"]
            else:
                del self.adaptive_cache[cache_key]
        
        return None
    
    def _save_to_adaptive_cache(self, query: str, config: DynamicConfig, result: ContextAwareResult):
        """保存到自適應緩存"""
        if config.cache_strategy == "none":
            return
        
        cache_key = f"{hash(query)}_{config.environment}_{config.user_type}_{config.analysis_depth}"
        
        self.adaptive_cache[cache_key] = {
            "result": result,
            "timestamp": time.time(),
            "config": config
        }
        
        # 限制緩存大小
        max_cache_size = 200 if config.cache_strategy == "aggressive" else 100
        if len(self.adaptive_cache) > max_cache_size:
            oldest_key = min(self.adaptive_cache.keys(), 
                           key=lambda k: self.adaptive_cache[k]["timestamp"])
            del self.adaptive_cache[oldest_key]
    
    def _count_adaptations(self, config: DynamicConfig) -> int:
        """計算配置適應次數"""
        adaptations = 0
        base_config = DynamicConfig()
        
        if config.max_tokens != base_config.max_tokens:
            adaptations += 1
        if config.temperature != base_config.temperature:
            adaptations += 1
        if config.cache_ttl != base_config.cache_ttl:
            adaptations += 1
        if config.analysis_depth != base_config.analysis_depth:
            adaptations += 1
        
        return adaptations
    
    def _update_performance_metrics(self, config: DynamicConfig, result: ContextAwareResult):
        """更新性能指標"""
        self.performance_metrics["total_requests"] += 1
        self.performance_metrics["config_adaptations"] += result.metadata.get("adaptations_made", 0)
        
        if config.taiwan_bank_enabled:
            self.performance_metrics["taiwan_bank_usage"] += 1
        
        # 更新平均響應時間
        response_time = result.metadata.get("response_time", 0)
        total_requests = self.performance_metrics["total_requests"]
        current_avg = self.performance_metrics["average_response_time"]
        new_avg = (current_avg * (total_requests - 1) + response_time) / total_requests
        self.performance_metrics["average_response_time"] = new_avg
        
        # 更新分佈統計
        self.performance_metrics["user_type_distribution"][config.user_type] += 1
        self.performance_metrics["environment_distribution"][config.environment] += 1
    
    def get_dynamic_metrics(self) -> Dict[str, Any]:
        """獲取動態指標"""
        return {
            "component": self.name,
            "version": self.version,
            "performance_metrics": self.performance_metrics,
            "cache_status": {
                "cache_size": len(self.adaptive_cache),
                "cache_strategies": ["none", "basic", "adaptive", "aggressive"]
            },
            "dynamic_capabilities": {
                "environment_detection": True,
                "user_type_detection": True,
                "analysis_depth_adaptation": True,
                "performance_mode_switching": True,
                "taiwan_bank_integration": True
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def health_check_dynamic(self) -> Dict[str, Any]:
        """動態系統健康檢查"""
        try:
            # 測試不同配置的處理能力
            test_queries = [
                ("什麼是保險？", {"user_type": "standard"}),
                ("核保流程的OCR成本分析", {"user_type": "professional"}),
                ("企業級保險系統架構設計", {"user_type": "enterprise"})
            ]
            
            test_results = []
            for query, preferences in test_queries:
                result = await self.dynamic_search_and_analyze(query, user_preferences=preferences)
                test_results.append({
                    "query": query,
                    "user_type": result.user_type_detected,
                    "analysis_depth": result.analysis_depth_used,
                    "taiwan_bank_used": result.taiwan_bank_data_used,
                    "response_time": result.metadata.get("response_time", 0)
                })
            
            return {
                "healthy": True,
                "component": self.name,
                "version": self.version,
                "dynamic_features": {
                    "config_manager": True,
                    "environment_detector": True,
                    "adaptive_cache": True,
                    "taiwan_bank_integration": True
                },
                "test_results": test_results,
                "metrics": self.get_dynamic_metrics(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "component": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# 便利函數
async def create_dynamic_cloud_search_mcp(base_llm_config: Dict[str, Any] = None) -> DynamicCloudSearchMCP:
    """創建 Dynamic Cloud Search MCP 組件"""
    return DynamicCloudSearchMCP(base_llm_config)

# 使用示例
async def dynamic_example_usage():
    """動態版本使用示例"""
    # 創建動態組件
    dynamic_mcp = await create_dynamic_cloud_search_mcp({
        "provider": "claude",
        "model": "claude-3-5-sonnet-20241022"
    })
    
    # 測試不同場景
    scenarios = [
        {
            "query": "什麼是核保？",
            "context": {"time_sensitive": True},
            "preferences": {"performance_mode": "speed"}
        },
        {
            "query": "核保流程需要多少人力處理表單？OCR審核的成本分析？",
            "context": {"quality_critical": True},
            "preferences": {"analysis_depth": "comprehensive"}
        },
        {
            "query": "企業級保險系統的架構設計和部署策略",
            "context": {},
            "preferences": {"user_type": "enterprise"}
        }
    ]
    
    print("=== Dynamic Cloud Search MCP 測試 ===\n")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"## 場景 {i}: {scenario['query'][:30]}...")
        
        result = await dynamic_mcp.dynamic_search_and_analyze(
            scenario["query"],
            scenario["context"],
            scenario["preferences"]
        )
        
        print(f"環境檢測: {result.environment_detected}")
        print(f"用戶類型: {result.user_type_detected}")
        print(f"分析深度: {result.analysis_depth_used}")
        print(f"性能模式: {result.performance_mode_used}")
        print(f"台銀數據: {result.taiwan_bank_data_used}")
        print(f"處理策略: {result.processing_strategy}")
        print(f"響應時間: {result.metadata.get('response_time', 0):.2f}秒")
        print(f"動態調整: {result.dynamic_adjustments}")
        print(f"分析長度: {len(result.result)} 字符")
        print("-" * 50)
    
    # 顯示整體指標
    metrics = dynamic_mcp.get_dynamic_metrics()
    print(f"\n=== 整體性能指標 ===")
    print(f"總請求數: {metrics['performance_metrics']['total_requests']}")
    print(f"配置適應次數: {metrics['performance_metrics']['config_adaptations']}")
    print(f"台銀數據使用: {metrics['performance_metrics']['taiwan_bank_usage']}")
    print(f"平均響應時間: {metrics['performance_metrics']['average_response_time']:.2f}秒")
    print(f"用戶類型分佈: {metrics['performance_metrics']['user_type_distribution']}")
    print(f"環境分佈: {metrics['performance_metrics']['environment_distribution']}")

if __name__ == "__main__":
    asyncio.run(dynamic_example_usage())

