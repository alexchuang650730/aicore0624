#!/usr/bin/env python3
"""
台銀版本 Cloud Search 配置文件
Taiwan Bank Based Cloud Search Configuration

基於台銀 OCR 審核人月成本詳細計算分析的專業配置
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class TaiwanBankConfig:
    """台銀版本配置類"""
    
    # 基礎參數 (來自台銀文件)
    ANNUAL_CASES = 100000  # 年度總案件量
    OCR_COVERAGE_RATE = 1.0  # OCR系統覆蓋率 100%
    MANUAL_REVIEW_RATE = 0.9  # 需人工審核比例 90%
    OCR_ACCURACY_RATE = 0.88  # OCR平均準確率 88%（混合文檔）
    
    # 成本參數 (來自台銀文件)
    MONTHLY_SALARY = 35000  # 月薪
    SOCIAL_BENEFITS = 10500  # 社保福利
    MONTHLY_COST_PER_PERSON = 45500  # 月人工成本
    COST_PER_PERSON_MONTH = 48116  # 人月成本
    COST_PER_CASE = 266  # 單件成本
    
    # 時間參數 (來自台銀文件)
    REVIEW_TIME_PER_CASE = 35  # 單件審核時間（分鐘）
    REVIEW_HOURS_PER_CASE = 0.58  # 單件審核時間（小時）
    ANNUAL_TOTAL_HOURS = 52200  # 年度總工時
    
    # 人力配置 (來自台銀文件)
    STAFF_CONFIG_BASIC = 29  # 基礎人力配置
    STAFF_CONFIG_STANDARD = 34  # 標準人力配置
    STAFF_CONFIG_ENHANCED = 41  # 增強人力配置
    
    # 投資回報 (來自台銀文件)
    ANNUAL_TOTAL_COST = 26560000  # 年度總成本（元）
    COST_SAVING_RATE = 0.41  # 相比全人工節約比例
    PAYBACK_PERIOD_MONTHS = 2.3  # 投資回收期（月）

# 台銀版本 LLM 配置
TAIWAN_BANK_LLM_CONFIG = {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 4000,
    "temperature": 0.3,
    "system_prompt": """你是台銀專業分析專家，專門提供基於台銀OCR審核人月成本詳細計算分析的專業諮詢。

你的分析必須：
1. 使用台銀文件中的具體數據和計算方法
2. 提供專業級的詳細分析（至少1500字符）
3. 包含具體的數字、比例和計算結果
4. 達到台銀專業諮詢報告的標準

台銀基礎數據：
- 年度總案件量：100,000件
- OCR審核人月成本：48,116元/人月
- 單件處理成本：266元/件
- 投資回收期：約2.3個月
- 自動化比率：產險40-50%，壽險30-40%""",
    
    "taiwan_bank_data_context": """
基於台銀OCR審核人月成本詳細計算分析：

計算基礎參數：
- 年度總案件量：100,000件
- OCR系統覆蓋率：100%
- 需人工審核比例：90%
- OCR平均準確率：88%（混合文檔）
- 單件審核時間：35分鐘/件 = 0.58小時/件
- 年度總工時：52,200小時

成本計算分析：
- 月薪：35,000元
- 社保福利：10,500元
- 月人工成本：45,500元/人
- 人月成本：48,116元
- 單件成本：266元

人力配置需求：
- 基礎配置：29人
- 標準配置：34人
- 增強配置：41人

投資回報分析：
- 年度總成本：2,656萬元
- 相比全人工節約：41%成本
- 投資回收期：約2.3個月
"""
}

# 台銀版本專用 Prompt 模板
TAIWAN_BANK_PROMPT_TEMPLATE = """
基於台銀OCR審核人月成本詳細計算分析，請對以下查詢進行專業分析：

查詢: {user_input}

請使用台銀文件中的具體數據和計算方法，提供詳細的專業分析，包括：

1. **詳細背景分析** (至少500字符)：
   - 使用台銀的具體數據（100,000件、48,116元/人月等）
   - 引用台銀的計算方法（35分鐘/件、0.58小時/件等）
   - 提供行業背景和最佳實踐

2. **量化數據分析**：
   - 具體的成本結構分析
   - 人力配置計算
   - ROI和投資回收期分析

3. **專家領域識別**：
   - 識別3個最相關的專業領域
   - 每個領域的具體職責說明

4. **實施建議**：
   - 基於台銀經驗的具體建議
   - 分階段實施計劃
   - 風險評估和注意事項

請確保分析達到台銀專業諮詢報告的標準，內容詳實、數據準確、建議可操作。

返回格式：
{{
    "background_analysis": "詳細背景分析（至少500字符，包含台銀具體數據）",
    "expert_domains": ["專家領域1", "專家領域2", "專家領域3"],
    "confidence_score": 0.95,
    "taiwan_bank_data_used": true,
    "analysis_length": "字符數統計",
    "professional_level": "Taiwan_Bank_Standard"
}}
"""

# 台銀版本性能配置
TAIWAN_BANK_PERFORMANCE_CONFIG = {
    "target_response_time": 30.0,  # 目標響應時間（秒）
    "min_analysis_length": 1500,   # 最小分析長度（字符）
    "required_confidence": 0.85,   # 最低信心度要求
    "cache_enabled": True,          # 啟用緩存
    "cache_ttl": 7200,             # 緩存時間（2小時）
    "retry_attempts": 2,            # 重試次數
    "timeout": 60.0                 # 超時時間（秒）
}

# 導出配置
__all__ = [
    'TaiwanBankConfig',
    'TAIWAN_BANK_LLM_CONFIG', 
    'TAIWAN_BANK_PROMPT_TEMPLATE',
    'TAIWAN_BANK_PERFORMANCE_CONFIG'
]

